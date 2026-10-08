"""The shop hid a card's Spark price (Klee suite 4, 2026-10-07).

THE FIND. The shop printed Klee's *Explosive Spark* -- 0 Energy and 1 Spark --
as `cost 0`, while the same card in hand wore its Spark badge.

THE CAUSE. Off a hand, the page's only source for a Spark price was
`qa_packet.spark_price_for`, an index read from THIS checkout's `klee-mod`
sources. The seats run the page from `main` and the game runs `klee-next`, so
a card that exists only on `klee-next` had no row and printed no Spark. The
bridge knew the price (`SparkCost.PriceOf`, the badge's own number) but put
it on a HAND card only (`BuildCardState`).

THE FIX. The bridge puts `spark_price` on every card row `BuildCardInfo`
builds (rewards, choosers, previews, piles) and `card_spark_price` on a shop
shelf; the page falls back to it where the index has no row. The card id used
below is deliberately one no branch defines, so the pin stays a test of the
fallback after `klee-next` reaches `main`.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about a bridge
and a renderer.
"""

from __future__ import annotations

from pathlib import Path

from understudy import blindplay, blindplay_faces, qa_packet

BRIDGE = Path(__file__).resolve().parents[2] / "vendor" / "STS2_MCP"
STATE_BUILDER = BRIDGE / "McpMod.StateBuilder.cs"

#: An id no `klee-mod` tree defines: the index answers nothing for it.
UNKNOWN_ID = "KLEEMOD-PROTO_KO_NOT_IN_THIS_CHECKOUT"


def _body(start_marker: str) -> str:
    text = STATE_BUILDER.read_text(encoding="utf-8")
    start = text.index(start_marker)
    return text[start:text.index("private static", start + 1)]


def _player() -> dict:
    return {"character": "Klee", "hp": 60, "max_hp": 75, "gold": 120,
            "status": [], "potions": [], "relics": [], "max_potion_slots": 3}


def test_the_index_has_no_row_for_the_fixture_card():
    assert qa_packet.spark_price_for(UNKNOWN_ID, False) is None


# ------------------------------------------------------------ the bridge ---

def test_every_card_row_carries_the_spark_price():
    """Seen to FAIL: `spark_price` was written in `BuildCardState` only."""
    body = _body("Dictionary<string, object?> BuildCardInfo(CardModel card")
    assert 'info["spark_price"] = sparkPrice' in body
    assert "GItS LOCAL EDIT (the shop Spark price" in body
    # The bank half stays on the hand: there is no bank off a fight.
    assert 'info["spark_affordable"]' not in body


def test_a_shop_shelf_carries_the_spark_price():
    body = _body("Dictionary<string, object?> BuildShopState(")
    assert 'item["card_spark_price"] = shelfSpark' in body


# -------------------------------------------------------------- the page ---

def test_a_shop_shelf_prints_the_wire_spark_price_the_index_lacks():
    """Seen to FAIL: the shelf printed `cost 0` for a 0 Energy + 1 Spark card."""
    blindplay_faces.forget_shelves()
    state = {"state_type": "shop", "player": _player(),
             "shop": {"can_proceed": True, "items": [
                 {"index": 0, "category": "card", "price": 52,
                  "is_stocked": True, "can_afford": True, "on_sale": False,
                  "card_id": UNKNOWN_ID, "card_name": "Explosive Spark",
                  "card_type": "Attack", "card_cost": "0",
                  "card_spark_price": 1, "card_rarity": "Common",
                  "card_description": "Deal 9 Pyro damage."}]}}
    page = blindplay.observe(state)
    assert "**Explosive Spark** — cost 1 Spark, card (attack), 52 gold" in page


def test_a_card_reward_prints_the_wire_spark_price_the_index_lacks():
    card = {"index": 0, "id": UNKNOWN_ID, "name": "Explosive Spark",
            "type": "Attack", "cost": "0", "spark_price": 1,
            "rarity": "Common", "description": "Deal 9 Pyro damage."}
    state = {"state_type": "card_reward",
             "card_reward": {"cards": [card], "can_skip": True},
             "run": {"act": 1, "floor": 2, "ascension": 0},
             "player": _player()}
    page = blindplay.observe(state)
    assert "cost 1 Spark" in page
    assert "cost 0" not in page


def test_a_chooser_prints_the_wire_spark_price_the_index_lacks():
    card = {"index": 0, "id": UNKNOWN_ID, "name": "Explosive Spark",
            "type": "Attack", "cost": "0", "spark_price": 2,
            "description": "Deal 9 Pyro damage."}
    state = {"state_type": "card_select", "player": _player(),
             "card_select": {"screen_type": "simple_select",
                             "prompt": "Choose a card to remove.",
                             "can_skip": True, "can_confirm": False,
                             "cards": [card]}}
    assert "cost 2 Sparks" in blindplay.observe(state)


def test_a_card_with_no_price_anywhere_still_reads_its_energy_cost():
    blindplay_faces.forget_shelves()
    state = {"state_type": "shop", "player": _player(),
             "shop": {"can_proceed": True, "items": [
                 {"index": 0, "category": "card", "price": 52,
                  "is_stocked": True, "can_afford": True, "on_sale": False,
                  "card_id": UNKNOWN_ID, "card_name": "Plain Card",
                  "card_type": "Skill", "card_cost": "1",
                  "card_rarity": "Common",
                  "card_description": "Gain 5 Block."}]}}
    assert "**Plain Card** — cost 1, card (skill), 52 gold" in \
        blindplay.observe(state)
