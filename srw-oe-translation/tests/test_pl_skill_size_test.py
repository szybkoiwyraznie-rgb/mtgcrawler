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


if __name__=='__main__':
    unittest.main()
