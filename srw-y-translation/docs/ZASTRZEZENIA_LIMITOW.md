# 25 linii, które nie mieszczą się w węższym polu — i co z nimi robię

**Krótka odpowiedź na pytanie „co mam zdecydować?”: nic.** To nie jest wybór
właściciela, tylko 25 konkretnych zdań do skrócenia — robota dla mnie i tłumacza.
Poprzednia wersja tego pliku niepotrzebnie odkładała ją na Ciebie.

## Skąd te 25 pozycji

* W grze ten sam japoński tekst i to samo `EN:` stoją czasem w **dwóch wierszach**
  tabeli — np. cytat bitewny powtórzony w drugim banku głosu. Tłumacz wpisuje
  przekład **raz**, w pierwszym wierszu; drugi dziedziczy go sam („powtórzenie
  elementu N — nie wpisuj tu nic”).
* Szerokość pola mierzymy z danych gry: limit to najdłuższy tekst, jaki gra
  w tym polu pokazuje (`data/limits_y.json`, `tools/s6_groups.py`). Powtórzony
  wiersz ma **własny, węższy** limit — tak samo traktuje to nasz importer, zgodnie
  z regułą z OE („kopia ma własny budżet”, `tests/test_pl_import_oe_regressions.py`).
  Reguła jest słuszna: gdy kopia trafi do węższego widgetu, za długi tekst się utnie.
* Plan PL2 powstał w imporcie **bez** pomiaru limitów (wtedy `limits.json` jeszcze
  nie istniał), więc 25 przekładów jest o 1–12 znaków dłuższych niż węższe pole.
  Wszystkie są w wydanym patchu; żadnego zachodzenia tekstu nie zgłosiłeś.

## Decyzja: zostawiam tekst, lista skrótów leży w zapasie

**Tekst przekładu nie został zmieniony ani na znak** i nie planuję go zmieniać.
Powody:

* różnica to 1–12 znaków, a „limit” to najdłuższy tekst **zaobserwowany** w polu,
  nie zmierzona szerokość prostokąta; zapasu zwykle trochę jest,
* większość tych linii to cytaty bitewne (kwestie mówione) — skróty typu
  „System plot., start!” czytają się w grze gorzej niż o 14 znaków dłuższe zdanie,
* żadnego zachodzenia tekstu nie zgłosiłeś, a wszystkie 25 linii są w wydanym patchu.

Skrócone wersje (`propozycja`) są więc **w zapasie**, każda sprawdzona tym samym
walidatorem, którego używa import (długość, tokeny gry). Jeśli kiedykolwiek
zobaczysz na zrzucie, że któraś z tych linii zachodzi na sąsiednią — wystarczy
słowo, biorę wariant z tabeli (albo robię nowy, krótszy). Nic nie czeka na decyzję.
Linia „Jeszcze nie!” do 8 znaków nie da się skrócić bez utraty sensu, więc dla niej
propozycji nie ma.

Nowe linie ponad limit nie przejdą już cicho: `tests/test_patch_pipeline_repo.py`
pilnuje, żeby takich pozycji nie było więcej niż te znane 25.

| tabela | klucz | limit | teraz | propozycja | EN |
| --- | --- | --- | --- | --- | --- |
| battle_voice | `01999dca:d020b000` | 28 | Ja i Aerial będziemy z tobą walczyć! (36) | Aerial i ja walczymy z tobą! (28) | Aerial and I will fight you! |
| battle_voice | `01999dcb:1b60b000` | 10 | Tam jesteś! (11) | Mam cię! (8) | Got you! |
| battle_voice | `01999dcb:2760b000` | 10 | Tam jesteś! (11) | Mam cię! (8) | Got you! |
| battle_voice | `01999dd2:94a0b001` | 20 | Błysk smoczych kłów!! (21) | Smocze kły — błysk! (19) | Dragon fangs, flash! |
| battle_voice | `01999dd3:2420b000` | 34 | System obrony przeciwlotniczej, start! (38) | System plot., start! (20) | Anti-air system, engage! |
| battle_voice | `01999dd3:2da0b000` | 24 | System obrony przeciwlotniczej, start! (38) | System plot., start! (20) | Anti-air system, engage! |
| battle_voice | `01999dd4:a8a0b000` | 35 | Nie może być…! J-jesteśmy nieśmiertelni!! (41) | Niemożliwe… nieśmiertelni?! (27) | Impossible! We...We are immortal! |
| battle_voice | `01999dd5:19e0b000` | 17 | Tym to rozstrzygnę! (19) | To rozstrzygnie! (16) | This will end it! |
| battle_voice | `01999dd5:4de0b000` | 14 | Huknij, gromie! (15) | Huknij gromem! (14) | Roar, thunder! |
| battle_voice | `01999dd8:4fe0b000` | 10 | Tam jesteś! (11) | Tu jesteś! (10) | There! |
| battle_voice | `01999dd9:ab60b000` | 19 | Pancerz mnie uratował…! (23) | Pancerz wytrzymał! (18) | My armor saved me! |
| battle_voice | `01999dda:0320b000` | 8 | Jeszcze nie! (12) | — zostaje bez zmian (sens nie do zmieszczenia w 8 znakach) | Not yet! |
| battle_voice | `01999ddf:fce0b000` | 22 | Pierwszy ruch jest mój…! (24) | Inicjatywa jest moja! (21) | I have the initiative. |
| battle_voice | `01999de1:d8a0b000` | 17 | Natychmiast odpowiedzieć ogniem! (32) | Ognia! (6) | Shoot it at once! |
| battle_voice | `01999de4:2360b000` | 10 | Tam jesteś! (11) | Tu jesteś! (10) | There! |
| battle_voice-DLC1 | `00000411:d560b030` | 21 | A teraz policz swoje grzechy… (29) | Policz swe grzechy… (19) | Now, count up... |
| skill_active_search-DLC1 | `00000b4e:c8e0b015` | 10 | Detektyw Fuuto (14) | Detektyw (8) | Fuuto's PI |
| system_text | `009a8dad:1e20b00c` | 6 | Rozmiar (7) | Wymiar (6) | Size |
| system_text | `009a8dad:1e20b01f` | 15 | Wymagana umiejętność (20) | Wymagana umiej. (15) | Required Skill |
| system_text | `009a8dad:1f20b019` | 4 | Maszyna (7) | Mech (4) | Unit |
| system_text | `00d07487:29a0b002` | 16 | Programy umiejętności (21) | Programy umiej. (15) | Skill Programs |
| tutorial_text | `002bd864:73e0b000` | 13 | Ulepsz maszyny (14) | Ulepsz mechy (12) | Upgrade Mechs |
| tutorial_text | `002bd864:7720b000` | 11 | Załóż części (12) | Załóż część (11) | Equip Parts |
| ICE_operation | `00000049:c8e0b00e` | 44 | Zestrzelenie jednego z: [p1:], [p2:], [p3:], [p4:]. (51) | Zestrzelono: [p1:], [p2:], [p3:], [p4:]. (40) | [p1:], [p2:], [p3:], or [p4:] defeated. |
| ICE_operation | `00000049:c920b025` | 77 | - Rzuć do walki wszystko, czego nauczyły cię dotychczasowe bitwy, i wygraj ostatnie starcie! (92) | - Wykorzystaj wszystko, czego nauczyły cię dotychczasowe bitwy, i wygraj! (73) | ・This is the final battle. Use everything 　 you've learned on the way here! |

## Jak to sprawdzić samemu

```sh
python3 tools/prepare_local_sources.py --write
python3 tools/build_translator_package.py --out-dir /tmp/pkg --source-dir local/s6
python3 tools/pl_fill_return.py --manifest /tmp/pkg/import_manifest.json \
  --plan translations/pl2/PLAN_PL2.json --out /tmp/zwrotka --check --source-dir local/s6
```

Raport pokaże `pominięto (…)`: 25 pozycji to właśnie te linie (limit 3, 4, 6 … 77).
Po podmianie na propozycje lista pominięć jest pusta, a reszta planu bez zmian.
