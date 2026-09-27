"""The base-game Regent control seat of 2026-09-26: the page's own defects it
found. The bridge already sent the star total and every card's star cost; the
page dropped both, so the seat learned each cost by being refused.

Record: the main checkout's
`review/qa/seats-2026-09-26/control-regent-lane2.md` (gitignored).
"""

from __future__ import annotations

from pathlib import Path

from understudy import blindplay, blindplay_faces, qa_packet

REPO = Path(__file__).resolve().parents[2]

FALLING_STAR = {"index": 0, "id": "FALLING_STAR", "name": "Falling Star",
                "type": "Attack", "cost": "0", "star_cost": "2",
                "description": "Deal 7 damage. Apply 1 Weak and 1 Vulnerable.",
                "target_type": "AnyEnemy", "can_play": True}
CRESCENT_SPEAR = {"index": 1, "id": "CRESCENT_SPEAR",
                  "name": "Crescent Spear", "type": "Attack", "cost": "1",
                  "star_cost": "1", "description": "Deal 14 damage.",
                  "target_type": "AnyEnemy", "can_play": True}
STRIKE = {"index": 2, "id": "STRIKE_REGENT", "name": "Strike",
          "type": "Attack", "cost": "1", "star_cost": None,
          "description": "Deal 6 damage.", "target_type": "AnyEnemy",
          "can_play": True}
DAZED = {"name": "Dazed", "type": "Status", "cost": "-1", "star_cost": None,
         "description": "Unplayable. Ethereal."}


def _combat(hand=(), status=(), **player) -> dict:
    state = {"state_type": "monster",
             "player": {"character": "Regent", "hp": 60, "max_hp": 75,
                        "block": 0, "energy": 3, "max_energy": 3,
                        "hand": list(hand), "potions": [], "relics": [],
                        "status": list(status), "draw_pile_count": 5,
                        "discard_pile_count": 0, "exhaust_pile_count": 0},
             "battle": {"round": 2, "enemies": [
                 {"entity_id": "HAUNTED_SHIP", "combat_id": 1,
                  "name": "Haunted Ship", "hp": 40, "max_hp": 63,
                  "block": 0, "intents": [{"type": "Attack", "damage": 5}],
                  "status": []}]}}
    state["player"].update(player)
    return state


def _short(card: dict) -> dict:
    return dict(card, can_play=False, unplayable_reason="StarCostTooHigh")


# ------------------------------------------------------ 1. the star total --

def test_the_star_total_prints_beside_energy():
    """"The battle screen never printed my star count", all run."""
    page = blindplay.observe(_combat(stars=3))
    assert "- Energy 3/3\n- Stars 3\n" in page


def test_a_zero_star_total_still_prints_when_the_wire_sends_it():
    assert "- Stars 0" in blindplay.observe(_combat(stars=0))


def test_no_star_line_where_the_wire_sends_no_stars():
    page = blindplay.observe(_combat())
    assert "Stars" not in page.split("## Your hand")[0]


def test_star_next_turn_keeps_its_row_beside_the_total():
    nxt = {"id": "STAR_NEXT_TURN_POWER", "name": "Star Next Turn",
           "amount": 3, "type": "Buff",
           "description": "Next turn, gain 3 Stars."}
    page = blindplay.observe(_combat(stars=1, status=[nxt]))
    assert "- Stars 1" in page
    assert "- Star Next Turn 3 (buff)" in page


# ------------------------------------------------------- 2. star costs --

def test_a_hand_card_prints_its_star_cost():
    """"Falling Star, Astral Pulse, Crescent Spear ... all print 'cost 0' or
    'cost 1' and are then refused for stars." """
    page = blindplay.observe(_combat([FALLING_STAR, CRESCENT_SPEAR, STRIKE],
                                     stars=3))
    assert "**Falling Star** — cost 2 Stars, attack" in page
    assert "**Crescent Spear** — cost 1 and 1 Star, attack" in page
    assert "**Strike** — cost 1, attack" in page


def test_an_x_star_cost_prints_as_x():
    assert qa_packet.cost_label({"cost": "0", "star_cost": "X"}) == "X Stars"


def test_an_absent_or_null_star_cost_prints_nothing():
    assert qa_packet.cost_label({"cost": "1", "star_cost": None}) == "1"
    assert qa_packet.cost_label({"cost": "1"}) == "1"


def test_a_reward_card_prints_its_star_cost():
    state = {"state_type": "card_reward",
             "card_reward": {"cards": [dict(FALLING_STAR, rarity="Common")],
                             "can_skip": True},
             "run": {"act": 1, "floor": 2, "ascension": 0},
             "player": {"character": "Regent", "hp": 60, "max_hp": 75,
                        "status": [], "potions": [], "relics": []}}
    assert "cost 2 Stars" in blindplay.observe(state)


def test_a_shop_card_prints_its_star_cost():
    blindplay_faces.forget_shelves()
    state = {"state_type": "shop",
             "player": {"character": "Regent", "hp": 60, "max_hp": 75,
                        "gold": 120},
             "shop": {"can_proceed": True, "items": [
                 {"index": 0, "category": "card", "price": 75,
                  "is_stocked": True, "can_afford": True, "on_sale": False,
                  "card_id": "GAMMA_BLAST", "card_name": "Gamma Blast",
                  "card_type": "Attack", "card_cost": "0",
                  "card_star_cost": "3", "card_rarity": "Uncommon",
                  "card_description": "Deal 13 damage."}]}}
    assert "**Gamma Blast** — cost 3 Stars, card (attack), 75 gold" in \
        blindplay.observe(state)


def test_a_chooser_card_prints_its_star_cost():
    state = {"state_type": "card_select",
             "player": {"character": "Regent", "potions": [], "relics": [],
                        "max_potion_slots": 3},
             "card_select": {"screen_type": "simple_select",
                             "prompt": "Choose a card.", "can_skip": True,
                             "can_confirm": False,
                             "cards": [FALLING_STAR]}}
    assert "cost 2 Stars" in blindplay.observe(state)


def _smith(**extra) -> dict:
    card = dict({"index": 0, "name": "Gamma Blast", "id": "GAMMA_BLAST",
                 "description": "Deal 13 damage.", "type": "Attack",
                 "cost": "0", "star_cost": "3"}, **extra)
    return {"state_type": "card_select",
            "player": {"character": "Regent", "potions": [], "relics": [],
                       "max_potion_slots": 3},
            "card_select": {"screen_type": "upgrade",
                            "prompt": "Choose a card to upgrade.",
                            "can_skip": True, "preview_showing": False,
                            "can_confirm": False, "selection_known": True,
                            "cards": [card]}}


def test_the_upgrade_grid_prints_the_star_cost_and_the_upgraded_one():
    """The rest-site Smith is the game's `FromDeckForUpgrade`, the same
    `NDeckUpgradeSelectScreen` the upgraded face rides on; the star half of
    the upgraded cost now rides with it."""
    page = blindplay.observe(_smith(upgraded_description="Deal 18 damage.",
                                    upgraded_cost="0",
                                    upgraded_star_cost="2"))
    assert "**Gamma Blast** — cost 3 Stars, attack" in page
    assert "Upgraded: cost 2 Stars — Deal 18 damage." in page


def test_an_upgrade_that_leaves_the_stars_prints_no_cost():
    page = blindplay.observe(_smith(upgraded_description="Deal 18 damage.",
                                    upgraded_cost="0",
                                    upgraded_star_cost="3"))
    assert "Upgraded: Deal 18 damage." in page


def test_the_bridge_sends_the_upgraded_star_cost():
    src = (REPO / "vendor" / "STS2_MCP"
           / "McpMod.StateBuilder.cs").read_text(encoding="utf-8")
    assert 'info["upgraded_star_cost"] = GetStarCostDisplay(preview);' in src


# ------------------------------------------ 6. the star refusal's numbers --

def test_a_star_short_card_says_how_many_stars():
    """Knockout Blow+ then Decisions refused: "with the star total invisible,
    I cannot tell which." The refusal carries both numbers now."""
    page = blindplay.observe(_combat([_short(FALLING_STAR)], stars=1))
    assert "CANNOT BE PLAYED: not enough Stars (have 1, need 2)" in page


def test_the_play_refusal_says_how_many_stars():
    state = _combat([_short(FALLING_STAR)], stars=1)
    res = blindplay.act(state, 'play "Falling Star" on "Haunted Ship"')
    assert "not enough Stars (have 1, need 2)" in res["refusal"]


def test_an_absent_star_total_on_a_refusal_is_zero():
    page = blindplay.observe(_combat([_short(FALLING_STAR)]))
    assert "not enough Stars (have 0, need 2)" in page


def test_an_energy_refusal_is_unchanged():
    assert qa_packet.unplayable_reason("EnergyCostTooHigh", 3, "2") == \
        "you do not have enough energy"


# ---------------------------------------------- 4. Shrink's applier name --

def test_the_shrink_row_branches_on_the_applier_like_the_game():
    """"While is alive, you deal 30% less damage": Beetle Juice on an enemy.
    `ApplierName` is filled only for a monster applier, and the game's own
    row branches on it; ours did not."""
    mod = (REPO / "klee-mod" / "KleeCode" / "KleeMod.cs").read_text(
        encoding="utf-8")
    assert "{ApplierName.StringValue:cond:While {} is alive, " in mod
    assert "\"While {ApplierName} is alive" not in mod


def test_the_shrink_gloss_names_both_ways_it_ends():
    from understudy.blindplay_notes import BASE_KEYWORDS
    gloss = BASE_KEYWORDS["Shrink"]
    assert "while whoever applied it is alive" in gloss
    assert "number of turns runs out" in gloss


# ------------------------------------------ 5. where Status cards went --

def test_the_pile_line_names_the_status_cards_in_each_pile():
    """Haunted Ship "give you 5 Status cards", "but none ever appeared". The
    game puts them in the discard pile (`HauntedShip`, `PileType.Discard`)."""
    page = blindplay.observe(_combat(
        discard_pile_count=6, discard_pile=[DAZED] * 5 + [STRIKE],
        draw_pile_count=2, draw_pile=[DAZED, STRIKE]))
    assert ("- Piles: 2 in the draw pile (1 Dazed), 6 discarded (5 Dazed), "
            "0 exhausted") in page


def test_a_pile_with_no_status_cards_reads_as_before():
    page = blindplay.observe(_combat(discard_pile=[STRIKE],
                                     discard_pile_count=1))
    assert "- Piles: 5 in the draw pile, 1 discarded, 0 exhausted" in page
