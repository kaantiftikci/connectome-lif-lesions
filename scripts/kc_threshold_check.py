"""Does the sparse-regime result depend on how sparsity is produced?

Instead of APL x5, raise the spike threshold of Kenyon cells by d mV.  Find
the d that gives ~4% KC activation under odour, then measure the noise floor
(2 intact seeds), PPL1 100% and RND16 100% distances with that threshold.

Run:  python scripts/kc_threshold_check.py --procs 3
"""
import argparse, sys, time
import multiprocessing as mp
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire, build_stimuli, readout_groups, group_indices   # noqa: E402
from sinek.lesion import LesionSpec, apply_lesion                                    # noqa: E402
from sinek.sim import simulate, firing_rates                                         # noqa: E402
from sinek.readout import phenotype_vector                                           # noqa: E402

_G = {}


def _job(a):
    d, what, seed = a
    cn = _G["cn"]; off = np.zeros(cn.n); off[_G["kc"]] = d
    if what == "odor":
        s = _G["stim"]["odor_DM1"]
        r = firing_rates(simulate(cn.W, 500.0, poisson=s.targets, poisson_rate=s.rate_hz, seed=seed, v_th_offset=off), 100.0)
        return {"d_mv": d, "what": what, "seed": seed, "kc_frac": float((r[_G["kc"]] > 5).mean()), "n_active": int((r > 5).sum()),
                "mbon_hz": float(r[_G["mbon"]].mean()), "ppl1_hz": float(r[_G["ppl1"]].mean()), "pam_hz": float(r[_G["pam"]].mean())}
    W = cn.W if what == "intact" else apply_lesion(cn, _G["groups"], LesionSpec({what: 1.0}, seed=0), keep_pattern=True)[0]
    x = phenotype_vector(W, list(_G["stim"].values()), _G["readouts"], duration=500.0, seed=100 + seed, v_th_offset=off)
    return {"d_mv": d, "what": what, "seed": seed, "x": x.tolist()}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--d", nargs="*", type=float, default=[1.0, 2.0, 3.0, 4.0])
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--out", default="results/kc_threshold.csv")
    args = ap.parse_args()
    cn = load_flywire(); _G["cn"] = cn
    _G["stim"] = {s.name: s for s in build_stimuli(cn)}; _G["readouts"] = readout_groups(cn)
    _G["kc"] = cn.select(cell_class="Kenyon_Cell"); _G["mbon"] = cn.select(cell_type__startswith="MBON")
    _G["ppl1"] = cn.select(cell_type__startswith="PPL1"); _G["pam"] = cn.select(cell_type__startswith="PAM")
    groups = group_indices(cn); m = cn.meta
    pool = m.loc[(m["super_class"] == "central") & (~m["cell_class"].isin(["DAN", "Kenyon_Cell"])), "idx"].to_numpy()
    groups["RND16"] = np.sort(np.random.default_rng(12345).choice(pool, size=16, replace=False)); _G["groups"] = groups
    rows, t0 = [], time.time()
    with mp.get_context("fork").Pool(args.procs) as p:
        for r in p.imap_unordered(_job, [(d, "odor", 0) for d in args.d]):
            rows.append(r); print(r, f"[{time.time()-t0:.0f}s]", flush=True)
    od = pd.DataFrame(rows)
    best = float(od.iloc[(od.kc_frac - 0.04).abs().argsort().iloc[0]].d_mv)
    print(f"closest to 4% KC activation: +{best} mV", flush=True)
    jobs = [(best, "intact", 0), (best, "intact", 1), (best, "PPL1", 0), (best, "RND16", 0), (best, "PAM", 0)]
    with mp.get_context("fork").Pool(args.procs) as p:
        for r in p.imap_unordered(_job, jobs):
            rows.append(r); print(r["what"], r["seed"], f"[{time.time()-t0:.0f}s]", flush=True)
    pd.DataFrame(rows).to_csv(args.out, index=False)
    X = {(r["what"], r["seed"]): np.array(r["x"]) for r in rows if "x" in r}
    floor = np.linalg.norm(X[("intact", 0)] - X[("intact", 1)]); base = (X[("intact", 0)] + X[("intact", 1)]) / 2
    print(f"\nKC threshold +{best} mV: noise floor {floor:.2f}, PPL1 100% {np.linalg.norm(X[('PPL1',0)]-base):.2f}, "
          f"PAM 100% {np.linalg.norm(X[('PAM',0)]-base):.2f}, RND16 100% {np.linalg.norm(X[('RND16',0)]-base):.2f}")
