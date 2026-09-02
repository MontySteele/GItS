"""The pre-push gate must not hand git's own environment to the suite.

THE INCIDENT (2026-09-02), which is why this file exists rather than a comment.

`tools/hooks/pre_push_gate.py` runs the fast lane and the lint lane as child
processes of a git `pre-push` hook. Git EXPORTS its state into a hook's
environment -- `GIT_DIR`, `GIT_INDEX_FILE`, `GIT_WORK_TREE`, `GIT_PREFIX`,
`GIT_COMMON_DIR`, `GIT_OBJECT_DIRECTORY`, `GIT_QUARANTINE_PATH` -- and
**`GIT_DIR` outranks the working directory**. This suite is full of fixtures
that build a repository under `tmp_path` and commit into it. Inherit `GIT_DIR`
and every one of those commits lands in the REAL repository instead, on the
branch being pushed.

Within minutes of the hook first being installed that produced, across three
worktrees: fixture commits on two agents' live branches, a tracked file deleted
on one of them, a stray `refs/heads/origin/main` branch and a `fixture-ledger`
tag in the shared repo, `core.bare = true` on a non-bare repository, and 28
`index.lock` collisions.

WHAT IS PINNED HERE, in the order a reader should want it:

  1. the scrub is by PREFIX, not by a list of names -- a list is the same
     defect one release of git later;
  2. END TO END: with `GIT_DIR` pointing at a real repository, a child launched
     through `_child_env` builds its own repo and commits, and the pointed-at
     repository does not move. This is the assertion the incident would have
     failed, and it runs no git hook and pushes nothing;
  3. the shell shim installs the same scrub, because the inline arm runs pytest
     from `sh` and never reaches the python above.

Complementary to, and deliberately not a substitute for, a conftest-level
scrub: this one fixes the source, that one defends every other way a stray
`GIT_DIR` could arrive.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOKS = REPO / "tools" / "hooks"

sys.path.insert(0, str(HOOKS))
import pre_push_gate                                              # noqa: E402
import install as hook_installer                                  # noqa: E402


GIT_LEAKS = {
    "GIT_DIR": "somewhere/else/.git",
    "GIT_WORK_TREE": "somewhere/else",
    "GIT_INDEX_FILE": "somewhere/else/index",
    "GIT_PREFIX": "sub/dir/",
    "GIT_COMMON_DIR": "somewhere/else/.git",
    "GIT_OBJECT_DIRECTORY": "somewhere/else/objects",
    "GIT_QUARANTINE_PATH": "somewhere/else/quarantine",
    # Not a real variable. The point of the prefix rule is the one nobody has
    # heard of yet.
    "GIT_SOMETHING_INVENTED_LATER": "1",
}


def test_no_git_variable_survives_into_the_child(monkeypatch):
    for key, value in GIT_LEAKS.items():
        monkeypatch.setenv(key, value)
    env = pre_push_gate._child_env(REPO)
    survived = sorted(k for k in env if k.startswith("GIT_"))
    assert survived == [], survived


def test_the_scrub_leaves_the_rest_of_the_environment_alone(monkeypatch):
    """A gate that emptied the environment would pass the test above and fail
    to run python at all."""
    monkeypatch.setenv("GIT_DIR", "somewhere/else/.git")
    monkeypatch.setenv("DIGITAL_SIGNATURE", "keep me")
    env = pre_push_gate._child_env(REPO)
    assert env.get("DIGITAL_SIGNATURE") == "keep me"
    assert env.get("PYTHONPATH") == str(REPO)
    assert "PATH" in env


def test_a_fixture_repo_built_under_the_hook_env_does_not_touch_the_real_one(
        tmp_path, monkeypatch):
    """THE INCIDENT, as an assertion.

    A 'surrounding' repository stands in for this checkout, `GIT_DIR` is
    pointed at it exactly as git would point it at ours, and a child process
    launched through `_child_env` does what a test fixture does: make its own
    repository somewhere else and commit. Afterwards the surrounding repo must
    be byte-for-byte where it was -- same HEAD, same ref count, still not bare.
    """
    if not _git_available():
        pytest.skip("git is not on PATH")

    surrounding = tmp_path / "surrounding"
    surrounding.mkdir()
    _git(surrounding, "init", "-q")
    (surrounding / "tracked.txt").write_text("one\n", encoding="utf-8")
    _git(surrounding, "add", "tracked.txt")
    _git(surrounding, "commit", "-q", "-m", "one")
    before_head = _git(surrounding, "rev-parse", "HEAD").stdout.strip()
    before_refs = _git(surrounding, "for-each-ref").stdout

    # Exactly what git hands a hook.
    monkeypatch.setenv("GIT_DIR", str(surrounding / ".git"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(surrounding / ".git" / "index"))
    monkeypatch.setenv("GIT_WORK_TREE", str(surrounding))

    fixture = tmp_path / "fixture"
    fixture.mkdir()
    script = (
        "import subprocess, sys, pathlib\n"
        "d = pathlib.Path(sys.argv[1])\n"
        "def g(*a):\n"
        "    subprocess.run(['git', '-C', str(d), *a], check=True,\n"
        "                   capture_output=True)\n"
        "g('init', '-q')\n"
        "g('-c', 'user.email=t@example.invalid', '-c', 'user.name=t',\n"
        "  'commit', '-q', '--allow-empty', '-m', 'fixture history')\n"
    )
    proc = subprocess.run(
        [sys.executable, "-c", script, str(fixture)],
        cwd=str(tmp_path), capture_output=True, text=True,
        env=pre_push_gate._child_env(tmp_path))
    assert proc.returncode == 0, proc.stdout + proc.stderr

    # The fixture really did commit -- otherwise this test proves nothing.
    assert _git(fixture, "rev-parse", "HEAD").returncode == 0

    # And the surrounding repository did not move.
    assert _git(surrounding, "rev-parse", "HEAD").stdout.strip() == before_head
    assert _git(surrounding, "for-each-ref").stdout == before_refs
    assert _git(surrounding, "config", "--get",
                "core.bare").stdout.strip() in ("", "false")


def test_the_shell_shim_scrubs_by_prefix_too():
    """The inline arm runs pytest from `sh` and never reaches the python
    above, so the shim carries the same rule in its own language."""
    shim = hook_installer.SHIM
    assert "GIT_[A-Za-z0-9_]*" in shim, (
        "the shim scrubs a named list only; deny by prefix")
    assert "unset GIT_DIR" in shim, (
        "the explicit fallback is gone, so a shell without sed scrubs nothing")


def _git_available() -> bool:
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return False
    return True


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    """git in `repo`, with a CLEAN environment.

    The helper has to scrub too: this module sets GIT_DIR on purpose, and a
    helper that inherited it would report on the wrong repository -- which is
    the very confusion under test.
    """
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = "t"
    env["GIT_AUTHOR_EMAIL"] = env["GIT_COMMITTER_EMAIL"] = "t@example.invalid"
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, env=env)
