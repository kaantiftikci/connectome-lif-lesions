"""Generate the simulator dataset (theta, x) for the surrogate and the NPE.

theta ~ sparse prior over K lesion groups (see sinek.lesion.sample_lesions),
x = phenotype vector.  Runs in parallel over processes; appends to an .npz so
it can be resumed and merged across machines.

Run:  python scripts/run_lesion_sweep.py --n 200 --procs 4 --out results/sweep.npz
"""
import argparse, sys, time
from multiprocessing import Pool
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire, group_indices, stimulus_indices, readout_groups   # noqa: E402
from sinek.lesion import apply_lesion, lesion_vector, sample_lesions                     # noqa: E402
from sinek.readout import Stimulus, phenotype_vector, phenotype_names                    # noqa: E402

_G = {}


def _init(duration, trials):
    cn = load_flywire()
    _G["cn"] = cn
    _G["groups"] = group_indices(cn)
    _G["stim"] = [Stimulus(k, v) for k, v in stimulus_indices(cn).items()]
    _G["readouts"] = readout_groups(cn)
    _G["duration"], _G["trials"] = duration, trials


def _one(spec):
    W, _ = apply_lesion(_G["cn"], _G["groups"], spec)
    return phenotype_vector(W, _G["stim"], _G["readouts"], duration=_G["duration"], n_trials=_G["trials"],
                            seed=spec.seed)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--duration", type=float, default=500.0)
    ap.add_argument("--trials", type=int, default=1)
    ap.add_argument("--mode", default="remove")
    ap.add_argument("--sparsity", type=float, default=0.5)
    ap.add_argument("--out", default="results/sweep.npz")
    args = ap.parse_args()

    cn = load_flywire()
    group_names = list(group_indices(cn).keys())
    stim = [Stimulus(k, v) for k, v in stimulus_indices(cn).items()]
    names = phenotype_names(stim, readout_groups(cn))
    specs = sample_lesions(group_names, args.n, seed=args.seed, mode=args.mode, sparsity=args.sparsity)
    theta = np.stack([lesion_vector(s, group_names) for s in specs])
    del cn

    t0 = time.time()
    with Pool(args.procs, initializer=_init, initargs=(args.duration, args.trials)) as pool:
        X = []
        for i, x in enumerate(pool.imap(_one, specs, chunksize=1)):
            X.append(x)
            if (i + 1) % 10 == 0:
                print(f"{i+1}/{args.n} in {time.time()-t0:.0f}s", flush=True)
    X = np.stack(X)
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        old = np.load(out, allow_pickle=False)
        theta = np.concatenate([old["theta"], theta]); X = np.concatenate([old["x"], X])
    np.savez(out, theta=theta, x=X, group_names=np.array(group_names), feature_names=np.array(names))
    print(f"saved {out}: theta {theta.shape}, x {X.shape}")
