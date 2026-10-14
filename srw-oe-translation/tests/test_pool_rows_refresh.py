#!/usr/bin/env python3
"""Tests for tools/pool_rows_refresh.py - the pool strings an older package never saw."""
from __future__ import annotations

import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "tools"))

import item_skill_records as ISR  # noqa: E402
import pool_rows_refresh as PRR   # noqa: E402

DAMAGE = b"\x0f*\xd2\xb0\x0f&"          # ﾀﾞﾒｰｼﾞ with the game's kana tokens


def record(kind, rid, name, effect):
    header = bytearray(ISR.STRING_BASE)
    struct.pack_into("<4H", header, 0, rid, rid, rid, 0)
    fields = [name.encode("cp932"), b"", effect.encode("cp932"), b"", b""]
    body, bounds, pos = b"", [], ISR.STRING_BASE
    for raw in fields:
        bounds.append(pos)
        body += raw + b"\x00"
        pos += len(raw) + 1
    bounds.append(pos)
    struct.pack_into("<6H", header, ISR.BOUNDARY_TABLE, *bounds)
    raw = bytes(header) + body
    return raw + b"\x00" * ((-len(raw)) % 4)


def member_b(pool):
    recs = [record("skill", 1, "対地", "効果")]
    table = 8 + 4 * len(recs)
    tail = table + sum(len(r) for r in recs)
    return (struct.pack("<2I", tail, len(recs)) + struct.pack("<I", table)
            + b"".join(recs) + ISR.build_tail_pool(tail, pool))


def member_c(pool):
    return struct.pack("<2I", 8, 0) + ISR.build_tail_pool(8, pool)


class StubContainers:
    def __init__(self, members):
        self.members = members

    def member(self, container, member):
        try:
            return self.members[(container, member)]
        except KeyError:
            raise PRR.TM.MapError(f"member not found: {container}/{member}")


class RefreshTest(unittest.TestCase):
    def setUp(self):
        pool = ["気力".encode("cp932"), DAMAGE + b"-", b"CT" + DAMAGE + b"+"]
        self.members = {("config00.cpk", "srwDL_Skill00.bin"): member_b(pool),
                        ("config01.EDAT", "srwDL_Skill01.bin"): member_c(pool)}
        self.original = PRR.TM.Containers
        PRR.TM.Containers = lambda dirs: StubContainers(self.members)

    def tearDown(self):
        PRR.TM.Containers = self.original

    def package(self, tmp):
        rows = [  # the older export: one shared pool-start id, the tokenised strings missing
            {"id": "skill:config00.cpk/srwDL_Skill00.bin:84", "category": "config_skill",
             "part": "text", "jp": "気力", "en": "Will", "mode": "grow", "max_bytes": None,
             "source": {"container": "config00.cpk", "member": "srwDL_Skill00.bin", "offset": 84}},
            {"id": "skill:config01.EDAT/srwDL_Skill01.bin:20", "category": "config_skill",
             "part": "text", "jp": "気力", "en": "Will", "mode": "grow", "max_bytes": None,
             "source": {"container": "config01.EDAT", "member": "srwDL_Skill01.bin", "offset": 20}},
        ]
        package = Path(tmp)
        (package / PRR.CONFIG_FILE).write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
        return package

    def test_check_reports_without_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.package(tmp)
            before = (package / PRR.CONFIG_FILE).read_text(encoding="utf-8")
            report = PRR.refresh(package, [], apply=False)
            self.assertEqual((report["added"], report["copies"], report["distinct_new_texts"]), (4, 2, 2))
            self.assertEqual(report["members"]["config00.cpk/srwDL_Skill00.bin"], {"pool": 3, "new": 2})
            self.assertEqual((package / PRR.CONFIG_FILE).read_text(encoding="utf-8"), before)

    def test_apply_appends_grow_rows_with_exact_offsets_and_copy_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.package(tmp)
            PRR.refresh(package, [], apply=True)
            rows = PRR.load_rows(package / PRR.CONFIG_FILE)
        self.assertEqual(len(rows), 6)
        self.assertEqual([r["en"] for r in rows[:2]], ["Will", "Will"])     # untouched
        new = rows[2:]
        blob = self.members[("config00.cpk", "srwDL_Skill00.bin")]
        tail = struct.unpack_from("<I", blob, 0)[0]
        pointers, _ = ISR.parse_tail_pool(blob, tail)
        self.assertEqual([(r["jp"], r["source"]["offset"]) for r in new[:2]],
                         [("%s*ﾒｰ%s&-", pointers[1]), ("CT%s*ﾒｰ%s&+", pointers[2])])
        self.assertTrue(all(r["mode"] == "grow" and r["max_bytes"] is None and r["en"] == ""
                            for r in new))
        self.assertEqual([r.get("copy_of") for r in new],
                         [None, None, new[0]["id"], new[1]["id"]])
        self.assertEqual(new[2]["source"]["container"], "config01.EDAT")

    def test_stale_rows_are_reported_and_pruned_only_on_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            package = self.package(tmp)
            tail = struct.unpack_from("<I", self.members[("config00.cpk", "srwDL_Skill00.bin")], 0)[0]
            junk = {"id": f"skill:config00.cpk/srwDL_Skill00.bin:{tail}", "category": "config_skill",
                    "part": "text", "jp": "痺", "en": "痺", "mode": "grow", "max_bytes": None,
                    "source": {"container": "config00.cpk", "member": "srwDL_Skill00.bin", "offset": tail}}
            with (package / PRR.CONFIG_FILE).open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(junk, ensure_ascii=False) + "\n")
            report = PRR.refresh(package, [], apply=True)
            self.assertEqual(report["stale"], {"config00.cpk/srwDL_Skill00.bin": ["痺"]})
            self.assertEqual(report["pruned"], 0)
            self.assertIn("痺", [r["jp"] for r in PRR.load_rows(package / PRR.CONFIG_FILE)])
            report = PRR.refresh(package, [], apply=True, prune_stale=True)
            self.assertEqual((report["pruned"], report["added"]), (1, 0))
            rows = PRR.load_rows(package / PRR.CONFIG_FILE)
            self.assertNotIn("痺", [r["jp"] for r in rows])
            self.assertEqual(len(rows), 6)

    def test_a_missing_container_is_reported_not_fatal(self):
        del self.members[("config01.EDAT", "srwDL_Skill01.bin")]
        with tempfile.TemporaryDirectory() as tmp:
            report = PRR.refresh(self.package(tmp), [], apply=False)
        self.assertEqual(report["added"], 2)
        self.assertEqual(len(report["unreadable"]), 1)


if __name__ == "__main__":
    unittest.main()
