# 🧙‍♂️ Mage's Journey

**Fabularna gra taktyczna osadzona w światach MTG — singleplayer, text-heavy, lore-driven.**

Gracz wciela się w Maga przemierzającego krainy zbudowane w 100% na lore kart Magic: The Gathering z własnej kolekcji. Po drodze spotyka potwory, werbuje je do drużyny i stawia czoła coraz potężniejszym wyzwaniom.

## 🎯 Założenia projektu

- **Lore Truthfulness** — każda karta MTG staje się postacią/monsterem opartym o jej prawdziwe lore, narrację i ilustrację
- **Monster Engine** — walka taktyczna oparta o sprawdzony system 4 domen, macierze wpływu, algorytm DVA i algebrę payloadów
- **Singleplayer RPG** — eksploracja świata, rozwój drużyny, progresja postaci
- **Text-heavy** — narracja tekstowa jest sercem gry, z opcjonalną wizualizacją 2D
- **Vanilla Web** — HTML + JS + CSS, hostowane na GitHub Pages, działa na desktop i iPad/iPhone

## 🏗️ Architektura

```
mtgcrawler/
├── docs/                    # Dokumentacja i GDD
│   └── GDD.md               # Game Design Document
├── src/
│   ├── engine/              # Port Monster Engine (domena, walka, payloady)
│   │   ├── domains.js       # Domeny, macierze 12×12
│   │   ├── dva.js           # Algorytm DVA (Defensive Valuation Algorithm)
│   │   ├── payloads.js      # Payloady (CON_DMG, HEAL, CC, DOT, RES...)
│   │   ├── combat.js        # Silnik walki
│   │   └── cooldowns.js     # System cooldownów
│   ├── game/                # Logika gry fabularnej
│   │   ├── world.js         # Świat, mapa, biomy
│   │   ├── explorer.js      # System eksploracji
│   │   ├── party.js         # Zarządzanie drużyną
│   │   ├── recruitment.js   # Mechanika rekrutacji potworów
│   │   └── mage.js          # Postać Maga (gracz)
│   ├── data/                # Dane gry
│   │   ├── cards/           # Baza kart MTG (JSON per set)
│   │   ├── biomes.js        # Biomy i ich właściwości
│   │   └── abilities.js     # Zdolności specjalne
│   └── ui/                  # Interfejs użytkownika
│       ├── renderer.js      # Renderowanie mapy i UI
│       ├── narrative.js     # Silnik narracji tekstowej
│       └── hud.js           # HUD i panele informacyjne
├── assets/
│   └── cards/               # Ilustracje kart (FOT, STD, KON)
├── index.html               # Punkt wejścia
├── css/
│   └── style.css            # Style
└── tests/                   # Testy jednostkowe
```

## 🎲 Mechaniki (dziedziczone z Monster Engine)

### System Domen
- **4 domeny per jednostka**: A (główna fizyczna), B (wspomagająca fizyczna), C (główna niefizyczna/tarot), D (wspomagająca niefizyczna/tarot)
- **12 żywiołów fizycznych**: Ogień, Woda, Ziemia, Powietrze, Metal, Elektryczność, Lód, Natura, Światło, Mrok, Eter, Zaraza
- **12 Wielkich Arkanów**: Mag, Kapłanka, Cesarz, Kochankowie, Rydwan, Sprawiedliwość, Pustelnik, Koło Fortuny, Wisielec, Śmierć, Diabeł, Wieża

### Walka (DVA)
- Algorytm Defensive Valuation Algorithm — dynamiczna obrona oparta o interakcję domen
- Rzuty k100, krytyki 1-5 (zawsze trafienie) i 96-100 (zawsze pudło)
- Sloty główne (A/C) = 100% BAC, sloty wspomagające (B/D) = 50% BAC

### Payloady
- `CON_DMG` — bezpośrednie obrażenia (cap 1.0, empowered 2.0)
- `HEAL` — leczenie (instant lub odroczone)
- `DOT/HOT` — efekty okresowe
- `CC` — kontrola tłumu (ROOT, STUN, SILENCE, DISARM)
- `CHARM/FEAR` — specjalne statusy
- `RES` — modyfikatory obrony
- `AOE` — efekty obszarowe
- `SETUP + EMPOWERED` — budowanie potężnych ataków
- `SACRIFICE` — poświęcenie HP za wzmocnienie

### Biomy (15 typów)
Łąki, Las Rzadki, Las Gęsty, Dżungla, Pogórze, Wysokie Góry, Bagna, Moczary, Step, Pustynia, Lądolód, Pustynia Bazaltowa, Ruiny, Wrzosowiska, Pola Uprawne

## 🆕 Nowe mechaniki (do zaprojektowania)

### Mag-Gracz
- Postać centralna, nie walczy bezpośrednio
- Zarządza drużyną potworów
- Zasób: **Mana** (odnawialna, służy do rekrutacji i specjalnych akcji)

### Eksploracja
- Mapa większa niż 10×10 (świat gry z wieloma regionami)
- Fog of War — odkrywanie terenu
- Losowe spotkania (encounters)
- Lokacje specjalne (dungeons, miasta, świątynie)

### Rekrutacja
- Pokonany potwór może zostać zwerbowany
- Koszt w manie zależny od siły potwora
- Limit drużyny (3-4 potwory jednocześnie?)
- Każdy potwór zachowuje swoje 4 zdolności i domeny

### Progresja
- Doświadczenie Maga → nowe zdolności specjalne
- Rozwój potworów? (nowe zdolności, ulepszenia?)
- Odblokowywanie nowych regionów

## 📊 Status

🚧 **Faza: Projektowanie i prototypowanie**

- [x] Monster Engine 6.0 — kompletna dokumentacja
- [x] Monster Engine 5.0 — implementacja Python (referencja)
- [ ] GDD — Game Design Document
- [ ] Port silnika na JavaScript
- [ ] Baza danych kart (import z kolekcji)
- [ ] Prototyp walki
- [ ] Prototyp eksploracji
- [ ] System rekrutacji
- [ ] Interfejs użytkownika

## 🛠️ Development

```bash
# Brak buildu! Otwórz index.html w przeglądarce
# lub użyj dowolnego serwera statycznego:
python3 -m http.server 8000
```

## 📜 Licencja

Projekt prywatny. Karty MTG © Wizards of the Coast.
