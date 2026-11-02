from copy import deepcopy
import unittest

from jsonschema import Draft202012Validator, FormatChecker

from scripts.validate_metadata import (
    canonical_document_type, load_bundle, mapping_example,
    matching_invoice_codes, matching_voucher_codes,
)


class InvoiceMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_bundle()
        cls.validator = Draft202012Validator(cls.bundle["schema"], format_checker=FormatChecker())

    def example(self, name="invoice.example.json"):
        return deepcopy(self.bundle["examples"][name])

    def codes(self, record):
        self.validator.validate(record)
        return set(matching_invoice_codes(record, self.bundle["mapping"]))

    def test_each_requested_code_has_valid_example(self):
        items = self.bundle["mapping"]["items"]
        self.assertEqual({item["code"] for item in items}, {f"INV{i:03d}" for i in range(1, 35)})
        for item in items:
            with self.subTest(code=item["code"]):
                self.assertIn(item["code"], self.codes(mapping_example(item, self.example())))

    def test_electronic_invoice_can_arrive_as_scan(self):
        record = self.example("invoice.scanned-electronic.example.json")
        self.assertEqual(record["source"], "Scanned")
        self.assertIn("INV005", self.codes(record))

    def test_electronic_source_does_not_establish_issuance_form(self):
        record = self.example()
        record["issuance_form"] = None
        self.assertNotIn("INV005", self.codes(record))

    def test_vat_adjustment_preserves_both_dimensions(self):
        codes = self.codes(self.example("invoice.adjusted-vat.example.json"))
        self.assertTrue({"INV001", "INV013"} <= codes)
        self.assertNotIn("INV014", codes)

    def test_outgoing_vat_is_not_automatically_sales_invoice_kind(self):
        record = self.example()
        record["direction"] = "Outgoing"
        codes = self.codes(record)
        self.assertIn("INV001", codes)
        self.assertNotIn("INV002", codes)
        self.assertNotIn("INV007", codes)

    def test_sales_kind_can_be_incoming(self):
        record = self.example()
        record.update({"document_type": "Sales_Invoice", "invoice_kind": "Sales_Invoice"})
        self.assertTrue({"INV002", "INV007"} <= self.codes(record))

    def test_receipt_does_not_become_invoice_through_tags(self):
        record = self.example("receipt.deposit.example.json")
        record.update({"issuance_form": "Electronic", "business_tags": ["Transportation"]})
        codes = self.codes(record)
        self.assertIn("INV019", codes)
        self.assertFalse({"INV001", "INV005", "INV009"} & codes)

    def test_multiple_business_contexts_match_one_file(self):
        self.assertTrue({"INV001", "INV005", "INV007", "INV023", "INV024"} <= self.codes(self.example()))

    def test_unknown_tag_is_rejected(self):
        record = self.example()
        record["business_tags"] = ["FixedAssetPurchsae"]
        self.assertFalse(self.validator.is_valid(record))

    def test_conflicting_kind_and_role_are_rejected(self):
        for name, updates in [
            ("invoice.example.json", {"invoice_kind": "Sales_Invoice"}),
            ("invoice.adjusted-vat.example.json", {"invoice_role": "Replacement"}),
            ("receipt.deposit.example.json", {"invoice_kind": "VAT_Invoice"}),
        ]:
            with self.subTest(name=name, updates=updates):
                record = self.example(name)
                record.update(updates)
                self.assertFalse(self.validator.is_valid(record))

    def test_financial_report_keeps_invoice_dimensions_null(self):
        record = deepcopy(self.bundle["records"][0])
        record["issuance_form"] = "Electronic"
        self.assertFalse(self.validator.is_valid(record))

    def test_unknown_values_do_not_match_invoice_code(self):
        record = self.example()
        record.update({"document_type": None, "invoice_kind": None, "invoice_role": None,
                       "issuance_form": None, "direction": None, "business_tags": [],
                       "classification_status": "Needs_Review"})
        self.assertEqual(self.codes(record), set())

    def test_path_traversal_and_backslashes_are_rejected(self):
        for path in ["03_Invoices/../outside.pdf", "03_Invoices/Asset_Invoices/../../outside.pdf", "03_Invoices/Asset_Invoices/..\\outside.pdf"]:
            with self.subTest(path=path):
                record = self.example()
                record["relative_path"] = path
                self.assertFalse(self.validator.is_valid(record))

    def test_invalid_date_rejected_and_negative_amount_preserved(self):
        record = self.example("invoice.adjusted-vat.example.json")
        record["total_amount"] = -11000000
        self.validator.validate(record)
        record["invoice_date"] = "2026-02-30"
        self.assertFalse(self.validator.is_valid(record))


class VoucherMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = load_bundle()
        cls.validator = Draft202012Validator(cls.bundle["schema"], format_checker=FormatChecker())

    def example(self, name="voucher.cash-receipt.example.json"):
        return deepcopy(self.bundle["examples"][name])

    def av_codes(self, record):
        self.validator.validate(record)
        return set(matching_voucher_codes(record, self.bundle["voucher_mapping"]))

    def test_all_47_codes_have_valid_metadata(self):
        items = self.bundle["voucher_mapping"]["items"]
        self.assertEqual(len(items), 47)
        self.assertEqual({item["code"] for item in items}, {f"AV{i:03d}" for i in range(1, 48)})
        for item in items:
            with self.subTest(code=item["code"]):
                record = mapping_example(item, self.example())
                self.assertEqual(self.av_codes(record), {item["code"]})

    def test_seven_group_counts(self):
        items = self.bundle["voucher_mapping"]["items"]
        self.assertEqual(
            [sum(item["group_code"] == group["code"] for item in items) for group in self.bundle["voucher_mapping"]["groups"]],
            [7, 7, 6, 6, 6, 8, 7],
        )

    def test_cash_voucher_and_cash_receipt_remain_distinct(self):
        voucher = self.example()
        slip = self.example("voucher.cash-receipt-slip.example.json")
        self.assertEqual(self.av_codes(voucher), {"AV001"})
        self.assertEqual(self.av_codes(slip), {"AV003"})
        self.assertNotIn("INV018", matching_invoice_codes(voucher, self.bundle["mapping"]))
        self.assertIn("INV018", matching_invoice_codes(slip, self.bundle["mapping"]))

    def test_cash_receipt_slip_alias_normalizes_to_existing_type(self):
        self.assertEqual(canonical_document_type("Cash_Receipt_Slip", self.bundle["taxonomy"]), "Cash_Receipt")
        record = self.example("voucher.cash-receipt-slip.example.json")
        record["document_type"] = "Cash_Receipt_Slip"
        self.assertFalse(self.validator.is_valid(record))
        record["document_type"] = canonical_document_type(record["document_type"], self.bundle["taxonomy"])
        self.assertEqual(self.av_codes(record), {"AV003"})

    def test_balance_confirmation_reuses_bank_statement_category(self):
        record = self.example("voucher.bank-balance.example.json")
        self.assertEqual(canonical_document_type("Bank_Balance_Confirmation", self.bundle["taxonomy"]), "Balance_Confirmation")
        self.assertEqual(record["document_category"], "Bank_Statements")
        self.assertEqual(self.av_codes(record), {"AV014"})
        record.update({"document_category": "Accounting_Vouchers", "document_subcategory": "Bank_Vouchers"})
        self.assertFalse(self.validator.is_valid(record))

    def test_bank_debit_advice_is_not_debit_note(self):
        record = self.example("voucher.bank-debit.example.json")
        self.assertEqual(self.av_codes(record), {"AV008"})
        self.assertNotIn("INV022", matching_invoice_codes(record, self.bundle["mapping"]))
        item = next(item for item in self.bundle["mapping"]["items"] if item["code"] == "INV022")
        debit_note = mapping_example(item, self.bundle["examples"]["invoice.example.json"])
        self.validator.validate(debit_note)
        self.assertNotIn("AV008", matching_voucher_codes(debit_note, self.bundle["voucher_mapping"]))

    def test_wrong_voucher_subgroup_is_rejected(self):
        record = self.example()
        record["document_subcategory"] = "Payroll_Vouchers"
        self.assertFalse(self.validator.is_valid(record))

    def test_accounting_adjustment_is_not_invoice_adjustment(self):
        item = next(item for item in self.bundle["voucher_mapping"]["items"] if item["code"] == "AV045")
        record = mapping_example(item, self.example())
        self.assertEqual(self.av_codes(record), {"AV045"})
        self.assertNotIn("INV013", matching_invoice_codes(record, self.bundle["mapping"]))

    def test_depreciation_is_not_asset_purchase_invoice(self):
        record = self.example("voucher.depreciation.example.json")
        self.assertEqual(self.av_codes(record), {"AV030"})
        self.assertEqual(matching_invoice_codes(record, self.bundle["mapping"]), [])

    def test_group_only_label_does_not_invent_specific_av_code(self):
        record = self.example()
        record.update({"document_type": "Cash_Voucher", "classification_status": "Needs_Review"})
        self.assertEqual(self.av_codes(record), set())
        record["document_type"] = None
        self.assertEqual(self.av_codes(record), set())

    def test_unknown_alias_is_rejected(self):
        with self.assertRaises(ValueError):
            canonical_document_type("BankDebtiAdvice", self.bundle["taxonomy"])


if __name__ == "__main__":
    unittest.main()
