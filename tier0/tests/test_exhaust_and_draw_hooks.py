"""EB-82 / EB-83 — two engine hooks, built as UNUSED MACHINERY. One is armed.

Both exist because the event-relic admission rule forbids inventing an
engine surface inline inside an event conversion, so each was built first and
alone:

  * `damage_per_exhaust` (EB-82, Forgotten Soul -- "whenever you Exhaust a
    card, deal 1 damage to a random enemy") is a relic hook, and it is now
    ARMED: Grave of the Forgotten converted onto it, and `forgotten_soul` is
    the one relic row in `tier05/content/relics.yaml` that carries it.
  * the on-draw cost randomiser (EB-83, the base game's Slither) is a
    per-instance card rider, and no sheet declares it -- `slither` is still
    in `enchantments.UNEXPRESSED` because Wood Carvings is blocked on a
    [USER] call (QUEUE `M23`), so nothing grants it.

The first tests below pin each hook's reachability -- one carrier for the
first, none at all for the second. The rest drive both by hand, which is
still the only way the machinery runs under a unit test.
"""

import random
from pathlib import Path

import yaml

from tier0.content import enchantments, loader
from tier0.engine import combat, refpowers, relics
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state


# --- what reaches each hook -----------------------------------------------

def test_exactly_one_shipped_relic_carries_the_exhaust_damage_hook():
    """The hook was built first and armed second (EB-82). Forgotten Soul is
    its only carrier, and it is an EVENT relic -- so the tier 0.5 world moved
    by one event's worth, not by an addition to any reward pool."""
    from tier05 import relics as relic_pool
    carriers = [rid for rid, spec in relic_pool.event_pool().items()
                if any(fx.get("hook") == "damage_per_exhaust"
                       for fx in spec["effects"])]
    assert carriers == ["forgotten_soul"]
    # ...and no DRAFTABLE row carries it: the reward, Neow and Ancient pools
    # are untouched, which is what keeps the world's move to one event.
    raw = yaml.safe_load(
        (Path(relics.__file__).resolve().parents[2] / "tier05" / "content"
         / "relics.yaml").read_text(encoding="utf-8"))
    for group in ("common", "neow", "ancient"):
        for spec in (raw.get(group) or {}).values():
            assert all(fx.get("hook") != "damage_per_exhaust"
                       for fx in (spec.get("effects") or []))
    # The combat engine already knew the word, so arming it tripped no
    # UNIMPLEMENTED alarm.
    assert "damage_per_exhaust" in relics.COMBAT_HOOKS


def test_no_shipped_card_declares_the_on_draw_randomiser():
    assert all(c.on_draw_randomise_cost is None
               and c.cost_set_this_combat is None
               for c in loader._card_index().values())
    # Slither stays unexpressed for a REASON that is no longer the engine's.
    assert "slither" in enchantments.UNEXPRESSED
    assert "slither" not in enchantments.CATALOG


# --- EB-82: damage_per_exhaust --------------------------------------------

def _exhaust_state(amount=1, enemies=None, seed=0):
    state = make_state(enemies=enemies, seed=seed)
    state.player.relic_effects = [{"hook": "damage_per_exhaust",
                                   "amount": amount}]
    return state


def test_an_exhaust_pays_one_random_enemy_unpowered_damage():
    enemy = make_enemy(hp=20)
    state = _exhaust_state(amount=3, enemies=[enemy])
    refpowers.after_card_exhausted(state, Card(id="c", name="c", cost=0,
                                               type="skill", effects=[]),
                                   caused_by_ethereal=False)
    assert enemy.hp == 17


def test_strength_does_not_scale_it():
    """UNPOWERED, like every other relic hit: the relic is not an attack."""
    enemy = make_enemy(hp=20)
    state = _exhaust_state(amount=3, enemies=[enemy])
    state.player.powers["strength"] = 5
    refpowers.after_card_exhausted(state, Card(id="c", name="c", cost=0,
                                               type="skill", effects=[]),
                                   caused_by_ethereal=False)
    assert enemy.hp == 17


def test_it_hits_exactly_one_of_several_enemies():
    enemies = [make_enemy(hp=20, name=f"e{i}") for i in range(3)]
    state = _exhaust_state(amount=4, enemies=enemies)
    refpowers.after_card_exhausted(state, Card(id="c", name="c", cost=0,
                                               type="skill", effects=[]),
                                   caused_by_ethereal=False)
    assert sorted(e.hp for e in enemies) == [16, 20, 20]


def test_an_empty_board_takes_no_damage_and_consumes_no_randomness():
    """A dead field means no target AND no draw -- so a fight that ends on
    an exhaust cannot shift every later roll."""
    dead = make_enemy(hp=20)
    dead.hp = 0
    state = _exhaust_state(amount=4, enemies=[dead])
    before = state.rng.getstate()
    refpowers.after_card_exhausted(state, Card(id="c", name="c", cost=0,
                                               type="skill", effects=[]),
                                   caused_by_ethereal=False)
    assert state.rng.getstate() == before


def test_a_player_with_no_relics_never_reaches_the_hook():
    """The battery's guarantee: `relic_effects` is empty there, and the
    module opens on it."""
    enemy = make_enemy(hp=20)
    state = make_state(enemies=[enemy])
    assert state.player.relic_effects == []
    refpowers.after_card_exhausted(state, Card(id="c", name="c", cost=0,
                                               type="skill", effects=[]),
                                   caused_by_ethereal=False)
    assert enemy.hp == 20


# --- EB-83: the on-draw cost randomiser -----------------------------------

def _drawable(cost=3, bound=4):
    return Card(id="slithery", name="slithery", cost=cost, type="skill",
                effects=[], on_draw_randomise_cost=bound)


def test_drawing_the_card_rerolls_its_cost_within_the_bound():
    seen = set()
    for seed in range(40):
        state = make_state(seed=seed)     # fresh hand: MAX_HAND_SIZE is real
        card = _drawable()
        state.player.draw_pile = [card]
        state.draw(1)
        assert card.cost_set_this_combat is not None
        seen.add(card.cost_set_this_combat)
    assert seen <= {0, 1, 2, 3}          # NextInt(4) is exclusive
    assert len(seen) > 1                  # and it really is a roll


def test_the_rolled_cost_is_what_the_card_costs_to_play():
    state = make_state()
    card = _drawable(cost=3)
    card.cost_set_this_combat = 1
    state.player.hand.append(card)
    assert combat.card_cost(state, card) == 1


def test_a_relative_discount_still_stacks_on_the_rolled_cost():
    """The game's `_localModifiers` walk: Absolute sets, Relative adds."""
    state = make_state()
    card = _drawable(cost=3)
    card.cost_set_this_combat = 2
    card.cost_delta_this_turn = -1
    state.player.hand.append(card)
    assert combat.card_cost(state, card) == 1


def test_an_ordinary_card_is_untouched_by_the_site():
    state = make_state()
    plain = Card(id="p", name="p", cost=2, type="skill", effects=[])
    state.player.draw_pile = [plain]
    before = state.rng.getstate()
    state.draw(1)
    assert plain.cost_set_this_combat is None
    assert combat.card_cost(state, plain) == 2
    assert state.rng.getstate() == before      # no roll taken


def test_the_roll_expires_at_the_next_combats_start():
    """`SetThisCombat` is combat-scoped; the reset rides the same walk that
    clears the first-play gate, so a run's next fight starts from print."""
    player = loader.build_player("ref_ironclad", "starter")
    # No randomiser on this instance: only the expiry can move the field, so
    # a re-roll cannot be mistaken for a clear.
    stale = Card(id="stale", name="stale", cost=3, type="skill", effects=[])
    stale.cost_set_this_combat = 0
    player.draw_pile.append(stale)
    combat.run_fight(player, [make_enemy(hp=1)], lambda s: None, seed=1)
    assert stale.cost_set_this_combat is None
