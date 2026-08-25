"""Behavioural pins for the eight EB-118 Phase-3 Window 3 rows (R211).

One window, three slices, eight sheet rows: three new Klee Spark sinks, two
new Furina rows, and three Kokomi rewrites that keep their card ids. Each
test plays a REAL sheet card and asserts what a player reads off it, so a
silent change to an arithmetic, a target spec or an ORDER has to break a test
before it can ship. Two of the eight are pinned on their order specifically
because the order is what the ruling settled.

The drafter half of the window gets a price pin at the bottom, on the same
ground the sheet pins stand on: `STATIC_SPARK_SPEND_COST` is a [USER]-held
value, and a later edit to it must not move a shipped offer-screen number
without a test saying so.
"""

import pytest

from tier0.content import loader, upgrades
from tier0.engine import combat
from tier0.engine.state import Bomb, Card
from tier0.tests.conftest import make_enemy, make_state
from tier05 import draft


def _play(state, card_id, energy=3):
    card = loader.get_card(card_id)
    state.player.energy = energy
    state.player.hand.append(card)
    combat.play_card(state, card)
    return card


def _events(state, name):
    return [ev for ev in state.log if ev["event"] == name]


def _price(card_id):
    """(base, upgraded) drafted price, to the four decimals the packet quotes."""
    card = loader.get_card(card_id)
    base = round(draft._static_power(card), 4)
    up = (round(draft._static_power(upgrades.apply_upgrade(card)), 4)
          if upgrades.has_upgrade(card_id) else None)
    return base, up


# --- W3-Klee: the three Spark sinks ----------------------------------------

def test_powder_charge_spends_two_sparks_and_detonates_at_plus_four():
    """The bridge card: 2 Sparks in, the target's whole Bomb pile out at +4
    each. Both halves in one play, and the Sparks come off the bank whatever
    the board does."""
    enemy = make_enemy(hp=200)
    state = make_state([enemy])
    state.player.sparks = 3
    enemy.bombs.extend([Bomb(damage=6), Bomb(damage=6)])

    _play(state, "powder_charge")

    assert state.player.sparks == 1                  # 3 - 2
    assert enemy.bombs == []
    assert enemy.hp == 200 - (6 + 4) - (6 + 4)


def test_powder_charge_is_unplayable_below_its_printed_price():
    """The price is a PLAYABILITY GATE, derived from the printed effect --
    `combat.spark_cost` reads the top-level `spend_spark` and the gate above
    it refuses the play. A short bank never pays a partial price."""
    state = make_state([make_enemy()])
    card = loader.get_card("powder_charge")
    state.player.energy = 3

    for bank, playable in ((0, False), (1, False), (2, True), (3, True)):
        state.player.sparks = bank
        assert combat.card_playable(state, card) is playable


def test_powder_charge_on_an_empty_board_still_burns_the_sparks():
    """The honest failure mode, pinned rather than described: no Bombs on the
    aim means the card does nothing at all, and it has already paid. The whole
    log is the spend."""
    enemy = make_enemy(hp=100)
    state = make_state([enemy])
    state.player.sparks = 3

    _play(state, "powder_charge")

    assert state.player.sparks == 1
    assert enemy.hp == 100
    assert _events(state, "bomb_detonation") == []


def test_hold_the_line_pays_the_branch_only_against_an_attack():
    """5 Block always, 6 more when an enemy intends to attack. It aims at
    nothing, so it is the one sink with no aiming exposure."""
    attacker = make_enemy(intents=[{"kind": "attack", "amount": 5}])
    state = make_state([attacker])
    state.player.sparks = 2

    _play(state, "hold_the_line")
    assert state.player.block == 11
    assert state.player.sparks == 0

    quiet = make_enemy(intents=[{"kind": "block", "amount": 5}])
    calm = make_state([quiet])
    calm.player.sparks = 2

    _play(calm, "hold_the_line")
    assert calm.player.block == 5


def test_hold_the_line_upgrade_raises_both_halves():
    """`{conditional_block: +3}` is the one W3 delta that moves a branch AND a
    top-level number together -- 5 -> 8 and 6 -> 9 -- which is why it is the
    only sink whose upgrade the offer screen can see."""
    up = loader.get_card("hold_the_line+")
    assert up.effects == [
        {"op": "spend_spark", "amount": 2},
        {"op": "block", "amount": 8},
        {"op": "conditional", "if": "enemy_intends_attack",
         "then": [{"op": "block", "amount": 9}]}]


def test_smoke_and_sparks_buys_exactly_one_stack_over_its_neighbour():
    """The printed exchange rate, asserted against the real neighbour rather
    than described: `surprise_visit` is the same rarity, cost and type and
    applies 2 Vulnerable for no Sparks; this applies 3 for two."""
    enemy = make_enemy()
    state = make_state([enemy])
    state.player.sparks = 2

    _play(state, "smoke_and_sparks")

    assert enemy.powers["vulnerable"] == 3
    assert state.player.sparks == 0

    neighbour = loader.get_card("surprise_visit")
    assert neighbour.rarity == "uncommon" and neighbour.cost == 1
    assert neighbour.effects == [
        {"op": "apply_power", "power": "vulnerable", "amount": 2,
         "target": "enemy"}]


def test_every_sink_prints_its_price_at_top_level():
    """A STRUCTURAL rule about this verb, not a preference about these cards:
    a `spend_spark` inside a conditional branch is invisible to the
    playability gate, so the payoff would fire unpaid."""
    for cid in ("powder_charge", "hold_the_line", "smoke_and_sparks"):
        card = loader.get_card(cid)
        assert card.effects[0] == {"op": "spend_spark", "amount": 2}
        assert combat.spark_cost(card) == 2


# --- W3-Furina -------------------------------------------------------------

def test_change_the_bill_rotates_then_performs_then_blocks():
    """The Salon control card, in the ruled order: the next performer goes to
    the back of the line, the NEW lead performs, and the printed Block lands.
    This is the first sheet row in the repo to print either Salon verb."""
    state = make_state([make_enemy(hp=200)])
    state.player.encore = 5
    state.player.salon = ["usher", "crabaletta", "chevalmarin"]

    _play(state, "change_the_bill")

    assert _events(state, "salon_rotate")[0]["company"] == [
        "crabaletta", "chevalmarin", "usher"]     # the usher goes to the back
    assert state.player.salon == ["crabaletta", "chevalmarin", "usher"]
    # ...and the NEW lead is who performs. A rotate that did not hand the tick
    # to the card it promoted would be a reorder with no control in it.
    assert _events(state, "salon_tick")[0]["member"] == "crabaletta"
    assert state.player.block == 3


def test_change_the_bill_on_an_empty_stage_is_a_legible_blank():
    """Both verbs whiff BY NAME and the printed Block still pays. A blank the
    log can explain is not the same thing as a silent one."""
    state = make_state([make_enemy()])
    state.player.salon = []

    _play(state, "change_the_bill")

    assert _events(state, "salon_rotate_whiffed")
    assert _events(state, "salon_perform_whiffed")
    assert state.player.block == 3


def test_take_it_from_the_top_pays_damage_only_off_the_bar():
    """5 Block unconditionally; the 10 arrives only if the Spotlight moved
    this turn. The bar is what the card is about, which is why the upgrade
    pays it off rather than the Block."""
    enemy = make_enemy(hp=100)
    state = make_state([enemy])
    state.spotlight_moved_this_turn = False

    _play(state, "take_it_from_the_top")
    assert state.player.block == 5
    assert enemy.hp == 100

    enemy2 = make_enemy(hp=100)
    moved = make_state([enemy2])
    moved.spotlight_moved_this_turn = True

    _play(moved, "take_it_from_the_top")
    assert moved.player.block == 5
    assert enemy2.hp == 90


def test_take_it_from_the_top_upgrade_moves_the_swing_not_the_block():
    """`{conditional_damage: +4}` -- the design-honest delta. It bumps every
    non-self damage op with a literal amount, and this card's only such op is
    the branch's, so the printed Block stays at 5."""
    up = loader.get_card("take_it_from_the_top+")
    assert up.effects == [
        {"op": "block", "amount": 5},
        {"op": "conditional", "if": "spotlight_moved_this_turn",
         "then": [{"op": "damage", "amount": 14, "target": "enemy"}]}]


# --- W3-Kokomi: three rewrites that keep their ids -------------------------

def test_the_two_renamed_rows_keep_their_ids():
    """R211 item 5, the R69 pattern, asserted as an identity rather than
    described: the identifier freezes and only the display string moves. The
    retired strings are burned in docs/reserved-card-names.txt."""
    assert loader.get_card("shell_of_sanctuary").name == "Salvage the Line"
    assert loader.get_card("the_tide_remembers").name == "Tide of Names"

    reserved = (loader.DOCS_DIR.parent / "docs"
                / "reserved-card-names.txt").read_text(encoding="utf-8")
    assert "Shell of Sanctuary |" in reserved
    assert "The Tide Remembers |" in reserved


def test_pearl_barrage_pays_five_plus_three_per_energy_chosen():
    """The ladder is 5 / 8 / 11 over the whole live range, because Kokomi's
    sheet has no card above cost 2. Pinned at both ends and in the middle."""
    for cost, expected in ((0, 5), (1, 8), (2, 11)):
        enemy = make_enemy(hp=200)
        state = make_state([enemy])
        victim = Card(id="victim", name="victim", cost=cost, type="skill",
                      effects=[])
        state.player.hand.append(victim)

        _play(state, "pearl_barrage")

        assert enemy.hp == 200 - expected
        assert victim in state.player.exhaust_pile


def test_pearl_barrage_on_an_empty_hand_is_a_reading_not_a_crash():
    """The selection row still emits, with size 0 and cost 0, and the card
    deals its base. "Nothing was there to take" is an answer."""
    enemy = make_enemy(hp=100)
    state = make_state([enemy])

    _play(state, "pearl_barrage")

    row = _events(state, "exhaust_selection")[0]
    assert row["size"] == 0 and row["cost"] == 0
    assert enemy.hp == 95


def test_salvage_the_line_draws_before_it_recalls():
    """THE RULED ORDER, and it is load-bearing. `recall_to_draw` puts the
    rescued card at index 0 of the draw pile and `draw` pops index 0, so
    recall-then-draw would put the rescued card STRAIGHT INTO HAND -- which
    defeats the rule that a retrieved card goes to the top of the draw pile
    and never to hand. draw -> recall -> gain_charge is the order that reads
    correctly."""
    state = make_state([make_enemy()])
    rescued = Card(id="rescued", name="rescued", cost=1, type="skill",
                   effects=[{"op": "damage", "amount": 9, "target": "enemy"}])
    ordinary = Card(id="ordinary", name="ordinary", cost=1, type="skill",
                    effects=[{"op": "block", "amount": 4}])
    state.player.exhaust_pile.append(rescued)
    state.player.draw_pile.append(ordinary)

    _play(state, "shell_of_sanctuary")     # id kept; the NAME is Salvage the Line

    assert [c.id for c in state.player.hand] == ["ordinary"]
    assert state.player.draw_pile[0] is rescued      # on top for NEXT draw
    assert state.player.charge == 2
    assert state.player.block == 4


def test_salvage_the_line_is_a_clean_no_op_on_an_empty_exhaust_pile():
    """The draw, the Charge and the Block all still pay."""
    state = make_state([make_enemy()])
    state.player.draw_pile.append(
        Card(id="ordinary", name="ordinary", cost=1, type="skill", effects=[]))

    _play(state, "shell_of_sanctuary")

    assert [c.id for c in state.player.hand] == ["ordinary"]
    assert state.player.charge == 2
    assert state.player.block == 4


def test_tide_of_names_is_wide_and_shallow_where_pearl_is_aimed_and_steep():
    """Two cards reading the same count with the same shape would be a clone.
    Different targets, different costs and different slopes are two jobs: the
    wide ladder is 5 / 7 / 9 and it lands on EVERY body."""
    left, right = make_enemy(hp=200, name="l"), make_enemy(hp=200, name="r")
    state = make_state([left, right])
    victim = Card(id="victim", name="victim", cost=2, type="skill", effects=[])
    state.player.hand.append(victim)

    _play(state, "the_tide_remembers")

    assert left.hp == right.hp == 200 - 9


def test_the_kokomi_pool_still_holds_seventy_six_rows():
    """R211 keeps the pool pinned: every Kokomi item in the window is a
    rewrite of an existing row, so neither the count nor the id list moves."""
    rows = [c for c in loader._card_index().values()
            if getattr(c, "character", None) == "kokomi"]
    assert len(rows) == 76
    assert "shell_of_sanctuary" in {c.id for c in rows}
    assert "the_tide_remembers" in {c.id for c in rows}


# --- the drafter half ------------------------------------------------------

@pytest.mark.parametrize("card_id, base, up", [
    ("powder_charge", 2.0, 5.0),
    ("hold_the_line", 0.0, 3.0),
    ("smoke_and_sparks", 1.0, 3.0),
])
def test_the_spend_dial_prices_the_three_sinks(card_id, base, up):
    """A pin on `STATIC_SPARK_SPEND_COST = 2.5`, so a later dial edit cannot
    move a shipped offer-screen price silently. The value is [USER]-held: at
    2.5 every sink loses 5.00 on both faces and `hold_the_line`'s base face
    lands on exactly zero, which is the safe direction under R194 but is a
    real offer-screen effect. 1.5 is the defensible smaller number in the same
    method, and moving to it is expected to break exactly this test."""
    assert draft.STATIC_SPARK_SPEND_COST == 2.5
    assert _price(card_id) == (base, up)


def test_the_gain_dial_stays_dead_and_no_shipped_spark_row_moved():
    """The asymmetry is the design position, and this is what it buys: R211
    kept `STATIC_SPARK_VALUE` at 0.0, so the drafter bump's archive scope is
    the three new rows and NOTHING ELSE. Every shipped Spark carrier, prices
    verified card by card."""
    assert draft.STATIC_SPARK_VALUE == 0.0
    assert {cid: _price(cid)[0] for cid in (
        "sparkly_treasure", "spark_collection", "hot_hands", "sugar_rush",
        "skip_and_hop", "cant_catch_me", "crackle", "warm_glow", "snap",
        "all_my_treasures", "da_da_da", "prune_witch_hunt")} == {
        "sparkly_treasure": 0.0, "spark_collection": 0.0, "hot_hands": 0.0,
        "sugar_rush": 0.0, "skip_and_hop": 2.0, "cant_catch_me": 2.0,
        "crackle": 3.0, "warm_glow": 6.0, "snap": 6.0,
        "all_my_treasures": 6.5, "da_da_da": 12.0, "prune_witch_hunt": 1.5}


def test_the_spotlight_rider_moves_one_shipped_price_not_two():
    """`directors_cut` does NOT re-price at any share, because BOTH its
    branches pay in dead dials -- energy and draw. Only `curtain_cue` moves,
    because its branches pay in Encore. Measured, and pinned because the
    register row expected two."""
    assert draft.STATIC_SPOTLIGHT_MOVED_SHARE == 0.167
    assert "spotlight_moved_this_turn" in draft.STATIC_STATE_CONDITIONS
    assert _price("directors_cut") == (0.0, 0.0)
    assert _price("curtain_cue")[0] == pytest.approx(0.4, abs=1e-3)
    # The whole point of taking the rider WITH the delta: before it, both
    # faces of the Furina reward priced 5.0000 and the offer screen could not
    # see the upgrade at all.
    base, up = _price("take_it_from_the_top")
    assert up > base
