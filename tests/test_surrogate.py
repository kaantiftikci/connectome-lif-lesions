import numpy as np
import pytest

torch = pytest.importorskip("torch")

from sinek.surrogate import Surrogate


def test_surrogate_fits_linear_map_and_screens():
    rng = np.random.default_rng(0)
    K, D = 4, 6
    A = rng.normal(size=(K, D))
    theta = rng.random((400, K)) * (rng.random((400, K)) > 0.5)
    x = theta @ A + 0.01 * rng.normal(size=(400, D))
    sur = Surrogate(K, D, hidden=64, n_members=2).fit(theta, x, epochs=150)
    mu, sd = sur.predict(theta[:50])
    r2 = 1 - ((mu - x[:50]) ** 2).sum() / ((x[:50] - x[:50].mean(0)) ** 2).sum()
    assert r2 > 0.9
    J = sur.sensitivity()
    assert J.shape == (D, K)
    target = np.zeros(K, np.float32); target[1] = 1.0
    xt, _ = sur.predict(target)
    mimic = sur.reverse_screen(xt[0], exclude=[1], steps=300)
    assert mimic[1] == 0.0 and mimic.shape == (K,)


def test_linear_surrogate_recovers_linear_map():
    from sinek.surrogate import LinearSurrogate, cv_r2
    rng = np.random.default_rng(1)
    K, D = 5, 7
    A = rng.normal(size=(K, D))
    theta = rng.random((80, K)); x = theta @ A + 0.05 * rng.normal(size=(80, D))
    assert cv_r2(lambda: LinearSurrogate(K, D, lam=0.1), theta, x) > 0.9
    m = LinearSurrogate(K, D, lam=0.1).fit(theta, x)
    assert np.allclose(m.sensitivity(), A.T, atol=0.15)
    t = np.zeros(K); t[2] = 0.8
    mimic = m.reverse_screen((t @ A), l1=0.0, exclude=[])
    assert abs(mimic[2] - 0.8) < 0.1
