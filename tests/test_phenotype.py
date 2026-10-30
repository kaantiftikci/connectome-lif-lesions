import numpy as np
import scipy.sparse as sp

from sinek.readout import Stimulus, phenotype_vector, phenotype_names


def test_phenotype_shape_and_response():
    n = 6
    W = sp.csr_matrix((np.array([30.0, 30.0]), ([0, 1], [2, 3])), shape=(n, n))
    stim = [Stimulus("a", np.array([0])), Stimulus("b", np.array([1]))]
    readouts = {"r2": np.array([2]), "r3": np.array([3]), "r45": np.array([4, 5])}
    x = phenotype_vector(W, stim, readouts, duration=300.0, t_start=50.0, seed=0)
    names = phenotype_names(stim, readouts)
    assert x.shape == (6,) and len(names) == 6
    d = dict(zip(names, x))
    assert d["a|r2"] > 0 and d["a|r3"] == 0 and d["a|r45"] == 0
    assert d["b|r3"] > 0 and d["b|r2"] == 0


def test_phenotype_torch_backend_matches_numpy_shape():
    import pytest
    pytest.importorskip("torch")
    n = 6
    W = sp.csr_matrix((np.array([30.0, 30.0]), ([0, 1], [2, 3])), shape=(n, n))
    stim = [Stimulus("a", np.array([0]))]
    readouts = {"r2": np.array([2]), "r3": np.array([3])}
    xa = phenotype_vector(W, stim, readouts, duration=200.0, t_start=50.0, seed=0)
    xb = phenotype_vector(W, stim, readouts, duration=200.0, t_start=50.0, seed=0, backend="torch")
    assert xa.shape == xb.shape == (2,) and xb[0] > 0 and xb[1] == 0
