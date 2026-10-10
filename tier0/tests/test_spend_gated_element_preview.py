"""Furina v2 seat round (2026-10-04): chooser titles and the Spend-gated
element preview, as the generator decides them.

Tidal Flourish and Quick Flourish applied Hydro only in their Spend mode, so
their reaction preview was emitted with `elementOnlyOnSpend: true`; since the
2026-10-09 playtest trim no Furina row is Spend-gated (Tidal Flourish's plain
mode applies Hydro too). Interval
Bell's Spend price moves on upgrade, so its option title is rendered per side
rather than cut at the template's colon.
"""

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import gen_klee_cards as gen                                   # noqa: E402

SHEET = ROOT / "docs" / "prototype-surface.yaml"


def _rows() -> dict:
    data = yaml.safe_load(SHEET.read_text(encoding="utf-8"))
    rows = data if isinstance(data, list) else next(
        v for v in data.values() if isinstance(v, list))
    return {r["id"]: r for r in rows if isinstance(r, dict) and "id" in r}


def test_spend_only_element_is_detected_on_the_two_flourishes():
    rows = _rows()
    # 2026-10-09 playtest trim (review/records/coop-human-playtest-2026-10-09.md
    # pick 2): Tidal Flourish's plain mode applied Hydro, so it was no longer
    # Spend-gated; the Spend paper (2026-10-10) then took its chooser away
    # ("Spend up to 10"). The detector's positive case is its old modal
    # shape, rebuilt here.
    assert not gen.element_only_in_gated_modes(rows["proto_fs_tidal_flourish"])
    gated = {"id": "probe_gated", "effects": [{"op": "choose_one", "modes": [
        {"label": "Deal 5 Hydro damage to ALL enemies",
         "effects": [{"op": "damage", "amount": 5,
                      "target": "all_enemies"}]},
        {"label": "Spend 6: deal 12 instead",
         "effects": [{"op": "stage_spend", "amount": 6},
                     {"op": "damage", "amount": 12, "target": "all_enemies",
                      "applies_element": True}]}]}]}
    assert gen.element_only_in_gated_modes(gated)
    # The Salon's Tab (2026-10-05): Quick Flourish's Spend is a fixed price
    # now, so its Hydro rides its only (unmoded) hit; Chevalmarin's Hydro is
    # in both of its modes.
    assert not gen.element_only_in_gated_modes(rows["proto_fs_quick_cue"])
    assert not gen.element_only_in_gated_modes(
        rows["proto_fs_surintendante_chevalmarin"])


def test_interval_bell_spend_title_is_rendered_per_side():
    card = _rows()["proto_fs_interval_bell"]
    assert gen.stage_mode_title(card, 1, None) == "Spend 3"
    assert gen.stage_mode_title(card, 1, None, upgraded=True) == "Spend 2"


def test_upgrade_swap_resolves_both_sides():
    text = "Spend {IfUpgraded:show:2|3}: gain {IfUpgraded:show:6|4}"
    assert gen.resolve_upgrade_swap(text, False) == "Spend 3: gain 4"
    assert gen.resolve_upgrade_swap(text, True) == "Spend 2: gain 6"
