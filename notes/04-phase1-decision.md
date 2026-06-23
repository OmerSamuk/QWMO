# Phase-1 Decision Report

> 📚 **Related Notes:** [[00-index|Vault Index]] · [[03-pilots-overview|Pilot History]] · [[../charters/qwmo-gapr-test|Faz-1 Charter]] · [[diary/phase1-audit|Phase-1 Audit]] · [[diary/qwmo-ozet|Research Diary]]
>
> 🏆 **FINAL DECISION: C** — GAPR excluded from main line

## 1. Amaç
QWMO-GAPR Faz-1 charter (Faz-1-final.md) kapsamında GAPR Final varyantının Pauli/adaptive epsilon problemini çözüp çözmediğine karar vermek.

## 2. Deney Protokolü
- **Fonksiyonlar:** F5 (Schwefel), F10 (Rastrigin), F20 (Hybrid), F28 (Composition)
- **Varyantlar:** V0 (Orbital+Escape), V1 (Static QWMO), V2 (Dynamic Epsilon), V3 (GAPR Final)
- **Boyut:** D=30
- **Popülasyon:** N=50
- **FE Bütçesi:** Tmax=300000
- **Run:** 30 bağımsız run × 4 fonksiyon × 4 varyant = 480 run
- **İstatistik:** Wilcoxon signed-rank (p<0.05), Cliff's delta

## 3. Test Edilen Varyantlar
| ID | Operatörler | Epsilon |
|----|------------|---------|
| V0 | Orbital + Escape | Yok (Pauli yok) |
| V1 | Orbital + Static Pauli + Escape | static_epsilon_ratio = 0.05 |
| V2 | Orbital + Dynamic Pauli + Escape | eps_max=0.10, eps_min=0.005 |
| V3 | Orbital + GAPR Pauli + Escape | k=3, λ0=0.75, eps_max=0.15 |

## 4. Fitness Sonuçları

### F5 (Schwefel)

| Varyant | Mean | Std | Median | Best |
|---|---|---|---|---|
| V0 | 5.9027e+02 | 1.2675e+01 | 5.8946e+02 | 5.6592e+02 |
| V1 | 5.9148e+02 | 1.6465e+01 | 5.9382e+02 | 5.6335e+02 |
| V2 | 5.9526e+02 | 1.6507e+01 | 5.9170e+02 | 5.6114e+02 |
| V3 | 5.8888e+02 | 1.6692e+01 | 5.8815e+02 | 5.5708e+02 |

### F10 (Rastrigin)

| Varyant | Mean | Std | Median | Best |
|---|---|---|---|---|
| V0 | 3.5562e+03 | 2.7460e+02 | 3.5046e+03 | 3.1485e+03 |
| V1 | 3.3611e+03 | 4.4351e+02 | 3.3729e+03 | 2.4152e+03 |
| V2 | 3.4714e+03 | 3.9899e+02 | 3.5018e+03 | 2.4645e+03 |
| V3 | 3.4997e+03 | 3.7481e+02 | 3.4991e+03 | 2.7637e+03 |

### F20 (Hybrid)

| Varyant | Mean | Std | Median | Best |
|---|---|---|---|---|
| V0 | 2.1899e+03 | 5.8074e+01 | 2.1840e+03 | 2.0838e+03 |
| V1 | 2.1872e+03 | 6.3395e+01 | 2.1883e+03 | 2.0936e+03 |
| V2 | 2.1932e+03 | 5.3743e+01 | 2.2080e+03 | 2.0854e+03 |
| V3 | 2.1882e+03 | 6.1546e+01 | 2.1729e+03 | 2.1006e+03 |

### F28 (Composition)

| Varyant | Mean | Std | Median | Best |
|---|---|---|---|---|
| V0 | 3.2065e+03 | 1.8749e+01 | 3.2101e+03 | 3.1113e+03 |
| V1 | 3.2037e+03 | 2.4492e+01 | 3.2093e+03 | 3.1093e+03 |
| V2 | 3.2004e+03 | 2.2394e+01 | 3.2067e+03 | 3.1279e+03 |
| V3 | 3.2092e+03 | 4.7987e+00 | 3.2097e+03 | 3.1960e+03 |

## 5. İstatistiksel Analiz

### F5 (Schwefel)

| Comparison | p-value | Significant | Cliff's delta | Effect Size | Median Improvement (%) |
|---|---|---|---|---|---|
| V3 vs V0 | 0.8078304156661034 | False | 0.0066666666666666 | negligible | -0.2224667381560777 |
| V3 vs V1 | 0.5158484429121017 | False | 0.0822222222222222 | negligible | -0.9549278579155136 |
| V3 vs V2 | 0.1909295208752155 | False | 0.1977777777777777 | small | -0.5999062064219977 |
| V2 vs V1 | 0.6120056137442589 | False | -0.0888888888888888 | negligible | -0.3571643023101987 |
| V1 vs V0 | 0.6408254038542509 | False | -0.0444444444444444 | negligible | 0.7395230312000667 |

### F10 (Rastrigin)

| Comparison | p-value | Significant | Cliff's delta | Effect Size | Median Improvement (%) |
|---|---|---|---|---|---|
| V3 vs V0 | 0.5158484429121017 | False | 0.0733333333333333 | negligible | -0.158614901100238 |
| V3 vs V1 | 0.4399667661637068 | False | -0.1644444444444444 | small | 3.7400800905965896 |
| V3 vs V2 | 0.8235769439488649 | False | -0.0111111111111111 | negligible | -0.0779234409800947 |
| V2 vs V1 | 0.4521643426269293 | False | -0.1044444444444444 | negligible | 3.820980971428817 |
| V1 vs V0 | 0.0449072085320949 | True | 0.2555555555555555 | small | -3.758137634260629 |

### F20 (Hybrid)

| Comparison | p-value | Significant | Cliff's delta | Effect Size | Median Improvement (%) |
|---|---|---|---|---|---|
| V3 vs V0 | 0.9838335812091829 | False | 0.0577777777777777 | negligible | -0.5090244105853758 |
| V3 vs V1 | 0.7921590935438871 | False | 0.0177777777777777 | negligible | -0.7082615450338496 |
| V3 vs V2 | 0.7456546742469072 | False | 0.0555555555555555 | negligible | -1.58976507193593 |
| V2 vs V1 | 0.8393927440047264 | False | -0.0133333333333333 | negligible | 0.8957437481441257 |
| V1 vs V0 | 0.8235769439488649 | False | 0.0288888888888888 | negligible | 0.2006583201671284 |

### F28 (Composition)

| Comparison | p-value | Significant | Cliff's delta | Effect Size | Median Improvement (%) |
|---|---|---|---|---|---|
| V3 vs V0 | 0.4399667661637068 | False | 0.0933333333333333 | negligible | -0.0110036117114348 |
| V3 vs V1 | 0.935398668050766 | False | 0.0511111111111111 | negligible | 0.013196413697839 |
| V3 vs V2 | 0.0576879289001226 | False | -0.2644444444444444 | small | 0.0922091776259165 |
| V2 vs V1 | 0.1293530762195587 | False | 0.2266666666666666 | small | -0.0789399740272088 |
| V1 vs V0 | 0.8078304156661034 | False | 0.0333333333333333 | negligible | -0.0241968322951823 |

## 6. Epsilon Davranışı
V3 epsilon saturasyon oranı:
- F5 (Schwefel): 0.0588138000262357
- F10 (Rastrigin): 0.931389975115535
- F20 (Hybrid): 0.7603305312517871
- F28 (Composition): 0.1305705444023639

## 7. Pauli Collision / Displacement Analizi
- F5 (Schwefel): V3 collision=0.0697472808883667, V0 collision=0.0
- F10 (Rastrigin): V3 collision=0.0989644851667947, V0 collision=0.0
- F20 (Hybrid): V3 collision=0.0881797907016641, V0 collision=0.0
- F28 (Composition): V3 collision=0.008792215481896, V0 collision=0.0

## 8. Escape Success / Failure Analizi
- F5 (Schwefel): V3 escape success ratio = 0.1030395294361623
- F10 (Rastrigin): V3 escape success ratio = 0.0297630913209708
- F20 (Hybrid): V3 escape success ratio = 0.0408287507099026
- F28 (Composition): V3 escape success ratio = 0.1059190666557885

## 9. Diversity Analizi
- F5 (Schwefel): V3 mean diversity (center) = 166.07678265931855
- F10 (Rastrigin): V3 mean diversity (center) = 233.08060730683744
- F20 (Hybrid): V3 mean diversity (center) = 215.04827901415516
- F28 (Composition): V3 mean diversity (center) = 167.46097369264177

## 10. Collision → Escape → Improvement Zinciri
(Chain analysis results from phase1_mechanism.py)

## 11. Ana Bulgular
- **C1 (V3 > V1 on F20/F10):** ✗
- **C2 (V3 >= V2 on F20/F10):** ✗
- **C3 (V3 >= V0 on F20/F10):** ✗
- **C4 (mechanism → fitness correlation):** ✓
- **C5 (epsilon not saturated):** ✗

- C1 (V3 cannot beat V0): ✓
- C2 (collision ↑ but fitness →): ✗
- C3 (diversity ↑ but fitness →): ✗
- C4 (failed escape ratio ↑): ✓
- C5 (epsilon saturation): ✓
- C6 (no advantage F20/F10): ✓
## 12. Karar

**Karar: C**

GAPR Final (V3) fails key exclusion criteria: it cannot systematically beat V0 (Orbital+Escape), and its mechanism costs (collision/displacement, epsilon saturation) do not translate to fitness gains.

## 13. Sonraki Faz İçin Öneri

GAPR, Pauli aktivasyonunu artırmasına rağmen bu aktivasyonu sistematik fitness kazanımına dönüştürememiştir; bu durum high-dimensional exclusion mekanizmalarında activation–utility ayrımını doğrulamaktadır.

---

## Decision Criteria Scores

| Decision | Score | Threshold |
|----------|-------|-----------|
| A (GAPR ana algoritmaya girer) | 1/4 | 4 |
| B (GAPR niş mekanizma olur) | 1/3 | 3 |
| C (GAPR ana hattan çıkar) | 4/4 | 4 |
