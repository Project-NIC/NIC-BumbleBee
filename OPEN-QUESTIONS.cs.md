# Otevřené otázky — co (zatím) nevíme

*Poctivý seznam. Koncept stojí na principech, které dávají fyzikální smysl,
ale čísla chybí. Tohle je zadání pro simulace, výpočty a prototyp — a zároveň
pozvánka: pokud umíte kteroukoliv položku posunout, ozvěte se v Issues.
Odpověď „nevím, ale zkusil bych tohle" má větší cenu než potlesk i než
paušální zamítnutí.*

---

## A. Termodynamika a výměna náplně

1. **0D/1D model cyklu** — tlaky, teploty, práce, účinnost v návrhovém bodě.
   Bez něj jsou všechny výkonové cíle (3 kW mech.) jen odhad.
   **Doplnění** (`calc/thermo.py`): 0D uzavřený cyklus (reálné palivo, Wiebeho
   hoření, Woschniho ztráty do stěn, zbytkové spaliny) na kinematice mezního
   cyklu. Při φ ≈ 0,8 dá ~5,8 bar IMEP (seed 5 bar tedy seděl), ~22 bar špičku,
   ~2400 K, **~26 % tepelné účinnosti (ne 38 %)**. Dva reálné nálezy: výfukový
   otvor se otevírá brzy (expanze zkrácena) a **efektivní kompresní poměr je jen
   ~3,5, ne geometrických 9** — píst se obrací na ~18 mm místo dojezdu k hlavě,
   takže provoz na vyšší amplitudě je hlavní páka účinnosti (kvantifikováno
   v `calc/compression.py`: 17 → 23 mm zvedne efektivní poměr ~3,2 → ~5,6
   a účinnost ~25 → ~33 % za cenu špičkového tlaku ~20 → ~29 bar). Zbývá 1D model
   výměny náplně a chemie (špičková teplota je horní mez) — viz A3.
2. **Časování výfukových otvorů** — výška horní hrany vs. délka expanze
   vs. kvalita výplachu. Strategie: vrtat níž, ladit frézováním nahoru.
   Potřeba: 1D simulace výměny náplně, poté experiment.
3. **CFD výplachu a stratifikace** — udrží kapkovité trysky + squish
   skutečně bohatou zónu pod svíčkou a spaliny na obvodu? Klíčový
   emisní i účinnostní předpoklad celého konceptu.
4. **Vnitřní EGR** — kolik zbytkových spalin je optimum; ověřit, že odpar
   na horkých inertních spalinách nevede k samovznícení (hranice teplot).
   **Doplnění** (`calc/chem.py` Cantera; `calc/knock.py`): NOx visí na špičkové teplotě, ne na chudosti — rovnovážné NO vrcholí mírně chudé; srazí ho nižší teplota přes vnitřní EGR (~20 % → NO ~10 700→~4 900 ppm; ~30 % → ~1 700 ppm). Klepání: benzín/LPG mají rezervu, heavy fuel (~70 ON) klepe = reálný strop výkonu na cyklus. Obojí závisí na tom, jak geometrie drží teplotu/stratifikaci (A3).
5. **Ejektorový efekt v Y** — délky větví vs. fáze pulzů (rychlost zvuku
   ve spalinách ~500–600 m/s). Funguje podtlaková podpora výplachu,
   nebo je to zanedbatelné?
   **Doplnění** (`calc/exhaust_acoustics.py`): při 40 Hz je vlnová délka ~17 m a laděná čtvrtvlna ~4,2 m → laděný výfuk je v kompaktním motoru nemožný. Ejektor je nanejvýš mírný přímý pulzní efekt, ne rezonance — potvrzuje volbu otevřeného výfuku. Jestli vůbec pomáhá, řekne 1D/CFD.
6. **Přestup tepla** — bilance: kolik do hliníku, kolik spalinami ven,
   ohřátí nasávané směsi průchodem přes generátor (ztráta plnění vs.
   zisk chlazení).
   **Doplnění** (`calc/heat.py`): z paliva ~26 % do práce, ~12 %+ do stěn (→ žebra ~1–2 kW; míň než odhad 2–4 kW), ~62 % horkým výfukem (~1700 K) ven — žebra mají skromnější úkol.

## B. Dynamika a rezonance

7. **Rezonanční frekvence soustavy** — f = (1/2π)√(k/m): dopočítat objem
   pod písty pro cílovou frekvenci; vliv netěsnosti futer na efektivní
   tuhost; vliv proměnné tuhosti vzduchové pružiny (nelinearita) na tvar
   kmitu. **První úloha pro `calc/` — rozpracováno (viz [`calc/`](calc/)).**
   První výsledek 0D modelu: samotná vzduchová pružina pod písty je měkká
   (~10 Hz při 1 kg) a tuhost dominuje **kompresní pružina spalování**, jejíž
   rychlost roste s tlakem. Mezní cyklus se proto sám usadí kolem ~40 Hz
   (nad pracovním odhadem 30 Hz) **a frekvence kolísá se zátěží/amplitudou**
   (~40–48 Hz napříč použitelným oknem zátěže — viz odrážka v sekci G).
   Otevřené: lze vůbec udržet jednu provozní frekvenci, nebo je „frekvenci
   určuje fyzika, ne řízení" jen přibližné? Potřeba spřažený model
   mechanika×EM×termo a prototyp.
   **Doplnění:** `calc/freq_hold.py` ukazuje, že směs (energie paliva) je druhý
   regulátor — zátěž nese změnu výkonu, směs dorovná frekvenci zpět — a dohromady
   drží ~40 Hz při skoro konstantní špičce tlaku napříč ~1,2–1,7 kW. Frekvenci
   tedy udržet *lze*, jen ne geometrií samotnou.
   **Cíl 50 Hz** (`calc/freq50.py`): knoflík na frekvenci je zdvih (kratší → vyšší f); komprese sama jen ~47 Hz, předkomprese nehne. Buď kratší zdvih (jakékoliv palivo), nebo zdvih+komprese (jen benzín/LPG). Daň: ~1,8 mld cyklů/10 000 h vs 1,4 mld při 40 Hz.
8. **Hmotnost pohyblivé soustavy** — reálná čísla (písty + tyč + zuby +
   koncovky + podíl pružin); každý gram mění rezonanci i vibrace.
   **Doplnění** (`calc/tradeoff.py`): hmota je hlavní páka (f ∝ 1/√m), ale
   kompromis je jiný, než by se čekalo — při konstantní amplitudě je vibrační
   síla daná spalovací silou (~konst.), takže těžší sestava ji *nesnižuje*
   (mírně roste). Lehčí sestava je lepší pro výkon i vibrace zároveň. Stock 25g
   ventil přepouští od ~0,7 kg (46 Hz) výš (s rezervou v pracovním bodě ~40 Hz),
   takže vázající omezení to není — zbývající daň za vyšší frekvenci je vibrace,
   řešená anti-fázovým dvojmodulem.
9. **Silový rozpočet pístových ventilů** — pružina vs. tlaková diference
   vs. setrvačnost v celém cyklu; velikost a stabilita setrvačnostního
   zpoždění otevření (asymetrické časování). Hmotnost konkrétních ventilů.
   **Doplnění** (`calc/valves.py`): s **pružinkou 1 N** (pružina ventil jen
   posadí, práci dělá dynamika plynu) a předkompresí ~2,5:1 **stock 25g motorkový
   výfukový ventil přepouští** — otevře se ~36° za úvratí, čili „výfuk první,
   přepouštění druhé" zadarmo. Otevírací síla (~32 N) a setrvačnost (~35 N) vyjdou
   srovnatelné, jak tvrdí kap. 5, a spalování ventil bouchne do sedla (~300 N =
   zpětná pojistka, kap. 20). Předkomprese je ladicí knoflík (víc → otevře dřív,
   menší zpoždění). Žádný speciální lehký ventil není potřeba — což byl celý smysl
   použití stock žáruvzdorného výfukového ventilu.
10. **Vibrace a uložení** — síly do rámu, návrh silentbloků; kdy přejít
    na dvoumodulové protifázové uspořádání.
    **Doplnění** (`calc/twin.py`): antifáze vyruší čistou budicí *sílu* výrazně
    (1387 N → 162 N, −88 %, cyklus s převahou lichých harmonických), ale
    zůstává velký *klopný moment* (~165 N·m při rozteči 120 mm), který musí
    nést uložení. Koaxiální poskládání modulů (menší rozteč) ho zmenší.
11. **Chování při poruše** — dolet pístu na hlavu: energie rázu, napětí
    v čepu, závitech, přírubě vložky (jednorázově i opakovaně).
    **Doplnění** (`calc/fatigue.py`): při ~1,7 kN je napětí v tyči ~8 MPa proti mezi únavy ~230 MPa — rezerva 50–100×. Tělo předimenzované; 10⁹ cyklů se vyhraje v lokálních detailech (povrch závitu, freting, creep) → FEA + pulzátor.

## C. Generátor a magnetika

12. **FEM magnetického obvodu** — geometrie vedení budicího toku **kolem**
    permanentních magnetů (ne skrz, proti polarizaci). Demagnetizační
    analýza za tepla = podmínka životnosti. Volba magnetů (NdFeB SH/UH
    vs. SmCo).
    **Doplnění** (`calc/magnetics.py`): první analytický reluktanční odhad dává vzduchovou mezeru ~0,9 T, ~185 závitů na 110 V špičku a **demagnetizační rezervu ~8×** proti horké koercitivitě — vyrušitelné pole vypadá geometricky proveditelné, *pokud* se tok vede kolem magnetů. Verdikt ale až FEMM/Maxwell.
13. **Poměr buzení PM/elektromagnet** — 50/50 pracovní hypotéza; trvalé
    budicí ztráty (I²R) vs. rozsah řiditelnosti pole. Optimalizace.
14. **Vzduchová mezera** — tolerance souososti přes futra; citlivost
    výkonu a sil na excentricitu.
15. **Ztráty** — železo (0,3 mm @ ~100 Hz), vířivé proudy ve zbytkových
    masivních částech, účinnost generátoru v provozním bodě.
16. **Indukované napětí vs. zdvih** — profil EMF po zdvihu (konce zdvihu,
    end-efekty), návrh počtu závitů na ~100 V DC po usměrnění.

## D. Únava a životnost (10⁹ cyklů)

17. **Závitové spoje tyče** — předpětí, amplituda napětí v jádru závitu,
    životnostní výpočet; zkouška na pulzátoru.
18. **Zubový paket na tyči** — creep izolačního kroužku pod nalisováním,
    únava epoxidu v rázech, teplotní cyklování. Materiálové volby (PEEK?).
19. **Kuželové pružiny ventilů** — životnost při kombinaci vlastního
    zdvihu a kmitání s pístem.
20. **Pístní kroužky přes vrtané otvory** — poměr otvor/můstek, hrany;
    opotřebení v čase.
21. **Polokulové čepy** — kontaktní tlaky, režim mazání, volba nitridace.

## E. Řízení

22. **Regulace amplitudy zátěží/buzením** — algoritmus (odezva ms),
    stabilita smyčky přes celý rozsah; simulace spřažené dynamiky
    (mechanika × elektromagnetika × termodynamika).
    **Doplnění** (`calc/control.py`): dvě PI smyčky (směs↔výkon, zátěž↔frekvence)
    udrží žádané hodnoty při skokové změně výkonu (1,2→1,55→1,3 kW) s 6 %
    rozptylem zápalů — frekvence drží na 40 Hz (±~0,6 Hz). Spřažená smyčka je
    v 0D stabilní; další krok je přidat reálnou elektromagnetiku generátoru a
    přechodové děje startu/misfiru.
23. **Startovací sekvence** — energie a čas rozkmitání v motorickém
    režimu; minimální amplituda pro první zápal; délka fáze s vyrušeným
    polem (bez elektromagnetické brzdy).
24. **Záchranný cyklus po misfire** — kolik energie zbyde, mez
    obnovitelnosti kmitů, počet pokusů.
25. **Detekce polohy z napětí cívek** — přesnost vs. indukční čidla;
    fúze tří zdrojů.

## F. Parametry k finálnímu určení

| Parametr                          | Stav                                  |
| --------------------------------- | ------------------------------------- |
| Zdvih                             | TBD (vazba na rezonanci a výkon)      |
| Mechanická frekvence              | TBD (určí rezonance; řádově desítky Hz)|
| Kompresní poměr nad pístem        | TBD (multi-fuel kompromis)            |
| Objem předkompresních komor       | TBD (z rezonance, kap. 14 DESIGN)     |
| Výška/počet výfukových otvorů     | TBD (1D simulace + ladění)            |
| Hmotnosti (ventil, píst, tyč…)    | TBD (vazba na vše výše)               |
| Hluk / tlumení                    | TBD                                   |
| Emise (HC/NOx/CO)                 | TBD (měření na prototypu)             |

## G. Co by koncept vyvrátilo (falzifikace)

*Abychom si nelhali — tohle jsou rány, na které může zemřít:*

- CFD ukáže, že stratifikace se při reálném výplachu rozpadá → emisní
  a účinnostní výhoda mizí,
- setrvačnostní zpoždění ventilů vyjde příliš velké/nestabilní →
  přepouštění nestíhá, výkon se hroutí,
- demagnetizační analýza neumožní vyrušitelné pole v dané zástavbě →
  padá startovací koncept i regulace,
- únava závitového spoje nevyjde na 10⁹ cyklů v rozumném průřezu →
  nutná jiná architektura spoje,
- spřažená simulace neudrží stabilní amplitudu při reálných rozptylech
  zápalů → řízení se zásadně komplikuje,
- provozní frekvence není daná geometrií samotnou — kolísá se zátěží/amplitudou,
  protože dominantní pružina (komprese spalování) závisí na tlaku. *Náprava
  nalezena* (0D, `calc/freq_hold.py`): směs + zátěž ji dohromady udrží konstantní
  (~40 Hz, skoro konstantní špička tlaku) napříč ~1,2–1,7 kW, v souladu se
  smyčkami z kap. 12. *Zbytkové riziko:* závisí to na dostatečné autoritě
  směsové smyčky uvnitř chudé, nezaklepávající, stratifikované obálky — pokud je
  ta autorita malá nebo je spřažená smyčka nestabilní při reálném rozptylu
  zápalů, provoz na konstantní frekvenci přes celý výkonový rozsah padá.

Každá z těchto věcí se dá ověřit **dřív**, než se utratí peníze za výrobu.
Proto je tenhle soubor v repu na prvním místě.

---

★ Viva La Resistánce ★
