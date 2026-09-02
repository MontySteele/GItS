"""The suite may not commit into the repository it is being run from.

WHAT HAPPENED, 2026-09-02. Five test files here build throwaway git
repositories under `tmp_path`. Every one of them passes `cwd=<the temp repo>`
and none passes `env` — correct, right up until the process they inherit
carries `GIT_DIR`, which OUTRANKS `cwd` absolutely. The push gate runs the
fast lane as a child of the harness, that environment carried a `GIT_DIR`
pointing at the session's own worktree, and sixteen xdist workers each ran
`test_rulings_index.py`'s seven fixture commits into it: twenty-eight tests
failed on `index.lock` contention, and the workers that won the lock left the
branch on *"R16 landed: the sixteenth ruling, as ruled"* with an empty index.
The reflog had the real commits and a mixed reset put them back — but the
suite had rewritten the developer's branch, and nothing in the tree could
have stopped it.

`tier0/tests/conftest.py` deletes the whole `GIT_DIR` family at import time.
This file is the gate on that: the first test proves the guard is in place,
and the second proves it is LOAD-BEARING by reproducing the escape — a child
handed `GIT_DIR` commits into the repository it names while sitting in a
different directory entirely.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

LEAKED = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE",
          "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
          "GIT_COMMON_DIR", "GIT_NAMESPACE", "GIT_CEILING_DIRECTORIES")

ID = ["-c", "commit.gpgsign=false", "-c", "user.name=Fixture",
      "-c", "user.email=fixture@example.invalid"]


def _repo(where: Path) -> Path:
    where.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(where)], check=True,
                   capture_output=True)
    return where


@pytest.mark.parametrize("name", LEAKED)
def test_the_git_environment_is_scrubbed_for_the_whole_session(name):
    assert name not in os.environ, (
        f"{name} is set in the test process. `conftest.py` deletes it at "
        f"import time precisely because it outranks every `cwd=` in this "
        f"suite; something re-set it.")


def test_the_scrub_is_load_bearing_because_GIT_DIR_outranks_cwd(tmp_path):
    """The escape, reproduced — and this is why the guard is not decoration.

    Two commits, same working directory, same command. The one handed
    `GIT_DIR` lands in the OTHER repository. If this ever stops being true,
    the conftest scrub can go.
    """
    theirs = _repo(tmp_path / "theirs")
    mine = _repo(tmp_path / "mine")

    clean = subprocess.run(["git", *ID, "commit", "-q", "--allow-empty",
                            "-m", "landed where I stood"],
                           cwd=mine, capture_output=True, text=True)
    assert clean.returncode == 0, clean.stdout + clean.stderr

    poisoned_env = dict(os.environ)
    poisoned_env["GIT_DIR"] = str(theirs / ".git")
    poisoned = subprocess.run(["git", *ID, "commit", "-q", "--allow-empty",
                               "-m", "landed somewhere else"],
                              cwd=mine, capture_output=True, text=True,
                              env=poisoned_env)
    assert poisoned.returncode == 0, poisoned.stdout + poisoned.stderr

    def subjects(root: Path) -> list[str]:
        out = subprocess.run(["git", "log", "--format=%s"], cwd=root,
                             capture_output=True, text=True)
        return [line for line in out.stdout.split("\n") if line.strip()]

    assert subjects(mine) == ["landed where I stood"]
    assert subjects(theirs) == ["landed somewhere else"], (
        "GIT_DIR no longer outranks cwd -- re-read conftest.py's scrub before "
        "deleting it")


def test_the_conftest_scrub_names_every_variable_this_file_checks():
    """The two lists are the same list, in two files. Keep them so."""
    text = (REPO / "tier0" / "tests" / "conftest.py").read_text(
        encoding="utf-8")
    for name in LEAKED:
        assert f'"{name}"' in text, f"conftest.py does not scrub {name}"
