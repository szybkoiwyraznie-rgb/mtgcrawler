# SRW Y — tło ekranu Database (bez zmian w grze bez Twojej zgody)

## O co chodzi

W ekranie **Database** (mechy i postacie) gra rysuje model na tle wnętrza
A. Adventu. Tło jest osobną teksturą, nie tekstem, którego dotyczy patch —
dlatego nie da się go zmienić żadnym z dotychczasowych planów.

Cel: **jednolite czarne tło** w tym ekranie, żeby screeny były czyste.

## Czego brakuje

W repozytorium nie ma **żadnych plików gry** (ani jednego bundla), więc nie mogę
nazwać tej tekstury. Nazwa musi wyjść z Twoich plików. Nie trzeba mi ich wysyłać
— wystarczy spis, który robi narzędzie tylko czytające.

## Co zrobić (jednorazowo, ~1–3 minuty)

1. W folderze `srw-y-translation/` (albo w dowolnym miejscu, gdzie masz to
   repozytorium) uruchom w PowerShell:

   ```powershell
   python tools/find_db_background.py --game "D:\Games\SUPER ROBOT WARS Y\SUPER ROBOT WARS Y_Data\StreamingAssets\aa\StandaloneWindows64" --out RAPORT_TEKSTUR.txt
   ```

   (Zmień ścieżkę, jeśli grę masz gdzie indziej. Python 3.10+ i pakiety
   `UnityPy==1.25.4`, `pycryptodome`, `lz4` — te same, których używa patcher.)

2. Wyślij mi **`RAPORT_TEKSTUR.txt`** (albo tylko dwie sekcje z jego końca:
   `NAJWIEKSZE OBRAZY` i `NAZWY MOGAce BYC TLEM MENU/BAZY`).

Narzędzie **niczego nie zmienia** — czyta bundel po bundlu i wypisuje:

```
bundle<TAB>tekstura<TAB>1920x1080<TAB>format<TAB>strumień
```

Na końcu raportu są dwie listy skrócone: największe obrazy (od 1280×720) i nazwy
przypominające tło menu/biblioteki (`db`, `data_base`, `library`, `zukan`,
`back`, `bg`).

## Co będzie dalej

Mając nazwę tekstury i bundla, zrobię to samo, co przy atlasie menu
(`tools/build_pl_ui_atlas.py`): podmiana pikseli na czarne w tym samym formacie
i rozmiarze, przebudowa bundla na Twojej kopii, weryfikacja odczytu i cofanie
`COFNIJ.bat`. Kolejność:

1. Podmiana **jednej** tekstury — test, czy to na pewno to tło.
2. Jeśli tło składa się z kilku warstw (np. osobna podłoga, osobne światła),
   raport pokaże sąsiednie tekstury z tego samego bundla i wtedy decydujemy,
   które zerować, a które zostawić.

## Czego to nie obiecuje

- Nie wiem, czy ekran nie rysuje tła także z geometrii 3D (mesh) — jeżeli tak,
  podmiana tekstury da czarną plamę tylko w miejscu obrazu, a nie w całym oknie.
  To rozstrzygnie pierwszy test na Twoim screenie.
- Nadal `runtime_tested: false` po naszej stronie: sprawdzenie robisz Ty, w grze.
