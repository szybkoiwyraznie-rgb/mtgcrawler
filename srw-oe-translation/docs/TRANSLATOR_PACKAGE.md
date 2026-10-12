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

Do wypełnienia w całym pakiecie: **69 753 elementy**
(23 202 w fabule + 46 551 w widokach nazw i tabel).

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

### Długość tekstu

* **Dialogi i cytaty** — okno gry mieści około **46 znaków półszerokich w linii** (czyli ~23 znaki
  japońskie). Tłumaczenie może być dłuższe niż japońskie (gra przebudowuje rozmiary), ale zbyt długa
  linia zostanie ucięta przy wyświetlaniu — narzędzie zgłosi to jako uwagę.
* **Nazwy w listach (itemy, umiejętności)** — pole w interfejsie jest wąskie; przekroczenie
  rozmiaru oryginału to uwaga, nie błąd, ale lepiej się mieścić.
* **Teksty misji** (`teksty-misji.md`) — **twardy limit w bajtach**. Tekst dłuższy się nie zmieści
  i narzędzie go odrzuci z liczbą bajtów. Tu trzeba skracać.

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

| plik | co zawiera | elementów |
|---|---|---|
| `postacie.md` | imiona, przezwiska, serie, aktorzy głosowi, wersje imion (pełne/krótkie/wąskie) | 2 291 |
| `cytaty.md` | kwestie bitewne, pogrupowane po mówcy | 19 841 |
| `mechy.md` | nazwy jednostek, serie, długość, masa **oraz wszystkie bronie** | 4 345 |
| `przedmioty.md` | nazwy przedmiotów i opisy efektów | 1 200 |
| `umiejetnosci.md` | nazwy umiejętności i opisy efektów | 4 932 |
| `teksty-config.md` | teksty menu i ekranów (sekcjami: umiejętności, przedmioty, duchy, itd.) | 12 631 |
| `teksty-misji.md` | tytuły misji, nazwy map, tytuły BGM, uwagi do misji | 1 311 |

Zasada jest **ta sama** co w fabule: linia japońska, pod nią `EN:` do wypełnienia.

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
* `teksty-misji.md` ma **twarde limity miejsca** — jeśli tekst jest za długi, narzędzie go odrzuci
  i poda, o ile bajtów trzeba skrócić. Tu nie da się „przekroczyć o trochę".
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

- [ ] `postacie.md`: każda postać ma imię, serię i aktora głosowego.
- [ ] `mechy.md`: każda jednostka ma nazwę, serię i wszystkie bronie (nazwa + skrót).
- [ ] `cytaty.md`: kwestie bez mówcy przetłumaczone neutralnie.
- [ ] `przedmioty.md` / `umiejetnosci.md`: nazwy krótkie (mieszczą się w liście), opisy z `%s`/`%%`.
- [ ] `teksty-misji.md`: nic nie jest dłuższe niż oryginał w bajtach.
- [ ] Te same nazwy w różnych plikach są zapisane identycznie.

---

## 6. Co jeszcze nie jest gotowe (stan prac)

* **Fabuła, nazwy, cytaty, itemy, umiejętności, teksty config i misji** — widoki są gotowe,
  czekają na tłumaczenie (69 753 elementy).
* **Tłumaczenie w grze** — działa wtryskiwanie przedmiotów i **dialogów** (sprawdzone na roboczej
  kopii `eventP00.cpk`: 6 linii sceny 1 wpisanych, kontener przebudowany i odczytany z powrotem bez
  różnic poza tymi liniami). Uruchomienia w PPSSPP jeszcze nie było — to po naszej stronie
  i zostanie pokazane, zanim cokolwiek ogłosimy gotowym.
* **Kwestie bez mówcy** — 451 z 27 383 (1,65 %), w granicach, które ustaliliśmy.
* **Nazwy mówców w dialogach** — postaci z nazwą 100 %; 42 klucze to postacie zbiorowe bez nazwy
  własnej (np. „żołnierz"), pokazywane jako `ID`.

---

## 7. Dodatek techniczny (dla nas, nie dla tłumacza)

* Pakiet to pliki `00_dialogue.jsonl` … `08_names_units_weapons.jsonl` (82 591 wierszy tekstu +
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
  `tools/translation_check.py`. Testy: 652 (1 pominięty).
* Kontrola całego pakietu: 82 591 wierszy, **0 błędów** (przed tłumaczeniem wszystkie puste).
