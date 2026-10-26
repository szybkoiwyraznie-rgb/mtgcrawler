# Limity tekstu w SRW Y — co zmierzono, a czego nie

Ten dokument odpowiada na jedno pytanie: **ile można napisać** w każdym elemencie.
W SRW OE odpowiedź była prosta, bo pola miały stały rozmiar (`limit: 117 B (stała
szerokość)`). W SRW Y pola są **zmiennej długości** — rekord tabeli niesie własną długość,
a scenariusz to plik Lua. Granicę wyznacza więc nie struktura pliku, a to, co gra potrafi
wyświetlić. To zmierzyliśmy z danych gry, w obu językach, i zapisaliśmy w
`local/s6/limits.json` (`tools/s6_limits.py`).

## 1. Sceny (dialog, narracja)

| co | japoński | angielski | wniosek |
|---|---|---|---|
| linii w jednym okienku | **max 3** | **max 3** | okno mieści 3 linie — to jest twarde |
| szerokość najszerszej kwestii | 145 celi | **240 celi** | okno jest pojemne, angielski idzie 65% dalej niż japoński |
| szerokość najszerszej **linii** | 62 cele | 137 celi | gra zawija tekst, więc liczy się całość, nie jedna linia |
| mediana kwestii | 44 cele | 52 cele | polski ≈ angielski, czyli ~50 celi to norma |

**Liczby do paczki:** liczba linii (zawsze 3 lub mniej), szerokość oryginału w celach,
pojemność okna (3 linie) i najszersza kwestia w grze (240 celi).

Czego **nie** zmierzono: marginesów okna i tego, czy gra przymnie tekst, czy go przytnie.
Dlatego w pakiecie jest „trzymaj się objętości oryginału”, a nie „wolno 240 celi”.

## 2. Tabele (nazwy, opisy, interfejs)

Dla każdej z 144 tabel policzono najdłuższy tekst, jaki gra w niej trzyma — w obu językach.
To jest **sprawdzona pojemność pola**: skoro gra wyświetla taki napis w japońskim
i angielskim, wyświetli go też po polsku.

| tabela | wpisów | max jp | max en | EN dłuższy od JP |
|---|---|---|---|---|
| `battle_voice` (cytaty) | 28 283 | 84 cele | 127 celi | 6 094 |
| `pilot_name` | 680 | 78 celi | 50 celi | 69 |
| `dic_text_pilot` (opisy) | 550 | 1 817 celi | 3 808 celi | 126 |
| `weapon_name` | 451 | 50 celi | 49 celi | 61 |
| `system_text` (interfejs) | 923 | 274 cele | 326 celi | 162 |
| `mission_detail` | 377 | 108 celi | 120 celi | 60 |

**Liczby do paczki:** `do N celi` (najszerszy napis w tej tabeli) + rozmiar japońskiego
w celach i bajtach.

Czego **nie** zmierzono: szerokości kolumn list (imię pilota, nazwa broni) i pól
przewijanych. Dlatego przy nazwach zalecenie brzmi: bliżej oryginału niż na granicy.

## 3. Który limit naprawdę „gryzie” — zależy od trybu zapisu

To jest najważniejsza część i jednocześnie miejsce, w którym **nie mamy jeszcze
sprawdzenia w grze**.

**Tryb A — podmiana w miejscu, ten sam rozmiar.** Sprawdzony w grze: tak działa polskie
otwarcie (v2, potwierdzone przez właściciela). Tekst jest wpisywany w miejsce oryginału
i dopełniany, więc plik się nie przesuwa. Limit twardy = **rozmiar tekstu, który
podmieniamy**, czyli angielskiego.

Ile polskich napisów się w to zmieści:

| dane | angielski dłuższy niż japoński | uwaga |
|---|---|---|
| tabele | 8 714 z 44 055 (**19,8%**) | głównie nazwy: `weapon_name` 61/451, `pilot_name` 69/680 |
| sceny | 29 200 z 114 383 (**25,5%**) | |

Polski jest zwykle o ~10% dłuższy od angielskiego (znaki diakrytyczne = 2 B w UTF-8),
więc w trybie A **część napisów się nie zmieści** — i nie da się tego naprawić skracaniem,
bo chodzi o nazwy własne.

**Tryb B — przebudowa, rozmiar może się zmienić.** Wtedy jedynym limitem jest szerokość
na ekranie (sekcje 1–2 powyżej), a rozmiar pliku przestaje być ograniczeniem.
Ten tryb **nie został jeszcze sprawdzony w grze**: pierwsza próba (v1) przebudowywała
bundle przez UnityPy, plik urósł o 9,5 KiB i gra odmówiła startu. Nie wiemy, czy
przeszkodził rozmiar, czy nowy nagłówek kontenera.

## 4. Co z tego wynika dla paczki

- W paczce są **zmierzone** liczby z sekcji 1–2 (nie „nie wiadomo”).
- Nie ma w niej jeszcze obietnicy „tyle się zmieści”, dopóki tryb B nie przejdzie testu
  w grze — bo od tego zależy, czy limitem jest ekran, czy rozmiar pliku.
- Plan obejścia dla scen w trybie A: plik Lua można dopełnić **komentarzami** (`-- …`),
  których gra nie wyświetla, więc rozmiar pliku da się utrzymać bez ruszania tekstu.
  Dla tabel takiego wypełniacza nie ma — tam działa tylko tryb B.

## 5. Test trybu B w grze (gotowy, czeka na uruchomienie)

Sprawdzenie offline nie wystarczy — potrzebny jest jeden bieg w grze. Zbudowany kit
podmienia **jedną scenę** (pierwsze dialogi po narracji otwierającej, `cse20_0000_0000300a`,
61 linii po polsku) w **obu wariantach językowych gry**, więc właściciel nie potrzebuje
sejwa: nowa gra i tekst jest na ekranie w pierwszej minucie.

Co ten test rozstrzyga i czego **nie** rusza:

| element | stan |
|---|---|
| nagłówek pliku serializowanego (wersja, typy, koniec pliku) | **bez zmian** — w pierwszych 4096 B różnią się 2 bajty: rozmiar metadanych `0x4B58 → 0x4948` |
| układ bloków LZ4 (128 KiB, LZ4HC) | bez zmian, ta sama liczba bloków (ja 239, en 259) |
| podmiana bloków + nowy blok informacyjny kontenera | **już sprawdzone w grze** — tak działa polska narracja (v2) |
| obiekty inne niż edytowany skrypt | **weryfikowane bajt w bajt** przy budowie, 606/679 obiektów bez zmian |
| nowy rozmiar obiektu w tabeli obiektów | **to jest nowe** |
| inny rozmiar całego pliku `.bundle` | **to jest nowe** (ja +1 666 B, en +1 096 B) |

Liczby z builda:

| wariant | bundle przed → po | skrypt przed → po | bloki |
|---|---|---|---|
| ja-JP `8939a711…` | 4 740 401 → 4 742 067 B | 40 133 → 39 068 B | 239 → 239 |
| en-US `1c12bbab…` | 5 591 151 → 5 592 247 B | 39 293 → 38 761 B | 259 → 259 |

Gdyby gra odmówiła startu, następny krok jest jednoznaczny: ten sam build dopełniony
zerami do **oryginalnego** rozmiaru pliku. Wtedy test odcina „inny rozmiar pliku” i
zostawia samo „inny rozmiar obiektu” — i od razu wiadomo, która z dwóch rzeczy szkodzi.

## 6. Co pokazał test 2 w grze (2026-10-26)

Potwierdzone przez właściciela na ekranie:

| rzecz | wynik |
|---|---|
| dialogi po polsku, plik o innym rozmiarze | **działa**, polskie znaki wyświetlają się poprawnie |
| tabele (MonoBehaviour) po polsku, inny rozmiar | **działa** — ekran wyboru postaci jest po polsku |
| etykiety w tabelach dłuższe od angielskich | gra **zmniejsza czcionkę** (`Ulubione danie` zamiast `Fav. Food` zmieściło się) |
| wartości w tabelach dłuższe od angielskich | **nachodzą na sąsiednie pole** — `Chłodny, bezwzględny` (20 celi) weszło na etykietę `Charakter`; `Książki` i `Sumo na żywo` mieszczą się |
| menu tytułowe (`Start`, `Option`, `Store`, `Quit Game`) | **nie jest w tabelach** — podmiana `system_text` 133-141 nic nie zmieniła |

Wniosek o menu: tekst menu tytułowego leży w assecie UI (prefab/scena), a nie w tabeli.
Z tabel obsługiwany jest tylko napis `Anniversary Expansion` (`system_text-DLC4`, idx 4) —
i ten trzeba podmieniać razem z tabelą DLC4, bo inaczej zostaje po angielsku.

**Decyzja o limitach (właściciel, 2026-10-26):** limit należy do **typu danych**, nie do
pojedynczego słowa — np. jeśli angielskie nazwy broni mają 5-49 celi, to limitem dla
wszystkich polskich nazw broni jest 49-50 celi, a nie długość konkretnej nazwy.
W paczce tłumacza każdy element tabeli ma więc limit swojej tabeli
(`do N celi (tyle ma najdłuższy tekst tego typu w grze)`).

## 7. Limit na pole, nie na słowo (decyzja właściciela, 2026-10-26)

Pytanie brzmiało: czy polski wpis w tabeli ma się mieścić w długości **tego jednego**
angielskiego słowa, czy w tym, ile gra mieści w **tym polu**. Druga odpowiedź — pole.

Realizacja: `tools/s6_groups.py` dzieli każdą tabelę na **pola** (podzbiory wpisów, które
gra rysuje w tym samym miejscu) i zapisuje wynik do `local/s6/groups.json`.

- **Tabela jednorodna** (wszystkie wpisy tego samego rodzaju: same nazwy albo same akapity)
  → jedno pole na całość, limit = najdłuższy tekst tej tabeli. Tak jest w 70 z 144 tabel
  (`weapon_name` 50 celi, `pilot_name` 78, `battle_voice` 127).
- **Tabela mieszana** (etykiety i wartości obok siebie) → 74 tabele dzielone na pola;
  `system_text` na 310 pól. Nowe pole zaczyna się, gdy długość skacze o więcej niż
  **1,6x** albo zmienia się liczba linii; sąsiednie pola bliższe niż 1,6x są scalane.
- Współczynnik 1,6 to **osąd, nie pomiar** — z pikseli nie znamy szerokości pól.
  Skutek dla ekranu wyboru postaci zgadza się z tym, co widać w grze:

| indeksy | pole | teksty w grze | limit |
|---|---|---|---|
| 238-241 | wzrost + etykiety | `Height`, `180cm`, `162cm`, `Traits` | 6 celi |
| 242-243 | charakter postaci | `Cold, ruthless`, `Upbeat, cheery` | 14 celi |
| 244-245 | zainteresowania | `Hobbies`, `Reading` | 7 celi |
| 246-249 | reszta wartości | `Watching sumo`, `Fav. Food`, `Shime saba`, `Yakitori` | 13 celi |

Polski `Chłodny, bezwzględny` (20 celi) przekraczał limit pola 14 — i faktycznie wchodził
na etykietę `Charakter`. `Ulubione danie` (14 celi przy limicie 13) zmieściło się, bo
etykiety gra zmniejsza czcionką; ta różnica jest opisana w paczce tłumacza.

## 8. Napisy UI siedzą w prefabach, nie w tabelach (2026-10-26)

Test 2 pokazał, że menu tytułowe nie reaguje na `system_text`. Przyczyna jest teraz znana:
**tekst interfejsu jest polem `m_text` (TextMeshPro) wewnątrz `MonoBehaviour` w prefabach**,
a nie rekordem tabeli. Sprawdzone w dwóch partiach plików od właściciela (23 bundle):

| bundle | co zawiera | napisów `m_text` |
|---|---|---|
| `15e5b9dd…` ButtonLists | etykiety przycisków walki: 待機, 攻撃, 変形, 修理, 説得… | 81 |
| `5ca325de…` General_Canvas | tytuł menu opcji, 分析設定 | 20 |
| `cea16a71…` LibraryMenu | Confirm, Database, Back | 15 |
| `ec293019…` Title | `Press Any Key` (×2, animacja wejścia i spoczynek) i licznik `30` | 3 |
| `f547a414…` UIData | brak tekstu | 0 |

Zapis takiego napisu to przepisanie **typetree** obiektu: `read_typetree` → zmiana
`m_text` → `save_typetree`. Jest wierny, ale dowód musi porównywać `obj.data`
(`get_raw_data()` zawsze zwraca stare bajty i przez to każdy zapis „wygląda” poprawnie).

**Pułapka, która kosztowała jedno przebudowanie:** bundle UI ma w jednym kontenerze
**dwa strumienie** — plik serializowany i `.resS` (tekstury, do 8 MB). `env.file.save()`
oddaje tylko pierwszy, więc przebudowa bez przepisania reszty **po cichu kasuje tekstury**,
a weryfikacja obiektów nadal przechodzi. `tools/srw_y_rebuild.py` składa teraz strumienie
z powrotem i sprawdza, że ogon kontenera wrócił bajt w bajt. Tabele tekstowe (test 2) były
pojedynczymi plikami, więc tamten build tego błędu nie miał.

**Menu tytułowe to grafika, nie tekst.** Atlas `OptionMenuButton_Font`
(`625dd570…`, 1440×240) to pięć wierszy napisów w pięciu językach: Save, Load, System,
To Title Screen, Quit Game. Katalog adresów pokazuje też `StrategyTop/Contents_*.png`
osobno dla `jp`, `en`, `ko`, `zhcn`, `zhtw`. Czyli `Start`, `Option`, `Store`,
`Quit Game` trzeba **narysować**, a nie podmienić jako napis — decyzja dla właściciela.

Narzędzie: `tools/build_pl_ui_patch.py` (`--check`, `--kit --zip`), teksty w
`translations/ui_test_pl.json`, testy w `tests/test_ui_prefab_patch.py`.

**Sprostowanie (właściciel, 2026-10-26):** `TOP_Font` to **nie** menu z ekranu
tytułowego. Właściciel nie ma tam pozycji `Mission / Customization / Unlock STG Memory /
Database` — te cztery są w menu *w grze*, a ekran tytułowy pokazuje
`START / OPTION / STORE / QUIT GAME`. Czyli atlas `TOP_Font` tłumaczy właściwą rzecz
w niewłaściwym miejscu, a ekranu tytułowego nadal nie mamy.

Do tego dwa sprzeczne fakty, które trzeba rozstrzygnąć, zanim powstanie kolejny test:

| fakt | źródło |
|---|---|
| `START`, `OPTION`, `STORE`, `QUIT GAME` **są** w tabeli `system_text` (idx 135, 137, 140, 141) | `local/s6/tables.jsonl` |
| podmiana tych indeksów w teście 2 **nic nie zmieniła** na ekranie tytułowym | relacja właściciela |
| `Press Any Key` jest polem TMP w prefabie `Title` (`ec293019…`), a po teście 3 **też zostało po angielsku** | relacja właściciela |

Dwa ostatnie punkty razem znaczą, że albo pliki nie weszły (test 3 nie miał żadnej
weryfikacji kopiowania — sam `copy` z `>nul`), albo ekran tytułowy jest składany
w locie z innego assetu. Kit testu 4 sprawdza kopiowanie (`certutil` + `RAPORT.txt`),
więc to pytanie da się wreszcie rozstrzygnąć. Jeśli pliki weszły (OK) i napis się nie
zmienił, to prefab `Title` nie jest tym, co widać — i wtedy tropem jest bundle `scene`
(`795b4b48…`) oraz atlasy czcionek z partii UI4/UI5.
