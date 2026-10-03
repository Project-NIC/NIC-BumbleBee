# Seznam změn

*[English](CHANGELOG.md) · [Čeština](CHANGELOG_cs.md) · [Русский](CHANGELOG_ru.md)*

*Závazná je anglická verze.*

Všechny podstatné změny NIC-FPLG.

---

## v0.5 — 2026-06-11

První vydání, ve kterém NIC-FPLG stojí na číslech, nejen na úvahách. Přidává
[`calc/`](calc/) — sadu 0D modelů (dynamika volného pístu + termodynamický cyklus +
řízení) — s výsledky zapracovanými do `DESIGN-FPLG` a `OPEN-QUESTIONS` (EN/CS/RU).

**Co model ukázal**
- **Pracovní bod ~40 Hz** drží smyčky směsi + zátěže generátoru,
  ne samotná geometrie, a zůstává konstantní v celém výkonovém rozsahu (1.2–1.7 kW el.)
  i při rozptylu zapalování.
- **Sériový motocyklový výfukový ventil 25 g funguje** s dosedací pružinou ~1 N
  a předkompresí ~2.5:1 (otevírá se ~36° po DÚ). Žádný zakázkový díl k výrobě.
- **Účinnost (~26–33 %) je dána žádanou hodnotou amplitudy**, nejen geometrií — čím
  blíže k hlavě válce, tím vyšší komprese a účinnost.
- Vibrace ~1.4 kN; protifázové dvojče vyruší ~88 % síly a zbude
  klopný moment ~165 N·m.

**Důvěryhodnost** — autotesty procházejí (`calc/verify.py`): konvergence v dt, jádro vs analytická
rezonance (~1 %), energetická bilance. Jde o **0D** model — na řadě je CFD vyplachování/stratifikace
(OQ-A3).

**Dále** — model říká, že není třeba vyrábět žádný speciální díl, takže dalším
milníkem není výkres, ale **prototyp a fyzikální měření**, které tato
0D čísla ověří.

---
