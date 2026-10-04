"""Furina v2 seat round (2026-10-04): chooser titles and the Spend-gated
element preview, as the generator decides them.

Tidal Flourish and Quick Flourish apply Hydro only in their Spend mode, so
their reaction preview is emitted with `elementOnlyOnSpend: true`. Interval
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
    assert gen.element_only_in_gated_modes(rows["proto_fs_tidal_flourish"])
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
