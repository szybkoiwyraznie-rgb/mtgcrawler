# SRW Y — patch z drugiej zwrotki PL2

## Dostawa i ograniczenia

`SRW_Y_PATCH_PL3_OPISY_MISJI.zip`: Drive `1qvtz7blYhkslWB5gFKUnVIRiMrNRtwZw`, 5 235 407 B, SHA-256 `1c165fc231150fdad68d5eb48bbdff963148fe6e574341f47cc1f40b5502698f` (MD5 `2e244bbc21e3e02b7f9b885f446d540e`). Dwa niezależne przebiegi dały identyczne bajty. Poprzedni `SRW_Y_PATCH_PL2_v2_DIALOGI_BEZ_LAMANIA.zip` (`1JF2HezSf_po0nRDDxGqGOKeK27nRZHbU`, 5 233 892 B) różni się **wyłącznie łamaniem opisów misji** — treść, plan scen i wszystkie inne pola są te same; starszy `SRW_Y_PATCH_PL2.zip` (`1EOnylL66TcrsRgGXi6Cp3P3H9qDMdSDs`) jest w koszu. To instalator budujący pliki lokalnie z oryginałów użytkownika, nie zawiera bundli gry. W katalogu głównym są tylko `CZYTAJ_TO.md`, `PATCH_PL.bat`, `COFNIJ.bat`; reszta w `narzedzia/`.

Zamknij grę, cofnij starszą wersję jej własnym `COFNIJ.bat`, rozpakuj nową paczkę i uruchom `PATCH_PL.bat`. Program weryfikuje oryginały, tworzy i sprawdza kopie `.srwy-original.bak`, zapisuje stan w `narzedzia/STAN_PATCHA.json`. Cofanie: `COFNIJ.bat` z tego samego folderu; nie usuwać stanu ani kopii. Instrukcja i wymagania Pythona są w archiwum.

Nie jest to pełne tłumaczenie całej gry. Czcionki, Windows/BAT oraz rozgrywka **nie zostały zweryfikowane** dla tej wersji; w grze widziano okno dialogowe i listę misji (zgłoszenia z 2026-11-07 i 2026-11-08). Dialogi i narracja **nie mają żadnego łamania od nas** — okno gry zawija je samo. Łamanie mamy w **833 polach**: 16 polach systemowego UI i 817 opisach misji (`mission_detail`/`mission_outline`, z dodatkami), łamanych **tak jak w wersji angielskiej** — ta sama liczba linii, szerokości możliwie blisko linii EN. Ostrzeżenia heurystyki: 158 pól ma linię dłuższą niż najdłuższa linia EN (polski tekst bywa dłuższy niż angielski, a linii nie dokładamy), 3 pola systemowe mają więcej linii niż EN. Budżet znaków nie mierzy szerokości glifów. Patrz `translations/pl2/LAYOUT_REVIEW.json`.

## Zmiana po zgłoszeniu z gry (2026-11-08): opisy misji łamane jak EN

Właściciel pokazał listę misji: polski opis („Insectorzy zbliżają się do
A. Adventu. Wtedy budzi się trójka wybrańców Gettera.”) wychodził poza ekran,
bo ten panel **nie zawija tekstu sam**, a angielska wersja ma to samo zdanie
w trzech liniach. Poprawka w `pl_import.layout()`: tabele `mission_detail`
i `mission_outline` (razem z `-DLC1…-DLC4`) są łamane funkcją
`wrap_matching_english_lines()` — bierzemy najdłuższą linię EN jako budżet,
a gdy polski tekst jest dłuższy, zwiększamy budżet tylko tyle, żeby **zachować
liczbę linii EN**. Wyrazów i tokenów nie dzielimy; wiersz bez wielolinijkowego
EN zostaje bez zmian. Zmieniło się 817 opisów; `LAYOUT_REVIEW.json` urósł
z 16 do 833 pól.

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
`LAYOUT_REVIEW.json` po dodaniu opisów misji ma **833** zmienione pola (16 pól systemowego UI + 817 opisów misji); przy samych polach UI było **16** (ostrzeżenia:
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

Python 3.10+, zależności kitowe `UnityPy==1.25.4`, `pycryptodome==4.2.0`, `lz4==4.4.5`.
Od katalogu `srw-y-translation/` **wszystko, czego trzeba, leży w repozytorium**:
korpus `data/s6-full/`, limity `data/limits_y.json`, grupowanie tabel
`data/s6-derived/groups.json`, plan `translations/pl2/PLAN_PL2.json` i jego audyt.
`local/` jest tylko katalogiem roboczym, który stawia jedna komenda:

```sh
python tools/prepare_local_sources.py --write
```

Kontrola całej drogi (niczego nie zapisuje w repo, tylko w katalogu tymczasowym):

```sh
# 1. pakiet dla tłumacza + manifest — z korpusu w repo
python tools/build_translator_package.py --out-dir /tmp/pkg --source-dir local/s6
# 2. zwrotka zbudowana z planu i wczytana z powrotem musi dać ten sam plan
python tools/pl_fill_return.py --manifest /tmp/pkg/import_manifest.json \
  --plan translations/pl2/PLAN_PL2.json --out /tmp/zwrotka --check --source-dir local/s6
# 3. wydany zestaw patcha powstaje z planu + audytu (bajt w bajt)
python tools/build_y_release.py --plan translations/pl2/PLAN_PL2.json \
  --report translations/pl2/AUDIT_PL2.json --output /tmp/SRW_Y_PATCH_PL4.zip
sha256sum /tmp/SRW_Y_PATCH_PL4.zip   # 136aab63a04b832b61e704fcd98b935654a3c0293f0b37438cf6b7f6e711dfc9
```

`tests/test_patch_pipeline_repo.py` pilnuje tych trzech kroków, a `local/` w ogóle
nie jest do nich potrzebne (testy stawiają własny katalog źródeł z `data/`).

Historyczna droga poniżej (zwrotka `translations/pl2/PL` → manifest → plan) opisuje,
jak powstał `PLAN_PL2.json`. Tej zwrotki **nie da się już wczytać**: została
napisana pod pakiet z misjami (`- misja: …`) i 611 scenami, a dzisiejszy korpus ma
614 scen i inne limity. Treść przekładu jest w planie, więc nic nie zginęło;
kolejna zwrotka wychodzi już z pakietu budowanego w repo i przechodzi krok 2.
Zostawione jako zapis metody:

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
python tools/build_y_release.py --plan local/pl2-plan.json --report translations/pl2/AUDIT_PL2.json --output local/SRW_Y_PATCH_PL3_OPISY_MISJI.zip
```

Przed użyciem patchera wykonaj kopię zapisów gry. Do testów warsztatu: `pytest`, `pytest-subtests`, `Pillow`, `tree-sitter`, `tree-sitter-powershell` oraz zależności kitowe. Żaden z testów offline nie zastępuje testu na komputerze gracza.

## Wydanie na GitHub Releases (2026-11-06): patch PL5

Paczka patchera jest od teraz publikowana w **Releases** tego repozytorium, obok
paczek OE EN/PL:

| | |
|---|---|
| wydanie | <https://github.com/szybkoiwyraznie-rgb/mtgcrawler/releases/tag/patch-y-pl5-e220dfef> |
| tag | `patch-y-pl5-<commit>` |
| załącznik | `srw-y-translation-pl-v5.zip` — 5 172 143 B, SHA-256 `e392f77e…0989c` |
| obok | `SHA256SUMS.txt`, `PL_COVERAGE.json`, `RELEASE_INFO.json` |
| pokrycie | tabele **44 184 z 44 196** wierszy (99,97%), scenariusz **29 017 z 116 359** linii (24,94%), **181 z 615** scen |

Zestaw plików wydania składa `tools/build_y_release_meta.py`:

```sh
python3 tools/build_y_release.py --plan translations/pl2/PLAN_PL2.json \
  --report translations/pl2/AUDIT_PL2.json \
  --output build/patcher/SRW_Y_PATCH_PL5_NAZWY_DUCHOW.zip
python3 tools/build_y_release_meta.py \
  --patch build/patcher/SRW_Y_PATCH_PL5_NAZWY_DUCHOW.zip \
  --out-dir build/release_y_pl5 --asset-name srw-y-translation-pl-v5.zip
```

Instalator jest podlinkowany w wydaniu z Dysku projektu
(`srw-y-translation-pl-v5.zip`, Drive `168T0wy90ilwQhwx6aOY03myhghUeujMw`): GitHub
blokuje `uploads.github.com` w piaskownicy, w której powstaje paczka, więc załącznika
nie da się tam wysłać z tego środowiska. Załączniki dokłada workflow
`.github/workflows/release-y.yml` (buduje z repo, testuje, wysyła pliki do wydania po
tagu) — działa po scaleniu do `main` albo po nadaniu tagu `patch-y-*`.

`RELEASE_INFO.json` wiąże wydanie z planem (`plan_sha256`), audytem
(`nonempty_slots`, `empty_slots`, `overrides_applied`) i commitem źródłowym, więc
da się sprawdzić, z czego powstał załącznik. Patch nie zawiera żadnych plików gry —
buduje je u użytkownika z jego oryginałów i zostawia kopie `.srwy-original.bak`.
