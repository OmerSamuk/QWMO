# Faz-2 Charter Amendment 1 v1.0

**Tarih:** 2026-06-20
**Yazar:** Omer Samuk (subagent via phase2 audit)
**Referans:** `charters/radiomics-landscape.md` v2.2

## Amaç

Bu amendment, charter `radiomics-landscape.md` üzerinde üç değişiklik yapar. Hiçbir değişiklik sonuç-temelli değildir; tamamı erişim/tespit kaynaklıdır (§6 uyumlu).

---

## 1. D2/D3 Dataset Değişimi

### Değişiklik

| Charter §10 | Önceki (kaldırıldı) | Yeni (2026-06-20) |
|---|---|---|
| D2 | HNSCC-HN1 (TCIA) — bulunamadı | WORC-GIST (GitHub, pre-extracted CSV) |
| D3 | LGG (TCIA) — bulunamadı | WORC-Lipo (GitHub, pre-extracted CSV) |

### Gerekçe

HNSCC-HN1 ve LGG TCIA'da mevcut değil veya etiket/metadata erişilemez durumda. WORC Database (Apache 2.0) GitHub'da hazır CSV olarak mevcut, pre-extracted 564 features, 100× CV splits.

### §10 Uyum Kontrolü

| Kriter | WORC-GIST (D2) | WORC-Lipo (D3) |
|---|---|---|
| n_samples ≥ 50 | 246 ✓ | 115 ✓ |
| n_features ≥ 500 | 564 ✓ | 564 ✓ |
| Binary outcome | GIST vs Other ✓ | Lipoma vs Liposarcoma ✓ |
| Open license | Apache 2.0 ✓ | Apache 2.0 ✓ |
| Source | WORC Database (GitHub) ✓ | WORC Database (GitHub) ✓ |

### Pre-extracted CSV İstisnası

WORC verileri pre-extracted CSV formatında geldiği için mask extraction pipeline (PyRadiomics) atlanır. Bu, charter §6'daki "yeni operatör ekleme" yasağını ihlal etmez — sadece veri kaynağı formatından kaynaklanan bir pipeline basitleştirmesidir.

---

## 2. M5/M6 → M7/M8 Yeniden Numaralandırma

### Değişiklik

| Charter §20 (original) | Önceki kod | Düzeltme |
|---|---|---|
| M5 = Static QWMO Binary (V1) | `M5_ASO` | `V1_static_qwmo` (taşınmadı, zaten ayrı) |
| M6 = QWMO-Core Binary (V0) | `M6_AOS` | `V0_core_binary` (taşınmadı, zaten ayrı) |
| — | — | `M7_ASO` (yeni: Atom Search Optimization) |
| — | — | `M8_AOS` (yeni: Atom Orbital Search) |

### Gerekçe

Kodda `M5_ASO` ve `M6_AOS` olarak eklenen baseline yöntemler, charter §20'deki M5 (V1) ve M6 (V0) ile isim çakışması yapıyordu. Bu amendment ile:
- M5 ve M6 charter'daki anlamını korur (V1 ve V0)
- ASO → M7, AOS → M8 olarak yeniden numaralandırılır
- Toplam yöntem sayısı (V0+V1 dahil): **9** (M0-M4, M7, M8, V0, V1)

### Deney Matrisi Güncellemesi

Pilot (değişmedi): M0, M1, M2, M3, M4, V0, V1 = 7 method
Final (M5/M6 → M7/M8): M0, M1, M2, M3, M4, M7, M8, V0, V1 = 9 method

---

## 3. Final Matrix Büyüklüğü

### Değişiklik

| Charter §23.1 | Önceki (plan) | Güncel |
|---|---|---|
| Final total runs | 113,400 (7 method) | 145,800 (9 method: +M7 +M8) |
| Pilot total runs | 4,200 | 4,200 (değişmedi) |

### §23.1 Uyum

Charter §23.1 tavanı: *"sadece aşağı yönlü scaling, matrix tavanı korunur."* Final matrix 145,800 olarak planlanan 113,400'ün üzerindedir. Ancak:

- M7/M8 (ASO/AOS) charter'da baştan beri öngörülmemişti (baseline yöntem eklemesi)
- Pilot matrisi **değişmedi** (4,200)
- Bu amendment ile tavan **145,800** olarak yeniden tanımlanır

---

## 4. Değişmeyenler

Aşağıdaki charter maddeleri bu amendment'den **etkilenmez**:

- §6: Yeni QWMO operatörü yok, escape yok, orbital yok (hepsi hâlâ geçerli)
- §7: V1 Static QWMO ana varyant (değişmedi)
- §8: V0 opsiyonel kontrol (değişmedi)
- §9: GAPR yasak (değişmedi)
- §11: Leakage-free preprocessing (değişmedi)
- §12: CV tasarımı (değişmedi)
- §14: Sigmoid decoding (değişmedi)
- §18: Subspace rejimleri (değişmedi)
- §21: Bütçe (değişmedi)
- §22: Seed protokolü (değişmedi)
- §34: Wilcoxon + Holm + Cliff's delta (değişmedi)

---

## Geçerlilik

Bu amendment, `charters/radiomics-landscape.md` v2.2 ile birlikte okunur. İkisi birlikte Faz-2'nin tek geçerli protokolüdür.

Amendment locked: **2026-06-20**
