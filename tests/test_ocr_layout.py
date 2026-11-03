import unittest

import cv2
import numpy as np

from scripts.ocr_baseline import reading_order
from scripts.ocr_layout import assemble_text, bounds, prepare_regions, rectangle, ruled_tables


class TableLayoutTests(unittest.TestCase):
    def grid(self):
        image = np.full((300, 400, 3), 255, dtype="uint8")
        for x in (30, 200, 370):
            cv2.line(image, (x, 40), (x, 240), (0, 0, 0), 1)
        for y in (40, 140, 240):
            cv2.line(image, (30, y), (370, y), (0, 0, 0), 1)
        return image

    def test_multiline_cell_is_contiguous_and_empty_cells_stay_empty(self):
        tables = ruled_tables(self.grid())
        self.assertEqual(len(tables), 1)
        self.assertEqual(len(tables[0]["cells"]), 4)
        labels = {(45, 65): "Item name", (45, 100): "continued",
                  (220, 70): "Total", (45, 170): "Second item"}
        polygons = [rectangle([x, y, x+80, y+18]) for x, y in labels]
        regions = prepare_regions(polygons, tables, reading_order)
        texts = [labels[tuple(map(int, bounds(r["polygon"])[:2]))] for r in regions]
        result = assemble_text(regions, texts, tables, reading_order)
        self.assertEqual(result, "Item name continued\tTotal\nSecond item\t")
        self.assertEqual(sum(len(c["line_indices"]) for c in tables[0]["cells"]), 4)

    def test_detection_crossing_two_cells_is_split_before_recognition(self):
        tables = ruled_tables(self.grid())
        regions = prepare_regions([rectangle([40, 65, 350, 88])], tables, reading_order)
        self.assertEqual(len(regions), 2)
        self.assertEqual([r["cell_id"] for r in regions], [0, 1])
        left, right = [bounds(r["polygon"]) for r in regions]
        self.assertLess(left[2], right[0])
        self.assertLessEqual(left[2], 201)
        self.assertGreaterEqual(right[0], 199)

    def test_merged_cell_is_emitted_once_with_span_metadata(self):
        image = np.full((360, 400, 3), 255, dtype="uint8")
        cv2.rectangle(image, (30, 30), (370, 310), (0, 0, 0), 1)
        for y in (110, 210):
            cv2.line(image, (30, y), (370, y), (0, 0, 0), 1)
        cv2.line(image, (200, 110), (200, 310), (0, 0, 0), 1)
        tables = ruled_tables(image)
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0]["cells"][0]["column_span"], 2)
        regions = prepare_regions([rectangle([60, 55, 300, 75])], tables, reading_order)
        text = assemble_text(regions, ["Merged heading"], tables, reading_order)
        self.assertEqual(text, "Merged heading\t")

    def test_page_frame_does_not_absorb_inner_table(self):
        image = self.grid()
        cv2.rectangle(image, (2, 2), (397, 297), (0, 0, 0), 1)
        tables = ruled_tables(image)
        self.assertEqual(len(tables), 1)
        self.assertGreater(tables[0]["bbox"][0], 20)

    def test_nested_grids_fall_back_instead_of_duplicating_recognition(self):
        image = np.full((600, 600, 3), 255, dtype="uint8")
        for x in (30, 300, 570):
            cv2.line(image, (x, 30), (x, 570), (0, 0, 0), 1)
        for y in (30, 300, 570):
            cv2.line(image, (30, y), (570, y), (0, 0, 0), 1)
        for x in (70, 160, 250):
            cv2.line(image, (x, 70), (x, 250), (0, 0, 0), 1)
        for y in (70, 160, 250):
            cv2.line(image, (70, y), (250, y), (0, 0, 0), 1)
        self.assertEqual(ruled_tables(image), [])

    def test_no_grid_retains_all_lines_and_duplicate_regions(self):
        image = np.full((300, 400, 3), 255, dtype="uint8")
        self.assertEqual(ruled_tables(image), [])
        polygon = rectangle([40, 65, 180, 88])
        regions = prepare_regions([polygon, polygon], [], reading_order)
        self.assertEqual(assemble_text(regions, ["first", "second"], [], reading_order), "first\nsecond")

    def test_unmatched_region_is_retained_instead_of_silently_discarded(self):
        tables = ruled_tables(self.grid())
        # Most of this region lies outside the grid, so splitting is unsafe.
        regions = prepare_regions([rectangle([5, 5, 390, 70])], tables, reading_order)
        self.assertEqual(len(regions), 1)
        self.assertIsNone(regions[0]["cell_id"])
        self.assertEqual(assemble_text(regions, ["keep original"], tables, reading_order), "keep original")


if __name__ == "__main__":
    unittest.main()
