"""Slot 6, the early probe: the two Evoke routes, measured against each other.

`review/active/furina-reframe-2026-08-29.md` §6.3 slot 6 states the worry in
its own words: under §4.2 a deploy onto a full stage Evokes the front member to
make room, and the ruled text prices that at NOTHING -- the deploy Evokes the
old front, lands a replacement, and performs the replacement, all for the
card's energy. A dedicated Evoke card pays a printed `encore_cost` under `F7`
(1), expends the front, and puts nothing back: the stage comes out one member
lighter. If the asymmetry is as large as it reads, the family [USER]'s brief
calls central -- "Encore ... spent down to direct the Stage via Evoke-style
plays" -- is strictly inferior to a deploy card on every full stage.

WHAT THIS FILE IS AND IS NOT. It is an INSTRUMENT: it stages the packet's own
required board (a full stage, both cards in hand, one turn) and reports what
each line yields under the slice's rules. It is not the slot 6 reading. Slot 6
is a BLIND READ of a staged turn by two independent graders (`EB-149`,
`EB-170`), and no engine test can stand in for one -- a number says the deploy
line pays more, and only a grader can say whether a player standing over the
two cards can see that. The numbers below are what the graders' board will
actually do, committed before anyone reads a form.

R215 B BINDS THESE NUMBERS: nothing measured on a prototype is quotable in a
packet, a register or a commit message as a balance fact. They are quoted in
the packet's §11 as a STRUCTURAL reading -- which line dominates, on which
axis, and by how much on this one board -- and that is the only claim made
for them.

NO DESIGN FIX IS PROPOSED HERE, and that is deliberate under R212: what the
probe finds returns `F7` and §4.2's full-stage rule to [USER] together, as one
numbered pick, and Claude does not settle it.
"""

import random

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, furina_reframe
from tier0.engine.state import Card, CombatState
from tier0.tests.conftest import make_enemy

FR = furina_reframe

# The board, stated once. Three members is a FULL stage
# (`SALON_MEMBER_SLOTS`), 30 held Fanfare is Focus +3 -- the top tier at the
# shipped cap of 39 -- with headroom left so a mint is not silently wasted
# against the ceiling, and 9 Encore funds either line without either running
# dry (a dry line would measure `SALON_DRY_DAMAGE_MULT`, not the question).
STAGE = ["usher", "crabaletta", "chevalmarin"]
HELD_FANFARE = 3 * C.SALON_FOCUS_PER
ENCORE = 9
ENERGY = 3
EVOKE_ENCORE_PRICE = 2
ENEMY_HP = 400


@pytest.fixture(autouse=True)
def slice_on(monkeypatch):
    """All four legs, because slot 6 asks about the design and not a leg."""
    for flag in ("FURINA_REFRAME", "FURINA_REFRAME_MANUAL",
                 "FURINA_REFRAME_EVOKE", "FURINA_REFRAME_METER"):
        monkeypatch.setattr(FR, flag, True)


def _board(front):
    """The staged board, rotated so `front` is the member at the FIFO end --
    which is the member BOTH lines take, and the only thing that varies
    between the two boards below."""
    p = loader.build_player("furina")
    stage = list(STAGE)
    while stage[0] != front:
        stage.append(stage.pop(0))
    p.salon = stage
    p.powers["salon_member"] = len(p.salon)
    p.encore = ENCORE
    p.fanfare = HELD_FANFARE
    p.energy = ENERGY
    return CombatState(player=p, enemies=[make_enemy(hp=ENEMY_HP)],
                       rng=random.Random(11))


def _play(state, card):
    """The whole play, through the front door. `combat.play_card` calls
    `_finish_play` itself -- calling both is a card resolved twice, which on
    this board is TWO Evokes and a measurement of nothing."""
    state.player.hand.append(card)
    assert combat.card_playable(state, card), "the board must pose the choice"
    combat.play_card(state, card)


def _deploy_card():
    """The full-stage deploy: one energy, no Encore price, and under §4.2 it
    Evokes the front member, lands a replacement and performs it."""
    return Card(id="slot6_deploy", name="deploy", cost=1, type="skill",
                character="furina",
                effects=[{"op": "apply_power", "power": "salon_member",
                          "amount": 1, "member": "crabaletta"}])


def _evoke_card():
    """The dedicated Evoke: the same energy, a printed Encore price (`F7`
    (1)), and it puts nothing back on the stage."""
    return Card(id="slot6_evoke", name="evoke", cost=1, type="skill",
                character="furina", encore_cost=EVOKE_ENCORE_PRICE,
                effects=[{"op": "salon_bow"}])


def _measure(front, card):
    st = _board(front)
    hp_before = st.enemies[0].hp
    fanfare_before = st.player.fanfare
    encore_before = st.player.encore

    _play(st, card)

    return {
        "damage": hp_before - st.enemies[0].hp,
        "block": st.player.block,
        "fanfare": st.player.fanfare - fanfare_before,
        "encore_spent": encore_before - st.player.encore,
        "stage": len(st.player.salon),
    }


def _lines(front):
    return _measure(front, _deploy_card()), _measure(front, _evoke_card())


# ======================================================================
# The measurement, printed. `pytest -s` shows the table; the assertions
# below are what fails if the board stops posing the question.
# ======================================================================

def test_the_two_lines_are_measured_and_reported(capsys):
    rows = []
    for front in ("usher", "crabaletta", "chevalmarin"):
        deploy, evoke = _lines(front)
        rows.append((front, "deploy (full-stage Evoke)", deploy))
        rows.append((front, "dedicated Evoke card", evoke))
    with capsys.disabled():
        print("\n  SLOT 6 -- full stage, Focus +3, both cards in hand")
        print("  front         line                        dmg  blk  "
              "fanfare  encore  stage")
        for front, name, r in rows:
            print(f"  {front:<13}{name:<27}{r['damage']:>4} {r['block']:>4}"
                  f"{r['fanfare']:>8}{r['encore_spent']:>8}{r['stage']:>7}")
    assert rows


def test_the_deploy_line_pays_more_on_the_axis_the_front_member_prints():
    """The core of the asymmetry: the deploy gets the SAME Evoke the dedicated
    card gets -- same member, same multiplied Focus term -- and then a
    performance on top of it."""
    for front in ("usher", "crabaletta", "chevalmarin"):
        deploy, evoke = _lines(front)
        assert deploy["damage"] + deploy["block"] >= (
            evoke["damage"] + evoke["block"]), front


def test_the_deploy_line_mints_more_fanfare():
    """Two performances (an Evoke and the replacement's deploy-perform) mint
    more than one, so the free route also climbs the meter faster."""
    for front in ("usher", "crabaletta", "chevalmarin"):
        deploy, evoke = _lines(front)
        assert deploy["fanfare"] > evoke["fanfare"], front


def test_the_deploy_line_costs_less_encore():
    """`F7` (1) prices the dedicated Evoke and §4.2 prices the deploy's Evoke
    at nothing. The deploy still pays the upkeep of the performance it buys,
    which is the only Encore it spends."""
    for front in ("usher", "crabaletta", "chevalmarin"):
        deploy, evoke = _lines(front)
        assert deploy["encore_spent"] < evoke["encore_spent"], front


def test_the_deploy_line_leaves_the_stage_bigger():
    """The board fact behind the whole worry: after the deploy the stage is
    still full; after the dedicated Evoke it is one member lighter, and the
    next Companion trigger has one fewer thing to walk."""
    for front in ("usher", "crabaletta", "chevalmarin"):
        deploy, evoke = _lines(front)
        assert deploy["stage"] == C.SALON_MEMBER_SLOTS, front
        assert evoke["stage"] == C.SALON_MEMBER_SLOTS - 1, front


def test_the_dedicated_evoke_wins_on_no_measured_axis():
    """THE FINDING, stated as the test that would go red if it stopped being
    true. On this board there is no axis the instrument measures -- output,
    mint, price, board size -- on which paying Encore to Evoke beats deploying
    over the top. If a later change gives the dedicated Evoke something the
    deploy cannot give it (an alternative effect, an aimed member, a
    positional payoff), this test is where that shows up.
    """
    for front in ("usher", "crabaletta", "chevalmarin"):
        deploy, evoke = _lines(front)
        assert evoke["damage"] <= deploy["damage"], front
        assert evoke["block"] <= deploy["block"], front
        assert evoke["fanfare"] <= deploy["fanfare"], front
        assert evoke["encore_spent"] >= deploy["encore_spent"], front
        assert evoke["stage"] <= deploy["stage"], front


def test_the_asymmetry_is_the_flags_doing_and_not_the_shipped_engine(
        monkeypatch):
    """With `FURINA_REFRAME_MANUAL` off, a deploy onto a full stage is the
    shipped displacement bow and performs nothing, so the extra performance --
    the half slot 6 is about -- is the reframe's own addition and not a
    property the shipped game already had."""
    monkeypatch.setattr(FR, "FURINA_REFRAME_MANUAL", False)
    monkeypatch.setattr(FR, "FURINA_REFRAME_METER", False)

    deploy = _measure("usher", _deploy_card())

    assert deploy["fanfare"] == 0
    assert deploy["encore_spent"] == 0
