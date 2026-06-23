# QWMO Faz-2 Charter v2.2

## Radiomics Optimization Landscape Diagnosis & Pauli Response Pilot

---

# 0. Belge Amacı

Bu belge, QWMO araştırma hattının Faz-2 aşamasını tanımlar.

Faz-2’nin amacı yalnızca yeni bir radiomics optimizer geliştirmek değildir.

Faz-2’nin ana amacı:

> Büyük, yüksek boyutlu, korelasyonlu ve redundant radiomics feature-selection uzayında Pauli-Inspired Exclusion operatörünün nasıl tepki verdiğini gözlemlemek ve bu uzayın gerçekten multimodal, korelasyon-platolu, seed-sensitive ve local-optimum açısından zor olup olmadığını deneysel olarak belirlemektir.

Bu fazda ana QWMO varyantı:

```text
V1 = Static QWMO
```

olacaktır.

V0:

```text
V0 = Orbital + Escape
```

yalnızca opsiyonel kontrol varyantıdır.

---

# 1. Faz-1’den Gelen Karar

Faz-1 sonunda GAPR için:

```text
Karar C
```

verilmiştir.

Faz-1’in temel sonucu:

```text
Activation ≠ Utility
```

şeklindedir.

Yani Pauli/GAPR hattı collision, displacement ve diversity üretebilmiş; ancak bu aktivasyon sürekli benchmark ortamlarında sistematik fitness kazanımına dönüşmemiştir.

Bu nedenle:

```text
GAPR Faz-2’de kullanılmayacaktır.
```

Ancak bu karar:

```text
Static Pauli operatörü her problem sınıfında değersizdir.
```

anlamına gelmez.

Faz-2’de test edilecek yeni soru şudur:

> Sürekli CEC-style benchmarklarda faydası sınırlı görünen Pauli-Inspired Exclusion, yüksek korelasyonlu ve redundant radiomics feature-selection uzayında farklı bir davranış gösteriyor mu?

---

# 2. Faz-2’nin Temel Felsefesi

Faz-2 artık yalnızca:

```text
Radiomics uzayı zor mu?
```

sorusunu değil, aynı zamanda:

```text
Pauli bu zor ve redundant uzayda anlamlı bir çeşitlilik tepkisi üretiyor mu?
```

sorusunu da araştırır.

Bu fazda QWMO, salt "en iyi optimizer" olarak değil, aynı zamanda:

```text
Pauli response diagnostic tool
```

olarak kullanılacaktır.

---

# 3. Ana Araştırma Soruları

## RQ1

Radiomics feature-selection uzayı multimodal mı?

## RQ2

Radiomics feature-selection uzayı yüksek boyut arttıkça daha zor hale geliyor mu?

## RQ3

Radiomics feature-selection uzayında korelasyon platoları / neutral ridge yapıları var mı?

## RQ4

Farklı seed'ler farklı feature subset'lere ve farklı local optimumlara mı gidiyor?

## RQ5

Static QWMO, yani V1, radiomics feature-selection uzayında population collapse'ı azaltıyor mu?

## RQ6

Pauli-Inspired Exclusion operatörü, yüksek boyutlu binary/latent feature-selection uzayında:

```text
collision
displacement
mask diversity
elite diversity
feature family coverage
```

üretebiliyor mu?

## RQ7

Pauli aktivasyonu, radiomics ortamında fitness/AUC veya feature-stability kazanımına dönüşüyor mu?

---

# 4. Hipotezler

## H0

Radiomics feature-selection uzayı klasik yöntemlerle yeterince kararlı biçimde çözülebilir.

Pauli-Inspired Exclusion:

* anlamlı diversity katkısı üretmez,
* population collapse'ı azaltmaz,
* AUC veya feature stability avantajına dönüşmez.

## H1

Radiomics feature-selection uzayı multimodal, yüksek boyutlu, korelasyon-platolu ve local-optimum açısından zordur.

Bu uzayda Static QWMO içindeki Pauli-Inspired Exclusion:

* population collapse'ı azaltabilir,
* farklı feature subset basin'lerini keşfedebilir,
* elite mask diversity'yi artırabilir,
* bazı rejimlerde AUC/stability/sparsity açısından fayda üretebilir.

---

# 5. Faz-2 Sonunda Verilecek Kararlar

## Karar A — Radiomics Uzayı Zor ve Pauli Tepkisi Anlamlı

Aşağıdaki durumda verilir:

* Radiomics uzayı zorluk kriterlerinin çoğunu sağlar.
* V1 belirgin Pauli aktivasyonu üretir.
* Pauli aktivasyonu en az bir pratik faydaya dönüşür:

  * daha iyi AUC,
  * daha yüksek stability,
  * daha düşük redundancy,
  * daha fazla elite diversity,
  * daha az population collapse.

Bu durumda Faz-3 başlar:

```text
Faz-3 = Static QWMO / Pauli-aware Radiomics Optimizer
```

---

## Karar B — Radiomics Uzayı Zor, Pauli Tepkisi Sınırlı

Aşağıdaki durumda verilir:

* Radiomics uzayı zor görünür.
* V1 Pauli aktivasyonu üretir.
* Ancak bu aktivasyon fitness/AUC avantajına net dönüşmez.
* Pauli daha çok mekanizma açıklaması veya niş katkı olarak kalır.

Bu durumda Faz-3 daraltılır:

```text
Faz-3 = Radiomics için QWMO varyantı, Pauli katkısı appendix/mechanism analysis
```

---

## Karar C — Radiomics Uzayı Bu Hat İçin Yeterince Zor Değil veya Pauli Tepkisi Faydasız

Aşağıdaki durumda verilir:

* Uzay zorluk kriterlerini sağlamaz,
* veya V1 klasik yöntemlere göre anlamlı davranış farkı göstermez,
* veya Pauli aktivasyonu yalnızca maliyet/gürültü üretir.

Bu durumda QWMO-Radiomics hattı ana araştırma hattı olmaktan çıkarılır.

---

# 6. Kesin Yasaklar

Faz-2 boyunca aşağıdakiler yapılmayacaktır:

* Yeni QWMO operatörü eklemek
* Yeni escape formülü eklemek
* Yeni orbital formülü eklemek
* Yeni epsilon formülü eklemek
* GAPR'ı geri getirmek
* Dynamic epsilon denemek
* SoftClip / rank-based yeni Pauli varyantı eklemek
* Sonuçlara göre veri seti değiştirmek
* Sonuçlara göre başarı kriteri değiştirmek
* Leakage içeren pipeline kullanmak
* V1 kötü gelirse sonradan V0'ı ana algoritma ilan etmek
* V1 iyi gelirse Faz-1 sonucunu yok saymak

---

# 7. Ana QWMO Varyantı

Faz-2'nin ana QWMO varyantı:

```text
V1 = Static QWMO
```

Kullanılan operatörler:

```text
Adaptive Orbital Sampling
Static Pauli-Inspired Exclusion
Adaptive Quantum Escape
```

Static Pauli epsilon:

```text
epsilon_r = 0.05
```

veya kod tabanındaki Faz-1 Static QWMO ile birebir aynı değer.

Bu değer deney başladıktan sonra değiştirilmeyecektir.

---

# 8. Opsiyonel Kontrol Varyantı

Opsiyonel kontrol:

```text
V0 = Orbital + Escape
```

Kullanılan operatörler:

```text
Adaptive Orbital Sampling
Adaptive Quantum Escape
```

Kullanılmayan operatör:

```text
Pauli-Inspired Exclusion
```

V0'ın amacı:

```text
Pauli etkisini izole etmek
```

olacaktır.

V0 çalıştırılmazsa, raporda şu sınırlama açıkça yazılacaktır:

```text
Bu Faz-2 çalışması V1 Static QWMO'nun radiomics uzayındaki davranışını gözlemlemiştir; ancak Pauli katkısının izole nedensel etkisi V0 kontrolü olmadan güçlü biçimde iddia edilemez.
```

---

# 9. GAPR Durumu

GAPR:

```text
kullanılmayacaktır.
```

Sebep:

```text
Faz-1'de GAPR aktivasyonu sistematik fitness kazanımına dönüşmemiştir.
```

Bu faz Static Pauli tepkisini gözlemleme fazıdır, GAPR kurtarma fazı değildir.

---

# 10. Veri Setleri

Minimum:

```text
2 radiomics dataset
```

Önerilen:

```text
3 radiomics dataset
```

Her veri seti için minimum kriterler:

```text
n_samples >= 50
n_features >= 100
binary outcome mevcut
eksik veri oranı makul
```

Tercihen:

```text
n_features >= 500
```

Her veri seti için raporlanacak bilgiler:

```text
dataset_id
modality
clinical task
n_samples
n_positive
n_negative
class_imbalance_ratio
n_raw_features
n_after_preprocessing
missing_value_rate
source
license/access status
```

---

# 11. Veri Sızıntısı Politikası

Aşağıdaki işlemler yalnızca training fold üzerinde fit edilir:

```text
imputation
scaling
variance filtering
correlation filtering
feature ranking
subspace construction
feature selection
model training
```

Tüm deney:

```text
Leakage-Free Nested Cross-Validation
```

yapısıyla yürütülür.

Tüm preprocessing pipeline, outer train/test ayrımı yapıldıktan sonra fit edilir.

---

# 12. Cross-Validation Tasarımı

## 12.1 Outer CV

Varsayılan:

```text
Repeated Stratified KFold
5 folds × 3 repeats
```

Eğer veri seti küçükse:

```text
5 folds × 2 repeats
```

kabul edilebilir.

## 12.2 Inner CV

Fitness değerlendirmesi için:

```text
Stratified KFold = 3 folds
```

Her candidate mask için:

```text
mean_inner_AUC
```

hesaplanır.

---

# 13. Ön İşleme

## 13.1 Missing Value

Varsayılan:

```text
Median Imputation
```

## 13.2 Scaling

Varsayılan:

```text
StandardScaler
```

## 13.3 Variance Filter

Near-zero variance feature'lar çıkarılır.

## 13.4 Correlation Filter

Varsayılan eşik:

```text
|r| > 0.95
```

Bu hesap yalnızca training fold içinde yapılır.

---

# 14. Problem Temsili

QWMO latent continuous uzayda çalışacaktır.

Latent çözüm:

```text
z ∈ R^p
```

Binary feature mask:

```text
mask_j = sigmoid(z_j) > 0.5
```

Bernoulli sampling kullanılmayacaktır.

```text
Bernoulli sampling = yasak
```

Amaç:

```text
QWMO'nun continuous orbital hareketini koruyup binary feature-selection uzayına deterministik projeksiyon yapmak.
```

---

# 15. V1 Static QWMO Binary Uygulaması

## 15.1 Orbital Sampling

Latent uzayda uygulanır:

```text
z'_i = z_i + N(0, sigma_i^2 I)
```

## 15.2 Binary Projection

Her candidate için:

```text
mask = sigmoid(z) > 0.5
```

## 15.3 Static Pauli Exclusion

Pauli collision ve displacement latent uzayda uygulanır.

Collision distance:

```text
||z_i - z_j|| < epsilon
```

Displacement:

```text
weaker agent latent z-space içinde ortogonal kaydırılır
```

Sonrasında yeni mask deterministik olarak tekrar üretilir.

## 15.4 Adaptive Quantum Escape

Escape latent uzayda uygulanır.

Escape sonrası:

```text
z_escape
↓
sigmoid
↓
mask
```

üretilir.

---

# 16. Fitness Fonksiyonu

Ana minimizasyon fitness:

```text
fitness = (1 - mean_inner_AUC) + lambda × selected_feature_ratio
```

Varsayılan:

```text
lambda = 0.01
```

Boş maske geçersizdir.

Minimum seçili feature:

```text
min_features = 2
```

Boş veya yetersiz mask için:

```text
fitness = penalty
```

---

# 17. Sınıflandırıcı

Ana sınıflandırıcı:

```text
Logistic Regression
```

Parametreler:

```text
class_weight = balanced
penalty = l2
solver = liblinear veya saga
max_iter = 5000
```

Ana metrik:

```text
AUC
```

Ek metrikler:

```text
accuracy
balanced_accuracy
sensitivity
specificity
F1
selected_feature_count
```

---

# 18. Subspace Rejimleri

Faz-2'de iki ayrı subspace rejimi kullanılacaktır.

---

## 18.1 Ranked Subspace

Training fold içinde feature ranking yapılır.

p-level:

```text
25
50
100
250
500
full
```

Amaç:

```text
Sinyal yoğun bölgede arama zorluğunu ölçmek.
```

---

## 18.2 Random Subspace

Training fold içindeki feature havuzundan rastgele p feature seçilir.

p-level:

```text
25
50
100
250
500
full
```

Amaç:

```text
Gürültü + korelasyon + sinyal karışık gerçekçi yüksek boyut zorluğunu ölçmek.
```

---

# 19. Random Subspace Adalet Kuralı

Her:

```text
dataset
outer fold
repeat
p-level
random_subspace_id
```

kombinasyonu için yalnızca tek random subspace oluşturulur.

Tüm yöntemler aynı random subspace üzerinde çalışır.

Bu kural adil karşılaştırma için zorunludur.

Random subspace seed'i loglanır:

```text
random_subspace_seed
```

---

# 20. Test Edilecek Yöntemler

Zorunlu yöntemler:

```text
M0 Random Search
M1 Greedy Forward Selection
M2 Greedy Backward Elimination
M3 Genetic Algorithm
M4 Binary PSO
M5 Static QWMO Binary = V1
```

Opsiyonel kontrol:

```text
M6 QWMO-Core Binary = V0
```

V0 çalıştırılırsa raporda appendix veya mekanizma kontrolü olarak sunulabilir.

---

# 21. Bütçe Politikası

## 21.1 Pilot

```text
1000 fitness evaluations
```

Amaç:

```text
pipeline doğrulama
hesap maliyeti ölçme
ilk landscape ve Pauli response sinyali
```

## 21.2 Final

```text
3000 fitness evaluations
```

Population tabanlı yöntemlerde:

```text
population_size = 30
```

Final yaklaşık iterasyon sayısı:

```text
3000 / 30 = 100 iteration
```

---

# 22. Seed Politikası

Pilot:

```text
10 seed
```

Final:

```text
30 seed
```

Önerilen seed listesi:

```text
0, 1, 2, ..., 29
```

Tüm yöntemlerde seed protokolü sabitlenir.

---

# 23. Deney Matrisi

## 23.1 Pilot Matrix

```text
2 dataset
2 subspace regime
p = 50, 100, 250, full
6 yöntem
10 seed
1000 FE
```

V0 eklenirse:

```text
6 yöntem → 7 yöntem
```

## 23.2 Final Matrix

Pilot pozitifse:

```text
3 dataset
2 subspace regime
p = 25, 50, 100, 250, 500, full
6 yöntem
30 seed
3000 FE
```

V0 eklenirse:

```text
6 yöntem → 7 yöntem
```

---

# 24. Loglama Gereklilikleri

## 24.1 Run-Level Log

Her run için:

```text
dataset_id
outer_fold_id
repeat_id
subspace_regime
p_level
random_subspace_seed
method_id
variant_id
seed
budget
best_fitness
best_inner_auc
outer_test_auc
outer_test_accuracy
outer_test_balanced_accuracy
outer_test_f1
outer_test_sensitivity
outer_test_specificity
selected_feature_count
selected_feature_ratio
runtime_seconds
n_evaluations
converged_iteration
final_stagnation_length
```

---

## 24.2 Iteration-Level Log

Her iterasyon için:

```text
iteration
best_fitness
mean_fitness
std_fitness
best_auc
mean_selected_feature_count
population_diversity_hamming
population_diversity_jaccard
population_diversity_latent
stagnation_counter_best
escape_count
pauli_collision_count
pauli_displacement_count
```

---

## 24.3 Candidate / Elite Log

Her run sonunda:

```text
top_k_masks
top_k_fitness
top_k_auc
top_k_selected_feature_count
```

Varsayılan:

```text
top_k = 20
```

---

## 24.4 Event Log

V1 için:

```text
event_type
iteration
agent_id
fitness_before
fitness_after
auc_before
auc_after
selected_feature_count_before
selected_feature_count_after
latent_distance_moved
mask_hamming_distance_moved
event_success
```

Event türleri:

```text
pauli_collision
pauli_displacement
escape
orbital_update
```

---

# 25. Pauli Response Metrikleri

V1 için zorunlu metrikler:

```text
pauli_collision_count
pauli_displacement_count
collision_per_agent
displacement_per_agent
pauli_success_count
pauli_failure_count
pauli_neutral_count
pauli_success_ratio
pauli_failure_ratio
```

Başarı penceresi:

```text
window = 5 iteration
```

İyileşme eşiği:

```text
improvement_threshold = 1e-12
```

veya göreli:

```text
relative_improvement_threshold = 1e-10
```

Eşik deney başlamadan önce sabitlenir.

---

# 26. Escape Analizi

Zorunlu metrikler:

```text
escape_count
successful_escape_count
failed_escape_count
neutral_escape_count
failed_escape_ratio
P(improvement | escape)
P(improvement | no_escape)
post_escape_fitness_improvement
post_escape_auc_improvement
post_escape_fitness_deterioration
post_escape_auc_deterioration
```

Eğer:

```text
failed_escape_ratio > 0.70
```

ise escape mekanizması:

```text
yüksek gürültülü relocation
```

olarak yorumlanır.

---

# 27. Multimodality Metrikleri

## 27.1 Elite Jaccard Distance

Top çözümler arasındaki ortalama Jaccard distance:

```text
Elite_Jaccard_Distance
```

## 27.2 Elite Hamming Distance

```text
Elite_Hamming_Distance
```

## 27.3 Elite Cluster Count

Jaccard distance tabanlı cluster sayısı:

```text
Elite_Cluster_Count
```

Varsayılan cluster ayrım eşiği:

```text
distance > 0.5
```

---

# 28. Stability Metrikleri

```text
mean_pairwise_jaccard_similarity
Kuncheva_index
seed_sensitivity_auc
seed_sensitivity_mask
std_outer_auc_across_seeds
```

---

# 29. Korelasyon Plato / Neutral Ridge Analizi

Seçili feature'lar arasında:

```text
mean_abs_correlation_selected
max_abs_correlation_selected
redundant_feature_ratio
```

hesaplanır.

Varsayılan redundancy eşiği:

```text
|r| > 0.80
```

Bu analiz, radiomics uzayında eşdeğer/korele feature platolarını göstermek için zorunludur.

---

# 30. Population Collapse Analizi

V1 için özellikle ölçülecek:

```text
population_mask_diversity
population_latent_diversity
elite_mask_diversity
feature_family_coverage
collapse_iteration
```

Population collapse tanımı:

```text
population_mask_diversity < 0.10
```

veya deney öncesi sabitlenen eşik.

Amaç:

```text
Pauli population collapse'ı geciktiriyor mu?
```

---

# 31. Karar Eşikleri

Aşağıdaki beş ana kriter kullanılacaktır.

## Kriter 1 — Multimodality

```text
Elite Jaccard Distance > 0.60
```

## Kriter 2 — Stability Düşüklüğü

```text
Kuncheva Stability < 0.70
```

## Kriter 3 — Seed Sensitivity

```text
AUC std across seeds > 0.03
```

## Kriter 4 — Escape Benefit

```text
P(improvement | escape)
>
P(improvement | no_escape) + 0.10
```

## Kriter 5 — Correlation Plateau

```text
Mean Selected Feature Correlation > 0.80
```

---

# 32. Pauli'ye Özgü Ek Karar Kriterleri

V1'in Pauli tepkisi anlamlı sayılırsa aşağıdakilerden en az ikisi görülmelidir:

```text
pauli_collision_count > 0
pauli_displacement_count > 0
population collapse gecikir
elite_jaccard_distance artar
mean_abs_correlation_selected düşer
feature_family_coverage artar
pauli_success_ratio > pauli_failure_ratio
```

Eğer V0 çalıştırılırsa bu metrikler V1 vs V0 karşılaştırmasıyla yorumlanır.

Eğer V0 çalıştırılmazsa bu metrikler yalnızca V1 davranışı olarak raporlanır.

---

# 33. Nihai Karar Kuralları

## Karar A

Aşağıdaki iki koşul birlikte sağlanırsa verilir:

```text
Ana 5 zorluk kriterinden en az 3 tanesi sağlanır.
```

ve

```text
Pauli'ye özgü ek kriterlerden en az 2 tanesi sağlanır.
```

Yorum:

```text
Radiomics uzayı zordur ve Pauli tepkisi anlamlıdır.
```

---

## Karar B

Aşağıdaki durumda verilir:

```text
Ana 5 zorluk kriterinden tam olarak 2 tanesi sağlanır.
```

veya

```text
Uzay zor görünür ama Pauli tepkisi sınırlıdır.
```

Yorum:

```text
Radiomics uzayı kısmen zordur veya Pauli etkisi niş düzeydedir.
```

---

## Karar C

Aşağıdaki durumda verilir:

```text
Ana 5 zorluk kriterinden 0 veya 1 tanesi sağlanır.
```

veya

```text
Pauli aktivasyonu yalnızca maliyet/gürültü üretir.
```

Yorum:

```text
Radiomics uzayı bu hat için yeterince zor değildir veya Pauli tepkisi faydasızdır.
```

---

# 34. İstatistiksel Analiz

Ana testler:

```text
Wilcoxon signed-rank test
Mann-Whitney U test
```

Eğer çoklu karşılaştırma varsa:

```text
Holm correction
```

Effect size:

```text
Cliff's delta
rank-biserial correlation
median difference
```

Ana karşılaştırmalar:

```text
V1 vs Random Search
V1 vs Greedy Forward
V1 vs Greedy Backward
V1 vs GA
V1 vs BPSO
```

Opsiyonel:

```text
V1 vs V0
```

---

# 35. Çıktı Dosyaları

Faz-2 sonunda üretilecek dosyalar:

```text
phase2_config.yaml
phase2_dataset_summary.csv
phase2_preprocessing_report.md
phase2_optimizer_audit.md
phase2_results_raw.csv
phase2_outer_cv_results.csv
phase2_iteration_logs.csv
phase2_event_logs.csv
phase2_elite_masks.csv
phase2_pauli_response_metrics.csv
phase2_landscape_metrics.csv
phase2_statistical_tests.csv
phase2_effect_sizes.csv
phase2_decision_report.md
```

Grafikler:

```text
phase2_plots/performance_auc/
phase2_plots/selected_feature_count/
phase2_plots/elite_jaccard/
phase2_plots/feature_stability/
phase2_plots/pauli_response/
phase2_plots/population_collapse/
phase2_plots/correlation_plateau/
phase2_plots/convergence/
phase2_plots/stagnation/
phase2_plots/escape_benefit/
phase2_plots/dimension_scaling/
```

---

# 36. phase2_decision_report.md Şablonu

```markdown
# Phase-2 Decision Report
## Radiomics Optimization Landscape Diagnosis & Pauli Response Pilot

## 1. Amaç

## 2. Faz-1'den Gelen Karar

## 3. Veri Setleri

## 4. Leakage-Free Pipeline

## 5. Problem Temsili

## 6. Fitness Fonksiyonu

## 7. Test Edilen Yöntemler

## 8. Deney Matrisi

## 9. Performans Sonuçları

## 10. Feature Count ve Sparsity Analizi

## 11. Seed Sensitivity Analizi

## 12. Elite Mask Diversity Analizi

## 13. Feature Stability Analizi

## 14. Korelasyon Plato / Neutral Ridge Analizi

## 15. Population Collapse Analizi

## 16. Pauli Collision / Displacement Analizi

## 17. Pauli Success / Failure Analizi

## 18. Escape Success / Failure Analizi

## 19. Yüksek Boyut Etkisi

## 20. Multimodality Kanıtı

## 21. Ana Bulgular

## 22. Karar

Karar: A / B / C

## 23. Faz-3 İçin Öneri
```

---

# 37. Gün Gün Uygulama Planı

## Gün 1 — Veri Seti Kilitleme

Çıktı:

```text
phase2_dataset_summary.csv
```

## Gün 2 — Leakage Audit

Çıktı:

```text
phase2_preprocessing_report.md
```

## Gün 3 — Fitness ve Baseline Smoke Test

Çıktı:

```text
phase2_smoke_test_report.md
```

## Gün 4 — Optimizer Entegrasyonu

Çıktı:

```text
phase2_optimizer_audit.md
```

## Gün 5–7 — Pilot Matrix

Çıktı:

```text
phase2_pilot_results_raw.csv
phase2_pilot_decision_note.md
```

## Gün 8 — Pilot Go / No-Go

Karar:

```text
Final Matrix çalıştırılsın mı?
```

## Gün 9–16 — Final Matrix

Çıktılar:

```text
phase2_results_raw.csv
phase2_iteration_logs.csv
phase2_event_logs.csv
phase2_elite_masks.csv
```

## Gün 17–18 — İstatistiksel Analiz

Çıktılar:

```text
phase2_statistical_tests.csv
phase2_effect_sizes.csv
```

## Gün 19 — Landscape ve Pauli Response Analizi

Çıktılar:

```text
phase2_landscape_metrics.csv
phase2_pauli_response_metrics.csv
```

## Gün 20 — Decision Report

Çıktı:

```text
phase2_decision_report.md
```

---

# 38. Nihai Kilit

```text
Faz adı:
Radiomics Optimization Landscape Diagnosis & Pauli Response Pilot

Ana amaç:
Radiomics uzayında Pauli tepkisini gözlemlemek

Ana QWMO:
V1 Static QWMO

Opsiyonel kontrol:
V0 Orbital + Escape

GAPR:
Yok

Dynamic epsilon:
Yok

Binary dönüşüm:
Deterministic Sigmoid Threshold

Pilot:
1000 FE

Final:
3000 FE

Subspace:
Ranked + Random

Karar:
A / B / C
```

---

# 39. Faz-2 Başarı Tanımı

Faz-2 başarılı sayılır eğer aşağıdaki sorulara açık cevap verebiliyorsa:

```text
Radiomics feature-selection uzayı gerçekten zor mu?
```

ve

```text
Static Pauli bu büyük, korelasyonlu ve redundant uzayda anlamlı bir tepki üretiyor mu?
```

Aşağıdaki cevap kabul edilemez:

```text
Pauli işe yarıyor olabilir ama emin değiliz.
```

Faz-2'nin görevi bu belirsizliği ortadan kaldırmaktır.
