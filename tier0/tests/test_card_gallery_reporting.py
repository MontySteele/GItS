"""The card gallery must not under-report on its own review surface.

Tooling-hardening sprint 2026-07-29, item 5. `render_card_gallery.tile` wrapped
the whole upgrade-diff block in `except Exception: pass`, which collapsed two
different facts into one identical blank:

  * this card HAS no upgrade (ordinary: basics, `_unexpressible` deltas, the
    UNAPPLIABLE set) -- correctly silent;
  * rendering its upgrade THREW (a defect) -- silently reported as the first.

The gallery exists because "an art/number mismatch is the class of defect no
lint can see -- it needs a human looking at the set as a set". A surface built
for that job may not quietly drop a line it failed to compute: the reviewer
reads the blank as a fact about the card. Absence stays silent; a throw now
renders a visible marker.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))

import render_card_gallery as gallery  # noqa: E402
from tier0.content import loader       # noqa: E402


def _any_card():
    """A real card with a real upgrade, so the happy path is the control."""
    for cid in sorted(loader._card_index()):
        try:
            loader.get_card(cid + "+")
        except Exception:               # noqa: BLE001
            continue
        return loader.get_card(cid)
    pytest.skip("no upgradeable card in the index")


def _tile(card):
    """One tile, no art row and no shipped/blocked data -- the upgrade block
    is what is under test."""
    return gallery.tile(card, None, False, False, REPO, {}, {})


def test_a_throwing_upgrade_renders_a_visible_marker(monkeypatch):
    """The red demonstration. Before this, the tile came back with NO upgrade
    line at all and nothing anywhere said why."""
    card = _any_card()

    def boom(card_id):
        if card_id.endswith("+"):
            raise RuntimeError("synthetic upgrade explosion")
        return loader.get_card(card_id)

    monkeypatch.setattr(gallery.loader, "get_card", boom)
    html = _tile(card)
    assert "upg-err" in html, (
        "a throwing upgrade must render an explicit marker, not a blank")
    assert "RuntimeError" in html and "synthetic upgrade explosion" in html


def test_a_throwing_effect_render_is_also_marked(monkeypatch):
    """The second half of the same block: `get_card` can succeed and the DIFF
    can still throw (a malformed effect the line renderer chokes on). Both
    arms of the old single try/except are covered."""
    card = _any_card()
    real = gallery.effect_lines
    calls = {"n": 0}

    def boom(c):
        calls["n"] += 1
        if calls["n"] > 1:              # first call is the base card
            raise ValueError("synthetic effect-line explosion")
        return real(c)

    monkeypatch.setattr(gallery, "effect_lines", boom)
    html = _tile(card)
    assert "upg-err" in html
    assert "synthetic effect-line explosion" in html


def test_a_card_with_no_upgrade_stays_silent(monkeypatch):
    """The other direction, and the reason this is not simply `raise`.

    "No applicable upgrade" is an ORDINARY fact about a card, not a failure of
    the gallery, and marking every basic with a red error box would bury the
    real ones. So absence is silent and only a throw is marked -- which is the
    whole distinction the old bare `except: pass` could not express.
    """
    card = _any_card()

    def no_upgrade(card_id):
        if card_id.endswith("+"):
            raise ValueError(f"no applicable upgrade for {card_id[:-1]!r}")
        return loader.get_card(card_id)

    monkeypatch.setattr(gallery.loader, "get_card", no_upgrade)
    html = _tile(card)
    assert "upg-err" not in html

    # A MISSING card id is the same kind of non-event.
    def missing(card_id):
        if card_id.endswith("+"):
            raise KeyError(card_id)
        return loader.get_card(card_id)

    monkeypatch.setattr(gallery.loader, "get_card", missing)
    assert "upg-err" not in _tile(card)


def test_a_malformed_upgrade_delta_is_not_mistaken_for_absence(monkeypatch):
    """`apply_upgrade` raises ValueError for BOTH "there is no upgrade here"
    and "this delta is malformed" (`innate delta on 'x' must be true`). Only
    the sentinel message is silence; anything else is a defect and shows."""
    card = _any_card()

    def malformed(card_id):
        if card_id.endswith("+"):
            raise ValueError("innate delta on 'probe' must be true")
        return loader.get_card(card_id)

    monkeypatch.setattr(gallery.loader, "get_card", malformed)
    html = _tile(card)
    assert "upg-err" in html
    assert "innate delta" in html


def test_the_error_marker_escapes_the_exception_text():
    """The marker goes into an HTML page, so the exception string is escaped
    like every other value the gallery prints."""
    out = gallery._upgrade_error(ValueError('<script>x</script> & "q"'))
    assert "<script>" not in out
    assert "&lt;script&gt;" in out and "&amp;" in out
