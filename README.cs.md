# calc/ — NIC-FPLG: emulátor dynamiky a první výpočty

*0D emulátor dynamiky volného pístu pro NIC-FPLG, s lehkými závislostmi.
Existuje proto, aby dal první čísla, na která návrh čeká (DESIGN kap.14:
„Konkrétní čísla TBD — první úloha pro `calc/`"). Tohle je živá česká verze;
anglicky v [`README.md`](README.md), rusky v [`README.ru.md`](README.ru.md).*

---

## Co to je (a co to není) — poctivě

**Je to** soustředěný (lumped) 0D model: jeden stupeň volnosti, komory s ideálním
plynem, idealizované přepouštění a výplach (reset tlaku, ne model proudění).
Je to správný nástroj na **dynamiku, rezonanci, amplitudu, regulaci a první
odhady**. Každý vstup je *seed* (výchozí odhad), ne výsledek.

**Není to** CFD (výplach/stratifikace — OQ-A3), magnetický obvod (OQ-C/FEM)
ani únavová životnost (OQ-D). Tam vede předěl na profesionální nástroje
(viz dole).

---

## Jak to spustit

```bash
pip install -r requirements.txt
python3 run.py                 # plný běh: report + grafy + CSV do out/
python3 run.py --no-plots      # jen text + CSV (bez matplotlib)
python3 verify.py              # self-testy — spusť dřív, než čemukoliv uvěříš
```

Všechno, co se dá měnit, je v [`params.py`](params.py); každé pole cituje
kapitolu DESIGN nebo otázku, ze které pochází.

---

## Soubory

| soubor | co dělá |
|--------|---------|
| `params.py`    | centrální sada parametrů (vše SI), geometrie objemů komor |
| `resonance.py` | lineární rezonance vzduchové pružiny (DESIGN kap.14) |
| `dynamics.py`  | nelineární časový mezní cyklus volného pístu (jádro modelu) |
| `run.py`       | spustí obojí, sweepuje zátěž generátoru do provozní mapy, zapíše `out/` |
| `freq_hold.py` | konstantní frekvence: jak směs + zátěž drží jednu frekvenci při měnícím se výkonu |
| `control.py`   | spřažené PI řízení (směs↔výkon, zátěž↔frekvence) při rozptylu zápalů — položka 22 |
| `valves.py`    | silový rozpočet přepouštěcího ventilu a setrvačné zpoždění — kap.5 / položka 9 |
| `twin.py`      | dvoumodulové protifázové vyvážení: zbytková síla a klopný moment — kap.15 / položka 10 |
| `tradeoff.py`  | hmota ↔ frekvence ↔ ventil ↔ vibrace ↔ výkon — položky 8/9/10 |
| `thermo.py`    | 0D termodynamický cyklus (reálné palivo, Wiebe, Woschni) — kap.4 / položka 1 |
| `compression.py` | amplituda → efektivní komprese → účinnost — kap.4 / položka 1 |
| **`knock.py`**     | **mez klepání (Livengood-Wu + Douaud-Eyzat) — strop pro „jak moc to hnát"** |
| **`clearance.py`** | **vůle píst-válec za tepla: stejný materiál vs hliník — kap.5 / kap.16** |
| **`heat.py`**      | **tepelná bilance: kam jde teplo (žebra vs výfuk) — kap.10 / OQ-A6** |
| **`fatigue.py`**   | **první odhad únavy tyče/spoje — kap.7 / OQ-D17** |
| **`chem.py`**      | **skutečná chemie spalování (Cantera): teplota plamene, NOx, vliv EGR — kap.4 / OQ-A4** |
| **`freq50.py`**    | **jak se dostat na cílových 50 Hz a co to stojí** |
| **`freq_explore.py`** | **co určuje frekvenci: hmota, zdvih, palivo, dolet pístu** |
| **`magnetics.py`** | **první odhad magnetického obvodu: tok mezerou, závity, demag. rezerva — kap.8 / OQ-C** |
| **`exhaust_acoustics.py`** | **1D akustika výfuku / proveditelnost Y-ejektoru — kap.9 / OQ-A5** |
| `verify.py`    | self-testy: konvergence kroku, fyzika vs analytika, energetická bilance |
| `out/`         | generované grafy a CSV |

(Tučně = nové soubory.)

---

## Co dnešní čísla říkají (headline)

**1. Frekvenci určuje spalovací pružina, ne vzduchová.** Sama vzduchová pružina
pod písty je měkká (~10 Hz při 1 kg). Dominuje tuhost komprese spalování (roste
s tlakem), takže se mezní cyklus sám usadí na **~40 Hz** (nad původním odhadem
30 Hz). Frekvence proto **není daná geometrií samotnou** — drží ji regulační
smyčky směs + zátěž (kap.12, `freq_hold.py`, `control.py`).

**2. Na 50 Hz (cíl kvůli velikosti generátoru) — `freq50.py`.** Předkomprese
s frekvencí nehne. Komprese sama dojede jen na ~47 Hz. **Knoflík na frekvenci
je zdvih.** Dvě cesty: *(a)* kratší zdvih (~34 mm), nízká komprese → funguje
i na heavy fuel; *(b)* mírnější zdvih (~40 mm) + vyšší komprese (~16) → víc
výkonu, ale jen benzín/LPG (vysoká komprese + heavy fuel = klepání). Pozor:
50 Hz = ~1,8 mld cyklů za 10 000 h (vs 1,4 mld při 40 Hz) — o čtvrtinu víc
únavy za kompaktní generátor.

**3. Mez klepání — `knock.py`.** Na benzín (ON 95) neklepe ani do bohaté směsi
(rezerva); chudý provozní bod φ=0,8 má pohodlnou rezervu — přesně proto je návrh
chudý a stratifikovaný. **Klepe heavy fuel** (~70 ON) — to je ten skutečný strop
té dronové aplikace. Je to homogenní (konzervativní) odhad; stratifikace +
vnitřní EGR ho mají posunout výš — o kolik řekne až CFD (OQ-A3). Výpočet
kvantifikuje, jakou práci ta CFD musí odvést.

**4. Vůle píst-válec — `clearance.py`.** Se stejným materiálem (ocel-ocel) se
mezera za tepla hne jen o ~0,035 mm (jen kvůli tomu, že píst je teplejší).
S hliníkovým pístem ~0,12 mm — 3,5× víc. Proto stejný materiál dovolí těsnou,
stálou mezeru (těsní *i* klouže). **Ocelový píst je navíc nutnost:** hliník
(ani hybrid s ocelovou vložkou) tu pevnost nepřežije; za horka lisovaný ocelový
píst s lehkým dofrézováním má největší pevnost a je nejjednodušší vyrobit.

**5. Tepelná bilance — `heat.py`.** Z paliva jde ~26 % do práce, ~12 %+ do stěn
(→ hliník → žebra) a ~62 % výfukem ven. **Žebra musí ufouknout řádově 1–2 kW**
(míň než odhadovaných 2–4 kW; pozor, prostup počítán jen v uzavřené fázi, reálně
o něco víc). Výfuk je velmi horký (~1700 K) — proto nerezové potrubí s tenkou
stěnou, aby teplo odešlo spalinami, ne do motoru (kap.9, kap.16).

**6. Únava tyče/spoje — `fatigue.py`.** Při provozní síle (~1,7 kN) je napětí
v tyči ~8 MPa proti mezi únavy ~230 MPa — **rezerva 50–100×**. Tělo je na tu
sílu hluboce předimenzované, přesně jak má robustní návrh být. **Boj o 10⁹ cyklů
se ale vyhrává jinde** — lokální detaily (povrch v koreni závitu, freting na
čepu, creep pod zubovým paketem). Na to je FEA + **pulzátor** (OQ-D), ne tohle.

**7. Hmota je hlavní páka — `tradeoff.py`.** f ∝ 1/√m. Při konstantní amplitudě
vibrační síla sleduje spalovací sílu, takže s těžší hmotou *neklesá* — lehčí
sestava je lepší pro výkon i vibrace. Těžký ocelový píst tedy *snižuje* frekvenci
(a tím počet cyklů → pomáhá životnosti) — tvoje robustní volby míří stejným
směrem.

**8. Vibrace — `twin.py`.** Jeden modul ~1,4 kN; protifázová dvojice vyruší
čistou *sílu* o ~88 %, ale zůstane *klopný moment* (~165 N·m při rozteči 120 mm),
který nesou silentbloky. Zmenší ho koaxiální poskládání modulů.

**9. NOx je o teplotě, ne o chudosti — `chem.py` (Cantera, propan = LPG).**
Skutečná chemie dá adiabatickou špičku ~2440–2820 K (disociace ji srazí ~120 K).
Překvapení: rovnovážné NO je vysoké u všech směsí a **vrcholí mírně chudé**
(~10 700 ppm při φ=0,8) — takže **chudá směs sama NOx neřeší**. Co ho řeší, je
nižší teplota: **vnitřní EGR** srazí špičku i NO dramaticky (20 % EGR → NO
z ~10 700 na ~4 900 ppm; 30 % → ~1 700 ppm). Návrhový low-NOx tedy stojí a padá
s tím, jak dobře EGR + stratifikace drží špičkovou teplotu — a to rozhodne až
CFD (OQ-A3). Výpočet říká, *kolik* EGR je potřeba.


**10. Magnetický obvod generátoru (první odhad) — `magnetics.py`.** Reluktanční síť dává
vzduchovou mezeru ~0,9 T, ~185 závitů/fázi na 110 V špičku sběrnice a ~1,1 kN síly na
3 kW. Klíčový výsledek je **demagnetizační rezerva ~8×** proti horké koercitivitě magnetu:
vyrušitelné hybridní pole vypadá geometricky proveditelné **bez trvalého odmagnetování,
pokud se budicí tok vede kolem magnetů** (kap. 8). Je to jen 1D reluktance — verdikt patří
FEMM/Maxwellu (OQ-C), ale sázka sekce C první pohled přežila.

**11. Akustika výfuku / Y-ejektor — `exhaust_acoustics.py`.** Při 40 Hz je vlnová délka
spalin ~17 m a laděná čtvrtvlnná trubka by chtěla ~4,2 m — v kompaktním motoru nemožné.
**Laděný výfuk je tedy ze hry** u téhle frekvence, což potvrzuje volbu otevřeného výfuku
(kap. 9): motor neztrácí směs do trubky, takže laděnou komoru nepotřebuje. Y-ejektor je
nanejvýš mírné přímé pulzní pokřížení, ne rezonance — má smysl ověřovat až nestacionární
1D/CFD (OQ-A5).

---

## Jak moc tomu věřit

`verify.py` kontroluje tři věci (všechny procházejí): mezní cyklus se nehne
s krokem; bez spalování a tlumení sedí volné kmitání na analytickou rezonanci
na ~1 %; energetická bilance se uzavírá. **Negarantuje** *absolutní* frekvenci —
ta visí na spalovacích seedech, takže čti absolutní čísla jako ±pár Hz, dokud je
nezpřesní 0D/1D cyklus (OQ-A1) a prototyp. *Trendy* (který knoflík pohne f a o
kolik) jsou robustní.

---

## Předěl na profesionální nástroje (= tvoje OPEN-QUESTIONS)

| otázka | nástroj |
|--------|---------|
| Výplach a stratifikace (OQ-A3) — *nosná otázka* | 3D CFD s chemií: Converge, AVL FIRE, STAR-CCM+, nebo zdarma OpenFOAM |
| 1D výměna náplně, ejektor ve výfuku (OQ-A2, A5) — *první odhad v `exhaust_acoustics.py`* | GT-Power, Ricardo WAVE, AVL BOOST |
| Magnetický obvod, demagnetizace (OQ-C) — *první odhad v `magnetics.py`* | FEM: FEMM (zdarma, 2D-osově-symetrický — ideální pro tubulární stroj), Ansys Maxwell |
| Únava na 10⁹ cyklů (OQ-D) | FEA + **pulzátor** (zkouška, ne simulace) |
| Lepší chemie spalování / NOx | Cantera (zdarma, Python) — dá se ještě dopočítat v 0D |

---

*Dokument je živý. Konkrétní námitky vítány v Issues.*

★ Viva La Resistánce ★
