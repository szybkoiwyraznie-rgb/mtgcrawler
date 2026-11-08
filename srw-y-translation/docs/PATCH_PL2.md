# SRW Y — patch z drugiej zwrotki PL2

## Dostawa i ograniczenia

`SRW_Y_PATCH_PL2_v2_DIALOGI_BEZ_LAMANIA.zip`: [Drive](https://drive.google.com/file/d/1JF2HezSf_po0nRDDxGqGOKeK27nRZHbU/view), 5 233 892 B, SHA-256 `3570cedd1e7514bb15a7dda65cbf912c648b45a12af51d926d732f91276ae61f` (MD5 `169d16868ba496cd3438efb18a465366`). Pobrany ponownie z Drive ma ten sam MD5 i rozmiar; dwa niezależne przebiegi dały identyczne bajty; CRC wszystkich członów ZIP jest poprawne. Poprzedni `SRW_Y_PATCH_PL2.zip` (`1EOnylL66TcrsRgGXi6Cp3P3H9qDMdSDs`) jest w koszu: różnił się **wyłącznie podziałem linii** w tekście, nie treścią. To instalator budujący pliki lokalnie z oryginałów użytkownika, nie zawiera bundli gry. W katalogu głównym są tylko `CZYTAJ_TO.md`, `PATCH_PL.bat`, `COFNIJ.bat`; reszta w `narzedzia/`.

Zamknij grę, cofnij starszą wersję jej własnym `COFNIJ.bat`, rozpakuj nową paczkę i uruchom `PATCH_PL.bat`. Program weryfikuje oryginały, tworzy i sprawdza kopie `.srwy-original.bak`, zapisuje stan w `narzedzia/STAN_PATCHA.json`. Cofanie: `COFNIJ.bat` z tego samego folderu; nie usuwać stanu ani kopii. Instrukcja i wymagania Pythona są w archiwum.

Nie jest to pełne tłumaczenie całej gry. Czcionki, Windows/BAT oraz rozgrywka **nie zostały zweryfikowane** dla tej wersji; w grze widziano tylko okno dialogowe (zgłoszenie z 2026-11-07). Dialogi i narracja **nie mają żadnego łamania od nas** — okno gry zawija je samo. Selektywne łamanie zostało wyłącznie w 16 polach systemowego UI, z czego 3 mają więcej niepustych linii niż EN i mogą zostać przycięte; budżet znaków nie mierzy szerokości glifów. Patrz `translations/pl2/LAYOUT_REVIEW.json`.

## Zmiana po zgłoszeniu z gry (2026-11-07)

Właściciel pokazał zrzuty okna dialogowego PL2: tekst łamał się brzydko, z
osieroconymi wyrazami („…a Treize / Khushrenada / poległ…”, „…Świat mógł /
wreszcie / zacząć od nowa…”). Przyczyna była po naszej stronie: `layout()`
wpisywał w sceny własne przełamania co 90 znaków, a okno gry zawija tekst
**samo** — nasze `\n` trafiały w środek jego zawijania i zostawiały samotne
słowo w linii. Ten sam mechanizm dotyczył tabel `dialog_text` i `prologue`,
które w v5 łamaliśmy według szerokości EN.

Nowa reguła (`tools/pl_import.py`):

- **sceny Lua: zero wstawianych przełamań.** Zostają tylko strukturalne puste
  linie na brzegach tekstu japońskiego; treść jest dokładnie tą jedną linią,
  którą napisał tłumacz.
- **`dialog_text` i `prologue`: też bez łamania** — to ten sam mechanizm
  zawijania w grze.
- **Zostaje tylko znane, nie-zawijające się UI** (`system_text` i powiązane
  wpisy DLC): nadal łamane według najdłuższej linii EN, bo tam gra nie zawija.

Skutek w planie: **29 017** wystąpień scen jest teraz jednoliniowych, a
`LAYOUT_REVIEW.json` zmniejszył się z 117 do **16** zmienionych pól (ostrzeżenia:
3 pola z większą liczbą linii niż EN). Treść, tokeny, klucze i limity bez zmian;
`AUDIT_PL2.json` różni się tylko skrótem planu. Wydanie czytanek jest
**bajtowo identyczne** z v3 — czytanki i tak składały zawinięte linie w akapit,
więc ich pliki i ZIP się nie zmieniły. Ogranicznik „3 × 90” pozostaje wyłącznie
jako budżet znaków na kwestię (270), nie jako podział linii.

## Zakres i rozstrzygnięcia

- Oryginalne `Y_PL2.zip`: SHA-256 `7dd15523ed295087386956bd78b86ac8b217f5679b37ae74f5d254354b5ec8f8`; 14/14 plików odpowiada zatwierdzonemu wzorcowi po wyzerowaniu PL. Niezmienione pliki w `translations/pl2/PL/`.
- 64 833 niepuste sloty, 4 538 pustych. Z ich powtórzeniami 73 341 wystąpień (44 324 klucze tabel, 29 017 scen). Wszystkie niepuste sloty i powtórzenia występują w planie; puste pozostają oryginalne. Innych, nieprzesłanych plików nie uznajemy za przetłumaczone.
- 24 historyczne grupy kwarantanny / 27 diagnostyk (raport w `QUARANTINE_PRECHECK.json`) usunięto, nie przez pominięcie tłumaczenia. Zachowano 22 wcześniejsze korekty tylko po sprawdzeniu oryginalnej wartości, ID i korzenia powtórzenia w PL2. Pięć nowych skrótów dotyczy konkretnych powtórzeń z mniejszym limitem niż ich korzeń. Pełna lista i powody: `CORRECTIONS.json`; audyt każdego wystąpienia: `AUDIT_PL2.json`.
- Sześć wystąpień znaku ♪ w nowych scenach zachowano, gdy występuje w tym samym oryginalnym tekście japońskim; pojawia się również w angielskim korpusie gry. Nie dowodzi to jakości renderowania.
- Odtworzony korpus uzupełnia pięć japońskich referencji wariantów po powstaniu szablonu v8: nie dodano tych nieistniejących w zwrotce slotów. W 17 plikach scen (280 wpisów) JP jest wyłącznie referencją z potwierdzonego wariantu pokrewnego; w indeksie nie ma pliku JA tej nazwy. Patcher zapisuje istniejący plik EN, nie wymyśla brakującego pliku JA; źródło, metoda i referencja są kontrolowane w manifeście i planie.

## Kontrole

Paczka rozpakowana i uruchomiona na kopiach 12 oryginalnych bundli pobranych z wcześniej otrzymanych archiwów, z sumami zgodnymi z indeksem. Wszystkie 12 przebudowano i odczytano kontrolnie, wszystkie backupy pasowały do oryginałów, po cofnięciu 12/12 plików i backupów miało oryginalne SHA-256. Odrębna powtórna budowa ZIP dała identyczne bajty. Nie jest to test gry ani Windows.

## Odtwarzanie z repozytorium

Python 3.10+, zależności kitowe `UnityPy==1.25.4`, `pycryptodome==4.2.0`, `lz4==4.4.5`. Od katalogu `srw-y-translation/`, używając nowych albo usuwalnych plików w ignorowanym `local/`:

```sh
python tools/bind_v8_return.py --input translations/pl2/PL --output local/pl2-manifest.json
python tools/build_pl2_corrections.py --manifest local/pl2-manifest.json --output local/pl2-corrections.json
cmp local/pl2-corrections.json translations/pl2/CORRECTIONS.json
# Opcjonalne odtworzenie preflight, wymaga nowego katalogu wyjściowego:
python tools/import_safe_subset.py --manifest local/pl2-manifest.json --input translations/pl2/PL --source-dir data/s6-full --output-dir local/pl2-quarantine
cmp local/pl2-quarantine/quarantine.json translations/pl2/QUARANTINE_PRECHECK.json
python tools/audit_full_return.py --manifest local/pl2-manifest.json --input translations/pl2/PL --source-dir data/s6-full --corrections translations/pl2/CORRECTIONS.json --historical-quarantine translations/pl2/QUARANTINE_PRECHECK.json --return-label PL2 --output-plan local/pl2-plan.json --output-report local/pl2-audit.json
cmp local/pl2-audit.json translations/pl2/AUDIT_PL2.json
python tools/build_unwrapped_plan.py --manifest local/pl2-manifest.json --input translations/pl2/PL --source-dir data/s6-full --corrections translations/pl2/CORRECTIONS.json --output local/pl2-unwrapped.json
python tools/audit_ui_wrap.py local/pl2-unwrapped.json local/pl2-plan.json --output local/pl2-layout.json
cmp local/pl2-layout.json translations/pl2/LAYOUT_REVIEW.json
python tools/build_y_release.py --plan local/pl2-plan.json --report translations/pl2/AUDIT_PL2.json --output local/SRW_Y_PATCH_PL2_v2_DIALOGI_BEZ_LAMANIA.zip
```

Przed użyciem patchera wykonaj kopię zapisów gry. Do testów warsztatu: `pytest`, `pytest-subtests`, `Pillow`, `tree-sitter`, `tree-sitter-powershell` oraz zależności kitowe. Żaden z testów offline nie zastępuje testu na komputerze gracza.
