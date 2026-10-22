"""Kokomi Balance suite 4 (2026-10-21): the seat page and the bridge.

`review/records/kokomi-balance-suite-4-2026-10-21.md`, "Defects and
legibility":

- Opening Gambit's double did not reach a Plan flipped to its now-line
  (15, expected 30), with no warning. The rule stands (Kokomi review r9,
  item 4: a now-line lands at printed size); the page now says the double
  is lost, off the wire's `double_lost` (`KokomiPlan.LosesDouble`).
- Two seats played Shoal Call ("Plan 3 Stings.") on the Bake-Kurage because
  the bridge's hint offered it: the game's own target gate answers true for a
  `Self` card over her pet. The bridge now asks for a printed Plan line too.
"""

from __future__ import annotations

from pathlib import Path

from tier0.tests.test_understudy_blindplay import _past_lethal_state
from understudy import blindplay, blindplay_board
from understudy.blindplay_notes import PLAN_DOUBLE_LOST_WARNING

REPO = Path(__file__).resolve().parents[2]


def _page(queue):
    state = _past_lethal_state(queue=queue, hp=40)
    return blindplay.render(blindplay.observation(state)).splitlines()


def _two_line(name, line, **extra):
    return {"name": name, "clauses": 1, "two_line": True, "line": line,
            "now_line": "Deal 7 damage.", "plan_line": "Plan: Deal 9.",
            **extra}


def test_a_flip_that_loses_opening_gambits_double_says_so():
    lines = _page([{"name": "Opening Gambit", "clauses": 2},
                   _two_line("Kurage's Oath", "now", double_lost=True)])
    assert lines.count(PLAN_DOUBLE_LOST_WARNING) == 1
    at = lines.index(PLAN_DOUBLE_LOST_WARNING)
    assert "Kurage's Oath" in "".join(lines[at - 3:at])


def test_no_warning_on_the_plan_line_or_an_older_bridge():
    lines = _page([{"name": "Opening Gambit", "clauses": 2},
                   _two_line("Kurage's Oath", "plan")])
    assert PLAN_DOUBLE_LOST_WARNING not in lines


def test_the_board_reads_double_lost_and_absent_is_false():
    player = {"kokomi_plans": {
        "pet": True, "pet_name": "Bake-Kurage",
        "queue": [{"name": "A", "double_lost": True}, {"name": "B"}]}}
    queue = blindplay_board.kokomi_plans(player)["queue"]
    assert [row["double_lost"] for row in queue] == [True, False]


def test_the_bridge_offers_the_jellyfish_only_cards_with_a_plan_line():
    src = (REPO / "vendor" / "STS2_MCP" / "gits"
           / "GitsKokomiPlan.cs").read_text(encoding="utf-8")
    body = src[src.index("private static bool GitsCanTargetPet"):]
    body = body[:body.index("\n    }\n")]
    assert "GitsPrintsPlanLine(card)" in body
    printed = src[src.index("internal static bool GitsPrintsPlanLine"):]
    assert '"PlanClauses"' in printed[:printed.index("\n    }\n")]
