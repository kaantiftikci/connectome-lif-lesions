"""Mushroom-body compartments derived from the connectome.

A dopaminergic neuron (DAN) and a mushroom-body output neuron (MBON) share a
compartment when the DAN makes direct synapses onto that MBON: DAN->MBON
connections are compartment-restricted (Aso et al. 2014), and in FlyWire the
strong ones are one-to-one (PPL103->MBON31 60.8 mV, PPL105->MBON13 78.6 mV,
PAM08->MBON29 56.4 mV; see docs/PLAN.md section 11).  Deriving the map from
the wiring instead of hard-coding anatomy keeps it dataset-agnostic (the same
code runs on the male connectome).
"""
from __future__ import annotations

import numpy as np
import scipy.sparse as sp

from ..data.flywire import Connectome


def compartment_map(cn: Connectome, min_w_mv: float = 2.0) -> dict[int, np.ndarray]:
    """MBON neuron index -> DAN neuron indices with direct input >= min_w_mv."""
    m = cn.meta
    is_dan = (m["cell_class"] == "DAN").to_numpy()
    mbon = cn.select(cell_type__startswith="MBON")
    Wc = cn.W.tocsc()
    out = {}
    for j in mbon:
        col = Wc[:, j]
        pre, w = col.indices, col.data
        keep = is_dan[pre] & (w >= min_w_mv)
        if keep.any():
            out[int(j)] = pre[keep]
    return out


def kc_mbon_synapses(cn: Connectome) -> dict[int, np.ndarray]:
    """MBON neuron index -> positions in ``cn.W.data`` (CSR) of its KC inputs."""
    m = cn.meta
    is_kc = (m["cell_class"] == "Kenyon_Cell").to_numpy()
    mbon_set = set(cn.select(cell_type__startswith="MBON").tolist())
    W = cn.W
    out: dict[int, list] = {j: [] for j in mbon_set}
    kc_rows = np.flatnonzero(is_kc)
    for i in kc_rows:
        a, b = W.indptr[i], W.indptr[i + 1]
        cols = W.indices[a:b]
        for pos, j in zip(range(a, b), cols):
            if j in mbon_set:
                out[int(j)].append(pos)
    return {j: np.array(v, dtype=np.int64) for j, v in out.items() if v}


def dan_targets(cn: Connectome) -> dict[int, np.ndarray]:
    """DAN neuron index -> positions in ``cn.W.data`` of its synapses onto KCs or MBONs
    (the fast synapses the modulation layer replaces)."""
    m = cn.meta
    is_dan = (m["cell_class"] == "DAN").to_numpy()
    is_target = ((m["cell_class"] == "Kenyon_Cell") | m["cell_type"].astype(str).str.startswith("MBON")).to_numpy()
    W = cn.W
    out = {}
    for i in np.flatnonzero(is_dan):
        a, b = W.indptr[i], W.indptr[i + 1]
        cols = W.indices[a:b]
        pos = np.arange(a, b)[is_target[cols]]
        if pos.size:
            out[int(i)] = pos
    return out
