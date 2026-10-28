import numpy as np
import pytest

pytest.importorskip("torch")
pytest.importorskip("sbi")

from sinek.inference import LesionPosterior


def test_posterior_recovers_known_lesion():
    rng = np.random.default_rng(0)
    K, D = 3, 4
    A = rng.normal(size=(K, D))
    theta = rng.random((600, K))
    x = theta @ A + 0.02 * rng.normal(size=(600, D))
    post = LesionPosterior([f"g{i}" for i in range(K)]).fit(theta, x, epochs=40)
    truth = theta[0]
    s = post.summarize(x[0], n=500)
    err = np.mean([abs(s[f"g{i}"][0] - truth[i]) for i in range(K)])
    assert err < 0.2
