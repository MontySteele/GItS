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

THE CASKET PASS (2026-09-28) REWROTE THE RELIC, and the tip and the page with
it. [USER]: "an artifact that grants / tracks an alternative energy that
builds by 1 for every Plan played, and adds one 0-cost Retain / Exhaust card
that converts that energy into Strength." The debuff strike is retired; the
Casket COUNTS the Plans the Bake-Kurage carries out. The tip still travels
with the printed word -- by the relic's full name (Shell Guard) and by its
short one ("the Casket gains 2") -- and the number it quotes is still read,
never typed: `KokomiOverhaulLaw.CasketPerPlan` on the mod side,
`blindplay_shape.CASKET_PER_PLAN` on the page. Shell Guard's own clause
("whenever the Tamakushi Casket strikes") no longer fires; the card was not
in the ruling.
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
    # The Casket pass: the short name is the same word.
    assert entry.tokens == ("Tamakushi Casket", "Casket")
    assert "ArmKeywordTips.ForCasket" in gen.arm_keyword_tip_calls(
        "Draw 1 card. [gold]Plan[/gold]: The [gold]Casket[/gold] gains 2.")

    face = ("Gain 5 [gold]Block[/gold]. Until your next turn, whenever the "
            "[gold]Tamakushi Casket[/gold] strikes, gain 3 [gold]Block[/gold].")
    assert "ArmKeywordTips.ForCasket" in gen.arm_keyword_tip_calls(face)
    # Shell Guard's own face since its re-aim names the Casket by its short
    # name, and carries the tip the same way.
    # And a face that does not name it does not carry it.
    assert "ArmKeywordTips.ForCasket" not in gen.arm_keyword_tip_calls(
        "Gain 8 [gold]Block[/gold].")

    assert "ArmKeywordTips.ForCasket(" in SHELL_GUARD_CS.read_text(
        encoding="utf-8")


def test_the_number_is_read_and_never_typed():
    """A retune of the per-Plan count must not be able to leave either surface
    quoting a retired number, which is `EB-89`'s standing rule for this
    table."""
    tips = TIPS_CS.read_text(encoding="utf-8")
    body = tips[tips.index("public static IEnumerable<IHoverTip> ForCasket"):]
    body = body[:body.index(";")]
    assert "KokomiOverhaulLaw.CasketPerPlan" in body
    assert "CasketStrike" not in body

    notes = (REPO / "understudy"
             / "blindplay_notes.py").read_text(encoding="utf-8")
    assert "{CASKET_PER_PLAN}" in notes
    assert "CASKET_STRIKE" not in notes


def test_both_surfaces_and_both_engines_carry_one_number():
    """`blindplay_shape` may not reach `tier0`, so its copy is held in step
    from here, and the C# law is the third copy `lint_constant_parity` pins
    by value."""
    assert blindplay_shape.CASKET_PER_PLAN == C.KOKOMI_OVERHAUL_CASKET_PER_PLAN
    assert not hasattr(blindplay_shape, "CASKET_STRIKE")
    law = LAW_CS.read_text(encoding="utf-8")
    assert (f"public const int CasketPerPlan = "
            f"{C.KOKOMI_OVERHAUL_CASKET_PER_PLAN};") in law
    assert "public const int CasketStrike" not in law


def test_the_relic_and_the_tip_say_the_casket_counts():
    """The relic's face, the card-side tip and the page all say the one rule:
    each carried-out Plan adds to the count, and Open the Casket turns it into
    Strength. The strike's words are gone from all three."""
    relic = RELIC_CS.read_text(encoding="utf-8")
    assert '"[gold]Open the Casket[/gold] in hand. Each [gold]Plan[/gold] it "' \
        in relic
    assert "+ KokomiOverhaulLaw.CasketPerPlan" in relic
    assert "debuff" not in relic[relic.index('("description",'):
                                 relic.index("ExtraHoverTips")]

    tips = TIPS_CS.read_text(encoding="utf-8")
    assert '"Your relic. Each [gold]Plan[/gold] the [gold]Bake-Kurage[/gold] "' \
        in tips

    page = blindplay_notes.ARM_KEYWORDS["Tamakushi Casket"]
    assert page == (
        f"Your relic. Each Plan the Bake-Kurage carries out adds "
        f"{C.KOKOMI_OVERHAUL_CASKET_PER_PLAN}. Open the Casket turns the count "
        f"into Strength.")
    assert blindplay_notes.ARM_KEYWORDS["Open the Casket"] == (
        "1-cost, Retain. Gain Strength equal to the Casket's count, "
        "then empty it. Upgraded, it also draws a card.")
    # Inside the 135-character mechanic-tip ceiling.
    assert len(page) <= 135


def test_the_tip_has_a_title_and_not_a_raw_key():
    """`EB-64`'s hazard, which has bitten this table before: a key with no
    localization row renders as the key."""
    mod = MOD_CS.read_text(encoding="utf-8")
    assert 'CasketKey + ".title"] =' in mod
    assert '"Tamakushi Casket",' in mod
    assert 'public const string CasketKey = "KLEEMOD-ARM_CASKET";' in \
        TIPS_CS.read_text(encoding="utf-8")
    # And the token's tip (the Casket pass).
    assert 'OpenTheCasketKey + ".title"] =' in mod
    assert '"Open the Casket",' in mod


def test_shell_guard_is_the_caskets_defensive_reader(overhaul):
    """SHELL GUARD, RE-AIMED (main session, 2026-09-28). The Casket pass
    retired the strike its second clause paid on, which left the clause dead;
    the fix makes the card read the Casket's count instead: "Gain 5 Block,
    plus 1 for each point in the Casket." Its window power is gone from both
    engines, and nothing closes a window any more."""
    assert any(c.id == "proto_kk_shell_guard"
               for c in loader.prototype_cards())

    import yaml
    sheet = yaml.safe_load(
        (REPO / "docs" / "prototype-surface.yaml").read_text(encoding="utf-8"))
    rows = sheet["cards"] if isinstance(sheet, dict) else sheet
    face = next(r for r in rows
                if r["id"] == "proto_kk_shell_guard")["description"]
    assert "for each point in the [gold]Casket[/gold]" in face
    assert "strikes" not in face
    assert "{CalculatedBlock:diff()}" in face

    card = SHELL_GUARD_CS.read_text(encoding="utf-8")
    assert "new FoldedCalculatedBlockVar(ValueProp.Move)" in card
    assert "get_CasketCount" in card or "CasketCount" in card
    assert "DynamicVars.CalculationBase.UpgradeValueBy(3m);" in card

    src = (REPO / "tier0" / "engine"
           / "kokomi_plan.py").read_text(encoding="utf-8")
    assert "def close_shell_guard" not in src
    combat = (REPO / "tier0" / "engine" / "combat.py").read_text(
        encoding="utf-8")
    assert "close_shell_guard" not in combat
    pet = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
           / "ProtoBakeKuragePower.cs").read_text(encoding="utf-8")
    assert "ShellGuardPower" not in pet
    powers = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
              / "KokomiOverhaulPowers.cs").read_text(encoding="utf-8")
    assert "class ShellGuardPower" not in powers


def test_the_debuff_answer_clause_is_silent_on_the_counting_relic():
    """`EB-433`'s panel clause is gated by matching the relic's sentence
    rather than its name, so it reads the relic a run holds. The Casket pass
    (2026-09-28) took the strike off the relic, and the clause -- "its
    answering strike is itself a Hydro hit" -- must go silent on the new face
    while still answering the old spellings a relic might carry.
    """
    from understudy import blindplay_render

    rx = blindplay_render._DEBUFF_ANSWERING_HIT
    now = ("Start each combat with the [gold]Bake-Kurage[/gold] and "
           "[gold]Open the Casket[/gold] in hand. Each [gold]Plan[/gold] it "
           f"carries out adds {C.KOKOMI_OVERHAUL_CASKET_PER_PLAN} to the "
           "Casket.")
    before = ("Start each combat with the [gold]Bake-Kurage[/gold]. Each debuff "
              "you apply lands a real [blue]2[/blue] [gold]Hydro[/gold] hit on "
              "that enemy.")
    assert not rx.search(now)
    assert rx.search(before)
