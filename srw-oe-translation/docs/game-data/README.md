# `docs/game-data/` — wyciąg z oryginalnych plików gry

Katalogi mechów i pilotów czytały dotąd dane wprost z oryginalnych kontenerów
`config*` i z odszyfrowanego programu gry 1.08. Dopóki tych plików nie było na dysku,
katalogi po prostu nie powstawały — i właśnie dlatego wypadły z paczki czytanek v4.12.

Ten katalog zamyka tę dziurę. Wszystko, co buildery naprawdę z tych plików czytają,
zostało wyciągnięte **raz** i leży w repozytorium. Od tej pory każda budowa — katalogi,
czytanki, łatki — opiera się wyłącznie na repozytorium.

## Co tu jest

| Plik | Zawartość |
| --- | --- |
| `engine-tables.json` | Tabele silnika odczytane z 21 kontenerów: jednostki (`unit_list*`), uzbrojenie (`wp_list*`), postacie (`charalist*`), umiejętności (`srwDL_Skill00.bin`), pula opisów, grupy (`groupunit00.bin`) i indeks jednostek. Każdy rekord zachowuje `raw_hex`, więc kontrole tożsamości japońskiego tekstu działają jak wcześniej. |
| `spirit-table.json` | `srwDL_Spirit.bin` z `configst.cpk` (Komendy Ducha), zapisane szesnastkowo. |
| `executable-strings.json` | Angielskie teksty spod wszystkich 112 wskaźników, które katalogi wyłuskują z programu gry, razem z offsetem w pliku i SHA-256 każdego z nich. |
| `manifest.json` | SHA-256 i rozmiary powyższych, hasz programu gry, spis kontenerów i liczności rekordów. |

Towarzyszy im `pakiet_katalog_EN/` w korzeniu projektu — zamrożony pakiet angielski
(6 plików), na którym katalogi zostały zamknięte i do którego odwołuje się
`docs/mech-catalog/source-inventory.json`.

## Czego tu nie ma i nie będzie

Oryginalnych kontenerów, obrazu ISO ani programu gry. To pliki gracza; repozytorium
trzyma wyłącznie wyciągnięte z nich dane potrzebne do złożenia dokumentów.

## Czy to nadal jest sprawdzane

Tak, i to w tych samych miejscach co wcześniej — wyciąg niczego nie obchodzi:

- `mech_catalog_sources.collect()` przepuszcza tabele przez komplet kontroli rosteru,
  tożsamości japońskiego tekstu i odwołań — tak samo jak dane prosto z kontenerów;
- `mech_catalog.build_model()` nadal porównuje SHA-256 pakietu `09_executable.jsonl`
  z mapą silnika, a każdy tekst z programu gry — z zapisanym `english_sha256`;
- `game_data_extract.verify()` pilnuje, żeby pliki wyciągu zgadzały się z manifestem.

Uszkodzony albo podmieniony wyciąg wywala budowę dokładnie tam, gdzie wywaliłby ją
uszkodzony kontener. Pilnuje tego `tests/test_no_external_game_files.py`.

## Odtworzenie wyciągu z oryginałów

Potrzebne tylko wtedy, gdy zmieni się zakres danych — nie przy zwykłym wydaniu:

```bash
python3 tools/game_data_extract.py --build \
    --containers <katalog z config00.cpk, config01-19.EDAT, configst.cpk> \
    --elf <odszyfrowany program gry 1.08> \
    --package pakiet_katalog_EN
```

Sprawdzenie bez oryginałów (to robi też test):

```bash
python3 tools/game_data_extract.py
```

## Budowa katalogów bez plików gry

```bash
python3 tools/build_polish_reading_editions.py \
    --english pakiet_EN --polish <zmaterializowany pakiet PL> --out <katalog wyjściowy>
```

W raporcie `verification.json` pojawia się `"game_files_required": false`.
