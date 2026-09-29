"""THE CASKET PASS (2026-09-28): the Tamakushi Casket counts, Open the Casket
turns the count into Strength, and the pool moves.

[USER], in his words. On the relic, Forge-style over Vigor-style, because Vigor
"devolves into 'solve for lethal, press the I Win button'": "an artifact that
grants / tracks an alternative energy that builds by 1 for every Plan played,
and adds one 0-cost Retain / Exhaust card that converts that energy into
Strength." Counting: "when it's carried out". Rate: "1 strength per point
seems fine; we can adjust down if we need to." "the casket keeps counting." No
card spends the gauge: "We don't need this to be the equivalent to Regent's
stars or Klee's sparks. This should feel like a distinct effect." On the
Commons: "they shouldn't just be 10 copies of 'do x damage, or plan y'".

The sim half. The C# twin is `KleeTests/Prototype/KokomiCasketPassTests.cs`.
NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import effects, kokomi_plan
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_plan import (  # noqa: F401
    carry_out, counts, kokomi_state, overhaul, plan_card)


def _casket(**kw):
    st = kokomi_state(**kw)
    st.player.relic_hooks = [loader.OVERHAUL_CASKET_HOOK]
    return st


def _row(cid):
    return loader.get_card(cid)


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _hit(state, card):
    enemy = state.enemies[0]
    before = enemy.hp
    effects.resolve_card(state, card)
    return before - enemy.hp


# --- A. the relic counts carry-outs ----------------------------------------

def test_each_plan_carried_out_adds_one_while_she_holds_the_casket(overhaul):
    st = _casket(enemies=[make_enemy(hp=100)])
    assert st.kk_casket == 0
    carry_out(st, [{"op": "energy", "amount": 1}])
    assert st.kk_casket == C.KOKOMI_OVERHAUL_CASKET_PER_PLAN == 1
    carry_out(st, [{"op": "energy", "amount": 1}])
    assert st.kk_casket == 2

    # Without the relic: nothing. It is the relic's sentence.
    bare = kokomi_state(enemies=[make_enemy(hp=100)])
    carry_out(bare, [{"op": "energy", "amount": 1}])
    assert bare.kk_casket == 0


def test_a_plan_carried_out_twice_counts_twice(overhaul):
    """Second Wave's rider and Nereid's Ascension each make one entry two
    carry-outs, and each carry-out adds (the same rule every per-Plan reader
    in the arm keeps, `EB-709`)."""
    st = _casket(enemies=[make_enemy(hp=100)])
    kokomi_plan.schedule(st, plan_card(
        [{"op": "next_plan_extra_carry_out"}], cid="proto_kk_wave"))
    kokomi_plan.schedule(st, plan_card(
        [{"op": "energy", "amount": 1}], cid="proto_kk_after"))
    kokomi_plan.resolve_all(st)
    assert st.kk_casket == 3                # 1 + 2
    assert st.kk_plans_carried_out_this_turn == 3

    asc = _casket(enemies=[make_enemy(hp=100)])
    asc.player.powers[kokomi_plan.NEREIDS_ASCENSION] = 1
    carry_out(asc, [{"op": "energy", "amount": 1}])
    assert asc.kk_casket == 2


def test_dusk_and_change_of_plans_count_too(overhaul):
    st = _casket(enemies=[make_enemy(hp=100)])
    kokomi_plan.schedule(st, loader.get_card("proto_kk_breakwater"))
    kokomi_plan.resolve_dusk(st)
    assert st.kk_casket == 1
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}]))
    kokomi_plan.resolve_front(st)
    assert st.kk_casket == 2


def test_the_count_is_per_fight_and_never_rolled_by_the_turn(overhaul):
    st = _casket(enemies=[make_enemy(hp=100)])
    carry_out(st, [{"op": "energy", "amount": 1}])
    kokomi_plan.roll_turn(st)
    assert st.kk_casket == 1
    assert st.kk_plans_carried_out_this_turn == 0


# --- B. Open the Casket ------------------------------------------------------

def test_the_token_is_a_zero_cost_retain_exhaust_skill_in_no_pool(overhaul):
    card = kokomi_plan.open_the_casket_card()
    assert (card.cost, card.type, card.rarity) == (0, "skill", "token")
    assert card.retain and card.exhaust
    assert card.id not in C.KOKOMI_OVERHAUL_POOL_IDS


def test_opening_grants_strength_equal_to_the_count_and_empties_it(overhaul):
    st = _casket(enemies=[make_enemy(hp=100)])
    st.kk_casket = 3
    effects.resolve_card(st, kokomi_plan.open_the_casket_card())
    assert st.player.powers.get("strength") == 3 * \
        C.KOKOMI_OVERHAUL_CASKET_STRENGTH_PER_POINT
    assert st.kk_casket == 0
    # "the casket keeps counting"
    carry_out(st, [{"op": "energy", "amount": 1}])
    assert st.kk_casket == 1


def test_an_empty_casket_grants_nothing(overhaul):
    st = _casket(enemies=[make_enemy(hp=100)])
    effects.resolve_card(st, kokomi_plan.open_the_casket_card())
    assert "strength" not in st.player.powers


def test_the_relic_deals_the_token_on_turn_one_only(overhaul):
    st = _casket(enemies=[make_enemy(hp=100)])
    st.turn = 1
    kokomi_plan.deal_open_the_casket(st)
    assert [c.id for c in st.player.hand] == [kokomi_plan.OPEN_THE_CASKET]
    st.turn = 2
    kokomi_plan.deal_open_the_casket(st)
    assert len(st.player.hand) == 1

    bare = kokomi_state(enemies=[make_enemy(hp=100)])
    bare.turn = 1
    kokomi_plan.deal_open_the_casket(bare)
    assert bare.player.hand == []


def test_the_token_retains(overhaul):
    """A whole fight: the token dealt on turn one is still in hand on turn
    two if it was not played."""
    from tier0.engine.combat import run_fight
    ids = list(C.KOKOMI_OVERHAUL_STARTER_IDS)
    player = loader.build_player_from_ids("kokomi", ids)
    player.relic_hooks = [loader.OVERHAUL_CASKET_HOOK]
    seen = {}

    def pilot(state):
        seen.setdefault(state.turn, [c.id for c in state.player.hand])
        return None

    run_fight(player, [make_enemy(hp=400)], pilot, seed=3)
    assert kokomi_plan.OPEN_THE_CASKET in seen[1]
    assert kokomi_plan.OPEN_THE_CASKET in seen[2]


# --- C. the re-keyed payoffs -------------------------------------------------

def test_feint_is_four_plus_three_per_carry_out(overhaul):
    st = kokomi_state(enemies=[make_enemy(hp=100)])
    assert _hit(st, _row("proto_kk_feint")) == 4
    carry_out(st, [{"op": "energy", "amount": 1}])
    assert _hit(st, _row("proto_kk_feint")) == 7
    up = _up("proto_kk_feint")
    assert up.effects[0]["amount_formula"] == {
        "base": 6, "per": 3, "count": "plans_carried_out_this_turn"}
    assert up.plan[0]["amount"] == 2


def test_sango_isshin_is_eight_plus_six_to_all_per_carry_out(overhaul):
    # 2026-09-29: a base of 8; 10 plus 8 per Plan upgraded.
    a, b = make_enemy(hp=100, name="a"), make_enemy(hp=100, name="b")
    st = kokomi_state(enemies=[a, b])
    carry_out(st, [{"op": "energy", "amount": 1}])
    effects.resolve_card(st, _row("proto_kk_sango_isshin"))
    assert (a.hp, b.hp) == (86, 86)
    assert _up("proto_kk_sango_isshin").effects[0]["amount_formula"] == {
        "base": 10, "per": 8, "count": "plans_carried_out_this_turn"}


# --- D, E. the numbers --------------------------------------------------------

def test_the_moved_numbers(overhaul):
    wave = _row("proto_kk_second_wave")
    assert wave.rarity == "uncommon"
    assert wave.effects[0]["amount"] == 7
    assert _up("proto_kk_second_wave").effects[0]["amount"] == 9
    pincer = _row("proto_kk_pincer")
    assert (pincer.effects[0]["amount"], pincer.effects[0]["times"]) == (4, 2)
    assert _up("proto_kk_pincer").effects[0]["amount"] == 5
    assert _row("proto_kk_opening_gambit").effects[0]["amount"] == 7
    assert _up("proto_kk_opening_gambit").effects[0]["amount"] == 9
    assert _row("proto_kk_deep_current").effects[0]["amount"] == 7
    assert _up("proto_kk_deep_current").effects[0]["amount"] == 9
    rip = _row("proto_kk_riptide")
    assert (rip.effects[0]["amount"], rip.effects[0]["bonus_vs_debuff"]) == \
        (11, 3)
    assert rip.plan == [{"op": "energy", "amount": 2},
                        {"op": "draw", "amount": 1}]
    rip_up = _up("proto_kk_riptide")
    assert (rip_up.effects[0]["amount"],
            rip_up.effects[0]["bonus_vs_debuff"]) == (14, 4)


# --- G. the thirteen ------------------------------------------------------------

def test_the_commons(overhaul):
    volley = _row("proto_kk_massed_volley")
    assert (volley.cost, volley.effects[0]["amount"],
            volley.effects[0]["times"]) == (1, 3, 3)
    assert _up("proto_kk_massed_volley").effects[0]["amount"] == 4

    arrow = _row("proto_kk_signal_arrow")
    assert arrow.effects[0]["amount"] == 7
    assert arrow.plan == [{"op": "damage", "amount": 3,
                           "target": "all_enemies", "times": 2}]
    arrow_up = _up("proto_kk_signal_arrow")
    assert arrow_up.effects[0]["amount"] == 10
    assert arrow_up.plan[0]["amount"] == 4

    shoal = _row("proto_kk_surging_shoal")
    assert (shoal.cost, shoal.effects[0]["amount"], shoal.plan[0]["amount"]) \
        == (2, 14, 22)
    shoal_up = _up("proto_kk_surging_shoal")
    assert (shoal_up.effects[0]["amount"], shoal_up.plan[0]["amount"]) == \
        (18, 28)

    diver = _row("proto_kk_pearl_diver")
    assert diver.effects == [{"op": "draw", "amount": 1}]
    assert diver.plan == [{"op": "casket_gain", "amount": 2}]
    assert _up("proto_kk_pearl_diver").effects == [{"op": "draw", "amount": 2}]

    press = _row("proto_kk_press_the_advantage")
    st = kokomi_state(enemies=[make_enemy(hp=100)])
    assert _hit(st, press) == 6
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}]))
    assert _hit(st, press) == 10
    press_up = _up("proto_kk_press_the_advantage")
    assert press_up.effects[0]["else"][0]["amount"] == 8
    assert press_up.effects[0]["then"][0]["amount"] == 13

    shell = _row("proto_kk_shell_of_sanctuary")
    assert shell.plan_dusk
    assert shell.effects == [{"op": "draw", "amount": 1}]
    assert shell.plan == [{"op": "block", "amount": 9}]
    assert _up("proto_kk_shell_of_sanctuary").plan == [
        {"op": "block", "amount": 12}]

    glass = _row("proto_kk_driftglass")
    st = kokomi_state(enemies=[make_enemy(hp=100)])
    assert _hit(st, glass) == 5
    st.kk_casket = 4
    assert _hit(st, glass) == 9
    assert _up("proto_kk_driftglass").effects[0]["amount_formula"]["base"] == 7


def test_no_common_increases_deck_size(overhaul):
    """LAW: a Kokomi Common never adds a card. Open the Casket is the relic's
    token, not a Common's."""
    creating = {"add_card", "generate_from_pool", "add_random_companion"}
    for cid in C.KOKOMI_OVERHAUL_POOL_IDS:
        card = _row(cid)
        if card.rarity != "common":
            continue
        ops = {fx.get("op") for fx in (card.effects or []) + (card.plan or [])}
        assert not ops & creating, cid


def test_the_uncommons_and_the_rare(overhaul):
    # What the Tokoyo Returns: fetch the token out of the Exhaust Pile.
    st = _casket(enemies=[make_enemy(hp=100)])
    st.player.exhaust_pile = [kokomi_plan.open_the_casket_card()]
    effects.resolve_card(st, _row("proto_kk_what_the_tokoyo_returns"))
    assert [c.id for c in st.player.hand] == [kokomi_plan.OPEN_THE_CASKET]
    # None there: nothing happens.
    empty = _casket(enemies=[make_enemy(hp=100)])
    effects.resolve_card(empty, _row("proto_kk_what_the_tokoyo_returns"))
    assert empty.player.hand == []
    returns = _row("proto_kk_what_the_tokoyo_returns")
    assert (returns.cost, returns.exhaust) == (1, True)
    assert _up("proto_kk_what_the_tokoyo_returns").cost == 0

    # Depths' Judgment: 3 x the count (4 x upgraded).
    st = kokomi_state(enemies=[make_enemy(hp=100)])
    st.kk_casket = 5
    assert _hit(st, _row("proto_kk_depths_judgment")) == 15
    assert _up("proto_kk_depths_judgment").effects[0]["amount_formula"][
        "per"] == 4

    # Tideturn: 4 per Plan waiting (5 upgraded).
    st = kokomi_state(enemies=[make_enemy(hp=100)])
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}]))
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}]))
    assert _hit(st, _row("proto_kk_tideturn")) == 8
    assert _up("proto_kk_tideturn").effects[0]["amount_formula"]["per"] == 5

    # Moon Signal: a Power, cost 1 (0 upgraded).
    signal = _row("proto_kk_moon_signal")
    assert (signal.type, signal.cost) == ("power", 1)
    assert _up("proto_kk_moon_signal").cost == 0

    # Pearl Current: 2 x4 / Plan 2 to ALL x3 (3s upgraded).
    current = _row("proto_kk_pearl_current")
    assert (current.effects[0]["amount"], current.effects[0]["times"]) == (2, 4)
    assert current.plan == [{"op": "damage", "amount": 2,
                             "target": "all_enemies", "times": 3}]
    current_up = _up("proto_kk_pearl_current")
    assert current_up.effects[0]["amount"] == 3
    assert current_up.plan[0]["amount"] == 3

    # What the Tokoyo Took: double the count. Rare, 2, Exhaust (1 upgraded).
    took = _row("proto_kk_what_the_tokoyo_took")
    assert (took.rarity, took.cost, took.exhaust) == ("rare", 2, True)
    assert _up("proto_kk_what_the_tokoyo_took").cost == 1
    st = _casket(enemies=[make_enemy(hp=100)])
    st.kk_casket = 3
    effects.resolve_card(st, took)
    assert st.kk_casket == 6


def test_pearl_divers_plan_fills_the_casket(overhaul):
    st = _casket(enemies=[make_enemy(hp=100)])
    kokomi_plan.schedule(st, _row("proto_kk_pearl_diver"))
    kokomi_plan.resolve_all(st)
    # 2 from the clause and 1 from the relic for the carry-out itself.
    assert st.kk_casket == 3


def test_moon_signal_reads_the_queue_before_the_drain(overhaul):
    """"If 2 or more Plans are waiting" is read off the pre-drain queue, which
    `combat._player_turn` hands in beside Song of Pearls' read -- after the
    drain it could never be true."""
    st = kokomi_state(enemies=[make_enemy(hp=100)])
    st.player.powers[kokomi_plan.MOON_SIGNAL] = 1
    kokomi_plan.moon_signal(st, 1)
    assert st.kk_casket == 0
    kokomi_plan.moon_signal(st, C.KOKOMI_OVERHAUL_MOON_SIGNAL_THRESHOLD)
    assert st.kk_casket == 1

    import pathlib
    src = (pathlib.Path(__file__).resolve().parents[2] / "tier0" / "engine"
           / "combat.py").read_text(encoding="utf-8")
    assert src.index("kokomi_plan.moon_signal(") < src.index(
        "kokomi_plan.resolve_all(state)")


# --- F. the offer -------------------------------------------------------------

def test_the_offer_is_forty_six(overhaul):
    ids = C.KOKOMI_OVERHAUL_POOL_IDS
    assert len(ids) == 46
    for cut in ("proto_kk_tide_chart", "proto_kk_cleansing_wave",
                "proto_kk_ripple", "proto_kk_well_laid",
                "proto_kk_sea_salt_prayer", "proto_kk_salt_line"):
        assert cut not in ids
        assert cut not in {c.id for c in loader.prototype_cards()}
    # And the co-op three stay outside the count.
    assert len(C.KOKOMI_OVERHAUL_MULTIPLAYER_IDS) == 3
