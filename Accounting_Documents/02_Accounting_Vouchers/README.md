# Chứng từ kế toán

Chứng từ kế toán theo nghiệp vụ. Phân biệt với hóa đơn, hợp đồng và sao kê.

Quy tắc và metadata: [hướng dẫn kho tài liệu](../README.md).

Bộ nhãn phiên bản 2.1.0 có đủ [47 mã AV theo 7 nhóm](../../metadata/ACCOUNTING_VOUCHER_MAPPING.md). Quy tắc máy đọc nằm trong [accounting_voucher_mappings.json](../../metadata/accounting_voucher_mappings.json).

| Nhóm | Mã chuẩn hóa | Số loại |
| --- | --- | ---: |
| Cash_Vouchers | AV001–AV007 | 7 |
| Bank_Vouchers | AV008–AV014 | 7 |
| Inventory_Vouchers | AV015–AV020 | 6 |
| Payroll_Vouchers | AV021–AV026 | 6 |
| Fixed_Asset_Vouchers | AV027–AV032 | 6 |
| Sales_Purchase_Vouchers | AV033–AV040 | 8 |
| General_Accounting_Vouchers | AV041–AV047 | 7 |
| **Tổng** | **AV001–AV047** | **47** |

| Thư mục | Nội dung |
| --- | --- |
| [Cash_Vouchers/](Cash_Vouchers/) | Phiếu thu, phiếu chi và chứng từ quỹ tiền mặt. |
| [Bank_Vouchers/](Bank_Vouchers/) | Ủy nhiệm chi, ủy nhiệm thu, giấy báo Nợ/Có. Sao kê và xác nhận số dư thuộc 05_Bank_Statements. |
| [Inventory_Vouchers/](Inventory_Vouchers/) | Phiếu nhập kho, xuất kho, kiểm kê và điều chuyển kho. |
| [Payroll_Vouchers/](Payroll_Vouchers/) | Bảng lương, bảng chấm công và chứng từ thanh toán lương. |
| [Fixed_Asset_Vouchers/](Fixed_Asset_Vouchers/) | Biên bản giao nhận, thanh lý, kiểm kê và bảng khấu hao. Hóa đơn mua tài sản thuộc 03_Invoices. |
| [Sales_Purchase_Vouchers/](Sales_Purchase_Vouchers/) | Chứng từ giao nhận, nhập mua, xuất bán; hóa đơn thuộc 03_Invoices, hợp đồng thuộc 06_Contracts. |
| [General_Accounting_Vouchers/](General_Accounting_Vouchers/) | Phiếu kế toán, phân bổ, kết chuyển và điều chỉnh sổ kế toán. |

## Loại chứng từ và vị trí lưu

- AV003 (Cash Receipt Slip) dùng lại `Cash_Receipt`, cùng loại với INV018, lưu chính ở `03_Invoices/Payment_Receipts`. AV001 là `Cash_Receipt_Voucher`, tức phiếu thu kế toán riêng biệt.
- AV014 (Bank Balance Confirmation) dùng lại `Balance_Confirmation`, lưu chính ở `05_Bank_Statements`. Nhóm nghiệp vụ vẫn là Bank_Vouchers trong bảng AV.
- AV008/AV009 (Bank Debit/Credit Advice) là giấy báo ngân hàng, phân biệt `Debit_Note`/`Credit_Note` trong hồ sơ công nợ.
- AV045 là điều chỉnh kế toán; INV013 là hóa đơn điều chỉnh. AV027–AV032 là hồ sơ TSCĐ, phân biệt hóa đơn mua tài sản.
- Nhãn nhóm cũ được giữ để xử lý tài liệu chưa rõ loại. Chưa xác định cụ thể thì giữ Needs_Review và chưa gán một mã AV chi tiết.

Một file chỉ lưu một lần. `group_code` của AV là nhóm tra cứu nghiệp vụ; với hai ngoại lệ AV003 và AV014, vị trí lưu được ghi rõ trong bảng ánh xạ. Không tạo thư mục riêng cho từng mã AV.
