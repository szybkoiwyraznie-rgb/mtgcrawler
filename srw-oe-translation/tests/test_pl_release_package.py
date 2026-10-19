"""Text-only snapshot tests, no game data or Drive credentials."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import pl_release_package as P
import translation_import as I


class PlReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.base=self.root/'EN';self.pkg=self.root/'imported'
        self.stored=self.root/'stored';self.out=self.root/'out'
        self.rows=[dict(id='reused',jp='字',en='English one',part='text'),
                   dict(id='reused',jp='文',en='English two',part='text')]
        self.write(self.base,self.rows)
        self.write(self.pkg,[dict(self.rows[0],pl='  Żółć '),dict(self.rows[1],pl='Łódź')])

    def write(self,where,rows):
        where.mkdir(exist_ok=True)
        (where/'04_config_text.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n'for r in rows),encoding='utf-8')
        (where/'tokeny.tsv').write_text('# empty\n')

    def freeze(self):
        return P.snapshot(self.base,self.pkg,self.stored,'PL3.zip','a'*64)

    def read(self):
        return I.load_rows(self.out)[0]

    def mutate_snapshot(self,change):
        path=self.stored/P.DATA;entries=[json.loads(l)for l in path.read_text().splitlines()]
        change(entries)
        data=''.join(P.canonical(r)+'\n'for r in entries).encode();path.write_bytes(data)
        m=json.loads((self.stored/P.MANIFEST).read_text());m.update(data_sha256=hashlib.sha256(data).hexdigest(),entries=len(entries))
        (self.stored/P.MANIFEST).write_text(json.dumps(m))

    def test_reused_ids_bind_by_full_source_not_id(self):
        m=self.freeze();self.assertEqual(m['entries'],2)
        P.materialize(self.base,self.stored,self.out)
        self.assertEqual([r['pl']for r in self.read()],['  Żółć ','Łódź'])
        self.assertEqual([r['en']for r in self.read()],['English one','English two'])
        entries=[json.loads(l)for l in (self.stored/P.DATA).read_text().splitlines()]
        self.assertTrue(all(set(r)=={'file','id','source_sha256','pl'}for r in entries))

    def test_english_wording_changes_do_not_invalidate_polish(self):
        self.freeze();self.rows[0]['en']='Updated English';self.write(self.base,self.rows)
        P.materialize(self.base,self.stored,self.out)
        self.assertEqual(self.read()[0]['en'],'Updated English')
        self.assertEqual(self.read()[0]['pl'],'  Żółć ')

    def test_changed_japanese_or_offset_fails_closed(self):
        self.freeze();self.rows[0]['source']={'offset':123};self.write(self.base,self.rows)
        with self.assertRaisesRegex(ValueError,'stale'):P.materialize(self.base,self.stored,self.out)
        self.assertFalse(self.out.exists())

    def test_new_source_row_is_blank_not_english_fallback(self):
        self.freeze();self.rows.append(dict(id='new',jp='新',en='Never Polish',part='text'))
        self.write(self.base,self.rows);P.materialize(self.base,self.stored,self.out)
        self.assertEqual(self.read()[-1]['pl'],'')

    def test_identical_physical_aliases_are_deduplicated_and_restored(self):
        self.rows.append(copy.deepcopy(self.rows[0]));self.write(self.base,self.rows)
        self.write(self.pkg,[dict(self.rows[0],pl='  Żółć '),dict(self.rows[1],pl='Łódź'),dict(self.rows[2],pl='  Żółć ')])
        self.assertEqual(self.freeze()['entries'],2)
        P.materialize(self.base,self.stored,self.out);self.assertEqual(self.read()[0]['pl'],self.read()[2]['pl'])

    def test_hash_corruption_refused(self):
        self.freeze();(self.stored/P.DATA).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'hash'):P.materialize(self.base,self.stored,self.out)

    def test_path_escape_is_never_written(self):
        self.freeze();self.mutate_snapshot(lambda entries:entries[0].update(file='../escape.jsonl'))
        with self.assertRaisesRegex(ValueError,'unknown'):P.materialize(self.base,self.stored,self.out)
        self.assertFalse((self.root/'escape.jsonl').exists())

    def test_duplicate_entry_refused_even_with_matching_hash(self):
        self.freeze();self.mutate_snapshot(lambda entries:entries.append(entries[0]))
        with self.assertRaisesRegex(ValueError,'duplicate'):P.materialize(self.base,self.stored,self.out)

    def test_invalid_polish_is_revalidated_on_materialization(self):
        self.freeze();self.mutate_snapshot(lambda entries:entries[0].update(pl='🦆'))
        with self.assertRaisesRegex(ValueError,'validation'):P.materialize(self.base,self.stored,self.out)

    def test_snapshot_refuses_modified_source_metadata(self):
        self.write(self.pkg,[dict(self.rows[0],jp='違',pl='Text'),dict(self.rows[1],pl='Text')])
        with self.assertRaisesRegex(ValueError,'binding'):self.freeze()

    def test_output_never_overwrites_existing_work(self):
        self.freeze();self.out.mkdir()
        with self.assertRaisesRegex(ValueError,'refusing'):P.materialize(self.base,self.stored,self.out)
