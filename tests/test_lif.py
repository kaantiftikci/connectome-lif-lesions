import numpy as np
import scipy.sparse as sp

from sinek.sim import LIFParams, simulate, firing_rates


def net(edges, n):
    W = sp.csr_matrix((np.array([w for *_, w in edges], float),
                       ([a for a, *_ in edges], [b for _, b, *_ in edges])), shape=(n, n))
    return W


def test_silent_without_input():
    rec = simulate(net([(0, 1, 5.0)], 2), duration=200.0, seed=1)
    assert rec.times.size == 0


def test_poisson_driven_neuron_fires_near_input_rate():
    rec = simulate(net([], 1), duration=2000.0, poisson=np.array([0]), poisson_rate=150.0, seed=1)
    r = firing_rates(rec)[0]
    assert 100 < r < 200          # every Poisson event (68.75 mV) crosses threshold


def test_excitation_drives_postsynaptic_and_inhibition_does_not():
    exc = net([(0, 1, 275 * 0.275)], 2)     # 275 synapses, +
    inh = net([(0, 1, -275 * 0.275)], 2)
    r_exc = firing_rates(simulate(exc, 1000.0, poisson=np.array([0]), seed=2))
    r_inh = firing_rates(simulate(inh, 1000.0, poisson=np.array([0]), seed=2))
    assert r_exc[1] > 20
    assert r_inh[1] == 0


def test_inhibition_reduces_rate():
    # 0 -> 2 strong excitation, 1 -> 2 inhibition; both driven
    base = net([(0, 2, 100 * 0.275)], 3)
    with_inh = net([(0, 2, 100 * 0.275), (1, 2, -100 * 0.275)], 3)
    r0 = firing_rates(simulate(base, 1000.0, poisson=np.array([0, 1]), seed=3))[2]
    r1 = firing_rates(simulate(with_inh, 1000.0, poisson=np.array([0, 1]), seed=3))[2]
    assert r1 < r0


def test_synaptic_delay():
    p = LIFParams()
    W = net([(0, 1, 1000.0)], 2)
    rec = simulate(W, 20.0, p, poisson={0: 1e9}, seed=0)   # neuron 0 fires every step
    t1 = rec.times[rec.ids == 1]
    t0 = rec.times[rec.ids == 0]
    assert t0[0] == 0.0
    assert np.isclose(t1[0], p.t_dly, atol=p.dt + 1e-9)


def test_refractory_limits_rate():
    p = LIFParams(t_rfc=2.2)
    W = net([(0, 1, 1000.0)], 2)
    rec = simulate(W, 1000.0, p, poisson={0: 1e9}, seed=0)
    r1 = firing_rates(rec)[1]
    assert r1 <= 1000.0 / p.t_rfc + 1
    assert r1 > 300
