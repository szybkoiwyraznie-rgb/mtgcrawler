# SRW Y — tekst, którego jeszcze nie ma

Wydanie **PL9**, plan SHA-256 `d79a47452ff5e24619999e995617916fa9a05dacddf2ed0a0f2423f3a06a819e`. Wszystko poniżej jest policzone z repozytorium: `tools/deliver_remaining_text.py --check` odtwarza ten katalog.

## Co jest w katalogu

- `sceny/` i `sceny.zip` — **61810 elementów** bez polskiego tekstu w 29 plikach `.md`. To praca dla tłumacza.
- `transfer.json` — **2148 brakujących linii**, które mają już polskie brzmienie w planie (identyczne zdanie japońskie, jedno brzmienie). Nie wymagają tłumaczenia.
- `CORRECTIONS.json` — ten sam transfer w formie, którą czyta `tools/one_click_patch.py`; każdy wpis ma japoński oryginał, jego sumę i powód.

## Czego to narzędzie nie robi

- Nie tłumaczy i nie dopisuje własnego tekstu. Przenosi wyłącznie brzmienie, które tłumacz już napisał dla **identycznego** zdania japońskiego.
- Nie przenosi tekstów, które mają w planie kilka brzmień (np. 「うん…」 → 「Ano…」/「Dobrze…」/「Mhm…」) — wybór zależy od mówcy i sceny, więc zostają w paczce dla tłumacza.
- Nie rusza niczego, co jest już w planie, i nie zmienia żadnego wiersza tłumacza.

## Powody, dla których element został dla tłumacza

| powód | elementów |
| --- | ---: |
| brak polskiego odpowiednika w planie | 60004 |
| kilka polskich brzmień — wybór zależy od mówcy i sceny | 1780 |
| polskie brzmienie identyczne z japońskim | 25 |
| brak tekstu w korpusie gry | 1 |
