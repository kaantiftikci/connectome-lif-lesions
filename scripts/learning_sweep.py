"""Positive arm 3: simulator dataset where the phenotype is the LEARNING readout.

theta ~ sparse prior over the 32 dopaminergic subtypes (as run_lesion_sweep);
x = [learning index per MBON type under odour+sugar, under odour+bitter,
     pre-pairing odour response per MBON type (log1p Hz)]
with the two teaching-signal routes supplied (compartment_map.py).  Resumable;
output format matches train_surrogate.py (theta, x, group_names, feature_names).

Run:  python scripts/learning_sweep.py --n 300 --procs 8 --resume --out results/learning_sweep.npz
"""
import argparse, json, sys, time
import multiprocessing as mp
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from sinek.data import load_flywire, group_indices, build_stimuli      # noqa: E402
from sinek.data.flywire import Connectome                              # noqa: E402
from sinek.data.groups import SUBTYPE_GROUPS                           # noqa: E402
from sinek.lesion import apply_lesion, lesion_vector, sample_lesions, apl_scaled   # noqa: E402
from sinek.neuromod import ModulationParams                            # noqa: E402
from compartment_map import build, run_protocol                        # noqa: E402

_G = {}


def _one(spec):
    cn = _G["cn"]
    W, _ = apply_lesion(cn, _G["groups"], spec, keep_pattern=True)
    lcn = Connectome(ids=cn.ids, W=W, meta=cn.meta, name=cn.name)
    feats = []
    pre_sugar = None
    for us_name in ("sugar", "bitter"):
        extra = (_G["us"]["sugar"], _G["pam"], _G["g_reward"]) if us_name == "sugar" else None
        pre, post, _ = run_protocol(lcn, _G["mpar"], _G["cs"], _G["us"][us_name], 150.0, extra)
        pre = pre.reindex(_G["mbon_types"]).fillna(0.0); post = post.reindex(_G["mbon_types"]).fillna(0.0)
        li = ((pre - post) / pre.replace(0, np.nan)).fillna(0.0).clip(-1, 1)
        feats.append(li.to_numpy(dtype=np.float32))
        if pre_sugar is None:
            pre_sugar = np.log1p(pre.to_numpy(dtype=np.float32))
    return np.concatenate(feats + [pre_sugar])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--sparsity", type=float, default=0.5)
    ap.add_argument("--apl-scale", type=float, default=5.0)
    ap.add_argument("--boost", type=float, default=4.0)
    ap.add_argument("--g-reward", type=float, default=0.5)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--out", default="results/learning_sweep.npz")
    args = ap.parse_args()
    cn = build(apl_scaled(load_flywire(), args.apl_scale), args.boost)
    fit = json.load(open("results/modulation_fit.json")) if Path("results/modulation_fit.json").exists() else {"kappa": 0.003, "eta": 1e-4}
    _G["mpar"] = ModulationParams(kappa=fit["kappa"], eta=max(fit["eta"], 1e-4), alpha_fast=0.0)
    _G["cn"] = cn; _G["groups"] = group_indices(cn, SUBTYPE_GROUPS)
    stim = {s.name: s for s in build_stimuli(cn)}
    _G.update(cs=stim["odor_DM1"].targets, us={"sugar": stim["sugar"].targets, "bitter": stim["bitter"].targets},
              pam=cn.select(cell_type__startswith="PAM"), g_reward=args.g_reward)
    mb = cn.select(cell_type__startswith="MBON")
    _G["mbon_types"] = sorted(set(cn.meta.loc[mb, "cell_type"].astype(str)))
    group_names = list(_G["groups"].keys())
    names = [f"sugar|LI:{m}" for m in _G["mbon_types"]] + [f"bitter|LI:{m}" for m in _G["mbon_types"]] + [f"odor|pre:{m}" for m in _G["mbon_types"]]
    specs = sample_lesions(group_names, args.n, seed=args.seed, mode="remove", sparsity=args.sparsity)
    theta = np.stack([lesion_vector(s, group_names) for s in specs])
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True); ckpt = out.with_suffix(".ckpt.npz")
    X_done = []
    if args.resume and ckpt.exists():
        X_done = list(np.load(ckpt, allow_pickle=False)["x"]); print(f"resuming: {len(X_done)} done", flush=True)
    todo = specs[len(X_done):]

    def _save(final=False):
        X = np.stack(X_done); th = theta[:len(X_done)]
        np.savez(ckpt, theta=th, x=X, group_names=np.array(group_names), feature_names=np.array(names))
        if final:
            np.savez(out, theta=th, x=X, group_names=np.array(group_names), feature_names=np.array(names)); print(f"saved {out}: theta {th.shape}, x {X.shape}")

    print(f"{len(todo)} simulations on {args.procs} workers; {len(names)} features", flush=True)
    t0 = time.time()
    with mp.get_context("fork").Pool(args.procs) as pool:
        for x in pool.imap(_one, todo, chunksize=1):
            X_done.append(x)
            if len(X_done) % 5 == 0:
                _save(); print(f"{len(X_done)}/{args.n} in {time.time()-t0:.0f}s", flush=True)
    _save(final=True)
