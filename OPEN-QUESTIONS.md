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
2. **Exhaust port timing** — upper edge height vs. expansion length vs.
   scavenging quality. Strategy: drill low first, tune by milling edge upward.
   Needs: 1D charge-exchange simulation, then experiment.
3. **CFD of scavenging and stratification** — do the drop-shaped nozzles + squish
   actually keep the rich zone under the plug and exhaust gas at the wall?
   The key emissions and efficiency assumption of the entire concept.
4. **Internal EGR** — what fraction of retained exhaust gas is optimum; confirm
   that flash evaporation on hot inert gas does not lead to autoignition
   (temperature boundary).
5. **Ejector effect in Y junction** — branch lengths vs. pulse phase (speed of
   sound in exhaust gas ~500–600 m/s). Does sub-pressure assist scavenging,
   or is the effect negligible?
6. **Heat transfer** — balance: how much into aluminium, how much out with
   exhaust, how much does the intake mixture heat up passing through the
   generator (loss of volumetric efficiency vs. cooling gain).

## B. Dynamics and Resonance

7. **System resonant frequency** — f = (1/2π)√(k/m): calculate under-piston
   volume for target frequency; effect of bushing leakage on effective stiffness;
   effect of variable air spring stiffness (non-linearity) on oscillation shape.
   **First task for `calc/`.**
8. **Moving assembly mass** — real figures (pistons + rod + teeth + end caps +
   spring share); every gram shifts resonance and vibration.
9. **In-piston valve force budget** — spring vs. pressure differential vs.
   inertia through the full cycle; magnitude and stability of the inertial
   opening delay (asymmetric timing). Actual valve mass.
10. **Vibration and mounting** — forces into the frame, anti-vibration mount
    design; when to move to two-module anti-phase arrangement.
11. **Limit-condition behaviour** — piston-to-head contact: impact energy,
    stress in joint, thread, sleeve flange (single event and repeated).

## C. Generator and Magnetics

12. **FEM of magnetic circuit** — geometry of field flux routing **around**
    permanent magnets (not through them against polarisation). Demagnetisation
    analysis at temperature = service life condition. Magnet selection
    (NdFeB SH/UH vs. SmCo).
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
  scatter → control becomes prohibitively complex.

Each of these can be verified **before** spending money on manufacturing.
That is why this file is in the repo first.

---

★ Viva La Resistánce ★
