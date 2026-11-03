"""Download the reviewed public bill dataset; do not import it as full-page OCR truth."""

import argparse
from pathlib import Path
import sys

if __package__:
    from .ocr_baseline import ROOT, digest, download_cached, inside, write_json
else:
    from ocr_baseline import ROOT, digest, download_cached, inside, write_json

REPOSITORY = "minhduc168/dataset-origin-vlm-extract-bill"
REVISION = "d24586e71318dec13c69f5f35f3d8bc04c5e561c"
PARQUET = "data/train-00000-of-00001.parquet"
SHA256 = "f97e62eaa9b9417cd0bfe2c27802a45b708166f22a7d35c88770c3e72e72a6a4"
SIZE = 81662819


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--output", default="datasets/external/vlm_extract_bill")
    args = cli.parse_args()
    target = inside(ROOT, args.output)
    allowed = inside(ROOT, "datasets/external")
    if target == allowed or not target.is_relative_to(allowed):
        raise ValueError("Output must be a dataset directory under datasets/external/.")
    url = f"https://huggingface.co/datasets/{REPOSITORY}/resolve/{REVISION}/{PARQUET}"
    path = download_cached(url, target / PARQUET, SHA256)
    if path.stat().st_size != SIZE:
        raise ValueError(f"Unexpected Parquet size: {path.stat().st_size}")
    card_url = f"https://huggingface.co/datasets/{REPOSITORY}/resolve/{REVISION}/README.md"
    card = download_cached(card_url, target / "README.upstream.md")
    write_json(target / "source.json", {
        "repository": REPOSITORY, "revision": REVISION, "url": url,
        "parquet_file": PARQUET, "sha256": digest(path), "bytes": SIZE,
        "upstream_readme_sha256": digest(card), "declared_license": "mit",
        "declared_split": "train", "declared_rows": 982,
        "columns": ["image", "source_image", "master_data"],
        "annotation_scope": "Structured line items, not a complete OCR transcription",
        "imported_to_baseline": False,
    })
    print(f"Saved {path} ({SIZE/1_000_000:.2f} MB); SHA256 verified.")
    print("Source images and structured labels are embedded in Parquet. Existing ground truth is unchanged.")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    try:
        raise SystemExit(main())
    except (ValueError, FileNotFoundError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
