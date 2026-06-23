# Phase-2 Design Review — Peer-Review Gate (Gün 0, Aşama A + C)

> **Plan:** [[phase2-plan|Faz-2 Uygulama Planı v1.3]] §2 Gün 0
> **Charter:** [[../charters/radiomics-landscape|Faz-2 Radiomics Landscape & Pauli Response Pilot v2.2]] (LOCKED) + [[../charters/radiomics-landscape-amendment-1|Amendment 1]]
> **Durum:** ✅ GÜNCELLENDİ — 2026-06-20 (Amendment 1 ile senkron)

---

## A. Tasarım İncelemesi

### A.1 Dataset Teklifi Onayı (Amendment 1 ile güncellendi)

| #  | Dataset | Modalite | Binary Task | n | Seçim |
|----|---------|----------|-------------|---|-------|
| D1 | NSCLC Radiogenomics (TCIA) | CT (toraks) | 2-yıl survival / EGFR mut | ~211 | ⏳ **final** (PyRadiomics extraction) |
| D2 | WORC-GIST (GitHub, pre-CSV) | CT (abdomen) | GIST vs other | 246 | ✅ **presmoke + pilot + final** |
| D3 | WORC-Lipo (GitHub, pre-CSV) | T1w MRI (extremite) | Lipoma vs liposarcoma | 115 | ✅ **pilot + final** |

**Karar:** Pilot = D2 + D3; Final = D1 + D2 + D3 (D1 extraction yapılırsa)

### A.2 Veri Erişim Doğrulaması (WORC swap)

- **D1 (NSCLC):** TCIA — NBIA Data Retriever CLI ile indirilecek (CC BY 4.0)
- **D2 (WORC-GIST):** GitHub CSV — `https://github.com/DIAGNijmegen/worc-data/raw/main/...`
- **D3 (WORC-Lipo):** GitHub CSV — aynı worc-data deposu
- **WORC lisans:** Apache 2.0
- **WORC etiketler:** XNAT Health-RI `https://xnat.health-ri.nl` — registration required

### A.3 Feature Extraction

- **D1:** PyRadiomics 3.x (nii.gz + mask) — TCIA'dan indirme bekleniyor
- **D2/D3:** Pre-extracted CSV (564 features) — WORC GitHub'dan hazır
- **PyRadiomics versiyon:** — (build başarısız oldu, conda-forge ile tekrar denenecek)
- **WORC feature format:** PREDICT/original prefix, single-lesion (multi-lesion yok)

---

## B. Pre-Smoke [K3] ✅ COMPLETE

### B.1 Matris (Amendment 1 — D2)

| Parametre | Değer |
|-----------|-------|
| Dataset | D2 (WORC-GIST, pre-extracted CSV) |
| Subspace regimes | ranked, random |
| p-levels | 100, full |
| Methods | M0_random, M3_GA, M4_BPSO, V1_static_qwmo |
| Seeds | [0,1,2,3,4] |
| Fitness budget | 1000 FE |
| Outer CV | Yok (timing amaçlı placeholder) |
| Inner CV | 3 folds |

### B.2 Ölçümler (Özet)

- **p=100:** 10-14s/run, avg 12.5s
- **p=full:** 30-48s/run, avg 34.7s
- **1 FE süresi (p=100):** 0.0125s
- **1 FE süresi (p=full):** 0.0347s
- **Toplam:** 80 run, 1,878s (**31.3 dakika**)
- **Bellek:** 16 GB RAM yeterli

Detaylı rapor: `[[../results/phase2/phase2_presmoke_report.md]]`

### B.3 Çıktılar

- ✅ `phase2_presmoke_timing.csv`
- ✅ `phase2_presmoke_report.md`
- ✅ `phase2_presmoke_results_raw.csv`

---

## C. Onay ✅ VERİLDİ

- ✅ Pre-smoke sürelerine göre ölçeklenmiş pilot matris
- ⏳ Final matrisi pilot sonrası (charter §31-33 karar eşikleri bekleniyor)
- ✅ `phase2_config.yaml` kilitlendi (locked: true)

| Parametre | Pilot tavanı (Plan §4) | Pilot (ölçeklenmiş) |
|-----------|----------------------|----------------------|
| Dataset | 2 | **D2 + D3** |
| Subspace | 2 | ranked, random |
| p-level | 4 | **100, 250, full** (50 çıktı) |
| Method | 7 | M0, M1, M2, M3, M4, V0, V1 |
| Seed | 10 | 10 (V0 dahil) |
| Outer CV | 5×2 | **5×1** (repeat 1) |
| Inner CV | 3 | 3 |
| FE | 1000 | 1000 |
| **Toplam** | 5,600 inner-run | **4,200 inner-run** (↓25%) |

---

## D. GCloud VM Kurulumu ✅ DONE

| Parametre | Değer |
|-----------|-------|
| Makine | `qwmo-phase1` (n2-highcpu-16) |
| Bölge | europe-west4-a |
| OS | Ubuntu 22.04 |
| Python | 3.10.12 |
| Workers | 8 (ProcessPoolExecutor) |
| Bağlantı | IAP tunnel (gcloud compute ssh --tunnel-through-iap) |

---

## İmza

- **Tarih:** 2026-06-20 (Amendment 1 ile güncellendi)
- **Onaylayan:** Pre-smoke sonuçları + subagent audit + kullanıcı onayı
- **Dataset kararı:** D2 + D3 (pilot), D1 + D2 + D3 (final)

## Related Notes

- [[00-index|Vault Index]]
- [[notes/08-phase2-charter.md|Phase2 charter]]
- [[notes/phase2-plan.md|Phase2 plan]]
