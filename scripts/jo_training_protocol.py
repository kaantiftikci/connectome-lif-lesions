"""Jo (2026)-style training: odour paired with DIRECT drive of PAM neurons at
100 Hz (the teaching signal bypasses the reinforcer pathway), dopamine-gated
depression on, learning index per MBON; under progressive PAM loss and a
random control.  A positive-control learning curve that the pathway problem
cannot block.  Sparse regime.

Run:  python scripts/jo_training_protocol.py --procs 3
"""
import argparse, json, sys, time
import multiprocessing as mp
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire, group_indices, build_stimuli      # noqa: E402
from sinek.data.flywire import Connectome                              # noqa: E402
from sinek.lesion import LesionSpec, apply_lesion, apl_scaled          # noqa: E402
from sinek.sim import firing_rates                                     # noqa: E402
from sinek.neuromod import ModulationParams, ModulatedNetwork, simulate_modulated  # noqa: E402

_G = {}


def mbon_rates(rec, cn, t0=200.0):
    r = firing_rates(rec, t0); mb = cn.select(cell_type__startswith="MBON")
    return pd.Series(r[mb], index=cn.meta.loc[mb, "cell_type"].astype(str).values).groupby(level=0).mean()


def _job(a):
    group, frac, seed = a
    cn, mpar, cs = _G["cn"], _G["mpar"], _G["cs"]
    W, hit = (cn.W, {}) if frac == 0 else apply_lesion(cn, _G["groups"], LesionSpec({group: frac}, seed=seed), keep_pattern=True)
    lcn = Connectome(ids=cn.ids, W=W, meta=cn.meta, name=cn.name)
    removed = set(int(i) for v in hit.values() for i in v)
    pam_drive = {int(i): 100.0 for i in _G["pam"] if int(i) not in removed}   # removed PAMs cannot be driven
    net0 = ModulatedNetwork(lcn, ModulationParams(kappa=0.0, eta=0.0, alpha_fast=0.0))
    _, rb = simulate_modulated(net0, 400.0, poisson=cs, poisson_rate=150.0, seed=0)
    net = ModulatedNetwork(lcn, mpar); net.set_baseline(rb)
    pre = mbon_rates(simulate_modulated(net, 500.0, poisson=cs, poisson_rate=150.0, seed=1, rbar=rb)[0], lcn)
    pair = {int(i): 150.0 for i in cs}; pair.update(pam_drive)
    _, rb = simulate_modulated(net, 1000.0, poisson=pair, seed=2, plastic=True, rbar=rb)
    _, rb = simulate_modulated(net, 400.0, poisson=None, seed=3, rbar=rb)
    post = mbon_rates(simulate_modulated(net, 500.0, poisson=cs, poisson_rate=150.0, seed=4, rbar=rb)[0], lcn)
    li = ((pre - post) / pre.replace(0, np.nan)).fillna(0.0)
    return group, frac, seed, len(removed), {m: (float(li[m]), float(pre[m]), float(post[m])) for m in li.index}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--apl-scale", type=float, default=5.0)
    ap.add_argument("--fractions", nargs="*", type=float, default=[0.0, 0.25, 0.5, 0.75, 1.0])
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--out", default="results/jo_training.csv")
    args = ap.parse_args()
    cn = apl_scaled(load_flywire(), args.apl_scale)
    fit = json.load(open("results/modulation_fit.json")) if Path("results/modulation_fit.json").exists() else {"kappa": 0.003, "eta": 1e-4}
    mpar = ModulationParams(kappa=fit["kappa"], eta=max(fit["eta"], 1e-4), alpha_fast=0.0)
    groups = group_indices(cn); m = cn.meta
    pool = m.loc[(m["super_class"] == "central") & (~m["cell_class"].isin(["DAN", "Kenyon_Cell"])), "idx"].to_numpy()
    groups["RND307"] = np.sort(np.random.default_rng(12345).choice(pool, size=307, replace=False))
    stim = {s.name: s for s in build_stimuli(cn)}
    _G.update(cn=cn, mpar=mpar, groups=groups, cs=stim["odor_DM1"].targets, pam=cn.select(cell_type__startswith="PAM"))
    jobs = [(g, f, s) for g in ("PAM", "RND307") for f in args.fractions for s in (range(args.seeds) if f > 0 else [0])]
    rows, t0 = [], time.time()
    with mp.get_context("fork").Pool(args.procs) as pool_:
        for i, (g, f, s, n_hit, out) in enumerate(pool_.imap_unordered(_job, jobs)):
            rows.extend({"group": g, "fraction": f, "seed": s, "n_lesioned": n_hit, "mbon": k, "li": v[0], "pre_hz": v[1], "post_hz": v[2]} for k, v in out.items())
            pd.DataFrame(rows).to_csv(args.out, index=False)
            print(f"{i+1}/{len(jobs)} {g} {f} seed {s} [{time.time()-t0:.0f}s]", flush=True)
    df = pd.DataFrame(rows)
    top = df[(df.group == "PAM") & (df.fraction == 0)].sort_values("li", ascending=False).head(6)
    print("\nintact: most depressed MBONs (li, pre Hz, post Hz):\n", top[["mbon", "li", "pre_hz", "post_hz"]].round(2).to_string(index=False))
    for mb_ in top.mbon.head(3):
        print(f"\n{mb_}:"); print(df[df.mbon == mb_].pivot_table(index=["group", "fraction"], values=["li", "pre_hz"], aggfunc="mean").round(2).to_string())
