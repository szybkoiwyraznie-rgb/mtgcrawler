# Pokrycie celu — audyt kategorii (stan 2026-10-12, sesja 5)

Cel (z `docs/GOAL.md`): **100% przygotowanego tekstu** przetłumaczone na angielski i wstrzyknięte
z powrotem — sceny fabuły z mówcą, cytaty bitewne z mówcą, imiona ↔ postacie (encyklopedia),
mechy ↔ bronie, itemy z opisem działania, UI i helpy. **100% kluczy** dla każdego typu danych.
Zapis w trybie **grow** wszędzie, gdzie struktura na to pozwala; stała szerokość tylko tam, gdzie
struktura pliku tego wymaga. Fakty oznaczam `[ZWERYFIKOWANE]`, hipotezy `[HIPOTEZA]`.

Ten dokument jest mapą: co jest zrobione, co blokuje, w jakiej kolejności domykać.
Nie jest planem tłumaczenia — tłumaczenia startują dopiero po domknięciu setupu (decyzja użytkownika).

## 1. Tabela zbiorcza

| # | Kategoria | Źródło | Wyekstrahowane / zweryfikowane | Zapis | Stan | Główne braki |
|---|---|---|---|---|---|---|
| 1 | Dialogi fabuły | `eventP00`–`P32`, `evept101–108` (32 kontenery, 293 członki) | **26 468 linii, 313 kluczy (100% z nazwą), 1 186 781 B tekstu** (`tools/event_dialogue.py`) **+ 360 tekstów innych typów** (narracja 136, warunki zwycięstwa/porażki 149, lokacje 41, help 19, tytuły scen 6, etykiety 9) **+ 273 teksty w blokach-tabelach** (13 KB) | **grow — sprawdzony w grze** | **ekstrakcja domknięta** (0 błędów, 0 nieczytelnych rekordów) | stara liczba 12 738 linii była zaniżona ~2× (stary chodzik kończył na granicy bloku); brak kroku `apply`; 4008 bloków to tabele (nie tekst), 137 z nich ma teksty – wyekstrahowane |
| 2 | Cytaty bitewne | `mesbtl00`–`mesbtl31` (32 kontenery) | **29 577 cytatów, 319 kluczy, 814 683 B tekstu, 0 błędów**; **300/319 kluczy ma nazwę** z tabeli postaci | grow (rozmiary rekordów + łańcuch EVNT) | **ekstrakcja + nazwy domknięte** | 19 kluczy bez rekordu w tabeli postaci: 5 to sloty zastępcze z pustym tekstem (3/6/7/8/991), 3 to także id jednostek (50/1005/1051), 11 (55, 60, 101, 151, 733, 1037, 1048, 3122, 3702, 3707, 3712) nadal bez nazwy – 1 182 rekordy cytatów; ścieżka `apply` jeszcze nie zbudowana |
| 3 | Imiona (mówcy) | `srwDL_CharaDictionary` + sloty `config*` | **339 kluczy, 301 nazwanych** (dialog 99,5%) | grow (pula NUL) | prawie domknięte | 14 kluczy dialogowych + 24 bitewne bez źródła nazwy; 2 klucze z podwójnym rekordem |
| 4 | Encyklopedia postaci | **nie zlokalizowana** | `CharaDictionary` = tylko nazwy i tytuły serii (max 43 B); `srwDL_Reference` = help/tutorial | — | **brak tabeli** | trzeba znaleźć tabelę biografii (kandydaci niżej) albo udowodnić, że jej nie ma |
| 5 | Mechy ↔ bronie | `config00`–`config19` | **393 jednostki, 1485 broni, 41 tytułów serii**, 74 katalogi modeli | grow (tabele + pule) | domknięte dla danych | semantyka pól 88–134; 91 jednostek bez serii; 24 pary modeli poza `robo00` |
| 6 | Itemy + opisy | `srwDL_Item00` + pule DLC (`config*`), `configst/srwDL_Item` | 2300 rekordów, **1929 stringów / 22,5 KB** (510 unikalnych) | grow (pary zakresów) | ekstrakcja tak, role pól nie | role pól w rekordzie; nazwa itemu ↔ klucz; opisy efektów częściowo w `srwDL_DLC_ID` |
| 7 | Umiejętności + opisy | `srwDL_Skill00` + pule DLC | 7380 rekordów, **9128 stringów / 142 KB** (3036 unikalnych) | grow (pary zakresów) | ekstrakcja tak, role pól nie | role pól; powiązanie z tagami (`srwDL_Skill_Tag`, 288 unikalnych) |
| 8 | Helpy / UI / system | `configst/sysmes.bin`, `srwDL_Reference`, `srwDL_DLC_ID`, `srwDL_Spirit`, `srwDL_Skill_Tag`, `srwDL_Achievement`, `srwDL_StatusChange` | sysmes 1182 wpisy ≈38 KB; Reference 230 stringów/17,4 KB; DLC_ID 279/10 KB; Spirit 342/9,3 KB; Skill_Tag 294/2,8 KB; Achievement 81/1,4 KB; StatusChange 311/2,3 KB | mieszany: sysmes=stała/shift, reszta grow | częściowo | UI stałej szerokości: budżety znaków; `mesbmp*` (obrazy); menu tytułowe tylko equal-length |
| 9 | Mapy / shop / drop | `srwDL_Map_S`, `lmaplist`, `srwDL_Shop00`, `srwDL_ItemDrop` | Shop 182 rekordy (19 z tekstem, żadna nie jest nazwą itemu); ItemDrop 1092 rekordy (5 stringów) | do ustalenia | **niezdekodowane** | nazwy map/terenów i nazwy itemów w sklepie — nie zlokalizowane |

Razem dla tabel z pkt 6–8 (`tools/config_text_tables.py`, 20 kontenerów + `configst`):
**11 254 rekordy, 12 599 stringów, 208 KB tekstu; unikalnych 4208 (3518 z kanji/kana), 89,3 KB.**
Cytaty bitewne (pkt 2, `tools/battle_quotes.py`): **29 577 rekordów, 814,7 KB tekstu, 319 kluczy.**

## 2. Klucze — stan (wymaganie „100% kluczy”)

| Typ danych | Klucz | Pokrycie |
|---|---|---|
| Jednostki (mechy) | `unit_list` +84 = `wp_list` u32 = `RoboDictionary` +28 = `unit_index_list` kol. 1 | **393 / 393 (cała gra)** `[ZWERYFIKOWANE]` |
| Bronie | pozycja wpisu w rekordzie `wp_list` jednostki (nazwa `.bsb` = `s<id>_<nnn>`) | **1485 / 1485** `[ZWERYFIKOWANE]` |
| Mówcy | u16 w rekordzie dialogu +10 → `CharaDictionary` +0x40 | 339 kluczy; 301 z nazwą (99,5% linii) |
| Cytaty bitewne | u16 klucza w rekordzie 0xC9 (nazwa członka `p<NNN>.pac` to *zestaw*, nie mówca) | **319 kluczy** `[ZWERYFIKOWANE]` (poprzednie 241 liczyło tylko rekordy zgodne z nazwą członka) |
| Itemy | u16 na +0 rekordu `srwDL_Item` (np. 10000, 10019) | 300 kluczy na płycie + pule DLC; mapowanie nazwa↔klucz niepotwierdzone |
| Skille | rekord `srwDL_Skill` (1469 na płycie + pule) | klucz nieustalony |
| Tytuły serii | `RoboDictionary` po id jednostki | 302 / 393 jednostek ma rekord |

## 3. Nowe narzędzie tej sesji

`tools/config_text_tables.py` (read-only, 16 testów syntetycznych) — ekstrahuje **każdy** przebieg
tekstu z tabel `Item`, `Skill`, `Reference`, `DLC_ID`, `Spirit`, `Achievement`, `Skill_Tag`,
`StatusChange`, `ItemDrop` wraz z dokładną lokalizacją (kontener, członek, rekord, offset).
Zapis: `local/text_tables/*.jsonl` + `unique_strings.jsonl` + `summary.json` (gitignored).

Zmierzona budowa tabel `[ZWERYFIKOWANE]`:
- **Konwencja A**: `u32 liczba` pod +0, offsety rekordów od +4; pierwszy offset = 4 + 4·liczba.
- **Konwencja B**: `u32 offset ogona` pod +0, `u32 liczba` pod +4, offsety od +8; rekordy kończą się
  pod offsetem ogona, a dalej leży **pula ogonowa** (teksty-fragmenty), też wyciągana.
- **Konwencja C**: `u32 start tablicy` pod +0 (zawsze 8), `u32 0` pod +4, tablica od +8 do wartości
  `u32[8]` (samoograniczająca się); wpisy to offsety stringów puli. Tak zbudowane są pliki DLC
  `Item01–08`/`Skill01–08`.
- **Referencje** (`srwDL_Reference`): 8 wskaźników u32 na początku rekordu celuje w tekst; reguła
  trafienia (wskaźnik na bajt drukowalny po bajcie NUL lub bajcie sterującym) zgadza się w **28/28**
  rekordach `Reference00`. `Reference03` = 3/4, `Reference08` = 0/1 (warianty DLC, otwarte).
- **Dekodowanie**: przebieg czysty = CP932 bez znaków sterujących (poza `\n`) i bez private-use;
  dzięki temu opis efektu `%s2倍\n5%s` (bez kanji) też jest wyciągany.

Pomiar relacji DLC ↔ płyta `[ZWERYFIKOWANE]`: pula `srwDL_Item01–08` jest podzbiorem puli ogonowej
`Item00` (75/75 tekstów bez nowych); pula `Skill01–08` zawiera wszystkie 583 teksty ogona `Skill00`
plus ~239 jedno- do trzyznakowych fragmentów formatujących. **DLC nie wnosi nowych tekstów itemów/skilli.**

## 3a. Cytaty bitewne — domknięcie (pkt 2)

`tools/battle_quotes.py` (read-only, 11 testów syntetycznych). Zmierzona budowa `[ZWERYFIKOWANE]`:
- członek `p<NNN>.pac` = łańcuch bloków `EVNT`; blok = tag + `u32 rozmiar` liczony **od pola rozmiaru**
  (blok kończy się dokładnie tam, gdzie zaczyna się następny tag `EVNT`);
- w bloku: `u32 0`, potem rekordy `u32 typ, u32 rozmiar` (rozmiar liczony od pola typu);
  typ **200** opakowuje, typ **201** (0xC9, ten sam co dialogi) to cytat;
- ładunek 0xC9: `u16 0x0029` (podtyp w dolnych 12 bitach; górny nibble to flagi — 0x8029 też występuje),
  `u16 klucz mówcy`, `u16 flagi`, `u16 0`, `u16 0`, `u16 id` (głos/asset, 0xFFFF = brak), tekst CP932 + NUL;
- **klucz mówcy jest w rekordzie, nie w nazwie pliku**: `p0050.pac` zawiera rekordy kluczy 50, 55, 60, 101, 151;
  `p0408.pac` zawiera klucze 407 i 405 (dlatego stara sonda liczyła dla niego 0 rekordów);
- w 32 kontenerach występują wyłącznie typy 200 i 201, a **wszystkie 29 577 rekordów typu 201 mają podtyp 41
  i wszystkie zostały wyekstrahowane** (0 błędów łańcucha) — pokrycie 100%.

## 3a2. Dialogi fabuły — pełna reekstrakcja (pkt 1)

`[ZWERYFIKOWANE]` `tools/event_dialogue.py` (10 testów). Tekst scen nie siedzi w jednym typie rekordu:
**0xC9** (dialog, nagłówek 12 B, klucz mówcy) = 26 468 linii; **0x1B7** (narracja, tekst od +4) = 136;
**0x1B4/0x1B5** (warunki zwycięstwa/porażki, tekst od +0) = 74/75; **0x152** (nazwy lokacji, +4) = 41;
**0x1FC** (help/tutorial, +4) = 19; **0x1B6** (tytuł sceny, +12) = 6; **0x14A/0x14F/0x1BA** (etykiety) = 9.
Dla typów innych niż 0xC9 pozycja tekstu jest **mierzona** (pierwszy czysty przebieg CP932 z ≥2 znakami
japońskimi), nie zakładana. Bloki bez łańcucha rekordów to tabele parametrów — 4008 z 5320 bloków;
137 z nich zawiera tekst wyświetlany (warunki misji, proza), raportowany jako `embedded`.
Razem: **27 101 pozycji tekstu / ~1,22 MB**. Nazwy: **313/313 kluczy** z tabeli postaci.

## 3b. Nazwy mówców — tabela postaci `charalist` (pkt 4/5)

`[ZWERYFIKOWANE]` `tools/charalist_table.py` (7 testów). Tabela `charalist<NN>.bin` wewnątrz
`config<NN>.pac` to tablica rekordów **172 B**: nazwa skrócona +0, pełna +32, wąska +76 (z tokenami
0x0F), **klucz mówcy u16 +96**, alias +100, pole grupy +102. 16 członków, **404 rekordy, 404 klucze**
(unikalne, rosnące w członku). Pokrycie: **313/313 klucze dialogów** (26 468 linii) i
**300/319 kluczy cytatów**. Brakujące 19 kluczy cytatów: 3/6/7/8/991 to sloty zastępcze z pustym
tekstem, 50/1005/1051 to również id jednostek (ガンバルガー, ガンキャノン, ザクⅡ), pozostałe 11
(55, 60, 101, 151, 733, 1037, 1048, 3122, 3702, 3707, 3712 → 1 182 rekordy) bez źródła nazwy.

## 3c. Rama `EVNT` — wspólny czytnik dla cytatów i scen (`evnt_walk.py`)

`[ZWERYFIKOWANE]` Dwa warianty tego samego formatu bloków:
- **mesbtl**: `EVNT` + u32 rozmiar (liczony od pola rozmiaru), ładunek od słowa zerowego, łańcuch rekordów;
- **eventy**: nagłówek pliku `EDAT` (u32 rozmiar, u32 liczba bloków), `EVNT` + u32 rozmiar (liczony od
  tagu), potem u32 rodzaj, `ECHK` + u32 oraz słowa nagłówka i dopiero łańcuch rekordów.
Reguła końca bloku jest dobierana per blok przez dopasowanie do następnego tagu `EVNT` (rozbieżność
= zgłoszony błąd, nigdy ciche założenie). Łańcuch rekordów znajduje się przez skanowanie pierwszych
64 B ładunku; rekord 0xC9 ma w cytatach kotwicę 0x0029 (maska 0x0FFF), a w dialogach własne słowo
flag (0x0001/0x0009/0x0011/0x0019) — dlatego test kotwicy jest opcjonalny. Po refaktorze narzędzie
cytatów daje identyczne wyniki jak przed nim (29 577 rekordów, 0 błędów), co jest regresją pilnowaną
testami.

## 4. Znaleziska audytu (nowe lub korygujące)

1. `imenu00.cpk` to **duplikat** zawartości `config00.pac` (te same 6 członków), nie osobny kontener —
   encyklopedii tam nie ma.
2. Encyklopedii postaci **nie ma** w `CharaDictionary` (najdłuższy tekst 43 B = tytuły serii) ani
   w `RoboDictionary` (najdłuższy 52 B; są tam listy pilotów, np. „パイロット：…”).
3. `configst.pac` zawiera 21 członków, w tym całe kategorie tekstu dotąd niekatalogowane:
   `srwDL_Spirit` (komendy duchowe — nazwy i opisy), `srwDL_Achievement` (trofea),
   `srwDL_Skill_Tag`, `srwDL_StatusChange`, `srwDL_ItemDrop`, `srwDL_Dmg`, `srwDL_CalcType`.
   `srwDL_Item` w configst jest identyczny rozmiarem z `Item00` z config00.
4. `srwDL_DLC_ID` zawiera **opisy zakupów** („部隊パーツをダウンロードします。…”), nie tylko tytuły —
   to największy nowy zasób tekstu w tej sesji po skillach.
5. **Korekta liczby kluczy cytatów**: stara metoda (klucz = nazwa członka) dawała 241 kluczy i 22 902
   rekordy; prawdziwe wartości to **319 kluczy i 29 577 rekordów** — 78 kluczy i 6 675 rekordów było
   pomijanych, bo siedzą w członkach nazwanych innym kluczem.
6. **Tabela postaci znaleziona**: `charalist<NN>.bin` (rekord 172 B, klucz u16 +96, 404 rekordy) —
   daje nazwę dla 100% kluczy dialogów i 94% kluczy cytatów. Poprzednia teza „layout nierozwiązany”
   jest nieaktualna.
7. **Rama `EVNT` wyjaśnia 42 członki bez łańcucha**: członki `eventP*` mają nagłówek `EDAT` i inny
   licznik rozmiaru bloku niż `mesbtl`; po uwzględnieniu obu wariantów łańcuch rekordów znajduje się
   (sprawdzone na `DL104_20.bin`, `SM001.bin`, `DL100_01.bin`).
8. `srwDL_Shop00` (182 rekordy) nie zawiera nazw itemów — 19 rekordów ma tekst, żaden nie jest nazwą
   itemu ani broni; nazwy w sklepie są czytane z innej tabeli (do znalezienia).

## 5. Plan domykania (kolejność i definicja „gotowe”)

Dla każdej kategorii „gotowe” znaczy: (a) ekstrakcja 100% z lokalizacjami, (b) ścieżka grow
zbudowana i `verify` przechodzi, (c) `apply` wkleja tłumaczenie, (d) przebieg bez zmian = bajt w bajt,
(e) test w grze. Poniżej kolejność prac — od blokad do wygody.

1. ~~Cytaty bitewne — odblokować granice rekordów.~~ **ZROBIONE (sesja 5)**: 29 577 cytatów z 319 kluczy,
   0 błędów. Pozostaje: ścieżka `apply` (przebudowa rozmiarów 200/201 i bloków `EVNT`) + scalenie z nazwami mówców.
2. **Nazwy mówców dla 319 kluczy cytatów** — przecięcie ze słownikiem postaci (`CharaDictionary` +0x40)
   i tabelą `name_union`; to domknie wymaganie „cytaty z imionami”.
3. **Narracja i warunki misji — domknięte przy okazji pkt 1** (360 tekstów innych typów + 273 embedded).
4. **Encyklopedia (pkt 4) — znaleźć albo zamknąć pytanie.** Sprawdzić kolejno: `system.cpk`, `navisys`,
   `tacsys`, `u16tbl.cpk`, `mesbmp00` (obrazy?), `celldata.bin`, `SRW_DL.acf`. Jeśli biografii nie ma,
   ustalić z użytkownikiem, czy „encyklopedia” ma być zbudowana z `CharaDictionary` + tytułów serii
   (dane, które gra ma), czy dopisana jako treść redakcyjna.
5. **Skille (pkt 7, 142 KB) — role pól.** Para (start, koniec) w rekordzie + tabela u16 pod +40;
   potwierdzić na próbce nazwę/opis/skrót, potem arkusz i ścieżka grow (przebudowa par).
6. **Itemy (pkt 6) — to samo dla itemów** + powiązanie klucza itemu z nazwą i z opisem zakupu
   w `srwDL_DLC_ID`.
7. **Helpy/UI (pkt 8) — budżety znaków.** Dla `sysmes.bin` (menu tytułowe = equal-length, opisy =
   shift) zmierzyć sloty i szerokości; `srwDL_Reference` (17 KB) i pozostałe tabele configst —
   ekstrakcja jak w pkt 3–4.
8. **Mapy/shop (pkt 9)** — zlokalizować nazwy map/terenów i nazwy itemów w sklepie.
9. **Arkusz scalony** — jeden plik wszystkich kategorii (klucz, źródło, japoński, angielski,
   maks. długość, tryb zapisu) + kontrola 100% pokrycia wobec tego dokumentu.
10. **Apply po kategorii** + repack + test w PPSSPP (dla każdej kategorii osobno, potem razem).

Zadania z kolejki, które nie są blokadą, ale zostają: 42 członki bez łańcucha (`event`), 14 kluczy
dialogowych bez nazwy, semantyka pól `unit_list` 88–134, `robo01`+ dla 24 par modeli.
