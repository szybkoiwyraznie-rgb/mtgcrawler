# Kotwice mówców — sprawdzenie połączenia na znanych okrzykach

Każdy okrzyk to jedna postać i jedno `nameText` z danych gry. Sprawdzamy, czy
gra sama nazywa mówcę tak, jak mówi się go w anime — a nie nazwą robotu,
który w tym okrzyku występuje.

| okrzyk | oczekiwany mówca | kwestii | z tym mówcą | odczytani mówcy | wynik |
|---|---|---|---|---|---|
| イデオンソード | コスモ | 3 | 2 | コスモ, デク | ZGODNY |
| ブライ・ソード | キッド | 3 | 2 | アイザック, キッド | ZGODNY |
| ダ・ガーン | 星史 | 49 | 40 | イグジス, ダ・ガーン, レッドロン, 星史 | ZGODNY |
| ゲッタービーム | 拓馬 | 2 | 2 | 拓馬 | ZGODNY |

Ci sami okrzyki wypowiadają czasem dwaj piloci tej samej serii (np.
`イデオンソード` — コスモ i デク, obaj z Ideonu), dlatego kolumna „odczytani
mówcy” bywa dłuższa niż jeden. To własność danych, nie błąd: każdy wiersz
ma własne `nameText`.


## Jak to jest zapisane (na jednym przykładzie)

```text
wiersz battle_voice    0000157d:5320b006
  bank (high32)        0000157d          # zestaw głosów serii
  wpis (low32)         5320b006          # id z generatora Unity
  -> Shared Data       0000157d:5320b006 -> B09_289
  -> kontener          3EXID_YK0_00
  -> nameText          コスモ
  -> NameKey           LGNGIDEON_001
  -> portret           COSMO_S
```

## Wniosek

Mówca nie jest zgadywany z treści: to pole `nameText` w kontenerze głosu,
wskazanym przez `WaveId` z `Shared Data`. Dlatego `[Cytat bitewny — <mówca>]`
można wpisać wszędzie tam, gdzie ten kontener jest — bez ryzyka pomyłki
