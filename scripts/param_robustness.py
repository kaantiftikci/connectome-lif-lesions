"""Do the two central claims depend on the inherited synaptic weight?

Claim A: any odour input drives the default model into a brain-wide attractor
         (75% of KCs active); APL x5 restores sparse coding.
Claim B: in the sparse regime, 100% PPL1 loss moves the phenotype no more than
         the trial-to-trial noise floor.

Re-measured at w_syn = 0.20, 0.275 (reference), 0.35 mV.  For each: KC
fraction and active-neuron count under odour at APL x1 and x5; then at APL x5
the noise floor (2 intact seeds) and the PPL1-100% and RND16 distances.

Run:  python scripts/param_robustness.py --procs 3
"""
import argparse, sys, time
import multiprocessing as mp
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire, build_stimuli, readout_groups, group_indices   # noqa: E402
from sinek.data.flywire import Connectome                                            # noqa: E402
from sinek.lesion import apl_scaled, LesionSpec, apply_lesion                        # noqa: E402
from sinek.sim import simulate, firing_rates                                         # noqa: E402
from sinek.readout import phenotype_vector                                           # noqa: E402

_G = {}


def _job(a):
    w, apl, what, seed = a
    cn = _G["cn"][(w, apl)]
    if what == "odor":
        s = _G["stim"]["odor_DM1"]
        r = firing_rates(simulate(cn.W, 500.0, poisson=s.targets, poisson_rate=s.rate_hz, seed=seed), 100.0)
        return {"w_syn": w, "apl": apl, "what": what, "seed": seed, "kc_frac": float((r[_G["kc"]] > 5).mean()),
                "n_active": int((r > 5).sum()), "mbon_hz": float(r[_G["mbon"]].mean()), "ppl1_hz": float(r[_G["ppl1"]].mean())}
    stim = list(_G["stim"].values())
    if what == "intact":
        W = cn.W
    else:
        W, _ = apply_lesion(cn, _G["groups"], LesionSpec({what: 1.0}, seed=0), keep_pattern=True)
    x = phenotype_vector(W, stim, _G["readouts"], duration=500.0, seed=100 + seed)
    return {"w_syn": w, "apl": apl, "what": what, "seed": seed, "x": x.tolist()}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--w", nargs="*", type=float, default=[0.20, 0.275, 0.35])
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--out", default="results/param_robustness.csv")
    args = ap.parse_args()
    base = load_flywire()
    _G["cn"] = {}
    for w in args.w:
        cw = Connectome(ids=base.ids, W=(base.W * (w / 0.275)).tocsr(), meta=base.meta, name=f"flywire_w{w:g}")
        _G["cn"][(w, 1.0)] = cw; _G["cn"][(w, 5.0)] = apl_scaled(cw, 5.0)
    _G["stim"] = {s.name: s for s in build_stimuli(base)}; _G["readouts"] = readout_groups(base)
    _G["kc"] = base.select(cell_class="Kenyon_Cell"); _G["mbon"] = base.select(cell_type__startswith="MBON")
    _G["ppl1"] = base.select(cell_type__startswith="PPL1")
    groups = group_indices(base); m = base.meta
    pool = m.loc[(m["super_class"] == "central") & (~m["cell_class"].isin(["DAN", "Kenyon_Cell"])), "idx"].to_numpy()
    groups["RND16"] = np.sort(np.random.default_rng(12345).choice(pool, size=16, replace=False)); _G["groups"] = groups
    jobs = [(w, apl, "odor", 0) for w in args.w for apl in (1.0, 5.0)]
    jobs += [(w, 5.0, what, s) for w in args.w for what, seeds in (("intact", (0, 1)), ("PPL1", (0,)), ("RND16", (0,))) for s in seeds]
    rows, t0 = [], time.time()
    with mp.get_context("fork").Pool(args.procs) as p:
        for i, r in enumerate(p.imap_unordered(_job, jobs)):
            rows.append(r); print(f"{i+1}/{len(jobs)} {r['w_syn']} apl{r['apl']} {r['what']} [{time.time()-t0:.0f}s]", {k: v for k, v in r.items() if k not in ('x',)}, flush=True)
            pd.DataFrame(rows).to_csv(args.out, index=False)
    df = pd.DataFrame(rows)
    print("\n== attractor claim ==")
    print(df[df.what == "odor"][["w_syn", "apl", "kc_frac", "n_active", "mbon_hz", "ppl1_hz"]].round(3).to_string())
    print("\n== sparse-regime lesion claim (APL x5) ==")
    for w in args.w:
        d = df[(df.w_syn == w) & (df.what != "odor")]
        X = {(r.what, r.seed): np.array(r.x) for r in d.itertuples()}
        floor = np.linalg.norm(X[("intact", 0)] - X[("intact", 1)])
        base_x = (X[("intact", 0)] + X[("intact", 1)]) / 2
        print(f"w_syn {w}: noise floor {floor:.2f}, PPL1 100% {np.linalg.norm(X[('PPL1',0)]-base_x):.2f}, RND16 100% {np.linalg.norm(X[('RND16',0)]-base_x):.2f}")
