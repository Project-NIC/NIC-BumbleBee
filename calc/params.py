"""
NIC-FPLG — central parameter set for the calc/ models.

Every value here is a *working seed*, not a result. Numbers marked (TBD in
DESIGN/OPEN-QUESTIONS) are first guesses chosen only so the models run; the
whole point of calc/ is to let you sweep them and find the real ones.

References point at the design documents:
  DESIGN  -> DESIGN-FPLG.md (chapter numbers)
  OQ      -> OPEN-QUESTIONS.md (item numbers)

SI units throughout (m, kg, s, Pa, J, N, Hz) unless a name says otherwise.
"""

from dataclasses import dataclass, field
import math

BAR = 1.0e5          # Pa per bar
CC = 1.0e-6          # m^3 per cm^3


@dataclass
class Params:
    # ---- Moving assembly (OQ-8, DESIGN ch.15) ---------------------------
    # pistons + rod + teeth + end caps + spring share. ch.15 working est. ~1 kg.
    m_moving: float = 1.0            # kg

    # ---- Cylinder geometry (DESIGN ch.4, ch.15; table F) ----------------
    bore: float = 0.036              # m   piston / cylinder diameter (TBD)
    stroke: float = 0.050            # m   total travel BDC->TDC (ch.15 = 50 mm)
    rod_dia: float = 0.025           # m   stainless tube OD (ch.7); sets under-
                                     #     piston effective area
    comp_ratio: float = 9.0          # -   geometric CR above piston (TBD,
                                     #     multi-fuel compromise, table F)

    # ---- Pre-compression / under-piston air spring (DESIGN ch.3, ch.14) -
    precomp_ratio: float = 2.5       # -   ~1:2 target (ch.3); raised slightly to
                                     #     give the stock transfer valve enough
                                     #     opening force at a ~1 N seat spring
                                     #     (see valves.py / tradeoff.py)
    p_intake: float = 1.00 * BAR     # Pa  abs pressure of fresh charge entering
                                     #     under-piston chamber (1.0 = naturally
                                     #     aspirated; raise for boost study)
    bushing_leak: float = 0.05       # -   fraction of air-spring stiffness lost
                                     #     to bushing labyrinth leakage (ch.8,
                                     #     ch.14 correction). 0 = perfect seal.

    # ---- Gas properties --------------------------------------------------
    gamma_air: float = 1.40          # -   fresh charge (compression spring)
    gamma_burn: float = 1.30         # -   burned-gas expansion (effective)
    T_intake: float = 330.0          # K   charge temp after passing generator

    # ---- Combustion (DESIGN ch.4, ch.11; OQ-1) --------------------------
    # Energy released per firing per cylinder. Seed from a target BMEP so the
    # power lands near the ~3 kW mechanical goal; tune against a 0D cycle (OQ-1).
    bmep_target: float = 5.0 * BAR   # Pa  indicated-mean-effective-pressure seed
    eta_indicated: float = 0.38      # -   fuel heat -> indicated work (0D, OQ-1)
    burn_duration_frac: float = 0.15 # -   burn spread, as fraction of half-cycle
    ign_pressure_ratio: float = 4.0  # -   fire when compression pressure exceeds
                                     #     this * p_intake. A free piston has no
                                     #     fixed TDC -- ignition is referenced to
                                     #     compression, which self-regulates
                                     #     amplitude (DESIGN ch.12).

    # ---- Exhaust ports (DESIGN ch.3, ch.9; OQ-2) ------------------------
    port_open_frac: float = 0.20     # -   ports uncovered in last 20% before BDC
    p_exhaust: float = 1.02 * BAR    # Pa  manifold back-pressure ("open" exhaust)

    # ---- Generator electromagnetic load (DESIGN ch.12, ch.13; OQ-22) ----
    # Linear damping coefficient: F_gen = -c_gen * v. Average extracted power
    # = c_gen * <v^2>. This is the amplitude actuator (ch.12).
    c_gen: float = 150.0             # N/(m/s)  load seed (sits mid-window;
                                     #          ~1.35 kW elec, ~7 mm head margin)
    gen_eff: float = 0.92            # -   mech -> electrical efficiency

    # ---- Motor-mode start (DESIGN ch.12, start sequence; OQ-23) ---------
    # Generator runs as a motor and pumps energy into the oscillation until the
    # first ignition. Modelled as positive velocity feedback F_motor = +gain*v
    # (an energy source), switched off the instant a chamber fires. Builds the
    # oscillation at the system's own frequency regardless of mass -> removes
    # the start sensitivity of a fixed kick.
    motor_gain: float = 60.0         # N/(m/s)  start-pump gain

    # ---- Parasitic friction (boundary-lubricated joints/rings) ----------
    c_visc: float = 2.0              # N/(m/s) viscous
    f_coulomb: float = 5.0           # N       dry/boundary

    # ---- Design target --------------------------------------------------
    f_target: float = 30.0           # Hz  desired mechanical frequency (ch.15)

    # ---- Derived (filled in __post_init__) ------------------------------
    area_piston: float = field(init=False)
    area_under: float = field(init=False)
    x_max: float = field(init=False)
    v_clear_comb: float = field(init=False)
    v_clear_under: float = field(init=False)

    def __post_init__(self):
        self.area_piston = math.pi * 0.25 * self.bore ** 2
        # under-piston (crankcase) side loses the rod cross-section
        self.area_under = self.area_piston - math.pi * 0.25 * self.rod_dia ** 2
        self.x_max = 0.5 * self.stroke
        # clearance volume above piston from CR:  CR = (Vc + A*S)/Vc
        self.v_clear_comb = self.area_piston * self.stroke / (self.comp_ratio - 1.0)
        # under-piston clearance from precompression ratio (swept by area_under)
        self.v_clear_under = (self.area_under * self.stroke /
                              (self.precomp_ratio - 1.0))

    # ---- Volume / area helpers (x = rod displacement from centre, +right) ----
    def vol_comb_right(self, x):
        """Right combustion chamber volume. Min (TDC) at x=+x_max."""
        return self.v_clear_comb + self.area_piston * (self.x_max - x)

    def vol_comb_left(self, x):
        """Left combustion chamber volume. Min (TDC) at x=-x_max."""
        return self.v_clear_comb + self.area_piston * (self.x_max + x)

    def vol_under_right(self, x):
        """Right under-piston (pre-compression) chamber. Min at x=-x_max."""
        return self.v_clear_under + self.area_under * (self.x_max + x)

    def vol_under_left(self, x):
        """Left under-piston (pre-compression) chamber. Min at x=+x_max."""
        return self.v_clear_under + self.area_under * (self.x_max - x)

    def vol_under_mid(self):
        """Under-piston chamber volume at the centre (x=0)."""
        return self.v_clear_under + self.area_under * self.x_max

    def swept_volume(self):
        return self.area_piston * self.stroke

    def summary(self):
        return (
            f"bore           {self.bore*1e3:7.2f} mm\n"
            f"stroke         {self.stroke*1e3:7.2f} mm\n"
            f"rod dia        {self.rod_dia*1e3:7.2f} mm\n"
            f"piston area    {self.area_piston*1e4:7.3f} cm^2\n"
            f"under area     {self.area_under*1e4:7.3f} cm^2\n"
            f"swept vol/cyl  {self.swept_volume()/CC:7.2f} cm^3\n"
            f"comp ratio     {self.comp_ratio:7.2f}\n"
            f"precomp ratio  {self.precomp_ratio:7.2f}\n"
            f"moving mass    {self.m_moving:7.3f} kg\n"
            f"target freq    {self.f_target:7.2f} Hz\n"
        )
