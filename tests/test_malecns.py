import numpy as np
import pandas as pd

from sinek.data.malecns import build_connectome
from sinek.data import group_indices, DA_GROUPS
from sinek.neuromod import compartment_map


def test_build_connectome_from_mock_tables():
    neurons = pd.DataFrame({
        "bodyId": [10, 11, 12, 13, 14, 15],
        "type": ["PAM08", "KCg-m", "MBON29", "DNp09", "ORN_DM1", "PPL103"],
        "class": [None, None, None, None, None, "DAN"],
        "superclass": ["central", "central", "central", "descending", "sensory", "central"],
        "somaSide": ["L", "R", "L", "R", "M", "L"],
        "predictedNt": ["dopamine", "acetylcholine", "glutamate", "acetylcholine", "acetylcholine", "dopamine"],
    })
    edges = pd.DataFrame({"bodyId_pre": [14, 11, 10, 12, 15, 99], "bodyId_post": [11, 12, 12, 13, 12, 12],
                          "weight": [40, 90, 60, 10, 5, 7]})
    cn = build_connectome(neurons, edges)
    assert cn.n == 6 and cn.W.nnz == 5                                   # unknown body 99 dropped
    assert cn.meta.loc[0, "cell_class"] == "DAN" and cn.meta.loc[1, "cell_class"] == "Kenyon_Cell"
    assert cn.meta.loc[0, "side"] == "left" and cn.meta.loc[4, "side"] == "center"
    assert np.isclose(cn.W[2, 3], -10 * 0.275)                          # glutamatergic MBON -> inhibitory
    assert np.isclose(cn.W[0, 2], 60 * 0.275)
    g = group_indices(cn, DA_GROUPS)
    assert list(g["PAM"]) == [0] and list(g["PPL1"]) == [5]
    comp = compartment_map(cn, min_w_mv=2.0)
    assert set(comp[2].tolist()) == {0}                                 # PAM08 (16.5 mV) in, PPL103 (1.4 mV) out
