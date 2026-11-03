"""Conservative layout handling for upright, visibly ruled tables on CPU.

No template coordinates or ground-truth text are used. Borderless, broken or
rotated grids fall back to the runner's ordinary line order.
"""


def bounds(polygon):
    xs, ys = zip(*polygon)
    return [float(min(xs)), float(min(ys)), float(max(xs)), float(max(ys))]


def rectangle(box):
    x0, y0, x1, y1 = box
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def clusters(values, tolerance=5):
    groups = []
    for value in sorted(values):
        if groups and value - groups[-1][-1] <= tolerance:
            groups[-1].append(value)
        else:
            groups.append([value])
    return [sum(group) / len(group) for group in groups]


def ruled_tables(image):
    import cv2
    import numpy as np

    height, width = image.shape[:2]
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ink = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY_INV, 31, 15)
    horizontal = cv2.morphologyEx(ink, cv2.MORPH_OPEN,
                                  np.ones((1, max(30, width // 30)), np.uint8))
    vertical = cv2.morphologyEx(ink, cv2.MORPH_OPEN,
                                np.ones((max(25, height // 40), 1), np.uint8))
    grid = cv2.bitwise_or(horizontal, vertical)
    grid = cv2.morphologyEx(grid, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
    count, labels, stats, _ = cv2.connectedComponentsWithStats(grid, connectivity=8)
    tables = []
    for label in range(1, count):
        x, y, w, h, area = map(int, stats[label])
        if w < max(80, width * .15) or h < 35 or area < 150:
            continue
        # Use this connected grid only: a page frame must not absorb a table inside it.
        component = (labels[y:y+h, x:x+w] == label).astype("uint8") * 255
        closed = cv2.dilate(component, np.ones((3, 3), np.uint8))
        n, _, spaces, _ = cv2.connectedComponentsWithStats(255 - closed, connectivity=8)
        cells = []
        for i in range(1, n):
            cx, cy, cw, ch, ca = map(int, spaces[i])
            if (cx <= 0 or cy <= 0 or cx+cw >= w or cy+ch >= h
                    or cw < 12 or ch < 10 or ca / (cw*ch) < .88):
                continue
            cells.append({"bbox": [x+cx, y+cy, x+cx+cw, y+cy+ch]})
        if len(cells) < 4:
            continue
        x_edges = clusters([edge for cell in cells for edge in (cell["bbox"][0], cell["bbox"][2])])
        y_edges = clusters([edge for cell in cells for edge in (cell["bbox"][1], cell["bbox"][3])])
        if len(x_edges) < 3 or len(y_edges) < 3:
            continue
        # Overlapping tables or L-shaped holes are ambiguous, so retain ordinary OCR there.
        for cell in cells:
            x0, y0, x1, y1 = cell["bbox"]
            col, end_col = [min(range(len(x_edges)), key=lambda i: abs(x_edges[i]-v)) for v in (x0, x1)]
            row, end_row = [min(range(len(y_edges)), key=lambda i: abs(y_edges[i]-v)) for v in (y0, y1)]
            cell.update(row=row, column=col, row_span=end_row-row, column_span=end_col-col)
        if any(c["row_span"] < 1 or c["column_span"] < 1 for c in cells):
            continue
        cells.sort(key=lambda c: (c["row"], c["column"]))
        occupied = set()
        valid = True
        for cell in cells:
            slots = {(r, c) for r in range(cell["row"], cell["row"]+cell["row_span"])
                     for c in range(cell["column"], cell["column"]+cell["column_span"])}
            if slots & occupied:
                valid = False
                break
            occupied.update(slots)
        # A badly fragmented grid should not impose a speculative reading order.
        if valid and len(occupied) / ((len(y_edges)-1)*(len(x_edges)-1)) >= .9:
            tables.append({"bbox": [x, y, x+w, y+h], "rows": len(y_edges)-1,
                           "columns": len(x_edges)-1, "cells": cells})
    ambiguous = set()
    for i, left in enumerate(tables):
        for j in range(i+1, len(tables)):
            a, b = left["bbox"], tables[j]["bbox"]
            if min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1]):
                ambiguous.update((i, j))
    tables = [table for i, table in enumerate(tables) if i not in ambiguous]
    tables.sort(key=lambda table: (table["bbox"][1], table["bbox"][0]))
    for ti, table in enumerate(tables):
        table["table_id"] = ti
        for ci, cell in enumerate(table["cells"]):
            cell.update(cell_id=ci, line_indices=[])
    return tables


def prepare_regions(polygons, tables, reading_order):
    """Split detector boxes crossing grid boundaries before recognition.

    Keep an original region if grid cells do not explain at least 80% of it;
    no such unmatched region is discarded during serialization.
    """
    import cv2
    import numpy as np

    regions = []
    for polygon in reading_order(polygons):
        polygon = np.asarray(polygon, dtype="float32")
        original = {"polygon": polygon, "table_id": None, "cell_id": None}
        x0, y0, x1, y1 = bounds(polygon)
        polygon_area = max(float(cv2.contourArea(polygon)), 1.)
        fragments, total_area = [], 0.
        for table in tables:
            for cell in table["cells"]:
                box = cell["bbox"]
                if box[0] >= x1 or box[2] <= x0 or box[1] >= y1 or box[3] <= y0:
                    continue
                # Extend the inner-cell boundary by one pixel towards the ruling.
                clip = np.asarray(rectangle([box[0]-1, box[1]-1, box[2]+1, box[3]+1]), dtype="float32")
                overlap, _ = cv2.intersectConvexConvex(polygon, clip)
                if overlap < 12:
                    continue
                intersection = [max(x0, box[0]-1), max(y0, box[1]-1),
                                min(x1, box[2]+1), min(y1, box[3]+1)]
                if intersection[2]-intersection[0] < 4 or intersection[3]-intersection[1] < 4:
                    continue
                part = polygon if overlap / polygon_area >= .98 else np.asarray(rectangle(intersection), dtype="float32")
                fragments.append({"polygon": part, "table_id": table["table_id"], "cell_id": cell["cell_id"]})
                total_area += overlap
        if fragments and total_area / polygon_area >= .8:
            regions.extend(fragments)
        else:
            regions.append(original)
    for index, region in enumerate(regions):
        if region["table_id"] is not None:
            tables[region["table_id"]]["cells"][region["cell_id"]]["line_indices"].append(index)
    return regions


def assemble_text(regions, texts, tables, reading_order):
    """Each cell is emitted once; its wrapped lines stay together.

    A merged cell is written at its top-left slot, with empty covered slots.
    Unassigned detector regions remain in the output, including ambiguous ones
    overlapping a table.
    """
    import numpy as np

    def ordered(indices):
        # reading_order creates new arrays; use exact coordinates to map back.
        lookup = {}
        for i in indices:
            key = np.asarray(regions[i]["polygon"], dtype="float32").tobytes()
            lookup.setdefault(key, []).append(i)
        return [lookup[p.tobytes()].pop(0) for p in reading_order([regions[i]["polygon"] for i in indices])]

    blocks = []
    for table in tables:
        rows = [[""] * table["columns"] for _ in range(table["rows"])]
        for cell in table["cells"]:
            indices = ordered(cell["line_indices"])
            cell["line_indices"] = indices
            cell["text"] = " ".join(texts[i].strip() for i in indices if texts[i].strip())
            rows[cell["row"]][cell["column"]] = cell["text"]
        table["text"] = "\n".join("\t".join(row) for row in rows if any(row))
        if table["text"]:
            blocks.append((float(table["bbox"][1]), float(table["bbox"][0]), table["text"]))
    outside = ordered([i for i, region in enumerate(regions) if region["table_id"] is None])
    # Preserve existing outside-line order while inserting each table as a block.
    result, cursor = [], 0
    blocks.sort()
    for index in outside:
        y = float(np.asarray(regions[index]["polygon"])[:, 1].mean())
        while cursor < len(blocks) and blocks[cursor][0] <= y:
            result.append(blocks[cursor][2])
            cursor += 1
        result.append(texts[index])
    result.extend(block[2] for block in blocks[cursor:])
    return "\n".join(result)
