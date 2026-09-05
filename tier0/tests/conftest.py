import os
import random
from pathlib import Path

import pytest

from tier0.engine.state import CombatState, Enemy, Player

# --- THE GIT ENVIRONMENT IS SCRUBBED BEFORE ANY TEST RUNS ------------------
# WHAT HAPPENED, 2026-09-02. Five files in this directory build throwaway git
# repositories under `tmp_path` -- `test_rulings_index.py`'s ruling-history
# fixture, `test_purge_worktree_guard.py`, `test_register_ids_lint.py`'s merge
# cases, `test_agent_rituals.py`, `test_understudy_seat.py`. Every one of them
# passes `cwd=<the temp repo>` and none of them passes `env`, which is correct
# right up until the process they inherit carries `GIT_DIR`.
#
# `GIT_DIR` OUTRANKS `cwd`, ABSOLUTELY. With it set, `git commit` in a temp
# directory commits INTO THE REPOSITORY IT NAMES. The push gate
# (`tools/hooks/push_gate.py`) runs the fast lane as a child of the harness,
# and that environment carried a `GIT_DIR` pointing at the session's own
# worktree: sixteen xdist workers each ran the rulings fixture's seven
# commits, twenty-eight tests failed on `index.lock` contention, and the ones
# that won the lock left the branch sitting on `R16 landed: the sixteenth
# ruling, as ruled` with an empty index. Nothing was lost -- the reflog had
# it, and a mixed reset put it back -- but the suite had rewritten the
# developer's branch, and nothing in the tree could have stopped it.
#
# Deleted at conftest IMPORT time rather than in an autouse fixture: a fixture
# runs after collection, and collection already imports modules that shell out.
# Nothing in this suite legitimately reads any of these -- every git command in
# every test names its repository by `cwd` or by an explicit path -- so the
# correct value in this process is "absent".
for _leaked in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE",
                "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                "GIT_COMMON_DIR", "GIT_NAMESPACE", "GIT_CEILING_DIRECTORIES"):
    os.environ.pop(_leaked, None)


# `EB-496`. THE FIGHT'S MEMORY IS ON DISK NOW, so it leaks between test FILES
# and between xdist workers, not merely between tests in one module. The
# blind-play module has carried its own `forget_fight` fixture since `EB-428`;
# this is the same rule for every other file that renders a page, and it has to
# be here because the store is one file per lane and the suite runs on lane 0.
#
# IMPORTED INSIDE THE FIXTURE. This conftest is imported during collection, and
# a top-level `understudy` import here would put the whole blind-play package
# in front of every test in the tier0 suite -- including the fences that assert
# what may import what.
#
# AND THE STORE IS MOVED, NOT ONLY EMPTIED. The suite runs under xdist and the
# path is one file per LANE, so sixteen workers on lane 0 share one file: the
# tests that drive the memory across a process boundary went red in the full
# run and green alone, which is a shared-file race and not a flake. Each worker
# gets its own directory (`getbasetemp` is already per worker), and the real
# one under `understudy/logs` is never touched by a test.
@pytest.fixture(autouse=True)
def _fresh_blindplay_fight(tmp_path_factory):
    from understudy import blindplay_faces as faces
    store = tmp_path_factory.getbasetemp() / "blindplay-fight"
    store.mkdir(parents=True, exist_ok=True)
    held, faces._FIGHT_STORE_DIR = faces._FIGHT_STORE_DIR, store
    faces.forget_fight()
    yield
    faces.forget_fight()
    faces._FIGHT_STORE_DIR = held


# `EB-401`. THE DECK'S MEMORY IS THE SAME HAZARD, and it is the one the
# push-gate flake was actually about (fixer I's cause read).
#
# `_blindplay-deck-lane0.json` is one file per LANE, under `understudy/logs`,
# and the whole suite runs on lane 0 -- so sixteen xdist workers share it. The
# tests that drive the deck across a process boundary passed alone and failed
# intermittently under `-n`: `test_the_map_prints_the_gold_and_the_deck` is the
# one that showed it, reading a deck another worker had just forgotten or just
# written. That is a shared-file race and not a flake.
#
# THE FIGHT STORE'S FIXTURE, VERBATIM, one store over: each worker gets its own
# directory (`getbasetemp` is already per worker), the store is MOVED rather
# than only emptied, and the real one under `understudy/logs` is never touched
# by a test. The in-process cache is cleared at both ends by `forget_deck`, so
# a test that never writes cannot inherit a neighbour's row either.
#
# IMPORTED INSIDE THE FIXTURE, for the reason the fixture above states: a
# top-level `understudy` import in this conftest would put the whole blind-play
# package in front of every test in the tier0 suite, including the fences that
# assert what may import what.
@pytest.fixture(autouse=True)
def _fresh_blindplay_deck(tmp_path_factory):
    from understudy import blindplay_faces as faces
    store = tmp_path_factory.getbasetemp() / "blindplay-deck"
    store.mkdir(parents=True, exist_ok=True)
    held, faces._DECK_STORE_DIR = faces._DECK_STORE_DIR, store
    faces.forget_deck()
    yield
    faces.forget_deck()
    faces._DECK_STORE_DIR = held


# --- THE ARMS ARE OFF AT EVERY TEST'S START, AND IT NAMES WHO LEFT ONE ON ---
# `EB-569`. Two tests -- `test_the_overhaul_ids_do_not_resolve_with_the_flag_off`
# and `test_no_prototype_row_is_upgradable_with_the_flags_off` -- assert the
# quarantine's own door is shut, and both passed alone and failed about one run
# in three under `-n auto`. Each failure was a NEIGHBOUR's residue: an arm test
# on the same xdist worker had left something behind, and the two tests that
# read the flag-off tree saw it.
#
# TWO LEAKERS, ONE AFTER THE OTHER. The first was the memoized upgrade indices
# (cleared in the `overhaul` fixture, 2026-09-05). The second was
# `loader._substituted_card_index`, which is built from `_starter_ids` and
# `_pool_substitutions` -- both READ THE FLAGS -- and which no fixture and
# neither test cleared: warmed once under `KLEE_OVERHAUL` it holds
# `proto_ko_jumpy_dumpty` and `proto_ko_kapow` for the rest of the worker's
# life, after which `get_card("proto_ko_kapow")` stops raising. Both are now
# behind `loader.reset_arm_caches()`, one list beside the flags it depends on.
#
# THIS FIXTURE IS THE THIRD ONE'S FUTURE. A leak of this shape is a fact about
# the PREVIOUS test, and pytest reports it against the next one, which is why
# it took two rounds to find. So the invariant is asserted at every test's
# START and the failure NAMES THE TEST THAT RAN BEFORE IT on this worker.
#
# WHAT IS CHECKED, and what each check costs:
#
#   * every arm flag is off -- five attribute reads and one module read;
#   * `_substituted_card_index` is EMPTY, which is the arms' own promise about
#     a flag-off tree ("It is empty on every flag-off tree, which is every
#     shipped tree") -- one memoized call, free;
#   * `_prototype_upgrade_index` is empty, and ONLY IF IT IS ALREADY WARM.
#     Building it walks the whole prototype surface (~100ms), so asking a cold
#     one would put that on every test in the suite; a cold cache has leaked
#     nothing by construction.
#
# AND IT REPAIRS BEFORE IT FAILS, so one leaker costs one red test and not a
# cascade of them: the flags go back off and the caches are dropped, then the
# assertion fires.
_ARM_FLAGS = ("SPARK_ALT_COST_ENABLED", "KLEE_OVERHAUL", "KOKOMI_OVERHAUL",
              "COMPANION_OVERHAUL", "KURAGE_MEMORY")

#: The last test to FINISH on this worker -- the one a leak found at the next
#: test's start belongs to. Per-process, which is per-worker under xdist.
_previous_test = {"id": "(nothing -- this was the first test on this worker)"}


def _arm_residue():
    """Everything about the world that says an arm is still on. Empty is good."""
    from tier0 import constants as C
    from tier0.content import loader, upgrades
    from tier0.engine import furina_reframe

    found = []
    for flag in _ARM_FLAGS:
        if getattr(C, flag):
            found.append(f"tier0.constants.{flag} is still True")
    if furina_reframe.FURINA_REFRAME:
        found.append("furina_reframe.FURINA_REFRAME is still True")
    warm = sorted(loader._substituted_card_index())
    if warm:
        found.append("loader._substituted_card_index still holds "
                     f"{warm} -- it is empty on a flag-off tree")
    if upgrades._prototype_upgrade_index.cache_info().currsize:
        rows = sorted(upgrades._prototype_upgrade_index())
        if rows:
            found.append("upgrades._prototype_upgrade_index still holds "
                         f"{rows} -- it is empty on a flag-off tree")
    return found


@pytest.fixture(autouse=True)
def _the_arms_stay_quarantined(request):
    from tier0 import constants as C
    from tier0.content import loader
    from tier0.engine import furina_reframe

    residue = _arm_residue()
    if residue:
        for flag in _ARM_FLAGS:
            setattr(C, flag, False)
        furina_reframe.FURINA_REFRAME = False
        loader.reset_arm_caches()
    culprit = _previous_test["id"]
    try:
        assert not residue, (
            "an arm was still on when this test started, which means the test "
            "BEFORE it on this worker left it on. The leaking test is:\n"
            f"    {culprit}\n"
            "It must restore the flag (monkeypatch, or a try/finally) and drop "
            "the memoized views that move with it "
            "(`loader.reset_arm_caches()`, plus `rewards.character_pool` in "
            "tier 0.5). What was found:\n  " + "\n  ".join(residue))
        yield
    finally:
        _previous_test["id"] = request.node.nodeid


# --- THE SEAM FAMILY, FOR THE FENCES THAT READ SOURCE ----------------------
# `EB-180` split `understudy/soak.py`, `blindplay.py` and `staged_turn.py`
# into one module per concern. Half a dozen fences in this suite are written
# as source reads -- "the soak cannot reach the seat", "blindplay cannot reach
# a sheet" -- and each of them named ONE file. A fence that keeps naming the
# facade after the code moved out of it is a fence that passes because it is
# looking somewhere else, which is worse than no fence at all. So they ask for
# the FAMILY: `<base>.py` and every `<base>_*.py` beside it.

def seam_files(base):
    """Every file `understudy/<base>.py` was split into, the facade first."""
    root = Path(__file__).resolve().parents[2] / "understudy"
    return ([root / f"{base}.py"]
            + sorted(p for p in root.glob(f"{base}_*.py")))


def seam_source(base):
    """The whole family's source, concatenated. For the substring fences."""
    return "\n".join(p.read_text(encoding="utf-8") for p in seam_files(base))


def make_enemy(hp=50, name="dummy", intents=None, is_boss=False):
    return Enemy(hp=hp, max_hp=hp, name=name, is_boss=is_boss,
                 intents=intents or [{"kind": "attack", "amount": 5}])


def make_state(enemies=None, hp=80, seed=0):
    player = Player(hp=hp, max_hp=hp)
    return CombatState(player=player,
                       enemies=enemies or [make_enemy()],
                       rng=random.Random(seed))


@pytest.fixture
def state():
    return make_state()
