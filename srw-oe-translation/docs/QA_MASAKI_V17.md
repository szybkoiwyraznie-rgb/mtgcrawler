# v17 — mieszane języki w Library → Characters dla Masakiego

**Potwierdzenie właściciela, 2026-10-18:** po podmianie testowego config19
„wszystko pięknie przetłumaczone”. Poprawka wyświetlanych pól na zgłoszonym ekranie
zaakceptowana. Poniższe opisy oczekiwania na test dokumentują wcześniejszy etap.
Nie jest to test wszystkich rozdziałów ani zgoda na globalne zdjęcie blokady.
Wąską poprawkę należy zachować przy następnym pełnym wydaniu; standardowy builder
nie został jeszcze zmieniony tak, aby stosował ją automatycznie.

**2026-10-18, PR #20.** Zgłoszenie właściciela: po misji 0-0 i zastosowaniu bonusów
DLC na ekranie Character Viewer lista Masaki/Shiro/Kuro jest japońska, pełne imię
Masaki Andoh i seria są angielskie, podpis pseudonimu JP + wartość Masaki EN,
aktor i jego podpis JP. Zrzut jest prywatny, nie w repozytorium.

## Przyczyna odtworzona w danych

Pobrano **faktycznie dostarczony ZIP v17**, SHA256 zgodny z manifestem:
`5afdd00fec393edba9bc76371e4283cc17c5cc90cd05eab0b6a711b7bec87937`.
Jego własny builder, nie zastępczy aktualny, zbudował oryginalne `config19.EDAT`
i `imenu19.EDAT`: 0 problemów. Oryginalne pule CharaDictionary19 są identyczne.

| Pole rekordu | config19 po v17 | imenu19 po v17 |
|---|---|---|
| 0 — pełne imię | EN | EN |
| 3 — seria | EN | EN |
| 4 — pseudonim z podpisem | podpis JP, wartość EN | całość EN |
| 1 / 5 — aktor bez/z podpisem | JP | EN |
| 11 — krótka nazwa do listy | JP | EN |

Dotyczy kluczy **4420, 4424, 4426**. Układ po stronie config19 odpowiada dokładnie
zgłoszonemu zrzutowi. To mocny dowód wyboru tej kopii w tym przebiegu UI, **nie ślad
wykonania ani dowód adresu aktualnie czytanego przez grę**.

Angielskie wartości istnieją w pakiecie. Wyłącza je
`build_translation_patch.CONFIG_DICT_SPARE_CATEGORIES`: globalna blokada aktorów,
krótkich nazw i podpisów po wcześniejszych crashach poszerzonych słowników config01–08.
W reprodukcji blokada zatrzymuje 326 wierszy dla config19, m.in. te pola.
Stare założenie „Character Viewer zawsze czyta imenu” nie jest bezpieczne.
To nie brak pracy polskiego tłumacza ani problem polskiej czcionki.
Nie ustalono, w której wcześniejszej wersji objaw pojawił się po raz pierwszy.

## Wąska poprawka TEST1 — runtime do potwierdzenia

**Nie wyłączono globalnej blokady i nie wydano v18.** Narzędzie
`tools/masaki_viewer_test.py` bierze bazę EN zbudowaną v17 i jego pakiet tekstów.
Poprawia wyłącznie **istniejące pola 1, 4, 5, 11** trzech wskazanych postaci.
Nie wpisuje danych do pustych pól 6/7/10, nie zmienia szablonów 2/8/9, identyfikatorów,
innych rekordów ani innych podplików kontenera. Rozpoznaje dokładny wzorzec v17
lub poprawione pola; inne dane odrzuca. Nie dotyka PL, umiejętności, EBOOT ani ISO.

Odczyt po zapisie:

- **12 zmienionych pól**, wszystkie pozostałe zachowane;
- słownik **658 → 706 B** (+48 B), nadal 3 rekordy;
- cały `config19.EDAT` **32 896 → 32 896 B** (zapas wyrównania);
- **10 pozostałych podplików bajtowo bez zmian**;
- poprawiony słownik jest **bajtowo identyczny z już angielskim słownikiem imenu19
  zbudowanym przez dostarczony v17**;
- bazowy v17 `config19.EDAT` MD5 `514434967daacf1afd588378794c1b20`;
- testowy `config19.EDAT` MD5 `077d4b17529f0d2d6d80ef8706935dc8`.

Poprawka jest eksperymentalna: nawet istniejące pola wymagają potwierdzenia w grze,
bo dokładnej przyczyny dawnych awarii słowników nie wyizolowano. Mały przyrost i
niezmieniony rozmiar kontenera nie gwarantują bezpieczeństwa każdej alokacji gry.

## Proste sprawdzenie u właściciela

1. Zamknąć grę. Zachować kopię obecnego **`config19.EDAT` poza aktywnym folderem DLC**.
2. W używanym folderze DLC zastąpić **tylko ten jeden plik** plikiem z testowej paczki.
   `imenu19.EDAT`, ISO, pozostałe DLC i zapisy pozostają bez zmian.
3. Zimny start PPSSPP, wczytać zwykły zapis gry — nie save state emulatora — i wrócić
   do tego samego Library → Characters. Nie potrzeba nowej gry ani nowego ISO.
4. Wystarczy screenshot tego samego ekranu. Oczekiwane: lista Masaki/Shiro/Kuro,
   `Nickname: Masaki`, `Voice: Hikaru Midorikawa`.
5. W razie crasha przywrócić kopię jednego pliku. Nie usuwać i nie nadpisywać sejwów.

## Odtworzenie budowy

Najpierw zbudować `config19.EDAT` i `imenu19.EDAT` **oryginalnym kitem v17** z
oryginalnych kontenerów (EN). Następnie:

```text
python tools/masaki_viewer_test.py --baseline local/qa-masaki-v17/reproduced/DLC/config19.EDAT --package local/qa-masaki-v17/v17/translation --out local/qa-masaki-v17/nowy-test
```

Wyjście musi być nowe/puste. Oryginał i baza v17 nie są nadpisywane. Generowane
EDAT-y, pełne odczyty pól i screenshot są wyłącznie lokalne/prywatne. Do repo trafiają
narzędzie, syntetyczne regresje, ustalenia i manifest dostawy, nie binaria gry.

## Dostawa prywatna

[v17_MASAKI_TEST1.zip](https://drive.google.com/file/d/1RW-thcVUA7QcMLxG63eqBsejR8h3BZv5/view)
— 4307 B, zawiera tylko testowy `config19.EDAT`, krótką instrukcję i raport odczytu.
Pobrany z Drive ponownie: bajtowo identyczny, wszystkie CRC zgodne. Udostępniania
nie zmieniano. Binarium jest wyłącznie w prywatnej paczce, nie w GitHub.
[Manifest](masaki-v17-test1-delivery.json). SHA256 ZIP:
`11ab934011727393ac7c85163c7b6dfd99e217dc942a33d42603650787eb0b0f`.

Pełny zestaw po zmianach: **1610 testów OK, 28 pominiętych** (prywatne dane nieobecne
w tym środowisku). Odczyt oryginalnych config19/imenu19 i przygotowanej poprawki
został sprawdzony niezależnie od tych pominięć. Potwierdzenie gry po podmianie pliku
pozostaje otwarte. Nie należy z powodu tej próby włączać wszystkich pól configNN.

## Integracja zwykłego buildera EN/PL — zakończona 2026-10-18

Powyższa procedura TEST1 to historia zaakceptowanego eksperymentu; nie prośba
ponownego testowania tego samego ekranu. Zwykły `build_translation_patch.py`,
używany przez oba launchery, stosuje teraz tę poprawkę automatycznie:

- wyjątek tylko dla config19/srwDL_CharaDictionary19, dokładnie trzech znanych
  kluczy i istniejących slotów1/4/5/11; nieznany układ pozostaje za bramką;
- aktywny pakiet EN lub PL, bez zaszytego tekstu EN i bez fallbacku PL→EN;
- po pełnym łańcuchu przebudowy kontenera obowiązkowy odczyt fizycznych komórek;
- puste pola i szablony bez zmian; pozostałe configy/kategorie nadal chronione.

Zestaw **1620 testów OK, 28 pominiętych**, w tym zwykłe wejścia EN/PL, znaki
polskie, pusty PL bez EN fallbacku, nieznane rekordy/puste komórki, inne configy,
błąd odczytu i kompletność aktualizatora.

Dodatkowo na prywatnych oryginalnych config19/imenu19: rozpakowano rzeczywisty
kit v17 i nałożono aktualizator, uruchomiono jego CLI EN oraz PL. PL pochodzi
ze ścisłego source-stamped importu zwróconego PL.zip do osobnej kopii pakietu.
Oba przebiegi: 0 problemów, 8 zwolnionych wierszy, 12 fizycznych pól, readback OK.
**Cały wynikowy EN config19 jest bajtowo identyczny z zaakceptowanym TEST1**
(SHA256 `84525e62f258ec54b13cda6144d8758beae2125cdee6b986aaf7472f10da8951`).
Niezależnie porównano 24 komórki EN/PL z surowymi polami językowymi JSONL,
nie tylko z planem writera. Pola szablonów/puste bez zmian, pakiety i oryginały
nietknięte. PL różni się od EN zgodnie z dostarczonym PL, bez redakcji tekstu.
Miniaturowy ISO użyty do wejścia CLI to nie gra — nie ma nowej deklaracji
runtime ani testu wszystkich rozdziałów. Za długi Skill00 w PL nadal blokowany.

[BUILDER_EN_PL_MASAKI_UPDATE.zip](https://drive.google.com/file/d/1ssmlgTfscMTp-da2Ou_2t3STjua6h-f2/view)
— wspólna aktualizacja obu istniejących kitów, 257303 B / 45 plików, tylko
narzędzia z zależnościami + instrukcja/manifest. Nie nadpisuje translation/,
launcherów ani save'ów. Rozpakować obok PATCH.bat, zastąpić tools/ i budować
jak dotąd. Nie zmienia już zbudowanego ISO/DLC bez ponownego builda.
Download-back identyczny; CRC i SHA256 wszystkich narzędzi zweryfikowane.
[Manifest dostawy](masaki-builder-update-delivery.json). Brak binariów gry w GitHub.
