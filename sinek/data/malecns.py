"""MaleCNS v1.0 (male central nervous system) loader with the same
``Connectome`` interface as the female FlyWire loader.

Data access needs a neuPrint token (https://neuprint.janelia.org, "Account"):

    export NEUPRINT_TOKEN=...
    python -c "from sinek.data.malecns import fetch_malecns; fetch_malecns('data/raw/malecns')"

``fetch_malecns`` downloads the neuron table and the full adjacency once and
caches them as parquet; ``load_malecns`` builds the Connectome from the cache
and ``build_connectome`` does the same from any pair of tables (used by the
offline unit test).  Field mapping (male -> FlyWire-style meta columns):

    type -> cell_type, class/superclass -> cell_class/super_class (labels mapped to the
    FlyWire vocabulary: descending_neuron -> descending, cb_intrinsic -> central, ...),
    somaSide (fallback rootSide; L/R/M) -> side (left/right/center), consensusNt (fallback predictedNt) -> top_nt

Synaptic sign follows Shiu et al.: acetylcholine, dopamine, octopamine and
serotonin excitatory (+1); GABA and glutamate inhibitory (-1).  Weights are
raw synapse counts x w_syn; the MaleCNS site notes male counts run ~1/0.581
higher than FlyWire for matched connections, so a ``count_scale`` is exposed
and should be set when comparing the sexes quantitatively.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp

from .flywire import Connectome, W_SYN_MV

EXCITATORY = {"acetylcholine", "dopamine", "octopamine", "serotonin", "ach", "da", "oa", "5ht", "unknown", ""}
INHIBITORY = {"gaba", "glutamate", "glu", "histamine"}   # histamine: photoreceptor -> HisCl, inhibitory (not present in the FlyWire sign table)
SIDE = {"L": "left", "R": "right", "M": "center", "left": "left", "right": "right", "center": "center"}
# neuPrint male-cns superclass labels -> FlyWire super_class vocabulary used by the selectors
SUPERCLASS = {"descending_neuron": "descending", "ascending_neuron": "ascending", "cb_intrinsic": "central",
              "ol_intrinsic": "optic", "vnc_intrinsic": "vnc", "visual_projection": "visual_projection",
              "visual_centrifugal": "visual_centrifugal", "cb_sensory": "sensory", "ol_sensory": "sensory",
              "vnc_sensory": "sensory", "sensory_ascending": "sensory_ascending", "cb_motor": "motor",
              "vnc_motor": "motor", "vnc_efferent": "efferent"}


def nt_sign(nt) -> int:
    s = str(nt).strip().lower() if nt is not None and nt == nt else ""
    return -1 if s in INHIBITORY else 1


def infer_cell_class(cell_type: str, cls) -> str:
    """Fill the class labels the lesion/readout selectors rely on."""
    if isinstance(cls, str) and cls not in ("", "nan"):
        return cls
    t = str(cell_type)
    if t.startswith(("PAM", "PPL1", "PPL2", "PPM")):
        return "DAN"
    if t.startswith("KC"):
        return "Kenyon_Cell"
    if t.startswith("MBON"):
        return "MBON"
    return "unknown"


def build_connectome(neurons: pd.DataFrame, edges: pd.DataFrame, w_syn_mv: float = W_SYN_MV,
                     count_scale: float = 1.0, name: str = "malecns_v1") -> Connectome:
    """neurons: columns bodyId, type, class, superclass, somaSide, predictedNt (extra columns kept).
    edges:   columns bodyId_pre, bodyId_post, weight (synapse count)."""
    neurons = neurons.drop_duplicates("bodyId").reset_index(drop=True)
    ids = neurons["bodyId"].to_numpy(np.int64)
    id2i = {int(b): k for k, b in enumerate(ids)}
    n = len(ids)
    meta = pd.DataFrame({
        "idx": np.arange(n), "root_id": ids,
        "cell_type": neurons.get("type", pd.Series([""] * n)).astype(str).replace({"None": "", "nan": ""}),
        "super_class": neurons.get("superclass", pd.Series([""] * n)).astype(str).str.lower().replace({"none": "", "nan": ""}).map(lambda v: SUPERCLASS.get(v, v)),
        "side": (neurons["somaSide"] if "somaSide" in neurons else neurons.get("rootSide", pd.Series([""] * n))).map(lambda s: SIDE.get(str(s), str(s))),
        "top_nt": neurons.get("consensusNt", neurons.get("predictedNt", pd.Series([""] * n))).astype(str).str.lower(),
    })
    meta["cell_class"] = [infer_cell_class(t, c) for t, c in zip(meta["cell_type"], neurons.get("class", pd.Series([None] * n)))]
    meta["cell_sub_class"] = neurons.get("subclass", pd.Series([None] * n)).to_numpy()
    meta["hemibrain_type"] = neurons.get("hemibrainType", pd.Series([None] * n)).to_numpy()
    for col in neurons.columns:
        if col not in ("bodyId", "type", "class", "superclass", "somaSide", "rootSide", "predictedNt", "consensusNt", "subclass", "hemibrainType", "somaLocation", "tosomaLocation") and col not in meta:
            meta[col] = neurons[col].to_numpy()
    nt_by_i = meta["top_nt"].map(nt_sign).to_numpy()
    e = edges[edges["bodyId_pre"].isin(id2i) & edges["bodyId_post"].isin(id2i)]
    pre = e["bodyId_pre"].map(id2i).to_numpy(); post = e["bodyId_post"].map(id2i).to_numpy()
    w = e["weight"].to_numpy(np.float32) * np.float32(count_scale) * nt_by_i[pre].astype(np.float32) * np.float32(w_syn_mv)
    W = sp.csr_matrix((w, (pre, post)), shape=(n, n)); W.sum_duplicates()
    return Connectome(ids=ids, W=W, meta=meta, name=name)


def fetch_malecns(cache_dir: str | Path, server: str = "https://neuprint.janelia.org", dataset: str = "male-cns:v1.0",
                  token: str | None = None, min_weight: int = 1) -> Path:
    """Download neuron and adjacency tables with neuprint-python and cache them."""
    from neuprint import Client, NeuronCriteria as NC, fetch_neurons, fetch_adjacencies
    # Token sources: explicit argument, NEUPRINT_TOKEN, or a proxy that injects the
    # Authorization header itself (proxy-injected "network secrets"); in the last case
    # any placeholder works because the proxy overwrites the header.
    token = token or os.environ.get("NEUPRINT_TOKEN") or "proxy-injected"
    cache = Path(cache_dir); cache.mkdir(parents=True, exist_ok=True)
    c = Client(server, dataset=dataset, token=token)
    neurons, _ = fetch_neurons(NC(status="Traced", client=c), client=c)
    neurons.to_parquet(cache / "neurons.parquet")
    _, conn = fetch_adjacencies(NC(status="Traced", client=c), NC(status="Traced", client=c), min_total_weight=min_weight, client=c)
    conn = conn.groupby(["bodyId_pre", "bodyId_post"], as_index=False)["weight"].sum()
    conn.to_parquet(cache / "edges.parquet")
    return cache


def load_malecns(cache_dir: str | Path = "data/raw/malecns", **kw) -> Connectome:
    cache = Path(cache_dir)
    return build_connectome(pd.read_parquet(cache / "neurons.parquet"), pd.read_parquet(cache / "edges.parquet"), **kw)


# ---------------------------------------------------------------------------
# Flat-file route (no neuPrint queries): the official release ships the full
# connectome as Apache Feather files on Google Cloud Storage
# (https://male-cns.janelia.org/download/):
#   body-annotations-male-cns-v1.0-minconf-0.5.feather   (14 MB)
#   body-neurotransmitters-male-cns-v1.0.feather         (42 MB)
#   connectome-weights-male-cns-v1.0-minconf-0.5.feather (1.0 GB, 152 M segment pairs)
GCS_BASE = "https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome"
FLAT_FILES = {"annotations": "body-annotations-male-cns-v1.0-minconf-0.5.feather",
              "nt": "body-neurotransmitters-male-cns-v1.0.feather",
              "weights": "connectome-weights-male-cns-v1.0-minconf-0.5.feather"}


def fetch_malecns_flat(cache_dir: str | Path = "data/raw/malecns") -> Path:
    """Download the three flat files (needs storage.googleapis.com reachable)."""
    import urllib.request
    cache = Path(cache_dir); cache.mkdir(parents=True, exist_ok=True)
    for f in FLAT_FILES.values():
        if not (cache / f).exists():
            urllib.request.urlretrieve(f"{GCS_BASE}/{f}", cache / f)
    return cache


def build_malecns_tables(cache_dir: str | Path = "data/raw/malecns", statuses=("Traced",)) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Neuron table (traced neurons with a superclass) and traced-to-traced edge
    table from the flat files; the edge table is cached as edges_traced.parquet."""
    import pyarrow.compute as pc
    import pyarrow.feather as pf
    cache = Path(cache_dir)
    ann = pf.read_table(cache / FLAT_FILES["annotations"]).to_pandas()
    ann = ann[ann["status"].isin(statuses) & ann["superclass"].notna()].copy()
    nt = pf.read_table(cache / FLAT_FILES["nt"], columns=["body", "consensus_nt", "predicted_nt"]).to_pandas()
    ann = ann.merge(nt.rename(columns={"body": "bodyId", "consensus_nt": "consensusNt", "predicted_nt": "predictedNt"}),
                    on="bodyId", how="left")
    edges_path = cache / "edges_traced.parquet"
    if edges_path.exists():
        edges = pd.read_parquet(edges_path)
    else:
        ids = pa_array = None
        import pyarrow as pa
        ids = pa.array(ann["bodyId"].to_numpy(np.int64))
        w = pf.read_table(cache / FLAT_FILES["weights"])
        mask = pc.and_(pc.is_in(w["body_pre"], value_set=ids), pc.is_in(w["body_post"], value_set=ids))
        w = w.filter(mask).to_pandas()
        edges = w.rename(columns={"body_pre": "bodyId_pre", "body_post": "bodyId_post"})
        edges.to_parquet(edges_path)
    return ann, edges


def load_malecns_flat(cache_dir: str | Path = "data/raw/malecns", **kw) -> Connectome:
    ann, edges = build_malecns_tables(cache_dir)
    return build_connectome(ann, edges, **kw)
