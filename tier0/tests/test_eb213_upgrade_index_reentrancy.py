"""`EB-213`'s upgrade channel built a cycle only `game_ref/` can reach.

THE DEFECT, in one line: `_card_index` -> `_external_cards` -> `has_upgrade`
-> `_upgrade_index` -> `_prototype_deltas` -> `prototype_cards` ->
`_card_index`, unbounded, because `lru_cache` does not memoize a call that is
still in flight.

WHY NOTHING CAUGHT IT. `loader._external_cards` returns an empty list the
moment `game_ref/` is absent, and that tree is gitignored: CI has none, a
fresh clone has none, and no worktree has one. The full suite, the lints and
`dotnet build` were all green on the branch that introduced it. The art-bearing
main checkout is the only tree in the house that carries the reference layer,
and there the whole content tree stopped loading -- surfacing as a
`RecursionError` raised inside PyYAML, naming neither end of the cycle. It was
found by `validate.ps1` refusing a deploy.

That is the *structurally invisible defect* shape: a check that needs data the
repo cannot see. The answer this file is: the reference layer is FAKED, so a
tree without one runs the same lock.
"""

from __future__ import annotations

import sys

import pytest

from tier0.content import loader, upgrades


def _fake_reference_layer(monkeypatch, tmp_path):
    """One external sheet, on disk, with one row that has an upgrade.

    Everything `_external_cards` reads is redirected into `tmp_path`: the
    pool sheet itself, the required merged layers (none), and the upgrade
    sheet `has_upgrade` must find the row in. The row's id is a base-game
    shape and never a `proto_` one, which is the whole point -- the cycle was
    reached by asking about an ORDINARY card.
    """
    pool = tmp_path / "ironclad_pool.yaml"
    pool.write_text(
        "- id: eb213_probe\n"
        "  name: EB-213 Probe\n"
        "  cost: 1\n"
        "  type: attack\n"
        "  rarity: common\n"
        "  effects:\n"
        "    - op: damage\n"
        "      amount: 6\n"
        "      target: enemy\n",
        encoding="utf-8")
    ups = tmp_path / "ironclad-upgrades.yaml"
    ups.write_text("eb213_probe:\n  damage: 9\n", encoding="utf-8")

    monkeypatch.setattr(loader, "GAME_REF_DIR", tmp_path)
    monkeypatch.setattr(loader, "EXTERNAL_CARD_SHEETS",
                        {"ironclad_pool.yaml": "real_ironclad"})
    monkeypatch.setattr(loader, "EXTERNAL_CARD_LAYERS", {})
    monkeypatch.setattr(upgrades, "EXTERNAL_UPGRADE_SHEETS", (ups,))
    monkeypatch.setattr(upgrades, "_external_pool_for", lambda sheet: pool)
    loader.reset_caches()


def test_the_card_index_loads_with_a_reference_layer_present(monkeypatch,
                                                             tmp_path):
    """THE LOCK. Bite: route `_external_cards`' `has_upgrade` call back
    through the merged index (drop `shipped_only=True`) and this raises
    `RecursionError` instead of returning, exactly as the main checkout did.

    The recursion limit is lowered so the failure is a second rather than the
    ~20 s a full 1000-deep stack of YAML parses costs, and restored either
    way.
    """
    _fake_reference_layer(monkeypatch, tmp_path)
    before = sys.getrecursionlimit()
    sys.setrecursionlimit(400)
    try:
        index = loader._card_index()
    finally:
        sys.setrecursionlimit(before)
        loader.reset_caches()
    assert "eb213_probe" in index


def test_the_two_halves_answer_the_same_question_as_the_merged_index():
    """`shipped_only` is a CYCLE BREAK and must not be a behaviour change.

    For every id the sheets rule, the shipped-only answer and the merged
    answer agree -- so the one caller that passes the flag gets the same
    verdict it always got.
    """
    for card_id in list(upgrades._shipped_upgrade_index()):
        assert (upgrades.has_upgrade(card_id, shipped_only=True)
                == upgrades.has_upgrade(card_id)), card_id


def test_the_merged_index_is_still_both_halves():
    """The union is what every ITERATING caller reads, and `EB-213`'s rows
    are still in it -- the split moved where a single-id LOOKUP goes, and
    nothing else."""
    merged = upgrades._upgrade_index()
    assert set(upgrades._shipped_upgrade_index()) <= set(merged)
    assert set(upgrades._prototype_upgrade_index()) <= set(merged)
    assert merged == {**upgrades._shipped_upgrade_index(),
                      **upgrades._prototype_upgrade_index()}


def test_reset_caches_clears_all_three(monkeypatch):
    """A stale half is a worse failure than a slow one: the prototype half is
    derived from the substitution table, which a flag flip moves."""
    upgrades._upgrade_index()
    upgrades._shipped_upgrade_index()
    upgrades._prototype_upgrade_index()
    loader.reset_caches()
    for fn in (upgrades._upgrade_index, upgrades._shipped_upgrade_index,
               upgrades._prototype_upgrade_index):
        assert fn.cache_info().currsize == 0, fn.__name__


@pytest.mark.parametrize("fn", ["_shipped_upgrade_index",
                                "_prototype_upgrade_index"])
def test_both_halves_are_memoized(fn):
    assert hasattr(getattr(upgrades, fn), "cache_clear")
