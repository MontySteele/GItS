"""Regression tests for the local base-game extraction plumbing.

These tests use tiny synthetic source trees. They never read or reproduce
base-game data, and they do not require ilspycmd or a game installation.
"""

from pathlib import Path
from types import SimpleNamespace

import pytest

from tools import build_ironclad_sheet as build
from tools import extract_base_game_pool as extract


def _write_type(root: Path, relative: str, namespace: str, body: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"namespace {namespace};\n\n{body}\n")
    return path


def test_game_dll_finds_macos_app_layout(tmp_path, monkeypatch):
    install = tmp_path / "Slay the Spire 2"
    dll = (install / "SlayTheSpire2.app" / "Contents" / "Resources"
           / "data_sts2_macos_arm64" / "sts2.dll")
    dll.parent.mkdir(parents=True)
    dll.touch()
    props = tmp_path / "local.props"
    props.write_text(
        f"<Project><PropertyGroup><GameDir>{install}</GameDir>"
        "</PropertyGroup></Project>"
    )
    monkeypatch.setattr(extract, "LOCAL_PROPS", props)

    assert extract.game_dll() == dll


def test_project_mode_passes_reference_path_and_runs_once(
        tmp_path, monkeypatch):
    dll = tmp_path / "data_sts2_macos_arm64" / "sts2.dll"
    dll.parent.mkdir()
    dll.touch()
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(extract.subprocess, "run", fake_run)
    extract._run_ilspy_project(dll, tmp_path / "out")

    assert len(calls) == 1
    command, kwargs = calls[0]
    assert command[command.index("-r") + 1] == str(dll.parent)
    assert "--project" in command
    assert "--nested-directories" in command
    assert kwargs["timeout"] == 300


def test_decompile_character_reads_pool_and_cards_from_one_project(
        tmp_path, monkeypatch):
    dll = tmp_path / "sts2.dll"
    dll.touch()
    calls = []

    def fake_project(_dll, root):
        calls.append(_dll)
        _write_type(
            root, "pool/IroncladCardPool.cs",
            "MegaCrit.Sts2.Core.Models.CardPools",
            "class IroncladCardPool { object Cards => "
            "ModelDb.Card<Bash>(); }",
        )
        _write_type(
            root, "cards/Bash.cs", "MegaCrit.Sts2.Core.Models.Cards",
            "class Bash { }",
        )
        # A same-named type in another namespace must not be selected.
        _write_type(root, "other/Bash.cs", "Example.Other", "class Bash { }")

    monkeypatch.setattr(extract, "_run_ilspy_project", fake_project)

    names, sources = extract.decompile_character(dll, "Ironclad")

    assert calls == [dll]
    assert names == ["Bash"]
    assert "MegaCrit.Sts2.Core.Models.Cards" in sources["Bash"]
    assert "Example.Other" not in sources["Bash"]


def test_emitted_upgrade_delta_supports_energy_and_hit_count():
    assert extract._delta_key({"op": "energy"}, "amount") == "energy"
    assert extract._delta_key({"op": "damage"}, "times") == "times"


def test_supplement_upgrade_uses_row_shape_not_card_identity():
    row = {"effects": [
        {"op": "conditional", "then": [
            {"op": "gain_max_hp", "amount": 2},
        ]},
        {"op": "upgrade_in_hand", "scope": "chosen"},
        {"op": "exhaust_from", "amount": 1},
    ]}
    source = """
class SyntheticCard
{
    bool Preview => base.IsUpgraded;

    void OnUpgrade()
    {
        base.DynamicVars.MaxHp.UpgradeValueBy(1m);
    }
}
"""

    assert extract._supplement_upgrade_delta(row, source) == {
        "max_hp": 1,
        "upgrade_scope": "all",
        "exhaust_select": "chosen",
    }


def test_builder_rejects_partial_upgrade_coverage(tmp_path, monkeypatch):
    upgrades = tmp_path / "upgrades.yaml"
    upgrades.write_text("one: {damage: 1}\n")
    monkeypatch.setattr(build, "UPGRADES", upgrades)

    with pytest.raises(SystemExit, match="missing upgrades for.*two"):
        build._validated_upgrades([{"id": "one"}, {"id": "two"}])
