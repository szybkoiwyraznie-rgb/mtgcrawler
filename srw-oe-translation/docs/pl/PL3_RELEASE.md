# PL3 — sprawdzony częściowy patcher i automatyczne wydania (2026-10-19)

## Latest: v2.5 model-viewer captions

**[v2.5-PL3-UI](https://drive.google.com/file/d/1lTiINU17MPaHcm1SwOFm-A1zzYkZhic8/view)**
shortens clipped model-viewer L/R/analog/SELECT prompts to `Zmień jedn.`, `Obr.`,
`Ukryj`. Only4physical sysmes entries differ from v2.4; all code/font/skills/other
resources identical.1705tests OK/3skip, normal authentic limited-fixture CLI and
readback pass; visual runtime approval pending. **ISO YES / DLC NO / no PBOOT
recopy** on owner's accepted PPSSPP ISO path. [Proof/receipt](UI_MECH_VIEWER_2026-10-19.md).
Earlier v2.4 fixes remain included, no new font/cache experiment.

## Aktualizacja UI — najnowszy kit v2.4

**[v2.4-PL3-UI — samodzielny patcher](https://drive.google.com/file/d/1O8p3IdvyTYLLrenmAwhj83613t20Nkjr/view)**
supersedes the historical kits below. Owner accepts v2.3 Skupienie/details/no crash;
this batch keeps that repair/font and fixes system-font routing, description joins,
compact labels and Parts atlas cleanup. **ISO TAK / DLC NIE**, no PBOOT recopy in
the owner's accepted PPSSPP ISO path. All120/1985 description fields audited;
Skill00216488B (280Bmargin),1697tests OK/3skipped, normal authentic limited-fixture
CLI/readback and EN+PL release-pair pass. New UI runtime approval pending.
[Verification and installation scope](UI_QA_THIRD_2026-10-19.md),
[delivery receipt](pl3-ui-third-delivery.json). Below: historical PL3 import evidence.

## Dostawa patchera

**[srw-oe-translation-pl-v2.1-PL3.zip](https://drive.google.com/file/d/1jkVKOzRyy8QE58elwLqezi19-iNXRNGq/view)**

Pełny samodzielny kit, nie aktualizator kilku narzędzi: rozpakować do nowego
folderu i uruchomić `PATCH.bat` na własnym oryginalnym ISO1.08/odszyfrowanym DLC.
Font v5, Masaki i kontrola DLC PL są zintegrowane. Zachować oryginały i sejwy.
Nie instalować częściowego wyniku po `Build FAILED`.

ZIP zawiera narzędzia, aktualny częściowy przekład, tokeny, specyfikacje UI,
fonty do podpisów graficznych i instrukcję. Nie zawiera ISO/DLC/EBOOT, natywnych
bitmap fontu gry, screenshotów ani zapisów. `RELEASE_MANIFEST.json` obejmuje
SHA256 każdego dołączonego pliku; `translation/PL_COVERAGE.json` opisuje zakres.

## Faktyczny import PL3

Zwrot `PL3.zip`: 2748884 B, SHA256
`d34f4cae81f869e00e4260999d16ef2367dc3f78e7017c30c448f69492af8351`.
13 MD, 48326 jawnych elementów PL: 48307 importowanych zmian +19 już zgodnych.
8924 kopie wypełnione, 0 odmów/duplikatów/obcych elementów, 0 błędów walidacji.
Pakiet ma 65577 wypełnionych wierszy tekstowych z109144; nie jest pełnym PL.

Niezależny roundtrip: wszystkie48326 jawnych bloków (56672 wiersze zaplecza)
porównane z końcowym pakietem po normalizacji tokenów i po propagacji kopii:
**0 rozbieżności**. Weryfikator ma regresję wykrywającą nadpisanie świeżej
poprawki rodzaju/starego wariantu nazwy przez dawcę kopii. Nie wykonywano
skryptów tłumacza i nie wykorzystywano jego TM do automatycznego przepisywania.

Widoki po uwzględnieniu kopii:
- cytaty19841/19841, mechy4701/4701, przedmioty1200/1200;
- umiejętności4932/4932, teksty misji1279/1279, teren111/111;
- postacie2509 +4 chronione, program399 +9 literałów silnika;
- config15940 +28 pól dowiedzionych wcześniej jako binarne — pozostają puste.

Sceny (wszystkie widoczne elementy, łącznie z kopiami):

| Eksport | Wypełnione po imporcie/kopiach | Linie ponad zalecenie46 | Maks. cele |
|---|---:|---:|---:|
| epizod00 | 273/273 | 8 | 50 |
| epizod01 | 1452/1452 | 109 | 55 |
| epizod02 | 2416/2416 | 297 | 56 |
| epizod03 | 1601/1601 | 242 | 53 |

Zero linii ponad limit właściwego rodzaju ramki według obecnego walidatora
(dialog/narracja mają różne limity). To nie to samo co brak uwag powyżej46 ani
potwierdzenie renderowania w grze. Liczby obejmują kopie, więc nie muszą być
równe licznikom tłumacza. Wszystkie634 znaczące prefiksy spacji zachowane.
Słownik319 kluczy, 0 konfliktów.1421 złożeń odtworzonych, 0 dawnych trafień `roń`.

## Fizyczne pomiary — zwykły builder z dostarczonego ZIP-a

Wyodrębniony kit uruchomiono w izolacji na autentycznych kontenerach
config00/configst/font/eventP00/mesbtl00/EBOOT i config01–08 umieszczonych
w **miniaturowym, niegrywalnym ISO**. Wybrano dostępne kontenery; UI tekstur
nie przebudowywano w tym teście binarnym. CLI exit0, **0 problemów**.

- **Skill00: 215764 B / limit216768 B —1004 B zapasu**.1469 rekordów;
  trzy kontrakty wskaźników (+32/+36/+52) poprawne po odczycie.
- **Każda z8 fizycznych pul DLC15329 B / limit15638 B —309 B zapasu**,
  po720 fragmentów. Projekcja ogona Skill00 jako osobnej puli15380 B nie jest
  pomiarem DLC i nie zastępuje powyższego wyniku.
- Sprawdzone18 komórek polskiego fontu: rodzime korpusy ASCII zachowane,
  zmieniają się akcenty; pozostałe subpliki fontu nietknięte.
-397 nieidentycznych pól EBOOT zapisanych zwykłą ścieżką (bezpośredni audyt
  obejmuje399, w tym2 identyczne zJP). Źródłowe ISO/kontenery nietknięte.
- Normalne bramki rozmiaru zachowane. Żadnego historycznego bypassu A/B.

Nie było uruchomienia pełnej gry/PPSSPP w tym środowisku. Nie twierdzimy,
że ukończono gameplay QA wszystkich rozdziałów ani że każda linia mieści się
wizualnie. Nadal otwarte: rodzaj w niektórych cytatach, zgłoszone158 uwag
formatowania złożeń, dalsze epizody i layouty. Nie poprawiano literatury za tłumacza.

## EN + PL po każdym scaleniu

`.github/workflows/release.yml`:
1. PR: testy i budowa **obu** kitów z bieżącego commita; artefakty do kontroli,
   **bez publikowania Release**.
2. Push na main (także merge PR): te same testy, walidacja, budowa EN i PL,
   CRC/hashe/launchery/pokrycie, następnie jedna publikacja obu ZIP-ów,
   SHA256SUMS i metadanych PL. Błąd któregokolwiek zatrzymuje publikację.
3. Unikalna wersja numer-run/hash, target taga dokładnie commit main. Starszy
   wolniejszy build nie oznacza się Latest ponad nowszym main.

Polskie dane są wersjonowanym **tekstowym snapshotem** w `pakiet_PL/` (65566
wiązań po deduplikacji11 identycznych aliasów). CI materializuje go względem
aktualnego `pakiet_EN/`, nie czyta Drive i nie potrzebuje gry ani sekretów.
ID wierszy nie zawsze jest unikalne: wiązanie obejmuje plik i hash metadanych
źródła, bez EN/PL. Zmiana samego EN jest dopuszczalna, JP/offsetów/roli — odmowa.
Nowe puste PL nie otrzymują EN fallbacku. Jawny tekst nie może zostać zmieniony
przez propagację kopii. Szczegóły aktualizacji: `pakiet_PL/README.md`.

Zbudowano parę lokalnie oraz rzeczywiście na GitHub Actions:
[run39226067711](https://github.com/szybkoiwyraznie-rgb/mtgcrawler/actions/runs/39226067711)
— **SUCCESS** na01b9a9d, build obu kitów/artefakty, publish prawidłowo SKIPPED naPR.
Wcześniejszy run39225476467 także SUCCESS. Etapu publikacji main nie wykonywano
z niepołączonej gałęzi. Workflow zacznie publikować po scaleniu PR20; nie scalano
PR bez prośby właściciela. Lokalne testy końcowe: **1644 OK/25 pominiętych,68.832s**.

[Manifest dostawy](pl3-release-delivery.json) zapisuje SHA256/CRC/download-back
oraz granice weryfikacji. Binaria/pełne odczyty pozostają prywatne/ignorowane.

## Korekta launchera v2.1 (2026-10-19)

Usunięto komunikat `(the font step takes a moment - it recompresses font.cpk)`
z normalnego PATCH.bat. Działanie fontu/buildera bez zmian. Doprecyzowano, że
158 uwag od tłumacza dotyczy składania opisów i odstępów, np. `Po aktyw.:Obraż.`,
a nie158 błędów łamania linii. Layout to osobno wygląd tekstu w ramce w grze.
Nie poprawiano za tłumacza tych158 miejsc, rodzaju ani dalszych epizodów.

Nowy pełny ZIP v2.1:7397155B/90plików. Narzędzia buildera, przekład JSONL,
tokeny i zasoby są bajtowo identyczne z v2. Zmieniły się tylko launcher,
instrukcja, objaśnienie w PL_COVERAGE i manifest ZIP.6 testów wydania OK;
CRC/hashe i download-back zgodne. Historyczny manifest v2 pozostaje nietknięty;
[aktualny manifest v2.1](pl3-launcher-cleanup-delivery.json).
