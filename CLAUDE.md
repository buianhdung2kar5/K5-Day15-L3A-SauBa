# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Trả lời người dùng bằng **tiếng Việt**. Luật cứng của repo (không sửa file khung, không sửa kết quả đã chạy, không sửa chuẩn "đạt"/metric sau CP2, không bịa số liệu…) nằm ở [AGENTS.md](AGENTS.md) — đọc và tuân theo, không chép lại ở đây.

## Context snapshot (ĐÃ CHỐT 27/11 — đọc trước khi góp ý thiết kế)

Repo hackathon AI20K, nhóm SauBa, Track A (EdTech). Trước khi đề xuất bất cứ điều gì về thiết kế, đối chiếu với các điểm dưới đây; đừng đổi vai người dùng hay giả định nguồn dữ liệu không có.

- **Người dùng = học viên AI20K tự ôn** trước bài kiểm tra giữa kỳ. Học viên **không được cung cấp đề hay đáp án**, và **không có giảng viên / TA duyệt** trong luồng. Mọi hướng kiểu "dùng ngân hàng đề có sẵn" hay "giảng viên duyệt rubric" là SAI context.
- **Lát cắt:** học viên đưa tài liệu một buổi học → AI sinh câu hỏi + rubric bám tài liệu (mỗi câu/ý có mã đoạn) → học viên trả lời → AI chấm và chỉ ra ý còn yếu kèm đoạn cần ôn. Quyết định AI chính: *học viên còn hổng ý nào trong tài liệu*.
- **Thay người duyệt bằng ràng buộc code kiểm được:** mỗi ý trong rubric phải trích **nguyên văn** tài liệu + mã đoạn; code kiểm câu trích có thật trong đoạn, không khớp thì bỏ ý/câu (G10). Nhãn tổng (đúng / đúng một phần / sai / cần làm rõ) do code tổng hợp theo luật rubric; câu code chấm theo test, không theo lời model.
- **Không tác động ra ngoài:** điểm chỉ để tự ôn, không lưu điểm chính thức, không gửi ai. Từ chối làm hộ bài kiểm tra thật, câu tấn công prompt, yêu cầu ngoài phạm vi.
- **Hai lượt độc lập:** mỗi lần `answer(text)` là một lượt. Lượt sinh đề lưu đề trong phiên và trả mã đề; lượt chấm lấy rubric theo mã đề. Sơ đồ đầy đủ: `spec.md` §4.
- **Hai loại "đáp án" phải tách riêng:**
  - Đề + rubric (câu hỏi, ý bắt buộc, mã đoạn, cách khớp) — dữ liệu runtime, model được thấy.
  - Câu trả lời mẫu + nhãn chuẩn (`examples` trong `data/rubric-tu-on.json`) — nhãn eval cho `eval/benchmark.csv`, **không bao giờ đưa vào prompt** (vi phạm luật "giấu câu thử").
- `data/rubric-tu-on.json` = một đề nhóm tự soạn (`synthetic`), đóng vai "đề đã sinh rồi chốt lại" để thử riêng khâu chấm. Tài liệu nguồn (`ON-01`, `ON-02`) hiện nằm chung file với đáp án — cần tách trước khi công cụ đọc. Chỉ commit đoạn trích / bản viết lại tài liệu khoá, không commit nguyên slide/PDF.
- Bằng chứng pain (canvas dòng 4) nói về *không biết mình hổng ý nào*; file data pre-class gốc đã bị xoá khỏi repo (commit `8c6bf70`), số liệu chỉ còn ở `canvas.md`.

Đổi bất kỳ điểm nào ở trên phải được người dùng xác nhận, cập nhật mục này, và (sau CP2 19:30 27/11) ghi dòng changelog ở `spec.md` §10.

## Lệnh

Bộ khung (`run.py`, `codebase/agent.py`, eval, simulate) chỉ dùng thư viện chuẩn Python 3.10+. Riêng giao diện `codebase/prototype.py` cần `pypdf` (`python -m pip install -r requirements.txt`). Trên Windows dùng `python` hoặc `py`.

```
python run.py                    # chạy bản chạy thử (codebase/app.py → agent.answer)
python run.py check              # kiểm benchmark.csv, metric_spec.yaml, TEAMS.md
python run.py eval --try [N]     # chạy N câu thử đầu (mặc định 3) → eval/run-try.csv
python run.py eval --fake        # thử bộ chạy, không gọi agent
python run.py eval               # cả bộ → eval/run-N.csv + traces/run-N.jsonl
python run.py score eval/run-N.csv
python run.py simulate --try     # mô phỏng chi phí 10 phiên
python run.py simulate           # → cost/simulate-N.csv
python codebase/prototype.py     # giao diện web tự ôn tại 127.0.0.1:8765 (upload PDF, sinh đề, chấm)
```

`eval`/`simulate` nhận `--wait 4` khi gói model giới hạn lượt/phút. Không có test runner riêng — "chạy thử một câu" = `python run.py eval --try 1`.

## Kiến trúc

- `run.py` (khung) điều phối mọi lệnh; `eval/run_eval.py` và `cost/simulate.py` đều gọi `codebase/agent.answer(text)` với **nguyên ô input** của câu thử. Dữ liệu nền phải do agent tự đọc qua công cụ, không truyền qua input.
- `codebase/ai.py::call_model` là chỗ duy nhất gọi model, bọc `@model_call` để `tracing.py` đếm token từ `usage` của API. Mặc định `MODEL_PROVIDER=fake` (đọc `.env`); lượt eval/simulate chạy bằng fake không được tính. Hiện chỉ có nhánh `openai` (gọi REST bằng `urllib`); provider khác ném `NotImplementedError` — xem `docs/connect-model.md`.
- `codebase/tools.py`: mỗi công cụ một hàm `@tool`, docstring ghi tên · input · output · tác động ra ngoài; bảng công cụ ở `spec.md` §4 phải khớp file này. Hai công cụ chỉ đọc: `search_passages` (khớp từ khoá ≥2 từ trên `data/tai-lieu-mau.json`, tối đa 3 đoạn) và `get_rubric` (theo mã `ON\d+` hoặc độ trùng lời câu hỏi trong `data/rubric-tu-on.json`).
- `codebase/agent.py`: workflow cố định 3 bước, không vòng lặp agent — tra đoạn → tra rubric → một lần `call_model`. Khi có rubric, model phải trả JSON (`grade` / `missing_answer` / `reply`) chỉ gồm trạng thái từng ý (đạt/thiếu/mâu thuẫn/chưa rõ); `_format_rubric_reply` kiểm đủ mã ý rồi **Python chốt nhãn tổng** và danh sách ý yếu kèm mã đoạn. JSON sai dạng → trả thông báo "chưa chấm được", không đoán. Với model `fake` bước chốt nhãn bị bỏ qua.
- `codebase/prototype.py`: giao diện HTTP riêng (không qua `agent.answer`), có luồng sinh đề từ PDF, chấm, kế hoạch ôn; lưu lịch sử cục bộ ở `.prototype/` — thư mục này không được commit. Chỉ bật model khi `MODEL_PROVIDER=openai` có đủ key.
- Trang Tạo đề là khung chat gọi `/api/chat`: model tự kiểm phân loại ý định *hỏi đáp* (chỉ trả lời từ PDF đã đính kèm, có mã đoạn) hoặc *tạo đề* (dùng lại `create_quiz`). Mọi lượt đi qua 6 tầng trong `codebase/guardrails.py`: L0 giới hạn → L1 regex trên các bản gỡ mã hoá (base64/hex/ROT13/URL/đảo ngược/leet/cách quãng/homoglyph) → L2 model tự kiểm đầu vào → L3 truy hồi (`codebase/retrieval.py`: chia chunk theo mục/câu có gối đầu, BM25 + embedding OpenAI trộn RRF, cấu hình `RAG_*`/`EMBED_MODEL` trong `.env`, vector cache ở `.prototype/embeddings/`) + loại đoạn PDF chứa chỉ thị → L4 canary/rò rỉ/mã đoạn bịa → L5 model tự kiểm bám nguồn. L2/L5 fail-closed. Mẫu L1 chỉ bắt yêu cầu *nhắm vào trợ lý* — câu hỏi kiến thức như "system prompt là gì?" phải qua. Nhật ký ở `.prototype/guard-log.jsonl`.
- Tài liệu nộp bài liên kết chéo: `canvas.md` (CP1/CP2) → `spec.md` §0–§10 → `evidence/`, `eval/` (`benchmark.csv`, `metric_spec.yaml` 5 metric chấm bởi người, `report.md`), `cost/`, `data/DATA_CARD.md`. Khi sửa một chỗ, kiểm các file trỏ tới nó.
