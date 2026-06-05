# NIC-FPLG — Technical Concept Description

*Two-stroke two-cylinder linear engine with an integrated linear generator.*
*Status: concept. Values marked (TBD) are waiting on simulation or calculation — see [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md).*

---

## Summary

Two-stroke linear engine without a crankshaft. Two pistons share a single rod;
a tubular linear generator sits at the rod's centre. The engine runs permanently
at one operating point in mechanical resonance — frequency is set by the physical
system, not by control electronics. System power is changed by the battery
charge current, not by RPM or throttling.

The key idea: functions that a conventional engine solves with moving parts are
handled here by geometry. Drop-shaped pockets in the piston face direct flow and
spin the charge without a camshaft. Valve inertia creates asymmetric timing
without membranes. The pre-compression air spring replaces a flywheel. The machine
is designed to survive limit conditions — not to avoid them.

Target output ~3 kW mechanical, 1–1.5 kW electrical, service life 10,000 hours.
Applications: stationary generator, range extender, drones, light vehicles with
a backbone tube. The full technical architecture is described in the chapters
below; open questions and falsification scenarios in [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md).

---

## 1. Design Philosophy

Five principles that repeat in every detail of the machine:

1. **Geometry does the work.** Functions that a conventional engine solves with
   valvetrain, electronics, or calibration maps are handled here by shape:
   pressure-controlled valves, drop-shaped nozzles in the piston face,
   inertia-delayed transfer timing, piston rotation from pocket offset.
   What has no actuator and no software cannot break.
2. **Robust rather than fragile.** The machine does not avoid limit conditions —
   it survives them. The steel integral sleeve and piston tolerate detonation
   and piston-to-head contact. The spark plug is recessed below the deck;
   the in-piston valves act as backfire check valves.
3. **One operating point.** Constant frequency, constant load ~50 % of maximum.
   No maps, no transient states; the battery absorbs everything variable.
4. **Wrought material.** Grain follows shape: cold-extruded sleeve (cartridge
   technology), die-forged piston, rolled threads, rolled bar stock. Fatigue
   at 10⁹ cycles is the primary enemy — metal forming is the primary weapon.
5. **Service built into the design.** Decarbonisation ports without disassembly,
   generator as a replaceable cartridge, off-the-shelf peripheral parts
   (valves, spark plugs, throttle body, ignition module) — serviceable from
   a breaker's yard.

---

## 2. Overall Architecture

```
      spark plug                                              spark plug
           ↓                                                        ↓
   ┌───────┴──────┐  ┌──────┐  ┌─────────────┐  ┌──────┐  ┌───────┴──────┐
   │  SLEEVE L    │  │PARTI-│  │  GENERATOR  │  │PARTI-│  │   SLEEVE R   │
   │  [PISTON L]==│==│=TION=│==│=====ROD=====│==│=TION=│==│==[PISTON R]  │
   │    valves    │  │bush  │  │ teeth+stator│  │bush  │  │    valves    │
   └───────┬──────┘  └──┬───┘  └─────────────┘  └──┬───┘  └───────┬──────┘
     exhaust         intake      ↑ intake        intake          exhaust
     ports (ring)    valve   (through gen.)      valve          ports (ring)
```

- **Two pistons on one rod** — they move together (this is not a boxer).
  Combustion on one side = compression on the other + pre-compression
  under both pistons.
- **Rod** = austenitic stainless steel tube (non-magnetic), carrying laminated
  generator teeth at the centre, screwed end caps with spherical-segment
  piston joints at the ends.
- **Body** = two-piece aluminium casting; forms the pre-compression chamber
  partitions, carries the rod bushings and the generator stator. Aluminium
  serves primarily as a heat sink — structural strength comes from the steel
  sleeves press-fitted inside.
- **Sleeves** ("integral sleeve", colloquially "cartridge head") = head +
  cylinder in one piece, cartridge shape: flange (≥8 bolts to body), barrel,
  tapered neck with spark plug thread. Each sleeve surrounded by a ring
  stainless exhaust manifold, everything cast into the aluminium.

**Charge flow (one-way highway):** throttle body → generator space (mixture
cools coils and magnets, oil mist lubricates bushings) → large intake valve
in partition → pre-compression chamber below piston (turbulence, piston crown
cooling, homogenisation with lubricant) → transfer valves in piston →
drop-shaped pockets → combustion space → combustion → ring exhaust ports →
Y junction → silencer. The charge never doubles back; every cubic centimetre
of air does four jobs on the way (cooling, lubrication, pre-compression, combustion).

**Applications:** stationary generator / range extender (primary target), drones
and aviation (heavy fuel, ~100 V bus), light vehicles with engine in a central
backbone tube (electric wheel drive, multiple modules in anti-phase = balance +
power scaling). Concept pays off up to ~40 kW per module; above that, conventional
rotary machinery is better.

**Safety built into the architecture:** in-piston valves are one-way — backfire
from above closes them, flame cannot reach the charge space and generator.
Partition intake valve is a second check barrier. Generator windings are
vacuum-impregnated (class H); no sparking parts inside. Cross-wired GPIO shutdown
of both ECUs ensures generator fault stops the engine and a misfire unloads
the amplitude without a hard crash. Robustness to detonation and piston travel
is intentional — the steel sleeve and recessed plug are there for exactly that.

---

## 3. Working Cycle and Charge Exchange

Two-stroke without transfer ports in the cylinder wall — transfer goes **through
the piston**.

1. **Expansion L / Compression R.** Combustion on the left drives the rod right.
   Right piston compresses its charge; both pistons simultaneously pre-compress
   fresh mixture below them (target ~1:2, partition intake valves closed).
2. **Exhaust L.** Left piston uncovers the ring exhaust ports; burnt gas leaves
   around the full circumference into the ring manifold. Upper edge of ports =
   the only fixed timing in the machine (TBD — tuned by milling the edge upward).
3. **Transfer L.** When pressure below the piston overcomes pressure above +
   spring force + inertia force, the in-piston valves open. Valve inertia
   (comparable in magnitude to the pressure force — see ch. 5) **delays opening
   past BDC** → exhaust first, transfer second = asymmetric timing for free,
   no membranes, no power valves.
4. **Internal EGR.** A portion of hot exhaust gas is retained intentionally:
   it is inert (no oxygen), flash-evaporates fuel, dilutes the charge at the
   wall, reduces combustion temperature (NOx) and HC slip.
5. Rod returns — roles swap. Synchronisation is held by physics: a stronger
   combustion on one side raises compression (and therefore combustion
   intensity) on the other; fine amplitude control is handled by generator
   load (ch. 12).

---

## 4. Combustion Chamber

- **Flat sleeve crown against flat piston face**, clearance at TDC ~1 mm (TBD)
  → **full-area squish**: charge is pushed from the wall into the centre,
  creating turbulence; no end-gas pocket prone to detonation at the wall.
- **Spark plug recess** in the tapered neck of the sleeve; reduced-reach racing
  plug, electrode 0.1 mm below the deck → piston travel to head does not
  damage the plug.
- **Drop-shaped pockets in the piston face** (ch. 5) hold the bulk of the rich
  charge under the plug → **stratified charge**: rich near the plug, lean and
  inert (exhaust gas) at the wall. Wall = location of exhaust ports → burnt
  gas leaves preferentially, not fresh charge.
- **Combustion sequence:** ignition in plug recess → flame flashes into pockets
  → progressive, slow burn controlled by geometry; pocket offset spins the
  charge (and by reaction, the piston). Intentionally **no detonation** —
  slow progressive burn, not shock combustion.

---

## 5. Piston, Valves, Drop-Shaped Nozzles

**Piston:** steel of the same grade as the sleeve (matched thermal expansion →
constant clearance at all temperatures → simpler rings, consistent seal).
Die forging (grain follows shape; prototype machined from rolled bar). Three
piston rings — softer material, large cross-section, **radiused edges**;
pre-compression pressure from below forces mixture and oil between the rings →
continuous lubricant circulation through the ring pack.

**Transfer valves:** 2× exhaust valve from a racing motorcycle, ⌀ ~16 mm,
thin stem ~4 mm, heat-resistant alloy. Here they run in a "cold" role —
washed by fresh mixture from below, with enormous reserve. Assembly:

- guides (bushings) pressed from the rear into the piston,
- **conical (tapered) spring** — progressive rate, compresses fully flat
  (minimum stack height), no sharp natural frequency → immune to surge
  in a continuously oscillating environment,
- standard cap and collets from automotive valvetrain.

**Valve force budget (working figures, TBD):** inertia force on valve ~25 g
at ~890 m/s² ≈ 22 N; opening pressure force ≈ 20 N per 1 bar differential
across ⌀16 disc. Forces are of **comparable magnitude** → spring is designed
against the sum (pressure − spring − inertia) and inertia intentionally
creates delayed opening (ch. 3). Every gram of valve mass shifts the balance
by ~0.9 N.

**Drop-shaped pockets (nozzles):** around each valve in the piston face, a
drop-shaped recess 2–3 mm deep. At the semicircular (wide) end only ~0.1 mm
clearance between the disc and the wall; toward the tip the profile opens.
**The valve disc is a moving part of the nozzle:** disc lift controls *flow
rate*, the pocket controls *direction* — the jet points at the tip regardless
of instantaneous lift. Two pockets opposing each other, tips offset from centre:

- main charge jet aims at the centre under the plug (stratification),
- offset gives the charge rotation → combustion rotates → reaction torque
  rotates the piston a small angle each cycle → **even wear** of rings, guides,
  and thermal loading. Left and right pistons are mirror images.

Pocket machining: piston face is accessible → standard 3-axis milling with a
ball-end cutter.

---

## 6. Spherical-Segment Joint (Piston–Rod Connection)

Joint = spherical segment ⌀ ~15 mm with ~15° curvature — just two curved
faces against each other. Properties:

- large contact area → **impact resistance** (combustion forces go through
  compression, not shear),
- allows **piston tilt** relative to the rod (piston self-aligns in the cylinder,
  system is statically determinate — see ch. 8, "self-alignment"),
- **slip during piston rotation is slow** (resultant piston RPM of order
  units/min) → boundary lubrication regime,
- both surfaces nitrided with micro-grooves; grooves fill with mixture and oil
  before each transfer stroke → self-lubricating plain bearing (cam–follower
  analogy; conditions here are more favourable).

---

## 7. Rod and Joints

**Rod:** austenitic stainless steel tube (304/316 — condition: non-magnetic;
watch for strain-induced martensite in drawn tubes, resolved by annealing).

- tubular section = best stiffness-to-mass ratio → light moving assembly,
- stainless = low thermal conductivity → rod does not conduct heat from pistons
  into generator,
- non-magnetic → magnetic flux flows exclusively through the laminated teeth.

**End caps with joints:** screwed. Key details for 10⁹ cycles:

- **left-hand and right-hand threads oriented against the piston rotation
  direction** → the piston's own rotation continuously tightens both joints
  (free locking),
- **abutment face** — the compressive half-cycle goes face-to-face, the thread
  never sees it,
- **preload above maximum working tensile load** — joint never opens in service,
  threads carry only static preload (connecting-rod bolt principle),
- **rolled fine thread** (not cut) — work-hardened surface, compressive
  residual stress, 3–5× fatigue life,
- radii on all transitions, thread runouts without sharp undercuts,
- high-temperature anaerobic adhesive as secondary lock,
- series: die-forged end caps (grain follows joint shape); prototype: rolled
  bar stock (longitudinal grain suitable for axial loading).

Note: thread engagement beyond ~1.5×⌀ no longer helps (first thread carries
30–40 % of the load); preload and face contact decide, not length.

---

## 8. Linear Generator

**Topology: tubular flux-switching machine with hybrid excitation.**

- **Magnets and coils both in the stator** — between pole pieces assembled
  from 0.3 mm laminations. The moving part (rod) carries only passive
  ferromagnetic teeth → minimum moving mass, magnets in the cooled zone.
- **Rod teeth:** 0.3 mm laminations pressed onto an insulating spacer ring
  on the enlarged tube section, potted in epoxy. Lamination = suppression of
  eddy currents (flux in teeth switches direction). Note: epoxy rated ≥150 °C
  (motor-grade systems); spacer ring from a creep-resistant material
  (PEEK / filled PA) — permanently loaded press-fit for 10,000 h.
- **Tubular arrangement:** radial magnetic forces cancel by symmetry (rod
  "floats" in the magnetic centre, bushings carry minimal load) and teeth are
  rotationally symmetric rings → **the only topology compatible with rod
  rotation**. Piston rotation (ch. 5) and machine topology are mutually
  dependent.
- **Double tooth count** → double electrical frequency (target ~100 Hz) →
  half the flux for the same voltage (e = N·dΦ/dt) → two coils in the space
  of one → simpler rectification. Cost: iron losses increase with frequency —
  acceptable at 0.3 mm laminations.
- **Hybrid excitation ~50 % PM / 50 % field winding:** flux can be boosted,
  reduced, or cancelled. ⚠ **Demagnetisation:** field flux must be routed
  along a parallel path in iron **around** the magnets, not through them
  against polarisation (especially when hot). High-coercivity magnets
  (NdFeB grade SH/UH, or SmCo). Magnetic circuit detail = critical design
  point (TBD, FEM).
- **Bushings** (plain bearings in partitions): rigid rod guidance (sag from
  tooth mass), length ~20 mm, clearance 0.05–0.1 mm → **labyrinth seal**
  (flow ~ clearance³): pre-compression leakage a few percent, returns to
  intake. Same material as rod (constant clearance with temperature) + hard
  coating. **Bushings also centre the stator** — rod↔stator concentricity
  (air gap!) guaranteed by a single part, not a chain of tolerances.
- **Assembly / service:** rod → stator → two body halves with bushings slide
  into the stator and bolt together. Generator = **sealed-for-life cartridge**;
  after wear (target 10,000 h) replace as a unit.

---

## 9. Exhaust System

- **Ring manifold** around each sleeve (Q-shape with outlet), full stainless
  steel — heat should leave with the exhaust gas, not be distributed into
  the engine.
- **Variable wall thickness (fabricated):** ~1 mm on the side facing the
  compression chamber (narrow thermal bridge along the wall), ~3 mm on the
  side cast into aluminium (resistance to heat transfer into the heat sink +
  stiffness against collapse under casting pressure; circular section with
  3 mm wall withstands casting pressures with margin).
- **Exhaust ports: drilled through** (aluminium + both tube walls + sleeve),
  10–20 circular holes around the circumference perpendicular to the axis.
  Circular hole = no stress concentrations; port edges **chamfered and
  polished from inside** (ring protection), bore the cylinder after this
  operation. Port-to-bridge ratio so that the ring always has adequate
  seating area (TBD).
- **Decarbonisation ports:** the opposite holes from drilling get a thread +
  screw with a copper sealing washer (anti-seize compound). Unscrew →
  brush through the port axis → re-screw. Cleaning without disassembly;
  essential for real service life in a two-stroke.
- **Y junction** of both rings into one silencer. Exhaust pulses alternate
  (pistons on a shared rod) → flow from one branch may create ejector-effect
  sub-pressure in the other branch and assist its scavenging. Effect depends
  on branch lengths vs. speed of sound in exhaust gas (~500–600 m/s) —
  **TBD, 1D simulation / experiment**; tuneable by pipe length.
- **"Open" exhaust:** total volume ~10× swept volume + dissipative silencer
  (~0.5 l, perforated baffles) → minimal back-pressure, no resonant waves.
  A conventional two-stroke needs an expansion chamber to return escaped
  charge — here charge does not escape (stratification, ch. 4), so a tuned
  pipe is not needed.
- **Port timing tuning:** drill first sleeve ports intentionally **low** (late
  exhaust, long expansion) and move the upper edge upward by milling until
  scavenging is right. One-directional tuning without destroyed sleeves.

---

## 10. Body, Cooling, Casting

- **Aluminium body** with longitudinal fins; fin slots against "banana effect"
  (thermal warping). Aluminium = heat sink; minimum material, strength from
  steel inserts. Bosses in the exhaust zone.
- **Insert casting (squeeze casting / liquid forging):** sleeve + exhaust
  manifold are cast/pressed in with molten aluminium in a die. Aluminium
  shrinks more than steel/stainless on cooling → permanent **shrink fit** =
  perfect thermal contact and mechanical retention without fasteners.
  - sleeve supported by a **mandrel** with ceramic release agent during casting,
  - tube keeps shape by wall thickness (3 mm on pressure side); alternative:
    salt core washed out with water,
  - **bore the cylinder only AFTER casting** (shrink fit changes geometry).
- **Air cooling:** fins = heat sink; intake mixture cools the generator from
  inside (fuel evaporation adds). Forced airflow by application: propeller
  (aviation), temperature-controlled electric fans (vehicle/stationary);
  waste heat to fins in the order of 2–4 kW at full power (TBD).

---

## 11. Fuel System — Multi-Fuel

- **Port injection** downstream of throttle body, into the turbulence zone
  (better atomisation). Throttle body and injector = off-the-shelf parts from
  a ~150 cc motorcycle (large flow reserve).
- **Separate lubricant injection:** pulsed metering pump (Webasto type);
  ester ("eco/bio") oil diluted with petrol (winter viscosity, injector
  passage). Dose controllable by load. **Essential for LPG** — dry gas does
  not lubricate; oil mist in intake simultaneously lubricates bushings, joints,
  and ring pack.
- **Fuels:** petrol; LPG (propane–butane); diesel+petrol with spark ignition
  ("heavy fuel" — used in military drone engines; petrol dilution improves
  evaporation and ignitability). Alcohol fuels excluded (low volumetric
  energy density).
- **One operating point = one row of parameters per fuel** (advance, mixture,
  oil dose) instead of a full map. Fuel switching is changing three numbers.

---

## 12. Electronics and Control

**Architecture: 2 processors** (STM32H503 — 250 MHz Cortex-M33, HW timers
with dead-time): engine ECU + generator ECU. Status communication +
**safety signals on dedicated GPIO** (hardwired, µs latency, no protocol).

**Cross-protection:**

- generator fault (overcurrent…) → GPIO → engine: close throttle + kill
  ignition; rod coasts down safely,
- misfire → GPIO → generator: **immediately shed load** → rod retains energy
  for the next compression → *recovery cycle* (2–3 ignition attempts), hard
  stop only after that.

**Position sensing — three independent sources of truth:**

1. 4× high-frequency inductive sensors through the sleeve (encapsulated,
   pressure-rated), sensing pistons **cross-wise** → position, velocity,
   direction + mutual redundancy,
2. generator coil voltage profile (position "for free"),
3. knock sensor on body (detonation + independent misfire detection).

**Ignition:** off-the-shelf dual-channel module (e.g. Renault D4F740),
**two independent channels — NO wasted spark:** the opposing cylinder has
open exhaust ports and fresh charge at the moment of firing; a shared spark
risks backfire. Phase information from sensors is available; each plug fires
on its own signal. Fixed advance + temperature correction (one operating point).

**Mixture:** wide-band lambda (LSU 4.9) for tuning, switching-type for
operation; no catalyst. MAP sensors before/after throttle, temperatures.

**Start sequence:**

1. full over-excitation (up to ~200 %) → generator in motor mode oscillates the rod,
2. first ignitions on minimum mixture,
3. briefly cancel field with reverse current → zero electromagnetic load,
   oscillation settles "pressure-on-pressure" on lean mixture (keep this
   phase short — without electromagnetic braking only the air spring controls
   amplitude),
4. gradual re-excitation = smooth load and mixture ramp to operating point.

**Amplitude control:** dead-centre position is set by energy balance, not
geometry. Main actuator = **generator load/excitation** (electromagnetic
brake, ms response). Three independent loops: mixture (slow), excitation
(fast), advance (corrective).

---

## 13. Electrical Output

- 2 coils → rectification with **2 MOSFETs** synchronously controlled; driver
  with **hardware dead-time** (STM32H5 timers have it built in) — shoot-through
  must not depend on software.
- **Capacitor bank between rectifier and BMS** (order of thousands of µF):
  BMS FETs and shunts are built for smooth DC; 100 Hz pulses without smoothing
  increase RMS heating and can trip overcurrent protection falsely.
- BMS → traction battery. **Battery = buffer and regulator:** charge current
  is continuously controllable; system power changes here, engine runs
  unchanged. Target ~100 V DC bus, ~15 A at 1.5 kW.

---

## 14. Resonant Operation

Pre-compression below the pistons forms an **air spring**; spring + moving
assembly mass = resonator:

```
f = (1/2π)·√(k/m)
m … mass of moving assembly (pistons + rod + teeth + end caps)
k … air spring stiffness (volume below pistons, pre-compression ratio, piston area)
```

The design procedure is **reversed**: choose the optimal combustion frequency →
weigh the assembly → **calculate the volume below the pistons** so that
resonance falls on the chosen frequency. Operating in resonance = the air spring
returns reversal energy for free, the generator takes only useful work.
(Correction: bushing leakage slightly reduces effective stiffness — include it.)
Specific numbers TBD — first task for `calc/`.

---

## 15. Vibration and Mounting

Both pistons move together → the moving mass oscillates with no inherent balance.
Working estimate: m ≈ 1 kg, stroke 50 mm, 30 Hz → F ≈ 890 N @ 30 Hz (TBD).

- stationary use: massive frame + anti-vibration mounts tuned well below the
  operating frequency (standard compressor practice),
- light rod (tube, teeth instead of magnets) reduces the problem at the source,
- **modular solution:** two machines side-by-side in anti-phase = perfect
  balance + double power (natural for a backbone tube, ch. 17).

---

## 16. Materials and Thermal Management

| Part                 | Material                   | Reason                                        |
|----------------------|----------------------------|-----------------------------------------------|
| Sleeve + piston      | steel, same grade          | matched expansion → constant clearance        |
| Rod                  | austenitic stainless, tube | non-magnetic, thermally isolating, light      |
| Exhaust manifold     | stainless, 1/3 mm wall     | low λ; heat leaves with exhaust gas           |
| Body                 | aluminium, finned          | heat sink; shrink-fit grip on inserts         |
| Gen. teeth + stator  | electrical sheet 0.3 mm    | eddy-current suppression                      |
| Magnets              | NdFeB SH/UH or SmCo        | coercivity (field cancellation, temperature)  |
| Joints, bushings     | steel + nitriding/coating  | boundary lubrication, impact, const. clearance|
| Valves               | heat-resistant alloy (moto)| enormous reserve in their "cold" role         |

Thermal flow principle: **combustion heat → aluminium → air; exhaust heat →
exhaust gas → out.** Stainless everywhere heat must not cross (manifold, rod);
wall thickness as controlled thermal resistance (ch. 9).

---

## 17. Manufacturing

**Prototype (no tooling, feasible in EU/CZ):** sleeve turned + honed (after
assembly), piston CNC from rolled bar, manifold fabricated, body machined
from billet + conventional shrink-fit, laminations laser-cut (anneal edges
for final version), rod from catalogue tube, peripheral parts off the shelf.

**Series:** sleeve by cold back-extrusion (cartridge technology — grain follows
shape), piston die forging ("3D" die, minimal machining; thin membranes
between cavities simply milled through), aluminium squeeze casting around
inserts (mandrel + ceramic release; cooling takes seconds), rolled threads.
Tooling (dies, moulds, fixtures) — realistically Asia.

---

## 18. Service and Service Life

Target **10,000 h ≈ 10⁹ cycles** → fatigue-driven design (preload, rolling,
radii, wrought grain, conical springs without surge).

- exhaust port decarbonisation: screw ports, ~10 minutes, no disassembly,
- generator module: sealed-for-life cartridge, replace as a unit,
- peripherals (plugs, valves, rings, injector, throttle body): off-the-shelf
  parts,
- in-service diagnostics: 3 position sources, lambda, knock, pressures, temperatures.

---

## 19. Applications

*Overview in ch. 2 (Overall Architecture). Details below.*

- **Stationary generator / range extender** — primary target (1–1.5 kW electrical),
- **drones / aviation** — heavy fuel, propeller airflow, ~100 V bus,
- **light vehicles:** engine in a **central backbone tube** (Tatra concept but
  without driveshafts — only cables exit): best-protected location, mass low
  and centred, longitudinal vibration absorbed by vehicle mass; multiple modules
  in anti-phase = balance + power scaling; intake from above, cooling air
  exhausted downward (reduced thermal signature of hull),
- series hybrid: generator covers **average** demand, battery covers **peaks** —
  ~40 kW module × N.

---

## 20. Safety Built into the Design

*Overview in ch. 2 (Overall Architecture). Details below.*

- in-piston valves = **check valves**: backfire from above closes them →
  flame cannot reach charge space and generator (a conventional two-stroke
  has no such protection),
- partition intake valve = second check barrier,
- windings: vacuum-impregnated, class H — fuel mist is present in the
  generator space; no sparking parts inside (no commutator, MOSFETs external),
- robustness to limit conditions: detonation, piston travel, amplitude runaway —
  steel sleeve, recessed plug, massive joints,
- cross-wired GPIO shutdown of both units, misfire recovery cycle,
- hardware dead-time in the power stage.

---

*This document is live — each chapter will be refined as simulations and
prototype tests produce results. Specific objections welcome in Issues.*

★ Viva La Resistánce ★
