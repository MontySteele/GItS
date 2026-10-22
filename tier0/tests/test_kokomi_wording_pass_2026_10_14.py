"""The Kokomi wording pass (2026-10-14), the sim side.

[USER], 2026-10-14: "Yep, please proceed". Four fixes, no number changes:
Pincer's Plan line names the turn it is carried out, Battle Formation says
once a turn, Juuga's Plan line says its three turns, and Crystal Collapse is
unplayable until a Companion has been played this combat (that gate is gone
since 2026-10-21: the card's face plays a random Common one with none). The C# twin is
`klee-mod/KleeTests/Prototype/KokomiWordingPassTests.cs`. NOTHING MEASURED
HERE IS QUOTABLE (R215 B): shape assertions about an engine.
"""

from pathlib import Path

from tier0.engine import combat, kokomi_plan
from tier0.engine.state import Card, PlanEntry
from tier0.tests.test_arm_keyword_tips import proto
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, card, carry_out, kokomi_state)

REPO = Path(__file__).resolve().parents[2]
GEN = REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"


def _row(cid):
    """The raw sheet row, as the generator reads it."""
    return next(r for r in proto._rows() if r["id"] == cid)


# --- 1. Pincer: the bonus is on the turn the Plan is carried out --------------

def test_pincer_reads_that_turn_not_next_turn():
    desc = _row("proto_kk_pincer")["description"]
    assert "[gold]Plan[/gold]: Your first Attack that turn is played twice." \
        in desc
    assert "Next turn" not in desc


def test_pincer_pays_on_the_morning_it_is_carried_out(caches):
    """Written on turn N, nothing on turn N; carried out at the start of
    turn N+1, the first Attack of THAT turn is played twice -- the turn the
    new face calls "that turn"."""
    st = kokomi_state()
    pincer = card("proto_kk_pincer")
    st.kk_plan_queue.append(PlanEntry(
        card_id=pincer.id, clauses=list(pincer.plan), card=pincer))
    assert kokomi_plan.FIRST_ATTACK_TWICE not in st.player.powers
    carry_out(st)
    assert st.player.powers[kokomi_plan.FIRST_ATTACK_TWICE] == 1
    # An Attack with no Plan line, so it is played face-up.
    attack = Card(id="proto_kk_probe_attack", name="a", cost=1,
                  type="attack", effects=[{"op": "damage", "amount": 5,
                                           "target": "enemy"}])
    assert kokomi_plan.spend_first_attack_twice(st, attack) == 1
    assert kokomi_plan.spend_first_attack_twice(st, attack) == 0


# --- 2. Battle Formation: once a turn ----------------------------------------

def test_battle_formation_says_when():
    # The Kokomi finish pass (2026-10-19): the base start-of-turn template.
    desc = _row("proto_kk_battle_formation")["description"]
    assert desc.startswith(
        "At the start of your turn, if 2 or more of your [gold]Plans[/gold] "
        "were carried out, gain ")
    src = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
           / "KokomiRefounding.cs").read_text(encoding="utf-8")
    assert '$"At the start of your turn, if {Threshold} or more of your "' in src


# --- 3. Juuga: the Plan line says its three turns -----------------------------

def test_juuga_plan_line_says_three_turns():
    row = _row("proto_mi_gorou_juuga")
    # Wording pass (2026-10-15): the 3 turns lead and cover both lines.
    assert row["description"].startswith("For 3 turns,")
    assert row["description"].endswith(
        "[gold]Plan[/gold]: Gain 6 [gold]Block[/gold] instead.")
    assert row["plan"] == [{"op": "juuga_guard", "amount": 3}]


def test_juuga_plan_grants_block_at_three_turn_ends(caches):
    st = kokomi_state()
    juuga = card("proto_mi_gorou_juuga")
    entry = PlanEntry(card_id=juuga.id, clauses=list(juuga.plan),
                      card=juuga)
    st.kk_plan_queue.append(entry)
    carry_out(st)
    assert st.player.powers[kokomi_plan.MI_JUUGA_GUARD] == 3


# --- 4. Crystal Collapse: playable with no Companion played -----------------
# The wording pass made it unplayable until a Companion had been played; the
# Kokomi upgrade pass (2026-10-19) gave it "If none, play a random Common
# one.", and the gate stayed behind -- refused with "no Companion has been
# played" in three lanes of the Kokomi Balance suite 4 (2026-10-21). Gone.

def test_crystal_collapse_is_playable_with_no_companion_played(caches):
    st = kokomi_state()
    collapse = card("proto_mi_gorou_crystal_collapse")
    st.player.hand.append(collapse)
    assert kokomi_plan.last_other_companion(st, collapse) is None
    assert combat.card_playable(st, collapse) is True
    assert not kokomi_plan.refuses_for_no_plan(st, collapse)


def test_crystal_collapse_written_names_the_companion(caches):
    st = kokomi_state()
    juuga = card("proto_mi_gorou_juuga")
    kokomi_plan.note_companion_played(st, juuga)
    collapse = card("proto_mi_gorou_crystal_collapse")
    assert kokomi_plan.plan_label(collapse, juuga) == \
        "Crystal Collapse: Gorou — Juuga: Forward Unto Victory"


def test_the_generated_card_carries_no_gate_and_keeps_its_preview():
    src = (GEN / "ProtoMiGorouCrystalCollapse.cs").read_text(encoding="utf-8")
    assert "IUnplayableReasonCard" not in src
    assert "IsPlayable" not in src
    assert "no Companion has been played" not in src
    assert "KokomiCards.WithCopiedCompanionPreview(" in src
