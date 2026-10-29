"""Is the sugar -> PAM reward route carried by octopaminergic neurons, as in
biology (Burke et al. 2012: OA-VUMa2 / OAMB)?  Sparse regime.

Measures: sugar GRN -> OA neuron synaptic input and OA rates under sugar;
OA -> PAM synaptic weights; and what PAM does when the OA neurons are driven
directly at 100 Hz (does the OA -> PAM wiring conduct at all?).

Run:  python scripts/octopamine_path.py
"""
import sys
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire
from sinek.lesion import apl_scaled
from sinek.sim import simulate, firing_rates

cn = apl_scaled(load_flywire(), 5.0); m = cn.meta; W = cn.W
oa = m.loc[m["cell_type"].astype(str).str.startswith("OA-"), "idx"].to_numpy()
print(f"{oa.size} octopaminergic (OA-*) neurons:", m.loc[oa, "cell_type"].value_counts().to_dict())
sugar = cn.select(cell_sub_class="sugar"); pam = cn.select(cell_type__startswith="PAM"); ppl1 = cn.select(cell_type__startswith="PPL1")
r = firing_rates(simulate(W, 500.0, poisson=sugar, poisson_rate=150.0, seed=0), 100.0)
A = np.where(r > 5)[0]
h1 = np.asarray(W[sugar].sum(0)).ravel(); drive = np.asarray(W[A].multiply(r[A][:, None] / 100.0).sum(0)).ravel()
to_pam = np.asarray(W[:, pam].sum(1)).ravel(); to_ppl1 = np.asarray(W[:, ppl1].sum(1)).ravel()
rows = []
for i in oa:
    rows.append({"cell_type": m.at[i, "cell_type"], "side": m.at[i, "side"], "direct_from_sugar_mV": h1[i], "from_active_mV_per_10ms": drive[i],
                 "rate_under_sugar_Hz": r[i], "to_PAM_mV": to_pam[i], "n_PAM_targets": int((W[i, pam] > 0).sum()), "to_PPL1_mV": to_ppl1[i]})
df = pd.DataFrame(rows).sort_values("to_PAM_mV", ascending=False)
print(df.round(2).to_string())
Path("results").mkdir(exist_ok=True); df.to_csv("results/octopamine_path.csv", index=False)
# drive the OA neurons directly: does OA -> PAM conduct?
for rate in (50.0, 100.0, 150.0):
    r2 = firing_rates(simulate(W, 500.0, poisson=oa, poisson_rate=rate, seed=0), 100.0)
    print(f"OA neurons driven at {rate:.0f} Hz: PAM mean {r2[pam].mean():.2f} Hz ({(r2[pam]>5).mean()*100:.0f}% >5 Hz), PPL1 {r2[ppl1].mean():.2f} Hz, active neurons {(r2>5).sum()}")
# and OA + sugar together
r3 = firing_rates(simulate(W, 500.0, poisson={**{int(i): 150.0 for i in sugar}, **{int(i): 100.0 for i in oa}}, seed=0), 100.0)
print(f"sugar 150 Hz + OA 100 Hz: PAM {r3[pam].mean():.2f} Hz, PPL1 {r3[ppl1].mean():.2f} Hz, active {(r3>5).sum()}")
