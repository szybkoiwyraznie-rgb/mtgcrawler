# SRW OE: handoff po sesji 4 (2026-10-12)

Gałąź: `arena/581a1b79-mtgcrawler` (jedyna dozwolona dla tej sesji). Cel projektu: `docs/GOAL.md`.
Stan: nic nie jest przetłumaczone ani zakończone. Brak wykazanego, działającego patcha xdelta.

## 1. Co zrobiono w tej sesji

| Commit       | Zawartość                                                                                               |
| ------------ | ------------------------------------------------------------------------------------------------------- |
| `2e73bf0`    | `tools/drive_manifest.tsv`: ID Drive, nazwy i rozmiary wejść (bez treści gry)                           |
| `7d159fa`    | dziennik eksperymentów (sekcja sesji 4) i status                                                        |
| `3a53156`    | korekta liczenia dialogów (łańcuch vs skanowanie znaczników)                                            |
| `044b096`    | `tools/mech_names.py` (kandydaci mechów z config00 + config01–46)                                       |
| (ten commit) | ten handoff; usunięcie lokalnych ścieżek absolutnych z `configst_pack.py`, `sysmes_pack.py` i dziennika |

## 2. Liczby i ich status

- **Dialogi, 12738 linii [ZWERYFIKOWANE]**: liczba rekordów dialogu (typ 201) po poprawnym łańcuchu rekordów, 293 członków z 32 kontenerów zdarzeń (`eventP00` z USRDIR, `eventP01–09`, `eventP13`, `eventP20–32`, `evept101–108`). Zgodna z `tools/speaker_probe.py`.
- **46703 [ZWERYFIKOWANE jako zawyżone]**: wynik skanowania znaczników w `tools/extract_scenes.py` (44876 dialogów + 1827 narracji). Tylko 29% trafień dialogowych leży na granicach łańcucha. To prawdopodobnie liczba z lokalnego narzędzia użytkownika (~46k). Nie używać jej jako liczby linii.
- **42 członki bez poprawnego łańcucha rekordów [NIEZWERYFIKOWANE]**: 1166 trafień skanowania, nieweryfikowane, poza 12738.
- **`eventP00`**: na Drive jest jedna kopia (USRDIR, 162264 B). Porównanie z kopią FULL_DLC niemożliwe, bo kopii nie ma.
- **Mechy [NIEZWERYFIKOWANE]**: cel 100+ NIE osiągnięty. Kandydaci: `unit_list` bazowe 267 unikatów, wyświetlane 390, slot 3 słownika mechów 40 (zero wspólnych nazw ze `unit_list`). Nie ustalono, czy `unit_list` to same mechy, czy też piloty.
- **`robo00.cpk` (USRDIR, 38 MB) [ZWERYFIKOWANE]**: archiwum modeli i animacji, 1318 członków. Nazwy `NNNN_KKK` NIE są kluczami jednostek (9 z 45 wspólnych).
- **`info.bin` z `robo00` [NIEZWERYFIKOWANE]**: CRILAYLA, 3114 B po dekompresji, struktura nieznana.
- **`robolist.bin` [NIEZWERYFIKOWANE]**: 363 wpisy (u32 count = 363), 8716 B, nie zdekodowany.

## 3. Krytyczne: trwałość danych

- Pliki w `google_drive/` i `local/` (gitignored) NIE przetrwały granicy tury. Na starcie każdej tury jest tylko `eventP00.cpk`.
- Odtwarzanie: `tools/drive_manifest.tsv` (ID, nazwa, rozmiar). Manifest jest niepełny: brakuje `config38` (nie istnieje na Drive), `imenu01–32`, większości plików USRDIR (68 w całości).
- Pobrano już w tej sesji i do odtworzenia: `config00.cpk`, `config01–46` (bez 38) z FULL_DLC, `robo00.cpk`, `eventP00–32`, `evept101–108`. Listingi ID FULL_DLC i USRDIR są w historii sesji, nie w manifeście.

## 4. Narzędzia (wszystkie w `srw-oe-translation/tools/`)

- `speaker_probe.py`: łańcuch rekordów, liczba dialogów i mówców per członek (metoda zweryfikowana).
- `extract_scenes.py`: skanowanie znaczników; zawyża liczbę, używać ostrożnie (lub poprawić o walidację granic).
- `mech_names.py`: kandydaci mechów z `config*` (wynik w `local/mech/mech_names.json`).
- `drive_manifest.tsv`: lista wejść do ponownego pobrania.
- Wcześniejsze (z poprzednich sesji): `unit_records.py`, `name_units.py`, `inline_names.py`, `battle_members.py`, `build_speaker_inputs.py`, `cpk_write.py`, `crilayla.py`.

## 5. Ustalenia do zachowania (bez zmian z poprzednich sesji)

- Speaker key: u16 w rekordzie +10 = u16 w CharaDictionary +0x40 (zweryfikowane).
- Nazwy z configu są autorytatywne; etykiety ze skryptu trzymać w `script_label`.
- Format `config`-`.pac`: nagłówek 0x800, wpisy co 0x28 od 0x10 (u32 offset, u32 size, nazwa +8).
- Rekordy `unit_list` 384 B; nazwa +0, wariant +140 (zgodny w 200 z 393).
- RoboDictionary: rekord to 7 slotów u32 (offsety względem początku rekordu). Rekord 0 = etykiety pól, nie mechy.
- `font.cpk`, `mesbtl`, `eventP00` i pozostałe: patrz `docs/TECHNICAL_FINDINGS.md`.

## 6. Zakazy (z GOAL/CONSTRAINTS, obowiązują dalej)

- Nie tłumaczyć nic, dopóki setup nie pokryje 100% kategorii tekstu.
- Nie używać skryptu Akurasu jako źródła.
- Nie commitować ISO, EDAT, CPK, BIN/DAT, zapisów, audio, obrazów ani pełnego japońskiego skryptu. `local/` i `google_drive/` są w gitignore.
- Modyfikacja plików gry jest częścią projektu; pliki gry nie są publikowane na GitHubie (lokalnie + Google Drive). (Zasada zaktualizowana 2026-10-17.)
- Nie wpisywać ścieżek absolutnych ani nazw użytkowników do commitowanych plików.
- Oznaczać fakty `[ZWERYFIKOWANE]`, a hipotezy `[HIPOTEZA]` lub `[NIEZWERYFIKOWANE]`.
- Dokumentacja i komunikacja z użytkownikiem po polsku. Bez liczb szesnastkowych w rozmowie z użytkownikiem (podawać dziesiętnie).

## 7. Następne kroki (w kolejności)

1. Odtworzyć wejścia z manifestu (config00, config01–46, eventP*, evept*, robo00).
2. Rozdzielić `unit_list` na mechy i piloty: porównać z `charalist*` i z polami pilotów (+98/+100/+102/+108/+110/+112, [HIPOTEZA]).
3. Zdekodować `robolist.bin` (363 wpisy) i `info.bin` z `robo00`.
4. Jeśli mechów poniżej 100: przeszukać `robo00` i `mesbmp00.cpk` (14 MB, nieidentyfikowany) pod kątem brakujących mechów.
5. Ustalić, czy `extract_scenes` ma walidować granice (żeby zgadzał się z 12738), albo zaakceptować 12738 jako metodę bazową.
6. Kolejka z poprzednich sesji: klucze bez nazwy w walkach (733, 220, 3122, …), walidacja slotów pilotów, 2 klucze do przeglądu (218, 50), rozbieżność 246 vs 216 nazw słownikowych, `lmaplist.bin`, `srwDL_ItemDrop`, nazwy przedmiotów w Shop00, `kanji21L.tbl`, CPK write-back, test rozruchu w PPSSPP.
7. Pytania otwarte do użytkownika: czy liczba 46k z jego narzędzia to skanowanie znaczników; czy dodać cytaty bitewne z ISO (`mesbtl00.cpk`) do liczby dialogów.
