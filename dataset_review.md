# Đánh giá dữ liệu hóa đơn có nhãn

Kiểm tra ngày 03/11/2026, phục vụ baseline pretrained trong hai tuần đầu. Hai nguồn dưới đây giảm công thu thập và gán nhãn, nhưng phạm vi nhãn không tương đương bản chép đầy đủ của trang.

| Tiêu chí | MC-OCR 2021 | VLM Extract Bill của minhduc168 |
| --- | --- | --- |
| Quy mô công bố | 2.436 ảnh; public train 1.155 ảnh | 982 mẫu, một split `train`; Parquet 81.662.819 byte, khoảng 81,66 MB |
| Đầu vào | Ảnh chụp biên nhận bán lẻ tiếng Việt | Ảnh/vùng hóa đơn; hai mẫu đã xem là nội dung dịch vụ y tế, thuốc |
| Nhãn dùng cho trích xuất | Người bán, địa chỉ, thời gian, tổng tiền; có thông tin vùng và chất lượng ảnh | Danh sách dòng hàng: `stt`, `ten_dich_vu`, `so_luong`, `don_vi_tinh`, `don_gia`, `thanh_tien` |
| Phù hợp baseline hiện tại | Có thể chấm recognition trên vùng có transcript chuẩn; chấm toàn trang cần transcript đủ | Phù hợp đánh giá trích xuất dòng hàng; chưa đủ để chấm OCR toàn ảnh |
| Giới hạn độ phủ | Không đại diện đầy đủ cho phiếu thu/chi, chứng từ ngân hàng, kho và tài sản | Chưa xác nhận tính đại diện cho nhiều nhóm chứng từ; nhãn không có vị trí vùng chữ |
| Truy cập | Cổng Legacy cần đăng nhập; trang gốc yêu cầu đăng ký sử dụng nghiên cứu | Công khai, không gated; metadata khai báo MIT |

Nguồn: [bài báo của ban tổ chức MC-OCR](https://people.cs.umu.se/sonvx/files/MCOCR_Preprint.pdf), [mô tả dữ liệu MC-OCR](https://www.rivf2021-mc-ocr.vietnlp.com/dataset), [dataset Hugging Face](https://huggingface.co/datasets/minhduc168/dataset-origin-vlm-extract-bill), [metadata và danh sách artifact](https://huggingface.co/api/datasets/minhduc168/dataset-origin-vlm-extract-bill?blobs=true).

## 1. Áp dụng cho phép đo hiện tại

Không đưa trực tiếp `anno_texts` của MC-OCR hoặc `master_data` của Hugging Face vào `ground_truth/texts/` để so với OCR toàn ảnh. Phần chữ không thuộc các trường được gán nhãn sẽ bị tính thành lỗi chèn, làm sai ý nghĩa CER/WER.

Với MC-OCR, lựa chọn phù hợp là cắt cùng các vùng được gán nhãn cho mọi mô hình, chấm CER/WER theo vùng, báo cáo riêng với bài toàn trang. Nếu chạy KIE, hệ thống phải chọn/gán bốn trường từ kết quả OCR trước khi chấm; điểm khi đó bao gồm cả lỗi trích xuất. Transcript dùng nội bộ trong quá trình xây dựng bộ dữ liệu không đồng nghĩa toàn bộ transcript đã được phát hành trong CSV cuộc thi.

Với Hugging Face, dùng `master_data` để chấm trường và dòng hàng, có thể so sánh OCR + parser với VLM. Mẫu 0 chứa cả chữ số tiền bằng chữ nhưng nhãn không chép phần này; mẫu 1 có hạn dùng và số lô không xuất hiện trong nhãn. Đây là kiểm tra trực tiếp hai mẫu, chưa phải kiểm định chất lượng toàn bộ 982 mẫu. Giá trị rỗng cần được phân biệt với thông tin thực sự không có và thông tin chưa được gán nhãn.

Giữ 43 ảnh hiện tại thành tập tài liệu kế toán riêng. Dùng bộ có nhãn để mở rộng phép thử theo đúng phạm vi nhãn. Tập chỉ có split `train` không cung cấp test độc lập sẵn có: cần cố định tập đánh giá, tránh chia các crop cùng nguồn sang các tập khác nhau và ghi rõ chưa xác minh trùng dữ liệu huấn luyện của checkpoint. Không cần train/fine-tune để chạy baseline pretrained.

## 2. Truy cập MC-OCR

Trang CodaLab cũ thông báo không nhận người đăng ký mới và dẫn sang Legacy. Địa chỉ `aihub.vn` hiện chuyển hướng sang **[AIHub Legacy](https://aihub.ml/competitions/1)**. Trang này đã truy cập được khi kiểm tra; mục Participate hiển thị yêu cầu đăng nhập, chưa xác minh được URL ZIP dành cho tài khoản đã tham gia.

1. Đọc yêu cầu tại [trang dataset](https://www.rivf2021-mc-ocr.vietnlp.com/dataset). Trang này yêu cầu ký [User Agreement](https://drive.google.com/file/d/1yKVGqYZ3JRp6nIaPQE1tL8rMgeNKw9NJ/view), gửi `vndag@vietnlp.com` để đăng ký trước khi dùng dữ liệu.
2. Tạo tài khoản/đăng nhập [AIHub](https://aihub.ml/accounts/login/?next=/competitions/1%23participate-get-data), mở cuộc thi, chọn **Participate → Get Data** và hoàn tất bước tham gia theo giao diện.
3. Nếu được cung cấp, lấy public training images và CSV annotation; giữ README/license/label dictionary kèm theo. Không dùng file mẫu `results.csv` hoặc nhãn dự đoán của đội thi làm ground truth test.
4. Nếu đã tham gia nhưng không có tệp hoặc link hỏng, liên hệ địa chỉ trên, xin bộ public train và CSV annotation dùng nghiên cứu; nêu rõ không cần nộp bài thi. Nội dung gợi ý: “Tôi đang xây dựng baseline OCR pretrained cho biên nhận tiếng Việt. Cổng Legacy hiện không cung cấp được tệp dữ liệu cho tài khoản của tôi. Xin hướng dẫn truy cập public training images và annotations MC-OCR, kèm điều kiện sử dụng hiện hành.”

URL ZIP trên cổng chính thức sau bước đăng nhập chưa được xác minh. Có thể lấy dữ liệu qua bản đóng gói cộng đồng trên Kaggle dưới đây, với phạm vi nhãn và phiên bản được ghi nhận riêng.

### 2.1. Bản MC-OCR trên Kaggle

[Vietnamese Receipts MC_OCR 2021 của domixi1989](https://www.kaggle.com/datasets/domixi1989/vietnamese-receipts-mc-ocr-2021) là một gói có cả dữ liệu gốc và các sản phẩm xử lý trung gian. API khai báo phiên bản **17**, kích thước giải nén **2.298.875.226 byte**, license **Unknown**, không có mô tả nguồn chi tiết. Không coi gói này là bản phát hành chính thức hoặc suy ra giấy phép mới cho dữ liệu gốc. [Metadata Kaggle](https://www.kaggle.com/api/v1/datasets/view/domixi1989/vietnamese-receipts-mc-ocr-2021).

Kiểm tra trực tiếp thư mục ZIP, CSV, hai tệp nhãn recognition, một TSV và ba ảnh cắt cho thấy:

| Thành phần | Số lượng/phạm vi | Giá trị sử dụng |
| --- | --- | --- |
| `train_images/` | 1.155 ảnh trang | Có thể chạy OCR toàn trang, nhưng CSV chỉ gán các trường MC-OCR |
| `val_images/` | 391 ảnh trang | `mcocr_val_sample_df.csv` chứa nhãn mẫu `abc abc abc`, không phải ground truth |
| `text_recognition_mcocr_data/.../` | 6.585 ảnh cắt | Đầu vào thuận tiện cho benchmark recognition |
| `text_recognition_train_data.txt` | 5.285 cặp ảnh–text, từ 922 biên nhận | Nhãn chữ cho ảnh cắt |
| `text_recognition_val_data.txt` | 1.300 cặp ảnh–text, từ 231 biên nhận | Có thể cố định làm tập đánh giá recognition |
| `kie_data/.../boxes_and_transcripts/` | 1.151 TSV | Mẫu đã xem có text trống và text sai ở các vùng `OTHER`; chưa xác minh là transcript thủ công toàn trang |
| Các thư mục detector, rotation, `data0_or_180`, ảnh visualize | Nhiều bản xử lý của cùng nguồn | Không đếm thành các tài liệu độc lập |

Toàn bộ 6.585 tên ảnh trong hai tệp nhãn có ảnh tương ứng trong archive; text đều khớp một giá trị trong `anno_texts` của CSV train gốc. Hai danh sách recognition không giao nhau theo mã biên nhận, nhưng chưa xác minh ảnh trùng bằng hash/perceptual hash. Đây là nhãn **vùng chứa thông tin được chọn**, không phải bản chép toàn trang.

Nhãn nguồn vẫn có lỗi: một ảnh ngày giờ đã xem hiển thị `30.09.2020 09.30`, trong khi nhãn đi kèm chứa chuỗi lặp khác. Kiểm tra chất lượng một tập mẫu trước khi chốt phép đo; giữ nguyên nhãn gốc và ghi riêng bản đã duyệt nếu sửa. Không dùng đầu ra OCR trung gian hoặc file submission làm truth thay thế.

**Đánh giá:** bản Kaggle thuận tiện hơn để chuẩn bị benchmark nhận dạng vì có sẵn ảnh cắt và text. Có thể bắt đầu với 1.300 crop validation. Runner hiện tại vẫn xử lý ảnh trang qua detector; benchmark crop cần một chế độ recognition riêng, cùng ảnh cắt cho PaddleOCR, VietOCR và VLM, và báo cáo riêng với end-to-end 43 ảnh. Chưa nhập dataset này vào manifest hay chạy benchmark mới.

**Tải dữ liệu:** [ZIP phiên bản 17](https://www.kaggle.com/api/v1/datasets/download/domixi1989/vietnamese-receipts-mc-ocr-2021?datasetVersionNumber=17), dung lượng tải **2.271.709.772 byte, khoảng 2,27 GB**. Đường tải đã trả dữ liệu ZIP công khai khi kiểm tra. Mới lấy danh sách archive và các tệp mẫu để thẩm định, chưa tải toàn bộ ZIP.

Để lấy riêng ảnh cắt và hai tệp nhãn, dùng `kagglehub` trong môi trường dữ liệu riêng (tạo `.venv-data` theo mục 3), cài gói bằng:

```powershell
.\.venv-data\Scripts\python.exe -m pip install kagglehub
```

Sau đó chạy Python trong môi trường đó:

```python
import kagglehub

handle = "domixi1989/vietnamese-receipts-mc-ocr-2021/versions/17"
for path in (
    "text_recognition_train_data.txt",
    "text_recognition_val_data.txt",
    "text_recognition_mcocr_data",
):
    print(kagglehub.dataset_download(
        handle,
        path=path,
        output_dir="datasets/external/mcocr_kaggle",
    ))
```

Đường ảnh cắt bên trong gói có hai tầng cùng tên: `text_recognition_mcocr_data/text_recognition_mcocr_data/<tên ảnh>.jpg`. Mỗi dòng nhãn có dạng `<tên ảnh>\t<text>`; tách ở tab đầu tiên. Các API tải từng file/thư mục và cố định phiên bản được mô tả trong [tài liệu KaggleHub](https://github.com/Kaggle/kagglehub#download-dataset). Nếu Kaggle yêu cầu xác thực, đăng nhập bằng cơ chế chính thức của KaggleHub trên máy cá nhân.

Báo cáo kiểm tra máy đọc được nằm ở `outputs/kaggle_mcocr_review.json`; đây là kiểm tra cấu trúc và mẫu nhãn, chưa phải kết quả CER/WER.

### 2.2. Bản đã tải trên máy

Thư mục thực tế là `MC_OCR_2021/` tại gốc repository. Kiểm tra 61.340 tệp cho thấy tên và kích thước khớp toàn bộ danh mục ZIP Kaggle v17. Gói có 1.155 ảnh public train và 391 ảnh public test, kèm crop và dữ liệu xử lý; không bao gồm đầy đủ 2.436 ảnh của các giai đoạn cuộc thi. Chưa có căn cứ coi toàn bộ gói là dữ liệu mô phỏng hoặc chỉ gồm ảnh đã lọc hợp lệ. Thư mục `data0.7/` riêng có 1.044 ảnh; tên thư mục chưa xác nhận được quy trình lọc.

- **Xem dữ liệu gốc:** mở `mcocr_train_df.csv`, đối chiếu `img_id` với `train_images/train_images/`; `anno_texts` và `anno_labels` phân cách bằng `|||`.
- **Đánh giá nhận dạng:** dùng `text_recognition_val_data.txt` gồm 1.300 cặp tên ảnh–text, ghép ảnh trong `text_recognition_mcocr_data/text_recognition_mcocr_data/`. Cả 1.300 ảnh đều hiện diện. Đây là phép thử crop, cần chế độ recognition riêng trong runner.
- **Giữ đúng phạm vi nhãn:** không dùng `mcocr_val_sample_df.csv` làm truth vì chứa `abc abc abc`; các bản xoay/crop của cùng biên nhận không được tính là tài liệu độc lập.

Git bỏ qua cả `/MC_OCR_2021/` và `/data/MC_OCR_2021/`; chưa có tệp nào trong thư mục dữ liệu được Git theo dõi.

## 3. Tải và đọc bộ Hugging Face

Lệnh tải sử dụng môi trường OCR đã có, không cài thêm gói:

```powershell
.\.venv\Scripts\python.exe scripts/download_bill_dataset.py
```

Đích lưu: `datasets/external/vlm_extract_bill/`, gồm Parquet chứa ảnh/nhãn, README gốc và `source.json`. Script cố định revision `d24586e71318dec13c69f5f35f3d8bc04c5e561c`, kiểm tra SHA256 Parquet; chạy lại tái sử dụng file hợp lệ. Thư mục dữ liệu đã được bỏ qua khi Git theo dõi; không thay đổi manifest, truth hoặc kết quả OCR hiện tại.

[Link Parquet trực tiếp, phiên bản cố định](https://huggingface.co/datasets/minhduc168/dataset-origin-vlm-extract-bill/resolve/d24586e71318dec13c69f5f35f3d8bc04c5e561c/data/train-00000-of-00001.parquet).

Để đọc/xuất ảnh bằng thư viện `datasets`, có thể tạo môi trường dữ liệu riêng:

```powershell
.\.venv\Scripts\python.exe -m venv .venv-data
.\.venv-data\Scripts\python.exe -m pip install datasets Pillow
```

Chạy đoạn Python sau trong môi trường đó:

```python
from pathlib import Path
import json
from datasets import load_dataset

base = Path("datasets/external/vlm_extract_bill")
ds = load_dataset(
    "parquet",
    data_files=str(base / "data/train-00000-of-00001.parquet"),
    split="train",
    cache_dir=str(base / ".arrow_cache"),
)
print(len(ds), ds.column_names)
print(ds[0]["master_data"])

# Tùy chọn: xuất ảnh và nhãn gốc; không ghi đè lần xuất trước.
export = base / "export"
export.mkdir(exist_ok=False)
(export / "images").mkdir()
with (export / "labels.jsonl").open("w", encoding="utf-8") as stream:
    for i, sample in enumerate(ds):
        sample_id = f"HFBILL{i+1:06d}"
        image_file = f"images/{sample_id}.png"
        sample["image"].save(export / image_file)
        stream.write(json.dumps({
            "sample_id": sample_id,
            "image_path": image_file,
            "source_image": sample["source_image"],
            "master_data": sample["master_data"],
        }, ensure_ascii=False) + "\n")
```

README nguồn có ví dụ chung dùng cột `description`; schema thực tế đã kiểm tra là **`image`, `source_image`, `master_data`**. Dùng các tên cột này khi đọc. Quy trình tải/đọc không cần GPU. Tải về không đồng nghĩa bộ dữ liệu đã tương thích với runner/chấm CER/WER hiện tại; chưa có adapter chấm KIE cho nhãn này.

API sử dụng theo [tài liệu Hugging Face Datasets](https://huggingface.co/docs/datasets/loading).
