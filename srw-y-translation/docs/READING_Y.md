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
referencje Unity, opcjonalna kolejność tekstów w oryginalnych Lua oraz lista braków.
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
- `rozdzial-01.md` itd. — teksty scen z obu wariantów bohatera, grupowane przez misje;
- `sceny-poza-rozdzialami.md` — misje bez numeru rozdziału;
- `sceny-bez-misji.md` — pozostałe pliki, bez zmyślonego przypisania;
- `piloci.md` — bazowe parametry, rozkazy ducha i ich koszt/poziomy nauki,
  umiejętności i listy poziomów, bonusy asa, osobny indeks tekstów encyklopedii;
- `mechy.md` — parametry bazowe, zdolności, bonusy modyfikacji, broń z mocą,
  zasięgiem, kosztem i zapisanymi warunkami; osobny indeks opisów encyklopedii;
- `deployment.md` — grupy rozmieszczenia gracza, pozostałych jednostek, sloty wyboru
  oraz rejestracje/zmiany załogi; zachowane `execNo`, warunki i identyfikatory;
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

1. **Kolejność dialogów.** Sam `scenario.jsonl` nie dowodzi oryginalnej kolejności
   literałów (ekstraktor sortował rekordy po ID). Nie sortujemy `0.10` i `0.2` jak
   liczb udających kolejność gry. Indeksowanie oryginalnych bundli scen odczytuje
   kolejność `string_id#occurrence` z Lua. Porównuje również tekst oryginalnego
   literału z JP lub EN w S6, by nie uznać za aktualny pliku innej rewizji tylko
   dlatego, że ma te same ID. Konflikt kolejności dwóch wersji językowych jest
   odrzucany, nie rozstrzygany przez kolejność plików. Bez nich generator jawnie ostrzega, że
   pokazuje kolejność indeksu S6. **Dla wydania docelowego dodać `--require-order`**:
   wtedy brak oryginalnego porządku lub brakujące ID przerywa generowanie.
   Nadal nie jest to jedna liniowa ścieżka rozgrywki: obie płcie, zdarzenia bitewne
   i warunki muszą pozostać rozdzielone. Nie opracowano jeszcze redakcyjnej selekcji
   scen/aliasów na poziomie gotowych, kuratorowanych odcinków OE.
2. **Deployment.** Wykryto 91 brakujących docelowych CAB-ów. `issues` indeksu zawiera
   dokładny target CAB/PathID, źródło i nazwę skryptu do dalszego sprawdzenia katalogu
   Addressables. Nie zgadujemy nazw bundli po prefiksie misji. Zanim powstanie nowa
   prośba o pliki, trzeba rozwiązać te zależności do najmniejszej listy bundli.
3. **Znaczenie grup.** `execNo` nie jest turą. Grupa z `enemyPlacementData` ma własne
   `allyGroup`; nazwa pola nie dowodzi wrogiej strony w każdej sytuacji.
   `ReferenceId` może wskazywać inny wariant niż `BasisID`, a globalne rejestracje,
   `VersionUp`, `RideOn` i warunki zmieniają załogę. Generator **nie symuluje** ich
   działania. Nazwy pilotów/mechów dołącza tylko przy rozpoznanym, jawnym BasisID.
   To jeszcze nie równoważnik engine-verified deploymentu OE.
4. **Biografie i opisy encyklopedii.** Klucze `dic_pilot_*` / `dic_robot_*` są znane,
   ale związek profilu z wersją/odblokowaniem opisu nie został potwierdzony w kodzie
   ani właściwym assetcie. Nie łączymy ich przez podobieństwo nazw. Wszystkie
   dostępne teksty trafiają do oddzielnego indeksu w odpowiednim katalogu.
5. **Wzrost i warianty zdolności.** Wyświetlamy bazowe parametry, zapisane poziomy
   nauki/koszty i listę `mastaryLevels`. Nie wyprowadzamy z tego statystyk na lvl 99,
   progów kolejnych rang, wartości z zapisu gry czy formuł walki bez weryfikacji.
6. **Tożsamość wydania.** Pełne S6, rzeczywisty zwrot PL i przebudowa całego patcha
   nie były dostępne do testu czytanki końcowej. Nie wygenerowano/wysłano prywatnego
   kompletnego `srwy_reading_PL.zip` udającego gotowe wydanie.

## Testy

```sh
python -m pytest -q tests/test_reading_y.py
```

**29 passed** — syntetyczny graf, pełne 64-bitowe klucze lokalizacji, zewnętrzne
referencje Unity i kolizje PathID, warianty DLC, brakujące presety, częściowe PL bez
fallbacku, mówcy po ID, obie płcie, powtarzające się ID kwestii, kolejność Lua,
nieprzypisane sceny, parametry/zdolności/broń, konflikty partii, pieczęć źródeł,
reprodukowalne MD/ZIP, ochrona wejść i wcześniejszych wydań, awaria publikacji.
Łącznie z importerem/renderem i adapterami: **138 passed, 1 skipped,
57 subtests passed**. Workflow Y rozszerzono o te testy; wynik CI jest osobną kontrolą.

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
