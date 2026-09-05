"""THE OPENING ENCORE (`EB-479`, R258) -- the sim half.

Under the reframe Furina starts every combat with
`furina_reframe.OPENING_ENCORE`, so turn one can pay one thing: a Spotlight
designation or a member performing wet rather than at 3/4. Both of those doors
cost 2, and she had 0. Rounds 5 to 8 each read her first turn as no decision,
and round 9 called the opening "by construction its own weakest version".

WHAT IS PINNED HERE: the amount, the site, the once-per-combat, the character
limb, and the flag off. The mod's twin is `FurinaReframeOpening.GrantEncore`,
on `AfterPlayerTurnStart`, and its own pins are in
`klee-mod/KleeTests/Prototype/FurinaReframeRuleTests.cs`.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE (R215 B): these are shape
assertions about an engine, not numbers about a game.
"""

import random

import pytest

from tier0 import constants as C
from tier0.engine import combat, effects, furina_reframe
from tier0.engine.state import Card, CombatState, Enemy, Player

FR = furina_reframe


@pytest.fixture
def arm(monkeypatch):
    """The MASTER flag and no leg: the opening belongs to the whole reframe,
    which is what `opening_encore` reads and `FurinaReframe.LiveFor` mirrors."""
    monkeypatch.setattr(FR, "FURINA_REFRAME", True)


@pytest.fixture
def manual_arm(monkeypatch):
    """The master AND the manual leg, which is the world the seats play: the
    deploy-performs clause lives inside `_deploy_salon_members` and is gated on
    `manual_active`, so the arrival performance only happens here."""
    monkeypatch.setattr(FR, "FURINA_REFRAME", True)
    monkeypatch.setattr(FR, "FURINA_REFRAME_MANUAL", True)


def _furina(**kw):
    """A Furina with the resource pair. `fanfare_cap` is the marker the
    engine's own Furina telemetry gates on, so a fixture without it is one
    half the log is blind to."""
    return Player(hp=200, max_hp=200, fanfare_cap=99,
                  character_id="furina", **kw)


def _state(player=None, turn=1):
    st = CombatState(player=player or _furina(),
                     enemies=[Enemy(hp=99, max_hp=99, name="paper",
                                    intents=[{"kind": "block", "amount": 0}])],
                     rng=random.Random(0))
    st.turn = turn
    return st


def _fight(player):
    """One real fight, won on the first turn by a 50-damage card, so the
    opening grant is the only thing that ever touches the buffer."""
    finisher = Card(id="finisher", name="Finisher", cost=0, type="attack",
                    effects=[{"op": "damage", "amount": 50, "target": "enemy"}])

    def pilot(s):
        return next((c for c in s.player.hand if c.id == "finisher"
                     and combat.card_playable(s, c)), None)

    player.draw_pile = [finisher]
    return combat.run_fight(
        player,
        [Enemy(hp=5, max_hp=5, name="paper",
               intents=[{"kind": "block", "amount": 0}])],
        pilot, seed=1)


def test_the_arm_opens_the_combat_with_two_encore(arm):
    st = _state()
    FR.grant_opening_encore(st)
    assert st.player.encore == FR.OPENING_ENCORE == 2


def test_the_shipped_kit_opens_on_nothing():
    """FLAG OFF IS THE SHIPPED OPENING, which is zero and always has been."""
    st = _state()
    FR.grant_opening_encore(st)
    assert st.player.encore == 0
    assert FR.opening_encore(st.player) == 0


def test_no_other_seat_is_paid(arm):
    """`is_furina`'s limb: in co-op the other seat may be Klee, and a bare
    flag read would hand him a buffer he has no rule for."""
    st = _state(player=Player(hp=200, max_hp=200, character_id="klee"))
    FR.grant_opening_encore(st)
    assert st.player.encore == 0


def test_it_is_turn_one_and_not_every_turn(arm):
    """`== 1` rather than `<= 1`, the opening Spark's own guard: a second turn
    pays nothing, and an extra first turn cannot pay twice."""
    st = _state(turn=2)
    FR.grant_opening_encore(st)
    assert st.player.encore == 0


def test_a_real_fight_opens_on_two_and_says_so_once(arm):
    """The SITE, through the engine rather than the reader: the grant lands in
    `_player_turn` at the same place `klee_overhaul.turn_start_late` does, so a
    fight that starts is a fight that opens with the buffer filled."""
    st = _fight(_furina())
    opened = [e for e in st.log if e["event"] == "fr_opening_encore"]
    assert [e["amount"] for e in opened] == [2]
    assert st.player.encore == 2          # nothing in the fight spends it


def test_a_real_fight_with_the_flag_off_opens_on_nothing():
    st = _fight(_furina())
    assert [e for e in st.log if e["event"] == "fr_opening_encore"] == []
    assert st.player.encore == 0


# ----------------------------------------------------------------------
# THE STAGE STARTS WITH A MEMBER (`EB-553`, R260)
# ----------------------------------------------------------------------
#
# Round 11 read both lanes' turn one as empty BY CONSTRUCTION: the stage starts
# unlit, so on turn one every Companion card prints "performs nobody". The
# natural lane's count is the fact -- zero empty turns in the fights where Salon
# Debut was in the opening hand, six of twenty-two otherwise. [USER] took the
# relic option over an Innate starter, by the analogy of the Necrobinder's Osty
# and the Defect's first orb: the starting relic fields Mademoiselle Crabaletta
# at combat start, and Salon Debut stays as printed and deploys a SECOND body.


def test_the_arm_opens_the_combat_with_crabaletta_on_stage(arm):
    st = _state()
    FR.field_opening_member(st)
    assert st.player.salon == [FR.OPENING_MEMBER] == ["crabaletta"]
    assert st.player.powers["salon_member"] == 1


def test_the_shipped_kit_opens_on_an_empty_stage():
    """FLAG OFF NOTHING IS FIELDED: the stage is empty until a card deploys
    onto it, which is the shipped rule and always has been."""
    st = _state()
    FR.field_opening_member(st)
    assert st.player.salon == []
    assert FR.opening_member(st.player) is None


def test_no_other_seat_gets_a_stage(arm):
    """In co-op the other seat may be Klee, who has no Salon at all."""
    st = _state(player=Player(hp=200, max_hp=200, character_id="klee"))
    FR.field_opening_member(st)
    assert st.player.salon == []


def test_the_stage_is_fielded_on_turn_one_and_never_again(arm):
    """`== 1` rather than `<= 1`, the opening Encore's own guard one rule over:
    a stage that refilled itself every turn would delete the Deploy cards'
    whole job."""
    st = _state(turn=2)
    FR.field_opening_member(st)
    assert st.player.salon == []


def test_the_member_is_named_and_never_rolled(arm):
    """`EB-416`'s finding one rule over: under the manual stage the FRONT
    member is the one a Companion play makes perform, so a rolled opening would
    decide for the player which member their first trigger fires."""
    assert FR.OPENING_MEMBER == "crabaletta"
    for seed in range(8):
        st = _state()
        st.rng = random.Random(seed)
        FR.field_opening_member(st)
        assert st.player.salon == ["crabaletta"]


def test_she_performs_on_arrival_and_the_arrival_is_free(manual_arm):
    """`EB-558`: A DEPLOY PERFORMS, and this one is not billed.

    THE DEFECT THIS REPLACES. The arrival used to pay
    `SALON_TICK_ENCORE_COST` out of the opening bank, so turn one opened on 1
    Encore -- and both of the doors R258 sized its 2 for cost 2 apiece, so the
    pick bought neither. [USER]'s own analogy for R260 settles it: "one free
    Osty". The Necrobinder's pet is out on turn one and nothing is billed for
    it being there.

    BOTH HALVES, because either alone would be a different rule: nothing is
    spent, AND she performs paid rather than at the dry three-quarters.
    """
    st = _state()
    FR.grant_opening_encore(st)
    assert st.player.encore == FR.OPENING_ENCORE

    FR.field_opening_member(st)

    assert st.player.encore == FR.OPENING_ENCORE == 2
    assert st.enemies[0].hp < 99          # she acted
    paid = [e for e in st.log if e["event"] == "salon_tick"]
    assert [e["paid"] for e in paid] == [True]
    # NOT a discount on the number, which is the other half of "performs paid":
    # the hit is the full tick and not `SALON_DRY_MULT` of it.
    dealt = 99 - st.enemies[0].hp
    assert dealt == effects.salon_tick_amount(st, "crabaletta", True)


def test_only_the_arrival_is_free_and_the_next_upkeep_bills_her(manual_arm):
    """The free pass is the one PERFORMANCE and not the turn (`EB-558`).

    A deploy a CARD makes pays its 1 exactly as it always has, and so does the
    turn-start upkeep that finds her still on the stage -- so the relic buys
    one performance, not a standing exemption.
    """
    st = _state()
    FR.grant_opening_encore(st)
    FR.field_opening_member(st)
    assert st.player.encore == 2

    effects._deploy_salon_members(st, 1, "crabaletta")
    assert st.player.encore == 2 - C.SALON_TICK_ENCORE_COST

    effects.salon_tick(st)
    assert st.player.encore == 0


def test_a_deploy_after_it_puts_a_second_body_on_the_stage(manual_arm):
    """Salon Debut stays as printed and deploys a SECOND body: duplicates on
    the stage are legal and always have been -- Grand Gala deploys Crabaletta
    twice on the shipped sheet."""
    from tier0.engine import effects

    st = _state()
    FR.field_opening_member(st)
    effects._deploy_salon_members(st, 1, "crabaletta")

    assert st.player.salon == ["crabaletta", "crabaletta"]
    assert st.player.powers["salon_member"] == 2


def test_a_real_fight_opens_with_the_stage_lit_and_says_so_once(arm):
    """The SITE, through the engine rather than the reader: the fielding lands
    in `_player_turn` one line after the opening Encore, so a fight that starts
    is a fight whose stage is already occupied."""
    st = _fight(_furina())
    fielded = [e for e in st.log if e["event"] == "fr_opening_stage"]
    assert [e["member"] for e in fielded] == ["crabaletta"]
    assert st.player.salon == ["crabaletta"]


def test_a_real_fight_with_the_flag_off_opens_unlit():
    st = _fight(_furina())
    assert [e for e in st.log if e["event"] == "fr_opening_stage"] == []
    assert st.player.salon == []


def test_a_real_fight_opens_on_the_whole_bank_with_the_stage_lit(manual_arm):
    """`EB-558`'s acceptance condition, through the engine rather than the
    reader: a fight that starts under the arm reaches its first decision with
    R258's bank intact AND a member already on the stage, which is the pair the
    two rulings were meant to hand turn one and did not."""
    st = _fight(_furina())
    assert [e["member"] for e in st.log
            if e["event"] == "fr_opening_stage"] == ["crabaletta"]
    assert st.player.salon == ["crabaletta"]
    assert st.player.encore == FR.OPENING_ENCORE == 2
    assert [e["paid"] for e in st.log if e["event"] == "salon_tick"] == [True]
