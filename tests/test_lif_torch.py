import numpy as np
import pytest
import scipy.sparse as sp

torch = pytest.importorskip("torch")

from sinek.sim import simulate, LIFParams, firing_rates
from sinek.sim.lif_torch import simulate_torch


def test_torch_matches_numpy_with_deterministic_drive():
    rng = np.random.default_rng(3)
    n = 25
    W = sp.random(n, n, density=0.25, random_state=3, format="csr")
    W.data = (rng.choice([-1, 1], size=W.nnz) * rng.integers(5, 80, size=W.nnz)) * 0.275
    W = W.tocsr()
    drive = {0: 1e9, 1: 1e9}          # fires every step: no randomness left
    a = simulate(W, 100.0, poisson=drive, seed=0)
    b = simulate_torch(W, 100.0, poisson=drive, seed=0)
    assert np.abs(a.counts() - b.counts()).max() <= 1               # float32 rounding can add/drop a threshold crossing
    assert abs(a.times.size - b.times.size) <= 2


def test_torch_poisson_rates_match_in_distribution():
    W = sp.csr_matrix((np.array([275 * 0.275]), ([0], [1])), shape=(2, 2))
    ra = firing_rates(simulate(W, 3000.0, poisson=np.array([0]), seed=1))
    rb = firing_rates(simulate_torch(W, 3000.0, poisson=np.array([0]), seed=1))
    assert abs(ra[0] - rb[0]) < 25 and abs(ra[1] - rb[1]) < 0.3 * max(ra[1], 1)
