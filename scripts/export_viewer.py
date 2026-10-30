"""Export a whole-brain simulation for the 3-D viewer (viewer/index.html).

Simulates one stimulus on the intact brain and on a lesioned brain, bins the
spikes, and writes viewer/data.json with soma positions (FlyWire annotation
coordinates, 4x4x40 nm voxels -> um), neuron classes and per-frame spike
lists.  Serve the viewer folder with any static server:

  python scripts/export_viewer.py --apl-scale 5 --out viewer/data_sparse.json
  python scripts/export_viewer.py --apl-scale 1 --out viewer/data_attractor.json
  python -m http.server -d viewer 8000     # then open http://localhost:8000
"""
import argparse, json, sys, time
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sinek.data import load_flywire, group_indices, build_stimuli   # noqa: E402
from sinek.lesion import LesionSpec, apply_lesion, apl_scaled       # noqa: E402
from sinek.sim import simulate                                      # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--stimulus", default="odor_DM1")
ap.add_argument("--lesion", default="PPL1")
ap.add_argument("--fraction", type=float, default=1.0)
ap.add_argument("--apl-scale", type=float, default=5.0)
ap.add_argument("--duration", type=float, default=500.0)
ap.add_argument("--bin-ms", type=float, default=5.0)
ap.add_argument("--out", default="viewer/data.json")
args = ap.parse_args()

cn = apl_scaled(load_flywire(), args.apl_scale)
m = cn.meta
stim = {s.name: s for s in build_stimuli(cn)}[args.stimulus]
groups = group_indices(cn)
W_les, hit = apply_lesion(cn, groups, LesionSpec({args.lesion: args.fraction}, seed=0), keep_pattern=True)
lesioned = np.concatenate([np.asarray(v) for v in hit.values()]) if hit else np.empty(0, int)

# positions: voxel (4,4,40 nm) -> um, centred
pos = m[["pos_x", "pos_y", "pos_z"]].to_numpy(float) * np.array([0.004, 0.004, 0.04])
ok = ~np.isnan(pos).any(1)
pos[~ok] = np.nanmedian(pos[ok], axis=0)
pos -= pos[ok].mean(0)
pos_i = np.round(pos * 2).astype(np.int16)       # 0.5 um resolution

classes = {"Kenyon_Cell": "KC", "DAN": "DAN", "MBON": "MBON"}
cls = np.full(cn.n, 0, np.int8)
cell_class = m["cell_class"].astype(str).to_numpy(); ctype = m["cell_type"].astype(str).to_numpy()
sc = m["super_class"].astype(str).to_numpy()
names = ["other", "Kenyon cell", "dopaminergic (DAN)", "MBON", "sensory", "descending", "stimulated"]
cls[cell_class == "Kenyon_Cell"] = 1
cls[cell_class == "DAN"] = 2
cls[m["cell_type"].astype(str).str.startswith("MBON").to_numpy()] = 3
cls[sc == "sensory"] = 4
cls[sc == "descending"] = 5
cls[np.asarray(stim.targets)] = 6

nb = int(round(args.duration / args.bin_ms))
def frames(rec):
    b = np.minimum((rec.times / args.bin_ms).astype(int), nb - 1)
    out = [[] for _ in range(nb)]
    for k in range(nb):
        out[k] = np.unique(rec.ids[b == k]).astype(int).tolist()
    return out

runs = {}
for label, W in (("intact", cn.W), (f"{args.lesion} {int(args.fraction*100)}% removed", W_les)):
    t0 = time.time()
    rec = simulate(W, args.duration, poisson=stim.targets, poisson_rate=stim.rate_hz, seed=0)
    runs[label] = {"frames": frames(rec), "n_spikes": int(rec.times.size),
                   "n_active": int(np.unique(rec.ids).size)}
    print(f"{label}: {rec.times.size} spikes, {np.unique(rec.ids).size} active neurons [{time.time()-t0:.0f}s]", flush=True)

out = {"meta": {"connectome": cn.name, "n": int(cn.n), "stimulus": args.stimulus, "rate_hz": stim.rate_hz,
                "duration_ms": args.duration, "bin_ms": args.bin_ms, "apl_scale": args.apl_scale,
                "lesion": args.lesion, "fraction": args.fraction, "n_lesioned": int(lesioned.size),
                "pos_scale_um": 0.5},
       "class_names": names, "cls": cls.tolist(),
       "pos": pos_i.ravel().tolist(), "lesioned": lesioned.astype(int).tolist(), "runs": runs}
Path(args.out).parent.mkdir(parents=True, exist_ok=True)
json.dump(out, open(args.out, "w"), separators=(",", ":"))
print("wrote", args.out, f"{Path(args.out).stat().st_size/1e6:.1f} MB")
