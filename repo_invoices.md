1. Các repository đáng chú ý:  
3 nhóm để lựa chọn: 
+ repo chuyên hóa đơn Việt Nam, 
+ framework OCR/Document Parsing
+ repo trích xuất thông tin kế toán.

*Nhóm A – Dự án chuyên hóa đơn, chứng từ tiếng Việt*

Mẫu hóa đơn điện tử có mã cơ quan thuế theo TT 78 và NĐ 123
 
1. VN-Invoice-Extractor

Ưu tiên cao
philipsgn/vn-invoice-extractor

GitHub repository https://github.com/philipsgn/vn-invoice-extractor  
Nhận dạng hóa đơn VAT, non-VAT và hóa đơn bán lẻ Việt Nam.

Kết hợp OCR đa phương thức, LLM và deep learning.

Có xử lý trích xuất trường, kiểm tra dữ liệu và xử lý nhiều hóa đơn.

Có nhánh xử lý local fallback.

Phù hợp: Xây dựng hệ thống nhập liệu hóa đơn kế toán Việt Nam.


GitHub
HH 563 (24.1.2025) - CVN Cvas | PDF
 
2. OCR-invoice

HoVDuc/OCR-invoice

GitHub repository https://github.com/HoVDuc/OCR-invoice  
PaddleOCR và VietOCR.

DB text detection.

VGG-Transformer recognition.

LayoutXLM cho Key Information Extraction.

Có thêm pipeline Gemini Vision để trích xuất thông tin.

Phù hợp: Nghiên cứu so sánh OCR truyền thống với Vision-Language Model.


GitHub
Hướng dẫn người mua tra cứu hoá đơn điện tử - Fast e-Invoice
 
3. VietReceipt

vietreceipt-team/vietreceipt

GitHub repository https://github.com/vietreceipt-team/vietreceipt  
Xử lý hóa đơn giấy, ảnh, PDF scan và PDF có text.

OCR → KIE → chuẩn hóa → kiểm tra → human review.

Xuất CSV, XLSX, JSON.

Có định hướng xây dựng bộ dữ liệu hóa đơn tiếng Việt tổng hợp và kiểm thử độc lập.

Phù hợp: Tham khảo kiến trúc ứng dụng kế toán có human-in-the-loop.


GitHub
Client Challenge
 
4. einvoice-lens

Python package – Vietnam e-invoice parsing

PyPI project https://pypi.org/project/einvoice-lens/  
OCR kết hợp rule-based parsing.

Đọc hóa đơn điện tử Việt Nam từ PDF.

Trích xuất dữ liệu hóa đơn có cấu trúc.

Có CLI để tích hợp vào pipeline.

Phù hợp: Tham khảo xử lý hóa đơn theo quy tắc nghiệp vụ Việt Nam.

*Nhóm B – Framework OCR và phân tích tài liệu PDF/ảnh*  

Đây là nhóm mình đánh giá quan trọng nhất nếu mục tiêu là phát triển một hệ thống có thể xử lý nhiều loại chứng từ, không chỉ hóa đơn.
 
5. PaddleOCR


PaddlePaddle/PaddleOCR

GitHub repository https://github.com/PaddlePaddle/PaddleOCR  
Thành phần đáng chú ý:

PP-OCR: text detection và recognition.

PP-StructureV3: phân tích cấu trúc tài liệu.

PaddleOCR-VL: mô hình Vision-Language cho document parsing.

Table Recognition: nhận dạng cấu trúc bảng.

Hỗ trợ PDF, ảnh và nhiều ngôn ngữ.

Ưu điểm: Có thể xây dựng pipeline từ OCR đến Markdown/JSON, phù hợp thử nghiệm tài liệu song ngữ.

Lưu ý: Cần kiểm tra chất lượng tiếng Việt trên hóa đơn thực tế, đặc biệt font nhỏ, dấu tiếng Việt và bảng nhiều cột.


GitHub
Visual Grounding from Docling! - DEV Community
 
6. Docling


docling-project/docling

GitHub repository  https://github.com/docling-project/docling  
Chuyển PDF, ảnh và tài liệu văn phòng thành cấu trúc có tổ chức.

Phân tích bảng, hình ảnh, text và layout.

Xuất Markdown, JSON.

Có thể tích hợp OCR backend.

Ưu điểm: Phù hợp xây dựng lớp document parsing trước khi trích xuất dữ liệu kế toán.

Lưu ý: Docling không phải hệ thống KIE hóa đơn hoàn chỉnh; cần thêm bước trích xuất trường.
 
7. Marker

VikParuchuri/marker

GitHub repository https://github.com/datalab-to/marker  
PDF/ảnh sang Markdown, JSON và HTML.

Phân tích layout, thứ tự đọc.

Trích xuất bảng, hình ảnh, công thức.

Kết hợp Surya OCR và LLM để cải thiện kết quả.

Ưu điểm: Hữu ích với báo cáo tài chính, báo cáo thường niên, tài liệu kế toán nhiều trang.

Lưu ý: Bảng phức tạp và form có cấu trúc lồng nhau vẫn cần kiểm tra.
 
8. Surya

VikParuchuri/surya

GitHub repository  https://github.com/datalab-to/surya 
OCR cho tài liệu.

Text detection.

Layout analysis.

Reading order.

Ưu điểm: Có thể dùng để nghiên cứu riêng lớp OCR và bố cục, hoặc làm thành phần trong pipeline Document AI.

*Nhóm C – Trích xuất thông tin kế toán và Invoice KIE*  
Nhóm này tập trung vào việc chuyển nội dung nhận dạng thành dữ liệu nghiệp vụ.

Multimodal Applications: Documents, Medical, Video, and Reasoning - Interactive | Michael Brenndoerfer | Michael Brenndoerfer
 
9. invoice-parser

manhsontran/invoice-parser

GitHub repository https://github.com/manhsontran/invoice-parser  
PaddleOCR và EasyOCR.

LayoutLMv3.

Trích xuất nhà cung cấp, ngày, số tiền và line items.

FastAPI và Streamlit.

Cấu hình tiếng Anh và tiếng Việt.

Phù hợp: Làm baseline ứng dụng OCR + KIE song ngữ.


GitHub

 
10. LayoutLM-Invoices

FrankZhaodong/LayoutLM-Invoices

GitHub repository https://github.com/FrankZhaodong/LayoutLM-Invoices  
OCR → tokens + bounding boxes.

LayoutLM và BERT kết hợp thông tin vị trí.

Token classification theo nhãn BIO.

Xuất JSON chứa thông tin hóa đơn.

Phù hợp: Nghiên cứu fine-tuning mô hình KIE với dữ liệu hóa đơn riêng.


GitHub
CORD Information Extraction Dataset | Datasets | HyperAI
 
11. invoice-kie

jhatch3/invoice-kie

GitHub repository https://github.com/jhatch3/invoice-kie  
Fine-tuning LayoutLMv3.

So sánh với Qwen2-VL.

Trích xuất trường tổng tiền, thuế, subtotal và line items.

Có thiết kế benchmark, tính Field F1 và Line-item F1.

Phù hợp: Nghiên cứu định lượng so sánh mô hình OCR/KIE truyền thống với VLM.


GitHub
Build a Document Extraction Pipeline With LLMs (Scanned PDFs, Images, DOCX, XLSX → Clean JSON) | by Tarun Singh | Jan, 2026 | Medium
 
12. InvoiceParser-AI

LeonAchata/InvoiceParser-AI

GitHub repository https://github.com/LeonAchata/InvoiceParser-AI  
PDF và scanned PDF.

Vision LLM trích xuất trường hóa đơn.

LangGraph workflow.

Kiểm tra tổng tiền, thuế, line items.

Xuất Excel/JSON và hỗ trợ PostgreSQL.

Phù hợp: Tham khảo kiến trúc tự động hóa xử lý hóa đơn đầu vào.

[Bổ sung 3/11/2026]

# HÓA ĐƠN/ CHỨNG TỪ
## 1. Dataset tiếng Việt

### 1. MC-OCR – Vietnamese Receipt Dataset

Ưu tiên số 1 cho OCR hóa đơn bán lẻ bill Object Detection Model by business

- Có tổng cộng 2.436 ảnh hóa đơn/biên lai tiếng Việt.
- Ảnh chụp bằng điện thoại, có các mức chất lượng khác nhau.
- Có annotation text, polygon/bounding box và nhãn semantic.
- Các trường thông tin gồm người bán, địa chỉ, thời gian, tổng tiền.
- Có train và test benchmark.

Nguồn:

- [MC-OCR – Dataset chính thức](<https://www.rivf2021-mc-ocr.vietnlp.com/dataset>)
- [Paper mô tả dataset](<https://people.cs.umu.se/sonvx/files/MCOCR_Preprint.pdf>)
- [HF, ver 17] (<https://www.kaggle.com/datasets/domixi1989/vietnamese-receipts-mc-ocr-2021>)

Lưu ý: Dataset yêu cầu đăng ký và ký thỏa thuận sử dụng dữ liệu nghiên cứu với VNDAG.

### 2. Vietnamese Bill Extraction VLM Dataset

Ưu tiên số 2 cho trích xuất thông tin- Ảnh hóa đơn và phiếu thu tiếng Việt.
- Có dữ liệu đã kiểm duyệt và chuẩn hóa.
- Phục vụ OCR nâng cao, Document Understanding và KIE.
- Có thông tin sản phẩm/dịch vụ, số lượng, đơn giá, tổng tiền.

[HF](<https://huggingface.co/datasets/minhduc168/dataset-origin-vlm-extract-bill>)

### 3. Nghiên cứu 731 hóa đơn Việt Nam

Đây là một nguồn rất đáng tìm hiểu:

- Nghiên cứu sử dụng 731 ảnh hóa đơn từ các cửa hàng tại Việt Nam.
- Ảnh được chụp bằng smartphone.
- Có bài toán OCR kết hợp trích xuất thông tin.
- Sử dụng VietOCR và Graph Convolutional Network.

[Paper: Information Extraction from Invoices – Vietnamese Stores](<https://www.kci.go.kr/kciportal/ci/sereArticleSearch/ciSereArtiView.kci?sereArticleSearchBean.artiId=ART002891221&utm_source=chatgpt.com>)

Lưu ý: Bài nghiên cứu xác nhận có 731 hóa đơn, nhưng chưa xác minh được bộ dữ liệu gốc được công khai để tải về.


## 2. Tổng hợp mức độ phù hợp

| Dataset | Quy mô | Loại dữ liệu | Mức phù hợp |
| --- | --- | --- | --- |
| MC-OCR | 2.436 | Receipt Việt Nam | Rất cao |
| Vietnamese Bill Extraction | 982 | Hóa đơn/phiếu thu | Cao |
| Nghiên cứu 731 invoices | 731 | Hóa đơn cửa hàng | Cao |

## 3. Đề xuất cho dự án của bạn

Mình sẽ ưu tiên tải và kiểm tra theo thứ tự:

1. MC-OCR: làm benchmark OCR text detection/recognition.
2. Vietnamese Bill Extraction: benchmark trích xuất JSON.
3. UIT-MLReceipts: bổ sung benchmark receipt nếu lấy được dữ liệu.
4. Tự xây dựng một tập test riêng gồm 200–300 hóa đơn VAT điện tử, PDF scan và ảnh chụp thực tế.

Có một điểm quan trọng: hóa đơn bán lẻ và hóa đơn VAT điện tử không hoàn toàn cùng một distribution. Vì vậy, dù có 2.000 ảnh receipt tiếng Việt, vẫn chưa đủ để khẳng định baseline tốt trên hóa đơn VAT.

Mình khuyên nên xây dựng benchmark riêng cho hóa đơn VAT thay vì gộp tất cả thành một tập test duy nhất.

# Báo cáo tài chính:

Với báo cáo tài chính dài 40–100 trang, bài toán này đã có một hướng nghiên cứu riêng, thường được gọi là **Financial Document Understanding (FDU)** hoặc **Financial Report Understanding**.

Khác với OCR hóa đơn, bài toán không chỉ là nhận diện chữ trong ảnh/PDF. Hệ thống cần hiểu cấu trúc tài liệu dài, bảng biểu tài chính, quan hệ giữa các chỉ tiêu, số liệu qua nhiều năm và đôi khi phải trả lời câu hỏi dựa trên nhiều trang.

Hướng nghiên cứu: Financial Document Understanding Benchmarking

## 1. Những dự án và research đã có

Có một số dự án rất đáng tham khảo. Tuy nhiên, cần phân biệt chúng giải quyết OCR, table extraction hay financial reasoning.

## 2. Các dự án tiếng Việt sát nhất với bài toán

1. TiniX Vietnam OCR Annual Financial Statements

- 18.231 báo cáo tài chính tiếng Việt.
- 1.491 mã chứng khoán.
- Dữ liệu giai đoạn 2015–2025.
- Bao gồm BCTC hợp nhất, công ty mẹ, báo cáo kiểm toán, thuyết minh BCTC.
- Mỗi báo cáo có một file text OCR chứa nội dung toàn tài liệu.
- Dataset card công bố độ chính xác trên dữ liệu số và bảng biểu là 95% (đây là số liệu do bên phát hành công bố, chưa phải kết quả benchmark độc lập).

Phù hợp: nghiên cứu OCR trên tài liệu tài chính nhiều trang, xử lý PDF, RAG và extraction.

- [Dataset HF](<https://huggingface.co/datasets/thuongdz/ocr_annual_financials>)
- [TiniX AI](<https://tinix.ai/>)

License: CC BY-NC 4.0. Cần kiểm tra quyền sử dụng nếu dự án có mục đích thương mại.


2. VietFinTab


Đây là dataset chuyên về bảng biểu tài chính Việt Nam.

- 10.383 ảnh bảng biểu.
- 10.383 annotation cấu trúc bảng XML.
- 1.000 bảng có annotation nội dung ô và bounding box.
- Thu thập từ báo cáo tài chính của 13 doanh nghiệp Việt Nam.
- Có thể dùng cho Table Detection, Table Structure Recognition, OCR và Table Parsing.

Phù hợp: đánh giá khả năng nhận diện bảng cân đối kế toán, báo cáo kết quả kinh doanh và lưu chuyển tiền tệ.

- [VietFinTab Dataset HF](<https://huggingface.co/datasets/VietFinTabGroup/VietFinTab>)

License: CC BY-NC 4.0.

3. ViFinQA – Vietnamese Financial QA **tham khảo**

OCR -> hiểu nội dung báo cáo tài chính.

- 1.012 câu hỏi tiếng Việt.
- 1.973 báo cáo OCR.
- 100 doanh nghiệp niêm yết.
- Dữ liệu 2015–2025.
- Câu hỏi về doanh thu, lợi nhuận, chi phí, tài sản, dòng tiền và tính toán số liệu.

Ví dụ câu hỏi:

- Lợi nhuận sau thuế năm 2023 là bao nhiêu?
- Chi phí tài chính tăng bao nhiêu so với năm trước?
- Dòng tiền từ hoạt động kinh doanh thay đổi thế nào?

Phù hợp: đánh giá LLM, RAG, retrieval và khả năng reasoning trên báo cáo tài chính Việt Nam.

- [ViFinQA Dataset](<https://huggingface.co/datasets/AIGuruTinix/ViFinQA>)
- [ViFinQA GitHub](<https://github.com/DSKT-NOWJ/ViFinQA>)

**Lưu ý quan trọng:** bản public trên Hugging Face có câu hỏi và tài liệu OCR nhưng không chứa đầy đủ answer labels, gold evidence hay train/test split chính thức. Muốn tái lập benchmark cần kiểm tra thêm repository đi kèm.


## 3. Các dự án quốc tế tham khảo về xử lý tài liệu dài

Đây là các benchmark có thể giúp thiết kế phương pháp đánh giá tốt hơn, không phải tiếng Việt.

| Dự án | Quy mô/đặc điểm | Bài toán |
| --- | --- | --- |
| FinLongDocQA | Báo cáo thường niên dài, hơn 129K tokens trong nhiều tài liệu | Reasoning trên nhiều bảng |
| LEDGER | 4.999 báo cáo, median 124 trang | Retrieval và KPI extraction |
| FinTabNet | Hơn 100K bảng từ báo cáo doanh nghiệp | Table extraction |
| FinanceBench | Câu hỏi dựa trên hồ sơ tài chính doanh nghiệp | Financial QA |

Nguồn:

- [FinLongDocQA](<https://huggingface.co/datasets/Amian/FinLongDocQA>)
- [LEDGER GitHub](<https://github.com/artefactory/LEDGER>)
- [FinTabNet](<https://github.com/ibm/FinTabNet>)
- [FinanceBench](<https://github.com/patronus-ai/financebench>)

LEDGER không chỉ đo việc model trả lời đúng mà còn đánh giá khả năng tìm đúng trang chứa KPI và trích xuất nhiều KPI từ toàn bộ báo cáo. Dataset có median 124 trang, khá gần với bài toán đang làm.


## 4. research cho baseline báo cáo tài chính 40–100 trang:

Chia thành 4 bài toán độc lập để không bị nhầm lẫn giữa OCR và khả năng hiểu tài liệu.

Pipeline:

PDF báo cáo tài chính (40–100 trang)

Document preprocessing (PDF parsing, page rendering, phân loại trang)

OCR (PaddleOCR, VietOCR) và Table extraction (PP-Structure, Table models); chữ viết tay, dấu mộc, giả mạo.

Document structure (Page, section, heading, table, paragraph)

Financial Document Understanding (LLM, RAG, KPI extraction, financial QA)

### Nhóm thực nghiệm triển khai

| Nhóm | Nội dung đánh giá | Metric |
| --- | --- | --- |
| OCR | Nhận diện text trên từng trang | CER, WER |
| Table extraction | Nhận diện cấu trúc bảng, số liệu | TEDS, cell accuracy |
| Document parsing | Phân loại trang, section, heading | F1 |
| Financial QA | Trả lời câu hỏi dựa trên toàn báo cáo | Exact Match, F1, evidence accuracy |

Với báo cáo tài chính, đặc biệt quan trọng là đánh giá:

- Khả năng nhận diện số âm, số trong ngoặc.
- Phân biệt đơn vị đồng, nghìn đồng, triệu đồng.
- Phân biệt cột năm hiện tại và năm trước.
- Bảng nhiều tầng header.
- Bảng kéo dài qua nhiều trang.
- Quan hệ giữa số liệu trong báo cáo chính và thuyết minh.

### Bộ model baseline:

| Nhóm | Model / công cụ |
| --- | --- |
| OCR | PaddleOCR |
| Vietnamese recognition | VietOCR |
| Layout & table | PP-StructureV3 |
| Table structure | Table Transformer |
| Vision LLM | Qwen2.5-VL |
| LLM extraction / QA | GPT, Gemini, Qwen |
| Retrieval | BM25 + multilingual embedding + reranker |

Chọn 4–5 cấu hình đại diện để benchmark, ko đưa hết vào.

## 5. Dataset:

Baseline nghiên cứu:

| Thành phần | Quy mô |
| --- | --- |
| Báo cáo tài chính | 50–100 PDF |
| Tổng số trang | 2.000–5.000 |
| Trang có annotation OCR | 300–500 |
| Bảng có annotation chi tiết | 100–200 |
| Câu hỏi financial QA | 200–300 |

Không cần gán nhãn toàn bộ 5.000 trang.  
Chọn các trang đại diện cho từng loại nội dung: trang văn bản, bảng tài chính, thuyết minh, trang scan và trang có bảng phức tạp.