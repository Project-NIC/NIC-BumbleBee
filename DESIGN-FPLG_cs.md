# NIC-FPLG — Technický popis koncepce

*[English](DESIGN-FPLG.md) · [Čeština](DESIGN-FPLG_cs.md) · [Русский](DESIGN-FPLG_ru.md)*

*Závazná je anglická verze.*

*Dvoutaktní dvouválcový lineární motor s integrovaným lineárním generátorem.*
*Stav: koncepce. Hodnoty označené (TBD) čekají na simulaci nebo výpočet — viz [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS_cs.md). První výsledky 0D dynamiky už existují v [`calc/`](calc/) a jsou zapracovány do kapitol níže.*

---

## Shrnutí

Dvoutaktní lineární motor bez klikového hřídele. Dva písty sdílejí jedinou pístnici;
uprostřed pístnice je trubkový lineární generátor. Motor běží trvale
v jednom pracovním bodě v mechanické rezonanci — frekvenci určuje fyzikální
soustava, nikoli řídicí elektronika. Výkon systému se mění nabíjecím proudem
baterie, nikoli otáčkami ani škrcením.

Klíčová myšlenka: funkce, které konvenční motor řeší pohyblivými díly, zde
obstarává geometrie. Kapkovité kapsy v čele pístu usměrňují proudění
a roztáčejí náplň bez vačkového hřídele. Setrvačnost ventilů vytváří asymetrické
časování bez membrán. Vzduchová pružina předkomprese nahrazuje setrvačník. Stroj
je navržen tak, aby mezní stavy přežil — ne aby se jim vyhýbal.

Cílový výkon ~3 kW mechanický, 1–1,5 kW elektrický, životnost 10 000 hodin.
Použití: stacionární generátor, range extender, drony, lehká vozidla
s páteřovou rourou. Úplná technická architektura je popsána v kapitolách
níže; otevřené otázky a scénáře falzifikace v [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS_cs.md).

---

## 1. Filozofie návrhu

Pět principů, které se opakují v každém detailu stroje:

1. **Práci odvádí geometrie.** Funkce, které konvenční motor řeší
   ventilovým rozvodem, elektronikou nebo kalibračními mapami, zde obstarává tvar:
   tlakem řízené ventily, kapkovité trysky v čele pístu,
   setrvačností zpožděné časování přepouštění, rotace pístu díky přesazení kapes.
   Co nemá aktuátor ani software, se nemůže porouchat.
2. **Robustní, nikoli křehký.** Stroj se mezním stavům nevyhýbá —
   přežívá je. Ocelová integrální vložka a píst snesou detonaci
   i kontakt pístu s hlavou válce. Zapalovací svíčka je zapuštěna pod úroveň čela;
   ventily v pístu fungují jako zpětné ventily proti zpětnému šlehnutí.
3. **Jeden pracovní bod.** Konstantní frekvence, konstantní zatížení ~50 % maxima.
   Žádné mapy, žádné přechodové stavy; vše proměnné pohltí baterie.
4. **Tvářený materiál.** Vlákno sleduje tvar: vložka tvářená protlačováním za studena (technologie
   výroby nábojnic), zápustkově kovaný píst, válcované závity, válcovaná tyčovina. Únava
   při 10⁹ cyklech je hlavní nepřítel — tváření kovů je hlavní zbraň.
5. **Servis zabudovaný do konstrukce.** Odkarbonovací otvory bez demontáže,
   generátor jako vyměnitelná kazeta, sériově dostupné periferní díly
   (ventily, zapalovací svíčky, škrticí těleso, zapalovací modul) — opravitelné
   díly z vrakoviště.

---

## 2. Celková architektura

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

- **Dva písty na jedné pístnici** — pohybují se společně (nejde o boxer).
  Spalování na jedné straně = komprese na druhé + předkomprese
  pod oběma písty.
- **Pístnice** = trubka z austenitické nerezové oceli (nemagnetická), nesoucí uprostřed
  lamelované zuby generátoru, na koncích našroubované koncovky s kulovými
  vrchlíkovými klouby pístů.
- **Těleso** = dvoudílný hliníkový odlitek; tvoří přepážky komor předkomprese,
  nese pouzdra pístnice a stator generátoru. Hliník
  slouží především jako chladič — konstrukční pevnost zajišťují ocelové
  vložky nalisované uvnitř.
- **Vložky** („integrální vložka“, hovorově „cartridge head“) = hlava válce +
  válec v jednom kuse, tvar nábojnice: příruba (≥8 šroubů do tělesa), válcová část,
  kuželové hrdlo se závitem pro zapalovací svíčku. Každá vložka je obklopena prstencovým
  nerezovým výfukovým sběrným potrubím, vše zalité do hliníku.

**Proudění náplně (jednosměrná dálnice):** škrticí těleso → prostor generátoru (směs
chladí cívky a magnety, olejová mlha maže pouzdra) → velký sací ventil
v přepážce → komora předkomprese pod pístem (turbulence, chlazení dna pístu,
homogenizace s mazivem) → přepouštěcí ventily v pístu →
kapkovité kapsy → spalovací prostor → spalování → prstencová výfuková okna →
Y-spojka → tlumič. Náplň se nikdy nevrací zpět; každý kubický centimetr
vzduchu cestou odvede čtyři úkoly (chlazení, mazání, předkomprese, spalování).

**Použití:** stacionární generátor / range extender (primární cíl), drony
a letectví (těžké palivo, sběrnice ~100 V), lehká vozidla s motorem v centrální
páteřové rouře (elektrický pohon kol, více modulů v protifázi = vyvážení +
škálování výkonu). Koncepce se vyplácí do ~40 kW na modul; nad touto hranicí jsou lepší konvenční
rotační stroje.

**Bezpečnost zabudovaná do architektury:** ventily v pístu jsou jednosměrné — zpětné šlehnutí
shora je zavře, plamen se nemůže dostat do prostoru náplně a ke generátoru.
Sací ventil v přepážce je druhá zpětná bariéra. Vinutí generátoru jsou
vakuově impregnovaná (třída H); uvnitř nejsou žádné jiskřící díly. Křížově propojené GPIO vypínání
obou ECU zajišťuje, že porucha generátoru zastaví motor a vynechání zapalování odlehčí
amplitudu bez tvrdého nárazu. Odolnost vůči detonaci a přejetí pístu
je záměrná — ocelová vložka a zapuštěná svíčka jsou tu právě kvůli tomu.

---

## 3. Pracovní cyklus a výměna náplně

Dvoutakt bez přepouštěcích kanálů ve stěně válce — přepouštění probíhá **skrz
píst**.

1. **Expanze L / komprese P.** Spalování vlevo žene pístnici doprava.
   Pravý píst stlačuje svou náplň; oba písty současně předkomprimují
   čerstvou směs pod sebou (cíl ~2,5:1 — zvýšeno z původních ~1:2, aby
   sériový přepouštěcí ventil dostal dostatečnou otevírací sílu při slabé dosedací pružině, viz
   ch.5 / `calc/`; sací ventily v přepážkách zavřené).
2. **Výfuk L.** Levý píst odkryje prstencová výfuková okna; spaliny odcházejí
   po celém obvodu do prstencového sběrného potrubí. Horní hrana oken =
   jediné pevné časování ve stroji (TBD — ladí se frézováním hrany směrem nahoru).
3. **Přepouštění L.** Když tlak pod pístem překoná tlak nad ním +
   sílu pružiny + setrvačnou sílu, ventily v pístu se otevřou. Setrvačnost ventilu
   (řádově srovnatelná s tlakovou silou — viz ch. 5) **zpozdí otevření
   za DÚ** → nejdřív výfuk, potom přepouštění = asymetrické časování zadarmo,
   bez membrán, bez výfukových šoupátek (power valves).
4. **Vnitřní EGR.** Část horkých spalin je záměrně zadržena:
   je inertní (bez kyslíku), okamžitě odpařuje palivo, ředí náplň u
   stěny, snižuje teplotu spalování (NOx) a únik HC.
5. Pístnice se vrací — role se prohodí. Synchronizaci drží fyzika: silnější
   spalování na jedné straně zvýší kompresi (a tím i intenzitu
   spalování) na druhé; jemné řízení amplitudy obstarává zatížení
   generátoru (ch. 12).

---

## 4. Spalovací prostor

- **Ploché dno vložky proti plochému čelu pístu**, vůle v HÚ ~1 mm (TBD)
  → **celoplošný squish**: náplň je vytlačována od stěny do středu
  a vytváří turbulenci; u stěny nevzniká kapsa koncových plynů náchylná k detonaci.
- **Zahloubení pro zapalovací svíčku** v kuželovém hrdle vložky; závodní svíčka
  se zkrácenou délkou závitu, elektroda 0,1 mm pod úrovní čela → přejetí pístu k hlavě válce
  svíčku nepoškodí.
- **Kapkovité kapsy v čele pístu** (ch. 5) drží většinu bohaté
  náplně pod svíčkou → **vrstvená náplň**: bohatá u svíčky, chudá a
  inertní (spaliny) u stěny. Stěna = místo výfukových oken → odchází
  přednostně spálený plyn, nikoli čerstvá náplň.
- **Průběh spalování:** zapálení v zahloubení svíčky → plamen prošlehne do kapes
  → postupné, pomalé hoření řízené geometrií; přesazení kapes roztáčí
  náplň (a reakcí i píst). Záměrně **bez detonace** —
  pomalé postupné hoření, nikoli rázové spalování.

**Efektivní komprese závisí na amplitudě, nejen na geometrii (calc):**
geometrický poměr je jen horní mez. *Skutečná (zachycená)* komprese závisí na tom, jak
blízko se píst skutečně dostane k čelu, což určuje provozní amplituda
(zatížení generátoru, ch.12). [`calc/compression.py`](calc/compression.py) ukazuje, že
přechod z amplitudy 17 mm na 23 mm (vůle k hlavě válce 8 → 2 mm) zvýší
efektivní poměr ~3,2 → ~5,6 a tepelnou účinnost ~25 % → ~33 %, za cenu
vyššího špičkového tlaku (~20 → ~29 bar). Účinnost je tedy z velké části otázkou volby žádané
amplitudy: řízení by mělo držet amplitudu tak blízko hlavě válce, jak to
vůle squishe a limit špičkového tlaku dovolí — což je přesně to, co
výše popsaný celoplošný squish chce (píst se téměř dotýká čela).

---

## 5. Píst, ventily, kapkovité trysky

**Píst:** ocel stejné jakosti jako vložka (shodná tepelná roztažnost →
konstantní vůle při všech teplotách → jednodušší kroužky, stálé utěsnění).
Zápustkové kování (vlákno sleduje tvar; prototyp obráběný z válcované tyče). Tři
pístní kroužky — měkčí materiál, velký průřez, **zaoblené hrany**;
tlak předkomprese zespodu vtlačuje směs a olej mezi kroužky →
nepřetržitá cirkulace maziva sadou kroužků.

**Přepouštěcí ventily:** 2× výfukový ventil ze závodního motocyklu, ⌀ ~16 mm,
tenký dřík ~4 mm, žáruvzdorná slitina. Zde pracují ve „studené“ roli —
omývané čerstvou směsí zespodu, s obrovskou rezervou. Sestava:

- vodítka (pouzdra) nalisovaná do pístu zezadu,
- **kuželová pružina** — progresivní tuhost, stlačí se úplně naplocho
  (minimální výška ve stlačení), nemá výraznou vlastní frekvenci → odolná vůči rozkmitání
  v trvale kmitajícím prostředí. Předpětí v sedle je drženo **slabé (~1 N)**:
  pružina ventil jen dosadí, přepouštění obstará dynamika plynů,
- standardní talířek a klínky z automobilového ventilového rozvodu.

**Bilance sil na ventilu (pracovní hodnoty):** setrvačná síla na ventil ~25 g
při ~890 m/s² ≈ 22 N; otevírací tlaková síla ≈ 20 N na 1 bar rozdílu
na talířku ⌀16. Síly jsou **srovnatelného řádu** → pružina se navrhuje
proti součtu (tlak − pružina − setrvačnost) a setrvačnost záměrně
vytváří zpožděné otevření (ch. 3). Každý gram hmotnosti ventilu posune rovnováhu
o ~0,9 N. **Potvrzeno v [`calc/valves.py`](calc/valves.py):** se sériovým
ventilem 25 g, dosedací pružinou ~1 N a předkompresí ~2,5:1 vycházejí otevírací tlak
(~32 N) a setrvačnost (~35 N) podle očekávání srovnatelně a ventil
se otevírá **~36° za DÚ** — časování nejdřív výfuk / potom přepouštění, zadarmo.
Ladicím prvkem je předkomprese (čím vyšší, tím dřív se ventil otevře), takže
asymetrické časování určuje poměr pod pístem, nikoli zakázkový díl — není potřeba
žádný speciální odlehčený ventil.

**Kapkovité kapsy (trysky):** kolem každého ventilu je v čele pístu
kapkovité vybrání hluboké 2–3 mm. Na půlkruhovém (širokém) konci je jen ~0,1 mm
vůle mezi talířkem a stěnou; směrem ke špičce se profil otevírá.
**Talířek ventilu je pohyblivou částí trysky:** zdvih talířku řídí *průtok*,
kapsa řídí *směr* — proud míří ke špičce bez ohledu na
okamžitý zdvih. Dvě kapsy proti sobě, špičky přesazené mimo střed:

- hlavní proud náplně míří do středu pod svíčku (vrstvení),
- přesazení uděluje náplni rotaci → spalování rotuje → reakční moment
  pootočí píst každý cyklus o malý úhel → **rovnoměrné opotřebení** kroužků, vodítek
  a rovnoměrné tepelné zatížení. Levý a pravý píst jsou zrcadlově souměrné.

Obrábění kapes: čelo pístu je přístupné → standardní 3osé frézování
kulovou frézou.

---

## 6. Kulový vrchlíkový kloub (spojení píst–pístnice)

Kloub = kulový vrchlík ⌀ ~15 mm se zakřivením ~15° — jen dvě zakřivené
plochy proti sobě. Vlastnosti:

- velká styčná plocha → **odolnost vůči rázům** (síly od spalování jdou přes
  tlak, nikoli smyk),
- umožňuje **naklopení pístu** vůči pístnici (píst se ve válci sám vystředí,
  soustava je staticky určitá — viz ch. 8, „samovystředění“),
- **prokluz při rotaci pístu je pomalý** (výsledné otáčky pístu řádově
  jednotky za minutu) → režim mezného mazání,
- obě plochy nitridované s mikrodrážkami; drážky se před každým přepouštěcím zdvihem
  naplní směsí a olejem → samomazné kluzné ložisko (analogie
  vačka–zdvihátko; podmínky zde jsou příznivější).

---

## 7. Pístnice a spoje

**Pístnice:** trubka z austenitické nerezové oceli (304/316 — podmínka: nemagnetická;
pozor na deformací indukovaný martenzit v tažených trubkách, řeší se žíháním).

- trubkový průřez = nejlepší poměr tuhosti k hmotnosti → lehká pohyblivá sestava,
- nerez = nízká tepelná vodivost → pístnice nevede teplo z pístů
  do generátoru,
- nemagnetická → magnetický tok prochází výhradně lamelovanými zuby.

**Koncovky s klouby:** šroubované. Klíčové detaily pro 10⁹ cyklů:

- **levé a pravé závity orientované proti směru rotace
  pístu** → vlastní rotace pístu oba spoje průběžně dotahuje
  (pojištění zadarmo),
- **dosedací čelo** — tlaková půlperioda jde z čela na čelo, závit
  ji vůbec nevidí,
- **předpětí nad maximálním provozním tahovým zatížením** — spoj se v provozu nikdy neotevře,
  závity nesou jen statické předpětí (princip šroubu ojnice),
- **válcovaný jemný závit** (ne řezaný) — zpevněný povrch, tlaková
  zbytková napětí, 3–5× vyšší únavová životnost,
- rádiusy na všech přechodech, výběhy závitů bez ostrých zápichů,
- vysokoteplotní anaerobní lepidlo jako sekundární pojistka,
- série: zápustkově kované koncovky (vlákno sleduje tvar spoje); prototyp: válcovaná
  tyčovina (podélné vlákno vhodné pro axiální zatížení).

Poznámka: délka zašroubování nad ~1,5×⌀ už nepomáhá (první závit nese
30–40 % zatížení); rozhoduje předpětí a dosednutí čel, nikoli délka.

---

## 8. Lineární generátor

**Topologie: trubkový stroj s přepínáním toku (flux-switching) s hybridním buzením.**

- **Magnety i cívky jsou ve statoru** — mezi pólovými nástavci složenými
  z plechů 0,3 mm. Pohyblivá část (pístnice) nese jen pasivní
  feromagnetické zuby → minimální pohyblivá hmota, magnety v chlazené zóně.
- **Zuby pístnice:** plechy 0,3 mm nalisované na izolační distanční kroužek
  na zesíleném úseku trubky, zalité epoxidem. Lamelování = potlačení
  vířivých proudů (tok v zubech mění směr). Poznámka: epoxid pro ≥150 °C
  (systémy pro elektromotory); distanční kroužek z materiálu odolného proti tečení
  (PEEK / plněný PA) — trvale zatížený nalisovaný spoj po dobu 10 000 h.
- **Trubkové uspořádání:** radiální magnetické síly se díky symetrii ruší (pístnice
  „plave“ v magnetickém středu, pouzdra nesou minimální zatížení) a zuby jsou
  rotačně symetrické prstence → **jediná topologie slučitelná s rotací
  pístnice**. Rotace pístu (ch. 5) a topologie stroje jsou na sobě vzájemně
  závislé.
- **Dvojnásobný počet zubů** → dvojnásobná elektrická frekvence (cíl ~100 Hz) →
  poloviční tok pro stejné napětí (e = N·dΦ/dt) → dvě cívky v prostoru
  jedné → jednodušší usměrnění. Cena: ztráty v železe rostou s frekvencí —
  při plechách 0,3 mm přijatelné.
- **Hybridní buzení ~50 % PM / 50 % budicí vinutí:** tok lze zesílit,
  zeslabit nebo zrušit. ⚠ **Odmagnetování:** budicí tok musí být veden
  paralelní cestou v železe **kolem** magnetů, nikoli skrz ně
  proti polarizaci (zvlášť za tepla). Magnety s vysokou koercitivitou
  (NdFeB jakosti SH/UH nebo SmCo). Detail magnetického obvodu = kritický bod
  návrhu (TBD, FEM).
- **Pouzdra** (kluzná ložiska v přepážkách): tuhé vedení pístnice (průhyb od
  hmoty zubů), délka ~20 mm, vůle 0,05–0,1 mm → **labyrintové těsnění**
  (průtok ~ vůle³): únik předkomprese několik procent, vrací se do
  sání. Stejný materiál jako pístnice (konstantní vůle při změně teploty) + tvrdý
  povlak. **Pouzdra zároveň vystřeďují stator** — souosost pístnice↔stator
  (vzduchová mezera!) zaručuje jediný díl, nikoli řetězec tolerancí.
- **Montáž / servis:** pístnice → stator → dvě poloviny tělesa s pouzdry se zasunou
  do statoru a sešroubují. Generátor = **uzavřená bezúdržbová kazeta (sealed-for-life)**;
  po opotřebení (cíl 10 000 h) se mění jako celek.

---

## 9. Výfukový systém

- **Prstencové sběrné potrubí** kolem každé vložky (tvar Q s vývodem), celé z nerezové
  oceli — teplo má odcházet se spalinami, nikoli se rozvádět do
  motoru.
- **Proměnná tloušťka stěny (svařenec):** ~1 mm na straně přivrácené ke
  kompresnímu prostoru (úzký tepelný most podél stěny), ~3 mm na
  straně zalité do hliníku (odpor proti přestupu tepla do chladiče +
  tuhost proti zborcení při tlaku lití; kruhový průřez se
  stěnou 3 mm snese tlaky lití s rezervou).
- **Výfuková okna: vrtaná skrz** (hliník + obě stěny trubky + vložka),
  10–20 kruhových otvorů po obvodu kolmo k ose.
  Kruhový otvor = žádné koncentrace napětí; hrany oken **zkosené a
  vyleštěné zevnitř** (ochrana kroužků), válec se vyvrtává až po této
  operaci. Poměr okno–můstek takový, aby kroužek měl vždy dostatečnou
  dosedací plochu (TBD).
- **Odkarbonovací otvory:** protilehlé otvory po vrtání dostanou závit +
  šroub s měděnou těsnicí podložkou (protizáděrová pasta). Vyšroubovat →
  vykartáčovat v ose okna → zašroubovat. Čištění bez demontáže;
  u dvoutaktu nezbytné pro skutečnou životnost.
- **Y-spojka** obou prstenců do jednoho tlumiče. Výfukové pulzy se střídají
  (písty na společné pístnici) → proudění z jedné větve může v druhé větvi vytvořit podtlak
  ejektorovým efektem a napomoci jejímu vyplachování. Efekt závisí
  na délkách větví vzhledem k rychlosti zvuku ve spalinách (~500–600 m/s) —
  **TBD, 1D simulace / experiment**; laditelné délkou potrubí.
- **„Otevřený“ výfuk:** celkový objem ~10× zdvihový objem + disipativní tlumič
  (~0,5 l, perforované přepážky) → minimální protitlak, žádné rezonanční vlny.
  Konvenční dvoutakt potřebuje expanzní komoru, aby vrátila uniklou
  náplň — zde náplň neuniká (vrstvení, ch. 4), takže laděná
  výfuková trubka není potřeba.
- **Ladění časování oken:** okna první vložky vyvrtat záměrně **nízko** (pozdní
  výfuk, dlouhá expanze) a horní hranu posouvat frézováním nahoru, dokud
  vyplachování nebude v pořádku. Jednosměrné ladění bez zničených vložek.

---

## 10. Těleso, chlazení, lití

- **Hliníkové těleso** s podélnými žebry; drážky v žebrech proti „banánovému efektu“
  (tepelné prohnutí). Hliník = chladič; minimum materiálu, pevnost z
  ocelových vložek. Výstupky (nálitky) ve výfukové zóně.
- **Zalévání vložek (squeeze casting / lisování z tekutého stavu):** vložka + výfukové
  sběrné potrubí se zalijí/zalisují roztaveným hliníkem ve formě. Hliník
  se při chladnutí smršťuje víc než ocel/nerez → trvalé **nalisování smrštěním** =
  dokonalý tepelný kontakt a mechanické upevnění bez spojovacích prvků.
  - vložka je během lití podepřena **trnem** s keramickým separačním prostředkem,
  - trubka drží tvar díky tloušťce stěny (3 mm na tlakové straně); alternativa:
    solné jádro vymyté vodou,
  - **válec vyvrtat až PO odlití** (smrštění mění geometrii).
- **Chlazení vzduchem:** žebra = chladič; nasávaná směs chladí generátor
  zevnitř (přispívá i odpařování paliva). Nucené proudění vzduchu podle použití: vrtule
  (letectví), teplotně řízené elektrické ventilátory (vozidlo/stacionární);
  odpadní teplo do žeber řádově 2–4 kW při plném výkonu (TBD).

---

## 11. Palivová soustava — vícepalivová

- **Vstřikování do sání** za škrticím tělesem, do zóny turbulence
  (lepší rozprášení). Škrticí těleso a vstřikovač = sériové díly z
  motocyklu ~150 ccm (velká rezerva průtoku).
- **Oddělené vstřikování maziva:** pulzní dávkovací čerpadlo (typ Webasto);
  esterový („eko/bio“) olej ředěný benzinem (zimní viskozita, průchod
  vstřikovačem). Dávku lze řídit podle zatížení. **Nezbytné pro LPG** — suchý plyn
  nemaže; olejová mlha v sání současně maže pouzdra, klouby
  a sadu kroužků.
- **Paliva:** benzin; LPG (propan-butan); nafta+benzin se zapalováním jiskrou
  („těžké palivo“ — používá se v motorech vojenských dronů; ředění benzinem zlepšuje
  odpařování a zápalnost). Alkoholová paliva vyloučena (nízká objemová
  hustota energie).
- **Jeden pracovní bod = jeden řádek parametrů na palivo** (předstih, směs,
  dávka oleje) místo celé mapy. Změna paliva znamená změnu tří čísel.

---

## 12. Elektronika a řízení

**Architektura: 2 procesory** (STM32H503 — 250 MHz Cortex-M33, HW časovače
s mrtvým časem): ECU motoru + ECU generátoru. Stavová komunikace +
**bezpečnostní signály na vyhrazených GPIO** (pevně zapojené, latence v µs, žádný protokol).

**Křížová ochrana:**

- porucha generátoru (nadproud…) → GPIO → motor: zavřít škrticí klapku + vypnout
  zapalování; pístnice bezpečně dokmitá,
- vynechání zapalování → GPIO → generátor: **okamžitě odpojit zátěž** → pístnice si ponechá energii
  pro další kompresi → *zotavovací cyklus* (2–3 pokusy o zapálení), tvrdé
  zastavení až potom.

**Snímání polohy — tři nezávislé zdroje pravdy:**

1. 4× vysokofrekvenční indukční snímače skrz vložku (zapouzdřené,
   dimenzované na tlak), snímající písty **křížově** → poloha, rychlost,
   směr + vzájemná redundance,
2. průběh napětí cívek generátoru (poloha „zadarmo“),
3. snímač klepání na tělese (detonace + nezávislá detekce vynechání zapalování).

**Zapalování:** sériový dvoukanálový modul (např. Renault D4F740),
**dva nezávislé kanály — ŽÁDNÁ ztrátová jiskra (wasted spark):** protilehlý válec má
v okamžiku zážehu otevřená výfuková okna a čerstvou náplň; společná jiskra
hrozí zpětným šlehnutím. Informace o fázi ze snímačů je k dispozici; každá svíčka zapaluje
na svůj vlastní signál. Pevný předstih + teplotní korekce (jeden pracovní bod).

**Směs:** širokopásmová lambda sonda (LSU 4.9) pro ladění, skoková pro
provoz; bez katalyzátoru. Snímače MAP před/za škrticí klapkou, teploty.

**Startovací sekvence:**

1. plné přebuzení (až ~200 %) → generátor v motorovém režimu rozkmitá pístnici,
2. první zážehy na minimální směs,
3. krátce zrušit buzení zpětným proudem → nulové elektromagnetické zatížení,
   kmitání se ustálí „tlak proti tlaku“ na chudé směsi (tuto
   fázi držet krátkou — bez elektromagnetického brzdění řídí amplitudu
   jen vzduchová pružina),
4. postupné opětovné nabuzení = plynulý náběh zatížení a směsi do pracovního bodu.

**Řízení amplitudy:** poloha úvratí je dána energetickou bilancí, nikoli
geometrií. Hlavní akční člen = **zatížení/buzení generátoru** (elektromagnetická
brzda, odezva v ms). Tři nezávislé smyčky: směs (pomalá), buzení
(rychlá), předstih (korekční). **Potvrzeno v [`calc/control.py`](calc/control.py):**
zatížení a směs společně drží konstantní frekvenci při změnách výkonu —
změnu výkonu nese zatížení, směs dorovnává frekvenci zpět — a smyčky
zůstávají stabilní při skokové změně požadovaného výkonu za realistického rozptylu
zapalování mezi cykly. Jediný pracovní bod drží tyto dvě smyčky, nikoli
samotná geometrie (viz ch.14).

---

## 13. Elektrický výstup

- 2 cívky → usměrnění pomocí **2 MOSFETů** synchronně řízených; budič
  s **hardwarovým mrtvým časem** (časovače STM32H5 ho mají vestavěný) — ochrana proti
  průrazu větve (shoot-through) nesmí záviset na softwaru.
- **Kondenzátorová baterie mezi usměrňovačem a BMS** (řádově tisíce µF):
  FETy a bočníky BMS jsou stavěné na hladký DC proud; pulzy 100 Hz bez vyhlazení
  zvyšují efektivní (RMS) ohřev a mohou falešně vybavit nadproudovou ochranu.
- BMS → trakční baterie. **Baterie = zásobník a regulátor:** nabíjecí proud
  lze plynule řídit; výkon systému se mění zde, motor běží
  beze změny. Cíl: stejnosměrná sběrnice ~100 V, ~15 A při 1,5 kW.

---

## 14. Rezonanční provoz

Předkomprese pod písty tvoří **vzduchovou pružinu**; pružina + hmota pohyblivé
sestavy = rezonátor:

```
f = (1/2π)·√(k/m)
m … mass of moving assembly (pistons + rod + teeth + end caps)
k … air spring stiffness (volume below pistons, pre-compression ratio, piston area)
```

Postup návrhu je **obrácený**: zvolit optimální frekvenci spalování →
zvážit sestavu → **vypočítat objem pod písty** tak, aby
rezonance padla na zvolenou frekvenci. Provoz v rezonanci = vzduchová pružina
vrací energii obratu zadarmo, generátor odebírá jen užitečnou práci.
(Korekce: únik přes pouzdra mírně snižuje efektivní tuhost — započítat.)

**Výsledek 0D ([`calc/`](calc/)):** obraz je jemnější než „frekvenci určuje vzduchová
pružina“. Při 1 kg dává samotná vzduchová pružina pod písty jen ~10 Hz;
dominantní tuhost je **kompresní pružina na straně spalování**, která je
závislá na tlaku, takže mezní cyklus si při výchozí geometrii sám zvolí **~40 Hz**
— nad původním pracovním odhadem ~30 Hz. Protože tuhost
závisí na tlaku spalování, frekvence *není* dána samotnou geometrií:
konstantní ji drží regulační smyčky směsi + zatížení (ch.12). Chceme-li dosáhnout dané
frekvence, páky jsou pohyblivá hmota (f ∝ 1/√m), předkomprese a vrtání/zdvih
— vše lze proměřit (sweep) v `calc/`.

---

## 15. Vibrace a uložení

Oba písty se pohybují společně → pohyblivá hmota kmitá bez jakéhokoli vlastního vyvážení.
Pracovní odhad: m ≈ 1 kg, zdvih 50 mm, 30 Hz → F ≈ 890 N @ 30 Hz. **Výsledek 0D
([`calc/`](calc/)):** při samovolně zvolených ~40 Hz je budicí síla blíže
**~1,4 kN** a — protože při pevné amplitudě sleduje sílu od spalování —
s větší hmotou *neklesá*, takže lehčí sestava je lepší pro vibrace
*i* výkon. Uspořádání dvou modulů v protifázi ruší výslednou sílu z ~88 %
(1,4 kN → ~0,16 kN), ale zanechává **klopný moment (~165 N·m při rozteči 120 mm)**,
který musí uložení přenést; souosé uspořádání modulů za sebou ho zmenšuje.

- stacionární použití: masivní rám + antivibrační uložení naladěné hluboko pod
  pracovní frekvenci (běžná praxe u kompresorů),
- lehká pístnice (trubka, zuby místo magnetů) zmenšuje problém už u zdroje,
- **modulární řešení:** dva stroje vedle sebe v protifázi = dokonalé
  vyvážení + dvojnásobný výkon (přirozené pro páteřovou rouru, ch. 17).

---

## 16. Materiály a tepelné hospodářství

| Díl                  | Materiál                   | Důvod                                         |
|----------------------|----------------------------|-----------------------------------------------|
| Vložka + píst        | ocel, stejná jakost        | shodná roztažnost → konstantní vůle           |
| Pístnice             | austenitická nerez, trubka | nemagnetická, tepelně izolující, lehká        |
| Výfukové potrubí     | nerez, stěna 1/3 mm        | nízké λ; teplo odchází se spalinami           |
| Těleso               | hliník, žebrovaný          | chladič; sevření vložek smrštěním             |
| Zuby gen. + stator   | elektroplech 0,3 mm        | potlačení vířivých proudů                     |
| Magnety              | NdFeB SH/UH nebo SmCo      | koercitivita (rušení buzení, teplota)         |
| Klouby, pouzdra      | ocel + nitridace/povlak    | mezné mazání, rázy, konst. vůle               |
| Ventily              | žáruvzdorná slitina (moto) | obrovská rezerva ve „studené“ roli            |

Princip tepelného toku: **teplo ze spalování → hliník → vzduch; teplo výfuku →
spaliny → ven.** Nerez všude tam, kudy teplo nesmí projít (sběrné potrubí, pístnice);
tloušťka stěny jako řízený tepelný odpor (ch. 9).

---

## 17. Výroba

**Prototyp (bez nástrojů, proveditelné v EU/ČR):** vložka soustružená + honovaná (po
montáži), píst CNC z válcované tyče, sběrné potrubí jako svařenec, těleso obráběné
z plného materiálu + konvenční nalisování za tepla, plechy řezané laserem (u finální verze žíhat
hrany), pístnice z katalogové trubky, periferní díly sériově dostupné.

**Série:** vložka zpětným protlačováním za studena (technologie výroby nábojnic — vlákno sleduje
tvar), píst zápustkovým kováním („3D“ zápustka, minimální obrábění; tenké blány
mezi dutinami se jednoduše profrézují), squeeze casting hliníku kolem
vložek (trn + keramický separátor; chladnutí trvá sekundy), válcované závity.
Nástroje (zápustky, formy, přípravky) — realisticky Asie.

---

## 18. Servis a životnost

Cíl **10 000 h ≈ 10⁹ cyklů** → konstrukce řízená únavou (předpětí, válcování,
rádiusy, tvářené vlákno, kuželové pružiny bez rozkmitání).

- odkarbonování výfukových oken: šroubované otvory, ~10 minut, bez demontáže,
- modul generátoru: uzavřená bezúdržbová kazeta, mění se jako celek,
- periferie (svíčky, ventily, kroužky, vstřikovač, škrticí těleso): sériově dostupné
  díly,
- diagnostika za provozu: 3 zdroje polohy, lambda, klepání, tlaky, teploty.

---

## 19. Použití

*Přehled v ch. 2 (Celková architektura). Podrobnosti níže.*

- **Stacionární generátor / range extender** — primární cíl (1–1,5 kW elektrických),
- **drony / letectví** — těžké palivo, proudění vzduchu od vrtule, sběrnice ~100 V,
- **lehká vozidla:** motor v **centrální páteřové rouře** (koncepce Tatra, ale
  bez hnacích hřídelí — ven vycházejí jen kabely): nejlépe chráněné místo, hmota nízko
  a uprostřed, podélné vibrace pohltí hmota vozidla; více modulů
  v protifázi = vyvážení + škálování výkonu; sání shora, chladicí vzduch
  vyfukovaný dolů (snížená tepelná stopa korby),
- sériový hybrid: generátor pokrývá **průměrnou** spotřebu, baterie pokrývá **špičky** —
  modul ~40 kW × N.

---

## 20. Bezpečnost zabudovaná do konstrukce

*Přehled v ch. 2 (Celková architektura). Podrobnosti níže.*

- ventily v pístu = **zpětné ventily**: zpětné šlehnutí shora je zavře →
  plamen se nemůže dostat do prostoru náplně a ke generátoru (konvenční dvoutakt
  takovou ochranu nemá),
- sací ventil v přepážce = druhá zpětná bariéra,
- vinutí: vakuově impregnovaná, třída H — v prostoru generátoru je přítomna
  palivová mlha; uvnitř nejsou žádné jiskřící díly (žádný komutátor, MOSFETy vně),
- odolnost vůči mezním stavům: detonace, přejetí pístu, nekontrolovaný nárůst amplitudy —
  ocelová vložka, zapuštěná svíčka, masivní klouby,
- křížově propojené GPIO vypínání obou jednotek, zotavovací cyklus po vynechání zapalování,
- hardwarový mrtvý čas ve výkonovém stupni.

---

*Tento dokument je živý — každá kapitola bude zpřesňována, jak budou simulace a
zkoušky prototypu přinášet výsledky. Konkrétní námitky jsou vítány v Issues.*

★ Viva La Resistánce ★
