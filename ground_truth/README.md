# Ground truth

Ảnh nguồn ở `Accounting_Documents/02_Accounting_Vouchers` và `03_Invoices`; không cần sao chép ảnh vào đây.

- [manifest.json](manifest.json): ID và hash của 43 ảnh; giữ ID của 15 ảnh pilot đã chọn.
- `texts/GTxxxxxx.txt`: bản chép đúng sau khi đối chiếu ảnh.
- `annotations/GTxxxxxx.json`: đường dẫn ảnh/text, hash và trạng thái duyệt.
- Mẫu đã được bạn duyệt: [GT000001.txt](texts/GT000001.txt), [GT000001.json](annotations/GT000001.json).

Tạo nháp bằng lệnh `draft` trong [pipeline.md](../pipeline.md). Sửa theo ảnh, giữ dấu tiếng Việt, số 0 đầu và dấu phân cách tiền; kiểm tra cả phần OCR bỏ sót. Bảng đọc theo hàng, các ô ngăn bằng tab.

Trong một ô, nối các dòng xuống hàng bằng khoảng trắng trước khi sang ô kế tiếp. Ô gộp ghi nội dung một lần tại vị trí trên-trái, các vị trí được phủ còn lại để trống. Tiêu đề bảng nhiều tầng giữ thành các hàng riêng; không lặp tên ô gộp để tự bổ sung nội dung. CER/WER gộp khoảng trắng nhưng vẫn xét thứ tự từ.

Không cần chép lại `GT000001`–`GT000007` đã đối chiếu; kiểm tra lại cách gom ô trong các bảng. Lệnh `draft --run outputs/vietocr --refresh-drafts --from-sample GT000008` chỉ thay nháp chưa có reviewer từ `GT000008`, có sao lưu ở `outputs/ground_truth_backup_*`; giữ nguyên nhãn `Verified`. Lệnh `draft` không có `--refresh-drafts` giữ nguyên mọi file nhãn đã tồn tại.

Giữ `Draft` khi sửa; đối chiếu xong thì đổi sang `Verified` và điền `reviewer`. Không đoán nội dung thiếu. Nếu crop/che vùng ngoài phạm vi, cập nhật ảnh/hash cho cả hai mô hình và truth. Token `###` không tự động được bỏ qua khi chấm.

`source_group=null` là chưa xác minh. `split` ghi cách chia tập; các lệnh mặc định không lọc theo split.
