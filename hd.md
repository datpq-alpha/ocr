# Phạm vi và phương pháp đánh giá OCR tài liệu kế toán

Cập nhật: 30/10/2026. Tài liệu xác định phạm vi dữ liệu, phương pháp đánh giá và kế hoạch xây dựng baseline. Tổng hợp mô hình và kết quả benchmark công bố được trình bày trong [research.md](research.md).

## 1. Mục tiêu và phạm vi

Bài toán gồm nhận dạng văn bản và trích xuất thông tin từ ảnh chụp chứng từ, hóa đơn và PDF. Chất lượng nhận dạng ký tự và chất lượng gán trường dữ liệu được đánh giá riêng: văn bản đọc đúng vẫn có thể bị gán sai trường hoặc sai cột số liệu.

| Giai đoạn | Phạm vi |
| --- | --- |
| Hai tuần đầu | Khảo sát PaddleOCR, VietOCR và ít nhất hai mô hình ngôn ngữ nhận ảnh; xây dựng baseline chữ và số; đo độ chính xác, tỷ lệ lỗi, thời gian xử lý và tài nguyên |
| Ba tuần tiếp theo | OCR bảng biểu, chữ viết tay, dấu mộc và dấu hiệu giả mạo tài liệu |

Baseline sử dụng mô hình pretrained, không bao gồm huấn luyện mô hình mới. Đánh giá trích xuất trường và cấu trúc bảng được thực hiện khi có dữ liệu gán nhãn tương ứng.

## 2. Dữ liệu và hệ thống nhãn

Kho [Accounting_Documents](Accounting_Documents/README.md) gồm 7 nhóm: báo cáo tài chính, chứng từ kế toán, hóa đơn, tài liệu thuế, sao kê ngân hàng, hợp đồng và tài liệu khác. Tập dữ liệu ban đầu có 15 PDF tại `Accounting_Documents/01_Financial_Reports/06_2026/`.

Metadata được quản lý bằng [taxonomy](metadata/taxonomy.json), [JSON Schema](metadata/document.schema.json) và [danh mục tài liệu](metadata/documents.jsonl), phiên bản 2.1.0. Hệ thống có 88 loại tài liệu chuẩn, 22 tag nghiệp vụ và hai bộ mã tra cứu:

- [AV001–AV047](metadata/ACCOUNTING_VOUCHER_MAPPING.md): 47 mục thuộc 7 nhóm chứng từ kế toán.
- [INV001–INV034](metadata/INVOICE_MAPPING.md): 34 mục về hóa đơn và tài liệu liên quan.

Tổng cộng 81 mã tra cứu không tương đương 81 lớp phân loại độc lập. Các mã INV có thể cùng mô tả một tài liệu; AV003 và INV018 dùng chung loại Cash_Receipt. Nhóm nghiệp vụ, vị trí lưu và thuộc tính tài liệu được quản lý riêng.

Tên thư mục và tên file không thay thế nhãn chuẩn. Loại tài liệu, công ty, ngôn ngữ, nguồn và thông tin nghiệp vụ chưa xác minh được để `null`, với trạng thái phân loại `Needs_Review`.

### 2.1. Loại đầu vào

| Đầu vào | Đặc điểm xử lý |
| --- | --- |
| PDF có lớp văn bản | Kiểm tra khả năng trích xuất trực tiếp; đánh giá độ phủ và thứ tự đọc |
| PDF scan | Xử lý ảnh trang qua OCR; chất lượng phụ thuộc độ rõ, độ nghiêng và kích thước chữ |
| Ảnh chụp | Có thể xuất hiện méo phối cảnh, bóng đổ, ánh sáng không đều, nhòe và nền phức tạp |
| PDF hỗn hợp | Phân loại theo từng trang hoặc vùng để tránh áp dụng một phương thức cho toàn bộ file |

Kết quả được phân tầng theo nguồn đầu vào và ngôn ngữ. `format` mô tả định dạng file, `source` mô tả nguồn ảnh/file, còn `issuance_form` mô tả hình thức phát hành; các trường này không được suy ra trực tiếp từ nhau.

## 3. Độ dài và đặc điểm tài liệu

### 3.1. Khoảng số trang phục vụ lập kế hoạch

Các khoảng dưới đây được tổng hợp từ nội dung thiết kế dữ liệu, chưa phải thống kê thực nghiệm trên kho tài liệu hiện tại. Số trang thực tế phụ thuộc mẫu biểu, phụ lục và cách đóng gói hồ sơ.

| Nhóm chứng từ | Mã | Khoảng số trang tham khảo |
| --- | --- | --- |
| Tiền mặt | AV001–AV007 | 1–2 |
| Ngân hàng | AV008–AV014 | 1–3 |
| Kho | AV015–AV020 | 1–2 |
| Tiền lương và nhân sự | AV021–AV026 | 1–5 |
| Tài sản cố định | AV027–AV032 | 1–3 |
| Mua bán hàng hóa, dịch vụ | AV033–AV040 | 1–5 |
| Kế toán tổng hợp | AV041–AV047 | 1–5 |

| Nhóm hóa đơn và tài liệu liên quan | Mã | Khoảng số trang tham khảo |
| --- | --- | --- |
| Bán hàng và cung cấp dịch vụ | INV001–INV006 | 1–2 |
| Mua hàng và chi phí | INV007–INV012 | 1–2 |
| Điều chỉnh và thay thế | INV013–INV016 | 1–3 |
| Thanh toán và biên lai | INV017–INV022 | 1–2 |
| Tài sản và đầu tư | INV023–INV027 | 1–3 |
| Hóa đơn đặc thù | INV028–INV034 | 1–3 |

### 3.2. Phân nhóm theo số trang

| Mã | Tên | Số trang |
| --- | --- | --- |
| PG001 | Single Page | 1 |
| PG002 | Short Document | 2–3 |
| PG003 | Medium Document | 4–10 |
| PG004 | Long Document | Trên 10 |

Số trang được xác định từ file thực tế, không gán mặc định theo mã AV/INV. `page_count` và `page_category` thuộc thiết kế mở rộng; hai trường này chưa được khai báo trong schema metadata 2.1.0.

### 3.3. Báo cáo tài chính

PDF MBS được nêu trong [đề bài](debai.md) là tài liệu thuộc nhóm báo cáo tài chính. Các đặc điểm cần kiểm tra trên từng trang gồm:

| Thành phần | Nội dung đánh giá |
| --- | --- |
| Bảng nhiều cột | Quan hệ giữa chỉ tiêu, kỳ báo cáo, đơn vị tính và giá trị |
| Thuyết minh | Văn bản dài, tiêu đề phân cấp, số tham chiếu và thứ tự đọc |
| Số liệu kế toán | Dấu âm, ngoặc, số 0, dấu gạch ngang, dấu phân cách và đơn vị tiền tệ |
| Hồ sơ nhiều thành phần | Công văn, báo cáo kiểm toán/soát xét và báo cáo tài chính trong cùng PDF |

Đọc đúng một giá trị nhưng gán sai kỳ báo cáo vẫn là lỗi trích xuất. Chỉ số nhận dạng ký tự và chỉ số khôi phục quan hệ hàng/cột được báo cáo riêng.

## 4. Quy mô dữ liệu và nhãn chuẩn

Tập thử nghiệm ban đầu gồm khoảng 10–15 trang đại diện cho văn bản, bảng nhiều số, chữ nhỏ và các mức chất lượng ảnh khác nhau. Phạm vi mở rộng 300–500 tài liệu phụ thuộc khả năng thu thập, gán nhãn và tài nguyên; không phải điều kiện bắt buộc của baseline hai tuần.

Quy mô bao phủ theo 81 mã được biểu diễn bằng số lượt gán nhãn:

| Số mẫu cho mỗi mã | Lượt bao phủ trên 81 mã |
| ---: | ---: |
| 10 | 810 |
| 30 | 2.430 |
| 50 | 4.050 |
| 100 | 8.100 |

Một file có thể đáp ứng nhiều mã, vì vậy các tổng trên không phải số file duy nhất. Số tài liệu thực tế được xác định sau khi loại trùng. Độ phủ dữ liệu còn phụ thuộc nhà phát hành, mẫu biểu, số trang và chất lượng ảnh, không chỉ số mẫu mỗi mã.

Nhãn chuẩn (ground truth) gồm văn bản được kiểm tra thủ công, vùng đánh giá, thứ tự đọc và các trường nghiệp vụ thuộc phạm vi thử nghiệm. Nội dung không đọc được được đánh dấu riêng; trường chưa rõ hoặc không áp dụng dùng `null`.

Tập phát triển và tập kiểm thử được tách theo tài liệu, mẫu biểu hoặc đơn vị phát hành khi có thể. Trang trùng, bản dịch và ảnh biến đổi từ cùng nguồn nằm trong cùng tập. Đầu ra OCR có thể làm bản nháp; nhãn chuẩn được xác lập sau khi đối chiếu thủ công.

## 5. Cấu trúc pipeline

Quy trình xử lý gồm kiểm tra đầu vào, tiền xử lý ảnh, nhận dạng văn bản, sắp xếp kết quả và trích xuất dữ liệu theo schema khi có tác vụ tương ứng.

| Pipeline | Chức năng | Phạm vi đánh giá |
| --- | --- | --- |
| Trích xuất PDF trực tiếp | Đọc lớp văn bản bằng thư viện PDF | Đối chứng cho trang có text; báo cáo riêng với OCR trên ảnh |
| PaddleOCR/PP-OCR | Phát hiện vùng chữ và nhận dạng | Baseline OCR toàn trang |
| Detector + VietOCR | Cắt vùng chữ và nhận dạng tiếng Việt | Đánh giá recognition và toàn pipeline |
| VLM độc lập thứ nhất | Qwen3-VL-4B-Instruct nhận ảnh và sinh văn bản | Đối chứng với VLM thứ hai, PaddleOCR và VietOCR |
| VLM độc lập thứ hai | Ministral-3-3B-Instruct-2512 nhận ảnh và sinh văn bản | So sánh giữa hai dòng mô hình ngôn ngữ trên cùng dữ liệu |
| PaddleOCR-VL | VLM chuyên tài liệu thuộc PaddleOCR | Cấu hình mở rộng, ghi nhận riêng với PP-OCR |
| OCR + parser hoặc LLM | Gán trường và kiểm tra dữ liệu sau OCR | Phần mở rộng trích xuất thông tin |

Danh mục mô hình, phiên bản, giấy phép và kết quả công bố nằm trong [research.md](research.md). Cấu hình OCR và parser được ghi nhận riêng để phân biệt lỗi nhận dạng với lỗi ánh xạ dữ liệu.

## 6. Thiết kế thực nghiệm

Hai mức đánh giá OCR gồm nhận dạng trên cùng ảnh cắt chuẩn và xử lý toàn trang. Phép thử ảnh cắt đo khả năng đọc chữ; phép thử toàn trang bao gồm phát hiện vùng chữ, bỏ sót nội dung và thứ tự đọc. Chất lượng detection chỉ được định lượng khi có nhãn vị trí tương ứng.

Đánh giá trích xuất thông tin sử dụng đầu ra JSON theo schema chung, tách khỏi điểm OCR thuần. Với VLM, tác vụ chép văn bản và tác vụ trích xuất trường sử dụng prompt riêng, cố định trước khi chạy tập kiểm thử.

Điều kiện thực nghiệm gồm:

1. Cùng tập kiểm thử, nhãn chuẩn và quy tắc chuẩn hóa; không điều chỉnh checkpoint, prompt hoặc ngưỡng theo kết quả test.
2. Cùng ảnh đầu vào đã lưu; mọi resize và tiền xử lý riêng của mô hình được ghi nhận. Độ phân giải khảo sát ban đầu là 200–300 DPI, sau đó cố định trên tập phát triển.
3. Ghi phần cứng, hệ điều hành, phiên bản thư viện, checkpoint, backend, batch size và độ chính xác tính toán; kết quả CPU/GPU được phân nhóm.
4. Đo riêng khởi tạo, render PDF, inference và tổng thời gian pipeline. Thời gian VietOCR toàn trang bao gồm detector và cắt ảnh.
5. Chạy warm-up, lặp phép đo và báo cáo số trang, số lần chạy, p50/p95. Nếu dùng API, thời gian toàn trình gồm truyền ảnh, độ trễ mạng và retry.
6. Lưu đầu ra nguyên bản, log lỗi và mẫu ảnh đối chiếu. Trang chưa có nhãn chỉ tham gia đánh giá vận hành.

## 7. Chỉ số đánh giá

### 7.1. OCR và vận hành

| Chỉ số | Nội dung |
| --- | --- |
| CER | Tỷ lệ lỗi ký tự |
| WER | Tỷ lệ lỗi từ |
| Line Exact Match | Tỷ lệ dòng đúng hoàn toàn |
| Numeric Exact Match | Tỷ lệ chuỗi số đúng, giữ dấu và dấu phân cách |
| Detection Recall | Độ phủ vùng chữ trên tập có nhãn vị trí |
| Latency p50/p95 | Phân bố thời gian xử lý mỗi trang |
| Throughput | Số trang xử lý trên đơn vị thời gian với cấu hình đã ghi nhận |
| Failure/Retry Rate | Tỷ lệ lỗi chạy, timeout, đầu ra không hợp lệ và chạy lại |
| RAM/VRAM | Mức sử dụng bộ nhớ và giá trị đỉnh |
| Chi phí/1.000 trang | Chi phí theo cấu hình chạy hoặc API, kèm giả định tính toán |

$$
CER = \frac{S + D + I}{N}
$$

Trong đó, $S$, $D$, $I$ lần lượt là số ký tự bị thay thế, xóa và chèn; $N$ là số ký tự của nhãn chuẩn. CER/WER được tính trên văn bản gốc và bản chuẩn hóa Unicode/khoảng trắng theo quy tắc cố định. Dấu tiếng Việt và dấu của số liệu được bảo toàn.

### 7.2. Trích xuất trường và bảng

| Chỉ số | Nội dung |
| --- | --- |
| Field Exact Match, Precision/Recall/F1 | Độ chính xác giá trị, trường thiếu và trường thừa |
| Critical Field Accuracy | Độ chính xác riêng của trường trọng yếu như ngày, mã số thuế và tổng tiền |
| JSON Validity | Tỷ lệ đầu ra hợp lệ theo schema |
| Cell/Line-item Accuracy | Độ chính xác ô hoặc dòng dữ liệu |
| Row/Column Alignment | Khả năng gán số liệu đúng chỉ tiêu và kỳ báo cáo |
| Sign Accuracy | Độ chính xác dấu âm, ngoặc và số 0 |
| Table Structure | Khả năng khôi phục hàng, cột, tiêu đề và ô gộp |
| Record Exact Match | Tỷ lệ bản ghi đúng toàn bộ các thành phần đã quy định |

Các chỉ số này chỉ được tính khi có nhãn tương ứng. Điểm trung bình được trình bày cùng kết quả từng trường trọng yếu để phản ánh lỗi số liệu có tác động lớn.

## 8. Giới hạn và nguồn sai số

Lỗi được phân loại thành: phát hiện thiếu vùng chữ; sai dấu tiếng Việt; nhầm ký tự/số; sai thứ tự đọc; gán nhầm trường hoặc cột; bỏ sót và tự thêm nội dung. Kết quả được phân tích theo loại tài liệu, mẫu biểu và chất lượng ảnh.

Khả năng hỗ trợ tiếng Việt được kiểm tra ở đúng checkpoint và cấu hình recognition. Số liệu công bố trên benchmark khác không thay thế kết quả trên tài liệu của dự án. Văn bản, số liệu tài chính và cấu trúc bảng cần được đối chiếu riêng.

Nếu sử dụng API ngoài hệ thống, điều kiện sử dụng dữ liệu, chi phí và cấu hình xử lý được ghi nhận trong hồ sơ thực nghiệm. Các giá trị không đủ bằng chứng không được tự điền từ suy luận ngữ cảnh.

## 9. Kế hoạch hai tuần

| Thời gian | Nội dung | Sản phẩm |
| --- | --- | --- |
| Ngày 1–2 | Khảo sát mô hình, kiểm tra dữ liệu, xác định metric và quy trình gán nhãn | Danh mục mô hình, tập trang pilot, quy tắc đánh giá |
| Ngày 3–5 | Chuẩn hóa ảnh/PDF, tích hợp PaddleOCR và VietOCR, thống nhất đầu ra | Pipeline baseline và log xử lý |
| Ngày 6–8 | Tích hợp hai VLM, chạy nhận dạng và đánh giá trên tập có nhãn | Bảng kết quả chất lượng, tốc độ và tài nguyên theo từng cấu hình |
| Ngày 9–10 | Phân tích lỗi, kiểm tra khả năng tái lập, hoàn thiện báo cáo | Báo cáo so sánh và bộ ví dụ lỗi |

Kế hoạch giả định dữ liệu và môi trường chạy sẵn có. Các phép thử trích xuất trường chỉ được đưa vào khi đã có nhãn và còn đủ thời gian; benchmark bảng chuyên sâu thuộc giai đoạn sau.

## 10. Sản phẩm và tiêu chí nghiệm thu

- Báo cáo khảo sát mô hình có nguồn, phiên bản benchmark, giấy phép và giới hạn so sánh.
- Bộ dữ liệu kiểm thử và nhãn chuẩn được kiểm tra thủ công, có quy tắc chia tập rõ ràng.
- Mã benchmark có cấu hình cố định, đầu ra thống nhất và khả năng chạy lại.
- Bảng so sánh chất lượng OCR, tốc độ, tài nguyên, lỗi vận hành và chi phí nếu phát sinh.
- Phân tích lỗi theo nhóm dữ liệu, kèm ảnh và kết quả đối chiếu; điểm trích xuất trường/bảng được báo cáo riêng khi có nhãn.

Ngưỡng chất lượng được xác định theo dữ liệu và yêu cầu sử dụng. Việc nghiệm thu baseline dựa trên tính đầy đủ, công bằng và khả năng tái lập của phép đo; báo cáo hiện chưa có kết quả thực nghiệm OCR trên tập PDF của dự án.
