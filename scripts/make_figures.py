"""Phase-1 figures.

  fig1_reserve_curves.png     phenotype distance vs loss fraction, mean +- SD over lesion orders/seeds, noise floor
  fig2_sensitivity.png        |dx/dtheta| per lesion group (surrogate sensitivity map)
  fig3_posterior_recovery.png truth vs posterior median (90% CI) per group, held-out simulations

Run:  python scripts/make_figures.py --progressive results/progressive.csv --noise results/noise_floor.npz \
          --report results/surrogate_report.npz --out artifacts/figures
"""
import argparse
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ap = argparse.ArgumentParser()
ap.add_argument("--progressive", default="results/progressive.csv")
ap.add_argument("--noise", default="results/noise_floor.npz")
ap.add_argument("--report", default="results/surrogate_report.npz")
ap.add_argument("--out", default="artifacts/figures")
args = ap.parse_args()
out = Path(args.out); out.mkdir(parents=True, exist_ok=True)

# ---- fig 1: reserve curves
df = pd.read_csv(args.progressive)
if "lesion_seed" not in df:
    df["lesion_seed"] = 0; df["sim_seed"] = 0
piv = df.pivot_table(index=["group", "fraction", "lesion_seed", "sim_seed"], columns="feature", values="value")
base = piv.xs(0.0, level="fraction").mean()
dist = piv.apply(lambda x: np.linalg.norm(x - base), axis=1).rename("L2").reset_index()
summ = dist.groupby(["group", "fraction"])["L2"].agg(["mean", "std"]).reset_index()
nf = None
if Path(args.noise).exists():
    X = np.load(args.noise)["x"]
    nf = np.mean([np.linalg.norm(X[i] - X[j]) for i in range(len(X)) for j in range(i + 1, len(X))])
fig, ax = plt.subplots(figsize=(6.5, 4.2))
order = [g for g in ["PPL1", "PAM", "PPL2", "PPM1", "RND16", "RND307", "KC"] if g in summ.group.unique()]
order += [g for g in summ.group.unique() if g not in order]
for g in order:
    s = summ[summ.group == g]
    style = "--" if g.startswith("RND") or g == "KC" else "-"
    ax.errorbar(s.fraction * 100, s["mean"], yerr=s["std"].fillna(0), fmt="o" + style, capsize=3, label=g)
if nf is not None:
    ax.axhline(nf, color="gray", lw=1, ls=":", label="noise floor (intact repeats)")
ax.set_xlabel("neurons lost in group (%)"); ax.set_ylabel("phenotype distance from intact (L2, log-rate features)")
ax.set_title("Progressive lesions (5 lesion orders x 2 simulation seeds)"); ax.legend(fontsize=8, ncol=2)
fig.tight_layout(); fig.savefig(out / "fig1_reserve_curves.png", dpi=160); plt.close(fig)
summ.to_csv(out / "fig1_reserve_curves.csv", index=False)

# ---- fig 2 + 3: surrogate report
if Path(args.report).exists():
    r = np.load(args.report, allow_pickle=False)
    groups = [str(g) for g in r["groups"]]; J = r["sensitivity"]
    sens = np.abs(J).sum(0)
    fig, ax = plt.subplots(figsize=(max(5, 0.35 * len(groups) + 2), 3.8))
    o = np.argsort(sens)[::-1]
    ax.bar([groups[i] for i in o], sens[o], color=["tab:red" if groups[i].startswith(("PAM", "PPL", "PPM")) else "tab:gray" for i in o])
    ax.set_ylabel(r"$\sum_{features} |\partial x / \partial \theta|$"); ax.set_title(f"Surrogate sensitivity (ridge CV R$^2$={float(r['r2_ridge']):.2f}, n={int(r['n_sims'])})")
    plt.setp(ax.get_xticklabels(), rotation=60, ha="right", fontsize=8)
    fig.tight_layout(); fig.savefig(out / "fig2_sensitivity.png", dpi=160); plt.close(fig)

    T, M, L, H = r["rec_truth"], r["rec_median"], r["rec_lo"], r["rec_hi"]
    k = len(groups); ncol = min(4, k); nrow = int(np.ceil(k / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3 * ncol, 3 * nrow), squeeze=False)
    for j, g in enumerate(groups):
        ax = axes[j // ncol][j % ncol]
        ax.errorbar(T[:, j], M[:, j], yerr=[M[:, j] - L[:, j], H[:, j] - M[:, j]], fmt="o", ms=3, alpha=0.7, capsize=2)
        ax.plot([0, 1], [0, 1], "k:", lw=1); ax.set_xlim(-0.05, 1.05); ax.set_ylim(-0.05, 1.05)
        err = np.abs(M[:, j] - T[:, j]).mean()
        ax.set_title(f"{g}  (|err| {err:.2f})", fontsize=9); ax.set_xlabel("true loss fraction"); ax.set_ylabel("posterior median")
    for j in range(k, nrow * ncol):
        axes[j // ncol][j % ncol].axis("off")
    fig.suptitle("NPE recovery of known lesions (held-out simulations, 90% CI)")
    fig.tight_layout(); fig.savefig(out / "fig3_posterior_recovery.png", dpi=160); plt.close(fig)
print("figures written to", out)
