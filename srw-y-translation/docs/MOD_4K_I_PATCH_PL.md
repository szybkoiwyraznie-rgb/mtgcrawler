# Mod 4K + patch PL: gdzie leży problem i co da się zrobić

Data: 2026-11-13. Autor: sesja agenta. Status: **diagnoza, brak zmian w kodzie**.

## Objaw

Po zainstalowaniu moda *4K Visual Overhaul* (Nexus, mod 2) `INSTALUJ.bat`
patcha PL kończy się natychmiast:

```
BŁĄD: aa/StandaloneWindows64/2d69c099bfdf0e252dabe84dbbba11df.bundle:
brak lub inna wersja pliku; gra nie została zmieniona
```

## Co ten komunikat naprawdę znaczy

`tools/patcher_y.py::install()` (i `check()`) **przed** jakimkolwiek zapisem
porównuje SHA-256 każdego z 488 bundli z `PLAN_PL9.json` z plikiem w grze.
Nazwa pliku jest nazwą skrótu treści (`2d69c099…` = skrót ścieżki assetu w
Unity), więc każdy bundel jest sprawdzany po tożsamości, nie po zawartości.

Komunikat znaczy dokładnie: **ten plik nie jest już plikiem z gry 1.4.0**.
Patch PL jest związany z jedną, konkretną wersją plików (świadoma decyzja:
`STAN_PATCHA.json` + sumy w `PLAN_PL9.json`), więc zatrzymanie jest celowe.

## Dlaczego mod assetów 4K dotyka bundli z tekstem

Bo w SRW Y tekst **nie** leży w osobnych „plikach tekstowych”. Menu jest
w Unity UI, a Unity trzyma UI razem z jego teksturami w tym samym bundlu.

Zmierzona struktura indeksu (`data/game_text_bundle_index.json`, 686 bundli,
`scope: owner-srw-y-1.4.0-s6`):

| grupa | bundli | zawartość |
|---|---|---|
| `aa/StandaloneWindows64/` z tabelami UI | 12 | 36–253 tabele tekstowe: `skill_program_en-US`, `dic_text_pilot_en-US`, `option_parts_en-US`, `strategypart_pilotmess_en-US`, … |
| `aa/StandaloneWindows64/` ze scenami | 48 | 920 obiektów scen (scenariusz) |
| dodatki (`AnniversaryExpansionPack/`, `ExpansionPack/`, …) | 609 | sceny (≤ 74 KB/bundel) |

Bundel z komunikatu — `2d69c099…bundle`, 948 652 B — trzyma **36 tabel UI w
angielskim**. Pakiet „SRWY 4K - UI” (2,2 GB) to dokładnie te same bundel-e:
tekstury menu sąsiadują tam z tekstem menu. Autor moda sam pisze, że archiwa
„lump many different element types together and it's all or nothing”.

Scenariusz leży w innych, małych bundlach (`1c12bbab…`, 5,6 MB, 678 scen),
które mod UI prawdopodobnie zostawia w spokoju — ale `install()` sprawdza
wszystkie 488 plików z góry, więc wystarczy **jeden** nadpisany plik, żeby
przebieg się zatrzymał, zanim cokolwiek zostanie zapisane.

## Czego nie wiemy (i czego nie zgadujemy)

1. **Które bundel-e nadpisuje każdy pakiet.** Nexus wymaga konta do
   pobrania, a pliki mają 0,3–16,7 GB — nie da się ich pobrać w tej sesji.
2. **Czy nadpisane bundel-e zmieniają tylko `Texture2D`/`Sprite`/atlas, czy
   też obiekty tekstowe.** Jeśli tylko tekstury, to podmiana danych obiektów
   tekstowych na nowe jest mechanicznie możliwa (patcher i tak podmienia
   *surowe bajty* obiektów po `path_id`, nie cały plik) — ale wymaga
   przeliczenia sum i przetestowania na prawdziwym pliku z moda.
3. **Czy autor moda nie ruszył `path_id`** obiektów tekstowych (przy
   przebudowie Unity zachowuje `path_id`, ale nie ma tego zagwarantowanego).

## Cztery drogi (od najtańszej)

### A. Ta sama kolejność, odwrotnie: patch PL → mod 4K → z powrotem PL

Nie działa bezpośrednio: mod nadpisze bundel z tekstem, więc polski tekst
zniknie z menu. Wymaga **B** albo **C**.

### B. „Nakładka tekstu na mod”: bundel z moda + obiekty tekstowe z patcha

Jeśli mod zmienia tylko tekstury:

1. wziąć nadpisany bundel z gry (po modzie),
2. podmienić w nim surowe dane obiektów `MonoBehaviour` o `path_id` z
   `PLAN_PL9.json` na wersję po polsku **w tym samym formacie** (tabele
   tekstowe to zwykłe `MonoBehaviour`, więc `rebuild_plain` z
   `tools/srw_y_rebuild.py` już to potrafi),
3. zapisać wynik (LZ4HC + AES, jak `pack()`), zachowując tekstury moda.

To jest rozszerzenie patchera o tryb **„wykryj mod po sumie pliku i nałóż
tekst na jego wersję bundla”**, nie o wyłączenie weryfikacji.

### C. „Wersja robocza patchera”: pomiń sprawdzanie sum i licz na raport

Najszybsze do sprawdzenia, czy w ogóle zadziała, ale **nie do wydania**:
patcher buduje każdy bundel z tekstem od zera (nie modyfikuje oryginału),
więc wynikowy plik nie zawierałby tekstur moda — nadpisałby je z powrotem
wersją 1.4.0. Do tego każda zmiana sumy jest dokładnie tym, czego patch
unika („źle trafiony plik = zepsuta gra”).

### D. Rozdzielić pracę: mod przez MO2, patch PL na „gołą” grę

Dla osoby z modem: gra w folderze nietknięta, patch PL nałożony na nią,
mod 4K jako **drugi** mod w MO2 z wyższym priorytetem — ale wtedy mod
przykrywa bundel-e z tekstem i polski tekst znika w menu. Odwrotna
kolejność (patch PL jako mod z wyższym priorytetem) daje tekst PL, ale
tekstury UI wracają do 1080p.

## Co realnie trzeba pobrać (żeby nie zgadywać)

Cały patch PL dotyka **488 plików / 39,7 MB** — to jedyne pliki, o które
naprawdę chodzi, i można je skopiować niezależnie od tego, co mod nadpisał:

| co skopiować | pliki | rozmiar |
|---|---|---|
| bundel-e z tabelami UI (`aa/...`) | 10 | 2,4 MB |
| bundel-e ze scenami używanymi przez PL9 razem z `aa/` | 461 | 15,6 MB |
| **dodatki** (`AnniversaryExpansionPack/`, `ExpansionPack/`, `Dlc1/`, `Dlc2/`, …) | 405 | 4,8 MB |

**Najprostsza droga (bez MO2):**

1. W Steam: prawy klik na grę → *Właściwości* → *Zainstalowane pliki* →
   *Sprawdź spójność plików gry*. To przywraca pliki 1.4.0 i usuwa mod.
2. `INSTALUJ.bat` — patch PL wchodzi, `.srwy-original.bak` obok każdego pliku
   to **czysta** gra 1.4.0 (dokładnie ta wersja, na której patch był testowany).
3. Skopiować **488 plików patchowanych przez PL9** (tabela wyżej) do pustego
   folderu poza grą. Lista ścieżek jest w repo:
   `data/pl9_patchowane_pliki.txt` (488 linii, wygenerowana z `PLAN_PL9.json`).
4. Dopiero teraz zainstalować mod 4K. Kopie z punktu 3 są nietknięte, bo leżą
   poza grą.
5. Wysłać nam **jeden plik** — `2d69c099…bundle` z moda (948 652 B w 1.4.0,
   po modzie pewnie podobny rozmiar) — i najlepiej drugi, `1c12bbab…bundle`
   (5,6 MB, sceny). To wystarczy, żeby sprawdzić `path_id`, nazwy obiektów
   tekstowych i to, czy tekstury siedzą w tym samym bundlu.

**Jeśli mod jest w MO2** (zalecany sposób przez autora moda):

1. W MO2 odznaczyć mod 4K (albo wyłączyć wirtualizację) i uruchomić
   `INSTALUJ.bat` z `--game` na katalog gry — patch wejdzie na czyste pliki.
2. Skopiować te same 488 plików do folderu poza grą.
3. Włączyć mod 4K z powrotem.

## Czego potrzebujemy, żeby ruszyć dalej

Minimum, żeby dało się to zrobić **bez zgadywania**:

1. **Jeden nadpisany bundel z moda** — najlepiej `2d69c099…bundle` po
   instalacji pakietu „UI” (948 652 B w 1.4.0). Wystarczy ten jeden plik;
   jeśli mod zmienia też bundel ze scenami, drugi: `1c12bbab…bundle`.
2. Albo **lista ścieżek** z archiwum moda (7z/zip) — same nazwy plików i
   rozmiary, bez zawartości.

Po otrzymaniu pliku: sprawdzimy, czy `path_id` i nazwy obiektów tekstowych
się zgadzają, czy tekstury są w tym samym bundlu, i dopiero wtedy wybierzemy
B albo C.
