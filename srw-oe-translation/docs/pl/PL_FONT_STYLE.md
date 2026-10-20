# PL font styling v5 — native ASCII bodies (2026-10-18)

## V5 runtime feedback — accepted (2026-10-18)

The owner supplied two **v5** runtime screenshots (opening narration and dialogue)
and reports that the font otherwise looks excellent, with no further objections.
Missing Ł/Ś in the all-caps headings are **source-text mistakes**, not dropped font
marks: the exact delivered ZIP contains `PROBA CZYTELNOSCI` and
`MALE I WIELKIE LITERY`. It also omits Ó in PROBA. Corrected source captions now
read `PRÓBA CZYTELNOŚCI` and `MAŁE I WIELKIE LITERY`; regression pins both.
No glyph, codec, body, spacing or accent recipe is changed. The existing Drive ZIP
remains immutable and still contains the old captions; no new build/test is needed
to establish the diagnosis. Do not ask the owner for another font-test cycle.
Acceptance is for the demonstrated screens, not all future translated layouts.
The screenshots remain private, outside Git.

## Owner feedback and evidence

Four owner screenshots confirm TEST_PL v4 prose renders in the opening narration,
scene title and dialogue, plus the `Zażółć` unit-name header. Owner reports Polish
letters look bolder/full and lowercase bodies sit 1–2 pixels lower. This is visual
feedback, not a measured engine advance or proof of every game screen.
Screenshots stay out of Git.

Bitmap measurements corroborate a style mismatch: v4 uses Roboto Medium with peak
coverage 15/15, while original ASCII peaks at 9/15 (lowercase `l` 6/15). Native
`c/e/n/o/s` bodies have meaningful pixels from row 4; the old counterparts' bodies
start at row 5. The exact difference varies by letter (`a` has its strong pixels
from row 5 natively too); do not claim every letter is 2 pixels too low.

## Correction

`tools/pl_glyph_compose.py` builds all 18 letters from original ASCII cells in the
user's `font.cpk` at patch time:

- ą/ć/ę/ł/ń/ó/ś/ź/ż use a/c/e/l/n/o/s/z/z; uppercase likewise;
- original bodies remain at their original position and coverage: no scaling,
  recentering, shifting, boldening or replacement typeface;
- only 2–6 sparse accent-mask pixels are permitted, with peak/edge values derived
  from the source cell, not full-opacity Roboto;
- ogoneks use the two free rows below the native row-11 baseline; acute/dot use
  headroom; ł/Ł add a small diagonal crossing the native stem;
- unsupported/blank source cells or insufficient accent room fail closed;
- the one-byte mapping and low-nibble-first packing from v3 remain unchanged.

**No original bitmap or native-derived glyph JSON is committed or shipped.** The
kit ships composition code only; the owner's own font supplies the base cells.
The old Roboto JSON/generator remains historical and is not used by v5.

The verifier reads the actual output ISO and independently checks physical cells,
exact source-body preservation outside mark masks, native peak coverage and
unchanged ASCII. Tests deliberately introduce boldening, a vertical shift, missing
accents and original-ASCII corruption and require failures.

## Initial checkpoint

11 native-style tests and 19 extracted-kit/panel tests pass, including the private
original containers in a synthetic ISO fixture. Local nearest-neighbour previews
were inspected; they are derived game art, remain ignored and are not an emulator
screenshot. At this initial checkpoint, V5 runtime appearance still needed confirmation. Natural test prose
from v4 is unchanged, apart from version labels.

## Delivery

[TEST_PL v5](https://drive.google.com/file/d/13tWWoHO6nBSmEVGFj4y46BtDIV2kz3uD/view)
is delivered; [manifest and numeric metrics](test-v5-delivery.json). Final suite:
1569 unittest tests OK (25 skipped), including corruption/missing-mark mutations.
The actual delivered ZIP was extracted and run with isolated Python on a fixture
ISO containing real original font/event/config containers. All 18 native-body
and coverage audits pass; unselected font/ASCII/event/config members are unchanged.
At delivery runtime aesthetics were unconfirmed; the subsequent v5 result is recorded above.
