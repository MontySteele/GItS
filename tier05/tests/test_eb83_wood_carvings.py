"""Wood Carvings converts EXACT, one pin per option (EB-83).

`EB-68`'s last unconverted event, and the acceptance its BACKLOG row states is
narrow: *all three options convert exact*. So this file is three pins plus the
machinery each one needed, and every number in it is the binary's --
`Models.Events.WoodCarvings`, `Models.Cards.Peck`, `Models.Cards.ToricToughness`
and `Models.Enchantments.Slither`, read out of `sts2.dll` v0.111.0 (the build
`STATE.md` pins) on 2026-09-02. The wiki is not the authority for any of them:
it carries no card text for the two colorless cards, and Slither is absent from
its Enchantments page altogether.

WHAT "EXACT" MEANS HERE, given R184 ruled a RESKIN. Two of the three options
hand over a base-game colorless card, which design principles §4.7 forbids
shipping, so *Peck* and *Toric Toughness* arrive as `tengu_flurry` and
`chinju_ward` (names ruled R231). Exact is therefore about FUNCTION and NUMBER
and never about the name: 1 cost / Attack / 2 damage × 3, and 2 cost / Skill /
5 Block now plus 5 at the start of each of the next 2 turns.

  1. the event and its three options -- shape, locks, and the numbers;
  2. `transform_starter_into`, the event-layer key the conversion needed;
  3. `slither`, and the delayed Block its neighbour prints, in a real fight.
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C
from tier0.content import enchantments, loader, upgrades
from tier0.engine import combat
from tier0.engine.state import CombatState, Enemy
from tier05 import events


def _st(**kw):
    base = dict(character="klee", archetype="demolition", hp=50, max_hp=70,
                gold=200, deck_ids=list(loader.starting_deck("klee")))
    base.update(kw)
    return events.EventState(**base)


def _event():
    return events.get_event("wood_carvings")


def _opt(label):
    return next(o for o in _event()["options"] if o["label"] == label)


# ---------------------------------------------------------------------------
# 1. The event: three options, the harvest's shape, the wiki's lock.
# ---------------------------------------------------------------------------

def test_the_event_is_reachable_in_act_1_and_only_act_1():
    """`### [act1] Wood Carvings` in docs/sts2-events-harvest.txt:430."""
    by_act = [{e["id"] for e in events.pool_for(act)}
              for act in range(len(C.RUN_ACTS))]
    assert "wood_carvings" in by_act[0]
    assert all("wood_carvings" not in s for s in by_act[1:])


def test_all_three_options_convert_and_none_was_dropped():
    """The acceptance in one line: three options, no approximation, no

    two-of-three ship. The labels are the harvest's own -- Bird / Snake /
    Torus -- rather than the conversion gallery's Teyvat reskins, which are a
    flavor artifact and not what this file is pinning."""
    assert [o["label"] for o in _event()["options"]] == ["Bird", "Snake",
                                                         "Torus"]
    assert _opt("Bird")["transform_starter_into"] == "tengu_flurry"
    assert _opt("Snake")["enchant"] == {"name": "slither"}
    assert _opt("Torus")["transform_starter_into"] == "chinju_ward"


def test_all_three_are_offered_on_a_printed_starter_deck():
    """No option is locked at run start on any character: every printed deck
    holds basics for the two transforms, and Slither takes any card whose cost
    is a number."""
    for character, archetype in (("klee", "demolition"), ("furina", "salon"),
                                 ("kokomi", "priest")):
        st = _st(character=character, archetype=archetype,
                 deck_ids=list(loader.starting_deck(character)))
        labels = [o["label"] for o in events.available(_event(), st)]
        assert labels == ["Bird", "Snake", "Torus"], character


def test_bird_transforms_one_starter_into_the_peck_reskin():
    st = _st()
    before = list(st.deck_ids)
    events.resolve(random.Random(4), _event(), _opt("Bird"), st)
    moved = [(a, b) for a, b in zip(before, st.deck_ids) if a != b]
    assert len(moved) == 1                       # ONE card, transformed
    was, now = moved[0]
    assert loader.peek_card(was).rarity == events.STARTER_RARITY
    assert now == "tengu_flurry"
    assert len(st.deck_ids) == len(before)       # a transform, not an add
    assert st.log[-1]["transformed"] == [was, "tengu_flurry"]


def test_torus_transforms_one_starter_into_the_toric_toughness_reskin():
    st = _st()
    before = list(st.deck_ids)
    events.resolve(random.Random(4), _event(), _opt("Torus"), st)
    moved = [(a, b) for a, b in zip(before, st.deck_ids) if a != b]
    assert len(moved) == 1
    was, now = moved[0]
    assert loader.peek_card(was).rarity == events.STARTER_RARITY
    assert now == "chinju_ward"
    assert len(st.deck_ids) == len(before)


def test_snake_enchants_exactly_one_deck_card_with_slither():
    st = _st()
    before = list(st.deck_ids)
    events.resolve(random.Random(4), _event(), _opt("Snake"), st)
    moved = [(a, b) for a, b in zip(before, st.deck_ids) if a != b]
    assert len(moved) == 1
    was, now = moved[0]
    # No amount on the id: Wood Carvings grants it with `Enchant<Slither>(c,
    # 1m)`, but nothing in the class reads that amount, so a number here would
    # be a number nothing spends.
    assert enchantments.split(now) == (was, "slither", None)
    assert st.log[-1]["enchanted"] == now


@pytest.mark.parametrize("cid,cost,ctype,rarity,effects", [
    # Models.Cards.Peck: base(1, Attack, Event, AnyEnemy),
    #                    DamageVar(2m, Move) + RepeatVar(3).
    ("tengu_flurry", 1, "attack", "event",
     [{"op": "damage", "amount": 2, "times": 3, "target": "enemy"}]),
    # Models.Cards.ToricToughness: base(2, Skill, Event, Self),
    #                    Turns 2m + BlockVar(5m, Move); OnPlay gains the Block
    #                    and then applies ToricToughnessPower for Turns.
    ("chinju_ward", 2, "skill", "event",
     [{"op": "block", "amount": 5},
      {"op": "block_at_turn_start", "amount": 5, "turns": 2}]),
])
def test_the_two_reskins_carry_the_decompiled_numbers(cid, cost, ctype,
                                                      rarity, effects):
    card = loader.peek_card(cid)
    assert (card.cost, card.type, card.rarity) == (cost, ctype, rarity)
    assert card.effects == effects


def test_neither_reskin_is_reachable_as_loot():
    """`rarity: event` is not in RARITY_ODDS, so no reward, shop, Neow or
    Ancient roll can reach these two: the event IS the only door, which is
    what makes them event cards rather than pool cards."""
    from tier05 import rewards
    assert "event" not in C.RARITY_ODDS
    for character in ("klee", "furina", "kokomi"):
        pool = {c.id for cs in rewards.character_pool(character).values()
                for c in cs}
        assert not ({"tengu_flurry", "chinju_ward"} & pool), character


def test_neither_reskin_ships_an_upgrade_path():
    """The standing rule for this sheet, and for `chinju_ward` it is also the
    only honest option today: its published 5 -> 7 bump would need a
    `block_at_turn_start` upgrade-delta key, and the delta keys are a shared
    schema with the C# emitter that R20/R92 says lands atomically with every
    consumer or not at all."""
    assert not upgrades.has_upgrade("tengu_flurry")
    assert not upgrades.has_upgrade("chinju_ward")


# ---------------------------------------------------------------------------
# 2. `transform_starter_into`: the key the conversion needed.
# ---------------------------------------------------------------------------

def test_the_victim_is_a_starter_and_never_a_drafted_card():
    """`c.IsTransformable && c.Rarity == CardRarity.Basic`, both branches.

    The printed deck is all basics, so the drafted cards are added here: two
    uncommons and a rare, none of which may be eaten however badly the drafter
    rates them against the plan."""
    drafted = ["sugar_rush", "controlled_demolition", "fish_blasting"]
    st = _st(deck_ids=list(loader.starting_deck("klee")) + drafted)
    assert all(loader.peek_card(c).rarity != events.STARTER_RARITY
               for c in drafted)                 # or the test is vacuous
    events.resolve(random.Random(0), _event(), _opt("Bird"), st)
    for cid in drafted:
        assert cid in st.deck_ids


def test_the_victim_is_the_drafters_worst_starter_not_the_first():
    """Selection reuses the draft valuation, the mirror image of the enchant
    branch's best-legal-target, so transform policy and removal policy cannot
    disagree about which starter is the bad one."""
    from tier05 import draft
    st = _st()
    cards = [loader.peek_card(cid) for cid in st.deck_ids]
    idxs = events._starter_targets(st)
    want = min(idxs, key=lambda i: (
        draft.score_offer(cards[i], cards, st.archetype), i))
    events.resolve(random.Random(0), _event(), _opt("Bird"), st)
    assert st.deck_ids[want] == "tengu_flurry"


def test_a_starterless_deck_locks_both_transform_branches():
    """The lock, and the one place this conversion is NARROWER than the game:
    `WoodCarvings.IsAllowed` refuses to offer the whole event unless a
    removable Basic exists, where the sim offers the Snake branch alone. The
    event layer models no event-level availability rule for any of the 36
    events that declare one, so this follows the house treatment rather than
    growing a second gate for one event."""
    st = _st(deck_ids=["kaeya_frostgnaw", "sugar_rush"])
    assert all(loader.peek_card(c).rarity != events.STARTER_RARITY
               for c in st.deck_ids)
    assert [o["label"] for o in events.available(_event(), st)] == ["Snake"]


def test_a_deck_with_no_slither_target_locks_only_the_snake_branch():
    """The wiki's own parenthetical: 'Locked if no cards can be enchanted with
    Slither'. A deck of X-cost cards is the shape that trips it -- Slither
    refuses `CostsX` -- and here it is built out of a starter plus Klee's two
    X-cost rows so the transform branches stay live and the lock is visibly
    per-option."""
    st = _st(deck_ids=["kaboom", "controlled_demolition", "fish_blasting"])
    st.deck_ids[0] = enchantments.decorate("kaboom", "sharp", 2)
    labels = [o["label"] for o in events.available(_event(), st)]
    assert labels == ["Bird", "Torus"]


def test_the_transform_counts_as_a_deck_add_for_book_of_five_rings():
    """A card entered the master deck, so the Book's counter ticks -- the same
    call `transform:` makes, through the same one door (EB-111)."""
    st = _st()
    assert events._adds_of(_opt("Bird"), st) == 1
    events.resolve(random.Random(0), _event(), _opt("Bird"), st)
    assert st.cards_added == 1
    # ...and it forecasts zero once there is nothing left to transform.
    dry = _st(deck_ids=["kaeya_frostgnaw"])
    assert events._adds_of(_opt("Bird"), dry) == 0


def test_the_two_named_branches_are_separated_by_card_fit_not_by_order():
    """Both branches score a flat CARD_HP, exactly as Bugslayer's two
    colorless cards do, so the drafter's opinion of the card is what decides
    -- and it has to actually decide, or the choice is declaration order
    forever."""
    st = _st()
    bird, torus = _opt("Bird"), _opt("Torus")
    assert events.option_value(bird, st) == events.option_value(torus, st)
    assert events._fit(bird, st) != events._fit(torus, st)


def test_the_option_key_is_declared_in_the_grammar_allowlist():
    """The audit's rule for this file: a key the reader honours but the
    allowlist does not know is a silent no-op waiting to happen, and one the
    allowlist knows but nothing reads is the defect the allowlist exists to
    catch."""
    assert "transform_starter_into" in events.OPTION_KEYS


# ---------------------------------------------------------------------------
# 3. What the three options put into a FIGHT.
# ---------------------------------------------------------------------------

def _fight_state(deck_ids, hp=80, seed=11):
    player = loader.build_player_from_ids("klee", deck_ids)
    player.hp = player.max_hp = hp
    enemy = Enemy(name="dummy", hp=999, max_hp=999,
                  intents=[{"op": "attack", "amount": 0}])
    return CombatState(player=player, enemies=[enemy], rng=random.Random(seed))


def test_tengu_flurry_deals_its_three_hits_separately():
    """2 × 3 and not 6 × 1: the hit count is what a block-per-hit or a
    thorns-style effect would read, so the shape matters and not just the
    total."""
    state = _fight_state(["tengu_flurry"])
    card = loader.get_card("tengu_flurry")
    state.player.hand = [card]
    state.player.energy = 3
    before = state.enemies[0].hp
    combat.play_card(state, card)
    assert before - state.enemies[0].hp == 6
    hits = [e for e in state.log if e["event"] == "damage"]
    assert len(hits) == 3


def test_chinju_ward_pays_five_now_and_five_on_each_of_the_next_two_turns():
    """`ToricToughnessPower` holds TURNS in its stack and the Block in a
    sidecar, and pays at the turn-start seam: 5 immediately, then 5 at the
    start of each of the next two turns, then nothing."""
    from tier0.engine import effects
    state = _fight_state(["chinju_ward"])
    card = loader.get_card("chinju_ward")
    state.player.hand = [card]
    state.player.energy = 3
    combat.play_card(state, card)
    assert state.player.block == 5                    # the immediate half
    assert state.player.powers[effects.BLOCK_AT_TURN_START] == 2
    assert state.player.timed_power_amounts[
        effects.BLOCK_AT_TURN_START] == 5

    paid = []
    for _ in range(3):
        state.player.block = 0                        # the turn-start reset
        effects.player_turn_start_triggers(state)
        paid.append(state.player.block)
    assert paid == [5, 5, 0]                          # pay, tick, expire
    assert effects.BLOCK_AT_TURN_START not in state.player.powers


def test_slither_rerolls_the_cost_of_its_own_card_when_it_is_drawn():
    """`AfterCardDrawn`, gated on the card being its own and on it landing in
    HAND, writing `EnergyCost.SetThisCombat(Rng.NextInt(4))` -- so the cost is
    in 0..3, the card's neighbours are untouched, and a card that never left
    the draw pile keeps its printed cost."""
    from tier0.engine import refpowers
    cid = enchantments.decorate("kaboom", "slither")
    seen = set()
    for seed in range(40):
        state = _fight_state([cid, "kaboom"], seed=seed)
        drawn = next(c for c in state.player.draw_pile
                     if c.on_draw_randomise_cost)
        plain = next(c for c in state.player.draw_pile
                     if not c.on_draw_randomise_cost)
        state.player.hand = [drawn]
        refpowers.after_card_drawn(state, drawn, from_hand_draw=True)
        assert drawn.cost_set_this_combat in (0, 1, 2, 3)
        assert plain.cost_set_this_combat is None
        seen.add(drawn.cost_set_this_combat)
    assert seen == {0, 1, 2, 3}, seen     # the whole range is reachable


def test_slither_survives_the_run_because_it_rides_the_deck_id():
    """The claim every enchantment in this repo makes, restated for the
    ninth: nothing stores the rider, it is re-derived from the deck list at
    each fight, so the enchantment cannot be lost by a deck mutation."""
    st = _st()
    events.resolve(random.Random(4), _event(), _opt("Snake"), st)
    cid = next(c for c in st.deck_ids
               if enchantments.enchantment_of(c) == "slither")
    for _ in range(3):
        state = _fight_state(st.deck_ids)
        armed = [c for c in state.player.draw_pile
                 if c.on_draw_randomise_cost == 4]
        assert len(armed) == 1
    assert enchantments.enchantment_of(cid) == "slither"
