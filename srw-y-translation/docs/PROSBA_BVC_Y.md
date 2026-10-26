# PROŚBA 2 — kontenery głosu (`SRW_Y_BVC_PROSBA.zip`)

## Co się zmieniło po pierwszej paczce

`SRW_Y_GLOSY.zip` (3 080 644 B) rozwiązał zagadkę do połowy:

- **`PilotBasicDatas`** (5 tabel) — **683 rekordy pilotów**; każdy ma `id` (`AKIRA_S`,
  `ECHIKA`, `HYOMA`…), nazwę, `genderType` i **`bvcFile`** (`REIRE_HA0`, `NAGCV_AH0`,
  `OSROG_EF0`…), a `RobotBasicDatas` (1 198 robotów) ma `voiceGroup` i `voiceContainer`;
- **`battle_voice Shared Data`** — 28 283 wpisy z **kluczami** typu `F321_026`,
  `DA03_274`, `10A_286`, `D498_001` (plus 4 067 w dodatkach);
- **`voiceactor`, `pilot_name`, `dic_text_pilot`, `assist_text`, `strategypart_pilotmess`,
  `ace_bonus`** — wszystkie mają czytelne klucze (`VAName_M_0001`, `dic_pilot_AKIRA_00_0`,
  `Serifu_AMRO_S_1`, `AB_DOMON`…), więc kody postaci są potwierdzone w danych.

Brakuje **jednego** elementu: pliku kontenera głosu, który mówi, które klucze
`battle_voice` należą do którego pilota. To adresowalne assety o nazwach równych
`bvcFile` plus `BvcCommon` (linie wspólne). Zmierzone po katalogu i spisie rozmiarów:

| | |
|---|---|
| bundli | **310** |
| razem | **1,237,239 B** (≈ 1.2 MB) |

## Co uruchomić

**`SRW_Y_BVC_PROSBA.zip`** — na Drive w folderze projektu
(`1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`), **id `1QnueT9fKBGkbxh8kGwjJV_FndY-7WJqt`**, 9 634 B,
sha256 `682cc3b8…7c262cf`. W środku `URUCHOM_TO.bat`, `ZBIERZ_BVC.ps1`, `CZYTAJ_TO.txt`.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie **`SRW_Y_BVC.zip`** — wgraj go na Drive (ten sam folder).

## Co z tego zrobimy

1. Z każdego kontenera odczytamy listę kluczy (`F321_026`…) i przypiszemy je do pilota,
   którego `bvcFile` wskazuje ten asset.
2. Połączymy to z tabelą `battle_voice` (klucz → tekst jp/en) i z `pilot_name`.
3. Sprawdzimy wynik na treści: grupa z „ブライ・ソード!” musi trafić do pilota z Big O /
   Braiger, grupa z „イデオンソード!” — do Kosmo (Ideon).
4. Etykieta w paczce tłumacza zmieni się na `[Cytat bitewny — アムロ (Amuro)]`,
   z płcią mówcy z `genderType`. Cytaty i tłumaczenia bez zmian.

## Pierwsze pliki w paczce

| plik | rozmiar | kontener |
|---|---|---|
| `00ca78c58b197aaa6684007eaa68a12b.bundle` | 2,424 B | GUNGW_RN0 |
| `017ad2aedcd4541d9d8fee75e442fd85.bundle` | 2,404 B | OSRVT_ME0 |
| `02ac558b8ca454b53d6375d2ef4d4a4c.bundle` | 14,498 B | GEARE_LL1_00 |
| `02de42cd35f3579e24a2fa61f175151b.bundle` | 2,428 B | SDBIN_DHA |
| `02f801e3a8d19ae2e1462815f6347a5e.bundle` | 2,423 B | MGP01_RM0 |
| `04296ae07e63f918970de647e5658b67.bundle` | 2,425 B | GUNGW_HY0, GUNGW_HY0, GUNGW_HY0 |
| `048fb7139a781a28fb267d89d832b2e1.bundle` | 2,182 B | 3EXID_AT0_00 |
| `0691e03167ace3e37f0f2777ffeb2237.bundle` | 2,424 B | SDBIN_TG0, SDBIN_TG0, SDBIN_TG0 |
| `069a39b30afd9714989c50da5107cc89.bundle` | 2,419 B | GUNSM_SF0 |
| `070c7acb2cf7358d9fe3b513d9e97a42.bundle` | 4,015 B | 2BVOG_EXP_00, 2BVOG_EXP_00 |
| `07e0de0ad0134457dcf68b20c5c786cc.bundle` | 2,420 B | GUNCC_GG0 |
| `07e90eac9a9e860634a8caeca656f35f.bundle` | 2,420 B | GUNZG_FY0, GUNZG_FY0 |
| … | | pozostałe 298 |
