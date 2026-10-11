# Wytyczne tłumaczenia SRW OE — stała szerokość vs grow, budżety, kontekst

**Zasada:** to, czy dany rodzaj tekstu tłumaczymy ze **stałą szerokością** (bajt‑w‑bajt) czy z
**możliwością rośnięcia**, wynika z *mechanizmu repacku* jego kontenera, a limit znaków —
z ograniczeń renderowania. Poniżej klasyfikacja z oznaczeniem `[ZWERYFIKOWANE]` (boot/testy)
vs `[HIPOTEZA]` (do potwierdzenia).

## 1. Fabuła / dialogi — `eventP00..P09` (rekordy EVNT) — **GROW** `[ZWERYFIKOWANE]`
- Rekord EVNT ma pole długości; `apply_strings` rośnie, a `patch_iso` przepisuje rozmiar i
  wewnętrzne offsety → bootuje (dowiedzione wielokrotnie).
- **Budżet:** suma otwarta, ale **linia ≤ 46 znaków półszerokich** (okno komunikatu; `BOX_WIDTH=46`).
- **Kontekst/mówca:** patrz §Kontekst.

## 2. Menu tytułowe — `configst.cpk` → `sysmes.bin` — **STAŁA SZEROKOŚĆ** `[ZWERYFIKOWANE]`
- Trzy niezależne booty pokazały: etykiety tytułowe są czytane pod **stałymi offsetami zapisanymi
  poza `sysmes`**; KAŻDY przesuw puli rozjeżdża menu. Jedyna bezpieczna transformacja = podmiana
  bajt‑w‑bajt (równa długość slotu, dosyłanie NUL/spacjami).
- **Budżet per etykieta = bajty slotu oryginału**, np. `ライブラリー`=16 B, `クレジット`=12 B,
  `ダウンロードリスト`=20 B. Tłumacz dostaje max znaków = (slot−1) z uwzględnieniem szerokości.

## 3. Help / opisy / komunikaty systemowe — `configst.cpk` → `sysmes.bin` — **stała szerokość** (bezpiecznie) / shift `[HIPOTEZA]`
- Czytane przez wewnętrzną tablicę `{offset,id}`; shift (przesuw + przepisanie tabeli) przechodzi
  check integralności `[ZWERYFIKOWANE strukturalnie]`, ale render niepotwierdzony.
- Zalecenie: **stała szerokość** (budżet = slot) dopóki mapa odnośników nie domknięta.

## 4. Nazwy własne (piloci / mechy / serie / seiyū / pseudonimy) — `imenu00` (`srwDL_CharaDictionary`) + DLC `config0X` — **STAŁA SZEROKOŚĆ** `[HIPOTEZA]`
- Pule NUL‑separowane (ekstrakcja `extract_tables` `[ZWERYFIKOWANE]`); apply jeszcze nie zbudowany.
- Nazwy są krótkie i pokazywane w polach UI → traktować jak budżetowane pola; budżet = szerokość
  pola nazwy (policzy go narzędzie). Angielskie nazwy własne często dłuższe → przewidzieć skróty.

## 5. Encyklopedia / Reference — `imenu00` (`srwDL_Reference`) — **budżet do ustalenia** `[HIPOTEZA]`
- Dłuższe teksty opisowe w puli NUL; jeśli okaże się, że mają pole długości/okno → stała szerokość
  z większym budżetem; jeśli rekordy z długością → możliwy grow. Do zbadania przy budowie apply.

## 6. Opisy przedmiotów / partsów / skilli / efektów — `configst` (`srwDL_Item`, `srwDL_Skill_Tag`, `sysmes`) — **STAŁA SZEROKOŚĆ** `[HIPOTEZA]`
- Jak §3: najbezpieczniej stała szerokość (budżet = slot), dopóki nie domkniemy repacku.

## 7. Nazwy map / terenu — `config00` — **STAŁA SZEROKOŚĆ** `[HIPOTEZA]`
- Krótkie nazwy w puli NUL; budżet = slot (kilka‑kilkanaście znaków).

## 8. Okrzyki bitewne — `mesbtl00` + DLC `mesbtl0X` — **linia ≤ 46** `[HIPOTEZA]`
- Krótkie kwestie w oknie komunikatu; render jak dialogi → limit liniowy 46, suma raczej stała
  (pula NUL, apply open).

## Kontekst i mówca (jakość tłumaczenia) `[STAN + PLAN]`
- Nagłówek rekordu narracji EVNT **NIE niesie mówcy** — pole „parametr" to indeks sekwencji
  (0,1,1,2…), zweryfikowane na `eventP00`.
- Asocjacja mówcy/portretu żyje w **sąsiednich rekordach sterujących**, których obecny export
  (`export_strings`) nie dołącza → tłumacz dziś dostałby sam tekst bez kontekstu.
- **Plan:** rozszerzyć export tak, by każda linia dialogu miała w JSON pole `speaker`/`portrait`
  (pochodzące z poprzedzającego rekordu sterującego) oraz `context` (scena/event), zanim oddamy
  teksty do tłumaczenia. To warunek jakości tłumaczenia dialogów.

## Budżety znaków — dostarczymy liczby
Narzędzie przeliczy per string: `slot_bajtów → max_znaki` (uwzględniając szerokość W/F vs półszerokie)
i wypisze je w plikach dla tłumacza, zgodnie z klasami powyżej. Stała szerokość = twardy limit;
grow (fabuła) = limit tylko liniowy (46).
