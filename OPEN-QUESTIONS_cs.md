# Otevřené otázky — co zatím nevíme

*[English](OPEN-QUESTIONS.md) · [Čeština](OPEN-QUESTIONS_cs.md) · [Русский](OPEN-QUESTIONS_ru.md)*

*Závazná je anglická verze.*

*Poctivý seznam. Koncept stojí na principech, které dávají fyzikální smysl,
ale čísla zatím neexistují. Je to zadání pro simulace, výpočty
a prototyp — a otevřená pozvánka: pokud dokážete posunout kterýkoli bod,
založte Issue. Odpověď „nevím, ale zkusil bych tohle“ má větší cenu než
potlesk i než paušální odmítnutí.*

---

## A. Termodynamika a výměna náplně

1. **0D/1D model cyklu** — tlaky, teploty, práce, účinnost v návrhovém
   bodě. Bez něj jsou všechny výkonové cíle (~3 kW mechanicky) jen odhady.
   **Aktualizace** (`calc/thermo.py`): 0D uzavřený cyklus (reálné palivo, Wiebeho
   hoření, tepelné ztráty podle Woschniho, podíl zbytkových plynů) na kinematice
   mezního cyklu. Při φ ≈ 0.8 dává ~5.8 bar IMEP (výchozí odhad 5 bar byl zhruba
   správný), špičku ~22 bar, špičku ~2400 K, **tepelnou účinnost ~26 % (ne 38 %)**.
   Dvě skutečná zjištění: výfukové okno se otevírá brzy (expanze je zkrácená)
   a **efektivní kompresní poměr je jen ~3.5, ne geometrických 9** — píst se obrací
   ve ~18 mm, místo aby došel až k hlavě válce, takže provoz s vyšší amplitudou je
   hlavní páka na účinnost (kvantifikováno v `calc/compression.py`: 17 → 23 mm zvedne
   efektivní poměr ~3.2 → ~5.6 a účinnost ~25 → ~33 %, za cenu špičkového
   tlaku ~20 → ~29 bar). Stále je potřeba 1D model výměny náplně a chemie
   (špičková T je horní mez) — viz A3.
2. **Časování výfukového okna** — výška horní hrany vs. délka expanze vs.
   kvalita vyplachování. Strategie: nejdřív vrtat nízko, ladit frézováním hrany nahoru.
   Potřeba: 1D simulace výměny náplně, poté experiment.
3. **CFD vyplachování a stratifikace** — udrží kapkovité trysky + squish
   skutečně bohatou zónu pod svíčkou a výfukové plyny u stěny?
   Klíčový předpoklad celého konceptu pro emise a účinnost.
4. **Vnitřní EGR** — jaký podíl zadržených výfukových plynů je optimální; potvrdit,
   že bleskové odpaření na horkém inertním plynu nevede k samovznícení
   (teplotní hranice).
5. **Ejektorový efekt v Y spojce** — délky větví vs. fáze pulzů (rychlost
   zvuku ve výfukových plynech ~500–600 m/s). Pomáhá podtlak vyplachování,
   nebo je efekt zanedbatelný?
   **Aktualizace** (`calc/exhaust_acoustics.py`): při 40 Hz je vlnová délka ~17 m a čtvrtvlna ~4.2 m → laděný výfuk je v kompaktním motoru nemožný. Ejektor je nanejvýš mírný přímý pulzní efekt, ne rezonance — což potvrzuje volbu otevřeného výfuku. Zda vůbec pomáhá = 1D/CFD.
6. **Přestup tepla** — bilance: kolik do hliníku, kolik odchází
   s výfukovými plyny, jak moc se nasávaná směs ohřeje při průchodu
   generátorem (ztráta plnicí účinnosti vs. přínos chlazení).

## B. Dynamika a rezonance

7. **Rezonanční frekvence systému** — f = (1/2π)√(k/m): spočítat podpístový
   objem pro cílovou frekvenci; vliv netěsnosti pouzder na efektivní tuhost;
   vliv proměnné tuhosti vzduchové pružiny (nelinearita) na tvar kmitů.
   **První úkol pro `calc/` — nyní rozpracováno (viz [`calc/`](calc/)).**
   První výsledek z 0D modelu: samotná podpístová vzduchová pružina je měkká
   (~10 Hz při 1 kg) a tuhosti dominuje **kompresní pružina na straně
   spalování**, jejíž tuhost roste s tlakem. Mezní cyklus si proto sám volí
   ~40 Hz (nad pracovním odhadem 30 Hz) **a frekvence se posouvá se zatížením/amplitudou**
   (~40–48 Hz v použitelném rozsahu zatížení — viz bod níže v sekci G).
   Otevřené: lze skutečně udržet jednu pracovní frekvenci, nebo platí „frekvenci
   určuje fyzikální systém, ne řízení“ jen přibližně? Potřebuje to sdružený model
   mechanika×EM×termodynamika a prototyp.
   **Aktualizace:** `calc/freq_hold.py` ukazuje, že směs (energie paliva) je druhý
   akční člen — zátěž nese změnu výkonu, směs dorovnává frekvenci zpět —
   a obojí společně udrží ~40 Hz při téměř konstantním špičkovém tlaku v rozsahu
   ~1.2–1.7 kW. Frekvenci tedy udržet *lze*, jen ne samotnou geometrií.
8. **Hmotnost pohyblivé sestavy** — skutečná čísla (písty + pístnice + zuby + koncová víčka +
   podíl pružin); každý gram posouvá rezonanci a vibrace.
   **Aktualizace** (`calc/tradeoff.py`): hmotnost je hlavní knoflík (f ∝ 1/√m), ale
   kompromis není takový, jaký byste čekali — při pevné amplitudě sleduje vibrační síla
   (zhruba konstantní) sílu od spalování, takže větší hmotnost ji *nesnižuje*
   (mírně roste). Lehčí hmota je lepší pro výkon i pro vibrace. Sériový
   ventil 25 g přepouští od ~0.7 kg (46 Hz) výše (s rezervou v pracovním bodě
   ~40 Hz), takže ventil není omezující podmínkou — zbývající
   cenou vyšší frekvence jsou vibrace, které řeší protifázové dvojče.
9. **Silová bilance ventilu v pístu** — pružina vs. tlakový rozdíl vs.
   setrvačnost během celého cyklu; velikost a stabilita setrvačného
   zpoždění otevření (asymetrické časování). Skutečná hmotnost ventilu.
   **Aktualizace** (`calc/valves.py`): s **dosedací pružinou 1 N** (pružina ventil
   jen dosazuje do sedla; práci odvádí dynamika plynů) a předkompresí ~2.5:1
   **sériový motocyklový výfukový ventil 25 g přepouští** — otevírá se ~36° po
   DÚ, což dává asymetrické časování „nejdřív výfuk, pak přepouštění“ zadarmo.
   Otevírací tlak (~32 N) a setrvačnost (~35 N) vycházejí srovnatelně, jak tvrdí
   ch.5, a spalování ventil zabouchne (~300 N = pojistka proti zpětnému šlehu, ch.20).
   Ladicím knoflíkem je předkomprese (více → otevírá dříve, menší zpoždění). Není
   potřeba žádný speciální odlehčený ventil — což byl celý smysl použití
   sériového žáruvzdorného výfukového ventilu.
10. **Vibrace a uložení** — síly do rámu, návrh antivibračního uložení;
    kdy přejít na dvoumodulové protifázové uspořádání.
    **Aktualizace** (`calc/twin.py`): protifáze silně ruší výslednou budicí *sílu*
    (1387 N → 162 N, −88 %, cyklus s převahou lichých harmonických), ale zanechává
    velký *klopný moment* (~165 N·m při rozteči 120 mm), který musí
    nést uložení. Souosé skládání modulů (menší rozteč) ho zmenšuje.
11. **Chování v mezních stavech** — dotyk pístu s hlavou válce: energie nárazu,
    napětí ve spoji, závitu, přírubě vložky (jednorázová událost i opakovaně).

## C. Generátor a magnetika

12. **FEM magnetického obvodu** — geometrie vedení budicího toku **kolem**
    permanentních magnetů (ne skrz ně proti polarizaci). Analýza demagnetizace
    za teploty = podmínka životnosti. Volba magnetů
    (NdFeB SH/UH vs. SmCo).
    **Aktualizace** (`calc/magnetics.py`): první hrubý odhad pomocí magnetických odporů dává ~0.9 T ve vzduchové mezeře, ~185 závitů pro špičku 110 V a **rezervu proti demagnetizaci ~8×** vůči koercivitě za tepla — potlačitelné buzení vypadá geometricky proveditelně, *pokud* je tok veden kolem magnetů. Rozhodne až FEMM/Maxwell.
13. **Poměr PM/budicí vinutí** — pracovní hypotéza 50/50; ustálené ztráty
    v budicím vinutí (I²R) vs. rozsah řízení buzení. Optimalizace.
14. **Vzduchová mezera** — tolerance souososti přes pouzdra; citlivost
    výkonu a sil na excentricitu.
15. **Ztráty** — v železe (0.3 mm @ ~100 Hz), vířivé proudy ve zbývajících plných
    dílech, účinnost generátoru v pracovním bodě.
16. **Indukované napětí vs. zdvih** — průběh EMF po zdvihu (koncové jevy
    na mezích zdvihu), návrh počtu závitů cívek pro ~100 V DC po usměrnění.

## D. Únava a životnost (10⁹ cyklů)

17. **Závitové spoje pístnice** — předpětí, amplituda napětí v kořeni závitu,
    výpočet životnosti; ověření pulzní zkouškou.
18. **Svazek lamel zubů na pístnici** — tečení izolačního kroužku pod zatížením
    nalisování, únava epoxidu při rázech, tepelné cyklování. Volba materiálů (PEEK?).
19. **Kuželové ventilové pružiny** — životnost při kombinaci zdvihu ventilu a kmitání
    s pístem.
20. **Pístní kroužky přes vrtaná okna** — poměr oken a můstků, úprava hran;
    rychlost opotřebení v čase.
21. **Kulové segmentové klouby** — kontaktní tlak, režim mazání, specifikace
    nitridace.

## E. Řízení

22. **Regulace amplitudy zátěží/buzením** — algoritmus řízení (odezva v ms),
    stabilita smyčky v celém rozsahu; sdružená simulace (mechanika × elektromagnetika
    × termodynamika).
    **Aktualizace** (`calc/control.py`): dvě PI smyčky (směs↔výkon, zátěž↔frekvence)
    drží žádané hodnoty při skokové změně požadovaného výkonu (1.2→1.55→1.3 kW) při rozptylu
    zapalování 6 % v každém zážehu — frekvence zůstává na 40 Hz (±~0.6 Hz).
    Sdružená smyčka je v 0D stabilní; dalším krokem je přidat skutečnou elektromagnetiku
    generátoru a přechodové děje při startu/vynechání zážehu.
23. **Startovací sekvence** — energie a čas potřebné k rozkmitání v motorovém režimu;
    minimální amplituda pro první zapálení; trvání fáze s nulovým buzením (bez
    elektromagnetického brzdění).
24. **Cyklus zotavení po vynechání zážehu** — kolik energie zbývá, mez obnovitelnosti,
    počet opakovaných pokusů.
25. **Snímání polohy z napětí cívek** — přesnost vs. indukční snímače;
    fúze tří zdrojů.

## F. Parametry, které je třeba určit

| Parametr                          | Stav                                  |
|-----------------------------------|---------------------------------------|
| Zdvih                             | Neurčeno (souvisí s rezonancí a výkonem) |
| Mechanická frekvence              | Neurčeno (dána rezonancí; desítky Hz) |
| Kompresní poměr nad pístem        | Neurčeno (kompromis pro více paliv)   |
| Objem předkompresní komory        | Neurčeno (z rezonance, ch. 14 DESIGN) |
| Výška / počet výfukových oken     | Neurčeno (1D simulace + ladění)       |
| Hmotnosti dílů (ventil, píst…)    | Neurčeno (souvisí se vším výše)       |
| Hluk / tlumení                    | Neurčeno                              |
| Emise (HC/NOx/CO)                 | Neurčeno (měření na prototypu)        |

## G. Co by koncept vyvrátilo

*Abychom byli k sobě upřímní — tohle jsou rány, které by ho mohly zabít:*

- CFD ukáže, že se stratifikace při realistickém vyplachování zhroutí → výhoda
  v emisích a účinnosti zmizí,
- setrvačné zpoždění ventilu se ukáže jako příliš velké nebo nestabilní → časování
  přepouštění selže, výkon se zhroutí,
- analýza demagnetizace ukáže, že potlačitelné buzení nelze v dostupném prostoru
  dosáhnout → padá koncept startu i řízení amplitudy,
- únava spoje pístnice nedosáhne 10⁹ cyklů při rozumném průřezu →
  architektura spojů se musí zásadně změnit,
- sdružená simulace neudrží stabilní amplitudu při realistickém rozptylu
  zapalování → řízení se stane neúnosně složitým,
- pracovní frekvence není dána samotnou geometrií — posouvá se se
  zatížením/amplitudou, protože dominantní pružina (komprese při spalování) závisí
  na tlaku. *Nalezené zmírnění* (0D, `calc/freq_hold.py`): směs +
  zátěž ji společně drží konstantní (~40 Hz, téměř konstantní špičkový tlak) v rozsahu
  ~1.2–1.7 kW, v souladu se smyčkami z ch.12. *Zbytkové riziko:* opírá se to o to,
  že smyčka směsi má dost autority uvnitř chudé, neklepající, stratifikované
  oblasti — pokud je tato autorita příliš malá, nebo je sdružená smyčka nestabilní
  při skutečném rozptylu zapalování, provoz s konstantní frekvencí v celém výkonovém
  rozsahu selže.

Každou z těchto věcí lze ověřit **dříve**, než se utratí peníze za výrobu.
Proto je tento soubor v repozitáři jako první.

---

★ Viva La Resistánce ★
