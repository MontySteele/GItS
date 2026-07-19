"""Combat loop + determinism (spec M1: same seed = identical log)."""

from tier0.content import loader
from tier0.engine.combat import run_fight
from tier0.harness import metrics
from tier0.harness.runner import run_battery
from tier0.pilot.policy import make_pilot


def _run(seed):
    player = loader.build_player("ref_ironclad", "starter")
    enemies = loader.build_encounter("punisher")
    pilot = make_pilot(loader.pilot_weights("generic"))
    return run_fight(player, enemies, pilot, seed=seed)


def test_fight_terminates_and_logs_end():
    state = _run(seed=1)
    assert state.log[-1]["event"] == "fight_end"
    assert state.over or state.log[-1]["turns"] >= 1


def test_determinism_same_seed_identical_log():
    log_a = _run(seed=12345).log
    log_b = _run(seed=12345).log
    assert log_a == log_b


def test_different_seeds_diverge():
    # Not logically guaranteed, but over a full fight the shuffle order
    # essentially always differs; a failure here means rng isn't wired in.
    logs = {tuple((e["event"], e.get("card")) for e in _run(seed=s).log)
            for s in range(5)}
    assert len(logs) > 1


def test_starter_vs_punisher_is_competitive():
    # Behavioral sanity, wide bounds (calibration happens in M2): the
    # starter deck should sometimes win and sometimes lose vs PUNISHER.
    stats = run_battery("ref_ironclad", "starter", "punisher", "generic",
                        fights=200, seed=7)
    s = metrics.summarize(stats)
    assert 0.05 < s["winrate"] < 0.95, s


def test_package_deck_beats_starter():
    base = metrics.summarize(run_battery("ref_ironclad", "starter",
                                         "punisher", "generic", 200, 7))
    pkg = metrics.summarize(run_battery("ref_ironclad", "archetype_package",
                                        "punisher", "generic", 200, 7))
    assert pkg["winrate"] > base["winrate"]


def test_no_degeneracy_flags_on_reference_deck():
    stats = run_battery("ref_ironclad", "starter", "punisher", "generic",
                        fights=100, seed=3)
    assert metrics.summarize(stats)["flags"] == []
