"""Event-driven leaky integrate-and-fire network, NumPy only.

Re-implements the Brian2 model of Shiu et al. 2024 (Nature) so the whole
brain runs without Brian2 and can be driven programmatically from the lesion
and inference code.  Units: mV and ms.

Neuron (unless refractory)::

    dv/dt = (v_0 - v + g) / t_mbr
    dg/dt = -g / tau

Spike when v > v_th, then v = v_rst, g = 0, refractory for t_rfc.  A
presynaptic spike adds w (mV, signed) to the postsynaptic g after t_dly.
Poisson-driven neurons receive w_syn * f_poi directly on v at rate r_poi and
have no refractory period, exactly as in the reference implementation.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp


@dataclass
class LIFParams:
    v_0: float = -52.0       # resting potential (mV)
    v_rst: float = -52.0     # reset
    v_th: float = -45.0      # threshold
    t_mbr: float = 20.0      # membrane time constant (ms)
    tau: float = 5.0         # synaptic time constant (ms)
    t_rfc: float = 2.2       # refractory period (ms)
    t_dly: float = 1.8       # synaptic delay (ms)
    w_syn: float = 0.275     # mV per synapse (already folded into W)
    r_poi: float = 150.0     # Hz, default Poisson drive
    f_poi: float = 250.0     # Poisson weight = w_syn * f_poi
    dt: float = 0.1          # ms
    tau_adapt: float = 0.0   # ms; spike-frequency adaptation time constant (0 = off)
    delta_adapt: float = 0.0 # mV added to the threshold per spike (decays with tau_adapt)


@dataclass
class SpikeRecord:
    times: np.ndarray        # ms
    ids: np.ndarray          # neuron index
    n: int
    duration: float          # ms

    def counts(self) -> np.ndarray:
        return np.bincount(self.ids, minlength=self.n)


def firing_rates(rec: SpikeRecord, t_start: float = 0.0) -> np.ndarray:
    """Mean rate (Hz) per neuron over [t_start, duration]."""
    m = rec.times >= t_start
    win = (rec.duration - t_start) / 1000.0
    return np.bincount(rec.ids[m], minlength=rec.n) / win


def _gather_rows(W: sp.csr_matrix, rows: np.ndarray):
    """Column indices and weights of all entries in the given CSR rows."""
    starts = W.indptr[rows]
    lens = W.indptr[rows + 1] - starts
    total = int(lens.sum())
    if total == 0:
        return np.empty(0, dtype=np.int64), np.empty(0, dtype=W.data.dtype)
    offs = np.repeat(starts - np.concatenate(([0], np.cumsum(lens)[:-1])), lens)
    pos = np.arange(total) + offs
    return W.indices[pos], W.data[pos]


def simulate_dense(W: sp.csr_matrix, duration: float, params: LIFParams = LIFParams(),
             poisson: dict[int, float] | np.ndarray | None = None,
             poisson_rate: float | None = None,
             seed: int | None = 0, record: bool = True) -> SpikeRecord:
    """Reference dense implementation (every neuron updated every step).

    Kept for cross-checking :func:`simulate`; ~5x slower in the sparse-activity
    regime.  W : csr (n, n), W[pre, post] in mV (signed).
    poisson : neuron indices driven by Poisson input (all at ``poisson_rate``
        or ``params.r_poi``), or a dict {index: rate_hz}.
    """
    rng = np.random.default_rng(seed)
    n = W.shape[0]
    p = params
    dt = p.dt
    n_steps = int(round(duration / dt))
    D = int(round(p.t_dly / dt))

    # exact integration constants for the linear system
    e_m = np.exp(-dt / p.t_mbr)
    e_s = np.exp(-dt / p.tau)
    a = p.tau / (p.tau - p.t_mbr)          # particular-solution coefficient

    v = np.full(n, p.v_0, dtype=np.float64)
    g = np.zeros(n, dtype=np.float64)
    rfc = np.full(n, p.t_rfc, dtype=np.float64)
    ref_until = np.full(n, -np.inf)

    # Poisson drive
    poi_idx = np.empty(0, dtype=np.int64)
    poi_p = np.empty(0)
    if poisson is not None:
        if isinstance(poisson, dict):
            poi_idx = np.fromiter(poisson.keys(), dtype=np.int64)
            rates = np.fromiter(poisson.values(), dtype=np.float64)
        else:
            poi_idx = np.asarray(poisson, dtype=np.int64)
            rates = np.full(len(poi_idx), poisson_rate if poisson_rate is not None else p.r_poi)
        poi_p = rates * dt / 1000.0
        rfc[poi_idx] = 0.0
    w_poi = p.w_syn * p.f_poi

    buf = np.zeros((D + 1, n), dtype=np.float64)   # delayed synaptic input ring buffer
    t_list, i_list = [], []

    for k in range(n_steps):
        t = k * dt
        slot = k % (D + 1)
        # arrive delayed synaptic input
        g += buf[slot]
        buf[slot] = 0.0
        # external Poisson input directly on v
        if poi_idx.size:
            hit = rng.random(poi_idx.size) < poi_p
            if hit.any():
                v[poi_idx[hit]] += w_poi
        # integrate non-refractory neurons
        active = t >= ref_until
        va, ga = v[active], g[active]
        v[active] = p.v_0 + (va - p.v_0 - a * ga) * e_m + a * ga * e_s
        g[active] = ga * e_s
        # threshold
        spk = np.nonzero(active & (v > p.v_th))[0]
        if spk.size:
            v[spk] = p.v_rst
            g[spk] = 0.0
            ref_until[spk] = t + rfc[spk]
            post, w = _gather_rows(W, spk)
            if post.size:
                buf[(k + D) % (D + 1)] += np.bincount(post, weights=w, minlength=n)
            if record:
                t_list.append(np.full(spk.size, t))
                i_list.append(spk)

    if t_list:
        times = np.concatenate(t_list)
        ids = np.concatenate(i_list)
    else:
        times = np.empty(0)
        ids = np.empty(0, dtype=np.int64)
    return SpikeRecord(times=times, ids=ids, n=n, duration=duration)


@dataclass
class LIFState:
    """Full network state so a simulation can be continued in windows (used by
    the neuromodulation layer, which changes weights between windows)."""
    v: np.ndarray
    g: np.ndarray
    ref_until: np.ndarray
    awake: np.ndarray
    buf: list
    k: int                      # steps simulated so far
    rng: np.random.Generator
    adapt: np.ndarray | None = None   # per-neuron threshold increment (adaptation)


def simulate(W: sp.csr_matrix, duration: float, params: LIFParams = LIFParams(),
             poisson: dict[int, float] | np.ndarray | None = None,
             poisson_rate: float | None = None,
             seed: int | None = 0, record: bool = True, eps: float = 1e-3,
             state: LIFState | None = None, return_state: bool = False,
             v_th_offset: np.ndarray | None = None):
    """Active-set implementation: only neurons that are away from rest, carry
    synaptic input, or are refractory are updated each step.  Identical
    dynamics to :func:`simulate_dense` up to ``eps`` (mV): a neuron is put to
    sleep once |v - v_0| < eps and |g| < eps and it is not refractory.

    W : csr (n, n), W[pre, post] in mV (signed).
    poisson : neuron indices driven by Poisson input (all at ``poisson_rate``
        or ``params.r_poi``), or a dict {index: rate_hz}.
    state : continue from a previous window (times keep counting from 0 of the
        first window); with ``return_state`` the call returns (record, state).
    v_th_offset : optional per-neuron threshold shift in mV (e.g. +2 on Kenyon
        cells), added to ``params.v_th``.
    """
    n = W.shape[0]
    p = params
    vth = p.v_th + (np.zeros(n) if v_th_offset is None else np.asarray(v_th_offset, dtype=np.float64))
    dt = p.dt
    n_steps = int(round(duration / dt))
    D = int(round(p.t_dly / dt))
    e_m = np.exp(-dt / p.t_mbr)
    e_s = np.exp(-dt / p.tau)
    a = p.tau / (p.tau - p.t_mbr)

    if state is None:
        rng = np.random.default_rng(seed)
        v = np.full(n, p.v_0, dtype=np.float64)
        g = np.zeros(n, dtype=np.float64)
        ref_until = np.full(n, -np.inf)
        awake = np.zeros(n, dtype=bool)
        k0 = 0
        adapt = np.zeros(n, dtype=np.float64)
    else:
        rng, v, g, ref_until, awake, k0 = state.rng, state.v, state.g, state.ref_until, state.awake, state.k
        adapt = state.adapt if state.adapt is not None else np.zeros(n, dtype=np.float64)
    use_adapt = p.tau_adapt > 0 and p.delta_adapt != 0
    e_ad = np.exp(-dt / p.tau_adapt) if use_adapt else 1.0
    rfc = np.full(n, p.t_rfc, dtype=np.float64)

    poi_idx = np.empty(0, dtype=np.int64)
    poi_p = np.empty(0)
    if poisson is not None:
        if isinstance(poisson, dict):
            poi_idx = np.fromiter(poisson.keys(), dtype=np.int64)
            rates = np.fromiter(poisson.values(), dtype=np.float64)
        else:
            poi_idx = np.asarray(poisson, dtype=np.int64)
            rates = np.full(len(poi_idx), poisson_rate if poisson_rate is not None else p.r_poi)
        poi_p = rates * dt / 1000.0
        rfc[poi_idx] = 0.0
    w_poi = p.w_syn * p.f_poi

    empty = (np.empty(0, dtype=np.int64), np.empty(0, dtype=W.data.dtype))
    buf = [empty] * (D + 1) if state is None else state.buf
    t_list, i_list = [], []

    for k in range(k0, k0 + n_steps):
        t = k * dt
        slot = k % (D + 1)
        post, w = buf[slot]
        if post.size:
            buf[slot] = empty
            np.add.at(g, post, w)
            awake[post] = True
        if poi_idx.size:
            hit = rng.random(poi_idx.size) < poi_p
            if hit.any():
                h = poi_idx[hit]
                v[h] += w_poi
                awake[h] = True
        idx = np.flatnonzero(awake)
        if idx.size == 0:
            continue
        act = idx[t >= ref_until[idx]]
        va, ga = v[act], g[act]
        v[act] = p.v_0 + (va - p.v_0 - a * ga) * e_m + a * ga * e_s
        g[act] = ga * e_s
        if use_adapt:
            adapt[idx] *= e_ad
            spk = act[v[act] > vth[act] + adapt[act]]
        else:
            spk = act[v[act] > vth[act]]
        if spk.size:
            v[spk] = p.v_rst
            g[spk] = 0.0
            ref_until[spk] = t + rfc[spk]
            if use_adapt:
                adapt[spk] += p.delta_adapt
            buf[(k + D) % (D + 1)] = _gather_rows(W, spk)
            if record:
                t_list.append(np.full(spk.size, t))
                i_list.append(spk)
        # put settled, non-refractory neurons to sleep
        quiet = act[(np.abs(v[act] - p.v_0) < eps) & (np.abs(g[act]) < eps) & (t >= ref_until[act]) & (adapt[act] < eps)]
        if quiet.size:
            v[quiet] = p.v_0
            g[quiet] = 0.0
            awake[quiet] = False

    if t_list:
        times = np.concatenate(t_list)
        ids = np.concatenate(i_list)
    else:
        times = np.empty(0)
        ids = np.empty(0, dtype=np.int64)
    rec = SpikeRecord(times=times, ids=ids, n=n, duration=(k0 + n_steps) * dt)
    if return_state:
        return rec, LIFState(v=v, g=g, ref_until=ref_until, awake=awake, buf=buf, k=k0 + n_steps, rng=rng, adapt=adapt)
    return rec
