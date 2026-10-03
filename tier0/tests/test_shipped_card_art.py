"""The shipped card-image set (`tools/shipped_card_art.py`).

Deploy used to copy every png in ImageGen's card dirs, so the 2026-10-02
install carried 743 images where 433 can be drawn. These tests hold the set
shut in both directions: every live card resolves to a shipped image or is on
`art_coverage.KNOWN_MISSING`, and nothing staged is unreachable.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools import art_coverage
from tools import shipped_card_art as sca

ROOT = Path(__file__).resolve().parents[2]


def test_every_surface_key_is_requested_by_the_mod():
    """A live row (or an art_of target) the C# does not ask for means the
    generated C# is stale: the card would render blank whatever ships."""
    drift = sca.surface_keys() - sca.runtime_keys()
    assert not drift, sorted(drift)


def test_the_runtime_set_is_not_vacuous():
    keys = sca.runtime_keys()
    assert len(keys) >= 400, len(keys)
    # Built in code, not on the surface: Ancients and hand-written tokens.
    for key in ("confiscated", "jumpy_dumpty_mk2", "prayer_to_the_moon",
                "the_sea_is_my_stage", "kk_sea_glass"):
        assert key in keys, key


def test_known_missing_names_only_live_keys():
    """An entry for a card that was cut is a stale excuse; delete it."""
    stale = set(art_coverage.KNOWN_MISSING) - sca.shipped_keys()
    assert not stale, sorted(stale)


@pytest.mark.skipif(not sca.IMAGES.is_dir(),
                    reason="no ImageGen/images/cards on this checkout")
def test_every_live_card_resolves_to_a_shipped_image_or_known_missing():
    _ship, _dropped, missing = sca.plan()
    assert not sca.missing_findings(missing)


def _png(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x89PNG")
    return path


def test_plan_ships_keys_and_drops_the_rest_from_any_dir(tmp_path):
    root = tmp_path / "cards"
    _png(root / "klee" / "live_a.png")
    _png(root / "klee" / "cut_card.png")
    _png(root / "newchar" / "live_b.png")     # a dir no list names
    ship, dropped, missing = sca.plan(root, {"live_a", "live_b", "unpainted"})
    assert set(ship) == {"live_a", "live_b"}
    assert set(dropped) == {"cut_card"}
    assert missing == ["unpainted"]


def test_check_stage_refuses_missing_and_unreachable(tmp_path):
    root = tmp_path / "cards"
    _png(root / "klee" / "live_a.png")
    _png(root / "klee" / "live_b.png")
    _png(root / "klee" / "cut_card.png")
    keys = {"live_a", "live_b"}
    stage = tmp_path / "stage"
    _png(stage / "live_a.png")
    _png(stage / "cut_card.png")
    findings = sca.check_stage(stage, root, keys)
    assert any("live_b.png ships" in f for f in findings), findings
    assert any("cut_card.png is staged" in f for f in findings), findings
    (stage / "cut_card.png").unlink()
    _png(stage / "live_b.png")
    assert sca.check_stage(stage, root, keys) == []


def test_missing_findings_both_directions(monkeypatch):
    monkeypatch.setattr(art_coverage, "KNOWN_MISSING", {"old": "painted now"})
    findings = sca.missing_findings(["fresh"])
    assert any(f.startswith("fresh:") for f in findings)
    assert any(f.startswith("old:") for f in findings)


@pytest.mark.parametrize("script", ["deploy.ps1", "deploy_proto.ps1"])
def test_deploy_scripts_stage_through_the_shipped_set(script):
    """The blanket `Copy-Item <dir>\\*.png` is what shipped 310 dead images."""
    text = (ROOT / "klee-mod" / "build" / script).read_text(encoding="utf-8")
    code = "\n".join(l for l in text.splitlines()
                     if not l.lstrip().startswith("#"))
    assert "tools\\shipped_card_art.py" in code
    assert "'--stage'" in code
    assert "$artSrcDirs" not in code
