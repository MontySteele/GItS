"""`EB-449`: no Furina face promises the retired Burst meter, and the set is a
RULE rather than a list.

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
"""

from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
FURINA_GEN = REPO / "klee-mod" / "KleeCode" / "Cards" / "Furina" / "Generated"
BURST_LINE = "[gold]Burst[/gold] +5."


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
    """Klee's fifteen and Kokomi's one keep their meters and their line, so
    nothing in their generated text may reach the switch."""
    assert len(_tagged("klee")) == 15
    assert len(_tagged("kokomi")) == 1

    for folder in ("Generated",):
        for path in (REPO / "klee-mod" / "KleeCode" / "Cards"
                     / folder).glob("*.cs"):
            assert "FurinaBurstRider" not in path.read_text(encoding="utf-8"), \
                path.name


def test_the_gameplay_marker_is_untouched():
    """Only the WORDS move: the tag still rides the row and the sim still
    decides whether it pays, so the day the arm is withdrawn the meter and its
    words come back together."""
    for card_id in _tagged("furina"):
        assert "ISkillTagCard" in _class_source(card_id), card_id


def test_the_generator_derives_the_set_and_never_lists_it():
    """The reopen's own words. A by-name list is what let Gentilhomme Usher be
    missed; the emission asks the sheet."""
    gen = (REPO / "tools" / "gen_klee_cards.py").read_text(encoding="utf-8")

    assert ('blanks_burst = (profile.character_id == "furina"\n'
            '                    and "skill_tag" in (card.get("tags") or ()))'
            ) in gen
