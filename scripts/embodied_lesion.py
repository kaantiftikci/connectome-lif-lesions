"""Phase 2: lesion -> descending-neuron rates -> NeuroMechFly walking.

For each condition (intact, full and partial dopaminergic lesions, controls)
run the DN-recruiting stimuli (wind/gravity mechanosensors, head bristles),
average DN rates per side over seeds, convert to a drive relative to the
intact brain, and run the body model on flat and tilted ground.

Run:  MUJOCO_GL= python scripts/embodied_lesion.py --out results/embodied.csv
"""
import argparse, sys, time
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire, group_indices, build_stimuli          # noqa: E402
from sinek.lesion import LesionSpec, apply_lesion                           # noqa: E402
from sinek.sim import simulate, firing_rates                                # noqa: E402
from sinek.embodied import descending_sides, descending_rates, descending_drive, LOCOMOTOR_DN_TYPES, walk  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--conditions", nargs="+", default=["intact", "PPL1:1.0", "PPL1:0.6", "PAM:1.0", "KC:1.0", "RND307:1.0", "RND16:1.0"])
ap.add_argument("--stimuli", nargs="+", default=["wind_gravity", "head_bristle"])
ap.add_argument("--seeds", type=int, default=3)
ap.add_argument("--brain-ms", type=float, default=500.0)
ap.add_argument("--walk-s", type=float, default=1.0)
ap.add_argument("--tilts", nargs="+", type=float, default=[0.0, 60.0])
ap.add_argument("--out", default="results/embodied.csv")
args = ap.parse_args()

cn = load_flywire()
groups = group_indices(cn)
m = cn.meta
pool = m.loc[(m["super_class"] == "central") & (~m["cell_class"].isin(["DAN", "Kenyon_Cell"])), "idx"].to_numpy()
rng = np.random.default_rng(12345)
for size in (16, 307):
    groups[f"RND{size}"] = np.sort(rng.choice(pool, size=size, replace=False))   # same seed as progressive_curve.py
stim = {s.name: s for s in build_stimuli(cn)}
sides_all = descending_sides(cn)
sides_loc = descending_sides(cn, LOCOMOTOR_DN_TYPES)
print(f"DNs: all L/R {len(sides_all['left'])}/{len(sides_all['right'])}, locomotor L/R {len(sides_loc['left'])}/{len(sides_loc['right'])}")

def dn_rates(W, stim_name):
    acc_all = np.zeros(2); acc_loc = np.zeros(2)
    for s in range(args.seeds):
        rec = simulate(W, args.brain_ms, poisson=stim[stim_name].targets, poisson_rate=stim[stim_name].rate_hz, seed=500 + s)
        r = firing_rates(rec, t_start=100.0)
        acc_all += descending_rates(r, sides_all); acc_loc += descending_rates(r, sides_loc)
    return acc_all / args.seeds, acc_loc / args.seeds

rows = []
intact = {}
t0 = time.time()
for cond in args.conditions:
    if cond == "intact":
        W = cn.W
    else:
        g, f = cond.split(":")
        W, _ = apply_lesion(cn, groups, LesionSpec({g: float(f)}))
    for st in args.stimuli:
        r_all, r_loc = dn_rates(W, st)
        if cond == "intact":
            intact[st] = (r_all, r_loc)
        d_all = descending_drive(r_all, intact[st][0]); d_loc = descending_drive(r_loc, intact[st][1])
        for readout, drive, rates in (("all_DN", d_all, r_all), ("locomotor_DN", d_loc, r_loc)):
            for tilt in args.tilts:
                w = walk(drive, duration=args.walk_s, tilt_deg=tilt, seed=0)
                rows.append({"condition": cond, "stimulus": st, "readout": readout, "dn_rate_L": rates[0], "dn_rate_R": rates[1],
                             **w})
                print(f"{cond:10s} {st:13s} {readout:12s} tilt {tilt:4.0f}: DN L/R {rates[0]:.2f}/{rates[1]:.2f} Hz, "
                      f"drive {drive[0]:.2f}/{drive[1]:.2f}, forward {w['forward_mm']:.2f} mm, fell={w['fell']}  [{time.time()-t0:.0f}s]", flush=True)
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(rows).to_csv(args.out, index=False)
print("wrote", args.out)
