"""Per-mission encyclopedia terms and series in the deployment document."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'docs/reading/pl2-oe-format/srwy_mission_deployments.md'
KINDS = ROOT / 'data/dictionary_word_kinds.json'
LINKS = ROOT / 'data/dictionary_links.json'
TABLES = ROOT / 'data/s6-full/tables.jsonl'
TERMS_HEAD = '#### Hasła encyklopedii w dialogach tej misji'
SERIES_HEAD = '#### Serie reprezentowane w misji'
CJK = re.compile(r'[\u3040-\u30ff\u4e00-\u9fff]')


def missions(text):
    parts = re.split(r'\n### Misja ', text)[1:]
    return parts


def test_every_mission_carries_both_new_blocks():
    text = DOC.read_text(encoding='utf8')
    parts = missions(text)
    assert len(parts) == 51
    for part in parts:
        assert part.count(TERMS_HEAD) == 1, part.splitlines()[0]
        assert part.count(SERIES_HEAD) == 1, part.splitlines()[0]
        terms, series = part.split(TERMS_HEAD, 1)[1].split(SERIES_HEAD, 1)
        assert re.search(r'^\*\*.+\*\*$', series, re.M), part.splitlines()[0]


def test_terms_are_glossary_entries_only_and_series_use_game_titles():
    text = DOC.read_text(encoding='utf8')
    first = missions(text)[0]
    terms = first.split(TERMS_HEAD, 1)[1].split(SERIES_HEAD, 1)[0]
    titles = re.findall(r'^\*\*(.+?)\*\*$', terms, re.M)
    assert titles, 'misja 1 bez haseł'
    assert 'Wojna rewolucyjna' in titles
    # Characters and mechs are excluded by the curated split; these heads are known
    # to be people or machines, so they must never show up as terms.
    for forbidden in ('Treize', 'Dr Hell', 'Devil Gundam', 'Lelouch', 'Nataku'):
        assert forbidden not in titles
    series = first.split(SERIES_HEAD, 1)[1]
    assert 'Mobile Suit Gundam Wing: Endless Waltz' in series


def test_the_document_holds_no_source_language_text():
    text = DOC.read_text(encoding='utf8')
    assert not CJK.search(text)
    assert '[Brak polskiego opisu]' not in text


def test_classification_covers_only_real_dictionary_headwords():
    kinds = json.loads(KINDS.read_text(encoding='utf8'))
    assert kinds['schema'] == 1
    assert kinds['method']
    links = json.loads(LINKS.read_text(encoding='utf8'))
    titles = set()
    rows = {}
    for line in TABLES.read_text(encoding='utf8').splitlines():
        row = json.loads(line)
        rows[(row['table'], row['key'])] = row.get('jp') or ''
    for items in links['groups']['word'].values():
        for item in items:
            if str(item.get('logical', '')).endswith('_title'):
                titles.add((rows.get((item['table'], item['address'])) or '').strip())
    # 81 title rows, 78 distinct headwords: `機動忍鎧` is listed under two ids.
    assert len(titles) == 78
    classified = set(kinds['characters']) | set(kinds['mechs'])
    assert classified <= titles, classified - titles
    assert not (set(kinds['characters']) & set(kinds['mechs']))
    assert len(kinds['characters']) == 18 and len(kinds['mechs']) == 4
