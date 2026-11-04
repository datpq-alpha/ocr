# Baseline VLM trên Colab T4

Chạy mỗi notebook trong **session riêng**, lần lượt sau khi đã tải kết quả mô hình trước. Chọn T4 GPU và chạy các ô từ trên xuống. Không cài thư viện của notebook mới vào session Qwen đang chạy.

| Notebook | Cấu hình | Thư mục kết quả trong ZIP |
| --- | --- | --- |
| [Qwen3-VL-4B](qwen3_vl_4b_colab.ipynb) | NF4, tính toán FP16 | `outputs/qwen3vl_4b_colab_t4_nf4/` |
| [Ministral 3 3B Instruct](ministral3_3b_colab.ipynb) | Bản BF16 chính thức của Mistral → NF4, tính toán FP16 | `outputs/ministral3_3b_colab_t4_nf4/` |
| [PaddleOCR-VL-1.6](paddleocr_vl_1_6_colab.ipynb) | Pipeline layout + nhận dạng vùng; Transformers, VLM FP16, layout FP32 | `outputs/paddleocr_vl_1_6_colab_t4_fp16/` |

Cả ba dùng cùng 43 ảnh/ID/hash từ commit GitHub cố định, có log mỗi 30 giây và checkpoint từng ảnh. Không tải ground truth. Bật Google Drive trong cấu hình nếu cần giữ tiến độ qua các phiên; mặc định `/content` chỉ tồn tại trong runtime hiện tại.

Giải nén ZIP vào thư mục repository trên máy local để có `outputs/<tên lượt>/`, kích hoạt `.venv`, rồi chấm:

```powershell
python scripts/ocr_baseline.py score --run outputs/ministral3_3b_colab_t4_nf4 --output outputs/ministral3_3b_colab_t4_nf4/scores_py312.json
python scripts/ocr_baseline.py score --run outputs/paddleocr_vl_1_6_colab_t4_fp16 --output outputs/paddleocr_vl_1_6_colab_t4_fp16/scores_py312.json
```

Lệnh dùng ground truth local đã duyệt. Không chạy `draft`. Nếu đã có file điểm cùng tên, chọn tên mới. Kiểm tra đủ 43 ảnh, lỗi và `truncated_images` trong `run.json`; đầu ra chạm giới hạn token vẫn tham gia CER/WER.

PaddleOCR-VL lưu kết quả native và HTML bảng trong JSONL; text chấm điểm là nội dung các block theo thứ tự native, chuyển HTML bảng thành text. CER/WER chưa đánh giá cấu trúc bảng. Báo cáo riêng cấu hình lượng tử hóa, backend và phần cứng CPU/GPU.

Đã kiểm tra processor/config thực tế bằng CPU, cú pháp và tương thích xuất/chấm qua kiểm thử local; chưa chạy inference trên T4 trong môi trường phát triển.
