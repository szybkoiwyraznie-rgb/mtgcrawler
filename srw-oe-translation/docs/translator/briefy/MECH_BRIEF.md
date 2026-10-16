# Brief: translate mecha & weapon names (mechy.md) for the SRW OE English translation

Read `/home/claude/work/STYLE.md` first (binding rules + tooling).
Your worksheet: `/home/claude/work/ws/mechy_<GROUP>.txt` (already extracted; groups `#G n` = one unit, with `# title | seria` line).
Fields: [Nazwa] unit name, [Nazwa na ekranie] on-screen name (may include variant suffix like ／合体攻撃用 = "/Combination Attack"),
[Seria] series title (use the glossary series title exactly), [Długość] `全長 25.0m` → `Length 25.0m`, [Masa] `重量 54.0t` → `Weight 54.0t`,
[Broń N — nazwa] weapon/attack name, [Broń N — skrót] short weapon name (narrow list — keep it short, ≤ the shown ~N, abbreviate sensibly, ASCII only).
Some fields are repeated elsewhere and inherit automatically — only what's in your worksheet needs English.

Rules for names:
- Official English names first: English SRW releases (V, X, T, 30 — attack names there are authoritative, e.g. "Rocket Punch", "Breast Fire",
  "Shining Finger", "Getter Beam", "Giga Drill Break"), then official anime English (subs/dubs, Bandai model kits), then established fan usage
  (Akurasu SRW wiki, series wikis). Use WebSearch/WebFetch to verify when unsure. Do not invent when a source exists.
- Model numbers keep their form: RX-78-2 Gundam, MS-06S Zaku II (Char Custom) — follow how the Japanese name is structured; keep codes as ASCII (ＲＸ－７８ → RX-78).
- Common weapon vocabulary: ビーム・ライフル Beam Rifle, ビーム・サーベル Beam Saber, バルカン Vulcan, ミサイル Missiles, 機関砲 Machine Cannon,
  対空機関砲 AA Machine Gun, 未武装 Unarmed, 体当たり Ram, 格闘 Melee / Strike, 連続攻撃 Combo; 合体攻撃 Combination Attack.
- Japanese attack shouts that are canonically kept in Japanese-flavoured romanization in English SRW (e.g. "Shin Shoken"/"Shinken" etc.) — follow the English SRW form.
- Units/weapons from the OE original series: check `/home/claude/work/glossary.json` terms (Exart, Raiko Blade, Waver Gun…).
- Append each confirmed unit name and signature attack name to `/home/claude/work/glossary_extra.tsv` (`JP<TAB>EN<TAB>source/confidence (mechy)`), skipping JP already present.

Write your translation file `/home/claude/work/tr/mechy_<GROUP>.txt` and validate:
`python3 /home/claude/tool/tr.py merge /home/claude/src/w/mechy.md /home/claude/work/val/mechy_<GROUP>.md /home/claude/work/tr/mechy_<GROUP>.txt`
(errors about elements of OTHER groups not being filled don't matter — only your groups). 0 "BŁĄD" lines required; minimize "UWAGA".
Finish with a SHORT reply (≤10 lines): counts, low-confidence names.
