"""Generate the simulator dataset (theta, x) for the surrogate and the NPE.

theta ~ sparse prior over K lesion groups (see sinek.lesion.sample_lesions),
x = phenotype vector.  Runs in parallel over processes; appends to an .npz so
it can be resumed and merged across machines.

Run:  python scripts/run_lesion_sweep.py --n 200 --procs 4 --out results/sweep.npz
"""
import argparse, sys, time
import multiprocessing as mp
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire, group_indices, build_stimuli, readout_groups   # noqa: E402
from sinek.lesion import apply_lesion, lesion_vector, sample_lesions                     # noqa: E402
from sinek.readout import Stimulus, phenotype_vector, phenotype_names                    # noqa: E402

_G = {}


def _load(duration, trials, groups=None, backend="numpy", device="cpu"):
    """Load once in the parent; forked workers inherit the arrays copy-on-write,
    so the 1-2 GB connectome is shared instead of duplicated per process."""
    cn = load_flywire()
    _G["cn"] = cn
    _G["groups"] = group_indices(cn, groups)
    _G["stim"] = build_stimuli(cn)
    _G["readouts"] = readout_groups(cn)
    _G["duration"], _G["trials"] = duration, trials
    _G["backend"], _G["device"] = backend, device
    return cn


def _one(spec):
    W, _ = apply_lesion(_G["cn"], _G["groups"], spec)
    return phenotype_vector(W, _G["stim"], _G["readouts"], duration=_G["duration"], n_trials=_G["trials"],
                            seed=spec.seed, backend=_G["backend"], device=_G["device"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--duration", type=float, default=500.0)
    ap.add_argument("--trials", type=int, default=1)
    ap.add_argument("--mode", default="remove")
    ap.add_argument("--sparsity", type=float, default=0.5)
    ap.add_argument("--groups", nargs="*", default=None,
                    help="restrict lesioned groups (e.g. PAM PPL1 PPL2 PPM1); others stay intact")
    ap.add_argument("--group-set", choices=["default", "subtype"], default="default")
    ap.add_argument("--resume", action="store_true", help="continue from <out>.ckpt.npz (same --n/--seed/--groups)")
    ap.add_argument("--backend", choices=["numpy", "torch"], default="numpy")
    ap.add_argument("--device", default="cpu", help="torch device, e.g. cuda (use --procs 1 on a single GPU)")
    ap.add_argument("--out", default="results/sweep.npz")
    args = ap.parse_args()

    from sinek.data.groups import DA_GROUPS, CONTROL_GROUPS, SUBTYPE_GROUPS
    group_defs = {"default": {**DA_GROUPS, **CONTROL_GROUPS}, "subtype": SUBTYPE_GROUPS}[args.group_set]
    cn = _load(args.duration, args.trials, group_defs, args.backend, args.device)
    group_names = list(_G["groups"].keys())
    names = phenotype_names(_G["stim"], _G["readouts"])
    lesion_groups = args.groups or group_names
    specs = sample_lesions(lesion_groups, args.n, seed=args.seed, mode=args.mode, sparsity=args.sparsity)
    theta = np.stack([lesion_vector(s, group_names) for s in specs])   # full-length vector, zeros elsewhere

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    ckpt = out.with_suffix(".ckpt.npz")
    X_done = []
    if args.resume and ckpt.exists():
        c = np.load(ckpt, allow_pickle=False)
        X_done = list(c["x"]); assert len(X_done) <= len(specs)
        print(f"resuming from checkpoint: {len(X_done)} of {args.n} done", flush=True)
    todo = specs[len(X_done):]

    def _save(final=False):
        X = np.stack(X_done)
        th = theta[: len(X_done)]
        np.savez(ckpt, theta=th, x=X, group_names=np.array(group_names), feature_names=np.array(names))
        if final:
            if out.exists() and not args.resume:
                old = np.load(out, allow_pickle=False)
                th = np.concatenate([old["theta"], th]); X = np.concatenate([old["x"], X])
            np.savez(out, theta=th, x=X, group_names=np.array(group_names), feature_names=np.array(names))
            print(f"saved {out}: theta {th.shape}, x {X.shape}")

    t0 = time.time()
    with mp.get_context("fork").Pool(args.procs) as pool:
        for i, x in enumerate(pool.imap(_one, todo, chunksize=1)):
            X_done.append(x)
            if len(X_done) % 10 == 0:
                _save()
                print(f"{len(X_done)}/{args.n} in {time.time()-t0:.0f}s", flush=True)
    _save(final=True)
