"""Train the surrogate and the NPE posterior on results/sweep.npz, then run the
in-silico validation: held-out prediction error, posterior recovery of known
lesions, and the reverse screen (which non-DA lesion mimics PPL1 loss?).

Run:  python scripts/train_surrogate.py --sweep results/sweep.npz
Requires the [ai] extra (torch, sbi).
"""
import argparse, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.surrogate import Surrogate, LinearSurrogate, cv_r2   # noqa: E402
from sinek.inference import LesionPosterior      # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--sweep", default="results/sweep.npz")
ap.add_argument("--epochs", type=int, default=300)
ap.add_argument("--holdout", type=float, default=0.2)
ap.add_argument("--min-sd", type=float, default=1e-6)
args = ap.parse_args()

d = np.load(args.sweep, allow_pickle=False)
theta, x = d["theta"], d["x"]
groups = [str(g) for g in d["group_names"]]
# drop features that never change across the sweep (silent readouts, stimuli untouched by these lesions)
keep = x.std(0) > args.min_sd
feat_names = [str(f) for f in d["feature_names"]]
print(f"features: {x.shape[1]} total, {int(keep.sum())} vary (sd > {args.min_sd}); dropping the rest")
x = x[:, keep]
# drop lesion groups that were never lesioned in this sweep (restricted sweeps); the posterior is over the rest
on = theta.std(0) > 1e-6
if (~on).any():
    print(f"lesion groups never varied in this sweep, excluded from the posterior: {[g for g, o in zip(groups, on) if not o]}")
theta = theta[:, on]; groups = [g for g, o in zip(groups, on) if o]
n = len(theta); k = int(n * (1 - args.holdout))
rng = np.random.default_rng(0); perm = rng.permutation(n)
tr, te = perm[:k], perm[k:]
print(f"{n} simulations, {theta.shape[1]} lesion groups {groups}, {x.shape[1]} features")

K, D = theta.shape[1], x.shape[1]
r2_lin = cv_r2(lambda: LinearSurrogate(K, D, lam=1.0), theta, x)
r2_mlp = cv_r2(lambda: Surrogate(K, D, n_members=2), theta, x, epochs=args.epochs)
print(f"5-fold CV R^2: ridge {r2_lin:.3f}   MLP ensemble {r2_mlp:.3f}")
sur = (LinearSurrogate(K, D) if r2_lin >= r2_mlp else Surrogate(K, D)).fit(theta, x, epochs=args.epochs)
print(f"using {'ridge' if r2_lin >= r2_mlp else 'MLP'} surrogate for sensitivity and reverse screen")

J = sur.sensitivity()
print("sensitivity |dx/dtheta| summed over features, per group:")
for g, s in sorted(zip(groups, np.abs(J).sum(0)), key=lambda t: -t[1]):
    print(f"  {g:6s} {s:8.3f}")

post = LesionPosterior(groups).fit(theta[tr], x[tr])
err = []
for i in te[:20]:
    s = post.summarize(x[i])
    err.append([abs(s[g][0] - theta[i, j]) for j, g in enumerate(groups)])
err = np.array(err)
print("posterior-median recovery error per group (held-out):")
for g, e in zip(groups, err.mean(0)):
    print(f"  {g:6s} {e:.3f}")

if "PPL1" in groups:
    j = groups.index("PPL1")
    target = np.zeros(theta.shape[1], np.float32); target[j] = 1.0
    x_ppl1, _ = sur.predict(target)
    mimic = sur.reverse_screen(x_ppl1[0], exclude=[j])
    print("reverse screen: lesion (excluding PPL1) that best mimics full PPL1 loss:")
    for g, v in sorted(zip(groups, mimic), key=lambda t: -t[1]):
        print(f"  {g:6s} {v:.2f}")
