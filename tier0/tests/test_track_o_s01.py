"""Track O slice 1 -- P1.5 bridge seed honouring, pinned where it is right.

These are PINS, not findings. Every assertion here passes against the code as
it stands and locks in behaviour that P1.5's own docs state is the contract:

    understudy/rng.py          the policy stream is reproducible ACROSS
                               processes and ACROSS runs, and the label offset
                               is deliberately not `hash()`
    understudy/bridge.py       `set_seed` sends what it was given; the
                               canonical form is ASKED FOR, never retyped here
    understudy/trace_replay.py the seed guard refuses two runs on two
                               different seeds before it diffs anything

The DEFECTS this slice found are deliberately NOT written as failing or xfail
tests. They live in the Track O report with their fixtures under
`review/redteam/fixtures/track_o/s01-*`, because a red bar in the suite is a
statement about the build and these are statements about an instrument's
blind spots.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from understudy import bridge, report, rng
from understudy import trace_replay as replay

FIXTURES = Path(__file__).resolve().parents[2] / "review" / "redteam" \
    / "fixtures" / "track_o"


# ------------------------------------------------------------------ rng ----

def test_the_label_offset_is_stable_across_processes():
    """`_label_offset`'s comment says "stable across processes, unlike
    hash()". That is only checkable by writing the numbers down: a switch to
    `hash()` would still pass every other test in the tree, and would make two
    soaks on one seed disagree for a reason no log records."""
    assert rng._label_offset("") == 0
    assert rng._label_offset("draft") == 1607
    assert rng._label_offset("shop") == 1104
    assert rng._label_offset("route") == 1656
    # Positional weighting is the whole mechanism: an anagram is a different
    # stream.
    assert rng._label_offset("ab") != rng._label_offset("ba")


def test_a_policy_stream_is_the_same_stream_in_every_process():
    """policy_v0/v1 are "meant to be reproducible ACROSS runs, so that two
    runs disagreeing is a fact about the runs" (rng.py, POLICY_BASE_SEED). A
    run recorded today and a rerun next month must draw the same numbers, so
    the numbers are written down rather than compared to themselves."""
    assert rng.POLICY_BASE_SEED + rng.UNDERSTUDY_STREAM_OFFSET == 7020260804
    # Spelled as integers rather than floats so the pin cannot rot on a
    # platform's float repr while still naming the actual sequence.
    assert [rng.policy_rng("draft").randrange(10**9) for _ in range(1)] == \
        [611523672]
    assert rng.policy_rng("shop").randrange(10**9) == 731096448
    a = rng.policy_rng("draft")
    b = rng.policy_rng("draft")
    assert [a.random() for _ in range(5)] == [b.random() for _ in range(5)]
    assert rng.policy_rng("draft").randrange(10**9) == \
        rng.policy_rng("draft").randrange(10**9)


def test_the_leak_guard_refuses_the_form_the_game_actually_reads_back():
    """`bridge.current_seed()` returns the CANONICAL seed -- upper case, 'O'
    mapped to '0' and 'I' to '1' -- so that is the exact string most likely to
    be passed as a label by hand. It must be refused."""
    for canonical in ("SSRWEGLNRG", "P15BR1DGE1", "ABCDEFGHIJ"):
        with pytest.raises(rng.GameSeedLeak):
            rng.policy_rng(canonical)


# --------------------------------------------------------------- bridge ----

def test_set_seed_does_not_canonicalise_on_this_side(monkeypatch):
    """"The mapping is asked for, never retyped" (soak.py, `_embark`). A
    client-side upper() here would be a second copy of SeedHelper's rule, and
    the copy is the thing that goes stale."""
    seen = {}
    monkeypatch.setattr(bridge, "_request",
                        lambda url, payload=None, timeout=20.0:
                        seen.update(url=url, payload=payload)
                        or {"status": "ok", "chosen": "P15BR1DGE1"})
    bridge.set_seed("p15bridgei")
    assert seen["payload"] == {"seed": "p15bridgei"}
    assert seen["url"] == bridge.SEED


def test_clear_seed_is_a_null_and_not_an_empty_string(monkeypatch):
    """The endpoint distinguishes null (clear) from a missing field (400).
    An empty string would reach the same clear branch by a different door and
    would leave `chosen` unset on the caller's side."""
    seen = {}
    monkeypatch.setattr(bridge, "_request",
                        lambda url, payload=None, timeout=20.0:
                        seen.update(payload=payload) or {"status": "ok"})
    bridge.clear_seed()
    assert json.dumps(seen["payload"]) == '{"seed": null}'


def test_current_seed_reads_the_run_and_not_the_compendium_root(monkeypatch):
    """The seed lives under `current_run`. Reading a top-level `seed` would
    pick up the compendium's own key on a build that grows one."""
    monkeypatch.setattr(bridge, "compendium",
                        lambda: {"seed": "WRONGWRONG",
                                 "current_run": {"seed": "ABCDEFGHIJ"}})
    assert bridge.current_seed() == "ABCDEFGHIJ"


# ---------------------------------------------------------- trace_replay ---

def _stage(tmp_path, monkeypatch, pairs):
    """Copy fixture logs into a private LOG_DIR under the soak naming."""
    for fixture, target in pairs:
        (tmp_path / target).write_bytes((FIXTURES / fixture).read_bytes())
    monkeypatch.setattr(report, "LOG_DIR", tmp_path)
    return tmp_path


def test_two_different_seeds_are_refused_before_anything_is_diffed(
        tmp_path, monkeypatch):
    """The guard's live half, from committed fixtures rather than an inline
    dict: a SEED finding is returned ALONE, and no per-field diff follows it.
    A comparison that also printed the field diffs would dress an
    incomparable pair as a measurement."""
    _stage(tmp_path, monkeypatch, [
        ("s01-seed-ABCDEFGHIJ-runA.jsonl", "soak-toA-run001.jsonl"),
        ("s01-seed-KLMNOPQRST-runB.jsonl", "soak-toB-run001.jsonl")])
    findings = replay.compare_runs(("toA", 1), ("toB", 1))
    assert len(findings) == 1
    assert findings[0].startswith("SEED: ABCDEFGHIJ != KLMNOPQRST")


def test_seed_of_reports_the_record_verbatim(tmp_path, monkeypatch):
    """`chosen` and `honoured` travel with the seed. They are what tells a
    reader whether a run was ASKED for or merely observed, and a reader that
    lost them could not tell a P1.5 arm from an R95 one."""
    _stage(tmp_path, monkeypatch,
           [("s01-seed-ABCDEFGHIJ-runA.jsonl", "soak-toA-run001.jsonl")])
    assert replay.seed_of("toA", 1) == {"seed": "ABCDEFGHIJ",
                                        "chosen": "ABCDEFGHIJ",
                                        "honoured": True}


def test_a_selector_divergence_on_one_seed_is_reported(tmp_path, monkeypatch):
    """The instrument's reason to exist, pinned from fixtures: same seed,
    different recorded answer, one finding naming the field."""
    _stage(tmp_path, monkeypatch, [
        ("s01-seed-ABCDEFGHIJ-runA.jsonl", "soak-toA-run001.jsonl"),
        ("s01-seed-ABCDEFGHIJ-runA.jsonl", "soak-toB-run001.jsonl")])
    assert replay.compare_runs(("toA", 1), ("toB", 1)) == []

    other = json.loads(
        (FIXTURES / "s01-nullseed-divergent-runB.jsonl").read_text(
            encoding="utf-8").splitlines()[1])
    head = (FIXTURES / "s01-seed-ABCDEFGHIJ-runA.jsonl").read_text(
        encoding="utf-8").splitlines()[0]
    (tmp_path / "soak-toB-run001.jsonl").write_text(
        head + "\n" + json.dumps(other) + "\n", encoding="utf-8")
    findings = replay.compare_runs(("toA", 1), ("toB", 1))
    assert len(findings) == 1 and "selectors diverges" in findings[0]
