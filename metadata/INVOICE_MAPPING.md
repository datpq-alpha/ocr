# Ánh xạ INV001–INV034

Phiên bản `2.1.0`. Các mã có thể giao nhau trên cùng một tài liệu.

Quy tắc máy đọc và gợi ý vị trí lưu: [invoice_mappings.json](invoice_mappings.json).

Một hóa đơn điện tử GTGT mua thiết bị có thể khớp INV001, INV005, INV007, INV023 và INV024. Không tạo bản sao file hoặc buộc chọn duy nhất một mã.

`document_type` giữ loại cụ thể đã biết. Các loại trong `suggested_metadata` của file JSON chỉ dùng khi chưa xác định được loại cụ thể hơn. Bảng dưới trình bày thuộc tính và tag gợi ý; điều kiện tìm kiếm chính xác nằm trong `match`. `null` nghĩa là chưa có bằng chứng hoặc không áp dụng.

## G01. Bán hàng và cung cấp dịch vụ

| Mã | Tên tiếng Anh | Tên tiếng Việt | Biểu diễn chuẩn |
| --- | --- | --- | --- |
| INV001 | VAT Invoice | Hóa đơn giá trị gia tăng | `invoice_kind=VAT_Invoice` |
| INV002 | Sales Invoice | Hóa đơn bán hàng | `invoice_kind=Sales_Invoice` |
| INV003 | Service Invoice | Hóa đơn cung cấp dịch vụ | tags: `Service` |
| INV004 | Export Invoice | Hóa đơn xuất khẩu | tags: `Export` |
| INV005 | Electronic Invoice | Hóa đơn điện tử | `issuance_form=Electronic` |
| INV006 | Retail Invoice | Hóa đơn bán lẻ | tags: `Retail` |

## G02. Mua hàng và chi phí

| Mã | Tên tiếng Anh | Tên tiếng Việt | Biểu diễn chuẩn |
| --- | --- | --- | --- |
| INV007 | Purchase Invoice | Hóa đơn mua hàng | `direction=Incoming`; tags: `Purchase` |
| INV008 | Expense Invoice | Hóa đơn chi phí | tags: `Operating_Expense` |
| INV009 | Transportation Invoice | Hóa đơn vận tải | tags: `Service`, `Transportation` |
| INV010 | Accommodation Invoice | Hóa đơn lưu trú | tags: `Service`, `Accommodation` |
| INV011 | Food and Beverage Invoice | Hóa đơn ăn uống | tags: `Service`, `Food_and_Beverage` |
| INV012 | Utility Invoice | Hóa đơn điện, nước, viễn thông | tags: `Utilities` |

## G03. Điều chỉnh và thay thế

| Mã | Tên tiếng Anh | Tên tiếng Việt | Biểu diễn chuẩn |
| --- | --- | --- | --- |
| INV013 | Adjusted Invoice | Hóa đơn điều chỉnh | `invoice_role=Adjusted` |
| INV014 | Replacement Invoice | Hóa đơn thay thế | `invoice_role=Replacement` |
| INV015 | Invoice Cancellation Record | Tài liệu hủy hóa đơn | `document_type=Invoice_Cancellation_Record` |
| INV016 | Invoice Correction Document | Tài liệu xử lý sai sót hóa đơn | `document_type=Invoice_Correction_Document` |

## G04. Thanh toán và biên lai

| Mã | Tên tiếng Anh | Tên tiếng Việt | Biểu diễn chuẩn |
| --- | --- | --- | --- |
| INV017 | Payment Receipt | Biên lai thanh toán | `document_type=Payment_Receipt` |
| INV018 | Cash Receipt | Biên lai thu tiền | `document_type=Cash_Receipt` |
| INV019 | Deposit Receipt | Biên lai đặt cọc | `document_type=Deposit_Receipt` |
| INV020 | Refund Receipt | Biên lai hoàn tiền | `document_type=Refund_Receipt` |
| INV021 | Credit Note | Chứng từ ghi giảm công nợ | `document_type=Credit_Note` |
| INV022 | Debit Note | Chứng từ ghi tăng công nợ | `document_type=Debit_Note` |

## G05. Tài sản và đầu tư

| Mã | Tên tiếng Anh | Tên tiếng Việt | Biểu diễn chuẩn |
| --- | --- | --- | --- |
| INV023 | Fixed Asset Invoice | Hóa đơn mua tài sản cố định | tags: `Fixed_Asset_Purchase` |
| INV024 | Equipment Invoice | Hóa đơn mua thiết bị | tags: `Equipment_Purchase` |
| INV025 | Vehicle Invoice | Hóa đơn mua phương tiện | tags: `Vehicle_Purchase` |
| INV026 | Construction Invoice | Hóa đơn xây dựng | tags: `Construction` |
| INV027 | Investment-related Invoice | Hóa đơn liên quan đến đầu tư | tags: `Investment` |

## G06. Hóa đơn đặc thù

| Mã | Tên tiếng Anh | Tên tiếng Việt | Biểu diễn chuẩn |
| --- | --- | --- | --- |
| INV028 | Insurance Invoice | Hóa đơn bảo hiểm | tags: `Service`, `Insurance` |
| INV029 | Telecommunications Invoice | Hóa đơn viễn thông | tags: `Utilities`, `Telecommunications` |
| INV030 | Electricity Invoice | Hóa đơn tiền điện | tags: `Utilities`, `Electricity` |
| INV031 | Water Invoice | Hóa đơn tiền nước | tags: `Utilities`, `Water` |
| INV032 | Fuel Invoice | Hóa đơn xăng dầu | tags: `Fuel` |
| INV033 | Advertising Invoice | Hóa đơn quảng cáo | tags: `Service`, `Advertising` |
| INV034 | Financial Service Invoice | Hóa đơn dịch vụ tài chính | tags: `Service`, `Financial_Service` |

## Quy tắc sử dụng

- INV005 là hình thức phát hành, độc lập với source. Electronic không tự tạo một lớp document_type mới.
- INV002 là loại hóa đơn bán hàng theo nội dung. Outgoing là chiều giao dịch, không thay cho INV002.
- INV007 dùng direction=Incoming theo đơn vị kế toán. Không ghi đè loại VAT_Invoice đã biết.
- Các tag lĩnh vực không tự xác nhận khả năng khấu trừ thuế hoặc phân loại tài sản trong sổ kế toán.
- Cash_Receipt khác phiếu thu kế toán Cash_Voucher. Debit_Note khác giấy báo Nợ ngân hàng.
- Credit_Note, Debit_Note và Invoice_Correction_Document có thể lưu trực tiếp ở 03_Invoices khi chưa có nhánh con phù hợp.
- Các trường null chưa khớp điều kiện tìm kiếm; không dùng để kết luận rằng tập dữ liệu không có loại tài liệu đó.
- INV018 dùng cùng canonical Cash_Receipt với AV003 trong [bộ mã chứng từ kế toán](ACCOUNTING_VOUCHER_MAPPING.md). Không nhân bản file và không đồng nhất với phiếu thu kế toán AV001.
