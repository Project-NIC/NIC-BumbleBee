# NIC-FPLG — Technický popis konceptu

*Dvoutaktní dvouválcový lineární motor s integrovaným lineárním generátorem.*
*Stav: koncept. Hodnoty označené (TBD) čekají na simulaci či výpočet — viz [`OPEN-QUESTIONS.cs.md`](OPEN-QUESTIONS.cs.md). První 0D výsledky dynamiky jsou v [`calc/`](calc/) a jsou zapracovány do kapitol níže.*

---

## Stručné shrnutí

Dvoutaktní lineární motor bez klikové hřídele. Dva písty sdílejí jedinou tyč;
uprostřed tyče sedí tubulární lineární generátor. Motor běží trvale v jednom
provozním bodě a v mechanické rezonanci — frekvence je dána fyzikální soustavou,
ne řízením. Výkon soustavy se mění nabíjecím proudem baterie, nikoli otáčkami
nebo škrcením.

Klíčová myšlenka: funkce, které klasický motor řeší pohyblivými díly, tady dělá
geometrie. Kapkovité komůrky v čele pístu řídí proudění a roztáčejí náplň bez
vačkového hřídele. Setrvačnost ventilů tvoří asymetrické časování bez membrán.
Vzduchová pružina předkomprese nahrazuje setrvačník. Stroj je navržen tak,
aby mezní stavy přežil — ne aby se jim vyhýbal.

Cílový výkon ~3 kW mechanicky, 1–1,5 kW elektricky, životnost 10 000 hodin.
Použití: stacionární generátor, range extender, drony, lehká vozidla s páteřovou
trubkou. Kompletní technická architektura je popsána v kapitolách níže;
otevřené otázky a falzifikační scénáře v [`OPEN-QUESTIONS.cs.md`](OPEN-QUESTIONS.cs.md).

---

## 1. Filozofie návrhu

Pět zásad, které se opakují v každém detailu stroje:

1. **Geometrie řídí fyziku.** Funkce, které klasický motor řeší rozvodem,
   elektronikou nebo mapami, zde dělá tvar: tlakově řízené ventily, kapkovité
   trysky v čele pístu, setrvačnostně zpožděné přepouštění, rotace pístu
   z vyosení komůrek. Co nemá pohon ani software, to se nerozbije.
2. **Robustní místo křehkého.** Stroj se nevyhýbá mezním stavům — přežívá je.
   Ocelová celovložka a píst snesou detonaci i dolet pístu na dno vložky.
   Svíčka je zapuštěná pod úroveň, ventily v pístu fungují jako zpětné klapky
   proti prošlehnutí dolů.
3. **Jeden provozní bod.** Konstantní frekvence a zatížení ~50 % maxima.
   Žádné mapy, žádné přechodové stavy; baterie absorbuje vše proměnné.
4. **Tvářený materiál.** Vlákna sledují tvar: protlačovaná vložka (technologie
   nábojnic), zápustkově kovaný píst, válcované závity, válcovaná tyčovina.
   Únava při 10⁹ cyklech je hlavní nepřítel — tváření je hlavní zbraň.
5. **Servis zabudovaný do konstrukce.** Dekarbonizační porty bez demontáže,
   generátor jako výměnný kartridž, díly ze sériové produkce (ventily, svíčky,
   klapka, zapalovací modul) — opravitelnost z vrakoviště.

---

## 2. Architektura celku

```
        svíčka                                                svíčka
          ↓                                                     ↓
   ┌──────┴───────┐   ┌──────┐  ┌─────────────┐  ┌──────┐  ┌───────┴──────┐
   │ VLOŽKA L     │   │PŘEPÁŽ│  │  GENERÁTOR  │  │PŘEPÁŽ│  │     VLOŽKA P │
   │  [PÍST L]====│===│=KA===│==│====TYČ======│==│===KA=│==│====[PÍST P]  │
   │   ventily    │   │futro │  │ zuby+stator │  │futro │  │   ventily    │
   └──────┬───────┘   └──┬───┘  └─────────────┘  └──┬───┘  └───────┬──────┘
      výfukové         sací ventil   ↑ sání      sací ventil    výfukové
      otvory (obvod)   (velký)    (přes generátor) (velký)      otvory (obvod)
```

- **Dva písty na jedné tyči** — pohybují se společně (není to boxer).
  Výbuch na jedné straně = komprese na druhé straně + předkomprese
  pod oběma písty.
- **Tyč** = nerezová trubka (austenit, nemagnetická), uprostřed nese
  laminované zuby generátoru, na koncích našroubované koncovky
  s polokulovými čepy pístů.
- **Tělo** = hliníkový odlitek/výlisek ze dvou dílů; tvoří přepážky
  předkompresních komor, nese futra (vedení tyče) a uvnitř stator generátoru.
  Hliník slouží primárně jako chladič — nosnou pevnost dodávají ocelové
  vložky zalisované uvnitř.
- **Vložky** („celovložka", pracovně „kondomová hlava") = hlava + válec
  v jednom kuse tvaru nábojnice: příruba (≥8 šroubů k tělu), válec, zúžené
  hrdlo se závitem svíčky. Kolem každé vložky obvodové nerezové výfukové
  potrubí, vše zalisováno do hliníku.

**Tok směsi (jednosměrná dálnice):** škrticí klapka → prostor generátoru
(směs chladí cívky a magnety, olejová mlha maže futra) → velký sací ventil
v přepážce → předkompresní komora pod pístem (víření, chlazení dna pístu,
homogenizace s mazivem) → přepouštěcí ventily v pístu → kapkovité komůrky →
spalovací prostor → shoření → obvodové výfukové otvory → Y → tlumič.
Směs nikde nependluje; každý kubík vzduchu cestou odpracuje čtyři funkce
(chlazení, mazání, předkomprese, spalování).

**Aplikace:** stacionární generátor / range extender (primární cíl), drony
a letecké užití (heavy fuel, ~100 V sběrnice), lehká vozidla s motorem
v centrální páteřové trubce (elektrický pohon kol, více modulů za sebou
v protifázi = vyvážení + škálování výkonu). Koncept se vyplatí do ~40 kW
na modul; nad to lépe klasická rotační soustrojí.

**Bezpečnost zabudovaná do architektury:** ventily v pístu jsou jednosměrné —
backfire shora je zavře, plamen neprojde do prostoru směsi a generátoru.
Sací ventil v přepážce je druhá zpětná bariéra. Vinutí generátoru je
impregnované (vakuová impregnace, třída H); uvnitř nejsou jiskřící části.
Křížové GPIO vypínání obou ECU zajistí, že porucha generátoru zastaví motor
a misfire odbrzdí amplitudu bez tvrdého pádu. Robustnost na detonaci
a dolet pístu je záměr, ne nehoda — ocelová celovložka a zapuštěná svíčka
jsou tam přesně proto.

---

## 3. Pracovní cyklus a výměna náplně

Dvoutakt bez přepouštěcích kanálů ve stěně válce — přepouštění jde **skrz píst**.

1. **Expanze L / komprese P.** Výbuch vlevo žene tyč doprava. Pravý píst
   stlačuje náplň nad sebou; oba písty zároveň stlačují čerstvou směs
   pod sebou (předkomprese cílově ~2,5:1 — zvýšeno z původních ~1:2, aby stock
   přepouštěcí ventil dostal dost otevírací síly při slabé pružince, viz kap. 5
   / `calc/`; sací ventily v přepážkách zavřené).
2. **Výfuk L.** Levý píst odkrývá obvodové výfukové otvory; spaliny odcházejí
   po celém obvodu do prstencového potrubí. Horní hrana otvorů = jediné
   pevné časování stroje (TBD — ladí se frézováním hrany směrem nahoru).
3. **Přepouštění L.** Když tlak pod pístem překoná tlak nad pístem + sílu
   pružiny + setrvačnou sílu, otevřou se ventily v pístu. Setrvačnost ventilu
   (řádově srovnatelná s tlakovou silou — viz kap. 5) otevření **zpozdí za
   dolní úvrať** → výfuk napřed, přepouštění potom = asymetrické časování
   zadarmo, bez membrán a přívěr.
4. **Vnitřní EGR.** Část horkých spalin záměrně zůstává: jsou inertní
   (bez kyslíku), flash-odpařují palivo, ředí směs na obvodu, snižují
   teplotu hoření (NOx) i únik HC.
5. Tyč se vrací — role stran se prohodí. Synchronizaci drží fyzika:
   silnější výbuch na jedné straně zvýší kompresi (a tedy i ráznost
   výbuchu) na straně druhé; jemnou regulaci amplitudy dělá zátěž
   generátoru (kap. 12).

---

## 4. Spalovací prostor

- **Rovné dno vložky proti rovnému čelu pístu**, mezera v horní úvrati
  ~1 mm (TBD) → **plnoplošný squish**: směs z obvodu je vytlačena do středu,
  vzniká turbulence, na okraji nezůstává koncová směs náchylná k detonaci.
- **Komůrka svíčky** ve zúženém hrdle vložky; závodní svíčka se sníženou
  délkou, elektroda zapuštěná 0,1 mm pod úroveň dna → dolet pístu na hlavu
  svíčku nezničí.
- **Kapkovité komůrky v čele pístu** (kap. 5) drží hlavní objem bohaté
  směsi pod svíčkou → **stratifikované plnění**: bohatě u svíčky, chudě
  a inertně (spaliny) na obvodu. Obvod = místo výfukových otvorů → uniká
  přednostně spálený plyn, ne čerstvá směs.
- **Průběh hoření:** zážeh v komůrce svíčky → plamen šlehne do kapek →
  postupné, pomalé prohořívání řízené geometrií; vyosení kapek roztáčí
  náplň (a reakcí píst). Záměrně **bez detonace** — pomalé prohořívání,
  ne rázové hoření.

**Efektivní komprese závisí na amplitudě, ne jen na geometrii (calc):**
geometrický poměr je jen horní mez. *Trapovaná* komprese závisí na tom, jak
blízko se píst skutečně dostane k hlavě, což určuje provozní amplituda (zátěž
generátoru, kap. 12). [`calc/compression.py`](calc/compression.py) ukazuje, že
provoz od 17 mm do 23 mm amplitudy (rezerva k hlavě 8 → 2 mm) zvedne efektivní
poměr ~3,2 → ~5,6 a tepelnou účinnost ~25 % → ~33 %, za cenu špičkového tlaku
(~20 → ~29 bar). Účinnost je tedy hlavně rozhodnutí o amplitudovém setpointu:
řízení má držet amplitudu tak blízko hlavě, jak dovolí squish vůle a limit
špičkového tlaku — což je přesně to, co plnoplošný squish výše chce (píst skoro
líbá dno).

---

## 5. Píst, ventily, kapkovité trysky

**Píst:** ocel stejné třídy jako vložka (shodná tepelná roztažnost →
konstantní vůle za všech teplot → jednodušší kroužky, stálé těsnění).
Zápustkový výkovek (vlákna sledují tvar; prototyp obrobený z kované
tyčoviny). Tři pístní kroužky — měkčí materiál, silný průřez, **zaoblené
hrany**; tlak předkomprese zespodu vtlačuje směs s olejem mezi kroužky →
trvalá cirkulace maziva kroužkovou partií.

**Přepouštěcí ventily:** 2× výfukový ventil ze závodní motorky, ⌀ ~16 mm,
tenká stopka ~4 mm, žáruvzdorná slitina. U nás pracují v „chladné" roli —
omývané čerstvou směsí zespodu, s obrovskou rezervou. Uložení:

- vodítka (futra) nalisovaná zezadu do pístu,
- **kuželová (kónická) pružina** — progresivní, stlačitelná na plocho
  (minimální zástavba), bez ostré vlastní frekvence → odolná proti surge
  v trvale kmitajícím prostředí. Předpětí v sedle **slabé (~1 N)**: pružina
  ventil jen posadí, práci dělá dynamika plynu,
- klasická miska + kuželíky z automobilového rozvodu.

**Silový rozpočet ventilu (pracovní čísla):** setrvačná síla na ventil
~25 g při ~890 m/s² ≈ 22 N; otevírací tlaková síla ≈ 20 N na 1 bar diference
na talíři ⌀16. Síly jsou **stejného řádu** → pružina se navrhuje proti
součtu (tlak − pružina − setrvačnost) a setrvačnost vědomě tvoří zpožděné
otevření (kap. 3). Každý gram hmoty ventilu mění bilanci o ~0,9 N.
**Ověřeno v [`calc/valves.py`](calc/valves.py):** se stock 25g ventilem,
pružinkou ~1 N a předkompresí ~2,5:1 vyjdou otevírací tlak (~32 N) a setrvačnost
(~35 N) srovnatelné dle očekávání a ventil se otevře **~36° za úvratí** —
„výfuk první, přepouštění druhé" zadarmo. Předkomprese je ladicí knoflík (víc →
otevře dřív), takže asymetrické časování dává poměr předkomprese, ne speciální
díl — žádný lehký ventil navíc není potřeba.

**Kapkovité komůrky (trysky):** kolem každého ventilu v čele pístu prohlubeň
tvaru kapky, hloubka 2–3 mm. U půlkruhové (široké) části jen ~0,1 mm mezera
mezi talířem a stěnou; směrem ke špičce se profil otevírá. **Talíř ventilu
je pohyblivou součástí trysky:** zdvih ventilu řídí *množství*, kapka řídí
*směr* — proud míří ke špičce bez ohledu na okamžitý zdvih. Dvě kapky proti
sobě, špičky vyosené mimo střed:

- hlavní proud směsi míří do středu pod svíčku (stratifikace),
- vyosení dává náplni rotaci → hoření rotuje → reakční moment pootáčí píst
  každý cyklus o malý úhel → **rovnoměrné opotřebení** kroužků, vedení
  i tepelné zatížení. Levý a pravý píst zrcadlově.

Výroba kapek: čelo pístu je přístupné → běžné 3osé frézování kulovou stopkou.

---

## 6. Polokulový čep (spojení píst–tyč)

Čep = výřez z koule ⌀ ~15 mm s prohnutím ~15° — jen dvě prohnuté plochy
proti sobě. Vlastnosti:

- velká kontaktní plocha → **rázová odolnost** (síly výbuchu jdou tlakem,
  ne střihem),
- dovoluje **naklápění pístu** vůči tyči (píst si sedne ve válci, soustava
  je staticky určitá — viz kap. 8, „samosrovnání"),
- **prokluz při rotaci pístu je pomalý** (výsledné otáčky pístu řádově
  jednotky ot./min) → režim mezného mazání,
- oba povrchy nitridované, s mikrodrážkami; drážky se před každým
  přepuštěním plní směsí s olejem → samomazné kluzné ložisko
  (analogie vačka–zdvihátko, podmínky příznivější).

---

## 7. Tyč a spoje

**Tyč:** trubka z austenitické nerezi (304/316 — podmínka: nemagnetická;
pozor na deformační martenzit u tažených trubek, řeší žíhání).

- trubkový průřez = nejlepší tuhost/hmotnost → lehká pohyblivá soustava,
- nerez = nízká tepelná vodivost → tyč nevede teplo z pístů do generátoru,
- nemagnetická → magnetický tok teče výhradně laminovanými zuby.

**Koncovky s čepy:** našroubované. Klíčové detaily pro 10⁹ cyklů:

- **levý a pravý závit orientované proti smyslu rotace tyče** → vlastní
  pootáčení pístů spoje trvale dotahuje (pojistka zadarmo),
- **dosedací čelo** — tlaková půlvlna jde čelem na čelo, závit ji nevidí,
- **předpětí nad maximální provozní tah** — spoj se za provozu nerozevírá,
  závity nesou jen statické předpětí (princip šroubů ojnic),
- **válcovaný jemný závit** (ne řezaný) — zpevněný povrch, tlaková zbytková
  napětí, 3–5× únavová životnost,
- rádiusy na všech přechodech, výběhy závitů bez ostrých zápichů,
- vysokoteplotní anaerobní lepidlo jako druhá pojistka,
- série: zápustkové výkovky koncovek (vlákna kopírují čep); prototyp:
  válcovaná tyčovina (podélná vlákna vyhovují osovému zatížení).

Pozn.: délka závitu nad ~1,5×⌀ již nepomáhá (první závit nese 30–40 % síly);
rozhoduje předpětí a čelo, ne délka.

---

## 8. Lineární generátor

**Topologie: tubulární flux-switching stroj s hybridním buzením.**

- **Magnety i cívky ve statoru** — mezi pólovými nástavci skládanými
  z plechů 0,3 mm. Pohyblivá část (tyč) nese pouze pasivní feromagnetické
  zuby → minimální pohyblivá hmota, magnety v chlazené zóně.
- **Zuby tyče:** plechy 0,3 mm nalisované přes izolační kroužek na rozšířenou
  část trubky, zalité epoxidem. Laminace = potlačení vířivých proudů
  (tok v zubech se přepíná). Pozor: epoxid teplotní třídy ≥150 °C
  (systémy pro elektromotory); izolační kroužek z materiálu odolného creepu
  (PEEK / plněný PA) — trvale lisovaný spoj na 10 000 h.
- **Tubulární uspořádání:** radiální magnetické síly se vyruší symetrií
  (tyč „plave" v magnetickém středu, futra nesou minimum) a zuby jsou
  rotačně symetrické prstence → **jediná topologie slučitelná s rotací
  tyče**. Rotace pístů (kap. 5) a volba stroje se navzájem podmiňují.
- **Dvojnásobný počet zubů** → dvojnásobná elektrická frekvence (cíl ~100 Hz)
  → poloviční tok na stejné napětí (e = N·dΦ/dt) → dvě cívky v zástavbě
  jedné → jednodušší usměrnění. Daň: ztráty v železe rostou s frekvencí —
  při 0,3 mm plechách v pořádku.
- **Hybridní buzení ~50 % PM / 50 % budicí vinutí:** pole lze zesílit,
  zeslabit i vyrušit. ⚠ **Demagnetizace:** budicí tok musí být veden
  paralelní cestou v železe **kolem** magnetů, ne skrz ně proti polarizaci
  (zvlášť za tepla). Magnety s vysokou koercitivitou (NdFeB grade SH/UH,
  příp. SmCo). Detail magnetického obvodu = kritický návrhový bod (TBD, FEM).
- **Futra** (kluzná pouzdra v přepážkách): pevné vedení tyče (průhyb od
  hmoty zubů), délka ~20 mm, vůle 0,05–0,1 mm → **štěrbinové těsnění**
  (průtok ~ vůle³): únik předkomprese v jednotkách procent a vrací se
  do sání. Stejný materiál jako tyč (konstantní vůle za tepla) + tvrdý
  povlak. **Futra zároveň centrují stator** — souosost tyč↔stator
  (vzduchová mezera!) je dána jediným dílem, ne řetězcem tolerancí.
- **Montáž / servis:** tyč → stator → dvě půlky těla s futry se zasunou
  do statoru a sešroubují. Generátor = **sealed-for-life kartridž**;
  po dožití (cíl 10 000 h) výměna celku.

---

## 9. Výfukový systém

- **Obvodové prstencové potrubí** kolem každé vložky (tvar „Q" s výstupem),
  celonerezové — teplo má odejít spalinami, ne se rozdávat motoru.
- **Proměnná tloušťka stěny (svařenec):** ~1 mm na straně ke kompresní
  komoře (úzký tepelný most podél stěny), ~3 mm na straně lisované do
  hliníku (odpor prostupu do chladiče + tuhost proti zborcení při lisování;
  kruhový průřez s 3 mm stěnou snese lisovací tlaky s rezervou).
- **Výfukové otvory: vrtané skrz** (hliník + obě stěny trubky + vložka),
  10–20 kruhových děr po obvodu kolmo k ose. Kruhová díra = bez koncentrací
  napětí; hrany otvorů **sražené a zaleštěné zevnitř** (ochrana kroužků),
  honování válce až po této operaci. Poměr otvor/můstek tak, aby kroužek
  vždy seděl na dostatečné ploše (TBD).
- **Dekarbonizační porty:** protilehlé díry po vrtání dostanou závit +
  šroub s měděným těsnicím kroužkem (anti-seize pasta). Vyšroubovat →
  proštětkovat otvor v ose → zašroubovat. Čištění bez demontáže;
  u dvoutaktu zásadní pro reálnou životnost.
- **Y spojka** obou prstenců do jednoho tlumiče. Výfukové pulzy se střídají
  (písty na společné tyči) → proud z jedné větve může ejektorovým efektem
  tvořit podtlak ve větvi druhé a podpořit její výplach. Funkce závisí
  na délkách větví vs. rychlost zvuku ve spalinách (~500–600 m/s) —
  **TBD, 1D simulace / experiment**; laditelné délkou potrubí.
- **„Otevřený" výfuk:** celkový objem ~10× zdvihový objem + ztrátový tlumič
  (~0,5 l, děrované přepážky) → minimální protitlak, žádné rezonanční
  vlny. Klasický dvoutakt potřebuje expanzní komoru, aby vracela uniklou
  směs — zde směs neuniká (stratifikace, kap. 4), takže laděná komora
  není nutná.
- **Ladění časování:** první vložku vrtat otvory záměrně **níž** (pozdní
  výfuk, dlouhá expanze) a horní hranu posouvat frézováním nahoru, dokud
  výplach nesedne. Jednosměrné ladění bez zničených vložek.

---

## 10. Tělo, chlazení, zalisování

- **Hliníkové tělo** s podélným žebrováním; prořezy žeber proti
  „banánovému efektu" (tepelná deformace). Hliník = chladič; minimum
  materiálu, pevnost dodávají ocelové inserty. Nálitky v zóně výfuku.
- **Zalisování insertů (squeeze casting / liquid forging):** vložka +
  výfukové potrubí se zalijí/zalisují rozžhaveným hliníkem ve formě.
  Hliník se při chladnutí smrští víc než ocel/nerez → trvalé **smršťovací
  sevření** = dokonalý tepelný kontakt i mechanické držení bez šroubů.
  - vložka při lisování podepřena **trnem** s keramickým separátorem,
  - trubka drží tvar tloušťkou stěny (3 mm na tlakové straně); alternativa
    solné jádro vyplavené vodou,
  - **honovat válec až PO zalisování** (sevření mění geometrii).
- **Chlazení vzduchem:** žebra = chladič; nasávaná směs chladí generátor
  zevnitř (a odpar paliva přidává). Nucený ofuk dle aplikace: vrtule
  (letecké užití), elektrické ventilátory řízené teplotou (vozidlo/stacionár);
  odpadní teplo do žeber řádově 2–4 kW při plném výkonu (TBD).

---

## 11. Palivový systém — multi-fuel

- **Vstřikování do sání** za škrticí klapku, do zóny turbulence (lepší
  rozprášení). Klapka i vstřikovač = sériové díly z motocyklu ~150 ccm
  (velká rezerva průtoku).
- **Oddělené vstřikování maziva:** dávkovací pulzní čerpadlo (typ Webasto);
  esterový („eko/bio") olej ředěný benzínem (viskozita v zimě, průchodnost
  tryskou). Dávka řiditelná dle zatížení. **Nutná podmínka pro LPG** —
  suchý plyn nemaže; olejová mlha v sání zároveň maže futra, čepy
  a kroužkovou partii.
- **Paliva:** benzín; LPG (propan–butan); nafta+benzín se zážehem
  („heavy fuel" — reálně používané u vojenských dronových motorů; ředění
  benzínem zlepšuje odpar a zápalnost). Lihová paliva vyřazena
  (nízká objemová výhřevnost).
- **Jeden provozní bod = jeden řádek parametrů na palivo** (předstih,
  dávka, dávka oleje) místo celé mapy. Přepnutí paliva je změna tří čísel.

---

## 12. Elektronika a řízení

**Architektura: 2 procesory** (STM32H503 — 250 MHz Cortex-M33, HW timery
s dead-time): ECU motoru + ECU generátoru. Komunikace stavů + **bezpečnostní
signály po dedikovaných GPIO** (hardwired, latence µs, žádný protokol).

**Křížová ochrana:**

- porucha generátoru (nadproud…) → GPIO → motor: zavřít klapku + vypnout
  zapalování; tyč bezpečně dokmitá naprázdno,
- vynechání zápalu → GPIO → generátor: **okamžitě shodit zátěž** → tyči
  zůstane energie na dokmit a další kompresi → *záchranný cyklus*
  (2–3 pokusy o zápal), teprve pak tvrdý stop.

**Snímání polohy — tři nezávislé zdroje pravdy:**

1. 4× vysokofrekvenční indukční čidlo skrz vložku (zapouzdřená, tlakuvzdorná),
   snímají písty **křížem** → poloha, rychlost, směr + vzájemná redundance,
2. průběh napětí cívek generátoru (poloha „zadarmo"),
3. knock senzor na bloku (detonace + nezávislá detekce misfire).

**Zapalování:** sériový dvoukanálový modul (např. Renault D4F740),
**dva nezávislé kanály — ZÁKAZ wasted spark:** protilehlý válec má v okamžiku
zážehu otevřený výfuk a čerstvou náplň; společná jiskra = riziko backfire.
Fázová informace z čidel je k dispozici, každá svíčka dostává impulz
ve svém čase. Předstih pevný + korekce teploty (jeden provozní bod).

**Směs:** širokopásmová lambda (LSU 4.9) pro ladění, skoková pro provoz;
bez katalyzátoru. Tlakové snímače před/za klapkou, teploty.

**Startovací sekvence:**

1. plné přebuzení (až ~200 %) → generátor v motorickém režimu rozkmitá tyč,
2. první zápaly na minimální směsi,
3. krátce vyrušit pole protiproudem → nulová elektromagnetická zátěž,
   ustálení kmitů „tlak na tlak" na chudé směsi (fáze držet co nejkratší —
   bez elektromagnetické brzdy hlídá amplitudu jen vzduchová pružina),
4. postupné přibuzování = spojitý náběh zátěže a bohatosti až do
   provozního bodu.

**Regulace amplitudy:** úvrať není dána geometrií, ale energetickou bilancí.
Hlavní akční člen = **zátěž/buzení generátoru** (elektromagnetická brzda,
odezva v ms). Tři nezávislé smyčky: směs (pomalá), buzení (rychlá),
předstih (korekční). **Ověřeno v [`calc/control.py`](calc/control.py):** zátěž
a směs dohromady drží konstantní frekvenci, zatímco se mění výkon — zátěž nese
změnu výkonu, směs dorovná frekvenci zpět — a smyčky zůstanou stabilní při
skokové změně výkonu i s reálným rozptylem zápalů. Jeden provozní bod drží tyhle
dvě smyčky, ne geometrie sama (viz kap. 14).

---

## 13. Elektrický výstup

- 2 cívky → usměrnění **2 MOSFETy** se synchronním řízením; budič
  s **hardwarovým dead-time** (STM32H5 má v timerech) — shoot-through
  nesmí záviset na software.
- **Kondenzátorová banka mezi usměrňovač a BMS** (řádově tisíce µF):
  BMS FETy a bočníky jsou stavěné na hladké DC; 100Hz pulzy bez vyhlazení
  zvyšují RMS ohřev a mohou falešně spouštět nadproudovou ochranu.
- BMS → trakční baterie. **Baterie = buffer i regulátor:** nabíjecí proud
  je spojitě říditelná veličina; výkon soustavy se mění tady, motor jede
  pořád stejně. Cíl ~100 V DC sběrnice, ~15 A při 1,5 kW.

---

## 14. Rezonanční provoz

Předkomprese pod písty tvoří **vzduchovou pružinu**; pružina + hmota
pohyblivé soustavy = rezonátor:

```
f = (1/2π)·√(k/m)
m … hmota pohyblivé soustavy (písty + tyč + zuby + koncovky)
k … tuhost vzduchové pružiny (objem pod písty, předkomprese, plocha pístu)
```

Postup návrhu je **obrácený**: zvolí se optimální spalovací frekvence →
zváží se soustava → **dopočítá se objem pod pístem** tak, aby rezonance
padla na zvolenou frekvenci. Provoz v rezonanci = vzduchová pružina vrací
energii obratu zdarma, generátor odebírá jen užitečnou práci.
(Korekce: netěsnost futer mírně snižuje efektivní tuhost — zahrnout.)

**0D výsledek ([`calc/`](calc/)):** obraz je jemnější než „frekvenci určuje
vzduchová pružina". Při 1 kg dá samotná vzduchová pružina jen ~10 Hz; dominantní
tuhost je **kompresní pružina spalování**, která závisí na tlaku, takže mezní
cyklus se sám usadí na **~40 Hz** při seed geometrii — nad původním odhadem
~30 Hz. Protože tuhost závisí na tlaku spalování, frekvence *není* daná
geometrií samotnou: drží ji konstantní regulační smyčky směs + zátěž (kap. 12).
Páky na cílovou frekvenci jsou hmota (f ∝ 1/√m), předkomprese a vrtání/zdvih —
vše sweepovatelné v `calc/`.

---

## 15. Vibrace a uložení

Oba písty se pohybují souhlasně → pohyblivá hmota kmitá nevyváženě.
Pracovní odhad: m ≈ 1 kg, zdvih 50 mm, 30 Hz → F ≈ 890 N @ 30 Hz. **0D výsledek
([`calc/`](calc/)):** při samočinně zvolených ~40 Hz je budicí síla blíž
**~1,4 kN**, a protože při konstantní amplitudě sleduje spalovací sílu,
s těžší hmotou *neklesá* — lehčí sestava je tedy lepší pro vibrace *i* výkon.
Dvoumodulové protifázové uspořádání vyruší čistou sílu ~88 % (1,4 kN → ~0,16 kN),
ale zůstane **klopný moment (~165 N·m při rozteči 120 mm)**, který nesou
silentbloky; koaxiální poskládání modulů ho zmenší.

- stacionární nasazení: masivní rám + silentbloky laděné hluboko pod
  provozní frekvenci (standard kompresorů),
- lehká tyč (trubka, zuby místo magnetů) problém zmenšuje u zdroje,
- **modulární řešení:** dva stroje vedle sebe v protifázi = úplné vyvážení
  + dvojnásobný výkon (přirozené pro páteřovou trubku, kap. 17).

---

## 16. Materiály a tepelný management

| Díl                  | Materiál                  | Důvod                                        |
| -------------------- | ------------------------- | -------------------------------------------- |
| Vložka + píst        | ocel, stejná třída        | shodná roztažnost → konstantní vůle          |
| Tyč                  | austenitická nerez, trubka| nemagnetická, tepelně izoluje, lehká         |
| Výfukové potrubí     | nerez, stěna 1/3 mm       | nízká λ; teplo odchází spalinami             |
| Tělo                 | hliník, žebrovaný         | chladič; smršťovací sevření insertů          |
| Zuby gen. + stator   | el. plechy 0,3 mm         | potlačení vířivých proudů                    |
| Magnety              | NdFeB SH/UH či SmCo       | koercitivita (vyrušování pole, teplo)        |
| Čepy, futra          | ocel + nitridace/povlak   | mezné mazání, rázy, konstantní vůle          |
| Ventily              | žáruvzdorná slitina (moto)| obrovská rezerva v „chladné" roli            |

Zásada tepelných toků: **spalovací teplo → hliník → vzduch; výfukové
teplo → spaliny → ven.** Nerez všude tam, kde teplo nemá přecházet
(potrubí, tyč); tloušťky stěn jako řízený tepelný odpor (kap. 9).

---

## 17. Výroba

**Prototyp (bez forem, proveditelné v EU):** vložka soustružená + honovaná
(po montáži), píst CNC z kované tyčoviny, potrubí svařenec, tělo obrobek
ze špalku + klasické nalisování za tepla, plechy laserem (na finále žíhat
hrany řezu), tyč z katalogové trubky, díly periferie ze sériové produkce.

**Série:** vložka zpětným protlačováním za studena (technologie nábojnic —
vlákna sledují tvar), píst zápustkový výkovek (forma „3D", minimum třísek;
tenké membrány mezi dutinami se jen profrézují), squeeze casting hliníku
kolem insertů (trn + keramický separátor; chladnutí sekundy), válcované
závity. Nástroje (zápustky, formy, přípravky) — realisticky Asie.

---

## 18. Servis a životnost

Cíl **10 000 h ≈ 10⁹ cyklů** → návrh řízený únavou (předpětí, válcování,
rádiusy, tvářená vlákna, kuželové pružiny bez surge).

- dekarbonizace výfukových otvorů: šroubové porty, ~10 minut, bez demontáže,
- generátorový modul: sealed-for-life kartridž, výměna celku,
- periferie (svíčky, ventily, kroužky, vstřikovač, klapka): běžné sériové
  díly,
- diagnostika za provozu: 3 zdroje polohy, lambda, knock, tlaky, teploty.

---

## 19. Aplikace

*Přehled viz kap. 2 (Architektura celku). Níže detaily.*

- **Stacionární generátor / range extender** — primární cíl (1–1,5 kW el.),
- **drony / letecké užití** — heavy fuel, ofuk vrtulí, ~100 V sběrnice,
- **lehká vozidla:** motor v **centrální páteřové trubce** (koncept Tatra,
  ale bez hřídelí — ven vedou jen kabely): nejchráněnější místo, hmota
  nízko v ose, podélné kmity pohlcuje hmotnost vozidla; více modulů
  za sebou v protifázi = vyvážení + škálování výkonu; sání shora, výdech
  chladicího vzduchu dolů (snížení tepelného kontrastu trupu),
- sériový hybrid: generátor kryje **průměr**, baterie **špičky** —
  modul ~40 kW × N.

---

## 20. Bezpečnost zabudovaná do konstrukce

*Přehled viz kap. 2 (Architektura celku). Níže detaily.*

- ventily v pístu = **zpětné klapky**: backfire shora je zavře → plamen
  neprojde do prostoru směsi a generátoru (klasický dvoutakt tuto ochranu
  nemá),
- sací ventil v přepážce = druhá zpětná bariéra,
- vinutí: impregnace tepl. třídy H (vakuová) — v prostoru generátoru je
  palivová mlha; uvnitř nejsou jiskřící části (bez komutátoru, MOSFETy vně),
- robustnost na mezní stavy: detonace, dolet pístu, přeběh amplitudy —
  ocelová celovložka, zapuštěná svíčka, masivní čepy,
- křížové GPIO vypínání obou jednotek, záchranný cyklus při misfire,
- HW dead-time ve výkonové větvi.

---

*Dokument je živý — každá kapitola se bude zpřesňovat podle výsledků
simulací a prototypových zkoušek. Konkrétní námitky vítány v Issues.*

★ Viva La Resistánce ★
