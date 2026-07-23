"""Character-aware Tier 0.5 CLI routing.

The engine could already execute Furina runs through bespoke experiment
scripts. These tests lock the ordinary runner surface so it cannot silently
route a Furina plan through a Klee pilot, or label a bare run as realistic.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from tier05 import runner


def test_furina_plan_defaults_and_explicit_routes():
    assert runner.resolve_plan("furina", None) == ("salon", "salon")
    assert runner.resolve_plan("furina", "spotlight") == (
        "spotlight", "spotlight")
    assert runner.resolve_plan("furina", "fanfare") == (
        "fanfare", "fanfare")


def test_character_plan_cross_wiring_fails_loudly():
    with pytest.raises(ValueError, match="no archetype 'demolition'"):
        runner.resolve_plan("furina", "demolition")
    with pytest.raises(ValueError, match="no archetype 'spotlight'"):
        runner.resolve_plan("klee", "spotlight")


def test_realistic_runner_enables_both_run_layers(monkeypatch, capsys):
    called = {}

    def fake_run_many(*args, **kwargs):
        called["args"] = args
        called["kwargs"] = kwargs
        return [SimpleNamespace(node_kinds=[], hp_by_node=[])]

    monkeypatch.setattr(runner.model, "run_many", fake_run_many)
    monkeypatch.setattr(runner.run_metrics, "summarize_runs", lambda _: {})
    monkeypatch.setattr(runner.run_metrics, "survival_profile",
                        lambda _results, _max_hp: {})
    monkeypatch.setattr(runner.run_metrics, "print_run_report",
                        lambda *_args, **_kwargs: None)

    assert runner.main([
        "--character", "furina",
        "--archetype", "spotlight",
        "--runs", "1",
        "--realistic",
    ]) == 0

    assert called["args"][:3] == ("furina", "spotlight", "spotlight")
    assert called["kwargs"] == {
        "grant_relics": True,
        "grant_potions": True,
    }
    assert "realistic (relics + potions)" in capsys.readouterr().out


def test_bare_runner_preserves_historical_defaults(monkeypatch):
    called = {}

    def fake_run_many(*args, **kwargs):
        called["args"] = args
        called["kwargs"] = kwargs
        return [SimpleNamespace(node_kinds=[], hp_by_node=[])]

    monkeypatch.setattr(runner.model, "run_many", fake_run_many)
    monkeypatch.setattr(runner.run_metrics, "summarize_runs", lambda _: {})
    monkeypatch.setattr(runner.run_metrics, "survival_profile",
                        lambda _results, _max_hp: {})
    monkeypatch.setattr(runner.run_metrics, "print_run_report",
                        lambda *_args, **_kwargs: None)

    assert runner.main(["--runs", "1"]) == 0
    assert called["args"][:3] == ("klee", "demolition", "demolition")
    assert called["kwargs"] == {
        "grant_relics": False,
        "grant_potions": False,
    }


def test_furina_rejects_klee_only_adaptive_ab():
    with pytest.raises(SystemExit):
        runner.main(["--character", "furina", "--ab"])
