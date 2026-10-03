"""
Nonlinear free-piston dynamics  --  0D time-domain limit-cycle model.

Single degree of freedom: x = displacement of the moving assembly (two pistons
+ rod) from the centre, +x toward the right cylinder. Four gas chambers act on
it (DESIGN ch.2, ch.3):

    combustion L / R      : adiabatic compression + heat release + port blowdown
    under-piston L / R     : adiabatic air spring with one-way intake refill

Equation of motion:
    m * x'' = (p_cL - p_cR)*A_p          (combustion: L pushes +x, R pushes -x)
            + (p_uR - p_uL)*A_u          (air spring: restoring toward centre)
            - c_gen*x'                   (generator load = amplitude actuator)
            - c_visc*x' - f_coulomb*sgn(x')

WHAT THIS IS:   a lumped 0D dynamics + simple thermodynamics model. It gives the
                limit-cycle frequency, the stroke actually reached (the "rozkmit"),
                peak velocity/acceleration, vibration force, compression pressures,
                indicated and electrical power.  (OQ-B7, B8, B10; F-table)

WHAT THIS IS NOT:  scavenging/stratification fidelity (that is CFD, OQ-A3), the
                magnetic circuit (OQ-C/FEM), or fatigue (OQ-D). Port blowdown and
                scavenge here are an idealised pressure reset, not a flow model.
"""

import math
import numpy as np
from params import Params, BAR, CC


def simulate(p: Params, dt=4e-6, t_end=2.5, x0_frac=0.0, v0=0.2,
             store_every=50, settle_frac=0.6,
             controller=None, ign_scatter=0.0, seed=None):
    """Integrate the free-piston model to its limit cycle.

    Start is the motor-mode sequence (DESIGN ch.12): from a tiny seed velocity
    v0, the generator-as-motor pumps energy (F_motor = +motor_gain*v) and the
    amplitude grows at the system's own frequency until compression first
    reaches ignition pressure; the motor then switches off and the machine
    settles onto its running limit cycle. This start is insensitive to mass
    (set p.motor_gain = 0 to disable it and use the bare v0 kick instead).

    Optional closed-loop hooks (used by control.py, off by default so the bare
    limit cycle and verify.py are unchanged):
      controller(meas) -> dict   called once per cycle (upward centre crossing)
                                 with {t, freq_hz, amplitude_mm, P_elec, c_gen,
                                 bmep_bar}; may return new 'c_gen' / 'bmep_bar'.
      ign_scatter                per-firing relative std of released heat
                                 (combustion/ignition variability), seed = RNG.

    Returns downsampled time histories, steady-state metrics, and a per-cycle
    log (lists under 'cyc_*').
    """
    A_p, A_u = p.area_piston, p.area_under
    x_max = p.x_max
    sgn = lambda z: (z > 0) - (z < 0)
    rng = np.random.default_rng(seed)
    swept_over_eta = p.swept_volume() / p.eta_indicated

    # live actuators (a controller may move these each cycle)
    c_gen_cur = p.c_gen
    bmep_cur = p.bmep_target
    # heat released per firing: indicated work (bmep*swept) is a fraction
    # eta_indicated of fuel heat, so heat = bmep*swept / eta_indicated
    Q_fuel = bmep_cur * swept_over_eta
    # burn spread, as a slice of one mechanical period
    t_burn = max(p.burn_duration_frac / p.f_target, 20 * dt)
    burn_rate = Q_fuel / t_burn                    # W during a burn
    qfacL = qfacR = 1.0                            # per-firing scatter factors

    d_port = p.port_open_frac * p.stroke
    p_ign = p.ign_pressure_ratio * p.p_intake   # compression-referenced ignition

    # --- state -----------------------------------------------------------
    x = x0_frac * x_max
    v = v0
    p_cL = p.p_intake     # combustion chamber pressures
    p_cR = p.p_intake
    p_uL = p.p_intake     # under-piston (air spring) pressures
    p_uR = p.p_intake

    # per-chamber bookkeeping: armed (fresh charge trapped), burning, burn timer
    armedL = armedR = True
    burnL = burnR = False
    tburnL = tburnR = 0.0
    portL_prev = portR_prev = False
    g_air, g_burn = p.gamma_air, p.gamma_burn
    motor_on = p.motor_gain > 0.0    # motor-mode start pump, off at first fire

    # previous volumes
    VcL = p.vol_comb_left(x);  VcR = p.vol_comb_right(x)
    VuL = p.vol_under_left(x); VuR = p.vol_under_right(x)

    n = int(t_end / dt)
    th, xh, vh, ah = [], [], [], []
    pcLh, pcRh, puLh, puRh = [], [], [], []
    pgen_acc = 0.0          # accumulated electrical energy
    pind_acc = 0.0          # accumulated indicated gas work
    acc_steps = 0
    settle_step = int(settle_frac * n)

    # per-cycle log + accumulators (upward centre crossing = cycle boundary)
    cyc_t, cyc_f, cyc_amp, cyc_pel, cyc_cgen, cyc_bmep = [], [], [], [], [], []
    x_prev = x
    t_cross = 0.0
    cyc_xmax = 0.0
    cyc_gen_E = 0.0

    for i in range(n):
        t = i * dt

        # ---- new volumes from current position ----
        VcL_n = p.vol_comb_left(x);  VcR_n = p.vol_comb_right(x)
        VuL_n = p.vol_under_left(x); VuR_n = p.vol_under_right(x)

        # ---- combustion RIGHT chamber ----
        portR = x < (-x_max + d_port)          # ports uncovered near right BDC
        if portR:
            p_cR = p.p_exhaust                  # blowdown / scavenge
            burnR = False
        else:
            if portR_prev:                      # ports just closed -> fresh trap
                p_cR = p.p_intake
                armedR = True
            gR = g_burn if burnR else g_air
            p_cR = p_cR * (VcR / VcR_n) ** gR
            # ignition: compression-referenced, while still compressing (v>0)
            if armedR and (v > 0) and (p_cR > p_ign):
                burnR = True; armedR = False; tburnR = 0.0
                motor_on = False                # first fire -> hand off to load
                qfacR = 1.0 + ign_scatter * rng.standard_normal()
            if burnR:
                if tburnR < t_burn:
                    p_cR += (g_burn - 1.0) * burn_rate * qfacR * dt / VcR_n
                    tburnR += dt
                else:
                    burnR = False

        # ---- combustion LEFT chamber ----
        portL = x > (x_max - d_port)
        if portL:
            p_cL = p.p_exhaust
            burnL = False
        else:
            if portL_prev:
                p_cL = p.p_intake
                armedL = True
            gL = g_burn if burnL else g_air
            p_cL = p_cL * (VcL / VcL_n) ** gL
            if armedL and (v < 0) and (p_cL > p_ign):
                burnL = True; armedL = False; tburnL = 0.0
                motor_on = False
                qfacL = 1.0 + ign_scatter * rng.standard_normal()
            if burnL:
                if tburnL < t_burn:
                    p_cL += (g_burn - 1.0) * burn_rate * qfacL * dt / VcL_n
                    tburnL += dt
                else:
                    burnL = False

        # ---- under-piston air springs (adiabatic + one-way intake refill) ----
        p_uR = p_uR * (VuR / VuR_n) ** g_air
        if VuR_n > VuR and p_uR < p.p_intake:   # expanding & below intake -> refill
            p_uR = p.p_intake
        p_uL = p_uL * (VuL / VuL_n) ** g_air
        if VuL_n > VuL and p_uL < p.p_intake:
            p_uL = p.p_intake

        # ---- forces ----
        F_comb = (p_cL - p_cR) * A_p
        F_air = (p_uR - p_uL) * A_u
        # motor-mode start pumps energy (field cancelled = no load, ch.12);
        # after first fire the generator load engages instead
        F_gen = p.motor_gain * v if motor_on else -c_gen_cur * v
        F_fric = -p.c_visc * v - p.f_coulomb * sgn(v)
        F = F_comb + F_air + F_gen + F_fric
        a = F / p.m_moving

        # ---- semi-implicit Euler ----
        v += a * dt
        x += v * dt
        # hard clamp at mechanical contact (piston-to-head); record as event
        if x > x_max:
            x = x_max; v = min(v, 0.0)
        elif x < -x_max:
            x = -x_max; v = max(v, 0.0)

        # roll volumes
        VcL, VcR, VuL, VuR = VcL_n, VcR_n, VuL_n, VuR_n
        portR_prev, portL_prev = portR, portL

        # ---- accumulate steady-state energy ----
        if i >= settle_step:
            pgen_acc += c_gen_cur * v * v * dt       # mech power into generator
            pind_acc += (F_comb + F_air) * v * dt    # gas work on assembly
            acc_steps += 1

        # ---- per-cycle measurement + closed-loop control ----
        cyc_gen_E += c_gen_cur * v * v * dt
        if abs(x) > cyc_xmax:
            cyc_xmax = abs(x)
        if x_prev <= 0.0 < x and v > 0.0:            # upward centre crossing
            period = t - t_cross
            if t_cross > 0.0 and period > 0.25 / p.f_target:
                f_meas = 1.0 / period
                pel_meas = cyc_gen_E / period * p.gen_eff
                cyc_t.append(t); cyc_f.append(f_meas)
                cyc_amp.append(cyc_xmax * 1e3); cyc_pel.append(pel_meas)
                cyc_cgen.append(c_gen_cur); cyc_bmep.append(bmep_cur / BAR)
                if controller is not None:
                    out = controller({"t": t, "freq_hz": f_meas,
                                      "amplitude_mm": cyc_xmax * 1e3,
                                      "P_elec": pel_meas, "c_gen": c_gen_cur,
                                      "bmep_bar": bmep_cur / BAR})
                    if out:
                        c_gen_cur = out.get("c_gen", c_gen_cur)
                        new_bmep = out.get("bmep_bar", bmep_cur / BAR) * BAR
                        if new_bmep != bmep_cur:
                            bmep_cur = new_bmep
                            burn_rate = bmep_cur * swept_over_eta / t_burn
                t_cross = t; cyc_xmax = 0.0; cyc_gen_E = 0.0
            elif t_cross == 0.0:
                t_cross = t; cyc_xmax = 0.0; cyc_gen_E = 0.0
        x_prev = x

        # ---- store downsampled history ----
        if i % store_every == 0:
            th.append(t); xh.append(x); vh.append(v); ah.append(a)
            pcLh.append(p_cL); pcRh.append(p_cR); puLh.append(p_uL); puRh.append(p_uR)

    th = np.array(th); xh = np.array(xh); vh = np.array(vh); ah = np.array(ah)
    pcLh = np.array(pcLh); pcRh = np.array(pcRh)
    puLh = np.array(puLh); puRh = np.array(puRh)

    # ---- steady-state metrics over the settled tail ----
    tail = th > (settle_frac * t_end)
    xt, vt, at = xh[tail], vh[tail], ah[tail]
    T_acc = acc_steps * dt

    metrics = {
        "amplitude_mm": float(np.max(np.abs(xt)) * 1e3),
        "stroke_mm": float((np.max(xt) - np.min(xt)) * 1e3),
        "freq_hz": _dominant_freq(th[tail], xt),
        "v_peak": float(np.max(np.abs(vt))),
        "a_peak": float(np.max(np.abs(at))),
        "vib_force_N": float(p.m_moving * np.max(np.abs(at))),
        "p_comb_peak_bar": float(max(np.max(pcLh), np.max(pcRh)) / BAR),
        "p_under_peak_bar": float(max(np.max(puLh), np.max(puRh)) / BAR),
        "P_mech_gen_W": float(pgen_acc / T_acc) if T_acc > 0 else 0.0,
        "P_elec_W": float(pgen_acc / T_acc * p.gen_eff) if T_acc > 0 else 0.0,
        "P_indicated_W": float(pind_acc / T_acc) if T_acc > 0 else 0.0,
    }
    return {
        "t": th, "x": xh, "v": vh, "a": ah,
        "p_cL": pcLh, "p_cR": pcRh, "p_uL": puLh, "p_uR": puRh,
        "metrics": metrics,
        "cyc_t": np.array(cyc_t), "cyc_f": np.array(cyc_f),
        "cyc_amp": np.array(cyc_amp), "cyc_pel": np.array(cyc_pel),
        "cyc_cgen": np.array(cyc_cgen), "cyc_bmep": np.array(cyc_bmep),
    }


def _dominant_freq(t, x):
    """Mechanical frequency from mean-crossing intervals (robust to DC offset)."""
    if len(t) < 8:
        return float("nan")
    xc = x - np.mean(x)
    crossings = np.where((xc[:-1] <= 0) & (xc[1:] > 0))[0]
    if len(crossings) < 2:
        return float("nan")
    periods = np.diff(t[crossings])
    return float(1.0 / np.mean(periods))


def report(p: Params, result) -> str:
    m = result["metrics"]
    L = []
    L.append("=" * 64)
    L.append("  NONLINEAR LIMIT CYCLE  (0D free-piston, OQ-B7/B8/B10)")
    L.append("=" * 64)
    L.append(f"limit-cycle frequency        {m['freq_hz']:9.2f} Hz   "
             f"(target {p.f_target:.1f})")
    L.append(f"oscillation amplitude        {m['amplitude_mm']:9.2f} mm   "
             f"(geom max {p.x_max*1e3:.1f})")
    L.append(f"stroke used                  {m['stroke_mm']:9.2f} mm   "
             f"(geom {p.stroke*1e3:.1f})")
    L.append("-" * 64)
    L.append(f"peak velocity                {m['v_peak']:9.2f} m/s")
    L.append(f"peak acceleration            {m['a_peak']:9.1f} m/s^2  "
             f"({m['a_peak']/9.81:.0f} g)")
    L.append(f"vibration force (m*a_peak)   {m['vib_force_N']:9.1f} N    "
             f"(ch.15 est ~890)")
    L.append("-" * 64)
    L.append(f"peak combustion pressure     {m['p_comb_peak_bar']:9.2f} bar")
    L.append(f"peak air-spring pressure     {m['p_under_peak_bar']:9.2f} bar")
    L.append("-" * 64)
    L.append(f"indicated (gas) power        {m['P_indicated_W']:9.1f} W")
    L.append(f"mech power into generator    {m['P_mech_gen_W']:9.1f} W")
    L.append(f"electrical power out         {m['P_elec_W']:9.1f} W   "
             f"(eta_gen {p.gen_eff:.2f})")
    L.append("=" * 64)
    return "\n".join(L)


if __name__ == "__main__":
    p = Params()
    res = simulate(p)
    print(report(p, res))
