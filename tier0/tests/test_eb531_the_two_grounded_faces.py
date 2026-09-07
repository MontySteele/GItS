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
from tier0.engine import companion_standins as standins
from tier0.engine import klee_overhaul
from tier0.tests.conftest import make_enemy, make_state

REPO = Path(__file__).resolve().parents[2]
MOD = REPO / "klee-mod" / "KleeCode"
KAEYA = "proto_mc_kaeya_cold_blooded_strike"
JEAN = "proto_mc_jean_lions_fang"


def _caches_clear():
    loader.reset_arm_caches()
    standins._replacements.cache_clear()


@pytest.fixture
def arms(monkeypatch):
    _caches_clear()
    monkeypatch.setattr(C, "COMPANION_OVERHAUL", True)
    monkeypatch.setattr(C, "KLEE_OVERHAUL", True)
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
    standins.roll_turn(state)


def _source(relative):
    return (MOD / relative).read_text(encoding="utf-8")


# ----------------------------------------------------------------------
# The behaviour: one board, two different answers.
# ----------------------------------------------------------------------
def test_lions_fang_pays_when_nothing_went_off_last_turn(arms):
    state = _klee_state()
    state.player.powers[standins.LIONS_FANG] = 8
    state.player.draw_pile = [loader.peek_card("strike")] * 3
    klee_overhaul.place(state, state.enemies[0], 5)
    _next_turn(state)
    before = state.player.block

    standins.turn_start(state)

    assert state.player.block == before + 8


def test_a_detonation_last_turn_silences_lions_fang_and_not_grounded(arms):
    """THE DISCRIMINATOR. A Bomb went off last turn AND a Bomb stands on the
    field now: Grounded's condition (`EB-516`, the board) is satisfied and
    Lion's Fang's (the ledger) is not."""
    state = _klee_state()
    state.player.powers[standins.LIONS_FANG] = 8
    state.player.powers[klee_overhaul.GROUNDED] = 6
    state.player.draw_pile = [loader.peek_card("strike")] * 3
    klee_overhaul.place(state, state.enemies[0], 5)
    klee_overhaul.set_off(state, state.enemies[0])
    klee_overhaul.place(state, state.enemies[0], 4)
    _next_turn(state)

    before = state.player.block
    standins.turn_start(state)
    assert state.player.block == before, "Lion's Fang paid off Grounded's rule"

    before = state.player.block
    klee_overhaul.turn_start_late(state)
    assert state.player.block == before + 6


def test_kaeyas_blind_does_not_reach_lions_fang(arms):
    """The marker names Grounded and pays Grounded only."""
    state = _klee_state()
    state.player.powers[standins.LIONS_FANG] = 8
    state.player.powers[standins.COLD_BLOODED] = 1
    state.player.draw_pile = [loader.peek_card("strike")] * 3
    klee_overhaul.place(state, state.enemies[0], 5)
    klee_overhaul.set_off(state, state.enemies[0])
    _next_turn(state)
    assert state.mc_grounded_blind          # the blind is up for this turn
    before = state.player.block

    standins.turn_start(state)

    assert state.player.block == before


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


def test_kaeyas_printed_condition_is_the_rule_the_engine_has(arms):
    face = _row(KAEYA)["description"]

    assert "counts a Bomb as on the field" in face
    assert "counts nothing as having gone off" not in face


def test_neither_of_jeans_faces_names_grounded():
    card = _source("Cards/Prototype/Generated/ProtoMcJeanLionsFang.cs")
    power = _source("Powers/Prototype/CompanionStandIns.cs")
    body = power[power.index("class LionsFangPower"):]
    body = body[:body.index("\n}")]

    for source in (card, body):
        assert "went off last turn" in source
        # Not even in a comment: the row's ask is that the tip stops calling
        # Grounded a sibling, and the cheapest way for that to come back is a
        # note that reads as a cross-reference.
        assert "Grounded" not in source

    # And the tip set attaches no Grounded definition to Jean's card, which is
    # the attach Kaeya's face DOES carry.
    assert "ArmKeywordTips.ForGrounded" not in card
    assert "ArmKeywordTips.ForGrounded" in _source(
        "Cards/Prototype/Generated/ProtoMcKaeyaColdBloodedStrike.cs")


def test_lions_fang_reads_the_ledger_and_never_the_blind():
    power = _source("Powers/Prototype/CompanionStandIns.cs")
    body = power[power.index("class LionsFangPower"):]

    assert "SetOffLastTurn > 0" in body
    assert "GroundedBlind" not in body


def test_the_grounded_tip_and_the_glossary_still_say_the_same_thing():
    """`EB-516` moved the condition and both printers moved with it; the row
    is only closed while they still agree."""
    from understudy import blindplay_notes

    tip = _source("Cards/Prototype/ArmKeywordTips.cs")
    glossary = blindplay_notes.ARM_KEYWORDS["Grounded"]

    assert "only if you have a Bomb on the field" in glossary
    assert "only if you have a [gold]Bomb[/gold] on the field" in (
        tip.replace("\"\n          + \"", "").replace("\" + \"", ""))
