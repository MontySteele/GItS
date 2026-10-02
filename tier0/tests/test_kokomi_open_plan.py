"""A PLAN STAYS OPEN (2026-10-01, ruled; review/active/
kokomi-delay-pays-2026-10-01.md).

[USER]: "Interesting idea! Yes, I think this makes sense. We'd want to make
sure that the UX is reasonably snappy so players don't have to spend forever
on their turns, but it sounds doable."

The rule (sec.2): a Plan written from a TWO-LINE card may be carried out as
its Plan line (the default) or its now-line at printed size. Plan-only cards
and Dusk Plans are unchanged; every carry-out of an entry takes the line it
holds; Plan payoffs count either line.

The UX (sec.3), pick 5 (a), ruled 2026-10-01: "Plans carry out on their Plan
line; click a waiting Plan to flip it." No chooser screen. During her turn the
player flips a waiting two-line Plan (the Plan strip's click in the mod,
`flip <n>` on the bridge) and flips it back the same way; at carry-out each
Plan uses the line it holds.

The sim half is `kokomi_plan.flip` / `choose_lines` / `line_policy` /
`pilot_flips` / `carry_out_now_line`; the page half is the waiting list's
line row and the `flip` verb. The C# twin is pinned in
`klee-mod/KleeTests/Prototype/KokomiOpenPlanTests.cs`.
"""

from __future__ import annotations

from tier0.content import loader
from tier0.engine import kokomi_plan
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_plan import (  # noqa: F401
    kokomi_state, overhaul, plan_card)
from tier0.tests.test_understudy_blindplay import (TWO_PLANS,
                                                    plans_combat_state)
from understudy import blindplay, blindplay_board, blindplay_notes


def _row(cid):
    return loader.get_card(cid)


def _quiet():
    """An enemy that intends nothing this turn: no incoming damage."""
    return make_enemy(hp=200, intents=[{"kind": "block", "amount": 5}])


def _hitter(amount=12):
    return make_enemy(hp=200, intents=[{"kind": "attack", "amount": amount}])


# --- which Plans offer the choice -------------------------------------------

def test_a_two_line_card_writes_an_open_plan(overhaul):
    st = kokomi_state()
    kokomi_plan.schedule(st, _row("proto_kk_kurages_oath"))
    entry = st.kk_plan_queue[0]
    assert entry.now_card is not None and kokomi_plan.two_line(entry)


def test_a_plan_only_card_and_a_dusk_plan_do_not(overhaul):
    st = kokomi_state()
    kokomi_plan.schedule(st, _row("proto_kk_nip"))
    kokomi_plan.schedule(st, _row("proto_kk_shell_of_sanctuary"))   # Dusk
    nip, dusk = st.kk_plan_queue
    assert not kokomi_plan.two_line(nip)
    assert dusk.dusk and not kokomi_plan.two_line(dusk)


# --- no chooser: the Plan line by default, a flip for the now-line ----------

def test_no_chooser_by_default_the_plan_line_is_carried_out(overhaul):
    """A 12-damage intent against 0 Block, and still the Plan line: nothing
    asks, so Kurage's Oath deals its Plan damage and gains no Block."""
    enemy = _hitter(12)
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, _row("proto_kk_kurages_oath"))
    kokomi_plan.resolve_all(st)
    assert st.player.block == 0
    assert enemy.hp < 200
    assert st.kk_plans_carried_out_this_turn == 1


def test_the_pilot_keeps_the_plan_line(overhaul):
    """`line_policy` is the Plan line, so the pilot's end-of-turn flips leave
    every waiting Plan where it is."""
    st = kokomi_state(enemies=[_hitter(30)])
    kokomi_plan.schedule(st, _row("proto_kk_kurages_oath"))
    entry = st.kk_plan_queue[0]
    assert kokomi_plan.line_policy(st, entry) == "plan"
    kokomi_plan.pilot_flips(st)
    assert entry.line == "plan"


def test_a_flipped_plan_carries_out_its_now_line(overhaul):
    """Kurage's Oath: "Gain 6 Block. Or plan: Deal 7 damage to ALL enemies."
    Flipped while it waits, it is carried out as the Block, at its printed 6,
    and no enemy is hit. A payoff counts either line."""
    enemy = _quiet()
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, _row("proto_kk_kurages_oath"))
    assert kokomi_plan.flip(st, 0)
    assert st.kk_plan_queue[0].line == "now"
    kokomi_plan.resolve_all(st)
    assert st.player.block == 6
    assert enemy.hp == 200
    assert st.kk_plans_carried_out_this_turn == 1
    assert any(e["event"] == "plan_line_chosen" and e["line"] == "now"
               for e in st.log)


def test_flipping_back_restores_the_plan_line(overhaul):
    enemy = _quiet()
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, _row("proto_kk_kurages_oath"))
    assert kokomi_plan.flip(st, 0)
    assert kokomi_plan.flip(st, 0)
    assert st.kk_plan_queue[0].line == "plan"
    kokomi_plan.resolve_all(st)
    assert st.player.block == 0
    assert enemy.hp < 200


def test_a_flip_needs_a_two_line_plan_her_turn_and_a_real_index(overhaul):
    st = kokomi_state(enemies=[_quiet()])
    kokomi_plan.schedule(st, _row("proto_kk_nip"))
    kokomi_plan.schedule(st, _row("proto_kk_kurages_oath"))
    assert not kokomi_plan.flip(st, 0)               # Plan-only
    assert not kokomi_plan.flip(st, 5)               # no such Plan
    st.in_player_turn = False
    assert not kokomi_plan.flip(st, 1)               # not her turn
    assert st.kk_plan_queue[1].line == "plan"


def test_a_flip_holds_through_a_mid_turn_carry_out(overhaul):
    """Change of Plans carries the front Plan out now, as the line it holds;
    there is no once-a-turn screen to have used up."""
    st = kokomi_state(enemies=[_hitter(30)])
    kokomi_plan.schedule(st, _row("proto_kk_kurages_oath"))
    kokomi_plan.flip(st, 0)
    kokomi_plan.resolve_all(st)
    assert st.player.block == 6
    kokomi_plan.schedule(st, _row("proto_kk_kurages_oath"))
    kokomi_plan.flip(st, 0)
    kokomi_plan.resolve_front(st)
    assert st.player.block == 12
    assert st.enemies[0].hp == 200


def test_every_carry_out_of_an_entry_takes_its_line(overhaul):
    """Nereid's Ascension carries the first Plan out twice; both copies take
    the line it was flipped to."""
    st = kokomi_state(enemies=[_hitter(30)])
    st.player.powers[kokomi_plan.NEREIDS_ASCENSION] = 1
    kokomi_plan.schedule(st, _row("proto_kk_kurages_oath"))
    kokomi_plan.flip(st, 0)
    kokomi_plan.resolve_all(st)
    assert st.player.block == 12
    assert st.enemies[0].hp == 200
    assert st.kk_plans_carried_out_this_turn == 2


def test_a_now_line_writes_no_rider(overhaul):
    """Second Wave chosen as its now-line is a hit and not "the next Plan is
    carried out twice"."""
    st = kokomi_state(enemies=[_quiet()])
    kokomi_plan.schedule(st, _row("proto_kk_second_wave"))
    entry = st.kk_plan_queue.pop(0)
    entry.line = "now"
    wrote = kokomi_plan._resolve_entry(st, entry, why="test")
    assert wrote == (False, False)
    assert st.enemies[0].hp < 200


# --- the page ----------------------------------------------------------------

def test_split_plan_lines():
    assert blindplay_board.split_plan_lines(
        "Gain 6 Block. Or plan: Deal 7 damage to ALL enemies.") == (
        "Gain 6 Block.", "Deal 7 damage to ALL enemies.")
    assert blindplay_board.split_plan_lines(
        "Draw 1 card. Or dusk plan: Gain 8 Block.") == (
        "Draw 1 card.", "Gain 8 Block.")


def _waiting(line="plan"):
    return dict(TWO_PLANS, queue=[
        {"name": "Nip", "clauses": 1},
        {"name": "Kurage's Oath", "clauses": 1, "two_line": True,
         "now_line": "Gain 6 Block.",
         "plan_line": "Deal 7 damage to ALL enemies.", "line": line}],
        pending=2)


def test_a_waiting_two_line_plan_shows_its_line_and_the_flip():
    page = blindplay.render(blindplay.observation(
        plans_combat_state(_waiting())))
    assert ("Carried out as its **Plan line**: Deal 7 damage to ALL "
            "enemies. · Now-line: Gain 6 Block. · `flip 2` switches it."
            ) in page
    assert page.count(blindplay_notes.TWO_LINE_WAITING_NOTE) == 1
    assert "flip <n>" in page


def test_a_flipped_plan_shows_its_now_line_first():
    page = blindplay.render(blindplay.observation(
        plans_combat_state(_waiting("now"))))
    assert ("Carried out as its **now-line**: Gain 6 Block. · Plan line: "
            "Deal 7 damage to ALL enemies. · `flip 2` switches it.") in page


def test_no_flip_verb_without_a_two_line_plan():
    page = blindplay.render(blindplay.observation(
        plans_combat_state(TWO_PLANS)))
    assert "flip <n>" not in page


def test_flip_is_the_bridge_click_on_the_waiting_plan():
    state = plans_combat_state(_waiting())
    res = blindplay.act(state, "flip 2")
    assert res["ok"] and res["post"] == {"action": "kokomi_flip_plan",
                                         "index": 1}
    res = blindplay.act(state, "flip \"Kurage's Oath\"")
    assert res["ok"] and res["post"] == {"action": "kokomi_flip_plan",
                                         "index": 1}


def test_flip_is_refused_on_a_one_line_plan_and_off_the_fight():
    state = plans_combat_state(_waiting())
    res = blindplay.act(state, "flip 1")
    assert res["ok"] is False and "only one line" in res["refusal"]
    res = blindplay.act(plans_combat_state(TWO_PLANS),
                        "flip \"Kurage's Oath\"")
    assert res["ok"] is False and "no Plan to flip" in res["refusal"]
