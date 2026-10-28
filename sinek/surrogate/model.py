"""Differentiable surrogate of the simulator: theta (lesion) -> x (phenotype).

A small MLP ensemble (deep-ensemble uncertainty) trained on simulator runs.
Two uses the reference lesion study does not have:

1. **Reverse screen** — gradient search over *all* K groups for the sparsest
   lesion that reproduces a target phenotype signature (e.g. "which non-DA
   loss mimics PPL1 loss?").
2. **Sensitivity map** — d x / d theta at theta = 0 ranks groups by how much
   their loss moves each readout, in one backward pass instead of K sweeps.

torch is imported lazily so the simulator side of the package runs without it.
"""
from __future__ import annotations

import numpy as np


def _torch():
    import torch  # noqa: WPS433
    return torch


class Surrogate:
    def __init__(self, n_in: int, n_out: int, hidden: int = 256, n_members: int = 5, seed: int = 0):
        torch = _torch()
        nn = torch.nn
        self.n_in, self.n_out = n_in, n_out
        self.members = []
        for m in range(n_members):
            torch.manual_seed(seed + m)
            self.members.append(nn.Sequential(
                nn.Linear(n_in, hidden), nn.SiLU(),
                nn.Linear(hidden, hidden), nn.SiLU(),
                nn.Linear(hidden, n_out)))
        self.x_mu = np.zeros(n_out, np.float32)
        self.x_sd = np.ones(n_out, np.float32)

    def fit(self, theta: np.ndarray, x: np.ndarray, epochs: int = 500, lr: float = 1e-3,
            batch: int = 256, verbose: bool = False):
        torch = _torch()
        self.x_mu = x.mean(0).astype(np.float32)
        self.x_sd = (x.std(0) + 1e-6).astype(np.float32)
        th = torch.as_tensor(theta, dtype=torch.float32)
        xx = torch.as_tensor((x - self.x_mu) / self.x_sd, dtype=torch.float32)
        n = len(th)
        for mi, net in enumerate(self.members):
            opt = torch.optim.Adam(net.parameters(), lr=lr)
            g = torch.Generator().manual_seed(mi)
            for ep in range(epochs):
                perm = torch.randperm(n, generator=g)
                for i in range(0, n, batch):
                    b = perm[i:i + batch]
                    loss = torch.mean((net(th[b]) - xx[b]) ** 2)
                    opt.zero_grad(); loss.backward(); opt.step()
                if verbose and ep % 100 == 0:
                    print(f"member {mi} epoch {ep} loss {loss.item():.4f}")
        return self

    def predict(self, theta: np.ndarray):
        """Return (mean, std) over ensemble members, in original x units."""
        torch = _torch()
        th = torch.as_tensor(np.atleast_2d(theta), dtype=torch.float32)
        with torch.no_grad():
            preds = torch.stack([net(th) for net in self.members]).numpy()
        preds = preds * self.x_sd + self.x_mu
        return preds.mean(0), preds.std(0)

    def sensitivity(self, theta0: np.ndarray | None = None) -> np.ndarray:
        """Jacobian d x / d theta (n_out, n_in) averaged over members."""
        torch = _torch()
        th = torch.zeros(1, self.n_in) if theta0 is None else torch.as_tensor(np.atleast_2d(theta0), dtype=torch.float32)
        th.requires_grad_(True)
        J = np.zeros((self.n_out, self.n_in), np.float32)
        for net in self.members:
            for j in range(self.n_out):
                out = net(th)[0, j]
                (grad,) = torch.autograd.grad(out, th, retain_graph=True)
                J[j] += grad[0].numpy() * self.x_sd[j]
        return J / len(self.members)

    def reverse_screen(self, x_target: np.ndarray, l1: float = 0.05, steps: int = 2000, lr: float = 0.05,
                       exclude: list[int] | None = None, seed: int = 0) -> np.ndarray:
        """Sparsest lesion theta in [0,1]^K whose predicted phenotype matches x_target."""
        torch = _torch()
        torch.manual_seed(seed)
        xt = torch.as_tensor((x_target - self.x_mu) / self.x_sd, dtype=torch.float32)
        logit = torch.full((1, self.n_in), -3.0, requires_grad=True)
        mask = torch.ones(self.n_in)
        if exclude:
            mask[exclude] = 0.0
        opt = torch.optim.Adam([logit], lr=lr)
        for _ in range(steps):
            th = torch.sigmoid(logit) * mask
            pred = torch.stack([net(th) for net in self.members]).mean(0)
            loss = torch.mean((pred - xt) ** 2) + l1 * th.sum()
            opt.zero_grad(); loss.backward(); opt.step()
        return (torch.sigmoid(logit) * mask).detach().numpy()[0]
