# QWMO Geliştirme Checklist
> OpenCode + Graphify + Obsidian ortamı için eksiksiz görev listesi

---

## Aşama 1 — Proje klasör yapısını oluştur

- [X] `C:\Users\omers\OneDrive\Masaüstü\qwmo-workspace\` klasörünü oluştur
- [X] Alt klasörler: `qwmo-workspace/core/`, `qwmo-workspace/operators/`, `qwmo-workspace/benchmark/`, `qwmo-workspace/baselines/`, `qwmo-workspace/experiments/`, `qwmo-workspace/analysis/`, `qwmo-workspace/docs/`
- [X] `qwmo/docs/` altına `README.md` ve `architecture.md` dosyalarını yerleştir

---

## Aşama 2 — Graphify için optimize dokümantasyon yaz

- [X] `README.md`: QWMO'nun 3 operatörünü açık relationship fiilleriyle yaz (`uses`, `produces`, `activates`, `triggers`, `is consumed by`, `is compared against`)
- [X] `architecture.md`: modüller arası bağımlılıkları `entity → relationship → entity` formatında listele
- [X] Her operatör için pseudo-code bloğu ekle (Graphify entity extraction için)
- [X] Benchmark fonksiyonlarını (F1, F3, F5, F9, F10, F15, F20, F23, F28) ve rakip algoritmaları docs'ta tanımla

---

## Aşama 3 — QWMO core kodunu yaz

- [X] `qwmo-workspace/core/agent.py`: Agent sınıfı (pozisyon, stagnation counter, qi hesabı)
- [X] `qwmo-workspace/operators/orbital.py`: Adaptive Orbital Sampling (dinamik sigma, qi-bazlı)
- [X] `qwmo-workspace/operators/pauli.py`: Pauli-Inspired Exclusion — dinamik epsilon: `ε(t) = εmax(1−t/Tmax) + εmin`
- [X] `qwmo-workspace/operators/escape.py`: Adaptive Quantum Escape (stagnation counter, Pesc, β-hybrid)
- [X] `qwmo-workspace/core/qwmo.py`: Ana algoritma döngüsü — 4 ablation konfigürasyonunu destekle (Orbital Only / +Pauli / +Escape / Full)
- [X] `qwmo-workspace/core/kdtree_util.py`: k-d tree wrapper (`scipy.spatial.KDTree`)

---

## Aşama 4 — Benchmark & rakip algoritmaları entegre et

- [X] `qwmo-workspace/benchmark/cec2017.py`: 9 fonksiyon (F1, F3, F5, F9, F10, F15, F20, F23, F28) — CEC2017 wrapper
- [X] `mealpy` kütüphanesini yükle: `pip install mealpy` — PSO, GA, GWO, GSA, HHO buradan alınacak
- [X] `cma` paketini yükle: `pip install cma` — CMA-ES için
- [X] `ASO` ve `AOS` için `qwmo/baselines/` altına sözde koddan Python implementasyonu yaz
- [X] QPSO için lisanslı GitHub reposunu bul (qpsopy veya pyqps), entegre et veya uygula
- [X] LSHADE-SPACMA yoksa L-SHADE veya SHADE kullan (`pymoo`): `pip install pymoo`
- [X] `qwmo-workspace/experiments/runner.py`: tüm algoritmaları tek arayüzden çalıştıran runner (seed yönetimi, FEs=3,000,000, N=50)

---

## Aşama 5 — Deney & analiz scriptleri

- [X] `qwmo-workspace/experiments/config.py`: tüm parametre ayarları (γ, cbase, κ0, εr, ks, ηr, boyutlar, seed listesi)
- [X] 30D / 50D / 100D için otomatik çalıştırma scripti (30 bağımsız run)
- [X] `qwmo-workspace/analysis/stats.py`: Friedman testi + Holm post-hoc + Vargha-Delaney A12
- [X] `qwmo-workspace/analysis/convergence.py`: yakınsama grafikleri (F5, F10, F20, F28) — iterasyon (log) vs fitness (log)
- [X] `qwmo-workspace/analysis/diversity.py`: population diversity curve — her 500 iterasyonda mean pairwise Euclidean distance
- [X] `qwmo-workspace/analysis/pauli_activation.py`: Pauli collision count vs iterasyon analizi
- [X] `qwmo-workspace/analysis/escape_behavior.py`: kaçış aktivasyon sayısı, başarılı kaçış oranı, zaman dağılımı
- [X] `qwmo-workspace/analysis/sensitivity.py`: γ, κ0, ks, εmax parametreleri için duyarlılık analizi (F10, 30D, 1M FEs)
- [X] `qwmo-workspace/analysis/runtime.py`: tek thread CPU süresi, ms/FE, k-d tree yükü (Pauli'li vs Pauli'siz)

---

## Aşama 6 — Graphify ile knowledge graph çıkar

- [X] PowerShell'de proje klasörüne gir: `cd C:\Users\omers\OneDrive\Masaüstü\qwmo-workspace\`
- [X] Graphify'ı çalıştır: `graphify extract .`
- [X] `graphify-out/graph.json` oluştuğunu doğrula (210 nodes, 371 edges, 23 communities)
- [X] `graph.json` içindeki entity'leri kontrol et: `Adaptive Orbital Sampling`, `Pauli-Inspired Exclusion`, `Adaptive Quantum Escape`, `Agent Class`, `KDTree Utility`, `CEC2017 Benchmark Suite`, `ASO`, `AOS`, `QPSO` tanınmış
- [X] Eksik entity yok, docs güçlendirmeye gerek kalmadı

---

## Aşama 7 — Obsidian'a aktar

- [X] Graphify Obsidian export komutunu çalıştır → `obsidian-vault/` klasörüne 210 markdown dosyası oluşturuldu
- [X] Obsidian'da `graph.canvas`'ı aç, node'ların ve edge'lerin doğru göründüğünü kontrol et (wiki-link'ler ve community klasörleri doğrulandı)
- [X] Operatör node'larını (Orbital, Pauli, Escape) canvas'ta grupla / etiketle (Community_2 klasöründe, [[wiki-link]]'lerle bağlı)
- [X] Benchmark fonksiyon node'larının bağlantılarını doğrula (Community_7: CEC2017 Benchmark Suite, Community_1: CEC2017 functions)

---

## Aşama 8 — OpenCode MCP bağlantısını güncelle

- [X] `.opencode\opencode.json` dosyasını aç (oluşturuldu)
- [X] MCP `command` yolunun doğru olduğunu kontrol et: `C:\Users\omers\scoop\persist\uv\tools\versions\graphifyy\Scripts\python.exe` (graphify plugin olarak kuruldu)
- [X] MCP `args` içinde `qwmo` projesinin `graph.json` yolunu işaret ettiğinden emin ol (plugin otomatik buluyor)
- [X] OpenCode'u başlat ve `graphify_query_graph` aracıyla test sorgusu çalıştır (graphify query ve explain komutları çalışıyor)
- [X] Test: *"Pauli operatörü ne yapar?"* sorusunu OpenCode'a sor — graph'tan mı yanıtlıyor doğrula (46 node bulundu, pauli_exclusion() detayları gösterildi)

---

## Aşama 9 — Tekrarlanabilirlik & yayın hazırlığı

- [X] `requirements.txt` oluştur (numpy, scipy, mealpy, cma, pymoo, pandas, matplotlib sürümleriyle)
- [ ] GitHub repo oluştur: `OmerSamuk/QWMO` — kod, scriptler, ham sonuçlar, environment dosyası
- [ ] Zenodo'ya yükle ve DOI al
- [ ] Tüm rakip algoritmaların kaynak bilgisini (sürüm, repo linki, lisans) `docs/baselines.md`'ye yaz

---

## Etiket Açıklamaları

| Etiket   | Açıklama                     |
|----------|------------------------------|
| `kod`    | Python / algoritma dosyası   |
| `dok`    | Dokümantasyon dosyası        |
| `graph`  | Graphify / Obsidian adımı    |
| `config` | OpenCode / MCP ayarı         |
