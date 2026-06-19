# Phase-2 Design Review — Peer-Review Gate (Gün 0, Aşama A)

> **Plan:** [[phase2-plan|Faz-2 Uygulama Planı v1.2]] §2 Gün 0
> **Charter:** [[../charters/radiomics-landscape|Faz-2 Radiomics Landscape & Pauli Response Pilot v2.2]] (LOCKED)
> **Durum:** Taslak — doldurulacak

---

## A. Tasarım İncelemesi

### A.1 Dataset Teklifi Onayı

| #  | Dataset | Modalite | Binary Task | n | Seçim |
|----|---------|----------|-------------|---|-------|
| D1 | NSCLC Radiogenomics (TCIA) | CT (toraks) | 2-yıl survival / EGFR mut | ~211 |  |
| D2 | HNSCC (TCIA, Grossmann 2017) | CT (boyun) | HPV status / lokal kontrol | ~215 |  |
| D3 | LGG 1p/19q (TCIA) | Multi-modal MRI | 1p/19q codeletion | ~159 |  |

**Karar:** [D1 / D2 / D3]

### A.2 TCIA Erişim Doğrulaması

- **Collection URL:** [URL girilecek]
- **Lisans:** [Creative Commons / etc.]
- **Mask formatı:** [nrrd / nii.gz / DICOM SEG / etc.]
- **İndirme yöntemi:** [NBIA Data Retriever / CLI / tar.gz]
- **Erişim tarihi:** [GG.AA.YYYY]

### A.3 PyRadiomics 3.x Uyumluluk

- **Input gereksinimi:** DICOM + RTSTRUCT / nii.gz + mask
- **Feature class'lar:** firstorder, shape, glcm, glrlm, glszm, ngtdm, gldm
- **Versiyon:** [PyRadiomics sürümü]

---

## B. Pre-Smoke [K3]

### B.1 Matris

| Parametre | Değer |
|-----------|-------|
| Dataset | D1 |
| Subspace regimes | ranked, random |
| p-levels | 100, full |
| Methods | M0_random, M3_GA, M4_BPSO, V1_static_qwmo |
| Seeds | [0,1,2,3,4] |
| Fitness budget | 1000 FE |
| Outer CV | 5 folds x 2 repeats |
| Inner CV | 3 folds |

### B.2 Ölçümler

- [ ] 1 FE süresi
- [ ] 1 run süresi
- [ ] dataset x p x method x seed süresi
- [ ] Bellek kullanımı

### B.3 Çıktılar

- [ ] `phase2_presmoke_timing.csv`
- [ ] `phase2_presmoke_report.md`

---

## C. Onay

- [ ] Pre-smoke sürelerine göre ölçeklenmiş pilot matris
- [ ] Pre-smoke sürelerine göre ölçeklenmiş final matris
- [ ] `phase2_config.yaml` kilitlendi

**Pilot tavanı:** `2 dataset x 2 subspace x 4 p x 7 method x 10 seed x 5x2 fold x 1000 FE`

**Final tavanı:** `3 dataset x 2 subspace x 6 p x 7 method x 30 seed x 5x3 fold x 3000 FE`

---

## D. GCloud VM Kurulumu

| Parametre | Değer |
|-----------|-------|
| Makine tipi | `n2-highmem-32` |
| Preemptible | [Evet / Hayır] |
| Bölge | [us-central1 / europe-west4] |
| Disk | [SSD boyutu] |
| Image | [Ubuntu 22.04 / 24.04] |
| Python | [3.10 / 3.11] |
| GCloud SDK kurulumu | [tarih] |

---

## İmza

- **Tarih:**
- **Onaylayan:**
- **Dataset kararı:**

## Related Notes

- [[00-index|Vault Index]]
- [[notes/08-phase2-charter.md|Phase2 charter]]
- [[notes/phase2-plan.md|Phase2 plan]]
