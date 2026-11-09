# PROŚBA 6 — katalog gry i japońskie wersje 17 scen

**Plik:** `SRW_Y_BRAKUJACE_DANE_PROSBA.zip` — folder projektu na Drive.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie `SRW_Y_BRAKUJACE_DANE.zip` — wgraj go na Drive.

Kit działa tak jak paczka do łamania opisów: `URUCHOM_TO.bat` szuka Pythona 3.9+
(`py -3`, potem `python`), sprawdza jego wersję, wypisuje krok po kroku co robi i przy
braku Pythona mówi to wprost. Cały przebieg trafia do `SRW_Y_BRAKUJACE_log.txt` na
pulpicie — czarne okno bez informacji już się nie zdarzy.

## Co już wiem (zmierzone na danych w repozytorium)

| pytanie | pomiar |
|---|---|
| misje w danych gry | **533** wpisy, 528 różnych id (5 duplikatów, np. `m0036_0001410`) |
| rozdział 2 | **34** misje — tyle, ile na zrzucie „30 / 34" |
| sceny w korpusie | **614**, 120,794 linii |
| sceny bez japońskiego | **17**, 4,893 linii, z tego **4,607** bez JP |
| misje bez linii `misja:` | **87**, 17,090 linii |

## Sceny, w których brakuje japońskiego

| scena | linii | z JP | bez JP | misja |
|---|---|---|---|---|
| `cse20_0024_0202800a` | 300 | 20 | 280 | — |
| `cse20_0024_0202800b` | 72 | 16 | 56 | — |
| `cse20_0024_0202800c` | 69 | 31 | 38 | — |
| `cse20_0024_0202800d` | 108 | 15 | 93 | — |
| `cse20_0025_0202801a` | 644 | 8 | 636 | — |
| `cse20_0025_0202801b` | 501 | 108 | 393 | — |
| `cse20_0041_0202810a` | 257 | 43 | 214 | — |
| `cse20_0041_0202810b` | 414 | 2 | 412 | — |
| `cse20_0041_0202810c` | 490 | 1 | 489 | — |
| `cse20_0047_0202820a` | 674 | 15 | 659 | — |
| `cse20_0047_0202820b` | 181 | 2 | 179 | — |
| `cse20_0047_0202820c` | 114 | 24 | 90 | — |
| `cse20_0059_0202830a` | 487 | 1 | 486 | — |
| `cse20_1014_0200900a` | 429 | 0 | 429 | — |
| `cse20_2000_0106300a` | 149 | 0 | 149 | m2000_0106300 |
| `cse20_8000_0000300a` | 3 | 0 | 3 | — |
| `cse20_9040_0000000a` | 1 | 0 | 1 | — |

W indeksie bundli te sceny występują wyłącznie jako `en`. Katalog gry powie, czy wersja
`ja` w ogóle istnieje — i w którym bundlu.

## Co zbiera kit

* katalogi Addressables z każdej paczki, w której leży katalog;
* `lista.txt` — wszystkie pliki pod StreamingAssets z rozmiarami;
* bundle misji (adresy z `mission`);
* bundle z japońskimi wersjami 17 scen;
* bundle z nieznanych paczek, pojedyncze, do 40 MB.

Nie wysyła ponownie 661 bundli znanych z indeksu korpusu.

## Co się dzieje po odesłaniu

1. Dla każdej z 17 scen sprawdzę, czy w grze istnieje asset `ja`. Jeśli tak — wchodzi do
   korpusu i do paczki; jeśli nie — w paczce zostaje angielski z adnotacją.
2. Z danych misji odczytam pole `name` i domknę 87 misji bez etykiety.
3. Wtedy napiszę odpowiedzi 8 i 9 — każdą z liczbą i wskazaniem pliku.

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

Razem **661** bundli.
