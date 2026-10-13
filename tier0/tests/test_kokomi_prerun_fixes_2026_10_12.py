"""Kokomi pre-run fixes (2026-10-12), the blind page's side.

From the Fable round-3 review sec.4 (provenance "Kokomi pre-run fixes,
2026-10-12"). The C# twin is
`klee-mod/KleeTests/Prototype/KokomiPreRunFixesTests.cs`. No number moves.
"""
from __future__ import annotations

from understudy import blindplay_board, blindplay_brief, blindplay_notes
from understudy import blindplay_render


# --- 1. Treatise's draw names Treatise ---------------------------------------

def _ledger(*rows):
    return {"resolutions": list(rows)}


def test_a_power_draw_names_the_power_not_the_card_row():
    player = _ledger(
        {"card": "Kelp Wall", "events": [
            {"kind": "drawn", "card": "Defend", "power": "Treatise",
             "seq": 2}]},
        {"card": "Strike", "events": [
            {"kind": "drawn", "card": "Bash", "power": "", "seq": 3}]})
    events = blindplay_board.page_events(player)
    assert [e["source"] for e in events] == ["Treatise", "Strike"]
    phrase = blindplay_render._event_phrases("drawn", events[:1])
    assert phrase == ["drew Defend (Treatise)"]


# --- 2. a written Companion is played ----------------------------------------

def test_the_written_number_note_carves_out_written_companions():
    said = blindplay_notes.PLAN_WRITTEN_NUMBER_NOTE
    assert "Every planned HIT is the jellyfish's" in said
    assert ("A written Companion is the exception: it is played as a card "
            "next turn, so your Strength and Weak then count.") in said


def test_the_sheet_face_is_labelled_unmodified_not_written():
    lines = blindplay_render._render_card({
        "title": "Jellyfish Drift", "upgraded": False, "cost": "1",
        "kind": "Attack", "text": "Deal 6 Hydro damage. Add a Sting to your "
        "hand.", "written_face": "Deal 8 Hydro damage. Add a Sting to your "
        "hand.", "keywords": [], "playable": True},
        you={"powers": [{"name": "Strength", "stacks": -2}]})
    assert any(line.strip().startswith("Unmodified: Deal 8") for line in lines)
    assert not any(line.strip().startswith("Written:") for line in lines)


# --- 4. the Casket row is one sentence again (the Ancient audit) ------------

def test_the_casket_row_is_the_one_sentence_face():
    assert blindplay_notes.CASKET_ROW == (
        "At the start of your turn, if a Plan is waiting, gain 3 Block.")


# --- 5. Surrounded and "turns you" under --define ----------------------------

def test_define_answers_surrounded_and_turns_you():
    surrounded = blindplay_brief.define("", "Surrounded")
    assert surrounded.startswith("- **Surrounded** — Enemies are on both")
    assert "50% more damage" in surrounded
    for asked in ("turns you", "(turns you)", "Turns You"):
        said = blindplay_brief.define("", asked)
        assert said.startswith("- **turns you** — While you are Surrounded")


# --- 7. a waiting damage Plan into Block -------------------------------------

def _plans(*queue, twice=False):
    return {"queue": list(queue), "twice": twice}


def _hit(damage, aim="front"):
    return {"name": "Kurage's Oath", "aim": aim, "damage": damage}


def _body(block=0, powers=(), intents=()):
    return [{"name": "Tunneler", "hp": 80, "block": block,
             "powers": [{"name": p} for p in powers],
             "intents": [{"type": t} for t in intents]}]


into = blindplay_render._into_block_clauses


def test_kept_block_is_run_down_by_the_plans_ahead():
    clauses = into(_plans(_hit(24), _hit(10), _hit(5)),
                   _body(32, powers=["Burrowed"]))
    # Worded "into 8 Block" since the Kokomi review (2026-10-13).
    assert clauses == {0: " (into 32 Block)", 1: " (into 8 Block)"}


def test_block_that_falls_at_its_turn_start_is_not_named():
    assert into(_plans(_hit(24)), _body(12)) == {}


def test_a_defend_intent_names_the_block_it_will_raise():
    assert into(_plans(_hit(9), _hit(9)), _body(0, intents=["Defend"])) == {
        0: " (into the Block it gains on its turn)"}
    assert into(_plans(_hit(9)), _body(5, powers=["Barricade"],
                                       intents=["Defend"])) == {
        0: " (into 5 Block, plus the Block it gains on its turn)"}


def test_only_front_aimed_damage_rows_carry_it():
    assert into(_plans(_hit(9, aim="all"), {"name": "Tide Wall", "aim": "self",
                                            "damage": 0}),
                _body(30, powers=["Burrowed"])) == {}


# --- Treatise draws on a direct play of a real card, turn after turn --------
#
# Round 4 lane 4 read Treatise as never drawing. Its telemetry and record say
# why: every turn without a draw was a turn its Plan cards were WRITTEN (the
# record: "wrote both Stings as plans"; "never drew a card when I wrote a
# Plan"), and the turns it played one directly drew one. These pin the rule
# on the real rows, a generated Sting included, across turns.

from tier0.engine import combat, kokomi_plan  # noqa: E402
from tier0.tests.test_kokomi_refounding import (  # noqa: E402,F401
    caches, card, kokomi_state, write)


def _treatise_state():
    st = kokomi_state()
    for e in st.enemies:
        e.intents = [{"kind": "attack", "amount": 5}]
    st.player.draw_pile = [card("proto_kk_kelp_wall") for _ in range(8)]
    st.player.powers[kokomi_plan.TREATISE] = 1
    return st


def _play(st, c):
    st.player.hand.append(c)
    assert not kokomi_plan.plan_aimed_at_pet(st, c)
    before = len(st.player.draw_pile)
    combat.play_card(st, c)
    return before - len(st.player.draw_pile)


def test_treatise_draws_on_brine_sting_oath_and_a_generated_sting():
    st = _treatise_state()
    assert _play(st, card("proto_kk_brine_sting")) == 1
    assert _play(st, card("proto_kk_brine_sting")) == 0, "once a turn"
    kokomi_plan.roll_turn(st)
    st.player.energy = 10
    assert _play(st, card("proto_kk_kurages_oath")) == 1
    kokomi_plan.roll_turn(st)
    st.player.energy = 10
    st.player.hand.append(card("proto_kk_shoal_call"))
    combat.play_card(st, st.player.hand[-1])
    sting = next(c for c in st.player.hand if c.id == "proto_kk_sting")
    st.player.hand.remove(sting)
    assert _play(st, sting) == 1


def test_treatise_draws_nothing_on_a_write():
    st = _treatise_state()
    for e in st.enemies:
        e.intents = []
    before = len(st.player.draw_pile)
    write(st, card("proto_kk_brine_sting"))
    assert len(st.kk_plan_queue) == 1
    assert len(st.player.draw_pile) == before
