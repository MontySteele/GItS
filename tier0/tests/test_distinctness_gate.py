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

# Known debt at ratification time (docs/archive/a2-gate-ratification-2026-07-27.md,
# "Where the roster lands"). An entry here is DEBT, not a pass. Remove each
# as its pool-sweep pass clears it; the staleness test below forces the
# removal so this list can only shrink.
KNOWN_FAILING = {
    ("klee", "uniq"),        # 61% -- signature repetition, one defect
    # furina uniq/neardup CLEARED by the Curtain Call sweep (R85,
    # 2026-07-27): 62->76 / 0.94->0.15 per card, inside the official band.
    # The Track-B maxclu transient (6) resolved in the same sweep (3).
    ("kokomi", "uniq"),      # 53% -- breadth (was 56% pre-EB-69)
    ("kokomi", "maxclu"),    # 8 -- the block cluster (was 7 pre-EB-69)
    # ("kokomi", "neardup") -- NEW AT EB-69 (R198, 2026-08-23), 26% -> 33%
    # against a ratified threshold of 30%. THIS IS THE FILL'S OWN FINDING AND
    # IT IS NOT BEING TREATED AS COVER. The 14 ruled bodies are rebuilds of
    # shapes the pool already prints -- another 0-cost cycler, another Sly
    # Block skill, another cost_mod rider, another metallicize common -- which
    # is precisely how a fill closes a COUNT gap without closing a BREADTH
    # gap. Phase-0 §2.5 keeps this gate independent and binding, so it is
    # entered here to keep the wall green while the content question went to
    # [USER] at QUEUE `M36` with the two strict-domination pairs it shares a
    # cause with.
    #
    # RULED 2026-08-24, R200 -- AND THE BREACH IS NOT RATIFIED. [USER] ruled
    # 33% TEMPORARY, carried by this entry THROUGH Phase 3 and cleared there.
    # One body from each pair is redesigned and the targets are named:
    # moon_signal, crane_wing, tighten_the_cords (see
    # tools/lint_strict_domination.PENDING_RULING for which end of each pair
    # and why). The replacement bodies are authored in the EB-118 Phase-3
    # batch -- a design act then, not now.
    # Gate: BACKLOG `EB-125`. When the three redesigns land, re-measure and
    # DELETE this entry; the staleness test below forces the deletion the
    # moment the breach stops reproducing. There is no branch where this
    # becomes a moved threshold -- R200 declined that. The two entries above
    # are pre-existing debt and are not part of EB-125.
    ("kokomi", "neardup"),
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
    committed = {os.path.basename(p).replace("-cards.yaml", "")
                 .replace(".yaml", "") for p in cdr.SHEETS}
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
    assert cdr.build_reports() == []
