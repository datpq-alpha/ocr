# Taxonomy và metadata tài liệu

Phiên bản hiện tại: `2.1.0`. Các file ở đây mô tả dữ liệu và quy tắc phân loại, chưa triển khai OCR hoặc mô hình phân loại.

## Các file

| File | Vai trò |
| --- | --- |
| [taxonomy.json](taxonomy.json) | 7 nhóm cha, 18 nhánh con, 88 loại canonical, 22 tag nghiệp vụ, tên thay thế và quy tắc phân loại |
| [document.schema.json](document.schema.json) | JSON Schema Draft 2020-12 cho một bản ghi metadata |
| [invoice_mappings.json](invoice_mappings.json) | Quy tắc máy đọc ánh xạ INV001–INV034, hỗ trợ một tài liệu khớp nhiều mã |
| [INVOICE_MAPPING.md](INVOICE_MAPPING.md) | Bảng ánh xạ đầy đủ 34 mục, tên Anh/Việt và cách biểu diễn |
| [accounting_voucher_mappings.json](accounting_voucher_mappings.json) | Quy tắc máy đọc AV001–AV047 theo 7 nhóm chứng từ kế toán |
| [ACCOUNTING_VOUCHER_MAPPING.md](ACCOUNTING_VOUCHER_MAPPING.md) | Bảng đủ 47 mã, tên Anh/Việt, nhãn canonical và các trường hợp dùng lại loại đã có |
| [documents.jsonl](documents.jsonl) | Danh mục file thật, mỗi dòng là một object JSON |
| [examples/invoice.example.json](examples/invoice.example.json) | Hóa đơn minh họa, tách khỏi dữ liệu thật |
| [examples/invoice.scanned-electronic.example.json](examples/invoice.scanned-electronic.example.json) | Hóa đơn điện tử được in rồi scan |
| [examples/invoice.adjusted-vat.example.json](examples/invoice.adjusted-vat.example.json) | Hóa đơn điều chỉnh giữ được loại nền GTGT |
| [examples/receipt.deposit.example.json](examples/receipt.deposit.example.json) | Biên lai đặt cọc, phân biệt với hóa đơn |
| [examples/voucher.cash-receipt.example.json](examples/voucher.cash-receipt.example.json) | AV001: phiếu thu kế toán |
| [examples/voucher.cash-receipt-slip.example.json](examples/voucher.cash-receipt-slip.example.json) | AV003/INV018: biên lai thu tiền, dùng lại Cash_Receipt |
| [examples/voucher.bank-debit.example.json](examples/voucher.bank-debit.example.json) | AV008: giấy báo Nợ ngân hàng |
| [examples/voucher.bank-balance.example.json](examples/voucher.bank-balance.example.json) | AV014: xác nhận số dư, dùng lại Balance_Confirmation |
| [examples/voucher.depreciation.example.json](examples/voucher.depreciation.example.json) | AV030: bảng tính khấu hao TSCĐ |
| [migration_2026-10-30.json](migration_2026-10-30.json) | Đường dẫn trước/sau và SHA-256 của 19 file gốc được chuyển |

## Ý nghĩa các trường

| Trường | Quy ước |
| --- | --- |
| schema_version | Phiên bản cấu trúc metadata, hiện là 2.1.0 |
| document_id | Mã ổn định dạng DOC000001; không cấp lại chỉ vì đổi tên hoặc thư mục |
| document_category | Mã nhóm không có số thứ tự, ví dụ Financial_Reports hoặc Invoices |
| document_type | Một mã loại trong taxonomy, ví dụ VAT_Invoice; chưa xác minh thì null |
| document_subcategory | Nhánh lưu trữ, ví dụ Asset_Invoices; null nếu nhóm không có nhánh hoặc chưa rõ |
| relative_path | Đường dẫn dùng dấu /, tính từ Accounting_Documents; không phải tính từ metadata |
| sha256 | Hash nội dung file, phục vụ kiểm tra toàn vẹn và trùng lặp |
| format | PDF, JPG hoặc PNG, theo định dạng file; .jpeg dùng JPG |
| source | Scanned, Camera, Electronic, Mixed hoặc null; không suy ra từ đuôi PDF |
| issuance_form | Hình thức phát hành Electronic/Paper hoặc null; độc lập với source |
| invoice_kind | Loại nền VAT_Invoice, Sales_Invoice, Other_Invoice hoặc null; giữ được loại nền khi document_type là Adjusted_Invoice/Replacement_Invoice |
| invoice_role | Original, Adjusted, Replacement hoặc null; chỉ điền khi có bằng chứng |
| direction | Incoming, Outgoing, Internal hoặc null, từ góc nhìn đơn vị kế toán đang quản lý hồ sơ |
| language | Mảng như ["Vietnamese", "English"] cho song ngữ; null nếu chưa kiểm tra |
| company | Tên hoặc mã đơn vị phát hành được xác minh từ nội dung; không tự điền theo tên file |
| industry | Securities, Banking, General_Business, Other hoặc null |
| invoice_number | Chuỗi để giữ số 0 đầu; null khi chưa biết/không áp dụng |
| invoice_date | Ngày hóa đơn theo YYYY-MM-DD; không dùng ngày tải file hoặc ngày công bố thay thế |
| tax_code | Mã số thuế của bên phát hành, lưu chuỗi; nếu cần cả hai bên thì bổ sung field riêng và tăng phiên bản schema |
| total_amount | Giá trị số theo tài liệu, giữ dấu; có thể âm đối với điều chỉnh, chưa rõ thì null |
| currency | Mã tiền tệ ba chữ in hoa, ví dụ VND; không tự mặc định từ ngôn ngữ |
| reporting_period_end | Ngày kết thúc kỳ báo cáo đã xác minh, dạng YYYY-MM-DD hoặc null |
| business_tags | Mảng tag trong bộ 22 giá trị kiểm soát của taxonomy, ví dụ Equipment_Purchase và Fixed_Asset_Purchase; schema từ chối tag chưa khai báo |
| contained_document_types | Các loại tài liệu thành phần trong cùng PDF, ví dụ Review_Report |
| related_document_ids | Liên kết đến hóa đơn/tài liệu gốc khi có điều chỉnh, thay thế hoặc quan hệ khác |
| ocr_status | Pending, Processing, Completed, Failed hoặc Skipped |
| classification_status | Needs_Review hoặc Confirmed; Confirmed bắt buộc có document_type |
| metadata_origin | Migrated_From_Directory, Manually_Reviewed, Model_Prediction hoặc Illustrative_Example |
| is_example | false cho file thật; true chỉ cho dữ liệu minh họa |
| notes | Ghi chú về nguồn nhãn, điểm chưa rõ hoặc lý do cần kiểm tra |

Các key được giữ ở cấp ngoài cùng như mẫu người dùng đưa. Để biểu diễn nhiều ngôn ngữ, `language` dùng mảng. Trường không có thông tin dùng `null`, không dùng chuỗi rỗng, số 0 hoặc ngày tự suy đoán. `[]` cho các danh sách tag/quan hệ nghĩa là chưa ghi nhận phần tử nào, không khẳng định rằng không có trong tài liệu.

`document_category` và `document_subcategory` xác định vị trí lưu. `document_type` xác định loại thực tế nên một VAT_Invoice có thể nằm ở Asset_Invoices hoặc Service_Invoices. Schema kiểm tra sự phù hợp giữa loại, nhóm và đường dẫn, nhưng không xác minh nội dung tài liệu.

## Các chiều hóa đơn và 34 mã tra cứu

- `source=Scanned`, `issuance_form=Electronic`, `format=PDF` cùng hợp lệ cho hóa đơn điện tử được in rồi scan. Không tự suy hình thức phát hành từ nguồn đầu vào.
- `document_type=Adjusted_Invoice`, `invoice_kind=VAT_Invoice`, `invoice_role=Adjusted` giữ đủ thông tin của hóa đơn GTGT điều chỉnh. Cũng có thể giữ `document_type=VAT_Invoice` và ghi vai trò Adjusted nếu quy tắc gán nhãn của bộ dữ liệu chọn loại nền làm loại chính.
- `Sales_Invoice` là loại được xác minh theo nội dung, độc lập với `direction=Outgoing`. Một hóa đơn loại Sales_Invoice có thể là đầu vào của bên mua.
- Các loại ngữ cảnh đã có như Service_Invoice, Asset_Invoice, Utility_Invoice vẫn được hỗ trợ. Khi biết loại nền cụ thể hơn, ưu tiên loại đó và lưu lĩnh vực trong business_tags. Service_Invoice, Export_Invoice, Utility_Invoice và Retail_Invoice yêu cầu tag tương ứng để không mất thông tin khi truy vấn.
- Nhóm Invoices còn có Invoice_Correction_Document, Cash_Receipt, Deposit_Receipt, Refund_Receipt, Credit_Note và Debit_Note. Các loại này không dùng invoice_kind/invoice_role. Vị trí lưu chung không xác định chúng là hóa đơn theo pháp luật.
- Các mã INV001–INV034 là mã tra cứu, có thể giao nhau. Không lưu chúng thay cho document_type và không coi chúng là 34 lớp loại trừ nhau.

`match` trong invoice_mappings.json là JSON Schema cho điều kiện tìm kiếm. `suggested_metadata` chỉ là gợi ý gán nhãn khi có bằng chứng; không ghi đè VAT_Invoice đã biết bằng loại rộng hơn và không tự chạy gán nhãn vào dữ liệu thật.

Các tag gợi ý theo nhóm có thể dùng cùng nhau. Ví dụ ghi cả Utilities và Electricity để tìm được theo tiện ích lẫn tiền điện; ghi cả Service và Transportation cho dịch vụ vận tải. Schema kiểm tra giá trị tag, không tự thêm tag cha hoặc suy ra nghiệp vụ từ nội dung.

## Bộ mã AV001–AV047

Danh mục chứng từ có 47 mã tra cứu theo 7 nhóm nghiệp vụ. Mỗi mã ánh xạ tới một document_type canonical; cùng một loại không được tạo nhãn mới chỉ vì xuất hiện trong cả danh mục AV và INV.

| Nhóm | Mã | Số loại |
| --- | --- | ---: |
| Cash_Vouchers | AV001–AV007 | 7 |
| Bank_Vouchers | AV008–AV014 | 7 |
| Inventory_Vouchers | AV015–AV020 | 6 |
| Payroll_Vouchers | AV021–AV026 | 6 |
| Fixed_Asset_Vouchers | AV027–AV032 | 6 |
| Sales_Purchase_Vouchers | AV033–AV040 | 8 |
| General_Accounting_Vouchers | AV041–AV047 | 7 |
| **Tổng** | **AV001–AV047** | **47** |

Hai mã dùng lại loại đã có:

- AV003, tên yêu cầu Cash_Receipt_Slip, dùng canonical `Cash_Receipt`, cùng loại với INV018. Nhóm nghiệp vụ AV là Cash_Vouchers, nhưng vị trí lưu chính giữ ở `03_Invoices/Payment_Receipts`.
- AV014, tên yêu cầu Bank_Balance_Confirmation, dùng canonical `Balance_Confirmation`, lưu chính ở `05_Bank_Statements`.

`group_code` trong bảng AV mô tả nhóm nghiệp vụ. `suggested_metadata` và `storage_folder` chỉ nhóm/vị trí lưu chính. Hai trường hợp trên không bị ép vào Accounting_Vouchers hoặc nhân bản file để khớp tên nhóm AV.

Taxonomy có `document_type_aliases` để chuẩn hóa tên thay thế trước khi kiểm tra schema. Schema chỉ nhận nhãn canonical; không tự sửa tên sai chính tả. Các nhãn nhóm cũ như Cash_Voucher và Payroll_Voucher được giữ với `granularity=Group` để dùng khi chưa đủ thông tin chi tiết. Nhãn nhóm hoặc document_type=null chưa tự khớp một mã AV cụ thể.

Các tên loại dự án mô tả nội dung chứng từ, không tự xác nhận mẫu biểu, hiệu lực hoặc điều kiện pháp lý. Khi phân biệt đơn đặt mua/bán hoặc công nợ phải thu/phải trả, cần xác minh góc nhìn đơn vị kế toán. Các trường hóa đơn chưa áp dụng vẫn để null; không ghi số phiếu kế toán vào invoice_number.

## Nâng từ phiên bản 2.0.0

- Thêm 45 loại chi tiết và dùng lại 2 loại đã có để ánh xạ đủ 47 mã AV; tổng taxonomy có 88 loại canonical, gồm cả các nhãn nhóm giữ lại từ trước.
- Giữ nguyên 34 mã INV, 22 tag, cây thư mục và 15 tài liệu thật. Bản ghi thật chỉ cập nhật schema_version sang 2.1.0.
- Schema kiểm tra loại chứng từ phù hợp nhánh nghiệp vụ: ví dụ Cash_Receipt_Voucher không nằm ở Payroll_Vouchers. Có thể để nhánh null khi file đang lưu tại nhóm cha và chưa chốt nhánh.
- Nhật ký chuyển file ngày 30/10/2026 giữ nguyên. Các ghi chú gốc được giữ; ghi chú tại nhánh chứng từ được bổ sung mã AV tương ứng.

## Nâng từ phiên bản 1.0.0

- Toàn bộ 15 bản ghi thật chuyển schema_version sang 2.0.0, thêm issuance_form/invoice_kind/invoice_role với giá trị null. Giữ nguyên ID, đường dẫn, hash và thông tin đã có.
- business_tags chuyển từ chuỗi tự do sang enum kiểm soát. Trước khi nhập dữ liệu cũ có tag tùy chỉnh, ánh xạ hoặc bổ sung định nghĩa tag vào taxonomy và schema; không tự bỏ tag.
- Quy tắc Sales_Invoice đã tách khỏi chiều bán ra. Nhãn Sales_Invoice cũ được gán chỉ dựa vào Outgoing cần kiểm tra lại.
- Các ví dụ đã cập nhật; metadata/migration_2026-10-30.json giữ nguyên vì là nhật ký chuyển file trước đó.

## Trạng thái danh mục ban đầu

15 bản ghi thật có `format=PDF`, `ocr_status=Pending`, `classification_status=Needs_Review`. Nhóm Financial_Reports được kế thừa cách sắp xếp hiện tại của người dùng. Loại cụ thể, công ty, ngôn ngữ, nguồn, kỳ báo cáo và các trường nghiệp vụ đều chờ kiểm tra.

`invoice.example.json` có `is_example=true`, không có đường dẫn/hash file thật, dùng DEMO_COMPANY. Không đưa file minh họa này vào tập benchmark hoặc tính số lượng tài liệu.

## Mở rộng ngành và bộ nhãn

- Dùng `industry` cho chứng khoán, ngân hàng hoặc doanh nghiệp thông thường. Các giá trị chưa biết để null.
- Đã có Capital_Adequacy_Report cho báo cáo an toàn tài chính/an toàn vốn.
- Khi có chứng từ ngành mới, bổ sung mã với tên Anh, Việt, nhóm cha và quy tắc phân loại trong taxonomy. Cập nhật enum/điều kiện của schema cùng lần và tăng phiên bản khi thay đổi ý nghĩa hoặc cấu trúc.
- Không tạo thêm thư mục theo mọi tổ hợp industry/company/source/direction. Tra cứu những thuộc tính này trong danh mục.
- Khi bắt đầu gán nhãn cấp trang, lưu nhãn theo document_id và page_number trong bộ nhãn riêng. Không coi nhãn cấp PDF là nhãn của mọi trang.

## Ví dụ đọc và lọc trong Python

Chạy từ thư mục gốc dự án:

```python
import json
from pathlib import Path

root = Path.cwd()
with (root / "metadata/documents.jsonl").open(encoding="utf-8") as handle:
    documents = [json.loads(line) for line in handle if line.strip()]

for doc in documents:
    if doc["document_category"] == "Financial_Reports":
        pdf_path = root / "Accounting_Documents" / doc["relative_path"]
        print(doc["document_id"], pdf_path)

asset_purchases = [
    doc for doc in documents
    if doc["document_type"] == "VAT_Invoice"
    and doc["direction"] == "Incoming"
    and "Fixed_Asset_Purchase" in doc["business_tags"]
]
```

Danh mục ban đầu chưa có hóa đơn thật nên bộ lọc cuối có thể trả danh sách rỗng. Các thuộc tính null sẽ chưa khớp bộ lọc; cần xác minh để làm giàu metadata trước khi kết luận về độ phủ dữ liệu.

## Kiểm tra dữ liệu và tra cứu mã INV/AV

Cần Python và package `jsonschema`. Chạy từ thư mục gốc dự án:

```powershell
python scripts/validate_metadata.py
python -m unittest discover -s tests -v
```

Lệnh kiểm tra đối chiếu schema, taxonomy, 34 ánh xạ INV, 47 ánh xạ AV theo đúng số lượng 7 nhóm, ví dụ, danh mục, đường dẫn và SHA-256 của tài liệu gốc. Các test kiểm tra hóa đơn có nhiều thuộc tính, tên thay thế, tham chiếu chéo giữa AV/INV và các loại chứng từ dễ nhầm.

```python
from scripts.validate_metadata import load_bundle, matching_invoice_codes

bundle = load_bundle()
example = bundle["examples"]["invoice.example.json"]
print(matching_invoice_codes(example, bundle["mapping"]))
# INV001, INV005, INV007, INV023, INV024
```

```python
from scripts.validate_metadata import canonical_document_type, matching_voucher_codes

print(canonical_document_type("Cash_Receipt_Slip", bundle["taxonomy"]))
# Cash_Receipt

voucher = bundle["examples"]["voucher.cash-receipt.example.json"]
print(matching_voucher_codes(voucher, bundle["voucher_mapping"]))
# ['AV001']

receipt = bundle["examples"]["voucher.cash-receipt-slip.example.json"]
print(matching_voucher_codes(receipt, bundle["voucher_mapping"]))
# ['AV003']
print(matching_invoice_codes(receipt, bundle["mapping"]))
# ['INV018']
```
