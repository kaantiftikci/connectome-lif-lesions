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
