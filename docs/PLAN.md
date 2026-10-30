# sinek — Araştırma Planı

## 0. Durum özeti: ne iddia edildi, ne çürüdü, ne kaldı (2026-10-29)

Bu belge iki günlük bir çalışmanın günlüğüdür; bölümler yazıldıkları
sırayla durur ve 8-15 arası bölümler sonradan çürüyen bir çerçeve içinde
yazılmıştır. Yayına esas okuma bu özet ve bölüm 18-21'dir; önbaskı taslağı
ayrıca Claude Docs'ta.

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

**Pozitif kol ve Parkinson kolu (bölüm 32–35, 2026-10-29/30).** Eksik ödül
yolu tek bir sinaps dışı terimle verilince konnektom, literatürün iştah
belleğine atadığı ve kokuya yanıt veren her MBON'un (07/α1, 02/β2β'2a,
09/γ3β'1) öğreneceğini kendiliğinden buluyor; rezerv kompartmana göre
%75–90. Acı kolu modelde koku ağının PPL1'i susturması yüzünden çalışmıyor
(MBON→DAN geri beslemesine dair test edilebilir iddia). Parkinson: konnektom
yükü PPL1'i PAM'ın 12 katı sıralıyor (parkin/PINK1 kaybıyla uyumlu); kayıp
sırası belirtinin zamanını belirliyor; pasif ve hareket okumaları %100
kayıpta bile kör, koşullanma %75–90'da duyarlı; eski bellek korunuyor, yeni
edinim kayboluyor; L-DOPA karşılığı öğrenmeyi kurtarmıyor, kapı adapte
değilse özgüllüğü bozuyor; kompanzasyon kompartmanda nöron kaldığı sürece
işe yarıyor. Şekil 8. Önbaskıya "Predictions for fly models of Parkinson's
disease" bölümü eklendi.

**Kapanış (bölüm 38–41).** Ceza kolunu çökerten bağlantı APL→PPL1 (MBON geri
beslemesi değil); kaldırılınca ara rejimde MBON12'de zayıf ama PPL1'e
bağımlı ceza öğrenmesi. İkinci koku aynı haritayı veriyor. Rezerv eşiği KC
girdisiyle küçülüyor. Jo'nun tam kuralı sıralamayı koruyor. Adaptasyonlu
nöron çekiciyi kaldırıyor ama kararlı seyrek kod vermiyor; negatif sonuç
aynen. Erkek pozitif kol bu çalışma noktasında ölçülemiyor.

**Açık.** Mac'te 5-tohumlu Parkinson koşuları (kullanıcı). Acı→PPL1 yolunun kokuyla sönmesinin mekanizması
(MBON→DAN geri besleme ağırlıkları) incelenmedi. w_syn
duyarlılığı (sırada); erkek için düşük tabanlı çalışma noktası (0.35/0.45
ölçekleri sırada); GPU ile büyük tarama (M4'te iki n=1000 tarama bitti, bölüm
26–27; `docs/gpu_runbook.md`); 3B görselleştirme (`viewer/`, çekici ve seyrek
rejim anahtarıyla yayınlandı); şekiller 1–7 önbaskı dokümanına gömüldü.
Son tur (bölüm 28–30): oktopamin yolu, KC eşiğiyle seyrekleştirme, Brian2
ile çekici doğrulaması, Jo eğitim protokolü.

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

## 24. Acı→PPL1 düzeltmesiyle öğrenme indeksi (2026-10-29)

`learning_index.py curves --us bitter --boost 4 --groups PPL1 --controls 16
--seeds 2` (seyrek rejim, κ=0.003, η=1e-4). Sonuç
`artifacts/learning_bitter_boost4.csv`. Koku (ORN_DM1 150 Hz) + acı (150 Hz)
eşleşmesi 1 s; indeks = (ön − son)/ön, MBON tipi başına.

| Grup | kayıp | tohum | MBON14 (PPL106 kompartmanı) | MBON20 | MBON33 |
|---|---|---|---|---|---|
| sağlam | 0 | — | 1.00 | 0.09 | 0.06 |
| PPL1 | %50 | 0 | 1.00 | −0.05 | 0.07 |
| PPL1 | %50 | 1 | 0.00 | 0.00 | −0.07 |
| PPL1 | %100 | 0, 1 | 0.00 | −0.02 | 0.18 |
| RND16 | %50, %100 | 0, 1 | 1.00 | 0.09 | 0.06 |

Tanı koşusu (ön/son hızlar): sağlam ağda eşleşme sırasında PPL106 13.9 Hz,
tüm PPL1 36 Hz; PPL1 kaldırılınca 0 Hz. MBON14 koku yanıtı sağlamda 0.83 Hz →
eşleşme sonrası 0 Hz; PPL1 kaldırılınca zaten 0 Hz. MBON33 28.3 → 26.7 Hz,
MBON20 78 → 72 Hz (küçük, tohumlar arası dalgalanma düzeyinde).

**Dürüst yorum.** Düzeltme yolu çalışıyor: acı artık PPL1'e, özellikle α3
kompartmanının DAN'ı PPL106'ya ulaşıyor ve bu kompartmanın MBON'unda
(MBON14 = MBON-α3, acı/ceza belleğinin bilinen kompartmanlarından biri)
dopamin kapılı bastırma PPL1 kaybıyla kayboluyor, rastgele 16 nöron kaybıyla
değişmiyor; %50 kayıpta sonuç PPL106'nın kaldırılan yarıda olup olmadığına
bağlı (tohum 0 korunuyor, tohum 1 kayboluyor). Ancak büyüklük anlamlı
değil: MBON14'ün koku yanıtı seyrek rejimde 1 Hz'in altında, "indeks 1.0"
0.8 Hz → 0 Hz demek. Öğrenme okuması niteliksel olarak doğru örüntüyü
veriyor ama nicel bir öğrenme eğrisi için MBON-α3'ün koku yanıtının
güçlendirilmesi (KC→MBON ağırlığı veya daha fazla KC girdisi) gerekir; bu
model-dışı bir ayar olduğu için burada yapılmadı.

## 25. Parametre sağlamlığı: w_syn 0.20 / 0.275 / 0.35 (2026-10-29)

`scripts/param_robustness.py`; sonuç `artifacts/param_robustness.csv`.
İki ana iddia, miras sinaptik ağırlık ±%27 değiştirilerek yeniden ölçüldü.

| w_syn (mV) | APL | koku: KC etkin | etkin nöron | MBON Hz | PPL1 Hz |
|---|---|---|---|---|---|
| 0.20 | ×1 | 0.64 | 7.784 | 104 | 146 |
| 0.20 | ×5 | 0.026 | 4.303 | 5.5 | 7.3 |
| 0.275 | ×1 | 0.75 | 9.945 | 161 | 206 |
| 0.275 | ×5 | 0.037 | 5.674 | 10.4 | 16.3 |
| 0.35 | ×1 | 0.79 | 11.486 | 200 | 240 |
| 0.35 | ×5 | 0.046 | 7.489 | 15.8 | 23.0 |

Seyrek rejimde (APL×5) lezyon iddiası (1 lezyon sırası, 2 sağlam tohum):

| w_syn | gürültü tabanı | PPL1 %100 | RND16 %100 |
|---|---|---|---|
| 0.20 | 1.24 | 0.56 | 0.63 |
| 0.275 | 1.55 | 0.96 | 0.83 |
| 0.35 | 6.66 | 9.61 | 3.94 |

**Yorum.** İddia A (koku çekicisi, APL×5 ile seyrekleşme) üç ağırlıkta da
geçerli. İddia B (PPL1 kaybı gürültü tabanının altında) referans ağırlıkta
ve altında geçerli; %27 daha güçlü sinapslarda ağ çekici sınırına yaklaşıyor
(etkin nöron 7.5 k, taban 6.66) ve PPL1 kaybı tabanı aşıyor (9.6, RND16 3.9).
Yani "dopamin etkisi yok" sonucu çalışma noktasına bağlı: çekiciye
yaklaştıkça dopamin lezyonu yine görünür oluyor, ama bu görünürlük çekici
mekanizmasının (doymuş MBON'ları açıp kapatan DAN) geri gelmesi demek.
Önbaskıda bu sınırlama açıkça belirtildi.

**Erkek çalışma noktası (bölüm 17 devamı).** APL×5 ile sinaps ölçeği
taraması: 0.581 → taban 10.4; 0.45 → 6.06; 0.35 → 1.81 (dişi 1.91 ile
aynı düzey). 0.35 ölçeğinde PPL1/PAM eğrileri (3 lezyon sırası × 1 tohum,
`artifacts/progressive_v7_male_s035_apl5.csv`, şekil 5 yenilendi):

| Grup | %20 | %60 | %80 | %100 | taban |
|---|---|---|---|---|---|
| PPL1 | 1.06 | 1.09 | 2.73 | 2.67 | 1.81 |
| PAM | 0.00 | 0.00 | 0.00 | 0.00 | |
| RND16 | 0.94 | 0.63 | 0.85 | 0.57 | |
| RND307 | 0.72 | 1.19 | 1.15 | 1.14 | |

Erkekte bu çalışma noktasında PPL1'in %80+ kaybı tabanın 1.5 katına çıkıyor
ve rastgele 307 nöron kaybının üstünde (dişide tabanın altındaydı); PAM ise
hiç ateşlemediği için (0.3'teki gibi) PAM lezyonu tanım gereği sıfır etki
veriyor. Yani erkek modelde dopamin sorusu için PPL1 okunabilir, PAM
okunamaz; tek simülasyon tohumuyla ölçüldüğü için küçük bir etki.

## 26. Alt tip taraması n = 1000 (Mac mini M4, çekici rejimi) (2026-10-29)

Kullanıcının M4'ünde 8 işçiyle 65 dakikada koşuldu (10 simülasyon / 32 s;
bulut konteynerinin 10 katı). `artifacts/sweep_v3_subtype1000.npz`,
`artifacts/surrogate_report_v3_subtype1000.npz`, şekiller
`artifacts/figures_n1000/`. Varsayılan rejim (APL×1), çünkü `--apl-scale`
tarama başladığında henüz yoktu.

| | n = 240 (bölüm 13) | n = 1000 |
|---|---|---|
| değişen özellik | — | 75 / 654 |
| ridge 5-kat CV R² | 0.33 | 0.52 |
| MLP topluluğu CV R² | — | 0.48 |
| NPE \|hata\|, lezyonlu girdiler | 0.475 | 0.406 |
| "hep 0.5" taban çizgisi | 0.268 | 0.258 |
| tespit (medyan > 0.2) lezyonlu / yanlış alarm | — | 0.20 / 0.08 |

Geri bulunan alt tipler (korelasyon): PPL101 0.91, PPL103 0.89, PPL105 0.87,
PPL106 0.70, PAM08 0.67, PAM04 0.64; geri kalan 26 alt tipte |r| < 0.6,
çoğu 0 civarı. Duyarlılık sıralaması aynı: PPL103 9.8, PPL105 5.1, PAM08 3.4,
sonra uzun kuyruk (0.5–1.8).

**Yorum.** Dört kat veri vekili iyileştiriyor (R² 0.33 → 0.52) ama ters
model hâlâ önemsiz taban çizgisini geçemiyor; bilgi taşıyan yalnızca
bölüm 10/13'te bulunan etiketli hatlar (doymuş MBON'u açıp kapatan DAN'lar).
Çekici rejiminde 32 boyutlu lezyon vektörünün ~5 boyutu okunabilir, gerisi
okunamaz; bu, artefakt bulgusunun büyük veriyle doğrulanması. Seyrek rejim
taraması (APL×5, n = 1000) Mac'te sırada.

## 27. Alt tip taraması n = 1000, seyrek rejim (APL×5) — ters model hiçbir şey öğrenmiyor (2026-10-29)

M4'te 63 dakika. `artifacts/sweep_v4_subtype1000_apl5.npz`,
`artifacts/surrogate_report_v4_subtype1000_apl5.npz`.

| | çekici (bölüm 26) | seyrek (APL×5) |
|---|---|---|
| değişen özellik | 75 / 654 | 56 / 654 |
| ridge 5-kat CV R² | 0.52 | −0.02 |
| MLP topluluğu CV R² | 0.48 | −0.40 |
| NPE \|hata\|, lezyonlu girdiler | 0.41 | 0.46 |
| "hep 0.5" taban çizgisi | 0.26 | 0.26 |
| tespit (medyan > 0.2) / yanlış alarm | 0.20 / 0.08 | 0.02 / 0.03 |
| geri bulunan alt tip (r > 0.6) | 6 | 0 (en iyi PPL107 r = 0.50) |

**Yorum.** Çekici rejiminde okunabilen altı etiketli hat (PPL101/103/105/106,
PAM08/04) seyrek rejimde tamamen kayboluyor; vekil modelin R²'si sıfıra
düşüyor, yani 32 boyutlu dopamin lezyon vektörü 654 boyutlu fenotipe
hiç yansımıyor. Bölüm 18'deki "PPL1/PAM kaybı gürültü tabanının altında"
bulgusunun 1000 rastgele karışık lezyonla, bütün alt tipler için
doğrulanmış hâli. Bu, çalışmanın ana negatif sonucunun en güçlü kanıtı.
Mac'te koşulacak başka iş kalmadı.

## 28. Oktopamin yolu: şeker→PAM ödül sinyali sinaptik konnektomda yok (2026-10-29)

`scripts/octopamine_path.py`, seyrek rejim; `artifacts/octopamine_path.csv`.
Biyolojide şeker ödülü PAM'a oktopamin nöronları üzerinden (OA-VUMa2,
OAMB reseptörü; Burke ve ark. 2012) taşınır. Konnektomda 43 OA-* nöronu
var (VUMa1-8, VPM3/4, AL2, ASM).

- Şeker GRN'lerinden hiçbir OA nöronuna doğrudan sinaps yok (0 mV).
- Şekerin etkinleştirdiği ağ OA nöronlarını çoğunlukla **inhibe** ediyor
  (hız-ağırlıklı girdi −0.3 … −7.5 mV/10 ms); hiçbiri şeker altında
  ateşlemiyor.
- OA→PAM sinapsları çok zayıf: en güçlüsü OA-VUMa6 (toplam 3.6 mV, 13 PAM),
  OA-VPM3 (3.3 mV, 12 PAM); 43 nöronun 35'inin PAM'a hiç sinapsı yok.
- 43 OA nöronunun tamamı 150 Hz'de doğrudan sürülünce PAM 0.5 Hz (%3'ü
  5 Hz üstünde), PPL1 ise 18 Hz; şeker + OA birlikte: PAM 0.4 Hz.

**Sonuç.** "Şeker→PAM yolu iki sinapsta var ama iletmiyor" ifadesi
yanlıştı; doğrusu: ödül yolu **sinaptik kablolamada yok**. Oktopamin
PAM'ı biyolojide sinaps dışı (hacim iletimi, OAMB) etkiler; konnektom
bunu içermez. Bu, modelin yapısal bir sınırı: tek-ağırlıklı LIF'e
parametre ayarıyla değil, ancak sinaps dışı bir modülasyon terimi
eklenerek giderilebilir. Önbaskıdaki ilgili cümleler buna göre düzeltildi.

## 29. Çekicinin Shiu'nun kendi Brian2 koduyla doğrulanması (2026-10-29)

`scripts/brian2_attractor_check.py`: aynı 68 ORN_DM1 nöronu, 150 Hz, 500 ms,
Shiu ve ark. 2024'ün orijinal `model.run_trial()` fonksiyonuyla (Brian2
2.11, cython), hiçbir değişiklik yapılmadan. Koşu 201 s. Sonuç
`artifacts/brian2_odor_DM1.npz`.

| | Shiu Brian2 (orijinal kod) | bizim NumPy simülatörü |
|---|---|---|
| KC'lerin 5 Hz üstü oranı | %64.4 (ort. 32.6 Hz) | %74.8 |
| MBON ortalama | 85 Hz | 161 Hz |
| PPL1 ortalama | 113 Hz (%81'i etkin) | 206 Hz |
| PAM ortalama | 21 Hz (%39'u etkin) | 45 Hz |
| 5 Hz üstü nöron | 7.946 | 9.945 |

**Yorum.** Beyin geneli çekici orijinal kodda da ortaya çıkıyor: KC'lerin
üçte ikisi, MBON'ların üçte ikisi, PPL1'in %81'i koku altında ateşliyor.
Bulgu simülatörümüze bağlı değil. Hızlar orijinal kodda yaklaşık %30–50
daha düşük (muhtemelen Poisson girdisinin ve sinaptik "g" değişkeninin
ayrıntılarındaki küçük farklar; şeker doğrulamasında r = 0.963 bunun
sıralamayı etkilemediğini gösteriyor); çekicinin varlığı ve ölçeği aynı.

## 30. Seyrekleştirme yönteminden bağımsızlık: KC eşiği +32 mV (2026-10-29)

`scripts/kc_threshold_check.py` (simülatöre nöron-başına `v_th_offset`
eklendi); `artifacts/kc_threshold.csv`. APL yerine Kenyon hücrelerinin
eşiği d mV yükseltildi. Koku altında KC etkin oranı: +1/+2 mV 0.73/0.70,
+4 0.65, +8 0.52, +12 0.36, +16 0.25, **+32 0.034**, +48 0.002. Çekici
şaşırtıcı derecede sağlam: KC'leri susturmak için 32 mV (eşik aralığının
4.5 katı) gerekiyor. +32 mV'de etkin nöron 5.664 (APL×5: 5.674), MBON
9.8 Hz (10.4), PPL1 13.9 Hz (16.3): APL×5 ile aynı çalışma noktası.

| seyrekleştirme | taban | PPL1 %100 | PAM %100 | RND16 %100 |
|---|---|---|---|---|
| APL×5 (bölüm 18, 5×2) | 1.91 | 1.74 | 1.12 | 1.16 |
| KC eşiği +32 mV (1 sıra, 2 tohum) | 1.67 | 1.22 | 1.15 | 0.88 |

**Yorum.** Dopamin lezyonlarının gürültü tabanının altında kalması APL'nin
nasıl ayarlandığına bağlı değil; KC seyrekliği hangi mekanizmayla
sağlanırsa sağlansın sonuç aynı.

## 31. Jo eğitim protokolü: PAM doğrudan sürülünce öğrenme ve sessiz rezerv (2026-10-29)

`scripts/jo_training_protocol.py` (seyrek rejim, κ=0.003, η=1e-4): koku
(ORN_DM1 150 Hz) + kalan PAM nöronlarının 100 Hz doğrudan sürülmesi 1 s;
PAM ve RND307 lezyonları %0/25/50/75/100, 2 tohum. `artifacts/jo_training.csv`.
Yol sorununu atlayan pozitif kontrol: öğretici sinyal kabloyla değil,
doğrudan veriliyor.

| MBON | ön hız | PAM %0 | %25 | %50 | %75 | %100 | RND307 %100 |
|---|---|---|---|---|---|---|---|
| MBON09 | 12.5 Hz | 1.00 | 1.00 | 1.00 | 1.00 | 0.06 | 1.00 |
| MBON33 | 18.3 Hz | 0.55 | 0.46 | 0.46 | 0.59 | 0.21 | 0.64 |
| MBON29 | 3.3 Hz | 1.00 | 1.00 | 0.50 | 0.50 | 0.00 | 1.00 |

(değerler öğrenme indeksi (ön − son)/ön, iki tohumun ortalaması)

**Yorum.** Modülatör katman doğrudan sürülen DAN'la nicel bir öğrenme
eğrisi veriyor ve bu eğri bir **sessiz rezerv** gösteriyor: MBON09'daki
bastırma PAM'ın %75'i kaybolana kadar tam, %100'de sıfır; rastgele 307
nöron kaybı etkisiz. Mekanizma kompartman yakınsaması: MBON09'a birden çok
PAM tipinden 52 nöron ≥2 mV'lik sinaps yapıyor (PAM12 23, PAM14 15, PAM13 12,
PAM08 2; toplam 244 mV) ve
kazanç kalan DAN'ların toplam hızına bağlı olduğu için dörtte biri bile
kapıyı açmaya yetiyor. Bu, Parkinson modellerindeki "belirtiler %60–80
dopamin kaybından sonra görünür" gözlemiyle aynı biçimde bir eşik; ama
burada rezerv pekiştireç yolunda değil DAN→MBON yakınsamasında, çünkü yol
atlanıyor. Jo'nun "DAN'ı kaldırınca öğrenme kaybolur" totolojisinin ötesine
geçen kısım, eşiğin konumu (%75–100 arası) ve kompartman yapısıyla
açıklanabilmesi.

## 32. Parkinson kolu I: konnektomdan hassasiyet haritası (2026-10-29)

`scripts/vulnerability_map.py`; `artifacts/vulnerability_map.csv`. Her dopamin
alt tipi için nöron başına sinaptik yük (giriş + çıkış temas sayısı), çıkış
temas sayısı ve postsinaptik partner sayısı: akson ağacı büyüklüğünün ve
enerji talebinin vekili (insan Parkinson'unda seçici hassasiyetin standart
açıklaması: büyük, miyelinsiz, yüksek yüklü aksonlar).

| Küme | n | yük (medyan/nöron) | çıkış temas | partner |
|---|---|---|---|---|
| PPL1 | 16 | 6.012 | 1.770 | 888 |
| PPL2 | 8 | 4.236 | 1.508 | 916 |
| PAM | 307 | 481 | 152 | 117 |

Alt tip sıralaması: PPL101 12.967, PPL103 11.916, PPL107 8.448 … en düşük
PAM03 257. PPL1 nöronları PAM nöronlarından nöron başına **12 kat** yüklü.

**Literatürle karşılaştırma** (`docs/literature_pd_vulnerability.json`,
doğrulanacak): mitokondriyal modellerde (parkin, PINK1; Whitworth 2005,
Yang 2006) kaybolan küme PPL1, PAM büyük ölçüde korunuyor; α-sinüklein
modelinde (Riemensperger 2013) ise PAM. Konnektom yükü ilk gruba tam
uyuyor: enerji-bağımlı (mitokondriyal) hasar yükü en yüksek kümeyi (PPL1)
vurmalı, ve vuruyor. α-sinüklein kaybının PAM'da olması ise yükle
açıklanamıyor; bu, iki hastalık mekanizmasının farklı hassasiyet kuralları
izlediğine dair modelden gelen bir ayrım. Öngörü: PINK1/parkin sineklerinde
PPL1 içinde kayıp sırası PPL101 → PPL103 → PPL107 olmalı; hücre tipi özgül
sayımla test edilebilir.

## 33. Pozitif kol: öğretici sinyal verilince konnektom hangi kompartmanların öğreneceğini söylüyor (2026-10-29)

`scripts/compartment_map.py` + `analyze_compartment_map.py`; sonuçlar
`artifacts/compartment_map_apl{5,3}.csv`, rezerv tabloları
`artifacts/compartment_reserve_apl{5,3}.csv`, eşleşmesiz gürültü
`artifacts/li_noise_apl{5,3}.csv`. Modülasyon katmanına sinaps dışı ödül
terimi eklendi (`ModulatedNetwork.add_extrasynaptic`: şeker GRN hızı × 0.5,
hayatta kalan her PAM'ın etkin dopamin hızına eklenir; oktopaminerjik
sinyalin yerine geçer); acı için ×4 röle yolu. Koku (ORN_DM1) + pekiştireç
1 s; indeks = (ön − son)/ön. Literatür haritası (Aso 2014/2016)
`docs/literature_compartments.json`, doğrulanacak.

**Şeker (ödül), öğrenen MBON'lar** (indeks ≥ 0.3, koku yanıtı ≥ 2 Hz;
eşleşmesiz kontrolün en büyüğü parantezde):

| Çalışma noktası | MBON | literatür kompartmanı | bellek | indeks | gürültü |
|---|---|---|---|---|---|
| APL×5 | MBON09 | γ3β'1 | iştah | 0.88 | 0.12 |
| APL×5 | MBON33 | (atanmamış) | ? | 0.47 | 0.13 |
| APL×3 | MBON07 | α1 | iştah | 1.00 | 0.03 |
| APL×3 | MBON02 | β2β'2a | iştah | 0.89 | 0.06 |
| APL×3 | MBON12 | γ2α'1 | ceza | 0.67 | 0.19 |

Üç atanmış iştah kompartmanının üçü de öğreniyor (literatürle uyum);
MBON12 ters yönde bir eşleşme (ceza kompartmanı şekerle bastırılıyor;
PPL1 kaybıyla kaybolmuyor ve RND307 kontrolde de 0.59, yani PPL1 üzerinden
değil, modelin bir artefaktı; olduğu gibi raporlandı). Kokuya yanıt veren
ama öğrenmeyen MBON'lar: 10, 20, 21, 26, 33 (APL×3'te ayrıca 09, 11, 14).

**Rezerv eşikleri (PAM kaybı; indeksin yarıya düştüğü ilk kayıp oranı):**
MBON07 %100 (%90'da hâlâ 1.00), MBON02 %90, MBON09 %75, MBON33 %75.
PPL1 kaybı hiçbirini etkilemiyor; RND307 %100 etkilemiyor. Eşik, yakınsayan
PAM sayısıyla tek başına açıklanmıyor (MBON09 52 PAM, MBON07 20): belirleyici
olan KC girdisi × kalan dopamin fazlası çarpımı.

**Acı (ceza): hiçbir MBON öğrenmiyor.** Nedeni mekanik ve ilginç: acı tek
başına PPL101'i 46 Hz'e çıkarıyor (giriş-sıçraması ×8), ama koku ile
birlikte verilince PPL101 0 Hz (koku ağı, büyük olasılıkla MBON→DAN geri
beslemesiyle, PPL1'i bastırıyor); eşleşme sırasında PPL1 hızı koku-tek
başına ile aynı (33 vs 36 Hz), dolayısıyla fazlalık yok. Modelde koku ve
ceza birbirini söndürüyor; biyolojide söndürmediği için bu, modelin MBON→DAN
geri besleme ağırlıklarına dair test edilebilir bir sorun işareti.

## 34. Parkinson kolu II: kayıp örüntüsü ve okuma değeri duyarlılığı (2026-10-30)

`scripts/pd_patterns.py`; `artifacts/pd_patterns.csv`; şekil 8A. PAM kaybı
rastgele (2 sıra), hassasiyet-sıralı (sinaptik yükü en yüksek nöronlar
önce; α-sinüklein benzeri seçici hassasiyet) ve dirençli-önce (tersi);
okumalar: iştah öğrenme indeksi (şeker protokolü, ödül terimiyle), pasif
koku yanıtı (MBON ortalaması) ve hareket DN'leri (DNp09, DNa01-03, DNb01-02,
DNg13; sol/sağ ortalama).

| MBON09 indeksi | %25 | %50 | %75 | %90 | %100 |
|---|---|---|---|---|---|
| rastgele | 0.88 | 0.97 | 0.90 | 0.07 | 0.07 |
| hassas-önce (yüksek yük önce) | 0.94 | 1.00 | 0.87 | 0.20 | 0.07 |
| dirençli-önce (düşük yük önce) | 0.88 | 1.00 | **0.00** | 0.07 | 0.07 |

Pasif okumalar hiçbir örüntüde, %100 kayıpta bile değişmiyor: MBON koku
ortalaması 6.3–6.8 Hz, hareket DN'leri sol 17.5–21.7 / sağ 8.3–11.7 Hz
(sağlam 20.0 / 8.8); PPL1 kaybında da aynı.

**Yorum.** (1) Kaybın sırası belirtinin zamanını belirliyor: MBON09'un
kompartmanındaki PAM'lar (PAM12/13/14) düşük yüklü olduğu için
"dirençli-önce" sırası bu belleği %75'te, "hassas-önce" sırası ancak %90'ın
üstünde siliyor. Öngörü: PINK1/parkin (yüksek yük önce) ve α-sinüklein
(farklı sıra) sineklerinde iştah belleği kusurunun aynı toplam kayıpta
farklı zamanda ortaya çıkması gerekir; hangi kompartmanın önce bozulduğu
kayıp örüntüsünün parmak izi. (2) Pasif ve hareket okumaları bu modelde
dopamin kaybını hiç göstermiyor; öğrenme testi %75–90'da gösteriyor.
İlaç taramalarında tırmanma yerine (ya da yanında) koşullanma testi
kullanılması modelin somut önerisi.

## 35. Parkinson kolu III: bellek korunumu, L-DOPA karşılığı, kompanzasyon (2026-10-30)

`scripts/pd_experiments.py retention|ldopa|compensation`; `artifacts/pd_*.csv`;
şekil 8B–C. Modülasyon katmanına `remove_neurons` (eğitimden sonra lezyon),
`add_tonic` (sinaps dışı sabit dopamin) ve `set_compensation` eklendi.

**Korunum.** Kayıptan önce öğretilen bellek, PAM'ın %50/75/100'ü
silindikten sonra tamamen korunuyor (MBON09 indeks 0.94–1.00; MBON33
0.41–0.53); aynı kayıptan sonra yeni edinim %90+'da yok (bölüm 34).
Öngörü: sinek Parkinson modellerinde edinim bozulurken hatırlama korunmalı;
insanda "eski alışkanlıklar korunur, yeni öğrenme bozulur" gözleminin devre
karşılığı. Mekanizma: bellek KC→MBON sinapsında, dopamin yalnızca yazma
kapısı.

**L-DOPA karşılığı.** Hayatta kalan tüm DAN'lara 10/30/60 Hz-eşdeğeri sabit
dopamin. Kapı tonik düzeye adapte olmuşsa (taban onunla ölçülmüşse) hiçbir
etki yok (eşleşmeli indeks 1.0, eşleşmesiz ≤ 0.21). Adapte olmamışsa
eşleşme olmadan da bastırma: MBON09 eşleşmesiz indeksi 30 Hz'de 0.75, 60
Hz'de 1.00, sağlam ve %75 kayıplı beyinde aynı; MBON33'te de 0.33'e çıkıyor,
diğer MBON'larda yok. Yani dopamin yerine koyma bu modelde öğrenmeyi
kurtarmıyor (rezerv zaten %75'i karşılıyor) ve kapı adapte değilse tam da
öğrenen kompartmanlarda eşleşmeden bağımsız, özgüllüğünü yitirmiş plastisite
üretiyor: "aşırı doz" / sapkın plastisite imzasının devre karşılığı.
Öngörü: L-DOPA beslenen sineklerde ödül kompartmanlarının MBON'larında
eşleşmesiz koku yanıtı düşmeli; adaptasyon varsa düşmemeli (ikisi ayırt
edilebilir).

**Kompanzasyon.** Kalan PAM'lar (1−f)^−α kat daha güçlü (α = 0, 0.5, 1;
%90 kayıpta 10 kata kadar). %50 ve %75'te zaten tam öğrenme (rezerv);
%90'da hiçbir kompanzasyon kurtarmıyor, çünkü MBON09 kompartmanının 52
PAM'ından 4'ü kalıyor ve kapı kompartman ortalamasına bağlı (4 nöron ×10
= 40 nöron-eşdeğeri, 52'nin altında). Sonuç: hayatta kalanların
hiperaktivitesi rezervi ancak kompartmanda yeterli nöron kaldığı sürece
uzatabilir; eşik kompartman başına kalan hücre sayısıyla sınırlı.

## 36. Pozitif/Parkinson kolunun parametre duyarlılığı (2026-10-30)

`scripts/pd_sensitivity.py`; `artifacts/pd_sensitivity.csv`. Sekiz takım:
temel (g_reward 0.5, κ 0.003, η 1e-4, acı ×4), g_reward ×0.5/×2, κ ×0.5/×2,
η ×0.5/×2, acı düzeltmesiz. Beş ölçüm, MBON09 için:

| takım | sağlam | %75 PAM | %90 PAM | korunum (%75) | L-DOPA 30 Hz eşleşmesiz |
|---|---|---|---|---|---|
| temel | 1.00 | 1.00 | −0.07 | 0.88 | 0.75 |
| g_reward ×0.5 | 0.56 | 0.53 | −0.07 | 0.50 | 0.75 |
| g_reward ×2 | 1.00 | 1.00 | 0.00 | 1.00 | 0.75 |
| κ ×0.5 | 1.00 | 1.00 | −0.07 | 0.94 | 0.54 |
| κ ×2 | 1.00 | 0.93 | −0.07 | 0.93 | 1.00 |
| η ×0.5 | 0.56 | 0.53 | −0.07 | 0.62 | 0.42 |
| η ×2 | 1.00 | 1.00 | 0.07 | 1.00 | 1.00 |
| acı düzeltmesiz | 0.93 | 1.00 | 0.12 | 0.93 | 0.79 |

**Yorum.** Dört nitel sonuç sekiz takımın hepsinde aynı: (1) iştah
belleği MBON09'da oluşuyor (0.56–1.00; MBON33 daha zayıf, 0.24–0.45); (2)
%75 PAM kaybında öğrenme korunuyor, %90'da kayboluyor (rezerv eşiği
parametreden bağımsız, çünkü eşik kompartmanda kalan hücre sayısıyla
belirleniyor); (3) kayıptan önce yazılan bellek korunuyor (korunum ≈
sağlam değer); (4) adapte olmamış kapıda tonik dopamin eşleşmesiz
bastırma üretiyor (0.42–1.00; κ ve η ile ölçeklenir). Acı yolunun
düzeltilmesi şeker koluna etki etmiyor. Yalnızca büyüklükler
(öğrenme indeksinin 0.56 mı 1.00 mü olduğu) ödül kazancı ve η ile
değişiyor. Not: filtresiz listede görünen MBON14/MBON29 "öğrenmeleri" 2 Hz
altı koku yanıtına dayanıyor (bölüm 33'teki eşik dışı), sayılmadı.

## 37. Öğrenme fenotipiyle ters model: n = 300, APL×3 (Mac, 2026-10-30)

`scripts/learning_sweep.py`; `artifacts/sweep_v5_learning_apl3.npz`,
`artifacts/surrogate_report_v5_learning.npz`. 32 alt tip üzerinde rastgele
karışık lezyonlar; fenotip = şeker ve acı eşleşmesi sonrası MBON başına
öğrenme indeksi + eşleşme öncesi koku yanıtı (105 özellik, 33'ü değişiyor).
M4'te 104 dakika.

| | çekici pasif (n=1000) | seyrek pasif (n=1000) | öğrenme (n=300) |
|---|---|---|---|
| ridge CV R² | 0.52 | −0.02 | −0.06 |
| NPE \|hata\| (taban 0.26) | 0.41 | 0.46 | 0.38 |
| tespit / yanlış alarm | 0.20 / 0.08 | 0.02 / 0.03 | 0.33 / 0.31 |
| r > 0.5 alt tip | 6 | 0 | PPL107 0.79, PAM12 0.56, PPL101 0.53, PPL106 0.51 |

**Yorum.** Öğrenme okumasıyla da 32 boyutlu lezyon vektörü geri
bulunamıyor; tespit oranı yanlış alarmla aynı. Ama alt tip düzeyinde bir
işaret var: PAM12 (MBON09 kompartmanının en kalabalık PAM tipi, 23 nöron)
öğrenme fenotipinden r = 0.56 ile okunuyor; pasif fenotipte 0.13 (çekici)
ve −0.44 (seyrek) idi. Yani öğrenme testi tam da öğrenen kompartmanın
DAN'larını okuyor, başkasını değil. Bu, problemin doğasını gösteriyor:
seyrek rejimde yalnızca 2–3 MBON öğreniyor, dolayısıyla fenotip ~3 bilgi
taşıyan boyut, parametre 32; 32-boyutlu karışık ters problem yanlış
tasarım. Doğru tasarım kompartman başına tek alt tip (ör. "PAM12 ne kadar
kayıp?") olmalı; o zaman rezerv eğrisi (bölüm 33–34) zaten cevabı veriyor.
Yapay zekâ kısmının dürüst sonucu: dopamin lezyonu için amortize ters model
ancak öğrenen kompartman sayısı kadar boyutta anlamlı.

## 38. Kapanış maddeleri I: PPL101'i susturan APL; ikinci koku (2026-10-30)

**Madde 1 — ceza kolunun çökme mekanizması.** `scripts/ppl1_silencing.py`,
`artifacts/ppl1_silencing.json`. PPL101'e gelen hız-ağırlıklı sinaptik
girdi (mV/10 ms), giriş-sıçraması ×8 ağında:

| koşul | PPL101 Hz | uyarım | inhibisyon | en güçlü inhibitör kaynak |
|---|---|---|---|---|
| koku | 0.0 | +133 | −241 | **APL −166**, CRE102 −26, SMP115 −17, MBON20 −9 |
| acı | 46.2 | +136 | −78 | MBON11 −55, CRE102 −12 |
| koku + acı | 0.0 | +173 | −242 | APL −166, CRE102 −26, SMP115 −17 |

Koku altında PPL101'i susturan MBON→DAN geri beslemesi değil, **APL**:
seyrek rejimi yaratmak için KC'lere inhibisyonunu 5 kat artırdığımız
GABAerjik APL, koku altında güçlü ateşliyor ve PPL101'e doğal ağırlığıyla
(ölçeklenmemiş) 166 mV/10 ms inhibisyon gönderiyor; uyarımın (KC'lerden
81) iki katı. Acı tek başına verilince APL sessiz, inhibisyon MBON11'den
(−55) geliyor ve PPL101 46 Hz ateşliyor. Düzeltme testi: APL→PPL1
sinapsları sıfırlanınca koku+acı altında PPL101 66 Hz, koku tek başına 45
Hz (fazlalık +21 Hz); CRE102 veya SMP115 çıkarmak hiçbir şey değiştirmiyor.
Yani acı öğrenmesini engelleyen tek bağlantı APL→PPL1. Acı koşullanması bu
düzeltmeyle koşuluyor (sırada). Biyolojik yorum: konnektomda APL→PPL1
sinapsları var; modelde APL'nin koku altındaki aşırı aktivitesi (seyreklik
için gereken ×5 kazancın yan etkisi) ceza kapısını kapatıyor. Öngörü:
koku+şok eşleşmesi sırasında PPL1-γ1pedc'nin ateşlemesi APL susturulunca
artmalı.

**Madde 2 — ikinci koku.** `compartment_map.py --apl-scale 3 --odor
ORN_DL5,ORN_DM2,ORN_VM2` (Jo'nun "koku B"si; 11 MBON tipi yanıt veriyor);
`artifacts/compartment_map_apl3_odorB.csv`. Öğrenenler koku A ile aynı:
MBON07 1.00, MBON02 0.78, MBON12 0.44 (artefakt, yine dopaminden
bağımsız); rezerv aynı (MBON07 ve MBON02 %90'da tam, %100'de sıfır; PPL1
ve RND307 etkisiz). Kompartman haritası ve rezerv eşiği kokudan bağımsız.
MBON01/03 bu kokuya da yanıt vermiyor; bu iki kompartman modelde hiçbir
kokuyla test edilemiyor.

## 39. Kapanış maddeleri II: rezerv ve KC girdisi; acı düzeltmesi (2026-10-30)

**Madde 6 — rezerv eşiği KC girdisine bağlı mı?** KC→MBON09 sinapsları
×0.5 ve ×2 (`artifacts/compartment_map_kc{0.5,2}.csv`, seyrek rejim, şeker).
×0.5: MBON09 kokuya hiç yanıt vermiyor (0 Hz), öğrenme ölçülemiyor. ×2:
koku yanıtı 13 → 48 Hz, ama öğrenme indeksi 0.88 → 0.37'ye düşüyor ve
rezerv eşiği öne geliyor (%50 0.38, %75 0.27, %90 0.08; PPL1 kaybı
etkisiz). Yani KC girdisi arttıkça aynı dopamin fazlası sinapsların daha
küçük bir oranını siliyor (plastisite kuralı sinaps başına kesirli,
yanıt ise doygun) ve bellek daha erken kaybolur. Eşik gerçekten KC girdisi
× dopamin fazlası çarpımıyla belirleniyor; tek başına yakınsayan DAN
sayısıyla değil (bölüm 33'teki hipotez doğrulandı, yön: güçlü KC girdisi =
daha küçük rezerv).

**Madde 1 devamı — APL→PPL1 düzeltmesiyle acı koşullanması** (APL×5,
`artifacts/compartment_map_bitter_aplppl1x0.csv`): eşleşme sırasında PPL1
58 Hz (koku tek başına 45 Hz, fazlalık +13 Hz), PPL1 kaldırılınca 0 Hz;
ama bu rejimde ceza kompartmanlarının MBON'ları (11, 12, 14) kokuya yanıt
vermediği için öğrenme görünmüyor (yanıt veren 6 MBON'da indeks ≤ 0.14,
gürültü düzeyi). Aynı düzeltme ara rejimde (APL×3; MBON11/12/14 yanıt
veriyor) sırada.

## 40. Kapanış maddeleri III: Jo'nun tam kuralı; adaptasyonlu nöron (2026-10-30)

**Madde 7 — Jo'nun üç kuralı birlikte** (nöron kaybı + sinaps kaybı
[temas başına p = 0.6·s·v] + eşik kayması [−2·s·v mV]; s = 0.5, 4 tekrar;
`jo_retest.py --full`, `artifacts/jo_retest_full.csv`):

| rejim | hub | shuffled | antihub | antihub/hub |
|---|---|---|---|---|
| çekici | %44 (temas kaybı %50) | %67 (%34) | %92 (%15) | 2.09 |
| seyrek | %71 (%50) | %76 (%34) | %100 (%15) | 1.41 |
| Jo (MaleCNS, PN sürülmüş) | %31 | %47 | %93 | 3.04 |

Sinaps kaybı ve eşik kayması eklenince çekici rejimdeki oran Jo'nunkine
yaklaşıyor (1.7 → 2.1); seyrek rejimde hub haritası yine iki-modlu (KC
ortalaması 0.28: APL kaybı olan tekrarlar çekiciye düşüyor). Bölüm 23 ile
aynı sonuç: sıralama korunuyor, büyüklük ve tüm-beyin okumasının işareti
çalışma noktasına bağlı.

**Madde 4 — farklı nöron modeli: spike-frekans adaptasyonu** (eşik her
spike'ta Δ mV yükselir, τ ile söner; `LIFParams(tau_adapt, delta_adapt)`;
`artifacts/adaptation_check.csv`, `compartment_map_adapt.csv`). APL×1,
koku, 1 s:

| τ, Δ | KC %5 Hz üstü (erken / geç pencere) | etkin | MBON Hz |
|---|---|---|---|
| yok | 75 / 75 | 9.943 | 161 |
| 1 s, 0.1 mV | 65 / 52 | 8.231 | 69 |
| 1 s, 0.25 mV | 47 / 22 | 6.347 | 21 |
| 1 s, 0.5 mV | 22 / 3 | 3.775 | 5 |
| 1 s, 1 mV (Jo) | 1 / 0 | 1.428 | 0.6 |
| 1 s, 2–4 mV | 0 / 0 | 462 / 73 | 0 |

Adaptasyon çekiciyi kaldırıyor ama yerine kararlı bir seyrek koku kodu
koymuyor: her Δ'da yanıt zamanla sönüyor, Jo'nun değerinde (1 mV) koku
yanıtı tamamen kayboluyor. Jo'nun PN'leri doğrudan sürmesi bunu
gizliyor; ORN'den sürülen modelde adaptasyon seyreklik için uygun bir
mekanizma değil. APL×5 + adaptasyon (Δ 1 mV): taban 1.93, PPL1 %100 0.97,
PAM 1.57, RND16 1.01 (negatif iddia aynen); MBON09 koku yanıtı 0 Hz
olduğundan pozitif kol bu varyantta ölçülemiyor. Sonuç: nöron modelini
değiştirmek negatif sonucu değiştirmiyor, pozitif kolun sınanması için
kararlı seyrek koda sahip bir varyant gerekir (bu, bir sonraki çalışmanın
konusu).

## 41. Kapanış maddeleri IV: erkek pozitif kol; ara rejimde acı düzeltmesi (2026-10-30)

**Madde 5 — erkek konnektomda pozitif kol** (ölçek 0.35, APL×5, ödül
terimiyle; `artifacts/compartment_map_male.csv`): koku altında yalnızca 3
MBON tipi (MBON31, 28, 26) 2 Hz üstünde, hiçbiri öğrenmiyor (en yüksek
0.22); PAM 0 Hz, PPL1 3 Hz. Bu çalışma noktası erkek mantar gövdesi için
fazla sessiz; erkekte pozitif kol ancak erkeğe özgü bir MB çalışma noktası
aranarak test edilebilir, burada yapılmadı.

**Madde 1 sonucu — APL→PPL1 kaldırılmış ağda acı koşullanması, ara rejim
(APL×3)** (`artifacts/compartment_map_bitter_apl3_aplppl1x0.csv`): eşleşme
sırasında PPL1 106 Hz; 10 MBON tipi kokuya yanıt veriyor. Öğrenen: MBON12
(literatürde γ2α'1, ceza kompartmanı) indeks 0.33 (10 → 6.7 Hz), PPL1 %100
kaybıyla −0.07, RND307 ile 0.13; eşleşmesiz gürültü bu MBON'da 0.19. Yani
modelin ilk PPL1'e bağımlı ceza öğrenmesi, doğru kompartmanda, ama zayıf
(gürültünün ~1.7 katı). MBON11 (γ1pedc; 125 Hz) ve MBON14 (α3; 61 Hz)
öğrenmiyor. Ceza kolunun tam çalışması için APL→PPL1'in kaldırılması
gerekli ama yeterli değil; MBON11/14'teki eksiklik bu kompartmanların
KC girdisinin doymuş olmasına (125 ve 61 Hz) bağlı olabilir (bölüm 39'daki
KC girdisi–rezerv ilişkisiyle tutarlı). Bu noktada bırakıldı.

## 42. Kapanış maddesi 3: Parkinson deneyleri 5 tohumla (Mac, 2026-10-30)

`artifacts/pd_patterns_s5.csv`, `pd_retention_s5.csv`, `pd_compensation_s5.csv`,
`pd_ldopa_s2.csv` (M4'te toplam ~50 dk). Ortalama ± SD, MBON09:

| PAM kaybı | %25 | %50 | %75 | %90 | %100 |
|---|---|---|---|---|---|
| öğrenme, rastgele sıra (5 tohum) | 0.91 ± 0.06 | 0.86 ± 0.28 | **0.67 ± 0.39** | 0.11 ± 0.19 | 0.07 ± 0.00 |
| korunum (5 tohum) | — | 0.96 ± 0.06 | 0.95 ± 0.07 | — | 1.00 ± 0.00 |
| kompanzasyon α=1 (5 tohum) | — | 0.86 ± 0.32 | 0.66 ± 0.49 | 0.12 ± 0.18 | — |

Hassas-önce: %75 0.87, %90 0.20; dirençli-önce: %75 0.00. Pasif okumalar
(70 lezyonlu iş): hareket DN sol 20.6 ± 1.3 Hz (sağlam 20.0; en büyük
sapma 3.8), sağ 9.8 ± 1.0 (8.8; 3.3), MBON koku ortalaması 6.5 ± 0.2
(6.5; 0.4). L-DOPA (2 tohum): adapte olmamış kapıda eşleşmesiz bastırma
0.15 / 0.75 / 1.00 (10/30/60 Hz), SD ≤ 0.01; adapte kapıda ≤ 0.21.

**Düzeltilen ifade.** İki tohumla "%75'e kadar tam" görünen rezerv, beş
tohumla iki-modlu çıktı: %75 kayıpta tohumların bir kısmı tam öğreniyor,
bir kısmı hiç (0.67 ± 0.39), çünkü sonuç MBON09'un kendi kompartmanındaki
52 PAM'dan kaçının rastgele kaldığına bağlı. Doğru ifade: rezerv %50'ye
kadar güvenilir (0.86), %75'te kaybın hangi hücrelere düştüğüne bağlı,
%90'da bitmiş. Bu, kayıp sırası bulgusuyla (bölüm 34) aynı mekanizma ve
onu güçlendiriyor. Korunum, kompanzasyonun etkisizliği ve L-DOPA imzası
tohumlar arasında kararlı. Önbaskı ve şekil 8 buna göre güncellendi.

## 43. Literatür eşlemelerinin doğrulanması (2026-10-30)

Ağ izni açılınca eLife tam metinleri okundu. `docs/literature_compartments.json`
yeniden yazıldı: MBON01–22 adları Aso 2014 Tablo 1'den birebir teyit edildi
(önceki dosyadaki hepsi doğruydu); DAN tip tablosu eklendi (PAM01 γ5, PAM02
β'2a, PAM03 β2β'2a, PAM04 β2, PAM05 β'2p, PAM06 β'2m, PAM07 γ4<γ1γ2, PAM08 γ4,
PAM09 β1ped, PAM10 β1, PAM11 α1, PAM12 γ3, PAM13 β'1ap, PAM14 β'1m, PAM15
γ5β'2a [Li 2020]; PPL101 γ1pedc, PPL102 γ1, PPL103 γ2α'1, PPL104 α'3, PPL105
α'2α2, PPL106 α3; PPL107/108 yalnızca FlyWire'da). Bellek atamaları Aso &
Rubin 2016'ya göre "doğrudan" (o kompartmanın DAN'ıyla eğitim yapılmış:
γ1pedc, γ2α'1+α'2α2, α3 → ceza; α1, γ5+β'2a → ödül) ve "dolaylı" (küme
bazlı) olarak işaretlendi. Bulgularımızın dayandığı üç atama — MBON07 (α1),
MBON02 (β'2a kısmı), MBON12 (γ2α'1) — doğrudan kanıtlı; MBON09 (γ3β'1) dolaylı.
MBON23+ hemibrain'in atipik tipleri; MBON33 (γ2γ3) ve MBON26/29 atanmamış.

`docs/literature_pd_vulnerability.json` düzeltildi: Whitworth 2005 ve Yang
2006 PPL1 kaybı (teyit); **Wang 2006 ise PAL, PPM1/2, PPM3, PPL2'de belirgin,
PPL1'de daha az kayıp bildiriyor** (önceki dosyada yanlış özetlenmişti);
Riemensperger 2013 ön-medyal ~15 DA nöronu (PAM alt kümesi, β/β' lobu);
ayrıca Navarro 2014 (J Neurochem 131:369-382) uyarısı eklendi: nükleer
muhabirle sayıldığında bu modellerin hiçbirinde DA nöron kaybı yok, yalnızca
muhabir sinyali düşüyor. Önbaskıdaki hassasiyet paragrafı buna göre
yumuşatıldı: "parkin ve PINK1'de PPL1 kaybı bildiren çalışmalarla uyumlu;
PINK1'de daha geniş kayıp bildiren ve hiç kayıp bulmayan çalışmalar da var".

## 44. Önbaskı: başlık, yazar bilgisi, yapay zekâ beyanı (30 Ekim 2026)

Son başlık (İngilizce ve Türkçe sekme): "Testing connectome-constrained
Drosophila brain models with simulation-based inference: the limits of
dopaminergic neuron loss and predictions for Parkinson's disease" /
"Simülasyon tabanlı çıkarımla konnektom kısıtlı Drosophila beyni modellerini
sınamak: dopaminerjik nöron kaybının sınırları ve Parkinson'a ilişkin
öngörüler". Başlık çalışmanın kendi makine öğrenmesi yöntemini (vekil
topluluğu + nöral posterior tahmini) adlandırıyor; "yapay zekâ destekli"
ifadesi başlığa alınmadı. Yazar: Kaan Tiftikçi, bağımsız araştırmacı, kurum
bağlantısı yok, yazışma kaantiftikci@outlook.com. "Yazar katkıları" bölümüne
asistanın hangi aşamalarda kullanıldığını (tasarım, yazılım, simülasyon ve
analiz, literatür kontrolü, yazım ve çeviri; veri üretilmedi/değiştirilmedi)
altı maddede açıklayan bir paragraf eklendi. Türkçe sekme tamamlandı.
