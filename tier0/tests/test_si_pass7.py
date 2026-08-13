"""Pins for coverage pass 7 -- the enchant rider (R82).

Same contract as test_si_pass4/5/6: every test drives the mechanic the way a
card row would, asserts on the runtime quantity, and contains NO number
extracted from the game. These run on CI, where game_ref/ does not exist.

The theme continues pass 6's: state that lives on the CARD OBJECT. An
enchantment is two riders on the INSTANCE -- flat damage on its own hits,
and effects appended after its own resolution -- attached in the same
add_card resolution that creates the token. The run-wide enchantment
subsystem (grant screens, enchanting relics) is outside the parity world;
the rider is the whole mechanic, and R82 ratified it as open design space
for house characters too.
"""

from tier0.content import loader
from tier0.engine import combat, powers
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state

WEAK_RIDER = {"op": "apply_power", "power": "weak", "amount": 1,
              "target": "enemy", "target_all_if_power": "fan_of_knives"}


def card(cid="c", type="skill", cost=0, fx=None, **kw):
    return Card(id=cid, name=cid, cost=cost, type=type,
                effects=fx if fx is not None else [], **kw)


def play(state, fx, **kw):
    c = card("driver", fx=fx, **kw)
    state.player.hand.append(c)
    combat.play_card(state, c)
    return c


def _create_enchanted(state, n=2, enchant=None):
    play(state, [{"op": "add_card", "card": "strike", "amount": n,
                  "zone": "hand",
                  "enchant": enchant if enchant is not None
                  else {"damage": 2, "effects": [dict(WEAK_RIDER)]}}])
    return [c for c in state.player.hand if c.id == "strike"]


def test_the_enchant_block_rides_the_created_instances_only():
    """The rider attaches in the creating resolution, per instance -- and
    never leaks back into the loader's template for everyone else's
    Strikes."""
    state = make_state()
    tokens = _create_enchanted(state)
    assert len(tokens) == 2
    assert all(t.enchant_damage == 2 for t in tokens)
    assert all(t.enchant_effects == [WEAK_RIDER] for t in tokens)
    fresh = loader.get_card("strike")
    assert fresh.enchant_damage == 0 and fresh.enchant_effects == []


def test_an_enchanted_attack_hits_harder_and_weakens_its_target():
    """Both halves of the rider on one play: the flat damage folds into the
    attack's own hit, and the appended effects land AFTER the card's own
    resolution, on the play's target."""
    enemy = make_enemy(hp=50)
    state = make_state(enemies=[enemy])
    plain = loader.get_card("strike")
    state.player.hand.append(plain)
    combat.play_card(state, plain)
    base_hit = 50 - enemy.hp
    assert enemy.powers.get("weak", 0) == 0

    enchanted = _create_enchanted(state, n=1)[0]
    before = enemy.hp
    combat.play_card(state, enchanted)
    assert before - enemy.hp == base_hit + 2
    assert enemy.powers.get("weak", 0) == 1


def test_the_rider_weak_widens_with_fan_of_knives():
    """Inky reads the card's LIVE TargetType, so when FanOfKnivesPower
    rewrites the token to all-enemies the Weak follows the damage wide --
    the same target_all_if_power contract the Shiv's damage row uses."""
    e1, e2 = make_enemy(hp=30, name="a"), make_enemy(hp=30, name="b")
    state = make_state(enemies=[e1, e2])
    powers.apply_power(state, state.player, "fan_of_knives", 1)
    token = _create_enchanted(state, n=1)[0]
    combat.play_card(state, token)
    assert e1.powers.get("weak", 0) == 1
    assert e2.powers.get("weak", 0) == 1


SPARK_COND = {"op": "conditional", "if": "has_spark",
              "then": [{"op": "block", "amount": 3}]}


def _play_block_card(state, fx, rider=2):
    c = card("nimble_card", fx=fx, enchant_block=rider)
    state.player.hand.append(c)
    combat.play_card(state, c)
    return c


def test_the_block_rider_lands_on_EVERY_block_gain_not_once_per_play():
    """EB-85 divergence 3: the cadence is per Block GAIN.

    The game pays Nimble inside `Hook.ModifyBlock`, which runs once per
    `CreatureCmd.GainBlock` call, with no latch and no EnchantmentStatus gate
    -- so a two-row Block card collects it twice. tier0 paid it once per card
    play off a state latch and under-counted every multi-gain card.
    Asserted with the conditional both dead and live, because the second row
    only exists in one of those worlds."""
    fx = [{"op": "block", "amount": 6}, SPARK_COND]
    dead = make_state()
    _play_block_card(dead, fx)
    assert dead.player.block == 6 + 2          # one gain, one rider

    live = make_state()
    live.player.sparks = 1
    _play_block_card(live, fx)
    assert live.player.block == (6 + 2) + (3 + 2)   # two gains, two riders


def test_the_block_rider_repeats_across_a_times_loop():
    """A `times` loop is N separate GainBlock calls in the game, so it is N
    riders -- the same fact the two-row card asserts, on the other shape."""
    state = make_state()
    _play_block_card(state, [{"op": "block", "amount": 4, "times": 3}])
    assert state.player.block == (4 + 2) * 3


def test_the_rider_never_rides_block_next_turn():
    """EB-85 divergence 4. `BlockNextTurnPower.AfterBlockCleared` gains its
    Block with a null card source, so `Hook.ModifyBlock` finds no
    `cardSource.Enchantment` and Nimble is not paid on it -- not even on a
    card that also gains ordinary Block, where the rider is paid once, for
    the ordinary gain only."""
    state = make_state()
    _play_block_card(state, [{"op": "block", "amount": 4},
                             {"op": "block_next_turn", "amount": 4}])
    assert state.player.block == 4 + 2
    assert state.player.powers.get("block_next_turn", 0) == 4

    # And a card whose ONLY Block arrives that way carries an inert rider,
    # exactly as it does in game. (It is not an eligible target either --
    # enchantments._grants_block -- but the engine must not pay one that is
    # attached some other way.)
    alone = make_state()
    _play_block_card(alone, [{"op": "block_next_turn", "amount": 5}])
    assert alone.player.block == 0
    assert alone.player.powers.get("block_next_turn", 0) == 5


def test_each_card_pays_its_OWN_rider_through_an_inner_free_play():
    """The _FREE_PLAY_CONTEXT question, restated for the per-gain cadence.

    The game reads `cardSource.Enchantment` off whichever card is producing
    the Block, so an inner free-played card pays its own Nimble and the outer
    card keeps paying its own on every gain of its own. There is no shared
    entitlement to spend, which is why the latch left _FREE_PLAY_CONTEXT."""
    state = make_state()
    inner = card("inner", fx=[{"op": "block", "amount": 1}], enchant_block=2)
    state.player.draw_pile.append(inner)
    outer = card("outer", enchant_block=2,
                 fx=[{"op": "block", "amount": 3},
                     {"op": "autoplay_from_draw", "amount": 1},
                     {"op": "block", "amount": 3}])
    state.player.hand.append(outer)
    combat.play_card(state, outer)
    #   outer 3+2, inner 1+2, outer 3+2 -- three gains, three riders
    assert state.player.block == (3 + 2) + (1 + 2) + (3 + 2)


def test_a_clone_of_an_enchanted_card_keeps_its_enchantment():
    """The Nightmare/Anger question from the design pass: what is copied is
    the INSTANCE, so a clone of an enchanted card is itself enchanted --
    plain dataclass fields, carried by the same deepcopy that carries the
    upgrade state."""
    state = make_state()
    original = card("clone_me", type="attack",
                    fx=[{"op": "add_card", "card": "self", "to": "discard"}])
    original.enchant_damage = 1
    original.enchant_effects = [dict(WEAK_RIDER)]
    state.player.hand.append(original)
    combat.play_card(state, original)
    # The played original follows its clone into discard, so select by
    # identity rather than position.
    clones = [c for c in state.player.discard_pile if c is not original]
    assert len(clones) == 1
    assert clones[0].enchant_damage == 1
    assert clones[0].enchant_effects == [WEAK_RIDER]
