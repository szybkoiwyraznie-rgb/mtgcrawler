# Cytaty bitewne SRW Y — mówcy, runda 3 (2026-10-26, po paczce od właściciela)

Runda 2 skończyła się prośbą o 17 plików danych (`SRW_Y_GLOSY_PROSBA.zip`). Właściciel
ją wykonał: **`SRW_Y_GLOSY.zip`, 3 080 644 B, sha256 `9d0ddfcf…f66067d`, 17/17 bundli,
dostarczone 2026-10-26 16:04**. Ten dokument opisuje, co z nich odczytano, co z tego
wynika dla etykiet mówców i czego jeszcze brakuje.

Wniosek z rundy 1 („mówców nie ma w danych i nie da się ich odzyskać”) jest **odrzucony
przez właściciela i wycofany**. Połączenie istnieje, jest w danych i w tej rundzie
zostało częściowo odczytane.

## 1. Co przyszło i co z tego odczytano

Bundli: 17, wszystkie odszyfrowane tym samym kluczem (`SeekableAesStream`, hasło
`ComBBStudioSRTeam`, sól = nazwa bundla bez `.bundle`). Razem **158 obiektów z nazwą**;
spis: `tools/voice_intake.py` → `local/s6/voice_intake.json`.

| obiekt | sztuk | co zawiera |
|---|---|---|
| `PilotBasicDatas*` | 5 | **683 pilotów**: `id`, nazwa, `genderType`, `bvcFile`, `voiceContainer`, `aceBonusId` |
| `RobotBasicDatas*` | 5 | **1 198 jednostek**: `id`, `ipnameId`, `voiceGroup`, `voiceContainer`, nazwy jp |
| `battle_voice* Shared Data` | 5 | **34 317 wpisów** z **kluczami** (`F321_026`, `10A_286`, `D498_001`…) |
| `DicDetail_Pilot` | 1 | słownik pilota (teksty) |
| `SystemBasicDatas*` | 3 | tytuły IP, flagi globalne, rangi — bez głosów |

Rozkład pilotów: 683 rekordy, **553 z niepustym `bvcFile`**, **127 kobiet**
(`genderType` 2; 0 i 1 to mężczyźni — 0 dostają jednostki bez pilota). Rozkład jednostek:
1 198 w **29 seriach** (`ipnameId`), każda z `voiceGroup` i `voiceContainer`.

## 2. Czego się dowiedzieliśmy o kluczach

`battle_voice Shared Data` **ma nazwy kluczy** i są one kodami, nie nazwami postaci:
`F321_026`, `DA03_274`, `10A_286`, `D498_001`, `05A_504`. Żadna inna tabela nie używa
tych kodów (katalog assetów: 0 trafień na `F321`, `10A`, `D498`), więc klucz sam nie
nazywa mówcy.

Struktura wiersza `high:low` po odczycie 34 317 wierszy:

- **`high` = bank**: 39 wartości (31 w podstawce, 2/1/4/1 w dodatkach), 932–2 079 kwestii
  na bank. Bank to **zestaw głosów jednej serii** — dowód w sekcji 3.
- **`low` = identyfikator wpisu** z generatora Unity: bity 12–21 to numer maszyny
  (`11` w 32 205 wierszach, `8` w 2 112), bity 0–11 sekwencja (maks. 148), reszta to
  znacznik czasu. Wewnątrz banku ten identyfikator **nie niesie informacji o mówcy** —
  to tylko ślad sesji edytora.

Poprzednia hipoteza („numer maszyny `0x20B`”) była błędna — poprawiona powyżej,
na pełnym zbiorze wierszy.

## 3. Bank = seria: dowód z treści i danych jednostek

Kwestie cytują własne roboty („ブライ・ソード!”, „イデオンソード!”), a `RobotBasicDatas`
podaje `ipnameId` każdej jednostki. `tools/voice_bank_ip.py` liczy, ile kwestii w banku
nazywa jednostkę danej serii:

| bank | kwestii | kwestii z nazwą | seria | udział |
|---|---|---|---|---|
| `01999dd4` | 1 066 | 22 | `ORGNL` | 92% |
| `01999dd0` | 1 062 | 39 | `DYNZNN` | 100% |
| `01999dda` | 1 060 | 31 | `ORGNL` | 72% |
| `01999dcc` | 1 049 | 34 | `GTRARK` | 81% |
| `01999dcb` | 1 042 | 24 | `MZKZRDSDG` | 67% |
| `01999de0` | 1 039 | 39 | `MJP` | 98% |
| `01999de1` | 1 026 | 52 | `MJP` | 96% |
| `01999dd3` | 1 024 | 63 | `ORGNL` | 100% |
| `01999dd2` | 1 023 | 82 | `ORGNL` | 93% |
| `01999dcf` | 1 014 | 35 | `GZLSP` | 70% |
| `01999dd1` | 1 005 | 32 | `DYNZNN` | 82% |

**11 z 39 banków** dostaje serię przy progu „≥20 kwestii nazywa jednostkę i ≥60% udziału
w kwestiach, które nazywają jakąkolwiek jednostkę”. Pełna tabela: `docs/VOICE_BANKS_Y.md`
(dane: `local/s6/voice_bank_ip.json`). Pozostałe 28 banków zostaje numerami — mieszają
serie albo mają za mało nazw. To nadal **nie jest mówca**, tylko seria.

## 4. Czego brakuje: jednostka → klucze

Łańcuch, który gra ma, a my mamy tylko do połowy:

```text
pilot (PilotBasicDatas)  →  bvcFile / voiceContainer   ← MAMY (683 pilotów)
        ↓                                                  brakujące ogniwo
kontener głosu (bundle o nazwie bvcFile)  →  klucze `F321_026` …
        ↓
wiersz battle_voice (klucz → tekst jp/en)              ← MAMY (34 317)
        ↓
robot (RobotBasicDatas) → pilot                        ← MAMY (1 198 jednostek)
```

Kontener to adresowalny asset o nazwie równej `bvcFile` (np. `REIRE_HA0`) plus
`BvcCommon` (linie wspólne). Katalog gry zna te adresy, spis plików właściciela podaje
rozmiary: **310 bundli, 1 237 239 B** — największy 37 KB, większość po ~2 KB. To dane
przypisań, nie audio.

Druga prośba: **`SRW_Y_BVC_PROSBA.zip`** — Drive `1QnueT9fKBGkbxh8kGwjJV_FndY-7WJqt`
(9 634 B, sha256 `682cc3b8…7c262cf`), opis `docs/PROSBA_BVC_Y.md`, skrypt
`tools/collect_bvc_bundles.ps1`. Ten sam format co pierwsza: rozpakuj na pulpit,
`URUCHOM_TO.bat`, na pulpicie powstaje `SRW_Y_BVC.zip`, wgraj na Drive.

## 5. Narzędzia tej rundy

| narzędzie | co robi |
|---|---|
| `tools/pilot_master.py` | czyta 5 tabel `PilotBasicDatas` + 5 `RobotBasicDatas` → `local/s6/pilots.json` (683) i `robots.json` (1 198); `--bvc-bundles` rozwiązuje `bvcFile` → bundle |
| `tools/voice_intake.py` | spis wszystkich 17 bundli: obiekty, nazwy, liczby wpisów, klucze → `local/s6/voice_intake.json` |
| `tools/voice_bank_ip.py` | bank → seria z nazw jednostek w kwestiach, z progiem i bez zgadywania → `local/s6/voice_bank_ip.json`, `docs/VOICE_BANKS_Y.md` |
| `tools/build_bvc_request.py` | generuje drugą prośbę (310 plików) → `build/bvc_request/SRW_Y_BVC_PROSBA.zip` |
| `tools/voice_bank_map.py` | po drugiej paczce: `bvcFile` → klucze → `local/s6/voice_banks.json` |
| `tools/voice_identify_speaker.py` | kotwice (`--phrase`, `--anchors`, `--derive`) — sprawdzenie mapowania na znanych okrzykach |
| `tools/voice_bank_content.py` | zaimki i nazwy per bank (`local/s6/voice_bank_evidence.*`, `voice_candidates.md`) |

## 6. Kolejność działań

1. Właściciel uruchamia `SRW_Y_BVC_PROSBA.zip` i wgrywa `SRW_Y_BVC.zip` (310 bundli).
2. `python3 tools/voice_bank_map.py` → klucz → `bvcFile` → pilot, z płcią z `genderType`.
3. Weryfikacja krzyżowa: bank↔seria z sekcji 3, nazwy wyłączne z
   `local/s6/voice_candidates.md`, kotwice (`--anchors`).
4. Nowa wersja paczki tłumacza: `[Cytat bitewny - アムロ (Amuro)]` zamiast `[głos 7/39]`;
   cytaty i tłumaczenia bez zmian, podmienia się tylko nagłówek elementu.

## 7. Czego nie zrobimy

- nie wpiszemy imienia na podstawie statystyki nazw w treści (błąd w paczce jest gorszy
  niż numer grupy); serie z sekcji 3 są publikowane **z progiem i udziałem**, jawnie jako
  seria, nie jako mówca,
- nie ogłosimy mapowania mówców, dopóki nie potwierdzą go dane z kontenerów głosu
  i weryfikacja krzyżowa.

## 8. Runda 4 (2026-10-26, wieczór) — połączenie jest odczytane i działa

Właściciel wykonał drugą prośbę: **`SRW_Y_BVC.zip`, 1 300 851 B, sha256
`be1fdc2f60fb49033c604c3316689e1a63a7b6018be20eed236ea90d012171e5`**, 310 bundli
(Drive `17z6uA0OVzSUW7PI4JM8lAMHeGr7UQuOA`). 84 z nich to kontenery głosu
(`PlayCategories`), pozostałe 226 to czyste audio CriWare (`.awb`) bez danych o mówcy.

### 8.1 Łańcuch, odtworzony w całości z danych gry

```
wiersz tabeli battle_voice      klucz 01999dc9:15e0b000
  -> battle_voice Shared Data   m_Id -> m_Key            "F069_002"
  -> kontener głosu             PlayDetails[].WaveId
                                -> {nameText, NameKey, FaceKey, dialogueText}
```

- `Shared Data` (5 obiektów) ma **45 303 wpisy** `m_Id -> m_Key`;
- **34 317 / 34 317** wierszy `battle_voice` rozwiązuje się do `WaveId` (100%);
- kontenery dają `WaveId -> nameText` — **imię mówcy, które gra sama wyświetla nad
  kwestią**, plus `NameKey` (klucz w `pilot_name`), `FaceKey` (portret) i `dialogueText`.

Narzędzie: `tools/voice_speaker_map.py` → `local/s6/voice_speakers.json`,
`local/s6/voice_map.json`, `docs/VOICE_MAP_Y.md`.

### 8.2 Co z tego wyszło

| tabela | z mówcą | wszystkich |
|---|---|---|
| `battle_voice` | 5 670 | 28 283 |
| `battle_voice-DLC1` | 1 071 | 1 175 |
| `battle_voice-DLC2` | 794 | 947 |
| `battle_voice-DLC3` | 1 335 | 1 833 |
| `battle_voice-DLC4` | 1 870 | 2 079 |
| **razem** | **10 740 (31,3%)** | **34 317** |

- **120 różnych mówców**, wszyscy z `nameText` (żadnego zgadywania z treści):
  スレッタ 524, ヒイロ 366, 拓馬 344, ダバ 322, ガウマ 305, 鉄也 302,
  仮面ライダーＷ 296, ルルーシュ 291, イズル 272, ショウ 260;
- **6 210 kwestii** ma płeć z `PilotBasicDatas.genderType` (imię mówcy = nazwa pilota);
- dodatki są prawie domknięte (DLC1 91%, DLC2 84%, DLC4 90%, DLC3 73%) — brakuje
  głównie podstawki (20%), bo to właśnie jej kontenery nie przyszły w tej paczce.

**Bank ≠ mówca — potwierdzone na danych.** Bank (`high`) to zestaw głosów serii; w jednym
banku mówi wielu bohaterów (np. `000a9ed0`: 40 mówców, `0000157d`: 12). Dlatego mówcę
bierzemy **wyłącznie** z `WaveId -> nameText`, nigdy z banku ani z treści.

### 8.3 Czego brakuje i jak to domykamy

23 577 kwestii wskazuje `WaveId`-y z kontenerów, których jeszcze nie mamy. Kontener to
asset o nazwie `GEARE_LL1_00`, `1SPBO_BK0_00`… — wzorzec sprawdzony na 84/84 posiadanych.
W katalogach (podstawka + 11 paczek) jest **395** takich assetów, 84 już mamy, więc
trzecia prośba to **311 bundli, 2 088 297 B**:

**`SRW_Y_BVC3_PROSBA.zip`** — 9 878 B, sha256
`eb71bcf05d32c320bdec27e9afb3ad1aacbe0c5e2caafd6d469fd506f6a64581`,
Drive `1eIG9ATPXU50ILlorT2KUd49MyoYkDagK`; opis `docs/PROSBA_BVC_REST_Y.md`,
skrypt `tools/collect_bvc_rest_bundles.ps1`, generator
`tools/build_bvc_rest_request.py`. Ten sam format: rozpakuj na pulpit →
`URUCHOM_TO.bat` → na pulpicie `SRW_Y_BVC3.zip` → wgraj na Drive.

Po tej paczce mówca jest przypisany **każdej** kwestii, dla której gra go zna — bez
etykiety „nieznany” i bez statystyki z treści.

### 8.4 Sprawdzenie na znanych okrzykach (wymóg właściciela)

`tools/voice_phrase_anchor.py` bierze okrzyk, o którym wiadomo, kto go wykrzykuje, i pokazuje
całą drogę: wiersz → `Shared Data` → `WaveId` → kontener → `nameText`. Wynik na czterech
kotwicach (`docs/VOICE_ANCHORS_Y.md`):

| okrzyk | oczekiwany | odczytani mówcy | wynik |
|---|---|---|---|
| イデオンソード | コスモ | コスモ, デク | ZGODNY |
| ブライ・ソード | キッド | キッド, アイザック | ZGODNY |
| ダ・ガーン | 星史 | 星史, レッドロン, ダ・ガーン, イグジス | ZGODNY |
| ゲッタービーム | 拓馬 | 拓馬 | ZGODNY |

To jest odpowiedź na pytanie „jak i gdzie to jest zapisane”: mówca siedzi w `nameText`
kontenera wskazanego przez `WaveId`, a nie w banku i nie w treści. Okrzyk nazywający robota
wraca z nazwą **pilota** (イデオンソード → コスモ, nie „イデオン”), więc pomyłka co do roli
tego pola jest wykluczona.

## 9. Runda 5 — po trzeciej paczce: **94,4% kwestii ma imię mówcy**

Właściciel wgrał trzecią paczkę: **`SRW_Y_BVC3.zip`, 2 152 053 B, sha256
`28fa1e39eff3aba7d02e9c42cc371993779f6cc7bb44265b02ddf257e80fba0f`**
(Drive `1I-J08uvFCoufOpfI5ZqsxBFO0mN9QMPY`), 311 plików = dokładnie 2 088 297 B
zamówionych. 309 z 311 bundli to kontenery z `PlayCategories` — reszta to audio.

### 9.1 Wynik

| tabela | z mówcą | wszystkich |
|---|---|---|
| `battle_voice` | 26 862 | 28 283 |
| `battle_voice-DLC1` | 1 075 | 1 175 |
| `battle_voice-DLC2` | 798 | 947 |
| `battle_voice-DLC3` | 1 775 | 1 833 |
| `battle_voice-DLC4` | 1 892 | 2 079 |
| **razem** | **32 402 (94,4%)** | **34 317** |

- **290 różnych mówców** — każdy z `nameText` kontenera, zero zgadywania z treści;
- **14 552 kwestie** z płcią z `PilotBasicDatas.genderType`;
- najczęstsi: ジルクスタン兵 634, スレッタ 566, ポセイダル兵 464, イズル 422, 天闘志 418,
  クロス 404, アンジュ 403, フォルテ 399;
- kontenery z treścią: **393** (84 z paczki 2 + 309 z paczki 3), 283 różnych nazw.

Narzędzie czyta teraz **wszystkie** katalogi kontenerów (`local/voice/bvc*/`), więc każda
kolejna paczka wchodzi bez zmian w kodzie.

### 9.2 Pozostałe 1 915 kwestii (5,6%) — co dokładnie wiemy

To nie jest „nie da się”. To jest policzone:

1. każde z tych 1 915 kwestii **ma** klucz w `Shared Data` i **ma** `WaveId`
   (np. `DA03_008`, `F363_001`, `dko_xxx`), więc łańcuch działa do drugiego kroku;
2. kontenera z tym `WaveId` nie ma **w żadnym** posiadanym pliku: przeszukanie wszystkich
   stringów w 840 obiektach `MonoBehaviour` z 632 bundli daje dla tych `WaveId`-ów tylko
   jedno trafienie — `m_Entries.m_Key` w `Shared Data` (czyli same nazwy kluczy);
3. zasoby tego samego typu co kontenery (`resource_type` 20 i 17) są **wszystkie** odebrane —
   w katalogach nie ma już ani jednego nieodczytanego assetu tej klasy;
4. `BvcCommon` (podstawka + 4 dodatki, typ 69) też już mamy: to nie tabela `WaveId`, tylko
   `judgeTables` + `attachTypeBases` (reguły, kiedy gra odtwarza linię wspólną).

Wniosek roboczy, który trzeba domknąć plikami: te zestawy głosu są adresowane **samym kodem**
(`GUNCC_ARB`, `GUNSM_SM5`, `4ANOG_AD0`…) albo ich nie ma w wydanym buildzie.

### 9.3 Prośba 4 — ostatnia z tej rodziny

**`SRW_Y_BVC4_PROSBA.zip`** — 6 329 B, sha256
`72ffa01404ba61abecc4f4315b9b50afdd5e2872ca708e2ee59a2947383e360e`,
Drive `1uKyYh0ai1cM-J2e2MmjmxwE1-S6Ih9At`; opis `docs/PROSBA_BVC_FINAL_Y.md`,
skrypt `tools/collect_bvc_final_bundles.ps1`, generator
`tools/build_bvc_final_request.py`. **145 bundli, 520 834 B**, dwa kryteria:

- każdy adres tego samego **typu zasobu** co kontenery (17, 20), bez względu na nazwę —
  zostały dokładnie dwa (`StrategyPartCharaSerifuData_dlc2`,
  `UnitBattleAnimDataLibrary_dlc_expansion2`);
- każdy adres w rodzinie kodów głosu (`KOD_XX0`, `KOD_XX0_00`, `BvcCommon…`), którego bundel
  ma ≤ 8 KiB, czyli jest tabelą, a nie sceną czy lokalizacją.

Jeśli po tej paczce te 1 915 kwestii nadal nie będą miały kontenera, to znaczy, że ich zestawy
głosu nie weszły do wydanego builda — i powiemy to liczbą („kwestia istnieje w tabeli, klipu
nie ma w danych”), a nie domysłem.
