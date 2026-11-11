# Workflow wydania SRW Y — od zwrotki tłumacza do patcha

Ten dokument jest **obowiązujący**. Jeśli agent w tej sprawie zadaje właścicielowi
pytanie („czy to pełne?”, „skąd wziąć pliki gry?”, „czego brakuje?”), to znaczy,
że nie przeczytał tego pliku. Wszystko poniżej jest w repozytorium i sprawdzane
testem `tests/test_repository_completeness.py`.

## Żelazne zasady

1. **Tekst tłumaczy tłumacz.** Agent nie tłumaczy linii gry. Jedyne dozwolone
   zmiany tekstu to skróty wymuszone **technicznym limitem pola** (i poprawki
   tokenów) — każda zapisana jako korekta z uzasadnieniem, z sumą oryginału,
   w pliku `CORRECTIONS.json`. Nic „na oko”, nic po cichu.
2. **Patch ma zawierać 100% tekstu, który przysłał tłumacz.** Nie 99%, nie
   „prawie wszystko”. Jeśli plik zwrotki nie wchodzi, to jest błąd do naprawy,
   a nie fakt do zakomunikowania.
3. **Brak danych nie jest wymówką.** W repozytorium są: źródła gry, indeks
   bundli, wzorzec v8, zwrotki, dodatek, narzędzia. Jeśli czegoś naprawdę brakuje,
   to znaczy, że trzeba to **dodać do repo** (i commitnąć), nie poprosić właściciela.
4. **Zero pytań o to, co już jest w repo.** Ten dokument mówi, gdzie co leży.

## Jedno polecenie

```bash
cd srw-y-translation
python3 tools/one_click_patch.py --return /sciezka/Y_PL4.zip --label PL8
```

Wynik w `build/one_click/`:

| plik | co to jest |
| --- | --- |
| `SRW_Y_PATCH_PL8.zip` | **gotowy patch** do rozpakowania i uruchomienia `PATCH_PL.bat` |
| `PLAN_PL8.json` | plan (co, gdzie i po polsku) — wchodzi do paczki jako `narzedzia/plan.json` |
| `AUDIT_PL8.json` | audyt: sumy zwrotki, pokrycie korpusu, lista plików wyrównanych |

Narzędzie samo:

1. czyta zwrotkę (ZIP / katalog / pliki `.md`),
2. **wyrównuje** pliki zrobione przed poprawką numeracji — po japońskim zdaniu,
   nigdy po numerze wiersza (`tools/realign_return.py`),
3. **znajduje korekty** po sumach zwrotki (`translations/*/surowe/CORRECTIONS.json`)
   i nakłada je raz; nowa zwrotka nie odziedziczy cudzych korekt,
4. wiąże pliki ze wzorcem v8 (`tools/bind_v8_return.py`); pliki spoza wzorca idą
   przez własny manifest dodatku (`translations/patch-v8-1/import_manifest.json`),
5. importuje wszystko przez tę samą bramkę co zawsze: tokeny, limity, układ
   (`tools/pl_import.py`),
6. składa **jeden** plan (baza + dodatek) i przerywa przy kolizji wiersza,
7. sprawdza, że **każda** scena z planu ma adres w indeksie bundli
   (`still_missing`), a potem buduje paczkę (`tools/build_y_release.py`),
8. zapisuje zwrotkę po wyrównaniu do `translations/<etykieta>/PL/`,
   żeby następna sesja nie musiała niczego odtwarzać.

Jeśli coś nie przejdzie, narzędzie **przerywa pracę i mówi co** (np. `limit 10,
wpisano 11 znaków`). Wtedy: albo tłumacz poprawia zwrotkę, albo powstaje korekta
techniczna (`CORRECTIONS.json`) z uzasadnieniem. Nigdy „obniżenie bramki”.

## Gdzie co leży (mapa repo)

| ścieżka | rola | odtworzenie |
| --- | --- | --- |
| `data/s6-full/scenario.jsonl`, `tables.jsonl` | tekst gry JP/EN (korpus) | z gry, `tools/*` ekstrakcja |
| `data/s6-extra/` | wiersze dodane po przypięciu korpusu sumą | kolejne sesje |
| `data/game_text_bundle_index.json` | **gdzie leży** każda scena/tabela w bundlach | `tools/build_game_text_index.py`, `tools/merge_index_entries.py` |
| `data/limits_y.json` | limity pól i grupy powtórzeń | z gry |
| `translations/template-v8/` | wzorzec v8: numeracja, limity, JP/EN | `tools/render_template_v8.py`, `tools/reconcile_template_v8.py` |
| `translations/pl3/surowe/PL.zip` | **dokładnie to, co przysłał tłumacz** | plik od właściciela/Dysku |
| `translations/pl3/surowe/CORRECTIONS.json` | zapis decyzji o skrótach (24) | `tools/build_pl3_corrections.py` |
| `translations/pl3/PL/` | zwrotka wydania (korekty w tekście) | `tools/normalize_return.py` |
| `translations/pl3/appendix/` | dodatek v8.1 + jego manifest | `translations/patch-v8-1/` |
| `translations/pl7/PLAN_PL7.json` | plan całej zwrotki (85 610 rekordów) | `one_click_patch.py` |
| `tools/` | wszystkie narzędzia (bez zależności od `local/`) | — |
| `local/` | **nic trwałego** — obszar roboczy, wycinany z gita | — |

Zasada: **jeśli plik jest potrzebny do zbudowania patcha, musi być w `data/`,
`translations/` albo `tools/`** — nigdy tylko w `local/`.

## Zależności

`tools/requirements.txt` w paczce: `UnityPy==1.25.4`, `pycryptodome==4.2.0`,
`lz4==4.4.5`. W repo (obok `tools/`) są też koła `archspec` i `etcpak` dla
Windows; patcher instaluje środowisko sam (`narzedzia/.venv`) przy pierwszym
uruchomieniu. Do samego **zbudowania** paczki wystarczy `python3` + te trzy
biblioteki (`pip install -r` z linii `REQUIREMENTS` w `build_y_release.py`).

## Publikacja

```bash
# patch na Dysk (folder SRWY) — przez złącze Google Drive
# nazwy: SRW_Y_PATCH_<etykieta>.zip; obok PLAN/AUDIT w repo
```

Po publikacji: wpis w `docs/EXPERIMENT_LOG.md` z sumą SHA-256 i liczbą bundli,
oraz commit planu + audytu do `translations/<etykieta>/`.

Dla GitHub Release zaktualizuj `translations/current_release.json`, tak aby
`label`, `plan` i `report` wskazywały nową pełną paczkę. Workflow oraz oba
buildery czytają ten sam wskaźnik; nie wolno zostawiać starego planu na stałe.
Metadane dodatkowo porównują plan wbudowany w ZIP z aktualnym audytem. Pokrycie
tabel pochodzi wyłącznie z `tools/coverage_y.py`: identyfikatory techniczne są
raportowane osobno, a każdy rzeczywisty brak tłumaczenia przerywa wydanie.

## Gdy przychodzi kolejna zwrotka (np. `Y_PL4.zip`)

1. Wrzuć plik do repo: `translations/pl4/surowe/PL.zip` (commit).
2. `python3 tools/one_click_patch.py --return translations/pl4/surowe/PL.zip --label PL9`
3. Jeśli przerwie na limitach: zbuduj korekty `tools/build_pl3_corrections.py`
   (albo odpowiednik dla nowej zwrotki) — **tylko** skróty wymuszone limitem.
4. Wgraj `SRW_Y_PATCH_PL9.zip` na Dysk, dopisz wpis w `docs/EXPERIMENT_LOG.md`.
5. `python3 -m pytest -q` — ma być zielone, w tym
   `tests/test_repository_completeness.py`.

Żadnego z tych kroków nie trzeba konsultować z właścicielem.

## Gdy gra ma inne japońskie brzmienie niż korpus

**Polskie zdanie trafia wyłącznie tam, gdzie gra ma co do znaku ten sam tekst
źródłowy, który widział tłumacz** (`tools/match_y.py`). Numer wystąpienia
(`49.0#1`) jest tylko podpowiedzią: klucze są pozycyjne w obrębie rewizji pliku,
a część scen leży w grze w dwóch kopiach o różnej liczbie jednostek, więc ten sam
numer wskazuje w nich inne zdanie. Zgodność numeru nigdy nie dowodziła, że pod
spodem stoi to samo zdanie — zgodność tekstu dowodzi tego wprost.

**Czego nie wolno zrobić.** Nie wolno dopisywać tłumaczenia do linii, której
brzmienia nie ma w zwrotce, ani „naprawiać” wzorca v8 czy zwrotki tłumacza po to,
żeby brama przestała protestować. Linia bez pokrycia zostaje japońska.

**Czego nie wolno przemilczeć.** Każda taka linia jest liczona i wypisywana
razem z tekstem z gry do `narzedzia/RAPORT_ROZJAZDOW.json`; patcher pokazuje
sumy na ekranie. Cichy brak byłby schowaniem problemu — jawna lista jest wsadem
do następnej paczki dla tłumacza.

**Co nadal zatrzymuje instalację.** Uszkodzony, nieznany albo niezbudowany plik:
gra zostaje wtedy bez zmian. Przebieg zawsze przechodzi **wszystkie** bundle,
zanim cokolwiek zapisze, więc jedno uruchomienie daje pełną listę problemów,
a nie pierwszy z brzegu. `SPRAWDZ.bat` (`patcher_y.py check`) robi to samo
sprawdzenie bez dotykania gry.

Co zrobić z rozjazdem (wszystko po naszej stronie, bez pytań do właściciela):

1. Patcher zapisuje **kopię** pliku, którego nie dało się zbudować, do
   `przyklady/` w folderze patchera (gra zostaje nietknięta).
2. `tools/diagnose_language_gaps.py --samples <folder>/przyklady --write`
   porównuje tekst z gry z korpusem i dopisuje poprawki do
   `data/s6-extra/jp_overrides_y.json` (albo pokazuje, że to plik gry jest inny).
3. Jeśli ten sam plik leży w grze w dwóch wersjach (wydanie i kopia `_Patch`),
   różnice lądują w `data/s6-extra/scenario_copies_y.json`, a patcher zapisuje
   każdą kopię **jej własnym** tekstem.
4. Przebudowa i ponowna instalacja — dopiero teraz, gdy źródło mówi to, co gra.

### Skąd wzięła się awaria PL7 (żeby się nie powtórzyła)

Korpus S6-full był zbudowany z kopii bundli spod adresu `_Patch`
(`aa/StandaloneWindows64/…`) — bo `tools/restore_s6_full.py` brał pierwszą
odzyskaną kopię. Dla 4 scen jest to starszy tekst niż ten, który gra ładuje
z paczki (`BonusMission/…`). Patcher porównywał plan z kopią z paczki i słusznie
odmawiał. Naprawa: `restore_s6_full.py` preferuje kopię wydania, a warianty
pozostałych kopii trzyma `data/s6-extra/scenario_copies_y.json`. Wzorzec v8 był
poprawny od początku — „poprawki” JP w `reconcile_template_v8.py` zostały cofnięte.

## Czego się **nie** robi

- nie obniża się walidacji, żeby zwrotka „przeszła”,
- nie dopisuje się tłumaczeń własnych (poza skrótami limitowymi z uzasadnieniem),
- nie pomija pliku zwrotki, bo „nie ma go w indeksie” — indeks jest naszym
  artefaktem i się go uzupełnia,
- nie mówi się właścicielowi „to nie jest pełne tłumaczenie” — mówi się, ile
  linii zwrotka objęła i że to **cały tekst od tłumacza**.
