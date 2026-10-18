# Super Robot Wars OE — Polish Translation Patch (v1)

Fanowskie tłumaczenie gry **Super Robot Wars OE** (PSP) na język polski.
Tekst bazuje na kompletnym tłumaczeniu angielskim (patch v17) przetłumaczonym
na polski; polskie znaki diakrytyczne są dodawane do fontu gry.

> **v1 (PL):** pierwszy kit polski. Font gry (`font.cpk`) jest rozszerzany o 18 glifów
> (ą ć ę ł ń ó ś ź ż oraz wersaliki) — to dzieje się automatycznie w trakcie patchowania,
> niczego nie trzeba wgrywać osobno. Tłumaczenie tekstu jest w trakcie (pole `pl`
> w pakiecie); wiersze jeszcze nieprzetłumaczone zostają po japońsku/angielsku.

---

## Co jest potrzebne

| Wymaganie | Uwagi |
|---|---|
| **ISO gry** | `SRW OE 1.08.iso` — własna, legalnie zdobyta kopia. **Wymagane** — font patch działa na pliku z płyty |
| **Pliki DLC** (opcjonalnie) | Odszyfrowany folder DLC (`NPJH50521`) z rozdziałami 2–8 |
| **PPSSPP** | Emulator PSP — https://www.ppsspp.org/ |
| **Windows 10/11** | Patcher to skrypt `.bat` |
| **Python 3.8+** | Instaluje się sam, jeśli brak (przez `winget`) |
| **Pillow** | Biblioteka obrazów Pythona — instaluje się sam |

## Szybki start

1. **Rozpakuj** archiwum do dowolnego folderu (np. `C:\Gry\SRW-OE-Patch-PL\`).

2. **Kliknij dwukrotnie `PATCH.bat`**. Skrypt:
   - sprawdzi Pythona i Pillow (dograi je, jeśli trzeba),
   - poprosi o **wybranie ISO gry** (okno wyboru pliku),
   - poprosi o **wybranie folderu DLC** (albo Anuluj, aby pominąć DLC),
   - zbuduje pliki patcha — w tym kroku **rozszerza font gry o polskie glify**
     (rekompresja `font.cpk` chwilę trwa, to normalne).

3. **Wynik** znajdziesz w podfolderze `output\`:
   | Plik | Co z nim zrobić |
   |---|---|
   | `patched.iso` | Otwórz w PPSSPP (File → Load...) — zawiera też polski font |
   | `DLC\` | Skopiuj **pliki ze środka** do istniejącego `memstick\PSP\GAME\NPJH50521\` |
   | `build_report.json` | Szczegóły techniczne (niepotrzebne do grania) |

4. **Zachowaj kopie zapasowe i istniejące save'y.** Buduj na oryginalnym
   japońskim ISO i odszyfrowanym DLC — nie na wcześniejszym spatchowanym ISO
   ani na mieszance oryginału ze starymi wynikami. Pliki z `output\DLC\`
   nakładaj na kompletny, zainstalowany folder DLC (bez zagnieżdżania
   dodatkowych podfolderów i bez usuwania nietkniętych plików).

5. **Uruchom grę na zimno** z nowym `patched.iso`, potem wczytaj zwykły save
   z gry. Stary save-state emulatora może trzymać w RAM stare zasoby.
   Nie trzeba usuwać zapisów gry.

## Co jest po polsku, a co nie (stan v1)

- **Dialogi, cytaty bojowe, przedmioty, umiejętności, teksty UI, misje,
  imiona, jednostki, bronie** — tłumaczone z polskiego pakietu `translation\`
  (pole `pl`). Wiersze jeszcze puste zostają w oryginale — patch jest
  częściowy z założenia, dopóki pakiet nie zostanie w całości wypełniony.
- **Font** — 18 polskich liter doklejonych do `kanji.fta`; reszta fontu
  nietknięta bajt w bajt.
- **Stringi w programie gry** (`EBOOT`) — tylko ASCII: tam, gdzie polski
  tekst użyłby diakrytyków, build odmawia wiersza i zapisuje powód
  w `build_report.json` (sekcja `executable`).
- **Podpisy terenu** — tylko ASCII, max 12 znaków (limit komórek ekranowych).
- **Napisy w teksturach UI** — rysowane z `ui_labels\`; spec-y mogą dostać
  pole `pl` (fallback: angielski).

## Znane ograniczenia

- Polska litera zajmuje na ekranie pełną szerokość (jak znak japoński):
  limit 46 jednostek na linię dialogu jest pilnowany przez build.
- Wiersze odrzucone (za długie, niekodowalne, niespójne tokeny) NIE psują
  całości — zostają oryginalne, a powód jest w `build_report.json`.
- Rozmiar: `patched.iso` rośnie (dopisywanie zmienionych memberów);
  `lmap.cpk` po przebudowaniu ~156 MB. Miej **min. 3 GB** wolnego miejsca.

## Struktura folderu po rozpakowaniu

```
PATCH.bat              ← uruchom to
CHECK_DLC.bat          ← diagnostyka DLC (tylko odczyt)
README.md              ← ten plik
translation\           ← pakiet tłumaczenia (JSONL, pole "pl")
tools\                 ← skrypty budujące
ui_labels\, assets\    ← specyfikacje napisów w teksturach UI
```

## Zgłaszanie problemów

Przy problemach wyślij `output\build_report.json` (zawiera listę odrzuconych
wierszy z powodami). Gdy po instalacji DLC nazwy rozdziałów są nadal
japońskie — uruchom `CHECK_DLC.bat` na **zainstalowanym** folderze NPJH50521
i prześlij `DLC_TITLE_CHECK.json`.
