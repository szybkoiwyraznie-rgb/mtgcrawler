# Krok S2 — potrzebny plik kodu gry (dla właściciela)

**Skrót:** metadane dotarły i zostały przeszukane. Klucza tam nie ma — sprawdziłem
2,2 mln literałów z metadanych na 13 różnych szyfrach i 3,8 mln kluczy
wyprowadzonych z tych literałów skrótami MD5/SHA. Żadnego trafienia. Sprawdziłem
też, czy to nie jest zwykłe maskowanie, kompresja albo szyfr z powtarzalnym
kluczem — nie jest. Szczegóły: `docs/S2_FINDINGS.md`.

Zostaje jeden plik, w którym klucz może być: **kod gry**.

## Co wgrać

```
D:\Games\SUPER ROBOT WARS Y\GameAssembly.dll
```

rozmiar **74 865 152 B** (71,4 MiB). Leży **w głównym folderze gry**, obok
`SUPER ROBOT WARS Y.exe` — nie w `_Data`.

```powershell
explorer "D:\Games\SUPER ROBOT WARS Y"
```

Przeciągnij `GameAssembly.dll` do folderu **`SRW/SRWY`** na Dysku Google, tak jak
poprzednie pliki.

## Co to jest i czego w nim nie ma

- To **skompilowany kod gry** (Unity z IL2CPP pakuje cały C# do jednego pliku).
  W nim jest logika odszyfrowywania bundli, a więc najprawdopodobniej i klucz.
- **Nie ma tam dialogów, tekstu gry, grafik ani dźwięków.** Same instrukcje
  procesora i stałe.
- Nie da się z niego „uruchomić gry” ani nic z niego podmienić — nic nie zmieniam
  w Twojej instalacji, plik tylko kopiujesz.

## Co z nim zrobię

1. Odczytam nagłówki i sekcje (czy to x86-64, gdzie leży część danych).
2. Poszukam nazw, które powiedzą, **czym** jest szyfrowanie: klasy
   `CustomAssetBundleProvider` oraz śladów `AES` / `CreateDecryptor` /
   `Rijndael` / `SHA256`.
3. Podam każde okno 16/24/32 bajtów z sekcji danych jako kandydata na klucz i
   sprawdzę na prawdziwym bundlu — jeśli odszyfrowanie da sygnaturę `UnityFS`,
   mamy klucz i cała reszta rusza w ciągu jednego dnia.

**Mówię uczciwie, jakie są szanse:** to długi strzał. Jeśli klucz jest zwykłą
tablicą bajtów w pliku — znajdę go. Jeśli kod składa klucz w runtime z kilku
kawałków (częste w nowszych grach), tą drogą go nie zobaczę.

## Jeśli to nie zadziała

Zostaje droga „z pamięci gry”: gra sama odszyfrowuje bundle, więc można tekst
przechwycić w trakcie działania. Tu mam własny problem, nie grę: **w moim
środowisku nie ma kompilatora C#**, więc nie zbuduję wtyczki od ręki. Nie
obiecuję tego na dziś — napiszę osobno, co i jak, gdy będę miał plan, który sam
uznam za realny. Wolę to powiedzieć teraz niż po trzech tygodniach.

## Czego nie trzeba robić

- Nie wysyłaj `resources.assets` ani innych bundli — te dwa, które mam, wystarczą.
- Nie zmieniaj nic w folderze gry.
- Nie próbuj samodzielnie nic „odblokowywać” — to nie jest kwestia ustawienia.
