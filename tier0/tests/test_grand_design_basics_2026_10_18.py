"""GRAND DESIGN TAKES BASICS (2026-10-18), the sim side.

The ruling is review/active/open-design-items-2026-10-18.md, "Ruled
2026-10-18" ([USER]: "Ok, agreed on all defaults for both the PR and inazuma
companions"): Grand Design may plan a Basic card with no Plan line (Strike,
Defend), and that Plan plays the card as itself when it is carried out. Only
Grand Design opens the door; the jellyfish still refuses such a card. The C#
twins are `KokomiRefounding.PlansAsItself` / `WriteAsItself` and
`KokomiPlan.Kind.PlayAsItself`, pinned in
`klee-mod/KleeTests/Prototype/KokomiGrandDesignBasicsTests.cs`.
NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about an engine.
"""

import copy

import pytest

from tier0.content import loader
from tier0.engine import combat, kokomi_plan
from tier0.tests.conftest import make_enemy, make_state
from tier05 import rewards


IDLE = [{"kind": "block", "amount": 5}]


@pytest.fixture(autouse=True)
def caches():
    def clear():
        from tier0.content import upgrades
        loader.reset_arm_caches()
        rewards.character_pool.cache_clear()
        for fn in (upgrades._upgrade_index,
                   upgrades._prototype_upgrade_index):
            getattr(fn, "cache_clear", lambda: None)()
    clear()
    yield
    clear()


def kokomi_state():
    st = make_state(enemies=[make_enemy(hp=200, name="e0",
                                        intents=list(IDLE))], hp=80)
    st.player.character_id = "kokomi"
    st.player.element = "hydro"
    st.player.cadence = "catalyst"
    st.in_player_turn = True
    st.player.energy = 10
    return st


def card(cid):
    return copy.deepcopy(loader.get_card(cid))


def test_strike_and_defend_are_planned_as_themselves_and_nothing_else_is():
    assert kokomi_plan.plans_as_itself(card("strike"))
    assert kokomi_plan.plans_as_itself(card("defend"))
    # A card with a Plan line is written, not planned as itself.
    assert not kokomi_plan.plans_as_itself(card("proto_kk_kurages_oath"))
    assert kokomi_plan.grand_design_takes(card("proto_kk_kurages_oath"))
    # A non-Basic with no Plan line is still out.
    assert not kokomi_plan.grand_design_takes(card("proto_kk_evening_watch"))
    # The jellyfish itself still refuses a Strike.
    assert not kokomi_plan.can_be_written(card("strike"))


def test_grand_design_is_playable_on_a_hand_of_basics():
    st = kokomi_state()
    gd = card("proto_kk_grand_design")
    st.player.hand = [gd, card("strike")]
    assert combat.card_playable(st, gd) is True
    st.player.hand = [gd, card("proto_kk_evening_watch")]
    assert combat.card_playable(st, gd) is False


def test_a_planned_strike_deals_its_damage_next_turn_and_stays_in_the_deck():
    st = kokomi_state()
    gd = card("proto_kk_grand_design")
    strike, defend = card("strike"), card("defend")
    st.player.hand = [gd, strike, defend]
    # Grand Design draws 1 for each (the Kokomi finish pass, 2026-10-19): a
    # draw pile, so no reshuffle takes the planned cards back.
    st.player.draw_pile = [card("proto_kk_coral_bulwark") for _ in range(4)]
    combat.play_card(st, gd)
    assert len(st.kk_plan_queue) == 2
    assert all(e.clauses == [{"op": kokomi_plan.PLAY_AS_ITSELF}]
               for e in st.kk_plan_queue)
    # Moved, not played: both originals are in the discard pile, unspent.
    assert strike in st.player.discard_pile and defend in st.player.discard_pile
    assert [c.id for c in st.player.hand] == ["proto_kk_coral_bulwark"] * 2
    # One-line Plans: nothing to flip to.
    assert all(e.now_card is None for e in st.kk_plan_queue)
    hp = st.enemies[0].hp
    st.player.block = 0
    kokomi_plan.resolve_all(st)
    assert st.enemies[0].hp < hp                  # the Strike landed
    assert st.player.block > 0                    # the Defend's Block
    # Copies were played and exhausted; the originals stay in the deck.
    assert strike in st.player.discard_pile and defend in st.player.discard_pile
    assert [c.id for c in st.player.exhaust_pile].count("strike") == 1
    assert [c.id for c in st.player.exhaust_pile].count("defend") == 1


def test_plan_cards_are_written_first_then_basics_fill_the_rest():
    st = kokomi_state()
    gd = card("proto_kk_grand_design")
    oath = card("proto_kk_kurages_oath")
    st.player.hand = [gd, card("strike"), oath, card("strike"),
                      card("strike")]
    st.player.draw_pile = [card("proto_kk_coral_bulwark") for _ in range(4)]
    combat.play_card(st, gd)
    assert len(st.kk_plan_queue) == 3
    assert st.kk_plan_queue[0].source is oath
    assert [e.clauses for e in st.kk_plan_queue[1:]] == [
        [{"op": kokomi_plan.PLAY_AS_ITSELF}]] * 2
    assert sorted(c.id for c in st.player.hand) == (
        ["proto_kk_coral_bulwark"] * 3 + ["strike"])
