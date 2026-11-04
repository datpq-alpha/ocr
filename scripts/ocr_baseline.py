"""Run pretrained OCR, prepare reviewed references, and score CER/WER."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import statistics
import sys
import time
import traceback
import unicodedata
import warnings
from uuid import uuid4

if __package__:
    from .ocr_layout import assemble_text, prepare_regions, ruled_tables
else:
    from ocr_layout import assemble_text, prepare_regions, ruled_tables

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "ground_truth/manifest.json"
IMAGE_ROOTS = ("02_Accounting_Vouchers", "03_Invoices")
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
VIETNAMESE_REQUIRED = set(chr(code) for code in range(0x1EA0, 0x1EFA)) | set("ĂăÂâĐđÊêÔôƠơƯư")
DEFAULT_RECOGNIZER = "PP-OCRv6_small_rec"
VI_RECOGNIZER = "ppocrv6_vi"
VI_REPOSITORY = "tieubaoca/pp-ocrv6-medium-rec-vietnamese"
VI_REVISION = "edc19ca6890bedb7a68c055d21190b44fc1aaa00"
VI_FILE_HASHES = {
    "inference.json": "3bd9cb6bd020ea3256d354cefbb68d38b120255393a2e461d7a107de306aa5a3",
    "inference.pdiparams": "ebca3d052b80cff3c8f8e20ed3deda2fc7b41cb39fffcc30c68fdbd221b92704",
    "inference.yml": "e26530feef43bbb3e11b8d4d46705eb0f65b149769bb88acf23a86f73c915ff6",
    "ppocr_keys.txt": "14d4a90049336cab150902cc61b41dc44d80e7b42134c0401998652cd28aaf27",
}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def inside(root, value):
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"Path outside repository: {value}")
    return path


def relative(root, path):
    return path.resolve().relative_to(root.resolve()).as_posix()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_samples(root=ROOT, manifest=MANIFEST, check_images=True):
    samples = read_json(inside(root, manifest))["samples"]
    ids, paths = set(), set()
    for sample in samples:
        key = sample["sample_id"]
        if not re.fullmatch(r"GT\d{6}", key) or key in ids:
            raise ValueError(f"Invalid or duplicate sample ID: {key}")
        path = inside(root, sample["image_path"])
        if path in paths:
            raise ValueError(f"Duplicate image: {path}")
        ids.add(key)
        paths.add(path)
        if check_images and digest(path) != sample["sha256"]:
            raise ValueError(f"Image changed: {key}; review the image and references before updating its hash.")
    return samples


def prepare(root=ROOT):
    """Append new images without renumbering or accepting changed inputs silently."""
    path = root / MANIFEST
    samples = load_samples(root) if path.exists() else []
    known = {sample["image_path"] for sample in samples}
    next_id = max((int(sample["sample_id"][2:]) for sample in samples), default=0) + 1
    from PIL import Image
    for category in IMAGE_ROOTS:
        for image in sorted((root / "Accounting_Documents" / category).rglob("*")):
            if not image.is_file() or image.suffix.lower() not in EXTENSIONS:
                continue
            image_path = relative(root, image)
            if image_path in known:
                continue
            with Image.open(image) as decoded:
                decoded.verify()
            samples.append({
                "sample_id": f"GT{next_id:06d}", "image_path": image_path,
                "sha256": digest(image), "category": category,
                "subcategory": image.parent.name, "source_group": None,
                "split": "Unassigned",
            })
            next_id += 1
    write_json(path, {"manifest_version": "1.0", "samples": samples})
    print(f"Manifest: {len(samples)} images; {dict(Counter(s['category'] for s in samples))}")
    return samples


def reading_order(polygons):
    """A fixed row-major heuristic, shared by both recognizers (no layout model)."""
    import numpy as np
    boxes = [np.asarray(p, dtype="float32").reshape(4, 2) for p in polygons]
    rows = []
    for polygon in sorted(boxes, key=lambda p: (float(p[:, 1].mean()), float(p[:, 0].min()))):
        center = float(polygon[:, 1].mean())
        height = max(1.0, float(polygon[:, 1].max() - polygon[:, 1].min()))
        if rows and abs(center - rows[-1]["center"]) <= 0.5 * min(height, rows[-1]["height"]):
            rows[-1]["boxes"].append(polygon)
        else:
            rows.append({"center": center, "height": height, "boxes": [polygon]})
    return [box for row in rows for box in sorted(row["boxes"], key=lambda p: float(p[:, 0].min()))]


def crop_text(image, polygon):
    import cv2
    import numpy as np
    points = np.asarray(polygon, dtype="float32").reshape(4, 2)
    # Paddle's detector returns TL, TR, BR, BL quadrilaterals.
    width = max(int(round(max(np.linalg.norm(points[0]-points[1]), np.linalg.norm(points[2]-points[3])))), 1)
    height = max(int(round(max(np.linalg.norm(points[0]-points[3]), np.linalg.norm(points[1]-points[2])))), 1)
    target = np.float32([[0, 0], [width-1, 0], [width-1, height-1], [0, height-1]])
    return cv2.warpPerspective(image, cv2.getPerspectiveTransform(points, target), (width, height), borderMode=cv2.BORDER_REPLICATE)


def download_cached(url, target, expected_sha256=None):
    """Keep complete model files only; a failed download must not become a cache hit."""
    if target.is_file() and target.stat().st_size:
        if expected_sha256 and digest(target) != expected_sha256:
            raise ValueError(f"Cached model checksum mismatch: {target}")
        return target
    import requests
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + f".{os.getpid()}.download")
    try:
        print(f"Downloading {url}", flush=True)
        with requests.get(url, stream=True, timeout=(20, 120)) as response:
            response.raise_for_status()
            with temporary.open("wb") as stream:
                for chunk in response.iter_content(1024*1024):
                    stream.write(chunk)
        if not temporary.stat().st_size:
            raise ValueError(f"Empty model download: {url}")
        if expected_sha256 and digest(temporary) != expected_sha256:
            raise ValueError(f"Downloaded model checksum mismatch: {url}")
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return target


def check_charset(characters, language, model_name, strict=True):
    """Expose dictionary limits; optionally reject an unsupported benchmark setup."""
    available = set("".join(characters))
    missing = []
    if language == "vi":
        missing = sorted(char for char in VIETNAMESE_REQUIRED
                         if char not in available
                         and not all(part in available for part in unicodedata.normalize("NFD", char)))
    if missing:
        message = (f"Recognizer {model_name} cannot represent {len(missing)} required Vietnamese characters "
                   f"(examples: {''.join(missing[:12])}). This is an incomplete Vietnamese baseline. "
                   "Choose weights trained with the required alphabet; changing thresholds or swapping a dictionary is not a fix.")
        if strict:
            raise ValueError(message)
        warnings.warn(message, RuntimeWarning, stacklevel=2)
    return {"language": language, "dictionary_entries": len(characters), "missing_required_characters": missing}


class OCR:
    def __init__(self, args, root):
        # Cache model downloads inside this project. No documents are sent to APIs.
        os.environ.setdefault("PADDLE_PDX_CACHE_HOME", str(root / ".cache" / "paddlex"))
        os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")
        os.environ.setdefault("PADDLE_PDX_MODEL_SOURCE", "BOS")
        os.environ.setdefault("MPLCONFIGDIR", str(root / ".cache" / "matplotlib"))
        # On Windows, load PyTorch first to avoid shared-runtime DLL conflicts
        # when VietOCR and the Paddle detector run in the same process.
        if args.engine == "vietocr":
            import torch
        from paddleocr import TextDetection, TextRecognition
        self.args = args
        self.model_files = {}
        common = {"device": "cpu", "cpu_threads": args.threads, "enable_mkldnn": False}
        self.detector = TextDetection(model_name=args.detector, **common)
        if args.engine == "paddleocr":
            import yaml
            if args.recognizer == VI_RECOGNIZER:
                directory = root / ".cache/paddlex/custom_models" / VI_RECOGNIZER / VI_REVISION
                for filename, checksum in VI_FILE_HASHES.items():
                    url = f"https://huggingface.co/{VI_REPOSITORY}/resolve/{VI_REVISION}/{filename}"
                    path = download_cached(url, directory / filename, checksum)
                    self.model_files[f"{VI_RECOGNIZER}/{filename}"] = {"sha256": digest(path), "url": url}
                dictionary_path = directory / "inference.yml"
                config = yaml.safe_load(dictionary_path.read_text(encoding="utf-8"))
                shape = next(op["RecResizeImg"]["image_shape"] for op in config["PreProcess"]["transform_ops"]
                             if "RecResizeImg" in op)
                self.recognizer_source = {"repository": VI_REPOSITORY, "revision": VI_REVISION,
                                          "model_name": config["Global"]["model_name"],
                                          "recognition_image_shape": shape,
                                          "resize": "aspect-preserving padding; dynamic width",
                                          "kind": "community Vietnamese fine-tune"}
                # Keep the exported alphabet, weights and preprocessing together.
                self.charset_check = check_charset(config["PostProcess"]["character_dict"], args.language,
                                                   args.recognizer, strict=True)
                self.recognizer = TextRecognition(model_name=config["Global"]["model_name"],
                                                  model_dir=str(directory), **common)
            else:
                self.recognizer = TextRecognition(model_name=args.recognizer, **common)
                dictionary_path = (Path(os.environ["PADDLE_PDX_CACHE_HOME"]) / "official_models"
                                   / args.recognizer / "inference.yml")
            if not dictionary_path.is_file():
                raise ValueError(f"Cannot verify recognizer dictionary: {dictionary_path}")
            config = yaml.safe_load(dictionary_path.read_text(encoding="utf-8"))
            self.charset_check = check_charset(config["PostProcess"]["character_dict"], args.language,
                                               args.recognizer, strict=args.strict_charset)
        else:
            import yaml
            from vietocr.tool.predictor import Predictor
            torch.set_num_threads(args.threads)
            torch.hub.set_dir(str(root / ".cache" / "torch"))
            cache = root / ".cache" / "vietocr"
            base_url = "https://raw.githubusercontent.com/pbcquoc/vietocr/master/config/"
            config_name = {"vgg_seq2seq": "vgg-seq2seq.yml", "vgg_transformer": "vgg-transformer.yml"}[args.vietocr_config]
            config = {}
            for filename in ("base.yml", config_name):
                path = download_cached(base_url + filename, cache / filename)
                config.update(yaml.safe_load(path.read_text(encoding="utf-8")))
                self.model_files[filename] = {"sha256": digest(path), "url": base_url + filename}
            weights_url = config["weights"]
            weights = download_cached(weights_url, cache / f"{args.vietocr_config}.pth")
            self.model_files[weights.name] = {"sha256": digest(weights), "url": weights_url}
            config["weights"] = str(weights)
            config["device"] = "cpu"
            config["cnn"]["pretrained"] = False
            config["predictor"]["beamsearch"] = False
            self.recognizer = Predictor(config)
        names = [args.detector] + ([args.recognizer] if args.engine == "paddleocr" else [])
        for name in names:
            directory = Path(os.environ["PADDLE_PDX_CACHE_HOME"]) / "official_models" / name
            for path in sorted(directory.glob("inference.*")):
                self.model_files[f"{name}/{path.name}"] = {"sha256": digest(path)}

    def predict(self, image_path):
        import cv2
        import numpy as np
        from PIL import Image, ImageOps
        started = time.perf_counter()
        with Image.open(image_path) as opened:
            rgba = ImageOps.exif_transpose(opened).convert("RGBA")
            white = Image.new("RGBA", rgba.size, "white")
            white.alpha_composite(rgba)
            image = cv2.cvtColor(np.asarray(white.convert("RGB")), cv2.COLOR_RGB2BGR)
        decoded = time.perf_counter()
        layout_mode = getattr(self.args, "layout", "ruled")
        tables = ruled_tables(image) if layout_mode == "ruled" else []
        layout_detected = time.perf_counter()
        detection = self.detector.predict(
            image, batch_size=1, limit_side_len=960, limit_type="max",
            thresh=0.3, box_thresh=0.6, unclip_ratio=1.5,
        )[0]
        regions = prepare_regions(detection["dt_polys"], tables, reading_order)
        polygons = [region["polygon"] for region in regions]
        detected = time.perf_counter()
        crops = [crop_text(image, polygon) for polygon in polygons]
        cropped = time.perf_counter()
        texts, scores = [], []
        for offset in range(0, len(crops), self.args.batch_size):
            batch = crops[offset:offset+self.args.batch_size]
            if self.args.engine == "paddleocr":
                results = self.recognizer.predict(batch, batch_size=len(batch))
                texts.extend(result["rec_text"] for result in results)
                scores.extend(float(result["rec_score"]) for result in results)
            else:
                batch = [Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)) for crop in batch]
                recognized, probabilities = self.recognizer.predict_batch(batch, return_prob=True)
                texts.extend(recognized)
                scores.extend(float(p) if p is not None else None for p in probabilities)
        recognized = time.perf_counter()
        if len(texts) != len(polygons):
            raise RuntimeError("Recognizer returned a different number of lines than crops.")
        text = assemble_text(regions, texts, tables, reading_order)
        finished = time.perf_counter()
        return {
            "text": text,
            "lines": [{"polygon": region["polygon"].tolist(), "text": line, "confidence": score,
                       "table_id": region["table_id"], "cell_id": region["cell_id"]}
                      for region, line, score in zip(regions, texts, scores)],
            "layout": {"method": layout_mode, "tables": tables,
                       "detected_regions": len(detection["dt_polys"]), "recognition_regions": len(regions)},
            "image_size": [int(image.shape[1]), int(image.shape[0])],
            "timing_seconds": {"decode": decoded-started, "layout_detection": layout_detected-decoded,
                               "detection_and_order": detected-layout_detected,
                               "crop": cropped-detected, "recognition": recognized-cropped,
                               "layout_assembly": finished-recognized,
                               "total": finished-started},
        }


def percentile(values, proportion):
    if not values:
        return None
    values = sorted(values)
    index = (len(values)-1)*proportion
    low = int(index)
    high = min(low+1, len(values)-1)
    return values[low] + (values[high]-values[low])*(index-low)


def run(args, root=ROOT, engine_factory=OCR):
    output = inside(root, args.output or f"outputs/{args.engine}")
    if not getattr(args, "overwrite", False):
        return _run(args, root, engine_factory, output)
    output_root = inside(root, "outputs")
    if output == output_root or not output.is_relative_to(output_root):
        raise ValueError("--overwrite is restricted to a run directory inside outputs/.")
    if not output.exists():
        return _run(args, root, engine_factory, output)
    report = output / "run.json"
    if (not report.is_file() or read_json(report).get("engine") != args.engine
            or not (output / "predictions.jsonl").is_file()):
        raise ValueError("--overwrite requires an existing OCR run with the same engine.")
    token = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid4().hex[:8]
    staging = inside(root, output.parent / f".{output.name}.pending_{token}")
    backup = inside(root, output.parent / f"{output.name}_backup_{token}")
    # Both rename targets stay under outputs/. A failed rerun leaves the old run in place.
    for path in (staging, backup):
        if not path.is_relative_to(output_root) or path.exists():
            raise ValueError(f"Invalid replacement directory: {path}")
    result = _run(args, root, engine_factory, staging)
    if result:
        print(f"Previous run retained at {output}; failed rerun retained at {staging}")
        return result
    metadata = read_json(staging / "run.json")
    metadata["replaced_run_backup"] = relative(root, backup)
    write_json(staging / "run.json", metadata)
    output.rename(backup)
    try:
        staging.rename(output)
    except OSError:
        backup.rename(output)
        raise
    print(f"Replaced {output}; previous run backed up at {backup}")
    return 0


def _run(args, root, engine_factory, output):
    samples = load_samples(root, args.manifest)
    if args.sample:
        samples = [sample for sample in samples if sample["sample_id"] == args.sample]
    if args.limit:
        samples = samples[:args.limit]
    if not samples:
        raise ValueError("No matching images.")
    output.mkdir(parents=True, exist_ok=False)
    (output / "texts").mkdir()
    packages = {}
    for package in ("paddleocr", "paddlepaddle", "vietocr", "torch", "torchvision", "numpy"):
        try:
            packages[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            packages[package] = None
    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(), "status": "Initializing",
        "engine": args.engine, "device": "cpu", "python": sys.version,
        "platform": platform.platform(), "packages": packages,
        "configuration": {"detector": args.detector,
                          "recognizer": args.recognizer if args.engine == "paddleocr" else args.vietocr_config,
                          "language": args.language,
                          "threads": args.threads, "recognition_batch_size": args.batch_size,
                          "reading_order": ("ruled-table cells; row-major outside tables"
                                            if getattr(args, "layout", "ruled") == "ruled" else "row-major heuristic"),
                          "layout": getattr(args, "layout", "ruled"), "layout_version": "1.0", "mkldnn": False,
                          "detection": {"limit_side_len": 960, "limit_type": "max", "thresh": 0.3,
                                        "box_thresh": 0.6, "unclip_ratio": 1.5},
                          "warmup_images": args.warmup},
        "samples": [{"sample_id": s["sample_id"], "image_path": s["image_path"], "sha256": s["sha256"]} for s in samples],
    }
    write_json(output / "run.json", metadata)
    try:
        started = time.perf_counter()
        engine = engine_factory(args, root)
        metadata["initialization_seconds"] = time.perf_counter()-started
        metadata["model_files"] = getattr(engine, "model_files", {})
        metadata["charset_check"] = getattr(engine, "charset_check", None)
        metadata["recognizer_source"] = getattr(engine, "recognizer_source", None)
        started = time.perf_counter()
        for _ in range(args.warmup):
            engine.predict(inside(root, samples[0]["image_path"]))
        metadata["warmup_seconds"] = time.perf_counter()-started
    except Exception:
        metadata.update(status="InitializationFailed", error=traceback.format_exc())
        write_json(output / "run.json", metadata)
        raise
    durations, failures = [], 0
    started = time.perf_counter()
    with (output / "predictions.jsonl").open("x", encoding="utf-8") as stream:
        for index, sample in enumerate(samples, 1):
            row = {"sample_id": sample["sample_id"], "image_path": sample["image_path"],
                   "image_sha256": sample["sha256"], "engine": args.engine}
            try:
                row.update(engine.predict(inside(root, sample["image_path"])), status="Success")
                durations.append(row["timing_seconds"]["total"])
                (output / "texts" / f"{sample['sample_id']}.txt").write_text(row["text"] + "\n", encoding="utf-8")
            except Exception:
                failures += 1
                row.update(status="Failed", error=traceback.format_exc())
            stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n")
            stream.flush()
            print(f"[{index}/{len(samples)}] {sample['sample_id']}: {row['status']}", flush=True)
    elapsed = time.perf_counter()-started
    metadata.update(status="Completed" if not failures else "CompletedWithErrors",
                    completed_images=len(durations), failed_images=failures,
                    failure_rate=failures/len(samples), wall_seconds=elapsed,
                    latency_p50_seconds=percentile(durations, 0.5),
                    latency_p95_seconds=percentile(durations, 0.95),
                    measured_inference_passes_per_image=1)
    write_json(output / "run.json", metadata)
    print(f"Saved {output}; successful={len(durations)}, failed={failures}")
    return 1 if failures else 0


def predictions(root, run_path):
    rows = {}
    for line in (inside(root, run_path) / "predictions.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row["sample_id"] in rows:
            raise ValueError(f"Duplicate prediction ID: {row['sample_id']}")
        rows[row["sample_id"]] = row
    return rows


def check_prediction(sample, row):
    if row["image_sha256"] != sample["sha256"] or row["image_path"] != sample["image_path"]:
        raise ValueError(f"Prediction image/hash mismatch: {sample['sample_id']}")


def draft(args, root=ROOT):
    samples = {s["sample_id"]: s for s in load_samples(root, args.manifest)}
    created, refreshed, skipped = 0, 0, 0
    backup = None
    from_sample = getattr(args, "from_sample", None)
    refresh = getattr(args, "refresh_drafts", False)
    if from_sample and from_sample not in samples:
        raise ValueError(f"Unknown start sample: {from_sample}")
    for key, row in predictions(root, args.run).items():
        if key not in samples:
            raise ValueError(f"Prediction not in manifest: {key}")
        sample = samples[key]
        check_prediction(sample, row)
        if row["status"] != "Success" or (from_sample and key < from_sample):
            skipped += 1
            continue
        annotation = root / "ground_truth" / "annotations" / f"{key}.json"
        text_path = root / "ground_truth" / "texts" / f"{key}.txt"
        replacing = annotation.exists() or text_path.exists()
        if replacing:
            # Refresh is explicit and never changes a reviewed reference. The
            # start ID also protects manual edits that still carry Draft status.
            if not refresh or not annotation.is_file() or not text_path.is_file():
                skipped += 1
                continue
            old = read_json(annotation)
            if old.get("status") != "Draft" or old.get("reviewer"):
                skipped += 1
                continue
            if (old.get("sample_id") != key or old.get("evaluation_sha256") != sample["sha256"]
                    or old.get("evaluation_image") != sample["image_path"]
                    or old.get("reference_text_file") != relative(root, text_path)):
                raise ValueError(f"Existing draft image/reference mismatch: {key}")
            if backup is None:
                token = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid4().hex[:8]
                backup = inside(root, f"outputs/ground_truth_backup_{token}")
                backup.mkdir(parents=True, exist_ok=False)
            for source in (annotation, text_path):
                saved = backup / source.relative_to(root / "ground_truth")
                saved.parent.mkdir(parents=True, exist_ok=True)
                saved.write_bytes(source.read_bytes())
        text_path.parent.mkdir(parents=True, exist_ok=True)
        text_path.write_text(row["text"] + "\n", encoding="utf-8")
        write_json(annotation, {
            "sample_id": key, "evaluation_image": sample["image_path"],
            "evaluation_sha256": sample["sha256"],
            "reference_text_file": relative(root, text_path), "scope": "FullImage",
            "status": "Draft", "annotator": None, "reviewer": None,
            "drafted_from": relative(root, inside(root, args.run)),
            "notes": "OCR draft. Compare every line with the image before marking Verified.",
        })
        if replacing:
            refreshed += 1
        else:
            created += 1
    print(f"Drafts created={created}; refreshed={refreshed}; existing labels/failed OCR skipped={skipped}")
    if backup:
        print(f"Previous drafts backed up at {backup}")
    return 0


def normalize(text):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def score(args, root=ROOT):
    from jiwer import process_characters, process_words
    samples = load_samples(root, args.manifest)
    rows = predictions(root, args.run)
    details = []
    verified = failed = missing = pending = 0
    for sample in samples:
        key = sample["sample_id"]
        annotation_path = root / "ground_truth" / "annotations" / f"{key}.json"
        if not annotation_path.exists():
            pending += 1
            continue
        annotation = read_json(annotation_path)
        if annotation.get("status") != "Verified":
            pending += 1
            continue
        if annotation["sample_id"] != key or annotation["evaluation_sha256"] != sample["sha256"] or inside(root, annotation["evaluation_image"]) != inside(root, sample["image_path"]):
            raise ValueError(f"Reference image/hash mismatch: {key}")
        if not annotation.get("reviewer"):
            raise ValueError(f"Verified reference has no reviewer: {key}")
        reference_path = inside(root, annotation["reference_text_file"])
        reference = normalize(reference_path.read_text(encoding="utf-8-sig"))
        if not reference:
            raise ValueError(f"Verified reference is empty: {key}")
        verified += 1
        row = rows.get(key)
        if row is None:
            missing += 1
            details.append({"sample_id": key, "status": "MissingPrediction"})
            continue
        check_prediction(sample, row)
        if row["status"] != "Success":
            failed += 1
            details.append({"sample_id": key, "status": "OCRFailed"})
            continue
        hypothesis = normalize(row["text"])
        characters = process_characters(reference, hypothesis)
        words = process_words(reference, hypothesis)
        details.append({
            "sample_id": key, "category": sample["category"], "status": "Scored",
            "reference_sha256": digest(reference_path),
            "cer": characters.cer, "wer": words.wer,
            "character_errors": characters.substitutions+characters.deletions+characters.insertions,
            "reference_characters": len(reference),
            "word_errors": words.substitutions+words.deletions+words.insertions,
            "reference_words": len(reference.split()),
        })
    scored = [row for row in details if row["status"] == "Scored"]
    if not scored:
        raise ValueError(f"No scorable Verified references (verified={verified}, failed={failed}, missing={missing}).")
    def aggregate(items):
        return {"images": len(items),
                "cer": sum(r["character_errors"] for r in items)/sum(r["reference_characters"] for r in items),
                "wer": sum(r["word_errors"] for r in items)/sum(r["reference_words"] for r in items),
                "mean_image_cer": statistics.mean(r["cer"] for r in items),
                "mean_image_wer": statistics.mean(r["wer"] for r in items)}
    report = {
        "normalization": "Unicode NFC; collapse whitespace; preserve case, accents, punctuation and numeric separators",
        "word_unit": "whitespace token (no Vietnamese linguistic word segmentation)",
        "verified_references": verified, "pending_references": pending,
        "failed_verified_predictions": failed, "missing_verified_predictions": missing,
        "overall": aggregate(scored),
        "by_category": {category: aggregate([r for r in scored if r["category"] == category])
                        for category in sorted({r["category"] for r in scored})},
        "images": details,
    }
    output = inside(root, args.output) if args.output else inside(root, args.run) / "scores.json"
    if output.exists():
        raise ValueError(f"Score report exists: {output}; choose --output with a new name.")
    write_json(output, report)
    print(f"Scored {len(scored)}/{verified} Verified references; pending={pending}, failed={failed}, missing={missing}")
    print(f"CER={report['overall']['cer']:.4%}; WER={report['overall']['wer']:.4%}; {output}")
    return 1 if failed or missing else 0


def parser():
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest="command", required=True)
    commands.add_parser("prepare", help="Index new images in groups 02 and 03; keep existing IDs")
    run_cli = commands.add_parser("run", help="Run CPU OCR; optionally replace an existing run after success")
    run_cli.add_argument("--engine", choices=("paddleocr", "vietocr"), required=True)
    run_cli.add_argument("--manifest", default=MANIFEST)
    run_cli.add_argument("--output", help="Default: outputs/<engine>")
    run_cli.add_argument("--overwrite", action="store_true",
                         help="Replace an existing run in outputs/ only after success; back up the previous run")
    run_cli.add_argument("--sample", help="Run one sample ID")
    run_cli.add_argument("--layout", choices=("ruled", "rows"), default="ruled",
                         help="Group wrapped text within ruled-table cells (default); rows keeps the old line order")
    run_cli.add_argument("--limit", type=int)
    run_cli.add_argument("--detector", default="PP-OCRv6_small_det")
    run_cli.add_argument("--recognizer", default=DEFAULT_RECOGNIZER,
                         help="Paddle model name, or ppocrv6_vi for a pinned community Vietnamese fine-tune")
    run_cli.add_argument("--language", choices=("vi", "en"), default="vi",
                         help="Validate requested script support; does not switch an explicitly selected model")
    run_cli.add_argument("--strict-charset", action="store_true",
                         help="Stop if the recognizer cannot express Vietnamese characters (default: warn and record limitation)")
    run_cli.add_argument("--vietocr-config", choices=("vgg_seq2seq", "vgg_transformer"), default="vgg_seq2seq")
    run_cli.add_argument("--threads", type=int, default=4)
    run_cli.add_argument("--batch-size", type=int, default=8)
    run_cli.add_argument("--warmup", type=int, default=1)
    for name, help_text in (("draft", "Copy OCR into new Draft references; preserve existing labels"),
                            ("score", "Score only human-Verified ground truth")):
        command = commands.add_parser(name, help=help_text)
        command.add_argument("--run", required=True)
        command.add_argument("--manifest", default=MANIFEST)
        if name == "draft":
            command.add_argument("--refresh-drafts", action="store_true",
                                 help="Back up and replace existing unreviewed Drafts; preserve Verified references")
            command.add_argument("--from-sample", help="Only draft this ID and later IDs, e.g. GT000008")
        if name == "score":
            command.add_argument("--output", help="Default: <run>/scores.json; choose a new name to re-score")
    return cli


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    args = parser().parse_args()
    if args.command == "run" and (args.threads < 1 or args.batch_size < 1 or args.warmup < 0 or (args.limit is not None and args.limit < 1)):
        raise ValueError("threads/batch-size/limit must be positive; warmup must be nonnegative.")
    if args.command == "prepare":
        prepare()
        return 0
    return {"run": run, "draft": draft, "score": score}[args.command](args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, FileExistsError, FileNotFoundError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
