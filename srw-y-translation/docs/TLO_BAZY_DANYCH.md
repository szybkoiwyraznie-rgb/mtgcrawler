# SRW Y — tło ekranu Database: paczka `SRW_Y_SPIS_TEKSTUR.zip`

## O co chodzi

W ekranie **Database** (mechy i postacie) gra rysuje model na tle wnętrza
A. Adventu. Tło jest osobną **teksturą**, nie tekstem, którego dotyczy patch —
dlatego nie zmienia go żaden z dotychczasowych planów. Cel: jednolite czarne tło,
żeby screeny były czyste.

## Czego brakuje

W repozytorium nie ma **żadnych plików gry** (ani jednego bundla), więc nie mogę
nazwać tej tekstury. Nazwa musi wyjść z kopii właściciela. Wysyłanie bundli nie
jest potrzebne: paczka robi na jego komputerze **spis tekstur** i jeden mały ZIP.

## Paczka dla właściciela

`SRW_Y_SPIS_TEKSTUR.zip` (Drive `1plOEQSWn2bjV0aNLyylUiDYC-2YRV5t2`, 11 019 B,
SHA-256 `cb9b5a31…d0f11`), zbudowana przez `tools/build_scan_kit.py`:

```
SRW_Y_SPIS_TEKSTUR/
  CZYTAJ_TO.md            instrukcja po polsku
  SKANUJ.bat              dwuklik: szuka gry, stawia .venv, skanuje, pakuje wynik
  narzedzia/
    spis_tekstur.py       silnik: czyta bundel po bundlu, nic nie zapisuje w grze
    srw_y_bundle_crypt.py cipher bundli (ten sam, co w patcherze)
    requirements.txt      UnityPy==1.25.4, pycryptodome==4.2.0, lz4==4.4.5,
                          texture2ddecoder, Pillow
```

BAT jest wzorowany na `PATCH_PL.bat` z kitów patcha: szuka `py -3`/`python`,
zakłada osobne `.venv`, przy pierwszym uruchomieniu dociąga zależności, a jeśli
gry nie znajdzie w typowych miejscach, przyjmuje folder przeciągnięty na plik.

Efekt: na Pulpicie `SPIS_TEKSTUR.zip` z `RAPORT_TEKSTUR.txt` (każda `Texture2D`:
nazwa, `WxH`, format, bundel) oraz `PODGLADY/` — zmniejszone PNG **wszystkich
obrazów ≥ 1280×720**, numerowane tak samo jak w raporcie.

## Jak działa skan (i dlaczego jest szybki)

- Pomija bundle mniejsze niż 64 KiB — tabele tekstu i scen mają kilka kilobajtów,
  więc odpada ~90% plików bez ich otwierania.
- Deszyfruje cipher strumieniowy tak samo jak `srw_y_bundle_crypt`, ale XOR robi
  `Crypto.Util.strxor` (C) zamiast pętli po bajtach: ~60 MB/s zamiast ~1 MB/s.
- Czyta tylko typetree `Texture2D` (bez dekodowania pikseli); piksele dekoduje
  wyłącznie dla podglądów, natychmiast po odczytaniu bundla, żeby nie trzymać
  w pamięci całych plików.
- Każdy bundel w `try/except`: nieczytelny plik trafia do raportu, nie przerywa
  skanu. Nagłówek raportu podaje liczbę bundli, tekstur, błędów i bundli bez
  obiektów — po tym poznam, czy gra ma inną wersję, niż zakładam.

## Co będzie dalej

1. Właściciel odsyła `SPIS_TEKSTUR.zip`.
2. Rozpoznaję wnętrze A. Adventu na podglądach (numer → bundel + nazwa tekstury).
3. Podmiana pikseli na czarne w tym samym formacie i rozmiarze, przebudowa
   bundla na jego kopii, odczyt zwrotny i `COFNIJ.bat` — tą samą drogą, co atlas
   menu (`tools/build_pl_ui_atlas.py`), ale na jego plikach, nie na moich.

## Czego to nie obiecuje

- Nie wiem, czy ekran rysuje tło wyłącznie z tekstury — jeśli część tła to
  geometria 3D, podmiana da czarną plamę tylko w miejscu obrazu. Rozstrzygnie to
  pierwszy test na screenie.
- Nadal `runtime_tested: false` po naszej stronie: sprawdzenie robi właściciel.
