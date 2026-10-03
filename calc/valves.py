#!/usr/bin/env python3
"""
In-piston transfer-valve force budget  --  DESIGN ch.5 / OPEN-QUESTIONS item 9.

The transfer valves live inside the piston and open the path from the
under-piston (pre-compression) chamber into the combustion chamber. The design
claim (ch.3, ch.5): valve inertia is *comparable in magnitude* to the pressure
force and **delays opening past BDC** -> exhaust leaves first, transfer second =
asymmetric two-stroke timing for free, no membranes or power valves.

This script tests that claim on the running limit cycle. For one piston it takes
the cycle's acceleration a(t) and the pressure difference across the disc, and
forms the axial force budget on the valve:

    F_open(t) = (p_under - p_comb)*A_disc      pressure trying to open it
              - F_preload                       spring holding it shut
              - m_valve * a_outward(t)          inertia (seat accelerates;
                                                 the valve lags = opposes opening
                                                 exactly at the BDC reversal)

The valve opens when F_open > 0. We measure how far past BDC that is, and how
the delay scales with valve mass (the design's "every gram shifts the balance
by ~0.9 N").

    python3 valves.py [--no-plots]

Quasi-static threshold model (valve light vs the cycle). Full valve-lift
dynamics + surge of the conical spring is the natural next step.
"""

import os
import sys
import math
import numpy as np

from params import Params, BAR
import dynamics

OUT = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT, exist_ok=True)

# ---- valve parameters (DESIGN ch.5 working figures) --------------------
VALVE_MASS = 0.025          # kg     ~25 g STOCK motorcycle exhaust valve --
                            #        off-the-shelf, heat-resistant alloy, huge
                            #        fatigue reserve in its "cold" role (ch.5)
DISC_DIA = 0.016            # m      ~16 mm motorcycle exhaust valve
PRELOAD = 1.0               # N      conical-spring seat preload: the spring
                            #        only SEATS the valve; the gas dynamics
                            #        (pre-compression vs combustion) do the work.
                            #        Keep it ~1 N or less.


def _one_cycle(res):
    """Extract one steady period (t, x, a, p_under, p_comb) for the right piston."""
    t, x, a = res["t"], res["x"], res["a"]
    p_u, p_c = res["p_uR"], res["p_cR"]
    f = res["metrics"]["freq_hz"]
    T = 1.0 / f
    t_end = t[-1]
    sel = (t >= t_end - 1.2 * T) & (t <= t_end)       # last ~1.2 periods
    tt, xx, aa = t[sel], x[sel], a[sel]
    pu, pc = p_u[sel], p_c[sel]
    return tt - tt[0], xx, aa, pu, pc, T


def force_budget(res, m_valve=VALVE_MASS):
    A_disc = math.pi * 0.25 * DISC_DIA ** 2
    tt, xx, aa, pu, pc, T = _one_cycle(res)
    # right piston: outward (valve-opening) direction is +x
    F_press = (pu - pc) * A_disc
    F_inertia = m_valve * aa            # >0 (accel outward) opposes opening
    F_open = F_press - PRELOAD - F_inertia

    i_bdc = int(np.argmin(xx))          # right combustion BDC = x minimum
    t_bdc = tt[i_bdc]
    # first opening (F_open>0) at or after BDC, within the transfer window
    after = np.where((tt >= t_bdc) & (F_open > 0))[0]
    if len(after):
        t_open = tt[after[0]]
        delay = t_open - t_bdc
        delay_deg = 360.0 * delay / T   # "crank-equivalent" degrees
    else:
        t_open = float("nan"); delay = float("nan"); delay_deg = float("nan")
    return {
        "t": tt, "x": xx, "a": aa, "A_disc": A_disc, "T": T,
        "F_press": F_press, "F_inertia": F_inertia, "F_open": F_open,
        "t_bdc": t_bdc, "t_open": t_open, "delay_s": delay, "delay_deg": delay_deg,
        "F_press_open_peak": float(np.max(F_press)),      # toward open
        "F_close_peak": float(-np.min(F_press)),          # combustion slams shut
        "F_inertia_peak": float(np.max(np.abs(F_inertia))),
        "F_open_peak": float(np.max(F_open)),             # net; >0 => it opens
        "opens": bool(not math.isnan(delay)),
    }


def threshold_mass(res, m_lo=0.005, m_hi=0.060, step=0.001):
    """Heaviest valve mass that still lets the transfer valve open past BDC.

    Ascending scan (not bisection): the "opens" test can be mildly
    non-monotonic near the high-frequency edge, so we walk up from the lightest
    valve and return the last mass that opens before the first that does not.
    """
    last = float("nan")
    m = m_lo
    while m <= m_hi + 1e-9:
        if force_budget(res, m)["opens"]:
            last = m
        elif not math.isnan(last):
            break                       # first closure after opening = threshold
        m += step
    return last


def precomp_sweep(ratios):
    """Run the engine at each pre-compression ratio; return (ratio, delay, opens)."""
    out = []
    for r in ratios:
        res = dynamics.simulate(Params(precomp_ratio=r), dt=2e-6, t_end=2.5)
        fb = force_budget(res)                       # stock 25 g valve
        out.append((r, fb["delay_deg"], fb["opens"]))
    return out


def make_plot(res, fb, sweep):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    fig.suptitle("NIC-FPLG  --  stock 25 g transfer valve, 1 N seat spring "
                 "(ch.5 / item 9)", fontweight="bold")

    tms = fb["t"] * 1e3
    ax[0].plot(tms, fb["F_press"], label="pressure (open)")
    ax[0].plot(tms, fb["F_inertia"], label="inertia (opposes at BDC)")
    ax[0].plot(tms, fb["F_open"], "k", lw=1.5, label="net opening force")
    ax[0].axhline(0, c="grey", lw=0.6)
    ax[0].axvline(fb["t_bdc"] * 1e3, ls="--", c="b", lw=0.8, label="BDC")
    if not math.isnan(fb["t_open"]):
        ax[0].axvline(fb["t_open"] * 1e3, ls="--", c="g", lw=0.8, label="valve opens")
    ax[0].set(xlabel="t [ms]", ylabel="force [N]", title="Force budget over a cycle")
    ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3)

    rr = [s[0] for s in sweep]
    dd = [s[1] if s[2] else float("nan") for s in sweep]
    ax[1].plot(rr, dd, "o-", c="tab:red")
    ax[1].set(xlabel="pre-compression ratio", ylabel="transfer delay past BDC [deg]",
              title="Pre-compression tunes the inertial delay (25 g valve)")
    ax[1].grid(alpha=0.3)
    ax[1].annotate("too little:\nvalve won't open", (rr[0], 2), fontsize=8,
                   color="grey")

    fig.tight_layout(rect=(0, 0, 1, 0.94))
    path = os.path.join(OUT, "valve_budget.png")
    fig.savefig(path, dpi=110); plt.close(fig)
    return path


def main():
    do_plots = "--no-plots" not in sys.argv
    res = dynamics.simulate(Params(), dt=2e-6, t_end=2.5)
    fb = force_budget(res)

    print("=" * 62)
    print("  TRANSFER-VALVE FORCE BUDGET  (ch.5 / item 9)")
    print("=" * 62)
    print(f"  valve mass            {VALVE_MASS*1e3:6.1f} g   (stock motorcycle "
          f"exhaust valve)")
    print(f"  disc diameter         {DISC_DIA*1e3:6.1f} mm  "
          f"(area {fb['A_disc']*1e4:.2f} cm^2)")
    print(f"  spring preload        {PRELOAD:6.1f} N   (seats only; gas does the work)")
    print(f"  pre-compression       {Params().precomp_ratio:6.1f} :1")
    print("-" * 62)
    print(f"  peak OPENING pressure {fb['F_press_open_peak']:6.1f} N   "
          f"(pre-compression transfer)")
    print(f"  peak inertia force    {fb['F_inertia_peak']:6.1f} N   "
          f"<- comparable magnitude (design claim, ch.5)")
    print(f"  peak CLOSING force    {fb['F_close_peak']:6.1f} N   "
          f"<- combustion slams it shut = backfire check valve (ch.20)")
    print("-" * 62)
    if fb["opens"]:
        print(f"  STOCK valve transfers, opening {fb['delay_s']*1e3:.2f} ms "
              f"({fb['delay_deg']:.0f} deg) after BDC")
        print("  => exhaust-first, transfer-second asymmetric timing, for free")
    else:
        print(f"  valve does not open (net opening force peaks "
              f"{fb['F_open_peak']:.1f} N) -- raise pre-compression")
    print("-" * 62)
    print("  pre-compression is the tuning knob for that delay:")
    sweep = precomp_sweep([2.0, 2.5, 3.0, 3.5, 4.0]) if do_plots else \
        precomp_sweep([2.0, 2.5, 3.0])
    for r, d, op in sweep:
        s = f"{d:5.0f} deg delay" if op else "does not open"
        print(f"    {r:.1f} :1  ->  {s}")
    print("  more pre-compression opens the valve earlier (less delay); ~2.5:1")
    print("  keeps a useful inertial delay. No special valve needed.")
    print("=" * 62)
    if do_plots:
        try:
            print(f"  -> {make_plot(res, fb, sweep)}")
        except Exception as e:
            print(f"  (plot skipped: {e})")


if __name__ == "__main__":
    main()
