# PROŚBA 3 — reszta kontenerów głosu (`SRW_Y_BVC3_PROSBA.zip`)

## Co już wiemy (po `SRW_Y_BVC.zip`)

Połączenie **jest** w danych i jest odtworzone bez zgadywania:

```
wiersz tabeli battle_voice        klucz 01999dc9:15e0b000
  -> battle_voice Shared Data    m_Id -> m_Key        "F069_002"
  -> kontener głosu              WaveId -> PlayDetails
                                 {nameText, NameKey, FaceKey, dialogueText}
```

- 45 303 wpisów `Shared Data`, **34 317 / 34 317** wierszy `battle_voice` rozwiązanych do `WaveId`;
- **10,740 / 34,317** kwestii
  (**31.3%**)
  ma nazwanego mówcę z pola `nameText`;
- **120** różnych mówców (スレッタ 524, ヒイロ 366, 拓馬 344,
  ダバ 322, ガウマ 305, 鉄也 302, 仮面ライダーＷ 296, ルルーシュ 291…);
- płeć mówcy z `PilotBasicDatas.genderType` (`local/s6/voice_map.json`).

Reszta — 23 577 kwestii — wskazuje `WaveId`-y z kontenerów, których jeszcze nie mamy.
Nie ma tu żadnej innej tajemnicy: to ta sama warstwa danych, brakuje tylko plików.

## Co zamawiamy

Wzorzec nazwy kontenera sprawdzony na **84/84** posiadanych:

```
^[0-9A-Z]{3,6}_[A-Z0-9]{2,4}\d?_\d\d$      GEARE_LL1_00, 1SPBO_BK0_00, 2BVDG_RG0_00
```

W katalogach (podstawka + 11 paczek) pasuje **395** bundli.
Posiadamy 327 plików z poprzednich paczek, więc ta prośba to
**311 bundli, 2,088,297 B** (≈ 2.0 MB),
każdy rozwiązany przez katalog Addressables do dokładnej ścieżki i rozmiaru ze spisu właściciela.

| kontener | plik | rozmiar | katalog |
|---|---|---|---|
| `OSROG_AI0_01` | `0001072104cecafc8b3a8d49a22b5d71.bundle` | 2,303 B | base |
| `DINMK_KK0_00` | `00865751030fa68b80974b2eefd29aa4.bundle` | 6,512 B | base |
| `DINAC_IG0_01` | `00f8a71ef114dd09eba741504b5b7811.bundle` | 4,087 B | base |
| `GUNSM_SZ0_00` | `018552a0eb1b4c0437d90d8a99437595.bundle` | 4,543 B | base |
| `GUNSM_GJ0_00` | `0365d8da31ddc266619e6bba93b29de3.bundle` | 3,381 B | base |
| `DINMK_AH0_00` | `03a5ce04bcf50e9f4473bea4604abbdc.bundle` | 6,993 B | base |
| `DINAC_IS0_04` | `04270a38d3ea76785d2726af081cb0e7.bundle` | 2,161 B | base |
| `SDBIN_KK0_00` | `042ac72077be167f58fb4e26f3b8fb5a.bundle` | 5,544 B | base |
| `3EXEH_ESZ_02` | `051f65b19eb127351d3a5f574995fbb4.bundle` | 5,364 B | base |
| `GUNJG_AB1_00` | `052989fff12416d123ddacafe6bda953.bundle` | 4,551 B | base |
| `1SPBO_RGZ_01` | `0539a13e25d531d052a1bc8d70600772.bundle` | 6,208 B | base |
| `GUNSM_SM5_03` | `0553f866f55f257415a8ff2b4de94ea3.bundle` | 5,601 B | base |
| `DINAC_NTP_01` | `05561d378153862c9cb07660de8a8062.bundle` | 3,949 B | base |
| `MACDG_TY0_00` | `0657565ded7ccb2950e04f0e01a7e3f1.bundle` | 5,004 B | base |
| `GUNCC_NZK_00` | `06c58c921c451dd8cf4cc1ae68754d35.bundle` | 4,196 B | base |
| … | | | pozostałe 296 |

## Co uruchomić

**`SRW_Y_BVC3_PROSBA.zip`** — na Drive w folderze projektu
(`1NRzLJq9HFPO1in9ml4MbQBu1Sfnn03Lr`). W środku `URUCHOM_TO.bat`, `ZBIERZ_BVC3.ps1`,
`CZYTAJ_TO.txt` — ten sam format co `SRW_Y_UI6_PROSBA.zip` i `SRW_Y_BVC_PROSBA.zip`.

1. Rozpakuj **na pulpit**.
2. Kliknij dwa razy `URUCHOM_TO.bat`.
3. Na pulpicie powstanie **`SRW_Y_BVC3.zip`** — wgraj go na Drive (ten sam folder).

## Co z tego będzie

Po tej paczce mapa mówców jest kompletna: każda kwestia dostaje
`[Cytat bitewny — アムロ (Amuro)]` zamiast `[głos 7/39]`, płeć z danych, zero zgadywania.
To warunek, który postawił właściciel projektu: żadnej kapitulacji i żadnej etykiety
„nieznany mówca”, dopóki w danych jest plik, który to nazywa.
