"""The blind seats of 2026-09-28 (build 0.2.3984): Kokomi and Furina runs.

Each test names the finding. Records: the seats' own scratch records
(gitignored), summarised in the commit that added this file.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from understudy import blindplay

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _fresh_run_ledger():
    blindplay.forget_run()
    yield
    blindplay.forget_run()


CASKET = {"id": "TAMAKUSHI_CASKET", "name": "Tamakushi Casket",
          "description": "Start each combat with the Bake-Kurage and Open the "
                         "Casket in hand. Each Plan it carries out adds 1 to "
                         "the Casket."}


def _combat(character="Kokomi", relics=(), pets=(), **player) -> dict:
    state = {"state_type": "monster",
             "player": {"character": character, "hp": 60, "max_hp": 80,
                        "block": 0, "energy": 3, "max_energy": 3, "hand": [],
                        "potions": [], "relics": list(relics), "status": [],
                        "pets": list(pets),
                        "draw_pile_count": 5, "discard_pile_count": 0,
                        "exhaust_pile_count": 0},
             "battle": {"round": 2, "enemies": [
                 {"entity_id": "SEAPUNK", "combat_id": 1, "name": "Seapunk",
                  "hp": 30, "max_hp": 44, "block": 0,
                  "intents": [{"type": "Attack", "damage": 5}],
                  "status": []}]}}
    state["player"].update(player)
    return state


def _kokomi(counter, twice=False, queue=None) -> dict:
    return _combat(relics=[dict(CASKET, counter=counter)], kokomi_plans={
        "pet": True, "pet_name": "Bake-Kurage", "pet_entity_id": "KURAGE",
        "pending": len(queue or []), "twice": twice,
        "queue": queue or [], "carried_out": []})


# ------------------------------------ 1. the Casket's count on the page --

def test_the_casket_count_is_printed_beside_the_bake_kurage():
    """Kokomi seat: "no screen shows the Casket's count, so I could not pick
    when to open it"."""
    page = blindplay.observe(_kokomi(3))
    at = page.index("## The Bake-Kurage")
    assert "- Casket: 3" in page[at:]


def test_a_casket_count_of_zero_is_printed_not_dropped():
    """`_text(0)` folded the counter to "" -- the relic row printed no count
    until the first Plan landed."""
    page = blindplay.observe(_kokomi(0))
    assert "- Casket: 0" in page
    assert "**Tamakushi Casket** (0)" in page


def test_no_casket_no_count_line():
    state = _kokomi(2)
    state["player"]["relics"] = []
    assert "Casket:" not in blindplay.observe(state)


# ------------------------------------------ 2. a won run says it won --

def _over(result, hp=0) -> dict:
    return {"state_type": "game_over", "run": {"floor": 48, "act": 3},
            "game_over": {"message": "Run ended.", "result": result},
            "player": {"hp": hp, "max_hp": 78, "gold": 191, "relics": []}}


def test_a_won_run_says_so_and_prints_no_hp():
    """Kokomi seat: after The Architect the page said only "The run ended on
    floor 48" with HP 0/78."""
    page = blindplay.observe(_over("victory"))
    assert "The run ended on floor 48. You WON the run." in page
    assert "HP 0/78" not in page


def test_a_lost_run_says_so_and_keeps_its_hp():
    page = blindplay.observe(_over("defeat"))
    assert "The run ended on floor 48. You LOST the run." in page
    assert "- HP 0/78" in page


def test_the_bridge_sends_the_result_on_the_singleplayer_page():
    src = (REPO / "vendor" / "STS2_MCP" / "McpMod.StateBuilder.cs").read_text(
        encoding="utf-8")
    assert ('["result"] = (currentRoom?.IsVictoryRoom ?? false) ? "victory" '
            ': "defeat"') in src


# ------------------------------------- 3. Nereid's Ascension's two drains --

def test_nereids_face_names_the_dusk_plan_too():
    """Seat: "the Nereid doubling went to the first non-Dusk Plan, which I
    only inferred". The Rare doubles the first entry of each drain
    (`KokomiPlan.Drain`), the morning's and the Dusk's."""
    sheet = (REPO / "docs" / "prototype-surface.yaml").read_text(
        encoding="utf-8")
    # The text pass of 2026-10-08 (rule 15) kept both halves and cut the
    # restated rule.
    assert ("your first [gold]Plan[/gold] is carried out twice. So is your "
            "first [gold]Dusk[/gold] [gold]Plan[/gold]."
            ) in sheet


def test_the_page_names_both_drains_under_the_queue():
    page = blindplay.observe(_kokomi(1, twice=True, queue=[
        {"name": "Dusk: Slack Water", "clauses": 1},
        {"name": "Surging Shoal", "clauses": 1}]))
    assert ("your FIRST Plan twice at the start of your turn, and your "
            "first Dusk Plan twice at the end of it.") in page


# ------------------------------------------------- 4. the Mend cap --

def test_the_mend_tip_names_its_cap_as_a_moment():
    """Seat: the Mend cap and Yumemizuki's "HP over 70%" read as one HP."""
    tips = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype"
            / "ArmKeywordTips.cs").read_text(encoding="utf-8")
    assert ('"[gold]Mend N[/gold]: heal N HP, but never above the HP you had "'
            '\n          + "at the start of this combat."') in tips


# ------------------------------------ 5. every performer's act on stage --

def _furina_with(member, name, badge_text) -> dict:
    stage = {"seats": [{"member": member, "name": name, "seat": 0,
                        "fanfare": 4, "entity_id": "7", "seat_key": 1}],
             "log": []}
    pet = {"id": "PERFORMER", "entity_id": "7", "name": name, "hp": 4,
           "max_hp": 99, "block": 0, "stage_member": member, "stage_seat": 0,
           "status": [{"id": "BADGE", "name": name, "amount": 1,
                       "type": "Buff", "description": badge_text}]}
    return _combat("Furina", pets=[pet], furina_stage=stage)


def test_chevreuses_act_is_printed_on_the_stage():
    """Furina seat: "Chevreuse's effect is not printed on her card or on the
    stage panel; I learned it only from the log"."""
    text = "End of your turn: Spend 2 to gain 1 Energy next turn."
    page = blindplay.observe(_furina_with("chevreuse", "Chevreuse", text))
    at = page.index("## Your stage")
    assert f"- **Chevreuse** — {text}" in page[at:]
    assert "Your ally **Chevreuse**" not in page


def test_a_performer_with_no_badge_prints_no_act_line():
    state = _furina_with("chevreuse", "Chevreuse", "x")
    state["player"]["pets"][0]["status"] = []
    page = blindplay.observe(state)
    stage = page[page.index("## Your stage"):page.index("## Your hand")]
    assert "**Chevreuse** —" not in stage
