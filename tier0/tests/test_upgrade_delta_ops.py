"""Data-free coverage for generic upgrade delta operations.

The real-Ironclad artifact is intentionally gitignored, so these tests keep
the shared applier covered on a bare clone while test_ironclad_upgrades.py
checks the generated external data when it is available locally.
"""
import ast
import inspect

from tier0.content import upgrades
from tier0.engine import effects
from tier0.engine.state import Card


def _dispatched_ops() -> set[str]:
    """Every op name `apply_upgrade`'s dispatch matches on, read off its AST.

    Each branch selects its target effect by comparing `fx.get("op")` against
    a literal, so the op names are string constants in the source and nothing
    binds them to the engine's registry. Parsing them back out is the only
    way to ask which ops the applier believes in.
    """
    tree = ast.parse(inspect.getsource(upgrades))
    fn = next(node for node in ast.walk(tree)
              if isinstance(node, ast.FunctionDef)
              and node.name == "apply_upgrade")
    ops: set[str] = set()
    for node in ast.walk(fn):
        if not isinstance(node, ast.Compare):
            continue
        left = node.left
        if not (isinstance(left, ast.Call)
                and isinstance(left.func, ast.Attribute)
                and left.func.attr == "get"
                and len(left.args) == 1
                and isinstance(left.args[0], ast.Constant)
                and left.args[0].value == "op"):
            continue
        for cmp in node.comparators:
            if isinstance(cmp, ast.Constant):
                ops.add(cmp.value)
            elif isinstance(cmp, (ast.Tuple, ast.List, ast.Set)):
                ops.update(el.value for el in cmp.elts
                           if isinstance(el, ast.Constant))
    return ops


def _iter_ops(node) -> set[str]:
    """Op names anywhere in an effect tree, branches included."""
    if isinstance(node, list):
        return set().union(*(_iter_ops(n) for n in node)) if node else set()
    if not isinstance(node, dict):
        return set()
    ops = {node["op"]} if isinstance(node.get("op"), str) else set()
    for branch in ("then", "else"):
        ops |= _iter_ops(node.get(branch) or [])
    return ops


def test_every_op_the_applier_dispatches_on_exists_in_the_engine():
    """The applier names ops as bare strings; the engine owns the registry.

    Nothing links the two, so renaming an op in `effects.OPS` leaves the
    matching branch here pointing at a name no effect will ever carry. The
    branch does not crash -- it simply matches nothing, `ok` goes False, and
    the failure surfaces as "found no matching effect" the first time some
    sim upgrades that one card. Which sim, and whether the suite drafts that
    card at all, is luck. This asks the question at gate time instead.
    """
    unknown = sorted(_dispatched_ops() - set(effects.OPS))
    assert not unknown, (
        "apply_upgrade dispatches on ops the engine does not define "
        f"{unknown} -- an op was renamed and its upgrade branch went dead "
        "silently; re-point the branch or drop it")


def test_the_op_extractor_still_finds_the_dispatch():
    """A guard that reads source can go quiet without going red.

    If the dispatch is ever rewritten into a shape the AST walk above does
    not recognise -- a lookup table, a helper predicate -- `_dispatched_ops`
    returns fewer names or none, and the coverage test passes vacuously
    while covering nothing. So pin the count's floor and a spread of names
    across the branch shapes it has to handle: `==` against a literal, `in`
    against a tuple, and a comparison nested inside a generator.
    """
    ops = _dispatched_ops()
    assert len(ops) >= 30, sorted(ops)
    assert {"damage", "chain_attack",          # `in` against a tuple
            "gain_encore",                     # `==` inside a generator
            "upgrade_in_hand"} <= ops          # `==` inside a `next()`


def test_every_op_an_add_delta_introduces_exists_in_the_engine():
    """The `add` key appends a raw effect dict straight onto the card.

    It is the one delta that WRITES an op rather than finding one, so a typo
    there ships an effect no resolver handles -- and the applier cannot catch
    it, because `add` is unconditionally ok. The card then upgrades cleanly
    and does nothing when played.
    """
    unknown = {}
    for card_id, delta in upgrades._upgrade_index().items():
        if not isinstance(delta, dict) or "add" not in delta:
            continue
        missing = sorted(_iter_ops(delta["add"]) - set(effects.OPS))
        if missing:
            unknown[card_id] = missing
    assert not unknown, (
        f"upgrade `add` deltas introduce ops the engine cannot resolve: "
        f"{unknown}")


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
