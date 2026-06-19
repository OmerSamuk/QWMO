import os
from dataclasses import dataclass, field
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
    "D2": HNSCC_DATASET,
    "D3": LGG_DATASET,
}


def get_dataset(dataset_id: str) -> Optional[RadiomicsDataset]:
    return DATASETS.get(dataset_id)


def verify_tcia_access(dataset_id: str) -> bool:
    ds = get_dataset(dataset_id)
    if ds is None:
        return False
    # TODO: implement actual TCIA access check (NBIA Data Retriever / curl)
    # For now, placeholder:
    path = ds.download_path
    os.makedirs(path, exist_ok=True)
    return os.path.isdir(path)
