"""Combat-side potion effects (engine/potions.py).

Two jobs, mirroring test_relics_dynamic's discipline:

1. Each drinkable potion, held singly on a fight player, ACTUALLY fires its
   effect -- driven through ``potions._drink`` (the held -> consumed -> applied
   use mechanic), so every assertion also proves the potion left the held list.
   fire_potion is checked on the UNPOWERED path: with the player carrying
   Strength and the enemy Vulnerable it still deals exactly its flat amount,
   proving it bypasses the powered attack pipeline.

2. The use path is a DEAD BRANCH when ``player.potions`` is empty. The empty
   test is load-bearing: it sets up a lethal telegraph that WOULD trip the
   defensive drink (proven by the companion test where the same setup with a
   held block_potion does drink), then asserts an empty-handed player emerges
   untouched -- no block, no HP change, no potion_used event.
"""

from tier0 import constants as C
from tier0.engine import potions
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state


def _dummy(i):
    """A drawable filler card for stocking the draw pile."""
    return Card(id=f"c{i}", name="c", cost=1, type="skill", effects=[])


def _used_events(state):
    return [e for e in state.log if e["event"] == "potion_used"]


# --- block_potion: +12 Block ------------------------------------------------

def test_block_potion_gains_twelve_block():
    st = make_state()
    st.player.potions = ["block_potion"]
    potions._drink(st, "block_potion")
    assert st.player.block == C.POTION_BLOCK == 12
    assert st.player.potions == []                       # consumed


# --- fire_potion: 20 flat to one enemy, ignoring Strength/Vulnerable --------

def test_fire_potion_deals_flat_damage_ignoring_strength_and_vulnerable():
    st = make_state(enemies=[make_enemy(hp=50)])
    # Load the powered pipeline in fire_potion's favour: were it routed through
    # the attack path, +5 Strength and x1.5 Vulnerable would push 20 to 37.
    st.player.powers["strength"] = 5
    st.enemies[0].powers["vulnerable"] = 5
    st.player.potions = ["fire_potion"]
    potions._drink(st, "fire_potion")
    assert st.enemies[0].hp == 50 - C.POTION_FIRE_DAMAGE == 30   # flat 20 only
    assert st.player.potions == []


def test_fire_potion_defaults_to_lowest_hp_enemy_when_untargeted():
    st = make_state(enemies=[make_enemy(hp=40, name="big"),
                             make_enemy(hp=10, name="small")])
    st.player.potions = ["fire_potion"]
    potions._drink(st, "fire_potion")                    # no explicit target
    assert st.enemies[0].hp == 40                         # untouched
    assert st.enemies[1].hp == 10 - C.POTION_FIRE_DAMAGE  # lowest-HP hit


# --- blood_potion: heal 20% of max HP, capped at max ------------------------

def test_blood_potion_heals_twenty_percent_max_hp():
    st = make_state(hp=80)
    st.player.hp = 50
    st.player.potions = ["blood_potion"]
    potions._drink(st, "blood_potion")
    assert st.player.hp == 50 + int(C.POTION_BLOOD_HEAL_FRACTION * 80) == 66
    assert st.player.potions == []


def test_blood_potion_heal_is_capped_at_max_hp():
    st = make_state(hp=80)
    st.player.hp = 75                                    # only 5 room to heal
    st.player.potions = ["blood_potion"]
    potions._drink(st, "blood_potion")
    assert st.player.hp == 80                            # capped, not 91


# --- strength_potion: +2 Strength (combat-scoped power) ---------------------

def test_strength_potion_adds_two_strength():
    st = make_state()
    assert st.player.powers.get("strength", 0) == 0
    st.player.potions = ["strength_potion"]
    potions._drink(st, "strength_potion")
    assert st.player.powers["strength"] == C.POTION_STRENGTH == 2
    assert st.player.potions == []


# --- swift_potion: draw 3 ---------------------------------------------------

def test_swift_potion_draws_three():
    st = make_state()
    st.player.draw_pile = [_dummy(i) for i in range(5)]
    st.player.hand = []
    st.player.potions = ["swift_potion"]
    potions._drink(st, "swift_potion")
    assert len(st.player.hand) == C.POTION_SWIFT_DRAW == 3
    assert len(st.player.draw_pile) == 2
    assert st.player.potions == []


# --- weak_potion: 3 Weak on an enemy ----------------------------------------

def test_weak_potion_applies_three_weak_to_enemy():
    st = make_state(enemies=[make_enemy(hp=50)])
    st.player.potions = ["weak_potion"]
    potions._drink(st, "weak_potion")
    assert st.enemies[0].powers["weak"] == C.POTION_WEAK == 3
    assert st.player.potions == []


# --- fear_potion: 3 Vulnerable on an enemy ----------------------------------

def test_fear_potion_applies_three_vulnerable_to_enemy():
    st = make_state(enemies=[make_enemy(hp=50)])
    st.player.potions = ["fear_potion"]
    potions._drink(st, "fear_potion")
    assert st.enemies[0].powers["vulnerable"] == C.POTION_FEAR_VULN == 3
    assert st.player.potions == []


# --- energy_potion: +2 Energy -----------------------------------------------

def test_energy_potion_grants_two_energy():
    st = make_state()
    st.player.energy = 0
    st.player.potions = ["energy_potion"]
    potions._drink(st, "energy_potion")
    assert st.player.energy == C.POTION_ENERGY == 2
    assert st.player.potions == []


# ==========================================================================
# EMPTY-POTIONS LOCK: the use path is dead when nothing is held.
# ==========================================================================

def _lethal_telegraph_state():
    """A fight where the enemy telegraphs a hit that WOULD drop the player past
    the defensive safety margin -- the exact condition try_use_potions drinks a
    defensive potion on. HP low, no block, enemy swinging for far more."""
    st = make_state(hp=10, enemies=[make_enemy(
        hp=50, intents=[{"kind": "attack", "amount": 50}])])
    st.player.block = 0
    return st


def test_block_potion_drunk_via_use_path_under_lethal_telegraph():
    # Load-bearing counterpart: proves the empty test's setup genuinely trips
    # the defensive drink, so its no-op below is the guard, not a dead setup.
    st = _lethal_telegraph_state()
    st.player.potions = ["block_potion"]
    potions.try_use_potions(st)
    assert st.player.block == C.POTION_BLOCK             # defensive drink fired
    assert st.player.potions == []                       # consumed
    assert len(_used_events(st)) == 1


def test_use_path_is_a_dead_branch_when_no_potions_held():
    st = _lethal_telegraph_state()
    st.player.potions = []                               # nothing to drink
    potions.try_use_potions(st)
    assert st.player.block == 0                          # no block gained
    assert st.player.hp == 10                            # no heal, no change
    assert st.player.potions == []
    assert _used_events(st) == []                        # nothing drunk


def test_apply_potion_unknown_id_logs_unimplemented_and_no_effect():
    st = make_state(enemies=[make_enemy(hp=50)])
    before_hp = st.player.hp
    potions.apply_potion(st, "made_up_potion")
    assert st.player.hp == before_hp
    assert st.enemies[0].hp == 50
    assert any(e["event"] == "UNIMPLEMENTED" for e in st.log)
    assert _used_events(st) == []
