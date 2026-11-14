# Mod 4K + patch PL: jak to teraz działa

Data: 2026-11-13. Status: **zrobione i przetestowane na prawdziwym pliku z moda**.

## Co było problemem

Po zainstalowaniu moda *4K Visual Overhaul* (Nexus, mod 2) `INSTALUJ.bat`
kończył się natychmiast:

```
BŁĄD: aa/StandaloneWindows64/2d69c099bfdf0e252dabe84dbbba11df.bundle:
brak lub inna wersja pliku; gra nie została zmieniona
```

`install()` i `check()` porównywały SHA-256 każdego z 488 bundli z sumą
zapisaną w indeksie. Mod dostarcza pliki jako **gotowe kopie**, więc suma
nigdy się nie zgadzała — i cały patch stawał, choć w grze brakowało tylko
polskiego tekstu.

## Co pokazał plik z moda

Właściciel przesłał `2d69c099…bundle` z moda (948 663 B; w 1.4.0: 948 652 B)
oraz czysty `1c12bbab…bundle`. Po odszyfrowaniu i rozłożeniu:

| pomiar | wynik |
|---|---|
| tabele tekstowe | 37, identyczne nazwy i `path_id` jak w planie |
| wiersze tabel | 36 209, z czego **36 206 identyczne** z 1.4.0 |
| wiersze różne | **3** — wszystkie to etykiety rozdzielczości w `system_text_en-US` |
| polskie znaki w pliku moda | brak (mod nie tłumaczy) |
| obiekty w bundlu | 38, `AssetBundle` bez zmian |

Trzy różnice to `009a8dad:1d60b014/15/16`: `3840x2160`, `2560x1440`,
`1920x1080` — dokładnie to, co robi patch rozdzielczości tego samego autora.
Mod **nie** rusza `path_id`, nazw obiektów ani tekstur w tym bundlu.

## Jak patch działa teraz

**Nakładka jest trybem domyślnym.** Patch bierze plik, który jest w grze
(mody z Drive'a, plik z moda 4K, cokolwiek), podmienia w nim **tylko surowe
bajty obiektów tekstowych** po `path_id` i zapisuje wynik z powrotem.
Tekstury i wszystko inne zostaje nietknięte.

* Plik, który nie jest bundlem gry, jest odrzucany, zanim cokolwiek zostanie
  zapisane: patcher odszyfrowuje pierwszy kilobajt i wymaga `UnityFS`.
  Nazwa pliku jest kluczem szyfru, więc to realna kontrola tożsamości.
* Kopia zapasowa (`.srwy-original.bak`) to plik, który **był w grze** — czyli
  kopia z moda. `COFNIJ.bat` przywraca dokładnie ten plik, nie „czystą” grę.
* `STAN_PATCHA.json` zapisuje `"overlay": true`, więc cofanie wie, że suma
  pliku nie musi się zgadzać z indeksem.

**Weryfikacja ścisła** jest dostępna jako `--bez-nakladki` (w `INSTALUJ.bat`
dopisz flagę): wymaga dokładnie plików 1.4.0 i odmawia instalacji na modzie.
Do użycia, gdy ktoś chce mieć pewność, że patchuje czystą grę.

## Los etykiet rozdzielczości

Plan PL9 ma w tych trzech wierszach tekst 1.4.0 (`1920×1200`, `1920×1080`,
`1280×800`). Zapisanie go na pliku z moda **cofałoby** podmianę na 4K.
Dlatego w trybie nakładki wiersz, pod którym gra trzyma znaną etykietę 4K,
jest **pomijany** i trafia do raportu jako `etykieta_moda`, a nie jako rozjazd.
Każdy inny rozjazd tekstu pozostaje rozjazdem i nie dostaje polskiego zdania.

## Wynik na prawdziwym pliku z moda

Sprawdzone end-to-end (`install` → `check` → `restore`) na `2d69c099…bundle`:

* 36 206 wierszy z polskim tekstem, 0 błędów,
* etykiety `3840x2160`, `2560x1440`, `1920x1080` **zostają z moda**,
* rozmiar wyniku 882 978 B, 17 bloków, tylko 36 obiektów `MonoBehaviour` zmienionych,
* kopia zapasowa = plik z moda; `restore()` oddaje plik **co do bajtu**.

## Co to znaczy dla Ciebie w praktyce

1. Zainstaluj mod 4K tak, jak każe jego autor.
2. Uruchom `INSTALUJ.bat` na tej samej grze. Patch sam wykryje pliki z moda
   i wypisze: `Tryb nakładki: N z M plików nie jest z wersji 1.4.0 (mod 4K)`.
3. Menu będzie po polsku **i** w 4K — tekstury pochodzą z moda, tekst z patcha.
4. `COFNIJ.bat` przywraca stan sprzed patcha, czyli moda bez polskiego tekstu.

Kolejność „patch PL, potem mod 4K” nadal nie działa i działać nie może: mod
nadpisuje cały bundel razem z tekstem. Kolejność ma być **mod, potem patch**.

## Czego nadal nie wiemy

1. **Pozostałe pakiety moda** (Battle Event Animations, Effects, Story Event
   Backgrounds, Character Art — razem ~60 GB). Sprawdzony jest jeden bundel
   z tekstem; jeśli inny pakiet nadpisze bundel ze scenami, patch też go
   przyjmie (ta sama droga), ale **nie zostało to zmierzone** na pliku.
2. **3D/map textures** — autor moda ich nie adresuje, więc nie ma powodu, żeby
   kolidowały z tekstem.

Ryzyko jest ograniczone: patch podmienia tylko obiekty tekstowe i przed
zapisem sprawdza, że każdy z nich nadal ma oczekiwaną nazwę i `path_id`.
