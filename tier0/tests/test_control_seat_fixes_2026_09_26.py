"""The base-game control seats of 2026-09-26: Ironclad, Silent, Defect and
Necrobinder played whole runs through the design-blind page, and these are the
page's own defects they found.

Each test names the seat and the finding. Records: the main checkout's
`review/qa/seats-2026-09-26/control-lane{1,2,3,4}.md` (gitignored).
"""

from __future__ import annotations

from understudy import blindplay

LIGHTNING = {"id": "LIGHTNING_ORB", "name": "Lightning", "passive_val": 3,
             "evoke_val": 8,
             "description": "Passive: At the end of turn, deal 3 damage to a "
                            "random enemy. Evoke: Deal 8 damage to a random "
                            "enemy."}
FROST = {"id": "FROST_ORB", "name": "Frost", "passive_val": 2,
         "evoke_val": 5,
         "description": "Passive: At the end of turn, gain 2 Block. Evoke: "
                        "Gain 5 Block."}


def _combat(character="Ironclad", status=(), **player) -> dict:
    state = {"state_type": "monster",
             "player": {"character": character, "hp": 60, "max_hp": 80,
                        "block": 0, "energy": 3, "max_energy": 3, "hand": [],
                        "potions": [], "relics": [], "status": list(status),
                        "draw_pile_count": 5, "discard_pile_count": 0,
                        "exhaust_pile_count": 0},
             "battle": {"round": 2, "enemies": [
                 {"entity_id": "SEAPUNK", "combat_id": 1, "name": "Seapunk",
                  "hp": 30, "max_hp": 44, "block": 0,
                  "intents": [{"type": "Attack", "damage": 5}],
                  "status": []}]}}
    state["player"].update(player)
    return state


# ---------------------------------------------------- Defect: the orbs --

def test_the_orbs_print_in_slot_order_oldest_first():
    """Defect, (c) 1: "Orbs are invisible. There is no list, count or
    order." The wire's list is `OrbQueue.Orbs`, oldest first."""
    page = blindplay.observe(_combat(
        "Defect", orbs=[LIGHTNING, FROST], orb_slots=3, orb_empty_slots=1))
    assert "- Orbs: 2 of 3 slots filled, oldest first:" in page
    first = page.index("1. **Lightning** — Passive: At the end of turn")
    second = page.index("2. **Frost** — Passive: At the end of turn")
    assert first < second


def test_an_orb_with_no_sentence_prints_its_two_numbers():
    page = blindplay.observe(_combat(
        "Defect", orbs=[dict(LIGHTNING, description=None)], orb_slots=3))
    assert "1. **Lightning** — passive 3, evoke 8" in page


def test_the_page_ties_rightmost_to_the_oldest_orb():
    """Defect, (c) 2: "'Rightmost' is never tied to channel order. I guessed
    wrong twice with Dualcast." The game's own word, tied to orb 1."""
    page = blindplay.observe(_combat(
        "Defect", orbs=[LIGHTNING, FROST], orb_slots=3))
    assert "Orb 1, the oldest, is your rightmost orb: it evokes next" in page
    assert "channelling into full slots evokes it first" in page


def test_empty_slots_print_a_count_and_no_order_note():
    page = blindplay.observe(_combat("Defect", orbs=[], orb_slots=3))
    assert "- Orbs: 0 of 3 slots filled." in page
    assert "rightmost" not in page


def test_a_character_with_no_orb_slots_prints_no_orb_line():
    assert "Orbs:" not in blindplay.observe(_combat())


def test_an_end_of_turn_orb_raises_the_turn_order_note():
    page = blindplay.observe(_combat("Defect", orbs=[LIGHTNING], orb_slots=3))
    assert "it comes BEFORE the enemies act" in page
    assert "an orb's passive" in page


# ------------------------------- Ironclad: no mod word on a base board --

PLATING = {"name": "Plating", "amount": 4, "type": "Buff",
           "description": "At the end of your turn, gain 4 Block."}


def test_the_turn_order_note_names_no_kit_word_on_a_base_board():
    """Ironclad, (c) 13: the glossary line mentioned "a performer's act, a
    Dusk Plan" on Ironclad screens."""
    page = blindplay.observe(_combat(status=[PLATING]))
    assert "it comes BEFORE the enemies act" in page
    assert "performer" not in page
    assert "Dusk" not in page


def test_a_dusk_plan_board_still_names_the_dusk_plan():
    state = _combat("kokomi", status=[PLATING])
    state["player"]["kokomi_plans"] = {
        "pet": True, "pet_name": "Bake-Kurage", "pet_entity_id": "KURAGE",
        "pending": 1, "twice": False,
        "queue": [{"name": "Dusk: Slack Water", "clauses": 1}],
        "carried_out": []}
    page = blindplay.observe(state)
    assert "a Dusk Plan" in page
    assert "a performer's act" not in page


# --------------------------------------------- Necrobinder: Osty's HP --

OSTY = {"id": "OSTY", "entity_id": "7", "name": "Osty", "alive": True,
        "hp": 6, "max_hp": 9, "block": 2, "status": []}


def test_osty_prints_with_his_hp():
    """Necrobinder: "Osty's current HP is never printed on the combat page.
    I read it off Unleash's printed number." """
    page = blindplay.observe(_combat("Necrobinder", pets=[OSTY]))
    assert "- Your ally **Osty**: HP 6/9, Block 2" in page


def test_a_downed_osty_prints_his_zero():
    page = blindplay.observe(_combat(
        "Necrobinder", pets=[dict(OSTY, alive=False, hp=0, block=0)]))
    assert "- Your ally **Osty**: HP 0/9" in page


def test_a_stage_performer_is_left_to_the_stage_block():
    usher = dict(OSTY, name="Gentilhomme Usher", entity_id="8",
                 stage_member="usher", stage_seat=0)
    page = blindplay.observe(_combat("Necrobinder", pets=[usher]))
    assert "Your ally" not in page


# ------------------------------- Defect and Necrobinder: the map page --

def _map() -> dict:
    """Floor 4 forks three ways; the rest site on floor 5 is reachable only
    from the left fork, and the right fork is a corridor into two fights."""
    def node(col, row, kind, *children, **extra):
        return dict({"col": col, "row": row, "type": kind,
                     "children": [list(c) for c in children]}, **extra)
    return {"state_type": "map",
            "run": {"act": 2, "floor": 23},
            "player": {"hp": 12, "max_hp": 75, "gold": 90},
            "map": {
                "current_position": {"col": 2, "row": 3, "type": "Monster"},
                "next_options": [
                    {"index": 0, "type": "Monster", "col": 1, "row": 4},
                    {"index": 1, "type": "Unknown", "col": 3, "row": 4}],
                "nodes": [
                    node(2, 3, "Monster", (1, 4), (3, 4)),
                    node(1, 4, "Monster", (0, 5), (1, 5)),
                    node(3, 4, "Unknown", (3, 5)),
                    node(0, 5, "RestSite", (1, 6)),
                    node(1, 5, "Monster", (1, 6)),
                    node(3, 5, "Monster", (1, 6)),
                    node(5, 5, "Merchant", (1, 6)),
                    node(1, 6, "Boss", id="KNOWLEDGE_DEMON",
                         name="Knowledge Demon")],
                "boss": {"col": 1, "row": 6, "id": "KNOWLEDGE_DEMON",
                         "name": "Knowledge Demon"}}}


def test_the_map_prints_every_reachable_room_and_its_links():
    """Defect, (c) 10: "The map page lists rooms per floor but not the links
    beyond the next floor." The right fork is a corridor with no rest site,
    and the page now shows it."""
    page = blindplay.observe(_map())
    assert "- 1 floor ahead: A Monster (to A, B); B Unknown (to C)" in page
    assert ("- 2 floors ahead: A RestSite (to A); B Monster (to A); "
            "C Monster (to A)") in page
    assert "- 3 floors ahead: A Boss" in page
    # The Merchant no path reaches is not printed as a room you can reach.
    assert "Merchant" not in page


def test_the_map_page_prints_the_hp():
    """Necrobinder: "The map page never shows HP." """
    assert "- HP 12/75" in blindplay.observe(_map())


# ------------------------------ Defect: Hologram+'s pile picker closes --

def test_the_combat_pile_picker_is_not_told_to_confirm():
    """Defect, fight 13: "The Hologram chooser said 'Say `confirm` after
    `choose` to take it'. But `choose` closed it, and my `confirm` was
    refused." The pile picker runs the same self-closing check as the event
    picker, and the wire names it by class name."""
    from understudy.blindplay_notes import (CHOOSER_CONFIRM_NOTE,
                                            CHOOSER_MAYBE_CLOSES_NOTE,
                                            CLOSES_NOTE_HEAD, chooser_note)
    kind = "NCombatPileCardSelectScreen"
    assert chooser_note(kind, True, 1).startswith(CLOSES_NOTE_HEAD)
    assert chooser_note(kind, None) == CHOOSER_MAYBE_CLOSES_NOTE
    assert chooser_note(kind, False) == CHOOSER_CONFIRM_NOTE


def test_the_bridge_reads_the_pile_pickers_prefs():
    from pathlib import Path
    src = (Path(__file__).resolve().parents[2] / "vendor" / "STS2_MCP"
           / "gits" / "GitsSelectPrefs.cs").read_text(encoding="utf-8")
    assert '"NCombatPileCardSelectScreen"' in src


# ------------------------ Silent and Necrobinder: a negative Strength --

def test_a_negative_strength_is_a_debuff():
    """Silent and Necrobinder: Tender "produced 'Strength -1 (buff)' and
    'Dexterity -1 (buff)', labelled as buffs." An older bridge sends the
    power's static type; the page reads the sign as the game does."""
    page = blindplay.observe(_combat(status=[
        {"name": "Strength", "amount": -1, "type": "Buff",
         "description": "Attacks deal 1 less damage."},
        {"name": "Dexterity", "amount": 2, "type": "Buff",
         "description": "Block gained is increased by 2."}]))
    assert "Strength -1 (debuff)" in page
    assert "Dexterity 2 (buff)" in page


# ------------------------------- Defect and Silent: the stolen card --

HOPPER_SWIPE = {"name": "Swipe", "amount": 1, "type": "Buff",
                "stack": "Single",
                "description": "Upon killing this enemy, the stolen card is "
                               "returned.",
                "keywords": [{"name": "Refract",
                              "description": "Deal 20 damage."}]}


def _hopper(power) -> dict:
    state = _combat("Defect")
    state["battle"]["enemies"][0].update(name="Thieving Hopper",
                                         status=[power])
    return state


def test_the_swipe_row_names_the_stolen_card():
    """Defect, (c) 7: "The Thieving Hopper's stolen card is never named." """
    page = blindplay.observe(_hopper(dict(HOPPER_SWIPE,
                                          stolen_card="Refract")))
    assert "the stolen card is returned. It holds your **Refract**." in page


def test_an_older_bridge_names_it_off_the_cards_own_tip():
    page = blindplay.observe(_hopper(HOPPER_SWIPE))
    assert "It holds your **Refract**." in page


# ------------------------------------------ Silent: Kaiser Crab's facing --

def _crab(behind) -> dict:
    state = _combat("Silent", status=[
        {"name": "Surrounded", "amount": 1, "type": "Debuff",
         "stack": "Single", "behind": behind,
         "description": "Receive 50% more damage if attacked from behind."}])
    state["battle"]["enemies"] = [
        {"entity_id": "CRUSHER", "combat_id": 4, "name": "Crusher",
         "hp": 200, "max_hp": 209, "block": 0, "status": [],
         "intents": [{"type": "Attack", "damage": 18}]},
        {"entity_id": "ROCKET", "combat_id": 5, "name": "Rocket",
         "hp": 190, "max_hp": 199, "block": 0, "status": [],
         "intents": [{"type": "Attack", "damage": 3}]}]
    return state


def test_surrounded_names_the_body_behind_you():
    """Silent: "The page never says which way I face; I read it off which
    intent had Surrounded folded in." """
    page = blindplay.observe(_crab(["5"]))
    assert "Behind you now: **Rocket**." in page


def test_surrounded_with_nobody_behind_says_so():
    assert "No enemy is behind you now." in blindplay.observe(_crab([]))


def test_the_bridge_sends_the_three_power_facts():
    from pathlib import Path
    src = (Path(__file__).resolve().parents[2] / "vendor" / "STS2_MCP"
           / "McpMod.StateBuilder.cs").read_text(encoding="utf-8")
    assert '["type"] = power.TypeForCurrentAmount.ToString()' in src
    assert 'row["stolen_card"]' in src and 'row["behind"]' in src


# ------------------ Silent and Ironclad: base cards' upgraded faces --

def _smith(**extra) -> dict:
    card = dict({"index": 0, "name": "Flame Barrier", "id": "FLAME_BARRIER",
                 "description": "Gain 12 Block. Whenever you are attacked "
                                "this turn, deal 4 damage back.",
                 "type": "Skill", "cost": "2"}, **extra)
    return {"state_type": "card_select",
            "player": {"character": "Ironclad", "potions": [], "relics": [],
                       "max_potion_slots": 3},
            "card_select": {"screen_type": "upgrade",
                            "prompt": "Choose a card to upgrade.",
                            "can_skip": True, "preview_showing": False,
                            "can_confirm": False, "selection_known": True,
                            "cards": [card]}}


def test_a_base_card_prints_the_games_own_upgraded_face():
    """Silent (Yummy Cookie) and Ironclad (Smith): "Upgraded: not shown --
    this page has no written face for this card" for almost every non-starter
    card. No sheet holds a base card's upgrade; the game's own face does."""
    page = blindplay.observe(_smith(
        upgraded_description="Gain 16 Block. Whenever you are attacked this "
                             "turn, deal 6 damage back.",
        upgraded_cost="2"))
    assert ("Upgraded: Gain 16 Block. Whenever you are attacked this turn, "
            "deal 6 damage back.") in page
    assert "not shown" not in page


def test_an_upgrade_that_cuts_the_cost_prints_the_new_cost():
    page = blindplay.observe(_smith(upgraded_description="Gain 12 Block.",
                                    upgraded_cost="1"))
    assert "Upgraded: cost 1 — Gain 12 Block." in page


def test_an_older_bridge_still_says_why_it_cannot_show_one():
    assert "Upgraded: not shown" in blindplay.observe(_smith())


def test_the_bridge_sends_the_upgraded_face_on_the_upgrade_grid():
    from pathlib import Path
    src = (Path(__file__).resolve().parents[2] / "vendor" / "STS2_MCP"
           / "McpMod.StateBuilder.cs").read_text(encoding="utf-8")
    assert 'info["upgraded_description"]' in src
    assert src.count("GitsAddUpgradePreview(screen, card, cardInfo);") == 2


# ------------------------------ Ironclad, Silent, Necrobinder: Tainted --

def test_the_tainted_gloss_says_it_lasts_through_the_enemy_turn():
    """Three seats: the gloss "says it 'wears off at the end of your turn',
    yet it added to the enemy's attack on the enemy's turn."
    `TaintedPower` removes itself at the end of the enemy side's turn."""
    from understudy.blindplay_notes import GAME_KEYWORDS
    gloss = GAME_KEYWORDS["Tainted"]
    assert "end of your turn" not in gloss
    assert "lasts through the enemies' next turn" in gloss


# ----------------------------------------------- Ironclad: Sozu's potion --

def _rewards(relics) -> dict:
    return {"state_type": "rewards",
            "player": {"character": "Ironclad", "potions": [],
                       "max_potion_slots": 3, "relics": relics},
            "rewards": {"can_proceed": True, "items": [
                {"index": 0, "type": "potion", "potion_id": "POWER_POTION",
                 "potion_name": "Power Potion", "description": "Power Potion",
                 "potion_description": "Choose 1 of 3 Powers."}]}}


SOZU = {"id": "SOZU", "name": "Sozu",
        "description": "Gain 1 Energy at the start of each turn. You can no "
                       "longer obtain potions."}


def test_a_potion_offer_under_sozu_says_it_gives_nothing():
    """Ironclad, (c) 6: "Sozu: the tool said 'Took: Power Potion' and nothing
    arrived." The reward screen says so before the claim."""
    page = blindplay.observe(_rewards([SOZU]))
    assert "You hold **Sozu**, which stops you obtaining potions" in page


def test_a_potion_offer_without_the_relic_says_nothing_of_it():
    assert "stops you obtaining" not in blindplay.observe(_rewards([]))


# ------------------------------- three seats: the blank first observe --

class _Wire:
    def __init__(self, *states):
        self.states = list(states)
        self.reads = 0

    def get_state(self):
        self.reads += 1
        return self.states.pop(0)


def _event(options, **extra) -> dict:
    return {"state_type": "event",
            "event": dict({"event_name": "This or That?", "is_ancient": False,
                           "in_dialogue": False, "options": options},
                          **extra)}


def test_an_event_drawn_before_its_options_is_read_again():
    """Ironclad, Silent and Defect: "The first observe of an event or Ancient
    room showed an empty option list; a second observe loaded it." """
    from understudy.blindplay_read import settle
    ready = _event([{"index": 0, "title": "Leave", "is_proceed": True}])
    wire = _Wire(_event([]), ready)
    assert settle(_event([]), wire, delay=0) is ready
    assert wire.reads == 2


def test_the_wait_is_short_and_a_room_with_no_options_still_draws():
    from understudy.blindplay_read import settle_event
    from understudy.blindplay_shape import EVENT_SETTLE_TRIES
    wire = _Wire(*[_event([]) for _ in range(EVENT_SETTLE_TRIES)])
    out = settle_event(_event([]), wire, delay=0)
    assert out["event"]["options"] == []
    assert wire.reads == EVENT_SETTLE_TRIES


def test_an_ancient_in_its_dialogue_is_not_waited_on():
    from understudy.blindplay_read import settle_event
    wire = _Wire()
    talking = _event([], is_ancient=True, in_dialogue=True)
    assert settle_event(talking, wire, delay=0) is talking
    assert wire.reads == 0


# ------------------------------------------- Necrobinder: Akabeko's Vigor --

def test_vigor_says_only_the_next_attack_gets_it():
    """Necrobinder: "Akabeko's Vigor 8 was folded into every attack's printed
    number, like Gigantification, but this time with no note that only one
    card gets it." """
    state = _combat("Necrobinder", status=[
        {"name": "Vigor", "amount": 8, "type": "Buff",
         "description": "Your next Attack deals 8 additional damage."}])
    state["player"]["hand"] = [
        {"index": 0, "name": "Strike", "id": "STRIKE_NECROBINDER",
         "type": "Attack", "cost": "1", "can_play": True,
         "description": "Deal 14 damage."}]
    page = blindplay.observe(state)
    assert ("**Vigor** pays for ONE card: its own words are \"your next "
            "Attack deals\"") in page
    assert "only the first one you actually play gets it" in page


# ------------------------------------------ Silent: the poison it put on --

def test_what_a_card_did_names_the_poison_it_put_on():
    """Silent: "the 'what it did' list prints 'Nothing this page can count
    landed off it' for every poison card. The page never confirms that
    poison landed." The ledger now files the power a card put on a body."""
    state = _combat("Silent", resolutions=[
        {"card_id": "DEADLY_POISON", "card": "Deadly Poison",
         "auto_played": False, "carried": False, "overflowed": False,
         "hits": [], "summoned": [],
         "applied": [{"target": "Seapunk", "power": "Poison", "amount": 7,
                      "combat_id": "1"}]}])
    page = blindplay.observe(state)
    assert "- **Deadly Poison**" in page
    assert "  Put **Poison 7** on **Seapunk**." in page
    assert "Nothing this page can count landed off it" not in page


def test_a_power_taken_off_reads_as_taken_off():
    state = _combat("Ironclad", resolutions=[
        {"card_id": "TREMBLE", "card": "Tremble", "auto_played": False,
         "carried": False, "overflowed": False, "hits": [], "summoned": [],
         "applied": [{"target": "Seapunk", "power": "Artifact",
                      "amount": -1, "combat_id": "1"}]}])
    assert "  Took **Artifact 1** off **Seapunk**." in \
        blindplay.observe(state)
