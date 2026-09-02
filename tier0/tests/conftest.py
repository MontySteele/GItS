import os
import random

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
