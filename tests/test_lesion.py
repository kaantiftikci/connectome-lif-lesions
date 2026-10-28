import numpy as np
import pandas as pd
import scipy.sparse as sp

from sinek.data.flywire import Connectome
from sinek.lesion import LesionSpec, apply_lesion, lesion_vector, lesioned_neurons, progressive, sample_lesions


def toy():
    n = 10
    rng = np.random.default_rng(0)
    W = sp.random(n, n, density=0.5, random_state=0, format="csr") + sp.eye(n, format="csr")
    meta = pd.DataFrame({"idx": np.arange(n), "cell_type": ["PAM01"] * 4 + ["PPL101"] * 2 + ["DNx"] * 4,
                         "super_class": ["central"] * 6 + ["descending"] * 4})
    return Connectome(ids=np.arange(n) + 100, W=W.tocsr(), meta=meta)


def test_select_and_groups():
    cn = toy()
    assert list(cn.select(cell_type__startswith="PAM")) == [0, 1, 2, 3]
    assert list(cn.select(super_class="descending")) == [6, 7, 8, 9]
    assert list(cn.index_of([101, 999, 105])) == [1, 5]


def test_remove_zeroes_rows_and_cols():
    cn = toy()
    groups = {"PAM": cn.select(cell_type__startswith="PAM")}
    W, hit = apply_lesion(cn, groups, LesionSpec({"PAM": 0.5}))
    assert len(hit["PAM"]) == 2
    for i in hit["PAM"]:
        assert W[i].nnz == 0 and W[:, i].nnz == 0
    assert W.nnz < cn.W.nnz


def test_silence_out_keeps_inputs():
    cn = toy()
    groups = {"PAM": cn.select(cell_type__startswith="PAM")}
    W, hit = apply_lesion(cn, groups, LesionSpec({"PAM": 1.0}, mode="silence_out"))
    for i in hit["PAM"]:
        assert W[i].nnz == 0
    assert any(W[:, i].nnz > 0 for i in hit["PAM"])


def test_synapse_scale():
    cn = toy()
    groups = {"PAM": cn.select(cell_type__startswith="PAM")}
    W, _ = apply_lesion(cn, groups, LesionSpec({"PAM": 0.5}, mode="synapse_scale"))
    i = 0
    assert np.allclose(W[i].toarray()[0, 5:], cn.W[i].toarray()[0, 5:] * 0.5)


def test_progressive_is_nested_and_deterministic():
    cn = toy()
    groups = {"PAM": cn.select(cell_type__startswith="PAM")}
    prev = set()
    for spec in progressive("PAM", fractions=(0.25, 0.5, 0.75, 1.0)):
        hit = set(lesioned_neurons(groups, spec)["PAM"])
        assert prev <= hit
        prev = hit
    a = lesioned_neurons(groups, LesionSpec({"PAM": 0.5}, seed=7))["PAM"]
    b = lesioned_neurons(groups, LesionSpec({"PAM": 0.5}, seed=7))["PAM"]
    assert list(a) == list(b)


def test_vector_and_prior():
    names = ["PAM", "PPL1", "KC"]
    v = lesion_vector(LesionSpec({"PPL1": 0.3}), names)
    assert np.allclose(v, [0.0, 0.3, 0.0])
    specs = sample_lesions(names, 50, seed=1, sparsity=0.5)
    th = np.stack([lesion_vector(s, names) for s in specs])
    assert th.shape == (50, 3) and th.min() >= 0 and th.max() <= 1
    assert 0.2 < (th > 0).mean() < 0.8
