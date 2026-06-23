# QWMO-GAPR Faz-1 Final Charter v1.0

> 📚 **Related Notes:** [[../notes/00-index|Vault Index]] · [[../notes/04-phase1-decision|Phase-1 Decision]] · [[../notes/diary/phase1-audit|Phase-1 Audit]] · [[../notes/03-pilots-overview|Pilot History]]
>
> 🔒 **LOCKED PROTOCOL** — Do not modify without explicit approval.

## Belge Amacı

Bu dosya, QWMO-GAPR araştırma hattında **Faz-1 deneylerinin eksiksiz, tekrarlanabilir ve tartışmasız biçimde yürütülmesi** için hazırlanmış uygulama planıdır.

Bu belgeyi okuyacak model, ajan veya geliştirici aşağıdaki ilkeye kesin olarak uymalıdır:

> **Faz-1 bir algoritma geliştirme fazı değildir. Faz-1 bir karar fazıdır.**

Bu fazda yeni formül icat edilmeyecek, yeni parametre araması yapılmayacak, sonuç kötü geldikçe deney protokolü değiştirilmeyecektir. Amaç, mevcut GAPR Final varyantının Pauli/adaptive epsilon problemini gerçekten çözüp çözmediğine karar vermektir.

---

# 1. Araştırma Bağlamı

QWMO algoritması üç ana operatörden oluşur:

1. Adaptive Orbital Sampling
2. Pauli-Inspired Exclusion
3. Adaptive Quantum Escape

İlk ablation sonuçları, Pauli operatörünün özellikle yüksek boyutlu optimizasyon ortamlarında beklenen katkıyı üretmediğini göstermiştir. Daha sonra Dynamic Epsilon ve GAPR varyantları geliştirilmiş, bu varyantların Pauli aktivasyonunu artırabildiği görülmüştür.

Ancak önceki deneylerin temel bulgusu şudur:

> **Pauli aktivasyonu artabilir; fakat bu artış fitness kazanımına dönüşmeyebilir.**

Bu nedenle Faz-1’in ana bilimsel sorusu şudur:

> **GAPR, Pauli operatörünü yalnızca aktive mi ediyor, yoksa bu aktivasyonu gerçek optimizasyon performansına dönüştürüyor mu?**

---

# 2. Faz-1 Hipotezleri

## H0 — Null Hipotez

Pauli aktivasyonundaki artış, yüksek boyutlu multimodal optimizasyonda sistematik fitness artışına dönüşmez.

## H1 — Alternatif Hipotez

Pauli aktivasyonundaki artış, belirli multimodal/hybrid rejimlerde sistematik fitness artışına dönüşür.

---

# 3. Faz-1 Sonunda Verilecek Kararlar

Faz-1 sonunda yalnızca aşağıdaki üç karardan biri verilecektir.

## Karar A — GAPR Ana Algoritmaya Girer

GAPR Final varyantı:

- Orbital + Escape varyantını geçer,
- Static QWMO varyantını geçer,
- Dynamic Epsilon varyantını geçer,
- en az F20 veya F10 üzerinde istatistiksel/pratik üstünlük gösterir.

Bu durumda Faz-2 tıbbi/radiomics uygulamasına **QWMO-GAPR** ile geçilir.

## Karar B — GAPR Niş Mekanizma Olarak Kalır

GAPR Final varyantı:

- Static QWMO’yu bazı fonksiyonlarda geçer,
- Dynamic Epsilon’a yakın veya sınırlı üstünlük gösterir,
- ancak Orbital + Escape varyantını net biçimde geçemez.

Bu durumda GAPR makalede ana algoritma değil, **sınırlı rejim avantajı / mekanizma katkısı** olarak sunulur.

## Karar C — GAPR Ana Hattan Çıkar

GAPR Final varyantı:

- collision/displacement sayısını artırır,
- diversity değerini artırır veya değiştirir,
- fakat fitness performansına anlamlı katkı üretmez,
- Orbital + Escape varyantını geçemez.

Bu durumda GAPR ana algoritmadan çıkarılır. Bulgular, **“Activation ≠ Utility”** ilkesi çerçevesinde Discussion/Future Work bölümüne taşınır.

---

# 4. Kesin Yasaklar

Faz-1 süresince aşağıdaki işlemler yapılmayacaktır:

- Yeni epsilon formülü tasarlamak
- Yeni GAPR formülü tasarlamak
- SoftClip varyantı eklemek
- Rank-based yeni varyant eklemek
- Yeni lambda araması yapmak
- Yeni kNN yoğunluk tanımı eklemek
- Yeni Pauli displacement formülü denemek
- Yeni escape formülü denemek
- 50D deney eklemek
- Sonuç kötü geldikçe protokol değiştirmek
- Fonksiyon listesini değiştirmek
- Run sayısını değiştirmek
- Varyant listesini değiştirmek
- Başarı kriterlerini deney sonrası değiştirmek

---

# 5. Deney Matrisi

## 5.1 Fonksiyonlar

Faz-1’de yalnızca aşağıdaki dört fonksiyon kullanılacaktır.

| Kod | Fonksiyon | Rol |
|---|---|---|
| F20 | Hybrid | Birincil karar fonksiyonu |
| F10 | Rastrigin | İkincil karar fonksiyonu |
| F5 | Schwefel | Yardımcı gözlem fonksiyonu |
| F28 | Composition | Zor referans fonksiyonu |

## 5.2 Boyut

Tüm deneyler:

```text
D = 30
```

olarak yürütülecektir.

50D deney **yapılmayacaktır**.

## 5.3 Run Sayısı

Her fonksiyon/varyant kombinasyonu için:

```text
30 bağımsız run
```

yapılacaktır.

## 5.4 Seed Kullanımı

Tüm varyantlar aynı seed listesiyle çalıştırılacaktır.

Örnek seed listesi:

```text
0, 1, 2, ..., 29
```

veya daha önce projede kullanılan sabit seed listesi.

Önemli olan, aynı fonksiyon için tüm varyantların aynı seed’lerle çalıştırılmasıdır.

## 5.5 Popülasyon

```text
N = 50
```

olarak sabitlenecektir.

## 5.6 FE / Iterasyon Bütçesi

Tüm varyantlarda aynı fonksiyon değerlendirme bütçesi kullanılacaktır.

Varsayılan:

```text
Tmax = 300000
```

Eğer kod tabanı iterasyon sayısı üzerinden çalışıyorsa, tüm varyantların toplam fonksiyon değerlendirme sayısı eşitlenmelidir.

## 5.7 Toplam Deney Sayısı

```text
4 fonksiyon × 4 varyant × 30 run = 480 run
```

Bu sayı sabittir.

---

# 6. Test Edilecek Varyantlar

Faz-1’de yalnızca dört varyant test edilecektir.

## V0 — Orbital + Escape

Pauli operatörü kapalıdır.

Kullanılan operatörler:

- Adaptive Orbital Sampling
- Adaptive Quantum Escape

Kullanılmayan operatör:

- Pauli-Inspired Exclusion

Amaç:

> Escape mekanizmasının tek başına ne kadar güçlü olduğunu ölçmek.

Bu varyant gerçeklik kontrolüdür. GAPR, V0’ı geçemiyorsa ana algoritma olamaz.

---

## V1 — Static QWMO

Orijinal QWMO varyantıdır.

Kullanılan operatörler:

- Adaptive Orbital Sampling
- Static Pauli-Inspired Exclusion
- Adaptive Quantum Escape

Epsilon:

```text
epsilon_r = 0.05
```

Amaç:

> Orijinal sabit epsilon yaklaşımına karşı GAPR’ın katkısını ölçmek.

---

## V2 — Dynamic Epsilon QWMO

Zamana bağlı epsilon kullanan QWMO varyantıdır.

Epsilon formülü:

```text
epsilon(t) = epsilon_max * (1 - t / Tmax) + epsilon_min
```

Önerilen parametreler:

```text
epsilon_max_r = 0.10
epsilon_min_r = 0.005
```

Amaç:

> Basit zaman-adaptif epsilon yaklaşımı ile GAPR’ın farkını ölçmek.

---

## V3 — GAPR Final

Mevcut son GAPR formülü kullanılacaktır.

Önemli:

- GAPR formülü değiştirilmeyecek.
- Lambda araması yapılmayacak.
- eps_max değiştirilmeyecek.
- Density tanımı değiştirilmeyecek.
- SoftClip eklenmeyecek.
- Rank tabanlı yeni varyant eklenmeyecek.

Amaç:

> Popülasyon geometrisine duyarlı adaptive epsilon yaklaşımının gerçek katkısını ölçmek.

---

# 7. Sabit QWMO Parametreleri

Aşağıdaki parametreler tüm varyantlarda sabit tutulacaktır.

| Parametre | Değer |
|---|---:|
| gamma | 0.05 |
| c_base | 5 |
| kappa_0 | 8 |
| k_s | 10 |
| eta_r | 0.001 |
| N | 50 |
| D | 30 |

Tüm varyantlar mümkün olduğunca yalnızca epsilon/Pauli davranışı bakımından farklılaşmalıdır.

---

# 8. Loglama Gereklilikleri

Fitness sonuçları tek başına yeterli değildir. Faz-1’in asıl amacı mekanizma kararı olduğu için her run’da ayrıntılı log tutulacaktır.

## 8.1 Her Iterasyonda Kaydedilecek Temel Değerler

Aşağıdaki değerler her iterasyonda veya belirlenen log aralığında kaydedilecektir.

```text
iteration
function_id
variant_id
run_id
seed
best_fitness
mean_fitness
worst_fitness
population_diversity_center
population_diversity_pairwise
mean_agent_distance
mean_knn_distance
epsilon_value
epsilon_to_mean_knn_ratio
collision_count
displacement_count
escape_triggered_count
escape_success_count
escape_failure_count
escape_neutral_count
pauli_success_count
pauli_failure_count
pauli_neutral_count
boundary_clipping_count
```

## 8.2 Diversity Metrikleri

En az iki diversity metriği hesaplanacaktır.

### D1 — Merkez Uzaklığı

Popülasyon merkezine ortalama uzaklık:

```text
D1(t) = mean_i || x_i(t) - mean(X(t)) ||
```

### D2 — Ortalama Pairwise Distance

Ajanlar arası ortalama uzaklık:

```text
D2(t) = mean_{i<j} || x_i(t) - x_j(t) ||
```

Eğer pairwise hesaplama pahalı olursa, örneklemeli pairwise hesaplama yapılabilir; ancak bu durumda yöntem raporda açıkça belirtilmelidir.

## 8.3 Epsilon Logları

Aşağıdaki değerler tutulacaktır:

```text
epsilon_value
epsilon_min
epsilon_max
epsilon_to_mean_knn_ratio
epsilon_saturated
```

`epsilon_saturated` aşağıdaki durumlarda `1` olmalıdır:

```text
epsilon_value == epsilon_max
```

veya floating point toleransı ile:

```text
abs(epsilon_value - epsilon_max) < 1e-12
```

## 8.4 Collision ve Displacement Logları

Aşağıdaki değerler tutulacaktır:

```text
collision_count
displacement_count
collision_per_agent
displacement_per_agent
```

## 8.5 Escape Logları

Her escape olayı aşağıdaki sınıflardan birine atanacaktır:

### Escape Success

Escape tetiklendikten sonra ilgili ajan, belirlenen pencere içinde iyileşme üretirse:

```text
escape_success = true
```

### Escape Failure

Escape sonrası ilgili ajan, pencere sonunda önceki fitness değerinden daha kötü durumdaysa:

```text
escape_failure = true
```

### Escape Neutral

Escape sonrası ilgili ajan, pencere sonunda anlamlı iyileşme veya kötüleşme göstermediyse:

```text
escape_neutral = true
```

## 8.6 Pauli Logları

Her Pauli displacement olayı aşağıdaki sınıflardan birine atanacaktır:

### Pauli Success

Pauli displacement sonrası ilgili ajan belirlenen pencere içinde iyileşme üretirse:

```text
pauli_success = true
```

### Pauli Failure

Pauli displacement sonrası ilgili ajan pencere sonunda önceki fitness değerinden daha kötü durumdaysa:

```text
pauli_failure = true
```

### Pauli Neutral

Pauli displacement sonrası ilgili ajan pencere sonunda anlamlı iyileşme veya kötüleşme göstermediyse:

```text
pauli_neutral = true
```

## 8.7 Success/Failure Penceresi

Escape ve Pauli başarısı için varsayılan pencere:

```text
window = 5 iteration
```

İyileşme eşiği:

```text
improvement_threshold = 1e-12
```

Eğer fonksiyon ölçeği nedeniyle bu eşik anlamsız kalırsa, göreli eşik kullanılabilir:

```text
relative_improvement_threshold = 1e-10
```

Ancak eşik deney başlamadan önce sabitlenmelidir.

---

# 9. Loglama Performans Notları

Loglama deney süresini aşırı artırmamalıdır.

Uygulama sırasında:

- Python listeleri yerine mümkünse NumPy array kullanılmalıdır.
- Event takibi için circular buffer kullanılmalıdır.
- Her ajan için son 5 iterasyonluk fitness geçmişi tutulmalıdır.
- Tüm population snapshot’ları gereksiz yere diske yazılmamalıdır.
- Ham ajan pozisyonları yalnızca debugging için opsiyonel tutulmalıdır.
- Ana CSV dosyaları iterasyon bazlı metrikleri içermelidir.

Önerilen yapı:

```text
logs/
  raw_events/
  iteration_metrics/
  summaries/
  plots/
```

---

# 10. Çalıştırma Sırası

Faz-1 aşağıdaki sırayla yürütülecektir.

## Gün 1 — Pauli Audit

Geçmiş deneyler incelenir.

Amaç:

- GAPR Final formülünün doğrulanması
- Dynamic Epsilon parametrelerinin doğrulanması
- V0/V1/V2/V3 varyantlarının kod seviyesinde netleştirilmesi
- önceki saturasyon, collision, escape bulgularının not edilmesi

Çıktı:

```text
phase1_audit_note.md
```

Bu nottan sonra yeni formül eklenmeyecektir.

---

## Gün 2 — Kod Dondurma

Yapılacaklar:

- varyant seçici yapı hazırlanır
- seed sistemi sabitlenir
- loglama sınıfı test edilir
- küçük smoke test yapılır
- tüm varyantlar aynı fonksiyon üzerinde kısa çalıştırılır
- çıktı formatları kontrol edilir

Çıktılar:

```text
phase1_config.yaml
phase1_smoke_test_report.md
```

Smoke test, gerçek deney sonucu olarak kullanılmayacaktır.

---

## Gün 3–10 — Ana 480 Run

Deney matrisi eksiksiz çalıştırılır.

Her run sonunda:

- raw result kaydedilir
- iteration log kaydedilir
- event log kaydedilir
- run summary kaydedilir

Her run dosya adı şu formatta olmalıdır:

```text
{function_id}_{variant_id}_seed{seed}_run{run_id}.csv
```

Örnek:

```text
F20_V3_seed12_run12.csv
```

---

## Gün 11–12 — İstatistiksel Analiz

Analizler:

- mean
- std
- median
- best
- worst
- Wilcoxon signed-rank test
- effect size
- median improvement
- convergence summary

Çıktılar:

```text
phase1_summary_table.csv
phase1_wilcoxon_results.csv
phase1_effect_sizes.csv
```

---

## Gün 13 — Mekanizma Analizi

Analizler:

- epsilon(t)
- epsilon / mean_kNN(t)
- collision(t)
- displacement(t)
- escape(t)
- failed escape ratio
- successful escape ratio
- diversity(t)
- collision → escape → improvement ilişkisi
- diversity → fitness improvement ilişkisi

Çıktılar:

```text
phase1_mechanism_summary.csv
phase1_mechanism_plots/
```

---

## Gün 14 — Decision Report

Tüm sonuçlar tek raporda birleştirilir.

Çıktı:

```text
phase1_decision_report.md
```

Bu rapor sonunda Karar A, Karar B veya Karar C’den biri açıkça yazılacaktır.

---

# 11. İstatistiksel Analiz Protokolü

## 11.1 Ana Karşılaştırmalar

Her fonksiyon için aşağıdaki karşılaştırmalar yapılacaktır.

```text
V3 vs V0
V3 vs V1
V3 vs V2
V2 vs V1
V1 vs V0
```

Özellikle V3 vs V0 karşılaştırması kritik karardır.

## 11.2 Test

Ana test:

```text
Wilcoxon signed-rank test
```

Anlamlılık eşiği:

```text
p < 0.05
```

## 11.3 Effect Size

p-değeri tek başına yeterli değildir.

Aşağıdakilerden en az biri raporlanmalıdır:

- rank-biserial correlation
- Cliff’s delta
- median improvement percentage

## 11.4 Ortalama ve Dağılım

Her varyant/fonksiyon için:

```text
mean
std
median
min
max
best
worst
```

raporlanacaktır.

## 11.5 Convergence Analizi

Her fonksiyon/varyant için ortalama convergence eğrisi çizilecektir.

Ek olarak:

- median convergence curve
- interquartile range band
- final best fitness boxplot

önerilir.

---

# 12. Mekanizma Analizi Protokolü

## 12.1 Epsilon Analizi

Sorular:

- GAPR gerçekten adaptif davranıyor mu?
- Epsilon sürekli eps_max’e yapışıyor mu?
- Epsilon / mean_kNN oranı anlamlı değişiyor mu?

Grafikler:

```text
epsilon(t)
epsilon_to_mean_knn_ratio(t)
epsilon_saturation_rate
```

## 12.2 Pauli Analizi

Sorular:

- Collision sayısı artıyor mu?
- Displacement sayısı artıyor mu?
- Pauli success ratio nedir?
- Pauli failure ratio nedir?
- Collision artışı fitness artışıyla ilişkili mi?

Grafikler:

```text
collision(t)
displacement(t)
pauli_success_ratio(t)
pauli_failure_ratio(t)
```

## 12.3 Escape Analizi

Sorular:

- Escape tetiklenme sayısı değişiyor mu?
- Escape success oranı değişiyor mu?
- GAPR, Escape success oranını artırıyor mu yoksa azaltıyor mu?
- Failed escape oranı GAPR ile artıyor mu?

Grafikler:

```text
escape_triggered(t)
escape_success_ratio(t)
escape_failure_ratio(t)
```

## 12.4 Diversity Analizi

Sorular:

- GAPR diversity collapse’ı geciktiriyor mu?
- Diversity korunumu fitness artışına dönüşüyor mu?
- Diversity artışı faydalı mı yoksa rastgele yayılım mı?

Grafikler:

```text
population_diversity_center(t)
population_diversity_pairwise(t)
mean_knn_distance(t)
```

## 12.5 Zincir Analizi

En kritik mekanizma analizi:

```text
collision
→ displacement
→ escape
→ improvement
```

Bu zincir için olay-temelli analiz yapılacaktır.

Önerilen metrikler:

```text
P(improvement | collision within previous 5 iterations)
P(improvement | escape within previous 5 iterations)
P(improvement | collision + escape within previous 5 iterations)
P(improvement | no collision and no escape)
```

Eğer `collision + escape` koşulu fitness improvement olasılığını artırıyorsa, GAPR-Pauli/Escape simbiyozu desteklenir.

---

# 13. Başarı Kriterleri

## 13.1 GAPR Ana Hatta Girer

GAPR Final, yani V3, aşağıdaki koşulları sağlamalıdır:

1. V3, F20 veya F10 üzerinde V1’den anlamlı derecede iyi olmalı.
2. V3, F20 veya F10 üzerinde V2’den anlamlı ya da pratik olarak iyi olmalı.
3. V3, F20 veya F10 üzerinde V0’dan anlamlı ya da pratik olarak iyi olmalı.
4. V3’ün mekanizma katkısı fitness kazanımıyla ilişkili olmalı.
5. Epsilon saturasyonu dominant davranış olmamalı.

## 13.2 GAPR Niş Mekanizma Olur

Aşağıdaki durumda Karar B verilir:

1. V3, V1’i geçer.
2. V3, V2’ye yakın veya sınırlı üstünlük gösterir.
3. V3, V0’ı geçemez veya yalnızca bir fonksiyonda geçer.
4. Mekanizma katkısı vardır ama fitness katkısı sınırlıdır.

## 13.3 GAPR Ana Hattan Çıkar

Aşağıdaki durumda Karar C verilir:

1. V3, V0’ı geçemez.
2. V3’te collision/displacement artar ama fitness artmaz.
3. V3’te diversity artar ama fitness artmaz.
4. V3’te failed escape oranı artar.
5. Epsilon saturasyonu devam eder.
6. F20 ve F10’da istatistiksel/pratik avantaj yoktur.

---

# 14. Dosya Çıktıları

Faz-1 sonunda aşağıdaki dosyalar üretilmelidir.

```text
phase1_audit_note.md
phase1_config.yaml
phase1_smoke_test_report.md
phase1_results_raw.csv
phase1_iteration_metrics.csv
phase1_event_logs.csv
phase1_summary_table.csv
phase1_wilcoxon_results.csv
phase1_effect_sizes.csv
phase1_mechanism_summary.csv
phase1_decision_report.md
```

Grafikler:

```text
phase1_plots/convergence/
phase1_plots/diversity/
phase1_plots/epsilon/
phase1_plots/collision/
phase1_plots/escape/
phase1_plots/correlation/
```

---

# 15. phase1_decision_report.md Şablonu

Rapor aşağıdaki başlıklarla yazılacaktır.

```markdown
# Phase-1 Decision Report

## 1. Amaç

## 2. Deney Protokolü

## 3. Test Edilen Varyantlar

## 4. Fitness Sonuçları

## 5. İstatistiksel Analiz

## 6. Epsilon Davranışı

## 7. Pauli Collision / Displacement Analizi

## 8. Escape Success / Failure Analizi

## 9. Diversity Analizi

## 10. Collision → Escape → Improvement Zinciri

## 11. Ana Bulgular

## 12. Karar

Karar: A / B / C

## 13. Sonraki Faz İçin Öneri
```

---

# 16. Uygulayıcı İçin Net Talimat

Bu belgeyi uygulayan model/geliştirici aşağıdaki sırayı izlemelidir:

1. Mevcut kod tabanında V0, V1, V2, V3 varyantlarını doğrula.
2. Yeni varyant ekleme.
3. 30D deney protokolünü sabitle.
4. 480 run matrisini oluştur.
5. Loglama sistemini test et.
6. Smoke test yap.
7. Ana deneyleri çalıştır.
8. Raw sonuçları kaydet.
9. İstatistiksel analizleri üret.
10. Mekanizma analizlerini üret.
11. Decision Report yaz.
12. Karar A/B/C’den birini açıkça belirt.
13. Karar verilmeden Faz-2’ye geçme.

---

# 17. Nihai İlke

Faz-1’in başarısı, GAPR’ın başarılı çıkmasına bağlı değildir.

Faz-1’in başarısı, belirsizliği ortadan kaldırmasına bağlıdır.

Bu faz sonunda aşağıdaki cümlelerden biri kesin olarak yazılabilmelidir:

## Senaryo 1

> GAPR, F20/F10 gibi multimodal-hybrid rejimlerde static ve time-based epsilon yaklaşımlarına göre daha kararlı fitness kazanımı üretmiştir.

## Senaryo 2

> GAPR, Pauli aktivasyonunu artırmasına rağmen bu aktivasyonu sistematik fitness kazanımına dönüştürememiştir; bu durum high-dimensional exclusion mekanizmalarında activation–utility ayrımını doğrulamaktadır.

Aşağıdaki durum kabul edilemez:

> GAPR işe yarıyor olabilir, ama emin değiliz.

Bu Faz-1’in başarısız olduğu anlamına gelir.

---

# 18. Kilitli Karar

Bu belgeyle Faz-1 planı kilitlenmiştir.

```text
Varyant sayısı: 4
Fonksiyon sayısı: 4
Boyut: 30D
Run: 30
Toplam deney: 480
SoftClip: yok
50D: yok
Yeni formül: yok
Yeni tuning: yok
Karar: A/B/C
```

Faz-1 başlasın.
