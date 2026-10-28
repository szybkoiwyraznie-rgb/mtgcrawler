# SRW Y — trwałe zaplecze importu i patchowania

Stan na 2026-10-28: pierwsza częściowa paczka PL1 przygotowana i sprawdzona offline; test na Windows i w grze oczekuje właściciela. Starsze uwagi w punktach poniżej zachowują historię braków; aktualne rozwiązanie i komendy są w sekcji „Pierwszy instalator PL1”.

## Punkt wyjścia

- Pierwsza zwrotka tłumacza jest w `translations/pl1/PL/` jako źródło, nie jako patch gry.
- `tools/pl_import.py` i generowanie manifestu istnieją, ale `docs/IMPORTER_Y.md` wymaga odtworzenia prywatnego manifestu z danych S6 i porównania go z wysłanym pakietem v8. Manifestu i S6 nie ma w repozytorium.
- Ten sam dokument stwierdza, że nie istnieje jeszcze zbiorczy orchestrator import → wszystkie sceny i tabele → patch. Nie należy przedstawiać pojedynczych skryptów ani patchera v2 jako dowodu, że cały proces dla rzeczywistej zwrotki jest ukończony.
- Katalog `local/` i `build/` jest ignorowany. Same narzędzia są w repozytorium, ale ignorowanie całego obszaru roboczego nie gwarantuje zachowania manifestów i innych danych niebinarnych potrzebnych kolejnej sesji.

## Cel

Odzyskać i utrwalić w repozytorium reużywalny warsztat i niebinarne wejścia potrzebne do walidacji i przygotowania kolejnych zwrotek, a oryginalne i zmodyfikowane binarne assety gry pozostawić poza repozytorium. Nie zakładać, że patchowanie istniejących bundli jest możliwe bez dostępu do oryginalnych bajtów: ustalić zakres operacji offline i wykonywanych u właściciela. Nie pomijać kontroli tożsamości źródeł ani nie publikować niezweryfikowanego patcha.

## Zachowany wzorzec v8

`translations/template-v8/` to tekstowa zawartość oryginalnego pakietu v8
(`README.md`, sceny i widoki), bajt w bajt z pobranego z Drive archiwum
`plik_dla_tlumacza_v8.zip`, SHA-256
`71c075111e7cddadbc531f9b6084f120530b0638b298fc0be50ccb0cf286b57c`.
Plik `SHA256SUMS` pozwala sprawdzić wszystkie 50 tekstów. Nie ma tam binarnych
assetów gry. To materiał dostarczony już tłumaczowi, nie manifest adresów gry:
nie zastępuje brakujących powiązań elementów z rekordami S6.

`python tools/check_pl_template.py translations/pl1/PL` sprawdza sumy całego
wzorca i porównuje zwrotkę po wyzerowaniu wyłącznie wartości `PL:`. Wynik PL1:
**10/10 identycznych tekstów**. Kod 0 oznacza zgodność wzorca, 1 — różnice,
2 — problem z odczytem. To potwierdza strukturę, JP, EN i limity względem v8,
ale nie poprawność samych tłumaczeń ani ich adresów docelowych.

## Zachowany tekstowy snapshot S6-full

`data/s6-full/` zawiera tekstowe `scenario.jsonl` (120 794 wiersze / 614
scen) i `tables.jsonl` (44 344 wiersze / 144 tabele) z odtworzenia za pomocą
istniejącego `tools/restore_s6_full.py`. Dane pobrano z istniejących na Drive
archiwów, bez proszenia właściciela o nowe pliki. SHA-256 zgodne z zapisem
w `HANDOFF_READING_WYNIKI_2026-10-27.md`:
`03455b67d97e29b637eba5f0f29efc0491f24d5557bf8dd563cbb2d2b646df93`
i `45e15696d11afd02afcc1af24e8979bafdf6ecd5864a4167e2b736c79fc2d577`.
To same rekordy tekstowe i metadane, **bez assetów binarnych**.

**S6-full nie jest snapshotem v8** (ten miał 120 665 wierszy / 611 scen,
44 340 wierszy / 143 tabele). Nie przepinać go pod stary manifest, nie zakładać
zgodności adresów ani nie ignorować różnic: powiązanie ze wzorcem v8 wymaga
osobnej, sprawdzalnej procedury. Te pliki pozwalają pracować z udokumentowanym
snapshotem bez ponownego ekstraktowania przy każdej sesji.

## Pierwsza kontrola PL1 bez danych gry

`python tools/check_pl_limits.py translations/pl1/PL` kontroluje tylko wpisane
wartości względem limitów *zwróconych przez tłumacza*. Nie wymaga S6, nie
zmienia zwrotki, zwraca JSON i kod 1 przy błędach. Nie jest importerem:
nie potwierdza autentyczności limitu, źródła, numeracji, tokenów, powtórzeń,
układu ani adresów docelowych. Pełna weryfikacja źródłowa nadal jest obowiązkowa.

Wynik: 26 279 wypełnionych i 20 529 pustych slotów; jeden wpis przekracza
podany limit: `02_cytaty_bitewne.md`, element 28254, **44 / 38 znaków**.
Nie zmieniono tłumaczenia ani nie uznano tej kontroli za pełną walidację.

Testy w bieżącej sesji: pełny `pytest -q -rs`: **583 passed, 0 skipped,
4558 subtests**. Kod i wynik możliwe do odtworzenia bez plików gry.

## Ustalenia wymagające dalszej pracy

Wcześniejsze instrukcje były niejednoznaczne: patcher v2 instaluje już
zbudowane bundle i był testowym zestawem, natomiast dokument importera wprost
mówi, że zbiorczy builder jeszcze nie powstał. Nie jest więc prawdą, że sam
patcher realizuje drogę od zwrotki do gry. Na Drive odnaleziono paczkę v8,
ale osobnych plików `scenario.jsonl`, `tables.jsonl` ani manifestu wyszukiwanie
nazw nie zwróciło. Odtworzone S6 z czytanek to inny snapshot: nie wolno go
podstawić jako v8 bez niezależnego porównania. Konieczne jest zachowanie
odpowiednich niebinarnych danych, proweniencji i procedury ich odtwarzania;
dalej należy wykonać właściwą walidację PL1 i uzupełnić brakujące etapy.


## Wiązanie PL1 ze snapshotem S6-full (2026-10-28)

`tools/bind_v8_return.py --input translations/pl1/PL --output local/pl1-manifest.json`
wiąże wyłącznie dostarczone pliki z zachowanym S6-full. Najpierw sprawdza
sumy oryginalnego wzorca i zgodność zwrotki, następnie dopasowuje **każdy**
numerowany element do rekordu jego sceny lub widoku, sprawdza kompletną
numerację, prezentację JP i EN oraz tożsamość źródła powtórzeń. Wynik ma
własne pieczęcie S6-full i przechodzi `verify_bindings`; **nie udaje starego
manifestu v8** i nie dowodzi bajtowej identyczności starych i nowych danych.

Powiązanie objęło 10 plików i 52 101 elementów. Pełny importer odrzucił partię
z 531 diagnostykami: m.in. 260 U+201C, 140 pustych źródeł, 98 niezgodności
tokenów oraz 3 błędy ich kolejności. Zgłosił również przekroczone limity
**odziedziczonych powtórzeń** (poprzednie narzędzie sprawdzało tylko wartości
wpisane bezpośrednio); dlatego twierdzenie o jednym problemie dotyczyło
wyłącznie tego wstępnego zakresu. Nie zmniejszać rygoru ani nie ukrywać
błędów, by uzyskać pozornie kompletny import. Przygotować jawny raport i
zachować bezpieczne części bez zmiany oryginału zwrotki.

## Bezpieczny częściowy import

`tools/import_safe_subset.py --manifest local/pl1-manifest.json --input
translations/pl1/PL --source-dir data/s6-full --output-dir local/pl1-safe`
nie zmienia zwrotki: uruchamia ten sam importer, odrzuca tylko całe grupy PL,
których element albo powtórzenie nie przejdzie walidacji, i ponawia walidację
bez osłabiania kontroli. Inne błędy powodują przerwanie. Powstają plan
`import.json`, `quarantine.json` i oczyszczone wejście `input/` w nowym,
atomowo publikowanym katalogu. Żadna grupa nie jest cicho pomijana; oryginalne
sumy kanoniczne i przyczyny są w raporcie.

Dla aktualnego PL1: **479 slotów w kwarantannie**, 21 008 pustych po
kwarantannie, **29 323 zaakceptowanych rekordów** (w tym powtórzenia):
25 060 kluczy tabel i 4 263 wystąpienia scen. Raport zachowany w
`translations/pl1/QUARANTINE.json`. Liczba rekordów nie jest liczbą osobnych
wpisów tłumacza. To wciąż tylko plan — pliki gry i instalator jeszcze nie
zostały zbudowane ani sprawdzone w grze.

## Przebudowa bundli

`data/game_text_bundle_index.json` przechowuje ścieżki, SHA-256 oryginałów,
nazwy obiektów, PathID i język; bez bundli gry. Generator:
`tools/build_game_index.py`. `tools/apply_y_plan.py` łączy plan z indeksem,
odmawia innych oryginałów i rozbieżnych rekordów, przebudowuje obiekty i
sprawdza je ponownie. Eksperymentalna przebudowa PL1: 12 bundli, 25 060
wpisów tabel JP / 24 919 EN i po 4 263 wystąpienia scen JP i EN; pozostałe
141 kluczy nie występuje w EN. Wszystkie sprawdzono offline. Instalator,
backupy i test w grze to nadal osobne bramki.

## Pierwszy instalator PL1 (2026-10-28)

Patcher jest podobny do OE: rozpakować paczkę, zamknąć grę i uruchomić
`PATCH_PL.bat`; `COFNIJ.bat` przywraca oryginały. Pierwszy start tworzy lokalne
środowisko Python i instaluje zależności. Paczka nie zawiera assetów ani
przebudowanych bundli: narzędzia budują je lokalnie z kopii użytkownika.
Każdy oryginał i kopia `.srwy-original.bak` jest kontrolowana hashem;
`STAN_PATCHA.json` w folderze patchera jest wymagany do cofnięcia. Gdy plik
jest inny niż oryginał (np. po starym teście), patcher odmawia zamiast go
nadpisać. Najpierw należy cofnąć poprzednią wersję.

Reprodukcja z czystego repozytorium (Python 3.10+, UnityPy, pycryptodome, lz4):

```sh
python tools/bind_v8_return.py --input translations/pl1/PL --output local/pl1-manifest.json
python tools/import_safe_subset.py --manifest local/pl1-manifest.json --input translations/pl1/PL --source-dir data/s6-full --output-dir local/pl1-safe
python tools/build_y_release.py --plan local/pl1-safe/import.json --report local/pl1-safe/quarantine.json --output build/SRW_Y_PATCH_PL1_v1.zip
```

Druga komenda celowo wymaga nowego katalogu wynikowego, aby nie nadpisać
poprzedniej partii. Generator kitów czyta liczbę rekordów, bundle i raport z
wejścia; następne zwrotki wymagają osobnego powiązania, walidacji, pakowania
oraz testów, a nie odtwarzania S6 z gry. Weryfikację pełnych wejść i źródła
pozostawiono obowiązkową.

Testy 2026-10-28: 601 passed, 0 skipped, 4558 subtests. Sprawdzono instalację
z rozpakowanego ZIP-a na oddzielnych kopiach 12 oryginalnych bundli: wynik
identyczny z niezależną przebudową, 12 backupów poprawnych i po `COFNIJ`
12/12 hashy oryginałów przywróconych. Nie jest to test na Windows ani w grze.

Paczka właściciela: **`SRW_Y_PATCH_PL1_v1.zip`**, Drive
`1-AwnIJhqBfCzH57rO8Na1q7qKMPM0waK`, 2 204 913 B, SHA-256
`9a86f8862943876511dae06611dc3f62b09e207472e0698c0088810ca67efca3`.
Pobrano ją ponownie z Drive: bajt w bajt identyczna, ZIP CRC poprawne.
W osobnym katalogu ponownie wykonano powiązanie, kwarantannę i generator
wyłącznie z wejść repozytorium: cały ZIP bajt w bajt identyczny. Nie zawiera
bundli ani żadnych binarnych plików gry.

## PL1 v3 — kompletna otrzymana zwrotka (nie kompletna gra)

Poprzedni v1 był częściowy i ma 479 grup w kwarantannie. **v3 go zastępuje**:
26 279/26 279 wypełnionych slotów i wszystkie ich powtórzenia; 20 529 pustych
slotów pozostawiono bez zmian. Łącznie 29 873 wystąpienia, 25 444 klucze tabel
i 4 429 wystąpień scen. 22 jawne korekty celu zapisano w
`translations/pl1/CORRECTIONS.json`, oryginalnej zwrotki nie zmieniano. Audyt
wszystkich pierwotnych 479 grup i 550 ich celów to
`translations/pl1/AUDIT_479.json`; informacja dla tłumacza to
`docs/INFORMACJA_DLA_TLUMACZA_PL1.md`.

Odtwarzanie v3 z repo (katalogi `local/` i `build/` są ignorowane):

```sh
python tools/bind_v8_return.py --input translations/pl1/PL --output local/pl1-manifest.json
python tools/audit_full_return.py --manifest local/pl1-manifest.json --input translations/pl1/PL --source-dir data/s6-full --corrections translations/pl1/CORRECTIONS.json --historical-quarantine translations/pl1/QUARANTINE.json --output-plan local/pl1-full-plan.json --output-report translations/pl1/AUDIT_479.json
python tools/build_y_release.py --plan local/pl1-full-plan.json --report translations/pl1/AUDIT_479.json --output build/SRW_Y_PATCH_PL1_v3.zip
```

`CORRECTIONS.json` jest ściśle powiązany z aktualną zwrotką, nie stosować go
do kolejnej partii bez ponownego audytu. Raport jest weryfikowany względem
bajtów planu; do ZIP-a trafiają narzędzia i plan, nie pliki gry. Przed instalacją
v3 należy cofnąć v1 jego własnym `COFNIJ.bat`, a v3 rozpakować do nowego
folderu; zachować kopie i stan nowej instalacji.

Instalacja i cofnięcie v3 przetestowane offline na kopiach 12 bundli; 12/12
hashy plików, backupów i cofniętych oryginałów zgodnych. Nie testowano Windows
ani gry, a limity znaków i łamanie tekstu są heurystykami.

Udostępniona paczka: `SRW_Y_PATCH_PL1_v3.zip`, Drive
`1FBDNVOz4i2hqI0o_b7y_tJ3HoGic5HwZ`, 2 584 328 B, SHA-256
`bb22a57417bd581d21d43c43d6905f8ca2ea08c44b6c1086f3ed45e530db5d7d`.
Pobrana ponownie z Drive: identyczna bajtowo, poprawna CRC ZIP. Niezależne
powtórzenie wiązania, audytu i pakowania z repo dało identyczny ZIP. Pełne
testy warsztatu: **612 passed, 4 558 subtests passed**. Informacja dla tłumacza
jest również na Drive: `18g_4wEVPhcWxj_K0dCY70RFoJLhDGe4Z`.

## PL1 v4 — eksperymentalna poprawka układu

Po in-game zgłoszeniu v3: `QA_PL1_LAMANIE.md`. Porównanie planu v3 z v4
wykazuje wyłącznie zmiany podziałów w 3 582 rekordach tabel; sceny Lua są
identyczne. Pokrycie i zawartość zwrotki pozostają takie same. V4 usuwa
nieuzasadnione wewnętrzne podziały w tabelach i wymaga weryfikacji w grze,
w tym ekranów jeszcze niepokazanych. Nie potwierdza działania zawijania
we wszystkich widgetach ani poprawności list punktowanych.

Regeneracja (po `python tools/bind_v8_return.py --input translations/pl1/PL
--output local/pl1-manifest.json`):

```sh
python tools/audit_full_return.py --manifest local/pl1-manifest.json --input translations/pl1/PL --source-dir data/s6-full --corrections translations/pl1/CORRECTIONS.json --historical-quarantine translations/pl1/QUARANTINE.json --output-plan local/v4-plan.json --output-report translations/pl1/AUDIT_LAYOUT_V4.json
python tools/compare_pl_layout.py local/v3-delivered-plan.json local/v4-plan.json
python tools/build_y_release.py --plan local/v4-plan.json --report translations/pl1/AUDIT_LAYOUT_V4.json --output build/SRW_Y_PATCH_PL1_v4.zip
```

`local/v3-delivered-plan.json` to `plan.json` z oryginalnej dostarczonej
paczki v3; alternatywnie można odtworzyć go kodem repo z commitu `bcd0c8d`.
Nie nadpisuj historycznego `AUDIT_479.json` z v3. Aby przejść na v4, zamknij
grę i cofnij v3 **jego** `COFNIJ.bat`, zachowaj backupy, rozpakuj v4 do nowego
katalogu i użyj jego `PATCH_PL.bat`. V4 nie instaluje się na aktywnym v3.

## PL1 v5 — UI z szacowaniem na podstawie EN

Właściciel potwierdził działanie v4 w grze i poprawny układ opisów, ale
zaobserwował brak automatycznego zawijania w kilku ekranach UI i narracji.
V5 zawija wybrane UI i prolog według najdłuższej linii EN; opisy i sceny Lua
bez zmian. 117 rekordów zmienionych tylko podziałem, 16 miejsc ma więcej
niepustych linii niż w EN: możliwe przycięcie lub konieczność redakcji.
`docs/QA_PL1_LAMANIE.md` określa zakres, ograniczenia i udokumentowany test.

Reprodukcja od dostarczonych danych w repo (plan v4 należy wydobyć z ZIP v4):

```sh
python tools/bind_v8_return.py --input translations/pl1/PL --output local/pl1-manifest.json
python tools/audit_full_return.py --manifest local/pl1-manifest.json --input translations/pl1/PL --source-dir data/s6-full --corrections translations/pl1/CORRECTIONS.json --historical-quarantine translations/pl1/QUARANTINE.json --output-plan local/v5-plan.json --output-report translations/pl1/AUDIT_LAYOUT_V5.json
python tools/audit_ui_wrap.py local/v4-plan.json local/v5-plan.json --output translations/pl1/LAYOUT_V5_REVIEW.json
python tools/build_y_release.py --plan local/v5-plan.json --report translations/pl1/AUDIT_LAYOUT_V5.json --output build/SRW_Y_PATCH_PL1_v5.zip
```

W katalogu głównym paczki są tylko BAT-y i instrukcja; plan, narzędzia,
środowisko, stan instalacji i raport są w `narzedzia/`. Na starszej v4 najpierw
uruchomić jej `COFNIJ.bat`, a v5 rozpakować do nowego folderu. Test offline
aktualizacji i cofania na 12 bundlach passed; v5 nie jest jeszcze sprawdzona w grze.
