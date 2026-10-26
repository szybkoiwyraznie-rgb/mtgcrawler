# Cytaty bitewne — mówcy z danych gry (`tools/voice_speaker_map.py`)

Każda kwestia jest przypisana **tylko** wtedy, gdy kontener głosu gry podaje
dla jej `WaveId` pole `nameText` — imię mówcy, które gra sama wyświetla nad
kwestią. Żadnego zgadywania z treści.

- kwestii w tabeli `battle_voice`: **34,317**
- z odczytanym mówcą: **10,740** (31.3%)
- różnych mówców: **120**
- z płcią z `PilotBasicDatas`: 6,210 kwestii

| tabela | z mówcą | wszystkich |
|---|---|---|
| `battle_voice` | 5,670 | 28,283 |
| `battle_voice-DLC1` | 1,071 | 1,175 |
| `battle_voice-DLC2` | 794 | 947 |
| `battle_voice-DLC3` | 1,335 | 1,833 |
| `battle_voice-DLC4` | 1,870 | 2,079 |

## Najczęstsi mówcy

| mówca | kwestii |
|---|---|
| スレッタ | 524 |
| ヒイロ | 366 |
| 拓馬 | 344 |
| ダバ | 322 |
| ガウマ | 305 |
| 鉄也 | 302 |
| 仮面ライダーＷ | 296 |
| ルルーシュ | 291 |
| イズル | 272 |
| ショウ | 260 |
| ジェットジャガー | 256 |
| ハヤテ | 234 |
| デュオ | 227 |
| チュチュ | 225 |
| 五飛 | 206 |

## Mówcy w więcej niż jednym banku

Bank głosów to jedna seria, więc ten sam mówca może mówić w kilku bankach
(np. postać gościnna w cudzej serii). To nie błąd — to własność danych.

- ショウ: `000a9ed0`, `01999dc9`, `01999dd5`, `01999dd6`, `01999dda`, `01999ddb`, `01999ddc`, `01999de3`
- ヒイロ: `000a9ed0`, `01999dc9`, `01999dca`, `01999dd5`, `01999dd6`, `01999dd7`, `01999dd8`, `01999dda`
- トロワ: `000a9ed0`, `01999dc9`, `01999dca`, `01999dd5`, `01999dd6`, `01999dd8`, `01999dda`
- カトル: `000a9ed0`, `01999dc9`, `01999dd5`, `01999dd6`, `01999dd7`, `01999dda`
- デュオ: `000a9ed0`, `01999dc9`, `01999dd5`, `01999dd6`, `01999dd8`, `01999dda`
- 拓馬: `000a9ed0`, `01999dcb`, `01999dcc`, `01999dd4`, `01999dd5`, `03477a0e`
- 豹馬: `000a9ed0`, `01999dd5`, `01999dd6`, `01999ddd`, `033f9035`
- スレッタ: `000a9ed0`, `01999dca`, `01999dcb`, `03355af9`
- ルルーシュ: `000a9ed0`, `01999dcf`, `01999dde`, `01999ddf`
- チャム: `01999dd5`, `01999dd8`, `01999ddc`, `03477a0e`
