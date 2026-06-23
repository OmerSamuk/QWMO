# Phase-1 Pauli Audit Note

> 📚 **Related Notes:** [[../00-index|Vault Index]] · [[../../charters/qwmo-gapr-test|Faz-1 Charter]] · [[../04-phase1-decision|Phase-1 Decision]] · [[../03-pilots-overview|Pilot History]]

## Amaç
Faz-1 charter'ı (Faz-1-final.md) temel alınarak V0/V1/V2/V3 varyantlarının kod seviyesinde doğrulanması, önceki pilot bulgularının özetlenmesi ve charter uyumluluğunun kontrol edilmesi.

---

## 1. Varyant-Kod Eşlemesi

| Varyant | Charter Açıklaması | Kod Config | Durum |
|---------|-------------------|------------|-------|
| V0 | Orbital + Escape (no Pauli) | `orbital_escape` | **Hazır** — `core/qwmo.py:82` `use_escape=True`, Pauli kapalı |
| V1 | Static QWMO, eps_r=0.05 | `full_static` | **Hazır** — `operators/pauli.py:75` `static_epsilon_ratio=0.05` |
| V2 | Dynamic Epsilon, eps_max_r=0.10, eps_min_r=0.005 | `full_dynamic` | **Kısmen** — `operators/pauli.py:50-56` formül uyumlu, **ancak code default eps_min_r=0.01 (charter=0.005)** |
| V3 | GAPR Final, k=3, lambda0=0.75, eps_max_r=0.15 | `full_gapr` | **Hazır** — `operators/pauli.py:5-47` GAPR v2 diagonal normalization mevcut |

### V2 Override Gereksinimi
V2 charter'da `eps_min_r = 0.005` olarak tanımlanmıştır (`Faz-1-final.md:244-246`). Kod default'u `0.01` olduğu için Phase-1 çalıştırmasında `epsilon_min_ratio=0.005` override edilecektir.

### V3 Parametre Doğrulaması
GAPR v2 formülü (`operators/pauli.py:5-47`):
```
epsilon = clip(lambda0 * (mean_knn / (sqrt(D) * search_range)) * search_range, eps_min, eps_max)
```
Bu formül charter §6 V3'te belirtilmeyen bir formüldür, ancak mevcut en son GAPR varyantıdır. Charter `"Mevcut son GAPR formülü kullanılacaktır"` dediği için uygundur.

---

## 2. Önceki Pilot Bulguları

### GAPR Revision Pilot v2.0 (results/gapr_revision_pilot_eps010/)
Karar: **D — Stop GAPR line**

| Kriter | Sonuç | Detay |
|--------|-------|-------|
| R1: Epsilon adaptivity | **FAIL** | std(eps) > 0 + unique(eps) > 5 in >= 4/5 functions başarısız |
| R2: Saturation reduction | **FAIL** | mean eps_max_saturation_ratio < 0.50 in >= 4/5 functions başarısız |
| R3: Pauli activation | **PASS** | collision > 0 AND displacement > 0 in 5/5 functions |
| R4: Performance | **PASS** | mean(Full_GAPR_eps010) <= 1.05 * min(Static, Dynamic) |

Önemli bulgular:
- F10, F15, F20, F23'te epsilon **tamamen eps_max'a yapışıyor** (saturation ratio = 1.0)
- F5'te epsilon değişken ancak saturation ratio ~0.71-0.80 (hala RED)
- Pauli collision/displacement her fonksiyonda aktif (R3 PASS)
- Fitness performansı kötü değil (R4 PASS) — yani epsilon saturation fitness'i düşürmüyor

### GAPR Comprehensive Pilot v1.0
- G1-G5 kriterleri üzerinden değerlendirme
- Pilot decision mevcut

---

## 3. Charter Uygunluk Kontrolü

| Charter Gereksinimi | Durum |
|--------------------|-------|
| V0/V1/V2/V3 varyantları kodda tanımlı | Kısmen — config isimleri farklı, yeni ablation config eklenmeli |
| 4 fonksiyon (F5, F10, F20, F28) | **Hazır** — `benchmark/cec2017.py:12-22` |
| D=30, N=50, Tmax=300000 | **Hazır** — `experiments/config.py:19-21` |
| 30 run, seed list 1-30 | **Hazır** |
| Logging: D1 (center distance) | **Eksik** — sadece D2 (pairwise) var |
| Logging: mean_knn_distance | **Eksik** |
| Logging: epsilon_to_mean_knn_ratio | **Eksik** |
| Logging: escape_failure/neutral ayrımı | **Eksik** — sadece escape_success var |
| Logging: pauli_failure/neutral ayrımı | **Eksik** — sadece pauli_success var |
| Logging: boundary_clipping_count | **Eksik** |
| Logging: window=5 iter sınıflaması | **Eksik** |
| İstatistik: Wilcoxon signed-rank | **Hazır** — `analysis/stats.py:155-190` |
| İstatistik: Effect size (Cliff's delta) | **Eksik** — A12 mevcut, Cliff's delta eklenecek |
| Mekanizma: Zincir analizi (§12.5) | **Eksik** |

---

## 4. Audit Kararı

**Kod seviyesinde Faz-1 uygulanabilir.** Gerekli altyapı (3 epsilon modu, escape, orbital, GAPR v2, benchmark, runner) mevcuttur. Eksik olan bileşenler:

1. Phase-1 logging sistemi (core/phase1_logger.py) — §8.1-8.7
2. 4 yeni ablation config ismi (phase1_v0..v3)
3. PHASE1_CONFIG (experiments/config.py)
4. 4 varyantlı smoke test
5. Cliff's delta implementation (analysis/stats.py)
6. Phase-1 runner (experiments/phase1_run.py)
7. Phase-1 stats/mechanism analysis (analysis/phase1_stats.py, analysis/phase1_mechanism.py)
8. Tüm phase1_* output dosyaları

Bu bileşenler Gün 2-15 kapsamında eklenecektir. Charter'da belirtilen "yeni formül yasakları"na uyulacaktır.

---

## 5. Risk Notları

1. **Epsilon Saturation**: Önceki pilotta (eps_max_r=0.10 ile) epsilon F10/F20/F28'de %100 eps_max'a yapıştı. Phase-1'de V3 eps_max_r=0.15 kullanıyor — saturation riski daha yüksek.
2. **Charter Kilidi**: Charter §18 kilitli. Saturation görülse bile protokol değiştirilmeyecek. Decision Report objektif olarak A/B/C'den birini seçecek.
3. **V0 vs V3**: Charter'ın en kritik karşılaştırması. Önceki pilotlarda V0 (OrbitalEscape) Pauli'siz çalışıyordu ve performansı V3'e yakındı.
4. **V2 eps_min=0.005**: Bu değer kod default'undan farklı. Override unutulmamalı.
