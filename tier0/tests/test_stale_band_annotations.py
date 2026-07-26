"""`stale_bands` annotations must point at bands that actually exist.

B4 (Serenitea Sweep II). A known-stale band still fires `BAND EXCEEDED` on
every run, because a band is ratified law and only a ruling moves it. The
annotation makes that flag say WHY it is firing and what closes it, so a gate
that fires on every Furina scorecard run is not mistaken for a live finding.

THE FAILURE THIS GUARDS is the annotation outliving its reason -- the B6
ledger lesson. When the axis-validity session re-ratifies a band, whoever
edits `deck_bands` must delete the matching `stale_bands` entry. If they
rename or remove the band instead, the annotation becomes a dangling excuse
attached to nothing, and the next reader has no way to tell it from a live
one. An orphan is a test failure here rather than a silent survivor.
"""

from __future__ import annotations

import pytest

from tier0 import roster
from tier0.content import loader

# Driven off the F1 registry rather than a literal list, so character #4
# inherits this rule without anyone remembering to add them.


@pytest.mark.parametrize("character", roster.IDS)
def test_stale_band_annotations_point_at_real_bands(character: str) -> None:
    bands = loader.deck_bands(character)
    stale = loader.stale_bands(character)

    orphans = []
    for axis, per_deck in stale.items():
        for deck in per_deck:
            if deck not in bands.get(axis, {}):
                orphans.append(f"{axis}/{deck}")

    assert not orphans, (
        f"{character}: stale_bands annotates band(s) that no longer exist: "
        f"{orphans}. Delete the annotation in the same change that moved or "
        "removed the band -- an exemption outliving its reason is exactly "
        "what this rule exists to stop.")


@pytest.mark.parametrize("character", roster.IDS)
def test_stale_band_reasons_say_something(character: str) -> None:
    empty = [
        f"{axis}/{deck}"
        for axis, per_deck in loader.stale_bands(character).items()
        for deck, reason in per_deck.items()
        if not str(reason).strip()
    ]

    assert not empty, (
        f"{character}: stale_bands entries with no reason: {empty}. The reason "
        "string is the whole point -- it is what the flag prints.")
