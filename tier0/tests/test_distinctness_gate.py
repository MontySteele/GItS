"""The RATIFIED distinctness gate as a red test.

Thresholds and their two-anchor derivation: [USER] ruling 2026-07-27,
docs/a2-gate-ratification-2026-07-27.md. The gate bites on NEW regressions
immediately; the debt that existed at ratification is curated below and is
worked off by the pool-sweep pass, not waived by it.

Official anchors live in gitignored game_ref/, so in CI this test covers
the committed house pools only -- which are exactly the pools the gate
exists to hold. The curated list contains only house pools for the same
reason: an official anchor can never be "known failing", it is the floor.
"""
import os

import pytest

from tools import card_distinctness_report as cdr

# THE DEBT, RE-BASELINED ON THE CURRENT KITS (legacy cleanup stage 6,
# 2026-10-01). The debt curated at ratification (docs/archive/a2-gate-
# ratification-2026-07-27.md) was measured on the shipped sheets, which are
# deleted; the house pools are now cut from the prototype surface
# (`cdr.surface_pools`), and these are the breaches those pools carry the day
# they were first measured. Every kit is at the Prototype stage, where
# measurement binds nothing (EXPERIMENTS.md binds only at Balance). An entry
# here is DEBT, not a pass, and the staleness test below still forces each one
# out as it clears.
KNOWN_FAILING = {
    ("kokomi", "uniq"),
    ("kokomi", "maxclu"),
    ("kokomi", "neardup"),
    ("varka", "uniq"),
    ("varka", "maxclu"),
    # Furina's pool to 39 (review/active/furina-pool-40-2026-10-05.md,
    # ruled): seven Guest Stars share the `stage_guest` shape and seven
    # two-mode cards share `choose_one`, which the shape metric cannot tell
    # apart (the guest and the mode bodies differ). Prototype-stage debt.
    ("furina", "uniq"),
    ("furina", "maxclu"),
}


def _breaches():
    breaches, _ = cdr.gate_breaches(cdr.build_reports())
    return breaches


def test_no_new_gate_breaches():
    new = [msg for pool, metric, msg in _breaches()
           if (pool, metric) not in KNOWN_FAILING]
    assert not new, (
        "NEW distinctness-gate regression (thresholds RATIFIED 2026-07-27, "
        "docs/archive/a2-gate-ratification-2026-07-27.md): " + "; ".join(new))


def test_known_failing_list_is_not_stale():
    """An entry whose breach no longer occurs must be deleted, or the list
    rots into cover for the next real regression on that (pool, metric)."""
    live = {(pool, metric) for pool, metric, _ in _breaches()}
    measured = {r["pool"] for r in cdr.build_reports()}
    stale = {(pool, metric) for pool, metric in KNOWN_FAILING
             if pool in measured and (pool, metric) not in live}
    assert not stale, f"clear these from KNOWN_FAILING, they pass now: {stale}"


def test_the_curated_list_names_only_house_pools():
    # The official anchors ARE the calibration; listing one as known-failing
    # would mean the gate disagrees with its own floor.
    assert not any(pool.startswith("OFFICIAL:") for pool, _ in KNOWN_FAILING)
    # And every curated pool must be a committed sheet CI can actually see.
    committed = {name for name, _ in cdr.surface_pools()}
    assert {pool for pool, _ in KNOWN_FAILING} <= committed


def test_an_unreadable_pool_is_a_hard_failure(tmp_path, monkeypatch):
    """The red demonstration for the tooling-hardening sprint, item 3.

    `build_reports` used to print `!! <pool>: unreadable` to stderr and
    `continue`. That silently narrowed the gate's scope, and combined with
    `test_no_new_gate_breaches` above -- which asserts over whatever pools
    build_reports happens to return -- a pool that stopped parsing turned its
    own breaches into a PASS. A gate that gets greener the less it can read is
    the worst shape a gate can have.

    Absence is still fine and is checked below: a gitignored game_ref pool that
    is simply not on disk is a legitimate no-op. Present-but-unparseable is not.
    """
    bad = tmp_path / "broken-cards.yaml"
    bad.write_text("cards: [ this: is: not: yaml\n", encoding="utf-8")
    monkeypatch.setattr(cdr, "SHEETS", [str(bad)])
    monkeypatch.setattr(cdr, "GAME_REF", [])

    with pytest.raises(RuntimeError) as exc:
        cdr.build_reports()
    assert "could not be read" in str(exc.value)
    assert "broken" in str(exc.value)


def test_a_pool_file_that_is_absent_is_still_a_no_op(tmp_path, monkeypatch):
    """The other half, and the reason the check keys on PRESENT-and-unreadable.

    game_ref pools are gitignored, so CI genuinely has none of them; skipping a
    path that does not exist is the documented contract, not a narrowing."""
    monkeypatch.setattr(cdr, "SHEETS", [str(tmp_path / "nope-cards.yaml")])
    monkeypatch.setattr(cdr, "GAME_REF", [])
    monkeypatch.setattr(cdr, "SURFACE", str(tmp_path / "nope-surface.yaml"))
    assert cdr.build_reports() == []
