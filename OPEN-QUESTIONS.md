# Open Questions — What We Don't Know Yet

*An honest list. The concept rests on principles that make physical sense,
but the numbers don't exist yet. This is a brief for simulations, calculations,
and a prototype — and an open invitation: if you can advance any item here,
open an Issue. The answer "I don't know, but I'd try this" is worth more than
applause and more than a blanket dismissal.*

---

## A. Thermodynamics and Charge Exchange

1. **0D/1D cycle model** — pressures, temperatures, work, efficiency at the
   design point. Without this, all power targets (~3 kW mechanical) are estimates.
   **Update** (`calc/thermo.py`): a 0D closed cycle (real fuel, Wiebe burn,
   Woschni heat loss, residual fraction) on the limit-cycle kinematics. At
   φ ≈ 0.8 it gives ~5.8 bar IMEP (the 5 bar seed was about right), ~22 bar peak,
   ~2400 K peak, **~26 % thermal efficiency (not 38 %)**. Two real findings: the
   exhaust port opens early (expansion cut short), and the **effective
   compression ratio is only ~3.5, not the geometric 9** — the piston reverses
   at ~18 mm instead of reaching the head, so running at higher amplitude is the
   main efficiency lever (quantified in `calc/compression.py`: 17 → 23 mm lifts
   the effective ratio ~3.2 → ~5.6 and efficiency ~25 → ~33 %, costing peak
   pressure ~20 → ~29 bar). Still needs a 1D charge-exchange model and chemistry
   (peak T is an upper bound) — see A3.
2. **Exhaust port timing** — upper edge height vs. expansion length vs.
   scavenging quality. Strategy: drill low first, tune by milling edge upward.
   Needs: 1D charge-exchange simulation, then experiment.
3. **CFD of scavenging and stratification** — do the drop-shaped nozzles + squish
   actually keep the rich zone under the plug and exhaust gas at the wall?
   The key emissions and efficiency assumption of the entire concept.
4. **Internal EGR** — what fraction of retained exhaust gas is optimum; confirm
   that flash evaporation on hot inert gas does not lead to autoignition
   (temperature boundary).
   **Update** (`calc/chem.py` Cantera; `calc/knock.py`): NOx rides on peak temperature, not leanness — equilibrium NO peaks slightly lean; only lower temperature via internal EGR cuts it (~20 % → NO ~10,700→~4,900 ppm; ~30 % → ~1,700 ppm). Knock: gasoline/LPG have margin, heavy fuel (~70 ON) knocks = the real ceiling on work-per-cycle. Both hinge on how the geometry holds temperature/stratification (A3).
5. **Ejector effect in Y junction** — branch lengths vs. pulse phase (speed of
   sound in exhaust gas ~500–600 m/s). Does sub-pressure assist scavenging,
   or is the effect negligible?
   **Update** (`calc/exhaust_acoustics.py`): at 40 Hz the wavelength is ~17 m and a quarter-wave ~4.2 m → a tuned exhaust is impossible in a compact engine. The ejector is at most a mild direct pulse effect, not a resonance — confirming the open-exhaust choice. Whether it helps at all = 1D/CFD.
6. **Heat transfer** — balance: how much into aluminium, how much out with
   exhaust, how much does the intake mixture heat up passing through the
   generator (loss of volumetric efficiency vs. cooling gain).
   **Update** (`calc/heat.py`): of the fuel ~26 % to work, ~12 %+ to the walls (→ fins ~1–2 kW; less than the 2–4 kW estimate), ~62 % out with the hot exhaust (~1700 K) — the fins have a more modest job.

## B. Dynamics and Resonance

7. **System resonant frequency** — f = (1/2π)√(k/m): calculate under-piston
   volume for target frequency; effect of bushing leakage on effective stiffness;
   effect of variable air spring stiffness (non-linearity) on oscillation shape.
   **First task for `calc/` — now under way (see [`calc/`](calc/)).**
   First result from the 0D model: the under-piston air spring alone is soft
   (~10 Hz at 1 kg), and stiffness is dominated by the **combustion-side
   compression spring**, whose rate scales with pressure. The limit cycle
   therefore self-selects ~40 Hz (above the 30 Hz working estimate) **and the
   frequency drifts with load/amplitude** (~40–48 Hz across the usable load
   window — see item below in section G). Open: can one operating frequency
   really be held, or is "frequency set by the physical system, not control"
   only approximate? Needs the coupled mech×EM×thermo model and a prototype.
   **Update:** `calc/freq_hold.py` shows mixture (fuel energy) is a second
   actuator — load carries the power change, mixture trims the frequency back —
   and the two together hold ~40 Hz at near-constant peak pressure across
   ~1.2–1.7 kW. So the frequency *can* be held, just not by geometry alone.
   **50 Hz target** (`calc/freq50.py`): the frequency knob is the stroke (shorter → higher f); compression alone only ~47 Hz, pre-compression does not move it. Either a shorter stroke (any fuel) or stroke+compression (gasoline/LPG only). Cost: ~1.8 billion cycles/10,000 h vs 1.4 billion at 40 Hz.
8. **Moving assembly mass** — real figures (pistons + rod + teeth + end caps +
   spring share); every gram shifts resonance and vibration.
   **Update** (`calc/tradeoff.py`): mass is the master knob (f ∝ 1/√m), but the
   trade is not what you'd expect — at fixed amplitude the vibration force tracks
   the (roughly constant) combustion force, so heavier mass does *not* reduce it
   (it slightly rises). Lighter mass is better for both power and vibration. The
   stock 25 g valve transfers from ~0.7 kg (46 Hz) up (with margin at the ~40 Hz
   operating point), so the valve is not the binding constraint — the remaining
   cost of higher frequency is vibration, handled by the anti-phase twin.
9. **In-piston valve force budget** — spring vs. pressure differential vs.
   inertia through the full cycle; magnitude and stability of the inertial
   opening delay (asymmetric timing). Actual valve mass.
   **Update** (`calc/valves.py`): with a **1 N seat spring** (the spring only
   seats the valve; the gas dynamics do the work) and ~2.5:1 pre-compression,
   the **stock 25 g motorcycle exhaust valve transfers** — it opens ~36° after
   BDC, giving the exhaust-first/transfer-second asymmetric timing for free.
   Opening pressure (~32 N) and inertia (~35 N) come out comparable, as ch.5
   claims, and combustion slams it shut (~300 N = backfire check, ch.20).
   Pre-compression is the tuning knob (more → opens earlier, less delay). No
   special lightweight valve needed — which was the whole point of using a
   stock heat-resistant exhaust valve.
10. **Vibration and mounting** — forces into the frame, anti-vibration mount
    design; when to move to two-module anti-phase arrangement.
    **Update** (`calc/twin.py`): anti-phase cancels the net shaking *force*
    strongly (1387 N → 162 N, −88 %, odd-harmonic-dominated cycle), but leaves a
    large *rocking couple* (~165 N·m at 120 mm spacing) that the mounts must
    carry. Stacking the modules coaxially (smaller spacing) shrinks it.
11. **Limit-condition behaviour** — piston-to-head contact: impact energy,
    stress in joint, thread, sleeve flange (single event and repeated).
    **Update** (`calc/fatigue.py`): at ~1.7 kN the rod stress is ~8 MPa vs a ~230 MPa endurance limit — 50–100× margin. The bulk is over-built; the 10⁹-cycle fight is in local details (thread finish, fretting, creep) → FEA + pulsator.

## C. Generator and Magnetics

12. **FEM of magnetic circuit** — geometry of field flux routing **around**
    permanent magnets (not through them against polarisation). Demagnetisation
    analysis at temperature = service life condition. Magnet selection
    (NdFeB SH/UH vs. SmCo).
    **Update** (`calc/magnetics.py`): a first-cut reluctance estimate gives a ~0.9 T air gap, ~185 turns for 110 V peak and a **demagnetisation margin ~8×** against the hot coercivity — the cancellable field looks geometrically feasible, *if* the flux is routed around the magnets. FEMM/Maxwell still decides.
13. **PM/field winding ratio** — 50/50 working hypothesis; steady field
    winding losses (I²R) vs. field control range. Optimisation.
14. **Air gap** — concentricity tolerance through bushings; sensitivity of
    power and forces to eccentricity.
15. **Losses** — iron (0.3 mm @ ~100 Hz), eddy currents in residual solid
    parts, generator efficiency at operating point.
16. **Induced voltage vs. stroke** — EMF profile over the stroke (end effects
    at stroke limits), coil turn count design for ~100 V DC after rectification.

## D. Fatigue and Service Life (10⁹ Cycles)

17. **Rod threaded joints** — preload, stress amplitude in thread root,
    life calculation; pulse-test verification.
18. **Tooth lamination pack on rod** — creep of insulating ring under press-fit
    load, epoxy fatigue under shock, thermal cycling. Material choices (PEEK?).
19. **Conical valve springs** — life under combined valve lift and oscillation
    with the piston.
20. **Piston rings across drilled ports** — port-to-bridge ratio, edge treatment;
    wear rate over time.
21. **Spherical-segment joints** — contact pressure, lubrication regime, nitriding
    specification.

## E. Control

22. **Amplitude regulation by load/excitation** — control algorithm (ms response),
    loop stability across full range; coupled simulation (mechanics × electromagnetics
    × thermodynamics).
    **Update** (`calc/control.py`): two PI loops (mixture↔power, load↔frequency)
    hold the setpoints across stepped power demand (1.2→1.55→1.3 kW) with 6 %
    per-firing ignition scatter — frequency stays at 40 Hz (±~0.6 Hz). The
    coupled loop is stable in 0D; next step is to add the real generator
    electromagnetics and the start/misfire transients.
23. **Start sequence** — energy and time to oscillate in motor mode; minimum
    amplitude for first ignition; duration of zero-field phase (without
    electromagnetic braking).
24. **Misfire recovery cycle** — how much energy remains, recoverability limit,
    number of retry attempts.
25. **Position sensing from coil voltage** — accuracy vs. inductive sensors;
    fusion of three sources.

## F. Parameters to Be Determined

| Parameter                         | Status                                |
|-----------------------------------|---------------------------------------|
| Stroke                            | TBD (linked to resonance and power)   |
| Mechanical frequency              | TBD (set by resonance; tens of Hz)    |
| Compression ratio above piston    | TBD (multi-fuel compromise)           |
| Pre-compression chamber volume    | TBD (from resonance, ch. 14 DESIGN)   |
| Exhaust port height / count       | TBD (1D simulation + tuning)          |
| Component masses (valve, piston…) | TBD (linked to everything above)      |
| Noise / damping                   | TBD                                   |
| Emissions (HC/NOx/CO)             | TBD (prototype measurement)           |

## G. What Would Falsify the Concept

*Being honest with ourselves — these are the blows that could kill it:*

- CFD shows stratification collapses under realistic scavenging → emissions
  and efficiency advantage disappears,
- inertial valve delay proves too large or unstable → transfer timing fails,
  power collapses,
- demagnetisation analysis shows the cancellable field cannot be achieved in
  the available space → start concept and amplitude control both fall,
- rod joint fatigue does not reach 10⁹ cycles within a reasonable cross-section →
  joint architecture must change fundamentally,
- coupled simulation cannot hold stable amplitude under realistic ignition
  scatter → control becomes prohibitively complex,
- the operating frequency is not fixed by geometry alone — it drifts with
  load/amplitude because the dominant spring (combustion compression) is
  pressure-dependent. *Mitigation found* (0D, `calc/freq_hold.py`): mixture +
  load together hold it constant (~40 Hz, near-constant peak pressure) across
  ~1.2–1.7 kW, matching the ch.12 loops. *Residual risk:* this leans on the
  mixture loop having enough authority inside the lean, knock-free, stratified
  envelope — if that authority is too small, or the coupled loop is unstable
  under real ignition scatter, constant-frequency operation across the power
  range fails.

Each of these can be verified **before** spending money on manufacturing.
That is why this file is in the repo first.

---

★ Viva La Resistánce ★
