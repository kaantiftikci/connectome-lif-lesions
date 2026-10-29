"""Independent check of the odour attractor with the reference model's own
Brian2 code (Shiu et al. 2024, github.com/philshiu/Drosophila_brain_model).

Drives the same ORN_DM1 set (or sugar, as a sanity control) in the original
run_trial() and reports Kenyon-cell / MBON / DAN activity, so the attractor
claim does not rest on our NumPy simulator.

Run:  python scripts/brian2_attractor_check.py --shiu-dir <clone> --stimulus odor_DM1 --duration 500
"""
import argparse, sys, time
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire, build_stimuli   # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--shiu-dir", required=True)
ap.add_argument("--stimulus", default="odor_DM1")
ap.add_argument("--duration", type=float, default=500.0)
ap.add_argument("--rate", type=float, default=None)
ap.add_argument("--codegen", default="numpy", help="brian2 codegen target: numpy (no compiler) or cython")
args = ap.parse_args()

sys.path.insert(0, args.shiu_dir)
from brian2 import prefs, ms, Hz   # noqa: E402
prefs.codegen.target = args.codegen
import model as shiu   # noqa: E402

shiu_dir = Path(args.shiu_dir)
path_comp = shiu_dir / "Completeness_783.csv"; path_con = shiu_dir / "Connectivity_783.parquet"
comp = pd.read_csv(path_comp, index_col=0)
root_ids = comp.index.to_numpy() if "root_id" not in comp.columns else comp["root_id"].to_numpy()
if "Unnamed: 0" in comp.columns:
    comp = comp.set_index("Unnamed: 0")
# brian index i corresponds to row i of the completeness table; map our root ids onto it
cn = load_flywire(); stim = {s.name: s for s in build_stimuli(cn)}[args.stimulus]
our_ids = cn.ids[np.asarray(stim.targets)]
id2brian = {int(r): i for i, r in enumerate(root_ids)}
exc = [id2brian[int(r)] for r in our_ids if int(r) in id2brian]
print(f"{args.stimulus}: {len(exc)}/{len(our_ids)} stimulated neurons mapped to brian indices", flush=True)
params = dict(shiu.default_params); params["t_run"] = args.duration * ms
params["r_poi"] = (args.rate if args.rate is not None else stim.rate_hz) * Hz
t0 = time.time()
spk = shiu.run_trial(exc, [], [], str(path_comp), str(path_con), params)
print(f"brian2 run done in {time.time()-t0:.0f}s", flush=True)
# rates after 100 ms
n = len(root_ids); counts = np.zeros(n)
for i, times in spk.items():
    t = np.asarray(times / ms if hasattr(times, "dimensions") else times)
    counts[i] = (t >= 100.0).sum()
rates = counts / ((args.duration - 100.0) / 1000.0)
brian2our = np.full(n, -1); id2our = {int(r): i for i, r in enumerate(cn.ids)}
for bi, r in enumerate(root_ids):
    brian2our[bi] = id2our.get(int(r), -1)
m = cn.meta
def frac(sel, thr=5.0):
    b = np.where(np.isin(brian2our, sel))[0]; return float((rates[b] > thr).mean()), float(rates[b].mean()), b.size
for name, sel in (("Kenyon cells", cn.select(cell_class="Kenyon_Cell")), ("MBON", cn.select(cell_type__startswith="MBON")),
                  ("PPL1", cn.select(cell_type__startswith="PPL1")), ("PAM", cn.select(cell_type__startswith="PAM"))):
    f, mean, k = frac(sel); print(f"{name:13s} n={k:5d}: {100*f:5.1f}% above 5 Hz, mean {mean:6.1f} Hz")
print(f"all neurons above 5 Hz: {(rates > 5).sum()}; total spikes after 100 ms: {int(counts.sum())}")
Path("results").mkdir(exist_ok=True)
np.savez(f"results/brian2_{args.stimulus}.npz", rates=rates, root_ids=root_ids)
