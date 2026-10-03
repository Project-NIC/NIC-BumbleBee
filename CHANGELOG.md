# Changelog

*[English](CHANGELOG.md) · [Čeština](CHANGELOG_cs.md) · [Русский](CHANGELOG_ru.md)*

All notable changes to NIC-FPLG.

---

## v0.5 — 2026-06-11

First release where NIC-FPLG rests on numbers, not just reasoning. Adds
[`calc/`](calc/) — a 0D model suite (free-piston dynamics + thermodynamic cycle +
control) — with results folded into `DESIGN-FPLG` and `OPEN-QUESTIONS` (EN/CS/RU).

**What the model showed**
- The **~40 Hz operating point** is held by the mixture + generator-load loops,
  not geometry alone, and stays constant across power (1.2–1.7 kW elec) under
  ignition scatter.
- A **stock 25 g motorcycle exhaust valve works** with a ~1 N seat spring and
  ~2.5:1 pre-compression (opens ~36° after BDC). No custom part to manufacture.
- **Efficiency (~26–33 %) is an amplitude setpoint**, not just geometry — closer
  to the head means higher compression and efficiency.
- Vibration ~1.4 kN; the anti-phase twin cancels ~88 % of the force, leaving a
  ~165 N·m rocking couple.

**Trust** — self-tests pass (`calc/verify.py`): dt convergence, core vs analytic
resonance (~1 %), energy balance. It is **0D** — scavenging/stratification CFD
(OQ-A3) is next.

**Next** — the model says there is no special part to manufacture, so the next
milestone is not a drawing but a **prototype and physical measurement** to check
these 0D numbers.

---
