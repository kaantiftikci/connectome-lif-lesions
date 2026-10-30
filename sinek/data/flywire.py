"""Load the FlyWire v783 female brain as a signed sparse weight matrix.

Inputs (all public, fetched by ``scripts/fetch_data.sh``):

* ``Completeness_783.csv`` and ``Connectivity_783.parquet`` from
  philshiu/Drosophila_brain_model (Shiu et al. 2024).  The parquet already
  carries ``Excitatory x Connectivity`` = sign * synapse count, with the sign
  derived from the predicted neurotransmitter (ACh/DA/OA/5-HT = +1,
  GABA/Glu = -1).
* ``Supplemental_file1_neuron_annotations.tsv`` from
  flyconnectome/flywire_annotations (Schlegel et al. 2024) for cell types.

The male MaleCNS v1.0 dataset needs a neuPrint token; a loader with the same
interface is planned in ``malecns.py`` and is not available offline.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp

DEFAULT_RAW = Path("data/raw")
W_SYN_MV = 0.275  # mV per synapse, Shiu et al. free parameter


@dataclass
class Connectome:
    ids: np.ndarray                 # root id per neuron index
    W: sp.csr_matrix                # signed weights in mV, shape (n, n), [pre, post]
    meta: pd.DataFrame              # one row per neuron index (annotations)
    name: str = "flywire_783"
    _id2idx: dict = field(default_factory=dict, repr=False)

    def __post_init__(self):
        if not self._id2idx:
            self._id2idx = {int(i): k for k, i in enumerate(self.ids)}

    @property
    def n(self) -> int:
        return len(self.ids)

    def index_of(self, root_ids) -> np.ndarray:
        """Map root ids to neuron indices, dropping unknown ids."""
        return np.array([self._id2idx[int(r)] for r in root_ids if int(r) in self._id2idx], dtype=np.int64)

    def select(self, **conds) -> np.ndarray:
        """Indices of neurons whose meta columns match.

        ``select(super_class="descending")`` or
        ``select(cell_type=["PAM01", "PAM02"])`` or
        ``select(cell_type__startswith="PAM")``.
        """
        mask = np.ones(self.n, dtype=bool)
        for key, val in conds.items():
            if key.endswith("__startswith"):
                col = self.meta[key[: -len("__startswith")]].astype(str)
                mask &= col.str.startswith(val).to_numpy()
            elif key.endswith("__contains"):
                col = self.meta[key[: -len("__contains")]].astype(str)
                mask &= col.str.contains(val, regex=False).to_numpy()
            else:
                col = self.meta[key]
                vals = val if isinstance(val, (list, tuple, set)) else [val]
                mask &= col.isin(vals).to_numpy()
        return np.nonzero(mask)[0]


def load_flywire(raw_dir: str | Path = DEFAULT_RAW, w_syn_mv: float = W_SYN_MV,
                 min_synapses: int = 1) -> Connectome:
    raw = Path(raw_dir)
    comp = pd.read_csv(raw / "Completeness_783.csv", index_col=0)
    ids = comp.index.to_numpy().astype(np.int64)
    n = len(ids)

    con = pd.read_parquet(raw / "Connectivity_783.parquet",
                          columns=["Presynaptic_Index", "Postsynaptic_Index",
                                   "Connectivity", "Excitatory x Connectivity"])
    if min_synapses > 1:
        con = con[con["Connectivity"] >= min_synapses]
    W = sp.csr_matrix(
        (con["Excitatory x Connectivity"].to_numpy(dtype=np.float32) * np.float32(w_syn_mv),
         (con["Presynaptic_Index"].to_numpy(), con["Postsynaptic_Index"].to_numpy())),
        shape=(n, n))
    W.sum_duplicates()

    ann = pd.read_csv(raw / "Supplemental_file1_neuron_annotations.tsv", sep="\t", low_memory=False)
    ann = ann.drop_duplicates("root_id").set_index("root_id")
    meta = ann.reindex(ids)
    meta.index.name = "root_id"
    meta = meta.reset_index()
    meta.insert(0, "idx", np.arange(n))
    return Connectome(ids=ids, W=W, meta=meta)
