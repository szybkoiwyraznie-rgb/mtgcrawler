# Instrukcja — widoki do tłumaczenia na polski (SRW OE)

Ten pakiet ma **dokładnie tę samą budowę** co `sceny.zip` i `widoki.zip` z etapu
angielskiego: pliki `md`, w których każdy element ma kontekst — gdzie dzieje się
scena, kto mówi (i z jakiej serii jest postać), jaki jest limit długości —
plus tekst japoński i **gotowe tłumaczenie angielskie jako referencję**.
Tłumaczenie ma być literackie i osadzone w kontekście, nie technicznym.

## Co robić

- Pod każdym elementem jest linia `PL:` — **tam wpisujesz tłumaczenie**.
- Linia `EN:` nad nią to gotowe tłumaczenie angielskie: używaj go jako kontekstu,
  terminologii i ostatecznej deski ratunkowej, ale tłumacz **z japońskiego**,
  po polsku, naturalnie — nie kalkuj angielskiego zdanie w zdanie.
  **Nie zmieniaj i nie usuwaj linii `EN:`.**
- Element z dopiskiem *(tłumaczenie dziedziczone automatycznie — nie wpisuj tu nic)*
  ma ten sam tekst co wcześniejszy element — pomiń go.
- Nagłówki `- odcinek:`, `- miejsce:`, `- uczestnicy:` itd. to kontekst —
  nie tłumacz ich.
- `spis-scen.md` to spis treści do nawigacji (numer sceny = kolejność w grze).

## Zasady techniczne (żeby gra przyjęła tekst)

1. **Polskie litery**: ą ć ę ł ń ó ś ź ż oraz Ą Ć Ę Ł Ń Ó Ś Ź Ż — wszystkie
   działają w grze. Inne znaki typograficzne NIE: nie używaj `—` (pauza),
   `–` (półpauza) ani `„` (cudzysłów otwierający). Zamiast tego: `-`,
   `"..."` (albo `…`), `”` jest dozwolone.
2. **Liczba linii musi zostać dokładnie taka jak w japońskim** — łamiesz tam,
   gdzie japoński. Końcowe `⏎` w tekście to łamanie okna gry: zostaw.
3. **Szerokość**: zwykła litera łacińska = 1 jednostka, polski znak
   diakrytyczny = 2 jednostki (tak samo `…` i znaki japońskie). Trzymaj się
   `limit:` podanym nad elementem — tekst poza limitem nie wejdzie do gry.
4. **Markery**: `⏎` = koniec linii, `<0x0F>` = niewidoczny znacznik gry —
   przepisuj je bez zmian, w tym samym miejscu.
5. **Symbole zastępcze**: `%s`, `%d`, `%02d` itd. to dane wstawiane przez grę
   (imię, liczba, nazwa). Każdy musi zostać w tłumaczeniu — bez nich gra
   pokaże krzak albo się zawiesi.
6. Nie dodawaj nowych elementów ani nie zmieniaj numerów — struktura pliku
   jest mapą na dane gry.

## Jak oddać pracę

- Edytuj pliki w dowolnym edytorze tekstu (kodowanie **UTF-8**), nie zmieniaj
  struktury linii poza linią `PL:`.
- Oddaj pliki (spakowane zipem lub pojedynczo) — wracają do pakietu jednym
  poleceniem `tools/translation_import.py --lang pl`, a każdy tekst przechodzi
  kontrolę powyższych zasad. To, co przekroczy limit albo złamie strukturę,
  **nie wejdzie** — dostaniesz raport z powodem.
- Możesz oddawać partiami (np. najpierw epizod 0–1) i sprawdzać fragmenty:
  `python tools/translation_import.py --views epizod-00.md --lang pl --check`.
