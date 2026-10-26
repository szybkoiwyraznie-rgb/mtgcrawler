# Odpowiedzi dla tłumacza SRW Y — 2026-10-26

Sześć pytań tłumacza z 26 października, odpowiedź i dowód z danych gry. Wszystko jest
też w `README.md` paczki **v5** (`plik_dla_tlumacza_v5.zip`), więc tłumacz nie musi
czytać tego pliku — to jest zapis dla właściciela projektu i dla historii.

Skrót: 1 pytanie (mówcy cytatów) **rozwiązujemy po stronie danych gry** — zamiast
zmyślać, wysłaliśmy prośbę o 17 plików i mamy gotowe narzędzia, które to domkną;
1 wymagało **wyrzucenia tabeli z paczki**, 1 to **reguła pisowni**, 1 wymaga
**decyzji właściciela** (mapa rozdziałów), 1 to **nie błąd danych** (tłumacz źle
przeczytał powtórzenie), a 1 odkryło **realną wadę paczki** — bohater ma dwie płcie
i obie są w grze.

## 1. Cytaty bitewne — mówca jest w danych, tylko nie w tabelach tekstowych

Tabela `battle_voice`: **34 317 kwestii w 39 grupach** (31 w podstawce, 8 w dodatkach).
Poprzednia odpowiedź („mówców nie ma i nie da się ich odzyskać”) była przedwczesna
i właściciel ją odrzucił. Po dokładniejszym rozbiorze klucza wiemy więcej:

**Czym naprawdę jest „grupa”.** Klucz wiersza to 64-bitowy identyfikator wpisu Unity
Localization: `high:low`. Rozbiór `low` na bity pokazuje układ generatora kluczy Unity
(`DistributedUIDGenerator`: 41 bitów czasu, 10 bitów numeru maszyny, 12 bitów sekwencji):
w 32 205 z 34 317 wierszy numer maszyny wynosi `523` (`0x20B`), a sekwencja nie
przekracza 148 — czyli klucze powstały **partiami, po ~1 000 wpisów na partię, mniej
więcej co sekundę**. `high` jest w obrębie partii stały, a partii jest dokładnie tyle, ile
grup. Innymi słowy: **grupa = jeden zestaw głosów jednej postaci, importowany w jednym
przebiegu** (932–2 079 kwestii na grupę). To już nie domysł — to odczyt struktury klucza.

**Czego brakuje.** Nazwy mówcy nie ma ani w tabeli `battle_voice`, ani w żadnej z 143
tabel tekstowych (sprawdzone: `high` grup nie występuje w `pilot_name`, `dic_text_pilot`,
`voiceactor`; hashe nazw — crc32, fnv1a, murmur3, md5, sha1 — nie dają żadnego z 39
numerów; **0 z 34 317** cytatów występuje w którejkolwiek linii fabuły). Nazwa siedzi
w **danych gry**, nie w tekstach: w `battle_voice Shared Data` (Unity trzyma tam nazwy
kluczy wpisów) i w `PilotBasicDatas` (pilot ma tam przypisany zestaw głosu).

**Co zrobiliśmy w tej rundzie:**

1. **Prośba do właściciela o 17 plików danych** (~3 MB, nie gigabajty):
   `docs/PROSBA_VOICE_SPEAKERS.md` + `tools/collect_voice_speaker_data.ps1`. Skrypt
   kopiuje konkretne bundle (adresy rozwiązał katalog gier) i pakuje zip na pulpit.
2. **Narzędzia, które domkną mapowanie w chwili, gdy pliki dotrą:**
   `tools/voice_bank_map.py` (czyta `Shared Data` i `PilotBasicDatas`, łączy identyfikator
   zestawu głosu z grupą; ma `--self-check` na danych syntetycznych),
   `tools/voice_catalog_codes.py` (398 kodów postaci z nazw klipów, np. `AMRO_001_A`),
   `tools/voice_bank_content.py` (dowody z treści: zaimki `俺`/`私`/`あたし` i nazwy
   własne per grupa), `tools/voice_identify_speaker.py` (`--phrase` — szukanie grupy po
   znanym okrzyku, `--anchors` — spójność przypisań, `--candidates` — hipotezy z nazw
   wyłącznych).
3. **Dowody z treści** (bez zgadywania): w grupie `00000411` pada „ブライ・ソード!”,
   w `0001168c` — „ダ・ガーン!”, w `0000157d` — „イデオンソード!”. To poszlaki, nie
   przypisania: te same nazwy padają w cudzych kwestiach („来い、蜃気楼蛟!” nie znaczy,
   że mówi pilot 蜃気楼), dlatego imiona podmienimy dopiero po odczycie danych.

**Co to znaczy dla paczki teraz.** Numer `[głos 7/39]` zostaje (ten sam numer = ta sama
postać, zawsze), a cytaty pisz **bez rodzaju**, dopóki mówca nie jest znany. Gdy dane
dotrą, etykieta zmieni się na `[Cytat bitewny — アムロ (Amuro)]`, a **same cytaty zostaną
bez zmian** — nic już przetłumaczonego nie trzeba przerabiać.

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

## 4. Scena → rozdział / misja → **nie ma tego powiązania w danych**

Sprawdzone: `cse20_NNNN_DDDDDDDD` to identyfikator pliku (NNNN = blok plików, reszta =
numer sceny w bloku); tytuły misji leżą w osobnej tabeli `mission_title` (378 pozycji,
w kolejności gry: prolog, potem rozdział po rozdziale — bloki `a020`, `a0e0`, `a120`,
`a160`, `a1a0`, `a260`, `a2a0`, `a2e0`, `a320`). **Tytuły misji nie występują w treści
żadnego skryptu sceny** (sprawdzone na całym pakiecie jap.), więc nie ma po czym złączyć
sceny z misją. Nazw rozdziałów w danych również nie ma.

Co dostaje tłumacz zamiast zmyślonej mapy:

- `spis-scen.md`: 611 scen w kolejności gry (grupa, identyfikator, plik, mówcy, liczba
  linii) + na górze **podsumowanie grup** (`odcinek-00` … `odcinek-11`, dodatki) z liczbą
  scen i linii;
- `06_teksty_misji.md`: tytuły i opisy misji w kolejności gry.

Sceny i tytuły idą tą samą kolejnością, więc tłumacząc po kolei, tłumacz wie, gdzie jest
w fabule. Prawdziwe „scena → rozdział” wymaga tabeli etapów z gry — jeśli właściciel ją
dostarczy (zrzut listy misji z nazwami albo tabela etapów), dorobimy mapę.

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
