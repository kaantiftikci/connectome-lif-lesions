"""Infer a lesion posterior for an observed phenotype vector.

The observed vector must be in the same feature space (same stimuli and
readouts) as the sweep.  Phase 1: x_obs comes from a held-out simulation;
phase 2: from an embodied readout matched to a published fly disease-model
phenotype (see docs/PLAN.md).

Run:  python scripts/infer_lesion.py --sweep results/sweep.npz --x-obs results/x_obs.npy
"""
import argparse, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.inference import LesionPosterior      # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--sweep", default="results/sweep.npz")
ap.add_argument("--x-obs", required=True)
ap.add_argument("--samples", type=int, default=5000)
args = ap.parse_args()

d = np.load(args.sweep, allow_pickle=False)
groups = [str(g) for g in d["group_names"]]
post = LesionPosterior(groups).fit(d["theta"], d["x"])
x_obs = np.load(args.x_obs)
for g, (med, lo, hi) in post.summarize(x_obs, n=args.samples).items():
    print(f"{g:6s} loss fraction median {med:.2f}  90% CI [{lo:.2f}, {hi:.2f}]")
