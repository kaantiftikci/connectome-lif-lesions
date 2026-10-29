"""Trial-to-trial noise floor of the phenotype vector on the intact brain, so
lesion-induced distances can be judged against it.

Run:  python scripts/noise_floor.py --seeds 3
"""
import argparse, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire, build_stimuli, readout_groups   # noqa: E402
from sinek.readout import Stimulus, phenotype_vector, phenotype_names   # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--seeds", type=int, default=3)
ap.add_argument("--duration", type=float, default=500.0)
ap.add_argument("--out", default="results/noise_floor.npz")
ap.add_argument("--sex", choices=["female", "male"], default="female")
ap.add_argument("--count-scale", type=float, default=0.581)
ap.add_argument("--odor-rate", type=float, default=None)
ap.add_argument("--apl-scale", type=float, default=1.0)
args = ap.parse_args()

if args.sex == "male":
    from sinek.data.malecns import load_malecns_flat, map_stimuli_from_female
    female = load_flywire(); cn = load_malecns_flat(count_scale=args.count_scale); stim = map_stimuli_from_female(cn, female); del female
else:
    cn = load_flywire(); stim = build_stimuli(cn)
if args.odor_rate is not None:
    for s_ in stim:
        if s_.name == "odor_DM1":
            s_.rate_hz = args.odor_rate
from sinek.lesion import apl_scaled   # noqa: E402
cn = apl_scaled(cn, args.apl_scale)
readouts = readout_groups(cn)
names = phenotype_names(stim, readouts)
X = []
for s in range(args.seeds):
    t0 = time.time()
    X.append(phenotype_vector(cn.W, stim, readouts, duration=args.duration, seed=100 + s))
    print(f"seed {s} done in {time.time()-t0:.0f}s", flush=True)
X = np.stack(X)
d = [np.linalg.norm(X[i] - X[j]) for i in range(len(X)) for j in range(i + 1, len(X))]
print(f"pairwise L2 between intact-brain repeats: mean {np.mean(d):.3f}, max {np.max(d):.3f}")
print(f"features changing >0.1 between repeats: mean {np.mean([(np.abs(X[i]-X[j])>0.1).sum() for i in range(len(X)) for j in range(i+1,len(X))]):.1f}")
Path(args.out).parent.mkdir(parents=True, exist_ok=True)
np.savez(args.out, x=X, feature_names=np.array(names))
