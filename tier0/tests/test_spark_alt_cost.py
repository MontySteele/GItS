"""Sparks as an ALTERNATIVE COST (R213 E2) -- the flag, and both sides of it.

[USER], 2026-08-29: "The old base rule ('At 3 Sparks, your Attacks cost 0.
Playing one consumes 3') is being retired as the universal base mechanic;
Sparks become an ALTERNATIVE card cost." The packet is
`review/ruled/klee-sparks-2026-08-29.md`; its sec.9 is the independent seat's
doctrine read, and the picks this file exercises are 1, 3, 4, 5, 6 and 7.

THE FIRST TEST IS THE ONE THAT MATTERS. PICK 6 took option 1 -- both economies
side by side behind `C.SPARK_ALT_COST_ENABLED` -- and the whole value of that
option is that with the flag OFF every Klee number ever measured is still
comparable. That is an ACCEPTANCE CONDITION, not an intention, so it is pinned
as a digest of a fixed-seed fight's event log rather than asserted in prose.

WHAT IS PINNED HERE, section by section:
  * flag off, byte-identical -- the log digest, the starter, both drafter
    dials, and `spark_price == spark_cost` for every card;
  * the base rule retired -- no zeroing at any bank, no automatic consume;
  * the printed Spark price -- each of the five proto Attacks gates on its
    own price and pays exactly it;
  * the strict Rare Power -- unplayable at 2, playable at 3, pays 3 Sparks
    and 0 Energy; an already-priced Attack is unaffected (sub-pick (a)); a
    Skill is unaffected; an X-cost Attack is exempt (MINE, not the packet's);
  * the starter -- ten cards either way, one substitution each side;
  * the pilot -- a Spark is worth a share of the cheapest affordable sink,
    and worth nothing with no sink to buy.

NOTHING MEASURED ON ANY PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B). These
are shape assertions about an engine, not numbers about a game.
"""

import hashlib
import json

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat
from tier0.engine.combat import (card_cost, card_playable, run_fight,
                                 spark_cost, spark_power_price, spark_price)
from tier0.engine.state import Card
from tier0.pilot import policy
from tier0.pilot.policy import make_pilot
from tier0.tests.conftest import make_state
from tier05 import draft

SEED = 7
PROTO_ATTACKS = ("proto_kaboom_sink", "proto_spark_strike",
                 "proto_spark_sweep", "proto_spark_double_tap",
                 "proto_spark_blast", "proto_spark_finisher")


@pytest.fixture
def alt_cost(monkeypatch):
    """The flag ON, with every id-resolving cache cleared on both sides.

    `_card_prototype` is memoized and its answer for a `proto_` id DEPENDS on
    the flag, so a test that flips the flag without clearing it would read a
    KeyError cached from an earlier test. Cleared going in and coming out.
    """
    loader._card_prototype.cache_clear()
    monkeypatch.setattr(C, "SPARK_ALT_COST_ENABLED", True)
    yield
    loader._card_prototype.cache_clear()


def proto(card_id: str) -> Card:
    """A prototype row as a Card, independent of the flag's card door."""
    return next(c for c in loader.prototype_cards() if c.id == card_id)


def attack(cost=1, cid="swing", fx=None):
    return Card(id=cid, name=cid, cost=cost, type="attack",
                effects=fx if fx is not None else
                [{"op": "damage", "amount": 5, "target": "enemy"}])


def klee_fight(seed=SEED):
    pilot = make_pilot(loader.pilot_weights("demolition"))
    player = loader.build_player("klee")
    return run_fight(player, loader.build_encounter("punisher"), pilot,
                     seed=seed)


def log_digest(state) -> str:
    return hashlib.sha256(
        json.dumps(state.log, sort_keys=True, default=str
                   ).encode("utf-8")).hexdigest()


# --- 1. FLAG OFF IS BYTE-IDENTICAL -----------------------------------------

def test_the_flag_ships_off():
    """The quarantine. Everything below only matters while this holds."""
    assert C.SPARK_ALT_COST_ENABLED is False


def test_a_fixed_seed_klee_fight_is_unchanged_with_the_flag_off():
    """THE ACCEPTANCE CONDITION ON PICK 6, as a digest of the whole log.

    A prose claim that "nothing moved" is worth nothing; a hash of every
    event of a fixed-seed fight is worth exactly as much as the fight is
    deterministic, which it is. If any flag-off path in combat, the loader or
    the pilot moves by one line, this goes red and the OFF arm has stopped
    being comparable with every Klee number on record.

    THE DIGEST IS THE MEASUREMENT, not a golden file: it was taken on this
    branch's parent (a8b8552) before one byte of this arm was written.
    """
    assert log_digest(klee_fight()) == (
        "20b877d3411ccdc5306f6b8c0664c8d0f0dd7f9b30421d73af411aa8c3dbe9fa")


def test_the_starter_is_the_printed_starter_with_the_flag_off():
    assert loader.starting_deck("klee") == [
        "kaboom", "kaboom", "kaboom", "kaboom",
        "duck_and_cover", "duck_and_cover", "duck_and_cover", "duck_and_cover",
        "jumpy_dumpty", "pop"]
    assert not any(cid.startswith("proto_")
                   for cid in loader.starting_deck("klee"))


def test_the_shipped_drafter_dials_do_not_move():
    """Both are [USER]-held. PICK 7 gives the arm its OWN number and leaves
    these two exactly where R211 put them."""
    assert draft.STATIC_SPARK_VALUE == 0.0
    assert draft.STATIC_SPARK_SPEND_COST == 2.5
    assert draft.spark_gain_value() == 0.0
    assert draft.spark_spend_cost() == 2.5


def test_the_power_contributes_nothing_with_the_flag_off():
    """`spark_price` is `spark_cost` for every card, so every call site that
    was switched from one to the other is byte-identical here."""
    state = make_state()
    state.player.powers["spark_attack_cost"] = 1
    state.player.sparks = 9
    for card in (attack(cost=1), attack(cost=0), proto("proto_spark_strike")):
        assert spark_power_price(state, card) == 0
        assert spark_price(state, card) == spark_cost(card)


def test_the_base_rule_still_runs_with_the_flag_off():
    """The other half of byte-identical: the shipped rule, still shipped."""
    state = make_state()
    state.player.sparks = C.SPARKS_FOR_FREE_ATTACK
    state.player.energy = 3
    card = attack(cost=1)
    state.player.hand.append(card)

    assert card_cost(state, card) == 0          # the zeroing
    combat.play_card(state, card)
    assert state.player.sparks == 0             # the consume
    assert state.player.energy == 3


# --- 2. THE BASE RULE IS RETIRED UNDER THE FLAG -----------------------------

@pytest.mark.parametrize("bank", [0, 3, 4, 99])
def test_no_attack_is_zeroed_at_any_bank(alt_cost, bank):
    state = make_state()
    state.player.sparks = bank
    assert card_cost(state, attack(cost=1)) == 1
    assert card_cost(state, attack(cost=2)) == 2


def test_playing_an_attack_consumes_nothing(alt_cost):
    """"Playing one consumes 3" -- gone. The bank moves only when a printed
    price or the Power charges it, and this card has neither."""
    state = make_state()
    state.player.sparks = 5
    state.player.energy = 3
    card = attack(cost=1)
    state.player.hand.append(card)

    combat.play_card(state, card)

    assert state.player.sparks == 5
    assert state.player.energy == 2
    assert not [e for e in state.log if e["event"] == "sparks_spent"]


def test_a_full_bank_does_not_make_an_attack_playable_for_free(alt_cost):
    """The turn the retirement is FOR: at 3 Sparks and 0 energy the shipped
    rule hands you an Attack. Here it does not."""
    state = make_state()
    state.player.sparks = C.SPARKS_FOR_FREE_ATTACK
    state.player.energy = 0
    assert not card_playable(state, attack(cost=1))


# --- 3. THE PRINTED SPARK PRICE (PICK 3 / PICK 4) --------------------------

@pytest.mark.parametrize("card_id", PROTO_ATTACKS)
def test_each_proto_attack_gates_on_its_price_and_pays_it(alt_cost, card_id):
    card = proto(card_id)
    price = spark_cost(card)
    assert price > 0, f"{card_id} is meant to be Spark-priced"
    assert card.cost == 0, f"{card_id} must print 0 Energy"
    assert card.type == "attack"

    state = make_state()
    state.player.energy = 3

    state.player.sparks = price - 1
    assert not card_playable(state, card)       # the gate, one short

    state.player.sparks = price
    assert card_playable(state, card)
    state.player.hand.append(card)
    combat.play_card(state, card)               # resolves via _finish_play
    assert state.player.sparks == 0             # paid, exactly
    assert state.player.energy == 3             # and no energy


def test_the_five_pool_attacks_carry_the_packets_prices(alt_cost):
    """The prices are the packet's sec.4.2 table. Pinned so a later edit to
    the surface cannot move a price without moving a test."""
    assert {cid: spark_cost(proto(cid)) for cid in PROTO_ATTACKS} == {
        "proto_kaboom_sink": 1,
        "proto_spark_strike": 1,
        "proto_spark_sweep": 1,
        "proto_spark_double_tap": 2,
        "proto_spark_blast": 2,
        "proto_spark_finisher": 3,
    }


# --- 4. THE STRICT RARE POWER (PICK 5, wording (1), sub-pick (a)) ----------

def with_power(bank, energy=3):
    state = make_state()
    state.player.powers["spark_attack_cost"] = 1
    state.player.sparks = bank
    state.player.energy = energy
    return state


def test_an_attack_is_unplayable_below_three_sparks(alt_cost):
    for bank in (0, 1, 2):
        assert not card_playable(with_power(bank), attack(cost=1))


def test_an_attack_is_playable_at_three_and_pays_three_and_no_energy(alt_cost):
    state = with_power(3)
    card = attack(cost=1)
    state.player.hand.append(card)

    assert card_playable(state, card)
    assert card_cost(state, card) == 0          # "instead of their Energy"
    combat.play_card(state, card)

    assert state.player.sparks == 0
    assert state.player.energy == 3
    # THE ONE TURN WHERE THE RETIRED CONSUME COULD STILL BITE, and the reason
    # it is asserted here rather than only in section 2: this is the only
    # shape that satisfies the old branch's guard under the flag -- an Attack
    # with a printed cost, zeroed, at a bank above the retired threshold. If
    # the consume ran, it would take the bank first and the Power's own
    # payment would then be REFUSED against an empty one, landing on the same
    # final bank by a completely different route.
    assert not [e for e in state.log if e["event"] == "sparks_spent"]
    assert not [e for e in state.log
                if e["event"] == "spend_spark_refused"]
    assert [e["amount"] for e in state.log
            if e["event"] == "spend_spark"] == [3]


def test_an_already_priced_attack_is_unaffected(alt_cost):
    """SUB-PICK (a), which is the seat's pick and mine. (b) would have raised
    Fwoosh! from 1 to 3 and punished the cards the archetype drafts."""
    card = proto("proto_spark_strike")           # prints Spend 1
    state = with_power(1)
    assert spark_power_price(state, card) == 0
    assert spark_price(state, card) == 1
    assert card_playable(state, card)            # playable at ONE, not three


def test_a_skill_is_unaffected(alt_cost):
    """Attacks only. Energy becomes very nearly pure Skill currency, which is
    the payoff loop the Power is a bet on."""
    skill = Card(id="guard", name="guard", cost=1, type="skill",
                 effects=[{"op": "block", "amount": 5}])
    state = with_power(0)
    assert spark_power_price(state, skill) == 0
    assert card_cost(state, skill) == 1
    assert card_playable(state, skill)


def test_an_x_cost_attack_is_exempt(alt_cost):
    """MINE, NOT THE PACKET'S -- sec.5 is silent on X and this is the reading
    taken. An X card's cost IS its energy spend, so converting it to a flat 3
    Sparks would resolve it at X = 0 and deal nothing. It goes back to
    [USER]."""
    card = attack(cost="X")
    state = with_power(9)
    assert spark_power_price(state, card) == 0
    assert card_cost(state, card) == state.player.energy


def test_the_power_does_nothing_without_the_flag():
    """The Power is the arm's, not the shipped world's."""
    state = make_state()
    state.player.powers["spark_attack_cost"] = 1
    state.player.sparks = 0
    state.player.energy = 3
    assert card_playable(state, attack(cost=1))


# --- 5. THE STARTER (PICK 1, options 1 and 5) ------------------------------

def test_the_starter_substitutes_one_generator_and_one_sink(alt_cost):
    deck = loader.starting_deck("klee")
    assert len(deck) == 10                       # a substitution, not a rework
    assert deck.count("proto_pop_spark") == 1
    assert deck.count("proto_kaboom_sink") == 1
    assert deck.count("pop") == 0
    assert deck.count("kaboom") == 3             # ONE copy, not four -- mine
    assert deck.count("duck_and_cover") == 4
    assert deck.count("jumpy_dumpty") == 1


def test_the_substituted_basics_are_a_source_and_a_sink(alt_cost):
    """Regent's starter shape: one card that makes, one card that spends."""
    maker = proto("proto_pop_spark")
    assert [fx["op"] for fx in maker.effects] == ["place_bomb", "gain_spark"]
    assert spark_cost(maker) == 0

    spender = proto("proto_kaboom_sink")
    assert spark_cost(spender) == 1
    assert spender.cost == 0


def test_build_player_resolves_the_substituted_ids(alt_cost):
    """The door into the quarantine, from the side that uses it."""
    player = loader.build_player("klee")
    assert [c.id for c in player.draw_pile].count("proto_kaboom_sink") == 1
    assert [c.id for c in player.draw_pile].count("proto_pop_spark") == 1


def test_the_quarantine_still_holds_under_the_flag(alt_cost):
    """The door is exactly one id-resolution wide. MEMBERSHIP does not move,
    so no reward, pool or digest can reach a prototype."""
    assert not any(cid.startswith("proto_") for cid in loader._card_index())
    assert not any(c.id.startswith("proto_")
                   for c in loader.cards_in_pool("spark_commons"))
    with pytest.raises(KeyError):
        loader.get_card("proto_spark_strike_not_a_row")


# --- 6. THE PILOT (a share of the cheapest affordable sink) ----------------

def hand_state(cards, bank):
    state = make_state()
    state.player.sparks = bank
    state.player.energy = 3
    state.player.hand.extend(cards)
    return state


def test_a_spark_with_nothing_to_buy_is_worth_nothing(alt_cost):
    """The packet's sec.6.3, in code: "a Spark is worth exactly what you buy
    with it". No affordable sink in hand, no hold value."""
    scored = attack(cost=1)
    state = hand_state([scored], bank=5)
    assert policy._spark_unit_value(state, scored) == 0.0


def test_the_unit_is_the_cheapest_affordable_sink_not_the_best_rate(alt_cost):
    """Cheapest, not best-rate: the cheapest affordable sink is the use the
    bank is GUARANTEED to be able to make. Under-valuing spends more readily,
    which is R194's safe direction everywhere else in that file too.

    The pair is chosen so the two rules DISAGREE: Tinder Toss is the cheaper
    price and the WORSE rate, Bang Bang! the dearer price and the better one.
    A best-rate implementation would pick Bang Bang! and pass a test built on
    a pair where cheapest and best happen to coincide."""
    cheap = proto("proto_spark_sweep")           # Spend 1, 4 to ALL
    better_rate = proto("proto_spark_double_tap")  # Spend 2, 5 x 2
    scored = attack(cost=1)
    state = hand_state([cheap, better_rate, scored], bank=2)

    cheap_rate = policy._spark_bank_probe(state, cheap, 2) / 1
    other_rate = policy._spark_bank_probe(state, better_rate, 2) / 2
    assert other_rate > cheap_rate, "the fixture must make the rules disagree"
    assert policy._spark_unit_value(state, scored) == pytest.approx(cheap_rate)


def test_the_hold_term_uses_the_unit_and_not_the_retired_dial(alt_cost):
    """`_spark_hold_cost`'s leg 1, end to end. The old floor was a flat
    `C.PILOT_SPARK_VALUE` per Spark -- "a third of a free Attack" -- and this
    pins that the term now reads what the bank can actually buy instead."""
    scored = proto("proto_spark_strike")         # Spend 1
    other = proto("proto_spark_strike")          # a second copy, the sink
    state = hand_state([scored, other], bank=2)

    cost = policy._spark_hold_cost(state, scored)
    assert cost == pytest.approx(policy._spark_unit_value(state, scored))
    assert cost > C.PILOT_SPARK_VALUE            # and it is not the old dial


def test_an_unaffordable_sink_does_not_set_the_unit(alt_cost):
    """A price the bank cannot meet is not a use the bank has."""
    dear = proto("proto_spark_finisher")         # Spend 3
    scored = attack(cost=1)
    assert policy._spark_unit_value(
        hand_state([dear, scored], bank=2), scored) == 0.0
    assert policy._spark_unit_value(
        hand_state([dear, scored], bank=3), scored) > 0.0


def test_the_free_attack_leg_is_retired(alt_cost):
    """Leg 2 priced a free Attack forfeited by dropping under the bar. There
    is no bar."""
    state = hand_state([attack(cost=1)], bank=3)
    assert policy._spark_free_attack_loss(state, 3, 0) == 0.0


def test_the_free_attack_leg_still_fires_with_the_flag_off():
    state = hand_state([attack(cost=1)], bank=3)
    assert policy._spark_free_attack_loss(state, 3, 0) > 0.0


def test_the_hold_term_charges_the_powers_price_too(alt_cost):
    """`spark_price`, not `spark_cost`: an Attack the Power prices costs the
    pilot three Sparks of hold value, not zero."""
    sink = proto("proto_spark_strike")
    converted = attack(cost=1)
    state = hand_state([sink, converted], bank=3)
    state.player.powers["spark_attack_cost"] = 1

    assert policy._spark_hold_cost(state, converted) > 0.0


def test_the_pilot_plays_a_spark_priced_attack_it_can_afford(alt_cost):
    """End to end, through the real chooser: a Spark-priced Attack is a card
    the pilot reaches, not one the gate hides."""
    card = proto("proto_spark_strike")
    state = hand_state([card], bank=1)
    pilot = make_pilot(loader.pilot_weights("spark"))
    assert pilot(state) is card


# --- 7. PICK 7, the derived dial -------------------------------------------

def test_the_arms_dial_is_one_number_on_both_sides(alt_cost):
    assert draft.SPARK_ALT_VALUE == 4.0
    assert draft.spark_gain_value() == 4.0
    assert draft.spark_spend_cost() == 4.0


def test_the_dial_is_the_median_of_what_the_five_sinks_buy():
    """The arithmetic at `SPARK_ALT_VALUE`, re-run here so the comment and
    the constant cannot drift apart. Baselines are shipped 0-energy Attacks:
    Common 3.5 (`crackle` 3, `study_of_explosions` 4), Uncommon 6.0
    (`flame_on_the_wick`)."""
    aoe = draft.STATIC_AOE_MULT
    rates = sorted([
        (8 - 3.5) / 1,              # Fwoosh!
        (4 * aoe - 3.5) / 1,        # Tinder Toss
        (5 * 2 - 3.5) / 2,          # Bang Bang!
        (7 * aoe - 6.0) / 2,        # Dodoco Blast
        (18 - 6.0) / 3,             # Firework Finale
    ])
    assert rates[2] == draft.SPARK_ALT_VALUE
