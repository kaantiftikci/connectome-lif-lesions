# sinek

Konnektom kısıtlı sinek beyninde hücre tipi çözünürlüklü lezyon modellemesi ve
amortize ters model (lezyon ↔ fenotip). Araştırma planı: `docs/PLAN.md`.

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
```

Paket düzeni:

| Modül | İş |
|---|---|
| `sinek.data` | FlyWire v783 yükleyici, hücre grubu / uyaran / okuma seçicileri |
| `sinek.sim` | Shiu et al. 2024 LIF modelinin olay güdümlü NumPy uygulaması |
| `sinek.lesion` | iç içe, ilerleyici, hücre tipi düzeyinde lezyonlar; lezyon vektörü ve prior |
| `sinek.readout` | uyaran bataryası altında fenotip vektörü |
| `sinek.surrogate` | θ→x MLP topluluğu, duyarlılık ve ters tarama |
| `sinek.inference` | sbi ile nöral posterior tahmini |
