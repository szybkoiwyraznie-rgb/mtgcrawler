# Odpowiedzi dla tłumacza SRW Y — 2026-10-26

Sześć pytań tłumacza z 26 października, odpowiedź i dowód z danych gry. Wszystko jest
też w `README.md` paczki **v6** (`plik_dla_tlumacza_v6.zip`, 8,283,635 B, sha256
`e19d8505…56aa93`), więc tłumacz nie musi czytać tego pliku — to jest zapis
dla właściciela projektu i dla historii.

Skrót: 1 pytanie (mówcy cytatów) **rozstrzygnęły dane gry** — właściciel odesłał 17
plików, z nich odczytano łańcuch „pilot → `bvcFile` → kontener → klucze”; brakuje już
tylko 310 kontenerów (druga prośba, 1,2 MB); 1 wymagało **wyrzucenia tabeli z paczki**,
1 to **reguła pisowni**, 1 to **nie błąd danych** (tłumacz źle przeczytał powtórzenie),
a 1 odkryło **realną wadę paczki** — bohater ma dwie płcie i obie są w grze. Mapa
rozdziałów, wcześniej odesłana jako „wymaga decyzji właściciela”, **jest już rozwiązana**
z danych misji i weszła do paczki **v8** (punkt 4).

## 1. Cytaty bitewne — mówca jest w danych i już wiemy gdzie

Tabela `battle_voice`: **34 317 kwestii w 39 bankach** (31 w podstawce, 8 w dodatkach).
Poprzednia odpowiedź („mówców nie ma i nie da się ich odzyskać”) była błędna i została
wycofana — właściciel miał rację, że połączenie musi być w danych.

**Co się stało 2026-10-26.** Właściciel wykonał pierwszą prośbę: odesłał
`SRW_Y_GLOSY.zip` (3 080 644 B, 17 bundli). Z nich odczytano:

- **683 pilotów** w pięciu tabelach `PilotBasicDatas` — każdy z polem `bvcFile`
  (`REIRE_HA0`, `NAGCV_AH0`, `OSROG_EF0`…), nazwą i `genderType` (0/1 mężczyzna,
  2 kobieta; 127 kobiet);
- **1 198 jednostek** w `RobotBasicDatas` — każda z `ipnameId` (seria), `voiceGroup`
  i `voiceContainer`;
- **34 317 wpisów** `battle_voice Shared Data` z nazwami kluczy (`F321_026`,
  `10A_286`, `D498_001`). Klucze to kody, nie nazwy postaci — żadna inna tabela ich
  nie używa, więc mówcy nie da się z nich odczytać bezpośrednio.

**Czym jest „grupa” (numer `[głos N/39]`).** Bankiem głosów **jednej serii**, nie jednej
postaci. Dowód z treści skrzyżowanej z `ipnameId`: w banku `01999dd0` 100% kwestii, które
nazywają jednostkę, nazywa jednostkę z ダイナゼノン; w `01999de0` — 98% z マジンガー;
w `01999dcc` — 81% z `GTRARK`; **11 z 39** banków przekracza próg (≥20 nazwanych
kwestii i ≥60% udziału). Reszta zostaje numerami — serie mieszają się w nich zbyt mocno.
Szczegóły: `docs/GLOSY_BITEWNE_Y.md`, `docs/VOICE_BANKS_Y.md`.

**Czego jeszcze brakuje.** Kontenera głosu: pliku o nazwie z `bvcFile`, który mówi,
które klucze (`F321_026`…) należą do którego pilota. To 310 bundli, **1 237 239 B**
(same tabele przypisań, zero audio) — druga prośba `SRW_Y_BVC_PROSBA.zip`
(Drive `1QnueT9fKBGkbxh8kGwjJV_FndY-7WJqt`, 9 634 B), opis w
`docs/PROSBA_BVC_Y.md`.

**Co to znaczy dla paczki teraz.** Numer `[głos 7/39]` zostaje i znaczy „mówi ktoś z tej
serii”. Cytaty pisz **bez rodzaju**, dopóki mówca nie jest znany — ale **nie zakładaj
jednej płci na numer**: w jednym banku mówi kilka postaci. Gdy kontenery dotrą, etykieta
zmieni się na `[Cytat bitewny - アムロ (Amuro)]` z płcią z `genderType`, a **same cytaty
zostaną bez zmian** — nic już przetłumaczonego nie trzeba przerabiać.

### Aktualizacja do wersji 7 (2026-10-26, wieczór) — mówca już jest, reszta ma grupy

Kontenery dotarły w trzech paczkach od właściciela i łańcuch został odczytany w całości:

```text
wiersz battle_voice (klucz 01999dc9:15e0b000)
  -> battle_voice Shared Data   (m_Id -> m_Key, np. F069_002)
  -> kontener głosu             (WaveId -> nameText: imię, które gra wypisuje nad kwestią)
```

- **32 402 z 34 317 cytatów (94,4%)** ma imię mówcy z danych gry — 290 różnych mówców;
- **28 763** z nich ma też płeć z `PilotBasicDatas` (`genderType`, dopasowanie po nazwisku
  i po polu `voiceContainer`), więc etykieta to np. `[Cytat bitewny — アムロ (Amuro), m]`;
- pozostałe **1 915 (5,6%)** to kwestie, których zestawu głosu **nie ma w wydanym buildzie**
  (dowód: `GLOSY_BITEWNE_Y.md` §9–10 — sprawdzone wszystkie bundel i zasoby tej klasy).
  **Decyzja właściciela: przekładamy je mimo to**, a żeby nie mieszać rodzaju, każda ma
  numer grupy: `[Cytat bitewny — ??? 012]`. Numer = jedna postać; 138 grup, indeks w
  `09_grupy_bez_mowcy.md` (liczba kwestii, tabela, seria, podpowiedź mówcy/płci).
- **Nic już przetłumaczonego nie trzeba przerabiać**: elementy i numeracja są te same,
  zmienił się tylko tekst w nawiasie kwadratowym.

Dodatkowo: 339 kwestii z tabeli `strategypart_pilotmess` (kwestie pilotów przy częściach)
przeniosło się z „pozostałych tabel” do pliku cytatów, bo to ten sam rodzaj tekstu.

## 2. Wiersze szesnastkowe w `08_pokrewne.md` → tabela wyrzucona z paczki

To tabela `font`: 4 wiersze, których „tekst” to nazwa zasobu czcionki (`a1b2…`, 32 znaki
heksadecymalne). To nie tekst do tłumaczenia i nie da się go zostawić „pustego”, bo gra
podstawia po nim plik czcionki. **W v4 tej tabeli nie ma w paczce w ogóle**, razem
z miejscem na `PL:`. Plik `08_pokrewne.md` zawiera teraz tylko `prologue` (35 krótkich
tekstów wprowadzających).

## 3. Fala `～` → nie używamy, zamiast niej `-` albo nic

- japoński: **134 wiersze** z `～`, głównie jako zakres (`1～3`) i przeciągnięcie w mowie
  (`は～い`), plus ozdobne nagłówki (`～エーアデント ブリッジ～`);
- angielska wersja gry: **0 wierszy** z `～` ani `〜` na 120 665 linii fabuły i 44 344
  elementy tabel — lokalizatorzy angielscy konsekwentnie ją usuwali.

Zasada dla polskiego (w README paczki, sekcja 4): **nigdy nie wpisuj `～` ani `〜`**.
Zakres → `-` (`1-3`), przeciągnięcie → nic (`Tak… no jasne`), nagłówek → `A. Advent -
mostek` (albo półpauza, jeśli edytor tłumacza ją przyjmie — decyduje właściciel przy
składaniu, bo `-` jest już sprawdzony w grze).

## 4. Scena → rozdział / misja → **powiązanie jest w danych misji, nie w skryptach** (poprawione 2026-10-26)

Pierwsza odpowiedź („takiego powiązania nie ma w danych”) była **za szeroka** i została
zawężona do tego, co naprawdę zostało zmierzone — a potem **domknięta**: powiązanie jest
w **danych misji**, które właściciel przysłał (`SRW_Y_MISSION.zip`), i weszło do paczki
**v8**. Poniżej najpierw to, czego nie ma w skryptach (wciąż prawda), potem mapa.

| sprawdzenie | wynik |
|---|---|
| tytuły misji w treści **946 skryptów scen** (cały pakiet japoński) | **15 z 378** tytułów występuje gdziekolwiek, i tylko jako zwykłe słowa w dialogu — ani jednego jako nagłówek sceny |
| jakikolwiek identyfikator misji/sceny w kodzie skryptów | **0** — wszystkie 45 komend `Cmd_*` przejrzane, żadna nie ustawia tytułu ani rozdziału |
| identyfikator pliku `cse20_NNNN_DDDDDDDD` | `NNNN` = blok/scena, `DDDDDDDD` = numer w bloku; nie jest to numer misji |
| etykiety rozdziałów w tabelach | **są**: `system_text` zawiera `CHAPTER 01` … `CHAPTER 07` oraz `ミッションチャート` (ekran mapy misji) |
| tabele tekstów misji | `mission_title` 378, `mission_outline` 200, `mission_detail` 377 — **klucze nie przecinają się między tabelami**, więc misję identyfikuje coś z zewnątrz |

**Gdzie to powiązanie jest.** Nie w tekście scen, tylko w `missionRomList[]` tabel
`Mission*Data` (15 tabel, 18 plików `.bundle`, 321 obiektów `MonoBehaviour`):

```text
missionRomList[]  id m0001_0000310 · chapterNo 1 · name "m0001_0000310：花と忍と誕生日"
                  composition[]  sdemo_file / dlgev_file / script_file
                                 = dokładne nazwy plików scen tej misji
```

Scena `cse20_0001_0000310a` ma tę samą nazwę co `composition.sdemo_file`, więc
przypisanie jest **porównaniem nazwy pliku**, nie kolejności i nie domysłem.

| miara | wynik |
|---|---|
| misje w danych | **533** (podstawka 363 + dodatki 170) |
| misje z rozdziałem 1–7 | **144** |
| sceny w grze | **611** |
| sceny przypisane do misji | **588** — 580 po nazwie pliku, 8 po kluczach `ICE_OP_ADVICE_*` w presetach |
| sceny bez wpisu misji | **23**, wypisane wprost w `docs/MISJE_Y.md` (`cse20_0900_*` samouczek, `cse20_095x_0999900` ekrany systemowe, kilka `0024/0041/0047/1014/8000/9040`) |
| sceny z rozdziałem 1–7 | **188** (rozdz. 1: 14, 2: 42, 3: 35, 4: 21, 5: 24, 6: 29, 7: 23) |

Dla tych 23 sprawdzone i odrzucone: `missionRomList` (brak wpisu), `missionPatchList`
(15 wpisów, żaden ich nie nazywa), klucze `ICE_OP_ADVICE_*` w 277 presetach (brak),
pola `composition` (brak dokładnej nazwy). Etykieta w paczce brzmi wtedy
`misja: brak wpisu misji w danych` — to nie luka w roboty, to pełny wynik wyszukiwania.

**Co dostał tłumacz (paczka v8):**
`spis-scen.md` z kolumnami misja/rozdział, nowy `spis-misji.md` (cały flow: rozdział
1 → 7, misje po numerze z tytułem, liczbą scen i linii, na końcu dodatki), linie
`misja:` / `tytuł misji:` w nagłówku każdej sceny i linia `misja:` przy każdym tytule
w `06_teksty_misji.md`. Numeracja elementów i linie `PL:` bez zmian.

## 5. `鋼鉄ジーグ` i „Getter Robot – The Jet-Black Drifters” → **dane są poprawne**

Tłumacz przeczytał powtórzenie jako drugą, sprzeczną wersję. W `00_postacie.md`:

| element | tekst | znaczenie |
|---|---|---|
| 732 | `[Imię pilota (DLC2)] 鋼鉄ジーグ` → EN `Kotetsu Jeeg` | właściwy wpis |
| 1901 | `[Nazwa serii (DLC2)] 鋼鉄ジーグ` | **powtórzenie elementu 732** — „nie wpisuj tu nic” |
| 1902 | `ダイナミック企画オリジナル（ゲッターロボ 漆黒の漂流者）` → EN „Dynamic Planning Original (Getter Robot – The Jet-Black Drifters)” | inna seria, własny wpis |

Czyli `鋼鉄ジーグ` = **Kotetsu Jeeg** (można też „Jeeg z Kotetsu”), a Getter to osobna
pozycja. W v4 powtórzenia są oznaczone wyraźniej, żeby to nie wracało.

## 6. `$n` / `$c` a rodzaj bohatera → **bohater ma dwie płcie i obie są w grze**

To najważniejsza poprawka v4. Bohater (i bohaterka) to **dwie wersje tej samej postaci**,
wybierane na starcie; scenariusze zawierają **oba warianty tekstu**, a gra pokazuje jeden.

Dowody z danych (nie z domysłów):

| dowód | gdzie |
|---|---|
| jawne znaczniki gałęzi | `{Cmd_BranchProtagonist_Begin, 0}` = `-- 男Ａ分岐開始` (bohater), `{Cmd_BranchProtagonist_Begin, 1}` = `-- 女Ａ分岐開始` (bohaterka), z `_End` — 1 146 par w całym pakiecie (po jednej na wariant i scenę) |
| identyfikator mówcy w każdej kwestii | `pid_MHERO` (bohater) / `pid_FHERO` (bohaterka) — **7 992 kwestii bohatera, wszystkie z identyfikatorem** |
| kwestie innych postaci też się różnią | EN: „Mister $F” vs „Miss $F” dla tego samego japońskiego „$F…さん…” |
| warianty w osobnych blokach | blok, w którym mówi bohater, może się wyświetlić tylko na jego trasie — więc wszystkie linie tego bloku są jednego wariantu |

W v4 każda taka kwestia ma znacznik: **9 034 linii `(wariant: bohater)`, 8 623 linie
`(wariant: bohaterka)`**, reszta (103 008 linii) jest wspólna dla obu tras. Nagłówek sceny
podaje, ile linii ma każdy wariant.

Instrukcja dla tłumacza (README, sekcja 6):

1. linia ze znacznikiem → rodzaj zgodny ze znacznikiem (także formy „pan/zrobiłeś” w
   kwestiach innych postaci);
2. linia bez znacznika → **forma neutralna** (czas teraźniejszy, bezosobowo, strona
   bierna), żeby obie trasy czytały się poprawnie — nie zgadujemy płci;
3. zwroty do bohatera bez znacznika → bez rodzaju („poznać $F”, „z $F”), a nie „pan/pani”;
4. tokeny `$n`, `$c`, `$F` są **bezrodzajowe** — gra podstawia imię, skrót i pełne
   nazwisko; rodzaj nosisz w słowach wokół tokenu.

## Co z tego weszło do paczki v4

| zmiana | efekt |
|---|---|
| znaczniki wariantu płci | 17 657 linii w `sceny.zip`, sekcja 6 README |
| numer grup w cytatach | 34 317 cytatów + 339 kwestii pilotów, sekcja 7 README |
| brak tabeli `font` | 4 wiersze mniej, `08_pokrewne.md` = prolog |
| nowa reguła `～` | sekcja 4 README |
| pełne dodatki | 611 scen / 120 665 linii z **0 brakujących bundli** — odtworzone w tym przebiegu z `srw_y_dlc_bundle.zip` (601) i `srw_y_free_patch.zip` (38) |
| podsumowanie grup w `spis-scen.md` | mapa „gdzie jestem w fabule” bez zmyślania rozdziałów |

Numeracja elementów w plikach scen **nie zmieniła się** wobec v3: 37 plików scen jest
identycznych poza dodanymi znacznikami, więc tłumaczenie zaczęte na v3 przenosi się do v4
przez numer elementu.
