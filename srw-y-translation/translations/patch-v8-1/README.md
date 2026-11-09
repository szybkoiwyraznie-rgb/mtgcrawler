# patch-v8-1 — dodatek do paczki v8

Ten katalog to **nie** nowa wersja szablonu v8. `translations/template-v8/` zostaje
zamrożony i podpisany w `SHA256SUMS`, bo po nim sprawdzane są zwrotki PL1.

Co tu jest:

* `odcinek-99-dodatek.md` — 299 elementów w 6 scenach, których paczka v8 nie miała.
  Numeracja jest lokalna: `Scena D1/6 … D6/6`, elementy od 1 w każdej scenie.
* `ODPOWIEDZI_TLUMACZOWI.txt` — odpowiedzi na 9 pytań tłumacza (każda bez pracy z jego strony);
  trafia do paczki razem z plikiem do wypełnienia,
* `import_manifest.json` — manifest wejściowy dla `tools/pl_import.py` (schemat 2,
  299 elementów, suma pliku i suma korpusu).

Plik powstaje z `data/package_appendix_y.json`:

    python3 tools/build_package_appendix.py --write     # plik + manifest
    python3 tools/build_appendix_kit.py                 # build/SRW_Y_PACZKA_v8_1_DODATEK.zip

Opis całej operacji, liczby i decyzje: `docs/DODATEK_8_1.md`.

Wydana paczka: `SRW_Y_PACZKA_v8_1_DODATEK.zip`, 20 312 B, SHA-256 `f71e2487…96cbab`,
Drive `1Y0gHYSCV7LuK3xeVBzAXoiySney7ACUO` (nowa wersja paczki; poprzednia poszła do kosza).
