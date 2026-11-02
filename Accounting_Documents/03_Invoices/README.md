# Hóa đơn và tài liệu liên quan

Hóa đơn, biên lai, tài liệu xử lý sai sót và chứng từ công nợ liên quan. Mỗi file có một vị trí lưu chính; các mục đích giao nhau lưu trong business_tags.

Quy tắc và metadata: [hướng dẫn kho tài liệu](../README.md).

| Thư mục | Nội dung |
| --- | --- |
| [Sales_Invoices/](Sales_Invoices/) | Nhánh lưu hóa đơn bán ra theo đơn vị kế toán. VAT_Invoice cũng có thể nằm ở đây; không tự gán loại Sales_Invoice từ vị trí lưu. |
| [Purchase_Invoices/](Purchase_Invoices/) | Hóa đơn của giao dịch mua vào. Xác minh chủ thể kế toán trước khi gán direction=Incoming. |
| [Service_Invoices/](Service_Invoices/) | Hóa đơn có nội dung chính là cung cấp hoặc sử dụng dịch vụ. |
| [Export_Invoices/](Export_Invoices/) | Hóa đơn của giao dịch xuất khẩu. |
| [Adjusted_Invoices/](Adjusted_Invoices/) | Tài liệu ghi rõ là hóa đơn điều chỉnh; liên kết chứng từ gốc trong related_document_ids nếu có. |
| [Replacement_Invoices/](Replacement_Invoices/) | Tài liệu ghi rõ là hóa đơn thay thế; liên kết chứng từ gốc trong related_document_ids nếu có. |
| [Cancellation_Records/](Cancellation_Records/) | Biên bản hoặc hồ sơ hủy hóa đơn; document_type=Invoice_Cancellation_Record. |
| [Payment_Receipts/](Payment_Receipts/) | Payment_Receipt, Cash_Receipt, Deposit_Receipt, Refund_Receipt. Phiếu thu kế toán nội bộ thuộc Cash_Vouchers. |
| [Asset_Invoices/](Asset_Invoices/) | Hóa đơn mua hoặc bán tài sản. Ghi thêm business_tags thay vì sao chép vào nhiều thư mục. |
| [Utility_Invoices/](Utility_Invoices/) | Hóa đơn điện, nước, viễn thông và dịch vụ tiện ích tương tự. |
| [Other_Invoices/](Other_Invoices/) | Tài liệu đã xác nhận thuộc nhóm hóa đơn nhưng chưa phù hợp các nhánh cụ thể. |

## Bộ nhãn mở rộng

Taxonomy/schema hiện dùng phiên bản 2.1.0. Xem [bảng ánh xạ INV001–INV034](../../metadata/INVOICE_MAPPING.md) và [quy tắc máy đọc](../../metadata/invoice_mappings.json).

- Các lĩnh vực vận tải, lưu trú, ăn uống, thiết bị, phương tiện, xây dựng, đầu tư, bảo hiểm, điện, nước, viễn thông, nhiên liệu, quảng cáo và dịch vụ tài chính có tag riêng. Không tạo thêm thư mục theo từng tổ hợp.
- Retail_Invoice dùng khi đã xác nhận là hóa đơn bán lẻ nhưng chưa biết loại nền cụ thể hơn. Nếu là GTGT thì giữ VAT_Invoice và gắn Retail.
- Invoice_Correction_Document, Credit_Note và Debit_Note có thể lưu trực tiếp trong 03_Invoices khi chưa có nhánh con phù hợp. Các tài liệu này được quản lý cùng hồ sơ liên quan, chưa phải kết luận về tính chất pháp lý.
- issuance_form mô tả phát hành điện tử/giấy, source mô tả nguồn ảnh/file. Hai trường độc lập.
- invoice_kind và invoice_role giúp giữ cả loại nền lẫn vai trò điều chỉnh/thay thế.

Một file có thể khớp nhiều mã INV. Ví dụ hóa đơn điện tử GTGT mua thiết bị ghi nhận tài sản cố định có thể khớp INV001, INV005, INV007, INV023, INV024.

Trong [bộ mã chứng từ AV](../../metadata/ACCOUNTING_VOUCHER_MAPPING.md), AV003 dùng lại Cash_Receipt của INV018. Biên lai được lưu một lần ở Payment_Receipts; phiếu thu kế toán là Cash_Receipt_Voucher/AV001 và thuộc Cash_Vouchers.
