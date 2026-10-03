#!/usr/bin/env python3
"""
Constant-frequency operating line  --  DESIGN ch.12 control concept.

The limit-cycle frequency drifts with generator load on its own (more load ->
smaller amplitude -> shallower compression -> softer gas spring -> lower f).
But the mixture (fuel energy per firing) is a second actuator: richer charge
returns energy, restoring amplitude / compression / frequency while the extra
energy leaves as power.

So load and mixture together hold ONE operating point (constant frequency,
constant amplitude, nearly constant peak pressure) while the electrical power is
varied -- exactly the multi-loop control of DESIGN ch.12 (load/excitation =
fast power actuator, mixture = the frequency trim).

This script finds, for a target frequency, the fuel level that holds it at each
generator load, and plots the resulting constant-frequency power line.

    python3 freq_hold.py                 # default: hold 40 Hz
    python3 freq_hold.py --no-plots
"""

import os
import sys
import csv

from params import Params
import dynamics

OUT = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT, exist_ok=True)


def _metrics(bmep_bar, c_gen, dt, t_end):
    p = Params()
    p.bmep_target = bmep_bar * 1e5
    p.c_gen = c_gen
    return p, dynamics.simulate(p, dt=dt, t_end=t_end)["metrics"]


def fuel_for_freq(c_gen, f_target, bmep_lo=2.5, bmep_hi=12.0, iters=22):
    """Bisect the fuel level (bmep, bar) that holds the limit cycle at f_target.

    Frequency increases monotonically with fuel; a dead (non-firing) result
    means too little fuel. Returns (bmep_bar, metrics) from a final accurate run.
    """
    lo, hi = bmep_lo, bmep_hi
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        _, m = _metrics(mid, c_gen, dt=3e-6, t_end=2.2)
        if m["v_peak"] < 0.1:           # engine died -> needs more fuel
            lo = mid
        elif m["freq_hz"] > f_target:   # too fast -> less fuel
            hi = mid
        else:
            lo = mid
    bmep = 0.5 * (lo + hi)
    _, m = _metrics(bmep, c_gen, dt=2e-6, t_end=2.5)
    return bmep, m


def constant_freq_line(f_target=40.0, c_values=(110, 130, 150, 170, 190, 210)):
    rows = []
    for c in c_values:
        bmep, m = fuel_for_freq(c, f_target)
        if m["v_peak"] < 0.1:
            continue
        rows.append({
            "c_gen": c,
            "fuel_bmep_bar": round(bmep, 2),
            "freq_hz": round(m["freq_hz"], 2),
            "amplitude_mm": round(m["amplitude_mm"], 2),
            "P_elec_W": round(m["P_elec_W"], 0),
            "p_comb_peak_bar": round(m["p_comb_peak_bar"], 2),
            "vib_force_N": round(m["vib_force_N"], 0),
        })
    return rows


def make_plot(rows, f_target):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    pel = [r["P_elec_W"] for r in rows]
    fuel = [r["fuel_bmep_bar"] for r in rows]
    cg = [r["c_gen"] for r in rows]
    amp = [r["amplitude_mm"] for r in rows]
    pcb = [r["p_comb_peak_bar"] for r in rows]
    frq = [r["freq_hz"] for r in rows]

    fig, ax = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle(f"NIC-FPLG  --  constant-{f_target:.0f} Hz operating line "
                 f"(mixture + load, ch.12)", fontweight="bold")

    ax[0, 0].plot(pel, fuel, "o-", label="fuel (mixture)")
    ax[0, 0].plot(pel, [c / 25 for c in cg], "s--", c="tab:orange",
                  label="gen load /25")
    ax[0, 0].set(xlabel="electrical power [W]",
                 ylabel="actuator", title="The two actuators vs power")
    ax[0, 0].legend(fontsize=8); ax[0, 0].grid(alpha=0.3)

    ax[0, 1].plot(pel, frq, "o-", c="tab:purple")
    ax[0, 1].axhline(f_target, ls="--", c="r", lw=0.8)
    ax[0, 1].set(xlabel="electrical power [W]", ylabel="frequency [Hz]",
                 title="Frequency held constant"); ax[0, 1].grid(alpha=0.3)
    ax[0, 1].set_ylim(f_target - 5, f_target + 5)

    ax[1, 0].plot(pel, amp, "o-", c="tab:blue")
    ax[1, 0].set(xlabel="electrical power [W]", ylabel="amplitude [mm]",
                 title="Amplitude ~constant"); ax[1, 0].grid(alpha=0.3)

    ax[1, 1].plot(pel, pcb, "o-", c="tab:red")
    ax[1, 1].set(xlabel="electrical power [W]", ylabel="peak comb. pressure [bar]",
                 title="Peak pressure ~constant (constant peak stress!)")
    ax[1, 1].grid(alpha=0.3)

    fig.tight_layout(rect=(0, 0, 1, 0.96))
    path = os.path.join(OUT, "constant_freq_line.png")
    fig.savefig(path, dpi=110)
    plt.close(fig)
    return path


def main():
    do_plots = "--no-plots" not in sys.argv
    f_target = 40.0

    print(f"finding constant-{f_target:.0f} Hz line (mixture trims f as load varies) ...\n")
    rows = constant_freq_line(f_target)

    print(f"  {'c_gen':>6} {'fuel[bar]':>10} {'f[Hz]':>7} {'amp[mm]':>8} "
          f"{'P_el[W]':>8} {'pcomb[bar]':>11} {'vib[N]':>7}")
    for r in rows:
        print(f"  {r['c_gen']:6d} {r['fuel_bmep_bar']:10.2f} {r['freq_hz']:7.1f} "
              f"{r['amplitude_mm']:8.1f} {r['P_elec_W']:8.0f} "
              f"{r['p_comb_peak_bar']:11.1f} {r['vib_force_N']:7.0f}")

    csv_path = os.path.join(OUT, "constant_freq_line.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"\n  -> {csv_path}")

    if do_plots:
        try:
            print(f"  -> {make_plot(rows, f_target)}")
        except Exception as e:
            print(f"  (plot skipped: {e})")

    print("\nReading: load carries the power change, mixture trims the frequency")
    print("back to target. Constant f, ~constant amplitude, ~constant peak")
    print("pressure -> 'one operating point' with power varied on top (ch.12).")


if __name__ == "__main__":
    main()
