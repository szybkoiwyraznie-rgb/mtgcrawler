# Cytaty bitewne — mówcy z danych gry (`tools/voice_speaker_map.py`)

Każda kwestia jest przypisana **tylko** wtedy, gdy kontener głosu gry podaje
dla jej `WaveId` pole `nameText` — imię mówcy, które gra sama wyświetla nad
kwestią. Żadnego zgadywania z treści.

- kwestii w tabeli `battle_voice`: **34,317**
- z odczytanym mówcą: **32,402** (94.4%)
- różnych mówców: **290**
- z płcią z `PilotBasicDatas`: 14,552 kwestii
- bez kontenera w wydanym buildzie: **1,915** (5.6%) — te kwestie nie mają swojego zestawu głosu w danych; nie są zgadywane

| tabela | z mówcą | bez kontenera | wszystkich |
|---|---|---|---|
| `battle_voice` | 26,862 | 1,421 | 28,283 |
| `battle_voice-DLC1` | 1,075 | 100 | 1,175 |
| `battle_voice-DLC2` | 798 | 149 | 947 |
| `battle_voice-DLC3` | 1,775 | 58 | 1,833 |
| `battle_voice-DLC4` | 1,892 | 187 | 2,079 |

## Najczęstsi mówcy

| mówca | kwestii |
|---|---|
| ジルクスタン兵 | 634 |
| スレッタ | 566 |
| ポセイダル兵 | 464 |
| イズル | 422 |
| 天闘志 | 418 |
| クロス | 404 |
| アンジュ | 403 |
| フォルテ | 399 |
| ウィンダミア兵 | 380 |
| ヒイロ | 366 |
| スザク | 359 |
| ルルーシュ | 357 |
| 拓馬 | 353 |
| マリーメイア兵 | 350 |
| アサギ | 324 |

## Mówcy w więcej niż jednym banku

Bank głosów to jedna seria, więc ten sam mówca może mówić w kilku bankach
(np. postać gościnna w cudzej serii). To nie błąd — to własność danych.

- ショウ: `000a9ed0`, `01999dc9`, `01999dd5`, `01999dd6`, `01999dda`, `01999ddb`, `01999ddc`, `01999de3`
- ヒイロ: `000a9ed0`, `01999dc9`, `01999dca`, `01999dd5`, `01999dd6`, `01999dd7`, `01999dd8`, `01999dda`
- トロワ: `000a9ed0`, `01999dc9`, `01999dca`, `01999dd5`, `01999dd6`, `01999dd8`, `01999dda`
- カトル: `000a9ed0`, `01999dc9`, `01999dd5`, `01999dd6`, `01999dd7`, `01999dda`
- デュオ: `000a9ed0`, `01999dc9`, `01999dd5`, `01999dd6`, `01999dd8`, `01999dda`
- 拓馬: `000a9ed0`, `01999dcb`, `01999dcc`, `01999dd4`, `01999dd5`, `03477a0e`
- シャア: `00928a8b`, `01999dc9`, `01999dd6`, `01999dd7`, `01999dd8`
- シン: `01999dca`, `01999dd7`, `01999dd8`, `01999dd9`, `01999de3`
- ルルーシュ: `000a9ed0`, `001b407b`, `01999dcf`, `01999dde`, `01999ddf`
- 豹馬: `000a9ed0`, `01999dd5`, `01999dd6`, `01999ddd`, `033f9035`
