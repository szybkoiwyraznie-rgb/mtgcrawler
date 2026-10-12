# Tłumaczenie Super Robot Taisen OE — instrukcja krok po kroku

Ten dokument jest **jedyną** instrukcją procesu. Opisuje, co tłumaczysz, w jakiej kolejności,
w jakim pliku i jak odesłać pracę. Nie trzeba znać JSON-ów, Excela ani żadnego z naszych narzędzi —
tłumaczy się **tekst w plikach `.md`**, po znaczniku `EN:`.

---

## 0. W skrócie

1. Rozpakowujesz **`sceny.zip`** — to fabuła (dialogi, narracja, warunki misji, tytuły misji).
2. Rozpakowujesz **`widoki.zip`** — to nazwy i tabele (postacie, mechy i bronie, cytaty bitewne,
   przedmioty, umiejętności, teksty interfejsu, teksty misji).
3. W każdym pliku pod każdym japońskim tekstem jest linia `EN:` — wpisujesz angielski **po dwukropku**.
4. Odsyłasz pliki **tak jak są** (może być zip) — nie zmieniasz nazw, nie przenosisz niczego do JSON.
5. Całą resztę robią nasze narzędzia: wpisanie tekstu do pakietu, uzupełnienie powtórzeń,
   sprawdzenie limitów i znaków.

**Co dostajesz — dokładnie trzy rzeczy i nic więcej:**

| plik | co to jest |
|---|---|
| `README.md` (ten dokument) | instrukcja |
| `sceny.zip` | fabuła: 37 plików `.md` (spis scen + odcinki + symulator) |
| `widoki.zip` | nazwy i tabele: 7 plików `.md` |

Do wypełnienia w całym pakiecie: **67 440 linii `EN:`**
(26 035 w fabule + 41 405 w widokach). Poza tym jest **5 146 elementów bez linii `EN:`** — to
powtórzenia tego samego tekstu w grze (np. nazwa serii przy każdym mechu z tej serii); tłumaczenie
dziedziczy się tam automatycznie, nie wpisuje się nic (patrz „Elementy bez linii `EN:`").

---

## 1. Zasady, które trzeba znać przed startem

1. **Piszesz tylko po `EN:`.** Linia japońska nad `EN:` jest nienaruszalna — to ona trzyma numer
   elementu, po którym narzędzia znajdują miejsce w grze.
2. **Nie zmieniasz numerów ani kolejności elementów** (`1.`, `2.`, `3.`). Możesz dopisywać tekst,
   nie możesz przesuwać ani usuwać linii elementu.
3. **Nie zmieniasz liczby przejść do nowej linii** wewnątrz tekstu. Jeśli japoński tekst łamie się
   na trzy linie, angielski też ma się łamać na trzy linie (w tym samym miejscu mniej więcej).
   Przejścia **na samym końcu** tekstu dodają się same — nie trzeba po nich zostawiać pustej linii.
4. **Nie tłumaczysz znaków specjalnych** — zostają dokładnie takie, jakie są: `＃` (mówca nieznany),
   `%s`, `%%`, `＠0`, `＠1`, `＠4`, `＠6`, `＠9` (podstawiane przez grę liczby i nazwy).
5. **Jedna nazwa — jedna pisownia** w całym pakiecie. Nazwy własne (postacie, mechy, bronie, serie)
   mają osobne pliki — tam je ustalasz, a w dialogach i cytatach ich używasz.

### Znaki, których gra nie wyświetli

Gra używa zestawu **CP932** (japoński Windows). Znaki spoza niego **nie wejdą do gry** —
nasze narzędzie odrzuci taką linię i zgłosi to.

| wolno | nie wolno |
|---|---|
| `―` (kreska japońska U+2015), `…`, `‘ ’ “ ”`, `°`, `×`, `→`, `★`, `〜`, `♪`, `①`, `Å` | `—` (U+2014), `–` (U+2013), `„`, `•`, `♥`, litery z akcentami (`é ä ö ñ ç å ø`) |

Zamiast `—` pisz `-` albo `―`. Zamiast `José` pisz `Jose`. Pełna szerokość japońska (`Ａ`, `１`, `％`)
jest dostępna, ale **dla angielskiego używaj zwykłych liter i cyfr** — chyba że tekst w grze stoi
w polu pisanym czcionką półszeroką (patrz `<0x0F>` niżej).

### Długość tekstu — czytaj linię `limit:` pod każdym elementem

Pod **każdym** elementem do przetłumaczenia jest linia `limit:` mówiąca, ile wolno napisać. Są trzy
rodzaje tej linii:

| linia `limit:` | co znaczy |
|---|---|
| `limit: 117 B (stała szerokość — dłuższe się nie zmieści)` | **twardy limit**. Miejsce w grze ma dokładnie tyle bajtów; dłuższy tekst **nie zostanie wpisany** (narzędzie go odrzuci i poda, o ile trzeba skrócić). Jeden znak japoński = 2 B, jeden znak angielski = 1 B. |
| `limit: 46 jedn. na linię (gra sama używa do 52 jedn.); oryginał: 3 linii` | tekst rysowany w oknie gry. Długość całego tekstu jest dowolna (gra przebudowuje rozmiary), ale **każda linia** ma się mieścić: trzymaj się 46, absolutne maksimum zmierzone w grze to 52 jednostki (jednostka = szerokość połowy znaku; znak japoński ma 2). `oryginał: N linii` mówi, na ile linii łamał się japoński — **zostaw tyle samo**. |
| `limit: bez twardego limitu (pole rośnie) — trzymaj się długości oryginału (najdłuższy w tej kategorii: 18 jedn.)` | nazwy w listach, serie, opisy. Długość jest dowolna, ale interfejs gry ma stałą szerokość listy — **nie przekraczaj długości oryginału** więcej niż o ~⅓. Liczba w nawiasie to najdłuższy oryginał w tej samej kategorii: to praktyczna granica. |

Uwaga: „dowolna długość" przy dialogach **nie znaczy „bez konsekwencji"** — tekst wpisany do gry
musi się jeszcze mieścić w oknie. Dlatego liczba linii i szerokość linii są w limicie, a nasze
narzędzia odrzucają linię szerszą niż 52 jednostki.

### Elementy bez linii `EN:` (dziedziczenie)

W grze ten sam tekst jest często zapisany **wielokrotnie**: nazwa serii powtarza się przy każdym
mechu z tej serii (w plikach gry to jedno wspólne pole, do którego odwołuje się każdy mech), opis
efektu przedmiotu przy każdym przedmiocie, który go używa, aktor głosowy przy każdej postaci,
którą gra. Żebyś nie pisał tego samego dwadzieścia razy (i żeby to nie wyszło dwadzieścia razy
inaczej), powtórzenia **nie mają linii `EN:`**, tylko dopisek:

```
3. [Seria] 絶対無敵ライジンオー
   (ten sam tekst co wcześniej — tłumaczenie dziedziczy się automatycznie, nic tu nie wpisuj)
```

Takich elementów jest 5 146. Tłumaczysz **pierwsze wystąpienie** (ono ma `limit:` i `EN:`), a reszta
dostaje ten sam angielski automatycznie. Jeśli chcesz — możesz w pierwszym wystąpieniu napisać
krótszą wersję i wspólną dla wszystkich; jedna pisownia na cały pakiet jest tym, czego chcemy.

---

## 2. Krok 1 — fabuła: `sceny.zip`

Rozpakuj `sceny.zip`. W środku jest 37 plików: `spis-scen.md` (lista wszystkich 293 scen)
oraz `epizod-00.md` … `epizod-34.md` + `simulator.md`.

Zacznij od `spis-scen.md` — to spis treści: numer sceny, odcinek, misja, miejsce. Każdy plik
odcinka to sceny **w kolejności gry**.

### Jak wygląda scena

```
## Scena 1/293 — 初等訓練
- odcinek: ０話 メインミッション (episode 0)
- miejsce: コネクト・ステーション／格納庫 (element 74)
- uczestnicy:
  - セイシロウ・クサナギ — スーパーロボット大戦 オリジナル
  - ヒマリ・ヤエガキ — スーパーロボット大戦 オリジナル

T1. [Tytuł misji] 初等訓練
   EN:
N1. [Uwaga do misji (pole powtarzane w grze — jeden tekst)] このミッションは出撃ユニットが固定されています。
   EN:
1. [Dialog - セイシロウ・クサナギ] （俺は今、宇宙貿易事業を推進する
   　民間組織『コネクト』にいる…）
   EN:
2. [Dialog - セイシロウ・クサナギ] 感度良好だ！
   ミッションをはじめよう。
   EN:

_koniec sceny_
```

Co jest czym:

* **`## Scena 1/293 — …`** — numer sceny (kolejność gry) i japoński tytuł misji.
* **`- odcinek:` / `- miejsce:`** — kontekst: który odcinek i gdzie scena się dzieje
  (miejsce też jest do przetłumaczenia — jako element w środku sceny).
* **`- limit:`** — ile wolno napisać w tej scenie (dialog 46 jednostek na linię, narracja 50).
  Szczegóły w sekcji 1.
* **`- uczestnicy:`** — wszystkie postacie mówiące w tej scenie, po japońsku, z **serią**, z której
  pochodzą. To podpowiedź dla Ciebie — nie tłumaczy się tego.
* **`T1. [Tytuł misji]`** — tytuł misji (widać go w menu gry). Wpisujesz go tutaj, w scenie, w której
  się pojawia. Jeśli scena dzieli tytuł z inną sceną, dopisek mówi o tym — wtedy tłumaczysz go raz.
* **`N1.`, `N2. [Uwaga do misji]`** — dodatkowe uwagi do misji (np. „jednostki są ustalone").
  Jeśli oba pola w grze trzymają ten sam tekst, jest jedno `N1` z dopiskiem „pole powtarzane w grze".
* **`1. [Dialog - セイシロウ・クサナギ]`** — kwestia dialogowa. Nazwa po myślniku to mówca.
  Inne rodzaje: `[Narracja]`, `[Miejsce]`, `[Warunek zwycięstwa]`, `[Warunek porażki]`,
  `[Etykieta]`, `[Tekst misji]`, `[Pomoc]`, `[Nagłówek miejsca]`.
* **`[kopia]`** — ten element powtarza kwestię z innej sceny (wersja DLC). **Nie ma linii `EN:`** i
  nic się tam nie wpisuje — tłumaczenie dziedziczy się samo.
* **`_koniec sceny_`** — koniec sceny. Nie usuwaj tej linii.

### Jak wypełniać

```
2. [Dialog - セイシロウ・クサナギ] 感度良好だ！
   ミッションをはじめよう。
   EN: Loud and clear!
   Let's begin the mission.
```

* Tekst wpisujesz **w linii `EN:`**, po dwukropku.
* Jeśli tekst ma więcej linii, piszesz je w kolejnych liniach **z takim samym wcięciem** (3 spacje) —
  dokładnie tyle linii, ile łamie się japoński.
* `⏎` w tekście japońskim = wymuszone przejście do nowej linii. **Zostaw `⏎` w swoim tekście**
  w tym samym miejscu — nie zamieniaj go na zwykłą nową linię.
* `<0x0F>` = gra przełącza czcionkę na półszeroką (tak są pisane skróty w nazwach broni).
  **Zostaw `<0x0F>`** w tym samym miejscu; tekst po nim pisz zwykłymi literami.
* Nie znasz mówcy? W nagłówku jest `ID 3122` zamiast imienia — wtedy pisz tak, żeby pasowało do
  postaci widocznej w grze (neutralny ton).

### Kolejność pracy

Możesz tłumaczyć odcinkami (plik = jeden odcinek). Po każdym pliku nic nie trzeba robić — pliki
wracają do nas razem.

---

## 3. Krok 2 — nazwy i tabele: `widoki.zip`

Rozpakuj `widoki.zip`. W środku jest siedem plików — każdy obejmuje jedną kategorię gry:

| plik | co zawiera | linii `EN:` | dziedziczy |
|---|---|---|---|
| `postacie.md` | imiona, przezwiska, serie, aktorzy głosowi, wersje imion (pełne/krótkie/wąskie) | 1 807 | 484 |
| `cytaty.md` | kwestie bitewne, pogrupowane po mówcy | 19 841 | 0 |
| `mechy.md` | nazwy jednostek, serie, długość, masa **oraz wszystkie bronie** | 2 303 | 2 042 |
| `przedmioty.md` | nazwy przedmiotów i opisy efektów | 443 | 757 |
| `umiejetnosci.md` | nazwy umiejętności i opisy efektów | 3 069 | 1 863 |
| `teksty-config.md` | teksty menu i ekranów (sekcjami: umiejętności, przedmioty, duchy, itd.) | 12 631 | 0 |
| `teksty-misji.md` | tytuły misji, nazwy map, tytuły BGM, uwagi do misji | 1 311 | 0 |

Zasada jest **ta sama** co w fabule: linia japońska, pod nią linia `limit:` (ile wolno napisać),
a pod nią `EN:`. Elementy w kolumnie „dziedziczy" nie mają `EN:` — nic tam nie wpisujesz.

### Postacie — `postacie.md`

```
## Postać 2/405 — 日向仁
- seria: 絶対無敵ライジンオー
- głos: 松本梨香

1. [Imię w grze] 日向仁
   EN:
2. [Przezwisko] 仁
   EN:
3. [Seria] 絶対無敵ライジンオー
   EN:
4. [Aktor głosowy] 松本梨香
   EN:
5. [Imię krótkie (lista)] 仁
   EN:
6. [Imię pełne (dialogi)] 日向仁
   EN:
7. [Imię wąskie (półszerokie znaki)] 仁
   EN:
```

* Nagłówek podaje **serię i aktora głosowego** — kontekst, z jakiego świata postać pochodzi.
* `[Imię pełne (dialogi)]` — tej wersji używa się w dialogach; `[Imię krótkie (lista)]` — w listach
  i na ekranach; `[Imię wąskie]` — wersja półszeroka (te same znaki, wąska czcionka) — tu mieszczą
  się tylko znaki półszerokie, więc tak, jak stoją w oryginale.
* `[Seria]` i `[Aktor głosowy]` też się tłumaczy (gra je pokazuje). Nazwę serii ustal raz —
  powtarza się przy wielu postaciach.
* Grupa bez `- seria:` to postać, której gry nie da się przypisać do serii (postacie zbiorowe typu
  „żołnierz"). Piszemy wtedy nazwę ogólną.

### Cytaty bitewne — `cytaty.md`

```
## Mówca 3/299 — シロー・アマダ
- seria: 機動戦士ガンダム 第０８ＭＳ小隊

1. [Kwestia] 「当たるかよ、こんなもん！」
   EN:
2. [Kwestia] 「援護射撃だ、下がってろ！」
   EN:
```

* Grupa = mówca; w nagłówku jego **imię i seria**, żeby ton wypowiedzi był zgodny z postacią.
* Kwestie stoją w japońskich cudzysłowach `「…」` — **zostaw je** (gra je rysuje).
* Mówca bez nazwy (`## Mówca 5/299 — ID 3122`) — ton neutralny; w grze widać, kto to mówi.
  Takich kwestii jest 1,65 % (451 z 27 383) i to jest w porządku.

### Mechy i bronie — `mechy.md`

```
## Jednostka 1/393 — ライジンオー
- seria: 絶対無敵ライジンオー
- długość: 全長 25.0m
- masa: 重量 54.0t

1. [Nazwa] ライジンオー
   EN:
2. [Nazwa na ekranie] ライジンオー
   EN:
3. [Seria] 絶対無敵ライジンオー
   EN:
4. [Broń 1 — nazwa] ライジンクロー
   EN:
5. [Broń 1 — skrót] ﾗｲジﾝｸﾛｰ
   EN:
```

* Jedna grupa = jedna jednostka: nazwy, seria, długość i masa (z księgi gry) **oraz wszystkie jej
  bronie** — dzięki temu nazwy broni tłumaczy się razem z mechem, do którego należą.
* `[Broń N — skrót]` to wersja półszeroka (wąskie znaki) — trzymaj się krótko.
* `全長 25.0m` / `重量 54.0t` — tłumaczysz liczbę i jednostkę razem z opisem
  (np. `Length 25.0m`, `Weight 54.0t`).

### Przedmioty i umiejętności — `przedmioty.md`, `umiejetnosci.md`

```
## Przedmiot 1/600 — 改造制限解除
1. [Nazwa] 改造制限解除
   EN:
2. [Opis efektu] %s20%s
   EN:
```

* Nazwa i opis stoją obok siebie — tłumaczysz je razem, jako jedno pojęcie.
* Opisy efektów używają `%s` (gra wstawia liczbę/poziom) i `%%` (znak procentu) — **zostaw je**.
* Umiejętności mają dodatkowo `[Nazwa z poziomem]` (np. `対地 Lv1`) i `[Opis skrócony]` (wersja na
  wąską listę — musi być krótka).

### Teksty interfejsu i misji — `teksty-config.md`, `teksty-misji.md`

* Te pliki są podzielone na **sekcje** (`## Sekcja 1/29 — config_skill`), a w środku elementy po
  kolei. To teksty menu, podpowiedzi, nazwy duchów, typów umiejętności, tytuły map i BGM.
* `teksty-misji.md` ma **twarde limity miejsca** — pisze to wprost linia `limit:` przy każdym
  elemencie (np. `limit: 117 B`). Tekst dłuższy zostanie odrzucony z podaniem, o ile bajtów skrócić;
  tu nie da się „przekroczyć o trochę".
* W tych plikach bywają tokeny `＠0`, `＠4`, `＠6`, `＠9` — to odwołania do nazw i liczb z gry.
  Zostaw je w tym samym miejscu.

---

## 4. Krok 3 — odesłanie pracy

1. Pliki `.md` **wracają do nas bez zmian nazw** (możesz je spakować w zip — nie trzeba).
2. Nie usuwaj plików, których nie skończyłeś — prześlemy je z powrotem z wolnymi liniami `EN:`.
3. Jeśli w pliku jest linia `EN:` pusta, element jest uznany za nieprzetłumaczony. Możesz odsyłać
   partiami, po odcinkach albo po kategoriach.

### Co robimy z plikami po naszej stronie

```
python3 tools/translation_import.py --views <pliki .md albo zip> --package local/translation
python3 tools/translation_copy.py --package local/translation      # powtórzenia scen DLC
python3 tools/translation_mirror.py --package local/translation    # ta sama nazwa w kilku tabelach
python3 tools/translation_check.py --package local/translation     # limity, znaki, tokeny, linie
```

* `translation_import.py` rozpoznaje plik po nazwie i wie, do którego miejsca w grze trafia każdy
  element. Jeśli plik pochodzi ze starszej wersji pakietu (tekst japoński się nie zgadza), **odrzuca
  go w całości** — nigdy nie wpisze tekstu w złe miejsce.
* Tekst, który złamałby grę (znak spoza CP932, zgubiony token, inna liczba linii, za długi tekst
  w polu o stałym rozmiarze) jest **odrzucany i wypisany** — poprawiamy i uruchamiamy ponownie.
  Uruchomienie można powtarzać bezpiecznie: nic nie jest wpisywane podwójnie.

---

## 5. Checklista

**Raz, na początku**

- [ ] Przeczytałem sekcję 1 (zasady, znaki, długość tekstu).
- [ ] Ustaliłem pisownię najważniejszych nazw własnych (protagonista, seria „oryginalna").
- [ ] Wiem, że piszę tylko po `EN:` i nie ruszam linii japońskich ani numerów.

**Fabula — dla każdego pliku odcinka**

- [ ] Każde `EN:` w scenie ma tekst (albo element jest `[kopia]` — wtedy zostaje pusty).
- [ ] W tytułach misji (`T1.`) i uwagach (`N1.`,`N2.`) nie ma pustych `EN:`.
- [ ] Liczba linii w moim tekście = liczba linii japońskich (końcowe łamanie dodaje się samo).
- [ ] `⏎` i `<0x0F>` zostały tam, gdzie były.
- [ ] Żadnego `—`, `„`, `•` ani liter z akcentami.

**Widoki nazw i tabel**

- [ ] Nie wpisałem nic w elementy z dopiskiem „ten sam tekst co wcześniej".
- [ ] W `teksty-misji.md` każdy tekst mieści się w bajtach z linii `limit:`.
- [ ] `mechy.md`: każda jednostka ma nazwę, serię i wszystkie bronie (nazwa + skrót).
- [ ] Seria każdego mecha/postaci jest zapisana **raz** — pozostałe wystąpienia dziedziczą.
- [ ] `cytaty.md`: kwestie bez mówcy przetłumaczone neutralnie.
- [ ] `przedmioty.md` / `umiejetnosci.md`: nazwy krótkie (mieszczą się w liście), opisy z `%s`/`%%`.
- [ ] `teksty-misji.md`: nic nie jest dłuższe niż oryginał w bajtach.
- [ ] Te same nazwy w różnych plikach są zapisane identycznie.

---

## 6. Co jeszcze nie jest gotowe (stan prac)

* **Fabuła, nazwy, cytaty, itemy, umiejętności, teksty config i misji** — widoki są gotowe,
  czekają na tłumaczenie (72 586 elementy: 67 440 z linią `EN:` + 5 146 dziedziczonych).
* **Tłumaczenie w grze** — działa wtryskiwanie przedmiotów, **dialogów, narracji i tytułów misji**
  (sprawdzone na roboczej kopii: cała scena 1 — 88 linii dialogu/narracji + 15 tytułów misji;
  kontener przebudowany i odczytany z powrotem bajt w bajt bez różnic poza tymi tekstami). Kwestie
  mówców i teksty w grze widział już człowiek — reszta do pokazania, zanim cokolwiek ogłosimy gotowym.
* **Kwestie bez mówcy** — 451 z 27 383 (1,65 %), w granicach, które ustaliliśmy.
* **Nazwy mówców w dialogach** — postaci z nazwą 100 %; 42 klucze to postacie zbiorowe bez nazwy
  własnej (np. „żołnierz"), pokazywane jako `ID`.

---

## 7. Dodatek techniczny (dla nas, nie dla tłumacza)

* Pakiet to pliki `00_dialogue.jsonl` … `08_names_units_weapons.jsonl` (85 424 wiersze tekstu +
  293 wiersze strukturalne scen) — jedyne źródło prawdy dla gry. Widoki `.md` są generowane z pakietu
  i do niego wracają.
* Klucz elementu fabuły: numer sceny (`seq` z `06_scenes.jsonl`) + numer elementu (`order`).
  Klucz elementu nazw/tabel: numer grupy + numer elementu w planie zbudowanym z tych samych wierszy,
  które idą z powrotem do pliku; import dodatkowo porównuje tekst japoński, żeby wykryć nieaktualny
  widok.
* Tytuł misji i uwagi do misji są elementami sceny (`T1`, `N1`, `N2`) i trafiają do
  `05_mission_text.jsonl` (mają twardy `max_bytes`).
* Jedna linia `EN:` może wypełnić **kilka wierszy gry** — gdy ta sama postać/mech figuruje w kilku
  tablicach rozdziałów (1 097 scalonych par w `07`, 300 w `08`, 7 542 identycznych kwestii w `01`).
* Narzędzia: `tools/scene_view.py` (widoki fabuły + zip), `tools/table_view.py` (widoki nazw i tabel
  + zip), `tools/translation_import.py`, `tools/translation_copy.py`, `tools/translation_mirror.py`,
  `tools/translation_check.py`, `tools/event_refresh.py` (domyka fabułę z kontenerów gry),
  `tools/package_copies.py` (znaczy powtórzenia). Testy: 728 (1 pominięty).
* Kontrola całego pakietu: 85 424 wiersze, **0 błędów** (przed tłumaczeniem wszystkie puste).
