# Đào dữ liệu BTC — lượt hậu kiểm của học viên AI20K

## 1. Cách đếm

- Nguồn là `data-btc/preclass/answers.csv` và từ điển cột đi kèm. Gói pre-class bao phủ 05–25/11/2026. Dữ liệu gốc lưu cục bộ và được Git bỏ qua.
- Câu hỏi phân tích là có bao nhiêu học viên làm sai ít nhất một ý sau buổi học và bao nhiêu lượt làm sai. Bộ lọc `nguon = pre_post_post` đã ghi trong Canvas CP1. Hồ sơ này tái lập số đếm sơ bộ.
- Chỉ giữ dòng có `was_correct=True` hoặc `False`. Giữ mọi lượt trong số đếm lượt làm, kể cả lần làm lại. Mẫu số người là số `hv` duy nhất trong tập đã lọc. Đếm mã sai theo từng người bằng cách khử trùng `kc_code`.
- Chạy `python -X utf8 evidence/count_preclass.py` từ thư mục gốc để tái lập số liệu và năm ví dụ.

## 2. Đọc trước, đếm sau

Từ điển cột phân biệt lần trả lời trước và sau buổi học qua `nguon`, các lần thử qua `lan_thu`, và từng ý qua `kc_code`. Một người có thể trả lời nhiều lần, nên dùng hai mẫu số riêng cho lượt làm và học viên. Ô đúng/sai trống biểu thị không áp dụng và bị loại khỏi phép đếm.

## 3. Kết quả

- **399/1.970 lượt hậu kiểm sai (20,3%)**.
- **69/77 học viên hậu kiểm sai ít nhất một lượt (89,6%)**.
- Trung vị là **3 mã kiến thức sai** trên toàn bộ 77 học viên và **4 mã** trong nhóm 69 học viên có mã sai.

## 4. Năm ví dụ từ BTC

Các dòng dưới đây giữ nguyên mã bản ghi, mã kiến thức và giá trị `was_correct`. Script chọn năm mã có nhiều lượt sai nhất trong hậu kiểm Ngày 2, rồi chọn bản ghi có mã dòng nhỏ nhất cho mỗi mã kiến thức.

1. `A00394` · `complete_ai_problem_statement` · `False` · 8 lượt sai cùng mã.
2. `A00452` · `select_rule_workflow_agent_level` · `False` · 8 lượt sai cùng mã.
3. `A00112` · `construct_eval_plan` · `False` · 7 lượt sai cùng mã.
4. `A00031` · `double_diamond_problem_discovery` · `False` · 4 lượt sai cùng mã.
5. `A00672` · `evaluate_ai_fit_and_alternatives` · `False` · 4 lượt sai cùng mã.

## 5. Giới hạn

Dữ liệu cho thấy học viên sai ở ý nào và bao nhiêu lượt. Các bản ghi chỉ chứa metadata nên chưa giải thích được vì sao học viên sai, họ có biết mình sai ở đâu hay mất bao lâu để ôn lại. Kết quả áp dụng cho 77 học viên có lượt hậu kiểm với nhãn đúng/sai. [Khảo sát](summary.md) cho biết 17/21 người trả lời chưa xác định rõ chỗ hổng khi ôn. Hai nguồn có mẫu và câu hỏi khác nhau, nên so sánh theo xu hướng và giữ nguyên từng mẫu số.
