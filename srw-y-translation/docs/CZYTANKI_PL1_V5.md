# Czytanki PL1 v5 — odtworzenie

Czytanki w `docs/reading/pl1-v5/` zawierają pierwszą zwrotkę z poprawkami zaakceptowanymi w patchu v5, nie całą grę. `rozdzial-01.md` i `rozdzial-02.md` obejmują pliki scen zawierające co najmniej jedną przetłumaczoną kwestię dla wybranego wariantu bohatera; pozostałe kwestie w tych scenach oznaczono jako braki. Nie ma cytatów bitewnych ani kolumn JP/EN. Domyślnie wybierany jest męski protagonista, żeński tylko gdy w misji nie ma męskiego wariantu; wspólne kwestie zostają. W tej zwrotce wszystkie 954 niewykorzystane polskie wiersze scen należą do pominiętego wariantu żeńskiego. Kolejność literałów Lua jest zweryfikowana; nie jest to dowód kolejności rozgrywania zdarzeń i misji.

`deployment.md` wymienia uczestników wynikających z presetów oraz osobno postacie dialogów, nie przewiduje momentu wejścia do walki. Przy pierwszym wystąpieniu podaje biografię lub opis z encyklopedii, jeżeli istnieje potwierdzone powiązanie. Statystyki bazowe, umiejętności i rozkazy ducha podano przy pierwszym wystąpieniu konkretnego rekordu w danym wariancie danych; postaciom wyłącznie dialogowym nie przypisujemy statystyk na podstawie podobieństwa nazw. Sloty wyboru i dynamiczne referencje pozostają niewiadomymi. `piloci.md`, `mechy.md` i `encyklopedia.md` są dodatkowymi indeksami.

Plan importu zawiera 26 279 wypełnionych slotów / 29 873 wystąpienia i 22 korekty. Layout v5 może w niektórych polach UI różnić się separatorami wierszy; czytanki bazują na zweryfikowanym planie tekstowym, a nie na mechanicznym formatowaniu ekranu gry. W tym wydaniu wykazano 6670 unikalnych braków tekstu lub powiązań, w tym 3172 nieprzetłumaczone wiersze scen; wiele dotyczy nieprzetłumaczonych pól, nierozwiązanych identyfikatorów lub rekordów bez wpisu encyklopedii. Nie są one wymyślane ani zastępowane tekstem źródłowym.

## Pełna regeneracja z repozytorium

Od katalogu `srw-y-translation/`, z Pythonem i zależnościami warsztatu (`docs/WARSZTAT_PL_Y.md`):

```sh
mkdir -p local/pl1-reading
python tools/bind_v8_return.py --input translations/pl1/PL \
  --output local/pl1-reading/manifest.json
python tools/audit_full_return.py --manifest local/pl1-reading/manifest.json \
  --input translations/pl1/PL --source-dir data/s6-full \
  --corrections translations/pl1/CORRECTIONS.json \
  --historical-quarantine translations/pl1/QUARANTINE.json \
  --output-plan local/pl1-reading/v5-plan.json \
  --output-report local/pl1-reading/audit.json
cmp local/pl1-reading/audit.json translations/pl1/AUDIT_LAYOUT_V5.json
python tools/build_reading_y.py --source-dir data/s6-full \
  --index data/reading-index-sourcebound.json \
  --translations local/pl1-reading/v5-plan.json --translated-scenes-only \
  --out local/pl1-reading/edition \
  --evidence data/dictionary_owner_assets.json --links data/dictionary_links.json \
  --graph-evidence data/script_graph_evidence.json \
  --preset-evidence data/preset_evidence.json \
  --final-preset-evidence data/final_preset_evidence.json
```

Katalog wyjściowy nie może już istnieć. Zawiera pliki Markdown, deterministyczny `srwy_reading_PL.zip` i pełną `receipt.json`. Dla tego wydania SHA-256 ZIP to `702ed87e6507c33abadd204cfc49542af87f4d4b895a7e0edc515da0faf03a33`. `receipt-summary.json` w repo zawiera skrót audytu. Dwa niezależne przebiegi dały identyczny ZIP i pełną receptę; skompaktowany i pełny indeks dały identyczną treść sześciu plików głównych.

## Indeks i źródła binarne

`data/reading-index-sourcebound.json` to tekstowy indeks bez bundli, związany sumami z `data/s6-full/`. Zachowuje jedną rzeczywistą, sprawdzoną wersję Lua na każdy z 966 plików źródłowych, potrzebną do ponownego sprawdzenia tekstu, kontekstu i porządku; generator odrzuca zmieniony korpus. Nie zawiera wszystkich alternatywnych rewizji i nie zastępuje pełnego indeksu do nowych analiz źródeł. Zachowuje dane misji, presetów, rekordów i lokalizacji. Dowody i narzędzia są w repo; binarne assety gry pozostają poza nim.

Jeśli potrzebna jest przebudowa indeksu od podstaw, użyj instrukcji w §11 `docs/HANDOFF_READING_WYNIKI_2026-10-27.md` z oryginalnymi bundlami: pełny indeks ma SHA-256 `b1b1c368212296123842d17079f314fd0e0330e249dcf0973c15901ea20ab478`. Potem:

```sh
python tools/compact_reading_index.py --source-dir data/s6-full \
  --index local/reading-research/context-index-final.json \
  --out local/reading-research/reading-index-sourcebound.json
```

Wynikowy indeks ma SHA-256 `864df220de7ec00a760daf0fc6924b57abeeba3bdaebdb6ef0124e658e1b8f87`. Odtwarzanie czytanek z pełnym indeksem też jest możliwe, ale indeks jest znacznie większy. Wszystkie 91/91 wskazań presetów zostało rozwiązanych; nie oznacza to, że każda dynamiczna referencja uczestnika została rozstrzygnięta.
