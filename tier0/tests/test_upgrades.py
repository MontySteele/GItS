"""M7 upgrade applier: an upgrade delta must apply mechanically, and where it
cannot, it must fail loudly rather than ship a card wearing an upgrade name
without the upgrade. (The shipped `docs/*-upgrades.yaml` sheets and their
per-card pins left at legacy cleanup stage 6; the kits' deltas ride their
prototype rows.)
"""

import pytest

from tier0.content import loader, upgrades


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


def test_upgraded_card_keeps_identity_fields():
    """Tags, archetypes, roles drive drafting and metrics -- an upgrade
    must never change what a card IS, only its numbers."""
    for cid in ("proto_ko_jumpy_dumpty", "proto_kk_kurages_oath",
                "proto_mc_dahlia_sacramental_shower"):
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
