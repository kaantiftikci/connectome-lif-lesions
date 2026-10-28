"""Cell-type-resolved, progressive lesions on a connectome.

A lesion is a vector theta in [0,1]^K: the fraction of each named group that
is lost.  Three mechanisms are supported, chosen to span what fly disease
models show:

* ``remove``       neuron death: all in- and out-going synapses deleted
* ``silence_out``  loss of output only (Shiu-style silencing)
* ``synapse_scale`` synaptic weakening without cell death: every synapse of
                   the group scaled by (1 - fraction)

Lesions are deterministic given ``seed`` and *nested*: a 40 % lesion removes a
superset of the neurons removed at 20 %, so progressive series are monotone.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import scipy.sparse as sp

from ..data.flywire import Connectome


@dataclass
class LesionSpec:
    fractions: dict[str, float]
    mode: str = "remove"
    seed: int = 0

    def __post_init__(self):
        for k, f in self.fractions.items():
            if not 0.0 <= f <= 1.0:
                raise ValueError(f"fraction for {k} must be in [0,1], got {f}")
        if self.mode not in {"remove", "silence_out", "synapse_scale"}:
            raise ValueError(f"unknown mode {self.mode}")


def lesion_vector(spec: LesionSpec, group_names: list[str]) -> np.ndarray:
    return np.array([spec.fractions.get(g, 0.0) for g in group_names], dtype=np.float32)


def _ordered(group: np.ndarray, seed: int, salt: str) -> np.ndarray:
    """Fixed random order per group so lesions are nested across fractions."""
    rng = np.random.default_rng([seed, abs(hash(salt)) % (2**32)])
    return group[rng.permutation(len(group))]


def lesioned_neurons(groups: dict[str, np.ndarray], spec: LesionSpec) -> dict[str, np.ndarray]:
    out = {}
    for name, frac in spec.fractions.items():
        if frac <= 0 or name not in groups:
            continue
        order = _ordered(groups[name], spec.seed, name)
        k = int(round(frac * len(order)))
        out[name] = order[:k]
    return out


def apply_lesion(cn: Connectome, groups: dict[str, np.ndarray], spec: LesionSpec):
    """Return (W_lesioned, removed) where removed maps group -> neuron indices."""
    hit = lesioned_neurons(groups, spec)
    n = cn.n
    if spec.mode == "synapse_scale":
        scale = np.ones(n, dtype=np.float32)
        for name, frac in spec.fractions.items():
            if name in groups and frac > 0:
                scale[groups[name]] *= (1.0 - frac)
        S = sp.diags(scale)
        W = (S @ cn.W @ S).tocsr()
        return W, {k: groups[k] for k in spec.fractions if k in groups and spec.fractions[k] > 0}
    keep = np.ones(n, dtype=np.float32)
    for idx in hit.values():
        keep[idx] = 0.0
    K = sp.diags(keep)
    if spec.mode == "remove":
        W = (K @ cn.W @ K).tocsr()
    else:  # silence_out
        W = (K @ cn.W).tocsr()
    W.eliminate_zeros()
    return W, hit


def progressive(group: str, fractions=(0.0, 0.2, 0.4, 0.6, 0.8, 1.0), mode="remove", seed=0):
    """A nested series of lesions on one group (for 'silent reserve' curves)."""
    return [LesionSpec({group: f}, mode=mode, seed=seed) for f in fractions]


def sample_lesions(group_names: list[str], n: int, seed: int = 0, mode: str = "remove",
                   sparsity: float = 0.5) -> list[LesionSpec]:
    """Prior over lesion vectors for simulator-based training.

    Each group is lesioned with probability (1 - sparsity); its fraction is
    Uniform(0, 1).  Sparse priors keep the inverse problem identifiable.
    """
    rng = np.random.default_rng(seed)
    specs = []
    for i in range(n):
        on = rng.random(len(group_names)) >= sparsity
        fr = rng.random(len(group_names)) * on
        specs.append(LesionSpec({g: float(f) for g, f in zip(group_names, fr)}, mode=mode, seed=seed + i))
    return specs
