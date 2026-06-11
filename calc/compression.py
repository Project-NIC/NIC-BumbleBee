#!/usr/bin/env python3
"""
Amplitude -> effective compression -> efficiency  (DESIGN ch.4 / item 1).

thermo.py surfaced the key point: the *effective* compression ratio is set by
how close the piston gets to the head, not by the geometric ratio. At the
default operating point the piston reverses ~18 mm short of full stroke, so the
trapped compression is only ~3.5:1 and efficiency suffers.

This script makes that a design curve: it tunes the generator load to run the
engine at a range of amplitudes (closer and closer to the head), and for each
runs the 0D thermodynamic cycle. Output: effective compression ratio, thermal
efficiency, peak pressure and head clearance vs amplitude — i.e. how much
efficiency you buy by running closer to the head, and what it costs in peak
pressure.

    python3 compression.py [--no-plots]

The squish design (ch.4) wants ~1 mm clearance at the head; the sweep stops
short of contact. Still 0D.
"""

import os
import sys
import numpy as np

from params import Params, BAR, CC
import dynamics
import thermo

OUT = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT, exist_ok=True)


def tune_load(target_mm, dt=4e-6, t_end=1.8):
    """Light bisection of generator load to hit a target amplitude (default mass)."""
    lo, hi = 70.0, 320.0
    best = None
    for _ in range(14):
        c = 0.5 * (lo + hi)
        p = Params(); p.c_gen = c
        m = dynamics.simulate(p, dt=dt, t_end=t_end)["metrics"]
        if m["v_peak"] < 0.1:           # died -> too much load
            hi = c
            continue
        best = c
        if m["amplitude_mm"] > target_mm:
            lo = c                      # bigger than target -> more load
        else:
            hi = c
    return best


def study(targets_mm):
    rows = []
    for tgt in targets_mm:
        c = tune_load(tgt)
        if c is None:
            continue
        p = Params(); p.c_gen = c
        km = thermo.kinematics(p)
        if not np.isfinite(km[5]) or km[5] <= 0:   # period (engine alive?)
            continue
        cyc = thermo.run_cycle(km, phi=0.8)
        Vmin = cyc["V"].min(); Vmax = cyc["V"].max()
        amp = km[1].max() * 1e3         # actual amplitude [mm] (max x of period)
        if not (np.isfinite(amp) and np.isfinite(cyc["eta"])):
            continue
        rows.append({
            "amp_mm": round(amp, 1),
            "head_clear_mm": round(p.x_max * 1e3 - amp, 1),
            "cr_eff": round(Vmax / Vmin, 2),
            "eff_pct": round(cyc["eta"] * 100, 1),
            "peakP_bar": round(cyc["peakP"] / BAR, 1),
            "peakT_K": round(cyc["peakT"], 0),
            "work_J": round(cyc["work"], 1),
            "P_ind_W": round(cyc["P_ind"], 0),
            "c_gen": round(c, 0),
        })
    return rows


def make_plot(rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    amp = [r["amp_mm"] for r in rows]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    fig.suptitle("NIC-FPLG  --  running closer to the head buys efficiency "
                 "(ch.4 / item 1)", fontweight="bold")

    a0 = ax[0]
    a0.plot(amp, [r["eff_pct"] for r in rows], "o-", c="tab:red",
            label="thermal eff [%]")
    a0.set(xlabel="amplitude [mm]", ylabel="thermal efficiency [%]",
           title="Efficiency vs amplitude")
    a0.grid(alpha=0.3)
    a0b = a0.twinx()
    a0b.plot(amp, [r["cr_eff"] for r in rows], "s--", c="tab:blue",
             label="effective CR")
    a0b.set_ylabel("effective compression ratio")
    lines = a0.get_lines() + a0b.get_lines()
    a0.legend(lines, [l.get_label() for l in lines], fontsize=8, loc="upper left")

    a1 = ax[1]
    a1.plot(amp, [r["peakP_bar"] for r in rows], "o-", c="tab:purple")
    a1.set(xlabel="amplitude [mm]", ylabel="peak pressure [bar]",
           title="…at the cost of peak pressure")
    a1.axvline(Params().x_max * 1e3, ls="--", c="grey", lw=0.8, label="head")
    a1.legend(fontsize=8); a1.grid(alpha=0.3)

    fig.tight_layout(rect=(0, 0, 1, 0.94))
    path = os.path.join(OUT, "compression.png")
    fig.savefig(path, dpi=110); plt.close(fig)
    return path


def main():
    do_plots = "--no-plots" not in sys.argv
    targets = [17, 19, 21, 22, 23]
    print("tuning generator load to run at each amplitude, then 0D cycle ...\n")
    rows = study(targets)

    print(f"  {'amp[mm]':>7} {'head[mm]':>8} {'CR_eff':>7} {'eff[%]':>7} "
          f"{'peakP':>6} {'peakT':>6} {'P_ind[W]':>9}")
    for r in rows:
        print(f"  {r['amp_mm']:7.1f} {r['head_clear_mm']:8.1f} {r['cr_eff']:7.2f} "
              f"{r['eff_pct']:7.1f} {r['peakP_bar']:6.1f} {r['peakT_K']:6.0f} "
              f"{r['P_ind_W']:9.0f}")

    if len(rows) >= 2:
        lo, hi = rows[0], rows[-1]
        d_eff = hi["eff_pct"] - lo["eff_pct"]
        print()
        print(f"  Running from {lo['amp_mm']:.0f} mm to {hi['amp_mm']:.0f} mm "
              f"(head clearance {hi['head_clear_mm']:.0f} mm) lifts the effective")
        print(f"  compression {lo['cr_eff']:.1f} -> {hi['cr_eff']:.1f} and thermal "
              f"efficiency {lo['eff_pct']:.0f}% -> {hi['eff_pct']:.0f}% "
              f"(+{d_eff:.0f} points),")
        print(f"  for a peak-pressure rise {lo['peakP_bar']:.0f} -> "
              f"{hi['peakP_bar']:.0f} bar. So efficiency is an amplitude setpoint")
        print("  decision (ch.12 load), not just a geometry (ch.4) decision.")
        print("  The control loop should hold amplitude as close to the head as")
        print("  the squish clearance and peak-pressure limit allow.")
    if do_plots:
        try:
            print(f"\n  -> {make_plot(rows)}")
        except Exception as e:
            print(f"  (plot skipped: {e})")


if __name__ == "__main__":
    main()
