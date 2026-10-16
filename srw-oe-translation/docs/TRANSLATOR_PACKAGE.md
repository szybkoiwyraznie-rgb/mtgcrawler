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

**Aktualizacja 2026-10-14:** do folderu doszedł plik **`tokeny.tsv`** — lista rodzajów `%s`
(patrz sekcja 3, „Co dokładnie oznacza `%s` w opisach"). Trzeba go położyć **obok plików JSON**
(pakiet roboczy), wtedy walidator i importer pilnują nowej reguły `%s` automatycznie.

Do wypełnienia w całym pakiecie: **84 579 linii `EN:`**
(40 464 w fabule + 44 115 w widokach). Poza tym jest **13 897 elementów bez linii `EN:`**
(8 751 w fabule — kopie scen i kwestii, i 5 146 w widokach — powtórzone nazwy i opisy);
tłumaczenie dziedziczy się tam automatycznie, nie wpisuje się nic (patrz „Elementy bez linii `EN:`").

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
   `%%`, `＠0`, `＠1`, `＠4`, `＠6`, `＠9` (podstawiane przez grę liczby i nazwy), a także `%s`
   **zgodnie z regułą z sekcji 3** (część `%s` to tokeny japońskiej kany — te znikają z angielskiego
   tekstu razem ze znakiem, który po nich stoi; lista `tokeny.tsv` mówi, które to które), oraz
   nawiasowe podstawki w rodzaju `＜主人公名＞` (imię protagonisty wpisane przez gracza — gra
   podmienia je przy wyświetlaniu). Podstawkę kopiujesz dosłownie, bez tłumaczenia; przy liczeniu
   limitu liczy się tak, jak stoi: `＜主人公名＞` = **12 jednostek** (`＜` i `＞` po 2, cztery
   znaki kanji po 2).
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
w polu pisanym czcionką półszeroką (patrz „Imiona wąskie" i `<0x0F>` niżej).

### Długość tekstu — czytaj linię `limit:` pod każdym elementem

Pod **każdym** elementem do przetłumaczenia jest linia `limit:` mówiąca, ile wolno napisać. Są trzy
rodzaje tej linii:

| linia `limit:` | co znaczy |
|---|---|
| `limit: 117 B (stała szerokość — dłuższe się nie zmieści)` | **twardy limit**. Miejsce w grze ma dokładnie tyle bajtów; dłuższy tekst **nie zostanie wpisany** (narzędzie go odrzuci i poda, o ile trzeba skrócić). Jeden znak japoński = 2 B, jeden znak angielski = 1 B. |
| `limit: 46 jedn. na linię (twardy limit 52 jedn. — tyle gra sama rysuje w tym miejscu); oryginał: 3 linii` | tekst rysowany w oknie gry. Długość całego tekstu jest dowolna (gra przebudowuje rozmiary), ale **każda linia** ma się mieścić: trzymaj się 46; twardy limit to tyle, ile sama gra rysuje w tym rodzaju tekstu — **dialog 52, cytat bitewny 50** jednostek (jednostka = szerokość połowy znaku; znak japoński ma 2; znaki sterujące jak `\r` nie liczą się). `oryginał: N linii` mówi, na ile linii łamał się japoński — **zostaw tyle samo**. |
| `limit: bez twardego limitu (pole rośnie) — trzymaj się długości oryginału (najdłuższy w tej kategorii: 18 jedn.)` | nazwy w listach, serie, opisy. Długość jest dowolna, ale interfejs gry ma stałą szerokość listy — **nie przekraczaj długości oryginału** więcej niż o ~⅓. Liczba w nawiasie to najdłuższy oryginał w tej samej kategorii: to praktyczna granica. |

Uwaga: „dowolna długość" przy dialogach **nie znaczy „bez konsekwencji"** — tekst wpisany do gry
musi się jeszcze mieścić w oknie. Dlatego liczba linii i szerokość linii są w limicie, a nasze
narzędzia odrzucają linię szerszą niż to, co gra sama rysuje w danym rodzaju tekstu (dialog 52,
cytat 50, podpowiedź misji 66, pozostałe 46 jednostek). Skąd te liczby: policzyliśmy szerokość
każdej japońskiej linii w całym skrypcie (2026-10-14) — 316 linii dialogu ma 50 jednostek, cztery
mają 52. Do 2026-10-14 narzędzia odrzucały wszystko powyżej 46 (liczba z pierwszej sceny); czy linie
47–52 znaków łacińskich mieszczą się w oknie tak samo jak japońskie, **jeszcze nie sprawdziliśmy w
grze** — 46 pozostaje zalecane.

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
oraz `epizod-00.md` … `epizod-34.md` + `simulator.md` (`epizod-00` to prolog z płyty gry).

Zacznij od `spis-scen.md` — to spis treści: numer sceny, odcinek, misja, miejsce. Każdy plik
odcinka to sceny **w kolejności gry**.

### Jak wygląda scena

To prawdziwy początek sceny 15/293 z pliku `epizod-02.md` (lista uczestników skrócona):

```
## Scena 15/293 — 黒いレイバー
- odcinek: ２話 メインミッション (episode 2)
- miejsce: 自衛隊演習場 (element 1)
- miejsce: シャフトエンタープライズ／オフィス (element 11)
- miejsce: 特車二課／格納庫 (element 19)
- miejsce: 自衛隊演習場／指揮所 (element 45)
- limit: dialog — 46 jedn. na linię (twardy limit 52 — tyle gra sama rysuje), narracja — do 56 jedn.; liczbę linii zostaw jak w oryginale (okno gry pokazuje 3 naraz)
- uczestnicy:
  - 自衛隊員
  - 内海 — 機動警察パトレイバー
  - 泉野明 — 機動警察パトレイバー
  (…)

T1. [Tytuł misji] 黒いレイバー
   EN:
N1. [Uwaga do misji (pole powtarzane w grze — jeden tekst)] このミッションは出撃ユニットが固定されています。
   EN:
1. [Nagłówek miejsca] 自衛隊演習場
   EN:
2. [Dialog - 自衛隊員] 本部、本部！　応答願います！
   EN:

_koniec sceny_
```

Co jest czym:

* **`## Scena 15/293 — …`** — numer sceny (kolejność gry) i japoński tytuł misji.
* **`- odcinek:` / `- miejsce:`** — kontekst: który odcinek i gdzie scena się dzieje
  (miejsce też jest do przetłumaczenia — jako element w środku sceny).
* **`- limit:`** — ile wolno napisać w tej scenie (dialog 46 jednostek na linię, twardy limit 52;
  narracja do 56). Szczegóły w sekcji 1.
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
3. [Dialog - 自衛隊員] 無線が電波障害を起こしています。
   本部と連絡が取れません。
   EN: Our radio is being jammed.
   We can't reach HQ.
```

* Tekst wpisujesz **w linii `EN:`**, po dwukropku.
* Jeśli tekst ma więcej linii, piszesz je w kolejnych liniach **z takim samym wcięciem** (3 spacje) —
  dokładnie tyle linii, ile łamie się japoński.
* **Pusta linia** w tekście japońskim (odstęp między akapitami narracji) stoi jako pusta linia
  z wcięciem — w bloku `EN:` zostaw taką samą pustą linię (wystarczą same 3 spacje albo zupełnie
  pusta). Liczba przejść do nowej linii musi się zgadzać co do sztuki z japońskim oryginałem —
  narzędzie importujące to sprawdza i odrzuci tekst z inną liczbą. Wyjątek: przejścia **na samym
  końcu** tekstu dodają się same, tam pustej linii nie odtwarzasz.
* `⏎` w tekście japońskim = wymuszone przejście do nowej linii. **Zostaw `⏎` w swoim tekście**
  w tym samym miejscu — nie zamieniaj go na zwykłą nową linię.
* `<0x0F>` = w japońskim tekście to **pierwszy bajt dwubajtowego znaku**: razem z JEDNYM znakiem
  stojącym bezpośrednio po nim tworzy jedną dźwięczną sylabę kany (ten znak po `<0x0F>` nie jest
  tekstem — jest częścią sylaby, mimo że wygląda jak cyfra lub interpunkcja). Po angielsku dźwięczna
  kana nie istnieje, więc **w tekście `EN:` usuwasz `<0x0F>` razem z tym jednym znakiem po nim**,
  a resztę piszesz zwykłymi literami. Jak odczytać sylabę: pełna wersja tej samej nazwy (np.
  „Imię pełne" przy „Imię wąskie") pokazuje ją zwykłą kaną z kropkami. Narzędzie **odrzuci**
  angielski tekst, w którym `<0x0F>` został — zostawiony przed angielską literą zjadłby ją w grze.
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
| `teksty-config.md` | teksty menu i ekranów (sekcjami: umiejętności, przedmioty, duchy, itd.) | 15 368 | 0 |
| `teksty-misji.md` | tytuły misji, nazwy map, tytuły BGM, uwagi do misji | 1 284 | 0 |

Zasada jest **ta sama** co w fabule: linia japońska, pod nią linia `limit:` (ile wolno napisać),
a pod nią `EN:`. Elementy w kolumnie „dziedziczy" nie mają `EN:` — nic tam nie wpisujesz.

> **Nagłówki grup zostają po japońsku.** Linie `- seria:`, `- głos:`, `- długość:`, `- masa:`
> w nagłówkach (i `- uczestnicy:` w fabule) to tylko **podpowiedź**, z jakiego świata pochodzi
> postać albo mech — **nie tłumaczy się ich** i nic się w nich nie wpisuje. To, co **widać w grze**,
> jest osobno, jako ponumerowany element: `[Seria]`, `[Aktor głosowy]`, `[Długość]`, `[Masa]` —
> i **te elementy się tłumaczy**.

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
## Mówca 67/299 — シロー・アマダ
- seria: 機動戦士ガンダム 第０８ＭＳ小隊

1. [Kwestia] 「守ったら負ける！」
   limit: 46 jedn. na linię (twardy limit 50 jedn. — tyle gra sama rysuje w tym miejscu); oryginał: 1 linii
   EN:
2. [Kwestia] 「あの時の二の舞はゴメンだ！」
   limit: 46 jedn. na linię (twardy limit 50 jedn. — tyle gra sama rysuje w tym miejscu); oryginał: 1 linii
   EN:
```

* Grupa = mówca; w nagłówku jego **imię i seria**, żeby ton wypowiedzi był zgodny z postacią.
* Kwestie stoją w japońskich cudzysłowach `「…」` — **zostaw je** (gra je rysuje).
* Mówca bez nazwy (`## Mówca 1/299 — ID 50`) — ton neutralny; w grze widać, kto to mówi.
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
* Opisy efektów używają `%s` i `%%` (znak procentu). **Uwaga: reguła `%s` zmieniła się
  2026-10-14** — czytaj następny podrozdział, zanim wypełnisz opisy.
* Umiejętności mają dodatkowo `[Nazwa z poziomem]` (np. `対地 Lv1`) i `[Opis skrócony]` (wersja na
  wąską listę — musi być krótka).

#### Co dokładnie oznacza `%s` w opisach — reguła z 2026-10-14

Pod `%s` w widokach kryją się **dwie różne rzeczy**, których nie da się rozróżnić wzrokiem.
Dotychczasowa reguła („zachowaj wszystkie `%s`") była dla drugiej z nich błędna: zachowany token
wstawiał japoński glif w środek angielskiego zdania. Teraz zgadywać nie trzeba — w pakiecie jest
lista **`tokeny.tsv`** (w tym samym folderze co pliki JSON), która dla każdego takiego tekstu
pokazuje rodzaj każdego `%s`.

1. **Literalny `%s` (w liście oznaczony `L`)** — własny placeholder silnika: w czasie działania
   gra wstawia w to miejsce wyliczaną wartość (liczbę, poziom, próg). Przykład: `%s20%s`
   (改造制限解除), `%s2倍`. **Musi zostać w angielskim tekście** — każdy co do sztuki, bez zmiany
   kolejności względem siebie i innych tokenów (`＠0`, `%%`). Przesunięcie całego fragmentu zdania
   razem z jego `%s` jest w porządku, zamiana `%s` miejscami — nie. W całym pakiecie jest ich
   9 391.
2. **Token kany (oznaczony `T`)** — bajt sterujący `0x0F` plus bajt po nim tworzą **jeden glif
   dźwięcznej kany** (np. ダ). Widok renderuje go jako `%s`, a drugi bajt glifu często widać jako
   znak tuż po nim (`%s*`, `%s&`, `%s4`, `%s.`…). **Musi zniknąć z angielskiego tekstu**: usuń
   `%s` **razem z jednym znakiem, który po nim stoi**, a słowo przetłumacz naturalnie. Przykład:
   `発動すると敵に追加%s*ﾒｰ%s&` (= 追加ダメージ) → EN `Adds damage to the enemy when activated` —
   bez żadnego `%s`. Takich tokenów jest 217 w 119 tekstach (głównie opisy umiejętności).
3. **Inna kontrolka (oznaczona `C`)** — rzadkie znaczniki strukturalne (np. na początku opisów
   ksiąg referencyjnych: `%s%s解説書：戦術`). **Zostają jako `%s`** w tym samym miejscu. Jest ich 20.

**Jak korzystać z listy.** Każda linia to `id_tekstu <TAB> rodzaje <TAB> tekst_japoński`, rodzaje
po przecinku w kolejności wystąpień `%s` w tekście (np. `L,T,L`). Widoki nie pokazują id —
wpisu szukaj **po tekście japońskim** (trzecia kolumna): jp elementu widoku i jp w liście to ten
sam napis. Zweryfikowane na całym pakiecie: ten sam tekst ma zawsze te same rodzaje (1 359 różnych
tekstów, zero konfliktów), więc dopasowanie po tekście jest jednoznaczne.

**Kto pilnuje poprawności.** Walidator i importer czytają `tokeny.tsv` automatycznie, jeśli plik
leży obok JSON-ów: angielski tekst z usuniętymi tokenami kany **przechodzi**; tekst, który je
zachował (`%s*`), jest **odrzucany** z wyjaśnieniem; brak literalnego `%s` też jest odrzucany.
Bez listy obok pakietu obowiązuje stara ścisła reguła (wszystkie `%s` zostają) — dlatego plik
**musi** leżeć w folderze pakietu.

**Znacznik `<0x0F>`** (imiona w widokach postaci i mechów, sceny) to **dokładnie ten sam** token
kany, tylko pokazany wprost: usuwamy go razem z jednym znakiem po nim. Tekstów z tym znacznikiem
nie ma w liście — są jednoznaczne same w sobie.

### Teksty interfejsu i misji — `teksty-config.md`, `teksty-misji.md`

* Te pliki są podzielone na **sekcje** (`## Sekcja 1/31 — config_achievement`), a w środku elementy po
  kolei. To teksty menu, podpowiedzi, nazwy duchów, typów umiejętności, tytuły map i BGM.
* `teksty-misji.md` ma **twarde limity miejsca** — pisze to wprost linia `limit:` przy każdym
  elemencie (np. `limit: 39 B`). Tekst dłuższy zostanie odrzucony z podaniem, o ile bajtów skrócić;
  tu nie da się „przekroczyć o trochę".
  **Uwaga do widoków wysłanych przed 2026-10-14:** przy tytułach misji, nazwach map, teł i oddziałów
  stoją tam limity za duże (117/159/111/99 B) — to był cały rekord, nie samo pole tekstu. Prawdziwe
  miejsce to **tytuł misji 39 B, nazwa mapy 31 B, nazwa tła 23 B, nazwa oddziału 31 B** (zmierzone na
  plikach gry; narzędzie i tak nie wpisze nic dłuższego). Widoki generowane od 2026-10-14 mają już
  poprawne liczby. Po pierwszym wgraniu `EN.zip` 32 takie nazwy były za długie — lista z numerami
  elementów jest w pliku `DO_ZROBIENIA.md` obok zbudowanych kontenerów.
* **Fragmenty opisów umiejętności, przedmiotów, duchów i stanów** (w `teksty-config.md` sekcje
  `config_skill`, `config_item`, `config_spirit`, `config_status_change` — krótkie kawałki typu
  `気力`, `発動すると`, `%s\n%s`) leżą w grze w jednej wspólnej puli z własną tablicą adresów
  (zmierzone 2026-10-14), więc **rosną jak każdy inny tekst** — napis „bez twardego limitu" jest
  prawdziwy. (Wcześniejsza wersja tego akapitu kazała trzymać się długości oryginału — to był błąd
  naszego czytnika, nie ograniczenie gry.) Gra skleja z tych kawałków całe zdania opisu, więc
  zachowaj spacje skrajne i interpunkcję dokładnie jak w oryginale.
* **Nowe elementy w sekcjach `config_skill` / `config_item` / `config_spirit` (2026-10-14):** około
  125 fragmentów z tokenem kany (`%s*ﾒｰ%s&` = ﾀﾞﾒｰｼﾞ „obrażenia", np. `防御時､%s*ﾒｰ%s&-`,
  `(ﾗｲ%s&ﾝｵｰと合体)`) wcześniej w ogóle nie trafiło do pakietu — pojawiają się w nowych widokach
  z pustą linią `EN:`. Zasada `%s` jak w umiejętnościach: token kany w angielskim znika, literalny
  `%s` zostaje. Kopie w sekcjach DLC (`Skill01–08`, `Item01–08`, `srwDL_Item`) są oznaczone jako
  dziedziczące — wpisuje się tylko raz.
* **Spacje na początku i końcu są częścią tekstu.** Japoński ma czasem wyśrodkowany tytuł
  (`　　 サブミッション　　`), spację wyrównującą kolumnę (` Lv`) albo znak nowej linii na końcu opisu
  (`\n`). Narzędzia wpisują angielski **dokładnie tak, jak go napiszesz** — ze spacjami i `\n` włącznie
  — więc zachowaj to, co ma oryginał (walidator ostrzega, gdy dodasz spację skrajną, której oryginał
  nie ma). Sam tekst złożony wyłącznie z białych znaków znaczy „nie przetłumaczone".
* W tych plikach bywają tokeny `＠0`, `＠4`, `＠6`, `＠9` — to odwołania do nazw i liczb z gry.
  Zostaw je w tym samym miejscu.

---

## 4. Krok 3 — odesłanie pracy

1. Pliki `.md` **wracają do nas bez zmian nazw** (możesz je spakować w zip — nie trzeba).
2. Nie usuwaj plików, których nie skończyłeś — prześlemy je z powrotem z wolnymi liniami `EN:`.
3. Jeśli w pliku jest linia `EN:` pusta, element jest uznany za nieprzetłumaczony. Możesz odsyłać
   partiami, po odcinkach albo po kategoriach.

### Co robimy z plikami po naszej stronie

* Każde Twoje `EN:` trafia **dokładnie tam, gdzie w grze stoi tekst japoński, który stał nad nim**.
  Jeśli plik pochodzi ze starszej wersji pakietu (tekst japoński się nie zgadza), **odrzucamy go
  w całości** — nigdy nie wpiszemy tekstu w złe miejsce.
* Tekst, który złamałby grę (znak spoza CP932, zgubiony obowiązkowy token `＠…`/literalny `%s`,
  zachowany token kany `%s`, inna liczba linii, za dużo
  bajtów w polu o stałej szerokości) jest **odrzucany i wypisany** — poprawiamy i sprawdzamy ponownie.
  Powtarzanie niczego nie psuje: żaden tekst nie jest wpisywany dwa razy.
* Powtórzenia uzupełniają się same, a ta sama nazwa użyta w kilku tabelach to nadal jedna linia `EN:`.

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
- [ ] `⏎` i podstawki `＜…＞` (np. `＜主人公名＞`) zostały tam, gdzie były; `<0x0F>` zniknęło z angielskiego tekstu (razem ze znakiem, który po nim stał).
- [ ] Żadnego `—`, `„`, `•` ani liter z akcentami.

**Widoki nazw i tabel**

- [ ] Nie wpisałem nic w elementy z dopiskiem „ten sam tekst co wcześniej".
- [ ] W `teksty-misji.md` każdy tekst mieści się w bajtach z linii `limit:`.
- [ ] `mechy.md`: każda jednostka ma nazwę, serię i wszystkie bronie (nazwa + skrót).
- [ ] Seria każdego mecha/postaci jest zapisana **raz** — pozostałe wystąpienia dziedziczą.
- [ ] `cytaty.md`: kwestie bez mówcy przetłumaczone neutralnie.
- [ ] `przedmioty.md` / `umiejetnosci.md`: nazwy krótkie (mieszczą się w liście), opisy według
      reguły `%s` (sekcja 3): literalne `%s` z `tokeny.tsv` zachowane co do sztuki, `%s` tokenów
      kany usunięte razem ze znakiem po nich, `%%` zostaje.
- [ ] `teksty-misji.md`: nic nie jest dłuższe niż oryginał w bajtach.
- [ ] Te same nazwy w różnych plikach są zapisane identycznie.

---

## 6. Na koniec

To cała instrukcja — nie trzeba nic wiedzieć o plikach gry, JSON-ach ani o naszych narzędziach.
Jeśli coś jest niejasne albo w którymś miejscu brakuje kontekstu (np. nie wiadomo, jak brzmi
wcześniejsza kwestia tej samej postaci), **pytaj** — dopiszemy brakujący fragment do pakietu.
Powodzenia!
