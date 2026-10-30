"""Parkinson-model predictions: how the pattern of dopaminergic loss and the
choice of readout change when a deficit becomes detectable.

Loss patterns within PAM (appetitive, sugar protocol) and PPL1 (aversive,
bitter protocol):
  random            two random orders (LesionSpec seeds 0, 1)
  vulnerable_first  neurons with the largest synaptic load go first
                    (selective-vulnerability analogue of alpha-synuclein models)
  resistant_first   the reverse order
Readouts per job: learning index per MBON, passive odour response per MBON
(pre-pairing), and the locomotor descending-neuron rates during the odour
test (left/right means of DNp09, DNa01-03, DNb01-02, DNg13).

Run:  python scripts/pd_patterns.py --procs 3 --out results/pd_patterns.csv
"""
import argparse, json, sys, time
import multiprocessing as mp
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sinek.data import load_flywire, build_stimuli                     # noqa: E402
from sinek.data.flywire import Connectome                              # noqa: E402
from sinek.lesion import apl_scaled                                    # noqa: E402
from sinek.sim import firing_rates                                     # noqa: E402
from sinek.neuromod import ModulationParams, ModulatedNetwork, simulate_modulated  # noqa: E402
from sinek.embodied.drive import descending_sides, LOCOMOTOR_DN_TYPES  # noqa: E402
from compartment_map import build, mbon_rates                          # noqa: E402

_G = {}


def contacts(cn, idx):
    W = cn.W; c = (abs(W) / 0.275)
    return np.asarray(c[idx].sum(1)).ravel() + np.asarray(c[:, idx].sum(0)).ravel()


def remove(cn, idx):
    W = cn.W.copy(); dead = np.zeros(cn.n, bool); dead[idx] = True
    row_of = np.repeat(np.arange(cn.n), np.diff(W.indptr))
    W.data[dead[row_of] | dead[W.indices]] = 0.0
    return W


def _job(a):
    us_name, group, order, seed, frac = a
    cn, mpar = _G["cn"], _G["mpar"]; g = _G["groups"][group]
    k = int(round(frac * g.size))
    if order == "random":
        idx = np.random.default_rng(seed).permutation(g)[:k]
    elif order == "vulnerable_first":
        idx = g[np.argsort(_G["load"][group])[::-1]][:k]
    else:
        idx = g[np.argsort(_G["load"][group])][:k]
    lcn = Connectome(ids=cn.ids, W=remove(cn, idx) if k else cn.W, meta=cn.meta, name=cn.name)
    cs = _G["cs"]; us_idx = _G["us"][us_name]
    net0 = ModulatedNetwork(lcn, ModulationParams(kappa=0.0, eta=0.0, alpha_fast=0.0))
    _, rb = simulate_modulated(net0, 400.0, poisson=cs, poisson_rate=150.0, seed=0)
    net = ModulatedNetwork(lcn, mpar); net.set_baseline(rb)
    if us_name == "sugar":
        net.add_extrasynaptic(_G["us"]["sugar"], _G["pam"], _G["g_reward"])
    pre_rec, _ = simulate_modulated(net, 500.0, poisson=cs, poisson_rate=150.0, seed=1, rbar=rb)
    pair = {int(i): 150.0 for i in cs}; pair.update({int(i): 150.0 for i in us_idx})
    _, rb = simulate_modulated(net, 1000.0, poisson=pair, seed=2, plastic=True, rbar=rb)
    _, rb = simulate_modulated(net, 400.0, poisson=None, seed=3, rbar=rb)
    post_rec, _ = simulate_modulated(net, 500.0, poisson=cs, poisson_rate=150.0, seed=4, rbar=rb)
    pre, post = mbon_rates(pre_rec, lcn), mbon_rates(post_rec, lcn)
    li = ((pre - post) / pre.replace(0, np.nan)).fillna(0.0)
    r = firing_rates(pre_rec, 200.0); dn = _G["dn"]
    extra = {"dn_left_hz": float(r[dn["left"]].mean()), "dn_right_hz": float(r[dn["right"]].mean()),
             "mbon_mean_hz": float(pre.mean()), "n_removed": int(k)}
    return us_name, group, order, seed, frac, extra, {m_: (float(li[m_]), float(pre[m_]), float(post[m_])) for m_ in li.index}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apl-scale", type=float, default=5.0)
    ap.add_argument("--boost", type=float, default=4.0)
    ap.add_argument("--g-reward", type=float, default=0.5)
    ap.add_argument("--fractions", nargs="*", type=float, default=[0.25, 0.5, 0.75, 0.9, 1.0])
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--seeds", type=int, default=2, help="random orders per fraction")
    ap.add_argument("--out", default="results/pd_patterns.csv")
    args = ap.parse_args()
    cn = build(apl_scaled(load_flywire(), args.apl_scale), args.boost)
    fit = json.load(open("results/modulation_fit.json")) if Path("results/modulation_fit.json").exists() else {"kappa": 0.003, "eta": 1e-4}
    _G["mpar"] = ModulationParams(kappa=fit["kappa"], eta=max(fit["eta"], 1e-4), alpha_fast=0.0)
    groups = {"PAM": cn.select(cell_type__startswith="PAM"), "PPL1": cn.select(cell_type__startswith="PPL1")}
    stim = {s.name: s for s in build_stimuli(cn)}
    _G.update(cn=cn, groups=groups, load={k: contacts(cn, v) for k, v in groups.items()}, cs=stim["odor_DM1"].targets,
              us={"sugar": stim["sugar"].targets, "bitter": stim["bitter"].targets}, pam=groups["PAM"], g_reward=args.g_reward,
              dn=descending_sides(cn, LOCOMOTOR_DN_TYPES))
    for k, v in groups.items():
        L = _G["load"][k]; print(f"{k}: {v.size} neurons, synaptic load median {np.median(L):.0f}, max {L.max():.0f}", flush=True)
    jobs = [("sugar", "PAM", "random", 0, 0.0), ("bitter", "PPL1", "random", 0, 0.0)]
    for us, g in (("sugar", "PAM"), ("bitter", "PPL1")):
        for f in args.fractions:
            jobs += [(us, g, "random", sd, f) for sd in range(args.seeds)] + [(us, g, "vulnerable_first", 0, f), (us, g, "resistant_first", 0, f)]
    rows, t0 = [], time.time()
    with mp.get_context("fork").Pool(args.procs) as pool:
        for i, (us, g, order, seed, f, extra, out) in enumerate(pool.imap_unordered(_job, jobs)):
            rows.extend({"us": us, "group": g, "order": order, "seed": seed, "fraction": f, **extra, "mbon": k, "li": v[0], "pre_hz": v[1], "post_hz": v[2]} for k, v in out.items())
            pd.DataFrame(rows).to_csv(args.out, index=False)
            print(f"{i+1}/{len(jobs)} {us} {g} {order} seed {seed} frac {f}: removed {extra['n_removed']}, DN L/R {extra['dn_left_hz']:.1f}/{extra['dn_right_hz']:.1f} Hz [{time.time()-t0:.0f}s]", flush=True)
    print("wrote", args.out)
