# Pakiet do tłumaczenia — SRW OE (NPJH50521)

Ten dokument opisuje pliki, które dostaje tłumacz, i zasady, których musi pilnować, żeby tekst dało
się wstawić z powrotem do plików gry. Pakiet powstaje komendą:

```
python3 tools/translator_export.py --local local --out local/translation
```

Wynik **nie trafia do repozytorium** (gra objęta jest ograniczeniami — patrz `docs/STATUS.md`,
sekcja o prawach): leży w `local/translation/` i jest wysyłany na Google Drive jako osobny folder.

## 1. Co jest w pakiecie

| plik | treść | wiersze |
|---|---|---|
| `00_dialogue.jsonl` | dialogi scen fabularnych + narracja, warunki misji, lokacje, helps, etykiety | 27 101 |
| `01_battle_quotes.jsonl` | cytaty bitewne (ataki, trafienia, porażki, zwycięstwa) | 27 383 |
| `02_items.jsonl` | nazwy itemów i opisy ich efektów | 1 200 |
| `03_skills.jsonl` | umiejętności: nazwa, nazwa z poziomem (`対地 Lv1`), długi efekt, skrót efektu, etykieta | 4 932 |
| `04_config_text.jsonl` | pomoce (`srwDL_Reference`), komendy duchowe, trofea, opisy zakupów DLC, etykiety sklepu, zmiany statusu | 12 631 |
| `05_mission_text.jsonl` | tytuły misji, uwagi do misji, tytuły BGM, nazwy map, teł i oddziałów | 1 311 |
| `10_names_characters.jsonl` | imiona i nazwiska postaci, pseudonimy, serie, seiyuu | 3 388 |
| `11_names_units_weapons.jsonl` | nazwy mechów, serie, nazwy broni, notki encyklopedii mechów | 4 645 |
| `strings.csv` | te same wiersze w arkuszu (do pracy w Excelu/LibreOffice) | 82 591 |
| `index.json` | statystyki: ile wierszy w każdym pliku, ile ma nazwę mówcy | — |

Razem **82 591 wierszy / 2 469 677 bajtów** tekstu japońskiego.

Itemy i umiejętności to jedyne kategorie, w których jeden rekord ma kilka tekstów — każdy jest osobnym
wierszem z tym samym `record` i innym `part` (`name`, `name_level`, `effect`, `effect_brief`, `label`).
Nie trzeba pilnować ich wzajemnej długości: każdy wiersz rośnie niezależnie.

## 2. Jeden wiersz = jeden tekst

```json
{"id": "dlg:eventP00.cpk/DL100_01.bin:1844", "category": "dialogue", "part": "dialogue",
 "jp": "（俺は今、宇宙貿易事業を推進する\n　民間組織『コネクト』にいる…）", "en": "",
 "bytes": 65, "mode": "grow", "max_bytes": null,
 "speaker": {"id": 4501, "jp": "アムロ・レイ", "source": "charalist"},
 "source": {"container": "eventP00.cpk", "member": "DL100_01.bin", "offset": 1844}}
```

* `id` — nie zmieniać; po nim program wstawia tekst z powrotem na swoje miejsce.
* `jp` — oryginał, nie zmieniać (służy do porównania i do weryfikacji).
* **`en` — jedyne pole do wypełnienia.** Puste = tekst nietłumaczony (zostanie japoński).
* `bytes` — ile bajtów CP932 zajmuje oryginał.
* `mode` / `max_bytes` / `suggested_max` — patrz punkt 3.
* `record` — numer rekordu w pliku gry (item/umiejętność). Wiersze z tym samym `record` opisują
  jeden przedmiot; nic z tym nie trzeba robić, to tylko informacja.
* `speaker` — kto mówi. `speaker.jp = null` znaczy „nie znamy nazwy, użyj `speaker.id`”.

## 3. Dwa tryby i budżet miejsca

* `mode = "grow"` — kontener przebuduje rozmiary (`apply` przelicza tabele i offsety), więc
  tłumaczenie może być **dłuższe niż oryginał**. Nie ma `max_bytes`. Uwaga: zbyt długi tekst w
  oknie dialogowym może wyjść za ekran — trzymaj się długości oryginału tam, gdzie się da.
* `mode = "grow"` z `suggested_max` — itemy i umiejętności. Plik gry przebudowuje rekordy, więc
  **limit techniczny nie istnieje**, ale `suggested_max` podaje, ile bajtów CP932 miało oryginalne pole.
  To podpowiedź z UI gry: w oknie listy itemów/umiejętności widać ~20–30 bajtów na nazwę i ~66 bajtów
  na opis, dłuższe teksty zostaną ucięte przy wyświetlaniu. Staraj się nie przekraczać `suggested_max`;
  jeśli musisz, skróć opis zamiast rozciągać nazwę.
* `mode = "slot"` — tekst siedzi w **stałym polu** (tytuł misji, nazwa mapy, tytuł BGM, uwaga do misji).
  Maksymalna długość w bajtach CP932 to `max_bytes`. Tekst dłuższy niż `max_bytes` nie wejdzie —
  trzeba skrócić.

## 4. Zasady, o których trzeba pamiętać

1. **Nie tłumacz tokenów sterujących**: zostaw dokładnie takie same znaki jak w `jp` —
   pełnoszerokościowe `＠0`…`＠9` (odwołania do zmiennych gry), `％` (procent), `＄`, `＃`.
   W cytatach bitewnych często występują na początku/końcu.
2. **Nie zmieniaj liczby przejść do nowej linii** (`\n`) i nie wstawiaj znaków, których nie ma
   w czcionce gry (napisy używają standardowych znaków latin + pełnej szerokości).
3. **CP932**: każde `en` musi dać się zapisać w CP932 (japoński zestaw znaków zawiera pełną
   łacinę, cyfry i znaki interpunkcyjne). Program zgłosi wiersze, które się nie kodują.
4. **Nazwy własne** — trzymaj się jednej pisowni w całym pakiecie; sekcja `10_` i `11_` to źródło nazw,
   których pilnują też dialogi.
5. **Kolejność**: nie zmieniaj kolejności wierszy i nie usuwaj pól — parser jest prosty z założenia.

## 5. Kontrola jakości przed zwrotem

Po wypełnieniu plików uruchamiany jest walidator pakietu:

```
python3 tools/translation_check.py --package <katalog z JSONL> --require-complete --strict
```

Dla każdego wypełnionego wiersza sprawdza: kodowalność CP932, **zgodność tokenów sterujących**
(`＠0`…`＠9`, `%s`, `%%`, `＄n`, `＃`, `{XX}` — te same znaki w tej samej kolejności co w `jp`),
liczbę przejść do nowej linii, twardy budżet `max_bytes` (błąd) i szerokość `suggested_max` (uwaga).
Wiersze z pustym `en` są liczone jako „nietłumaczone”; `--require-complete` zamienia je w błędy,
`--strict` zwraca kod wyjścia 1, gdy są błędy. Raport (`check_report.txt`) zawiera tabelę per plik
oraz pierwsze problemy. Pełny przebieg po 82 591 wierszach zajmuje ~1,6 s.

## 6. Stan pokrycia (2026-10-12)

* **Dialogi: 100% linii ma mówcę** (26 468/26 468); teksty dialogów są wyekstrahowane w całości.
* **Cytaty bitewne: 98,35% rekordów ma mówcę** (451 rekordów = 14 kluczy nie ma nazwy w danych gry —
  dla nich `speaker.jp` jest `null`, tłumacz dostaje ID i musi wnioskować z kontekstu).
* Reszta kategorii: tekst wyekstrahowany w 100% z lokalnie dostępnych plików (szczegóły w
  `docs/COVERAGE.md`, sekcje 1 i 3g).
