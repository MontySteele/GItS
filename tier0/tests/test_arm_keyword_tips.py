"""`EB-272`: every arm keyword a prototype face prints carries its definition.

THE DEFECT THIS PINS. Not one word the three quarantined arms invented had a
tooltip -- in the game or on the blind-play page -- while every shipped keyword
beside them did. [USER] hit it on the dev build ("Set Off has no tooltip
text"); both Kokomi seats in round one inferred `Exert` from watching their own
HP drop; and the Casket's `Mend` read as broken at full HP because the entry-HP
bound is enforced in `KokomiRules.Mend` and was printed nowhere.

WHY A TEST AND NOT ONLY A LINT. The failure is invisible by construction: a
missing hover tip renders as NOTHING AT ALL -- no wrong number, no exception,
no visual seam -- so it can only be caught by a machine that knows the join.
That is the same argument `tools/lint_keyword_meters.py` makes for Charge and
Burst, and these keywords take the join one turn tighter: the attach reads the
`[gold]...[/gold]` SPAN rather than the bare word, because `EB-258`'s golding
discipline means an arm keyword is always a keyword on a face.

FOUR HALVES, and each of them can fail on its own:
  1. the attach rule itself (`gen.arm_keyword_tip_calls`), with its ONE
     exclusion driven both ways;
  2. the committed generated tree obeys it, with non-vacuous denominators;
  3. the C# side answers for every row of the table -- a `For<Word>` method
     and a registered `.title` row, which is what stops a keyword rendering as
     the raw loc key (0.2-589, 0.2-634);
  4. the wire's keyword rows reach the BLIND PAGE, under the card face, the
     way `Applies Pyro` already does.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import gen_klee_cards as gen                    # noqa: E402
import gen_prototype_cards as proto             # noqa: E402

from understudy import blindplay                # noqa: E402

CARD_ROOT = REPO / "klee-mod" / "KleeCode" / "Cards"
PROTOTYPE_DIR = CARD_ROOT / "Prototype" / "Generated"
TIPS_CS = CARD_ROOT / "Prototype" / "ArmKeywordTips.cs"
MOD_CS = REPO / "klee-mod" / "KleeCode" / "KleeMod.cs"

# The shipped generated trees. Nothing here may reference the arm tips: on a
# shipped sheet `[gold]Bombs[/gold]` means the SHIPPED Bomb, whose rules are the
# opposite ones.
SHIPPED_DIRS = (CARD_ROOT / "Generated",
                CARD_ROOT / "Furina" / "Generated",
                CARD_ROOT / "Kokomi" / "Generated")

_DESCRIPTION = re.compile(r'\("description", (.*?)\),\n', re.S)


def _descriptions(text: str) -> list[str]:
    return _DESCRIPTION.findall(text)


def _prototype_files() -> list[Path]:
    return sorted(PROTOTYPE_DIR.glob("*.cs"))


# ---------------------------------------------------------------- the rule --

def test_the_rule_reads_the_golded_span_and_not_the_bare_word():
    """`Battle Plan`'s NAME is not the `Plan` verb, and "mine" is not `Mine`."""
    assert gen.arm_keyword_tip_calls("Battle Plan. Deal 5 to the mine.") == []
    assert gen.arm_keyword_tip_calls("[gold]Plan[/gold]: gain 2 Energy.") == [
        "ArmKeywordTips.ForPlan"]


def test_a_hole_inside_a_golded_span_is_not_part_of_the_word():
    """The badge prints `[gold]Mine{Mines:plural:|s}[/gold]`."""
    assert gen.arm_keyword_tip_calls(
        "[gold]Mine{Mines:plural:|s}[/gold] on every enemy.") == [
            "ArmKeywordTips.ForMine"]


def test_plurals_are_the_same_keyword():
    assert (gen.arm_keyword_tip_calls("[gold]Bombs[/gold] grow by 4.")
            == gen.arm_keyword_tip_calls("[gold]Bomb[/gold] 5."))
    assert (gen.arm_keyword_tip_calls("The pulse [gold]Mends[/gold] 3.")
            == ["ArmKeywordTips.ForMend"])


def test_a_face_naming_several_keywords_owes_several_tips_in_table_order():
    """TABLE ORDER, not face order, and the pair below is what shows it: the
    face names Mend first and the table lists Bomb first."""
    calls = gen.arm_keyword_tip_calls(
        "[gold]Mend[/gold] 10. Place a [gold]Bomb[/gold] dealing 5.")
    assert calls == ["ArmKeywordTips.ForBomb", "ArmKeywordTips.ForMend"]


def test_the_shipped_bomb_keeps_its_own_definition_and_the_arm_stands_down():
    """THE ONE EXCLUSION, driven both ways.

    A row that places a SHIPPED `BombPower` already carries `KLEEMOD-BOMB`,
    whose rules are the opposite of the arm's. Both tips are titled "Bomb", so
    raising both would let the game's de-duplication pick which definition of
    one word a player reads.
    """
    face = "Place a [gold]Bomb[/gold] dealing 5. Gain 1 [gold]Spark[/gold]."
    assert gen.arm_keyword_tip_calls(face, includes_bomb_rules=False) == [
        "ArmKeywordTips.ForBomb", "ArmKeywordTips.ForSpark"]
    # The shipped-Bomb row loses the Bomb tip and KEEPS the Spark one: Spark
    # has no shipped card-side definition on either arm.
    assert gen.arm_keyword_tip_calls(face, includes_bomb_rules=True) == [
        "ArmKeywordTips.ForSpark"]


# ------------------------------------------- EB-372: Grounded travels too --
#
# THE FINDING. `Grounded` is a Power card of Klee's, and Kaeya's Cold-Blooded
# Strike is written against it by name -- "Next turn, Grounded triggers even
# if you played a Set off card"
# as on the field" (`EB-576`) -- as is the buff that card leaves behind.
# A seat that drafted Kaeya and never drafted Grounded met the word on a card
# face with nothing on the screen saying what it is, and read it as noise in
# both acts (r9 act 1 sec.(c) 3, act 2 sec.(c) 2).
#
# THE FIX IS THE TABLE, which is what makes it travel: the attach is derived
# from the printed face, so the definition rides every face that prints the
# word whether or not the run holds the Power.


def test_the_grounded_word_owes_its_definition_wherever_it_is_printed():
    # TWO WORDS SINCE `EB-749`, and that is the table working rather than a
    # widened claim: the corrected clause names `Set off` as well as
    # `Grounded`, so the face that prints both owes both definitions. A reader
    # meeting Kaeya without Klee's kit needs the second sentence exactly as
    # much as the first.
    assert gen.arm_keyword_tip_calls(
        "Next turn, [gold]Grounded[/gold] triggers even if you played a "
        "[gold]Set off[/gold] card.") == ["ArmKeywordTips.ForSetOff",
                                          "ArmKeywordTips.ForGrounded"]
    # The bare word in prose is not the keyword, the rule every row here is
    # under: the span has to be golded.
    assert gen.arm_keyword_tip_calls("This turn, Grounded counts nothing.")         == []


def test_kaeyas_face_carries_the_grounded_tip_in_the_shipped_generation():
    """The card the seat was actually holding, read off the emitted C# rather
    than off the rule that emits it.

    Seen to FAIL: the row's face printed the word bare, so the derived attach
    had nothing to fire on and the card carried no definition.
    """
    card = (PROTOTYPE_DIR / "ProtoMcKaeyaColdBloodedStrike.cs").read_text(
        encoding="utf-8")
    assert ("Next turn, [gold]Grounded[/gold] triggers even if you played a "
            "[gold]Set off[/gold] card.") in card
    assert "ArmKeywordTips.ForGrounded(" in card


def test_the_buff_kaeyas_card_leaves_behind_carries_it_too():
    """The card is gone by the time the buff is read, and the buff is the only
    thing on screen naming the word for the rest of that turn."""
    power = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
             / "CompanionStandIns.cs").read_text(encoding="utf-8")
    head = power.index("class ColdBloodedPower")
    body = power[head:power.index("class LionsFangPower")]
    # The face's literal is split across two lines by the concatenation, so
    # the clause is asserted the way the source spells it.
    assert "Next turn, [gold]Grounded[/gold] triggers even if you played a "         in body
    assert "ArmKeywordTips.ForGrounded(base.ExtraHoverTips)" in body


def test_the_grounded_tip_states_the_condition_and_defers_on_the_payout():
    """The CONDITION is the whole rule a Kaeya reader needs. What Grounded
    pays is the Power card's own printed line and moves with its upgrade, so
    the tip must not quote a number a second card would contradict."""
    tips = TIPS_CS.read_text(encoding="utf-8")
    assert "that pays at the start of your turn, but " in tips
    assert ("only if you played no [gold]Set off[/gold] card last turn. "
            "Its ") in tips
    assert "card prints what it pays." in tips
    sheet = (REPO / "docs" / "prototype-surface.yaml").read_text(
        encoding="utf-8")
    # `EB-622`: the payout moved 6 -> 4 (upgrade still `+2`, so 6 upgraded).
    assert "gain 4 [gold]Block[/gold] and 1 [gold]Spark[/gold]" in sheet
    # `EB-749` (R271 sec.5.1): the sheet row's own condition, held in step
    # with the tip.
    assert ("if you played no [gold]Set off[/gold] card last turn, gain 4 "
            "[gold]Block[/gold]") in sheet


def test_the_attach_is_scoped_to_the_quarantined_surface():
    """A shipped profile must never carry the arm's contradicting sentence."""
    assert gen.KLEE_PROFILE.arm_keyword_tips is False
    assert gen.FURINA_PROFILE.arm_keyword_tips is False
    assert gen.KOKOMI_PROFILE.arm_keyword_tips is False
    assert proto.DIR_PROFILE.arm_keyword_tips is True
    for character in sorted(gen.PROFILES):
        assert proto._profile_for(character).arm_keyword_tips is True


def test_every_klee_companion_carries_the_kits_spark_rider():
    """`EB-418`, the committed tree, retargeted by R276 pick 2. Every Companion
    row on Klee's profile carries `ForCovenSpark`, and no other row does.

    THE DENOMINATOR IS THE POINT. The trigger is keyed on the SET
    (`effects.klee_companion_spark`, `KleeCompanionSpark`), and R276 made the
    set "any Companion card", so the sentence has to reach every companion row
    Klee's profile emits, or the next row added is the r11 seat's finding
    again.

    2026-09-23: UNDER THE ARM THE RIDER PRINTS NOTHING, because no Companion
    play pays there any more; `ForCovenSpark` returns its inherited tips at
    runtime (`HexereiReaderTests`), so the call is still emitted on every
    row for the off-arm world this test pins.

    GOROU IS THE NEGATIVE CASE, and he is a real one: he is a Personal
    Companion of KOKOMI'S on this same sheet, and Sparks are Klee's resource
    with no surface of Kokomi's to read them off. The sentence is scoped to the
    kit that declared it.
    """
    owed, carried = set(), set()
    for row in proto._rows():
        if not gen.is_companion(row):
            continue
        cls = gen.pascal(row["id"])
        if row.get("character") == "klee":
            owed.add(cls)
        path = PROTOTYPE_DIR / f"{cls}.cs"
        if path.exists() and "ForCovenSpark" in path.read_text(encoding="utf-8"):
            carried.add(cls)

    assert owed, "no Klee Companion on the sheet is not a read"
    assert owed == carried
    assert "ProtoMiGorouCrystalCollapse" in {
        gen.pascal(r["id"]) for r in proto._rows()
        if gen.is_companion(r) and r.get("character") == "kokomi"}
    assert "ProtoMiGorouCrystalCollapse" not in carried


def test_no_face_prints_a_family_mark():
    """R276 pick 2 retired the Hexerei mark, and `EB-642` had retired "Klee's
    own" before it: no generated prototype face prints either, and no card
    attaches a Hexerei tip. The readers print "Companion" instead."""
    for path in sorted(PROTOTYPE_DIR.glob("*.cs")):
        text = path.read_text(encoding="utf-8")
        faces = _descriptions(text)
        assert not any("Hexerei" in face for face in faces), path.name
        assert not any("Klee's own" in face for face in faces), path.name
        assert "ForHexerei" not in text, path.name
    for cls in ("ProtoKoCovenErrand", "ProtoKoWitchesCircle",
                "ProtoKoAlicesIntroductionMagic"):
        face, = _descriptions(
            (PROTOTYPE_DIR / f"{cls}.cs").read_text(encoding="utf-8"))[:1]
        assert "[gold]Companion[/gold]" in face, cls


def test_no_shipped_generated_card_reaches_the_arm_tips():
    offenders = [p.relative_to(REPO).as_posix()
                 for directory in SHIPPED_DIRS
                 for p in sorted(directory.glob("*.cs"))
                 if "ArmKeywordTips" in p.read_text(encoding="utf-8")]
    assert offenders == []


# ------------------------------------------- the committed generated tree --

@pytest.mark.parametrize("keyword", gen.ARM_KEYWORDS,
                         ids=[k.word for k in gen.ARM_KEYWORDS])
def test_every_prototype_face_printing_a_keyword_attaches_its_tip(keyword):
    """The join, over the files that actually ship to a dev build."""
    printed: list[str] = []
    missing: list[str] = []
    for path in _prototype_files():
        text = path.read_text(encoding="utf-8")
        owed = any(keyword.attach in gen.arm_keyword_tip_calls(
                       description, "includesBombRules: true" in text)
                   for description in _descriptions(text))
        if not owed:
            continue
        printed.append(path.stem)
        if f"{keyword.attach}(" not in text:
            missing.append(path.stem)
    assert missing == [], f"{keyword.word}: {missing}"
    # Non-vacuous: every row of the table is exercised by real faces, so a
    # scrape that silently read nothing could not pass this file.
    assert printed, f"{keyword.word}: no prototype face prints it"


def test_the_two_faces_the_row_names_render_their_keyword():
    """`EB-272`'s acceptance, by name: a *Set off* line and an *Exert* line.

    THE SET-OFF FACE MOVED, and the move is the point rather than an
    inconvenience. The row named Kaboom!, which under draft 2 said "Set off.
    Deal 6." Draft 3 (2026-09-02) made Kaboom! the PLAIN hit and Ka-pow! the
    cash button, so the keyword left one face and landed on the other. The tip
    follows the printed word, which is exactly the rule EB-272 built, so this
    now asserts BOTH ends of the move: Ka-pow! gained the line, and a row that
    does not print the word does not carry its definition.

    KABOOM! IS GONE (R242): draft 4 took the starter to the canonical shape and
    the plain hit left the sheet with Duck and Cover, so the negative half is
    now made on Pop!, which places a Bomb and never sets one off.
    """
    kapow = (PROTOTYPE_DIR / "ProtoKoKapow.cs").read_text(encoding="utf-8")
    assert "[gold]Set off[/gold]" in kapow
    assert "ArmKeywordTips.ForSetOff(" in kapow

    pop = (PROTOTYPE_DIR / "ProtoKoPop.cs").read_text(encoding="utf-8")
    assert "[gold]Set off[/gold]" not in pop
    assert "ArmKeywordTips.ForSetOff(" not in pop

    # THE KOKOMI HALF MOVED TOO, and further: draft 6 cut Exert with the rest
    # of draft 2's rules, so the row that carried the acceptance face is gone.
    # `Plan` is the keyword the arm has now, and Kurage's Oath -- a Plan-only
    # Skill under draft 6 -- is the row that prints it.
    oath = (PROTOTYPE_DIR / "ProtoKkKuragesOath.cs").read_text(encoding="utf-8")
    assert "[gold]Plan[/gold]" in oath
    assert "ArmKeywordTips.ForPlan(" in oath


def test_a_spark_priced_row_keeps_its_tip_without_the_sentence():
    """`EB-282` met `EB-272` head on. The Spark price came off the seven bodies
    because the cost slot already shows the badge -- and the tip rule is "the
    face PRINTS the word", so all seven silently lost the definition of the
    word they charge in. A price shown as a badge is still the keyword on the
    card, so the row's own `spend_spark` raises the tip instead."""
    # `EB-749` re-pointed two of the seven: Fwoosh! was cut and Powder Charge
    # became Booby Trap. R276 cut Sugar Rush, so Bottomless Bag takes the
    # seventh. Pocket Match lost its price on 2026-09-24; six remain.
    for stem in ("ProtoKoTinderToss", "ProtoKoQuickFuse",
                 "ProtoKoBangBang", "ProtoKoBoobyTrap", "ProtoKoDigIn",
                 "ProtoKoBottomlessBag"):
        text = (PROTOTYPE_DIR / f"{stem}.cs").read_text(encoding="utf-8")
        # The FACE, not the file: `SparkPower.CanSpend` is in every one of
        # these bodies and always was.
        face = re.search(r'\("description", "(.*)"\),', text).group(1)
        assert "Spend" not in face, stem
        assert "ArmKeywordTips.ForSpark(" in text, stem
        assert "PrintedSparkPrice" in text, stem

    # And it is a ROW-level fact rather than a blanket: a row that charges no
    # Sparks and prints none gains nothing. Kaboom! used to make this point and
    # left the sheet at R242; Pop! is the row that makes it now.
    pop = (PROTOTYPE_DIR / "ProtoKoPop.cs").read_text(encoding="utf-8")
    assert "ArmKeywordTips.ForSpark(" not in pop


def test_the_sparks_arms_bomb_rows_keep_the_shipped_definition():
    """SEEN, not asserted in the abstract: the three rows the exclusion drops
    are the three that place a shipped Bomb, and they still carry the shipped
    keyword and the arm's Spark tip."""
    # `EB-750` retired `ProtoPopSpark` and `ProtoPowderChargeSpark` with the
    # rest of the superseded Sparks pool; `ProtoSparkModeBombs` is the row of
    # the three that still exists, and it carries the same proof.
    for stem in ("ProtoSparkModeBombs",):
        text = (PROTOTYPE_DIR / f"{stem}.cs").read_text(encoding="utf-8")
        assert "includesBombRules: true" in text, stem
        assert "ArmKeywordTips.ForBomb(" not in text, stem
        assert "ArmKeywordTips.ForSpark(" in text, stem


# ----------------------------------------------------------- the C# side ---

def _key_const(keyword: gen.ArmKeyword) -> str:
    """`ArmKeywordTips.ForSetOff` -> `SetOffKey`."""
    method = keyword.attach.split(".", 1)[1]
    return method[len("For"):] + "Key"


@pytest.mark.parametrize("keyword", gen.ARM_KEYWORDS,
                         ids=[k.word for k in gen.ARM_KEYWORDS])
def test_every_table_row_has_a_method_and_a_registered_title_row(keyword):
    """A key with no `.title` row renders as the raw loc key on a card face --
    which shipped twice before `KleeSelfCheck` R20 existed (0.2-589, 0.2-634).
    This is that rule's python half, in the CI job that always runs."""
    tips = TIPS_CS.read_text(encoding="utf-8")
    method = keyword.attach.split(".", 1)[1]
    assert f"IEnumerable<IHoverTip> {method}(" in tips, keyword.word

    const = _key_const(keyword)
    assert re.search(rf'\bconst string {const} = "KLEEMOD-ARM_[A-Z_]+";',
                     tips), keyword.word
    assert f"ArmKeywordTips.{const} + \".title\"" in MOD_CS.read_text(
        encoding="utf-8"), keyword.word


# `EB-378` put ONE key in this file that titles no keyword: the Plan-element
# rider, which is a sentence about a card rather than a definition of a word.
# `EB-418` put the second, the Spark Klee's KIT mints on a play of one of her
# own Personal Companions -- a rule LAW:145 keeps off the Companion's face, so
# no word on any card can carry it. (`EB-553`'s third left with the retired
# reframe under `EB-726`.) They are named here so the count below stays a
# real pin instead of a number somebody bumps.
NON_KEYWORD_KEYS = {"KLEEMOD-ARM_PLAN_ELEMENT", "KLEEMOD-ARM_COVEN_SPARK",
                    # `EB-575`: the fourth rider here that titles no keyword,
                    # and the first whose sentence comes and goes with the
                    # board.
                    "KLEEMOD-ARM_EMPTY_FIELD",
                    # `EB-573`: what a merge keeps besides the Mine.
                    "KLEEMOD-ARM_MERGE_RIDERS",
                    # `EB-709`: how many Plans a doubled carry-out is, on the
                    # one card that doubles one. A per-Plan reader's own face
                    # states its rate truthfully; what no face said is that a
                    # card can make the queue longer than the queue looks.
                    "KLEEMOD-ARM_PLAN_TWICE",
                    # (`Encore` was the sixth until R276's hygiene: no card
                    # attached its tip, so the body and its key left.)
                    # A Stage round-three defect: WHICH BAR a reader's number
                    # is. Since the text pass only the Rare carries it: the
                    # other readers' faces name the seat outright.
                    "KLEEMOD-ARM_STAGE_READER",
                    # 2026-09-25: what a summon does and what each performer
                    # does. Faces print these words UNGOLDED ("Summon
                    # Usher"), so they attach off the `stage_summon` op
                    # (`gen.stage_summon_tip_calls`), not off the table.
                    "KLEEMOD-ARM_STAGE_SUMMON", "KLEEMOD-ARM_STAGE_USHER",
                    "KLEEMOD-ARM_STAGE_CHEVALMARIN",
                    "KLEEMOD-ARM_STAGE_CRABALETTA"}


def test_the_arm_keys_never_collide_with_a_shipped_keyword_id():
    """`Bomb` and `Swirl` are the same WORD under two different rules, so the
    keys must differ or the loc merge would let one arm overwrite the other."""
    tips = TIPS_CS.read_text(encoding="utf-8")
    keys = set(re.findall(r'"(KLEEMOD-[A-Z0-9_]+)"', tips))
    assert len(keys - NON_KEYWORD_KEYS) == len(gen.ARM_KEYWORDS)
    assert NON_KEYWORD_KEYS <= keys
    assert all(k.startswith("KLEEMOD-ARM_") for k in keys)
    assert "KLEEMOD-BOMB" not in keys
    assert "KLEEMOD-SWIRL_PREVIEW" not in keys


def test_the_merge_row_says_riders_survive_it():
    """`EB-573`. The rider the merge keeps, on the card that does the merging.

    THE FIND (Klee r21 lane 1, (c) 4). "A Bomb 21 that was Jumpy's Bomb 8 two
    merges and two turns ago still dropped Mine 3 on ALL when it went off. This
    is a GOOD interaction and a large part of the kit's ceiling, and it is
    completely undiscoverable except by accident."

    Seen to FAIL: Careful Arrangement's face promises "a Mine if any of them
    was" and says nothing about riders, and no badge counted one.
    """
    rows = {row["id"]: row for row in proto._rows()}
    mergers = {rid for rid, row in rows.items() if gen.merges_bombs(row)}
    assert mergers == {"proto_ko_careful_arrangement"}
    merge = (PROTOTYPE_DIR / "ProtoKoCarefulArrangement.cs").read_text(
        encoding="utf-8")
    assert "ArmKeywordTips.ForMergeRiders(" in merge
    # AND THE RIDER EXISTS TO SURVIVE: the one row that plants one.
    riders = {rid for rid, row in rows.items()
              if any(fx.get("payload_mine_all")
                     for fx in gen.iter_effects(row.get("effects") or []))}
    assert "proto_ko_jumpy_dumpty" in riders


def test_a_set_off_row_on_a_bare_board_says_so():
    """`EB-575`. The attach and which of the two sentences a row gets, both
    derived from the row's own effects.

    THE FIND (Klee r21 lane 1, (c) 2 and (c) 3). Careful Arrangement on a bare
    board and Fwoosh! on another were ACCEPTED (`EB-749` has since cut Fwoosh!;
    Pocket Match below is the same Spark-priced Set off shape): the Energy went, the Spark
    went, nothing resolved. On the same screen a Spark-priced card the bank was
    short for printed CANNOT BE PLAYED and named the price and the bank.

    Seen to FAIL: nothing on either face, in either engine, said the board was
    empty.
    """
    rows = {row["id"]: row for row in proto._rows()}
    # EVERY SET OFF AND THE MERGE, and nothing else.
    readers = {rid for rid, row in rows.items() if gen.reads_the_field(row)}
    assert "proto_ko_careful_arrangement" in readers
    assert "proto_ko_pocket_match" in readers
    assert "proto_ko_jumpy_dumpty" not in readers      # a placer reads nothing
    # THE TWO SENTENCES. A row with a line of its own still does that line; a
    # row that is nothing but the Bomb work does nothing whatever.
    blanks = {rid for rid in readers if not gen.empty_field_tip_arg(rows[rid])}
    # `EB-749`: Fireworks Show was CUT and merged into Tinder Toss, which has a
    # damage line of its own and is therefore not blank.
    # Hair Trigger reads the field but draws a card of its own (2026-09-23),
    # so it is no longer blank on a bare board.
    assert blanks == {"proto_ko_careful_arrangement", "proto_ko_the_big_one",
                      "proto_ko_quick_fuse"}
    # AND THE ATTACH REACHED THE EMITTED C#, with the derived argument on it.
    merge = (PROTOTYPE_DIR / "ProtoKoCarefulArrangement.cs").read_text(
        encoding="utf-8")
    assert "ArmKeywordTips.ForEmptyField(" in merge and ", this, false)" in merge
    match = (PROTOTYPE_DIR / "ProtoKoPocketMatch.cs").read_text(encoding="utf-8")
    assert "ArmKeywordTips.ForEmptyField(" in match and ", this, true)" in match


def test_the_merge_clause_is_on_the_tip_and_the_page():
    """`EB-287`, the glossary half (proofs-9 lane 0, A2, 2026-09-16).

    THE DEFECT. `ForBomb` carried "; a second Bomb joins the first." and the
    blind page's own `Bomb` glossary row did not -- and the two print on ONE
    screen, the tip on the card rail and the row twenty lines below it. So the
    reader the keyword exists for, the one who has not built a pile yet, met
    one surface saying a second placer joins the charge and another that never
    mentioned it. The row's acceptance names both surfaces.

    A PIN AND NOT A SHARED CONSTANT, and the reason is structural: the tip is a
    C# literal compiled into the mod, the glossary row is a Python string in a
    process that reads the WIRE and never loads the assembly -- and that
    renders pages on builds carrying no klee mod at all. Nothing can be read by
    both at run time, so the agreement is asserted here, at the only place that
    sees both files. That is `test_rule_three_...`'s shape, one surface out.

    Seen to FAIL on the live look: `Bomb 9` on the badge, the merge on the tip,
    and the glossary row silent about it.
    """
    import sys
    sys.path.insert(0, str(REPO))
    from tools import lint_text_conventions as ltc
    from understudy import blindplay_notes

    clause = "; a second Bomb stacks beside the first, and a Mine among them goes off alone. "
    tips = {row.ident: ltc.render(row.raw) for row in ltc.tip_rows()}
    assert clause in tips["BombKey"]
    # The same words in the same place on the page: the clause hangs off what
    # a charge IS, and `Block stops it.` still follows it.
    page = blindplay_notes.ARM_KEYWORDS["Bomb"]
    assert clause in page
    assert page.index(clause) < page.index("Block stops it.")
    # The clause carries no `[gold]` span, so the two readings are identical
    # character for character rather than one being the other's paraphrase.
    assert "[gold]" not in clause


def test_rule_three_says_which_kill_it_means_on_all_three_surfaces():
    """`EB-574`. The sentence is about the BODY, not the charge.

    "Kills move it on" (Bomb tip) and "a kill moves them to a survivor" (the
    badge) both read as a promise about the charge that does the killing, and
    the badge prints its copy on the body the pile is about to kill -- which is
    exactly where that reading is invited. The r21 lane-1 seat set off Mine 11,
    killed Toadpole B, saw nothing arrive on A and filed the screen as
    contradicting itself.

    Seen to FAIL: the Mine tip carried no jump clause at all, so the surface a
    Mine reader stands in front of said nothing about the rule.
    """
    import sys
    sys.path.insert(0, str(REPO))
    from tools import lint_text_conventions as ltc
    tips = {row.ident: ltc.render(row.raw) for row in ltc.tip_rows()}
    sentence = "If the enemy dies with it on, it moves to a survivor."
    assert sentence in tips["BombKey"]
    assert sentence in tips["MineKey"]
    # The badge speaks of a PILE, so the same claim in the plural.
    badge = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
             / "ProtoBombPower.cs").read_text(encoding="utf-8")
    assert (' " If the enemy dies with them on, they move to a '
            'survivor.";') in badge
    # And the old wording is gone from every one of the three.
    assert "Kills move it on" not in tips["BombKey"]
    assert '" A kill moves them to a survivor.";' not in badge


def test_the_ruled_sentences_are_the_ones_that_ship():
    """The wording pin. Every clause below is quoted from the ruled slice
    packets; `Mend`'s bound is the one `EB-272` names outright."""
    tips = TIPS_CS.read_text(encoding="utf-8")
    for clause in (
            # Klee, klee-overhaul-slice-1-2026-09-01.md sec.2 rules 1/2/4/6,
            # in the shape docs/current/text-conventions.md sets (one clause
            # per sentence, under the keyword-tip ceiling).
            #
            # `EB-343` (R248) gave the Bomb a FOURTH rule -- a Bomb takes the
            # enemy's debuffs and none of Klee's -- and the word was REWRITTEN
            # rather than extended ([USER], PR #340): four sentences carrying
            # four rules would have run 60 characters over the tip ceiling, and
            # the ceiling is the base game's own longest mechanic tip on the one
            # word a seat reads every turn. All four rules are still here in
            # two sentences, and the tip takes no length exception.
            #
            # `EB-373` REWROTE THE LAST CLAUSE. The fold is `FoldedMods` and
            # it reads two things off the target -- Vulnerable and whichever
            # power sets the lowest damage cap -- so "takes the enemy's
            # debuffs" was a promise the code does not keep; a Bomb's hit is
            # not an Attack, which is what the clause leads with now.
            # `EB-361` ADDED A FIFTH RULE in the same 135 characters: a Bomb
            # whose enemy dies moves to a survivor at its size, which three
            # round-10 seats met as a stack they could not account for. Rule
            # 2's "all at once" (the `Set off` clauses state it in full),
            # "their" and "to a survivor" paid for it: 133 rendered.
            "A charge on an enemy: grows ",
            # `EB-536`: the Mine joins the sentence, because the Mine tip
            # printed under it says a Mine also goes off before its enemy's
            # hit and the two contradicted each other on one screen.
            " a turn, and goes off when [gold]Set off[/gold] or as a ",
            # `EB-287` (the live look of 2026-09-16): the MERGE, which was
            # stated on the enemy badge of a pile that already exists and
            # nowhere a reader who has not built one could meet it. A CLAUSE
            # and not a sentence, because the tip is at the base game's
            # four-sentence cap and a fifth would displace a ruled finding.
            "[gold]Mine[/gold]",
            "; a second Bomb stacks beside the first, and a Mine among them goes off alone. ",
            # `EB-555` defined the cap inside the clause that names it.
            # `EB-400`: Block, named in the clause that read as a list of
            # the only two things that touch the hit.
            "[gold]Block[/gold] stops it. Only ",
            "[gold]Vulnerable[/gold] and the HP cap move it. ",
            # `EB-574` SPELT RULE 3 OUT, in the same words on both tips and
            # the badge: "kills move it on" read as a promise about the charge
            # doing the killing, and the r21 lane-1 seat set off Mine 11,
            # killed Toadpole B and saw nothing arrive on A.
            "If the enemy dies with it on, it moves to a survivor.",
            # `EB-432` named the order INSIDE the pile: `SetOff` walks the
            # charges in placement order and the first one meets the aura,
            # because a reaction consumes it. "Oldest first" carries "one at a
            # time" -- an order that names a first and a rest is one at a time
            # -- and `EB-287`'s "together" claim is now the subject.
            # `EB-443` added Block and the Attack trigger, and "for its
            # size" paid for them: a tip is read in hand where there is no
            # pile to quote, so the live number stays on the badge.
            # `EB-490` RENAMED THE CLASS AND NOT THE CLAIM, in the same
            # fourteen characters: "Attack trigger" reads as something on the
            # player's own side of the board, and the r16 seat read it that
            # way beside a Block clause pointing the other direction.
            # `EB-755` (R276): "in the order placed" says which of two Bombs
            # placed in one turn goes first, which "oldest first" did not.
            "The target's [gold]Bombs[/gold] go off first, in the order placed, ",
            # `EB-516` ADDED THE AIM, and it is on the WORD because the two
            # rows that roll (Tinder Toss, Rapid Fire) print only "a random
            # enemy" and cannot say where it lands.
            "each a Pyro hit. [gold]Block[/gold] stops them, no when-hit power ",
            "fires, the first takes the aura. A random one picks a Bombed ",
            "enemy first.",
            "Some cards cost [gold]Sparks[/gold] instead of Energy, with no cap. ",
            "Start each combat with ",
            "Gone after combat.",
            # `EB-436`: the clause said WHEN and nothing about the attack,
            # and a seat read mitigation into it. A Mine blunts nothing; the
            # only thing it can do to the hit is stop it happening.
            "that also goes off just before its enemy's ",
            "hit, and the hit still lands unless the Mine kills. ",
            # The Mine's last two sentences are `ForBomb`'s WORD FOR WORD
            # after the 2026-09-08 trim -- `EB-373`'s two terms, `EB-400`'s
            # Block and `EB-574`'s rule 3 -- so they are pinned once above
            # and a Mine reader and a Bomb reader cannot be told two things.
            # Kokomi, kokomi-overhaul-slice-1-2026-09-01.md DRAFT 6 sec.2.
            # Two keywords, not six: draft 6 cut Tide, Surge, Exert and the
            # Garment, and their four sentences left with them.
            #
            # THE 2026-09-25 TEXT PASS rewrote the Plan word to two short
            # sentences ("the existing text is often very verbose and
            # unintuitive"): 292 rendered characters of seat edge cases came
            # off it, and the panel keeps the long forms. Spec and census:
            # review/records/text-pass-2026-09-25/.
            "Play the card on the [gold]Bake-Kurage[/gold] and this happens ",
            "at the start of your next turn. Plans are carried out in the ",
            "order you made them.",
            "heal N HP, never above the HP you entered ",
            # Furina, THE STAGE (`EB-723`; the brief's sec.12 names the
            # seven words and sec.3 states each rule). The reframe's four --
            # Deploy, Evoke, Drain, Encore -- left this list with the eleven
            # `proto_fr_` rows that printed them, under R213 B's deletion rule:
            # a ruled sentence for a word no row prints is a rule nobody can
            # meet. What is here instead is the SEVEN, and each carries the
            # half of its rule a player cannot infer -- rule 8's "fires in full
            # even if the bar is short", rule 6's damage order, rule 5's "with
            # one performer that is the lead", rules 7-and-9's difference
            # between a bow and a death, and rotation's refusal of both.
            # `EB-746`: a mode the player chooses, not a rider the engine
            # fires whenever a lead stands. R276 picks 1 and 2: the BACK
            # performer pays, in full or not at all, and an exact emptying
            # bows.
            # THE TEXT PASS (2026-09-25,
            # review/records/furina-text-pass-2026-09-25.md): `Raise` and
            # `Rotate` retired, the lead renamed the FRONT performer, and
            # every Stage tip reworded in [USER]'s words.
            "Pay Fanfare from your [gold]back performer[/gold]. Offered only ",
            "if it can pay in full. If that empties it exactly, it ",
            "A performer's health. Hits take your [gold]Block[/gold], then ",
            "the front performer's, then you. Gained on an empty stage, it ",
            "summons a performer.",
            # `EB-744`: the CONTRAST -- a Spend earns a Bow, a hit does not.
            "A performer's parting effect, shown on each performer. Spending ",
            "its last Fanfare triggers it; losing it to a hit doesn't.",
            "Takes hits first. Regains ",
            " [gold]Fanfare[/gold] at the start of your turn.",
            # Round four's empty-stage summon is the Fanfare tip's (above).
            "Gains and Spends [gold]Fanfare[/gold]. Hits reach it last.",
    ):
        assert clause in tips, clause


def test_the_mend_tip_carries_the_entry_hp_bound():
    """THE ROW'S SECOND HALF. The Casket read as broken at full HP because
    nothing on screen said there was a ceiling; the sentence is
    `KokomiRules.Mend`'s own."""
    tips = TIPS_CS.read_text(encoding="utf-8")
    assert "never above the HP you entered " in tips
    assert "the fight with." in tips

    rule = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
            / "ProtoBakeKuragePower.cs").read_text(encoding="utf-8")
    assert "never above the HP you entered the" in rule


def test_the_numerals_are_interpolated_from_the_arms_law():
    """`EB-89`: a retune must not be able to leave a tip quoting a retired
    number. The two sentences that carry a number read the constant."""
    tips = TIPS_CS.read_text(encoding="utf-8")
    assert "KleeOverhaulLaw.BombGrowth" in tips
    assert "KleeOverhaulLaw.SparkPerExplosion" in tips
    # THE STAGE's Bow and lead sentences carry three numbers -- the two bows
    # that have one and the lead's regen -- and all three are prototype SEEDS
    # (R215 B, the brief's sec.10 default 3), which makes a retune likelier
    # here than anywhere else on this list. `EB-723` replaced the reframe's
    # Evoke pair, which left with that arm's rows.
    assert "FurinaStageLaw.BowUsherBlock" in tips
    assert "FurinaStageLaw.BowCrabalettaDamage" in tips
    assert "FurinaStageLaw.LeadRegen" in tips
    # Kokomi's two draft-6 sentences carry no number at all: the Plan rule is
    # structural and the Mend rule's bound is her entry HP, not a constant.
    # The arm's one number lives on the relic, whose face interpolates it
    # (`KokomiOverhaulLaw.CasketStrike`, TamakushiCasket.cs).
    casket = (REPO / "klee-mod" / "KleeCode" / "Relics"
              / "TamakushiCasket.cs").read_text(encoding="utf-8")
    assert "KokomiOverhaulLaw.CasketStrike" in casket


def test_the_tips_are_quarantined_out_of_a_release_build():
    """The file lives where `KleeCode.csproj` removes it, and its title rows
    are inside the same switch."""
    assert TIPS_CS.parent.name == "Prototype"
    mod = MOD_CS.read_text(encoding="utf-8")
    head = mod.index("ArmKeywordTips.BombKey")
    tail = mod.index("ArmKeywordTips.SwirlKey")
    # The nearest switch ABOVE the rows, not the file's first one (Rally's
    # selection prompt opens an earlier block of its own).
    assert mod.rindex("#if PROTOTYPE_CARDS", 0, head) > mod.index(
        "KleeCardTooltips.BurstKey")
    assert "#endif" in mod[tail:]


# ------------------------------------------------------- the blind page ----

SET_OFF_TIP = {
    "name": "Set off",
    "description": ("Every Bomb on the target goes off, one at a time, each a "
                    "Pyro hit for its size, before the rest of the card."),
}

EXERT_TIP = {
    "name": "Exert",
    "description": ("Exert N: on Skills and Powers only, never Attacks. "
                    "Lose N HP, Block first."),
}


#: `EB-418`. The rider the kit's Spark rule rides, in the shape the bridge
#: sends it: `KleeMod.cs` titles the key and `ArmKeywordTips.ForCovenSpark`
#: builds the body, so a seat reading a Companion in hand reads the income
#: before it commits the energy.
COVEN_SPARK_TIP = {
    "name": "Sparks from your Companion",
    "description": ("Playing a Companion card gives Klee 1 Spark, 1 more if "
                    "it triggered an Elemental Reaction and 1 more if it is "
                    "upgraded."),
}


def _hand_with(tips: list[dict]) -> dict:
    """The recorded combat wire, with one hand card carrying arm keywords.

    The keyword ROWS are the shape the bridge already sends -- `name` plus
    `description`, built by `BuildHoverTips` off `card.HoverTips`, which is the
    list `ExtraHoverTips` feeds. The recorded fixture proves that path is real:
    its `All Streams Flow to the Sea` carries a `Charge scaling` row that only
    `KokomiRiderTips.ForChargeRider` can have put there.
    """
    from tier0.tests.test_understudy_blindplay import combat_state
    state = combat_state()
    # `EB-753`: `Set off` is Klee's word and the glossary is scoped to the arm
    # the run's character owns, so the board this card is dealt onto is hers.
    state["player"]["character"] = "Klee"
    card = state["player"]["hand"][0]
    card["name"] = "Kaboom!"
    card["description"] = "Set off. Deal 6 damage."
    card["keywords"] = tips
    return state


def test_the_wire_s_keyword_rows_survive_into_the_observation():
    obs = blindplay.observation(_hand_with([SET_OFF_TIP]))
    hand = obs["combat"]["hand"]
    assert hand[0]["keywords"] == [
        {"name": "Set off", "text": SET_OFF_TIP["description"]}]


def test_the_blind_page_prints_the_set_off_definition_under_the_card():
    page = blindplay.observe(_hand_with([SET_OFF_TIP]))
    assert "*Set off* — " + SET_OFF_TIP["description"] in page


def test_the_blind_page_prints_the_exert_definition_under_the_card():
    """The Kokomi arm's half of the same pin: two seats inferred this rule
    from losing HP because the page carried no line for it."""
    page = blindplay.observe(_hand_with([EXERT_TIP]))
    assert "*Exert* — " + EXERT_TIP["description"] in page


def test_the_blind_page_prints_the_kits_companion_spark_under_the_card():
    """`EB-418`'s page twin. The r11 seat read every screen this page draws and
    could not name the Spark it watched arrive; the rider now travels with the
    Companion, and the page carries a card's keyword rows verbatim."""
    page = blindplay.observe(_hand_with([COVEN_SPARK_TIP]))
    assert "*Sparks from your Companion* — " + COVEN_SPARK_TIP["description"]         in page


def test_a_card_with_no_keyword_row_prints_no_keyword_line():
    """SEEN TO FAIL: the state this row was filed against. The face is
    identical and the CARD LINE is simply absent -- this page invents no tip
    for a card whose wire row carries none, which is the non-vacuous
    denominator the three tests above need.

    `EB-272`'s second half narrowed what "absent" means here rather than
    weakening it. The card's own indented `*Set off* — ...` line still comes
    from the wire and from nowhere else; what the screen now also carries is
    ONE definition of the word, once, in its own section, because a body that
    prints an arm keyword reaches a reader who has never met it whether or not
    the tip happened to ride on that particular card. The two are different
    lines in different places and this asserts both.
    """
    page = blindplay.observe(_hand_with([]))
    assert "Kaboom!" in page
    assert "    *Set off* — " not in page
    assert "- **Set off** — " in page.split("## Words on this screen")[1]


# ------------------------------------------ `EB-377`: the base game's words --
#
# THE SECOND HALF OF THE SAME GAP. `EB-272` gave every word the arms INVENTED a
# definition on the face that prints it; the words the arms merely USE still had
# none. The round-9 Kokomi seat read `Weak`, `Frail`, `Slow` and `Minion`
# correctly defined and `Vulnerable` defined on no screen at all -- because
# those four arrive as POWERS on a body, carrying the game's own hover tip, and
# a card that APPLIES one carries nothing. `Exposed Flank+` was bought on a
# genre assumption for exactly that reason (r9 run 2, act 1, (c) 6).

BASE_TIPS_CS = CARD_ROOT / "Prototype" / "BaseKeywordTips.cs"


@pytest.mark.parametrize("keyword", gen.BASE_KEYWORDS,
                         ids=[k.word for k in gen.BASE_KEYWORDS])
def test_every_prototype_face_printing_a_base_keyword_attaches_its_tip(
        keyword):
    """The join, over the files that actually ship to a dev build.

    NON-VACUITY IS ASSERTED ONCE, BELOW, RATHER THAN PER ROW: unlike the arm
    table, this one carries a word no face prints today (`Frail`), and it
    carries it on purpose -- the attach is DERIVED, so the row is what makes a
    face that prints it tomorrow carry its definition without anybody
    remembering to add one.
    """
    missing = [path.stem for path in _prototype_files()
               if any(keyword.attach in gen.base_keyword_tip_calls(description)
                      for description in _descriptions(
                          path.read_text(encoding="utf-8")))
               and f"{keyword.attach}(" not in path.read_text(encoding="utf-8")]
    assert missing == [], f"{keyword.word}: {missing}"


def test_the_four_base_words_the_surface_prints_are_exercised():
    """The denominator. A scrape that silently read nothing would pass the
    parametrised join above and fail here."""
    printed = {keyword.word
               for path in _prototype_files()
               for description in _descriptions(
                   path.read_text(encoding="utf-8"))
               for keyword in gen.BASE_KEYWORDS
               if keyword.attach in gen.base_keyword_tip_calls(description)}
    assert printed == {"Vulnerable", "Weak", "Strength", "Dexterity"}


def test_the_row_the_defect_was_filed_against_carries_the_vulnerable_tip():
    """`Exposed Flank`, by name, and it keeps its Plan tip: the two words on
    that face are two definitions and the card owes both."""
    flank = (PROTOTYPE_DIR / "ProtoKkExposedFlank.cs").read_text(
        encoding="utf-8")
    assert "[gold]Vulnerable[/gold]" in flank
    assert "BaseKeywordTips.ForVulnerable(" in flank
    assert "ArmKeywordTips.ForPlan(" in flank


def test_the_base_rule_reads_the_golded_span_and_not_the_bare_word():
    """`ArmKeywordTips`' rule, unchanged: `EB-258`'s golding discipline means
    a keyword on a face is always a `[gold]` span, so prose can never raise
    one."""
    assert gen.base_keyword_tip_calls(
        "This enemy is weak to fire and strength of will.") == []
    assert gen.base_keyword_tip_calls(
        "Apply 2 [gold]Vulnerable[/gold].") == [
            "BaseKeywordTips.ForVulnerable"]
    assert gen.base_keyword_tip_calls(
        "Apply 1 [gold]Weak[/gold]. Gain 2 [gold]Strength[/gold].") == [
            "BaseKeywordTips.ForWeak", "BaseKeywordTips.ForStrength"]


def test_no_shipped_generated_card_reaches_the_base_tips():
    """Quarantined with its sibling. Eighty release faces print `Weak`, and
    widening the attach to them is a change to the SHIPPED surface."""
    offenders = [p.relative_to(REPO).as_posix()
                 for directory in SHIPPED_DIRS
                 for p in sorted(directory.glob("*.cs"))
                 if "BaseKeywordTips" in p.read_text(encoding="utf-8")]
    assert offenders == []


@pytest.mark.parametrize("keyword", gen.BASE_KEYWORDS,
                         ids=[k.word for k in gen.BASE_KEYWORDS])
def test_every_base_row_has_a_method_and_a_registered_title_row(keyword):
    """A key with no `.title` row renders as the raw loc key on a card face."""
    tips = BASE_TIPS_CS.read_text(encoding="utf-8")
    method = keyword.attach.split(".", 1)[1]
    assert f"IEnumerable<IHoverTip> {method}(" in tips, keyword.word

    const = _key_const(keyword)
    assert re.search(rf'\bconst string {const} = "KLEEMOD-BASE_[A-Z_]+";',
                     tips), keyword.word
    assert f"BaseKeywordTips.{const} + \".title\"" in MOD_CS.read_text(
        encoding="utf-8"), keyword.word


def test_the_base_keys_never_collide_with_an_arm_key():
    """Two tables, two prefixes. A shared key would let one definition
    overwrite the other at the loc merge."""
    base = set(re.findall(r'"(KLEEMOD-[A-Z0-9_]+)"',
                          BASE_TIPS_CS.read_text(encoding="utf-8")))
    arm = set(re.findall(r'"(KLEEMOD-[A-Z0-9_]+)"',
                         TIPS_CS.read_text(encoding="utf-8")))
    assert len(base) == len(gen.BASE_KEYWORDS)
    assert all(k.startswith("KLEEMOD-BASE_") for k in base)
    assert not base & arm


def test_the_base_tips_are_quarantined_out_of_a_release_build():
    """The file lives where `KleeCode.csproj` removes it, and its title rows
    are inside the same `#if PROTOTYPE_CARDS` switch the arm rows are."""
    assert BASE_TIPS_CS.parent.name == "Prototype"
    mod = MOD_CS.read_text(encoding="utf-8")
    head = mod.index("BaseKeywordTips.VulnerableKey")
    assert mod.rindex("#if PROTOTYPE_CARDS", 0, head) > mod.index(
        "KleeCardTooltips.BurstKey")
    assert "#endif" in mod[mod.index("BaseKeywordTips.DexterityKey"):]


# ------------------------------ `EB-377`: no page names a word it defines not --

_GOLD_SPAN = re.compile(r"\[gold\](.*?)\[/gold\]")

# THE CURATED HALF, and it is curated because the alternative is a test that
# proves nothing. Every entry is a word a prototype face golds and the page
# owes no glossary row for, with the reason it owes none. A word that is
# neither here nor defined fails the test below, which is the whole point: a
# new face naming a new base keyword cannot ship silently, and adding a word
# here is a decision somebody has to write down.
NO_GLOSSARY_ROW_OWED = {
    # The four numbers the page prints on the player line every single turn.
    "Block": "the page prints the figure on the player line every turn",
    "Energy": "the page prints the figure on the player line every turn",
    "Exhaust Pile": "a zone the page prints by name, with its contents",
    # The elements. None is a glossary row and none should be: the element is
    # the card's own indicator (`blindplay_faces._element` puts it on the card
    # LINE), and every pairing it can make is a `REACTION_KEYWORDS` row on any
    # screen that shows one.
    "Pyro": "the card line carries the element; the reactions define the pairs",
    "Hydro": "the card line carries the element; the reactions define the pairs",
    "Electro": "the card line carries the element; the reactions define the pairs",
    "Cryo": "the card line carries the element; the reactions define the pairs",
    "Geo": "no card in this build supplies Geo, so no pairing is reachable",
    # A thing the card's own sentence names and then rules, in the same
    # sentence. Defining it a second line down would restate the face.
    "White": "the face's own mode, ruled in the clause that names it",
    "Dark": "the face's own mode, ruled in the clause that names it",
    "Lightfall Sword": "the face's own placed object, ruled in the next clause",
    "Sakura": "the face's own placed object, ruled in the next clause",
    "Bake-Kurage": "her pet, whose whole panel is a section of the page",
    "Tamakushi Casket": "a relic, printed with its own text in the relic list",
    # Furina's meters. All three are RESOURCES the page prints on the player
    # line with their amount and their maximum (`EB-181`'s `resource_info`),
    # which is the standing `Block` and `Energy` have, and the reframe's two
    # carry their own C# tips besides.
    "Fanfare": "a meter the page prints with its amount, and its own tips",
    "Salon": "the reframe's stage, named by the member tips on every face",
    "Encore": "a meter the page prints with its amount and its maximum",
}

# The words a per-card TIP defines, on the card that prints them, because the
# rule is arithmetic about that card and a glossary row could only restate the
# name. Each maps to the C# attach the codegen derives, and the test below
# proves the attach is really on a face that prints the word -- so an entry
# here is a claim about the generated tree rather than an excuse.
DEFINED_BY_A_CARD_TIP = {
    "Charge": "KokomiRiderTips.ForCharge",
    "Muster": "KokomiRiderTips.ForMuster",
    "Burst": "KleeCardTooltips.ForBurst",
    "Burst Energy": "KleeCardTooltips.ForBurst",
    # `EB-491` (Fish Blasting). Confiscated is a STATUS CARD, not a keyword: it
    # is a card the player will hold, with its own printed face, and the rule a
    # reader wants is what that card does -- which the tip on the row that
    # makes one already states (`includesConfiscatedRules`). A glossary row
    # could only name it a second time.
    "Confiscated": "KleeCardTooltips.ForCard",
}

# `Exhaust` conjugates and the glossary keys do not, so the past participle
# resolves to the `Exhaust` row. Spelled here rather than guessed at by the
# assertion, which compares whole names.
CONJUGATIONS = {"Exhausted": "Exhaust",
                # The co-op set: "their next Attack Sets off your Bombs".
                "Sets off": "Set off"}


def _word_owner(word: str) -> str:
    """Whose run is this printed word's own? (`EB-504`, `EB-753`)

    Two tables answer it and they answer different questions. `EB-504`'s says
    whose RULE a universally printed word states (`Oz`; `Hexerei` until
    R276);
    `EB-753`'s says which kit OWNS the word outright, and a word another kit
    owns has no glossary row on this run at all. Either way the census has to
    ask its question on the run the word belongs to: the recorded fixture is a
    Kokomi, and asking there whether Klee's `Bomb` is defined would be asking
    about the defect rather than about the contract.

    THE PLURAL IS THE SAME WORD, which is the assertion's own rule ("a row
    whose name is a prefix of the printed span counts"), so `Bombs` resolves
    through `Bomb` and `Sparks` through `Spark`.
    """
    from understudy.blindplay_notes import (_ARM_KEYWORD_ARM,
                                            _ARM_KEYWORD_CHARACTER)
    for table in (_ARM_KEYWORD_CHARACTER, _ARM_KEYWORD_ARM):
        if word in table:
            return table[word]
        for name, owner in table.items():
            if word.startswith(name):
                return owner
    return ""


def _page_for_word(word: str) -> str:
    """One rendered page whose hand holds a single face naming `word`.

    The face carries an `Applies Pyro` keyword row so the screen is
    element-bearing: `Elemental Reaction` is a rule about a BOARD, and
    `_elements_on_screen` is what raises the six reaction rows. Everything else
    about the card is deliberately bare, so a definition on the page came from
    the glossary and not from a tip that happened to ride along.

    `EB-504`. THE RUN IS THE WORD'S OWN WHERE THE RULE HAS ONE. One row --
    `Oz` (and `Hexerei` until R276) -- states a rule that belongs to Klee and printed it on
    every character's screens, because the faces carrying the words are
    drafted by the whole roster. Since that row they print their NAME alone on
    a run that cannot use them, so this census asks the question on the run
    the rule is about; the recorded fixture is a Kokomi, and asking it there
    would be asking whether Klee's rule reaches a Kokomi -- which is the
    defect, not the contract.
    """
    from tier0.tests.test_understudy_blindplay import combat_state
    import json
    state = json.loads(json.dumps(combat_state()))
    owner = _word_owner(word)
    if owner:
        state["player"]["character"] = owner.capitalize()
    # Round four: a word that belongs to ONE card (Ousia and Pneuma, Arkhe
    # Alignment's) is defined only beside that card, and that card is the only
    # face golding it -- so the probe wears its name.
    from understudy.blindplay_notes import _ARM_KEYWORD_ANCHOR
    state["player"]["hand"] = [{
        "id": "KLEEMOD-PROTO_GOLD_PROBE",
        "name": _ARM_KEYWORD_ANCHOR.get(word, "Probe"), "type": "Skill",
        "cost": "1", "can_play": True, "index": 0, "target_type": "AnyEnemy",
        "is_upgraded": False,
        "keywords": [{"name": "Applies Pyro",
                      "description": "Applies a Pyro aura for 2 turns."}],
        "description": f"Apply 2 {word} to ALL enemies."}]
    return blindplay.observe(state)


def _surface_gold_words() -> list[str]:
    """Every `[gold]` word the committed prototype tree prints, deduped."""
    words: set[str] = set()
    for path in _prototype_files():
        for description in _descriptions(path.read_text(encoding="utf-8")):
            for span in _GOLD_SPAN.findall(description):
                span = re.sub(r"\{[^{}]*\}", "", span).strip()
                if span:
                    words.add(span)
    return sorted(words)


def test_the_gold_word_census_is_not_empty():
    """The denominator. A scrape that read nothing would pass the test below
    vacuously, and this is the shape that has failed before (`EB-118` L4)."""
    words = _surface_gold_words()
    assert len(words) > 20
    assert "Vulnerable" in words and "Plan" in words


@pytest.mark.parametrize("word", _surface_gold_words())
def test_every_golded_word_a_face_prints_has_a_definition_on_the_page(word):
    """`EB-377`'s acceptance, as a machine: no page names a keyword it does
    not define.

    SEEN TO FAIL: `Vulnerable` was in the census and in neither the glossary
    nor the list above, which is the state the row was filed against.

    The plural is the same word -- `Bombs` is defined by the `Bomb` row -- so a
    row whose name is a prefix of the printed span counts, which is exactly how
    `_ARM_KEYWORD_RE` matches it in the first place.
    """
    if word in NO_GLOSSARY_ROW_OWED or word in DEFINED_BY_A_CARD_TIP:
        return
    word = CONJUGATIONS.get(word, word)
    page = _page_for_word(word)
    assert "## Words on this screen" in page, word
    glossary = page.split("## Words on this screen")[1]
    defined = [line.split("**")[1] for line in glossary.splitlines()
               if line.startswith("- **") and "** — " in line]
    assert any(word == name or word.startswith(name) for name in defined), (
        word, defined)


@pytest.mark.parametrize("word", sorted(DEFINED_BY_A_CARD_TIP))
def test_a_word_excused_by_a_card_tip_really_carries_that_tip(word):
    """The excuse, driven. A word is only allowed out of the glossary because
    a tip defines it on the face that prints it -- so at least one committed
    prototype row must both print the word and attach the tip named."""
    attach = DEFINED_BY_A_CARD_TIP[word]
    span = f"[gold]{word}[/gold]"
    carriers = [path.stem for path in _prototype_files()
                for text in [path.read_text(encoding="utf-8")]
                if span in text and f"{attach}(" in text]
    assert carriers, (word, attach)


# ------------- the 2026-09-25 text pass: the Plan tip is two sentences ------
#
# The word carried six seats' edge cases in 292 rendered characters against
# the 135 tip ceiling, under a named lint exception. The owner's ask ("the
# existing text is often very verbose and unintuitive") took them off the
# word: it says what a Plan is and in what order Plans happen. The facts a
# board needs stay on the blind-play panel, which has no ceiling, and each
# note is pinned where it is built (`test_understudy_blindplay.py`).
# Spec and census: review/records/text-pass-2026-09-25/.

PLAN_TIP = ("Play the card on the Bake-Kurage and this happens at the start "
            "of your next turn. Plans are carried out in the order you made "
            "them.")


def test_the_plan_tip_is_the_rewrite_on_the_page():
    assert blindplay.ARM_KEYWORDS["Plan"] == PLAN_TIP


def test_the_plan_tip_is_under_the_ceiling_and_carries_no_exception():
    """The overage is gone, so the lint's named exception is too -- and the
    lint's rot rule would fail the build if it were left behind."""
    from tools import lint_text_conventions as lint

    assert len(PLAN_TIP) <= lint.CEILING["tip"]
    assert "PlanKey" not in lint.EXCEPTIONS


def test_the_retired_clauses_left_the_word_and_the_panel_keeps_the_board_facts():
    """What left the tip is gone from BOTH copies of it, and the board facts
    a seat still needs are where the panel prints them."""
    body = blindplay.ARM_KEYWORDS["Plan"]
    for gone in ("non-Minion", "folds as you write it", "when-hit",
                 "any number wait", "still standing", "Dusk", "instead",
                 "go off"):
        assert gone not in body, gone
    assert "never a Minion" in blindplay.PLAN_AIM_NOTE
    assert "still standing in" in blindplay.PLAN_BLOCK_NOTE
    assert "holds any number of Plans" in blindplay.PLAN_COUNT_NOTE
    assert "not a limit" in blindplay.PLAN_COUNT_NOTE


def test_the_panels_aim_note_still_matches_the_two_aims_the_resolution_has():
    """The aim rule left the word and stayed on the panel, so the panel's
    sentence is what is held against the code now: a single-target Plan
    skips a Minion and an ALL Plan walks every living body."""
    plan = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
            / "KokomiPlan.cs").read_text(encoding="utf-8")
    assert "hittable.FirstOrDefault(IsNotMinion)" in plan
    assert "if (plan.Aim == Aim.AllEnemies)" in plan
    assert "never a Minion" in blindplay.PLAN_AIM_NOTE
    assert "Minions included" in blindplay.PLAN_AIM_NOTE


def test_the_card_that_doubles_a_carry_out_says_it_counts_twice():
    """`EB-709`. THE RULE IS ON THE CARD THAT DOUBLES.

    THE FIND (Kokomi r31 lane 2, (c)). Tide Wall paid 6 and then 9 under
    Second Wave, and the seat could not tell from any face whether the doubled
    entry counted as one Plan or two for a per-Plan counter. It counts as two
    (`EB-501`, `EB-718`: every carry-out draws off the drain-local counter),
    and no surface said so.

    DERIVED FROM THE CLAUSE, never a list of ids: `doubles_a_carry_out` asks
    the row, so a second doubler carries the sentence the day its row exists.
    """
    rows = {row["id"]: row for row in proto._rows()}
    doublers = {rid for rid, row in rows.items()
                if gen.doubles_a_carry_out(row)}
    assert doublers == {"proto_kk_second_wave"}

    src = (PROTOTYPE_DIR / "ProtoKkSecondWave.cs").read_text(encoding="utf-8")
    assert "ArmKeywordTips.ForPlanTwice(" in src
    # And the definition of `Plan` still prints beside it.
    assert "ArmKeywordTips.ForPlan(" in src

    tips = TIPS_CS.read_text(encoding="utf-8")
    assert ("\"A [gold]Plan[/gold] carried out twice counts as two. Every \"" in tips)
    assert "clause that counts [gold]Plans[/gold] carried out pays for " in tips
    # The title row is registered, or the tip renders with a raw key.
    assert 'ArmKeywordTips.PlanTwiceKey + ".title"' in MOD_CS.read_text(
        encoding="utf-8")

    # Never on a row that merely READS the count: those faces are honest.
    scout = (PROTOTYPE_DIR / "ProtoKkScoutAhead.cs")
    if scout.exists():
        assert "ForPlanTwice" not in scout.read_text(encoding="utf-8")


# --- a Stage round-three defect: the readers' literal 0 off the board --------
#
# THE FIND (round three). *Let the People Rejoice* read "Deal 0 damage to ALL
# enemies" on the Neow screen and *Ousia Surge* read "Deal 0 damage" at a card
# reward, and two seats turned the Rare down on it. The number is right in
# combat and right at resolution -- `EB-747`, whose tests stand below -- but
# every reader multiplies a LIVE bar and off a board there are no bars, so a
# CalculatedVar honestly reports nothing and the face prints the nothing.
#
# R276 FIXED IT ON THE FACE, the base game's own way. Body Slam's loc row is
# "Deal damage equal to your [gold]Block[/gold].{InCombat:\n(Deals
# {CalculatedDamage:diff()} damage)|}" -- the game hands every description an
# `InCombat` flag -- so each reader now prints its RULE in words and its live
# number on a line of its own only in combat. The hover tip stays, as the
# one-line statement of which seat the number is read off, without the
# off-board disclaimer it carried while the face printed 0.

#: Each reader, the bar its number is, and the sentence it owes. THE TEXT
#: PASS (2026-09-25) deleted the tip "wherever the face now names the
#: performer": Ousia Surge, Pneuma Refrain and Final Bow print "your back
#: performer's" / "your front performer's", and only the Rare -- "all your
#: performers' Fanfare" -- keeps its sentence.
STAGE_READERS = {
    "proto_fs_let_the_people_rejoice": ("SpendAll",
                                        "ProtoFsLetThePeopleRejoice"),
}

#: The three readers whose face names the seat, and so carry no reader tip.
STAGE_READERS_NAMED_ON_THE_FACE = {
    "proto_fs_ousia_surge": "ProtoFsOusiaSurge",
    "proto_fs_pneuma_refrain": "ProtoFsPneumaRefrain",
    "proto_fs_final_bow": "ProtoFsFinalBow",
}


def test_the_four_readers_are_the_rows_whose_number_is_a_bar():
    """DERIVED FROM THE MULTIPLIER, never a list of ids.

    `stage_reader_source` reads the C# expression `EB-747` already picked for
    the row's `amount_formula`, so a fifth reader carries the sentence the day
    its row exists and a row that stops reading a bar loses it the same day.

    Seen to FAIL before the rider: no row on the surface attached one.
    """
    rows = {row["id"]: row for row in proto._rows()}
    found = {rid: gen.stage_reader_source(row)
             for rid, row in rows.items()
             if gen.stage_reader_source(row)}
    assert found == {rid: src for rid, (src, _) in STAGE_READERS.items()}


@pytest.mark.parametrize("rid", sorted(STAGE_READERS))
def test_every_reader_carries_the_rule_its_number_obeys(rid):
    """The attach is committed, with the right one of the four sentences."""
    source, cls = STAGE_READERS[rid]
    src = (PROTOTYPE_DIR / f"{cls}.cs").read_text(encoding="utf-8")
    assert ("ArmKeywordTips.ForStageReader(base.ExtraHoverTips, this, "
            f"ArmKeywordTips.StageReader.{source})") in src


@pytest.mark.parametrize("rid", sorted(STAGE_READERS_NAMED_ON_THE_FACE))
def test_a_reader_whose_face_names_the_seat_carries_no_reader_tip(rid):
    """The text pass: the face says "your back performer's" or "your front
    performer's", so a tip restating which bar it is would be noise."""
    cls = STAGE_READERS_NAMED_ON_THE_FACE[rid]
    src = (PROTOTYPE_DIR / f"{cls}.cs").read_text(encoding="utf-8")
    assert "ForStageReader" not in src
    row = {r["id"]: r for r in proto._rows()}[rid]
    assert ("[gold]back performer[/gold]" in row["description"]
            or "[gold]front performer[/gold]" in row["description"])


def test_the_readers_tip_states_each_rule():
    """The rule, on every screen. The off-board disclaimer ("the number above
    reads 0") left with R276: the faces print the rule outside combat now, so
    the sentence would be false everywhere."""
    tips = TIPS_CS.read_text(encoding="utf-8")
    assert 'const string ReaderKey = "KLEEMOD-ARM_STAGE_READER";' in tips
    # The one rule left (the text pass deleted the three whose face names
    # the seat), and none of the three it deleted.
    assert ("The number is every performer's [gold]Fanfare[/gold] added up and"
            in tips)
    assert "The number is the [gold]lead performer[/gold]'s " not in tips
    assert "The number is the [gold]back performer[/gold]'s " not in tips
    assert "no stage outside combat" not in tips
    assert "return With(inherited, ReaderKey, rule);" in tips
    # The title row is registered, or the tip renders with a raw loc key.
    assert 'ArmKeywordTips.ReaderKey + ".title"' in MOD_CS.read_text(
        encoding="utf-8")


def test_the_readers_rules_are_measured():
    """The census sees the one rule left (four before the text pass).

    A `With(...)` call whose body is a named const reaches
    `lint_text_conventions.tip_rows` as an empty string -- the silence
    `EB-343` was filed on -- so the rule is parsed out by name.
    """
    sys.path.insert(0, str(REPO / "tools"))
    import lint_text_conventions as lint       # noqa: E402

    rows = {row.ident: row.raw for row in lint.tip_rows()
            if row.ident.startswith("ReaderKey.")}
    assert len(rows) == 1
    for ident, raw in rows.items():
        assert len(lint.render(raw)) <= lint.CEILING["tip"], ident


# ---------------------------------------------------------------------------
# 2026-09-25. WHAT A SUMMON DOES, AND WHAT EACH PERFORMER DOES.
#
# THE FIND. A first-time co-op player on 0.2.3737+proto "found it very hard to
# understand what was going on from the tooltips, such as what each summoned
# actor actually did". No card said what a summon puts on the board, and no
# card or body said what a performer does.
# ---------------------------------------------------------------------------

#: Every row that summons, and the performer tips it owes, in attach order.
STAGE_SUMMONERS = {
    "proto_fs_salon_debut": ("Usher", "Chevalmarin", "Crabaletta"),
    "proto_fs_understudy": ("Usher", "Chevalmarin", "Crabaletta"),
    "proto_fs_double_casting": ("Usher", "Chevalmarin", "Crabaletta"),
    # A summon inside a conditional's branch owes the same tips.
    "proto_fs_improvised_number": ("Usher", "Chevalmarin", "Crabaletta"),
    "proto_fs_gentilhomme_usher": ("Usher",),
    "proto_fs_surintendante_chevalmarin": ("Chevalmarin",),
    "proto_fs_mademoiselle_crabaletta": ("Crabaletta",),
}


#: The rows whose summons are all NAMED, and so take the Summon tip's named
#: variant: no full-stage sentence, because their face says what a performer
#: already on stage does.
NAMED_SUMMONERS = {"proto_fs_gentilhomme_usher",
                   "proto_fs_surintendante_chevalmarin",
                   "proto_fs_mademoiselle_crabaletta"}


def test_every_summoning_row_and_no_other_owes_the_summon_tips():
    """DERIVED FROM THE OP, never a list of ids: a row that gains a summon
    gains the tips the day its row exists."""
    rows = {row["id"]: row for row in proto._rows()}
    found = {rid: gen.stage_summon_tip_calls(row)
             for rid, row in rows.items()
             if gen.stage_summon_tip_calls(row)}
    expected = {rid: [("ArmKeywordTips.ForSummon",
                       ", false" if rid in NAMED_SUMMONERS else ", true")]
                + [(f"ArmKeywordTips.For{who}", "") for who in cast]
                for rid, cast in STAGE_SUMMONERS.items()}
    assert found == expected


@pytest.mark.parametrize("rid", sorted(STAGE_SUMMONERS))
def test_every_summoning_row_carries_the_summon_and_performer_tips(rid):
    """The attach is committed: the generated card wraps its tips in the Summon
    tip first and then each performer it can field."""
    cls = "ProtoFs" + "".join(
        part.capitalize() for part in rid.removeprefix("proto_fs_").split("_"))
    src = (PROTOTYPE_DIR / f"{cls}.cs").read_text(encoding="utf-8")
    variant = "false" if rid in NAMED_SUMMONERS else "true"
    assert (f"ArmKeywordTips.ForSummon(base.ExtraHoverTips, this, {variant})"
            in src)
    for who in STAGE_SUMMONERS[rid]:
        assert f"ArmKeywordTips.For{who}(" in src
    for who in {"Usher", "Chevalmarin", "Crabaletta"} - set(
            STAGE_SUMMONERS[rid]):
        assert f"ArmKeywordTips.For{who}(" not in src


def test_the_summon_and_performer_tips_state_the_ruled_sentences():
    """[USER]'s wording, wired exactly, the numerals interpolated from
    `FurinaStageLaw` (`EB-89`)."""
    tips = TIPS_CS.read_text(encoding="utf-8")
    for clause in (
            '"A performer joins at the back with "',
            "FurinaStageLaw.SummonFanfare",
            '" [gold]Fanfare[/gold]. If the "',
            '"stage is full, your front performer [gold]Bow[/gold]s and "',
            '"moves to the back instead."',
            '" [gold]Fanfare[/gold].");',
            "if (random)",
            '"End of your turn: gain " + FurinaStageLaw.ActUsherBlock',
            '" [gold]Block[/gold]. [gold]Bow[/gold]: gain "',
            "FurinaStageLaw.BowUsherBlock",
            '"End of your turn: deal " + FurinaStageLaw.ActChevalmarinDamage',
            '" [gold]Hydro[/gold] damage to ALL enemies. [gold]Bow[/gold]: "',
            '"apply [gold]Hydro[/gold] to ALL enemies."',
            '"End of your turn: deal " + FurinaStageLaw.ActCrabalettaDamage',
            '" [gold]Hydro[/gold] damage to a random enemy. [gold]Bow[/gold]: "',
            "FurinaStageLaw.BowCrabalettaDamage"):
        assert clause in tips, clause
    mod = MOD_CS.read_text(encoding="utf-8")
    assert 'ArmKeywordTips.SummonKey + ".title"] = "Summon"' in mod
    # The performer titles are the LEDGER'S display names (`EB-735`), the
    # names the body and its badge print.
    for who in ("Usher", "Chevalmarin", "Crabaletta"):
        assert (f"ArmKeywordTips.{who}Key + \".title\"] =\n"
                f"                        Powers.FurinaStageLedger.DisplayName("
                f"\n                            Powers.StagePerformer.{who})"
                ) in mod


def test_the_page_glossary_says_what_the_summon_and_performer_tips_say():
    """The seat glossary is held in step from this side: the same sentences,
    the numerals written out."""
    rows = blindplay.ARM_KEYWORDS
    assert rows["Summon"] == (
        "A performer joins at the back with 1 Fanfare. If the stage is full, "
        "your front performer Bows and moves to the back instead.")
    from understudy import blindplay_notes
    assert blindplay_notes.SUMMON_NAMED_ROW == (
        "A performer joins at the back with 1 Fanfare.")
    assert rows["Gentilhomme Usher"] == (
        "End of your turn: gain 3 Block. Bow: gain 4 Block.")
    assert rows["Surintendante Chevalmarin"] == (
        "End of your turn: deal 2 Hydro damage to ALL enemies. Bow: apply "
        "Hydro to ALL enemies.")
    assert rows["Mademoiselle Crabaletta"] == (
        "End of your turn: deal 5 Hydro damage to a random enemy. Bow: deal 8 "
        "Hydro damage to a random enemy.")


# ---------------------------------------------------------------------------
# 2026-09-25, THE FURINA TEXT PASS: a Spend card's face is two sentences.
# ---------------------------------------------------------------------------

def test_a_spend_cards_sentence_face_still_splits_into_its_modes():
    """The pass dropped "Choose one:" and the "|" from the five Spend cards,
    so the chooser's option faces are read off the face's SENTENCES -- one
    per mode, with the parent's var tokens -- and the chooser and the hand
    stay one sentence by construction."""
    rows = {row["id"]: row for row in proto._rows()}
    row = rows["proto_fs_curtain_rise"]
    modes = gen.modal_effect(row)["modes"]
    assert gen.modal_option_faces(row, modes) == [
        "Deal {PlainDamage:diff()} damage",
        "[gold]Spend[/gold] 3: deal {BranchDamage:diff()} instead"]
    for rid in ("proto_fs_tidal_flourish", "proto_fs_interposition",
                "proto_fs_grand_entrance", "proto_fs_quick_cue"):
        assert gen.modal_option_faces(
            rows[rid], gen.modal_effect(rows[rid])["modes"]) is not None, rid
