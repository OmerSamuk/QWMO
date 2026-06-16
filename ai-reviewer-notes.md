Genel olarak **opencode’un planını onaylıyorum**. Hatta önceki analizlerimize göre oldukça isabetli toparlamış. Mevcut repo + ilk 30D run + log anomalileri dikkate alındığında bu plan doğru sıraya sahip: önce implementasyon güvenilirliği, sonra pilot doğrulama, sonra full/long-budget deney.

Puanım: **9.1 / 10**

Ama **3 noktada revizyon şartı** koyarım.

---

## 1. En büyük itirazım: Pauli sonrası fitness evaluation doğrudan kabul edilmeli ama “FE bütçesi” dikkatle korunmalı

Plan, `pauli_exclusion(agents, func, fes_counter, ...)` diyerek Pauli sonrası fitness değerlendirmesi eklemeyi öneriyor. Bu doğru; çünkü önceki kodda Pauli pozisyonu değiştiriyor ama fitness eski kalıyordu. Bu, OrbitalOnly ile OrbitalPauli’nin birebir aynı çıkmasının en güçlü açıklamasıydı.

Ancak burada kritik risk var:

> Pauli her collision için yeni evaluation yaparsa QWMO diğer algoritmalardan daha fazla FE tüketebilir veya orbital iterasyon sayısı azalır.

Bu yüzden sadece `fes_counter[0] += 1` yetmez. Mutlaka şu kontrol olmalı:

```python
if fes_counter[0] >= max_fes:
    break
```

Yani `pauli_exclusion` imzası bence şöyle olmalı:

```python
pauli_exclusion(
    agents,
    func,
    fes_counter,
    max_fes,
    rng,
    t,
    T_max,
    lower_bound,
    upper_bound,
    epsilon_mode="dynamic",
    epsilon_max_ratio=0.1,
    epsilon_min_ratio=0.01,
    static_epsilon_ratio=0.05,
)
```

Aksi halde düzeltme yeni bir adaletsizlik doğurabilir.

---

## 2. RNG revizyonu doğru ama tüm operatörlere açıkça geçirilmeli

`np.random.seed(seed)` yerine `self.rng = np.random.default_rng(seed)` geçişi doğru. Bu, multiprocessing altında daha temiz ve reproducible olur.

Ama plan “tüm `np.random.*` çağrılarını `self.rng.*`’ye çevir” diyor. Bu eksik uygulanırsa sonuçlar tekrar karışır.

Özellikle şu dosyalar tam kontrol edilmeli:

* `core/qwmo.py`
* `operators/orbital.py`
* `operators/pauli.py`
* `operators/escape.py`
* `baselines/aso.py`
* `baselines/aos.py`
* `baselines/qpso.py`

QWMO için RNG düzeltmek yetmez; kendi yazdığımız ASO/AOS/QPSO da seed determinism açısından kontrol edilmeli.

---

## 3. `epsilon_r` kaldırılması doğru, ama geriye dönük uyumluluk için dikkat

Plan, `epsilon_r` planda olmadığı için kaldırmayı öneriyor. Bunu **onaylıyorum**. Ölü kod temizliği doğru.

Fakat eski config veya scriptler `epsilon_r` geçiriyorsa `TypeError` verir. Bu yüzden ya tüm referanslar temizlenmeli ya da geçici olarak şu yapılmalı:

```python
def __init__(..., epsilon_r=None, ...):
    # deprecated, ignored
```

Benim önerim:

* Faz-1 branch’inde tamamen kaldır.
* README/changelog’a yaz:

  > `epsilon_r` was removed as unused/deprecated.

Bu daha temiz.

---

# Planın güçlü tarafları

## Aşama 1 doğru önceliklendirilmiş

Plan önce şu kritik hataları düzeltiyor:

* Pauli sonrası fitness evaluation
* Escape `kappa_0` / `k_s` ayrımı
* FE budget wrapper
* RNG determinism
* mechanism logs
* A12 minimization yönü
* global Friedman rank analizi
* GSA ekleme veya baseline genişletme

Bunlar doğrudan önceki analizlerde tespit ettiğimiz ana sorunlardı. Plan dosyasında da bu maddeler net şekilde sıralanmış. 

## Aşama 2 pilot doğrulama çok doğru

Özellikle şu pilot set mükemmel seçilmiş:

* F1
* F3
* F10
* F20
* 30D
* seed 1–10
* 300k FE
* 6 QWMO konfigürasyonu

Bu, tam koşuya geçmeden önce doğru soruları yanıtlar:

1. Pauli gerçekten aktif mi?
2. Static vs dynamic epsilon fark yaratıyor mu?
3. Escape F1’i hâlâ bozuyor mu?
4. Full dynamic gerçekten Full static’ten farklı mı?

Bu pilot olmadan full run tekrar etmek zaman kaybı olur.

---

# Revize edilmesi gereken ayrıntılar

## 1. Ablation isimleri daha net olmalı

Plan şunları söylüyor:

* OrbitalOnly
* OrbitalPauli-static
* OrbitalPauli-dynamic
* OrbitalEscape
* Full-static
* Full-dynamic

Bunu kesinlikle koru. JSON’da da isimler böyle olmalı:

```text
QWMO_OrbitalOnly
QWMO_OrbitalPauli_Static
QWMO_OrbitalPauli_Dynamic
QWMO_OrbitalEscape
QWMO_Full_Static
QWMO_Full_Dynamic
```

Eski `QWMO_Full` belirsiz kalıyor. Bundan sonra `QWMO_Full` yerine açıkça `QWMO_Full_Dynamic` kullanılmalı.

---

## 2. Pauli logları yetersiz kalmasın

Sadece `collision_count` yetmez. En az şu üç metrik kaydedilmeli:

```python
pauli_collision_count
pauli_displacement_count
pauli_success_count
```

Burada:

* collision_count: epsilon mesafesinde bulunan çift sayısı
* displacement_count: gerçekten yer değiştirilen ajan sayısı
* success_count: Pauli sonrası fitness iyileşen ajan sayısı

Bu özellikle önemli. Çünkü Pauli agent’ı hareket ettirip kötüleştiriyor olabilir.

---

## 3. Escape logları da “başarı” bilgisini içermeli

Plan “activations_list” diyor ama bu tek başına yetersiz.

Şunlar olmalı:

```python
escape_attempt_count
escape_success_count
escape_mean_delta
escape_phase_counts
```

Phase:

* early: `t/T_max < 0.33`
* mid: `0.33 <= t/T_max < 0.66`
* late: `>= 0.66`

Böylece Q1 makalede escape operatörü gerçekten analiz edilebilir.

---

## 4. A12 düzeltmesi kesinlikle yapılmalı

Plan A12 yönünü düzeltmeyi yazmış. Bunu çok güçlü onaylıyorum.

Minimization için:

```python
if xi < yj:
    r1 += 1
elif xi == yj:
    r1 += 0.5
```

Çıktı adı da şöyle olmalı:

```text
A12_QWMO_better
```

Yoksa tablo yine yanlış yorumlanır.

---

## 5. GSA ekleme iyi ama geciktirilebilir

Plan `BASELINE_ALGORITHMS`’a GSA eklemeyi öneriyor. Akademik olarak doğru.

Ama pratikte şu riski var:

* mealpy import yolu değişebilir
* GSA beklenenden yavaş olabilir
* yeni baseline debugging’i Aşama 1’i uzatabilir

Benim önerim:

**Aşama 1A:** QWMO çekirdeğini düzelt.
**Aşama 1B:** GSA ekle.

GSA yüzünden Pauli/escape düzeltmeleri gecikmemeli.

---

# En önemli eksik: test kriterleri daha sayısal olmalı

Plan “fark var mı?” diyor. Bu biraz belirsiz. Pilot doğrulama için net pass/fail kriterleri koymalıyız.

Benim önerim:

## Pilot pass/fail kriterleri

### Kriter 1 — Pauli aktifliği

```text
mean(pauli_displacement_count) > 0
```

F10 veya F20 üzerinde en azından bazı runlarda sıfırdan büyük olmalı.

### Kriter 2 — Pauli sonuç etkisi

```text
OrbitalPauli_Dynamic ile OrbitalOnly final fitness dizileri birebir aynı olmamalı.
```

Bu minimum sanity check.

### Kriter 3 — Dynamic epsilon farkı

```text
OrbitalPauli_Static ile OrbitalPauli_Dynamic final fitness dizileri birebir aynı olmamalı.
```

### Kriter 4 — Escape başarı oranı

```text
escape_success_count / escape_attempt_count raporlanabilir olmalı.
```

Yani attempt > 0 ve success metrikleri dolu olmalı.

### Kriter 5 — FE budget

Her run için:

```text
fes_count <= max_fes
```

ve mümkünse:

```text
fes_count >= 0.98 * max_fes
```

Aksi halde algoritmalar bütçeyi adil kullanmıyor olabilir.

---

# Benim revize nihai önerim

Opencode planını şu küçük düzenlemeyle uygula:

## Aşama 1A — QWMO core fix

1. `epsilon_r` kaldır.
2. `rng` mimarisine geç.
3. `_evaluate()` wrapper ekle.
4. Escape `kappa_0` / `k_s` ayrımını düzelt.
5. Pauli sonrası fitness evaluation ekle.
6. FE budget guard ekle.
7. Pauli ve escape success loglarını ekle.

## Aşama 1B — analysis fix

1. A12 minimization yönünü düzelt.
2. Per-function Wilcoxon + A12 raporu üret.
3. Dimension-level Friedman + Holm global rank analizi ekle.
4. Results JSON’a mechanism logs kaydet.

## Aşama 1C — experiment config

1. Ablation isimlerini static/dynamic olarak ayır.
2. Pilot validation config ekle.
3. GSA’yı ekle ama QWMO core fix’ten sonra.
4. `QWMO_Full` eski adını deprecated yap.

## Aşama 2 — pilot validation

Fonksiyonlar:

```text
F1, F3, F10, F20
```

Konfigürasyonlar:

```text
QWMO_OrbitalOnly
QWMO_OrbitalPauli_Static
QWMO_OrbitalPauli_Dynamic
QWMO_OrbitalEscape
QWMO_Full_Static
QWMO_Full_Dynamic
```

Seeds:

```text
1–10
```

FE:

```text
300,000
```

Çıktı:

```text
results/pilot_D30.json
results/pilot_validation_report.md
```

---

# Nihai hüküm

**Onaylıyorum.**

Bu plan, bizim önceki eleştirilerimizin yaklaşık %85–90’ını doğru yakalamış. En önemli eksiği, Pauli ve escape loglarını sadece “count” düzeyinde değil, **success/effect** düzeyinde zorunlu tutmaması.

Benim notum:

**Mevcut opencode planı:** 9.1/10
**Benim revizyonlarımla:** 9.6/10

Özellikle şu üç madde eklenirse plan çok sağlam olur:

1. Pauli için `collision/displacement/success` üçlü logu
2. Escape için `attempt/success/delta/phase` logu
3. Pilot validation için sayısal pass/fail kriterleri

Bunlarla beraber uygulamaya geçilebilir.
