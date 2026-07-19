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
