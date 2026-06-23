# QWMO Araştırma Günlüğü ve Teknik Değerlendirme Raporu

> 📚 **Related Notes:** [[../00-index|Vault Index]] · [[../03-pilots-overview|Pilot History]] · [[../../charters/qwmo-gapr-test|Faz-1 Charter]] · [[../04-phase1-decision|Phase-1 Decision]]

## QWMO → Dynamic Epsilon → GAPR Evrimi

**Yazar:** Ömer Samuk ve Yapay Zeka Araştırma Ekibi
**Durum:** Araştırma Hattı Devam Ediyor
**Tarih:** 2026

---

# 1. Başlangıç Noktası

Araştırmanın başlangıç amacı, kuantum esinli bir sürekli optimizasyon algoritması geliştirmekti.

Bu amaçla aşağıdaki üç operatörden oluşan QWMO (Quantum Wave Motion Optimization) algoritması tasarlandı:

1. Orbital Motion
2. Pauli Exclusion
3. Adaptive Quantum Escape

İlk preprint çalışması tamamlandı ve yayınlandı.

Algoritma çeşitli benchmark fonksiyonlarında umut verici sonuçlar verdi.

Ancak ilk çalışma sırasında şu kritik soru henüz cevaplanmamıştı:

> Pauli operatörü gerçekten katkı sağlıyor mu?

---

# 2. İlk Büyük Keşif: Ablasyon Analizi

Preprint sonrasında algoritmanın iç mekanizmasını anlamak amacıyla sistematik ablasyon çalışmaları gerçekleştirildi.

Karşılaştırılan yapılandırmalar:

* Orbital Only
* Orbital + Pauli
* Orbital + Escape
* Full QWMO

Sonuçlar beklenmedik bir tablo ortaya koydu.

Orbital + Escape konfigürasyonu ile Full QWMO çoğu durumda benzer performans gösteriyordu.

Buna karşılık:

Orbital + Pauli ≈ Orbital Only

davranışı gözlemlendi.

Bu durum Pauli operatörünün neredeyse hiç katkı üretmediğini gösteriyordu.

Bu sonuç araştırmanın yönünü tamamen değiştirdi.

---

# 3. İlk Hipotez: Statik Epsilon Problemi

Pauli operatörünün çalışmamasının nedeni olarak sabit dışlama yarıçapı (static epsilon) hipotezi ortaya atıldı.

Orijinal QWMO'da:

ε = sabit

olarak tanımlanmıştı.

Hipotez:

> Yüksek boyutlu uzaylarda ajanlar birbirinden çok uzak kalıyor ve sabit epsilon nedeniyle Pauli operatörü neredeyse hiç tetiklenmiyor.

Bu nedenle ilk revizyon olarak Dynamic Epsilon çalışması başlatıldı.

---

# 4. Dynamic Epsilon Aşaması

Yeni yaklaşım:

ε(t) = εmax(1 − t/Tmax) + εmin

şeklinde lineer azalan bir epsilon fonksiyonu kullanılmasıydı.

Amaç:

* başlangıçta büyük etkileşim alanı
* ilerleyen iterasyonlarda daha hassas dışlama

oluşturmaktı.

Pilot sonuçlar önemli bir keşif ortaya çıkardı:

* Pauli operatörü artık aktifleşiyordu.
* Collision sayıları artıyordu.
* Displacement sayıları artıyordu.

Ancak:

* Nihai fitness sonuçlarında anlamlı bir sıçrama oluşmuyordu.

Bu aşamada şu sonuç elde edildi:

> Pauli'nin çalışması ile faydalı olması aynı şey değildir.

Bu araştırmanın ikinci büyük kırılma noktası oldu.

---

# 5. İkinci Hipotez: Geometri Farkındalığı

Dynamic Epsilon deneyleri sonucunda yeni soru ortaya çıktı:

> Sorun zaman mı, yoksa popülasyon geometrisini bilmiyor olmak mı?

Bunun üzerine yeni yaklaşım geliştirildi:

Geometry-Adaptive Pauli Radius (GAPR)

Temel fikir:

Epsilon'un zamana göre değil, popülasyon yoğunluğuna göre değişmesi.

İlk formül:

ε = λ × mean_kNN

şeklindeydi.

---

# 6. İlk GAPR Deneyi

İlk GAPR pilotunda ciddi bir problem ortaya çıktı.

Epsilon sürekli üst sınıra (eps_max) çarpıyordu.

Sonuç:

* epsilon adaptif davranmıyordu
* sistem büyük bir statik epsilon gibi davranıyordu

Ancak bu başarısızlık önemli bir bilgi üretti:

Yüksek boyutlarda kNN mesafeleri beklenenden çok daha büyük ölçeklerdeydi.

Bu nedenle yeni normalizasyon yaklaşımı geliştirildi.

---

# 7. Diagonal-Normalized GAPR

Yeni formül:

ε_GAPR(t) =
clip(
λ₀ × d̄_kNN(t)/L_max × (u-l),
ε_min,
ε_max
)

L_max = √D × (u-l)

olarak tanımlandı.

Amaç:

* boyut bağımlılığını azaltmak
* yüksek boyutlarda daha tutarlı epsilon davranışı üretmek
* popülasyon yoğunluğunu ölçekten bağımsız ölçmek

---

# 8. GAPR Pilot v1 Sonuçları

İlk normalize edilmiş GAPR pilotu önemli bulgular verdi.

Gözlemler:

* Pauli ilk kez ciddi biçimde aktive oldu.
* Collision sayıları belirgin şekilde arttı.
* Success oranları yükseldi.
* Escape–Pauli etkileşimi ortaya çıktı.

Ancak:

* Epsilon hâlâ birçok durumda üst sınıra yapışıyordu.
* Performans kazanımları tutarlı değildi.

Bu aşamada araştırma şu noktaya geldi:

> GAPR doğru yön olabilir, ancak mevcut formül nihai çözüm değildir.

---

# 9. Comprehensive Pilot

Daha kapsamlı bir pilot tasarlandı.

Fonksiyonlar:

* F5
* F10
* F15
* F20
* F28

Konfigürasyonlar:

* OrbitalOnly
* OrbitalEscape
* Full_Static
* Full_Dynamic
* Full_GAPR
* OrbitalPauli_GAPR

Amaç:

* Pauli'nin gerçekten çalışıp çalışmadığını anlamak
* Escape-Pauli ilişkisini incelemek
* GAPR'ın davranışını ölçmek

Sonuç:

Pauli aktive oluyordu.

Ancak:

OrbitalPauli_GAPR tek başına güçlü değildi.

Bu bulgu yeni bir yoruma yol açtı:

> Pauli bağımsız bir operatör değildir.
>
> Escape ile birlikte çalışan bir çeşitlilik düzenleme mekanizmasıdır.

---

# 10. Revision Pilot (eps_max = 0.10)

Bir sonraki adımda:

eps_max_ratio

0.15'ten

0.10'a düşürüldü.

Amaç:

* saturasyonu azaltmak
* epsilon'un daha fazla değişebilmesini sağlamak

Yeni sonuçlar:

R1 FAIL
R2 FAIL
R3 PASS
R4 PASS

olarak raporlandı.

Temel bulgular:

* Pauli hâlâ aktifti.
* Collision ve displacement üretmeye devam etti.
* Ancak epsilon yine büyük ölçüde üst sınıra çarpıyordu.
* Adaptif davranış beklenen seviyeye ulaşmadı.

Bu sonuç kritik bir bilimsel sonuca işaret etti:

> Sorun artık parametre değildir.
>
> Sorun mevcut GAPR formülünün kendisidir.

---

# 11. Bugün Bildiklerimiz

Araştırma sonunda aşağıdaki sonuçlar yüksek güvenle doğrulanmıştır.

## Doğrulananlar

✓ Statik epsilon yüksek boyutlarda yetersizdir.

✓ Pauli operatörü aslında tamamen ölü değildir.

✓ Dynamic epsilon Pauli'yi aktive eder.

✓ GAPR Pauli aktivasyonunu daha da artırabilir.

✓ Escape ve Pauli arasında güçlü bir etkileşim vardır.

✓ Collision sayısını artırmak tek başına çözüm değildir.

✓ Daha fazla Pauli aktivasyonu her zaman daha iyi fitness üretmez.

✓ Diversity koruma ile performans arasında denge vardır.

---

## Henüz Doğrulanmayanlar

✗ GAPR mevcut haliyle nihai çözümdür.

✗ Adaptif epsilon sistematik olarak performansı artırır.

✗ QWMO-GAPR statik QWMO'dan açık şekilde üstündür.

✗ Pauli'nin optimum çalışma rejimi bulunmuştur.

---

# 12. Araştırmanın Geldiği Nokta

Araştırmanın bugünkü temel sorusu artık:

> QWMO çalışıyor mu?

değildir.

Bugünkü temel soru:

> Pauli exclusion operatörü yüksek boyutlu optimizasyonda neden başarısız olur ve hangi koşullarda faydalı hale gelir?

sorusudur.

Bu soru ilk preprint sırasında sorulamıyordu.

Bugün ise bu soruya cevap verebilecek deneysel altyapı oluşmuştur.

---

# 13. Genel Değerlendirme

Araştırma hattı başarısız olmamıştır.

Ancak başlangıçta düşünülen hikâye değişmiştir.

İlk hedef:

> Yeni bir metaheuristic geliştirmek

iken,

araştırma zamanla şu noktaya evrilmiştir:

> Yüksek boyutlu optimizasyonda exclusion mekanizmalarının davranışını anlamak ve yeniden tasarlamak.

Bilimsel açıdan en büyük kazanım budur.

Çünkü bugün:

* Pauli'nin neden çalışmadığını,
* nasıl aktive olduğunu,
* ne zaman faydalı olduğunu,
* ne zaman zarar verdiğini,

başlangıca göre çok daha iyi anlayabiliyoruz.

Bu bilgi, algoritmanın mevcut performansından daha değerli olabilir.

---

# 14. Nihai Sonuç

QWMO araştırma hattı sona ermemiştir.

Ancak mevcut GAPR formülü araştırma problemini tamamen çözememiştir.

Bugünkü durum:

* QWMO preprint → tamamlandı
* Dynamic Epsilon → incelendi
* GAPR → kısmen başarılı
* GAPR formülü → henüz nihai değil
* Pauli problemi → ilk kez anlaşılmaya başlandı

Dolayısıyla araştırmanın bugünkü çıktısı:

> Yeni ve kesin olarak üstün bir algoritma

değil,

> Pauli exclusion mekanizmasının davranışına ilişkin sistematik ve deneysel bir anlayış

olarak özetlenebilir.

Bu, araştırma hattının şimdiye kadarki en önemli bilimsel kazanımıdır.
