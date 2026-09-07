"""`EB-625`: Shell Guard names a relic, and now something says what it is.

[USER]'s Kokomi act-1 run of 2026-09-07 read "Until your next turn, whenever
the [gold]Tamakushi Casket[/gold] strikes, gain 3 [gold]Block[/gold]" and asked
two things of it: how the Casket could strike at all, and what the Casket is.
Neither had an answer on screen. The relic prints the rule on the relic; the
card printing the proper noun printed nothing.

THE ANSWER IS A KEYWORD TIP, which is `Grounded`'s shape and `Oz`'s one kit
over: the attach travels with the printed word, so a second row written against
the relic carries the definition the day it is authored rather than the day
somebody remembers it. The sentence is the relic's own, word for word, because
two spellings of one rule is how a player learns there are two rules. The
number is read off the shared constant on both surfaces and typed on neither.

AND THE WINDOW STANDS AT "until your next turn", which is where the row's own
proposed face ("This turn, whenever ...") turns out to be wrong. The window is
deliberately wider than her turn: R246 pick 2 says "the morning's Plans that
apply Weak strike it too, so the Block is there before the enemy swings", and
both engines close the window one line AFTER the next morning's drain
(`kokomi_plan.close_shell_guard`, `ShellGuardPower.Close` from
`ProtoBakeKuragePower.AfterPlayerTurnStart`) precisely so that sentence is
true. "This turn" would print a smaller window than the rule has, which is the
defect this row exists to end running the other way. The face keeps its words;
this file pins WHY.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import kokomi_plan
from tier05 import rewards
from understudy import blindplay_notes, blindplay_shape

REPO = Path(__file__).resolve().parents[2]

TIPS_CS = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
           / "ArmKeywordTips.cs")
MOD_CS = REPO / "klee-mod" / "KleeCode" / "KleeMod.cs"
LAW_CS = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
          / "KokomiOverhaul.cs")
RELIC_CS = REPO / "klee-mod" / "KleeCode" / "Relics" / "TamakushiCasket.cs"
SHELL_GUARD_CS = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
                  / "Generated" / "ProtoKkShellGuard.cs")


@pytest.fixture
def overhaul(monkeypatch):
    """The Kokomi arm ON -- `test_kokomi_overhaul`'s fixture, for its
    reasons."""
    loader.reset_arm_caches()
    rewards.character_pool.cache_clear()
    monkeypatch.setattr(C, "KOKOMI_OVERHAUL", True)
    yield
    loader.reset_arm_caches()
    rewards.character_pool.cache_clear()


def test_the_tip_attaches_to_every_face_that_names_the_relic():
    """Derived from the printed word, not from a card list: Shell Guard is
    the only face naming the Casket today, and the next one carries the tip
    without anybody adding it here."""
    from tools import gen_klee_cards as gen

    entry = next(k for k in gen.ARM_KEYWORDS if k.word == "Tamakushi Casket")
    assert entry.attach == "ArmKeywordTips.ForCasket"
    assert entry.tokens == ("Tamakushi Casket",)

    face = ("Gain 5 [gold]Block[/gold]. Until your next turn, whenever the "
            "[gold]Tamakushi Casket[/gold] strikes, gain 3 [gold]Block[/gold].")
    assert "ArmKeywordTips.ForCasket" in gen.arm_keyword_tip_calls(face)
    # And a face that does not name it does not carry it.
    assert "ArmKeywordTips.ForCasket" not in gen.arm_keyword_tip_calls(
        "Gain 8 [gold]Block[/gold].")

    assert "ArmKeywordTips.ForCasket(" in SHELL_GUARD_CS.read_text(
        encoding="utf-8")


def test_the_number_is_read_and_never_typed():
    """A retune of the strike must not be able to leave either surface
    quoting a retired number, which is `EB-89`'s standing rule for this
    table."""
    tips = TIPS_CS.read_text(encoding="utf-8")
    body = tips[tips.index("public static IEnumerable<IHoverTip> ForCasket"):]
    body = body[:body.index(";")]
    assert "KokomiOverhaulLaw.CasketStrike" in body
    # The digit itself appears nowhere in the sentence.
    assert " 2 [gold]Hydro[/gold]" not in body

    # The page's twin interpolates its own mirror of the same constant.
    notes = (REPO / "understudy"
             / "blindplay_notes.py").read_text(encoding="utf-8")
    assert "{CASKET_STRIKE} Hydro damage" in notes


def test_both_surfaces_and_both_engines_carry_one_number():
    """`blindplay_shape` may not reach `tier0`, so its copy is held in step
    from here -- the discipline `BOMB_GROWTH` and `SHATTER_DAMAGE` are already
    under -- and the C# law is the third copy `lint_constant_parity` pins by
    value."""
    assert blindplay_shape.CASKET_STRIKE == C.KOKOMI_OVERHAUL_CASKET_STRIKE
    law = LAW_CS.read_text(encoding="utf-8")
    assert (f"public const int CasketStrike = "
            f"{C.KOKOMI_OVERHAUL_CASKET_STRIKE};") in law


def test_the_tip_is_the_relics_own_sentence():
    """Word for word off the relic's face, minus the summon clause the card
    has no use for and plus the two words the relic cannot say about itself.
    """
    tips = TIPS_CS.read_text(encoding="utf-8")
    assert ('"Your relic. Whenever you apply a debuff to an enemy, it deals "'
            in tips)
    relic = RELIC_CS.read_text(encoding="utf-8")
    assert '"Start each combat with the [gold]Bake-Kurage[/gold]. Whenever "' \
        in relic
    assert '+ "you apply a debuff to an enemy, it deals [blue]"' in relic

    page = blindplay_notes.ARM_KEYWORDS["Tamakushi Casket"]
    assert page == ("Your relic. Whenever you apply a debuff to an enemy, it "
                    f"deals {C.KOKOMI_OVERHAUL_CASKET_STRIKE} Hydro damage to "
                    "that enemy.")
    # Inside the 135-character mechanic-tip ceiling with room to spare, so it
    # needs no exception in `lint_text_conventions`.
    assert len(page) <= 135


def test_the_tip_has_a_title_and_not_a_raw_key():
    """`EB-64`'s hazard, which has bitten this table before: a key with no
    localization row renders as the key."""
    mod = MOD_CS.read_text(encoding="utf-8")
    assert 'CasketKey + ".title"] =' in mod
    assert '"Tamakushi Casket",' in mod
    assert 'public const string CasketKey = "KLEEMOD-ARM_CASKET";' in \
        TIPS_CS.read_text(encoding="utf-8")


def test_the_window_is_wider_than_this_turn_and_the_face_says_so(overhaul):
    """THE ROW'S OTHER PREMISE, WHICH IS WRONG, and this is the reading that
    says why.

    The proposal was "This turn, whenever the Tamakushi Casket strikes". The
    window is not this turn: it deliberately survives into the NEXT turn's
    morning, because R246 pick 2 puts the Plans that apply Weak inside it --
    "so the Block is there before the enemy swings". Both engines close it one
    line after the drain rather than at her turn end or on the turn-start
    roll, and both say so in their headers. So the face keeps "Until your next
    turn", and the half that was missing was never the window: it was the
    relic.
    """
    # The row is on the arm's surface at all, which is what makes the rest of
    # this a live reading rather than an archaeology of a withdrawn card.
    assert any(c.id == "proto_kk_shell_guard"
               for c in loader.prototype_cards())

    import yaml
    sheet = yaml.safe_load(
        (REPO / "docs" / "prototype-surface.yaml").read_text(encoding="utf-8"))
    rows = sheet["cards"] if isinstance(sheet, dict) else sheet
    face = next(r for r in rows
                if r["id"] == "proto_kk_shell_guard")["description"]
    assert "Until your next turn" in face
    assert "This turn" not in face

    # The sim's window is closed by its own function, and that function is
    # called from turn start AFTER the drain -- never by `roll_turn`.
    src = (REPO / "tier0" / "engine"
           / "kokomi_plan.py").read_text(encoding="utf-8")
    assert "def close_shell_guard" in src
    assert "SHELL GUARD'S WINDOW IS NOT ON THIS LINE" in src
    assert callable(kokomi_plan.close_shell_guard)

    combat = (REPO / "tier0" / "engine" / "combat.py").read_text(
        encoding="utf-8")
    assert combat.index("resolve_all") < combat.index("close_shell_guard")

    # And the C# closes it from the jellyfish's turn-start hook, one line
    # after the morning, for the sentence's sake.
    pet = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
           / "ProtoBakeKuragePower.cs").read_text(encoding="utf-8")
    assert "await ShellGuardPower.Close(Owner);" in pet
    powers = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
              / "KokomiOverhaulPowers.cs").read_text(encoding="utf-8")
    assert '"Until your next turn, whenever the [gold]Tamakushi Casket[/gold] "' \
        in powers
