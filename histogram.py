import json
import os
from typing import Dict, List, Tuple

import cv2 as cv
import numpy as np


DEFAULT_BINS = 256
DEFAULT_NORMALIZE = True


def load_rgb_dictionary(
    json_path: str = "rgb_dictionary.json",
) -> Dict[str, List[float]]:
    """Load the precomputed RGB histograms from a JSON file.

    Returns a mapping: filename -> histogram list (length 3*bins).
    """
    if not os.path.isfile(json_path):
        raise FileNotFoundError(f"RGB dictionary JSON not found: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    by_filename = data.get("by_filename")
    if not isinstance(by_filename, dict):
        raise ValueError("Invalid rgb_dictionary.json format: missing 'by_filename'")
    return by_filename


def compute_rgb_histogram(
    image_bgr: np.ndarray, bins: int = DEFAULT_BINS, normalize: bool = DEFAULT_NORMALIZE
) -> np.ndarray:
    """Compute concatenated RGB histogram using OpenCV consistent with rgb_index.py."""
    if image_bgr is None or image_bgr.size == 0:
        raise ValueError("Empty image provided to compute_rgb_histogram")

    image_rgb = cv.cvtColor(image_bgr, cv.COLOR_BGR2RGB)
    hist_r = cv.calcHist([image_rgb], [0], None, [bins], [0, 256])
    hist_g = cv.calcHist([image_rgb], [1], None, [bins], [0, 256])
    hist_b = cv.calcHist([image_rgb], [2], None, [bins], [0, 256])
    hist = np.concatenate([hist_r, hist_g, hist_b], axis=0).astype(np.float32).ravel()

    if normalize:
        s = hist.sum()
        if s > 0:
            hist /= s
    return hist


def l2_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Euclidean distance between two 1D vectors (assumes same length)."""
    return float(np.linalg.norm(a - b))


def chi_square_distance(p: np.ndarray, q: np.ndarray, eps: float = 1e-12) -> float:
    """Chi-square distance between two histograms (assumes non-negative). Lower is more similar."""
    return float(0.5 * np.sum(((p - q) ** 2) / (p + q + eps)))


def bhattacharyya_distance(p: np.ndarray, q: np.ndarray) -> float:
    """Bhattacharyya distance for (L1) normalized histograms in [0,1]. Lower is more similar."""
    # Clamp negatives due to numeric noise and (re)normalize to be safe
    p = np.clip(p, 0, None)
    q = np.clip(q, 0, None)
    sp = p.sum()
    sq = q.sum()
    if sp > 0:
        p = p / sp
    if sq > 0:
        q = q / sq
    bc = float(np.sum(np.sqrt(p * q)))
    bc = max(0.0, min(1.0, bc))
    return float(np.sqrt(max(0.0, 1.0 - bc)))


def search_images_by_histogram(
    query_image_path: str,
    db_json_path: str = "rgb_dictionary.json",
    bins: int = DEFAULT_BINS,
    normalize: bool = DEFAULT_NORMALIZE,
    metric: str = "chi2",
) -> Tuple[List[str], Dict[str, float]]:
    """Compare query image histogram to database and return images sorted by distance (closest first).

    Returns: (sorted_filenames, distances)
    """
    if not os.path.isfile(query_image_path):
        raise FileNotFoundError(f"Query image not found: {query_image_path}")

    # Load database
    db = load_rgb_dictionary(db_json_path)

    # Load and compute query histogram
    img = cv.imread(query_image_path)
    if img is None:
        raise ValueError(
            "cv.imread returned None for query image (unsupported or unreadable)"
        )
    q_hist = compute_rgb_histogram(img, bins=bins, normalize=normalize)

    # Compare
    distances: Dict[str, float] = {}
    q_len = q_hist.shape[0]
    for fname, hist_list in db.items():
        # Ensure vector sizes match; skip otherwise
        h = np.asarray(hist_list, dtype=np.float32).ravel()
        if h.shape[0] != q_len:
            # Different bin configuration; skip
            continue
        # Safeguard: L1 normalize DB hist as well if requested
        if normalize:
            s = h.sum()
            if s > 0:
                h = h / s

        if metric == "bhattacharyya":
            d = bhattacharyya_distance(q_hist, h)
        elif metric in ("chi2", "chi_square", "chi-square"):
            d = chi_square_distance(q_hist, h)
        elif metric in ("l2", "euclidean"):
            d = l2_distance(q_hist, h)
        else:
            d = bhattacharyya_distance(q_hist, h)
        distances[fname] = d

    sorted_images = [k for k, _ in sorted(distances.items(), key=lambda x: x[1])]
    return sorted_images, distances
