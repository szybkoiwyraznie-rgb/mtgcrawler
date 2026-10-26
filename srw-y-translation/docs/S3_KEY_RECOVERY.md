# S3 — getting the key, so bundles can be patched like OE

*2026-10-26. Direction set by the owner: the deliverable is **patched game files**,
not text harvested from a running game. Harvesting stays a diagnostic; this
document is the path that ends with a modified `.bundle` on disk.*

## 1. What a patch needs, and why the format allows it

The OE kit works because the replacement text is written into files the game
already reads. For SRW Y the same is possible only if the encrypted bundles can be
turned into plaintext and back **without changing their size**. Three measurements
say they can [confirmed]:

| measurement | result |
|---|---|
| carved plaintext bundle size vs on-disk size | 362 of 362 distinct sizes match a disk size exactly (delta-0 is the only peak; 25,735 disk bundles, 22,893 distinct sizes) |
| sample `1cc7e02ee5711c6ba87a0e364f62198c.bundle` | 940,012 B, so 940,012 mod 16 = **12** — not a whole number of AES blocks |
| repeated 16-byte blocks in that sample | **0** in the first 64 KiB (ECB would repeat them) |

No padding, no extra header, no block alignment. So the cipher is a keystream
(CTR/CFB/OFB-style) and **a same-length Polish line can be written in place**.
A longer line is also fine as long as the enclosing asset keeps its size; that is
the S4 budget question, not a format question.

*Correction to an earlier note:* the 940,012 B sample has **no** plaintext twin in
the carved set — the largest carved bundle is 275,626 B. The known-plaintext route
does not need one, see §3.

## 2. Why the key is not in any file [confirmed]

- `GameAssembly.dll` (74,865,152 B) contains **no** `SeekableAesStream`,
  `Rfc2898`, `PasswordDeriveBytes`, `AesManaged`, `Rijndael`, `Encryption` or
  `UnityFS` literal. IL2CPP compiles method and field names away; the names known
  so far come from `global-metadata.dat`, which carries the metadata strings but
  not the values.
- The static sweeps are exhausted: 2,249,429 literal windows, 3,836,487 derived
  keys, 61,201,575 aligned windows, 4,712 PBKDF2 combinations — all negative.

The password and salt are therefore not reachable as literals. The key does exist
at runtime, though: the game decrypts every bundle it uses, and 594 plaintext
bundles were carved out of its memory, which proves the plaintext passes through.

## 3. The trick: one AES decryption per candidate key

Every bundle in this build starts with the same 30 bytes (one distinct prefix
across 200 carved samples):

    UnityFS\x00 | 00 00 00 08 | 5.x.x\x00 | 2022.3.44f1\x00

So the first ciphertext block `C0` and the known plaintext block `P0` give the
analyst something for free:

- **stream construction** (CTR/CFB/OFB): `keystream0 = C0 xor P0`, and
  `AES-decrypt(key, keystream0)` is the counter/feedback block — a real 16-byte
  array living in the process;
- **CBC**: `C0 = E(P0 xor IV)`, so `AES-decrypt(key, C0) = P0 xor IV`; precompute
  `P0 xor IV` for every IV candidate and the test stays a single dictionary lookup.

Either way it is **one AES operation per candidate key**, and the result is
accepted only when it matches a structured value (an all-zero block, or one of the
16-byte arrays found in the same heap). No brute force over the address space, no
plaintext/ciphertext pair needed. A few thousand candidates cost milliseconds.

That is what `tools/key_from_memory.py` does: read-only
(`PROCESS_QUERY_INFORMATION | PROCESS_VM_READ`), finds managed `byte[]` payloads of
16/24/32 bytes in both IL2CPP layouts, and reports every key that satisfies the
test together with the counter block. Throughput of the scanner is **656 MB/s**
(anchored on the little-endian length field: walking the heap's zero runs instead
took minutes per megabyte).

## 4. Putting a file back: `tools/bundle_crypt.py`

The construction is **not guessed**. `identify` tries `ctr-le`, `ctr-be`,
`cfb128`, `ofb`, `cbc` in order and accepts the first one whose decryption starts
with a `UnityFS` header *and* whose declared size equals the file size. Result on a
real carved bundle (18,708 B and 275,626 B, 12 bytes past a block boundary — same
shape as the on-disk files): **each stream mode round-trips exactly, and is
identified as itself.** CBC is only tried when the length divides by 16, because
this build's files do not.

`encrypt` is the exact inverse of `decrypt`, so the workflow is:

    bundle (encrypted) -> decrypt -> UnityPy -> replace text -> encrypt -> same file

No padding is added or removed, and the byte length is preserved.

## 5. One file for the owner

`tools/srw_y_key.py` is the same two jobs in a single self-contained script
(`selftest`, `key`, `decrypt`, `encrypt`), because the two-file download failed at
step 0 on the owner's machine: Windows PowerShell 5.1 negotiates TLS 1.0/1.1 and
`raw.githubusercontent.com` requires TLS 1.2. The owner sheet now sets
`[Net.SecurityProtocolType]::Tls12` and falls back to `curl.exe`. Uploading the
script to Drive instead was refused by the connector provider's security filter,
so GitHub stays the delivery path.

The sheet also stopped showing file names as `name.py` tokens: the owner's client
auto-links `memory.py` / `crypt.py` (`.py` is Paraguay's TLD) and the pasted command
then contained a markdown link instead of a file name. Names are built from parts
(`[char]46`), commands locate the script with `Get-ChildItem *key*`, and the sheet
is checked to contain no `.py` token and no literal URL.

## 6. What is proven here and what is not

Proven in the sandbox: known-prefix keystream, the CBC target-set test, the array
scanner (finds planted keys in heap-like noise, 2,048/2,048), the end-to-end run
against a fake kernel with a fake process (`OpenProcess` → `VirtualQueryEx` →
`ReadProcessMemory` → key found → file verified), and mode identification plus
byte-exact round-trip on real bundles. Suite: **148 tests**, green.

Not proven, because it needs the owner's machine: that the key sits in the heap in
one of the two layouts at the moment of the scan, and which construction the game
actually uses. Both are answered by the same one-minute run, and the run says so
plainly instead of guessing — `key_report.json` records the scanned volume, the
candidate counts and every hit, and `bundle_crypt.py` refuses to claim success
until a real bundle opens.

## 7. After the key

1. Decrypt one bundle, open it with UnityPy, confirm the text layer is readable
   (the Addressables catalogue already points at
   `Assets/Datas/Scenario/{jp,en}/…lua.txt` and the Localization tables).
2. Build the patch pipeline: extract → translate in-place with a length budget →
   re-encrypt. Same shape as the OE kit, so the delivery stays "replace these
   files", not "run a tool while the game is open".
3. Only then the S4 length budget, S5 install/reversal, S6 go/no-go.
