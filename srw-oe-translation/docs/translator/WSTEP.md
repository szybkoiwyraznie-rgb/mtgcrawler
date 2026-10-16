# Wstęp do nowej sesji: tłumaczenie SRW OE (JP → EN), ciąg dalszy

Kontynuujesz rozpoczęty projekt tłumaczenia gry **Super Robot Wars OE** z japońskiego na angielski.
Odpowiadaj mi po polsku. W tym projekcie NIE wersjonujemy plików: zawsze nadpisuj jedną, ostateczną wersję.

## Stan projektu
- **Gotowe i przyjęte przez autora patcha:** wszystkie widoki (postacie, mechy, przedmioty, umiejętności, teksty-config, teksty-misji, cytaty) oraz fabuła epizod-00 … epizod-15.
- **Do zrobienia:** `epizod-16.md` … `epizod-34.md` oraz `simulator.md`. epizod-34 jest bardzo duży (~950 KB): dziel go na 3–4 części po grupach scen, z sufiksem (_a, _b…).
- Gotowe pliki odsyłam autorowi patcha porcjami. Format i numeracja muszą zostać bez zmian.

## Gdzie co leży (mój komputer, folder `…\Pulpit\Claude Cowork\trOE`, poproś o dostęp)
- `sceny.zip`: japońskie źródła fabuły (epizod-00…34, simulator, spis-scen).
- `widoki_v2.zip`: aktualne widoki (wersja v2, z numeracją autora patcha).
- `tokeny.tsv`: klasyfikacja każdego `%s` (L/T/C). Musi leżeć w `/home/claude/work/tokeny.tsv`.
- `README.md`: oryginalna instrukcja autora pakietu.
- `tlumaczenie\EN\sceny\` i `tlumaczenie\EN\widoki\`: **pełna, aktualna wersja angielska**. Tu dopisuj kolejne odcinki pod oryginalnymi nazwami plików.
- `tlumaczenie\_robocze\stan_pracy.zip`: cały warsztat do rozpakowania w `/home/claude/`:
  - `work/STYLE.md`: wiążące zasady stylu i techniczne. **Przeczytaj w całości.**
  - `work/SCENE_BRIEF.md`: instrukcja dla agenta tłumaczącego odcinek.
  - `work/glossary.json`: postacie, serie i terminy (oficjalne angielskie nazwy).
  - `work/glossary_extra.tsv`: mechy, bronie, ataki, umiejętności, duchy, nowe nazwy z odcinków, decyzje.
  - `work/voice_cards.md`: 175 kart głosu postaci.
  - `work/bible/`: streszczenia fabuły odcinków (część odcinków je ma, agenci dopisują brakujące).
  - `work/tr/`: pliki tłumaczeń w formacie `#G`/`@id`.
  - `tool/tr.py`: walidator, ekstraktor i scalanie; `tool/tm.py`: pamięć tłumaczeń; `tool/persist.sh` i `tool/mergeall.sh`.

## Rozruch środowiska (zrób raz na początku sesji)
1. Poproś o dostęp do folderu `trOE`. Przenieś do chmury (stage) pliki: `stan_pracy.zip`, `sceny.zip`, `widoki_v2.zip`, `tokeny.tsv` oraz pliki z `tlumaczenie\EN\` (mogą być spakowane).
2. Rozpakuj `stan_pracy.zip` do `/home/claude/`, co da katalogi `work/` i `tool/`.
3. Rozpakuj `sceny.zip` do `/home/claude/src/`, a `widoki_v2.zip` do `/home/claude/src/w/`. Skopiuj `tokeny.tsv` do `/home/claude/work/`.
4. Skopiuj gotowe pliki EN do `/home/claude/out/sceny/` i `/home/claude/out/widoki/`. Pamięć tłumaczeń i `persist.sh` z nich korzystają.
5. Sprawdź: `python3 /home/claude/tool/tr.py check /home/claude/out/sceny/epizod-15.md` ma dać 0 błędów.

## Jak pracować nad jednym odcinkiem
1. Uruchom **jednego** agenta (general-purpose) z poleceniem: „Read /home/claude/work/SCENE_BRIEF.md and follow it. FILE = epizod-NN, whole file, no suffix. Put helper scripts in /home/claude/work/scratch/epizod-NN/.”
2. Po jego zakończeniu scal wynik: `bash /home/claude/tool/mergeall.sh` (wynik trafia do `/home/claude/out/sceny/` oraz do `/mnt/user-data/outputs/EN/…`).
3. Zapisz na moim dysku (commit): `EN\sceny\epizod-NN.md` oraz zaktualizowany `_robocze\stan_pracy.zip`. Najlepiej po każdym odcinku, bo kontener w chmurze może zostać wyczyszczony.
4. Zrelacjonuj krótko: liczba linii, 0 błędów, ważniejsze decyzje.

## Zasady limitów (bardzo ważne)
- **Nigdy nie uruchamiaj agentów równolegle.** Zawsze jeden naraz.
- **Przed każdym agentem zapytaj mnie o aktualne procenty limitu** (5-godzinny / tygodniowy). Sam ich nie widzisz, ja je podaję.
- Kalibracja z poprzedniej sesji: **jeden odcinek kosztuje ok. 10–12% okna 5h i ok. 2–3% tygodnia** (agent zużywa ok. 230–330 tys. tokenów). Duże odcinki (22, 28, 30, 34) kosztują proporcjonalnie więcej.
- Domyślnie zatrzymuj się tak, żeby **nie przekroczyć 80%** w oknie 5h ani w tygodniu. Wyższy pułap tylko za moją wyraźną zgodą (czasem pozwolę dojść blisko 100%, ale nigdy ponad, bo przerwane zadanie marnuje tokeny).
- Twoja własna koordynacja też kosztuje, i to tym więcej, im dłuższa rozmowa (pod koniec poprzedniej sesji jedna wiadomość zjadała ~1% okna). Pisz zwięźle, nie czytaj dużych plików w głównym wątku (to robią agenci) i ograniczaj liczbę wywołań narzędzi.
- Nie używaj zaplanowanych zadań (scheduled tasks). Kolejne etapy uruchamiam ręcznie.

## Kluczowe decyzje stylu (pełne w STYLE.md i glosariuszu)
- Oficjalna angielska terminologia (angielskie SRW V/X/T/30, potem oficjalne wydania anime, w ostateczności konwencja fanowska).
- Bez honoryfików, imiona w kolejności Imię Nazwisko, tylko znaki CP932 (bez makronów, akcentów, myślników — i –).
- Tokeny `＜主人公名＞` i `＜主人公姓＞` zostają bez zmian. `⏎` zostaje w tym samym miejscu. `<0x0F>` usuwamy razem z następnym znakiem.
- Duchy: Bullseye, Flash, Fortune, Gain itd. 気力 = **Will**. Umiejętności: Potential, Instinct, Fighter's Spirit, Supreme, Battler, Meikyou-Shisui.
- Okrzyki drużyn zostają zromanizowane: „Nekketsu Saikyo!”, „Genki Bakuhatsu!”, „Matchless!”.
- Stopnie w Gundamie UC według systemu morskiego (Char = Lieutenant Commander, w zwrotach „Commander”).
- Tytuły misji w polach 39 B zapisujemy jako „Ep. N: …”. W dialogach i narracji używamy „Episode”.
- Szerokość linii: zalecane 46 jednostek. Twardy limit autora: dialog 52, cytat 50, narracja 56.
