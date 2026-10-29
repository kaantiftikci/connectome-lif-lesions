# sinek — Araştırma Planı

## 0. Durum özeti: ne iddia edildi, ne çürüdü, ne kaldı (2026-10-29)

Bu belge iki günlük bir çalışmanın günlüğüdür; bölümler yazıldıkları
sırayla durur ve 8-15 arası bölümler sonradan çürüyen bir çerçeve içinde
yazılmıştır. Yayına esas okuma bu özet ve bölüm 18-21'dir; önbaskı taslağı
ayrıca `docs/preprint/` altındaki PDF'lerde.

**İddia edilen (faz 1-2, bölüm 8-14).** Konnektom + LIF modelinde dopamin
kümelerinin kaybı hücre tipi çözünürlüğünde okunur: PPL1 kaybı aynı
büyüklükteki rastgele kayıptan 6 kat büyük iz bırakır, etki üç etiketli
hattan geçer, ters model bu hatları fenotipten geri bulur, gövdeli okuma
yürüme hızında %13 düşüş verir.

**Çürüyen (bölüm 18-20).** Bu özgüllüğün tamamı koku uyaranının tetiklediği
beyin geneli bir çekici durumun ürünüdür: KC'lerin %75'i ateşler, MBON'lar
doyar, dopamin nöronu doymuş MBON'u açıp kapatan anahtara dönüşür. KC
seyrekliği gerçekçi düzeye (%3.8) çekilince dopamin etkileri gürültü
tabanının altına iner (PPL1 1.74, PAM 1.12, taban 1.91; rastgele 307 nöron
1.84). Dopamin modülatör olarak ele alınsa da değişmez. Nedeni: pekiştireçler
(şeker, acı, su) ve mekanosensör girdiler dopamin nöronlarını hiç sürmez
(0 Hz); modeldeki tek dopamin sürücüsü koku çekicisidir. Şeker→PAM yolu
grafta 2 sinapta vardır ama dinamikte iletmez.

**Kalan (geçerli katkılar).** Doğrulanmış ve 2.2× hızlı simülatör (r = 0.963,
APL ölçeklemesiyle de aynı); hücre tipi çözünürlüklü, iç içe, kontrol noktalı
lezyon çerçevesi; konnektomdan türetilen kompartmanlı dopamin modülasyon
katmanı ve koşullanma uydurması (DAN doğrudan sürüldüğünde mekanizma
çalışır: PPL101→MBON11 %59 bastırma); vekil + NPE ters çıkarım hattı;
NeuroMechFly gövdeli okuma; MaleCNS yükleyici ve cinsiyetler arası uyaran
eşlemesi; çekici rejiminin haritası ve seyrek rejim reçetesi (APL×5).
Bilimsel ana sonuç: mevcut parametrelerle konnektom kısıtlı LIF modelleri
pekiştirmeyi dopamin nöronlarına iletmez; dopamine bağlı öğrenme ve
nörodejenerasyon bu modelle simüle edilemez.

**Sonradan eklenen (bölüm 17, 22, 23).** Erkek beyin seyrek rejimde de aynı
tabloyu veriyor (PPL1 9.0, RND307 9.9, taban 10.4). Pekiştireç yolu izlendi:
acı→PPL1 yolu 20 röle nöronuyla var ve bu rölelerin giriş-çıkış sinapsları
4 kat güçlendirilince 150 Hz acı PPL1'i 34 Hz'e çıkarıyor (darboğazı
adlandıran, test edilebilir bir öngörü); şeker→PAM iki-sinaps yolu 16 kat
güçlendirmeyle bile iletmiyor. Jo (2026) nöron-kaybı protokolü her iki
rejimde de sıralamasını koruyor (hub > shuffled > antihub), ama tüm-beyin
aktivite okuması APL kaybında işaret değiştiriyor. Önbaskı buna göre
"model ne söyleyebilir, ne söyleyemez" çerçevesine alındı.

**Açık.** Acı→PPL1 düzeltmesiyle öğrenme indeksi (koşuluyor); w_syn
duyarlılığı (sırada); erkek için düşük tabanlı çalışma noktası (0.35/0.45
ölçekleri sırada); GPU ile büyük tarama (M4'te CPU ile koşuluyor;
`docs/gpu_runbook.md`); 3B görselleştirme (`viewer/`, yayınlandı).

---

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

arXiv 2610.19153 (Taeho Jo, "Simulating Alzheimer's amyloid-like pathology
on a fly central nervous system connectome", 13 Ekim 2026; özet birincil
kaynaktan doğrulandı 2026-10-29) MaleCNS üzerinde 166.700 nöronlu LIF
(referans modelle hız korelasyonu 0.9997) ile amiloid benzeri üç hasar
(eşik düşürme, sinaps kaybı, nöron kaybı) uygular; büyüklükler varsayılır;
nöronlar bağlantı derecesine göre (az bağlantılı / rastgele / çok bağlantılı)
seçilir; 1.424 simüle sinek; okuma koku ile uyarılan tüm-beyin aktivitesi,
dev lif hızı ve bir öğrenme indeksi. Bulgular: kaybolan nöron sayısı
bozukluğu kötü öngörüyor, kaybolan temas sayısı ve komuta nöronları
belirleyici (%12 nöron kaybında aktivite %93 / %47 / %31). Hücre tipine
göre hedefleme, ilerleyici seyir, gövdeli davranış, gerçek fenotiplerle
karşılaştırma, makine öğrenmesi ve ters çıkarım yok.

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

### 5b. Koku uyaranı bir çekici durumdur (2026-10-29 düzeltmesi)

Bölüm 5'teki "ORN_DM1 kararlı" ifadesi eksikti. ORN_DM1 sürüşü, hızdan
bağımsız olarak (40, 75, 150 Hz'de aynı), dişide ~9.950, erkekte ~11.600
nöronluk kalıcı bir yüksek aktivite durumunu tetikliyor; MBON ortalaması
dişide 161 Hz, erkekte 272 Hz. Bu, modelin bistabil doğasının (bölüm 5)
koku girişiyle tetiklenen hali: ORN_DA1 ve ORN_VM4'teki "kaçak" ile aynı
olgu, yalnızca daha küçük bir çekici. Sonuçları: (a) koku altındaki tüm
MBON ve dopamin ölçümleri (bölüm 8-15) bu rejimde alınmıştır, MBON
doyumunun nedeni budur; (b) rejim her iki cinste de aynı olduğu için
cinsiyet karşılaştırması simetriktir; (c) tat ve mekanosensör uyaranlar
bu çekiciye girmez (dişi 400-1.000 aktif nöron). Koku altı sonuçlar
"çekici durumda dopamin etkisi" olarak okunmalı. Gerçek koku cevabının
seyrek olduğu biliniyor (KC'lerin ~%5'i); bu rejim modelin eksik inhibisyon
veya adaptasyonunun işareti ve referans LIF'in bilinen sınırı.

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
  prior'un 2-3 katı daha iyi. Yalnızca lezyonlu girişler üzerinden (adil
  metrik, `train_surrogate.py` artık bunu basıyor): PAM korelasyon 0.97,
  PPL1 0.95, PPL2 −0.22, PPM1 −0.11; tespit oranı 0.72, yanlış alarm 0.32. Bu, "gözlenen fenotipten hasar örüntüsünü
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

Yapılanlar (hepsi `main` dalında, testler geçiyor):
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
başına; hedef: hedef MBON'da ~%50 bastırma, hedef dışı < %15. Kompartman
çiftleri bağlantıdan seçildi: PPL101, MBON11'in en güçlü dopaminerjik girdisi
(124 mV; MBON11 glutamaterjik, aversif çıkış); PAM11, MBON07'nin (98-113 mV;
kolinerjik, apetitif çıkış). Hemibrain kodlarının Yunanca kompartman adlarıyla
(γ1pedc, α1 vb.) eşleşmesi annotasyon dosyasında yok ve bu çalışmada
doğrulanmadı; metin boyunca adlar bağlantı tabanlıdır.

| κ, η | PPL101→MBON11 (aversif kompartman) bastırma | PAM11→MBON07 (apetitif kompartman) bastırma | hedef dışı |
|---|---|---|---|
| 0.003, 1e-4 (seçilen) | **0.59** | 0.19 | 0.16 / 0.03 |
| 0.003, 3e-4 | 0.96 | 0.90 | 0.28 / 0.12 |
| 0.03, 1e-4 | 0.33 | 0.00 | 0.39 / 0.56 |

Akut kazanç κ'nın küçük olması gerekiyor: 0.03'te hedef dışı MBON'lar
çöküyor çünkü modelde DAN'lar koku altında 100-300 Hz ateşliyor (doyum).
MBON07 341 Hz'de refrakter tavanına yakın olduğu için ağırlık bastırması
hıza az yansıyor; apetitif hat için hedefe ulaşılamadı.

**İlerleyici lezyonlar, modülasyonlu** (`artifacts/progressive_v2_modulated.csv`,
`fig4_modulation_curves.png`; 3 lezyon sırası × 2 simülasyon tohumu; tonik
taban çizgisi kazanç kapalıyken ölçüldü, 2026-10-29 düzeltmesi):

| Grup | Model | %0 | %20 | %40 | %60 | %80 | %100 | %60'ta sıralar arası aralık |
|---|---|---|---|---|---|---|---|---|
| PPL1 | referans | 0.84 | 1.49 | 2.37 | 3.52 | 4.09 | 6.19 | 1.96-6.28 |
| PPL1 | modülatör | 0.85 | 1.21 | 1.56 | 1.62 | 2.03 | 2.23 | **1.46-1.81** |
| PAM | referans | 0.84 | 1.58 | 2.53 | 2.62 | 2.94 | 3.00 | 2.13-2.98 |
| PAM | modülatör | 0.85 | 1.21 | 1.63 | 2.80 | 3.10 | 4.00 | 2.11-3.52 |

(Düzeltme öncesi koşu `results/progressive_modulated_oldbaseline.csv`; aynı
biçim, PPL1 tam kayıpta 2.63, PAM 4.17.) Faz 1a'nın ya-hep-ya-hiç davranışı
gitti: eğriler kademeli, PAM plato yapmıyor, PPL1'de lezyon sırasına
duyarlılık 12 kat azaldı (aralık genişliği 4.3 → 0.35). Etkinin yönü değişti:
MBON'lar susmak yerine disinhibisyonla artıyor (MBON31 0→1.25, MBON29
0→2.77 log-hız).

**Gövdeli okuma, modülasyonlu** (`artifacts/embodied_v3_combo_modulated.csv`):

| Koşul | Referans, yürüme değişimi | Modülatör (taban çizgisi düzeltilmiş) | Modülatör, ilk koşu |
|---|---|---|---|
| PPL1 %100 | −13 % | **+4 %** | +6 % |
| PPL1 %60 | −1 % | +3 % | +3 % |
| PAM %100 | −4 % | −1 % | +2 % |
| KC %100 | −32 % | −25 % | −20 % |
| RND16 / RND307 | −1 % / +5 % | 0 % / −1 % | 0 % / +5 % |
| CX dopaminerjik (61 nöron) %100, referans | −1 % | — | — |

**Ana sonuç ve açık problem.** Modülasyon katmanı faz 1'in eksik bıraktığı
kademeliliği sağlıyor ama davranış işaretini tersine çeviriyor: PPL1 kaybı
referans modelde yürüyüşü düşürür (doğru yön, yanlış biçim), modülatör
modelde kontrol gürültüsü içinde kalır ya da hafifçe artırır (doğru biçim,
yanlış ya da sıfır yön; gerçek sinek Parkinson modellerinde azalma). Merkezi kompleksin dopaminerjik hücreleri (sinek
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

## 16. Literatürdeki tırmanma ve dopamin kaybı değerleri (2026-10-29)

Birincil makalelerden (PMC tam metinleri, bu oturumda doğrudan okundu)
derlenen nicel karşılaştırma. Hiçbiri tek bir "yüzde kaç nöron kaybında
yüzde kaç tırmanma" sayısı vermiyor; fenotipler ayrı ölçülüp kümeye
atfediliyor.

| Çalışma | Model | Etkilenen DA kümesi | Tırmanma |
|---|---|---|---|
| Whitworth 2005 (PNAS, PMC1142368) | parkin null | PPL1 (1 günde anlamlı, 20 günde daha yaygın); diğer kümeler etkilenmez | hipomorf mutantlarda kısmi tırmanma defekti; kas kaynaklı |
| Yang 2006 (PNAS, PMC1502310) | PINK1 RNAi | PPL1 belirgin, PPM orta (25 gün) | 10 güne dek tırmanma ciddi azalır, uçma tamamen gider |
| Wang 2006 (PNAS, PMC1569195) | PINK1 RNAi | PAL, PPM1/2, PPM3, PPL2 belirgin; PPL1 daha az (10 gün) | yaşa bağlı ilerleyici |
| Riemensperger 2013 (Cell Reports, 24239353) | pan-nöronal α-synuclein | yarım beyin başına 15 PAM nöronu, mantar gövdesi β′ lobu | β′ bloğu negatif geotaksiyi bozar; ilerleyici |

Modelle karşılaştırma ve açık uyumsuzluk:
* **Küme uyumu kısmen doğru.** parkin ve erken PINK1 modelleri PPL1'i
  vurguluyor; modelde de PPL1 kaybı en duyarlı grup (bölüm 11, 13). Ama
  Wang 2006 ve Riemensperger PAM/PPM3'ü öne çıkarıyor; modelde PAM etkisi
  tek kompartmana (PAM08→MBON29) sıkışıyor, PPM3 (merkezi kompleks) hiç
  etki vermiyor (bölüm 15). Yani model, parkin-benzeri PPL1 tablosuyla
  uyumlu, α-synuclein-benzeri PAM/β′ tablosuyla değil.
* **Devre uyumu dikkat çekici.** Riemensperger'in bulduğu "kritik PAM
  nöronları mantar gövdesine projekte eder ve tırmanmayı sürer" ifadesi,
  modelin tüm dopamin etkisini KC→MBON kompartmanlarında bulmasıyla aynı
  anatomiyi işaret ediyor. Modelin eksiği bu projeksiyonun yürümeye nasıl
  çevrildiği (inen nöron eşlemesi), mekanizmanın yeri değil.
* **Yön hâlâ uyumsuz.** Literatürde tırmanma azalıyor; modelde referansta
  azalıyor ama ya-hep-ya-hiç, modülatörde kademeli ama sıfır/pozitif
  (bölüm 15). Literatür yön sorununu çözmüyor, sadece onaylıyor: modelin
  üretmesi gereken işaret negatif ve kademeli.
* **Zaman ekseni modelde yok.** Tüm deneysel defektler yaşa bağlı
  (10-25 gün); model anlık. Kronik kompanzasyonun eksikliği (bölüm 15,
  3. aday) bu yüzden ciddi; gerçek fenotip günler süren bir süreç.

Not: Greene 2003 (PMC153051) tam metni PMC bot korumasına takıldığı için
okunamadı; özeti parkin'de lokomotor defekt ve dorsomedial DA nöron
değişikliği bildiriyor, yukarıdakilerle tutarlı.

## 17. Cinsiyet karşılaştırması: erkek konnektomda ilerleyici lezyonlar (2026-10-29, ön sonuç)

Erkek MaleCNS v1.0, hazır feather dosyalarından (bölüm 15 yükleyici);
164.606 nöron, 25.6 M kenar. Batarya, dişi hücre tiplerinin erkek
`flywireType` eşleşmesiyle taşındı (şeker 23, su 17, acı 38, koku 74,
rüzgar 559, kıl 863 nöron). `artifacts/progressive_v3_male_scale030.csv`,
`fig5_sex_comparison.png`.

**Çalışma noktası sorunu.** Yayınlanan hizalama ölçeğinde (0.581) erkek model
her uyaranda çekici duruma giriyor; sağlam tekrarlar arası gürültü tabanı
L2 20.4 (dişide 1.68), özellikle rüzgar/yerçekimi altında MBON okumalarında.
Ölçek 0.3'te taban 3.25'e iniyor, ama o zaman PAM nöronları hiç ateşlemiyor.
Dişiyle aynı mutlak ölçekte karşılaştırma mümkün olmadı; aşağıdaki sayılar
0.3 ölçeğinde, 3 lezyon sırası × 1 tohum.

| Grup | Dişi (taban 1.68) %100 kayıp | Erkek @0.3 (taban 3.25) %100 kayıp |
|---|---|---|
| PPL1 | 6.19 | 2.38 (taban altı) |
| PAM | 3.00 | 0.00 (PAM sessiz) |
| RND16 | 0.97 | 0.42 |
| RND307 | 1.77 | 1.31 |

Dürüst yorum: bu rejimde erkek lezyon etkileri gürültü tabanının altında,
dolayısıyla "erkekte PPL1 etkisi daha küçük" denemez; "bu çalışma noktasında
okunamıyor" denir. Erkek modelin asıl bulgusu, aynı per-sinaps ağırlıkta
dişiden belirgin daha uyarılabilir olması ve kararlı bir çalışma noktasının
dopamin devrelerini sessizleştirmesi. Temiz karşılaştırma için her iki
cinsin de seyrek MB rejiminde (bölüm 18, APL kazancı) koşulması gerekiyor.

**Erkek, seyrek rejimde (APL×5, ölçek 0.581; 2026-10-29).** Gürültü tabanı
20.4'ten 10.4'e iniyor (`results/noise_floor_male_apl5.npz`), yine de dişinin
5 katı. 3 lezyon sırası × 1 tohum, %100 kayıpta uzaklıklar
(`artifacts/progressive_v6_male_apl5.csv`):

| Grup | Erkek APL×5 (taban 10.4) | Dişi APL×5 (taban 1.91) |
|---|---|---|
| PPL1 | 8.97 | 1.74 |
| PAM | 1.21 | 1.12 |
| RND16 | 4.35 | 1.16 |
| RND307 | 9.86 | 1.84 |

Her iki cinste de aynı tablo: seyrek rejimde dopamin lezyonları gürültü
tabanının altında ve boyut-eşli rastgele kontrolden ayırt edilemiyor. Erkek
modelde tabanın hâlâ yüksek olması, çalışma noktasının (sinaps ölçeği) ayrı
bir tarama gerektirdiğini gösteriyor (0.35 ve 0.45 ölçeklerinde APL×5 taban
ölçümü sırada).

## 18. Seyrek mantar gövdesi rejimi: dopamin etkileri kayboluyor (2026-10-29)

Rejim araması (`artifacts/odor_regime_search_v1.csv`): koku çekicisi uyaran
tasarımıyla kırılamadı (8 ORN, 50 ms darbe, 6 glomerül, genel ölçek 0.6:
hepsinde KC'lerin yüzde 51-75'i aktif). KC→KC yinelemesini sıfırlamak da
yetmedi (yüzde 67). Yalnızca APL→KC inhibisyonunu 5 kat artırmak KC
aktivasyonunu yüzde 3.8'e, MBON ortalamasını 10 Hz'e indirdi (biyolojik
seyreklik ~yüzde 5); beyin geneli çekici (5.9 bin aktif nöron) sürüyor.

Bu rejimde ilerleyici lezyonlar (5 sıra × 2 tohum, güncellendi 2026-10-29;
`artifacts/progressive_v4_sparse_apl5.csv`, gürültü tabanı 1.91):

| Grup | Çekici rejimi, %100 kayıp | Seyrek rejim, %100 kayıp (ort ± sd) |
|---|---|---|
| PPL1 | 6.19 | 1.74 ± 0.20 (taban altı) |
| PAM | 3.00 | 1.12 ± 0.22 (taban altı) |
| RND16 | 0.97 | 1.16 ± 0.08 |
| RND307 | 1.77 | 1.84 ± 0.15 |

(İlk 3×1 koşuda PPL1 1.62, PAM 1.24, RND307 2.19 idi; sonuç değişmedi.)

Sonuç: bölüm 11 ve 13'teki dopamin özgüllüğü (PPL1 ≫ rastgele, etiketli
hatlar) MBON doyumunun ürünü. MBON'lar doyumdan çıkınca dopaminerjik kayıp
bu batarya altında okunamıyor; rastgele 307 nöron daha büyük iz bırakıyor.
Referans LIF'te dopamin etkisi, DAN→MBON hızlı sinapslarının doymuş MBON'u
kapatmasından ibaretti. Modülatör katman (bölüm 15) ve seyrek rejim birlikte
test edilmeli; bu, projenin sıradaki deneyi. Bölüm 11, 13 ve 14'ün
sonuçları "çekici rejiminde" ibaresiyle okunmalı.

## 19. Modülatör katman seyrek rejimde: pasif batarya yetmiyor (2026-10-29)

Seyrek MB rejiminde (APL×5) hem referans hem modülatör modelde ilerleyici
lezyonlar (`artifacts/progressive_v5_modulated_sparse.csv`, gürültü tabanı 1.91):

| Grup, %100 kayıp | Çekici referans | Seyrek referans | Seyrek modülatör |
|---|---|---|---|
| PPL1 | 6.19 | 1.62 | 0.89 |
| PAM | 3.00 | 1.24 | 1.12 |
| RND307 | 1.77 | 2.19 | — |

Üç koşul birlikte tek sonucu veriyor: **pasif duyusal batarya altında
dopaminerjik kayıp, MBON'lar doymadıkça bu modelde okunamıyor; modülasyon
bunu değiştirmiyor.** Faz 1'in dopamin özgüllüğü yalnızca çekici rejimin
MBON doyumunun ürünüydü. Modülatör katman kademeliliği sağlıyor ama pasif
uyaran dopamin devresini zaten zayıf sürdüğü için görünür bir iz bırakmıyor.

Bu, dopaminin modeldeki asıl rolüne işaret ediyor: dopamin öğrenme
sinyalidir, pasif duyusal cevabın sürücüsü değil. Dolayısıyla dopamin
kaybını okumak için fenotip davranış değil **öğrenme** olmalı. Sıradaki
deney (bölüm 20) tam bunu test ediyor: doğal pekiştireçle (şeker=ödül,
acı=ceza) koşullanma ve lezyonun öğrenme indeksini ne kadar düşürdüğü.

## 20. Kritik bulgu: pekiştireçler dopamin nöronlarına ulaşmıyor (2026-10-29)

Öğrenme deneyinin ön tanısı beklenmedik ama kesin bir sonuç verdi.
Dopaminerjik kümelerin (PAM, PPL1) her uyaran altındaki ateşleme hızı:

| Uyaran | PAM (çekici) | PPL1 (çekici) | PAM (seyrek) | PPL1 (seyrek) |
|---|---|---|---|---|
| şeker (ödül) | 0.0 | 0.0 | 0.0 | 0.0 |
| acı (ceza) | 0.0 | 0.0 | 0.0 | 0.0 |
| su | 0.0 | 0.0 | 0.0 | 0.0 |
| koku DM1 | 53.0 | 206.4 | 0.6 | 16.3 |
| rüzgar/yerçekimi | 0.0 | 0.0 | 0.0 | 0.0 |
| baş kılı | 0.0 | 0.0 | 0.0 | 0.0 |

Graf yapısında şeker→PAM yolu var (2 sinapta 69, 3 sinapta 225 PAM
erişilebilir), ama LIF'te sinyal yayılmıyor: PAM, ölçeklemesiz bile
şeker altında 0 Hz. Şeker yalnızca ~418 nöronluk yerel SEZ kümesini
sürüyor, röle nöronları eşiği aşmıyor.

**Sonuç.** Bu modelde dopamin nöronlarını süren tek şey koku çekicisi.
Pekiştireçler (şeker ödülü, acı cezası) dopamin nöronlarına hiç ulaşmıyor.
Biyolojide şeker→PAM ödül yolu iyi kurulmuştur (Liu 2012, Burke 2012); model
bunu üretmiyor. Dolayısıyla:

1. Faz 1'in dopamin "özgüllüğü" tamamen koku çekicisinin ürünü (bölüm 18-19
   bunu zaten göstermişti; bu bölüm nedenini veriyor: çekici dışında DAN'lar
   sessiz).
2. Doğal pekiştireçle öğrenme deneyi (görev 18) bu modelde yapılamaz: US,
   DAN'lara ulaşmıyor. Yapay öğretme sinyali (DAN'ları doğrudan sürmek)
   enjekte edilen etkiyi geri ölçmek olur, döngüsel; biyoloji testi değil.

**Projenin asıl sonucu.** Konnektom + basitleştirilmiş LIF, dopamine bağlı
davranışı (ödül öğrenmesi, Parkinson defekti) modellemek için yetersiz,
çünkü pekiştirmeyi dopamin nöronlarına yönlendiremiyor. Bunu düzeltmek için
ya daha zengin dinamik (nöromodülasyon, uyarlanma, gerçekçi sinaptik
kazanç) ya da öğretme sinyalinin doğrudan enjekte edilmesi gerekir. Bu,
negatif ama sağlam bir sonuç: alandaki 80+ hobi projesinin hiçbiri bu
sınırı ölçmedi.

### Yöntemsel katkı olarak kalan

Dopamin modülasyon katmanı (bölüm 15) ve koşullanma uydurması (bölüm 15)
hâlâ geçerli araçlar: DAN'lar doğrudan sürüldüğünde (yapay öğretme sinyali)
kompartman MBON'u beklendiği gibi bastırılıyor (PPL101→MBON11 %59). Bu, yol
işlediğinde mekanizmanın doğru olduğunu gösterir; eksik olan, duyusal
girdinin bu yolu sürmesi.

## 21. APL ölçeklemesi referans doğrulamayı değiştirmiyor (2026-10-29)

`validate_vs_shiu.py --apl-scale 5`: 630 tablolarında APL, KC'lere en çok
inhibitör sinaps yapan iki nöron olarak tanımlandı (2.565 ve 2.547 KC hedefi;
5.112 sinaps 5 kat ölçeklendi). Sonuç referansla birebir: r = 0.963, 5 Hz üstü
333 nörondan 320'si, 7 yanlış pozitif. Seyrek rejim müdahalesi tat devresine
dokunmuyor; önbaskıda duyarlılık analizi olarak raporlanabilir.

## 22. Pekiştireç → dopamin yolunu ileten en küçük değişiklik (2026-10-29)

`scripts/reinforcer_path.py` (rates / paths / boost), seyrek rejim (APL×5).
Sonuç dosyaları: `results/reinforcer_rates.csv`, `results/boost_bitter_PPL1.csv`,
`results/boost_sugar_PAM.csv`; günlükler `results/reinforcer_paths_{sugar,bitter}.log`.

**Hız / küme taraması.** Şeker (32 GRN) 150–600 Hz'de 366–491 nöron
etkinleşiyor, PAM/PPL1 0 Hz; 1000 Hz'de ağ çekiciye düşüyor (5.897 etkin)
ve PPL1 ancak o zaman 13 Hz'e çıkıyor. Şeker+düşük-tuz (57 GRN) her hızda
çekici (5.7 k etkin). Su hiçbir hızda DAN'a ulaşmıyor. Acı (42 GRN) 600 Hz'de
PPL1'in %12'sini 5 Hz üstüne çıkarıyor (ortalama 1.4 Hz); 150 Hz'de 0.

**Nerede kopuyor.** Şeker GRN'leri 414 nörona doğrudan sinaps yapıyor, 121'i
ateşliyor (SEZ ara nöronları CB0192, CB0248, CB0616… 85–200 Hz). Bu etkin
küme PAM'a projeksiyon yapan hiçbir nöronu anlamlı sürmüyor: GRN'den 2
sıçramada PAM'a giden en iyi röle 0.3–1.9 mV girdi alıyor (1–7 sinaps).
Acıda ise etkin küme (113 nöron) PPL1'e projeksiyon yapan röleleri (CB0135,
SMP026, DNpe053, LAL154, SMP154) 2–4 mV/10 ms sürüyor, eşiğin altında.

**En küçük düzeltme (boost).** Etkin küme → röle (20 nöron) → hedef DAN
kenarları k kat ölçeklendi:

| US → hedef | sıçrama | k | hedef Hz (150 Hz US) | etkin nöron | yan etki |
|---|---|---|---|---|---|
| acı → PPL1 | giriş | 4 | 17.3 | 5.272 (çekici) | PPL2 42 Hz |
| acı → PPL1 | giriş | 8 | 26.3 | 760 | PPL2 11 Hz |
| acı → PPL1 | her iki | 4 | 33.6 (%50'si >5 Hz) | 822 | PPL2 12 Hz, koku KC oranı değişmedi |
| acı → PPL1 | çıkış | 16 | 0 | 113 | — |
| şeker → PAM | her iki | 16 | 5.4 (%18'i >5 Hz) | 469 | — |

Yorum: acı→PPL1 yolu **vardır ve dört kat güçlendirilmiş 20 röleyle iletir**
(deneysel olarak test edilebilir bir öngörü: bu röleler darboğaz). Şeker→PAM
yolu iki sıçramada 16 kata kadar ölçeklemeyle bile iletmiyor; ödül sinyali
konnektomun bu modeldeki iki-sinapslı yollarında yok, muhtemelen oktopamin/
çok-sinapslı veya modülatör yollardan geliyor (OA-VUMa2, OA-VPM3/4 röle
listelerinde görünüyor). Öğrenme indeksi deneyi bu nedenle yalnızca acı
(ceza) kolunda, k=4 düzeltmesiyle koşuluyor (`learning_index.py --boost 4`).

## 23. Jo (2026) nöron-kaybı protokolünün iki rejimde yeniden testi (2026-10-29)

`scripts/jo_retest.py`; sonuçlar `results/jo_retest.csv`, özet
`results/jo_retest_summary.csv`. Jo'nun kuralı: duyusal olmayan her nöron
0.5·s·v olasılıkla kaldırılır; v = sinaptik temas sayısına göre yüzdelik
sıra (hub haritası), aynı değerlerin karıştırılmışı (shuffled) veya tersi
(antihub). s = 0.5, 8 tekrar × 3 harita × 2 rejim, koku = ORN_DM1 150 Hz,
500 ms. Jo (MaleCNS, PN doğrudan sürülmüş, sinaps kaybı + eşik kayması da
dahil): hub %31, shuffled %47, antihub %93; antihub/hub oranı 3.0.

| Rejim | Harita | nöron kaybı | temas kaybı | koku-tetikli spike (sağlam=%100) | KC etkin | fenotip uzaklığı (taban) |
|---|---|---|---|---|---|---|
| çekici (APL×1) | hub | %12.2 | %33 | %52 (IQR 50–59) | 0.49 | 12.5 ± 1.3 (0.92) |
| çekici | shuffled | %11.0 | %23 | %72 | 0.57 | 7.7 ± 1.6 |
| çekici | antihub | %9.9 | %12 | %90 | 0.63 | 3.6 ± 0.2 |
| seyrek (APL×5) | hub | %12.2 | %33 | %65 (IQR 62–94) | 0.16 | 12.9 ± 7.8 (1.31) |
| seyrek | shuffled | %11.0 | %23 | %81 | 0.02 | 5.8 ± 0.8 |
| seyrek | antihub | %9.9 | %12 | %97 | 0.03 | 1.9 ± 0.9 |

antihub/hub oranı: çekici 1.7, seyrek 1.5 (Jo 3.0).

**Yorum.** Jo'nun niteliksel sonucu (hub > shuffled > antihub; hasar, kaybedilen
temas sayısını izler) her iki rejimde de yeniden üretiliyor; bu bulgu koku
çekicisinin artefaktı değil. İki önemli fark:

1. Oran bizde 1.5–1.7, Jo'da 3.0. Jo'nun protokolü sinaps kaybı ve eşik
   kaymasını da içeriyor, PN'leri doğrudan sürüyor ve erkek konnektomda;
   yalnızca nöron kaybı kısmının karşılığı bizim ölçümümüz.
2. Seyrek rejimde hub haritası iki-modlu: iki APL nöronu sinaptik temas
   sıralamasında en tepede (yüzdelik 1.0, kaldırılma olasılığı 0.25) ve 8
   tekrarın 3'ünde biri kaldırılınca beyin çekiciye düşüyor (KC etkin oranı
   0.01 → 0.41, MBON 3 → 90 Hz, "tüm-beyin aktivitesi" sağlamın %108'ine
   çıkıyor). Yani tüm-beyin spike sayısı bu modelde hasarla artabilir de; bir
   okuma olarak işaretini çalışma noktası belirliyor. Jo'nun modelinde
   koku sonrası süren aktiviteyi adaptasyonla bastırma ihtiyacı (makalesinde
   "üçüncü gereklilik karşılanamadı") aynı çekicinin oradaki izi.

Sonuç: Jo'nun ana iddiası sağlam; bizim katkımız, tüm-beyin aktivite
okumasının APL kaybında tersine döndüğünü ve rejimden bağımsız olmadığını
göstermek.
