# Tytuły misji dopasowane do paska wyboru — PL v4.5 (2026-10-24)

Zgłoszenie właściciela ze zrzutem ekranu: w dolnym pasku ekranu wyboru misji tytuł
**„Ep. 2: Groźba czająca się pod ziemią”** wchodził na licznik misji **`(8)`**.
Polecenie: sprawdzić, czy inne misje mają ten sam problem, i skrócić tytuły, które
nie mieszczą się w pasku.

Plan źródłowy: `config/pl/ui-mission-title-length-2026-10-24.json`
(48 zmian, wszystkie w `05_mission_text.jsonl`). Plan jest autorytatywną listą
„przed/po”; ten dokument opisuje pomiar, zakres i walidację.

## Pomiar [ZWERYFIKOWANE z jednego zrzutu]

Zrzut właściciela: 2222 × 361 px, ekran PSP 480 px → skala 4,629.

| Element | px na zrzucie | px na ekranie |
| --- | --- | --- |
| początek tytułu | 774 | **167** |
| pierwszy znak licznika `(8)` | 1969 | **425** |
| szerokość pola tytułu | — | **258** |

Tytuł Ep. 2 ma 35 znaków i zajmuje 774–1935 px zrzutu, czyli 251 px ekranu →
**7,17 px na znak** (znak + odstęp, uśrednione). Pole 258 px mieści więc
**~36 znaków**. Tytuł 35-znakowy kończył się dokładnie pod licznikiem; każdy
dłuższy wchodziłby w niego.

**Założenie [HIPOTEZA]:** tytuły są rysowane od tego samego x w każdej misji
(wszystkie zmierzone tytuły zaczynają się w tej samej kolumnie). Zapas na inne
zestawy licznika jest kalibrowany na jednym ekranie; stąd zapas 4 znaków.

## Zakres

Policzone zostały **wszystkie** pola tytułu w grze, nie tylko menu:

| Kategoria | wierszy | > 32 znaków przed | > 32 znaków po |
| --- | --- | --- | --- |
| `mission_title` (menu, `milstP*.bin`, slot 40 B) | 303 | 24 | **0** |
| `mission_note` – kopie tytułów (`*_ext.dat`, slot 40 B) | 224 | 6 (wszystkie w skróconych 24) | **0** |
| `mission_note` – `note_a` / `note_b` (osobny panel listy) | 224 | do 49 znaków | bez zmian |
| `bgm_title` (osobny panel) | — | długie wiersze | bez zmian |

`note_a`/`note_b` i `bgm_title` renderują się w innych panelach i nie mają
zgłoszonego defektu — świadomie **niezmienione** (osobna sprawa, jeśli właściciel
zgłosi).

## Poprawki — 24 tytuły menu (i ich 24 kopie w `*_ext.dat`)

| przed (znaki) | przed | po (znaki) | po |
| --- | --- | --- | --- |
| 38 | `Ep. 21-2: Ostateczna forma Goburikiego` | 29 | `Ep. 21-2: Ostateczny Goburiki` |
| 38 | `Ep. 22-3: Devil Gundam, ostatnia runda` | 29 | `Ep. 22-3: Devil Gundam, finał` |
| 38 | `Ep. 30-3: Death Saurer, bestia zagłady` | 22 | `Ep. 30-3: Death Saurer` |
| 38 | `Ep. 31-1: Starcie!! Forteca Invaderów!` | 29 | `Ep. 31-1: Forteca Invaderów!!` |
| 37 | `Ep. 3-1: Zbrojna interwencja Gundamów` | 29 | `Ep. 3-1: Interwencja Gundamów` |
| 37 | `Operacja: schwytanie uśpionych Zoidów` | 23 | `Operacja: uśpione Zoidy` |
| 36 | `Ep. 11-3: Leże Imperium Mechanizacji` | 23 | `Ep. 11-3: Leże Imperium` |
| 36 | `Ep. 2: Groźba czająca się pod ziemią` | 24 | **`Ep. 2: Groźba pod ziemią`** |
| 36 | `Pragnący wskrzesić demonicznego boga` | 23 | `Pragnący wskrzesić boga` |
| 35 | `Ep. 3-2: Skradający się czarny cień` | 28 | `Ep. 3-2: Skradający się cień` |
| 35 | `Ep. 31-2: Błysk!! U kresu ewolucji!` | 31 | `Ep. 31-2: Błysk!! Kres ewolucji` |
| 35 | `Ep. 9-2: Śmiertelny bój z Riemannem` | 24 | `Ep. 9-2: Bój z Riemannem` |
| 34 | `Ep. 13-2: Stolica imperium w ogniu` | 25 | `Ep. 13-2: Stolica w ogniu` |
| 34 | `Ep. 19-2: Szturmowy desant na Axis` | 24 | `Ep. 19-2: Desant na Axis` |
| 34 | `Poszukiwanie Imperium Mechanizacji` | 21 | `Poszukiwanie Imperium` |
| 34 | `Rzekoma członkini Czarnych Rycerzy` | 22 | `Rzekoma Czarna Rycerka` |
| 34 | `SIM: Bitwa mobile suitów na lądzie` | 23 | `SIM: Bitwa MS na lądzie` |
| 34 | `Święty wojownik upadłego królestwa` | 27 | `Wojownik upadłego królestwa` |
| 33 | `Ep. 19-1: Przełamanie obrony Axis` | 26 | `Ep. 19-1: Przełamanie Axis` |
| 33 | `Ep. 26-3: Odrodzenie Ultrasaurusa` | 29 | `Ep. 26-3: Powrót Ultrasaurusa` |
| 33 | `Ep. 27-1: Ku Zamkowi Mechanizacji` | 28 | `Ep. 27-1: Zamek Mechanizacji` |
| 33 | `Ep. 27-2: Groza! Gniew Kikaishina` | 26 | `Ep. 27-2: Gniew Kikaishina` |
| 33 | `Ep. 29-2: Natarcie Death Stingera` | 29 | `Ep. 29-2: Atak Death Stingera` |
| 33 | `Uderz w bazę zaopatrzeniową wroga` | 25 | `Uderz w bazę zaopatrzenia` |

Kopie w `*_ext.dat` mają dokładnie ten sam tekst (dla pozycji z prefiksem `Ep. N`
w formie dwuwierszowej `Ep. N\n<tytuł>`), więc lista w grze i panel noty pokazują
to samo. Kontrolki formatowania i podziały wierszy pozostały nietknięte.

Tytuły, które już mieściły się w 32 znakach (279 z 303 w menu), są **bajt w bajt**
niezmienione — m.in. `Ep. 0: Misje główne` i `Szkolenie podstawowe`.

## Walidacja

- **Snapshot:** 108 794 wpisy; SHA-256 `polish.jsonl`
  `da2ad33f3c9ad813cd3601ca1a3400586a0ec24cd087dbd0cbe09e5bfc303e1f` →
  `788ab91c72822b149e6d893b4c3b404d1dbebc50743dae0cc8380b46202fcf62`;
  17. wpis `owner_ui_corrections` (`entries: 48`, `runtime_tested: false`,
  plan SHA-256 `f191db7df6e6a7abffb0952401c4990ddb49da1b86554b16e047ee1e152e8d64`).
- **Nakładanie planu:** `tools/pl_ui_corrections.py --stored pakiet_PL --plan … --out …`
  — 48/48 zmian zastosowanych, każda powiązana hashem źródłowego wiersza EN.
- **Materializacja:** `tools/pl_release_package.py materialize` → 109 176 wierszy,
  108 805 wypełnionych, 371 pustych, **0 błędów**, 4 176 ostrzeżeń; zmierzona
  maksymalna szerokość tytułu menu i noty = **32 znaki**, 0 wierszy powyżej.
- **Testy:** nowy `tests/test_pl_mission_title_fit.py` (7 testów: kształt planu
  i pomiaru, powiązanie każdej zmiany z `pakiet_PL`, limit szerokości, równość
  kontrolek i podziałów wierszy, wpis w ledgerze, zgodność menu ↔ kopia
  `*_ext.dat`, limit 32 znaków w materializacji, dokładne teksty Ep. 2, brak zmian
  w `Ep. 0: Misje główne` / `Szkolenie podstawowe`) — pełny przebieg
  `150/150` modułów OK.
- **Kit:** `tools/build_release_pair.py --out local/dist_v4_5 --version 4.5`;
  ZIP PL `8 764 842 B`, SHA-256 `6a602305…d025`, MD5 `568637c9…ed3`,
  92 elementy; kontrola CRC i pokrycia wewnątrz archiwum: 0 błędów,
  108 805/109 176. `README_DIST_PL.md` zyskał sekcję v4.5.

## Status

`runtime_tested` = **false**. Cała weryfikacja jest statyczna (pomiar ze zrzutu,
plan źródłowy, materializacja, testy, CRC/hashe ZIP). Docelowy wygląd paska
wymaga ponownego zrzutu właściciela z PPSSPP — jeśli 32 znaki nadal są zbyt
szerokie przy innym zestawie licznika, limit można obniżyć kolejnym planem.
