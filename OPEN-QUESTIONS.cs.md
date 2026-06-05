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
2. **Časování výfukových otvorů** — výška horní hrany vs. délka expanze
   vs. kvalita výplachu. Strategie: vrtat níž, ladit frézováním nahoru.
   Potřeba: 1D simulace výměny náplně, poté experiment.
3. **CFD výplachu a stratifikace** — udrží kapkovité trysky + squish
   skutečně bohatou zónu pod svíčkou a spaliny na obvodu? Klíčový
   emisní i účinnostní předpoklad celého konceptu.
4. **Vnitřní EGR** — kolik zbytkových spalin je optimum; ověřit, že odpar
   na horkých inertních spalinách nevede k samovznícení (hranice teplot).
5. **Ejektorový efekt v Y** — délky větví vs. fáze pulzů (rychlost zvuku
   ve spalinách ~500–600 m/s). Funguje podtlaková podpora výplachu,
   nebo je to zanedbatelné?
6. **Přestup tepla** — bilance: kolik do hliníku, kolik spalinami ven,
   ohřátí nasávané směsi průchodem přes generátor (ztráta plnění vs.
   zisk chlazení).

## B. Dynamika a rezonance

7. **Rezonanční frekvence soustavy** — f = (1/2π)√(k/m): dopočítat objem
   pod písty pro cílovou frekvenci; vliv netěsnosti futer na efektivní
   tuhost; vliv proměnné tuhosti vzduchové pružiny (nelinearita) na tvar
   kmitu. **První úloha pro `calc/`.**
8. **Hmotnost pohyblivé soustavy** — reálná čísla (písty + tyč + zuby +
   koncovky + podíl pružin); každý gram mění rezonanci i vibrace.
9. **Silový rozpočet pístových ventilů** — pružina vs. tlaková diference
   vs. setrvačnost v celém cyklu; velikost a stabilita setrvačnostního
   zpoždění otevření (asymetrické časování). Hmotnost konkrétních ventilů.
10. **Vibrace a uložení** — síly do rámu, návrh silentbloků; kdy přejít
    na dvoumodulové protifázové uspořádání.
11. **Chování při poruše** — dolet pístu na hlavu: energie rázu, napětí
    v čepu, závitech, přírubě vložky (jednorázově i opakovaně).

## C. Generátor a magnetika

12. **FEM magnetického obvodu** — geometrie vedení budicího toku **kolem**
    permanentních magnetů (ne skrz, proti polarizaci). Demagnetizační
    analýza za tepla = podmínka životnosti. Volba magnetů (NdFeB SH/UH
    vs. SmCo).
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
  zápalů → řízení se zásadně komplikuje.

Každá z těchto věcí se dá ověřit **dřív**, než se utratí peníze za výrobu.
Proto je tenhle soubor v repu na prvním místě.

---

★ Viva La Resistánce ★
