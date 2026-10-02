"""A PLAN STAYS OPEN (2026-10-01, ruled; review/active/
kokomi-delay-pays-2026-10-01.md).

[USER]: "Interesting idea! Yes, I think this makes sense. We'd want to make
sure that the UX is reasonably snappy so players don't have to spend forever
on their turns, but it sounds doable."

The rule (sec.2): when the Bake-Kurage carries out a Plan written from a
TWO-LINE card, the player chooses which line it resolves as -- the Plan line
(the default) or the now-line at printed size. Plan-only cards and Dusk Plans
are unchanged; every carry-out of an entry takes the line chosen for it; Plan
payoffs count either line. The UX (sec.3): one chooser a turn, only when a
two-line Plan is due, `flip "<card>"` and `confirm` on the bridge.

The sim half is `kokomi_plan.choose_lines` / `line_policy` /
`carry_out_now_line`; the page half is `blindplay_board.plan_chooser_rows`,
the `flip` verb and the chooser render. The C# twin is pinned in
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


# --- the pilot's choice and what each line does ------------------------------

def test_the_block_now_line_is_taken_when_the_hit_would_land(overhaul):
    """Kurage's Oath: "Gain 6 Block. Or plan: Deal 7 damage to ALL enemies."
    A 12-damage intent against 0 Block: the pilot takes the Block, at its
    printed 6, and no enemy is hit."""
    enemy = _hitter(12)
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, _row("proto_kk_kurages_oath"))
    kokomi_plan.resolve_all(st)
    assert st.player.block == 6
    assert enemy.hp == 200
    # A payoff counts either line.
    assert st.kk_plans_carried_out_this_turn == 1
    assert any(e["event"] == "plan_line_chosen" and e["line"] == "now"
               for e in st.log)


def test_the_plan_line_is_the_default_on_a_quiet_turn(overhaul):
    enemy = _quiet()
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, _row("proto_kk_kurages_oath"))
    kokomi_plan.resolve_all(st)
    assert st.player.block == 0
    assert enemy.hp < 200


def test_an_intangible_target_turns_a_damage_plan_to_its_now_line(overhaul):
    """The paper's Soul Fysh turn: every body the Plan line would hit is
    Intangible, so the pilot takes the now-line even with nothing incoming
    (Kurage's Oath's Block, not a hit into Intangible)."""
    enemy = _quiet()
    enemy.powers["intangible"] = 1
    st = kokomi_state(enemies=[enemy])
    kokomi_plan.schedule(st, _row("proto_kk_kurages_oath"))
    entry = st.kk_plan_queue[0]
    assert kokomi_plan.line_policy(st, entry) == "now"
    enemy.powers.pop("intangible")
    assert kokomi_plan.line_policy(st, entry) == "plan"


def test_one_chooser_a_turn(overhaul):
    """The morning claims the turn's one screen; a Change of Plans later the
    same turn carries its Plan out on the Plan line."""
    st = kokomi_state(enemies=[_hitter(30)])
    kokomi_plan.schedule(st, _row("proto_kk_kurages_oath"))
    kokomi_plan.resolve_all(st)
    assert st.player.block == 6                      # the morning chose
    kokomi_plan.schedule(st, _row("proto_kk_kurages_oath"))
    kokomi_plan.resolve_front(st)
    assert st.player.block == 6                      # Plan line: a hit
    assert st.enemies[0].hp < 200


def test_every_carry_out_of_an_entry_takes_its_line(overhaul):
    """Nereid's Ascension carries the first Plan out twice; both copies take
    the line chosen for it."""
    st = kokomi_state(enemies=[_hitter(30)])
    st.player.powers[kokomi_plan.NEREIDS_ASCENSION] = 1
    kokomi_plan.schedule(st, _row("proto_kk_kurages_oath"))
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


def _chooser_state(selected=(False, False)):
    state = plans_combat_state(TWO_PLANS)
    state = dict(state)
    state["state_type"] = "card_select"
    state["card_select"] = {
        "screen_type": "simple_select", "can_confirm": True,
        "can_cancel": False,
        "prompt": blindplay_board.PLAN_CHOOSER_PROMPT,
        "selection_known": True,
        "cards": [
            {"name": "Kurage's Oath", "cost": "1", "index": 0,
             "selected": selected[0],
             "description": "Gain 6 Block. Or plan: Deal 7 damage to ALL "
                            "enemies."},
            {"name": "Tidal Screen", "cost": "1", "index": 1,
             "selected": selected[1],
             "description": "Gain 7 Block. Or plan: Draw 2 cards."}]}
    return state


def test_the_chooser_page_lists_both_lines_and_the_selection():
    page = blindplay.render(blindplay.observation(_chooser_state((True,
                                                                  False))))
    assert blindplay_notes.PLAN_CHOOSER_HEADING in page
    assert "**Kurage's Oath** — carried out as its **now-line**" in page
    assert "**Tidal Screen** — carried out as its **Plan line**" in page
    assert "Plan line: Deal 7 damage to ALL enemies." in page
    assert "Now-line: Gain 6 Block." in page
    assert '`flip "<card>"`' in page and "`confirm`" in page


def test_flip_is_a_click_on_the_named_plan_and_confirm_closes():
    res = blindplay.act(_chooser_state(), 'flip "Tidal Screen"')
    assert res["ok"] and res["post"] == {"action": "select_card", "index": 1}
    res = blindplay.act(_chooser_state(), "flip 1")
    assert res["ok"] and res["post"] == {"action": "select_card", "index": 0}
    res = blindplay.act(_chooser_state(), "confirm")
    assert res["ok"] and res["post"] == {"action": "confirm_selection"}


def test_flip_is_refused_off_the_chooser():
    res = blindplay.act(plans_combat_state(TWO_PLANS), 'flip "Kurage\'s Oath"')
    assert res["ok"] is False and "no Plan to flip" in res["refusal"]


def test_a_waiting_two_line_plan_shows_both_lines():
    plans = dict(TWO_PLANS, queue=[
        {"name": "Kurage's Oath", "clauses": 1, "two_line": True,
         "now_line": "Gain 6 Block.",
         "plan_line": "Deal 7 damage to ALL enemies."},
        {"name": "Nip", "clauses": 1}], pending=2)
    page = blindplay.render(blindplay.observation(plans_combat_state(plans)))
    assert (f"{blindplay_notes.TWO_LINE_WAITING_NOTE} Plan line: Deal 7 "
            "damage to ALL enemies. · Now-line: Gain 6 Block.") in page
    assert page.count(blindplay_notes.TWO_LINE_WAITING_NOTE) == 1
