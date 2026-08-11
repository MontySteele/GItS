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
        return [SimpleNamespace(node_kinds=[], hp_by_node=[], n_acts=1,
                                events=[], deck_ids=[],
                                # P2 telemetry: the runner reads this off
                                # every result, so the stand-in has to carry
                                # it. Left strict on the runner side on
                                # purpose -- a getattr default there would
                                # swallow a real RunResult regression.
                                kurage_traces=[],
                                # C4 (addendum): same rule -- the
                                # runner reads this off every result
                                # strictly, so a stand-in must carry
                                # it or the aggregate is silently
                                # empty instead of loudly wrong.
                                overlap_traces=[], won=False,
                                # C2 (addendum): the elite columns
                                # walk these three off every result,
                                # strictly, for the same reason.
                                fight_stats=[], relics_by_act=[])]

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
        "n_acts": None,                 # §10.1: default spans RUN_ACTS
        "jobs": 1,                      # serial unless --jobs asks
        "route_name": "hunter",         # §11: elite-seeking is the default
        "force_cards": None,            # EB-17p: the CLI never forces a card
    }
    assert "realistic (relics + potions)" in capsys.readouterr().out


def test_bare_runner_preserves_historical_defaults(monkeypatch):
    called = {}

    def fake_run_many(*args, **kwargs):
        called["args"] = args
        called["kwargs"] = kwargs
        return [SimpleNamespace(node_kinds=[], hp_by_node=[], n_acts=1,
                                events=[], deck_ids=[],
                                # P2 telemetry: the runner reads this off
                                # every result, so the stand-in has to carry
                                # it. Left strict on the runner side on
                                # purpose -- a getattr default there would
                                # swallow a real RunResult regression.
                                kurage_traces=[],
                                # C4 (addendum): same rule -- the
                                # runner reads this off every result
                                # strictly, so a stand-in must carry
                                # it or the aggregate is silently
                                # empty instead of loudly wrong.
                                overlap_traces=[], won=False,
                                # C2 (addendum): the elite columns
                                # walk these three off every result,
                                # strictly, for the same reason.
                                fight_stats=[], relics_by_act=[])]

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
        "n_acts": None,                 # §10.1: default spans RUN_ACTS
        "jobs": 1,                      # serial unless --jobs asks
        "route_name": "hunter",         # §11: elite-seeking is the default
        "force_cards": None,            # EB-17p: the CLI never forces a card
    }


def test_furina_rejects_klee_only_adaptive_ab():
    with pytest.raises(SystemExit):
        runner.main(["--character", "furina", "--ab"])


# --- EB-20w: the Encore census on the run report ---

def test_encore_census_pools_fight_stats_and_delegates(monkeypatch):
    """run_metrics.encore_census is a POOLING call, not a second definition:
    every fight record, in run order, goes to the one fight-side profile."""
    seen = {}
    def fake_profile(stats):
        seen["stats"] = stats
        return {"marker": True}

    monkeypatch.setattr(runner.run_metrics.t0_metrics,
                        "encore_census_profile", fake_profile)
    a, b, c = object(), object(), object()
    results = [SimpleNamespace(fight_stats=[a, b]),
               SimpleNamespace(fight_stats=[]),
               SimpleNamespace(fight_stats=[c])]
    assert runner.run_metrics.encore_census(results) == {"marker": True}
    assert seen["stats"] == [a, b, c]


def test_run_report_wires_the_encore_census(monkeypatch):
    """The default report reaches print_encore_census (no flag to remember --
    the C4 rule); the printer's own empty-profile silence is what keeps it
    off non-Encore rosters, and that half is pinned in
    tier0/tests/test_eb20_encore_census.py."""
    seen = {}

    def fake_run_many(*args, **kwargs):
        return [SimpleNamespace(node_kinds=[], hp_by_node=[], n_acts=1,
                                events=[], deck_ids=[], kurage_traces=[],
                                overlap_traces=[], won=False,
                                fight_stats=[], relics_by_act=[])]

    monkeypatch.setattr(runner.model, "run_many", fake_run_many)
    monkeypatch.setattr(runner.run_metrics, "summarize_runs", lambda _: {})
    monkeypatch.setattr(runner.run_metrics, "survival_profile",
                        lambda _results, _max_hp: {})
    monkeypatch.setattr(runner.run_metrics, "print_run_report",
                        lambda *_args, **_kwargs: None)
    monkeypatch.setattr(runner.t0_report, "print_encore_census",
                        lambda label, census: seen.update(
                            label=label, census=census))

    assert runner.main(["--runs", "1"]) == 0
    assert seen["label"] == "run cohort"
    assert seen["census"] == {}         # no Encore in the stand-in cohort
