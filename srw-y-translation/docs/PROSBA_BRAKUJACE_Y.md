# PROŚBA 6 (wersja 5) — katalog gry i 1 scena do pobrania

**Plik:** `SRW_Y_BRAKUJACE_DANE_PROSBA.zip` (56 559 B) — folder projektu na Drive.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie `SRW_Y_BRAKUJACE_DANE.zip` — wgraj go na Drive.

Kit działa tak jak paczka do łamania opisów: `URUCHOM_TO.bat` szuka Pythona 3.9+
(`py -3`, potem `python`), sprawdza jego wersję, wypisuje krok po kroku co robi i przy
braku Pythona mówi to wprost. Cały przebieg trafia do `SRW_Y_BRAKUJACE_log.txt` na
pulpicie — czarne okno bez informacji już się nie zdarzy.

## Co już wiem (zmierzone na danych z Twoich dwóch paczek i w repozytorium)

| pytanie | pomiar |
|---|---|
| misje w danych gry | **533** wpisy, 528 różnych id (5 duplikatów, np. `m0036_0001410`) |
| misje z tytułem z gry | **528** — po DANE2 każda misja bez etykiety ma tytuł |
| rozdział 2 | **34** misje — tyle, ile na zrzucie „30 / 34" |
| sceny w grze (11 katalogów) | **618**, z japońskim **600** |
| sceny w korpusie | **614**, 120,794 linii |
| wiersze korpusu z japońskim | **116 339**, bez japońskiego **4 455** |
| sceny do pobrania | **1** |
| sceny bez japońskiego w całej grze | **4** — żaden bundle tego nie zmieni |

## Co jeszcze trzeba pobrać

| scena | stan | linii w korpusie | misja |
|---|---|---|---|
| `cse20_3738_0999900a` | brak sceny | 0 | m3738_0999900 |

Scen **bez japońskiego w całej grze** jest 4: `cse20_0577_0999900a`, `cse20_0578_0999900a`, `cse20_0579_0999900a`, `cse20_9040_0000000a`. Nic ich nie
uzupełni — żaden bundle nie zawiera ich po japońsku. Trzy z nich
(`cse20_0577/0578/0579_0999900a`) są **tylko chińskie**. Pozostałych 13 scen z listy
„bez japońskiego” nie ma go tylko **pod własnym id** — japoński mają pod id bliźniaczym
(`0202830a` ↔ `0202831a`) i ten japoński jest już w korpusie, więc ich też nie ruszam.


## Co zbiera kit

* katalogi Addressables z każdej paczki, w której leży katalog;
* `lista.txt` — wszystkie pliki pod StreamingAssets z rozmiarami;
* bundle misji (adresy z `mission`);
* bundle sceny `cse20_3738_0999900a`;
* bundle z nieznanych paczek, pojedyncze, do 40 MB.

Nie wysyła ponownie **741** bundli, które już mam.

## Co się dzieje po odesłaniu

1. Scenę `cse20_3738_0999900a` wczytam do korpusu i do paczki tłumacza.
2. Uruchomię `tools/fill_scene_jp.py` dla każdej sceny, w której japoński jest pod
   bliźniaczym id — tak jak dla `cse20_2000_0106300a` (149 wierszy) i
   `cse20_8000_0000300a` (3 wiersze).
3. Etykiety `misja:` wejdą do paczki z tytułami z danych gry (87 misji
   bez etykiety ma już tytuł).

## Rozkład korpusu, który mam

| paczka | bundli w indeksie |
|---|---|
| `AnniversaryExpansionPack` | 210 |
| `ExpansionPack` | 149 |
| `Dlc2` | 102 |
| `BonusMission` | 68 |
| `aa` | 60 |
| `Dlc1` | 46 |
| `EarlyPurchase` | 10 |
| `SeasonPassBonus` | 10 |
| `DeluxeEdition` | 2 |
| `PremiumSound` | 2 |
| `UltimateEdition` | 2 |

Razem **741** bundli.
