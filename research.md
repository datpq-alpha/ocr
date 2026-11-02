# Khảo sát PaddleOCR, VietOCR và mô hình ngôn ngữ đa phương thức cho OCR

Mốc đối chiếu nguồn: 30/10/2026. Phạm vi báo cáo là baseline OCR trong hai tuần đầu theo [debai.md](debai.md), sử dụng mô hình có sẵn để so sánh tốc độ, tỷ lệ lỗi và độ chính xác trên ảnh chứng từ, hóa đơn và PDF.

Các cấu hình dưới đây thuộc thiết kế thực nghiệm. Dự án chưa có kết quả đo OCR trên tập PDF hiện tại. Mô hình và benchmark phân tích tài liệu mở rộng được trình bày trong phụ lục.

## 1. Phạm vi theo đề bài

| Nội dung đề bài | Phạm vi khảo sát |
| --- | --- |
| PaddleOCR | Pipeline phát hiện và nhận dạng chữ bằng PP-OCR |
| VietOCR | Nhận dạng tiếng Việt, kết hợp detector để xử lý toàn trang |
| Các LLM | Hai mô hình ngôn ngữ đa phương thức thuộc hai dòng Qwen và Mistral, nhận ảnh trực tiếp cho tác vụ chép văn bản |
| So sánh tốc độ, tỷ lệ lỗi, độ chính xác | Đánh giá trên cùng dữ liệu và nhãn chuẩn, ghi nhận cấu hình chạy |
| OCR bảng, chữ viết tay, dấu mộc, giả mạo | Phạm vi chuyên sâu của ba tuần tiếp theo |

Đối với đầu vào ảnh, nhánh LLM sử dụng VLM (Vision-Language Model), tức mô hình xử lý cả ảnh và văn bản. LLM chỉ nhận văn bản có thể xử lý đầu ra OCR nhưng không trực tiếp thay thế bước đọc ảnh.

Đề bài không ấn định số lượng LLM cụ thể. Thiết kế baseline sử dụng tối thiểu hai đại diện để so sánh giữa các mô hình ngôn ngữ và đối chiếu với OCR chuyên dụng. Một cấu hình Qwen riêng lẻ chỉ cung cấp kết quả của một đại diện trong nhóm này.

## 2. Phân biệt bộ công cụ, mô hình và pipeline

| Tên gọi | Bản chất | Quan hệ với PaddleOCR |
| --- | --- | --- |
| PaddleOCR | Bộ công cụ OCR và xử lý tài liệu | Hệ thống chứa các nhánh bên dưới |
| PP-OCR, như PP-OCRv6 | Nhánh phát hiện và nhận dạng chữ | Thuộc PaddleOCR; dùng trong baseline OCR |
| PP-DocLayout | Mô hình phát hiện vùng bố cục | Thuộc hệ sinh thái PaddleOCR |
| PP-Structure | Pipeline phân tích cấu trúc tài liệu | Thuộc PaddleOCR; liên quan đánh giá bảng và bố cục |
| PaddleOCR-VL | VLM chuyên tài liệu | Thuộc PaddleOCR, là nhánh khác với PP-OCR |
| VietOCR | Dự án nhận dạng văn bản tiếng Việt | Độc lập; có thể kết hợp detector của PaddleOCR |
| Qwen3-VL | Dòng mô hình ngôn ngữ đa phương thức | Độc lập với PaddleOCR |
| Ministral 3 | Dòng mô hình ngôn ngữ có khả năng nhận ảnh của Mistral | Độc lập với PaddleOCR và thuộc dòng khác với Qwen |

PP-OCR, PP-DocLayout và PP-Structure không phải tên các dự án OCR độc lập cần triển khai đồng loạt. Trong baseline, cấu hình PaddleOCR được xác định cụ thể bằng checkpoint detection và recognition. [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR), [VietOCR](https://github.com/pbcquoc/vietocr), [Qwen3-VL](https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct), [Ministral 3](https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512).

## 3. Các giải pháp trong baseline

### 3.1. PaddleOCR với PP-OCR

PaddleOCR cung cấp pipeline phát hiện vùng chữ và nhận dạng văn bản. Tài liệu PP-OCRv6 liệt kê hỗ trợ tiếng Việt qua mã `vi` và các mức tiny/small/medium. Cấu hình khảo sát ban đầu sử dụng `PP-OCRv6_small_det` và `PP-OCRv6_small_rec`; việc thay đổi mức mô hình được thực hiện trên tập phát triển và cố định trước phép đo cuối. Toolkit sử dụng giấy phép Apache-2.0. [Tài liệu PP-OCR](https://www.paddleocr.ai/main/en/version3.x/pipeline_usage/OCR.html), [Repository PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR).

Đầu vào là ảnh trang hoặc ảnh render từ PDF. Kết quả gồm vùng chữ và văn bản nhận dạng, được chuyển về biểu diễn chung để chấm điểm. Các lỗi được phân tách thành phát hiện thiếu vùng, nhận dạng sai và sắp xếp sai thứ tự đọc.

### 3.2. VietOCR kết hợp detector

VietOCR là dự án độc lập cung cấp pretrained nhận dạng tiếng Việt, với các cấu hình `vgg_seq2seq` và `vgg_transformer`. Cấu hình baseline sử dụng `vgg_seq2seq`; `vgg_transformer` là biến thể đối chứng khi mở rộng phép thử. Repository công bố giấy phép Apache-2.0. [VietOCR](https://github.com/pbcquoc/vietocr).

Pipeline toàn trang sử dụng detector PP-OCR, cắt vùng chữ và đưa từng ảnh cắt vào VietOCR. Detector được giữ giống nhánh PaddleOCR để so sánh ảnh hưởng của bộ nhận dạng. Phép thử nhận dạng riêng sử dụng cùng ảnh cắt chuẩn; thời gian toàn pipeline bao gồm cả detection và cắt ảnh.

Các chỉ tiêu tập trung vào dấu tiếng Việt, chữ nhỏ, chuỗi số và độ chính xác toàn dòng. Chất lượng trên ảnh cắt và chất lượng toàn trang được báo cáo riêng.

### 3.3. Mô hình nhận ảnh Qwen3-VL

Cấu hình VLM thứ nhất trong thiết kế baseline là `Qwen/Qwen3-VL-4B-Instruct`. Đây là mô hình ảnh–văn bản độc lập, được công bố với giấy phép Apache-2.0 và có ví dụ chạy qua Transformers/vLLM. Việc đưa mô hình vào cấu hình khảo sát nhằm đại diện cho phương pháp sinh văn bản từ ảnh; chưa xác nhận đây là cấu hình tốt nhất hoặc phù hợp nhất với hạ tầng dự án. [Model card Qwen3-VL-4B-Instruct](https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct).

Mô hình nhận ảnh trang và yêu cầu chép nguyên văn, giữ dấu, số liệu và thứ tự đọc. Prompt, cách resize, tham số sinh và giới hạn đầu ra được cố định. Phần bỏ sót, tự thêm nội dung hoặc bị cắt do giới hạn sinh được ghi nhận trong kết quả.

Qwen3-VL được đánh giá trên cùng tác vụ nhận dạng văn bản với hai pipeline OCR. Khả năng đọc tiếng Việt, mức sử dụng bộ nhớ và thời gian mỗi trang cần được đo trên dữ liệu thực nghiệm.

### 3.4. Mô hình nhận ảnh Ministral 3

Cấu hình VLM thứ hai là `mistralai/Ministral-3-3B-Instruct-2512`, thuộc dòng mô hình của Mistral. Model card công bố khả năng nhận ảnh, giấy phép Apache-2.0 và bản trọng số Instruct ở định dạng FP8. Đây là đại diện thứ hai để so sánh với Qwen trên cùng tác vụ chép văn bản từ ảnh. [Model card Ministral 3 3B Instruct](https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512).

Hai mô hình dùng cùng nội dung yêu cầu chép văn bản, cùng ảnh gốc và quy tắc chấm. Các khác biệt về resize, xử lý ảnh, tham số sinh và độ chính xác tính toán được ghi nhận. Khả năng nhận dạng tiếng Việt và mức sử dụng tài nguyên chưa được đo trên dữ liệu dự án.

Kết quả FP8 và BF16/FP16 được ghi rõ theo cấu hình thực chạy. Chênh lệch tốc độ và bộ nhớ giữa các mức độ chính xác không được quy hoàn toàn cho khác biệt kiến trúc mô hình. Điều kiện chạy local, GPU ngoài máy hoặc API được trình bày riêng nếu khác hạ tầng.

### 3.5. Phạm vi mở rộng trong PaddleOCR

PaddleOCR-VL-1.6 là VLM chuyên tài liệu thuộc PaddleOCR, có đầu ra Markdown/JSON và giấy phép Apache-2.0. Đây là cấu hình bổ sung để khảo sát nhánh xử lý tài liệu của cùng hệ sinh thái; kết quả được ghi riêng với PP-OCR, Qwen3-VL và Ministral. [PaddleOCR-VL-1.6](https://huggingface.co/PaddlePaddle/PaddleOCR-VL-1.6).

PP-DocLayout và PP-Structure liên quan đến bố cục và bảng biểu. Việc khôi phục cấu trúc bảng, ô gộp, chữ viết tay, dấu mộc và phát hiện giả mạo thuộc phạm vi chuyên sâu sau baseline hai tuần.

## 4. Cấu hình so sánh

| Mã | Pipeline | Đầu ra đánh giá | Phạm vi |
| --- | --- | --- | --- |
| B1 | PP-OCR detection + PP-OCR recognition | Văn bản và vùng chữ | Baseline PaddleOCR |
| B2 | Cùng PP-OCR detector + VietOCR `vgg_seq2seq` | Văn bản và vùng chữ | Baseline VietOCR |
| B3 | Qwen3-VL-4B-Instruct nhận ảnh trực tiếp | Văn bản được sinh từ ảnh | Baseline mô hình ngôn ngữ thứ nhất |
| B4 | Ministral-3-3B-Instruct-2512 nhận ảnh trực tiếp | Văn bản được sinh từ ảnh | Baseline mô hình ngôn ngữ thứ hai |
| B5 | PaddleOCR-VL-1.6 | Nội dung trang theo biểu diễn đầu ra | Cấu hình mở rộng |
| P0 | Trích xuất trực tiếp lớp văn bản PDF | Văn bản trích xuất | Đối chứng cho trang có text, báo cáo riêng với OCR ảnh |

B1 và B2 cho phép giữ detector cố định và thay bộ nhận dạng. B3 và B4 so sánh hai dòng mô hình ảnh–ngôn ngữ, đồng thời đối chiếu với pipeline OCR. B5 thuộc cùng hệ sinh thái PaddleOCR nhưng sử dụng nhánh VLM chuyên tài liệu.

Định dạng và phạm vi đầu ra được thống nhất trước khi tính điểm. Nếu mô hình tạo Markdown/JSON, nội dung được chuyển về văn bản theo quy tắc cố định; điểm OCR không bao gồm đánh giá cấu trúc bảng ở giai đoạn này.

### 4.1. Hình thức chạy và yêu cầu GPU

Local là thực thi mô hình trên máy cá nhân hoặc máy chủ do dự án quản lý. API bên ngoài là gửi dữ liệu tới dịch vụ đã triển khai mô hình; máy gửi yêu cầu không cần GPU. API tự triển khai chỉ thay đổi cách truy cập: tài nguyên suy luận vẫn nằm ở máy chủ. Một endpoint tương thích OpenAI không đồng nghĩa với việc sử dụng dịch vụ OpenAI.

| Cấu hình | CPU/GPU khi tự chạy | API |
| --- | --- | --- |
| B1 — PP-OCR | Có thể chạy CPU; GPU là tùy chọn tăng tốc. | Không bắt buộc API bên ngoài; có thể đóng gói pipeline thành dịch vụ nội bộ. |
| B2 — VietOCR + detector | Cả VietOCR và detector có đường chạy CPU hoặc CUDA; GPU không bắt buộc cho inference. | Không bắt buộc API bên ngoài. |
| B3 — Qwen3-VL-4B-Instruct | Có trọng số để tự chạy. Thiết kế thực nghiệm ưu tiên GPU; chưa xác nhận tốc độ CPU hay ngưỡng VRAM trên máy dự án. | Có thể tự triển khai server; API của bên cung cấp khác cần xác minh đúng checkpoint và phiên bản trước khi so sánh. |
| B4 — Ministral 3 3B Instruct | Có trọng số để tự chạy. Đường triển khai FP8/vLLM được tài liệu minh họa trên GPU; cần kiểm tra GPU và backend tương thích FP8. Chưa xác nhận cấu hình CPU. | Có thể triển khai thành endpoint riêng; không mặc định rằng API thương mại sử dụng đúng checkpoint đang khảo sát. |
| B5 — PaddleOCR-VL-1.6 | Tài liệu có đường chạy x64 CPU và GPU; GPU không bắt buộc cho mọi backend, nhưng có thể cần cho đường phục vụ hiệu năng cao. | Hỗ trợ tự triển khai API; GPU/CPU nằm ở máy chủ chạy mô hình. |
| P0 — Đọc lớp text PDF | CPU; không cần GPU cho thao tác trích xuất lớp văn bản. | Không cần API bên ngoài. |

Nguồn cấu hình: [PP-OCR](https://www.paddleocr.ai/main/en/version3.x/pipeline_usage/OCR.html), [device của VietOCR](https://github.com/pbcquoc/vietocr/blob/master/config/base.yml), [Qwen3-VL Quickstart](https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct#quickstart), [Ministral 3](https://huggingface.co/mistralai/Ministral-3-3B-Instruct-2512), [PaddleOCR-VL — phần cứng và triển khai](https://www.paddleocr.ai/main/en/version3.x/pipeline_usage/PaddleOCR-VL.html).

Các ghi nhận trên áp dụng cho suy luận, không phải huấn luyện. Dung lượng VRAM phụ thuộc checkpoint, precision, độ phân giải ảnh, độ dài đầu ra và số yêu cầu đồng thời. Chỉ các mức được tác giả công bố rõ mới được ghi thành con số; báo cáo chưa có phép đo tài nguyên trên máy dự án.

## 5. Dữ liệu và phương pháp đánh giá

Tập hiện tại có 15 PDF tại `Accounting_Documents/01_Financial_Reports/06_2026/`; ID và đường dẫn nằm trong [documents.jsonl](metadata/documents.jsonl). Pilot sử dụng khoảng 10–15 trang đại diện cho văn bản, số liệu và chữ nhỏ. Kết quả trên báo cáo tài chính không tự đại diện cho hóa đơn, chứng từ hoặc ảnh chụp chưa có trong tập kiểm thử.

Nhãn chuẩn được đối chiếu thủ công. Phép thử ảnh cắt dùng cùng các vùng chuẩn; phép thử toàn trang tính cả detection, recognition và thứ tự đọc. Dấu tiếng Việt, dấu âm, ngoặc và dấu phân cách số được giữ nguyên. Quy tắc chuẩn hóa Unicode và khoảng trắng được cố định.

| Nhóm chỉ số | Chỉ số |
| --- | --- |
| Lỗi nhận dạng | CER, WER |
| Độ chính xác | Line Exact Match, Numeric Exact Match |
| Tốc độ | Latency p50/p95, số trang trên đơn vị thời gian |
| Vận hành | Tỷ lệ lỗi, timeout, đầu ra thiếu hoặc bị cắt |
| Tài nguyên | RAM, VRAM và cấu hình CPU/GPU |

Thời gian khởi tạo, render PDF, inference và tổng thời gian được đo riêng. Phiên bản thư viện, checkpoint, backend, độ phân giải, batch size và tham số sinh được ghi nhận trong mỗi cấu hình. Các bản dịch, trang trùng và ảnh biến đổi từ cùng nguồn nằm trong cùng tập để hạn chế rò rỉ giữa tập phát triển và kiểm thử.

Điểm CER/WER và thời gian từ các công bố khác không được so trực tiếp khi khác dữ liệu, phần cứng hoặc phương pháp chấm. Các bảng benchmark ở phụ lục chỉ cung cấp bối cảnh khảo sát. Phạm vi dữ liệu, kế hoạch và chỉ số chi tiết được trình bày trong [hd.md](hd.md).

## 6. Repository tham khảo cho xử lý hóa đơn

Danh sách được tổng hợp từ [repo_invoices.md](repo_invoices.md) và đối chiếu với README hoặc trang phát hành của từng dự án. Các repository gồm ứng dụng, framework và pipeline trích xuất thông tin; không tương ứng với 12 mô hình OCR độc lập. Chức năng dưới đây phản ánh mô tả của tác giả, chưa được kiểm thử trên dữ liệu dự án.

### 6.1. Ứng dụng hóa đơn tiếng Việt

| Repository | Nội dung chính | Cách chạy và GPU/API |
| --- | --- | --- |
| [philipsgn/vn-invoice-extractor](https://github.com/philipsgn/vn-invoice-extractor) | Pipeline kết hợp: Gemini Flash là nhánh chính; nhánh dự phòng chạy local dùng PaddleOCR, VietOCR và LayoutLMv3. Có trích xuất trường, dòng hàng và kiểm tra quan hệ tổng tiền–thuế. | Kết hợp API và local. Nhánh Gemini không cần GPU trên máy gửi; README cấu hình nhánh dự phòng bằng `DEVICE=cpu`. GPU không bắt buộc trong cấu hình này. |
| [HoVDuc/OCR-invoice](https://github.com/HoVDuc/OCR-invoice) | Pipeline OCR với DB detection, VGG-Transformer recognition và LayoutXLM cho KIE; có nhánh Gemini nhận ảnh để trích xuất dữ liệu hóa đơn. | Nhánh Gemini dùng API, không cần GPU local. Nhánh truyền thống tự chạy mô hình; README so sánh chi phí GPU, chưa xác nhận cấu hình CPU đầy đủ cho pipeline này. |
| [vietreceipt-team/vietreceipt](https://github.com/vietreceipt-team/vietreceipt) | Prototype xử lý hóa đơn đa định dạng, kết hợp trích xuất, chuẩn hóa, đối chiếu và người dùng kiểm duyệt. Thiết kế đầu ra gồm CSV/XLSX/JSON và bằng chứng cho các trường cần kiểm tra. | Yêu cầu tài nguyên phụ thuộc backend OCR/KIE được chọn. README chưa xác định đủ cấu hình để kết luận GPU bắt buộc hoặc toàn bộ xử lý chỉ dùng API. |
| [einvoice-lens trên PyPI](https://pypi.org/project/einvoice-lens/) | Package OCR kết hợp quy tắc để đọc PDF hóa đơn điện tử Việt Nam thành dữ liệu có cấu trúc; có CLI. Trang PyPI dẫn tới mã nguồn [thuyetbao/einvoice-lens](https://github.com/thuyetbao/einvoice-lens). | Package chạy qua Python/CLI; trang PyPI chưa công bố rõ backend OCR và yêu cầu GPU. Chưa đủ cơ sở xác nhận CPU-only hoặc phụ thuộc API. |

### 6.2. Framework OCR và phân tích tài liệu

| Repository | Nội dung chính | Cách chạy và GPU/API |
| --- | --- | --- |
| [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | Chứa PP-OCR cho phát hiện/nhận dạng chữ, PP-Structure cho cấu trúc tài liệu và PaddleOCR-VL cho phân tích trang bằng VLM. Các nhánh được phân biệt tại mục 2–4. | Có đường CPU/GPU tùy nhánh và backend; không bắt buộc API bên ngoài. Chi tiết baseline tại mục 4.1. |
| [docling-project/docling](https://github.com/docling-project/docling) | Chuyển PDF, ảnh và tài liệu văn phòng thành biểu diễn có cấu trúc, có xử lý bảng/bố cục và xuất Markdown/JSON. Lớp trích xuất trường hóa đơn cần được bổ sung riêng. | Pipeline tiêu chuẩn chạy local bằng CPU hoặc GPU; không bắt buộc API bên ngoài. Nhánh VLM phụ thuộc model/backend được cấu hình. |
| [datalab-to/marker](https://github.com/datalab-to/marker) | Pipeline chuyển PDF/ảnh sang Markdown, JSON và HTML, xử lý bảng, công thức và bố cục; sử dụng Surya trong quá trình phân tích tài liệu. | Có GPU qua vLLM và CPU/Apple Silicon qua llama.cpp. LLM bổ sung là tùy chọn; bật Gemini thì có gọi API bên ngoài. |
| [datalab-to/surya](https://github.com/datalab-to/surya) | Cung cấp OCR, phân tích bố cục, thứ tự đọc và nhận dạng bảng; có thể khảo sát như thành phần của pipeline xử lý tài liệu. | Có GPU qua vLLM và CPU/Apple Silicon qua llama.cpp. Server có thể tự khởi động trên máy hoặc cấu hình endpoint đã triển khai; không bắt buộc dịch vụ cloud. |

Ví dụ cấu hình CPU/GPU của Docling được công bố trong [Run with accelerator](https://docling-project.github.io/docling/_generated/examples/run_with_accelerator/). Với Marker, `--disable_ocr` chỉ trích xuất lớp văn bản và bỏ qua các phần cần OCR; cấu hình này không tương đương phép thử trên ảnh quét. Các đường CPU có OCR sử dụng backend suy luận tương ứng, theo README Marker/Surya.

### 6.3. Trích xuất thông tin hóa đơn (KIE)

KIE (Key Information Extraction) chuyển nội dung tài liệu thành trường nghiệp vụ như số hóa đơn, ngày, thuế, tổng tiền và dòng hàng.

| Repository | Nội dung chính | Cách chạy và GPU/API |
| --- | --- | --- |
| [manhsontran/invoice-parser](https://github.com/manhsontran/invoice-parser) | Parser dùng PaddleOCR/EasyOCR, có tùy chọn LayoutLMv3; trích xuất nhà cung cấp, ngày, số tiền và dòng hàng, kèm FastAPI và giao diện Streamlit. | Chạy local; README có `use_gpu: false` cho OCR và Document AI, GPU là tùy chọn. FastAPI ở đây là API của ứng dụng tự triển khai. |
| [FrankZhaodong/LayoutLM-Invoices](https://github.com/FrankZhaodong/LayoutLM-Invoices) | OCR tạo token và tọa độ; BERT kết hợp bbox hoặc LayoutLM phân loại token theo nhãn BIO, sau đó chuyển thành JSON. Có baseline dựa trên quy tắc. | Tự chạy OCR và mô hình, không bắt buộc API cloud. Baseline Tesseract + quy tắc có thể dùng CPU; README chưa nêu rõ yêu cầu GPU cho inference mô hình và fine-tuning. |
| [jhatch3/invoice-kie](https://github.com/jhatch3/invoice-kie) | Thiết kế benchmark LayoutLMv3 fine-tuning và Qwen2-VL zero-shot trên bộ biên lai CORD; chỉ số gồm Field F1, Line-item F1 và latency. README ghi số liệu giao diện còn là minh họa khi phần đánh giá chưa hoàn tất. | Thiết kế chạy local bằng trọng số mở, đo trên một GPU cố định; không dùng API trả phí. Chưa coi đây là pipeline đã hoàn tất kiểm thử. |
| [LeonAchata/InvoiceParser-AI](https://github.com/LeonAchata/InvoiceParser-AI) | Pipeline LangGraph kết hợp OpenAI API để trích xuất; mã kiểm tra dữ liệu thực hiện bước xác thực. Hỗ trợ xuất dữ liệu và tích hợp PostgreSQL. | Khi gọi dịch vụ bên ngoài, máy chạy ứng dụng không cần GPU cho suy luận. Có thể đổi `OPENAI_BASE_URL` sang endpoint tương thích tự triển khai; lúc đó phần cứng phụ thuộc model trên server. |

Các dự án trên cung cấp ví dụ cho ba lớp: đọc tài liệu, trích xuất trường và kiểm tra dữ liệu. Baseline hai tuần tại mục 4 vẫn đánh giá OCR chữ/số; độ chính xác trường và dòng hàng thuộc phép đánh giá KIE riêng. Các pipeline có Gemini hoặc OpenAI API được phân biệt với cấu hình chạy local khi ghi nhận điều kiện thực nghiệm.

## Phụ lục A. Các dự án khảo sát mở rộng

Các giải pháp dưới đây là dự án độc lập với PaddleOCR và không thuộc bốn cấu hình baseline chính B1–B4. MinerU là pipeline xử lý tài liệu; GLM-OCR sử dụng PP-DocLayoutV3 trong pipeline nhưng mô hình OCR là của dự án GLM.

| Giải pháp | Đặc điểm theo tài liệu công bố | Giấy phép được công bố |
| --- | --- | --- |
| [TeleOCR](https://huggingface.co/XingChen-AGI/TeleOCR/raw/main/README.md) | Khoảng 1.2B tham số; xử lý tài liệu số và ảnh chụp; model card gắn nhãn zh/en | Model card: Apache-2.0 |
| [OvisOCR2](https://huggingface.co/ATH-MaaS/OvisOCR2) / [OvisOCR3](https://huggingface.co/ATH-MaaS/OvisOCR3) | Công bố khoảng 0.8B; bản 3 mở rộng trích xuất thông tin và tái dựng bảng qua trang | Apache-2.0 |
| [GLM-OCR](https://github.com/zai-org/GLM-OCR) | Phân tích layout và nhận dạng song song với PP-DocLayoutV3 | Code Apache-2.0; model MIT; layout Apache-2.0 |
| [MinerU2.5-Pro](https://huggingface.co/opendatalab/MinerU2.5-Pro-2605-1.2B) | Checkpoint công bố 1.2B; sử dụng trong pipeline xử lý tài liệu | Checkpoint Apache-2.0; giấy phép code/backend được xác định riêng |
| [DeepSeek-OCR 2](https://github.com/deepseek-ai/DeepSeek-OCR-2) | Mô hình OCR có phương thức chạy vLLM và Transformers; môi trường mẫu dùng CUDA/PyTorch | Repository Apache-2.0 |

### Trọng số công khai có điều kiện sử dụng riêng

| Mô hình | Điều kiện được nguồn công bố ghi nhận |
| --- | --- |
| [OXR-1.0](https://github.com/SoMarkAI/OXR/blob/main/LICENSE) | Giấy phép OXR bổ sung điều kiện về sử dụng thương mại, ghi nhận nguồn và dịch vụ API cạnh tranh trên nền Apache-2.0 |
| [Chandra-OCR-2](https://huggingface.co/datalab-to/chandra-ocr-2#commercial-usage) | Code Apache-2.0; trọng số modified OpenRAIL-M, có điều kiện về phạm vi sử dụng và dịch vụ cạnh tranh |

Hai mô hình này được trình bày riêng để phân biệt với các lựa chọn công bố giấy phép Apache-2.0/MIT thông thường.

## Phụ lục B. Benchmark phân tích tài liệu

Các phép đo này bao gồm bảng, công thức hoặc bố cục; không thay thế kết quả OCR chữ và số trên tập dữ liệu của dự án.

### B.1. OmniDocBench

Bảng end-to-end của bên duy trì benchmark được ghi nhãn `v1.6_full`, trong khi changelog có đề cập phiên bản v1.7. Các số dưới đây giữ nguyên nhãn và giá trị của bảng tại mốc đối chiếu nguồn.

| Mô hình | Overall, cao hơn tốt hơn | Repository dự án / mô hình | Cách chạy và GPU/API |
| --- | ---: | --- | --- |
| OXR-1.0 | 97.03 | [SoMarkAI/OXR](https://github.com/SoMarkAI/OXR) | Local: Linux, NVIDIA hỗ trợ BF16; tác giả nêu 24 GB VRAM cho thử nghiệm ít đồng thời, khuyến nghị ≥48 GB. Có API thử nghiệm do tác giả cung cấp, không cần GPU phía client. |
| TeleOCR | 96.91 | [caipeng328/TeleOCR](https://github.com/caipeng328/TeleOCR) | Đường chạy chính thức dùng GPU CUDA/vLLM. Có thể triển khai mô hình trên server rồi gửi yêu cầu; chưa xác nhận API cloud được vận hành sẵn. |
| OvisOCR2 | 96.47 | [ATH-MaaS/OvisOCR2 — Hugging Face](https://huggingface.co/ATH-MaaS/OvisOCR2) | Ví dụ của tác giả dùng vLLM với GPU. Có trọng số để tự chạy; chưa xác nhận cấu hình CPU hoặc API cloud sẵn dùng. |
| PaddleOCR-VL-1.6 | 96.34 | [PaddlePaddle/PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | Có đường x64 CPU/GPU và tự triển khai API. Backend hiệu năng cao có yêu cầu phần cứng riêng; xem mục 4.1. |
| MinerU2.5-Pro | 95.75 | [opendatalab/MinerU](https://github.com/opendatalab/MinerU) | Checkpoint Pro có ví dụ Transformers và khuyến nghị vLLM/GPU. Toolkit MinerU hiện có đường CPU ở một số backend; chưa xác nhận tương đương cấu hình Pro trong bảng. API tự triển khai không loại bỏ phần cứng ở server. |
| GLM-OCR | 95.22 | [zai-org/GLM-OCR](https://github.com/zai-org/GLM-OCR) | Có Zhipu MaaS API: client không cần GPU. Tự triển khai có đường GPU/vLLM/SGLang và hướng dẫn Ollama/MLX; riêng layout có thể chạy CPU. |
| DeepSeek-OCR 2 | 90.25 | [deepseek-ai/DeepSeek-OCR-2](https://github.com/deepseek-ai/DeepSeek-OCR-2) | Đường chạy mẫu dùng NVIDIA CUDA qua Transformers/vLLM. Có trọng số để tự triển khai; README chưa xác nhận CPU-only hoặc API cloud sẵn dùng. |

Các liên kết GitHub dẫn tới mã nguồn dự án; riêng OvisOCR2 dẫn tới repository mô hình chính thức trên Hugging Face. Với PaddleOCR và MinerU, phiên bản checkpoint được xác định theo tên mô hình trong bảng, không theo phiên bản mới nhất của repository.

Thông tin thực thi được đối chiếu từ các repository trong bảng, [hướng dẫn PaddleOCR-VL](https://www.paddleocr.ai/main/en/version3.x/pipeline_usage/PaddleOCR-VL.html) và [model card MinerU2.5-Pro](https://huggingface.co/opendatalab/MinerU2.5-Pro-2605-1.2B#1-quick-start). API miễn phí của OXR được tác giả mô tả là dịch vụ thử nghiệm, không bảo đảm ổn định cho production. Khi dùng API hosted, cần ghi tên dịch vụ, phiên bản mô hình và thời gian truyền dữ liệu; không mặc định kết quả bằng cấu hình local trong benchmark.

Overall tổng hợp kết quả văn bản, bảng và công thức. Phần đánh giá text gồm tiếng Trung và tiếng Anh; điểm này không biểu diễn tỷ lệ ký tự tiếng Việt nhận dạng đúng. Việc xuất hiện trên leaderboard không xác nhận rằng mọi kết quả đều đã được tái lập độc lập. [OmniDocBench, End-to-End Evaluation](https://github.com/opendatalab/OmniDocBench#end-to-end-evaluation).

OXR-1.0 có điểm cao nhất trong các hàng được trích. TeleOCR có điểm cao nhất trong các lựa chọn Apache/MIT của bảng khảo sát này. Hai kết quả mô tả phạm vi so sánh cụ thể, chưa xác định mô hình phù hợp nhất với dữ liệu của dự án.

### B.2. Kết quả OvisOCR3 do tác giả công bố

Model card OvisOCR3 báo cáo **96.74 trên OmniDocBench1.6**. Giá trị này được tách khỏi bảng trên vì nguồn và lần đánh giá khác nhau; OvisOCR3 chưa có trong bảng chung tại mốc đối chiếu. [OvisOCR3, Performance](https://huggingface.co/ATH-MaaS/OvisOCR3#performance).

Về thực thi, ví dụ của tác giả yêu cầu môi trường GPU được vLLM hỗ trợ. Mô hình có trọng số để tự triển khai; lời gọi API tới server tự dựng không đồng nghĩa với API cloud đã có sẵn. Chưa xác nhận cấu hình CPU cho bản này. [OvisOCR3, Inference](https://huggingface.co/ATH-MaaS/OvisOCR3#inference).

### B.3. OmniParseBench

Trong công bố ngày 23/10/2026, Datalab đánh giá các mô hình trên 16.288 kiểm tra thuộc 2.937 trang, với các thành phần văn bản, bảng và bố cục.

| Mô hình | Điểm tổng hợp công bố |
| --- | ---: |
| Chandra-OCR-2 | 90.1 |
| MinerU2.5-Pro | 87.1 |
| GLM-OCR | 81.5 |
| PaddleOCR-VL-1.6 | 78.7 |

Datalab đồng thời là đơn vị phát triển Chandra. Các giá trị phản ánh phép thử do đơn vị này công bố và không dùng chung thang đo với OmniDocBench. [Datalab, Open-source OCR models on OmniParseBench](https://api.datalab.to/blog/open-ocr-models-omniparsebench).

Chandra-OCR-2 có mã nguồn và trọng số để tự triển khai qua Transformers hoặc server vLLM; đường phục vụ vLLM dùng GPU. Datalab cũng cung cấp API hosted, nhưng được liệt kê riêng với Chandra trong tài liệu đánh giá; không mặc định hai cấu hình là cùng checkpoint hoặc cho cùng kết quả. Chưa xác nhận cấu hình CPU-only của Chandra-OCR-2. [Repository Chandra](https://github.com/datalab-to/chandra).
