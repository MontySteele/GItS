"""The ELEMENT INDICATOR: the element a card applies is a gem, not a sentence.

[USER], 2026-09-01, after playing Klee: *"instead of saying 'applies pyro' -
maybe make it a card indicator as well to remove text overhead? That would be a
universal shift."*

WHAT THE SENTENCE WAS, because it decided the shape of the change. It was never
emitted text: no sheet row and no generated `Localization` has ever contained
the words. `KleeKeywords.AppliesPyro` and its three siblings carried
`AutoKeywordPosition.After`, which BaseLib's `GenEnumValues` puts into
`AutoKeywordText.AdditionalAfterKeywords` and from there into the base game's
`CardKeywordOrder.afterDescription`, where `CardModel.BuildDescription` appends
it as a line of the rules box. So ONE switch -- those four fields moving to
`AutoKeywordPosition.None` -- is the whole of the removal, on every face of
every sheet at once, and the same four keywords are now what
`Vfx/ElementBadge.cs` reads to paint the aura's own icon beside the type plaque.

WHAT IS PROVABLE HERE, AND WHY IT IS THE HEADLESS HALF. Painting needs Godot
nodes and the keyword VALUES are assigned by BaseLib at `ModelDb.Init`, so
neither is reachable from a Python test or from a test host (`klee-mod/
KleeTests/README.md`, the headless boundary). What is reachable is every
DECLARATION the gem depends on, and each one is a way the change could rot:

  1. the generator's one rule (`gen.aura_elements_for`), driven both ways;
  2. the committed prototype tree obeying it -- every row that applies an
     element carries the keyword that draws its gem, with non-vacuous
     denominators, and no row carries one it does not apply;
  3. no face on any sheet printing the sentence, which is the half [USER] asked
     for;
  4. the switch itself, in `KleeKeywords.cs`, since a field quietly returning
     to `After` would put the sentence back on 114 faces; and
  5. `ElementBadge` declaring a gem for exactly the four elements that leave an
     aura -- a keyword with no icon draws nothing at all and would be invisible
     in exactly the way the missing tooltips of `EB-272` were.

The C# side of the same join is `klee-mod/KleeTests/ElementBadgeTests.cs`, which
reads the compiled attribute rather than the source line.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import gen_klee_cards as gen                    # noqa: E402
import gen_prototype_cards as proto             # noqa: E402

CARD_ROOT = REPO / "klee-mod" / "KleeCode" / "Cards"
KEYWORDS_CS = CARD_ROOT / "KleeKeywords.cs"
BADGE_CS = REPO / "klee-mod" / "KleeCode" / "Vfx" / "ElementBadge.cs"

# Every generated tree plus the hand-written faces beside them. The claim in
# test 3 is about what a PLAYER reads, so it is scoped to card faces and not to
# the keyword's own definition, which still says "Applies Pyro" in its tooltip
# and must.
GENERATED_DIRS = (CARD_ROOT / "Generated",
                  CARD_ROOT / "Furina" / "Generated",
                  CARD_ROOT / "Kokomi" / "Generated",
                  CARD_ROOT / "Prototype" / "Generated")

_DESCRIPTION = re.compile(r'\("description", "((?:[^"\\]|\\.)*)"\)')
_KEYWORDS_MEMBER = re.compile(
    r"CanonicalKeywords =>\s*\n\s*new\[\] \{ (.*?) \};", re.S)

# `[CustomEnum("applies_pyro")]` then `[KeywordProperties(<position>)]`.
_APPLIES_FIELD = re.compile(
    r'\[CustomEnum\("(applies_\w+)"\)\]\s*\n'
    r'\s*\[KeywordProperties\(AutoKeywordPosition\.(\w+)\)\]')


def _declared_keywords(source: str) -> list[str]:
    m = _KEYWORDS_MEMBER.search(source)
    if not m:
        return []
    return [part.strip() for part in m.group(1).split(",") if part.strip()]


# ------------------------------------------------------------- the rule -----

def test_the_rule_takes_the_cadence_first_and_the_printed_aura_after():
    """Both halves of `aura_elements_for`, and their ORDER.

    Klee is catalyst-grade, so her Attack's element comes from her cadence and
    nothing on the row says so; an `apply_aura` effect names its own. A face
    that does both wears the element its DAMAGE carries, which is the one
    `ElementBadge.ElementOf` draws.
    """
    attack = {"id": "x", "type": "attack",
              "effects": [{"op": "damage", "amount": 6, "target": "enemy"}]}
    assert gen.aura_elements_for(attack, gen.KLEE_PROFILE, True) == ["pyro"]
    assert gen.aura_elements_for(attack, gen.KLEE_PROFILE, False) == []

    both = {"id": "x", "type": "attack",
            "effects": [{"op": "damage", "amount": 6, "target": "enemy"},
                        {"op": "apply_aura", "element": "cryo",
                         "target": "enemy"}]}
    assert gen.aura_elements_for(both, gen.KLEE_PROFILE, True) == [
        "pyro", "cryo"]


def test_an_element_that_leaves_no_aura_gets_no_keyword_and_no_gem():
    """LAW, combat: *"Anemo/Geo leave no aura -- they only trigger."* A Swirl
    card has always been keyword-less and sentence-less; it stays gem-less, so
    the indicator says exactly what the sentence said and no more."""
    swirl = {"id": "x", "type": "skill",
             "effects": [{"op": "swirl", "target": "enemy"}]}
    assert gen.aura_elements_for(swirl, gen.KLEE_PROFILE, False) == []
    assert set(gen.AURA_KEYWORD_BY_ELEMENT) == {
        "pyro", "hydro", "electro", "cryo"}


# ------------------------------------------- the committed prototype tree ---

def test_every_prototype_row_that_applies_an_element_carries_its_gem():
    """THE JOIN, over the rows that ship to a dev build.

    The keyword is the indicator: `ElementBadge.ElementOf` reads it off the
    card, `KleeCardTooltips` raises the tip from it, and codegen emits it from
    the sheet's cadence. So a prototype row that applies an element and carries
    no keyword is a card that says nothing about its element anywhere -- which
    is the state every face would have been left in had the sentence been
    removed without the gem.
    """
    wearing: list[str] = []
    missing: list[str] = []
    surplus: list[str] = []
    for row in proto._rows():
        card = proto.authorship.strip_field(row)
        profile = proto._profile_for(card["character"])
        if gen.is_companion(card):
            elemental = any(e.get("applies_element")
                            for e in gen.companion_damage_effects(card))
        else:
            elemental = profile.damage_applies_element(card)
        expected = [gen.AURA_KEYWORD_BY_ELEMENT[e]
                    for e in gen.aura_elements_for(card, profile, elemental)]

        path = proto.OUT_DIR / f"{gen.pascal(card['id'])}.cs"
        if not path.is_file():
            continue                      # a blocked row emits no class
        declared = [k for k in _declared_keywords(
            path.read_text(encoding="utf-8"))
            if k.startswith("KleeKeywords.Applies")]

        if expected:
            wearing.append(card["id"])
        for keyword in expected:
            if keyword not in declared:
                missing.append(f"{card['id']}: {keyword}")
        for keyword in declared:
            if keyword not in expected:
                surplus.append(f"{card['id']}: {keyword}")

    assert missing == []
    assert surplus == []
    # Non-vacuous, and by arm: a scrape that silently read nothing could not
    # pass this test, and neither could one that only reached Klee's rows.
    assert len(wearing) >= 40, wearing
    for prefix in ("proto_ko_", "proto_kk_", "proto_mc_", "proto_mi_"):
        assert any(cid.startswith(prefix) for cid in wearing), prefix


# --------------------------------------------------------- the sentence ----

def test_no_card_face_prints_the_applies_sentence():
    """[USER]'s ask, checked where a player reads.

    It has always been true of the SHEETS -- the words came from the keyword's
    auto-position, never from a description -- so this is the pin that keeps it
    true from the other direction too: a row typing the sentence into its own
    text would put back exactly the overhead the gem removes.
    """
    offenders = []
    for directory in GENERATED_DIRS:
        for path in sorted(directory.glob("*.cs")):
            for description in _DESCRIPTION.findall(
                    path.read_text(encoding="utf-8")):
                if re.search(r"\bApplies (Pyro|Hydro|Electro|Cryo)\b",
                             description):
                    offenders.append(f"{path.name}: {description}")
    assert offenders == []


def test_no_applies_keyword_auto_prints_a_line_any_more():
    """THE ONE SWITCH, in the file that owns it.

    `AutoKeywordPosition.After` is what printed the sentence, so a field
    quietly returning to it would put the sentence back on all 114 faces and
    nothing else in this repo would notice. All four are `None` -- the position
    `Bomb`, `Confiscated` and the eight reaction previews have always ridden,
    which is the standing proof that a tip survives it: they have never printed
    a line and have always hovered.
    """
    fields = dict(_APPLIES_FIELD.findall(
        KEYWORDS_CS.read_text(encoding="utf-8")))

    assert set(fields) == {"applies_pyro", "applies_hydro",
                           "applies_electro", "applies_cryo"}
    assert set(fields.values()) == {"None"}


# ------------------------------------------------------------- the gem -----

def test_every_aura_element_declares_a_gem_of_its_own():
    """A keyword whose element has no icon draws NOTHING -- the invisible
    failure `EB-272` was made of, one surface over. Each path is under
    `klee/powers/`, which is what makes `build_pck` carry it, and each is the
    AURA's own icon: the badge a player will see on the enemy is the picture on
    the card that puts it there."""
    source = BADGE_CS.read_text(encoding="utf-8")
    declared = dict(re.findall(
        r"Element\.(\w+) => \"(klee/powers/aura_\w+\.png)\"", source))

    assert declared == {
        "Pyro": "klee/powers/aura_pyro.png",
        "Hydro": "klee/powers/aura_hydro.png",
        "Electro": "klee/powers/aura_electro.png",
        "Cryo": "klee/powers/aura_cryo.png",
    }
    # The four the keywords name, and only those.
    assert {e.capitalize() for e in gen.AURA_KEYWORD_BY_ELEMENT} == set(
        declared)


# ------------------------ `EB-378`: the two holes in the scan ---------------
#
# THE FINDING. "Kurage's Oath and Sango Isshin apply a Hydro aura but do not
# print `[Hydro]`. Slack Water, Undertow and Feint all carry a visible
# `[Hydro]` tag with the *Applies Hydro* gloss... In a kit whose whole reaction
# system keys off which element is clinging to a body, an untagged aura source
# is a real hole." (Kokomi r9 run 2, act 1, finding 2.)


def test_a_branch_gated_aura_still_declares_its_element():
    """The scan read the TOP LEVEL only, so a row whose `apply_aura` sat inside
    a `conditional` declared nothing while applying the aura on resolution --
    `EB-142`'s shape, one scan over.

    SEEN TO FAIL: with the old top-level walk this row returned `[]`.
    """
    branched = {"id": "x", "type": "skill",
                "effects": [{"op": "conditional", "if": "x",
                             "then": [{"op": "apply_aura", "element": "cryo",
                                       "target": "enemy"}],
                             "else": [{"op": "block", "amount": 5}]}]}
    assert gen.aura_elements_for(branched, gen.KLEE_PROFILE, False) == ["cryo"]


def test_a_damaging_plan_declares_the_carry_outs_element():
    """`KokomiPlan.ResolveAll` deals every damaging Plan clause as
    `ElementalHit.Deal(..., Element.Hydro, ...)`, whatever the card's type, and
    the sim's twin does the same. So a SKILL with a damaging Plan leaves a
    Hydro aura and its face must say so."""
    oath = {"id": "x", "type": "skill",
            "effects": [{"op": "damage", "amount": 3, "target": "all_enemies"}],
            "plan": [{"op": "damage", "amount": 7, "target": "all_enemies"}]}
    assert gen.plan_applies_element(oath, gen.KOKOMI_PROFILE) is True
    assert gen.aura_elements_for(oath, gen.KOKOMI_PROFILE, False) == ["hydro"]
    # All three hitting clauses, and only those.
    for op in sorted(gen.PLAN_DAMAGE_OPS):
        row = {"id": "x", "type": "skill", "effects": [],
               "plan": [{"op": op, "amount": 4, "target": "enemy"}]}
        assert gen.plan_applies_element(row, gen.KOKOMI_PROFILE), op
    for op in ("block", "draw", "mend", "apply_power"):
        row = {"id": "x", "type": "skill", "effects": [],
               "plan": [{"op": op, "amount": 4, "target": "self"}]}
        assert not gen.plan_applies_element(row, gen.KOKOMI_PROFILE), op


def test_the_plan_half_never_elements_the_cards_own_hit():
    """The split that keeps this a DISPLAY fix. `elemental` is what puts
    `IElementalCard` on the row, which is what
    `CatalystCadence.PrintedElement` reads to element the card's own play --
    so a Skill with a damaging Plan gains the face declaration and its now-line
    still applies nothing, which is what it did before this row."""
    oath = {"id": "x", "type": "skill",
            "effects": [{"op": "damage", "amount": 3, "target": "all_enemies"}],
            "plan": [{"op": "damage", "amount": 7, "target": "all_enemies"}]}
    assert gen.KOKOMI_PROFILE.damage_applies_element(oath) is False
    text = (proto.OUT_DIR / "ProtoKkKuragesOath.cs").read_text(
        encoding="utf-8")
    assert "IElementalCard" not in text
    assert "KleeKeywords.AppliesHydro" in text
    # And the sentence that says when, so the gem cannot be read as "this
    # card's own hit applies Hydro".
    assert "ArmKeywordTips.ForPlanElement(" in text


def test_a_plan_is_not_a_furina_rule():
    """Scoped to the catalyst profiles. Furina is Skill-grade and has no
    jellyfish, so the question is asked of the profile and answered no."""
    row = {"id": "x", "type": "skill", "effects": [],
           "plan": [{"op": "damage", "amount": 7, "target": "enemy"}]}
    assert gen.plan_applies_element(row, gen.FURINA_PROFILE) is False


def test_the_rows_the_finding_names_carry_the_gem():
    """`Kurage's Oath` and `Sango Isshin` by name, beside the three the seat
    read as correct."""
    for stem in ("ProtoKkKuragesOath", "ProtoKkSangoIsshin",
                 "ProtoKkSlackWater", "ProtoKkUndertow", "ProtoKkFeint"):
        text = (proto.OUT_DIR / f"{stem}.cs").read_text(encoding="utf-8")
        assert "KleeKeywords.AppliesHydro" in text, stem


def test_only_the_plan_only_rows_carry_the_when_sentence():
    """An Attack of hers already elements its own hit, so it owes no
    explanation; the sentence rides exactly the rows where the Plan is the
    only source."""
    carriers = {p.stem for p in proto.OUT_DIR.glob("*.cs")
                if "ArmKeywordTips.ForPlanElement(" in p.read_text(
                    encoding="utf-8")}
    assert carriers, "no row carries the sentence"
    for stem in carriers:
        text = (proto.OUT_DIR / f"{stem}.cs").read_text(encoding="utf-8")
        assert "IElementalCard" not in text, stem
        assert "KleeKeywords.AppliesHydro" in text, stem
    assert "ProtoKkSangoIsshin" not in carriers


def test_a_skill_grade_row_whose_damage_is_branch_gated_is_elemental():
    """THE PARITY HALF OF `EB-378`. The sim decides per EFFECT at resolution
    (`effects._element_for` asks `fx["op"] == "damage"` of whatever op is
    resolving); this generator asks the CARD once, off a scan that read the top
    level only. `Take It From the Top` -- Block 5, then 10 damage inside
    `spotlight_moved_this_turn` -- was elemental in the sim and carried no
    `IElementalCard` in the mod, so the branch applied a Hydro aura in one
    engine and nothing in the other.

    SEEN TO FAIL: with the old top-level walk this returns False.
    """
    row = {"id": "x", "type": "skill",
           "effects": [{"op": "block", "amount": 5},
                       {"op": "conditional", "if": "y",
                        "then": [{"op": "damage", "amount": 10,
                                  "target": "enemy"}]}]}
    assert gen.FURINA_PROFILE.damage_applies_element(row) is True
    text = (gen.FURINA_PROFILE.out_dir / "TakeItFromTheTop.cs").read_text(
        encoding="utf-8")
    assert "IElementalCard" in text
    assert "KleeKeywords.AppliesHydro" in text
