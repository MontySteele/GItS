#!/usr/bin/env python3
"""Every prototype face that applies an element NAMES it.

WHY ([USER], 2026-10-02, after a co-op run): "Unify the language across all
cards - say if it does an element and also apply the symbol to the card". That
reversed the 2026-09-01 rule, under which the element gem beside the type
plaque replaced the sentence. A face now says the element in words AND wears
the gem (`klee-mod/KleeCode/Vfx/ElementBadge.cs`). Before the ruling, 84 rows
across all four kits hit with an element their text never named, because the
element came from the kit's cadence or from `applies_element: true` and not
from anything printed. This lint keeps that from drifting back.

WHAT A FACE OWES, per row, read off the same generator predicates that decide
the gem (`gen_klee_cards.aura_elements_for`, `plan_applies_element`):

  * an `apply_aura` (anywhere in the tree) or a Varka kind's own hit: its
    element, always;
  * the card's own hit, when that hit applies an element (the cadence, or
    `applies_element: true`): the element, if the face prints a hit sentence
    ("Deal N damage", "Deal damage equal to ...");
  * a Plan whose carry-out hits (Kokomi): Hydro.

A Swirl owes no word: it is Anemo by definition, so the verb names it, and the
card wears the Anemo gem. The text convention is
`docs/current/text-conventions.md`, the row "Element application".

Usage: python tools/lint_element_text.py
Exit 1 with findings on stdout.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import gen_klee_cards as gen                    # noqa: E402
import gen_prototype_cards as proto             # noqa: E402

#: A printed hit: "Deal 6 damage", "deal {Damage:diff()} damage", "Deal
#: damage equal to", with an element word allowed before "damage".
HIT = re.compile(
    r"\b[Dd]eal (?:(?:\d+|\{[^{}]+\}) )?(?:\[gold\]\w+\[/gold\] )?damage\b")

#: Faces that cannot take the word without going over the 120-character card
#: ceiling `lint_text_conventions.py` measures, and that the ruling did not
#: ask to be reworded. Each needs a shorter sentence from the design session.
#: ROTS ON PURPOSE: an entry whose face has since named its element FAILS, so
#: the set only shrinks.
DEBT: dict[str, str] = {
    "proto_kk_riptide":
        "naming Hydro puts the face at 124 of 120",
    "proto_kk_undertide_lance":
        "naming Hydro on the hit alone puts the face at 126 of 120",
}


def owed_elements(card: dict, profile: gen.CharacterProfile,
                  face: str) -> list[str]:
    """The elements this face must name, lowercase, in face order."""
    if gen.is_companion(card):
        elemental = any(e.get("applies_element")
                        for e in gen.companion_damage_effects(card))
        own = card.get("element")
    else:
        elemental = profile.damage_applies_element(card)
        own = profile.native_element
    owed: list[str] = []
    if elemental and own and HIT.search(face):
        owed.append(own)
    # The printed auras and the Varka kinds' own hits: `aura_elements_for`
    # with `elemental=False` is exactly those, without the cadence.
    owed.extend(gen.aura_elements_for(card, profile, False))
    if gen.plan_applies_element(card, profile):
        owed.append(profile.native_element)
    return list(dict.fromkeys(owed))


def findings(stats: dict | None = None) -> list[str]:
    out: list[str] = []
    checked = 0
    seen_debt: set[str] = set()
    for row in proto._rows():
        card = proto.authorship.strip_field(row)
        profile = proto._profile_for(card["character"])
        face = gen.build_description(card)
        owed = owed_elements(card, profile, face)
        if not owed:
            continue
        checked += 1
        missing = [e for e in owed if f"[gold]{e.capitalize()}[/gold]" not in face]
        if card["id"] in DEBT:
            seen_debt.add(card["id"])
            if not missing:
                out.append(f"{card['id']}: names its element now; delete its "
                           f"DEBT row")
            continue
        if missing:
            out.append(f"{card['id']}: applies "
                       f"{', '.join(e.capitalize() for e in missing)} and its "
                       f"face does not say so: {face!r}")
    for cid in sorted(set(DEBT) - seen_debt):
        out.append(f"{cid}: DEBT row names no element row on the surface; "
                   f"delete it")
    if stats is not None:
        stats["checked"] = checked
    if checked < 100:
        out.append(f"only {checked} element rows checked; the scan read "
                   f"less of the surface than it should")
    return out


def main() -> int:
    stats: dict = {}
    out = findings(stats)
    for line in out:
        print(line)
    if out:
        print(f"\n{len(out)} face(s) apply an element they do not name. "
              "Write it in: \"Deal 6 [gold]Pyro[/gold] damage.\", "
              "\"Apply [gold]Hydro[/gold] to an enemy.\" "
              "(docs/current/text-conventions.md).")
        return 1
    print(f"element-text: {stats['checked']} faces that apply an element "
          f"checked; every one names it but the {len(DEBT)} carried as DEBT")
    for cid, why in DEBT.items():
        print(f"  {cid}: {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
