"""Same local scoring contract for Ministral and native PaddleOCR-VL notebooks."""

from copy import deepcopy
from contextlib import nullcontext
import hashlib
from types import SimpleNamespace
import unittest

from tests import test_qwen_colab_notebook as contract


class MinistralColabTests(contract.QwenColabTests):
    NOTEBOOK_NAME = "ministral3_3b_colab.ipynb"

    def setUp(self):
        super().setUp()
        self.identity["engine"] = "ministral3_3b"


class PaddleVLColabTests(contract.QwenColabTests):
    NOTEBOOK_NAME = "paddleocr_vl_1_6_colab.ipynb"

    def setUp(self):
        super().setUp()
        self.identity["engine"] = "paddleocr_vl_1_6"

    def load_predict_adapter(self, **extra):
        self.ns.update(MAX_NEW_TOKENS=2, **extra)
        exec(compile(self.cells["predict"], str(self.notebook_path) + ":predict", "exec"), self.ns)

    def test_inference_adapter_trims_prompt_and_preserves_raw_output(self):
        import numpy as np
        from PIL import Image, ImageOps

        class Tensor:
            def __init__(self, value):
                self.value = np.asarray(value)
                self.shape = self.value.shape
            def __getitem__(self, key):
                return Tensor(self.value[key])
            def detach(self):
                return self
            def cpu(self):
                return self
            def tolist(self):
                return self.value.tolist()

        seen = []
        class Model:
            generation_config = SimpleNamespace(eos_token_id=9)
            def generate(self, **kwargs):
                result = Tensor([[10, 11, 12, 3, 4]])
                seen.append(kwargs)
                self.assert_continues = kwargs["stopping_criteria"][0](result, None) is False
                return result
        model = Model()
        original_generate = model.generate
        processor = SimpleNamespace(tokenizer=SimpleNamespace(
            decode=lambda token_ids, **kwargs: "<table><tr><td>1.000</td></tr></table>"))
        blocks = [
            {"block_label": "header", "block_content": "CÔNG TY A", "block_bbox": [0, 0, 30, 10]},
            {"block_label": "table",
             "block_content": "<table><tr><td>Thiết<br>bị</td><td>1.000</td></tr></table>",
             "block_bbox": [0, 10, 30, 40]},
            {"block_label": "footer", "block_content": "Trang 1", "block_bbox": [0, 40, 30, 48]},
        ]
        class Pipeline:
            def predict(self, image_bgr, **kwargs):
                self.seen_pixels = image_bgr
                model.generate(input_ids=Tensor([[10, 11, 12]]),
                               max_new_tokens=kwargs["max_new_tokens"])
                return [SimpleNamespace(json={"res": {"parsing_res_list": blocks}})]
        pipeline = Pipeline()
        sample = deepcopy(self.samples[0])
        path = self.root / sample["image_path"]
        Image.new("RGB", (32, 48), (255, 0, 0)).save(path)
        sample["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.load_predict_adapter(
            MIN_PIXELS=256, MAX_PIXELS=1024, DATA_ROOT=self.root, np=np,
            Image=Image, ImageOps=ImageOps, model=model, processor=processor, pipeline=pipeline,
            torch=SimpleNamespace(
                inference_mode=nullcontext,
                cuda=SimpleNamespace(synchronize=lambda: None, reset_peak_memory_stats=lambda: None,
                                     max_memory_allocated=lambda: 123, max_memory_reserved=lambda: 456)))
        row = self.ns["predict_image"](sample)
        self.assertEqual(row["image_size"], [32, 48])
        self.assertEqual(row["generated_tokens"], 2)
        self.assertEqual(row["input_tokens"], 3)
        self.assertEqual(row["text"], "CÔNG TY A\nThiết\nbị\t1.000\nTrang 1")
        self.assertIn("<table>", row["raw_response"])
        self.assertEqual(row["native_result"]["parsing_res_list"], blocks)
        self.assertTrue(row["truncated"])
        self.assertTrue(model.assert_continues)
        self.assertEqual(model.generate, original_generate)
        self.assertNotIn("generate", model.__dict__)
        self.assertFalse(seen[0]["do_sample"])
        self.assertTrue(seen[0]["use_cache"])
        self.assertEqual(pipeline.seen_pixels[0, 0].tolist(), [0, 0, 255])

    def test_html_text_conversion_preserves_content_and_boundaries(self):
        self.load_predict_adapter()
        convert = self.ns["block_to_text"]
        text = convert({
            "block_label": "table",
            "block_content": '<table><tr><th colspan="2">Tên &amp; số</th></tr>'
                             '<tr><td>Thiết<br>bị</td><td>1.000,50</td></tr></table>',
        })
        self.assertIn("Tên & số", text)
        self.assertIn("Thiết\nbị\t1.000,50", text)
        literal = "x < 5 và y > 2"
        self.assertEqual(convert({"block_label": "text", "block_content": literal}), literal)

    def test_region_hook_restores_generate_after_interrupt(self):
        self.load_predict_adapter()
        class Model:
            def generate(self, **kwargs):
                return None
        model = Model()
        original = model.generate
        progress = SimpleNamespace(update=lambda *args, **kwargs: None)
        with self.assertRaises(KeyboardInterrupt):
            with self.ns["observe_region_generation"](model, None, progress, []):
                self.assertIn("generate", model.__dict__)
                raise KeyboardInterrupt()
        self.assertEqual(model.generate, original)
        self.assertNotIn("generate", model.__dict__)


if __name__ == "__main__":
    unittest.main()
