"""Item 4: does a different neuron model change the two central claims?
Spike-frequency adaptation (threshold rises by delta per spike, decays with
tau; Jo 2026 used tau = 1 s, delta = 1 mV) added to the LIF.

  (a) attractor: odour at APL x1 with adaptation -> KC fraction, active count
  (b) sparse regime (APL x5) with adaptation: noise floor (2 seeds), PPL1 100 %, RND16 100 %

Run:  python scripts/adaptation_check.py --procs 3
"""
import argparse, sys, time
import multiprocessing as mp
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire, build_stimuli, readout_groups, group_indices
from sinek.lesion import apl_scaled, LesionSpec, apply_lesion
from sinek.sim import simulate, firing_rates, LIFParams
from sinek.readout import phenotype_vector

_G = {}


def _job(a):
    apl, delta, what, seed = a
    cn = _G["cn"][apl]; p = LIFParams(tau_adapt=1000.0, delta_adapt=delta) if delta > 0 else LIFParams()
    if what == "odor":
        s = _G["stim"]["odor_DM1"]
        r = firing_rates(simulate(cn.W, 1000.0, poisson=s.targets, poisson_rate=s.rate_hz, seed=seed, params=p), 100.0)
        r_late = firing_rates(simulate(cn.W, 1000.0, poisson=s.targets, poisson_rate=s.rate_hz, seed=seed, params=p), 600.0)
        return {"apl": apl, "delta": delta, "what": what, "seed": seed, "kc_frac": float((r[_G["kc"]] > 5).mean()), "kc_frac_late": float((r_late[_G["kc"]] > 5).mean()),
                "n_active": int((r > 5).sum()), "mbon_hz": float(r[_G["mbon"]].mean()), "ppl1_hz": float(r[_G["ppl1"]].mean())}
    W = cn.W if what == "intact" else apply_lesion(cn, _G["groups"], LesionSpec({what: 1.0}, seed=0), keep_pattern=True)[0]
    x = phenotype_vector(W, list(_G["stim"].values()), _G["readouts"], duration=500.0, seed=100 + seed, params=p)
    return {"apl": apl, "delta": delta, "what": what, "seed": seed, "x": x.tolist()}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--procs", type=int, default=3); ap.add_argument("--out", default="results/adaptation_check.csv")
    args = ap.parse_args()
    base = load_flywire(); _G["cn"] = {1.0: base, 5.0: apl_scaled(base, 5.0)}
    _G["stim"] = {s.name: s for s in build_stimuli(base)}; _G["readouts"] = readout_groups(base)
    _G["kc"] = base.select(cell_class="Kenyon_Cell"); _G["mbon"] = base.select(cell_type__startswith="MBON"); _G["ppl1"] = base.select(cell_type__startswith="PPL1")
    groups = group_indices(base); m = base.meta
    pool = m.loc[(m["super_class"] == "central") & (~m["cell_class"].isin(["DAN", "Kenyon_Cell"])), "idx"].to_numpy()
    groups["RND16"] = np.sort(np.random.default_rng(12345).choice(pool, size=16, replace=False)); _G["groups"] = groups
    jobs = [(1.0, d, "odor", 0) for d in (0.0, 1.0, 2.0, 4.0)] + [(5.0, 1.0, "odor", 0)]
    jobs += [(5.0, 1.0, "intact", 0), (5.0, 1.0, "intact", 1), (5.0, 1.0, "PPL1", 0), (5.0, 1.0, "RND16", 0), (5.0, 1.0, "PAM", 0)]
    rows, t0 = [], time.time()
    with mp.get_context("fork").Pool(args.procs) as p:
        for r in p.imap_unordered(_job, jobs):
            rows.append(r); print({k: v for k, v in r.items() if k != "x"}, f"[{time.time()-t0:.0f}s]", flush=True)
    pd.DataFrame(rows).to_csv(args.out, index=False)
    X = {(r["what"], r["seed"]): np.array(r["x"]) for r in rows if "x" in r}
    floor = np.linalg.norm(X[("intact", 0)] - X[("intact", 1)]); b = (X[("intact", 0)] + X[("intact", 1)]) / 2
    print(f"\nAPL x5 + adaptation (tau 1 s, delta 1 mV): noise floor {floor:.2f}, PPL1 100% {np.linalg.norm(X[('PPL1',0)]-b):.2f}, PAM 100% {np.linalg.norm(X[('PAM',0)]-b):.2f}, RND16 100% {np.linalg.norm(X[('RND16',0)]-b):.2f}")
