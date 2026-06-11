# Changelog

Všechny podstatné změny projektu NIC-FPLG. / All notable changes. / Все значимые изменения.

---

## v0.5 — 2026-06-11

### 🇨🇿 Česky

První verze, kde NIC-FPLG stojí na číslech, ne jen na úvaze. Přibyl [`calc/`](calc/) —
0D sada modelů (dynamika volného pístu + termodynamický cyklus + řízení) — a její
výsledky jsou propsané do `DESIGN-FPLG` a `OPEN-QUESTIONS` (EN/CS/RU).

**Co model ukázal**
- **Pracovní bod ~40 Hz** drží regulační smyčky směs + zátěž generátoru, ne
  geometrie sama — a udrží se konstantní napříč výkonem (1,2–1,7 kW el.) i při
  rozptylu zápalů.
- **Stock motorkový výfukový ventil (25 g) funguje** — pružinka ~1 N a
  předkomprese ~2,5:1 ho otevřou ~36° za úvratí. Nic speciálního se nevyrábí.
- **Účinnost (~26–33 %) je otázka amplitudy**, ne jen geometrie — čím blíž k hlavě,
  tím vyšší komprese i účinnost.
- Vibrace ~1,4 kN; anti-fázový dvojmodul vyruší sílu ~88 %, zbývá klopný moment ~165 N·m.

**Důvěryhodnost** — self-testy (`calc/verify.py`): konvergence kroku, jádro proti
analytické rezonanci (~1 %), uzavřená energetická bilance. Je to **0D** — CFD
vyplachu a stratifikace (OQ-A3) je další krok.

**Další** — model říká, že není co speciálního vyrábět. Takže dalším milníkem není
výkres, ale **prototyp a fyzické měření**, které ta 0D čísla ověří.

---

### 🇬🇧 English

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

### 🇷🇺 Русский

Первый релиз, где NIC-FPLG опирается на числа, а не только на рассуждение. Добавлен
[`calc/`](calc/) — набор 0D-моделей (динамика свободного поршня + термодинамический
цикл + управление); результаты внесены в `DESIGN-FPLG` и `OPEN-QUESTIONS` (EN/CS/RU).

**Что показала модель**
- **Рабочая точка ~40 Гц** удерживается контурами смесь + нагрузка генератора, а не
  одной геометрией — и держится постоянной во всём диапазоне мощности (1,2–1,7 кВт
  эл.) даже при разбросе зажиганий.
- **Штатный мотоциклетный выпускной клапан (25 г) работает** — пружина ~1 Н и
  предсжатие ~2,5:1 открывают его ~36° после НМТ. Никаких особых деталей.
- **КПД (~26–33 %) — это уставка амплитуды**, а не только геометрия: ближе к головке —
  выше степень сжатия и КПД.
- Вибрация ~1,4 кН; противофазный сдвоенный модуль гасит силу ~88 %, остаётся
  качающий момент ~165 Н·м.

**Достоверность** — самотесты (`calc/verify.py`): сходимость по шагу, ядро против
аналитического резонанса (~1 %), энергобаланс. Это **0D** — CFD продувки и
послойного наполнения (OQ-A3) — следующий шаг.

**Дальше** — модель говорит, что особых деталей делать не нужно, поэтому следующая
веха — не чертёж, а **прототип и физические измерения** для проверки этих 0D-чисел.

---

★ Viva La Resistánce ★
