# Nazwy Rozkazów ducha — pełne słowa w budżecie 10 znaków

**Data:** 2026-11-06. **Wchodzi do:** `PLAN_PL2.json` (źródło patcha), patcha
**`SRW_Y_PATCH_PL5_NAZWY_DUCHOW.zip`** (5 171 767 B, SHA-256
`80195405…ba589`, Drive `1mrpSKP4zXzmctizyRKS0mKKqrzT7RgLk`) i czytanek **v15** (`SRW_Y_CZYTANKI_PL2_POPRAWIONE_v15.zip`,
1 547 358 B, SHA-256 `9cb4e118…df9ab`, Drive `1zUbRe-VNeXsxCZ2c-9m6imWd-XkLQPSf`).

## Co było nie tak

Do v8 limit każdej nazwy Rozkazu ducha liczył się z **długości angielskiego słowa**:
`魂` / „Soul” → 4 znaki, `熱血` / „Valor” → 5. To nie był limit pola w grze, tylko
artefakt podziału tabeli na kolumny (opis w `docs/LIMITY_Y.md`, §7). Tłumacz, żeby
zmieścić się w tak postawionej granicy, pisał skróty z kropką: „Dus.”, „Mił.”,
„Prz.”, „Dop.”, „Zawz.”, „Cel.str.”.

Prawdziwa szerokość pola jest jedna dla całej kolumny: **10 znaków** — tyle ma
najdłuższa nazwa, jaką gra pokazuje (`威圧` / „Intimidate”,
`data/s6-derived/groups.json`: `cap: 10`, `cells_en_max: 10`). Opisy mają osobny
budżet: 193 znaki.

## Co zrobiono

`tools/improve_spirit_names.py` podmienia w planie 30 skróconych nazw na pełne
polskie słowa, nie zmieniając **niczego** innego — żadnego klucza, żadnej liczby
wierszy, żadnego opisu. Audyt dostaje nowy `plan_sha256`; `input_sha256`
i `manifest_sha256` zostają, bo tekst wejściowy i manifest się nie zmieniły.

| jp | EN | było | jest | znaków |
|---|---|---|---|---:|
| 努力 | Gain | Wys. | **Wysiłek** | 7 |
| 希望 | Wish | Cud | **Życzenie** | 8 |
| 愛 | Love | Mił. | **Miłość** | 6 |
| 覚醒 | Zeal | Prz. | **Gorliwość** | 9 |
| 鉄壁 | Wall | Mur | **Bariera** | 7 |
| 魂 | Soul | Dus. | **Dusza** | 5 |
| 信頼 | Trust | Zauf. | **Zaufanie** | 8 |
| 共感 | Unity | Zgoda | **Jedność** | 7 |
| 友情 | Faith | Wiara | **Przyjaźń** | 8 |
| 巧手 | Trick | Zręc. | **Zręczność** | 9 |
| 応援 | Cheer | Dop. | **Wsparcie** | 8 |
| 根性 | Vigor | Hart | **Wytrwałość** | 10 |
| 激励 | Rouse | Zagr. | **Zachęta** | 7 |
| 狙撃 | Snipe | Snaj. | **Snajper** | 7 |
| 祝福 | Bless | Błog. | **Łaska** | 5 |
| 脱力 | Daunt | Osł. | **Osłabienie** | 10 |
| 重撃 | Crush | Miaż. | **Miażdżenie** | 10 |
| 闘志 | Smash | Zawz. | **Zawziętość** | 10 |
| 集中 | Focus | Skup. | **Skupienie** | 9 |
| 感応 | Attune | Więź | **Rezonans** | 8 |
| 気合 | Spirit | D.wal. | **Duch walki** | 10 |
| 直撃 | Pierce | Przes. | **Przeszycie** | 10 |
| かく乱 | Disrupt | Zamęt | **Zakłócenie** | 10 |
| 不屈 | Persist | Niezł. | **Niezłomny** | 9 |
| 先見 | Foresee | Wizja | **Przeczucie** | 10 |
| 幸運 | Fortune | Fortuna | **Szczęście** | 9 |
| 必中 | Bullseye | Cel.str. | **Pewny cel** | 9 |
| 補給 | Resupply | Zaopatr. | **Dostawa** | 7 |
| 威圧 | Intimidate | Zastrasz. | **Postrach** | 8 |
| 加速 | Accel | Pęd | **Rozpęd** | 6 |

Pozostałe 11 nazw (Valor „Zapał”, Mercy „Litość”, Bonds „Więzy”, Flash „Błysk”,
Charge „Szarża”, Bravery „Męstwo”, Prospect „Nadzieja”, Analyze „Analiza”,
Intuition „Intuicja”, Press „Napór”, Faith→Przyjaźń policzona wyżej) mieściło się
w limicie i zostały bez zmian.

## Gdzie to trafia

* `translations/pl2/PLAN_PL2.json` — nowe brzmienie (źródło patcha; **przyszłe**
  paczki patchera biorą je stąd automatycznie),
* `translations/pl2/AUDIT_PL2.json` — nowy `plan_sha256`, reszta bez zmian,
* `SRW_Y_PATCH_PL5_NAZWY_DUCHOW.zip` — patch do gry zbudowany z tego planu,
* `docs/reading/pl2-oe-format/` + `SRW_Y_CZYTANKI_PL2_POPRAWIONE_v15.zip` —
  czytanki z pełnymi nazwami; wierszy tabel ubyło/przybyło tyle, ile wynika
  z szerszej kolumny (56 079 → 56 480 wierszy kontynuacji).

## Kontrole

* `tests/test_spirit_names.py` — 41 nazw mieści się w 10 znakach, żadna nie jest
  skrótem z kropką, żadna nie jest krótsza niż 4 znaki, `cap` pochodzi z danych gry,
  a narzędzie jest idempotentne (`--check` → 0).
* `tools/improve_spirit_names.py --check` — 0, gdy plan ma już pełne nazwy.
* `python3 tools/rebuild_reading_pl2.py --check` — czytanki odtwarzają się z repo
  bajt w bajt.
* Pełny zestaw: **784 passed, 4 558 subtests**.
