"""Amortised inverse model: posterior over lesions given an observed phenotype.

Neural Posterior Estimation (NPE, via the ``sbi`` library): a normalising flow
q(theta | x) trained on simulator pairs (theta, x).  Once trained, inference
for any observed phenotype is a forward pass, so it can be applied to every
published fly disease-model phenotype without re-simulating.

Validation protocol (phase 1, all in silico):
  * recover known lesions from their own simulated phenotype (posterior mean
    vs truth, per group),
  * simulation-based calibration (``sbi.analysis.run_sbc``) for coverage,
  * identifiability: which groups are confounded (posterior correlations).
"""
from __future__ import annotations

import numpy as np


class LesionPosterior:
    def __init__(self, group_names: list[str], seed: int = 0):
        self.group_names = group_names
        self.seed = seed
        self._posterior = None

    def fit(self, theta: np.ndarray, x: np.ndarray, density: str = "nsf", epochs: int | None = None):
        import torch
        from sbi.inference import NPE
        from sbi.utils import BoxUniform

        torch.manual_seed(self.seed)
        K = theta.shape[1]
        prior = BoxUniform(low=torch.zeros(K), high=torch.ones(K))
        inf = NPE(prior=prior, density_estimator=density)
        inf.append_simulations(torch.as_tensor(theta, dtype=torch.float32),
                               torch.as_tensor(x, dtype=torch.float32))
        est = inf.train(max_num_epochs=epochs) if epochs else inf.train()
        self._posterior = inf.build_posterior(est)
        return self

    def sample(self, x_obs: np.ndarray, n: int = 2000) -> np.ndarray:
        import torch
        if self._posterior is None:
            raise RuntimeError("call fit first")
        s = self._posterior.sample((n,), x=torch.as_tensor(x_obs, dtype=torch.float32), show_progress_bars=False)
        return s.numpy()

    def summarize(self, x_obs: np.ndarray, n: int = 2000) -> dict[str, tuple[float, float, float]]:
        s = self.sample(x_obs, n)
        return {g: (float(np.median(s[:, i])), float(np.quantile(s[:, i], 0.05)), float(np.quantile(s[:, i], 0.95)))
                for i, g in enumerate(self.group_names)}
