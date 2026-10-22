"""THE KOKOMI CARD PAPER V2 (2026-10-18), the sim side.

Paper `review/active/kokomi-cards-2026-10-18.md` sec.2, ruled picks 1 (b),
2 (a) and 3 (a) ([USER]: "On Kokomi, I'm good with all three - let's try that
and see if it works."). Four changes: Draft the Orders replaces Shell of
Sanctuary, Tidal Rebuke spends the Block twice over, Tidal Riposte stores its
bonus for the next Attack card, and Endless Shoal and Kurage Canopy skip a
Sting's or Ward's Plan. The C# twin is
`klee-mod/KleeTests/Prototype/KokomiCardsV2Tests.cs`. NOTHING MEASURED HERE IS
QUOTABLE (R215 B): shape assertions about an engine.
"""

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, kokomi_plan
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, card, carry_out, kokomi_state, write)


def _attacking(st, amount=5, times=1):
    for e in st.enemies:
        e.intents = [{"kind": "attack", "amount": amount, "times": times}]


def _face_up(st, c):
    st.player.hand.append(c)
    assert not kokomi_plan.plan_aimed_at_pet(st, c)
    combat.play_card(st, c)


# --- the pool -------------------------------------------------------------------

def test_draft_the_orders_takes_shell_of_sanctuarys_slot():
    ids = C.KOKOMI_OVERHAUL_POOL_IDS
    assert "proto_kk_draft_the_orders" in ids
    assert "proto_kk_shell_of_sanctuary" not in ids
    row = loader.get_card("proto_kk_draft_the_orders")
    assert (row.type, row.rarity, row.cost) == ("skill", "common", 1)


# --- 1. Draft the Orders --------------------------------------------------------

def test_the_discount_is_on_a_card_written_on_the_jellyfish():
    st = kokomi_state()
    st.player.powers[kokomi_plan.DRAFT_THE_ORDERS] = 1
    brine = card("proto_kk_brine_sting")
    assert kokomi_plan.plan_aimed_at_pet(st, brine)
    assert combat.card_cost(st, brine) == brine.cost - 1
    write(st, brine)
    assert st.player.energy == 10 - (brine.cost - 1)
    assert kokomi_plan.DRAFT_THE_ORDERS not in st.player.powers
    # Spent: the next write pays full price.
    feint = card("proto_kk_feint")
    assert combat.card_cost(st, feint) == feint.cost


def test_a_card_played_face_up_pays_full_price_and_keeps_it():
    st = kokomi_state()
    _attacking(st)
    st.player.powers[kokomi_plan.DRAFT_THE_ORDERS] = 1
    brine = card("proto_kk_brine_sting")
    assert combat.card_cost(st, brine) == brine.cost
    _face_up(st, brine)
    assert st.player.powers[kokomi_plan.DRAFT_THE_ORDERS] == 1


def test_a_planned_sting_does_not_spend_it():
    st = kokomi_state()
    st.player.powers[kokomi_plan.DRAFT_THE_ORDERS] = 1
    write(st, card(kokomi_plan.STING_ID))
    assert st.player.powers[kokomi_plan.DRAFT_THE_ORDERS] == 1


def test_it_is_gone_at_the_end_of_her_turn():
    """The whole fight loop: set on turn 1, gone by turn 2."""
    from tier0.tests.conftest import make_enemy
    seen = []

    def pilot(state):
        if state.turn == 1:
            state.player.powers[kokomi_plan.DRAFT_THE_ORDERS] = 1
        elif state.turn == 2 and not seen:
            seen.append(kokomi_plan.DRAFT_THE_ORDERS in state.player.powers)
        return None

    enemy = make_enemy(hp=500, intents=[{"kind": "block", "amount": 5}])
    player = kokomi_state().player
    combat.run_fight(player, [enemy], pilot, seed=1)
    assert seen == [False]


def test_the_seat_page_says_the_cut_is_for_one_planned_card():
    from understudy import blindplay_notes, blindplay_render
    you = {"powers": [{"name": "Draft the Orders",
                       "text": "The next card you [gold]plan[/gold] this turn "
                               "costs [blue]1[/blue] less."}]}
    out = blindplay_render._one_use_discount_note(you)
    assert out == ["", blindplay_notes.PLAN_DISCOUNT_NOTE.format(
        power="**Draft the Orders**")]


# --- 3. Tidal Rebuke -------------------------------------------------------------

def test_tidal_rebuke_loses_the_block_and_deals_twice_it():
    st = kokomi_state(n_enemies=2)
    _attacking(st)
    st.player.block = 9
    rebuke = card("proto_kk_tidal_rebuke")
    _face_up(st, rebuke)
    assert st.player.block == 0
    assert [e.hp for e in st.enemies] == [200 - 18, 200 - 18]


def test_tidal_rebuke_with_no_block_deals_nothing():
    st = kokomi_state()
    _attacking(st)
    st.player.block = 0
    _face_up(st, card("proto_kk_tidal_rebuke"))
    assert st.enemies[0].hp == 200


# --- 4. Tidal Riposte ------------------------------------------------------------

def test_a_fully_blocked_multi_hit_attack_stores_the_bonus_once():
    st = kokomi_state()
    _attacking(st, amount=3, times=3)
    st.player.powers[kokomi_plan.TIDAL_RIPOSTE] = 8
    st.player.block = 20
    combat._enemy_turn(st, st.enemies[0])
    assert st.player.powers[kokomi_plan.TIDAL_RIPOSTE_CHARGE] == 8
    assert st.enemies[0].hp == 200            # no damage back any more


def test_an_attack_that_gets_through_stores_nothing():
    st = kokomi_state()
    _attacking(st, amount=5, times=2)
    st.player.powers[kokomi_plan.TIDAL_RIPOSTE] = 8
    st.player.block = 7                       # the second hit gets through
    combat._enemy_turn(st, st.enemies[0])
    assert kokomi_plan.TIDAL_RIPOSTE_CHARGE not in st.player.powers


def test_the_stored_bonus_stacks_and_rides_every_hit_of_one_attack():
    def pearl(charge):
        st = kokomi_state()
        _attacking(st)
        if charge:
            st.player.powers[kokomi_plan.TIDAL_RIPOSTE_CHARGE] = charge
        _face_up(st, card("proto_kk_pearl_current"))
        return st, 200 - st.enemies[0].hp

    base_st, base = pearl(0)
    st, dealt = pearl(16)                     # two fully blocked attacks
    assert dealt - base == 16 * 4             # Pearl Current hits 4 times
    assert kokomi_plan.TIDAL_RIPOSTE_CHARGE not in st.player.powers


def test_a_write_and_a_carried_out_plan_do_not_spend_it():
    st = kokomi_state()
    st.player.powers[kokomi_plan.TIDAL_RIPOSTE_CHARGE] = 8
    write(st, card("proto_kk_pearl_current"))
    assert st.player.powers[kokomi_plan.TIDAL_RIPOSTE_CHARGE] == 8
    carry_out(st)
    assert st.player.powers[kokomi_plan.TIDAL_RIPOSTE_CHARGE] == 8


def test_a_skill_does_not_spend_it():
    st = kokomi_state()
    _attacking(st)
    st.player.powers[kokomi_plan.TIDAL_RIPOSTE_CHARGE] = 8
    _face_up(st, card("proto_kk_draft_the_orders"))
    assert st.player.powers[kokomi_plan.TIDAL_RIPOSTE_CHARGE] == 8


# --- 5. Endless Shoal and Kurage Canopy -----------------------------------------

def test_endless_shoal_skips_a_sting_or_ward_plan():
    st = kokomi_state()
    st.player.powers[kokomi_plan.ENDLESS_SHOAL] = 1
    write(st, card(kokomi_plan.STING_ID))
    write(st, card(kokomi_plan.WARD_ID))
    st.player.hand.clear()
    carry_out(st)
    assert st.player.hand == []
    write(st, card("proto_kk_brine_sting"))
    carry_out(st)
    assert [c.id for c in st.player.hand] == [kokomi_plan.STING_ID]


def test_kurage_canopy_skips_a_sting_or_ward_plan():
    """Kokomi defence pass (2026-10-22): Battle Formation's count, so a Sting
    or Ward Plan is not one of the 2."""
    st = kokomi_state()
    st.player.powers[kokomi_plan.KURAGE_CANOPY] = 1
    write(st, card(kokomi_plan.STING_ID))
    write(st, card("proto_kk_brine_sting"))
    st.player.hand.clear()
    carry_out(st)
    kokomi_plan.kurage_canopy(st)
    assert st.player.hand == []
