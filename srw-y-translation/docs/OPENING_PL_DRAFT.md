# SRW Y — szkic otwarcia (NIEAKTUALNY)

Ten plik jest archiwalny: szkic powstał z **angielskiego** tekstu i z budżetem
bajtowym, którego już nie potrzebujemy (klucz jest znany, więc plik może zmienić
rozmiar). Aktualne tłumaczenie, z japońskiego, jest w
[`../translations/opening_pl.json`](../translations/opening_pl.json); opis pracy —
w [`STATUS.md`](STATUS.md) (sekcja S5).

---

# SRW Y — opening narration: Polish draft (not yet installed)

Source offered by the owner on 2026-10-26, as displayed by the English build:

> Sixty years ago, interstellar war ravaged our planet... The conflict was our first
> contact with extraterrestrials, and it nearly wiped humanity from the universe. The
> species' recovery was nothing short of miraculous, and in just half a century, we
> have stepped into the galactic frontier and begun to spread across the stars.

This is the **English** text, so it is a translation of a translation. The project rule
is to translate from the Japanese original; the draft below is therefore provisional -
its job is to prove the patch mechanism on the first screen of the game, and it will be
redone from the ja-JP table once that table is carved (it is in the same collection run).

## Byte budget first

A patched bundle must keep its exact file size, and a string inside the compressed
stream can only be overwritten byte for byte. So the replacement is limited by the
**byte** count of the original, not its character count - and Polish carries
two-byte letters (ą ć ę ł ń ó ś ź ż).

| version | chars | UTF-8 bytes | vs English (326 B) |
|---|---|---|---|
| English original | 326 | 326 | — |
| A — faithful | 314 | 338 | +12 |
| B — tight | 235 | 255 | −71 |

A is the version to install if the storage has twelve spare bytes (tables usually
align entries, so it may); B is the fallback and always fits.

## A — faithful

Sześćdziesiąt lat temu wojna międzygwiezdna pustoszyła naszą planetę... Ten konflikt
był naszym pierwszym kontaktem z obcymi i niemal starł ludzkość z wszechświata.
Odbudowa gatunku graniczyła z cudem, a w ciągu zaledwie pół wieku wkroczyliśmy na
galaktyczne rubieże i zaczęliśmy rozprzestrzeniać się wśród gwiazd.

## B — tight

Sześćdziesiąt lat temu wojna międzygwiezdna spustoszyła naszą planetę... Był to
pierwszy kontakt z obcymi i niemal zgubił ludzkość. Odbudowa graniczyła z cudem -
w pół wieku wkroczyliśmy na rubieże galaktyki i zaczęliśmy sięgać gwiazd.

## What decides which one ships

The carved table shows whether the paragraph is one entry or several, how the entry is
length-prefixed, and how much slack the bundle has. That is read from the bundle the
owner's scan returns; nothing here is guessed into a file.
