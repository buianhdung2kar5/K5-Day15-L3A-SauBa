# Chi phí khi dùng thật

> Điền ở guide bước 4.2, nộp ở CP4 14:30 Thứ Bảy 28/11. Ôn lại: ngày 13, ngày 1, ngày 14 · lab ngày 13, lab ngày 14. Chấm ở rubric R6.
> Số **không điền tay**: điền `cost/personas.yaml` → `python run.py simulate` → chép bảng trong `cost/simulate-N-summary.md` vào đây.
> Lúc build dùng gói miễn phí vẫn tính theo **giá gói trả phí** — đây là chi phí cho lúc đưa vào dùng thật.

**Thử CP3.** `simulate-try@20261128-050357` chạy 10 phiên, seed 42, 0 lỗi. Đo token trên GPT‑5.4 mini và dùng tỷ lệ đạt Lượt 1 (17/23). Chi phí ước tính với GPT‑5.4 mini là **0,0026 USD/phiên**, **0,0035 USD/task thành công** và **16,39 USD/tháng** ở kịch bản 436 người. Kịch bản dùng số tài khoản hoạt động của gói pre-class làm mốc và giả định tần suất dùng SauBa. Kết quả đầy đủ nằm trong `simulate-try-summary.md` do runner sinh tại máy.

## 1. Đầu vào

- **Persona.** Dùng ít 50%, 4 phiên/tháng, 1 lượt/phiên. Dùng vừa 30%, 10 phiên/tháng, 3 lượt/phiên. Dùng nhiều 20%, 20 phiên/tháng, 5 lượt/phiên. Các tỷ trọng và tần suất là giả định trong [personas.yaml](personas.yaml).
- **Quy mô.** Thấp 200 người (tự ước tính), cơ sở 436 tài khoản hoạt động và cao 721 tài khoản từ README gói BTC preclass. Đây là ba kịch bản triển khai giả định.
- **Giá cấu hình.** GPT-5.4 mini 0,75 USD vào và 4,50 USD ra trên một triệu token. GPT-5.4 2,50 USD vào và 15,00 USD ra. Nguồn giá ghi trong cấu hình ngày 28/11/2026. [GPT-5.4 mini](https://developers.openai.com/api/docs/models/gpt-5.4-mini) · [GPT-5.4](https://developers.openai.com/api/docs/models/gpt-5.4)
- **Tỷ lệ qua dùng để tính.** 19/23 (83%), `run-2@20261128-142503`. Token đo trên `gpt-5.4-mini-2026-03-17`. Mức GPT-5.4 là đối chiếu giá trên cùng lượng token đo được.

## 2. Kết quả mô phỏng

Lượt `simulate-1@20261128-142736` chạy 50 phiên gọi model, seed 42, 0 phiên lỗi. [CSV](simulate-1.csv) · [Tóm tắt từ runner](simulate-1-summary.md)

| Model | Chi phí / phiên | Chi phí / task thành công | / tháng — thấp | / tháng — cơ sở | / tháng — cao | / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|
| gpt-5.4-mini (vào 0.75 · ra 4.5 $/1M) | $0.0031 | $0.0038 | $7.02 | $15.31 | $25.32 | $0.0351 |
| gpt-5.4 (vào 2.5 · ra 15.0 $/1M) | $0.0104 | $0.0125 | $23.41 | $51.03 | $84.39 | $0.1170 |

Chi phí trên mỗi task thành công bằng chi phí trung bình mỗi phiên chia tỷ lệ qua 19/23. Tổng chi phí tháng được tính theo tỷ trọng và tần suất của từng persona.

## 3. So với impact

- Ở nhóm học viên gặp vấn đề, giả định 4 phiên/tháng và 10 phút tìm đoạn mỗi phiên tương ứng 40 phút/học viên/tháng. Cần đo trước–sau để xác nhận số phút thực sự tiết kiệm. Xem `spec.md` §2.
- Kịch bản 436 người có chi phí model bình quân $0.0351/người/tháng theo giá GPT-5.4 mini. Chi phí này chưa gồm lưu trữ, hosting và công duyệt.
- Kết luận: tiếp tục thử với nhóm học viên nhỏ và đo thời gian tìm đúng đoạn. Kết quả Lượt 2 còn thiếu 1 ca từ chối để đạt chuẩn.
