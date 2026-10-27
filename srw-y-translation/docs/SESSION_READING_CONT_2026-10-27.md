# Wznowienie czytanek SRW Y — checkpoint sesji (2026-10-27, sesja `arena/ff68be19-mtgcrawler`)

Cel właściciela (doprecyzowanie z 2026-10-27): dostarczyć **pliki `.md`** czytanek
SRW Y — **sceny, deployment, mechy, piloci** — analogiczne do wydań OE, ale
**rozszerzone o dane z encyklopedii Y**, zbudowane na danych przygotowanych dla
tłumaczenia. Nowy handoff ma jawnie wypisać, co nadal pozostaje niezrobione.

Kontynuacja [`HANDOFF_READING_Y_2026-10-27.md`](HANDOFF_READING_Y_2026-10-27.md):
priorytety A (biografie/opisy encyklopedii przy pierwszym wystąpieniu),
B (91 nierozwiązanych PPtr presetów), C (chronologia scen i wywołań zdarzeń)
oraz ograniczenia z sekcji D.

## Stan wyjściowy tego checkoutu (zmierzone, nie założone)

- Gałąź `arena/ff68be19-mtgcrawler` wychodzi z `main` = `d3e0f97` (PR #27
  scalony). Nie ma otwartego PR z tej gałęzi — zakładany jest draft PR.
- Katalog `srw-y-translation/local/` i `.venv/` **nie istnieją** w tym klonie:
  prywatne indeksy, zrzuty obiektów, korpus S6 i buildy diagnostyczne
  poprzedniej sesji trzeba odtworzyć z archiwów na Drive.
- Na Drive (folder `1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`) dostępne są wszystkie
  archiwa wejściowe wymienione w handoffie: `SRW_Y_MISSION.zip`
  (`15Bzc6K9DvaJqKH5S0wE9uR3hGs_pH-l7`, 685 573 B), `SRW_Y_GLOSY.zip`
  (`1rOZ30lS92VanYAexxZNayKU3-0RQgMZz`, 3 080 644 B), `srw_y_text.zip`
  (`11RHT7izprqiKEtNTLs2kOneSACUvYeqW`, 12 224 594 B), `srw_y_tekst.zip`
  (`1DFKONYYeRO-aQXpIvKQDVoAXmEam49xB`, 22 472 543 B),
  `srw_y_dlc_bundle.zip` (`1Jof_EGWnMjxCa7klPP76whZfd7FTDQJC`, 7 146 855 B),
  `srw_y_free_patch.zip` (`1NucgseGzZRGM0QqgZ2Gmf-IK_8mSF6tH`, 363 847 B),
  `srw_y_dlc_catalog.zip` (`16qmHBB5hhM1Zou09OUSaxyMipezM0FgF`, 2 884 114 B)
  oraz bazowy `catalog.json` (`1cSFIutg4pfL_KGimi4tab4_j29uC3s7N`,
  41 543 062 B).
- Na Drive **nie ma** prywatnych plików `complete-objects.json`,
  `base-text-objects.json`, `extra-objects.json`, `context-index.json`,
  `prerequisite-mode-audit.json` ani `restore_s6.py`. Wyszukiwanie po nazwach
  (`object|catalog|reading|audit|restore|context|dictionary`) zwróciło 5 plików,
  żaden z nich nie jest zrzutem obiektów — trzeba je odtworzyć z powyższych ZIP-ów.
- Na Drive **nie ma zwrotu od tłumacza**: jedyny plik z 2026-10-27 to
  `samples-b080-2026-10-27.zip`, który właściciel określił jako należący do
  innego projektu — jest ignorowany. Ostatni materiał dla tłumacza to
  `plik_dla_tlumacza_v8.zip` (`1N4RRwggKU6o8BWd-3LNpDqHXB98MqGih`,
  8 364 702 B) z pustymi slotami `PL:`.
- Repozytorium zawiera gotowe narzędzia `tools/reading_index.py`,
  `tools/build_reading_y.py`, `tools/reading_audit.py`, `tools/reading_events.py`,
  `tools/pl_import.py` oraz 169 testów syntetycznych (według poprzedniego handoffu).

## Konsekwencja (hipoteza robocza do potwierdzenia na danych)

Dopóki nie ma zaakceptowanych planów PL z `pl_import.py`, czytanki mogą być
wydaniem **częściowym**: struktura, dane liczbowe, powiązania i encyklopedia
pochodzą z assetów gry, a brakujące teksty pozostają jawnie oznaczone. Nie wolno
podkładać EN jako polskiego tekstu ani ogłaszać wydania pełnym. Wszystkie
powyższe twierdzenia o brakach są ograniczone do zakresu danych na Drive i w
repozytorium, nie są diagnozą kompletności gry u właściciela.

## Kolejne checkpointy (będą dopisywane)

1. Odtworzenie prywatnych wejść, indeksu i S6 z archiwów na Drive.
2. Badanie źródłowe encyklopedii (`PilotDictionaryEntryTable` /
   `RobotDictionaryEntryTable`) — dokładne powiązania, nie nazwy.
3. Generacja plików `.md` do nowego katalogu + receipt z jawnymi brakami.
4. Nowy handoff z listą tego, co pozostało (A–D).
