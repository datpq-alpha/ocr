# Ánh xạ AV001–AV047

Phiên bản `2.1.0`. Bao phủ 47 mục theo 7 nhóm nghiệp vụ do người dùng cung cấp.

Quy tắc máy đọc: [accounting_voucher_mappings.json](accounting_voucher_mappings.json). Nhãn lưu trong metadata là document_type canonical; mã AV dùng để tra cứu.

## Tổng hợp

| Nhóm | Số mã |
| --- | ---: |
| Cash Vouchers | 7 |
| Bank Vouchers | 7 |
| Inventory Vouchers | 6 |
| Payroll Vouchers | 6 |
| Fixed Asset Vouchers | 6 |
| Sales Purchase Vouchers | 8 |
| General Accounting Vouchers | 7 |
| **Tổng** | **47** |

AV003 dùng lại Cash_Receipt của INV018, lưu chính ở 03_Invoices/Payment_Receipts. AV014 dùng lại Balance_Confirmation, lưu chính ở 05_Bank_Statements. Đây là hai tham chiếu chéo có chủ đích, tránh tạo nhãn hoặc bản sao file trùng.

## Cash Vouchers – Chứng từ tiền mặt

| Mã | Document Type theo danh mục | Tên tiếng Việt | Nhãn canonical |
| --- | --- | --- | --- |
| AV001 | Cash Receipt Voucher | Phiếu thu | `Cash_Receipt_Voucher` |
| AV002 | Cash Payment Voucher | Phiếu chi | `Cash_Payment_Voucher` |
| AV003 | Cash Receipt Slip | Biên lai thu tiền | `Cash_Receipt` |
| AV004 | Cash Advance Request | Giấy đề nghị tạm ứng | `Cash_Advance_Request` |
| AV005 | Cash Advance Settlement | Giấy thanh toán tiền tạm ứng | `Cash_Advance_Settlement` |
| AV006 | Cash Count Record | Biên bản kiểm kê quỹ | `Cash_Count_Record` |
| AV007 | Cash Handover Record | Biên bản bàn giao tiền mặt | `Cash_Handover_Record` |

## Bank Vouchers – Chứng từ ngân hàng

| Mã | Document Type theo danh mục | Tên tiếng Việt | Nhãn canonical |
| --- | --- | --- | --- |
| AV008 | Bank Debit Advice | Giấy báo Nợ | `Bank_Debit_Advice` |
| AV009 | Bank Credit Advice | Giấy báo Có | `Bank_Credit_Advice` |
| AV010 | Payment Order | Ủy nhiệm chi | `Payment_Order` |
| AV011 | Collection Order | Ủy nhiệm thu | `Collection_Order` |
| AV012 | Bank Transfer Voucher | Chứng từ chuyển tiền | `Bank_Transfer_Voucher` |
| AV013 | Bank Reconciliation Statement | Biên bản đối chiếu ngân hàng | `Bank_Reconciliation_Statement` |
| AV014 | Bank Balance Confirmation | Giấy xác nhận số dư ngân hàng | `Balance_Confirmation` |

## Inventory Vouchers – Chứng từ kho

| Mã | Document Type theo danh mục | Tên tiếng Việt | Nhãn canonical |
| --- | --- | --- | --- |
| AV015 | Goods Receipt Note | Phiếu nhập kho | `Goods_Receipt_Note` |
| AV016 | Goods Issue Note | Phiếu xuất kho | `Goods_Issue_Note` |
| AV017 | Internal Stock Transfer Note | Phiếu điều chuyển kho nội bộ | `Internal_Stock_Transfer_Note` |
| AV018 | Material Inspection Record | Biên bản kiểm nhận vật tư | `Material_Inspection_Record` |
| AV019 | Inventory Count Record | Biên bản kiểm kê hàng tồn kho | `Inventory_Count_Record` |
| AV020 | Internal Transportation Note | Phiếu xuất kho kiêm vận chuyển nội bộ | `Internal_Transportation_Note` |

## Payroll Vouchers – Chứng từ tiền lương và nhân sự

| Mã | Document Type theo danh mục | Tên tiếng Việt | Nhãn canonical |
| --- | --- | --- | --- |
| AV021 | Timesheet | Bảng chấm công | `Timesheet` |
| AV022 | Payroll Statement | Bảng thanh toán tiền lương | `Payroll_Statement` |
| AV023 | Bonus Payment Statement | Bảng thanh toán tiền thưởng | `Bonus_Payment_Statement` |
| AV024 | Payroll Allocation Statement | Bảng phân bổ tiền lương | `Payroll_Allocation_Statement` |
| AV025 | Social Insurance Payment Record | Chứng từ thanh toán bảo hiểm | `Social_Insurance_Payment_Record` |
| AV026 | Employee Payment Confirmation | Xác nhận thanh toán cho nhân viên | `Employee_Payment_Confirmation` |

## Fixed Asset Vouchers – Chứng từ tài sản cố định

| Mã | Document Type theo danh mục | Tên tiếng Việt | Nhãn canonical |
| --- | --- | --- | --- |
| AV027 | Fixed Asset Handover Record | Biên bản giao nhận TSCĐ | `Fixed_Asset_Handover_Record` |
| AV028 | Fixed Asset Disposal Record | Biên bản thanh lý TSCĐ | `Fixed_Asset_Disposal_Record` |
| AV029 | Fixed Asset Revaluation Record | Biên bản đánh giá lại TSCĐ | `Fixed_Asset_Revaluation_Record` |
| AV030 | Depreciation Calculation Sheet | Bảng tính khấu hao TSCĐ | `Depreciation_Calculation_Sheet` |
| AV031 | Fixed Asset Transfer Record | Biên bản điều chuyển TSCĐ | `Fixed_Asset_Transfer_Record` |
| AV032 | Fixed Asset Inventory Record | Biên bản kiểm kê TSCĐ | `Fixed_Asset_Inventory_Record` |

## Sales Purchase Vouchers – Chứng từ mua bán hàng hóa, dịch vụ

| Mã | Document Type theo danh mục | Tên tiếng Việt | Nhãn canonical |
| --- | --- | --- | --- |
| AV033 | Goods Delivery Note | Phiếu giao hàng | `Goods_Delivery_Note` |
| AV034 | Goods Receipt Confirmation | Biên bản giao nhận hàng hóa | `Goods_Receipt_Confirmation` |
| AV035 | Purchase Order | Đơn đặt hàng | `Purchase_Order` |
| AV036 | Sales Order | Đơn đặt hàng bán | `Sales_Order` |
| AV037 | Purchase Acceptance Record | Biên bản nghiệm thu mua hàng | `Purchase_Acceptance_Record` |
| AV038 | Service Acceptance Record | Biên bản nghiệm thu dịch vụ | `Service_Acceptance_Record` |
| AV039 | Accounts Receivable Reconciliation | Biên bản đối chiếu công nợ phải thu | `Accounts_Receivable_Reconciliation` |
| AV040 | Accounts Payable Reconciliation | Biên bản đối chiếu công nợ phải trả | `Accounts_Payable_Reconciliation` |

## General Accounting Vouchers – Chứng từ kế toán tổng hợp

| Mã | Document Type theo danh mục | Tên tiếng Việt | Nhãn canonical |
| --- | --- | --- | --- |
| AV041 | General Journal Voucher | Phiếu kế toán | `General_Journal_Voucher` |
| AV042 | Accounting Entry Voucher | Chứng từ ghi sổ | `Accounting_Entry_Voucher` |
| AV043 | Cost Allocation Statement | Bảng phân bổ chi phí | `Cost_Allocation_Statement` |
| AV044 | Cost Calculation Sheet | Bảng tính giá thành | `Cost_Calculation_Sheet` |
| AV045 | Accounting Adjustment Voucher | Chứng từ điều chỉnh kế toán | `Accounting_Adjustment_Voucher` |
| AV046 | Accrual Voucher | Chứng từ ghi nhận chi phí phải trả | `Accrual_Voucher` |
| AV047 | Prepayment Allocation Statement | Bảng phân bổ chi phí trả trước | `Prepayment_Allocation_Statement` |

## Quy tắc phân biệt

- AV001 là phiếu thu kế toán; AV003/INV018 là biên lai thu tiền. Không đồng nhất chỉ vì đều xác nhận nhận tiền.
- AV008/AV009 là giấy báo ngân hàng; INV022/INV021 là chứng từ công nợ. Không đổi Debit_Note thành Bank_Debit_Advice hoặc Credit_Note thành Bank_Credit_Advice chỉ theo từ Nợ/Có.
- AV013 là đối chiếu ngân hàng; Bank_Statement là sao kê giao dịch, AV014 là xác nhận số dư tại thời điểm.
- AV045 điều chỉnh bút toán/sổ kế toán; INV013 điều chỉnh hóa đơn.
- AV027–AV032 là hồ sơ tài sản cố định; hóa đơn mua tài sản giữ nhóm Invoices và các tag tương ứng.
- AV035/AV036 và AV039/AV040 cần xác minh góc nhìn đơn vị kế toán trước khi phân loại mua/bán hoặc phải thu/phải trả.
- Nếu mới biết nhóm mà chưa xác định loại cụ thể, giữ nhãn nhóm cũ hoặc document_type=null và Needs_Review; chưa gán mã AV.
- Một PDF chứa nhiều thành phần dùng loại chính và contained_document_types. Nếu cần nhãn cấp trang thì lưu riêng theo document_id/page_number, chưa tách hoặc nhân bản file.
