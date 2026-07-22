"""Data-free coverage for generic upgrade delta operations.

The real-Ironclad artifact is intentionally gitignored, so these tests keep
the shared applier covered on a bare clone while test_ironclad_upgrades.py
checks the generated external data when it is available locally.
"""

from tier0.content import upgrades
from tier0.engine.state import Card


def test_external_numeric_and_selection_deltas_apply(monkeypatch):
    delta = {
        "energy": 1,
        "times": 1,
        "max_hp": 1,
        "upgrade_scope": "all",
        "exhaust_select": "chosen",
    }
    monkeypatch.setattr(upgrades, "_upgrade_index",
                        lambda: {"synthetic": delta})
    card = Card(
        id="synthetic",
        name="Synthetic",
        cost=1,
        type="skill",
        effects=[
            {"op": "conditional", "then": [
                {"op": "energy", "amount": 1},
                {"op": "gain_max_hp", "amount": 2},
            ]},
            {"op": "damage", "amount": 4, "times": 2},
            {"op": "upgrade_in_hand", "scope": "chosen"},
            {"op": "exhaust_from", "amount": 1},
        ],
    )

    upgraded = upgrades.apply_upgrade(card)

    assert upgraded.id == "synthetic+"
    assert upgraded.effects[0]["then"] == [
        {"op": "energy", "amount": 2},
        {"op": "gain_max_hp", "amount": 3},
    ]
    assert upgraded.effects[1]["times"] == 3
    assert upgraded.effects[2]["scope"] == "all"
    assert upgraded.effects[3]["select"] == "chosen"


def test_runtime_formula_and_conditional_deltas_apply(monkeypatch):
    delta = {
        "formula_per": 1,
        "target_power_per": 1,
        "conditional_damage": 2,
    }
    monkeypatch.setattr(upgrades, "_upgrade_index",
                        lambda: {"synthetic": delta})
    card = Card(
        id="synthetic",
        name="Synthetic",
        cost=1,
        type="attack",
        effects=[
            {"op": "damage", "target": "enemy", "amount_formula": {
                "base": 4, "per": 2, "count": "exhaust_pile",
            }},
            {"op": "damage", "amount": 3, "target": "enemy",
             "bonus_per_target_power": {"power": "vulnerable", "per": 1}},
            {"op": "conditional", "if": "target_has_power_vulnerable",
             "then": [{"op": "damage", "amount": 5, "target": "enemy"}],
             "else": [{"op": "damage", "amount": 5, "target": "enemy"}]},
        ],
    )

    upgraded = upgrades.apply_upgrade(card)

    assert upgraded.effects[0]["amount_formula"]["per"] == 3
    assert upgraded.effects[1]["bonus_per_target_power"]["per"] == 2
    conditional = upgraded.effects[2]
    assert conditional["then"][0]["amount"] == 7
    assert conditional["else"][0]["amount"] == 7


def test_bounded_history_card_deltas_apply(monkeypatch):
    delta = {
        "conditional_block": 3,
        "damage_growth": 4,
        "on_exhaust_energy": 1,
    }
    monkeypatch.setattr(upgrades, "_upgrade_index",
                        lambda: {"synthetic": delta})
    card = Card(
        id="synthetic",
        name="Synthetic",
        cost=1,
        type="skill",
        on_exhaust_energy=2,
        effects=[
            {"op": "conditional", "if": "card_exhausted_this_turn",
             "then": [{"op": "block", "amount": 5},
                      {"op": "block", "amount": 5}],
             "else": [{"op": "block", "amount": 5}]},
            {"op": "grow_damage", "amount": 5},
        ],
    )

    upgraded = upgrades.apply_upgrade(card)

    conditional = upgraded.effects[0]
    assert [fx["amount"] for fx in conditional["then"]] == [8, 8]
    assert conditional["else"][0]["amount"] == 8
    assert upgraded.effects[1]["amount"] == 9
    assert upgraded.on_exhaust_energy == 3
