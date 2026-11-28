# Khai báo dùng AI

README của nhóm có mục "Dùng AI vào việc gì" (2–3 dòng, bắt buộc). Ghi chi tiết vào bảng dưới đây.

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử | | | | |
| Prompt / thiết kế lời gọi mô hình | | | | |
| Đào data (viết script đếm, gợi ý nhãn) | | | Kiểm tay __ dòng, khớp __ | |
| Rà câu hỏi phỏng vấn / khảo sát | | Chỉ rà câu dẫn dắt | | |
| Viết câu thử (benchmark) | | | Mỗi câu thử có `source`; câu thử AI viết được ghi rõ | |
| Sinh data `synthetic` (nếu có) | | | Seed __ · kiểm tay __ dòng | |
| Chấm cột `pass` bằng LLM | Codex | Đối chiếu output với `pass_criterion` và metric, ghi chú ca trượt và tổng hợp bằng `run.py score` | Lượt 1 có chấm chéo 5 ca ghi trong `eval/README.md`. Lượt 2 chưa có số chấm chéo độc lập. | Vương Xuân Dương (theo TEAMS.md) |
| Slide, văn bản | Codex | Soạn PDF CP4 và cập nhật báo cáo từ hồ sơ bằng chứng, eval và mô phỏng chi phí | Đối chiếu Run ID, tỷ lệ qua, bảng chi phí và link demo dự phòng với file nguồn. | Phan Văn Cường (theo TEAMS.md) |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát; sửa kết quả các lượt đã chạy (`eval/run-*.csv`, `cost/simulate-*.csv`, `traces/`).
