#!/usr/bin/env python3
"""
Two-module anti-phase balancing  --  DESIGN ch.15 / OPEN-QUESTIONS item 10.

One module has no inherent balance: both pistons move together, so the moving
mass m oscillates and throws a reciprocating force F(t) = m*a(t) into the frame.
The design's fix (ch.15, ch.17): run two modules side by side in anti-phase, so
their forces cancel.

This script takes the real (non-sinusoidal, combustion-asymmetric) acceleration
a(t) from the limit cycle and asks how well anti-phase actually cancels it:

  * net force of the twin = F(t) + F(t - T/2)   -- the residual the mounts feel
  * because a(t) has even harmonics (the waveform is not a pure sine), the
    half-period-shifted copy does not cancel perfectly; the 2nd harmonic adds.
  * two modules a distance d apart also leave a rocking COUPLE even when the
    net force is small.

    python3 twin.py [--no-plots]

Reports the single-module shaker force, the twin residual force, the cancellation
factor, and the residual couple. Still 0D.
"""

import os
import sys
import numpy as np

from params import Params
import dynamics

OUT = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT, exist_ok=True)

MODULE_SPACING = 0.12       # m   centre-to-centre distance of the two modules


def _one_period(res, n=720):
    """Resample one steady period of acceleration onto n even points."""
    t, a = res["t"], res["a"]
    f = res["metrics"]["freq_hz"]
    T = 1.0 / f
    t0 = t[-1] - T
    tg = np.linspace(t0, t[-1], n, endpoint=False)
    ag = np.interp(tg, t, a)
    return ag, T


def analyse(res, m=None, spacing=MODULE_SPACING):
    p = Params()
    m = p.m_moving if m is None else m
    a, T = _one_period(res)
    n = len(a)

    F1 = m * a                       # module 1 shaker force
    F2 = np.roll(m * a, n // 2)      # module 2 = anti-phase (half period later)
    F_net = F1 + F2                  # net force on the common frame
    # couple about the frame centre: forces at +/- spacing/2
    M_couple = (F1 - F2) * (spacing / 2.0)

    single_peak = float(np.max(np.abs(F1)))
    twin_peak = float(np.max(np.abs(F_net)))
    couple_peak = float(np.max(np.abs(M_couple)))

    # harmonic content (why it does not fully cancel)
    spec = np.abs(np.fft.rfft(a)) / n
    spec[1:] *= 2.0
    harmonics = spec[:6] / (spec[1] if spec[1] > 0 else 1.0)  # normalised to 1st

    return {
        "T": T, "F1": F1, "F_net": F_net, "M_couple": M_couple,
        "single_peak_N": single_peak, "twin_peak_N": twin_peak,
        "couple_peak_Nm": couple_peak,
        "cancellation": twin_peak / single_peak if single_peak else float("nan"),
        "harmonics": harmonics,
    }


def make_plot(res, an):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    n = len(an["F1"])
    ph = np.linspace(0, 360, n, endpoint=False)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    fig.suptitle("NIC-FPLG  --  two-module anti-phase balancing (ch.15 / item 10)",
                 fontweight="bold")

    ax[0].plot(ph, an["F1"], lw=1.0, label="single module  m·a(t)")
    ax[0].plot(ph, an["F_net"], "k", lw=1.5, label="twin net (anti-phase)")
    ax[0].axhline(0, c="grey", lw=0.6)
    ax[0].set(xlabel="phase [deg]", ylabel="force [N]",
              title=f"Shaker force: single {an['single_peak_N']:.0f} N "
                    f"-> twin {an['twin_peak_N']:.0f} N")
    ax[0].legend(fontsize=8); ax[0].grid(alpha=0.3)

    ax2 = ax[1]
    ax2.plot(ph, an["M_couple"], lw=1.2, c="tab:red")
    ax2.axhline(0, c="grey", lw=0.6)
    ax2.set(xlabel="phase [deg]", ylabel="couple [N·m]",
            title=f"Residual rocking couple {an['couple_peak_Nm']:.0f} N·m "
                  f"(force cancels, couple doesn't)")
    ax2.grid(alpha=0.3)

    fig.tight_layout(rect=(0, 0, 1, 0.94))
    path = os.path.join(OUT, "twin_balance.png")
    fig.savefig(path, dpi=110); plt.close(fig)
    return path


def main():
    do_plots = "--no-plots" not in sys.argv
    res = dynamics.simulate(Params(), dt=2e-6, t_end=2.5)
    an = analyse(res)

    print("=" * 60)
    print("  TWO-MODULE ANTI-PHASE BALANCING  (ch.15 / item 10)")
    print("=" * 60)
    print(f"  single-module shaker force   {an['single_peak_N']:7.0f} N peak")
    print(f"  twin net force (anti-phase)  {an['twin_peak_N']:7.0f} N peak  "
          f"(-{(1-an['cancellation'])*100:.0f} %)")
    print(f"  residual rocking couple      {an['couple_peak_Nm']:7.1f} N·m "
          f"(spacing {MODULE_SPACING*1e3:.0f} mm)")
    print("-" * 60)
    h = an["harmonics"]
    print(f"  harmonics of a(t) (norm.): 1st {h[1]:.2f}  2nd {h[2]:.2f}  "
          f"3rd {h[3]:.2f}  4th {h[4]:.2f}")
    print("  The cycle is odd-harmonic dominated (1st + 3rd), and a half-period")
    print("  anti-phase shift cancels ODD harmonics -> the net shaking FORCE")
    print("  nearly vanishes. (Only EVEN harmonics would survive; here ~0.)")
    print("  BUT the two large opposed forces sit a distance apart, so a big")
    print(f"  rocking COUPLE remains (~{an['couple_peak_Nm']:.0f} N·m) -- that, not the")
    print("  net force, is what the mounts must carry. Shrink it by stacking the")
    print("  modules coaxially (smaller spacing) rather than side by side.")
    print("=" * 60)
    if do_plots:
        try:
            print(f"  -> {make_plot(res, an)}")
        except Exception as e:
            print(f"  (plot skipped: {e})")


if __name__ == "__main__":
    main()
