---
tags: [pilots, decisions, history]
---

# Pilot History Overview

Bu not tüm pilot çalışmalarının özetini ve kararlarını içerir. Detaylar için her pilot'ın charter ve raporlarına bakın.

## 📊 Karar Tablosu

| Pilot | Karar | Tarih | Kriterler | Durum |
|---|---|---|---|---|
| K1-K6 (Erken pilot validation) | ALL PASS | — | 6/6 | ✓ Tamamlandı |
| [[../charters/qwmo-gapr-test\|Faz-1 Final Charter]] | — | locked | 480 run | ✓ Charter kilitli |
| GAPR Comprehensive Pilot v1.0 | **D — Stop** | — | G1-G5 | G1/G3/G5 FAIL |
| GAPR Revision Pilot v2.0 (eps_max=0.10) | **D — Stop GAPR line** | — | R1-R5 | R1/R2 FAIL, R3/R4/R5 PASS |
| **Phase-1 (Faz-1)** | **C — Stop GAPR line** | — | C1-C6 | **Aktif karar** |

➡️ **Güncel karar:** [[04-phase1-decision|Phase-1 Decision Report — Decision C]]

## 🔬 Pilot Zaman Çizgisi

### 1. İlk Ablasyon (`qwmo-özet` Bölüm 2)
- 4 konfig: OrbitalOnly, Orbital+Pauli, Orbital+Escape, Full QWMO
- **Bulgu:** Pauli operatörü neredeyse hiç katkı üretmiyor (Orbital+Pauli ≈ OrbitalOnly)
- Karar: Pauli problemini çözmek için yeni yaklaşım gerekli

### 2. Statik Epsilon Hipotezi
- İlk QWMO'da ε = sabit
- Yüksek boyutlarda ajanlar birbirinden uzak → Pauli tetiklenmiyor
- Karar: Dynamic Epsilon çalışmasına geç

### 3. Dynamic Epsilon (`qwmo-özet` Bölüm 4)
- ε(t) = ε_max(1 − t/T_max) + ε_min
- Pauli aktive oluyor, collision/displacement artıyor
- **Bulgu:** Fitness kazanımı yok
- Karar: Geometri farkındalığı gerekli → GAPR

### 4. GAPR Pilot v1 (`qwmo-özet` Bölüm 6)
- İlk formül: ε = λ × mean_kNN
- **Sorun:** Epsilon sürekli eps_max'a çarpıyor
- Karar: Normalizasyon gerekli

### 5. Diagonal-Normalized GAPR v2
- ε_GAPR(t) = clip(λ₀ × d̄_kNN(t)/L_max × (u-l), ε_min, ε_max)
- L_max = √D × (u-l)
- Pauli ilk kez ciddi biçimde aktive oldu

### 6. GAPR Comprehensive Pilot (`results/gapr_comprehensive_pilot/`)
- 5 fonksiyon × 8 konfig × 15 seed
- Pauli aktive oluyor, OrbitalPauli_GAPR zayıf
- **Karar D = Stop** (G1/G3/G5 FAIL)

### 7. GAPR Revision Pilot v2.0 (`results/gapr_revision_pilot_eps010/`)
- eps_max_ratio 0.15 → 0.10
- 5 fonksiyon × 4 konfig × 10 seed = 200 run
- **Karar D = Stop GAPR line** (R1/R2 FAIL, R3/R4/R5 PASS)

### 8. Faz-1 Phase-1 (`results/phase1/`)
- 4 varyant × 4 fonksiyon × 30 seed = **480 run**
- V0 (Orbital+Escape) vs V1 (Static) vs V2 (Dynamic) vs V3 (GAPR Final)
- **Karar C = GAPR ana hattan çıkar**
- Detay: [[04-phase1-decision]]

## 📌 Anahtar Bulgular

- ✓ Statik epsilon yüksek boyutlarda yetersiz
- ✓ Pauli operatörü tamamen ölü değil, dynamic epsilon ile aktive oluyor
- ✓ GAPR Pauli aktivasyonunu daha da artırıyor
- ✗ **Aktivasyon ≠ Fayda** — collision/displacement fitness'a dönüşmüyor
- ✗ Epsilon saturation (eps_max'a yapışma) hâlâ problem
- ✗ GAPR formülü nihai çözüm değil

## 📂 İlgili Charter & Dokümanlar

- [[../charters/qwmo-gapr-test|Faz-1 Final Charter v1.0]] (locked protocol)
- [[../charters/gapr-revision-pilot|GAPR Revision Pilot v2.0]] (öncül pilot)
- [[../charters/dynamic-update-plan|Dynamic Update Plan]]
- [[diary/phase1-audit|Phase-1 Audit Note]] (kod seviyesi doğrulama)

## 📂 İlgili Raporlar (results/)

- `results/phase1/phase1_decision_report.md` → taşındı: `notes/04-phase1-decision.md`
- `results/gapr_revision_pilot_eps010/revision_decision.md`
- `results/gapr_comprehensive_pilot/pilot_decision.md`
- `results/gapr_pilot/gapr_pilot_validation_report.md`
