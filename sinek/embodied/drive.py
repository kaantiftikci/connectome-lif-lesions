"""Brain -> body interface: descending-neuron population rates to a two-sided
locomotor drive for the NeuroMechFly turning controller.

The descending neurons (DNs) are the only route from brain to ventral nerve
cord, so their population activity is the natural place to cut the brain
model and hand over to the body model.  The mapping used here is deliberately
simple and stated as a modelling assumption:

    drive_side = clip( rate_side(lesioned) / rate_side(intact), 0, 1.5 )

so the intact brain under the same stimulus gives drive (1, 1), i.e. nominal
walking (~12 mm/s in the controller), and a lesion that halves descending
output halves the drive.  Two readout populations are reported: all DNs per
side, and a small set of DN types with published roles in walking.
"""
from __future__ import annotations

import numpy as np

from ..data.flywire import Connectome

# Types with published roles in forward walking / steering (checked present in FlyWire v783).
LOCOMOTOR_DN_TYPES = ["DNp09", "DNa01", "DNa02", "DNa03", "DNb01", "DNb02", "DNg13"]


def descending_sides(cn: Connectome, types: list[str] | None = None) -> dict[str, np.ndarray]:
    m = cn.meta
    dn = m["super_class"] == "descending"
    if types is not None:
        dn &= m["cell_type"].astype(str).isin(types)
    return {"left": m.loc[dn & (m["side"] == "left"), "idx"].to_numpy(),
            "right": m.loc[dn & (m["side"] == "right"), "idx"].to_numpy()}


def descending_rates(rates: np.ndarray, sides: dict[str, np.ndarray]) -> np.ndarray:
    """Mean firing rate (Hz) of the left and right DN populations."""
    return np.array([rates[sides["left"]].mean(), rates[sides["right"]].mean()])


def descending_drive(rates_lesioned: np.ndarray, rates_intact: np.ndarray, floor_hz: float = 0.05,
                     clip: tuple[float, float] = (0.0, 1.5)) -> np.ndarray:
    """Two-sided drive relative to the intact brain under the same stimulus."""
    ref = np.maximum(rates_intact, floor_hz)
    return np.clip(rates_lesioned / ref, *clip)
