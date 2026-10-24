# Our tools

Project-owned wrappers, adapters and the owner patch-kit builder land here
as they are built. The pinned upstream retro-trans tools live in
[`../vendor/retro-trans/tools/`](../vendor/retro-trans/tools/) and are not
edited in place (see `../vendor/retro-trans/PROVENANCE.md`).

Planned first entries (phase 1, see `../docs/STATUS.md`):

- a sparse-virtual-image builder that mounts the extracted
  `DATA/stage.bin` at LBA 1651029 × 2048 so the unmodified vendored
  `extract_script.py` / `apply_script.py` / `verify_pointers.py` can run in
  the sandbox without the owner's ISO;
- the owner-side `PATCH.bat` kit builder (runs the same apply step against
  the owner's real ISO, writes a new image, keeps logs/hashes).
