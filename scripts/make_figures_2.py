"""Figures 6-7: Jo (2026) re-test in both regimes; reinforcer-pathway boost.

Run:  python scripts/make_figures_2.py
"""
import numpy as np, pandas as pd
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

out = Path("artifacts/figures"); out.mkdir(parents=True, exist_ok=True)
C = {"hub": "#2a78d6", "shuffled": "#eb6834", "antihub": "#1baf7a", "in": "#2a78d6", "out": "#eb6834", "both": "#1baf7a"}
INK, MUTED, GRID = "#1f1f1e", "#6b6a63", "#e4e3dd"
plt.rcParams.update({"font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK, "ytick.color": INK,
                     "axes.spines.top": False, "axes.spines.right": False})

# ---- fig 6: Jo re-test
d = pd.read_csv("results/jo_retest.csv")
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4), sharey=False)
for ax, reg in zip(axes, ("attractor", "sparse")):
    h = d[(d.regime == reg) & (d["map"] == "healthy")].spikes_odor.median()
    for i, mp in enumerate(("hub", "shuffled", "antihub")):
        g = d[(d.regime == reg) & (d["map"] == mp)]
        y = 100 * g.spikes_odor / h
        ax.bar(i, y.median(), width=0.55, color=C[mp], alpha=0.25, edgecolor=C[mp], linewidth=1.2)
        ax.scatter(np.full(len(y), i) + np.random.default_rng(i).uniform(-0.12, 0.12, len(y)), y, s=14, color=C[mp], zorder=3)
        ax.text(i, y.median() + 3, f"{y.median():.0f} %", ha="center", va="bottom", fontsize=8, color=INK)
    ax.axhline(100, color=MUTED, lw=0.8, ls=":")
    ax.set_xticks(range(3)); ax.set_xticklabels(["hub", "shuffled", "antihub"])
    ax.set_title({"attractor": "attractor regime (APL ×1)", "sparse": "sparse regime (APL ×5)"}[reg], fontsize=10, color=INK)
    ax.set_ylim(0, 125); ax.yaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
axes[0].set_ylabel("odour-evoked whole-brain spikes (% of healthy)")
fig.suptitle("Neuron-loss rule of Jo (2026) at s = 0.5: median bar, 8 replicates as dots", fontsize=10, color=INK, y=0.99)
fig.tight_layout(); fig.savefig(out / "fig6_jo_retest.png", dpi=160); plt.close(fig)

# ---- fig 7: pathway boost
b = pd.read_csv("results/boost_bitter_PPL1.csv"); s = pd.read_csv("results/boost_sugar_PAM.csv")
fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.3), sharey=True)
for ax, df, title in zip(axes, (b, s), ("bitter → PPL1", "sugar → PAM")):
    for hop in ("in", "out", "both"):
        g = df[df.hop == hop].sort_values("k")
        ax.plot(g.k, g.target_hz, "-o", color=C[hop], lw=2, ms=5, label={"in": "input hop (active set → relays)", "out": "output hop (relays → DANs)", "both": "both hops"}[hop])
    ax.set_xscale("log", base=2); ax.set_xticks([1, 2, 4, 8, 16]); ax.set_xticklabels(["×1", "×2", "×4", "×8", "×16"])
    ax.set_xlabel("synaptic strengthening of 20 relay neurons"); ax.set_title(title, fontsize=10, color=INK)
    ax.yaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
axes[0].set_ylabel("target cluster rate (Hz) at 150 Hz reinforcer")
axes[0].legend(fontsize=7.5, frameon=False, loc="upper left")
axes[0].annotate("brain-wide\nattractor", xy=(4, 17.3), xytext=(1.6, 60), fontsize=7.5, color=MUTED, arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.6))
fig.suptitle("Smallest local change that conducts a reinforcer to its dopaminergic cluster (sparse regime)", fontsize=10, color=INK, y=0.99)
fig.tight_layout(); fig.savefig(out / "fig7_pathway_boost.png", dpi=160); plt.close(fig)
print("wrote fig6, fig7")
