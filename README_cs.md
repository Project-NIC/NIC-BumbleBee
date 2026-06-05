<p align="center">
  <img src="NICBumble.svg" width="200"/>
</p>

*[English](README.md) · [Čeština](README_cs.md) · [Русский](README_ru.md)*

★ N.I.C. ★

# NIC-FPLG

## Lineární generátor s volným pístem — otevřený koncept

[![License: MIT](https://img.shields.io/badge/License-MIT-red.svg)](LICENSE)
[![Status: Koncept](https://img.shields.io/badge/Status-koncept-orange.svg)](OPEN-QUESTIONS.cs.md)

---

## Co je FPLG?

NIC-FPLG je otevřený koncept dvoutaktního dvouválcového lineárního motoru
s integrováným tubulárním lineárním generátorem. Žádná klíková hřídel.
Žádné vačky. Žádný rozvod. Dva pístý sdílejí jedinou tyč; generátor sedí
uprostřed tyče. Motor běží trvalé v jednom provozním bodě v mechanické
rezonanci; výkon se reguluje baterí, ne motorem.

Projekt vznikl z jednoduché úhy: klíková hřídel převádí lineární pohyb
na rotační jen proto, aby ho generátor převedl zpět na lineární.
Každý mezipřevod má ztráty a přidává složitost. FPLG tyto mezčlánky
vynechává.

---

## Proč ne klasický motor s klikovou hřídelcí?

- Provozní bod sleduje celou otačkovou mapu — každé palivo a každé zatížení vyžaduje vlastní kalibraci
- Klíková hřídel, vačky, rozvod, rozvodový řetěz — každý pohyblivý díl je potenciální závada
- Rezonance je nemožná — frekvence je svázaná s otačkami, ne s fyzikální soustavou
- Rozdîlná tepelná roztažnost materiálů vyžaduje těsné tolerance všude

## Proč ne rotační generátor?

- Lineární pohyb se převádí na rotační a zpět — dva mechanické převody, dvojnásobné ztráty
- Ložiska klíkové hřídele nesou plné spalovací zatížení pod úhlem
- Provoz na více paliv vyžaduje celou mapu otačky × zatížení pro každé palivo

## Proč lineární uspořádání s volným pístem?

- Jeden trvalý provozní bod — tři čísla na palivo místo celé mapy
- Rezonanční frekvence je dána geometrií: vzduchovová pružina (předkomprese pod pístó ~1:2) plus hmota tyče tvoří rezonátor — naladí se návrhem, ne softwarem
- Píst a vložka ze stejné třídy oceli — shodná tepelná roztažnost, konstantní vůle za všech teplot
- Geometrie dělá práci: kapkovité komůrky v čele pístu řídí proudění a roztočí náplň bez vačkového hřídele; setrvac̋nost ventilu přirozeně zpozdí přepouštění tak, aby výfuk odešel dřív

---

## Jak to funguje

### Jeden provozní bod

Motor nikdy nemění otačky. Baterie absorbuje veškerou proměnnou poptávku.
Přepnutí paliv (benzín / LPG / nafta+benzín) znamená změnu tří čísel
— předstih, směs, dávka oleje — ne přemapování celé tabulky.

### Mechanická rezonance

Předkomprese pod pístý (~1:2) tvoří vzduchovou pružinu. Vzduchová pružina
plus hmota tyče tvoří rezonátor. Provozní frekvence je dána objemem pod pístý
a hmotností tyče — naladí se návrhem, ne softwarem. Provoz v rezonanci
znamená, že vzduchová pružina vrací energii obratu pohybu zdarma; generátor
odebírá jen užitec̋nou práci.

### Výměna náplně

Žádné přepouštěcí kanály ve stěně válce. Přepouštění probíhá skrz ventily
v čele pístu — výfukové ventily ze závodní motorky (~16 mm), pracující
v chladné roli (omývané čerstvou směsí zdola). Kapkovité komůrky kolem
každého ventilu směřují náplň pod svíčku a roztočí píst při každém zápalu.
Setrvac̋nost ventilu vytváří přirozené fázové zpozdění — výfuk se otevře dřív,
přepouštění následuje.

### Generátor

Tubulární flux-switching stroj s hybridním buzením (~50 % permanentní magnety /
~50 % budicí vinutí). Magnety a cívky jsou ve statoru; tyč nese pouze pasivní
laminované zuby — minimální pohyblivá hmota, magnety v chlazené zóně.
Pole lze snížit téměř na nulu pro start a postupně zvyšovat pro regulaci výstupu.

---

## Dokumentace

| Dokument | Popis |
|---|---|
| [DESIGN-FPLG.cs.md](DESIGN-FPLG.cs.md) | Kompletní technický popis — 20 kapitol |
| [OPEN-QUESTIONS.cs.md](OPEN-QUESTIONS.cs.md) | Co nevíme — úkoly pro simulace a zkoušky |
| [SCHEMA-FPLG.svg](SCHEMA-FPLG.svg) | Schématický podélný řez (placeholder) |
| `calc/` | (připravováno) numerické modely — rezonance, cyklus |

---

## Stav

Fáze konceptu. Základní architektura a návrhová filozofie jsou definovány.
Simulace, výpočty a prototyp jsou dalším krokem.

Příspěvky vítány — simulace, dynamika, výroba, nebo kdokoliv, kdo najde
díru v úvaze. Konkrétní námitka je cennější než potlesk.

---

## Licence

MIT Licence — Copyright (c) 2026 NIC — Native Intellect Community

---

## Poděkování

Bráchovi za rady při vývoji tohoto projektu.
Za technickou oponenturu při rozpracování konceptu AI asistentovi Claude (Anthropic).

★ Viva La Resistánce ★
