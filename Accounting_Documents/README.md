# Kho tài liệu kế toán

Kho được tổ chức theo 7 nhóm lưu trữ. Loại tài liệu và các thuộc tính tìm kiếm được quản lý riêng trong [metadata](../metadata/README.md).

## Cấu trúc thư mục

```text
Accounting_Documents/
├── 01_Financial_Reports/
│   └── 06_2026/
├── 02_Accounting_Vouchers/
│   ├── Cash_Vouchers/
│   ├── Bank_Vouchers/
│   ├── Inventory_Vouchers/
│   ├── Payroll_Vouchers/
│   ├── Fixed_Asset_Vouchers/
│   ├── Sales_Purchase_Vouchers/
│   └── General_Accounting_Vouchers/
├── 03_Invoices/
│   ├── Sales_Invoices/
│   ├── Purchase_Invoices/
│   ├── Service_Invoices/
│   ├── Export_Invoices/
│   ├── Adjusted_Invoices/
│   ├── Replacement_Invoices/
│   ├── Cancellation_Records/
│   ├── Payment_Receipts/
│   ├── Asset_Invoices/
│   ├── Utility_Invoices/
│   └── Other_Invoices/
├── 04_Tax_Documents/
├── 05_Bank_Statements/
├── 06_Contracts/
└── 07_Other_Documents/
```

`06_2026/` giữ cách tổ chức kỳ báo cáo đã có của người dùng. Không tự tạo thêm thư mục theo công ty, ngôn ngữ, định dạng hoặc chiều giao dịch.

| Nhóm | Nội dung |
| --- | --- |
| 01_Financial_Reports | Báo cáo tài chính, thường niên, kiểm toán, soát xét và tài liệu công bố liên quan |
| 02_Accounting_Vouchers | Chứng từ kế toán theo nghiệp vụ |
| 03_Invoices | Hóa đơn, biên nhận và hồ sơ liên quan |
| 04_Tax_Documents | Tờ khai, quyết toán và thông báo thuế |
| 05_Bank_Statements | Sao kê và xác nhận số dư |
| 06_Contracts | Hợp đồng mua bán, vay, dịch vụ và hợp đồng khác |
| 07_Other_Documents | Các tài liệu khác |

## Phân loại hai chiều

1. **Document Type:** `document_category` là nhóm cha, `document_type` là loại thực tế, `document_subcategory` là nhánh lưu trữ nếu có.
2. **Document Attributes:** `format`, `source`, `issuance_form`, `direction`, `language`, `company`, `industry`, thông tin hóa đơn và `business_tags`. Hóa đơn có thêm `invoice_kind` và `invoice_role` để giữ loại nền cùng vai trò điều chỉnh/thay thế.

Ví dụ một hóa đơn GTGT mua thiết bị có thể lưu một lần tại `03_Invoices/Asset_Invoices/`, mang `document_type=VAT_Invoice`, `direction=Incoming` và các tag `Purchase`, `Equipment_Purchase`, `Fixed_Asset_Purchase`. Không cần tạo bản sao trong Purchase_Invoices và Service_Invoices để tìm theo thuộc tính.

Bộ nhãn phiên bản 2.1.0 có [ánh xạ INV001–INV034](../metadata/INVOICE_MAPPING.md), [ánh xạ AV001–AV047](../metadata/ACCOUNTING_VOUCHER_MAPPING.md), 88 loại canonical và 22 tag nghiệp vụ kiểm soát. Các mã INV có thể giao nhau trên cùng một file. Sales_Invoice là loại xác minh theo nội dung; nhánh Sales_Invoices là vị trí lưu theo chiều bán ra, không tự quyết định loại hóa đơn.

AV003 dùng lại Cash_Receipt của INV018 và lưu chính ở `03_Invoices/Payment_Receipts`; AV014 dùng lại Balance_Confirmation và lưu chính ở `05_Bank_Statements`. Các nhóm nghiệp vụ AV vẫn giữ đủ 7 nhóm, nhưng không tạo thêm nhãn hoặc bản sao file cho hai trường hợp dùng chung này.

Nếu hóa đơn phù hợp nhiều nhánh, chọn một vị trí chính theo quy tắc ưu tiên: hồ sơ hủy, hóa đơn điều chỉnh/thay thế, xuất khẩu, tài sản, tiện ích, dịch vụ, mua/bán theo chiều giao dịch, sau cùng là Other_Invoices. Chỉ chọn khi có bằng chứng; khi chưa rõ có thể lưu ngay tại nhóm cha và để nhánh con `null`.

Tên thư mục không phải ground truth của model. Một PDF có thể chứa công văn, báo cáo soát xét và báo cáo tài chính; dùng một loại chính và `contained_document_types`, hoặc ghi metadata cấp trang khi triển khai OCR sau này.

## Tài liệu và ghi chú đã có

- 15 PDF được chuyển từ `Financial_Reports/06_2026/` sang `01_Financial_Reports/06_2026/`, giữ nguyên tên và nội dung.
- Ghi chú từ `Audit_Reports/note.txt` được giữ nguyên tại `01_Financial_Reports/audit_reports.note.txt`.
- Các ghi chú gốc của Accounting_Vouchers, Bank_Statements và Contracts được giữ ở nhóm đã đánh số tương ứng.
- [Nhật ký chuyển thư mục](../metadata/migration_2026-10-30.json) lưu đường dẫn cũ, mới và SHA-256 trước khi chuyển.

Số lượng trên là tại thời điểm sắp xếp ngày 30/10/2026. Danh mục hiện hành nằm trong [documents.jsonl](../metadata/documents.jsonl).

## Thêm tài liệu mới

1. Lưu file tại một nhóm chính. Giữ nguyên bản gốc và kiểm tra trùng bằng SHA-256.
2. Tạo bản ghi trong `metadata/documents.jsonl`, cấp `document_id` tiếp theo và giữ ID khi đổi tên/chuyển file.
3. Chỉ điền thuộc tính đã xác minh. Dùng `null` cho thông tin chưa rõ hoặc không áp dụng.
4. Ban đầu đặt `ocr_status=Pending`, `classification_status=Needs_Review`. Sau khi kiểm tra nội dung mới chuyển phân loại sang Confirmed.
5. Khi chỉ đổi vị trí, cập nhật `relative_path`; nội dung không đổi thì SHA-256 phải giữ nguyên.

Đây là taxonomy của repository. PaddleOCR cung cấp kết quả nhận dạng; bước ánh xạ taxonomy và trích xuất thuộc tính sẽ do pipeline của dự án thực hiện.
