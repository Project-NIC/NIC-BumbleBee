#!/usr/bin/env python3
"""
NIC-FPLG  --  calc/ entry point.

Runs the linear resonance design and the nonlinear limit-cycle simulation for
the current parameter seed, sweeps the generator load to build the amplitude /
power operating map (DESIGN ch.12), and writes plots + CSV into calc/out/.

    python3 run.py                 # everything, default seed
    python3 run.py --no-plots      # text + CSV only (no matplotlib needed)

Edit calc/params.py to change the machine. Numbers are seeds, not results --
see OPEN-QUESTIONS.md.
"""

import os
import sys
import csv

from params import Params
import resonance
import dynamics

OUT = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT, exist_ok=True)


def operating_map(p: Params, c_values):
    """Sweep generator load; return list of metric rows + the live limit cycles."""
    rows = []
    for c in c_values:
        pc = Params(**{k: getattr(p, k) for k in _seed_fields(p)})
        pc.c_gen = c
        res = dynamics.simulate(pc, t_end=2.5)
        m = res["metrics"]
        alive = m["v_peak"] > 0.1
        rows.append({
            "c_gen": c,
            "freq_hz": m["freq_hz"] if alive else float("nan"),
            "amplitude_mm": m["amplitude_mm"],
            "v_peak": m["v_peak"],
            "a_peak": m["a_peak"],
            "vib_force_N": m["vib_force_N"],
            "p_comb_peak_bar": m["p_comb_peak_bar"],
            "P_elec_W": m["P_elec_W"],
            "alive": alive,
            "hits_head": m["amplitude_mm"] >= 0.99 * pc.x_max * 1e3,
        })
    return rows


def _seed_fields(p: Params):
    # init=True dataclass fields only (skip the derived ones)
    from dataclasses import fields
    return [f.name for f in fields(p) if f.init]


def write_csv(rows, path):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def make_plots(p: Params, res, rows):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    t, x, v = res["t"], res["x"], res["v"]
    # show ~6 cycles at the tail
    tail = t > (t[-1] - 6.0 / max(res["metrics"]["freq_hz"], 1.0))

    fig, ax = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("NIC-FPLG  --  nonlinear limit cycle (0D)", fontweight="bold")

    ax[0, 0].plot(t[tail] * 1e3, x[tail] * 1e3, lw=1.2)
    ax[0, 0].axhline(p.x_max * 1e3, ls="--", c="r", lw=0.8, label="head (TDC)")
    ax[0, 0].axhline(-p.x_max * 1e3, ls="--", c="r", lw=0.8)
    ax[0, 0].set(xlabel="t [ms]", ylabel="position [mm]", title="Displacement")
    ax[0, 0].legend(fontsize=8); ax[0, 0].grid(alpha=0.3)

    ax[0, 1].plot(t[tail] * 1e3, v[tail], lw=1.2, c="tab:orange")
    ax[0, 1].set(xlabel="t [ms]", ylabel="velocity [m/s]", title="Velocity")
    ax[0, 1].grid(alpha=0.3)

    ax[1, 0].plot(t[tail] * 1e3, res["p_cL"][tail] / 1e5, lw=1.0, label="comb L")
    ax[1, 0].plot(t[tail] * 1e3, res["p_cR"][tail] / 1e5, lw=1.0, label="comb R")
    ax[1, 0].plot(t[tail] * 1e3, res["p_uL"][tail] / 1e5, lw=0.8, ls=":", label="air L")
    ax[1, 0].plot(t[tail] * 1e3, res["p_uR"][tail] / 1e5, lw=0.8, ls=":", label="air R")
    ax[1, 0].set(xlabel="t [ms]", ylabel="pressure [bar]", title="Chamber pressures")
    ax[1, 0].legend(fontsize=8, ncol=2); ax[1, 0].grid(alpha=0.3)

    ax[1, 1].plot(x[tail] * 1e3, v[tail], lw=0.8, c="tab:green")
    ax[1, 1].set(xlabel="position [mm]", ylabel="velocity [m/s]",
                 title="Phase portrait")
    ax[1, 1].grid(alpha=0.3)

    fig.tight_layout(rect=(0, 0, 1, 0.96))
    p1 = os.path.join(OUT, "limit_cycle.png")
    fig.savefig(p1, dpi=110); plt.close(fig)

    # operating map
    cg = [r["c_gen"] for r in rows if r["alive"]]
    amp = [r["amplitude_mm"] for r in rows if r["alive"]]
    frq = [r["freq_hz"] for r in rows if r["alive"]]
    pel = [r["P_elec_W"] for r in rows if r["alive"]]
    pcb = [r["p_comb_peak_bar"] for r in rows if r["alive"]]

    fig2, bx = plt.subplots(2, 2, figsize=(12, 8))
    fig2.suptitle("NIC-FPLG  --  generator-load operating map (DESIGN ch.12)",
                  fontweight="bold")
    bx[0, 0].plot(cg, amp, "o-"); bx[0, 0].axhline(p.x_max * 1e3, ls="--", c="r",
                  lw=0.8, label="head")
    bx[0, 0].set(xlabel="c_gen [N/(m/s)]", ylabel="amplitude [mm]",
                 title="Amplitude vs load"); bx[0, 0].legend(fontsize=8)
    bx[0, 1].plot(cg, frq, "o-", c="tab:purple")
    bx[0, 1].set(xlabel="c_gen [N/(m/s)]", ylabel="frequency [Hz]",
                 title="Frequency vs load")
    bx[1, 0].plot(cg, pel, "o-", c="tab:green")
    bx[1, 0].set(xlabel="c_gen [N/(m/s)]", ylabel="electrical power [W]",
                 title="Power vs load")
    bx[1, 1].plot(cg, pcb, "o-", c="tab:red")
    bx[1, 1].set(xlabel="c_gen [N/(m/s)]", ylabel="peak comb. pressure [bar]",
                 title="Peak pressure vs load")
    for a in bx.flat:
        a.grid(alpha=0.3)
    fig2.tight_layout(rect=(0, 0, 1, 0.96))
    p2 = os.path.join(OUT, "operating_map.png")
    fig2.savefig(p2, dpi=110); plt.close(fig2)
    return [p1, p2]


def main():
    do_plots = "--no-plots" not in sys.argv
    p = Params()

    print(resonance.report(p))
    print()

    res = dynamics.simulate(p)
    print(dynamics.report(p, res))
    print()

    c_values = [90, 100, 110, 120, 130, 140, 150, 160, 170, 180]
    print("sweeping generator load for operating map ...")
    rows = operating_map(p, c_values)
    csv_path = os.path.join(OUT, "operating_map.csv")
    write_csv(rows, csv_path)
    print(f"  -> {csv_path}")

    if do_plots:
        try:
            files = make_plots(p, res, rows)
            for f in files:
                print(f"  -> {f}")
        except Exception as e:
            print(f"  (plots skipped: {e})")


if __name__ == "__main__":
    main()
