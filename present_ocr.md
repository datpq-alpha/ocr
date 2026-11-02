# Quick research OCR mã nguồn mở

Nội dung trình bày cho team trong khoảng 5–7 phút. Ngày kiểm tra nguồn: 30/10/2026.

Tài liệu chi tiết và nguồn theo từng model: [research.md](research.md).

## Slide 1. Kết quả research

- TeleOCR là ứng viên chất lượng hàng đầu trong shortlist giấy phép Apache/MIT đã kiểm tra.
- PaddleOCR-VL-1.6 là lựa chọn đề xuất để bắt đầu parsing tài liệu.
- OvisOCR3 là ứng viên mới đáng thử.
- Model tốt nhất cho PDF tiếng Việt của team cần được xác định qua pilot.

**Lời nói:** “Em đã khảo sát các model và nguồn benchmark hiện có. Em chia kết quả thành hai phần: bằng chứng công bố và lựa chọn nên thử với dữ liệu của mình. Phần này chưa có kết quả chạy model trên PDF dự án.”

Nguồn: [OmniDocBench](https://github.com/opendatalab/OmniDocBench#end-to-end-evaluation), [OvisOCR3](https://huggingface.co/ATH-MaaS/OvisOCR3).

## Slide 2. Các nhóm OCR

| Nhóm | Đại diện | Đầu ra |
| --- | --- | --- |
| Detection + recognition | PP-OCRv6 | Vùng chữ và văn bản |
| Recognition tiếng Việt | VietOCR + detector | Văn bản từ các ảnh cắt |
| VLM chuyên tài liệu | PaddleOCR-VL, TeleOCR, OvisOCR3 | Markdown/JSON hoặc text theo tác vụ |

**Lời nói:** “VietOCR cần bước cắt vùng chữ khi xử lý cả trang. Vì vậy em sẽ có phép thử trên cùng crop để so khả năng đọc chữ, và phép thử toàn trang để so cả pipeline.”

Nguồn: [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR), [VietOCR](https://github.com/pbcquoc/vietocr), [OvisOCR3](https://huggingface.co/ATH-MaaS/OvisOCR3).

## Slide 3. Benchmark công bố

OmniDocBench, bảng v1.6_full:

| Model | Overall |
| --- | ---: |
| TeleOCR | 96.91 |
| OvisOCR2 | 96.47 |
| PaddleOCR-VL-1.6 | 96.34 |
| GLM-OCR | 95.22 |

OXR có điểm cao hơn nhưng dùng giấy phép bổ sung điều kiện. Bảng này chỉ trích một số ứng viên.

**Lời nói:** “Overall tổng hợp nhiều tác vụ. Team chưa thể dùng điểm này để kết luận chất lượng trên báo cáo tài chính tiếng Việt.”

Nguồn: [Leaderboard](https://github.com/opendatalab/OmniDocBench#end-to-end-evaluation), [OXR LICENSE](https://github.com/SoMarkAI/OXR/blob/main/LICENSE).

## Slide 4. Các điểm cần kiểm chứng

- OvisOCR3 có kết quả mới do tác giả công bố, tách khỏi bảng chung.
- Thứ hạng thay đổi ở benchmark khác.
- Công khai trọng số có thể đi kèm điều kiện sử dụng riêng.
- Chưa có phép thử chung cho toàn bộ shortlist trên dữ liệu tiếng Việt của dự án.

**Lời nói:** “Em ghi riêng mức độ bằng chứng để tránh xếp hạng bằng số lấy từ các lần đánh giá khác nhau. OXR và Chandra cần phân biệt giấy phép với nhóm Apache/MIT.”

Nguồn: [OvisOCR3](https://huggingface.co/ATH-MaaS/OvisOCR3), [OmniParseBench và kết quả Datalab](https://api.datalab.to/blog/open-ocr-models-omniparsebench), [OXR LICENSE](https://github.com/SoMarkAI/OXR/blob/main/LICENSE), [Chandra Commercial Usage](https://huggingface.co/datalab-to/chandra-ocr-2#commercial-usage).

## Slide 5. Shortlist cho dự án

| Pipeline | Vai trò đề xuất |
| --- | --- |
| PP-OCRv6 | Baseline OCR truyền thống |
| Detector + VietOCR | Baseline tiếng Việt |
| PaddleOCR-VL-1.6 | Baseline VLM chuyên tài liệu |
| TeleOCR | Đối chứng bổ sung sau khi pipeline ổn |

OvisOCR3 là lựa chọn mở rộng tiếp theo. GLM-OCR là phương án dự phòng.

**Lời nói:** “Để kịp hai tuần, em đề xuất hoàn thiện ba pipeline đầu, có nhãn và cách đo thống nhất rồi mới mở rộng. Đây là lựa chọn theo phạm vi dự án, chưa phải kết quả model nào tốt nhất.”

## Slide 6. Pilot trên PDF có sẵn

- Nguồn pilot: `Accounting_Documents/01_Financial_Reports/06_2026/`; quản lý ID và thuộc tính trong [metadata/documents.jsonl](metadata/documents.jsonl).
- 10–15 trang đại diện: đoạn văn, chữ nhỏ, nhiều số và trang chất lượng kém.
- Nhãn chuẩn kiểm tra thủ công, giữ dấu tiếng Việt và định dạng số.
- Chất lượng: CER, WER, Numeric Exact Match.
- Vận hành: p50/p95, tỷ lệ lỗi, RAM/VRAM.
- Cùng ảnh đầu vào, lưu đủ cấu hình và raw output.

**Lời nói:** “Em sẽ đo recognition trên cùng vùng chữ và đo toàn trang riêng. Nhờ vậy team biết lỗi đến từ đọc sai chữ hay phát hiện thiếu vùng chữ.”

## Slide 7. Quyết định đề xuất

**Bắt đầu PP-OCRv6, detector + VietOCR và PaddleOCR-VL-1.6. Bổ sung TeleOCR để kiểm chứng lựa chọn theo research.**

Đầu ra sau pilot:

- Bảng điểm trên cùng tập nhãn.
- Thời gian và tài nguyên trên cùng máy.
- Ví dụ lỗi chữ, số và bỏ sót nội dung.
- Model được chọn cho benchmark đầy đủ.

**Lời kết:** “Research giúp team chọn được các ứng viên có bằng chứng. Pilot sẽ trả lời ứng viên nào phù hợp nhất với PDF tiếng Việt và hạ tầng của mình.”
