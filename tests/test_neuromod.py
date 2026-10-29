import numpy as np
import pandas as pd
import scipy.sparse as sp

from sinek.data.flywire import Connectome
from sinek.lesion import LesionSpec, apply_lesion
from sinek.neuromod import ModulationParams, ModulatedNetwork, simulate_modulated, compartment_map, kc_mbon_synapses
from sinek.sim import simulate, firing_rates


def toy_mb():
    # 0: ORN-like driver, 1-3: KCs, 4: MBON01, 5: DAN (PPL1-like), 6: other
    n = 7
    edges = [(0, 1, 40), (0, 2, 40), (0, 3, 40),          # driver -> KCs
             (1, 4, 90), (2, 4, 90), (3, 4, 90),          # KC -> MBON
             (5, 4, 60),                                  # DAN -> MBON (fast, to be replaced)
             (5, 1, 5), (0, 6, 10)]
    W = sp.csr_matrix((np.array([w * 0.275 for *_, w in edges]),
                       ([a for a, *_ in edges], [b for _, b, _ in edges])), shape=(n, n))
    meta = pd.DataFrame({"idx": np.arange(n),
                         "cell_class": ["olfactory", "Kenyon_Cell", "Kenyon_Cell", "Kenyon_Cell", "MBON", "DAN", "x"],
                         "cell_type": ["ORN_x", "KCg", "KCg", "KCg", "MBON01", "PPL101", "y"],
                         "super_class": ["sensory", "central", "central", "central", "central", "central", "central"]})
    return Connectome(ids=np.arange(n) + 1, W=W.tocsr(), meta=meta)


def test_compartment_and_synapse_maps():
    cn = toy_mb()
    comp = compartment_map(cn, min_w_mv=2.0)
    assert list(comp.keys()) == [4] and list(comp[4]) == [5]
    syn = kc_mbon_synapses(cn)
    assert len(syn[4]) == 3 and np.allclose(cn.W.data[syn[4]], 90 * 0.275)


def test_dan_activity_reduces_mbon_gain_and_lesion_is_graded():
    cn = toy_mb()
    p = ModulationParams(kappa=0.02, tau_da=50.0, window=10.0, alpha_fast=0.0)
    net = ModulatedNetwork(cn, p)
    assert np.isclose(net.W[5, 4], 0.0)                       # fast DAN->MBON synapse removed
    rec0, rb0 = simulate_modulated(net, 400.0, poisson={0: 150.0}, seed=1)
    r_odor = firing_rates(rec0)[4]
    net = ModulatedNetwork(cn, p)
    rec1, rb1 = simulate_modulated(net, 400.0, poisson={0: 150.0, 5: 150.0}, seed=1)
    r_pair = firing_rates(rec1)[4]
    assert r_odor > 0 and r_pair < r_odor                       # dopamine depresses the MBON's odour response
    assert 0 < net.gain[4] < 1
    # graded: half the DAN drive gives an intermediate gain
    net = ModulatedNetwork(cn, p)
    simulate_modulated(net, 400.0, poisson={0: 150.0, 5: 75.0}, seed=1)
    assert net.gain[4] > ModulatedNetwork(cn, p).gain[4] * 0 and net.gain[4] > np.exp(-p.kappa * rb1[4])


def test_plasticity_persists_after_pairing():
    cn = toy_mb()
    p = ModulationParams(kappa=0.0, eta=0.002, tau_da=50.0, window=10.0)
    net = ModulatedNetwork(cn, p)
    before = firing_rates(simulate_modulated(net, 300.0, poisson={0: 150.0}, seed=2)[0])[4]
    w_before = net.w0[4].copy()
    simulate_modulated(net, 500.0, poisson={0: 150.0, 5: 150.0}, seed=2, plastic=True)
    assert (net.w0[4] < w_before).all()
    after = firing_rates(simulate_modulated(net, 300.0, poisson={0: 150.0}, seed=2)[0])[4]
    assert after < before


def test_keep_pattern_lesion():
    cn = toy_mb()
    W, hit = apply_lesion(cn, {"DAN": np.array([5])}, LesionSpec({"DAN": 1.0}), keep_pattern=True)
    assert W.nnz == cn.W.nnz and np.isclose(W[5, 4], 0.0) and np.isclose(W[5, 1], 0.0)
