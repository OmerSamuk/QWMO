import numpy as np
from skimage.feature import graycomatrix, graycoprops
from skimage.measure import label, regionprops
from scipy import ndimage, stats
from typing import Dict, Optional, List


def _get_sitk():
    import SimpleITK as sitk
    return sitk


def load_nifti(path: str) -> np.ndarray:
    sitk = _get_sitk()
    img = sitk.ReadImage(path)
    return sitk.GetArrayFromImage(img)


def load_dicom_series(path: str) -> np.ndarray:
    sitk = _get_sitk()
    reader = sitk.ImageSeriesReader()
    dicom_names = reader.GetGDCMSeriesFileNames(path)
    reader.SetFileNames(dicom_names)
    img = reader.Execute()
    return sitk.GetArrayFromImage(img)


def extract_firstorder(pixels: np.ndarray, mask: np.ndarray) -> Dict[str, float]:
    masked = pixels[mask > 0]
    if len(masked) == 0:
        return {}
    return {
        "mean": float(np.mean(masked)),
        "std": float(np.std(masked)),
        "skewness": float(stats.skew(masked)),
        "kurtosis": float(stats.kurtosis(masked)),
        "p10": float(np.percentile(masked, 10)),
        "p25": float(np.percentile(masked, 25)),
        "p50": float(np.percentile(masked, 50)),
        "p75": float(np.percentile(masked, 75)),
        "p90": float(np.percentile(masked, 90)),
        "min": float(np.min(masked)),
        "max": float(np.max(masked)),
        "energy": float(np.sum(masked ** 2)),
        "entropy": float(-np.sum(masked * np.log(masked + 1e-10))),
    }


def extract_glcm(pixels: np.ndarray, mask: np.ndarray,
                 distances: Optional[List[int]] = None,
                 angles: Optional[List[float]] = None) -> Dict[str, float]:
    if distances is None:
        distances = [1]
    if angles is None:
        angles = [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4]

    masked = pixels.copy()
    masked[mask == 0] = 0
    vmin, vmax = masked[mask > 0].min(), masked[mask > 0].max()
    n_bins = 32
    if vmax <= vmin:
        return {}
    bins = np.linspace(float(vmin), float(vmax + 1e-6), n_bins)
    quantized = np.digitize(masked, bins) - 1

    glcm = graycomatrix(
        quantized, distances=distances, angles=angles,
        levels=n_bins, symmetric=True, normed=True
    )

    features = {}
    props = ["contrast", "dissimilarity", "homogeneity", "energy",
             "correlation", "ASM"]
    for prop in props:
        vals = graycoprops(glcm, prop)
        for d_idx, d in enumerate(distances):
            for a_idx, a in enumerate(angles):
                key = f"glcm_{prop}_d{d}_a{int(a * 4 / np.pi)}"
                features[key] = float(vals[d_idx, a_idx])

    return features


def extract_glrlm(pixels: np.ndarray, mask: np.ndarray) -> Dict[str, float]:
    masked = pixels.copy()
    masked[mask == 0] = 0
    vmin, vmax = masked[mask > 0].min(), masked[mask > 0].max()
    if vmax <= vmin:
        return {}
    n_bins = 32
    bins = np.linspace(float(vmin), float(vmax + 1e-6), n_bins)
    quantized = np.digitize(masked, bins) - 1

    features = {}
    for angle_idx, angle in enumerate([0, 1]):
        runs = _compute_rle(quantized, angle=angle)
        if runs.size == 0:
            continue
        n_gray = n_bins
        n_run = runs.shape[1]
        total = float(np.sum(runs))

        i = np.arange(n_gray, dtype=float)[:, None]
        j = np.arange(n_run, dtype=float)[None, :]

        features[f"glrlm_sre_a{angle}"] = float(np.sum(runs / (j + 1) ** 2) / total) if total > 0 else 0.0
        features[f"glrlm_lre_a{angle}"] = float(np.sum(runs * (j + 1) ** 2) / total) if total > 0 else 0.0
        features[f"glrlm_rlnu_a{angle}"] = float(np.sum(np.sum(runs, axis=1) ** 2) / total) if total > 0 else 0.0
        features[f"glrlm_rp_a{angle}"] = float(np.sum(runs) / np.prod(masked[mask > 0].shape)) if np.prod(masked[mask > 0].shape) > 0 else 0.0

    return features


def _compute_rle(matrix: np.ndarray, angle: int = 0) -> np.ndarray:
    n_gray = int(matrix.max() + 1) if matrix.max() >= 0 else 1
    if angle == 0:
        runs = np.zeros((n_gray, max(matrix.shape[1], 1)), dtype=np.float64)
        for row in matrix:
            vals, lengths = _rle_row(row)
            for v, l in zip(vals, lengths):
                if 0 <= int(v) < n_gray and l - 1 < runs.shape[1]:
                    runs[int(v), l - 1] += 1
    else:
        runs = np.zeros((n_gray, max(matrix.shape[0], 1)), dtype=np.float64)
        for col in matrix.T:
            vals, lengths = _rle_row(col)
            for v, l in zip(vals, lengths):
                if 0 <= int(v) < n_gray and l - 1 < runs.shape[1]:
                    runs[int(v), l - 1] += 1
    return runs


def _rle_row(arr: np.ndarray):
    if len(arr) == 0:
        return [], []
    vals = []
    lengths = []
    current = arr[0]
    count = 1
    for x in arr[1:]:
        if x == current:
            count += 1
        else:
            vals.append(current)
            lengths.append(count)
            current = x
            count = 1
    vals.append(current)
    lengths.append(count)
    return np.array(vals), np.array(lengths)


def extract_shape(mask: np.ndarray, spacing: Optional[List[float]] = None) -> Dict[str, float]:
    labeled = label(mask > 0)
    props = regionprops(labeled, spacing=spacing or [1, 1, 1])
    if not props:
        return {}
    r = props[0]
    return {
        "volume": float(r.area * np.prod(spacing or [1, 1, 1])),
        "surface_area": float(r.perimeter if mask.ndim == 2 else r.perimeter),
        "sphericity": float((np.pi ** (1 / 3) * (6 * r.area) ** (2 / 3)) / r.perimeter) if r.perimeter > 0 else 0.0,
        "compactness": float(r.area / (r.perimeter ** 2 + 1e-10)),
        "elongation": float(r.major_axis_length / (r.minor_axis_length + 1e-10)),
    }


def _central_slice(mask: np.ndarray) -> int:
    indices = np.where(mask > 0)
    if len(indices[0]) == 0:
        return 0
    z_vals = indices[0]
    return int(np.median(z_vals))


def extract_all_features(image: np.ndarray, mask: np.ndarray) -> Dict[str, float]:
    features = {}
    features.update(extract_firstorder(image, mask))
    if image.ndim == 3:
        z = _central_slice(mask)
        slice_img = image[z]
        slice_mask = mask[z]
        if slice_mask.max() > 0:
            features.update(extract_glcm(slice_img, slice_mask))
            features.update(extract_glrlm(slice_img, slice_mask))
    else:
        features.update(extract_glcm(image, mask))
        features.update(extract_glrlm(image, mask))
    features.update(extract_shape(mask))
    return features


def extract_from_path(image_path: str, mask_path: str) -> Dict[str, float]:
    image = load_nifti(image_path)
    mask = load_nifti(mask_path)
    return extract_all_features(image, mask)
