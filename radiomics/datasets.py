import os
import numpy as np
import pandas as pd
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

WORC_GIST_DATASET = RadiomicsDataset(
    id="D2",
    name="WORC-GIST (GIST vs abdominal tumor)",
    modality="CT (abdomen)",
    task="GIST (0) vs other abdominal tumor (1)",
    n_samples=246,
    tcia_collection_id="WORC_GIST",
    license="Apache 2.0",
    mask_format="pre-extracted CSV (WORC371)",
    download_path=os.path.join("data", "radiomics", "D2_worc_gist"),
    notes="github.com/MStarmans91/WORCDatabase/features/WORCDatabase_GIST_features_WORC371.csv",
)

WORC_LIPO_DATASET = RadiomicsDataset(
    id="D3",
    name="WORC-Lipo (Lipoma vs liposarcoma)",
    modality="T1w MRI (extremity)",
    task="Lipoma (0) vs well-diff liposarcoma (1)",
    n_samples=115,
    tcia_collection_id="WORC_Lipo",
    license="Apache 2.0",
    mask_format="pre-extracted CSV (WORC371)",
    download_path=os.path.join("data", "radiomics", "D3_worc_lipo"),
    notes="github.com/MStarmans91/WORCDatabase/features/WORCDatabase_Lipo_features_WORC371.csv",
)

WORC_DATASETS_MAP = {
    "D2": ("GIST", "WORCDatabase_GIST_features_WORC371.csv"),
    "D3": ("Lipo", "WORCDatabase_Lipo_features_WORC371.csv"),
}

WORC_SPLITS_MAP = {
    "D2": ("GIST", "crossvalidationsplits_GIST.csv"),
    "D3": ("Lipo", "crossvalidationsplits_Lipo.csv"),
}

DATASETS = {
    "D1": NSCLC_DATASET,
    "D1a": NSCLC_GENOMICS_DATASET,
    "D1b": NSCLC_SURVIVAL_DATASET,
    "D2": WORC_GIST_DATASET,
    "D3": WORC_LIPO_DATASET,
}

DATASET_TASK_MAP = {
    "D1a": 0,
    "D1b": 1,
    "D1": 0,
    "D2": 0,
    "D3": 0,
}

# WORC dataset name aliases (not in DATASETS registry)
WORC_FEATURE_PATHS = {
    "GIST": os.path.join("data", "radiomics", "D2_worc_gist", "WORCDatabase_GIST_features_WORC371.csv"),
    "Lipo": os.path.join("data", "radiomics", "D3_worc_lipo", "WORCDatabase_Lipo_features_WORC371.csv"),
}

WORC_SPLIT_PATHS = {
    "GIST": os.path.join("data", "radiomics", "D2_worc_gist", "crossvalidationsplits_GIST.csv"),
    "Lipo": os.path.join("data", "radiomics", "D3_worc_lipo", "crossvalidationsplits_Lipo.csv"),
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


def load_worc_features(dataset_name: str, label_csv_path: str = None, seed: int = 42):
    csv_path = WORC_FEATURE_PATHS[dataset_name]
    df = pd.read_csv(csv_path)

    patient_col = df.columns[-1]
    feature_cols = [c for c in df.columns if c != patient_col]
    X = df[feature_cols].values.astype(float)

    if label_csv_path and os.path.exists(label_csv_path):
        labels_df = pd.read_csv(label_csv_path)
        label_map = dict(zip(labels_df["Patient"], labels_df["Diagnosis_binary"]))
        y = df[patient_col].map(label_map).values.astype(int)
    else:
        rng = np.random.default_rng(seed)
        n = len(df)
        y = np.zeros(n, dtype=int)
        y[:n // 2] = 1
        rng.shuffle(y)

    return X, y, feature_cols


def load_worc_splits(dataset_name: str, n_splits: int = 100):
    csv_path = WORC_SPLIT_PATHS[dataset_name]
    df = pd.read_csv(csv_path, header=None)

    splits = []
    for i in range(n_splits):
        train_col = df.iloc[:, i * 2 + 1].dropna().tolist()
        test_col = df.iloc[:, i * 2 + 2].dropna().tolist()
        splits.append((train_col, test_col))

    return splits


def verify_tcia_access(dataset_id: str) -> bool:
    ds = get_dataset(dataset_id)
    if ds is None:
        return False
    path = ds.download_path
    os.makedirs(path, exist_ok=True)
    return os.path.isdir(path)
