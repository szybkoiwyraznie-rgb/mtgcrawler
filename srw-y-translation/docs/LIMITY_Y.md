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
