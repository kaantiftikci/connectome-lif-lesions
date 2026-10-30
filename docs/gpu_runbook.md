# Runbook: large sweeps on a GPU, a cloud box, or an Apple-silicon Mac

The surrogate/NPE dataset (`scripts/run_lesion_sweep.py`) is the only part
of the project whose cost scales with the number of simulations: one
phenotype vector = 6 stimuli x 500 ms whole-brain LIF runs (~140k neurons,
15 M synapses). Everything else (progressive curves, noise floor, embodied
readout) runs in minutes to an hour on a laptop.

## Measured throughput (phenotype vectors per hour)

| machine                         | backend           | procs | throughput         |
|---------------------------------|-------------------|-------|--------------------|
| cloud container (3 vCPU, 8 GB)  | numpy active-set  | 3     | ~110 / h           |
| Mac mini M4 (10 cores, 16 GB)   | numpy active-set  | 8     | ~1100 / h (10 per 32 s) |
| NVIDIA GPU (A100/L4/T4)         | torch CSR, cuda   | 1     | not yet measured; expected 500-2000 / h |
| Apple MPS                       | torch index_add   | 1     | slower than numpy on the same Mac (see below) |

Rule of thumb: the sparse-regime subtype sweep (32 groups, n=1000) is a
one-hour job on the M4 and a day on the cloud container.

## 1. Apple-silicon Mac (recommended for this project)

```bash
git clone https://github.com/kaantiftikci/connectome-lif-lesions && cd connectome-lif-lesions
bash scripts/fetch_data.sh                   # ~1.5 GB into data/raw
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -e ".[ai,dev]"
python -m pytest -q
python scripts/run_lesion_sweep.py --group-set subtype --apl-scale 5 --n 1000 --procs 8 --resume \
       --out results/sweep_subtype_apl5.npz
```

`--procs 8` leaves two performance cores free; the connectome is loaded once
and shared copy-on-write by forked workers, so memory stays ~3 GB total.
Ctrl-C is safe: every 10 simulations go to `<out>.ckpt.npz` and `--resume`
continues from there (same `--n`, `--seed`, `--groups`, `--apl-scale`).

**Why not `--device mps`?** Apple's MPS backend has no sparse mat-vec, so the
torch path falls back to an edge-list gather + `index_add_` (15 M
multiply-adds per 0.1 ms step, 5 000 steps per stimulus). That is O(nnz)
work every step regardless of how few neurons spike, whereas the NumPy
active-set code only touches the rows of neurons that fired (a few hundred
to a few thousand). On the same Mac the MPS path is therefore slower than
8 NumPy workers. It exists so that the code *runs* on MPS and so a batched
version (many lesioned brains per kernel launch) can be added later; it is
not a speed-up today.

## 2. NVIDIA GPU (Colab, a cloud VM, a lab workstation)

The torch backend keeps the 15 M-synapse matrix as a CSR tensor on the GPU and
does one `spmv` per time step. Per-step cost is nearly independent of how
many neurons spike, so it wins in the attractor regime (thousands of active
neurons) and is roughly break-even with 8 CPU workers in the sparse regime.
Use one process per GPU:

```bash
pip install -e ".[ai]"                        # torch with CUDA wheels
python scripts/run_lesion_sweep.py --group-set subtype --apl-scale 5 --n 1000 \
       --backend torch --device cuda --procs 1 --resume --out results/sweep_subtype_apl5_gpu.npz
```

Colab (free T4) notebook cell sequence:

```python
!git clone https://github.com/kaantiftikci/connectome-lif-lesions && cd connectome-lif-lesions && bash scripts/fetch_data.sh
%cd sinek
!pip install -q -e ".[ai]"
!python scripts/run_lesion_sweep.py --group-set subtype --apl-scale 5 --n 300 \
    --backend torch --device cuda --procs 1 --resume --out /content/drive/MyDrive/sinek/sweep_gpu.npz
```

Mount Drive first so the checkpoint survives a disconnect. Verify the backend
before a long run: `python -m pytest -q tests/test_lif_torch.py` and one
10-simulation sweep with `--n 10`, comparing its `x` against the same specs on
the numpy backend (same `--seed`; rates should agree within the trial-to-trial
noise floor, ~1.9 L2 in the sparse regime).

## 3. Merging sweeps from several machines

Each run draws its lesion specs from `--seed`; two machines must use
different seeds (`--seed 0`, `--seed 1`, ...) or they simulate the same
lesions. Concatenate afterwards:

```python
import numpy as np
parts = [np.load(f) for f in ["results/sweep_a.npz", "results/sweep_b.npz"]]
assert all((p["group_names"] == parts[0]["group_names"]).all() for p in parts)
np.savez("results/sweep_merged.npz",
         theta=np.concatenate([p["theta"] for p in parts]),
         x=np.concatenate([p["x"] for p in parts]),
         group_names=parts[0]["group_names"], feature_names=parts[0]["feature_names"])
```

Then train and report as usual:

```bash
python scripts/train_surrogate.py --report --sweep results/sweep_merged.npz
python scripts/make_figures.py --report results/surrogate_report.npz
```

## 4. What is still missing for a real GPU speed-up

- **Batching.** The torch kernel simulates one brain at a time. Lesions are
  neuron removals, so B lesioned brains share one weight matrix with a
  per-brain alive-mask; a (B x n) state and one `spmm` per step would give
  near-linear speed-up up to GPU memory (B ~ 32-64 on a 16 GB card).
- **Poisson input on-device** is already done; spike recording still copies
  indices to the host each step, which is the main remaining host-device
  traffic. Recording only the readout neurons would remove most of it.
