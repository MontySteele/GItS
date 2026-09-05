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
# Strike is written against it by name -- "This turn, Grounded counts nothing
# as having gone off" -- as is the Cold-Blooded buff that card leaves behind.
# A seat that drafted Kaeya and never drafted Grounded met the word on a card
# face with nothing on the screen saying what it is, and read it as noise in
# both acts (r9 act 1 sec.(c) 3, act 2 sec.(c) 2).
#
# THE FIX IS THE TABLE, which is what makes it travel: the attach is derived
# from the printed face, so the definition rides every face that prints the
# word whether or not the run holds the Power.


def test_the_grounded_word_owes_its_definition_wherever_it_is_printed():
    assert gen.arm_keyword_tip_calls(
        "This turn, [gold]Grounded[/gold] counts nothing as having gone "
        "off.") == ["ArmKeywordTips.ForGrounded"]
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
    assert "[gold]Grounded[/gold] counts nothing as having gone off." in card
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
    assert "This turn, [gold]Grounded[/gold] counts nothing as having gone "         in body
    assert "ArmKeywordTips.ForGrounded(base.ExtraHoverTips)" in body


def test_the_grounded_tip_states_the_condition_and_defers_on_the_payout():
    """The CONDITION is the whole rule a Kaeya reader needs. What Grounded
    pays is the Power card's own printed line and moves with its upgrade, so
    the tip must not quote a number a second card would contradict."""
    tips = TIPS_CS.read_text(encoding="utf-8")
    assert "that pays at the start of your turn, but " in tips
    assert "only if none of your [gold]Bombs[/gold] went off last turn. Its "         in tips
    assert "card prints what it pays." in tips
    sheet = (REPO / "docs" / "prototype-surface.yaml").read_text(
        encoding="utf-8")
    assert "gain 6 [gold]Block[/gold] and 1 [gold]Spark[/gold]" in sheet


def test_the_attach_is_scoped_to_the_quarantined_surface():
    """A shipped profile must never carry the arm's contradicting sentence."""
    assert gen.KLEE_PROFILE.arm_keyword_tips is False
    assert gen.FURINA_PROFILE.arm_keyword_tips is False
    assert gen.KOKOMI_PROFILE.arm_keyword_tips is False
    assert proto.DIR_PROFILE.arm_keyword_tips is True
    for character in sorted(gen.PROFILES):
        assert proto._profile_for(character).arm_keyword_tips is True


def test_every_klee_personal_companion_carries_the_kits_spark_rider():
    """`EB-418`, the committed tree. Every row on the quarantined sheet that is
    a Personal Companion of KLEE'S carries `ForCovenSpark`, and no other row
    does.

    THE DENOMINATOR IS THE POINT. The trigger is keyed on the POOL and not on
    one card (`effects.klee_personal_companion_spark`, `KleeCompanionSpark`),
    which is how it reached Diona and the coven stand-ins with nobody deciding
    it should -- so the sentence has to reach the same set by the same read, or
    the next Personal added to the sheet is the r11 seat's finding again.

    GOROU IS THE NEGATIVE CASE, and he is a real one: he is a Personal
    Companion of KOKOMI'S on this same sheet, he walks the engines' identical
    branch, and Sparks are Klee's resource with no surface of Kokomi's to read
    them off. The sentence is scoped to the kit that declared it.
    """
    owed, carried = set(), set()
    for row in proto._rows():
        if not gen.is_companion(row):
            continue
        cls = gen.pascal(row["id"])
        if (row.get("character") == "klee"
                and gen.personal_pool_id(row) == "klee"):
            owed.add(cls)
        path = PROTOTYPE_DIR / f"{cls}.cs"
        if path.exists() and "ForCovenSpark" in path.read_text(encoding="utf-8"):
            carried.add(cls)

    assert owed, "no Klee Personal Companion on the sheet is not a read"
    assert owed == carried
    assert "ProtoMiGorouCrystalCollapse" in {
        gen.pascal(r["id"]) for r in proto._rows()
        if gen.is_companion(r) and r.get("character") == "kokomi"}
    assert "ProtoMiGorouCrystalCollapse" not in carried


def test_every_hexerei_companion_prints_the_family_tag():
    """`EB-392`, the committed tree. Every Companion row the sheet marks
    `hexerei` prints the word on its own face, and no row that is not marked
    does.

    THE DEFECT. `hexerei: true` emitted `IHexereiCard` and nothing a player
    could see, so the family was readable only from the three cards that ASK
    about it -- and those ask about a set whose members never said they were
    in it. The r12 run-2 seat held Witches' Circle for four fights: "I owned no
    Hexerei card and the reminder text does not say which of my cards are
    Hexerei", and found the answer "only by counting bombs on the enemy badge,
    because Fischl's own face never prints the word Hexerei".

    THE DENOMINATOR IS THE POINT, exactly as it is for the Spark rider above:
    the tag is DERIVED from the sheet key (`gen._hexerei_tag`), so a row that
    joins the family carries the mark because it joined. The negative case is
    every unmarked Companion on the same sheet.

    THE READERS ARE NOT MEMBERS. Coven Errand and Witches' Circle are Klee's
    own cards and carry no `hexerei` key; Alice's Introduction Magic carries
    it and already prints the word in its body, which is why the tag is
    skipped where the face has said it.
    """
    marked, printed = set(), set()
    for row in proto._rows():
        if not gen.is_companion(row):
            continue
        cls = gen.pascal(row["id"])
        if row.get("hexerei"):
            marked.add(cls)
        path = PROTOTYPE_DIR / f"{cls}.cs"
        if not path.exists():
            continue
        if any("[gold]Hexerei[/gold]" in face
               for face in _descriptions(path.read_text(encoding="utf-8"))):
            printed.add(cls)

    assert marked, "no Hexerei Companion on the sheet is not a read"
    assert marked == printed
    # ... and the definition rides the printed word, which is `EB-272`'s
    # attach rule doing the work rather than a second list to maintain.
    for cls in sorted(marked):
        assert "ForHexerei" in (PROTOTYPE_DIR / f"{cls}.cs").read_text(
            encoding="utf-8"), cls


def test_the_hexerei_readers_are_not_tagged_as_members():
    """Klee's own three read the word; none of them is a Companion, so none of
    them takes the tag. Named rather than derived, because the point is that
    the tag's guard is `is_companion` and these are the rows it excludes."""
    for cls in ("ProtoKoCovenErrand", "ProtoKoWitchesCircle"):
        face, = _descriptions(
            (PROTOTYPE_DIR / f"{cls}.cs").read_text(encoding="utf-8"))[:1]
        assert "[gold]Hexerei[/gold]" in face
        assert not face.startswith("[gold]Hexerei[/gold]. "), cls


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
    for stem in ("ProtoKoFwoosh", "ProtoKoTinderToss", "ProtoKoQuickFuse",
                 "ProtoKoBangBang", "ProtoKoPowderCharge", "ProtoKoDigIn",
                 "ProtoKoSugarRush"):
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
    for stem in ("ProtoPopSpark", "ProtoPowderChargeSpark",
                 "ProtoSparkModeBombs"):
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
# no word on any card can carry it. They are named here so the count below
# stays a real pin instead of a number somebody bumps.
NON_KEYWORD_KEYS = {"KLEEMOD-ARM_PLAN_ELEMENT", "KLEEMOD-ARM_COVEN_SPARK"}


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
            " a turn, goes off only when [gold]Set off[/gold]. ",
            "Not an Attack: only [gold]Vulnerable[/gold] and a cap move it. ",
            "Kills move it on.",
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
            "The target's [gold]Bombs[/gold] go off first, oldest first, each ",
            "a Pyro hit. [gold]Block[/gold] stops them, no when-hit power ",
            "fires, the first takes the aura.",
            "Some cards cost [gold]Sparks[/gold] instead of Energy, with no cap. ",
            "Start each combat with ",
            ". Pounding Surprise grants more. ",
            "Gone after combat.",
            # `EB-436`: the clause said WHEN and nothing about the attack,
            # and a seat read mitigation into it. A Mine blunts nothing; the
            # only thing it can do to the hit is stop it happening.
            "that also goes off before its enemy's hit, ",
            "which lands in full unless the Mine kills.",
            # `EB-373`: a Mine IS a Bomb, so the same two terms move it and
            # the two tips say so in the same words.
            "Only their ",
            # Kokomi, kokomi-overhaul-slice-1-2026-09-01.md DRAFT 6 sec.2.
            # Two keywords, not six: draft 6 cut Tide, Surge, Exert and the
            # Garment, and their four sentences left with them.
            #
            # `EB-329` REWROTE THE AIM CLAUSE. "On the front enemy" was the
            # whole of it and it was false for every Plan that says ALL --
            # including the starter Kurage's Oath -- so the clause now defers
            # to the face, which was right all along. "First thing" and
            # "raises it" paid for the room: 144 characters with them, 132
            # without, against a ceiling of 135 and no exception taken.
            #
            # `R250` (round-5 sec.6 pick 1) ADDED "NEVER A MINION": two
            # formations put a decoy on the leftmost slot on purpose, and the
            # sixth clause compressed "lands next turn on" to "next turn:" to
            # stay under the same 135-character ceiling.
            #
            # `EB-380` SPLIT THAT CLAUSE, because the rule is not flat: an ALL
            # Plan walks every living body, decoys included, and the round-9
            # act-1 seat watched one land on `Eye With Teeth` while this
            # sentence said it could not. And `Strength` joined the modifier
            # clause -- naming Vulnerable and Weak and stopping read as a
            # complete list, and the carry-out is an UNPOWERED hit. 135
            # characters rendered, at the ceiling: "the front enemy" and "or
            # ALL if it says so" paid for both facts.
            "On the [gold]Bake-Kurage[/gold], paid now; next turn: front ",
            "non-[gold]Minion[/gold], or ALL, [gold]Minions[/gold] too. ",
            "Enemy [gold]Vulnerable[/gold] counts; your [gold]Weak[/gold] ",
            "and [gold]Strength[/gold] do not.",
            "heal N HP, never above the HP you entered ",
            # Furina, furina-reframe-2026-08-29.md sec.4.2 / sec.4.4 / sec.4.6,
            # staged as slice two. Three words the SHIPPED kit does not have:
            # its deploy performs nobody, its bow neither triples the Fanfare
            # bonus nor mints, and it has no drain at all.
            #
            # `EB-368` REWROTE Deploy's sentence rather than extending it: the
            # act-2 seat played no Salon card in three fights because the word
            # never said what makes a member act AFTER the deploy, and three
            # rules appended to the old two sentences ran 50 characters over
            # the keyword-tip ceiling. Same call R248 made for the Bomb.
            "A member joins and performs at once; a full stage ",
            "[gold]Evokes[/gold] the front member first. Afterwards only a ",
            "[gold]Companion[/gold] play performs a member.",
            "The member performs and leaves. Its [gold]Fanfare[/gold] bonus ",
            " [gold]Fanfare[/gold]. The card's [gold]Encore[/gold] price pays ",
            "for it.",
            "Your [gold]Fanfare[/gold] falls to nothing. What the card does ",
            "next is priced off the amount it took.",
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
    # The Furina reframe's Evoke sentence carries TWO numbers -- the Focus
    # multiplier and the mint -- and both are prototype SEEDS (R215 B), which
    # makes a retune likelier here than anywhere else on this list.
    assert "FurinaReframeLaw.EvokeFocusMult" in tips
    assert "FurinaReframeLaw.FanfarePerEvoke" in tips
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
    "description": ("Playing one of Klee's own Companions makes 1 Spark, 1 "
                    "more if it triggered an Elemental Reaction and 1 more if "
                    "it is upgraded."),
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
CONJUGATIONS = {"Exhausted": "Exhaust"}


def _page_for_word(word: str) -> str:
    """One rendered page whose hand holds a single face naming `word`.

    The face carries an `Applies Pyro` keyword row so the screen is
    element-bearing: `Elemental Reaction` is a rule about a BOARD, and
    `_elements_on_screen` is what raises the six reaction rows. Everything else
    about the card is deliberately bare, so a definition on the page came from
    the glossary and not from a tip that happened to ride along.

    `EB-504`. THE RUN IS THE WORD'S OWN WHERE THE RULE HAS ONE. Two rows --
    `Hexerei` and `Oz` -- state a rule that belongs to Klee and printed it on
    every character's screens, because the faces carrying the words are
    drafted by the whole roster. Since that row they print their NAME alone on
    a run that cannot use them, so this census asks the question on the run
    the rule is about; the recorded fixture is a Kokomi, and asking it there
    would be asking whether Klee's rule reaches a Kokomi -- which is the
    defect, not the contract.
    """
    from tier0.tests.test_understudy_blindplay import combat_state
    from understudy.blindplay_notes import _ARM_KEYWORD_CHARACTER
    import json
    state = json.loads(json.dumps(combat_state()))
    owner = _ARM_KEYWORD_CHARACTER.get(word)
    if owner:
        state["player"]["character"] = owner.capitalize()
    state["player"]["hand"] = [{
        "id": "KLEEMOD-PROTO_GOLD_PROBE", "name": "Probe", "type": "Skill",
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


# ------------------ `EB-380`: the Plan tip states the rule it has ----------


def test_the_plan_tip_matches_the_two_aims_the_resolution_has():
    """`KokomiPlan.FrontTarget` skips a Minion; `Aim.AllEnemies` walks every
    living body, decoys included. The tip said "never a Minion" flat, and the
    r9 act-1 seat watched an `Exposed Flank+` Plan land on `Eye With Teeth`
    (run 2, act 1, (c) 4).

    Driven against the RESOLUTION rather than restated: both branches are read
    out of `KokomiPlan.cs` here, so a tip that stops matching the code goes red
    from this side too.

    THE TIP STILL NAMES TWO AND THERE ARE THREE (`EB-492`, Flank's
    `EnemiesIntendingAttack`), and that is deliberate rather than a gap. The
    tip is AT its 135-character ceiling and states the DEFAULT -- where a
    planned hit lands when the line does not say -- while the third aim is a
    clause the one card that uses it prints in full on its own face ("to each
    enemy that intends to attack"). A tip that tried to carry it would have to
    drop the modifier clause the r9 seat needed.
    """
    plan = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
            / "KokomiPlan.cs").read_text(encoding="utf-8")
    assert "hittable.FirstOrDefault(IsNotMinion)" in plan
    assert "if (plan.Aim == Aim.AllEnemies)" in plan
    assert "if (plan.Aim == Aim.EnemiesIntendingAttack)" in plan
    body = blindplay.ARM_KEYWORDS["Plan"]
    assert "front non-Minion" in body
    assert "or ALL, Minions too" in body
    assert "never a Minion" not in body


def test_the_plan_tip_names_strength_among_the_modifiers_that_do_not_reach():
    """The carry-out is an UNPOWERED `ElementalHit` -- no Strength, no Weak,
    no attack buff of hers -- while the TARGET's Vulnerable multiplies. The
    clause named two of the three, which reads as a complete list, and the seat
    priced `Kurage's Oath+` face 4 under Vajra at Plan 10 expecting Strength to
    ride it (run 2, act 1, (c) 5)."""
    plan = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
            / "KokomiPlan.cs").read_text(encoding="utf-8")
    assert "UNPOWERED -- no Strength, no Weak" in plan
    body = blindplay.ARM_KEYWORDS["Plan"]
    assert "Enemy Vulnerable counts; your Weak and Strength do not." in body


def test_the_plan_tip_stays_under_the_keyword_ceiling():
    """135, the base game's own longest mechanic tip, and this word is read on
    every battle screen of every run."""
    assert len(blindplay.ARM_KEYWORDS["Plan"]) <= 135
