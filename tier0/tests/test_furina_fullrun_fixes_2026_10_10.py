"""The Furina full-run round's page fixes
(`review/records/furina-fullrun-round-2026-10-10.md`, "What changes").

- A 0-damage Neuvillette act says why (his number is the HP she lost since
  her last turn).
- A power the game lists twice on one creature prints once, with a note.
- The Strength tip says it lasts for the rest of this fight.

The chooser's enchantment and the turn-start Fanfare telemetry are C# and are
pinned in `klee-mod/KleeTests/Prototype/ModeFaceUpgradeTests.cs` and
`FurinaSpendRoundFixesTests.cs`.

NOTHING MEASURED HERE IS QUOTABLE: shape assertions about a renderer.
"""

import copy

import pytest

from understudy import blindplay
from understudy.blindplay_render import (POWER_LISTED_TWICE_CLAUSE,
                                         STAGE_NO_DAMAGE_HP_LOST, _once,
                                         _render_power, _stage_act_effect)
from tier0.tests.test_eb735_eb736_the_page_prints_the_stage import (
    _beat, _seat, _stage, _state)


@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


def test_a_neuvillette_act_that_dealt_nothing_says_why():
    row = {"member": "neuvillette", "moved": 0}
    assert _stage_act_effect(row) == STAGE_NO_DAMAGE_HP_LOST
    assert STAGE_NO_DAMAGE_HP_LOST == (
        ": no damage (you lost no HP since your last turn)")
    page = blindplay.observe(_state(_stage(
        seats=[_seat("neuvillette", "Neuvillette", 0, "7", guest=True)],
        log=[_beat("act", "neuvillette", "Neuvillette", moved=0)])))
    assert ("**Neuvillette** acted: no damage (you lost no HP since your "
            "last turn).") in page


def test_other_zero_damage_acts_keep_the_plain_line():
    assert _stage_act_effect({"member": "navia", "moved": 0}) == ": no damage"
    assert _stage_act_effect(
        {"member": "neuvillette", "moved": 21}).startswith(": 21 Hydro damage")


def _power(name, stacks, kind="Debuff"):
    return {"name": name, "stacks": stacks, "kind": kind, "text": ""}


def test_a_power_listed_twice_prints_once_with_a_note():
    rows = _once([_power("Weak", 1), _power("Weak", 1),
                  _power("Crab Rage", 6, "Buff")])
    assert [r["name"] for r in rows] == ["Weak", "Crab Rage"]
    assert _render_power(rows[0], "").endswith(POWER_LISTED_TWICE_CLAUSE)
    assert POWER_LISTED_TWICE_CLAUSE not in _render_power(rows[1], "")
    assert POWER_LISTED_TWICE_CLAUSE == " (the game lists this twice)"


def test_two_rows_with_different_amounts_both_print():
    rows = _once([_power("Weak", 1), _power("Weak", 2)])
    assert len(rows) == 2
    assert not any(r.get("listed_twice") for r in rows)


def test_the_enemy_block_prints_a_doubled_power_once():
    state = _state(_stage(seats=[]))
    state = copy.deepcopy(state)
    weak = {"id": "WEAK_POWER", "name": "Weak", "amount": 1, "type": "Debuff",
            "description": "Deals less damage."}
    state["enemies"][0]["status"] = [weak, dict(weak)]
    page = blindplay.observe(state)
    lines = [ln for ln in page.splitlines() if ln.lstrip().startswith("Weak 1")]
    assert len(lines) == 1, lines
    assert POWER_LISTED_TWICE_CLAUSE.strip() in lines[0]


def test_the_strength_tip_says_how_long_it_lasts():
    assert blindplay.BASE_KEYWORDS["Strength"].endswith(
        "It does not decay; it lasts for the rest of this fight.")
