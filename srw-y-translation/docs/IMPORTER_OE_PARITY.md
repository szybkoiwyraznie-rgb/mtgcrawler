# Importer Y — audyt zabezpieczeń względem OE (2026-10-27)

## Punkt odniesienia i zasady przeniesienia

Na prośbę właściciela przegląd wykonano **po pierwszym prototypie Y**, nie przed
nim. Nie przedstawiamy pierwszej wersji jako importera o udowodnionej dojrzałości OE.
W tej iteracji przeczytano kod i testy referencyjne OE:

- `tools/translation_import.py`: parser, rozwiązywanie adresów, pieczęć źródeł,
  kontrola całego JP, konflikty, walidacja przed zapisem;
- `tools/pl_handoff.py`: fingerprint źródła, ochrona pól i wyjątki techniczne;
- `tools/translation_copy.py`: tożsamość JP, łańcuchy, cykle, budżet celu, izolacja PL;
- `tools/translation_check.py`: tokeny, kolejność, procenty i kontrola znaków;
- `tests/test_translation_import.py`, `tests/test_pl_handoff.py`,
  `tests/test_translation_copy.py`.

**OE nie zostało zmienione.** Nie ma importów kodu ani danych z katalogu OE do Y.
Przeniesiono zasady i przypadki regresyjne, dostosowując je do istniejącego formatu
Y (jednoliniowe PL, Unicode, Unity/Lua, powtórzenia wewnątrz pliku).
Testy mają własne, syntetyczne rekordy — nie wciągają tekstów gry z OE.

## Co faktycznie znaleziono i poprawiono

1. **Brak odpowiednika kontroli aktualności pakietu OE.** Manifest Y chronił wzorzec
   Markdown, ale nie wiązał go z bieżącymi plikami S6. Manifest **schema 2** zawiera
   teraz SHA-256 całych źródeł: `scenario.jsonl`, `tables.jsonl`, `limits.json`,
   `groups.json`, `voice_map.json`, `voice_groups.json`, `mission_map.json`.
   Brak opcjonalnego pliku jest również częścią pieczęci; jego późniejsze pojawienie
   się unieważnia manifest. Wymagane są oba pliki JSONL, również gdy partia dotyczy
   tylko tabel. Zmiana niezwróconej sceny też unieważnia pieczęć.
2. **Tożsamość celu.** Oprócz hasha sprawdzane jest istnienie każdego rekordu
   manifestu w aktualnym S6: ID/plik/wystąpienie sceny albo tabela/klucz/indeks,
   a także JP i EN. Uszkodzona mapa z innym kluczem nie przekieruje tłumaczenia
   tylko dlatego, że japoński napis wygląda podobnie.
3. **Brak trybu bez zapisu.** Dodano `--check`, z tą samą walidacją źródeł, zwrotki,
   powtórzeń i układu. Nie wymaga `--output`, nie tworzy raportów ani plików.
4. **Zbyt wąska lista tokenów (`%s`/`%d`).** Walidator rozpoznaje też printf z
   szerokością/precyzją, np. `%02d`, `%.2f`, i `%%`. Nie zmienia to linii `tokeny:`
   w dostarczonym v8. Rozpoznawanie rozszerzono w importerze, nie w rendererze v8.
5. **Błędne dopuszczenie dowolnej kolejności.** OE nie dopuszcza zamiany kolejności
   tokenów sterujących/argumentów. Y sprawdza teraz zarówno liczebność, jak i
   kolejność. Jedyny ruchomy wyjątek to `%%`, który nie pobiera argumentu.
6. **Regresja literalnego procentu.** Wzorem OE spacja nie jest flagą printf:
   `50% obrażeń`, `10% i`, `% EN+` nie tworzą fikcyjnych placeholderów.
7. **Niewidoczne końcowe przejścia do nowej linii.** Tabele zachowują puste linie
   początkowe, wewnętrzne, końcowe oraz ich separatory LF/CRLF/CR — bez żądania
   dodatkowych słów w pustej linii. Sceny zachowują strukturalne separatory na
   brzegach, nadal z limitem 3 linii łącznie z pustymi.
8. **Ukryta modyfikacja przy składaniu tekstu.** Token przylegający do słowa,
   np. `＜仮＞tekst`, nie dostaje już dodatkowej spacji. Przenoszenie na następną
   linię nie dzieli tokenów ani nie usuwa znaków prozy.
9. **Uszkodzone dziedziczenie.** Źródło powtórzenia musi poprzedzać cel oraz mieć
   to samo JP+EN. Brak dawcy, wskazanie na siebie, naprzód, cykl czy zmieniony JP/EN
   kończą się odmową zamiast częściowego zapisu lub wyjątku rozwiązywania kopii.
10. **Konflikty celu.** Ten sam adres z różnym JP/EN jest odrzucany również wtedy,
    gdy przypadkiem wpisano identyczne PL. Różne PL tego samego celu także są błędem.
11. **Odporność zapisu.** Test wymusza błąd `os.replace`: poprzedni wynik zostaje
    identyczny bajtowo, plik tymczasowy jest usuwany. Wynik nie może nadpisać S6.
    Pieczęć sprawdzana jest ponownie po walidacji. Builder sprawdza, czy dane nie
    zmieniły się podczas renderowania. Nie jest to blokada transakcyjna systemu
    plików: nie modyfikować S6 równolegle podczas budowania/importu.

## Macierz odpowiedników

Nazwy regresji poniżej odnoszą się do nowego
`tests/test_pl_import_oe_regressions.py`, chyba że wskazano inaczej.

| Zabezpieczenie/przypadek OE | Odpowiednik Y / świadoma różnica |
|---|---|
| Nieaktualna pieczęć całego pakietu | `change_outside_returned_batch_still_invalidates_snapshot`, `optional_limits_voice_and_mission_inputs_are_also_bound`, `missing_sources_and_unstamped_manifest_are_refused` |
| Pełny, wieloliniowy JP, nie tylko pierwsza linia | `full_multiline_japanese_and_parenthesized_reference_stay_immutable` + ścisłe porównanie całego Markdown |
| Adres rekordu zamiast dopasowania samego JP | `manifest_target_or_japanese_damage_cannot_redirect_to_another_row`; istniejący test adaptera `test_imported_scene_goes_directly_to_apply_pl` rozróżnia `ID#1` i `ID#2` |
| `--check` nie zapisuje | `check_without_output_does_not_write`, `check_with_output_does_not_touch_existing_output` |
| Idempotencja ponownego importu | `repeated_import_is_deterministic_and_does_not_mutate_inputs`, `cli_is_byte_idempotent` |
| EN i JP nie zmieniają się przy imporcie PL | `polish_does_not_change_japanese_or_english`; zmieniony EN w zwrotce jest w Y odrzucany, nie ignorowany |
| Brak PL nie uruchamia fallbacku EN | `missing_polish_never_falls_back_to_english`; wynik partii nie zawiera takiego celu |
| Brak częściowego zapisu przy błędzie | `test_cli_atomic_failure_and_success`, `test_bad_batch_does_not_return_good_subset` w podstawowych testach Y |
| Duplikat elementu/bloku PL | `duplicate_element_even_if_identical_is_not_silently_collapsed` + podstawowy `test_multiline_and_extra_slot_rejected` |
| Sprzeczne przypisania do rekordu | `conflicting_assignments_to_one_target_are_refused`, `same_pl_does_not_hide_conflicting_source_for_one_target` |
| Cel kopii ma swój własny limit | `copy_uses_its_own_target_budget` |
| Brak dawcy, cykl, zmienione źródło kopii | `missing_self_forward_and_cyclic_donors_are_refused`, `changed_copy_source_is_refused`; Y używa wyłącznie wcześniejszych dawców w tym samym pliku, nie ogólnego grafu `copy_of` |
| Imię gracza, printf, krotność, kolejność | `real_printf_width_precision_and_escaped_percent_are_mandatory`, `engine_token_order_cannot_be_swapped`, `escaped_percent_can_move_without_moving_arguments` + podstawowe testy krotności |
| Zwykły procent w zdaniu nie jest placeholderem | `literal_percent_before_polish_word_is_not_printf` |
| Niewidoczne końcowe przejścia | `table_trailing_and_empty_lines_are_structure_not_word_slots`, `inner_empty_lines_stay_empty`, `scene_structural_edges_are_not_silently_dropped` |
| Nawias w kontynuacji nie jest metadanymi | JP i EN są w Y chronione w całości; `full_multiline_japanese_and_parenthesized_reference_stay_immutable`. Wieloliniowe PL odrzucane zgodnie z decyzją dla Y |
| Limit i nieobsługiwany znak | podstawowe testy Y `test_exact_limit`, `test_unsupported_and_controls`, `test_polish_and_source_tokens` |
| Puste pole / literał silnika | Y chroni puste źródła i tabele `font`/`fonts`; `readonly_empty_and_resource_fields`. Konkretne PSP `NoData`/EBOOT nie są automatycznie uznawane za literały Y bez dowodu z Y |
| ZIP i pliki | podstawowe `test_zip_and_directory`, `test_duplicate_basename_in_directory`; Y dodatkowo odrzuca ścieżki ZIP i ma limit rozpakowanej partii |
| Granice parsera/etykiety kopii | Y nie rekonstruuje JP z etykiet. Manifest wiąże pełną niezmienioną treść z kolejnością rekordów renderera; dodanie/zmiana etykiety nie jest tolerowana |
| Pełny roundtrip pakietu | **syntetyczny** builder → manifest → zwrotka → planner tabel / adapter scen jest sprawdzony. **Pełny prywatny v8 pozostaje niesprawdzony** |

## Różnice, których nie wolno „przenieść na ślepo”

- CP932, prywatne kody polskich liter, komórki PSP, limity bajtowe slotów,
  `0x0F`/kana i OE `tokeny.tsv`: **nie są modelem zapisu Y**. Y używa Unicode,
  przebudowy bundli oraz własnych tokenów; źródło jest japońskie, nie kolumna EN.
- Znaczniki `⏎` / `<0x0F>` z widoków OE nie są poleceniami formatu Y. Nie są
  automatycznie zamieniane na sterujące bajty. Sterujące znaki wpisane do PL są
  odrzucane; struktura pochodzi z oryginalnego S6.
- OE posiada globalne, udokumentowane `copy_of`/resync i aktualizuje pakiet PL.
  Y emituje plan pojedynczej partii i dziedziczy tylko jawnie pominięte sloty
  zgodnie z regułą eksportera Y (dokładne JP+EN w tym samym pliku).
  **Nie ma jeszcze scalania wielu wcześniejszych planów ani globalnego resync.**
  Nie należy ręcznie scalać słowników bez walidacji konfliktów.
- Układ Y nadal jest heurystyczny: sceny 3 × 90, tabele z zachowaną strukturą
  separatorów i zrównoważonym podziałem słów między niepustymi linijkami.
  To nie gwarantuje poprawnej semantyki linii formularza ani wymiarów w pikselach.
- Konserwatywna lista dozwolonych znaków Y **nie jest pomiarem całego fontu**.
- Pieczęć Y obejmuje dokładne bajty źródeł. To bardziej restrykcyjne niż
  semantyczny fingerprint OE ignorujący `pl`: nawet zmiana formatowania JSONL
  wymaga świadomego odtworzenia i porównania pakietu, nie wyłączenia kontroli.
- Manifest jest zaufanym plikiem operatora, bez podpisu kryptograficznego.
  Niezwiązane manifesty tworzone przez `make_manifest(..., source_sha256=None)`
  służą tylko izolowanym testom renderera; CLI ich nie akceptuje. Związany manifest
  również w Python API wymaga `source_dir` i przechodzi kontrolę żywych rekordów.

## Wyniki i granica gotowości

- Oryginalne, niezmienione testy referencyjne OE uruchomione osobno:
  **71 passed** (`test_translation_import.py`, `test_pl_handoff.py`, `test_translation_copy.py`).
- Y: **109 passed, 1 skipped, 57 subtests passed** — intake, nowe regresje OE,
  renderer oraz adaptery zapisu. Pominięty test wymaga prywatnego bundla.
- Pełna seria Y: **433 passed, 44 skipped, 20 failed, 65 subtests passed**.
  Wszystkie 20 niepowodzeń to nadal brak prywatnych listingów (1 test misji +
  18 podtestów kitów PS) albo bundli test6 (1 test patchera).
- Dodano osobny workflow `SRW Y — importer regressions` dla Python 3.11/3.12,
  uruchamiający tylko syntetyczny zakres Y. Lokalnie sprawdzono Python 3.11;
  wynik GitHub CI należy odczytać osobno. Workflow nie publikuje danych/artefaktów gry.

**Nie deklarujemy pełnej równoważności produkcyjnej z OE.** Przed prawdziwym importem
wciąż potrzebne są: odtworzenie manifestu schema 2 na prywatnych danych v8,
porównanie dostarczonego Markdown, rzeczywista zwrotka i odczyt zwrotny z przebudowanych
bundli. Dopiero potem kontrola układu w grze. Zbiorczy orchestrator przebudowy scen
oraz trwały pakiet/scalanie kolejnych partii pozostają poza tym importerem.
