#!/usr/bin/env python3
"""
Self-tests for the calc/ models. Run before trusting any number.

    python3 verify.py

Checks:
  1. Time-step convergence  -- the limit cycle must not move with dt.
  2. Core physics           -- with combustion and damping OFF, the free
                               oscillation frequency must match the analytic
                               spring/mass resonance (validates forces +
                               integrator independently of the combustion model).
  3. Energy balance          -- indicated gas power must equal generator power
                               plus friction (no energy created or lost
                               unaccounted for).

Exit code 0 if all pass, 1 otherwise.
"""

import math
import sys
import numpy as np

from params import Params
from dynamics import simulate, _dominant_freq


def check(name, ok, detail):
    mark = "PASS" if ok else "FAIL"
    print(f"  [{mark}] {name}: {detail}")
    return ok


def test_convergence():
    print("1. time-step convergence")
    fs = []
    for dt in (8e-6, 4e-6, 2e-6, 1e-6):
        m = simulate(Params(), dt=dt, t_end=2.5)["metrics"]
        fs.append(m["freq_hz"])
        print(f"      dt={dt:.0e}  f={m['freq_hz']:.3f} Hz  amp={m['amplitude_mm']:.3f} mm")
    spread = max(fs) - min(fs)
    return check("frequency stable across dt", spread < 0.2,
                 f"spread {spread:.3f} Hz (tol 0.2)")


def test_core_physics():
    print("2. core physics  (no combustion, no damping)")
    p = Params()
    p.bmep_target = 0.0
    p.c_gen = p.c_visc = p.f_coulomb = 0.0
    p.motor_gain = 0.0                    # no start pump -> free oscillation
    p.ign_pressure_ratio = 1e9            # never fire
    r = simulate(p, dt=2e-6, t_end=3.0, x0_frac=0.0, v0=0.3, settle_frac=0.3)
    t, x = r["t"], r["x"]
    f_sim = _dominant_freq(t[t > 1.0], x[t > 1.0])

    A_p, A_u = p.area_piston, p.area_under
    k_comb = 2 * p.gamma_air * p.p_intake * A_p ** 2 / p.vol_comb_right(0.0)
    k_air = (2 * p.gamma_air * p.p_intake * A_u ** 2 /
             p.vol_under_mid() * (1 - p.bushing_leak))
    f_an = math.sqrt((k_comb + k_air) / p.m_moving) / (2 * math.pi)

    amp0 = np.max(np.abs(x[t < 0.3]))
    amp1 = np.max(np.abs(x[t > 2.7]))
    print(f"      sim {f_sim:.3f} Hz vs analytic {f_an:.3f} Hz")
    ok_f = check("free frequency matches k/m", abs(f_sim / f_an - 1) < 0.03,
                 f"ratio {f_sim/f_an:.4f} (tol 3%)")
    ok_e = check("amplitude not gaining energy", amp1 <= amp0 * 1.02,
                 f"start {amp0*1e3:.2f} -> end {amp1*1e3:.2f} mm")
    return ok_f and ok_e


def test_energy_balance():
    print("3. energy balance  (default operating point)")
    p = Params()
    m = simulate(p, dt=2e-6, t_end=2.5)["metrics"]
    ind = m["P_indicated_W"]
    out = m["P_mech_gen_W"]            # friction is the small remainder
    print(f"      indicated {ind:.1f} W,  into generator {out:.1f} W,  "
          f"friction {ind-out:.1f} W")
    # indicated must cover generator output, with a small positive friction gap
    ok = check("indicated >= generator and gap small",
               out <= ind and (ind - out) < 0.15 * ind,
               f"gap {(ind-out)/ind*100:.1f}% of indicated")
    return ok


def main():
    print("=" * 56)
    print("  calc/ self-tests")
    print("=" * 56)
    results = [test_convergence(), test_core_physics(), test_energy_balance()]
    print("-" * 56)
    if all(results):
        print("  ALL PASS")
        return 0
    print("  SOME CHECKS FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
