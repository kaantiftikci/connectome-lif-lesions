"""Positive arm 1+2: with the two missing teaching-signal routes supplied, which
compartments learn from natural reinforcers, and how much dopamine loss does
each tolerate?

  reward   : sugar GRN rate -> extrasynaptic drive onto surviving PAM neurons
             (gain g_reward; stands in for octopaminergic signalling)
  punish   : bitter -> PPL1 relay route strengthened x4 (reinforcer_path.py)

Protocol per job (sparse regime, modulation layer with fitted kappa/eta):
  odour test 500 ms -> pairing 1 s (odour + US) -> rest 400 ms -> odour test 500 ms
  learning index per MBON type = (pre - post) / pre.
Lesions: PAM and PPL1 at 0/0.25/0.5/0.75/0.9/1.0 (2 orders), RND307 at 1.0.

Run:  python scripts/compartment_map.py --procs 3 --out results/compartment_map.csv
"""
import argparse, json, sys, time
import multiprocessing as mp
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sinek.data import load_flywire, group_indices, build_stimuli      # noqa: E402
from sinek.data.flywire import Connectome                              # noqa: E402
from sinek.lesion import LesionSpec, apply_lesion, apl_scaled, scale_edges   # noqa: E402
from sinek.sim import firing_rates                                     # noqa: E402
from sinek.neuromod import ModulationParams, ModulatedNetwork, simulate_modulated  # noqa: E402

_G = {}


def mbon_rates(rec, cn, t0=200.0):
    r = firing_rates(rec, t0); mb = cn.select(cell_type__startswith="MBON")
    return pd.Series(r[mb], index=cn.meta.loc[mb, "cell_type"].astype(str).values).groupby(level=0).mean()


def build(cn, boost, procs_note=True):
    """bitter -> PPL1 relay route strengthened (synaptic); reward is added at run time."""
    from reinforcer_path import active_relays
    T = cn.select(cell_type__startswith="PPL1"); us = cn.select(cell_sub_class="bitter")
    A, relays, _ = active_relays(cn, us, T)
    W = scale_edges(cn, A, relays, boost)
    W = scale_edges(Connectome(ids=cn.ids, W=W, meta=cn.meta, name=cn.name), relays, T, boost)
    return Connectome(ids=cn.ids, W=W, meta=cn.meta, name=f"{cn.name}_bitterboost{boost:g}")


def run_protocol(lcn, mpar, cs, us_idx, us_rate, extra):
    net0 = ModulatedNetwork(lcn, ModulationParams(kappa=0.0, eta=0.0, alpha_fast=0.0))
    _, rb = simulate_modulated(net0, 400.0, poisson=cs, poisson_rate=150.0, seed=0)
    net = ModulatedNetwork(lcn, mpar); net.set_baseline(rb)
    if extra is not None:
        net.add_extrasynaptic(*extra)
    pre_rec, _ = simulate_modulated(net, 500.0, poisson=cs, poisson_rate=150.0, seed=1, rbar=rb)
    pair = {int(i): 150.0 for i in cs}; pair.update({int(i): us_rate for i in us_idx})
    pair_rec, rb = simulate_modulated(net, 1000.0, poisson=pair, seed=2, plastic=True, rbar=rb)
    _, rb = simulate_modulated(net, 400.0, poisson=None, seed=3, rbar=rb)
    post_rec, _ = simulate_modulated(net, 500.0, poisson=cs, poisson_rate=150.0, seed=4, rbar=rb)
    rp = firing_rates(pair_rec, 100.0)
    return mbon_rates(pre_rec, lcn), mbon_rates(post_rec, lcn), rp


def _job(a):
    us_name, group, frac, seed = a
    cn, mpar = _G["cn"], _G["mpar"]
    W, hit = (cn.W, {}) if frac == 0 else apply_lesion(cn, _G["groups"], LesionSpec({group: frac}, seed=seed), keep_pattern=True)
    lcn = Connectome(ids=cn.ids, W=W, meta=cn.meta, name=cn.name)
    us_idx = _G["us"][us_name]
    extra = (_G["us"]["sugar"], _G["pam"], _G["g_reward"]) if us_name == "sugar" else None
    pre, post, rp = run_protocol(lcn, mpar, _G["cs"], us_idx, 150.0, extra)
    li = ((pre - post) / pre.replace(0, np.nan)).fillna(0.0)
    n_hit = sum(len(v) for v in hit.values())
    dan = {"pam_hz": float(rp[_G["pam"]].mean()), "ppl1_hz": float(rp[_G["ppl1"]].mean())}
    return us_name, group, frac, seed, n_hit, dan, {m: (float(li[m]), float(pre[m]), float(post[m])) for m in li.index}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apl-scale", type=float, default=5.0)
    ap.add_argument("--boost", type=float, default=4.0)
    ap.add_argument("--g-reward", type=float, default=0.5, help="extrasynaptic gain: Hz added to each PAM per Hz of mean sugar-GRN rate")
    ap.add_argument("--fractions", nargs="*", type=float, default=[0.0, 0.25, 0.5, 0.75, 0.9, 1.0])
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--only", nargs="*", default=None, help="restrict US, e.g. sugar")
    ap.add_argument("--out", default="results/compartment_map.csv")
    args = ap.parse_args()
    cn = build(apl_scaled(load_flywire(), args.apl_scale), args.boost)
    fit = json.load(open("results/modulation_fit.json")) if Path("results/modulation_fit.json").exists() else {"kappa": 0.003, "eta": 1e-4}
    mpar = ModulationParams(kappa=fit["kappa"], eta=max(fit["eta"], 1e-4), alpha_fast=0.0)
    groups = group_indices(cn); m = cn.meta
    pool = m.loc[(m["super_class"] == "central") & (~m["cell_class"].isin(["DAN", "Kenyon_Cell"])), "idx"].to_numpy()
    groups["RND307"] = np.sort(np.random.default_rng(12345).choice(pool, size=307, replace=False))
    stim = {s.name: s for s in build_stimuli(cn)}
    _G.update(cn=cn, mpar=mpar, groups=groups, cs=stim["odor_DM1"].targets, g_reward=args.g_reward,
              us={"sugar": stim["sugar"].targets, "bitter": stim["bitter"].targets},
              pam=cn.select(cell_type__startswith="PAM"), ppl1=cn.select(cell_type__startswith="PPL1"))
    uses = args.only or ["sugar", "bitter"]
    jobs = [(u, "PAM", 0.0, 0) for u in uses]
    jobs += [(u, g, f, s) for u in uses for g in ("PAM", "PPL1") for f in args.fractions if f > 0 for s in range(args.seeds)]
    jobs += [(u, "RND307", 1.0, 0) for u in uses]
    rows, t0 = [], time.time()
    with mp.get_context("fork").Pool(args.procs) as pool_:
        for i, (u, g, f, s, n_hit, dan, out) in enumerate(pool_.imap_unordered(_job, jobs)):
            rows.extend({"us": u, "group": g, "fraction": f, "seed": s, "n_lesioned": n_hit, **dan, "mbon": k, "li": v[0], "pre_hz": v[1], "post_hz": v[2]} for k, v in out.items())
            pd.DataFrame(rows).to_csv(args.out, index=False)
            print(f"{i+1}/{len(jobs)} {u} {g} {f} seed {s}: pairing PAM {dan['pam_hz']:.1f} Hz, PPL1 {dan['ppl1_hz']:.1f} Hz [{time.time()-t0:.0f}s]", flush=True)
    print("wrote", args.out)
