#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
First-cut exhaust acoustics / Y-junction ejector (DESIGN ch.9 / OQ-A5).

Question: do the alternating exhaust pulses, cross-coupled through the Y, give a
useful suction (ejector) to scavenge the other cylinder -- or is a tuned pipe even
possible at this engine's frequency?

Method (1D acoustics, first cut):
  * speed of sound in hot exhaust gas
  * wavelength and quarter-wave length at the firing frequency
  * pulse travel time down a branch vs the half-cycle offset between cylinders
"""
import math
from params import Params
import dynamics

R_GAS = 287.0         # J/kg/K
GAMMA = 1.33          # exhaust gas
T_EXH = 1200.0        # K, mean exhaust gas temperature (seed)


def main():
    p = Params()
    m = dynamics.simulate(p, dt=3e-6, t_end=2.2)["metrics"]
    f_mech = m["freq_hz"]                       # each cylinder fires at f_mech
    T_cycle = 1.0 / f_mech

    a = math.sqrt(GAMMA * R_GAS * T_EXH)        # speed of sound, m/s
    wavelength = a / f_mech
    quarter = wavelength / 4.0
    # cylinders fire half a cycle apart -> for A's pulse to reach B's scavenge
    # window, the branch travel time should be ~ T_cycle/2
    L_ideal = a * (T_cycle / 2.0)

    print("=" * 64)
    print("  EXHAUST ACOUSTICS / Y-EJECTOR  (ch.9 / OQ-A5)")
    print("=" * 64)
    print(f"  firing freq per cyl        {f_mech:6.0f} Hz  (cycle {T_cycle*1e3:.1f} ms)")
    print(f"  exhaust gas ({T_EXH:.0f} K)      sound speed {a:6.0f} m/s")
    print("-" * 64)
    print(f"  wavelength at firing freq  {wavelength:6.1f} m")
    print(f"  quarter-wave (tuned pipe)  {quarter:6.1f} m")
    print(f"  branch length for half-cyc {L_ideal:6.1f} m")
    print("=" * 64)
    print("  READING:")
    print(f"  At {f_mech:.0f} Hz the wavelength is ~{wavelength:.0f} m and a tuned (quarter-")
    print(f"  wave) pipe would need ~{quarter:.1f} m -- impossible in a compact engine.")
    print("  So a CLASSIC TUNED EXHAUST IS OFF THE TABLE at this frequency, which")
    print("  confirms the DESIGN's OPEN exhaust (ch.9): the engine does not lose charge")
    print("  to the pipe (stratified, ch.4), so it needs no tuned expansion chamber to")
    print("  return it.")
    print("  The Y-ejector, if it helps at all, is a direct PULSE cross-coupling effect")
    print("  (one branch's blowdown momentarily lowering pressure at the other), not an")
    print("  acoustic resonance -- a mild, velocity-driven bonus at best. Whether it is")
    print("  worth the plumbing = unsteady 1D / CFD (OQ-A5); this calc just shows it is")
    print("  NOT a resonance you can tune at this frequency.")


if __name__ == "__main__":
    main()
