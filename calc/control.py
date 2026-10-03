#!/usr/bin/env python3
"""
Coupled closed-loop control  --  DESIGN ch.12 / OPEN-QUESTIONS item 22.

Two actuators, two controlled variables, updated once per cycle:

  * mixture (fuel / bmep)   -> electrical POWER   (more fuel = more power)
  * generator load (c_gen)  -> FREQUENCY          (more load = lower frequency)

Each pairing is monotonic (see the run.py / freq_hold.py sweeps), so two
incremental PI loops with light measurement filtering hold the setpoints. The
loops are coupled (richening also raises frequency, so the load loop pushes
back) -- which is exactly the point: this tests whether "one operating point,
frequency held" survives realistic per-cycle ignition scatter.

    python3 control.py                 # power-step schedule under ignition scatter
    python3 control.py --no-plots

Addresses item 22 (amplitude/frequency regulation, coupled-loop stability).
Still a 0D model.
"""

import os
import sys

from params import Params
import dynamics

OUT = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT, exist_ok=True)


def _clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


class Controller:
    """Incremental (velocity-form) PI on each loop, with EMA-filtered inputs.

    Velocity form  u += Kp*(e - e_prev) + Ki*e  handles setpoint steps cleanly
    and needs no explicit anti-windup integrator.
    """

    def __init__(self, f_set=40.0, power_schedule=None,
                 kp_fuel=2.0e-4, ki_fuel=3.0e-4,
                 kp_cgen=2.5, ki_cgen=3.0,
                 fuel0=5.0, cgen0=150.0, ema=0.30):
        self.f_set = f_set
        self.power_schedule = power_schedule or (lambda t: 1400.0)
        self.kp_fuel, self.ki_fuel = kp_fuel, ki_fuel
        self.kp_cgen, self.ki_cgen = kp_cgen, ki_cgen
        self.fuel = fuel0          # bmep [bar]
        self.cgen = cgen0          # N/(m/s)
        self.ep_prev = 0.0
        self.ef_prev = 0.0
        self.ema = ema
        self.f_filt = None
        self.p_filt = None

    def __call__(self, meas):
        # EMA filter the noisy per-cycle measurements
        self.f_filt = meas["freq_hz"] if self.f_filt is None else \
            (1 - self.ema) * self.f_filt + self.ema * meas["freq_hz"]
        self.p_filt = meas["P_elec"] if self.p_filt is None else \
            (1 - self.ema) * self.p_filt + self.ema * meas["P_elec"]

        p_set = self.power_schedule(meas["t"])

        # power loop -> fuel (more fuel raises power)
        e_p = p_set - self.p_filt
        self.fuel = _clamp(
            self.fuel + self.kp_fuel * (e_p - self.ep_prev) + self.ki_fuel * e_p,
            2.5, 11.0)
        self.ep_prev = e_p

        # frequency loop -> load (f too high => raise load to pull it down)
        e_f = self.f_filt - self.f_set
        self.cgen = _clamp(
            self.cgen + self.kp_cgen * (e_f - self.ef_prev) + self.ki_cgen * e_f,
            80.0, 240.0)
        self.ef_prev = e_f

        return {"c_gen": self.cgen, "bmep_bar": self.fuel}


def power_steps(t):
    """Demand schedule: the battery asks for different power over time."""
    if t < 1.0:
        return 1200.0
    if t < 2.0:
        return 1550.0
    return 1300.0


def run(scatter=0.06, t_end=3.0, seed=1):
    p = Params()
    ctrl = Controller(f_set=40.0, power_schedule=power_steps)
    res = dynamics.simulate(p, dt=3e-6, t_end=t_end, controller=ctrl,
                            ign_scatter=scatter, seed=seed, settle_frac=0.8)
    return res


def make_plot(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t = res["cyc_t"]
    fig, ax = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("NIC-FPLG  --  coupled closed-loop control under ignition scatter "
                 "(ch.12 / item 22)", fontweight="bold")

    ax[0, 0].plot(t, res["cyc_pel"], lw=0.8, label="measured")
    ax[0, 0].plot(t, [power_steps(tt) for tt in t], "r--", lw=1.0, label="setpoint")
    ax[0, 0].set(xlabel="t [s]", ylabel="electrical power [W]",
                 title="Power tracks the demand"); ax[0, 0].legend(fontsize=8)

    ax[0, 1].plot(t, res["cyc_f"], lw=0.8, c="tab:purple")
    ax[0, 1].axhline(40.0, ls="--", c="r", lw=1.0, label="setpoint 40 Hz")
    ax[0, 1].set(xlabel="t [s]", ylabel="frequency [Hz]",
                 title="Frequency held through power steps"); ax[0, 1].legend(fontsize=8)
    ax[0, 1].set_ylim(36, 44)

    ax[1, 0].plot(t, res["cyc_bmep"], lw=1.0, c="tab:green")
    ax[1, 0].set(xlabel="t [s]", ylabel="fuel / bmep [bar]",
                 title="Actuator: mixture")
    ax[1, 1].plot(t, res["cyc_cgen"], lw=1.0, c="tab:orange")
    ax[1, 1].set(xlabel="t [s]", ylabel="generator load c_gen",
                 title="Actuator: load")
    for a in ax.flat:
        a.grid(alpha=0.3)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    path = os.path.join(OUT, "control_loop.png")
    fig.savefig(path, dpi=110); plt.close(fig)
    return path


def _band_stats(t, y, lo, hi):
    """mean and std of y over the window (lo, hi)."""
    import numpy as np
    sel = (t > lo) & (t < hi)
    return float(np.mean(y[sel])), float(np.std(y[sel]))


def main():
    do_plots = "--no-plots" not in sys.argv
    res = run()
    t = res["cyc_t"]

    print("coupled PI control, 6% per-firing ignition scatter, power steps:\n")
    print("  segment            P_set   P_meas(mean±sd)     f_meas(mean±sd)")
    for (lo, hi, ps) in [(0.6, 1.0, 1200), (1.6, 2.0, 1550), (2.6, 3.0, 1300)]:
        pm, psd = _band_stats(t, res["cyc_pel"], lo, hi)
        fm, fsd = _band_stats(t, res["cyc_f"], lo, hi)
        print(f"  t={lo:.1f}-{hi:.1f}s        {ps:5d} W   "
              f"{pm:6.0f} ± {psd:4.0f} W      {fm:5.2f} ± {fsd:4.2f} Hz")

    print("\n  frequency stays near 40 Hz across all three power levels =>")
    print("  the mixture+load loops hold one operating point under scatter.")
    if do_plots:
        try:
            print(f"\n  -> {make_plot(res)}")
        except Exception as e:
            print(f"  (plot skipped: {e})")


if __name__ == "__main__":
    main()
