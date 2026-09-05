"""Furina reframe, ROUND TWO -- what the blind act-1 seat's run turned out to be.

`review/qa/furina-reframe-round-2-2026-09-04/opus-act1.md`, finding (c) 2:
"Banked Encore disappears, silently, and only when a member is on stage",
with three fights of evidence and one control turn. `EB-382` filed the
turn-start hooks as the suspect, because the arm suppresses the Salon upkeep
and no Encore decay exists.

THE TURN START IS NOT WHERE IT GOES, and this file is the pin that says so:
with the MANUAL leg on, a member on stage and four banked Encore, the whole
turn-start trigger set leaves the buffer at four. The spend the seat saw is
the SHIPPED post-Block absorption (`resources.absorb_into_encore`), which the
arm's METER leg silences -- it used to print one Fanfare per point absorbed,
and §4.1 retires that leg, so under the arm the buffer empties with no mark on
any surface at all.

The seat's own numbers reconcile against absorption exactly, which is why this
is a located cause rather than a guess. Fight 1, turn 2 into turn 3: the intent
read `2x4` after the Shatter un-froze it, so 8 damage arrived, HP went 57 -> 53
and Encore went 4 -> 0. Four absorbed, four to HP, eight total. Fight 2's
"control case" -- 1 Encore surviving a turn boundary -- is the turn the seat
recorded as "Took 0 damage", so what carried it was the absence of a hit and
not the absence of a member.

The sim has the same rule and has always had it (`tier0/engine/resources.py`
absorbs after Block, `combat.py:1398`), and it is not a defect there either:
what the round found is a legibility gap, closed page-side by
`understudy.blindplay_notes.METER_RULES`.
"""

import random
import re
from pathlib import Path

import pytest

from tier0.content import loader
from tier0.engine import effects, furina_reframe, resources
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy
from understudy import blindplay, blindplay_board

FR = furina_reframe

REPO = Path(__file__).resolve().parents[2]
FURINA_CS = (REPO / "klee-mod" / "KleeCode" / "Powers" / "FurinaResources.cs")


def _staged(members, encore=4, fanfare=0, seed=0):
    """The seat's board: a Furina with a company and a banked buffer."""
    p = loader.build_player("furina")
    st = CombatState(player=p, enemies=[make_enemy(hp=300)],
                     rng=random.Random(seed))
    p.salon = list(members)
    p.powers["salon_member"] = len(p.salon)
    p.encore = encore
    p.fanfare = fanfare
    return st


@pytest.fixture
def manual(monkeypatch):
    monkeypatch.setattr(FR, "FURINA_REFRAME", True)
    monkeypatch.setattr(FR, "FURINA_REFRAME_MANUAL", True)


@pytest.fixture
def meter(monkeypatch):
    monkeypatch.setattr(FR, "FURINA_REFRAME", True)
    monkeypatch.setattr(FR, "FURINA_REFRAME_METER", True)


# ======================================================================
# `EB-382` -- the turn start spends nothing
# ======================================================================

@pytest.mark.parametrize("banked", [4, 3, 1])
def test_a_staged_turn_start_spends_no_encore_under_the_arm(manual, banked):
    """The row's own scenario, at each of the three amounts it reports: one
    member on stage, N banked, the turn-start triggers run, N still banked."""
    st = _staged(["chevalmarin"], encore=banked)

    effects.player_turn_start_triggers(st)

    assert st.player.encore == banked
    assert st.player.salon == ["chevalmarin"]


def test_the_empty_stage_is_not_what_carried_the_control_turn(manual):
    """The seat read the control case as "no member, so nothing ate it". An
    empty stage and a staged one carry the same buffer, so the member was
    never the variable."""
    staged = _staged(["chevalmarin"], encore=1)
    empty = _staged([], encore=1)

    effects.player_turn_start_triggers(staged)
    effects.player_turn_start_triggers(empty)

    assert staged.player.encore == empty.player.encore == 1


def test_the_suppressed_upkeep_is_the_only_reason_it_survives():
    """The mirror half, and the one that would fail if the suppression leaked:
    with the arm OFF the same board pays the upkeep, so this file's other
    tests are asserting the arm's behaviour rather than an inert board."""
    st = _staged(["chevalmarin"], encore=4)

    effects.player_turn_start_triggers(st)

    assert st.player.encore < 4


# ======================================================================
# `EB-382` -- where it actually goes
# ======================================================================

def test_absorption_is_the_spend_the_seat_saw(manual, meter):
    """Fight 1's arithmetic, reproduced: 8 damage past Block against 4 banked
    Encore leaves 4 to reach HP and empties the buffer."""
    st = _staged(["chevalmarin"], encore=4)

    reached_hp = resources.absorb_into_encore(st, 8, "enemy_hit")

    assert reached_hp == 4
    assert st.player.encore == 0


def test_the_arm_makes_that_spend_leave_no_mark(manual, meter):
    """WHY IT READ AS A DISAPPEARANCE. The shipped engine printed one Fanfare
    per point absorbed, so the buffer emptying had a receipt on the meter
    beside it. §4.1 retires that leg, and nothing replaced the receipt."""
    st = _staged(["chevalmarin"], encore=4, fanfare=0)

    resources.absorb_into_encore(st, 4, "enemy_hit")

    assert st.player.encore == 0
    assert st.player.fanfare == 0


def test_the_shipped_engine_still_prints_that_receipt():
    """The flag-off half: absorption is a Fanfare source in a release build,
    which is what made the same spend visible before the arm."""
    st = _staged(["chevalmarin"], encore=4, fanfare=0)

    resources.absorb_into_encore(st, 4, "enemy_hit")

    assert st.player.encore == 0
    assert st.player.fanfare > 0


# ======================================================================
# `EB-382` -- the page says it now
# ======================================================================

def _meter_row(name, amount, top=None):
    """One combat page, rendered down to its meter row for `name`."""
    page = _page({name: amount}, top)
    return next(line for line in page.splitlines()
                if line.startswith(f"- {name}: "))


def _page(meters, top=None):
    """The rendered combat page for a set of already-labelled meters."""
    name = next(iter(meters), "")
    obs = {
        "screen": "combat", "state_type": "battle", "blocked": "",
        "combat": {
            "round": 1,
            "you": {"hp": 53, "max_hp": 78, "block": 0, "energy": 3,
                    "max_energy": 3, "meters": meters,
                    "meter_max": {name: top} if top else {},
                    "powers": [], "potions": [], "potion_slots": 3,
                    "relics": []},
            "piles": {"draw": 5, "discard": 2, "exhaust": 0},
            "hand": [], "hand_repeats": 0, "enemies": [],
        },
        "commands": ["end turn"], "guardrail": "-", "items": [],
    }
    return blindplay.render(obs)


def test_the_encore_row_prints_its_spend_rule_instead_of_the_gap():
    """The row the seat read said the feed carries "no rule for how it is
    spent". Where the mod declares one, the page prints it."""
    row = _meter_row("Encore", 4)

    assert "no rule for how it is spent" not in row
    assert "absorbs incoming damage before HP" in row


def test_a_meter_with_no_declared_rule_keeps_the_honest_gap():
    """The table is not a glossary: a meter it says nothing about still says
    what is missing and whose it is to carry.

    `EB-437` MOVED THE EXAMPLE. `Fanfare` used to stand here and now has a row
    of its own, so the denominator is a meter the mod declares no spend rule
    for -- which is what this test has always been about."""
    row = _meter_row("Burst Energy", 6)

    assert "no rule for how it is spent" in row


def test_the_fanfare_row_prints_the_rule_its_own_badge_states():
    """`EB-437`. TWO READOUTS ON ONE SCREEN, DISAGREEING.

    `FanfareMeterPower`'s arm face ends "Cards read it and none spends it";
    this block, with no row for the word, printed `METER_NOTE` -- "no maximum,
    and no rule for how it is spent". The r6 act-1 seat read both and filed the
    pair: "the two Fanfare readouts on the same screen say different things
    about whether a rule exists for spending it."

    Each sentence was true of its own source and the pair was not: the mod
    states the rule, so the page prints it rather than saying there is none."""
    row = _meter_row("Fanfare", 6)

    assert "no rule for how it is spent" not in row
    assert "cards read it and none spends it" in row


def test_the_fanfare_meter_rule_is_the_mods_own_sentence():
    """Held in step from this side, the Encore row's discipline: the page's
    clause is `FanfareMeterPower`'s own, off the arm face."""
    src = FURINA_CS.read_text(encoding="utf-8")
    body = src[src.index("class FanfareMeterPower"):]
    printed = " ".join(re.findall(r'"((?:[^"\\]|\\.)*)"', body))

    assert "Cards read it and none spends it" in printed
    assert ("cards read it and none spends it"
            == blindplay.METER_RULES["Fanfare"])


def test_the_encore_meter_rule_is_the_mods_own_sentence():
    """Held in step from this side, the discipline `ARM_KEYWORDS` is under:
    the page's clause is the mod's own, off `EncoreMeterPower`."""
    src = FURINA_CS.read_text(encoding="utf-8")
    body = src[src.index("class EncoreMeterPower"):]
    body = body[:body.index("public override PowerType")]
    printed = " ".join(re.findall(r'"((?:[^"\\]|\\.)*)"', body))

    assert "absorbs incoming damage before HP" in printed
    assert "absorbs incoming damage before HP" in blindplay.METER_RULES["Encore"]


# ======================================================================
# `EB-386` -- the three meters that meant nothing on the page
# ======================================================================

SPOTLIGHT_CS = (REPO / "klee-mod" / "KleeCode" / "Powers" / "SpotlightSystem.cs")


def _combat_page(resources):
    """One combat page, with the board's meters read off a wire-shaped
    `player.resources` blob -- which is where the hide has to bite."""
    meters = blindplay_board._combat(
        {"state_type": "battle",
         "player": {"hp": 53, "max_hp": 78, "block": 0, "energy": 3,
                    "max_energy": 3, "resources": resources, "status": [],
                    "hand": [], "relics": [], "potions": []},
         "battle": {"round": 3, "enemies": []}})["you"]["meters"]
    return _page(meters)


def test_the_three_spotlight_meters_do_not_reach_the_page():
    """"appeared and disappeared in the status list all run and I never worked
    out what any of them meant" -- and could not have. They are the mod's own
    bookkeeping: the mode is printed by the two named buffs it selects between,
    and the two counters back card conditions the cards print themselves."""
    page = _combat_page({"KLEEMOD_SPOTLIGHT_MODE": 2,
                         "KLEEMOD_SPOTLIGHT_MOVED": 1,
                         "KLEEMOD_SPOTLIGHT_PLAYS": 2})

    assert "Spotlight Mode" not in page
    assert "Spotlight Moved" not in page
    assert "Spotlight Plays" not in page


def test_the_spend_boost_accumulator_does_not_reach_the_page():
    """`EB-422`, the fourth of the same kind, found the same way three rounds
    later: "Spotlight Spend Boost: 30" sat in the status bar all fight with no
    gloss and no card naming it (round 5, run 1, fight 4).

    It is bookkeeping, not a currency. `SpotlightSystem.OnEncoreSpent` is its
    only writer and adds `OvationSpendBoostPower`'s amount on each Encore
    spend; `ClearSpendBoost` zeroes it at turn end. The rule is already on the
    page under the name a card prints -- "Standing Ovation", whose own text
    says what it multiplies and when -- and the running total is a quantity
    that sentence never promises, which is what the seat reported: "Standing
    Ovation says 10%; the meter said 30"."""
    page = _combat_page({"KLEEMOD_SPOTLIGHT_SPEND_BOOST": 30})

    assert "Spend Boost" not in page
    assert "30" not in page


def test_a_real_meter_beside_them_still_reaches_the_page():
    """The mutation guard: the hide is a named list, not a Spotlight-shaped
    hole that would take a future meter with it."""
    page = _combat_page({"KLEEMOD_SPOTLIGHT_MODE": 2, "KLEEMOD_ENCORE": 4})

    assert "- Encore: 4" in page
    assert "Spotlight Mode" not in page


def test_the_hidden_ids_are_the_ids_the_mod_registers():
    """Held in step from this side: a rename in `SpotlightSystem.cs` must not
    quietly put three undefined rows back on the board."""
    src = SPOTLIGHT_CS.read_text(encoding="utf-8")
    registered = set(re.findall(r'base\("(KLEEMOD_SPOTLIGHT_[A-Z_]+)"\)', src))

    assert blindplay_board.INTERNAL_METERS <= registered


def test_both_spotlight_modes_print_a_duration():
    """The feed carries no duration field, so a power that does not say when it
    ends reaches a reader as a buff with no end. Both modes say it now, which
    is what makes hiding the mode NUMBER safe: the named buff is the surface."""
    src = SPOTLIGHT_CS.read_text(encoding="utf-8")

    for power in ("CenterStagePower", "GuestCastPower"):
        body = src[src.index(f"class {power}"):]
        body = body[:body.index("public override PowerType")]
        printed = "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', body))
        assert "Lasts until the [gold]Spotlight[/gold] moves" in printed


# ==================================================================
# `EB-406` -- the second Ethereal Spotlight, and the face that says so
# ==================================================================

SPOTLIGHT_CARDS_CS = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Furina"
                      / "SpotlightCards.cs")
SPOTLIGHT_RELIC_CS = (REPO / "klee-mod" / "KleeCode" / "Relics"
                      / "EtherealSpotlightRelic.cs")


def test_the_redundant_spotlight_is_refused_and_not_priced():
    """`EB-406`. At 0 Encore the card was refused one turn and accepted the
    next at the same 0 Encore, Exhausting with no effect (Furina round 4, run
    1, fight 1).

    The price gate stepped aside once the mode WAS Guest Cast -- correctly, it
    names a price and there is none to fail -- and under the arm that is the
    only second play there is, because R228 (1) retires Center Stage. So the
    card now refuses the redundant copy on its own predicate, and the reason it
    gives is the redundancy rather than the price: banking Encore is not the
    way out of this one. The C# behaviour is pinned in
    `KleeTests/Prototype/FurinaSpotlightPriceGateTests.cs`; this holds the two
    sentences in step from the sim side.
    """
    system = SPOTLIGHT_CS.read_text(encoding="utf-8")
    body = system[system.index("DesignateOneModeIsRedundant(Creature? creature)"):]
    body = body[:body.index(";") + 1]
    assert "FurinaReframe.SpotlightLiveFor(creature)" in body
    assert "Mode(creature) == SpotlightMode.GuestCast" in body

    card = SPOTLIGHT_CARDS_CS.read_text(encoding="utf-8")
    assert "the Spotlight is already on your Companion cards" in card
    # ...and it is asked BEFORE the price, so a redundant copy at an empty
    # buffer is never reported as a shortfall.
    assert (card.index("DesignateOneModeIsRedundant(owner)")
            < card.index("DesignateOneModeIsUnpayable(owner)"))


def test_the_relics_arm_face_says_the_copy_it_hands_back_is_dead():
    """The other half of the row: the starter relic puts a fresh copy in hand
    every turn, and once the Spotlight is out every one of them is a dead
    Exhaust. The relic's face says so, and ONLY under the arm -- off it the
    selector has two modes and a second play re-aims, where the sentence would
    be false."""
    relic = SPOTLIGHT_RELIC_CS.read_text(encoding="utf-8")
    arm = relic[relic.index("#if PROTOTYPE_CARDS && FURINA_REFRAME"):
                relic.index("#else")]
    shipped = relic[relic.index("#else"):relic.index("#endif")]
    # `EB-437`: "Companions" is the noun the r6 seat read as the Salon
    # members, and the Spotlight reaches CARDS.
    assert "It does nothing once your " in arm
    # `EB-485` PUT THE DURATION ON THE END OF THAT CLAUSE: the lighting is a
    # power and dies with the fight, and the r10 seat priced the Spotlight as
    # a one-time purchase off this very sentence.
    assert "[gold]Companion[/gold] cards are lit for this combat." in arm
    assert "does nothing" not in shipped
