"""Nối model — chỗ DUY NHẤT trong bản chạy thử gọi model AI. NHÓM VIẾT phần gọi model thật.

Hợp đồng (giữ nguyên để khung đo được token):
    call_model(system: str, user: str) -> dict với 4 khoá
        "text":       str   chữ model trả về
        "model":      str   tên model đã gọi (để tra giá ở bảng giá model)
        "tokens_in":  int   số token vào, lấy từ trường usage trong phản hồi API — KHÔNG ước lượng
        "tokens_out": int   số token ra, gồm cả token suy luận / suy nghĩ nếu API tính riêng
    @model_call (từ tracing.py) tự ghi mỗi lần gọi vào trace; agent.py gọi call_model bao nhiêu lần
    cũng được, khung tự cộng token.
    Lỗi gọi model (hết lượt, sai key, mất mạng): cứ để exception bay ra — khung ghi lỗi vào cột error.

Chế độ giả (mặc định khi .env chưa có MODEL_PROVIDER, hoặc MODEL_PROVIDER=fake):
    trả một câu giả cố định, model "fake", token 0 — để luồng chạy hết từ trước CP2 (guide bước 3.2).
    Lượt `run.py eval` / `run.py simulate` chạy bằng model giả KHÔNG được tính.

Nối model thật: điền .env (chép từ .env.example), rồi viết nhánh gọi API ở dưới theo docs/connect-model.md
(có ví dụ OpenAI, Claude, model chạy trên máy, và cách nối nhà cung cấp khác). Không dán API key vào file này.
"""
import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from tracing import model_call

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env(path=os.path.join(ROOT, ".env")):
    """Đọc file .env (KEY=VALUE mỗi dòng) vào biến môi trường, không ghi đè biến đã có. Khung — không cần sửa."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()
MODEL_PROVIDER = (os.environ.get("MODEL_PROVIDER") or "fake").strip().lower()
MODEL_NAME = (os.environ.get("MODEL_NAME") or "").strip()
API_KEY = (os.environ.get("API_KEY") or "").strip()


@model_call
def call_model(system: str, user: str) -> dict:
    if MODEL_PROVIDER == "fake":
        last = (user.strip().splitlines() or [""])[-1]
        return {"text": "[câu trả lời giả — chưa nối model] " + last[:60], "model": "fake", "tokens_in": 0, "tokens_out": 0}

    # NHÓM VIẾT: gọi model thật ở đây (theo MODEL_PROVIDER, MODEL_NAME, API_KEY) rồi trả đúng 4 khoá.
    # Ví dụ chép được cho từng nhà cung cấp: docs/connect-model.md mục 2.
    if MODEL_PROVIDER == "openai":
        if not MODEL_NAME or not API_KEY:
            raise ValueError("Cần điền MODEL_NAME và API_KEY trong .env.")
        body = {"model": MODEL_NAME, "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]}
        request = Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=75) as response:
                data = json.load(response)
        except HTTPError as error:
            raise RuntimeError(f"OpenAI trả lỗi HTTP {error.code}.") from None
        return {"text": data["choices"][0]["message"]["content"], "model": data["model"],
                "tokens_in": data["usage"]["prompt_tokens"],
                "tokens_out": data["usage"]["completion_tokens"]}

    raise NotImplementedError(
        "chưa viết phần gọi model thật cho MODEL_PROVIDER=%s trong codebase/ai.py — xem docs/connect-model.md"
        % MODEL_PROVIDER)


EMBED_MODEL = (os.environ.get("EMBED_MODEL") or "text-embedding-3-small").strip()


def embed_texts(texts: list) -> dict:
    """Embedding cho retrieval của prototype (codebase/retrieval.py). Không dùng trong agent.answer / eval.

    Trả {"vectors": [[float, ...], ...] đúng thứ tự texts, "model": str, "tokens": int (từ usage của API)}.
    Chỉ hỗ trợ MODEL_PROVIDER=openai; provider khác ném NotImplementedError để retrieval lùi về BM25.
    """
    if MODEL_PROVIDER != "openai" or not API_KEY:
        raise NotImplementedError("Embedding chỉ hỗ trợ MODEL_PROVIDER=openai có API_KEY.")
    request = Request(
        "https://api.openai.com/v1/embeddings",
        data=json.dumps({"model": EMBED_MODEL, "input": texts}).encode("utf-8"),
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=75) as response:
            data = json.load(response)
    except HTTPError as error:
        raise RuntimeError(f"OpenAI embeddings trả lỗi HTTP {error.code}.") from None
    rows = sorted(data["data"], key=lambda row: row["index"])
    return {"vectors": [row["embedding"] for row in rows], "model": data.get("model", EMBED_MODEL),
            "tokens": data.get("usage", {}).get("total_tokens", 0)}
