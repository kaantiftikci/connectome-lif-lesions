"""Torch implementation of the same LIF dynamics as :func:`sinek.sim.simulate`,
dense over neurons per step with sparse spike propagation.  On a GPU every
step is a handful of kernels, so a 1 s whole-brain run takes seconds instead
of tens of seconds; on CPU it is slower than the NumPy active-set version
and exists only for testing.

Differences from the NumPy version: Poisson draws come from torch's RNG, so
spike trains match in distribution, not sample by sample.

Spike propagation has two implementations selected by ``propagate``:
  "csr"       sparse CSR mat-vec (CUDA, CPU)
  "index_add" gather over the edge list + index_add_ (works on Apple MPS,
              which has no sparse kernels; O(nnz) per step so slower)
  "auto"      "index_add" on mps, "csr" elsewhere
"""
from __future__ import annotations

import numpy as np
import scipy.sparse as sp

from .lif import LIFParams, SpikeRecord


def simulate_torch(W: sp.csr_matrix, duration: float, params: LIFParams = LIFParams(),
                   poisson=None, poisson_rate: float | None = None, seed: int = 0,
                   device: str = "cpu", record: bool = True, propagate: str = "auto") -> SpikeRecord:
    import torch
    if propagate == "auto":
        propagate = "index_add" if str(device).startswith("mps") else "csr"
    p = params
    dt = p.dt
    n = W.shape[0]
    n_steps = int(round(duration / dt))
    D = int(round(p.t_dly / dt))
    e_m, e_s = float(np.exp(-dt / p.t_mbr)), float(np.exp(-dt / p.tau))
    a = p.tau / (p.tau - p.t_mbr)
    gen = torch.Generator(device=device); gen.manual_seed(seed)
    if propagate == "csr":
        WT = W.T.tocsr().astype(np.float32)        # post x pre, so g_delta = WT @ spikes
        Wt = torch.sparse_csr_tensor(torch.as_tensor(WT.indptr, dtype=torch.int64), torch.as_tensor(WT.indices, dtype=torch.int64),
                                     torch.as_tensor(WT.data), size=(n, n), device=device)
    else:
        C = W.tocoo()
        e_pre = torch.as_tensor(C.row.astype(np.int64), device=device)
        e_post = torch.as_tensor(C.col.astype(np.int64), device=device)
        e_w = torch.as_tensor(C.data.astype(np.float32), device=device)
    v = torch.full((n,), p.v_0, device=device)
    g = torch.zeros(n, device=device)
    rfc = torch.full((n,), p.t_rfc, device=device)
    ref_until = torch.full((n,), -1e30, device=device)
    poi_idx = torch.empty(0, dtype=torch.int64, device=device); poi_p = torch.empty(0, device=device)
    if poisson is not None:
        if isinstance(poisson, dict):
            poi_idx = torch.as_tensor(list(poisson.keys()), dtype=torch.int64, device=device)
            rates = torch.as_tensor(list(poisson.values()), dtype=torch.float32, device=device)
        else:
            poi_idx = torch.as_tensor(np.asarray(poisson), dtype=torch.int64, device=device)
            rates = torch.full((len(poi_idx),), float(poisson_rate if poisson_rate is not None else p.r_poi), device=device)
        poi_p = rates * dt / 1000.0
        rfc[poi_idx] = 0.0
    w_poi = p.w_syn * p.f_poi
    buf = torch.zeros((D + 1, n), device=device)
    t_list, i_list = [], []
    for k in range(n_steps):
        t = k * dt
        slot = k % (D + 1)
        g += buf[slot]; buf[slot].zero_()
        if poi_idx.numel():
            hit = torch.rand(poi_idx.numel(), generator=gen, device=device) < poi_p
            v[poi_idx[hit]] += w_poi
        active = t >= ref_until
        v_new = p.v_0 + (v - p.v_0 - a * g) * e_m + a * g * e_s
        g_new = g * e_s
        v = torch.where(active, v_new, v); g = torch.where(active, g_new, g)
        spk = active & (v > p.v_th)
        if bool(spk.any()):
            idx = torch.nonzero(spk).squeeze(1)
            v[idx] = p.v_rst; g[idx] = 0.0; ref_until[idx] = t + rfc[idx]
            if propagate == "csr":
                buf[(k + D) % (D + 1)] += torch.mv(Wt, spk.to(torch.float32))
            else:
                buf[(k + D) % (D + 1)].index_add_(0, e_post, e_w * spk.to(torch.float32)[e_pre])
            if record:
                t_list.append(np.full(idx.numel(), t)); i_list.append(idx.cpu().numpy())
    times = np.concatenate(t_list) if t_list else np.empty(0)
    ids = np.concatenate(i_list) if i_list else np.empty(0, dtype=np.int64)
    return SpikeRecord(times=times, ids=ids, n=n, duration=duration)
