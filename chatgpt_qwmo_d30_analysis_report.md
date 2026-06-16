# QWMO v1.2.0 — D30 GCP Koşusu Analiz Raporu
**Kaynak dosyalar:** `results_D30.json` ve `qwmo_v1.2.0_run.log`
**Analiz kapsamı:** CEC2017 30D sonuçları, 9 fonksiyon, 13 algoritma/konfigürasyon, 30 bağımsız seed.
## 1. Yönetici Özeti
Bu koşu teknik olarak başarıyla üretilmiş ve JSON ile log kayıtları birbiriyle tutarlı görünmektedir. Ancak bilimsel olarak final Faz-1 kanıtı sayılmamalıdır. En önemli nedenler: Pauli operatörünün etkisinin çoğu fonksiyonda görünmemesi, koşunun nihai plandaki 3,000,000 FE yerine logda açıkça belirtilen 300,000 FE bütçesiyle yapılmış olması, mekanizma loglarının sonuç JSON’una taşınmaması ve runtime değerlerinin paralel GCP wall-clock ortamından gelmesidir.
**Nihai hüküm:** Bu veri seti final tablo değil, güçlü bir diagnostic/pilot koşudur. QWMO’nun escape mekanizması bazı multimodal/hybrid fonksiyonlarda ciddi katkı üretirken, Pauli/dynamic epsilon katkısı mevcut kayıtlarla doğrulanmamaktadır.
## 2. Deney Protokolü ve Veri Bütünlüğü
- Log dosyası D=30 deneyinin çalıştığını ve FE bütçesinin `300,000 (CEC2017 standard: 10,000·D)` olduğunu bildiriyor. Bu, nihai plandaki 3M FE protokolünden farklıdır.
- Toplam görev sayısı 3510’dur: `9 fonksiyon × 13 algoritma/konfigürasyon × 30 seed`. Bu deney matrisi planlanan 30D kapsamıyla uyumludur.
- Logdaki F1 örnekleri JSON değerleriyle örtüşmektedir; veri aktarımında belirgin bir serialization hatası görünmüyor.
- Checkpoint sistemi logda düzenli aralıklarla çalışmış görünmektedir.

**Önemli protokol notu:** Bu koşu CEC-standard kısa bütçe koşusu olarak raporlanmalı; 3M FE ana Faz-1 koşusu gibi sunulmamalıdır.
## 3. Ortalama Rank Analizi
Aşağıdaki sıralama, her fonksiyonda mean fitness küçük olanın daha iyi kabul edilmesiyle hesaplanan ortalama ranktır.
| Sıra | Algoritma | Ortalama Rank |
|---:|---|---:|
| 1 | SHADE | 1.22 |
| 2 | ASO | 3.67 |
| 3 | CMA_ES | 3.78 |
| 4 | QPSO | 4.33 |
| 5 | QWMO_Full | 6.22 |
| 6 | QWMO_OrbitalOnly | 6.67 |
| 7 | QWMO_OrbitalEscape | 7.00 |
| 8 | QWMO_OrbitalPauli | 7.44 |
| 9 | GWO | 8.00 |
| 10 | PSO | 8.67 |
| 11 | HHO | 10.44 |
| 12 | AOS | 10.56 |
| 13 | GA | 13.00 |

**Yorum:** QWMO_Full genel tabloda orta-üst düzeydedir; klasik/zayıf baseline’lara karşı güçlüdür fakat SHADE, ASO, CMA-ES ve QPSO gibi güçlü rakipler karşısında genel üstünlük göstermemektedir.
## 4. Fonksiyon Bazlı Birinciler ve QWMO_Full Konumu
| Fonksiyon | En iyi algoritma | En iyi mean fitness | QWMO_Full mean | QWMO_Full konumu |
|---|---|---:|---:|---|
| F1 | SHADE | 100 | 1.86824e+07 | QWMO_Full rank 8 |
| F3 | CMA_ES | 300 | 14240.1 | QWMO_Full rank 7 |
| F5 | SHADE | 523.075 | 596.341 | QWMO_Full rank 8 |
| F9 | ASO | 900 | 1866.22 | QWMO_Full rank 7 |
| F10 | SHADE | 3014.07 | 3428.14 | QWMO_Full rank 2 |
| F15 | SHADE | 1624.23 | 36488.1 | QWMO_Full rank 8 |
| F20 | SHADE | 2124.81 | 2184.58 | QWMO_Full rank 2 |
| F23 | SHADE | 2674.51 | 2714.44 | QWMO_Full rank 7 |
| F28 | SHADE | 3133.19 | 3204.88 | QWMO_Full rank 7 |

**Ana gözlem:** QWMO_Full özellikle F10 ve F20 çevresinde rekabetçi görünürken, F1 ve F15 gibi alanlarda belirgin şekilde zayıflamaktadır.
## 5. QWMO_Full Karşılaştırmalı Win/Tie/Loss Özeti
Aşağıdaki tablo fonksiyon mean değerleri üzerinden QWMO_Full’un her rakibe karşı kaç fonksiyonda daha iyi/eşit/daha kötü olduğunu gösterir.
| Rakip | QWMO daha iyi | Eşit | QWMO daha kötü |
|---|---:|---:|---:|
| QWMO_OrbitalOnly | 4 | 0 | 5 |
| QWMO_OrbitalPauli | 4 | 0 | 5 |
| QWMO_OrbitalEscape | 8 | 0 | 1 |
| PSO | 7 | 0 | 2 |
| GA | 9 | 0 | 0 |
| GWO | 6 | 0 | 3 |
| HHO | 8 | 0 | 1 |
| SHADE | 0 | 0 | 9 |
| ASO | 2 | 0 | 7 |
| AOS | 9 | 0 | 0 |
| QPSO | 2 | 0 | 7 |
| CMA_ES | 2 | 0 | 7 |

**Yorum:** QWMO_Full GA, AOS ve HHO gibi baseline’lara karşı güçlü görünür. Ancak SHADE karşısında tüm fonksiyonlarda geride; ASO/CMA-ES/QPSO karşısında da genel üstün değildir.
## 6. Ablation Bulguları
### 6.1 Pauli Etkisi
OrbitalOnly ve OrbitalPauli sonuçlarının seed bazında birebir aynı veya neredeyse aynı olması Pauli operatörü açısından en kritik anomalidir.
| Fonksiyon | Birebir aynı seed sayısı | Run sayısı | OrbitalOnly mean | OrbitalPauli mean |
|---|---:|---:|---:|---:|
| F1 | 0 | 30 | 1.76589e+06 | 2.07835e+06 |
| F3 | 17 | 30 | 37811.6 | 37811.6 |
| F5 | 12 | 30 | 593.645 | 593.645 |
| F9 | 22 | 30 | 5885.2 | 5885.2 |
| F10 | 13 | 30 | 3707.2 | 3707.2 |
| F15 | 16 | 30 | 36098.1 | 36098.1 |
| F20 | 19 | 30 | 2270.71 | 2270.71 |
| F23 | 14 | 30 | 2708.3 | 2708.3 |
| F28 | 14 | 30 | 3194.56 | 3194.56 |

Bu tablo Pauli operatörünün çoğu fonksiyonda final fitness’a ölçülebilir katkı üretmediğini gösterir. Önceki repo incelemesindeki Pauli sonrası fitness yeniden değerlendirmeme problemiyle bu bulgu uyumludur.
### 6.2 Escape Etkisi
Escape operatörü bazı fonksiyonlarda iyileştirici, bazı fonksiyonlarda bozucudur. Aşağıdaki oranlarda 1’den küçük değer iyileşmeyi, 1’den büyük değer kötüleşmeyi gösterir.
| Fonksiyon | Full / OrbitalOnly | OrbitalEscape / OrbitalOnly | Yorum |
|---|---:|---:|---|
| F1 | 10.580 | 10.825 | kötüleşme |
| F3 | 0.377 | 0.394 | iyileşme |
| F5 | 1.005 | 1.005 | kötüleşme |
| F9 | 0.317 | 0.317 | iyileşme |
| F10 | 0.925 | 0.951 | iyileşme |
| F15 | 1.011 | 1.219 | kötüleşme |
| F20 | 0.962 | 0.964 | iyileşme |
| F23 | 1.002 | 1.011 | kötüleşme |
| F28 | 1.003 | 1.004 | kötüleşme |

**Yorum:** Escape F3, F9, F10 ve F20 gibi yapılarda faydalı; F1’de ise ciddi biçimde bozucu. Bu, escape politikasının landscape-aware veya improvement-gated yapılması gerektiğini düşündürür.
## 7. Runtime Analizi
Aşağıdaki tablo 9 fonksiyondaki `mean_time` değerlerinin ortalamasını verir. Bunlar paralel GCP wall-clock koşullarında ölçülmüştür; izole tek-process CPU-time olarak yorumlanmamalıdır.
| Sıra | Algoritma | Ortalama süre (s) |
|---:|---|---:|
| 1 | GA | 47.24 |
| 2 | QWMO_OrbitalEscape | 119.59 |
| 3 | QWMO_OrbitalPauli | 122.01 |
| 4 | QWMO_OrbitalOnly | 122.11 |
| 5 | AOS | 122.91 |
| 6 | QWMO_Full | 154.68 |
| 7 | QPSO | 161.70 |
| 8 | CMA_ES | 178.78 |
| 9 | HHO | 241.38 |
| 10 | PSO | 316.87 |
| 11 | GWO | 331.64 |
| 12 | ASO | 334.84 |
| 13 | SHADE | 410.71 |

**Yorum:** QWMO_Full runtime bakımından SHADE, ASO, PSO, GWO ve HHO gibi algoritmalardan daha hızlı görünmektedir. Ancak paralel worker ortamı nedeniyle final makale için ayrıca tek-thread/tek-process runtime benchmark önerilir.
## 8. SHADE ve CMA-ES Bulguları
SHADE ve CMA-ES bazı fonksiyonlarda CEC bias değerine çok yakın veya tam ulaşmaktadır. Bu tek başına hata değildir; CEC fonksiyonlarında bias değerleri nedeniyle beklenebilir. Ancak final rapor öncesinde benchmark wrapper, bounds, batch/single evaluation ve tüm algoritmaların aynı objective fonksiyonunu kullandığı doğrulanmalıdır.
## 9. Bilimsel Mesaj
Bu koşudan çıkarılabilecek güvenli bilimsel mesaj şudur:
> QWMO_Full, 30D CEC-standard kısa bütçede bazı multimodal/hybrid fonksiyonlarda rekabetçi davranır. Performans kazancı esas olarak escape mekanizmasıyla ilişkilidir. Pauli/dynamic epsilon katkısı mevcut implementasyon ve log yapısıyla doğrulanmamıştır.

Kaçınılması gereken iddia:
> QWMO v1.2.0 dynamic epsilon sayesinde genel olarak state-of-the-art algoritmaları aşmaktadır.
## 10. Kritik Düzeltme Listesi
1. **Pauli sonrası fitness evaluation + FE accounting:** Pauli ile yeri değişen ajanların fitness değerleri yeniden hesaplanmalı ve FE bütçesine yazılmalı.
2. **Escape parametre ayrımı:** `kappa_0` ve `k_s` semantik olarak ayrılmalı; biri escape probability decay, diğeri stagnation threshold olmalı.
3. **Mekanizma logları JSON’a eklenmeli:** convergence, collision count, active displacement ratio, diversity history, escape attempts, successful escape ratio.
4. **Static vs dynamic epsilon ablation:** Full static epsilon ve Full dynamic epsilon ayrı raporlanmalı.
5. **FE protokolü netleştirilmeli:** CEC-standard `10,000×D` ve long-budget `3M FE` ayrımı açık yazılmalı.
6. **Runtime tekrar ölçülmeli:** Makaleye konacak runtime için tek-process, tek-thread, aynı CPU ortamı kullanılmalı.
7. **A12 yönü kontrol edilmeli:** Minimization probleminde Vargha–Delaney A12 düşük fitness lehine yorumlanmalı.
## 11. Önerilen Sonraki Deney
Tam koşuya geçmeden önce küçük doğrulama koşusu önerilir:
- Fonksiyonlar: F1, F3, F10, F20
- Boyut: 30D
- Seeds: 5 veya 10
- FE: 300k
- Konfigürasyonlar: OrbitalOnly, OrbitalPauli static, OrbitalPauli dynamic, OrbitalEscape, Full static, Full dynamic

Amaç Pauli’nin gerçekten aktif olup olmadığını, dynamic epsilon’un static epsilon’dan ayrışıp ayrışmadığını ve escape’in F1’deki bozucu etkisinin sürüp sürmediğini doğrulamaktır.
## 12. Nihai Değerlendirme
| Boyut | Puan |
|---|---:|
| Deney altyapısı | 8.5 / 10 |
| Veri bütünlüğü | 8.0 / 10 |
| QWMO mekanizma doğrulaması | 4.0 / 10 |
| Makaleye doğrudan konabilirlik | 5.0 / 10 |
| Diagnostic değer | 9.0 / 10 |

**Son karar:** Bu 30D GCP koşusu başarılı bir pilot/diagnostic deneydir; final Faz-1 kanıtı değildir. Kod düzeltmeleri ve kısa doğrulama koşusu tamamlandıktan sonra 30D sonuçları yeniden üretilmelidir.
