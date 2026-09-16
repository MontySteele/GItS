#!/usr/bin/env python3
"""The one writer and reader of `docs/retired-card-ids.yaml` (`EB-790`).

A retired card id is an id a SAVE can still hold after the class that owned it
has left the tree; the register's own header is the why, and this module is
the machinery: it derives the id a deleted generated class used to answer to,
and appends a row for it.

WHY A MODULE AND NOT A LINE IN THE GENERATOR. Every card-codegen profile --
the three character sheets and the quarantined prototype surface -- funnels
through `gen_klee_cards._write_plan`, which deletes the stale `.cs` files
before it writes the new ones. That delete IS the retirement, and it is the
ONLY moment in the whole pipeline when both halves are in hand: the id that is
going away and the fact that it is going away. Recording it anywhere else
means someone remembering, and a list that depends on remembering is the list
that was missing when `live-looks-8c` read the owner's godot.log.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REGISTER = REPO / "docs" / "retired-card-ids.yaml"
PREFIX = "KLEEMOD-"
OWNERS = ("klee", "furina", "kokomi")

# The prototype surface's id prefixes name the owning character; the surface's
# own `character_id` is the string "prototype", which is no pool. Order
# matters only in that every key here is distinct.
PROTO_OWNER_PREFIXES = {
    "PROTO_FR_": "furina",
    "PROTO_FS_": "furina",
    "PROTO_KK_": "kokomi",
    "PROTO_CHARGE_": "kokomi",
    "PROTO_KO_": "klee",
}


def entry_for(class_name: str) -> str:
    """The `ModelId.Entry` a generated class answers to.

    `ModelDb.GetEntry` is `StringHelper.Slugify(type.Name)` and BaseLib's
    `PrefixIdPatch` puts the root namespace in front of it for anything
    implementing `ICustomModel`, which every generated card does --
    `ProtoKoFwoosh` -> `KLEEMOD-PROTO_KO_FWOOSH`. Slugify inserts `_` at each
    lower-or-digit-to-upper boundary, uppercases, and drops what is left.
    """
    slug = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", class_name)
    return PREFIX + re.sub(r"[^A-Z0-9_]", "", slug.upper())


def owner_for(entry: str, character_id: str) -> str:
    """Which character's pool the alias should point at."""
    if character_id in OWNERS:
        return character_id
    body = entry[len(PREFIX):]
    for prefix, owner in PROTO_OWNER_PREFIXES.items():
        if body.startswith(prefix):
            return owner
    # The Klee arms carried no character infix (PROTO_SPARK_STRIKE,
    # PROTO_KABOOM_SINK). Klee is the fallback because she is the character
    # whose prototype rows have never used one.
    return "klee"


def listed() -> set[str]:
    """Ids already in the register. Deliberately a text scan and not a YAML
    parse: this runs inside a codegen write, and a register that has been
    hand-edited into something `yaml` rejects must not take the codegen down
    with it -- the lint is where a malformed register is reported."""
    if not REGISTER.is_file():
        return set()
    return set(re.findall(r"\bid:\s*(KLEEMOD-[A-Z0-9_]+)",
                          REGISTER.read_text(encoding="utf-8")))


def record(class_names: list[str], character_id: str, reason: str) -> list[str]:
    """Append a register row for each departing class. Returns the ids added.

    Idempotent: a class whose id is already listed is skipped, so a regen that
    changes nothing writes nothing, and re-adding a row and cutting it again
    does not duplicate it.
    """
    if not REGISTER.is_file():
        return []
    have = listed()
    rows = []
    for name in sorted(class_names):
        entry = entry_for(name)
        if entry in have:
            continue
        have.add(entry)
        owner = owner_for(entry, character_id)
        rows.append(f"  - {{id: {entry}, owner: {owner}, left: \"{reason}\"}}")
    if not rows:
        return []
    text = REGISTER.read_text(encoding="utf-8").rstrip("\n")
    REGISTER.write_text(text + "\n" + "\n".join(rows) + "\n",
                        encoding="utf-8", newline="\n")
    return [row.split()[2].rstrip(",") for row in rows]
