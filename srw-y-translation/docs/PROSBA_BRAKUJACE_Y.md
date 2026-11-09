# PROŚBA 6 — katalog gry i japońskie wersje 17 scen

## Dlaczego dopiero teraz

Poprzednie odpowiedzi na pytania 8 i 9 pisałem z danych, które akurat miałem pod ręką,
i dwie z nich były po prostu złe: twierdziłem, że misji „苦闘する忍者" nie ma w danych,
a ona jest — pod zapisem `ＮＩＮＪＡ奮闘` (EN: „The Struggling NINJA"), misja
`m1001_0001100`, 299 linii w korpusie. Wniosek: odpowiedź bez sprawdzenia w tabelach
i w danych misji jest gorsza niż brak odpowiedzi.

## Co już wiem (zmierzone na danych w repozytorium)

| pytanie | pomiar |
|---|---|
| ile jest misji w danych gry | **533** wpisy, 528 różnych id (5 duplikatów, np. `m0036_0001410`) |
| ile ma rozdział 1–7 | 144; rozdział 2 ma **34** misje — tyle, ile na Twoim zrzucie „30 / 34" |
| ile scen w korpusie | **614** scen, 120,794 linii |
| sceny bez japońskiego | **17** scen, 4,893 linii, z tego **4,607** bez JP |
| misje bez linii `misja:` w paczce | **87** misji, 17,090 linii |
| tytuły misji | 378 podstawa + 149 dodatki (DLC1 31, DLC2 29, DLC3 48, DLC4 41) |

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

To jest **4,607 z 120,794 linii (3.8%)**. W indeksie bundli te sceny
występują wyłącznie jako `en` — nie ma dla nich żadnego assetu `ja`. Nie wiem, czy to
dlatego, że japoński leży w bundlu, którego nie zebrałem, czy dlatego, że tych linii
w grze po japońsku nie ma. Katalog gry odpowiada na to wprost.

## Co zbiera kit

* **katalogi Addressables** z każdej paczki (`catalog.json`, `catalog.hash`,
  `settings.json`, `catalog.bin`);
* **`lista.txt`** — wszystkie pliki pod `StreamingAssets/aa` z rozmiarami;
* **bundle misji** (adresy z `mission`) — stamtąd pole `name` każdej misji, czyli tytuł
  dokładnie tak, jak pokazuje go gra;
* **bundle z japońskimi wersjami 17 scen** — wybrane po nazwie sceny w adresie;
* **bundle z nieznanych paczek**, pojedyncze, do 40 MB.

Kit nie wysyła ponownie 661 bundli, które są już w indeksie korpusu.

## Co się dzieje po odesłaniu

1. Dla każdej z 17 scen sprawdzę, czy w grze istnieje asset `ja`. Jeśli tak —
   wchodzi do korpusu i do paczki; jeśli nie — w paczce zostaje sam angielski, z adnotacją.
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
