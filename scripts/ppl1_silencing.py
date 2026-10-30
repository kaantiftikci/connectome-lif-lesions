"""Item 1: what silences PPL101 when the odour is present?

Under bitter alone (input-hop x8 route) PPL101 fires ~46 Hz; with the odour
added it fires 0 Hz.  Decompose the rate-weighted synaptic input onto PPL101
(and the whole PPL1 cluster) under odour, bitter and odour+bitter by
presynaptic cell class/type, then test the minimal fixes: removing the
dominant inhibitory feedback (by class) and re-measuring PPL1 under pairing,
and finally running the bitter conditioning with that fix.

Run:  python scripts/ppl1_silencing.py --apl-scale 5
"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from sinek.data import load_flywire, build_stimuli
from sinek.data.flywire import Connectome
from sinek.lesion import apl_scaled, scale_edges
from sinek.sim import simulate, firing_rates
from reinforcer_path import active_relays

ap = argparse.ArgumentParser(); ap.add_argument("--apl-scale", type=float, default=5.0); ap.add_argument("--k", type=float, default=8.0)
args = ap.parse_args()
base = apl_scaled(load_flywire(), args.apl_scale); m = base.meta
T = base.select(cell_type__startswith="PPL1"); us = base.select(cell_sub_class="bitter")
A, relays, _ = active_relays(base, us, T)
cn = Connectome(ids=base.ids, W=scale_edges(base, A, relays, args.k), meta=m, name="in-only")
stim = {s.name: s for s in build_stimuli(cn)}; cs = stim["odor_DM1"].targets
ppl101 = cn.select(cell_type="PPL101")
conds = {"odour": {int(i): 150.0 for i in cs}, "bitter": {int(i): 150.0 for i in us}, "odour+bitter": {**{int(i): 150.0 for i in cs}, **{int(i): 150.0 for i in us}}}
rates = {k: firing_rates(simulate(cn.W, 500.0, poisson=v, seed=0), 100.0) for k, v in conds.items()}
W = cn.W.tocsc()
def inputs(r, targets):
    col = W[:, targets]; pre = col.tocoo()
    df = pd.DataFrame({"pre": pre.row, "w": pre.data, "r": r[pre.row]})
    df["drive"] = df.w * df.r / 100.0   # mV per 10 ms
    df["cls"] = m.loc[df.pre, "cell_class"].astype(str).values; df["typ"] = m.loc[df.pre, "cell_type"].astype(str).values
    df["sc"] = m.loc[df.pre, "super_class"].astype(str).values
    return df
rows = []
for k, r in rates.items():
    print(f"\n== {k}: PPL101 {r[ppl101].mean():.1f} Hz, PPL1 {r[T].mean():.1f} Hz, active {(r>5).sum()} ==")
    df = inputs(r, ppl101); df = df[df.r > 0]
    exc = df[df.w > 0].drive.sum(); inh = df[df.w < 0].drive.sum()
    print(f"  total excitation {exc:.1f} mV/10ms, inhibition {inh:.1f} mV/10ms")
    top_i = df[df.w < 0].groupby("typ")["drive"].sum().sort_values().head(8)
    top_e = df[df.w > 0].groupby("typ")["drive"].sum().sort_values(ascending=False).head(8)
    print("  strongest inhibitory presynaptic types:", {t: round(v, 1) for t, v in top_i.items()})
    print("  strongest excitatory presynaptic types:", {t: round(v, 1) for t, v in top_e.items()})
    by_cls = df.groupby("cls")["drive"].sum().sort_values(); print("  by class:", {c: round(v, 1) for c, v in by_cls.items() if abs(v) > 0.5})
    rows.append({"cond": k, "ppl101_hz": float(r[ppl101].mean()), "exc": exc, "inh": inh, "top_inh": top_i.to_dict(), "top_exc": top_e.to_dict()})
Path("results").mkdir(exist_ok=True); pd.DataFrame(rows).to_json("results/ppl1_silencing.json", orient="records", indent=1)
# minimal fix candidates: remove the top inhibitory presynaptic types' synapses onto PPL1 (odour+bitter condition)
df = inputs(rates["odour+bitter"], ppl101); df = df[(df.r > 0) & (df.w < 0)]
cands = df.groupby("typ")["drive"].sum().sort_values().head(3).index.tolist()
print("\nfix candidates (inhibitory types onto PPL101 under odour+bitter):", cands)
for t in cands:
    pre = cn.select(cell_type=t)
    W2 = scale_edges(cn, pre, T, 0.0)
    r2 = firing_rates(simulate(W2, 500.0, poisson=conds["odour+bitter"], seed=0), 100.0)
    r3 = firing_rates(simulate(W2, 500.0, poisson=conds["odour"], seed=0), 100.0)
    print(f"  remove {t}->PPL1 ({pre.size} neurons): odour+bitter PPL101 {r2[ppl101].mean():.1f} Hz, PPL1 {r2[T].mean():.1f}; odour alone PPL101 {r3[ppl101].mean():.1f}, PPL1 {r3[T].mean():.1f}; active {(r2>5).sum()}")
