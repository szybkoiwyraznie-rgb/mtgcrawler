# S3 closed — the bundle cipher is recovered (2026-10-27)

*Confirmed by data: 276 of 276 known pairs decrypt byte for byte. The key was not
guessed and did not come from the running game: it came out of
`global-metadata.dat` plus the 276 pairs that were already here.*

## What the files are protected with

```
password = "ComBBStudioSRTeam"                    # one constant, same for every bundle
salt     = the bundle's own file name minus ".bundle"   (Path.GetFileName, UTF-8)
key      = new PasswordDeriveBytes(password, salt).GetBytes(16)   # PBKDF1-SHA1, 100 rounds
aes      = AesManaged { KeySize = 128, Mode = ECB, Padding = None, IV = zeros }
keystream[16n .. 16n+16) = AES_ECB(key, LE32(n) || 0^12)          for n = 1, 2, 3, ...
plain    = cipher XOR keystream          (whole file from offset 0, same length, no padding)
```

That is the published `SeekableAesStream`, and the game's own copy of it is in
`Assembly-CSharp`: `SeekableAesStream` with 14 methods, `.ctor` at RVA `0x429cf0`,
`Cipher` at RVA `0x429840`. The stream is constructed in
`CustomAssetBundleResource::LoadLocalBundle` (RVA `0xbce440`), where the call

```
SeekableAesStream..ctor(fileStream, password, Encoding.UTF8.GetBytes(filePath))
```

takes the password from one fixed slot and the salt from the file name.

## How it was found

1. **The construction was known, the password was not.** Nine earlier sweeps
   (716,558 direct key candidates, 12,500 PBKDF2 derivations, 428,538 printable
   literals against 10 salt forms and 3 derivations, and a 16.1-million-check
   key/layout matrix) all failed. Negative results that broad mean the *assumption*,
   not the candidate list, has to be wrong — and the one assumption never tested was
   that the password is a printable run inside the binary.
2. **The literal table is not a string dump.** `global-metadata.dat` carries 13,428
   `Il2CppStringLiteral` records whose lengths and boundaries are explicit. Sweeping
   those instead of printable runs found `ComBBStudioSRTeam` on the first pair
   (`stem` salt, 100 iterations) in 73 seconds —
   `tools/srw_y_seekable.py` with the literal list from the table.
3. **The code confirms it.** Once `tools/il2cpp_modules.py` could turn a method into
   an address (81 `Il2CppCodeGenModule` records, 147,184 methods total;
   `Assembly-CSharp` 37,353), `CustomAssetBundleResource::LoadLocalBundle` shows the
   password slot and the `Encoding.UTF8.GetBytes(...)` salt construction, and
   `SeekableAesStream::.ctor` shows `KeySize = 0x80`, ECB, `PaddingMode.None`.

## Verification

`tools/srw_y_bundle_crypt.py verify --pairs local/pairs --plain local/owner_carve4`

```
pairs checked        : 276
32-byte oracle       : 276/276
carved head matches  : 276/276
```

276 independent files, each with its own salt. The carve only ever held the first
32 KiB of a bundle and zero-filled the rest (`CARVE_LIMIT`), which is why the first
full-length comparison looked like a failure at offset 32,768 — it was the carve
that ended, not the cipher.

## What this changes

- **No more memory runs, ever.** Any bundle can be decrypted and re-encrypted on
  disk, offline, with no game running. The owner's requirement — "Musisz odkodować
  te pliki, zamienić je na polski, zakodować" — is now the actual pipeline.
- The 276-pair keystream trick (`keystream_patch.py`) stays as a cross-check, but it
  is no longer the mechanism: the text tables and scenario scripts were never in the
  pair set, and they can now be opened directly.
- Re-encryption is exact: same length, same salt, same key, so a patched bundle
  needs no size budget beyond the original file's own length.

## Next

`docs/OWNER_STEPS_S4_TEXT.md` asks for the four bundles that hold the opening:
`dialog_text_en-US` (948,652 B), `dialog_text_ja-JP` (940,012 B) and the two
scenario bundles (`1c12bbab…` 5,591,151 B en, `8939a711…` 4,740,401 B jp). With
those on hand the opening narration is extracted from the Japanese original,
translated, re-encrypted and shipped as one or two files to swap.

## Labels

- **confirmed:** the password, the salt rule, the keystream layout, the 276/276
  verification, the class name/addresses in `Assembly-CSharp`.
- **confirmed by code, not yet by a patched file in the game:** that a re-encrypted
  bundle loads. It cannot be tested here; the first owner install answers it.
- **unknown:** whether the opening narration sits in the text table or in the
  scenario script — the four bundles in the S4 sheet settle it.
