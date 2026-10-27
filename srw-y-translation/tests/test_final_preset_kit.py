"""The fourth, targeted kit: test everything without the owner's game files.

The PowerShell collector decrypts the first 512 bytes of every bundle and looks
for three literal CAB names. These tests verify the three targets come from the
committed evidence, that the cipher port (PBKDF1-SHA1 x100 -> AES-128-ECB
counter keystream) is exactly the recovered cipher, that the built-in
known-answer self-test vector is correct, and that the kit is byte-reproducible.
"""
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import tempfile
import unittest
import zipfile

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / 'tools'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_final_preset_request as kit  # noqa: E402
import srw_y_bundle_crypt as C  # noqa: E402
from test_ps_kits import strip_strings  # noqa: E402


def ps_cipher_decrypt(name: str, data: bytes) -> bytes:
    """Python mirror of Get-Stream/Decrypt-Head in the PowerShell collector."""
    from Crypto.Cipher import AES
    key = C.key_for(name)
    blocks = (len(data) + 15) // 16
    nonces = b''.join(struct.pack('<i', i) + b'\x00' * 12 for i in range(1, blocks + 1))
    stream = AES.new(key, AES.MODE_ECB).encrypt(nonces)[:len(data)]
    return bytes(a ^ b for a, b in zip(data, stream))


class TargetTests(unittest.TestCase):
    def setUp(self):
        self.plan = kit.survey()
        self.text = kit.ps_block(self.plan)

    def test_three_targets_come_from_committed_evidence(self):
        evidence = json.loads(kit.EVIDENCE.read_text(encoding='utf-8'))
        self.assertEqual(self.plan['cabs'],
                         [row['cab'] for row in evidence['pptr']['remaining']])
        self.assertEqual(len(self.plan['cabs']), 3)
        self.assertTrue(all(re.fullmatch(r'CAB-[0-9a-f]{32}', cab)
                            for cab in self.plan['cabs']))
        self.assertEqual(self.plan['evidence_sha256'],
                         hashlib.sha256(kit.EVIDENCE.read_bytes()).hexdigest())

    def test_ps_text_is_ascii_and_contains_exactly_three_needles(self):
        self.text.encode('ascii')
        self.assertEqual(self.text.count("'CAB-"), 3)
        for cab in self.plan['cabs']:
            self.assertIn(cab, self.text)
        self.assertIn('samotest szyfru: OK', self.text)
        self.assertIn('Get-ChildItem -Path $sa -Filter', self.text)
        self.assertIn('Compress-Archive', self.text)

    def test_ps_syntax_is_ps51_safe(self):
        self.assertEqual(re.findall(r',\s*\n\s*\)', self.text), [])
        code = strip_strings(self.text)
        self.assertEqual(code.count('{'), code.count('}'))
        self.assertEqual(code.count('('), code.count(')'))

    def test_committed_ps1_matches_the_generator(self):
        raw = kit.PS1.read_bytes()
        self.assertTrue(raw.startswith(b'\xef\xbb\xbf'))
        self.assertEqual(raw.count(b'\n'), raw.count(b'\r\n'))
        raw[3:].decode('ascii')
        self.assertEqual(raw, b'\xef\xbb\xbf' + self.text.replace('\n', '\r\n').encode('ascii'))


class CipherTests(unittest.TestCase):
    def test_ps_algorithm_matches_the_recovered_cipher(self):
        plain = (b'UnityFS\x00\x00\x00\x00\x085.x.x\x002022.3.44f1\x00'
                 + b'CAB-0123456789abcdef0123456789abcdef' + b'\x00' * 200)
        cipher = C.encrypt('0123456789abcdef0123456789abcdef.bundle', plain)
        self.assertEqual(
            ps_cipher_decrypt('0123456789abcdef0123456789abcdef.bundle', cipher[:512]),
            plain[:512])

    def test_selftest_vector_decrypts_to_unityfs(self):
        plan = kit.survey()
        cipher = bytes(plan['selftest_cipher'])
        self.assertEqual(len(cipher), 16)
        self.assertEqual(C.encrypt(plan['selftest_name'], b'UnityFS\x00' + b'\x00' * 8),
                         cipher)
        self.assertEqual(ps_cipher_decrypt(plan['selftest_name'], cipher),
                         b'UnityFS\x00' + b'\x00' * 8)
        for byte in cipher:
            self.assertIn(f'0x{byte:02x}', kit.ps_block(plan))

    def test_key_derivation_is_pbkdf1_sha1_x100(self):
        # The PowerShell Get-Key takes the first 16 bytes of the 100th SHA-1.
        digest = hashlib.sha1(b'ComBBStudioSRTeam' + b'srw_y_selftest').digest()
        for _ in range(99):
            digest = hashlib.sha1(digest).digest()
        self.assertEqual(C.key_for('srw_y_selftest.bundle'), digest[:16])


class KitTests(unittest.TestCase):
    def test_kit_zip_is_deterministic_and_has_three_known_members(self):
        plan = kit.survey()
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / 'a', Path(tmp) / 'b'
            first = kit.write_kit(plan, a)
            second = kit.write_kit(plan, b)
            one = Path(first['zip']).read_bytes()
            self.assertEqual(one, Path(second['zip']).read_bytes())
            with zipfile.ZipFile(first['zip']) as z:
                self.assertEqual(set(z.namelist()),
                                 {'URUCHOM_TO.bat', 'CZYTAJ_TO.txt', kit.PS_NAME})
                self.assertEqual(z.read(kit.PS_NAME), kit.PS1.read_bytes())
                z.read('URUCHOM_TO.bat').decode('ascii')
                readme = z.read('CZYTAJ_TO.txt').decode('utf-8-sig')
                for cab in plan['cabs']:
                    self.assertIn(cab, readme)
                self.assertIn(kit.STEM + '.zip', readme)
                self.assertEqual({i.date_time for i in z.infolist()},
                                 {(2026, 10, 26, 12, 0, 0)})

    def test_main_generates_every_output_without_private_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code = kit.main(['--out-dir', str(root / 'kit'),
                             '--json', str(root / 'plan.json'),
                             '--doc', str(root / 'PROSBA.md'),
                             '--ps1', str(root / 'collector.ps1')])
            self.assertEqual(code, 0)
            self.assertTrue((root / 'kit' / (kit.STEM + '_PROSBA.zip')).is_file())
            self.assertEqual((root / 'collector.ps1').read_bytes(), kit.PS1.read_bytes())
            doc = (root / 'PROSBA.md').read_text(encoding='utf-8')
            for cab in kit.survey()['cabs']:
                self.assertIn(cab, doc)
            self.assertIn('88 z 91', doc)
            plan = json.loads((root / 'plan.json').read_text(encoding='utf-8'))
            self.assertEqual(len(plan['cabs']), 3)

    def test_committed_doc_exists_and_names_the_result_zip(self):
        doc = kit.DOC.read_text(encoding='utf-8')
        self.assertIn(kit.STEM + '_PROSBA.zip', doc)
        self.assertIn('SRW_Y_PRESETY3.zip', doc)
        self.assertIn('SeekableAesStream', doc)


if __name__ == '__main__':
    unittest.main()
