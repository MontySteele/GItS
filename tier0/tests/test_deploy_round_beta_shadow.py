"""The beta shadow (2026-10-20): `tools/deploy_round.py` warns when the
subscribed `klee-beta` Workshop copy will load instead of the dev deploy.

[USER] played beta 0.3.9 believing it was dev 0.2.6094: the game sorts the
Workshop item ahead of `mods\\klee`, both assemblies are named `klee`, and
the second fails with "Assembly with same name is already loaded". Fake
directories only; nothing here reads the real Steam or %APPDATA% tree.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _deploy():
    path = REPO / "tools" / "deploy_round.py"
    spec = importlib.util.spec_from_file_location("_beta_deploy_round", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _steam(tmp_path: Path, beta: bool = True) -> Path:
    """A fake `<steamapps>` with the game and, optionally, the beta item."""
    steamapps = tmp_path / "steamapps"
    game = steamapps / "common" / "Slay the Spire 2"
    (game / "mods" / "klee").mkdir(parents=True)
    content = steamapps / "workshop" / "content" / "2868840"
    other = content / "3737335127" / "BaseLib"
    other.mkdir(parents=True)
    (other / "manifest.json").write_text(json.dumps({"id": "BaseLib"}),
                                         encoding="utf-8")
    if beta:
        item = content / "3821050238" / "klee-beta"
        item.mkdir(parents=True)
        (item / "manifest.json").write_text(
            json.dumps({"id": "klee-beta", "version": "0.3.9"}),
            encoding="utf-8")
    return game


def _settings(tmp_path: Path, rows, mods_enabled: bool = True) -> Path:
    appdata = tmp_path / "appdata"
    save = appdata / "SlayTheSpire2" / "steam" / "765" / "settings.save"
    save.parent.mkdir(parents=True)
    save.write_text(json.dumps({"mod_settings": {
        "mod_list": rows, "mods_enabled": mods_enabled}}), encoding="utf-8")
    return appdata


BETA_ON = [{"id": "klee-beta", "is_enabled": True, "source": "steam_workshop"},
           {"id": "klee", "is_enabled": True, "source": "mods_directory"}]
BETA_OFF = [{"id": "klee-beta", "is_enabled": False,
             "source": "steam_workshop"},
            {"id": "klee", "is_enabled": True, "source": "mods_directory"}]


def test_the_content_dir_is_found_from_the_game_dir(tmp_path):
    d = _deploy()
    game = _steam(tmp_path)
    assert d.workshop_content_dir(game) == (
        tmp_path / "steamapps" / "workshop" / "content" / "2868840")
    found = d.beta_manifests(d.workshop_content_dir(game))
    assert [p.parent.name for p in found] == ["klee-beta"]


def test_an_enabled_beta_warns_loudly_and_names_the_fix(tmp_path):
    d = _deploy()
    game = _steam(tmp_path)
    line, warning = d.beta_shadow(game, _settings(tmp_path, BETA_ON))
    assert line.startswith("workshop beta:") and "SHADOWS" in line
    assert warning.startswith("WARNING")
    assert "WILL NOT LOAD" in warning
    assert "Teyvat Spire (Beta)" in warning


def test_a_disabled_beta_is_a_quiet_line(tmp_path):
    d = _deploy()
    game = _steam(tmp_path)
    line, warning = d.beta_shadow(game, _settings(tmp_path, BETA_OFF))
    assert warning is None
    assert "disabled in settings" in line


def test_mods_off_altogether_counts_as_disabled(tmp_path):
    d = _deploy()
    game = _steam(tmp_path)
    _, warning = d.beta_shadow(
        game, _settings(tmp_path, BETA_ON, mods_enabled=False))
    assert warning is None


def test_an_unlisted_beta_is_treated_as_enabled(tmp_path):
    # The game turns a newly found mod on, so "not listed yet" is not "off".
    d = _deploy()
    game = _steam(tmp_path)
    _, warning = d.beta_shadow(
        game, _settings(tmp_path, [{"id": "klee", "is_enabled": True}]))
    assert warning is not None


def test_no_readable_settings_still_warns(tmp_path):
    d = _deploy()
    game = _steam(tmp_path)
    line, warning = d.beta_shadow(game, tmp_path / "no-appdata")
    assert warning is not None and "no readable settings.save" in line


def test_no_beta_item_is_no_warning(tmp_path):
    d = _deploy()
    game = _steam(tmp_path, beta=False)
    line, warning = d.beta_shadow(game, _settings(tmp_path, BETA_ON))
    assert warning is None and "not subscribed" in line


def test_the_settings_are_read_never_written(tmp_path):
    d = _deploy()
    game = _steam(tmp_path)
    appdata = _settings(tmp_path, BETA_ON)
    save = next(appdata.rglob("settings.save"))
    before = save.read_bytes()
    d.beta_shadow(game, appdata)
    assert save.read_bytes() == before


LOG = """\
[INFO] Loading assembly DLL C:\\Steam\\steamapps\\workshop\\content\\2868840\\3821050238\\klee-beta\\klee-beta.dll
[INFO] Calling initializer method of type KleeMod.KleeMod for klee, Version=0.3.9.0, Culture=neutral, PublicKeyToken=null
[INFO] Loading assembly DLL C:\\Steam\\steamapps\\common\\Slay the Spire 2\\mods\\klee\\klee.dll
[ERROR] Exception thrown while loading mod klee: System.IO.FileLoadException: Could not load file or assembly 'klee, Version=0.2.6094.0, Culture=neutral, PublicKeyToken=null'. Assembly with same name is already loaded
"""


def test_the_log_report_names_what_loaded_and_the_clash():
    d = _deploy()
    lines = d.klee_load_report(LOG)
    text = "\n".join(lines)
    assert "klee-beta.dll" in text and "mods\\klee\\klee.dll" in text
    assert "klee loaded:       version 0.3.9.0" in lines
    assert any(l.startswith("ERROR:") and "0.2.6094.0" in l for l in lines)


def test_a_clean_log_reports_no_clash():
    d = _deploy()
    clean = "\n".join(LOG.splitlines()[2:3]) + (
        "\n[INFO] Calling initializer method of type KleeMod.KleeMod for "
        "klee, Version=0.2.6094.0, Culture=neutral\n")
    lines = d.klee_load_report(clean)
    assert "klee loaded:       version 0.2.6094.0" in lines
    assert "already-loaded:    none" in lines


def test_log_flag_reads_the_fake_appdata(tmp_path, capsys):
    d = _deploy()
    logs = tmp_path / "SlayTheSpire2" / "logs"
    logs.mkdir(parents=True)
    (logs / "godot.log").write_text(LOG, encoding="utf-8")
    assert d.log_report(tmp_path) == 0
    out = capsys.readouterr().out
    assert "already loaded" in out and "0.3.9.0" in out
    assert d.log_report(tmp_path / "nowhere") == 0
    assert "no godot.log" in capsys.readouterr().out
