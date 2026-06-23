# Faz-2 Radiomics Çalışması — Uygulama Planı v1.3 (WORC Amendment)

> **Plan durumu:** GÜNCELLENDİ — amendment-1 ile senkron.
> **Charter referansı:** [[../charters/radiomics-landscape|Faz-2 Radiomics Landscape & Pauli Response Pilot v2.2]] (LOCKED) + [[../charters/radiomics-landscape-amendment-1|Amendment 1]].
> **Versiyon:** v1.3 — 2026-06-20 WORC dataset swap + M5/M6 → M7/M8 rename.

---

## 0. Çerçeveleme (charter §1 + revision-notes D-5)

> V1 Static QWMO Faz-2'de **Pauli'yi kurtarmak** için değil, **yeni (radiomics) uzayda Pauli tepkisini gözlemlemek** için kullanılır. Faz-1 sonucu (Activation ≠ Utility, [[04-phase1-decision|Karar C]]) geçerlidir; bu çalışma onu çürütmez, sadece yeni bir uzayda sınar.

---

## 1. Karar Özeti (revision-notes + son onay)

| #  | Karar                                                                   | Kaynak     |
|----|-------------------------------------------------------------------------|------------|
| K1 | Peer-Review Gate Gün 0'da zorunlu                                       | rev D-3    |
| K2 | TCIA/ROI erişim doğrulaması Gün 0 içinde                                | rev D-3    |
| K3 | Pre-Smoke: 1 dataset = D2 (WORC-GIST), 4 method = M0+M3+M4+V1, 5 seed, 1000 FE | amendment-1 |
| K4 | Charter §23.1 tavan matris korunur; pre-smoke sonrası **yalnız aşağı** ölçeklenir | son onay |
| K5 | V0 pilotta zorunlu, 10 seed (full pilot seed protokolü ile aynı)        | son onay   |
| K6 | V1 ana varyant; V0 = Pauli izolasyon kontrolü                           | rev D-2    |
| K7 | Feature extraction: PyRadiomics (D1); WORC pre-CSV (D2/D3)             | amendment-1 |
| K8 | Compute: GCloud VM, yalnızca Peer-Review Gate Aşama C onayından sonra   | orijinal   |

Dataset teklifi (Amendment 1 ile güncellendi):

| #  | Dataset                         | Modalite       | Binary task                | n     |
|----|---------------------------------|----------------|----------------------------|-------|
| D1 | NSCLC Radiogenomics (TCIA)      | CT (toraks)    | 2-yıl survival / EGFR mut  | ~211  |
| D2 | WORC-GIST (GitHub, pre-CSV)     | CT (abdomen)   | GIST vs other              | 246   |
| D3 | WORC-Lipo (GitHub, pre-CSV)     | T1w MRI (extremite) | Lipoma vs liposarcoma | 115   |

---

## 2. Final Zaman Çizelgesi

```
Gün 0   PEER-REVIEW GATE (yerel, kapalı döngü)
        ├─ A. Tasarım İncelemesi
        │     • Dataset teklifi onayı: D1 / D2 / D3
        │     • TCIA collection URL + lisans + mask formatı doğrulaması [K2]
        │     • PyRadiomics 3.x modality uyumluluğu
        │     • Çıktı: notes/phase2-design-review.md
        ├─ B. Pre-Smoke [K3]
        │     • 1 dataset = D1
        │     • 2 subspace (Ranked, Random)
        │     • p ∈ {100, full}
        │     • 4 method: M0 Random, M3 GA, M4 BPSO, V1 Static QWMO  ← V0 yok
        │     • 5 seed × 1000 FE
        │     • Çıktı: phase2_presmoke_timing.csv + phase2_presmoke_report.md
        │     • Ölçümler: 1 FE süresi, 1 run süresi, dataset×p×method×seed süresi, bellek
        ├─ C. Onay
        │     • Pre-smoke sürelerine göre ölçeklenmiş pilot/final matris [K4]
        │     • phase2_config.yaml'da pilot_budget_fe, final_budget_fe, p-level subsetleri sabitlenir
        └─ D. GCloud VM kurulumu (n2-highmem-32 önerisi, preemptible opsiyonu)

Gün 1   Dataset kilidi (erişim teyitli) + phase2_dataset_summary.csv
Gün 2   Leakage-free preprocessing audit → phase2_preprocessing_report.md
Gün 3   Fitness evaluator + tam baseline smoke (M0..M6 + V0+V1, hafif ölçek)
Gün 4   Optimizer entegrasyonu → phase2_optimizer_audit.md
Gün 5–7 Asıl Pilot
        • 2 dataset × 2 subspace × p ⊆ {50,100,250,full} (charter §23.1 tavan) [K4]
        • 7 method (M0..M6 dahil) — V0 = 10 seed [K5]
        • 10 seed (V0 dahil tüm methodlar aynı seed protokolü)
        • 1000 FE
Gün 8   Pilot Go/No-Go
Gün 9–16 Final matris (ölçeklenmiş; charter §23.1 tavan)
        • 3 dataset × 2 subspace × p ⊆ {25,50,100,250,500,full} [K4]
        • 7 method × 30 seed × 3000 FE
Gün 17–18 Wilcoxon + Holm + Cliff's delta
Gün 19  Landscape + Pauli response analizi
Gün 20  Decision Report → phase2_decision_report.md (Karar A/B/C)
```

---

## 3. Pre-Smoke Matris (Amendment 1 ile güncellendi)

```text
datasets          : [D2]                                            # WORC-GIST
subspace_regimes  : [ranked, random]
p_levels          : [100, full]
methods           : [M0_random, M3_GA, M4_BPSO, V1_static_qwmo]   # V0 yok
seeds             : [0,1,2,3,4]                                    # 5 seed
fitness_budget    : 1000 FE
outer_cv          : 5 folds × 2 repeats                            # charter §12
inner_cv          : 3 folds                                         # charter §12
```

---

## 4. Pilot / Final Tavan Matris (charter §23 — K4)

**Tavan = charter §23.1 / §23.2**; pre-smoke süreleri bunu **yalnızca küçültmek** için kullanılır.

Pilot tavanı:

```text
2 dataset × 2 subspace × 4 p × 7 method × 10 seed × 5×2 fold × 1000 FE
```

Final tavanı (pilot pozitifse):

```text
3 dataset × 2 subspace × 6 p × 9 method × 30 seed × 5×3 fold × 3000 FE   # M7/M8 eklendi
```

V0 her zaman **10 seed** ile çalışır (pilot ölçekli) [K5].

---

## 5. Kod Modül Eşlemesi (final)

### Yeniden kullanılacak

```text
core/qwmo.py
core/agent.py
core/kdtree_util.py
operators/orbital.py
operators/pauli.py
operators/escape.py
baselines/aso.py
baselines/aos.py
baselines/qpso.py
analysis/stats.py
analysis/convergence.py
analysis/diversity.py
analysis/pauli_activation.py
analysis/escape_behavior.py
analysis/sensitivity.py
analysis/runtime.py
```

### Eklenecek (charter'a dokunmadan)

```text
radiomics/
  extract.py            # PyRadiomics wrapper (DICOM/nii.gz + mask → features)
  datasets.py           # D1/D2/D3 loader, lisans/bilgi metadata

fitness/
  evaluator.py          # (X, y, mask) → (mean_inner_AUC, n_features, valid)
  preprocessing.py      # median impute, StandardScaler, variance/corr filter — inner-train only

core/
  qwmo_binary.py        # V1: latent z + sigmoid>0.5 mask + Orbital/Static Pauli/Escape
  qwmo_core_binary.py   # V0: aynı, Pauli yok

baselines/
  bpso.py               # M4 Binary PSO (qpso.py'dan adapte)
  ga_binary.py          # M3 Genetic Algorithm
  greedy.py             # M1 Forward, M2 Backward
  random_search.py      # M0
  aso_binary.py         # M7 ASO Binary (latent → sigmoid → mask)
  aos_binary.py         # M8 AOS Binary (latent → sigmoid → mask)

experiments/
  phase2_runner.py      # matris orkestratörü (presmoke / smoke / pilot / final modları)
  phase2_smoke_test.py  # mode=presmoke | smoke
  phase2_outer_audit.py # leakage audit

analysis/
  phase2_pauli_response.py   # §25, §26, §30
  phase2_landscape.py        # §27, §28, §29
  phase2_stats.py            # Wilcoxon + Holm + Cliff's delta
  phase2_decision.py         # §31-33 → A/B/C
```

---

## 6. Çıktı Dosyaları (charter §35)

```text
phase2_config.yaml
phase2_dataset_summary.csv
phase2_presmoke_timing.csv
phase2_presmoke_report.md
phase2_preprocessing_report.md
phase2_smoke_test_report.md
phase2_optimizer_audit.md
phase2_pilot_results_raw.csv
phase2_pilot_decision_note.md
phase2_results_raw.csv
phase2_iteration_logs.csv
phase2_event_logs.csv
phase2_elite_masks.csv
phase2_pauli_response_metrics.csv
phase2_landscape_metrics.csv
phase2_statistical_tests.csv
phase2_effect_sizes.csv
phase2_decision_report.md
notes/phase2-design-review.md
```

Plotlar (charter §35):

```text
phase2_plots/performance_auc/
phase2_plots/selected_feature_count/
phase2_plots/elite_jaccard/
phase2_plots/feature_stability/
phase2_plots/pauli_response/
phase2_plots/population_collapse/
phase2_plots/correlation_plateau/
phase2_plots/convergence/
phase2_plots/stagnation/
phase2_plots/escape_benefit/
phase2_plots/dimension_scaling/
```

---

## 7. Karar Eşikleri (charter §31-33)

### Ana 5 kriter (Karar A için en az 3'ü)

```text
Kriter 1 — Multimodality       : Elite Jaccard Distance > 0.60
Kriter 2 — Stability Düşüklüğü : Kuncheva Stability < 0.70
Kriter 3 — Seed Sensitivity    : AUC std across seeds > 0.03
Kriter 4 — Escape Benefit      : P(improvement | escape) > P(improvement | no_escape) + 0.10
Kriter 5 — Correlation Plateau : Mean Selected Feature Correlation > 0.80
```

### Pauli-spesifik ek kriterler (Karar A için en az 2'si)

```text
pauli_collision_count > 0
pauli_displacement_count > 0
population collapse gecikir
elite_jaccard_distance artar
mean_abs_correlation_selected düşer
feature_family_coverage artar
pauli_success_ratio > pauli_failure_ratio
```

### Karar Kuralları

```text
Karar A: ana kriterlerden ≥3 + Pauli kriterlerden ≥2
         → Faz-3 = Static QWMO Pauli-aware Radiomics Optimizer

Karar B: ana kriterlerden =2  VEYA  uzay zor ama Pauli tepkisi sınırlı
         → Faz-3 = Radiomics QWMO varyantı, Pauli appendix/mechanism

Karar C: ana kriterlerden ≤1  VEYA  Pauli yalnız maliyet/gürültü
         → QWMO-Radiomics hattı ana araştırma hattı olmaktan çıkar
```

---

## 8. Yasaklar (charter §6 + Amendment 1 — teyit)

```text
• Yeni QWMO operatörü / yeni escape / orbital / epsilon formülü eklemek yok
• GAPR geri gelmez; dynamic epsilon yok; SoftClip / rank-based Pauli yok
• Sonuçlara göre dataset veya başarı kriteri değiştirmek yok
• Leakage içeren pipeline yok
• V1 kötü gelirse V0'ı ana algoritma ilan etmek yok
• V1 iyi gelirse Faz-1 sonucunu yok saymak yok
• charters/radiomics-landscape.md ve cec2017-py/* dosyaları kilitli, dokunulmaz
• amendment-1 geçerlidir ve charter ile birlikte okunur
```

---

## 9. Plan Modu Çıkışı Sonrası Yapılacaklar (sıralı)

```text
1. notes/phase2-design-review.md (taslak, gözden geçirme şablonu)
2. phase2_config.yaml (placeholder anahtarlar: presmoke/pilot/final modları)
3. radiomics/datasets.py (D1 indirme yolu + lisans teyit notu)
4. core/qwmo_binary.py ve core/qwmo_core_binary.py sözleşme taslakları
5. experiments/phase2_runner.py iskeleti (mode in {presmoke, smoke, pilot, final})
6. experiments/phase2_smoke_test.py iskeleti
```

Hiçbir koşulda `charters/*` veya `cec2017-py/*` dokunulmayacak.

---

## 10. Cross-References

- [[../charters/radiomics-landscape|Faz-2 Radiomics Landscape & Pauli Response Pilot v2.2]] (LOCKED)
- [[../charters/radiomics-landscape-amendment-1|Amendment 1]] (2026-06-20)
- [[04-phase1-decision|Phase-1 Decision = C]]
- [[00-index|Vault Index]]
- [[../revision-notes|revision-notes.txt]] (plan revizyon kaynağı)

## Related Notes

- [[00-index|Vault Index]]
- [[notes/08-phase2-charter.md|Phase2 charter]]
- [[../charters/dynamic-update-plan.md|Dynamic update plan]]
