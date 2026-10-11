# HANDOFF — SRW OE (Super Robot Wars Operation Extend) — fan-translation EN

> Samodzielny dokument przejęcia. Przeczytaj też `AGENTS.md` (guardrails), `docs/METHOD.md`,
> `docs/EXTRACTION_MAP.md`, `docs/TRANSLATION_GUIDELINES.md`, `docs/EXPERIMENT_LOG.md`,
> `docs/STATUS.md`. Wszystko poniżej = stan na moment handoffu.

## 0. Cel
Przetłumaczyć **całą grę** SRW OE (PSP) na angielski; dostarczyć jako **`.xdelta`** na
japońską kopię użytkownika. Twardy wymóg: **wzrost tekstu** (grow) tam, gdzie to możliwe.
**Nic nie tłumaczymy, dopóki setup nie obejmuje 100% kategorii** (decyzja użytkownika).

## 1. Środowisko i ograniczenia (KRYTYCZNE)
- Repo: `mtgcrawler`, branch **`arena/c656a5df-mtgcrawler`** (tylko ten; push tylko tu).
- Cała praca pod **`srw-oe-translation/`**.
- `.gitignore` wyklucza `google_drive/` i `srw-oe-translation/local/` — **NIGDY nie commituj**
  ISO/EDAT/CPK ani pełnego skryptu JP.
- **Nie modyfikuj oryginałów.** Etykietuj fakty `[ZWERYFIKOWANE]` vs hipotezy.
- Tłumaczenie **fresh** (Akurasu odrzucone). Nie nazywaj projektu „przetłumaczonym”.
- **Piaskownica robi rollbacki** (HEAD potrafi wrócić do bazy `d4e2488`). Po rollbacku:
  `git add -A && git commit && git pull --rebase origin arena/c656a5df-mtgcrawler && git push`.
  Pliki w workspace trwają niezależnie od commitów.
- **Wydajność:** `cpk_write.load(cpk)` jest WOLNE (deszyfruje EDAT); do skanów używaj
  `cpk_table.read_cpk_table` (tylko ITOC). Kopiuj duży cpk do `/tmp/c.cpk` (find-loopy na
  `google_drive/*.cpk` potrafią zawiesić piaskownicę). Nie iteruj `cpk_write.load` w pętli.
- **Testy:** `cd srw-oe-translation && python3 -m unittest discover tests -q` (ostatnio **336 OK**, 1 skipped).

## 2. Kontenery tekstu — klasyfikacja grow vs fixed
| Kontener | Plik(i) | Tryb | Stan |
|---|---|---|---|
| Fabuła/dialogi (EVNT) | `eventP00..P09` | **GROW** | dowiedzione (rekord z polem długości + patch ISO bootuje) |
| Menu tytułowe | `configst.cpk/sysmes.bin` | **STAŁA szerokość** | dowiedzione 3 bootami (stałe offsety ZEWNĘTRZNE) |
| Help/opisy/systemowe | `configst/sysmes` | grow możliwy (shift) | `sysmes_shift` integralność verified; render niepotwierdzony |
| Słownik postaci (nazwy) | `imenu00` `srwDL_CharaDictionary` | do zbudowania grow | pula NUL; ekstrakcja verified |
| Encyklopedia/Reference | `imenu00` `srwDL_Reference` | do zbudowania grow | pula NUL |
| Nazwy mechów/serii/seiyū | `config0X` (DLC) | do zbudowania grow | pula NUL |
| Opisy przedmiotów/skilli | `configst` (`srwDL_Item`,`srwDL_Skill_Tag`) | do zbudowania grow | — |
| Nazwy map/terenu | `config00` | do zbudowania grow | pula NUL |
| Okrzyki bitewne | `mesbtl00`+DLC `mesbtl0X` | do zbudowania grow | linia ≤46 (render) |

**Zasada użytkownika:** grow wszędzie, gdzie budowa pozwala; stałe TYLKO tam, gdzie struktura
pliku nie pozwala (jak menu tytułowe). Nie „dla bezpieczeństwa”.

## 3. sysmes.bin (configst) — struktura + wniosek z 3 bootów `[ZWERYFIKOWANE]`
- Nagłówek: `SMES | u32 size@4 | u32 count@8 | u32 table@0xc`.
- **Wewnętrzna tablica odnośników** `~0x22f0–0x2368`: `count × {u32 offset, u32 id}`.
  Np. `{off=0x91a0, id=0x45e}` = „ゲームスタート". Czytana dla **opisów/help**.
- **Etykiety menu tytułowego NIE mają tu wskaźnika** — gra czyta je pod **stałymi offsetami
  zapisanymi POZA sysmes**. Dowód: 3 booty patcha shift → CREDITS ok, DOWNLOAD LIST ucięty,
  reszta rozjechana o jeden slot ⇒ **każdy przesuw puli rozjeżdża menu**. Jedyna bezpieczna
  transformacja tytułu = **bajt-w-bajt (równa długość slotu)**.
- `sysmes_shift.py` (committed): `shift_translate` przesuwa pulę, przepisuje wewnętrzną tablicę
  (strict `v>off`, size@4, pomija shared-tail), `verify` = multiset-diff (edycje usunięte,
  reszta musi być pusta). **Integralność True** — ale render NIEZWERYFIKOWANY, a dla MENU
  tytułowego shift jest NIEBEZPIECZNY (patrz wyżej). Używaj shift tylko dla stringów czytanych
  przez wewnętrzną tablicę (opisy), nie dla etykiet tytułu.

## 4. EVNT (eventP00..) — strumień rekordów `[ZWERYFIKOWANE na eventP00]`
- Member = zdeszyfrowany EDAT; EVNT body = samo-rozmiarowy strumień rekordów (`u32 type`,
  `u32 length`, payload). Rekordy łańcuchują się po `length`.
- **Typy tekstowe:** `0x000001b7` narracja (prolog), `0x000000c9` dialog/monolog,
  `0x000001b6` **nagłówek sceny** (miejsce/czas, np. „宇宙世紀００７９ 地球圏 中立宙域").
- Nagłówek narracji: `type|length|parameter`; **parameter = indeks sekwencji** (0,1,1,2…),
  **NIE mówca**.
- **Mówca NIE jest w rekordzie tekstu** — to stan VM ustawiany poprzedzającymi komendami
  portretu/postaci (typy `0x160` pozycje ASCII `$(x y z /`, `0x1b8`, `0x145`…). Przypisanie
  mówcy = zdekodować te komendy + zmapować ID pilota na `srwDL_CharaDictionary`.
- **Placeholdery w tekście**: ＜主人公名＞ itd. — zachować w tłumaczeniu.
- `extract_scenes.py` (committed): sceny grupowane po `0x1b6`, chronologia, `monologue`
  (（…）), `placeholders`. Na eventP00: **19 scen, 1598 linii**. `speaker` = null (TODO).
  **Monologi/narracja nie potrzebują mówcy** — mówca tylko dla kwestii z portretem.
- Linia ≤ **46 znaków półszerokich** (okno komunikatu; `BOX_WIDTH=46`).

## 5. Narzędzia (wszystko pod `srw-oe-translation/tools/`)
- `cpk_write.py` (`load`/`rebuild`), `cpk_table.py` (`read_cpk_table` ITOC-only), `crilayla.py`
  (dekompresja CRI), `edat.py` (EDAT).
- `iso_pack.py patchiso` — patch pełnego ISO9660 (obchodzi limit 0x100000000, rośnie, bootuje).
- `configst_pack.py` — PAC layer (`ALIGN=0x800`, `DIR_OFF=0x10`); byte-identical bez edycji.
- `sysmes_pack.py` — `equal_translate` (równa długość, NIE przesuwa; DEFAULT_EDITS), `apply_edits`,
  `grow_one`, `string_starts`.
- `sysmes_shift.py` — `shift_translate` + `verify` (grow puli + przepisanie tablicy).
- `extract_tables.py` — pule NUL (imenu00/config0X/config00/mesbtl) → JSONL {member,key,text}.
- `extract_structured.py` — rekordy {u32 len,u32 id} + nazwy NUL (config00/configst) → JSONL.
- `export_strings.py` — eventy → JSONL {member,record_index,record_offset,source,target}
  (BEZ speakra). `apply_strings.py` — wkleja tłumaczenia (rośnie).
- `extract_scenes.py` — sceny z chronologią/nagłówkami/placeholderami (speaker TODO).
- `scan_translatable.py` — inwentaryzacja; `dlc_catalog.json`, `local/extracted/*.jsonl`.
- Testy: `tests/test_sysmes_shift.py`, `test_sysmes_pack.py`, `test_configst_pack.py`, + reszta (331).

## 6. Zasoby (poza git)
- **Google Drive** (connector `google_drive`, użytkownik podłączył): katalog DLC
  `155zwn1AuwR_O8Sx0UpNPGIi52ysAlaPU` (eventP00-P09, config0X, mesbtl0X, tacsys, configst).
  eventP00 file id `1or9mKqqJzL_0aFqHOxLCTLKN3lEyNG1w`.
- Na PC użytkownika: `D:\SRWOE\SRW_OE_1.08\` (rozpakowane PSP_GAME), `D:\SRWOE\iso\` (ISO),
  Python 3.12 (brak `lz4` — używać crilayla.py). PPSSPP do testów.
- **Nie ma kluczy klicen** — EDAT z PSP_GAME są zaszyfrowane; `config07.EDAT` z DESYGNOWANEGO
  źródła jest zdeszyfrowany (`head=0x75091211`). Deszyfrowanie wymaga klicen (brak) — na razie
  pracujemy na tym, co mamy (configst via CPK, config07 decrypted, eventP00 via CPK).

## 7. Zadania OTWARTE (kolejność)
1. **Dekodowanie mówcy** w EVNT: rozpoznać komendę portretu/postawi, wyciągnąć ID pilota,
   zmapować na `srwDL_CharaDictionary`, dopisać `speaker` do `extract_scenes`. (Monologi pomijamy.)
   **Postęp (2026-10-11, HIPOTEZA):** `tools/speaker_probe.py` (read-only, tylko liczby) pokazuje, że
   u16 na offsecie `+10` rekordu `0xc9` zmienia się per linia jak stan mówcy (w rozmowie naprzemienne
   pary kluczy, np. `0x1195`/`0x119e`; 620 linii w 11 członkach eventP00). NIE zweryfikowane jako
   indeks słownika. Następny krok: mapowanie na `srwDL_CharaDictionary` + sprawdzenie zmian mówcy
   względem komend `0x160`/`0x1b8`/`0x145`. Dopiero po tym `speaker` idzie do tłumaczeń.
   **Wynik mapowania (2026-10-11, `tools/speaker_map.py`):** ID w slotach +0x30..+0x38 słowników
   CharaDictionary (399 ID, 0 duplikatów) pokrywają tylko 9 z 60 kluczy (500–516) — **61 z 608 linii**
   (10%). Pozostałe 51 kluczy (700s, 1000s, 2800s, 3700s, 4500s; najczęstsze 0x1195/0x119e = 4501/4510)
   nie występuje w żadnym słowniku z 25 pul imenu00–32 (16 z nich nie jest czytanych przez writer, ale
   czytane przez `cpk_table`). Hipoteza do sprawdzenia: klucze 4500s/3700s to ID z innej tabeli
   (np. `face*.EDAT` lub tabele bazowej gry spoza Dysku). Bez tego mówca NIE jest rozstrzygnięty.
2. **Repack grow dla każdej puli NUL** (char dict, Reference, config0X, config00, mesbtl):
   **Postęp (2026-10-11):** `tools/dict_pool_shift.py` — `srwDL_CharaDictionary*` ma zmierzony układ
   (12 wskaźników u32 na rekord + ciągłe stringi NUL + stałe bloki ID na +0x30..+0x3c). Rebuild bez
   zmian jest bajt-w-bajt na 15/15 niepustych pul (imenu00-19, 10 pul jest pustych: count=0).
   Grow/shrink z `verify` przechodzi na pulach w pamięci (nie zapisano CPK). Strażnik odrzuca edycję,
   gdy słowo w prefiksie wskazuje do wnętrza obszaru stringów (0 takich na realnych danych).
   **Nie zweryfikowane:** odwołania spoza puli (inne kontenery) i render w grze. Pozostałe pule
   (RoboDictionary, Reference, Shop, DLC_ID) mają INNY układ — jeszcze nie zmierzone.
   znaleźć tablicę wskaźników/offsetów, zbudować `*_shift` z `verify` (wzór: `sysmes_shift`).
   Stałe zostaje tylko to, co nie ma wewnętrznych wskaźników i ma stałe offsety zewnętrzne.
3. **Budżety znaków** per string dla kategorii stałych (slot→max znaków, z szerokością W/F).
4. **apply** (wklejanie tłumaczeń) dla każdej puli NUL + pełny pipeline xdelta.
5. Dopiero 1–4 gotowe i przetestowane → tłumaczenie.

## 8. Komendy (PC użytkownika, PowerShell)
```powershell
cd D:\SRWOE\mtgcrawler\srw-oe-translation
# patch ISO z rozbudowanego drzewa:
python tools\iso_pack.py patchiso "D:\SRWOE\iso\Super_Robot_Taisen_OE_v1.08_JPN_PSP-PLAYME\Super Robot Wars OE (Japan).iso" "D:\SRWOE\patch.iso" "D:\SRWOE\patch"
# grow jednego pliku event:
python tools\grow_event_text.py <member.bin> --at <off> --text "<EN>" -o <out.bin> --check
# eksport/sceny event:
python tools\extract_scenes.py eventP00.cpk --out scenes.json
# repack CPK (PAC):
python tools\configst_pack.py pack <orig.cpk> --replacements rep.json --out <out.cpk>
# repack sysmes (równa długość / shift):
python tools\sysmes_pack.py <in.cpk> <out.cpk>          # equal-length
python tools\sysmes_shift.py <in.cpk> <out.cpk>         # grow (NIE dla menu tytułowego)
```

## 9. Znane pułapki (nie powtarzaj)
- Shift/grow **menu tytułowego** = rozjazd (stałe offsety zewnętrzne). Tylko equal-length.
- `apply_edits` (przebudowa z mapy przesunięć) rozjeżdża referencje zewnętrzne → garble.
- In-place `v>=off` psuje własny base pointer → używaj `v>off`.
- `verify` musi usuwać klucze edycji (angielski ASCII niewidoczny dla multisetu JP).
- `compress_literal` (rozszerzanie) CRASHOWAŁO w grze — używaj tylko shrink/identity w crilayla.
- Nie nazywaj projektu przetłumaczonym; nie commituj binariów gry.
