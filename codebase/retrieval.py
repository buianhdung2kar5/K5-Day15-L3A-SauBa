"""Chia chunk hybrid + tìm kiếm hybrid (BM25 + embedding, trộn RRF) cho chatbot hỏi đáp của prototype.

Chia chunk (chunk_pages) — theo cấu trúc trước, theo độ dài sau:
    1. Gom trang theo mục (bookmark của PDF); một chunk không vượt qua ranh giới mục.
    2. Tách văn bản thành đơn vị: dòng nối tiếp được ghép lại, đơn vị dài được cắt ở cuối câu.
    3. Gom đơn vị đến khoảng RAG_CHUNK_WORDS từ, không quá RAG_CHUNK_MAX; khối mới gối đầu
       khoảng RAG_OVERLAP_WORDS từ cuối khối trước (trong cùng mục).
    4. Khối cuối mục quá ngắn được gộp vào khối trước.
    Mã chunk giữ dạng P{trang}-{số thứ tự}, vd P012-01, nên tầng kiểm trích dẫn không đổi.

Tìm kiếm (search):
    - BM25 trên âm tiết đã bỏ dấu + cặp âm tiết liền nhau (từ tiếng Việt thường 2 âm tiết).
    - Embedding (ai.embed_texts) so cosine; vector lưu ở .prototype/embeddings/, tính một lần.
    - Đoạn chỉ được xét khi qua ngưỡng: trùng ≥ min(2, số từ khoá) từ khoá, HOẶC cosine ≥ RAG_MIN_COSINE.
    - Trộn hai bảng xếp hạng bằng Reciprocal Rank Fusion: điểm = Σ 1 / (60 + hạng).
    - Embedding lỗi → chỉ dùng BM25 (retrieval không phải tầng an toàn; L2/L5 vẫn fail-closed).

Cấu hình trong .env (đều tuỳ chọn): EMBED_MODEL, RAG_CHUNK_WORDS, RAG_CHUNK_MAX, RAG_OVERLAP_WORDS,
RAG_TOP_K, RAG_MIN_COSINE, RAG_MODE (hybrid | bm25 | dense).
"""
from __future__ import annotations

import json
import math
import os
import re
import unicodedata
from collections import Counter
from pathlib import Path

from ai import EMBED_MODEL, embed_texts

ROOT = Path(__file__).resolve().parents[1]
VECTOR_DIR = ROOT / ".prototype" / "embeddings"
CHUNKER = "hybrid-v1"


def _env_int(name, default):
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        return default


def _env_float(name, default):
    try:
        return float(os.environ.get(name, default))
    except ValueError:
        return default


CHUNK_WORDS = _env_int("RAG_CHUNK_WORDS", 180)
CHUNK_MAX = max(_env_int("RAG_CHUNK_MAX", 260), CHUNK_WORDS)
OVERLAP_WORDS = _env_int("RAG_OVERLAP_WORDS", 40)
MIN_WORDS = 40
TOP_K = _env_int("RAG_TOP_K", 6)
MIN_COSINE = _env_float("RAG_MIN_COSINE", 0.30)
MODE = (os.environ.get("RAG_MODE") or "hybrid").strip().lower()
RRF_K = 60


# ============================================================
# Chia chunk
# ============================================================

_END = re.compile(r"[.!?…:;]\s*$")
_BULLET = re.compile(r"^\s*(?:[-–•●▪◦*]|\d+[.)]|[a-zA-Z][.)])\s+")
_SENTENCE = re.compile(r"(?<=[.!?…])\s+(?=[A-ZĐÀ-Ỹ0-9\"“(])")


def _units(text: str) -> list[str]:
    """Ghép dòng bị ngắt giữa câu, tách đơn vị dài ở cuối câu."""
    lines = [re.sub(r"\s+", " ", line).strip() for line in (text or "").splitlines()]
    units = []
    for line in filter(None, lines):
        continues = (units and not _END.search(units[-1]) and not _BULLET.match(line)
                     and line[:1].islower())
        if continues:
            units[-1] += " " + line
        else:
            units.append(line)
    pieces = []
    for unit in units:
        for sentence in _SENTENCE.split(unit):
            words = sentence.split()
            for start in range(0, len(words), CHUNK_MAX):  # câu không dấu chấm, dài bất thường
                pieces.append(" ".join(words[start:start + CHUNK_MAX]))
    return [piece for piece in pieces if piece]


def chunk_pages(pages: list[dict]) -> list[dict]:
    """pages: [{"page": int, "text": str, "sections": tuple}] → chunk {"code","page","pages","sections","text"}."""
    groups = []
    for page in pages:
        sections = tuple(page.get("sections") or ())
        units = [(page["page"], unit) for unit in _units(page["text"])]
        if not units:
            continue
        # PDF không có bookmark: mỗi trang là một nhóm, khối ngắn vẫn được gộp với trang sau ở bước dưới.
        if groups and groups[-1]["sections"] == sections and sections:
            groups[-1]["units"] += units
        else:
            groups.append({"sections": sections, "units": units})

    chunks = []
    carry = []  # khối nhỏ của nhóm không có mục, chờ gộp với trang sau
    for group in groups:
        units = carry + group["units"]
        carry = []
        current, size = [], 0
        built = []
        for page, unit in units:
            words = len(unit.split())
            if current and size + words > CHUNK_MAX:
                built.append(current)
                overlap, kept = [], 0
                for item in reversed(current):  # gối đầu vài câu cuối của khối trước
                    kept += len(item[1].split())
                    if kept > OVERLAP_WORDS:
                        break
                    overlap.insert(0, item)
                current, size = overlap, sum(len(u.split()) for _, u in overlap)
            current.append((page, unit))
            size += words
            if size >= CHUNK_WORDS:
                built.append(current)
                overlap, kept = [], 0
                for item in reversed(current):
                    kept += len(item[1].split())
                    if kept > OVERLAP_WORDS:
                        break
                    overlap.insert(0, item)
                current, size = overlap, sum(len(u.split()) for _, u in overlap)
        if current and (not built or current != built[-1][-len(current):]):
            tail_words = sum(len(u.split()) for _, u in current)
            if built and tail_words < MIN_WORDS:
                fresh = [item for item in current if item not in built[-1]]
                built[-1] = built[-1] + fresh
            elif not group["sections"] and tail_words < MIN_WORDS and group is not groups[-1]:
                carry = current
            else:
                built.append(current)
        for items in built:
            chunks.append({"sections": group["sections"], "items": items})

    counters = Counter()
    result = []
    for chunk in chunks:
        first = chunk["items"][0][0]
        counters[first] += 1
        pages_used = sorted({page for page, _ in chunk["items"]})
        result.append({"code": f"P{first:03d}-{counters[first]:02d}", "page": first, "pages": pages_used,
                       "sections": chunk["sections"], "text": " ".join(unit for _, unit in chunk["items"])})
    return result


def pages_from_passages(passages: list[dict]) -> list[dict]:
    """Dựng lại trang từ các khối 250 từ kiểu cũ, để chia lại tài liệu đã tải trước đây."""
    pages = {}
    for passage in passages:
        page = pages.setdefault(passage["page"], {"page": passage["page"], "text": [],
                                                  "sections": tuple(passage.get("sections") or ())})
        page["text"].append(passage["text"])
    return [{**page, "text": "\n".join(page["text"])} for _, page in sorted(pages.items())]


# ============================================================
# BM25
# ============================================================

STOP = set("""và là của cho một các có không để trong với này khi được thì mà như nào gì sao bao những đó
the of a an to in is are what how why which tôi mình bạn em hãy về giúp giải thích cho biết nghĩa
tài liệu nói theo ra thế""".split())


def fold(text: str) -> str:
    text = unicodedata.normalize("NFD", (text or "").casefold().replace("đ", "d"))
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


STOP_FOLDED = {fold(word) for word in STOP}


def terms(text: str) -> list[str]:
    """Âm tiết (bỏ dấu, bỏ stopword) + cặp âm tiết liền nhau, vd 'tap test' → tap, test, tap_test."""
    syllables = [w for w in re.findall(r"\w+", fold(text)) if len(w) > 1 and w not in STOP_FOLDED]
    return syllables + [f"{a}_{b}" for a, b in zip(syllables, syllables[1:])]


def _index_text(passage: dict) -> str:
    return " › ".join(passage.get("sections") or ()) + "\n" + passage["text"]


def bm25(query: str, passages: list[dict], k1=1.5, b=0.75) -> list[tuple[float, int, dict]]:
    """Trả [(điểm, số từ khoá đơn trùng, đoạn)] cho đoạn có điểm > 0."""
    q = [t for t in dict.fromkeys(terms(query))]
    if not q or not passages:
        return []
    docs = [Counter(terms(_index_text(p))) for p in passages]
    lengths = [sum(d.values()) for d in docs]
    avg = sum(lengths) / len(lengths) or 1
    n = len(docs)
    scored = []
    for doc, length, passage in zip(docs, lengths, passages):
        score, matched = 0.0, 0
        for term in q:
            freq = doc.get(term, 0)
            if not freq:
                continue
            matched += "_" not in term
            df = sum(1 for d in docs if term in d)
            idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
            score += idf * freq * (k1 + 1) / (freq + k1 * (1 - b + b * length / avg))
        if score > 0:
            scored.append((score, matched, passage))
    scored.sort(key=lambda item: -item[0])
    return scored


# ============================================================
# Embedding
# ============================================================

def _vector_file(token: str) -> Path:
    return VECTOR_DIR / f"{re.sub(r'[^0-9a-f]', '', token)}.json"


def ensure_vectors(token: str, passages: list[dict]) -> dict:
    """Vector cho mọi đoạn của một tài liệu, tính phần còn thiếu theo lô 64 đoạn rồi lưu lại."""
    path = _vector_file(token)
    stored = {}
    if path.exists():
        saved = json.loads(path.read_text(encoding="utf-8"))
        if saved.get("model") == EMBED_MODEL and saved.get("chunker") == CHUNKER:
            stored = saved["vectors"]
    missing = [p for p in passages if p["code"] not in stored]
    for start in range(0, len(missing), 64):
        batch = missing[start:start + 64]
        result = embed_texts([_index_text(p)[:8000] for p in batch])
        for passage, vector in zip(batch, result["vectors"]):
            stored[passage["code"]] = [round(x, 5) for x in vector]
    if missing:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"model": EMBED_MODEL, "chunker": CHUNKER, "vectors": stored}), encoding="utf-8")
    return stored


def _cosine(a, b) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm = math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))
    return dot / norm if norm else 0.0


def dense(query: str, passages: list[dict]) -> list[tuple[float, dict]]:
    """passages mang khoá "doc" (mã tài liệu) và "local_code" (mã trong tài liệu) để tra vector."""
    by_doc = {}
    for passage in passages:
        by_doc.setdefault(passage["doc"], []).append(passage)
    vectors = {}
    for token, items in by_doc.items():
        stored = ensure_vectors(token, [{**p, "code": p["local_code"]} for p in items])
        for passage in items:
            vectors[id(passage)] = stored[passage["local_code"]]
    query_vector = embed_texts([query])["vectors"][0]
    scored = [(_cosine(query_vector, vectors[id(p)]), p) for p in passages]
    scored.sort(key=lambda item: -item[0])
    return scored


# ============================================================
# Hybrid
# ============================================================

def search(query: str, passages: list[dict], k: int = TOP_K) -> tuple[list[dict], dict]:
    """Trả (đoạn đã xếp hạng, thông tin để hiện trong vết kiểm tra)."""
    info = {"mode": MODE, "bm25": 0, "dense": 0, "note": ""}
    lexical = bm25(query, passages) if MODE in ("hybrid", "bm25") else []
    need = min(2, len([t for t in dict.fromkeys(terms(query)) if "_" not in t]) or 1)
    lexical = [(score, p) for score, matched, p in lexical if matched >= need]
    info["bm25"] = len(lexical)

    semantic = []
    if MODE in ("hybrid", "dense"):
        try:
            semantic = [(score, p) for score, p in dense(query, passages) if score >= MIN_COSINE]
            info["dense"] = len(semantic)
        except Exception as error:  # mất mạng, provider khác… → lùi về BM25
            info["note"] = f"embedding lỗi ({type(error).__name__}), chỉ dùng BM25"
            if MODE == "dense":
                lexical = [(score, p) for score, _, p in bm25(query, passages)]

    fused = {}
    for ranking in (lexical[:20], semantic[:20]):
        for rank, (_, passage) in enumerate(ranking, 1):
            entry = fused.setdefault(passage["code"], [0.0, passage])
            entry[0] += 1 / (RRF_K + rank)
    ordered = sorted(fused.values(), key=lambda item: -item[0])
    return [passage for _, passage in ordered[:k]], info
