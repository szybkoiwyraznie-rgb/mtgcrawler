# SRW Y - KROK 3 (nowe podejscie): 276 par "jawny / zaszyfrowany"

Wersja arkusza: 2026-10-26.9 (poprzedni: 2026-10-26.6, szukanie klucza w pamieci)

## Co sie zmienilo i dlaczego to lepsza droga

Dwa dni temu z pamieci dzialajacej gry wycial sie 597 **odszyfrowanych** bundle'i
(kazdy zaczyna sie od `UnityFS` i deklaruje wlasny rozmiar - to prawdziwe,
kompletne paczki, nie smieci). Sprawdzilem je z Twoja lista plikow:

- 362 rozmiary z tych 597 istnieja na dysku,
- dla **276** z nich na dysku jest **dokladnie jeden** plik o takim rozmiarze,
- razem te 276 plikow to tylko **3,0 MB**.

Czyli dla tych 276 plikow mam juz **odszyfrowana tresc** (z pamieci) i moge miec
**zaszyfrowana** (z dysku). Z takiej pary liczy sie strumien klucza:

    strumien = plik_zaszyfrowany XOR plik_jawny

Ten strumien zalezy tylko od klucza i stanu danego pliku - **nie od tresci**.
Wiec moge podmienic tekst w jawnej wersji, dopelnic zerami do oryginalnego
rozmiaru, przepuscic przez ten sam strumien i dostaje plik, ktory gra odszyfruje
poprawnie. **Bez znajdowania klucza i bez grzebania w pamieci w trakcie gry.**

Uczciwie: tej drogi nie moglem sprawdzic bez tych plikow. Pierwszy test to jeden
podmieniony napis, ktory zobaczysz w grze (punkt 3 nizej).

Dlatego ten krok jest tylko kopiowaniem plikow. Nic nie nadpisujemy w grze.

## KROK 1 - skopiuj 276 plikow i spakuj je

Otworz PowerShell (Win+R -> `powershell` -> Enter) i wklej **caly** blok naraz:

```powershell
$game = 'D:\Games\SUPER ROBOT WARS Y'
$out  = "$env:USERPROFILE\Desktop\srw_y_pairs"
$sizes = @(
1629,2062,2104,2331,2493,2494,2773,2794,2839,2855,2870,2871,3041,3154,3157,3790,4100,4109,4111
4112,4120,4128,4133,4138,4140,4142,4202,4206,4219,4231,4273,4311,4317,4319,4342,4413,4472,4485
4489,4500,4558,4574,4578,4609,4620,4639,4656,4659,4668,4669,4674,4709,4736,4743,4755,4826,4839
4846,4879,4928,4945,5013,5028,5057,5061,5066,5159,5161,5163,5190,5212,5260,5430,5453,5454,5455
5517,5593,5675,5684,5688,5694,5696,5713,5782,5913,5934,5946,6100,6134,6196,6266,6303,6347,6415
6511,6548,6584,6638,7201,7360,7432,7454,7473,7610,7687,7732,7775,7862,8064,8066,8067,8133,8151
8161,8163,8188,8241,8301,8332,8335,8416,8436,8459,8490,8491,8609,8628,8672,8683,8710,8717,8720
8723,8795,8797,8801,8836,8861,8879,8928,8941,9007,9055,9097,9102,9103,9107,9147,9171,9218,9221
9311,9329,9330,9379,9383,9412,9436,9444,9475,9481,9494,9599,9615,9625,9635,9655,9690,9699,9737
9750,9751,9768,9770,9796,9798,9820,9858,9862,9967,10018,10056,10058,10075,10223,10298,10313
10400,10427,10515,10560,10576,10600,10693,10701,10708,10748,10752,10818,10924,11255,11469,11481
11763,12114,12292,12454,12522,12585,12599,12829,13235,13371,13635,13972,14420,14497,15119,15226
15289,15421,15561,15795,15978,15991,16004,16090,16704,16876,17186,17381,18017,18466,18658,18692
18708,18732,18763,19277,19492,19669,19686,19755,19827,19867,19938,19940,20174,20416,20463,20826
20850,21083,21086,21130,21186,21414,21517,21521,21535,21597,22074,22315,23190,23326,24058,25737
27292,28139,28151,29497,30710,45534,67372,275626
)
New-Item -ItemType Directory -Force -Path $out | Out-Null
$set = New-Object 'System.Collections.Generic.HashSet[long]'
foreach ($s in $sizes) { [void]$set.Add([long]$s) }
$copied = 0
Get-ChildItem -Path $game -Recurse -Filter *.bundle -File -ErrorAction SilentlyContinue |
  Where-Object { $set.Contains([long]$_.Length) } |
  ForEach-Object {
    Copy-Item $_.FullName -Destination $out -Force
    $copied++
  }
"skopiowano: $copied plikow"
Get-ChildItem -Path $out -File | Measure-Object -Property Length -Sum |
  ForEach-Object { "rozmiar: {0:N0} B" -f $_.Sum }
Compress-Archive -Path "$out\*" -DestinationPath "$env:USERPROFILE\Desktop\srw_y_pairs.zip" -Force
"zip: $env:USERPROFILE\Desktop\srw_y_pairs.zip"
```

Co powinno wyjsc na koncu (w przyblizeniu):

```
skopiowano: 276 plikow
rozmiar: 3,113,778 B
zip: C:\Users\<Ty>\Desktop\srw_y_pairs.zip
```

Jesli `skopiowano` pokaze inna liczbe niz 276 - napisz mi jaka, to tez jest
informacja (znaczy, ze ktoras paczka sie rozni rozmiarem od tej z listy).
Jesli wyjdzie `skopiowano: 0`, to folder gry ma inna nazwe niz
`D:\Games\SUPER ROBOT WARS Y` - zmien pierwsza linijke na wlasciwa sciezke
i wklej blok jeszcze raz. Nazw plikow nie zmieniaj.

## KROK 2 - wyslij mi `srw_y_pairs.zip`

Plik lezy na pulpicie: `srw_y_pairs.zip` (ok. 3 MB). Wrzuc go na Dysk Google do
tego samego folderu, z ktorego bralem `key_report.json`, albo po prostu dolacz do
rozmowy. Folder na pulpicie `srw_y_pairs` mozesz potem zostawic - przyda sie,
jesli bede potrzebowal wiecej paczek.

## Co zrobie z tym dalej

1. Policze 276 strumieni klucza i sprawdze, czy ktorys sie powtarza (to od razu
   powie, czy stan jest wspolny czy per plik).
2. Wybiore jedna mala paczke z japonskim tekstem, podmienie jeden napis na polski,
   przepuszcze przez strumien i odezwie sie z jednym plikiem `.bundle` + komenda
   podmiany (z kopia zapasowa). Wtedy zobaczysz polski tekst w grze i bedziemy
   mieli dzialajaca metode - tak jak w OE.

Zadnych zmian w grze w tym kroku nie rob. Samo kopiowanie i zip.
