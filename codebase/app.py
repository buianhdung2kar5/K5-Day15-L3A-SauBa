"""Giao diện bản chạy thử: trang web cục bộ (chỉ thư viện chuẩn) → answer() trong agent.py.

Chạy bằng: python run.py   (macOS/Linux có thể là python3, Windows có thể là py)
Mở trình duyệt tại http://127.0.0.1:8000 (đổi cổng: biến môi trường PORT=8080).
Muốn dùng dòng lệnh như khung gốc: APP_MODE=cli python run.py   (PowerShell: $env:APP_MODE="cli"; python run.py)

Điểm hiện ra chỉ để tự ôn, không lưu, không gửi đi đâu. Mỗi lần gửi là một lượt answer() độc lập.
"""
import json
import os
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

for _stream in (sys.stdout, sys.stderr, sys.stdin):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

PAGE = """<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Trợ lý tự ôn</title>
<style>
:root{--bg:#f6f7f9;--fg:#1d2330;--card:#fff;--line:#d9dde5;--accent:#2457d6;--muted:#5d6676}
@media(prefers-color-scheme:dark){:root{--bg:#14171d;--fg:#e8ebf1;--card:#1d222b;--line:#323a48;--accent:#7aa2ff;--muted:#9aa3b5}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 system-ui,sans-serif}
main{max-width:760px;margin:0 auto;padding:24px 16px 48px}h1{font-size:1.4rem;margin:0 0 4px}
p.sub{margin:0 0 16px;color:var(--muted)}
textarea{width:100%;min-height:130px;padding:12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg);font:inherit;resize:vertical}
.row{display:flex;gap:8px;flex-wrap:wrap;margin:10px 0}
button{padding:9px 16px;border-radius:8px;border:1px solid var(--line);background:var(--card);color:var(--fg);font:inherit;cursor:pointer}
button.primary{background:var(--accent);border-color:var(--accent);color:#fff}button:disabled{opacity:.6;cursor:wait}
.card{border:1px solid var(--line);border-radius:8px;background:var(--card);padding:14px 16px;margin-top:14px;white-space:pre-wrap;word-wrap:break-word}
.meta{font-size:.85rem;color:var(--muted);margin-top:6px}.err{border-color:#c0392b}
</style></head><body><main>
<h1>Trợ lý tự ôn</h1>
<p class="sub">Gõ yêu cầu ôn tập, hoặc gửi câu hỏi kèm câu trả lời của bạn để được chấm. Điểm chỉ để tự ôn, không phải điểm chính thức.</p>
<textarea id="t" placeholder="Ví dụ: Tạo một câu hỏi ôn về hồi quy tuyến tính."></textarea>
<div class="row"><button class="primary" id="go">Gửi</button><button id="clr">Xoá</button></div>
<div id="out"></div>
<script>
const t=document.getElementById('t'),out=document.getElementById('out'),go=document.getElementById('go');
const esc=s=>s.replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const fmt=s=>esc(s).replace(/\\*\\*(.+?)\\*\\*/g,'<strong>$1</strong>');
async function send(){
  const text=t.value.trim(); if(!text) return;
  go.disabled=true; out.innerHTML='<div class="card">Đang xử lý…</div>';
  try{
    const r=await fetch('/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text})});
    const d=await r.json();
    out.innerHTML='<div class="card'+(d.error?' err':'')+'">'+fmt(d.error||d.output)+'</div>'+(d.meta?'<div class="meta">'+esc(d.meta)+'</div>':'');
  }catch(e){out.innerHTML='<div class="card err">Không kết nối được tới máy chủ cục bộ.</div>';}
  go.disabled=false;
}
go.onclick=send;
document.getElementById('clr').onclick=()=>{t.value='';out.innerHTML='';t.focus();};
t.addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.ctrlKey||e.metaKey)) send();});
</script></main></body></html>
"""


def _where(e):
    """File (trong codebase/) gây lỗi khi nạp: SyntaxError có e.filename, lỗi khác lấy khung cuối của traceback."""
    import traceback
    path = getattr(e, "filename", None) or (traceback.extract_tb(e.__traceback__)[-1].filename if e.__traceback__ else "")
    if not path:
        return "codebase/"
    p = os.path.abspath(path)
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.relpath(p, base).replace(os.sep, "/") if p.startswith(base) else path


def _load():
    try:
        import tracing
        from agent import answer
        return tracing, answer
    except Exception as e:  # lỗi cú pháp, thiếu thư viện… trong codebase/
        print("Không nạp được codebase/ — lỗi ở %s: %s: %s" % (_where(e), type(e).__name__, e))
        print("Sửa lỗi rồi chạy lại. Cách nối model: docs/connect-model.md")
        return None, None


def _run_once(tracing, answer, text):
    """Một lượt answer() có ghi trace. Trả (output hoặc None, lỗi hoặc None, dòng thống kê)."""
    tracing.begin("app")
    try:
        result = answer(text)
    except NotImplementedError as e:
        tracing.end()
        return None, "Chưa nối model: %s" % e, ""
    except Exception as e:  # lỗi gọi model: báo rồi cho hỏi tiếp
        tracing.end()
        return None, "[lỗi] %s: %s" % (type(e).__name__, e), ""
    s, _ = tracing.end()
    out = result.get("output", "") if isinstance(result, dict) else str(result)
    meta = "model: %s · gọi model %d lần · công cụ %d lần · token vào %d / ra %d" % (
        ", ".join(s["models"]) or "—", s["model_calls"], s["tool_calls"], s["tokens_in"], s["tokens_out"])
    return out, None, meta


def _make_handler(tracing, answer):
    lock = threading.Lock()  # tracing dùng trạng thái chung: xử lý lần lượt từng yêu cầu

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, body, ctype):
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", ctype + "; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self._send(200, PAGE, "text/html")
            else:
                self._send(404, "Không có trang này.", "text/plain")

        def do_POST(self):
            if self.path != "/ask":
                self._send(404, json.dumps({"error": "Không có đường dẫn này."}), "application/json")
                return
            try:
                size = int(self.headers.get("Content-Length") or 0)
                text = str(json.loads(self.rfile.read(size).decode("utf-8")).get("text", "")).strip()
            except Exception:
                self._send(400, json.dumps({"error": "Yêu cầu không hợp lệ."}), "application/json")
                return
            if not text:
                self._send(400, json.dumps({"error": "Bạn chưa nhập gì."}), "application/json")
                return
            with lock:
                out, err, meta = _run_once(tracing, answer, text)
            payload = {"error": err} if err else {"output": out, "meta": meta}
            self._send(200, json.dumps(payload, ensure_ascii=False), "application/json")

        def log_message(self, fmt, *args):  # không in từng yêu cầu ra terminal
            pass

    return Handler


def serve(tracing, answer):
    port = int(os.environ.get("PORT") or 8000)
    try:
        server = HTTPServer(("127.0.0.1", port), _make_handler(tracing, answer))
    except OSError as e:
        print("Không mở được cổng %d (%s). Thử PORT=8080 python run.py" % (port, e))
        return 1
    url = "http://127.0.0.1:%d" % port
    print("Bản chạy thử đang chạy tại %s — thoát: Ctrl+C" % url)
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()
    return 0


def cli(tracing, answer):
    print("Bản chạy thử — gõ đầu vào rồi Enter. Thoát: Ctrl+C (hoặc Enter 2 lần với dòng trống).")
    blank = 0
    while True:
        try:
            text = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not text:
            blank += 1
            if blank >= 2:
                return 0
            continue
        blank = 0
        out, err, meta = _run_once(tracing, answer, text)
        if err and err.startswith("Chưa nối model"):
            print(err)
            return 1
        print(err or out)
        if meta:
            print("   (%s)" % meta)


def main() -> int:
    tracing, answer = _load()
    if answer is None:
        return 1
    if (os.environ.get("APP_MODE") or "").strip().lower() == "cli" or "--cli" in sys.argv[1:]:
        return cli(tracing, answer)
    return serve(tracing, answer)


if __name__ == "__main__":
    sys.exit(main())
