"""Learning-index noise floor: the same pre/post odour tests WITHOUT pairing
(odour alone with plasticity on), so an LI can be judged against trial-to-trial
variability per MBON.  Also tests an input-hop-only bitter route (relays' input
x k, output untouched) so that the odour itself does not drive PPL1 harder.

Run:  python scripts/li_noise.py --apl-scale 5 --seeds 3
"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from sinek.data import load_flywire, build_stimuli
from sinek.data.flywire import Connectome
from sinek.lesion import apl_scaled, scale_edges
from sinek.sim import simulate, firing_rates
from sinek.neuromod import ModulationParams, ModulatedNetwork, simulate_modulated
from compartment_map import build, mbon_rates
from reinforcer_path import active_relays

ap = argparse.ArgumentParser()
ap.add_argument("--apl-scale", type=float, default=5.0); ap.add_argument("--seeds", type=int, default=3)
ap.add_argument("--boost", type=float, default=4.0)
args = ap.parse_args()
base = apl_scaled(load_flywire(), args.apl_scale); cn = build(base, args.boost)
fit = json.load(open("results/modulation_fit.json")); mpar = ModulationParams(kappa=fit["kappa"], eta=max(fit["eta"], 1e-4), alpha_fast=0.0)
stim = {s.name: s for s in build_stimuli(cn)}; cs = stim["odor_DM1"].targets
rows = []
for s in range(args.seeds):
    net0 = ModulatedNetwork(cn, ModulationParams(kappa=0.0, eta=0.0, alpha_fast=0.0)); _, rb = simulate_modulated(net0, 400.0, poisson=cs, poisson_rate=150.0, seed=0)
    net = ModulatedNetwork(cn, mpar); net.set_baseline(rb)
    pre, rb = mbon_rates(simulate_modulated(net, 500.0, poisson=cs, poisson_rate=150.0, seed=10 + 3 * s, rbar=rb)[0], cn), rb
    _, rb = simulate_modulated(net, 1000.0, poisson=cs, poisson_rate=150.0, seed=11 + 3 * s, plastic=True, rbar=rb)
    _, rb = simulate_modulated(net, 400.0, poisson=None, seed=12 + 3 * s, rbar=rb)
    post = mbon_rates(simulate_modulated(net, 500.0, poisson=cs, poisson_rate=150.0, seed=13 + 3 * s, rbar=rb)[0], cn)
    li = ((pre - post) / pre.replace(0, np.nan)).fillna(0.0)
    rows += [{"seed": s, "mbon": m, "pre_hz": float(pre[m]), "post_hz": float(post[m]), "li_unpaired": float(li[m])} for m in pre.index]
d = pd.DataFrame(rows); d.to_csv(f"results/li_noise_apl{args.apl_scale:g}.csv", index=False)
g = d[d.pre_hz >= 2].groupby("mbon")["li_unpaired"].agg(["mean", "std", "max"]).round(2)
print(f"APL x{args.apl_scale:g}: unpaired LI per responding MBON (mean, sd, max over {args.seeds} seeds):"); print(g.to_string())
# input-hop-only bitter route
T = base.select(cell_type__startswith="PPL1"); us = base.select(cell_sub_class="bitter")
A, relays, _ = active_relays(base, us, T)
for k in (8.0, 16.0):
    W = scale_edges(base, A, relays, k); c2 = Connectome(ids=base.ids, W=W, meta=base.meta, name="in-only")
    for name, poi in (("odour", {int(i): 150.0 for i in cs}), ("bitter", {int(i): 150.0 for i in us}), ("odour+bitter", {**{int(i): 150.0 for i in cs}, **{int(i): 150.0 for i in us}})):
        r = firing_rates(simulate(c2.W, 500.0, poisson=poi, seed=0), 100.0)
        print(f"input-hop x{k:g} {name:13s}: PPL1 {r[T].mean():5.1f} Hz, PPL106 {r[base.select(cell_type='PPL106')].mean():5.1f}, PPL101 {r[base.select(cell_type='PPL101')].mean():5.1f}, active {(r>5).sum()}")
