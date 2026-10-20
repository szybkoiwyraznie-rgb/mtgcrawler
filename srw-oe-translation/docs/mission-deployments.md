# Predefined Mission Deployments: Mechs and Combat Units

A source-grounded catalogue of scenario-defined machine/combat deployments for both sides. It excludes player-selected roster slots. It preserves uncertain scripted entries separately rather than assigning them an unsupported allegiance.

## Scope and reading guide

- **Source coverage:** 24 eventP packages with `_Entry.dat` files (eventP00.cpk, eventP01.EDAT, eventP02.EDAT, eventP03.EDAT, eventP04.EDAT, eventP05.EDAT, eventP06.EDAT, eventP07.EDAT, eventP08.EDAT, eventP09.EDAT, eventP13.EDAT, eventP20.EDAT, eventP21.EDAT, eventP22.EDAT, eventP23.EDAT, eventP24.EDAT, eventP25.EDAT, eventP26.EDAT, eventP27.EDAT, eventP28.EDAT, eventP29.EDAT, eventP30.EDAT, eventP31.EDAT, eventP32.EDAT); 226 package-file instances representing 224 distinct mission codes. The separately inspected `evept101.EDAT`–`evept108.EDAT` packages contain no `_Entry.dat` members.
- **Entry-data coverage:** 8,915 records from 226 `_Entry.dat` files; every file is a whole number of 64-byte records. 8,504 rows have both a nonzero entry ID and unit ID. All nonzero unit IDs and nonzero pilot/character IDs resolve to canonical names in the checked-in English dictionaries.
- **Excluded roster/placeholders:** 205 records have entry ID 0 and 368 have unit ID 0 (these counts overlap). They are not listed as fixed deployments. This is a structural exclusion based on the entry-data pattern; the complete runtime schema is not decoded.
- **Repeated states:** repeated rows with the same entry ID and the same unit/pilot are collapsed. If one entry ID points to different unit/pilot rows, the alternatives are retained and explicitly not counted as simultaneous units. The data does not establish turn-by-turn waves or when alternate records become active.
- **Mission labels:** headings use the exact `DL…`/`SM…` source code and the matching `_ext.dat` mission title when present. For `DL` codes, the two digits after the package digit identify the episode; the numeric source code is retained so the file can be found unambiguously.
- **Side labels:** “Allied” and “Enemy” are evidence-led inferences from the repeated entry-ID groups (`10xxx`/`11xxx`/`20xxx` and `12xxx`) cross-checked against recurring team-flag families. Since the full `_Entry.dat` schema is not decoded, unusual records remain in **Scripted units — side not established**; `13xxx`/`15xxx` are not assigned by prefix alone, and any entry ID whose observed flags disagree is held unresolved.
- **Pilot versus crew:** the mission record supplies at most one character key; that is shown as the mission-assigned character. Where the global `unit_list` has multiple default character/crew references, they are listed separately and explicitly marked **not mission-confirmed**. They must not be read as proof that every referenced character sorties in that mission.
- **Conditions and waves:** translated mission-note conditions are quoted below when present (for example fixed sorties, unit restrictions, allied NPCs, carrier changes, or special movement). The remaining timing/wave fields are not decoded; no wave timing is inferred.
- **Non-mech records:** `Container` and `Repair Unit` entries are map objects/utilities and are excluded from the combat roster; their source-record counts are summarized at the end. Mines, gates, turrets, missiles, and other scripted combat targets are retained and tagged when recognizable.
- **Verification limits:** the original `config00.cpk`, `config01`–`config19.EDAT`, and `configst.cpk` downloaded for this audit match all 21 hashes in `docs/mech-catalog/source-inventory.json` (including `config00.cpk`, 929,920 bytes, MD5 `266366c3bee66130d4b7cb57a1b1e3d4`). Event packages are listed by name above; their package hashes are not pinned by that inventory. This is a static data audit; no physical ISO or in-game runtime test was performed.

**Record classification totals (after excluding Container/Repair Unit rows, before collapsing repeated states):** 881 allied-inferred, 7,198 enemy-inferred, 206 side-unresolved. These are source-record counts, not simultaneous unit counts.

## Catalogue

### Episode 0 — Basic Training (`DL100_01`)

**Source:** `eventP00.cpk/DL100_01_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage

**Enemy deployments (inferred):**
  - **Brocken/Melee** — mission Entry character/pilot field: Control AI — ×3 source Entry IDs (simultaneous count not verified)

### Episode 0 — Rescue White Base (`DL100_02`)

**Source:** `eventP00.cpk/DL100_02_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Gundam** — mission Entry character/pilot field: Amuro Ray
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Zaku II (Char)** — mission Entry character/pilot field: Char Aznable
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Crown
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Slender

### Episode 1 — Ep. 1 Rogue Prototype Labor Incident (`DL101_11`)

**Source:** `eventP00.cpk/DL101_11_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Ingram Unit 1** — mission Entry character/pilot field: Noa Izumi
  - **Ingram Unit 2** — mission Entry character/pilot field: Isao Ota

**Enemy deployments (inferred):**
  - **HAL-X10** — mission Entry character/pilot field: Shinohara HOS
  - **HAL-X10/Green** — mission Entry character/pilot field: Shinohara HOS — ×3 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Helldiver** — mission Entry character/pilot field: JSDF Soldier — ×3 source Entry IDs (simultaneous count not verified)
  - **Medea** — mission Entry character/pilot field: JSDF Soldier

### Episode 1 — The Black Tri-Stars (`DL101_20`)

**Source:** `eventP00.cpk/DL101_20_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.
**Alternate-record caution:** 5 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **G-Fighter** — mission Entry character/pilot field: Sayla Mass
  - **Guncannon** — mission Entry character/pilot field: Kai Shiden
  - **Gundam** — mission Entry character/pilot field: Amuro Ray
  - **Guntank** — mission Entry character/pilot field: Hayato Kobayashi
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Dom (Black Tri-Stars)** — mission Entry character/pilot field: Gaia
  - **Dom (Black Tri-Stars)** — mission Entry character/pilot field: Mash
  - **Dom (Black Tri-Stars)** — mission Entry character/pilot field: Ortega
  - **Dopp** — mission Entry character/pilot field: Zeon Soldier — ×3 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **General-Purpose Turret** — mission Entry character/pilot field: Zeon Soldier — ×5 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present — scripted target/object; not a piloted mech
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Zeon Soldier
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)

### Episode 1 — Stop the H-Bomb Missile (`DL101_30`)

**Source:** `eventP00.cpk/DL101_30_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.
**Alternate-record caution:** 4 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **G-Fighter** — mission Entry character/pilot field: Sayla Mass
  - **Guncannon** — mission Entry character/pilot field: Kai Shiden
  - **Gundam** — mission Entry character/pilot field: Amuro Ray
  - **Guntank** — mission Entry character/pilot field: Hayato Kobayashi
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Dom** — mission Entry character/pilot field: Zeon Soldier — ×3 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Dopp** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **H-Bomb Missile** — mission Entry character/pilot field: No mission-assigned pilot key — scripted target/object; not a piloted mech
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Zeon Soldier
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)

### Episode 1 — Defense Class Training (`DL101_40`)

**Source:** `eventP00.cpk/DL101_40_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Raijin-Oh** — mission Entry character/pilot field: Jin Hyuga — unit-list default character/crew refs (not mission-confirmed): Jin Hyuga, Asuka Tsukishiro, Koji Hoshiyama

**Enemy deployments (inferred):**
  - **Brocken/Melee** — mission Entry character/pilot field: Control AI — ×4 source Entry IDs (simultaneous count not verified)

### Episode 1 — Launch the Alex (`DL101_50`)

**Source:** `eventP00.cpk/DL101_50_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.
**Alternate-record caution:** 2 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Gundam Ez8** — mission Entry character/pilot field: Shiro Amada
  - **Gundam Ground Type** — mission Entry character/pilot field: Karen Joshua
  - **Gundam Ground Type** — mission Entry character/pilot field: Terry Sanders Jr.
  - **Gundam Ground Type/GM Head** — mission Entry character/pilot field: Karen Joshua
  - **Hover Truck** — mission Entry character/pilot field: Michel Ninorich — unit-list default character/crew refs (not mission-confirmed): Michel Ninorich, Eledore Massis

**Enemy deployments (inferred):**
  - **Kampfer/Bazooka** — mission Entry character/pilot field: Andy Strauss
  - **Kampfer/High Mobility** — mission Entry character/pilot field: Mikhail Kaminsky
  - **Zaku II Kai** — mission Entry character/pilot field: Gabriel Ramirez Garcia
  - **Zaku II Kai** — mission Entry character/pilot field: Hardy Steiner

**Scripted units — side not established:**
  - **General-Purpose Turret** — mission Entry character/pilot field: Narration — scripted target/object; not a piloted mech

### Episode 1 — Rescue the Medea Transport (`DL101_60`)

**Source:** `eventP00.cpk/DL101_60_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned. Medea appears as an allied NPC.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Gundam Ez8** — mission Entry character/pilot field: Shiro Amada
  - **Gundam Ground Type** — mission Entry character/pilot field: Terry Sanders Jr.
  - **Gundam Ground Type/GM Head** — mission Entry character/pilot field: Karen Joshua
  - **Hover Truck** — mission Entry character/pilot field: Michel Ninorich — unit-list default character/crew refs (not mission-confirmed): Michel Ninorich, Eledore Massis

**Enemy deployments (inferred):**
  - **Dopp** — mission Entry character/pilot field: Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Zeon Soldier — ×3 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Zeon Soldier — ×3 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Medea** — mission Entry character/pilot field: Federation Officer
  - **Mucus Gate S** — mission Entry character/pilot field: No mission-assigned pilot key — scripted target/object; not a piloted mech

### Episode 1 — The Rogue Labor Returns (`DL101_70`)

**Source:** `eventP00.cpk/DL101_70_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Ingram Unit 1** — mission Entry character/pilot field: Noa Izumi
  - **Ingram Unit 2** — mission Entry character/pilot field: Isao Ota
  - **Raijin-Oh** — mission Entry character/pilot field: Jin Hyuga — unit-list default character/crew refs (not mission-confirmed): Jin Hyuga, Asuka Tsukishiro, Koji Hoshiyama

**Enemy deployments (inferred):**
  - **Brocken/Melee** — mission Entry character/pilot field: Control AI — ×5 source Entry IDs (simultaneous count not verified)

### Episode 1 — Undercover Investigation (`DL101_80`)

**Source:** `eventP00.cpk/DL101_80_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Ingram Unit 1** — mission Entry character/pilot field: Noa Izumi
  - **Ingram Unit 2** — mission Entry character/pilot field: Isao Ota

**Enemy deployments (inferred):**
  - **HAL-X10/Green** — mission Entry character/pilot field: Shinohara HOS — ×2 source Entry IDs (simultaneous count not verified)
  - **Helldiver** — mission Entry character/pilot field: Control AI — ×2 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **HAL-X10/Green** — mission Entry character/pilot field: Shinohara HOS — ×2 source Entry IDs (simultaneous count not verified)
  - **Helldiver** — mission Entry character/pilot field: Control AI — ×2 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech

### Episode 2 — Ep. 2 The Threat Lurking Underground (`DL102_11`)

**Source:** `eventP00.cpk/DL102_11_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Go-Saurer** — mission Entry character/pilot field: Kenichi Minezaki — unit-list default character/crew refs (not mission-confirmed): Kenichi Minezaki, Hiromi Tachibana, Shinobu Asaoka, Taro Shirogane, Yoji Hiyama
  - **Gurren Lagann (Simon)** — mission Entry character/pilot field: Simon — unit-list default character/crew refs (not mission-confirmed): Simon, Kamina, Yoko, Boota
  - **Ingram Unit 1** — mission Entry character/pilot field: Noa Izumi
  - **Ingram Unit 2** — mission Entry character/pilot field: Isao Ota
  - **Mazinger Z** — mission Entry character/pilot field: Koji Kabuto
  - **Raijin-Oh** — mission Entry character/pilot field: Jin Hyuga — unit-list default character/crew refs (not mission-confirmed): Jin Hyuga, Asuka Tsukishiro, Koji Hoshiyama
  - **Shin Getter-1 (Go)** — mission Entry character/pilot field: Go — unit-list default character/crew refs (not mission-confirmed): Go, Kei, Gai

**Enemy deployments (inferred):**
  - **Bolt Robo/Long-Range** — mission Entry character/pilot field: Mechanized Beast — ×5 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Melee** — mission Entry character/pilot field: Mechanized Beast — ×8 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Standard** — mission Entry character/pilot field: Mechanized Beast — ×9 source Entry IDs (simultaneous count not verified)
  - **Invader/Ground** — mission Entry character/pilot field: Invader — ×15 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate S IN** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Mucus Gate S MC** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×12 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Mazinger Z** — mission Entry character/pilot field: Koji Kabuto

### Episode 2 — The Black Labor (`DL102_20`)

**Source:** `eventP01.EDAT/DL102_20_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **HAL-X10/Green** — mission Entry character/pilot field: JSDF Soldier
  - **Helldiver** — mission Entry character/pilot field: JSDF Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Ingram Unit 1** — mission Entry character/pilot field: Noa Izumi
  - **Ingram Unit 2** — mission Entry character/pilot field: Isao Ota

**Enemy deployments (inferred):**
  - **Brocken/Machine Cannon** — mission Entry character/pilot field: Control AI — ×4 source Entry IDs (simultaneous count not verified)
  - **Brocken/Melee** — mission Entry character/pilot field: Control AI — ×2 source Entry IDs (simultaneous count not verified)
  - **Griffon** — mission Entry character/pilot field: Badrinath Harchand — ×2 source Entry IDs (simultaneous count not verified)

### Episode 2 — Roar of the Wild (`DL102_30`)

**Source:** `eventP01.EDAT/DL102_30_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Final Dancouga** — mission Entry character/pilot field: Shinobu Fujiwara — unit-list default character/crew refs (not mission-confirmed): Shinobu Fujiwara, Sara Yuki, Ryo Shiba, Masato Shikibu, Alan Igor
  - **Ingram Unit 1** — mission Entry character/pilot field: Noa Izumi
  - **Ingram Unit 2** — mission Entry character/pilot field: Isao Ota

**Enemy deployments (inferred):**
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)

### Episode 2 — Battle of Jaburo (`DL102_40`)

**Source:** `eventP01.EDAT/DL102_40_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **G-Fighter** — mission Entry character/pilot field: Sayla Mass
  - **Guncannon** — mission Entry character/pilot field: Kai Shiden
  - **Gundam** — mission Entry character/pilot field: Amuro Ray
  - **Gundam Ez8** — mission Entry character/pilot field: Shiro Amada
  - **Gundam Ground Type** — mission Entry character/pilot field: Terry Sanders Jr.
  - **Gundam Ground Type/GM Head** — mission Entry character/pilot field: Karen Joshua
  - **Guntank** — mission Entry character/pilot field: Hayato Kobayashi
  - **Hover Truck** — mission Entry character/pilot field: Michel Ninorich — unit-list default character/crew refs (not mission-confirmed): Michel Ninorich, Eledore Massis

**Enemy deployments (inferred):**
  - **Dom** — mission Entry character/pilot field: Zeon Soldier — ×9 source Entry IDs (simultaneous count not verified)
  - **Zaku II (Char)** — mission Entry character/pilot field: Char Aznable
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Crown
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Zeon Soldier — ×5 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Slender
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Zeon Soldier — ×3 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Zanzibar** — mission Entry character/pilot field: Zeon Officer — ×2 source Entry IDs (simultaneous count not verified)

### Episode 2 — Apsalus Assault (`DL102_50`)

**Source:** `eventP01.EDAT/DL102_50_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **G-Fighter** — mission Entry character/pilot field: Sayla Mass
  - **Guncannon** — mission Entry character/pilot field: Kai Shiden
  - **Gundam** — mission Entry character/pilot field: Amuro Ray
  - **Gundam Ez8** — mission Entry character/pilot field: Shiro Amada
  - **Gundam Ground Type** — mission Entry character/pilot field: Terry Sanders Jr.
  - **Gundam Ground Type/GM Head** — mission Entry character/pilot field: Karen Joshua
  - **Guntank** — mission Entry character/pilot field: Hayato Kobayashi
  - **Hover Truck** — mission Entry character/pilot field: Michel Ninorich — unit-list default character/crew refs (not mission-confirmed): Michel Ninorich, Eledore Massis
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Apsalus III** — mission Entry character/pilot field: Ginias Sahalin
  - **Dom** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Gouf (Ramba Ral)** — mission Entry character/pilot field: Ramba Ral
  - **Zaku II Kai** — mission Entry character/pilot field: Cozun Graham
  - **Zaku II Kai** — mission Entry character/pilot field: Zeon Soldier
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Acous
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Zeon Soldier
  - **Zanzibar** — mission Entry character/pilot field: Crowley Hamon

**Scripted units — side not established:**
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech

### Episode 2 — Forced Breakthrough (`DL102_60`)

**Source:** `eventP01.EDAT/DL102_60_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **G-Fighter** — mission Entry character/pilot field: Sayla Mass — alternate Entry ID record present
  - **Guncannon** — mission Entry character/pilot field: Kai Shiden — alternate Entry ID record present
  - **Gundam** — mission Entry character/pilot field: Amuro Ray — alternate Entry ID record present
  - **Guntank** — mission Entry character/pilot field: Hayato Kobayashi — alternate Entry ID record present
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Musai** — mission Entry character/pilot field: Dren
  - **Musai** — mission Entry character/pilot field: Zeon Officer — ×2 source Entry IDs (simultaneous count not verified)
  - **Rick Dom** — mission Entry character/pilot field: Zeon Soldier — ×6 source Entry IDs (simultaneous count not verified)

### Episode 2 — Zanzibar in Pursuit (`DL102_70`)

**Source:** `eventP01.EDAT/DL102_70_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **G-Fighter** — mission Entry character/pilot field: Sayla Mass — alternate Entry ID record present
  - **Guncannon** — mission Entry character/pilot field: Kai Shiden — alternate Entry ID record present
  - **Gundam** — mission Entry character/pilot field: Amuro Ray — alternate Entry ID record present
  - **Guntank** — mission Entry character/pilot field: Hayato Kobayashi — alternate Entry ID record present
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Bigro** — mission Entry character/pilot field: Tokwan
  - **Gelgoog (Char)** — mission Entry character/pilot field: Char Aznable
  - **Rick Dom** — mission Entry character/pilot field: Crown
  - **Rick Dom** — mission Entry character/pilot field: Slender
  - **Rick Dom** — mission Entry character/pilot field: Zeon Soldier — ×5 source Entry IDs (simultaneous count not verified)
  - **Zaku II Kai** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Zanzibar** — mission Entry character/pilot field: Zeon Officer

### Episode 2 — The Defense Class Heads to Space (`DL102_90`)

**Source:** `eventP01.EDAT/DL102_90_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Daiteioh** — mission Entry character/pilot field: Taro Omomo — unit-list default character/crew refs (not mission-confirmed): Taro Omomo, Mai Ozora, Kakeru Daichi
  - **Ganbaruger** — mission Entry character/pilot field: Kotaro Kirigakure — unit-list default character/crew refs (not mission-confirmed): Kotaro Kirigakure, Yosuke Kazamatsuri, Rikiya Ryuzaki
  - **Go-Saurer** — mission Entry character/pilot field: Kenichi Minezaki — unit-list default character/crew refs (not mission-confirmed): Kenichi Minezaki, Hiromi Tachibana, Shinobu Asaoka, Taro Shirogane, Yoji Hiyama
  - **Gurren Lagann (Simon)** — mission Entry character/pilot field: Simon — unit-list default character/crew refs (not mission-confirmed): Simon, Kamina, Yoko, Boota
  - **Raijin-Oh** — mission Entry character/pilot field: Jin Hyuga — unit-list default character/crew refs (not mission-confirmed): Jin Hyuga, Asuka Tsukishiro, Koji Hoshiyama

**Enemy deployments (inferred):**
  - **Bolt Robo/Anti-Air** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Long-Range** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Melee** — mission Entry character/pilot field: Mechanized Beast — ×5 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Standard** — mission Entry character/pilot field: Mechanized Beast — ×4 source Entry IDs (simultaneous count not verified)
  - **Brocken/Cannon** — mission Entry character/pilot field: Control AI — ×2 source Entry IDs (simultaneous count not verified)
  - **Brocken/Machine Cannon** — mission Entry character/pilot field: Control AI — ×2 source Entry IDs (simultaneous count not verified)
  - **Brocken/Melee** — mission Entry character/pilot field: Control AI — ×2 source Entry IDs (simultaneous count not verified)
  - **Gandoppler** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate S MC** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech

### Episode 3 — Episode 3 Gundam Intervention (`DL103_11`)

**Source:** `eventP01.EDAT/DL103_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Final Dancouga** — mission Entry character/pilot field: Shinobu Fujiwara — unit-list default character/crew refs (not mission-confirmed): Shinobu Fujiwara, Sara Yuki, Ryo Shiba, Masato Shikibu, Alan Igor
  - **Gundam Exia** — mission Entry character/pilot field: Setsuna F. Seiei
  - **Mazinger Z** — mission Entry character/pilot field: Koji Kabuto
  - **Shin Getter-1 (Go)** — mission Entry character/pilot field: Go — unit-list default character/crew refs (not mission-confirmed): Go, Kei, Gai
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima
  - **Wing Gundam Zero/NB** — mission Entry character/pilot field: Heero Yuy

**Enemy deployments (inferred):**
  - **Dom (Black Tri-Stars)** — mission Entry character/pilot field: Gaia
  - **Dom (Black Tri-Stars)** — mission Entry character/pilot field: Mash
  - **Dom (Black Tri-Stars)** — mission Entry character/pilot field: Ortega
  - **Gelgoog (Char)** — mission Entry character/pilot field: Char Aznable
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Zeon Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Zanzibar** — mission Entry character/pilot field: Garma Zabi
  - **Zanzibar** — mission Entry character/pilot field: M'Quve

**Scripted units — side not established:**
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech

### Episode 3 — Episode 3 A Black Shadow Creeps Closer (`DL103_12`)

**Source:** `eventP01.EDAT/DL103_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Final Dancouga** — mission Entry character/pilot field: Shinobu Fujiwara — unit-list default character/crew refs (not mission-confirmed): Shinobu Fujiwara, Sara Yuki, Ryo Shiba, Masato Shikibu, Alan Igor
  - **Gundam Exia** — mission Entry character/pilot field: Setsuna F. Seiei
  - **Mazinger Z** — mission Entry character/pilot field: Koji Kabuto
  - **Shin Getter-1 (Go)** — mission Entry character/pilot field: Go — unit-list default character/crew refs (not mission-confirmed): Go, Kei, Gai
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima
  - **Wing Gundam Zero** — mission Entry character/pilot field: Heero Yuy

**Enemy deployments (inferred):**
  - **Invader/Air** — mission Entry character/pilot field: Invader — ×6 source Entry IDs (simultaneous count not verified)
  - **Invader/Ground** — mission Entry character/pilot field: Invader — ×10 source Entry IDs (simultaneous count not verified)
  - **Metal Beast/Shell** — mission Entry character/pilot field: Invader

### Episode 3 — The Green Invader (`DL103_20`)

**Source:** `eventP01.EDAT/DL103_20_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Ingram Unit 1** — mission Entry character/pilot field: Noa Izumi
  - **Ingram Unit 2** — mission Entry character/pilot field: Isao Ota
  - **Keroro Robo Mk-II** — mission Entry character/pilot field: Sgt. Keroro

**Enemy deployments (inferred):**
  - **Brocken/Machine Cannon** — mission Entry character/pilot field: Control AI — ×5 source Entry IDs (simultaneous count not verified)
  - **Brocken/Melee** — mission Entry character/pilot field: Control AI — ×8 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Brocken/Melee** — mission Entry character/pilot field: Control AI — ×6 source Entry IDs (simultaneous count not verified)

### Episode 3 — Raid on the Pirate Base (`DL103_30`)

> **Source variants differ:** this mission code occurs in 2 packages. Each package roster is shown separately; the files are not merged.

#### Source package: `eventP01.EDAT`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Gelgoog** — mission Entry character/pilot field: MS Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Rick Dom** — mission Entry character/pilot field: MS Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Bazooka** — mission Entry character/pilot field: MS Pilot — ×3 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: MS Pilot — ×3 source Entry IDs (simultaneous count not verified)

#### Source package: `eventP09.EDAT`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Gelgoog** — mission Entry character/pilot field: MS Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Rick Dom** — mission Entry character/pilot field: MS Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Bazooka** — mission Entry character/pilot field: MS Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Zeon Soldier
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: MS Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Zeon Soldier

### Episode 3 — The Mars Base Attack (`DL103_40`)

**Source:** `eventP01.EDAT/DL103_40_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Enhanced Layzner** — mission Entry character/pilot field: Albatro Null Eiji Asuka
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass
  - **RVF-25 Messiah/Fighter** — mission Entry character/pilot field: Luca Angeloni
  - **VF-25F Messiah/Fighter** — mission Entry character/pilot field: Alto Saotome
  - **VF-25G Messiah/Fighter** — mission Entry character/pilot field: Michael Blanc

**Enemy deployments (inferred):**
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×12 source Entry IDs (simultaneous count not verified)
  - **Daljan** — mission Entry character/pilot field: Gosterro

### Episode 4 — Episode 4 Strike the Grados Warship (`DL104_11`)

**Source:** `eventP01.EDAT/DL104_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Enhanced Layzner** — mission Entry character/pilot field: Albatro Null Eiji Asuka
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×23 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Daljan** — mission Entry character/pilot field: Gosterro
  - **Grados New Giant Space Carrier** — mission Entry character/pilot field: Grados Officer — alternate Entry ID record present

### Episode 4 — The Invaders' Clutches (`DL104_20`)

**Source:** `eventP01.EDAT/DL104_20_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Shin Getter-1 (Go)** — mission Entry character/pilot field: Go — unit-list default character/crew refs (not mission-confirmed): Go, Kei, Gai
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Invader/Air** — mission Entry character/pilot field: Invader — ×8 source Entry IDs (simultaneous count not verified)
  - **Invader/Ground** — mission Entry character/pilot field: Invader — ×8 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate S IN** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech

### Episode 4 — The Time Etranger (`DL104_30`)

**Source:** `eventP01.EDAT/DL104_30_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 6 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **GoShogun** — mission Entry character/pilot field: Shingo Hojo — unit-list default character/crew refs (not mission-confirmed): Shingo Hojo, Killy Gagley, Remy Shimada
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass
  - **Raijin-Oh** — mission Entry character/pilot field: Jin Hyuga — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Jin Hyuga, Asuka Tsukishiro, Koji Hoshiyama

**Enemy deployments (inferred):**
  - **Bolt Robo/Anti-Air** — mission Entry character/pilot field: Mechanized Beast — ×7 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Bolt Robo/Long-Range** — mission Entry character/pilot field: Mechanized Beast — ×8 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Bolt Robo/Melee** — mission Entry character/pilot field: Mechanized Beast — ×4 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Bolt Robo/Standard** — mission Entry character/pilot field: Mechanized Beast — ×7 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Dark Go-Saurer** — mission Entry character/pilot field: Mechanized Beast
  - **Mucus Gate S MC** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech

### Episode 4 — Lelouch of the Rebellion (`DL104_40`)

**Source:** `eventP20.EDAT/DL104_40_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.
**Alternate-record caution:** 3 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **L-Gaim** — mission Entry character/pilot field: Daba Myroad — unit-list default character/crew refs (not mission-confirmed): Daba Myroad, Lilis Faw
  - **Novel D-Sserd** — mission Entry character/pilot field: Gaw Ha Leccee
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×23 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present

**Scripted units — side not established:**
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular
  - **Gawain** — mission Entry character/pilot field: Lelouch Lamperouge — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Zero, C.C.
  - **Gawain** — mission Entry character/pilot field: Zero — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Zero, C.C.

### Episode 5 — Episode 5 Warp Gate (`DL105_11`)

**Source:** `eventP01.EDAT/DL105_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 4 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Gurren Lagann (Simon)** — mission Entry character/pilot field: Simon — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Simon, Kamina, Yoko, Boota
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Enkidu** — mission Entry character/pilot field: Viral
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×13 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×13 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present

**Scripted units — side not established:**
  - **Vasage** — mission Entry character/pilot field: Vasage

### Episode 5 — Episode 5 Viral the Beastman (`DL105_12`)

**Source:** `eventP01.EDAT/DL105_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Final Dancouga** — mission Entry character/pilot field: Shinobu Fujiwara — unit-list default character/crew refs (not mission-confirmed): Shinobu Fujiwara, Sara Yuki, Ryo Shiba, Masato Shikibu, Alan Igor
  - **GoShogun** — mission Entry character/pilot field: Shingo Hojo — unit-list default character/crew refs (not mission-confirmed): Shingo Hojo, Killy Gagley, Remy Shimada
  - **Gundam Exia** — mission Entry character/pilot field: Setsuna F. Seiei
  - **Gurren Lagann (Kamina)** — mission Entry character/pilot field: Kamina — unit-list default character/crew refs (not mission-confirmed): Kamina, Simon, Yoko, Boota
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass
  - **Vasage** — mission Entry character/pilot field: Vasage
  - **VF-25F Messiah/Fighter** — mission Entry character/pilot field: Alto Saotome

**Enemy deployments (inferred):**
  - **Enkidu** — mission Entry character/pilot field: Viral
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×28 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×13 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech

### Episode 5 — The Boy from Planet Zi (`DL105_20`)

**Source:** `eventP01.EDAT/DL105_20_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.
**Alternate-record caution:** 2 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Command Wolf/Black/Upgraded** — mission Entry character/pilot field: Irvine
  - **Gustav/Moonbay Special** — mission Entry character/pilot field: Moonbay

**Enemy deployments (inferred):**
  - **Molga** — mission Entry character/pilot field: Zoid Pilot — ×6 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Zoid Pilot — alternate Entry ID record present

**Scripted units — side not established:**
  - **Redler (Viola)** — mission Entry character/pilot field: Viola
  - **Shield Liger** — mission Entry character/pilot field: Van Flyheight — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette

### Episode 5 — Roots of Ambition (`DL105_30`)

**Source:** `eventP01.EDAT/DL105_30_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.
**Alternate-record caution:** 4 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Scopedog RSC (Byman)** — mission Entry character/pilot field: Byman Hagard
  - **Scopedog RSC (Chirico)** — mission Entry character/pilot field: Chirico Cuvie
  - **Scopedog RSC (Gregore)** — mission Entry character/pilot field: Gregore Garosh
  - **Scopedog RSC (Murza)** — mission Entry character/pilot field: Murza Melym

**Enemy deployments (inferred):**
  - **General-Purpose Turret** — mission Entry character/pilot field: Control AI — ×4 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present — scripted target/object; not a piloted mech
  - **Scopedog TC-RS** — mission Entry character/pilot field: Red Shoulder Trooper — ×13 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Scopedog TC-RS/M** — mission Entry character/pilot field: Red Shoulder Trooper — ×8 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present

**Scripted units — side not established:**
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech

### Episode 5 — Hero Lamuness's New Journey (`DL105_40`)

**Source:** `eventP01.EDAT/DL105_40_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Keroro Robo Mk-II** — mission Entry character/pilot field: Sgt. Keroro
  - **King Squasher** — mission Entry character/pilot field: Hero Lamuness (Lamune Baba) — unit-list default character/crew refs (not mission-confirmed): Hero Lamuness (Lamune Baba), Tama-Q
  - **Queen Cideron/Ally** — mission Entry character/pilot field: Da Cider — unit-list default character/crew refs (not mission-confirmed): Da Cider, Hebi Metako

**Enemy deployments (inferred):**
  - **Monskar Medessa** — mission Entry character/pilot field: Monskar — ×6 source Entry IDs (simultaneous count not verified)
  - **Monskar Neppoon** — mission Entry character/pilot field: Monskar — ×5 source Entry IDs (simultaneous count not verified)

### Episode 5 — The Terror of the DG Cells (`DL105_50`)

**Source:** `eventP02.EDAT/DL105_50_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **God Gundam** — mission Entry character/pilot field: Domon Kasshu
  - **LCT-05-AT Space Landing Craft** — mission Entry character/pilot field: Bouleuse Gotho
  - **Scopedog** — mission Entry character/pilot field: AT Pilot — ×2 source Entry IDs (simultaneous count not verified)

**Enemy deployments (inferred):**
  - **Death Army** — mission Entry character/pilot field: DG Cells — ×6 source Entry IDs (simultaneous count not verified)
  - **Gundam Head** — mission Entry character/pilot field: DG Cells

### Episode 5 — Remnants of the Dark Dragon Clan (`DL105_70`)

**Source:** `eventP02.EDAT/DL105_70_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Dark Knight Steru/Dark Dragon Form** — mission Entry character/pilot field: Galden

**Enemy deployments (inferred):**
  - **Dark Dragon Escort Ship** — mission Entry character/pilot field: Dark Dragon Soldier
  - **Dark Dragon Soldier** — mission Entry character/pilot field: Dark Dragon Soldier — ×3 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Flying** — mission Entry character/pilot field: Dark Dragon Soldier — ×2 source Entry IDs (simultaneous count not verified)

### Episode 5 — The White Knight (`DL105_90`)

**Source:** `eventP21.EDAT/DL105_90_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned. Iron Kong SS is available.
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.
**Alternate-record caution:** 4 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Enemy deployments (inferred):**
  - **Molga** — mission Entry character/pilot field: Zoid Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Zoid Pilot — ×8 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Iron Kong SS/Ally** — mission Entry character/pilot field: Karl Lichten Schubaltz — alternate Entry ID record present
  - **Lancelot/Ally** — mission Entry character/pilot field: Suzaku Kururugi — alternate Entry ID record present
  - **Mucus Gate S** — mission Entry character/pilot field: Zoid Pilot — scripted target/object; not a piloted mech

### Episode 6 — Episode 6 Macross Frontier (`DL206_11`)

**Source:** `eventP02.EDAT/DL206_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass
  - **VF-25F Messiah/Fighter** — mission Entry character/pilot field: Alto Saotome

**Enemy deployments (inferred):**
  - **Bat-Shu/Strong** — mission Entry character/pilot field: Gavlet Gablae
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×12 source Entry IDs (simultaneous count not verified)
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×5 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Grados New Giant Space Carrier** — mission Entry character/pilot field: Grados Officer

### Episode 6 — Episode 6 The Vajra Homeworld (`DL206_12`)

**Source:** `eventP02.EDAT/DL206_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Fatty (Ground)** — mission Entry character/pilot field: Balarant Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Lesrion-class Space Battleship** — mission Entry character/pilot field: Balarant Officer

### Episode 6 — The ISTO Fleet (`DL206_50`)

**Source:** `eventP02.EDAT/DL206_50_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Enhanced Layzner** — mission Entry character/pilot field: Albatro Null Eiji Asuka — alternate Entry ID record present
  - **VF-25F Messiah/Battroid Super Pack** — mission Entry character/pilot field: Alto Saotome — alternate Entry ID record present
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×11 source Entry IDs (simultaneous count not verified)
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Lesrion-class Space Battleship** — mission Entry character/pilot field: Balarant Officer

### Episode 6 — Operation: Sever the Warp Route (`DL206_60`)

**Source:** `eventP02.EDAT/DL206_60_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×3 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×3 source Entry IDs (simultaneous count not verified)
  - **Lesrion-class Space Battleship** — mission Entry character/pilot field: Balarant Officer

### Episode 6 — The Black Organoid (`DL206_70`)

**Source:** `eventP02.EDAT/DL206_70_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Command Wolf/Black/Upgraded** — mission Entry character/pilot field: Irvine
  - **Command Wolf/White** — mission Entry character/pilot field: Helic Republic Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Command Wolf/White** — mission Entry character/pilot field: Rob Herman
  - **Gustav/Moonbay Special** — mission Entry character/pilot field: Moonbay
  - **Shield Liger** — mission Entry character/pilot field: Van Flyheight — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette

**Enemy deployments (inferred):**
  - **Dark Horn** — mission Entry character/pilot field: Guylos Imperial Officer
  - **Molga** — mission Entry character/pilot field: Guylos Imperial Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Saber Tiger (Raven)** — mission Entry character/pilot field: Raven

**Scripted units — side not established:**
  - **Mucus Gate S** — mission Entry character/pilot field: --- — scripted target/object; not a piloted mech

### Episode 6 — Deliver Supplies to the Republic (`DL206_80`)

**Source:** `eventP02.EDAT/DL206_80_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Command Wolf/Black/Upgraded** — mission Entry character/pilot field: Irvine
  - **Gustav/Moonbay Special** — mission Entry character/pilot field: Moonbay
  - **Shield Liger** — mission Entry character/pilot field: Van Flyheight — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette

**Enemy deployments (inferred):**
  - **Redler** — mission Entry character/pilot field: Guylos Imperial Officer — ×3 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Guylos Imperial Soldier — ×21 source Entry IDs (simultaneous count not verified)

### Episode 7 — Episode 7 Mt. Ossa Fortress (`DL207_11`)

**Source:** `eventP02.EDAT/DL207_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 2 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Dark Horn** — mission Entry character/pilot field: Guylos Imperial Officer — ×2 source Entry IDs (simultaneous count not verified)
  - **Dark Horn** — mission Entry character/pilot field: Guylos Imperial Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Iron Kong** — mission Entry character/pilot field: Guylos Imperial Officer
  - **Iron Kong** — mission Entry character/pilot field: Guylos Imperial Soldier — ×4 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Molga** — mission Entry character/pilot field: Zoid Core — ×41 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Redler** — mission Entry character/pilot field: Guylos Imperial Officer
  - **Redler** — mission Entry character/pilot field: Guylos Imperial Soldier — ×15 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Mucus Gate S** — mission Entry character/pilot field: Control AI — ×3 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech

### Episode 7 — Episode 7 Schubaltz's Offensive (`DL207_12`)

**Source:** `eventP02.EDAT/DL207_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 5 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Command Wolf/Black/Upgraded** — mission Entry character/pilot field: Irvine
  - **Final Dancouga** — mission Entry character/pilot field: Shinobu Fujiwara — unit-list default character/crew refs (not mission-confirmed): Shinobu Fujiwara, Sara Yuki, Ryo Shiba, Masato Shikibu, Alan Igor
  - **Gustav/Moonbay Special** — mission Entry character/pilot field: Moonbay
  - **Shield Liger** — mission Entry character/pilot field: Van Flyheight — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette

**Enemy deployments (inferred):**
  - **Dark Horn** — mission Entry character/pilot field: Guylos Imperial Officer — ×7 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Dark Horn** — mission Entry character/pilot field: Guylos Imperial Soldier — ×8 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Dark Horn** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)
  - **Iron Kong SS** — mission Entry character/pilot field: Karl Lichten Schubaltz
  - **Lancelot** — mission Entry character/pilot field: Suzaku Kururugi
  - **Molga** — mission Entry character/pilot field: Zoid Core — ×20 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Redler** — mission Entry character/pilot field: Guylos Imperial Soldier — ×12 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Gawain** — mission Entry character/pilot field: Zero — unit-list default character/crew refs (not mission-confirmed): Zero, C.C.

### Episode 7 — Episode 7 Battle for the Capital (`DL207_13`)

**Source:** `eventP02.EDAT/DL207_13_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Shield Liger** — mission Entry character/pilot field: Van Flyheight — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Dark Horn** — mission Entry character/pilot field: Guylos Imperial Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Iron Kong** — mission Entry character/pilot field: Guylos Imperial Officer — ×2 source Entry IDs (simultaneous count not verified)
  - **Iron Kong** — mission Entry character/pilot field: Guylos Imperial Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Molga** — mission Entry character/pilot field: Zoid Core — ×14 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Guylos Imperial Soldier — ×10 source Entry IDs (simultaneous count not verified)
  - **Saber Tiger (Raven)** — mission Entry character/pilot field: Raven
  - **Whale King** — mission Entry character/pilot field: Gunther Prozen

### Episode 7 — Search for Zoid Eve (`DL207_20`)

**Source:** `eventP02.EDAT/DL207_20_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Command Wolf/Black/Upgraded** — mission Entry character/pilot field: Irvine
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Gustav/Moonbay Special** — mission Entry character/pilot field: Moonbay
  - **Shield Liger** — mission Entry character/pilot field: Van Flyheight — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette

**Enemy deployments (inferred):**
  - **Molga** — mission Entry character/pilot field: Zoid Core — ×6 source Entry IDs (simultaneous count not verified)
  - **Molga** — mission Entry character/pilot field: Zoid Pilot — ×7 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Red Horn (Rosso)** — mission Entry character/pilot field: Rosso
  - **Redler (Viola)** — mission Entry character/pilot field: Viola

### Episode 7 — Woman Who Calls Herself a Black Knight (`DL207_30`)

**Source:** `eventP02.EDAT/DL207_30_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Gawain** — mission Entry character/pilot field: Zero — unit-list default character/crew refs (not mission-confirmed): Zero, C.C.
  - **Guren Mk-II** — mission Entry character/pilot field: Kallen Kozuki

**Enemy deployments (inferred):**
  - **Command Wolf/White** — mission Entry character/pilot field: Zoid Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper** — mission Entry character/pilot field: Zoid Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper/WW** — mission Entry character/pilot field: Zoid Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Molga** — mission Entry character/pilot field: Zoid Core — ×11 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Command Wolf/Khaki** — mission Entry character/pilot field: Zoid Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Command Wolf/White** — mission Entry character/pilot field: Zoid Pilot
  - **Mucus Gate S** — mission Entry character/pilot field: --- — scripted target/object; not a piloted mech

### Episode 7 — Doki Doki Space (`DL207_50`)

**Source:** `eventP02.EDAT/DL207_50_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **God Gundam** — mission Entry character/pilot field: Domon Kasshu

**Enemy deployments (inferred):**
  - **Death Army** — mission Entry character/pilot field: DG Cells — ×8 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate S DG** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)

### Episode 8 — Episode 8 Earthtia (`DL208_11`)

**Source:** `eventP02.EDAT/DL208_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Dark Knight Steru/Dark Dragon Form** — mission Entry character/pilot field: Galden
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass
  - **Ryu Knight Zephyr/Later** — mission Entry character/pilot field: Adeu Waltham
  - **Ryu Mage Magidora** — mission Entry character/pilot field: Paffy Pafuricia — unit-list default character/crew refs (not mission-confirmed): Paffy Pafuricia, Hagu Hagu

**Enemy deployments (inferred):**
  - **Dark Dragon Escort Ship** — mission Entry character/pilot field: Dark Dragon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier** — mission Entry character/pilot field: Dark Dragon Soldier — ×11 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Flying** — mission Entry character/pilot field: Dark Dragon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Sniper** — mission Entry character/pilot field: Dark Dragon Soldier — ×4 source Entry IDs (simultaneous count not verified)

### Episode 8 — Episode 8 Dark Dragon Pirates (`DL208_12`)

**Source:** `eventP02.EDAT/DL208_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Dark Dragon Soldier** — mission Entry character/pilot field: Dark Dragon Soldier — ×13 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Flying** — mission Entry character/pilot field: Dark Dragon Soldier — ×11 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Sniper** — mission Entry character/pilot field: Dark Dragon Soldier — ×9 source Entry IDs (simultaneous count not verified)

### Episode 8 — Da Cider Returns (`DL208_20`)

**Source:** `eventP02.EDAT/DL208_20_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Hulk Gunship Axe Bomber** — mission Entry character/pilot field: Cocoa Arara — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Cocoa Arara, Milk Arara, Cafe au Lait Arara
  - **Keroro Robo Mk-II** — mission Entry character/pilot field: Sgt. Keroro — alternate Entry ID record present
  - **King Squasher** — mission Entry character/pilot field: Hero Lamuness (Lamune Baba) — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Hero Lamuness (Lamune Baba), Tama-Q
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Monskar Medessa** — mission Entry character/pilot field: Monskar — ×6 source Entry IDs (simultaneous count not verified)
  - **Monskar Neppoon** — mission Entry character/pilot field: Monskar — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified)
  - **Queen Cideron** — mission Entry character/pilot field: Da Cider

### Episode 8 — Scenario `DL208_30`

> **Source variants differ:** this mission code occurs in 2 packages. Each package roster is shown separately; the files are not merged.

#### Source package: `eventP13.EDAT`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Gurren Lagann (Simon)** — mission Entry character/pilot field: Simon — unit-list default character/crew refs (not mission-confirmed): Simon, Kamina, Yoko, Boota
  - **Gustav/Moonbay Special** — mission Entry character/pilot field: Moonbay

**Enemy deployments (inferred):**
  - **Crystal Pillar** — mission Entry character/pilot field: ---
  - **Dark Dragon Soldier** — mission Entry character/pilot field: Dark Dragon Soldier — ×10 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Flying** — mission Entry character/pilot field: Dark Dragon Soldier — ×24 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Sniper** — mission Entry character/pilot field: Dark Dragon Soldier — ×8 source Entry IDs (simultaneous count not verified)

#### Source package: `eventP22.EDAT`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Gurren Lagann (Simon)** — mission Entry character/pilot field: Simon — unit-list default character/crew refs (not mission-confirmed): Simon, Kamina, Yoko, Boota
  - **Gustav/Moonbay Special** — mission Entry character/pilot field: Moonbay

**Enemy deployments (inferred):**
  - **Crystal Pillar** — mission Entry character/pilot field: ---
  - **Dark Dragon Soldier** — mission Entry character/pilot field: Dark Dragon Soldier — ×10 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Flying** — mission Entry character/pilot field: Dark Dragon Soldier — ×24 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Sniper** — mission Entry character/pilot field: Dark Dragon Soldier — ×8 source Entry IDs (simultaneous count not verified)

### Episode 8 — Red Shoulder (`DL208_45`)

**Source:** `eventP02.EDAT/DL208_45_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Scopedog RSC (Byman)** — mission Entry character/pilot field: Byman Hagard
  - **Scopedog RSC (Chirico)** — mission Entry character/pilot field: Chirico Cuvie
  - **Scopedog RSC (Gregore)** — mission Entry character/pilot field: Gregore Garosh — alternate Entry ID record present
  - **Scopedog RSC (Murza)** — mission Entry character/pilot field: Murza Melym — alternate Entry ID record present

**Enemy deployments (inferred):**
  - **Scopedog** — mission Entry character/pilot field: AT Pilot — ×13 source Entry IDs (simultaneous count not verified)
  - **Scopedog/M** — mission Entry character/pilot field: AT Pilot — ×8 source Entry IDs (simultaneous count not verified)

### Episode 8 — Battle of Sunsa (`DL208_50`)

**Source:** `eventP02.EDAT/DL208_50_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Scopedog RSC (Byman)** — mission Entry character/pilot field: Byman Hagard
  - **Scopedog RSC (Chirico)** — mission Entry character/pilot field: Chirico Cuvie
  - **Scopedog RSC (Gregore)** — mission Entry character/pilot field: Gregore Garosh
  - **Scopedog RSC (Murza)** — mission Entry character/pilot field: Murza Melym

**Enemy deployments (inferred):**
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Balarant Land Battleship** — mission Entry character/pilot field: Balarant Officer
  - **Fatty (Ground)** — mission Entry character/pilot field: Balarant Soldier — ×25 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech

**Scripted units — side not established:**
  - **Scopedog TC-RS** — mission Entry character/pilot field: Red Shoulder Trooper — ×2 source Entry IDs (simultaneous count not verified)
  - **Scopedog TC-RS/M** — mission Entry character/pilot field: Red Shoulder Trooper

### Episode 9 — Episode 9 Intervention at Sunsa (`DL209_11`)

**Source:** `eventP02.EDAT/DL209_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass
  - **VF-25F Messiah/Fighter Super Pack** — mission Entry character/pilot field: Alto Saotome

**Enemy deployments (inferred):**
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×10 source Entry IDs (simultaneous count not verified)
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Ray** — mission Entry character/pilot field: Posaydal Regular Officer

### Episode 9 — Episode 9 Death Match with Riemann (`DL209_12`)

**Source:** `eventP02.EDAT/DL209_12_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Scopedog RSC (Byman)** — mission Entry character/pilot field: Byman Hagard
  - **Scopedog RSC (Chirico)** — mission Entry character/pilot field: Chirico Cuvie
  - **Scopedog RSC (Gregore)** — mission Entry character/pilot field: Gregore Garosh
  - **Scopedog RSC (Murza)** — mission Entry character/pilot field: Murza Melym

**Enemy deployments (inferred):**
  - **Balarant Land Battleship** — mission Entry character/pilot field: Balarant Officer
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×2 source Entry IDs (simultaneous count not verified)
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Fatty (Ground)** — mission Entry character/pilot field: Balarant Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Scopedog RS (Riemann)** — mission Entry character/pilot field: Inge Riemann
  - **Scopedog TC-RS** — mission Entry character/pilot field: Gilgamesh Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Scopedog TC-RS/M** — mission Entry character/pilot field: Gilgamesh Soldier — ×4 source Entry IDs (simultaneous count not verified)

### Episode 9 — Episode 9 Seed of the Mucus (`DL209_13`)

**Source:** `eventP02.EDAT/DL209_13_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Scopedog RSC (Chirico)** — mission Entry character/pilot field: Chirico Cuvie
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×5 source Entry IDs (simultaneous count not verified)
  - **Balarant Land Battleship** — mission Entry character/pilot field: Balarant Officer
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×2 source Entry IDs (simultaneous count not verified)
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Fatty (Ground)** — mission Entry character/pilot field: Balarant Soldier — ×12 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus
  - **Mucus Gate M** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Sarge Aupus (Nei)** — mission Entry character/pilot field: Nei Moh Han

**Scripted units — side not established:**
  - **Scopedog RSC (Byman)** — mission Entry character/pilot field: Byman Hagard
  - **Scopedog RSC (Chirico)** — mission Entry character/pilot field: Chirico Cuvie
  - **Scopedog RSC (Gregore)** — mission Entry character/pilot field: Gregore Garosh
  - **Scopedog RSC (Murza)** — mission Entry character/pilot field: Murza Melym

### Episode 9 — The Shadow of Drago Returns (`DL209_20`)

**Source:** `eventP02.EDAT/DL209_20_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Go-Saurer** — mission Entry character/pilot field: Kenichi Minezaki — unit-list default character/crew refs (not mission-confirmed): Kenichi Minezaki, Hiromi Tachibana, Shinobu Asaoka, Taro Shirogane, Yoji Hiyama
  - **Liger** — mission Entry character/pilot field: Ken Taiga

**Enemy deployments (inferred):**
  - **Mass-Produced Metal Knight** — mission Entry character/pilot field: Metal Knight — ×5 source Entry IDs (simultaneous count not verified)
  - **Mass-Produced Metal Knight/Heavy** — mission Entry character/pilot field: Metal Knight — ×4 source Entry IDs (simultaneous count not verified)

### Episode 9 — Griffon VS Alphonse (`DL209_35`)

**Source:** `eventP02.EDAT/DL209_35_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Ingram Unit 1** — mission Entry character/pilot field: Noa Izumi

**Enemy deployments (inferred):**
  - **Griffon** — mission Entry character/pilot field: Badrinath Harchand

### Episode 9 — Warriors Adrift (`DL209_40`)

**Source:** `eventP03.EDAT/DL209_40_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Medea** — mission Entry character/pilot field: Zechs Merquise
  - **Tallgeese/Ally** — mission Entry character/pilot field: Zechs Merquise
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima
  - **Wing Gundam Zero** — mission Entry character/pilot field: Heero Yuy

**Enemy deployments (inferred):**
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate M** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×12 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×10 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Tallgeese** — mission Entry character/pilot field: Zechs Merquise
  - **Zanzibar** — mission Entry character/pilot field: Zeon Officer

### Episode 9 — The Mechanization Empire's Next Move (`DL209_60`)

**Source:** `eventP03.EDAT/DL209_60_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Daiteioh** — mission Entry character/pilot field: Taro Omomo — unit-list default character/crew refs (not mission-confirmed): Taro Omomo, Mai Ozora, Kakeru Daichi
  - **Ganbaruger** — mission Entry character/pilot field: Kotaro Kirigakure — unit-list default character/crew refs (not mission-confirmed): Kotaro Kirigakure, Yosuke Kazamatsuri, Rikiya Ryuzaki
  - **Go-Saurer** — mission Entry character/pilot field: Kenichi Minezaki — unit-list default character/crew refs (not mission-confirmed): Kenichi Minezaki, Hiromi Tachibana, Shinobu Asaoka, Taro Shirogane, Yoji Hiyama
  - **Liger** — mission Entry character/pilot field: Ken Taiga

**Enemy deployments (inferred):**
  - **Bolt Robo/Anti-Air** — mission Entry character/pilot field: Mechanized Beast
  - **Bolt Robo/Long-Range** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Standard** — mission Entry character/pilot field: Mechanized Beast — ×4 source Entry IDs (simultaneous count not verified)
  - **HAL-X10** — mission Entry character/pilot field: Shinohara HOS — ×4 source Entry IDs (simultaneous count not verified)
  - **Helldiver** — mission Entry character/pilot field: Control AI — ×4 source Entry IDs (simultaneous count not verified)

### Episode 9 — The 30 Bunch Incident (`DL209_70`)

**Source:** `eventP23.EDAT/DL209_70_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Gundam Exia** — mission Entry character/pilot field: Setsuna F. Seiei
  - **Hyaku Shiki** — mission Entry character/pilot field: Quattro Bajeena
  - **Zeta Gundam** — mission Entry character/pilot field: Kamille Bidan

**Enemy deployments (inferred):**
  - **Rick Dom** — mission Entry character/pilot field: MS Pilot — ×7 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Bazooka** — mission Entry character/pilot field: MS Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: MS Pilot — ×3 source Entry IDs (simultaneous count not verified)

### Episode 10 — Episode 10 Signs of the Evil God (`DL310_11`)

**Source:** `eventP03.EDAT/DL310_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Ganbaruger** — mission Entry character/pilot field: Kotaro Kirigakure — unit-list default character/crew refs (not mission-confirmed): Kotaro Kirigakure, Yosuke Kazamatsuri, Rikiya Ryuzaki
  - **Liger** — mission Entry character/pilot field: Ken Taiga
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Mass-Produced Metal Knight** — mission Entry character/pilot field: Metal Knight — ×12 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×23 source Entry IDs (simultaneous count not verified)

### Episode 10 — Episode 10 The Mucus Gate Below (`DL310_12`)

**Source:** `eventP03.EDAT/DL310_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Liger** — mission Entry character/pilot field: Ken Taiga

**Enemy deployments (inferred):**
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus
  - **Mass-Produced Metal Knight** — mission Entry character/pilot field: Metal Knight — ×13 source Entry IDs (simultaneous count not verified)
  - **Mass-Produced Metal Knight/Heavy** — mission Entry character/pilot field: Metal Knight — ×3 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate M DR** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)

### Episode 10 — Talking with the Envoy (`DL310_20`)

**Source:** `eventP03.EDAT/DL310_20_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass
  - **Vasage** — mission Entry character/pilot field: Vasage

**Enemy deployments (inferred):**
  - **Benthos Cruiser α** — mission Entry character/pilot field: Mucus
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate M** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×12 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech

**Scripted units — side not established:**
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech

### Episode 10 — Operation: Seize the Alex (`DL310_40`)

**Source:** `eventP03.EDAT/DL310_40_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Guncannon** — mission Entry character/pilot field: Kai Shiden
  - **Gundam** — mission Entry character/pilot field: Amuro Ray
  - **Gundam Ez8** — mission Entry character/pilot field: Shiro Amada
  - **Gundam Ground Type** — mission Entry character/pilot field: Terry Sanders Jr.
  - **Gundam Ground Type/GM Head** — mission Entry character/pilot field: Karen Joshua
  - **Guntank** — mission Entry character/pilot field: Hayato Kobayashi
  - **Hover Truck** — mission Entry character/pilot field: Michel Ninorich — unit-list default character/crew refs (not mission-confirmed): Michel Ninorich, Eledore Massis
  - **NT-1 Alex** — mission Entry character/pilot field: Christina Mackenzie

**Enemy deployments (inferred):**
  - **Gelgoog** — mission Entry character/pilot field: Crown
  - **Gelgoog** — mission Entry character/pilot field: Slender
  - **Gelgoog (Char)** — mission Entry character/pilot field: Char Aznable
  - **Kampfer/Bazooka** — mission Entry character/pilot field: Mikhail Kaminsky
  - **Kampfer/High Mobility** — mission Entry character/pilot field: Hardy Steiner
  - **Zaku II Kai** — mission Entry character/pilot field: Andy Strauss
  - **Zaku II Kai** — mission Entry character/pilot field: Bernard Wiseman
  - **Zaku II Kai** — mission Entry character/pilot field: Gabriel Ramirez Garcia
  - **Zaku II Kai** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)

### Episode 10 — Stop the Nuclear Attack (`DL310_50`)

**Source:** `eventP03.EDAT/DL310_50_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Enemy deployments (inferred):**
  - **Gattle** — mission Entry character/pilot field: Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Musai** — mission Entry character/pilot field: Zeon Officer — ×2 source Entry IDs (simultaneous count not verified)
  - **Rick Dom** — mission Entry character/pilot field: Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)

### Episode 10 — Space Fortress Solomon (`DL310_60`)

**Source:** `eventP03.EDAT/DL310_60_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **G-Fighter** — mission Entry character/pilot field: Sayla Mass — alternate Entry ID record present
  - **Guncannon** — mission Entry character/pilot field: Kai Shiden — alternate Entry ID record present
  - **Gundam** — mission Entry character/pilot field: Amuro Ray — alternate Entry ID record present
  - **Guntank** — mission Entry character/pilot field: Hayato Kobayashi — alternate Entry ID record present
  - **NT-1 Alex** — mission Entry character/pilot field: Christina Mackenzie — alternate Entry ID record present
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Big Zam** — mission Entry character/pilot field: Dozle Zabi
  - **Gwazine** — mission Entry character/pilot field: Conscon
  - **Kampfer/Bazooka** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Rick Dom** — mission Entry character/pilot field: Zeon Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Zaku II Kai** — mission Entry character/pilot field: Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Mucus Gate S** — mission Entry character/pilot field: Control AI — scripted target/object; not a piloted mech

### Episode 11 — Episode 11 Operation Retake the Ark (`DL311_11`)

**Source:** `eventP03.EDAT/DL311_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Ingram Unit 1** — mission Entry character/pilot field: Noa Izumi
  - **Ingram Unit 2** — mission Entry character/pilot field: Isao Ota
  - **Scopedog RSC (Chirico)** — mission Entry character/pilot field: Chirico Cuvie

**Enemy deployments (inferred):**
  - **Bolt Robo/Long-Range** — mission Entry character/pilot field: Mechanized Beast — ×4 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Melee** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Standard** — mission Entry character/pilot field: Mechanized Beast — ×6 source Entry IDs (simultaneous count not verified)
  - **Chaldea** — mission Entry character/pilot field: Control AI — ×30 source Entry IDs (simultaneous count not verified)
  - **HAL-X10** — mission Entry character/pilot field: Shinohara HOS — ×2 source Entry IDs (simultaneous count not verified)
  - **Helldiver** — mission Entry character/pilot field: Control AI — ×10 source Entry IDs (simultaneous count not verified)
  - **Type-Zero/Enemy** — mission Entry character/pilot field: Shinohara HOS

### Episode 11 — Ep. 11 The Door That Opens in Darkness (`DL311_12`)

**Source:** `eventP03.EDAT/DL311_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Shin Getter-1 (Go)** — mission Entry character/pilot field: Go — unit-list default character/crew refs (not mission-confirmed): Go, Kei, Gai

**Enemy deployments (inferred):**
  - **Bolt Robo/Standard** — mission Entry character/pilot field: Mechanized Beast — ×4 source Entry IDs (simultaneous count not verified)
  - **Chaldea** — mission Entry character/pilot field: Control AI — ×20 source Entry IDs (simultaneous count not verified)
  - **Gandoppler** — mission Entry character/pilot field: Mechanized Beast — ×4 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate M MC** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)

### Episode 11 — Ep. 11 Den of the Mechanization Empire (`DL311_13`)

**Source:** `eventP03.EDAT/DL311_13_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Go-Saurer** — mission Entry character/pilot field: Kenichi Minezaki — unit-list default character/crew refs (not mission-confirmed): Kenichi Minezaki, Hiromi Tachibana, Shinobu Asaoka, Taro Shirogane, Yoji Hiyama

**Enemy deployments (inferred):**
  - **Bolt Robo/Anti-Air** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Long-Range** — mission Entry character/pilot field: Mechanized Beast — ×6 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Melee** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Standard** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Chaldea** — mission Entry character/pilot field: Control AI — ×20 source Entry IDs (simultaneous count not verified)
  - **Control Unit (Mega Castle)** — mission Entry character/pilot field: Mechanized Beast
  - **Dark Go-Saurer** — mission Entry character/pilot field: Mechanized Beast
  - **HAL-X10** — mission Entry character/pilot field: Control AI — ×6 source Entry IDs (simultaneous count not verified)
  - **Helldiver** — mission Entry character/pilot field: Control AI — ×6 source Entry IDs (simultaneous count not verified)
  - **Type-Zero/Enemy** — mission Entry character/pilot field: Control AI — ×4 source Entry IDs (simultaneous count not verified)

### Episode 11 — SV2 and a New Ally (`DL311_20`)

**Source:** `eventP03.EDAT/DL311_20_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Griffon/Ally** — mission Entry character/pilot field: Badrinath Harchand
  - **Ingram Unit 1** — mission Entry character/pilot field: Noa Izumi
  - **Ingram Unit 2** — mission Entry character/pilot field: Isao Ota
  - **Type-Zero** — mission Entry character/pilot field: Kanuka Clancy

**Enemy deployments (inferred):**
  - **Brocken/Cannon** — mission Entry character/pilot field: Labor Pilot — ×7 source Entry IDs (simultaneous count not verified)
  - **Brocken/Machine Cannon** — mission Entry character/pilot field: Labor Pilot — ×9 source Entry IDs (simultaneous count not verified)
  - **Brocken/Melee** — mission Entry character/pilot field: Labor Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Chaldea** — mission Entry character/pilot field: Control AI — ×12 source Entry IDs (simultaneous count not verified)
  - **Kampfer/Bazooka** — mission Entry character/pilot field: MS Pilot
  - **Zaku II Kai** — mission Entry character/pilot field: MS Pilot — ×2 source Entry IDs (simultaneous count not verified)

### Episode 11 — Operation Stop the Solar Ray (`DL311_40`)

**Source:** `eventP24.EDAT/DL311_40_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Big Zam** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Gattle** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Gelgoog** — mission Entry character/pilot field: Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Rick Dom** — mission Entry character/pilot field: Zeon Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Zanzibar** — mission Entry character/pilot field: Zeon Officer

### Episode 11 — The Pulse of Zeta (`DL311_50`)

**Source:** `eventP03.EDAT/DL311_50_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Hyaku Shiki** — mission Entry character/pilot field: Quattro Bajeena
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima
  - **Zeta Gundam** — mission Entry character/pilot field: Kamille Bidan

**Enemy deployments (inferred):**
  - **Gattle** — mission Entry character/pilot field: Zeon Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Gelgoog** — mission Entry character/pilot field: Zeon Soldier — ×14 source Entry IDs (simultaneous count not verified)
  - **Gwazine** — mission Entry character/pilot field: Zeon Officer
  - **Kampfer/High Mobility** — mission Entry character/pilot field: Zeon Soldier — ×9 source Entry IDs (simultaneous count not verified)
  - **Musai** — mission Entry character/pilot field: Zeon Officer — ×2 source Entry IDs (simultaneous count not verified)
  - **Rick Dom** — mission Entry character/pilot field: Zeon Soldier — ×15 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Zeon Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Zeon Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Zanzibar** — mission Entry character/pilot field: Zeon Officer

### Episode 12 — Episode 12 Guardians of the Colonies (`DL312_11`)

**Source:** `eventP03.EDAT/DL312_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Gundam Exia** — mission Entry character/pilot field: Setsuna F. Seiei
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Brocken/Cannon** — mission Entry character/pilot field: Control AI — ×8 source Entry IDs (simultaneous count not verified)
  - **Brocken/Machine Cannon** — mission Entry character/pilot field: Control AI — ×10 source Entry IDs (simultaneous count not verified)
  - **Chaldea** — mission Entry character/pilot field: Control AI — ×10 source Entry IDs (simultaneous count not verified)
  - **Dark Go-Saurer** — mission Entry character/pilot field: Mechanized Beast
  - **Gelgoog** — mission Entry character/pilot field: Control AI — ×4 source Entry IDs (simultaneous count not verified)
  - **Kampfer/Bazooka** — mission Entry character/pilot field: Control AI — ×2 source Entry IDs (simultaneous count not verified)
  - **Zaku II Kai** — mission Entry character/pilot field: Control AI — ×8 source Entry IDs (simultaneous count not verified)

### Episode 12 — Episode 12 Mop-Up Operation (`DL312_12`)

**Source:** `eventP03.EDAT/DL312_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Wing Gundam Zero** — mission Entry character/pilot field: Heero Yuy

**Enemy deployments (inferred):**
  - **Bolt Robo/Anti-Air** — mission Entry character/pilot field: Mechanized Beast — ×4 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Melee** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Standard** — mission Entry character/pilot field: Mechanized Beast — ×5 source Entry IDs (simultaneous count not verified)
  - **Brocken/Cannon** — mission Entry character/pilot field: Control AI — ×6 source Entry IDs (simultaneous count not verified)
  - **Brocken/Machine Cannon** — mission Entry character/pilot field: Control AI — ×8 source Entry IDs (simultaneous count not verified)
  - **Chaldea** — mission Entry character/pilot field: Control AI — ×16 source Entry IDs (simultaneous count not verified)
  - **Dark Go-Saurer** — mission Entry character/pilot field: Mechanized Beast
  - **Gandoppler** — mission Entry character/pilot field: Mechanized Beast — ×9 source Entry IDs (simultaneous count not verified)
  - **Gelgoog** — mission Entry character/pilot field: Control AI — ×5 source Entry IDs (simultaneous count not verified)
  - **Rick Dom** — mission Entry character/pilot field: Control AI — ×5 source Entry IDs (simultaneous count not verified)

### Episode 12 — The Mucus Nesting in the Asteroid Belt (`DL312_20`)

**Source:** `eventP03.EDAT/DL312_20_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×8 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×8 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)

### Episode 12 — Assassinate Rudolph (`DL312_40`)

**Source:** `eventP03.EDAT/DL312_40_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Red Horn (Rosso Ally)** — mission Entry character/pilot field: Rosso
  - **Redler (Viola Ally)** — mission Entry character/pilot field: Viola

**Enemy deployments (inferred):**
  - **Command Wolf/White** — mission Entry character/pilot field: Zoid Pilot — ×3 source Entry IDs (simultaneous count not verified)
  - **Dark Horn** — mission Entry character/pilot field: Guylos Imperial Soldier — ×2 source Entry IDs (simultaneous count not verified)

### Episode 12 — The Beast Reborn (`DL312_50`)

**Source:** `eventP03.EDAT/DL312_50_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 5 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Command Wolf/Black/Upgraded** — mission Entry character/pilot field: Irvine
  - **Gustav/Moonbay Special** — mission Entry character/pilot field: Moonbay
  - **Red Horn (Rosso Ally)** — mission Entry character/pilot field: Rosso
  - **Redler (Viola Ally)** — mission Entry character/pilot field: Viola — alternate Entry ID record present
  - **Redler (Viola)** — mission Entry character/pilot field: Viola — alternate Entry ID record present
  - **Shield Liger** — mission Entry character/pilot field: Van Flyheight — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette

**Enemy deployments (inferred):**
  - **Dark Horn** — mission Entry character/pilot field: Zoid Core — ×6 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Geno Breaker** — mission Entry character/pilot field: Raven
  - **Molga** — mission Entry character/pilot field: Zoid Core — ×8 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Redler** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech

### Episode 12 — Valiant! The Geno Breaker (`DL312_60`)

**Source:** `eventP03.EDAT/DL312_60_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Blade Liger** — mission Entry character/pilot field: Van Flyheight — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette
  - **Shield Liger** — mission Entry character/pilot field: Van Flyheight — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Dark Horn** — mission Entry character/pilot field: Zoid Core — ×7 source Entry IDs (simultaneous count not verified)
  - **Geno Breaker** — mission Entry character/pilot field: Raven
  - **Gun Sniper** — mission Entry character/pilot field: Zoid Core — ×5 source Entry IDs (simultaneous count not verified)
  - **Molga** — mission Entry character/pilot field: Zoid Core — ×15 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Zoid Core — ×12 source Entry IDs (simultaneous count not verified)

### Episode 13 — Episode 13 The Young King Returns (`DL313_11`)

**Source:** `eventP03.EDAT/DL313_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Dark Horn** — mission Entry character/pilot field: Guylos Imperial Officer — ×2 source Entry IDs (simultaneous count not verified)
  - **Dark Horn** — mission Entry character/pilot field: Guylos Imperial Soldier — ×3 source Entry IDs (simultaneous count not verified)
  - **Iron Kong** — mission Entry character/pilot field: Guylos Imperial Officer — ×3 source Entry IDs (simultaneous count not verified)
  - **Molga** — mission Entry character/pilot field: Guylos Imperial Soldier — ×14 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Guylos Imperial Soldier — ×10 source Entry IDs (simultaneous count not verified)
  - **Whale King** — mission Entry character/pilot field: Guylos Imperial Officer

**Scripted units — side not established:**
  - **Death Saurer/Replica** — mission Entry character/pilot field: Gunther Prozen
  - **Iron Kong** — mission Entry character/pilot field: Guylos Imperial Officer — ×2 source Entry IDs (simultaneous count not verified)
  - **Molga** — mission Entry character/pilot field: Guylos Imperial Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate S** — mission Entry character/pilot field: No mission-assigned pilot key — scripted target/object; not a piloted mech
  - **Redler** — mission Entry character/pilot field: Guylos Imperial Soldier — ×4 source Entry IDs (simultaneous count not verified)

### Episode 13 — Ep. 13 The Imperial Capital in Flames (`DL313_12`)

**Source:** `eventP03.EDAT/DL313_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Blade Liger** — mission Entry character/pilot field: Van Flyheight — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette
  - **Command Wolf/Black/Upgraded** — mission Entry character/pilot field: Irvine
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Gawain** — mission Entry character/pilot field: Zero — unit-list default character/crew refs (not mission-confirmed): Zero, C.C.
  - **Gustav/Moonbay Special** — mission Entry character/pilot field: Moonbay
  - **Lancelot/Ally** — mission Entry character/pilot field: Suzaku Kururugi

**Enemy deployments (inferred):**
  - **Dark Horn** — mission Entry character/pilot field: Guylos Imperial Officer — ×2 source Entry IDs (simultaneous count not verified)
  - **Dark Horn** — mission Entry character/pilot field: Guylos Imperial Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Death Saurer/Replica** — mission Entry character/pilot field: Gunther Prozen
  - **Iron Kong** — mission Entry character/pilot field: Guylos Imperial Officer — ×4 source Entry IDs (simultaneous count not verified)
  - **Molga** — mission Entry character/pilot field: Guylos Imperial Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Guylos Imperial Soldier — ×4 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Mucus Gate S** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech

### Episode 13 — Holy Warrior of a Fallen Kingdom (`DL313_25`)

**Source:** `eventP03.EDAT/DL313_25_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Dunbine** — mission Entry character/pilot field: Show Zama — unit-list default character/crew refs (not mission-confirmed): Show Zama, Chum Huau

**Enemy deployments (inferred):**
  - **Monskar Medessa** — mission Entry character/pilot field: Monskar
  - **Monskar Neppoon** — mission Entry character/pilot field: Monskar
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Zwarth** — mission Entry character/pilot field: Black Knight

### Episode 13 — Coordinator (`DL313_40`)

**Source:** `eventP03.EDAT/DL313_40_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.
**Alternate-record caution:** 2 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Infinite Justice Gundam** — mission Entry character/pilot field: Athrun Zala
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Strike Freedom Gundam** — mission Entry character/pilot field: Kira Yamato

**Enemy deployments (inferred):**
  - **Dreissen** — mission Entry character/pilot field: Neo Zeon Soldier — ×3 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Endra** — mission Entry character/pilot field: Neo Zeon Officer — ×2 source Entry IDs (simultaneous count not verified)
  - **Gaza-C** — mission Entry character/pilot field: Neo Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Gaza-C/MA** — mission Entry character/pilot field: Neo Zeon Soldier
  - **Musai** — mission Entry character/pilot field: Neo Zeon Officer
  - **Rick Dom** — mission Entry character/pilot field: Neo Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Zaku II Kai** — mission Entry character/pilot field: Neo Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Zaku III (Rakan)** — mission Entry character/pilot field: Rakan Dahkaran

### Episode 13 — Leccee Mind (`DL313_55`)

**Source:** `eventP04.EDAT/DL313_55_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.
**Alternate-record caution:** 2 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **D-Sserd** — mission Entry character/pilot field: Fannaria Amm
  - **L-Gaim** — mission Entry character/pilot field: Daba Myroad — unit-list default character/crew refs (not mission-confirmed): Daba Myroad, Lilis Faw
  - **Novel D-Sserd** — mission Entry character/pilot field: Gaw Ha Leccee
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×3 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu/Strong** — mission Entry character/pilot field: Gavlet Gablae
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×6 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present

### Episode 13 — Seize the Nuclear Storage Facility (`DL313_66`)

**Source:** `eventP04.EDAT/DL313_66_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Gundam Ez8** — mission Entry character/pilot field: Shiro Amada
  - **Gundam Ground Type** — mission Entry character/pilot field: Terry Sanders Jr.
  - **Gundam Ground Type/GM Head** — mission Entry character/pilot field: Karen Joshua
  - **Hover Truck** — mission Entry character/pilot field: Michel Ninorich — unit-list default character/crew refs (not mission-confirmed): Michel Ninorich, Eledore Massis
  - **Hyaku Shiki** — mission Entry character/pilot field: Quattro Bajeena
  - **Zeta Gundam** — mission Entry character/pilot field: Kamille Bidan

**Enemy deployments (inferred):**
  - **Gelgoog** — mission Entry character/pilot field: MS Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Zaku II Kai** — mission Entry character/pilot field: MS Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Bazooka** — mission Entry character/pilot field: MS Pilot — ×8 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: MS Pilot — ×8 source Entry IDs (simultaneous count not verified)

### Episode 13 — The Nighthawk's Dream (`DL313_70`)

**Source:** `eventP25.EDAT/DL313_70_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Iron Kong Mk-II** — mission Entry character/pilot field: Karl Lichten Schubaltz
  - **Murasame Liger** — mission Entry character/pilot field: Ruuji Familon
  - **Red Horn (Rosso Ally)** — mission Entry character/pilot field: Rosso
  - **Redler (Viola Ally)** — mission Entry character/pilot field: Viola

**Enemy deployments (inferred):**
  - **Command Wolf/Khaki** — mission Entry character/pilot field: Zoid Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Dark Horn** — mission Entry character/pilot field: Zoid Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper** — mission Entry character/pilot field: Zoid Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper/WW** — mission Entry character/pilot field: Zoid Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Iron Kong** — mission Entry character/pilot field: Zoid Pilot
  - **Molga** — mission Entry character/pilot field: Zoid Pilot — ×4 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Iron Kong Mk-II** — mission Entry character/pilot field: Karl Lichten Schubaltz
  - **Mucus Gate S** — mission Entry character/pilot field: Control AI — scripted target/object; not a piloted mech
  - **Murasame Liger** — mission Entry character/pilot field: Ruuji Familon
  - **Red Horn (Rosso)** — mission Entry character/pilot field: Rosso
  - **Redler (Viola Ally)** — mission Entry character/pilot field: Viola

### Episode 14 — Episode 14 War Cloud (`DL414_11`)

**Source:** `eventP04.EDAT/DL414_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Dunbine** — mission Entry character/pilot field: Show Zama — unit-list default character/crew refs (not mission-confirmed): Show Zama, Chum Huau
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Auge** — mission Entry character/pilot field: Nei Moh Han
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×8 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu/Strong** — mission Entry character/pilot field: Hekeler Mauzer
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×11 source Entry IDs (simultaneous count not verified)
  - **Fatty (Ground)** — mission Entry character/pilot field: Balarant Soldier — ×10 source Entry IDs (simultaneous count not verified)
  - **Sarge Aupus (Nei)** — mission Entry character/pilot field: Antoon Randow

### Episode 14 — Episode 14 Against (`DL414_12`)

**Source:** `eventP04.EDAT/DL414_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **D-Sserd** — mission Entry character/pilot field: Fannaria Amm — alternate Entry ID record present
  - **L-Gaim** — mission Entry character/pilot field: Daba Myroad — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Daba Myroad, Lilis Faw
  - **Novel D-Sserd** — mission Entry character/pilot field: Gaw Ha Leccee — alternate Entry ID record present
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×6 source Entry IDs (simultaneous count not verified)
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×10 source Entry IDs (simultaneous count not verified)
  - **Directional Mine** — mission Entry character/pilot field: Control AI — ×6 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Fatty (Ground)** — mission Entry character/pilot field: Balarant Soldier — ×10 source Entry IDs (simultaneous count not verified)

### Episode 14 — Episode 14 Planet Bomber (`DL414_13`)

**Source:** `eventP04.EDAT/DL414_13_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 2 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **D-Sserd** — mission Entry character/pilot field: Fannaria Amm
  - **L-Gaim** — mission Entry character/pilot field: Daba Myroad — unit-list default character/crew refs (not mission-confirmed): Daba Myroad, Lilis Faw
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Novel D-Sserd** — mission Entry character/pilot field: Gaw Ha Leccee

**Enemy deployments (inferred):**
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu** — mission Entry character/pilot field: Hatchia Motchia
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×8 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Bat-Shu/Strong** — mission Entry character/pilot field: Gavlet Gablae
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×12 source Entry IDs (simultaneous count not verified)
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Slender Skala** — mission Entry character/pilot field: Posaydal Regular Officer

### Episode 14 — Guardian Force (`DL414_25`)

**Source:** `eventP04.EDAT/DL414_25_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Blade Liger** — mission Entry character/pilot field: Van Flyheight — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette
  - **Dibison** — mission Entry character/pilot field: Thomas Richard Schubaltz
  - **Gustav/Moonbay Special** — mission Entry character/pilot field: Moonbay
  - **Lightning Saix** — mission Entry character/pilot field: Irvine

**Enemy deployments (inferred):**
  - **Gun Sniper** — mission Entry character/pilot field: Guylos Imperial Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Iron Kong SS** — mission Entry character/pilot field: Karl Lichten Schubaltz
  - **Molga** — mission Entry character/pilot field: Guylos Imperial Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Red Horn (Rosso)** — mission Entry character/pilot field: Rosso
  - **Redler** — mission Entry character/pilot field: Guylos Imperial Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Redler (Viola)** — mission Entry character/pilot field: Viola

### Episode 14 — Ryoma Returns (`DL414_35`)

**Source:** `eventP04.EDAT/DL414_35_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Gurren Lagann (Simon)** — mission Entry character/pilot field: Simon — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Simon, Kamina, Yoko, Boota
  - **Shin Getter-1 (Go)** — mission Entry character/pilot field: Go — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Go, Kei, Gai
  - **Shin Getter-1 (Ryoma)** — mission Entry character/pilot field: Ryoma Nagare — unit-list default character/crew refs (not mission-confirmed): Ryoma Nagare, Hayato Jin, Benkei Kuruma
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Benthos Cruiser α** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Enkidu** — mission Entry character/pilot field: Viral
  - **Invader/Starfish** — mission Entry character/pilot field: Invader — ×32 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)

### Episode 14 — ZZ Gundam Transport Operation (`DL414_45`)

**Source:** `eventP04.EDAT/DL414_45_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima
  - **Zeta Gundam** — mission Entry character/pilot field: Kamille Bidan

**Enemy deployments (inferred):**
  - **Dreissen** — mission Entry character/pilot field: Neo Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Gaza-C** — mission Entry character/pilot field: Neo Zeon Soldier — ×10 source Entry IDs (simultaneous count not verified)
  - **Gaza-C/MA** — mission Entry character/pilot field: Neo Zeon Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Qubeley Mk-II (Ple)** — mission Entry character/pilot field: Elpeo Ple

### Episode 14 — The Boy of Shangri-La (`DL414_50`)

**Source:** `eventP04.EDAT/DL414_50_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Gundam** — mission Entry character/pilot field: Amuro Ray
  - **Hyaku Shiki** — mission Entry character/pilot field: Quattro Bajeena
  - **Zeta Gundam** — mission Entry character/pilot field: Kamille Bidan
  - **ZZ Gundam** — mission Entry character/pilot field: Judau Ashta

**Enemy deployments (inferred):**
  - **Dom** — mission Entry character/pilot field: Neo Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Gaza-C** — mission Entry character/pilot field: Neo Zeon Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Qubeley Mk-II (Ple)** — mission Entry character/pilot field: Elpeo Ple
  - **Zaku III (Rakan)** — mission Entry character/pilot field: Rakan Dahkaran

**Scripted units — side not established:**
  - **Brocken/Machine Cannon** — mission Entry character/pilot field: Federation Soldier
  - **Brocken/Melee** — mission Entry character/pilot field: Federation Soldier

### Episode 15 — Episode 15 Rise of Neo Zeon (`DL415_11`)

**Source:** `eventP04.EDAT/DL415_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Dreissen** — mission Entry character/pilot field: Neo Zeon Soldier — ×7 source Entry IDs (simultaneous count not verified)
  - **Endra** — mission Entry character/pilot field: Neo Zeon Officer
  - **Gaza-C** — mission Entry character/pilot field: Neo Zeon Soldier — ×9 source Entry IDs (simultaneous count not verified)
  - **Kampfer/Bazooka** — mission Entry character/pilot field: Neo Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Qubeley** — mission Entry character/pilot field: Haman Karn
  - **Sadalahn** — mission Entry character/pilot field: Neo Zeon Officer
  - **Zaku II Kai** — mission Entry character/pilot field: Neo Zeon Soldier — ×5 source Entry IDs (simultaneous count not verified)

### Episode 15 — Episode 15 Axis Impact (`DL415_12`)

**Source:** `eventP04.EDAT/DL415_12_Entry.dat`
**Mission-note conditions:**
> The mothership changes partway through. First Turner, then White Base.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Dreissen** — mission Entry character/pilot field: Neo Zeon Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Endra** — mission Entry character/pilot field: Neo Zeon Officer
  - **Endra** — mission Entry character/pilot field: Rakan Dahkaran
  - **Gaza-C** — mission Entry character/pilot field: Neo Zeon Soldier — ×11 source Entry IDs (simultaneous count not verified)
  - **Gaza-C/MA** — mission Entry character/pilot field: Neo Zeon Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Gelgoog** — mission Entry character/pilot field: Neo Zeon Soldier — ×3 source Entry IDs (simultaneous count not verified)
  - **Qubeley Mk-II (Ple Two)** — mission Entry character/pilot field: Ple Two
  - **Rick Dom** — mission Entry character/pilot field: Neo Zeon Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Zaku III (Rakan)** — mission Entry character/pilot field: Rakan Dahkaran

### Episode 15 — Battle of the Burning Sands (`DL415_20`)

**Source:** `eventP04.EDAT/DL415_20_Entry.dat`
**Mission-note conditions:**
> NT-1 Alex must sortie as GR, but Zaku II Kai cannot be deployed.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Directional Mine** — mission Entry character/pilot field: Control AI — ×12 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Dom** — mission Entry character/pilot field: Zeon Soldier — ×10 source Entry IDs (simultaneous count not verified)
  - **Dopp** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Dreissen** — mission Entry character/pilot field: Desert Rommel
  - **Gaza-C/MA** — mission Entry character/pilot field: Neo Zeon Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Gouf** — mission Entry character/pilot field: Acous
  - **Gouf** — mission Entry character/pilot field: Cozun Graham
  - **Gouf (Ramba Ral)** — mission Entry character/pilot field: Ramba Ral
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Zeon Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Zanzibar** — mission Entry character/pilot field: Crowley Hamon

### Episode 15 — Wings Called Freedom (`DL415_30`)

**Source:** `eventP04.EDAT/DL415_30_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Strike Freedom Gundam** — mission Entry character/pilot field: Kira Yamato
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Bigro** — mission Entry character/pilot field: Tokwan
  - **Dreissen** — mission Entry character/pilot field: Neo Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Endra** — mission Entry character/pilot field: Neo Zeon Officer
  - **Gaza-C** — mission Entry character/pilot field: Neo Zeon Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Gaza-C/MA** — mission Entry character/pilot field: Neo Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Qubeley Mk-II (Ple Two)** — mission Entry character/pilot field: Ple Two
  - **Rick Dom** — mission Entry character/pilot field: Zeon Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Zaku III (Rakan)** — mission Entry character/pilot field: Rakan Dahkaran
  - **Zanzibar** — mission Entry character/pilot field: M'Quve

### Episode 15 — Destiny (`DL415_40`)

**Source:** `eventP04.EDAT/DL415_40_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Destiny Gundam** — mission Entry character/pilot field: Shinn Asuka
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Infinite Justice Gundam** — mission Entry character/pilot field: Athrun Zala
  - **Shin Getter-1 (Go)** — mission Entry character/pilot field: Go — unit-list default character/crew refs (not mission-confirmed): Go, Kei, Gai
  - **Strike Freedom Gundam** — mission Entry character/pilot field: Kira Yamato

**Enemy deployments (inferred):**
  - **Invader/Air** — mission Entry character/pilot field: Invader — ×6 source Entry IDs (simultaneous count not verified)
  - **Invader/Ground** — mission Entry character/pilot field: Invader — ×8 source Entry IDs (simultaneous count not verified)
  - **Metal Beast/Missile** — mission Entry character/pilot field: Invader — ×4 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Metal Beast/Shell** — mission Entry character/pilot field: Invader

### Episode 15 — Return of the Goburiki Army (`DL415_60`)

**Source:** `eventP26.EDAT/DL415_60_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Dunbine** — mission Entry character/pilot field: Show Zama — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Show Zama, Chum Huau
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Hulk Gunship Axe Bomber** — mission Entry character/pilot field: Cocoa Arara — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Cocoa Arara, Milk Arara, Cafe au Lait Arara
  - **King Squasher** — mission Entry character/pilot field: Hero Lamuness (Lamune Baba) — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Hero Lamuness (Lamune Baba), Tama-Q
  - **Ryu Knight Zephyr/Later** — mission Entry character/pilot field: Adeu Waltham
  - **Ryu Mage Magidora** — mission Entry character/pilot field: Paffy Pafuricia — unit-list default character/crew refs (not mission-confirmed): Paffy Pafuricia, Hagu Hagu
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus
  - **Monskar Medessa** — mission Entry character/pilot field: Monskar — ×6 source Entry IDs (simultaneous count not verified)
  - **Monskar Neppoon** — mission Entry character/pilot field: Monskar — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×8 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Zwarth** — mission Entry character/pilot field: Black Knight

### Episode 15 — Those Who Seek the Demon God's Return (`DL415_70`)

**Source:** `eventP04.EDAT/DL415_70_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Dark Dragon Soldier** — mission Entry character/pilot field: Dark Dragon Soldier — ×7 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Flying** — mission Entry character/pilot field: Dark Dragon Soldier — ×7 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Sniper** — mission Entry character/pilot field: Dark Dragon Soldier — ×5 source Entry IDs (simultaneous count not verified)
  - **Monskar Medessa** — mission Entry character/pilot field: Monskar — ×4 source Entry IDs (simultaneous count not verified)
  - **Monskar Neppoon** — mission Entry character/pilot field: Monskar — ×4 source Entry IDs (simultaneous count not verified)

### Episode 16 — Episode 16 Assault of the Goburiki Army (`DL416_11`)

**Source:** `eventP04.EDAT/DL416_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Hulk Gunship Axe Bomber** — mission Entry character/pilot field: Cocoa Arara — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Cocoa Arara, Milk Arara, Cafe au Lait Arara
  - **King Squasher** — mission Entry character/pilot field: Hero Lamuness (Lamune Baba) — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Hero Lamuness (Lamune Baba), Tama-Q
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Dark Dragon Escort Ship** — mission Entry character/pilot field: Dark Dragon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier** — mission Entry character/pilot field: Dark Dragon Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Flying** — mission Entry character/pilot field: Dark Dragon Soldier — ×10 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Sniper** — mission Entry character/pilot field: Dark Dragon Soldier — ×7 source Entry IDs (simultaneous count not verified)
  - **Monskar Medessa** — mission Entry character/pilot field: Monskar — ×2 source Entry IDs (simultaneous count not verified)
  - **Monskar Neppoon** — mission Entry character/pilot field: Monskar — ×2 source Entry IDs (simultaneous count not verified)
  - **Queen Cideron** — mission Entry character/pilot field: Da Cider

### Episode 16 — Episode 16 Aura Power Run Amok (`DL416_12`)

**Source:** `eventP04.EDAT/DL416_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Benthos Cruiser α** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Monskar Medessa** — mission Entry character/pilot field: Monskar — ×4 source Entry IDs (simultaneous count not verified)
  - **Monskar Neppoon** — mission Entry character/pilot field: Monskar — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×8 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Zwarth** — mission Entry character/pilot field: Black Knight
  - **Zwarth/Hyper** — mission Entry character/pilot field: Black Knight

### Episode 16 — The Day of Departure (`DL416_30`)

**Source:** `eventP04.EDAT/DL416_30_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Blade Liger** — mission Entry character/pilot field: Van Flyheight — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette
  - **Dibison** — mission Entry character/pilot field: Thomas Richard Schubaltz — alternate Entry ID record present
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Lightning Saix** — mission Entry character/pilot field: Irvine — alternate Entry ID record present
  - **Murasame Liger** — mission Entry character/pilot field: Ruuji Familon
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)

### Episode 16 — The Galeade Front (`DL416_45`)

**Source:** `eventP04.EDAT/DL416_45_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Scopedog TC/ISS (Barcoff)** — mission Entry character/pilot field: Nor Barcoff
  - **Scopedog TC/ISS (Chirico)** — mission Entry character/pilot field: Chirico Cuvie
  - **Scopedog TC/ISS (Godan)** — mission Entry character/pilot field: Gary Godan
  - **Scopedog TC/ISS (Kochak)** — mission Entry character/pilot field: Dare Kochak
  - **Scopedog TC/ISS (Zaki)** — mission Entry character/pilot field: Gerenborash Droka Zaki

**Enemy deployments (inferred):**
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Fatty (Ground)** — mission Entry character/pilot field: Balarant Soldier — ×12 source Entry IDs (simultaneous count not verified)

### Episode 16 — Rescue on Galeade (`DL416_55`)

**Source:** `eventP04.EDAT/DL416_55_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Scopedog RSC (Byman)** — mission Entry character/pilot field: Byman Hagard
  - **Scopedog RSC (Gregore)** — mission Entry character/pilot field: Gregore Garosh
  - **Scopedog RSC (Murza)** — mission Entry character/pilot field: Murza Melym
  - **Scopedog TC/ISS (Barcoff)** — mission Entry character/pilot field: Nor Barcoff
  - **Scopedog TC/ISS (Chirico)** — mission Entry character/pilot field: Chirico Cuvie
  - **Scopedog TC/ISS (Godan)** — mission Entry character/pilot field: Gary Godan
  - **Scopedog TC/ISS (Kochak)** — mission Entry character/pilot field: Dare Kochak
  - **Scopedog TC/ISS (Zaki)** — mission Entry character/pilot field: Gerenborash Droka Zaki
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Balarant Land Battleship** — mission Entry character/pilot field: Balarant Officer
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×8 source Entry IDs (simultaneous count not verified)
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×14 source Entry IDs (simultaneous count not verified)
  - **Fatty (Ground)** — mission Entry character/pilot field: Balarant Soldier — ×58 source Entry IDs (simultaneous count not verified)

### Episode 17 — Episode 17 The Battle for Monad (`DL417_11`)

**Source:** `eventP04.EDAT/DL417_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×10 source Entry IDs (simultaneous count not verified)
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×18 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×9 source Entry IDs (simultaneous count not verified)
  - **Lesrion-class Space Battleship** — mission Entry character/pilot field: Balarant Officer — ×2 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

### Episode 17 — Episode 17 Abnormal Survivor (`DL417_12`)

**Source:** `eventP04.EDAT/DL417_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Scopedog TC/ISS (Barcoff)** — mission Entry character/pilot field: Nor Barcoff
  - **Scopedog TC/ISS (Chirico)** — mission Entry character/pilot field: Chirico Cuvie
  - **Scopedog TC/ISS (Godan)** — mission Entry character/pilot field: Gary Godan
  - **Scopedog TC/ISS (Kochak)** — mission Entry character/pilot field: Dare Kochak — alternate Entry ID record present
  - **Scopedog TC/ISS (Zaki)** — mission Entry character/pilot field: Gerenborash Droka Zaki
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao — alternate Entry ID record present

**Enemy deployments (inferred):**
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×35 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×5 source Entry IDs (simultaneous count not verified)

### Episode 17 — Episode 17 Rescue (`DL417_13`)

**Source:** `eventP04.EDAT/DL417_13_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Dark Knight Steru/Dark Dragon Form** — mission Entry character/pilot field: Galden
  - **Enhanced Layzner** — mission Entry character/pilot field: Albatro Null Eiji Asuka
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Lancelot/Ally** — mission Entry character/pilot field: Suzaku Kururugi
  - **Shin Getter-1 (Ryoma)** — mission Entry character/pilot field: Ryoma Nagare — unit-list default character/crew refs (not mission-confirmed): Ryoma Nagare, Hayato Jin, Benkei Kuruma
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Daljan** — mission Entry character/pilot field: Gosterro — ×2 source Entry IDs (simultaneous count not verified)
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×18 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×8 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present

### Episode 17 — Planet of the Seal (`DL417_30`)

**Source:** `eventP04.EDAT/DL417_30_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Enhanced Layzner** — mission Entry character/pilot field: Albatro Null Eiji Asuka
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×6 source Entry IDs (simultaneous count not verified)
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×16 source Entry IDs (simultaneous count not verified)
  - **Directional Mine** — mission Entry character/pilot field: Control AI — ×4 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×10 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Grados New Giant Space Carrier** — mission Entry character/pilot field: Grados Officer

### Episode 17 — Defend the Warp Gate (`DL417_40`)

**Source:** `eventP05.EDAT/DL417_40_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Ingram Unit 1** — mission Entry character/pilot field: Noa Izumi
  - **Scopedog RSC (Chirico)** — mission Entry character/pilot field: Chirico Cuvie
  - **Scopedog TC/ISS (Barcoff)** — mission Entry character/pilot field: Nor Barcoff

**Enemy deployments (inferred):**
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×14 source Entry IDs (simultaneous count not verified)
  - **Fatty (Ground)** — mission Entry character/pilot field: Balarant Soldier — ×6 source Entry IDs (simultaneous count not verified)

### Episode 17 — The Evolving DG Cells (`DL417_50`)

**Source:** `eventP05.EDAT/DL417_50_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Death Army** — mission Entry character/pilot field: DG Cells — ×6 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Death Bird** — mission Entry character/pilot field: DG Cells — ×6 source Entry IDs (simultaneous count not verified)
  - **Gundam Head** — mission Entry character/pilot field: DG Cells
  - **Mucus Gate S DG** — mission Entry character/pilot field: Mucus — alternate Entry ID record present — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)

### Episode 17 — The Bandits' Misfortune (`DL417_70`)

**Source:** `eventP27.EDAT/DL417_70_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Blade Liger** — mission Entry character/pilot field: Van Flyheight — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette
  - **Gun Sniper (Naomi)** — mission Entry character/pilot field: Naomi Fluegel
  - **Iron Kong Mk-II** — mission Entry character/pilot field: Karl Lichten Schubaltz
  - **Lancelot/Ally** — mission Entry character/pilot field: Suzaku Kururugi
  - **Murasame Liger** — mission Entry character/pilot field: Ruuji Familon

**Enemy deployments (inferred):**
  - **Command Wolf/Khaki** — mission Entry character/pilot field: Zoid Pilot — ×7 source Entry IDs (simultaneous count not verified)
  - **Directional Mine** — mission Entry character/pilot field: Control AI — ×7 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **General-Purpose Turret** — mission Entry character/pilot field: Control AI — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Gun Sniper** — mission Entry character/pilot field: Zoid Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper/WW** — mission Entry character/pilot field: Zoid Pilot — ×7 source Entry IDs (simultaneous count not verified)
  - **Molga** — mission Entry character/pilot field: Zoid Pilot — ×5 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Zoid Pilot — ×8 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Gun Sniper/LS** — mission Entry character/pilot field: Leena Toros — alternate Entry ID record present
  - **Whale King** — mission Entry character/pilot field: Zoid Pilot

### Episode 18 — Episode 18 Overture to Liberation (`DL518_11`)

**Source:** `eventP05.EDAT/DL518_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×8 source Entry IDs (simultaneous count not verified)
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×28 source Entry IDs (simultaneous count not verified)
  - **Directional Mine** — mission Entry character/pilot field: Control AI — ×10 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Grados New Giant Space Carrier** — mission Entry character/pilot field: Grados Officer — ×3 source Entry IDs (simultaneous count not verified)
  - **Ray** — mission Entry character/pilot field: Posaydal Regular Officer

**Scripted units — side not established:**
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech

### Episode 18 — Episode 18 Le Cain's Challenge (`DL518_12`)

**Source:** `eventP05.EDAT/DL518_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Enhanced Layzner** — mission Entry character/pilot field: Albatro Null Eiji Asuka
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×6 source Entry IDs (simultaneous count not verified)
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×12 source Entry IDs (simultaneous count not verified)
  - **Daljan** — mission Entry character/pilot field: Gosterro
  - **Fatty (Ground)** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Zakarl** — mission Entry character/pilot field: Le Cain

### Episode 18 — Valley of Greed (`DL518_20`)

**Source:** `eventP05.EDAT/DL518_20_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Enhanced Layzner** — mission Entry character/pilot field: Albatro Null Eiji Asuka

**Enemy deployments (inferred):**
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×10 source Entry IDs (simultaneous count not verified)
  - **Fatty (Ground)** — mission Entry character/pilot field: Balarant Soldier — ×10 source Entry IDs (simultaneous count not verified)

### Episode 18 — Asteroid Lido (`DL518_35`)

**Source:** `eventP05.EDAT/DL518_35_Entry.dat`
**Mission-note conditions:**
> The sortie units for this mission are fixed. Scopedog appears as an allied NPC.
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Scopedog RSC (Chirico)** — mission Entry character/pilot field: Chirico Cuvie

**Enemy deployments (inferred):**
  - **Scopedog** — mission Entry character/pilot field: Gilgamesh Soldier — ×6 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Scopedog** — mission Entry character/pilot field: Gilgamesh Soldier — ×2 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Scopedog/M** — mission Entry character/pilot field: Gilgamesh Soldier

### Episode 18 — Uoodo (`DL518_40`)

**Source:** `eventP05.EDAT/DL518_40_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Berserga WP** — mission Entry character/pilot field: Ru Shako
  - **Scopedog/Chirico Special** — mission Entry character/pilot field: Chirico Cuvie

**Enemy deployments (inferred):**
  - **Scopedog** — mission Entry character/pilot field: AT Pilot — ×10 source Entry IDs (simultaneous count not verified)
  - **Scopedog/M** — mission Entry character/pilot field: AT Pilot — ×4 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Scopedog** — mission Entry character/pilot field: Gilgamesh Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Scopedog/M** — mission Entry character/pilot field: Gilgamesh Soldier — ×4 source Entry IDs (simultaneous count not verified)

### Episode 18 — Escape (`DL518_50`)

**Source:** `eventP05.EDAT/DL518_50_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **AT Fly** — mission Entry character/pilot field: Vanilla Vartla
  - **Berserga WP** — mission Entry character/pilot field: Ru Shako
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **God Gundam** — mission Entry character/pilot field: Domon Kasshu
  - **Scopedog/Chirico Special** — mission Entry character/pilot field: Chirico Cuvie
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Giga-class Space Battleship** — mission Entry character/pilot field: Gilgamesh Officer
  - **Scopedog** — mission Entry character/pilot field: Gilgamesh Soldier — ×27 source Entry IDs (simultaneous count not verified)
  - **Scopedog/M** — mission Entry character/pilot field: Gilgamesh Soldier — ×18 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Scopedog** — mission Entry character/pilot field: Gilgamesh Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Scopedog/M** — mission Entry character/pilot field: Gilgamesh Soldier — ×2 source Entry IDs (simultaneous count not verified)

### Episode 19 — Ep. 19 Breaking the Axis Defense Line (`DL519_11`)

**Source:** `eventP05.EDAT/DL519_11_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Bigro** — mission Entry character/pilot field: Tokwan
  - **Directional Mine** — mission Entry character/pilot field: Control AI — ×7 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Endra** — mission Entry character/pilot field: Neo Zeon Officer
  - **Gaza-C** — mission Entry character/pilot field: Neo Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Gaza-C/MA** — mission Entry character/pilot field: Neo Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Gelgoog** — mission Entry character/pilot field: Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Rick Dom** — mission Entry character/pilot field: Zeon Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Zanzibar** — mission Entry character/pilot field: Garma Zabi

### Episode 19 — Episode 19 Assault Landing on Axis (`DL519_12`)

**Source:** `eventP05.EDAT/DL519_12_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Gundam Ez8** — mission Entry character/pilot field: Shiro Amada
  - **Gundam Ground Type** — mission Entry character/pilot field: Terry Sanders Jr.
  - **Gundam Ground Type/GM Head** — mission Entry character/pilot field: Karen Joshua
  - **Hover Truck** — mission Entry character/pilot field: Michel Ninorich — unit-list default character/crew refs (not mission-confirmed): Michel Ninorich, Eledore Massis

**Enemy deployments (inferred):**
  - **Directional Mine** — mission Entry character/pilot field: Control AI — ×8 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Dom (Black Tri-Stars)** — mission Entry character/pilot field: Gaia
  - **Dom (Black Tri-Stars)** — mission Entry character/pilot field: Mash
  - **Dom (Black Tri-Stars)** — mission Entry character/pilot field: Ortega
  - **Dreissen** — mission Entry character/pilot field: Desert Rommel
  - **Gouf (Ramba Ral)** — mission Entry character/pilot field: Ramba Ral
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Acous
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Cozun Graham

### Episode 19 — Episode 19 Withdrawal from Axis (`DL519_13`)

**Source:** `eventP05.EDAT/DL519_13_Entry.dat`
**Mission-note conditions:**
> NT-1 Alex must sortie as GR, but Zaku II Kai cannot be deployed.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Dreissen** — mission Entry character/pilot field: Neo Zeon Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Gattle** — mission Entry character/pilot field: Zeon Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Gaza-C** — mission Entry character/pilot field: Neo Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Gaza-C/MA** — mission Entry character/pilot field: Neo Zeon Soldier — ×3 source Entry IDs (simultaneous count not verified)
  - **Gelgoog** — mission Entry character/pilot field: Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Gwazine** — mission Entry character/pilot field: Kycilia Zabi
  - **Kampfer/Bazooka** — mission Entry character/pilot field: Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Rick Dom** — mission Entry character/pilot field: Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Zaku II Kai** — mission Entry character/pilot field: Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Zeong** — mission Entry character/pilot field: Char Aznable

### Episode 19 — Pursuit by the Newtype Corps (`DL519_20`)

**Source:** `eventP05.EDAT/DL519_20_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Dreissen** — mission Entry character/pilot field: Neo Zeon Soldier — ×5 source Entry IDs (simultaneous count not verified)
  - **Endra** — mission Entry character/pilot field: Neo Zeon Officer — ×2 source Entry IDs (simultaneous count not verified)
  - **Gaza-C** — mission Entry character/pilot field: Neo Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Gaza-C/MA** — mission Entry character/pilot field: Neo Zeon Soldier — ×5 source Entry IDs (simultaneous count not verified)
  - **Qubeley** — mission Entry character/pilot field: Haman Karn
  - **Qubeley Mk-II (Ple Two)** — mission Entry character/pilot field: Ple Two
  - **Qubeley Mk-II (Ple)** — mission Entry character/pilot field: Elpeo Ple

### Episode 19 — Mr. Bushido (`DL519_30`)

**Source:** `eventP05.EDAT/DL519_30_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **00 Raiser** — mission Entry character/pilot field: Setsuna F. Seiei — unit-list default character/crew refs (not mission-confirmed): Setsuna F. Seiei, Saji Crossroad
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Gundam Exia** — mission Entry character/pilot field: Setsuna F. Seiei
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao
  - **Wing Gundam Zero** — mission Entry character/pilot field: Heero Yuy

**Enemy deployments (inferred):**
  - **Gelgoog** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Kampfer/Bazooka** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Kampfer/High Mobility** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Susanowo** — mission Entry character/pilot field: Mr. Bushido
  - **Tallgeese** — mission Entry character/pilot field: Zechs Merquise
  - **Zaku II Kai** — mission Entry character/pilot field: Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Zanzibar** — mission Entry character/pilot field: Zeon Officer

**Scripted units — side not established:**
  - **Spaceship** — mission Entry character/pilot field: Saji Crossroad

### Episode 19 — Strike the Enemy Supply Base (`DL519_40`)

**Source:** `eventP05.EDAT/DL519_40_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×6 source Entry IDs (simultaneous count not verified)
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×10 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Lesrion-class Space Battleship** — mission Entry character/pilot field: Balarant Officer

### Episode 19 — Base Suppression (`DL519_50`)

**Source:** `eventP05.EDAT/DL519_50_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Enemy deployments (inferred):**
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×2 source Entry IDs (simultaneous count not verified)
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Fatty (Ground)** — mission Entry character/pilot field: Balarant Soldier — ×8 source Entry IDs (simultaneous count not verified)

### Episode 20 — Episode 20 The 203rd Warp Gate (`DL520_11`)

**Source:** `eventP05.EDAT/DL520_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×8 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)

### Episode 20 — Episode 20 The Sword to Inherit (`DL520_12`)

**Source:** `eventP05.EDAT/DL520_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **God Gundam** — mission Entry character/pilot field: Domon Kasshu — alternate Entry ID record present
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Benthos Carrier α** — mission Entry character/pilot field: Mucus
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×8 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)

### Episode 20 — Episode 20 Planetary Survey (`DL520_13`)

**Source:** `eventP05.EDAT/DL520_13_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate L** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×8 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×8 source Entry IDs (simultaneous count not verified)
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)

### Episode 20 — Resolve Beneath the Mask (`DL520_40`)

**Source:** `eventP05.EDAT/DL520_40_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 3 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **00 Raiser** — mission Entry character/pilot field: Setsuna F. Seiei — unit-list default character/crew refs (not mission-confirmed): Setsuna F. Seiei, Saji Crossroad
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Gundam** — mission Entry character/pilot field: Amuro Ray
  - **Hyaku Shiki** — mission Entry character/pilot field: Quattro Bajeena
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass
  - **Mucus Gate S** — mission Entry character/pilot field: No mission-assigned pilot key — scripted target/object; not a piloted mech
  - **Susanowo/Ally** — mission Entry character/pilot field: Mr. Bushido
  - **Tallgeese/Ally** — mission Entry character/pilot field: Zechs Merquise
  - **Wing Gundam Zero** — mission Entry character/pilot field: Heero Yuy

**Enemy deployments (inferred):**
  - **Invader/Air** — mission Entry character/pilot field: Invader — ×10 source Entry IDs (simultaneous count not verified)
  - **Invader/Starfish** — mission Entry character/pilot field: Invader — ×13 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Susanowo** — mission Entry character/pilot field: Mr. Bushido — alternate Entry ID record present
  - **Tallgeese** — mission Entry character/pilot field: Zechs Merquise — alternate Entry ID record present
  - **Zeong** — mission Entry character/pilot field: Char Aznable — alternate Entry ID record present

### Episode 20 — Trap on the Moon (`DL520_50`)

**Source:** `eventP28.EDAT/DL520_50_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Nu Gundam** — mission Entry character/pilot field: Amuro Ray
  - **Sazabi** — mission Entry character/pilot field: Quattro Bajeena
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Dreissen** — mission Entry character/pilot field: Neo Zeon Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Endra** — mission Entry character/pilot field: Neo Zeon Officer
  - **Gaza-C** — mission Entry character/pilot field: Neo Zeon Soldier — ×10 source Entry IDs (simultaneous count not verified)
  - **Gaza-C/MA** — mission Entry character/pilot field: Neo Zeon Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Gelgoog** — mission Entry character/pilot field: MS Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: --- — ×4 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Qubeley Mk-II (Ple Two)** — mission Entry character/pilot field: Ple Two
  - **Rick Dom** — mission Entry character/pilot field: MS Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Zaku II Kai** — mission Entry character/pilot field: MS Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Zaku III (Rakan)** — mission Entry character/pilot field: Rakan Dahkaran

### Episode 20 — Da Cider the Flash (`DL520_60`)

**Source:** `eventP05.EDAT/DL520_60_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Hulk Gunship Axe Bomber** — mission Entry character/pilot field: Cocoa Arara — unit-list default character/crew refs (not mission-confirmed): Cocoa Arara, Milk Arara, Cafe au Lait Arara
  - **King Squasher** — mission Entry character/pilot field: Hero Lamuness (Lamune Baba) — unit-list default character/crew refs (not mission-confirmed): Hero Lamuness (Lamune Baba), Tama-Q
  - **Queen Cideron/Ally** — mission Entry character/pilot field: Da Cider — unit-list default character/crew refs (not mission-confirmed): Da Cider, Hebi Metako

**Enemy deployments (inferred):**
  - **Dark Dragon Soldier** — mission Entry character/pilot field: Dark Dragon Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Sniper** — mission Entry character/pilot field: Dark Dragon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Monskar Medessa** — mission Entry character/pilot field: Monskar — ×5 source Entry IDs (simultaneous count not verified)
  - **Monskar Neppoon** — mission Entry character/pilot field: Monskar — ×7 source Entry IDs (simultaneous count not verified)
  - **Queen Cideron** — mission Entry character/pilot field: Da Cider

### Episode 21 — Episode 21 The Dark Zwarth (`DL521_11`)

**Source:** `eventP05.EDAT/DL521_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Billbine** — mission Entry character/pilot field: Show Zama — unit-list default character/crew refs (not mission-confirmed): Show Zama, Chum Huau
  - **Dunbine** — mission Entry character/pilot field: Show Zama — unit-list default character/crew refs (not mission-confirmed): Show Zama, Chum Huau
  - **Giga-class Space Battleship** — mission Entry character/pilot field: Gilgamesh Officer — ×2 source Entry IDs (simultaneous count not verified)
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Dark Dragon Escort Ship** — mission Entry character/pilot field: Dark Dragon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Flying** — mission Entry character/pilot field: Dark Dragon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Sniper** — mission Entry character/pilot field: Dark Dragon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Monskar Medessa** — mission Entry character/pilot field: Monskar — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×8 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Zwarth** — mission Entry character/pilot field: Black Knight
  - **Zwarth/Hyper** — mission Entry character/pilot field: Black Knight

### Episode 21 — Episode 21 Goburiki, Ultimate Form (`DL521_12`)

**Source:** `eventP05.EDAT/DL521_12_Entry.dat`
**Mission-note conditions:**
> Demon God Goburiki has special movement.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Hulk Gunship Axe Bomber** — mission Entry character/pilot field: Cocoa Arara — unit-list default character/crew refs (not mission-confirmed): Cocoa Arara, Milk Arara, Cafe au Lait Arara
  - **King Squasher** — mission Entry character/pilot field: Hero Lamuness (Lamune Baba) — unit-list default character/crew refs (not mission-confirmed): Hero Lamuness (Lamune Baba), Tama-Q
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass
  - **Queen Cideron/Ally** — mission Entry character/pilot field: Da Cider — unit-list default character/crew refs (not mission-confirmed): Da Cider, Hebi Metako

**Enemy deployments (inferred):**
  - **Demon God Goburiki/Ultimate** — mission Entry character/pilot field: Don Harumage
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Monskar Medessa** — mission Entry character/pilot field: Monskar — ×14 source Entry IDs (simultaneous count not verified)
  - **Monskar Neppoon** — mission Entry character/pilot field: Monskar — ×18 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech

### Episode 21 — Vanguard of the DG Cells (`DL521_20`)

**Source:** `eventP05.EDAT/DL521_20_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Qubeley Mk-II (Ple, Ally)** — mission Entry character/pilot field: Elpeo Ple
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Death Army** — mission Entry character/pilot field: DG Cells — ×16 source Entry IDs (simultaneous count not verified)
  - **Death Bird** — mission Entry character/pilot field: DG Cells — ×34 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate M DG** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Mucus Gate S DG** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)

### Episode 21 — DG Asteroid Approaching (`DL521_40`)

**Source:** `eventP06.EDAT/DL521_40_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **God Gundam** — mission Entry character/pilot field: Domon Kasshu

**Enemy deployments (inferred):**
  - **Death Army** — mission Entry character/pilot field: DG Cells — ×10 source Entry IDs (simultaneous count not verified)
  - **Death Bird** — mission Entry character/pilot field: DG Cells — ×5 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate S DG** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech

### Episode 21 — A New Knightmare Frame (`DL521_70`)

**Source:** `eventP29.EDAT/DL521_70_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Guren S.E.I.T.E.N.** — mission Entry character/pilot field: Kallen Kozuki
  - **Lancelot Albion** — mission Entry character/pilot field: Suzaku Kururugi
  - **Shinkiro** — mission Entry character/pilot field: Zero

**Enemy deployments (inferred):**
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)

### Episode 22 — Episode 22 Showdown, DG Cells R1 (`DL622_11`)

**Source:** `eventP06.EDAT/DL622_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Benthos Cruiser α** — mission Entry character/pilot field: Mucus
  - **Death Army** — mission Entry character/pilot field: DG Cells — ×8 source Entry IDs (simultaneous count not verified)
  - **Death Bird** — mission Entry character/pilot field: DG Cells — ×15 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus

### Episode 22 — Episode 22 Showdown, DG Cells R2 (`DL622_12`)

**Source:** `eventP06.EDAT/DL622_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Death Army** — mission Entry character/pilot field: DG Cells — ×8 source Entry IDs (simultaneous count not verified)
  - **Death Bird** — mission Entry character/pilot field: DG Cells — ×12 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate L DG** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech

### Episode 22 — Episode 22 Devil Gundam - Final Round (`DL622_13`)

**Source:** `eventP06.EDAT/DL622_13_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **God Gundam** — mission Entry character/pilot field: Domon Kasshu
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Death Army** — mission Entry character/pilot field: DG Cells — ×6 source Entry IDs (simultaneous count not verified)
  - **Death Bird** — mission Entry character/pilot field: DG Cells — ×6 source Entry IDs (simultaneous count not verified)
  - **Devil Gundam** — mission Entry character/pilot field: DG Cells
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Gundam Head** — mission Entry character/pilot field: DG Cells — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech

### Episode 22 — God Keron Is Here! (`DL622_30`)

**Source:** `eventP06.EDAT/DL622_30_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Blade Liger** — mission Entry character/pilot field: Van Flyheight — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette
  - **Dibison** — mission Entry character/pilot field: Thomas Richard Schubaltz
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **God Keron** — mission Entry character/pilot field: Sgt. Keroro — unit-list default character/crew refs (not mission-confirmed): Sgt. Keroro, Cpl. Giroro, Pvt. Tamama, Sgt. Major Kululu, Lance Cpl. Dororo
  - **Keroro Robo Mk-II** — mission Entry character/pilot field: Sgt. Keroro
  - **Lightning Saix** — mission Entry character/pilot field: Irvine
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate M** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×7 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×7 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified)
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified)

### Episode 22 — Eldran's Heroes Assemble! (`DL622_50`)

**Source:** `eventP06.EDAT/DL622_50_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Ganbaruger** — mission Entry character/pilot field: Kotaro Kirigakure — unit-list default character/crew refs (not mission-confirmed): Kotaro Kirigakure, Yosuke Kazamatsuri, Rikiya Ryuzaki
  - **Go-Saurer** — mission Entry character/pilot field: Kenichi Minezaki — unit-list default character/crew refs (not mission-confirmed): Kenichi Minezaki, Hiromi Tachibana, Shinobu Asaoka, Taro Shirogane, Yoji Hiyama
  - **Perfect Daiteioh** — mission Entry character/pilot field: Taro Omomo — unit-list default character/crew refs (not mission-confirmed): Taro Omomo, Mai Ozora, Kakeru Daichi, Hiryu Tsukishiro
  - **Raijin-Oh** — mission Entry character/pilot field: Jin Hyuga — unit-list default character/crew refs (not mission-confirmed): Jin Hyuga, Asuka Tsukishiro, Koji Hoshiyama

**Enemy deployments (inferred):**
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×7 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate L MC** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)

### Episode 22 — Colony Laser Reactivated (`DL622_60`)

**Source:** `eventP06.EDAT/DL622_60_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Directional Mine** — mission Entry character/pilot field: Control AI — ×6 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Gattle** — mission Entry character/pilot field: Zeon Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Gelgoog** — mission Entry character/pilot field: Zeon Soldier — ×12 source Entry IDs (simultaneous count not verified)
  - **Gwazine** — mission Entry character/pilot field: Conscon
  - **Kampfer/Bazooka** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Kampfer/High Mobility** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Musai** — mission Entry character/pilot field: Zeon Officer — ×2 source Entry IDs (simultaneous count not verified)
  - **Rick Dom (Black Tri-Stars)** — mission Entry character/pilot field: Gaia
  - **Rick Dom (Black Tri-Stars)** — mission Entry character/pilot field: Mash
  - **Rick Dom (Black Tri-Stars)** — mission Entry character/pilot field: Ortega
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Zeon Soldier — ×6 source Entry IDs (simultaneous count not verified)

### Episode 23 — Episode 23 Gihren's Trap (`DL623_11`)

**Source:** `eventP06.EDAT/DL623_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Apsalus III** — mission Entry character/pilot field: Ginias Sahalin
  - **Bigro** — mission Entry character/pilot field: Zeon Soldier
  - **Gattle** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Gelgoog** — mission Entry character/pilot field: Zeon Soldier — ×12 source Entry IDs (simultaneous count not verified)
  - **Gwazine** — mission Entry character/pilot field: Gihren Zabi
  - **Kampfer/Bazooka** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Kampfer/High Mobility** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Musai** — mission Entry character/pilot field: Zeon Officer — ×2 source Entry IDs (simultaneous count not verified)
  - **Rick Dom** — mission Entry character/pilot field: Zeon Soldier — ×14 source Entry IDs (simultaneous count not verified)
  - **Zaku II Kai** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)

### Episode 23 — Episode 23 Haman's Resolve (`DL623_12`)

**Source:** `eventP06.EDAT/DL623_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Big Zam** — mission Entry character/pilot field: Neo Zeon Soldier
  - **Dreissen** — mission Entry character/pilot field: Neo Zeon Soldier — ×10 source Entry IDs (simultaneous count not verified)
  - **Endra** — mission Entry character/pilot field: Neo Zeon Officer — ×2 source Entry IDs (simultaneous count not verified)
  - **Gaza-C** — mission Entry character/pilot field: Neo Zeon Soldier — ×12 source Entry IDs (simultaneous count not verified)
  - **Gaza-C/MA** — mission Entry character/pilot field: Neo Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Qubeley** — mission Entry character/pilot field: Haman Karn
  - **Sadalahn** — mission Entry character/pilot field: Haman Karn
  - **Zaku III** — mission Entry character/pilot field: Neo Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Zaku III (Rakan)** — mission Entry character/pilot field: Rakan Dahkaran

### Episode 23 — Episode 23 The Earth Sphere United (`DL623_13`)

**Source:** `eventP06.EDAT/DL623_13_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Gundam Ez8** — mission Entry character/pilot field: Shiro Amada
  - **Qubeley Mk-II (Ple, Ally)** — mission Entry character/pilot field: Elpeo Ple
  - **ZZ Gundam** — mission Entry character/pilot field: Judau Ashta

**Enemy deployments (inferred):**
  - **Dreissen** — mission Entry character/pilot field: Neo Zeon Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Gaza-C** — mission Entry character/pilot field: Neo Zeon Soldier — ×10 source Entry IDs (simultaneous count not verified)
  - **Kampfer/Bazooka** — mission Entry character/pilot field: Neo Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Qubeley** — mission Entry character/pilot field: Haman Karn
  - **Quin Mantha** — mission Entry character/pilot field: Ple Two
  - **Zaku III** — mission Entry character/pilot field: Neo Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)

### Episode 23 — Joint Front (`DL623_25`)

**Source:** `eventP06.EDAT/DL623_25_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Benthos Cruiser α** — mission Entry character/pilot field: Mucus
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate L** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)

### Episode 23 — Mucus Gate Sweep (`DL623_35`)

**Source:** `eventP06.EDAT/DL623_35_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate L** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×10 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×10 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified)

### Episode 23 — Ominous Signs (`DL623_45`)

**Source:** `eventP06.EDAT/DL623_45_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Final Dancouga** — mission Entry character/pilot field: Shinobu Fujiwara — unit-list default character/crew refs (not mission-confirmed): Shinobu Fujiwara, Sara Yuki, Ryo Shiba, Masato Shikibu, Alan Igor
  - **Mazinger Z** — mission Entry character/pilot field: Koji Kabuto

**Enemy deployments (inferred):**
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×7 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)

### Episode 24 — Episode 24 A Mother's Memory (`DL624_11`)

**Source:** `eventP06.EDAT/DL624_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Benthos Carrier α** — mission Entry character/pilot field: Mucus
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×14 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×8 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×8 source Entry IDs (simultaneous count not verified)

### Episode 24 — Episode 24 Duel with Viral (`DL624_12`)

**Source:** `eventP06.EDAT/DL624_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **GoShogun** — mission Entry character/pilot field: No mission-assigned pilot key — ×6 source Entry IDs (simultaneous count not verified) — unit-list default character/crew refs (not mission-confirmed): Shingo Hojo, Killy Gagley, Remy Shimada
  - **Gurren Lagann (Simon)** — mission Entry character/pilot field: Simon — unit-list default character/crew refs (not mission-confirmed): Simon, Kamina, Yoko, Boota

**Enemy deployments (inferred):**
  - **Enkidu** — mission Entry character/pilot field: Viral
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)

### Episode 24 — Unearthing the Sirbine (`DL624_25`)

**Source:** `eventP30.EDAT/DL624_25_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Gurren Lagann (Simon)** — mission Entry character/pilot field: Simon — unit-list default character/crew refs (not mission-confirmed): Simon, Kamina, Yoko, Boota
  - **Sirbine** — mission Entry character/pilot field: Show Zama — unit-list default character/crew refs (not mission-confirmed): Show Zama, Chum Huau
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Dark Dragon Escort Ship** — mission Entry character/pilot field: Dark Dragon Soldier
  - **Dark Dragon Soldier** — mission Entry character/pilot field: Dark Dragon Soldier — ×10 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Flying** — mission Entry character/pilot field: Dark Dragon Soldier — ×9 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Sniper** — mission Entry character/pilot field: Dark Dragon Soldier — ×6 source Entry IDs (simultaneous count not verified)

### Episode 24 — Metal Knight Invasion (`DL624_35`)

**Source:** `eventP06.EDAT/DL624_35_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Mass-Produced Metal Knight** — mission Entry character/pilot field: Metal Knight — ×6 source Entry IDs (simultaneous count not verified)
  - **Mass-Produced Metal Knight/Heavy** — mission Entry character/pilot field: Metal Knight — ×5 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)

### Episode 24 — Earthtia Ravaged (`DL624_45`)

**Source:** `eventP06.EDAT/DL624_45_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Mass-Produced Metal Knight** — mission Entry character/pilot field: Metal Knight — ×5 source Entry IDs (simultaneous count not verified)
  - **Mass-Produced Metal Knight/Heavy** — mission Entry character/pilot field: Metal Knight — ×4 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech

### Episode 25 — Episode 25 The Defense of Eldgear (`DL625_11`)

**Source:** `eventP06.EDAT/DL625_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Dark Knight Steru/Dark Dragon Form** — mission Entry character/pilot field: Galden
  - **Eldgear Central Tower** — mission Entry character/pilot field: White Dragon — scripted target/object; not a piloted mech
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Dark Dragon Escort Ship** — mission Entry character/pilot field: Dark Dragon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier** — mission Entry character/pilot field: Dark Dragon Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Flying** — mission Entry character/pilot field: Dark Dragon Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Sniper** — mission Entry character/pilot field: Dark Dragon Soldier — ×4 source Entry IDs (simultaneous count not verified)

### Episode 25 — Episode 25 To the Earth Blade (`DL625_12`)

**Source:** `eventP06.EDAT/DL625_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Benthos Cruiser α** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified)
  - **Mass-Produced Metal Knight/Heavy** — mission Entry character/pilot field: Metal Knight — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)

### Episode 25 — Episode 25 The Evil God Drago (`DL625_13`)

**Source:** `eventP06.EDAT/DL625_13_Entry.dat`
**Mission-note conditions:**
> Evil God Drago uses special movement.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Maryu-Oh Dolga** — mission Entry character/pilot field: Ryu Dolk
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Evil God Drago** — mission Entry character/pilot field: Evil God Drago
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×10 source Entry IDs (simultaneous count not verified)
  - **Mass-Produced Metal Knight** — mission Entry character/pilot field: Metal Knight — ×7 source Entry IDs (simultaneous count not verified)
  - **Mass-Produced Metal Knight/Heavy** — mission Entry character/pilot field: Metal Knight — ×15 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate L DR** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×8 source Entry IDs (simultaneous count not verified)

### Episode 25 — Operation: Sleeper Zoid Capture (`DL625_40`)

**Source:** `eventP06.EDAT/DL625_40_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Command Wolf/White** — mission Entry character/pilot field: Zoid Core — ×6 source Entry IDs (simultaneous count not verified)
  - **Dark Horn** — mission Entry character/pilot field: Zoid Core — ×4 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper/WW** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)
  - **Iron Kong** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)
  - **Molga** — mission Entry character/pilot field: Zoid Core — ×10 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate M** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)

### Episode 25 — Giwaza Lowaw (`DL625_45`)

**Source:** `eventP06.EDAT/DL625_45_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Auge** — mission Entry character/pilot field: Nei Moh Han
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×25 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu/Strong** — mission Entry character/pilot field: Hekeler Mauzer
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×10 source Entry IDs (simultaneous count not verified)
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×9 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Sarge Aupus** — mission Entry character/pilot field: Posaydal Regular Officer
  - **Sarge Aupus (Giwaza)** — mission Entry character/pilot field: Giwaza Lowaw

### Episode 25 — The Geno Breaker Returns (`DL625_50`)

**Source:** `eventP06.EDAT/DL625_50_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 2 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Blade Liger** — mission Entry character/pilot field: Van Flyheight — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette
  - **Dibison** — mission Entry character/pilot field: Thomas Richard Schubaltz
  - **Iron Kong Mk-II** — mission Entry character/pilot field: Karl Lichten Schubaltz
  - **Lightning Saix** — mission Entry character/pilot field: Irvine

**Enemy deployments (inferred):**
  - **Command Wolf/Khaki** — mission Entry character/pilot field: Zoid Core — ×4 source Entry IDs (simultaneous count not verified)
  - **Dark Horn** — mission Entry character/pilot field: Zoid Core — ×3 source Entry IDs (simultaneous count not verified)
  - **Geno Breaker** — mission Entry character/pilot field: Raven
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus
  - **Gun Sniper** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper/WW** — mission Entry character/pilot field: Zoid Core
  - **Iron Kong** — mission Entry character/pilot field: Zoid Core — ×3 source Entry IDs (simultaneous count not verified)
  - **Molga** — mission Entry character/pilot field: Zoid Core — ×8 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×8 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Command Wolf/White** — mission Entry character/pilot field: Helic Republic Soldier — ×3 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Iron Kong** — mission Entry character/pilot field: Guylos Imperial Officer
  - **Mucus Gate S** — mission Entry character/pilot field: No mission-assigned pilot key — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech

### Episode 26 — Episode 26 Harbinger of the End (`DL726_11`)

**Source:** `eventP07.EDAT/DL726_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Blade Liger** — mission Entry character/pilot field: Van Flyheight — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette
  - **Dibison** — mission Entry character/pilot field: Thomas Richard Schubaltz
  - **Lightning Saix** — mission Entry character/pilot field: Irvine
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Dark Horn** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)
  - **Death Stinger** — mission Entry character/pilot field: Hiltz
  - **Geno Breaker** — mission Entry character/pilot field: Raven
  - **Gun Sniper** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)
  - **Iron Kong** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)
  - **Molga** — mission Entry character/pilot field: Zoid Core — ×4 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)

### Episode 26 — Episode 26 Fall of the Capital (`DL726_12`)

**Source:** `eventP07.EDAT/DL726_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Dark Horn** — mission Entry character/pilot field: Zoid Core — ×3 source Entry IDs (simultaneous count not verified)
  - **Death Stinger** — mission Entry character/pilot field: Hiltz
  - **Gun Sniper** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)
  - **Iron Kong** — mission Entry character/pilot field: Zoid Core — ×3 source Entry IDs (simultaneous count not verified)
  - **Molga** — mission Entry character/pilot field: Zoid Core — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Zoid Core — ×4 source Entry IDs (simultaneous count not verified)

### Episode 26 — Episode 26 The Ultrasaurus Revived (`DL726_13`)

**Source:** `eventP07.EDAT/DL726_13_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Blade Liger** — mission Entry character/pilot field: Van Flyheight — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette
  - **Dibison** — mission Entry character/pilot field: Thomas Richard Schubaltz
  - **Lightning Saix** — mission Entry character/pilot field: Irvine
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao
  - **Ultrasaurus** — mission Entry character/pilot field: Rob Herman — unit-list default character/crew refs (not mission-confirmed): Rob Herman, Moonbay, Karl Lichten Schubaltz
  - **Ultrasaurus/Inactive** — mission Entry character/pilot field: Rob Herman — unit-list default character/crew refs (not mission-confirmed): Rob Herman, Moonbay, Karl Lichten Schubaltz

**Enemy deployments (inferred):**
  - **Command Wolf/Khaki** — mission Entry character/pilot field: Zoid Core — ×10 source Entry IDs (simultaneous count not verified)
  - **Dark Horn** — mission Entry character/pilot field: Zoid Core — ×9 source Entry IDs (simultaneous count not verified)
  - **Death Stinger** — mission Entry character/pilot field: Hiltz
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper** — mission Entry character/pilot field: Zoid Core — ×5 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper/WW** — mission Entry character/pilot field: Zoid Core — ×5 source Entry IDs (simultaneous count not verified)
  - **Iron Kong** — mission Entry character/pilot field: Zoid Core — ×5 source Entry IDs (simultaneous count not verified)
  - **Molga** — mission Entry character/pilot field: Zoid Core — ×18 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×22 source Entry IDs (simultaneous count not verified)

### Episode 26 — Brush with Death (`DL726_25`)

**Source:** `eventP07.EDAT/DL726_25_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **AT Fly** — mission Entry character/pilot field: Vanilla Vartla
  - **Berserga WP** — mission Entry character/pilot field: Ru Shako
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Scopedog RSC (Byman)** — mission Entry character/pilot field: Byman Hagard
  - **Scopedog RSC (Chirico)** — mission Entry character/pilot field: Chirico Cuvie
  - **Scopedog RSC (Gregore)** — mission Entry character/pilot field: Gregore Garosh
  - **Scopedog RSC (Murza)** — mission Entry character/pilot field: Murza Melym
  - **Scopedog TC/ISS (Barcoff)** — mission Entry character/pilot field: Nor Barcoff
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Fatty (Ground)** — mission Entry character/pilot field: Balarant Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Scopedog** — mission Entry character/pilot field: AT Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Scopedog/M** — mission Entry character/pilot field: AT Pilot — ×2 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Scopedog** — mission Entry character/pilot field: AT Pilot — ×10 source Entry IDs (simultaneous count not verified)
  - **Scopedog/M** — mission Entry character/pilot field: AT Pilot — ×6 source Entry IDs (simultaneous count not verified)

### Episode 26 — Hunting the Mechanization Empire (`DL726_35`)

**Source:** `eventP07.EDAT/DL726_35_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Dark Go-Saurer** — mission Entry character/pilot field: Mechanized Beast — ×3 source Entry IDs (simultaneous count not verified)
  - **Gandoppler** — mission Entry character/pilot field: Mechanized Beast — ×14 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus
  - **Mucus Gate M MC** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×7 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech

### Episode 26 — A Lead on the Mechanization Empire (`DL726_45`)

**Source:** `eventP07.EDAT/DL726_45_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Bolt Robo/Anti-Air** — mission Entry character/pilot field: Mechanized Beast — ×6 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Long-Range** — mission Entry character/pilot field: Mechanized Beast — ×5 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Melee** — mission Entry character/pilot field: Mechanized Beast — ×5 source Entry IDs (simultaneous count not verified)
  - **Dark Go-Saurer** — mission Entry character/pilot field: Mechanized Beast — ×5 source Entry IDs (simultaneous count not verified)
  - **Gandoppler** — mission Entry character/pilot field: Mechanized Beast — ×6 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus
  - **Mucus Gate M MC** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×9 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech

### Episode 27 — Episode 27 Toward Mechanization Castle (`DL727_11`)

**Source:** `eventP07.EDAT/DL727_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Benthos Carrier α** — mission Entry character/pilot field: Mucus
  - **Benthos Cruiser α** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Dark Go-Saurer** — mission Entry character/pilot field: Mechanized Beast — ×4 source Entry IDs (simultaneous count not verified)
  - **Gandoppler** — mission Entry character/pilot field: Mechanized Beast — ×8 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×10 source Entry IDs (simultaneous count not verified)

### Episode 27 — Ep. 27 Terror! The Wrath of Kikaishin (`DL727_12`)

**Source:** `eventP07.EDAT/DL727_12_Entry.dat`
**Mission-note conditions:**
> Kikaishin has special movement.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Go-Saurer** — mission Entry character/pilot field: Kenichi Minezaki — unit-list default character/crew refs (not mission-confirmed): Kenichi Minezaki, Hiromi Tachibana, Shinobu Asaoka, Taro Shirogane, Yoji Hiyama
  - **God Raijin-Oh** — mission Entry character/pilot field: Jin Hyuga — unit-list default character/crew refs (not mission-confirmed): Jin Hyuga, Asuka Tsukishiro, Koji Hoshiyama, Bakuryu-Oh
  - **Great Ganbaruger** — mission Entry character/pilot field: Kotaro Kirigakure — unit-list default character/crew refs (not mission-confirmed): Kotaro Kirigakure, Yosuke Kazamatsuri, Rikiya Ryuzaki
  - **Perfect Daiteioh** — mission Entry character/pilot field: Taro Omomo — unit-list default character/crew refs (not mission-confirmed): Taro Omomo, Mai Ozora, Kakeru Daichi, Hiryu Tsukishiro
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Bolt Robo/Anti-Air** — mission Entry character/pilot field: Mechanized Beast — ×11 source Entry IDs (simultaneous count not verified)
  - **Dark Go-Saurer** — mission Entry character/pilot field: Mechanized Beast — ×10 source Entry IDs (simultaneous count not verified)
  - **Dreissen** — mission Entry character/pilot field: Control AI — ×2 source Entry IDs (simultaneous count not verified)
  - **Gandoppler** — mission Entry character/pilot field: Mechanized Beast — ×12 source Entry IDs (simultaneous count not verified)
  - **Gelgoog** — mission Entry character/pilot field: Control AI — ×2 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **HAL-X10** — mission Entry character/pilot field: Control AI
  - **Helldiver** — mission Entry character/pilot field: Control AI
  - **Kampfer/High Mobility** — mission Entry character/pilot field: Control AI — ×2 source Entry IDs (simultaneous count not verified)
  - **Kikaishin** — mission Entry character/pilot field: Kikaishin
  - **Mucus Gate L MC** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Type-Zero/Enemy** — mission Entry character/pilot field: Control AI

**Scripted units — side not established:**
  - **Mucus Gate S** — mission Entry character/pilot field: No mission-assigned pilot key — scripted target/object; not a piloted mech

### Episode 27 — Quwasan Olibee (`DL727_40`)

**Source:** `eventP07.EDAT/DL727_40_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Auge** — mission Entry character/pilot field: Antoon Randow
  - **Auge** — mission Entry character/pilot field: Nei Moh Han
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×6 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu/Strong** — mission Entry character/pilot field: Hekeler Mauzer
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Sarge Aupus (Nei)** — mission Entry character/pilot field: Posaydal Regular Officer

### Episode 27 — Under the Flag (`DL727_50`)

**Source:** `eventP07.EDAT/DL727_50_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×6 source Entry IDs (simultaneous count not verified)
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×18 source Entry IDs (simultaneous count not verified)
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×14 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×12 source Entry IDs (simultaneous count not verified)
  - **Grados New Giant Space Carrier** — mission Entry character/pilot field: Grados Officer
  - **Lesrion-class Space Battleship** — mission Entry character/pilot field: Balarant Officer

### Episode 27 — Chess Piece (`DL727_60`)

**Source:** `eventP07.EDAT/DL727_60_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Slender Skala** — mission Entry character/pilot field: Gavlet Gablae
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×18 source Entry IDs (simultaneous count not verified)
  - **B-SFTV-AT-105 Zahatt** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Balarant Land Battleship** — mission Entry character/pilot field: Balarant Officer
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×21 source Entry IDs (simultaneous count not verified)
  - **Directional Mine** — mission Entry character/pilot field: Control AI — ×6 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Fatty (Ground)** — mission Entry character/pilot field: Balarant Soldier — ×20 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Grados New Giant Space Carrier** — mission Entry character/pilot field: Grados Officer — ×3 source Entry IDs (simultaneous count not verified)

### Episode 28 — Episode 28 First Attack (`DL728_11`)

**Source:** `eventP07.EDAT/DL728_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Auge** — mission Entry character/pilot field: Nei Moh Han
  - **Bat-Shu** — mission Entry character/pilot field: Antoon Randow
  - **Bat-Shu** — mission Entry character/pilot field: Hekeler Mauzer
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×15 source Entry IDs (simultaneous count not verified)
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Daljan** — mission Entry character/pilot field: Gosterro
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Sarge Aupus (Nei)** — mission Entry character/pilot field: Nei Moh Han

### Episode 28 — Episode 28 Revenge Battle (`DL728_12`)

**Source:** `eventP07.EDAT/DL728_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Auge** — mission Entry character/pilot field: Antoon Randow
  - **Auge** — mission Entry character/pilot field: Nei Moh Han
  - **Auge** — mission Entry character/pilot field: Posaydal Regular — ×4 source Entry IDs (simultaneous count not verified)
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×22 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu/Strong** — mission Entry character/pilot field: Hekeler Mauzer
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Daljan** — mission Entry character/pilot field: Gosterro
  - **Grados New Giant Space Carrier** — mission Entry character/pilot field: Grados Officer
  - **Sarge Aupus (Giwaza)** — mission Entry character/pilot field: Giwaza Lowaw
  - **Zakarl** — mission Entry character/pilot field: Le Cain

### Episode 28 — Episode 28 Dreamers Again (`DL728_13`)

**Source:** `eventP07.EDAT/DL728_13_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **D-Sserd** — mission Entry character/pilot field: Fannaria Amm
  - **L-Gaim Mk-II** — mission Entry character/pilot field: Daba Myroad — unit-list default character/crew refs (not mission-confirmed): Daba Myroad, Lilis Faw
  - **Novel D-Sserd** — mission Entry character/pilot field: Gaw Ha Leccee
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Aug** — mission Entry character/pilot field: True Posaydal
  - **Auge** — mission Entry character/pilot field: Posaydal Regular — ×10 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×12 source Entry IDs (simultaneous count not verified)
  - **Fatty (Ground)** — mission Entry character/pilot field: Balarant Soldier — ×10 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Heart of Lachesis** — mission Entry character/pilot field: ---

**Scripted units — side not established:**
  - **Heart of Lachesis** — mission Entry character/pilot field: ---

### Episode 28 — The Last Red Shoulder (`DL728_20`)

**Source:** `eventP07.EDAT/DL728_20_Entry.dat`
**Mission-note conditions:**
> Units for this mission are preassigned.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Scopedog RSC (Byman)** — mission Entry character/pilot field: Byman Hagard
  - **Scopedog RSC (Chirico)** — mission Entry character/pilot field: Chirico Cuvie
  - **Scopedog RSC (Gregore)** — mission Entry character/pilot field: Gregore Garosh
  - **Scopedog RSC (Murza)** — mission Entry character/pilot field: Murza Melym

**Enemy deployments (inferred):**
  - **Blood Sucker** — mission Entry character/pilot field: Red Shoulder Trooper — ×7 source Entry IDs (simultaneous count not verified)
  - **Scopedog TC-RS** — mission Entry character/pilot field: Red Shoulder Trooper — ×2 source Entry IDs (simultaneous count not verified)
  - **Scopedog TC-RS/M** — mission Entry character/pilot field: Red Shoulder Trooper — ×4 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Mucus Gate S** — mission Entry character/pilot field: Control AI — scripted target/object; not a piloted mech

### Episode 28 — Perfect Soldier (`DL728_30`)

**Source:** `eventP07.EDAT/DL728_30_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Berserga WP** — mission Entry character/pilot field: Ru Shako
  - **Scopedog RSC (Byman)** — mission Entry character/pilot field: Byman Hagard
  - **Scopedog RSC (Chirico)** — mission Entry character/pilot field: Chirico Cuvie
  - **Scopedog RSC (Gregore)** — mission Entry character/pilot field: Gregore Garosh
  - **Scopedog RSC (Murza)** — mission Entry character/pilot field: Murza Melym
  - **Scopedog TC/ISS (Zaki)** — mission Entry character/pilot field: Gerenborash Droka Zaki

**Enemy deployments (inferred):**
  - **Blood Sucker** — mission Entry character/pilot field: Red Shoulder Trooper — ×8 source Entry IDs (simultaneous count not verified)
  - **Blood Sucker (Ypsilon)** — mission Entry character/pilot field: Ypsilon
  - **Scopedog TC-RS** — mission Entry character/pilot field: Red Shoulder Trooper — ×2 source Entry IDs (simultaneous count not verified)
  - **Scopedog TC-RS/M** — mission Entry character/pilot field: Red Shoulder Trooper — ×8 source Entry IDs (simultaneous count not verified)

### Episode 28 — Preparing for the Rematch (`DL728_50`)

**Source:** `eventP07.EDAT/DL728_50_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Ultrasaurus** — mission Entry character/pilot field: Rob Herman — unit-list default character/crew refs (not mission-confirmed): Rob Herman, Moonbay, Karl Lichten Schubaltz

**Enemy deployments (inferred):**
  - **Dark Horn** — mission Entry character/pilot field: Zoid Core — ×3 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper** — mission Entry character/pilot field: Zoid Core — ×3 source Entry IDs (simultaneous count not verified)
  - **Iron Kong** — mission Entry character/pilot field: Zoid Core — ×3 source Entry IDs (simultaneous count not verified)
  - **Molga** — mission Entry character/pilot field: Zoid Core — ×5 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×9 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Zoid Core — ×8 source Entry IDs (simultaneous count not verified)

### Episode 28 — Eve of the Decisive Battle (`DL728_60`)

**Source:** `eventP07.EDAT/DL728_60_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Command Wolf/Khaki** — mission Entry character/pilot field: Zoid Core — ×9 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper/WW** — mission Entry character/pilot field: Zoid Core — ×15 source Entry IDs (simultaneous count not verified)
  - **Iron Kong** — mission Entry character/pilot field: Zoid Core — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Zoid Core — ×18 source Entry IDs (simultaneous count not verified)
  - **Whale King** — mission Entry character/pilot field: Zoid Core

### Episode 29 — Episode 29 Gravity Cannon (`DL729_11`)

**Source:** `eventP07.EDAT/DL729_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Blade Liger** — mission Entry character/pilot field: Van Flyheight — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette
  - **Dibison** — mission Entry character/pilot field: Thomas Richard Schubaltz
  - **Lightning Saix** — mission Entry character/pilot field: Irvine
  - **Murasame Liger** — mission Entry character/pilot field: Ruuji Familon
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao
  - **Ultrasaurus** — mission Entry character/pilot field: Rob Herman — unit-list default character/crew refs (not mission-confirmed): Rob Herman, Moonbay, Karl Lichten Schubaltz

**Enemy deployments (inferred):**
  - **Dark Horn** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)
  - **Death Stinger** — mission Entry character/pilot field: Hiltz
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)
  - **Iron Kong** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Command Wolf/White** — mission Entry character/pilot field: Helic Republic Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech

### Episode 29 — Ep. 29 The Death Stinger's Onslaught (`DL729_12`)

**Source:** `eventP07.EDAT/DL729_12_Entry.dat`
**Mission-note conditions:**
> Death Stinger uses special movement.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Ultrasaurus** — mission Entry character/pilot field: Rob Herman — unit-list default character/crew refs (not mission-confirmed): Rob Herman, Moonbay, Karl Lichten Schubaltz

**Enemy deployments (inferred):**
  - **Command Wolf/Khaki** — mission Entry character/pilot field: Zoid Core — ×4 source Entry IDs (simultaneous count not verified)
  - **Dark Horn** — mission Entry character/pilot field: Zoid Core — ×4 source Entry IDs (simultaneous count not verified)
  - **Death Stinger** — mission Entry character/pilot field: Hiltz
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper** — mission Entry character/pilot field: Zoid Core — ×4 source Entry IDs (simultaneous count not verified)
  - **Iron Kong** — mission Entry character/pilot field: Zoid Core — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech

### Episode 29 — An Invitation from the Void (`DL729_20`)

**Source:** `eventP07.EDAT/DL729_20_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Benthos Carrier α** — mission Entry character/pilot field: Mucus
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Invader/Air** — mission Entry character/pilot field: Invader — ×4 source Entry IDs (simultaneous count not verified)
  - **Invader/Starfish** — mission Entry character/pilot field: Invader — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×8 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine GG** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×12 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Cowen & Stinger** — mission Entry character/pilot field: Cowen & Stinger
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech

### Episode 29 — The Devil in the Crater (`DL729_50`)

**Source:** `eventP07.EDAT/DL729_50_Entry.dat`
**Mission-note conditions:**
> Invader (Devourer Type) uses special movement.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Invader/Air** — mission Entry character/pilot field: Invader — ×5 source Entry IDs (simultaneous count not verified)
  - **Invader/Giant Worm** — mission Entry character/pilot field: Invader
  - **Invader/Ground** — mission Entry character/pilot field: Invader — ×5 source Entry IDs (simultaneous count not verified)
  - **Metal Beast/Missile** — mission Entry character/pilot field: Invader — ×5 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Metal Beast/Shell** — mission Entry character/pilot field: Invader — ×6 source Entry IDs (simultaneous count not verified)

### Episode 30 — Episode 30 Ancient Memories (`DL830_11`)

**Source:** `eventP08.EDAT/DL830_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Blade Liger** — mission Entry character/pilot field: Van Flyheight — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette
  - **Dibison** — mission Entry character/pilot field: Thomas Richard Schubaltz
  - **Lightning Saix** — mission Entry character/pilot field: Irvine
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Command Wolf/Khaki** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)
  - **Dark Horn** — mission Entry character/pilot field: Zoid Core — ×3 source Entry IDs (simultaneous count not verified)
  - **Death Stinger** — mission Entry character/pilot field: Hiltz
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper/WW** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)
  - **Iron Kong** — mission Entry character/pilot field: Zoid Core — ×4 source Entry IDs (simultaneous count not verified)
  - **Molga** — mission Entry character/pilot field: Zoid Core — ×7 source Entry IDs (simultaneous count not verified)
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)

### Episode 30 — Episode 30 Above Eve Polis (`DL830_12`)

**Source:** `eventP08.EDAT/DL830_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Benthos Cruiser α** — mission Entry character/pilot field: Mucus
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine GG** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×9 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Zoid Core — ×24 source Entry IDs (simultaneous count not verified)
  - **Whale King** — mission Entry character/pilot field: Zoid Core

**Scripted units — side not established:**
  - **Whale King** — mission Entry character/pilot field: Guylos Imperial Officer — ×3 source Entry IDs (simultaneous count not verified)

### Episode 30 — Episode 30 Death Saurer, Beast of Ruin (`DL830_13`)

**Source:** `eventP08.EDAT/DL830_13_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Blade Liger** — mission Entry character/pilot field: Van Flyheight — unit-list default character/crew refs (not mission-confirmed): Van Flyheight, Fiona Elisi Linette
  - **Dibison** — mission Entry character/pilot field: Thomas Richard Schubaltz
  - **Geno Breaker/Ally** — mission Entry character/pilot field: Raven
  - **Lightning Saix** — mission Entry character/pilot field: Irvine
  - **Ultrasaurus** — mission Entry character/pilot field: Rob Herman — unit-list default character/crew refs (not mission-confirmed): Rob Herman, Moonbay, Karl Lichten Schubaltz

**Enemy deployments (inferred):**
  - **Dark Horn** — mission Entry character/pilot field: Zoid Core — ×6 source Entry IDs (simultaneous count not verified)
  - **Death Stinger** — mission Entry character/pilot field: Hiltz
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×14 source Entry IDs (simultaneous count not verified)
  - **Iron Kong** — mission Entry character/pilot field: Zoid Core — ×6 source Entry IDs (simultaneous count not verified)
  - **Molga** — mission Entry character/pilot field: Zoid Core — ×4 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate L** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×9 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×10 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine GG** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Original Death Saurer** — mission Entry character/pilot field: Hiltz
  - **Redler** — mission Entry character/pilot field: Zoid Core — ×7 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Mucus Gate L** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Original Death Saurer** — mission Entry character/pilot field: Dark Kaiser

### Episode 30 — Invader Sweep (`DL830_40`)

**Source:** `eventP08.EDAT/DL830_40_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Benthos Cruiser α** — mission Entry character/pilot field: Mucus
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Invader/Air** — mission Entry character/pilot field: Invader — ×3 source Entry IDs (simultaneous count not verified)
  - **Invader/Ground** — mission Entry character/pilot field: Invader — ×3 source Entry IDs (simultaneous count not verified)
  - **Invader/Starfish** — mission Entry character/pilot field: Invader — ×11 source Entry IDs (simultaneous count not verified)
  - **Metal Beast/Missile** — mission Entry character/pilot field: Invader — ×5 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Mucus Gate L IN** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine GG** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)

### Episode 30 — Consensus (`DL830_50`)

**Source:** `eventP08.EDAT/DL830_50_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Benthos Cruiser α** — mission Entry character/pilot field: Mucus
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate L** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×7 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine GG** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified) — alternate Entry ID record present

### Episode 30 — Warp Ring Activation (`DL830_60`)

**Source:** `eventP08.EDAT/DL830_60_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Giga-class Space Battleship** — mission Entry character/pilot field: Gilgamesh Officer
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Benthos Carrier α** — mission Entry character/pilot field: Mucus
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×7 source Entry IDs (simultaneous count not verified)
  - **Invader/Starfish** — mission Entry character/pilot field: Invader — ×17 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine GG** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)

### Episode 31 — Ep. 31 Death Match!! Invader Fortress! (`DL831_11`)

**Source:** `eventP08.EDAT/DL831_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Enemy deployments (inferred):**
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Invader/Air** — mission Entry character/pilot field: Invader — ×2 source Entry IDs (simultaneous count not verified)
  - **Invader/Giant Worm** — mission Entry character/pilot field: Invader — ×2 source Entry IDs (simultaneous count not verified)
  - **Invader/Ground** — mission Entry character/pilot field: Invader — ×2 source Entry IDs (simultaneous count not verified)
  - **Invader/Starfish** — mission Entry character/pilot field: Invader — ×8 source Entry IDs (simultaneous count not verified)
  - **Metal Beast/Missile** — mission Entry character/pilot field: Invader — ×6 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Metal Beast/Shell** — mission Entry character/pilot field: Invader — ×3 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate L IN** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine GG** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Cowen & Stinger** — mission Entry character/pilot field: Cowen & Stinger
  - **Shin Getter-1 (Go)** — mission Entry character/pilot field: Go — unit-list default character/crew refs (not mission-confirmed): Go, Kei, Gai
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao
  - **White Base** — mission Entry character/pilot field: Bright Noa — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

### Episode 31 — Episode 31 Flash!! At Evolution's End! (`DL831_12`)

**Source:** `eventP08.EDAT/DL831_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Shin Getter-1 (Go)** — mission Entry character/pilot field: Go — unit-list default character/crew refs (not mission-confirmed): Go, Kei, Gai
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Cowen & Stinger** — mission Entry character/pilot field: Cowen & Stinger
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Invader/Giant Worm** — mission Entry character/pilot field: Invader — ×2 source Entry IDs (simultaneous count not verified)
  - **Invader/Starfish** — mission Entry character/pilot field: Invader — ×22 source Entry IDs (simultaneous count not verified)
  - **Metal Beast/Missile** — mission Entry character/pilot field: Invader — ×6 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine GG** — mission Entry character/pilot field: Mucus — ×10 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech

### Episode 31 — Sweeping the Warp Gate (`DL831_20`)

**Source:** `eventP08.EDAT/DL831_20_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage

**Enemy deployments (inferred):**
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×14 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×14 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine GG** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)

### Episode 31 — Warriors of the Dark Dragon Realm (`DL831_30`)

**Source:** `eventP08.EDAT/DL831_30_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Dark Dragon Escort Ship** — mission Entry character/pilot field: Dark Dragon Soldier
  - **Dark Dragon Soldier** — mission Entry character/pilot field: Dark Dragon Soldier
  - **Dark Dragon Soldier/Flying** — mission Entry character/pilot field: Dark Dragon Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Sniper** — mission Entry character/pilot field: Dark Dragon Soldier

### Episode 31 — The Ultrasaurus Sets Sail (`DL831_40`)

**Source:** `eventP08.EDAT/DL831_40_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Ultrasaurus** — mission Entry character/pilot field: Rob Herman — unit-list default character/crew refs (not mission-confirmed): Rob Herman, Moonbay, Karl Lichten Schubaltz

**Enemy deployments (inferred):**
  - **Command Wolf/Khaki** — mission Entry character/pilot field: Zoid Core — ×9 source Entry IDs (simultaneous count not verified)
  - **Dark Horn** — mission Entry character/pilot field: Zoid Core — ×3 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper** — mission Entry character/pilot field: Zoid Core — ×6 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper/WW** — mission Entry character/pilot field: Zoid Core — ×4 source Entry IDs (simultaneous count not verified)
  - **Iron Kong** — mission Entry character/pilot field: Zoid Core — ×3 source Entry IDs (simultaneous count not verified)
  - **Molga** — mission Entry character/pilot field: Zoid Core — ×4 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Zoid Core — ×11 source Entry IDs (simultaneous count not verified)

### Episode 32 — Episode 32 The Recoral Galaxy (`DL832_11`)

**Source:** `eventP08.EDAT/DL832_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Benthos Carrier α** — mission Entry character/pilot field: Mucus
  - **Benthos Cruiser α** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×8 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×8 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×14 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×8 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine GG** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)

### Episode 32 — Episode 32 The Mucus Fortress (`DL832_12`)

**Source:** `eventP08.EDAT/DL832_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Benthos Carrier α** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×7 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate L** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine GG** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)

### Episode 32 — Go to Our Allies' Aid (`DL832_30`)

**Source:** `eventP08.EDAT/DL832_30_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Benthos Cruiser α** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×10 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×14 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine GG** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×7 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Sarge Aupus** — mission Entry character/pilot field: Posaydal Regular Officer

### Episode 32 — Ark Ship Transport Operation (`DL832_40`)

**Source:** `eventP08.EDAT/DL832_40_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Ultrasaurus** — mission Entry character/pilot field: Rob Herman — unit-list default character/crew refs (not mission-confirmed): Rob Herman, Moonbay, Karl Lichten Schubaltz

**Enemy deployments (inferred):**
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×9 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×11 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine GG** — mission Entry character/pilot field: Mucus — ×5 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)

### Episode 33 — Episode 33 The Domain of Harmony (`DL833_11`)

**Source:** `eventP08.EDAT/DL833_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass
  - **Vasage** — mission Entry character/pilot field: Vasage — ×2 source Entry IDs (simultaneous count not verified)
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Benthos Carrier β** — mission Entry character/pilot field: Mucus
  - **Giga Nekton β** — mission Entry character/pilot field: Mucus — ×8 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton ββ** — mission Entry character/pilot field: Mucus — ×9 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Vasage** — mission Entry character/pilot field: Vasage — ×5 source Entry IDs (simultaneous count not verified)

### Episode 33 — Episode 33 Gatekeeper (`DL833_12`)

**Source:** `eventP08.EDAT/DL833_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Benthos Carrier β** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton β** — mission Entry character/pilot field: Mucus — ×7 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton ββ** — mission Entry character/pilot field: Mucus — ×12 source Entry IDs (simultaneous count not verified)

### Episode 33 — The Mists of Genesis (`DL833_50`)

**Source:** `eventP08.EDAT/DL833_50_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 3 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Enemy deployments (inferred):**
  - **Benthos Carrier α** — mission Entry character/pilot field: Mucus
  - **Benthos Carrier β** — mission Entry character/pilot field: Mucus
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton β** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton ββ** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×9 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×9 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech
  - **Nekton Mine GG** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Giga-class Space Battleship** — mission Entry character/pilot field: Gilgamesh Officer
  - **Lesrion-class Space Battleship** — mission Entry character/pilot field: Balarant Officer
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao — alternate Entry ID record present
  - **Ultrasaurus** — mission Entry character/pilot field: Rob Herman — unit-list default character/crew refs (not mission-confirmed): Rob Herman, Moonbay, Karl Lichten Schubaltz
  - **White Base** — mission Entry character/pilot field: Bright Noa — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

### Episode 33 — The Infernal Spatial Barrier (`DL833_60`)

**Source:** `eventP08.EDAT/DL833_60_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Ultrasaurus** — mission Entry character/pilot field: Rob Herman — unit-list default character/crew refs (not mission-confirmed): Rob Herman, Moonbay, Karl Lichten Schubaltz

**Enemy deployments (inferred):**
  - **Benthos Carrier β** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton β** — mission Entry character/pilot field: Mucus — ×10 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton ββ** — mission Entry character/pilot field: Mucus — ×7 source Entry IDs (simultaneous count not verified)

### Episode 34 — Episode 34 Into Genesis (`DL834_11`)

**Source:** `eventP08.EDAT/DL834_11_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.
**Alternate-record caution:** 1 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Vasage** — mission Entry character/pilot field: Vasage

**Enemy deployments (inferred):**
  - **Giga Nekton β** — mission Entry character/pilot field: Mucus — ×14 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton ββ** — mission Entry character/pilot field: Mucus — ×7 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×13 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×15 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×7 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine G** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×9 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Giga Nekton β** — mission Entry character/pilot field: Mucus
  - **Giga Nekton ββ** — mission Entry character/pilot field: Mucus
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — ×7 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus
  - **White Base** — mission Entry character/pilot field: Bright Noa — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

### Episode 34 — Episode 34 The Hopes Entrusted (`DL834_12`)

**Source:** `eventP08.EDAT/DL834_12_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Gurren Lagann (Simon)** — mission Entry character/pilot field: Simon — unit-list default character/crew refs (not mission-confirmed): Simon, Kamina, Yoko, Boota
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Benthos Carrier β** — mission Entry character/pilot field: Mucus
  - **Giga Nekton β** — mission Entry character/pilot field: Mucus — ×20 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton ββ** — mission Entry character/pilot field: Mucus — ×16 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×21 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×14 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×10 source Entry IDs (simultaneous count not verified)
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×11 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech

### Episode 34 — Episode 34 Operation Extend (`DL834_13`)

**Source:** `eventP08.EDAT/DL834_13_Entry.dat`
**Mission-note conditions:**
> Mucus Arm uses special movement.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.
**Alternate-record caution:** 3 Entry ID(s) have more than one unit/pilot/side row; bullets marked “alternate Entry ID record present” are not assumed simultaneous.

**Allied deployments (inferred):**
  - **Gurren Lagann (Simon)** — mission Entry character/pilot field: Simon — unit-list default character/crew refs (not mission-confirmed): Simon, Kamina, Yoko, Boota

**Enemy deployments (inferred):**
  - **Giga Nekton β** — mission Entry character/pilot field: Mucus — ×16 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton ββ** — mission Entry character/pilot field: Mucus — ×15 source Entry IDs (simultaneous count not verified)
  - **Mucus Arm** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×12 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×10 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×12 source Entry IDs (simultaneous count not verified)
  - **Nekton Mine GG** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×10 source Entry IDs (simultaneous count not verified)

**Scripted units — side not established:**
  - **Exart** — mission Entry character/pilot field: Seishiro Kusanagi — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Seishiro Kusanagi, Himari Yaegaki, Vasage
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass
  - **Macross Quarter (Storm Attack)** — mission Entry character/pilot field: Jeffrey Wilder — alternate Entry ID record present — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass
  - **Mucus Emperor** — mission Entry character/pilot field: Mucus — alternate Entry ID record present
  - **Mucus Emperor/MAX** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Mucus Gate S** — mission Entry character/pilot field: Mucus — scripted target/object; not a piloted mech

### Simulator — Rogue Machines (`SM001`)

**Source:** `eventP01.EDAT/SM001_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Bolt Robo/Anti-Air** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Long-Range** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Melee** — mission Entry character/pilot field: Mechanized Beast — ×3 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Standard** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Brocken/Melee** — mission Entry character/pilot field: Control AI — ×4 source Entry IDs (simultaneous count not verified)
  - **Gandoppler** — mission Entry character/pilot field: Mechanized Beast — ×3 source Entry IDs (simultaneous count not verified)
  - **HAL-X10/Green** — mission Entry character/pilot field: Shinohara HOS — ×2 source Entry IDs (simultaneous count not verified)
  - **Helldiver** — mission Entry character/pilot field: Control AI — ×4 source Entry IDs (simultaneous count not verified)

### Simulator — Ground Mobile Suit Battle (`SM002`)

**Source:** `eventP01.EDAT/SM002_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Dom** — mission Entry character/pilot field: Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Dopp** — mission Entry character/pilot field: Zeon Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **General-Purpose Turret** — mission Entry character/pilot field: Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Gouf** — mission Entry character/pilot field: Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Zanzibar** — mission Entry character/pilot field: Zeon Officer — ×2 source Entry IDs (simultaneous count not verified)

### Simulator — Armed Groups (`SM003`)

**Source:** `eventP20.EDAT/SM003_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Enemy deployments (inferred):**
  - **Brocken/Cannon** — mission Entry character/pilot field: Labor Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Brocken/Machine Cannon** — mission Entry character/pilot field: Labor Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Brocken/Melee** — mission Entry character/pilot field: Labor Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Dom** — mission Entry character/pilot field: MS Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Gelgoog** — mission Entry character/pilot field: MS Pilot
  - **Gouf** — mission Entry character/pilot field: MS Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Griffon** — mission Entry character/pilot field: Badrinath Harchand
  - **HAL-X10** — mission Entry character/pilot field: Labor Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **HAL-X10/Green** — mission Entry character/pilot field: Shinohara HOS — ×2 source Entry IDs (simultaneous count not verified)
  - **Helldiver** — mission Entry character/pilot field: Control AI — ×4 source Entry IDs (simultaneous count not verified)

### Simulator — Threats from Space (`SM004`)

**Source:** `eventP21.EDAT/SM004_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Bolt Robo/Anti-Air** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Long-Range** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Melee** — mission Entry character/pilot field: Mechanized Beast — ×3 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Standard** — mission Entry character/pilot field: Mechanized Beast — ×3 source Entry IDs (simultaneous count not verified)
  - **Dark Go-Saurer** — mission Entry character/pilot field: Mechanized Beast
  - **Gandoppler** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Invader/Air** — mission Entry character/pilot field: Invader — ×4 source Entry IDs (simultaneous count not verified)
  - **Invader/Ground** — mission Entry character/pilot field: Invader — ×4 source Entry IDs (simultaneous count not verified)
  - **Metal Beast/Missile** — mission Entry character/pilot field: Invader — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Metal Beast/Shell** — mission Entry character/pilot field: Invader — ×2 source Entry IDs (simultaneous count not verified)

### Simulator — Veteran MS Pilots (`SM005`)

**Source:** `eventP22.EDAT/SM005_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Dom (Black Tri-Stars)** — mission Entry character/pilot field: Gaia
  - **Dom (Black Tri-Stars)** — mission Entry character/pilot field: Mash
  - **Dom (Black Tri-Stars)** — mission Entry character/pilot field: Ortega
  - **Dopp** — mission Entry character/pilot field: Zeon Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Gouf (Ramba Ral)** — mission Entry character/pilot field: Ramba Ral
  - **Kampfer/Bazooka** — mission Entry character/pilot field: Mikhail Kaminsky
  - **Kampfer/High Mobility** — mission Entry character/pilot field: Hardy Steiner
  - **Zaku II (Char)** — mission Entry character/pilot field: Char Aznable
  - **Zaku II Kai** — mission Entry character/pilot field: Andy Strauss
  - **Zaku II Kai** — mission Entry character/pilot field: Gabriel Ramirez Garcia
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Cozun Graham
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Slender
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Acous
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Crown
  - **Zanzibar** — mission Entry character/pilot field: Crowley Hamon
  - **Zanzibar** — mission Entry character/pilot field: Garma Zabi
  - **Zanzibar** — mission Entry character/pilot field: M'Quve

### Simulator — Solar System Defense Drill (`SM006`)

**Source:** `eventP23.EDAT/SM006_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Bolt Robo/Anti-Air** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Long-Range** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Melee** — mission Entry character/pilot field: Mechanized Beast — ×3 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Standard** — mission Entry character/pilot field: Mechanized Beast — ×3 source Entry IDs (simultaneous count not verified)
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Daljan** — mission Entry character/pilot field: Gosterro
  - **Dark Go-Saurer** — mission Entry character/pilot field: Mechanized Beast
  - **Gandoppler** — mission Entry character/pilot field: Mechanized Beast — ×4 source Entry IDs (simultaneous count not verified)
  - **Grados New Giant Space Carrier** — mission Entry character/pilot field: Grados Officer
  - **Invader/Air** — mission Entry character/pilot field: Invader — ×3 source Entry IDs (simultaneous count not verified)
  - **Invader/Ground** — mission Entry character/pilot field: Invader — ×3 source Entry IDs (simultaneous count not verified)
  - **Metal Beast/Missile** — mission Entry character/pilot field: Invader — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Metal Beast/Shell** — mission Entry character/pilot field: Invader

### Simulator — The Lawless Galaxy (`SM007`)

**Source:** `eventP24.EDAT/SM007_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×4 source Entry IDs (simultaneous count not verified)
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Escort Ship** — mission Entry character/pilot field: Dark Dragon Soldier
  - **Dark Dragon Soldier** — mission Entry character/pilot field: Dark Dragon Soldier — ×3 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Flying** — mission Entry character/pilot field: Dark Dragon Soldier — ×3 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Sniper** — mission Entry character/pilot field: Dark Dragon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Death Army** — mission Entry character/pilot field: DG Cells — ×4 source Entry IDs (simultaneous count not verified)
  - **Death Bird** — mission Entry character/pilot field: DG Cells — ×4 source Entry IDs (simultaneous count not verified)
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Lesrion-class Space Battleship** — mission Entry character/pilot field: Balarant Officer
  - **Monskar Medessa** — mission Entry character/pilot field: Monskar — ×3 source Entry IDs (simultaneous count not verified)
  - **Monskar Neppoon** — mission Entry character/pilot field: Monskar — ×3 source Entry IDs (simultaneous count not verified)

### Simulator — Mixed AT Unit (`SM008`)

**Source:** `eventP25.EDAT/SM008_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: AT Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Balarant Land Battleship** — mission Entry character/pilot field: Gilgamesh Officer
  - **Brocken/Cannon** — mission Entry character/pilot field: Control AI — ×2 source Entry IDs (simultaneous count not verified)
  - **Brocken/Machine Cannon** — mission Entry character/pilot field: Control AI — ×2 source Entry IDs (simultaneous count not verified)
  - **Chaldea** — mission Entry character/pilot field: Control AI — ×4 source Entry IDs (simultaneous count not verified)
  - **Fatty (Ground)** — mission Entry character/pilot field: AT Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **HAL-X10/Green** — mission Entry character/pilot field: Control AI — ×4 source Entry IDs (simultaneous count not verified)
  - **Helldiver** — mission Entry character/pilot field: Control AI — ×4 source Entry IDs (simultaneous count not verified)
  - **Scopedog** — mission Entry character/pilot field: AT Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Scopedog** — mission Entry character/pilot field: Gilgamesh Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Scopedog RS (Riemann)** — mission Entry character/pilot field: Inge Riemann
  - **Scopedog TC-RS** — mission Entry character/pilot field: Red Shoulder Trooper — ×4 source Entry IDs (simultaneous count not verified)
  - **Scopedog TC-RS/M** — mission Entry character/pilot field: Red Shoulder Trooper — ×2 source Entry IDs (simultaneous count not verified)
  - **Scopedog/M** — mission Entry character/pilot field: AT Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Scopedog/M** — mission Entry character/pilot field: Gilgamesh Soldier — ×2 source Entry IDs (simultaneous count not verified)

### Simulator — Earth's Nightmare (`SM009`)

**Source:** `eventP26.EDAT/SM009_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Bolt Robo/Anti-Air** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Long-Range** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Melee** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Standard** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Chaldea** — mission Entry character/pilot field: Control AI — ×8 source Entry IDs (simultaneous count not verified)
  - **Dark Go-Saurer** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Death Army** — mission Entry character/pilot field: DG Cells — ×2 source Entry IDs (simultaneous count not verified)
  - **Death Bird** — mission Entry character/pilot field: DG Cells — ×2 source Entry IDs (simultaneous count not verified)
  - **Gandoppler** — mission Entry character/pilot field: Mechanized Beast — ×7 source Entry IDs (simultaneous count not verified)
  - **HAL-X10/Green** — mission Entry character/pilot field: Control AI — ×2 source Entry IDs (simultaneous count not verified)
  - **Helldiver** — mission Entry character/pilot field: Control AI — ×2 source Entry IDs (simultaneous count not verified)
  - **Invader/Air** — mission Entry character/pilot field: Invader — ×3 source Entry IDs (simultaneous count not verified)
  - **Invader/Ground** — mission Entry character/pilot field: Invader — ×3 source Entry IDs (simultaneous count not verified)
  - **Mass-Produced Metal Knight** — mission Entry character/pilot field: Metal Knight — ×7 source Entry IDs (simultaneous count not verified)
  - **Mass-Produced Metal Knight/Heavy** — mission Entry character/pilot field: Metal Knight — ×7 source Entry IDs (simultaneous count not verified)
  - **Metal Beast/Missile** — mission Entry character/pilot field: Invader — ×3 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Metal Beast/Shell** — mission Entry character/pilot field: Invader — ×2 source Entry IDs (simultaneous count not verified)

### Simulator — Zoid Legion (`SM010`)

**Source:** `eventP27.EDAT/SM010_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Command Wolf/Khaki** — mission Entry character/pilot field: Zoid Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Dark Horn** — mission Entry character/pilot field: Guylos Imperial Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Death Saurer/Replica** — mission Entry character/pilot field: Gunther Prozen
  - **Geno Breaker** — mission Entry character/pilot field: Raven
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus
  - **Gun Sniper** — mission Entry character/pilot field: Zoid Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper/WW** — mission Entry character/pilot field: Zoid Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Iron Kong** — mission Entry character/pilot field: Guylos Imperial Officer — ×5 source Entry IDs (simultaneous count not verified)
  - **Iron Kong SS** — mission Entry character/pilot field: Karl Lichten Schubaltz
  - **Molga** — mission Entry character/pilot field: Guylos Imperial Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Red Horn (Rosso)** — mission Entry character/pilot field: Rosso
  - **Redler** — mission Entry character/pilot field: Guylos Imperial Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Zoid Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Redler (Viola)** — mission Entry character/pilot field: Viola
  - **Whale King** — mission Entry character/pilot field: Guylos Imperial Officer — ×2 source Entry IDs (simultaneous count not verified)

### Simulator — Multiplying War Machines (`SM011`)

**Source:** `eventP28.EDAT/SM011_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Enemy deployments (inferred):**
  - **Bolt Robo/Long-Range** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Standard** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Brocken/Cannon** — mission Entry character/pilot field: Control AI — ×2 source Entry IDs (simultaneous count not verified)
  - **Brocken/Machine Cannon** — mission Entry character/pilot field: Control AI — ×2 source Entry IDs (simultaneous count not verified)
  - **Chaldea** — mission Entry character/pilot field: Control AI — ×2 source Entry IDs (simultaneous count not verified)
  - **Dark Go-Saurer** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Death Army** — mission Entry character/pilot field: DG Cells — ×16 source Entry IDs (simultaneous count not verified)
  - **Death Bird** — mission Entry character/pilot field: DG Cells — ×2 source Entry IDs (simultaneous count not verified)
  - **Gundam Head** — mission Entry character/pilot field: DG Cells
  - **Invader/Ground** — mission Entry character/pilot field: Invader — ×2 source Entry IDs (simultaneous count not verified)
  - **Mass-Produced Metal Knight** — mission Entry character/pilot field: Metal Knight — ×3 source Entry IDs (simultaneous count not verified)
  - **Mass-Produced Metal Knight/Heavy** — mission Entry character/pilot field: Metal Knight — ×2 source Entry IDs (simultaneous count not verified)
  - **Metal Beast/Missile** — mission Entry character/pilot field: Invader — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Type-Zero/Enemy** — mission Entry character/pilot field: Control AI — ×2 source Entry IDs (simultaneous count not verified)

### Simulator — Heroes of Ground Combat (`SM012`)

**Source:** `eventP29.EDAT/SM012_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Dark Horn** — mission Entry character/pilot field: Guylos Imperial Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Directional Mine** — mission Entry character/pilot field: Control AI — ×8 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Dom (Black Tri-Stars)** — mission Entry character/pilot field: Gaia
  - **Dom (Black Tri-Stars)** — mission Entry character/pilot field: Mash
  - **Dom (Black Tri-Stars)** — mission Entry character/pilot field: Ortega
  - **Dopp** — mission Entry character/pilot field: Zeon Soldier — ×12 source Entry IDs (simultaneous count not verified)
  - **Dreissen** — mission Entry character/pilot field: Desert Rommel
  - **Endra** — mission Entry character/pilot field: Neo Zeon Officer
  - **Gaza-C** — mission Entry character/pilot field: Neo Zeon Soldier — ×3 source Entry IDs (simultaneous count not verified)
  - **Gaza-C/MA** — mission Entry character/pilot field: Neo Zeon Soldier — ×3 source Entry IDs (simultaneous count not verified)
  - **Gouf (Ramba Ral)** — mission Entry character/pilot field: Ramba Ral
  - **Iron Kong SS** — mission Entry character/pilot field: Karl Lichten Schubaltz
  - **Kampfer/Bazooka** — mission Entry character/pilot field: Mikhail Kaminsky
  - **Kampfer/High Mobility** — mission Entry character/pilot field: Hardy Steiner
  - **Lancelot** — mission Entry character/pilot field: Suzaku Kururugi
  - **Molga** — mission Entry character/pilot field: Guylos Imperial Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Red Horn (Rosso)** — mission Entry character/pilot field: Rosso
  - **Redler** — mission Entry character/pilot field: Guylos Imperial Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Redler (Viola)** — mission Entry character/pilot field: Viola
  - **Saber Tiger (Raven)** — mission Entry character/pilot field: Raven
  - **Scopedog RS (Riemann)** — mission Entry character/pilot field: Inge Riemann
  - **Scopedog TC-RS** — mission Entry character/pilot field: Red Shoulder Trooper — ×3 source Entry IDs (simultaneous count not verified)
  - **Scopedog TC-RS/M** — mission Entry character/pilot field: Red Shoulder Trooper — ×2 source Entry IDs (simultaneous count not verified)
  - **Whale King** — mission Entry character/pilot field: Gunther Prozen
  - **Zaku II Kai** — mission Entry character/pilot field: Andy Strauss
  - **Zaku II Kai** — mission Entry character/pilot field: Gabriel Ramirez Garcia
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Cozun Graham
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Acous
  - **Zaku III** — mission Entry character/pilot field: Neo Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Zanzibar** — mission Entry character/pilot field: Crowley Hamon

### Simulator — Mixed Mobile Force (`SM013`)

**Source:** `eventP30.EDAT/SM013_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu** — mission Entry character/pilot field: Posaydal Regular — ×6 source Entry IDs (simultaneous count not verified)
  - **Bat-Shu/Strong** — mission Entry character/pilot field: Gavlet Gablae
  - **Bat-Shu/Strong** — mission Entry character/pilot field: Hatchia Motchia
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×14 source Entry IDs (simultaneous count not verified)
  - **Daljan** — mission Entry character/pilot field: Gosterro
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×9 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Grados New Giant Space Carrier** — mission Entry character/pilot field: Grados Officer
  - **Lesrion-class Space Battleship** — mission Entry character/pilot field: Balarant Officer
  - **Sarge Aupus** — mission Entry character/pilot field: Posaydal Regular Officer
  - **Slender Skala** — mission Entry character/pilot field: Posaydal Regular Officer
  - **Zakarl** — mission Entry character/pilot field: Le Cain

### Simulator — The Stolen Moon (`SM014`)

**Source:** `eventP31.EDAT/SM014_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Dark Dragon Escort Ship** — mission Entry character/pilot field: Dark Dragon Soldier
  - **Dark Dragon Soldier** — mission Entry character/pilot field: Dark Dragon Soldier — ×3 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Flying** — mission Entry character/pilot field: Dark Dragon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Sniper** — mission Entry character/pilot field: Dark Dragon Soldier — ×3 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus
  - **Giga Nekton αα** — mission Entry character/pilot field: Mucus
  - **Invader/Air** — mission Entry character/pilot field: Invader — ×5 source Entry IDs (simultaneous count not verified)
  - **Invader/Ground** — mission Entry character/pilot field: Invader — ×4 source Entry IDs (simultaneous count not verified)
  - **Invader/Starfish** — mission Entry character/pilot field: Invader — ×11 source Entry IDs (simultaneous count not verified)
  - **Metal Beast/Missile** — mission Entry character/pilot field: Invader — ×2 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Metal Beast/Shell** — mission Entry character/pilot field: Invader — ×3 source Entry IDs (simultaneous count not verified)
  - **Monskar Medessa** — mission Entry character/pilot field: Monskar — ×4 source Entry IDs (simultaneous count not verified)
  - **Monskar Neppoon** — mission Entry character/pilot field: Monskar — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Creek** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)
  - **Nekton Hauser** — mission Entry character/pilot field: Mucus — ×4 source Entry IDs (simultaneous count not verified)
  - **Nekton Shooter** — mission Entry character/pilot field: Mucus — ×3 source Entry IDs (simultaneous count not verified)

### Simulator — Anti-Labor, Anti-AT Combat (`SM015`)

**Source:** `eventP31.EDAT/SM015_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Enemy deployments (inferred):**
  - **Brocken/Cannon** — mission Entry character/pilot field: Labor Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Brocken/Machine Cannon** — mission Entry character/pilot field: Labor Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Chaldea** — mission Entry character/pilot field: Control AI — ×11 source Entry IDs (simultaneous count not verified)
  - **Command Wolf/White** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)
  - **Fatty (Ground)** — mission Entry character/pilot field: AT Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Griffon** — mission Entry character/pilot field: Badrinath Harchand
  - **Gun Sniper** — mission Entry character/pilot field: Zoid Core — ×4 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper/WW** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)
  - **HAL-X10** — mission Entry character/pilot field: Shinohara HOS — ×3 source Entry IDs (simultaneous count not verified)
  - **HAL-X10/Green** — mission Entry character/pilot field: Labor Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Helldiver** — mission Entry character/pilot field: Control AI — ×5 source Entry IDs (simultaneous count not verified)
  - **Scopedog** — mission Entry character/pilot field: AT Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Scopedog/M** — mission Entry character/pilot field: AT Pilot — ×3 source Entry IDs (simultaneous count not verified)
  - **Type-Zero/Enemy** — mission Entry character/pilot field: Shinohara HOS — ×4 source Entry IDs (simultaneous count not verified)

### Simulator — Dark Attacker Assault (`SM016`)

**Source:** `eventP31.EDAT/SM016_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Macross Quarter (Fortress Ship)** — mission Entry character/pilot field: Jeffrey Wilder — unit-list default character/crew refs (not mission-confirmed): Jeffrey Wilder, Bobby Margot, Catherine Glass

**Enemy deployments (inferred):**
  - **Bat-Shu/Strong** — mission Entry character/pilot field: Antoon Randow
  - **Bat-Shu/Strong** — mission Entry character/pilot field: Gavlet Gablae
  - **Bat-Shu/Strong** — mission Entry character/pilot field: Hatchia Motchia
  - **Bat-Shu/Strong** — mission Entry character/pilot field: Hekeler Mauzer
  - **Bolt Robo/Anti-Air** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Bolt Robo/Melee** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Dark Go-Saurer** — mission Entry character/pilot field: Mechanized Beast — ×2 source Entry IDs (simultaneous count not verified)
  - **Dreissen** — mission Entry character/pilot field: Neo Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Giga Nekton α** — mission Entry character/pilot field: Mucus — ×2 source Entry IDs (simultaneous count not verified)
  - **Iron Kong** — mission Entry character/pilot field: Zoid Core — ×2 source Entry IDs (simultaneous count not verified)
  - **Monskar Medessa** — mission Entry character/pilot field: Monskar — ×2 source Entry IDs (simultaneous count not verified)
  - **Monskar Neppoon** — mission Entry character/pilot field: Monskar — ×8 source Entry IDs (simultaneous count not verified)
  - **Nekton Assault** — mission Entry character/pilot field: Mucus — ×6 source Entry IDs (simultaneous count not verified)
  - **Qubeley Mk-II (Ple Two)** — mission Entry character/pilot field: Ple Two
  - **Qubeley Mk-II (Ple)** — mission Entry character/pilot field: Elpeo Ple
  - **Queen Cideron** — mission Entry character/pilot field: Da Cider
  - **Saber Tiger (Raven)** — mission Entry character/pilot field: Raven
  - **Susanowo** — mission Entry character/pilot field: Mr. Bushido
  - **Zwarth** — mission Entry character/pilot field: Black Knight

### Simulator — Zeon Ground Intercept Drill (`SM017`)

**Source:** `eventP31.EDAT/SM017_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **Apsalus III** — mission Entry character/pilot field: Ginias Sahalin
  - **Dom** — mission Entry character/pilot field: Zeon Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Dom (Black Tri-Stars)** — mission Entry character/pilot field: Gaia
  - **Dom (Black Tri-Stars)** — mission Entry character/pilot field: Mash
  - **Dom (Black Tri-Stars)** — mission Entry character/pilot field: Ortega
  - **Dopp** — mission Entry character/pilot field: Zeon Soldier — ×12 source Entry IDs (simultaneous count not verified)
  - **Gelgoog** — mission Entry character/pilot field: Crown
  - **Gelgoog** — mission Entry character/pilot field: Slender
  - **Gelgoog** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Gouf** — mission Entry character/pilot field: Acous
  - **Gouf** — mission Entry character/pilot field: Cozun Graham
  - **Gouf** — mission Entry character/pilot field: Zeon Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Gouf (Ramba Ral)** — mission Entry character/pilot field: Ramba Ral
  - **Zaku II/Bazooka** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Zaku II/Machine Gun** — mission Entry character/pilot field: Zeon Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Zanzibar** — mission Entry character/pilot field: Char Aznable
  - **Zanzibar** — mission Entry character/pilot field: Crowley Hamon
  - **Zanzibar** — mission Entry character/pilot field: Garma Zabi
  - **Zanzibar** — mission Entry character/pilot field: M'Quve

### Simulator — Lawless Zone (`SM018`)

**Source:** `eventP32.EDAT/SM018_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **Ultrasaurus** — mission Entry character/pilot field: Rob Herman — unit-list default character/crew refs (not mission-confirmed): Rob Herman, Moonbay, Karl Lichten Schubaltz

**Enemy deployments (inferred):**
  - **Blood Sucker** — mission Entry character/pilot field: Red Shoulder Trooper — ×3 source Entry IDs (simultaneous count not verified)
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×8 source Entry IDs (simultaneous count not verified)
  - **Brocken/Cannon** — mission Entry character/pilot field: Labor Pilot — ×3 source Entry IDs (simultaneous count not verified)
  - **Brocken/Machine Cannon** — mission Entry character/pilot field: Labor Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Command Wolf/Khaki** — mission Entry character/pilot field: Zoid Pilot — ×3 source Entry IDs (simultaneous count not verified)
  - **Daljan** — mission Entry character/pilot field: Gosterro
  - **Dark Horn** — mission Entry character/pilot field: Zoid Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Dom** — mission Entry character/pilot field: MS Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Fatty** — mission Entry character/pilot field: AT Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Fatty (Ground)** — mission Entry character/pilot field: AT Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Gouf** — mission Entry character/pilot field: MS Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Gun Sniper** — mission Entry character/pilot field: Zoid Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Molga** — mission Entry character/pilot field: Zoid Pilot — ×3 source Entry IDs (simultaneous count not verified)
  - **Redler** — mission Entry character/pilot field: Zoid Pilot — ×2 source Entry IDs (simultaneous count not verified)
  - **Scopedog** — mission Entry character/pilot field: AT Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Scopedog TC-RS** — mission Entry character/pilot field: Red Shoulder Trooper — ×4 source Entry IDs (simultaneous count not verified)
  - **Scopedog TC-RS/M** — mission Entry character/pilot field: Red Shoulder Trooper — ×3 source Entry IDs (simultaneous count not verified)
  - **Scopedog/M** — mission Entry character/pilot field: AT Pilot — ×4 source Entry IDs (simultaneous count not verified)
  - **Zaku II Kai** — mission Entry character/pilot field: MS Pilot — ×3 source Entry IDs (simultaneous count not verified)

### Simulator — Zeon Space Intercept Drill (`SM019`)

**Source:** `eventP32.EDAT/SM019_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Allied deployments (inferred):**
  - **White Base** — mission Entry character/pilot field: Bright Noa — unit-list default character/crew refs (not mission-confirmed): Bright Noa, Mirai Yashima

**Enemy deployments (inferred):**
  - **B-FH-14/Dual-Role Fighter** — mission Entry character/pilot field: Balarant Soldier — ×6 source Entry IDs (simultaneous count not verified)
  - **Big Zam** — mission Entry character/pilot field: Dozle Zabi
  - **Bigro** — mission Entry character/pilot field: Tokwan
  - **Braver** — mission Entry character/pilot field: Grados Soldier — ×3 source Entry IDs (simultaneous count not verified)
  - **Dreissen** — mission Entry character/pilot field: Desert Rommel
  - **Dreissen** — mission Entry character/pilot field: Neo Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Endra** — mission Entry character/pilot field: Rakan Dahkaran
  - **Fatty** — mission Entry character/pilot field: Balarant Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Fatty/Anti-Ship** — mission Entry character/pilot field: Balarant Soldier — ×5 source Entry IDs (simultaneous count not verified)
  - **Gattle** — mission Entry character/pilot field: Zeon Soldier — ×4 source Entry IDs (simultaneous count not verified)
  - **Gaza-C** — mission Entry character/pilot field: Neo Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Gaza-C/MA** — mission Entry character/pilot field: Neo Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Gelgoog** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Gwazine** — mission Entry character/pilot field: Gihren Zabi
  - **Kampfer/Bazooka** — mission Entry character/pilot field: Andy Strauss
  - **Kampfer/Bazooka** — mission Entry character/pilot field: Mikhail Kaminsky
  - **Kampfer/High Mobility** — mission Entry character/pilot field: Gabriel Ramirez Garcia
  - **Kampfer/High Mobility** — mission Entry character/pilot field: Hardy Steiner
  - **Qubeley** — mission Entry character/pilot field: Haman Karn
  - **Qubeley Mk-II (Ple Two)** — mission Entry character/pilot field: Ple Two
  - **Qubeley Mk-II (Ple)** — mission Entry character/pilot field: Elpeo Ple
  - **Rick Dom** — mission Entry character/pilot field: Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Rick Dom (Black Tri-Stars)** — mission Entry character/pilot field: Gaia
  - **Rick Dom (Black Tri-Stars)** — mission Entry character/pilot field: Mash
  - **Rick Dom (Black Tri-Stars)** — mission Entry character/pilot field: Ortega
  - **Sadalahn** — mission Entry character/pilot field: Haman Karn
  - **Zaku III** — mission Entry character/pilot field: Neo Zeon Soldier — ×2 source Entry IDs (simultaneous count not verified)
  - **Zaku III (Rakan)** — mission Entry character/pilot field: Rakan Dahkaran
  - **Zeong** — mission Entry character/pilot field: Char Aznable

### Simulator — The Writhing Earth (`SM020`)

**Source:** `eventP32.EDAT/SM020_Entry.dat`
**Mission-note conditions:**
> Invader (Devourer Type) uses special movement.
**Wave/timing:** beyond the specific note above, arrival order and turn timing are unknown.

**Allied deployments (inferred):**
  - **Turner** — mission Entry character/pilot field: Mirawoo Kyao

**Enemy deployments (inferred):**
  - **Dark Dragon Soldier** — mission Entry character/pilot field: Dark Dragon Soldier — ×3 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Flying** — mission Entry character/pilot field: Dark Dragon Soldier — ×3 source Entry IDs (simultaneous count not verified)
  - **Dark Dragon Soldier/Sniper** — mission Entry character/pilot field: Dark Dragon Soldier — ×3 source Entry IDs (simultaneous count not verified)
  - **Death Army** — mission Entry character/pilot field: DG Cells — ×3 source Entry IDs (simultaneous count not verified)
  - **Death Bird** — mission Entry character/pilot field: DG Cells — ×3 source Entry IDs (simultaneous count not verified)
  - **Gandoppler** — mission Entry character/pilot field: Mechanized Beast — ×3 source Entry IDs (simultaneous count not verified)
  - **Invader/Air** — mission Entry character/pilot field: Invader — ×3 source Entry IDs (simultaneous count not verified)
  - **Invader/Giant Worm** — mission Entry character/pilot field: Invader — ×3 source Entry IDs (simultaneous count not verified)
  - **Invader/Ground** — mission Entry character/pilot field: Invader — ×6 source Entry IDs (simultaneous count not verified)
  - **Mass-Produced Metal Knight** — mission Entry character/pilot field: Metal Knight — ×3 source Entry IDs (simultaneous count not verified)
  - **Mass-Produced Metal Knight/Heavy** — mission Entry character/pilot field: Metal Knight — ×3 source Entry IDs (simultaneous count not verified)
  - **Metal Beast/Missile** — mission Entry character/pilot field: Invader — ×6 source Entry IDs (simultaneous count not verified) — scripted target/object; not a piloted mech
  - **Metal Beast/Shell** — mission Entry character/pilot field: Invader — ×2 source Entry IDs (simultaneous count not verified)
  - **Molga** — mission Entry character/pilot field: Zoid Core — ×3 source Entry IDs (simultaneous count not verified)
  - **Monskar Medessa** — mission Entry character/pilot field: Monskar — ×3 source Entry IDs (simultaneous count not verified)
  - **Monskar Neppoon** — mission Entry character/pilot field: Monskar — ×3 source Entry IDs (simultaneous count not verified)

### Simulator — Warring Rivals (`SM021`)

**Source:** `eventP32.EDAT/SM021_Entry.dat`
**Wave/timing:** unknown; not specified in the available mission note or decoded fields.

**Enemy deployments (inferred):**
  - **Aug** — mission Entry character/pilot field: True Posaydal
  - **Auge** — mission Entry character/pilot field: Nei Moh Han
  - **Blood Sucker (Ypsilon)** — mission Entry character/pilot field: Ypsilon
  - **Daljan** — mission Entry character/pilot field: Gosterro
  - **Enkidu** — mission Entry character/pilot field: Viral
  - **Gelgoog (Char)** — mission Entry character/pilot field: Char Aznable
  - **Geno Breaker** — mission Entry character/pilot field: Raven
  - **Gouf (Ramba Ral)** — mission Entry character/pilot field: Ramba Ral
  - **Griffon** — mission Entry character/pilot field: Badrinath Harchand
  - **Iron Kong SS** — mission Entry character/pilot field: Karl Lichten Schubaltz
  - **Lancelot** — mission Entry character/pilot field: Suzaku Kururugi
  - **Qubeley** — mission Entry character/pilot field: Haman Karn
  - **Queen Cideron** — mission Entry character/pilot field: Da Cider
  - **Quin Mantha** — mission Entry character/pilot field: Ple Two
  - **Scopedog RS (Riemann)** — mission Entry character/pilot field: Inge Riemann
  - **Susanowo** — mission Entry character/pilot field: Mr. Bushido
  - **Tallgeese** — mission Entry character/pilot field: Zechs Merquise
  - **Zakarl** — mission Entry character/pilot field: Le Cain
  - **Zaku III (Rakan)** — mission Entry character/pilot field: Rakan Dahkaran
  - **Zwarth/Hyper** — mission Entry character/pilot field: Black Knight

## Excluded map objects / utilities

- **Container:** 184 source records across the scanned package files; excluded from the mech/combat roster as map utility objects.
- **Repair Unit:** 35 source records across the scanned package files; excluded from the mech/combat roster as map utility objects.

## Provenance and interpretation

- Deployment candidates come from the scenario-specific `_Entry.dat` members in the eventP packages, not from the player roster or global unit catalogue alone. Their unit and character keys are resolved against `pakiet_EN/08_names_units_weapons.jsonl` and `pakiet_EN/07_names_characters.jsonl` respectively.
- The single mission-assigned character is read from the third u32 of each 64-byte record; the global default character/crew references are separately read from original `unit_list` records. The latter are contextual metadata only, not a mission assignment.
- Exact same-code duplicates were preserved: `DL103_30` differs between `eventP01.EDAT` and `eventP09.EDAT`; `DL208_30` differs between `eventP13.EDAT` and `eventP22.EDAT`. No version was silently preferred.
- Names use the canonical English unit/character dictionaries. Unavailable timing, trigger semantics, and ambiguous allegiance are left unresolved rather than reconstructed from record order or position.

## Examples in this data

- **White Base** appears with Bright Noa as its mission-assigned character where the entry record names him. Its separate global default unit-list references are Bright Noa and Mirai Yashima; this catalog does not claim Mirai is assigned in every White Base deployment.
- **Exart** mission entries identify Seishiro Kusanagi. Its separate global default references include Seishiro Kusanagi, Himari Yaegaki, and Vasage; those additional refs are not mission-specific assignments.
- **Gundam** entries resolve to Amuro Ray. Zaku II model/weapon variants remain distinct by their canonical unit-display names and are not collapsed into a generic Zaku II.
