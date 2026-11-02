"""Validate taxonomy, INV/AV mappings, metadata, examples and original files."""

from copy import deepcopy
from pathlib import Path
import hashlib
import json
import sys

from jsonschema import Draft202012Validator, FormatChecker, SchemaError, ValidationError

ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_bundle(root=ROOT):
    metadata = root / "metadata"
    return {
        "taxonomy": load_json(metadata / "taxonomy.json"),
        "schema": load_json(metadata / "document.schema.json"),
        "mapping": load_json(metadata / "invoice_mappings.json"),
        "voucher_mapping": load_json(metadata / "accounting_voucher_mappings.json"),
        "records": [
            json.loads(line)
            for line in (metadata / "documents.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ],
        "examples": {
            path.name: load_json(path)
            for path in sorted((metadata / "examples").glob("*.json"))
        },
    }


def matching_codes(record, mapping):
    """Return all matching codes; a null attribute does not satisfy a value."""
    return [
        item["code"] for item in mapping["items"]
        if Draft202012Validator(item["match"]).is_valid(record)
    ]


def matching_invoice_codes(record, mapping):
    return matching_codes(record, mapping)


def matching_voucher_codes(record, mapping):
    return matching_codes(record, mapping)


def canonical_document_type(code, taxonomy):
    """Normalize a declared alias before schema validation; reject unknown types."""
    canonical = taxonomy.get("document_type_aliases", {}).get(code, code)
    if canonical not in {entry["code"] for entry in taxonomy["document_types"]}:
        raise ValueError(f"Unknown document type: {code}")
    return canonical


def mapping_example(item, base):
    """Build a synthetic metadata record to verify a mapping is satisfiable."""
    record = deepcopy(base)
    record.update({
        "document_type": "Other_Invoice",
        "document_subcategory": item["suggested_subcategory"],
        "invoice_kind": None,
        "invoice_role": None,
        "issuance_form": None,
        "business_tags": [],
    })
    record.update(item["suggested_metadata"])
    return record


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_repository(root=ROOT):
    bundle = load_bundle(root)
    taxonomy, schema, mapping = (bundle[key] for key in ("taxonomy", "schema", "mapping"))
    voucher_mapping = bundle["voucher_mapping"]
    records, examples = bundle["records"], bundle["examples"]
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    version = taxonomy["taxonomy_version"]
    require(schema["properties"]["schema_version"]["const"] == version, "Schema version differs from taxonomy")
    require(mapping["taxonomy_version"] == version == mapping["mapping_version"], "Mapping version differs from taxonomy")
    require(voucher_mapping["taxonomy_version"] == version == voucher_mapping["mapping_version"], "Voucher mapping version differs from taxonomy")
    categories = {entry["code"]: entry for entry in taxonomy["categories"]}
    types = {entry["code"]: entry for entry in taxonomy["document_types"]}
    tags = set(taxonomy["attribute_vocabularies"]["business_tags"])
    require(len(categories) == len(taxonomy["categories"]), "Duplicate category codes")
    require(len(types) == len(taxonomy["document_types"]), "Duplicate document types")
    aliases = taxonomy.get("document_type_aliases", {})
    for alias, canonical in aliases.items():
        require(alias not in types and canonical in types, f"Invalid type alias: {alias}")
    require(set(schema["properties"]["document_type"]["enum"]) == set(types) | {None}, "Type enum is out of sync")
    require(set(schema["properties"]["contained_document_types"]["items"]["enum"]) == set(types), "Contained type enum is out of sync")
    require(set(schema["properties"]["business_tags"]["items"]["enum"]) == tags, "Tag enum is out of sync")
    require({entry["code"] for entry in taxonomy["business_tag_definitions"]} == tags, "Tag definitions are out of sync")
    for field in ("issuance_form", "invoice_kind", "invoice_role"):
        require(set(schema["properties"][field]["enum"]) == set(taxonomy["attribute_vocabularies"][field]) | {None}, f"{field} enum is out of sync")
    data_root = (root / taxonomy["document_root"]).resolve()
    require({p.name for p in data_root.iterdir() if p.is_dir()} == {c["folder"] for c in categories.values()}, "Category directories differ from taxonomy")
    for category in categories.values():
        for sub in category["subcategories"]:
            require(sub["parent_code"] == category["code"], "Invalid subcategory parent")
            require((data_root / sub["folder"]).is_dir(), f"Missing subcategory: {sub['folder']}")
    for entry in types.values():
        require(entry["parent_code"] in categories, f"Unknown parent for {entry['code']}")
        if entry["default_subcategory"]:
            require(entry["default_subcategory"] in {sub["code"] for sub in categories[entry["parent_code"]]["subcategories"]}, f"Invalid default subcategory: {entry['code']}")

    ids, paths = set(), set()
    for record in records:
        validator.validate(record)
        require(not record["is_example"], "Example found in real catalog")
        require(record["document_id"] not in ids, "Duplicate document ID")
        ids.add(record["document_id"])
        path = (data_root / record["relative_path"]).resolve()
        require(path.is_relative_to(data_root), "Document path escapes root")
        require(path not in paths, "Duplicate document path")
        paths.add(path)
        require(path.is_file(), f"Missing file: {path}")
        expected_format = {".pdf": "PDF", ".jpg": "JPG", ".jpeg": "JPG", ".png": "PNG"}.get(path.suffix.lower())
        require(record["format"] == expected_format, f"File format mismatch: {path}")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"], f"Hash mismatch: {path}")
    actual_paths = {p.resolve() for p in data_root.rglob("*") if p.is_file() and p.suffix.lower() in {".pdf", ".jpg", ".jpeg", ".png"}}
    require(actual_paths == paths, "Catalog does not cover every document file")
    for record in records:
        require(set(record["related_document_ids"]) <= ids - {record["document_id"]}, "Unresolved or self-referencing related document")
    example_ids = set()
    for name, record in examples.items():
        validator.validate(record)
        require(record["is_example"] and record["metadata_origin"] == "Illustrative_Example", f"Invalid example marker: {name}")
        require(record["document_id"] not in ids | example_ids, "Example ID collides with another record")
        example_ids.add(record["document_id"])

    codes = [item["code"] for item in mapping["items"]]
    require(len(codes) == 34 and set(codes) == {f"INV{i:03d}" for i in range(1, 35)}, "Expected exactly INV001 through INV034")
    groups = {entry["code"] for entry in mapping["groups"]}
    subcodes = {sub["code"] for sub in categories["Invoices"]["subcategories"]}
    for item in mapping["items"]:
        Draft202012Validator.check_schema(item["match"])
        require(item["group_code"] in groups, f"Unknown group: {item['code']}")
        require(item["suggested_subcategory"] in subcodes | {None}, f"Unknown mapping subcategory: {item['code']}")
        record = mapping_example(item, examples["invoice.example.json"])
        validator.validate(record)
        require(item["code"] in matching_invoice_codes(record, mapping), f"Unsatisfiable mapping: {item['code']}")

    av_items = voucher_mapping["items"]
    av_codes = [item["code"] for item in av_items]
    require(len(av_codes) == 47 and set(av_codes) == {f"AV{i:03d}" for i in range(1, 48)}, "Expected exactly AV001 through AV047")
    expected_av_counts = {
        "Cash_Vouchers": 7, "Bank_Vouchers": 7, "Inventory_Vouchers": 6,
        "Payroll_Vouchers": 6, "Fixed_Asset_Vouchers": 6,
        "Sales_Purchase_Vouchers": 8, "General_Accounting_Vouchers": 7,
    }
    av_groups = {group["code"]: group for group in voucher_mapping["groups"]}
    require(len(av_groups) == len(voucher_mapping["groups"]) == 7 and set(av_groups) == set(expected_av_counts), "Invalid voucher groups")
    require(set(av_groups) == {sub["code"] for sub in categories["Accounting_Vouchers"]["subcategories"]}, "Voucher groups differ from folders")
    require(len({item["canonical_document_type"] for item in av_items}) == 47, "Two AV codes resolve to the same canonical type")
    for group_code, count in expected_av_counts.items():
        require(av_groups[group_code]["expected_count"] == count, f"Invalid declared count: {group_code}")
        require(sum(item["group_code"] == group_code for item in av_items) == count, f"Invalid voucher count: {group_code}")
    for item in av_items:
        Draft202012Validator.check_schema(item["match"])
        require(item["group_code"] in av_groups, f"Unknown voucher group: {item['code']}")
        canonical = canonical_document_type(item["requested_document_type"], taxonomy)
        require(canonical == item["canonical_document_type"] == item["suggested_metadata"]["document_type"], f"Wrong canonical type: {item['code']}")
        entry = types[canonical]
        require(item["suggested_metadata"]["document_category"] == entry["parent_code"], f"Wrong voucher storage category: {item['code']}")
        require(item["suggested_subcategory"] == item["suggested_metadata"]["document_subcategory"] == entry["default_subcategory"], f"Wrong voucher storage subcategory: {item['code']}")
        folder = categories[entry["parent_code"]]["folder"]
        if entry["default_subcategory"]:
            folder += "/" + entry["default_subcategory"]
        require(item["storage_folder"] == folder and (data_root / folder).is_dir(), f"Wrong voucher storage folder: {item['code']}")
        if entry["parent_code"] == "Accounting_Vouchers":
            require(item["group_code"] == entry["default_subcategory"], f"Voucher type/group mismatch: {item['code']}")
        else:
            require(item["code"] in {"AV003", "AV014"}, f"Unexpected cross-category voucher: {item['code']}")
        record = mapping_example(item, examples["voucher.cash-receipt.example.json"])
        validator.validate(record)
        require(item["code"] in matching_voucher_codes(record, voucher_mapping), f"Unsatisfiable voucher mapping: {item['code']}")

    snapshot = load_json(root / "metadata/migration_2026-10-30.json")
    for entry in snapshot["files"]:
        require(hashlib.sha256((root / entry["new_path"]).read_bytes()).hexdigest() == entry["sha256"], f"Original file changed: {entry['new_path']}")
    return f"PASS: v{version}; {len(types)} types, {len(tags)} tags, 34 INV + 47 AV mappings, {len(records)} documents, {len(examples)} examples; paths and hashes verified."


if __name__ == "__main__":
    try:
        print(validate_repository())
    except (ValueError, OSError, ValidationError, SchemaError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
