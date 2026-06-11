# Changelog

Všechny podstatné změny projektu NIC-FPLG. / All notable changes to NIC-FPLG.

---

## v0.5 — 2026-06-11

První verze opřená o čísla, ne jen o úvahu. Přibyl [`calc/`](calc/) — odlehčená
0D sada modelů (dynamika volného pístu + termodynamický cyklus + řízení) — a její
výsledky jsou propsané do `DESIGN-FPLG` a `OPEN-QUESTIONS` (EN/CS/RU).

**Co model říká**
- **Pracovní bod ~40 Hz** drží regulační smyčky směs + zátěž generátoru, ne
  geometrie sama; frekvenci lze udržet konstantní napříč výkonem (1,2–1,7 kW el.)
  i při rozptylu zápalů.
- **Stock motorkový výfukový ventil (25 g) funguje** — pružinka ~1 N a
  předkomprese ~2,5:1 ho otevřou ~36° za úvratí. Žádný speciální díl, nic se nevyrábí.
- **Účinnost (~26–33 %) je otázka amplitudy**, ne jen geometrie: blíž k hlavě =
  vyšší efektivní komprese a účinnost (za cenu špičkového tlaku).
- Vibrace ~1,4 kN; anti-fázový dvojmodul vyruší sílu ~88 %, zbývá klopný moment ~165 N·m.

**Ověřeno** — self-testy (`calc/verify.py`): konvergence kroku, jádro proti
analytické rezonanci (~1 %), uzavřená energetická bilance.

**Rozsah** — 0D: dynamika, rezonance, řízení, ventily, vibrace, cyklus.
Nepokrývá CFD vyplachování/stratifikaci (OQ-A3).

**Další (v0.x)** — model říká, že není co speciálního vyrábět (stock ventil,
sériová periferie), takže dalším milníkem není výkres, ale **prototyp a fyzické
měření**, které ověří tahle 0D čísla; pak 1D vyplach / CFD.

<details>
<summary>English</summary>

First release where the concept rests on numbers, not just reasoning. Adds
[`calc/`](calc/) — a dependency-light 0D model suite (free-piston dynamics +
thermodynamic cycle + control) — with results folded into `DESIGN-FPLG` and
`OPEN-QUESTIONS` (EN/CS/RU).

- The **~40 Hz operating point** is held by the mixture + generator-load loops,
  not geometry alone, and stays constant across power (1.2–1.7 kW elec) under
  ignition scatter.
- A **stock 25 g motorcycle exhaust valve works** with a ~1 N seat spring and
  ~2.5:1 pre-compression (opens ~36° after BDC). No custom part to manufacture.
- **Efficiency (~26–33 %) is an amplitude setpoint**, not just geometry.
- Vibration ~1.4 kN; the anti-phase twin cancels ~88 % of the force, leaving a
  ~165 N·m rocking couple.

Verified: self-tests pass (dt convergence, analytic resonance to ~1 %, energy
balance). Scope: 0D — scavenging/stratification CFD (A3) and a prototype are next.

</details>

★ Viva La Resistánce ★
