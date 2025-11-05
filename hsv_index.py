import os
import json
from typing import Dict, List, Tuple

import cv2 as cv
import numpy as np


# Global dictionary mapping image filename -> HSV histogram (concatenated H,S,V vectors)
hsv_dictionary: Dict[str, List[float]] = {}
# 1-based indexed view: index -> { 'filename': str, 'histogram': List[float] }
hsv_indexed_dictionary: Dict[int, Dict[str, List[float]]] = {}


def compute_hsv_histogram(
    image_bgr: np.ndarray, bins: int = 256, normalize: bool = True
) -> np.ndarray:
    """Compute concatenated HSV channel histograms.

    Note: In OpenCV, H ranges in [0, 180], S and V in [0, 256].
    We still use `bins` bins per channel to keep a fixed-length vector (3*bins).
    """
    if image_bgr is None or image_bgr.size == 0:
        raise ValueError("Empty image provided to compute_hsv_histogram")

    hsv = cv.cvtColor(image_bgr, cv.COLOR_BGR2HSV)

    hist_h = cv.calcHist([hsv], [0], None, [bins], [0, 180])
    hist_s = cv.calcHist([hsv], [1], None, [bins], [0, 256])
    hist_v = cv.calcHist([hsv], [2], None, [bins], [0, 256])

    hist = np.concatenate([hist_h, hist_s, hist_v], axis=0).astype(np.float32).ravel()

    if normalize:
        s = hist.sum()
        if s > 0:
            hist /= s
    return hist


def build_hsv_index(
    images_dir: str = "images",
    bins: int = 256,
    normalize: bool = True,
    extensions: Tuple[str, ...] = (".jpg", ".jpeg", ".png", ".bmp", ".webp", ".avif"),
) -> Dict[str, List[float]]:
    global hsv_dictionary, hsv_indexed_dictionary
    hsv_dictionary.clear()
    hsv_indexed_dictionary.clear()

    if not os.path.isdir(images_dir):
        print(f"[hsv_index] Directory not found: {images_dir}")
        return hsv_dictionary

    files = sorted(os.listdir(images_dir))
    count_ok = 0
    count_fail = 0

    for fname in files:
        if not fname.lower().endswith(extensions):
            continue
        fpath = os.path.join(images_dir, fname)
        try:
            img = cv.imread(fpath)
            if img is None:
                raise ValueError(
                    "cv.imread returned None (unsupported format or unreadable file)"
                )
            hist = compute_hsv_histogram(img, bins=bins, normalize=normalize)
            hsv_dictionary[fname] = hist.tolist()
            count_ok += 1
        except Exception as e:
            print(f"[hsv_index] Skip '{fname}': {e}")
            count_fail += 1

    # Build stable indexed view (sorted by filename for determinism)
    for idx, fname in enumerate(sorted(hsv_dictionary.keys()), start=1):
        hsv_indexed_dictionary[idx] = {
            "filename": fname,
            "histogram": hsv_dictionary[fname],
        }

    print(
        f"[hsv_index] Indexed {count_ok} image(s), failed {count_fail} in '{images_dir}'."
    )
    return hsv_dictionary


def save_hsv_dictionary_json(file_path: str = "hsv_dictionary.json") -> None:
    if not hsv_dictionary:
        print(
            "[hsv_index] Nothing to save: hsv_dictionary is empty. Build the index first."
        )
        return
    payload = {
        "by_filename": hsv_dictionary,
        "by_index": hsv_indexed_dictionary,
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    print(f"[hsv_index] Wrote JSON dictionary to {file_path}")


if __name__ == "__main__":
    build_hsv_index("images", bins=256, normalize=True)
    # small sample print
    for i, (k, v) in enumerate(hsv_dictionary.items()):
        print(f"{i + 1:02d}. {k} -> hist length: {len(v)}")
        if i >= 2:
            break
    save_hsv_dictionary_json("hsv_dictionary.json")
