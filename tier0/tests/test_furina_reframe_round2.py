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
from understudy import blindplay

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
    obs = {
        "screen": "combat", "state_type": "battle", "blocked": "",
        "combat": {
            "round": 1,
            "you": {"hp": 53, "max_hp": 78, "block": 0, "energy": 3,
                    "max_energy": 3, "meters": {name: amount},
                    "meter_max": {name: top} if top else {},
                    "powers": [], "potions": [], "potion_slots": 3,
                    "relics": []},
            "piles": {"draw": 5, "discard": 2, "exhaust": 0},
            "hand": [], "hand_repeats": 0, "enemies": [],
        },
        "commands": ["end turn"], "guardrail": "-", "items": [],
    }
    page = blindplay.render(obs)
    return next(line for line in page.splitlines()
                if line.startswith(f"- {name}: "))


def test_the_encore_row_prints_its_spend_rule_instead_of_the_gap():
    """The row the seat read said the feed carries "no rule for how it is
    spent". Where the mod declares one, the page prints it."""
    row = _meter_row("Encore", 4)

    assert "no rule for how it is spent" not in row
    assert "absorbs incoming damage before HP" in row


def test_a_meter_with_no_declared_rule_keeps_the_honest_gap():
    """The table is not a glossary: a meter it says nothing about still says
    what is missing and whose it is to carry."""
    row = _meter_row("Fanfare", 6)

    assert "no rule for how it is spent" in row


def test_the_encore_meter_rule_is_the_mods_own_sentence():
    """Held in step from this side, the discipline `ARM_KEYWORDS` is under:
    the page's clause is the mod's own, off `EncoreMeterPower`."""
    src = FURINA_CS.read_text(encoding="utf-8")
    body = src[src.index("class EncoreMeterPower"):]
    body = body[:body.index("public override PowerType")]
    printed = " ".join(re.findall(r'"((?:[^"\\]|\\.)*)"', body))

    assert "absorbs incoming damage before HP" in printed
    assert "absorbs incoming damage before HP" in blindplay.METER_RULES["Encore"]
