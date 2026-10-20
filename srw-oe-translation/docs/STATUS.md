# Project status

**PL4 partial return integrated and v2.7-PL4 kit delivered (2026-10-20).**
[Download](https://drive.google.com/file/d/1T4EPs_7fbJEyAVLIdCmDYLkEtNcWFViF/view);
All nine views plus episodes00–21: strict import67,143 explicit blocks,0 errors,
0 stale/unknown/duplicate,exact roundtrip.1,283 existing owner-UI source bindings
plus32 mission rows retained;57 translator correction-file entries round-trip.
Episodes00–21 contain28,078/28,079 PL visible entries (one whitespace-only
structural blank). Package validator:87,794/109,176 filled,0 hard errors/25,165
soft warnings. New PL4 rows map only to25 DLC EDAT names; originals unavailable
in this sandbox, so actual physical build/DLC output/runtime remains unverified.
Episodes22–34 and simulator remain unfinished. See
[PL4 audit](pl/PL4_RETURN_REVIEW.md); keep UI/protagonist/cache/font corrections.

**PL UI v2.6 delivered (2026-10-20):** seven owner screenshots addressed in one
text-only batch, all527mission title fields checked/read back,10missing base
copies filled, all20Spirit families compact-name reviewed.1724tests OK/2skip;
cache/font unchanged, new runtime layout confirmation pending. For current owner
PPSSPP1.20.4 upgrade: ISOYES/DLCNO/PBOOTNO recopy.
[Download](https://drive.google.com/file/d/1ZYLUYsDd97K1itqHGDqQQTDgX33wGVQg/view),
[scope/proof](pl/UI_SIX_2026-10-20.md). Older releases below are history.

**PL3 release (2026-10-19):** partial standalone PL patcher delivered from actual
PL3.zip. Quotes19841/19841, all editable visible views filled (protected/binary
blanks preserved), scenes00–03 fully filled after copies.0 import/validation errors;
634 leading spaces preserved;48326 explicit MD blocks compared after propagation,
0 mismatches. **Physical Skill00215764B (1004B margin)**,8 DLC pools15329B each
(309B margin), extracted-kit CLI on authentic-container NONPLAYABLE fixture0problems.
[Download PL patcher](https://drive.google.com/file/d/1jkVKOzRyy8QE58elwLqezi19-iNXRNGq/view).
EN+PL workflow now tested successfully on GitHub Actions; publishes BOTH only
on main after merge, not from PR. Source-bound PL text snapshot tracked, no Drive
secrets/game data in CI. **PR20 still open; main publication awaits merge.**
1644 tests OK/25 skipped. Quote gender/158 formatting findings/later story/runtime
QA remain open; not a literary/full-game approval. This supersedes PL2's686B
blocker below. See [PL3_RELEASE.md](pl/PL3_RELEASE.md) and its delivery receipt.

**PL2 return (2026-10-18):** audited actual PL2.zip. Leading spaces preserved in
all 634 config fields; all 33 prior join suspects corrected in 1421 format previews.
**Skill00 remains 217454 B vs 216768 (+686 B)**; normal builder refuses it,
no bypass/new oversized test. All eight physical DLC pools build/read back at
15331 B each (307 B margin). Delivered quotes are **11801/19841**, not reported
13460 — request newest MD export before further edits. One glossary full/short
variant to review, no import errors. Fixed EN-only chapter-4 DLC readback for PL.
1626 tests OK/27 skipped; no playable ISO/runtime claim. See
[PL2_RETURN_REVIEW.md](pl/PL2_RETURN_REVIEW.md). Keep translator's literary work;
next: latest MD export and remaining ≥686 B of actual Skill00 savings.

**Masaki v17 update (2026-10-18):** delivered-kit reproduction confirms the
reported JP/EN mix in the config19 dictionary while imenu19 is fully EN. The
global config-side viewer safety gate is the cause of those held-back fields;
not missing translator work. A private existing-cell-only TEST1 for three
characters is delivered and owner-confirmed ("wszystko pięknie przetłumaczone").
Narrow integration is now active automatically in the normal shared **EN and PL**
builder; global gate stays enabled elsewhere. The EN container is byte-identical
to accepted TEST1; PL uses its own source-stamped returned fields (no EN fallback).
[Tools-only updater](https://drive.google.com/file/d/1ssmlgTfscMTp-da2Ou_2t3STjua6h-f2/view)
for both existing kits is delivered; no translations/launchers/game files included.
1620 tests OK/28 skipped; isolated updated-kit EN/PL builds and independent
original-DLC readback pass. No playable ISO/full-game QA here. See
[QA_MASAKI_V17.md](QA_MASAKI_V17.md) and [delivery receipt](masaki-builder-update-delivery.json).

**V5 runtime update (2026-10-18): owner accepts the font on two opening
narration/dialogue screenshots, with no further styling objections.** Missing
Ł/Ś (also Ó) in all-caps headings were ASCII caption literals in the exact delivered
ZIP, not a font defect. Source captions corrected; font/codec unchanged. No new
font build/test requested. [Details](pl/PL_FONT_STYLE.md). Older pending notes below
refer to the state at delivery, not the latest feedback.

**Translator PL audit complete (2026-10-18, PR #20).** Replace the old
`sceny_PL.zip` / `widoki_PL.zip` with checked **v2** archives linked in
[`pl/TRANSLATOR_VIEWS_AUDIT.md`](pl/TRANSLATOR_VIEWS_AUDIT.md).
All 109144 extracted text rows classified: 108761 editable/inherited, 19 protected,
364 unclassified leftovers quarantined (8 necessary leftover roots retained).
Full synthetic PL import/copy/check/build-load passed; 1591 tests OK, 25 skipped.
Tools from `0053e01` or newer are required; use `--lang pl --require-template`.
Next: external translator fills PL only; later validate returned text and runtime
layout. No literary PL translation done; **v5 opening-screen appearance now accepted by owner**.
Manifest: [`pl/translator-views-v2-delivery.json`](pl/translator-views-v2-delivery.json).

Last updated: 2026-10-18 (PL v4 runtime/style feedback; native font v5 — PR #20)

**Najnowsze PL: v4 działa; [TEST_PL v5](https://drive.google.com/file/d/13tWWoHO6nBSmEVGFj4y46BtDIV2kz3uD/view) dopasowuje styl fontu.**
Cztery zrzuty właściciela pokazują działający tekst w narracji, dialogu, tytule
sceny i nazwie jednostki; uwagi o grubości i wysokości potwierdzone pomiarem bitmap.
V5 nie rasteruje Roboto: kopiuje korpusy ASCII z własnego oryginalnego fontu gry
podczas budowy i dodaje tylko małe maski diakrytyków. Bez skalowania, przesuwania
ani pogrubienia; źródłowe ASCII bez zmian. Korpusy i krycie sprawdzane niezależnym
odczytem ISO, żadne bitmapy gry/pochodne JSON nie są w Git ani w paczce.
1569 unittest OK (25 skipped), wydany ZIP wypakowany i jego CLI sprawdzone na fixture
ISO z oryginalnymi kontenerami; Drive download-back identyczny. Teksty v4 zachowane
(poza etykietami wersji). **V5 nie uruchomiono tu w PPSSPP; wygląd runtime oczekuje
oceny**, czego nie zastępuje potwierdzenie v4. [Dowody stylu](pl/PL_FONT_STYLE.md),
[manifest v5](pl/test-v5-delivery.json). Starsze stany poniżej są historią.

**Najnowsze PL: v3 potwierdzony na zrzutach właściciela; [TEST_PL v4](https://drive.google.com/file/d/1ic0N5bx0PMF_3xnu2ZWhlG0e3nOQRc-U/view) dostarczony.**
Właściciel ocenił font pozytywnie i poprosił o naturalne zdania w pierwszym dialogu.
V4 ma wymyślone próbki polskiej prozy (nie przekład scenariusza), w tym ł/ś/ć/ą/ę/ń
w pierwszej kwestii; długie ciągi testowe w narracji 3–6 zastąpione dwiema liniami.
Font i kodek bez zmian; SHA-256 font.cpk identyczny z v3. 1558 unittest OK
(25 skipped); rzeczywiście wydany ZIP wypakowany, CLI i odczyt ISO z oryginalnymi
kontenerami sprawdzone, pobranie zwrotne Drive identyczne. V4 nie uruchomiono tu
w PPSSPP. Screenshoty v3 potwierdzają scenę otwierającą, nie wszystkie ekrany gry.
[Manifest v4](pl/test-v4-delivery.json). Starsze stany poniżej są historią.

**Najnowsze PL: [TEST_PL v3](https://drive.google.com/file/d/16mPAOMpab8aSFbuqv1LSxMWyStEQmn_K/view) dostarczony.**
Analiza prywatnego ELF ujawniła błędny indeks: katakana czytana z `bajt−0x40`,
nie `bajt−0x20`. Podgląd bitmap ujawnił drugi błąd: piksele należy pakować młodszym
nibblem jako lewym. Obie poprawki zapisane w kodzie; niezależne testy fizycznych
bajtów i wykonanie małego fragmentu MIPS (ze slotami opóźnienia skoków).
Jedna pierwsza plansza misji 0-0 pokazuje 18 liter, ASCII i odstępy. Kit sprawdza
ISO po budowie, bez udziału właściciela. 1553 unittest OK (25 skipped); rzeczywiste
kontenery font/event/config w fixture ISO + uruchomienie narzędzi z wypakowanego
wydawanego ZIP sprawdzone. Nie uruchomiono pełnej gry/PPSSPP ani Windows BAT.
Pobranie zwrotne Drive identyczne. **Oczekiwany tylko screenshot pierwszej planszy
`PL V3 / 1` po New Game**, nie szukanie katakany w menu. To test techniczny, nie
pełne PL; EN/katalog/scenariusz bez zmian. [Dowody](pl/PL_FONT_MAPPING.md),
[manifest](pl/test-v3-delivery.json).

**Najnowsze (§21.66): prezentacja katalogu v3 dostarczona.**
[Nowy Markdown](https://drive.google.com/file/d/1h32WYqZ9SfrzO5BseooIdLzBNhNns-nt/view),
667590 B. Pełna lista (a–h): poprzednie usunięcia zachowane, dodatkowo bez tagów
unit dictionary, ID wszystkich pilotów/profili oraz dwóch wskazanych powtarzanych
komunikatów. Model/dane, bronie/statystyki/opisy oraz klasyfikacja wpisów specjalnych
bez zmian; niepewności nadal oznaczone. 1509 PASS,1 skipped,382 subtests; download-back
identyczny. Poprzednie wydania zachowane. Gra i kit v17 bez zmian.

**Poprzednia prezentacja (§21.65): katalog mechów — prezentacja v2 dostarczona.**
[Nowy Markdown](https://drive.google.com/file/d/1uDgRdtFqVVx7eel5jqkFBwT1zMCJcjlj/view),
707653 B. Usunięto kotwice HTML, sufiksy „— Unit N” i wiersze „Data: …” dla wszystkich
393 rekordów; model/dane, bronie, umiejętności i piloci bez zmian. Odsyłacze do
usuniętych kotwic zamieniono na czytelny tekst. Pierwsze wydanie zachowane.
1500 testów PASS,1 skipped,382 subtests; odczyt zwrotny Drive identyczny. Szczegóły:
[README katalogu](mech-catalog/README.md). Nie zmieniano gry ani kitu v17.

**Osobny stan QA gry (§21.64): [kit v17](https://drive.google.com/file/d/1TnJziZix9DxrC5XykEZM1vC0ujTBAjaw/view) dostarczony.**
`宇宙構造物` -> `Space Str.`; cała odnaleziona rodzina: 111 nazw w 271 kopiach
attr.par/lmap, 30081 zapisanych komórek. Liczby, geometria i tekstury nietknięte.
DLC04: nazwy były już EN w odtworzonym v16; dodano dwa pozostałe JP opisy i twardą
kontrolę odczytu wszystkich 12 pól obu kopii. Odtworzony błąd procesu v16: wejściowe
podfoldery były przenoszone do output/DLC i mogły nie trafić do katalogu gry.
V17 daje płaskie pliki, obsługuje różnice liter i odmawia niejednoznacznych backupów.
**Nie ustalono, czy dokładnie ten układ występował u właściciela.** Stary sejw nie
jest automatycznie dowodem save state. CHECK_DLC.bat czyta zainstalowane pliki bez
zmiany czegokolwiek; jeśli objaw zostanie, potrzebny DLC_TITLE_CHECK.json.
Testy: **1493 passed,1 skipped,382 subtests**. Wypakowany rzeczywisty ZIP i fixture
ISO z oryginalnymi plikami sprawdzone bajtowo; to nie boot pełnej gry/PPSSPP.
ZIP 7245833B, pobranie zwrotne Drive identyczne. [Dowody i granice](QA_V17.md),
[manifest](qa-v17/delivery.json). Oryginały/sejwy zachować. Lmap rośnie do156174576B
(STORED), a ISO dopisuje zmienione człony — większy plik jest oczekiwany.

**Poprzednia dostawa (§21.63): katalog mechów ukończony w zakresie dostępnych danych.**
[`srwoe_mech_catalog.md`](https://drive.google.com/file/d/1cBbPxTiY-MFASz2H3UJ1aS7SmSD-8uQC/view):
761 353 B, pełny odczyt zwrotny Drive identyczny bajtowo. 393 rekordy jednostek
(własne/wrogie, formy, obiekty i rekordy filmowe), 1485 wpisów broni/akcji;
535 przypisań pilotów/załóg, osobne profile alternatywne, zdolności bez Spirits,
opisy bazowe, statystyki broni i jawne bramki warunkowe. Dane z oryginalnej 1.08
oraz istniejącego EN; 20 nadpisań opisów w EBOOT uwzględnionych. 17 poprawek
złożonego tekstu **tylko w katalogu**, bez zmian pakietu lub plików gry.
Pozostałe braki są oznaczone: 20 serii, 2 referencje zdolności (110/230), brak
potwierdzonych misji odblokowania; puste sloty natywne nie oznaczają braku efektów
systemowych. 302 serie są bezpośrednie, 57 po jawnej nazwie formy, 14 to oznaczone
skojarzenia z pilotem. Pełny suite: **1438 passed, 1 skipped, 382 subtests passed**;
59 nowych testów, w tym 24 mutacje semantyczne. Narzędzia, dowody, testy i manifest
w Git/PR #17. [Szczegóły i reprodukcja](mech-catalog/README.md).

**Poprzednia dostawa (§21.62): finał angielskiego scenariusza do czytania 34 ukończony.**
Na Drive jest komplet pojedynczych epizodów **00–34**. [Epizod 34](https://drive.google.com/file/d/1roWkSt4ur91OMSHqIDonmouEYBDYF0-j/view)
ma 212 920 B; pobranie zwrotne jest identyczne bajt w bajt. Pełne 7471 wpisów prozy
rozliczone: 3338 pokazane, 4133 identyczne aliasy; zachowane wszystkie unikalne
zakończenia, metadane, rozmówcy i myśli, wydzielone dialogi warunkowe i porażka.
To wydanie istniejącego angielskiego z `pakiet_EN`, **nie nowy przekład ani patch gry**.
Pełny suite: **1379 passed, 1 skipped, 382 subtests passed**; 57 nowych testów czytelniczych.
Patch poprzedniego agenta zarchiwizowany 1:1 w `docs/recovered/`, wszystkie 918
odzyskanych linii w `READING_SCRIPT_HISTORY.md`, bez nadpisania historii QA v16.
Patch zawierał wyłącznie dziennik — potrzebne narzędzia/plan odtworzono i zapisano
w Git wraz z testami. Instrukcje i manifest: [`reading-script/README.md`](reading-script/README.md).
Epizodów 00–33 nie regenerowano; ich dawne wyniki testów są historią. Sceny `simulator`
nie należą do ukończonej serii `story`. PR #17 zawiera kolejne wypchnięte checkpointy.

**Osobny stan QA gry (§21.61): poprawki misji 0-1 przygotowane w v16.**
Przywrócone cztery znaczniki imienia gracza w EBOOT (bez hardkodowania Seishiro),
Foe/Oth → `F.`/`O.`, Post-Mv → `P-Mv`; 21 tytułów DLC w obu polach nazw oraz kopiach
config/imenu (84 pola), brakująca karta `Basic Training` w DL100_01_ext.dat.
Pisarz chroni stałe silnika i osobne limity ekranowe. Rozmiary config01–07 bez zmian;
pozostałe pola katalogu i bramki słowników nietknięte. **1322 testy OK, 1 pominięty;
0 błędów kontroli pakietu; build z wypakowanego kitu i odczyt wyników sprawdzone offline.**
Kit `srw-oe-translation-v16.zip` na Drive (`1AHsLPKWTTnEh7G7Sovsld7kfqQalDet-`).
**Oczekuje tylko potwierdzenie tych nowych poprawek w PPSSPP** — nie wykonano testu
emulatorowego. Zimny start z nowego buildu, nie stary save state; sejwów nie kasować.
Szczegóły, komendy, hashe i ograniczenia: `EXPERIMENT_LOG.md` §21.61,
`pakiet_EN/CO_NOWEGO_v16.txt`. Starsze zadania poniżej pozostają historią.

> **Stan przekazania PRZED nowymi zgłoszeniami QA (2026-10-17, wg właściciela projektu):** gra jest w 100% przetłumaczona na angielski.
> Pełne tłumaczenie = `PATCH15.zip` (dostarczane lokalnie / przez Google Drive, nie na GitHubie).
> Brak otwartych zadań i issues — wszystkie zostały wyjaśnione i zamknięte.
> Poniższe wpisy („Latest", „Open", „Still open", „Otwarte") opisują **historię prac** i są nieaktualne jako lista zadań.
> Zasada modyfikacji plików gry: modyfikacja jest częścią projektu; publikacja plików gry na GitHubie jest wykluczona.


**Latest (2026-10-17, §21.58): kit v14.** Foe Robots: narrow+type wydane do strony config (oryginalne komórki; weryfikacja: RoboDict02 EN ×6, JP 0, rozmiary = oryginały; rollback = v13). Build wyciszony (bramka/probe = „Uwagi planowe”), cheaty opt-out (--cwcheat). README korzenia + workflow Release (v14 opublikowana ręcznie, tag patch-v14; decyzja o automatyzacji = pytanie do usera). Suite 1 285 OK.
**Latest (2026-10-17, §21.57): Robot Viewer/nagroda rozgryzione md5-identycznym rebuildem.** Lista czyta globalny słownik (config00) z fallbackiem do rozdziału; JP 邪竜兵 = słowniki v16 (celowo JP, era `"` — do wycofania). Build ma własne configi 01-19 z EN nazwami. 'First Clear Bonus:' → 'First Clear:' (nakładanie kolumn). Kit v13: md5 26d3a9fd….
**Latest (2026-10-17, §21.56): `"` WYJAŚNIONY I NAPRAWIONY.** Mechanizm: exe strings naruszyły tablicę interpunkcyjną EBOOT (「 　」 co 4 B) → silnik rysował sam `"`; fix = revert 3 wierszy (§21.54, potwierdzone grą §21.55). DLC uniewinnione (JP ISO + EN DLC = dialogi OK); configi v16 (słowniki JP) w grze OK. Backlog: glif 連→LNK, exe 404/404, patcher v12 (ui_labels+assets/fonts w zipie — poprawka „braku ikon”). Otwarte: info o nagrodzie (czeka treść z ekranu usera), potwierdzenie nazw wrogów w Robot Viewer na świeżym ISO. Kit: srw-oe-translation-v12.zip (md5 6a53774b…).

**Latest (2026-10-16, §21.46): misja 2.1 `"`.** Hash pliku usera = rebuild → polowanie po
formacie: rekordy **0x13E** niosą bezwzględne offsety do puli tekstów; po tłumaczeniu zostały
stare (silnik czytał śmieci — m.in. `"`, tofu, `?!`). Pisarz: `remap_text_anchors()` (tylko
0x13E; inne typy = ryzyko korupcji id), testy +3, suite 1 284 OK. eventP01 naprawiony
(`0106b237…`). Test 3-krokowy na Drive (naprawiony eventP01 / oryginał JP / config #18).
Priorytet bez zmian: 100% w grze → patcher.zip.

**Latest (2026-10-16, §21.43): v14 PADAŁO (mój błąd: slot 5 „Voice:" nie miał pokrycia w działających
stanach), ALE przełom: imenu01 v9 (pełne EN, podwojony rozmiar) działa u użytkownika cały czas →
trująca jest tylko strona config. Builder utrwala fix: configNN.EDAT zawsze traci spare-sloty
słowników (weryfikacja: pełny pakiet → config01–08 bajt w bajt = v13), imenuNN zachowuje pełne EN.
Następny test (opcjonalny): config01–08 v13 + imenu02–08 v9 z folderu NPJH50521_v9 → encyklopedia
rozdz. 2–8 pełna EN. Szczegóły: `EXPERIMENT_LOG.md` §21.43.**

**Latest (2026-10-16, §21.42): v13 DZIAŁA ✅ — rozdziały DLC znów gramy po angielsku.** Winne
crashowi: nowe sloty v7 w słownikach (Voice:/short_name/alt_name/note/type/narrow). Aktualny stan
działający: ISO v9 + config01–08 **v13** + połowa B i imenu01 v9. **v14** (na Drive) = v13 + głosy
(slot 1 i „Voice:" slot 5), wagi, etykiety, entry — pola o strukturze z działających stanów; JEDEN
test. Szczegóły: `EXPERIMENT_LOG.md` §21.42.**

**Latest (2026-10-16, §21.41): v12A PADAŁO — SŁOWNIKI WINNE [test].** Mapa slotów z diffu #17↔v11:
EN w #17 działało (głos slot1, „Nickname:" slot4, entry, Weight, serie); nowe od v7 = Chara slot 5
(„Voice:"), slot 11 (krótkie nazwy), slot 10, Robo note/type/narrow + EN- broadcast na rekordy JP.
**v13** = słowniki EN tylko w polach z #17 (+ skrócenia), nowe sloty JP, reszta jak v11 — kandydat
jednego testu. Szczegóły: `EXPERIMENT_LOG.md` §21.41.**

**Latest (2026-10-16, §21.40): v11 PADAŁO — katalog DLC uniewinniony.** Zostają 2 grupy podejrzanych:
słowniki (CharaDict/RoboDict) i listy nazw (unit_list/charalist). Przypadek: wariant „#17 + listy z v11"
okazał się md5 w md5 = **build #18 (sprawdzony w grze)** — odnaleziony ostatni działający stan DLC.
**v12 = JEDEN test decydujący (folder_A = #17 + słowniki z v11): pada → winne słowniki; działa → winne
listy nazw (folder_B == #18, zapas nie wymaga testu).** Szczegóły: `EXPERIMENT_LOG.md` §21.40.**

**Latest (2026-10-16, §21.39): v10 PADAŁO — koperta sfalsyfikowana (build #17 config02 = 159 872 B >
oryginał DZIAŁAŁ w Y4a; odtworzyłem #17 1:1 z historii PR #13). Diff „działał(#17) ↔ padał(v10)" =
5 klas członów; teza: przetłumaczony KATALOG DLC (srwDL_DLC_ID01–07: tytuły/opisy rozdziałów, od v7;
wiersze tylko dla rozdz. 00–07 → połowa B i imenu01 naturalnie czyste; #17 miał je po japońsku).
**v11 = v10 z katalogiem DLC przywróconym do bajtów ORYGINAŁÓW 1:1** (DLC_ID01–07 + Reference03/08;
EN wrócą po drabince szerokości) — KANDYDAT JEDNEGO TESTU. Bramę koperty usunięto z buildera
(fałszywe odmowy). Jeśli v11 padnie: revert {unit_list, charalist, CharaDict, RoboDict} do #17
(= gwarantowany stan działający) i bisekcja 4 klas. Szczegóły: `EXPERIMENT_LOG.md` §21.39.**

**Latest (2026-10-16, §21.38): PRZYCZYNA CRASHU DLC v9 ZNALEZIONA I NAPRAWIONA OFFLINE.** Gra trzyma
stały bufor per plik DLC `configNN.EDAT` = oryginał zaokrąglony w górę do 0x800; v9 config01
(249 984 B) i config02 (159 872 B) siedziały dokładnie 128 B nad granicą i padały na Loading
(koperta rodzinowa — podwojony imenu01.EDAT działa, boot-scan config01–46 §21.12). Dowód: reprodukcja
bajt w bajt padających plików + odtworzenie DZIAŁAJĄCEGO builda #17 z historii PR #13 (md5 `7c6459fa…`
z listy Y4a) i diff człon po członie (pule/listy == #17, słowniki == imenu01, jedyna różnica globalna
= +1 kwant). FIX: (1) brama koperty w builderze (limit = align_up(oryginał, 0x800); drabinka pełny →
bez slotów viewerów po stronie config (UI czyta imenuNN) → odmowa fail-closed); (2) pakiet v10: 4
reguły skróceń robo (Ryu Knight, VOTOMS, Code Geass, Length→Len.) ratujące config02; (3) trim padu
PAC odpada (EToc musi być na 0x800 — zmierzone). **8 plików config01–08 v10 zbudowanych, wszystkie
≤ oryginałów; JEDEN test weryfikacyjny do wykonania** (instrukcja na Drive). Testy 1 287 OK/24
pominięte. Szczegóły: `EXPERIMENT_LOG.md` §21.38.**

**Latest (2026-10-16, §21.37): v9 (pełny build HOKUS_POKUS) PADA na „Loading" — pierwszy w grze test NARAZ
podmiany EBOOT.BIN (exe_step, nigdy nie boota; możliwy fallback `source: PBOOT.PBP`) i danych v7/v8/v9 (też
nigdy). DIAGNOZA (sekcja 1): narzędzia CZYSTE (7/7 md5 = gałąź); EBOOT = jawny ELF md5 `4d8b8a85…` NIEZNANY
(zgodny ze świeżym łatem programu z płyty, ale też z dziedziczeniem ze stacka — builder NIE MA bramki na
nieoryginalne źródłowe ISO); `eventP00`/`mesbtl00` w ISO = build v3-era bajt w bajt; brak `build_report.json`
i `pakiet_EN` obok batów — niewiadome, którego pakietu i JAKIEGO ISO użyto (pytania do użytkownika + raport).
Przyczyna NIEZNANA — rozdziela ją test A/B: nowe `EBOOT_TEST.bat` + `tools/eboot_swap.py` robią z
istniejącego `patched.iso` kopię z ORYGINALNYM programem z oryginalnego ISO 1.08 (zmiana TYLKO `EBOOT.BIN`,
dane builda bajt w bajt; fail-closed: kolejność `~PSP`/ELF, identyczne programy, nasz znany ELF jako
„oryginał", odczyt kontrolny; 17 nowych testów, całość 1 283 OK, 24 pominięte). Przed testem: CHEAT WYŁĄCZONY
(adresy cheatu × podmieniony program = nieprzetestowana kombinacja). E1 działa ⇒ winny EBOOT (napisy programu
wracają na pewny CWCheat); pada na Loading ⇒ winne dane — jeśli źródłem był poprzedni patched.iso: CZYSTA
przebudowa z oryginału; jeśli oryginał: BISEKCJA A–I (podejrzani: `imenu00.cpk` 34 984 → 88 232 B, configst
Achievement/tokeny, eventy/mesbtl DLC z 23 030 nowych EN). Szczegóły: `EXPERIMENT_LOG.md` §21.37.**

**Latest (2026-10-16, §21.37 WYNIK T1): GRA DZIAŁA z v9 ISO + ORYGINALNYM DLC — a przy cheat OFF
zdolności broni 1.08 są po angielsku, czyli JAWNY ELF JAKO EBOOT.BIN POTWIERDZONY W GRZE. Strona ISO
v9 przyjęta w całości (config00, configst, imenu00 z pisarzami v7/v8, eventP00/mesbtl00, tekstury
UI_TEST4). Winne: DLC v9 (cały zestaw po raz pierwszy w grze). Nowe `tools/dlc_test.py` +
`DLC_TEST.bat` — bisekcja DLC CZYSTE KOPIOWANIE: runda = jedna grupa v9 plików w folderze emulatora +
boot; grupy `konfig_imenu`/`eventy`/`mesbtl` + połówki `_a`/`_b` + przywracanie `r_*`/`oryginaly`;
fail-closed (foldery parami różne, tylko różne-md5 obecne po obu stronach, odczyt kontrolny, raport
JSON); 15 nowych testów, całość 1 301 OK (24 pominięte). PROTOKÓŁ: start = DLC oryginalne, R1
`konfig_imenu` (podejrzany nr 1, historia Y) → R2 `eventy` → R3 `mesbtl`; padająca grupa = rozbijanie
połówkami do pliku. Szczegóły: `EXPERIMENT_LOG.md` §21.37.**

**Previous (2026-10-16, §21.37 odczyt raportu): build_report.json padającego v9 rozstrzyga exe:** EBOOT
płyty = znany ELF PBOOT (`8ba77a79…`), 402/404 w miejscu, out = `4d8b8a85…` z DIAGNOZY ⇒ **EBOOT niskie
podejrzenie** (goły ELF z ISO bootuje mu codziennie; mechanizm = działający CWCheat). `eventP00`/
`mesbtl00` = bajty już działające w grze (kanon v3). Podejrzani: **DLC v9** (nigdy w grze),
config00/configst/imenu00 (v7/v8), system+tacsys (UI_TEST4); 325 odmów = śmieciowe wiersze pakietu.
Build szedł z klona c0e5c9d1 (pakiet tam) — BISEKCJA/HOKUS wskazywać TEN pakiet. **PLAN: T1 = v9 ISO +
ORYGINALNE DLC** (zamiana folderu `NPJH50521` w emulatorze na kopię `D:\SRWOE\NPJH50521`, cheat OFF):
działa ⇒ DLC → BISEKCJA I/H; pada ⇒ T2 = E1 (świeży `eboot_swap.py`) → działa ⇒ EBOOT; pada ⇒ BISEKCJA
A/E/B + tekstury. Szczegóły: `EXPERIMENT_LOG.md` §21.37.**

**Previous (2026-10-16, §21.37 addendum): E1 próba 1 odmówiła — ORYGINAŁ UŻYTKOWNIKA MA JUŻ ODSZYFROWANY
EBOOT (jawny ELF, nie `~PSP`) [ZMIERZONE]**; `exe_step` łatał więc ELF płyty w miejscu (nieznany md5
`4d8b8a85…` = ELF płyty + napisy EN, najpewniej bez PBOOT-fallbacku). `eboot_swap` poprawiony: para ELF→ELF
rozstrzygana po zawartości (równe rozmiary + różne bajty japońskie w oryginale vs ASCII w buildzie; odwrócona
kolejność / dwa załatane / różne wydruki → odmowa; `--force` omija; profil różnic w raporcie). Testy 1 286 OK.
E1 uruchamia się tym samym `EBOOT_TEST.bat` (zapamiętane ISO działa).

**Previous (2026-10-16, §21.35): CORRECTION + PACKAGE v8. The §21.34 claim "426 voice-actor names deliberately left
Japanese" was WRONG: 424/426 `char:K:voice_actor` rows already carried Latin names since v4 (Western order, Hepburn
without macrons; 2 rows are the `NoData` placeholder) — one misreading fixed (`高乃麗` "Rei" → "Urara Takano"), the full
list is `aktorzy_glosowi.tsv` in the package. A byte scan of every built member (now including half-width kana) found
three REAL leftovers, all in `configst.cpk`: the Fortune/Bless spirit descriptions (kana-token fields the record refresher
only reported), five `Skill_Tag` strings (configst was not in the v7 refresh) and seven achievements with English for
weeks that `table_write` REFUSED because the record's target count (30/40/100) looked like an in-record pointer (visible
only in the container `problems` of `build_report.json`). Fixes: `Family(2, exempt=((8, 28),))` for Achievement (layout
measured on 75 records), `record_rows_refresh` adds token fields as display-form rows (`%s` per control byte, `tokeny.tsv`
entries computed straight from the field bytes), `table_rows_refresh` run over configst. Package v8 = v7 + 12 corrected
English values (Takano ×4, `SRWHPｺﾗﾎ` → "SRW Web Collab" ×8) + 14 rows − 8 junk/obsolete rows: 109 032 rows / 81 678 EN /
0 errors; on Drive, v7 moved to `_STARE_NIE_UZYWAC`, `diagnoza` expects v8 (and checks the Achievement exemption in the
tools). Sandbox build #23b (config00 + imenu00 + configst, plus config01.EDAT separately): 0 skipped, configst problems 0,
0 readable Japanese runs in Spirit / Skill_Tag / Achievement. Still unknown: whether `srwDL_CalcType.bin` (34 untranslated
formula labels) is ever displayed; nothing of v7/v8 confirmed in-game yet. Tests: 1 266 OK (1 skipped).**

**Previous (2026-10-16, §21.34): FULL v6 BUILD CONFIRMED IN-GAME (intermission English, graphics intact; program strings via the
cheat file). The five leftover screenshots — Character Viewer (non-pilot names in the grid, `愛称：` / `声優：` lines and the
voice-actor names), Robot Viewer foe units (`ボルトロボ`, `邪竜兵`) and the whole Game Reference (`解説書`) — traced to four
causes, all measured in the files: (1) the intermission reads `imenuNN.cpk/.EDAT`, whose six members are byte-identical
copies of `configNN`'s, while the Reference / Shop / DLC_ID rows were addressed to `configNN` only (the coverage audit is
container-agnostic, so it never saw it); (2) the CharaDictionary writer wrote slots 0–4 only — slot 5 (`声優：`+actor), 10
(alt name) and 11 (the grid's short name, the ONLY name a non-pilot has) were never written, and 146 `config_leftover`
`愛称：X` rows collided silently with the keyed nickname rows; (3) the RoboDictionary writer wrote slots 0/1/3 only — note
(2), type (4), the name of units without a `unit_list` entry (5, the foes) and the narrow kana-token name (6) were not;
(4) Reference section titles (slot 0) had no rows and the `レベル差補正` page existed only as 27 fragments (the exporter
rejects kana-token bodies). Fixes: `table_write` viewer slots + label rows (`label:<family>:<slot>`, one row per label),
`build_translation_patch.mirror_identical_members` (rows reach every byte-identical member copy, both ways; the
`unit_list` series rows follow the RoboDictionary too — build #22 caught a 6-byte difference without that), NEW
`tools/table_rows_refresh.py` (walks every table member of the real containers, adds the missing rows with `copy_of` /
sibling English, prunes stale / superseded / unreachable offset rows, salvages glued English, writes `tokeny.tsv`
entries), `coverage_audit` counts `愛称：仁` as covered when label and text are separate rows. Package v7 (109 026 rows /
81 672 EN, 0 errors, coverage 0 missing; ~~426 voice-actor names deliberately left Japanese~~ — WRONG, see §21.35) on Drive,
v6 moved to `_STARE_NIE_UZYWAC`; `diagnoza` knows v7. Sandbox build #22 (synthetic ISO with `imenu00.cpk` + 30 DLC EDATs):
0 skipped rows, 0 verification failures, every config/imenu pair 00–08 identical, 0 Japanese runs left in the five
viewer/reference members. Tests: 1 261 OK (1 skipped). NOT run in-game: v7 (watch: `imenu00.cpk` grows 34 984 → 88 232 B
because the CPK is re-stored uncompressed; "Extra Controls" header width; "Voice: " + Japanese actor name), the
EBOOT.BIN-in-ISO route (user testing), UI_TEST4. Details: `EXPERIMENT_LOG.md` §21.34.**

**Previous (2026-10-15, night): EXE_TEST1 IN-GAME RESULT — swapping `PBOOT.PBP` in the emulator's DLC folder changes
NOTHING (confirmed: release PPSSPP never reads the update; `FindGameUpdatePBOOT` exists only in master), while the
CWCheat file `cheats\NPJH50521.ini` turns the program strings English at once (CONFIRMED). The cheat addresses come from
the PBOOT-derived ELF, so the program PPSSPP boots — `PSP_GAME/SYSDIR/EBOOT.BIN` inside the ISO (a dump of the 1.08
PKG) — has the same string layout. Consequence: the builder's `exe_step` now patches the ISO's `EBOOT.BIN` as its
PRIMARY target (decrypt with `psp_prx` → verify Japanese bytes → in-place English → plain ELF appended into
`patched.iso`), keeps `DLC\PBOOT.PBP` as a secondary target and still writes the cheat file; an undecryptable disc EBOOT
with a `~PSP` header identical to PBOOT's falls back to the PBOOT program (flagged `source: PBOOT.PBP`). `psp_prx` gained
the type-6 retail tags (`0xD91680F0/81F0`, ported, no sample run), `diagnoza` classifies `EBOOT.BIN` (original `~PSP` /
known plain build / unknown) and the report's per-target lines, `WGRAJ_DO_ISO` (`iso_insert`) accepts an `EBOOT.BIN`.
Sandbox build #21 (synthetic ISO carrying the real encrypted `DATA.PSP` as EBOOT.BIN): 397/397 on both targets, EBOOT in
`patched.iso` = plain ELF md5 `ba4cc05c…`. `EXE_TEST2.zip` (EBOOT.BIN for WGRAJ_DO_ISO, cheat disabled) on Drive. Tests:
1 238 OK (1 skipped). STILL A HYPOTHESIS: PPSSPP boots the plain-ELF `EBOOT.BIN` from the ISO (loader source + fan-patch
practice; not run in-game yet); the user's disc EBOOT tag/md5 are unknown until his rebuilt `build_report.json` arrives.
The confirmed route for the program strings today is the cheat file. Details: `EXPERIMENT_LOG.md` §21.33.**

**Previous (2026-10-15, late evening): build #19 (v5 text + UI_TEST3 textures via HOKUS_POKUS) CONFIRMED WORKING in-game
("everything runs beautifully"). The 8 screenshots of leftovers traced to three sources, all by bytes: (a) the GAME
PROGRAM — `PBOOT.PBP` (the 1.08 update in the DLC folder) → `DATA.PSP`: `移動後`, `TGT 敵`, Evade / Sup. Def / Low EN
banners, the Guard effect line, the 1.08-only `<貫通 Lv2>` / `<ビーム兵器 Lv2>` / `<連携攻撃 Lv2>` weapon-ability lines, the
command and tactical menus, save / network / DLC messages — 0 hits in any data container; (b) `sysmes.bin` WHOLE strings
written in half-width kana with `0x0F` tokens (`メインパイロット`, `サブパイロット`, `SELECT パイロット表示変更`, Sort, Page, …) — the
v5 package held only their tails, which the sysmes writer ignores (root cause: the package was never re-merged after the
whole-string exporter landed, and the exporter's Japanese test skipped half-width katakana); (c) texture UV cells
(`WPN名`, clipped RNG, EN Cost sliver, half-cut part / ability icons). Fixes: new `tools/psp_prx.py` (pure-Python PRX
decrypter for tag `0x2E5E10F0`, which stock pspdecrypt does not know; ELF md5 `8ba77a79…`) and `tools/exe_strings.py`
(408 referenced strings, in-place `slot` rows with alignment slack, printf-conversion check, CWCheat export); 397/408
translated in the new `09_executable.jsonl`; the builder's `exe_step` writes `DLC\PBOOT.PBP` with a PLAIN-ELF `DATA.PSP`
(builder output == hand-made `PBOOT_en.PBP`, md5 `26689964…`) plus `cheats\NPJH50521.ini` as the fallback; 31 whole sysmes
rows added to `04`; `coverage_audit.py` now checks whole sysmes strings and `PBOOT.PBP` (v5 → 33 missing, v6 → 0);
`sysmes_text` / `translator_export` fixed for the future; texture batch 4 (`mensys_03/07/11/13`, `tacsys_16/18`);
`diagnoza` knows v6, UI_TEST4 and classifies `PBOOT.PBP` (md5 + header). Package v6 (108 574 rows / 81 220 EN, 0 errors),
sandbox build #20 (5 containers + PBOOT 397/397 verified), `EXE_TEST1.zip` and `UI_TEST4.zip` on Drive (v5 / KIT18 /
UI_TEST3 moved to `_STARE_NIE_UZYWAC`). Tests: 1 227 OK (1 skipped). HYPOTHESES, not run in-game: PPSSPP boots a
`PBOOT.PBP` whose `DATA.PSP` is a plain ELF (source-verified in `sceKernelModule.cpp` only); the ISO `EBOOT.BIN` is the
same binary; `＠4Gamer:` reading of `ゲーマー`. Details: `EXPERIMENT_LOG.md` §21.32.**

**Previous (2026-10-15, evening): UI batch 3 — the single-kanji ICONS now carry 2-letter codes and `navisys.cpk` is in
scope. Measured badge geometry (1-px border, 2-px frame, ~10×10 px inner area) allows two letters at 7–9 px; one
letter would clash with the S/A/B/C/D rank letters drawn next to the terrain badges, three do not fit. Codes:
terrain GR / AI / SP (`mensys_03`, `mensys_14`), weapon abilities BR Break / AR Arc Shot / PU Push / TH Throw (notched
variant = Pull Throw) / CO Combination (`mensys_13`; M and B are original), map badges SR Surround / DH Direct Hit /
PU / TH (`tacsys_15/17`, `mensys_15`), spirit orbs VA BU AC FL FO / PE WA GA FR DI (`mensys_15`, shading copied per
column, pictograms fire / freeze / stun untouched). `navisys.cpk`: TOC container with two BARE GIMs (no PAC),
true-colour RGBA8888, `ExtractSize` stored as a schema constant — `cpk_write` now accepts that layout and keeps the
constant on rebuild (identity rebuild == original), `gim_image.encode_rgba8888` writes true colour back same-size,
`ui_texture_patch` handles bare-GIM members and several members per TOC container; `navisys_02`: Battle / Evade /
Musai / Confirm / Cancel / Enemy Sighted (`navisys_01` has no text). Totals: 26 textures, 137 labels painted, 6 kept,
4 erased, 0 fit refusals, 6 containers. `UI_TEST3.zip` on Drive (supersedes UI_TEST2, moved to `_STARE_NIE_UZYWAC`);
the builder paints all 6 containers (end-to-end on the synthetic ISO byte-identical to the kit); `iso_insert`,
`diagnoza` know `navisys.cpk` / UI_TEST3. Still Japanese: `mensys_12` (連 持 特 防 突 早 狙 回 — where the game shows
them is unconfirmed; screenshot requested), the 6-px link markers in `intsys_01`, 用 / 名. NOT yet in-game: UI_TEST2,
UI_TEST3, builds #19+. Details: `EXPERIMENT_LOG.md` §21.31.**

**Previous (2026-10-15, afternoon): `UI_TEST1 A_stored` WORKS in-game (user's screenshots: intermission tabs, ATK/DEF/HIT/EVA,
Will, Support in English, no crash) ⇒ the game accepts `.pac` members stored uncompressed, and that is the only variant
shipped from now on. Second batch done the same way: 23 textures total (18 new — battle `tacsys.cpk`: Attack / Defend /
Evade / Counter, Counter Attack / Defend / Critical / Evade banners, Unit Info, Start Battle, Support Setup, Will, Units
Ready, Spirit Cmd / Skill / Level Up! / Get!, Your turn / Enemy turn, N/A badge; menus: sound options, In Use, NOTE,
Gain / Funds / Cost / Req.; intermission `intsys_03/04`: Upgrades, Linked Units, Upgrade Limit Break, Parts List, Convert,
Equip, Team …) in 5 containers (`system`, `tacsys`, `IM1000`, `IM3000`, `IM9000`), 101 labels painted, 4 katakana
sub-captions erased, 0 fit refusals. `UI_TEST2.zip` on Drive (supersedes UI_TEST1). **`build_translation_patch.py`
(HOKUS_POKUS) now paints these textures into `patched.iso` itself** (fail-closed step, `--no-ui-textures` to disable;
end-to-end on a synthetic ISO: text containers byte-identical to build #18, UI containers byte-identical to UI_TEST2).
Weapon-panel ability line: its five pool fragments exist only in `srwDL_Skill00/0N.bin`, 0 hits in UI containers, and are
English in builds #17/#18 ⇒ the game composed it from a JAPANESE pool at the time of the screenshot (hypothesis: the
`DLC_pulaJP` diagnostic `config02.EDAT` from KIT 17, or an original EDAT, in the user's DLC folder) — awaiting a fresh
`DIAGNOZA.bat`. Kept Japanese on purpose: single-kanji badges (`mensys_12/15`, 包/押/投, terrain), `navisys_02` (writer
blocked). UI_TEST2 and build #19 NOT yet run in-game. Details: `EXPERIMENT_LOG.md` §21.30.**

**Previous (2026-10-15, night, after the first screenshots of actual play with v4/#17): package v5 / build #18 — unit
and pilot names in the intermission lists ≤ 14 half-width cells (the game squeezes Japanese, never ASCII; measured on
the user's screenshot), 8 Skill00 `effect` texts without the stray `4` after `%s` (the Japanese byte completes the kana
fragment ｸﾞﾙｰ<0F>; the English fragment `Group` has no dangling byte, so #17 showed "Group4All units attack"), pilot
Kuro (foreign English). New `translation_check` rules: list-column width (CP932 bytes), completion byte, conflicting
duplicate rows of one Skill00/Item00 string (the writer silently skips the whole record otherwise — hit in the first
#18 run). The Japanese ability line on the user's battle weapon panel is Skill00 r239 rendered from an ORIGINAL
`config00.cpk` (build #17 is fully English there) — most likely UI_TEST1 applied to the original ISO (the instruction
allowed it; corrected) — awaiting `DIAGNOZA.bat --iso`. v5/#18 NOT yet run in-game. Details: `EXPERIMENT_LOG.md` §21.29.**

**Previous (2026-10-15, night → next day): Y4a, Y4 and Z4 ALL WORK in-game (PPSSPP, ISO 1.08): Loading, new game,
the chapter-2 save, pilot status and skill screens — package v4 + build #17 is the first fully accepted TEXT set**
(the pool budget rule — each `srwDL_Skill0N.bin` ≤ 15 638 B, Skill00 + pools ≤ 342 194 B — holds in every test so
far; still a measured rule, not a proven mechanism). The user's screenshots then raised the next front: the
system labels on the status / weapon / skill screens (攻撃 防御 命中 回避, tabs 能力 改造 武器 機体, 特殊能力・スキル,
気力, 援護 …) are still Japanese. They are NOT text — they are **GIM textures** inside `system.cpk`, `IM1000.cpk`,
`IM3000.cpk` (never in scope until now). New offline tool chain (`tools/gim_image.py` decoder + same-size INDEX8
encoder, identity 52/52; `tools/cpk_itoc_write.py` for TOC-less CPKs; `tools/gim_label.py` fail-closed caption
renderer driven by `ui_labels/*.json`; `tools/ui_texture_patch.py` container builder) rewrote 5 textures
(`intsys_01`, `mensys_01/03/08/13`: Stats/Mods/Arms/Unit/Pilot tabs, ATK DEF HIT EVA SIZE MOV, EN Cost RNG HIT TGT
Will Req, Abilities / Skills, Parts, Spirits, Will, Support …). `UI_TEST1.zip` on Drive (variants `A_stored` and
`B_crilayla`, 3 containers each) — **nothing of this has run in-game yet**; it is deliberately not a HOKUS_POKUS step.
Battle textures (`tacsys`), `mensys_05/07/10–12/14`, `intsys_03/04`, `.sp`/`sprstd`/`mesbmp` remain Japanese.
Details: `EXPERIMENT_LOG.md` §21.28.

**Previous (2026-10-15, night): tests X/Y in-game split the full-patch crash — X (patched.iso with the rebuilt
`eventP00`/`mesbtl00`/`imenu00` + config #14, ORIGINAL DLC folder) WORKS into the dictionary screen; Y (original
ISO + the complete 91-EDAT build #15) CRASHES at "Loading" with the exact build-#8 stack.** The only sub-file
that grows in every chapter in a way matching that stack is the DLC skill fragment pool `srwDL_Skill01–08.bin`
(15 638 → 17 396 B each; Skill00 + 8 pools: original 334 062, X 341 622 works, Y 355 686 crashes). HYPOTHESIS,
not proof: one arena for Skill00 + the eight pools, bound between 342 194 (W1 works) and 343 214 (W2 crashes).
Package **v4** = v3 + Tier 4 shortening rules (219 total) + pools re-synced to the shortened Skill00 English
(`skill_shrink.py --dlc-original`; a package defect — 583 Skill00 tail rows share one id — is worked around by
`copy_of` only on unique ids): every pool 15 578 B, Skill00 215 462 B, total 340 086 B. Gates now in the tools:
pool ≤ 15 638 B is FATAL in `table_write.py` (container "NOT written"), builder reports `skill_total` ≤ 342 194.
**Build #17** (config00 md5 `80b8fae6…`, config01–08 at original sizes) + `KIT_build17_2026-10-15.zip` and the v4
package are on Drive (v3/KIT15 moved to `_STARE_NIE_UZYWAC`, instruction replaced and verified). Next, in-game by
the user: Y4a (original DLC + the 10 config files of build #17) → Y4 (full v4 DLC build) → Z4 (full patch +
chapter-2 save); Y3 (Japanese pools) only if Y4a crashes. Known layout bug: the dictionary hint bar overlaps the
"Pilot" tab. v4/#17 have NOT been run in-game yet. Details: `EXPERIMENT_LOG.md` §21.27.

**Previous (2026-10-15, late evening): the user's FULL patch (provenance unknown) CRASHES at "Loading" with the
exact build-#8 stack** (`memcpy_jak` ← `z_un_08b3d554` …, `Read/Write Block at 00000000`). Two findings: (1) my
fault — the Drive `INSTRUKCJA_PL.md` was still the 2026-10-14 text pointing at package v1 and the build-#6 kits
(all now moved to `_STARE_NIE_UZYWAC`, instruction rewritten and re-uploaded, KIT_build15 uploaded); (2) the
three ISO containers `eventP00`/`mesbtl00`/`imenu00` and the 91 EDATs have NEVER been run in-game with the
fixed writers (bisection letters C/D/E/G were never executed). Build #15 here (v3, 13 containers) reproduces #14
for config00/configst; the other files grow 1.6–2.9× because changed members are STORED (uncompressed content
grows ≤ 6 %) — a boot-time memory budget on whole files is an open hypothesis. New read-only `DIAGNOZA.bat`
(`tools/diagnoza.py`) reports which tools/package/build/emulator files are actually in place, with md5 tables
of every shipped build; `build_report.json` now carries a tools stamp. Next: user runs DIAGNOZA, then test X
(original DLC + patched.iso) and test Y (original ISO + full DLC build), then container bisection via
`WGRAJ_DO_ISO.bat` / `BISEKCJA.bat`. Details: `EXPERIMENT_LOG.md` §21.26.

**Previous (2026-10-15, evening): CONFIRMED IN-GAME — build #14 loads the user's mid-chapter-2 save and the skill
descriptions read correctly; Y5 (= Y3 with only the `+52` word corrected) loads where Y3 crashed**, so the
chapter-2 crash was the stale parameter pointer, not the member size (the Loading budget 216 768 B stays as
measured). Build #14 is the first build that passes Loading, a new game and the chapter-2 save. Package **v3**
(= v2 + button-bar label rule + 408 DLC pool copies re-synced to the shortened Skill00 fragments,
`translation_copy.py --resync`; `translation_check` 0 errors) is on Drive; building config00/configst from it
reproduces build #14 byte for byte. Next: the user builds the FULL patch locally (`HOKUS_POKUS.bat`, fresh
branch ZIP, v3 in `pakiet_EN\`) and tests the chapter-2 save on the complete set, then plays from the start —
the 94 other containers have never run in-game past Loading. Details: `EXPERIMENT_LOG.md` §21.25.

**Previous (2026-10-15, afternoon): the chapter-2 save crash has a concrete cause in the writer — a THIRD
record-relative pointer, u16 `+52` (start of the skill's parameter words after the texts), was copied verbatim by
builds #6–#13**, so every record whose English changed length had the game read its parameters from the wrong
place (build #12: 1 152 of 1 469 Skill00 records, 458 pointing into the text). Round 7 (Y1 OK, Y2 OK, Y3 crash,
A OK, B OK) ruled out record positions and save contents; the stale-pointer counts match the matrix exactly.
`item_skill_write` now moves `+52` with the texts and refuses sources that break the rule (suite 1 093 OK).
Round 8 kit `RUNDA8_build14.zip`: Y5 (= Y3 with only `+52` fixed) decides pointer vs size; **build #14** = #13 +
the fix in all five convention-B members; PLAN_B size ladder only if Y5 crashes. Details: `EXPERIMENT_LOG.md`
§21.23–21.24, `TECHNICAL_FINDINGS.md` (three pointers).

**Previous (2026-10-15, day): round 6 in-game — Z1 crash, Z2 OK, Z3 crash ⇒ the rebuilt `srwDL_Skill00.bin` ALONE
makes the chapter-2 save (from the original JP game) crash on load** (`CPU Jump to ffffffff`, RA `08a62f34` — a
different signature from the Loading crash). A full cross-record scan of the original Skill00 found no
offset references between records (only `+32`/`+36`, both rewritten), so the remaining split is layout (save
stores record positions) vs size vs English content: round 7 kit `BISEKCJA_SEJW_runda7.zip` (Y1 same-size
shifted layout, Y2 210,942 B, Y3 216,518 B = build #12 size, all Japanese text) plus the A/B own-save tests.
If Y1 crashes, the Skill00 layout must be frozen before release and JP-game saves declared incompatible.
Details: `EXPERIMENT_LOG.md` §21.23.

**Previous (2026-10-15, night): build #12 WORKS in a new game** (Loading, mission, Spirits list and descriptions
in English, no crash in a longer session) — the `+32` finding is confirmed. Still open: loading the user's save from
mid-chapter 2 crashes right after "Start" (same as #11); convention-A members show no position-dependent words,
DLC_ID identifiers are untouched, so round 6 bisects the members in-game (`BISEKCJA_SEJW_runda6.zip`, Z1–Z10 +
two save experiments). Button-bar labels overflow because the bar places icons at the JAPANESE label width:
new rule `cells(EN) <= cells(JP)` for one-line `sysmes.bin` labels ≤ 16 B (`tools/label_fit.py`,
`config/label_fit_rules.tsv`, 280 rows → 4 left), shipped as **build #13** (= #12 + shorter labels;
`configst.cpk` md5 `27a8cdea…`). Details: `EXPERIMENT_LOG.md` §21.22.

**Earlier (2026-10-15, evening): build #11 LOADS in-game (Loading, first mission) — the Skill00 size budget
holds (W1 217 090 B loads, W2 218 110 B crashes). Two further crashes it showed (pilot → Spirits → hover; loading a
mid-chapter-2 save → crash before the intermission) are attributed to a second position-dependent record word the
writer never rewrote: `i32@+32 = -record_offset` in every convention-B record (2 230/2 230 originals; stale in
2 215 records of build #11). `item_skill_write` now rewrites and proves both `+32` and `+36`; 12 spirit-command
names the export had skipped (集中/鉄壁/感応/信頼 ×3 levels, hidden behind a two-byte preamble) were added by the new
`tools/record_rows_refresh.py`. **Build #12** (`config00.cpk` md5 `3c56686d…`, same sizes as #11; `configst.cpk`
md5 `856f8ba5…`) is on Drive as `WGRAJ_build12.zip` and awaits the in-game test (chapter-2 save → intermission;
Spirits hover). Also observed: English menu texts overflow their boxes — 56 % of the filled UI rows are wider than
the Japanese in half-width cells; a width rule for menu/table categories is the next design item (needs
screenshots to calibrate). Details: `EXPERIMENT_LOG.md` §21.21, `TECHNICAL_FINDINGS.md` (two pointers).

**Earlier the same day: the crash of `config00.cpk` is a SIZE BUDGET of the skill table member
`srwDL_Skill00.bin` itself** (in-game matrix: U2 = tighter container + big Skill00 crashes, U1 = tighter container
+ original Skill00 works, W5 = 217 086 B with refreshed CPK header works; T3 217 086 B works, T4 221 182 B
crashes). The full English of the 2026-10-14 package needs 228 202 B (+19 244 B); the budget is now built in
(`item_skill_write.SKILL00_LIMIT = 216 768 B`; a member over it refuses its WHOLE container - "NOT written",
exit 1). `tools/skill_shrink.py` + `config/skill_shrink_rules.tsv` (141 rules: shorter skill names ≤ 13 B,
` LvN` → ` LN`, Prevail/Break/Cmd:/Carrier/Ship/foe/cut/Dmg/Regen/Crit…, tokens guarded) bring the member to
**216 518 B** (568 B under the proven-safe size). **Build #11** (`config00.cpk` md5 `abacf828…`, CPK header
byte-identical to the working W5; `configst.cpk` md5 `512e2397…`) is on Drive as `WGRAJ_build11.zip` and
awaits ONE in-game test (KROK 1 = config00 alone, KROK 2 = both). Shrunk package of record:
`pakiet_EN_2026-10-15_ciasny.zip`. Details: `EXPERIMENT_LOG.md` §21.20.

**Latest in-game result (2026-10-14, user, PPSSPP): build #9 (`config00.cpk` with the unit-name fix) CRASHES
exactly like #8/#6 at the "Loading" screen right after the DLC scan (`memcpy_jak`, `Read/Write Block at
00000000 (sz: 0)` — per the PPSSPP source that means a `memcpy` with `bytes > 0` and a NULL `dst`/`src`).
Bisection so far: A (`configst.cpk` only) works to the title menu; B (`config00.cpk` only) crashes with #8 and
#9. A structural review of `srwDL_Skill00.bin` then found a real writer defect: in every convention-B record
(Skill00/Item00/Item/Spirit/StatusChange) the u32 at `+36` is the fragment pool's position RELATIVE to the
record (`tail_offset − record_offset`, 2230/2230 original records measured); builds #6–#9 copied it
verbatim (and mis-read 46 as record cross references), so after growth 1468/1469 Skill00 and 274/300 Item00
records pointed into the record area instead of the pool table. `item_skill_write` now recomputes the word
for every record and proves it on the output (fail-closed on sources that break the rule). Build #10
(`config00.cpk` md5 `37251325…`, `configst.cpk` md5 `ee1aae95…`) differs from #9/#8 only in those words (plus
pool parity in configst) and is on Drive with sub-file bisection variants V1–V6 (`tools/container_mix.py`)
as plan B. UPDATE (same night): build #10 STILL crashes; sub-file bisection says V1 (DLC list only) works and V2 (the
rebuilt `srwDL_Skill00.bin` alone, pool pointers right) crashes — so the pointer defect was real but not
the cause. Round 2 (`tools/member_variants.py`, S1–S7: size / records vs pool / names vs effects / halves)
is with the user; no name-based skill references were found in any other file.
2026-10-15: S1 (ORIGINAL Skill00 + zero padding to the built size) crashes too, so the English text is
not needed for the crash - the file's size is (or the padding); round 3 is a size ladder T1-T6 (Japanese
text + spaces, structurally valid growth of +2/+4/+8/+12/+16/+19 KB) to find the budget.
T6 (+19 KB, Japanese text) CRASHES: the size is the cause. Round 4 asks which size - the whole `.pac`
(U2: sub-files packed at 64 B instead of 2048 B, container smaller than the original even with the
grown skill file - a fix if it works) or the skill file alone (then the T1-T5 ladder gives the budget).
`cpk_write` now also refreshes EnabledPackedSize/EnabledDataSize (stale in builds #6-#10; T7 tests it).
Round 3 complete: T1 and T3 (+8 128 B) work, T4 (+12 224 B), T5, T6 crash - the growth budget of the
skill file (Japanese text) is between +8 and +12 KB against the +19 KB English needs; 0x35000 is the
suspected fixed buffer. Round 5 (W1-W5) pins the exact boundary; round 4 (U2/U1) decides whether the
limit is the whole container (fix: pack sub-files at 64 B) or the skill file alone (fix: shorter text).
Details: `EXPERIMENT_LOG.md` §21.13–21.17, `HANDOFF.md` §7.
The project is NOT a finished translation; no full in-game acceptance exists.

## Target

- Game: Japanese PSP **Super Robot Taisen: Operation Extend** (SRT/SRW OE).
- Title/content ID reported by the user: `NPJH50521`.
- Base image reported by the user: `SRW OE 1.08.iso`, 679,243,152 bytes — the PSP UMD disc with **chapter 1 of 8** (user-provided context, 2026-10-09); chapters 2–8 are PSN DLC in the user's game folder (`D:\SRWOE\NPJH50521`).
- **End goal (stated by the user, 2026-10-09): the whole game translated into English and delivered as a patch**, following the SRW Z workflow (`retro-trans/SRW-Z`, already in `EXTERNAL_REFERENCES.md`): extract every string, translate, re-apply with an exact round-trip, verify against the game, and ship an `.xdelta` patch the user applies to their own Japanese copy — chapter 1 from the disc ISO, chapters 2–8 from the DLC files (chapter 4 only after the user decrypts the `*04` packages).
- User has the DLC data in the PPSSPP memory-stick game directory and wants an **English** translation.
- Translation source: the Japanese game itself. The user considers the old Akurasu script too low-quality to use as a source.

## Verified milestones

Milestones 9–15 record the detector and audit at earlier revisions. The half-width-aware figures in milestone 16 supersede their earlier candidate counts and derived candidate-range overlap totals; milestone 17 broadens Japanese-script coverage without changing the candidate inventory, milestone 18 adds a count-only private-use diagnostic, and milestone 19 adds a separate punctuation-only review supplement without changing the main candidate/range set; milestone 20 adds same-EVNT context for those leads, milestone 21 records the target one-command local ISO/DLC workflow, milestone 22 implements its first read-only inventory slice, milestone 23 records the Windows/`.EDAT`-heavy input and converter-location constraints, milestone 24 prepares a mocked batch CPK extraction driver, milestone 25 adds one-time Windows INI path configuration, milestone 26 adds an unfiltered inventory of every `FF FF` marker start, milestone 27 inventories every nonempty NUL-delimited `.dat` run, milestone 28 profiles text-like DAT cohorts and a repeated `_Entry.dat` offset lattice without assigning field semantics, milestone 29 compares CP932 with Python's standard Shift-JIS codec on all BIN/DAT review spans without printing source text, milestone 30 adds an all-run BIN NUL inventory with literal-marker overlap flags, and milestone 31 extends the codec differential to those BIN runs. Older observations remain useful as historical results.

1. `imenu01.EDAT`, `eventP01.EDAT`, and `config01.EDAT` all had the first four bytes `43 50 4B 20` (`CPK `).
2. YACpkTool extracted `imenu01.EDAT` and `eventP01.EDAT`.
3. The extracted `eventP01` package contained multiple scenario/event files, including `DL102_20.bin` and companion `.dat` files.
4. Japanese dialogue is visibly present in `DL102_20.bin` when viewed as Shift-JIS/CP932 in Notepad++.
5. A no-change repack/re-extract cycle of `eventP01` was reported to preserve `DL102_20.bin` byte-for-byte. The exact digest from that earlier comparison was not saved; the SHA-256 of the later uploaded sample is recorded in `FILE_INVENTORY.md`.
6. The user ran the candidate text-dump heuristic on `DL102_20.bin`; it included the known Japanese text and the output file appeared to have 215 lines.
7. Direct analysis of the supplied archive reproduces 181 Japanese-containing candidate spans in `DL102_20.bin`; 34 embedded CR bytes explain the 215 physical lines because the original formatter replaced LF but not CR.
8. Four row examples were reviewed: readable candidates at `0x158C` and `0x1D68`, and coherent Japanese candidates at `0x14E8` and `0x25A8` with different post-text byte patterns.
9. The ZIP is valid and contains 22 BINs; a CP932 heuristic finds 3,241 candidate spans across them, with 627 single-NUL suffix cases whose pre-NUL prefixes all contain Japanese and whose suffixes contain no Japanese.
10. The clean-row raw endings show Japanese bytes followed immediately by `00 00`; noisy rows instead have `00`, then `76 01` / `22 02`, then `00 00`, then `10 00`. Exact field meanings remain unknown.
11. A diagnostic JSONL export with 3,241 unique file/offset IDs was generated locally; unknown suffix bytes remain separate. A later quality audit found that all prefixes strictly decode as CP932 but only 3,240/3,241 round-trip byte-for-byte, so the remaining candidate is now flagged for review. The initial export stage had five synthetic tests.
12. A read-only companion audit mapped 42 Japanese-bearing NUL-delimited runs across 22 `_ext.dat` files and measured numeric overlaps from all `_edit.dat` and `_Entry.dat` files against heuristic BIN ranges. The observations are reproducible; no companion field semantics have been identified.
13. A byte-pattern probe verified EDAT size/count relations and EVNT block-boundary arithmetic across all 22 BINs: 319/319 EVNT boundaries match the next tag or EOF, every EVNT is followed by ECHK at `+12`, and all 3,241 heuristic candidates fit inside one EVNT block. This is top-level framing evidence, not a decoded event parser.
14. All 319 EVNT blocks have an observed ECHK endpoint chain starting at `EVNT+12` and ending at little-endian u32 `200`; chain length equals the literal EVNT `+8` word (309 one-segment, seven two-segment, three three-segment chains). The chains cover all 332 ECHK tags. All 3,241 heuristic `FF FF` markers follow the terminal u32 `200`; the minimum marker gap is 34 bytes. Stratifying the 1,066 tentative rows by chain position shows repeated layouts but no decoded fields. Numeric comparison of row column 2 finds 541 overlaps with heuristic candidate spans (539 prefixes, four exact candidate starts); 524 matches are in spans before the owning EVNT block, 11 within it, and six after it. Of the 539 prefix hits, 300 fall on CP932 character-byte boundaries versus a 50.7% matched-candidate baseline; this does not resolve pointer use. A reproducible same-row-value cross-BIN control gives same-BIN full-span overlap of 541/1,056 in-range values (51.2%) versus 9,846/21,716 other-BIN row/target pairs (45.3%); nonzero-only rates are 53.5% versus 47.4%, with positive per-source lift in only 9/22 BINs (mean -5.1 pp; median -7.5 pp). The control is coarse and non-independent, and does not support a consistent paired-BIN pointer interpretation. A short probe of absolute and six record-relative c2 formulas also found no compelling address pattern: absolute c2 has 541/1,011 nonzero in-file candidate overlaps but only 11 are in the owning EVNT block; the tested relative formulas yield 396–437 full-span hits from 880–986 nonzero in-file targets. Fifteen synthetic tests now pass.
15. Refined the read-only candidate detector with review-only quality signals. Across the sample ZIP there are 3,477 overlapping-allowed `FF FF` byte-start positions; the sequential scan selects 3,402 outer starts, with 49 additional starts inside bounded spans and 26 overlapping an outer marker. Of 3,402 spans, eight are empty and 153 nonempty spans contain no Japanese; the remaining 3,241 are candidates under the earlier wide-script-only rule. Every proposed prefix strictly decodes as CP932, but one does not byte-roundtrip; two candidates contain nested markers/private-use codepoints, and 20 have only one Japanese-matched codepoint. These signals flag possible false positives without dropping any rows. Fifteen synthetic tests passed at that revision.
16. Expanded the detector to recognize half-width Katakana in the proposed pre-NUL prefix and to reject suffix-only matches from candidate export. The current inventory has 3,277 candidates: 36 half-width-only matches, of which 27 fail strict CP932 decoding and nine round-trip. Across all candidates, 3,250 strictly decode and 3,249 round-trip. For 627 single-NUL cases, every prefix has wide-script Japanese; none of the suffixes has a wide-script match, but 497 suffixes decode to half-width kana (likely byte-field collisions). The broader `_ext.dat` scan also surfaces five two-byte half-width/control hits at offset 0, likely binary/header noise. A nested-marker alternate-start pass found zero wide-script inner prefixes across 49 markers (23 half-width matches, none unique to inner starts). Updated companion metrics remain inconclusive about c2 pointer semantics; all 19 synthetic tests passed at that revision. See `CANDIDATE_SCAN_AUDIT.md` for the current exact counts.
17. Broadened Japanese-script matching to include kana iteration/long-vowel marks and CJK compatibility ideographs, which CP932 can encode but the earlier narrow regex missed. The archive still has the same 3,277 candidate IDs and unchanged strict-decode/roundtrip and review-flag totals; four sample prefixes now have more complete script-codepoint counts. Added synthetic tests for `﨑`, `々`, and `ー`; all 21 tests passed at that revision.
18. Added a count-only report for otherwise non-Japanese prefixes that CP932 decodes to private-use codepoints; they are not promoted automatically. Across the archive, 39 of 117 unmatched prefixes contain 59 such codepoints (U+F8F2 x4, U+F8F3 x55); 20 strictly decode/round-trip and 15 contain nested `FF FF`. The signal is ambiguous because `FE`/`FF` marker-adjacent bytes map into the private-use area. A synthetic test confirms a PUA-only prefix remains excluded; all 22 tests passed at that revision.
19. Added a separate punctuation-only review scan/export, leaving the main 3,277 candidate IDs and companion range calculations unchanged. It finds 35 leads in 12 BINs; 34 strictly decode and round-trip, 33 consist only of Japanese punctuation plus CR/LF, none has a single-NUL suffix, and 22 share the U+2026/U+2026/U+3002 codepoint pattern. A companion framing check places all 35 wholly inside EVNT blocks, after ECHK terminal u32 200, with a 34-byte minimum gap. These are likely text leads, not validated strings; all 25 tests passed at that revision.
20. Added same-EVNT context reporting for punctuation leads: the 35 leads occur in 22 EVNT blocks, each containing at least one main Japanese-script candidate; 33 leads have a preceding and 33 a following main candidate in their block. This adds context without merging them into candidate or pointer-range totals. All 26 tests passed at that revision.
21. Recorded the requested one-command local workflow: configure or place the source set once, then have one offline entrypoint recursively discover, extract, scan, apply reviewed translations, repack, and verify all supported files without manual unpacking, extension changes, or per-file tool launches. The plan requires untouched originals, separate outputs, content-based detection, explicit unsupported-format reports, and no writes until text/archive round-trip gates pass.
22. Implemented `tools/inventory_local_inputs.py` as the first read-only automation slice. It recursively hashes inputs, probes CPK/ZIP/PBP/SFO/ISO9660-PVD signatures independent of filename suffix, reports duplicate-content paths, groups signatures by extension hint, and skips symlinks. Seven synthetic tests passed at that revision; it identified the supplied `eventP01.zip` by its ZIP signature without extracting or changing it. The full suite had 33 tests then. This is not a container parser or the planned end-to-end pipeline; the base ISO/DLC remain unprocessed.
23. The user clarified the eventual local input shape: one source directory will contain mostly `.EDAT` files and one ISO; the ISO may optionally be pre-extracted if required, and the user can place the previously used converter locally. The workflow is now designed for a flat/mixed root, content-based CPK detection within `.EDAT`, one configured YACpkTool distribution invoked in batch without per-file user action; the user's Windows converter path may be anywhere accessible (Desktop or game folder, with required DLLs beside the executable), and direct ISO handling is preferred (a pre-extracted tree is only a fallback). The archived YACpkTool README documents `-L`/`-X`/`-P` and marks `-R` experimental; the `.EDAT`-path behavior and no-change round trip still require a disposable-copy test. No ISO/DLC or converter executable was processed in this phase.
24. Prepared `tools/extract_cpk_batch.py`, a dry-run-default batch driver that detects CPK signatures in a mixed directory, lists/extracts all matching `.EDAT` inputs using one configured/discovered YACpkTool path, isolates outputs, reports unknown `.EDAT` files, and checks source hashes before/after tool calls. Seven synthetic tests use a mocked CLI, including path-with-spaces, failure, source-mutation, and report-path cases; a synthetic mixed-directory CLI dry-run reported one CPK, one unresolved `.EDAT`, and one ISO without creating outputs. The full suite now has 40 passing tests. The actual YACpkTool binary and actual `.EDAT` inputs were not available, so real `-L`/`-X`, extension acceptance, and member round trips remain unverified. This is not an ISO reader, packer, or end-to-end pipeline.
25. Added a private Windows INI configuration path for `extract_cpk_batch.py`: input/output roots and an optional converter path are set once, relative paths resolve beside the INI, command-line paths override config, and the tracked example is `config/local-workflow.example.ini`. The user's YACpkTool may remain on the Desktop or next to game files; only a path is needed. Two new config tests pass; the full suite had 42 tests at that milestone. No actual converter or game assets were used in that phase.
26. Added `--export-marker-inventory-jsonl`, an unfiltered local inventory of every literal `FF FF` start, including nested/overlapping alternatives, empty rows, and raw proposed spans. Re-audited the previously uploaded 162,546-byte `eventP01.zip` (SHA-256 `187cc54669be48909c99f9f1c83acad032e57858680753381ea5fae9638fe0c7`) restored to ignored `local/`; the user's ISO and DLC were not read or processed. The inventory contains 3,477 unique marker rows (3,402 greedy-selected, 75 alternate; all bounded), and byte-by-byte verification found zero marker/span/prefix-suffix/terminator mismatches. The alternates contain 25 half-width-only matches but no wide-script or punctuation matches. No proposed prefix has an ASCII printable run of 3+ characters or non-ASCII letters/numbers without detected Japanese script; this is not coverage outside `FF FF` spans or validation of string boundaries. Three synthetic tests were added; the full 45-test suite passed at that milestone.
27. Added `tools/audit_event_dat_runs.py`, which inventories every nonempty maximal nonzero-byte run in all `.dat` files without assuming it is text. The previously supplied ZIP yields 6,288 unique rows across 66 files; offset/raw-byte/NUL-boundary verification found zero mismatches. The 1,352 broad Japanese-script matches in `_Entry.dat` are noisy (1,122 half-width-only; only eight contain two wide-script characters and none contains three); all 76 `_edit.dat` half-width hits are 2–3 bytes and include non-newline controls. The 42 wide-script `_ext.dat` runs reproduce prior results; two also contain a nine-character ASCII run and remain mixed-script review leads. Three tests were added; the full suite now has 48 passing tests. The JSONL contains decoded data and stays ignored local; no ISO or DLC was opened.
28. Extended the DAT-run audit with a print-free review-cohort profile. All 42 `_ext.dat` rows with at least two wide-Japanese codepoints strictly decode and round-trip as CP932 without non-newline controls, PUA, or replacement characters; 20 rows at `0x18`/`0xB8` are one repeated 48-byte payload, and 22 unique 10–28-byte rows begin at `0x158`. All 42 are NUL-bounded on both sides; seven LF bytes occur once each in seven `0x158` rows (five at relative byte 3, two at byte 9), with no CR. The complete 116-run map uses eight offsets; each of the 15 runs at `0x180` and `0x182` is a one-byte `0x01`, still uninterpreted. `_Entry.dat` has 569 NUL-bounded runs at offset modulo 64 `0x1A` (548 length 7, 539 control-bearing, 530 half-width; raw C0/DEL at byte +3 in 320 and +6 in 547 of the seven-byte runs); five seven-byte runs in one file meet strict/roundtrip/control-free criteria, but no two-wide-character `_Entry` run passes the clean cohort. The alignment is a review lead, not a decoded schema. Added a synthetic profile test; all 49 tests pass. No game text is printed and no ISO/DLC was opened.
29. Added `tools/audit_event_codecs.py` to compare Python CP932 and `shift_jis` across every literal BIN marker prefix and every companion DAT NUL-run without printing decoded text. Among 3,277 greedy Japanese-script candidates, 3,245 round-trip under both codecs, five are strict CP932-only (four wide-script, one half-width-only), and 27 fail strict decoding under both. Eighty-two rows differ at 93 Unicode codepoint positions (U+FF5E/U+301C 90 times; U+FF0D/U+2212 three times), without decoded-length changes. All 42 clean wide-script `_ext.dat` leads round-trip identically under both. Added three tests; all 52 project tests pass. The result does not resolve Notepad++'s exact codec implementation and does not justify normalizing punctuation or changing raw bytes.
30. Added `tools/audit_event_bin_nul_runs.py`, which inventories every nonempty NUL-delimited BIN run and annotates overlap with all literal `FF FF` span envelopes without asserting either boundary model. The sample produced 33,827 rows across 22 BINs. Outside every marker envelope, 263 NUL-bounded runs contain at least two wide-Japanese codepoints; 257 strictly decode and round-trip under CP932 without PUA, replacement, or non-newline-control flags, and the clean cohort has 216 unique payloads, three of which recur as byte substrings in four main marker prefixes. The six other leads are all NUL-bounded and contain one raw `0x01`/`0x02` control byte each; two 34-byte `DL103_20.bin` payloads are identical at their two offsets. The same scan finds 525 raw printable-ASCII NUL-runs >=3 bytes (180 unique); all letter-bearing rows are 4–6 bytes and only one has letters plus a space, at the EDAT header. A pre-run 16-byte/u32 relation covers 134 runs; 133 are clean wide-Japanese leads, but its aligned extent strictly decodes as CP932 for only 78/133 and is never used as a trim boundary. All 263 lie inside 48 EVNT blocks after their ECHK terminals; one 512-byte `DL103_11.bin` block has no literal `FF FF` markers but contains three clean NUL-runs. Two other clean 52-byte rows at `DL105_30.bin@0x2FEC` and `DL105_40.bin@0x3A30` share a 16-byte ASCII sequence found only at those two locations among the 88 BIN/DAT members. The ignored JSONL keeps all raw runs and decoded diagnostic views; the CLI prints no game text. Six synthetic tests were added; the full suite now has 58 tests. This is a new string-like review cohort, not a validated parser or translation table. No ISO/DLC was processed.
31. Extended `tools/audit_event_codecs.py` to compare all BIN NUL-runs as well as BIN marker prefixes and DAT runs. Across 33,827 BIN NUL-runs, 3,511 decode strictly only under CP932 and 4,344 under neither codec. Of the 257 clean outside-marker wide-script runs, all round-trip under CP932 and 15 are CP932-only under Python `shift_jis`; two more have one U+FF0D/U+2212 mapping difference each, with no byte-length change. The no-text summary does not validate boundaries or semantics.
32. Rechecked all 75 non-greedy `FF FF` starts against their nearest greedy-selected parent and EVNT/ECHK framing. Every alternative ends no later than the parent's `00 00` stop, lies with its terminator in the same valid EVNT block after the observed ECHK terminal, and adds no wide-script or punctuation prefix; the 25 half-width-only alternatives remain review-only. Separately profiled all 627 single-NUL candidate splits: their prefixes strictly decode and byte-round-trip under CP932 (7–123 bytes, median 59), while suffixes are 2–3 bytes and 132 carry one raw `0x01`/`0x02`/`0x03` byte. This supports preserving the proposed split but does not validate the string boundary or suffix semantics; no source bytes were trimmed.
33. Exact-byte cross-searched the five clean seven-byte `_Entry.dat` rows across all 88 members. Each occurs only at its own offset in `DL102_90_Entry.dat`; their profiles mix ASCII with zero or one wide-Japanese and one or two half-width-Katakana codepoints. Treat them as short mixed-field review leads, not confirmed prose or identifiers; surrounding record semantics remain unknown.

34. Added `tools/extract_event_text.py`, a read-only deterministic extractor. It repeats the candidate scanner's greedy `FF FF … 00 00` walk, checks that walk against the existing audit at run time, and partitions each event BIN into text units, other selected marker spans, unselected gaps, and any unterminated tail, with exact raw hex. The 3,277 text units keep the existing `file@HEX` IDs, and their prefix and suffix bytes match the candidate export. Each prefix has a lossless CP932 placeholder view in which controls, private-use mappings, invalid bytes, and non-byte-exact pairs appear as `{XX}`/`{XXXX}` tokens. On the restored 22-BIN sample, the segments cover all 333,732 bytes; the exported files reload from disk and pass the same checks; raw and placeholder-view rebuilds match each file's SHA-256; and two runs produce byte-identical exports. The suite has 84 passing tests. Boundaries remain heuristic. No reinsertion, field decoding, or game-load test was performed.

35. Added the first one-click local run slice: `RUN_PIPELINE.bat` and `tools/run_pipeline.py` (see [`ONE_CLICK_RUN.md`](ONE_CLICK_RUN.md)). After a one-time folder setup it inventories inputs by content signature, runs preflight checks, probes the converter (original `.EDAT` name first, `.cpk` staging copy only as fallback, captured then console output), extracts unique CPKs (nested up to depth 2), exports and verifies event text for each package, runs a CPK round-trip repack gate, and writes `REPORT.txt`, `registry.json`, and CSV files. It was tested only with synthetic data and a fake converter (`tests/test_run_pipeline.py`, 34 tests; full suite 118 tests OK). Its first real run is recorded in item 36. Repacking to the game, text insertion, and ISO unpacking are **not** automated.

36. First real run of the one-click slice on the user's Windows PC (2026-10-09; details in [`EXPERIMENT_LOG.md`](EXPERIMENT_LOG.md)). Status `completed`: 424 packages reported extracted and 0 failed; 11,389 member files; 83 text packages verified; repack round trip passed for the smallest package. The captured-output probe crashed the user's YACpkTool build (exit code 3762504530, 0xE0434352), so extraction ran in console-output mode, where YACpkTool's error lines are not checked. Not processed: 47 non-CPK `.EDAT` files, 3 metadata containers, and the ISO. Completeness of extraction is **not** verified. Repacking into the game, text insertion, and ISO unpacking are **not** automated.

37. Analysed the first real run's `-L` listing for one package (`NPJH50521/bacb01.EDAT`). The user's upload landed on PR #8's branch, which belongs to another session, not on this one. The listing has 541 entries but only 260 distinct names. The converter wrote one file per name and exited 0, so 281 entries (about 52% of the content bytes) have no file, while the pipeline had recorded the package as `extracted`. Added a listing check that compares each package's entries with its files by count and name. Packages with repeated names, or with a listing that cannot be verified, now fail and their output is removed. Also fixed the repack gate, which had repacked a package whose only member is 0 bytes, and redacted the converter logs. Whether the hidden entries differ in content is unknown, and so is the cause of the ISO file being 5,533,072 bytes longer than its descriptor. The next run will show how many of the 424 packages are affected. Repacking, insertion, and ISO processing are **not** automated.

38. Rechecked the eight control-bearing `_Entry.dat` runs with two wide-Japanese codepoints. One five-byte round-tripping payload ending in raw `0x03` occurs as a full run at `DL104_30_Entry.dat@0x00DC` and as a substring at `@0x005C`/`@0x009C` inside longer runs with `0x02`/`0x03` controls. This is a repeated inner-span lead, not proof of string boundaries or a control protocol; all original runs remain intact.

39. Extended `audit_event_dat_runs.py` with a metadata-only one-wide `_Entry.dat` profile. The sample has 222 NUL-runs with exactly one wide-Japanese codepoint; 86 pass strict/exact CP932 and no-control/PUA/replacement checks. Those rows contain 50 unique payloads; 18 repeat groups cover 54 rows, 16 across files, with max multiplicity nine. The 86 are all NUL-bounded, have no CR/LF, and are concentrated at record-relative `0x12`, `0x16`, and `0x1A`. They remain one-codepoint leads, not confirmed text. Added a synthetic stdout test; all 59 tests pass, as do `py_compile` and `git diff --check`.

40. Added `tools/iso9660.py` for read-only ISO9660 PVD directory/member inventory and first-four-byte CPK-signature detection. It validates both-endian fields and extent bounds, supports adjacent multi-extent files, and explicitly does not extract members; Joliet names are ignored and interleaved/multi-volume records are unsupported. Integrated metadata into `inventory_local_inputs.py` and separate nested ISO CPK candidates from top-level extraction plans in `extract_cpk_batch.py`. Six ISO/inventory tests and two batch-reporting tests were added; all 66 tests pass. No actual ISO/DLC or converter was opened or processed, and no output was extracted or modified.

41. Ported the valuable commits from PR #8 (branch `arena/382dda12-mtgcrawler`, written after PR #7 was merged) into this branch with `git cherry-pick -x`: `40bfa82` (research notes), `7efa795` (one-wide `_Entry.dat` profile in `tools/audit_event_dat_runs.py`), and `558d9d6` (read-only ISO9660 directory indexer `tools/iso9660.py` with tests, plus inventory and batch-driver changes). Their STATUS items are renumbered 38–40. The uploaded zip was not ported. PR #8 was closed at the user's request; its branch is to be deleted by the user. The ISO indexer is tested with synthetic images only (7 tests, plus a corruption check). Full suite 131 OK.

42. Second real run of the one-click slice on the user's Windows PC (2026-10-09; details in [`EXPERIMENT_LOG.md`](EXPERIMENT_LOG.md)). Status `completed_with_failures`: 346 packages (189 extracted, 157 failed); listing check verified 189, incomplete 41 (duplicate entry names, all `bacb*`/`bseq*`), unverified 116 (listing rows the parser could not read, mostly `face*`/`mesbmp*`/`mesbtl*`/`mov*`/`n1-bcam*`); event text 39,103 units from 80 packages, 0 failed; repack gate passed on a package with non-empty members. The first run's "424 extracted, 0 failed" is corrected: extraction completeness is now measured, and 157 packages fail closed. The package count dropped from 424 to 346 because failed packages keep no output, so their nested CPKs are not discovered. Repacking into the game, text insertion, and ISO processing are **not** automated.

43. Widened the listing parser with a single-space fallback for narrow columns (validated against the real `bacb01` listing and a narrowed copy of it), added raw-row diagnostics and unknown-input head-byte groups to `REPORT.txt`, and copied the read-only ISO inventory into `registry.json` (136 tests OK). The 116 unverified packages are expected to verify once their real row layout is confirmed. The 41 duplicate-name packages still need a read-only CPK table reader or an ID-extracting converter to recover the hidden entries. Repacking, insertion, and ISO processing are **not** automated.

44. Analysed the second run's full logs and registry (uploaded as `20261009-194153.zip`; details in [`EXPERIMENT_LOG.md`](EXPERIMENT_LOG.md)) and rewrote the listing parser around each listing's own column header. All 346 listings now parse; the 157 failures are exactly explained: 42 listings have no filename column (the converter writes ID-named files, e.g. `ID00000`), 59 have no ID column, 16 print a `,00` percent for 0-byte entries, 2 print a thousands separator in the `Content files` count, 2 have one console-mangled name each, and 38 have duplicate entry names hiding 1,111 entries / 206,898,244 bytes (197.3 MiB). The check now verifies name **and size** per file, and entry count plus the size multiset for ID-named packages; all 189 extracted packages verify against real data. The 47 unknown inputs are identified by signature: 20 PSP EDAT and 27 AFS2. The three text packages that left the export contributed 0 units, so the 39,103-unit total is unchanged. Repacking into the game, text insertion, and ISO processing are **not** automated.

45. Third real run with the rewritten parser (2026-10-09, run `20261009-214604`; details in [`EXPERIMENT_LOG.md`](EXPERIMENT_LOG.md)). Status `completed_with_failures`: 377 packages (337 extracted, 40 failed); listing check **verified 337, incomplete 38, unverified 2, not checked 0** — exactly the two known classes remain: the 38 duplicate-name packages (1,111 hidden entries, 197.3 MiB) and the 2 packages with one console-mangled name each (`robo01`, `robo03`; every other name and size matches). Layouts: 246 full, 89 no ID column, 42 no filename column. Event text: 39,103 units from 81 packages, 0 failed. Repack gate passed. The report now also prints why a read-only ISO index failed (the real ISO's index returned `unsupported`; the error is in the registry). At the user's request, the old zip upload commits were removed from the branch history (rebase plus `--force-with-lease`; the leftover PR #8 branch was deleted; the closed PR #8 page still exposes its zip through GitHub's pull refs, which needs GitHub Support). Repacking into the game, text insertion, and ISO processing are **not** automated.

46. Fourth real run (run `20261009-215909`) reproduced the third run exactly (337 verified, 38 incomplete, 2 unverified; text 39,103; gate passed) and printed the ISO index failure: `ISO9660 extent extends beyond the image volume` — a member extent ends beyond the PVD's declared volume, consistent with the file being 5,533,072 bytes longer than its descriptor. The read-only ISO index now tolerates such trailing data: extents beyond the declared volume but inside the file become warnings with counts (`extents_beyond_volume`, `max_extent_overflow_bytes`, `last_extent_end_bytes`, `trailing_bytes_after_last_extent`), extents beyond the file are still rejected, and the report carries the beyond-volume note (145 tests OK). At the user's request, the five `szybkoiwyraznie-rgb-patch-1..5` branches (personal web-upload commits, text files only — no binaries found) were deleted; `arena/01a0437d-mtgcrawler` was left untouched (its non-base commit is an agent commit with the `Co-authored-by: arena-agent` mark), and `main` has no user commits. The user's personal commits remain reachable only through GitHub's pull refs, which needs GitHub Support. Repacking into the game, text insertion, and ISO processing are **not** automated.

47. Fifth real run (run `20261009-222046`): identical extraction results (337 verified, 38 incomplete, 2 unverified; text 39,103; gate passed), and the ISO question is answered. The read-only index succeeds: **80 files, 6 directories, 63 CPK-signature members** inside `SRW OE 1.08.iso` (not extracted). The 5,533,072-byte descriptor mismatch is fully explained: **1 member extent ends beyond the PVD volume by exactly 5,533,072 bytes**, ending exactly at the file's last byte — the descriptor understates the volume by that member's tail; the image is complete and internally consistent. Repacking into the game, text insertion, and ISO processing are **not** automated.

48. The ISO cross-check is done (the user's fifth-run `registry.json`, commit `da4d1cc`): `SRW OE 1.08.iso` is a **PSP UMD image** (`PSP_GAME/`, `EBOOT.BIN`, `UMD_DATA.BIN`; 80 files, 6 directories, 63 CPK-signature members), and the mismatch is the tail of `PSP_GAME/SYSDIR/EBOOT.BIN` (5,531,024 bytes) beyond the declared volume, ending at the file's last byte. The loose `NPJH50521` folder is a different data set: 0 of its 290 CPK-signature files share a name with the ISO's 63 CPK-signature members; only `PARAM.SFO` matches by name and size. The folder is not this ISO unpacked. Added `tools/cpk_table.py`, a read-only CPK table reader (`@UTF` CpkHeader/TOC/ITOC parsing, fail closed, CLI, `entries_match_listing` against `-L` listings), validated on the real 6,272-byte sample: the TOC row (`p0000.pac`, ID 0, size 0) and the ITOC row (ID 0 → TocIndex 0) agree with the package's real listing with no mismatches (150 tests OK). Repacking into the game, text insertion, and ISO processing are **not** automated.

49. User-provided context recorded (details in [`EXPERIMENT_LOG.md`](EXPERIMENT_LOG.md)): the game shipped as a PSP UMD disc with **chapter 1 of 8** (that is the ISO); **chapters 2–8 were sold as PSN DLC**, and the input folder `D:\SRWOE\NPJH50521` holds those PSN-downloaded files. This explains the whole ISO/folder picture: the disc's 00-series packages versus the folder's 01-series-and-higher `.EDAT` names, only `PARAM.SFO` in common, and the folder's 20 still-encrypted PSP EDAT inputs (`*04` files, `evept101.EDAT`) as undecrypted PSN packages. The current workflow already processes the DLC content (the 39,103 text units come from those packages); chapter 1 on the disc is not processed (ISO processing is not automated). Repacking into the game, text insertion, and ISO processing are **not** automated.

50. The CPK table reader is wired into the one-click run as a per-package cross-check (report-only): every package's TOC tables are read with `tools/cpk_table.py` and compared with its `-L` listing; the report adds a `CPK table check (TOC vs listing, report-only)` line and a mismatches section, `packages.csv` gains `table_status`/`table_duplicate_entries`, and the registry stores per-package `table_check` results including the TOC's duplicate-entry counts (the recovery targeting data). A table mismatch never fails a package in this version — the listing check remains the authoritative gate; after a real run shows agreement on all packages, the table check can be promoted to fail-closed (156 tests OK). Repacking into the game, text insertion, and ISO processing are **not** automated.

51. Coverage analysis answered the user's question precisely (details in [`EXPERIMENT_LOG.md`](EXPERIMENT_LOG.md) and [`TECHNICAL_FINDINGS.md`](TECHNICAL_FINDINGS.md)): the DLC folder carries per-chapter data **and** per-chapter menu/config/credit/sprstd (imenu 01–32, config 01–46, credit 01–19, sprstd 01–19), so system/menu text is not disc-only; the 39,103 text units are 25,530 from `eventP*` + 13,543 from `evept*` + 30 from `imenu*`. Missing: chapter 1 (on the disc — `eventP00.cpk` and chapter-1 data/menu), chapter 4 (the `*04` series — 20 still-encrypted PSP EDAT files needing decryption by the user), and the disc-only base/system packages (font, system, tactics, texanm, txa00, u16tbl, navisys, tacsys, taclevup, smap, svicon, logodata, colorlst, bg2d, btlcam, ef*, cprt*, IM*, configst, segu01, semv01–15). No translation exists yet; the translation phase starts only after coverage is complete.

52. Read-only ISO member extraction is wired into the one-click run: every ISO's CPK-signature members are extracted read-only into the run folder's `iso/` directory (the image is never modified) and processed like any package — probed, extracted, listing-checked, table-checked, text-exported. The preflight free-space estimate includes the ISO member bytes; the report and registry record the counts. This brings chapter 1 and the disc-only base/system packages into scope on the next run. Rebuilding or repacking an ISO is still **not** automated; repacking into the game and text insertion are **not** automated (161 tests OK).

53. The 2026-10-10 08:35–11:09 commits (merged with PR #9, recorded late in `EXPERIMENT_LOG.md`) added the colliding-name recovery and the translator workspace: `hidden/<package>/<TOC index>_<name>` entries read straight from the CPK table (CRILAYLA streams decoded with `tools/crilayla.py`, others recorded by their first 16 bytes), `tools/layout_probe.py` (`layout_probe.zip` with the header and table bytes of those packages, including ISO members), `tools/diagnostic_bundle.py` (`diagnostics_<run id>.zip` with a size/SHA-256 index, no game files), hard-linked verified-cache entries with per-package timings, the hidden-entry step for listings with one undecodable name (`robo01`, `robo03`), and `tools/translation_tools.py` (`translation/units.csv` written at the end of every run, plus a checker for filled-in rows). None of this has been run on real data yet; the run status and the listing gate are unchanged by it.

54. Added `tools/boundary_probe.py` and stage 8/9 of the one-click run: read-only, count-only evidence about the exported units. It re-verifies each unit's offsets and prefix bytes against the extracted file, then measures a length-prefix scan (all 96 delta/width/endian configurations), a pointer scan (unit starts as u32 values in their own file), byte context before the marker and after the text, the suffix length and per-byte-position profile, gaps/alignment/pitch, and payload repetition. Every hypothesis carries a control: the length scan against a matched-distribution null (those same field values paired at random with the units' lengths), the pointer scan against `start + 1` searched in the same bytes. Both scans are byte-budgeted and report how much was searched. Results go to `boundary_probe.json`, `registry.json` (`boundary_probe`), and a `Boundary evidence` section in `REPORT.txt`; the diagnostic ZIP includes the JSON, and a probe failure never changes the run status. Synthetic checks: on 3,000 units in pseudo-random bytes the scan found 1,656 chance length hits and the null absorbed all of them (best lift +0.01%); a fixture with a real u16 length field and one with a u32 pointer table both show their expected lift, and removing the structure removes it (16 probe tests; full suite 206 OK, 1 skipped). **Nothing is validated by this yet — it has not seen real event data.** Repacking into the game, text insertion, and ISO rebuilding are **not** automated.

55. Extended the boundary probe before the next real run, so one run answers more questions (probe schema `srw-oe-boundary-probe/2`; 22 probe tests, full suite 214 OK, 1 skipped). Additions: the pointer scan now searches the marker **and** the text-start offsets as u32 **and** u16, in LE and BE, unaligned and aligned, against `marker + 1`/`start + 1` controls, and records where matches fall (by eighth of the file), so a pointer table would be localized; a `FF FF`-inside-a-unit measure (inner markers, how many are followed by wide-script Japanese); a companion cross-check that searches every NUL-delimited run of at least six bytes from each package's `_ext.dat`/`_Entry.dat`/`_edit.dat` files verbatim in that package's BINs; run-wide text coverage from the export manifests (bytes by segment kind, unit flags, control tokens, unterminated tails); and units grouped under their top-level source file (the per-chapter picture). Both scans are budgeted per file and in total and report how much was searched, how many offsets did not fit the width, and how many files were truncated; measured cost is about 0.5 s per 3,000 units. `RUN_PROBE.bat` (and `boundary_probe.py` with no argument, which resolves the newest run folder from the saved config) re-runs the probe against an existing run folder in seconds with no converter call, so later measurements do not need another full run.

56. User-provided context (2026-10-10): the `*04` chapter-4 packages are **already decrypted**, so every input on the user's side is ready. The next run should therefore cover all 8 chapters for the first time; chapter 4's unit count is the check. Not verified by a run yet.

57. **Full run `20261010-142640` on the user's PC (item 56's run) — the first real boundary evidence.** 341 inputs readable; 497 packages, 453 extracted, 44 failed (42 colliding-name packages, now fully recovered under `hidden/`, plus `robo01`/`robo03` with one undecodable console name each); 12,203 member files. **CPK table check: agree 495, mismatch 2, unreadable 0** — the ID matching fixed the 4 blob-layout mismatches from the previous run. Colliding-name recovery was complete everywhere (`bacb01` 541/541 entries, 132,272,768 bytes, `listing sizes match: True`), with 0 compressed entries. Text: 91 packages, **45,325 units** (was 39,103), including `eventP00` (1,582 units, chapter 1 from the ISO) and `eventP04`/`evept104` (3,520/3,562, **chapter 4's decrypted `*04` packages are readable CPK containers**). Probe: 163,523 units in 2,617 files over 114 exports, integrity clean (0 offset problems, 0 marker mismatches, 0 prefix mismatches, 0 missing files). Findings: **no length prefix** (best of 96 configurations +0.6% lift over the matched-distribution null; the scan covers every unit, so this rules it out for the event files too); **no nested strings** (4,757 inner `FF FF` markers, 0 followed by wide-script Japanese); **no fixed record pitch or gap alignment**; the pointer scan was **inconclusive as measured** (1,382 of 163,523 offsets searched before the budget ran out); `_Entry.dat` shares nothing with the BINs (0 of 5,472 runs) while `_ext.dat` shares a little (12 of 242 runs, 11 distinct payloads of 10–24 bytes); and 88% of two-byte suffixes are `00 C9`, with `0000C9000000` the most common 6 bytes after the text. Bundle `diagnostics_20261010-142640.zip` (commit `f728517`), extracted to ignored `local/run-20261010-142640/`.

58. The same run exposed two defects in the probe, both fixed (schema `srw-oe-boundary-probe/3`, 29 probe tests, full suite 220 OK, 1 skipped). **(a) Pooling hid the script:** 118,198 of the 163,523 units and 523 MB of the 529 MB measured came from the 42 recovered battle-data exports, none of which is prose, so every pooled statistic mixed script with binary data. The probe now measures each export on its own, merges it into the pooled evidence, into a `text` or `binary` cohort (decided from the export's own manifest before any BIN is read), and into a per-export row; `boundary_probe.json` has `cohorts`, `per_export`, `text_share`, and `units_wide_script`, and `REPORT.txt` prints a `by cohort` section plus the ten largest exports. On the real manifests the split is 32 prose exports / 45,252 units versus 82 binary exports / 118,271 units. **(b) The pointer scan was starved:** taking the first N values per file let the first huge file spend the whole budget (`files_truncated_by_budget: 2,653`), and the rewrite had also dropped the truncation flag, so an unsearched offset could have read as a negative result. Offsets are now sampled evenly, the unaligned search is u32-only with coverage counters (`offsets_available_unaligned`, `offsets_searched_unaligned`, `offsets_too_large_for_width`), u16 is measured by the aligned scan (one pass per width, complete for every file it reaches), budgets are 256 MiB/8 GiB unaligned and 32 MiB/2 GiB aligned, and the truncation flag is set for the sampled case. Measured on a synthetic run shaped like the real one: 82,080 units / 840 files / 98 MB in 28.3 s, with the text cohort at 46,080/46,080 offsets searched and 720/720 files scanned.

59. `RUN_PROBE.bat` failed on the user's PC with `No run folder given and none found`, and the cause was mine: `latest_run_folder()` read `output_base` while `run_pipeline.save_settings()` writes `output_root`, so the automatic lookup could never succeed anywhere. The test that should have caught it hand-wrote its fixture INI with the reader's own key. Fixed by reading `output_root` (alias `output_base` still accepted, relative paths resolved from the INI's folder), by returning and printing a reason for every "nothing found" case, by accepting a run folder **or** its parent as the argument, and by making the launcher prompt for a folder when the probe exits 2. The regression test now writes the INI with the pipeline's own writer (34 probe tests, full suite 226 OK, 1 skipped).

60. **The cohort-split probe ran on the user's PC, and the event files really do contain text-start offsets.** In the text cohort (32 exports, 45,252 units, 293 files) the units' start offsets occur as u32 little-endian values 6,535 times against 1,339 for `start + 1`, while a synthetic corpus built to the same density (5,351,375 bytes, 45,122 units, 119 bytes per unit against the real 111) and containing no pointer table gives 421 against 374 — a ratio of 1.13 instead of 4.88, at a fifteenth of the count. Marker offsets are not elevated (599 vs 446), so whatever is stored points at the byte after `FF FF`. The same cohort settles three more things: no length prefix (best lift +0.4%), no nested strings (522 inner markers, none before wide-script Japanese), and only 0/2/3-byte suffixes (`C9` in 90% of the two-byte ones), with the extractor covering 45.1% of the event bytes as text and 0.4% left as unselected marker spans. Two layout facts: the gap between units is never ≡ 1 (mod 4) (43 of 44,959), and the commonest pitches are 52–68 bytes. What is *not* explained: u32 big-endian shows the same lift, the 4-byte-aligned scan shows none, and the matches are spread evenly over the file, so this is not a contiguous aligned table. The probe now records where each match sits relative to the offset it encodes (`deltas`), plus a same-parity `start + 2` control, and `aligned_bytes_scanned` no longer counts a file four times (36 probe tests, full suite 228 OK, 1 skipped).

61. **Second probe run: the start-offset matches are neither a self-reference nor a table.** In the text cohort, 6,236 of the 6,335 u32 LE matches (98.4%) sit more than 256 bytes from the offset they encode, and the rest scatter over ~67 distances at 1–6 each; big-endian and the aligned scan look the same. With matches also spread evenly over every eighth of the file, no record stores its own string's offset and there is no contiguous offset table. The same-parity control removed the last artefact explanation: `start + 2` gives 528 matches against `start + 1` at 1,258 and `start` at 6,335. A second synthetic null, built with the real pre-marker structure (`XX 00 00 00 00 00`) and density, gives 776/750/509 — so the real files hold ~5,000 more matches of the exact offsets than a file with no references, and that excess is still unexplained. **The distance measurement could not have explained it in any case**: it only sees a field pointing at its own string, so the probe now attributes each match to the record holding it (position relative to that record's `FF FF`, the stored value against that record's own start, how many distinct offsets are involved, and which files), attributed to the *nearest* marker because a record's header precedes its own marker (39 probe tests, full suite 231 OK, 1 skipped).

62. **Prior-art survey: the container questions have already been answered elsewhere — and a working Korean patch exists for this exact game, DLC included.** `z3oo3z/PSP-SRWOE-KPatch` (base game, `v250810`) and `z3oo3z/PSP-SRWOEDLC-KPatch` (DLC, `v250617`) are released as GitHub Releases: a 54 MB ISO patcher applied by dragging the ISO onto a `.bat`, and a 2.9 MB DLC archive holding **73 xdelta patches** with a `.bat` pipeline and an MD5 checker that names any file that failed. The patched DLC output is an `.EDAT` placed in `memstick/PSP/GAME/NPJH50521`; menus are handled as **PPSSPP texture replacement**; verified on PPSSPP 1.18.1, "unknown on real hardware". Both repos contain only a README — no tools — and the archives were not downloaded here (the sandbox cannot reach `release-assets.githubusercontent.com`), so this is README evidence, not inspected bytes. A partial **English** patch also exists (CrashmanX, v1.02, distributed as a whole ISO) covering names and menus but **not** the story dialogue. Separately, `retro-trans/SRW-Z` documents reaching this project's exact negative result — "no contiguous offset/length table anywhere in the record (checked as u16/u32, absolute and relative)", offsets inline in the scenario bytecode — and settling it with a **grow-test in the emulator** rather than more static scanning. The Korean SRW patches share one method for the glyph problem: overwrite the font's entries for a code range with the target language's glyphs and keep each string's byte length. Everything found is recorded in `docs/PRIOR_ART.md`; the pointer question (item 61) is now **superseded by evidence** rather than by another probe run.

63. **The user's ISO is a different dump from the one the Korean base patch targets, so the base-game diff is closed and the DLC diff is the evidence route.** Measured: `certutil -hashfile "D:\SRWOE\SRW OE 1.08.iso" MD5` → `3bfd26f800b7b7a635df29f2c0c936ae`, against the `ce57eb21bcdc9bdd6204f63a4fd9f716` that `z3oo3z/PSP-SRWOE-KPatch` v250810 names as its original. This is a dump-level difference, not proof of a different game version: this project already found the image is 679,243,152 bytes while its own descriptor declares 673,710,080, and public catalogues list at least two dumps of the title (CRC-32 `2866c6c0` and `1718f49a`, with the community split on whether "v2" is v1.02 or v1.08). Which edition the user holds is still unrecorded — only its MD5 and size are. Actions: do not download the 54 MB base patch; the DLC patch is independent of the ISO and its `dlcmd5checker.exe` says per file whether the user's copies match (offer it the PSN `.EDAT` files, not the decrypted chapter-4 copies); and for Gate 4 the release must be keyed to recorded hashes, because more than one dump circulates.

64. **The method was found in the open, and it retires the offset investigation as a gate.** `docs/METHOD.md` records it from three sources. CrashmanX — who started the English patch for this game and whose progress table in gbatemp thread 351431 shows story, attack shouts and reference at 0% for want of tools — worked "with the constraint of having to use the same amount of spaces as the Japanese characters", using a hex editor and the Danball CPK tools. `retro-trans/SRW-Z` states on the sibling engine that in-place replacement at identical byte length "is safe and verified", while growing a string requires rewriting every inline offset operand. **So an equal-length replacement cannot move any offset, and the pointer layout is not needed to produce a testable patch.** Repacking is also settled: "It's possible to re-pack the .cpk files ... I just left 'Force Compress' unchecked and it worked", which agrees with this project's own finding of 0 compressed entries; a contradictory report in the same thread ("repack without any changes, the game crash") means the setting and the tool both matter. Extraction has three known-good routes here: YACpkTool, the QuickBMS CRI CPK script posted in that thread, and renaming a DLC `.EDAT` to `.CPK`. New tool: `tools/rewrite_units.py` performs the equal-length write-back from a filled `units.csv`, verifying each row's source view against the file's bytes, padding with `0x20`, refusing anything over budget, and asserting the output length equals the input length (16 tests, full suite 263 OK, 1 skipped). Still genuinely unknown, and now the whole remaining risk: the font (glyph substitution as in `snake759494/NDS-SRW-K`, or a renderer remap as in SRW-Z) and whether YACpkTool can be told to store rather than compress.

65. **Correction: the pointer work is back on the critical path, and the search that failed was the wrong shape.** `docs/METHOD.md` originally presented equal-length replacement as *the* method. It is only the safe fallback — English needs more bytes than Japanese almost always. `retro-trans/SRW-Z` grows strings routinely: `tools/apply_fixes.py` "Rows that outgrow their slot are relocated (append + repoint + zero)", and `tools/verify_pointers.py` is a structural gate asserting every pointer still lands on a string start. Their `tools/pool.py` also explains this project's negative result: "every static search for an index, **a record-relative offset, or an offset/8 failed, because the stored value is `0x0073xxxx`**" — pointers are **load-base-relative addresses**, so a search for bare offsets (which is what `boundary_probe` did, milestone 61) was documented to fail on this engine family. Their predicate: find a 4-aligned word equal to `BASE + offset`. Ported here as `tools/pointer_base_scan.py`, which tests every candidate base in the PSP user-memory window (`0x08800000`-`0x0A000000` at 16 KiB steps) plus small constants, ranks them by how many of a file's string starts they reach, includes a starts-shifted-by-+1 control, and reports whether the winning words form a dense run (11 tests, full suite 274 OK, 1 skipped). Two of their hard-won details are recorded for when this lands: pointer-shaped words that miss a string start were real table entries 60 times out of 91 (pointing into NUL padding or into a substring) and dismissing them as coincidence "broke all 60" — the fix is a stride test that refuses rather than guesses; and their pointer-health metric has a natural floor (84.4% on Bandai Namco's own disc), so thresholds must be read against a baseline.

66. **First measurements on real event files: the format is parsed exactly, and there are no offsets in it.** The user supplied 21 decrypted DLC files out-of-band (kept outside the repository; the upload commit was removed at their request). `tools/cpk_table.py` + `tools/crilayla.py` extract `eventP01.EDAT` cleanly: 88 entries, 66 CRILAYLA-decompressed, **0 failed**, 3,405 dialogue units. Each member parses as `"EDAT" + u32 size (= file size − 8) + u32 section_count`, then `section_count` blocks of `magic[4] + u32 body_size + body`, all sections `EVNT`, and **the walk lands exactly on the end of the file** in every file tested. Three offset hypotheses were then measured against a null and all came back at chance: load-base pointers (`BASE + start`, 1,601 candidate bases — best reaches 2% of starts, the +1 control the same); a longest-increasing-run table detector (1–4 positions against a null 2–5, where a real table would run to hundreds); and section-relative offsets (at or below the null). So SRW-Z's COMPDATA pointer-table model does not apply here, and these event files look **walked, not indexed** — strings delimited by `FF FF … 00 00` inside `EVNT` sections, with the only structural values being the file's own size and the section sizes. **That makes growing a string tractable without repointing**: update the containing `EVNT` section size, the `EDAT` header size, and the CPK entry's `file_size`/`extract_size`, then recompress or store. Not ruled out: intra-section operands addressing a string by index, by a word/2/4-scaled position, PC-relative, or including the 8-byte section header — none of those four was tested, and the decisive test is now small (grow one string, fix the three size fields, repack, boot).
67. **Chapter 2 located, the narration record decoded, and two modified containers built and verified.** The user's memory-monitor line from event 2.0 is in `DL105_50.bin` (entry #0 of `eventP02.EDAT`) at body offset 196, 118 bytes — not the 116 bytes the monitor showed, because the file stores line breaks as `0x0A` inside the text. The record holding it is length-prefixed (`b7 01 00 00 | length | parameter | text | 00 00`, with `length == 12 + len(text) + 2`) and all six such records chain end to end (184 → 316 → 460 → 540 → 632 → 676), so these files really are walked rather than indexed and growing a string needs no repointing. This is the first length prefix found here, and it explains the earlier empty result: that scan looked before `FF FF` markers and this text has none. `tools/cpk_write.py` rebuilds a container with one member replaced and is gated on byte identity — 18 of the 23 sample containers reproduce the original exactly, and the 5 refusals each name a reason (ITOC-only layouts, constant-storage size columns, one `AFS2` file). One real bug only the end-to-end check caught: member offsets are relative to `data_base` 2048 while content starts at `content_offset` 10240, so the first rebuild misplaced every shifted blob and the identity gate passed anyway. `tools/grow_event_text.py` then produced `eventP02.jp.EDAT` (MD5 `14e0d138084a4080e4a3617b63aaf3e5`) and `eventP02.en.EDAT` (MD5 `91118db85ae22752194ce48963dfb89d`), 371,896 B each, both re-parsing to 96 entries with **95 of 95 untouched members byte-identical after full extraction** and the changed member written stored, since no CRILAYLA compressor exists here. Kept under ignored `local/deliverables/`. Suite 288 OK, 1 skipped. **Re-encryption is not needed:** the user reports their PPSSPP reads encrypted and decrypted files identically, so the decrypted containers are tested directly — user-reported, not verified here, and the first suspect if a file will not boot. **Still open:** whether the font has Latin glyphs (why the English variant is a separate run), and whether the engine tolerates a grown record at all — which the boot test decides. Both variants ship as `local/deliverables/srwoe-test-eventP02.zip`, Japanese first to keep the charset constant.
68. **The sandbox loses everything outside git, so the build is now a script the user runs.** By the next turn the user's samples and both built containers were gone; only the committed tree survived (and the local clone had been reset to the base commit, so the new tools read as deleted while sitting on disk — a stale index, fixed with a mixed reset onto the pushed commit). `tools/build_event_text_test.py` plus `BUILD_TEST_PATCH.bat` now rebuild both `eventP02.EDAT` variants on the user's own machine from their own file and check each MD5 against the recorded `14e0d138084a4080e4a3617b63aaf3e5` / `91118db85ae22752194ce48963dfb89d`, so a matching hash means byte-for-byte the verified file. The three strings still encode to 118, 151 and 148 CP932 bytes, but the end-to-end rebuild could not be re-run here without the source container. **Two real bugs in already-pushed code, found by the new `tests/test_cpk_write.py`:** `rebuild` hard-coded the region order head → TOC → ITOC → content → EToc, and the synthetic container from `test_cpk_table` puts content *before* the TOC, so it emitted 1718 bytes for a 1048-byte file; and when content moves, `TocOffset`/`ItocOffset` were not shifted with it. Neither could surface on the real containers. Suite 301 OK, 1 skipped.
69. **The jp build crashed PPSSPP (write at 0x10FA0000): the grown container was not re-aligned.** The original keeps content-end/EToc on the `Align` boundary (10240+356352=366592=2048*179); growing by 4416 dropped the EToc at 371008, not a multiple of 2048, and the loader followed garbage outside RAM. `cpk_write` now pads the content region back to `Align` when the original was aligned. The earlier recorded MD5s describe the crashing unaligned build and are invalidated; the corrected build needs a fresh source `eventP02.EDAT`, which the sandbox no longer has. Alignment tests added; suite 304 OK, 1 skipped.
70. **Corrected, aligned builds produced from a re-uploaded source and verified.** With the `Align` fix and a fresh original (`60316f4639b906cf70b91fc28fc863be`) delivered via Drive, both variants rebuilt at 373,624 bytes and passed the structural gate: readable, EToc on the 2048 boundary and closing the file, 95 of 95 untouched members byte-identical, grown member exact. New acceptance MD5s: jp `cf1e703c2e1ca435ef514840e233c20b`, en `ee40c5b4ef138d092d4e4fe4bc6f9194`. Uploaded to the shared Drive folder; the only thing left unproven is the real boot.
71. **The aligned build crashed at the same PC, so alignment was not the cause (retracted). Prime suspect is writing the member stored: the game may always CRILAYLA-decode event members. A literal-only CRILAYLA encoder was built and round-trips the decompressor (72/72 real members, 3 tests) but makes the stream larger than the data (`FileSize > ExtractSize`), inverting the invariant, so it cannot ship. A control build (member stored as the original decompressed bytes, no growth) is on Drive as `00-KONTROLA-stored-bezWzrostu.EDAT`; one boot disambiguates stored-vs-growth. Suite 307 OK.
72. **Control booted: stored members are accepted and the container rewrite is sound; the crash is the *growth* of the record.** EToc holds only UpdateDateTime/LocalDir, so it is exonerated. A second control (`03-KONTROLA-taSamaDlugosc.EDAT`, MD5 `fa5319f5f930cf7114e168e89888d4a9`) edits the record content at the same 118-byte length; its boot result separates 'size change' from 'content edit' as the fault. Pending one user boot.
73. **Same-length edit boots in the real game -- equal-length translation is proven end to end.** The crash on growth is a stale *nested* size field: EVNT contains inner subsections (an 'ECHK' tag, a 6760 size at offset 60) and `grow_record` bumps only the EDAT total and the outer EVNT size. First in-game English delivered as `05-EN-taSamaDlugosc.EDAT` (MD5 `391770431ef5efd32e46b40777461a38`), 118-byte equal-length English. Growth needs the nested EVNT size fields reversed and all enclosing sizes bumped.
74. **Growth crash root cause found and fixed.** A differential across eventP01/02/03/09 shows the u32 at EVNT body offset 60 is always `EVNTsize - 36` -- an inner subsection size for region [56, EVNT_end). `grow_record` left it stale, breaking the inner bounds on insertion. It now bumps every inner size field tracking the owner end; `check()` whitelists them. Grown jp/en rebuilt, inner field consistent, structural gate clean (jp `cecd72631f73d469131e42eb42cc177e`). Suite 307 OK. First growth boot pending.
75. **Growth confirmed in game.** The grown jp build (inner EVNT size field bumped) boots, so `grow_record` now supports in-place growth and translation is no longer limited to equal length. English grown variant delivered (`07-en-WZROST`, MD5 `4f82950c3b9074a248d8f9fa42b5f4ec`). Regression test `InnerSizeFieldTests` added; suite 308 OK. Next: scale the proof record to all event strings across chapters, then the full export-translate-apply-xdelta flow.
76. **Scope pivot: translation deferred to a separate workflow; build the process.** Added `tools/export_strings.py` (readable per-record JSON with `max_line_width` to `local/strings/`, gitignored) and `tools/iso_pack.py` (ISO9660 packer preserving the 32 KiB UMD system area) with a pack->inspect->extract round-trip test. In-game box clips lines past ~46 half-width (screenshot), so that is the per-line budget. Suite 312 OK. UI/names/menus remain to be exported as separate tables.
77. **ISO prep for the user's 660 MB image.** `tools/iso_prep.py` (prep) + `PREP_ISO.bat` extract a small uploadable bundle (inventory.json, system_area.bin = first 32 KiB, and only eventP*/evept*/PARAM.SFO members) read-only. Tested on a synthetic ISO; `tests/test_iso_prep.py` added. Suite 316 OK. User to run the .bat on the real ISO and upload the zip; a streaming repack for the full image is next.
78. **Disc containers are `*.cpk` (chapter 1 = `eventP00.cpk`, 162,264 B), DLC are `*.EDAT`.** `iso_prep.WANT_RE` now matches both; test extended. Chapter-1 disc container exported via `export_strings` to `local/strings/eventP00.strings.json` (38 records, DL1xx members). Real ISO inventory: 80 files, 679,243,152 B. Suite 316 OK. Streaming repack of the disc (patched ISO) is the next step and runs on the user's PC.
79. **User's ISO extraction incomplete (tree 293 MB vs disc data 672 MB); tree-repack truncates. Added `iso_pack.repack_from_iso` (`repackiso`) streaming unchanged members from the original ISO with case-insensitive patch override; tested. `REPACK_GUIDE.md` primary method switched to `repackiso`. FAZA 1 identity boot on the user's PPSSPP still pending. Suite 324 OK.\n
80. **Case-preserving identifiers did not change the boot crash (identical PC) -> the repack failure is structural, not a name lookup; a from-scratch ISO9660 rebuild misses UMD metadata. Next evidence: PPSSPP debug log. Fallback: chapters 2-8 loose DLC, chapter 1 via external UMD repacker. Suite 324 OK.\n81. **patchiso VALIDATED by the user: boots, ~same size as the original.** The surgical method
   (copy original verbatim, append patched member, update only its directory record + PVD volume
   size) ran on the real disc as an identity patch of `eventP00.cpk` and **boots**; `repacked.iso`
   differs from the original by only tens of KB. From-scratch rebuild was the wrong approach;
   `patchiso` preserves the UMD structure the PSP needs. Next: FAZA 2 -- patch a *modified*
   `eventP00.cpk` (grown/English) through `patchiso` and boot, proving edit->repack->patch->boot with
   growth. Suite 325 OK.

82. **FAZA 2 result: patchiso boots the game to gameplay; the grown eventP00 crashes at first narration.**
   FAZA 1 (identity) and FAZA 2 both boot through title/character-creation (unlike from-scratch
   rebuild, which crashed at boot), so patchiso is the working ISO-packing method. But the *grown*
   `eventP00.cpk` crashes on the first prologue narration (Invalid Mem Access Read@0, PC 088a7378,
   SazThread). Header size fields are all consistent (+delta); the cause is EVNT forward-offsets:
   records AFTER the grown one shift, but their offsets stored in the ECHK block header are not
   updated by `grow_record` (it only fixes size fields). This is the growth requirement gap; the
   retro-trans/SRW-Z project solves the analogous pointer-rewrite problem (pool.py repack /
   verify_pointers). Next: either RE the EVNT forward-offset table to make growth safe, or proceed
   to B (readable translation-source files) with growth-in-ISO as the known open blocker.

83. **patch_iso ROOT CAUSE fixed and validated: identity patch now boots into chapter 1.** The
   crash that plagued every variant was `patch_iso` writing the patched member at the unaligned
   EOF while its directory record pointed at ceil(EOF/2048)*2048 (past the bytes); the game read
   garbage for eventP00.cpk (constant PC 088a7378). Fix pads to a sector boundary first
   (LBA=start/2048); regression test uses a non-aligned image. User confirms identity.iso enters
   chapter 1. Remaining: a *modified* cpk member still crashes (user_main, PC 088caea0) -- the cpk
   member encoding (expanding CRILAYLA + stale cpk header aggregate fields), i.e. growth-in-cpk.

84. **GROWTH-IN-CPK VALIDATED IN GAME: the longer English line renders in chapter 1.** With the
   patch_iso sector-alignment fix (83) plus the corrected descending CRILAYLA compressor (member
   shrinks, FileSize<ExtractSize), `make_demo_growth` + `patchiso` produced a repacked.iso that
   boots and displays "GROWTH TEST: THIS LINE IS NOW LONGER AND IN ENGLISH." in the prologue
   narration (user screenshot). The full chain edit -> repack cpk -> patch ISO -> boot with growth
   is proven on a real UMD. A is complete; next is B (readable translation-source files).

## Not yet demonstrated

- The one-click run has been run six times on Windows with the user's YACpkTool and game files (items 36, 42, 45, 46, 47, and 57). Extraction completeness is measured per package against its `-L` listing, whose three real column layouts are known and parsed (full, no ID column, no filename column with ID-named files). The latest run verified 453 of 497 packages; the remaining failures are the 42 colliding-name packages (whose entries are recovered separately under `hidden/` and verified against their listing sizes) and `robo01`/`robo03`, where one listed name each does not decode from the converter's console output. Whether the hidden duplicate-name entries differ in content, whether the game uses the ID column, the `@UTF` table row encoding, and the formats inside the AFS2 audio inputs remain unknown.
- A rebuilt CPK has **not** been tested in PPSSPP or on PSP.
- No Japanese string has yet been changed and successfully displayed in-game.
- The event-file structure and field meanings are still not understood. Ruled out on real data: a length field in the 16 bytes before the marker, nested strings, and (for the script) a fixed record pitch. **Open and now the main lead:** the text cohort's start offsets occur as u32 LE values 5× their shifted controls and ~8× a structure-matched null (~5,000 excess matches), but they are not self-references (98.4% sit over 256 bytes from the value), not 4-byte aligned, and not in one region. What holds them — and whether they are references at all — is what the record attribution measures. What the `C9` byte after the stop means is unexplained; the 8.3% unselected `FF FF …` spans are a binary-cohort effect (0.4% in the text cohort).
- The colliding-name recovery, the layout probe, the translation template, and the boundary probe have produced output on a real run (item 57); the CRILAYLA decoder has not been needed yet (0 compressed entries among the recovered entries). The **cohort-split probe (item 58) has not run on real data** — it needs `RUN_PROBE.bat` on the saved run folder.
- Chapter 4's decrypted `*04` packages are readable CPK containers (item 57): `eventP04` exported 3,520 units and `evept104` 3,562.
- It is unknown whether the single `00` after each noisy Japanese line terminates the text, and what `76 01`, `22 02`, `00 00`, or the trailing `10 00` represent.
- English glyph coverage, line width, wrapping, and longer-string relocation are unknown.
- The exact image/DLC hashes and completeness/version of every DLC file are not recorded.
- The original PowerShell scan was only run by the user on `DL102_20.bin`; the all-file Python audit uses the same heuristic but is not a validated parser. The `00`/suffix semantics and event structure remain unknown. Do not discard suffix bytes.

## Immediate next step

Extraction, the table reader, the colliding-name recovery, and the translator workspace are built and have now run on real data (items 47–57). Three boundary hypotheses are ruled out and the pointer question is still open, so the next step is a cheap re-measurement of the run the user already has:

1. **Run `RUN_PROBE.bat` on the user's PC** against the saved `20261010-142640` run folder — no converter call, about a minute, no new extraction. It re-measures the same data with the cohort-split probe (item 58) and answers what the pooled numbers could not: the length-prefix verdict, the suffix and post-text structure, and a pointer scan that actually covers the 32 event exports.
2. Read the `by cohort` section, not the pooled one. If the `text` cohort shows a length field or an aligned pointer table, extend the probe to that exact layout and treat the units as validated strings. If it stays negative, the units stay candidates and the next evidence has to come from elsewhere (another resource/version, or the game's own records), not from translation.
3. Then decide about the `C9` byte after the stop and the 8.3% of unselected `FF FF …` spans — both are visible in the same run folder without another extraction.
4. The table check can now be promoted to fail-closed once the two remaining mismatches are explained: they are the `robo01`/`robo03` console-name decoding, not the table (495 of 497 agreed).
5. Keep repack, write-back, and reinsertion blocked. The recovered colliding-name entries are read-only; no container the converter cannot write completely is repacked.

The agent sandbox has neither the game files nor the converter, so only the user's machine can run the pipeline. Keep the restored sample, exports, and decoded text under ignored `local/`. See [`NEXT_STEP.md`](NEXT_STEP.md).
93. `tools/extract_tables.py` added (dumps NUL-separated CP932 strings from a cpk to `local/tables/*.json`, fill-target/apply shape like events) + `tests/test_extract_tables.py` (suite 324 OK). Full category→container map of translatable containers recorded in `docs/EXTRACTION_MAP.md`: events=`eventP00..P09`; string tables=`mesbtl00`/`imenu00`(DLC char dict)/`config00`/`cprt000x`; structured(open)=`configst/system/tacsys/tactics/taclevup/navisys/logodata`. DLC is in translation scope.
94. `tools/extract_structured.py` added: byte-scans fixed-record structured containers (configst/system/tacsys/tactics/taclevup/navisys/logodata) for CP932 runs -> same row schema. Verified on real configst.cpk (3690 strings: spirit names + menu/help/warning text). Repack of these fixed records still open (no length field). +2 tests; suite 326 OK.
95. **Speaker-key probe (read-only, hypothesis).** `tools/speaker_probe.py` + `tests/test_speaker_probe.py`
   (5 synthetic tests). On eventP00 the u16 at `+10` of `0xc9` records behaves like a per-line speaker
   state (620 lines across 11 members, alternating key pairs within conversations). Not verified as a
   dictionary index; mapping to `srwDL_CharaDictionary` is the next measurement. Suite 336 OK (1 skipped).
96. **Speaker mapping + dictionary grow (2026-10-11).** `tools/speaker_map.py` maps dialogue keys to the
   CharaDictionary ID slots: 9/60 keys (61/608 lines, 10%) found, 0 duplicate IDs over 399 IDs. The remaining
   keys (4500s, 3700s, 1000s, …) are not in any dictionary read from imenu00–32. `tools/dict_pool_shift.py`
   implements the 12-pointer record layout: identity-exact on 15/15 pools; grow/shrink verified in memory;
   guard refuses unexplained in-record refs (0 on real data). CPK write-back and boot test NOT done.
   Suite 350 OK (1 skipped).
97. **Speaker key located (2026-10-11, supersedes 96's mapping).** The dialogue speaker key is the u16 at
   record offset +0x40 of `srwDL_CharaDictionary` records. 56/60 eventP00 keys map (574/608 lines); 55 unique,
   0xe93 ambiguous (records 86, 87); 0x4b1/0x4b6/0xec0/0xec1 unmapped. Seven named characters agree with a
   user-supplied line transcript. The mapping is numeric and committed; game text stays in `local/`.
   Suite 351 OK (1 skipped).
98a. **Speaker names resolved (2026-10-11).** `tools/speaker_names.py resolve` combines CharaDictionary
   names (string[0]) with config name slots. Chapter 1: 60/60 keys named. Chapter 2: 158/167 keys named;
   9 generic-role keys remain without a name source (listed by key in EXPERIMENT_LOG). Names stay in `local/`.
   Suite 355 OK (1 skipped).
98b. **Whole-game speaker map (2026-10-11).** 244 keys with >=3 lines: 216 named from dictionary, 11 config-only,
   17 no source. 39/43 chapter-1 keys return later. Each DLC event brings its own dictionary pool (HIPOTEZA).
   Local-only list in `local/WHOLE_GAME_SPEAKER_MAP.md`.
98c. **Open leads (2026-10-11).** (a) 17 no-source keys use a `0x0F xx` glyph-token name format; token table
   not solved. (b) Keys 0xe93 and 0x101a have identical names in duplicate records, so no alias evidence.
   (c) Masaki Andoh key 0x1144 has no dialogue in the 32 probed event files; the missing event file is still to find.
98d. **Masaki located (2026-10-11).** Dictionary record in imenu19 (key 0x1144 = 4420). Battle quotes in
   mesbtl19.EDAT, member p4420.pac (`p<key decimal>.pac` naming, 242 members overall). No event lines for 4420 in the
   32 probed event files (no event for him in the downloaded set). Quote text decoding still open.

## Session 2 (2026-10-11): names, battle quotes, font, tables
- Speaker table covers all 339 keys (283 dialogue + 56 battle-only): 301 named; dialogue lines named 99.5 %.
  Build: `tools/name_union.py`. Output stays in `local/`.
- Battle quotes: `p<key>.pac` members in mesbtl; 241 keys; record anchor documented in `docs/NAME_SOURCES.md`.
- font.cpk: decompressed (one CRILAYLA entry). Token map NOT found; 0x0F is an escape in configst.
- Mecha names: RoboDictionary slot 3 (verified). Weapon/item/shop/unit tables: layout not decoded yet.
- Open: 14 dialogue keys (65 lines) + 24 battle-only keys with no name; unit tables next.


### Session 2, part 3 (2026-10-11)
- Weapon names (wp_list00–19): inline at relpos 42/44, 205 unique; item names (srwDL_Item00): inline at relpos 54, 70/74.
- Mech names: RoboDictionary slot 3, 40 unique.
- Translation sheet: `local/name_units_unique.csv` (769 unique texts, with locations). Filled by translators later; not translated yet.
- `ItemDrop` names (177) are unverified; not the same as Item00 names.
- Growth of inline names untested (needs offset-table rebuild).
- Speaker table reconfirmed after the 32-probe rebuild: no change.

### Session 3 (2026-10-12): cel i stan
- Stały cel (100% tekstu przetłumaczone i reinject, 100% kluczy): `docs/GOAL.md`. Czytać przed każdą pracą.
- Sandbox cofnął HEAD dwa razy. Odtworzenie: `git reset --mixed origin/arena/581a1b79-mtgcrawler`, potem commit i push. Pliki robocze nie zmieniają się przy resecie.
- `local/` odtworzone z Drive (wejścia w `google_drive/`, `tools/build_speaker_inputs.py`).
- Otwarte: rozbieżność 246 vs 216 nazw słownikowych (`docs/NAME_REVIEW.md`); klucze bitewne bez nazwy (23 w kolejce, bez 4420); walidacja pól pilotów w `unit_list` (hipoteza).
- Kategorie wymagane przez cel, stan pokrycia:
  - dialog (283 klucze, 12738 linii): tak, nazwy częściowo;
  - battle quotes (241 kluczy, 22902 rekordy): tak, nazwy częściowo;
  - mechy/jednostki (393 rekordy `unit_list`, 40 tytułów serii w `RoboDictionary`): nazwy tak; powiązanie jednostka→bronie TAK na 7/46 kontenerów (`tools/unit_weapons.py`, sesja 5);
  - bronie (389 nazw): nazwy tak, opisy nie;
  - przedmioty (317 nazw): nazwy tak, opisy działania nie;
  - helpy/UI: nie zaczęte (poza tabelą referencyjną `srwDL_Reference`, 28 rekordów z tekstem);
  - encyklopedia postaci: nie zlokalizowana.

### Trwałość danych między turami (ważne)
- `google_drive/` i `local/` (gitignored) NIE przetrwały granicy tury: na początku każdej tury jest tylko `eventP00.cpk`.
- Odtwarzanie: `tools/drive_manifest.tsv` (nazwa, ID Drive, rozmiar). Pobrać każdy ID narzędziem Drive do `google_drive/<nazwa>`.
- Manifest jest niepełny: config01–46 (bez 38), imenu01–32, USRDIR (68 plików) dopisać przy następnym pobieraniu. ID z listingu FULL_DLC i USRDIR z tej tury są w historii rozmowy.

### Sesja 4 (2026-10-12): stan
- Dialogi: 12738 linii `0xc9` z łańcucha rekordów (293 członków, 32 kontenery, w tym `eventP00` z USRDIR). 42 członki bez łańcucha nieobjęte. Liczba znacznikowa 46703 jest zawyżona (tylko 29% trafień leży na granicach).
- Hash `eventP00`: jedna kopia na Drive, porównanie niemożliwe.
- Mechy: 100+ NIE osiągnięte. `robo00.cpk` to archiwum modeli; nazwy członków nie są kluczami jednostek (9/45 pokrycia). Dalej: `config*` (unit_list, robolist, RoboDictionary).
- Trwałość: wejścia gitignored znikają między turami; odtwarzać przez `tools/drive_manifest.tsv`.

### Mechy, stan po pobraniu config01–46
- Narzędzie: `tools/mech_names.py` (czyta config*, zwraca kandydatów z trzech źródeł). Wynik w `local/mech/mech_names.json`.
- Kandydaci: `unit_list` base 267, display 390, slot3 40. Brak wspólnych nazw slot3 z unit_list.
- Cel 100+ mechów NIEPOTWIERDZONY: nie wiadomo, czy unit_list to same mechy.

### Sesja 5 (2026-10-12): tożsamość jednostek (jednostka → bronie → seria) — CAŁA GRA
- Nowe narzędzie `tools/unit_weapons.py` (read-only): scala `unit_list`, `wp_list`, `srw_DL_RoboDictionary`,
  `robo_cpkid` i `unit_index_list` po id jednostki; wynik `local/units/unit_weapons.json` + CSV (gitignored).
  16 nowych testów syntetycznych; cały zestaw **383 OK (1 skipped)**.
- [ZWERYFIKOWANE] **Cała gra, 46 kontenerów:** 393 jednostki (= cały `unit_index_list`) i 1485 broni;
  id `unit_list` +84 == id `wp_list` w każdym kontenerze, ta sama kolejność (46/46); każda jednostka ma
  listę broni, każda broń ma nazwę i animację `.bsb` (1481 także formę skróconą).
- [ZWERYFIKOWANE] Dane gry siedzą w `config00`–`config19` (20 kontenerów). `config20`–`config46` to zaślepki
  z tekstem-powtórzeniem „configNN" (32 B) i czasem 256-bajtowym `milstPnn.bin`; `config09` ma puste pule.
- [ZWERYFIKOWANE] `unit_index_list.bin` = globalna lista **393 jednostek całej gry** (id, liczba broni, offset);
  łańcuch offsetów 393/393 (offset[i+1] − offset[i] = 12 + 256·liczba); liczba broni zgodna z `wp_list` 332/333
  (anomalia: id 2940 — indeks 3, rekord 4). 60 id należy do kontenerów `config07`–`config46`.
- [ZWERYFIKOWANE, korekta] nazwa broni jest ZAWSZE pod entry+32 (dawne „+30" to artefakt float32 pod +28).
  Nazwa jednostki: +0 (bazowa) i +140 (z wariantem); seria = `RoboDictionary` slot 3 po id z +28
  (261 rekordów, 259 id pokrytych, jedno id z dwoma rekordami: 3201; 74 jednostki bez serii w tych kontenerach).
- [ZWERYFIKOWANE] Komplet: `srw_DL_RoboDictionary` 305 rekordów → 302 jednostki z serią (91 bez);
  `robo_cpkid` 360 par → 336 jednostek z modelem w `robo00`, 24 pary poza `robo00`; `unitfacelist` 321 rekordów.
- Otwarte: semantyka pól +88…+134; `robo01`+ dla 24 par modeli; 91 jednostek bez rekordu serii;
  2 anomalie liczby broni (2940, 3246).

### Sesja 5, część 2 (2026-10-12): audyt kategorii, cytaty bitewne, tabele tekstowe config
- Nowy dokument **`docs/COVERAGE.md`** — mapa wszystkich kategorii celu (stan, źródła, braki, kolejność
  domykania, definicja „gotowe” per kategoria). To punkt odniesienia dla dalszej pracy.
- **Cytaty bitewne: domknięte.** `tools/battle_quotes.py` dekoduje łańcuch `EVNT` i rekordy 200/201;
  wynik na 32 kontenerach: **29 577 cytatów, 319 kluczy, 814 683 B tekstu, 0 błędów** (pokrycie 100%
  rekordów typu 201). Korekta: stara liczba 241 kluczy / 22 902 rekordy liczyła tylko rekordy zgodne
  z nazwą członka — prawdziwy klucz mówcy jest w rekordzie.
- **Tabele tekstowe config: ekstrakcja.** `tools/config_text_tables.py`: 11 254 rekordy, 12 599 stringów,
  208 109 B (unikalnych 4208 / 89 259 B) z Item/Skill/Reference/DLC_ID + Spirit/Achievement/Skill_Tag/
  StatusChange/ItemDrop. Trzy konwencje tabel zmierzone i przetestowane.
- Ustalenia: `imenu00` = duplikat `config00`; `configst` = 21 członków (m.in. komendy duchowe, trofea);
  DLC itemy/skille nie wnoszą nowych tekstów; tabela biografii postaci nadal niezidentyfikowana.
- Testy: **410 OK (1 skipped)**.

### Sesja 5, część 3 (2026-10-12): tabela postaci, wspólna rama EVNT, nazwy kluczy
- **Tabela postaci `charalist<NN>.bin` znaleziona i zdekodowana** (`tools/charalist_table.py`):
  172-bajtowe rekordy, nazwa skrócona +0, pełna +32, wąska +76, **klucz mówcy u16 +96**;
  16 członków, 404 rekordy, 404 unikalne klucze.
- Nazwy kluczy: **dialogi 283/283 (100%)**, cytaty 300/319; pozostałe 19 kluczy opisane
  (5 slotów zastępczych z pustym tekstem, 3 to także id jednostek, 11 nadal otwarte).
- **Wspólna rama `EVNT`** (`tools/evnt_walk.py`): wariant `mesbtl` i wariant eventowy z nagłówkiem
  `EDAT`; wyjaśnia 42 członki bez łańcucha. `battle_quotes.py` używa teraz tej implementacji,
  wynik bez zmian: 29 577 cytatów / 319 kluczy / 0 błędów.
- Pobrano brakujące kontenery: `imenu01–32` (25 plików) i wszystkie eventy (`eventP02–09, 13,
  20–32`, `evept101–108`). Manifest uzupełniony o brakujące ID.
- Testy: **435 OK (1 skipped)**.

### Sesja 5, część 4 (2026-10-12): pełna ekstrakcja tekstu scen
- `tools/event_dialogue.py` (10 testów) czyta wszystkie bloki `EVNT`: **26 468 linii dialogu**
  (32 kontenery, 293 członki), 313 kluczy mówców — **wszystkie mają nazwę** w tabeli postaci.
- Poprzednia liczba 12 738 linii / 283 klucze była zaniżona ~2x (chodzik kończył na granicy bloku).
- Poza dialogiem: 360 tekstów innych typów (narracja, warunki zwycięstwa/porażki, lokacje, help,
  tytuły scen) + 273 teksty w blokach-tabelach. Razem 27 101 pozycji / ~1,22 MB.
- **Korekta (sesja 5, część 11)**: czytnik gubił narrację schowaną w osłonkach `0xC8` — patrz wpis 44
  w `EXPERIMENT_LOG.md`; po dociągnięciu: **29 934 wiersze** fabuły, 32/32 kontenery obecne.
- Testy: **445 OK (1 skipped)**.

### Sesja 5, część 5 (2026-10-12): nazwy mówców (381 kluczy) i encyklopedia postaci
- `tools/chara_dictionary.py` (9 testów): słownik postaci z 25 kontenerów `imenu` — **582 rekordy /
  289 kluczy**, pola: nazwa, seiyuu (`－－－` = brak), **opis do encyklopedii [2]**, tytuł serii,
  `愛称：`, `声優：`, szablony wyświetlania, nazwa alternatywna, krótka nazwa.
- **Encyklopedia zlokalizowana**: to pole [2] rekordu (dowód: rekord `NoData` ma tam
  `図鑑用のデータが存在していません。`). Opisów w danych gry **nie ma** (579/582 puste) — trzeba je
  napisać redakcyjnie; wstrzyknięcie jest wykonalne w polu [2] (pula rośnie).
- `tools/name_map.py` (12 testów): jeden stół **klucz → nazwa** dla 381 kluczy gry (313 dialogów ∪
  319 cytatów). **362 klucze z nazwą (95,0%)**; nazwę dostaje **100% linii dialogu** i **96,0%**
  rekordów cytatów. Źródła: `charalist` (podstawa) + `CharaDictionary` (seiyuu, seria, pseudonim).
- Kontrola krzyżowa źródeł: `charalist.name_short` == `CharaDictionary.nickname` w 288/288, `name_full`
  == `name` w 285/288 (NFKC). Sloty `config*` **zbędne**: 190/201 trafień już w `charalist`, a 11 to
  przypadkowe bajty; reguła markera `0x6401` zgadza się w 89/91, bez markera myli się w 91/214.
- Zostaje **19 kluczy cytatów = 1 182 rekordy (4,0%)** bez nazwy (13 z tekstem); 3 z nich to także
  id jednostek — hipoteza „klucz = jednostka generyczna” do sprawdzenia (plan pkt 11).
- Naprawiony dług: `speaker_names.scan()` działa jako biblioteka (leniwy regex).
- Testy: **466 OK (1 skipped)**.

### Sesja 5, część 6 (2026-10-12): itemy i umiejętności — klucze, role pól, pule DLC
- `tools/item_skill_records.py` (11 testów): rekord itemu/umiejętności = nagłówek u16, **3 pary
  `u16` (start, end) pod +40** (nazwa / efekt / etykieta), ogon liczbowy i pula fragmentów po rekordach.
- **Itemy**: 300 rekordów = **300 kluczy** (u16 +0); nazwy 4 001 B (273 unikalne), efekty 3 941 B.
  `srwDL_Item00` (config00) i `srwDL_Item` (configst) są **identyczne** (md5 `18f16420f2`).
- **Umiejętności**: 1 469 rekordów = **1 469 kluczy** (u16 +4, unikalne); nazwy 10 322 B (189 unikalnych,
  część z tokenami 0x0F), efekty 40 208 B (1 237 unikalnych). Rodzina +0/+2 (193/254 wartości), poziom +6.
- Sloty nazwy i efektu **bez zapasu** (0 w 1769/1769) → grow wymaga przebudowy tabeli offsetów.
- **DLC `Item01–08`/`Skill01–08` nie dodają tekstu** — to kopie pul fragmentów bazowych plików (0 nowych).
- `srwDL_Skill_Tag` to tabela etykiet JP/EN (常時/ALWAYS), nie tabela skilli.
- Testy: **477 OK (1 skipped)**.

### Sesja 5, część 7 (2026-10-12): inwentarz plików, brak opisów encyklopedii, nowe kategorie tekstu
- `tools/member_inventory.py` (11 testów w `tests/test_member_inventory.py`): czyta **oba warianty CPK**
  (klasyczny z TOC i „ITOC blob” bez offsetów) oraz **oba poziomy** (członek kontenera + podpliki PAC),
  a każdy plik przypisuje do czytnika na podstawie JSON-ów wyjściowych. Wynik na przekazanym materiale:
  **155 kontenerów / 4 043 pliki**; z czytnikiem 1 097, bez czytnika 3 101 (wyłącznie grafika, dźwięk
  i puste sloty `_Entry.dat`/`_edit.dat`; każdy plik z tekstem ≥ 12 B jest rozliczony).
- Drugi wariant CPK: członki leżą kolejno od `ContentOffset`, każdy na granicy 2048 B — reguła
  potwierdzona budżetem bajtów (`speaker_map.member_offsets`, fail-closed). Wyjątek: `mesbmp00`
  (kolejność inna niż tabela ITOC; zbiór bitmap, dla tekstu nieistotny) — udokumentowany.
- **Nowe kategorie tekstu**: tytuły misji i uwagi do misji (`*_ext.dat`: 224 tytuły, 114 uwag, 10 147 B),
  tytuły misji w liście (`milstP`, 203), **tytuły BGM** (`bgmlist`, 490 / 10 953 B), nazwy teł
  (`bg2dlist`, 64), nazwy map (`srwDL_Map_S`, 15), nazwy oddziałów (`groupunit`, 16), etykiety sklepu
  (`srwDL_Shop`, 5). Wszystkie mają ramę „slot + NUL”, więc ścieżka grow jak w itemach — ale czytnika
  jeszcze nie ma (pkt 12 planu).
- **Encyklopedia**: opisów per-postać **nie ma w żadnym z 155 kontenerów** (pole [2] `CharaDictionary`
  puste w 579/582; `RoboDictionary` notki ≤ 52 B). Przeskanowane też wszystkie kontenery grafiki
  (`lmap`, `face00`, `bg2d`, `txa00`, `smap`, `mesbmp`, `bacb`, `eftex*`, `efmodel`, `efclump`, `bmp00`,
  `logodata`, `colorlst`, `bseq00`, `sprstd00`) — **0 tekstu**. Do rozstrzygnięcia z użytkownikiem:
  jeden japoński przykład tekstu z ekranu encyklopedii → szukanie bajtowe; jeśli nie znajdzie się
  w danych, opis jest obrazem/teksturą albo siedzi w `EBOOT.BIN`/`UPDATE/DATA.BIN` (95 MB).
- Higiena: pliki pobrane tylko do pomiaru (`bacb04`, `mesbmp00`, `lmap`, `face00`, `bg2d`, `txa00`,
  `smap`) usunięte po skanie; ID i rozmiary w `tools/drive_manifest.tsv` (workspace 143 MB → 51 MB).
- Testy: **488 OK (1 skipped)**.

## Sesja 5, część 8 (2026-10-12): czytnik nowych kategorii + pakiet dla tłumacza

- **Nowe kategorie tekstu są już czytane**: `tools/mission_text.py` (`*_ext.dat` tytuły i uwagi do misji,
  `milstP`, `bgmlist`, `bg2dlist`, `srwDL_Map_S`, `groupunit`) — **871 rekordów, 0 błędów**, 20 testów
  syntetycznych. Każdy slot ma policzony **span** (= twardy budżet tłumaczenia); uwagi do misji są
  zduplikowane w dwóch slotach (deduplikacja przy eksporcie).
- **Pakiet dla tłumacza gotowy**: `tools/translator_export.py` skleja wszystko w 8 plików JSONL +
  `strings.csv` + `index.json` — **80 606 wierszy / 2 447 484 B**; wiersz ma `id`, `jp`, puste `en`,
  budżet (`mode=grow` albo `max_bytes` dla slotów) i mówcę. Pliki jadą na Google Drive (poza repo).
- **Nazwy mówców**: **26 468/26 468 linii dialogu = 100,0%** (poprawiony błąd eksportu gubiący klucz 0),
  cytaty 26 932/27 383 = 98,35%. Reszta to **14 kluczy / 451 rekordów** (1,65%) występujących wyłącznie
  w `mesbtl00`; cztery metody sprawdzenia wykluczone, zostaje odczyt ze skryptu bitwy.
- **2 194 rekordy cytatów** (`p0995.pac`, `p0996.pac`) **nie mają w grze tekstu** (24-B rekordy,
  `flags=0`) — 7,4% puli, nic do tłumaczenia.
- **Sklep**: `srwDL_Shop` dodany do `config_text_tables`; pełny przebieg 36 członków / 12 631 stringów /
  208 229 B / 0 błędów.
- Testy: **521 OK (1 skipped)**.

## Sesja 5, część 9 (2026-10-12): itemy i umiejętności — korekta układu pól i ścieżka zapisu

- **KOREKTA**: +40 w rekordzie itemu/umiejętności to **sześć granic `u16` = pięć pól tekstu**
  (`name`, `name_level`, `effect`, `effect_brief`, `label`), nie trzy pary `(start, end)`. Poprzedni
  odczyt **zgubił dwa pola**: `name_level` (15 032 B) i `effect_brief` (7 161 B) — razem **22 193 B
  tekstu widocznego w grze** wróciło do pakietu. Wypełnienie: umiejętności 1469/1469/1469/516/9,
  itemy 300/0/300/0/0.
- **Reguła zapisu**: rekord ma zawsze długość % 4 == 0, a nadmiar leży w ostatnim polu (2069/2069).
- **`tools/item_skill_write.py`** (19 testów): przebudowuje rekord, tabelę offsetów, `tail_offset`,
  PAC i CPK; wiersz stosuje tylko przy zgodnym `member` i zgodnym tekście `jp`; przebudowa bez zmian
  = **bajt w bajt**. Przebieg demo: 20 wierszy w `config00` (Skill00 208 958 → 209 170 B,
  Item00 34 566 → 34 726 B) i 8 w `configst` (34 566 → 34 726 B), kontrola 20/20 i 8/8.
- **Pakiet dla tłumacza**: **82 591 wierszy / 2 469 677 B** (`03_skills` 4 932 wiersze), wiersze
  itemów/umiejętności w trybie `grow` z `suggested_max` (podpowiedź UI) i `record`.
- **CLI zapisu**: `item_skill_write.py --translations` przyjmuje katalog z JSONL albo wiele plików;
  przebieg po całym pakiecie (wszystkie `en` puste) → 0 zastosowanych, 0 błędów.
- **Walidator pakietu** `tools/translation_check.py` (14 testów): tokeny sterujące w kolejności,
  liczba linii, CP932, `max_bytes` (błąd) / `suggested_max` (uwaga), licznik nietłumaczonych,
  `check_report.txt`, `--require-complete`, `--strict`. Pełny przebieg: 82 591 wierszy / 0 błędów.
- **Pułapka**: nowa linia w tekstach gry to prawdziwy LF (0x0A), nie `\n` — walidator to liczy.
- Testy: **560 OK (1 skipped)**.

## Sesja 5, część 10 (2026-10-12): kolejność scen, numeracja pakietu i proces tłumaczenia

- **Sceny**: `tools/scene_map.py` — 293 sceny w kolejności gry (seria → odcinek → numer → wariant DLC),
  tytuł misji dla każdej (224 własne + 69 dziedziczonych, 0 braków), 32 sceny z elementem
  „miejsce/czas”; 36 scen to kopie, 33 to warianty edytowane → 4 186 wierszy z `copy_of`.
- **Pakiet**: wiersze dialogu w kolejności scen (`scene`, `order`), nowy plik strukturalny
  `06_scenes.jsonl`, pliki nazw przenumerowane `10_`→`07_`, `11_`→`08_` (numeracja ciągła 00–08,
  09 wolny). `strings.csv` tylko z `--csv`; przy ponownym eksporcie stare nazwy są kasowane.
- **Widok scen dla tłumacza**: `tools/scene_view.py` → `sceny/spis-scen.md` + `epizod-NN.md` +
  `sceny.zip` — nagłówek sceny (odcinek, miejsce, czas), elementy po kolei, `_koniec sceny_`.
- **Kopie wariantów**: `tools/translation_copy.py` przepisuje tłumaczenie ze źródła `copy_of`
  (nie nadpisuje wypełnionych, zgłasza rozjazd `jp`).
- **Znaki sterujące**: walidator pilnuje `\r` (1 389 wierszy dialogu) i `0x0F` (1 645 wierszy w itemach,
  skillach i nazwach) — zgubienie któregokolwiek to błąd.
- **Proces tłumaczenia**: `docs/TRANSLATOR_PACKAGE.md` to instrukcja krok po kroku — tłumacz wypełnia
  **tylko linie `EN:` w plikach `.md`** (widoki), a nie JSONL; import → `translation_copy.py` →
  `translation_mirror.py` → `translation_check.py`. CSV to wyłącznie widok (nie wraca do gry).
- Testy: **595 OK (1 skipped)** (stan tej części; po części 10c — 652).

## Sesja 5, część 10b (2026-10-12): widok scen = plik do pracy (import angielskiego)

- `tools/scene_view.py`: linia `EN:` pod każdym elementem sceny + ochrona pracy — plik z nieprzeniesionym
  angielskim nie zostanie nadpisany przy ponownym generowaniu widoku (`skipped`, `--force`).
- `tools/translation_import.py` (**nowe**, 13 testów): rozpakowany `sceny.zip` / folder `.md` →
  `00_dialogue.jsonl` jednym poleceniem; wcięte linie po `EN:` to ciąg dalszy tekstu, `⏎` i `<0x0F>`
  wracają jako znaki; tekst łamiący zasady gry jest odrzucany, nie wpisywany (idempotentnie).
- Proces: **tłumaczysz sceny w `.md`** → `translation_import.py` → `translation_copy.py` →
  `translation_check.py`; JSONL to plik, z którego buduje się gra (nie trzeba go czytać),
  a `sceny.zip` nigdy nie wraca spakowany do gry.
- Demo na 12 liniach sceny 1: import 12/12, kontrola 0 błędów, 0 uwag. Widok pakietu regenerowany
  z liniami `EN:` (`sceny.zip` 767 501 B) — do podmiany na Drive.

## Sesja 5, część 10d (2026-10-12): wtrysk dialogów do zdarzeń — działa na prawdziwym kontenerze

- `tools/event_text_apply.py` (**nowe**, 14 testów) domyka ścieżkę pakiet → gra dla fabuły.
  Zmierzony format rekordu dialogowego: `0xC9`, `[typ][rozmiar][6×u16: 1, id mówcy, 0,0,0,FFFF]`,
  tekst od +20, dopełnienie do 4 bajtów (1–4 zera). Offset z pakietu **jest** początkiem tekstu
  (sprawdzone na wszystkich 90 wierszach członu `DL100_01.bin`); rekord siedzi w opakowaniu `0xC8`,
  to w sekcji `EVNT`, a to w nagłówku `EDAT`.
- Rozszerzenie linii przepisuje: rozmiar rekordu, rozmiar każdego opakowania `0xC8`, rozmiar sekcji
  `EVNT` i rozmiar `EDAT` — wszystkie te pola leżą **przed** wstawianym tekstem, więc nic nie trzeba
  przeliczać (plik jest chodzony, nie indeksowany).
- Bramki: tekst musi stać pod zapisanym offsetem (inaczej wiersz pominięty), linia musi zmieścić się
  w oknie (46 jednostek), tekst musi kodować się w CP932, a po zmianie plik jest **ponownie parsowany**
  (chodzenie bloków, liczba rekordów, wielozbiór tekstów) — wynik niezgodny nie jest zapisywany.
- Przebieg na prawdziwym `eventP00.cpk`: **6 linii sceny 1 przetłumaczone → 6/6 wpisanych**,
  0 pominiętych, 0 odrzuconych, 0 problemów weryfikacji; człon `DL100_01.bin` 13 112 → 13 080 B,
  kontener 162 264 → 170 456 B (zmieniony człon zapisany bez kompresji). Odczyt patrzonego kontenera
  z zewnątrz: **44 członki, różni się tylko `DL100_01.bin`**, 82 teksty sceny bez błędów, pierwsze
  sześć po angielsku. Bramka tożsamości `cpk_write`: `eventP00.cpk` i `config00.cpk` **bajt w bajt**.
- Ograniczenia (uczciwie): rekordy inne niż dialogowe (narracja, warunki, etykiety, teksty
  wbudowane — 633 wiersze) mają tekst bez pola długości, więc dostaną własny zapis; tytuły i uwagi
  misji czekają na zapis pól o stałej szerokości (`*_ext.dat`); uruchomienia w PPSSPP nie mam —
  to po stronie użytkownika.

## Decyzje użytkownika (2026-10-12, po cz. 10e)

1. **Nazwy serii zostają po japońsku** — nie tłumaczymy ich; kontekst serii w widokach i scenach
   pozostaje w oryginalnym zapisie.
2. **Instrukcja dla tłumacza tylko po polsku** — wersja angielska nie jest potrzebna.
3. **Dane gry poza repozytorium** — plik `google_drive/eventP00.cpk` usunięty ze śledzenia
   (`git rm --cached`); historia commitów pozostaje nietknięta. `google_drive/` i `local/` są
   ignorowane, więc plik nie wróci przypadkiem przy `git add -A`. Audyt `git ls-files` po tej
   zmianie: **żaden** plik danych gry (CPK/ISO/BIN/DAT/…) nie jest śledzony.

## Sesja 5, część 10f (2026-10-12): test w grze jednym batem, bez danych gry w repo

- `PATCH_ISO_TEST.bat` przestał potrzebować paczki z Drive: bierze **Twoje ISO**, wyciąga z niego
  `PSP_GAME/USRDIR/eventP00.cpk`, wpisuje 6 angielskich linii prologu i zapisuje nowe ISO obok
  (`SRW_OE-test.iso`). Uruchomienie: dwuklik (albo przeciągnięcie ISO na plik).
- Nowe: `tools/iso_test_patch.py` (+11 testów, w tym przepis z repo sprawdzony na atrapie ISO z
  prawdziwym kontenerem), `tools/iso_pack.py`: `find_member` / `read_member` (+4 testy),
  `test-patches/eventP00-scena1.json` — offsety, skróty MD5 i nasze angielskie linie; **żadnego
  japońskiego tekstu i żadnego pliku gry w repozytorium**.
- Bramki w narzędziu: MD5 kontenera i członu (inna wersja gry → stop, nie cicha korupcja), każda
  linia musi trafić w swój rekord dialogowy, weryfikacja zapisu musi wyjść pusta, po przebudowie
  zmieniony może być **tylko** wskazany członek. `--dry-run` sprawdza wszystko i nic nie zapisuje.
- Test końcowy: atrapa ISO z prawdziwym `eventP00.cpk` + przepis z repo → **6/6 linii**, zmieniony
  tylko `DL100_01.bin`, kontener przebudowany, ISO czytelne dla `iso9660.inspect_iso9660`.
- Zestaw testów: **681 OK** (1 pominięty).

## Sesja 5, część 10g (2026-10-12): wybór ISO w oknie, wynik obok oryginału

- `PATCH_ISO_TEST.bat` nie wymaga już wpisywania niczego z klawiatury: otwiera **okno wyboru
  pliku** (ten sam mechanizm Tk, co w `run_pipeline.py`), a nowe ISO zapisuje **obok oryginału**
  jako `<nazwa>-test.iso`. Przeciągnięcie ISO na bata nadal działa (wtedy okna nie ma).
- Bez Tk albo bez pulpitu narzędzie pyta w konsoli, a anulowanie okna kończy pracę komunikatem
  (kod wyjścia 2). Rozszerzenie pliku i brak pliku są sprawdzane przed czymkolwiek innym.
- Testy: `tests/test_iso_test_patch.py` ma 15 testów (doszły: nazwa pliku wyjściowego obok
  wejścia, przebieg CLI bez podanej ścieżki, brak okna/anulowanie, brak okna ≠ błąd).
- Zestaw: **685 testów OK** (1 pominięty).

## Sesja 5, część 11 (2026-10-12): narracja i tytuły misji — po Twoim teście w grze

Po potwierdzeniu, że gra czyta nasze linie, domknięte zostały trzy rzeczy, które widziałeś po
japońsku:

1. **Narracja** — miała własny typ rekordu (`0x1B7`, tekst od +12) i własny problem: leżała
   w opakowaniu, którego ekstraktor nie otwierał, więc **nie było jej w pakiecie tłumacza**
   (41 z 44 rekordów w `eventP00.cpk`). Ekstraktor naprawiony, zapis obsługuje oba typy rekordów,
   a okno narracji zmierzone na 52 znaki.
2. **Tytuły misji** — pola stałej szerokości w `config00.cpk` → `config00.pac` → `milstP00.bin`
   (komórka 128 B, tytuł od +10). Nowe narzędzie `tools/slot_text_apply.py` pisze w takie pola:
   mieści się albo odmowa, zero zmian poza pisanymi komórkami, bramka tożsamości dla całego
   kontenera. Przetłumaczone wszystkie 15 tytułów z tego pliku.
3. **Cała pierwsza scenka** — przełożona w całości: 6 rekordów narracji + 82 linie dialogu
   (Seishiro Kusanagi, Himari Yaegaki, mech „Exert”). `PATCH_ISO_TEST.bat` wpisuje teraz jedno
   i drugie w jednym przebiegu.

Do zrobienia dalej: **odświeżyć pakiet tłumacza** (widoki scen bez narracji to skutek naprawionej
luki — potrzebna ponowna ekstrakcja z kontenerów fabuły), imiona mówców w okienku dialogowym
(`config00.cpk`, sloty nazw), pozostałe rodzaje tekstu (warunki, etykiety, teksty w tabelach),
UI (`system.cpk` — układ tylko-ITOC), potem przebudowa ISO i test w PPSSPP.

### Sesja 5, część 11 (2026-10-12): pakiet dla tłumacza domknięty i wgrany

- **Fabuła domknięta**: `tools/event_refresh.py` dociągnął z kontenerów gry to, czego nie widział
  czytnik — **+2 833 wiersze** (w tym 1 706 narracji ukrytej w osłonkach `0xC8`); fabuła ma teraz
  **29 934 wiersze**, kontenery **32/32** (rozdziały `eventP10`–`12`, `14`–`19` nie istnieją w DLC).
- **Limity długości przy każdym elemencie**: każdy element do tłumaczenia ma linię `limit:`
  (slot: ile bajtów; dialog/cytat: 46 jednostek na linię + liczba linii oryginału; pole tabeli:
  bez twardego limitu, z długością oryginału).
- **Powtórzenia dziedziczą tłumaczenie**: `tools/package_copies.py` oznaczył **6 504 wiersze**;
  w widokach **5 146** pozycji nie ma linii `EN:` (m.in. „Seria" przy każdym mechu/postaci).
- **Pakiet**: 67 440 linii `EN:` (26 035 fabuła + 41 405 widoki), kontrola **0 błędów**,
  85 424 wiersze tekstu. Testy: **728 OK (1 skipped)**.
- **Drive**: folder „Pakiet do tłumaczenia" zawiera **dokładnie trzy pliki** (`README.md`,
  `sceny.zip`, `widoki.zip`); nasze kopie JSONL i raporty przeniesione do folderu
  „Robocze (JSONL — nie dla tłumacza)".
- **Jasność pakietu**: README (wersja 2) mówi wprost, że **nagłówki grup** (`- seria:`, `- głos:`,
  `- uczestnicy:`) zostają po japońsku jako podpowiedź, a tłumaczy się tylko elementy widoczne
  w grze (`[Seria]`, `[Aktor głosowy]`, …).
- **Szacunek pracy na całość** (zmierzony, nie na oko): 1 406 489 znaków JP → ~3,16 mln znaków EN
  (~527 tys. słów), ~0,8 mln tokenów czystego tekstu; rząd 5–10 mln tokenów z otoczką, ~100–250 tur
  roboczych (~10–20 sesji). Szczegóły we wpisie 46 `EXPERIMENT_LOG.md`.
- **Instrukcja dla tłumacza = tylko instrukcja**: rozdziały o naszym stanie prac i kuchni
  technicznej przeniesione do `docs/TRANSLATOR_PACKAGE_TECH.md`; pilnuje tego
  `tests/test_translator_readme.py` (6 testów). Testy: **734 OK (1 skipped)**.
- **AUDYT POKRYCIA (nowe)**: `tools/coverage_audit.py` porównuje surowe kontenery z pakietem.
  Pierwszy przebieg: **26 756 tekstów / 413 943 znaki są w plikach gry, a nie ma ich w pakiecie**
  (najwięcej w fabule: czytnik scen kończy chodzenie po członku przedwcześnie, np. `DL830_13.bin`
  ma 507 rekordów dialogu, a pakiet zna 98; `configst` 824 opisy interfejsu). Szczegóły i dowody
  bajtowe w `EXPERIMENT_LOG.md` wpisy 48–49. **Pakiet nie jest kompletny — nie oddawać tłumaczowi**
  do czasu, gdy audyt da 0 braków.
- **KOREKTA LICZB (2026-10-12)**: dialog fabuły to **~44 500 linii**, nie 26 468 — czytnik gubił
  całe bloki (w `eventP08`/`DL830_13.bin` pominięte 60 z 65 bloków). Brakuje ~18 519 linii
  (451 025 znaków jp). Cytaty bitewne sprawdzone na **wszystkich 32 `mesbtl`** — **0 braków**.
  Tekst do tłumaczenia rośnie z 1,41 mln do ~1,86 mln znaków jp (~4,2 mln znaków angielskiego).
  Szczegóły: `EXPERIMENT_LOG.md` wpis 50.
- **CZYTNIK NAPRAWIONY, PAKIET PRZEBUDOWANY, BRAMA ZIELONA (2026-10-12)**: nowa reguła startu
  łańcucha w `evnt_walk.find_chain` — najwcześniejsze opakowanie `0xC8` (zmierzone na wszystkich
  **5 211 blokach**; stara reguła „najwięcej rekordów” myliła się w 5 104). Wynik: **43 708
  rekordów dialogu, 0 błędów**. `coverage_audit.py` na przebudowanym pakiecie: **0 brakujących
  tekstów** (2 pozostałe trafienia to wpisy Makefile w `configst.pac`, nie tekst gry). Pakiet:
  **105 372 wiersze** (dialog 47 175 — mówca nienazwany 2 = 0,0%; cytaty 27 383 — 451 = 1,65%;
  przedmioty 1 200; umiejętności 4 932; config 15 368 — w tym **2 196 tekstów z `sysmes.bin`**
  i 541 doczyszczeń; misje 1 281; postacie 3 388; jednostki/bronie 4 645; sceny 282).
  Dziedziczenie przywrócone (`package_copies.py`): **6 504 `copy_of`** → do wpisania **83 536
  linii `EN:`**, 13 162 elementy dziedziczone. Pliki dla tłumacza przebudowane: `sceny.zip`
  (36 plików), `widoki.zip` (7 plików), instrukcja zaktualizowana. Testy: **734 OK (1 skipped)**.
  Szczegóły: `EXPERIMENT_LOG.md` wpis 51. Nadal brakuje `eventP00.cpk` (rozdział 1).
- **PEŁNY BUDOWNICZY PATCHA GOTOWY (2026-10-13)**: `tools/build_translation_patch.py` +
  `HOKUS_POKUS.bat` — jeden przebieg: ISO użytkownika + folder DLC + zwrócony pakiet
  tłumaczenia → `srw-oe-patch/patched.iso` + `srw-oe-patch/DLC/...` (tylko zmienione pliki)
  + `build_report.json` (każda odmowa z powodem). Oryginały tylko czytane. Nowi pisarze:
  `name_table_write.py` (stałe komórki charalist/unit_list/wp_list, pasuje-albo-odmawia,
  trzecia forma jp „token-solved" dla krótkich nazw broni) i `slot_apply.py` (generyczny
  zapis in-place: sloty 04/05 i tail-poole konwencji B przed przebudową rekordów). Poprawka
  CRILAYLA: `cpk_write.decompressed()` — membery event*/imenu* bywają skompresowane, wszyscy
  pisarze dekodują przed parsowaniem i zapisują stored. Sysmes przez `apply_edits` (pełna
  przebudowa poola; `equal_translate` nie widzi stringów z `\n`/tokenami). Rozpoznawanie form
  jp: `table_write.match_form/encode_en` — literalne `%s` (printf gry) odróżnione od bajtów
  sterujących (`token_kinds`). Smoke na żywo: **21/21 markerów TEST w 5 kontenerach**
  (config00, configst, eventP00, imenu00, mesbtl00), konflikty celów wykrywane i odmawiane
  (fail-closed), robonote bez kontenera ląduje we wszystkich lustrach, redirect
  `unit_series`→RoboDict działa. Testy: **836 OK (1 skipped)** (commity c11adb3, 6e83c97;
  szczegóły: EXPERIMENT_LOG części 13–15). `eventP00.cpk` dostępny (pobrany z Drive —
  poprzedni wpis „brakuje" nieaktualny). 
- **PRÓBA PEŁNOSKALOWA + WSZYSTKIE RODZAJE REKORDÓW SCENY (2026-10-13)**: smoke orkiestratora
  powtórzony po resecie (21/21); próba pełnoskalowa na 26 729 wypełnionych wierszach
  (`local/scale_pkg`, 7 JSONL-ów): **24 823 zapisów / 1 781 odmów w 6 kontenerach, 1 m 37 s**,
  spot 408/420 (chybione = udokumentowane uczciwe odmowy). Bug G naprawiony: kopie DLC
  `Skill01-08`/`Item01-08` (pool-only konwencja C) routowane w całości do `table_write` przed
  sprawdzeniem kategorii; konflikty i offsety ze środka stringa w poolach A/C odmawiane
  fail-closed. **ETA zna teraz wszystkie zmierzone rodzaje rekordów sceny** (odwrócone na
  żywym eventP00.cpk): condition_victory 0x1B4 i condition_defeat 0x1B5 (tekst @8), location
  0x152 i help 0x1FC (u32 parametr, tekst @12), scene_title 0x1B6 (3×u32, tekst @20), label
  0x1BA (dwie postaci: @8 albo u32 id + @12), 0x14F (id + @12), 0x14A (@8) — reguła paddingu
  `padded_size` potwierdzona na każdej próbce, `grow_text` bez zmian; rozstrzyganie postaci
  per rekord (`text_start_of`) + `find_record` niesie pozycję z offsetu wiersza. eventP00:
  **1 709/1 709 wierszy, 0 skipped** (luka pisarza 3,7% pakietu 00 zamknięta). Testy:
  **855 OK (1 skipped)** (commity e8edd30, 5b5d472; szczegóły: EXPERIMENT_LOG część 16).
  **Następny krok**: pełny przebieg na maszynie użytkownika (HOKUS_POKUS.bat: ISO + folder
  DLC + zwrócony pakiet tłumaczenia) i test w PPSSPP; do zweryfikowania w grze: szerokość
  okna dla nowych rodzajów (reguła 46 jedn. zastosowana przez analogię do dialogu).

## 2026-10-14 — %s: token kany znika z EN (pytanie tłumacza załatwione twierdząco)

* **Reguła (od 26c3560):** EN zachowuje wyłącznie %s-y obowiązkowe — literały `%s` silnika i
  kontrolki funkcjonalne (\r); tokeny kany `0x0F xx` (glif dźwięcznej kany) znikają z EN razem
  ze znakiem po %s, dokładnie jak `<0x0F>` w scenach/widokach nazw. Liczba %s w EN = liczba
  obowiązkowych, inaczej pisarz odmawia (kontrakt deterministyczny, bez zgadywania po tekście —
  drugie bajty glifów to cyfry/spacje/interpunkcja tak samo często jak symbole).
* **tokeny.tsv** (tools/token_map.py, 6e21255): mapa L/T/C dla 4 098 display-form wierszy z %s
  (L=9 391, T=217 w 119 tekstach, C=20); 0 nierozwiązanych; 0 konfliktów jp→rodzaje. Na Drive
  w „Pakiet do tłumaczenia" i „Robocze (JSONL)" — użytkownik kładzie ją OBOK JSONL-ów.
* **Walidator/importer** (549fa1d) czytają sidecar automatycznie: EN bez tokenów kany przechodzi,
  z zachowanymi — odrzucany; bez sidecara stara ścisła reguła. Stare EN-y z `%s*` będą odmawiane —
  po stronie tłumacza poprawka masowa wg listy (przed tłumaczeniem umiejętności — zgodnie z prośbą).
* Manual §3 przepisany; README Drive v4 w trakcie synchronizacji. Suite **882 OK**.
* Następne: ponowny przebieg scale/smoke na realnych kontenerach (pomocniki lokalne do odtworzenia)
  i finalny patch — bez zmian wobec planu; nowa reguła %s nic w łańcuchu budowania nie łamie
  (odmowy token-only SLA zamienią się w zapisy).


## 2026-10-14 — próba pełnoskalowa na realnych kontenerach: pięć błędów pisarzy/pakietu zamkniętych

* **Pomocniki odtworzone w repo** (zapowiedź z poprzedniego wpisu): `tools/scale_fill.py`
  (syntetyczne wypełnienie pakietu pod te same bramy co prawdziwe tłumaczenie, `--smoke` = 1 wiersz
  na rodzinę) i `tools/patch_spot_check.py` (czyta zbudowane kontenery i liczy, które EN naprawdę
  wylądowały; pełna lista braków — build_report trzyma tylko pierwsze odmowy). Oba z testami.
* **Znalezione i naprawione [ZWERYFIKOWANE na config00/config01/configst/eventP00]:**
  1. pisarz slotów ufał heurystyce „zera = padding" i **nadpisałby zerowe pole binarne** za
     krótszą nazwą mapy (`srwDL_Map_S` +32); teraz `mission_text.SPECS` niesie zmierzone rozmiary
     pól (mapa 32, tło 24, tytuł misji 40, oddział 32 B) i tną budżet pisarza, walidatora i filla;
  2. **wszystkie pisarze ucinały skrajne białe znaki EN** (`\n`, spacje, U+3000 wyśrodkowanych
     tytułów, ` Lv` kolumn) — wspólny `table_write.english()`; walidator ostrzega o dodanej spacji;
  3. slot po bajtach binarnych bez NUL-a (`bg2dlist`, `milstP01`) — 15 „uczciwych" odmów z v7 było
     błędem; przy okazji pętla zapisu **zerowałaby pole binarne za nazwą tła** — naprawione, zapis
     nie może wyjść poza zmierzony slot (0 bajtów poza slotami na 6 członkach);
  4. `max_bytes` liczony z NUL-em w `slot_apply`/`text_runs_export`, bez NUL-a w walidatorze i
     instrukcji — jedna semantyka (bajty EN), pozycja terminatora sprawdzana jawnie;
  5. strażnik „niewyjaśnione odwołania" odrzucał całe członki (78 achievement, 171 DLC_ID) — teraz
     per wiersz; rekordy DLC_ID mają zmierzony blok liczb (+32 cena, +36 numer, +48 punkty) →
     wyjątek rodziny, DLC_ID00/01 piszą się (139+60 edycji).
* **Higiena pakietu 04 (eksport):** 84 „sieroty" (ceny/identyfikatory dekodujące się jako `' N'`,
  `'0u'`) pomijane; 53 napisy przycięte do wskaźnika (26 nagłówków Reference wraca do pakietu,
  `!チョバムアーマーSR` bez bajtu licznika); 927 wierszy puli ogonowej B (Skill00/StatusChange/
  Item/Spirit) oznaczone `slot` + `max_bytes = bytes`, bo pisarz pisze je w miejscu — pakiet
  z Drive (sprzed zmian) ma je jeszcze jako `grow`; **następny eksport na maszynie użytkownika
  naprawi plik**, a `TRANSLATOR_PACKAGE.md` (v5, lokalnie — Drive README dalej v4, bez wysyłki
  bez zgody) mówi tłumaczowi, jak czytać stare widoki (limity 05: 39/31/23/31 B zamiast
  117/159/111/99; fragmenty opisów = limit długości oryginału; spacje skrajne są częścią tekstu).
* **Wyniki (6 kontenerów, 7 vs 8 JSONL):** smoke 93/8/1 (8 = udokumentowane odmowy); scale
  v8a 25 289 trafionych / 1 334 braków → v8d **26 032 / 482** (base) i **30 929 / 482** (full,
  z 03: +4 897 trafionych, 0 nowych braków; 13 odmów „token-only" z v7 to zapisy); walidator
  0 błędów; build ~110 s. Pozostałe braki = polityka (robonote bez rekordu 144, pseudonimy 77,
  nierozkodowalne Map_S 5, ItemDrop bez pisarza 10) + sieroty/przycięcia, które znikają po
  eksporcie (≈70) + DLC_ID (po wyjątku rodziny: 13 → po eksporcie 0). Szczegóły: EXPERIMENT_LOG cz. 18.
* **Otwarte [HIPOTEZA]:** jak gra adresuje fragmenty puli ogonowej (słowa ogona rekordów to
  parametry, nie offsety) — wzrost puli wymaga testu w grze; do tego czasu w miejscu.
* Testy: **942 OK (1 skipped)**.
* **Następny krok:** eksport pakietu na maszynie użytkownika (nowe limity 05, sieroty, pula w
  miejscu) → podmiana Robocze/Pakiet na Drive po zgodzie → pełny przebieg HOKUS_POKUS z ISO +
  DLC i test w PPSSPP (w grze do sprawdzenia: tytuły misji z nowym limitem, nazwa tła po
  binariach, DLC_ID w menu pobierania, fragment opisu umiejętności w miejscu).


## 2026-10-14 — pierwszy prawdziwy import tłumaczeń i budowa na 13 kontenerach z Drive

* **Import `EN.zip` [ZWERYFIKOWANE]:** 61 468 elementów z EN → **61 322 w pakiecie, 41 odrzuconych**
  (9 opisów sysmes bez pierwszej linijki doklejanej przez grę, 32 nazwy za długie na zmierzone pola
  23/31/39 B). Po kopiach: 79 612 wierszy z EN w pakiecie (108 123 wierszy), walidator 0 błędów.
* **Pula ogonowa Skill/Item/Spirit/StatusChange ma własną tablicę wskaźników u32 [ZWERYFIKOWANE]** —
  hipoteza „w miejscu" z poprzedniego wpisu odwołana: pisarz przebudowuje tablicę i napisy
  (`item_skill_write.rebuild_pool`, krok `tail-pool` przed rekordami), fragmenty rosną. Przy okazji
  wyszło, że **125 tekstów z tokenem kany nigdy nie było w pakiecie** (`clean_run` je odrzucał, a
  `coverage_audit` tego nie widzi) — `tools/pool_rows_refresh.py` dopisał je (+1 127 wierszy z kopiami,
  −85 śmieci); są puste i czekają na tłumacza.
* **Szerokość linii:** 46 było z pierwszej sceny; spis całego skryptu daje dialog 52 (316 linii gry ma 50),
  cytat 50, narracja 56. Pisarze i walidator używają teraz najszerszej linii gry per rodzaj
  (`export_strings.GAME_WIDEST`), 46 zostaje zalecane; `\r` nie liczy się do szerokości. **W grze
  niesprawdzone** (hipoteza: czcionka ASCII półszeroka).
* **Budowa (13 kontenerów: config00/01/02–08, configst, eventP00, imenu00, mesbtl00; 91 s):**
  **38 598 z 39 290 sprawdzalnych tekstów wylądowało, 101 braków** (wszystkie znane: 38 bez rekordu
  w słowniku robotów, 31 przycięte/nierozkodowalne resztki, 13+11 śmieciowe wiersze liczb, 6 achievement,
  2 pseudonimy), 591 za krótkich do sprawdzenia; 40 322 wiersze z EN czekają na kontenery spoza Drive.
  Rozmiary rosną (mesbtl00 349 KB → 1 010 KB), bo zmienione członki CPK są zapisywane stored.
  Hashe i kroki: EXPERIMENT_LOG cz. 19. Wyjścia + `DO_ZROBIENIA.md` + nowe widoki idą na Drive.
* **Nie jest to grywalny patch całości:** brak ISO (rozdział 1 poza DLC), brak kontenerów rozdziałów 2–8
  poza config02–08, zero testów w grze dla tej budowy. Testy: **971 OK (1 skipped)**.
* **Następny krok:** test w PPSSPP na zbudowanych kontenerach (pula umiejętności, linie 47–52, DLC_ID);
  tłumacz: `DO_ZROBIENIA.md`; wgranie pozostałych kontenerów na Drive; ponowny eksport pakietu.

## 2026-10-14 — import `EN2.zip`, wszystkie 96 kontenerów zbudowane, pakiet do wgrania na Dysku

* **Import `EN2.zip` [ZWERYFIKOWANE]:** sceny 17 353 elementów (0 odrzuconych), widoki v2 **44 051
  wpisanych, 0 odrzuconych, 0 nieznanych** — w tym wszystkie 41 poprawek i 126 nowych tekstów. Tokeny kany
  w EN tłumacza (`%s*%s&`) importer usuwa sam (`strip_kana_tokens`); `pool_rows_refresh` dopisuje
  `tokeny.tsv` (5 225 wpisów = 100 % wierszy z `%s`). Pakiet: 108 123 wiersze, **80 780 z EN, 27 343 puste
  (same dialogi)**, 0 błędów.
* **Pole tytułu misji w `*_ext.dat` ma 40 B, nie 44 [ZWERYFIKOWANE]:** za tytułem leżą dwa u16 gry.
  Limit 39 w narzędziach i pakiecie; 10 tytułów skrócono prowizorycznie (`Ep.`) — do potwierdzenia
  przez tłumacza (`DO_ZROBIENIA_2.md`).
* **Budowa #6 na wszystkich 96 kontenerach (5 USRDIR + 91 DLC, 197 s): 96/96, 0 problemów;
  deterministyczna (dwa przebiegi #5/#5b bajt w bajt równe). Spot check: 80 084 teksty odnalezione
  w plikach wynikowych, 63 braki** (31 resztki tablic, 13 liczniki DLC_ID, 11 puste rekordy skill —
  śmieci eksportu; 6 achievementów; 2 przydomki), 633 za krótkie do sprawdzenia.
* **Fabuła w buildzie:** rozdziały 1–3 (eventP00–03) 100 %, rozdział 4 59 %, rozdziały 5–8 0 %;
  scenki poboczne eventP09/13/20–26 95–100 %, eventP27–32 0 %, evept101–102 100 %, evept103–108 9–71 %
  (128 scen w całości, 1 częściowo, 164 puste). Wszystko poza dialogami: 100 % wpisane.
* **Do wgrania (Drive „SRW OE - PATCH 2026-10-14 (EN2)"):** `DLC_EN_2026-10-14.zip` (91 EDAT, gotowe
  do skopiowania do folderu DLC emulatora), `pakiet_EN_2026-10-14.zip` + `HOKUS_POKUS.bat`
  (buduje `patched.iso` z ISO użytkownika i te same DLC), `USRDIR_EN_2026-10-14.zip`, raporty, md5,
  `docs/INSTRUKCJA_PATCH_PL.md`. Hashe/kroki: EXPERIMENT_LOG cz. 20.
* **Nie jest to skończone tłumaczenie i nie było testu w grze dla tej budowy** — to pierwszy pakiet,
  który pozwala taki test zrobić (linie 47–52, stored mesbtl00 1 MB, pula umiejętności, DLC_ID, tytuły).
  Testy: **977 OK (1 skipped)**.

### 2026-10-19 — Polish reading/reference export delivered

Four owner-requested PL3 counterparts (episodes01–03 + mech catalogue v3) are
on Drive, individually and in one ZIP; all5 files download-back verified.
5225 prose rows covered,393 catalogue unit records/1485 weapon-action entries;
PL aliases rechecked, v3 cosmetics/uncertainty retained. No game/source changes
or fresh literary translation.1695 tests OK/24 skipped.
See [Polish reading editions](reading-script/polish/README.md) and delivery receipt.
