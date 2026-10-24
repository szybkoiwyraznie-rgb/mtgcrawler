# Dopasowanie tytułów misji do paska wyboru misji (v4.5, 2026-10-24)

## Zgłoszenie właściciela

Właściciel przysłał zrzut ekranu z PPSSPP: w dolnym pasku ekranu wyboru misji tytuł epizodu 2 („Ep. 2: Groźba czająca się pod ziemią”) wchodzi w plakietkę licznika misji. To jedyny zgłoszony ekran, ale przyczyna jest systemowa — długość tytułu, nie treść jednego napisu.

## Pomiar ze zrzutu

| Element | Wartość |
| --- | --- |
| Szerokość ekranu | 480 px (obraz 4,629×) |
| Początek tekstu tytułu | x = 167 px (obraz 774 px) |
| Początek plakietki `(8)` | x = 425 px (obraz 1969 px) |
| Tytuł 35 znaków | obraz 774–1935 px = 251 px ekranu |
| Średni krok znaku | ~7,17 px |
| Pojemność paska | ~36 komórek = ~258 px |

Wniosek: tytuł 36-komórkowy dotyka plakietki, więc limit ustawiono na **32 komórki**, czyli 4 komórki zapasu (~29 px) na dłuższy licznik (np. `(12)`).

## Audyt

Przejrzano **303** tytuły menu i **224** kopie w plikach `*_ext.dat`. **24** tytuły menu przekraczały 32 komórki (maksymalnie **38**, „Ep. 2: Groźba czająca się pod ziemią”). Wszystkie skrócono do ≤32 komórek razem z ich kopiami w panelu notki misji — **24** wierszy `mission_title` + **24** wiersze `mission_note` = **48** zmian źródłowo powiązanych w `config/pl/ui-mission-title-length-2026-10-24.json` (SHA-256 `f191db7d…8d64`). Pozostałe **255** tytułów jest bajt w bajt bez zmian.

Kryteria skracania: zachować prefiks epizodu (`Ep. N`, `Ep. N-M`, `SIM:`) i unikalny człon rozpoznawczy; usuwać powtórzenia i ozdobniki („czająca się pod ziemią” → „pod ziemią”), nie skracać nazw własnych, nie zmieniać sensu. Tytuły spoza paska — linie `note_a`/`note_b` w treści panelu oraz `bgm_title` — należą do innych paneli i pozostały nietknięte.

## Zmiany

| # | Identyfikator | Przed | Po | Komórki przed → po |
| --- | --- | --- | --- | --- |
| 1 | `mission_title:config00.cpk/milstP00.bin:r14:title` | Ep. 2: Groźba czająca się pod ziemią | **Ep. 2: Groźba pod ziemią** | 36 → 24 |
| 2 | `mission_title:config01.EDAT/milstP01.bin:r9:title` | Ep. 3-1: Zbrojna interwencja Gundamów | **Ep. 3-1: Interwencja Gundamów** | 37 → 29 |
| 3 | `mission_title:config01.EDAT/milstP01.bin:r10:title` | Ep. 3-2: Skradający się czarny cień | **Ep. 3-2: Skradający się cień** | 35 → 28 |
| 4 | `mission_title:config01.EDAT/milstP01.bin:r30:title` | SIM: Bitwa mobile suitów na lądzie | **SIM: Bitwa MS na lądzie** | 34 → 23 |
| 5 | `mission_title:config02.EDAT/milstP02.bin:r16:title` | Rzekoma członkini Czarnych Rycerzy | **Rzekoma Czarna Rycerka** | 34 → 22 |
| 6 | `mission_title:config02.EDAT/milstP02.bin:r28:title` | Ep. 9-2: Śmiertelny bój z Riemannem | **Ep. 9-2: Bój z Riemannem** | 35 → 24 |
| 7 | `mission_title:config03.EDAT/milstP03.bin:r13:title` | Ep. 11-3: Leże Imperium Mechanizacji | **Ep. 11-3: Leże Imperium** | 36 → 23 |
| 8 | `mission_title:config03.EDAT/milstP03.bin:r28:title` | Ep. 13-2: Stolica imperium w ogniu | **Ep. 13-2: Stolica w ogniu** | 34 → 25 |
| 9 | `mission_title:config03.EDAT/milstP03.bin:r30:title` | Święty wojownik upadłego królestwa | **Wojownik upadłego królestwa** | 34 → 27 |
| 10 | `mission_title:config04.EDAT/milstP04.bin:r19:title` | Pragnący wskrzesić demonicznego boga | **Pragnący wskrzesić boga** | 36 → 23 |
| 11 | `mission_title:config05.EDAT/milstP05.bin:r11:title` | Ep. 19-1: Przełamanie obrony Axis | **Ep. 19-1: Przełamanie Axis** | 33 → 26 |
| 12 | `mission_title:config05.EDAT/milstP05.bin:r12:title` | Ep. 19-2: Szturmowy desant na Axis | **Ep. 19-2: Desant na Axis** | 34 → 24 |
| 13 | `mission_title:config05.EDAT/milstP05.bin:r17:title` | Uderz w bazę zaopatrzeniową wroga | **Uderz w bazę zaopatrzenia** | 33 → 25 |
| 14 | `mission_title:config05.EDAT/milstP05.bin:r29:title` | Ep. 21-2: Ostateczna forma Goburikiego | **Ep. 21-2: Ostateczny Goburiki** | 38 → 29 |
| 15 | `mission_title:config06.EDAT/milstP06.bin:r4:title` | Ep. 22-3: Devil Gundam, ostatnia runda | **Ep. 22-3: Devil Gundam, finał** | 38 → 29 |
| 16 | `mission_title:config06.EDAT/milstP06.bin:r29:title` | Operacja: schwytanie uśpionych Zoidów | **Operacja: uśpione Zoidy** | 37 → 23 |
| 17 | `mission_title:config07.EDAT/milstP07.bin:r3:title` | Ep. 26-3: Odrodzenie Ultrasaurusa | **Ep. 26-3: Powrót Ultrasaurusa** | 33 → 29 |
| 18 | `mission_title:config07.EDAT/milstP07.bin:r6:title` | Poszukiwanie Imperium Mechanizacji | **Poszukiwanie Imperium** | 34 → 21 |
| 19 | `mission_title:config07.EDAT/milstP07.bin:r9:title` | Ep. 27-1: Ku Zamkowi Mechanizacji | **Ep. 27-1: Zamek Mechanizacji** | 33 → 28 |
| 20 | `mission_title:config07.EDAT/milstP07.bin:r10:title` | Ep. 27-2: Groza! Gniew Kikaishina | **Ep. 27-2: Gniew Kikaishina** | 33 → 26 |
| 21 | `mission_title:config07.EDAT/milstP07.bin:r26:title` | Ep. 29-2: Natarcie Death Stingera | **Ep. 29-2: Atak Death Stingera** | 33 → 29 |
| 22 | `mission_title:config08.EDAT/milstP08.bin:r3:title` | Ep. 30-3: Death Saurer, bestia zagłady | **Ep. 30-3: Death Saurer** | 38 → 22 |
| 23 | `mission_title:config08.EDAT/milstP08.bin:r9:title` | Ep. 31-1: Starcie!! Forteca Invaderów! | **Ep. 31-1: Forteca Invaderów!!** | 38 → 29 |
| 24 | `mission_title:config08.EDAT/milstP08.bin:r10:title` | Ep. 31-2: Błysk!! U kresu ewolucji! | **Ep. 31-2: Błysk!! Kres ewolucji** | 35 → 31 |
| 25 | `mission_note:eventP01.EDAT/DL103_11_ext.dat:r0:title` | Ep. 3 / Zbrojna interwencja Gundamów | **Ep. 3 / Interwencja Gundamów** | 28 → 20 |
| 26 | `mission_note:eventP01.EDAT/DL103_12_ext.dat:r0:title` | Ep. 3 / Skradający się czarny cień | **Ep. 3 / Skradający się cień** | 26 → 19 |
| 27 | `mission_note:eventP01.EDAT/SM002_ext.dat:r0:title` | Symulator / Bitwa mobile suitów na lądzie | **Symulator / Bitwa MS na lądzie** | 29 → 18 |
| 28 | `mission_note:eventP02.EDAT/DL207_30_ext.dat:r0:title` | Rzekoma członkini Czarnych Rycerzy | **Rzekoma Czarna Rycerka** | 34 → 22 |
| 29 | `mission_note:eventP02.EDAT/DL209_12_ext.dat:r0:title` | Ep. 9 / Śmiertelny bój z Riemannem | **Ep. 9 / Bój z Riemannem** | 26 → 15 |
| 30 | `mission_note:eventP03.EDAT/DL311_13_ext.dat:r0:title` | Ep. 11 / Leże Imperium Mechanizacji | **Ep. 11 / Leże Imperium** | 26 → 13 |
| 31 | `mission_note:eventP03.EDAT/DL313_12_ext.dat:r0:title` | Ep. 13 / Stolica imperium w ogniu | **Ep. 13 / Stolica w ogniu** | 24 → 15 |
| 32 | `mission_note:eventP03.EDAT/DL313_25_ext.dat:r0:title` | Święty wojownik upadłego królestwa | **Wojownik upadłego królestwa** | 34 → 27 |
| 33 | `mission_note:eventP04.EDAT/DL415_70_ext.dat:r0:title` | Pragnący wskrzesić demonicznego boga | **Pragnący wskrzesić boga** | 36 → 23 |
| 34 | `mission_note:eventP05.EDAT/DL519_11_ext.dat:r0:title` | Ep. 19 / Przełamanie obrony Axis | **Ep. 19 / Przełamanie Axis** | 23 → 16 |
| 35 | `mission_note:eventP05.EDAT/DL519_12_ext.dat:r0:title` | Ep. 19 / Szturmowy desant na Axis | **Ep. 19 / Desant na Axis** | 24 → 14 |
| 36 | `mission_note:eventP05.EDAT/DL519_40_ext.dat:r0:title` | Uderz w bazę zaopatrzeniową wroga | **Uderz w bazę zaopatrzenia** | 33 → 25 |
| 37 | `mission_note:eventP05.EDAT/DL521_12_ext.dat:r0:title` | Ep. 21 / Ostateczna forma Goburikiego | **Ep. 21 / Ostateczny Goburiki** | 28 → 19 |
| 38 | `mission_note:eventP06.EDAT/DL622_13_ext.dat:r0:title` | Ep. 22 / Devil Gundam, ostatnia runda | **Ep. 22 / Devil Gundam, finał** | 28 → 19 |
| 39 | `mission_note:eventP06.EDAT/DL625_40_ext.dat:r0:title` | Operacja: schwytanie uśpionych Zoidów | **Operacja: uśpione Zoidy** | 37 → 23 |
| 40 | `mission_note:eventP07.EDAT/DL726_13_ext.dat:r0:title` | Ep. 26 / Odrodzenie Ultrasaurusa | **Ep. 26 / Powrót Ultrasaurusa** | 23 → 19 |
| 41 | `mission_note:eventP07.EDAT/DL726_35_ext.dat:r0:title` | Poszukiwanie Imperium Mechanizacji | **Poszukiwanie Imperium** | 34 → 21 |
| 42 | `mission_note:eventP07.EDAT/DL727_11_ext.dat:r0:title` | Ep. 27 / Ku Zamkowi Mechanizacji | **Ep. 27 / Zamek Mechanizacji** | 23 → 18 |
| 43 | `mission_note:eventP07.EDAT/DL727_12_ext.dat:r0:title` | Ep. 27 / Groza! Gniew Kikaishina | **Ep. 27 / Gniew Kikaishina** | 23 → 16 |
| 44 | `mission_note:eventP07.EDAT/DL729_12_ext.dat:r0:title` | Ep. 29 / Natarcie Death Stingera | **Ep. 29 / Atak Death Stingera** | 23 → 19 |
| 45 | `mission_note:eventP08.EDAT/DL830_13_ext.dat:r0:title` | Ep. 30 / Death Saurer, bestia zagłady | **Ep. 30 / Death Saurer** | 28 → 12 |
| 46 | `mission_note:eventP08.EDAT/DL831_11_ext.dat:r0:title` | Ep. 31 / Starcie!! Forteca Invaderów! | **Ep. 31 / Forteca Invaderów!!** | 28 → 19 |
| 47 | `mission_note:eventP08.EDAT/DL831_12_ext.dat:r0:title` | Ep. 31 / Błysk!! U kresu ewolucji! | **Ep. 31 / Błysk!! Kres ewolucji** | 25 → 21 |
| 48 | `mission_note:eventP00.cpk/DL102_11_ext.dat:r0:title` | Ep. 2 / Groźba czająca się pod ziemią | **Ep. 2 / Groźba pod ziemią** | 29 → 17 |

## Weryfikacja

- Każdy wiersz planu jest powiązany ze źródłem przez `source_sha256` (`pakiet_EN` i snapshot PL); narzędzie `tools/pl_story_corrections.py` nakłada plan asertywnie i odmawia pracy przy niezgodności.
- Po nałożeniu cały pakiet PL jest materializowany od zera (`109 176` wierszy, `108 805` wypełnionych, `371` pustych, `0` błędów, `4 176` ostrzeżeń — bez zmian względem v4.4).
- `tests/test_pl_mission_title_fit.py` (7 testów) sprawdza: plan i jego hash, brak tytułu >32 komórek w menu i kopiach, zachowanie prefiksów epizodu i unikalności tytułów, brak zmian w `note_a`/`note_b`/`bgm_title`, oraz to, że teksty w snapshocie dokładnie odpowiadają planowi.
- Snapshot: `data_sha256` `da2ad33f…e1f` → `788ab91c…62` (17. wpis w ledgerze planów UI).
- **Brak testu PPSSPP** — fix mierzy się jednym zrzutem ekranu wyboru misji epizodu 2; `runtime_tested` pozostaje `false`.

## Ryzyko szczątkowe

Jeśli na innym ekranie licznik misji jest dłuższy niż 4 komórki (np. trzycyfrowy), pasek może nadal się zetknąć; wtedy wystarczy obniżyć limit do 30 komórek w kolejnym planie — mechanizm i test już istnieją. Nie zaobserwowano żadnego innego panelu rysującego ten sam tytuł w innym rozmiarze.
