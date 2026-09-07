"""`EB-412`: Endless Waltz's +3 reaches the two members it deploys.

WHAT THE SEAT SAW (Furina r4 run 2 (c) 2, again at r7 fight 6). Under the
reframe a Deploy performs the member it fields at once, and Endless Waltz
printed its two deploys first and its crescendo last -- so the pair joined at
4 and 2, the unbumped numbers, while a Companion play one beat later performed
at 6. The buff was landing after the card's own deploys had already resolved.

THE FIX IS THE CARD'S CLAUSE ORDER, on the sheet, so both engines take it from
the same place: `docs/furina-cards.yaml` prints the `salon_damage_up` line
first and the codegen re-emits `EndlessWaltz.OnPlay` in that order.

AND THE REPLACEMENT MULTIPLIER SURVIVES THE MOVE, which is the half that had
to be built rather than reordered. `SALON_REPLACE_NUMERIC_MULT` doubles "a
deploy card's OTHER numerics", and the sim used to answer that by counting
bows that had already happened -- an answer that is 0 for a numeric printed
above the deploys. The mod never had the problem (`ReplacementDelta` asks
`WillReplace` off the PRE-PLAY company and the generated body captures the
value at the top of `OnPlay`), so the sim gained the same closed form:
`state.salon_will_replace_this_card`, seeded at `resolve_card` start, ORed
with the running count by `effects.salon_numerics_replaced`. Ordering is now
free in both engines, which is what makes the reorder above a fix and not a
trade.
"""

from __future__ import annotations

import random
from pathlib import Path

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects, furina_reframe
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy

REPO = Path(__file__).resolve().parents[2]
ENEMY_HP = 400


@pytest.fixture(autouse=True)
def manual_on(monkeypatch):
    """The deploy-performs clause is the reframe's MANUAL leg."""
    for flag in ("FURINA_REFRAME", "FURINA_REFRAME_MANUAL"):
        monkeypatch.setattr(furina_reframe, flag, True)


def _board(stage=()):
    p = loader.build_player("furina")
    p.salon = list(stage)
    p.powers["salon_member"] = len(p.salon)
    p.encore = 9                       # nothing dry: the question is the
    #                                    number, not the upkeep rate
    return CombatState(player=p, enemies=[make_enemy(hp=ENEMY_HP)],
                       rng=random.Random(3))


def _waltz(state):
    effects.resolve_card(state, loader.get_card("endless_waltz"))


def test_the_crescendo_stands_before_the_pair_it_fields_performs():
    state = _board()
    crab = C.SALON_MEMBERS["crabaletta"]["tick"]["damage"]
    usher = C.SALON_MEMBERS["usher"]["tick"]["block"]
    bump = 3

    _waltz(state)

    assert state.player.salon == ["crabaletta", "usher"]
    # The seat's two numbers: 4 and 2 were the unbumped pair.
    assert ENEMY_HP - state.enemies[0].hp == crab + bump
    assert state.player.block == usher + bump


def test_the_buff_is_applied_before_either_deploy_resolves():
    """The log is the order, so a later reordering cannot pass by arriving at
    the same totals through a different sequence."""
    state = _board()

    _waltz(state)

    events = [row["event"] for row in state.log]
    assert events.index("apply_power") < events.index("salon_deploy")


def test_a_full_stage_still_doubles_the_crescendo():
    """`SALON_REPLACE_NUMERIC_MULT`, from ABOVE the deploys. This is the
    reorder's whole cost if the closed form is missing, and it is the same
    assertion `test_furina_sheet.test_replacing_member_doubles_salon_power_
    without_clipping` makes -- kept here too because that one would still pass
    off a runtime count if the buff were printed last again."""
    state = _board(["usher", "usher", "usher"])

    _waltz(state)

    assert (state.player.powers["salon_damage_up"]
            == 3 * C.SALON_REPLACE_NUMERIC_MULT)


def test_a_stage_with_room_does_not_double_it():
    """The closed form is a predicate, not a licence: two deploys into an
    empty stage bow nobody, so the crescendo is its printed 3."""
    state = _board()

    _waltz(state)

    assert state.player.powers["salon_damage_up"] == 3


def test_the_predicate_is_scoped_to_the_card_that_set_it():
    """A card with no deploys never reads the flag -- `_resolve_card_bound`
    re-seeds it per play, so a deploy card cannot leave its answer behind for
    the card after it."""
    state = _board(["usher", "usher", "usher"])

    _waltz(state)
    assert state.salon_will_replace_this_card

    effects.resolve_card(state, loader.get_card("graceful_retreat"))
    assert not state.salon_will_replace_this_card
    assert not effects.salon_numerics_replaced(state)


def test_the_generated_card_applies_the_power_before_it_deploys():
    """CROSS-ENGINE SOURCE PIN. `OnPlay` needs a live `CombatState`, so what a
    headless test can read is the call ORDER the codegen emitted -- and the
    scaled value is still captured above all three, which is what keeps the
    doubling on the pre-play company the face read."""
    source = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Furina"
              / "Generated" / "EndlessWaltz.cs").read_text(encoding="utf-8")

    snapshot = source.index("var salonScaledPowerAmount =")
    apply_up = source.index("PowerCmd.Apply<SalonDamageUpPower>")
    crabaletta = source.index("SalonMember.Crabaletta)")
    usher = source.index("SalonMember.Usher)")

    assert snapshot < apply_up < crabaletta < usher
    assert "(int)salonScaledPowerAmount" in source
