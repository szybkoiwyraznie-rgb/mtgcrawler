# Audyt katalogów gry pod kątem kontenerów głosu — wszystkie paczki z dysku

Pytanie właściciela: czy sprawdzone zostały **wszystkie** paczki z dysku — darmowe DLC,
anniversary, bonus missions, season pass, deluxe/ultimate — a nie tylko `Dlc1`/`Dlc2`.

**Odpowiedź: tak, wszystkie. Wynik: zero brakujących kontenerów głosu.** Poniżej liczby.

## 1. Sprawdzone katalogi: 11, nie 2

Katalog Addressables (`StreamingAssets/aa/catalog.json` w podstawce i osobny w każdej
paczce) to jedyny spis tego, co jest w `.bundle`-ach. Właściciel wysłał je wszystkie:

| katalog | adresów | bundli | bundli mamy | zestawów głosu (`KOD_XX0_00`) | z nich **brak** | zasobów typu 17/20 | z nich **brak** |
|---|---|---|---|---|---|---|---|
| `base` | 187,039 | 19,924 | 770 | 391 | **0** | 778 | **0** |
| `AnniversaryExpansionPack` | 21,543 | 2,702 | 259 | 0 | **0** | 2 | **0** |
| `BonusMission` | 826 | 275 | 68 | 0 | **0** | 0 | **0** |
| `DeluxeEdition` | 24 | 8 | 2 | 0 | **0** | 0 | **0** |
| `Dlc1` | 6,556 | 857 | 58 | 0 | **0** | 2 | **2** |
| `Dlc2` | 6,698 | 805 | 113 | 0 | **0** | 2 | **0** |
| `EarlyPurchase` | 130 | 43 | 10 | 0 | **0** | 0 | **0** |
| `ExpansionPack` | 11,892 | 1,587 | 162 | 0 | **0** | 2 | **2** |
| `PremiumSound` | 200 | 67 | 2 | 0 | **0** | 0 | **0** |
| `SeasonPassBonus` | 6,577 | 434 | 18 | 4 | **0** | 8 | **0** |
| `UltimateEdition` | 24 | 8 | 2 | 0 | **0** | 0 | **0** |
| **razem** | | | | **395** | **0** | **794** | **4** |

Kryterium „zestaw głosu”: ten sam wzorzec nazwy, którym adresowane są kontenery odczytane
z paczek 2–4 (`GUNZG_ES0_00`, `DINAC_IG0_01`). Kryterium „typ 17/20”: `resource_type`
zasobów, które **na pewno są** kontenerami — spośród 283
kontenerów z odczytanym mówcą wszystkie mają w katalogu typ 17 albo 20 (typ 17: 4, typ 20: 279).

## 2. Co konkretnie brakuje z klasy kontenerów

`1abba1de6e4354a43b4fddd8f33b7b56`, `cri_addressables_dummy_anchor` — to nie kontener, a techniczna kotwica CriWare
(`cri_addressables_anchor_group_assets_…`), ten sam bundel w `Dlc1` i `ExpansionPack`.
Poza nią **nie ma ani jednego nieodebranego zasobu tej klasy**.

## 3. Paczka tekstowa DLC też objęła każdą paczkę

Bundli odebranych z tekstem, per paczka (razem **601**):

| paczka | bundli |
|---|---|
| `AnniversaryExpansionPack` | 210 |
| `BonusMission` | 68 |
| `DeluxeEdition` | 2 |
| `Dlc1` | 46 |
| `Dlc2` | 102 |
| `EarlyPurchase` | 10 |
| `ExpansionPack` | 149 |
| `PremiumSound` | 2 |
| `SeasonPassBonus` | 10 |
| `UltimateEdition` | 2 |

Czyli `AnniversaryExpansionPack`, `BonusMission`, `SeasonPassBonus`, `EarlyPurchase`,
`PremiumSound` i wydania `Deluxe`/`Ultimate` były otwierane tak samo jak `Dlc1`/`Dlc2` —
to z nich pochodzą tabele `battle_voice-DLC1…DLC4`.

## 4. Czy brakujące `WaveId`-y są gdziekolwiek w katalogach

Rodziny `WaveId` z 1 915 kwestii bez mówcy (137 rodzin) przeszukane
w adresach **wszystkich 11 katalogów**, bez podziału na paczki:

| rodzina | występuje w katalogach |
|---|---|
| — | **żadna z 137 rodzin nie występuje w żadnym katalogu** |

## 5. Co to znaczy

Wszystkie paczki z dysku są pokryte tym samym, mechanicznym kryterium. Kontenery głosu to
zasoby typu 17/20 i **wszystkie są na dysku**; rodziny brakujących `WaveId`-ów nie
występują w żadnym katalogu jako adres. Wniosek się nie zmienia: **32 402 z 34 317 kwestii
(94,4 %)** mają mówcę z danych gry, a pozostałe 1 915 to wiersze, których zestaw głosu nie
wszedł do wydanego builda — i tak są opisane w paczce tłumacza numerami `??? 001`…`??? 138`.
