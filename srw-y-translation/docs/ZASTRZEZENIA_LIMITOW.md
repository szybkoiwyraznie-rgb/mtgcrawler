# Zastrzeżenia limitów w planie PL2

Pomiar szerokości pól (`data/limits_y.json`, z `tools/s6_limits.py`) pokazuje **25**
miejsc, w których ten sam japoński tekst stoi w grze w dwóch polach o różnej
szerokości, a polski przekład mieści się w szerszym i nie mieści w węższym.
Tekst nie jest tu zmieniany — to lista do decyzji tłumacza, nie błąd importu.

| plik | tabela | klucz | limit | znaków PL | polski tekst |
| --- | --- | --- | --- | --- | --- |
| 02_cytaty_bitewne.md | battle_voice | `01999dca:d020b000` | 28 | 36 | Ja i Aerial będziemy z tobą walczyć! |
| 02_cytaty_bitewne.md | battle_voice | `01999dcb:1b60b000` | 10 | 11 | Tam jesteś! |
| 02_cytaty_bitewne.md | battle_voice | `01999dcb:2760b000` | 10 | 11 | Tam jesteś! |
| 02_cytaty_bitewne.md | battle_voice | `01999dd2:94a0b001` | 20 | 21 | Błysk smoczych kłów!! |
| 02_cytaty_bitewne.md | battle_voice | `01999dd3:2420b000` | 34 | 38 | System obrony przeciwlotniczej, start! |
| 02_cytaty_bitewne.md | battle_voice | `01999dd3:2da0b000` | 24 | 38 | System obrony przeciwlotniczej, start! |
| 02_cytaty_bitewne.md | battle_voice | `01999dd4:a8a0b000` | 35 | 41 | Nie może być…! J-jesteśmy nieśmiertelni!! |
| 02_cytaty_bitewne.md | battle_voice | `01999dd5:19e0b000` | 17 | 19 | Tym to rozstrzygnę! |
| 02_cytaty_bitewne.md | battle_voice | `01999dd5:4de0b000` | 14 | 15 | Huknij, gromie! |
| 02_cytaty_bitewne.md | battle_voice | `01999dd8:4fe0b000` | 10 | 11 | Tam jesteś! |
| 02_cytaty_bitewne.md | battle_voice | `01999dd9:ab60b000` | 19 | 23 | Pancerz mnie uratował…! |
| 02_cytaty_bitewne.md | battle_voice | `01999dda:0320b000` | 8 | 12 | Jeszcze nie! |
| 02_cytaty_bitewne.md | battle_voice | `01999ddf:fce0b000` | 22 | 24 | Pierwszy ruch jest mój…! |
| 02_cytaty_bitewne.md | battle_voice | `01999de1:d8a0b000` | 17 | 32 | Natychmiast odpowiedzieć ogniem! |
| 02_cytaty_bitewne.md | battle_voice | `01999de4:2360b000` | 10 | 11 | Tam jesteś! |
| 02_cytaty_bitewne.md | battle_voice-DLC1 | `00000411:d560b030` | 21 | 29 | A teraz policz swoje grzechy… |
| 03_umiejetnosci.md | skill_active_search-DLC1 | `00000b4e:c8e0b015` | 10 | 14 | Detektyw Fuuto |
| 05_interfejs.md | system_text | `009a8dad:1e20b00c` | 6 | 7 | Rozmiar |
| 05_interfejs.md | system_text | `009a8dad:1e20b01f` | 15 | 20 | Wymagana umiejętność |
| 05_interfejs.md | system_text | `009a8dad:1f20b019` | 4 | 7 | Maszyna |
| 05_interfejs.md | system_text | `00d07487:29a0b002` | 16 | 21 | Programy umiejętności |
| 05_interfejs.md | tutorial_text | `002bd864:73e0b000` | 13 | 14 | Ulepsz maszyny |
| 05_interfejs.md | tutorial_text | `002bd864:7720b000` | 11 | 12 | Załóż części |
| 05_interfejs.md | ICE_operation | `00000049:c8e0b00e` | 44 | 51 | Zestrzelenie jednego z: [p1:], [p2:], [p3:], [p4:]. |
| 05_interfejs.md | ICE_operation | `00000049:c920b025` | 77 | 92 | - Rzuć do walki wszystko, czego nauczyły cię dotychczasowe bitwy, i wygraj ostatnie starcie! |

Źródło: `python3 tools/pl_fill_return.py --manifest /tmp/pkg/import_manifest.json \
  --plan translations/pl2/PLAN_PL2.json --out /tmp/zwrotka` — sloty, których plan nie
mieści w węższym polu, zostają puste i są wypisane w raporcie. Ten sam warunek
sprawdza `tools/pl_import.py` przy każdej zwrotce od tłumacza.
