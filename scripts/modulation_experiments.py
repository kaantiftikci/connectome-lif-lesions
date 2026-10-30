"""Phase 3 experiments for the dopamine-modulation layer.

  check      MBON odour responses: reference LIF vs modulated network (no DAN drive)
  condition  grid-fit kappa/eta so that pairing odour with a compartment's DANs
             depresses that compartment's MBON by ~50% (Hige 2015 / Owald 2015
             range) with little off-target change
  curves     progressive PPL1/PAM lesions with modulation on, full battery

Run:  python scripts/modulation_experiments.py check|condition|curves [--procs 3]
"""
import argparse, json, sys, time
import multiprocessing as mp
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire, group_indices, build_stimuli, readout_groups   # noqa: E402
from sinek.lesion import LesionSpec, apply_lesion, apl_scaled                        # noqa: E402
from sinek.sim import simulate, firing_rates                                         # noqa: E402
from sinek.neuromod import ModulationParams, ModulatedNetwork, simulate_modulated   # noqa: E402
from sinek.readout import phenotype_names                                            # noqa: E402

_G = {}


def mbon_rates(rec, cn, t_start):
    r = firing_rates(rec, t_start)
    mb = cn.select(cell_type__startswith="MBON")
    return pd.Series(r[mb], index=cn.meta.loc[mb, "cell_type"].astype(str).values).groupby(level=0).mean()


def cmd_check(cn, args):
    stim = {s.name: s for s in build_stimuli(cn)}
    odor = stim["odor_DM1"].targets
    ref = mbon_rates(simulate(cn.W, 600.0, poisson=odor, seed=0), cn, 200.0)
    for kappa in (0.0, 0.03):
        net = ModulatedNetwork(cn, ModulationParams(kappa=kappa, alpha_fast=0.0))
        rec, _ = simulate_modulated(net, 600.0, poisson=odor, seed=0)
        mod = mbon_rates(rec, cn, 200.0)
        d = pd.DataFrame({"reference_LIF": ref, f"modulated_k{kappa}": mod}).round(1)
        print(f"\nkappa={kappa}: MBON odour responses (Hz), top 15 by reference:")
        print(d.sort_values("reference_LIF", ascending=False).head(15).to_string())
        chg = (mod - ref).abs()
        print(f"  MBON types with |change| > 2 Hz: {(chg > 2).sum()} / {len(chg)}")


def _condition_job(a):
    kappa, eta, dan_group, target_mbon = a
    cn = _G["cn"]; stim = _G["stim"]
    odor = {int(i): 150.0 for i in stim["odor_DM1"].targets}
    dans = _G["groups"][dan_group]
    pair = dict(odor); pair.update({int(i): 100.0 for i in dans})
    net0 = ModulatedNetwork(cn, ModulationParams(kappa=0.0, eta=0.0, alpha_fast=0.0))
    _, rb = simulate_modulated(net0, 600.0, poisson=odor, seed=0)   # tonic DAN level, gain off
    net = ModulatedNetwork(cn, ModulationParams(kappa=kappa, eta=eta, alpha_fast=0.0))
    net.set_baseline(rb)
    pre_rec, rb = simulate_modulated(net, 600.0, poisson=odor, seed=0, rbar=rb)
    pre = mbon_rates(pre_rec, cn, 200.0)
    _, rb = simulate_modulated(net, 1000.0, poisson=pair, seed=1, plastic=True, rbar=rb)
    _, rb = simulate_modulated(net, 400.0, poisson=None, seed=2, rbar=rb)      # rest: dopamine decays
    post_rec, _ = simulate_modulated(net, 600.0, poisson=odor, seed=3, rbar=rb)
    post = mbon_rates(post_rec, cn, 200.0)
    responders = pre[pre > 2.0].index
    dep = 1.0 - post[target_mbon] / pre[target_mbon] if pre.get(target_mbon, 0) > 0 else np.nan
    others = [m for m in responders if m != target_mbon]
    off = float(np.mean([abs(1.0 - post[m] / pre[m]) for m in others])) if others else 0.0
    return {"kappa": kappa, "eta": eta, "dan_group": dan_group, "target": target_mbon,
            "pre_target_hz": float(pre.get(target_mbon, 0)), "post_target_hz": float(post.get(target_mbon, 0)),
            "depression": float(dep), "off_target_change": off, "n_responders": int(len(responders))}


def cmd_condition(cn, args):
    _G.update(cn=cn, stim={s.name: s for s in build_stimuli(cn)}, groups=group_indices(cn, {"PPL101": {"cell_type": "PPL101"}, "PAM11": {"cell_type": "PAM11"}}))
    # Compartment pairs chosen from connectivity: PPL101 is MBON11's strongest DAN input (124 mV, aversive output),
    # PAM11 is MBON07's (98-113 mV, appetitive output). Greek compartment names deliberately not asserted.
    jobs = [(k, e, g, t) for g, t in (("PPL101", "MBON11"), ("PAM11", "MBON07"))
            for k in (0.0, 0.003, 0.01, 0.03) for e in (0.0, 3e-5, 1e-4, 3e-4)]
    rows = []
    t0 = time.time()
    with mp.get_context("fork").Pool(args.procs) as pool:
        for i, r in enumerate(pool.imap_unordered(_condition_job, jobs)):
            rows.append(r); print(f"{i+1}/{len(jobs)} {r['dan_group']} k={r['kappa']} eta={r['eta']}: pre {r['pre_target_hz']:.1f} post {r['post_target_hz']:.1f} Hz, depression {r['depression']:.2f}, off-target {r['off_target_change']:.2f} [{time.time()-t0:.0f}s]", flush=True)
    df = pd.DataFrame(rows).sort_values(["dan_group", "kappa", "eta"])
    Path("results").mkdir(exist_ok=True); df.to_csv("results/conditioning_grid.csv", index=False)
    # choose: depression closest to 0.5 with off-target < 0.15, averaged over both compartments
    df["score"] = (df["depression"] - 0.5).abs() + 2.0 * np.clip(df["off_target_change"] - 0.15, 0, None)
    best = df.groupby(["kappa", "eta"])["score"].mean().idxmin()
    print("\nbest (kappa, eta):", best)
    json.dump({"kappa": best[0], "eta": best[1]}, open("results/modulation_fit.json", "w"))
    print(df.round(3).to_string())


def _curve_job(a):
    group, frac, lseed, sseed = a
    cn = _G["cn"]
    W, hit = apply_lesion(cn, _G["groups"], LesionSpec({group: frac}, seed=lseed), keep_pattern=True)
    feats = []
    for s in _G["stim"]:
        net = ModulatedNetwork(cn, _G["mp"], W=W)
        net.set_baseline(_G["baseline"][s.name])
        rec, _ = simulate_modulated(net, 500.0, poisson=s.targets, poisson_rate=s.rate_hz, seed=sseed, rbar=_G["baseline"][s.name])
        r = firing_rates(rec, 100.0)
        feats.append(np.log1p(np.array([r[idx].mean() if idx.size else 0.0 for idx in _G["readouts"].values()])))
    return group, frac, lseed, sseed, sum(len(v) for v in hit.values()), np.concatenate(feats)


def cmd_curves(cn, args):
    fit = json.load(open("results/modulation_fit.json")) if Path("results/modulation_fit.json").exists() else {"kappa": 0.03, "eta": 0.0}
    mpar = ModulationParams(kappa=fit["kappa"], eta=0.0, alpha_fast=0.0)   # acute gain only; no training during the battery
    print("modulation params:", mpar)
    _G.update(cn=cn, groups=_add_controls(cn, group_indices(cn), args.controls), stim=build_stimuli(cn), readouts=readout_groups(cn), mp=mpar)
    # tonic DAN baseline per stimulus from the intact modulated network
    base = {}
    mpar0 = ModulationParams(kappa=0.0, eta=0.0, alpha_fast=mpar.alpha_fast)   # tonic level with the gain off
    for s_ in _G["stim"]:
        net = ModulatedNetwork(cn, mpar0)
        _, rb = simulate_modulated(net, 400.0, poisson=s_.targets, poisson_rate=s_.rate_hz, seed=0)
        base[s_.name] = rb
    _G["baseline"] = base
    print("baselines measured", flush=True)
    names = phenotype_names(_G["stim"], _G["readouts"])
    jobs = [(g, f, ls, ss) for g in args.groups for f in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
            for ls in range(args.lesion_seeds if f > 0 else 1) for ss in range(args.sim_seeds)]
    rows = []; t0 = time.time()
    with mp.get_context("fork").Pool(args.procs) as pool:
        for i, (g, f, ls, ss, n_hit, x) in enumerate(pool.imap_unordered(_curve_job, jobs)):
            rows.extend({"group": g, "fraction": f, "lesion_seed": ls, "sim_seed": ss, "n_lesioned": n_hit, "feature": nm, "value": float(v)} for nm, v in zip(names, x))
            pd.DataFrame(rows).to_csv(args.out, index=False)
            print(f"{i+1}/{len(jobs)} {g} {f} order {ls} seed {ss} [{time.time()-t0:.0f}s]", flush=True)
    print("wrote", args.out)


def _add_controls(cn, groups, sizes):
    """Size-matched random central-neuron controls (non-DA, non-KC), same seed as progressive_curve.py."""
    m = cn.meta
    pool = m.loc[(m["super_class"] == "central") & (~m["cell_class"].isin(["DAN", "Kenyon_Cell"])), "idx"].to_numpy()
    rng = np.random.default_rng(12345)
    for size in sizes:
        groups[f"RND{size}"] = np.sort(rng.choice(pool, size=size, replace=False))
    return groups


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["check", "condition", "curves"])
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--groups", nargs="+", default=["PPL1", "PAM"])
    ap.add_argument("--controls", nargs="*", type=int, default=[])
    ap.add_argument("--lesion-seeds", type=int, default=3)
    ap.add_argument("--sim-seeds", type=int, default=2)
    ap.add_argument("--apl-scale", type=float, default=1.0)
    ap.add_argument("--out", default="results/progressive_modulated.csv")
    args = ap.parse_args()
    cn = apl_scaled(load_flywire(), args.apl_scale)
    {"check": cmd_check, "condition": cmd_condition, "curves": cmd_curves}[args.cmd](cn, args)
