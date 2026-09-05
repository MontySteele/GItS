"""`EB-508`: a Deploy performs the member it FIELDS, on a stage that already
has members standing.

WHAT THE SEAT SAW (Furina r11, natural lane, (c) 2). Fight 4 turn 6: Salon
Début prints *"Deploy Mademoiselle Crabaletta"* and the glossary says a Deploy
performs the member it fields at once. The Salon block's first line was the
USHER performing and taking the last Encore, and Crabaletta -- the member the
card named -- performed dry underneath it. "Something performed the front
member off a Deploy, and no printed line says it should."

THE RULE IS BUILT AND THIS FILE IS WHAT SAYS SO. Both engines perform
`entering` and never `salon[0]`: `effects._deploy_salon_members` calls
`salon_member_act(state, entering)` immediately after `p.salon.append`, and the
C# twin `SalonMemberPower.Deploy` calls `PerformMember(..., entering)` at the
same seam (`EB-493`'s `member:` aim is the other end of it). What the seat's
turn actually held was FOUR performances from four different causes -- a
Companion card's front trigger, this deploy, a second Companion card, and a
second deploy -- with only the deploy's own line saying which member it was
about. The page's attribution is `EB-505`/`EB-506`; the rule is pinned here.

A FULL STAGE IS THE HARD CASE, and it is the seat's board: the deploy has to
bow the OLDEST member out first, and a reading that performs "the front" after
that displacement performs the wrong body twice over.
"""

from __future__ import annotations

import random
from pathlib import Path

from tier0.content import loader
from tier0.engine import effects, furina_reframe
from tier0.engine.state import CombatState
from tier0.tests.conftest import make_enemy

import pytest

REPO = Path(__file__).resolve().parents[2]
ENEMY_HP = 400


@pytest.fixture(autouse=True)
def manual_on(monkeypatch):
    """The deploy-performs clause is the reframe's MANUAL leg."""
    for flag in ("FURINA_REFRAME", "FURINA_REFRAME_MANUAL"):
        monkeypatch.setattr(furina_reframe, flag, True)


def _board(stage):
    p = loader.build_player("furina")
    p.salon = list(stage)
    p.powers["salon_member"] = len(p.salon)
    p.encore = 9                       # nothing dry: the question is WHO, not
    #                                    at what rate
    return CombatState(player=p, enemies=[make_enemy(hp=ENEMY_HP)],
                       rng=random.Random(3))


def _ticks(state):
    return [row["member"] for row in state.log if row["event"] == "salon_tick"]


def test_a_deploy_onto_an_occupied_stage_performs_the_member_it_fields():
    state = _board(["usher", "usher"])

    effects._deploy_salon_members(state, 1, "crabaletta")

    assert _ticks(state) == ["crabaletta"]
    assert state.enemies[0].hp < ENEMY_HP        # a Crabaletta hits; an Usher
    #                                              would only have blocked


def test_a_deploy_onto_a_FULL_stage_still_performs_the_member_it_fields():
    """The seat's own board: three standing, so the oldest bows out first and
    a 'perform the front' reading would take an Usher."""
    state = _board(["usher", "usher", "usher"])

    effects._deploy_salon_members(state, 1, "crabaletta")

    assert state.player.salon == ["usher", "usher", "crabaletta"]
    assert _ticks(state) == ["crabaletta"]


def test_the_usher_it_displaced_never_performs():
    """A bow is not a performance: the displaced member pays its bow and is
    gone, and only the entering member reaches `salon_member_act`."""
    state = _board(["usher", "usher", "usher"])

    effects._deploy_salon_members(state, 1, "crabaletta")

    assert "usher" not in _ticks(state)


def test_a_multi_deploy_performs_each_member_as_it_enters():
    state = _board(["usher"])

    effects._deploy_salon_members(state, 2, "crabaletta")

    assert _ticks(state) == ["crabaletta", "crabaletta"]


def test_the_deploy_performs_nobody_with_the_manual_leg_off(monkeypatch):
    """The clause is the arm's, so a release build deploys and stops."""
    monkeypatch.setattr(furina_reframe, "FURINA_REFRAME_MANUAL", False)
    state = _board(["usher"])

    effects._deploy_salon_members(state, 1, "crabaletta")

    assert _ticks(state) == []


def test_the_c_sharp_twin_performs_the_entering_member_too():
    """CROSS-ENGINE SOURCE PIN. `SalonMemberPower.Deploy` needs a live
    `CombatState`, so no headless C# test can watch a deploy land; what a
    test CAN read is which local the call site passes. `company[0]` there
    would be the defect the seat reported."""
    source = (REPO / "klee-mod" / "KleeCode" / "Powers"
              / "SalonPowers.cs").read_text(encoding="utf-8")

    assert "await PerformMember(choiceContext, owner, entering);" in source
    assert "await PerformMember(choiceContext, owner, company[0]);" not in source
