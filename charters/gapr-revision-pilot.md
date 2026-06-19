# QWMO-GAPR Revision Pilot v2.0 — OpenCode Uygulama Yönergesi

> 📚 **Related Notes:** [[../notes/00-index|Vault Index]] · [[qwmo-gapr-test|Faz-1 Charter]] · [[../notes/04-phase1-decision|Phase-1 Decision]] · [[../notes/03-pilots-overview|Pilot History]]
>
> 📊 **Sonuç: Decision D — Stop GAPR line** (R1/R2 FAIL, R3/R4/R5 PASS)

## 0. Amaç

Bu görev, mevcut `feature/gapr` branch'indeki QWMO-GAPR kapsamlı pilot sonuçlarına dayanarak yapılacak kontrollü bir revizyon pilotudur.

Önceki comprehensive pilot sonucu:

* `Full_GAPR` içinde Pauli operatörü aktifleşti.
* `OrbitalPauli_GAPR` tek başına çoğu fonksiyonda zayıf/etkisiz kaldı.
* `Full_GAPR` 4/5 fonksiyonda rekabetçi performans gösterdi.
* Ancak adaptive epsilon hâlâ üst sınıra yakın çalıştı.
* Validation tarafında `V1` ve `V4` başarısız oldu.
* Otomatik karar `D = Stop` verdi; fakat bilimsel yorumumuz bu kararı reddediyor.
* Yeni karar: `C = Formula Revision`.

Bu revizyonun amacı:

> GAPR formülünü terk etmek değil; epsilon üst sınırını daha kontrollü hale getirerek `Full_GAPR` içindeki Pauli düzenleyici mekanizmasının daha sağlıklı çalışıp çalışmadığını test etmektir.

Bu pilot bir full benchmark değildir.

---

# 1. Yeni Bilimsel Hipotez

Eski hipotez:

> GAPR, Pauli operatörünü bağımsız bir arama operatörü olarak etkili hale getirir.

Bu hipotez kapsamlı pilotla desteklenmedi.

Yeni hipotez:

> GAPR, Escape tarafından yeniden dağıtılan popülasyon geometrisi üzerinde çalışan bir diversity-regulation mekanizmasıdır. Pauli tek başına bir arama motoru değildir; Escape ile birlikte popülasyon çeşitliliğini düzenler.

Bu nedenle bu pilotta ana odak:

```text
OrbitalPauli_GAPR
```

değil,

```text
Full_GAPR
```

olacaktır.

`OrbitalPauli_GAPR` artık başarı kriteri değildir; sadece mekanizma kanıtı olarak raporlanabilir.

---

# 2. Revizyonun Temel Kararı

Mevcut GAPR parametreleri:

```python
adaptive_lambda0 = 0.75
adaptive_epsilon_max_ratio = 0.15
epsilon_min_ratio = 0.01
adaptive_k = 3
```

Önceki pilotta epsilon çoğu zaman `epsilon_max = 30` çevresinde çalıştı.

Yeni revizyon:

```python
adaptive_epsilon_max_ratio = 0.10
```

Yani 30D ve `[-100, 100]` aralığında:

```python
epsilon_max = 0.10 * 200 = 20
```

Amaç:

* epsilon saturasyonunu azaltmak
* GAPR’ın daha hassas adaptif davranmasını sağlamak
* F10/F20 avantajı korunuyor mu görmek
* F15 bozulması azalıyor mu görmek

---

# 3. GAPR Formülü Değişmeyecek

Aşağıdaki diagonal-normalized GAPR formülü korunacaktır:

```math
epsilon_GAPR(t)
=
clip(
    lambda0
    *
    mean_d_kNN(t) / L_max
    *
    (u-l),
    epsilon_min,
    epsilon_max
)
```

Burada:

```math
L_max = sqrt(D) * (u-l)
```

Kod karşılığı:

```python
search_range = upper_bound - lower_bound
L_max = np.sqrt(dimension) * search_range

normalized_knn = mean_knn / (L_max + 1e-12)

epsilon = adaptive_lambda0 * normalized_knn * search_range

epsilon = np.clip(
    epsilon,
    epsilon_min_ratio * search_range,
    adaptive_epsilon_max_ratio * search_range
)
```

Kesinlikle eski formüle dönülmeyecek:

```python
epsilon = lambda0 * mean_knn
```

Bu yasaktır.

---

# 4. Kod Revizyonları

## 4.1 `experiments/config.py`

Yeni bir config eklenecek.

Mevcut `GAPR_COMPREHENSIVE_PILOT_CONFIG` silinmeyecek ve değiştirilmeden kalacak.

Yeni config adı:

```python
GAPR_REVISION_PILOT_CONFIG
```

İçerik:

```python
GAPR_REVISION_PILOT_CONFIG = {
    "functions": [5, 10, 15, 20, 23],
    "dimension": 30,
    "population_size": 50,
    "max_fes": 300_000,
    "seeds": list(range(1, 11)),
    "search_range": 200,
    "ablation_configs": [
        "QWMO_OrbitalEscape",
        "QWMO_Full_Static",
        "QWMO_Full_Dynamic",
        "QWMO_Full_GAPR_eps010",
    ],
    "gapr_override": {
        "adaptive_epsilon_max_ratio": 0.10,
        "adaptive_lambda0": 0.75,
        "adaptive_k": 3,
    },
    "output_dir": "results/gapr_revision_pilot_eps010",
    "json_name": "revision_pilot_results.json",
    "report_name": "revision_pilot_report.md",
    "validation_report_name": "revision_validation_report.md",
    "decision_name": "revision_decision.md",
    "summary_csv_name": "revision_summary.csv",
    "figures_subdirs": {
        "convergence": "convergence",
        "diversity": "diversity",
        "epsilon": "epsilon",
        "pauli": "pauli",
    },
}
```

Not:

* Bu pilotta `OrbitalPauli_GAPR` zorunlu değildir.
* Bu pilotun ana sorusu `Full_GAPR_eps010` davranışıdır.
* Eski comprehensive pilot dosyaları korunacak.

---

## 4.2 `core/qwmo.py`

Yeni ablation config eklenecek:

```python
"full_gapr_eps010"
```

`ABLATION_CONFIGS` içine eklenecek.

`use_pauli` içinde `full_gapr_eps010` True olmalı.

`use_escape` içinde `full_gapr_eps010` True olmalı.

`pauli_epsilon_mode` için:

```python
if "adaptive" in ablation_config or "gapr" in ablation_config:
    self.pauli_epsilon_mode = "adaptive"
```

mantığı zaten varsa çalışır. Değiştirilmeyebilir.

Ancak `full_gapr_eps010` seçildiğinde `adaptive_epsilon_max_ratio` değerinin `0.10` olarak geçirilmesi gerekir. Bunun tercihen `runner.py` tarafından yapılması beklenir.

---

## 4.3 `experiments/runner.py`

`ALGO_TO_QWMO_CONFIG` içine ekle:

```python
"QWMO_Full_GAPR_eps010": "full_gapr_eps010"
```

`run_qwmo()` fonksiyonuna opsiyonel parametre desteği ekle.

Mevcut imza örneği:

```python
def run_qwmo(self, benchmark, ablation_config='full_dynamic', seed=None):
```

Yeni imza:

```python
def run_qwmo(
    self,
    benchmark,
    ablation_config='full_dynamic',
    seed=None,
    qwmo_param_overrides=None,
):
```

İçeride default parametreleri dict olarak kur:

```python
params = {
    "gamma": 0.05,
    "c_base": 5,
    "kappa_0": 8,
    "k_s": 10,
    "eta_r": 0.001,
    "epsilon_max_ratio": 0.1,
    "epsilon_min_ratio": 0.01,
    "static_epsilon_ratio": 0.05,
    "adaptive_k": 3,
    "adaptive_lambda0": 0.75,
    "adaptive_epsilon_max_ratio": 0.15,
}
```

Sonra override uygula:

```python
if qwmo_param_overrides:
    params.update(qwmo_param_overrides)
```

Sonra `QWMO(...)` çağrısına bu parametreleri geçir.

Önemli:

* Static ve Dynamic configler bu override’dan etkilenmemeli.
* `QWMO_Full_GAPR_eps010` için `adaptive_epsilon_max_ratio=0.10` geçmeli.

Bunu iki şekilde yapabilirsin:

### Seçenek A — Script içinde override ver

Revision pilot scripti `_run_single()` sırasında config ismi `QWMO_Full_GAPR_eps010` ise:

```python
qwmo_param_overrides={
    "adaptive_epsilon_max_ratio": 0.10
}
```

geçer.

### Seçenek B — Runner içinde isimden algıla

```python
if algorithm_name == "QWMO_Full_GAPR_eps010":
    overrides = {"adaptive_epsilon_max_ratio": 0.10}
```

Tercih edilen: **Seçenek A**.

---

## 4.4 `_run_single_experiment` ve `run_single_experiment`

Mevcut runner yapısı paralel çalıştırmada override geçirmiyorsa, yeni revision pilot scripti kendi `_run_single()` fonksiyonunda doğrudan `ExperimentRunner.run_qwmo()` çağırabilir.

Yani revision pilot için genel `run_single_experiment()` zorunlu kullanılmayabilir.

Ama kod tekrarını azaltmak için şu değişiklik daha temizdir:

```python
def run_single_experiment(
    self,
    func_id,
    algorithm_name,
    seed,
    qwmo_param_overrides=None,
):
```

QWMO algoritması ise:

```python
return self.run_qwmo(
    benchmark,
    ALGO_TO_QWMO_CONFIG[algorithm_name],
    seed,
    qwmo_param_overrides=qwmo_param_overrides,
)
```

Baseline algoritmalar için override ignore edilir.

---

# 5. Yeni Script

Yeni dosya oluştur:

```text
experiments/gapr_revision_pilot.py
```

Bu script, comprehensive pilot scriptinin daha küçük ve hedeflenmiş versiyonu olacak.

## 5.1 Kapsam

Fonksiyonlar:

```python
[5, 10, 15, 20, 23]
```

Boyut:

```python
30
```

Seed:

```python
1..10
```

FE:

```python
300_000
```

Konfigürasyonlar:

```python
[
    "QWMO_OrbitalEscape",
    "QWMO_Full_Static",
    "QWMO_Full_Dynamic",
    "QWMO_Full_GAPR_eps010",
]
```

Toplam run:

```text
5 functions × 4 configs × 10 seeds = 200 runs
```

Bu pilot küçük ve hızlı olmalıdır.

---

# 6. Revision Pilot Kriterleri

Bu pilotun karar kriterleri eski G1-G5 değildir.

Yeni kriterler:

## R1 — Epsilon adaptivity

Sadece `QWMO_Full_GAPR_eps010` için hesaplanacak.

Koşul:

```python
std(epsilon_history) > 0
unique(epsilon_history) > 5
```

Başarı:

```text
En az 4/5 fonksiyonda PASS
```

---

## R2 — Saturation azalmalı

`QWMO_Full_GAPR_eps010` için:

```python
eps_max_saturation_ratio
```

hesaplanacak.

Tanım:

```python
number_of_iterations_where_epsilon_at_eps_max / total_epsilon_history_length
```

Başarı:

```text
En az 4/5 fonksiyonda ortalama eps_max_saturation_ratio < 0.50
```

Not:

Önceki comprehensive pilotta saturation problemi vardı. Bu pilotun ana amacı bunu azaltmaktır.

---

## R3 — Pauli activation korunmalı

`QWMO_Full_GAPR_eps010` için:

```python
collision_count > 0
displacement_count > 0
```

Başarı:

```text
5/5 fonksiyonda PASS
```

---

## R4 — Performance competitiveness korunmalı

`QWMO_Full_GAPR_eps010`, her fonksiyonda şu referansa göre değerlendirilecek:

```python
best_reference = min(
    mean(QWMO_Full_Static),
    mean(QWMO_Full_Dynamic)
)
```

Başarı:

```python
mean(QWMO_Full_GAPR_eps010) <= 1.05 * best_reference
```

Başarı eşiği:

```text
En az 4/5 fonksiyonda PASS
```

---

## R5 — F15 özel kontrol

Önceki pilotta F15 problemliydi.

F15 için ayrıca raporla:

```python
mean(Full_GAPR_eps010)
mean(Full_Static)
mean(Full_Dynamic)
mean(OrbitalEscape)
```

Beklenen:

```text
Full_GAPR_eps010, eski Full_GAPR v1.0'a göre daha az bozulmalı.
```

Not:

Bu script eski v1.0 sonuçlarını doğrudan bilmiyorsa bu yorumu sadece rapora “manual comparison required” olarak yaz.

---

# 7. Raporlar

Yeni script şu dosyaları üretmeli:

```text
results/gapr_revision_pilot_eps010/
    revision_pilot_results.json
    revision_pilot_report.md
    revision_validation_report.md
    revision_decision.md
    revision_summary.csv
    figures/
        convergence/
        diversity/
        epsilon/
        pauli/
```

---

## 7.1 `revision_pilot_report.md`

İçerik:

1. Setup
2. Tested configs
3. Final fitness summary
4. Full_GAPR_eps010 vs Full_Static/Full_Dynamic
5. Pauli mechanism statistics
6. Runtime statistics
7. F15 special analysis
8. Preliminary interpretation

---

## 7.2 `revision_validation_report.md`

İçerik:

1. Epsilon min/max/mean/std
2. Unique epsilon count
3. eps_max_saturation_ratio
4. eps_min_saturation_ratio
5. R1-R3 validation table

---

## 7.3 `revision_decision.md`

Şu formatta olacak:

```text
R1 PASS/FAIL
R2 PASS/FAIL
R3 PASS/FAIL
R4 PASS/FAIL
R5 OBSERVATION

FINAL DECISION:
A = Proceed to full QWMO-GAPR benchmark
B = Keep GAPR as mechanism variant
C = Further formula revision required
D = Stop GAPR line
```

Karar mantığı:

```python
if R1 and R2 and R3 and R4:
    decision = "A"
elif R1 and R3 and R4:
    decision = "B"
elif R1 and R3:
    decision = "C"
else:
    decision = "D"
```

---

# 8. Plot Scripti

Mevcut:

```text
analysis/gapr_plots.py
```

kullanılabilir.

Ancak `QWMO_Full_GAPR_eps010` configini tanıması gerekir.

Aşağıdaki plotlarda `Full_GAPR_eps010` görünmeli:

* convergence
* diversity
* epsilon
* pauli mechanism

Eğer mevcut plot scripti config listelerini hard-coded tutuyorsa şu isim eklenmeli:

```python
"QWMO_Full_GAPR_eps010"
```

---

# 9. CSV

`revision_summary.csv` şu kolonları içermeli:

```text
Function
Config
Seed
Fitness
CER
DER
SER
Runtime
EpsilonMean
EpsilonStd
EpsilonUnique
EpsMaxSaturationRatio
EpsMinSaturationRatio
```

---

# 10. Çalıştırma Komutları

VM üzerinde:

```bash
git checkout feature/gapr
git pull
```

Sonra:

```bash
python experiments/gapr_revision_pilot.py --max-workers 8
```

Grafikler:

```bash
python analysis/gapr_plots.py \
  --input results/gapr_revision_pilot_eps010/revision_pilot_results.json \
  --output-dir results/gapr_revision_pilot_eps010/figures
```

---

# 11. Smoke Test

Full pilot öncesi şu küçük test çalışmalı:

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
    ablation_config="full_gapr_eps010",
    adaptive_epsilon_max_ratio=0.10,
    seed=1,
)

_, fit = opt.run()

print("fit:", fit)
print("fes:", opt.fes_count)
print("epsilon_len:", len(opt.epsilon_history))
print("epsilon_min:", min(opt.epsilon_history) if opt.epsilon_history else None)
print("epsilon_max:", max(opt.epsilon_history) if opt.epsilon_history else None)
print("epsilon_std:", __import__("numpy").std(opt.epsilon_history) if opt.epsilon_history else None)
print("collisions:", sum(opt.pauli_collision_history))
print("displacements:", sum(opt.pauli_displacement_history))
PY
```

Beklenen:

```text
fes <= 5000
epsilon_len > 0
epsilon_max <= 20
collisions/displacements raporlanır
```

---

# 12. Yapılmayacaklar

Bu görevde yapılmayacak:

* 50D / 100D
* 30 seed
* baseline algoritmalar
* LSHADE / CMA-ES
* parametre grid search
* yeni GAPR formülü
* ACE tasarımı
* makale yazımı
* comprehensive pilot dosyasını silmek
* eski sonuçları overwrite etmek

---

# 13. Teslim Edilecekler

OpenCode uygulama sonunda şu dosyaları commit etsin:

```text
experiments/config.py
core/qwmo.py
experiments/runner.py
experiments/gapr_revision_pilot.py
analysis/gapr_plots.py
docs/GAPR_REVISION_PILOT_V2.md
```

Ve çalıştırma sonrası şu çıktı dosyalarını üretip raporlasın:

```text
results/gapr_revision_pilot_eps010/revision_pilot_results.json
results/gapr_revision_pilot_eps010/revision_pilot_report.md
results/gapr_revision_pilot_eps010/revision_validation_report.md
results/gapr_revision_pilot_eps010/revision_decision.md
results/gapr_revision_pilot_eps010/revision_summary.csv
results/gapr_revision_pilot_eps010/figures/
```

---

# 14. Final Not

Bu pilotun amacı GAPR’ı kanıtlamak değildir.

Bu pilotun amacı:

> Epsilon üst sınırı düşürüldüğünde GAPR hâlâ Full QWMO içinde Pauli aktivasyonunu koruyor mu, saturasyonu azaltıyor mu ve performans rekabetçiliğini kaybetmiyor mu?

sorusuna cevap vermektir.

Bu sorunun cevabı olumlu olursa QWMO-GAPR hattı devam eder.

Olumsuz olursa GAPR formülü yeniden tasarlanır veya ACE gibi collision-feedback tabanlı yeni bir yaklaşım değerlendirilir.
