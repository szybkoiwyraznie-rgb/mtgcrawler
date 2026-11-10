# Wyjątki długościowe EN — zmierzone, nie deklarowane

Plik generowany przez `tools/measure_en_length_exceptions.py`. Nie edytuj
ręcznie: po zmianie planów w `config/en/` uruchom narzędzie i dołóż
uzasadnienie nowej klasy w `EXCEPTION_CLASSES`.

Reguła z [`EN_PL_PARITY_LEDGER.md`](../EN_PL_PARITY_LEDGER.md): EN ma się
mieścić w szerokości PL-final; jeśli się nie da — w pojemności JP; każde
odstępstwo musi być wypisane. Ten dokument jest tym wypisem.

## Podsumowanie

- wierszy dotkniętych planami portu: **349**
- EN szersze niż **zmierzony limit pola**: **0** (brak)
  → twardy błąd, gdy niepuste; pilnuje tego test
- EN szersze niż **napis japoński**, ale bez zmierzonego limitu pola: **55** (`config_dlc_id` 1, `dialogue` 1, `skill_effect` 47, `sysmes` 6)
- EN szersze niż PL-final, ale **w limicie pola**: **71** (`config_dlc_id` 16, `dialogue` 2, `mission_note` 5, `mission_title` 39, `skill_effect` 1, `spirit_effect` 3, `sysmes` 5)

## EN szersze niż zmierzony limit pola (wymaga decyzji)

Puste = żaden wiersz portu nie przekracza limitu zmierzonego w grze.

_Brak._

## EN szersze niż napis japoński, bez zmierzonego limitu pola

Dla tych klas nie znamy zmierzonej pojemności widgetu — szerokość napisu
japońskiego jest tylko **dolną granicą** (gra mogła pokazywać w polu
tekst dłuższy niż to, co ma japoński odpowiednik). Ryzyko niepotwierdzone:
`runtime_tested` jest `false`. Lista jest kompletna i generowana z danych.

| klasa | plan | slot | EN | kom. EN | kom. JP | nadwyżka |
|---|---|---|---|---|---|---|
| `sysmes` | `clipboard-2026-10-21-en-port.json` | `sysmes:configst.cpk/sysmes.bin:11644` | `＠0Damage ＠230％＠0 reduced` | 19 | 16 | 3 |
| `sysmes` | `clipboard-2026-10-21-en-port.json` | `sysmes:configst.cpk/sysmes.bin:11647` | `Damage ＠230％＠0 reduced` | 19 | 16 | 3 |
| `sysmes` | `clipboard-2026-10-21-en-port.json` | `sysmes:configst.cpk/sysmes.bin:11672` | `＠0Evade bonus ＠230％＠0 up` | 19 | 16 | 3 |
| `sysmes` | `clipboard-2026-10-21-en-port.json` | `sysmes:configst.cpk/sysmes.bin:11675` | `Evade bonus ＠230％＠0 up` | 19 | 16 | 3 |
| `config_dlc_id` | `dlc-download-prompts-2026-11-10.json` | `dlc_id:config06.EDAT/srwDL_DLC_ID06.bin:496` | `Download the add-on\n"Tactical Simulator Alpha".` | 27 | 26 | 1 |
| `dialogue` | `eldran-dialogue-2026-11-10.json` | `dlg:eventP05.EDAT/DL518_12.bin:25080` | `Someone like you, who trusts nobody,\ncould never be the same as Eldran!` | 36 | 32 | 4 |
| `sysmes` | `v26-ui-2026-10-19-en-port.json` | `sysmes:configst.cpk/sysmes.bin:27299` | `Clears:` | 7 | 5 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r117:effect` | `＠4<DG Cells %s1>＠0 Foe %s4 1%s20%% %s10%%` | 25 | 22 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r118:effect` | `＠4<DG Cells %s2>＠0 Foe %s8 1%s25%% %s15%%` | 25 | 22 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r119:effect` | `＠4<DG Cells %s3>＠0 Foe %s12 1%s30%% %s20%%` | 26 | 23 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r120:effect` | `＠4<DG Cells %s4>＠0 Foe %s16 1%s35%% %s25%%` | 26 | 23 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r121:effect` | `＠4<DG Cells %s5>＠0 Foe %s20 1%s40%% %s30%%` | 26 | 23 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r123:effect` | `＠4<Mechanize %s1>＠0 1%s20%% Eva-20%% %s10%%` | 27 | 24 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r124:effect` | `＠4<Mechanize %s2>＠0 1%s25%% Eva-24%% %s15%%` | 27 | 24 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r125:effect` | `＠4<Mechanize %s3>＠0 1%s30%% Eva-28%% %s20%%` | 27 | 24 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r126:effect` | `＠4<Mechanize %s4>＠0 1%s35%% Eva-32%% %s25%%` | 27 | 24 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r127:effect` | `＠4<Mechanize %s5>＠0 1%s40%% Eva-36%% %s30%%` | 27 | 24 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r141:effect` | `＠4<Shock %s1>＠0 %s600 1%s20%% %s30%%` | 20 | 18 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r142:effect` | `＠4<Shock %s2>＠0 %s800 1%s25%% %s35%%` | 20 | 18 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r143:effect` | `＠4<Shock %s3>＠0 %s1000 1%s30%% %s40%%` | 21 | 19 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r144:effect` | `＠4<Shock %s4>＠0 %s1200 1%s35%% %s45%%` | 21 | 19 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r145:effect` | `＠4<Shock %s5>＠0 %s1400 1%s40%% %s50%%` | 21 | 19 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r251:effect` | `＠4<Detonate>＠0 Fixed %s = %s in %s\nUnit lost after use` | 24 | 23 | 1 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r255:effect` | `＠4<Druid System %s1>＠0 1%s20%% Eva-20%%` | 27 | 25 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r256:effect` | `＠4<Druid System %s2>＠0 1%s25%% Eva-22%%` | 27 | 25 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r257:effect` | `＠4<Druid System %s3>＠0 1%s30%% Eva-24%%` | 27 | 25 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r258:effect` | `＠4<Druid System %s4>＠0 1%s35%% Eva-26%%` | 27 | 25 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r259:effect` | `＠4<Druid System %s5>＠0 1%s40%% Eva-28%%` | 27 | 25 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r87:effect` | `＠4<Stun %s1>＠0 Voids counter, %s500 %s30%%` | 30 | 28 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r88:effect` | `＠4<Stun %s2>＠0 Voids counter, %s800 %s40%%` | 30 | 28 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r89:effect` | `＠4<Stun %s3>＠0 Voids counter, %s1100 %s50%%` | 31 | 29 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r90:effect` | `＠4<Stun %s4>＠0 Voids counter, %s1400 %s60%%` | 31 | 29 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:r91:effect` | `＠4<Stun %s5>＠0 Voids counter, %s1700 %s70%%` | 31 | 29 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:18222` | `＠4<Stun %s1>＠0 Voids counter, %s500 %s30%%` | 30 | 28 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:18366` | `＠4<Stun %s2>＠0 Voids counter, %s800 %s40%%` | 30 | 28 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:18510` | `＠4<Stun %s3>＠0 Voids counter, %s1100 %s50%%` | 31 | 29 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:18650` | `＠4<Stun %s4>＠0 Voids counter, %s1400 %s60%%` | 31 | 29 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:18790` | `＠4<Stun %s5>＠0 Voids counter, %s1700 %s70%%` | 31 | 29 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:22556` | `＠4<DG Cells %s1>＠0 Foe %s4 1%s20%% %s10%%` | 25 | 22 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:22704` | `＠4<DG Cells %s2>＠0 Foe %s8 1%s25%% %s15%%` | 25 | 22 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:22852` | `＠4<DG Cells %s3>＠0 Foe %s12 1%s30%% %s20%%` | 26 | 23 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:23004` | `＠4<DG Cells %s4>＠0 Foe %s16 1%s35%% %s25%%` | 26 | 23 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:23156` | `＠4<DG Cells %s5>＠0 Foe %s20 1%s40%% %s30%%` | 26 | 23 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:23460` | `＠4<Mechanize %s1>＠0 1%s20%% Eva-20%% %s10%%` | 27 | 24 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:23616` | `＠4<Mechanize %s2>＠0 1%s25%% Eva-24%% %s15%%` | 27 | 24 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:23772` | `＠4<Mechanize %s3>＠0 1%s30%% Eva-28%% %s20%%` | 27 | 24 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:23928` | `＠4<Mechanize %s4>＠0 1%s35%% Eva-32%% %s25%%` | 27 | 24 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:24084` | `＠4<Mechanize %s5>＠0 1%s40%% Eva-36%% %s30%%` | 27 | 24 | 3 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:26036` | `＠4<Shock %s1>＠0 %s600 1%s20%% %s30%%` | 20 | 18 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:26176` | `＠4<Shock %s2>＠0 %s800 1%s25%% %s35%%` | 20 | 18 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:26316` | `＠4<Shock %s3>＠0 %s1000 1%s30%% %s40%%` | 21 | 19 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:26452` | `＠4<Shock %s4>＠0 %s1200 1%s35%% %s45%%` | 21 | 19 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:26588` | `＠4<Shock %s5>＠0 %s1400 1%s40%% %s50%%` | 21 | 19 | 2 |
| `skill_effect` | `v300-ui-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:41176` | `＠4<Detonate>＠0 Fixed %s = %s in %s\nUnit lost after use` | 24 | 23 | 1 |
| `sysmes` | `v300-ui-2026-10-21-en-port.json` | `sysmes:configst.cpk/sysmes.bin:17096` | `Search for units, parts, abilities,\nskills, Spirit Commands and more.` | 35 | 34 | 1 |

## EN szersze niż PL-final, ale w limicie pola (bez ryzyka)

Tu limitem jest zmierzony slot, jeśli klasa go ma, a w przeciwnym razie
szerokość napisu japońskiego.

| klasa | plan | slot | EN | kom. EN | kom. PL | limit |
|---|---|---|---|---|---|---|
| `config_dlc_id` | `dlc-download-prompts-2026-11-10.json` | `dlc_id:config01.EDAT/srwDL_DLC_ID01.bin:1094` | `Download the Chapter 5 main story.\n＠4You must clear Chapter 4's\nmain story to play this.` | 34 | 31 | 36 |
| `config_dlc_id` | `dlc-download-prompts-2026-11-10.json` | `dlc_id:config01.EDAT/srwDL_DLC_ID01.bin:126` | `Download the Chapter 2 main story.\n＠4You must clear Chapter 1's\nmain story to play this.` | 34 | 31 | 36 |
| `config_dlc_id` | `dlc-download-prompts-2026-11-10.json` | `dlc_id:config01.EDAT/srwDL_DLC_ID01.bin:1422` | `Download the Chapter 6 main story.\n＠4You must clear Chapter 5's\nmain story to play this.` | 34 | 31 | 36 |
| `config_dlc_id` | `dlc-download-prompts-2026-11-10.json` | `dlc_id:config01.EDAT/srwDL_DLC_ID01.bin:1758` | `Download the Chapter 7 main story.\n＠4You must clear Chapter 6's\nmain story to play this.` | 34 | 31 | 36 |
| `config_dlc_id` | `dlc-download-prompts-2026-11-10.json` | `dlc_id:config01.EDAT/srwDL_DLC_ID01.bin:2078` | `Download the Chapter 8 main story.\n＠4You must clear Chapter 7's\nmain story to play this.` | 34 | 31 | 36 |
| `config_dlc_id` | `dlc-download-prompts-2026-11-10.json` | `dlc_id:config01.EDAT/srwDL_DLC_ID01.bin:2416` | `Download the extra mission\n"Lelouch of the Rebellion".\n＠4You may need to progress through\nChapter 1's main story to play it.` | 34 | 27 | 44 |
| `config_dlc_id` | `dlc-download-prompts-2026-11-10.json` | `dlc_id:config01.EDAT/srwDL_DLC_ID01.bin:2786` | `Download the extra mission\n"The White Knight". \n＠4You may need to progress through\nChapter 1's main story to play it.` | 34 | 27 | 44 |
| `config_dlc_id` | `dlc-download-prompts-2026-11-10.json` | `dlc_id:config01.EDAT/srwDL_DLC_ID01.bin:448` | `Download the Chapter 3 main story.\n＠4You must clear Chapter 2's\nmain story to play this.` | 34 | 31 | 36 |
| `config_dlc_id` | `dlc-download-prompts-2026-11-10.json` | `dlc_id:config01.EDAT/srwDL_DLC_ID01.bin:770` | `Download the Chapter 4 main story.\n＠4You must clear Chapter 3's\nmain story to play this.` | 34 | 31 | 36 |
| `config_dlc_id` | `dlc-download-prompts-2026-11-10.json` | `dlc_id:config02.EDAT/srwDL_DLC_ID02.bin:108` | `Download the extra mission\n"Rare Metal Mining". \n＠4You may need to progress through\nChapter 2's main story to play it.` | 34 | 28 | 44 |
| `config_dlc_id` | `dlc-download-prompts-2026-11-10.json` | `dlc_id:config02.EDAT/srwDL_DLC_ID02.bin:484` | `Download the extra mission\n"The 30 Bunch Incident". \n＠4You may need to progress through\nChapter 2's main story to play it.` | 34 | 27 | 44 |
| `config_dlc_id` | `dlc-download-prompts-2026-11-10.json` | `dlc_id:config03.EDAT/srwDL_DLC_ID03.bin:118` | `Download the extra mission\n"Operation: Stop Solar Ray". \n＠4You may need to progress through\nChapter 3's main story to play it.` | 34 | 32 | 44 |
| `config_dlc_id` | `dlc-download-prompts-2026-11-10.json` | `dlc_id:config03.EDAT/srwDL_DLC_ID03.bin:472` | `Download the extra mission\n"The Nighthawk's Dream". \n＠4You may need to progress through\nChapter 3's main story to play it.` | 34 | 27 | 44 |
| `config_dlc_id` | `dlc-download-prompts-2026-11-10.json` | `dlc_id:config05.EDAT/srwDL_DLC_ID05.bin:468` | `Download the extra mission\n"The New Knightmare Frame".\n＠4You may need to progress through\nChapter 5's main story to play it.` | 34 | 27 | 44 |
| `config_dlc_id` | `dlc-download-prompts-2026-11-10.json` | `dlc_id:config05.EDAT/srwDL_DLC_ID05.bin:96` | `Download the extra mission\n"Trap on the Moon". \n＠4You may need to progress through\nChapter 5's main story to play it.` | 34 | 27 | 44 |
| `config_dlc_id` | `dlc-download-prompts-2026-11-10.json` | `dlc_id:config06.EDAT/srwDL_DLC_ID06.bin:108` | `Download the extra mission\n"Unearthing the Sirbine". \n＠4You may need to progress through\nChapter 6's main story to play it.` | 34 | 27 | 44 |
| `skill_effect` | `eldran-2026-10-21-en-port.json` | `skill:config00.cpk/srwDL_Skill00.bin:193328` | `Hint: Eldran robots x` | 21 | 18 | 29 |
| `dialogue` | `eldran-dialogue-2026-11-10.json` | `dlg:eventP05.EDAT/DL518_12.bin:24728` | `I know of it…\nYour own planet is protected by a guardian\ncalled Eldran, is it not?` | 42 | 30 | 44 |
| `dialogue` | `eldran-dialogue-2026-11-10.json` | `dlg:eventP05.EDAT/DL518_12.bin:24984` | `Eldran believed in us and entrusted us\nwith Raijin-Oh to protect the Earth!` | 38 | 35 | 42 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config00.cpk/milstP00.bin:r14:title` | `Ep. 2: Threat Lurking Below` | 27 | 24 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config01.EDAT/milstP01.bin:r10:title` | `Ep. 3-2: The Black Shadow Creeps` | 32 | 28 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config01.EDAT/milstP01.bin:r16:title` | `Ep. 4: Strike the Grados Warship` | 32 | 28 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config02.EDAT/milstP02.bin:r12:title` | `Ep. 7-2: Schubaltz's Offensive` | 30 | 28 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config02.EDAT/milstP02.bin:r13:title` | `Ep. 7-3: Battle for the Capital` | 31 | 24 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config02.EDAT/milstP02.bin:r16:title` | `Self-Proclaimed Black Knight` | 28 | 22 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config02.EDAT/milstP02.bin:r28:title` | `Ep. 9-2: Deathmatch with Riemann` | 32 | 24 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config03.EDAT/milstP03.bin:r1:title` | `Mechanization Empire's Next Move` | 32 | 31 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config03.EDAT/milstP03.bin:r3:title` | `Ep. 10-1: Signs of the Evil God` | 31 | 25 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config03.EDAT/milstP03.bin:r12:title` | `Ep. 11-2: The Door Opens in Dark` | 32 | 31 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config03.EDAT/milstP03.bin:r13:title` | `Ep. 11-3: The Mechanization Den` | 31 | 23 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config03.EDAT/milstP03.bin:r19:title` | `Ep. 12-1: Guardians of Colonies` | 31 | 27 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config03.EDAT/milstP03.bin:r27:title` | `Ep. 13-1: The Young King Returns` | 32 | 29 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config03.EDAT/milstP03.bin:r28:title` | `Ep. 13-2: Imperial Capital Burns` | 32 | 25 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config04.EDAT/milstP04.bin:r1:title` | `Seize the Nuclear Storage Depot` | 31 | 28 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config04.EDAT/milstP04.bin:r19:title` | `Seeking the Demon God's Return` | 30 | 23 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config04.EDAT/milstP04.bin:r22:title` | `Ep. 16-2: Aura Power Run Wild` | 29 | 28 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config05.EDAT/milstP05.bin:r3:title` | `Ep. 18-1: Prelude to Liberation` | 31 | 30 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config05.EDAT/milstP05.bin:r4:title` | `Ep. 18-2: Le Cain's Challenge` | 29 | 27 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config05.EDAT/milstP05.bin:r11:title` | `Ep. 19-1: Breaking Axis Defenses` | 32 | 25 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config05.EDAT/milstP05.bin:r12:title` | `Ep. 19-2: Axis Landing Assault` | 30 | 24 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config05.EDAT/milstP05.bin:r13:title` | `Ep. 19-3: Withdrawal from Axis` | 30 | 23 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config05.EDAT/milstP05.bin:r20:title` | `Ep. 20-1: The 203rd Warp Gate` | 29 | 27 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config05.EDAT/milstP05.bin:r21:title` | `Ep. 20-2: The Sword to Inherit` | 30 | 28 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config05.EDAT/milstP05.bin:r29:title` | `Ep. 21-2: Goburiki Ultimate Form` | 32 | 29 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config06.EDAT/milstP06.bin:r4:title` | `Ep. 22-3: Devil Gundam, Final` | 29 | 28 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config06.EDAT/milstP06.bin:r12:title` | `Ep. 23-3: Uniting Earth Sphere` | 30 | 28 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config06.EDAT/milstP06.bin:r25:title` | `Ep. 25-1: The Defense of Eldgear` | 32 | 24 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config06.EDAT/milstP06.bin:r29:title` | `Capture the Sleeper Zoids` | 25 | 23 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config07.EDAT/milstP07.bin:r2:title` | `Ep. 26-2: Fall of the Capital` | 29 | 24 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config07.EDAT/milstP07.bin:r6:title` | `Search the Mechanization Empire` | 31 | 21 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config07.EDAT/milstP07.bin:r7:title` | `Clues to Mechanization Empire` | 29 | 26 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config07.EDAT/milstP07.bin:r9:title` | `Ep. 27-1: Mechanization Castle` | 30 | 28 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config07.EDAT/milstP07.bin:r10:title` | `Ep. 27-2: Kikaishin's Wrath` | 27 | 26 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config07.EDAT/milstP07.bin:r26:title` | `Ep. 29-2: Death Stinger Strikes` | 31 | 29 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config08.EDAT/milstP08.bin:r2:title` | `Ep. 30-2: Skies over Eve Polis` | 30 | 23 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config08.EDAT/milstP08.bin:r3:title` | `Ep. 30-3: Death Saurer of Ruin` | 30 | 22 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config08.EDAT/milstP08.bin:r10:title` | `Ep. 31-2: Flash!! Evolution End` | 31 | 30 | 32 |
| `mission_title` | `mission-titles-2026-10-24-en-port.json` | `mission_title:config08.EDAT/milstP08.bin:r22:title` | `Ep. 33-1: The Domain of Harmony` | 31 | 25 | 32 |
| `mission_note` | `mission-titles-2026-10-24-en-port.json` | `mission_note:eventP02.EDAT/DL207_30_ext.dat:r0:title` | `Self-Proclaimed Black Knight` | 28 | 22 | 32 |
| `mission_note` | `mission-titles-2026-10-24-en-port.json` | `mission_note:eventP03.EDAT/DL209_60_ext.dat:r0:title` | `Mechanization Empire's Next Move` | 32 | 31 | 32 |
| `mission_note` | `mission-titles-2026-10-24-en-port.json` | `mission_note:eventP04.EDAT/DL313_66_ext.dat:r0:title` | `Seize the Nuclear Storage Depot` | 31 | 28 | 32 |
| `mission_note` | `mission-titles-2026-10-24-en-port.json` | `mission_note:eventP04.EDAT/DL415_70_ext.dat:r0:title` | `Seeking the Demon God's Return` | 30 | 23 | 32 |
| `mission_note` | `mission-titles-2026-10-24-en-port.json` | `mission_note:eventP07.EDAT/DL726_45_ext.dat:r0:title` | `A Lead on Mechanization Empire` | 30 | 26 | 32 |
| `sysmes` | `nondialogue-sysmes-2026-10-26-en-port.json` | `sysmes:configst.cpk/sysmes.bin:43894` | `of\nDownload the full version.` | 26 | 24 | 28 |
| `sysmes` | `nondialogue-sysmes-2026-10-26-en-port.json` | `sysmes:configst.cpk/sysmes.bin:43897` | `Download the full version.` | 26 | 24 | 28 |
| `sysmes` | `nondialogue-sysmes-2026-10-26-en-port.json` | `sysmes:configst.cpk/sysmes.bin:44010` | `of\nDownload the full version.` | 26 | 24 | 28 |
| `sysmes` | `nondialogue-sysmes-2026-10-26-en-port.json` | `sysmes:configst.cpk/sysmes.bin:44013` | `Download the full version.` | 26 | 24 | 28 |
| `sysmes` | `v26-ui-2026-10-19-en-port.json` | `sysmes:configst.cpk/sysmes.bin:27276` | `Missions:` | 9 | 6 | 12 |
| `spirit_effect` | `v270-ui-2026-10-20-en-port.json` | `spirit:configst.cpk/srwDL_Spirit.bin:9412` | `＠6%s1 unit(s)＠0\nLv1%s20%s3 1500 Rec.+HP5%s\nLv2 SP-30 Range4 2500 HP+10％ Rec.\nLv3 SP-40 Range5 3500 HP+15％ Rec.` | 34 | 32 | 35 |
| `spirit_effect` | `v270-ui-2026-10-20-en-port.json` | `spirit:configst.cpk/srwDL_Spirit.bin:9692` | `＠6%s1 unit(s)＠0\nLv1%s20%s3 1500 Rec.+HP5%s\nLv2 SP-30 Range4 2500 HP+10％ Rec.\nLv3 SP-40 Range5 3500 HP+15％ Rec.` | 34 | 32 | 35 |
| `spirit_effect` | `v270-ui-2026-10-20-en-port.json` | `spirit:configst.cpk/srwDL_Spirit.bin:9972` | `＠6%s1 unit(s)＠0\nLv1%s20%s3 1500 Rec.+HP5%s\nLv2 SP-30 Range4 2500 HP+10％ Rec.\nLv3 SP-40 Range5 3500 HP+15％ Rec.` | 34 | 32 | 35 |

## Klasy i uzasadnienia

- **`config_dlc_id`** — Zapowiedź pobierania (pula stringów, tryb `grow`). 1 komórka ponad JP przy nazwie „Tactical Simulator”; JP ma 26 komórek, EN 27. Zostawione: pole jest pulą (realokacja przy zapisie), a pełna nazwa trybu jest nazwą własną z tabeli (alpha/beta). Odnotowane jawnie, nie ukryte.
- **`dialogue`** — Dialog. Limit linii dialogu pilnuje builder (`export_strings.box_limit`); EN mieści się w pojemności JP, a jest szersze od PL-final tylko dlatego, że polski przekład tej linii jest krótszy. To nie odstępstwo od reguły.
- **`mission_note`** — Kopie tytułu misji w `*_ext.dat` (karta misji) — ten sam slot i ta sama decyzja co `mission_title`.
- **`mission_title`** — Tytuły misji w pasku wyboru misji. Decyzja właściciela (2026-11-10, opcja (a)): 32 komórki na linię — slot zmierzony na zrzucie z gry (PL v4.5), szerszy niż najkrótszy japoński tytuł. JP jest tu krótsze, bo japońskie tytuły są zwięzłe; limit wyznacza slot, nie JP.
- **`skill_effect`** — Efekt umiejętności/cechy broni w wierszu tabeli (`rNNN:effect` i jego lustra w puli). Tabele są zawijane wg liczby linii EN od 2026-11-09 (docs/LAMANIE_LINII_TABEL.md); nadwyżka 1-3 komórek wobec napisu jp siedzi w tokenach %sNN%% i tagu <Nazwa> i nie przekracza żadnego zmierzonego progu wiersza. Bez zmierzonego limitu widgetu - runtime_tested: false.
- **`sysmes`** — Krótkie etykiety paska/statusu (sysmes.bin). Część z nich ma własne, węższe powtórzone pole - te pilnuje label_fit i plan portu; nadwyżka wobec napisu jp wynosi tu 1-3 komórki i dotyczy wierszy, których slot nie został zmierzony na zrzucie. Do potwierdzenia w grze, nie do skracania w ciemno.
