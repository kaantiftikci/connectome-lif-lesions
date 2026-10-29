# sinek — Araştırma Planı

**Başlık (çalışma):** Konnektom kısıtlı sinek beyninde hücre tipi çözünürlüklü
ilerleyici lezyonlar ve amortize ters model: davranış fenotipinden hasar
örüntüsünü çıkarmak.

Tarih: 2026-10-28. Durum: faz 0 (altyapı) tamamlandı, faz 1 başladı.

## 1. Soru

Sinek, Parkinson ve tauopati modellerinin en yaygın hayvanı. Bu modellerde
belirli hücre kümeleri kaybolur (Parkinson: PPL1 ve PAM dopamin kümeleri;
tau: Kenyon hücreleri) ve ölçülebilir davranış bozuklukları ortaya çıkar
(tırmanma, yürüme hızı, koku öğrenme, uyku). Tüm beyin konnektomu ve
Shiu et al. 2024'ün LIF modeliyle artık şu sorular sorulabilir:

1. **Sessiz rezerv.** Bir dopamin kümesinin yüzde kaçı kaybolunca inen
   nöron (davranış) çıktısı değişir? Parkinson'da belirtiler yaklaşık yüzde
   altmış kayıptan sonra görünür. Model aynı eşiği üretiyor mu?
2. **Özgüllük.** Aynı büyüklükte dopaminerjik olmayan bir kayıp (ör. Kenyon,
   MBON, mAL) aynı fenotipi üretir mi? Üretmiyorsa fark nerede?
3. **Ters problem.** Gözlenen bir fenotipten, hangi hücre tiplerinin ne
   oranda kaybolduğu geri çıkarılabilir mi, hangi kümeler birbirine karışır?
4. **Cinsiyet.** Aynı lezyon dişi (FlyWire) ve erkek (MaleCNS) beyinde farklı
   kırılganlık gösteriyor mu?

## 2. Benzer çalışma ve fark

arXiv 2610.19153 (Ekim 2026) MaleCNS üzerinde amiloid benzeri hasar
(eşik düşürme, sinaps ve nöron kaybı) uygular; hasar rastgele ya da hub
derecesine göre seçilir, büyüklükler varsayılır, okuma kokuya verilen
tüm-beyin aktivitesidir, davranış ve gerçek fenotiplerle karşılaştırma yoktur,
öğrenme yoktur.

| Boyut | 2610.19153 | sinek |
|---|---|---|
| Hedef | rastgele / hub | hastalığa özgü hücre tipleri (PPL1, PAM, KC...) |
| Zaman | tek seferlik | ilerleyici, iç içe (nested) seriler |
| Okuma | koku aktivitesi | inen nöron + MBON popülasyon hızları, faz 2'de gövdeli davranış |
| Cinsiyet | erkek | dişi + erkek |
| Yapay zeka | yok | vekil model (surrogate) + nöral posterior tahmini (NPE) + ters tarama |

## 3. Yapay zeka bileşeni

İleri model `x = S(θ)`: θ ∈ [0,1]^K lezyon vektörü (K grup × kayıp oranı),
x fenotip vektörü (uyaran × okuma grubu hız matrisi, log ölçek).

1. **Vekil model** `sinek.surrogate.Surrogate`: MLP topluluğu, θ → x.
   Simülatör 1 s için ~25 s sürer, vekil mikrosaniye. Kullanımları:
   * **Duyarlılık haritası:** ∂x/∂θ tek geri yayılımla tüm grupları sıralar.
   * **Ters tarama:** hedef bir fenotip imzasını (ör. tam PPL1 kaybı) yeniden
     üreten *en seyrek* lezyonu gradyanla arar. "PPL1 kaybını hangi
     dopaminerjik olmayan kayıp taklit eder?" sorusunun cevabı, deneysel
     olarak test edilebilir yeni bir hipotez olur.
2. **Amortize ters model** `sinek.inference.LesionPosterior`: sbi
   kütüphanesiyle NPE (normalize edici akış). Bir kez eğitilince her
   gözlenen fenotip için posterior tek ileri geçiş. Doğrulama: bilinen
   lezyonları kendi fenotiplerinden geri bulma, simülasyon tabanlı
   kalibrasyon (SBC), posterior korelasyonlarıyla tanımlanabilirlik.
3. **(Faz 3) Öğrenilen nöromodülasyon:** Shiu modeli dopamini yalnızca
   uyarıcı sayar. Mantar gövdesi KC→MBON sinapslarında dopamin kapılı bir
   kazanç parametresi ekleyip bilinen öğrenme fenotiplerinden öğrenmek,
   dopamin kaybı sorusu için modelin en zayıf varsayımını düzeltir.

## 4. Fazlar

**Faz 0 — altyapı (tamam).**
* NumPy LIF, Shiu modelinin birebir yeniden uygulaması. Doğrulama: Shiu'nun
  repodaki Brian2 çıktısıyla (21 şeker GRN, 200 Hz, FlyWire 630) nöron
  bazında Pearson r = 0.963; 5 Hz üstü 333 nörondan 320'si aynen bulundu,
  7 yanlış pozitif. `scripts/validate_vs_shiu.py`.
* Hücre tipi çözünürlüklü, iç içe, üç mekanizmalı lezyon (`remove`,
  `silence_out`, `synapse_scale`).
* Fenotip vektörü, uyaran bataryası, okuma grupları.
* Vekil ve NPE sarmalayıcıları (torch/sbi tembel içe aktarılır).

**Faz 1 — dişi beyinde in-silico (devam ediyor).**
* `scripts/progressive_curve.py`: PPL1, PAM, KC için sessiz rezerv eğrileri.
* `scripts/run_lesion_sweep.py`: ~500-2000 (θ, x) çifti (4 çekirdekte
  ~1 dk/örnek; GPU'lu makinede torch.sparse ile hızlandırılabilir).
* `scripts/train_surrogate.py`: vekil R², duyarlılık, posterior geri bulma,
  ters tarama.
* Çıktı: önbaskı kalitesinde 3 şekil (rezerv eğrileri, duyarlılık haritası,
  posterior geri bulma matrisi).

**Faz 2 — gövdeli okuma.** FlyGym/NeuroMechFly v2 ile inen nöron çıktısını
yürüme hızı ve negatif geotaksiye çevirmek; gerçek Parkinson-model sinek
tırmanma eğrileriyle karşılaştırmak (literatürde yüzlerce ölçüm var).

**Faz 3 — erkek beyin ve cinsiyet farkı.** MaleCNS v1.0 yükleyici
(neuPrint token gerekir; bu oturumda ağ kapalı). Aynı grup seçicileri
(`sinek.data.groups`) erkek etiketlerine çözümlenir; aynı lezyon, aynı
batarya, kırılganlık farkı.

## 5. Kararlı rejim (önemli teknik not)

Model bistabil: 32 şeker GRN'i 150 Hz'de ~400 aktif nöron (Shiu ile uyumlu)
üretirken, 25 "sugar/low_salt" GRN'i de eklenince ~9.000 nöron refrakter
tavanında (435 Hz) kilitlenen bir kaçak çekiciye düşer. Lezyon deneyleri
kararlı rejimde kalmalı; bu yüzden batarya küçük, tanımlı popülasyonlar
kullanır (32 şeker, 30 su, 42 acı, 68 ORN_DM1). Kaçak eşiğinin lezyonla
nasıl kaydığı başlı başına bir sonuç olarak raporlanacak.

## 6. Riskler

* LIF modelinde nöromodülasyon, bazal ateşleme ve gap junction yok; dopamin
  uyarıcı sayılır. Dopamin kaybı için en kötü varsayım; faz 3 bunu hedefler
  ve makalede açıkça belirtilir.
* Fenotip vektörü davranışın vekilidir; faz 2 olmadan "tırmanma" iddiası
  yapılamaz.
* Dişi FlyWire'da VNC yok; motor çıktı inen nöronlarda biter.
* Alan hızlı: MaleCNS yayınından bu yana 8 haftada 80'den fazla repo.
  Avantaj, doğrulanmış simülatör ve ters model; hobi projelerinde yok.

## 7. Veri ve kaynaklar

* FlyWire v783 bağlantı tablosu ve Shiu modeli: github.com/philshiu/Drosophila_brain_model (MIT)
* Hücre tipi etiketleri: github.com/flyconnectome/flywire_annotations (Schlegel et al. 2024)
* MaleCNS v1.0: male-cns.janelia.org (neuPrint)
* Shiu et al. 2024, Nature 634:210. Lappalainen et al. 2024, Nature 634:1132.
  Robie et al. 2017, Cell 170:393 (davranış taraması, faz 2 doğrulama verisi).

## 8. Faz 1 ilk sonuçlar (2026-10-28, tek deneme, tek lezyon sırası)

Dişi FlyWire v783, 4 uyaran (şeker, su, acı, ORN_DM1) × 109 okuma grubu =
436 özellik, 500 ms. Gürültü tabanı (sağlam beyin, 3 tohum): L2 ortalama
0.82, en çok 0.97; tohumlar arası 7 özellik >0.1 değişiyor.

| Grup | n | %20 | %40 | %60 | %80 | %100 | Biçim |
|---|---|---|---|---|---|---|---|
| PPL1 | 16 | 1.22 | 1.15 | 3.02 | 6.14 | 6.26 | **sigmoid, eşik ~%50-60, sessiz rezerv** |
| PAM | 307 | 2.86 | 2.92 | 2.88 | 2.90 | 2.98 | **basamak: %20'de tam etki, sonra düz** |
| KC (kontrol) | 5177 | 4.13 | 6.37 | 11.99 | 21.39 | 25.57 | **doğrusal/hızlanan, rezerv yok** |

(L2 uzaklık = sağlam beyinden, log-hız özellikleri üzerinde.)

Yorum ve uyarılar:
* PPL1 eğrisi Parkinson'daki "belirtiler ~%60 kayıptan sonra" gözlemiyle
  aynı biçimde. Ama 16 nöronluk bir kümede hangi nöronların önce gittiği
  eşiği belirler; bu tek bir rastgele sıralama. Yapılacak: 10+ lezyon sırası
  × 3 simülasyon tohumu, ve alt tip bazında (PPL101..108) lezyon.
* PAM etkisinin neredeyse tamamı tek özellik: koku altında MBON29 çıkışı
  %20 kayıpta 2.77'den 0'a düşüyor ve bir daha değişmiyor. Yani küçük bir
  PAM alt tipi MBON29'u doğrudan sürüyor; model bunu kapı gibi gösteriyor.
  Bağlantı izi: MBON29'un en güçlü dopaminerjik girdisi PAM08 (iki MBON29
  nöronuna 38 ve 18 mV toplam ağırlık; PAM01 7 ve 4 mV). %20 lezyon 6 PAM08
  nöronu götürüyor ve MBON29'un koku cevabı eşik altına düşüp sıfırlanıyor.
  Yani eşiğin hemen üstünde çalışan bir devrenin kırılganlığı; büyüklük
  değil, hangi alt tipin kaybolduğu belirleyici. Alt tip çözünürlüklü
  lezyon (PAM01..15 ayrı gruplar) bir sonraki tarama için şart.
* Her üç grupta da etki koku→MBON özelliklerinde; inen nöron (davranış
  vekili) özellikleri neredeyse hiç kıpırdamıyor (PAM'da DNp41 -0.49 en
  büyüğü). Bu, (a) LIF'te dopaminin doğrudan uyarıcı sayılmasının ve
  (b) kısa koku uyaranının inen nöronlara zayıf yansımasının sonucu.
  Faz 3'teki nöromodülasyon katmanı ve faz 2'deki gövdeli okuma tam bu
  boşluk için.
* Özgüllük sorusu için ilk cevap: büyüklük eşleştirilmiş olmasa da KC
  kaybı tamamen farklı bir eğri veriyor; dopamin kümeleri "rezerv/basamak",
  KC "doğrusal". Büyüklük eşleştirilmiş kontroller (ör. 16 rastgele
  merkezi nöron, 307 rastgele merkezi nöron) sıradaki deney.

## 9. Ters model hattının durumu (2026-10-28)

Uçtan uca çalışıyor: `run_lesion_sweep.py` → `train_surrogate.py`
(vekil + NPE + ters tarama). İlk veri seti: 60 karışık lezyon (8 grup,
seyreklik 0.5), 436 özellik.

| Ölçüm | Değer | Anlamı |
|---|---|---|
| Değişen özellik | 53 / 436 | tat uyaranları ve inen nöronların çoğu bu lezyonlardan etkilenmiyor |
| Ridge vekil, 5 kat CV R² | 0.49 | öğrenilebilir sinyal var |
| MLP topluluğu, 5 kat CV R² | 0.39 | 60 örnekte aşırı uyum; ridge varsayılan taban çizgisi oldu |
| NPE posterior ortanca hatası | 0.22-0.36 | düzgün prior'un hatasıyla aynı (~0.33): 60 örnek NPE için yetersiz |
| Duyarlılık sırası | MBON 92, KC 86, PPM1 17, LHLN 16, PPL2 13, PPL1 13, mAL 11, PAM 10 | MB'nin kendisi dopamin kümelerini 5-9 kat eziyor |

Çıkarımlar ve sıradaki adımlar:
1. **Kontrolleri ayrı taramaya al.** KC ve MBON lezyonları aynı taramada
   olduğunda dopamin etkisi maskeleniyor. Dopamin odaklı tarama
   (`--groups PAM PPL1 PPL2 PPM1`) başlatıldı; büyüklük eşleştirilmiş
   kontroller ayrı taramada.
2. **Örnek sayısı.** NPE için en az 500-1000 çift gerekir. Bu makinede
   örnek başına ~55 s (500 ms, 4 uyaran); 2 işlemle ~7 saat/500 örnek.
   GPU'da torch.sparse ile 10-50 kat hızlanır; bu ilk yerel iş.
3. **Bellek.** Her işlem konnektomu ayrı yüklüyor (~1.2 GB + yükleme
   tepesi). 15 GB'lık makinede 3 işlem + eğitim OOM verdi; 2 işlem güvenli.
   Paylaşımlı bellek (np.memmap üzerinden CSR) ile 4+ işlem mümkün.
4. **Alt tip çözünürlüğü.** PAM08→MBON29 bulgusu grupların alt tipe
   bölünmesini zorunlu kılıyor (PAM01..15, PPL101..108 → K ≈ 30).
5. **Özellik tasarımı.** Sabit 383 özellik atılıyor; inen nöron okumaları
   için daha uzun süre (1-2 s) veya mekanosensör uyaran eklenmeli, aksi
   halde "davranış vekili" fiilen MBON çıkışına indirgeniyor.

## 10. Dopamin odaklı tarama: ters problemin ilk cevabı (2026-10-28)

80 lezyon, yalnızca PAM / PPL1 / PPL2 / PPM1 (seyreklik 0.4), kontroller
sağlam. `artifacts/sweep_v1_da80.npz`.

| Ölçüm | PAM | PPL1 | PPL2 | PPM1 |
|---|---|---|---|---|
| Duyarlılık (ridge, Σ\|∂x/∂θ\|) | 4.4 | **13.6** | 2.2 | 1.5 |
| NPE posterior ortanca hatası (prior ≈ 0.33) | **0.15** | **0.11** | 0.34 | 0.29 |

Vekil 5 kat CV R²: ridge 0.46, MLP 0.43. Değişen özellik 46/436.

* **PAM ve PPL1 kaybı fenotipten geri çıkarılabiliyor**, 80 örnekle bile
  prior'un 2-3 katı daha iyi. Bu, "gözlenen fenotipten hasar örüntüsünü
  çıkarma" fikrinin modelde çalıştığının ilk kanıtı.
* **PPL2 ve PPM1 tanımlanamıyor:** bu uyaran bataryası altında çıktıya
  neredeyse hiç yansımıyorlar (duyarlılık 1.5-2.2). Ya batarya genişlemeli
  (bu kümelerin hedeflediği devreleri süren uyaranlar) ya da bu kümelerin
  kaybının bu modelde sessiz olduğu raporlanmalı; ikisi de sonuç.
* **PPL1 en duyarlı küme**: 16 nöron, PAM'ın 307 nöronundan 3 kat büyük
  etki. Kırılganlık nöron sayısıyla değil, bağlantı konumuyla ilgili;
  2610.19153'ün hub bulgusunun hücre tipi düzeyinde karşılığı.
* **Ters tarama:** tam PPL1 kaybını taklit etmeye en yakın dopaminerjik
  lezyon %13 PAM, ama uyum zayıf; yani PPL1 imzası bu grup kümesi içinde
  benzersiz. Kontrol gruplarını da içeren taramada "MBON %8" çıkmıştı.
  Alt tip çözünürlüklü tarama bu soruyu asıl cevaplayacak.

## 11. Faz 1a sonucu: tekrarlı ilerleyici lezyonlar (2026-10-29)

6 uyaran × 109 okuma = 654 özellik; 5 lezyon sırası × 2 simülasyon tohumu;
büyüklük eşleştirmeli rastgele kontroller RND16 ve RND307 (merkezi beyin,
DAN ve KC hariç). Gürültü tabanı: sağlam tekrarlar arası L2 1.68, sağlam
tekrarın ortalamadan uzaklığı 0.84. `artifacts/figures/fig1_reserve_curves.png`,
`artifacts/progressive_v1_replicated.csv.gz`.

| Grup | n | %20 | %40 | %60 | %80 | %100 | Yorum |
|---|---|---|---|---|---|---|---|
| PPL1 | 16 | 1.49±0.31 | 2.37±0.70 | 3.52±1.57 | 4.09±1.97 | 6.19±0.00 | büyük, sıraya bağlı (iki modlu) |
| PAM | 307 | 1.58±0.66 | 2.53±0.65 | 2.62±0.39 | 2.94±0.02 | 3.00±0.02 | %40'ta doyuyor |
| PPL2 | 8 | 1.02 | 0.96 | 1.01 | 0.95 | 1.04 | gürültü |
| PPM1 | 16 | 0.85 | 0.86 | 0.86 | 0.87 | 0.87 | gürültü |
| RND16 | 16 | 0.85 | 0.89 | 0.92 | 0.94 | 0.97 | gürültü |
| RND307 | 307 | 1.29±0.36 | 1.49±0.33 | 1.63±0.29 | 1.59±0.27 | 1.77±0.24 | zayıf, gürültü sınırında |

**Özgüllük cevabı:** PPL1 (16 nöron) tam kaybı, aynı büyüklükteki rastgele
kayıptan 6 kat (6.19 / 0.97), PAM (307) 1.7 kat (3.00 / 1.77) daha büyük
etki yapıyor. PPL2 ve PPM1 bu bataryada hiç görünmüyor.

**"Sessiz rezerv" yeniden yorumu.** İlk tek-sıra deneyindeki sigmoid, sıralar
üzerinden ortalama alınınca büyük varyansla geliyor: PPL1 %60 kayıpta
L2 1.96 ile 6.28 arasında. Bağlantı izi nedenini gösteriyor: her PPL1 alt
tipi bir MBON'u neredeyse tek başına sürüyor (etiketli hat):

| Kaynak | Hedef | Toplam ağırlık (mV) | Rakip girdi |
|---|---|---|---|
| PPL105 | MBON13 | 78.6 | PPL103 1.4 |
| PPL103 | MBON31 | 60.8 | PPL107 0.8 |
| PAM08 | MBON29 | 56.4 | PAM01 11.6 |
| PPL104 | MBON28 | 20.1 | PPL107 1.9 |

Her hat anahtar gibi kapanıyor (MBON cevabı ya tam ya sıfır). Fenotip
uzaklığı kesilen hat sayısını sayıyor; yüzde-kayıp eğrisi bu sayının
sıralar üzerindeki beklentisi. Yani modelde dopamin kaybı için kademeli bir
rezerv yok, hücre tipi düzeyinde ya hep ya hiç var. Gerçek sineklerde
tırmanma kademeli azalıyor; bu fark modelin (dopamin = doğrudan uyarı)
eksik bıraktığı kademeli nöromodülasyon katmanına işaret ediyor. Faz 3'ün
gerekçesi doğrudan bu tablo.

Not: eğri gerçekten "kaç hat kesildi" ise alt tip çözünürlüklü tarama (1c)
grupları değil hatları öğrenmeli; tam da o tarama çalışıyor.

## 12. Faz 2 sonucu: gövdeli okuma (2026-10-29)

Hat: lezyon → tüm-beyin LIF → inen nöron (DN) hızları (sol/sağ) → sağlam
beyne göre sürücü → NeuroMechFly v2 (flygym 2.1.1) hibrit dönüş kontrolcüsü
→ düz zeminde ve 30° eğimde 1 s yürüyüş. `sinek/embodied/`,
`scripts/embodied_lesion.py`, `artifacts/embodied_v*.csv`. Kontrolcü
sürücüye doğrusal cevap veriyor (1.0 → 12.8 mm/s, 0.5 → 6.5, 0.2 → 2.1); 30°
eğimde tırmanıyor, 45°'de kayıyor.

**Tek modaliteli uyaranla negatif sonuç.** Yalnızca mekanosensör uyaran
(rüzgar/yerçekimi ya da baş kılı) altında PPL1 %60/%100, PAM %100 ve KC %100
lezyonları DN hızlarını hiç değiştirmiyor (iki ondalığa kadar aynı); yürüyüş
aynı. Mantar gövdesi çıkışı bu uyaranlarda DN'lere hiç ulaşmıyor.

**Birleşik uyaranla (koku DM1 + rüzgar/yerçekimi) kademeli sonuç.** MB
lezyonları 140-200 DN'yi >0.5 Hz değiştiriyor, ama DN popülasyon
ortalaması yalnızca %1-3 oynuyor; etki belirli DN'lerde. Yürüme rolü
yayınlanmış DN tipleri (DNp09, DNa01-03, DNb01-02, DNg13; 8+8 nöron)
üzerinden sürücü alınınca:

| Koşul | Lokomotor DN sürücü (L/R) | Düz, mm/s | 30° eğim, mm/s | Değişim |
|---|---|---|---|---|
| sağlam | 1.00 / 1.00 | 12.75 | 11.88 | — |
| PPL1 %60 | 0.99 / 0.96 | 12.57 | 11.66 | −1 % |
| PPL1 %100 | 0.86 / 0.98 | 11.05 | 10.45 | **−13 %** |
| PAM %100 | 0.96 / 0.97 | 12.27 | 11.39 | −4 % |
| KC %100 | 0.72 / 1.00 | 8.71 | 8.69 | **−32 %** |
| RND16 | 0.99 / 0.99 | 12.65 | 11.76 | −1 % |
| RND307 | 1.07 / 1.05 | 13.42 | 12.59 | +5 % |

Yorum ve sınırlar:
* Model ilk kez davranış düzeyinde bir fark üretiyor: PPL1 kaybı yürüme ve
  tırmanma hızını düşürüyor, aynı büyüklükteki rastgele kayıp düşürmüyor.
  Yön doğru, büyüklük küçük: gerçek Parkinson-model sineklerde tırmanma
  kaybı 20-30 günde yaygın olarak %30-60 düzeyinde raporlanıyor (arama
  özetleri; birincil makaleler bu oturumdan okunamadı, yerelde doğrulanmalı).
* %60 PPL1 kaybında neredeyse hiç etki yok, %100'de var: faz 1a'daki
  etiketli-hat bulgusunun davranış karşılığı. Gerçek sinekteki kademeli
  düşüşü üretmek için faz 3 (nöromodülasyon) gerekiyor.
* Beyin→beden eşlemesi varsayımsal: 8+8 nöronluk alt küme, 3 beyin tohumu,
  belirleyici kontrolcü. DN'lerin yürüme hızına ağırlıkları öğrenilmiş
  değil; faz 3'te DN→hız eşlemesini gerçek yürüme kayıtlarıyla kısıtlamak
  doğal bir sonraki adım.
* Bu modelde sol lokomotor DN hızı (29 Hz) sağdan (9 Hz) çok yüksek;
  DM1 koku girdisi çift taraflı olduğu için bu asimetri konnektomdan
  geliyor, incelenmeli.

## 13. Faz 1c sonucu: alt tip çözünürlüklü tarama ve ters model (2026-10-29)

240 lezyon, 32 dopaminerjik alt tip (PAM01-15, PPL101-108, PPL201-204,
PPM1201-1205), seyreklik 0.85 (örnek başına ~5 alt tip), 6 uyaran × 109
okuma. `artifacts/sweep_v2_subtype240.npz`, `artifacts/surrogate_report_v2_subtype.npz`,
`artifacts/figures/fig2_sensitivity.png`, `fig3_posterior_recovery.png`.

| Ölçüm | Değer |
|---|---|
| Değişen özellik | 68 / 654 |
| Vekil 5 kat CV R² | ridge 0.33, MLP 0.31 |
| Duyarlılık, ilk üç | **PPL103 10.5**, PPL105 4.8, PAM08 4.6; geri kalan 29 alt tip 1.3-2.3 (gürültü düzeyi) |
| NPE, lezyonlu girişlerde ortanca hatası | 0.475 (sıfır-tahmin taban çizgisi 0.489, prior ortancası 0.268) |
| NPE, sağlam girişlerde hata | 0.009 |
| Alt tip bazında anlamlı geri bulma | PPL103 (r = 0.98, hata 0.20), PPL104 (r = 0.55); diğerleri yok |

**Yorum.** Vekil modelin duyarlılık haritası, bağlantı iziyle (bölüm 11)
elle bulunan üç etiketli hattı (PPL103→MBON31, PPL105→MBON13,
PAM08→MBON29) veriden bağımsız olarak en üste koyuyor; yöntem çalışıyor.
Ters model ise bu veri büyüklüğünde yalnızca en güçlü hattı öğreniyor ve
geri kalan 29 alt tip için seyrek prior'a çöküyor ("hepsi sıfır" diyor).
Nedeni belirsizlik değil, bilgi yokluğu: bu batarya altında 29 alt tipin
kaybı okumalara yansımıyor, dolayısıyla hiçbir ters model onları bulamaz.
Doğru sonuç şu: **bu LIF modelinde dopaminerjik kaybın okunabilir izi 3
alt tiple sınırlı.** Daha fazla alt tipi görünür kılmak için ya uyaran
bataryası o alt tiplerin devrelerini sürmeli ya da (faz 3) dopaminin
modülatör etkisi modele girmeli.

## 14. Faz 1 ve 2 kapanış özeti

Yapılanlar (hepsi `claude/lesion-inverse-model` dalında, testler geçiyor):
1. Doğrulanmış simülatör (Shiu referansıyla r = 0.963), 2.2× hızlı,
   bellek paylaşımlı paralel koşu, kontrol noktalı deneyler.
2. 6 uyaranlık kararlı batarya; kaçak rejim haritası.
3. Tekrarlı ilerleyici lezyonlar + büyüklük eşleştirmeli kontroller (şekil 1).
4. Etiketli-hat mekanizması: dopamin kaybı modelde ya hep ya hiç, kademeli
   rezerv yok.
5. Alt tip taraması; vekil duyarlılık haritası (şekil 2); NPE geri bulma
   (şekil 3), sınırlarıyla.
6. Gövdeli okuma: PPL1 tam kaybı yürüme/tırmanma hızını %13, KC %32
   düşürüyor; kontroller ±5 %.

Ana bilimsel mesaj: konnektom + LIF, dopaminerjik kaybın *nereye*
yansıyacağını hücre tipi çözünürlüğünde söylüyor (3 etiketli hat, belirli
MBON'lar, lokomotor DN'ler) ama *kademeli* davranışsal bozulmayı
üretemiyor. Bu, modelin eksik bıraktığı nöromodülasyonun ölçülebilir bir
sonucu ve faz 3'ün doğrudan gerekçesi.

Faz 3 için sıradaki iş: (a) KC→MBON sinapslarında dopamin kapılı kazanç
parametresi, bilinen öğrenme fenotiplerinden öğrenme; (b) DN→yürüme hızı
eşlemesini gerçek yürüme kayıtlarıyla kısıtlama; (c) MaleCNS yükleyici
(neuPrint token, yerelde) ve cinsiyet karşılaştırması; (d) GPU'da 1000+
örnekli tarama.

## 15. Faz 3 sonuçları: dopamin modülatör olarak (2026-10-29)

Kod: `sinek/neuromod/` (kompartmanlar konnektomdan türetilir: DAN→MBON
doğrudan sinapsı ≥ 2 mV; akut kazanç g = exp(−κ(r̄ − b)), b sağlam beyindeki
tonik DAN düzeyi; faz artışına bağlı dopamin kapılı plastisite),
`sinek/sim/lif.py` pencereli/durum taşıyan simülasyon,
`scripts/modulation_experiments.py`. Ayrıca: `sinek/data/malecns.py`
(neuPrint yükleyici, çevrimdışı sahte tablo testi; token yerelde) ve
`sinek/sim/lif_torch.py` (GPU'ya hazır torch arka ucu, CPU'da NumPy ile
eşdeğerlik testi).

**Koşullanma uydurması** (`artifacts/conditioning_grid_v1.csv`). Koku
(ORN_DM1) ile kompartman DAN'larının 1 s eşleştirilmesi, sonra koku tek
başına; hedef: hedef MBON'da ~%50 bastırma, hedef dışı < %15.

| κ, η | PPL101→MBON11 (γ1pedc, aversif) bastırma | PAM11→MBON07 (α1, apetitif) bastırma | hedef dışı |
|---|---|---|---|
| 0.003, 1e-4 (seçilen) | **0.59** | 0.19 | 0.16 / 0.03 |
| 0.003, 3e-4 | 0.96 | 0.90 | 0.28 / 0.12 |
| 0.03, 1e-4 | 0.33 | 0.00 | 0.39 / 0.56 |

Akut kazanç κ'nın küçük olması gerekiyor: 0.03'te hedef dışı MBON'lar
çöküyor çünkü modelde DAN'lar koku altında 100-300 Hz ateşliyor (doyum).
MBON07 341 Hz'de refrakter tavanına yakın olduğu için ağırlık bastırması
hıza az yansıyor; apetitif hat için hedefe ulaşılamadı.

**İlerleyici lezyonlar, modülasyonlu** (`artifacts/progressive_v2_modulated.csv`,
`fig4_modulation_curves.png`; 3 lezyon sırası, tek tohum):

| Grup | Model | %20 | %40 | %60 | %80 | %100 | %60'ta sıralar arası aralık |
|---|---|---|---|---|---|---|---|
| PPL1 | referans | 1.49 | 2.37 | 3.52 | 4.09 | 6.19 | 1.96-6.28 |
| PPL1 | modülatör | 1.48 | 1.79 | 1.91 | 2.21 | 2.65 | **1.46-2.23** |
| PAM | referans | 1.58 | 2.53 | 2.62 | 2.94 | 3.00 | 2.13-2.98 |
| PAM | modülatör | 1.78 | 2.15 | 2.88 | 3.46 | 4.26 | 2.30-3.59 |

Faz 1a'nın ya-hep-ya-hiç davranışı gitti: eğriler kademeli, PAM plato
yapmıyor, lezyon sırasına duyarlılık 4 kat azaldı. Etkinin yönü değişti:
MBON'lar susmak yerine disinhibisyonla artıyor (MBON31 0→1.25, MBON29
0→2.77 log-hız).

**Gövdeli okuma, modülasyonlu** (`artifacts/embodied_v3_combo_modulated.csv`):

| Koşul | Referans, yürüme değişimi | Modülatör, yürüme değişimi |
|---|---|---|
| PPL1 %100 | −13 % | **+6 %** |
| PPL1 %60 | −1 % | +3 % |
| PAM %100 | −4 % | +2 % |
| KC %100 | −32 % | −20 % |
| RND16 / RND307 | −1 % / +5 % | 0 % / +5 % |
| CX dopaminerjik (61 nöron) %100, referans | −1 % | — |

**Ana sonuç ve açık problem.** Modülasyon katmanı faz 1'in eksik bıraktığı
kademeliliği sağlıyor ama davranış işaretini tersine çeviriyor: PPL1 kaybı
referans modelde yürüyüşü düşürür (doğru yön, yanlış biçim), modülatör
modelde artırır (doğru biçim, yanlış yön; gerçek sinek Parkinson
modellerinde azalma). Merkezi kompleksin dopaminerjik hücreleri (sinek
lokomotor bozukluğunda sorumlu tutulan PPM3 hedefleri) referans modelde bu
batarya altında hiç etki yapmıyor. Yani lokomotor bozukluğun modeldeki
yolu henüz bulunmadı; üç aday: (1) dopaminin MB dışında da modülatör
olması (merkezi kompleks, LAL), (2) tonik dopaminin DN uyarılabilirliğini
doğrudan ayarlaması, (3) lezyonun kronik etkilerinin (kompanzasyon,
sinaptik yeniden ölçekleme) eksikliği. Üçü de aynı katmanla test edilebilir;
sıradaki deneyler bunlar.

**Durum:** faz 3a, 3b, 3c, 3d bu ortamda yapılabilen kısımlarıyla tamam.
Yapılamayanlar: MaleCNS verisi (ağ ve token), GPU taraması (donanım),
literatür tırmanma değerleriyle nicel karşılaştırma (birincil makaleler
ağ dışı).
