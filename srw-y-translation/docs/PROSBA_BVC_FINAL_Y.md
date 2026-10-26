# PROŚBA 4 — ostatnie kontenery głosu (`SRW_Y_BVC4_PROSBA.zip`)

## Stan po `SRW_Y_BVC3.zip`

| tabela | z mówcą | wszystkich |
|---|---|---|
| `battle_voice` | 26,862 | 28,283 |
| `battle_voice-DLC1` | 1,075 | 1,175 |
| `battle_voice-DLC2` | 798 | 947 |
| `battle_voice-DLC3` | 1,775 | 1,833 |
| `battle_voice-DLC4` | 1,892 | 2,079 |
| **razem** | **32,402 (94.4%)** | **34,317** |

Odrzucona teza „mówców nie ma w danych” jest nie tylko obalona — jest **policzona**:
290 różnych mówców, każdy z pola `nameText`, plus płeć z `PilotBasicDatas.genderType`.

## Co jeszcze brakuje

**1,915 kwestii** (5,6 %) wskazuje `WaveId`-y z zestawów głosu, których nie było w
żadnej paczce. Nie są adresowane jako `KOD_XX0_00` — w katalogu gry występują pod **samym
kodem**, np. `GUNCC_ARB`, `GUNSM_SM5`, `4ANOG_AD0`, oraz jako **`BvcCommon`** +
`BvcCommon--DLC1…4` (linie wspólne dla wszystkich jednostek). Dlatego nie trafiły do prośby 2
(`bvcFile` pilotów) ani 3 (wzorzec z numerem).

Kryterium jest mechaniczne, nie zgadywane: adres w rodzinie kodów głosu, bundel ≤ 64 KiB
(tabela, nie scena czy lokalizacja), którego jeszcze nie mamy →
**145 bundli, 520,834 B** (≈ 0.5 MB).

| kontener | plik | rozmiar |
|---|---|---|
| `DINAC_KS1` | `01dcdfefae8d50bbf938690b661f13dd.bundle` | 2,849 B |
| `GRD_05` | `05fd4bf0546fd7f1874e450fd2eddce7.bundle` | 4,132 B |
| `1SPOG_WL0` | `06a32abc775cd613d4d9fbd83f5369a8.bundle` | 2,848 B |
| `NAGCV_AH1` | `06e63a6780d9aadf05bc95d927ff1197.bundle` | 2,850 B |
| `Rader_02` | `07a3b868b3cd8ad78ceea0eca2156ced.bundle` | 4,119 B |
| `Text_de` | `0c7a76a688ce50ae7fe5480e1df4017b.bundle` | 5,367 B |
| `Flame_Head_56` | `10968f0dbb2c190c0b19e8ba491daffc.bundle` | 4,875 B |
| `cge_m04` | `10ca8b6a3265f196136125aa8158ee11.bundle` | 2,498 B |
| `Arrow_Down` | `13111d92accc064d74ebb08488e90918.bundle` | 6,192 B |
| `Arrow_Flip` | `144b9abec2d3755888f0a679c81eb723.bundle` | 5,713 B |
| `MJP_M00` | `14861b0125428426a94cd4878bfbea57.bundle` | 2,498 B |
| `GUNSM_ND1` | `15d42c59491c83d11dde7e31aad1ffbd.bundle` | 2,853 B |
| `GUNSM_GJ4` | `19acaf2f970f7860a94da892f35d062c.bundle` | 2,856 B |
| `GUNSM_SM5` | `1afaebe1ab671f97ced06bd2b2d5e678.bundle` | 2,848 B |
| `CYB_M00` | `1b03615efb00283a4387979da0b82a87.bundle` | 2,499 B |
| … | | pozostałe 130 |

## Co uruchomić

**`SRW_Y_BVC4_PROSBA.zip`** — na Drive w folderze projektu
(`1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`). W środku `URUCHOM_TO.bat`, `ZBIERZ_BVC4.ps1`,
`CZYTAJ_TO.txt` — ten sam format co poprzednie paczki.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie **`SRW_Y_BVC4.zip`** — wgraj go na Drive.

## Co będzie po niej

Każda kwestia, którą gra zna, dostaje mówcę z danych: `[Cytat bitewny — アムロ (Amuro)]`,
z płcią z tabeli pilotów. Jeśli po tej paczce zostaną pojedyncze kwestie bez kontenera,
będą to linie, których gra naprawdę nie przypisuje żadnej postaci — i to też pokażemy
liczbą, nie domysłem.
