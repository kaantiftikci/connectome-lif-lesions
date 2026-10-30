"""Why do reinforcers not reach the dopaminergic neurons, and what is the
smallest change that makes them?

  rates   : US rate / set-size sweep in the sparse regime -> DAN cluster rates
  paths   : where along GRN -> ... -> PAM/PPL1 does activity die (hop analysis)
  boost   : scale one hop of the pathway by k and find the smallest k that makes
            the DAN cluster respond; report the off-target cost

Run:  python scripts/reinforcer_path.py rates --apl-scale 5
      python scripts/reinforcer_path.py paths --apl-scale 5
      python scripts/reinforcer_path.py boost --apl-scale 5 --us sugar --target PAM
"""
import argparse, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire, build_stimuli, group_indices        # noqa: E402
from sinek.data.flywire import Connectome                                 # noqa: E402
from sinek.lesion import apl_scaled, scale_edges                          # noqa: E402
from sinek.sim import simulate, firing_rates, LIFParams                   # noqa: E402

DAN = {"PAM": "PAM", "PPL1": "PPL1", "PPL2": "PPL2", "PPM1": "PPM1"}


def dan_idx(cn):
    return {k: cn.select(cell_type__startswith=v) for k, v in DAN.items()}


def dan_report(r, dix):
    return {k: (round(float(r[v].mean()), 1), round(float((r[v] > 5).mean()), 2)) for k, v in dix.items()}


def cmd_rates(cn, args):
    dix = dan_idx(cn); m = cn.meta
    sets = {"sugar32": cn.select(cell_sub_class="sugar"), "water": cn.select(cell_sub_class="water"),
            "bitter": cn.select(cell_sub_class="bitter"),
            "sugar+lowsalt57": m.loc[m["cell_sub_class"].astype(str).str.startswith("sugar"), "idx"].to_numpy(),
            "all_gustatory": m.loc[m["cell_class"].astype(str).str.contains("gustatory", case=False), "idx"].to_numpy()}
    rows = []
    for name, idx in sets.items():
        for rate in args.rates:
            t0 = time.time()
            rec = simulate(cn.W, 500.0, poisson=idx, poisson_rate=rate, seed=0)
            r = firing_rates(rec, 100.0)
            rep = dan_report(r, dix)
            rows.append({"set": name, "n_in": int(idx.size), "rate_hz": rate, "n_active": int((r > 5).sum()),
                         **{f"{k}_hz": v[0] for k, v in rep.items()}, **{f"{k}_frac": v[1] for k, v in rep.items()}})
            print(f"{name:16s} n={idx.size:3d} {rate:5.0f} Hz: active {int((r>5).sum()):6d}  DAN {rep} [{time.time()-t0:.0f}s]", flush=True)
    pd.DataFrame(rows).to_csv(args.out, index=False); print("wrote", args.out)


def cmd_paths(cn, args):
    """Hop analysis: summed excitatory input from the US set at hop 1, and the
    strongest hop-1 -> DAN edges; then simulate and see which hop fires."""
    dix = dan_idx(cn); m = cn.meta
    us = cn.select(cell_sub_class=args.us)
    W = cn.W
    h1 = np.asarray(W[us].sum(0)).ravel()                    # mV summed from all US neurons
    cand = np.where(h1 > 0)[0]
    rec = simulate(W, 500.0, poisson=us, poisson_rate=args.us_rate, seed=0)
    r = firing_rates(rec, 100.0)
    print(f"US={args.us} n={us.size} at {args.us_rate} Hz: {int((r>5).sum())} neurons >5 Hz; hop-1 targets {cand.size}, of which firing >5 Hz: {int((r[cand]>5).sum())}")
    top = cand[np.argsort(h1[cand])[::-1][:25]]
    print("\nstrongest hop-1 targets (summed input mV, rate Hz, cell_type):")
    for i in top:
        print(f"  {h1[i]:7.1f} mV  {r[i]:6.1f} Hz  {m.at[i,'cell_type']}  ({m.at[i,'cell_class']}, {m.at[i,'super_class']})")
    for tname in ("PAM", "PPL1"):
        T = dix[tname]
        W2 = W[cand][:, T]                                   # hop-1 -> DAN
        in2 = np.asarray(W2.sum(1)).ravel()                  # total mV each hop-1 neuron sends to the DAN cluster
        order = np.argsort(h1[cand] * np.clip(in2, 0, None))[::-1][:15]
        print(f"\nbest 2-hop relays into {tname} (h1 mV, ->{tname} mV, rate Hz, cell_type):")
        for j in order:
            i = cand[j]
            if in2[j] <= 0: break
            print(f"  {h1[i]:7.1f}  {in2[j]:7.1f}  {r[i]:6.1f}  {m.at[i,'cell_type']}")
        direct = np.asarray(W[us][:, T].sum(0)).ravel()
        print(f"  direct US->{tname} input: max {direct.max():.1f} mV on one neuron, {int((direct>0).sum())}/{T.size} receive any")
        print(f"  {tname} rate under US: mean {r[T].mean():.2f} Hz, {int((r[T]>5).sum())}/{T.size} > 5 Hz")


def active_relays(cn, us, T, rate=150.0, n_relays=20, seed=0):
    """Neurons that receive rate-weighted input from the network the US activates
    and project onto the target DAN cluster, ranked by input x output."""
    r = firing_rates(simulate(cn.W, 500.0, poisson=us, poisson_rate=rate, seed=seed), 100.0)
    A = np.where(r > 5)[0]
    drive = np.asarray(cn.W[A].multiply(r[A][:, None] / 100.0).sum(0)).ravel()
    toT = np.asarray(cn.W[:, T].sum(1)).ravel()
    proj = np.where((toT > 0) & (drive > 0))[0]
    proj = proj[~np.isin(proj, T)]
    order = proj[np.argsort(drive[proj] * toT[proj])[::-1][:n_relays]]
    return A, order, r


def cmd_boost(cn, args):
    """Scale the hop into the relays (active set -> relays), the hop out of them
    (relays -> target DANs) or both by k; smallest k that makes the target
    respond at a physiological US rate (150 Hz), and the off-target cost."""
    dix = dan_idx(cn); T = dix[args.target]; m = cn.meta
    us = cn.select(cell_sub_class=args.us)
    A, relays, r0 = active_relays(cn, us, T, n_relays=args.n_relays)
    print(f"US={args.us}: {A.size} active neurons; {relays.size} relays onto {args.target}:",
          sorted(set(m.loc[relays, "cell_type"].astype(str))))
    odor = {s.name: s for s in build_stimuli(cn)}["odor_DM1"]
    kc = cn.select(cell_class="Kenyon_Cell")
    r_ref = firing_rates(simulate(cn.W, 500.0, poisson=odor.targets, poisson_rate=odor.rate_hz, seed=0), 100.0)
    rows = []
    for hop in args.hops:
        for k in args.k:
            W = cn.W
            if hop in ("in", "both"):
                W = scale_edges(Connectome(ids=cn.ids, W=W, meta=cn.meta, name=cn.name), A, relays, k)
            if hop in ("out", "both"):
                W = scale_edges(Connectome(ids=cn.ids, W=W, meta=cn.meta, name=cn.name), relays, T, k)
            r_us = firing_rates(simulate(W, 500.0, poisson=us, poisson_rate=150.0, seed=0), 100.0)
            r_od = firing_rates(simulate(W, 500.0, poisson=odor.targets, poisson_rate=odor.rate_hz, seed=0), 100.0)
            row = {"us": args.us, "target": args.target, "hop": hop, "k": k,
                   "target_hz": float(r_us[T].mean()), "target_frac": float((r_us[T] > 5).mean()),
                   "relay_hz": float(r_us[relays].mean()), "n_active_us": int((r_us > 5).sum()),
                   "other_dan_hz": {g: round(float(r_us[v].mean()), 1) for g, v in dix.items() if g != args.target},
                   "odor_kc_frac": float((r_od[kc] > 5).mean()), "odor_n_active": int((r_od > 5).sum()),
                   "odor_n_active_ref": int((r_ref > 5).sum()),
                   "odor_lograte_l2": float(np.linalg.norm(np.log1p(r_od) - np.log1p(r_ref)))}
            rows.append(row); print(row, flush=True)
    pd.DataFrame(rows).to_csv(args.out, index=False); print("wrote", args.out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["rates", "paths", "boost"])
    ap.add_argument("--apl-scale", type=float, default=5.0)
    ap.add_argument("--rates", nargs="*", type=float, default=[150, 300, 600, 1000])
    ap.add_argument("--us", default="sugar"); ap.add_argument("--us-rate", type=float, default=150.0)
    ap.add_argument("--target", default="PAM")
    ap.add_argument("--k", nargs="*", type=float, default=[1, 2, 4, 8, 16])
    ap.add_argument("--hops", nargs="*", default=["in", "out", "both"])
    ap.add_argument("--n-relays", type=int, default=20)
    ap.add_argument("--out", default="results/reinforcer_rates.csv")
    args = ap.parse_args()
    cn = apl_scaled(load_flywire(), args.apl_scale)
    {"rates": cmd_rates, "paths": cmd_paths, "boost": cmd_boost}[args.cmd](cn, args)
