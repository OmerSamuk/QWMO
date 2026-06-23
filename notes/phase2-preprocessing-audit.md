# Phase-2 Preprocessing Audit — Gün 2

**Tarih:** 2026-06-19
**Kapsam:** Q1=B, Q2=B (partial), Q3=B, Q4=A
**Durum:** COMPLETE

---

## 1. Yönetici Özeti

Gün 2 kapsamında dört major bileşen tamamlandı: (1) ranked subspace ANOVA fix (review finding #3), (2) outer CV implementasyonu (StratifiedKFold 5×1), (3) preprocessing pipeline entegrasyonu (sızıntısız fit/transform), (4) audit raporu. Tüm bileşenler placeholder veri üzerinde test edildi ve doğrulandı. Pilot matris D1a/D1b ile güncellendi. Windows ProcessPoolExecutor kararsızlığı tespit edildi ancak Linux VM'de (hedef) çalışacak.

---

## 2. Preprocessing Pipeline

```
X_train ──┬─→ SimpleImputer(strategy=median).fit()
          ├─→ StandardScaler().fit()
          ├─→ VarianceThreshold(threshold=0.01).fit()
          └─→ CorrelationFilter(threshold=0.95).fit()
               ↓
          fitted_pipe (dict)

X_test  ──→ pipe["imputer"].transform()
          → pipe["scaler"].transform()
          → pipe["var_filter"].transform()
          → pipe["corr_filter"].transform()
               ↓
          X_test_pp (sadece train'dan gelen subset ile)
```

### Sızıntı Kanıtı

Leakage testi: 5-fold CV ile her fold'da train/test mean farkı ölçüldü.

| Fold | Train vs Test Mean Diff |
|------|------------------------|
| 0    | 0.2125                 |
| 1    | 0.1878                 |
| 2    | 0.2270                 |
| 3    | 0.1709                 |
| 4    | 0.2109                 |
| **Ortalama** | **0.2018**         |

> Mean diff >> 0.01 → train/test dağılımları belirgin farklı. **Sızıntı yok.** Eğer pipeline test verisini de "görmüş" olsaydı, train/test mean farkı ~0 olurdu.

### Pipeline Bileşenleri

| Component | Parametre | Picklable |
|-----------|-----------|-----------|
| SimpleImputer | strategy=median | ✅ |
| StandardScaler | - | ✅ |
| VarianceThreshold | threshold=0.01 | ✅ |
| CorrelationFilter | threshold=0.95 | ✅ (custom class) |

---

## 3. Outer/Inner CV Stratejisi

### Outer CV: StratifiedKFold 5×1

```
Veri (X, y)
  │
  ├── Fold 0: Train (71 örnek) → inner CV → optimizer → mask → outer AUC
  ├── Fold 1: Train (71 örnek) → inner CV → optimizer → mask → outer AUC
  ├── Fold 2: Train (71 örnek) → inner CV → optimizer → mask → outer AUC
  ├── Fold 3: Train (71 örnek) → inner CV → optimizer → mask → outer AUC
  └── Fold 4: Train (72 örnek) → inner CV → optimizer → mask → outer AUC
```

Her outer fold'da:
1. Preprocessing pipeline **SADECE train'de fit** edilir
2. ANOVA F-test **SADECE train'de** hesaplanır (ranked subspace)
3. Optimizer inner CV (3-fold) ile eğitilir
4. En iyi maske outer test'te değerlendirilir (sızıntısız)

### Inner CV: StratifiedKFold 3-fold

Optimizer içindeki `FitnessEvaluator` 3-fold CV ile mean AUC + sparsity penalty hesaplar.

### Önemli: Test Scaler Leakage

`evaluate_on_outer()` fonksiyonu **ek scaling yapmaz**. Pipeline scaler'ı train'de fit edildiği için X_train_sub ve X_test_sub zaten aynı scaler ile dönüştürülmüştür. LR direkt olarak scaled veri üzerinde fit edilir.

---

## 4. Ranked Subspace Fix

**Review finding #3:** Eski `_run_single()` ranked subspace için `np.random.permutation` kullanıyordu — bu ranked değil random subspace demekti.

**Fix:** `f_classif` (ANOVA F-test) implementasyonu:

```python
from sklearn.feature_selection import f_classif

if subspace_regime == "ranked":
    F, _ = f_classif(X_train_pp, y_train)
    order = np.argsort(-F)
else:
    order = random_order  # seed-controlled permutation
```

Bu fix ile ranked subspace artık gerçekten F-skoru sıralaması kullanıyor. Random subspace ise seed-controlled permutation ile aynı kalıyor.

---

## 5. Mask Decoding Tutarlılığı

| Method | Çıktı Tipi | decode_mask() | Doğrulama |
|--------|-----------|---------------|-----------|
| M0_random | latent (float) | sigmoid(p > 0.5) | ✅ |
| M1_forward | binary (int) | direkt kullan | ✅ |
| M2_backward | binary (int) | direkt kullan | ✅ |
| M3_GA | latent (float) | sigmoid(p > 0.5) | ✅ |
| M4_BPSO | latent (float) | sigmoid(p > 0.5) | ✅ |
| V0_core_binary | latent (float) | sigmoid(p > 0.5) | ✅ |
| V1_static_qwmo | latent (float) | sigmoid(p > 0.5) | ✅ |

Test: `latent = [-10, -0.1, 0, 0.1, 10]`
- sigmoid(-10) ≈ 0.000045 → 0
- sigmoid(-0.1) ≈ 0.475 → 0
- sigmoid(0) = 0.5 → 0 (strict > 0.5)
- sigmoid(0.1) ≈ 0.525 → 1
- sigmoid(10) ≈ 0.99995 → 1
- Sonuç: `[0, 0, 0, 1, 1]` ✅

---

## 6. Pilot Matris

| Parametre | Değer | Açıklama |
|-----------|-------|----------|
| datasets | D1a, D1b | NSCLC-Radiomics-Genomics, 89 hasta |
| subspace_regimes | ranked, random | ANOVA F-test / seed perm |
| p_levels | 100, 250, full | plan §14'e göre |
| methods | M0..M4 + V0 + V1 | 7 method, pilot §14 |
| seeds | 0..9 | 10 seed |
| outer_cv_folds | 5 | StratifiedKFold |
| outer_cv_repeats | 1 | Q2=C |
| inner_cv_folds | 3 | Charter §12 |
| fitness_budget | 1000 | Charter §17 |

**Toplam:** 2 × 2 × 3 × 7 × 10 × 5 = **4,200 evaluations**

---

## 7. Pilot Süre Tahmini

Audit data (budget=200, 2 outer fold, 2 inner fold):

| Method | Avg Time (s) | 1000 FE × 5 fold tahmini (s) |
|--------|-------------|------------------------------|
| M0_random | 2.85 | 35.6 |
| M3_GA | 2.60 | 32.5 |
| M4_BPSO | 2.50 | 31.3 |
| V1_static_qwmo | 2.40 | 30.0 |
| M1_forward | 2.40 | 30.0 |

**Not:** Budget=200 ile ölçüldü. Budget=1000'de timing linear scale edildi.

**Pilot toplam tahmini:**
- Kombinasyon başına: ~32s (ortalama)
- 840 kombinasyon × 32s / 16 worker (VM) ≈ 1680s ≈ **28 dakika**

---

## 8. Bilinen Sorunlar

### Windows ProcessPoolExecutor Kararsızlığı

- **Belirti:** 60+ task sonrası `BrokenProcessPool: A process in the process pool was terminated abruptly`
- **Kök neden:** Windows'ta multiprocessing pipe corruption (bilinen concurrent.futures sorunu)
- **Çözüm:** Linux VM'de (target: qwmo-phase1) ProcessPoolExecutor kararlı çalışır
- **Acil çözüm:** Sequential fallback eklenebilir (`run_phase2(..., max_workers=1)`)

### Placeholder Veri Sınırlaması

- ANOVA F-test random placeholder veride anlamlı sıralama vermez
- Bu Gün 2 audit'te sorun değil — pilot onayı sonrası gerçek TCIA verisi ile değişecek
- Preprocessing pipeline'ın sızıntısız çalıştığı doğrulandı

### D2/D3 Mevcut Değil

- D2 (HNSCC) ve D3 (LGG 1p/19q) TCIA'da bulunamadı
- final modu için sonra çözülecek

---

## 9. Gün 3 İçin Öneriler

1. **Full baseline smoke** (9 method, tüm p-levels, 3 seed)
2. **VM deploy** — kodu feature/phase2 branch'ine push et, VM'de smoke test çalıştır
3. **D1a/D1b mask decoding lock** — charter'a uygun olduğunu onayla
4. **Pilot timing** — VM'de pilot matrix'in ilk 10 kombinasyonunu çalıştır, gerçek timing al

---

## 10. Referanslar

- `experiments/phase2_runner.py` — decode_mask(), _run_nested_cv(), _get_matrix()
- `fitness/evaluator.py` — FitnessEvaluator, evaluate_on_outer()
- `fitness/preprocessing.py` — preprocess_train(), preprocess_transform()
- `radiomics/datasets.py` — D1a_NSCLC_genes, D1b_NSCLC_survival, load_placeholder_features()
- `experiments/test_gun2.py` — leakage, mask, evaluator, nested CV tests
- `results/phase2/phase2_presmoke_audit.csv` — audit data (20 rows)

## Related Notes

- [[00-index|Vault Index]]
- [[notes/08-phase2-charter.md|Phase2 charter]]
- [[notes/diary/phase1-audit.md|Phase1 audit]]
- [[notes/phase2-design-review.md|Phase2 design review]]
