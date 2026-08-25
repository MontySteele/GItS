"""The `game_ref/` backup wipe-guard, exercised hermetically.

WHY THIS TEST IS THE POINT OF THE TOOL. `tools/backup_game_ref.py` mirrors the
primary checkout's `game_ref/` into the OneDrive vault, and it REFUSES (exit 2)
when the source is missing or holds fewer than ten files. That refusal is not a
nicety. `game_ref/` has been destroyed four times and each time the directory
was left *present and empty* with `git status` clean, so a plain mirror pointed
at a destroyed-empty source would faithfully propagate the destruction — delete
every file in the vault — and the one surviving copy of the hand-authored,
explicitly NOT tool-regenerable pass layers would be gone the moment someone
ran the backup "to be safe". The guard is what makes an unattended run safe to
type, and until now nothing proved it fires.

HERMETIC, AND THAT WORD IS LOAD-BEARING HERE. Every path in this file is a
pytest `tmp_path`. No test reads the real `game_ref/` (absent in every worktree
by construction — it is gitignored and decompile-derived) and, more
importantly, **no test can reach the real vault**: both `SOURCE` and `VAULT`
are monkeypatched on every test that calls `main` or `mirror`, and the
assertions afterwards are about the temp vault's contents. A test for a
destructive tool that could itself be destructive would be worse than no test.

HERMETIC ACROSS PLATFORMS, WHICH IS A SEPARATE CLAIM. The CI runner is Ubuntu
(`.github/workflows/repo.yml`, job `pytest`) and `pathlib.Path` binds to the
running platform: the vault string is one *relative* component named
`C:\\Users\\...` on POSIX. So no assertion here may read `backup.VAULT.parts`
— shape questions go to `backup.VAULT_WINDOWS`, which parses as Windows on
every host — and no test may depend on the configured vault being absolute.
The two `platform_refusal` tests below drive `sys.platform` themselves, so they
assert the same thing on Windows and on the runner.

FAST LANE. Deliberately unmarked: `battery` is the only registered marker and
the fast lane is `-m "not battery"`, so an unmarked test runs there. This is
filesystem work on a handful of tiny temp files and belongs in the inner loop —
the guard is exactly the thing you want checked before you push a change to the
tool.
"""

from __future__ import annotations

import sys
from pathlib import Path, PurePosixPath, PureWindowsPath

import pytest

from tools import backup_game_ref as backup


def _populate(root, count, prefix="f"):
    """`count` tiny files under `root`, some of them nested."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "sub").mkdir(exist_ok=True)
    for i in range(count):
        target = (root / "sub" if i % 3 == 0 else root) / f"{prefix}{i}.yaml"
        target.write_text(f"row: {i}\n", encoding="utf-8")
    return root


# --- the guard, on its own -------------------------------------------------

def test_guard_refuses_a_missing_source(tmp_path):
    reason = backup.guard(tmp_path / "nope")
    assert reason is not None
    assert "does not exist" in reason


def test_guard_refuses_an_empty_source(tmp_path):
    """The destroyed-empty state: present, zero files, `git status` clean."""
    (tmp_path / "game_ref").mkdir()
    reason = backup.guard(tmp_path / "game_ref")
    assert reason is not None and "0 file(s)" in reason


@pytest.mark.parametrize("count", [1, 5, backup.MIN_SOURCE_FILES - 1])
def test_guard_refuses_a_short_source(tmp_path, count):
    """A PARTIAL restore is as dangerous as none: mirroring it deletes every
    vault file the partial tree happens not to carry."""
    src = _populate(tmp_path / "game_ref", count)
    reason = backup.guard(src)
    assert reason is not None
    assert f"{count} file(s)" in reason and "floor" in reason


@pytest.mark.parametrize("count", [backup.MIN_SOURCE_FILES,
                                   backup.MIN_SOURCE_FILES + 15])
def test_guard_passes_a_real_looking_source(tmp_path, count):
    assert backup.guard(_populate(tmp_path / "game_ref", count)) is None


def test_the_floor_is_below_a_real_tree_and_above_the_empty_state():
    """The threshold's own reason for being 10, kept as an assertion rather
    than as a comment that can drift from the constant."""
    assert 0 < backup.MIN_SOURCE_FILES < 25


# --- the catastrophe the guard exists to prevent ---------------------------

@pytest.mark.parametrize("source_state", ["missing", "empty", "partial"])
def test_a_destroyed_source_cannot_wipe_the_vault(tmp_path, monkeypatch,
                                                  capsys, source_state):
    """THE LOAD-BEARING TEST. A full vault, a destroyed source, and `main`
    must exit 2 with the vault byte-for-byte untouched."""
    vault = _populate(tmp_path / "vault", 12, prefix="v")
    before = {p.relative_to(vault).as_posix(): p.read_text(encoding="utf-8")
              for p in vault.rglob("*") if p.is_file()}
    assert len(before) == 12

    src = tmp_path / "game_ref"
    if source_state == "empty":
        src.mkdir()
    elif source_state == "partial":
        _populate(src, 3)

    monkeypatch.setattr(backup, "SOURCE", src)
    monkeypatch.setattr(backup, "VAULT", vault)

    assert backup.main([]) == 2
    assert "REFUSING TO MIRROR" in capsys.readouterr().out

    after = {p.relative_to(vault).as_posix(): p.read_text(encoding="utf-8")
             for p in vault.rglob("*") if p.is_file()}
    assert after == before, "the guard let a destroyed source reach the vault"


def test_the_refusal_is_the_same_on_a_dry_run(tmp_path, monkeypatch, capsys):
    """`--dry-run` must not be a way past the guard: it refuses first."""
    vault = _populate(tmp_path / "vault", 12, prefix="v")
    monkeypatch.setattr(backup, "SOURCE", tmp_path / "gone")
    monkeypatch.setattr(backup, "VAULT", vault)
    assert backup.main(["--dry-run"]) == 2
    assert "REFUSING TO MIRROR" in capsys.readouterr().out
    assert len(list(vault.rglob("*.yaml"))) == 12


# --- the happy path, so the guard is not passing by never running ----------

def test_a_healthy_source_mirrors(tmp_path, monkeypatch, capsys):
    src = _populate(tmp_path / "game_ref", 12)
    vault = tmp_path / "vault"
    monkeypatch.setattr(backup, "SOURCE", src)
    monkeypatch.setattr(backup, "VAULT", vault)

    assert backup.main([]) == 0
    assert "REFUSING" not in capsys.readouterr().out
    mirrored = {p.relative_to(vault).as_posix()
                for p in vault.rglob("*") if p.is_file()}
    assert mirrored == {p.relative_to(src).as_posix()
                        for p in src.rglob("*") if p.is_file()}


def test_a_dry_run_writes_nothing(tmp_path, monkeypatch):
    src = _populate(tmp_path / "game_ref", 12)
    vault = tmp_path / "vault"
    vault.mkdir()
    monkeypatch.setattr(backup, "SOURCE", src)
    monkeypatch.setattr(backup, "VAULT", vault)
    copied, deleted, unchanged = backup.mirror(src, vault, dry_run=True)
    assert len(copied) == 12 and deleted == [] and unchanged == []
    assert list(vault.rglob("*")) == []


def test_a_vault_only_file_is_deleted_once_the_guard_passes(tmp_path):
    """The delete arm is real — which is precisely why the guard matters."""
    src = _populate(tmp_path / "game_ref", 12)
    vault = _populate(tmp_path / "vault", 12)
    (vault / "stale_generation.yaml").write_text("old\n", encoding="utf-8")
    _copied, deleted, _unchanged = backup.mirror(src, vault)
    assert "stale_generation.yaml" in deleted
    assert not (vault / "stale_generation.yaml").exists()


# --- the vault location is ruled, not configurable -------------------------

def test_the_vault_is_hard_coded_outside_any_worktree():
    """R[USER] 2026-08-24: OneDrive, chosen because it is not a directory a
    worktree teardown can reach — `git worktree remove` deletes gitignored
    content out of a clean worktree, which is what took both prior backups.
    A configurable backup root is a backup root that can be pointed at a temp
    directory and quietly stop being a backup, so the constant is asserted
    rather than merely commented.

    Asked of `VAULT_WINDOWS`, not `VAULT`: the question is about the Windows
    path's shape, and `Path` cannot answer it off Windows."""
    parts = [p.lower() for p in backup.VAULT_WINDOWS.parts]
    assert backup.VAULT_WINDOWS.is_absolute()
    assert parts[-1] == "game_ref"
    assert "onedrive" in parts
    assert "worktrees" not in parts


# --- the vault is a Windows path, and this host may not be Windows ----------

def test_the_vault_string_is_relative_under_posix_semantics():
    """The whole reason `platform_refusal` exists, pinned as the fact it is
    rather than as prose. Same verdict on either host — both parsers are
    asked by name, neither is the running platform's."""
    assert PureWindowsPath(backup.VAULT_SPEC).is_absolute()
    posix = PurePosixPath(backup.VAULT_SPEC)
    assert not posix.is_absolute()
    assert len(posix.parts) == 1, "one backslash-laden component, not a tree"


@pytest.mark.parametrize("platform", ["linux", "darwin"])
def test_the_configured_vault_is_refused_off_windows(monkeypatch, platform):
    monkeypatch.setattr(backup.sys, "platform", platform)
    reason = backup.platform_refusal(backup.VAULT)
    assert reason is not None and platform in reason


def test_an_absolute_override_is_accepted_anywhere(monkeypatch, tmp_path):
    """The escape hatch the suite itself rides: a vault that is absolute HERE
    is fine on any host, which is what keeps every other test in this file
    hermetic on the Ubuntu runner."""
    for platform in ("linux", "darwin", "win32"):
        monkeypatch.setattr(backup.sys, "platform", platform)
        assert backup.platform_refusal(tmp_path / "vault") is None


@pytest.mark.skipif(sys.platform != "win32",
                    reason="the configured vault is only a vault on Windows")
def test_the_configured_vault_is_accepted_on_the_windows_primary():
    """The converse of the refusal, and it can only be asked where it holds:
    `Path` is platform-bound, so no monkeypatching of `sys.platform` makes the
    Windows vault absolute on the Ubuntu runner. The skip there is the
    accurate answer, not a gap — the tool does not run there."""
    assert backup.platform_refusal(backup.VAULT) is None


def test_a_relative_vault_cannot_be_created_underfoot(tmp_path, monkeypatch,
                                                      capsys):
    """THE FAUX-DIRECTORY TEST. A healthy source passes the wipe-guard, so
    only the platform refusal stands between a relative vault and a directory
    of that name appearing under the working directory. Exit 2, cwd empty.

    The vault here is relative on BOTH hosts rather than the configured
    Windows string, which is what the configured string DEGRADES TO on POSIX:
    a regression then writes into a temp cwd instead of into the real vault.
    A test for a destructive tool cannot itself be destructive."""
    src = _populate(tmp_path / "game_ref", 12)
    cwd = tmp_path / "cwd"
    cwd.mkdir()
    monkeypatch.chdir(cwd)
    monkeypatch.setattr(backup, "SOURCE", src)
    monkeypatch.setattr(backup, "VAULT", Path("faux_vault") / "game_ref")

    assert backup.main([]) == 2
    assert "REFUSING TO MIRROR" in capsys.readouterr().out
    assert list(cwd.iterdir()) == [], "the mirror created a vault underfoot"
