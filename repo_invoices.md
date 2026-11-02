1. Các repository đáng chú ý
Mình chia thành 3 nhóm để dễ lựa chọn: repo chuyên hóa đơn Việt Nam, framework OCR/Document Parsing và repo trích xuất thông tin kế toán.

Nhóm A – Dự án chuyên hóa đơn, chứng từ tiếng Việt
Đây là nhóm nên ưu tiên đọc mã nguồn trước vì gần với dữ liệu ứng dụng của bạn nhất.

Mẫu hóa đơn điện tử có mã cơ quan thuế theo TT 78 và NĐ 123
 
1. VN-Invoice-Extractor

Ưu tiên cao
philipsgn/vn-invoice-extractor

GitHub repository https://github.com/philipsgn/vn-invoice-extractor?utm_source=chatgpt.com  
Nhận dạng hóa đơn VAT, non-VAT và hóa đơn bán lẻ Việt Nam.

Kết hợp OCR đa phương thức, LLM và deep learning.

Có xử lý trích xuất trường, kiểm tra dữ liệu và xử lý nhiều hóa đơn.

Có nhánh xử lý local fallback.

Phù hợp: Xây dựng hệ thống nhập liệu hóa đơn kế toán Việt Nam.


GitHub
HH 563 (24.1.2025) - CVN Cvas | PDF
 
2. OCR-invoice

HoVDuc/OCR-invoice

GitHub repository https://github.com/HoVDuc/OCR-invoice?utm_source=chatgpt.com  
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

GitHub repository https://github.com/vietreceipt-team/vietreceipt?utm_source=chatgpt.com  
Xử lý hóa đơn giấy, ảnh, PDF scan và PDF có text.

OCR → KIE → chuẩn hóa → kiểm tra → human review.

Xuất CSV, XLSX, JSON.

Có định hướng xây dựng bộ dữ liệu hóa đơn tiếng Việt tổng hợp và kiểm thử độc lập.

Phù hợp: Tham khảo kiến trúc ứng dụng kế toán có human-in-the-loop.


GitHub
Client Challenge
 
4. einvoice-lens

Python package – Vietnam e-invoice parsing

PyPI project https://pypi.org/project/einvoice-lens/?utm_source=chatgpt.com  
OCR kết hợp rule-based parsing.

Đọc hóa đơn điện tử Việt Nam từ PDF.

Trích xuất dữ liệu hóa đơn có cấu trúc.

Có CLI để tích hợp vào pipeline.

Phù hợp: Tham khảo xử lý hóa đơn theo quy tắc nghiệp vụ Việt Nam.


PyPI
Nhóm B – Framework OCR và phân tích tài liệu PDF/ảnh
Đây là nhóm mình đánh giá quan trọng nhất nếu mục tiêu là phát triển một hệ thống có thể xử lý nhiều loại chứng từ, không chỉ hóa đơn.
 
5. PaddleOCR


PaddlePaddle/PaddleOCR

GitHub repository https://github.com/PaddlePaddle/PaddleOCR?utm_source=chatgpt.com  
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

GitHub repository  https://github.com/docling-project/docling?utm_source=chatgpt.com  
Chuyển PDF, ảnh và tài liệu văn phòng thành cấu trúc có tổ chức.

Phân tích bảng, hình ảnh, text và layout.

Xuất Markdown, JSON.

Có thể tích hợp OCR backend.

Ưu điểm: Phù hợp xây dựng lớp document parsing trước khi trích xuất dữ liệu kế toán.

Lưu ý: Docling không phải hệ thống KIE hóa đơn hoàn chỉnh; cần thêm bước trích xuất trường.

marker | PDF 转 Markdown 工具
 
7. Marker

VikParuchuri/marker

GitHub repository https://github.com/datalab-to/marker?utm_source=chatgpt.com  
PDF/ảnh sang Markdown, JSON và HTML.

Phân tích layout, thứ tự đọc.

Trích xuất bảng, hình ảnh, công thức.

Kết hợp Surya OCR và LLM để cải thiện kết quả.

Ưu điểm: Hữu ích với báo cáo tài chính, báo cáo thường niên, tài liệu kế toán nhiều trang.

Lưu ý: Bảng phức tạp và form có cấu trúc lồng nhau vẫn cần kiểm tra.


Mozilla Builders
+1
Using SuryaOCR with Docling. Combination of Docling with SuryaOCR. | by Alain Airom (Ayrom) | Jan, 2026 | Medium
 
8. Surya

VikParuchuri/surya

GitHub repository  https://github.com/datalab-to/surya?utm_source=chatgpt.com 
OCR cho tài liệu.

Text detection.

Layout analysis.

Reading order.

Ưu điểm: Có thể dùng để nghiên cứu riêng lớp OCR và bố cục, hoặc làm thành phần trong pipeline Document AI.

Nhóm C – Trích xuất thông tin kế toán và Invoice KIE
Nhóm này tập trung vào việc chuyển nội dung nhận dạng thành dữ liệu nghiệp vụ.

Multimodal Applications: Documents, Medical, Video, and Reasoning - Interactive | Michael Brenndoerfer | Michael Brenndoerfer
 
9. invoice-parser

manhsontran/invoice-parser

GitHub repository https://github.com/manhsontran/invoice-parser?utm_source=chatgpt.com  
PaddleOCR và EasyOCR.

LayoutLMv3.

Trích xuất nhà cung cấp, ngày, số tiền và line items.

FastAPI và Streamlit.

Cấu hình tiếng Anh và tiếng Việt.

Phù hợp: Làm baseline ứng dụng OCR + KIE song ngữ.


GitHub

 
10. LayoutLM-Invoices

FrankZhaodong/LayoutLM-Invoices

GitHub repository https://github.com/FrankZhaodong/LayoutLM-Invoices?utm_source=chatgpt.com  
OCR → tokens + bounding boxes.

LayoutLM và BERT kết hợp thông tin vị trí.

Token classification theo nhãn BIO.

Xuất JSON chứa thông tin hóa đơn.

Phù hợp: Nghiên cứu fine-tuning mô hình KIE với dữ liệu hóa đơn riêng.


GitHub
CORD Information Extraction Dataset | Datasets | HyperAI
 
11. invoice-kie

jhatch3/invoice-kie

GitHub repository https://github.com/jhatch3/invoice-kie?utm_source=chatgpt.com  
Fine-tuning LayoutLMv3.

So sánh với Qwen2-VL.

Trích xuất trường tổng tiền, thuế, subtotal và line items.

Có thiết kế benchmark, tính Field F1 và Line-item F1.

Phù hợp: Nghiên cứu định lượng so sánh mô hình OCR/KIE truyền thống với VLM.


GitHub
Build a Document Extraction Pipeline With LLMs (Scanned PDFs, Images, DOCX, XLSX → Clean JSON) | by Tarun Singh | Jan, 2026 | Medium
 
12. InvoiceParser-AI

LeonAchata/InvoiceParser-AI

GitHub repository https://github.com/LeonAchata/InvoiceParser-AI?utm_source=chatgpt.com  
PDF và scanned PDF.

Vision LLM trích xuất trường hóa đơn.

LangGraph workflow.

Kiểm tra tổng tiền, thuế, line items.

Xuất Excel/JSON và hỗ trợ PostgreSQL.

Phù hợp: Tham khảo kiến trúc tự động hóa xử lý hóa đơn đầu vào.


GitHub
