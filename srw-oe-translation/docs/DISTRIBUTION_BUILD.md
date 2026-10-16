# Procedura budowania pakietu dystrybucyjnego

## Kiedy budować

- Po każdej nowej wersji pakietu tłumaczenia (v10, v11, …)
- Po poprawkach w narzędziach (bug fix, nowa funkcja buildera)
- Po aktualizacji materiałów translatorskich (glossariusz, voice_cards)

## Co robić

### 1. Przygotuj pakiet tłumaczenia

```bash
# Upewnij się, że最新的 pakiet jest w local/pakiet_vN/
# (pobierz z Drive lub zbuduj lokalnie)
```

### 2. Zaktualizuj wersję

Plik `tools/build_distribution.py` automatycznie wykrywa wersję z `CO_NOWEGO_v*.txt`.
Jeśli chcesz ręcznie zmienić, edytuj zmienną `version` w skrypcie.

### 3. Zbuduj zipa

```bash
cd srw-oe-translation
python3 tools/build_distribution.py
```

Wynik: `local/dist/srw-oe-translation-vN.zip`

### 4. Przetestuj

1. Rozpakuj zipa do nowego folderu
2. Sprawdź, czy `PATCH.bat` się uruchamia (Python, Pillow)
3. Sprawdź, czy build kończy się sukcesem na testowym ISO
4. Sprawdź `build_report.json` — 0 błędów, 0 pominiętych

### 5. Opublikuj

Wrzuć zipa na Drive / GitHub Releases / gdziekolwiek dystrybuujesz.

## Co jest w zipie

```
PATCH.bat                   — launcher (one-click, Windows)
README.md                   — instrukcja dla użytkownika
translation/                — pliki JSONL + tokeny.tsv
  00_dialogue.jsonl         — dialogi
  01_battle_quotes.jsonl    — okrzyki bojowe
  ... (10 plików)
tools/                      — skrypty Python (35 plików)
  build_translation_patch.py — główny builder
  pick_path.py              — selektor plików (okno dialogowe)
  ... (33 transitive deps)
docs/translator/            — materiały dla tłumaczy
  glossary.json             — słownik postaci/serii/terminów
  voice_cards.md            — karty głosu postaci
  STYLE.md                  — przewodnik stylu
  bible/                    — streszczenia odcinków
  briefy/                   — instrukcje zadań
```

## Naprawy i aktualizacje

### Nowa wersja tłumaczenia

1. Umieść nowy pakiet w `local/pakiet_vN/`
2. Uruchom `python3 tools/build_distribution.py`
3. Nowy zip z nową wersją

### Poprawka w narzędziach

1. Napraw bug w `tools/*.py`
2. Uruchom testy: `python3 -m unittest discover tests -q`
3. `python3 tools/build_distribution.py` — zip automatycznie weźmie最新 tools

### Aktualizacja materiałów translatorskich

1. Zaktualizuj pliki w `docs/translator/`
2. `python3 tools/build_distribution.py`

## Ważne uwagi

- **Nigdy nie dodawaj** do zipa: gry ISO, plików DLC, lokalnych buildów, kluczy API
- `PATCH.bat` **musi** otwierać okno wyboru pliku (reguła użytkownika)
- Zip musi działać na czystym Windows 10/11 z Python 3.8+ (auto-instalacja)
- Testuj zipa na czystym środowisku (bez zainstalowanego Pythona), jeśli to możliwe