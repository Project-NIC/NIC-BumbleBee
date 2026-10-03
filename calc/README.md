# calc/ — NIC-FPLG: dynamics emulator & first calculations

*[English](README.md) · [Čeština](README_cs.md) · [Русский](README_ru.md)*

*A dependency-light 0D emulator for the free-piston dynamics of the NIC-FPLG.
It exists to answer the first numbers the design is waiting on (DESIGN ch.14:
"Specific numbers TBD — first task for `calc/`").*

---

## What it is (and isn't) — honestly

**It is** a lumped 0D model: one degree of freedom, ideal-gas chambers,
idealised port blow-down and scavenge (a pressure reset, not a flow model).
It is the right tool for **dynamics, resonance, amplitude, control and
first-order estimates**. Every input is a *seed*, not a result.

**It is not** CFD (scavenging/stratification — OQ-A3), the magnetic circuit
(OQ-C/FEM), or fatigue life (OQ-D). That is where the handoff to professional
tools begins (see below).

---

## Run it

```bash
pip install -r requirements.txt
python3 run.py                 # full run: report + plots + CSV in out/
python3 run.py --no-plots      # text + CSV only (no matplotlib)
python3 verify.py              # self-tests — run before trusting any number
```

Everything you can change lives in [`params.py`](params.py); each field cites
the design chapter or open question it comes from.

---

## Files

| file | what it does |
|------|--------------|
| `params.py`    | central parameter set (all SI), chamber-volume geometry |
| `resonance.py` | linear air-spring resonance (DESIGN ch.14) |
| `dynamics.py`  | nonlinear time-domain free-piston limit cycle (model core) |
| `run.py`       | runs both, sweeps generator load into an operating map, writes `out/` |
| `freq_hold.py` | constant-frequency line: how mixture + load hold one frequency as power varies |
| `control.py`   | coupled PI control (mixture↔power, load↔frequency) under ignition scatter — item 22 |
| `valves.py`    | in-piston transfer-valve force budget and inertial delay — ch.5 / item 9 |
| `twin.py`      | two-module anti-phase balancing: residual force and rocking couple — ch.15 / item 10 |
| `tradeoff.py`  | mass ↔ frequency ↔ valve ↔ vibration ↔ power — items 8/9/10 |
| `thermo.py`    | 0D thermodynamic cycle (real fuel, Wiebe, Woschni) — ch.4 / item 1 |
| `compression.py` | amplitude → effective compression → efficiency — ch.4 / item 1 |
| `magnetics.py` | first-cut magnetic circuit: air-gap flux, turns, demag margin — ch.8 / OQ-C |
| `exhaust_acoustics.py` | 1D exhaust acoustics / Y-ejector feasibility — ch.9 / OQ-A5 |
| `verify.py`    | self-tests: step convergence, physics vs analytic, energy balance |
| `out/`         | generated plots and CSV |

---

## What today's numbers say (headline)

**1. The combustion spring sets the frequency, not the air spring.** The
under-piston air spring alone is soft (~10 Hz at 1 kg). The combustion-compression
stiffness (which rises with pressure) dominates, so the limit cycle self-selects
**~40 Hz** (above the original 30 Hz estimate). The frequency is therefore **not
fixed by geometry alone** — the mixture + load loops hold it (ch.12, `freq_hold.py`,
`control.py`).

**2. Mass is the master lever — `tradeoff.py`.** f ∝ 1/√m. At fixed amplitude the
vibration force tracks the combustion force, so heavier mass does *not* reduce it
— lighter is better for both power and vibration. A heavy steel piston therefore
*lowers* the frequency (and the cycle count → helps life) — your robust choices
all point the same way.

**3. Vibration — `twin.py`.** A single module is ~1.4 kN; the anti-phase pair
cancels the net *force* by ~88 %, but leaves a *rocking couple* (~165 N·m at
120 mm spacing) that the mounts carry. Shrink it by stacking the modules coaxially.

**4. Generator magnetic circuit (first cut) — `magnetics.py`.** A reluctance-network
estimate gives a ~0.9 T air gap, ~185 turns/phase for the 110 V peak bus, and ~1.1 kN
of force for 3 kW. The key result is a **demagnetisation margin of ~8×** against the
magnet's hot coercivity: the cancellable hybrid field looks geometrically feasible
**without permanent demag, if the field flux is routed around the magnets** (ch.8).
This is 1D reluctance only — FEMM/Maxwell still owns the verdict (OQ-C), but the
Section-C bet survives a first look.

**5. Exhaust acoustics / Y-ejector — `exhaust_acoustics.py`.** At 40 Hz the exhaust-gas
wavelength is ~17 m and a tuned quarter-wave pipe would need ~4.2 m — impossible in a
compact engine. So a **tuned exhaust is off the table** at this frequency, which confirms
the open-exhaust choice (ch.9): the engine does not lose charge to the pipe, so it needs
no tuned chamber. The Y-ejector, if it helps at all, is a mild direct pulse cross-coupling,
not a resonance — worth checking only with unsteady 1D/CFD (OQ-A5).

**Not computed here.** Knock, combustion chemistry and NOx, the hot piston–cylinder clearance, the heat balance, fatigue to 10⁹ cycles and the route to 50 Hz are not questions for a 0D model: they need better software — CFD with chemistry, Cantera, FEA — or a built engine on a test stand (*Handoff to professional tools*, below).

---

## How far to trust it

`verify.py` checks three things (all pass): the limit cycle is step-independent;
with combustion and damping off the free oscillation matches the analytic resonance
to ~1 %; the energy balance closes. It does **not** guarantee the *absolute*
frequency — that rides on the combustion seeds, so read absolute numbers as
±a few Hz until the 0D/1D cycle (OQ-A1) and a prototype pin them down. The *trends*
(which lever moves f, and by how much) are robust.

---

## Handoff to professional tools (= your OPEN-QUESTIONS)

| question | tool |
|----------|------|
| Scavenging & stratification (OQ-A3) — *the load-bearing one* | 3D CFD with chemistry: Converge, AVL FIRE, STAR-CCM+, or free OpenFOAM |
| 1D charge exchange, exhaust ejector (OQ-A2, A5) — *first cut in `exhaust_acoustics.py`* | GT-Power, Ricardo WAVE, AVL BOOST |
| Magnetic circuit, demagnetisation (OQ-C) — *first cut in `magnetics.py`* | FEM: FEMM (free, 2D-axisymmetric — ideal for a tubular machine), Ansys Maxwell |
| Fatigue to 10⁹ cycles (OQ-D) | FEA + **pulsator** (a test, not a simulation) |
| Better combustion chemistry / NOx | Cantera (free, Python) — still doable in 0D |

---

*This document is live. Specific objections welcome in Issues.*

★ Viva La Resistánce ★
