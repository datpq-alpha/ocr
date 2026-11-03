# Chạy baseline OCR

Chạy pretrained trên CPU cho 43 ảnh thuộc nhóm `02` và `03`. Hai nhánh dùng chung detector/crop, thay bộ nhận dạng PaddleOCR hoặc VietOCR.

Mặc định `--layout ruled`: tìm đường kẻ, tách vùng chữ vượt ranh giới ô trước recognition, rồi ghép các dòng trong cùng ô. Bảng xuất theo hàng, các ô cách nhau bằng tab. Ô gộp chỉ xuất nội dung ở vị trí trên-trái; vị trí được phủ còn lại để trống. JSON lưu `layout.tables`, tọa độ, hàng/cột, span và chỉ số các dòng trong ô. Bảng không xác định được lưới rõ dùng thứ tự dòng cũ; thêm `--layout rows` để dùng hoàn toàn cách cũ. Chưa xử lý tổng quát bảng không đường kẻ, nghiêng hoặc lồng nhau.

Checkpoint Paddle mặc định `PP-OCRv6_small_rec` thiếu nhiều ký tự dấu tiếng Việt. Preset `ppocrv6_vi` dùng [checkpoint cộng đồng đã huấn luyện tiếng Việt](https://huggingface.co/tieubaoca/pp-ocrv6-medium-rec-vietnamese), thay bộ nhận dạng bằng `PP-OCRv6_medium_rec`; giữ nguyên detector/crop. Dictionary đi kèm có đủ bộ ký tự tiếng Việt runner kiểm tra. Đây là checkpoint khác, cần chấm lại CER/WER để so sánh chất lượng.

## 1. Môi trường PowerShell

```powershell
. .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

`.venv` dùng Python 3.11. Nếu không kích hoạt được, thay `python` bằng `.\.venv\Scripts\python.exe`. Model tải ở lần đầu; ảnh xử lý local.

## 2. Chạy OCR

```powershell
python scripts/ocr_baseline.py run --engine paddleocr --recognizer ppocrv6_vi --overwrite
python scripts/ocr_baseline.py run --engine vietocr --overwrite
```

Đầu ra: `outputs/<engine>/texts/`, `predictions.jsonl`, `run.json` (cấu hình, nguồn/phiên bản/hash checkpoint, kiểm tra dictionary, thời gian và lỗi). `--overwrite` chỉ thay kết quả sau khi lượt mới thành công; bản cũ gồm cả điểm chấm được lưu ở `outputs/paddleocr_backup_*`. Nếu lỗi, kết quả cũ giữ nguyên, lượt lỗi ở thư mục `.paddleocr.pending_*`. Ground truth không bị thay đổi. Bỏ `--overwrite` và dùng `--output outputs/paddleocr_vi_v2` nếu cần lưu riêng.

Thử một ảnh vào thư mục mới: thêm `--sample GT000001 --output outputs/paddleocr_vi_test` và bỏ `--overwrite`. Tải checkpoint một lần vào `.cache/`; suy luận trên CPU, không gửi ảnh qua API. Preset giữ nguyên dictionary/trọng số và resize giữ tỷ lệ ảnh cắt; không dùng bước tự thêm dấu vào kết quả.

## 3. Tạo và duyệt ground truth

```powershell
python scripts/ocr_baseline.py draft --run outputs/vietocr --refresh-drafts --from-sample GT000008
```

Lệnh trên giữ nguyên `GT000001`–`GT000007`, cập nhật nháp `Draft` chưa có reviewer từ `GT000008` trở đi và sao lưu bản nháp cũ vào `outputs/ground_truth_backup_*`. Nhãn `Verified` luôn được giữ nguyên. Bỏ `--refresh-drafts` để chỉ tạo nhãn còn thiếu.

Sửa `ground_truth/texts/GTxxxxxx.txt` theo ảnh; trong annotation đổi `status` sang `Verified`, điền `reviewer`. Bảy ảnh đã đối chiếu không cần chép lại, nhưng kiểm tra thứ tự ở các bảng: nối các dòng trong cùng ô bằng khoảng trắng, đọc các ô từ trái sang phải, các hàng từ trên xuống dưới. Không sửa truth theo lỗi của OCR. Hai mô hình dùng chung truth; giữ nguyên OCR gốc.

## 4. Chấm CER/WER

```powershell
python scripts/ocr_baseline.py score --run outputs/paddleocr
python scripts/ocr_baseline.py score --run outputs/vietocr
```

Kết quả: `outputs/<engine>/scores.json`, theo ảnh/nhóm và tổng. Chỉ chấm nhãn `Verified`, có reviewer và đúng hash ảnh. Chấm lại dùng `--output outputs/paddleocr/scores_v2.json`.

Chấm NFC/khoảng trắng, giữ dấu, hoa/thường và dấu phân cách số; WER theo token khoảng trắng. CER/WER có thể vượt 100%. Thứ tự từ vẫn ảnh hưởng điểm; thay layout cần chấm lại cả hai nhánh trên cùng truth. Chưa chấm riêng cấu trúc bảng/trường nghiệp vụ. Mỗi ảnh đo một lượt sau warm-up.

Thêm ảnh: `python scripts/ocr_baseline.py prepare`. Không đổi ảnh đã duyệt mà chưa kiểm tra nhãn. Tách development/test theo nguồn/mẫu; lệnh mặc định chạy tất cả ảnh.

Kiểm tra mã: `python -m unittest discover -s tests -v`.

Tài liệu API: [PaddleOCR](https://www.paddleocr.ai/main/en/version3.x/pipeline_usage/OCR.html), [VietOCR](https://github.com/pbcquoc/vietocr).
