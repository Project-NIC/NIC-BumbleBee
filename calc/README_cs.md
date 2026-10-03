# calc/ — NIC-FPLG: emulátor dynamiky a první výpočty

*[English](README.md) · [Čeština](README_cs.md) · [Русский](README_ru.md)*

*Závazná je anglická verze.*

*0D emulátor dynamiky volného pístu NIC-FPLG s minimem závislostí.
Existuje proto, aby dodal první čísla, na která návrh čeká (DESIGN ch.14:
„Konkrétní čísla neurčena — první úkol pro `calc/`“).*

---

## Co to je (a co ne) — poctivě

**Je to** model se soustředěnými parametry (0D): jeden stupeň volnosti, komory
s ideálním plynem, idealizovaný výfukový výtok oknem a vyplachování (reset tlaku,
ne model proudění). Je to správný nástroj pro **dynamiku, rezonanci, amplitudu,
řízení a odhady prvního řádu**. Každý vstup je *výchozí odhad*, ne výsledek.

**Není to** CFD (vyplachování/stratifikace — OQ-A3), magnetický obvod
(OQ-C/FEM) ani únavová životnost (OQ-D). Tam začíná předání profesionálním
nástrojům (viz níže).

---

## Spuštění

```bash
pip install -r requirements.txt
python3 run.py                 # full run: report + plots + CSV in out/
python3 run.py --no-plots      # text + CSV only (no matplotlib)
python3 verify.py              # self-tests — run before trusting any number
```

Vše, co lze měnit, je v [`params.py`](params.py); každé pole uvádí
kapitolu návrhu nebo otevřenou otázku, ze které pochází.

---

## Soubory

| soubor | co dělá |
|------|--------------|
| `params.py`    | centrální sada parametrů (vše v SI), geometrie objemů komor |
| `resonance.py` | lineární rezonance vzduchové pružiny (DESIGN ch.14) |
| `dynamics.py`  | nelineární mezní cyklus volného pístu v časové oblasti (jádro modelu) |
| `run.py`       | spouští oba, rozmítá zátěž generátoru do mapy pracovních bodů, zapisuje `out/` |
| `freq_hold.py` | čára konstantní frekvence: jak směs + zátěž drží jednu frekvenci při změně výkonu |
| `control.py`   | sdružené PI řízení (směs↔výkon, zátěž↔frekvence) při rozptylu zapalování — item 22 |
| `valves.py`    | silová bilance přepouštěcího ventilu v pístu a setrvačné zpoždění — ch.5 / item 9 |
| `twin.py`      | protifázové vyvážení dvou modulů: zbytková síla a klopný moment — ch.15 / item 10 |
| `tradeoff.py`  | hmotnost ↔ frekvence ↔ ventil ↔ vibrace ↔ výkon — items 8/9/10 |
| `thermo.py`    | 0D termodynamický cyklus (reálné palivo, Wiebe, Woschni) — ch.4 / item 1 |
| `compression.py` | amplituda → efektivní komprese → účinnost — ch.4 / item 1 |
| `magnetics.py` | první hrubý magnetický obvod: tok ve vzduchové mezeře, závity, rezerva proti demagnetizaci — ch.8 / OQ-C |
| `exhaust_acoustics.py` | 1D akustika výfuku / proveditelnost Y-ejektoru — ch.9 / OQ-A5 |
| `verify.py`    | autotesty: konvergence kroku, fyzika vs analytika, energetická bilance |
| `out/`         | vygenerované grafy a CSV |

---

## Co říkají dnešní čísla (hlavní body)

**1. Frekvenci určuje spalovací pružina, ne vzduchová pružina.** Samotná
podpístová vzduchová pružina je měkká (~10 Hz při 1 kg). Dominuje tuhost
komprese při spalování (která roste s tlakem), takže si mezní cyklus sám volí
**~40 Hz** (nad původním odhadem 30 Hz). Frekvence proto **není dána samotnou
geometrií** — drží ji smyčky směsi + zátěže (ch.12, `freq_hold.py`,
`control.py`).

**2. Hmotnost je hlavní páka — `tradeoff.py`.** f ∝ 1/√m. Při pevné amplitudě
vibrační síla sleduje sílu od spalování, takže větší hmotnost ji *nesnižuje*
— lehčí je lepší pro výkon i pro vibrace. Těžký ocelový píst proto
frekvenci *snižuje* (a počet cyklů → pomáhá životnosti) — vaše robustní volby
míří všechny stejným směrem.

**3. Vibrace — `twin.py`.** Jeden modul dává ~1.4 kN; protifázová dvojice
vyruší výslednou *sílu* o ~88 %, ale zanechá *klopný moment* (~165 N·m při
rozteči 120 mm), který nese uložení. Zmenšíte ho souosým skládáním modulů.

**4. Magnetický obvod generátoru (první hrubý odhad) — `magnetics.py`.** Odhad pomocí sítě
magnetických odporů dává ~0.9 T ve vzduchové mezeře, ~185 závitů/fázi pro sběrnici se špičkou 110 V a ~1.1 kN
síly pro 3 kW. Klíčovým výsledkem je **rezerva proti demagnetizaci ~8×** vůči
koercivitě magnetu za tepla: potlačitelné hybridní buzení vypadá geometricky proveditelně
**bez trvalé demagnetizace, pokud je budicí tok veden kolem magnetů** (ch.8).
Jde jen o 1D model magnetických odporů — konečný verdikt má stále FEMM/Maxwell (OQ-C), ale
sázka ze sekce C první pohled přežila.

**5. Akustika výfuku / Y-ejektor — `exhaust_acoustics.py`.** Při 40 Hz je vlnová délka
ve výfukových plynech ~17 m a laděná čtvrtvlnná trubka by potřebovala ~4.2 m — v kompaktním
motoru nemožné. **Laděný výfuk tedy při této frekvenci nepřichází v úvahu**, což potvrzuje
volbu otevřeného výfuku (ch.9): motor neztrácí náplň do potrubí, takže nepotřebuje
žádnou laděnou komoru. Y-ejektor, pokud vůbec pomáhá, je mírná přímá pulzní vazba,
ne rezonance — má smysl ho ověřovat jen nestacionárním 1D/CFD (OQ-A5).

**Tady se to nepočítá.** Klepání, chemie spalování a NOx, vůle mezi pístem a válcem za tepla, tepelná bilance, únava do 10⁹ cyklů a cesta k 50 Hz nejsou otázky pro 0D model: potřebují lepší software — CFD s chemií, Canteru, FEA — nebo postavený motor na zkušebně (*Předání profesionálním nástrojům*, níže).

---

## Jak moc tomu věřit

`verify.py` kontroluje tři věci (vše prochází): mezní cyklus nezávisí na kroku;
s vypnutým spalováním a tlumením odpovídá volné kmitání analytické rezonanci
na ~1 %; energetická bilance se uzavírá. **Nezaručuje** *absolutní*
frekvenci — ta závisí na výchozích odhadech spalování, takže absolutní čísla čtěte jako
±několik Hz, dokud je nezpřesní 0D/1D cyklus (OQ-A1) a prototyp. *Trendy*
(která páka hýbe s f a o kolik) jsou robustní.

---

## Předání profesionálním nástrojům (= vaše OPEN-QUESTIONS)

| otázka | nástroj |
|----------|------|
| Vyplachování a stratifikace (OQ-A3) — *ta nosná* | 3D CFD s chemií: Converge, AVL FIRE, STAR-CCM+ nebo volně dostupný OpenFOAM |
| 1D výměna náplně, výfukový ejektor (OQ-A2, A5) — *první hrubý odhad v `exhaust_acoustics.py`* | GT-Power, Ricardo WAVE, AVL BOOST |
| Magnetický obvod, demagnetizace (OQ-C) — *první hrubý odhad v `magnetics.py`* | FEM: FEMM (zdarma, 2D osově symetrický — ideální pro trubkový stroj), Ansys Maxwell |
| Únava do 10⁹ cyklů (OQ-D) | FEA + **pulzátor** (zkouška, ne simulace) |
| Lepší chemie spalování / NOx | Cantera (zdarma, Python) — stále proveditelné v 0D |

---

*Tento dokument je živý. Konkrétní námitky jsou vítány v Issues.*

★ Viva La Resistánce ★
