---
tags: [phase2, datasets, evaluation, candidates]
---

# Phase-2 Radiomics Dataset Candidates — Structured Evaluation

> **Date**: 2026-06-20
> **Purpose**: Evaluate candidate radiomics datasets for Phase-2 QWMO binary feature-selection study.
> **Method**: Web fetches from Synapse, TCIA, grand-challenge.org, GitHub.

## Requirements (Charter §10)

- n_samples ≥ 50 (pref > 100)
- n_features ≥ 100 (pref ≥ 500)
- Binary outcome
- Mask available (PyRadiomics-compatible)
- License: CC BY 4.0-class open access
- 3 different modalities/anatomical regions preferred

## Candidates Evaluated

### 1. BraTS 2021 (syn53708249)

- **n_samples**: 1251 (challenge training); 199 TCGA-LGG subset on TCIA
- **Modality**: Multi-modal MRI (T1, T1ce, T2, FLAIR) — 4 channels
- **Mask**: Native .nii.gz (3 sub-regions; aggregate to WT/ET/TC)
- **Binary task**: HGG vs LGG, or 1p/19q codeletion (TCGA-LGG subset)
- **License**: Synapse DUO (registration required); some CC BY derivatives via TCIA
- **Access**: synapse.org + DUO e-sig; 2–7 days
- **PyRadiomics**: High (native .nii.gz)
- **Size**: 10–30 GB
- **Class imbalance**: ~4.4:1 HGG:LGG
- **Pre-extracted CSV**: No
- **Fit: 4 / Practical: 3 / Total: 7**

### 2. HNSCC-Head-Neck-Radiomics-HN1 (TCIA)

- **n_samples**: 215 (Head-Neck-CT-Atlas) or 412 (Oropharyngeal-Radiomics-Outcomes)
- **Modality**: CT + RTSTRUCT (+ PET subset)
- **Mask**: RTSTRUCT DICOM (TG-263 named GTVp/GTVn)
- **Binary task**: HPV status, local control at 2y
- **License**: NIH Controlled Access (images); CC BY 4.0 (clinical CSV)
- **Access**: TCIA Data Retriever; 1–3 days
- **PyRadiomics**: Medium (RTSTRUCT needs converter: dicomrtstruct2nifti)
- **Size**: 55 GB (OPC subset)
- **Class imbalance**: ~4:1 HPV+ (OPC)
- **Pre-extracted CSV**: No
- **Fit: 4 / Practical: 4 / Total: 8** ⭐ already D2 in Phase-2 plan

### 3. OPC-Radiomics (Aerts Lab)

- **GitHub URL**: 404 — repo not found at `qurit/OPC-Radiomics` or `AertsLab/OPC-Radiomics`
- **Status**: **DISQUALIFIED** — likely confusion with Aerts 2014 Lung1 (NSCLC, not OPC)
- **Note**: The OPC HPV dataset is the OPC sub-cohort inside TCIA HNSCC collection (412 patients, already candidate #2)

### 4. NSCLC-Radiogenomics (TCIA)

- **n_samples**: 211
- **Modality**: CT (+ PET subset) + DICOM SEG
- **Mask**: DICOM SEG + AIM XML annotations
- **Binary task**: EGFR mutation (23% mutant), 2y survival
- **License**: CC BY 3.0 (images, AIM, clinical CSV)
- **Access**: TCIA Data Retriever, auto-approved; <1 day
- **PyRadiomics**: High (DICOM SEG native support since v3.0)
- **Size**: 98 GB
- **Class imbalance**: ~3.3:1 EGFR+ (acceptable)
- **Pre-extracted CSV**: No (Aerts 2014 Lung1 has features but is a different 422-patient subset)
- **Fit: 4 / Practical: 5 / Total: 9** ⭐ already D1 in Phase-2 plan

### 5. PI-CAI (Prostate MRI)

- **n_samples**: 1500 (public) + 7607 (sequestered, inaccessible)
- **Modality**: bpMRI — axial T2W + DWI + ADC (+ optional sag/cor T2W)
- **Mask**: .mha (MetaImage) + voxel csPCa lesion delineations
- **Binary task**: csPCa detection (ISUP ≥ 2 vs < 2)
- **License**: **CC BY-NC 4.0** ⚠️ non-commercial
- **Access**: grand-challenge.org + Zenodo (DOI 10.5281/zenodo.6624726); <1 day
- **PyRadiomics**: High (.mha supported)
- **Size**: ~150 GB
- **Class imbalance**: ~3.6:1
- **Pre-extracted CSV**: No (annotations only)
- **Fit: 5 / Practical: 5 / Total: 10** ⚠️ **DISQUALIFIED BY LICENSE** for journal publication

### 6. WORC Database (MStarmans91/WORCDatabase)

- **n_samples**: 932 across 8 datasets:
  - Lipo (~105), Desmoid (~203), Liver (186), GIST (~248), CRLM (~77), Melanoma (~93), Head&Neck (~402 from HN1), Glioma (~163)
- **Modality**: **CT + MRI**, multiple anatomical regions (liver, HN, brain, soft tissue, etc.)
- **Mask**: DICOM SEG / NIfTI on XNAT (`xnat.health-ri.nl/data/projects/worc`)
- **Binary task**: Per-dataset — desmoid recurrence, lipoma vs liposarcoma, GIST risk, CRLM resection, melanoma metastases, HN1 T-stage, **glioma HGG vs LGG**
- **License**: Open via Health-RI XNAT; code Apache 2.0
- **Access**: XNAT registration (auto-approved); 1–5 days
- **PyRadiomics**: **Pre-extracted 546 features per lesion** (PyRadiomics 71 + PREDICT 493) ✅
- **Size**: 50–80 GB raw; few MB pre-extracted CSVs
- **Class imbalance**: Per-dataset, mostly 2:1 to 4:1
- **Pre-extracted CSV**: **✅ YES — full 546-feature CSVs in `features/` folder**
- **Pre-defined CV splits**: **✅ 100× random splits in `crossvalidationsplits/` (leakage-free ready)**
- **Fit: 5 / Practical: 5 / Total: 10** ⭐ **RECOMMENDED #1**

## Cross-Cutting Notes

### Multi-modality diversity (Charter §10)
- **WORC**: CT + MRI across 3+ regions ✅
- **TCIA combo** (NSCLC + HNSCC + TCGA-LGG): CT + CT + MRI = 3 regions ✅
- **BraTS** alone: single-region multi-channel MRI ❌
- **PI-CAI** alone: single-region multi-channel MRI ❌

### Pre-extracted CSV
| Dataset | Pre-extracted CSV |
|---|---|
| BraTS 2021 | No |
| HNSCC | No |
| OPC-Radiomics | n/a |
| NSCLC-Radiogenomics | No (Lung1 has, different subset) |
| PI-CAI | No (annotations only) |
| **WORC** | **✅ YES — 546 features/lesion** |

### License / commercial-use compatibility
| Dataset | License | Commercial OK? |
|---|---|---|
| BraTS 2021 | Synapse DUO | Restricted |
| HNSCC | NIH Controlled + CC BY | Academic mostly OK |
| NSCLC-Radiogenomics | CC BY 3.0 | **Yes** |
| PI-CAI | **CC BY-NC 4.0** | **NO** |
| WORC | Open (XNAT) + Apache 2.0 | **Yes** |

## Final Ranking

| # | Candidate | Fit | Practical | Total | Notes |
|---|---|---|---|---|---|
| 1 | **WORC Database** | 5 | 5 | **10** | Pre-extracted 546 features, 8 datasets, CT+MRI, Apache 2.0 |
| 2 | **NSCLC-Radiogenomics** | 4 | 5 | **9** | Already D1 in Phase-2 plan; CC BY 3.0 |
| 3 | **HNSCC-OPC subset** | 4 | 4 | **8** | Already D2 in Phase-2 plan; CC BY 4.0 |
| 4 | **BraTS 2021** | 4 | 3 | **7** | Synapse DUO friction; multi-channel design decision |
| 5 | **PI-CAI** | 5 | 5 | 10 | **Disqualified by CC BY-NC 4.0** |
| 6 | **OPC-Radiomics** | — | — | — | **Disqualified — repo 404** |

## Top-3 Recommendation

1. **WORC Database** — pick 3 datasets for 3 modalities/regions:
   - Glioma (MRI, HGG-vs-LGG)
   - Liver (CT, malignancy)
   - HN1 (CT, T-stage)
2. **NSCLC-Radiogenomics** (D1, existing)
3. **HNSCC-OPC subset** (D2, existing)

**Strong alternative**: replace D3 (TCGA-LGG) with WORC-Glioma to gain MRI diversity, pre-extracted features, and pre-defined CV splits.

## Related Notes

- [[phase2-plan|Phase-2 Plan v1.2]]
- [[../charters/radiomics-landscape|Faz-2 Radiomics Landscape Charter v2.2]]