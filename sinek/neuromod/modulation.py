"""Dopamine as a modulator instead of a fast excitatory transmitter.

In the reference LIF model dopaminergic synapses are ordinary excitatory
synapses, so a DAN drives its compartment MBON directly and all-or-none
(docs/PLAN.md section 11).  Biologically, dopamine released onto KC axon
terminals sets the gain of KC->MBON synapses in that compartment and, when
paired with KC activity, depresses them persistently (the basis of
associative memory; Hige et al. 2015, Owald et al. 2015).

This layer implements that:

* the DAN->KC and DAN->MBON fast synapses are scaled by ``alpha_fast``
  (0 removes them),
* every ``window`` ms, each MBON's KC inputs are multiplied by an acute gain
  g_m = exp(-kappa * (rbar_m - b_m)), clipped to [0, g_max], where rbar_m is
  the low-pass (tau_da) mean rate of the DANs in MBON m's compartment and
  b_m the tonic level measured in the intact brain under the same stimulus
  (``set_baseline``).  Intact: g = 1.  Pairing (rbar > b): depression.
  DAN loss (rbar < b): disinhibition that grows with the fraction lost,
* if ``plastic``, the KC->MBON baseline weights are depressed by
  eta * rbar_KC * max(rbar_DAN - b, 0) * window: dopamine-gated,
  activity-dependent, and driven by the phasic increase over tonic level
  (the model's DANs sit at 100-300 Hz under odour alone, so an absolute rule
  would depress every compartment at once).

Partial DAN loss now moves rbar_m in proportion, so the MBON output changes
gradually instead of switching off: the mechanism phase 1 found missing.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import scipy.sparse as sp

from ..data.flywire import Connectome
from ..sim.lif import LIFParams, SpikeRecord, simulate, LIFState
from .compartments import compartment_map, kc_mbon_synapses, dan_targets


@dataclass
class ModulationParams:
    kappa: float = 0.05        # gain per Hz of compartment DAN rate (g = exp(-kappa * r))
    tau_da: float = 200.0      # ms, low-pass of DAN rate (dopamine kinetics)
    eta: float = 0.0           # plasticity rate: fractional depression per (Hz_KC * Hz_DAN * s)
    alpha_fast: float = 0.0    # residual scale of DAN->KC/MBON fast synapses
    window: float = 20.0       # ms between gain updates
    min_w_mv: float = 2.0      # DAN->MBON weight that defines compartment membership
    g_max: float = 3.0         # cap on disinhibition


class ModulatedNetwork:
    def __init__(self, cn: Connectome, params: ModulationParams = ModulationParams(),
                 W: sp.csr_matrix | None = None):
        """``W`` may be a lesioned copy of ``cn.W`` (same sparsity pattern required,
        which apply_lesion preserves for mode='remove'/'silence_out' only up to
        eliminate_zeros; pass W built with keep_pattern=True)."""
        self.cn, self.p = cn, params
        base = cn.W if W is None else W
        if base.nnz != cn.W.nnz:
            raise ValueError("W must keep cn.W's sparsity pattern (use apply_lesion(..., keep_pattern=True))")
        self.W = base.copy()
        self.comp = compartment_map(cn, params.min_w_mv)           # mbon -> DAN idx
        self.kc_syn = kc_mbon_synapses(cn)                          # mbon -> data positions
        self.mbons = [j for j in self.comp if j in self.kc_syn]
        for pos in dan_targets(cn).values():
            self.W.data[pos] *= params.alpha_fast
        self.w0 = {j: self.W.data[self.kc_syn[j]].copy() for j in self.mbons}
        kc = cn.select(cell_class="Kenyon_Cell")
        self.kc_of = {j: cn.W.indices[self.kc_syn[j]] for j in self.mbons}   # not used: CSR cols are posts
        # presynaptic KC index for each KC->MBON synapse position
        row_of_pos = np.repeat(np.arange(cn.n), np.diff(cn.W.indptr))
        self.kc_pre = {j: row_of_pos[self.kc_syn[j]] for j in self.mbons}
        self.gain = {j: 1.0 for j in self.mbons}
        self.baseline = {j: 0.0 for j in self.mbons}

    def set_baseline(self, rbar: dict[int, float]):
        """Tonic compartment-DAN rates of the intact brain under the current stimulus."""
        self.baseline = {j: float(rbar.get(j, 0.0)) for j in self.mbons}

    def lesion_rates(self, rates: np.ndarray, rbar: dict[int, float], dt_s: float) -> dict[int, float]:
        a = np.exp(-1000.0 * dt_s / self.p.tau_da)
        for j in self.mbons:
            r = rates[self.comp[j]].mean() if self.comp[j].size else 0.0
            rbar[j] = a * rbar.get(j, 0.0) + (1 - a) * r
        return rbar

    def apply_gain(self, rbar: dict[int, float]):
        for j in self.mbons:
            self.gain[j] = float(np.clip(np.exp(-self.p.kappa * (rbar[j] - self.baseline[j])), 0.0, self.p.g_max))
            self.W.data[self.kc_syn[j]] = self.w0[j] * self.gain[j]

    def apply_plasticity(self, rates: np.ndarray, rbar: dict[int, float], dt_s: float):
        if self.p.eta <= 0:
            return
        for j in self.mbons:
            pre = rates[self.kc_pre[j]]
            dep = 1.0 - self.p.eta * pre * max(rbar[j] - self.baseline[j], 0.0) * dt_s
            self.w0[j] = self.w0[j] * np.clip(dep, 0.0, 1.0)


def simulate_modulated(net: ModulatedNetwork, duration: float, poisson=None, poisson_rate=None,
                       seed: int = 0, params: LIFParams = LIFParams(), plastic: bool = False,
                       rbar: dict[int, float] | None = None) -> tuple[SpikeRecord, dict[int, float]]:
    """Windowed simulation with dopamine-dependent KC->MBON gain.  Returns the
    spike record and the final low-passed DAN rates (pass back in as ``rbar``
    to continue a protocol, e.g. train then test)."""
    rbar = {} if rbar is None else dict(rbar)
    net.apply_gain({j: rbar.get(j, 0.0) for j in net.mbons})
    win = net.p.window
    n_win = int(round(duration / win))
    state: LIFState | None = None
    t_list, i_list = [], []
    for w in range(n_win):
        rec, state = simulate(net.W, win, params, poisson=poisson, poisson_rate=poisson_rate,
                              seed=seed, state=state, return_state=True)
        t_list.append(rec.times); i_list.append(rec.ids)
        rates = np.bincount(rec.ids, minlength=net.cn.n) / (win / 1000.0)
        rbar = net.lesion_rates(rates, rbar, win / 1000.0)
        if plastic:
            net.apply_plasticity(rates, rbar, win / 1000.0)
        net.apply_gain(rbar)
    times = np.concatenate(t_list) if t_list else np.empty(0)
    ids = np.concatenate(i_list) if i_list else np.empty(0, dtype=np.int64)
    return SpikeRecord(times=times, ids=ids, n=net.cn.n, duration=n_win * win), rbar
