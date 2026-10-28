"""Run the NeuroMechFly (flygym 2.x) hybrid turning controller with a constant
two-sided descending drive and report locomotion metrics.

``tilt_deg`` rotates gravity so that +x (the fly's forward axis at spawn) is
uphill: 0 = flat ground, 60 = steep slope, 90 = vertical wall (needs leg
adhesion).  ``climbed_mm`` is forward displacement on the tilted ground, the
quantity the negative-geotaxis (RING) assay scores in real flies.

Requires ``pip install "flygym @ git+https://github.com/NeLy-EPFL/flygym.git@v2.1.1"``
(the PyPI wheel lacks the ``flygym_demo`` controllers) and ``MUJOCO_GL=`` (empty)
for a headless machine without EGL.
"""
from __future__ import annotations

import os

import numpy as np

os.environ.setdefault("MUJOCO_GL", "")


def walk(signal, duration: float = 1.0, tilt_deg: float = 0.0, seed: int = 0, warmup: bool = True,
         adhesion_gain: float = 40.0) -> dict:
    from flygym import Simulation
    from flygym.anatomy import BodySegment, ContactBodiesPreset
    from flygym.compose import FlatGroundWorld
    from flygym.utils.math import Rotation3D
    from flygym_demo.complex_terrain import (HybridTurningController, HybridControllerObservation,
                                             LocomotionAction, PreprogrammedSteps, apply_locomotion_action,
                                             make_locomotion_fly)

    signal = np.asarray(signal, dtype=float)
    fly = make_locomotion_fly(name="fly", add_adhesion=True, adhesion_gain=adhesion_gain)
    world = FlatGroundWorld()
    world.add_fly(fly, [0, 0, 0.8], Rotation3D("quat", [1, 0, 0, 0]),
                  bodysegs_with_ground_contact=ContactBodiesPreset.TIBIA_TARSUS_ONLY,
                  add_ground_contact_sensors=False)
    sim = Simulation(world)
    if tilt_deg:
        g = float(np.linalg.norm(sim.mj_model.opt.gravity))
        th = np.deg2rad(tilt_deg)
        sim.mj_model.opt.gravity[:] = [-g * np.sin(th), 0.0, -g * np.cos(th)]
    steps = PreprogrammedSteps()
    dof = fly.get_actuated_jointdofs_order("position")
    ctrl = HybridTurningController(timestep=sim.timestep, preprogrammed_steps=steps, output_dof_order=dof)
    thorax = fly.get_bodysegs_order().index(BodySegment("c_thorax"))

    sim.reset(); ctrl.reset(seed=seed)
    apply_locomotion_action(sim, fly.name, LocomotionAction(
        joint_angles=steps.default_pose_by_dof_order(dof), adhesion_onoff=np.ones(6, dtype=bool)))
    if warmup:
        sim.warmup()
    p0 = sim.get_body_positions(fly.name)[thorax].copy()
    n = int(round(duration / sim.timestep))
    zs = []
    for k in range(n):
        obs = HybridControllerObservation.from_sim(sim, fly.name)
        apply_locomotion_action(sim, fly.name, ctrl.step(signal, obs))
        sim.step()
        if k % 1000 == 0:
            zs.append(sim.get_body_positions(fly.name)[thorax][2])
    p1 = sim.get_body_positions(fly.name)[thorax]
    d = p1 - p0
    return {"forward_mm": float(d[0]), "lateral_mm": float(d[1]), "speed_mm_s": float(d[0] / duration),
            "climbed_mm": float(d[0]) if tilt_deg else 0.0, "min_height_mm": float(np.min(zs)),
            "fell": bool(np.min(zs) < 0.2), "tilt_deg": tilt_deg, "drive_left": float(signal[0]),
            "drive_right": float(signal[1])}
