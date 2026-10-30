"""Parameter sensitivity of the positive/Parkinson arm.

For each parameter set (reward gain g_reward, gate kappa, plasticity eta,
bitter relay boost) measure: intact appetitive learning per MBON, learning
after 75 % and 90 % random PAM loss (reserve), retention of a memory stored
before a 75 % loss, and unpaired depression under 30 Hz tonic dopamine with
a non-adapted gate (the L-DOPA specificity signature).

Run:  python scripts/pd_sensitivity.py --procs 3
"""
import argparse, json, sys, time
import multiprocessing as mp
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1])); sys.path.insert(0, str(Path(__file__).resolve().parent))
from sinek.data import load_flywire, build_stimuli
from sinek.data.flywire import Connectome
from sinek.lesion import apl_scaled
from sinek.neuromod import ModulationParams
import pd_experiments as pe
from compartment_map import build
from pd_patterns import remove

_G = pe._G


def _job(a):
    pset, what = a
    _G["mpar"] = ModulationParams(kappa=pset["kappa"], eta=pset["eta"], alpha_fast=0.0); _G["g_reward"] = pset["g_reward"]
    cn = _G["cn"]
    if what == "intact":
        rows = pe.job_comp((0.0, 0.0, 0)) if False else None
        net, rb = pe._net(cn, True); pre, rb = pe._test(net, rb, 1); rb = pe._pair(net, rb, "sugar"); post, _ = pe._test(net, rb, 4)
        li = ((pre - post) / pre.replace(0, np.nan)).fillna(0.0)
        out = {m: float(li[m]) for m in pre.index}; extra = {"pre_MBON09": float(pre.get("MBON09", 0))}
    elif what in ("pam75", "pam90"):
        f = 0.75 if what == "pam75" else 0.9
        idx = pe._random_subset("pam", f, 0); lcn = Connectome(ids=cn.ids, W=remove(cn, idx), meta=cn.meta, name=cn.name)
        net, rb = pe._net(lcn, True); pre, rb = pe._test(net, rb, 1); rb = pe._pair(net, rb, "sugar"); post, _ = pe._test(net, rb, 4)
        li = ((pre - post) / pre.replace(0, np.nan)).fillna(0.0); out = {m: float(li[m]) for m in pre.index}; extra = {}
    elif what == "retention75":
        r = pe.job_retention(("sugar", "pam", 0.75, 0)); out = {x["mbon"]: x["li_after_lesion"] for x in r}; extra = {}
    else:  # ldopa30 non-adapted, intact, unpaired
        r = pe.job_ldopa((30.0, False, 0.0, 0)); out = {x["mbon"]: x["li_unpaired"] for x in r if x["us"] == "sugar"}; extra = {}
    return pset["name"], what, extra, out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--procs", type=int, default=3); ap.add_argument("--apl-scale", type=float, default=5.0)
    ap.add_argument("--out", default="results/pd_sensitivity.csv"); args = ap.parse_args()
    fit = json.load(open("results/modulation_fit.json")); k0, e0 = fit["kappa"], max(fit["eta"], 1e-4)
    psets = [{"name": "base", "g_reward": 0.5, "kappa": k0, "eta": e0, "boost": 4.0},
             {"name": "g_reward x0.5", "g_reward": 0.25, "kappa": k0, "eta": e0, "boost": 4.0},
             {"name": "g_reward x2", "g_reward": 1.0, "kappa": k0, "eta": e0, "boost": 4.0},
             {"name": "kappa x0.5", "g_reward": 0.5, "kappa": k0 / 2, "eta": e0, "boost": 4.0},
             {"name": "kappa x2", "g_reward": 0.5, "kappa": k0 * 2, "eta": e0, "boost": 4.0},
             {"name": "eta x0.5", "g_reward": 0.5, "kappa": k0, "eta": e0 / 2, "boost": 4.0},
             {"name": "eta x2", "g_reward": 0.5, "kappa": k0, "eta": e0 * 2, "boost": 4.0},
             {"name": "no bitter boost", "g_reward": 0.5, "kappa": k0, "eta": e0, "boost": 1.0}]
    base = apl_scaled(load_flywire(), args.apl_scale)
    cns = {4.0: build(base, 4.0), 1.0: base}
    stim = {s.name: s for s in build_stimuli(base)}
    _G.update(cs=stim["odor_DM1"].targets, us={"sugar": stim["sugar"].targets, "bitter": stim["bitter"].targets},
              pam=base.select(cell_type__startswith="PAM"), ppl1=base.select(cell_type__startswith="PPL1"))
    _G["dans"] = np.concatenate([_G["pam"], _G["ppl1"]])
    rows, t0 = [], time.time()
    for boost, cn in cns.items():
        _G["cn"] = cn
        jobs = [(p, w) for p in psets if p["boost"] == boost for w in ("intact", "pam75", "pam90", "retention75", "ldopa30")]
        if not jobs:
            continue
        with mp.get_context("fork").Pool(args.procs) as pool:
            for i, (name, what, extra, out) in enumerate(pool.imap_unordered(_job, jobs)):
                rows += [{"pset": name, "what": what, **extra, "mbon": m, "li": v} for m, v in out.items()]
                pd.DataFrame(rows).to_csv(args.out, index=False); print(f"{name} {what} done [{time.time()-t0:.0f}s]", flush=True)
    d = pd.DataFrame(rows)
    print("\n== MBON09 (and MBON33) learning index by parameter set ==")
    print(d[d.mbon.isin(["MBON09", "MBON33"])].pivot_table(index=["mbon", "pset"], columns="what", values="li").round(2).to_string())
    print("\n== which MBONs learn intact (LI >= 0.3) per set ==")
    for name, g in d[d.what == "intact"].groupby("pset"):
        print(f"  {name:16s}:", ", ".join(f"{m} {v:.2f}" for m, v in g[g.li >= 0.3].sort_values('li', ascending=False)[['mbon', 'li']].itertuples(index=False)))
