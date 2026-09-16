"""`EB-701`: the battle page says that end-of-turn effects resolve before the
enemies act.

THE FIND (Kokomi r30 lane 1, debrief 5). No line anywhere said when "the end of
your turn" happens relative to the enemy turn -- a companion's end-of-turn hit,
a Dusk Plan -- and the seat learned the order from a Gas Bomb dying without its
Death Blow: a body that did not do the thing the page had just telegraphed for
it.

WHERE IT PRINTS. Beside `POWER_NOTE`, once per screen, on a screen where
something actually fires at the end of your turn -- a power on either side
whose printed sentence says so, a queued Dusk Plan, or the Stage, whose
performers act at the end of your turn by rule. A quiet board reads exactly as
it did.
"""

from __future__ import annotations

from understudy import blindplay

GOROU = {"name": "Gorou", "amount": 1, "type": "Buff",
         "description": "Deals 3 damage to the front enemy at the end of your "
                        "turn."}
STRENGTH = {"name": "Strength", "amount": 2, "type": "Buff",
            "description": "Attacks deal 2 additional damage."}


def _combat(you_status=(), enemy_status=(), **extra) -> dict:
    state = {"state_type": "monster",
             "player": {"character": "kokomi", "hp": 60, "max_hp": 80,
                        "block": 0, "energy": 3, "max_energy": 3, "hand": [],
                        "potions": [], "relics": [], "status": list(you_status),
                        "draw_pile_count": 5, "discard_pile_count": 0,
                        "exhaust_pile_count": 0},
             "battle": {"round": 2, "enemies": [
                 {"entity_id": "GAS", "combat_id": 1, "name": "Gas Bomb",
                  "hp": 3, "max_hp": 12, "block": 0,
                  "intents": [{"type": "Attack", "damage": 5}],
                  "status": list(enemy_status)}]}}
    state.update(extra)
    return state


ORDER = "it comes BEFORE the enemies act"


def test_a_board_with_an_end_of_turn_power_states_the_order():
    page = blindplay.observe(_combat(you_status=[GOROU]))
    assert ORDER in page


def test_the_note_says_what_the_order_buys():
    """The seat's own find, stated: the body killed at the end of your turn
    never takes the intent printed above it."""
    page = blindplay.observe(_combat(you_status=[GOROU]))
    assert "never takes the intent this page printed for it" in page


def test_an_enemys_own_end_of_turn_trigger_raises_it_too():
    page = blindplay.observe(_combat(enemy_status=[
        {"name": "Slow Burn", "amount": 1, "type": "Debuff",
         "description": "Loses 2 HP at the end of the turn."}]))
    assert ORDER in page


def test_a_board_with_no_end_of_turn_effect_does_not_carry_the_note():
    page = blindplay.observe(_combat(you_status=[STRENGTH]))
    assert ORDER not in page


def test_it_prints_once_however_many_powers_carry_the_trigger():
    page = blindplay.observe(_combat(you_status=[GOROU, dict(GOROU,
                                                             name="Gorou+")]))
    assert page.count(ORDER) == 1


def test_a_queued_dusk_plan_raises_it_with_no_power_on_the_board():
    """A Dusk entry is a Plan whose carry-out moved to the end of THIS turn.
    It is not a power, so the power rows alone would never find it.

    The queue row's own mark is the `Dusk: ` prefix on the printed name
    (`_is_dusk`), which is the mod's own spelling.
    """
    state = _combat()
    state["player"]["kokomi_plans"] = {
        "pet": True, "pet_name": "Bake-Kurage", "pet_entity_id": "KURAGE",
        "pending": 1, "twice": False,
        "queue": [{"name": "Dusk: Slack Water", "clauses": 1}],
        "carried_out": []}
    page = blindplay.observe(state)
    assert "Dusk" in page, "the fixture did not reach the Plan block"
    assert ORDER in page


def test_a_plan_queue_with_no_dusk_entry_does_not_raise_it():
    """A morning Plan is carried out at the START of your next turn, which is
    a different moment and not this note's."""
    state = _combat()
    state["player"]["kokomi_plans"] = {
        "pet": True, "pet_name": "Bake-Kurage", "pet_entity_id": "KURAGE",
        "pending": 1, "twice": False,
        "queue": [{"name": "Slack Water", "clauses": 1}],
        "carried_out": []}
    page = blindplay.observe(state)
    assert "Bake-Kurage" in page
    assert ORDER not in page
