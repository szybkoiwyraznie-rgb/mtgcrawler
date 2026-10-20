# Aktualizacja buildera EN i PL — Masaki i kontrola DLC PL

Ten sam ZIP aktualizuje narzędzia w istniejącym builderze angielskim lub polskim.
Nie jest pełnym patchem gry ani nowym kompletnym tłumaczeniem PL.

1. Zamknij uruchomiony builder i zrób kopię swojego folderu buildera.
2. Rozpakuj zawartość ZIP-a **do folderu, w którym masz PATCH.bat**.
   Zezwól na zastąpienie plików w `tools/`. Nie twórz dodatkowego podfolderu.
   Przy dwóch osobnych builderach EN i PL wykonaj ten krok w obu folderach.
3. Uruchom swój dotychczasowy `PATCH.bat` jak zwykle, na swoich oryginalnych
   plikach gry. Zastosuj nowy wynik tak samo jak poprzedni patch.

ZIP nie zawiera plików gry, fontów, save'ów ani katalogu `translation/`.
Nie zastępuje launcherów ani Twoich przekładów: EN korzysta z EN, PL z PL.
Samo rozpakowanie aktualizuje builder, nie zmienia już zbudowanego ISO/DLC.

Poprawka wchodzi automatycznie w zwykły build. Dotyczy wyłącznie istniejących
pól aktora głosowego, etykiet i krótkich imion trzech postaci w config19.
Nie odblokowuje pustych pól ani innych configów. Builder sprawdza wynikowe
bajty przed zapisaniem poprawionego kontenera; raport zawiera
`character_viewer_fix` / `readback_ok`.

Wersja EN odpowiada poprawce TEST1 zaakceptowanej w grze. Wspólna ścieżka PL
używa polskiego pakietu, nie angielskich tekstów zaszytych w narzędziu.
Brakujące pola PL nie są automatycznie wypełniane angielskim tekstem.
Nie oznacza to testu wszystkich ekranów czy rozdziałów.

W PL nadal obowiązują normalne limity bezpieczeństwa, w tym limit rozmiaru
Skill00. Aktualizator nie rozwiązuje nadmiernej długości zwróconych umiejętności;
nie omija tego ograniczenia i nie skraca literacko tekstu tłumacza.

`BUILDER_TOOLS.json` podaje wersję i sumy SHA-256 dołączonych narzędzi.
Aktualizacja zawiera pełny zestaw ich zależności, nie tylko jeden skrypt.

Aktualizacja po audycie PL2 obejmuje również odczyt kontrolny tytułów DLC
rozdziału 4 kodekiem aktywnego języka. Poprzednia kontrola CP932 błędnie
odrzucała poprawne polskie bajty. Nadal sprawdzane są oba pola tytułu, opis
i identyfikatory DLC; kontrola nie jest wyłączana.
