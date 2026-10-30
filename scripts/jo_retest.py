"""Re-test the neuron-loss protocol of Jo (arXiv 2610.19153, "Simulating
Alzheimer's amyloid-like pathology on a fly CNS connectome") on the FlyWire
female brain in two operating regimes.

Jo's rule: each non-sensory neuron is removed with probability
0.5 * s * v_i, where v_i is the neuron's percentile rank by number of
synaptic contacts (hub map), the same values shuffled (shuffled map) or
reversed (antihub map).  At s = 0.5 about 12% of neurons go.  Readout: odour-
evoked whole-brain spikes relative to healthy.  Jo reports 31% (hub), 47%
(shuffled), 93% (antihub) of healthy, antihub/hub ratio 3.0, on MaleCNS with
PNs driven directly.

Here: same rule, same s, 3 maps x R replicates, in the attractor regime
(APL x1, the default of the Shiu model) and in the sparse regime (APL x5),
with odour = ORN_DM1 at 150 Hz.  Whole-brain spikes, KC fraction active and
the full phenotype vector are recorded, plus the fraction of contacts lost.

Run:  python scripts/jo_retest.py --s 0.5 --reps 8 --procs 3 --out results/jo_retest.csv
"""
import argparse, sys, time
import multiprocessing as mp
from pathlib import Path
import numpy as np, pandas as pd
import scipy.sparse as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire, build_stimuli, readout_groups      # noqa: E402
from sinek.lesion import apl_scaled                                     # noqa: E402
from sinek.sim import simulate, firing_rates                            # noqa: E402

_G = {}


def contacts(cn):
    """number of synaptic contacts per neuron (in + out), from synapse counts"""
    W = cn.W
    cnt = (abs(W) / 0.275).astype(np.int64)
    return np.asarray(cnt.sum(1)).ravel() + np.asarray(cnt.sum(0)).ravel()


def vulnerability_maps(cn, seed=0):
    c = contacts(cn)
    rank = (pd.Series(c).rank(method="average").to_numpy() - 1) / (cn.n - 1)   # percentile 0..1
    rng = np.random.default_rng(seed)
    return {"hub": rank, "shuffled": rng.permutation(rank), "antihub": 1.0 - rank}


def _job(a):
    regime, mapname, rep, s = a
    cn = _G["cn"][regime]; v = _G["maps"][mapname]
    rng = np.random.default_rng(1000 * rep + 7)
    exempt = (cn.meta["super_class"].astype(str) == "sensory").to_numpy()
    remove = (rng.random(cn.n) < 0.5 * s * v) & ~exempt
    W = cn.W.copy()
    vth_off = None
    if _G.get("full"):
        # synapse loss: each outgoing contact of neuron i lost with probability 0.6*s*v_i
        row_of = np.repeat(np.arange(cn.n), np.diff(W.indptr))
        p_loss = np.where(exempt, 0.0, 0.6 * s * v)[row_of]
        contacts = np.rint(np.abs(W.data) / 0.275).astype(np.int64)
        surv = rng.binomial(contacts, 1.0 - p_loss)
        W.data = np.sign(W.data) * surv * 0.275
        # threshold shift: lowered by up to 2 mV
        vth_off = np.where(exempt, 0.0, -2.0 * s * v)
    nnz_before = int((W.data != 0).sum())
    d = sp.diags((~remove).astype(np.float32))
    W = (d @ W @ d).tocsr(); W.eliminate_zeros()
    lost = 1.0 - (np.abs(W.data) / 0.275).sum() / (np.abs(cn.W.data) / 0.275).sum()
    stim = _G["stim"]; odor = stim["odor_DM1"]
    rec = simulate(W, 500.0, poisson=odor.targets, poisson_rate=odor.rate_hz, seed=rep, v_th_offset=vth_off)
    r = firing_rates(rec, 100.0)
    kc = _G["kc"]
    feats = np.log1p(np.array([r[idx].mean() if idx.size else 0.0 for idx in _G["readouts"].values()]))
    return {"regime": regime, "map": mapname, "rep": rep, "s": s, "n_removed": int(remove.sum()),
            "frac_removed": float(remove.mean()), "frac_contacts_lost": float(lost),
            "spikes_odor": int((rec.times >= 100.0).sum()), "n_active": int((r > 5).sum()),
            "kc_frac": float((r[kc] > 5).mean()), "mbon_hz": float(r[_G["mbon"]].mean()),
            "feats": feats.tolist()}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--s", type=float, default=0.5)
    ap.add_argument("--reps", type=int, default=8)
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--out", default="results/jo_retest.csv")
    ap.add_argument("--full", action="store_true", help="also apply synapse loss (p=0.6 s v per contact) and threshold shift (-2 s v mV)")
    args = ap.parse_args()
    _G["full"] = args.full
    base = load_flywire()
    _G["cn"] = {"attractor": base, "sparse": apl_scaled(base, 5.0)}
    _G["maps"] = vulnerability_maps(base)
    _G["stim"] = {s_.name: s_ for s_ in build_stimuli(base)}
    _G["readouts"] = readout_groups(base)
    _G["kc"] = base.select(cell_class="Kenyon_Cell"); _G["mbon"] = base.select(cell_type__startswith="MBON")
    for k, v in _G["maps"].items():
        print(f"{k}: expected fraction removed at s={args.s}: {(0.5*args.s*v).mean():.3f}")
    jobs = [(reg, mp_, rep, args.s) for reg in ("attractor", "sparse") for mp_ in ("hub", "shuffled", "antihub") for rep in range(args.reps)]
    jobs += [(reg, "healthy", rep, 0.0) for reg in ("attractor", "sparse") for rep in range(3)]
    _G["maps"]["healthy"] = np.zeros(base.n)
    rows, t0 = [], time.time()
    with mp.get_context("fork").Pool(args.procs) as pool:
        for i, row in enumerate(pool.imap_unordered(_job, jobs)):
            rows.append(row); pd.DataFrame(rows).to_csv(args.out, index=False)
            print(f"{i+1}/{len(jobs)} {row['regime']} {row['map']} rep {row['rep']}: removed {row['frac_removed']:.3f}, contacts lost {row['frac_contacts_lost']:.3f}, spikes {row['spikes_odor']}, KC {row['kc_frac']:.3f} [{time.time()-t0:.0f}s]", flush=True)
    print("wrote", args.out)
