"""`tools/art_process.py`'s command line moves no pixels it was not asked to.

2026-10-21: `art_process.py --help` ignored the flag and ran a full pass,
rewriting about 285 plates under the main checkout's ImageGen (restored with
`--apply-picks art/picks.tsv`). `-h`/`--help` now prints the module docstring
and exits; any other unknown flag exits 2 before the plan is even read --
#1314's fix to `tools/art_fetch.py`, one script over.

The pass itself is replaced with a tripwire (`read_plan`, `process`,
`apply_picks`), so a regression fails here instead of touching art.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

pytest.importorskip("PIL", reason="art_process imports Pillow at module load")

import art_process  # noqa: E402


@pytest.fixture
def tripwire(monkeypatch):
    calls = []

    def boom(name):
        def _f(*args, **kwargs):
            calls.append(name)
            raise AssertionError(f"{name} ran: the pass must not start")
        return _f

    for name in ("read_plan", "process", "apply_picks", "update_manifest"):
        monkeypatch.setattr(art_process, name, boom(name))
    return calls


def _run(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["art_process.py", *args])
    art_process.main()


@pytest.mark.parametrize("flag", ["-h", "--help"])
def test_help_prints_the_docstring_and_runs_nothing(monkeypatch, capfd,
                                                    tripwire, flag):
    _run(monkeypatch, flag)
    out = capfd.readouterr().out
    assert "Process art/raw/ into ImageGen targets" in out
    assert "--apply-picks" in out
    assert tripwire == []


def test_help_wins_beside_other_flags(monkeypatch, capfd, tripwire):
    _run(monkeypatch, "--assets", "a,b", "--help")
    assert "Process art/raw/" in capfd.readouterr().out
    assert tripwire == []


@pytest.mark.parametrize("args", [
    ["--dry-run"],
    ["--usage"],
    ["stray"],
    ["--assets", "a", "--verbose"],
    ["--apply-picks"],
    ["--apply-picks", "--assets", "a"],
    ["--apply-picks", "art/picks.tsv", "extra"],
])
def test_an_unknown_flag_exits_2_before_any_pixels_move(monkeypatch, capfd,
                                                        tripwire, args):
    with pytest.raises(SystemExit) as exc:
        _run(monkeypatch, *args)
    assert exc.value.code == 2
    assert "usage: art_process.py" in capfd.readouterr().err
    assert tripwire == []


def test_the_shipped_spellings_still_reach_the_pass(monkeypatch, tripwire):
    # The bare run and `--apply-picks PATH` get as far as reading the plan,
    # which is the tripwire's first call.
    for args in ([], ["--apply-picks", "art/picks.tsv"],
                 ["--assets", "a,b"]):
        tripwire.clear()
        with pytest.raises(AssertionError):
            _run(monkeypatch, *args)
        assert tripwire == ["read_plan"]
