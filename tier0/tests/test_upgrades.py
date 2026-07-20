"""M7 upgrade applier: the sheet (docs/klee-upgrades.yaml) must apply
mechanically, and where it cannot, it must fail loudly rather than ship a
card wearing an upgrade name without the upgrade.
"""

import pytest
import yaml

from tier0.content import loader, upgrades


# R20 (2026-07-20): klee-cards.yaml keeps its inline fields until the M9
# session lands its revert (their file, their revert — the deltas already
# live in klee-upgrades.yaml). Remove the entry when that happens; an
# EMPTY allowlist is this test's steady state.
INLINE_UPGRADE_ALLOWLIST = {"klee-cards.yaml"}


def test_no_inline_upgrades_on_docs_sheets():
    """R20: *-upgrades.yaml sheets are the ONE upgrade convention. Inline
    `upgrade:` fields on card sheets are deprecated, ignored by Tier 0,
    and — outside the temporary allowlist — forbidden: an inline-only
    upgrade would silently never apply."""
    for sheet in loader.DOCS_CARD_SHEETS:
        if sheet in INLINE_UPGRADE_ALLOWLIST:
            continue
        path = loader.DOCS_DIR / sheet
        if not path.exists():
            continue
        rows = yaml.safe_load(path.read_text())
        inline = [d["id"] for d in rows if "upgrade" in d]
        assert not inline, (
            f"{sheet}: inline `upgrade:` on {inline} — R20 rules these "
            "belong in the *-upgrades.yaml sheet")


def test_every_sheet_entry_applies_or_is_declared_unappliable():
    """The exhaustiveness check IS the drift guard: a new sheet row with a
    key the applier does not know must fail here, not silently no-op."""
    for cid in upgrades._upgrade_index():
        if cid in upgrades.UNAPPLIABLE:
            with pytest.raises(ValueError):
                loader.get_card(cid + "+")
            continue
        up = loader.get_card(cid + "+")
        assert up.id == cid + "+"
        assert up.name.endswith("+")


def test_number_bumps_follow_the_mined_grammar():
    assert loader.get_card("kaboom+").effects[0]["amount"] == 9      # 6->9
    assert loader.get_card("duck_and_cover+").effects[0]["amount"] == 8
    jd = loader.get_card("jumpy_dumpty+")                # dual bump privilege
    assert jd.effects[0]["amount"] == 9                  # 7->9
    assert jd.effects[1]["bomb_damage"] == 8             # 6->8
    assert loader.get_card("big_badda_boom+").effects[0]["amount"] == 16


def test_condition_and_keyword_class_upgrades():
    assert loader.get_card("sugar_rush+").exhaust is False
    hot = loader.get_card("hot_hands+")                  # self-damage removed
    assert not any(fx.get("target") == "self" for fx in hot.effects)
    pd = loader.get_card("patched_dress+")               # hoisted then-branch
    assert not any(fx.get("op") == "conditional" for fx in pd.effects)
    assert sum(fx["amount"] for fx in pd.effects
               if fx.get("op") == "block") == 7          # 5 + 2 unconditional
    both = loader.get_card("eager_to_help+")             # BOTH branches
    cond = next(fx for fx in both.effects if fx.get("op") == "conditional")
    assert cond["then"][0]["amount"] == 3 and cond["else"][0]["amount"] == 2


def test_cost_formula_and_override_upgrades():
    assert loader.get_card("bombs_away+").cost == 2
    assert loader.get_card("endless_fireworks+").cost == 0
    cd = loader.get_card("controlled_demolition+")
    assert cd.effects[0]["amount"] == "X_plus_2"
    gf = loader.get_card("grand_finale+")
    assert gf.effects[0]["bonus_formula"] == "3_per_detonation_this_combat"
    bb = loader.get_card("borrowed_brilliance+")
    assert bb.effects[0]["cost_override"] == 0
    cr = loader.get_card("chained_reactions+")
    assert cr.effects[1]["chance"] == 0.75               # replace, not bump


def test_upgraded_card_keeps_identity_fields():
    """Tags, archetypes, roles drive drafting and metrics -- an upgrade
    must never change what a card IS, only its numbers."""
    for cid in ("mine_toss", "sizzle", "dahlia_sacramental_shower"):
        base, up = loader.get_card(cid), loader.get_card(cid + "+")
        assert up.archetypes == base.archetypes
        assert up.role == base.role and up.role_c == base.role_c
        assert up.rarity == base.rarity
        assert up.is_companion == base.is_companion


def test_x_plus_n_generalization_in_engine():
    from tier0.engine import effects as fx_mod
    from tier0.tests.conftest import make_state
    st = make_state()
    st.current_x = 3
    assert fx_mod._amount(st, "X_plus_2") == 5
    with pytest.raises(ValueError):
        fx_mod._amount(st, "X_times_2")
