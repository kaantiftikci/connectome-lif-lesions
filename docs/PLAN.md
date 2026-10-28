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
