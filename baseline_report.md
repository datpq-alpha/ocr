# Báo cáo baseline OCR — 03/11/2026

Đánh giá hai pipeline pretrained trên **43 ảnh toàn trang**, gồm 22 chứng từ kế toán và 21 hóa đơn/tài liệu liên quan. Ground truth có 43 nhãn `Verified`, tổng cộng 47.548 ký tự và 9.465 đơn vị tách bằng khoảng trắng sau chuẩn hóa. Hai lượt chạy hoàn thành bằng Python 3.12.5 trên Windows 11, CPU, 4 luồng, batch nhận dạng 8; warm-up một ảnh và đo một lượt cho mỗi ảnh.

## Cấu hình và cách chấm

Hai pipeline dùng chung detector `PP-OCRv6_small_det`, bước cắt ảnh và sắp xếp văn bản theo ô bảng có đường kẻ. Nhánh PaddleOCR dùng `ppocrv6_vi` (`PP-OCRv6_medium_rec`, checkpoint tiếng Việt cộng đồng `tieubaoca/pp-ocrv6-medium-rec-vietnamese`, revision `edc19ca6890bedb7a68c055d21190b44fc1aaa00`); nhánh VietOCR dùng `vgg_seq2seq`. Phiên bản: PaddleOCR 3.7.0, PaddlePaddle 3.2.0, VietOCR 0.3.13 và PyTorch 2.5.1+cpu.

CER/WER tính bằng `(thay thế + xóa + chèn) / số đơn vị trong ground truth`, cộng số lỗi trên toàn tập trước khi chia. Văn bản được chuẩn hóa Unicode NFC và gộp khoảng trắng; giữ dấu tiếng Việt, hoa/thường, dấu câu và dấu phân cách số. WER dùng đơn vị tách theo khoảng trắng, chưa phân đoạn từ tiếng Việt. Thứ tự đọc ảnh hưởng điểm; xuống dòng/tab không được chấm riêng như cấu trúc bảng.

## Kết quả

| Chỉ số | PaddleOCR tiếng Việt | Detector + VietOCR |
| --- | ---: | ---: |
| CER ↓ | 19,19% | **9,49%** |
| WER ↓ | 48,19% | **15,33%** |
| Điểm ký tự quy đổi `1 − CER` ↑ | 80,81% | **90,51%** |
| Ảnh khớp hoàn toàn sau chuẩn hóa | 0/43 | 0/43 |
| Thời gian trung bình/ảnh | 24,93 giây | **6,79 giây** |
| Latency p50 / p95 | 20,19 / 70,86 giây | **6,26 / 10,94 giây** |
| Thời gian xử lý 43 ảnh | 1.072,25 giây (17,87 phút) | **292,30 giây (4,87 phút)** |
| Throughput | 2,41 ảnh/phút | **8,83 ảnh/phút** |
| Lỗi thực thi / thiếu đầu ra | 0/43 / 0/43 | 0/43 / 0/43 |

`1 − CER` là điểm quy đổi từ khoảng cách chỉnh sửa, không phải tỷ lệ ký tự khớp trực tiếp hay độ chính xác trường dữ liệu. Ảnh khớp hoàn toàn yêu cầu toàn bộ chuỗi văn bản đúng sau chuẩn hóa. Lỗi thực thi 0% không đồng nghĩa văn bản không có lỗi nhận dạng.

Thời gian xử lý cả tập gồm đọc ảnh, xử lý layout, detection, crop, recognition, ghép văn bản và ghi đầu ra; không gồm khởi tạo và warm-up. Thời gian khởi tạo/warm-up lần lượt là 5,72/15,16 giây với PaddleOCR và 10,92/4,92 giây với VietOCR. Throughput tính bằng 43 ảnh chia thời gian xử lý cả tập.

| Nhóm dữ liệu | Số ảnh | CER PaddleOCR | CER VietOCR | WER PaddleOCR | WER VietOCR |
| --- | ---: | ---: | ---: | ---: | ---: |
| Chứng từ kế toán | 22 | 17,85% | **10,17%** | 43,34% | **14,98%** |
| Hóa đơn và tài liệu liên quan | 21 | 20,55% | **8,79%** | 53,30% | **15,70%** |

Trong cấu hình đã đo, VietOCR giảm CER 9,70 điểm phần trăm và WER 32,86 điểm phần trăm, đồng thời đạt throughput gấp 3,67 lần nhánh PaddleOCR. Kết quả phản ánh toàn pipeline với các checkpoint nêu trên, không đại diện cho mọi cấu hình của hai thư viện.

## Phạm vi và giới hạn

Kết quả đáp ứng phần so sánh **tốc độ, tỷ lệ lỗi và điểm chất lượng văn bản** cho hai nhánh OCR. So sánh với Qwen3-VL-4B-Instruct và Ministral-3-3B-Instruct-2512 chưa có kết quả, nên baseline theo đầy đủ phạm vi mô hình trong đề bài chưa hoàn tất.

Chưa đo RAM/VRAM đỉnh, chi phí, Line/Numeric Exact Match và retry. Detection Recall, độ chính xác trường và cấu trúc bảng chưa được tính vì chưa có nhãn tương ứng. Tập 43 ảnh và một lượt đo/ảnh chưa đủ để suy rộng kết quả; ground truth được hiệu chỉnh từ nháp VietOCR nên còn nguy cơ giữ lại lỗi của bản nháp. Các phép đo hiện tại chưa bao gồm xử lý PDF.

Nguồn thực nghiệm: [manifest](ground_truth/manifest.json), [điểm PaddleOCR](outputs/paddleocr/scores_py312.json), [điểm VietOCR](outputs/vietocr/scores_py312.json), [cấu hình/thời gian PaddleOCR](outputs/paddleocr/run.json), [cấu hình/thời gian VietOCR](outputs/vietocr/run.json). Điểm đã được kiểm tra lại từ predictions và ground truth hiện tại; hash các file truth khớp báo cáo chấm. Thư mục `outputs/` hiện không được Git theo dõi.
