"""`observe --brief` / `act --brief`: what the compact page may cut, and the
lines it may never cut.

THE FIND (2026-09-30). A seat's own grep filter around `observe` dropped every
line containing "this part lands on you" -- the enemy attack intents -- and
the refusals with them, and the seat lost 41 HP to hits it never saw. The
brief page is the tool's own trim; these tests pin the lines it keeps.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from understudy import blindplay, blindplay_brief, blindplay_shape
from understudy.blindplay_notes import (ENEMY_HANDLE_NOTE,
                                        NO_REACTION_THIS_TURN, POWER_NOTE)
from understudy.blindplay_shape import PLAY_GUARDRAIL

REPO = Path(__file__).resolve().parents[2]
RECORDED_COMBAT = (REPO / "review" / "qa" / "kokomi-slice1-r3-t01"
                   / "observed.json")
SEAT_BRIEF = REPO / "docs" / "current" / "operations" / "seat-brief.md"

INTENT = ("    Intent: Aggressive (Attack) — the number on its icon is 12 — "
          "This enemy intends to Attack for 12 damage. — this part lands on "
          "you, and the feed carries no target for an intent part, so this "
          "page cannot say which body")

#: Every line here that is not in DROPPABLE must survive the brief verbatim.
NEVER_DROPPED = [
    "# Battle — round 4",
    "- HP 68/78",
    "- Block 0",
    "- Energy 3/3",
    "- Constrict 6 (debuff) — While the Slithering Strangler is alive, at the "
    "end of your turn, take 6 damage.",
    "## Your stage",
    "- The attacks shown, after the acts' Block of 3: your front performer "
    "takes 3, you take 6.",
    "## Your hand",
    "- **Curtain Rise** — cost 1, attack",
    "    Deal 7 damage. Spend 3: deal 13 instead.",
    "## The other side",
    "- **Slithering Strangler** [C] — HP 7/53",
    INTENT,
    "## What you can say",
    '- `play "<card title>" [on "<enemy>"]`',
    "- `end turn`",
]

DROPPABLE = [
    "## Words on this screen",
    "- **Spend** — Pay Fanfare from your back performer.",
    "- **Weak** — The wearer deals 25% less damage with every hit it lands.",
    ENEMY_HANDLE_NOTE,
    POWER_NOTE,
    "*The end of your turn is a step of its own, and it comes BEFORE the "
    "enemies act: everything that fires at the end of your turn -- a "
    "performer's act -- resolves first, and only then do the bodies above "
    "take their intents. So an enemy killed by one of those never takes the "
    "intent this page printed for it.*",
    "## What reacted this turn",
    NO_REACTION_THIS_TURN,
    PLAY_GUARDRAIL,
]


def _page(words_rows: list[str] | None = None) -> str:
    words = words_rows if words_rows is not None else DROPPABLE[1:3]
    return "\n".join([
        NEVER_DROPPED[0], "", *NEVER_DROPPED[1:5], "",
        NEVER_DROPPED[5], "", NEVER_DROPPED[6], "",
        DROPPABLE[6], "", DROPPABLE[7], "",
        NEVER_DROPPED[7], "", *NEVER_DROPPED[8:10], "",
        NEVER_DROPPED[10], "", *NEVER_DROPPED[11:13], "",
        DROPPABLE[3], "", DROPPABLE[4], "", DROPPABLE[5], "",
        DROPPABLE[0], "", *words, "",
        NEVER_DROPPED[13], "", *NEVER_DROPPED[14:], "",
        DROPPABLE[8], ""])


def test_the_brief_page_keeps_every_never_dropped_line_verbatim():
    out = blindplay_brief.brief(_page()).splitlines()
    for line in NEVER_DROPPED:
        assert line in out, line


def test_the_brief_page_drops_the_glossary_and_the_standing_notes():
    out = blindplay_brief.brief(_page())
    for line in DROPPABLE:
        assert line not in out.splitlines(), line
    assert blindplay_brief.BRIEF_NOTE in out


def test_the_brief_page_keeps_the_full_pages_order():
    out = blindplay_brief.brief(_page()).splitlines()
    at = [out.index(line) for line in NEVER_DROPPED]
    assert at == sorted(at)


def test_a_removal_that_would_hide_an_intent_returns_the_full_page():
    """The safety net. A glossary row that happened to carry an intent's
    words is not a row the brief may cut, so the whole page is printed."""
    page = _page([DROPPABLE[1], "- **Odd** — " + INTENT.strip()])
    assert blindplay_brief.brief(page) == page


@pytest.mark.parametrize("line", [
    INTENT, "- HP 3/70", "- Block 12", "- Energy 0/3",
    "REFUSED: nothing here is called 'Nope'.", "TOOL-BLOCKED: crystal_sphere",
    "- `end turn`", "WAITING: the other player has not ended their turn",
    "blind play error: something", "# Battle — round 2"])
def test_the_protected_pattern_covers_each_kind_of_line(line):
    assert blindplay_brief.PROTECTED.search(line)


def test_the_recorded_combat_page_keeps_its_board():
    state = json.loads(RECORDED_COMBAT.read_text(encoding="utf-8"))["state"]
    full = blindplay.observe(state)
    out = blindplay_brief.brief(full)
    assert "## Words on this screen" in full
    assert "## Words on this screen" not in out
    head, words = full.split("## Words on this screen", 1)
    tail = words[words.index("## What you can say"):]
    kept = out.splitlines()
    for line in (head + tail).splitlines():
        if line.strip() and not blindplay_brief._drop_line(line):
            assert line in kept, line
    assert "Intent:" in out and "- Energy 2/3" in out
    assert len(out) < len(full)
    # 2026-10-01: the italic glosses under the hand are gone too.
    assert "*Applies Hydro* — " in full
    assert "*Applies Hydro*" not in out


# --- 2026-10-01: the italic glosses ------------------------------------------

GLOSS = ("    *Applies Hydro* — If the target has no aura, this applies Hydro "
         "for 2 turns.")


def test_the_brief_page_drops_the_italic_glosses_and_keeps_the_hand():
    """Three of four seats on 2026-10-01 still cut `--brief` with their own
    `grep -v` to drop the gloss lines. The card's own face stays."""
    page = _page().replace(NEVER_DROPPED[9],
                           "\n".join([NEVER_DROPPED[9], GLOSS]))
    assert GLOSS in page.splitlines()
    out = blindplay_brief.brief(page).splitlines()
    assert GLOSS not in out
    for line in NEVER_DROPPED:
        assert line in out, line


def test_a_gloss_that_carries_a_protected_line_is_kept_in_place():
    """A line-level drop never removes an intent, a refusal or a verb,
    whatever it is wrapped in; and it does not cost the rest of the trim."""
    hit = "    *Weak* — this part lands on you for 6"
    page = _page().replace(NEVER_DROPPED[9],
                           "\n".join([NEVER_DROPPED[9], hit, GLOSS]))
    out = blindplay_brief.brief(page).splitlines()
    assert hit in out
    assert GLOSS not in out
    assert blindplay_brief.BRIEF_NOTE in out


def test_an_italic_note_that_is_not_a_gloss_is_kept():
    """Only the `*Word* — meaning` shape is a gloss. A whole italic sentence
    can be an instruction (a chooser's `confirm`, a chest's `choose`)."""
    note = ("*Choosing here arms a pick; it does not close the screen. Say "
            "`confirm` to close it.*")
    assert not blindplay_brief._drop_line(note)
    assert blindplay_brief._drop_line(GLOSS)


# --- the CLI -----------------------------------------------------------------

@pytest.fixture
def lane_budget(tmp_path, monkeypatch):
    monkeypatch.setattr(blindplay_shape, "_BUDGET_STORE_DIR", tmp_path)
    monkeypatch.delenv(blindplay.LANE_ENV, raising=False)
    monkeypatch.delenv(blindplay.MAX_ACTIONS_ENV, raising=False)
    blindplay.forget_fight()
    blindplay.forget_run()
    yield tmp_path
    blindplay.forget_fight()
    blindplay.forget_run()


def _args(**kw) -> argparse.Namespace:
    base = {"raw_file": str(RECORDED_COMBAT), "dry_run": False,
            "brief": True}
    base.update(kw)
    return argparse.Namespace(**base)


def test_observe_brief_prints_the_brief_page(lane_budget, capsys):
    assert blindplay.cmd_observe(_args()) == 0
    out = capsys.readouterr().out
    assert blindplay_brief.BRIEF_NOTE in out
    assert "Intent:" in out and "- HP 24/70" in out


def test_act_brief_puts_a_refusal_on_stdout_and_no_dump(lane_budget, capsys):
    assert blindplay.cmd_act(_args(command='play "Nope"')) == 1
    cap = capsys.readouterr()
    assert cap.out.startswith("REFUSED: nothing here is called 'Nope'")
    assert '"ok"' not in cap.out
    assert cap.err == ""


def test_act_brief_puts_the_budget_refusal_on_stdout(lane_budget, capsys):
    blindplay.set_budget(1)
    blindplay_shape.count_action()
    assert blindplay.cmd_act(_args(raw_file="",
                                   command='play "Coral Guard"')) == 2
    cap = capsys.readouterr()
    assert cap.out.startswith(blindplay.BUDGET_REACHED)
    assert cap.err == ""


def test_act_without_brief_is_unchanged(lane_budget, capsys):
    assert blindplay.cmd_act(_args(brief=False, command='play "Nope"')) == 1
    out = capsys.readouterr().out
    assert '"ok": false' in out
    assert out.rstrip().splitlines()[-1].startswith("REFUSED:")


def test_the_seat_brief_names_the_brief_mode():
    text = SEAT_BRIEF.read_text(encoding="utf-8")
    assert "observe --brief" in text
    assert "grep" in text


# --- 2026-10-01: a word is defined the first time a lane meets it -----------
#
# An Infested Prism elite made every Skill "Tainted 2" and the base-game seat,
# on `--brief`, never once read what Tainted does: the glossary was cut on the
# first screen as on every other.

TAINTED = ("- **Tainted** — A debuff on YOU: each Attack hit on you deals N "
           "more damage.")


def test_the_first_brief_page_on_a_lane_keeps_its_definitions():
    seen: set[str] = set()
    page = _page([DROPPABLE[1], TAINTED]).replace(
        NEVER_DROPPED[9], "\n".join([NEVER_DROPPED[9], GLOSS]))
    out = blindplay_brief.brief(page, seen).splitlines()
    assert "## Words on this screen" in out
    assert TAINTED in out and DROPPABLE[1] in out and GLOSS in out
    # The standing notes still go, and the board is all there.
    assert ENEMY_HANDLE_NOTE not in out and POWER_NOTE not in out
    for line in NEVER_DROPPED:
        assert line in out, line
    assert len(seen) == 3


def test_a_word_already_shown_is_cut_on_the_next_screen():
    seen: set[str] = set()
    blindplay_brief.brief(_page([DROPPABLE[1]]), seen)
    out = blindplay_brief.brief(_page([DROPPABLE[1], TAINTED]),
                                seen).splitlines()
    assert DROPPABLE[1] not in out
    assert TAINTED in out
    again = blindplay_brief.brief(_page([DROPPABLE[1], TAINTED]),
                                  seen).splitlines()
    assert "## Words on this screen" not in again
    assert TAINTED not in again


def test_a_gloss_repeated_on_one_page_prints_once():
    seen: set[str] = set()
    page = _page().replace(NEVER_DROPPED[9],
                           "\n".join([NEVER_DROPPED[9], GLOSS, GLOSS]))
    out = blindplay_brief.brief(page, seen).splitlines()
    assert out.count(GLOSS) == 1


def test_a_gloss_whose_figure_moves_is_still_the_same_word():
    """`*Charge scaling*` prints the Charge held; that is not a new word."""
    def charge(n):
        return (f"    *Charge scaling* — +1 damage per 2 Charge you hold. You "
                f"hold {n} Charge: +{n // 2} damage.")
    seen: set[str] = set()
    first = _page().replace(NEVER_DROPPED[9],
                            "\n".join([NEVER_DROPPED[9], charge(8)]))
    assert charge(8) in blindplay_brief.brief(first, seen).splitlines()
    later = first.replace(charge(8), charge(12))
    assert charge(12) not in blindplay_brief.brief(later, seen).splitlines()


def test_a_protected_glossary_row_still_returns_the_full_page():
    seen: set[str] = set()
    blindplay_brief.brief(_page([DROPPABLE[1]]), seen)
    page = _page([DROPPABLE[1], "- **Odd** — " + INTENT.strip()])
    assert blindplay_brief.brief(page, seen) == page


def test_define_prints_the_row_and_the_gloss_of_one_word():
    page = _page([DROPPABLE[1], TAINTED]).replace(
        NEVER_DROPPED[9], "\n".join([NEVER_DROPPED[9], GLOSS, GLOSS]))
    assert blindplay_brief.define(page, "tainted") == TAINTED + "\n"
    hydro = blindplay_brief.define(page, '"Applies Hydro"').splitlines()
    assert hydro == ["- **Applies Hydro** — " + GLOSS.split(" — ", 1)[1]]


def test_define_says_when_the_screen_has_no_such_word():
    out = blindplay_brief.define(_page([TAINTED]), "Vulnerable")
    assert out.startswith('No definition of "Vulnerable" on this screen.')
    assert "Tainted" in out


def test_observe_brief_remembers_the_lanes_words(lane_budget, capsys,
                                                 monkeypatch):
    monkeypatch.setenv(blindplay.LANE_ENV, "7")
    assert blindplay.cmd_observe(_args()) == 0
    first = capsys.readouterr().out
    assert "## Words on this screen" in first
    assert "*Applies Hydro* — " in first
    assert blindplay_shape.words_seen_path("7").exists()
    assert blindplay.cmd_observe(_args()) == 0
    second = capsys.readouterr().out
    assert "## Words on this screen" not in second
    assert "*Applies Hydro*" not in second
    # Another lane has met none of them.
    monkeypatch.setenv(blindplay.LANE_ENV, "8")
    assert blindplay.cmd_observe(_args()) == 0
    assert "## Words on this screen" in capsys.readouterr().out


def test_an_embark_forgets_the_lanes_words(lane_budget, capsys, monkeypatch):
    monkeypatch.setenv(blindplay.LANE_ENV, "7")
    assert blindplay.cmd_observe(_args()) == 0
    capsys.readouterr()
    blindplay_shape.set_budget(0, "7")
    assert not blindplay_shape.words_seen_path("7").exists()
    assert blindplay.cmd_observe(_args()) == 0
    assert "## Words on this screen" in capsys.readouterr().out


def test_observe_define_prints_one_definition(lane_budget, capsys):
    assert blindplay.cmd_observe(_args(define="Exhaust")) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith("- **Exhaust** — ")
    assert all(line.startswith("- **Exhaust**") for line in out)
    assert blindplay.cmd_observe(_args(define="Nope")) == 0
    assert capsys.readouterr().out.startswith('No definition of "Nope"')


def test_the_seat_brief_names_define():
    assert "observe --define" in SEAT_BRIEF.read_text(encoding="utf-8")


# --- 2026-10-01: an event option that grants a relic prints its rules -------

def test_a_doll_option_prints_its_relics_rules():
    """The Doll Room titles each option with its relic's name and words it
    "take the doll"; the relic's rules arrive only on the hover tip under
    the same name, and the dedupe threw them away."""
    from understudy import blindplay_board
    rules = "At the start of each combat, gain 1 Vigor."
    entry = {"index": 0, "title": "Daughter of the Wind",
             "description": "Take Daughter of the Wind.",
             "is_locked": False, "is_proceed": False, "was_chosen": False,
             "keywords": [{"name": "Daughter of the Wind",
                           "description": rules}]}
    option = blindplay_board._event_option(entry)
    assert option["names"] == [{"name": "Daughter of the Wind",
                                "text": rules, "cost": ""}]
    state = {"state_type": "event",
             "player": {"character": "furina", "hp": 78, "max_hp": 78,
                        "gold": 99, "relics": [], "potions": [],
                        "status": []},
             "event": {"event_id": "DOLL_ROOM", "event_name": "Doll Room",
                       "is_ancient": False, "in_dialogue": False,
                       "body": "Pick a doll.", "options": [entry]}}
    page = blindplay.observe(state)
    assert rules in page
    assert rules in blindplay_brief.brief(page, set())
    assert rules in blindplay_brief.brief(page)
