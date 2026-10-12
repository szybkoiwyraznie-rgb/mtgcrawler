# Pakiet do tłumaczenia — SRW OE (NPJH50521)

Ten dokument opisuje pliki, które dostaje tłumacz, i zasady, których musi pilnować, żeby tekst dało
się wstawić z powrotem do plików gry. Pakiet powstaje komendą:

```
python3 tools/translator_export.py --local local --out local/translation
```

Wynik **nie trafia do repozytorium** (gra objęta jest ograniczeniami — patrz `docs/STATUS.md`,
sekcja o prawach): leży w `local/translation/` i jest wysyłany na Google Drive jako osobny folder.
Pliki `*.jsonl` są **jedynym** źródłem prawdy; arkusz `strings.csv` to tylko widok do czytania.

## 1. Co jest w pakiecie

| plik | treść | wiersze |
|---|---|---|
| `00_dialogue.jsonl` | dialogi scen fabularnych w kolejności gry + narracja, warunki misji, lokacje, helps, etykiety | 27 101 |
| `01_battle_quotes.jsonl` | cytaty bitewne (ataki, trafienia, porażki, zwycięstwa) | 27 383 |
| `02_items.jsonl` | nazwy itemów i opisy ich efektów | 1 200 |
| `03_skills.jsonl` | umiejętności: nazwa, nazwa z poziomem (`対地 Lv1`), długi efekt, skrót efektu, etykieta | 4 932 |
| `04_config_text.jsonl` | pomoce (`srwDL_Reference`), komendy duchowe, trofea, opisy zakupów DLC, etykiety sklepu, zmiany statusu | 12 631 |
| `05_mission_text.jsonl` | tytuły misji, uwagi do misji, tytuły BGM, nazwy map, teł i oddziałów | 1 311 |
| `06_scenes.jsonl` | **struktura**: 293 sceny — nagłówki (miejsce, czas), kolejność, tytuł misji, znaczniki kopii. Bez tekstu do tłumaczenia | 293 |
| `07_names_characters.jsonl` | imiona i nazwiska postaci, pseudonimy, serie, seiyuu | 3 388 |
| `08_names_units_weapons.jsonl` | nazwy mechów, serie, nazwy broni, notki encyklopedii mechów | 4 645 |
| `strings.csv` | widok tych samych wierszy w arkuszu (tylko z opcją `--csv`; **nie wraca** do gry) | 82 591 |
| `index.json` | statystyki: wiersze i bajty na plik, pokrycie mówców, liczba scen | — |

Razem **82 591 wierszy / 2 469 677 bajtów** tekstu japońskiego (pliki `0x_`, bez `06_scenes`).
Numeracja jest ciągła: 00–08; numer 09 zostaje wolny, a numery 10/11 z poprzednich wydań pakietu
zostały skasowane przy pierwszym przebiegu po zmianie nazw.

Itemy i umiejętności to jedyne kategorie, w których jeden rekord ma kilka tekstów — każdy jest osobnym
wierszem z tym samym `record` i innym `part` (`name`, `name_level`, `effect`, `effect_brief`, `label`).
Nie trzeba pilnować ich wzajemnej długości: każdy wiersz rośnie niezależnie.

## 2. Sceny — kontekst dla tłumacza

Scena = jeden plik zdarzenia w grze. Kolejność scen to kolejność gry: seria, odcinek (`N話`), numer
zdarzenia, wariant DLC. Wiersze `00_dialogue.jsonl` są w **tej samej kolejności** — najpierw cała
scena 1, potem scena 2 itd. Każdy wiersz niesie dwa pola porządkujące:

* `scene` — identyfikator sceny, np. `eventP00.cpk/DL100_01.bin` (ten sam co `id` w `06_scenes.jsonl`),
* `order` — numer elementu w scenie (1, 2, 3…).

`06_scenes.jsonl` otwiera scenę nagłówkiem: `episode`, `episode_label`, `container`, `member`,
`mission` (tytuł misji, z odnośnikiem do wiersza `05_mission_text.jsonl` do przetłumaczenia),
`sections` (elementy typu „miejsce/czas”, np. `コネクト・ステーション／格納庫`) i `counts`.
Scena z `duplicate_of` jest kopią innej (tekst identyczny — tłumaczy się raz), a z `variant_of` to ta
sama scena w innym DLC (część linii jest identyczna; te wiersze mają `copy_of`).

Do czytania w tej formie służy widok:

```
python3 tools/scene_view.py --package local/translation --out local/translation/sceny --zip
```

Wynik to `spis-scen.md` (293 sceny w kolejności) + `epizod-NN.md` (po jednym pliku na odcinek, sceny
z nagłówkami i dialogami po kolei) + `sceny.zip` — wysyłane na Drive razem z pakietem.

**Widok jest plikiem do pracy, nie tylko do czytania.** Pod każdym elementem jest pusta linia `EN:` —
tam wpisuje się tłumaczenie, a dalsze linie (z wcięciem) to jego ciąg dalszy::

    1. [Dialog - セイシロウ・クサナギ] （俺は今、宇宙貿易事業を推進する
       　民間組織『コネクト』にいる…）
       EN: (I'm now at Connect - a civilian
        organization promoting interstellar trade...)

Liczba linii angielskiego musi się zgadzać z liczbą linii japońskiego (okno gry jest rysowane wokół
nich), a dwa niewidzialne znaki widoku — `⏎` (czyści okno) i `<0x0F>` (przełącza czcionkę) — wpisuje
się tak, jak stoją w oryginale. Elementy bez tekstu po `EN:` zostają nietknięte.

Gotowy plik wraca do pakietu **jednym poleceniem** (patrz §6), a nie przez zipowanie: widok nie jest
wysyłany do gry i nie jest przez nią czytany. `scene_view.py` pilnuje zresztą, żeby ponowne wygenerowanie
widoku nie skasowało pracy — plik, w którym jest nieprzeniesiony angielski, jest pomijany
(`--force` nadpisuje świadomie).

## 3. Jeden wiersz = jeden tekst

```json
{"id": "dlg:eventP00.cpk/DL100_01.bin:1844", "category": "dialogue", "part": "dialogue",
 "jp": "（俺は今、宇宙貿易事業を推進する\n　民間組織『コネクト』にいる…）", "en": "",
 "bytes": 65, "mode": "grow", "max_bytes": null,
 "scene": "eventP00.cpk/DL100_01.bin", "order": 1,
 "speaker": {"id": 4501, "jp": "アムロ・レイ", "source": "charalist"},
 "source": {"container": "eventP00.cpk", "member": "DL100_01.bin", "offset": 1844}}
```

* `id` — nie zmieniać; po nim program wstawia tekst z powrotem na swoje miejsce.
* `jp` — oryginał, nie zmieniać (służy do porównania i do weryfikacji).
* **`en` — jedyne pole do wypełnienia.** Puste = tekst nietłumaczony (zostanie japoński).
* `bytes` — ile bajtów CP932 zajmuje oryginał.
* `mode` / `max_bytes` / `suggested_max` — patrz punkt 4.
* `record` — numer rekordu w pliku gry (item/umiejętność). Wiersze z tym samym `record` opisują
  jeden przedmiot; nic z tym nie trzeba robić, to tylko informacja.
* `scene` / `order` — patrz punkt 2 (tylko dialogi).
* `copy_of` — ten wiersz jest kopią innego (wariant DLC); jeśli zostanie pusty, program przepisze mu
  tłumaczenie ze źródła — nie trzeba go wypełniać ręcznie.
* `speaker` — kto mówi. `speaker.jp = null` znaczy „nie znamy nazwy, użyj `speaker.id`”.

## 4. Tryby i budżet miejsca

* `mode = "grow"` — kontener przebuduje rozmiary (przelicza tabele i offsety), więc tłumaczenie może
  być **dłuższe niż oryginał**. Nie ma `max_bytes`. Uwaga: zbyt długi tekst w oknie dialogowym może
  wyjść za ekran — trzymaj się długości oryginału tam, gdzie się da.
* `mode = "grow"` z `suggested_max` — itemy i umiejętności. Plik gry przebudowuje rekordy, więc
  **limit techniczny nie istnieje**, ale `suggested_max` podaje, ile bajtów CP932 miało oryginalne pole.
  To podpowiedź z UI gry: w oknie listy itemów/umiejętności widać ~20–30 bajtów na nazwę i ~66 bajtów
  na opis, dłuższe teksty zostaną ucięte przy wyświetlaniu. Staraj się nie przekraczać `suggested_max`.
* `mode = "slot"` — tekst siedzi w **stałym polu** (tytuł misji, nazwa mapy, tytuł BGM, uwaga do misji).
  Maksymalna długość w bajtach CP932 to `max_bytes`. Tekst dłuższy nie wejdzie — trzeba skrócić.

## 5. Zasady, o których trzeba pamiętać

1. **Nie tłumacz tokenów sterujących**: zostaw dokładnie takie same znaki jak w `jp` —
   pełnoszerokościowe `＠0`…`＠9` (odwołania do zmiennych gry), `％`, `＄`, `＃`. W tekście występują
   wyłącznie: `＃` (dialogi), `%s` i `＠0/＠1/＠4/＠6/＠9` (skille, teksty `config`, misje). W cytatach
   bitewnych często stoją na początku/końcu.
2. **Nie zmieniaj liczby przejść do nowej linii** ani znaków niewidocznych: `⏎` (`\r` — czyści okno
   dialogowe) i `0x0F` (przełącza czcionkę na połówkową — stoi w nazwach i skrótach opisów).
   Walidator pilnuje obu; w widoku wpisuje się je jako `⏎` i `<0x0F>`, a import zamienia je na znaki.
3. **CP932**: każde `en` musi dać się zapisać w CP932 (japoński zestaw znaków zawiera pełną
   łacinę, cyfry i znaki interpunkcyjne). Program zgłosi wiersze, które się nie kodują.
4. **Nazwy własne** — trzymaj się jednej pisowni w całym pakiecie; sekcje `07_` i `08_` to źródło nazw,
   których pilnują też dialogi.
5. **Kolejność**: nie zmieniaj kolejności wierszy i nie usuwaj pól — parser jest prosty z założenia.

## 6. Proces tłumaczenia (jeden, obowiązujący)

1. **Tłumaczysz sceny w widoku** — rozpakowujesz `sceny.zip` i po kolei uzupełniasz linie `EN:`
   w `epizod-NN.md` (kontekst: nagłówek sceny z odcinkiem, tytułem misji i miejscem + japoński tekst
   wszystkich elementów w kolejności gry). Kategorie bez widoku (cytaty bitewne, itemy, umiejętności,
   nazwy) wypełnia się bezpośrednio polem `en` w odpowiednim `*.jsonl`.
2. **Przenieś pracę do pakietu** — widok nie idzie do gry, tylko do jednego polecenia:

   ```
   python3 tools/translation_import.py --views <folder z plikami md albo sceny.zip> --package local/translation
   ```

   Narzędzie wpisuje angielski z linii `EN:` do `00_dialogue.jsonl` (element `3.` w scenie
   `eventP00.cpk / DL100_01.bin` to wiersz o `scene` = `eventP00.cpk/DL100_01.bin` i `order` = 3).
   Tekst, który zepsułby grę — inna liczba linii, zgubiony token `＠0`/`%s`, znak spoza czcionki,
   zgubiony `⏎`/`<0x0F>` — jest **odrzucany i wypisany**, a nie wpisany; poprawiasz i uruchamiasz
   ponownie (polecenie jest bezpieczne wielokrotnie). `--check` pokazuje, co zostałoby wpisane.
3. **Uzupełnij kopie wariantów** — jednym poleceniem, przed kontrolą jakości:

   ```
   python3 tools/translation_copy.py --package local/translation
   ```

   Program przepisuje `en` z wiersza wskazanego w `copy_of` do każdego pustego wiersza-kopii
   (4 186 wierszy), nie nadpisuje niczego wypełnionego i odmawia, gdy `jp` kopii różni się od źródła.
   `--check` pokazuje, co zostałoby zrobione, bez zapisu.
4. **Sprawdź pakiet** przed zwrotem:

   ```
   python3 tools/translation_check.py --package local/translation --require-complete --strict
   ```

   Dla każdego wypełnionego wiersza sprawdza: kodowalność CP932, **tokeny sterujące** (te same znaki
   w tej samej kolejności co w `jp`), liczbę przejść do nowej linii, znaki niewidoczne (`\r`, `0x0F`),
   twardy budżet `max_bytes` (błąd) i szerokość `suggested_max` (uwaga). Puste `en` są liczone jako
   „nietłumaczone”; `--require-complete` zamienia je w błędy, `--strict` zwraca kod wyjścia 1.
   Raport (`check_report.txt`, domyślnie w katalogu pakietu) ma tabelę per plik i pierwsze problemy.
   Wiersze `06_scenes.jsonl` są pomijane jako struktura. Pełny przebieg po 82 591 wierszach: **0 błędów
   w ~1,6 s**.
5. **Zwrot**: wypełnione pliki JSONL wracają na Drive; program `tools/item_skill_write.py --translations
   <plik lub katalog>` wstawia teksty itemów i umiejętności do kontenerów gry, a `tools/apply_strings.py`
   (EVNT) obsługuje narrację scen. Ścieżka zapisu dialogów scen jest następna w kolejce — patrz
   `docs/STATUS.md`.

## 7. Stan pokrycia (2026-10-12)

* **Dialogi: 100% linii ma mówcę** (26 468/26 468), a tekst jest wyekstrahowany w **293 scenach**
  w kolejności gry (224 mają własny tytuł misji, 69 dziedziczy go z wariantu bazowego; 0 bez tytułu).
* **Cytaty bitewne: 98,35% rekordów ma mówcę** (451 rekordów = 14 kluczy nie ma nazwy w danych gry —
  dla nich `speaker.jp` jest `null`, tłumacz dostaje ID i wnioskuje z kontekstu; użytkownik akceptuje
  do ~2%).
* Reszta kategorii: tekst wyekstrahowany w 100% z lokalnie dostępnych plików (szczegóły w
  `docs/COVERAGE.md`).
