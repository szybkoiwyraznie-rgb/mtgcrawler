# Predefiniowane rozmieszczenia w misjach: mechy i jednostki bojowe

Oparty na źródłach binarnych katalog jednostek i maszyn rozstawianych skryptowo po wszystkich stronach konfliktu. Pomija puste gniazda wyboru gracza. Dla każdej jednostki wieloosobowej wyznacza rzeczywistych aktywnych pilotów wspierających w danej misji na podstawie kodu wykonawczego 1.08 (`DATA.PSP`) oraz skryptów scenariuszy (`.bin`), zamiast przepisywać globalną listę domyślną z `unit_list`.

## Zakres i zasady odczytu

- **Pokrycie pakietów:** 24 kontenery `eventP` zawierające pliki `_Entry.dat` (eventP00.cpk, eventP01.EDAT, eventP02.EDAT, eventP03.EDAT, eventP04.EDAT, eventP05.EDAT, eventP06.EDAT, eventP07.EDAT, eventP08.EDAT, eventP09.EDAT, eventP13.EDAT, eventP20.EDAT, eventP21.EDAT, eventP22.EDAT, eventP23.EDAT, eventP24.EDAT, eventP25.EDAT, eventP26.EDAT, eventP27.EDAT, eventP28.EDAT, eventP29.EDAT, eventP30.EDAT, eventP31.EDAT, eventP32.EDAT); 226 instancji plików odpowiadających 224 unikalnym kodom misji. Sprawdzone osobno pakiety `evept101.EDAT`–`evept108.EDAT` nie zawierają członków `_Entry.dat`.
- **Pokrycie rekordów `_Entry.dat`:** 8915 rekordów 64-bajtowych w 226 plikach `_Entry.dat` (8504 rekordów ma jednocześnie niezerowe `Entry ID` oraz `unit_id`). Wszystkie niezerowe identyfikatory jednostek i pilotów rozwiązują się do kanonicznych nazw z pakietu `pakiet_PL`.
- **Wykluczone gniazda wyboru i obiekty użytkowe:** 205 rekordów ma `Entry ID = 0`, a 368 ma `unit_id = 0` (zakresy częściowo wspólne — są to gniazda oddziału gracza lub puste wpisy). Obiekty użytkowe mapy — **Container** (`unit_id = 3670`, 184 rekordy) oraz **Moduł naprawy** (`unit_id = 3660`, 35 rekordów) — wyłączono z list bojowych i podsumowano na końcu dokumentu.
- **Powtarzające się stany `Entry ID`:** identyczne wiersze o tym samym `(Entry ID, unit_id, pilot_id, strona)` są łączone. Jeżeli jedno `Entry ID` występuje w kilku wariantach (np. przemiana formy lub kolejna faza bossa), warianty są zachowane z jawnym oznaczeniem `obecny alternatywny rekord Entry ID` i nie oznaczają jednoczesnej obecności na mapie.
- **Oznaczenia misji:** nagłówki podają odcinek (lub tryb Symulatora), polski tytuł misji z `_ext.dat` / `05_mission_text.jsonl` oraz dokładny kod źródłowy `DL…` / `SM…`.
- **Przynależność stron (zweryfikowana w silniku 1.08 `0x1f9810` oraz `op 519` `0x24af0c`):** pole bitowe `(w[3] >> 8) & 7` w 64-bajtowym rekordzie `_Entry.dat` określa początkową stronę jednostki (`0` — gracz, `2` — sojusznik NPC, `1` — wróg, `4` — strona neutralna / trzecia). Jeżeli skrypt `.bin` zmienia stronę w trakcie misji rozkazem `op 519(entry_id, strona)`, zmiana ta jest jawnie odnotowana przy jednostce.
- **Pilot główny i aktywni piloci wspierający w misji (`0x202a68..0x202c1c`, `0x214688..0x2146e0`, `0x1d9500..0x1d96dc`):** trzecie słowo 32-bitowe rekordu (`w[2]`) wskazuje pilota głównego (slot 0), natomiast pętla inicjalizacji załogi `0x202b80..0x202bd8` dodaje do slotów `1..4` niezerowych sub-pilotów z `unit_list` (`i16@+100..+106`), po czym silnik i skrypt misji nakładają warunki fabularne: dla **Exart** (`3900`) flaga `1075` odblokowuje **Himari Yaegaki** od `DL101_11` (w odcinku 0 brak sub-pilotów), a flaga `1112` odblokowuje **Vasage'a** w trakcie `DL310_20` (sekcja 2) i odłącza go na starcie `DL833_11`; dodatkowo rozkazy skryptowe `op 516` / `op 679` oraz strażnik fuzji Zeke (`0x214688..0x2146e0` w `DL830_11` dla **Fiony Elisi Linette**) modyfikują aktywną obsadę w konkretnych misjach.
- **Warunki misji i fale:** polskie opisy warunków z `_ext.dat` są cytowane w bloku `Warunki misji`. Dokładny numer tury pojawienia się posiłków zależy od wyzwalaczy zdarzeń w `.bin`.
- **Cele niebędące mechami:** miny, wieżyczki, bramy Mucus, rakiety i wieże są zachowane na listach bojowych z oznaczeniem `cel/obiekt skryptowy; nie jest pilotowanym mechem`.
- **Weryfikacja źródeł:** wszystkie 21 plików `config00.cpk`, `config01`–`config19.EDAT` oraz `configst.cpk` zgadzają się bajt w bajt z sumami kontrolnymi w `docs/mech-catalog/source-inventory.json`, a kod wykonawczy 1.08 (`DATA.PSP`, SHA-256 `26e7f1a17ace5276076e6f904934a885a99c9f7fae7c665855435797e9edd052`) posłużył do weryfikacji logiki załóg i stron.

**Łączna liczba rekordów bojowych według początkowej strony (po wyłączeniu obiektów użytkowych mapy, przed łączeniem duplikatów):** 882 sojuszniczych (gracza), 61 sojuszniczych (NPC), 7266 wrogich, 76 neutralnych / trzeciej strony (łącznie 8285 rekordów bojowych).

## Katalog misji

### Odcinek 0 — Szkolenie podstawowe (`DL100_01`)

**Źródło:** `eventP00.cpk/DL100_01_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: brak

**Jednostki wrogie:**
  - **Brocken/Melee** — pilot główny: Control AI — ×3 rekordy źródłowe Entry ID

### Odcinek 0 — Na ratunek White Base (`DL100_02`)

**Źródło:** `eventP00.cpk/DL100_02_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: brak
  - **Gundam** — pilot główny: Amuro Ray
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Zaku II (Char)** — pilot główny: Char Aznable
  - **Zaku II/Bazooka** — pilot główny: Crown
  - **Zaku II/Karabin maszynowy** — pilot główny: Slender

### Odcinek 1 — Szalejący prototyp Labora (`DL101_11`)

**Źródło:** `eventP00.cpk/DL101_11_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **Ingram nr 1** — pilot główny: Noa Izumi
  - **Ingram nr 2** — pilot główny: Isao Ota
  - **Medea** — pilot główny: Żołnierz JSDF

**Jednostki wrogie:**
  - **HAL-X10** — pilot główny: Shinohara HOS
  - **HAL-X10/Green** — pilot główny: Shinohara HOS — ×3 rekordy źródłowe Entry ID

**Jednostki neutralne / trzeciej strony:**
  - **Helldiver** — pilot główny: Żołnierz JSDF
  - **Helldiver** — pilot główny: Żołnierz JSDF — ×2 rekordy źródłowe Entry ID

### Odcinek 1 — Black Tri-Stars (`DL101_20`)

**Źródło:** `eventP00.cpk/DL101_20_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.
**Uwaga o rekordach alternatywnych:** 5 identyfikatorów `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **G-Fighter** — pilot główny: Sayla Mass
  - **Guncannon** — pilot główny: Kai Shiden
  - **Gundam** — pilot główny: Amuro Ray
  - **Guntank** — pilot główny: Hayato Kobayashi
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Dom (Black Tri-Stars)** — pilot główny: Gaia
  - **Dom (Black Tri-Stars)** — pilot główny: Mash
  - **Dom (Black Tri-Stars)** — pilot główny: Ortega
  - **Dopp** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID
  - **Dopp** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID
  - **Wieżyczka uniwersalna** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Wieżyczka uniwersalna** — pilot główny: Żołnierz Zeonu — ×5 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID

### Odcinek 1 — Powstrzymaj pocisk termojądrowy (`DL101_30`)

**Źródło:** `eventP00.cpk/DL101_30_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.
**Uwaga o rekordach alternatywnych:** 4 identyfikatory `Entry ID` posiadają więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **G-Fighter** — pilot główny: Sayla Mass
  - **Guncannon** — pilot główny: Kai Shiden
  - **Gundam** — pilot główny: Amuro Ray
  - **Guntank** — pilot główny: Hayato Kobayashi
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Dom** — pilot główny: Żołnierz Zeonu — ×3 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID
  - **Dom** — pilot główny: Żołnierz Zeonu — ×3 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID
  - **Dopp** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID
  - **Dopp** — pilot główny: Żołnierz Zeonu — obecny alternatywny rekord Entry ID
  - **H-Bomb Missile** — pilot główny: Brak przypisanego klucza pilota w Entry — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID

### Odcinek 1 — Trening Klasy Obrony (`DL101_40`)

**Źródło:** `eventP00.cpk/DL101_40_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **Raijin-Oh** — pilot główny: Jin Hyuga — piloci wspierający w misji: Asuka Tsukishiro, Koji Hoshiyama

**Jednostki wrogie:**
  - **Brocken/Melee** — pilot główny: Control AI — ×4 rekordy źródłowe Entry ID

### Odcinek 1 — Start Alexa (`DL101_50`)

**Źródło:** `eventP00.cpk/DL101_50_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.
**Zmiana obsady oddziału gracza (skrypt `.bin`):** w sekcji 0 skrypt usuwa z obsady maszyny pilota **Seishiro Kusanagi** pilota wspierającego **Himari Yaegaki**.

**Jednostki sojusznicze (gracza):**
  - **Gundam Ez8** — pilot główny: Shiro Amada
  - **Gundam Ground Type** — pilot główny: Karen Joshua
  - **Gundam Ground Type** — pilot główny: Terry Sanders Jr.
  - **Gundam Ground Type/głowa GM** — pilot główny: Karen Joshua
  - **Hover Truck** — pilot główny: Michel Ninorich — piloci wspierający w misji: Eledore Massis
  - **Wieżyczka uniwersalna** — pilot główny: Narration — cel/obiekt skryptowy; nie jest pilotowanym mechem

**Jednostki wrogie:**
  - **Kampfer/Bazooka** — pilot główny: Andy Strauss
  - **Kampfer/High Mobility** — pilot główny: Mikhail Kaminsky
  - **Zaku II Kai** — pilot główny: Gabriel Ramirez Garcia
  - **Zaku II Kai** — pilot główny: Hardy Steiner

### Odcinek 1 — Ratuj transportowiec Medea (`DL101_60`)

**Źródło:** `eventP00.cpk/DL101_60_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
> Jako sojuszniczy NPC pojawi się Medea.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Gundam Ez8** — pilot główny: Shiro Amada
  - **Gundam Ground Type** — pilot główny: Terry Sanders Jr.
  - **Gundam Ground Type/głowa GM** — pilot główny: Karen Joshua
  - **Hover Truck** — pilot główny: Michel Ninorich — piloci wspierający w misji: Eledore Massis
  - **Mucus Gate S** — pilot główny: Brak przypisanego klucza pilota w Entry — cel/obiekt skryptowy; nie jest pilotowanym mechem

**Jednostki sojusznicze (NPC):**
  - **Medea** — pilot główny: Oficer Federacji

**Jednostki wrogie:**
  - **Dopp** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Dopp** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu

### Odcinek 1 — Szalejący Labor powraca (`DL101_70`)

**Źródło:** `eventP00.cpk/DL101_70_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Ingram nr 1** — pilot główny: Noa Izumi
  - **Ingram nr 2** — pilot główny: Isao Ota
  - **Raijin-Oh** — pilot główny: Jin Hyuga — piloci wspierający w misji: Asuka Tsukishiro, Koji Hoshiyama

**Jednostki wrogie:**
  - **Brocken/Melee** — pilot główny: Control AI — ×5 rekordów źródłowych Entry ID

### Odcinek 1 — Śledztwo pod przykrywką (`DL101_80`)

**Źródło:** `eventP00.cpk/DL101_80_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **Ingram nr 1** — pilot główny: Noa Izumi
  - **Ingram nr 2** — pilot główny: Isao Ota

**Jednostki sojusznicze (NPC):**
  - **Mucus Gate S** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem

**Jednostki wrogie:**
  - **HAL-X10/Green** — pilot główny: Shinohara HOS — ×4 rekordy źródłowe Entry ID
  - **Helldiver** — pilot główny: Control AI — ×4 rekordy źródłowe Entry ID

### Odcinek 2 — Groźba czająca się pod ziemią (`DL102_11`)

**Źródło:** `eventP00.cpk/DL102_11_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **Go-Saurer** — pilot główny: Kenichi Minezaki — piloci wspierający w misji: Hiromi Tachibana, Shinobu Asaoka, Taro Shirogane, Yoji Hiyama
  - **Gurren Lagann (Simon)** — pilot główny: Simon — piloci wspierający w misji: Kamina, Yoko, Boota
  - **Ingram nr 1** — pilot główny: Noa Izumi
  - **Ingram nr 2** — pilot główny: Isao Ota
  - **Mazinger Z** — pilot główny: Koji Kabuto — ×2 rekordy źródłowe Entry ID
  - **Raijin-Oh** — pilot główny: Jin Hyuga — piloci wspierający w misji: Asuka Tsukishiro, Koji Hoshiyama
  - **Shin Getter-1 (Go)** — pilot główny: Go — piloci wspierający w misji: Kei, Gai

**Jednostki wrogie:**
  - **Bolt Robo/Long-Range** — pilot główny: Mechabestia — ×5 rekordów źródłowych Entry ID
  - **Bolt Robo/Melee** — pilot główny: Mechabestia — ×8 rekordów źródłowych Entry ID
  - **Bolt Robo/Standard** — pilot główny: Mechabestia — ×9 rekordów źródłowych Entry ID
  - **Invader/Ground** — pilot główny: Invader — ×15 rekordów źródłowych Entry ID
  - **Mucus Gate S IN** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Mucus Gate S MC** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×12 rekordów źródłowych Entry ID

### Odcinek 2 — Czarny Labor (`DL102_20`)

**Źródło:** `eventP01.EDAT/DL102_20_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **Ingram nr 1** — pilot główny: Noa Izumi
  - **Ingram nr 2** — pilot główny: Isao Ota

**Jednostki sojusznicze (NPC):**
  - **HAL-X10/Green** — pilot główny: Żołnierz JSDF

**Jednostki wrogie:**
  - **Brocken/Działko automatyczne** — pilot główny: Control AI — ×4 rekordy źródłowe Entry ID
  - **Brocken/Melee** — pilot główny: Control AI — ×2 rekordy źródłowe Entry ID
  - **Griffon** — pilot główny: Badrinath Harchand — ×2 rekordy źródłowe Entry ID

**Jednostki neutralne / trzeciej strony:**
  - **Helldiver** — pilot główny: Żołnierz JSDF — ×2 rekordy źródłowe Entry ID
  - **Helldiver** — pilot główny: Żołnierz JSDF — ×2 rekordy źródłowe Entry ID

### Odcinek 2 — Ryk dziczy (`DL102_30`)

**Źródło:** `eventP01.EDAT/DL102_30_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **Final Dancouga** — pilot główny: Shinobu Fujiwara — piloci wspierający w misji: Sara Yuki, Ryo Shiba, Masato Shikibu, Alan Igor
  - **Ingram nr 1** — pilot główny: Noa Izumi
  - **Ingram nr 2** — pilot główny: Isao Ota

**Jednostki wrogie:**
  - **Nekton Assault** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID

### Odcinek 2 — Bitwa o Jaburo (`DL102_40`)

**Źródło:** `eventP01.EDAT/DL102_40_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **G-Fighter** — pilot główny: Sayla Mass
  - **Guncannon** — pilot główny: Kai Shiden
  - **Gundam** — pilot główny: Amuro Ray
  - **Gundam Ez8** — pilot główny: Shiro Amada
  - **Gundam Ground Type** — pilot główny: Terry Sanders Jr.
  - **Gundam Ground Type/głowa GM** — pilot główny: Karen Joshua
  - **Guntank** — pilot główny: Hayato Kobayashi
  - **Hover Truck** — pilot główny: Michel Ninorich — piloci wspierający w misji: Eledore Massis

**Jednostki wrogie:**
  - **Dom** — pilot główny: Żołnierz Zeonu — ×5 rekordów źródłowych Entry ID
  - **Dom** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Zaku II (Char)** — pilot główny: Char Aznable
  - **Zaku II/Bazooka** — pilot główny: Crown
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu — ×3 rekordy źródłowe Entry ID
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zaku II/Karabin maszynowy** — pilot główny: Slender
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu
  - **Zanzibar** — pilot główny: Oficer Zeonu
  - **Zanzibar** — pilot główny: Oficer Zeonu

### Odcinek 2 — Szturm Apsalusa (`DL102_50`)

**Źródło:** `eventP01.EDAT/DL102_50_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **G-Fighter** — pilot główny: Sayla Mass
  - **Guncannon** — pilot główny: Kai Shiden
  - **Gundam** — pilot główny: Amuro Ray
  - **Gundam Ez8** — pilot główny: Shiro Amada
  - **Gundam Ground Type** — pilot główny: Terry Sanders Jr.
  - **Gundam Ground Type/głowa GM** — pilot główny: Karen Joshua
  - **Guntank** — pilot główny: Hayato Kobayashi
  - **Hover Truck** — pilot główny: Michel Ninorich — piloci wspierający w misji: Eledore Massis
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Apsalus III** — pilot główny: Ginias Sahalin
  - **Dom** — pilot główny: Żołnierz Zeonu
  - **Dom** — pilot główny: Żołnierz Zeonu
  - **Gouf (Ramba Ral)** — pilot główny: Ramba Ral
  - **Zaku II Kai** — pilot główny: Cozun Graham
  - **Zaku II Kai** — pilot główny: Żołnierz Zeonu
  - **Zaku II/Karabin maszynowy** — pilot główny: Acous
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu
  - **Zanzibar** — pilot główny: Crowley Hamon

**Jednostki neutralne / trzeciej strony:**
  - **Mucus Gate S** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 2 — Przebicie się siłą (`DL102_60`)

**Źródło:** `eventP01.EDAT/DL102_60_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.
**Uwaga o rekordach alternatywnych:** 1 identyfikator `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **G-Fighter** — pilot główny: Sayla Mass — obecny alternatywny rekord Entry ID
  - **Guncannon** — pilot główny: Kai Shiden — obecny alternatywny rekord Entry ID
  - **Gundam** — pilot główny: Amuro Ray — obecny alternatywny rekord Entry ID
  - **Guntank** — pilot główny: Hayato Kobayashi — obecny alternatywny rekord Entry ID
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Musai** — pilot główny: Dren
  - **Musai** — pilot główny: Oficer Zeonu — ×2 rekordy źródłowe Entry ID
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID

### Odcinek 2 — W pościgu za Zanzibarem (`DL102_70`)

**Źródło:** `eventP01.EDAT/DL102_70_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.
**Uwaga o rekordach alternatywnych:** 1 identyfikator `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **G-Fighter** — pilot główny: Sayla Mass — obecny alternatywny rekord Entry ID
  - **Guncannon** — pilot główny: Kai Shiden — obecny alternatywny rekord Entry ID
  - **Gundam** — pilot główny: Amuro Ray — obecny alternatywny rekord Entry ID
  - **Guntank** — pilot główny: Hayato Kobayashi — obecny alternatywny rekord Entry ID
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Bigro** — pilot główny: Tokwan
  - **Gelgoog (Char)** — pilot główny: Char Aznable
  - **Rick Dom** — pilot główny: Crown
  - **Rick Dom** — pilot główny: Slender
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×3 rekordy źródłowe Entry ID
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zaku II Kai** — pilot główny: Żołnierz Zeonu
  - **Zaku II Kai** — pilot główny: Żołnierz Zeonu
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu
  - **Zanzibar** — pilot główny: Oficer Zeonu — zmiana strony w trakcie misji: wroga / agresywna frakcja

### Odcinek 2 — Klasa Obrony leci w kosmos (`DL102_90`)

**Źródło:** `eventP01.EDAT/DL102_90_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Daiteioh** — pilot główny: Taro Omomo — piloci wspierający w misji: Mai Ozora, Kakeru Daichi
  - **Ganbaruger** — pilot główny: Kotaro Kirigakure — piloci wspierający w misji: Yosuke Kazamatsuri, Rikiya Ryuzaki
  - **Go-Saurer** — pilot główny: Kenichi Minezaki — piloci wspierający w misji: Hiromi Tachibana, Shinobu Asaoka, Taro Shirogane, Yoji Hiyama
  - **Gurren Lagann (Simon)** — pilot główny: Simon — piloci wspierający w misji: Kamina, Yoko, Boota
  - **Raijin-Oh** — pilot główny: Jin Hyuga — piloci wspierający w misji: Asuka Tsukishiro, Koji Hoshiyama

**Jednostki wrogie:**
  - **Bolt Robo/Anti-Air** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Bolt Robo/Long-Range** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Bolt Robo/Melee** — pilot główny: Mechabestia — ×5 rekordów źródłowych Entry ID
  - **Bolt Robo/Standard** — pilot główny: Mechabestia — ×4 rekordy źródłowe Entry ID
  - **Brocken/Cannon** — pilot główny: Control AI — ×2 rekordy źródłowe Entry ID
  - **Brocken/Działko automatyczne** — pilot główny: Control AI — ×2 rekordy źródłowe Entry ID
  - **Brocken/Melee** — pilot główny: Control AI — ×2 rekordy źródłowe Entry ID
  - **Gandoppler** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Mucus Gate S MC** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 3 — Zbrojna interwencja Gundamów (`DL103_11`)

**Źródło:** `eventP01.EDAT/DL103_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **Final Dancouga** — pilot główny: Shinobu Fujiwara — piloci wspierający w misji: Sara Yuki, Ryo Shiba, Masato Shikibu, Alan Igor
  - **Mazinger Z** — pilot główny: Koji Kabuto
  - **Shin Getter-1 (Go)** — pilot główny: Go — piloci wspierający w misji: Kei, Gai
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki sojusznicze (NPC):**
  - **Gundam Exia** — pilot główny: Setsuna F. Seiei
  - **Wing Gundam Zero/NB** — pilot główny: Heero Yuy

**Jednostki wrogie:**
  - **Dom (Black Tri-Stars)** — pilot główny: Gaia
  - **Dom (Black Tri-Stars)** — pilot główny: Mash
  - **Dom (Black Tri-Stars)** — pilot główny: Ortega
  - **Gelgoog (Char)** — pilot główny: Char Aznable
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Zanzibar** — pilot główny: Garma Zabi
  - **Zanzibar** — pilot główny: M'Quve

**Jednostki neutralne / trzeciej strony:**
  - **Mucus Gate S** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 3 — Skradający się czarny cień (`DL103_12`)

**Źródło:** `eventP01.EDAT/DL103_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **Final Dancouga** — pilot główny: Shinobu Fujiwara — piloci wspierający w misji: Sara Yuki, Ryo Shiba, Masato Shikibu, Alan Igor
  - **Gundam Exia** — pilot główny: Setsuna F. Seiei
  - **Mazinger Z** — pilot główny: Koji Kabuto
  - **Shin Getter-1 (Go)** — pilot główny: Go — piloci wspierający w misji: Kei, Gai
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima
  - **Wing Gundam Zero** — pilot główny: Heero Yuy

**Jednostki wrogie:**
  - **Invader/Air** — pilot główny: Invader — ×6 rekordów źródłowych Entry ID
  - **Invader/Ground** — pilot główny: Invader — ×10 rekordów źródłowych Entry ID
  - **Metal Beast/Muszla** — pilot główny: Invader

### Odcinek 3 — Zielony najeźdźca (`DL103_20`)

**Źródło:** `eventP01.EDAT/DL103_20_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **Ingram nr 1** — pilot główny: Noa Izumi
  - **Ingram nr 2** — pilot główny: Isao Ota
  - **Keroro Robo Mk-II** — pilot główny: Sierżant Keroro

**Jednostki wrogie:**
  - **Brocken/Działko automatyczne** — pilot główny: Control AI — ×5 rekordów źródłowych Entry ID
  - **Brocken/Melee** — pilot główny: Control AI — ×8 rekordów źródłowych Entry ID

**Jednostki neutralne / trzeciej strony:**
  - **Brocken/Melee** — pilot główny: Control AI — ×6 rekordów źródłowych Entry ID — zmiana strony w trakcie misji: sojusznicza (NPC)

### Odcinek 3 — Szturm na kryjówkę piratów (`DL103_30`)

> **Różne warianty pakietów źródłowych:** ten kod misji występuje w 2 pakietach. Każdy wariant pokazano osobno bez łączenia rekordów.

#### Pakiet źródłowy: `eventP01.EDAT`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Gelgoog** — pilot główny: Pilot MS — ×4 rekordy źródłowe Entry ID
  - **Rick Dom** — pilot główny: Pilot MS — ×4 rekordy źródłowe Entry ID
  - **Zaku II/Bazooka** — pilot główny: Pilot MS — ×3 rekordy źródłowe Entry ID
  - **Zaku II/Karabin maszynowy** — pilot główny: Pilot MS — ×3 rekordy źródłowe Entry ID

#### Pakiet źródłowy: `eventP09.EDAT`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Gelgoog** — pilot główny: Pilot MS — ×4 rekordy źródłowe Entry ID
  - **Rick Dom** — pilot główny: Pilot MS — ×4 rekordy źródłowe Entry ID
  - **Zaku II/Bazooka** — pilot główny: Pilot MS — ×2 rekordy źródłowe Entry ID
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu
  - **Zaku II/Karabin maszynowy** — pilot główny: Pilot MS — ×2 rekordy źródłowe Entry ID
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu

### Odcinek 3 — Napaść na bazę marsjańską (`DL103_40`)

**Źródło:** `eventP01.EDAT/DL103_40_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Enhanced Layzner** — pilot główny: Albatro Null Eiji Asuka
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass
  - **RVF-25 Messiah/Fighter** — pilot główny: Luca Angeloni
  - **VF-25F Messiah/Fighter** — pilot główny: Alto Saotome
  - **VF-25G Messiah/Fighter** — pilot główny: Michael Blanc

**Jednostki wrogie:**
  - **Braver** — pilot główny: Żołnierz Gradosu — ×6 rekordów źródłowych Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×6 rekordów źródłowych Entry ID
  - **Daljan** — pilot główny: Gosterro

### Odcinek 4 — Atak na okręt Gradosu (`DL104_11`)

**Źródło:** `eventP01.EDAT/DL104_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 1 identyfikator `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Enhanced Layzner** — pilot główny: Albatro Null Eiji Asuka
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Braver** — pilot główny: Żołnierz Gradosu — ×11 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×12 rekordów źródłowych Entry ID
  - **Daljan** — pilot główny: Gosterro
  - **Nowy gigantyczny lotniskowiec Grados** — pilot główny: Oficer Gradosu — obecny alternatywny rekord Entry ID

### Odcinek 4 — Szpony Invaderów (`DL104_20`)

**Źródło:** `eventP01.EDAT/DL104_20_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Shin Getter-1 (Go)** — pilot główny: Go — piloci wspierający w misji: Kei, Gai
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Invader/Air** — pilot główny: Invader — ×8 rekordów źródłowych Entry ID
  - **Invader/Ground** — pilot główny: Invader — ×8 rekordów źródłowych Entry ID
  - **Mucus Gate S IN** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 4 — Przybysz z innego czasu (`DL104_30`)

**Źródło:** `eventP01.EDAT/DL104_30_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 6 identyfikatorów `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki — obecny alternatywny rekord Entry ID
  - **GoShogun** — pilot główny: Shingo Hojo — piloci wspierający w misji: Killy Gagley, Remy Shimada
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass
  - **Raijin-Oh** — pilot główny: Jin Hyuga — piloci wspierający w misji: Asuka Tsukishiro, Koji Hoshiyama — obecny alternatywny rekord Entry ID

**Jednostki wrogie:**
  - **Bolt Robo/Anti-Air** — pilot główny: Mechabestia — ×7 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID
  - **Bolt Robo/Long-Range** — pilot główny: Mechabestia — ×8 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID
  - **Bolt Robo/Melee** — pilot główny: Mechabestia — ×4 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID
  - **Bolt Robo/Standard** — pilot główny: Mechabestia — ×7 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID
  - **Dark Go-Saurer** — pilot główny: Mechabestia
  - **Mucus Gate S MC** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 4 — Lelouch buntownik (`DL104_40`)

**Źródło:** `eventP20.EDAT/DL104_40_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.
**Uwaga o rekordach alternatywnych:** 3 identyfikatory `Entry ID` posiadają więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Gawain** — pilot główny: Zero — piloci wspierający w misji: C.C. — obecny alternatywny rekord Entry ID
  - **L-Gaim** — pilot główny: Daba Myroad — piloci wspierający w misji: Lilis Faw
  - **Novel D-Sserd** — pilot główny: Gaw Ha Leccee
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×15 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×11 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID

**Jednostki neutralne / trzeciej strony:**
  - **Gawain** — pilot główny: Lelouch Lamperouge — piloci wspierający w misji: C.C. — obecny alternatywny rekord Entry ID

### Odcinek 5 — Brama warp (`DL105_11`)

**Źródło:** `eventP01.EDAT/DL105_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 4 identyfikatory `Entry ID` posiadają więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki — obecny alternatywny rekord Entry ID
  - **Gurren Lagann (Simon)** — pilot główny: Simon — piloci wspierający w misji: Kamina, Yoko, Boota — obecny alternatywny rekord Entry ID
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Enkidu** — pilot główny: Viral
  - **Nekton Assault** — pilot główny: Mucus — ×13 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×13 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID

**Jednostki neutralne / trzeciej strony:**
  - **Vasage** — pilot główny: Vasage

### Odcinek 5 — Viral, zwierzoczłowiek (`DL105_12`)

**Źródło:** `eventP01.EDAT/DL105_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **Final Dancouga** — pilot główny: Shinobu Fujiwara — piloci wspierający w misji: Sara Yuki, Ryo Shiba, Masato Shikibu, Alan Igor
  - **GoShogun** — pilot główny: Shingo Hojo — piloci wspierający w misji: Killy Gagley, Remy Shimada
  - **Gundam Exia** — pilot główny: Setsuna F. Seiei
  - **Gurren Lagann (Kamina)** — pilot główny: Kamina — piloci wspierający w misji: Simon, Yoko, Boota
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass
  - **Vasage** — pilot główny: Vasage
  - **VF-25F Messiah/Fighter** — pilot główny: Alto Saotome

**Jednostki wrogie:**
  - **Enkidu** — pilot główny: Viral
  - **Mucus Gate S** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×28 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×13 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID

### Odcinek 5 — Chłopiec z planety Zi (`DL105_20`)

**Źródło:** `eventP01.EDAT/DL105_20_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.
**Uwaga o rekordach alternatywnych:** 2 identyfikatory `Entry ID` posiadają więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Command Wolf/Black/Upgraded** — pilot główny: Irvine
  - **Gustav/Moonbay Special** — pilot główny: Moonbay
  - **Shield Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette — obecny alternatywny rekord Entry ID

**Jednostki wrogie:**
  - **Molga** — pilot główny: Pilot Zoida — ×3 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Pilot Zoida — ×3 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Pilot Zoida — obecny alternatywny rekord Entry ID
  - **Redler** — pilot główny: Pilot Zoida — obecny alternatywny rekord Entry ID
  - **Redler (Viola)** — pilot główny: Viola

**Jednostki neutralne / trzeciej strony:**
  - **Shield Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette — obecny alternatywny rekord Entry ID

### Odcinek 5 — Źródła ambicji (`DL105_30`)

**Źródło:** `eventP01.EDAT/DL105_30_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.
**Uwaga o rekordach alternatywnych:** 4 identyfikatory `Entry ID` posiadają więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Scopedog RSC (Byman)** — pilot główny: Byman Hagard
  - **Scopedog RSC (Chirico)** — pilot główny: Chirico Cuvie
  - **Scopedog RSC (Gregore)** — pilot główny: Gregore Garosh
  - **Scopedog RSC (Murza)** — pilot główny: Murza Melym

**Jednostki wrogie:**
  - **Mucus Gate S** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Scopedog TC-RS** — pilot główny: Żołnierz Red Shoulder — ×13 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID
  - **Scopedog TC-RS/M** — pilot główny: Żołnierz Red Shoulder — ×8 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID
  - **Wieżyczka uniwersalna** — pilot główny: Control AI — ×4 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 5 — Bohater Lamuness znów wyrusza (`DL105_40`)

**Źródło:** `eventP01.EDAT/DL105_40_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Keroro Robo Mk-II** — pilot główny: Sierżant Keroro
  - **King Squasher** — pilot główny: Hero Lamuness — piloci wspierający w misji: Tama-Q
  - **Queen Cideron/Ally** — pilot główny: Da Cider — piloci wspierający w misji: Hebi Metako

**Jednostki wrogie:**
  - **Monskar Medessa** — pilot główny: Monskar — ×6 rekordów źródłowych Entry ID
  - **Monskar Neppoon** — pilot główny: Monskar — ×5 rekordów źródłowych Entry ID

### Odcinek 5 — Groza komórek DG (`DL105_50`)

**Źródło:** `eventP02.EDAT/DL105_50_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **God Gundam** — pilot główny: Domon Kasshu
  - **LCT-05-AT Space Landing Craft** — pilot główny: Bouleuse Gotho

**Jednostki sojusznicze (NPC):**
  - **Scopedog** — pilot główny: Pilot AT
  - **Scopedog** — pilot główny: Pilot AT

**Jednostki wrogie:**
  - **Death Army** — pilot główny: DG Cells — ×6 rekordów źródłowych Entry ID
  - **Gundam Head** — pilot główny: DG Cells

### Odcinek 5 — Niedobitki Klanu Mrocznego Smoka (`DL105_70`)

**Źródło:** `eventP02.EDAT/DL105_70_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Dark Knight Steru/Dark Dragon Form** — pilot główny: Galden

**Jednostki wrogie:**
  - **Okręt eskorty Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka
  - **Żołnierz Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka — ×3 rekordy źródłowe Entry ID
  - **Żołnierz Mrocznego Smoka/Lot** — pilot główny: Żołnierz Mrocznego Smoka — ×2 rekordy źródłowe Entry ID

### Odcinek 5 — Biały rycerz (`DL105_90`)

**Źródło:** `eventP21.EDAT/DL105_90_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
> Można używać "Iron Kong SS".
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Iron Kong SS/Ally** — pilot główny: Karl Lichten Schubaltz
  - **Lancelot/Ally** — pilot główny: Suzaku Kururugi

**Jednostki wrogie:**
  - **Molga** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Pilot Zoida — ×4 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Pilot Zoida — ×4 rekordy źródłowe Entry ID

**Jednostki neutralne / trzeciej strony:**
  - **Mucus Gate S** — pilot główny: Pilot Zoida — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 6 — Macross Frontier (`DL206_11`)

**Źródło:** `eventP02.EDAT/DL206_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass
  - **VF-25F Messiah/Fighter** — pilot główny: Alto Saotome

**Jednostki wrogie:**
  - **Bat-Shu/Strong** — pilot główny: Gavlet Gablae
  - **Braver** — pilot główny: Żołnierz Gradosu — ×6 rekordów źródłowych Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×6 rekordów źródłowych Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Nowy gigantyczny lotniskowiec Grados** — pilot główny: Oficer Gradosu

### Odcinek 6 — Rodzima planeta Vajra (`DL206_12`)

**Źródło:** `eventP02.EDAT/DL206_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu
  - **Braver** — pilot główny: Żołnierz Gradosu
  - **Braver** — pilot główny: Żołnierz Gradosu
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×6 rekordów źródłowych Entry ID
  - **Pancernik kosmiczny klasy Lesrion** — pilot główny: Oficer Balarantu

### Odcinek 6 — Flota ISTO (`DL206_50`)

**Źródło:** `eventP02.EDAT/DL206_50_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 1 identyfikator `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Enhanced Layzner** — pilot główny: Albatro Null Eiji Asuka — obecny alternatywny rekord Entry ID
  - **VF-25F Messiah/Battroid Super Pack** — pilot główny: Alto Saotome — obecny alternatywny rekord Entry ID
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×5 rekordów źródłowych Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×6 rekordów źródłowych Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Pancernik kosmiczny klasy Lesrion** — pilot główny: Oficer Balarantu

### Odcinek 6 — Operacja: przeciąć szlak warp (`DL206_60`)

**Źródło:** `eventP02.EDAT/DL206_60_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Braver** — pilot główny: Żołnierz Gradosu — ×3 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×3 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **Pancernik kosmiczny klasy Lesrion** — pilot główny: Oficer Balarantu

### Odcinek 6 — Czarny Organoid (`DL206_70`)

**Źródło:** `eventP02.EDAT/DL206_70_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Command Wolf/Black/Upgraded** — pilot główny: Irvine
  - **Gustav/Moonbay Special** — pilot główny: Moonbay
  - **Mucus Gate S** — pilot główny: --- — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Shield Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette

**Jednostki sojusznicze (NPC):**
  - **Command Wolf/White** — pilot główny: Rob Herman
  - **Command Wolf/White** — pilot główny: Żołnierz Republiki Helic — ×8 rekordów źródłowych Entry ID

**Jednostki wrogie:**
  - **Dark Horn** — pilot główny: Oficer Imperium Guylos
  - **Molga** — pilot główny: Żołnierz Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Żołnierz Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Saber Tiger (Raven)** — pilot główny: Raven

### Odcinek 6 — Dostarcz zapasy Republice (`DL206_80`)

**Źródło:** `eventP02.EDAT/DL206_80_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Command Wolf/Black/Upgraded** — pilot główny: Irvine
  - **Gustav/Moonbay Special** — pilot główny: Moonbay
  - **Shield Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette

**Jednostki wrogie:**
  - **Redler** — pilot główny: Oficer Imperium Guylos — ×3 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Żołnierz Imperium Guylos — ×11 rekordów źródłowych Entry ID
  - **Redler** — pilot główny: Żołnierz Imperium Guylos — ×10 rekordów źródłowych Entry ID

### Odcinek 7 — Twierdza Mount Ossa (`DL207_11`)

**Źródło:** `eventP02.EDAT/DL207_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 2 identyfikatory `Entry ID` posiadają więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Dark Horn** — pilot główny: Oficer Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Dark Horn** — pilot główny: Żołnierz Imperium Guylos — ×3 rekordy źródłowe Entry ID
  - **Dark Horn** — pilot główny: Żołnierz Imperium Guylos — ×5 rekordów źródłowych Entry ID
  - **Iron Kong** — pilot główny: Oficer Imperium Guylos
  - **Iron Kong** — pilot główny: Żołnierz Imperium Guylos — ×2 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID
  - **Iron Kong** — pilot główny: Żołnierz Imperium Guylos — ×2 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID
  - **Molga** — pilot główny: Zoid Core — ×41 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID
  - **Redler** — pilot główny: Oficer Imperium Guylos
  - **Redler** — pilot główny: Żołnierz Imperium Guylos — ×8 rekordów źródłowych Entry ID
  - **Redler** — pilot główny: Żołnierz Imperium Guylos — ×7 rekordów źródłowych Entry ID

**Jednostki neutralne / trzeciej strony:**
  - **Mucus Gate S** — pilot główny: Control AI — ×3 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 7 — Ofensywa Schubaltza (`DL207_12`)

**Źródło:** `eventP02.EDAT/DL207_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 5 identyfikatorów `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Command Wolf/Black/Upgraded** — pilot główny: Irvine
  - **Final Dancouga** — pilot główny: Shinobu Fujiwara — piloci wspierający w misji: Sara Yuki, Ryo Shiba, Masato Shikibu, Alan Igor
  - **Gustav/Moonbay Special** — pilot główny: Moonbay
  - **Shield Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette

**Jednostki wrogie:**
  - **Dark Horn** — pilot główny: Oficer Imperium Guylos — ×7 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID
  - **Dark Horn** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID
  - **Dark Horn** — pilot główny: Żołnierz Imperium Guylos — ×2 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID
  - **Dark Horn** — pilot główny: Żołnierz Imperium Guylos — ×6 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID
  - **Iron Kong SS** — pilot główny: Karl Lichten Schubaltz
  - **Lancelot** — pilot główny: Suzaku Kururugi
  - **Molga** — pilot główny: Zoid Core — ×20 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID
  - **Redler** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Żołnierz Imperium Guylos — ×6 rekordów źródłowych Entry ID
  - **Redler** — pilot główny: Żołnierz Imperium Guylos — ×6 rekordów źródłowych Entry ID

**Jednostki neutralne / trzeciej strony:**
  - **Gawain** — pilot główny: Zero — piloci wspierający w misji: C.C.

### Odcinek 7 — Bitwa o stolicę (`DL207_13`)

**Źródło:** `eventP02.EDAT/DL207_13_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Shield Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Dark Horn** — pilot główny: Żołnierz Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Dark Horn** — pilot główny: Żołnierz Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Iron Kong** — pilot główny: Oficer Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Iron Kong** — pilot główny: Żołnierz Imperium Guylos
  - **Iron Kong** — pilot główny: Żołnierz Imperium Guylos
  - **Molga** — pilot główny: Zoid Core — ×14 rekordów źródłowych Entry ID
  - **Redler** — pilot główny: Żołnierz Imperium Guylos — ×7 rekordów źródłowych Entry ID
  - **Redler** — pilot główny: Żołnierz Imperium Guylos — ×3 rekordy źródłowe Entry ID
  - **Saber Tiger (Raven)** — pilot główny: Raven
  - **Whale King** — pilot główny: Gunther Prozen

### Odcinek 7 — W poszukiwaniu Zoid Eve (`DL207_20`)

**Źródło:** `eventP02.EDAT/DL207_20_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Command Wolf/Black/Upgraded** — pilot główny: Irvine
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **Gustav/Moonbay Special** — pilot główny: Moonbay
  - **Shield Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette

**Jednostki wrogie:**
  - **Molga** — pilot główny: Pilot Zoida — ×4 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Pilot Zoida — ×3 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Zoid Core — ×6 rekordów źródłowych Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Red Horn (Rosso)** — pilot główny: Rosso
  - **Redler (Viola)** — pilot główny: Viola

### Odcinek 7 — Rzekoma członkini Czarnych Rycerzy (`DL207_30`)

**Źródło:** `eventP02.EDAT/DL207_30_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 3 identyfikatory `Entry ID` posiadają więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **Gawain** — pilot główny: Zero — piloci wspierający w misji: C.C.
  - **Guren Mk-II** — pilot główny: Kallen Kozuki

**Jednostki wrogie:**
  - **Command Wolf/Khaki** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID — zmiana strony w trakcie misji: sojusznicza (NPC)
  - **Command Wolf/White** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID — zmiana strony w trakcie misji: sojusznicza (NPC)
  - **Command Wolf/White** — pilot główny: Pilot Zoida
  - **Gun Sniper** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID
  - **Gun Sniper** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID
  - **Gun Sniper/WW** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Zoid Core — ×11 rekordów źródłowych Entry ID

**Jednostki neutralne / trzeciej strony:**
  - **Command Wolf/Khaki** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID — zmiana strony w trakcie misji: sojusznicza (NPC)
  - **Command Wolf/White** — pilot główny: Pilot Zoida — obecny alternatywny rekord Entry ID — zmiana strony w trakcie misji: sojusznicza (NPC)
  - **Mucus Gate S** — pilot główny: --- — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 7 — Doki Doki Space (`DL207_50`)

**Źródło:** `eventP02.EDAT/DL207_50_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **God Gundam** — pilot główny: Domon Kasshu

**Jednostki wrogie:**
  - **Death Army** — pilot główny: DG Cells — ×8 rekordów źródłowych Entry ID
  - **Mucus Gate S DG** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID

### Odcinek 8 — Earthtia (`DL208_11`)

**Źródło:** `eventP02.EDAT/DL208_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Dark Knight Steru/Dark Dragon Form** — pilot główny: Galden
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass
  - **Ryu Knight Zephyr/Later** — pilot główny: Adeu Waltham
  - **Ryu Mage Magidora** — pilot główny: Paffy Pafuricia — piloci wspierający w misji: Hagu Hagu

**Jednostki wrogie:**
  - **Okręt eskorty Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka — ×2 rekordy źródłowe Entry ID
  - **Żołnierz Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka — ×11 rekordów źródłowych Entry ID
  - **Żołnierz Mrocznego Smoka/Lot** — pilot główny: Żołnierz Mrocznego Smoka — ×4 rekordy źródłowe Entry ID
  - **Żołnierz Mrocznego Smoka/Snajper** — pilot główny: Żołnierz Mrocznego Smoka — ×4 rekordy źródłowe Entry ID

### Odcinek 8 — Piraci Mrocznego Smoka (`DL208_12`)

**Źródło:** `eventP02.EDAT/DL208_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Żołnierz Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka — ×13 rekordów źródłowych Entry ID
  - **Żołnierz Mrocznego Smoka/Lot** — pilot główny: Żołnierz Mrocznego Smoka — ×11 rekordów źródłowych Entry ID
  - **Żołnierz Mrocznego Smoka/Snajper** — pilot główny: Żołnierz Mrocznego Smoka — ×9 rekordów źródłowych Entry ID

### Odcinek 8 — Da Cider powraca (`DL208_20`)

**Źródło:** `eventP02.EDAT/DL208_20_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 1 identyfikator `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki — obecny alternatywny rekord Entry ID
  - **Hulk Gunship Axe Bomber** — pilot główny: Cocoa Arara — piloci wspierający w misji: Milk Arara, Cafe au Lait Arara — obecny alternatywny rekord Entry ID
  - **Keroro Robo Mk-II** — pilot główny: Sierżant Keroro — obecny alternatywny rekord Entry ID
  - **King Squasher** — pilot główny: Hero Lamuness — piloci wspierający w misji: Tama-Q — obecny alternatywny rekord Entry ID
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Monskar Medessa** — pilot główny: Monskar — ×6 rekordów źródłowych Entry ID
  - **Monskar Neppoon** — pilot główny: Monskar — ×4 rekordy źródłowe Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID
  - **Queen Cideron** — pilot główny: Da Cider

### Odcinek 8 — Wydobycie metali rzadkich (`DL208_30`)

> **Różne warianty pakietów źródłowych:** ten kod misji występuje w 2 pakietach. Każdy wariant pokazano osobno bez łączenia rekordów.

#### Pakiet źródłowy: `eventP13.EDAT`
**Warunki misji:**
> ????
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Gurren Lagann (Simon)** — pilot główny: Simon — piloci wspierający w misji: Kamina, Yoko, Boota
  - **Gustav/Moonbay Special** — pilot główny: Moonbay

**Jednostki wrogie:**
  - **Crystal Pillar** — pilot główny: ---
  - **Żołnierz Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka — ×10 rekordów źródłowych Entry ID
  - **Żołnierz Mrocznego Smoka/Lot** — pilot główny: Żołnierz Mrocznego Smoka — ×24 rekordy źródłowe Entry ID
  - **Żołnierz Mrocznego Smoka/Snajper** — pilot główny: Żołnierz Mrocznego Smoka — ×8 rekordów źródłowych Entry ID

#### Pakiet źródłowy: `eventP22.EDAT`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Gurren Lagann (Simon)** — pilot główny: Simon — piloci wspierający w misji: Kamina, Yoko, Boota
  - **Gustav/Moonbay Special** — pilot główny: Moonbay

**Jednostki wrogie:**
  - **Crystal Pillar** — pilot główny: ---
  - **Żołnierz Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka — ×10 rekordów źródłowych Entry ID
  - **Żołnierz Mrocznego Smoka/Lot** — pilot główny: Żołnierz Mrocznego Smoka — ×24 rekordy źródłowe Entry ID
  - **Żołnierz Mrocznego Smoka/Snajper** — pilot główny: Żołnierz Mrocznego Smoka — ×8 rekordów źródłowych Entry ID

### Odcinek 8 — Red Shoulder (`DL208_45`)

**Źródło:** `eventP02.EDAT/DL208_45_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 1 identyfikator `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **Scopedog RSC (Byman)** — pilot główny: Byman Hagard
  - **Scopedog RSC (Chirico)** — pilot główny: Chirico Cuvie
  - **Scopedog RSC (Gregore)** — pilot główny: Gregore Garosh — obecny alternatywny rekord Entry ID
  - **Scopedog RSC (Murza)** — pilot główny: Murza Melym — obecny alternatywny rekord Entry ID

**Jednostki wrogie:**
  - **Scopedog** — pilot główny: Pilot AT — ×13 rekordów źródłowych Entry ID
  - **Scopedog/M** — pilot główny: Pilot AT — ×8 rekordów źródłowych Entry ID

### Odcinek 8 — Szturm na Sunsę (`DL208_50`)

**Źródło:** `eventP02.EDAT/DL208_50_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Scopedog RSC (Byman)** — pilot główny: Byman Hagard
  - **Scopedog RSC (Chirico)** — pilot główny: Chirico Cuvie
  - **Scopedog RSC (Gregore)** — pilot główny: Gregore Garosh
  - **Scopedog RSC (Murza)** — pilot główny: Murza Melym

**Jednostki sojusznicze (NPC):**
  - **Scopedog TC-RS** — pilot główny: Żołnierz Red Shoulder — ×2 rekordy źródłowe Entry ID
  - **Scopedog TC-RS/M** — pilot główny: Żołnierz Red Shoulder

**Jednostki wrogie:**
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×13 rekordów źródłowych Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×12 rekordów źródłowych Entry ID
  - **Lądowy pancernik Balarant** — pilot główny: Oficer Balarantu
  - **Mucus Gate S** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 9 — Interwencja na Sunsie (`DL209_11`)

**Źródło:** `eventP02.EDAT/DL209_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass
  - **VF-25F Messiah/Fighter Super Pack** — pilot główny: Alto Saotome

**Jednostki wrogie:**
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×5 rekordów źródłowych Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×5 rekordów źródłowych Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×2 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×2 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu
  - **Ray** — pilot główny: Oficer armii Posaydala

### Odcinek 9 — Śmiertelny bój z Riemannem (`DL209_12`)

**Źródło:** `eventP02.EDAT/DL209_12_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Scopedog RSC (Byman)** — pilot główny: Byman Hagard
  - **Scopedog RSC (Chirico)** — pilot główny: Chirico Cuvie
  - **Scopedog RSC (Gregore)** — pilot główny: Gregore Garosh
  - **Scopedog RSC (Murza)** — pilot główny: Murza Melym

**Jednostki wrogie:**
  - **Bat-Shu** — pilot główny: Posaydal Regular
  - **Bat-Shu** — pilot główny: Posaydal Regular
  - **Braver** — pilot główny: Żołnierz Gradosu
  - **Braver** — pilot główny: Żołnierz Gradosu
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×4 rekordy źródłowe Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×4 rekordy źródłowe Entry ID
  - **Lądowy pancernik Balarant** — pilot główny: Oficer Balarantu
  - **Scopedog RS (Riemann)** — pilot główny: Inge Riemann
  - **Scopedog TC-RS** — pilot główny: Żołnierz Gilgameshu — ×3 rekordy źródłowe Entry ID
  - **Scopedog TC-RS** — pilot główny: Żołnierz Gilgameshu — ×3 rekordy źródłowe Entry ID
  - **Scopedog TC-RS/M** — pilot główny: Żołnierz Gilgameshu — ×2 rekordy źródłowe Entry ID
  - **Scopedog TC-RS/M** — pilot główny: Żołnierz Gilgameshu — ×2 rekordy źródłowe Entry ID

### Odcinek 9 — Zarodek Mucus (`DL209_13`)

**Źródło:** `eventP02.EDAT/DL209_13_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Scopedog RSC (Chirico)** — pilot główny: Chirico Cuvie
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular
  - **Bat-Shu** — pilot główny: Posaydal Regular
  - **Braver** — pilot główny: Żołnierz Gradosu — ×2 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×2 rekordy źródłowe Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×6 rekordów źródłowych Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×6 rekordów źródłowych Entry ID
  - **Giga Nekton α** — pilot główny: Mucus
  - **Lądowy pancernik Balarant** — pilot główny: Oficer Balarantu
  - **Mucus Gate M** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Sarge Aupus (Nei)** — pilot główny: Nei Moh Han

**Jednostki neutralne / trzeciej strony:**
  - **Scopedog RSC (Byman)** — pilot główny: Byman Hagard
  - **Scopedog RSC (Chirico)** — pilot główny: Chirico Cuvie
  - **Scopedog RSC (Gregore)** — pilot główny: Gregore Garosh
  - **Scopedog RSC (Murza)** — pilot główny: Murza Melym

### Odcinek 9 — Cień Drago powraca (`DL209_20`)

**Źródło:** `eventP02.EDAT/DL209_20_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Go-Saurer** — pilot główny: Kenichi Minezaki — piloci wspierający w misji: Hiromi Tachibana, Shinobu Asaoka, Taro Shirogane, Yoji Hiyama
  - **Liger** — pilot główny: Ken Taiga

**Jednostki wrogie:**
  - **Seryjny Metal Knight** — pilot główny: Metal Knight — ×5 rekordów źródłowych Entry ID
  - **Seryjny Metal Knight/Ciężki** — pilot główny: Metal Knight — ×4 rekordy źródłowe Entry ID

### Odcinek 9 — Griffon kontra Alphonse (`DL209_35`)

**Źródło:** `eventP02.EDAT/DL209_35_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Ingram nr 1** — pilot główny: Noa Izumi

**Jednostki wrogie:**
  - **Griffon** — pilot główny: Badrinath Harchand

### Odcinek 9 — Wojownicy bez przystani (`DL209_40`)

**Źródło:** `eventP03.EDAT/DL209_40_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **Tallgeese/Ally** — pilot główny: Zechs Merquise
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima
  - **Wing Gundam Zero** — pilot główny: Heero Yuy

**Jednostki sojusznicze (NPC):**
  - **Medea** — pilot główny: Zechs Merquise

**Jednostki wrogie:**
  - **Giga Nekton α** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Mucus Gate M** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×12 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×10 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Shooter** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Tallgeese** — pilot główny: Zechs Merquise
  - **Zanzibar** — pilot główny: Oficer Zeonu

### Odcinek 9 — Nowy ruch Imperium Mechanizacji (`DL209_60`)

**Źródło:** `eventP03.EDAT/DL209_60_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Daiteioh** — pilot główny: Taro Omomo — piloci wspierający w misji: Mai Ozora, Kakeru Daichi
  - **Ganbaruger** — pilot główny: Kotaro Kirigakure — piloci wspierający w misji: Yosuke Kazamatsuri, Rikiya Ryuzaki
  - **Go-Saurer** — pilot główny: Kenichi Minezaki — piloci wspierający w misji: Hiromi Tachibana, Shinobu Asaoka, Taro Shirogane, Yoji Hiyama
  - **Liger** — pilot główny: Ken Taiga

**Jednostki wrogie:**
  - **Bolt Robo/Anti-Air** — pilot główny: Mechabestia
  - **Bolt Robo/Long-Range** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Bolt Robo/Standard** — pilot główny: Mechabestia — ×4 rekordy źródłowe Entry ID
  - **HAL-X10** — pilot główny: Shinohara HOS — ×4 rekordy źródłowe Entry ID
  - **Helldiver** — pilot główny: Control AI — ×4 rekordy źródłowe Entry ID

### Odcinek 9 — Incydent 30 Bunch (`DL209_70`)

**Źródło:** `eventP23.EDAT/DL209_70_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Gundam Exia** — pilot główny: Setsuna F. Seiei
  - **Hyaku Shiki** — pilot główny: Quattro Bajeena
  - **Zeta Gundam** — pilot główny: Kamille Bidan

**Jednostki wrogie:**
  - **Rick Dom** — pilot główny: Pilot MS — ×7 rekordów źródłowych Entry ID
  - **Zaku II/Bazooka** — pilot główny: Pilot MS — ×2 rekordy źródłowe Entry ID
  - **Zaku II/Karabin maszynowy** — pilot główny: Pilot MS — ×3 rekordy źródłowe Entry ID

### Odcinek 10 — Ślady złego boga (`DL310_11`)

**Źródło:** `eventP03.EDAT/DL310_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **Ganbaruger** — pilot główny: Kotaro Kirigakure — piloci wspierający w misji: Yosuke Kazamatsuri, Rikiya Ryuzaki
  - **Liger** — pilot główny: Ken Taiga
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Nekton Assault** — pilot główny: Mucus — ×23 rekordy źródłowe Entry ID
  - **Seryjny Metal Knight** — pilot główny: Metal Knight — ×12 rekordów źródłowych Entry ID

### Odcinek 10 — Mucus Gate pod ziemią (`DL310_12`)

**Źródło:** `eventP03.EDAT/DL310_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **Liger** — pilot główny: Ken Taiga

**Jednostki wrogie:**
  - **Giga Nekton α** — pilot główny: Mucus
  - **Mucus Gate M DR** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Seryjny Metal Knight** — pilot główny: Metal Knight — ×13 rekordów źródłowych Entry ID
  - **Seryjny Metal Knight/Ciężki** — pilot główny: Metal Knight — ×3 rekordy źródłowe Entry ID

### Odcinek 10 — Rozmowa z Wysłannikiem (`DL310_20`)

**Źródło:** `eventP03.EDAT/DL310_20_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage (dołącza w trakcie misji, sekcja 2)
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass
  - **Vasage** — pilot główny: Vasage

**Jednostki wrogie:**
  - **Benthos Cruiser α** — pilot główny: Mucus
  - **Giga Nekton α** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Mucus Gate M** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Mucus Gate S** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×12 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 10 — Operacja: przejęcie Alexa (`DL310_40`)

**Źródło:** `eventP03.EDAT/DL310_40_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Guncannon** — pilot główny: Kai Shiden
  - **Gundam** — pilot główny: Amuro Ray
  - **Gundam Ez8** — pilot główny: Shiro Amada
  - **Gundam Ground Type** — pilot główny: Terry Sanders Jr.
  - **Gundam Ground Type/głowa GM** — pilot główny: Karen Joshua
  - **Guntank** — pilot główny: Hayato Kobayashi
  - **Hover Truck** — pilot główny: Michel Ninorich — piloci wspierający w misji: Eledore Massis
  - **NT-1 Alex** — pilot główny: Christina Mackenzie

**Jednostki wrogie:**
  - **Gelgoog** — pilot główny: Crown
  - **Gelgoog** — pilot główny: Slender
  - **Gelgoog (Char)** — pilot główny: Char Aznable
  - **Kampfer/Bazooka** — pilot główny: Mikhail Kaminsky
  - **Kampfer/High Mobility** — pilot główny: Hardy Steiner
  - **Zaku II Kai** — pilot główny: Andy Strauss
  - **Zaku II Kai** — pilot główny: Bernard Wiseman
  - **Zaku II Kai** — pilot główny: Gabriel Ramirez Garcia
  - **Zaku II Kai** — pilot główny: Żołnierz Zeonu
  - **Zaku II Kai** — pilot główny: Żołnierz Zeonu

### Odcinek 10 — Powstrzymaj atak atomowy (`DL310_50`)

**Źródło:** `eventP03.EDAT/DL310_50_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki wrogie:**
  - **Gattle** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Gattle** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Musai** — pilot główny: Oficer Zeonu
  - **Musai** — pilot główny: Oficer Zeonu
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu

### Odcinek 10 — Kosmiczna twierdza Solomon (`DL310_60`)

**Źródło:** `eventP03.EDAT/DL310_60_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.
**Uwaga o rekordach alternatywnych:** 1 identyfikator `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **G-Fighter** — pilot główny: Sayla Mass — obecny alternatywny rekord Entry ID
  - **Guncannon** — pilot główny: Kai Shiden — obecny alternatywny rekord Entry ID
  - **Gundam** — pilot główny: Amuro Ray — obecny alternatywny rekord Entry ID
  - **Guntank** — pilot główny: Hayato Kobayashi — obecny alternatywny rekord Entry ID
  - **NT-1 Alex** — pilot główny: Christina Mackenzie — obecny alternatywny rekord Entry ID
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Big Zam** — pilot główny: Dozle Zabi
  - **Gwazine** — pilot główny: Conscon
  - **Kampfer/Bazooka** — pilot główny: Żołnierz Zeonu
  - **Kampfer/Bazooka** — pilot główny: Żołnierz Zeonu
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×3 rekordy źródłowe Entry ID
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×3 rekordy źródłowe Entry ID
  - **Zaku II Kai** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zaku II Kai** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID

**Jednostki neutralne / trzeciej strony:**
  - **Mucus Gate S** — pilot główny: Control AI — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 11 — Operacja Odbicie Arki (`DL311_11`)

**Źródło:** `eventP03.EDAT/DL311_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Ingram nr 1** — pilot główny: Noa Izumi
  - **Ingram nr 2** — pilot główny: Isao Ota
  - **Scopedog RSC (Chirico)** — pilot główny: Chirico Cuvie

**Jednostki wrogie:**
  - **Bolt Robo/Long-Range** — pilot główny: Mechabestia — ×4 rekordy źródłowe Entry ID
  - **Bolt Robo/Melee** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Bolt Robo/Standard** — pilot główny: Mechabestia — ×6 rekordów źródłowych Entry ID
  - **Chaldea** — pilot główny: Control AI — ×30 rekordów źródłowych Entry ID
  - **HAL-X10** — pilot główny: Shinohara HOS — ×2 rekordy źródłowe Entry ID
  - **Helldiver** — pilot główny: Control AI — ×10 rekordów źródłowych Entry ID
  - **Type-Zero/Wróg** — pilot główny: Shinohara HOS

### Odcinek 11 — Wrota otwarte w mroku (`DL311_12`)

**Źródło:** `eventP03.EDAT/DL311_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage
  - **Shin Getter-1 (Go)** — pilot główny: Go — piloci wspierający w misji: Kei, Gai

**Jednostki wrogie:**
  - **Bolt Robo/Standard** — pilot główny: Mechabestia — ×4 rekordy źródłowe Entry ID
  - **Chaldea** — pilot główny: Control AI — ×20 rekordów źródłowych Entry ID
  - **Gandoppler** — pilot główny: Mechabestia — ×4 rekordy źródłowe Entry ID
  - **Giga Nekton α** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Mucus Gate M MC** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Shooter** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID

### Odcinek 11 — Leże Imperium Mechanizacji (`DL311_13`)

**Źródło:** `eventP03.EDAT/DL311_13_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Go-Saurer** — pilot główny: Kenichi Minezaki — piloci wspierający w misji: Hiromi Tachibana, Shinobu Asaoka, Taro Shirogane, Yoji Hiyama

**Jednostki wrogie:**
  - **Bolt Robo/Anti-Air** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Bolt Robo/Long-Range** — pilot główny: Mechabestia — ×6 rekordów źródłowych Entry ID
  - **Bolt Robo/Melee** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Bolt Robo/Standard** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Chaldea** — pilot główny: Control AI — ×20 rekordów źródłowych Entry ID
  - **Dark Go-Saurer** — pilot główny: Mechabestia
  - **HAL-X10** — pilot główny: Control AI — ×6 rekordów źródłowych Entry ID
  - **Helldiver** — pilot główny: Control AI — ×6 rekordów źródłowych Entry ID
  - **Moduł kontroli (Mega Castle)** — pilot główny: Mechabestia
  - **Type-Zero/Wróg** — pilot główny: Control AI — ×4 rekordy źródłowe Entry ID

### Odcinek 11 — SV2 i nowe siły (`DL311_20`)

**Źródło:** `eventP03.EDAT/DL311_20_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Griffon/Ally** — pilot główny: Badrinath Harchand
  - **Ingram nr 1** — pilot główny: Noa Izumi
  - **Ingram nr 2** — pilot główny: Isao Ota
  - **Type-Zero** — pilot główny: Kanuka Clancy

**Jednostki wrogie:**
  - **Brocken/Cannon** — pilot główny: Pilot Labora — ×7 rekordów źródłowych Entry ID
  - **Brocken/Działko automatyczne** — pilot główny: Pilot Labora — ×9 rekordów źródłowych Entry ID
  - **Brocken/Melee** — pilot główny: Pilot Labora — ×4 rekordy źródłowe Entry ID
  - **Chaldea** — pilot główny: Control AI — ×12 rekordów źródłowych Entry ID
  - **Kampfer/Bazooka** — pilot główny: Pilot MS
  - **Zaku II Kai** — pilot główny: Pilot MS — ×2 rekordy źródłowe Entry ID

### Odcinek 11 — Operacja: zatrzymać Solar Ray (`DL311_40`)

**Źródło:** `eventP24.EDAT/DL311_40_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Big Zam** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Gattle** — pilot główny: Żołnierz Zeonu
  - **Gattle** — pilot główny: Żołnierz Zeonu
  - **Gelgoog** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Gelgoog** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu
  - **Zanzibar** — pilot główny: Oficer Zeonu

### Odcinek 11 — Puls Zety (`DL311_50`)

**Źródło:** `eventP03.EDAT/DL311_50_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Hyaku Shiki** — pilot główny: Quattro Bajeena
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima
  - **Zeta Gundam** — pilot główny: Kamille Bidan

**Jednostki wrogie:**
  - **Gattle** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Gattle** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Gelgoog** — pilot główny: Żołnierz Zeonu — ×7 rekordów źródłowych Entry ID
  - **Gelgoog** — pilot główny: Żołnierz Zeonu — ×7 rekordów źródłowych Entry ID
  - **Gwazine** — pilot główny: Oficer Zeonu
  - **Kampfer/High Mobility** — pilot główny: Żołnierz Zeonu — ×5 rekordów źródłowych Entry ID
  - **Kampfer/High Mobility** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Musai** — pilot główny: Oficer Zeonu
  - **Musai** — pilot główny: Oficer Zeonu
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×8 rekordów źródłowych Entry ID
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×7 rekordów źródłowych Entry ID
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu — ×3 rekordy źródłowe Entry ID
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu — ×5 rekordów źródłowych Entry ID
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu — ×3 rekordy źródłowe Entry ID
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu — ×3 rekordy źródłowe Entry ID
  - **Zanzibar** — pilot główny: Oficer Zeonu

### Odcinek 12 — Strażnicy kolonii (`DL312_11`)

**Źródło:** `eventP03.EDAT/DL312_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Gundam Exia** — pilot główny: Setsuna F. Seiei
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Brocken/Cannon** — pilot główny: Control AI — ×8 rekordów źródłowych Entry ID
  - **Brocken/Działko automatyczne** — pilot główny: Control AI — ×10 rekordów źródłowych Entry ID
  - **Chaldea** — pilot główny: Control AI — ×10 rekordów źródłowych Entry ID
  - **Dark Go-Saurer** — pilot główny: Mechabestia
  - **Gelgoog** — pilot główny: Control AI — ×4 rekordy źródłowe Entry ID
  - **Kampfer/Bazooka** — pilot główny: Control AI — ×2 rekordy źródłowe Entry ID
  - **Zaku II Kai** — pilot główny: Control AI — ×8 rekordów źródłowych Entry ID

### Odcinek 12 — Operacja oczyszczania (`DL312_12`)

**Źródło:** `eventP03.EDAT/DL312_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass
  - **Mucus Gate S** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Wing Gundam Zero** — pilot główny: Heero Yuy

**Jednostki wrogie:**
  - **Bolt Robo/Anti-Air** — pilot główny: Mechabestia — ×4 rekordy źródłowe Entry ID
  - **Bolt Robo/Melee** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Bolt Robo/Standard** — pilot główny: Mechabestia — ×5 rekordów źródłowych Entry ID
  - **Brocken/Cannon** — pilot główny: Control AI — ×6 rekordów źródłowych Entry ID
  - **Brocken/Działko automatyczne** — pilot główny: Control AI — ×8 rekordów źródłowych Entry ID
  - **Chaldea** — pilot główny: Control AI — ×16 rekordów źródłowych Entry ID
  - **Dark Go-Saurer** — pilot główny: Mechabestia
  - **Gandoppler** — pilot główny: Mechabestia — ×9 rekordów źródłowych Entry ID
  - **Gelgoog** — pilot główny: Control AI — ×5 rekordów źródłowych Entry ID
  - **Rick Dom** — pilot główny: Control AI — ×5 rekordów źródłowych Entry ID

### Odcinek 12 — Gniazdo Mucus w pasie asteroid (`DL312_20`)

**Źródło:** `eventP03.EDAT/DL312_20_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Mucus Gate S** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID

### Odcinek 12 — Zamach na Rudolpha (`DL312_40`)

**Źródło:** `eventP03.EDAT/DL312_40_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Red Horn (Rosso Ally)** — pilot główny: Rosso
  - **Redler (Viola Ally)** — pilot główny: Viola

**Jednostki wrogie:**
  - **Command Wolf/White** — pilot główny: Pilot Zoida — ×3 rekordy źródłowe Entry ID
  - **Dark Horn** — pilot główny: Żołnierz Imperium Guylos
  - **Dark Horn** — pilot główny: Żołnierz Imperium Guylos

### Odcinek 12 — Odrodzona bestia (`DL312_50`)

**Źródło:** `eventP03.EDAT/DL312_50_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 5 identyfikatorów `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Command Wolf/Black/Upgraded** — pilot główny: Irvine
  - **Gustav/Moonbay Special** — pilot główny: Moonbay
  - **Mucus Gate S** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Red Horn (Rosso Ally)** — pilot główny: Rosso
  - **Redler (Viola Ally)** — pilot główny: Viola — obecny alternatywny rekord Entry ID
  - **Redler (Viola)** — pilot główny: Viola — obecny alternatywny rekord Entry ID
  - **Shield Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette

**Jednostki wrogie:**
  - **Dark Horn** — pilot główny: Zoid Core — ×6 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID
  - **Geno Breaker** — pilot główny: Raven
  - **Molga** — pilot główny: Zoid Core — ×8 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID
  - **Redler** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID

### Odcinek 12 — Waleczny! Geno Breaker (`DL312_60`)

**Źródło:** `eventP03.EDAT/DL312_60_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Blade Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette
  - **Shield Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Dark Horn** — pilot główny: Zoid Core — ×7 rekordów źródłowych Entry ID
  - **Geno Breaker** — pilot główny: Raven
  - **Gun Sniper** — pilot główny: Zoid Core — ×5 rekordów źródłowych Entry ID
  - **Molga** — pilot główny: Zoid Core — ×15 rekordów źródłowych Entry ID
  - **Redler** — pilot główny: Zoid Core — ×12 rekordów źródłowych Entry ID

### Odcinek 13 — Powrót młodego króla (`DL313_11`)

**Źródło:** `eventP03.EDAT/DL313_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Mucus Gate S** — pilot główny: Brak przypisanego klucza pilota w Entry — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki sojusznicze (NPC):**
  - **Iron Kong** — pilot główny: Oficer Imperium Guylos
  - **Iron Kong** — pilot główny: Oficer Imperium Guylos
  - **Molga** — pilot główny: Żołnierz Imperium Guylos — ×4 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Żołnierz Imperium Guylos — ×4 rekordy źródłowe Entry ID

**Jednostki wrogie:**
  - **Dark Horn** — pilot główny: Oficer Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Dark Horn** — pilot główny: Żołnierz Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Dark Horn** — pilot główny: Żołnierz Imperium Guylos
  - **Death Saurer/Replica** — pilot główny: Gunther Prozen
  - **Iron Kong** — pilot główny: Oficer Imperium Guylos
  - **Iron Kong** — pilot główny: Oficer Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Żołnierz Imperium Guylos — ×8 rekordów źródłowych Entry ID
  - **Molga** — pilot główny: Żołnierz Imperium Guylos — ×6 rekordów źródłowych Entry ID
  - **Redler** — pilot główny: Żołnierz Imperium Guylos — ×5 rekordów źródłowych Entry ID
  - **Redler** — pilot główny: Żołnierz Imperium Guylos — ×5 rekordów źródłowych Entry ID
  - **Whale King** — pilot główny: Oficer Imperium Guylos

### Odcinek 13 — Stolica imperium w ogniu (`DL313_12`)

**Źródło:** `eventP03.EDAT/DL313_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Blade Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette
  - **Command Wolf/Black/Upgraded** — pilot główny: Irvine
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage
  - **Gawain** — pilot główny: Zero — piloci wspierający w misji: C.C.
  - **Gustav/Moonbay Special** — pilot główny: Moonbay
  - **Lancelot/Ally** — pilot główny: Suzaku Kururugi
  - **Mucus Gate S** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem

**Jednostki wrogie:**
  - **Dark Horn** — pilot główny: Oficer Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Dark Horn** — pilot główny: Żołnierz Imperium Guylos
  - **Dark Horn** — pilot główny: Żołnierz Imperium Guylos
  - **Death Saurer/Replica** — pilot główny: Gunther Prozen
  - **Iron Kong** — pilot główny: Oficer Imperium Guylos — ×3 rekordy źródłowe Entry ID
  - **Iron Kong** — pilot główny: Oficer Imperium Guylos
  - **Molga** — pilot główny: Żołnierz Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Żołnierz Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Żołnierz Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Żołnierz Imperium Guylos — ×2 rekordy źródłowe Entry ID

### Odcinek 13 — Święty wojownik upadłego królestwa (`DL313_25`)

**Źródło:** `eventP03.EDAT/DL313_25_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Dunbine** — pilot główny: Show Zama — piloci wspierający w misji: Chum Huau

**Jednostki wrogie:**
  - **Monskar Medessa** — pilot główny: Monskar
  - **Monskar Neppoon** — pilot główny: Monskar
  - **Nekton Creek** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Zwarth** — pilot główny: Black Knight

### Odcinek 13 — Koordynator (`DL313_40`)

**Źródło:** `eventP03.EDAT/DL313_40_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.
**Uwaga o rekordach alternatywnych:** 2 identyfikatory `Entry ID` posiadają więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Infinite Justice Gundam** — pilot główny: Athrun Zala
  - **Nekton Mine** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Strike Freedom Gundam** — pilot główny: Kira Yamato

**Jednostki wrogie:**
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID
  - **Endra** — pilot główny: Oficer Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu
  - **Musai** — pilot główny: Oficer Neo Zeonu
  - **Rick Dom** — pilot główny: Żołnierz Neo Zeonu
  - **Rick Dom** — pilot główny: Żołnierz Neo Zeonu
  - **Zaku II Kai** — pilot główny: Żołnierz Neo Zeonu
  - **Zaku II Kai** — pilot główny: Żołnierz Neo Zeonu
  - **Zaku III (Rakan)** — pilot główny: Rakan Dahkaran

### Odcinek 13 — Leccee Mind (`DL313_55`)

**Źródło:** `eventP04.EDAT/DL313_55_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.
**Uwaga o rekordach alternatywnych:** 2 identyfikatory `Entry ID` posiadają więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **D-Sserd** — pilot główny: Fannaria Amm
  - **L-Gaim** — pilot główny: Daba Myroad — piloci wspierający w misji: Lilis Faw
  - **Novel D-Sserd** — pilot główny: Gaw Ha Leccee
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×2 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular
  - **Bat-Shu/Strong** — pilot główny: Gavlet Gablae
  - **Braver** — pilot główny: Żołnierz Gradosu — ×4 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×4 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID

### Odcinek 13 — Przejmij skład broni jądrowej (`DL313_66`)

**Źródło:** `eventP04.EDAT/DL313_66_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Gundam Ez8** — pilot główny: Shiro Amada
  - **Gundam Ground Type** — pilot główny: Terry Sanders Jr.
  - **Gundam Ground Type/głowa GM** — pilot główny: Karen Joshua
  - **Hover Truck** — pilot główny: Michel Ninorich — piloci wspierający w misji: Eledore Massis
  - **Hyaku Shiki** — pilot główny: Quattro Bajeena
  - **Zeta Gundam** — pilot główny: Kamille Bidan

**Jednostki wrogie:**
  - **Gelgoog** — pilot główny: Pilot MS — ×4 rekordy źródłowe Entry ID
  - **Zaku II Kai** — pilot główny: Pilot MS — ×2 rekordy źródłowe Entry ID
  - **Zaku II/Bazooka** — pilot główny: Pilot MS — ×8 rekordów źródłowych Entry ID
  - **Zaku II/Karabin maszynowy** — pilot główny: Pilot MS — ×8 rekordów źródłowych Entry ID

### Odcinek 13 — Sen lelka (`DL313_70`)

**Źródło:** `eventP25.EDAT/DL313_70_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Iron Kong Mk-II** — pilot główny: Karl Lichten Schubaltz
  - **Murasame Liger** — pilot główny: Ruuji Familon
  - **Red Horn (Rosso Ally)** — pilot główny: Rosso
  - **Redler (Viola Ally)** — pilot główny: Viola

**Jednostki wrogie:**
  - **Command Wolf/Khaki** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID
  - **Command Wolf/Khaki** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID
  - **Dark Horn** — pilot główny: Pilot Zoida
  - **Dark Horn** — pilot główny: Pilot Zoida
  - **Gun Sniper** — pilot główny: Pilot Zoida
  - **Gun Sniper** — pilot główny: Pilot Zoida
  - **Gun Sniper/WW** — pilot główny: Pilot Zoida
  - **Gun Sniper/WW** — pilot główny: Pilot Zoida
  - **Iron Kong** — pilot główny: Pilot Zoida
  - **Molga** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID
  - **Mucus Gate S** — pilot główny: Control AI — cel/obiekt skryptowy; nie jest pilotowanym mechem

**Jednostki neutralne / trzeciej strony:**
  - **Iron Kong Mk-II** — pilot główny: Karl Lichten Schubaltz
  - **Murasame Liger** — pilot główny: Ruuji Familon
  - **Red Horn (Rosso)** — pilot główny: Rosso
  - **Redler (Viola Ally)** — pilot główny: Viola

### Odcinek 14 — War Cloud (`DL414_11`)

**Źródło:** `eventP04.EDAT/DL414_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Dunbine** — pilot główny: Show Zama — piloci wspierający w misji: Chum Huau
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Auge** — pilot główny: Nei Moh Han
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×4 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×4 rekordy źródłowe Entry ID
  - **Bat-Shu/Strong** — pilot główny: Hekeler Mauzer
  - **Braver** — pilot główny: Żołnierz Gradosu — ×5 rekordów źródłowych Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×6 rekordów źródłowych Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×6 rekordów źródłowych Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×4 rekordy źródłowe Entry ID
  - **Sarge Aupus (Nei)** — pilot główny: Antoon Randow

### Odcinek 14 — Against (`DL414_12`)

**Źródło:** `eventP04.EDAT/DL414_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 1 identyfikator `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **D-Sserd** — pilot główny: Fannaria Amm — obecny alternatywny rekord Entry ID
  - **L-Gaim** — pilot główny: Daba Myroad — piloci wspierający w misji: Lilis Faw — obecny alternatywny rekord Entry ID
  - **Novel D-Sserd** — pilot główny: Gaw Ha Leccee — obecny alternatywny rekord Entry ID
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×4 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×2 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×5 rekordów źródłowych Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×5 rekordów źródłowych Entry ID
  - **Directional Mine** — pilot główny: Control AI — ×6 rekordów źródłowych Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×5 rekordów źródłowych Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×5 rekordów źródłowych Entry ID

### Odcinek 14 — Planet Bomber (`DL414_13`)

**Źródło:** `eventP04.EDAT/DL414_13_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 2 identyfikatory `Entry ID` posiadają więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **D-Sserd** — pilot główny: Fannaria Amm
  - **L-Gaim** — pilot główny: Daba Myroad — piloci wspierający w misji: Lilis Faw
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass
  - **Mucus Gate S** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Novel D-Sserd** — pilot główny: Gaw Ha Leccee

**Jednostki wrogie:**
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu
  - **Bat-Shu** — pilot główny: Hatchia Motchia
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×5 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×5 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID
  - **Bat-Shu/Strong** — pilot główny: Gavlet Gablae
  - **Braver** — pilot główny: Żołnierz Gradosu — ×6 rekordów źródłowych Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×6 rekordów źródłowych Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **Slender Skala** — pilot główny: Oficer armii Posaydala

### Odcinek 14 — Guardian Force (`DL414_25`)

**Źródło:** `eventP04.EDAT/DL414_25_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Blade Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette
  - **Dibison** — pilot główny: Thomas Richard Schubaltz
  - **Gustav/Moonbay Special** — pilot główny: Moonbay
  - **Lightning Saix** — pilot główny: Irvine

**Jednostki wrogie:**
  - **Gun Sniper** — pilot główny: Żołnierz Imperium Guylos
  - **Gun Sniper** — pilot główny: Żołnierz Imperium Guylos
  - **Iron Kong SS** — pilot główny: Karl Lichten Schubaltz
  - **Molga** — pilot główny: Żołnierz Imperium Guylos
  - **Molga** — pilot główny: Żołnierz Imperium Guylos
  - **Red Horn (Rosso)** — pilot główny: Rosso
  - **Redler** — pilot główny: Żołnierz Imperium Guylos
  - **Redler** — pilot główny: Żołnierz Imperium Guylos
  - **Redler (Viola)** — pilot główny: Viola

### Odcinek 14 — Ryoma powraca (`DL414_35`)

**Źródło:** `eventP04.EDAT/DL414_35_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 1 identyfikator `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage — obecny alternatywny rekord Entry ID
  - **Gurren Lagann (Simon)** — pilot główny: Simon — piloci wspierający w misji: Kamina, Yoko, Boota — obecny alternatywny rekord Entry ID
  - **Shin Getter-1 (Go)** — pilot główny: Go — piloci wspierający w misji: Kei, Gai — obecny alternatywny rekord Entry ID
  - **Shin Getter-1 (Ryoma)** — pilot główny: Ryoma Nagare — piloci wspierający w misji: Hayato Jin, Benkei Kuruma
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Benthos Cruiser α** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Enkidu** — pilot główny: Viral
  - **Invader/Starfish** — pilot główny: Invader — ×32 rekordy źródłowe Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID

### Odcinek 14 — Operacja: transport ZZ Gundama (`DL414_45`)

**Źródło:** `eventP04.EDAT/DL414_45_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima
  - **Zeta Gundam** — pilot główny: Kamille Bidan

**Jednostki wrogie:**
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×6 rekordów źródłowych Entry ID
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×4 rekordy źródłowe Entry ID
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Qubeley Mk-II (Ple)** — pilot główny: Elpeo Ple

### Odcinek 14 — Chłopiec z Shangri-La (`DL414_50`)

**Źródło:** `eventP04.EDAT/DL414_50_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Gundam** — pilot główny: Amuro Ray
  - **Hyaku Shiki** — pilot główny: Quattro Bajeena
  - **Zeta Gundam** — pilot główny: Kamille Bidan
  - **ZZ Gundam** — pilot główny: Judau Ashta — zmiana strony w trakcie misji: wroga / agresywna frakcja

**Jednostki sojusznicze (NPC):**
  - **Brocken/Działko automatyczne** — pilot główny: Żołnierz Federacji
  - **Brocken/Melee** — pilot główny: Żołnierz Federacji

**Jednostki wrogie:**
  - **Dom** — pilot główny: Żołnierz Neo Zeonu
  - **Dom** — pilot główny: Żołnierz Neo Zeonu
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×4 rekordy źródłowe Entry ID
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×4 rekordy źródłowe Entry ID
  - **Qubeley Mk-II (Ple)** — pilot główny: Elpeo Ple
  - **Zaku III (Rakan)** — pilot główny: Rakan Dahkaran

### Odcinek 15 — Powstanie Neo Zeonu (`DL415_11`)

**Źródło:** `eventP04.EDAT/DL415_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×4 rekordy źródłowe Entry ID
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Endra** — pilot główny: Oficer Neo Zeonu
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×5 rekordów źródłowych Entry ID
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×4 rekordy źródłowe Entry ID
  - **Kampfer/Bazooka** — pilot główny: Żołnierz Neo Zeonu
  - **Kampfer/Bazooka** — pilot główny: Żołnierz Neo Zeonu
  - **Qubeley** — pilot główny: Haman Karn
  - **Sadalahn** — pilot główny: Oficer Neo Zeonu
  - **Zaku II Kai** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Zaku II Kai** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID

### Odcinek 15 — Uderzenie Axis (`DL415_12`)

**Źródło:** `eventP04.EDAT/DL415_12_Entry.dat`
**Warunki misji:**
> W połowie tej misji zmienia się okręt-matka.
> Najpierw "Turner", potem "White Base".
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Turner** — pilot główny: Mirawoo Kyao
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Endra** — pilot główny: Oficer Neo Zeonu
  - **Endra** — pilot główny: Rakan Dahkaran
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×6 rekordów źródłowych Entry ID
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×5 rekordów źródłowych Entry ID
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu — ×4 rekordy źródłowe Entry ID
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu — ×4 rekordy źródłowe Entry ID
  - **Gelgoog** — pilot główny: Żołnierz Neo Zeonu
  - **Gelgoog** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Qubeley Mk-II (Ple Two)** — pilot główny: Ple Two
  - **Rick Dom** — pilot główny: Żołnierz Neo Zeonu — ×4 rekordy źródłowe Entry ID
  - **Rick Dom** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zaku III (Rakan)** — pilot główny: Rakan Dahkaran

### Odcinek 15 — Bój na palących piaskach (`DL415_20`)

**Źródło:** `eventP04.EDAT/DL415_20_Entry.dat`
**Warunki misji:**
> W tej misji "NT-1 Alex" musi wyruszyć jako GR,
> a "Zaku II Kai" nie może wziąć udziału.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Directional Mine** — pilot główny: Control AI — ×12 rekordów źródłowych Entry ID
  - **Dom** — pilot główny: Żołnierz Zeonu — ×5 rekordów źródłowych Entry ID
  - **Dom** — pilot główny: Żołnierz Zeonu — ×5 rekordów źródłowych Entry ID
  - **Dopp** — pilot główny: Żołnierz Zeonu
  - **Dopp** — pilot główny: Żołnierz Zeonu
  - **Dreissen** — pilot główny: Desert Rommel
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Gouf** — pilot główny: Acous
  - **Gouf** — pilot główny: Cozun Graham
  - **Gouf (Ramba Ral)** — pilot główny: Ramba Ral
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Zanzibar** — pilot główny: Crowley Hamon

### Odcinek 15 — Skrzydła zwane wolnością (`DL415_30`)

**Źródło:** `eventP04.EDAT/DL415_30_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Strike Freedom Gundam** — pilot główny: Kira Yamato
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Bigro** — pilot główny: Tokwan
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Endra** — pilot główny: Oficer Neo Zeonu
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Qubeley Mk-II (Ple Two)** — pilot główny: Ple Two
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×3 rekordy źródłowe Entry ID
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×3 rekordy źródłowe Entry ID
  - **Zaku III (Rakan)** — pilot główny: Rakan Dahkaran
  - **Zanzibar** — pilot główny: M'Quve

### Odcinek 15 — Destiny (`DL415_40`)

**Źródło:** `eventP04.EDAT/DL415_40_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Destiny Gundam** — pilot główny: Shinn Asuka
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage
  - **Infinite Justice Gundam** — pilot główny: Athrun Zala
  - **Shin Getter-1 (Go)** — pilot główny: Go — piloci wspierający w misji: Kei, Gai
  - **Strike Freedom Gundam** — pilot główny: Kira Yamato

**Jednostki wrogie:**
  - **Invader/Air** — pilot główny: Invader — ×6 rekordów źródłowych Entry ID
  - **Invader/Ground** — pilot główny: Invader — ×8 rekordów źródłowych Entry ID
  - **Metal Beast/Muszla** — pilot główny: Invader
  - **Metal Beast/Rakieta** — pilot główny: Invader — ×4 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 15 — Powrót armii Goburikiego (`DL415_60`)

**Źródło:** `eventP26.EDAT/DL415_60_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 1 identyfikator `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Dunbine** — pilot główny: Show Zama — piloci wspierający w misji: Chum Huau — obecny alternatywny rekord Entry ID
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage — obecny alternatywny rekord Entry ID
  - **Hulk Gunship Axe Bomber** — pilot główny: Cocoa Arara — piloci wspierający w misji: Milk Arara, Cafe au Lait Arara — obecny alternatywny rekord Entry ID
  - **King Squasher** — pilot główny: Hero Lamuness — piloci wspierający w misji: Tama-Q — obecny alternatywny rekord Entry ID
  - **Ryu Knight Zephyr/Later** — pilot główny: Adeu Waltham
  - **Ryu Mage Magidora** — pilot główny: Paffy Pafuricia — piloci wspierający w misji: Hagu Hagu
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Giga Nekton α** — pilot główny: Mucus
  - **Monskar Medessa** — pilot główny: Monskar — ×6 rekordów źródłowych Entry ID
  - **Monskar Neppoon** — pilot główny: Monskar — ×6 rekordów źródłowych Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Shooter** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Zwarth** — pilot główny: Black Knight

### Odcinek 15 — Pragnący wskrzesić demonicznego boga (`DL415_70`)

**Źródło:** `eventP04.EDAT/DL415_70_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Monskar Medessa** — pilot główny: Monskar — ×4 rekordy źródłowe Entry ID
  - **Monskar Neppoon** — pilot główny: Monskar — ×4 rekordy źródłowe Entry ID
  - **Żołnierz Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka — ×7 rekordów źródłowych Entry ID
  - **Żołnierz Mrocznego Smoka/Lot** — pilot główny: Żołnierz Mrocznego Smoka — ×7 rekordów źródłowych Entry ID
  - **Żołnierz Mrocznego Smoka/Snajper** — pilot główny: Żołnierz Mrocznego Smoka — ×5 rekordów źródłowych Entry ID

### Odcinek 16 — Atak armii Goburikiego (`DL416_11`)

**Źródło:** `eventP04.EDAT/DL416_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 1 identyfikator `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Hulk Gunship Axe Bomber** — pilot główny: Cocoa Arara — piloci wspierający w misji: Milk Arara, Cafe au Lait Arara — obecny alternatywny rekord Entry ID
  - **King Squasher** — pilot główny: Hero Lamuness — piloci wspierający w misji: Tama-Q — obecny alternatywny rekord Entry ID
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Monskar Medessa** — pilot główny: Monskar — ×2 rekordy źródłowe Entry ID
  - **Monskar Neppoon** — pilot główny: Monskar — ×2 rekordy źródłowe Entry ID
  - **Okręt eskorty Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka — ×2 rekordy źródłowe Entry ID
  - **Queen Cideron** — pilot główny: Da Cider
  - **Żołnierz Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka — ×8 rekordów źródłowych Entry ID
  - **Żołnierz Mrocznego Smoka/Lot** — pilot główny: Żołnierz Mrocznego Smoka — ×10 rekordów źródłowych Entry ID
  - **Żołnierz Mrocznego Smoka/Snajper** — pilot główny: Żołnierz Mrocznego Smoka — ×7 rekordów źródłowych Entry ID

### Odcinek 16 — Szalejąca moc aury (`DL416_12`)

**Źródło:** `eventP04.EDAT/DL416_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Benthos Cruiser α** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Monskar Medessa** — pilot główny: Monskar — ×4 rekordy źródłowe Entry ID
  - **Monskar Neppoon** — pilot główny: Monskar — ×4 rekordy źródłowe Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Zwarth** — pilot główny: Black Knight
  - **Zwarth/Hyper** — pilot główny: Black Knight

### Odcinek 16 — Dzień wyruszenia w drogę (`DL416_30`)

**Źródło:** `eventP04.EDAT/DL416_30_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 1 identyfikator `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Blade Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette
  - **Dibison** — pilot główny: Thomas Richard Schubaltz — obecny alternatywny rekord Entry ID
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage — obecny alternatywny rekord Entry ID
  - **Lightning Saix** — pilot główny: Irvine — obecny alternatywny rekord Entry ID
  - **Murasame Liger** — pilot główny: Ruuji Familon
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Nekton Assault** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Shooter** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID

### Odcinek 16 — Front pod Galeade (`DL416_45`)

**Źródło:** `eventP04.EDAT/DL416_45_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Scopedog TC/ISS (Barcoff)** — pilot główny: Nor Barcoff
  - **Scopedog TC/ISS (Chirico)** — pilot główny: Chirico Cuvie
  - **Scopedog TC/ISS (Godan)** — pilot główny: Gary Godan
  - **Scopedog TC/ISS (Kochak)** — pilot główny: Dare Kochak
  - **Scopedog TC/ISS (Zaki)** — pilot główny: Gerenborash Droka Zaki

**Jednostki wrogie:**
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×6 rekordów źródłowych Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×6 rekordów źródłowych Entry ID

### Odcinek 16 — Operacja: ratunek dla Galeade (`DL416_55`)

**Źródło:** `eventP04.EDAT/DL416_55_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Scopedog RSC (Byman)** — pilot główny: Byman Hagard
  - **Scopedog RSC (Gregore)** — pilot główny: Gregore Garosh
  - **Scopedog RSC (Murza)** — pilot główny: Murza Melym
  - **Scopedog TC/ISS (Barcoff)** — pilot główny: Nor Barcoff
  - **Scopedog TC/ISS (Chirico)** — pilot główny: Chirico Cuvie
  - **Scopedog TC/ISS (Godan)** — pilot główny: Gary Godan
  - **Scopedog TC/ISS (Kochak)** — pilot główny: Dare Kochak
  - **Scopedog TC/ISS (Zaki)** — pilot główny: Gerenborash Droka Zaki
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×4 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×4 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×10 rekordów źródłowych Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×4 rekordy źródłowe Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×29 rekordów źródłowych Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×29 rekordów źródłowych Entry ID
  - **Lądowy pancernik Balarant** — pilot główny: Oficer Balarantu

### Odcinek 17 — Szturm na Monad (`DL417_11`)

**Źródło:** `eventP04.EDAT/DL417_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×10 rekordów źródłowych Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×8 rekordów źródłowych Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×10 rekordów źródłowych Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×8 rekordów źródłowych Entry ID
  - **Pancernik kosmiczny klasy Lesrion** — pilot główny: Oficer Balarantu — ×2 rekordy źródłowe Entry ID

**Jednostki neutralne / trzeciej strony:**
  - **Turner** — pilot główny: Mirawoo Kyao
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

### Odcinek 17 — Anomalny ocalały (`DL417_12`)

**Źródło:** `eventP04.EDAT/DL417_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 1 identyfikator `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Scopedog TC/ISS (Barcoff)** — pilot główny: Nor Barcoff
  - **Scopedog TC/ISS (Chirico)** — pilot główny: Chirico Cuvie
  - **Scopedog TC/ISS (Godan)** — pilot główny: Gary Godan
  - **Scopedog TC/ISS (Kochak)** — pilot główny: Dare Kochak — obecny alternatywny rekord Entry ID
  - **Scopedog TC/ISS (Zaki)** — pilot główny: Gerenborash Droka Zaki
  - **Turner** — pilot główny: Mirawoo Kyao — obecny alternatywny rekord Entry ID

**Jednostki wrogie:**
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×18 rekordów źródłowych Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×17 rekordów źródłowych Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID

### Odcinek 17 — Ratunek (`DL417_13`)

**Źródło:** `eventP04.EDAT/DL417_13_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.
**Uwaga o rekordach alternatywnych:** 1 identyfikator `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Dark Knight Steru/Dark Dragon Form** — pilot główny: Galden
  - **Enhanced Layzner** — pilot główny: Albatro Null Eiji Asuka
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage
  - **Lancelot/Ally** — pilot główny: Suzaku Kururugi
  - **Shin Getter-1 (Ryoma)** — pilot główny: Ryoma Nagare — piloci wspierający w misji: Hayato Jin, Benkei Kuruma
  - **Turner** — pilot główny: Mirawoo Kyao
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Braver** — pilot główny: Żołnierz Gradosu
  - **Braver** — pilot główny: Żołnierz Gradosu
  - **Daljan** — pilot główny: Gosterro — ×2 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×10 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×8 rekordów źródłowych Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×5 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID

### Odcinek 17 — Planeta Pieczęci (`DL417_30`)

**Źródło:** `eventP04.EDAT/DL417_30_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Enhanced Layzner** — pilot główny: Albatro Null Eiji Asuka
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×3 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×3 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×8 rekordów źródłowych Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×8 rekordów źródłowych Entry ID
  - **Directional Mine** — pilot główny: Control AI — ×4 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×5 rekordów źródłowych Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×5 rekordów źródłowych Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×4 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×4 rekordy źródłowe Entry ID
  - **Nowy gigantyczny lotniskowiec Grados** — pilot główny: Oficer Gradosu

### Odcinek 17 — Obrona bramy warp (`DL417_40`)

**Źródło:** `eventP05.EDAT/DL417_40_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage
  - **Ingram nr 1** — pilot główny: Noa Izumi
  - **Scopedog RSC (Chirico)** — pilot główny: Chirico Cuvie
  - **Scopedog TC/ISS (Barcoff)** — pilot główny: Nor Barcoff

**Jednostki wrogie:**
  - **Braver** — pilot główny: Żołnierz Gradosu — ×3 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×3 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×7 rekordów źródłowych Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×7 rekordów źródłowych Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID

### Odcinek 17 — Ewoluujące komórki DG (`DL417_50`)

**Źródło:** `eventP05.EDAT/DL417_50_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 1 identyfikator `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Death Army** — pilot główny: DG Cells — ×6 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID
  - **Death Bird** — pilot główny: DG Cells — ×6 rekordów źródłowych Entry ID
  - **Gundam Head** — pilot główny: DG Cells
  - **Mucus Gate S DG** — pilot główny: Mucus — obecny alternatywny rekord Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Shooter** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID

### Odcinek 17 — Tragedia rabusiów (`DL417_70`)

**Źródło:** `eventP27.EDAT/DL417_70_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Blade Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette
  - **Gun Sniper (Naomi)** — pilot główny: Naomi Fluegel
  - **Gun Sniper/LS** — pilot główny: Leena Toros
  - **Iron Kong Mk-II** — pilot główny: Karl Lichten Schubaltz
  - **Lancelot/Ally** — pilot główny: Suzaku Kururugi
  - **Murasame Liger** — pilot główny: Ruuji Familon

**Jednostki wrogie:**
  - **Command Wolf/Khaki** — pilot główny: Pilot Zoida — ×3 rekordy źródłowe Entry ID
  - **Command Wolf/Khaki** — pilot główny: Pilot Zoida — ×4 rekordy źródłowe Entry ID
  - **Directional Mine** — pilot główny: Control AI — ×7 rekordów źródłowych Entry ID
  - **Gun Sniper** — pilot główny: Pilot Zoida
  - **Gun Sniper** — pilot główny: Pilot Zoida
  - **Gun Sniper/WW** — pilot główny: Pilot Zoida — ×4 rekordy źródłowe Entry ID
  - **Gun Sniper/WW** — pilot główny: Pilot Zoida — ×3 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Pilot Zoida — ×3 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Pilot Zoida — ×4 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Pilot Zoida — ×4 rekordy źródłowe Entry ID
  - **Whale King** — pilot główny: Pilot Zoida
  - **Wieżyczka uniwersalna** — pilot główny: Control AI — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 18 — Preludium wyzwolenia (`DL518_11`)

**Źródło:** `eventP05.EDAT/DL518_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×4 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×4 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×14 rekordów źródłowych Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×14 rekordów źródłowych Entry ID
  - **Directional Mine** — pilot główny: Control AI — ×10 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Nowy gigantyczny lotniskowiec Grados** — pilot główny: Oficer Gradosu — ×3 rekordy źródłowe Entry ID
  - **Ray** — pilot główny: Oficer armii Posaydala

**Jednostki neutralne / trzeciej strony:**
  - **Mucus Gate S** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 18 — Wyzwanie Le Caina (`DL518_12`)

**Źródło:** `eventP05.EDAT/DL518_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Enhanced Layzner** — pilot główny: Albatro Null Eiji Asuka
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×3 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×3 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×6 rekordów źródłowych Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×6 rekordów źródłowych Entry ID
  - **Daljan** — pilot główny: Gosterro
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu
  - **Zakarl** — pilot główny: Le Cain

### Odcinek 18 — Dolina pożądania (`DL518_20`)

**Źródło:** `eventP05.EDAT/DL518_20_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Enhanced Layzner** — pilot główny: Albatro Null Eiji Asuka

**Jednostki wrogie:**
  - **Braver** — pilot główny: Żołnierz Gradosu — ×5 rekordów źródłowych Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×5 rekordów źródłowych Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×5 rekordów źródłowych Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×5 rekordów źródłowych Entry ID

### Odcinek 18 — Asteroida Lido (`DL518_35`)

**Źródło:** `eventP05.EDAT/DL518_35_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
> "Scopedog" pojawia się jako sojuszniczy NPC.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.
**Uwaga o rekordach alternatywnych:** 1 identyfikator `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Scopedog RSC (Chirico)** — pilot główny: Chirico Cuvie

**Jednostki sojusznicze (NPC):**
  - **Scopedog** — pilot główny: Żołnierz Gilgameshu — ×2 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID
  - **Scopedog** — pilot główny: Żołnierz Gilgameshu — obecny alternatywny rekord Entry ID
  - **Scopedog/M** — pilot główny: Żołnierz Gilgameshu

**Jednostki wrogie:**
  - **Scopedog** — pilot główny: Żołnierz Gilgameshu — ×4 rekordy źródłowe Entry ID
  - **Scopedog** — pilot główny: Żołnierz Gilgameshu — ×2 rekordy źródłowe Entry ID

### Odcinek 18 — Uoodo (`DL518_40`)

**Źródło:** `eventP05.EDAT/DL518_40_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Berserga WP** — pilot główny: Ru Shako
  - **Scopedog/Chirico Special** — pilot główny: Chirico Cuvie

**Jednostki sojusznicze (NPC):**
  - **Scopedog** — pilot główny: Żołnierz Gilgameshu — ×3 rekordy źródłowe Entry ID
  - **Scopedog** — pilot główny: Żołnierz Gilgameshu — ×3 rekordy źródłowe Entry ID
  - **Scopedog/M** — pilot główny: Żołnierz Gilgameshu — ×2 rekordy źródłowe Entry ID
  - **Scopedog/M** — pilot główny: Żołnierz Gilgameshu — ×2 rekordy źródłowe Entry ID

**Jednostki wrogie:**
  - **Scopedog** — pilot główny: Pilot AT — ×10 rekordów źródłowych Entry ID
  - **Scopedog/M** — pilot główny: Pilot AT — ×4 rekordy źródłowe Entry ID

**Jednostki neutralne / trzeciej strony:**
  - **Mucus Gate S** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 18 — Ucieczka (`DL518_50`)

**Źródło:** `eventP05.EDAT/DL518_50_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **AT Fly** — pilot główny: Vanilla Vartla
  - **Berserga WP** — pilot główny: Ru Shako
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage
  - **God Gundam** — pilot główny: Domon Kasshu
  - **Scopedog/Chirico Special** — pilot główny: Chirico Cuvie
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki sojusznicze (NPC):**
  - **Scopedog** — pilot główny: Żołnierz Gilgameshu — ×2 rekordy źródłowe Entry ID
  - **Scopedog/M** — pilot główny: Żołnierz Gilgameshu — ×2 rekordy źródłowe Entry ID

**Jednostki wrogie:**
  - **Pancernik kosmiczny klasy Giga** — pilot główny: Oficer Gilgameshu
  - **Scopedog** — pilot główny: Żołnierz Gilgameshu — ×27 rekordów źródłowych Entry ID
  - **Scopedog/M** — pilot główny: Żołnierz Gilgameshu — ×18 rekordów źródłowych Entry ID

### Odcinek 19 — Przełamanie obrony Axis (`DL519_11`)

**Źródło:** `eventP05.EDAT/DL519_11_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Bigro** — pilot główny: Tokwan
  - **Directional Mine** — pilot główny: Control AI — ×7 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Endra** — pilot główny: Oficer Neo Zeonu
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu
  - **Gelgoog** — pilot główny: Żołnierz Zeonu
  - **Gelgoog** — pilot główny: Żołnierz Zeonu
  - **Gelgoog** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Zanzibar** — pilot główny: Garma Zabi

### Odcinek 19 — Szturmowy desant na Axis (`DL519_12`)

**Źródło:** `eventP05.EDAT/DL519_12_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Gundam Ez8** — pilot główny: Shiro Amada
  - **Gundam Ground Type** — pilot główny: Terry Sanders Jr.
  - **Gundam Ground Type/głowa GM** — pilot główny: Karen Joshua
  - **Hover Truck** — pilot główny: Michel Ninorich — piloci wspierający w misji: Eledore Massis

**Jednostki wrogie:**
  - **Directional Mine** — pilot główny: Control AI — ×8 rekordów źródłowych Entry ID
  - **Dom (Black Tri-Stars)** — pilot główny: Gaia
  - **Dom (Black Tri-Stars)** — pilot główny: Mash
  - **Dom (Black Tri-Stars)** — pilot główny: Ortega
  - **Dreissen** — pilot główny: Desert Rommel
  - **Gouf (Ramba Ral)** — pilot główny: Ramba Ral
  - **Zaku II/Bazooka** — pilot główny: Acous
  - **Zaku II/Karabin maszynowy** — pilot główny: Cozun Graham

### Odcinek 19 — Odwrót z Axis (`DL519_13`)

**Źródło:** `eventP05.EDAT/DL519_13_Entry.dat`
**Warunki misji:**
> W tej misji "NT-1 Alex" musi wyruszyć jako GR,
> a "Zaku II Kai" nie może wziąć udziału.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Gattle** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Gattle** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu
  - **Gelgoog** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Gwazine** — pilot główny: Kycilia Zabi
  - **Kampfer/Bazooka** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zaku II Kai** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zaku II Kai** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zeong** — pilot główny: Char Aznable

### Odcinek 19 — Pościg jednostki Newtype (`DL519_20`)

**Źródło:** `eventP05.EDAT/DL519_20_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Endra** — pilot główny: Oficer Neo Zeonu
  - **Endra** — pilot główny: Oficer Neo Zeonu
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Qubeley** — pilot główny: Haman Karn
  - **Qubeley Mk-II (Ple Two)** — pilot główny: Ple Two
  - **Qubeley Mk-II (Ple)** — pilot główny: Elpeo Ple

### Odcinek 19 — Mr. Bushido (`DL519_30`)

**Źródło:** `eventP05.EDAT/DL519_30_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **00 Raiser** — pilot główny: Setsuna F. Seiei — piloci wspierający w misji: Saji Crossroad (po połączeniu w trakcie misji; wcześniej osobno w Spaceship (`Entry ID 15000`))
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage
  - **Gundam Exia** — pilot główny: Setsuna F. Seiei
  - **Turner** — pilot główny: Mirawoo Kyao
  - **Wing Gundam Zero** — pilot główny: Heero Yuy

**Jednostki wrogie:**
  - **Gelgoog** — pilot główny: Żołnierz Zeonu
  - **Gelgoog** — pilot główny: Żołnierz Zeonu
  - **Kampfer/Bazooka** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Kampfer/High Mobility** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Susanowo** — pilot główny: Mr. Bushido
  - **Tallgeese** — pilot główny: Zechs Merquise
  - **Zaku II Kai** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zaku II Kai** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zanzibar** — pilot główny: Oficer Zeonu

**Jednostki neutralne / trzeciej strony:**
  - **Spaceship** — pilot główny: Saji Crossroad

### Odcinek 19 — Uderz w bazę zaopatrzeniową wroga (`DL519_40`)

**Źródło:** `eventP05.EDAT/DL519_40_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×3 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×3 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×4 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×4 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×5 rekordów źródłowych Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×5 rekordów źródłowych Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×4 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×4 rekordy źródłowe Entry ID
  - **Pancernik kosmiczny klasy Lesrion** — pilot główny: Oficer Balarantu

### Odcinek 19 — Zajęcie bazy (`DL519_50`)

**Źródło:** `eventP05.EDAT/DL519_50_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki wrogie:**
  - **Bat-Shu** — pilot główny: Posaydal Regular
  - **Bat-Shu** — pilot główny: Posaydal Regular
  - **Braver** — pilot główny: Żołnierz Gradosu — ×2 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×2 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×4 rekordy źródłowe Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×4 rekordy źródłowe Entry ID

### Odcinek 20 — Brama warp nr 203 (`DL520_11`)

**Źródło:** `eventP05.EDAT/DL520_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Giga Nekton αα** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine G** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID

### Odcinek 20 — Dziedzictwo miecza (`DL520_12`)

**Źródło:** `eventP05.EDAT/DL520_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 1 identyfikator `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage — obecny alternatywny rekord Entry ID
  - **God Gundam** — pilot główny: Domon Kasshu — obecny alternatywny rekord Entry ID
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Benthos Carrier α** — pilot główny: Mucus
  - **Giga Nekton α** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID

### Odcinek 20 — Badanie planety (`DL520_13`)

**Źródło:** `eventP05.EDAT/DL520_13_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Giga Nekton α** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Mucus Gate L** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID
  - **Nekton Shooter** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID

### Odcinek 20 — Determinacja pod maską (`DL520_40`)

**Źródło:** `eventP05.EDAT/DL520_40_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **00 Raiser** — pilot główny: Setsuna F. Seiei — piloci wspierający w misji: Saji Crossroad
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage
  - **Gundam** — pilot główny: Amuro Ray
  - **Hyaku Shiki** — pilot główny: Quattro Bajeena
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass
  - **Mucus Gate S** — pilot główny: Brak przypisanego klucza pilota w Entry — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Susanowo/Ally** — pilot główny: Mr. Bushido
  - **Tallgeese/Ally** — pilot główny: Zechs Merquise
  - **Wing Gundam Zero** — pilot główny: Heero Yuy

**Jednostki wrogie:**
  - **Invader/Air** — pilot główny: Invader — ×10 rekordów źródłowych Entry ID
  - **Invader/Starfish** — pilot główny: Invader — ×13 rekordów źródłowych Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Shooter** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Susanowo** — pilot główny: Mr. Bushido
  - **Tallgeese** — pilot główny: Zechs Merquise
  - **Zeong** — pilot główny: Char Aznable

### Odcinek 20 — Pułapka na Księżycu (`DL520_50`)

**Źródło:** `eventP28.EDAT/DL520_50_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Nu Gundam** — pilot główny: Amuro Ray
  - **Sazabi** — pilot główny: Quattro Bajeena
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Endra** — pilot główny: Oficer Neo Zeonu
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×5 rekordów źródłowych Entry ID
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×5 rekordów źródłowych Entry ID
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Gelgoog** — pilot główny: Pilot MS — ×4 rekordy źródłowe Entry ID
  - **Nekton Mine** — pilot główny: --- — ×4 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Qubeley Mk-II (Ple Two)** — pilot główny: Ple Two
  - **Rick Dom** — pilot główny: Pilot MS — ×4 rekordy źródłowe Entry ID
  - **Zaku II Kai** — pilot główny: Pilot MS — ×2 rekordy źródłowe Entry ID
  - **Zaku III (Rakan)** — pilot główny: Rakan Dahkaran

### Odcinek 20 — Da Cider Błyskawica (`DL520_60`)

**Źródło:** `eventP05.EDAT/DL520_60_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Hulk Gunship Axe Bomber** — pilot główny: Cocoa Arara — piloci wspierający w misji: Milk Arara, Cafe au Lait Arara
  - **King Squasher** — pilot główny: Hero Lamuness — piloci wspierający w misji: Tama-Q
  - **Queen Cideron/Ally** — pilot główny: Da Cider — piloci wspierający w misji: Hebi Metako

**Jednostki wrogie:**
  - **Monskar Medessa** — pilot główny: Monskar — ×5 rekordów źródłowych Entry ID
  - **Monskar Neppoon** — pilot główny: Monskar — ×7 rekordów źródłowych Entry ID
  - **Queen Cideron** — pilot główny: Da Cider
  - **Żołnierz Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka — ×6 rekordów źródłowych Entry ID
  - **Żołnierz Mrocznego Smoka/Snajper** — pilot główny: Żołnierz Mrocznego Smoka — ×4 rekordy źródłowe Entry ID

### Odcinek 21 — Mroczny Zwarth (`DL521_11`)

**Źródło:** `eventP05.EDAT/DL521_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Billbine** — pilot główny: Show Zama — piloci wspierający w misji: Chum Huau
  - **Dunbine** — pilot główny: Show Zama — piloci wspierający w misji: Chum Huau
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki sojusznicze (NPC):**
  - **Pancernik kosmiczny klasy Giga** — pilot główny: Oficer Gilgameshu — ×2 rekordy źródłowe Entry ID

**Jednostki wrogie:**
  - **Monskar Medessa** — pilot główny: Monskar — ×4 rekordy źródłowe Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Shooter** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Okręt eskorty Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka — ×2 rekordy źródłowe Entry ID
  - **Zwarth** — pilot główny: Black Knight
  - **Zwarth/Hyper** — pilot główny: Black Knight
  - **Żołnierz Mrocznego Smoka/Lot** — pilot główny: Żołnierz Mrocznego Smoka — ×4 rekordy źródłowe Entry ID
  - **Żołnierz Mrocznego Smoka/Snajper** — pilot główny: Żołnierz Mrocznego Smoka — ×2 rekordy źródłowe Entry ID

### Odcinek 21 — Ostateczna forma Goburikiego (`DL521_12`)

**Źródło:** `eventP05.EDAT/DL521_12_Entry.dat`
**Warunki misji:**
> "Demon God Goburiki" porusza się w specjalny sposób.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Hulk Gunship Axe Bomber** — pilot główny: Cocoa Arara — piloci wspierający w misji: Milk Arara, Cafe au Lait Arara
  - **King Squasher** — pilot główny: Hero Lamuness — piloci wspierający w misji: Tama-Q
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass
  - **Queen Cideron/Ally** — pilot główny: Da Cider — piloci wspierający w misji: Hebi Metako

**Jednostki wrogie:**
  - **Demon God Goburiki/Ultimate** — pilot główny: Don Harumage
  - **Giga Nekton α** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Monskar Medessa** — pilot główny: Monskar — ×14 rekordów źródłowych Entry ID
  - **Monskar Neppoon** — pilot główny: Monskar — ×18 rekordów źródłowych Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 21 — Awangarda komórek DG (`DL521_20`)

**Źródło:** `eventP05.EDAT/DL521_20_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Qubeley Mk-II (Ple, Ally)** — pilot główny: Elpeo Ple
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Death Army** — pilot główny: DG Cells — ×16 rekordów źródłowych Entry ID
  - **Death Bird** — pilot główny: DG Cells — ×34 rekordy źródłowe Entry ID
  - **Mucus Gate M DG** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Mucus Gate S DG** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Hauser** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Shooter** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID

### Odcinek 21 — Nadlatuje asteroida DG (`DL521_40`)

**Źródło:** `eventP06.EDAT/DL521_40_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage
  - **God Gundam** — pilot główny: Domon Kasshu

**Jednostki wrogie:**
  - **Death Army** — pilot główny: DG Cells — ×10 rekordów źródłowych Entry ID
  - **Death Bird** — pilot główny: DG Cells — ×5 rekordów źródłowych Entry ID
  - **Mucus Gate S DG** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 21 — Nowy Knightmare Frame (`DL521_70`)

**Źródło:** `eventP29.EDAT/DL521_70_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Guren S.E.I.T.E.N.** — pilot główny: Kallen Kozuki
  - **Lancelot Albion** — pilot główny: Suzaku Kururugi
  - **Shinkiro** — pilot główny: Zero

**Jednostki wrogie:**
  - **Giga Nekton α** — pilot główny: Mucus
  - **Nekton Assault** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID

### Odcinek 22 — Bój z komórkami DG R1 (`DL622_11`)

**Źródło:** `eventP06.EDAT/DL622_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Benthos Cruiser α** — pilot główny: Mucus
  - **Death Army** — pilot główny: DG Cells — ×8 rekordów źródłowych Entry ID
  - **Death Bird** — pilot główny: DG Cells — ×15 rekordów źródłowych Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus
  - **Nekton Hauser** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine G** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus

### Odcinek 22 — Bój z komórkami DG R2 (`DL622_12`)

**Źródło:** `eventP06.EDAT/DL622_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Death Army** — pilot główny: DG Cells — ×8 rekordów źródłowych Entry ID
  - **Death Bird** — pilot główny: DG Cells — ×12 rekordów źródłowych Entry ID
  - **Giga Nekton α** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Mucus Gate L DG** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Mucus Gate S** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Hauser** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID

### Odcinek 22 — Devil Gundam, ostatnia runda (`DL622_13`)

**Źródło:** `eventP06.EDAT/DL622_13_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **God Gundam** — pilot główny: Domon Kasshu
  - **Turner** — pilot główny: Mirawoo Kyao
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Death Army** — pilot główny: DG Cells — ×6 rekordów źródłowych Entry ID
  - **Death Bird** — pilot główny: DG Cells — ×6 rekordów źródłowych Entry ID
  - **Devil Gundam** — pilot główny: DG Cells
  - **Giga Nekton α** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Giga Nekton αα** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Gundam Head** — pilot główny: DG Cells — ×2 rekordy źródłowe Entry ID
  - **Mucus Gate S** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID

### Odcinek 22 — Nadchodzi God Keron! (`DL622_30`)

**Źródło:** `eventP06.EDAT/DL622_30_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Blade Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette
  - **Dibison** — pilot główny: Thomas Richard Schubaltz
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage
  - **God Keron** — pilot główny: Sierżant Keroro — piloci wspierający w misji: Cpl. Giroro, Pvt. Tamama, Starszy sierżant Kululu, Lance Cpl. Dororo
  - **Keroro Robo Mk-II** — pilot główny: Sierżant Keroro
  - **Lightning Saix** — pilot główny: Irvine
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Giga Nekton α** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Mucus Gate M** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×7 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×7 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID
  - **Nekton Shooter** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID

### Odcinek 22 — Wielki zlot bohaterów Eldrana! (`DL622_50`)

**Źródło:** `eventP06.EDAT/DL622_50_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Ganbaruger** — pilot główny: Kotaro Kirigakure — piloci wspierający w misji: Yosuke Kazamatsuri, Rikiya Ryuzaki
  - **Go-Saurer** — pilot główny: Kenichi Minezaki — piloci wspierający w misji: Hiromi Tachibana, Shinobu Asaoka, Taro Shirogane, Yoji Hiyama
  - **Perfect Daiteioh** — pilot główny: Taro Omomo — piloci wspierający w misji: Mai Ozora, Kakeru Daichi, Hiryu Tsukishiro
  - **Raijin-Oh** — pilot główny: Jin Hyuga — piloci wspierający w misji: Asuka Tsukishiro, Koji Hoshiyama

**Jednostki wrogie:**
  - **Giga Nekton α** — pilot główny: Mucus — ×7 rekordów źródłowych Entry ID
  - **Mucus Gate L MC** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Nekton Mine G** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID

### Odcinek 22 — Laser kolonijny znów działa (`DL622_60`)

**Źródło:** `eventP06.EDAT/DL622_60_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Directional Mine** — pilot główny: Control AI — ×6 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Gattle** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Gattle** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Gelgoog** — pilot główny: Żołnierz Zeonu — ×6 rekordów źródłowych Entry ID
  - **Gelgoog** — pilot główny: Żołnierz Zeonu — ×6 rekordów źródłowych Entry ID
  - **Gwazine** — pilot główny: Conscon
  - **Kampfer/Bazooka** — pilot główny: Żołnierz Zeonu
  - **Kampfer/Bazooka** — pilot główny: Żołnierz Zeonu
  - **Kampfer/High Mobility** — pilot główny: Żołnierz Zeonu
  - **Kampfer/High Mobility** — pilot główny: Żołnierz Zeonu
  - **Musai** — pilot główny: Oficer Zeonu
  - **Musai** — pilot główny: Oficer Zeonu
  - **Rick Dom (Black Tri-Stars)** — pilot główny: Gaia
  - **Rick Dom (Black Tri-Stars)** — pilot główny: Mash
  - **Rick Dom (Black Tri-Stars)** — pilot główny: Ortega
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu — ×3 rekordy źródłowe Entry ID
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID

### Odcinek 23 — Pułapka Gihrena (`DL623_11`)

**Źródło:** `eventP06.EDAT/DL623_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Apsalus III** — pilot główny: Ginias Sahalin
  - **Bigro** — pilot główny: Żołnierz Zeonu
  - **Gattle** — pilot główny: Żołnierz Zeonu
  - **Gattle** — pilot główny: Żołnierz Zeonu
  - **Gelgoog** — pilot główny: Żołnierz Zeonu — ×6 rekordów źródłowych Entry ID
  - **Gelgoog** — pilot główny: Żołnierz Zeonu — ×6 rekordów źródłowych Entry ID
  - **Gwazine** — pilot główny: Gihren Zabi
  - **Kampfer/Bazooka** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Kampfer/High Mobility** — pilot główny: Żołnierz Zeonu
  - **Kampfer/High Mobility** — pilot główny: Żołnierz Zeonu
  - **Musai** — pilot główny: Oficer Zeonu
  - **Musai** — pilot główny: Oficer Zeonu
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×7 rekordów źródłowych Entry ID
  - **Rick Dom** — pilot główny: Żołnierz Zeonu — ×7 rekordów źródłowych Entry ID
  - **Zaku II Kai** — pilot główny: Żołnierz Zeonu
  - **Zaku II Kai** — pilot główny: Żołnierz Zeonu

### Odcinek 23 — Determinacja Haman (`DL623_12`)

**Źródło:** `eventP06.EDAT/DL623_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Big Zam** — pilot główny: Żołnierz Neo Zeonu
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×5 rekordów źródłowych Entry ID
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×5 rekordów źródłowych Entry ID
  - **Endra** — pilot główny: Oficer Neo Zeonu
  - **Endra** — pilot główny: Oficer Neo Zeonu
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×6 rekordów źródłowych Entry ID
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×6 rekordów źródłowych Entry ID
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu
  - **Qubeley** — pilot główny: Haman Karn
  - **Sadalahn** — pilot główny: Haman Karn
  - **Zaku III** — pilot główny: Żołnierz Neo Zeonu — ×4 rekordy źródłowe Entry ID
  - **Zaku III (Rakan)** — pilot główny: Rakan Dahkaran

### Odcinek 23 — Zjednoczenie Ziemi (`DL623_13`)

**Źródło:** `eventP06.EDAT/DL623_13_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Gundam Ez8** — pilot główny: Shiro Amada
  - **Qubeley Mk-II (Ple, Ally)** — pilot główny: Elpeo Ple
  - **ZZ Gundam** — pilot główny: Judau Ashta

**Jednostki wrogie:**
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×5 rekordów źródłowych Entry ID
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×5 rekordów źródłowych Entry ID
  - **Kampfer/Bazooka** — pilot główny: Żołnierz Neo Zeonu
  - **Kampfer/Bazooka** — pilot główny: Żołnierz Neo Zeonu
  - **Qubeley** — pilot główny: Haman Karn
  - **Quin Mantha** — pilot główny: Ple Two
  - **Zaku III** — pilot główny: Żołnierz Neo Zeonu — ×4 rekordy źródłowe Entry ID

### Odcinek 23 — Wspólny front (`DL623_25`)

**Źródło:** `eventP06.EDAT/DL623_25_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Benthos Cruiser α** — pilot główny: Mucus
  - **Giga Nekton α** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Mucus Gate L** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine G** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID

### Odcinek 23 — Oczyszczenie Mucus Gate (`DL623_35`)

**Źródło:** `eventP06.EDAT/DL623_35_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Giga Nekton α** — pilot główny: Mucus
  - **Giga Nekton αα** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Mucus Gate L** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×10 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×10 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine G** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID

### Odcinek 23 — Złowrogie znaki (`DL623_45`)

**Źródło:** `eventP06.EDAT/DL623_45_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage
  - **Final Dancouga** — pilot główny: Shinobu Fujiwara — piloci wspierający w misji: Sara Yuki, Ryo Shiba, Masato Shikibu, Alan Igor
  - **Mazinger Z** — pilot główny: Koji Kabuto

**Jednostki wrogie:**
  - **Mucus Gate S** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×7 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID

### Odcinek 24 — Wspomnienia o matce (`DL624_11`)

**Źródło:** `eventP06.EDAT/DL624_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Benthos Carrier α** — pilot główny: Mucus
  - **Giga Nekton α** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Giga Nekton αα** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×14 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID

### Odcinek 24 — Pojedynek z Viralem (`DL624_12`)

**Źródło:** `eventP06.EDAT/DL624_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage
  - **GoShogun** — pilot główny: Brak przypisanego klucza pilota w Entry — piloci wspierający w misji: Killy Gagley, Remy Shimada — ×6 rekordów źródłowych Entry ID
  - **Gurren Lagann (Simon)** — pilot główny: Simon — piloci wspierający w misji: Kamina, Yoko, Boota

**Jednostki wrogie:**
  - **Enkidu** — pilot główny: Viral
  - **Giga Nekton α** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Shooter** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID

### Odcinek 24 — Odkopywanie Sirbine (`DL624_25`)

**Źródło:** `eventP30.EDAT/DL624_25_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Gurren Lagann (Simon)** — pilot główny: Simon — piloci wspierający w misji: Kamina, Yoko, Boota
  - **Sirbine** — pilot główny: Show Zama — piloci wspierający w misji: Chum Huau
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Okręt eskorty Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka
  - **Żołnierz Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka — ×10 rekordów źródłowych Entry ID
  - **Żołnierz Mrocznego Smoka/Lot** — pilot główny: Żołnierz Mrocznego Smoka — ×9 rekordów źródłowych Entry ID
  - **Żołnierz Mrocznego Smoka/Snajper** — pilot główny: Żołnierz Mrocznego Smoka — ×6 rekordów źródłowych Entry ID

### Odcinek 24 — Inwazja Metal Knights (`DL624_35`)

**Źródło:** `eventP06.EDAT/DL624_35_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Mucus Gate S** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus
  - **Nekton Shooter** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Seryjny Metal Knight** — pilot główny: Metal Knight — ×6 rekordów źródłowych Entry ID
  - **Seryjny Metal Knight/Ciężki** — pilot główny: Metal Knight — ×5 rekordów źródłowych Entry ID

### Odcinek 24 — Najazd na Earthtię (`DL624_45`)

**Źródło:** `eventP06.EDAT/DL624_45_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Mucus Gate S** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Nekton Shooter** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Seryjny Metal Knight** — pilot główny: Metal Knight — ×5 rekordów źródłowych Entry ID
  - **Seryjny Metal Knight/Ciężki** — pilot główny: Metal Knight — ×4 rekordy źródłowe Entry ID

### Odcinek 25 — Obrona Eldgear (`DL625_11`)

**Źródło:** `eventP06.EDAT/DL625_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Dark Knight Steru/Dark Dragon Form** — pilot główny: Galden
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki sojusznicze (NPC):**
  - **Eldgear Central Tower** — pilot główny: White Dragon — cel/obiekt skryptowy; nie jest pilotowanym mechem

**Jednostki wrogie:**
  - **Okręt eskorty Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka — ×2 rekordy źródłowe Entry ID
  - **Okręt eskorty Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka — ×2 rekordy źródłowe Entry ID
  - **Żołnierz Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka — ×8 rekordów źródłowych Entry ID
  - **Żołnierz Mrocznego Smoka/Lot** — pilot główny: Żołnierz Mrocznego Smoka — ×8 rekordów źródłowych Entry ID
  - **Żołnierz Mrocznego Smoka/Snajper** — pilot główny: Żołnierz Mrocznego Smoka — ×4 rekordy źródłowe Entry ID

### Odcinek 25 — Ku Earth Blade (`DL625_12`)

**Źródło:** `eventP06.EDAT/DL625_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Benthos Cruiser α** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Giga Nekton αα** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine G** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Seryjny Metal Knight/Ciężki** — pilot główny: Metal Knight — ×6 rekordów źródłowych Entry ID

### Odcinek 25 — Zły Bóg Drago (`DL625_13`)

**Źródło:** `eventP06.EDAT/DL625_13_Entry.dat`
**Warunki misji:**
> "Evil God Drago" porusza się w specjalny sposób.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Maryu-Oh Dolga** — pilot główny: Ryu Dolk
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Evil God Drago** — pilot główny: Evil God Drago — zmiana strony w trakcie misji: neutralna / trzeciej strony, sojusznicza (NPC)
  - **Giga Nekton α** — pilot główny: Mucus — ×10 rekordów źródłowych Entry ID
  - **Mucus Gate L DR** — pilot główny: Mucus — zmiana strony w trakcie misji: neutralna / trzeciej strony, sojusznicza (NPC) — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID
  - **Seryjny Metal Knight** — pilot główny: Metal Knight — ×7 rekordów źródłowych Entry ID
  - **Seryjny Metal Knight/Ciężki** — pilot główny: Metal Knight — ×15 rekordów źródłowych Entry ID

### Odcinek 25 — Operacja: schwytanie uśpionych Zoidów (`DL625_40`)

**Źródło:** `eventP06.EDAT/DL625_40_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Command Wolf/White** — pilot główny: Zoid Core — ×6 rekordów źródłowych Entry ID
  - **Dark Horn** — pilot główny: Zoid Core — ×4 rekordy źródłowe Entry ID
  - **Gun Sniper** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID
  - **Gun Sniper/WW** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID
  - **Iron Kong** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Zoid Core — ×10 rekordów źródłowych Entry ID
  - **Mucus Gate M** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID

### Odcinek 25 — Giwaza Lowaw (`DL625_45`)

**Źródło:** `eventP06.EDAT/DL625_45_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Auge** — pilot główny: Nei Moh Han
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×13 rekordów źródłowych Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×12 rekordów źródłowych Entry ID
  - **Bat-Shu/Strong** — pilot główny: Hekeler Mauzer
  - **Braver** — pilot główny: Żołnierz Gradosu — ×5 rekordów źródłowych Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×5 rekordów źródłowych Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×4 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×5 rekordów źródłowych Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Sarge Aupus** — pilot główny: Oficer armii Posaydala
  - **Sarge Aupus (Giwaza)** — pilot główny: Giwaza Lowaw

### Odcinek 25 — Geno Breaker powraca (`DL625_50`)

**Źródło:** `eventP06.EDAT/DL625_50_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Blade Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette
  - **Dibison** — pilot główny: Thomas Richard Schubaltz
  - **Iron Kong Mk-II** — pilot główny: Karl Lichten Schubaltz
  - **Lightning Saix** — pilot główny: Irvine
  - **Mucus Gate S** — pilot główny: Brak przypisanego klucza pilota w Entry — cel/obiekt skryptowy; nie jest pilotowanym mechem

**Jednostki sojusznicze (NPC):**
  - **Command Wolf/White** — pilot główny: Żołnierz Republiki Helic — ×3 rekordy źródłowe Entry ID
  - **Iron Kong** — pilot główny: Oficer Imperium Guylos

**Jednostki wrogie:**
  - **Command Wolf/Khaki** — pilot główny: Zoid Core — ×4 rekordy źródłowe Entry ID
  - **Dark Horn** — pilot główny: Zoid Core — ×3 rekordy źródłowe Entry ID
  - **Geno Breaker** — pilot główny: Raven
  - **Giga Nekton α** — pilot główny: Mucus
  - **Gun Sniper** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID
  - **Gun Sniper/WW** — pilot główny: Zoid Core
  - **Iron Kong** — pilot główny: Zoid Core — ×3 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Zoid Core — ×8 rekordów źródłowych Entry ID
  - **Mucus Gate S** — pilot główny: Brak przypisanego klucza pilota w Entry — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID

### Odcinek 26 — Wysłannik zagłady (`DL726_11`)

**Źródło:** `eventP07.EDAT/DL726_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Blade Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette
  - **Dibison** — pilot główny: Thomas Richard Schubaltz
  - **Lightning Saix** — pilot główny: Irvine
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Dark Horn** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID
  - **Death Stinger** — pilot główny: Hiltz
  - **Geno Breaker** — pilot główny: Raven
  - **Gun Sniper** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID
  - **Iron Kong** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Zoid Core — ×4 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID

### Odcinek 26 — Upadek stolicy (`DL726_12`)

**Źródło:** `eventP07.EDAT/DL726_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Dark Horn** — pilot główny: Zoid Core — ×3 rekordy źródłowe Entry ID
  - **Death Stinger** — pilot główny: Hiltz
  - **Gun Sniper** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID
  - **Iron Kong** — pilot główny: Zoid Core — ×3 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Zoid Core — ×4 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Nekton Shooter** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Zoid Core — ×4 rekordy źródłowe Entry ID

### Odcinek 26 — Odrodzenie Ultrasaurusa (`DL726_13`)

**Źródło:** `eventP07.EDAT/DL726_13_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Blade Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette
  - **Dibison** — pilot główny: Thomas Richard Schubaltz
  - **Lightning Saix** — pilot główny: Irvine
  - **Turner** — pilot główny: Mirawoo Kyao
  - **Ultrasaurus** — pilot główny: Rob Herman — piloci wspierający w misji: Moonbay, Karl Lichten Schubaltz
  - **Ultrasaurus/Inactive** — pilot główny: Rob Herman — piloci wspierający w misji: Moonbay, Karl Lichten Schubaltz

**Jednostki wrogie:**
  - **Command Wolf/Khaki** — pilot główny: Zoid Core — ×10 rekordów źródłowych Entry ID
  - **Dark Horn** — pilot główny: Zoid Core — ×9 rekordów źródłowych Entry ID
  - **Death Stinger** — pilot główny: Hiltz
  - **Giga Nekton α** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Gun Sniper** — pilot główny: Zoid Core — ×5 rekordów źródłowych Entry ID
  - **Gun Sniper/WW** — pilot główny: Zoid Core — ×5 rekordów źródłowych Entry ID
  - **Iron Kong** — pilot główny: Zoid Core — ×5 rekordów źródłowych Entry ID
  - **Molga** — pilot główny: Zoid Core — ×18 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×22 rekordy źródłowe Entry ID

### Odcinek 26 — Na krawędzi śmierci (`DL726_25`)

**Źródło:** `eventP07.EDAT/DL726_25_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **AT Fly** — pilot główny: Vanilla Vartla
  - **Berserga WP** — pilot główny: Ru Shako
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage
  - **Scopedog RSC (Byman)** — pilot główny: Byman Hagard
  - **Scopedog RSC (Chirico)** — pilot główny: Chirico Cuvie
  - **Scopedog RSC (Gregore)** — pilot główny: Gregore Garosh
  - **Scopedog RSC (Murza)** — pilot główny: Murza Melym
  - **Scopedog TC/ISS (Barcoff)** — pilot główny: Nor Barcoff
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Bat-Shu** — pilot główny: Posaydal Regular
  - **Braver** — pilot główny: Żołnierz Gradosu
  - **Braver** — pilot główny: Żołnierz Gradosu
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **Scopedog** — pilot główny: Pilot AT — ×14 rekordów źródłowych Entry ID
  - **Scopedog/M** — pilot główny: Pilot AT — ×8 rekordów źródłowych Entry ID

### Odcinek 26 — Poszukiwanie Imperium Mechanizacji (`DL726_35`)

**Źródło:** `eventP07.EDAT/DL726_35_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Dark Go-Saurer** — pilot główny: Mechabestia — ×3 rekordy źródłowe Entry ID
  - **Gandoppler** — pilot główny: Mechabestia — ×14 rekordów źródłowych Entry ID
  - **Giga Nekton α** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Giga Nekton αα** — pilot główny: Mucus
  - **Mucus Gate M MC** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×7 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine G** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 26 — Trop Imperium Mechanizacji (`DL726_45`)

**Źródło:** `eventP07.EDAT/DL726_45_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Bolt Robo/Anti-Air** — pilot główny: Mechabestia — ×6 rekordów źródłowych Entry ID
  - **Bolt Robo/Long-Range** — pilot główny: Mechabestia — ×5 rekordów źródłowych Entry ID
  - **Bolt Robo/Melee** — pilot główny: Mechabestia — ×5 rekordów źródłowych Entry ID
  - **Dark Go-Saurer** — pilot główny: Mechabestia — ×5 rekordów źródłowych Entry ID
  - **Gandoppler** — pilot główny: Mechabestia — ×6 rekordów źródłowych Entry ID
  - **Giga Nekton αα** — pilot główny: Mucus
  - **Mucus Gate M MC** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×9 rekordów źródłowych Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine G** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 27 — Ku Zamkowi Mechanizacji (`DL727_11`)

**Źródło:** `eventP07.EDAT/DL727_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Benthos Carrier α** — pilot główny: Mucus
  - **Benthos Cruiser α** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Dark Go-Saurer** — pilot główny: Mechabestia — ×4 rekordy źródłowe Entry ID
  - **Gandoppler** — pilot główny: Mechabestia — ×8 rekordów źródłowych Entry ID
  - **Giga Nekton α** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Giga Nekton αα** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×10 rekordów źródłowych Entry ID

### Odcinek 27 — Groza! Gniew Kikaishina (`DL727_12`)

**Źródło:** `eventP07.EDAT/DL727_12_Entry.dat`
**Warunki misji:**
> "Kikaishin" porusza się w specjalny sposób.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Go-Saurer** — pilot główny: Kenichi Minezaki — piloci wspierający w misji: Hiromi Tachibana, Shinobu Asaoka, Taro Shirogane, Yoji Hiyama
  - **God Raijin-Oh** — pilot główny: Jin Hyuga — piloci wspierający w misji: Asuka Tsukishiro, Koji Hoshiyama, Bakuryu-Oh
  - **Great Ganbaruger** — pilot główny: Kotaro Kirigakure — piloci wspierający w misji: Yosuke Kazamatsuri, Rikiya Ryuzaki
  - **Perfect Daiteioh** — pilot główny: Taro Omomo — piloci wspierający w misji: Mai Ozora, Kakeru Daichi, Hiryu Tsukishiro
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Bolt Robo/Anti-Air** — pilot główny: Mechabestia — ×11 rekordów źródłowych Entry ID
  - **Dark Go-Saurer** — pilot główny: Mechabestia — ×10 rekordów źródłowych Entry ID
  - **Dreissen** — pilot główny: Control AI — ×2 rekordy źródłowe Entry ID
  - **Gandoppler** — pilot główny: Mechabestia — ×12 rekordów źródłowych Entry ID
  - **Gelgoog** — pilot główny: Control AI — ×2 rekordy źródłowe Entry ID
  - **Giga Nekton α** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Giga Nekton αα** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **HAL-X10** — pilot główny: Control AI
  - **Helldiver** — pilot główny: Control AI
  - **Kampfer/High Mobility** — pilot główny: Control AI — ×2 rekordy źródłowe Entry ID
  - **Kikaishin** — pilot główny: Kikaishin — zmiana strony w trakcie misji: neutralna / trzeciej strony, sojusznicza (NPC)
  - **Mucus Gate L MC** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Mucus Gate S** — pilot główny: Brak przypisanego klucza pilota w Entry — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine G** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Type-Zero/Wróg** — pilot główny: Control AI

### Odcinek 27 — Quwasan Olibee (`DL727_40`)

**Źródło:** `eventP07.EDAT/DL727_40_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Auge** — pilot główny: Antoon Randow
  - **Auge** — pilot główny: Nei Moh Han
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×3 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×3 rekordy źródłowe Entry ID
  - **Bat-Shu/Strong** — pilot główny: Hekeler Mauzer
  - **Braver** — pilot główny: Żołnierz Gradosu — ×3 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×3 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Sarge Aupus (Nei)** — pilot główny: Oficer armii Posaydala

### Odcinek 27 — Under the Flag (`DL727_50`)

**Źródło:** `eventP07.EDAT/DL727_50_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×3 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×3 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×9 rekordów źródłowych Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×9 rekordów źródłowych Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×8 rekordów źródłowych Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×6 rekordów źródłowych Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×5 rekordów źródłowych Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×7 rekordów źródłowych Entry ID
  - **Nowy gigantyczny lotniskowiec Grados** — pilot główny: Oficer Gradosu
  - **Pancernik kosmiczny klasy Lesrion** — pilot główny: Oficer Balarantu

### Odcinek 27 — Chess Piece (`DL727_60`)

**Źródło:** `eventP07.EDAT/DL727_60_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Slender Skala** — pilot główny: Gavlet Gablae
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×10 rekordów źródłowych Entry ID
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×8 rekordów źródłowych Entry ID
  - **B-SFTV-AT-105 Zahatt** — pilot główny: Żołnierz Balarantu — ×4 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×12 rekordów źródłowych Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×9 rekordów źródłowych Entry ID
  - **Directional Mine** — pilot główny: Control AI — ×6 rekordów źródłowych Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×10 rekordów źródłowych Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×10 rekordów źródłowych Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Lądowy pancernik Balarant** — pilot główny: Oficer Balarantu
  - **Nowy gigantyczny lotniskowiec Grados** — pilot główny: Oficer Gradosu — ×3 rekordy źródłowe Entry ID

### Odcinek 28 — First Attack (`DL728_11`)

**Źródło:** `eventP07.EDAT/DL728_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Auge** — pilot główny: Nei Moh Han
  - **Bat-Shu** — pilot główny: Antoon Randow — zmiana strony w trakcie misji: neutralna / trzeciej strony
  - **Bat-Shu** — pilot główny: Hekeler Mauzer — zmiana strony w trakcie misji: neutralna / trzeciej strony
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×8 rekordów źródłowych Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×7 rekordów źródłowych Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×4 rekordy źródłowe Entry ID — zmiana strony w trakcie misji: neutralna / trzeciej strony
  - **Braver** — pilot główny: Żołnierz Gradosu — ×4 rekordy źródłowe Entry ID — zmiana strony w trakcie misji: neutralna / trzeciej strony
  - **Daljan** — pilot główny: Gosterro — zmiana strony w trakcie misji: neutralna / trzeciej strony
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×4 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×4 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Sarge Aupus (Nei)** — pilot główny: Nei Moh Han — zmiana strony w trakcie misji: neutralna / trzeciej strony

### Odcinek 28 — Revenge Battle (`DL728_12`)

**Źródło:** `eventP07.EDAT/DL728_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Turner** — pilot główny: Mirawoo Kyao
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Auge** — pilot główny: Antoon Randow
  - **Auge** — pilot główny: Nei Moh Han
  - **Auge** — pilot główny: Posaydal Regular — ×2 rekordy źródłowe Entry ID
  - **Auge** — pilot główny: Posaydal Regular — ×2 rekordy źródłowe Entry ID
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×3 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×12 rekordów źródłowych Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×10 rekordów źródłowych Entry ID
  - **Bat-Shu/Strong** — pilot główny: Hekeler Mauzer
  - **Braver** — pilot główny: Żołnierz Gradosu — ×3 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×3 rekordy źródłowe Entry ID
  - **Daljan** — pilot główny: Gosterro
  - **Nowy gigantyczny lotniskowiec Grados** — pilot główny: Oficer Gradosu
  - **Sarge Aupus (Giwaza)** — pilot główny: Giwaza Lowaw
  - **Zakarl** — pilot główny: Le Cain

### Odcinek 28 — Dreamers Again (`DL728_13`)

**Źródło:** `eventP07.EDAT/DL728_13_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **D-Sserd** — pilot główny: Fannaria Amm
  - **L-Gaim Mk-II** — pilot główny: Daba Myroad — piloci wspierający w misji: Lilis Faw
  - **Novel D-Sserd** — pilot główny: Gaw Ha Leccee
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Aug** — pilot główny: True Posaydal
  - **Auge** — pilot główny: Posaydal Regular — ×5 rekordów źródłowych Entry ID
  - **Auge** — pilot główny: Posaydal Regular — ×5 rekordów źródłowych Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×6 rekordów źródłowych Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×6 rekordów źródłowych Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×5 rekordów źródłowych Entry ID
  - **Fatty (Ground)** — pilot główny: Żołnierz Balarantu — ×5 rekordów źródłowych Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Serce Lachesis** — pilot główny: ---

**Jednostki neutralne / trzeciej strony:**
  - **Serce Lachesis** — pilot główny: ---

### Odcinek 28 — The Last Red Shoulder (`DL728_20`)

**Źródło:** `eventP07.EDAT/DL728_20_Entry.dat`
**Warunki misji:**
> W tej misji skład jednostek jest z góry ustalony.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Scopedog RSC (Byman)** — pilot główny: Byman Hagard
  - **Scopedog RSC (Chirico)** — pilot główny: Chirico Cuvie
  - **Scopedog RSC (Gregore)** — pilot główny: Gregore Garosh
  - **Scopedog RSC (Murza)** — pilot główny: Murza Melym

**Jednostki wrogie:**
  - **Blood Sucker** — pilot główny: Żołnierz Red Shoulder — ×7 rekordów źródłowych Entry ID
  - **Mucus Gate S** — pilot główny: Control AI — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Scopedog TC-RS** — pilot główny: Żołnierz Red Shoulder — ×2 rekordy źródłowe Entry ID
  - **Scopedog TC-RS/M** — pilot główny: Żołnierz Red Shoulder — ×4 rekordy źródłowe Entry ID

### Odcinek 28 — Perfect Soldier (`DL728_30`)

**Źródło:** `eventP07.EDAT/DL728_30_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Berserga WP** — pilot główny: Ru Shako
  - **Scopedog RSC (Byman)** — pilot główny: Byman Hagard
  - **Scopedog RSC (Chirico)** — pilot główny: Chirico Cuvie
  - **Scopedog RSC (Gregore)** — pilot główny: Gregore Garosh
  - **Scopedog RSC (Murza)** — pilot główny: Murza Melym
  - **Scopedog TC/ISS (Zaki)** — pilot główny: Gerenborash Droka Zaki

**Jednostki wrogie:**
  - **Blood Sucker** — pilot główny: Żołnierz Red Shoulder — ×8 rekordów źródłowych Entry ID
  - **Blood Sucker (Ypsilon)** — pilot główny: Ypsilon
  - **Scopedog TC-RS** — pilot główny: Żołnierz Red Shoulder — ×2 rekordy źródłowe Entry ID
  - **Scopedog TC-RS/M** — pilot główny: Żołnierz Red Shoulder — ×8 rekordów źródłowych Entry ID

### Odcinek 28 — Przygotowania do rewanżu (`DL728_50`)

**Źródło:** `eventP07.EDAT/DL728_50_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Ultrasaurus** — pilot główny: Rob Herman — piloci wspierający w misji: Moonbay, Karl Lichten Schubaltz

**Jednostki wrogie:**
  - **Dark Horn** — pilot główny: Zoid Core — ×3 rekordy źródłowe Entry ID
  - **Giga Nekton α** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Gun Sniper** — pilot główny: Zoid Core — ×3 rekordy źródłowe Entry ID
  - **Iron Kong** — pilot główny: Zoid Core — ×3 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Zoid Core — ×5 rekordów źródłowych Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×9 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Zoid Core — ×8 rekordów źródłowych Entry ID

### Odcinek 28 — W przededniu decydującej bitwy (`DL728_60`)

**Źródło:** `eventP07.EDAT/DL728_60_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Command Wolf/Khaki** — pilot główny: Zoid Core — ×9 rekordów źródłowych Entry ID
  - **Giga Nekton αα** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Gun Sniper/WW** — pilot główny: Zoid Core — ×15 rekordów źródłowych Entry ID
  - **Iron Kong** — pilot główny: Zoid Core — ×6 rekordów źródłowych Entry ID
  - **Nekton Shooter** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID
  - **Redler** — pilot główny: Zoid Core — ×18 rekordów źródłowych Entry ID
  - **Whale King** — pilot główny: Zoid Core

### Odcinek 29 — Gravity Cannon (`DL729_11`)

**Źródło:** `eventP07.EDAT/DL729_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Blade Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette
  - **Dibison** — pilot główny: Thomas Richard Schubaltz
  - **Lightning Saix** — pilot główny: Irvine
  - **Murasame Liger** — pilot główny: Ruuji Familon
  - **Turner** — pilot główny: Mirawoo Kyao
  - **Ultrasaurus** — pilot główny: Rob Herman — piloci wspierający w misji: Moonbay, Karl Lichten Schubaltz

**Jednostki sojusznicze (NPC):**
  - **Command Wolf/White** — pilot główny: Żołnierz Republiki Helic — ×2 rekordy źródłowe Entry ID

**Jednostki wrogie:**
  - **Dark Horn** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID
  - **Death Stinger** — pilot główny: Hiltz
  - **Giga Nekton α** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Gun Sniper** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID
  - **Iron Kong** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID
  - **Mucus Gate S** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID

### Odcinek 29 — Natarcie Death Stingera (`DL729_12`)

**Źródło:** `eventP07.EDAT/DL729_12_Entry.dat`
**Warunki misji:**
> "Death Stinger" porusza się w specjalny sposób.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Ultrasaurus** — pilot główny: Rob Herman — piloci wspierający w misji: Moonbay, Karl Lichten Schubaltz

**Jednostki wrogie:**
  - **Command Wolf/Khaki** — pilot główny: Zoid Core — ×4 rekordy źródłowe Entry ID
  - **Dark Horn** — pilot główny: Zoid Core — ×4 rekordy źródłowe Entry ID
  - **Death Stinger** — pilot główny: Hiltz
  - **Giga Nekton αα** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Gun Sniper** — pilot główny: Zoid Core — ×4 rekordy źródłowe Entry ID
  - **Iron Kong** — pilot główny: Zoid Core — ×4 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID

**Jednostki neutralne / trzeciej strony:**
  - **Mucus Gate S** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 29 — Zaproszenie z pustki (`DL729_20`)

**Źródło:** `eventP07.EDAT/DL729_20_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Benthos Carrier α** — pilot główny: Mucus
  - **Cowen &amp; Stinger** — pilot główny: Cowen &amp; Stinger
  - **Giga Nekton α** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Giga Nekton αα** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Invader/Air** — pilot główny: Invader — ×4 rekordy źródłowe Entry ID
  - **Invader/Starfish** — pilot główny: Invader — ×4 rekordy źródłowe Entry ID
  - **Mucus Gate S** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine G** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine GG** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×12 rekordów źródłowych Entry ID

### Odcinek 29 — Demon w kraterze (`DL729_50`)

**Źródło:** `eventP07.EDAT/DL729_50_Entry.dat`
**Warunki misji:**
> "Invader (typ Pożeracz)" porusza się w specjalny sposób.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Invader/Air** — pilot główny: Invader — ×5 rekordów źródłowych Entry ID
  - **Invader/Giant Worm** — pilot główny: Invader
  - **Invader/Ground** — pilot główny: Invader — ×5 rekordów źródłowych Entry ID
  - **Metal Beast/Muszla** — pilot główny: Invader — ×6 rekordów źródłowych Entry ID
  - **Metal Beast/Rakieta** — pilot główny: Invader — ×5 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 30 — Pradawne wspomnienia (`DL830_11`)

**Źródło:** `eventP08.EDAT/DL830_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Blade Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: brak (Fiona Elisi Linette poza obsadą na starcie misji)
  - **Dibison** — pilot główny: Thomas Richard Schubaltz
  - **Lightning Saix** — pilot główny: Irvine
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Command Wolf/Khaki** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID
  - **Dark Horn** — pilot główny: Zoid Core — ×3 rekordy źródłowe Entry ID
  - **Death Stinger** — pilot główny: Hiltz
  - **Giga Nekton α** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Gun Sniper** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID
  - **Gun Sniper/WW** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID
  - **Iron Kong** — pilot główny: Zoid Core — ×4 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Zoid Core — ×7 rekordów źródłowych Entry ID
  - **Nekton Shooter** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID

### Odcinek 30 — Nad Eve Polis (`DL830_12`)

**Źródło:** `eventP08.EDAT/DL830_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Benthos Cruiser α** — pilot główny: Mucus
  - **Giga Nekton αα** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine G** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine GG** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×9 rekordów źródłowych Entry ID
  - **Redler** — pilot główny: Zoid Core — ×24 rekordy źródłowe Entry ID
  - **Whale King** — pilot główny: Zoid Core

**Jednostki neutralne / trzeciej strony:**
  - **Whale King** — pilot główny: Oficer Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Whale King** — pilot główny: Oficer Imperium Guylos

### Odcinek 30 — Death Saurer, bestia zagłady (`DL830_13`)

**Źródło:** `eventP08.EDAT/DL830_13_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Blade Liger** — pilot główny: Van Flyheight — piloci wspierający w misji: Fiona Elisi Linette
  - **Dibison** — pilot główny: Thomas Richard Schubaltz
  - **Geno Breaker/Ally** — pilot główny: Raven
  - **Lightning Saix** — pilot główny: Irvine
  - **Ultrasaurus** — pilot główny: Rob Herman — piloci wspierający w misji: Moonbay, Karl Lichten Schubaltz

**Jednostki wrogie:**
  - **Dark Horn** — pilot główny: Zoid Core — ×6 rekordów źródłowych Entry ID
  - **Death Stinger** — pilot główny: Hiltz
  - **Giga Nekton α** — pilot główny: Mucus — ×14 rekordów źródłowych Entry ID
  - **Iron Kong** — pilot główny: Zoid Core — ×6 rekordów źródłowych Entry ID
  - **Molga** — pilot główny: Zoid Core — ×4 rekordy źródłowe Entry ID
  - **Mucus Gate L** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×9 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Nekton Mine G** — pilot główny: Mucus — ×10 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine GG** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Original Death Saurer** — pilot główny: Hiltz
  - **Redler** — pilot główny: Zoid Core — ×7 rekordów źródłowych Entry ID

**Jednostki neutralne / trzeciej strony:**
  - **Mucus Gate L** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Mucus Gate S** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Original Death Saurer** — pilot główny: Dark Kaiser

### Odcinek 30 — Operacja: likwidacja Invaderów (`DL830_40`)

**Źródło:** `eventP08.EDAT/DL830_40_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Benthos Cruiser α** — pilot główny: Mucus
  - **Giga Nekton αα** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Invader/Air** — pilot główny: Invader — ×3 rekordy źródłowe Entry ID
  - **Invader/Ground** — pilot główny: Invader — ×3 rekordy źródłowe Entry ID
  - **Invader/Starfish** — pilot główny: Invader — ×11 rekordów źródłowych Entry ID
  - **Metal Beast/Rakieta** — pilot główny: Invader — ×5 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Mucus Gate L IN** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Mine** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine G** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine GG** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID

### Odcinek 30 — Konsensus (`DL830_50`)

**Źródło:** `eventP08.EDAT/DL830_50_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 1 identyfikator `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Benthos Cruiser α** — pilot główny: Mucus
  - **Giga Nekton α** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Mucus Gate L** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×7 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID — obecny alternatywny rekord Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine G** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine GG** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID — obecny alternatywny rekord Entry ID

### Odcinek 30 — Uruchomienie pierścienia warp (`DL830_60`)

**Źródło:** `eventP08.EDAT/DL830_60_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass
  - **Pancernik kosmiczny klasy Giga** — pilot główny: Oficer Gilgameshu

**Jednostki wrogie:**
  - **Benthos Carrier α** — pilot główny: Mucus
  - **Giga Nekton αα** — pilot główny: Mucus — ×7 rekordów źródłowych Entry ID
  - **Invader/Starfish** — pilot główny: Invader — ×17 rekordów źródłowych Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Mine G** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine GG** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID

### Odcinek 31 — Starcie!! Forteca Invaderów! (`DL831_11`)

**Źródło:** `eventP08.EDAT/DL831_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Shin Getter-1 (Go)** — pilot główny: Go — piloci wspierający w misji: Kei, Gai
  - **Turner** — pilot główny: Mirawoo Kyao
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Cowen &amp; Stinger** — pilot główny: Cowen &amp; Stinger
  - **Giga Nekton αα** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Invader/Air** — pilot główny: Invader — ×2 rekordy źródłowe Entry ID
  - **Invader/Giant Worm** — pilot główny: Invader — ×2 rekordy źródłowe Entry ID
  - **Invader/Ground** — pilot główny: Invader — ×2 rekordy źródłowe Entry ID
  - **Invader/Starfish** — pilot główny: Invader — ×8 rekordów źródłowych Entry ID
  - **Metal Beast/Muszla** — pilot główny: Invader — ×3 rekordy źródłowe Entry ID
  - **Metal Beast/Rakieta** — pilot główny: Invader — ×6 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Mucus Gate L IN** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine GG** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID

### Odcinek 31 — Błysk!! U kresu ewolucji! (`DL831_12`)

**Źródło:** `eventP08.EDAT/DL831_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Shin Getter-1 (Go)** — pilot główny: Go — piloci wspierający w misji: Kei, Gai
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Cowen &amp; Stinger** — pilot główny: Cowen &amp; Stinger — zmiana strony w trakcie misji: neutralna / trzeciej strony
  - **Giga Nekton αα** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Invader/Giant Worm** — pilot główny: Invader — ×2 rekordy źródłowe Entry ID
  - **Invader/Starfish** — pilot główny: Invader — ×22 rekordy źródłowe Entry ID
  - **Metal Beast/Rakieta** — pilot główny: Invader — ×6 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine G** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine GG** — pilot główny: Mucus — ×10 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 31 — Poszukiwania w bramie warp (`DL831_20`)

**Źródło:** `eventP08.EDAT/DL831_20_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki, Vasage

**Jednostki wrogie:**
  - **Giga Nekton α** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×14 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×14 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID
  - **Nekton Mine G** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine GG** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID

### Odcinek 31 — Wojownicy Krainy Mrocznego Smoka (`DL831_30`)

**Źródło:** `eventP08.EDAT/DL831_30_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Okręt eskorty Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka
  - **Żołnierz Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka
  - **Żołnierz Mrocznego Smoka/Lot** — pilot główny: Żołnierz Mrocznego Smoka — ×8 rekordów źródłowych Entry ID
  - **Żołnierz Mrocznego Smoka/Snajper** — pilot główny: Żołnierz Mrocznego Smoka

### Odcinek 31 — Ultrasaurus rusza w kosmos (`DL831_40`)

**Źródło:** `eventP08.EDAT/DL831_40_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Ultrasaurus** — pilot główny: Rob Herman — piloci wspierający w misji: Moonbay, Karl Lichten Schubaltz

**Jednostki wrogie:**
  - **Command Wolf/Khaki** — pilot główny: Zoid Core — ×9 rekordów źródłowych Entry ID
  - **Dark Horn** — pilot główny: Zoid Core — ×3 rekordy źródłowe Entry ID
  - **Gun Sniper** — pilot główny: Zoid Core — ×6 rekordów źródłowych Entry ID
  - **Gun Sniper/WW** — pilot główny: Zoid Core — ×4 rekordy źródłowe Entry ID
  - **Iron Kong** — pilot główny: Zoid Core — ×3 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Zoid Core — ×4 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Zoid Core — ×11 rekordów źródłowych Entry ID

### Odcinek 32 — Galaktyka Recoral (`DL832_11`)

**Źródło:** `eventP08.EDAT/DL832_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Benthos Carrier α** — pilot główny: Mucus
  - **Benthos Cruiser α** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Giga Nekton α** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID
  - **Giga Nekton αα** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×14 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Mine G** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine GG** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID

### Odcinek 32 — Forteca Mucus (`DL832_12`)

**Źródło:** `eventP08.EDAT/DL832_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Benthos Carrier α** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Giga Nekton α** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID
  - **Giga Nekton αα** — pilot główny: Mucus — ×7 rekordów źródłowych Entry ID
  - **Mucus Gate L** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine G** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine GG** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID

### Odcinek 32 — Na pomoc sojusznikom (`DL832_30`)

**Źródło:** `eventP08.EDAT/DL832_30_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Benthos Cruiser α** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Giga Nekton α** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Giga Nekton αα** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×10 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×14 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID
  - **Nekton Mine G** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine GG** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×7 rekordów źródłowych Entry ID

**Jednostki neutralne / trzeciej strony:**
  - **Sarge Aupus** — pilot główny: Oficer armii Posaydala

### Odcinek 32 — Operacja: transport Arki (`DL832_40`)

**Źródło:** `eventP08.EDAT/DL832_40_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Ultrasaurus** — pilot główny: Rob Herman — piloci wspierający w misji: Moonbay, Karl Lichten Schubaltz

**Jednostki wrogie:**
  - **Giga Nekton α** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID
  - **Giga Nekton αα** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×9 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×11 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine G** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine GG** — pilot główny: Mucus — ×5 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID

### Odcinek 33 — Domena harmonii (`DL833_11`)

**Źródło:** `eventP08.EDAT/DL833_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Zmiana obsady oddziału gracza (skrypt `.bin`):** w sekcji 0 skrypt usuwa z obsady maszyny pilota **Seishiro Kusanagi** pilota wspierającego **Vasage**.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass
  - **Vasage** — pilot główny: Vasage — ×2 rekordy źródłowe Entry ID
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Benthos Carrier β** — pilot główny: Mucus
  - **Giga Nekton β** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID
  - **Giga Nekton ββ** — pilot główny: Mucus — ×9 rekordów źródłowych Entry ID

**Jednostki neutralne / trzeciej strony:**
  - **Vasage** — pilot główny: Vasage — ×5 rekordów źródłowych Entry ID

### Odcinek 33 — Gatekeeper (`DL833_12`)

**Źródło:** `eventP08.EDAT/DL833_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Benthos Carrier β** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Giga Nekton β** — pilot główny: Mucus — ×7 rekordów źródłowych Entry ID
  - **Giga Nekton ββ** — pilot główny: Mucus — ×12 rekordów źródłowych Entry ID

### Odcinek 33 — Mgły Genesis (`DL833_50`)

**Źródło:** `eventP08.EDAT/DL833_50_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.
**Uwaga o rekordach alternatywnych:** 3 identyfikatory `Entry ID` posiadają więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass — obecny alternatywny rekord Entry ID
  - **Turner** — pilot główny: Mirawoo Kyao — obecny alternatywny rekord Entry ID
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima — obecny alternatywny rekord Entry ID

**Jednostki wrogie:**
  - **Benthos Carrier α** — pilot główny: Mucus
  - **Benthos Carrier β** — pilot główny: Mucus
  - **Giga Nekton α** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Giga Nekton αα** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Giga Nekton β** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Giga Nekton ββ** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×9 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×9 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Nekton Mine** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine G** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Mine GG** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID

**Jednostki neutralne / trzeciej strony:**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass — obecny alternatywny rekord Entry ID
  - **Pancernik kosmiczny klasy Giga** — pilot główny: Oficer Gilgameshu
  - **Pancernik kosmiczny klasy Lesrion** — pilot główny: Oficer Balarantu
  - **Turner** — pilot główny: Mirawoo Kyao — obecny alternatywny rekord Entry ID
  - **Ultrasaurus** — pilot główny: Rob Herman — piloci wspierający w misji: Moonbay, Karl Lichten Schubaltz
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima — obecny alternatywny rekord Entry ID

### Odcinek 33 — Piekielna bariera przestrzenna (`DL833_60`)

**Źródło:** `eventP08.EDAT/DL833_60_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Ultrasaurus** — pilot główny: Rob Herman — piloci wspierający w misji: Moonbay, Karl Lichten Schubaltz

**Jednostki wrogie:**
  - **Benthos Carrier β** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Giga Nekton β** — pilot główny: Mucus — ×10 rekordów źródłowych Entry ID
  - **Giga Nekton ββ** — pilot główny: Mucus — ×7 rekordów źródłowych Entry ID

### Odcinek 34 — Wtargnięcie do Genesis (`DL834_11`)

**Źródło:** `eventP08.EDAT/DL834_11_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Vasage** — pilot główny: Vasage
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Giga Nekton β** — pilot główny: Mucus — ×15 rekordów źródłowych Entry ID
  - **Giga Nekton ββ** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×15 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×17 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×8 rekordów źródłowych Entry ID
  - **Nekton Mine G** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×10 rekordów źródłowych Entry ID

**Jednostki neutralne / trzeciej strony:**
  - **Mucus Gate S** — pilot główny: Mucus — ×7 rekordów źródłowych Entry ID — zmiana strony w trakcie misji: sojusznicza (NPC) — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 34 — Powierzone nadzieje (`DL834_12`)

**Źródło:** `eventP08.EDAT/DL834_12_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **Gurren Lagann (Simon)** — pilot główny: Simon — piloci wspierający w misji: Kamina, Yoko, Boota
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Benthos Carrier β** — pilot główny: Mucus
  - **Giga Nekton β** — pilot główny: Mucus — ×20 rekordów źródłowych Entry ID
  - **Giga Nekton ββ** — pilot główny: Mucus — ×16 rekordów źródłowych Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×21 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×14 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×10 rekordów źródłowych Entry ID
  - **Nekton Shooter** — pilot główny: Mucus — ×11 rekordów źródłowych Entry ID

**Jednostki neutralne / trzeciej strony:**
  - **Mucus Gate S** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Odcinek 34 — Operation Extend (`DL834_13`)

**Źródło:** `eventP08.EDAT/DL834_13_Entry.dat`
**Warunki misji:**
> "Mucus Arm" porusza się w specjalny sposób.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.
**Uwaga o rekordach alternatywnych:** 1 identyfikator `Entry ID` posiada więcej niż jeden wariant jednostki/pilota/strony; pozycje oznaczone `obecny alternatywny rekord Entry ID` nie oznaczają jednoczesnej obecności.

**Jednostki sojusznicze (gracza):**
  - **Exart** — pilot główny: Seishiro Kusanagi — piloci wspierający w misji: Himari Yaegaki
  - **Gurren Lagann (Simon)** — pilot główny: Simon — piloci wspierający w misji: Kamina, Yoko, Boota
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass — obecny alternatywny rekord Entry ID
  - **Macross Quarter (Storm Attack)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass — obecny alternatywny rekord Entry ID

**Jednostki wrogie:**
  - **Giga Nekton β** — pilot główny: Mucus — ×16 rekordów źródłowych Entry ID
  - **Giga Nekton ββ** — pilot główny: Mucus — ×15 rekordów źródłowych Entry ID
  - **Mucus Arm** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Mucus Emperor** — pilot główny: Mucus
  - **Mucus Emperor/MAX** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Mucus Gate S** — pilot główny: Mucus — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Assault** — pilot główny: Mucus — ×12 rekordów źródłowych Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×10 rekordów źródłowych Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×12 rekordów źródłowych Entry ID
  - **Nekton Mine GG** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nekton Shooter** — pilot główny: Mucus — ×10 rekordów źródłowych Entry ID

### Symulator — Szalejące maszyny (`SM001`)

**Źródło:** `eventP01.EDAT/SM001_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Bolt Robo/Anti-Air** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Bolt Robo/Long-Range** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Bolt Robo/Melee** — pilot główny: Mechabestia — ×3 rekordy źródłowe Entry ID
  - **Bolt Robo/Standard** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Brocken/Melee** — pilot główny: Control AI — ×4 rekordy źródłowe Entry ID
  - **Gandoppler** — pilot główny: Mechabestia — ×3 rekordy źródłowe Entry ID
  - **HAL-X10/Green** — pilot główny: Shinohara HOS — ×2 rekordy źródłowe Entry ID
  - **Helldiver** — pilot główny: Control AI — ×4 rekordy źródłowe Entry ID

### Symulator — Bitwa mobile suitów na lądzie (`SM002`)

**Źródło:** `eventP01.EDAT/SM002_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Dom** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Dom** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Dopp** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Dopp** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Gouf** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Gouf** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Wieżyczka uniwersalna** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Wieżyczka uniwersalna** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zanzibar** — pilot główny: Oficer Zeonu
  - **Zanzibar** — pilot główny: Oficer Zeonu

### Symulator — Grupy zbrojne (`SM003`)

**Źródło:** `eventP20.EDAT/SM003_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki wrogie:**
  - **Brocken/Cannon** — pilot główny: Pilot Labora — ×2 rekordy źródłowe Entry ID
  - **Brocken/Działko automatyczne** — pilot główny: Pilot Labora — ×2 rekordy źródłowe Entry ID
  - **Brocken/Melee** — pilot główny: Pilot Labora — ×4 rekordy źródłowe Entry ID
  - **Dom** — pilot główny: Pilot MS — ×2 rekordy źródłowe Entry ID
  - **Gelgoog** — pilot główny: Pilot MS
  - **Gouf** — pilot główny: Pilot MS — ×2 rekordy źródłowe Entry ID
  - **Griffon** — pilot główny: Badrinath Harchand
  - **HAL-X10** — pilot główny: Pilot Labora — ×2 rekordy źródłowe Entry ID
  - **HAL-X10/Green** — pilot główny: Shinohara HOS — ×2 rekordy źródłowe Entry ID
  - **Helldiver** — pilot główny: Control AI — ×4 rekordy źródłowe Entry ID

### Symulator — Zagrożenia z kosmosu (`SM004`)

**Źródło:** `eventP21.EDAT/SM004_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Bolt Robo/Anti-Air** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Bolt Robo/Long-Range** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Bolt Robo/Melee** — pilot główny: Mechabestia — ×3 rekordy źródłowe Entry ID
  - **Bolt Robo/Standard** — pilot główny: Mechabestia — ×3 rekordy źródłowe Entry ID
  - **Dark Go-Saurer** — pilot główny: Mechabestia
  - **Gandoppler** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Invader/Air** — pilot główny: Invader — ×4 rekordy źródłowe Entry ID
  - **Invader/Ground** — pilot główny: Invader — ×4 rekordy źródłowe Entry ID
  - **Metal Beast/Muszla** — pilot główny: Invader — ×2 rekordy źródłowe Entry ID
  - **Metal Beast/Rakieta** — pilot główny: Invader — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem

### Symulator — Doświadczeni piloci MS (`SM005`)

**Źródło:** `eventP22.EDAT/SM005_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Dom (Black Tri-Stars)** — pilot główny: Gaia
  - **Dom (Black Tri-Stars)** — pilot główny: Mash
  - **Dom (Black Tri-Stars)** — pilot główny: Ortega
  - **Dopp** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Dopp** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Gouf (Ramba Ral)** — pilot główny: Ramba Ral
  - **Kampfer/Bazooka** — pilot główny: Mikhail Kaminsky
  - **Kampfer/High Mobility** — pilot główny: Hardy Steiner
  - **Zaku II (Char)** — pilot główny: Char Aznable
  - **Zaku II Kai** — pilot główny: Andy Strauss
  - **Zaku II Kai** — pilot główny: Gabriel Ramirez Garcia
  - **Zaku II/Bazooka** — pilot główny: Cozun Graham
  - **Zaku II/Bazooka** — pilot główny: Slender
  - **Zaku II/Karabin maszynowy** — pilot główny: Acous
  - **Zaku II/Karabin maszynowy** — pilot główny: Crown
  - **Zanzibar** — pilot główny: Crowley Hamon
  - **Zanzibar** — pilot główny: Garma Zabi
  - **Zanzibar** — pilot główny: M'Quve

### Symulator — Obrona Układu Słonecznego (`SM006`)

**Źródło:** `eventP23.EDAT/SM006_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Bolt Robo/Anti-Air** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Bolt Robo/Long-Range** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Bolt Robo/Melee** — pilot główny: Mechabestia — ×3 rekordy źródłowe Entry ID
  - **Bolt Robo/Standard** — pilot główny: Mechabestia — ×3 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×3 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×3 rekordy źródłowe Entry ID
  - **Daljan** — pilot główny: Gosterro
  - **Dark Go-Saurer** — pilot główny: Mechabestia
  - **Gandoppler** — pilot główny: Mechabestia — ×4 rekordy źródłowe Entry ID
  - **Invader/Air** — pilot główny: Invader — ×3 rekordy źródłowe Entry ID
  - **Invader/Ground** — pilot główny: Invader — ×3 rekordy źródłowe Entry ID
  - **Metal Beast/Muszla** — pilot główny: Invader
  - **Metal Beast/Rakieta** — pilot główny: Invader — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Nowy gigantyczny lotniskowiec Grados** — pilot główny: Oficer Gradosu

### Symulator — Galaktyczne bezprawie (`SM007`)

**Źródło:** `eventP24.EDAT/SM007_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×4 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×2 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×2 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×2 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×2 rekordy źródłowe Entry ID
  - **Death Army** — pilot główny: DG Cells — ×4 rekordy źródłowe Entry ID
  - **Death Bird** — pilot główny: DG Cells — ×4 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×4 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Monskar Medessa** — pilot główny: Monskar — ×3 rekordy źródłowe Entry ID
  - **Monskar Neppoon** — pilot główny: Monskar — ×3 rekordy źródłowe Entry ID
  - **Okręt eskorty Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka
  - **Pancernik kosmiczny klasy Lesrion** — pilot główny: Oficer Balarantu
  - **Żołnierz Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka — ×3 rekordy źródłowe Entry ID
  - **Żołnierz Mrocznego Smoka/Lot** — pilot główny: Żołnierz Mrocznego Smoka — ×3 rekordy źródłowe Entry ID
  - **Żołnierz Mrocznego Smoka/Snajper** — pilot główny: Żołnierz Mrocznego Smoka — ×2 rekordy źródłowe Entry ID

### Symulator — Mieszany oddział AT (`SM008`)

**Źródło:** `eventP25.EDAT/SM008_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Pilot AT — ×4 rekordy źródłowe Entry ID
  - **Brocken/Cannon** — pilot główny: Control AI — ×2 rekordy źródłowe Entry ID
  - **Brocken/Działko automatyczne** — pilot główny: Control AI — ×2 rekordy źródłowe Entry ID
  - **Chaldea** — pilot główny: Control AI — ×4 rekordy źródłowe Entry ID
  - **Fatty (Ground)** — pilot główny: Pilot AT — ×4 rekordy źródłowe Entry ID
  - **HAL-X10/Green** — pilot główny: Control AI — ×4 rekordy źródłowe Entry ID
  - **Helldiver** — pilot główny: Control AI — ×4 rekordy źródłowe Entry ID
  - **Lądowy pancernik Balarant** — pilot główny: Oficer Gilgameshu
  - **Scopedog** — pilot główny: Pilot AT — ×4 rekordy źródłowe Entry ID
  - **Scopedog** — pilot główny: Żołnierz Gilgameshu — ×4 rekordy źródłowe Entry ID
  - **Scopedog RS (Riemann)** — pilot główny: Inge Riemann
  - **Scopedog TC-RS** — pilot główny: Żołnierz Red Shoulder — ×4 rekordy źródłowe Entry ID
  - **Scopedog TC-RS/M** — pilot główny: Żołnierz Red Shoulder — ×2 rekordy źródłowe Entry ID
  - **Scopedog/M** — pilot główny: Pilot AT — ×2 rekordy źródłowe Entry ID
  - **Scopedog/M** — pilot główny: Żołnierz Gilgameshu — ×2 rekordy źródłowe Entry ID

### Symulator — Koszmar Ziemi (`SM009`)

**Źródło:** `eventP26.EDAT/SM009_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Bolt Robo/Anti-Air** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Bolt Robo/Long-Range** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Bolt Robo/Melee** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Bolt Robo/Standard** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Chaldea** — pilot główny: Control AI — ×8 rekordów źródłowych Entry ID
  - **Dark Go-Saurer** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Death Army** — pilot główny: DG Cells — ×2 rekordy źródłowe Entry ID
  - **Death Bird** — pilot główny: DG Cells — ×2 rekordy źródłowe Entry ID
  - **Gandoppler** — pilot główny: Mechabestia — ×7 rekordów źródłowych Entry ID
  - **HAL-X10/Green** — pilot główny: Control AI — ×2 rekordy źródłowe Entry ID
  - **Helldiver** — pilot główny: Control AI — ×2 rekordy źródłowe Entry ID
  - **Invader/Air** — pilot główny: Invader — ×3 rekordy źródłowe Entry ID
  - **Invader/Ground** — pilot główny: Invader — ×3 rekordy źródłowe Entry ID
  - **Metal Beast/Muszla** — pilot główny: Invader — ×2 rekordy źródłowe Entry ID
  - **Metal Beast/Rakieta** — pilot główny: Invader — ×3 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Seryjny Metal Knight** — pilot główny: Metal Knight — ×7 rekordów źródłowych Entry ID
  - **Seryjny Metal Knight/Ciężki** — pilot główny: Metal Knight — ×7 rekordów źródłowych Entry ID

### Symulator — Legion Zoidów (`SM010`)

**Źródło:** `eventP27.EDAT/SM010_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Command Wolf/Khaki** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID
  - **Command Wolf/Khaki** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID
  - **Dark Horn** — pilot główny: Żołnierz Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Dark Horn** — pilot główny: Żołnierz Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Death Saurer/Replica** — pilot główny: Gunther Prozen
  - **Geno Breaker** — pilot główny: Raven
  - **Giga Nekton α** — pilot główny: Mucus
  - **Gun Sniper** — pilot główny: Pilot Zoida
  - **Gun Sniper** — pilot główny: Pilot Zoida
  - **Gun Sniper/WW** — pilot główny: Pilot Zoida
  - **Gun Sniper/WW** — pilot główny: Pilot Zoida
  - **Iron Kong** — pilot główny: Oficer Imperium Guylos — ×3 rekordy źródłowe Entry ID
  - **Iron Kong** — pilot główny: Oficer Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Iron Kong SS** — pilot główny: Karl Lichten Schubaltz
  - **Molga** — pilot główny: Żołnierz Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Żołnierz Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Nekton Shooter** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Red Horn (Rosso)** — pilot główny: Rosso
  - **Redler** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Żołnierz Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Żołnierz Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Redler (Viola)** — pilot główny: Viola
  - **Whale King** — pilot główny: Oficer Imperium Guylos
  - **Whale King** — pilot główny: Oficer Imperium Guylos

### Symulator — Mnożące się maszyny bojowe (`SM011`)

**Źródło:** `eventP28.EDAT/SM011_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki wrogie:**
  - **Bolt Robo/Long-Range** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Bolt Robo/Standard** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Brocken/Cannon** — pilot główny: Control AI — ×2 rekordy źródłowe Entry ID
  - **Brocken/Działko automatyczne** — pilot główny: Control AI — ×2 rekordy źródłowe Entry ID
  - **Chaldea** — pilot główny: Control AI — ×2 rekordy źródłowe Entry ID
  - **Dark Go-Saurer** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Death Army** — pilot główny: DG Cells — ×16 rekordów źródłowych Entry ID
  - **Death Bird** — pilot główny: DG Cells — ×2 rekordy źródłowe Entry ID
  - **Gundam Head** — pilot główny: DG Cells
  - **Invader/Ground** — pilot główny: Invader — ×2 rekordy źródłowe Entry ID
  - **Metal Beast/Rakieta** — pilot główny: Invader — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Seryjny Metal Knight** — pilot główny: Metal Knight — ×3 rekordy źródłowe Entry ID
  - **Seryjny Metal Knight/Ciężki** — pilot główny: Metal Knight — ×2 rekordy źródłowe Entry ID
  - **Type-Zero/Wróg** — pilot główny: Control AI — ×2 rekordy źródłowe Entry ID

### Symulator — Bohaterowie walk lądowych (`SM012`)

**Źródło:** `eventP29.EDAT/SM012_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Dark Horn** — pilot główny: Żołnierz Imperium Guylos — ×2 rekordy źródłowe Entry ID
  - **Directional Mine** — pilot główny: Control AI — ×8 rekordów źródłowych Entry ID
  - **Dom (Black Tri-Stars)** — pilot główny: Gaia
  - **Dom (Black Tri-Stars)** — pilot główny: Mash
  - **Dom (Black Tri-Stars)** — pilot główny: Ortega
  - **Dopp** — pilot główny: Żołnierz Zeonu — ×3 rekordy źródłowe Entry ID
  - **Dopp** — pilot główny: Żołnierz Zeonu — ×9 rekordów źródłowych Entry ID
  - **Dreissen** — pilot główny: Desert Rommel
  - **Endra** — pilot główny: Oficer Neo Zeonu
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu — ×3 rekordy źródłowe Entry ID
  - **Gouf (Ramba Ral)** — pilot główny: Ramba Ral
  - **Iron Kong SS** — pilot główny: Karl Lichten Schubaltz
  - **Kampfer/Bazooka** — pilot główny: Mikhail Kaminsky
  - **Kampfer/High Mobility** — pilot główny: Hardy Steiner
  - **Lancelot** — pilot główny: Suzaku Kururugi
  - **Molga** — pilot główny: Żołnierz Imperium Guylos — ×4 rekordy źródłowe Entry ID
  - **Red Horn (Rosso)** — pilot główny: Rosso
  - **Redler** — pilot główny: Żołnierz Imperium Guylos — ×4 rekordy źródłowe Entry ID
  - **Redler (Viola)** — pilot główny: Viola
  - **Saber Tiger (Raven)** — pilot główny: Raven
  - **Scopedog RS (Riemann)** — pilot główny: Inge Riemann
  - **Scopedog TC-RS** — pilot główny: Żołnierz Red Shoulder — ×3 rekordy źródłowe Entry ID
  - **Scopedog TC-RS/M** — pilot główny: Żołnierz Red Shoulder — ×2 rekordy źródłowe Entry ID
  - **Whale King** — pilot główny: Gunther Prozen
  - **Zaku II Kai** — pilot główny: Andy Strauss
  - **Zaku II Kai** — pilot główny: Gabriel Ramirez Garcia
  - **Zaku II/Bazooka** — pilot główny: Cozun Graham
  - **Zaku II/Karabin maszynowy** — pilot główny: Acous
  - **Zaku III** — pilot główny: Żołnierz Neo Zeonu — ×4 rekordy źródłowe Entry ID
  - **Zanzibar** — pilot główny: Crowley Hamon

### Symulator — Mieszane siły mobilne (`SM013`)

**Źródło:** `eventP30.EDAT/SM013_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×3 rekordy źródłowe Entry ID
  - **Bat-Shu** — pilot główny: Posaydal Regular — ×3 rekordy źródłowe Entry ID
  - **Bat-Shu/Strong** — pilot główny: Gavlet Gablae
  - **Bat-Shu/Strong** — pilot główny: Hatchia Motchia
  - **Braver** — pilot główny: Żołnierz Gradosu — ×7 rekordów źródłowych Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×7 rekordów źródłowych Entry ID
  - **Daljan** — pilot główny: Gosterro
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×9 rekordów źródłowych Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×4 rekordy źródłowe Entry ID
  - **Nowy gigantyczny lotniskowiec Grados** — pilot główny: Oficer Gradosu
  - **Pancernik kosmiczny klasy Lesrion** — pilot główny: Oficer Balarantu
  - **Sarge Aupus** — pilot główny: Oficer armii Posaydala
  - **Slender Skala** — pilot główny: Oficer armii Posaydala
  - **Zakarl** — pilot główny: Le Cain

### Symulator — Skradziony Księżyc (`SM014`)

**Źródło:** `eventP31.EDAT/SM014_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Giga Nekton α** — pilot główny: Mucus
  - **Giga Nekton αα** — pilot główny: Mucus
  - **Invader/Air** — pilot główny: Invader — ×5 rekordów źródłowych Entry ID
  - **Invader/Ground** — pilot główny: Invader — ×4 rekordy źródłowe Entry ID
  - **Invader/Starfish** — pilot główny: Invader — ×11 rekordów źródłowych Entry ID
  - **Metal Beast/Muszla** — pilot główny: Invader — ×3 rekordy źródłowe Entry ID
  - **Metal Beast/Rakieta** — pilot główny: Invader — ×2 rekordy źródłowe Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Monskar Medessa** — pilot główny: Monskar — ×4 rekordy źródłowe Entry ID
  - **Monskar Neppoon** — pilot główny: Monskar — ×4 rekordy źródłowe Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Creek** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Nekton Hauser** — pilot główny: Mucus — ×4 rekordy źródłowe Entry ID
  - **Nekton Shooter** — pilot główny: Mucus — ×3 rekordy źródłowe Entry ID
  - **Okręt eskorty Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka
  - **Żołnierz Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka — ×3 rekordy źródłowe Entry ID
  - **Żołnierz Mrocznego Smoka/Lot** — pilot główny: Żołnierz Mrocznego Smoka — ×4 rekordy źródłowe Entry ID
  - **Żołnierz Mrocznego Smoka/Snajper** — pilot główny: Żołnierz Mrocznego Smoka — ×3 rekordy źródłowe Entry ID

### Symulator — Walka z Laborami i AT (`SM015`)

**Źródło:** `eventP31.EDAT/SM015_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki wrogie:**
  - **Brocken/Cannon** — pilot główny: Pilot Labora — ×2 rekordy źródłowe Entry ID
  - **Brocken/Działko automatyczne** — pilot główny: Pilot Labora — ×2 rekordy źródłowe Entry ID
  - **Chaldea** — pilot główny: Control AI — ×11 rekordów źródłowych Entry ID
  - **Command Wolf/White** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID
  - **Fatty (Ground)** — pilot główny: Pilot AT — ×2 rekordy źródłowe Entry ID
  - **Griffon** — pilot główny: Badrinath Harchand
  - **Gun Sniper** — pilot główny: Zoid Core — ×4 rekordy źródłowe Entry ID
  - **Gun Sniper/WW** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID
  - **HAL-X10** — pilot główny: Shinohara HOS — ×3 rekordy źródłowe Entry ID
  - **HAL-X10/Green** — pilot główny: Pilot Labora — ×2 rekordy źródłowe Entry ID
  - **Helldiver** — pilot główny: Control AI — ×5 rekordów źródłowych Entry ID
  - **Scopedog** — pilot główny: Pilot AT — ×4 rekordy źródłowe Entry ID
  - **Scopedog/M** — pilot główny: Pilot AT — ×3 rekordy źródłowe Entry ID
  - **Type-Zero/Wróg** — pilot główny: Shinohara HOS — ×4 rekordy źródłowe Entry ID

### Symulator — Szturm Dark Attackera (`SM016`)

**Źródło:** `eventP31.EDAT/SM016_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Macross Quarter (forteca)** — pilot główny: Jeffrey Wilder — piloci wspierający w misji: Bobby Margot, Catherine Glass

**Jednostki wrogie:**
  - **Bat-Shu/Strong** — pilot główny: Antoon Randow
  - **Bat-Shu/Strong** — pilot główny: Gavlet Gablae
  - **Bat-Shu/Strong** — pilot główny: Hatchia Motchia
  - **Bat-Shu/Strong** — pilot główny: Hekeler Mauzer
  - **Bolt Robo/Anti-Air** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Bolt Robo/Melee** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Dark Go-Saurer** — pilot główny: Mechabestia — ×2 rekordy źródłowe Entry ID
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Giga Nekton α** — pilot główny: Mucus — ×2 rekordy źródłowe Entry ID
  - **Iron Kong** — pilot główny: Zoid Core — ×2 rekordy źródłowe Entry ID
  - **Monskar Medessa** — pilot główny: Monskar — ×2 rekordy źródłowe Entry ID
  - **Monskar Neppoon** — pilot główny: Monskar — ×8 rekordów źródłowych Entry ID
  - **Nekton Assault** — pilot główny: Mucus — ×6 rekordów źródłowych Entry ID
  - **Qubeley Mk-II (Ple Two)** — pilot główny: Ple Two
  - **Qubeley Mk-II (Ple)** — pilot główny: Elpeo Ple
  - **Queen Cideron** — pilot główny: Da Cider
  - **Saber Tiger (Raven)** — pilot główny: Raven
  - **Susanowo** — pilot główny: Mr. Bushido
  - **Zwarth** — pilot główny: Black Knight

### Symulator — Zeon na lądzie - trening (`SM017`)

**Źródło:** `eventP31.EDAT/SM017_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **Apsalus III** — pilot główny: Ginias Sahalin
  - **Dom** — pilot główny: Żołnierz Zeonu — ×3 rekordy źródłowe Entry ID
  - **Dom** — pilot główny: Żołnierz Zeonu — ×3 rekordy źródłowe Entry ID
  - **Dom (Black Tri-Stars)** — pilot główny: Gaia
  - **Dom (Black Tri-Stars)** — pilot główny: Mash
  - **Dom (Black Tri-Stars)** — pilot główny: Ortega
  - **Dopp** — pilot główny: Żołnierz Zeonu — ×6 rekordów źródłowych Entry ID
  - **Dopp** — pilot główny: Żołnierz Zeonu — ×6 rekordów źródłowych Entry ID
  - **Gelgoog** — pilot główny: Crown
  - **Gelgoog** — pilot główny: Slender
  - **Gelgoog** — pilot główny: Żołnierz Zeonu
  - **Gelgoog** — pilot główny: Żołnierz Zeonu
  - **Gouf** — pilot główny: Acous
  - **Gouf** — pilot główny: Cozun Graham
  - **Gouf** — pilot główny: Żołnierz Zeonu — ×3 rekordy źródłowe Entry ID
  - **Gouf** — pilot główny: Żołnierz Zeonu — ×3 rekordy źródłowe Entry ID
  - **Gouf (Ramba Ral)** — pilot główny: Ramba Ral
  - **Zaku II/Bazooka** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zaku II/Karabin maszynowy** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Zanzibar** — pilot główny: Char Aznable
  - **Zanzibar** — pilot główny: Crowley Hamon
  - **Zanzibar** — pilot główny: Garma Zabi
  - **Zanzibar** — pilot główny: M'Quve

### Symulator — Strefa bezprawia (`SM018`)

**Źródło:** `eventP32.EDAT/SM018_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **Ultrasaurus** — pilot główny: Rob Herman — piloci wspierający w misji: Moonbay, Karl Lichten Schubaltz

**Jednostki wrogie:**
  - **Blood Sucker** — pilot główny: Żołnierz Red Shoulder — ×3 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×4 rekordy źródłowe Entry ID
  - **Braver** — pilot główny: Żołnierz Gradosu — ×4 rekordy źródłowe Entry ID
  - **Brocken/Cannon** — pilot główny: Pilot Labora — ×3 rekordy źródłowe Entry ID
  - **Brocken/Działko automatyczne** — pilot główny: Pilot Labora — ×4 rekordy źródłowe Entry ID
  - **Command Wolf/Khaki** — pilot główny: Pilot Zoida — ×3 rekordy źródłowe Entry ID
  - **Daljan** — pilot główny: Gosterro
  - **Dark Horn** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID
  - **Dom** — pilot główny: Pilot MS — ×4 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Pilot AT — ×2 rekordy źródłowe Entry ID
  - **Fatty (Ground)** — pilot główny: Pilot AT — ×4 rekordy źródłowe Entry ID
  - **Gouf** — pilot główny: Pilot MS — ×2 rekordy źródłowe Entry ID
  - **Gun Sniper** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID
  - **Molga** — pilot główny: Pilot Zoida — ×3 rekordy źródłowe Entry ID
  - **Redler** — pilot główny: Pilot Zoida — ×2 rekordy źródłowe Entry ID
  - **Scopedog** — pilot główny: Pilot AT — ×4 rekordy źródłowe Entry ID
  - **Scopedog TC-RS** — pilot główny: Żołnierz Red Shoulder — ×4 rekordy źródłowe Entry ID
  - **Scopedog TC-RS/M** — pilot główny: Żołnierz Red Shoulder — ×3 rekordy źródłowe Entry ID
  - **Scopedog/M** — pilot główny: Pilot AT — ×4 rekordy źródłowe Entry ID
  - **Zaku II Kai** — pilot główny: Pilot MS — ×3 rekordy źródłowe Entry ID

### Symulator — Zeon w kosmosie - trening (`SM019`)

**Źródło:** `eventP32.EDAT/SM019_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki sojusznicze (gracza):**
  - **White Base** — pilot główny: Bright Noa — piloci wspierający w misji: Mirai Yashima

**Jednostki wrogie:**
  - **B-FH-14/Myśliwiec dwuzadaniowy** — pilot główny: Żołnierz Balarantu — ×6 rekordów źródłowych Entry ID
  - **Big Zam** — pilot główny: Dozle Zabi
  - **Bigro** — pilot główny: Tokwan
  - **Braver** — pilot główny: Żołnierz Gradosu — ×3 rekordy źródłowe Entry ID
  - **Dreissen** — pilot główny: Desert Rommel
  - **Dreissen** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Endra** — pilot główny: Rakan Dahkaran
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty** — pilot główny: Żołnierz Balarantu — ×2 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu — ×4 rekordy źródłowe Entry ID
  - **Fatty/Na okręty** — pilot główny: Żołnierz Balarantu
  - **Gattle** — pilot główny: Żołnierz Zeonu — ×4 rekordy źródłowe Entry ID
  - **Gaza-C** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Gaza-C/MA** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Gelgoog** — pilot główny: Żołnierz Zeonu — ×2 rekordy źródłowe Entry ID
  - **Gwazine** — pilot główny: Gihren Zabi
  - **Kampfer/Bazooka** — pilot główny: Andy Strauss
  - **Kampfer/Bazooka** — pilot główny: Mikhail Kaminsky
  - **Kampfer/High Mobility** — pilot główny: Gabriel Ramirez Garcia
  - **Kampfer/High Mobility** — pilot główny: Hardy Steiner
  - **Qubeley** — pilot główny: Haman Karn
  - **Qubeley Mk-II (Ple Two)** — pilot główny: Ple Two
  - **Qubeley Mk-II (Ple)** — pilot główny: Elpeo Ple
  - **Rick Dom** — pilot główny: Żołnierz Zeonu
  - **Rick Dom** — pilot główny: Żołnierz Zeonu
  - **Rick Dom (Black Tri-Stars)** — pilot główny: Gaia
  - **Rick Dom (Black Tri-Stars)** — pilot główny: Mash
  - **Rick Dom (Black Tri-Stars)** — pilot główny: Ortega
  - **Sadalahn** — pilot główny: Haman Karn
  - **Zaku III** — pilot główny: Żołnierz Neo Zeonu — ×2 rekordy źródłowe Entry ID
  - **Zaku III (Rakan)** — pilot główny: Rakan Dahkaran
  - **Zeong** — pilot główny: Char Aznable

### Symulator — Wijąca się ziemia (`SM020`)

**Źródło:** `eventP32.EDAT/SM020_Entry.dat`
**Warunki misji:**
> "Invader (typ Pożeracz)" porusza się w specjalny sposób.
**Fale i moment wejścia:** poza powyższą adnotacją kolejność fal i numery tur zależą od wyzwalaczy skryptu.

**Jednostki sojusznicze (gracza):**
  - **Turner** — pilot główny: Mirawoo Kyao

**Jednostki wrogie:**
  - **Death Army** — pilot główny: DG Cells — ×3 rekordy źródłowe Entry ID
  - **Death Bird** — pilot główny: DG Cells — ×3 rekordy źródłowe Entry ID
  - **Gandoppler** — pilot główny: Mechabestia — ×3 rekordy źródłowe Entry ID
  - **Invader/Air** — pilot główny: Invader — ×3 rekordy źródłowe Entry ID
  - **Invader/Giant Worm** — pilot główny: Invader — ×3 rekordy źródłowe Entry ID
  - **Invader/Ground** — pilot główny: Invader — ×6 rekordów źródłowych Entry ID
  - **Metal Beast/Muszla** — pilot główny: Invader — ×2 rekordy źródłowe Entry ID
  - **Metal Beast/Rakieta** — pilot główny: Invader — ×6 rekordów źródłowych Entry ID — cel/obiekt skryptowy; nie jest pilotowanym mechem
  - **Molga** — pilot główny: Zoid Core — ×3 rekordy źródłowe Entry ID
  - **Monskar Medessa** — pilot główny: Monskar — ×3 rekordy źródłowe Entry ID
  - **Monskar Neppoon** — pilot główny: Monskar — ×3 rekordy źródłowe Entry ID
  - **Seryjny Metal Knight** — pilot główny: Metal Knight — ×3 rekordy źródłowe Entry ID
  - **Seryjny Metal Knight/Ciężki** — pilot główny: Metal Knight — ×3 rekordy źródłowe Entry ID
  - **Żołnierz Mrocznego Smoka** — pilot główny: Żołnierz Mrocznego Smoka — ×3 rekordy źródłowe Entry ID
  - **Żołnierz Mrocznego Smoka/Lot** — pilot główny: Żołnierz Mrocznego Smoka — ×3 rekordy źródłowe Entry ID
  - **Żołnierz Mrocznego Smoka/Snajper** — pilot główny: Żołnierz Mrocznego Smoka — ×3 rekordy źródłowe Entry ID

### Symulator — Wojna watażków (`SM021`)

**Źródło:** `eventP32.EDAT/SM021_Entry.dat`
**Fale i moment wejścia:** nieokreślone w nocie misji; zależne od wyzwalaczy skryptu `.bin`.

**Jednostki wrogie:**
  - **Aug** — pilot główny: True Posaydal
  - **Auge** — pilot główny: Nei Moh Han
  - **Blood Sucker (Ypsilon)** — pilot główny: Ypsilon
  - **Daljan** — pilot główny: Gosterro
  - **Enkidu** — pilot główny: Viral
  - **Gelgoog (Char)** — pilot główny: Char Aznable
  - **Geno Breaker** — pilot główny: Raven
  - **Gouf (Ramba Ral)** — pilot główny: Ramba Ral
  - **Griffon** — pilot główny: Badrinath Harchand
  - **Iron Kong SS** — pilot główny: Karl Lichten Schubaltz
  - **Lancelot** — pilot główny: Suzaku Kururugi
  - **Qubeley** — pilot główny: Haman Karn
  - **Queen Cideron** — pilot główny: Da Cider
  - **Quin Mantha** — pilot główny: Ple Two
  - **Scopedog RS (Riemann)** — pilot główny: Inge Riemann
  - **Susanowo** — pilot główny: Mr. Bushido
  - **Tallgeese** — pilot główny: Zechs Merquise
  - **Zakarl** — pilot główny: Le Cain
  - **Zaku III (Rakan)** — pilot główny: Rakan Dahkaran
  - **Zwarth/Hyper** — pilot główny: Black Knight

## Wykluczone obiekty użytkowe mapy

- **Container (`unit_id = 3670`):** 184 rekordy źródłowe we wszystkich zbadanych plikach `_Entry.dat`; wyłączone z list bojowych jako obiekty użytkowe mapy.
- **Moduł naprawy (`unit_id = 3660`):** 35 rekordów źródłowych we wszystkich zbadanych plikach `_Entry.dat`; wyłączone z list bojowych jako obiekty użytkowe mapy.

## Pochodzenie danych i weryfikacja

- Rozmieszczenia pochodzą bezpośrednio z plików `_Entry.dat`, a aktywne składy załóg wspierających i zmiany stron w trakcie misji — z dezasemblacji `DATA.PSP` wersji 1.08 (`0x1f9810`, `0x202a68..0x202c1c`, `0x214688..0x2146e0`, `0x1d9500..0x1d96dc`) oraz analizy wszystkich 226 skryptów `.bin` (`op 300`, `op 318`, `op 516`, `op 519`, `op 679`).
- Polskie nazwy maszyn, postaci, tytułów misji oraz warunków pochodzą wyłącznie ze zweryfikowanego pakietu `pakiet_PL` (`05_mission_text.jsonl`, `07_names_characters.jsonl`, `08_names_units_weapons.jsonl`).
- Zachowano osobno oba duplikaty kodów między pakietami (`DL103_30` w `eventP01.EDAT` i `eventP09.EDAT`; `DL208_30` w `eventP13.EDAT` i `eventP22.EDAT`).

## Przykłady weryfikacji obsady w tym katalogu

- **Exart (`unit_id = 3900`, pilot główny: Seishiro Kusanagi):** w `DL100_01` i `DL100_02` nie ma jeszcze żadnych pilotów wspierających (`flag[1075] = 0`); od `DL101_11` do `DL310_12` jedynym aktywnym pilotem wspierającym jest **Himari Yaegaki** (`Vasage` nie figuruje w załodze); w `DL310_20` **Vasage** dołącza w trakcie misji (sekcja 2, `op 679` + `flag[1112] = 1`); od `DL311_12` do `DL831_20` aktywni są **Himari Yaegaki, Vasage**; po odłączeniu w `DL833_11` (`op 318(1112, 0)` + `op 516`), w finałowych `DL834_12` i `DL834_13` ponownie aktywna jest wyłącznie **Himari Yaegaki**.
- **Blade Liger (`unit_id = 3203`, pilot główny: Van Flyheight):** standardowo ma aktywną **Fionę Elisi Linette**, natomiast w `DL830_11` skrypt sekcji 0 (`op 516(-4101, 4105)`) oraz kod fuzji Zeke (`0x214688..0x2146e0`) usuwają ją z obsady na czas tej misji (`brak`).
- **White Base (`unit_id = 1090`, pilot główny: Bright Noa):** pętla `0x202b80..0x202bd8` w każdej misji z udziałem White Base aktywuje **Mirai Yashimę** jako pilota wspierającego (brak jakichkolwiek wywołań `op 516` usuwających `1209` w skryptach gry).
