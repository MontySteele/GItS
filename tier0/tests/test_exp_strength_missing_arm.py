"""A comparison table must say when an arm is MISSING.

Tooling-hardening sprint 2026-07-29, item 8. `tier05/exp_furina_strength.py`
cell S4 is the roster calibration -- the cell whose whole output is the
sentence "Furina is N times the reference Ironclad". A failing arm used to
print `SKIPPED` above the table and then drop out of `rows`, so the table a
reader quotes was computed over the SURVIVORS with nothing in it saying so.

The worst case is specific and silent: lose `ref_ironclad` and `ref` is None,
every `vs ref_IC` cell becomes `--`, and the winrate column still reads like a
finished measurement. That is a measurement instrument reporting a narrower
scope in the same shape as a full one, which is the class this repo keeps
calling out.

No sims run here. `model.run_many` is replaced wholesale, so this is cheap and
deterministic and never touches the CPU-heavy batteries the file exists to run.
"""

from __future__ import annotations

from types import SimpleNamespace

from tier05 import exp_furina_strength as exp
from tier05 import model


def _fake_results(n: int):
    return [SimpleNamespace(won=True, acts_completed=3.0, fight_stats=[])
            for _ in range(n)]


def _run_s4(monkeypatch, capsys, broken: set[str]):
    """Run S4 with the named CHARACTERS forced to raise."""
    def fake_run_many(character, archetype, pilot_id, policy, runs, seed,
                      **kw):
        if character in broken:
            raise RuntimeError(f"synthetic arm failure for {character}")
        return _fake_results(3)

    monkeypatch.setattr(model, "run_many", fake_run_many)
    exp.s4(runs=3)
    return capsys.readouterr().out


def test_a_failing_arm_holds_a_missing_row_in_the_table(monkeypatch, capsys):
    """The red demonstration: the arm's LABEL must still be a row, marked."""
    out = _run_s4(monkeypatch, capsys, {"kokomi"})
    rows = [ln for ln in out.splitlines() if "kokomi" in ln]
    assert rows, "the failing arm dropped out of the table entirely"
    assert any("MISSING" in ln for ln in rows), rows
    assert "ARM FAILED" in out
    assert "synthetic arm failure for kokomi" in out
    # ...and the surviving arms still print their numbers.
    assert any("klee" in ln and "%" in ln for ln in out.splitlines())


def test_the_footer_says_the_table_is_not_the_full_comparison(monkeypatch,
                                                             capsys):
    out = _run_s4(monkeypatch, capsys, {"kokomi", "klee"})
    assert "2 of 6 arms MISSING" in out
    assert "NOT the full comparison" in out


def test_losing_the_reference_arm_is_stated_not_implied(monkeypatch, capsys):
    """The specific silent failure. With `ref_ironclad` gone the ratio column
    is `--` for every row, and nothing used to explain why."""
    out = _run_s4(monkeypatch, capsys, {"ref_ironclad"})
    ref_rows = [ln for ln in out.splitlines()
                if ln.strip().startswith("ref_ironclad")]
    assert ref_rows and "MISSING" in ref_rows[0], ref_rows
    assert "ref_ironclad" in out.split("arms MISSING")[1]
    assert "meaningless if ref_ironclad" in out


def test_a_fully_green_run_prints_no_missing_marker(monkeypatch, capsys):
    """The other direction -- the marker must not appear when nothing failed,
    or it stops meaning anything."""
    out = _run_s4(monkeypatch, capsys, set())
    assert "MISSING" not in out
    assert "ARM FAILED" not in out
    # All six arms present, with a ratio column against the reference.
    assert out.count("x\n") >= 6 or "1.0x" in out


def test_s4_arms_are_unchanged_by_this_repair():
    """The repair is to the REPORTING. If the arm list ever shrinks, the fix
    was a scope change wearing a formatting change's clothes."""
    import inspect
    src = inspect.getsource(exp.s4)
    for arm in ("furina / salon", "furina / fanfare", "klee", "kokomi",
                "ref_ironclad", "real_ironclad"):
        assert f'"{arm}"' in src
