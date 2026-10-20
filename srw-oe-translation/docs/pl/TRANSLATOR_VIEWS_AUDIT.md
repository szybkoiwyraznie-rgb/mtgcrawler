# Audyt paczek tłumacza PL — wynik i wydanie 2

**Data:** 2026-10-18. **Zakres:** `sceny_PL.zip` i `widoki_PL.zip`, zgodnie
z korektą właściciela. Nie jest to audyt wcześniejszego ZIP-a patchera.

## Wniosek

**Wcześniejszych paczek nie należy przekazywać tłumaczowi.** Miały nieaktualne
liczenie polskich liter, niepełne informacje o limitach i problemy w ścieżce importu.
Przygotowano zastępujące je **sprawdzone wydanie 2**, z poprawionymi narzędziami.
Oba nowe archiwa należy używać razem. Oryginały pozostawiono bez zmian.

### Gotowe paczki

| Archiwum | Pobranie | Rozmiar | Pliki |
|---|---|---:|---:|
| `sceny_PL_sprawdzone_v2.zip` | [Google Drive](https://drive.google.com/file/d/1ZHubQHhoh65WPC2mweJmPhzZaY1LtdXB/view) | 3 078 178 B | 39 |
| `widoki_PL_sprawdzone_v2.zip` | [Google Drive](https://drive.google.com/file/d/1ibWIHHf8JsiqAH6cX_EtUL1pVmKmxnV_/view) | 1 204 212 B | 11 |

Każde zawiera aktualną `INSTRUKCJA_PL.txt` i liczbowy `AUDYT_PL.json`.
Druga paczka ma teraz 9 widoków: wcześniejsze 7 oraz `program.md` i `teren.md`.
To nadal **puste miejsca PL do wypełnienia**, nie automatyczny przekład.

## Co zostało poprawione

1. **Polskie litery = 1 bajt / 1 cela**, zgodnie z jednobajtowym fontem, także v5.
   Dwubajtowe symbole CP932, np. `…` i cudzysłowy `“”`, liczą się jako 2, nie 1.
2. **Rzeczywiste limity zapisu i ekranu pod każdym edytowalnym elementem.**
   Nazwy nie są już uznawane za nieograniczone tylko dlatego, że eksport ma `grow`.
   Imiona w `charalist`: 31/43/19 B; nazwy jednostek: 31/31/63 B;
   nazwy broni: 63/31 B. Jednocześnie lista jednostek ma limit 14 celi;
   14 celi dla pilota jest zaleceniem, nie tym samym co limit zapisu.
3. **Sceny również pokazują limity elementów**, w tym tytułów i uwag misji.
   Rodzaj okna decyduje o szerokości, nie jeden globalny limit dla wszystkiego.
4. **Tokeny opisane przy konkretnych tekstach.** Wymagane zmienne/kolory pozostają,
   ale `%s` będące znacznikami japońskich głosek i surowe `<0x0F>` nie trafiają do PL.
   Walidator chroni też `%d`, `%02d` i zmienne imienia/nazwiska gracza.
5. **Pełny JP i odcisk źródła chronią import przed niezgodnym szablonem.**
   Podwójne bloki, nieznane elementy i sprzeczne wpisy powodują błąd bez zapisu
   całej partii PL. CLI sygnalizuje niepowodzenie kodem 1.
6. **Polskie kopie propagują się w polu PL**, także po edycji źródła i w łańcuchach.
   Obsłużono powtarzane identyfikatory między tabelami/rozdziałami. Referencyjne
   EN nie zmienia się i nie zastępuje automatycznie brakującego PL.
7. **Etykiety tabel zapisują się właściwym kodekiem PL**, nie sztywnym CP932.
8. **Dopisano brakujące kategorie programu i terenu**, z ich odrębnymi zasadami.
   Nie potwierdzono fontu PL w EBOOT, więc polskie litery są tam blokowane nawet
   dla regionów UTF-8; zalecane ASCII. Teren: ASCII, maks. 12 znaków.
9. **Ochroniono `NoData`, puste pola i literały silnika.** Odłożono 364 nierozpoznane
   `leftover:`. Zachowano 8 takich źródeł potrzebnych 24 rzeczywistym polom katalogu —
   usunięcie wszystkich `leftover:` naruszałoby dziedziczenie.
10. Pełny audyt wykrył i naprawił także odczyt zagnieżdżonych etykiet `[kopia]`,
    kontynuacji zaczynających się nawiasem i początkowego wyrównania EN.

## Co faktycznie sprawdzono

Bazą był bieżący `pakiet_EN`: **109 144 wiersze tekstowe i 293 strukturalne**.
Odcisk bazy: `70c6aad517a69b7cbd8cd01c76b6f3a5b14e4fbd3661bcc59aabbbd36fac112d`.

- Każdy element wszystkich **46 plików MD** porównano z właściwymi źródłowymi
  rekordami: JP, referencja EN i przypisanie do późniejszego importu.
- Pokrycie tekstu: **108 761 edytowalnych/dziedziczonych wierszy + 19 chronionych
  + 364 odłożone = 109 144**. **0 nieprzypisanych wierszy** w tym podziale.
- Sprawdzono wszystkie **17 031 jawnych kopii**. Brak brakujących źródeł,
  niezgodnego JP i cykli po poprawieniu rozwiązywania identyfikatorów.
- Mechanicznie wypełniono wszystkie edytowalne bloki tekstami kontrolnymi PL,
  zachowując tokeny i strukturę. Import zmienił **84 153 elementy**, uzupełnił
  **16 262 kopie** i dał **108 761 wypełnionych wierszy PL**.
- Kontrola całego syntetycznego pakietu: **0 błędów**. JP, EN, kolejność, liczba
  wierszy i pozostałe metadane nie zmieniły się. Drugi import był bajtowo obojętny.
- Pakiet syntetyczny przeszedł ładowanie przez builder w trybie PL, bez wycieku EN.
- **1591 testów: OK, 25 pominiętych**. W tym granice długości i izolowane budowanie
  zestawu TEST_PL na trzech oryginalnych kontenerach z niezależnym odczytem wyniku.
- Dokładne wydane ZIP-y: zgodność bajtów z katalogami wyjściowymi, CRC, odcisk
  źródła i import pustych bloków bez zmian. Po wysłaniu na Drive pobrano oba ponownie
  i potwierdzono identyczne SHA256.

Źródłowe archiwa, angielski pakiet i oryginalne pliki gry nie zostały zmienione.
Teksty kontrolne są wyłącznie lokalnym testem; **nie znajdują się w paczkach tłumacza**.

## Granice tego wyniku — bez obietnicy „100% wszystkich ekranów”

To pełne sprawdzenie **kontraktu wyodrębnionego pakietu i importu**, nie dowód,
że każdy przyszły przekład zmieści się na każdym ekranie gry. Pozostają:

- testy układu po rzeczywistym tłumaczeniu, zwłaszcza pól o niezmierzonym limicie UI;
- rozwijane przez grę zmienne `%s` / imię gracza, których wynik zależy od kontekstu;
- niepotwierdzone 364 `leftover:` i napisy/tekstury niewyodrębnione do tej bazy;
- aktualizacja po wydaniu: właściciel zaakceptował wygląd v5 na dwóch zrzutach
  otwierającej narracji/dialogu; nagłówki bez Ł/Ś/Ó były tekstami ASCII w źródle,
  nie awarią fontu. Nie jest to test wszystkich ekranów;
- program i teren bez polskich liter — to jawne ograniczenie, nie „naprawione” fontem.

Pełny syntetyczny import nie oznacza zbudowania i obejrzenia w grze wszystkich
108 761 tekstów. Test na oryginalnych kontenerach obejmuje istniejący zestaw próbny.

## Późniejsza integracja

Tłumacz zmienia tylko bloki **PL** i oddaje te same MD/ZIP-y. Nie musi edytować JSONL.
Integracja wymaga narzędzi z checkpointu `0053e01` lub nowszego, nie starego patchera v1.
Szczegółowe polecenia są w instrukcji dołączonej do obu archiwów.

Narzędzie odtworzenia i pełnej kontroli:

```text
python tools/build_pl_translator_views.py --package pakiet_EN --out local/nowy_katalog_PL
```

Katalog wyjściowy musi być nowy/pusty; generator odmawia nadpisania pracy tłumacza.
Narzędzia, testy i instrukcje są wypchnięte do [PR #20](https://github.com/szybkoiwyraznie-rgb/mtgcrawler/pull/20).
Prywatne archiwa i pliki gry nie są publikowane w repozytorium.

Pełny manifest: `docs/pl/translator-views-v2-delivery.json`.
