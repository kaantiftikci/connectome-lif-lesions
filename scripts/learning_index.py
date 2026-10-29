"""Learning-index readout under progressive dopamine lesions.

A readout the passive stimulus battery cannot give: associative memory.  The
conditioned stimulus (CS) is odour (ORN_DM1); the unconditioned stimulus (US)
is a natural reward (sugar GRNs) or punishment (bitter GRNs).  Pairing CS+US
with dopamine-gated plasticity on should depress the KC->MBON synapses of the
compartments whose dopaminergic neurons the US recruits.  The learning index
is that depression, measured as (pre - post) / pre of each MBON's odour
response.  Removing the dopaminergic neurons should abolish it -- the direct
test of whether the connectome routes reward/punishment to the right
compartments and whether dopamine loss is readable through behaviour-relevant
plasticity rather than tonic firing.

  diagnose : does sugar drive PAM, does bitter drive PPL1? (one run each)
  curves   : learning index vs lesion fraction for PPL1, PAM, controls

Run:  python scripts/learning_index.py diagnose --apl-scale 5
      python scripts/learning_index.py curves --apl-scale 5 --out results/learning.csv
"""
import argparse, json, sys, time
import multiprocessing as mp
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire, group_indices, build_stimuli      # noqa: E402
from sinek.data.flywire import Connectome                              # noqa: E402
from sinek.lesion import LesionSpec, apply_lesion, apl_scaled          # noqa: E402
from sinek.sim import simulate, firing_rates                           # noqa: E402
from sinek.neuromod import ModulationParams, ModulatedNetwork, simulate_modulated  # noqa: E402

_G = {}


def mbon_rates(rec, cn, t0=200.0):
    r = firing_rates(rec, t0)
    mb = cn.select(cell_type__startswith="MBON")
    return pd.Series(r[mb], index=cn.meta.loc[mb, "cell_type"].astype(str).values).groupby(level=0).mean()


def cmd_diagnose(cn, args):
    """Does the US recruit the expected dopaminergic cluster?"""
    stim = {s.name: s for s in build_stimuli(cn)}
    da = {"PAM": cn.select(cell_type__startswith="PAM"), "PPL1": cn.select(cell_type__startswith="PPL1"),
          "PPL2": cn.select(cell_type__startswith="PPL2"), "PPM1": cn.select(cell_type__startswith="PPM1")}
    for us in ("sugar", "bitter", "water"):
        rec = simulate(cn.W, 500.0, poisson=stim[us].targets, poisson_rate=stim[us].rate_hz, seed=0)
        r = firing_rates(rec, 100.0)
        print(f"{us:7s}:", {k: round(float(r[v].mean()), 1) for k, v in da.items()}, "Hz (DAN cluster mean)")


def _learn_job(a):
    group, frac, seed = a
    cn, mpar = _G["cn"], _G["mpar"]
    cs = _G["cs"]
    W = cn.W if frac == 0 else apply_lesion(cn, _G["groups"], LesionSpec({group: frac}, seed=seed), keep_pattern=True)[0]
    lcn = Connectome(ids=cn.ids, W=W, meta=cn.meta, name=cn.name)
    out = {}
    for us_name, us in _G["us"].items():
        net0 = ModulatedNetwork(lcn, ModulationParams(kappa=0.0, eta=0.0, alpha_fast=0.0))
        _, rb = simulate_modulated(net0, 400.0, poisson=cs, poisson_rate=150.0, seed=0)
        net = ModulatedNetwork(lcn, mpar)
        net.set_baseline(rb)
        pre = mbon_rates(simulate_modulated(net, 500.0, poisson=cs, poisson_rate=150.0, seed=1, rbar=rb)[0], lcn)
        pair = {int(i): 150.0 for i in cs}
        pair.update({int(i): us[1] for i in us[0]})
        _, rb = simulate_modulated(net, 1000.0, poisson=pair, seed=2, plastic=True, rbar=rb)
        _, rb = simulate_modulated(net, 400.0, poisson=None, seed=3, rbar=rb)
        post = mbon_rates(simulate_modulated(net, 500.0, poisson=cs, poisson_rate=150.0, seed=4, rbar=rb)[0], lcn)
        li = ((pre - post) / pre.replace(0, np.nan)).fillna(0.0)
        for m, v in li.items():
            out[f"{us_name}|LI:{m}"] = float(v)
    n_hit = 0 if frac == 0 else sum(len(v) for v in apply_lesion(cn, _G["groups"], LesionSpec({group: frac}, seed=seed), keep_pattern=True)[1].values())
    return group, frac, seed, n_hit, out


def cmd_curves(cn, args):
    fit = json.load(open("results/modulation_fit.json")) if Path("results/modulation_fit.json").exists() else {"kappa": 0.003, "eta": 1e-4}
    mpar = ModulationParams(kappa=fit["kappa"], eta=max(fit["eta"], 1e-4), alpha_fast=0.0)
    print("modulation params:", mpar, flush=True)
    groups = group_indices(cn)
    m = cn.meta
    pool = m.loc[(m["super_class"] == "central") & (~m["cell_class"].isin(["DAN", "Kenyon_Cell"])), "idx"].to_numpy()
    rng = np.random.default_rng(12345)
    for size in args.controls:
        groups[f"RND{size}"] = np.sort(rng.choice(pool, size=size, replace=False))
    stim = {s.name: s for s in build_stimuli(cn)}
    _G.update(cn=cn, mpar=mpar, groups=groups,
              cs=stim["odor_DM1"].targets,
              us={"sugar": (stim["sugar"].targets, 150.0), "bitter": (stim["bitter"].targets, 150.0)})
    jobs = [(g, f, s) for g in (list(args.groups) + [f"RND{s}" for s in args.controls])
            for f in (0.0, 0.5, 1.0) for s in range(args.seeds if f > 0 else 1)]
    rows = []
    t0 = time.time()
    with mp.get_context("fork").Pool(args.procs) as pool_:
        for i, (g, f, s, n_hit, out) in enumerate(pool_.imap_unordered(_learn_job, jobs)):
            rows.extend({"group": g, "fraction": f, "seed": s, "n_lesioned": n_hit, "feature": k, "value": v}
                        for k, v in out.items())
            pd.DataFrame(rows).to_csv(args.out, index=False)
            print(f"{i+1}/{len(jobs)} {g} {f} seed {s} [{time.time()-t0:.0f}s]", flush=True)
    print("wrote", args.out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["diagnose", "curves"])
    ap.add_argument("--apl-scale", type=float, default=5.0)
    ap.add_argument("--groups", nargs="+", default=["PPL1", "PAM"])
    ap.add_argument("--controls", nargs="*", type=int, default=[16, 307])
    ap.add_argument("--seeds", type=int, default=2)
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--out", default="results/learning.csv")
    args = ap.parse_args()
    cn = apl_scaled(load_flywire(), args.apl_scale)
    {"diagnose": cmd_diagnose, "curves": cmd_curves}[args.cmd](cn, args)
