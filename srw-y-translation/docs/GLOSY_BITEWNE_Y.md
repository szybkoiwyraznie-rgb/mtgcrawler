# Cytaty bitewne SRW Y — dokąd doszliśmy z mówcami (2026-10-26, runda 2)

Poprzednia runda zakończyła się wnioskiem „mówców nie ma w danych”. Właściciel to
odrzucił: skoro gra puszcza konkretnemu pilotowi konkretny okrzyk, połączenie **musi**
gdzieś być. Ten dokument opisuje, co udało się ustalić bez nowych plików, czego brakuje
i co dokładnie jest potrzebne, żeby domknąć przypisanie.

## 1. Struktura klucza `battle_voice` — rozłożona

Wiersz tabeli ma klucz `high:low`, czyli 64-bitowy identyfikator wpisu Unity
Localization (para „tabela zbiorcza : klucz”). Rozbiór `low` na pola:

| pole | bity | zaobserwowane wartości |
|---|---|---|
| sekwencja | 0–11 | 0–148 |
| numer maszyny | 12–21 | **523** (`0x20B`) w 32 205 z 34 317 wierszy, 40 w pozostałych 2 112 |
| znacznik czasu | 22–63 | rośnie monotonicznie w obrębie grupy |

To układ `DistributedUIDGenerator` z pakietu Unity Localization (41 bitów czasu,
10 bitów maszyny, 12 bitów sekwencji — patrz `Runtime/Tables/Keys/DistributedUIDGenerator.cs`).
Wniosek, który zmienia wszystko: **klucze powstały partiami po ~1 000 wpisów, mniej
więcej co sekundę**, a `high` jest w obrębie partii stały. Partii jest dokładnie tyle,
ile „grup” w tabeli (31 w podstawce + 8 w dodatkach). Grupa to więc nie „numer w tabeli”,
tylko **jeden import jednego zestawu głosów** — czyli jedna postać (932–2 079 kwestii).

Ta sama analiza dla pozostałych tabel (np. `pilot_name`, `dic_text_pilot`) daje inne
pary `high`, więc klucze grup nie są identyfikatorami postaci z żadnej innej tabeli.

## 2. Czego brakuje i gdzie tego szukać

Nazwa mówcy nie jest częścią tekstu — jest w danych, do których gra sięga, żeby wybrać
klip. Dwa miejsca są rozstrzygające:

1. **`battle_voice Shared Data.asset`** (podstawka + 4 dodatki). Unity trzyma w nim
   wpisy `(id → nazwa klucza)`. Jeśli nazwy są opisowe (np. `AMRO_012`), mapa
   „grupa → postać” powstaje natychmiast, bez żadnych domysłów. Sprawdzone: obiekty
   `StringTable` (`battle_voice_ja-JP`, 28 283 wpisy) **nie** zawierają nazw — tylko
   `m_Id` i tekst, a `m_SharedData` wskazuje na osobny bundle, którego jeszcze nie mamy.
2. **`PilotBasicDatas{,_DlcOf1,_DlcOf2,_DlcOfEXP,_DlcOfEXP2}`**. Dane bazowe pilota —
   tam gra ma przypisanie „pilot → zestaw głosu”. Identyfikator zestawu głosu to
   dokładnie `high` klucza.

Do weryfikacji krzyżowej prosimy też `DicDetail_Pilot`, `RobotBasicDatas*`
i `SystemBasicDatas*`. Razem **17 plików, 3 076 247 B** — poniżej 3 MB, bo to dane,
nie audio.

## 3. Co już mamy gotowe (i czym się to sprawdza)

| narzędzie | co robi |
|---|---|
| `tools/build_voice_speaker_request.py` | rozwiązuje adresy do bundli przez katalog gier i generuje prośbę (`.ps1` + opis) — 17 plików, suma kontrolna w logu |
| `tools/collect_voice_speaker_data.ps1` | skrypt dla właściciela: kopiuje pliki z `StreamingAssets`, pakuje `srw_y_voice_data.zip` na pulpit; niczego w grze nie zmienia |
| `tools/voice_bank_map.py` | po dotarciu zipa: skanuje `Shared Data` (pary `klucz ↔ id`) i `PilotBasicDatas` (pary `kod postaci ↔ id`), zapisuje `local/s6/voice_banks.json`; `--self-check` przechodzi na danych syntetycznych, okno dopasowania pilnuje, żeby nie łapać przypadkowych par |
| `tools/voice_catalog_codes.py` | wyciąga z katalogu assetów **398 kodów postaci** i 6 627 klipów (`AMRO_001_A` → `AMRO`); to one są mostem między nazwą postaci a identyfikatorem |
| `tools/voice_bank_content.py` | dowody z treści: zaimki pierwszej osoby (`俺` 1 000+ razy, `私`, `あたし`…) i nazwy własne per grupa → `local/s6/voice_bank_evidence.{json,md}` |
| `tools/voice_identify_speaker.py` | `--phrase` (szukanie grupy po znanym okrzyku), `--anchors` (spójność: dwóch mówców nie może dzielić grupy), `--candidates` (nazwy występujące tylko w jednej grupie) |

Testy: `tests/test_voice_tools.py` (12 testów, wszystkie zielone) sprawdzają wyszukiwanie
frazy, wykrywanie niejednoznaczności, dekodowanie pól klucza i skanery danych Unity.

## 4. Dowody z treści (poszlaki, nie przypisania)

`local/s6/voice_candidates.md` (generowane) — dla każdej grupy nazwy, które **nie
pojawiają się w żadnej innej grupie**:

| grupa | kwestii | nazwy wyłączne (przykład) |
|---|---|---|
| `0000157d` | 1 447 | インベル ×47, イデオン ×20, コスモ ×29, ヴィルキス ×19 |
| `0001168c` | 947 | ダ・ガーン ×58, 星史 ×25, 鋼鉄ジーグ ×7, レッドガイスト ×12 |
| `00000411` | 1 172 | 翔太郎 ×28, ビッグオー ×18, ベック ×12, ビッグデュオ ×8 |
| `000a9ed0` | 2 079 | ニカ ×16, グーゴル・プレックス ×14, 虚神ラグマドク ×13 |
| `01999dcc` | 1 049 | 拓馬 ×28, バグ ×24, インセクター ×17 |

Dlaczego to za mało, żeby wpisać imię do paczki: kwestie cytują **cudze** roboty i bronie
(«来い、蜃気楼蛟!» pada w dwóch grupach, a アムロ pojawia się w czterech). Dopóki nie
odczytamy identyfikatora zestawu głosu z `PilotBasicDatas`, każde imię byłoby zgadywaniem.

## 5. Kolejność działań

1. Właściciel uruchamia `tools/collect_voice_speaker_data.ps1` (prawy klik → Uruchom
   z PowerShell) i wrzuca `srw_y_voice_data.zip` na Drive.
2. `python3 tools/voice_bank_map.py` → `local/s6/voice_banks.json` z parami
   `grupa ↔ kod ↔ nazwa`.
3. Krzyżowa weryfikacja z sekcją 4: jeśli odczytany mówca nie zgadza się z nazwami,
   które grupa sama wymienia — szukamy dalej, nie publikujemy.
4. Nowa wersja paczki: etykiety `[Cytat bitewny — アムロ (Amuro)]` zamiast `[głos 7/39]`.
   Cytaty i tłumaczenia bez zmian — podmienia się tylko nagłówek elementu.

## 6. Kotwice: „znam ten okrzyk, wiem kto go mówi"

Gdyby właściciel (albo tłumacz) chciał sprawdzić mapowanie bez plików danych, wystarczy
kilka pewnych okrzyków. Format `--anchors` to lista:

```json
[
  {"phrase": "ブライ・ソード", "speaker": "Braiger"},
  {"phrase": "イデオンソード", "speaker": "Cosmo"}
]
```

```text
python3 tools/voice_identify_speaker.py --anchors kotwice.json --derive
```

Narzędzie wyszuka frazę w tabeli, wskaże grupę, **odrzuci sprzeczność** (dwóch mówców
w jednej grupie, jedna fraza w kilku grupach po równo) i wypisze kolejność tworzenia grup
(znaczniki czasu z klucza), która jest dodatkowym dowodem przy łączeniu z listą kodów
postaci z katalogu assetów.

## 7. Czego nie zrobimy

- nie wpiszemy imienia na podstawie statystyki nazw w treści (błąd w paczce jest gorszy
  niż numer grupy),
- nie ogłosimy sukcesu bez plików od właściciela — zgodnie z zasadą „żadnych twierdzeń
  o działaniu bez dowodu”.
