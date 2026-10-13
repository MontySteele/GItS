"""The Kokomi round 4 A-list (2026-10-13; review
`review/active/kokomi-review-r4-2026-10-13.md` section 5A, items 1, 3, 5, 6
and 7; item 2 stays closed and item 4 did not fit its ceiling).

Moon's Reflection's empty-pile gate, the page fixes (a copy a play adds takes
the next number, the difference line names only what moved, `--define` reads a
power on the board) and the brief's Casket line. Opening Gambit's and Second
Wave's Vigor is the C# side's (the sim never let a Skill spend
`next_attack_up`, pinned here); the C# twin is
`klee-mod/KleeTests/Prototype/KokomiRound4AListTests.cs`.
"""
from __future__ import annotations

import copy
from pathlib import Path

from tier0.content import loader
from tier0.engine import combat, kokomi_plan
from tier0.tests.test_kokomi_refounding import (  # noqa: F401
    caches, kokomi_state)
from tier0.tests.test_kokomi_round_2_fixes_2026_10_13 import (  # noqa: F401
    _act, _fight, _guard, _live, _observe, _play_index, lane)
from tier0.tests.test_arm_keyword_tips import proto
from tools import gen_klee_cards
from understudy import blindplay_brief, blindplay_render

REPO = Path(__file__).resolve().parents[2]
GEN = REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"


def _card(cid: str):
    return copy.deepcopy(loader.get_card(cid))


# --- 1. Moon's Reflection -------------------------------------------------------

def test_moons_reflection_is_unplayable_while_the_exhaust_pile_is_empty(caches):
    st = kokomi_state()
    moon = _card("proto_kk_moons_reflection")
    assert kokomi_plan.needs_an_exhausted_card(moon) is True
    assert combat.card_playable(st, moon) is False
    st.player.exhaust_pile.append(_card("proto_kk_riptide"))
    assert combat.card_playable(st, moon) is True


def test_moons_reflection_carries_the_reason_and_keeps_its_face():
    src = (GEN / "ProtoKkMoonsReflection.cs").read_text(encoding="utf-8")
    assert "IUnplayableReasonCard" in src
    assert "KokomiRefounding.AnyExhausted(this)" in src
    assert '"your Exhaust Pile is empty"' in src
    assert ("Choose a card in your [gold]Exhaust Pile[/gold]. Next turn, "
            "carry out its [gold]Plan[/gold], or play it if it has none.") in src
    rows = {r["id"]: r for r in proto._rows()}
    assert gen_klee_cards.card_needs_an_exhausted_card(
        rows["proto_kk_moons_reflection"])


def test_only_moons_reflection_takes_the_exhaust_gate():
    hits = [c.id for c in loader.prototype_cards()
            if kokomi_plan.needs_an_exhausted_card(c)]
    assert hits == ["proto_kk_moons_reflection"]


# --- 3. Opening Gambit and Second Wave: a Skill never spends Vigor ---------------

def test_the_sim_never_lets_a_skill_spend_next_attack_up(caches):
    for cid in ("proto_kk_opening_gambit", "proto_kk_second_wave"):
        st = kokomi_state()
        st.player.powers["next_attack_up"] = 4
        card = _card(cid)
        assert card.type == "skill"
        st.player.hand.append(card)
        combat.play_card(st, card)
        assert st.player.powers.get("next_attack_up") == 4, cid


def test_the_mod_patches_vigor_for_the_two_skills():
    src = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
           / "KokomiSkillVigor.cs").read_text(encoding="utf-8")
    assert "ProtoKkOpeningGambit or ProtoKkSecondWave" in src
    assert "nameof(VigorPower.ModifyDamageAdditive)" in src
    assert "nameof(VigorPower.BeforeAttack)" in src


# --- 5a. a copy a play adds takes the next number ---------------------------------

def _sting(**over) -> dict:
    return _guard(id="KLEEMOD-STING", name="Sting", cost="0",
                  description="Deal 3 damage.", **over)


def test_a_copy_added_after_the_page_takes_the_next_number(lane, monkeypatch):
    # The page shows two Stings; a play adds two more; the seat counts four.
    wire = _live(monkeypatch, _fight([_sting(), _sting(), _guard()]))
    assert _observe() == 0
    hand = wire.state["player"]["hand"]
    hand.extend([dict(_sting()), dict(_sting())])
    for i, c in enumerate(hand):
        c["index"] = i
    for name in ("Sting (1)", "Sting (2)", "Sting (3)", "Sting (4)"):
        assert _act(f'play "{name}"') == 0, name
        _play_index(wire, wire.posts[-1][1]["card_index"])
    assert len(wire.posts) == 4
    assert not any(c["name"] == "Sting" for c in wire.state["player"]["hand"])


def test_an_unrepeated_title_is_remembered_and_numbered_on(lane, monkeypatch):
    wire = _live(monkeypatch, _fight([_sting(), _guard()]))
    assert _observe() == 0
    hand = wire.state["player"]["hand"]
    hand.extend([dict(_sting()), dict(_sting())])
    for i, c in enumerate(hand):
        c["index"] = i
    assert _act('play "Sting (3)"') == 0
    _play_index(wire, wire.posts[-1][1]["card_index"])
    assert _act('play "Sting (2)"') == 0
    _play_index(wire, wire.posts[-1][1]["card_index"])
    assert len(wire.posts) == 2


# --- 5b. the difference line names only what moved --------------------------------

def test_the_difference_line_names_only_the_terms_that_moved():
    you = {"powers": [{"name": "Dexterity", "stacks": 1},
                      {"name": "Weak", "stacks": 2}]}
    itto = {"written_face": "Gain 9 Block. Deal 12 Geo damage.",
            "text": "Gain 9 Block. Deal 9 Geo damage."}
    assert blindplay_render._face_movers(itto, you) == ["Weak"]
    both = {"written_face": "Gain 9 Block. Deal 12 Geo damage.",
            "text": "Gain 10 Block. Deal 9 Geo damage."}
    assert blindplay_render._face_movers(both, you) == ["Dexterity", "Weak"]
    # Faces that do not split alike keep the old, wider reading.
    odd = {"written_face": "Gain 9 Block. Deal 12 Geo damage.",
           "text": "Deal 9 Geo damage."}
    assert blindplay_render._face_movers(odd, you) == ["Dexterity", "Weak"]


# --- 5c. --define reads a power on the board ---------------------------------------

def test_define_reads_a_power_standing_on_the_board():
    sandpit = "In 4 turns you will be eaten and die."
    state = {"player": {"status": [{"title": "Sandpit", "amount": 4,
                                    "description": sandpit}]},
             "battle": {"enemies": [{"status": [
                 {"name": "Frantic", "description": "Its own text."}]}]}}
    powers = blindplay_brief.screen_powers(state)
    assert ("Sandpit", sandpit) in powers
    out = blindplay_brief.define("", "sandpit", None, powers)
    assert out == f"- **Sandpit** — {sandpit}\n"
    assert blindplay_brief.OFF_SCREEN_MARK not in out
    # Off the board, the enemy briefing still answers, marked off-screen.
    assert blindplay_brief.define("", "Sandpit").rstrip().endswith(
        blindplay_brief.OFF_SCREEN_MARK.strip())


# --- 6. the brief's Casket line --------------------------------------------------

def test_the_brief_casket_line_reads_start_of_turn():
    brief = (REPO / "review" / "active" / "kokomi-brief-2026-09-01.md"
             ).read_text(encoding="utf-8")
    flat = " ".join(brief.split())
    assert ('"At the start of your turn, if a Plan is waiting, gain 3 Block." '
            "It lands after the Block clear and before Plans resolve.") in flat
    assert "At the end of your turn, if a Plan is waiting" not in flat
