# sinek

Konnektom kısıtlı sinek beyninde hücre tipi çözünürlüklü lezyon modellemesi ve
amortize ters model (lezyon ↔ fenotip). Araştırma planı: `docs/PLAN.md`.

Önbaskı (İngilizce ve Türkçe): https://claude.ai/artifact/DruVxt92vyNSXWUAV9bQ1K
— "Testing connectome-constrained Drosophila brain models with simulation-based
inference: the limits of dopaminergic neuron loss and predictions for
Parkinson's disease" (Kaan Tiftikçi, 2026). Atıf bilgisi: `CITATION.cff`.

```
pip install -e ".[dev]"          # simülatör + testler (NumPy/SciPy yeterli)
pip install -e ".[ai]"           # vekil model ve NPE için torch + sbi
scripts/fetch_data.sh            # FlyWire v783 verisi (GitHub, ~200 MB)
python -m pytest -q
python scripts/smoke_sugar_fdg.py                 # tüm beyin, 300 ms, ~8 s
python scripts/validate_vs_shiu.py --shiu-dir <Drosophila_brain_model klonu>
python scripts/progressive_curve.py --groups PPL1 PAM KC
python scripts/run_lesion_sweep.py --n 500 --procs 4
python scripts/train_surrogate.py
python scripts/reinforcer_path.py rates|paths|boost --apl-scale 5    # pekiştireç → DAN yolu
python scripts/jo_retest.py --s 0.5 --reps 8                        # Jo (2026) nöron-kaybı protokolü, iki rejim
python scripts/export_viewer.py && python -m http.server -d viewer  # 3B izleyici
```

Ana bulgu (ayrıntı `docs/PLAN.md` bölüm 0): modelin dopamin özgüllüğü koku
çekicisinin artefaktı; seyrek rejimde (APL×5) dopamin lezyonları gürültü
tabanının altında; pekiştireçler dopamin nöronlarına ulaşmıyor (acı→PPL1
yolu 20 rölenin 4 kat güçlendirilmesiyle iletiyor, şeker→PAM yolu iletmiyor).
GPU/M4 koşum notları: `docs/gpu_runbook.md`.

Kaynak notları: her işçi konnektomu çatallama (fork) ile paylaşır, ama
16 GB'lık bir makinede 3 işçi + eş zamanlı vekil/NPE eğitimi belleği aşıp
oturumu düşürdü. `--procs 3` üst sınır, eğitimi taramalardan sonra ayrı
çalıştırın. Uzun deneyler kontrol noktası yazar (`--resume`). GPU'da:
`python scripts/run_lesion_sweep.py --backend torch --device cuda --procs 1`.

Paket düzeni:

| Modül | İş |
|---|---|
| `sinek.data` | FlyWire v783 yükleyici, hücre grubu / uyaran / okuma seçicileri |
| `sinek.sim` | Shiu et al. 2024 LIF modelinin olay güdümlü NumPy uygulaması |
| `sinek.lesion` | iç içe, ilerleyici, hücre tipi düzeyinde lezyonlar; lezyon vektörü ve prior |
| `sinek.readout` | uyaran bataryası altında fenotip vektörü |
| `sinek.surrogate` | θ→x MLP topluluğu, duyarlılık ve ters tarama |
| `sinek.inference` | sbi ile nöral posterior tahmini |
| `sinek.neuromod` | konnektomdan türetilen MB kompartmanları, dopamin kapılı kazanç ve plastisite |
| `sinek.embodied` | inen nöron hızları → NeuroMechFly yürüyüş |
| `sinek.data.malecns` | MaleCNS v1.0 yükleyici (neuPrint token) |
| `sinek.sim.lif_torch` | GPU'ya hazır torch arka ucu |

Sonuçlar ve şekiller: `artifacts/figures/` (şekil 1 ilerleyici lezyon
eğrileri, şekil 2 vekil duyarlılık haritası, şekil 3 posterior geri bulma),
veri dosyaları `artifacts/*.npz|csv.gz`. Ayrıntılı sonuç bölümleri için
`docs/PLAN.md` 8-15.

Gövdeli okuma (faz 2) için ek kurulum:

```
pip install "flygym @ git+https://github.com/NeLy-EPFL/flygym.git@v2.1.1"
MUJOCO_GL= python scripts/embodied_lesion.py --stimuli combo
```
