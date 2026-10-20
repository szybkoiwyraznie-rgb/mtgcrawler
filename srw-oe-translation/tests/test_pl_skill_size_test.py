"""Synthetic-only coverage of the opt-in experiment; no proprietary fixtures."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import pl_skill_size_test as T
import item_skill_write as W


class TrialTests(unittest.TestCase):
    def test_guard_is_restored_after_normal_scope_and_exception(self):
        before=W.MEMBER_SIZE_LIMITS.copy()
        with T.experimental_budget():
            self.assertNotIn(T.MEMBER,W.MEMBER_SIZE_LIMITS)
            self.assertIsNone(W.size_limit_problem(T.MEMBER,W.SKILL00_LIMIT+8000))
        self.assertEqual(W.MEMBER_SIZE_LIMITS,before)
        with self.assertRaisesRegex(RuntimeError,'synthetic failure'):
            with T.experimental_budget():
                raise RuntimeError('synthetic failure')
        self.assertEqual(W.MEMBER_SIZE_LIMITS,before)
        self.assertIsNotNone(W.size_limit_problem(T.MEMBER,W.SKILL00_LIMIT+1))

    def test_requires_explicit_ack_before_any_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            with self.assertRaisesRegex(ValueError,'acknowledgement'):
                T.build(root/'missing.iso',root/'package',root/'out','')
            self.assertFalse((root/'out').exists())

    def test_selected_text_is_verbatim_and_other_pl_is_not_applied(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);source=root/'source';source.mkdir()
            selected={'id':'s','jp':'a','en':'A','pl':'Próba bez skrótu',
                      'source':{'container':'config00.cpk','member':T.MEMBER}}
            other={'id':'other','jp':'b','en':'B','pl':'Nie stosuj',
                   'source':{'container':'config00.cpk','member':'Other.bin'}}
            (source/'03_skills.jsonl').write_text(json.dumps(selected)+'\n'+json.dumps(other)+'\n')
            counts=T.select_package(source,root/'target',set())
            actual=[json.loads(l)for l in(root/'target/03_skills.jsonl').read_text().splitlines()]
            self.assertEqual(actual[0],selected)
            self.assertEqual(actual[1],{**other,'pl':''})
            self.assertEqual(counts['03_skills.jsonl'],1)

class NativeControlTests(unittest.TestCase):
    def test_japanese_control_uses_native_codec_and_restores_pl(self):
        from test_item_skill_write import build_member, build_record
        import text_codec
        import item_skill_records as R
        blob=build_member('skill',[build_record('skill',1000,'ｶﾅ','攻撃ｶﾅ'),build_record('skill',1001,'長い名前','長い説明テキスト')],pool_runs=['気力'])
        previous=text_codec.lang()
        try:
            text_codec.set_lang('pl')
            with T.experimental_budget():
                padded=T.grow_control(blob,len(blob)+4)
            self.assertEqual(text_codec.lang(),'pl')
            self.assertEqual(len(padded),len(blob)+4)
            before=R.parse_member(blob,'skill',T.MEMBER)['records'][0]
            after=R.parse_member(padded,'skill',T.MEMBER)['records'][0]
            self.assertEqual(W.field_raw(padded,after,'effect'),W.field_raw(blob,before,'effect')+b'    ')
            self.assertEqual(W.field_raw(padded,after,'name'),W.field_raw(blob,before,'name'))
        finally:
            text_codec.set_lang(previous)

    def test_codec_restored_when_control_writer_refuses(self):
        from unittest.mock import patch
        import text_codec
        previous=text_codec.lang()
        try:
            text_codec.set_lang('pl')
            with patch.object(T.M,'grow_with_spaces',side_effect=ValueError('synthetic refusal')):
                with self.assertRaisesRegex(ValueError,'synthetic refusal'):
                    T.grow_control(b'fixture',123)
            self.assertEqual(text_codec.lang(),'pl')
        finally:
            text_codec.set_lang(previous)


if __name__=='__main__':
    unittest.main()
