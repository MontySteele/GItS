"""`EB-789`: a card in a pile and the same card in hand were two cards.

THE FIND (live look 8c, `#575`). An enchanted card sat in the draw pile reading
*Gain 5 Block*, was drawn, and read *Gain 7 Block* in hand a turn later.
Nothing had changed but the pile it was in.

TWO CAUSES, ONE SITE. `McpMod.StateBuilder.BuildPileCardList` built a
deliberate four-key row of its own -- `name`, `cost`, `star_cost`,
`description` -- beside `BuildCardInfo` rather than through it. So (1) no pile
row carried the `enchantment` block `EB-181` added to `BuildCardInfo`, nor
`id`, `is_upgraded` or `keywords`; and (2) its `description` was
`GetDescriptionForPile(<that pile>)` where the hand's is the `Hand` face, and
only the hand face folds the enchantment's number into the printed sentence.

The same builder feeds `master_deck` (`EB-447`), so both defects rode into
every deck list this page prints outside a fight --
`blindplay_faces._deck_card` has been asking every pile row for `id` and
`is_upgraded` since that row, and no pile row has ever carried either.

WHAT IS PINNED HERE. The bridge half is a SOURCE assertion, because the C# is
not reachable from pytest and "the pile row quietly grew its own key list
again" is exactly the structurally-invisible shape a live look had to catch by
eye the first time. The page half is the ordinary kind: a wire-shaped fixture
in, a printed page out.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about a bridge
and a renderer.
"""

from __future__ import annotations

import copy
import re
from pathlib import Path

import pytest

from understudy import blindplay, blindplay_board, blindplay_faces

from tier0.tests.test_understudy_blindplay import map_state

BRIDGE = Path(__file__).resolve().parents[2] / "vendor" / "STS2_MCP"
STATE_BUILDER = BRIDGE / "McpMod.StateBuilder.cs"
PILE_CARD = BRIDGE / "gits" / "GitsPileCard.cs"


@pytest.fixture(autouse=True)
def _clean_deck_store():
    """The deck memory is on disk and per lane (`EB-447`)."""
    blindplay_faces.forget_deck()
    yield
    blindplay_faces.forget_deck()


# ------------------------------------------------------------ the bridge ---

def _build_pile_card_list() -> str:
    """The body of `BuildPileCardList`, as source."""
    text = STATE_BUILDER.read_text(encoding="utf-8")
    start = text.index("BuildPileCardList(IEnumerable<CardModel> cards")
    return text[start:text.index("private static", start + 1)]


def test_the_pile_row_goes_through_the_hands_own_builder():
    """Seen to FAIL: the loop built `{name, cost, star_cost, description}` of
    its own, which is the whole defect -- two key lists for one card."""
    body = _build_pile_card_list()
    assert "GitsPileCardRow(card, pile)" in body
    assert "GItS LOCAL EDIT (`EB-789`)" in body
    # The four-key literal is gone rather than shadowed by the new call.
    assert '["star_cost"] = GetStarCostDisplay(card)' not in body


def test_the_gits_block_asks_for_the_hand_face():
    """`BuildCardInfo` for the keys, and the HAND pile for the sentence: the
    face the card will present when it is played is the only face a reader
    planning off the draw pile can use."""
    assert PILE_CARD.is_file()
    text = PILE_CARD.read_text(encoding="utf-8")
    assert "GItS LOCAL ADDITION" in text          # the vendor-pin lint's rule
    row = text[text.index("GitsPileCardRow("):]
    assert "BuildCardInfo(card)" in row
    assert 'info["description"] = SafeGetCardDescription(card);' in row
    # And the pile's own sentence is kept rather than dropped, under a key of
    # its own and only where it says something different.
    assert 'info["pile_description"] = pileText;' in row


def test_the_wire_grew_keys_and_renamed_none():
    """Backward compatibility is the row's own constraint: a page older than
    this change reads the four keys it always read, spelled the same. All four
    come off `BuildCardInfo`, which is what makes the swap additive."""
    text = STATE_BUILDER.read_text(encoding="utf-8")
    start = text.index("BuildCardInfo(CardModel card, PileType pile")
    info = text[start:text.index("/// <summary>", start)]
    for key in ("name", "cost", "star_cost", "description"):
        assert f'["{key}"]' in info


# -------------------------------------------------------------- the page ---

def _pile_row(name: str, description: str, *, card_id: str | None = None,
              upgraded: bool = False,
              enchantment: dict | None = None) -> dict:
    """One pile row in the shape `BuildPileCardList` sends since `EB-789`."""
    row = {"id": card_id or re.sub(r"[^a-z]+", "_", name.lower()).strip("_"),
           "name": name,
           "type": "Skill",
           "cost": "1",
           "star_cost": None,
           "description": description,
           "rarity": "Common",
           "is_upgraded": upgraded,
           "keywords": [],
           "pile": "Draw"}
    if enchantment:
        row["enchantment"] = enchantment
    return row


SHARP = {"id": "SHARP", "name": "Sharp", "description": "Gain 2 more Block.",
         "amount": 2, "shows_amount": True}


def _map_with_deck(rows: list[dict]) -> dict:
    """A map screen whose lane store holds a deck read off `master_deck`."""
    state = copy.deepcopy(map_state())
    state["player"]["character"] = "Klee"
    state["player"]["master_deck"] = rows
    return state


def test_the_enchanted_copy_is_not_the_plain_one():
    """Seen to FAIL: two copies of one title folded into one row, because a
    pile row carried no enchantment at all -- so the deck list said `Guard x 2`
    over a deck holding a Sharp copy and a plain one."""
    state = _map_with_deck([
        _pile_row("Guard", "Gain 5 Block."),
        _pile_row("Guard", "Gain 7 Block.", enchantment=SHARP)])
    blindplay_faces.remember_deck(state)
    titles = [c["title"] for c in blindplay_board.deck_titles(state)]
    assert "Guard" in titles
    assert "Guard (Sharp 2)" in titles


def test_the_pile_prints_the_enchanted_sentence():
    """The bridge sends the HAND face on a pile row now, so the text the page
    carries for a card in the draw pile is the text it will read in hand."""
    state = _map_with_deck([_pile_row("Guard", "Gain 7 Block.",
                                      enchantment=SHARP)])
    face = blindplay_faces._card_face(state["player"]["master_deck"][0])
    assert face["text"] == "Gain 7 Block."
    assert face["enchantment"] == {"name": "Sharp", "text": "Gain 2 more Block.",
                                   "amount": 2}


def test_a_pile_and_a_hand_row_of_one_card_are_one_face():
    """The acceptance, stated as a page assertion: the same card, read out of
    the draw pile and out of the hand, prints the same face."""
    pile = _pile_row("Guard", "Gain 7 Block.", enchantment=SHARP)
    hand = dict(pile, index=0, can_play=True, target_type="None")
    hand.pop("pile")
    a, b = blindplay_faces._card_face(pile), blindplay_faces._card_face(hand)
    for key in ("title", "text", "kind", "upgraded", "enchantment"):
        assert a[key] == b[key]


def test_the_deck_memory_reads_the_id_and_the_upgrade_flag():
    """`_deck_card` has asked every pile row for `id` and `is_upgraded` since
    `EB-447` and no pile row carried either; it fell back to the `+` on the
    title, which is a mark the game does not always print."""
    card = blindplay_faces._deck_card(
        _pile_row("Guard", "Gain 8 Block.", card_id="klee_guard",
                  upgraded=True))
    assert card["upgraded"] is True
    assert card["key"]
    assert card["enchantment"] is None       # asked, and there is none


def test_an_older_bridge_folds_exactly_as_it_did():
    """A bridge predating this row sends the four thin keys and no more. The
    list it produces is the list it always produced."""
    thin = [{"name": "Guard", "cost": "1", "description": "Gain 5 Block."},
            {"name": "Guard", "cost": "1", "description": "Gain 5 Block."}]
    state = _map_with_deck(thin)
    blindplay_faces.remember_deck(state)
    assert blindplay_board.deck_titles(state) == [{"title": "Guard",
                                                   "count": 2}]
    page = blindplay.observe(state)
    assert "- **Guard** × 2" in page
