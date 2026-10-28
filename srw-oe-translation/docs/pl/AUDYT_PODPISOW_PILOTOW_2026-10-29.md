# OE — audyt japońskich podpisów pilotów w przeglądzie robotów

## Zgłoszenie i wynik

Właściciel pokazał dwa zrzuty z gry: Gurren Lagann z podpisem pilota Simona oraz Shin Getter-1 z podpisem pilota Go. Widoczny jest oryginalny japoński podpis. Audyt dotyczy wyłącznie podpisów pilotów w tym przeglądzie, nie wszystkich napisów w pozostałych widokach.

Ponownie odczytano **20 oryginalnych, odszyfrowanych kontenerów** `config00.cpk` oraz `config01.EDAT`–`config19.EDAT`, weryfikując ich SHA-256 z `docs/mech-catalog/source-inventory.json`. Zawierają łącznie **305 rekordów** słownika robotów. W każdym z siedmiu pól tekstowych rekordu sprawdzono obecność japońskiego słowa „pilot”; wszystkie znalezione wystąpienia są w polu 4. Nie jest to twierdzenie, że globalny katalog ma tylko 305 jednostek — liczba 393 dotyczy innego, globalnego wykazu jednostek.

- **35 rekordów jednostek** ma w tym polu podpis „Pilot: …”. To rekordy wariantów, nie 35 różnych konstrukcji.
- Po odtworzeniu snapshotu PL v4.6 i sprawdzeniu docelowych zapisów istniejącego writera **4 rekordy mają przygotowany zapis**, a **31 nie ma polskiego tekstu**, więc w przypadku użycia tych danych pozostaną japońskie. Obejmuje to jednostki spotykane po obu stronach konfliktu.
- Te 31 rekordów ma **18 różnych nazw maszyn** i 30 różnych tekstów podpisu. Powtórzenia w kopiach `config`/`imenu` nie są liczone jako dodatkowe jednostki. Dane nie rozstrzygają, czy wszystkie warianty są w konkretnej rozgrywce dostępne, jak również nie zastępują wizualnej próby w grze.
- W `04_config_text.jsonl` jest 68 osobnych eksportowanych wierszy z podpisem: po 34 w `config` i `imenu`. Snapshot zawiera jawnie 5 takich wierszy, a 63 są puste. Nie należy utożsamiać 63 z liczbą błędnych mechów: jedna strukturalna kopia jest pokryta osobnym wpisem `robonote:1061:type`, a builder przenosi zmiany między identycznymi kopiami. Ostateczną liczbę 31 ustalono na rekordach słownika i faktycznym planie writera, nie przez proste policzenie pustych eksportów.
- Potwierdzono bajtową identyczność oryginalnego `srw_DL_RoboDictionary00.bin` w `config00.cpk` i `imenu00.cpk` (9442 B, SHA-256 `9c6e80a17cd1a7ce467be4afd2d646960956381a3297d6a6b06b102d3c1544e3`). Lustrzanie kolejnych kontenerów jest opisane i obsługiwane w istniejącym builderze; ten audyt nie udaje, że zweryfikował od nowa wszystkie ich pliki `imenu`.

## Jednostki bez pokrycia w obecnym snapshocie

Nazwy robotów to aktualne nazwy PL z pakietu, imiona w poniższej tabeli są istniejącymi nazwami referencyjnymi i służą identyfikacji wariantu, a nie stanowią nowej korekty tłumaczenia.

| Jednostka | Podpisy pilotów bez pokrycia |
| --- | --- |
| Real PG Gundam | Keroro |
| Gurren Lagann | Simon; Kamina |
| Shin Getter-1 | Ryoma; Go |
| Shin Getter-2 | Hayato; Kei |
| Shin Getter-3 | Benkei; Gai |
| Gouf | Ramba Ral |
| Scopedog TC-RS | Chirico; Gregore; Murza; Byman |
| Gustav MS | Moonbay |
| Redler | Viola |
| Sarge Aupus | Nei; Giwaza |
| Scopedog RS | Riemann |
| Zaku III | Rakan |
| Qubeley Mk-II | Ple; Ple Two |
| Scopedog ISS | Chirico; Barcoff; Zaki; Godan; Kochak |
| Blood Sucker | Ypsilon |
| Bat-Shu | Gablae |
| Gun Sniper NS | Naomi |
| Gun Sniper LS | Leena |

Przygotowane wcześniej podpisy obejmują warianty Zaku II i Gelgoog Chara oraz Dom i Rick Dom Czarnej Trójcy. To wynik kontroli pakietu i planu writera; właściciel nie potwierdził wszystkich czterech w grze.

## Dlaczego poprzedni przegląd tego nie wychwycił

Podpis jest w polu `type` słownika robotów. Większość takich napisów trafiła do wyeksportowanych wierszy `config_leftover`, które są domyślnie poddawane kwarantannie, a nie do standardowych, widocznych pól nazwy jednostki i pilota. Przy wcześniejszym zgłoszeniu naprawiono napisy typu uzbrojenia i osobno cztery wpisy Chara. Dokument `UI_ZAKU_CHAR_PILOT_2026-10-20.md` wprost odnotował, że pozostałe podpisy pilotów nie zostały wtedy objęte tą poprawką. Późniejszy audyt pokrycia 08 nie dowodził tłumaczenia tych oddzielnych wierszy 04.

## Odtworzenie i kontrola

Po zgromadzeniu zweryfikowanych źródeł w lokalnym katalogu, z katalogu projektu:

```sh
python tools/audit_robot_pilot_footers.py --configs ../google_drive \
  --out local/audyt-pilotow/wynik.json
python -m unittest discover -s tests -p test_audit_robot_pilot_footers.py -q
python -m unittest discover -s tests -p test_pl_zaku_enemy_viewer.py -q
```

Narzędzie nie zmienia snapshota ani kontenerów. Odtwarza PL v4.6 w katalogu tymczasowym, weryfikuje jego wiązania i rzeczywiste adresy w oryginalnych rekordach oraz odpytuje `table_write.resolve_rows`; raport z treścią gry pozostaje w ignorowanym `local/`. Czytanie całego słowa „pilot” jest fail-closed: inne miejsce lub nieoczekiwany format nie są pomijane. Snapshot `pakiet_PL/polish.jsonl`: SHA-256 `321d22bd9297569ed9e5caca1dcd64319c12f863b3a8c1b488d5147559711fd8`.

Testy syntetyczne: 4/4; wcześniejszy test regresyjny podpisu Char i typów: 6/6. **Nie wprowadzono jeszcze poprawki ani nie zbudowano nowego patcha**; potwierdzenia w PPSSPP poza dwoma zrzutami właściciela nie ma.
