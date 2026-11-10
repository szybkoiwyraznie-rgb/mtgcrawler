> **Status: NAPRAWIONE 2026-11-10 — ten dokument opisuje stan zastany.** Wzorzec i snapshot
> zgadzają się teraz na 160 694 z 160 694 elementów; poniższe pomiary i uzasadnienia
> zostają jako zapis tego, co było nie tak i dlaczego naprawa wygląda właśnie tak.
> Narzędzia: `tools/reconcile_template_v8.py` (naprawa), `tools/realign_return.py`
> (przeniesienie tłumaczeń). Wpisy w `docs/EXPERIMENT_LOG.md` z 2026-11-10.

# Wzorzec v8 a snapshot S6-full — gdzie się rozjeżdżają (2026-11-10)

**Do czego to jest.** `tools/bind_v8_return.py` odrzuca całą partię, jeśli
wyświetlana linia japońska nie zgadza się z numerowanym rekordem S6-full. Ta
brama jest słuszna — to jedyny dowód, że linia tłumacza trafia na właściwy
rekord. Ten dokument odpowiada na **inne** pytanie: skoro brama pada, to kto się
myli — zwrotka czy my? Odpowiedź jest mierzona: bramę puszczono na **samym
wzorcu v8 + doklejce v8.1**, bez zwrotki.

## Wynik pomiaru

`tools/diag_template_vs_snapshot.py`, wynik w `data/template_snapshot_diff_y.json`:

| miara | liczba |
|---|---|
| plików (49 v8 + doklejka v8.1) | 50 |
| elementów | **160 695** |
| zgodnych z S6-full | 160 520 |
| **niezgodnych** | **175** |
| — inna treść JP | 174 |
| — numer bez wiersza w snapshocie | 1 |
| — niezgodne EN | 0 |

Rozkład: `sceny/odcinek-20.md` 172, `sceny/dlc-BonusMission.md` 3.
Żaden inny plik nie ma ani jednej różnicy. Cztery pliki nie mają elementów
z numeracją i słusznie nie są liczone: `spis-misji.md`, `spis-scen.md`,
`odcinek-90.md`, `widoki/09_grupy_bez_mowcy.md`.

**Wniosek, wprost:** te 175 różnic są w **wzorcu, który dostarczyliśmy
tłumaczowi**, nie w jego zwrotce. Brama odrzuciłaby każdą zwrotkę tego typu —
także nasz własny, podpisany szablon z repozytorium, którego sum pilnuje
`SHA256SUMS`.

## Cztery różne klasy rozjazdu — nie wolno ich streszczać jednym „JP się różni”

### 1. Zdezaktualizowany blok: `odcinek-20.md` element 104 należy do wiersza, który doklejka już przejęła

To najważniejsze odkrycie i **jedyna** przyczyna przesunięcia o jeden.

Scena `cse20_2010_0201710a` ma w snapshocie **276** wierszy, ale `load_scenes()`
zostawia **274**: dwa wiersze przenosi do doklejki v8.1
(`data/package_appendix_y.json`), bo w chwili budowy v8 nie było ich tekstu:

| `string_id` | mówca | tekst w snapshocie | gdzie trafia dziś |
|---|---|---|---|
| `sdemo:103.1` | カナメ | 「私達から…ライブは決行すると」 | tylko doklejka `D2/1` |
| `sdemo:49.0` | ドロシー | 「ワルキューレはキラキラしている。／それを否定するの？」 | doklejka `D2/2` |

Wzorzec pokazuje jednak **277** elementów: 275 w `odcinek-20.md` + 2 w doklejce.
Element **104 pliku głównego** to osierocony, starszy wariant tego samego
wiersza `sdemo:49.0`:

```
104. [Dialog - ドロシー] 「ワルキューはキラキラしている。
   それを否定するの？」
```

Brakuje w nim `レ` (`ワルキュー` zamiast `ワルキューレ`) — to tekst spoza
snapshota, w korpusie `ワルキューはキラキラしている` nie występuje **ani raz**,
a `ワルキューレはキラキラしている` występuje raz, w wierszu `sdemo:49.0`.
Czyli wiersz `sdemo:49.0` jest dziś renderowany **dwa razy**: raz jako
zdezaktualizowany element 104 pliku głównego, raz poprawnie w doklejce.

Dowód pozycyjny, że to właśnie ten blok jest nadmiarowy: po jego pominięciu
wszystkie pozostałe elementy sceny trafiają w wiersze bez przesunięcia
(element 105 ↔ wiersz 104, 106 ↔ 105, …), a liczba się zgadza
(275 − 1 = 274 = liczba wierszy po przeniesieniu dwóch do doklejki).

Jak do tego doszło: logika w `build_translator_package.load_scenes()` usuwa
przeniesione wiersze z `scene['rows']`, ale `translations/template-v8/sceny/odcinek-20.md`
nie został po tej zmianie przeliczony — plik zachował blok 104 i numerację
105–275. Doklejka ma 6 sekcji: 4 sceny (`cse20_3000_0100000a`,
`cse20_3499_0107410a`, `cse20_8000_0000300a`, `cse20_3738_0999900a`)
nie występują we wzorcu v8 wcale (148 wierszy), a 151 wierszy to faktycznie
nowe kwestie w dwóch scenach, które już są w v8.

### 2. Numer elementu bez wiersza w snapshocie

`odcinek-20.md` element **275** (ostatni w scenie) nie ma wiersza: 274 wiersze
po przeniesieniu dwóch do doklejki, a wzorzec pokazuje 275 elementów. To ten sam
skutek co w punkcie 1 — nadmiarowy element 104 przesuwa całą resztę o jeden
i ostatniemu elementowi brakuje wiersza. Po usunięciu bloku 104 problem znika
sam, bez osobnej naprawy.

### 3. Prawdziwe różnice treści JP — trzy pozycje

| plik | scena | element | wzorzec v8 | snapshot S6-full |
|---|---|---|---|---|
| `dlc-BonusMission.md` | `cse20_1001_0001100a` | 279 | 「友情…」 | 「友達…」 |
| `dlc-BonusMission.md` | `cse20_1001_0001100a` | 284 | 「帰るよ、$n！／続きは『Ａアデン』でやるから！」 | 「…続きは別の場所でやるから！」 |
| `dlc-BonusMission.md` | `cse20_1002_0000100a` | 277 | 「…生きて**返**ってくるのよ！」 | 「…生きて**帰**ってくるのよ！」 |

Te trzy nie są artefaktem formatowania i **nie dają się** sprowadzić do jednej
reguły — idą w różne strony:

- `生きて返ってくる` — w korpusie **0** wystąpień; `生きて帰ってくる` — 4.
  Tu prawdopodobnie myli się **wzorzec** (literówka `返`/`帰`).
- `『Ａアデン』` — w korpusie **61** wystąpień (nazwa po zmianie szyldu kawiarni);
  `別の場所でやるから` — 1, tylko w tym wierszu. Tu prawdopodobnie myli się
  **snapshot** (tekst sprzed przemianowania).
- `友情` (13 wystąpień) vs `友達` (94) — oba poprawne; bez pliku z gry nie
  rozstrzygniemy, która wersja jest w tym wierszu.

Czyli: **żadne z dwóch źródeł nie jest w całości wiarygodne** — wzorzec ma
starsze warianty w jednym miejscu, snapshot w innym. Rozstrzygnięcie wymaga
odczytu rekordu z bundla gry; identyfikator `string_id` każdej z 175 pozycji
jest w raporcie JSON.

### 4. Uwaga o markerach miejsc (`～…～`)

Markery miejsc mają w snapshocie surowy tekst z pustą linią i pełnoszeroką
spacją (`\n～ワルキューレ\u3000楽屋～`), a renderer v8 podaje jedną linię.
Ta różnica **nie trafia** do listy 175 — brama porównuje tekst po renderowaniu,
więc markery przechodzą. Zostawiam to tu jako ostrzeżenie: porównywanie surowego
`jp` z korpusu (tak jak robiłem to na początku) daje fałszywe trafienia.

## Co z tego wynika dla zwrotki PL3

Zwrotka `Y_PL3.zip` wypełnia właśnie te dwa pliki: `odcinek-20.md`
(2 533 sloty) i `dlc-BonusMission.md`. **Trafia w 5 z 175 spornych elementów**
i wszystkie 5 ma wypełniony `PL:`:

| plik / scena | element | co tłumacz przetłumaczył | wartość wiersza |
|---|---|---|---|
| `odcinek-20.md` / `cse20_2010_0201710a` | 124 | duplikat-przesunięcie | `sdemo:69.0` |
| `odcinek-20.md` / `cse20_2010_0201710a` | 185 | duplikat-przesunięcie | `sdemo:130.0` |
| `dlc-BonusMission.md` / `cse20_1001_0001100a` | 279 | 「友情…」 | `dlgev:216.0` |
| `dlc-BonusMission.md` / `cse20_1001_0001100a` | 284 | 「Ａアデン…」 | `dlgev:221.0` |
| `dlc-BonusMission.md` / `cse20_1002_0000100a` | 277 | — (pusty slot) | `dlgev:225.0` |

To nie jest problem teoretyczny: 4 przetłumaczone kwestie czekają na
rozstrzygnięcie, a brama słusznie nie chce ich przypisać po numerze.

## Rozstrzygnięcie (2026-11-10, po awarii PL7)

Ten dokument zapisywał otwarte pytanie: czy prawdę mówi wzorzec v8, czy snapshot.
Odpowiedź przyszła z pliku gry i jest jednoznaczna — **wzorzec v8 był poprawny**,
a mylił się snapshot, bo był zbudowany z niewłaściwej kopii bundla.

Obie sceny mają w grze po dwie kopie: wydanie (`BonusMission/…`, bez `_Patch`)
i kopię spod adresu `_Patch` (`aa/StandaloneWindows64/…`).
`tools/restore_s6_full.py` brał **pierwszą odzyskaną kopię**, czyli dla 4 scen
właśnie `_Patch` — starszy tekst. Gra ładuje kopię z paczki.

| element | wzorzec v8 (= gra, paczka) | snapshot (kopia `_Patch`) |
|---|---|---|
| 279 | 「友情…」 | 「友達…」 |
| 277 | 生きて**返**ってくる | 生きて**帰**ってくる |

Dwie „poprawki” w `tools/reconcile_template_v8.py` (`JP_FIXES`) przepisały
wzorzec pod zły snapshot, a potem — żeby brama porównująca wzorzec ze zwrotką
przestała protestować — przepisano też `translations/pl3/PL`. Tłumacz wysłał
poprawnie (`translations/pl3/surowe/PL.zip` ma `友情…` i `返`); poprawka była
nasza, nie jego.

Naprawa: `JP_FIXES` jest puste, `JP_REVERTS` cofa oba brzmienia, zwrotka w repo
wróciła do tekstu tłumacza, `restore_s6_full.py` preferuje kopię wydania,
a warianty pozostałych kopii trzyma `data/s6-extra/scenario_copies_y.json`
(patcher zapisuje każdą kopię jej własnym tekstem).

## Czego ten dokument nie rozstrzyga — i czego nie wolno zrobić

- **Nie wolno** przestawić numeracji w `odcinek-20.md` ani w doklejce bez
  decyzji: oba pliki są już w rękach tłumacza, a w doklejce wypełniono 279
  slotów. Przeliczenie pliku głównego przesunie numery 104–275 (i wszystkie
  przyszłe `PL:`), przeliczenie doklejki przesunie jej numerację.
- **Nie wolno** dopisać wierszy wprost do `data/s6-full/scenario.jsonl` —
  unieważnia `compaction.source_sha256` w `data/reading-index-sourcebound.json`
  (patrz `tools/s6_extra.py`).
- **Nie wolno** osłabić `validate_rendered` „żeby przeszło”.

Odtworzenie pomiaru:

```sh
python3 tools/diag_template_vs_snapshot.py --out data/template_snapshot_diff_y.json
python3 -m pytest tests/test_template_snapshot_diff.py
```
