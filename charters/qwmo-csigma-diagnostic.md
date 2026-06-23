> 📚 **Related Notes:** [[../notes/00-index|Vault Index]] · [[../notes/03-pilots-overview|Pilot History]] · [[../notes/diary/qwmo-ozet|Research Diary]]
>
> 🔒 **LOCKED PROTOCOL** — Do not modify without explicit approval.

# QWMO-Cσ Rev-Final-1.0

## Amaç

Bu deneyin amacı yeni bir optimizasyon algoritması geliştirmek değildir.

Amaç, mevcut QWMO'nun continuous-domain (sürekli uzay) performansındaki zayıflığın temel nedeninin Pauli operatörü mü yoksa zaman-bağımlı orbital daralma mekanizması mı olduğunu belirlemektir.

Bu nedenle deney yalnızca aşağıdaki hipotezi test edecektir:

> H0: Time-decay orbital mekanizmasının improvement-aware sigma ile değiştirilmesi performansta anlamlı iyileşme sağlamaz.

> H1: Time-decay orbital mekanizmasının improvement-aware sigma ile değiştirilmesi performansta anlamlı iyileşme sağlar.

Bu deneyde başka hiçbir araştırma sorusu test edilmeyecektir.

---

# Temel İlke

Deney boyunca yalnızca tek değişken değiştirilecektir.

Değiştirilecek tek bileşen:

* Orbital sigma güncelleme mekanizması

Değiştirilmeyecek bileşenler:

* Escape operatörü
* Escape parametreleri
* Escape olasılık fonksiyonu
* Pauli operatörünün eski implementasyonu
* Popülasyon büyüklüğü
* Maksimum değerlendirme sayısı
* Tüm benchmark ayarları

Amaç maksimum izolasyondur.

---

# Deney Varyantları

## 1. QWMO-Full-old

Referans algoritma.

Bileşenler:

* Orbital Sampling = Eski sürüm
* Pauli = Açık
* Escape = Açık

Makaledeki orijinal implementasyon kullanılacaktır.

Bu varyant benchmark referansı olarak kullanılacaktır.

---

## 2. QWMO-E-old

Pauli kaldırılmış sürüm.

Bileşenler:

* Orbital Sampling = Eski sürüm
* Pauli = Kapalı
* Escape = Açık

Amaç:

Pauli'nin gerçek katkısını görmek.

---

## 3. QWMO-Cσ

Yeni deneysel sürüm.

Bileşenler:

* Orbital Sampling = Improvement-Aware Sigma
* Pauli = Kapalı
* Escape = Açık

QWMO-Cσ dışındaki hiçbir bileşen değiştirilmeyecektir.

---

# Test Fonksiyonları

Yalnızca aşağıdaki üç fonksiyon kullanılacaktır.

## F1 Sphere

Amaç:

* Hassas yakınsama
* Exploitation testi

---

## F5 Schwefel

Amaç:

* Deceptive landscape testi
* Global arama kapasitesi

---

## F10 Rastrigin

Amaç:

* Multimodal yapı
* Escape etkinliği

---

# Ortak Deney Parametreleri

Tüm varyantlarda aynı parametreler kullanılacaktır.

Boyut:

```text
D = 30
```

Popülasyon:

```text
N = 50
```

Run sayısı:

```text
Runs = 30
```

Maksimum değerlendirme:

```text
Tmax = 300000
```

Seed listesi:

```text
Aynı seed listesi tüm varyantlarda kullanılacaktır.
```

Seed farklılaştırılmayacaktır.

---

# QWMO-Cσ Sigma Mekanizması

Bu bölüm yalnızca QWMO-Cσ için geçerlidir.

---

## Adım 1

Yeni aday değerlendirildikten sonra:

```text
f_old
f_new
```

değerleri alınacaktır.

---

## Adım 2

Popülasyonun mevcut en iyi ve en kötü fitness değerleri hesaplanacaktır.

```text
f_best
f_worst
```

---

## Adım 3

Güvenli payda oluşturulacaktır.

```text
denom =
max(
    f_worst - f_best,
    1e-8 * (abs(f_best) + 1)
)
```

Bu koruma zorunludur.

Amaç:

* Bölme hatalarını önlemek
* Popülasyon çöküşünde kararlılığı korumak

---

## Adım 4

Ham iyileşme oranı:

```text
r_raw =
(f_old - f_new) / denom
```

---

## Adım 5

İyileşme oranı sınırlandırılacaktır.

```text
r_i =
tanh(r_raw)
```

Bu işlem zorunludur.

Sonuç:

```text
r_i ∈ [-1,1]
```

garantisi sağlanacaktır.

---

# Dinamik Tau Hesabı

Her iterasyonda:

Pozitif iyileşme değerleri:

```text
r_i > 0
```

olan ajanlar alınacaktır.

Bu kümenin medyanı hesaplanacaktır.

```text
median_positive_r
```

Daha sonra:

```text
tau =
max(
    1e-6,
    1e-3 * median_positive_r
)
```

hesaplanacaktır.

Eğer pozitif iyileşme yoksa:

```text
tau = 1e-6
```

kullanılacaktır.

---

# Sigma Güncellemesi

## Başarılı ajan

Eğer:

```text
r_i > tau
```

ise:

```text
sigma_i =
sigma_i * (1 - 0.01 * r_i)
```

ve:

```text
k_i = 0
```

olacaktır.

---

## Başarısız veya stagnation ajanı

Eğer:

```text
r_i <= tau
```

ise:

```text
sigma_i =
sigma_i * (1 + 0.01)
```

ve:

```text
k_i = k_i + 1
```

olacaktır.

---

# Sigma Sınırları

Her güncelleme sonrasında:

```text
sigma_i =
clip(
    sigma_i,
    1e-10,
    sigma_max_i
)
```

uygulanacaktır.

Alt sınır:

```text
sigma_min = 1e-10
```

Sabit tutulacaktır.

---

# Escape Operatörü

Bu deneyde Escape operatörüne DOKUNULMAYACAKTIR.

Aşağıdakiler kesinlikle değiştirilmeyecektir:

* Escape denklemleri
* Escape olasılığı
* Escape parametreleri
* Escape eşikleri
* Escape zaman bağımlılığı

Amaç:

Sigma değişikliğinin etkisini izole etmektir.

---

# Pauli Operatörü

QWMO-Cσ ve QWMO-E-old için:

```text
Pauli = OFF
```

olacaktır.

QWMO-Full-old için:

```text
Pauli = ON
```

olacaktır.

Başka varyant oluşturulmayacaktır.

---

# Toplanacak Metrikler

Her varyant için:

## Temel Sonuçlar

```text
Best Fitness
Mean Fitness
Median Fitness
Standard Deviation
```

---

## İstatistiksel Analiz

```text
Wilcoxon Signed-Rank Test
Cliff's Delta
```

---

## Tanısal Metrikler

```text
Mean Sigma
Median Sigma
Escape Count
Stagnation Count
Convergence Curve
Best-So-Far Curve
```

---

# Başarı Kriterleri

## Güçlü Başarı

Aşağıdaki üç koşul birlikte sağlanmalıdır:

### Sphere

QWMO-Cσ

hem:

```text
QWMO-Full-old
```

hem:

```text
QWMO-E-old
```

üzerinde belirgin iyileşme göstermelidir.

---

### Rastrigin

QWMO-Cσ

QWMO-Full-old performansını korumalıdır.

Ciddi bozulma kabul edilmez.

---

### Schwefel

QWMO-Cσ

QWMO-E-old'dan kötü olmamalıdır.

---

# Karar Ağacı

## Senaryo A

Sphere iyileşir

Rastrigin korunur

Schwefel korunur

Karar:

```text
QWMO-C hattı devam eder.
```

---

## Senaryo B

Sphere iyileşir

Rastrigin bozulur

Karar:

```text
Escape-Sigma etkileşimi araştırılır.
```

---

## Senaryo C

Sphere iyileşmez

Karar:

```text
QWMO-C başarısız kabul edilir.
```

---

## Senaryo D

QWMO-E-old ≈ QWMO-Full-old

Karar:

```text
Pauli continuous-domain için gereksiz kabul edilir.
```

---

## Senaryo E

QWMO-Cσ

E-old'u geçer

ancak

Full-old'u geçemez

Karar:

```text
Sinyal zayıftır.

QWMO-C hattının devamı için ek kanıt gerekir.
```

---

# Yasaklar

Bu deney sırasında:

* Yeni Pauli tasarımı yapılmayacaktır.
* Density Pauli denenmeyecektir.
* Wave Interference eklenmeyecektir.
* Archive sistemi eklenmeyecektir.
* Failure Archive eklenmeyecektir.
* Yeni Escape tasarımı yapılmayacaktır.
* Yeni hiperparametre optimizasyonu yapılmayacaktır.
* QWMO-D çalışmalarına geçilmeyecektir.

Bu deney tamamlanmadan yeni tasarım tartışması açılmayacaktır.

---

# Nihai Karar

Bu protokol:

```text
QWMO-Cσ Rev-Final-1.0
```

olarak kilitlenmiştir.

Bu aşamadan sonra yapılacak tek iş:

```text
KODLA
ÇALIŞTIR
RAPORLA
```

Veri konuşacaktır.
