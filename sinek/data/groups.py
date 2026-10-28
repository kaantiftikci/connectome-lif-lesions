"""Named neuron groups: lesion targets, stimuli and readouts.

Dopaminergic clusters follow the standard nomenclature (PAM, PPL1, PPL2ab,
PPM1/2/3).  In FlyWire v783 these are annotated as cell_type prefixes
``PAM``, ``PPL1``, ``PPL2``, ``PPM1``.  Counts in the female brain: PAM 307,
PPL1 16, PPL2 8, PPM1 16 (cell_class == "DAN" totals 331).

Everything here is a *selector* (dict of ``Connectome.select`` kwargs), so the
same names can be resolved against the male dataset once it is loaded.
"""
from __future__ import annotations

import numpy as np

from .flywire import Connectome


class _LazySubtypes(dict):
    """Placeholder resolved by ``group_indices`` when a Connectome is at hand."""

# Lesion targets with a disease rationale.
DA_GROUPS: dict[str, dict] = {
    "PAM":  {"cell_type__startswith": "PAM"},    # reward / appetitive memory, vulnerable in PD models
    "PPL1": {"cell_type__startswith": "PPL1"},   # punishment / aversive memory, classic PD-model cluster
    "PPL2": {"cell_type__startswith": "PPL2"},
    "PPM1": {"cell_type__startswith": "PPM1"},
}

# Non-dopaminergic controls with comparable size, to test specificity.
CONTROL_GROUPS: dict[str, dict] = {
    "KC":     {"cell_class": "Kenyon_Cell"},      # tauopathy-model target (mushroom body)
    "MBON":   {"cell_type__startswith": "MBON"},
    "mAL":    {"cell_class": "mAL"},
    "LHLN":   {"cell_class": "LHLN"},
}

# Stimulus battery: sensory populations driven with Poisson input.
STIMULI: dict[str, dict] = {
    # NOTE: only the 32 "sugar" GRNs.  Adding the 25 "sugar/low_salt" GRNs at
    # 150 Hz tips the whole model into a runaway attractor (~9,000 neurons at
    # the refractory ceiling); see docs/PLAN.md, "stable regime".
    "sugar":  {"cell_sub_class": "sugar"},
    "water":  {"cell_sub_class": "water"},
    "bitter": {"cell_sub_class": "bitter"},
    "odor_DM1": {"cell_type": "ORN_DM1"},   # one food-odour glomerulus (68 ORNs); all 2,282 ORNs would saturate the model
}


def group_indices(cn: Connectome, groups: dict[str, dict] | None = None) -> dict[str, np.ndarray]:
    if groups is None:
        groups = {**DA_GROUPS, **CONTROL_GROUPS}
    elif isinstance(groups, _LazySubtypes):
        groups = subtype_groups(cn)
    return {name: cn.select(**sel) for name, sel in groups.items()}


def stimulus_indices(cn: Connectome, stimuli: dict[str, dict] | None = None) -> dict[str, np.ndarray]:
    return {name: cn.select(**sel) for name, sel in (stimuli or STIMULI).items()}


def readout_groups(cn: Connectome, min_size: int = 4, extra: dict[str, np.ndarray] | None = None) -> dict[str, np.ndarray]:
    """Readout populations whose firing rates form the phenotype vector.

    Descending neurons (the brain's motor output) grouped by cell_type, plus
    MBON types.  Types with fewer than ``min_size`` neurons are pooled into
    ``DN_other`` so the vector stays stable across datasets.
    """
    out: dict[str, np.ndarray] = {}
    dn = cn.meta[cn.meta["super_class"] == "descending"]
    small = []
    for ct, sub in dn.groupby(dn["cell_type"].astype(str)):
        if len(sub) >= min_size:
            out[f"DN:{ct}"] = sub["idx"].to_numpy()
        else:
            small.append(sub["idx"].to_numpy())
    if small:
        out["DN:other"] = np.concatenate(small)
    mbon = cn.meta[cn.meta["cell_type"].astype(str).str.startswith("MBON")]
    for ct, sub in mbon.groupby(mbon["cell_type"].astype(str)):
        out[f"MBON:{ct}"] = sub["idx"].to_numpy()
    if extra:
        out.update(extra)
    return out


# Subtype-resolved dopaminergic groups (one group per annotated cell type).
# Built lazily from the annotation table so the list matches the dataset.
_PREFIXES = ("PAM", "PPL1", "PPL2", "PPM1")


def subtype_groups(cn: Connectome, min_size: int = 2) -> dict[str, dict]:
    ct = cn.meta["cell_type"].astype(str)
    out: dict[str, dict] = {}
    for pre in _PREFIXES:
        for name, cnt in ct[ct.str.startswith(pre)].value_counts().items():
            if cnt >= min_size:
                out[name] = {"cell_type": name}
    return out


SUBTYPE_GROUPS = _LazySubtypes()
