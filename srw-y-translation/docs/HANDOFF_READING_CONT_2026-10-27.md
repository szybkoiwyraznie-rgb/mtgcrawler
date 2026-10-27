# SRW Y — czytanki: co dostarczono i co zostało (2026-10-27)

Kontynuacja [`HANDOFF_READING_Y_2026-10-27.md`](HANDOFF_READING_Y_2026-10-27.md).
Gałąź `arena/ff68be19-mtgcrawler`, draft PR #28
(`https://github.com/szybkoiwyraznie-rgb/mtgcrawler/pull/28`).

## 1. Co zostało dostarczone

**Pliki `.md`** w [`docs/reading/pl-2026-10-27/`](reading/pl-2026-10-27/)
(14 plików, 63 834 352 B): `README.md`, `rozdzial-01..07.md`,
`sceny-poza-rozdzialami.md`, `sceny-bez-misji.md`, `deployment.md`, `piloci.md`,
`mechy.md`, `encyklopedia.md` plus `receipt-summary.json` (skrót dowodów).

Paczka na Drive: `SRW_Y_CZYTANKI_2026-10-27.zip`, 18 375 102 B,
SHA-256 `55322200b3b461efc57119560e53e107f906c6aeaffd05b777fbe4811d4ec71f`,
id `1ThXiK2pm_4oCvvpRCYLUHbJQJziU0IMf`. Zawiera te same `.md`, **pełny**
`receipt.json` (12 MB; listy braków, rejestry zdarzeń, protagonistów) oraz
deterministyczny `srwy_reading_PL.zip` z narzędzia.

**To nie jest pełne polskie wydanie.** Tłumacz nie zwrócił wypełnionych `PL:`;
pusty pakiet v8 nie jest zwrotem. W trybie `--reference` każdy brak ma jawny
`[BRAK PL: ...]`, a pod spodem dwie wyraźnie nazwane kolumny: `JP (źródło
tłumaczenia)` i `EN (odniesienie oficjalne, NIE polski)`. Angielski nie jest
podkładany jako polski. Liczba jawnych braków w recepcie: **115 153**;
użytych unikalnych adresów: **111 756**.

**Encyklopedia Y jest w czytankach jako dane**, nie jako zgadywane przypisanie:
`encyklopedia.md` ma wszystkie wpisy czterech rodzin tabel `dic_text_pilot`,
`dic_text_robot`, `dic_text_name`, `dic_text_word` (podstawka + DLC) z kluczem
Shared Data, adresem wiersza S6 i tekstem JP/EN. `piloci.md` i `mechy.md` mają
też własne, czytelne indeksy biografii/opisów. Nadal **nie** ma biografii przy
pierwszym wystąpieniu — powód w §4 A.

## 2. Co zmieniono w kodzie

- `tools/build_reading_y.py`: `--reference`, `--evidence`, `Reader.reference_lines`,
  `Reader.label` (jednowierszowe etykiety dla nagłówków i mówców),
  `localized(..., as_label=True)` w miejscach nazw, `dictionary_key()` (odwrócenie
  `m_Key → m_Id`), `dictionary_stats()`, `encyklopedia.md`. Receipt ma teraz
  `schema: 2` przy trybie referencyjnym/evidencji, `reference_mode`,
  `dictionary_evidence_sha256`, `dictionary_stats`. Pełna pieczęć źródeł i zakaz
  nadpisania wyniku zostały zachowane.
- `tests/test_reading_reference.py` — 10 testów syntetycznych: brak PL nie znika,
  JP/EN są zawsze oznaczone, przetłumaczony wiersz nie jest zastępowany,
  nagłówki pozostają jednowierszowe, encyklopedia ma klucze Shared Data,
  **dokładna równość ID w kluczu `dic_pilot_P1_00_0` nie tworzy powiązania
  biografii**, evidencja jest reprodukowalna i pilnowana w trakcie buildu.
- `.github/workflows/srw-y-import.yml` — dodano nowy plik testów.
- `data/dictionary_owner_assets.json` — tylko metadane z katalogu Addressables
  i listingu właściciela (11 nazw, bundli, rozmiarów); zero danych gry.

Testy w odtworzonym środowisku: **pełne `pytest -q`: 525 passed, 27 skipped,
80 subtests passed**; zestaw CI (9 plików): **180 passed, 57 subtests passed**.
Historyczny wynik poprzedniego agenta to 169 passed / 1 skipped / 57 subtests —
różnica to 10 nowych testów i odtworzone prywatne wejścia w `local/`.

## 3. Jak to odtworzyć (prywatne `local/`, nie w Git)

Świeży checkout nie ma `local/`. Wejścia pobrane z Drive i zweryfikowane
SHA-256 rozpakowano do `local/reading-research/`. Prywatne skrypty odtworzenia
(`restore_s6_public.py`, `restore_s6_full.py`, `scan_*`, `supplied-objects-next.json`)
są w tym katalogu i nie są częścią repo.

```
# 1) pełny korpus S6 ze wszystkich odzyskanych bundli
.venv/bin/python tools/reading_index.py \
  --bundles local/reading-research/{SRW_Y_MISSION,SRW_Y_GLOSY,srw_y_text,\
srw_y_tekst,srw_y_dlc_bundle,srw_y_free_patch} \
  --out local/reading-research/context-index-next.json
# 2) język każdego pliku Lua z adresu w catalog.json + 10 katalogach DLC
../.venv/bin/python local/reading-research/restore_s6_full.py
# 3) czytanki
../.venv/bin/python tools/build_reading_y.py \
  --source-dir local/reading-research/s6-full \
  --index local/reading-research/context-index-next.json \
  --evidence data/dictionary_owner_assets.json --reference \
  --out local/reading-research/reference-edition
```

Zmierzone wyjście pełnego S6: **120 794 wiersze scen, 614 scen, 144 tabele,
44 344 wiersze tabel, 948 plików Lua JP i 976 EN**, 0 niesparowanych tabel.
Uwaga: to **inny snapshot** niż pakiet v8 / historyczny handoff (120 665 wierszy,
611 scen, 143 tabele, 44 340 wierszy). Różnica wynika z tego, że odtworzenie czyta
wszystkie sześć języków ze wszystkich odzyskanych bundli; 2 724 warianty Lua
`cn/tw/hk/kr` są celowo pomijane, a 3 fizyczne warianty jednego assetu JP
(`cse20_2010_0201710a_sdemo.lua`) różnią się między bundlami — zachowano
pierwszy i zapisano konflikt w `restore_report.json`. **Nie wolno mieszać**
tego S6 z pieczęcią źródeł v8 przy imporcie zwrotki: `pl_import` słusznie
odrzuci taką zwrotkę jako nieaktualną.

## 4. Co jeszcze nie jest zrobione (A–D z poprzedniego handoffu)

### A. Biografie/opisy przy pierwszym wystąpieniu — NADAL OTWARTE

Teksty encyklopedii są (`dic_text_*`), ale **rekordy właścicielskie nie**.
Bazowy `catalog.json` (SHA-256 `12c17bf9…73b4`) wskazuje **11 assetów**
(`Pilot/RobotDictionaryEntryTable` + `_D1.._D4` oraz `WordDictionaryEntryTable`),
łącznie **58 461 B**. `reading_audit.py` widzi 10 z nich (klasy `PilotDicEntryList`
i `RobotDicEntryList`); 11. to `WordDicEntryList`. `data/dictionary_owner_assets.json`
ma pełną listę z bundlami i rozmiarami.

Ponowny audyt na świeżym indeksie, 741 nazwanych obiektach MonoBehaviour ze
wszystkich bundli i 11 katalogach (`prerequisite-mode-audit-next.json`):
**11/11 bundli nie ma w żadnej odzyskanej paczce**, 0 obiektów źródłowych dla
10 audytowanych assetów, 0 obiektów `ScriptGraphAsset`. Nie ma też obiektów z
rekordami encyklopedii wśród 358 nienazwanych MonoBehaviour (są to komponenty UI,
tabele lokalizacyjne i presety).

Dlaczego nie łączymy po kluczu: `dic_text_pilot` ma 427 grup logicznych,
`dic_text_robot` 297, `dic_text_name` 29, `dic_text_word` 78. Tylko 16 grup
pilotów i 29 robotów nie ma **żadnego** dokładnego ID w rekordach gry, ale
większość grup pasuje do wielu różnych pól (`listFacialSettingData`,
`listShotdownMessageData`, `listHaveSpiritCommandData`, `defaultReferenceId`…),
więc równość `dic_pilot_X` z jakimś `X` nie wyznacza właściciela. W `piloci.md`
i `deployment.md` pierwsze wystąpienia nadal mają
`[BRAK POTWIERDZONEGO POWIĄZANIA BIOGRAFII/OPISU]`.

Żeby zamknąć A: potrzebne są te 11 małych bundli z katalogu gry (nie presety!),
potem odczytanie schematu `PilotDicEntryList` / `RobotDicEntryList` /
`WordDicEntryList`, odtworzenie `entry → character/robot ID → klucze dic_text_*`
i dodanie biografii przy pierwszym wystąpieniu z pełną proweniencją. Bez tego
osobny indeks tekstów (nawet czytelny) nie spełnia wymagania właściciela.

### B. 91 nierozwiązanych PPtr — bez zmian, bez nowej prośby o presety

Audyt odtworzył dokładnie: **91 wskaźników, 0 celów w dostarczonych obiektach,
0 przypadków tego samego PathID w innym CAB**. To **nie jest dowód brakujących
plików u właściciela**; zgodnie z decyzją właściciela nie prosimy o kolejne
presety na tej podstawie. Do zrobienia, gdy będą dostępne grafy zdarzeń (§4 C):
sprawdzić, czy te referencje są rozwiązywane w runtime/catalogu, a nie dopasowywać
je po nazwie.

### C. Chronologia scen / wywołań zdarzeń — NADAL NIEPOTWIERDZONA

`receipt.json` ma `literal_order_verified: true`,
`conditional_event_order_verified: false`, `mission_chronology_verified: false`.
Audyt: 589 kompozycji z `script_file`, z czego **368 wskazuje na
`Unity.VisualScripting.ScriptGraphAsset`**, 218 ma `serifuOnly = 1` bez wpisu
w katalogu, 3 nie mają ani wpisu, ani flagi. Te 368 wpisów mapuje się na
**366 różnych bundli, z których 0 jest w odzyskanych archiwach**. Kolejność
literałów Lua (potwierdzona dla renderowanych plików) nie dowodzi kolejności
wywołań warunkowych zdarzeń; czytanki mają bloki zdarzeń opisane jako
„kolejność źródłowa, nie kolejność rozegrania”. Do zamknięcia C potrzebne są
te grafy (albo rejestr wywołań z runtime) i statyczna analiza przepływu.

### D. Pozostałe ograniczenia przed pełnym wydaniem

- **Brak polskiego tekstu.** 115 153 jawne braki; ostatni pakiet v8 ma puste
  `PL:`. Bez zwrotu od tłumacza nie wolno ogłaszać wydania pełnym.
- **Importer zwrotek niezweryfikowany** na prawdziwym, wypełnionym zwrocie z
  pakietu v8 w tym checkoucie; `pl_import` był testowany syntetycznie i na
  prywatnych danych poprzedniej sesji. Trzeba przeprowadzić `pl_import`
  + `build_reading_y.py` bez `--reference` na realnym zwrocie i porównać
  pieczęcie źródeł (UWAGA na inny snapshot S6 z §3).
- **Pełna przebudowa bundle'i / patch / test w grze**: `runtime_tested = false`.
  Poprzedni `runtime_tested = true` dotyczył wcześniejszego patcha UI, nie tego
  wydania czytanek ani nowego korpusu.
- **Cytaty bitewne pozostają poza czytankami**; deployment listuje uczestników
  bez momentów wejścia do bitwy; protagonista jest jeden na misję (domyślnie
  mężczyzna, kobieta tylko przy wyłącznie żeńskim wariancie).
- **Różnice snapshotów** (§3) trzeba wyjaśnić przed użyciem czytanek jako
  materiału do nauki numeracji zwrotki v8.

## 5. Czego nie robić (decyzje właściciela, nadal wiążące)

- Nie dopasowywać encyklopedii po imieniu, prefiksie `dic_pilot_*` ani po
  podobieństwie klucza; nie robić fuzzy matching.
- Nie podkładać angielskiej prozy jako polskiej; każdy obcy tekst musi być
  wyraźnie oznaczony jako odniesienie.
- Nie interpretować 91 PPtr jako brakujących plików u właściciela i nie prosić
  o presety na tej podstawie.
- Nie twierdzić, że kolejność literałów Lua to chronologia zdarzeń.
- Nie wykorzystywać `samples-b080-2026-10-27.zip` (inny projekt).

## 6. Następny krok (rekomendacja)

1. Jeśli właściciel chce zamknąć A: pobrać z gry 11 bundli z
   `data/dictionary_owner_assets.json` (58 kB łącznie) i przesłać jako małą paczkę.
   To precyzyjnie zidentyfikowany brak dowodu, **nie** prośba o presety.
2. Jeśli właściciel chce zamknąć C: potrzebne są bundlie `ScriptGraphAsset`
   (366 nazw z katalogu; audyt ma je w `script_graphs[].catalog_entries`).
3. Gdy przyjdzie zwrot tłumacza: zregenerować S6 w tej samej wersji co pieczęć
   v8, uruchomić `pl_import`, potem `build_reading_y.py` bez `--reference`
   i porównać `receipt.json`.
