"""`EB-531`: the two faces written near Grounded, pinned so neither drifts on
to the other's rule.

THE ROW'S TWO HALVES. Kaeya -- Cold-Blooded Strike printed the pre-`EB-516`
Grounded ("counts nothing as having gone off") after `EB-516` had moved the
condition to the board; that half is BUILT under `EB-576` and its words are
pinned here beside the other's. The Jean half is this file's own claim:

  * JEAN -- LION'S FANG KEEPS ITS OWN CONDITION. "If none of your Bombs went
    off last turn" is the card's rule and not a stale copy of Grounded's. It
    reads `ko_set_off_last_turn` directly in the sim and `SetOffLastTurn` in
    the mod, and it does NOT read Kaeya's blind -- that marker names Grounded,
    and a marker that quietly paid a second Power would be a rule the player
    was never shown.
  * AND ITS FACE NEVER CALLS GROUNDED A SIBLING. The word does not appear on
    the card, on the Power it grants, or in either engine's tip set for them,
    so a reader is never sent to Grounded's rule to understand Jean's.

THE DISCRIMINATOR both halves turn on: a turn that begins with a Bomb on the
field AFTER a Bomb went off is one where Grounded pays and Lion's Fang does
not. Any drift in either direction shows up there, which is what the two
behavioural tests below stand on.

NOTHING MEASURED ON A PROTOTYPE ROW IS QUOTABLE ANYWHERE (R215 B).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import lions_fang
from tier0.engine import klee_overhaul
from tier0.tests.conftest import make_enemy, make_state

REPO = Path(__file__).resolve().parents[2]
MOD = REPO / "klee-mod" / "KleeCode"
JEAN = "proto_mc_jean_lions_fang"


def _caches_clear():
    loader.reset_arm_caches()


@pytest.fixture
def arms(monkeypatch):
    _caches_clear()
    yield
    _caches_clear()


def _klee_state():
    state = make_state(enemies=[make_enemy(hp=200)])
    state.player.character_id = "klee"
    state.turn = 1
    klee_overhaul.roll_to(state, state.turn)
    return state


def _next_turn(state):
    state.turn += 1
    klee_overhaul.roll_to(state, state.turn)


def _source(relative):
    return (MOD / relative).read_text(encoding="utf-8")


# ----------------------------------------------------------------------
# The behaviour: one board, two different answers.
# ----------------------------------------------------------------------
def test_lions_fang_pays_when_nothing_went_off_last_turn(arms):
    state = _klee_state()
    state.player.powers[lions_fang.LIONS_FANG] = 8
    state.player.draw_pile = [loader.peek_card("strike")] * 3
    klee_overhaul.place(state, state.enemies[0], 5)
    _next_turn(state)
    before = state.player.block

    lions_fang.turn_start(state)

    assert state.player.block == before + 8


# ----------------------------------------------------------------------
# The faces, on the sheet and in the mod.
# ----------------------------------------------------------------------
def _row(card_id):
    import yaml
    sheet = (REPO / "docs" / "prototype-surface.yaml").read_text(
        encoding="utf-8")
    rows = {row["id"]: row for row in yaml.safe_load(sheet)}
    return rows[card_id]


def test_jeans_printed_condition_is_its_own(arms):
    face = _row(JEAN)["description"]

    assert "if none of your [gold]Bombs[/gold] went off last turn" in face
    assert "Grounded" not in face


def test_neither_of_jeans_faces_names_grounded():
    card = _source("Cards/Prototype/Generated/ProtoMcJeanLionsFang.cs")
    power = _source("Powers/Prototype/LionsFangPower.cs")
    body = power[power.index("class LionsFangPower"):]
    body = body[:body.index("\n}")]

    for source in (card, body):
        assert "went off last turn" in source
        # Not even in a comment: the row's ask is that the tip stops calling
        # Grounded a sibling, and the cheapest way for that to come back is a
        # note that reads as a cross-reference.
        assert "Grounded" not in source

    # And the tip set attaches no Grounded definition to Jean's card (Kaeya's
    # Cold-Blooded Strike, the face that did, was cut 2026-10-03).
    assert "ArmKeywordTips.ForGrounded" not in card


def test_lions_fang_reads_the_ledger_and_never_the_blind():
    power = _source("Powers/Prototype/LionsFangPower.cs")
    body = power[power.index("class LionsFangPower"):]

    assert "SetOffLastTurn > 0" in body
    assert "GroundedBlind" not in body

