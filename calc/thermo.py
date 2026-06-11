#!/usr/bin/env python3
"""
0D thermodynamic cycle  --  DESIGN ch.4 / OPEN-QUESTIONS item 1 (A1).

The dynamics model (dynamics.py) drives combustion from a *seed* BMEP and a seed
indicated efficiency. This module is the layer underneath: a real closed-cycle
thermodynamic model on the actual free-piston kinematics, with

  * real fuel        (LHV, air-fuel ratio, equivalence ratio phi),
  * Wiebe heat release,
  * Woschni wall heat transfer,
  * trapped charge with a residual (internal-EGR) fraction,

integrated by the first law (m*cv*dT = dQ_comb + dQ_wall - p*dV; p = m*R*T/V).
It produces the numbers the power targets hang on: peak pressure and temperature,
indicated work, thermal efficiency, exhaust temperature, and the **real BMEP** —
which we compare against the dynamics seed.

    python3 thermo.py [--no-plots]

The volume-vs-time profile V(t) comes from a dynamics limit-cycle run, so the
free-piston dwell near TDC/BDC is the real one. Single combustion chamber.
0D (no spatial/CFD detail, no stratification fidelity -- that is OQ-A3).
"""

import os
import sys
import math
import numpy as np

from params import Params, BAR, CC
import dynamics

OUT = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT, exist_ok=True)

# ---- gas / fuel constants ----------------------------------------------
R_GAS = 287.0            # J/kg/K   specific gas constant (air-like)
# Temperature-dependent specific heat: cold charge ~720, hot products ~1300+.
# A linear cv(T) captures the main effect (and self-limits the peak temperature
# the way real cv-rise + dissociation do) far better than a constant. Still 0D,
# no chemistry -- peak T remains an upper bound.
CV0, CV1 = 720.0, 0.22   # cv(T) = CV0 + CV1*T  [J/kg/K]


def cv_of(T):
    return CV0 + CV1 * T


LHV = 44.0e6             # J/kg     gasoline lower heating value
AFR_STOICH = 14.7        # -        stoichiometric air/fuel
T_WALL = 450.0           # K        mean wall temperature
COMB_EFF = 0.97          # -        combustion completeness
F_RESIDUAL = 0.10        # -        retained burned-gas fraction (internal EGR)
P_TRAP = 1.10 * BAR      # Pa       charge pressure trapped at port close
WIEBE_A, WIEBE_M = 5.0, 2.0
BURN_FRAC = 0.12         # -        burn duration as a fraction of the period
ADVANCE_FRAC = 0.02      # -        ignition advance before TDC (fraction of period)


def kinematics(p: Params, n=2000):
    """One steady period: time, position, volume, |piston speed| (right cylinder)."""
    res = dynamics.simulate(p, dt=2e-6, t_end=2.5)
    t, x = res["t"], res["x"]
    f = res["metrics"]["freq_hz"]
    T = 1.0 / f
    t0 = t[-1] - T
    tg = np.linspace(t0, t[-1], n, endpoint=False)
    xg = np.interp(tg, t, x)
    Vg = np.array([p.vol_comb_right(xx) for xx in xg])
    vpg = np.abs(np.gradient(xg, tg))
    # rotate so the cycle starts at port close (open -> closed transition)
    d_port = p.port_open_frac * p.stroke
    ports_open = xg < (-p.x_max + d_port)
    close_idx = None
    for i in range(n):
        if ports_open[i - 1] and not ports_open[i]:
            close_idx = i
            break
    if close_idx is None:
        close_idx = 0
    roll = -close_idx
    return (np.roll(tg, roll) , np.roll(xg, roll), np.roll(Vg, roll),
            np.roll(vpg, roll), np.roll(ports_open, roll), T, p)


def woschni_h(p_pa, T, B, w):
    """Woschni convective coefficient [W/m^2/K] (p in kPa form)."""
    return 3.26 * (p_pa / 1e3) ** 0.8 * T ** (-0.53) * B ** (-0.2) * max(w, 1.0) ** 0.8


def run_cycle(km, phi=0.8, n_cycles=12):
    tg, xg, Vg, vpg, ports_open, T, p = km
    n = len(tg)
    dt = tg[1] - tg[0]
    B = p.bore
    Vmin_idx = int(np.argmin(Vg))
    n_burn = max(int(BURN_FRAC * n), 5)
    ign_idx = int(Vmin_idx - ADVANCE_FRAC * n) % n

    # find the closed window length (from start=port close to first port open)
    open_after = np.where(ports_open)[0]
    i_open = open_after[0] if len(open_after) else n - 1

    T_exh = 1000.0          # K, initial guess; updated each cycle
    last = None
    for _cyc in range(n_cycles):
        # ---- trap charge at port close (index 0) ----
        V0 = Vg[0]
        m_fresh = P_TRAP * V0 * (1 - F_RESIDUAL) / (R_GAS * p.T_intake)
        m_res = P_TRAP * V0 * F_RESIDUAL / (R_GAS * T_exh)
        m_gas = m_fresh + m_res
        # energy-weighted trapped temperature
        Ttr = (m_fresh * p.T_intake + m_res * T_exh) / m_gas
        m_air = m_fresh / (1 + phi / AFR_STOICH)
        m_fuel = m_air * phi / AFR_STOICH
        Q_total = m_fuel * LHV * COMB_EFF

        Tg_ = Ttr
        pg_ = m_gas * R_GAS * Tg_ / V0
        hist_p, hist_V, hist_T = [], [], []
        work = 0.0
        peakP = pg_
        peakT = Tg_
        mfb_prev = 0.0

        for i in range(1, i_open + 1):
            V = Vg[i]; dV = V - Vg[i - 1]
            # Wiebe heat release (delta from ignition, no cyclic wrap: the closed
            # phase runs monotonically from port close to port open)
            delta = i - ign_idx
            if delta < 0:
                mfb = 0.0
            elif delta <= n_burn:
                xb = delta / n_burn
                mfb = 1.0 - math.exp(-WIEBE_A * xb ** (WIEBE_M + 1))
            else:
                mfb = 1.0
            dQ_comb = Q_total * max(mfb - mfb_prev, 0.0)
            mfb_prev = mfb
            # Woschni wall heat transfer
            A = math.pi * B * B / 2.0 + 4.0 * V / B
            w = 2.28 * vpg[i] + 0.5
            h = woschni_h(pg_, Tg_, B, w)
            dQ_wall = -h * A * (Tg_ - T_WALL) * dt
            # first law
            dT = (dQ_comb + dQ_wall - pg_ * dV) / (m_gas * cv_of(Tg_))
            Tg_ += dT
            pg_ = m_gas * R_GAS * Tg_ / V
            work += pg_ * dV
            peakP = max(peakP, pg_); peakT = max(peakT, Tg_)
            hist_p.append(pg_); hist_V.append(V); hist_T.append(Tg_)

        T_exh = Tg_             # blowdown temperature feeds next cycle's residual
        last = dict(work=work, peakP=peakP, peakT=peakT, T_exh=T_exh,
                    m_fuel=m_fuel, Q_total=Q_total, m_gas=m_gas,
                    p=np.array(hist_p), V=np.array(hist_V), T=np.array(hist_T))

    # derived performance
    f = 1.0 / T
    W = last["work"]
    imep = W / p.swept_volume()
    P_ind = 2.0 * W * f                       # two cylinders, one fire each per cycle
    eta = W / (last["m_fuel"] * LHV) if last["m_fuel"] > 0 else 0.0
    last.update(imep=imep, P_ind=P_ind, eta=eta, f=f, phi=phi)
    return last


def make_plots(km, base, sweep):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
    fig.suptitle("NIC-FPLG  --  0D thermodynamic cycle (ch.4 / item 1)",
                 fontweight="bold")

    ax[0].plot(base["V"] / CC, base["p"] / BAR, lw=1.3)
    ax[0].set(xlabel="volume [cm³]", ylabel="pressure [bar]",
              title=f"P–V loop  (phi={base['phi']:.2f}, "
                    f"peak {base['peakP']/BAR:.0f} bar, "
                    f"work {base['work']:.0f} J)")
    ax[0].grid(alpha=0.3)

    phis = [s["phi"] for s in sweep]
    ax2 = ax[1]
    ax2.plot(phis, [s["P_ind"] for s in sweep], "o-", c="tab:green",
             label="indicated power [W]")
    ax2.set(xlabel="equivalence ratio phi", ylabel="indicated power [W]",
            title="Power / efficiency / peak T vs mixture")
    ax2.grid(alpha=0.3)
    ax3 = ax2.twinx()
    ax3.plot(phis, [s["eta"] * 100 for s in sweep], "s--", c="tab:red",
             label="thermal eff [%]")
    ax3.plot(phis, [s["peakT"] / 100 for s in sweep], "^:", c="tab:purple",
             label="peak T [×100 K]")
    lines = ax2.get_lines() + ax3.get_lines()
    ax2.legend(lines, [l.get_label() for l in lines], fontsize=8, loc="upper left")

    fig.tight_layout(rect=(0, 0, 1, 0.94))
    path = os.path.join(OUT, "thermo_cycle.png")
    fig.savefig(path, dpi=110); plt.close(fig)
    return path


def main():
    do_plots = "--no-plots" not in sys.argv
    p = Params()
    km = kinematics(p)
    base = run_cycle(km, phi=0.8)

    print("=" * 62)
    print("  0D THERMODYNAMIC CYCLE  (ch.4 / item 1)   phi = 0.80, lean")
    print("=" * 62)
    cr_eff = base["V"].max() / base["V"].min()
    print(f"  trapped charge mass     {base['m_gas']*1e6:7.1f} mg")
    print(f"  fuel per firing         {base['m_fuel']*1e6:7.2f} mg  "
          f"-> {base['Q_total']:6.1f} J heat")
    print(f"  effective compression   {cr_eff:7.2f} :1   "
          f"(geometric {p.comp_ratio:.0f}; lower -- piston stops at ~{base['V'].min()/CC:.0f} cm³,")
    print(f"                                       amplitude < full stroke)")
    print("-" * 62)
    print(f"  peak pressure           {base['peakP']/BAR:7.1f} bar   "
          f"(dynamics seed gave ~16)")
    print(f"  peak temperature        {base['peakT']:7.0f} K")
    print(f"  exhaust temperature     {base['T_exh']:7.0f} K")
    print("-" * 62)
    print(f"  indicated work / cycle  {base['work']:7.1f} J")
    print(f"  indicated mean eff. p.  {base['imep']/BAR:7.2f} bar   "
          f"(dynamics seed = 5.0)")
    print(f"  thermal efficiency      {base['eta']*100:7.1f} %     "
          f"(dynamics seed = 38)")
    print(f"  indicated power         {base['P_ind']:7.0f} W   "
          f"(2 cyl @ {base['f']:.0f} Hz)")
    print("=" * 62)

    sweep = [run_cycle(km, phi=ph) for ph in
             (0.55, 0.65, 0.75, 0.85, 0.95, 1.05)]
    print("  mixture sweep:")
    print(f"    {'phi':>5} {'IMEP[bar]':>9} {'eff[%]':>7} {'peakP[bar]':>11} "
          f"{'peakT[K]':>9} {'P_ind[W]':>9}")
    for s in sweep:
        print(f"    {s['phi']:5.2f} {s['imep']/BAR:9.2f} {s['eta']*100:7.1f} "
              f"{s['peakP']/BAR:11.0f} {s['peakT']:9.0f} {s['P_ind']:9.0f}")
    # which phi gives the ~1.5 kW electrical (-> ~1.6 kW indicated-ish) target?
    print()
    print("  Reading:")
    print("   - the seed IMEP (5 bar) holds up: the real cycle gives ~5.8 bar at")
    print("     phi 0.8, so the dynamics power estimate was about right.")
    print("   - efficiency is ~26 %, NOT the 38 % seed -- early exhaust-port")
    print("     opening cuts expansion short and the effective compression is low")
    print("     (~3.5, because the piston only reaches ~18 mm, not full stroke).")
    print("     More amplitude (closer to the head) is the main efficiency lever.")
    print("   - real peak pressure ~22 bar (vs 16 in dynamics) -> the combustion")
    print("     spring is a little stiffer, so the true frequency sits slightly")
    print("     above 40 Hz. phi sets power monotonically; lean ~0.8 is a sane")
    print("     operating point (peak T ~2400 K, low NOx).")
    if do_plots:
        try:
            print(f"\n  -> {make_plots(km, base, sweep)}")
        except Exception as e:
            print(f"  (plot skipped: {e})")


if __name__ == "__main__":
    main()
