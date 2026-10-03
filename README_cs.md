<p align="center">
  <img src="NICBumble.svg" width="200"/>
</p>

★ N.I.C. ★

# NIC-FPLG

*[English](README.md) · [Čeština](README_cs.md) · [Русский](README_ru.md)*

*Závazná je anglická verze.*

## Lineární generátor s volným pístem — otevřený koncept

[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)
[![Status: Concept](https://img.shields.io/badge/Status-concept-orange.svg)](OPEN-QUESTIONS_cs.md)
[![Version: 0.5](https://img.shields.io/badge/version-0.5-blue.svg)](calc/)

---

## Co je FPLG?

NIC-FPLG je otevřený koncept dvoudobého dvouválcového lineárního motoru
s integrovaným trubkovým lineárním generátorem. Žádný klikový hřídel. Žádný vačkový
hřídel. Žádný ventilový rozvod. Dva písty sdílejí jednu pístnici; trubkový generátor
sedí uprostřed pístnice. Motor běží trvale v jednom pracovním bodě v mechanické
rezonanci; výkon reguluje baterie, nikoli motor.

Projekt vyrostl z jednoduchého postřehu: klikový hřídel převádí přímočarý pohyb
na rotační jen proto, aby ho v generátoru zase převedl zpět na přímočarý.
Každá mezilehlá přeměna znamená ztráty a složitost. FPLG prostředníka vynechává.

---

## Proč ne klasický motor s klikovým hřídelem?

- Pracovní bod se pohybuje po celé mapě otáček — každé palivo a každé zatížení potřebuje vlastní kalibraci
- Klikový hřídel, vačkový hřídel, ventilový rozvod, rozvodový řetěz — každý pohyblivý díl je možný zdroj poruchy
- Rezonance je nemožná — frekvence je svázána s otáčkami, ne s fyzikálním systémem
- Rozdílná tepelná roztažnost nestejných materiálů vyžaduje všude úzké tolerance

## Proč ne rotační generátor?

- Přímočarý pohyb se převádí na rotační a zpět — dvě mechanické přeměny, dvě sady ztrát
- Ložiska klikového hřídele nesou plné zatížení od spalování pod úhlem
- Provoz na více paliv vyžaduje pro každé palivo úplnou mapu otáčky × zatížení

## Proč konstrukce s volným pístem a lineárním generátorem?

- Jeden trvalý pracovní bod — tři čísla pro každé palivo místo celé mapy
- Rezonanční frekvenci určuje geometrie: vzduchová pružina (podpístová předkomprese ~1:2) spolu s hmotností pístnice tvoří rezonátor — naladěný konstrukcí, ne softwarem
- Píst a vložka válce ze shodné slitiny — stejná tepelná roztažnost, konstantní vůle při všech teplotách
- Práci odvádí geometrie: kapkovité kapsy v čele pístu usměrňují proudění a roztáčejí náplň bez vačkového hřídele; setrvačnost ventilů zpožďuje přepouštění, takže výfukové plyny odcházejí jako první

---

## Jak to funguje

### Jeden pracovní bod

Motor nikdy nemění otáčky. Veškerou proměnlivou poptávku pokrývá baterie.
Změna paliva (benzín / LPG / nafta+benzín) znamená změnu tří čísel
— předstihu, směsi, dávky oleje — nikoli přemapování celé tabulky.

### Mechanická rezonance

Podpístová předkomprese (~1:2) tvoří vzduchovou pružinu. Vzduchová pružina spolu
s hmotností pístnice tvoří rezonátor. Pracovní frekvenci určuje objem pod písty
a hmotnost pístnice — je naladěná konstrukcí, ne softwarem. Provoz v rezonanci
znamená, že vzduchová pružina vrací energii obratu zadarmo; generátor odebírá jen
užitečnou práci.

### Přepouštění náplně

Ve stěně válce nejsou žádné přepouštěcí kanály. Přepouštění probíhá ventily v čele
pístu — výfukovými ventily ze závodních motocyklů (~16 mm), které zde pracují ve
studené roli (omývá je zespodu čerstvá směs). Kapkovité kapsy kolem každého ventilu
směřují náplň ke svíčce a při každém pracovním zdvihu udělují pístu rotaci.
Setrvačnost ventilů vytváří přirozené fázové zpoždění — nejdřív se otevře výfuk,
pak následuje přepouštění.

### Generátor

Trubkový stroj s přepínáním toku a hybridním buzením (~50 % permanentní magnety /
~50 % budicí vinutí). Magnety i cívky sedí ve statoru; pístnice nese jen pasivní
lamelované zuby — minimální pohyblivá hmotnost, magnety v chlazené zóně.
Buzení lze pro start snížit téměř na nulu a pro regulaci výkonu ho postupně
zvyšovat.

---

## Dokumentace

| Dokument | Popis |
|---|---|
| [DESIGN-FPLG.md](DESIGN-FPLG_cs.md) | Úplný technický koncept — 20 kapitol |
| [OPEN-QUESTIONS.md](OPEN-QUESTIONS_cs.md) | Co nevíme — úkoly pro simulace a zkoušky |
| [calc/](calc/README_cs.md) | 0D modely — dynamika, rezonance, termodynamický cyklus, řízení — a co říkají jejich čísla |
| [CHANGELOG.md](CHANGELOG_cs.md) | Co se změnilo, vydání po vydání |

---

## Stav

**v0.5** — fáze konceptu. Základní architektura a filozofie konstrukce jsou
definované a klíčová čísla nyní podkládá 0D model dynamiky + termodynamiky (viz
[`calc/`](calc/)). Na řadě je 1D model výměny náplně / vyplachování, CFD
a prototyp.

Příspěvky jsou vítány — simulace, dynamika, výroba, nebo kdokoli, kdo najde díru
v úvahách. Konkrétní námitka má větší cenu než potlesk.

---

## Licence

MIT License — Copyright (c) 2026 NIC — Native Intellect Community

---

## Poděkování

Bratrovi za rady během vývoje tohoto projektu.
Za technickou oponenturu během vývoje konceptu AI asistentovi Claude (Anthropic).

★ Viva La Resistánce ★
