"""Exercise notebook export/resume against the real local scorer, without a GPU."""

import ast
from argparse import Namespace
from contextlib import nullcontext, redirect_stdout
from copy import deepcopy
from io import StringIO
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import threading
from types import SimpleNamespace
import unittest
import zipfile

from scripts.ocr_baseline import score, write_json


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks/qwen3_vl_4b_colab.ipynb"


def notebook_cells(path=NOTEBOOK):
    notebook = json.loads(path.read_text(encoding="utf-8"))
    return {cell["id"]: "".join(cell["source"]) for cell in notebook["cells"]}


class QwenColabTests(unittest.TestCase):
    NOTEBOOK_NAME = NOTEBOOK.name

    @classmethod
    def setUpClass(cls):
        cls.notebook_path = ROOT / "notebooks" / cls.NOTEBOOK_NAME
        cls.cells = notebook_cells(cls.notebook_path)

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.ns = {"Path": Path}
        exec(compile(self.cells["helpers"], str(NOTEBOOK) + ":helpers", "exec"), self.ns)
        self.samples = []
        for index, text in enumerate(("Phiếu thu tiền", "Tổng tiền: 1.000.000"), 1):
            key = f"GT{index:06d}"
            relative = f"Accounting_Documents/02_Accounting_Vouchers/{key}.png"
            image = self.root / relative
            image.parent.mkdir(parents=True, exist_ok=True)
            image.write_bytes(b"image fixture " + key.encode())
            sample = {"sample_id": key, "image_path": relative,
                      "sha256": hashlib.sha256(image.read_bytes()).hexdigest(),
                      "category": "02_Accounting_Vouchers"}
            self.samples.append(sample)
            reference = self.root / "ground_truth/texts" / f"{key}.txt"
            reference.parent.mkdir(parents=True, exist_ok=True)
            reference.write_text(text, encoding="utf-8")
            write_json(self.root / "ground_truth/annotations" / f"{key}.json", {
                "sample_id": key, "evaluation_image": relative,
                "evaluation_sha256": sample["sha256"],
                "reference_text_file": reference.relative_to(self.root).as_posix(),
                "status": "Verified", "reviewer": "test",
            })
        write_json(self.root / "ground_truth/manifest.json", {"samples": self.samples})
        self.output = self.root / "outputs/qwen3vl_4b_colab_t4_nf4"
        self.identity = {"engine": "qwen3_vl", "configuration": {"max_new_tokens": 8192}}
        self.session = {"initialization_seconds": 1, "warmup_seconds": 0.5}

    def predict(self, sample):
        text = "Phiếu thu tiền" if sample["sample_id"] == "GT000001" else "Tổng tiền: 1.000.000"
        return {"text": text, "raw_response": text, "truncated": False,
                "timing_seconds": {"total": 0.25},
                "gpu_memory": {"peak_allocated_bytes": 123, "peak_reserved_bytes": 456}}

    def run_notebook(self, predict_fn=None, identity=None):
        with redirect_stdout(StringIO()):
            return self.ns["run_benchmark"](
                self.samples, self.output, identity or self.identity,
                self.session, predict_fn or self.predict)

    def test_all_cells_compile_and_sources_are_unexecuted(self):
        notebook = json.loads(self.notebook_path.read_text(encoding="utf-8"))
        ids = [cell["id"] for cell in notebook["cells"]]
        self.assertEqual(len(ids), len(set(ids)))
        for cell in notebook["cells"]:
            if cell["cell_type"] == "code":
                ast.parse("".join(cell["source"]), filename=str(NOTEBOOK) + ":" + cell["id"])
                self.assertIsNone(cell["execution_count"])
                self.assertEqual(cell["outputs"], [])

    def test_pinned_manifest_matches_local(self):
        # Read literal assignments without executing the Colab/Drive setup.
        assignments = {}
        for node in ast.parse(self.cells["config"]).body:
            if isinstance(node, ast.Assign):
                try:
                    value = ast.literal_eval(node.value)
                except (ValueError, TypeError):
                    continue
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assignments[target.id] = value
        manifest = json.loads((ROOT / "ground_truth/manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(self.ns["canonical_sha256"](manifest),
                         assignments["EXPECTED_MANIFEST_SHA256"])
        self.assertEqual(len(self.ns["validate_samples"](manifest)), 43)

    def test_zip_round_trip_is_accepted_by_existing_scorer(self):
        metadata = self.run_notebook()
        self.assertEqual(metadata["status"], "Completed")
        self.assertEqual(metadata["completed_images"], 2)
        self.assertEqual(metadata["peak_gpu_allocated_bytes"], 123)
        archive = shutil.make_archive(str(self.root / "results"), "zip",
                                      root_dir=self.root, base_dir="outputs/" + self.output.name)
        with zipfile.ZipFile(archive) as zipped:
            self.assertIn("outputs/" + self.output.name + "/predictions.jsonl", zipped.namelist())
            self.assertFalse(any("Accounting_Documents" in name for name in zipped.namelist()))
            zipped.extractall(self.root / "received")
        received = self.root / "received/outputs" / self.output.name
        args = Namespace(manifest="ground_truth/manifest.json",
                         run=received.relative_to(self.root).as_posix(), output=None)
        with redirect_stdout(StringIO()):
            self.assertEqual(score(args, self.root), 0)
        report = json.loads((received / "scores.json").read_text(encoding="utf-8"))
        self.assertEqual(report["overall"]["cer"], 0)
        self.assertEqual(report["overall"]["wer"], 0)

    def test_interrupted_run_resumes_only_missing_ids(self):
        def interrupt(sample):
            if sample["sample_id"] == "GT000002":
                raise KeyboardInterrupt()
            return self.predict(sample)
        with self.assertRaises(KeyboardInterrupt):
            self.run_notebook(interrupt)
        metadata = json.loads((self.output / "run.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["status"], "Interrupted")
        self.assertEqual(metadata["pending_images"], 1)
        # Simulate a damaged JSONL snapshot: records remain the recovery source.
        (self.output / "predictions.jsonl").write_text('{"partial":', encoding="utf-8")
        calls = []
        def resumed(sample):
            calls.append(sample["sample_id"])
            return self.predict(sample)
        metadata = self.run_notebook(resumed)
        self.assertEqual(calls, ["GT000002"])
        self.assertEqual(len(metadata["sessions"]), 2)
        self.assertEqual(metadata["status"], "Completed")
        self.assertEqual(len((self.output / "predictions.jsonl").read_text(encoding="utf-8").splitlines()), 2)
        self.run_notebook(lambda sample: self.fail("Completed images must not run twice"))

    def test_configuration_and_image_hash_mismatches_are_rejected(self):
        self.run_notebook()
        changed = deepcopy(self.identity)
        changed["configuration"]["max_new_tokens"] = 4096
        with self.assertRaisesRegex(ValueError, "Configuration/data/runtime changed"):
            self.run_notebook(identity=changed)
        path = self.output / "records/GT000001.json"
        row = json.loads(path.read_text(encoding="utf-8"))
        row["image_sha256"] = "0" * 64
        write_json(path, row)
        with self.assertRaisesRegex(ValueError, "identity mismatch"):
            self.run_notebook()

    def test_failure_and_truncation_remain_visible_in_scoring(self):
        def incomplete(sample):
            if sample["sample_id"] == "GT000002":
                raise RuntimeError("simulated CUDA OOM")
            row = self.predict(sample)
            row.update(text="Phiếu", raw_response="Phiếu", truncated=True)
            return row
        metadata = self.run_notebook(incomplete)
        self.assertEqual(metadata["status"], "CompletedWithErrors")
        self.assertEqual(metadata["truncated_images"], 1)
        self.assertEqual(metadata["failed_images"], 1)
        self.assertEqual(metadata["failure_rate"], 0.5)
        args = Namespace(manifest="ground_truth/manifest.json",
                         run=self.output.relative_to(self.root).as_posix(), output=None)
        with redirect_stdout(StringIO()):
            self.assertEqual(score(args, self.root), 1)
        report = json.loads((self.output / "scores.json").read_text(encoding="utf-8"))
        self.assertEqual(report["failed_verified_predictions"], 1)
        self.assertEqual(report["overall"]["images"], 1)
        self.assertGreater(report["overall"]["cer"], 0)

    def test_inference_adapter_trims_prompt_and_preserves_raw_output(self):
        import numpy as np
        from PIL import Image, ImageOps

        class Tensor:
            def __init__(self, value):
                self.value = np.asarray(value)
                self.shape = self.value.shape
            def __getitem__(self, item):
                return Tensor(self.value[item])
            def to(self, *args, **kwargs):
                return self
            def detach(self):
                return self
            def cpu(self):
                return self
            def tolist(self):
                return self.value.tolist()

        class Batch(dict):
            def to(self, device):
                self.device = device
                return self

        seen = {}
        raw_text = "```text\nTổng tiền: 1.000.000\n```"
        class Processor:
            def apply_chat_template(self, messages, **kwargs):
                seen["messages"] = messages
                return "prompt"
            def __call__(self, **kwargs):
                seen["processor_args"] = kwargs
                return Batch(input_ids=Tensor([[10, 11, 12]]),
                             image_grid_thw=Tensor([[1, 2, 3]]),
                             image_sizes=Tensor([[48, 32]]),
                             pixel_values=Tensor([0.5]))
            @property
            def tokenizer(self):
                return self
            def decode(self, ids, **kwargs):
                seen["decoded_ids"] = ids
                return raw_text

        class Model:
            generation_config = SimpleNamespace(eos_token_id=[9])
            output_ids = [3, 4]
            def generate(self, **kwargs):
                seen["generation"] = kwargs
                result = Tensor([[10, 11, 12] + self.output_ids])
                seen["monitor_stop"] = kwargs["stopping_criteria"][0](result, None)
                return result

        sample = deepcopy(self.samples[0])
        image = self.root / sample["image_path"]
        Image.new("RGBA", (32, 48), (255, 255, 255, 0)).save(image)
        sample["sha256"] = hashlib.sha256(image.read_bytes()).hexdigest()
        fake_model = Model()
        self.ns.update(
            MAX_NEW_TOKENS=2, MIN_PIXELS=256, MAX_PIXELS=1024, MAX_IMAGE_SIDE=1024,
            PROMPT="transcribe verbatim", DATA_ROOT=self.root,
            Image=Image, ImageOps=ImageOps, processor=Processor(), model=fake_model,
            torch=SimpleNamespace(
                float16="float16", inference_mode=nullcontext,
                cuda=SimpleNamespace(synchronize=lambda: None, reset_peak_memory_stats=lambda: None,
                                     max_memory_allocated=lambda: 123, max_memory_reserved=lambda: 456)))
        exec(compile(self.cells["predict"], str(NOTEBOOK) + ":predict", "exec"), self.ns)
        row = self.ns["predict_image"](sample)
        self.assertEqual(seen["decoded_ids"], [3, 4])
        self.assertEqual(row["text"], raw_text)
        self.assertEqual(row["raw_response"], raw_text)
        self.assertEqual(row["image_size"], [32, 48])
        self.assertEqual(row["generated_tokens"], 2)
        self.assertEqual(row["input_tokens"], 3)
        if "max_pixels" in seen["processor_args"]:
            self.assertEqual(seen["processor_args"]["max_pixels"], 1024)
        else:
            self.assertEqual(seen["processor_args"]["images_kwargs"]["size"]["longest_edge"], 1024)
        self.assertFalse(seen["generation"]["do_sample"])
        self.assertFalse(seen["monitor_stop"])
        self.assertTrue(row["truncated"])
        fake_model.output_ids = [3, 9]
        row = self.ns["predict_image"](sample)
        self.assertFalse(row["truncated"])
        self.assertEqual(row["finish_reason"], "eos")

    def test_heartbeat_reports_before_completion_and_stops_on_exception(self):
        self.ns["MAX_NEW_TOKENS"] = 8192
        exec(compile(self.cells["predict"], str(NOTEBOOK) + ":predict", "exec"), self.ns)
        output = StringIO()
        progress = self.ns["ImageProgress"]("GT000005", interval=0.01)
        with redirect_stdout(output):
            with self.assertRaises(KeyboardInterrupt):
                with progress:
                    progress.update("generation", generated_tokens=10)
                    progress.emit()
                    # Let the background watcher report without waiting for inference to finish.
                    threading.Event().wait(0.04)
                    raise KeyboardInterrupt()
        self.assertIn("GT000005", output.getvalue())
        self.assertIn("generated=10 tokens", output.getvalue())
        self.assertGreaterEqual(output.getvalue().count("GT000005"), 2)
        self.assertFalse(progress.thread.is_alive())


if __name__ == "__main__":
    unittest.main()
