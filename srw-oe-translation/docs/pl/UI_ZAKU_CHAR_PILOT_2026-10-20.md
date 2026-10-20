# Enemy Robots: Zaku II (Char) pilot footer (2026-10-20)

The follow-up screenshot shows a different Japanese footer from the weapon-type captions: `パイロット：シャア`, meaning **Pilot: Char**. The type-caption audit did not cover this field.

The exact Char footer occurs in two source dictionaries: global `config00.cpk` (Zaku II) and `config01.EDAT` (another Char entry), each mirrored by the corresponding `imenu` dictionary. All four exact source bindings are now added to PL as `Pilot: Char`, within the measured 19-byte slots. The additions are listed in `config/pl/ui-zaku-char-pilot-footer-2026-10-20.json` and retained as explicit IDs for the PL handoff. Generic leftovers remain quarantined; other pilot-name leftovers are not included in this screenshot-specific correction.

The normal PL materializer reports zero hard errors, and focused tests verify the source bindings and RoboDictionary table-writer route. **No physical ISO/DLC rebuild or in-game confirmation was possible here.** To see the change, rebuild the installed data using the updated PL snapshot; this is not a save-data or DLC-only toggle.
