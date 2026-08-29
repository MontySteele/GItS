"""The pinned-assembly backup's refusals and its tripwire, exercised hermetically.

WHY THIS TEST IS THE POINT OF THE TOOL (EB-172 / R218 C).
`tools/backup_game_assemblies.py` copies the four assemblies the repo compiles
against — `sts2.dll`, `0Harmony.dll`, `GodotSharp.dll`, `BaseLib.dll` — into
the OneDrive vault, so that a Steam update can stop a live RUN but never the
BUILD. Its two claims are both refusals, and a refusal nothing proves is a
comment:

  * a PARTIAL set is refused (exit 2). Three of four assemblies is not a
    buildable pin, and a mirror that copied what it found would leave a vault
    that looks like a backup and is not. This is the difference from
    `backup_game_ref`, whose source is a tree with a file-count floor.
  * off Windows the hard-coded vault string is a RELATIVE path, so mirroring
    would build a faux `C:\\Users\\...` directory under the working directory
    and report success. Same hazard, same guard, same reasoning as its sibling.

And `tools/lint_game_assemblies_backup.py` must fail on a vault that disagrees
with its own `PIN.json` and must NOT fail merely because the live game has
moved off the pin — that second case is the exact situation the vault exists
for, and a tripwire that screams then is one the reader learns to silence.

HERMETIC, AND THAT WORD IS LOAD-BEARING HERE. Every path below is a pytest
`tmp_path`, and `VAULT` is monkeypatched on every test that writes. No test
can reach the real vault, and none reads the real Steam install (absent on the
CI runner by construction). A test for a tool that writes outside the repo
would be worse than no test if it could itself write outside the repo.

HERMETIC ACROSS PLATFORMS, a separate claim. CI is Ubuntu and `pathlib.Path`
binds to the running platform, so no assertion here reads `VAULT.parts`; the
platform tests drive `sys.platform` themselves and assert the same thing on
both hosts.

FAST LANE. Deliberately unmarked, like its sibling: tiny temp files, and the
guard is what you want checked before pushing a change to the tool.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from tools import backup_game_assemblies as backup


def _fake_install(tmp_path, *, names=backup.ASSEMBLIES,
                  version="v0.111.0", baselib="v3.4.5"):
    """A minimal install tree: a data dir, a Workshop dir, and their metadata.

    Returns (data_dir, baselib_dll). `names` selects which assemblies exist,
    which is how the partial-set refusal is driven.
    """
    data = tmp_path / "game" / "data_sts2_windows_x86_64"
    data.mkdir(parents=True)
    wsp = tmp_path / "workshop" / "BaseLib"
    wsp.mkdir(parents=True)
    for n in backup.GAME_ASSEMBLIES:
        if n in names:
            (data / n).write_bytes(n.encode() * 8)
    baselib_dll = wsp / backup.BASELIB_ASSEMBLY
    if backup.BASELIB_ASSEMBLY in names:
        baselib_dll.write_bytes(b"baselib-bytes")
    (data.parent / "release_info.json").write_text(
        json.dumps({"version": version, "commit": "41cef1ea",
                    "date": "2026-08-13", "main_assembly_hash": 222455745}),
        encoding="utf-8")
    (wsp / "BaseLib.json").write_text(
        json.dumps({"id": "BaseLib", "version": baselib}), encoding="utf-8")
    return data, baselib_dll


# --- the guard, on its own -------------------------------------------------

def test_guard_passes_on_the_complete_set(tmp_path):
    data, baselib = _fake_install(tmp_path)
    assert backup.guard(backup.sources(data, baselib)) is None


def test_guard_refuses_a_partial_set_and_names_what_is_missing(tmp_path):
    """The whole difference from `backup_game_ref`: no floor, an exact set."""
    names = tuple(n for n in backup.ASSEMBLIES if n != "GodotSharp.dll")
    data, baselib = _fake_install(tmp_path, names=names)
    refusal = backup.guard(backup.sources(data, baselib))
    assert refusal is not None
    assert "GodotSharp.dll" in refusal


def test_guard_refuses_when_local_props_resolved_nothing():
    """`local.props` missing or unparsed yields Nones, and a mirror that ran
    on that would copy an empty set and write a PIN for it."""
    refusal = backup.guard(backup.sources(None, None))
    assert refusal is not None
    for name in backup.ASSEMBLIES:
        assert name in refusal


# --- the platform refusal --------------------------------------------------

def test_the_configured_vault_is_refused_off_windows(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    assert backup.platform_refusal(Path(backup.VAULT_SPEC)) is not None


def test_a_relative_vault_is_refused_on_any_host(tmp_path, monkeypatch):
    monkeypatch.setattr(sys, "platform", "win32")
    assert backup.platform_refusal(Path("vault")) is not None
    assert backup.platform_refusal(tmp_path) is None


def test_the_vault_sits_beside_game_ref_in_the_ruled_location():
    """RULED [USER] 2026-08-24 -- one vault, and backups never live in a
    worktree. Asked of VAULT_WINDOWS, which parses as Windows on every host."""
    parts = backup.VAULT_WINDOWS.parts
    assert "OneDrive" in parts and "GItS-vault" in parts
    assert backup.VAULT_WINDOWS.name == "game_assemblies"
    assert backup.VAULT_WINDOWS.parent.name == "GItS-vault"


# --- the mirror and its PIN ------------------------------------------------

def test_the_mirror_writes_all_four_and_a_pin_that_identifies_them(tmp_path):
    data, baselib = _fake_install(tmp_path)
    src = backup.sources(data, baselib)
    vault = tmp_path / "vault"
    pin = backup.build_pin(src, data, baselib)
    written, unchanged = backup.mirror(src, vault, pin)

    assert written == sorted(backup.ASSEMBLIES) and unchanged == []
    for name in backup.ASSEMBLIES:
        assert (vault / name).read_bytes() == src[name].read_bytes()

    on_disk = json.loads((vault / backup.PIN_FILE).read_text(encoding="utf-8"))
    assert on_disk["game_version"] == "v0.111.0"
    assert on_disk["game_commit"] == "41cef1ea"
    assert on_disk["baselib_version"] == "v3.4.5"
    assert set(on_disk["files"]) == set(backup.ASSEMBLIES)


def test_a_second_run_rewrites_nothing(tmp_path):
    data, baselib = _fake_install(tmp_path)
    src = backup.sources(data, baselib)
    vault = tmp_path / "vault"
    backup.mirror(src, vault, backup.build_pin(src, data, baselib))
    written, unchanged = backup.mirror(
        src, vault, backup.build_pin(src, data, baselib))
    assert written == [] and unchanged == sorted(backup.ASSEMBLIES)


def test_a_dry_run_writes_nothing_at_all(tmp_path):
    data, baselib = _fake_install(tmp_path)
    src = backup.sources(data, baselib)
    vault = tmp_path / "vault"
    written, _ = backup.mirror(
        src, vault, backup.build_pin(src, data, baselib), dry_run=True)
    assert written == sorted(backup.ASSEMBLIES)
    assert not vault.exists()


def test_the_mirror_never_deletes_a_prior_generation(tmp_path):
    """`game_ref`'s mirror prunes because its source is the authority. Here the
    VAULT is the authority for a build the live install no longer has, so an
    older file is data, not litter."""
    data, baselib = _fake_install(tmp_path)
    src = backup.sources(data, baselib)
    vault = tmp_path / "vault"
    vault.mkdir()
    stale = vault / "sts2-0.107.1.dll"
    stale.write_bytes(b"an older generation")
    backup.mirror(src, vault, backup.build_pin(src, data, baselib))
    assert stale.exists()


# --- the tripwire ----------------------------------------------------------

def _lint(monkeypatch, vault, data_dir):
    import tools.lint_game_assemblies_backup as lint
    monkeypatch.setattr(lint, "VAULT", vault)
    monkeypatch.setattr(lint, "local_props_paths", lambda: (data_dir, None))
    return lint.main()


def test_the_lint_notes_and_passes_when_there_is_no_vault(tmp_path,
                                                          monkeypatch):
    """A fresh clone, a CI runner and every worktree have no vault. A lint that
    failed there is one everybody learns to ignore."""
    assert _lint(monkeypatch, tmp_path / "absent", None) == 0


def test_the_lint_passes_a_complete_current_vault(tmp_path, monkeypatch):
    data, baselib = _fake_install(tmp_path)
    src = backup.sources(data, baselib)
    vault = tmp_path / "vault"
    backup.mirror(src, vault, backup.build_pin(src, data, baselib))
    assert _lint(monkeypatch, vault, data) == 0


def test_the_lint_fails_a_vault_with_no_pin(tmp_path, monkeypatch):
    vault = tmp_path / "vault"
    vault.mkdir()
    for name in backup.ASSEMBLIES:
        (vault / name).write_bytes(b"x")
    assert _lint(monkeypatch, vault, None) == 1


def test_the_lint_fails_a_missing_assembly(tmp_path, monkeypatch):
    data, baselib = _fake_install(tmp_path)
    src = backup.sources(data, baselib)
    vault = tmp_path / "vault"
    backup.mirror(src, vault, backup.build_pin(src, data, baselib))
    (vault / "GodotSharp.dll").unlink()
    assert _lint(monkeypatch, vault, data) == 1


def test_the_lint_fails_bytes_that_no_longer_match_the_pin(tmp_path,
                                                           monkeypatch):
    data, baselib = _fake_install(tmp_path)
    src = backup.sources(data, baselib)
    vault = tmp_path / "vault"
    backup.mirror(src, vault, backup.build_pin(src, data, baselib))
    (vault / "sts2.dll").write_bytes(b"tampered but the same length!!!!")
    assert _lint(monkeypatch, vault, data) == 1


def test_a_live_game_that_has_moved_off_the_pin_is_a_NOTE_not_a_failure(
        tmp_path, monkeypatch, capsys):
    """The moment the vault's value is highest is not the moment to fail the
    build. Re-pinning is a decision (a ruling moves STATE.md's pin block)."""
    data, baselib = _fake_install(tmp_path)
    src = backup.sources(data, baselib)
    vault = tmp_path / "vault"
    backup.mirror(src, vault, backup.build_pin(src, data, baselib))
    (data.parent / "release_info.json").write_text(
        json.dumps({"version": "v0.112.0"}), encoding="utf-8")
    assert _lint(monkeypatch, vault, data) == 0
    out = capsys.readouterr().out
    assert "v0.112.0" in out and "v0.111.0" in out
    assert "NOT a defect" in out
