"""Summarise results/progressive.csv: distance from the intact brain per
(group, fraction) with mean and SD over lesion orders and simulation seeds,
and the features that move most at full loss.

Run:  python scripts/analyze_progressive.py [--csv results/progressive.csv] [--noise results/noise_floor.npz]
"""
import argparse
import numpy as np, pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--csv", default="results/progressive.csv")
ap.add_argument("--noise", default=None)
ap.add_argument("--top", type=int, default=6)
ap.add_argument("--save", default=None, help="write the summary table to this csv")
args = ap.parse_args()

df = pd.read_csv(args.csv)
if "lesion_seed" not in df:
    df["lesion_seed"] = 0; df["sim_seed"] = 0
piv = df.pivot_table(index=["group", "fraction", "lesion_seed", "sim_seed"], columns="feature", values="value")
base_rows = piv.xs(0.0, level="fraction")
base = base_rows.groupby(level="sim_seed").mean().mean()          # intact brain, averaged over seeds
rows = []
for (g, f, ls, ss), x in piv.iterrows():
    rows.append((g, f, ls, ss, float(np.linalg.norm(x - base)), int((np.abs(x - base) > 0.1).sum())))
d = pd.DataFrame(rows, columns=["group", "fraction", "lesion_seed", "sim_seed", "L2", "changed"])
n_les = df.groupby(["group", "fraction"])["n_lesioned"].first()
summ = d.groupby(["group", "fraction"]).agg(L2_mean=("L2", "mean"), L2_sd=("L2", "std"), L2_min=("L2", "min"),
                                             L2_max=("L2", "max"), changed_mean=("changed", "mean"), n=("L2", "size"))
summ.insert(0, "n_lesioned", n_les.reindex(summ.index).to_numpy())
if args.noise:
    X = np.load(args.noise)["x"]
    nf = [np.linalg.norm(X[i] - X[j]) for i in range(len(X)) for j in range(i + 1, len(X))]
    print(f"noise floor (intact repeats): L2 mean {np.mean(nf):.3f}, max {np.max(nf):.3f}")
print("phenotype distance from intact brain (L2 over log-rate features)")
print(summ.round(3).to_string())
if args.save:
    summ.to_csv(args.save)

print(f"\ntop {args.top} features moved at full loss (mean over seeds), per group:")
full = piv.groupby(level=["group", "fraction"]).mean()
for g in full.index.get_level_values(0).unique():
    fmax = full.loc[g].index.max()
    delta = (full.loc[(g, fmax)] - base).sort_values(key=np.abs, ascending=False).head(args.top)
    print(f"  {g} ({fmax:.0%}):")
    for k, v in delta.items():
        print(f"    {v:+.3f}  {k}  (intact {base[k]:.2f})")
