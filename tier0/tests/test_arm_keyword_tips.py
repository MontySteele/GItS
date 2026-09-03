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


def test_the_arm_keys_never_collide_with_a_shipped_keyword_id():
    """`Bomb` and `Swirl` are the same WORD under two different rules, so the
    keys must differ or the loc merge would let one arm overwrite the other."""
    tips = TIPS_CS.read_text(encoding="utf-8")
    keys = set(re.findall(r'"(KLEEMOD-[A-Z0-9_]+)"', tips))
    assert len(keys) == len(gen.ARM_KEYWORDS)
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
            # word a seat reads every turn. All four rules are still here in two
            # sentences, and the tip takes no length exception.
            # `EB-373` REWROTE THE LAST CLAUSE. The fold is `FoldedMods` and
            # it reads two things off the target -- Vulnerable and whichever
            # power sets the lowest damage cap -- so "takes the enemy's
            # debuffs" was a promise the code does not keep. The r9 seat
            # priced two fights off it: a Slow 50 enemy took 48 from a pile
            # printing 46, and a Flutter 5 enemy took a 27 Bomb whole while a
            # printed 8 Attack landed 4. Both debuffs say "from Attacks", and
            # a Bomb's hit is not an Attack -- which is what the clause leads
            # with now, inside the same 135-character ceiling.
            "A charge on an enemy: grows ",
            " a turn, goes off only when [gold]Set off[/gold], all at once. ",
            "Not an Attack: only their [gold]Vulnerable[/gold] and a cap ",
            "move it.",
            "on the target goes off first, one at a ",
            "time, each a Pyro hit for its size.",
            "Some cards cost [gold]Sparks[/gold] instead of Energy, with no cap. ",
            "Start each combat with ",
            ". Pounding Surprise grants more. ",
            "Gone after combat.",
            "that also goes off when its enemy attacks ",
            "you, before the hit lands.",
            # `EB-373`: a Mine IS a Bomb, so the same two terms move it and
            # the two tips say so in the same words.
            "Read the badge: only their ",
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
            "On the [gold]Bake-Kurage[/gold], paid now; next turn: front ",
            "enemy, or ALL if it says so; never a Minion. ",
            "[gold]Vulnerable[/gold] counts; your [gold]Weak[/gold] does ",
            "not.",
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
