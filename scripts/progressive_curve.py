"""Silent-reserve curves with replication: progressive loss of each group under
several lesion orders (which neurons go first) and simulation seeds, plus
size-matched random controls.  Parallel over forked workers that share the
connectome.

Output: results/progressive.csv, one row per (group, fraction, lesion_seed,
sim_seed, feature).  Summarise with scripts/analyze_progressive.py.

Run:  python scripts/progressive_curve.py --groups PPL1 PAM PPL2 PPM1 --controls 16 307 \
          --lesion-seeds 5 --sim-seeds 2 --procs 4
"""
import argparse, sys, time
import multiprocessing as mp
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire, group_indices, build_stimuli, readout_groups   # noqa: E402
from sinek.lesion import LesionSpec, apply_lesion                                        # noqa: E402
from sinek.readout import Stimulus, phenotype_vector, phenotype_names                    # noqa: E402

_G = {}


def _job(args):
    group, frac, lseed, sseed = args
    W, hit = apply_lesion(_G["cn"], _G["groups"], LesionSpec({group: frac}, mode=_G["mode"], seed=lseed))
    x = phenotype_vector(W, _G["stim"], _G["readouts"], duration=_G["duration"], seed=sseed)
    return group, frac, lseed, sseed, sum(len(v) for v in hit.values()), x


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--groups", nargs="+", default=["PPL1", "PAM", "PPL2", "PPM1"])
    ap.add_argument("--controls", nargs="*", type=int, default=[16, 307],
                    help="sizes of random central-neuron control groups (non-DA, non-KC)")
    ap.add_argument("--fractions", nargs="+", type=float, default=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ap.add_argument("--lesion-seeds", type=int, default=5)
    ap.add_argument("--sim-seeds", type=int, default=2)
    ap.add_argument("--mode", default="remove")
    ap.add_argument("--duration", type=float, default=500.0)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--out", default="results/progressive.csv")
    ap.add_argument("--resume", action="store_true", help="skip (group, fraction, seeds) already present in --out")
    ap.add_argument("--sex", choices=["female", "male"], default="female")
    ap.add_argument("--count-scale", type=float, default=0.581, help="male synapse-count scale to align with FlyWire (MaleCNS release note)")
    ap.add_argument("--odor-rate", type=float, default=None, help="override ORN_DM1 drive rate (Hz) in both sexes")
    ap.add_argument("--apl-scale", type=float, default=1.0,
                    help="multiply APL->Kenyon-cell synapses (5.0 gives ~4%% KCs active under odour instead of 75%%)")
    args = ap.parse_args()

    if args.sex == "male":
        from sinek.data.malecns import load_malecns_flat, map_stimuli_from_female
        female = load_flywire()
        cn = load_malecns_flat(count_scale=args.count_scale)
        stim = map_stimuli_from_female(cn, female)
        del female
    else:
        cn = load_flywire()
        stim = build_stimuli(cn)
    if args.odor_rate is not None:
        for s_ in stim:
            if s_.name == "odor_DM1":
                s_.rate_hz = args.odor_rate
    if args.apl_scale != 1.0:
        from sinek.lesion import scale_edges
        from sinek.data.flywire import Connectome
        W_apl = scale_edges(cn, cn.select(cell_type="APL"), cn.select(cell_class="Kenyon_Cell"), args.apl_scale)
        cn = Connectome(ids=cn.ids, W=W_apl, meta=cn.meta, name=f"{cn.name}_apl{args.apl_scale}")
    groups = group_indices(cn)
    m = cn.meta
    pool_mask = (m["super_class"] == "central") & (m["cell_class"] != "DAN") & (m["cell_class"] != "Kenyon_Cell")
    pool_idx = m.loc[pool_mask, "idx"].to_numpy()
    rng = np.random.default_rng(12345)
    for size in args.controls:
        groups[f"RND{size}"] = np.sort(rng.choice(pool_idx, size=size, replace=False))
    _G.update(cn=cn, groups=groups, mode=args.mode, duration=args.duration,
              stim=stim, readouts=readout_groups(cn))
    names = phenotype_names(_G["stim"], _G["readouts"])
    all_groups = list(args.groups) + [f"RND{s}" for s in args.controls]

    jobs = []
    for g in all_groups:
        for f in args.fractions:
            for ls in range(args.lesion_seeds if f > 0 else 1):
                for ss in range(args.sim_seeds):
                    jobs.append((g, f, ls, ss))
    rows = []
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    if args.resume and out.exists():
        prev = pd.read_csv(out)
        done = set(map(tuple, prev[["group", "fraction", "lesion_seed", "sim_seed"]].drop_duplicates().itertuples(index=False)))
        jobs = [j for j in jobs if (j[0], float(j[1]), j[2], j[3]) not in done]
        rows = prev.to_dict("records")
        print(f"resuming: {len(done)} simulations already in {out}, {len(jobs)} to go", flush=True)
    print(f"{cn.n} neurons; {len(names)} features; {len(jobs)} simulations on {args.procs} workers", flush=True)
    t0 = time.time()
    with mp.get_context("fork").Pool(args.procs) as pool:
        for i, (g, f, ls, ss, n_hit, x) in enumerate(pool.imap_unordered(_job, jobs, chunksize=1)):
            rows.extend({"group": g, "fraction": f, "lesion_seed": ls, "sim_seed": ss, "n_lesioned": n_hit,
                         "feature": nm, "value": float(v)} for nm, v in zip(names, x))
            if (i + 1) % 10 == 0 or i + 1 == len(jobs):
                pd.DataFrame(rows).to_csv(out, index=False)
                print(f"{i+1}/{len(jobs)} in {time.time()-t0:.0f}s", flush=True)
    print("wrote", out)
