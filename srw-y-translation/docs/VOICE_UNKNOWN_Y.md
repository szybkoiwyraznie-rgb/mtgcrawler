# Cytaty bez kontenera — grupy dla tłumacza (`??? 001`…)

Tych kwestii **nie da się przypisać do postaci z plików gry**: ich zestaw głosu
nie wszedł do wydanego builda (dowód w `GLOSY_BITEWNE_Y.md` §9–10). Właściciel
zdecydował, że tłumacz przekłada je mimo to — lepsze to niż angielski — ale musi
wiedzieć, **które z nich mówi jedna postać, a które inna**, żeby nie mieszać
rodzaju gramatycznego. Stąd identyfikatory `??? 001`, `??? 002`…

- kwestii bez mówcy: **1,915**
- grup: **138**
- kwestii w grupach z podpowiedzią mówcy: 1,870
- kwestii w grupach z podpowiedzią płci: 1,800

## Skąd się bierze grupa

Klucz jest **zmierzony** na 32 402 kwestiach, które mają mówcę. `WaveId` to
`<rodzina>_<numer>` (`F363_142`, `DA03_008`, `gra_001_0007`), a rodzina to jeden
zestaw głosu. Sprawdzenie, ile grup ma jednego mówcę:

| klucz | grup | grup z jednym mówcą | kwestii w takich grupach |
|---|---|---|---|
| sam bank | 39 | 5 | 0.0% |
| rodzina | 470 | 414 | 89.2% |
| rodzina + bank (użyty tutaj) | 556 | 514 | 92.8% |

Grupowanie jest więc rodziną głosu (a gdy rodzina bywa wielomówcza — rodziną
w obrębie banku). Tam, gdzie grupa nadal zawiera dwóch mówców, to prawie zawsze
ten sam bohater w duecie (`カムイ` vs `カムイ＆獏`), nie dwie różne osoby.

## Grupy

| grupa | kwestii | tabele | rodzina | seria (z banku) | podpowiedź mówcy |
|---|---|---|---|---|---|
| **??? 001** | 122 | battle_voice | `DA03` | — | バーン (mężczyzna), 152 kwestii w tej rodzinie |
| **??? 002** | 55 | battle_voice | `DA04` | — | 黒騎士 (mężczyzna), 90 kwestii w tej rodzinie |
| **??? 003** | 65 | battle_voice | `DA08` | — | シーラ (kobieta), 118 kwestii w tej rodzinie |
| **??? 004** | 12 | battle_voice | `DA09` | — | カワッセ (mężczyzna), 17 kwestii w tej rodzinie |
| **??? 005** | 95 | battle_voice | `F084a` | — | スルガ (mężczyzna), 266 kwestii w tej rodzinie |
| **??? 006** | 15 | battle_voice | `F300` | — | ヒイロ (mężczyzna), 119 kwestii w tej rodzinie |
| **??? 007** | 3 | battle_voice | `F301` | — | シン (mężczyzna), 55 kwestii w tej rodzinie |
| **??? 008** | 10 | battle_voice | `F302` | — | スレッタ (kobieta), 292 kwestii w tej rodzinie |
| **??? 009** | 3 | battle_voice | `F303` | — | ミオリネ (mężczyzna), 79 kwestii w tej rodzinie |
| **??? 010** | 1 | battle_voice | `F308` | — | エラン (mężczyzna), 48 kwestii w tej rodzinie |
| **??? 011** | 8 | battle_voice | `F309` | — | シャディク (mężczyzna), 69 kwestii w tej rodzinie |
| **??? 012** | 4 | battle_voice | `F310` | — | チュチュ (mężczyzna), 179 kwestii w tej rodzinie |
| **??? 013** | 8 | battle_voice | `F311` | — | サビーナ (kobieta), 61 kwestii w tej rodzinie |
| **??? 014** | 4 | battle_voice | `F312` | — | 鉄也 (mężczyzna), 142 kwestii w tej rodzinie |
| **??? 015** | 3 | battle_voice | `F313` | — | 悪霊将軍ハーディアス, 126 kwestii w tej rodzinie |
| **??? 016** | 2 | battle_voice | `F314` | — | 戦闘獣ダンテ, 117 kwestii w tej rodzinie |
| **??? 017** | 23 | battle_voice | `F315` | — | 拓馬 (mężczyzna), 198 kwestii w tej rodzinie |
| **??? 018** | 2 | battle_voice | `F316` | — | カムイ (mężczyzna), 123 kwestii w tej rodzinie |
| **??? 019** | 18 | battle_voice | `F317` | — | カムイ (mężczyzna), 200 kwestii w tej rodzinie |
| **??? 020** | 16 | battle_voice | `F318` | — | 獏 (mężczyzna), 194 kwestii w tej rodzinie |
| **??? 021** | 2 | battle_voice | `F319` | — | マクドナルド (mężczyzna), 121 kwestii w tej rodzinie |
| **??? 022** | 7 | battle_voice | `F320` | — | バイス (mężczyzna), 116 kwestii w tej rodzinie |
| **??? 023** | 13 | battle_voice | `F321` | — | 恐竜兵士 (mężczyzna), 169 kwestii w tej rodzinie |
| **??? 024** | 4 | battle_voice | `F322` | — | ボブ, 112 kwestii w tej rodzinie |
| **??? 025** | 15 | battle_voice | `F323` | — | ハヤテ (mężczyzna), 211 kwestii w tej rodzinie |
| **??? 026** | 21 | battle_voice | `F324` | — | ミラージュ (kobieta), 160 kwestii w tej rodzinie |
| **??? 027** | 10 | battle_voice | `F325` | — | アラド (mężczyzna), 142 kwestii w tej rodzinie |
| **??? 028** | 17 | battle_voice | `F326` | — | メッサー (mężczyzna), 159 kwestii w tej rodzinie |
| **??? 029** | 13 | battle_voice | `F327` | — | チャック (mężczyzna), 121 kwestii w tej rodzinie |
| **??? 030** | 1 | battle_voice | `F328` | — | アーネスト (mężczyzna), 132 kwestii w tej rodzinie |
| **??? 031** | 8 | battle_voice | `F329` | — | キース (mężczyzna), 133 kwestii w tej rodzinie |
| **??? 032** | 7 | battle_voice | `F331` | — | ロイド, 71 kwestii w tej rodzinie |
| **??? 033** | 8 | battle_voice | `F332` | — | ボーグ (mężczyzna), 128 kwestii w tej rodzinie |
| **??? 034** | 7 | battle_voice | `F333` | — | ヘルマン (mężczyzna), 96 kwestii w tej rodzinie |
| **??? 035** | 8 | battle_voice | `F334` | — | カシム (mężczyzna), 99 kwestii w tej rodzinie |
| **??? 036** | 4 | battle_voice | `F335` | — | テオ (mężczyzna), 86 kwestii w tej rodzinie |
| **??? 037** | 5 | battle_voice | `F336` | — | ザオ (mężczyzna), 85 kwestii w tej rodzinie |
| **??? 038** | 9 | battle_voice | `F337` | — | ウィンダミア兵 (mężczyzna), 190 kwestii w tej rodzinie |
| **??? 039** | 9 | battle_voice | `F338` | — | ウィンダミア兵 (mężczyzna), 190 kwestii w tej rodzinie |
| **??? 040** | 3 | battle_voice | `F339` | — | フレイア, 6 kwestii w tej rodzinie |
| **??? 041** | 5 | battle_voice | `F340` | — | — |
| **??? 042** | 3 | battle_voice | `F341` | — | — |
| **??? 043** | 3 | battle_voice | `F342` | — | — |
| **??? 044** | 3 | battle_voice | `F343` | — | — |
| **??? 045** | 3 | battle_voice | `F344` | — | ルルーシュ (mężczyzna), 42 kwestii w tej rodzinie |
| **??? 046** | 3 | battle_voice | `F345` | — | スザク (mężczyzna), 45 kwestii w tej rodzinie |
| **??? 047** | 2 | battle_voice | `F346` | — | カレン (kobieta), 31 kwestii w tej rodzinie |
| **??? 048** | 18 | battle_voice | `F348` | — | ジェットジャガー (mężczyzna), 207 kwestii w tej rodzinie |
| **??? 049** | 10 | battle_voice | `F349` | — | — |
| **??? 050** | 15 | battle_voice | `F350` | — | ガウマ (mężczyzna), 144 kwestii w tej rodzinie |
| **??? 051** | 26 | battle_voice | `F350` | — | ガウマ (mężczyzna), 145 kwestii w tej rodzinie |
| **??? 052** | 22 | battle_voice | `F351` | — | 蓬 (mężczyzna), 95 kwestii w tej rodzinie |
| **??? 053** | 25 | battle_voice | `F352` | — | 夢芽 (kobieta), 68 kwestii w tej rodzinie |
| **??? 054** | 21 | battle_voice | `F353` | — | 暦 (mężczyzna), 58 kwestii w tej rodzinie |
| **??? 055** | 3 | battle_voice | `F354` | — | ちせ (mężczyzna), 28 kwestii w tej rodzinie |
| **??? 056** | 21 | battle_voice | `F356` | — | ジュウガ (mężczyzna), 165 kwestii w tej rodzinie |
| **??? 057** | 5 | battle_voice | `F357` | — | ジュウガ (mężczyzna), 60 kwestii w tej rodzinie |
| **??? 058** | 22 | battle_voice | `F358` | — | オニジャ (mężczyzna), 173 kwestii w tej rodzinie |
| **??? 059** | 5 | battle_voice | `F359` | — | オニジャ (mężczyzna), 46 kwestii w tej rodzinie |
| **??? 060** | 62 | battle_voice | `F360` | — | ムジナ (kobieta), 26 kwestii w tej rodzinie |
| **??? 061** | 2 | battle_voice | `F361` | — | ムジナ (kobieta), 122 kwestii w tej rodzinie |
| **??? 062** | 6 | battle_voice | `F362` | — | ムジナ (kobieta), 49 kwestii w tej rodzinie |
| **??? 063** | 144 | battle_voice | `F363` | — | シズム (mężczyzna), 38 kwestii w tej rodzinie |
| **??? 064** | 17 | battle_voice | `F364` | — | グリッドナイト (mężczyzna), 184 kwestii w tej rodzinie |
| **??? 065** | 7 | battle_voice | `F365` | — | ジュウガ (mężczyzna), 73 kwestii w tej rodzinie |
| **??? 066** | 9 | battle_voice | `F366` | — | オニジャ (mężczyzna), 76 kwestii w tej rodzinie |
| **??? 067** | 7 | battle_voice | `F367` | — | ムジナ (kobieta), 60 kwestii w tej rodzinie |
| **??? 068** | 9 | battle_voice | `F368` | — | シズム (mężczyzna), 97 kwestii w tej rodzinie |
| **??? 069** | 9 | battle_voice | `F377` | — | クロス (mężczyzna), 404 kwestii w tej rodzinie |
| **??? 070** | 9 | battle_voice | `F378` | — | フォルテ (kobieta), 399 kwestii w tej rodzinie |
| **??? 071** | 6 | battle_voice | `F380` | — | エチカ (kobieta), 229 kwestii w tej rodzinie |
| **??? 072** | 1 | battle_voice | `F381` | — | エチカ (kobieta), 12 kwestii w tej rodzinie |
| **??? 073** | 2 | battle_voice | `F382` | — | ノーヴィー (mężczyzna), 74 kwestii w tej rodzinie |
| **??? 074** | 12 | battle_voice | `F383` | — | ノーヴィー (mężczyzna), 7 kwestii w tej rodzinie |
| **??? 075** | 1 | battle_voice | `F386` | — | アニーナ (kobieta), 50 kwestii w tej rodzinie |
| **??? 076** | 1 | battle_voice | `F387` | — | ミナ (kobieta), 30 kwestii w tej rodzinie |
| **??? 077** | 4 | battle_voice | `F399` | — | セイヴァース (mężczyzna), 278 kwestii w tej rodzinie |
| **??? 078** | 2 | battle_voice | `F400` | — | システィス (kobieta), 187 kwestii w tej rodzinie |
| **??? 079** | 2 | battle_voice | `F401` | — | ヴァルベルム (mężczyzna), 155 kwestii w tej rodzinie |
| **??? 080** | 3 | battle_voice | `F402` | — | ヴァルベルム (mężczyzna), 142 kwestii w tej rodzinie |
| **??? 081** | 1 | battle_voice | `F403` | — | 天闘志, 208 kwestii w tej rodzinie |
| **??? 082** | 1 | battle_voice | `F404` | — | 天闘志, 210 kwestii w tej rodzinie |
| **??? 083** | 1 | battle_voice | `F405` | — | イザナ (kobieta), 107 kwestii w tej rodzinie |
| **??? 084** | 2 | battle_voice | `F406` | — | イヴォルバー (mężczyzna), 120 kwestii w tej rodzinie |
| **??? 085** | 1 | battle_voice | `F408` | — | ヴィル (mężczyzna), 85 kwestii w tej rodzinie |
| **??? 086** | 1 | battle_voice | `F409` | — | 高性能AIR, 148 kwestii w tej rodzinie |
| **??? 087** | 64 | battle_voice | `gra_001` | — | 拓馬 (mężczyzna), 68 kwestii w tej rodzinie |
| **??? 088** | 34 | battle_voice | `gra_004` | — | 號 (mężczyzna), 56 kwestii w tej rodzinie |
| **??? 089** | 5 | battle_voice | `gra_005` | — | 兎猿猴 (mężczyzna), 63 kwestii w tej rodzinie |
| **??? 090** | 33 | battle_voice | `hayate` | — | ハヤテ (mężczyzna), 5 kwestii w tej rodzinie |
| **??? 091** | 32 | battle_voice | `mak_010` | — | 鉄也 (mężczyzna), 76 kwestii w tej rodzinie |
| **??? 092** | 2 | battle_voice | `s269` | — | バラオ (mężczyzna), 31 kwestii w tej rodzinie |
| **??? 093** | 54 | battle_voice | `v201` | — | 鉄也 (mężczyzna), 66 kwestii w tej rodzinie |
| **??? 094** | 20 | battle_voice | `E153` | — | ネバンリンナ (kobieta), 63 kwestii w tej rodzinie |
| **??? 095** | 14 | battle_voice-DLC1 | `D155` | — | ロジャー (mężczyzna), 52 kwestii w tej rodzinie |
| **??? 096** | 2 | battle_voice-DLC1 | `D165` | — | ベック (mężczyzna), 47 kwestii w tej rodzinie |
| **??? 097** | 20 | battle_voice-DLC1 | `D167` | — | — |
| **??? 098** | 7 | battle_voice-DLC1 | `D638` | — | ロジャー (mężczyzna), 46 kwestii w tej rodzinie |
| **??? 099** | 16 | battle_voice-DLC1 | `F410` | — | 仮面ライダーＷ (mężczyzna), 211 kwestii w tej rodzinie |
| **??? 100** | 13 | battle_voice-DLC1 | `F411` | — | 仮面ライダーＷ (mężczyzna), 87 kwestii w tej rodzinie |
| **??? 101** | 12 | battle_voice-DLC1 | `F412` | — | 仮面ライダーアクセル (mężczyzna), 140 kwestii w tej rodzinie |
| **??? 102** | 16 | battle_voice-DLC1 | `F413` | — | 仮面ライダースカル (mężczyzna), 162 kwestii w tej rodzinie |
| **??? 103** | 70 | battle_voice-DLC2 | `dko_001` | — | リョウマ (mężczyzna), 55 kwestii w tej rodzinie |
| **??? 104** | 29 | battle_voice-DLC2 | `F415` | — | ダ・ガーン (mężczyzna), 181 kwestii w tej rodzinie |
| **??? 105** | 30 | battle_voice-DLC2 | `F416` | — | 星史, 111 kwestii w tej rodzinie |
| **??? 106** | 7 | battle_voice-DLC2 | `F417` | — | レッドロン (mężczyzna), 81 kwestii w tej rodzinie |
| **??? 107** | 8 | battle_voice-DLC2 | `F418` | — | リョウマ (mężczyzna), 132 kwestii w tej rodzinie |
| **??? 108** | 2 | battle_voice-DLC2 | `F429` | — | イグジス (mężczyzna), 69 kwestii w tej rodzinie |
| **??? 109** | 3 | battle_voice-DLC2 | `F430` | — | イグジス (mężczyzna), 68 kwestii w tej rodzinie |
| **??? 110** | 22 | battle_voice-DLC3 | `F419` | — | タクト (mężczyzna), 164 kwestii w tej rodzinie |
| **??? 111** | 3 | battle_voice-DLC3 | `F420` | — | エウレカ (kobieta), 174 kwestii w tej rodzinie |
| **??? 112** | 5 | battle_voice-DLC3 | `F421` | — | 春香 (kobieta), 145 kwestii w tej rodzinie |
| **??? 113** | 5 | battle_voice-DLC3 | `F422` | — | コスモ (mężczyzna), 97 kwestii w tej rodzinie |
| **??? 114** | 15 | battle_voice-DLC3 | `F424` | — | デク, 56 kwestii w tej rodzinie |
| **??? 115** | 1 | battle_voice-DLC3 | `F427` | — | — |
| **??? 116** | 3 | battle_voice-DLC3 | `F431` | — | ユザーパー (mężczyzna), 84 kwestii w tej rodzinie |
| **??? 117** | 3 | battle_voice-DLC3 | `F432` | — | ユザーパー (mężczyzna), 121 kwestii w tej rodzinie |
| **??? 118** | 1 | battle_voice-DLC3 | `D350` | — | Ｃ．Ｃ． (kobieta), 29 kwestii w tej rodzinie |
| **??? 119** | 42 | battle_voice-DLC4 | `D498` | — | クロウ (mężczyzna), 97 kwestii w tej rodzinie |
| **??? 120** | 61 | battle_voice-DLC4 | `D568` | — | クロウ (mężczyzna), 15 kwestii w tej rodzinie |
| **??? 121** | 29 | battle_voice-DLC4 | `D809` | — | クロウ (mężczyzna), 46 kwestii w tej rodzinie |
| **??? 122** | 8 | battle_voice-DLC4 | `F433` | — | 洸 (mężczyzna), 24 kwestii w tej rodzinie |
| **??? 123** | 3 | battle_voice-DLC4 | `F445` | — | グエル, 109 kwestii w tej rodzinie |
| **??? 124** | 1 | battle_voice-DLC4 | `F446` | — | エラン (mężczyzna), 72 kwestii w tej rodzinie |
| **??? 125** | 3 | battle_voice-DLC4 | `F447` | — | エラン (mężczyzna), 101 kwestii w tej rodzinie |
| **??? 126** | 2 | battle_voice-DLC4 | `F448` | — | チュチュ (mężczyzna), 85 kwestii w tej rodzinie |
| **??? 127** | 1 | battle_voice-DLC4 | `F453` | — | ノレア (kobieta), 54 kwestii w tej rodzinie |
| **??? 128** | 1 | battle_voice-DLC4 | `F454` | — | ノレア (kobieta), 33 kwestii w tej rodzinie |
| **??? 129** | 3 | battle_voice-DLC4 | `F456` | — | 拓馬 (mężczyzna), 35 kwestii w tej rodzinie |
| **??? 130** | 2 | battle_voice-DLC4 | `F457` | — | ハヤテ (mężczyzna), 24 kwestii w tej rodzinie |
| **??? 131** | 2 | battle_voice-DLC4 | `F458` | — | メッサー (mężczyzna), 19 kwestii w tej rodzinie |
| **??? 132** | 3 | battle_voice-DLC4 | `F459` | — | ルルーシュ (mężczyzna), 39 kwestii w tej rodzinie |
| **??? 133** | 3 | battle_voice-DLC4 | `F460` | — | イズル (mężczyzna), 32 kwestii w tej rodzinie |
| **??? 134** | 1 | battle_voice-DLC4 | `F461` | — | ジェットジャガー (mężczyzna), 50 kwestii w tej rodzinie |
| **??? 135** | 3 | battle_voice-DLC4 | `F463` | — | ガウマ (mężczyzna), 35 kwestii w tej rodzinie |
| **??? 136** | 1 | battle_voice-DLC4 | `F464` | — | 鉄也 (mężczyzna), 19 kwestii w tej rodzinie |
| **??? 137** | 17 | battle_voice-DLC4 | `F466` | — | マグダ (mężczyzna), 23 kwestii w tej rodzinie |
| **??? 138** | 1 | battle_voice-DLC4 | `F468` | — | グーゴル (mężczyzna), 107 kwestii w tej rodzinie |

## Jak to czytać

1. **Numer `??? NNN` = jedna postać.** W obrębie numeru trzymaj jeden rodzaj
   gramatyczny; zmiana rodzaju w środku numeru to błąd.
2. **Liczby w kolumnie „kwestii”** pokazują, jak duża to grupa — od 1 do
   kilkuset linii.
3. **Podpowiedź mówcy** jest dowodem z danych, nie etykietą: w tej samej
   rodzinie głosu są już kwestie z imieniem i wszystkie mają jednego mówcę.
   W paczce dla tłumacza ta podpowiedź jest podana jako *podpowiedź*, a nie
   jako imię — decyzja o rodzaju należy do tłumacza, a japoński tekst często
   sam mówi o płci (`俺` / `私` / `あたし`).
4. **Seria** pochodzi z banku i jest dowiedziona tylko dla części banków
   (`VOICE_BANKS_Y.md`); puste pole = nie wiemy.
