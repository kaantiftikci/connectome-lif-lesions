"""Four Parkinson-model experiments on the modulation layer (sparse regime,
reward term for sugar, x4 relay route for bitter; see compartment_map.py).

  retention     train intact, THEN remove dopaminergic neurons, test: is the
                stored memory kept while new acquisition (compartment_map.py)
                is lost?
  ldopa         tonic extrasynaptic dopamine on all surviving DANs, with the
                gate either adapted to it (baseline measured with it) or not:
                does it restore learning after 75% PAM loss, and does it
                impair intact compartments (overdose)?
  compensation  surviving PAM neurons fire (1-f)^-alpha x more after a loss
                of fraction f (alpha = 0 none, 0.5 partial, 1 full): how far
                does the reserve threshold move?

Run:  python scripts/pd_experiments.py retention|ldopa|compensation --procs 3
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
from sinek.neuromod import ModulationParams, ModulatedNetwork, simulate_modulated  # noqa: E402
from compartment_map import build, mbon_rates                          # noqa: E402

_G = {}


def _net(lcn, with_reward, tonic=None, tonic_adapted=True, comp=None):
    """baseline (gain off), then the modulated network with the requested extras"""
    cs = _G["cs"]
    net0 = ModulatedNetwork(lcn, ModulationParams(kappa=0.0, eta=0.0, alpha_fast=0.0))
    if tonic and tonic_adapted:
        net0.add_tonic(_G["dans"], tonic)
    _, rb = simulate_modulated(net0, 400.0, poisson=cs, poisson_rate=150.0, seed=0)
    net = ModulatedNetwork(lcn, _G["mpar"]); net.set_baseline(rb)
    if with_reward:
        net.add_extrasynaptic(_G["us"]["sugar"], _G["pam"], _G["g_reward"])
    if tonic:
        net.add_tonic(_G["dans"], tonic)
    if comp:
        net.set_compensation(_G["pam"], comp)
    return net, rb


def _pair(net, rb, us_name):
    cs = _G["cs"]; pair = {int(i): 150.0 for i in cs}; pair.update({int(i): 150.0 for i in _G["us"][us_name]})
    _, rb = simulate_modulated(net, 1000.0, poisson=pair, seed=2, plastic=True, rbar=rb)
    _, rb = simulate_modulated(net, 400.0, poisson=None, seed=3, rbar=rb)
    return rb


def _test(net, rb, seed):
    rec, rb2 = simulate_modulated(net, 500.0, poisson=_G["cs"], poisson_rate=150.0, seed=seed, rbar=rb)
    return mbon_rates(rec, net.cn), rb2


def _random_subset(group, frac, seed):
    g = _G[group]; k = int(round(frac * g.size))
    return np.random.default_rng(seed).permutation(g)[:k]


def job_retention(a):
    us_name, group, frac, seed = a
    cn = _G["cn"]; net, rb = _net(cn, us_name == "sugar")
    pre, rb = _test(net, rb, 1)
    rb = _pair(net, rb, us_name)
    post1, rb = _test(net, rb, 4)                      # memory in the intact brain
    idx = _random_subset(group, frac, seed)
    net.remove_neurons(idx)                            # lesion AFTER training
    post2, rb = _test(net, rb, 5)                      # retention test
    li1 = ((pre - post1) / pre.replace(0, np.nan)).fillna(0.0)
    li2 = ((pre - post2) / pre.replace(0, np.nan)).fillna(0.0)
    return [{"exp": "retention", "us": us_name, "group": group, "fraction": frac, "seed": seed, "mbon": m_, "pre_hz": float(pre[m_]),
             "li_before_lesion": float(li1[m_]), "li_after_lesion": float(li2[m_]), "post_after_hz": float(post2[m_])} for m_ in pre.index]


def job_ldopa(a):
    tonic, adapted, frac, seed = a
    cn = _G["cn"]
    idx = _random_subset("pam", frac, seed) if frac > 0 else np.empty(0, int)
    W = cn.W
    if idx.size:
        from pd_patterns import remove
        W = remove(cn, idx)
    lcn = Connectome(ids=cn.ids, W=W, meta=cn.meta, name=cn.name)
    rows = []
    for us_name in ("sugar", "bitter"):
        net, rb = _net(lcn, us_name == "sugar", tonic=tonic or None, tonic_adapted=adapted)
        pre, rb = _test(net, rb, 1)
        # unpaired control: odour alone for 1 s with plasticity on (does tonic dopamine depress without pairing?)
        _, rb_u = simulate_modulated(net, 1000.0, poisson=_G["cs"], poisson_rate=150.0, seed=2, plastic=True, rbar=rb)
        unp, _ = _test(net, rb_u, 4)
        net, rb = _net(lcn, us_name == "sugar", tonic=tonic or None, tonic_adapted=adapted)
        pre2, rb = _test(net, rb, 1)
        rb = _pair(net, rb, us_name); post, _ = _test(net, rb, 4)
        li = ((pre2 - post) / pre2.replace(0, np.nan)).fillna(0.0)
        li_unp = ((pre - unp) / pre.replace(0, np.nan)).fillna(0.0)
        rows += [{"exp": "ldopa", "tonic_hz": tonic, "adapted": adapted, "pam_fraction_lost": frac, "seed": seed, "us": us_name, "mbon": m_,
                  "pre_hz": float(pre2[m_]), "li_paired": float(li[m_]), "li_unpaired": float(li_unp[m_])} for m_ in pre.index]
    return rows


def job_comp(a):
    alpha, frac, seed = a
    cn = _G["cn"]
    from pd_patterns import remove
    idx = _random_subset("pam", frac, seed)
    lcn = Connectome(ids=cn.ids, W=remove(cn, idx) if idx.size else cn.W, meta=cn.meta, name=cn.name)
    factor = (1.0 - frac) ** (-alpha) if frac < 1 else 1.0
    net, rb = _net(lcn, True, comp=factor if alpha > 0 else None)
    pre, rb = _test(net, rb, 1); rb = _pair(net, rb, "sugar"); post, _ = _test(net, rb, 4)
    li = ((pre - post) / pre.replace(0, np.nan)).fillna(0.0)
    return [{"exp": "compensation", "alpha": alpha, "factor": factor, "fraction": frac, "seed": seed, "mbon": m_, "pre_hz": float(pre[m_]), "li": float(li[m_])} for m_ in pre.index]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["retention", "ldopa", "compensation"])
    ap.add_argument("--apl-scale", type=float, default=5.0); ap.add_argument("--boost", type=float, default=4.0)
    ap.add_argument("--g-reward", type=float, default=0.5); ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    cn = build(apl_scaled(load_flywire(), args.apl_scale), args.boost)
    fit = json.load(open("results/modulation_fit.json")) if Path("results/modulation_fit.json").exists() else {"kappa": 0.003, "eta": 1e-4}
    stim = {s.name: s for s in build_stimuli(cn)}
    _G.update(cn=cn, mpar=ModulationParams(kappa=fit["kappa"], eta=max(fit["eta"], 1e-4), alpha_fast=0.0), g_reward=args.g_reward,
              cs=stim["odor_DM1"].targets, us={"sugar": stim["sugar"].targets, "bitter": stim["bitter"].targets},
              pam=cn.select(cell_type__startswith="PAM"), ppl1=cn.select(cell_type__startswith="PPL1"))
    _G["dans"] = np.concatenate([_G["pam"], _G["ppl1"]])
    if args.cmd == "retention":
        jobs = [(u, g, f, s) for u, g in (("sugar", "pam"), ("bitter", "ppl1")) for f in (0.5, 0.75, 1.0) for s in (0, 1)]; fn = job_retention
    elif args.cmd == "ldopa":
        jobs = [(t, ad, f, 0) for t in (0.0, 10.0, 30.0, 60.0) for ad in (True, False) for f in (0.0, 0.75)]; fn = job_ldopa
    else:
        jobs = [(al, f, 0) for al in (0.0, 0.5, 1.0) for f in (0.5, 0.75, 0.9)]; fn = job_comp
    out = args.out or f"results/pd_{args.cmd}.csv"
    rows, t0 = [], time.time()
    with mp.get_context("fork").Pool(args.procs) as pool:
        for i, r in enumerate(pool.imap_unordered(fn, jobs)):
            rows += r; pd.DataFrame(rows).to_csv(out, index=False); print(f"{i+1}/{len(jobs)} [{time.time()-t0:.0f}s]", flush=True)
    print("wrote", out)
