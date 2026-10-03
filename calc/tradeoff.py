#!/usr/bin/env python3
"""
Design trade-off: moving mass vs frequency vs valve vs vibration.

The modules so far surfaced a tension:
  * the engine self-selects ~40 Hz at 1 kg (dynamics.py);
  * at 40 Hz the 25 g transfer valve is inertia-bound and will not open
    (valves.py) -- you need <=~10 g;
  * frequency moves as 1/sqrt(mass), and vibration / valve inertia scale with
    acceleration (~omega^2), so mass is the master knob.

This script sweeps the moving mass, holds the amplitude roughly constant by
tuning the generator load (a fair comparison), and reports for each mass:
limit-cycle frequency, vibration force, the heaviest workable transfer-valve
mass, peak pressure and electrical power. It marks where the heaviest workable
valve reaches the design's 25 g.

    python3 tradeoff.py [--no-plots]

All 0D, seed-driven -- the trends are the message, not the absolute numbers.
"""

import os
import sys
import numpy as np

from params import Params
import dynamics
import valves

OUT = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT, exist_ok=True)

TARGET_AMP_MM = 18.0        # hold amplitude here by tuning load (fair compare)


def tune_load_for_amplitude(mass, target_mm=TARGET_AMP_MM, dt=3e-6, t_end=2.2):
    """Bisect generator load so the limit-cycle amplitude ~= target (mass fixed)."""
    lo, hi = 80.0, 320.0
    best = None
    for _ in range(20):
        c = 0.5 * (lo + hi)
        p = Params(); p.m_moving = mass; p.c_gen = c
        m = dynamics.simulate(p, dt=dt, t_end=t_end)["metrics"]
        if m["v_peak"] < 0.1:          # died (load too high) -> reduce load
            hi = c
            continue
        best = (c, m)
        if m["amplitude_mm"] > target_mm:   # too big -> more load
            lo = c
        else:
            hi = c
    return best


def study(masses):
    rows = []
    for mass in masses:
        tuned = tune_load_for_amplitude(mass)
        if tuned is None:
            continue
        c, _ = tuned
        p = Params(); p.m_moving = mass; p.c_gen = c
        res = dynamics.simulate(p, dt=2e-6, t_end=2.5)
        m = res["metrics"]
        m_thr = valves.threshold_mass(res)
        rows.append({
            "mass_kg": mass,
            "c_gen": round(c, 0),
            "freq_hz": round(m["freq_hz"], 1),
            "amp_mm": round(m["amplitude_mm"], 1),
            "vib_N": round(m["vib_force_N"], 0),
            "valve_g": round(m_thr * 1e3, 1) if not np.isnan(m_thr) else float("nan"),
            "pcomb_bar": round(m["p_comb_peak_bar"], 1),
            "Pel_W": round(m["P_elec_W"], 0),
        })
    return rows


def make_plot(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    mass = [r["mass_kg"] for r in rows]
    freq = [r["freq_hz"] for r in rows]
    vib = [r["vib_N"] for r in rows]
    valve = [r["valve_g"] for r in rows]
    pel = [r["Pel_W"] for r in rows]

    fig, ax = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("NIC-FPLG  --  mass vs frequency vs valve vs vibration "
                 "(amplitude held ~18 mm)", fontweight="bold")

    ax[0, 0].plot(mass, freq, "o-", c="tab:purple")
    ax[0, 0].set(xlabel="moving mass [kg]", ylabel="frequency [Hz]",
                 title="Frequency ~ 1/sqrt(mass)")

    ax[0, 1].plot(mass, valve, "o-", c="tab:red", label="heaviest workable valve")
    ax[0, 1].axhline(25, ls="--", c="k", lw=1.0, label="design 25 g valve")
    ax[0, 1].set(xlabel="moving mass [kg]", ylabel="max valve mass [g]",
                 title="Valve gets easier as mass rises (lower f)")
    ax[0, 1].legend(fontsize=8)

    ax[1, 0].plot(mass, vib, "o-", c="tab:orange")
    ax[1, 0].set(xlabel="moving mass [kg]", ylabel="vibration force [N]",
                 title="Vibration force (m*a_peak)")

    ax[1, 1].plot(mass, pel, "o-", c="tab:green")
    ax[1, 1].set(xlabel="moving mass [kg]", ylabel="electrical power [W]",
                 title="Power")
    for a in ax.flat:
        a.grid(alpha=0.3)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    path = os.path.join(OUT, "tradeoff.png")
    fig.savefig(path, dpi=110); plt.close(fig)
    return path


def main():
    do_plots = "--no-plots" not in sys.argv
    masses = [0.45, 0.55, 0.7, 0.85, 1.0, 1.15, 1.3]
    print("sweeping moving mass (amplitude held ~18 mm by load tuning) ...\n")
    rows = study(masses)

    print(f"  {'mass':>6} {'c_gen':>6} {'f[Hz]':>6} {'amp':>5} {'vib[N]':>7} "
          f"{'valve[g]':>9} {'pcomb':>6} {'P_el[W]':>8}")
    for r in rows:
        vg = f"{r['valve_g']:.1f}" if not np.isnan(r["valve_g"]) else "  none"
        print(f"  {r['mass_kg']:6.2f} {r['c_gen']:6.0f} {r['freq_hz']:6.1f} "
              f"{r['amp_mm']:5.1f} {r['vib_N']:7.0f} {vg:>9} "
              f"{r['pcomb_bar']:6.1f} {r['Pel_W']:8.0f}")

    # where does the workable valve reach 25 g?
    good = [r for r in rows if not np.isnan(r["valve_g"])]
    reach = [r for r in good if r["valve_g"] >= 25.0]
    print()
    if reach:
        r = min(reach, key=lambda r: r["mass_kg"])
        print(f"  => the STOCK 25 g valve transfers from ~{r['mass_kg']:.2f} kg "
              f"({r['freq_hz']:.0f} Hz) upward.")
        print("     With a 1 N seat spring and ~2.5:1 pre-compression the valve is")
        print("     NOT the binding constraint -- no special part needed.")
    else:
        hv = max(good, key=lambda r: r["valve_g"])
        print(f"  => even at {hv['mass_kg']:.2f} kg ({hv['freq_hz']:.0f} Hz) the "
              f"workable valve is only {hv['valve_g']:.0f} g < 25 g "
              f"(raise pre-compression).")
    print("  Trade: lighter mass = higher f, more power AND lower vibration force")
    print("  (at fixed amplitude the shaker force tracks the ~constant combustion")
    print("  force, so heavier mass does NOT reduce it -- it slightly rises).")
    print("  So lighter is better for power and vibration; pre-compression sets")
    print("  the valve's inertial delay independently of mass.")
    if do_plots:
        try:
            print(f"\n  -> {make_plot(rows)}")
        except Exception as e:
            print(f"  (plot skipped: {e})")


if __name__ == "__main__":
    main()
