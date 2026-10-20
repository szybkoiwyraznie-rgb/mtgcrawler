"""Read-only adapter for the early reading editions, with explicit EN/PL selection.

EN is used only to recover the delivered editorial plan. Polish never falls back
onto English. The original source rows and game tokens remain untouched.
"""
import re
from collections import defaultdict

from reading_script_source import ReadingSource, Entry, HEADINGS, jsonl, paragraphs


class EarlyReadingSource(ReadingSource):
    def __init__(self, package, episode, language='en'):
        if language not in ('en', 'pl'):
            raise ValueError('Unsupported reading language')
        self.language = language
        super().__init__(package, episode)

    def prepare_speakers(self):
        self.names = defaultdict(lambda: defaultdict(set))
        for row in jsonl(self.package / '07_names_characters.jsonl'):
            value = row.get(self.language, '')
            if row.get('key') is not None and value:
                self.names[row['key']][row.get('part')].add(value.strip())
        super().prepare_speakers()

    def make_entry(self, row):
        value = row.get(self.language, '')
        if not value.strip():
            raise ValueError(f'Missing {self.language}: {row["id"]}')
        speaker = None
        raw = row.get('speaker') or {}
        override = None
        if row['kind'] == 'dialogue':
            jp_prefix = row['jp'].splitlines()[0]
            first = value.splitlines()[0]
            if jp_prefix in ('＃？？？', '＃???'):
                if first not in ('＃？？？', '＃???'):
                    raise ValueError(f'Anonymous speaker changed: {row["id"]}')
                override = '???'
            elif jp_prefix == '＃通信／スピーカー':
                expected = {'en': '＃Comms / Speaker', 'pl': '＃Łączność / Głośnik'}[self.language]
                if first != expected:
                    raise ValueError(f'Unreviewed communications prefix: {row["id"]}')
                override = first[1:]
            elif first.startswith(('＃', '#')) or jp_prefix.startswith(('＃', '#')):
                raise ValueError(f'Unreviewed speaker prefix: {row["id"]}')
            speaker = override or self.display_names.get(raw.get('id')) or self.name(raw.get('id'))
            if override:
                value = value.split('\n', 1)[1]
        elif row['kind'] in HEADINGS:
            value = value.removeprefix('＃')
        # Display-only default protagonist names; never write them to the package.
        value = value.replace('＜主人公名＞', self.name(4501))
        if '＜主人公姓＞' in value:
            full = self.names[4501]['name_full']
            if len(full) != 1 or len(next(iter(full)).split()) != 2:
                raise ValueError('Default protagonist surname needs review')
            value = value.replace('＜主人公姓＞', next(iter(full)).split()[1])
        if re.search(r'[\u3040-\u30ff\u4e00-\u9fff\uff66-\uff9f＜＞＃\x00-\x08\x0b\x0c\x0e-\x1f]', value):
            raise ValueError(f'Unreviewed reading token: {row["id"]}')
        text = paragraphs(value)
        if not text:
            raise ValueError(f'No readable text: {row["id"]}')
        return Entry(row, speaker, text, (row['kind'], raw.get('id'), raw.get('jp'), override, speaker,
                                          paragraphs(row[self.language])))
