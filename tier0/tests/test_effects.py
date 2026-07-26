from tier0 import constants as C
from tier0.engine import effects
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state


def card(**kw):
    base = dict(id="t", name="t", cost=1, type="attack")
    base.update(kw)
    return Card(**base)


def test_damage_hits_hp(state):
    c = card(effects=[{"op": "damage", "amount": 6, "target": "enemy"}])
    effects.resolve_card(state, c)
    assert state.enemies[0].hp == 44


def test_damage_respects_block(state):
    state.enemies[0].block = 4
    c = card(effects=[{"op": "damage", "amount": 6, "target": "enemy"}])
    effects.resolve_card(state, c)
    assert state.enemies[0].hp == 48
    assert state.enemies[0].block == 0


def test_multi_hit_and_all_enemies():
    st = make_state(enemies=[make_enemy(hp=20, name="a"),
                             make_enemy(hp=20, name="b")])
    c = card(effects=[{"op": "damage", "amount": 3, "target": "all_enemies",
                       "times": 2}])
    effects.resolve_card(st, c)
    assert [e.hp for e in st.enemies] == [14, 14]


def test_block_draw_energy(state):
    state.player.draw_pile = [card(id=f"c{i}") for i in range(3)]
    c = card(type="skill", effects=[{"op": "block", "amount": 5},
                                    {"op": "draw", "amount": 2},
                                    {"op": "energy", "amount": 1}])
    effects.resolve_card(state, c)
    assert state.player.block == 5
    assert len(state.player.hand) == 2
    assert state.player.energy == 1


def test_strength_and_vulnerable_pipeline(state):
    state.player.powers["strength"] = 2
    state.enemies[0].powers["vulnerable"] = 1
    c = card(effects=[{"op": "damage", "amount": 6, "target": "enemy"}])
    effects.resolve_card(state, c)
    # (6+2) * 1.5 = 12
    assert state.enemies[0].hp == 38


def test_weak_reduces_damage(state):
    state.player.powers["weak"] = 1
    c = card(effects=[{"op": "damage", "amount": 8, "target": "enemy"}])
    effects.resolve_card(state, c)
    # 8 * 0.75 = 6
    assert state.enemies[0].hp == 44


def test_bomb_places_and_detonates_on_attack_hit(state):
    state.player.relic_hooks.append("spark_on_detonation")
    bomb_card = card(type="skill", effects=[
        {"op": "place_bomb", "amount": 1, "target": "enemy", "bomb_damage": 6}])
    effects.resolve_card(state, bomb_card)
    assert len(state.enemies[0].bombs) == 1

    hit = card(effects=[{"op": "damage", "amount": 5, "target": "enemy"}])
    effects.resolve_card(state, hit)
    # 5 (hit) + 6 (bomb, applies pyro -> no aura yet, no reaction) = 11
    assert state.enemies[0].hp == 39
    assert state.enemies[0].bombs == []
    assert state.player.sparks == 1        # relic hook fired
    assert state.enemies[0].aura == "pyro"  # bomb applied its element


def test_sparks_do_not_trigger_without_relic(state):
    bomb_card = card(type="skill", effects=[
        {"op": "place_bomb", "amount": 1, "target": "enemy", "bomb_damage": 6}])
    effects.resolve_card(state, bomb_card)
    hit = card(effects=[{"op": "damage", "amount": 5, "target": "enemy"}])
    effects.resolve_card(state, hit)
    assert state.player.sparks == 0


def test_heal_caps_at_max_hp(state):
    state.player.hp = 78
    c = card(type="skill", effects=[{"op": "heal", "amount": 10}])
    effects.resolve_card(state, c)
    assert state.player.hp == 80


# --- Nicole, Celestial Gift (redesigned 2026-07-26, red-pen item 4) ---------
#
# This power had ZERO behavioural coverage before the redesign, which is how a
# semantics change -- static flat attack bonus -> per-turn Strength ratchet --
# left the suite count unmoved. The gap is the point of these three.

def test_celestial_gift_ratchets_strength_every_turn():
    """The amount is Strength PER TURN, not a total.

    Two turn-starts must leave 2 Strength from a 1-amount power. A reading
    that set Strength to the amount instead of adding it would pass a
    single-turn test and silently flatten the card's whole identity, which is
    scaling.
    """
    st = make_state()
    st.player.powers["celestial_gift"] = 1
    effects.player_turn_start_triggers(st)
    assert st.player.powers.get("strength", 0) == 1
    effects.player_turn_start_triggers(st)
    assert st.player.powers.get("strength", 0) == 2


def test_celestial_gift_grants_its_block_each_turn():
    st = make_state()
    st.player.powers["celestial_gift"] = 1
    st.player.block = 0
    effects.player_turn_start_triggers(st)
    assert st.player.block == C.CELESTIAL_GIFT_BLOCK


def test_celestial_gift_no_longer_pays_a_flat_attack_bonus():
    """The double-count guard.

    Strength is folded in by the damage pipeline. If celestial_gift ALSO stayed
    in flat_attack_bonus -- where it lived before the redesign -- every attack
    would be paid the buff twice, and nothing else in the suite would notice.
    """
    st = make_state()
    st.player.powers["celestial_gift"] = 3
    card = Card(id="t", name="t", cost=1, type="attack",
                effects=[{"op": "damage", "amount": 5}])
    assert effects.flat_attack_bonus(st, card, 1) == 0
