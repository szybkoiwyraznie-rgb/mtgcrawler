# Czytanki SRW Y — rozpoczęcie prac 2026-10-27

Cel właściciela: odpowiednik kompletu OE (sceny, deployment, mechy, piloci),
regenerowany z tego samego zaakceptowanego tłumaczenia co patch, również częściowego.
Bez fallbacku EN udającego polski tekst i bez zgadywania związków po nazwach.

Punkt odniesienia: struktura czytanek i suplementów OE; bez importów danych/kodu OE.
Sceny Y i mapa misji są rozpoznane. Powiązania zdolności, broni i deploymentu
wymagają sprawdzenia pól oryginalnych assetów Y. To nie jest jeszcze gotowy katalog.

## Odtworzone wejścia do badań (Drive, 2026-10-27)

Wyłącznie wcześniej odebrane niewielkie paczki, bez ponownej prośby o całą grę:

- `SRW_Y_MISSION.zip`: ID `15Bzc6K9DvaJqKH5S0wE9uR3hGs_pH-l7`,
  685573 B, SHA-256 `780b59935581281b42d2ad9fbe449418d2cbc6d296f6ba91b94d8d6830c86b2c`.
- `SRW_Y_GLOSY.zip`: ID `1rOZ30lS92VanYAexxZNayKU3-0RQgMZz`,
  3080644 B, SHA-256 `9d0ddfcf80cafef636f91fd2fdb9e8e5b7f6468f403425decd9f0f822f66067d`.

Archiwa pozostają w ignorowanym `google_drive/`, wypakowanie i dane pochodne w
`local/reading-research/`. Żadne teksty/assety gry nie trafiają do Git.

## Narzędzia gotowe w tej iteracji

### 1. Indeks danych z oryginalnych bundli

Uruchamiać w `srw-y-translation/` (Python 3.11+, UnityPy i pycryptodome).

```sh
python tools/reading_index.py \
  --bundles local/voice local/mission local/s6/plain \
  --out local/reading_index.json
```

Podać **rzeczywiście istniejące** katalogi lub pojedyncze `.bundle` (przykład zakłada,
że dane odzyskano w tych ścieżkach). Można podać inne ścieżki. Narzędzie nie pobiera
niczego z sieci. Czyta zarówno zaszyfrowane bundle, jak i plaintext UnityFS; oryginałów
nie modyfikuje. Błędy odczytu danych nie są cicho pomijane.

Indeks jest prywatnym JSON-em: źródłowe kolekcje, klucze Shared Data, misje, presety,
referencje Unity, źródłowa kolejność tekstów w Lua oraz lista nierozwiązanych powiązań.
Nie trafia do Git. W odróżnieniu od istniejącej mapy misji zawiera także `preset_file`
i jego rozwiązaną parę **serialized file/CAB + PathID**, bez dopasowania nazwy presetu.
Zachowuje warianty rekordów z DLC osobno; konflikt definicji jest błędem, nie regułą
„ostatni plik wygrywa”.

### 2. Czytanki z zaakceptowanego tłumaczenia (także częściowego)

```sh
python tools/build_reading_y.py \
  --source-dir local/s6 \
  --index local/reading_index.json \
  --translations local/import-partia-1.json local/import-partia-2.json \
  --out local/czytanki-wersja-001
```

`--translations` przyjmuje wyniki obecnego `pl_import.py`, nie edytowane pliki `.md`.
Każdy plan musi mieć pieczęć aktualnego S6; dodatkowo porównywane są adresy i JP/EN
każdego importowanego napisu. Nie ma zgadywania po tekście ani cichego zastępowania
poprzedniej partii: zgodne powtórzenia planów są dozwolone, różne PL tego samego celu
są błędem. Przy poprawkach podać aktualny zaakceptowany zestaw planów — nie starą i
nową, sprzeczną wersję równocześnie. To nie jest narzędzie automatycznego resync.

Wynik w **nowym katalogu**:

- `README.md` — spis i ostrzeżenia o brakach;
- `rozdzial-01.md` itd. — teksty scen z jednym protagonistą na całą misję (domyślnie mężczyzna), grupowane przez misje;
- `sceny-poza-rozdzialami.md` — misje bez numeru rozdziału;
- `sceny-bez-misji.md` — pozostałe pliki, bez zmyślonego przypisania;
- `piloci.md` — bazowe parametry, rozkazy ducha i ich koszt/poziomy nauki,
  umiejętności i listy poziomów, bonusy asa, osobny indeks tekstów encyklopedii;
- `mechy.md` — parametry bazowe, zdolności, bonusy modyfikacji, broń z mocą,
  zasięgiem, kosztem i zapisanymi warunkami; osobny indeks opisów encyklopedii;
- `deployment.md` — unikalni uczestnicy wymienieni w presetach, bez momentów wejścia;
  nierozwiązane referencje jawnie osobno. Pierwsze wystąpienia postaci/mecha oznaczone;
  właściwe powiązanie biografii/opisu nadal niepotwierdzone, z jawnym znacznikiem braku;
- `srwy_reading_PL.zip` — deterministyczne archiwum plików `.md`;
- `receipt.json` — hashe źródeł, indeksu, planów, wszystkich plików i ZIP-a,
  braki, niewykorzystane tłumaczenia, nierozwiązane referencje i kolejność Lua.

Brakujące polskie teksty mają jawne **`[BRAK PL: ...]`**, brak mapy klucza
**`[BRAK KLUCZA: ...]`**. Nie podkładamy angielskiej/japońskiej prozy.
Nierozpoznany mówca może mieć wyraźnie opisaną **źródłową etykietę JP**, a warunki
mają surowe kody gry — to metadane, nie udawane tłumaczenie.

Czytanki powstają z **tego samego zestawu zaakceptowanych planów, który powinien
zasilać budowę patcha**. Samo narzędzie nie sprawdza aktualnej instalacji gry.
Hash w `receipt.json` identyfikuje wejścia czytanki, nie stan folderu Steam.
Docelowo należy zachować ten sam zestaw hashy z wydaniem patcha. Nie deklarujemy,
że obecny patcher już automatycznie uruchamia generator.

Katalog wyjściowy nie może istnieć ani zawierać wejść. Walidacja i renderowanie
odbywają się przed publikacją; komplet jest składany w tymczasowym katalogu,
a następnie przenoszony do docelowego. Nie nadpisujemy wcześniejszej czytanki.
Tekst tłumaczenia jest escapowany dla Markdown/HTML (bez wykonywania znaczników).

## Rzeczywisty research — co potwierdzono

Dwa wcześniej odebrane archiwa wystarczyły do sprawdzenia struktury, bez zamawiania
nowych danych u właściciela:

| miara | odczytane |
|---|---:|
| rekordy misji w zakresie | 533 |
| dodatkowy wpis systemowy (`mission_global_preset`, nie misja fabularna) | 1 |
| presety odczytane | 277 |
| rozwiązane referencje misja → preset | 276 |
| nierozwiązane niezerowe referencje do presetów | 91 |
| rekordy pilotów | 683 |
| rekordy mechów / wariantów | 1198 |
| rekordy broni wewnątrz mechów | 3686 |
| tabele Shared Data (w tym techniczna `font`) | 144 |
| skrypty scen Lua w tych dwóch archiwach | 0 |
| rekordy rozmieszczenia gracza w odczytanych presetach | 705 |
| rekordy pozostałych rozmieszczeń | 8659 |
| sloty wyboru | 3700 |

To liczby **rekordów danych**, nie liczba unikalnych grywalnych postaci, jednostek
ani zdarzeń, które wystąpią w jednej rozgrywce. Warianty misji/ID w różnych kolekcjach
pozostają osobno. Wpis globalny i wszystkie rekordy master są zachowane w indeksie,
nie symulujemy ich wpływu na runtime.

Potwierdzone ścieżki:

```text
PilotBasicDatas*.listPilotBaseData[]
  -> characterData / facialId -> listFacialSettingData[].{fullNameKey,nameKey}
  -> pilot_name[-DLCn] Shared Data m_Key -> m_Id -> tables.jsonl -> zaakceptowane PL
  -> growSpirits[].id -> listSpiritCommandData[].{nameKey,descriptionKey}
  -> growSkills[].skillId -> listPilotSkillData[].{nameKey,descriptionKey}
  -> aceBonusId -> ace_bonus Shared Data

RobotBasicDatas*.listRobotBaseData[]
  -> displayNameKey -> robot_name Shared Data
  -> skills[].{nameKey,descriptionKey} -> active_ability Shared Data
  -> customBonusId -> custom_bonus Shared Data
  -> weapons[].displayNameKey -> weapon_name Shared Data

Mission*Data.missionRomList[].composition[]
  -> preset_file {m_FileID,m_PathID}
  -> lokalny CAB albo externals[m_FileID-1] + PathID
  -> preset.{playerPlacementData,enemyPlacementData,selectPlacementData}
```

Kolekcja DLC szuka własnej definicji/klucza, następnie podstawki — nie arbitralnej
innej paczki DLC. Każdy wynik jest rozwiązywany po identyfikatorze w zakresie kolekcji.
Nie wyprowadzamy reguł ładowania konfliktowych assetów: niejednoznaczność jest błędem.

Zmierzona dostępność powiązań w odzyskanym zestawie (nie pokrycie tłumaczenia):

| powiązanie | znalezione | brak |
|---|---:|---:|
| pilot → klucz imienia/nazwiska | 678 | 5 |
| wpis umiejętności pilota → definicja | 2348 | 2 |
| wpis rozkazu ducha → definicja | 3114 | 0 |
| mech → klucz nazwy | 1198 | 0 |
| broń → klucz nazwy | 3674 | 12 |

Próba diagnostycznego renderu **rzeczywistego indeksu**, ale z pustym korpusem S6 i
bez tłumaczeń, przeszła dla katalogów i deploymentu. To sprawdza kształty danych,
nie jest gotową czytanką ani dowodem importu rzeczywistego PL. Wyniki zostały tylko
w ignorowanym `local/reading-research/diagnostic-render/`.

## Granice gotowości i dalszy research

1. **Kolejność dialogów — kontrola obowiązkowa.** Każdy publikowany plik musi mieć
   zgodność ID wystąpień i wszystkich tekstów z jedną fizyczną wersją źródłowego Lua.
   Jeżeli istnieją zgodne wersje JP i EN, wybierana jest JP. Kilka pasujących wersji
   o różnym porządku tych samych wystąpień oznacza błąd, nie arbitralny wybór.
   Nie ma awaryjnego porządku indeksu S6; `--require-order` pozostaje tylko zgodnym
   wstecznie przełącznikiem i niczego nie zaostrza. Kontrola poprzedza filtr płci.
   Na odtworzonym korpusie sprawdzono **964/964 pliki zawierające JP** (116056 wierszy)
   — żadnego błędu tożsamości/kolejności. Pozostałe 4609 wierszy bez JP są wykazane
   w receipt, nie zastępowane angielską prozą. Dwa oznaczenia płci wewnątrz misji
   nie dają dwóch czytanek: wybór jest wspólny dla wszystkich jej składników.
   Potwierdzony jest **porządek literałów w konkretnej wersji źródła**, nie jedna
   chronologia zdarzeń warunkowych ani liniowa ścieżka gry. Kolejność misji
   (obecnie rozdział, kolekcja, ID) jest porządkiem edycji, nie zweryfikowaną
   chronologią rozgrywki. Nie deklarować pełnego spełnienia wymagania kolejności
   scen/zdarzeń wyłącznie na podstawie tego testu literałów.
2. **91 PPtr — korekta diagnozy.** To nierozwiązane odnośniki wewnątrz danych
   misji, **nie dowód brakujących plików u właściciela** i nie nierozpoznani mówcy
   cytatów bitewnych. Po odtworzeniu dostępnych archiwów tekstowych i katalogów
   stan PPtr nie zmienił się; dotyczą kolekcji DLC/bonusów, nie podstawowej
   `MissionData`. Dokładne rozbicie: D1 16, D2 20, D3 28, Bn 14, B3 9, Er 2, Sz 2.
   Nie włączamy cytatów bitewnych do czytanek ani nie prosimy o nowe presety.
   Katalogi DLC mają odrębne adresy presetów; ich samo istnienie nie rozwiązuje
   CAB/PathID ani nie uprawnia do podstawienia presetu o podobnej nazwie.
   Przyczyna niepełnego lokalnego rozwiązania nadal pozostaje otwarta.
3. **Uczestnicy zamiast czasu wejścia.** Deployment łączy jawne BasisID z placement
   i rejestracji w obrębie misji, uwzględnia subpilotów i deduplikuje uczestników.
   Referencja runtime rozwiązuje się wyłącznie przez jawne przypisanie BasisID
   z tej samej misji. Brak przypisania pozostaje widoczny, nigdy nie utożsamia się
   ReferenceId z BasisID. Warunkowe warianty są unią uczestnictwa, nie symulacją
   `VersionUp`/`RideOn`, nie gwarancją początkowego składu ani momentu wejścia.
4. **Biografie i opisy encyklopedii — jeszcze niespełnione.** Pierwsze wystąpienie
   jest śledzone po facial ID postaci / BasisID mecha i ma jawny znacznik braku
   właściwego powiązania. Katalogi tekstów nie są zamiennikiem wymaganych opisów.
   Sprawdzony katalog bazowy wskazuje dziesięć konkretnych assetów:
   `PilotDictionaryEntryTable` / `RobotDictionaryEntryTable`, każdy base + D1…D4.
   Żadnego z tych dziesięciu bundli nie znaleziono w lokalnie odtworzonych archiwach.
   To wskazanie właściwej klasy danych do dalszego badania, **nie** potwierdzenie
   schematu jej rekordów. Nie zgadujemy właściciela z prefiksu `dic_pilot_*`,
   podobieństwa nazwy ani tekstu nagłówka. Nie zadeklarowano gotowego deploymentu
   z biografiami.
5. **Wzrost i warianty zdolności.** Wyświetlamy bazowe parametry, zapisane poziomy
   nauki/koszty i listę `mastaryLevels`. Nie wyprowadzamy z tego statystyk na lvl 99,
   progów kolejnych rang, wartości z zapisu gry czy formuł walki bez weryfikacji.
6. **Tożsamość wydania.** S6 odtworzono ponownie (120665 wierszy scen, 144 tabele / 44344 wiersze,
   bez problemów parsowania). To nie dowodzi zgodności z pieczęcią wydanego v7/v8:
   historyczny pakiet miał 143 tabele / 44340 wierszy. Rzeczywisty zwrot PL
   i przebudowa całego patcha nie były dostępne do testu czytanki końcowej. Nie wygenerowano/wysłano prywatnego
   kompletnego `srwy_reading_PL.zip` udającego gotowe wydanie.

## Testy

```sh
python -m pytest -q tests/test_reading_y.py
```

**35 passed** — syntetyczne regresje czytanek, w tym wybór protagonisty dla całej
misji, źródłowa tożsamość wersji językowych i obowiązkowa kolejność, uczestnicy
bez czasu wejścia, referencje runtime, subpiloci i pierwsze wystąpienia.
Łącznie z importerem, regresjami niezawodności OE, pakietem tłumacza i adapterem
patcha: **144 passed, 1 skipped, 57 subtests passed**. OE nie modyfikowano.

Na rzeczywistych odtworzonych danych wykonano prywatny diagnostyczny build bez PL:
13 plików MD, wszystkie 964 renderowalne skrypty przeszły weryfikację; receipt i
archiwum pozostają w `local/reading-research/diagnostic-complete-no-pl/`.
To sprawdzenie źródeł/struktur, nie gotowa czytanka PL do przekazania.

## Wiążące decyzje właściciela — kolejna iteracja 2026-10-27

- Jeden protagonista na całą misję: domyślnie mężczyzna; kobieta tylko przy braku
  wariantu męskiego i obecności żeńskiego w całej misji. Linie wspólne zostają.
- Nie uznawać poprzedniego wyniku 91 nierozwiązanych PPtr za brak dostarczonych
  presetów. Ponownie zbadać komplet już odebranych danych (bez cytatów bitewnych).
- Deployment to uczestnicy misji, bez momentu wejścia.
- Przy pierwszej postaci/mechu w kolejności misji w deployment dołączyć właściwą
  biografię/opis encyklopedii, raz na tożsamość postaci/modelu, nie na nazwę.
- Kolejność musi być potwierdzona; żadnego awaryjnego publikowania porządku S6.

Do weryfikacji odtworzono dodatkowe, wcześniej dostarczone archiwa:
`srw_y_tekst.zip` (Drive `1DFKONYYeRO-aQXpIvKQDVoAXmEam49xB`, 22472543 B,
SHA-256 `3d283d30124d9feca8453207a775ee1e3ead52b558be54885a403e27eacc3d20`),
`srw_y_dlc_bundle.zip` (`1Jof_EGWnMjxCa7klPP76whZfd7FTDQJC`, 7146855 B,
SHA-256 `4f148a67134069fc34868062631342829003591e942c7d4f79c0b464278d076d`),
`srw_y_free_patch.zip` (`1NucgseGzZRGM0QqgZ2Gmf-IK_8mSF6tH`, 363847 B,
SHA-256 `3be76fcce5fc13e308d36273bac7dd19aadf526f82553c0a7418a3bd80f974c0`).
Źródła i wyniki tylko w ignorowanych katalogach; nie zamówiono nowych plików gry.


Dodatkowo odtworzono wcześniejsze wejścia do audytu, bez nowej prośby do właściciela:

| Archiwum / Drive ID | B | SHA-256 |
|---|---:|---|
| `srw_y_text.zip` / `11RHT7izprqiKEtNTLs2kOneSACUvYeqW` | 12224594 | `b542d5b6ae69c80085e1f0385a81c5e2d4b32ddc426de71a1ffcce4ee058db89` |
| `srw_y_dlc_catalog.zip` / `16qmHBB5hhM1Zou09OUSaxyMipezM0FgF` | 2884114 | `714cd1bfc18c704bfd09a115d51456ac87ee02525061bc137fa0e2fb992d642f` |
| `SRW_Y_UI3.zip` / `1MMnmJm_GM65oe_t7srvqtkrmxa2ELo7w` | 16384052 | `005cf8226ed67d4fa2f62d6eb189837b1bdd820e1b7a611b5e4273da1ae4fa50` |
| `srw_y_pilot.zip` / `1AjCIwywLcOSb7KC2feuOUTAPsn6LeHWZ` | 33730 | `d2baf07ff6b4952fd2c136b89a074643b5007cdafa9953ec830ce8535d994f42` |

Bazowy `catalog.json` (Drive `1cSFIutg4pfL_KGimi4tab4_j29uC3s7N`, 41543062 B)
SHA-256 `12c17bf97478eca66f2aa6066c0a14974639443d0e9d79af3355abdd895273b4`
i wszystkie dziesięć katalogów DLC sprawdzono narzędziem `map_catalog.py`.
