# 📜 Game Design Document — Mage's Journey

> **Wersja:** 0.3 (prototyp grywalny)
> **Ostatnia aktualizacja:** 2026-08-27
> **Status:** Prototyp — eksploracja + walka + rekrutacja działają

---

## 1. Wizja

Gracz wciela się w **Maga** — wędrownego czarodzieja przemierzającego krainy zbudowane na fundamentach lore kart Magic: The Gathering z jego prywatnej kolekcji (~400 kart, rosnąca baza).

Gra łączy:
- **Eksplorację** świata z fog-of-war i losowymi encounterami
- **Walkę taktyczną** opartą o Monster Engine (domeny, macierze, DVA, payloady)
- **Rekrutację** potworów do drużyny
- **Narrację tekstową** budowaną na lore każdej karty

### 1.1. Filary Projektowe

1. **100% Lore Truthfulness** — Każda postać/monster w grze jest materializacją prawdziwej karty MTG. Teksty, opisy, ilustracje i zachowania wynikają bezpośrednio z lore karty i jej settingu (Śródziemie, Dominaria, Ravnica, itd.)

2. **Immersja przez tekst** — Narracja tekstowa jest podstawowym nośnikiem doświadczenia. Walki, odkrycia, rekrutacje — wszystko opisywane bogatym, sugestywnym językiem.

3. **Balans matematyczny** — System walki dziedziczy sprawdzony model Monster Engine: algebra efektów gwarantuje, że każda jednostka jest fair, niezależnie od lore.

4. **Kolekcjonerska głębia** — Gracz widzi swoją kolekcję kart jako żywy bestiariusz. Każda nowa karta w kolekcji = nowy potwór do odkrycia.

---

## 2. Świat Gry

### 2.1. Struktura Świata

Świat podzielony jest na **Regiony**, z których każdy odpowiada innemu setowi/settingowi MTG:

| Region | Setting MTG | Charakter | Przykładowe karty |
|--------|-----------|-----------|-------------------|
| Eriador | Lord of the Rings (LTR) | Mroczne lasy, ruiny, góry | Dunland Crebain, Uruk-hai |
| *...kolejne regiony w miarę rozbudowy kolekcji...* |

### 2.2. Mapa

- **Hex grid** lub **square grid** — do ustalenia
- Rozmiar: ~30×30 na region (do ustalenia)
- Każde pole = biom (z 15 typów z Monster Engine)
- Fog of War — pola odkrywane w miarę eksploracji
- Dziedziczenie biomów (70/30 z Monster Engine)

### 2.3. Lokacje Specjalne

- **Wieże Magów** — safe houses, regeneracja many
- **Lochy** — wielopoziomowe dungeon crawle z bossami
- **Obozowiska** — miejsca odpoczynku drużyny
- **Portale** — przejścia między regionami
- **Ołtarze** — specjalne miejsca rekrutacji

---

## 3. Gracz: Mag

### 3.1. Tożsamość

Mag **nie walczy bezpośrednio**. Jest dowódcą, strategiem, rekruterem.

### 3.2. Zasoby

| Zasób | Opis | Regeneracja |
|-------|------|-------------|
| **Mana** (MANA) | Główny zasób — rekrutacja, specjalne akcje | Odnawia się w Wieżach Magów, po zwycięskich walkach |
| **Renoma** (RENOWN) | Prestiż — odblokowuje nowe możliwości | Za eliminacje, rekrutacje, eksplorację |
| **Wiedza** (LORE) | Zbierana z kart — odblokowuje sekrety | Za odkrycie nowych kart/potworów |

### 3.3. Zdolności Maga (do zaprojektowania)

Mag posiada własne zdolności specjalne, niezależne od potworów:
- **Rozkaz** — zmiana celu ataku potwora
- **Przyzwanie** — teleportacja potwora na inne pole
- **Bariera** — tymczasowa ochrona dla drużyny
- **Wgląd** — podgląd zdolności wroga

### 3.4. Progresja

- Nowe zdolności Maga odblokowywane za Renomę
- Zwiększanie limitu drużyny
- Nowe typy rekrutacji

---

## 4. Potwory (Karty MTG → Byty)

### 4.1. Materializacja

Każda karta MTG jest materializowana jako unikalny Byt z:
- **Nazwą** (z karty)
- **Bio** (z narracji karty)
- **Ilustracją** (z kolekcji — FOT/STD/KON)
- **4 Domenami** (A, B, C, D)
- **4 Zdolnościami** (A, B, C, D) — z lore i payloadem
- **CON = 5.0** (standard Monster Engine)

### 4.2. Baza Kart

Każda karta w kolekcji ma wpis w bazie:

```json
{
  "id": "1LTR",
  "name": "Dunland Crebain",
  "set": "LTR",
  "setting": "Śródziemie",
  "mv": 4,
  "colors": ["B"],
  "prompt": "Dynamiczna, mroczna scena bitewna...",
  "narrative": "Na skraju dunlandzkiego urwiska dwaj Uruk-hai...",
  "assets": {
    "FOT": "assets/cards/1LTR_FOT.jpg",
    "STD": "assets/cards/1LTR_STD.jpg",
    "KON": "assets/cards/1LTR_KON.jpg"
  }
}
```

### 4.3. Mapowanie Karta → Byt

Proces materializacji (do zaimplementowania):

1. **Kolory many → Domeny fizyczne (A, B):**
   - W (biały) → Światło, Metal
   - U (niebieski) → Woda, Powietrze, Lód
   - B (czarny) → Mrok, Zaraza, Eter
   - R (czerwony) → Ogień, Elektryczność
   - G (zielony) → Natura, Ziemia

2. **Zdolności karty → Domeny tarota (C, D):**
   - Kontrola (Tap) → Wisielec, Kapłanka
   - Destrukcja → Śmierć, Wieża, Diabeł
   - Wzmocnienie → Mag, Cesarz, Rydwan
   - Leczenie → Kapłanka, Kochankowie

3. **Lore → 4 zdolności** z opisem fabularnym i payloadem

---

## 5. Walka

### 5.1. System

Walka dziedziczy **100% mechanik** z Monster Engine:
- 4 domeny (A/B fizyczne, C/D tarot)
- Macierze 12×12
- Algorytm DVA
- Algebra payloadów (soft-capy, BAC, cooldowny)
- System Argos (kolejność aktywacji)
- Biomy (modyfikatory BAC)

### 5.2. Drużyna vs Przeciwnicy

```
┌─────────────────────────────┐
│     Drużyna Gracza          │  Przeciwnicy
│                             │
│  🧙 Mag (nie walczy)        │  👹 Potwór A
│  🐺 Potwór 1                │  👹 Potwór B
│  🦅 Potwór 2                │  👹 Potwór C
│  🗡️ Potwór 3                │
│                             │
└─────────────────────────────┘
```

### 5.3. Przebieg Walki

1. **Encounter** — gracz napotyka grupę potworów
2. **Deploy** — rozmieszczenie drużyny na mapie
3. **Walka** — tury z Argosem, AI kontroluje przeciwników
4. **Rozstrzygnięcie** — zwycięstwo: nagrody + opcja rekrutacji

### 5.4. Rola Maga w Walce

Mag stoi poza polem walki ale może:
- Wydawać **Rozkazy** (zmiana priorytetów AI)
- Używać **Zdolności Maga** (koszt many)
- Obserwować i planować

---

## 6. Rekrutacja (MECHANIKA DO ZAPROJEKTOWANIA)

### 6.1. Propozycja A: Rytaul Przyzwania

Po pokonaniu potwora, gracz może wydać Manę na rytuał:
- Koszt = MV karty × mnożnik
- Szansa sukcesu zależna od Renomy
- Nieudany rytuał = potwór ucieka

### 6.2. Propozycja B: Złamanie Woli

Walka nie zabija potwora, ale obniża jego CON do 1. Na tym etapie gracz może:
- **Zwerbować** (koszt many, pewny sukces)
- **Wyeliminować** (pewna renoma)

### 6.3. Propozycja C: Pact

Niektóre potwory (szczególnie czarne/czerwone) wymagają „paktu":
- Koszt w CON Maga (stałe obniżenie max_many)
- Gwarantowany werbunek
- Fabularne uzasadnienie w lore

**Do decyzji:** Który wariant (lub hybryda)?

---

## 7. Eksploracja

### 7.1. Ruch

- Mag porusza się po mapie (1 pole na turę? swobodny ruch?)
- Drużyna podąża za Magiem
- Każdy ruch może wywołać encounter

### 7.2. Encountery

| Typ | Szansa | Opis |
|-----|--------|------|
| **Walka** | 40% | Spotkanie z wrogimi potworami |
| **Neutralny** | 25% | Potwór neutralny — można rekrutować bez walki |
| **Pułapka** | 10% | Mechaniczna przeszkoda (obrażenia, status) |
| **Skarb** | 10% | Znalezisko (mana, lore, artefakt) |
| **Fabuła** | 15% | Tekstowe wydarzenie fabularne z wyborem |

### 7.3. Biomy i Eksploracja

Każdy biom wpływa na:
- Typ encounterów
- Modyfikatory walki (+/- BAC)
- Dostępne potwory do rekrutacji
- Teksty narracyjne

---

## 8. Interfejs Użytkownika

### 8.1. Styl

- **Text-first** — narracja tekstowa dominuje
- **Dark fantasy** — mroczna kolorystyka
- **Minimalistyczny** — czysty, czytelny
- **Responsywny** — desktop + iPad

### 8.2. Ekrany

1. **Ekran Eksploracji** — mapa + narracja + HUD
2. **Ekran Walki** — pole bitwy + log walki + panel Maga
3. **Ekran Drużyny** — karty potworów, statystyki, zdolności
4. **Ekran Kolekcji** — przeglądanie kart z ilustracjami
5. **Ekran Regionu** — wybór regionu/settingu

### 8.3. Ilustracje

- **FOT** (fotorealizm) — ekran kolekcji, tła
- **STD** (akwarela 16:9) — narracja, ekrany wydarzeń
- **KON** (karta referencyjna) — ekran walki, HUD

---

## 9. Technologia

### 9.1. Stack

- **HTML5** — struktura
- **Vanilla JavaScript (ES2022+)** — logika
- **CSS3** — style (dark theme, responsive)
- **localStorage** — zapis gry
- **GitHub Pages** — hosting

### 9.2. Brak zależności

- Zero frameworków
- Zero build tools
- Zero backendu

### 9.3. Struktura modułów (ES Modules)

```javascript
import { DVA, calculateHitChance } from './engine/dva.js';
import { PHYSICAL_MATRIX, TAROT_MATRIX } from './engine/domains.js';
import { resolvePayload } from './engine/payloads.js';
```

---

## 10. Roadmapa

### Phase 1: Fundamenty 🏗️
- [x] Struktura repozytorium
- [x] Port silnika Monster Engine na JS (domeny, DVA, biomy, jednostki)
- [x] Materializacja kart → byty gry (7 kart z 6 setów MTG)
- [x] Rejestr kart (card_registry.js)
- [ ] Import bazy 400 kart (wymaga danych od autora)

### Phase 2: Walka ⚔️
- [x] Prototyp walki z systemem DVA
- [x] AI przeciwników (losowe zdolności, targeting)
- [x] Narrator walki (tekstowe opisy)
- [x] Walka drużyna vs wielu wrogów
- [ ] Pełna implementacja wszystkich payloadów
- [ ] Lepsze AI (priorytetyzacja celów, taktyka)

### Phase 3: Eksploracja 🗺️
- [x] Generowanie mapy 30x30 z algorytmem dziedziczenia
- [x] Ruch gracza i fog of war
- [x] Encountery (walka, neutralne, pułapki, skarby, fabuła)
- [x] Biomy (15 typów z modyfikatorami)
- [x] Specjalne lokacje (Wieże Magów, Lochy, Portale, Ołtarze, Obozowiska)
- [ ] Większe regiony / świat z wieloma obszarami

### Phase 4: Gra 🎮
- [x] System rekrutacji (neutralne + po walce)
- [x] Drużyna (max 3 potwory, zarządzanie)
- [x] Statystyki gry (odkryte pola, walki, rekrutacje)
- [x] System many (regeneracja co 5 tur)
- [x] Save/Load (localStorage)
- [ ] Mag i jego zdolności specjalne
- [ ] Progresja (levele, nowe zdolności, większa drużyna)

### Phase 5: Polish ✨
- [x] Narrator (bogate opisy tekstowe)
- [x] Tooltips na mapie
- [x] Responsywność (desktop + iPad)
- [ ] Ilustracje (integracja FOT/STD/KON)
- [ ] Dźwięk/ambient
- [ ] Animacje walki
- [ ] Mini-mapa

---

## 11. Otwarte Pytania

1. **Rekrutacja** — który model (rytuał / złamanie woli / pakt)?
2. **Limit drużyny** — ile potworów jednocześnie? (3? 4? 5?)
3. **Mag w walce** — jakie zdolności? Jak silne?
4. **Śmierć Maga** — game over czy respawn?
5. **Progresja potworów** — czy mogą się rozwijać?
6. **Skala mapy** — ile regionów na start?
7. **Hex vs Square** — jaki typ gridu?
8. **Czas w grze** — turowy globalnie czy tylko w walce?
9. **Ilustracje** — jak je serwować? (osobny branch? LFS?)

---

## 12. Podjęte Decyzje Projektowe

### ✅ Rozstrzygnięte

1. **Typ gridu:** Square grid (30×30) — prostszy do implementacji, lepszy na mobile
2. **Limit drużyny:** 3 potwory jednocześnie — dobry balans między taktyką a prostotą
3. **Czas w grze:** Swobodny ruch w eksploracji + turowy w walce (auto-battle z narracją)
4. **Rekrutacja:** Hybryda — neutralne istoty za manę + pokonani wrogowie za manę po walce
5. **Mag w walce:** Nie walczy bezpośrednio, ale może wydawać rozkazy (do implementacji)
6. **Śmierć Maga:** Respawn w Wieży Magów z utratą renomy (do implementacji)
7. **Ilustracje:** Na razie placeholder — integracja FOT/STD/KON w późniejszej fazie

### 🔄 W toku

- Progresja Maga (system leveli)
- Zaawansowane AI walki
- Import bazy 400 kart

---

*Ten dokument jest żywy. Każda decyzja projektowa powinna być tu udokumentowana.*
