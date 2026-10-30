"""Search for an odour stimulus that stays out of the model's high-activity
attractor (docs/PLAN.md 5b).  Variants: fewer ORNs, other glomeruli, brief
pulses, global synaptic scale.  Reports active neurons, fraction of Kenyon
cells active (real odour responses: ~5-10 %), MBON mean rate, and whether
activity persists after a pulse ends.

Run:  python scripts/odor_regime_search.py --out results/odor_regime.csv
"""
import argparse, sys, time
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire      # noqa: E402
from sinek.sim import simulate           # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--out", default="results/odor_regime.csv")
args = ap.parse_args()

cn = load_flywire()
kc = cn.select(cell_class="Kenyon_Cell")
mbon = cn.select(cell_type__startswith="MBON")
dn = cn.select(super_class="descending")
rng = np.random.default_rng(0)
rows = []


def stats(rec, a, b):
    sel = (rec.times >= a) & (rec.times < b)
    ids = rec.ids[sel]
    act = np.unique(ids)
    rate = np.bincount(ids, minlength=cn.n) / ((b - a) / 1000.0)
    return dict(active=int(act.size), kc_frac=float(np.isin(kc, act).mean()),
                mbon_hz=float(rate[mbon].mean()), dn_active=int(np.isin(act, dn).sum()))


def run(label, W, targets, rate, pulse=None, duration=600.0):
    t0 = time.time()
    if pulse is None:
        rec = simulate(W, duration, poisson=targets, poisson_rate=rate, seed=0)
    else:
        r1, st = simulate(W, pulse, poisson=targets, poisson_rate=rate, seed=0, return_state=True)
        r2 = simulate(W, duration - pulse, poisson=None, state=st)
        rec = r2
        rec.times = np.concatenate([r1.times, r2.times]); rec.ids = np.concatenate([r1.ids, r2.ids])
    on = stats(rec, 100.0, 300.0)
    late = stats(rec, 450.0, 600.0)
    row = dict(variant=label, n_targets=int(len(targets)), rate=rate, pulse_ms=pulse or 0,
               active_on=on["active"], kc_frac_on=round(on["kc_frac"], 3), mbon_hz_on=round(on["mbon_hz"], 1),
               dn_on=on["dn_active"], active_late=late["active"], kc_frac_late=round(late["kc_frac"], 3),
               secs=round(time.time() - t0))
    rows.append(row)
    print(row, flush=True)
    pd.DataFrame(rows).to_csv(args.out, index=False)


dm1 = cn.select(cell_type="ORN_DM1")
run("DM1_all@150", cn.W, dm1, 150.0)
for k in (34, 17, 8):
    run(f"DM1_{k}@150", cn.W, rng.choice(dm1, k, replace=False), 150.0)
for p in (50.0, 150.0):
    run(f"DM1_all_pulse{int(p)}", cn.W, dm1, 150.0, pulse=p)
for g in ("ORN_DL5", "ORN_DC2", "ORN_VC3", "ORN_DM5", "ORN_VA2", "ORN_DA2"):
    idx = cn.select(cell_type=g)
    if idx.size:
        run(f"{g}@150", cn.W, idx, 150.0)
for scale in (0.8, 0.6):
    W = (cn.W * scale).tocsr()
    run(f"DM1_all@150_wsyn{scale}", W, dm1, 150.0)
    run(f"sugar@150_wsyn{scale}", W, cn.select(cell_sub_class="sugar"), 150.0)
print("wrote", args.out)
