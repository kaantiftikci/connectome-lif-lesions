"""Summarise results/progressive.csv: phenotype distance from the intact brain
per (group, fraction), and the features that move most.

Run:  python scripts/analyze_progressive.py [--csv results/progressive.csv]
"""
import argparse
import numpy as np, pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--csv", default="results/progressive.csv")
ap.add_argument("--top", type=int, default=8)
args = ap.parse_args()

df = pd.read_csv(args.csv)
piv = df.pivot_table(index=["group", "fraction"], columns="feature", values="value")
base = piv.xs(0.0, level="fraction").iloc[0]      # fraction 0 is identical for every group
n_les = df.groupby(["group", "fraction"])["n_lesioned"].first()

print("phenotype distance from intact brain (L2 over log-rate features; baseline = 0)")
rows = []
for (g, f), x in piv.iterrows():
    d = float(np.linalg.norm(x - base))
    changed = int((np.abs(x - base) > 0.1).sum())
    rows.append((g, f, int(n_les[(g, f)]), d, changed))
tab = pd.DataFrame(rows, columns=["group", "fraction", "n_lesioned", "L2_dist", "features_changed>0.1"])
print(tab.to_string(index=False, float_format=lambda v: f"{v:.3f}"))

print(f"\ntop {args.top} features moved at full loss, per group:")
for g in piv.index.get_level_values(0).unique():
    full = piv.loc[(g, piv.loc[g].index.max())]
    delta = (full - base).sort_values(key=np.abs, ascending=False).head(args.top)
    print(f"  {g}:")
    for k, v in delta.items():
        print(f"    {v:+.3f}  {k}  (intact {base[k]:.2f})")
