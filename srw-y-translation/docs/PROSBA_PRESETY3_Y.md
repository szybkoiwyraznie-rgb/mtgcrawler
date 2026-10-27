# PROŚBA — 3 ostatnie presety (`SRW_Y_PRESETY3_PROSBA.zip`)

Dokumenty powiązane: [`HANDOFF_READING_WYNIKI_2026-10-27.md`](HANDOFF_READING_WYNIKI_2026-10-27.md) §9,
[`PROSBA_PRESETY_Y.md`](PROSBA_PRESETY_Y.md). To **czwarty, ostatni kit**.

## Dlaczego nie wystarczą nazwy plików

`SRW_Y_PRESETY.zip` (109 bundli, SHA-256 `0abd10565f9b…`)
rozwiązał **88 z 91** wskaźników `preset_file` po dokładnej parze
(CAB, PathID). Zostały trzy:

| misja | brakujący CAB | PathID | `script_file` |
|---|---|---:|---|
| `m4003_0202500` | `CAB-58e9cd9947154ef535126db225215ad0` | `-3378871923023034847` | `sg4003_0202500a` |
| `m4020_0200230` | `CAB-79ddf87b4d63e5a85be58e6e5bdadfe8` | `-713082379541291897` | `sg4020_0200230a` |
| `m5003_0107330` | `CAB-cd5151f08eae3cb61aecc23bad1bd323` | `-6070146337825874469` | `sg5003_0107330a` |

Dla tych trzech misji katalogi Addressables mają wyłącznie adresy
`_Normal` i `_Hard`; oba bundl e są już w zwróconej paczce, ale ich
wewnętrzne nazwy plików i PathID-y nie są celami wskaźników. Żadna
z 91 docelowych par nie występuje też w dziewięciu wcześniejszych
archiwach. Źródłem prawdy są [`data/preset_evidence.json`](../data/preset_evidence.json)
(`pptr.remaining`, SHA-256 `0f17b9e39717…`).

## Co robi skrypt

`ZBIERZ_PRESETY3.ps1` (BOM + CRLF + ASCII, PowerShell 5.1, bez Pythona):

1. Znajduje `StreamingAssets` w typowych folderach Steam.
2. Dla każdego `.bundle` czyta pierwsze **512 B**.
3. Odszyfrowuje je znanym szyfrem `SeekableAesStream`
   (`PasswordDeriveBytes` SHA-1 × 100 → AES-128-ECB, licznik od 1, XOR).
   Pomiar na 109 bundlach: wewnętrzna nazwa `CAB-…` leży na pozycji **92**.
4. Porównuje z trzema dosłownymi napisami; trafione bundl e kopiuje do
   `SRW_Y_PRESETY3` wraz z `manifest.txt` (ścieżka, nazwa, który CAB).
5. Pakuje `SRW_Y_PRESETY3.zip` i wypisuje rozmiar + SHA-256.

**Samotest szyfru:** w skrypcie jest znany szyfrogram
(`srw_y_selftest.bundle` → `UnityFS\0…`). Jeśli port kryptografii w .NET
byłby błędny, skrypt zatrzyma się z czerwonym komunikatem zamiast
odesłać pusty zip. Wektor jest też sprawdzany w `tests/test_final_preset_kit.py`.

Nic nie jest modyfikowane w grze; nie są kopiowane żadne inne pliki.

## Co uruchomić

**`SRW_Y_PRESETY3_PROSBA.zip`** — na Drive w folderze projektu
(id `18xIBclTKykKOP67fvJ55UZDMotGIVZA2`, 4,287 B,
SHA-256 `a4dee52800a3e4bed146b49e1902e77602410063ecb4e60cd61e0142223fe088`). W środku `URUCHOM_TO.bat`, `ZBIERZ_PRESETY3.ps1`,
`CZYTAJ_TO.txt`.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie **`SRW_Y_PRESETY3.zip`** — wgraj go na ten sam
   folder na Drive i daj znać. Razem z logiem, jeśli skrypt wypisał `BLAD`
   albo znalazł mniej niż 3 pliki.

## Co zrobię po otrzymaniu

1. Zweryfikuję SHA-256 i rozmiary; odszyfruję bundl e.
2. Sprawdzę dokładne pary (CAB, PathID) z trzema pozostałymi wskaźnikami.
3. Jeśli się zgadzają — przebuduję indeks i `deployment.md`;
   `structural_issues` powinno spaść do **0**.
4. Jeśli nie — podam liczbę i opis tego, co jest, bez zgadywania.
