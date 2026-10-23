# SRW OE PL v4.0 — Session Handoff State (2026-10-23)

## Committed & Pushed Checkpoints on `arena/df413232-mtgcrawler` (PR #22)

All file edits completed prior to session close are already committed and pushed:

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
   - Current pushed snapshot state: `entries: 108794`, `rows: 109176`, `filled: 108805`, `empty: 371`, `errors: 0`, `data_sha256: d1f9170d99aac8745b3923cdca7914512504b0cf4a5a4c2cab019a073950d912`.
   - All `1,385` owner-reviewed bindings (`mensys_15.json`, `02_items.jsonl`, `03_skills.jsonl`, `04_config_text.jsonl`, `08_names_units_weapons.jsonl`, `09_executable.jsonl`) remain untouched.

---

## Completed Review Notes Queued for Checkpoint 7 (Not Yet Applied to `polish.jsonl`)

Zero-elision line-by-line review is already complete for **`eventP09.EDAT`**, **`eventP13.EDAT`**, and **`eventP08.EDAT` up through `dlg:eventP08.EDAT/DL834_12.bin:15276`**. Apply these queued items in Checkpoint 7 along with the final half of `DL834`:

1. **Chapter 7 residual spot-checks (verify & apply if still unpatched in `00_dialogue.jsonl`):**
   - `dlg:eventP07.EDAT/DL726_11.bin:7460`: `[レイヴン] 君がかい？` -> `"Mówisz o sobie?"`
   - `dlg:eventP07.EDAT/DL726_12.bin:11132`: neutralize `'panowie z Connect Force!'` -> `"Do zobaczenia, Connect Force!"`
   - `dlg:eventP07.EDAT/DL728_12.bin:11256` & `dlg:eventP07.EDAT/DL728_13.bin:28692`: `'jako była Trzynastka'` -> `'jako była członkini Trzynastki'` / `'jako dawna członkini Trzynastki'`
2. **`dlg:eventP08.EDAT/DL830_11.bin:16984`:** `[ヒルツ] 終焉の宴にようこそ、コネクト・フォースの諸君。` -> `'Witajcie na uczcie końca, wojownicy Connect Force.'` (replaces masculine-only `'panowie z Connect Force'`).
3. **`dlg:eventP08.EDAT/DL830_13.bin:38044,38464` & `dlg:eventP08.EDAT/DL834_11.bin:6432`:** Standardize team inflection/spelling (`Saurersów` -> `Saurerów`; `Zaurersi` -> `Saurersi`, matching `Saurersi / Saurerów`).
4. **`dlg:eventP08.EDAT/DL830_13.bin:61756`:** `[フィーネ] ええ…バンは勝ったわ！` after `nic się pani nie stało?!` -> `"Nic mi nie jest... Van wygrał!"` (replaces ambiguous `"Nie... Van wygrał!"`).
5. **`Mucus Gate` vs `Brama Mucus` in Chapter 8 (`DL831_11`, `DL832_12`, `DL833_11:1448`, `DL833_60:2180`):** Harmonize untranslated feminine `Mucus Gate` back to `Brama Mucus / Bramy Mucus / Bramę Mucus` matching `DL830_13..50` and Chapters 1–7.
6. **`dlg:eventP08.EDAT/DL831_12.bin:9360`:** Fix masculine `'zostań wreszcie jednym z naaami'` addressed to female Himari (`一緒になろうよぉ`) -> `"Himariii, nie musisz już cierpieć.\nNo chodź, połącz się wreszcie z naaami."`.
7. **`dlg:eventP08.EDAT/DL831_12.bin:29396`:** Fix gender drift `'Przeklęte Connect Force!'` -> `"Przeklęty Connect Force!"`.
8. **`dlg:eventP08.EDAT/DL832_11.bin:1488`:** Audit all `[ボビー・マルゴ]` lines across `00_dialogue.jsonl` to keep Bobby Margot's grammatical gender consistent across the entire script.
9. **`dlg:eventP08.EDAT/DL832_30.bin:4304`:** Fix orthography `'z przed chwili'` -> `"Ten Sarge Aupus sprzed chwili\nzgłosił, że bezpiecznie się wycofał!\n"`.
10. **`dlg:eventP08.EDAT/DL833_11.bin:12956,13872`:** Fix feminine gender drift on `Macross Quarter` (`weszła do walki` -> `wszedł do walki`, `ma pokonać wroga sama?` -> `ma pokonać wroga sam?`).
11. **`dlg:eventP08.EDAT/DL834_11.bin:1920`:** Fix ungrammatical `'się odrośnie'` -> `"Connect Force musi wedrzeć się do środka,\nzanim błona na wejściu odrośnie."`.

---

## Remaining Work to Finish `PL v4.0` in Next Session

1. **Finish reading the remaining tail of the game (zero elision):**
   - `eventP08.EDAT` starting immediately **after `dlg:eventP08.EDAT/DL834_12.bin:15276`** through the end of Episode 34 (`~1,787` unique lines).
   - Remaining non-`copy_of` DLC dialogue rows in `evept101.EDAT`–`evept108.EDAT` (`~455` lines).
   - All non-`copy_of` rows in `05_mission_text.jsonl`, plus global checks on `[ボビー・マルゴ]`, `Genesis` gender, and `『...』` mission target names.
2. **Commit & push Checkpoint 7:** Apply all Chapter 8 + DLC + `05_mission_text.jsonl` edits with transitive `copy_of` propagation and full `pl_release_package.validate` verification (`errors: 0`).
3. **Deliver `PL v4.0` (Checkpoint 8):**
   - Refresh `docs/pilot-catalog/srwoe_pilot_catalog_PL.md` and `docs/srwoe_mission_deployments.md` (`<= 216` pipe-table width).
   - Add `tests/test_pl_v4_0_consistency.py` and pass full `unittest` suite.
   - Regenerate `srwoe_episode_00_PL.md`..`34_PL.md`, `srwoe_reading_PL_00-34.zip`, and `srw-oe-translation-pl-v4.0.zip` (`--version 4.0`).
   - Upload `srw-oe-translation-pl-v4.0.zip` to Google Drive root (`1oZ6xnvpV64ZcJhfrob8tVNs_SoPF3H1w`), update `srwoe_reading_PL_00-34.zip` (`1d7JOPlRqH6Pd5ibCiMB1y2H-j59mFLw1`) in `Skrypty` (`1zBVlAv_Nu-2hynN86f-vml7Yy823q22H`), verify byte parity (`cmp -s == 0`), and trash superseded `srw-oe-translation-pl-v3.5.zip` (`1Umr2dARMw6TP7k0FNddbpZmYLja6wZAp`).
   - Remove temporary working files (`PL_V4_0_HANDOFF.md` once superseded by `EXPERIMENT_LOG.md`), update `README.md` + `docs/EXPERIMENT_LOG.md`, commit, and push.
