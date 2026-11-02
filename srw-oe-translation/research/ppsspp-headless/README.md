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

## Wynik wariantu bez LIBRETRO (2026-11-02)

Kompilacja wariantu bez LIBRETRO zakończyła się powodzeniem, a test `pspautotests/tests/cpu/cpu_alu/cpu_alu.prx --graphics=software --compare` dał 1/1. Serwer początkowo zawieszał się przed przyjęciem żądania, bo próbował zarejestrować się w sieci; w wariancie badawczym wyłączono zdalną rejestrację. WebSocket po poprawce odpowiada na `game.status`, `cpu.status`, `cpu.resume`, `input.buttons.press` i `memory.read`. `gpu.buffer.screenshot` nie zwrócił obrazu. Z zastrzeżeniem adresu, formatu i możliwego braku synchronizacji odczytano bezpośrednio pamięć VRAM: widać ekrany startowe i prośbę o wciśnięcie kółka. To nie jest dowód dojścia do listy pilotów ani wpływu zmian w ich słownikach. W logu pozostają m.in. błędy HLE PSN i semaforów.

`PPSSPP_RESEARCH_THROTTLE=1` dodaje eksperymentalną pauzę 10 ms w pętli headless w celu sterowania; nie gwarantuje rzeczywistej prędkości PSP, a tym bardziej zgodności czasowej. CPU test wykonano bez tej opcji. Ten build nie był jeszcze testowany przez uruchomienie całego skryptu od zera.

## Odczyt kontrolny pamięci wideo

`probe_oe.py` jest narzędziem diagnostycznym dla tego konkretnego eksperymentu (adresy 0x04000000 i 0x04044000, stride 512, 5551). Wymaga Pythona, `websocket-client` i `Pillow` (sprawdzono odpowiednio 1.9.2 i 13.0.0). Na przykład, po przygotowaniu **oddzielnej kopii** HOME i zawartości `.ppsspp`, można wskazać nowy prywatny katalog wynikowy:

```sh
python research/ppsspp-headless/probe_oe.py --binary /sciezka/do/PPSSPPHeadless \
  --iso-copy /sciezka/do/kopii.iso --home-copy /sciezka/do/izolowanego-home \
  --output /sciezka/do/nowego-katalogu --samples 10 --interval 2 \
  --press-circle --accept-local-debugger-risk
```

Przełącznik ryzyka wolno podać dopiero po upewnieniu się, że debugger nie jest osiągalny spoza izolowanego środowiska. Katalog wynikowy musi nie istnieć; obrazy zawierają dane gry i nie mogą trafić do Git. Oba zrzuty mogą być nieaktualne lub rozdarte, bo odczyt nie wybiera aktywnego bufora i nie synchronizuje się z klatką. Próba nie stwierdza automatycznie, jaki ekran jest widoczny, czy gra jest stabilna ani czy tłumaczenie działa. `--press-circle` jest opcjonalne; bez niego program nie wysyła przycisków.
