# Tóm tắt mô phỏng simulate-1@20261128-142736

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| dung_it | 21 | 1 | 804 | 104 | 1.0 | 2.0 |
| dung_vua | 14 | 3 | 2525 | 330 | 3.0 | 6.0 |
| dung_nhieu | 15 | 5 | 4775 | 473 | 5.0 | 10.0 |

Tỉ lệ đạt dùng để tính: 19/23 (83%) — lượt run-2@20261128-142503

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-2.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (200 người) | Chi phí / tháng — cơ sở (436 người) | Chi phí / tháng — cao (721 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-5.4-mini (vào 0.75 · ra 4.5 $/1M) | $0.0031 | $0.0038 | $0.0014 | $7.02 | $15.31 | $25.32 | $0.0351 |
| gpt-5.4 (vào 2.5 · ra 15.0 $/1M) | $0.0104 | $0.0125 | $0.0045 | $23.41 | $51.03 | $84.39 | $0.1170 |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (2.8) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: gpt-5.4-mini-2026-03-17. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/50.
