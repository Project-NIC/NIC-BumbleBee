"""
Linear resonance model  --  DESIGN ch.14, OPEN-QUESTIONS B7/B8.

The air spring is the under-piston pre-compression chamber. For an adiabatic
gas spring of piston area A and instantaneous volume V at pressure p, the
stiffness about an operating point is

    k = gamma * p * A^2 / V          (k = -dF/dx, F = p*A, dV/dx = A)

Two opposing under-piston chambers (left + right) act in parallel on the moving
assembly, so k_air = 2 * k_chamber. Bushing leakage (ch.8) softens it slightly.

    f = (1/2pi) * sqrt(k_air / m)

This is the *linear* baseline about the centre. The combustion-side compression
adds a strong, intermittent, hardening stiffness near TDC -- reported here for
scale, but the true limit-cycle frequency comes from dynamics.py.
"""

import math
from params import Params, CC


def _air_pressure_at_centre(p: Params, v_mid: float, v_max: float) -> float:
    """Air-spring pressure at the centre position.

    Charge enters at p_intake at the largest (BDC-side) volume v_max and is
    adiabatically compressed to v_mid at the centre.
    """
    return p.p_intake * (v_max / v_mid) ** p.gamma_air


def air_spring_stiffness(p: Params, v_mid: float = None, v_max: float = None) -> float:
    """Linear air-spring stiffness k_air [N/m] of the two under-piston chambers."""
    if v_mid is None:
        v_mid = p.vol_under_mid()
    if v_max is None:
        v_max = p.v_clear_under + p.area_under * p.stroke
    p_centre = _air_pressure_at_centre(p, v_mid, v_max)
    k_one = p.gamma_air * p_centre * p.area_under ** 2 / v_mid
    return 2.0 * k_one * (1.0 - p.bushing_leak)


def natural_frequency(p: Params) -> float:
    """Air-spring-only natural frequency [Hz] for the current geometry/mass."""
    k = air_spring_stiffness(p)
    return math.sqrt(k / p.m_moving) / (2.0 * math.pi)


def combustion_stiffness(p: Params) -> float:
    """Hardening stiffness contribution of the two combustion chambers at centre.

    Charge is trapped at p_intake when the exhaust port closes (near BDC) and
    compressed adiabatically to the centre volume. Intermittent and strongly
    nonlinear -- this is an order-of-magnitude figure only.
    """
    v_trap = p.v_clear_comb + p.area_piston * p.stroke * (1.0 - p.port_open_frac)
    v_centre = p.vol_comb_right(0.0)
    p_centre = p.p_intake * (v_trap / v_centre) ** p.gamma_air
    k_one = p.gamma_air * p_centre * p.area_piston ** 2 / v_centre
    return 2.0 * k_one


def combined_frequency(p: Params) -> float:
    """Frequency if air spring + combustion-compression spring acted together."""
    k = air_spring_stiffness(p) + combustion_stiffness(p)
    return math.sqrt(k / p.m_moving) / (2.0 * math.pi)


def mass_for_target(p: Params, f_target: float = None) -> float:
    """Moving mass [kg] that puts the AIR-SPRING resonance on f_target (B8)."""
    if f_target is None:
        f_target = p.f_target
    k = air_spring_stiffness(p)
    return k / (2.0 * math.pi * f_target) ** 2


def plenum_for_target(p: Params, f_target: float = None):
    """Extra dead under-piston volume [m^3] to soften the air spring onto f_target.

    Adding a plenum Vp raises both v_mid and v_max equally (swept volume
    unchanged), lowering the pre-compression ratio and the spring rate. Returns
    (Vp, achieved_f, note). Vp < 0 means the target is *below* what a plenum can
    reach from here (spring already too soft) -- you would instead reduce volume,
    add mass, or boost. If the natural frequency is already below target, a
    plenum cannot help (it only lowers f); note says so.
    """
    if f_target is None:
        f_target = p.f_target
    f_nat = natural_frequency(p)
    if f_target >= f_nat:
        return (0.0, f_nat,
                f"target {f_target:.1f} Hz >= natural {f_nat:.1f} Hz; a plenum "
                f"only LOWERS f. Raise it by: less volume, more boost, or less mass.")

    v_mid0 = p.vol_under_mid()
    v_max0 = p.v_clear_under + p.area_under * p.stroke

    def f_with_plenum(vp):
        k = air_spring_stiffness(p, v_mid=v_mid0 + vp, v_max=v_max0 + vp)
        return math.sqrt(k / p.m_moving) / (2.0 * math.pi)

    lo, hi = 0.0, 1.0  # 1 m^3 is an absurd upper bound; bisection converges fast
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if f_with_plenum(mid) > f_target:
            lo = mid
        else:
            hi = mid
    vp = 0.5 * (lo + hi)
    return (vp, f_with_plenum(vp), "ok")


def boost_for_target(p: Params, f_target: float = None) -> float:
    """Intake (boost) pressure [Pa] that lifts the air-spring resonance to f_target.

    k_air is proportional to operating pressure, which scales with p_intake, so
    f scales with sqrt(p_intake). Returns the required absolute intake pressure.
    """
    if f_target is None:
        f_target = p.f_target
    f_nat = natural_frequency(p)
    return p.p_intake * (f_target / f_nat) ** 2


def report(p: Params) -> str:
    f_nat = natural_frequency(p)
    k_air = air_spring_stiffness(p)
    k_comb = combustion_stiffness(p)
    f_comb = combined_frequency(p)
    m_t = mass_for_target(p)
    vp, f_vp, note = plenum_for_target(p)
    p_boost = boost_for_target(p)

    lines = []
    lines.append("=" * 64)
    lines.append("  LINEAR RESONANCE  (DESIGN ch.14 / OQ-B7,B8)")
    lines.append("=" * 64)
    lines.append(p.summary())
    lines.append(f"air-spring stiffness k_air      {k_air:10.1f} N/m")
    lines.append(f"combustion stiffness  k_comb    {k_comb:10.1f} N/m  (intermittent)")
    lines.append(f"under-piston vol @centre        {p.vol_under_mid()/CC:10.2f} cm^3")
    lines.append("-" * 64)
    lines.append(f"natural f (air spring only)     {f_nat:10.2f} Hz")
    lines.append(f"combined f (air + combustion)   {f_comb:10.2f} Hz  (upper bound)")
    lines.append("-" * 64)
    lines.append(f"TARGET frequency                {p.f_target:10.2f} Hz")
    lines.append("  reach it by ONE of:")
    lines.append(f"   - moving mass                {m_t:10.3f} kg   (now {p.m_moving:.3f})")
    if note == "ok":
        lines.append(f"   - extra under-piston plenum  {vp/CC:10.2f} cm^3 "
                     f"(-> {f_vp:.1f} Hz)")
    else:
        lines.append(f"   - plenum: N/A  ({note})")
    lines.append(f"   - intake boost pressure      {p_boost/1e5:10.3f} bar abs")
    lines.append("=" * 64)
    return "\n".join(lines)


if __name__ == "__main__":
    print(report(Params()))
