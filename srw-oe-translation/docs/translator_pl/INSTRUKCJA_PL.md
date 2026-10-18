# INSTRUKCJA — pakiet `pakiet_PL` (Super Robot Wars OE → polski)

Pakiet na bazie kompletu `pakiet_EN` (109 144 wiersze, stan patcha v17). To jest **pełny,
aktualny** zestaw tekstu gry — zastępuje stare pakiety `widoki.zip` / `sceny.zip`
(widoki v3 z 2026-10-16 są nieaktualne; niczego z nich nie używaj).

Twoje zadanie: wypełnić pole **`"pl"`** w plikach JSONL. Niczego więcej nie zmieniaj.

## 1. Format

Jeden wiersz JSON na linię pliku `.jsonl`. Przykład:

```json
{"id": "dlg:eventP00.cpk/DL100_01.bin:1844", "category": "dialogue", "part": "dialogue",
 "jp": "アムロ「了解。ガンダム、出ます！」", "en": "Amuro: \"Roger. Gundam, launching!\"",
 "pl": "", "bytes": 65, "mode": "grow", "max_bytes": null,
 "speaker": {"id": 4501, "jp": "アムロ・レイ", "source": "charalist"},
 "source": {"container": "eventP00.cpk", "member": "DL100_01.bin", "offset": 1844}}
```

- **`jp`** — oryginał japoński. Źródło prawdy znaczenia, układu linii i tokenów.
- **`en`** — przyjęte tłumaczenie angielskie (cała gra jest już przetłumaczona na EN).
  Traktuj jako referencję: rozstrzygnięcia terminologiczne, co autor miał na myśli,
  co zostało już zdecydowane. Tłumacz z japońskiego; przy wątpliwościach en jest
  interpretacją referencyjną, nie obowiązkiem do skopiowania.
- **`pl`** — tu piszesz tłumaczenie. Puste `""` = do zrobienia.
- **`speaker`** — kto wypowiada kwestię (dialogi i cytaty bojowe).
- **`bytes`/`mode`/`max_bytes`** —budżet (patrz §4).

Pliki:

| Plik | Zawartość | Uwagi |
|---|---|---|
| `00_dialogue.jsonl` | dialogi fabularne (48 881) | sceny w kolejności gry |
| `01_battle_quotes.jsonl` | cytaty bojowe (27 383) | krótkie, "[Kwestia]" — zachowaj 「 」 |
| `02_items.jsonl` | przedmioty (1 200) | twarde limity bajtów |
| `03_skills.jsonl` | umiejętności/duchy (4 932) | twarde limity bajtów |
| `04_config_text.jsonl` | teksty UI/config (16 326) | etykiety, pomoc, warunki misji |
| `05_mission_text.jsonl` | teksty misji (1 285) | tytuły misji, BGM, nazwy map |
| `06_scenes.jsonl` | indeks scen (293) | **struktura — nie tłumacz** |
| `07_names_characters.jsonl` | imiona postaci (3 610) | patrz §6 |
| `08_names_units_weapons.jsonl` | jednostki/bronie (5 008) | twarde limity |
| `09_executable.jsonl` | stringi EBOOT (408) | **tylko ASCII, patrz §5** |
| `10_map_terrain.jsonl` | nazwy terenu (111) | **tylko ASCII, ≤ 12 znaków** |

`tokeny.tsv` — klasyfikacja każdego `%s` w jp (patrz §3). `name_map.tsv` — mapa mówców.

## 2. Polskie znaki diakrytyczne

Font gry został rozszerzony o **18 liter**: `ą ć ę ł ń ó ś ź ż` oraz `Ą Ć Ę Ł Ń Ó Ś Ź Ż`.
Możesz ich swobodnie używać w `"pl"`.

**Nic poza tym.** Każdy inny znak spoza CP932 to twardy błąd importu. Konsekwencje:

- **Nie ma** „ü", „ö", „é", „ā" ani żadnych innych znaków diakrytycznych.
- **Nie ma** polskiego cudzysłowu otwierającego `„` ani półpauzy `–` i pauzy `—`.
- **Są** (w CP932, po 2 bajty/jednostki szerokości): `“ ” ‘ ’ …` oraz ASCII `" ' - ( ) [ ] ? !`.
  Cudzysłów i myślnik wybierz sam — byle konsekwentnie w całej grze (zapisz decyzję
  w `dokumenty/glossary_pl.tsv`).
- ASCII (`a-z 0-9 ! ? …`) = 1 bajt/1 jednostka; litera PL = 2 bajty/2 jednostki
  (rysuje się z komórki pełnej szerokości); znak japoński/fullwidth = 2/2.

## 3. Tokeny i kontrolki (twarde)

- `%s` `%d` `%%` `＠0`…`＠9` `＃` `{XX}` `＄n` `＜主人公名＞` `＜主人公姓＞` —
  przenoś **dokładnie**, ta sama liczba, ta sama kolejność.
- `tokeny.tsv` mówi, jaki `%s` jest czym: **L** = dosłowny placeholder gry (zostaje),
  **T** = token kany 0x0F (w jp `%s` + znak; w tłumaczeniu **znika wraz z następnym
  znakiem** — dokładnie tak samo jak w en), **C** = inna kontrolka (zostaje).
- `\r` (czyszczenie okna dialogowego) — zostaje tam, gdzie jest w jp.
- Liczba `\n` musi się zgadzać z jp (okno i układ rysują się wokół nich).
- Nigdy nie pisz `<0x0F>` ani znaków fullwidth zamiast ASCII (`Ａ１` → `A1`).

## 4. Budżety (twarde)

- **`max_bytes`** — twardy limit bajtów CAŁEGO tekstu (slot o stałym rozmiarze).
  Litera PL liczy się jako 2 bajty, znak fullwidth jako 2, ASCII jako 1.
- **Dialogi/cytaty**: szerokość linii ≤ **46** jednostek (absolutne maksimum 52);
  litera PL = 2 jednostki.
- **`suggested_max`** — ostrzeżenie (pole UI; nie przekraczaj zbytnio).
- Wiersze z `"mode": "grow"` mogą być dowolnie długie bajtowo — limit jest tylko
  szerokością linii na ekranie.

## 5. Kategorie specjalne

- **`09_executable`**: stringi wszyte w `EBOOT.BIN` — **tylko ASCII** (pisarz exe nie ma
  ścieżki dla polskich kodów). Większość to literały silnika / licencje — zostaw
  bez zmian, jeśli en == jp.
- **`10_map_terrain`**: podpisy terenu — **tylko ASCII, max 12 znaków**.
- **`06_scenes`**: indeks scen — nie tłumacz (struktura).

## 6. Nazwy własne

- `dokumenty/glossary.json` to kanon nazw (oficjalne angielskie). Utrzymuj spójność
  z nim w formach łacińskich; polską postać nazw własnych (np. czy transliterować,
  czy zostawić) rozstrzygnij **raz** i zapisz w `dokumenty/glossary_pl.tsv`
  (format: `EN<TAB>PL<TAB>uwaga`, dopisuj na końcu).
- `dokumenty/voice_cards.md` — jak mówi każda główna postać (175 kart).
- `dokumenty/STYLE.md` — przewodnik stylu projektu (zasady tokenów, budżetów i
  techniczne są wiążące tak samo; wskazówki językowe dotyczą angielskiego —
  polskie odpowiedniki to twoja robota, ale decyzje typu „bez dosłowności",
  „zachowaj głos postaci" obowiązują).
- `dokumenty/briefy/`, `dokumenty/bible/` — instrukcje i streszczenia odcinków (EN).

## 7. Jak oddajesz pracę

1. Wypełnione pliki JSONL (te same nazwy, ta sama struktura, zmienione tylko `"pl"`).
2. Całość spakuj zipem o tej samej nazwie i odeślij.
3. Weryfikacja po naszej stronie: `translation_check --field pl` — sprawdzi
   kodowanie, tokeny, kontrolki, liczbę linii i budżety. Wiersze odrzucone
   dostaniesz z powrotem z opisem błędu.

## 8. Czego nie robić

- Nie zmieniaj `id`, `jp`, `en`, `source`, `bytes` ani kolejności wierszy.
- Nie usuwaj wierszy, nie dodawaj nowych, nie przenoś między plikami.
- Nie „naprawiaj" angielskiego w `en` — to pole referencyjne, zapisane w grze.
- Nie tłumacz `06_scenes.jsonl` ani wierszy, gdzie en == jp i to literał silnika
  (zostaw wtedy `pl` = en).
