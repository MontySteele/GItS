"""The Kokomi wording pass (2026-10-14), the sim side.

[USER], 2026-10-14: "Yep, please proceed". Four fixes, no number changes:
Pincer's Plan line names the turn it is carried out, Battle Formation says
once a turn, Juuga's Plan line says its three turns, and Crystal Collapse is
unplayable until a Companion has been played this combat. The C# twin is
`klee-mod/KleeTests/Prototype/KokomiWordingPassTests.cs`. NOTHING MEASURED
HERE IS QUOTABLE (R215 B): shape assertions about an engine.
"""

from pathlib import Path

from tier0.content import loader
from tier0.engine import combat, kokomi_plan
from tier0.engine.state import Card, PlanEntry
from tier0.tests.test_arm_keyword_tips import proto
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, card, carry_out, kokomi_state)
from tools import gen_klee_cards

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

def test_battle_formation_says_once_a_turn():
    desc = _row("proto_kk_battle_formation")["description"]
    assert desc.startswith(
        "The first time each turn 2 or more [gold]Plans[/gold] are carried "
        "out, gain ")
    src = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
           / "KokomiRefounding.cs").read_text(encoding="utf-8")
    assert '$"The first time each turn {Threshold} or more "' in src


def test_battle_formation_pays_once_however_many_plans(caches):
    st = kokomi_state()
    st.player.powers[kokomi_plan.BATTLE_FORMATION] = 1
    energy = st.player.energy
    st.kk_plans_carried_out_this_turn = 2
    kokomi_plan.battle_formation(st)
    st.kk_plans_carried_out_this_turn = 3
    kokomi_plan.battle_formation(st)
    assert st.player.energy == energy + 1


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


# --- 4. Crystal Collapse: unplayable until a Companion has been played --------

def test_crystal_collapse_is_unplayable_until_a_companion_is_played(caches):
    st = kokomi_state()
    collapse = card("proto_mi_gorou_crystal_collapse")
    st.player.hand.append(collapse)
    assert kokomi_plan.needs_a_played_companion(collapse)
    assert combat.card_playable(st, collapse) is False
    # Another Crystal Collapse played earlier is never "the last Companion".
    kokomi_plan.note_companion_played(
        st, card("proto_mi_gorou_crystal_collapse"))
    assert combat.card_playable(st, collapse) is False
    kokomi_plan.note_companion_played(st, card("proto_mi_gorou_juuga"))
    assert combat.card_playable(st, collapse) is True
    # Combat-wide: a turn boundary keeps it playable.
    kokomi_plan.roll_turn(st)
    assert combat.card_playable(st, collapse) is True


def test_crystal_collapse_written_names_the_companion(caches):
    st = kokomi_state()
    juuga = card("proto_mi_gorou_juuga")
    kokomi_plan.note_companion_played(st, juuga)
    collapse = card("proto_mi_gorou_crystal_collapse")
    assert kokomi_plan.plan_label(collapse, juuga) == \
        "Crystal Collapse: Gorou — Juuga: Forward Unto Victory"


def test_only_crystal_collapse_takes_the_companion_gate():
    hits = [c.id for c in loader.prototype_cards()
            if kokomi_plan.needs_a_played_companion(c)]
    assert hits == ["proto_mi_gorou_crystal_collapse"]


def test_the_gate_agrees_with_the_emitter_over_every_row():
    for c in loader.prototype_cards():
        row = {"effects": c.effects, "plan": c.plan}
        assert kokomi_plan.needs_a_played_companion(c) == \
            gen_klee_cards.card_needs_a_played_companion(row), c.id


def test_the_generated_card_carries_the_gate_reason_and_preview():
    src = (GEN / "ProtoMiGorouCrystalCollapse.cs").read_text(encoding="utf-8")
    assert "IUnplayableReasonCard" in src
    assert "KokomiRefounding.AnyCompanionPlayed(this)" in src
    assert '"no Companion has been played this combat"' in src
    assert "KokomiCards.WithCopiedCompanionPreview(" in src
