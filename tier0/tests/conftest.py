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
