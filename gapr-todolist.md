# QWMO-GAPR Comprehensive Pilot v1.0

## Amaç

Bu çalışma bir makale yazma çalışması değildir.

Bu çalışma, QWMO içerisindeki Pauli Exclusion operatörünün Geometry-Adaptive Pauli Radius (GAPR) ile yeniden tasarlanmasının bilimsel olarak anlamlı olup olmadığını belirlemek için hazırlanmış kapsamlı bir pilot çalışmadır.

Bu aşamadaki temel araştırma sorusu:

> "Geometry-Adaptive Pauli Radius (GAPR), yüksek boyutlu optimizasyonda Pauli Exclusion operatörünü gerçekten işlevsel hale getiriyor mu?"

Amaç:

* GAPR fikrini doğrulamaya çalışmak değil,
* GAPR fikrini zorlamak,
* Mekanizmanın gerçekten çalışıp çalışmadığını anlamak,
* Full benchmark ve makale aşamasına geçmeden önce karar verebilmek.

---

# 1. Araştırma Arka Planı

## QWMO v1 (Preprint)

İlk QWMO çalışmasında Pauli Exclusion operatörü statik epsilon kullanıyordu.

Örnek:

```python
epsilon = constant
```

Ablasyon sonuçları gösterdi ki:

* Orbital + Escape ≈ Full QWMO
* Orbital + Pauli ≈ Orbital Only

Dolayısıyla Pauli operatörü pratikte anlamlı katkı sağlamıyordu.

---

## Dinamik Epsilon

İlk hipotez:

> Pauli operatörü çalışmıyorsa sebebi statik epsilon olabilir.

Bu nedenle lineer azalan epsilon geliştirildi.

```math
\epsilon(t)
=
\epsilon_{max}
\left(
1-\frac{t}{T_{max}}
\right)
+
\epsilon_{min}
```

Sonuç:

* Pauli artık aktifleşti
* Collision üretti
* Displacement üretti

Ancak performans katkısı sınırlı kaldı.

---

## GAPR

Yeni hipotez:

> Epsilon zamana göre değil, popülasyon geometrisine göre değişmelidir.

Bu nedenle Geometry-Adaptive Pauli Radius (GAPR) geliştirildi.

---

# 2. GAPR Teknik Spesifikasyonu

## Amaç

Statik exclusion radius problemini çözmek.

Eski yapı:

```python
epsilon = constant
```

Dinamik yapı:

```python
epsilon = f(time)
```

Yeni yapı:

```python
epsilon = f(population_geometry)
```

---

# 3. Nihai GAPR Formülü

Her iterasyonda:

```math
\epsilon_{GAPR}(t)
=
clip
\left(
\lambda_0
\cdot
\frac{\bar d_{kNN}(t)}
{L_{max}}
\cdot
(u-l),
\epsilon_{min},
\epsilon_{max}
\right)
```

Burada:

```math
\bar d_{kNN}(t)
```

=
ortalama k-en-yakın komşu mesafesi

---

```math
L_{max}
=
\sqrt D
\cdot
(u-l)
```

=
arama uzayının köşegen uzunluğu

---

## Varsayılan Parametreler

```python
lambda0 = 0.75

k = 3

eps_min_ratio = 0.01

eps_max_ratio = 0.15
```

---

## Referans Implementasyon

```python
search_range = upper_bound - lower_bound

L_max = np.sqrt(dimension) * search_range

normalized_knn = mean_knn / L_max

epsilon = (
    lambda0
    * normalized_knn
    * search_range
)

epsilon = np.clip(
    epsilon,
    eps_min_ratio * search_range,
    eps_max_ratio * search_range
)
```

---

# 4. Yasaklanan Eski Formül

Aşağıdaki formül kullanılmayacaktır:

```python
epsilon = lambda0 * mean_knn
```

Sebep:

İlk pilotta epsilon sürekli epsilon_max değerine saturasyon göstermiştir.

Bu bug tekrar üretilmemelidir.

---

# 5. KDTree Gereksinimi

Mesafe hesaplamaları için:

```python
scipy.spatial.cKDTree
```

kullanılacaktır.

Her iterasyonda:

```python
tree.query(...)
```

kullanılarak kNN hesaplanacaktır.

Brute-force distance matrix kullanılmayacaktır.

---

# 6. Test Fonksiyonları

Pilot yalnızca aşağıdaki fonksiyonlarda yapılacaktır.

| Fonksiyon | Kategori               |
| --------- | ---------------------- |
| F5        | Multimodal             |
| F10       | Multimodal (Rastrigin) |
| F15       | Hybrid                 |
| F20       | Hybrid                 |
| F23       | Composition            |

Fonksiyon listesi sabittir.

---

# 7. Boyut

Yalnızca:

```text
30D
```

kullanılacaktır.

50D ve 100D bu pilotun kapsamı dışındadır.

---

# 8. Seed Sayısı

Her konfigürasyon:

```text
15 bağımsız seed
```

ile çalıştırılacaktır.

Önerilen:

```python
seed = 1..15
```

---

# 9. FE Bütçesi

Her çalışma:

```text
300,000 Function Evaluations
```

ile sınırlandırılacaktır.

Tüm konfigürasyonlar aynı FE bütçesine sahip olmak zorundadır.

---

# 10. Test Edilecek Konfigürasyonlar

## Baseline

```text
OrbitalOnly
OrbitalEscape
```

## Pauli Evrimi

```text
OrbitalPauli_Static
OrbitalPauli_Dynamic
OrbitalPauli_GAPR
```

## Full Sistem

```text
Full_Static
Full_Dynamic
Full_GAPR
```

Bu liste değiştirilmeyecektir.

---

# 11. Toplanacak Veriler

Her run için:

## Performans

```text
best_fitness
fitness_history
```

## Diversity

```text
diversity_history
```

Tanım:

```text
mean pairwise Euclidean distance
```

---

## Adaptive GAPR

```text
epsilon_history
mean_knn_history
normalized_knn_history
```

---

## Pauli

```text
collision_count
displacement_count
success_count

collision_history
displacement_history
success_history
```

---

## Escape

```text
escape_attempts
escape_executed
escape_successes
```

---

## Runtime

```text
cpu_time_seconds
```

---

# 12. Türetilmiş Metrikler

## CER

Collision Efficiency Ratio

```math
CER
=
\frac{success\_count}
{collision\_count}
```

---

## DER

Displacement Efficiency Ratio

```math
DER
=
\frac{displacement\_count}
{collision\_count}
```

---

## SER

Success Efficiency Ratio

```math
SER
=
\frac{success\_count}
{displacement\_count}
```

---

## Activation Ratio

```math
AR
=
\frac{displacement\_count}
{collision\_count}
```

---

# 13. GAPR Validasyon Testleri

Her adaptive run sonunda otomatik kontrol yapılacaktır.

## V1

```python
std(epsilon_history) > 0
```

---

## V2

```python
min(epsilon_history) >= eps_min
```

---

## V3

```python
max(epsilon_history) <= eps_max
```

---

## V4

```python
unique(epsilon_history) > 5
```

Amaç:

Epsilon'ın gerçekten değiştiğini doğrulamak.

---

# 14. Üretilecek Grafikler

## Convergence Curves

```text
Best Fitness vs Iteration
```

---

## Diversity Curves

```text
Diversity vs Iteration
```

---

## Adaptive Epsilon Curves

```text
Epsilon vs Iteration
```

---

## Pauli Efficiency

```text
CER
DER
SER
```

bar chart

---

# 15. Go / No-Go Kriterleri

## G1

Adaptive epsilon gerçekten değişmelidir.

```python
std(epsilon_history) > 0
```

---

## G2

Pauli aktif olmalıdır.

```python
collision_count > 0

displacement_count > 0
```

---

## G3

Pauli verimliliği artmalıdır.

Beklenen:

```text
SER_GAPR > SER_Static
```

en az 3 fonksiyonda.

---

## G4

Performans sinyali oluşmalıdır.

Beklenen:

```text
Full_GAPR
```

en az

```text
3/5 fonksiyonda
```

Full_Static veya Full_Dynamic ile rekabetçi olmalıdır.

---

## G5

Pauli evrimi gözlenmelidir.

Beklenen:

```text
OrbitalPauli_GAPR
>
OrbitalPauli_Dynamic
>
OrbitalPauli_Static
```

özellikle:

* Collision
* Displacement
* SER

metriklerinde.

---

# 16. Çıktı Klasör Yapısı

```text
results/

gapr_comprehensive_pilot/

    pilot_results.json

    pilot_report.md

    pilot_decision.md

    validation_report.md

    figures/

        convergence/

        diversity/

        epsilon/

        pauli/
```

---

# 17. Zorunlu Kod Validasyonları

Pilot çalıştırılmadan önce:

* Adaptive epsilon unit test
* KDTree test
* Bounds test
* Saturation regression test

başarılı olmak zorundadır.

---

# 18. validation_report.md

Aşağıdaki bilgiler zorunlu olarak üretilecektir.

```text
epsilon min
epsilon max
epsilon mean
epsilon std

unique epsilon count

mean knn
normalized knn

collision count
displacement count
success count
```

---

# 19. pilot_decision.md

Son rapor aşağıdaki formatta oluşturulacaktır.

```text
G1 PASS/FAIL
G2 PASS/FAIL
G3 PASS/FAIL
G4 PASS/FAIL
G5 PASS/FAIL

FINAL DECISION:

A = Full Benchmark
B = Mechanism Paper
C = Formula Revision
D = Stop
```

---

# 20. Başarı Tanımı

Bu pilotun amacı:

> "GAPR daha iyi skor aldı"

demek değildir.

Bu pilotun amacı:

> "Pauli operatörü gerçekten yeniden işlevsel hale geldi mi?"

sorusuna cevap vermektir.

Bu soru olumlu cevaplanırsa:

```text
QWMO-GAPR
```

full benchmark ve makale aşamasına geçecektir.
