"""G-B3: the tripwire for the co-op ownership bug class.

THE HONEST SHAPE OF THIS TEST, stated up front because it is weaker than the
sprint doc asks for and the gap matters.

The doc asks for "a co-op-shaped unit test (two owners, interleaved companion
plays, assert the copy set)". That test cannot be written. The logic lives in
C#, there is no C# test project (the DLL only executes inside the game), and
tier 0.5 models exactly one seat -- so there is no runtime, on either side of
the language boundary, in which two owners can play cards at all.

That is not a gap in this test. It is the finding: **co-op has no sim
backstop.** Every co-op defect is play-derived, and will stay play-derived
until something models a second seat. G-B1 was found by two people playing the
game, and nothing in this repository could have found it.

So what is achievable is a STRUCTURAL tripwire: assert that the ownership
filter exists and that every consumer goes through it. That catches the
realistic regression -- somebody deletes the filter, or adds a second caller
that forgets it -- which is exactly how this bug got in. It does not catch a
filter that is present and wrong.
"""

from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_CS = _ROOT / "klee-mod" / "KleeCode"
_COMPANION_POWERS = _CS / "Powers" / "CompanionPowers.cs"


def test_companion_plays_are_recorded_with_their_owner():
    """The tracker stores who played what, not just what was played.

    The bug was that it stored only `List<ModelId>`, so ownership was not
    merely unfiltered -- it was unrecoverable.
    """
    src = _COMPANION_POWERS.read_text(encoding="utf-8")
    assert re.search(r"_played\s*=\s*new\(\)", src), "tracker list not found"
    # The entry may carry MORE than owner+id -- BFF-copy added the upgrade
    # flag the copy has to travel with -- but never less.
    assert re.search(r"List<\(Player Owner, ModelId Id[,)]", src), (
        "CompanionPlays no longer records an owner alongside the card id -- "
        "ownership becomes unrecoverable and Best Friends Forever copies the "
        "co-op partner's companions again (G-B1)")


def test_played_this_combat_requires_an_owner():
    """The query cannot be asked without saying whose plays it wants."""
    src = _COMPANION_POWERS.read_text(encoding="utf-8")
    signature = re.search(
        r"public static IReadOnlyList<.+?> PlayedThisCombat\(([^)]*)\)",
        src, re.S)
    assert signature, "PlayedThisCombat signature not found"
    params = signature.group(1)
    assert "Player" in params, (
        "PlayedThisCombat no longer takes an owner; a combat-wide query is "
        "the bug (G-B1)")
    assert "ReferenceEquals(entry.Owner, owner)" in src, (
        "PlayedThisCombat no longer filters by owner")


def test_the_entry_carries_the_upgrade_the_copy_has_to_travel_with():
    """BFF-copy (R114/FLAG-2(i)), pinned here because this tracker is the
    only record the replay has to read.

    An id alone names the PRINTED card and `ModelDb.GetById` rebuilds it
    pristine, so a ledger of bare ModelIds replays every companion
    un-upgraded. The sim never had the gap -- it appends `card.id`, which is
    `foo+` when the played card was upgraded. Same class as the ownership bug
    above: state that was never recorded cannot be recovered downstream.
    """
    src = _COMPANION_POWERS.read_text(encoding="utf-8")
    assert re.search(r"_played\.Add\(\(owner,\s*card\.Id,\s*card\.IsUpgraded\)\)",
                     src), (
        "CompanionPlays no longer records the played card's upgrade state -- "
        "Best Friends Forever replays upgraded companions un-upgraded again "
        "(BFF-copy)")


def test_uniqueness_is_per_owner_not_global():
    """If both players play Oz, both must get an Oz back.

    Deduplicating across owners would fix the leak by creating a subtler one:
    the second player's copy silently vanishes.
    """
    src = _COMPANION_POWERS.read_text(encoding="utf-8")
    assert re.search(
        r"_played\.Any\(entry\s*=>\s*ReferenceEquals\(entry\.Owner,\s*owner\)"
        r"\s*&&\s*entry\.Id\s*==\s*card\.Id\)", src), (
        "the duplicate check is no longer scoped to the owner -- one player "
        "playing a companion would suppress the other's copy of it")


def test_no_caller_asks_the_combat_wide_question():
    """Every call site passes an owner. This is the tripwire that matters.

    A regression here is not a rewrite of the tracker -- it is a NEW consumer
    that copies the old one-argument call shape from somewhere, or a
    regenerated card emitted by a generator branch nobody updated.
    """
    offenders = []
    for path in _CS.rglob("*.cs"):
        for n, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), 1):
            for call in re.finditer(r"PlayedThisCombat\(([^)]*)\)", line):
                args = call.group(1)
                # The declaration itself carries the parameter list, which
                # legitimately names its types rather than passing values.
                if re.search(r"IReadOnlyList<.+?> PlayedThisCombat", line):
                    continue
                if "," not in args:
                    offenders.append(
                        f"{path.relative_to(_ROOT)}:{n}: {line.strip()}")
    assert not offenders, (
        "combat-wide PlayedThisCombat call(s) -- pass the owner (G-B1):\n"
        + "\n".join(offenders))
