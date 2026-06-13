#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
First-cut analytical magnetic circuit of the tubular generator (DESIGN ch.8 / OQ-C).

NOT a substitute for FEMM/Maxwell -- it is a reluctance-network sanity bound that
answers the one question that is otherwise pure "TBD, FEM": is the cancellable
hybrid field geometrically feasible without permanently demagnetising the magnets,
and roughly how many turns give the target bus voltage?

Method:
  * PM load line in a simple gap + magnet reluctance loop -> air-gap flux density
  * EMF from flux switching: e = N * dPhi/dt, with dPhi/dt set by rod velocity
    and the pole pitch -> turns N for the target peak voltage
  * force / power check against the mechanical target
  * demagnetisation margin: demagnetising H in the magnet from the field/armature
    MMF vs the magnet intrinsic coercivity Hci at hot operating temperature

All inputs are labelled seeds -- override with reality.
"""
import math
from params import Params, BAR
import dynamics

MU0 = 4e-7 * math.pi

# --- magnetic seeds (override with reality) ----------------------------
B_R        = 1.20      # T     NdFeB SH/UH remanence (cold)
HCI_COLD   = 1900e3    # A/m   intrinsic coercivity (cold), |Hci|
MU_REC     = 1.05      # -     recoil permeability
T_MAGNET   = 120.0     # C     hot magnet operating temperature
DBR_DT     = -0.0012   # /K    Br temperature coefficient (~-0.12 %/K)
DHCI_DT    = -0.005    # /K    Hci temperature coefficient (~-0.5 %/K, SH grade)

GAP        = 0.0005    # m     radial air gap (rod tooth <-> stator pole)
L_MAGNET   = 0.006     # m     magnet length in the flux direction
A_POLE     = 4.0e-4    # m^2   pole face area (one tooth/pole), seed
POLE_PITCH = 0.008     # m     tooth/pole pitch along the rod

V_BUS_PEAK = 110.0     # V     target peak AC per phase (-> ~100 V DC after rect.)
P_MECH     = 3000.0    # W     mechanical target
FIELD_NI   = 700.0     # A-turns  field MMF roughly needed to null/reverse the flux


def hot(value, tempco):
    return value * (1.0 + tempco * (T_MAGNET - 20.0))


def main():
    p = Params()
    print("running operating point for velocity ...")
    m = dynamics.simulate(p, dt=3e-6, t_end=2.2)["metrics"]
    f_mech = m["freq_hz"]
    v_peak = m["v_peak"]                       # m/s
    print("done.\n")

    Br = hot(B_R, DBR_DT)
    Hci = hot(HCI_COLD, DHCI_DT)

    # --- air-gap flux density from PM load line -------------------------
    # series loop: magnet + two gaps; B_gap ~ Br / (1 + mu_rec * 2*GAP / L_MAGNET)
    B_gap = Br / (1.0 + MU_REC * (2.0 * GAP / L_MAGNET))
    phi_pole = B_gap * A_POLE                   # Wb per pole

    # --- electrical frequency from flux switching -----------------------
    # one full flux cycle per pole pair traversed = 2 * POLE_PITCH (peak, at v_peak)
    f_elec = v_peak / (2.0 * POLE_PITCH)
    omega_e = 2.0 * math.pi * f_elec

    # --- turns for target voltage (e_peak = N * phi * omega_e) ----------
    N_turns = V_BUS_PEAK / (phi_pole * omega_e)

    # --- force / power sanity -------------------------------------------
    v_avg = (2.0 / math.pi) * v_peak            # sinusoidal average
    F_need = P_MECH / max(v_avg, 1e-3)

    # --- demagnetisation margin -----------------------------------------
    H_demag = FIELD_NI / L_MAGNET               # A/m, worst case all across magnet
    margin = Hci / H_demag

    print("=" * 66)
    print("  FIRST-CUT MAGNETIC CIRCUIT  (generator, ch.8 / OQ-C)")
    print("=" * 66)
    print(f"  operating point: f_mech {f_mech:.0f} Hz, v_peak {v_peak:.2f} m/s")
    print(f"  magnet hot ({T_MAGNET:.0f} C): Br {Br:.2f} T, Hci {Hci/1e3:.0f} kA/m")
    print("-" * 66)
    print(f"  air-gap flux density        {B_gap:6.2f} T")
    print(f"  flux per pole               {phi_pole*1e6:6.1f} uWb")
    print(f"  electrical freq (peak)      {f_elec:6.0f} Hz")
    print(f"  turns for {V_BUS_PEAK:.0f} V peak        {N_turns:6.0f} turns/phase")
    print(f"  force needed for {P_MECH/1e3:.0f} kW     {F_need:6.0f} N")
    print("-" * 66)
    print(f"  demagnetising H (field MMF) {H_demag/1e3:6.0f} kA/m")
    print(f"  margin to Hci (hot)         {margin:6.1f} x")
    print("=" * 66)
    print("  READING:")
    if margin > 1.5:
        print(f"  The nulling/reversing field stays below the magnet's hot coercivity")
        print(f"  (margin ~{margin:.0f}x) -> the cancellable hybrid field looks geometrically")
        print("  feasible WITHOUT permanent demag, IF the field flux is routed AROUND the")
        print("  magnets (DESIGN ch.8). That is the key Section-C bet, and it survives a")
        print("  first look.")
    elif margin > 1.0:
        print(f"  Margin only ~{margin:.1f}x -- tight. Hot corner + armature reaction could")
        print("  push a magnet past its knee. Wants a higher-coercivity grade or more iron.")
    else:
        print(f"  Margin < 1 -- the field MMF would demagnetise the magnet. Lower field NI,")
        print("  shorter gap, or route the flux fully around the magnets.")
    print()
    print("  Honest limits: 1D reluctance only -- no leakage, no saturation, no")
    print("  armature-reaction detail, ideal flux routing. Real verdict = FEMM/Maxwell")
    print("  (OQ-C). This bounds whether the concept is worth modelling, not the number.")


if __name__ == "__main__":
    main()
