#!/usr/bin/env python3
"""Build the test-patch spec for the whole first scene (narration + dialogue).

The spec is what the repository can carry: byte offsets, the hashes of the file they were measured
on, and our English lines.  The Japanese is never written down here -- ``iso_test_patch.py`` reads
it back out of the user's own ISO to check that each offset still holds what it did.

Run it after changing a translation:
    python3 tools/build_test_spec.py           # rewrites test-patches/eventP00-scena1.json
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cpk_write  # noqa: E402
import event_text_apply as ETA  # noqa: E402
import iso_pack  # noqa: E402
import slot_text_apply  # noqa: E402
import speaker_map as SM  # noqa: E402

HERE = Path(__file__).resolve().parent.parent
SPEC = HERE / "test-patches" / "eventP00-scena1.json"
CONTAINER = "PSP_GAME/USRDIR/eventP00.cpk"
MEMBER = "DL100_01.bin"

#: (offset, kind, English).  The Japanese stand next to each line in tools/build_test_spec.ja.txt,
#: which is deliberately not committed: it is game text.  ``\r\n`` at the end is kept from the
#: original line, where the game clears the box with it.
LINES = [
    # --- narration: the history that opens the game (0x1B7 records) -------------------------
    (180, "narration",
     "Decades have passed since the Earth Federation,\na unified government of all mankind, was founded.\n"
     "Human science, technology and economy gathered pace,\ngiant space colonies rose around the Earth,\n"
     "and the Universal Century began."),
    (348, "narration",
     "In time humanity spread across the solar system\nand grew mighty on vast resources and energy.\n"
     "But as human activity raced ahead, prosperity\nmagnified the scale of every problem as well."),
    (524, "narration",
     "An expanding economy bred inequality and drew\nvast money, resources and people into criminal\n"
     "hands. Terrorist and pirate groups grew bolder,\nand men like Dr. Hell appeared, openly declaring\n"
     "world conquest and defying all of humanity.\n\n"
     "But the Earth Federation Forces could not keep up.\nOld national governments and the colonies were\n"
     "forced to arm themselves for their own defence.\n"
     "That arms race, of course, only raised tension\nbetween nations and between peoples, and it took\n"
     "little time for the ideal of a unified government\nto be lost."),
    (988, "narration",
     "Ironically, war accelerated science even further,\ngiving birth to one runaway technology after\n"
     "another -- the Devil Gundam incident being the\nmost notorious.\n\n"
     "In the same way, research into unknown energies\naltered the energy balance of the Earth itself,\n"
     "and became the very thing that invites invasion\nby races that are not human."),
    (1244, "narration",
     "The Invaders, the Muge Empire, the evil god\nDragon, the Machine Empire, the Jark Empire,\n"
     "the Great Demon World -- threats beyond human\ncomprehension struck the Earth Sphere one after\n"
     "another, and the memory is still fresh."),
    (1388, "narration",
     "But humanity has overcome crisis after crisis,\nrebuilding and pressing on, again and again.\n\n"
     "Even with the fear of a threat that may come at\nany moment, people live each day with strength."),

    # --- scene 1: the prologue --------------------------------------------------------------
    (1844, "dialogue", "(I am now at Connect, a civilian\norganization promoting space trade...)"),
    (1976, "dialogue", "(Connect is famous, but its origins\nand true purpose are unknown...)"),
    (2128, "dialogue",
     "(People of Earth have faced so many\ndisasters that one company's doings\nare not worth their attention.)"),
    (2312, "dialogue", "(But that is fine. If I reach my goal\nwithout anyone knowing,\nso much the better...)"),
    (2532, "dialogue", "Now then, it is time for training."),
    (2820, "dialogue", "Ah, ah, testing, testing."),
    (2872, "dialogue", "＜主人公名＞, can you hear me?"),
    (2928, "dialogue", "Read you loud and clear!\nLet us begin the mission."),
    (2988, "dialogue", "Catapult connected!\nExert, please launch!"),
    (3060, "dialogue", "Understood!"),
    (3088, "dialogue", "CF-00 Exert, launching!"),
    (3336, "dialogue",
     "Today you will test combat manoeuvres\nusing the new mobility control system."),
    (3424, "dialogue", "First, please 'Move' to the designated area."),
    (3488, "dialogue", "Roger! Moving to the target!"),
    (3540, "dialogue", "Displaying the designated area."),
    (3760, "dialogue", "Target confirmed!\nBeginning 'Move' now."),
    (6048, "dialogue", "EN resupply complete!\r\n"),
    (6100, "dialogue", "Next, we will recover 'Parts'.\r\n"),
    (6160, "dialogue", "Deploying container blocks.\r\n"),
    (6372, "dialogue",
     "\"At the same coordinates as a 'Container',\n the unit identifies and recovers 'Parts'\n on its own.\"\r\n"),
    (6476, "dialogue", "Roger!\nAfter moving to the 'Container' coordinates,\nI will recover the 'Parts'.\r\n"),
    (6804, "dialogue", "Parts recovery complete!"),
    (6868, "dialogue",
     "This is a repair kit that patches up damage\nin the field. Good to have one aboard."),
    (7012, "dialogue", "Now we move on to combat manoeuvres."),
    (7072, "dialogue", "Displaying a simulated enemy."),
    (7204, "dialogue", "Enemy unit confirmed!"),
    (7240, "dialogue", "Well now... this one does not look\nlike a simulation."),
    (7308, "dialogue", "The system was upgraded the other day."),
    (7376, "dialogue",
     "Impact from hits is fed back into the unit,\nso combat feels far more real, they say."),
    (7484, "dialogue", "That I have to see."),
    (7528, "dialogue", "Beginning 'Attack'!"),
    (9048, "dialogue",
     "Halt!\nThe Exert hangar is off limits to outsiders.\nHow did you get in?"),
    (9180, "dialogue",
     "Oh, I am sorry!\nI have been transferred here from the 44th\nGeneral Affairs Department."),
    (9256, "dialogue",
     "This is only my first year with the company,\nbut I look forward to working with you!"),
    (9332, "dialogue", "So you are...?\nThe new member of the Connect Force, then."),
    (9408, "dialogue",
     "Yes! My name is Himari Yaegaki.\nI am from Japan on Earth. I studied\nengineering."),
    (9512, "dialogue", "I see. Nice to meet y--"),
    (9556, "dialogue",
     "People say I do not look the science type,\nbut I skipped grades and finished my master's."),
    (9656, "dialogue", "I see. That is impress--"),
    (9696, "dialogue",
     "My favourites are yakiniku, ramen and\ndessert buffets. And with dessert...\na caramel macchiato, no question!"),
    (9828, "dialogue",
     "Oh, there was pilot and operator training\nlast week, and, well... I cannot even drive,\nso will I really be all right...?"),
    (9964, "dialogue", "Er... hold on a moment..."),
    (10016, "dialogue",
     "I can push myself through most things,\nbut the cold is one thing I am bad with..."),
    (10112, "dialogue", "Oh, but I do love a good bath! And also..."),
    (10176, "dialogue", "T-that is quite enough!"),
    (10216, "dialogue", "Ah... I am sorry!"),
    (10268, "dialogue", "I talked far too much, did I not..."),
    (10320, "dialogue",
     "We are the Connect Force, a combat unit.\nLong chats on duty get people killed.\nSave them for later."),
    (10432, "dialogue", "Understood... I will be careful."),
    (10484, "dialogue", "Good."),
    (10532, "dialogue", "Um, may I ask you one question?"),
    (10588, "dialogue", "You said combat unit just now,\nbut what do we actually do?"),
    (10676, "dialogue", "Nobody told me anything when I\nwas transferred..."),
    (10736, "dialogue", "Just what it says. We are expected to fight."),
    (10788, "dialogue",
     "The robot in front of you is no work machine.\nIt is the newest weapon, made for any mission."),
    (10892, "dialogue", "A weapon...?"),
    (10936, "dialogue", "What?! Why would a private\ncompany like Connect...?"),
    (11000, "dialogue", "Everyone assigned here is\nsurprised at first..."),
    (11064, "dialogue",
     "But once you know the purpose, you will see\nthis is the most rewarding work here."),
    (11168, "dialogue", "Is that so."),
    (11208, "dialogue",
     "Still, hearing you say it so firmly, senior,\nmakes me want to work harder!"),
    (11292, "dialogue",
     "You have what it takes. You were chosen\nfrom hundreds of thousands of candidates."),
    (11376, "dialogue", "So I am one of the chosen?!"),
    (11436, "dialogue", "Well... I would not go that far."),
    (11480, "dialogue",
     "For now this is combat training, but you\nnever know when something might happen."),
    (11564, "dialogue", "Make every day count, and always\ndo your best!"),
    (11648, "dialogue", "Yes! I will do my best!"),
    (11800, "dialogue",
     "(I did not expect a fresh graduate.\n I thought we would get an old hand...)"),
    (11912, "dialogue", "(Surely this project is not\n short of people...)"),
    (12016, "dialogue", "Welcome back, senior!"),
    (12060, "dialogue", "Good work, Himari."),
    (12104, "dialogue",
     "Send the data on to Headquarters for analysis.\nDo you know how?"),
    (12188, "dialogue", "The data... er... how do I...?"),
    (12244, "dialogue", "You have not been taught this?"),
    (12296, "dialogue", "Sorry, I have not studied enough..."),
    (12344, "dialogue",
     "It seems I have a lot to teach you yet.\nLet me walk you through the steps."),
    (12420, "dialogue", "Sorry.\nI am keeping you late because of this."),
    (12488, "dialogue", "Do not worry about that."),
    (12532, "dialogue",
     "This job really can cost you your life.\nKeep that in mind, all right?"),
    (12628, "dialogue", "Yes!"),
    (12712, "dialogue",
     "(Himari's assignment was the organisation's\n choice. She must be key to the project.)"),
    (12812, "dialogue",
     "(Well, what she does not know can be taught.\n What matters is how she fits the team.)"),
]


#: Mission titles (config00.cpk -> config00.pac -> milstP00.bin, 128-byte cells, text at +10).
TITLES = [
    (10, "Episode 0 Main Mission"),
    (138, "Basic Training"),
    (266, "Rescue the White Base"),
    (394, "Episode 1 Main Mission"),
    (522, "Ep. 1: Prototype Labor Rampage"),
    (650, "\u3000\u3000 Sub Mission\u3000\u3000"),
    (778, "The Black Tri-Stars"),
    (906, "Stop the H-Bomb Missile"),
    (1034, "Defence Corps Training"),
    (1162, "Launching the Alex"),
    (1290, "Rescue the Medea Transport"),
    (1418, "The Rampaging Labor Returns"),
    (1546, "Infiltration"),
    (1674, "Episode 2 Main Mission"),
    (1802, "Ep. 2: Threat Beneath the Earth"),
]


def slot_section() -> dict:
    """The mission-title part of the spec: offsets, hashes and the English titles."""
    import configst_pack

    path = HERE.parent / "google_drive" / "config00.cpk"
    cpk = cpk_write.load(path)
    member = None
    for entry in cpk.members:
        if entry.name.lower().endswith(".pac"):
            for sub in configst_pack.parse_pac(entry.blob)["subs"]:
                if sub["name"] == "milstP00.bin":
                    member = sub["data"]
    if member is None:
        raise SystemExit("config00.cpk holds no milstP00.bin")
    layout = slot_text_apply.spec_for("mission_title")
    stride, slot = layout["stride"], layout["slot"]
    for offset, text in TITLES:
        if (offset - layout["header"]) % stride != slot % stride or offset % stride != slot:
            raise SystemExit(f"{offset} is not a mission_title slot")
        room = stride - slot - 1
        if len(text.encode("cp932")) > room:
            raise SystemExit(f"{offset}: {text!r} does not fit {room} bytes")
        index = offset // stride
        current = member[index * stride + slot:(index + 1) * stride].split(b"\x00", 1)[0]
        if not current:
            raise SystemExit(f"{offset}: the slot is empty in this file")
    return {"container": "PSP_GAME/USRDIR/config00.cpk", "kind": "mission_title",
            "member": "milstP00.bin", "md5_container": hashlib.md5(path.read_bytes()).hexdigest(),
            "md5_member": hashlib.md5(member).hexdigest(),
            "lines": [{"offset": offset, "text": text} for offset, text in TITLES]}


def main() -> int:
    too_wide = []
    for offset, kind, text in LINES:
        limit = {"narration": ETA.NARRATION_WIDTH, "dialogue": ETA.BOX_WIDTH}[kind]
        for line in text.split("\n"):
            width = ETA.export_strings.display_width(line)
            if width > limit:
                too_wide.append(f"{offset} ({kind}, {width} > {limit}): {line!r}")
    if too_wide:
        raise SystemExit("lines that do not fit, all of them:\n  " + "\n  ".join(too_wide))
    texts = [text for _o, _k, text in LINES]
    if len(set(texts)) != len(texts):
        raise SystemExit("two lines have the same English text; the verification counts texts")

    members = dict(SM.read_members(HERE.parent / "google_drive" / "eventP00.cpk"))
    blob = members[MEMBER]
    records, _ = ETA.parse_block_records(blob)
    known = {record["offset"] + ETA.text_start_of(blob, record): record["type"]
             for record in records if record["type"] in ETA.TEXT_START}
    for offset, kind, _text in LINES:
        if offset not in known:
            raise SystemExit(f"no text record starts at {offset} in {MEMBER}")
        expected = ETA.RECORD_NARRATION if kind == "narration" else ETA.RECORD_TEXT
        if known[offset] != expected:
            raise SystemExit(f"{offset} is type {known[offset]:#x}, not {expected:#x} ({kind})")

    container = (HERE.parent / "google_drive" / "eventP00.cpk").read_bytes()
    spec = {
        "opis": ("Test wtrysku: cale pierwsze scenki (narracja + dialogi). Repozytorium nie zawiera "
                 "danych gry - ten plik trzyma tylko offsety, skroty MD5 i nasze angielskie linie. "
                 "Japonski tekst jest czytany z Twojego ISO i pokazywany na ekranie."),
        "wersja_gry": "SRW OE 1.08 (PSP_GAME/USRDIR z ISO)",
        "container": CONTAINER,
        "member": MEMBER,
        "md5_container": hashlib.md5(container).hexdigest(),
        "md5_member": hashlib.md5(blob).hexdigest(),
        "lines": [{"offset": offset, "kind": kind, "text": text} for offset, kind, text in LINES],
        "slots": slot_section(),
    }
    SPEC.parent.mkdir(parents=True, exist_ok=True)
    SPEC.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"zapisane {SPEC.relative_to(HERE)}: {len(LINES)} linii scenki "
          f"({sum(1 for _o, k, _t in LINES if k == 'narration')} narracji, "
          f"{sum(1 for _o, k, _t in LINES if k == 'dialogue')} dialogow) "
          f"+ {len(TITLES)} tytulow misji")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
