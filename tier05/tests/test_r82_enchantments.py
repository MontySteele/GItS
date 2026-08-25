"""The reopened enchantment scope: vocabulary, events, persistence (R82).

[USER] reopened R82 on 2026-08-10 (M7). Clause (2) had closed the scope at
the per-instance rider that Blade Of Ink needs -- flat damage plus an on-play
effect list, attached to a token as it is CREATED. Seven events in the
conversion gallery were blocked on the other half: an enchantment attached to
a card that is already in the run's DECK, which has to survive every later
deck operation and every remaining fight.

Three claims, and the file is laid out as three sections in that order:

  1. each named enchantment produces the rider its published text states,
     and nothing else touches a card that has no enchantment;
  2. each converted event selects a LEGAL target by its own stated rule,
     locks itself when there is none, and attaches exactly one enchantment;
  3. the attachment is a decoration on the deck-list ID, so it persists --
     across upgrades, across deck mutations, and across fights in a run.

Six of the seven have now converted -- Grave of the Forgotten joined them
once EB-82's `damage_per_exhaust` hook existed to carry Forgotten Soul. The
one that still has not is pinned in section 4: a skip that is not asserted is
a skip that quietly un-skips itself.
"""

from __future__ import annotations

import random

import pytest

from tier0 import constants as C
from tier0.content import enchantments, loader, upgrades
from tier0.engine import combat
from tier0.engine.state import CombatState, Enemy
from tier05 import events


CONVERTED = ("sapphire_seed", "field_of_man_sized_holes", "stone_of_all_time",
             "symbiote", "self_help_book", "grave_of_the_forgotten")


def _st(**kw):
    base = dict(character="klee", archetype="demolition", hp=50, max_hp=70,
                gold=200, deck_ids=list(loader.starting_deck("klee")))
    base.update(kw)
    return events.EventState(**base)


# ---------------------------------------------------------------------------
# 1. The vocabulary: name -> rider.
# ---------------------------------------------------------------------------

def test_the_catalogue_holds_exactly_the_names_the_events_grant():
    """A name with no granting event is a name with no caller, and an event
    naming an enchantment the catalogue lacks would fail at load."""
    granted = set()
    for section in events._pool().values():
        for event in section:
            for opt in events.options_of(event):
                if opt.get("enchant"):
                    granted.add(opt["enchant"]["name"])
    # Soul's Power was the one registered name no shipped event granted; the
    # day its relic landed (EB-82) arrived, so the catalogue is now exactly
    # the set of names the pool hands out, with nothing held in reserve.
    assert granted == set(enchantments.CATALOG)


@pytest.mark.parametrize("name,amount,field,expected", [
    ("sharp", 2, "enchant_damage", 2),
    ("nimble", 2, "enchant_block", 2),
    ("vigorous", 8, "enchant_first_play_damage", 8),
    ("perfect_fit", None, "enchant_top_of_draw", True),
    ("corrupted", None, "enchant_damage_mult", 1.5),
])
def test_a_named_enchantment_writes_its_published_rider(name, amount, field,
                                                        expected):
    card = loader.peek_card(enchantments.decorate("kaboom", name, amount))
    assert getattr(card, field) == expected


def test_sown_and_swift_ride_the_first_play_effect_list():
    sown = loader.peek_card(enchantments.decorate("kaboom", "sown"))
    assert sown.enchant_first_play_effects == [{"op": "energy", "amount": 1}]
    swift = loader.peek_card(enchantments.decorate("kaboom", "swift", 2))
    assert swift.enchant_first_play_effects == [{"op": "draw", "amount": 2}]


def test_souls_power_unsets_exhaust_rather_than_adding_a_rider():
    """The one enchantment that needs no engine surface at all: it clears a
    printed card field, which IS the published effect ('loses Exhaust')."""
    base = loader.peek_card("sugar_rush")
    ench = loader.peek_card(enchantments.decorate(base.id, "souls_power"))
    assert base.exhaust and not ench.exhaust


def test_corrupted_carries_its_hp_cost_on_the_shipped_rider():
    card = loader.peek_card(enchantments.decorate("kaboom", "corrupted"))
    assert card.enchant_effects == [{"op": "damage", "target": "self",
                                     "amount": 2}]


def test_an_unenchanted_card_carries_no_rider_at_all():
    """The whole extension is inert unless something asks for it -- the
    reason the frozen battery is byte-identical across this pass."""
    card = loader.peek_card("kaboom")
    assert (card.enchant_damage == 0 and card.enchant_block == 0
            and card.enchant_damage_mult == 1.0
            and card.enchant_first_play_damage == 0
            and card.enchant_first_play_effects == []
            and card.enchant_effects == []
            and not card.enchant_top_of_draw
            and not card.enchant_played_this_combat)


def _skill(fx):
    from tier0.engine.state import Card
    return Card(id="s", name="s", cost=1, type="skill", effects=fx)


def test_nimble_targets_only_a_card_that_actually_gains_block():
    """The published text is 'Block gained from this card', and 83 of the
    repo's 134 skills gain none -- on those, Nimble is silently inert. The
    event picker takes the drafter's best LEGAL card, so a loose predicate
    is not corrected downstream; it has to be right here."""
    inert = _skill([{"op": "draw", "amount": 2}])
    assert not enchantments.eligible(inert, "nimble")
    plain = _skill([{"op": "block", "amount": 5}])
    assert enchantments.eligible(plain, "nimble")


def test_nimble_is_not_skill_only_and_takes_a_block_granting_attack():
    """EB-85 divergence 1. `Nimble.CanEnchant` is `base.CanEnchant(card) &&
    card.GainsBlock` with NO `CanEnchantCardType` override, so card type is
    not part of the rule and a Block-granting Attack is a legal target. Four
    live sheet rows are that shape; naming them keeps the fix from decaying
    back into a type check the moment somebody prints a fifth."""
    from tier0.engine.state import Card
    attack = Card(id="a", name="a", cost=1, type="attack",
                  effects=[{"op": "damage", "amount": 5},
                           {"op": "block", "amount": 5}])
    assert enchantments.eligible(attack, "nimble")
    power = Card(id="p", name="p", cost=1, type="power",
                 effects=[{"op": "block", "amount": 5}])
    assert enchantments.eligible(power, "nimble")
    # ... and a card of ANY type that gains none is still refused.
    dry = Card(id="d", name="d", cost=1, type="attack",
               effects=[{"op": "damage", "amount": 9}])
    assert not enchantments.eligible(dry, "nimble")
    # The named four are the MOD sheets' rows of this shape (three of them
    # are companions, which carry their OWN character id, so the set is taken
    # by excluding the reference ids rather than by naming the three
    # protagonists). Scoping matters: `_card_index()` also
    # holds the extracted reference sheets when `game_ref/` is present, and
    # those carry the base game's OWN Block-granting Attacks (`ic_iron_wave`,
    # `si_dash`). An unscoped equality is therefore green on CI, where
    # `game_ref/` does not exist, and red on any primary checkout -- the
    # environment-dependent assertion this repo has a standing rule against.
    # The reference rows are asserted separately, and as a PRESENCE rather
    # than an equality, because their count is a fact about an extracted
    # artifact rather than about this fix.
    from tier0 import roster
    live = {c.id for c in loader._card_index().values()
            if c.type == "attack"
            and c.character not in roster.REFERENCE_IDS
            and enchantments.eligible(c, "nimble")}
    # FIVE since R208 / W2b (2026-08-25): `depths_judgment` (Sango Isshin) is
    # an Attack whose ratified body gains Block out of an
    # `exhaust_pile_at_least_8` branch (bar 6 -> 8 by R209), so it is exactly the shape this test
    # exists to keep legal. The C# side agrees by construction -- its
    # generated class declares `GainsBlock => true` because BaseLib's
    # auto-detect cannot see a conditional Block row (EB-84).
    assert live == {"warmup_act", "freminet_pressurized_floe",
                    "thoma_crimson_ooyoroi", "itto_superlative_superstrength",
                    "depths_judgment"}
    reference = {c.id for c in loader._card_index().values()
                 if c.type == "attack"
                 and c.character in roster.REFERENCE_IDS
                 and enchantments.eligible(c, "nimble")}
    if reference:                      # only on a checkout holding game_ref/
        assert "ic_iron_wave" in reference


def test_nimble_refuses_a_block_next_turn_only_card():
    """EB-85 divergence 4, the eligibility half. `BlockNextTurnPower` pays
    out with `CreatureCmd.GainBlock(Owner, Amount, Unpowered, null)` -- no
    card source -- so `Hook.ModifyBlock` never sees an enchantment and the
    Block is not "Block gained from this card" at all. The mod agrees from
    the other side: `TidelineWatch` declares neither a BlockVar nor a
    GainsBlock override, so the game refuses it the enchantment outright."""
    later = _skill([{"op": "block_next_turn", "amount": 4}])
    assert not enchantments.eligible(later, "nimble")
    both = _skill([{"op": "block", "amount": 2},
                   {"op": "block_next_turn", "amount": 4}])
    assert enchantments.eligible(both, "nimble")   # the ordinary row carries it
    live = {c.id for c in loader._card_index().values()
            if enchantments.eligible(c, "nimble")}
    assert "tideline_watch" not in live


def test_nimble_sees_block_under_a_conditional():
    """A Block row that only exists inside a conditional branch still counts
    -- BaseLib's auto-detect misses it, which is why three shipped cards
    declare `GainsBlock` by hand."""
    nested = _skill([{"op": "conditional", "if": "has_spark",
                      "then": [{"op": "block", "amount": 3}]}])
    assert enchantments.eligible(nested, "nimble")
    else_only = _skill([{"op": "conditional", "if": "has_spark",
                         "then": [{"op": "draw", "amount": 1}],
                         "else": [{"op": "block", "amount": 3}]}])
    assert enchantments.eligible(else_only, "nimble")


def test_a_card_holds_exactly_one_enchantment_and_never_swaps_it():
    once = enchantments.decorate("kaboom", "sharp", 2)
    with pytest.raises(ValueError):
        enchantments.decorate(once, "vigorous", 8)


def test_the_two_decorations_are_independent_and_compose_either_way():
    """An enchantment must not cost a card its upgrade path, and the
    upgraded-then-enchanted id must resolve to the same card as the
    enchanted-then-upgraded one."""
    up_then_ench = enchantments.decorate("kaboom" + upgrades.SUFFIX,
                                         "sharp", 2)
    ench_then_up = enchantments.decorate("kaboom", "sharp", 2) \
        + upgrades.SUFFIX
    assert up_then_ench == ench_then_up
    assert upgrades.has_upgrade(enchantments.decorate("kaboom", "sharp", 2))
    assert not upgrades.has_upgrade(up_then_ench)
    card = loader.peek_card(up_then_ench)
    assert card.enchant_damage == 2
    assert card.effects == loader.peek_card("kaboom" + upgrades.SUFFIX).effects


# ---------------------------------------------------------------------------
# 2. The events: selection rule, lock, attachment.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("event_id", CONVERTED)
def test_every_converted_event_is_reachable_in_a_run(event_id):
    reachable = {e["id"] for act in range(len(C.RUN_ACTS))
                 for e in events.pool_for(act)}
    assert event_id in reachable


def test_each_self_help_reading_is_gated_on_its_own_enchantment():
    """Each reading is offered while ITS enchantment has a legal target.

    On Klee's printed starter all three are live. The third one is the EB-85
    divergence-2 move: Swift's reading needed a Power before this window, and
    Klee's starter has none, so it was locked here for all of RT10. The
    game's Swift has no card-level restriction at all, so it is live on any
    non-empty enchantable deck."""
    event = events.get_event("self_help_book")
    st = _st()
    labels = [o["label"] for o in events.available(event, st)]
    assert labels == ["Read the Back", "Read a Random Passage",
                      "Read the Entire Book"]
    assert "Move On" not in labels          # a valid card exists, so no null


def test_swift_takes_any_card_type_the_base_rules_allow():
    """EB-85 divergence 2, the widest of the five. `Enchantments.Swift`
    overrides HasExtraCardText / ShowAmount / OnPlay and NOTHING else -- no
    CanEnchant, no CanEnchantCardType -- so base CanEnchant is the entire
    gate. tier0's `_is_power` came from the granting event's flavor."""
    from tier0.engine.state import Card
    for kind in ("attack", "skill", "power"):
        assert enchantments.eligible(
            Card(id="x", name="x", cost=1, type=kind), "swift")
    # The three shared refusals are base CanEnchant's own and still bite.
    assert not enchantments.eligible(
        Card(id="s", name="s", cost=1, type="status"), "swift")
    assert not enchantments.eligible(
        Card(id="c", name="c", cost=1, type="skill", rarity="curse"), "swift")
    assert not enchantments.eligible(
        Card(id="k", name="k", cost=1, type="skill", kit_card=True), "swift")


def test_move_on_appears_only_when_every_reading_is_locked():
    """The wiki's availability rule, inverted: the null branch is the one
    thing on offer when nothing else is."""
    st = _st(deck_ids=["curse_normality", "curse_normality"])
    labels = [o["label"] for o in
              events.available(events.get_event("self_help_book"), st)]
    assert labels == ["Move On"]


def test_an_enchant_option_locks_itself_with_no_legal_target():
    """Symbiote's Approach wants an Attack; a deck with none cannot take it,
    and the event still offers its other branch."""
    st = _st(deck_ids=["duck_and_cover", "duck_and_cover"])
    labels = [o["label"] for o in
              events.available(events.get_event("symbiote"), st)]
    assert labels == ["Kill with Fire"]


def test_a_curse_is_never_an_enchant_target():
    st = _st(deck_ids=["curse_normality"])
    opt = {"enchant": {"name": "sown"}}
    assert events._enchant_targets(opt, st) == []


def test_an_already_enchanted_card_is_not_a_second_target():
    st = _st(deck_ids=[enchantments.decorate("kaboom", "sharp", 2), "kaboom"])
    opt = {"enchant": {"name": "vigorous", "amount": 8}}
    assert events._enchant_targets(opt, st) == [1]


@pytest.mark.parametrize("event_id,label,name", [
    ("sapphire_seed", "Plant and Nourish", "sown"),
    ("field_of_man_sized_holes", "Enter Your Hole", "perfect_fit"),
    ("stone_of_all_time", "Push", "vigorous"),
    ("symbiote", "Approach", "corrupted"),
    ("self_help_book", "Read the Back", "sharp"),
])
def test_resolving_the_enchant_branch_attaches_exactly_one(event_id, label,
                                                           name):
    st = _st()
    before = list(st.deck_ids)
    event = events.get_event(event_id)
    opt = next(o for o in event["options"] if o["label"] == label)
    events.resolve(random.Random(4), event, opt, st)
    moved = [(a, b) for a, b in zip(before, st.deck_ids) if a != b]
    assert len(moved) == 1
    was, now = moved[0]
    assert enchantments.split(now) == (was, name, opt["enchant"].get("amount"))
    assert st.log[-1]["enchanted"] == now


def test_the_target_is_the_drafters_best_legal_card_not_the_first():
    """Selection reuses the draft valuation, the mirror of `_worst_cards`, so
    enchant policy and draft policy cannot disagree."""
    from tier05 import draft
    st = _st()
    opt = {"enchant": {"name": "sown"}}
    idxs = events._enchant_targets(opt, st)
    cards = [loader.peek_card(cid) for cid in st.deck_ids]
    want = max(idxs, key=lambda i: (draft.score_offer(cards[i], cards,
                                                      st.archetype), -i))
    events.resolve(random.Random(0), {"id": "x", "options": [opt]}, opt, st)
    assert enchantments.enchantment_of(st.deck_ids[want]) == "sown"


def test_the_field_of_holes_resist_branch_grants_the_real_normality():
    """Not a softened clog: the 3-card turn cap is expressed exactly."""
    st = _st()
    event = events.get_event("field_of_man_sized_holes")
    opt = next(o for o in event["options"] if o["label"] == "Resist")
    events.resolve(random.Random(0), event, opt, st)
    assert "curse_normality" in st.deck_ids
    assert loader.peek_card("curse_normality").status_play_cap == 3


# --- Grave of the Forgotten (EB-82): the branch that waited on a relic -----

def test_the_grave_confront_branch_locks_without_an_exhaust_card():
    """The wiki's lock, and it is NOT a special case: Klee's printed starter
    Exhausts nothing, so Soul's Power has no legal target and `available`
    drops the branch on the enchantment's own eligibility rule."""
    st = _st()
    labels = [o["label"] for o in
              events.available(events.get_event("grave_of_the_forgotten"), st)]
    assert labels == ["Accept the Forgotten Soul"]


def test_the_grave_confront_branch_opens_once_a_card_exhausts():
    st = _st(deck_ids=list(loader.starting_deck("klee")) + ["sugar_rush"])
    labels = [o["label"] for o in
              events.available(events.get_event("grave_of_the_forgotten"), st)]
    assert labels == ["Accept the Forgotten Soul", "Confront with Truth"]


def test_confronting_costs_decay_and_clears_the_cards_exhaust():
    st = _st(deck_ids=list(loader.starting_deck("klee")) + ["sugar_rush"])
    event = events.get_event("grave_of_the_forgotten")
    opt = next(o for o in event["options"] if o["label"] == "Confront with Truth")
    events.resolve(random.Random(0), event, opt, st)
    assert "curse_decay" in st.deck_ids
    enchanted = [c for c in st.deck_ids
                 if enchantments.enchantment_of(c) == "souls_power"]
    assert len(enchanted) == 1
    assert enchantments.split(enchanted[0])[0] == "sugar_rush"
    assert not loader.peek_card(enchanted[0]).exhaust


def test_accepting_grants_forgotten_soul_and_arms_the_exhaust_hook():
    """The whole reason this event waited: the relic ships only onto a hook
    the engine already honors, and holding it must put that hook in front of
    every later fight."""
    from tier05 import relics as relic_pool
    held = relic_pool.HeldRelics.empty("klee")
    st = _st()
    event = events.get_event("grave_of_the_forgotten")
    opt = next(o for o in event["options"]
               if o["label"] == "Accept the Forgotten Soul")
    events.resolve(random.Random(0), event, opt, st, held=held)
    assert st.relics_granted == ["forgotten_soul"]
    assert {"hook": "damage_per_exhaust", "amount": 1} in held.combat_effects


def test_forgotten_soul_is_an_event_relic_and_never_a_reward_roll():
    """§11.2: an event relic has exactly one source, so it must not be
    reachable through the ordinary reward pool."""
    from tier05 import relics as relic_pool
    assert "forgotten_soul" in relic_pool.event_pool()
    held = relic_pool.HeldRelics.empty("klee")
    rolled = {relic_pool.roll_relic_reward(random.Random(s), held, "klee")
              for s in range(200)}
    assert "forgotten_soul" not in rolled


# ---------------------------------------------------------------------------
# 3. Persistence, and what the rider actually does in a fight.
# ---------------------------------------------------------------------------

def _fight_state(deck_ids, hp=80):
    player = loader.build_player_from_ids("klee", deck_ids)
    player.hp = player.max_hp = hp
    enemy = Enemy(name="dummy", hp=999, max_hp=999,
                  intents=[{"op": "attack", "amount": 0}])
    state = CombatState(player=player, enemies=[enemy],
                        rng=random.Random(11))
    return state


def test_an_enchanted_deck_card_arrives_in_combat_enchanted():
    cid = enchantments.decorate("kaboom", "sharp", 2)
    state = _fight_state([cid, "kaboom"])
    enchanted = [c for c in state.player.draw_pile if c.enchant_damage]
    plain = [c for c in state.player.draw_pile if not c.enchant_damage]
    assert len(enchanted) == 1 and len(plain) == 1
    # The rider rides BESIDE the printed number, never inside it.
    assert enchanted[0].effects == plain[0].effects


def test_the_enchantment_survives_every_fight_of_a_run():
    """The claim R82's shipped rider could not make: a token's enchantment
    dies with its combat, and a DECK card's must not. Persistence is
    structural here -- the rider is not stored anywhere, it is re-derived
    from the deck id every fight -- so this asserts the structure."""
    deck = [enchantments.decorate("kaboom", "vigorous", 8), "kaboom"]
    for _ in range(3):                       # three fights off one deck list
        state = _fight_state(deck)
        riders = sorted(c.enchant_first_play_damage
                        for c in state.player.draw_pile)
        assert riders == [0, 8]
        # Spend the rider inside this fight; the DECK LIST is what carries
        # forward, so the next fight must see a fresh 8 rather than a 0.
        for c in state.player.draw_pile:
            c.enchant_played_this_combat = True
    assert enchantments.enchantment_of(deck[0]) == "vigorous"


def test_vigorous_pays_once_and_the_gate_closes():
    card = loader.get_card(enchantments.decorate("kaboom", "vigorous", 8))
    state = _fight_state(["kaboom"])
    state.player.hand = [card]
    before = state.enemies[0].hp
    combat.play_card(state, card)
    first = before - state.enemies[0].hp
    assert card.enchant_played_this_combat
    state.player.hand = [card]
    state.player.energy = 9
    mid = state.enemies[0].hp
    combat.play_card(state, card)
    assert mid - state.enemies[0].hp == first - 8


def test_sown_refunds_energy_on_the_first_play_only():
    card = loader.get_card(enchantments.decorate("kaboom", "sown"))
    state = _fight_state(["kaboom"])
    state.player.hand = [card]
    state.player.energy = 3
    cost = card.cost
    combat.play_card(state, card)
    assert state.player.energy == 3 - cost + 1     # spent, then refunded 1
    after_first = state.player.energy
    state.player.hand = [card]
    combat.play_card(state, card)
    assert state.player.energy == after_first - cost   # no second refund


def test_perfect_fit_takes_the_reshuffle_and_refuses_the_opening_one():
    """EB-85 divergence 5: Perfect Fit is NOT an Innate.

    `PerfectFit.ModifyShuffleOrder` opens `if (!isInitialShuffle && ...)`, so
    the combat-start shuffle is explicitly refused however the printed text
    reads. tier0 hoisted the card at both sites, which made the enchantment
    strictly stronger than the game's -- a free Innate on any card.

    The opening shuffle is asserted statistically rather than on one seed: a
    single hoisted card lands at index 0 every time, and a card that is
    merely shuffled does not."""
    top = 0
    for seed in range(40):
        state = _fight_state([enchantments.decorate("pop", "perfect_fit")]
                             + ["kaboom"] * 8)
        state.rng = random.Random(seed)
        state.rng.shuffle(state.player.draw_pile)
        combat.surface_innate(state.player.draw_pile)
        top += state.player.draw_pile[0].enchant_top_of_draw
    assert 0 < top < 40, top          # shuffled, not hoisted

    # The mid-combat reshuffle IS the site it rides, every time.
    for seed in range(10):
        state = _fight_state([enchantments.decorate("pop", "perfect_fit")]
                             + ["kaboom"] * 8)
        state.rng = random.Random(seed)
        state.player.discard_pile = state.player.draw_pile
        state.player.draw_pile = []
        state.shuffle_discard_into_draw()
        assert state.player.draw_pile[0].enchant_top_of_draw


def test_perfect_fit_does_not_borrow_innates_opening_hoist():
    """The two flags shared one site; only `innate` keeps it."""
    state = _fight_state(["kaboom"] * 8)
    fitted = loader.get_card(enchantments.decorate("pop", "perfect_fit"))
    innate = loader.get_card("kaboom")
    innate.innate = True
    state.player.draw_pile = [fitted, innate] + state.player.draw_pile
    state.rng.shuffle(state.player.draw_pile)
    combat.surface_innate(state.player.draw_pile)
    assert state.player.draw_pile[0] is innate


def test_normality_caps_the_turn_at_three_plays():
    state = _fight_state(["kaboom"] * 5 + ["curse_normality"])
    state.hand_play_cap = True
    state.player.hand = [loader.get_card("kaboom"),
                         loader.get_card("curse_normality")]
    state.player.energy = 99
    playable = state.player.hand[0]
    assert combat.card_playable(state, playable)
    state.cards_played_this_turn = 3
    assert not combat.card_playable(state, playable)


# ---------------------------------------------------------------------------
# 4. The one that still has not converted, and why.
# ---------------------------------------------------------------------------

def test_the_last_unconverted_enchant_event_is_still_out_of_every_pool():
    reachable = {e["id"] for act in range(len(C.RUN_ACTS))
                 for e in events.pool_for(act)}
    assert "wood_carvings" not in reachable            # needs Slither + 2 cards


def test_slither_is_named_as_unexpressed_rather_than_approximated():
    assert "slither" in enchantments.UNEXPRESSED
    assert "slither" not in enchantments.CATALOG
