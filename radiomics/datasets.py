import os
import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class RadiomicsDataset:
    id: str
    name: str
    modality: str
    task: str
    n_samples: int
    tcia_collection_id: str
    license: str
    mask_format: str
    download_path: str
    notes: str = ""


NSCLC_DATASET = RadiomicsDataset(
    id="D1",
    name="NSCLC Radiogenomics",
    modality="CT (toraks)",
    task="2-yil survival / EGFR mutasyon",
    n_samples=211,
    tcia_collection_id="NSCLC_Radiogenomics",
    license="CC BY 4.0",
    mask_format="nii.gz",
    download_path=os.path.join("data", "radiomics", "D1_nsclc"),
    notes="TCIA: https://www.cancerimagingarchive.net/collection/nsclc-radiogenomics/",
)

NSCLC_GENOMICS_DATASET = RadiomicsDataset(
    id="D1a_NSCLC_genes",
    name="NSCLC Radiomics-Genomics (EGFR mutation)",
    modality="CT (toraks)",
    task="EGFR mutation binary",
    n_samples=89,
    tcia_collection_id="NSCLC_Radiogenomics",
    license="CC BY 4.0",
    mask_format="none",
    download_path=os.path.join("data", "radiomics", "D1a_nsclc_genes"),
    notes="NSCLC-Radiomics-Genomics subset, 6.6 GB, 89 patients, CT only (no SEG)",
)

NSCLC_SURVIVAL_DATASET = RadiomicsDataset(
    id="D1b_NSCLC_survival",
    name="NSCLC Radiomics-Genomics (2-y survival)",
    modality="CT (toraks)",
    task="2-year survival binary",
    n_samples=89,
    tcia_collection_id="NSCLC_Radiogenomics",
    license="CC BY 4.0",
    mask_format="none",
    download_path=os.path.join("data", "radiomics", "D1b_nsclc_survival"),
    notes="NSCLC-Radiomics-Genomics subset, same 89 patients, survival label",
)

HNSCC_DATASET = RadiomicsDataset(
    id="D2",
    name="HNSCC (Grossmann 2017)",
    modality="CT (boyun)",
    task="HPV status / lokal kontrol",
    n_samples=215,
    tcia_collection_id="HNSCC",
    license="CC BY 4.0",
    mask_format="nii.gz",
    download_path=os.path.join("data", "radiomics", "D2_hnscc"),
    notes="TCIA: https://www.cancerimagingarchive.net/collection/head-neck-scc/",
)

LGG_DATASET = RadiomicsDataset(
    id="D3",
    name="LGG 1p/19q (TCIA)",
    modality="Multi-modal MRI",
    task="1p/19q codeletion",
    n_samples=159,
    tcia_collection_id="LGG-1p19qDeletion",
    license="CC BY 4.0",
    mask_format="nii.gz",
    download_path=os.path.join("data", "radiomics", "D3_lgg"),
    notes="TCIA: https://www.cancerimagingarchive.net/collection/lgg-1p19qdeletion/",
)

DATASETS = {
    "D1": NSCLC_DATASET,
    "D1a": NSCLC_GENOMICS_DATASET,
    "D1b": NSCLC_SURVIVAL_DATASET,
    "D2": HNSCC_DATASET,
    "D3": LGG_DATASET,
}

# D1a and D1b are the same 89 patients with different labels
DATASET_TASK_MAP = {
    "D1a": 0,
    "D1b": 1,
    "D1": 0,
}


def get_dataset(dataset_id: str) -> Optional[RadiomicsDataset]:
    return DATASETS.get(dataset_id)


def get_task_for_dataset(dataset_id: str) -> int:
    return DATASET_TASK_MAP.get(dataset_id, 0)


def load_placeholder_features(dataset_id: str, n_features: int = 500,
                              seed: int = 42):
    ds = get_dataset(dataset_id)
    if ds is None:
        raise ValueError(f"Unknown dataset: {dataset_id}")
    rng = np.random.default_rng(seed)
    X = rng.uniform(-1.0, 1.0, (ds.n_samples, n_features))
    n = ds.n_samples
    n_pos = n // 2
    y = np.zeros(n, dtype=int)
    y[:n_pos] = 1
    rng.shuffle(y)
    return X, y


def verify_tcia_access(dataset_id: str) -> bool:
    ds = get_dataset(dataset_id)
    if ds is None:
        return False
    path = ds.download_path
    os.makedirs(path, exist_ok=True)
    return os.path.isdir(path)
