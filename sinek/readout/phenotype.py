"""Phenotype vector: readout-population firing rates under a stimulus battery.

This is the simulator's observable, x = f(theta).  It is a *proxy* for
behaviour: descending neurons are the only route from brain to body, so their
population rates under standard stimuli are the closest thing to a behavioural
signature available without an embodied model.  Phase 2 replaces this with
FlyGym/NeuroMechFly readouts (walking speed, negative geotaxis).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import scipy.sparse as sp

from ..sim.lif import LIFParams, simulate, firing_rates


@dataclass
class Stimulus:
    name: str
    targets: np.ndarray
    rate_hz: float = 150.0


def phenotype_names(stimuli: list[Stimulus], readouts: dict[str, np.ndarray]) -> list[str]:
    return [f"{s.name}|{r}" for s in stimuli for r in readouts]


def phenotype_vector(W: sp.csr_matrix, stimuli: list[Stimulus], readouts: dict[str, np.ndarray],
                     duration: float = 500.0, t_start: float = 100.0, n_trials: int = 1,
                     params: LIFParams = LIFParams(), seed: int = 0,
                     log: bool = True, backend: str = "numpy", device: str = "cpu",
                     v_th_offset: np.ndarray | None = None) -> np.ndarray:
    """Mean log(1+rate) of each readout group under each stimulus.

    backend: "numpy" (active-set, default) or "torch" (dense per step, use with
    device="cuda" on a GPU; see sinek.sim.lif_torch)."""
    if backend == "torch":
        from ..sim.lif_torch import simulate_torch
        def run(W_, dur, p_, tg, rate, sd):
            return simulate_torch(W_, dur, p_, poisson=tg, poisson_rate=rate, seed=sd, device=device)
    else:
        def run(W_, dur, p_, tg, rate, sd):
            return simulate(W_, dur, p_, poisson=tg, poisson_rate=rate, seed=sd, v_th_offset=v_th_offset)
    feats = []
    for s in stimuli:
        acc = np.zeros(len(readouts))
        for tr in range(n_trials):
            rec = run(W, duration, params, s.targets, s.rate_hz, seed * 1000 + tr)
            r = firing_rates(rec, t_start)
            acc += np.array([r[idx].mean() if idx.size else 0.0 for idx in readouts.values()])
        acc /= n_trials
        feats.append(np.log1p(acc) if log else acc)
    return np.concatenate(feats).astype(np.float32)
