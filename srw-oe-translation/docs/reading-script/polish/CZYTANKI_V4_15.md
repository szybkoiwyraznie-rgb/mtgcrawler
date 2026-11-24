# Czytanka OE v4.15 — seria pochodzenia przy postaciach mówiących tylko w scenie (2026-11-23)

## Zgłoszenie właściciela

W `srwoe_mission_deployments.md`, w sekcji **„Postacie wypowiadające się w skrypcie
sceny (bez obecności w deployment — bez statystyk)”**, obok każdej postaci ma być
widoczna **seria, z której pochodzi**.

## Co się zmieniło

`docs/srwoe_mission_deployments.md` — **wyłącznie** ta jedna sekcja (plus trzy zdania
wstępu/opisów, które o niej mówią). Każdy wpis listy ma teraz postać:

```
- Fraw Bow — seria: Mobile Suit Gundam
- Himari Yaegaki — seria: Super Robot Wars Original
- Oficer Federacji — seria: brak wpisu w słowniku postaci
```

| Miara | Wartość |
| --- | ---: |
| Misje w dokumencie / listy mówców | 224 / **221** (194 liczby mnogiej + 27 pojedynczych) |
| Wpisy z serią | **4 363** (100 % wpisów listy) |
| Wpisy bez wiersza serii w słowniku | **74** (14 różnych nazw: `Oficer Federacji`, `Żołnierz Zeonu`, `???`, `Bandit`, …) |
| Zmienione linie pliku | 4 587 = 4 363 wpisy + 221 nagłówków list + 3 zdania opisowe |
| Reszta pliku | bajt w bajt bez zmian (karty mechów, pilotów, tabele, nagłówki misji) |
| Rozmiar / SHA-256 | **6 800 904 B** / `135f8328d179ddcae8dcc6bec466b01769004d9885e47aa51be717b7ac1e49a7` |

## Skąd bierze się seria

Z **słownika postaci gry** (`07_names_characters.jsonl`, część `series`), po kluczu
postaci, którą `00_dialogue.jsonl`/`06_scenes.jsonl` zapisują jako mówcę danej misji —
dokładnie ten sam mechanizm, z którego katalog pilotów bierze swoje linie
`**Seria:** …`. Tytuły serii pozostają w brzmieniu oryginalnym (nie są tłumaczone),
tak jak w kartach pilotów. Postać bez wiersza serii dostaje jawną etykietę
`brak wpisu w słowniku postaci` (sformułowanie z katalogu pilotów) — nic nie jest
zgadywane.

Rozstrzyganie jest **per misja**: mówcy są brani z jej scen, więc dwie postacie o tym
samym przydomku nie zlewają się. Przykład z dokumentu: w `DL209_13` mówią
`Shiro Amada` (Zoids/Gundam 08th) i `Shiro` z SRW Original; lista podaje obu z ich
własnymi seriami, a przydomek nigdy nie decyduje.

## Narzędzia i zabezpieczenia

- `tools/mission_deployments.py` — generator emituje teraz ten sam wiersz
  (`scene_speaker_line`, `load_character_series`) i ma policzony nowy licznik
  `scene_speaker_series_unrecorded` w podsumowaniu.
- `tools/add_scene_speaker_series.py` — narzędzie chirurgiczne dla środowiska bez
  kontenerów gry: przyjmuje **przypięty** dokument (`--pin-sha256`), przepisuje tylko
  wpisy list (i pięć zdań opisowych), a resztę pliku reprodukuje bajt w bajt; raport:
  `docs/mission-deployments-scene-series-2026-11-23.json`.
- `tests/test_scene_speaker_series.py` (9 testów) — format wpisów, liczby 221/4 363/74,
  pary znanych postaci, rozstrzyganie per misja, idempotencja, brak zgadywania,
  zgodność raportu z dostarczonym plikiem.
- `tests/test_mission_deployments.py` — dotychczasowe asercje wpisów mówców
  zaktualizowane do nowego formatu + inwarianty list.

## Wydanie

- Archiwum: **`srwoe_czytanki_PL_v4.15.zip`**, `1 569 346 B`,
  SHA-256 `e29d245f5d3de5821de9845ebd6004a41d2f6a8ab134e619f6630ab5f3c81c5a`,
  MD5 `95d5cf2e48bc148e5d07ec608788b16e`, 5 członków.
- Drive: `1cYpnVg4lCKELseQs_D__6Y_F697tGTr7` (folder `1zBVlAv_Nu-2hynN86f-vml7Yy823q22H`),
  odczyt metadanych po wgraniu zgodny (rozmiar, MD5, SHA-256).
- Bez zmian bajt w bajt wobec v4.14: `srwoe_scenariusz_PL.md` (`bd8d2de5…`, 2 391 177 B),
  `srwoe_mech_catalog_v4_PL.md` (`07f11deb…`, 873 130 B),
  `srwoe_pilot_catalog_PL.md` (`a22f5a9a…`, 303 453 B). Zmienione: `README.md`
  (etykieta wydania) i `srwoe_mission_deployments.md` (`686e18af…` → `135f8328…`).
- Kwit: `docs/reading-script/polish/czytanki-v4.15.delivery.json`.
  Poprzednie wydanie v4.14 (`1vaStE8a2Had8QfywRmqekIHXDfckx6GM`) **pozostawiono** na Dysku.

Pakiet gry (`pakiet_PL`), snapshot i plany PL są nietknięte; to zmiana wyłącznie
dokumentu do czytania. `runtime_tested` pozostaje `false` — dokument nie trafia do gry.
