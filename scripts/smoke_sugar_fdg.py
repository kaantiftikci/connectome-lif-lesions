"""Validation smoke test: activate sugar GRNs, check the feeding command neuron
Fdg fires (Shiu et al. 2024, Fig. 1-2).  Also reports wall time so the
lesion-sweep budget can be planned.

Run:  python scripts/smoke_sugar_fdg.py [--duration 500]
"""
import argparse
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire, stimulus_indices                      # noqa: E402
from sinek.data.pickle_text import read_name_to_ids                       # noqa: E402
from sinek.sim import simulate, firing_rates                               # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--duration", type=float, default=500.0)
ap.add_argument("--rate", type=float, default=150.0)
args = ap.parse_args()

t0 = time.time()
cn = load_flywire()
print(f"loaded {cn.name}: {cn.n} neurons, {cn.W.nnz} connections in {time.time()-t0:.1f}s")

stim = stimulus_indices(cn)
sugar = stim["sugar"]
sez = read_name_to_ids("data/raw/sez_neurons.pickle")
fdg = cn.index_of(sez["Fdg"])
print(f"sugar GRNs: {len(sugar)}  Fdg: {len(fdg)}")

t0 = time.time()
rec = simulate(cn.W, args.duration, poisson=sugar, poisson_rate=args.rate, seed=0)
dt = time.time() - t0
print(f"simulated {args.duration:.0f} ms in {dt:.1f}s  ({rec.times.size} spikes, "
      f"{np.unique(rec.ids).size} neurons active)")
r = firing_rates(rec, t_start=100.0)
print(f"Fdg rates (Hz): {np.round(r[fdg], 1).tolist()}")

top = np.argsort(r)[::-1][:15]
m = cn.meta
print("top responders (excluding driven GRNs):")
shown = 0
for i in top:
    if i in set(sugar):
        continue
    print(f"  {r[i]:7.1f} Hz  idx={i}  {m.loc[i,'cell_type']}  {m.loc[i,'cell_class']}  {m.loc[i,'super_class']}")
    shown += 1
    if shown >= 10:
        break
dn = cn.select(super_class="descending")
print(f"descending neurons active: {(r[dn] > 0).sum()} / {len(dn)}")
