# Eksperymentalny warsztat PPSSPP bez okna

To narzędzie badawcze dla Linux x86-64, **nie część wydawanego patchera** i nie dowód bezpieczeństwa patcha. Żadnych plików gry ani zrzutów ekranu nie ma w repozytorium. Buduj i uruchamiaj wyłącznie na kopiach ISO, DLC i osobnego katalogu domowego/emulowanych zapisów.

## Budowanie

Potrzebne: bash, git, C/C++ compiler i make, CMake (lokalnie użyto wydania z pakietu Python `cmake`), możliwość pobierania repozytoriów GitHub wraz z podmodułami i miejsce na kilka GB. PPSSPP i podmoduły mają własne licencje; pobiera się je z upstream, bez kopiowania do tego repozytorium. Odtworzenie wymaga wersji i zależności dostępnych dla systemu użytkownika. Skrypt nie instaluje ich automatycznie.

```sh
research/ppsspp-headless/build.sh local/nowy-warsztat-ppsspp
```

Katalog docelowy musi nie istnieć. Skrypt pobiera PPSSPP 1.20.4, commit `fa50bb1976065c4f8b1b47af227d367fe9771555`, jego podmoduły z przypiętych przez upstream commitów oraz nagłówki OpenGL Registry `6af574a14089ccfee87efe230ebcdd8742859813` i EGL Registry `e964211ff5f7c2bcada786954a16d5b813379395`. Stosuje lokalny tekstowy patch i buduje `PPSSPPHeadless`; `JOBS` kontroluje równoległość. Wersje upstream i lokalne zmiany są istotne dla interpretacji wyników; nie jest to oficjalny build PPSSPP.

## Ograniczenia i bezpieczeństwo

- Funkcje GL/EGL zastąpiono atrapami kończącymi proces przez `abort()`. Używać wyłącznie `--graphics=software`. GPU, filmy, biblioteki PSP i obsługa usług mogą zachowywać się inaczej niż w normalnym PPSSPP.
- Patch wiąże serwer HTTP/debuggera z adresem loopback, ale **nie jest uwierzytelniany** i może odczytywać/zapisywać pamięć gry. Środowiska kontenerowe lub pośredniki mogą mimo to udostępnić port na zewnątrz. Nie używać debuggera bez sprawdzenia całej ścieżki sieciowej lub izolowanej przestrzeni sieciowej. Nie wystawiać go publicznie.
- `--timeout` może skończyć się statusem 0 mimo przerwania testu: trzeba niezależnie odczytać wynik, log i stan gry. `--log` może wygenerować setki MB w kilka sekund; ograniczać i filtrować strumień.
- Emulator nie jest dowodem przejścia gry ani bezpieczeństwa zapisów. Należy osobno raportować kontrolę CPU, uruchomienie gry, ekran docelowy, porównania oraz ograniczenia. W żadnym razie nie zdejmować bramki config na podstawie samego uruchomienia.

Wcześniejszy lokalny wariant z mostem LIBRETRO przeszedł pojedynczy test CPU i znalazł moduł w naprawionym obrazie, ale nie dotarł do ekranu pilotów; jego wynik nie jest dowodem dla tego wariantu bez LIBRETRO. Status budowy i prób należy sprawdzić w `docs/EXPERIMENT_LOG.md`.
