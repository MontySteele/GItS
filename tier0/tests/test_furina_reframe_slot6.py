"""Slot 6, the early probe: the two Evoke routes, measured against each other.

`review/ruled/furina-reframe-2026-08-29.md` §6.3 slot 6 states the worry in
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

2026-08-30 -- [USER] TOOK THAT PICK, and this file grew a second half. The
ruling keeps removal and gives the dedicated Evoke a member CHOICE, while
full-stage deployment goes on automatically evoking the front: Encore now buys
deliberate control, and overflow deployment stays the reward for filling the
stage. The arithmetic arm above is untouched and still reports what it always
reported -- the deploy pays more per energy, and §11.5's published rows stand
as published (R101b). The arm below measures what the ruling ADDED: the one
axis the deploy structurally cannot reach, which is taking a chosen member
that is not at the front.
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


def _evoke_card(aim=None):
    """The dedicated Evoke: the same energy, a printed Encore price (`F7`
    (1)), and it puts nothing back on the stage.

    `aim` is what the slot-6 ruling added -- the card names which member it
    removes. `aim=None` prints no aim and takes the front, which is the card
    the published §11.5 rows were measured with, so those rows are still
    exactly what this file produces."""
    fx = {"op": "salon_bow"}
    if aim is not None:
        fx["member"] = aim
    return Card(id="slot6_evoke", name="evoke", cost=1, type="skill",
                character="furina", encore_cost=EVOKE_ENCORE_PRICE,
                effects=[fx])


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


def test_the_unaimed_evoke_wins_on_no_measured_axis():
    """THE PUBLISHED FINDING, unchanged: with no aim printed on it, the
    dedicated Evoke is dominated on every axis this instrument measures --
    output, mint, price, board size. §11.5's rows are what this arm produces
    and they stand as published (R101b).

    This is now HALF the picture rather than all of it, and the half the
    slot-6 ruling did not move: the ruling kept the free overflow Evoke and
    kept its price at nothing, so on the arithmetic the deploy still buys more
    per energy. What the ruling added is measured by the test below, and the
    two together are the honest reading of this board.
    """
    for front in ("usher", "crabaletta", "chevalmarin"):
        deploy, evoke = _lines(front)
        assert evoke["damage"] <= deploy["damage"], front
        assert evoke["block"] <= deploy["block"], front
        assert evoke["fanfare"] <= deploy["fanfare"], front
        assert evoke["encore_spent"] >= deploy["encore_spent"], front
        assert evoke["stage"] <= deploy["stage"], front


# ======================================================================
# What the slot-6 ruling ADDED: the axis the deploy structurally cannot
# reach. "Keep removal, but let a dedicated Evoke choose which member to
# remove; full-stage deployment continues automatically evoking the front."
# ======================================================================

def test_the_deploy_can_only_ever_take_the_front_member():
    """The deploy half of the ruling, pinned as the thing that did NOT move.
    Whichever member the deploy card names -- and it names the one ENTERING --
    the member it takes off a full stage is the front, on every rotation of
    the board. This is what makes the aim below an axis rather than a
    preference."""
    for front in ("usher", "crabaletta", "chevalmarin"):
        st = _board(front)
        _play(st, _deploy_card())

        gone = [ev["member"] for ev in st.log
                if ev["event"] == "salon_evoke"]
        assert gone == [front], front


def test_the_dedicated_evoke_takes_a_member_the_deploy_cannot():
    """THE FINDING AS THE RULING LEFT IT, stated as the test that goes red if
    it stops being true. On the packet's own full-stage board there is now one
    thing the dedicated Evoke does that no deploy card can do at any price:
    it takes a member that is NOT at the front off the stage, chosen. The
    deploy's overflow Evoke is automatic and front-only by ruling, so this is
    a structural difference and not a number that could be tuned away.

    The arithmetic above is unchanged and still says the deploy pays more.
    Whether a player standing over the two cards can SEE that the aim is worth
    the Encore is slot 6's blind read, and no engine test can stand in for
    one -- which is the same limit §11.5 recorded for the original probe.
    """
    stage_after = {}
    for front in ("usher", "crabaletta", "chevalmarin"):
        # The member at the BACK of the queue: the one the deploy route can
        # never reach on this board, because a full-stage deploy pops index 0.
        back = _board(front).player.salon[-1]
        st = _board(front)

        _play(st, _evoke_card(aim=back))

        gone = [ev["member"] for ev in st.log if ev["event"] == "salon_evoke"]
        assert gone == [back], front
        assert back not in st.player.salon, front
        assert st.player.salon[0] == front, front   # the front is UNTOUCHED
        stage_after[front] = list(st.player.salon)

    # Three different boards, three different members removed: the aim is the
    # variable, and the board it leaves behind is different in each.
    assert len({tuple(v) for v in stage_after.values()}) == 3


def test_the_aimed_payoff_is_the_chosen_members_own():
    """Damage, Block, Fanfare and the Encore refund all route through the
    member the card NAMED, not through the front one. Pinned as an
    equivalence, which is the strongest form available here: aiming member X
    from any rotation pays exactly what an unaimed Evoke pays on the board
    where X happens to be front. Usher prints Block, Crabaletta damage and
    Chevalmarin an Encore refund, so the three rows also cover the three
    shapes the shipped roster has."""
    for aimed in ("usher", "crabaletta", "chevalmarin"):
        unaimed = _measure(aimed, _evoke_card())
        for front in ("usher", "crabaletta", "chevalmarin"):
            got = _measure(front, _evoke_card(aim=aimed))
            assert got == unaimed, (aimed, front)


def test_the_aim_is_the_evoke_legs_to_give(monkeypatch):
    """The flag-off guard this file owes, in the slice-1 style. With
    `FURINA_REFRAME_EVOKE` off, a card carrying an aim is the shipped bow: it
    takes the front member and the printed aim does nothing. Nothing about the
    aim can reach a build where the leg is off."""
    monkeypatch.setattr(FR, "FURINA_REFRAME_EVOKE", False)

    for front in ("usher", "crabaletta", "chevalmarin"):
        back = _board(front).player.salon[-1]
        st = _board(front)

        _play(st, _evoke_card(aim=back))

        assert [ev["member"] for ev in st.log
                if ev["event"] == "salon_final_bow"] == [front], front
        assert back in st.player.salon, front


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
