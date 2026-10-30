"""Validate the NumPy LIF against Shiu et al.'s own Brian2 output.

The reference repository ships ``results/example/sugarR.parquet``: 30 trials x
1 s of spikes from activating 21 right-hemisphere sugar GRNs at 200 Hz on the
FlyWire **630** connectivity.  We rerun the identical protocol with our
simulator on the same 630 tables and compare per-neuron rates.

Run:  python scripts/validate_vs_shiu.py --shiu-dir <clone of philshiu/Drosophila_brain_model> [--trials 3]
"""
import argparse, sys, time
from pathlib import Path
import numpy as np, pandas as pd, scipy.sparse as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.sim import LIFParams, simulate, firing_rates  # noqa: E402

NEU_SUGAR = [720575940624963786, 720575940630233916, 720575940637568838, 720575940638202345,
             720575940617000768, 720575940630797113, 720575940632889389, 720575940621754367,
             720575940621502051, 720575940640649691, 720575940639332736, 720575940616885538,
             720575940639198653, 720575940620900446, 720575940617937543, 720575940632425919,
             720575940633143833, 720575940612670570, 720575940628853239, 720575940629176663,
             720575940611875570]

ap = argparse.ArgumentParser()
ap.add_argument("--shiu-dir", required=True)
ap.add_argument("--trials", type=int, default=3)
ap.add_argument("--duration", type=float, default=1000.0)
ap.add_argument("--apl-scale", type=float, default=1.0, help="multiply APL->KC synapses (sensitivity check of the sparse regime)")
args = ap.parse_args()
d = Path(args.shiu_dir)

comp = pd.read_csv(d / "2023_03_23_completeness_630_final.csv", index_col=0)
ids = comp.index.to_numpy().astype(np.int64)
n = len(ids)
con = pd.read_parquet(d / "2023_03_23_connectivity_630_final.parquet")
W = sp.csr_matrix((con["Excitatory x Connectivity"].to_numpy(float) * 0.275,
                   (con["Presynaptic_Index"].to_numpy(), con["Postsynaptic_Index"].to_numpy())), shape=(n, n))
W.sum_duplicates()
id2i = {int(r): k for k, r in enumerate(ids)}
if args.apl_scale != 1.0:
    # 630 tables carry no annotations; APL and KCs are identified through the 783 annotation file by root id
    ann = pd.read_csv("data/raw/Supplemental_file1_neuron_annotations.tsv", sep="\t", low_memory=False)
    apl = np.array([id2i[r] for r in ann.loc[ann["cell_type"].astype(str) == "APL", "root_id"] if int(r) in id2i], dtype=np.int64)
    kcs = np.array([id2i[r] for r in ann.loc[ann["cell_class"].astype(str) == "Kenyon_Cell", "root_id"] if int(r) in id2i], dtype=np.int64)
    row_of = np.repeat(np.arange(n), np.diff(W.indptr)); km = np.zeros(n, bool); km[kcs] = True
    if apl.size < 2:   # APL root ids changed between releases: take the two neurons with most inhibitory synapses onto KCs
        inh_kc = (W.data < 0) & km[W.indices]
        cnt = np.bincount(row_of[inh_kc], minlength=n)
        apl = np.argsort(cnt)[::-1][:2].astype(np.int64)
        print(f"APL by signature: {cnt[apl].tolist()} inhibitory KC targets each")
    pm = np.zeros(n, bool); pm[apl] = True
    sel = pm[row_of] & km[W.indices]; W.data[sel] *= args.apl_scale
    print(f"APL->KC scaled x{args.apl_scale}: {len(apl)} APL, {len(kcs)} KCs matched on 630 ids, {int(sel.sum())} synapses")
sugar = np.array([id2i[r] for r in NEU_SUGAR])
print(f"630 dataset: {n} neurons, {W.nnz} connections")

ref = pd.read_parquet(d / "results/example/sugarR.parquet")
ref_rate = ref.groupby("flywire_id").size() / 30.0   # 30 trials x 1 s -> Hz
print(f"reference: {len(ref_rate)} active neurons, {ref_rate.max():.0f} Hz max")

p = LIFParams(r_poi=200.0)
rates = np.zeros(n)
t0 = time.time()
for tr in range(args.trials):
    rec = simulate(W, args.duration, p, poisson=sugar, poisson_rate=200.0, seed=tr)
    rates += firing_rates(rec) / args.trials
print(f"ours: {args.trials} trials in {time.time()-t0:.0f}s, {(rates>0).sum()} active neurons, {rates.max():.0f} Hz max")

ours = pd.Series(rates, index=ids)
both = pd.DataFrame({"ref": ref_rate, "ours": ours.reindex(ref_rate.index)}).fillna(0)
extra = ours[(ours > 0) & ~ours.index.isin(ref_rate.index)]
corr = np.corrcoef(both["ref"], both["ours"])[0, 1]
print(f"Pearson r over reference-active neurons: {corr:.3f}")
print(f"neurons active in ours but silent in reference: {len(extra)} (max {extra.max() if len(extra) else 0:.1f} Hz)")
thr = 5.0
tp = ((both.ref > thr) & (both.ours > thr)).sum(); fn = ((both.ref > thr) & (both.ours <= thr)).sum()
print(f"neurons >{thr:.0f} Hz in reference: {tp+fn}, recovered by ours: {tp}")
print(both.sort_values("ref", ascending=False).head(15).round(1).to_string())
