"""Silent-reserve curve: progressive loss of one group vs phenotype shift.

For each group and loss fraction, lesion the connectome, run the stimulus
battery, and record the phenotype vector.  Output: results/progressive.csv
with one row per (group, fraction, feature).  The question answered: how much
of a dopaminergic cluster can be lost before the descending-neuron output
changes, and does that threshold differ from a size-matched control group?

Run:  python scripts/progressive_curve.py --groups PPL1 PAM KC --fractions 0 0.2 0.4 0.6 0.8 1.0
"""
import argparse, sys, time
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire, group_indices, stimulus_indices, readout_groups   # noqa: E402
from sinek.lesion import LesionSpec, apply_lesion                                        # noqa: E402
from sinek.readout import Stimulus, phenotype_vector, phenotype_names                    # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--groups", nargs="+", default=["PPL1", "PAM", "KC"])
ap.add_argument("--fractions", nargs="+", type=float, default=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
ap.add_argument("--mode", default="remove")
ap.add_argument("--duration", type=float, default=500.0)
ap.add_argument("--trials", type=int, default=1)
ap.add_argument("--out", default="results/progressive.csv")
args = ap.parse_args()

cn = load_flywire()
groups = group_indices(cn)
stim = [Stimulus(k, v) for k, v in stimulus_indices(cn).items()]
readouts = readout_groups(cn)
names = phenotype_names(stim, readouts)
print(f"{cn.n} neurons; stimuli {[s.name for s in stim]}; {len(readouts)} readouts -> {len(names)} features")

rows = []
Path(args.out).parent.mkdir(parents=True, exist_ok=True)
for g in args.groups:
    for f in args.fractions:
        t0 = time.time()
        W, hit = apply_lesion(cn, groups, LesionSpec({g: f}, mode=args.mode))
        x = phenotype_vector(W, stim, readouts, duration=args.duration, n_trials=args.trials)
        n_hit = sum(len(v) for v in hit.values())
        rows.extend({"group": g, "fraction": f, "n_lesioned": n_hit, "feature": nm, "value": float(v)}
                    for nm, v in zip(names, x))
        pd.DataFrame(rows).to_csv(args.out, index=False)
        print(f"{g:5s} {f:.1f} ({n_hit:4d} neurons) done in {time.time()-t0:.0f}s; mean feature {x.mean():.3f}")
print("wrote", args.out)
