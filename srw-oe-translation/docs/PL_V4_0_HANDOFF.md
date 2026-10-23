# SRW OE PL v4.0 — Session Handoff State (2026-10-23)

## Status: editorial work COMPLETE — release packaging intentionally on hold

All review and fix work for **`PL v4.0`** is finished and pushed on
`arena/df413232-mtgcrawler` (PR #22). Per the owner's instruction of 2026-10-23 the
**full release archive (`srw-oe-translation-pl-v4.0.zip`) is deliberately not built yet**;
only the fix scope was to be closed 100% first.

## Committed & Pushed Checkpoints on `arena/df413232-mtgcrawler` (PR #22)

1. **`27d3561` — Checkpoint 1 (`Groups A + B + C` + `CharaDictionary` + `Kallen` + DLC sync):**
   - `srw-oe-translation/pakiet_EN/07_names_characters.jsonl`: promoted `char:2320:{nickname,name_short,name_narrow}` (`en: "Kallen"`).
   - `srw-oe-translation/pakiet_PL/polish.jsonl`: `103` updates (`57` `00_dialogue.jsonl`, `21` `01_battle_quotes.jsonl`, `25` `07_names_characters.jsonl`).
   - Kept `"Matchless"` and `(Ally)` / `/Ally` unchanged per owner direction.
2. **`ea10165` — Checkpoint 2 (Chapter 3 `Ep 10–13` + sub-missions complete):**
   - `14` `00_dialogue.jsonl` updates across `eventP03.EDAT`, `eventP23–25.EDAT`, `evept*`, and global `"Hymen"` / `"Mamy ich?!"` audit.
3. **`b21c994` — Checkpoint 5 (Chapters 4–6 `Ep 14–25` + `eventP26–32` complete):**
   - `43` updates (`40` `00_dialogue.jsonl` + `3` `01_battle_quotes.jsonl`) plus global `Kozuki`, `Show Zamo`/`Show Zamą`, `Zerowi`/`Zeru`, and `\bbacza\b` scans.
4. **`d55660d` — Checkpoint 6 (Chapter 7 `Ep 26–29.5` complete):**
   - `23` `00_dialogue.jsonl` updates (`Gastogalu`, `Zera`/`Zeru`, masculine `Connect Force` & `Vasage`, short replies, context fixes).
5. **`9713861` — CI provenance fix for the `char:2320` promotion:**
   - Added `config/pl/char-2320-kallen-2026-10-23.json` (audited `old_line` / `new_line` / SHA-256 for the `5` promoted rows) and taught
     `tools/polish_reading_script.py::validate_source_bindings` plus `tests/test_reading_script_episode34.py` to reverse exactly those
     `5` lines and require byte-identical reconstruction of the frozen baseline. Any unreviewed edit still fails closed.
6. **`ee1cc45` — Checkpoint 7 (Chapter 8 `Ep 30–34`, finale, epilogues, DLC `evept101–108`, `05_mission_text.jsonl`, global consistency):**
   - `125` snapshot rows changed (`123` `00_dialogue.jsonl` + `2` … **see `docs/EXPERIMENT_LOG.md`** for the authoritative per-class list).
   - Follow-up commit harmonizing `17` mixed-capitalisation `Brama/Bramy Mucus` rows to `Mucus Gate` (prose in lowercase declension left intact).
   - Current pushed snapshot state: `entries: 108794`, `rows: 109176`, `filled: 108805`, `empty: 371`, `errors: 0`,
     `data_sha256: 8cb37fb30f8c1551083a2e1c050abb645ed561c706a1515cbc8152cc32a6269c`.
   - All `1,385` owner-reviewed bindings (`mensys_15.json`, `02_items.jsonl`, `03_skills.jsonl`, `04_config_text.jsonl`,
     `08_names_units_weapons.jsonl`, `09_executable.jsonl`) remain untouched.

---

## Previously Queued Checkpoint 7 Items — ALL APPLIED

| # | Item | Applied value |
| - | ---- | ------------- |
| 1 | `DL726_11.bin:7460` | `"Mówisz o sobie?"` |
| 2 | `DL726_12.bin:11132` | `"Hahahaha!\nDo zobaczenia, Connect Force!"` |
| 3 | `DL728_12.bin:11256` / `DL728_13.bin:28692` | `"Rozstrzygnijmy to między byłymi z Trzynastki!"` / `"Jako była z Trzynastki wyrównam z nim rachunki!"` |
| 4 | `DL830_11.bin:16984` | `"Witajcie na uczcie końca, Connect Force."` |
| 5 | `DL830_13.bin:38044,38464` / `DL834_11.bin:6432` | `"Saurersów"` / `"Saurersi zawsze są Nekketsu Saikyo!"` |
| 6 | `DL830_13.bin:61756` | `"Tak... Van wygrał!"` |
| 7 | `Mucus Gate` Chapter 8 | Unified indeclinable `Mucus Gate` across the whole corpus (dropped `Brama Mucus`) |
| 8 | `DL831_12.bin:9360` | `"…zostań wreszcie jedną z naaas."` |
| 9 | `DL831_12.bin:29396` | `"Przeklęty Connect Force!"` |
| 10 | `DL832_11.bin:1488` + all Bobby Margot lines | Audited: feminine agreement consistent; no change needed |
| 11 | `DL832_30.bin:4304` | `"Ten Sarge Aupus sprzed chwili\nzgłosił, że bezpiecznie się wycofał!\n"` |
| 12 | `DL833_11.bin:12956,13872` | `"…wszedł do walki z flotą wroga!"` / `"…ma pokonać wroga sam?"` |
| 13 | `DL834_11.bin:1920` | `"…zanim błona na wejściu odrośnie."` |

## Remaining Work (release packaging only — no editorial work left)

1. **Refresh deliverable docs and catalogues** (`docs/pilot-catalog/srwoe_pilot_catalog_PL.md`,
   `docs/srwoe_mission_deployments.md` — already re-synced with the new names on 2026-10-23; keep `<= 216` pipe width and no `[ID ...]`).
2. **Pass the full `unittest` suite** (now including `tests/test_pl_v4_0_consistency.py`).
3. **Build `PL v4.0`:** regenerate `srwoe_episode_00_PL.md`..`34_PL.md`, `srwoe_reading_PL_00-34.zip`, and
   `srw-oe-translation-pl-v4.0.zip` (`python3 tools/build_release_pair.py --version 4.0`).
4. **Deliver to Google Drive:** upload `srw-oe-translation-pl-v4.0.zip` to root `1oZ6xnvpV64ZcJhfrob8tVNs_SoPF3H1w`,
   replace `srwoe_reading_PL_00-34.zip` (`1d7JOPlRqH6Pd5ibCiMB1y2H-j59mFLw1`) in `Skrypty` `1zBVlAv_Nu-2hynN86f-vml7Yy823q22H`,
   verify byte parity (`cmp -s == 0`), and trash the superseded `srw-oe-translation-pl-v3.5.zip` (`1Umr2dARMw6TP7k0FNddbpZmYLja6wZAp`).
5. **Close out:** delete this handoff file once `docs/EXPERIMENT_LOG.md` is the authoritative record, update `README.md`, commit, push.

> Evidence note: everything above is verified by repository diffs, snapshot hashes and CI runs. No gameplay-level PPSSPP
> runtime QA was performed in this environment.
