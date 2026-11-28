# Data card — dữ liệu bản chạy thử dùng

> Bản đầu CP2 (27/11). Đủ ở CP3. Một trang, mỗi dataset một mục.
> Không commit nguyên tài liệu khoá, dữ liệu cá nhân thật hay nguyên file data BTC cấp — chỉ đoạn trích ngắn, bản viết lại, hoặc số đã tổng hợp.

## Dataset 1 · Đoạn tài liệu ôn mẫu (`data/tai-lieu-mau.json`) + rubric (`data/rubric-tu-on.json`)

| | |
|---|---|
| Dùng để làm gì | nguồn đoạn tài liệu cho công cụ `search_passages` · rubric chấm cho công cụ `get_rubric` · căn cứ để viết và chấm `eval/benchmark.csv` (metric `trich_dung_nguon`, `cham_khop_dap_an`, `chi_dung_y_yeu`) |
| Từ đâu | nhóm tự viết lại, ngắn, kiến thức nhập môn ML chung; **không** trích nguyên tài liệu khoá. `ON-01`, `ON-02` trùng với `rubric-tu-on.json`; `ON-03`…`ON-06` viết thêm |
| Xử lý những bước gì | viết tay · không có dữ liệu cá nhân nên không cần ẩn danh · không lọc, không chia tập |
| Số dòng / số đoạn | 6 đoạn nguồn (`ON-01`…`ON-06`: hồi quy/phân loại, tập test, quá khớp, validation, gradient descent, chuẩn hoá) · rubric cho 2 câu hỏi (`ON1`: 1 ý; `ON2`: 2 ý) cùng 10 ví dụ trả lời đã gán nhãn |
| Phiên bản / ngày lấy | bản đầu CP2, 27/11 |
| Nhãn | tự viết — không phải `synthetic` sinh bằng model, cũng **không phải bằng chứng pain** |
| Giới hạn | chỉ 6 đoạn và 2 câu có rubric, nên câu chấm trong bộ thử chỉ xoay quanh ON1/ON2. Chưa phải tài liệu khoá thật → câu tìm thấy đoạn trong demo không chứng minh được nó bám tài liệu học viên đang học. Chỉ có câu điền text, chưa có bài nộp code hay trắc nghiệm (nên metric `cham_code_khop_test` hiện chưa có dòng nào áp dụng). Tìm đoạn bằng so khớp từ khoá, sẽ sót khi người dùng diễn đạt khác |

### Đoạn ôn bổ sung từ PDF Ngày 2

`tai-lieu-mau.json` có 19 đoạn diễn giải từ tài liệu AI20K “Ngày 2 — Discovery & Problem Framing”, ngoài 6 đoạn ML mẫu. Các đoạn phủ kiểm chứng thống kê, PAIR và baseline, Discovery, stakeholder, metric và chi phí lỗi, tính khả thi, Gate 0, acceptance test và quản lý rủi ro. Mỗi đoạn có mã `D02-Pxxx` và số trang tính từ bìa PDF. Nhóm chọn và diễn giải nội dung từ lớp chữ, gồm cả nhãn trong sơ đồ Kim cương đôi và bảng hai kiểu sai. Phần cần đọc trực tiếp từ hình chưa được đối chiếu. Bộ rubric hiện dùng cho hai câu ML mẫu.

## Dataset 2 · Metadata pre-class của học viên (data BTC cấp, `data-btc/preclass/answers.csv`)

| | |
|---|---|
| Dùng để làm gì | **đào bằng chứng pain** (`evidence/data-mining.md`) · tham khảo kiểu sai để viết câu thử. Công cụ của agent **không** đọc file này |
| Từ đâu | data BTC cấp. File **không có trong repo** (không commit nguyên file data BTC cấp); repo chỉ chứa số đã tổng hợp |
| Xử lý những bước gì | Lọc `nguon = pre_post_post` và giữ nhãn đúng/sai. Đếm theo lượt, theo học viên và theo mã kiến thức sai duy nhất của mỗi người. Chạy `python -X utf8 evidence/count_preclass.py` để tái lập. |
| Số dòng / số đoạn | 1.970 lượt trả lời của 77 học viên. 399/1.970 lượt sai (20,3%). 69/77 học viên sai ít nhất một lượt (89,6%). Trung vị 3 mã kiến thức sai trên toàn mẫu và 4 mã trong nhóm có ít nhất một mã sai. |
| Phiên bản / ngày lấy | bản BTC cấp ngày __ *(cần điền)* |
| Nhãn | thật |
| Giới hạn | Dữ liệu cho biết học viên sai ở ý nào, lý do sai và cách ôn cần khảo sát thêm. Mẫu gồm một nhóm học viên khóa 5. Cách đếm và năm ví dụ nằm ở `evidence/data-mining.md`. Benchmark dùng các ca đã chuyển thể. |

## Dataset 3 · Bộ câu thử (`eval/benchmark.csv`)

| | |
|---|---|
| Dùng để làm gì | chạy `python run.py eval`, chấm theo `eval/metric_spec.yaml` |
| Từ đâu | 15 ca tự soạn dựa trên rubric mẫu. 8 ca chuyển thể từ metadata hậu kiểm Ngày 2 trong Dataset 2 và đối chiếu đoạn ôn trong Dataset 1. |
| Xử lý những bước gì | Lọc hậu kiểm Ngày 2 có `was_correct=False`, chọn tám mã kiến thức có đoạn PDF tương ứng và viết yêu cầu tự ôn cho từng mã. Chỉ lưu mã bản ghi và mã kiến thức để đối chiếu. |
| Số dòng / số đoạn | 23 câu (thuong 7 · kho 12 · tu_choi 4, gồm hai ca tấn công B13 và B14) |
| Phiên bản / ngày lấy | bản CP3, 28/11 |
| Nhãn | 15 `tu_viet`, 8 `data_that` (chuyển thể từ metadata BTC) |
| Giới hạn | Các dòng B16–B23 kiểm sinh đề theo chủ đề từng làm sai. Bộ dữ liệu không chứa bài làm nguyên văn để kiểm AI chấm lại câu trả lời thật. |

**Data `synthetic`:** hiện chưa có dữ liệu sinh bằng model hoặc script. Nếu sinh thêm câu thử hay đoạn nguồn, ghi cách sinh (prompt / script), seed, người kiểm và số dòng đã kiểm tay vào mục tương ứng. Data tự dựng không phải bằng chứng pain.
