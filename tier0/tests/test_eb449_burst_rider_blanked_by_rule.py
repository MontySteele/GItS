"""`EB-449` / `EB-524`: no face promises the retired Burst meter under the
Furina arm, and the set is a RULE rather than a list.

WHAT THE SEAT SAW (Furina r11, lane 1). Under the reframe the shipped Burst
meter is retired -- `furina_reframe.burst_retired` is the one question the
display guard, the income funnel and the kit grant all ask -- and the r8 pass
took the explanatory TIP off her faces. It did not touch the two things a seat
actually reads: the printed "Burst +5." at the end of the body, and the gold
"Elemental Skill" keyword the game appends under it. The seat met both on
Gentilhomme Usher at two separate rewards and skipped the card for it.

THE SET IS `tags: [skill_tag]` ON HER OWN SHEET, thirteen rows, derived at
codegen off the same field that emits `ISkillTagCard` -- so a fourteenth row
inherits the blank instead of having to be remembered. That is the reopen:
"census every shipped face with the rider, not five by name".

FURINA-SCOPED, and this file is where that is checkable from: `skill_tag` is
also on fifteen Klee rows and one of Kokomi's, and those two meters are not
retired. A blank that reached them would be a silent nerf to two other kits.

THE RUNTIME READ, not a `#if`: the generated files are committed and must be
one text whatever the build, so `FurinaBurstRider.Face` picks between the two
faces at boot off the flag whose default IS the compile switch. That is what
lets the C# suite read BOTH sides (`KleeTests/Prototype/Round17Tests.cs`);
what is checkable here is the census and the emission.

`EB-524`, THE SECOND SOURCE, one sheet over. A COMPANION row is on nobody's
character sheet, so the `skill_tag` predicate never reached one -- and a
companion is drafted by whoever is playing. Furina r12 lane 1: "Bennett and
Barbara print 'Burst +5', no screen defines it, no meter appears." What those
faces print is their own `burst_energy` clause, and `KleeBurstResource.Gain`
already refuses to pay a creature whose meter the arm retired, so the effect
was right and only the sentence was left promising. The second predicate is
derived from the EFFECT the same way the first is from the field, and it drops
the clause alone: a companion row carries no `Elemental Skill` keyword.
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
FURINA_GEN = REPO / "klee-mod" / "KleeCode" / "Cards" / "Furina" / "Generated"
COMPANION_GEN = REPO / "klee-mod" / "KleeCode" / "Cards" / "Generated"
BURST_LINE = "[gold]Burst[/gold] +5."
#: `EB-524`: what a COMPANION row prints for its own `burst_energy` clause.
COMPANION_BURST = "[gold]Burst Energy[/gold]."
COMPANION_SHEETS = ("mondstadt", "inazuma", "fontaine")


def _sheet(name: str) -> list[dict]:
    return yaml.safe_load(
        (REPO / "docs" / f"{name}-cards.yaml").read_text(encoding="utf-8"))


def _tagged(name: str) -> list[str]:
    return [row["id"] for row in _sheet(name)
            if "skill_tag" in (row.get("tags") or ())]


def _class_source(card_id: str) -> str:
    cls = "".join(part.title() for part in card_id.split("_"))
    hits = [path for path in FURINA_GEN.glob("*.cs")
            if f"class {cls} :" in path.read_text(encoding="utf-8")]
    assert len(hits) == 1, (card_id, cls, hits)
    return hits[0].read_text(encoding="utf-8")


def test_the_census_is_thirteen_rows_off_her_own_sheet():
    tagged = _tagged("furina")

    assert len(tagged) == 13
    assert "gentilhomme_usher" in tagged


def test_every_one_of_them_carries_both_arm_switches():
    """Both surfaces, on every row: the printed body and the keyword. The
    keyword cannot be re-worded per arm -- its loc row is registered once at
    boot for every carrier -- so under the arm the card does not carry it."""
    for card_id in _tagged("furina"):
        source = _class_source(card_id)

        assert "FurinaBurstRider.Face(" in source, card_id
        keywords = source.split("FurinaBurstRider.Keywords(", 1)[1]
        assert "KleeKeywords.ElementalSkill" in keywords.split(");")[0], card_id


def test_the_arm_face_drops_the_line_and_the_shipped_face_keeps_it():
    """One `Face(arm, shipped)` call per row, and the two arguments differ by
    exactly the rider."""
    for card_id in _tagged("furina"):
        source = _class_source(card_id)
        call = source.split("FurinaBurstRider.Face(", 1)[1]
        arm, shipped = call.split('", "', 1)

        assert BURST_LINE not in arm, card_id
        assert BURST_LINE in shipped.split('")')[0], card_id


def test_the_blank_is_furina_scoped():
    """Klee's fifteen and Kokomi's one keep their meters and their line, so no
    row of theirs may reach the switch. `EB-524` widened it to the COMPANION
    sheets and to nothing else -- a companion is drafted by whoever is playing,
    and a character sheet is not."""
    assert len(_tagged("klee")) == 15
    assert len(_tagged("kokomi")) == 1

    for path in COMPANION_GEN.glob("*.cs"):
        source = path.read_text(encoding="utf-8")
        if "FurinaBurstRider" not in source:
            continue
        assert "ICompanionCard" in source, path.name


def test_the_gameplay_marker_is_untouched():
    """Only the WORDS move: the tag still rides the row and the sim still
    decides whether it pays, so the day the arm is withdrawn the meter and its
    words come back together."""
    for card_id in _tagged("furina"):
        assert "ISkillTagCard" in _class_source(card_id), card_id


def test_the_generator_derives_the_set_and_never_lists_it():
    """The reopen's own words. A by-name list is what let Gentilhomme Usher be
    missed; the emission asks the sheet, and `EB-524`'s half asks the effect."""
    gen = (REPO / "tools" / "gen_klee_cards.py").read_text(encoding="utf-8")

    assert ('blanks_skill_tag = (profile.character_id == "furina"\n'
            '                        and "skill_tag" in (card.get("tags") or ()))'
            ) in gen
    assert ('blanks_burst = blanks_skill_tag or (\n'
            '        is_companion(card)\n'
            '        and any(eff.get("op") == "burst_energy"\n'
            '                for eff in (card.get("effects") or ())))') in gen


# --- `EB-524`: THE COMPANION SHEETS, WHERE THE SAME PROMISE HAD NO SHEET ----


def _companion_rows() -> list[dict]:
    rows: list[dict] = []
    for nation in COMPANION_SHEETS:
        rows += yaml.safe_load(
            (REPO / "docs" / f"{nation}-companions.yaml").read_text(
                encoding="utf-8"))
    return rows


def _companion_source(card_id: str) -> str:
    """A companion row's emitted class. BOTH folders, because the Fontaine
    sheet also carries Furina's three Guest Stars, which are hers rather than
    the roster's and emit into her own directory."""
    cls = "".join(part.title() for part in card_id.split("_"))
    hits = [path for folder in (COMPANION_GEN, FURINA_GEN)
            for path in folder.glob("*.cs")
            if f"class {cls} :" in path.read_text(encoding="utf-8")]
    assert len(hits) == 1, (card_id, cls, hits)
    return hits[0].read_text(encoding="utf-8")


def _grants_burst(row: dict) -> bool:
    return any(eff.get("op") == "burst_energy"
               for eff in (row.get("effects") or ()))


def test_the_census_is_every_companion_row_that_grants_burst():
    """SHEET-WIDE over all three nations, which is the row's own ask: the set
    is "grants Burst", not a list of the two faces the seat happened to meet,
    so a fourth such row inherits the blank."""
    granting = [row["id"] for row in _companion_rows() if _grants_burst(row)]

    assert len(granting) == 3
    assert "bennett_passion" in granting          # the seat's own two
    assert "barbara_melody" in granting


def test_every_granting_companion_carries_the_arm_switch():
    """And no other companion does: the switch follows the clause."""
    for row in _companion_rows():
        source = _companion_source(row["id"])
        assert ("FurinaBurstRider.Face(" in source) == _grants_burst(row), \
            row["id"]


def test_the_arm_face_drops_the_companion_clause_and_the_shipped_one_keeps_it():
    for row in _companion_rows():
        if not _grants_burst(row):
            continue
        call = _companion_source(row["id"]).split(
            "FurinaBurstRider.Face(", 1)[1]
        arm, shipped = call.split('", "', 1)

        assert COMPANION_BURST not in arm, row["id"]
        assert COMPANION_BURST in shipped.split('")')[0], row["id"]


def test_a_companion_row_drops_the_clause_and_no_keyword():
    """The two sheets print the promise in different places, so they take
    different halves of the switch: `Elemental Skill` is a `skill_tag` row's
    keyword and a companion carries none, so wrapping its keyword list would
    filter a set the word was never in."""
    for row in _companion_rows():
        if not _grants_burst(row):
            continue
        assert "FurinaBurstRider.Keywords(" not in _companion_source(
            row["id"]), row["id"]


def test_the_grant_itself_is_untouched():
    """`EB-449`'s last rule, one sheet over: only the WORDS move. The play
    still calls the shared funnel, which is where the arm already refuses to
    pay a creature whose meter it retired."""
    for row in _companion_rows():
        if not _grants_burst(row):
            continue
        assert "KleeBurstResource.Gain" in _companion_source(row["id"]), \
            row["id"]


# ======================================================================
# `EB-568`: THE FLOOR IS ON THE FACE, AND `EB-507` MUST NOT BLANK IT
# ======================================================================
#
# WHAT THE SEAT SAW (Furina r14 lane 2, (c) 1). Rapturous Applause printed
# "Fanfare +8" and the card's durable effect is a BASELINE of 8: Fanfare sat
# at 8 for three fights, two meters the seat could not explain appeared
# ("Fanfare Floor / Cap Bonus 8"), and the verdict was "much better than
# printed" -- a card under-reporting itself by the half that lasts.
#
# THE OP MOVES ALL THREE NUMBERS (`resources.gain_fanfare_floor`: floor, cap
# and current), so the face is two clauses because the effect is two facts.
# Both are true on every build; the arm is only where the second is
# load-bearing, because there Fanfare is minted by performance alone and the
# floor is most of what a deck ever holds.

FLOOR_LINE = ("[gold]Fanfare[/gold] +{FanfareFloor:diff()}, and cannot fall "
              "below {FanfareFloor:diff()}.")

#: Every shipped row carrying `gain_fanfare_floor`. Derived rather than named,
#: `_tagged`'s rule one op over: a fourth row inherits the sentence.
def _floor_rows() -> list[str]:
    return [row["id"] for row in _sheet("furina")
            if any(fx.get("op") == "gain_fanfare_floor"
                   for fx in (row.get("effects") or ()))]


def test_every_floor_row_prints_the_bound_it_buys():
    rows = _floor_rows()

    assert "rapturous_applause" in rows
    for card_id in rows:
        assert FLOOR_LINE in _class_source(card_id), card_id


def test_the_floor_clause_is_not_a_fanfare_promise_eb507_may_blank():
    """`EB-507` blanks a rider whose face promises Fanfare from something
    other than a performance. THE FLOOR CLAUSE IS NOT ONE: it states a bound
    the arm's own meter is read against, mints nothing, and is the one true
    sentence this card had been missing. A blank that reached it would put the
    row back where `EB-568` found it.

    Pinned as the SENTENCE rather than as an exemption list, because the rule
    is about what the words say: any future blanking rule that removes this
    text fails here.
    """
    for card_id in _floor_rows():
        source = _class_source(card_id)
        assert "cannot fall below" in source, card_id
        # The grant half is still printed -- the op really does raise current
        # Fanfare -- so the two clauses stand or fall together.
        assert "[gold]Fanfare[/gold] +{FanfareFloor:diff()}" in source, card_id
