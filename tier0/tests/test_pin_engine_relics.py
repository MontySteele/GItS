"""Pin tests for the combat-side relic engine (tier0/engine/relics.py).

Two riders whose exact matching rule is the whole behaviour: the
conditional_power HP comparison (Red Skull) is INCLUSIVE of the threshold,
and the card_name_damage_bonus substring is matched against the card's
display NAME as well as its id.
"""

from tier0.engine import effects, relics
from tier0.engine.state import Card

from tier0.tests.conftest import make_enemy, make_state


def test_conditional_power_is_active_at_exactly_the_threshold_hp():
    """conditional_power's hp_below condition holds when current HP is at or
    below threshold * max_hp, threshold included. A player sitting on exactly
    half HP has the power; one HP above the line does not."""
    st = make_state(hp=80)
    p = st.player
    p.relic_effects = [{"hook": "conditional_power", "power": "strength",
                        "amount": 3, "when": "hp_below", "threshold": 0.5}]
    relics.reset_combat(st)

    p.hp = 41                             # one above the line: inactive
    relics.reevaluate_conditionals(st)
    assert p.powers.get("strength", 0) == 0

    p.hp = 40                             # EXACTLY 0.5 * 80: active
    relics.reevaluate_conditionals(st)
    assert p.powers.get("strength", 0) == 3

    p.hp = 41                             # back above the line: removed again
    relics.reevaluate_conditionals(st)
    assert p.powers.get("strength", 0) == 0


def test_card_name_damage_bonus_matches_the_display_name_not_only_the_id():
    """card_name_damage_bonus pays its rider when the substring appears in
    EITHER the card's id or its display name. A card whose id has been renamed
    away from its printed name still collects the bonus off the name alone."""
    st = make_state(enemies=[make_enemy(hp=50)])
    st.player.relic_effects = [{"hook": "card_name_damage_bonus",
                                "substring": "Strike", "amount": 3}]
    card = Card(id="pommel_smack", name="Pommel Strike", cost=1, type="attack",
                effects=[{"op": "damage", "amount": 6, "target": "enemy"}])
    assert "Strike" not in card.id        # the id half cannot be what matches

    assert relics.card_damage_bonus(st.player, card) == 3
    effects.resolve_card(st, card)
    assert st.enemies[0].hp == 50 - 9     # base 6 + 3 name-matched rider
