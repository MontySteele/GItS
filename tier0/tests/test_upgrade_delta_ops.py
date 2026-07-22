"""Data-free coverage for generic upgrade delta operations.

The real-Ironclad artifact is intentionally gitignored, so these tests keep
the shared applier covered on a bare clone while test_ironclad_upgrades.py
checks the generated 57-card data when it is available locally.
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
