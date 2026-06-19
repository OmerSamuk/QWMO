# QWMO Phase-2 Araştırma Günlüğü

**Başlangıç:** 2026-06-19
**Branch:** `feature/phase2`
**Repo:** https://github.com/OmerSamuk/QWMO/tree/feature/phase2

---

## Genel Bağlam

**QWMO (Quantum Wave-function Metaheuristic Optimizer)** araştırma projesinin Phase-2'si: Radiomics Feature Selection pilot çalışması. Hedef: Static QWMO (V1)'nin Pauli exclusion operatörünün radyomik feature selection problemlerinde nasıl cevap verdiğini test etmek.

Phase-1 sonucu (Decision C — GAPR durduruldu): `notes/04-phase1-decision.md`

---

## Gün 0 — Tasarım Lock (Aşama C)

### Tamamlanan
- `phase2_config.yaml` — `locked: true`, `locked_date: 2026-06-19`
- Tüm K1-K8 plan kararları kabul edildi (değişiklik yok)
- Peer-Review Gate `notes/phase2-design-review.md` kapatıldı
- `notes/phase2-plan.md` v1.2 FINAL olarak onaylandı

### Kod
- `core/qwmo_binary.py` — V1: Static QWMO (Orbital + Static Pauli + Escape)
- `core/qwmo_core_binary.py` — V0: Pauli-free control (Orbital + Escape)
- `baselines/random_search.py` — M0
- `baselines/ga_binary.py` — M3
- `baselines/bpso.py` — M4
- `baselines/greedy.py` — M1 (Forward Selection), M2 (Backward Selection)
- `fitness/evaluator.py` — AUC + sparsity penalty (lambda=0.01, solver=liblinear, max_iter=5000)
- `fitness/preprocessing.py` — Sızıntısız pipeline (SimpleImputer + StandardScaler + VarianceThreshold + CorrelationFilter)
- `radiomics/extract.py` — SimpleITK fallback (50 features, 3D central slice)
- `radiomics/datasets.py` — D1/D2/D3 metadata + TCIA API lookup
- `experiments/phase2_runner.py` — İlk runner (presmoke/smoke/pilot/final modları)

### VM Kurulumu
- GCloud VM: `qwmo-phase1` (n2-highcpu-16, europe-west4-a, 16 vCPU, 43 GB free disk)
- IAP tunnel confirmed
- PyRadiomics: A (CMake) → B (conda-forge) → C (SimpleITK) — tümü başarısız
- SimpleITK + scikit-learn kuruldu
- `tcia-utils` v3.3.1 kuruldu

### TCIA Keşfi
- NSCLC-Radiomics (33 GB, 422 hasta, CT+SEG) → D1a/D1b için yeterli, API download yavaş
- D2 (HNSCC Grossmann 2017) ve D3 (LGG 1p/19q) TCIA'da bulunamadı

---

## Gün 1 — PyRadiomics ve Pre-smoke

### Kritik Kararlar
| Karar | Seçim | Gerekçe |
|---|---|---|
| PyRadiomics stratejisi | C (SimpleITK fallback) | versioneer/build chain başarısız |
| Pilot p-levels | [100, 250, full] | timing: 50 çok hızlı, ek bilgi yok |
| Outer CV stratejisi | C — StratifiedKFold 5×1 | charter §12 |
| TCIA download | C — ertelendi | API yavaş, placeholder yeterli |
| Placeholder veri | random placeholder | gerçek veri pilot onayı sonrası |

### Pre-smoke Testi
- 80/80 runs complete, 31 min wall-clock
- Pre-smoke timing: p=100 avg 12.5s/run, p=full avg 34.7s/run
- 1 FE ≈ 0.0125s (p=100) / 0.0347s (p=full)
- Pilot tahmini: 4,200 runs ÷ 16 workers ≈ 1.7h
- Tüm import/smoke testleri geçti

### Özel Notlar
- Review bulgusu #1 (sparsity penalty) — düzeltildi, charter uyumlu
- Review bulgusu #2 (solver) — düzeltildi, liblinear + max_iter=5000
- Review bulgusu #3 (ranked subspace) — Gün 2'de düzeltildi
- `feature/phase2` branch pushed: https://github.com/OmerSamuk/QWMO/tree/feature/phase2

---

## Gün 2 — Preprocessing Audit

**Tarih:** 2026-06-19
**Soru-Cevap:** Q1=B, Q2=B (partial — sadece smoke/pilot), Q3=B, Q4=A (bugün dur)

### Değişen Dosyalar

| Dosya | Değişiklik |
|---|---|
| `radiomics/datasets.py` | D1a_NSCLC_genes (EGFR), D1b_NSCLC_survival (2-year) eklendi |
| `radiomics/datasets.py` | `load_placeholder_features()`, `get_task_for_dataset()` eklendi |
| `fitness/evaluator.py` | `evaluate_on_outer()` eklendi (sızıntısız outer değerlendirme) |
| `experiments/phase2_runner.py` | Major refactor (detay aşağıda) |
| `notes/phase2-preprocessing-audit.md` | Yeni audit raporu |

### Runner Refactor Detayı

1. **`decode_mask()`** — method-aware mask decoding:
   - M1_forward / M2_backward → direkt binary mask (greedy çıktısı)
   - Diğer tüm methodlar → `sigmoid(p > 0.5)` (latent continuous)

2. **`_run_nested_cv()`** — outer CV implementasyonu:
   - StratifiedKFold outer loop
   - Preprocessing fit on train / transform on test
   - ANOVA F-test (`f_classif`) for ranked subspace
   - Inner CV (FitnessEvaluator) için optimizer
   - Sızıntısız outer AUC değerlendirme

3. **Pilot matrix güncellendi:**
   - datasets: D1a, D1b (NSCLC-Radiomics-Genomics, 89 hasta)
   - p_levels: [100, 250, full] (plan §14)
   - methods: M0_random, M1_forward, M2_backward, M3_GA, M4_BPSO, V0_core_binary, V1_static_qwmo
   - seeds: 0..9
   - outer_cv_folds: 5, outer_cv_repeats: 1
   - inner_cv_folds: 3
   - **Toplam: 2 × 2 × 3 × 7 × 10 × 5 = 4,200 evaluations**

4. **Diğer düzeltmeler:**
   - `_get_optimizer` artık max_fes (fitness_budget) doğru geçiyor
   - M1_forward ve M2_backward için optimizer eklendi
   - Eksik `y` argümanı `preprocess_train()` çağrısına eklendi

### Doğrulama Testleri

| Test | Durum | Detay |
|---|---|---|
| Preprocessing leakage | PASS | 5-fold, train/test mean diff = 0.20 >> 0.01 |
| Mask decoding | PASS | M0/M1/M2/M3 doğru decode |
| FitnessEvaluator | PASS | inner fitness + outer AUC + zero mask |
| Nested CV (5 method) | PASS | M0/M1/M3/M4/V1, 2+2 fold, budget=200 |
| Sequential smoke (10 run) | PASS | 20 folds, ~2.5s/run avg |

### Pilot Süre Tahmini
- Kombinasyon başına: ~32s (budget=1000, 5 fold)
- 840 kombinasyon × 32s / 16 worker ≈ 28 dakika (VM'de)

### Bilinen Sorunlar

| Sorun | Durum | Çözüm |
|---|---|---|
| Windows ProcessPoolExecutor crash | Açık | Linux VM'de çalışır, sequential fallback mevcut |
| PyRadiomics build | Çözüldü | SimpleITK fallback |
| D2/D3 TCIA'da yok | Ertelendi | Post-pilot |
| Placeholder ANOVA anlamsız | Ertelendi | Gerçek veri pilot onayı sonrası |

### Git
- Commit: `d5cd8cf` — "Gün 2 — Preprocessing audit: outer CV, ranked ANOVA, leakage-free pipeline, mask decoding"
- Push: `feature/phase2` branch

---

## Pilot Matris (Plan)

```
2 dataset (D1a, D1b)
× 2 subspace (ranked, random)
× 3 p-level (100, 250, full)
× 7 method (M0..M4 + V0 + V1)
× 10 seed (0..9)
× 5 outer fold
= 4,200 evaluations
```

**VM tahmini:** 28 dakika (16 worker, budget=1000)
**Analiz:** Wilcoxon signed-rank (p<0.05) + Holm correction + Cliff's delta

---

## Sırada (Gün 3+)

| Gün | Başlık | Süre |
|---|---|---|
| Gün 3 | Full baseline smoke (9 method, 3 seed, tüm p) | ~1h |
| Gün 4 | Optimizer integration audit | ~2h |
| Gün 5-7 | Pilot (4,200 runs) | ~28dk VM |
| Gün 8 | Pilot Go/No-Go (Wilcoxon + Holm + Cliff's) | ~2h |

---

## Referans Dosyalar

- `notes/phase2-plan.md` — Governing plan v1.2 FINAL
- `notes/phase2-design-review.md` — Peer-Review Gate (kapalı)
- `notes/phase2-preprocessing-audit.md` — Gün 2 audit raporu
- `charters/radiomics-landscape.md` — Locked charter v2.2
- `phase2_config.yaml` — Locked config
- `experiments/phase2_runner.py` — Ana runner
- `fitness/evaluator.py` — Fitness evaluator + outer evaluation
- `fitness/preprocessing.py` — Sızıntısız preprocessing
- `radiomics/datasets.py` — Dataset metadata + placeholder loader
- `core/qwmo_binary.py` — V1 Static QWMO
- `core/qwmo_core_binary.py` — V0 Pauli-free control

---

*Gün 2 sonu — 2026-06-19. VM durduruldu.*

## Related Notes

- [[00-index|Vault Index]]
- [[notes/08-phase2-charter.md|Phase2 charter]]
- [[notes/phase2-design-review.md|Phase2 design review]]
- [[notes/phase2-plan.md|Phase2 plan]]
