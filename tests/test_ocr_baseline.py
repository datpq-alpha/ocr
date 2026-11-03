from argparse import Namespace
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import hashlib
import json
import tempfile
import unittest

from scripts.ocr_baseline import VIETNAMESE_REQUIRED, check_charset, download_cached, draft, load_samples, run, score, write_json


class BaselineTests(unittest.TestCase):
    def test_reject_recognizer_without_vietnamese_alphabet(self):
        with self.assertRaisesRegex(ValueError, "cannot represent"):
            check_charset(list("abcABC0123"), "vi", "wrong-checkpoint")
        self.assertEqual(check_charset(sorted(VIETNAMESE_REQUIRED), "vi", "vi-checkpoint")["missing_required_characters"], [])
        self.assertEqual(check_charset(list("abcABC0123"), "en", "english-checkpoint")["language"], "en")
        with self.assertWarnsRegex(RuntimeWarning, "incomplete Vietnamese baseline"):
            report = check_charset(list("abcABC0123"), "vi", "limited-checkpoint", strict=False)
        self.assertTrue(report["missing_required_characters"])

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.samples = []

    def add_sample(self, key, reference, prediction, status="Verified"):
        image = self.root / "Accounting_Documents" / "02_Accounting_Vouchers" / f"{key}.png"
        image.parent.mkdir(parents=True, exist_ok=True)
        image.write_bytes(b"unchanged input bytes " + key.encode())
        image_path = image.relative_to(self.root).as_posix()
        checksum = hashlib.sha256(image.read_bytes()).hexdigest()
        sample = {"sample_id": key, "image_path": image_path, "sha256": checksum,
                  "category": "02_Accounting_Vouchers", "subcategory": "Bank_Vouchers",
                  "source_group": None, "split": "Test"}
        self.samples.append(sample)
        write_json(self.root / "ground_truth/manifest.json", {"samples": self.samples})
        text = self.root / "ground_truth/texts" / f"{key}.txt"
        text.parent.mkdir(parents=True, exist_ok=True)
        text.write_text(reference, encoding="utf-8")
        write_json(self.root / "ground_truth/annotations" / f"{key}.json", {
            "sample_id": key, "evaluation_image": image_path,
            "evaluation_sha256": checksum, "reference_text_file": text.relative_to(self.root).as_posix(),
            "status": status, "reviewer": "Dat" if status == "Verified" else None,
        })
        output = self.root / "outputs/test"
        output.mkdir(parents=True, exist_ok=True)
        row = {"sample_id": key, "image_path": image_path, "image_sha256": checksum,
               "text": prediction, "status": "Success", "engine": "paddleocr"}
        with (output / "predictions.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
        return sample

    def score_args(self):
        return Namespace(manifest="ground_truth/manifest.json", run="outputs/test", output=None)

    def run_args(self):
        return Namespace(manifest="ground_truth/manifest.json", engine="paddleocr", output="outputs/fake",
                         sample=None, limit=None, detector="det", recognizer="rec", vietocr_config="vgg_seq2seq",
                         threads=1, batch_size=1, warmup=0, language="vi", overwrite=False)

    def test_cached_checkpoint_checksum_is_verified(self):
        model = self.root / "weights.pdiparams"
        model.write_bytes(b"weights")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            download_cached("https://unused.invalid/model", model, "0"*64)
        self.assertEqual(download_cached("https://unused.invalid/model", model,
                                        hashlib.sha256(b"weights").hexdigest()), model)

    def test_overwrite_keeps_old_run_on_failure_then_replaces_after_success(self):
        self.add_sample("GT000001", "manually reviewed", "old")
        args = self.run_args()
        class FakeEngine:
            failure = False

            def __init__(self, args, root):
                pass

            def predict(self, path):
                if self.failure:
                    raise RuntimeError("inference failure")
                return {"text": "new", "lines": [], "timing_seconds": {"total": 0.01}}
        class FailedInit:
            def __init__(self, args, root):
                raise RuntimeError("initialization failure")
        with redirect_stdout(StringIO()):
            run(args, self.root, FakeEngine)
        output = self.root / args.output
        (output / "texts/GT000001.txt").write_text("old", encoding="utf-8")
        (output / "texts/stale.txt").write_text("stale", encoding="utf-8")
        (output / "scores.json").write_text("old scores", encoding="utf-8")
        references = {p: p.read_bytes() for p in (self.root / "ground_truth").rglob("*") if p.is_file()}
        args.overwrite = True
        with redirect_stdout(StringIO()), self.assertRaisesRegex(RuntimeError, "initialization failure"):
            run(args, self.root, FailedInit)
        self.assertEqual((output / "texts/GT000001.txt").read_text(), "old")
        FakeEngine.failure = True
        with redirect_stdout(StringIO()):
            self.assertEqual(run(args, self.root, FakeEngine), 1)
        self.assertEqual((output / "texts/GT000001.txt").read_text(), "old")
        FakeEngine.failure = False
        with redirect_stdout(StringIO()):
            self.assertEqual(run(args, self.root, FakeEngine), 0)
        self.assertEqual((output / "texts/GT000001.txt").read_text(), "new\n")
        self.assertFalse((output / "texts/stale.txt").exists())
        self.assertFalse((output / "scores.json").exists())
        report = json.loads((output / "run.json").read_text())
        backup = self.root / report["replaced_run_backup"]
        self.assertEqual((backup / "texts/GT000001.txt").read_text(), "old")
        self.assertTrue((backup / "scores.json").exists())
        self.assertEqual(references, {p: p.read_bytes() for p in references})

    def test_overwrite_rejects_labels_unrecognized_directories_and_other_engine(self):
        args = self.run_args()
        args.overwrite = True
        for path in ("ground_truth", "outputs", "Accounting_Documents", "../outside"):
            args.output = path
            with self.subTest(path=path), self.assertRaises(ValueError):
                run(args, self.root)
        args.output = "outputs/existing"
        output = self.root / args.output
        output.mkdir(parents=True)
        sentinel = output / "keep.txt"
        sentinel.write_bytes(b"keep")
        with self.assertRaisesRegex(ValueError, "same engine"):
            run(args, self.root)
        write_json(output / "run.json", {"engine": "vietocr"})
        (output / "predictions.jsonl").write_bytes(b"")
        with self.assertRaisesRegex(ValueError, "same engine"):
            run(args, self.root)
        self.assertEqual(sentinel.read_bytes(), b"keep")

    def test_scores_use_weighted_corpus_errors_and_exclude_drafts(self):
        self.add_sample("GT000001", "a b", "a c")
        self.add_sample("GT000002", "abcdefghij", "abcdefghij")
        self.add_sample("GT000003", "must not count", "wrong", status="Draft")
        with redirect_stdout(StringIO()):
            self.assertEqual(score(self.score_args(), self.root), 0)
        report = json.loads((self.root / "outputs/test/scores.json").read_text())
        self.assertEqual(report["overall"]["images"], 2)
        self.assertAlmostEqual(report["overall"]["cer"], 1/13)
        self.assertAlmostEqual(report["overall"]["wer"], 1/3)
        self.assertEqual(report["pending_references"], 1)

    def test_empty_successful_ocr_counts_as_deletions(self):
        self.add_sample("GT000001", "Tiền: 001.000", "")
        with redirect_stdout(StringIO()):
            score(self.score_args(), self.root)
        report = json.loads((self.root / "outputs/test/scores.json").read_text())
        self.assertEqual(report["overall"]["cer"], 1)
        self.assertEqual(report["overall"]["wer"], 1)

    def test_normalization_preserves_accents_case_and_numeric_separators(self):
        self.add_sample("GT000001", "Thuế\t001.000\n", "Thuế 001,000")
        with redirect_stdout(StringIO()):
            score(self.score_args(), self.root)
        report = json.loads((self.root / "outputs/test/scores.json").read_text())
        self.assertEqual(report["images"][0]["character_errors"], 1)
        self.assertEqual(report["images"][0]["word_errors"], 1)

    def test_changed_input_or_wrong_prediction_hash_is_rejected(self):
        sample = self.add_sample("GT000001", "text", "text")
        predictions = self.root / "outputs/test/predictions.jsonl"
        row = json.loads(predictions.read_text())
        row["image_sha256"] = "0"*64
        predictions.write_text(json.dumps(row), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Prediction image/hash mismatch"):
            score(self.score_args(), self.root)
        (self.root / sample["image_path"]).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "Image changed"):
            load_samples(self.root)

    def test_failed_and_missing_predictions_report_incomplete_coverage(self):
        self.add_sample("GT000001", "one", "one")
        self.add_sample("GT000002", "two", "two")
        self.add_sample("GT000003", "three", "three")
        path = self.root / "outputs/test/predictions.jsonl"
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        rows[1].update(status="Failed", error="backend error")
        path.write_text("\n".join(json.dumps(row) for row in rows[:2]), encoding="utf-8")
        with redirect_stdout(StringIO()):
            self.assertEqual(score(self.score_args(), self.root), 1)
        report = json.loads((self.root / "outputs/test/scores.json").read_text())
        self.assertEqual(report["verified_references"], 3)
        self.assertEqual(report["overall"]["images"], 1)
        self.assertEqual(report["failed_verified_predictions"], 1)
        self.assertEqual(report["missing_verified_predictions"], 1)

    def test_draft_never_overwrites_manual_reference_or_review(self):
        self.add_sample("GT000001", "correct manual text", "incorrect OCR")
        reference = self.root / "ground_truth/texts/GT000001.txt"
        annotation = self.root / "ground_truth/annotations/GT000001.json"
        before = (reference.read_bytes(), annotation.read_bytes())
        with redirect_stdout(StringIO()):
            draft(self.score_args(), self.root)
        self.assertEqual((reference.read_bytes(), annotation.read_bytes()), before)
        annotation.unlink()
        reference.unlink()
        with redirect_stdout(StringIO()):
            draft(self.score_args(), self.root)
        self.assertEqual(reference.read_text(), "incorrect OCR\n")
        self.assertEqual(json.loads(annotation.read_text())["status"], "Draft")

    def test_refresh_drafts_protects_earlier_work_and_verified_labels_with_backup(self):
        self.add_sample("GT000007", "edited but still Draft", "new OCR seven", status="Draft")
        self.add_sample("GT000008", "old draft eight", "new OCR eight", status="Draft")
        self.add_sample("GT000009", "verified nine", "new OCR nine")
        before = {p: p.read_bytes() for p in (self.root / "ground_truth").rglob("*") if p.is_file()}
        args = self.score_args()
        args.refresh_drafts = True
        args.from_sample = "GT000008"
        with redirect_stdout(StringIO()):
            self.assertEqual(draft(args, self.root), 0)
        for key in ("GT000007", "GT000009"):
            for folder, extension in (("texts", ".txt"), ("annotations", ".json")):
                path = self.root / "ground_truth" / folder / (key+extension)
                self.assertEqual(path.read_bytes(), before[path])
        path = self.root / "ground_truth/texts/GT000008.txt"
        self.assertEqual(path.read_text(), "new OCR eight\n")
        backup, = (self.root / "outputs").glob("ground_truth_backup_*")
        for folder, extension in (("texts", ".txt"), ("annotations", ".json")):
            original = self.root / "ground_truth" / folder / ("GT000008"+extension)
            self.assertEqual((backup / folder / original.name).read_bytes(), before[original])

    def test_refresh_drafts_refuses_mismatched_reference(self):
        self.add_sample("GT000008", "old", "new", status="Draft")
        annotation = self.root / "ground_truth/annotations/GT000008.json"
        old = json.loads(annotation.read_text())
        old["evaluation_sha256"] = "0"*64
        write_json(annotation, old)
        args = self.score_args()
        args.refresh_drafts = True
        with self.assertRaisesRegex(ValueError, "Existing draft image/reference mismatch"):
            draft(args, self.root)
        self.assertEqual((self.root / "ground_truth/texts/GT000008.txt").read_text(), "old")

    def test_run_records_per_image_errors_and_refuses_reuse(self):
        self.add_sample("GT000001", "one", "one")
        self.add_sample("GT000002", "two", "two")
        class FakeEngine:
            def __init__(self, args, root):
                pass

            def predict(self, path):
                if path.stem == "GT000002":
                    raise RuntimeError("Unreadable sample")
                return {"text": "one", "lines": [], "timing_seconds": {"total": 0.01}}
        args = Namespace(manifest="ground_truth/manifest.json", engine="paddleocr", output="outputs/fake",
                         sample=None, limit=None, detector="det", recognizer="rec", vietocr_config="vgg_seq2seq",
                         threads=1, batch_size=1, warmup=0, language="vi")
        with redirect_stdout(StringIO()):
            self.assertEqual(run(args, self.root, FakeEngine), 1)
        report = json.loads((self.root / "outputs/fake/run.json").read_text())
        self.assertEqual(report["completed_images"], 1)
        self.assertEqual(report["failed_images"], 1)
        self.assertTrue((self.root / "outputs/fake/texts/GT000001.txt").exists())
        self.assertFalse((self.root / "outputs/fake/texts/GT000002.txt").exists())
        with self.assertRaises(FileExistsError):
            run(args, self.root, FakeEngine)


if __name__ == "__main__":
    unittest.main()
