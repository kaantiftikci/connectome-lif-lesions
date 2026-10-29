"""Summarise compartment_map.py output: which MBONs learn from which reinforcer,
agreement with the literature valence map, and per-MBON reserve thresholds
against the number of dopaminergic neurons converging on the MBON.

Run:  python scripts/analyze_compartment_map.py results/compartment_map.csv --apl-scale 5
"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire   # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("csv")
ap.add_argument("--apl-scale", type=float, default=5.0)
ap.add_argument("--li-min", type=float, default=0.3)
ap.add_argument("--pre-min", type=float, default=2.0)
ap.add_argument("--out", default=None)
args = ap.parse_args()
d = pd.read_csv(args.csv)
lit = json.load(open("docs/literature_compartments.json"))["mbon"]
cn = load_flywire(); m = cn.meta
dan = {k: cn.select(cell_type__startswith=k) for k in ("PAM", "PPL1")}
conv = {}
for t in sorted(d.mbon.unique()):
    mb = cn.select(cell_type=t)
    conv[t] = {k: int((np.asarray(cn.W[v][:, mb].sum(1)).ravel() >= 2.0).sum()) for k, v in dan.items()}

rows = []
print(f"== learned MBONs (intact, LI >= {args.li_min}, pre >= {args.pre_min} Hz) ==")
for us in ("sugar", "bitter"):
    it = d[(d.us == us) & (d.fraction == 0)].set_index("mbon")
    resp = it[it.pre_hz >= args.pre_min]
    learned = resp[resp.li >= args.li_min].sort_values("li", ascending=False)
    print(f"\n{us}: {len(resp)} MBON types respond to the odour; {len(learned)} learn")
    for t, r in learned.iterrows():
        L = lit.get(t, {}); exp = L.get("memory", "?")
        agree = "agrees" if (us == "sugar" and exp == "appetitive") or (us == "bitter" and exp == "aversive") else ("opposite" if exp in ("appetitive", "aversive") else "unassigned")
        print(f"  {t:7s} LI {r.li:.2f}  pre {r.pre_hz:5.1f} -> post {r.post_hz:5.1f} Hz   PAM in {conv[t]['PAM']:3d}, PPL1 in {conv[t]['PPL1']:2d}   literature: {L.get('compartment','?')} {exp} -> {agree}")
    unlearned = resp[resp.li < args.li_min]
    print("  responding but not learning:", ", ".join(f"{t} (LI {r.li:.2f}, {lit.get(t,{}).get('memory','?')})" for t, r in unlearned.iterrows()))
    # reserve thresholds
    for g in ("PAM", "PPL1"):
        for t, r in learned.iterrows():
            s = d[(d.us == us) & (d.group == g) & (d.mbon == t)].groupby("fraction")["li"].mean()
            s0 = float(r.li); half = s[s < 0.5 * s0]
            thr = float(half.index.min()) if len(half) else np.nan
            rows.append({"us": us, "lesion": g, "mbon": t, "li_intact": s0, "threshold_fraction": thr, "n_PAM_in": conv[t]["PAM"], "n_PPL1_in": conv[t]["PPL1"],
                         **{f"li@{f:g}": float(v) for f, v in s.items()}})
res = pd.DataFrame(rows)
print("\n== reserve: smallest loss fraction at which LI falls below half of intact (NaN = never) ==")
print(res.round(2).to_string(index=False))
rnd = d[(d.group == "RND307")].groupby(["us", "mbon"])["li"].mean()
print("\nRND307 100% control, learned MBONs:", {f"{u}/{t}": round(float(rnd.get((u, t), np.nan)), 2) for u, t in zip(res.us, res.mbon)})
if args.out:
    res.to_csv(args.out, index=False); print("wrote", args.out)
