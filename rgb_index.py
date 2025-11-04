import os
import json
from typing import Dict, List, Tuple
import cv2 as cv
import numpy as np


# Global dictionary mapping image filename -> RGB histogram (concatenated vector)
rgb_dictionary: Dict[str, List[float]] = {}
# 1-based indexed view: index -> { 'filename': str, 'histogram': List[float] }
rgb_indexed_dictionary: Dict[int, Dict[str, List[float]]] = {}


def compute_rgb_histogram(
    image_bgr: np.ndarray, bins: int = 16, normalize: bool = False
) -> np.ndarray:
    
    if image_bgr is None or image_bgr.size == 0:
        raise ValueError("Empty image provided to compute_rgb_histogram")

    # Convert to RGB to match naming
    image_rgb = cv.cvtColor(image_bgr, cv.COLOR_BGR2RGB)

    # Compute histogram per channel
    hist_r = cv.calcHist([image_rgb], [0], None, [bins], [0, 256])
    hist_g = cv.calcHist([image_rgb], [1], None, [bins], [0, 256])
    hist_b = cv.calcHist([image_rgb], [2], None, [bins], [0, 256])

    # Concatenate and convert to 1D float32
    hist = np.concatenate([hist_r, hist_g, hist_b], axis=0).astype(np.float32).ravel()

    if normalize:
        # L1 normalize to sum to 1; avoid division by zero
        s = hist.sum()
        if s > 0:
            hist /= s

    return hist


def build_rgb_index(
    images_dir: str = "images",
    bins: int = 256,
    normalize: bool = True,
    extensions: Tuple[str, ...] = (".jpg", ".jpeg", ".png", ".bmp", ".webp", ".avif"),
) -> Dict[str, List[float]]:
    
    global rgb_dictionary, rgb_indexed_dictionary
    rgb_dictionary.clear()
    rgb_indexed_dictionary.clear()

    if not os.path.isdir(images_dir):
        print(f"[rgb_index] Directory not found: {images_dir}")
        return rgb_dictionary

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
            hist = compute_rgb_histogram(img, bins=bins, normalize=normalize)
            rgb_dictionary[fname] = hist.tolist()
            count_ok += 1
        except Exception as e:
            print(f"[rgb_index] Skip '{fname}': {e}")
            count_fail += 1

    # Build stable indexed view (sorted by filename for determinism)
    for idx, fname in enumerate(sorted(rgb_dictionary.keys()), start=1):
        rgb_indexed_dictionary[idx] = {
            "filename": fname,
            "histogram": rgb_dictionary[fname],
        }

    print(
        f"[rgb_index] Indexed {count_ok} image(s), failed {count_fail} in '{images_dir}'."
    )
    return rgb_dictionary


def save_rgb_dictionary_json(file_path: str = "rgb_dictionary.json") -> None:
    """Save both filename-keyed and indexed dictionaries to a JSON file."""
    if not rgb_dictionary:
        print(
            "[rgb_index] Nothing to save: rgb_dictionary is empty. Build the index first."
        )
        return
    payload = {
        "by_filename": rgb_dictionary,
        "by_index": rgb_indexed_dictionary,
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    print(f"[rgb_index] Wrote JSON dictionary to {file_path}")


if __name__ == "__main__":
    # Quick manual run
    build_rgb_index("images", bins=256, normalize=True)
    # Print a tiny sample
    for i, (k, v) in enumerate(rgb_dictionary.items()):
        print(f"{i + 1:02d}. {k} -> hist length: {len(v)}")
        if i >= 2:
            break
    # Save outputs for later reuse
    save_rgb_dictionary_json("rgb_dictionary.json")
