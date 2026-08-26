"""EB-115 — `--help` on a tier 0.5 experiment must not RUN the experiment.

`python -m tier05.exp_roster_anchors --help` used to execute a full 600-run,
seed-11 twelve-arm sweep and only then print something, because every
`exp_*.py` reads its arguments inside `main()` -- after the sweep is built and
usually after it has already run. Nothing was recorded from that accidental
run, but the cost was real and it is a curated-footgun class (the same trap
`art_fetch --help` had), not a one-off.

WHY THE GUARD IS THE TEST. Asserting only that `--help` prints something would
pass on the broken code -- the broken code printed too, eventually. What has
to be true is that NOTHING EXPENSIVE RAN, so every door into a simulated run
is booby-trapped before the module is invoked and any call through one fails
the case loudly. The doors are patched by ATTRIBUTE on the modules the scripts
import (`from tier05 import model` / `cells`), which is how every one of them
spells it, so the trap is live no matter which script reaches which door:

  * `model.run_many` / `model.run_one` / `model._run_range` -- the run layer
  * `cells.Cell.run` -- the cell wrapper most of the newer scripts use
  * `harness.runner.run_battery` and `engine.combat.run_fight` -- the two
    deeper doors the older, cell-less scripts reach directly

EVERY `exp_*.py` IS SWEPT, discovered by glob rather than listed. A list is
the thing the next script is not added to; the acceptance is "every one", and
a hard-coded roster would quietly stop meaning that.

The scripts are invoked the way a person invokes them -- `runpy` with
`run_name="__main__"`, so the `__main__` block itself is what runs, which is
where the guard lives. Import alone would prove nothing: none of these
scripts ever did their work at import time.
"""

from __future__ import annotations

import importlib
import runpy
import sys
from pathlib import Path

import pytest

from tier0.engine import combat
from tier0.harness import runner
from tier05 import cells, expcli, model

EXP_DIR = Path(cells.__file__).resolve().parent
SCRIPTS = sorted(p.stem for p in EXP_DIR.glob("exp_*.py"))


def test_there_are_experiments_to_check():
    """A glob that matches nothing passes every parametrised case below."""
    assert len(SCRIPTS) >= 20, SCRIPTS


@pytest.fixture
def no_runs(monkeypatch):
    """Booby-trap every door into a simulated run."""
    fired: list[str] = []

    def trap(name):
        def boom(*args, **kwargs):
            fired.append(name)
            raise AssertionError(
                f"--help reached {name}: the script started doing its work "
                f"before it handled the help flag. That is EB-115's trap "
                f"exactly -- the one command a reader types to find out what "
                f"a script does is the command that runs it.")
        return boom

    monkeypatch.setattr(model, "run_many", trap("model.run_many"))
    monkeypatch.setattr(model, "run_one", trap("model.run_one"))
    monkeypatch.setattr(model, "_run_range", trap("model._run_range"))
    monkeypatch.setattr(cells.Cell, "run", trap("cells.Cell.run"))
    monkeypatch.setattr(runner, "run_battery", trap("runner.run_battery"))
    monkeypatch.setattr(combat, "run_fight", trap("combat.run_fight"))
    return fired


@pytest.mark.parametrize("stem", SCRIPTS)
@pytest.mark.parametrize("flag", ["--help", "-h"])
def test_help_prints_and_exits_without_running_anything(
        stem, flag, no_runs, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", [f"tier05/{stem}.py", flag])
    with pytest.raises(SystemExit) as exc:
        runpy.run_module(f"tier05.{stem}", run_name="__main__")
    # Exit 0: asking for help is not an error, and a non-zero help is a thing
    # CI scripts learn to ignore.
    assert exc.value.code in (0, None), (stem, exc.value.code)
    assert not no_runs, (stem, no_runs)
    out = capsys.readouterr().out
    assert out.strip(), f"{stem} --help printed nothing"


@pytest.mark.parametrize("stem", SCRIPTS)
def test_help_prints_the_scripts_own_documentation(stem, monkeypatch, capsys):
    """Not any old banner: the module's docstring, verbatim. These docstrings
    carry the predictions, the RNG discipline and the usage lines, so a
    hand-written usage string would be a second thing to keep in step."""
    monkeypatch.setattr(sys, "argv", [f"tier05/{stem}.py", "--help"])
    with pytest.raises(SystemExit):
        runpy.run_module(f"tier05.{stem}", run_name="__main__")
    # `runpy` runs the module under the name `__main__` and does not
    # register it, so the docstring is read off a plain import -- which
    # is free here precisely because none of these scripts work at
    # import time.
    doc = importlib.import_module(f"tier05.{stem}").__doc__
    assert doc, f"{stem} has no docstring, so --help has nothing to print"
    assert doc.strip() in capsys.readouterr().out


# ---------------------------------------------------------------------------
#  The helper's own edges
# ---------------------------------------------------------------------------

def test_a_flag_that_merely_starts_with_help_is_not_a_help_request():
    """Prefix matching would turn a future `--helper-arm` into a script that
    prints its docstring instead of running."""
    assert not expcli.help_requested(["--helpful", "-help", "help"])
    assert expcli.help_requested(["--runs", "12", "--help"])
    assert expcli.help_requested(["-h"])


def test_no_help_flag_means_the_helper_does_nothing_at_all():
    """The property the two STAGED REGISTERED INSTRUMENTS depend on
    (`exp_shop_companion_channel` = M14, `exp_eb17p_forced_copy`): a real
    invocation must take the identical path it took before this landed, so
    the helper must not consume, rewrite or even inspect anything but the two
    literal flags."""
    argv = ["--runs", "2400", "--jobs", "0"]
    assert expcli.help_if_asked("doc", argv) is None
    assert argv == ["--runs", "2400", "--jobs", "0"]
