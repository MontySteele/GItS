"""The Kokomi whole-run round (2026-10-10), "What changes", seat-page items.

Record: `review/records/kokomi-fullrun-round-2026-10-10.md`. The card retunes
are pinned where each row already was (`test_kokomi_feed_pass.py`,
`test_eb311_plan_pricing.py`, the C# pins); the telemetry in
`KokomiFullRunFixesTests.cs`.
"""

from __future__ import annotations

import pytest

from understudy import blindplay

# `TamakushiCasket.cs`, `WatatsumiCasket.Localization`, as the wire prints
# them since the Kokomi re-founding (2026-10-12): no count.
TAMAKUSHI = {"id": "KLEEMOD-TAMAKUSHI_CASKET", "name": "Tamakushi Casket",
             "description": "At the start of your turn, if a Plan is waiting, "
                            "gain 3 Block."}
WATATSUMI = {"id": "KLEEMOD-WATATSUMI_CASKET", "name": "Watatsumi Casket",
             "description": "At the start of your turn, gain 3 Block for each "
                            "Plan waiting."}


@pytest.fixture(autouse=True)
def _fresh_run_ledger():
    blindplay.forget_run()
    yield
    blindplay.forget_run()


def _kokomi(relics=(), **player) -> dict:
    state = {"state_type": "monster",
             "player": {"character": "Kokomi", "hp": 60, "max_hp": 80,
                        "block": 0, "energy": 3, "max_energy": 3, "hand": [],
                        "potions": [], "relics": list(relics), "status": [],
                        "pets": [],
                        "draw_pile_count": 5, "discard_pile_count": 0,
                        "exhaust_pile_count": 0,
                        "kokomi_plans": {
                            "pet": True, "pet_name": "Bake-Kurage",
                            "pet_entity_id": "KURAGE", "pending": 0,
                            "twice": False, "queue": [], "carried_out": []}},
             "battle": {"round": 2, "enemies": [
                 {"entity_id": "SEAPUNK", "combat_id": 1, "name": "Seapunk",
                  "hp": 30, "max_hp": 44, "block": 0,
                  "intents": [{"type": "Attack", "damage": 5}],
                  "status": []}]}}
    state["player"].update(player)
    return state


@pytest.mark.parametrize("relic", [TAMAKUSHI, WATATSUMI],
                         ids=["tamakushi", "watatsumi"])
def test_neither_casket_prints_a_count_line(relic):
    """The count line printed for either Casket while the relic counted
    Plans; the re-founding (2026-10-12) retired the count, so a stray counter
    on the wire prints nothing."""
    page = blindplay.observe(_kokomi([dict(relic, counter=4)]))
    at = page.index("## The Bake-Kurage")
    assert "- Casket:" not in page[at:]


def test_another_counted_relic_prints_no_casket_line():
    other = {"id": "KUNAI", "name": "Kunai", "counter": 2,
             "description": "Every time you play 3 Attacks in a single turn, "
                            "gain 1 Dexterity."}
    page = blindplay.observe(_kokomi([other]))
    assert "- Casket:" not in page


def test_the_plan_list_says_strength_is_read_when_written():
    page = blindplay.observe(_kokomi([dict(TAMAKUSHI, counter=0)]))
    at = page.index("## The Bake-Kurage")
    assert "- Strength is read when the Plan is written." in page[at:]


def test_a_treatise_draw_prints_a_receipt():
    """Treatise printed nothing when it drew, so a turn on which it did not
    fire looked the same. `TreatisePower` now files a `NoteGain` row."""
    state = _kokomi([dict(TAMAKUSHI, counter=0)])
    state["player"]["relic_answers"] = [
        {"source": "Treatise", "amount": 1, "target": "", "combat_id": "",
         "carried": False, "unit": "card"}]
    page = blindplay.observe(state)
    assert "## What your relics and powers answered with" in page
    assert "- **Treatise** gave you 1 card." in page
