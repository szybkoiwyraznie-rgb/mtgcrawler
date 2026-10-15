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
- **Każdy `.bat` dla użytkownika otwiera OKNO WYBORU pliku/folderu — nigdy nie każe wpisywać
  ścieżki z palca.** Użytkownik zwracał na to uwagę dwa razy (2026-10-12 `PATCH_ISO_TEST.bat`,
  2026-10-14 `HOKUS_POKUS.bat`). Gotowy selektor: `tools/pick_path.py` (tkinter; presety
  `iso|dlc|package|translation`; wynik do pliku, kody 0/2/3) + podprogram `:pick` w
  `HOKUS_POKUS.bat` — kopiuj go do nowych batów. `set /p` na ścieżkę tylko jako awaryjne
  wyjście, gdy `pick_path.py` zwróci 3 (Python bez Tk). Pilnuje tego test
  `tests/test_pick_path.py::UserFacingBatRuleTests`.
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
| Menu tytułowe + help/systemowe | `configst.cpk/sysmes.bin` | **GROW** (tablica względna, `sysmes_pack.translate_bytes`) | struktura zmierzona 2026-10-14 (1182/1182 wpisów), 3 booty „shift" wyjaśnione nowym modelem; render po wzroście NIEZWERYFIKOWANY |
| Słownik postaci (nazwy) | `imenu00` `srwDL_CharaDictionary` | do zbudowania grow | pula NUL; ekstrakcja verified |
| Encyklopedia/Reference | `imenu00` `srwDL_Reference` | do zbudowania grow | pula NUL |
| Nazwy mechów/serii/seiyū | `config0X` (DLC) | do zbudowania grow | pula NUL |
| Opisy przedmiotów/skilli | `configst` (`srwDL_Item`,`srwDL_Skill_Tag`) | do zbudowania grow | — |
| Nazwy map/terenu | `config00` | do zbudowania grow | pula NUL |
| Okrzyki bitewne | `mesbtl00`+DLC `mesbtl0X` | do zbudowania grow | linia ≤50 (tyle gra sama rysuje; zalecane 46) |

**Zasada użytkownika:** grow wszędzie, gdzie budowa pozwala; stałe TYLKO tam, gdzie struktura
pliku nie pozwala (jak menu tytułowe). Nie „dla bezpieczeństwa”.

## 3. sysmes.bin (configst) — struktura `[ZWERYFIKOWANE offline 2026-10-14]` (poprzedni wniosek o „stałych offsetach" ODWOŁANY)
- Nagłówek: `SMES | u32 size@4 | u32 count@8 (1182) | u32 1@0xc`.
- Od 0x10: **`count × {u32 off, u32 id}`**. Pula zaczyna się pod **`base = 0x10 + count·8 − 4`**
  (= 0x24fc w oryginale; pierwszy string `'Ａ\0\0'` dzieli 4 bajty z polem id ostatniego wpisu).
  **`off` jest WZGLĘDNE wobec `base`**, wpis k wskazuje k-ty string sekwencyjnej puli (NUL, pad 4).
  Sprawdzone na wszystkich 1182 wpisach oryginału (0 wyjątków); `parse`+`build` = bajt w bajt.
- **Etykiety menu tytułowego SĄ w tablicy**: wpisy 906–911 (ゲームスタート id 0x28c, ライブラリー 0x28d,
  リファレンス 0x28e, クレジット 0x28f, ダウンロードリスト 0x2c6, データインストール 0x290) + drugi komplet
  157/158/168/169. Wynik „3 bootów shift" (CREDITS ok, DOWNLOAD LIST ucięty, reszta o slot) to dokładnie
  to, co przewiduje ten model dla starego `_grow` (przesuwał tylko słowa o wartości > offsetu
  bezwzględnego, więc wskaźniki w oknie 0x24fc za edycją zostawały stare); hipoteza stałych offsetów
  przewiduje inne śmieci. Nie ma dowodu na żaden odczyt sysmes po stałym offsecie.
- Jedyna poprawna transformacja: **`sysmes_pack.translate_bytes`** — pula przepisana sekwencyjnie
  z nowymi stringami (dowolna długość), słowo k = nowy offset względny stringu k, id/nagłówek bez zmian,
  `size@4` odświeżone, string 0 nietykany; `verify(orig, new, edits)` musi być puste. Build #6 użył
  starego `apply_edits` (offsety bezwzględne, 3× pula) → wszystkie komunikaty systemowe = śmieci.
- Render po wzroście w grze **NIEZWERYFIKOWANY** (pierwszy boot po naprawie = test). `sysmes_shift.py`
  to tylko shim. Eksport wierszy: `sysmes_text.py` = jeden wiersz na CAŁY string (1080); stare wiersze-
  ogony (1141 w pakiecie 2026-10-14) builder ignoruje, `--merge-into --prune-fragments` je usuwa.

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
- Linia: zalecane ≤ **46 jednostek półszerokich**; twardy limit pisarzy = najszersza linia, jaką gra
  sama rysuje w danym rodzaju (`export_strings.GAME_WIDEST`, spis całego skryptu 2026-10-14: dialog 52,
  cytat 50, narracja 56, help 66; reszta ma podłogę 46). 46 pochodziło z pierwszej sceny; 316 linii
  dialogu gry ma 50. Znaki sterujące (`\r`) nie mają szerokości. **Nie sprawdzone w grze** dla linii
  ASCII 47–52 — hipoteza (czcionka półszeroka).

## 5. Narzędzia (wszystko pod `srw-oe-translation/tools/`)
- `cpk_write.py` (`load`/`rebuild`), `cpk_table.py` (`read_cpk_table` ITOC-only), `crilayla.py`
  (dekompresja CRI), `edat.py` (EDAT).
- `iso_pack.py patchiso` — patch pełnego ISO9660 (obchodzi limit 0x100000000, rośnie, bootuje).
- `configst_pack.py` — PAC layer (`ALIGN=0x800`, `DIR_OFF=0x10`); byte-identical bez edycji.
- `sysmes_pack.py` — `parse`/`build`/`translate_bytes`/`verify` (model względny 2026-10-14; `apply_edits`/`equal_translate`/`grow_one` = nakładki, dowolna długość),
  `grow_one`, `string_starts`.
- `sysmes_shift.py` — shim na `sysmes_pack.translate` (stary model shift był błędny; zostawiony dla starych wywołań).
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
**Stan 2026-10-15 wieczór (najnowszy; `EXPERIMENT_LOG.md` §21.23–21.25):** rekordy conv-B mają **TRZY**
wskaźniki względne: `+32` (baza członu), `+36` (pula), **`+52` = `ostatnia_granica_tekstu + delta` (słowa
parametrów za tekstami)** — pisarz kopiował `+52` dosłownie do buildu #13; sejw z 2. rozdziału padał
(`Jump to ffffffff`). Naprawione (`parameter_delta`, `parameter_pointer_faults`, testy), **potwierdzone w grze
A/B (Y3 pada ↔ Y5 = Y3 + sam `+52` działa); build #14** (`config00` md5 `71d9fcaf…`, `configst` `6cfe245d…`)
przechodzi Loading, nową grę i sejw z 2. rozdziału. Sejwy nie zależą od układu pliku (Y1, B). Budżet Skill00
216 768 B (Loading) bez zmian. Pakiet **v3** (`1ptwsZAtLb-6_0ydGfFOakXlWjBKIa3iB`): v2 + `label_fit` + 408 kopii
puli DLC po `translation_copy.py --resync` (0 błędów). **Następne:** pełny patch u użytkownika
(`HOKUS_POKUS.bat`, świeży ZIP gałęzi + v3) → sejw z 2. rozdziału na pełnym zestawie → gra od początku;
pozostałe 94 kontenery nigdy nie działały w grze poza Loading. Pułapki: `skill_shrink`/`label_fit` nie
aktualizują wierszy-kopii (`copy_of`) — po każdym z nich `translation_copy.py --resync` i `translation_check`
z finalnego pakietu; `check_report.txt` w zipie v2 był nieaktualny.

**Stan 2026-10-15 (najnowszy; `EXPERIMENT_LOG.md` §21.20): U2 PADA, U1 DZIAŁA, W5 DZIAŁA ⇒ limit rozmiaru
SAMEGO członu `srwDL_Skill00.bin`** (nie kontenera, nie nagłówka): bezpieczne 217 086 B, crash od 221 182 B.
Zrobione: (1) budżet w pisarzu `item_skill_write.SKILL00_LIMIT = 216 768` (`SizeBudgetError`; builder nie
zapisuje całego kontenera: „NOT written", exit 1 — test e2e na pakiecie 2026-10-14 potwierdza); (2)
`tools/skill_shrink.py` + `config/skill_shrink_rules.tsv` (141 reguł, pakiet → pakiet, ta sama funkcja na
wierszach `03` i `04`, straże tokenów/CP932, `SKROCENIA_Skill00.tsv` do przeglądu) ⇒ 228 202 → **216 518 B**;
(3) **build #11** z `local/pakiet_ciasny` (`config00.cpk` 936 064 B md5 `abacf828…`, nagłówek CPK bajt w bajt
jak W5; `configst.cpk` md5 `512e2397…`) — `WGRAJ_build11.zip` Drive DELIVERY `1-9wvXVMEVNKVHAaMFPgDA_9hLFjsSe_a`,
skrócony pakiet `pakiet_EN_2026-10-15_ciasny.zip` Drive Pakiet `1mNZ2wxKypbuKO1_RG_R2R6mk57Zj8CaC`.
**Czeka na jeden test w grze: KROK 1 (config00), KROK 2 (oba).** Opcjonalnie W3/W4 (W4 działa ⇒ budżet +3 KB).
Następne po teście: jeśli KROK 1 działa — pełna piątka (eventP00, mesbtl00, imenu00 + DLC) przez
`HOKUS_POKUS.bat` na skróconym pakiecie; jeśli pada — przyczyna poza rozmiarem Skill00 (wzrost 6 pozostałych
członów +311 B lub treść) → bisekcja członów z `container_mix.py`. Otwarte: `skill_shrink` nie jest jeszcze
krokiem `HOKUS_POKUS`/buildera (ręcznie przed buildem po każdej edycji pakietu); 23 wiersze identycznościowe
Skill00 (` Lv`→`Lv` itp.) builder słusznie pomija.

**Stan 2026-10-14 noc, runda 2 (`EXPERIMENT_LOG.md` §21.16):** build #10 (`config00`) **pada**; V1 (sam
`DLC_ID00`) działa; **V2 (sam `srwDL_Skill00.bin` z buildu #10) pada** → winny jest przebudowany Skill00, nie
wskaźnik +36 (poprawiony, nadal pada). Brak odwołań po nazwie umiejętności w innych plikach. W toku: V6/V3/V4
z PLANU B + runda 2 `RUNDA_2_Skill00.zip` (Drive `1DAxpAe4u3hn0kJ_ADpniJDdmnA03lqBV`, `tools/member_variants.py`:
S1 rozmiar / S2 rekordy EN+pula JP / S3 rekordy JP+pula EN / S4 nazwy / S5 opisy / S6–S7 połowy). Hipotezy:
rozmiar `.pac`/członu (V6, S1), stałe bufory nazw (JP max 14 B, EN do 26 B — S4), opisy (S5), pula (S3).
**2026-10-15: S1 (oryginał + zera do rozmiaru buildu) PADA** ⇒ treść EN niepotrzebna do crasha. Runda 3 =
drabinka rozmiaru T1–T6 (`--ladder`: tekst JP + spacje w `effect`, §21.17, Drive `1PtpZT4IfmE_TcV_2swTzFtlVhTwHrT3y`);
po wyniku: budżet wzrostu Skill00 (albo dowód, że zera były winne) → poprawka pisarza / skracanie EN.
**T6 PADA (2026-10-15) ⇒ ROZMIAR potwierdzony.** Runda 4 (§21.18, Drive `1EwulWduWbchzpKy-kUWBz9P6Bo-3sNLR`):
U2 = ciasny `.pac` (krok 64 B, pac 905 216 < oryginał) z Skill00 jak T6 — jeśli działa, to zarazem poprawka
(`configst_pack.rebuild_pac(align=64)` do włączenia w `build_translation_patch`); U1 = kontrola samego pakowania;
T7 = T6 + przeliczone `EnabledPackedSize/EnabledDataSize` (od teraz `cpk_write` liczy je zawsze). Potem drabinka
T1/T3/T4. `WGRAJ_DO_ISO.bat` pamięta ISO (`%APPDATA%\SRWOE`).
**Runda 3 pełna: T1, T3 (217 086 B) DZIAŁAJĄ; T4 (221 182 B), T5, T6 PADAJĄ** ⇒ budżet wzrostu Skill00 w
[+8 128, +12 224) B; 217 088 = 0x35000 podejrzany jako stały bufor. Runda 5 (§21.19, Drive
`10vzESMi8y2FFKNoMFwIPxpMfUikzgOqY`): W1 217 090 / W2 218 110 / W3 219 134 / W4 220 158 (stary nagłówek) +
W5 = T3 z przeliczonym nagłówkiem. Kolejność: U2 → U1 (→ V6) → W1 → W3 → W2/W4 → W5; T7 zbędny.

**Stan 2026-10-14 bardzo późna noc (najnowszy; `EXPERIMENT_LOG.md` §21.15):** build #9 w wariancie B **padł
identycznie** (`memcpy_jak`, NULL + `bytes>0`). Znaleziona pewna usterka pisarza: w rekordach conv-B
(Skill00/Item00/Item/Spirit/StatusChange) u32 pod **+36 = `tail_offset − offset_rekordu`** (wskaźnik puli
względem rekordu; 2230/2230 w oryginałach), a `item_skill_write` kopiował go bez zmian po przesunięciu
rekordów (1468/1469 złych w Skill00). Naprawione (`POOL_POINTER`, `pool_pointer_faults`, dowód na wyniku,
odmowa źródła łamiącego regułę). **Build #10** (`config00` md5 `37251325…`, `configst` md5 `ee1aae95…`) na
Drive DELIVERY `1GQUD_g9VuujLPzsrt-xsw0y3UDdm6uys` z `CZYTAJ.txt`: KROK 1 = wariant B z nowym `config00`,
KROK 2 = oba, PLAN B = warianty V1–V6 z `tools/container_mix.py` (bisekcja sub-plików `.pac`: `--take`/
`--keep`/`--pad-only`, raport `.mix.json`). Czy +36 było przyczyną crasha — **hipoteza do testu**. Pytanie
otwarte: czy wariant A (configst z tym samym błędem w Item/Spirit/StatusChange) przeszedł „Loading" do gry.
DLC `config01..08` błąd nie dotyczy (conv-C, 0 rekordów). Użytkownik nie wiedział, co zrobić z luźnymi
`.cpk` → `WGRAJ_DO_ISO.bat` + `tools/iso_insert.py` (okna: ISO → folder; wkłada pliki z folderu do KOPII
ISO, odmawia ISO już załatanego i plików spoza USRDIR, czyta wgrane człony z powrotem); dostawa
`WGRAJ_build10.zip` (Drive `1yjzP39z6qtWO457uZd4IoBG-w4zr2-Ak`, samowystarczalna: bat + 3 narzędzia +
`KROK_1_tylko_config00/`, `KROK_2_config00_i_configst/`, `PLAN_B/V1..V6/`).

**Stan 2026-10-15 późny wieczór (najnowszy; `EXPERIMENT_LOG.md` §21.26):** pełny patch użytkownika (pochodzenie
plików nieznane) pada na „Loading" stosem buildu #8. Dysk uporządkowany (stare zestawy w `_STARE_NIE_UZYWAC`,
nowa `INSTRUKCJA_PL.md`, `KIT_build15_2026-10-15.zip`). Nowy `DIAGNOZA.bat` + `tools/diagnoza.py` (tylko czyta:
narzędzia / pakiet / wynik budowy / folder DLC emulatora / ISO — md5 i rozpoznanie buildów; raport `DIAGNOZA.txt`).
`build_report.json` ma `"tools"` (`TOOLS_STAMP`). Nieuruchomione nigdy w grze z poprawionymi pisarzami:
`eventP00`/`mesbtl00`/`imenu00` (STORED, 1,6–2,9× większe pliki) i 91 EDAT. Następne: DIAGNOZA → test X (oryginalny
DLC + `patched.iso`) i Y (oryginalne ISO + pełny `DLC\`) → `WGRAJ_DO_ISO.bat` z `ISO_B/C/D` albo `BISEKCJA.bat` H/I.

**Stan 2026-10-14 późna noc (`EXPERIMENT_LOG.md` §21.13–21.14):** build #8 padł jak #6;
**bisekcja: A (`configst.cpk`) DZIAŁA — menu po angielsku; B (`config00.cpk`) PADA**; C/D/E nie testowane.
Audyt `config00` oryginał↔build: jedyny ubytek = 84 skrócone nazwy jednostek (kana, `unit_list00` +32)
wyzerowane przez `name_table_write` (komórka nazwy to 32 B, nie 64). Naprawione: SPECS `unit_list`
name 32/name_short 32/display 64, EN nazwa kopiowana do komórki +32 (`derived_short`), parzystość rekordów
pul (`rebuild_pool`), eksport `unit:<id>:name_short` + `mode: slot`/`max_bytes` dla komórek tablic nazw.
Build #9 = sam `config00.cpk` (md5 `d42e1493…`) do ponownego testu wariantu B; związek z crashem =
hipoteza do czasu testu. Potem C/D/E (eventP00, mesbtl00, imenu00) i dopiero pełna piątka.

**Stan 2026-10-14 noc (`EXPERIMENT_LOG.md` cz. 21):** build #6 **padł w grze** na „Loading"
(`Read Word at 00000000`, PC `088e6120`, po 45 otwarciach EDAT DLC — log PPSSPP bez nazw plików).
Znalezione i naprawione offline: (1) `sysmes.bin` budowany złym modelem (offsety są WZGLĘDNE wobec
`0x24fc`, wpis k = string k; #6 dał 145 KB śmieci w miejsce 1182 komunikatów systemowych — §3);
(2) spacja końcowa identyfikatora DLC `…ADDPACKAGE000002-J001␠` zjedzona przez wiersz-kopię tłumacza
(builder: `identity(row)` = nie pisz). Czy to był jedyny powód crasha — **NIEZNANE** do testu użytkownika.
Do bisekcji: `BISEKCJA.bat` (okno A–I, builder `--only/--skip/--filter`), wynik `srw-oe-bisekcja\<litera>\`.
Komunikat o autozapisie na starcie = `EBOOT.BIN` (poza pakietem). Dla tłumacza: 25 całych stringów sysmes
bez wiersza (`sysmes_text.py --merge-into --prune-fragments` przy następnym pakiecie).

**Stan 2026-10-14 wieczór (szczegóły `STATUS.md`, `EXPERIMENT_LOG.md` cz. 20):** `EN2.zip`
tłumacza wczytany bez odrzuceń (44 051 + 17 353 elementów), pakiet 80 780/108 123 wierszy z EN (puste =
tylko dialogi: rozdziały 1–3 w całości, 4 w 59 %, 5–8 puste), **budowa na wszystkich 96 kontenerach:
96/96, 0 problemów, 80 084 teksty odnalezione w wynikach, 63 braki (same znane)**, deterministyczna.
Pakiet do wgrania na Drive („SRW OE - PATCH 2026-10-14 (EN2)", `1mQaFQlVjn_Io93cVeY3jLKj3Cy0pvkPr`):
gotowe DLC, pakiet JSONL dla `HOKUS_POKUS.bat` (buduje `patched.iso` u użytkownika), instrukcja
`docs/INSTRUKCJA_PATCH_PL.md`. Pole tytułu `*_ext.dat` = 40 B (nie 44) — 10 tytułów skrócono prowizorycznie.
Otwarte: (a) **test w grze tej budowy** (nigdy nie zrobiony: linie 47–52, stored mesbtl00/config00/configst,
pula umiejętności, DLC_ID, pełny splice 5 kontenerów do ISO — w grze sprawdzony tylko sam eventP00);
(b) tłumacz: `DO_ZROBIENIA_2.md` (10 tytułów) + dalsze `epizod-NN.md`; (c) 6 achievementów (liczba rekordu
czytana jako odwołanie) i 2 przydomki; (d) ponowny eksport pakietu (limit 39 w widoku, sieroty, Reference,
`coverage_audit` ślepy na fragmenty z tokenem).

**Stan 2026-10-14 rano (szczegóły `EXPERIMENT_LOG.md` cz. 19):** pierwszy prawdziwy
import tłumaczeń (`EN.zip`: 61 322/61 468 elementów) i budowa na 13 kontenerach z Drive
(`config00/01/02–08`, `configst`, `eventP00`, `imenu00`, `mesbtl00`): 38 598/39 290 sprawdzalnych
tekstów wylądowało. Pula ogonowa `srwDL_Skill/Item/Spirit/StatusChange` ma własną tablicę wskaźników
u32 (`item_skill_records.parse_tail_pool`) — pisarz przebudowuje ją (`item_skill_write.rebuild_pool`),
a 126 fragmentów z tokenem kany doszło do pakietu dopiero teraz (`tools/pool_rows_refresh.py`).
Otwarte: (a) weryfikacja w grze zbudowanych kontenerów (brak ISO/emulatora w sandboxie), w tym szerokość
linii 47–52 i przebudowana pula umiejętności; (b) 126 nowych fragmentów + 41 odrzuconych elementów do
tłumacza (`DO_ZROBIENIA.md` przy kontenerach na Drive); (c) kontenery spoza Drive (config10–46, eventP01+,
mesbtl01+, imenu01+) — 40 322 wiersze z EN czekają na pliki; (d) ponowny eksport pakietu (śmieciowe
wiersze z liczb znikną, `coverage_audit` nadal nie widzi fragmentów rozciętych tokenem).

1. **Dekodowanie mówcy** w EVNT: rozpoznać komendę portretu/postawi, wyciągnąć ID pilota,
   zmapować na `srwDL_CharaDictionary`, dopisać `speaker` do `extract_scenes`. (Monologi pomijamy.)
   **Postęp (2026-10-11, HIPOTEZA):** `tools/speaker_probe.py` (read-only, tylko liczby) pokazuje, że
   u16 na offsecie `+10` rekordu `0xc9` zmienia się per linia jak stan mówcy (w rozmowie naprzemienne
   pary kluczy, np. `0x1195`/`0x119e`; 620 linii w 11 członkach eventP00). NIE zweryfikowane jako
   indeks słownika. Następny krok: mapowanie na `srwDL_CharaDictionary` + sprawdzenie zmian mówcy
   względem komend `0x160`/`0x1b8`/`0x145`. Dopiero po tym `speaker` idzie do tłumaczeń.
   **Wynik (2026-10-11, KOREKTA poprzedniego wpisu):** klucz mówcy to u16 na offsecie **+0x40** rekordu
   `srwDL_CharaDictionary` (nie sloty ID +0x30). Siedmiu nazwanych bohaterów (katakana w słowniku) ma dokładnie
   ten klucz, który transkrypcja linia-po-linii przypisuje tej samej postaci (Seishiro 0x1195, Himari 0x119e,
   Bright 0x3fb, Mirai 0x3fe, Paolo 0x415, Sayla 0x401, Marker 0x41c). **56/60 kluczy** ma rekord w słowniku
   (**574/608 linii, 94%**); 55 jednoznacznie, **0xe93** w dwóch rekordach (86, 87) — niejednoznaczne.
   Nie znaleziono 4 kluczy (0x4b1, 0x4b6, 0xec0, 0xec1 — 34 linie). `tools/speaker_map.py` (liczby;
   tekst rekordów tylko do `local/`). **Nie zrobione:** pełne sprawdzenie transkrypcją innych mówców oraz
   weryfikacja w grze.
   **Imiona mówców (2026-10-11):** `tools/speaker_names.py resolve` łączy dwa źródła: (A) imię pełne =
   string[0] rekordu słownika powiązanego kluczem (`speaker_map`); (B) sloty imion w `config*.pac`
   (u32 klucza na +0x14 slotu 16 B, CP932). Pierwszeństwo ma słownik. Wynik: rozdział 1 — **60/60**
   kluczy; rozdział 2 — **158/167**. Pozostałe 9 kluczy (postacie generyczne i 3 bez źródła) jest
   OTWARTE — lista kluczy w `EXPERIMENT_LOG.md`. Imiona zostają w `local/` (nie w git).
   **Mapa całej gry (2026-10-11):** configi 00–46, imenu 00–32, eventy P00–P09/P13/P20–P32 zbadane.
   283 klucze; 244 z ≥3 liniami: 216 ma imię ze słownika, 11 tylko z configu, 17 bez źródła.
   39 z 43 kluczy rozdziału 1 wraca w późniejszych eventach. Żaden rekord słownika postaci z rozdziału 1
   nie leży poza imenu00. Każdy DLC event wnosi własną pulę słownika (HIPOTEZA). Dwa klucze mają 2 rekordy
   (0xe93, 0x101a) — wymaga reguły. Szczegóły w `EXPERIMENT_LOG.md`, pełna lista w `local/` (nie w git).
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
python tools\sysmes_pack.py <in.cpk> <out.cpk>          # DEFAULT_EDITS tytułu, dowolna długość, zrzut wpisów 906-911
```

## 9. Znane pułapki (nie powtarzaj)
- `unit_list<NN>.bin` (384 B/rekord): `name` @+0 to komórka **32 B**, @+32 leży półszeroka kana
  (skrócona nazwa, w 100 % rekordów), `name_display` @+140 (64 B). Pisarz z komórką „64" zerował kanę
  w 84/84 rekordach config00 (build #6–#8). Nigdy nie zostawiaj komórki tablicy nazw pustej; „najdłuższa
  nazwa 46 B" pochodziła z nieograniczonego `cstring` czytającego w kanę (3 nazwy DLC bez NUL w 32 B).
- Pule wskaźnikowe (CharaDictionary/RoboDictionary/Shop/DLC_ID/Reference/Skill_Tag/Achievement): każdy
  oryginalny rekord ma PARZYSTY offset i długość (1 051/1 051); `rebuild_pool` dopełnia edytowane rekordy
  1 bajtem zera. Nie usuwaj tego dopełnienia.
- `sysmes.bin`: offsety tablicy są **względne wobec `0x10 + count·8 − 4`**, nie bezwzględne; wpis k =
  k-ty string. Stary `apply_edits`/`sysmes_shift._grow` (model bezwzględny, pula od 0x2500) psuł wszystko —
  build #6 (145 KB śmieci). Wniosek „menu tytułowe = stałe offsety zewnętrzne" był artefaktem tego modelu
  (odwołany 2026-10-14, §3). Używaj tylko `sysmes_pack.translate_bytes` + `verify`.
- Wiersze pakietu z EN == JP (identyfikatory PSN, ` N`) nie są tłumaczeniem — builder je pomija
  (`identity`); kopia bez spacji końcowej zmieniała bajt porównywany przez grę.
- `compress_literal` (rozszerzanie) CRASHOWAŁO w grze — używaj tylko shrink/identity w crilayla.
- Nie nazywaj projektu przetłumaczonym; nie commituj binariów gry.
- Pula ogonowa Skill/Item/Spirit/StatusChange: słowa w ogonie rekordu to PARAMETRY, nie odwołania;
  adresowanie = własna tablica u32 na `tail_offset`. Naiwne cięcie po NUL dawało śmieciowe wiersze
  (bajty wskaźników jako tekst) i gubiło teksty z tokenem kany; wpis in-place `slot` i stary
  `rebuild_member` (stare wskaźniki po wzroście rekordów) były błędne — nie wracaj do nich.
- `coverage_audit.py` jest ślepy na fragmenty rozcięte bajtem sterującym (akceptuje podciągi) —
  „0 brakujących” dla pul config było fałszywe.
- Szerokość 46 była z pierwszej sceny; limity pisarzy = spis najszerszych linii gry per rodzaj.
- cmd.exe: `%X:~…%`/`%X:a=b%` dla NIEZDEFINIOWANEGO X usuwa tylko `%X:` i skanuje dalej → linia zamienia
  się w śmieci; w `if` to fatalny błąd składni („The syntax of the command is incorrect"), nawet gdy
  warunek `if defined X` jest fałszywy. Guard = `if not defined X goto :dalej` w osobnej linii. Bez `%` w `rem`.
  (HOKUS_POKUS `:pick`, 2026-10-14, Windows 10 1709.)
- `.bat` z `set /p` na ścieżkę = błąd zgłaszany przez użytkownika (dwukrotnie). Zawsze okno wyboru
  (`tools/pick_path.py`, `call :pick`). W argumentach dla Pythona folder bez końcowego `\` przed
  cudzysłowem (`"D:\x\"` → `\"` zjada cudzysłów).
- `*_ext.dat`: za tytułem (+344) leżą dwa u16 gry (+384, +386), zera tylko w eventP00 — heurystyka
  „zerowe wypełnienie" ich nie odróżnia; sloty stałe mają zmierzone rozmiary (`mission_text.SPECS`) i twardy
  limit, nie szukaj padding-u za slotem.
- `patch_spot_check.py --report` to ścieżka WYJŚCIA raportu spot checku — podanie `build_report.json`
  buildera nadpisuje go (stało się przy #5). Zawsze osobny plik.
- Sandbox może zostać zresetowany bez ostrzeżenia (`local/`, `google_drive/` i niewypchnięte commity
  znikają) — commit+push wcześnie, wyniki z `local/` od razu na Drive.
- Każde nowe wiersze puli (`pool_rows_refresh`) muszą od razu dostać wpis w `tokeny.tsv`, inaczej
  pisarz odmawia po cichu przy budowie (126 tekstów w #4).
