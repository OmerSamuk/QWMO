# QWMO-GAPR Adaptive Epsilon Uygulama TODO Listesi

Bu belge, QWMO projesine **Adaptive Epsilon / Geometry-Adaptive Pauli Radius (GAPR)** eklemek için uygulanacak kesin görev listesidir.

Amaç: statik ve lineer-dinamik epsilon yerine, popülasyonun anlık geometrisine bağlı çalışan adaptif bir Pauli exclusion radius eklemek; bunu kontrollü pilot deneyle doğrulamak; başarılı olursa Faz-1 ana deneylerine taşımak.

---

## 0. Genel Karar

### 0.1 Yeni hipotez

Mevcut pilot sonuçları şunu gösterdi:

- Pauli operatörü artık aktif.
- Static ve dynamic epsilon farklı davranıyor.
- Ancak dynamic epsilon açık bir performans üstünlüğü göstermedi.
- Escape operatörü hâlâ ana performans katkısını taşıyor.
- Pauli’nin final fitness katkısı problem-bağımlı ve zayıf.

Bu nedenle yeni hipotez:

> Pauli exclusion radius, zamana bağlı bir schedule yerine popülasyonun anlık geometrisinden türetilirse, Pauli operatörü daha anlamlı ve problem-bağımlı şekilde çalışabilir.

Bu yeni varyantın adı:

```text
QWMO-GAPR
Geometry-Adaptive Pauli Radius
```

---

## 1. Kesin Kapsam

Bu çalışma **Faz-1.5 / GAPR Pilot** olarak uygulanacak.

Bu aşamada:

- Mevcut static epsilon silinmeyecek.
- Mevcut dynamic epsilon silinmeyecek.
- Adaptive epsilon üçüncü mod olarak eklenecek.
- Full 30D/50D/100D ana deney hemen çalıştırılmayacak.
- Önce küçük pilot doğrulama yapılacak.

---

## 2. Matematiksel Tanım

### 2.1 Kullanılacak formül

İlk sürümde sadece kNN tabanlı sade adaptif formül kullanılacak:

```math
epsilon_adaptive(t) = clip(lambda0 * mean_d_kNN(t), epsilon_min, epsilon_max)
```

Burada:

```math
mean_d_kNN(t) = (1/N) * sum_i d_i^(k)
```

- `d_i^(k)`: i. ajanın k-en-yakın komşusuna olan mesafe.
- `N`: popülasyon büyüklüğü.
- `k`: k-en-yakın komşu indeksi.
- `lambda0`: kNN mesafe ölçek katsayısı.
- `epsilon_min`: minimum izin verilen exclusion radius.
- `epsilon_max`: maksimum izin verilen exclusion radius.

### 2.2 Varsayılan değerler

```python
adaptive_k = 3
adaptive_lambda0 = 0.75
epsilon_min_ratio = 0.01
epsilon_max_ratio = 0.15
```

Bounds:

```python
search_range = upper_bound - lower_bound
epsilon_min = epsilon_min_ratio * search_range
epsilon_max = epsilon_max_ratio * search_range
```

### 2.3 Bu aşamada EKLENMEYECEK şeyler

Aşağıdakiler bu aşamada uygulanmayacak:

- stagnation-aware epsilon
- diversity-collapse multiplier
- alpha / beta ek katsayıları
- fonksiyona özel epsilon tuning
- boyuta özel elle ayarlanmış epsilon
- adaptive lambda schedule
- full GAPR theory proof

Bu maddeler future work veya Faz-2 konusu olabilir.

---

## 3. Kod Değişiklikleri

Ana branch:

```text
feature/gapr
```

Mevcut branch üzerinden yeni branch aç:

```bash
git checkout perf/cec-standard-budget
git pull
git checkout -b feature/gapr
```

---

## 4. `operators/pauli.py` Değişiklikleri

### 4.1 Yeni fonksiyon ekle

`operators/pauli.py` içine aşağıdaki fonksiyon eklenecek.

```python
def compute_adaptive_epsilon(
    positions,
    lower_bound,
    upper_bound,
    k=3,
    lambda0=0.75,
    epsilon_min_ratio=0.01,
    epsilon_max_ratio=0.15,
):
    \"\"\"Geometry-Adaptive Pauli Radius (GAPR).

    Computes epsilon from the current population geometry using the mean
    k-nearest-neighbor distance.
    \"\"\"
    positions = np.asarray(positions)
    n_agents = positions.shape[0]

    search_range = upper_bound - lower_bound
    epsilon_min = epsilon_min_ratio * search_range
    epsilon_max = epsilon_max_ratio * search_range

    if n_agents <= 1:
        return float(epsilon_min)

    k_eff = min(k, n_agents - 1)

    tree = build_kdtree(positions)
    distances, _ = tree.query(positions, k=k_eff + 1)

    distances = np.asarray(distances)
    if distances.ndim == 1:
        kth_distances = distances
    else:
        kth_distances = distances[:, k_eff]

    mean_knn = float(np.mean(kth_distances))
    epsilon = lambda0 * mean_knn

    return float(np.clip(epsilon, epsilon_min, epsilon_max))
```

Notlar:

- Yeni `KDTree` import etme; mevcut `build_kdtree` helper kullanılacak.
- `build_kdtree` SciPy KDTree/cKDTree dönüyorsa `tree.query(...)` desteklemeli.
- Eğer mevcut helper query API farklıysa helper uyumlu hale getirilecek, ama matematik değiştirilmeyecek.

---

### 4.2 Epsilon hesaplama tek fonksiyona bağlanacak

`pauli.py` içine şu fonksiyon eklenecek veya mevcut logic bu yapıya çevrilecek:

```python
def compute_epsilon(
    positions,
    t,
    T_max,
    lower_bound,
    upper_bound,
    mode="dynamic",
    epsilon_max_ratio=0.1,
    epsilon_min_ratio=0.01,
    static_epsilon_ratio=0.05,
    adaptive_k=3,
    adaptive_lambda0=0.75,
    adaptive_epsilon_max_ratio=0.15,
):
    if mode == "static":
        return float(static_epsilon_ratio * (upper_bound - lower_bound))

    if mode == "dynamic":
        return compute_dynamic_epsilon(
            t=t,
            T_max=T_max,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            epsilon_max_ratio=epsilon_max_ratio,
            epsilon_min_ratio=epsilon_min_ratio,
        )

    if mode == "adaptive":
        return compute_adaptive_epsilon(
            positions=positions,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            k=adaptive_k,
            lambda0=adaptive_lambda0,
            epsilon_min_ratio=epsilon_min_ratio,
            epsilon_max_ratio=adaptive_epsilon_max_ratio,
        )

    raise ValueError(f"Unknown epsilon mode: {mode}")
```

---

### 4.3 `pauli_exclusion` imzası güncellenecek

Mevcut fonksiyon şu parametreleri almalı:

```python
def pauli_exclusion(
    agents,
    evaluate,
    rng,
    t,
    T_max,
    lower_bound,
    upper_bound,
    epsilon_mode="dynamic",
    epsilon_max_ratio=0.1,
    epsilon_min_ratio=0.01,
    static_epsilon_ratio=0.05,
    adaptive_k=3,
    adaptive_lambda0=0.75,
    adaptive_epsilon_max_ratio=0.15,
):
```

Dikkat:

- `fes_counter` kullanılmayacak.
- `max_fes` kullanılmayacak.
- FE bütçesinin tek otoritesi `core/qwmo.py` içindeki `_evaluate()` olacak.
- `evaluate(new_position)` BudgetExceeded fırlatabilir.
- Tercih edilen davranış: BudgetExceeded dışarı çıksın ve `QWMO.run()` Pauli çağrısında yakalayıp döngüyü temiz şekilde bitirsin.

---

### 4.4 `pauli_exclusion` dönüş değeri değişecek

Dönüş:

```python
return {
    "epsilon": epsilon_t,
    "collision_count": collision_count,
    "displacement_count": displacement_count,
    "success_count": success_count,
}
```

Eski tuple dönüşü kullanılmayacak.

Neden: `epsilon_history` kaydı için epsilon değeri dışarı taşınmalı.

---

### 4.5 Pauli success tanımı

`success_count` sadece şu durumda artacak:

```python
if new_fitness < old_fitness:
    success_count += 1
```

Displacement olan ama fitness kötüleşen örnekler success sayılmayacak.

---

## 5. `core/qwmo.py` Değişiklikleri

### 5.1 Yeni ablation configleri

`ABLATION_CONFIGS` içine şunlar eklenecek:

```python
"orbital_pauli_adaptive",
"full_adaptive",
```

Tam liste:

```python
ABLATION_CONFIGS = {
    "orbital_only",
    "orbital_pauli_static",
    "orbital_pauli_dynamic",
    "orbital_pauli_adaptive",
    "orbital_escape",
    "full_static",
    "full_dynamic",
    "full_adaptive",
}
```

---

### 5.2 Pauli kullanım flagleri

`self.use_pauli` şu configlerde `True` olacak:

```python
"orbital_pauli_static",
"orbital_pauli_dynamic",
"orbital_pauli_adaptive",
"full_static",
"full_dynamic",
"full_adaptive",
```

`self.use_escape` şu configlerde `True` olacak:

```python
"orbital_escape",
"full_static",
"full_dynamic",
"full_adaptive",
```

---

### 5.3 Epsilon mode seçimi

Şu mantık kullanılacak:

```python
if "adaptive" in ablation_config:
    self.pauli_epsilon_mode = "adaptive"
elif "static" in ablation_config:
    self.pauli_epsilon_mode = "static"
elif "dynamic" in ablation_config:
    self.pauli_epsilon_mode = "dynamic"
else:
    self.pauli_epsilon_mode = None
```

---

### 5.4 Yeni parametreler

`QWMO.__init__` içine eklenecek:

```python
adaptive_k=3,
adaptive_lambda0=0.75,
adaptive_epsilon_max_ratio=0.15,
```

Kaydedilecek:

```python
self.adaptive_k = adaptive_k
self.adaptive_lambda0 = adaptive_lambda0
self.adaptive_epsilon_max_ratio = adaptive_epsilon_max_ratio
```

---

### 5.5 Yeni log alanı

`__init__` içine eklenecek:

```python
self.epsilon_history = []
```

Bu liste:

- static modda her Pauli iterasyonunda aynı değerleri kaydeder.
- dynamic modda lineer azalan değerleri kaydeder.
- adaptive modda kNN tabanlı değişen değerleri kaydeder.
- orbital_only ve orbital_escape modlarında boş kalabilir.

---

### 5.6 Pauli çağrısı güncellenecek

`run()` içinde Pauli çağrısı şu yapıda olacak:

```python
if self.use_pauli:
    try:
        pauli_info = pauli_exclusion(
            agents=self.agents,
            evaluate=self._evaluate,
            rng=self.rng,
            t=t,
            T_max=T_max,
            lower_bound=self.lower_bound,
            upper_bound=self.upper_bound,
            epsilon_mode=self.pauli_epsilon_mode,
            epsilon_max_ratio=self.epsilon_max_ratio,
            epsilon_min_ratio=self.epsilon_min_ratio,
            static_epsilon_ratio=self.static_epsilon_ratio,
            adaptive_k=self.adaptive_k,
            adaptive_lambda0=self.adaptive_lambda0,
            adaptive_epsilon_max_ratio=self.adaptive_epsilon_max_ratio,
        )
    except BudgetExceeded:
        break

    self.epsilon_history.append(pauli_info["epsilon"])
    self.pauli_collision_history.append(pauli_info["collision_count"])
    self.pauli_displacement_history.append(pauli_info["displacement_count"])
    self.pauli_success_history.append(pauli_info["success_count"])
```

Ardından global best güncellenecek:

```python
for agent in self.agents:
    if agent.fitness < self.best_agent.fitness:
        self.best_agent = agent.copy()
```

---

### 5.7 Escape success semantiği kontrol edilecek

Aşağıdaki ayrım kesin olacak:

```python
escape_attempts
escape_executed
escape_successes
```

Tanımlar:

- `escape_attempts`: stagnation threshold aşılmış ve escape probability denenmiş ajan sayısı.
- `escape_executed`: `adaptive_quantum_escape(...)` yeni pozisyon döndürdüyse artar.
- `escape_successes`: yeni pozisyonun fitness değeri eski fitness değerinden daha iyiyse artar.

Eğer `escape_executed_history` henüz yoksa eklenecek:

```python
self.escape_executed_history = []
```

Loglama:

```python
self.escape_attempt_history.append(escape_attempts)
self.escape_executed_history.append(escape_executed)
self.escape_success_history.append(escape_successes)
self.escape_delta_history.append(mean_delta)
```

`mean_delta` sadece executed escape sayısına göre hesaplanacak:

```python
mean_delta = delta_sum / escape_executed if escape_executed > 0 else 0.0
```

---

## 6. `experiments/config.py` Değişiklikleri

### 6.1 QWMO params

`QWMO_PARAMS` içine eklenecek:

```python
"adaptive_k": 3,
"adaptive_lambda0": 0.75,
"adaptive_epsilon_max_ratio": 0.15,
```

---

### 6.2 Ablation configs

`ABLATION_CONFIGS` şu hale getirilecek:

```python
ABLATION_CONFIGS = [
    "QWMO_OrbitalOnly",
    "QWMO_OrbitalPauli_Static",
    "QWMO_OrbitalPauli_Dynamic",
    "QWMO_OrbitalPauli_Adaptive",
    "QWMO_OrbitalEscape",
    "QWMO_Full_Static",
    "QWMO_Full_Dynamic",
    "QWMO_Full_Adaptive",
]
```

---

### 6.3 Pilot GAPR config

Yeni config:

```python
GAPR_PILOT_CONFIG = {
    "functions": [10, 20],
    "dimension": 30,
    "population_size": 50,
    "max_fes": 300_000,
    "seeds": list(range(1, 11)),
    "ablation_configs": [
        "QWMO_OrbitalOnly",
        "QWMO_OrbitalPauli_Static",
        "QWMO_OrbitalPauli_Dynamic",
        "QWMO_OrbitalPauli_Adaptive",
        "QWMO_OrbitalEscape",
        "QWMO_Full_Static",
        "QWMO_Full_Dynamic",
        "QWMO_Full_Adaptive",
    ],
    "output_dir": "results/gapr_pilot",
    "json_name": "gapr_pilot_D30.json",
    "report_name": "gapr_pilot_validation_report.md",
}
```

Not:

- İlk pilot sadece F10 ve F20.
- F1 ve F3 başlangıç pilotuna alınmayacak.
- Eğer F10/F20 başarılı olursa ikinci pilotta F1/F3 eklenecek.

---

## 7. `experiments/runner.py` Değişiklikleri

### 7.1 ALGO_TO_QWMO_CONFIG güncelle

Şunlar eklenecek:

```python
"QWMO_OrbitalPauli_Adaptive": "orbital_pauli_adaptive",
"QWMO_Full_Adaptive": "full_adaptive",
```

Eski aliaslar korunabilir ama yeni deneylerde kullanılmayacak.

---

### 7.2 `run_qwmo` parametre geçişi

`QWMO(...)` çağrısına ekle:

```python
adaptive_k=3,
adaptive_lambda0=0.75,
adaptive_epsilon_max_ratio=0.15,
```

Eğer `QWMO_PARAMS` merkezi kullanılıyorsa oradan geçir.

---

### 7.3 Result dict’e yeni loglar

`run_qwmo` return dict içine ekle:

```python
"epsilon_history": optimizer.epsilon_history,
"escape_executed_history": optimizer.escape_executed_history,
```

---

### 7.4 QWMO_MECHANISM_KEYS güncelle

Listeye ekle:

```python
"epsilon_history",
"escape_executed_history",
```

---

## 8. Yeni Pilot Script

Yeni dosya oluştur:

```text
experiments/gapr_pilot_validation.py
```

Bu dosya mevcut `pilot_validation.py` mantığını kopyalayabilir ama config olarak `GAPR_PILOT_CONFIG` kullanacak.

---

## 9. GAPR Pilot Pass/Fail Kriterleri

Yeni pilot raporu şu kriterleri içerecek.

### K1 — Adaptive epsilon bounded

Her adaptive run için:

```text
epsilon_min <= epsilon_history[t] <= epsilon_max
```

Başarı:

```text
Tüm adaptive runlarda PASS
```

Rapor:

```text
min_epsilon, max_epsilon, mean_epsilon
```

---

### K2 — Adaptive epsilon gerçekten değişiyor

Her adaptive run için:

```python
np.std(epsilon_history) > 1e-12
```

Başarı:

```text
Adaptive runların en az %80'inde epsilon_history std > 1e-12
```

Rapor:

```text
std(epsilon_history) mean ± std
```

---

### K3 — Adaptive epsilon static ve dynamic’ten farklı davranıyor

Karşılaştır:

```text
QWMO_OrbitalPauli_Adaptive vs QWMO_OrbitalPauli_Static
QWMO_OrbitalPauli_Adaptive vs QWMO_OrbitalPauli_Dynamic
QWMO_Full_Adaptive vs QWMO_Full_Static
QWMO_Full_Adaptive vs QWMO_Full_Dynamic
```

Başarı:

```text
En az bir fonksiyonda final fitness dizileri birebir aynı olmamalı.
```

Bu düşük seviye sanity check’tir.

---

### K4 — Adaptive Pauli aktif

Adaptive configlerde toplam displacement sayısı:

```text
sum(pauli_displacement_history) > 0
```

Başarı:

```text
Her fonksiyonda QWMO_OrbitalPauli_Adaptive veya QWMO_Full_Adaptive için displacement > 0
```

---

### K5 — Collision efficiency raporlanabilir

Her Pauli config için hesapla:

```python
CER = total_success_count / max(total_collision_count, 1)
DER = total_displacement_count / max(total_collision_count, 1)
SER = total_success_count / max(total_displacement_count, 1)
```

Tanımlar:

- `CER`: successful displacements / collisions
- `DER`: displacements / collisions
- `SER`: successful displacements / displacements

Başarı:

```text
Adaptive configlerde CER, DER, SER hesaplanabilir olmalı.
```

Bu kriter performans pass/fail değil, mekanizma raporlanabilirlik kriteridir.

---

### K6 — Full Adaptive performans sinyali

Her fonksiyon için:

```text
Full_Adaptive <= min(Full_Static, Full_Dynamic)
```

mean fitness üzerinden kontrol et.

Başarı şartı:

```text
F10 ve F20’den en az birinde Full_Adaptive, Full_Static veya Full_Dynamic’ten daha iyi ya da eşit olmalı.
```

Not:

Bu zayıf bir kriterdir. Pilotun amacı nihai üstünlük göstermek değil, sinyal aramaktır.

---

### K7 — OrbitalPauli Adaptive performans sinyali

Her fonksiyon için:

```text
OrbitalPauli_Adaptive <= OrbitalOnly
```

mean fitness üzerinden kontrol et.

Başarı şartı:

```text
F10 ve F20’den en az birinde OrbitalPauli_Adaptive, OrbitalOnly’den daha iyi ya da eşit olmalı.
```

Not:

Eğer bu sağlanmazsa GAPR tamamen reddedilmeyecek; çünkü Pauli’nin Full modelde escape ile etkileşimli etkisi ayrıca değerlendirilecek.

---

### K8 — FE budget korunuyor

Tüm runlar için:

```text
fes_count <= 300000
```

Ek uyarı:

```text
fes_count < 0.98 * 300000 ise WARN
```

---

### K9 — Diversity ve epsilon birlikte kaydediliyor

Tüm adaptive runlarda:

```text
len(diversity_history) > 0
len(epsilon_history) > 0
```

Başarı:

```text
Tüm adaptive runlarda PASS
```

---

## 10. GAPR Pilot Rapor Formatı

`gapr_pilot_validation_report.md` şu bölümleri içerecek:

```markdown
# QWMO-GAPR Pilot Validation Report

## Setup
- Functions
- Dimension
- FE budget
- Seeds
- Configs
- Adaptive parameters

## Pass/Fail Summary
K1-K9 tablo halinde

## Final Fitness Summary
mean ± std tablosu

## Epsilon Statistics
Her adaptive config için:
- min epsilon
- max epsilon
- mean epsilon
- std epsilon

## Pauli Mechanism Statistics
Her Pauli config için:
- total collisions
- total displacements
- total successes
- CER
- DER
- SER

## Escape Statistics
Her escape config için:
- attempts
- executed
- successes
- success/executed ratio
- mean delta

## Interpretation
- Adaptive epsilon çalışıyor mu?
- Full_Adaptive umut veriyor mu?
- OrbitalPauli_Adaptive tek başına katkı veriyor mu?
- Full run’a geçilsin mi?
```

---

## 11. Grafik Üretimi

Yeni dosya:

```text
analysis/gapr_plots.py
```

Üretilecek grafikler:

### 11.1 Epsilon history

Dosya adı:

```text
results/gapr_pilot/figures/epsilon_history_F10.png
results/gapr_pilot/figures/epsilon_history_F20.png
```

İçerik:

- x-axis: logged Pauli step index
- y-axis: epsilon
- curves:
  - Full_Static
  - Full_Dynamic
  - Full_Adaptive
  - OrbitalPauli_Adaptive

### 11.2 Collision/displacement/success

Dosya adı:

```text
pauli_mechanism_F10.png
pauli_mechanism_F20.png
```

Curves veya bar:

- collisions
- displacements
- successes

### 11.3 Diversity vs epsilon

Dosya adı:

```text
diversity_F10.png
epsilon_F10.png
diversity_F20.png
epsilon_F20.png
```

Not:

Grafikler sadece pilot analizi içindir; makaleye alınmadan önce tekrar düzenlenebilir.

---

## 12. Pilot Komutları

### 12.1 Smoke test

```bash
python - <<'PY'
from benchmark.cec2017 import CEC2017Benchmark
from core.qwmo import QWMO

bench = CEC2017Benchmark(10, 30)
opt = QWMO(
    func=bench,
    dimension=30,
    lower_bound=bench.lower_bound,
    upper_bound=bench.upper_bound,
    population_size=50,
    max_fes=5000,
    ablation_config="full_adaptive",
    seed=1,
)
_, fit = opt.run()
print("fit:", fit)
print("fes:", opt.fes_count)
print("epsilon_history_len:", len(opt.epsilon_history))
print("epsilon_first_last:", opt.epsilon_history[0] if opt.epsilon_history else None, opt.epsilon_history[-1] if opt.epsilon_history else None)
print("pauli_displacements:", sum(opt.pauli_displacement_history))
PY
```

Beklenen:

```text
fes <= 5000
epsilon_history_len > 0
pauli_displacements değeri raporlanır
```

---

### 12.2 GAPR pilot

```bash
python experiments/gapr_pilot_validation.py --max-workers 8
```

Beklenen çıktılar:

```text
results/gapr_pilot/gapr_pilot_D30.json
results/gapr_pilot/gapr_pilot_validation_report.md
```

---

### 12.3 Grafik üretimi

```bash
python analysis/gapr_plots.py --input results/gapr_pilot/gapr_pilot_D30.json --output-dir results/gapr_pilot/figures
```

---

## 13. Pilot Sonrası Karar Ağacı

### Durum A — Güçlü başarı

Şartlar:

- K1-K9 PASS.
- Full_Adaptive en az bir fonksiyonda Full_Static ve Full_Dynamic’ten iyi.
- Adaptive CER veya SER static/dynamic’ten daha iyi.

Karar:

```text
GAPR ana Faz-1 varyantı olarak genişletilebilir.
```

Sonraki deney:

```text
30D full CEC-standard run:
F1, F3, F5, F9, F10, F15, F20, F23, F28
Tüm algoritmalar
QWMO varyantları: OrbitalOnly, OrbitalEscape, Full_Static, Full_Dynamic, Full_Adaptive, OrbitalPauli_Adaptive
```

---

### Durum B — Mekanizma başarılı, performans karışık

Şartlar:

- K1-K5 PASS.
- Adaptive epsilon çalışıyor ve değişiyor.
- Ancak Full_Adaptive genel olarak üstün değil.

Karar:

```text
GAPR makalede mekanizma analizi / variant study olarak sunulur.
Ana algoritma Full_Static veya Full_Dynamic sonuçlara göre seçilir.
```

---

### Durum C — Başarısız

Şartlar:

- Epsilon sabitleniyor.
- Pauli displacement yok.
- Adaptive final fitness hiç farklılaşmıyor.
- FE budget bozuluyor.

Karar:

```text
GAPR ana çalışmaya alınmaz.
Future work olarak bırakılır.
Mevcut static/dynamic Faz-1 devam eder.
```

---

## 14. Makale Dili İçin Notlar

Eğer GAPR başarılı olursa kullanılacak ifade:

```text
QWMO-GAPR replaces externally scheduled exclusion radii with a population-geometry-aware Pauli radius inferred from the mean k-nearest-neighbor distance. This allows the exclusion mechanism to respond to local crowding and diversity collapse without introducing additional landscape-specific parameters.
```

Türkçe açıklama:

```text
QWMO-GAPR, dışarıdan belirlenmiş statik veya zamana bağlı exclusion radius yerine, popülasyonun anlık geometrisinden türetilen bir Pauli radius kullanır. Böylece Pauli operatörü yerel yoğunlaşmaya ve çeşitlilik kaybına daha doğal biçimde tepki verir.
```

Eğer GAPR performans olarak karışık çıkarsa kullanılacak ifade:

```text
Although GAPR produced measurable changes in exclusion activity and population geometry, its optimization benefit was function-dependent. Therefore, it is reported as an interpretable adaptive variant rather than a universally superior replacement.
```

---

## 15. Kesin Yapılmayacaklar

Bu pilotta yapılmayacak:

- Full 30D/50D/100D run.
- Tüm baseline algoritmaları tekrar çalıştırma.
- GSA ekleme.
- LSHADE-SPACMA ekleme.
- Adaptive epsilon için alpha/beta/stagnation factor ekleme.
- Epsilon parametrelerini fonksiyon bazında elle tuning etme.
- F1’de kötüleşti diye GAPR’ı hemen reddetme.
- Sadece F10’da iyi çıktı diye GAPR’ı ana algoritma ilan etme.

---

## 16. Teslim Edilecek Dosyalar

Uygulama sonrası şu dosyalar bekleniyor:

```text
operators/pauli.py
core/qwmo.py
experiments/config.py
experiments/runner.py
experiments/gapr_pilot_validation.py
analysis/gapr_plots.py
results/gapr_pilot/gapr_pilot_D30.json
results/gapr_pilot/gapr_pilot_validation_report.md
results/gapr_pilot/figures/
```

---

## 17. Final Kontrol Listesi

Kod tarafı:

- [ ] `compute_adaptive_epsilon` eklendi.
- [ ] `compute_epsilon` static/dynamic/adaptive destekliyor.
- [ ] `pauli_exclusion` adaptive mode destekliyor.
- [ ] `fes_counter` kullanılmıyor.
- [ ] FE budget sadece `_evaluate()` ile kontrol ediliyor.
- [ ] `orbital_pauli_adaptive` config çalışıyor.
- [ ] `full_adaptive` config çalışıyor.
- [ ] `epsilon_history` kaydediliyor.
- [ ] `escape_executed_history` varsa runner’a ekleniyor.
- [ ] `runner.py` adaptive configleri tanıyor.
- [ ] `GAPR_PILOT_CONFIG` eklendi.
- [ ] `gapr_pilot_validation.py` çalışıyor.
- [ ] `gapr_plots.py` çalışıyor.

Pilot tarafı:

- [ ] Smoke test geçti.
- [ ] F10/F20 pilotu tamamlandı.
- [ ] K1-K9 raporlandı.
- [ ] Epsilon history non-empty.
- [ ] Pauli mechanism stats raporlandı.
- [ ] FE budget aşılmadı.
- [ ] Pilot raporu üretildi.
- [ ] Grafikler üretildi.
- [ ] Full run’a geçilip geçilmeyeceğine karar verildi.

---

## 18. Kısa Özet

Bu işin amacı adaptive epsilon’u doğrudan “daha iyi algoritma” diye ilan etmek değildir.

Amaç:

```text
Pauli exclusion radius popülasyon geometrisine göre ayarlandığında, Pauli operatörü daha anlamlı ve ölçülebilir şekilde çalışıyor mu?
```

sorusunu test etmektir.

Bu soru pilotla cevaplanmadan GAPR ana Faz-1 deneyine taşınmayacak.
