# SRW OE — English fan translation

Fanowskie tłumaczenie **Super Robot Taisen: Operation Extend** (PSP, `NPJH50521`,
japońska wersja 1.08) na język angielski. Repozytorium zawiera kompletne narzędzia,
pakiet tłumaczenia oraz **kit one-click** (`PATCH.bat`), który z Twojej własnej kopii
gry budzi patch do PPSSPP.

> **Ważne:** to projekt fanowski i niekomercyjny. Nie zawiera i nie dystrybuuje
> danych gry (ISO, DLC, zasobów). Wymaga własnej, oryginalnej kopii japońskiej
> wersji 1.08. Nie jest powiązany z Bandai Namco.

---

## Szybki start

1. Pobierz najnowsze wydanie z zakładki **Releases** (`srw-oe-translation-vNN.zip`).
2. Rozpakuj do dowolnego folderu i uruchom **`PATCH.bat`**.
3. Wskaż w oknach wyboru: swoje **ISO 1.08** oraz folder **DLC** (`NPJH50521`).
4. Z folderu `output\`:
   - `patched.iso` → odpal w PPSSPP (File → Load…),
   - `DLC\` → skopiuj całość do `memstick\PSP\GAME\NPJH50521\` (nadpisując).

Wymagania: Windows 10/11, [PPSSPP](https://www.ppsspp.org/). Python i Pillow
instalują się same (skrypt poprowadzi). Pełna instrukcja: [`srw-oe-translation/README_DIST.md`](srw-oe-translation/README_DIST.md).

## Co jest po angielsku

- scenki i **dialogi misji** (z nazwami mówców), teksty bitewne z mówcami,
- nazwy postaci, mechów i broni + encyklopedie z biogramami,
- przedmioty z opisami efektów, umiejętności, pomoc i całe menu/UI,
- komunikaty systemowe oraz **napisy wpisane w grafiki interfejsu**,
- napisy w programie gry (EBOOT.BIN).

Narracja, nazwy misji i interfejs czytają się po angielsku od rozdziału 1
(japońska baza + DLC rozdziałów 2–8). Cytat kwestii okna dialogowego ma
japoński kształt typograficzny `「…」` — to element struktury silnika.

## Jak to działa

Narzędzia czytają Twoje pliki (ISO + DLC) i zapisują **nowe** kontenery:
`patched.iso` oraz podmienione `EDAT`. Teksty pochodzą z pakietu
[`srw-oe-translation/pakiet_EN/`](srw-oe-translation/pakiet_EN/) (pary `jp → en`).
Żadne oryginalne pliki nie są modyfikowane na miejscu; danych gry w repo nie ma.

## Struktura repozytorium

| Ścieżka | Zawartość |
|---|---|
| `srw-oe-translation/` | projekt tłumaczenia: narzędzia (`tools/`), pakiet (`pakiet_EN/`), specy ikon (`ui_labels/`), testy (`tests/`) |
| `srw-oe-translation/docs/` | dokumentacja: [`GOAL`](srw-oe-translation/docs/GOAL.md), [`ROADMAP`](srw-oe-translation/docs/ROADMAP.md), [`METHOD`](srw-oe-translation/docs/METHOD.md), [`COVERAGE`](srw-oe-translation/docs/COVERAGE.md), dziennik [`EXPERIMENT_LOG`](srw-oe-translation/docs/EXPERIMENT_LOG.md), bieżący [`STATUS`](srw-oe-translation/docs/STATUS.md) |
| `srw-oe-translation/tests/` | testy jednostkowe narzędzi (`python -m pytest srw-oe-translation/tests`) |

Wydania (`Releases`) buduje automatycznie workflow
[`.github/workflows/release.yml`](.github/workflows/release.yml) — przy każdym
scaleniui PR do `main` oraz ręcznie (zakładka Actions → *Release PATCH* → *Run workflow*).

## Historia

Repozytorium powstało jako `mtgcrawler` — robocze środowisko badawcze; projekt
tłumaczenia żyje w wydzielonym katalogu `srw-oe-translation/` od pierwszego dnia.
Pełna historia prac (setki eksperymentów z hashami i wnioskami) jest w
`srw-oe-translation/docs/EXPERIMENT_LOG.md`.
