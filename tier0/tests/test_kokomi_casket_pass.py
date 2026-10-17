"""THE CASKET PASS (2026-09-28): the Tamakushi Casket counts, Open the Casket
turns the count into Strength, and the pool moves.

[USER], in his words. On the relic, Forge-style over Vigor-style, because Vigor
"devolves into 'solve for lethal, press the I Win button'": "an artifact that
grants / tracks an alternative energy that builds by 1 for every Plan played,
and adds one 0-cost Retain / Exhaust card that converts that energy into
Strength." (2026-10-01: the token now costs 1 and has no Exhaust, so it pays
more than once; the four-kit review, Kokomi pick 1.) Counting: "when it's carried out". Rate: "1 strength per point
seems fine; we can adjust down if we need to." "the casket keeps counting." No
card spends the gauge: "We don't need this to be the equivalent to Regent's
stars or Klee's sparks. This should feel like a distinct effect." On the
Commons: "they shouldn't just be 10 copies of 'do x damage, or plan y'".

THE RE-FOUNDING (2026-10-12) retired the count, Open the Casket and the
count's readers (Driftglass, Depths' Judgment, What the Tokoyo Returns and
Took); their tests left with them. What stays is the pass's re-keyed payoffs
and moved numbers that survive, at their current values.

The sim half. NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

from tier0 import constants as C
from tier0.content import loader, upgrades
from tier0.engine import effects, kokomi_plan
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_plan import (  # noqa: F401
    carry_out, counts, kokomi_state, overhaul, plan_card)


def _row(cid):
    return loader.get_card(cid)


def _up(cid):
    return upgrades.apply_upgrade(loader.get_card(cid))


def _hit(state, card):
    enemy = state.enemies[0]
    before = enemy.hp
    effects.resolve_card(state, card)
    return before - enemy.hp


# --- C. the re-keyed payoffs -------------------------------------------------

def test_sango_isshin_is_eight_plus_two_to_all_per_carry_out_this_combat(overhaul):
    # [USER]'s run (2026-10-11): this combat, 2 per Plan; 10 plus 3 upgraded.
    a, b = make_enemy(hp=100, name="a"), make_enemy(hp=100, name="b")
    st = kokomi_state(enemies=[a, b])
    carry_out(st, [{"op": "energy", "amount": 1}])
    effects.resolve_card(st, _row("proto_kk_sango_isshin"))
    assert (a.hp, b.hp) == (90, 90)
    assert _up("proto_kk_sango_isshin").effects[0]["amount_formula"] == {
        "base": 10, "per": 3, "count": "plans_carried_out_this_combat"}


# --- D, E. the numbers --------------------------------------------------------

def test_the_moved_numbers(overhaul):
    wave = _row("proto_kk_second_wave")
    assert wave.rarity == "uncommon"
    assert wave.effects[0]["amount"] == 7
    assert _up("proto_kk_second_wave").effects[0]["amount"] == 9
    pincer = _row("proto_kk_pincer")
    # The Kokomi card pass (2026-10-11): 5 [6] twice.
    assert (pincer.effects[0]["amount"], pincer.effects[0]["times"]) == (5, 2)
    assert _up("proto_kk_pincer").effects[0]["amount"] == 6
    assert _row("proto_kk_opening_gambit").effects[0]["amount"] == 7
    assert _up("proto_kk_opening_gambit").effects[0]["amount"] == 9
    # (Ceremonial Garment left with the Kokomi pool overhaul, 2026-10-13.)
    rip = _row("proto_kk_riptide")
    assert (rip.effects[0]["amount"], rip.effects[0]["bonus_vs_debuff"]) == \
        (11, 3)
    # The re-founding (2026-10-12): the Plan is "Draw 3 cards" (4 upgraded).
    assert rip.plan == [{"op": "draw", "amount": 3}]
    rip_up = _up("proto_kk_riptide")
    assert (rip_up.effects[0]["amount"],
            rip_up.effects[0]["bonus_vs_debuff"]) == (14, 4)
    assert rip_up.plan == [{"op": "draw", "amount": 4}]


# --- G. the thirteen ------------------------------------------------------------

def test_the_commons(overhaul):
    # Kokomi review r8 (2026-10-14, item 4): 10 [13] to ALL and 10 [13]
    # Block now, no Plan (was 14, Plan 12 to ALL).
    shoal = _row("proto_kk_surging_shoal")
    assert shoal.cost == 2 and shoal.plan == []
    assert shoal.effects == [{"op": "damage", "amount": 10,
                              "target": "all_enemies"},
                             {"op": "block", "amount": 10}]
    shoal_up = _up("proto_kk_surging_shoal")
    assert (shoal_up.effects[0]["amount"],
            shoal_up.effects[1]["amount"]) == (13, 13)

    # Pearl Diver left the pool in the status batch (2026-10-01).
    # The cleanup pass (2026-09-29): 7 / 11, upgraded 9 / 14.
    press = _row("proto_kk_press_the_advantage")
    st = kokomi_state(enemies=[make_enemy(hp=100)])
    assert _hit(st, press) == 7
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}]))
    assert _hit(st, press) == 11
    press_up = _up("proto_kk_press_the_advantage")
    assert press_up.effects[0]["else"][0]["amount"] == 9
    assert press_up.effects[0]["then"][0]["amount"] == 14

    # Kokomi review r9 (2026-10-15, item 4): 6 [9] Block, Retain.
    shell = _row("proto_kk_shell_of_sanctuary")
    assert shell.plan == []
    assert shell.effects == [{"op": "block", "amount": 6}]
    assert _up("proto_kk_shell_of_sanctuary").effects[0]["amount"] == 9


def test_no_common_increases_deck_size(overhaul):
    """LAW: a Kokomi Common never adds a card to the DECK. (The re-founding's
    Commons that hand her a Sting, a Ward or a Companion add it to the hand
    for the combat, through the `kokomi` op, not a deck op.)"""
    creating = {"add_card", "generate_from_pool", "choose_companion"}
    for cid in C.KOKOMI_OVERHAUL_POOL_IDS:
        card = _row(cid)
        if card.rarity != "common":
            continue
        ops = {fx.get("op") for fx in (card.effects or []) + (card.plan or [])}
        assert not ops & creating, cid


def test_the_uncommons_and_the_rare(overhaul):
    # Tideturn: 8, plus 8 per Plan waiting (10 and 10 upgraded; the floor is
    # the Kokomi level pass, 2026-10-12).
    st = kokomi_state(enemies=[make_enemy(hp=100)])
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}]))
    kokomi_plan.schedule(st, plan_card([{"op": "energy", "amount": 1}]))
    assert _hit(st, _row("proto_kk_tideturn")) == 24
    up = _up("proto_kk_tideturn").effects[0]["amount_formula"]
    assert (up["base"], up["per"]) == (10, 10)
    assert _hit(kokomi_state(enemies=[make_enemy(hp=100)]),
                _row("proto_kk_tideturn")) == 8

    # Moon Signal left the pool in the status batch (2026-10-01); its
    # power stays registered (`test_moon_signal_reads_the_queue_...`).

    # Pearl Current: 2 x4 / Plan 3 to ALL x3 (3 x4 / Plan 4s upgraded; Plan
    # pricing 2026-10-11).
    current = _row("proto_kk_pearl_current")
    assert (current.effects[0]["amount"], current.effects[0]["times"]) == (2, 4)
    assert current.plan == [{"op": "damage", "amount": 3,
                             "target": "all_enemies", "times": 3}]
    current_up = _up("proto_kk_pearl_current")
    assert current_up.effects[0]["amount"] == 3
    assert current_up.plan[0]["amount"] == 4


# --- F. the offer -------------------------------------------------------------

def test_the_offer_is_seventy(overhaul):
    # Forty-six after the Casket pass; the cleanup pass (2026-09-29) cut two;
    # the feed pass (2026-09-29) cut Exposed Flank and added five; expansion
    # batch one (2026-09-29) cut The Clouds Like Waves and added 22; the
    # payoff pass (2026-10-01) cut Second Thoughts and added two; pool
    # completion (2026-10-01) added eight; the status batch (2026-10-01)
    # cut seven and added seven; the re-founding (2026-10-12) cut 24 and
    # added 20 and Gorou's four.
    ids = C.KOKOMI_OVERHAUL_POOL_IDS
    assert len(ids) == 78
    for cut in ("proto_kk_tide_chart", "proto_kk_cleansing_wave",
                "proto_kk_ripple", "proto_kk_well_laid",
                "proto_kk_sea_salt_prayer", "proto_kk_salt_line",
                "proto_kk_scout_ahead", "proto_kk_song_of_pearls",
                "proto_kk_exposed_flank", "proto_kk_second_thoughts",
                "proto_kk_pearl_diver", "proto_kk_moon_signal",
                # The re-founding (2026-10-12).
                "proto_kk_driftglass", "proto_kk_depths_judgment",
                "proto_kk_what_the_tokoyo_returns",
                "proto_kk_what_the_tokoyo_took", "proto_kk_massed_volley",
                "proto_kk_signal_arrow", "proto_kk_deep_current"):
        assert cut not in ids
        assert cut not in {c.id for c in loader.prototype_cards()}
    # And the co-op five (three, and pool completion's two) stay outside the
    # count.
    assert len(C.KOKOMI_OVERHAUL_MULTIPLAYER_IDS) == 5
