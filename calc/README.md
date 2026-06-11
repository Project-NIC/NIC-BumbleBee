# calc/ — NIC-FPLG dynamics & resonance emulator

A small, dependency-light **0D emulator** for the free-piston dynamics of the
NIC-FPLG. It exists to answer the first numbers the design is waiting on
(DESIGN ch.14: *"Specific numbers TBD — first task for `calc/`"*):

- **piston / cylinder sizing** and the **oscillation amplitude** ("rozkmit"),
- the **resonant / limit-cycle frequency**,
- the **generator-load operating map** (amplitude regulation, DESIGN ch.12),
- compression pressures, vibration force, indicated and electrical power.

It directly addresses **OPEN-QUESTIONS items B7, B8** and parts of **B10**.

> **Scope, honestly.** This is a *lumped* model: one degree of freedom, ideal-gas
> chambers, idealised port blow-down and scavenge (a pressure reset, not a flow
> model). It is the right tool for dynamics, resonance and amplitude. It is **not**
> CFD (scavenging/stratification — OQ-A3), **not** the magnetic circuit
> (OQ-C/FEM), and **not** fatigue (OQ-D). Every input is a *seed*, not a result.

---

## Run it

```bash
pip install -r requirements.txt
python3 run.py                 # full run: text report + plots + CSV in out/
python3 run.py --no-plots      # text + CSV only (no matplotlib needed)

python3 resonance.py           # just the linear resonance design
python3 dynamics.py            # just the nonlinear limit cycle
python3 verify.py              # self-tests -- run before trusting any number
```

Everything you can change lives in [`params.py`](params.py); each field cites the
design chapter or open-question it comes from.

## Files

| file           | what it does |
|----------------|--------------|
| `params.py`    | central parameter set (all SI), with chamber-volume geometry helpers |
| `resonance.py` | linear air-spring resonance (DESIGN ch.14): natural frequency, and the *reversed design* — mass / plenum / boost needed to hit a target frequency |
| `dynamics.py`  | nonlinear time-domain free-piston limit cycle (combustion + ports + air spring + generator load) |
| `run.py`       | runs both, sweeps the generator load into an operating map, writes `out/` |
| `freq_hold.py` | constant-frequency operating line: how mixture + load together hold one frequency while power varies (DESIGN ch.12) |
| `control.py`   | coupled closed-loop PI control (mixture↔power, load↔frequency) under per-cycle ignition scatter — item 22 |
| `valves.py`    | in-piston transfer-valve force budget and inertial opening delay — ch.5 / item 9 |
| `twin.py`      | two-module anti-phase balancing: residual force and rocking couple — ch.15 / item 10 |
| `tradeoff.py`  | mass ↔ frequency ↔ valve ↔ vibration ↔ power, amplitude held constant — items 8/9/10 |
| `thermo.py`    | 0D thermodynamic cycle (real fuel, Wiebe burn, Woschni heat loss) on the limit-cycle kinematics — ch.4 / item 1 |
| `compression.py` | amplitude → effective compression → efficiency: how much efficiency you buy by running closer to the head — ch.4 / item 1 |
| `verify.py`    | self-tests: dt convergence, core physics vs analytic resonance, energy balance |
| `out/`         | generated plots (`limit_cycle.png`, `operating_map.png`) and `operating_map.csv` |

## How far to trust it

`verify.py` checks three things and all pass: the limit cycle does not move with
the time step (spread < 0.03 Hz over an 8× dt range); with combustion and damping
switched off the free oscillation matches the analytic spring/mass resonance to
~1 % (this validates the forces and integrator independently of the combustion
model); and the energy balance closes (indicated = generator + friction, ~3 %
friction). What is **not** guaranteed is the *absolute* frequency — it rides on
the combustion seeds (ignition pressure, indicated efficiency, burn duration), so
read absolute numbers as ±a few Hz until the 0D/1D cycle model (OQ-A1) and a
prototype pin them down. The *trends* (which lever moves f, and by how much) are
robust.

---

## The model in one screen

**One degree of freedom** `x` = displacement of the moving assembly (two pistons
+ rod) from the centre, `+x` toward the right cylinder. Four ideal-gas chambers
act on it:

```
m·ẍ = (p_cL − p_cR)·A_p      combustion: left pushes +x, right pushes −x
    + (p_uR − p_uL)·A_u      under-piston air spring: restoring toward centre
    − c_gen·ẋ                generator load  = the amplitude actuator (ch.12)
    − c_visc·ẋ − f_coul·sgn(ẋ)
```

- **Combustion chambers** compress adiabatically; a Wiebe-style heat release
  fires when the **compression pressure** crosses a threshold (a free piston has
  no fixed TDC — ignition is referenced to compression, which is what makes the
  amplitude self-regulating). Near BDC the exhaust port uncovers and the chamber
  blows down / scavenges to intake pressure.
- **Under-piston chambers** are the pre-compression **air spring** (DESIGN ch.3,
  ch.14): adiabatic, with a one-way intake refill (the partition check valve).
- **Generator** is modelled as linear electromagnetic damping `F = −c_gen·ẋ`;
  the extracted power is `c_gen·⟨ẋ²⟩`. Raising `c_gen` lowers the amplitude —
  this is the amplitude-by-load control of ch.12.

The machine is started in **motor mode** (ch.12 start sequence): from a tiny
seed velocity the generator-as-motor pumps energy (`F = +motor_gain·ẋ`, field
cancelled = no load) and the amplitude grows at the system's own frequency until
compression first reaches ignition pressure; the motor then switches off and the
load engages. This start is **mass-independent** — it finds the same limit cycle
whether the assembly is 0.5 kg or 1 kg (set `motor_gain = 0` for the bare-kick
behaviour instead).

---

## What the seed numbers say today

With the seed in `params.py` (bore 36 mm, stroke 50 mm, 1 kg moving mass, CR 9,
2.5:1 pre-compression, naturally aspirated), two findings stand out — and both are
worth arguing with:

1. **The air spring alone is soft.** Its natural frequency is only ~10 Hz at 1 kg;
   even adding the combustion-compression spring the linear upper bound is
   ~22 Hz. To reach the 30 Hz working estimate (ch.15) on the air spring alone
   you would need an unrealistically light assembly (~0.1 kg), or boost. **The
   combustion-side compression spring, not the under-piston air spring, sets the
   operating frequency.** The nonlinear sim then self-selects **~40 Hz** at the
   default load — higher than the 30 Hz guess, because peak compression (15–30
   bar) stiffens the system.
2. **There is a clean load window.** Generator load `c_gen ≈ 90…160` gives a
   stable limit cycle with amplitude between the head and the firing threshold;
   below it the piston hits the head (runaway), above it the machine dies
   (load exceeds what combustion sustains). The default `c_gen = 150` sits in the
   middle: **~18 mm amplitude, ~40 Hz, ~1.35 kW electrical, ~16 bar peak** — and
   a vibration force around **1.4 kN** (higher than the 890 N of ch.15, because
   of the higher frequency). See `out/operating_map.png`.

These are seed-driven, not gospel. Change the bore, stroke, mass, compression
ratio or pre-compression in `params.py` and re-run — that is the whole point.

### Reaching a higher frequency (e.g. 50 Hz)

Frequency rises as `1/√m` and with spring stiffness, so 50 Hz is reachable from
the default by more than one route (all confirmed in the sim):

| route | change | f | amplitude | P_elec | peak | vib. force |
|-------|--------|---|-----------|--------|------|------------|
| lighter assembly | m ≈ 0.50 kg | ~52 Hz | 18 mm | ~1.7 kW | 13 bar | ~1.15 kN |
| shorter stroke   | S ≈ 35 mm   | ~49 Hz | 14 mm | ~1.25 kW | 21 bar | ~1.64 kN |
| combination      | m 0.65 kg + CR 11 | ~49 Hz | 17.5 mm | ~1.65 kW | 15 bar | ~1.28 kN |

The cleanest lever is **reducing the moving mass** — it lifts frequency, keeps
power up and pressure modest, and is the direction the design already pushes
(tubular rod, teeth instead of magnets). The unavoidable cost of higher
frequency is **higher vibration force** (`F = m·ω²·X` grows with ω²) — an
argument for the two-module anti-phase arrangement (DESIGN ch.15).

### Holding the frequency constant (mixture + load) — `freq_hold.py`

The frequency drifts with load on its own, but **mixture is a second actuator**:
richer charge returns energy, restoring amplitude / compression / frequency
while the extra energy leaves as power. Load carries the power change, mixture
trims the frequency back. The two together hold **one operating point** — see
`out/constant_freq_line.png`:

| gen load | fuel (mixture) | frequency | amplitude | P_elec | peak pressure |
|----------|----------------|-----------|-----------|--------|---------------|
| 110 | 4.09 bar | 40.0 Hz | 19.6 mm | 1160 W | 16.4 bar |
| 150 | 5.03 bar | 40.0 Hz | 18.2 mm | 1372 W | 16.8 bar |
| 210 | 6.44 bar | 40.0 Hz | 17.0 mm | 1681 W | 18.7 bar |

Power varies 1.2 → 1.7 kW at a flat 40 Hz and a **near-constant peak pressure** —
so the peak mechanical/thermal load is the same regardless of output, which is a
gift for the 10⁹-cycle fatigue target. This is exactly the multi-loop control of
ch.12 (load/excitation = fast power actuator, mixture = frequency trim). The
authority is bounded, though: richening past stoichiometric stops adding energy,
and the lean-stratified, knock-free philosophy (ch.4) limits the rich headroom.

### Three more studies

- **`control.py` (item 22)** — closes the two loops above with PI controllers and
  injects 6 % per-firing **ignition scatter**, then steps the power demand
  (1.2 → 1.55 → 1.3 kW). Power tracks the demand and the frequency stays at
  40 Hz (±~0.6 Hz). So the "one operating point" survives realistic combustion
  variability — at least in 0D. See `out/control_loop.png`.
- **`valves.py` (ch.5 / item 9)** — the transfer-valve force budget for a **stock
  25 g motorcycle exhaust valve** with a **1 N seat spring** (the spring only
  seats it; the gas dynamics do the work). Combustion **slams the valve shut**
  (~300 N closing = the backfire check valve, ch.20). At ~2.5:1 pre-compression
  the opening pressure (~32 N) and inertia (~35 N) are comparable — exactly the
  design's claim (ch.5) — and the valve **opens ~36° after BDC**: the
  exhaust-first, transfer-second asymmetric timing, for free. Pre-compression is
  the tuning knob: more of it opens the valve earlier (less delay); ~2.5:1 keeps
  a useful delay. **No special lightweight part needed.**
- **`twin.py` (ch.15 / item 10)** — anti-phase twin. The net shaking **force**
  cancels strongly (1387 N → 162 N, −88 %, because the cycle is odd-harmonic
  dominated and a half-period shift kills odd harmonics). The catch is the
  **rocking couple** (~165 N·m at 120 mm spacing) that does *not* cancel —
  that, not the force, is what the mounts carry. Shrink it by stacking the
  modules coaxially. See `out/twin_balance.png`.

### Mass vs frequency vs valve vs vibration: `tradeoff.py`

Putting the chain together — moving mass sets frequency (`f ∝ 1/√m`), and
frequency drives both the valve inertia and the vibration. Holding amplitude at
18 mm and sweeping the mass, with the stock 25 g valve and 1 N seat spring
(`out/tradeoff.png`):

| mass | frequency | heaviest workable valve | vibration | power |
|------|-----------|--------------------------|-----------|-------|
| 0.45 kg | 55 Hz | 13 g | 1126 N | 1781 W |
| 0.55 kg | 51 Hz | 21 g | 1172 N | 1662 W |
| 0.70 kg | 46 Hz | ≥60 g | 1240 N | 1537 W |
| 1.00 kg | 40 Hz | ≥60 g | 1360 N | 1338 W |
| 1.30 kg | 35 Hz | ≥60 g | 1464 N | 1206 W |

Two things fall out. First, **vibration force does *not* improve with heavier
mass** — at fixed amplitude the shaker force tracks the (roughly constant)
combustion force, so it is flat-to-rising; lighter mass is actually better for
both vibration *and* power. Second, the **stock 25 g valve transfers comfortably
from ~0.7 kg (46 Hz) upward** (huge margin at the ~40 Hz / 1 kg operating point);
only at the aggressive light-mass, >50 Hz corner does it tighten. So the valve is
*not* the binding constraint — pre-compression sets its inertial delay
independently of mass. The remaining real cost of higher frequency is the
vibration force / rocking couple, handled by the anti-phase twin (ch.15).

### The thermodynamic floor: `thermo.py`

The dynamics drives combustion from a *seed* BMEP (5 bar) and efficiency (38 %).
`thermo.py` is the layer underneath — a real 0D closed cycle on the limit-cycle
kinematics, with actual fuel (LHV, air-fuel ratio, equivalence ratio φ), a Wiebe
burn, Woschni wall heat transfer, a temperature-dependent `cv`, and a residual
(internal-EGR) fraction. At φ = 0.8 (lean):

| quantity | 0D cycle | dynamics seed |
|----------|----------|---------------|
| IMEP | 5.8 bar | 5.0 bar |
| peak pressure | 22 bar | 16 bar |
| peak temperature | 2424 K | — |
| thermal efficiency | **26 %** | 38 % |
| indicated power | 2.3 kW | ~1.5 kW |

Three findings. (1) **The seed BMEP was about right** — 5.8 vs 5.0 bar — so the
power estimates stand. (2) **Efficiency is ~26 %, not 38 %**: the exhaust port
opens early (expansion cut short) and — the real surprise — the **effective
compression ratio is only ~3.5, not the geometric 9**, because the piston
reverses at ~18 mm instead of reaching the head. **Amplitude (running closer to
the head) is the main efficiency lever**, and it ties straight back to the
generator-load setpoint. (3) Real peak pressure ~22 bar (vs 16) means the
combustion spring is a little stiffer, so the true frequency sits slightly above
40 Hz. φ sets power monotonically; lean ~0.8 (peak T ~2400 K, low NOx) is a sane
operating point. See `out/thermo_cycle.png` for the P–V loop. Still 0D — no
chemistry or stratification (peak T is an upper bound; that is OQ-A3/CFD).

### Efficiency is an amplitude setpoint: `compression.py`

Following the effective-compression thread: tune the generator load to run at
different amplitudes (closer to the head), and run the 0D cycle at each
(`out/compression.png`):

| amplitude | head clearance | effective CR | efficiency | peak pressure |
|-----------|----------------|--------------|------------|---------------|
| 17 mm | 8 mm | 3.2 | 25 % | 20 bar |
| 21 mm | 4 mm | 4.5 | 30 % | 25 bar |
| 23 mm | 2 mm | 5.6 | **33 %** | 29 bar |

Running from 17 → 23 mm lifts the effective compression 3.2 → 5.6 and thermal
efficiency by **~8 points (25 → 33 %)**, at the cost of peak pressure (20 → 29
bar). So **efficiency is largely an amplitude-setpoint decision (ch.12 generator
load), not just a geometry decision (ch.4)**. The control loop should hold the
amplitude as close to the head as the squish clearance and a peak-pressure limit
allow — which is also exactly what the full-area squish of ch.4 wants (piston
nearly kissing the deck). It ties back to the runaway/headroom window in
`run.py`: the most efficient operating point sits just below head contact.

★ Viva La Resistánce ★
