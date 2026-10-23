""" polish_reading_source.py: source adapter for Polish reading editions (episodes 00-34). """
from collections import defaultdict
from pathlib import Path
import re
from reading_script_source import EMPTY_STRUCTURAL_IDS, Entry, HEADINGS, PROSE, ReadingSource, jsonl, paragraphs

PREFIXES = {
    'en': {
        '＃???': '???',
        '＃Comms / Speaker': 'Comms / Speaker',
        '＃Transporter': 'Transporter',
        '＃Yui/Mai': 'Yui / Mai',
        '＃Neo Zeon Soldier': 'Neo Zeon Soldier',
        '＃Pentagona Soldier': 'Pentagona Soldier',
        '＃Pentagona Officer': 'Pentagona Officer',
        '＃Simulator Mission': 'Simulator Mission',
    },
    'pl': {
        '＃???': '???',
        '＃Łączność / Głośnik': 'Łączność / Głośnik',
        '＃Przewoźnik': 'Przewoźnik',
        '＃Yui/Mai': 'Yui / Mai',
        '＃Żołnierz Neo Zeonu': 'Żołnierz Neo Zeonu',
        '＃Żołnierz Pentagony': 'Żołnierz Pentagony',
        '＃Oficer Pentagony': 'Oficer Pentagony',
        '＃Misja symulatora': 'Misja symulatora',
    },
}


class PolishReadingSource(ReadingSource):
    def __init__(self, package: Path, episode: int, language: str = 'en'):
        if language not in PREFIXES:
            raise ValueError(f'Unsupported reading language: {language}')
        if episode not in range(0, 35):
            raise ValueError(f'Story episode out of range (expected 0..34): {episode}')
        self.language = language
        super().__init__(package, episode)
        if self.language == 'en' and 202 in self.names:
            self.names[202]['_alias'].add('Yui / Mai')

    def name(self, key: int) -> str:
        for part in ('nickname', 'name_short', 'name', 'name_full'):
            values = self.names[key][part]
            if len(values) > 1:
                raise ValueError(f'Conflicting {self.language} names for speaker {key}: {values}')
            if values:
                return next(iter(values))
        raise KeyError(f'No {self.language} name for speaker {key}')

    def prepare_speakers(self) -> None:
        groups = defaultdict(set)
        for rows in self.rows.values():
            for row in rows:
                if row['kind'] == 'dialogue':
                    key = (row.get('speaker') or {}).get('id')
                    groups[self.name(key)].add(key)
        self.display_names = {}
        for short, keys in groups.items():
            full = {}
            for key in keys:
                values = self.names[key]['name_full'] or self.names[key]['name'] or {short}
                if len(values) > 1:
                    raise ValueError(f'Conflicting full names for speaker {key}: {values}')
                full[key] = next(iter(values))
            if len(set(full.values())) > 1:
                self.display_names.update(full)

    def make_entry(self, row: dict) -> Entry:
        value = row.get(self.language, '')
        if not value or not value.strip():
            raise ValueError(f'Missing {self.language} reading text for {row["id"]}')
        speaker = None
        raw = row.get('speaker') or {}
        override = None
        if row['kind'] == 'dialogue':
            jp_prefix = row['jp'].splitlines()[0]
            first = value.splitlines()[0]
            if first in PREFIXES[self.language]:
                override = PREFIXES[self.language][first]
                value = value.split('\n', 1)[1] if '\n' in value else ''
            speaker = override or self.display_names.get(raw.get('id')) or self.name(raw.get('id'))
            if jp_prefix == '＃？？？' and override != '???':
                raise ValueError(f'Anonymous speaker changed in {row["id"]}')
            if jp_prefix == '＃通信／スピーカー' and override is None:
                raise ValueError(f'Channel speaker changed in {row["id"]}')
            if first.startswith(('＃', '#')) and override is None:
                raise ValueError(f'Unreviewed speaker prefix in {row["id"]}: {first}')
        elif row['kind'] in HEADINGS:
            value = value.removeprefix('＃')
        value = value.replace('＜主人公名＞', self.name(4501))
        if '＜主人公姓＞' in value:
            full = self.names[4501]['name_full']
            if len(full) != 1:
                raise ValueError(f'Ambiguous protagonist surname: {full}')
            value = value.replace('＜主人公姓＞', next(iter(full)).split()[1])
        if re.search(r'[＜＞<>]', value):
            raise ValueError(f'Unreviewed reading token in {row["id"]}: {value}')
        text = paragraphs(value)
        if not text:
            raise ValueError(f'Empty {self.language} reading text in {row["id"]}')
        return Entry(row, speaker, text, (row['kind'], raw.get('id'), raw.get('jp'), override, speaker, paragraphs(row[self.language])))


# Backwards-compatible alias preserved for external imports and unit tests.
EarlyReadingSource = PolishReadingSource
