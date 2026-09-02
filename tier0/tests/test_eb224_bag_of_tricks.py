"""EB-224 -- *Bag of Tricks*, the first row priced at a MODE HEAD.

THE ROW. `proto_spark_mode_bombs`, 0, Skill, Uncommon, on the quarantined
prototype surface: *Choose one: Place 1 Bomb dealing 5 | Spend 3 Sparks: place
3 Bombs dealing 5.* The cheap mode is the shipped `pop` printed alone; the
expensive mode is `bomb_voyage`'s body, which ships at 2 Energy, with the bank
buying that Energy instead. Every number on the face is lifted off a shipped
face.

WHY IT IS ONLY NOW LEGAL. The written Spark-cost clause said the spend must
stay at the CARD's top level; the doctrine seat held the arm on it twice
(`review/ruled/klee-slice-1-2026-08-29.md` sec.6.1 and sec.6.1.1). R225
amended the clause on 2026-08-30 to read TOP LEVEL **or** the HEAD of a
`choose_one` MODE, and nothing nested or conditional. The seat's other clause,
D4, was already RESOLVED by `EB-182` -- which is the machinery this row runs
on and which this file therefore does not re-test in general; the general rule
is `test_eb182_mode_playability.py`. What is tested here is the rule ON THIS
ROW, which is the thing that could have been authored wrong.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B).
"""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import gen_klee_cards as gen                                   # noqa: E402
import gen_prototype_cards as proto_gen                        # noqa: E402

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import combat, effects
from tier05 import rewards

ROW_ID = "proto_spark_mode_bombs"
PRICE = 3


@pytest.fixture
def bag():
    rows = [c for c in loader.prototype_cards() if c.id == ROW_ID]
    assert rows, f"{ROW_ID} is not on the prototype surface"
    return rows[0]


@pytest.fixture
def modes(bag):
    fx, = bag.effects
    assert fx["op"] == "choose_one"
    return fx["modes"]


# --- the row, as authored --------------------------------------------------

def test_the_row_is_the_face_the_packet_and_the_seat_were_shown(bag, modes):
    """The arm was HELD, re-asked, and admitted WITHOUT re-authoring. So the
    face is pinned against the packet's own words rather than described: id,
    cost, type, rarity, and both mode bodies lifted whole off `pop` and
    `bomb_voyage`."""
    assert (bag.id, bag.name, bag.cost, bag.type, bag.rarity) == (
        ROW_ID, "Bag of Tricks", 0, "skill", "uncommon")

    shipped = loader._card_index()
    pop, = shipped["pop"].effects
    voyage, = shipped["bomb_voyage"].effects

    # Mode 1 IS the shipped twin printed alone, byte for byte.
    assert modes[0]["effects"] == [pop]
    # Mode 2 is `bomb_voyage`'s body behind the price, and the only delta
    # against the shipped card is that the bank buys its 2 Energy.
    assert modes[1]["effects"] == [{"op": "spend_spark", "amount": PRICE},
                                   voyage]
    assert shipped["bomb_voyage"].cost == 2


def test_the_price_is_the_slices_one_price(modes):
    """Three, the same figure the slice's other three arms charge -- the
    retired free-Attack threshold, LIFTED, so the pair asks whether the bank is
    worth more as this card than as the rule was."""
    head = modes[1]["effects"][0]
    assert head == {"op": "spend_spark", "amount": PRICE}


def test_the_spend_is_at_the_mode_head_and_nowhere_else(bag, modes):
    """R225's amended clause, read off the row. The spend is the FIRST effect
    of its mode -- which is what makes it a price -- and there is no other
    `spend_*` anywhere on the card, nested or otherwise. A spend one line
    further down would be a consequence the gate cannot see."""
    def spends(effs):
        return [e for e in effs if str(e.get("op", "")).startswith("spend_")]

    assert spends(bag.effects) == []          # not a CARD-level price
    assert combat.spark_cost(bag) == 0        # ... and the card line says so
    assert spends(modes[0]["effects"]) == []
    assert spends(modes[1]["effects"]) == [modes[1]["effects"][0]]


# --- the price derivation, on this row -------------------------------------

def test_the_mode_price_is_derived_from_the_printed_spend(state, modes):
    """`effects.mode_price` reads the meter and the number off the op, so the
    price shown and the price paid cannot drift apart. Mode 1 prices nothing
    and says so as None rather than as zero."""
    assert effects.mode_price(state, modes[0]) is None
    assert effects.mode_price(state, modes[1]) == ("sparks", "Sparks", PRICE)


# --- affordability: bank 2 against bank 3 ----------------------------------

def test_at_two_sparks_the_priced_mode_is_not_offered_and_the_card_lives(
        state, bag, modes):
    """One short. The expensive mode leaves the choose-a-card screen -- the
    0.111.0 decompile gives it no per-option disabled state to grey, so
    omission is the rule -- and the FREE mode keeps the card playable. That is
    the whole reason the price could not move to the card's cost line: at the
    top level a short bank would kill the free Bomb too."""
    state.player.sparks = 2
    assert effects.offered_modes(state, modes) == [0]
    assert combat.card_playable(state, bag)
    assert combat.modal_refusal(state, bag) is None
    assert effects._chosen_mode(state, modes, bag) == 0


def test_at_three_sparks_both_modes_are_offered(state, bag, modes):
    """The bank is the gate, not the card: nothing about the row changed
    between this test and the one above."""
    state.player.sparks = PRICE
    assert effects.offered_modes(state, modes) == [0, 1]
    assert combat.card_playable(state, bag)


def test_the_free_mode_is_offered_at_an_empty_bank(state, bag, modes):
    """Mode 1 prices nothing, so it is offered at zero Sparks -- and the card
    is therefore NEVER priced out. This row can not reach `modal_refusal`'s
    refusal branch, which is why the refusal SHAPE is exercised below on a
    fixture that can."""
    state.player.sparks = 0
    assert effects.offered_modes(state, modes) == [0]
    assert combat.card_playable(state, bag)


# --- the refusal shape -----------------------------------------------------

def test_the_refusal_names_this_rows_price_and_the_bank(state, modes):
    """`mode_refusal` on the priced mode: the printable half of the rule, which
    a staged-turn packet, the falsifier and a replay all reach through
    `combat.modal_refusal`. Asserted on THIS row's label and THIS row's price
    so a re-authored label cannot silently stop naming what is short."""
    state.player.sparks = 2
    assert effects.mode_refusal(state, modes[0]) is None
    assert effects.mode_refusal(state, modes[1]) == (
        "'Spend 3 [gold]Sparks[/gold]: place 3 [gold]Bombs[/gold] dealing 5' "
        "needs 3 Sparks, bank holds 2")


def test_a_card_with_this_price_on_every_mode_is_refused_whole(state):
    """The card-level half, exercised on the shape this row is one mode away
    from: price BOTH modes and the card has no line left to offer, so it is
    unplayable and the reason names each dead mode.

    This is deliberately a fixture and not the row. Bag of Tricks keeps a free
    mode by design, and a test that pretended otherwise would be testing a
    card nobody authored."""
    from tier0.engine.state import Card
    twin = Card(id="both_priced", name="t", cost=0, type="skill", effects=[
        {"op": "choose_one", "modes": [
            {"label": "Spend 3 Sparks: place 1 Bomb",
             "effects": [{"op": "spend_spark", "amount": PRICE},
                         {"op": "place_bomb", "amount": 1, "target": "enemy",
                          "bomb_damage": 5}]},
            {"label": "Spend 3 Sparks: place 3 Bombs",
             "effects": [{"op": "spend_spark", "amount": PRICE},
                         {"op": "place_bomb", "amount": 3, "target": "enemy",
                          "bomb_damage": 5}]}]}])
    state.player.sparks = 2
    assert effects.offered_modes(state, twin.effects[0]["modes"]) == []
    assert not combat.card_playable(state, twin)
    assert combat.modal_refusal(state, twin) == (
        "both_priced: no mode is affordable -- "
        "'Spend 3 Sparks: place 1 Bomb' needs 3 Sparks, bank holds 2; "
        "'Spend 3 Sparks: place 3 Bombs' needs 3 Sparks, bank holds 2")


# --- the pool: this row substitutes NOTHING --------------------------------

def test_the_row_replaces_no_shipped_row_in_any_pool():
    """THE STAGING PATH IS A GRANT BY ID, like its three slice-1 siblings.

    `C.SPARK_ALT_POOL_SUBS` is the SPARKS packet's own one-for-one conversion
    map (PICK 4) and carries none of the four slice-1 arms. The only shipped
    row this arm names is `pop`, its cheap mode's twin -- and `pop` is a BASIC
    starter card, substituted through the other seam entirely
    (`C.SPARK_ALT_STARTER_SUBS`), so it is not a pool row at all. There is
    nothing here to swap one-for-one, and inventing a donor Uncommon would be
    a picked number in a slice that has none.
    """
    assert ROW_ID not in C.SPARK_ALT_POOL_SUBS.values()
    assert ROW_ID not in dict(C.SPARK_ALT_STARTER_SUBS).values()
    # `pop` is where it always was: the starter seam, not the pool seam.
    assert dict(C.SPARK_ALT_STARTER_SUBS)["pop"] == "proto_pop_spark"
    assert "pop" not in C.SPARK_ALT_POOL_SUBS


@pytest.mark.parametrize("flag", [False, True])
def test_no_offer_surface_can_reach_the_row_on_either_flag(flag, monkeypatch):
    """The quarantine, stated as the thing a player could be handed. It holds
    with the Spark arm ON as well as off, because this row is not in the
    substitution map at all -- the flag is not what is keeping it away."""
    monkeypatch.setattr(C, "SPARK_ALT_COST_ENABLED", flag)
    # `loader.reset_caches()` rather than two loader memos by name: its own
    # docstring is the rule, and clearing `_substituted_card_index` alone
    # leaves `upgrades._upgrade_index` memoized against a substitution table
    # that no longer exists -- an id it says can be smithed and `get_card` can
    # then no longer resolve.
    loader.reset_caches()
    rewards.character_pool.cache_clear()
    try:
        pool = [c.id for cards in rewards.character_pool("klee").values()
                for c in cards]
        assert ROW_ID not in pool
        assert ROW_ID not in loader._card_index()
    finally:
        loader.reset_caches()
        rewards.character_pool.cache_clear()


# --- the codegen leg: the mode-head price reaches C# -------------------------

@pytest.fixture
def emitted():
    """The generated C# for this row, straight off the dev-only generator."""
    return proto_gen.plan().generated[ROW_ID]


def test_the_generator_emits_this_row_rather_than_blocking_it(emitted):
    """A prototype the emitter refuses cannot be staged, and `spend_spark`
    inside a mode body WAS refused until EB-224 added the branch resolver: the
    written clause only admitted a top-level Spark price, so the codegen
    grammar only admitted one there too."""
    assert "public sealed class ProtoSparkModeBombs" in emitted


def test_the_price_is_declared_once_and_read_by_the_gate_and_the_badge(
        emitted):
    """EB-182 + EB-220, on this row. ONE literal: the `ModePrices` table. The
    playability gate consults it, the screen filter consults it, and the mode
    FACE reads its own row out of it -- so the badge paints the very number the
    bank was measured against, with the Spark glyph, and no second copy exists
    to drift."""
    assert "new ModePrice(Meter.Sparks, 3)" in emitted
    assert emitted.split("ModePrices =")[1].lstrip().startswith("{\n        null,")
    assert ("protected override bool IsPlayable =>\n"
            "        ModalChoice.AnyAffordable(Owner, ModePrices);") in emitted
    assert ("ModalChoice.SelectAffordableMode(choiceContext, Owner, "
            "modeOptions, ModePrices)") in emitted
    assert ("public sealed class ProtoSparkModeBombsModeB : ModalOptionCard, "
            "IMeterPricedCard") in emitted
    assert ("public Meter PricedMeter =>\n"
            "        ProtoSparkModeBombs.ModePrices[1]!.Value.Meter;") in emitted
    assert ("public int PrintedMeterPrice =>\n"
            "        ProtoSparkModeBombs.ModePrices[1]!.Value.Amount;") in emitted
    # The free mode declares no price at all -- not a price of zero.
    assert ("public sealed class ProtoSparkModeBombsModeA : ModalOptionCard\n"
            in emitted)


def test_the_mode_head_spend_is_emitted_GUARDED(emitted):
    """THE DEFECT EB-224 CLOSED, and it is why this test is spelled out.

    `spend_spark` was in neither `BRANCH_OPS` nor `_emit_branch_op`. The first
    absence blocked the ROW; the second meant `emit()` -- which does not
    consult `blocked_reason`, and which `test_eb118_modal_parity`'s badge case
    calls directly -- produced a mode that declared a 3-Spark price, filtered
    the option in by it, and then placed the Bombs WITHOUT DEBITING THE BANK.
    An op in a price table with no resolver is an unpaid payoff.

    The resolver is the GUARDED form, matching `spend_charge`: a mode body has
    no `IsPlayable` of its own, so the early return is what makes the price a
    price if anything ever reaches the body past the screen."""
    assert ("if (!await SparkPower.Spend(choiceContext, Owner.Creature, 3, "
            "this)) return;") in emitted
    # ... and it precedes the payoff it pays for, three Bombs at 5.
    body = emitted.split("else\n        {")[1]
    assert body.index("SparkPower.Spend") < body.index("BombPower.Place")
    assert "for (var i = 0; i < 3; i++)" in body


def test_the_two_engines_agree_on_which_ops_may_head_a_priced_mode():
    """The parity that made this row legal in one engine and not the other.
    `effects.MODE_PRICE_OPS` (sim) and the codegen's `MODE_PRICE_OPS` name the
    same three meters, and every one of them must also be a legal BRANCH op --
    a meter the price table knows and the emitter does not is exactly the
    silent drop above."""
    assert set(effects.MODE_PRICE_OPS) == set(gen.MODE_PRICE_OPS)
    assert set(gen.MODE_PRICE_OPS) <= gen.BRANCH_OPS
    for op in gen.MODE_PRICE_OPS:
        assert gen.BRANCH_FIELDS[op] == {"op", "amount"}
