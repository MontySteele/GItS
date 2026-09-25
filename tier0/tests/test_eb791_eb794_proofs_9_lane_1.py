"""The four defects proofs-9 lane 1 raised that were on no row.

The record is not on main yet -- it is on PR #586's branch -- so it is
retrieved the way CLAUDE.md sec."History retrieval" gives:
`git show fa7b516f:review/records/teyvat-proofs-9-lane1-2026-09-16.md`, its
section "Defects found that are not on any row above". Nothing measured here
is quotable (R215 B): these are shape assertions about a generator, a renderer
and a bridge.

  * `EB-791` A MODE CARD'S TITLE PRINTED ITS RAW MARKUP.
    `KLEEMOD-PROTO_FS_CURTAIN_RISE_MODE_B` sent
    `"[gold]Spend[/gold] 3: deal 13 instead"` as its NAME and the game drew
    that string, brackets and all, on the card in the chooser -- while the
    description an inch below rendered the same word in gold. A title is not
    rich text in this game and a description is. Invisible to a seat (the
    blind page strips tags), which is why three seat rounds walked past it.

  * `EB-792` THE INTENT CAVEAT CONTRADICTED THE LINE ABOVE IT. The page
    printed *"the game folded Strength into that: it is 12 on the move and 15
    after"* and then, at the foot of the same section, *"the feed carries no
    base, no modifier list and no breakdown"*. True before `EB-607`'s bridge
    half, false after it.

  * `EB-793` `master_deck` ROWS READ THIN on the deployed bridge -- `name`,
    `cost`, `star_cost`, `description` and nothing else. The SOURCE fix is
    `EB-789`'s (`#580`): `master_deck` shares `BuildPileCardList`, whose row
    goes through `BuildCardInfo` now, and the look was taken on a bridge dll
    built before it. So what is pinned here is the CALL SITE -- that the deck
    keeps sharing that builder rather than growing a thin one of its own --
    and the deploy plus a live look are what the row still owes.

  * `EB-794` THE REMOVAL GRID MARKED NO ROW. `select_card index=36` on the
    shop's removal grid answered "Toggling card selection: Kurage's Oath",
    `can_confirm` flipped, the confirm removed that card -- and no row carried
    `selected: true`, where the Smith's upgrade grid marks its row. The pick
    is armed on the SCREEN, not in the grid's paint list the bridge reads.
"""

from __future__ import annotations

import copy
import re
from pathlib import Path

from understudy import blindplay
from understudy.qa_packet import strip_markup

from tier0.tests.test_understudy_blindplay import combat_state

REPO = Path(__file__).resolve().parents[2]
BRIDGE = REPO / "vendor" / "STS2_MCP"
STATE_BUILDER = BRIDGE / "McpMod.StateBuilder.cs"
CARD_SELECTION = BRIDGE / "gits" / "GitsCardSelection.cs"
GENERATED = (REPO / "klee-mod" / "KleeCode" / "Cards")

#: `("title", "...")` inside a generated `Localization` initializer.
_TITLE = re.compile(r'\("title", "(.*?)"\),')
#: The game's closed rich-text tags, which a title must not carry.
_TAG = re.compile(r"\[/?[a-z0-9_]+(?:=[^\]]*)?\]")


# ------------------------------------- `EB-791`: the mode face's own title ---

def _mode_face_files() -> list[Path]:
    """Every generated file holding at least one `ModalOptionCard`."""
    files = [p for p in GENERATED.rglob("*.cs")
             if ": ModalOptionCard" in p.read_text(encoding="utf-8")]
    assert files, "no generated mode faces found; the glob moved"
    return files


def test_no_mode_face_title_carries_markup():
    """Seen to FAIL on seven faces across four cards, including the one a
    person read off the screen (proofs-9 lane 1)."""
    offenders: list[str] = []
    for path in _mode_face_files():
        text = path.read_text(encoding="utf-8")
        for block in text.split(": ModalOptionCard")[1:]:
            for title in _TITLE.findall(block):
                if _TAG.search(title):
                    offenders.append(f"{path.name}: {title}")
    assert not offenders, offenders


def test_the_description_keeps_its_markup():
    """The two halves are different questions and only one of them renders.
    Curtain Rise's mode B is the face the defect was read off."""
    text = (GENERATED / "Prototype" / "Generated"
            / "ProtoFsCurtainRise.cs").read_text(encoding="utf-8")
    mode_b = text[text.index("class ProtoFsCurtainRiseModeB"):]
    # 2026-09-25 (opus-furina-l2b): titled by its PRICE, with no number the
    # board folds -- see `test_furina_seat_fixes_2026_09_25`.
    assert '("title", "Spend 3"),' in mode_b
    assert '("description", "[gold]Spend[/gold] 3: deal ' in mode_b


def test_the_wire_contract_keeps_the_sheets_spelling():
    """`ModeLabels` is read by NAME off the played card's runtime type by
    `gits/GitsModalTargeting.cs` and matched against the sheet, so the labels
    there are the sheet's own -- the tags come off the TITLE and nowhere
    else."""
    text = (GENERATED / "Prototype" / "Generated"
            / "ProtoFsCurtainRise.cs").read_text(encoding="utf-8")
    labels = text[text.index("IReadOnlyList<string> ModeLabels"):]
    assert "[gold]Spend[/gold] 3: deal 13 instead" in labels[:400]


def test_the_stripper_is_the_pages_own():
    """One rule for what a tag is. The generator and the blind page
    disagreeing about that would be this defect one layer up."""
    assert strip_markup("[gold]Spend[/gold] 3") == "Spend 3"


# ------------------------------- `EB-792`: the caveat and the line above it ---

def _strength_attack(breakdown: dict | None) -> dict:
    """A board with one enemy wearing Strength and telegraphing an Attack,
    which is the only board the provenance note prints on."""
    state = copy.deepcopy(combat_state())
    base = state["battle"]["enemies"][0]
    intent = {"type": "Attack", "label": "15", "title": "Aggressive"}
    if breakdown is not None:
        intent["breakdown"] = breakdown
    enemy = dict(base,
                 status=[{"title": "Strength", "name": "Strength",
                          "amount": 3, "type": "Buff",
                          "description": "Deals additional damage."}],
                 intents=[intent])
    state["battle"] = dict(state["battle"], enemies=[enemy])
    return state


def test_a_board_with_a_breakdown_stops_denying_it_has_one():
    """Seen to FAIL: the page named the base, the folded figure and the model
    it folded, then said the feed carried none of the three."""
    blindplay.forget_fight()
    page = blindplay.observe(_strength_attack(
        {"base_damage": 12, "folded_damage": 15, "repeats": 1,
         "total_damage": 15, "modifiers": ["Strength"]}))
    assert "it is 12 on the move and 15 after" in page
    assert "no base, no modifier list and no breakdown" not in page
    assert blindplay.INTENT_SOURCE_NOTE_BREAKDOWN in page


def test_a_bridge_older_than_eb607_reads_exactly_as_before():
    """No breakdown on the feed, and the sentence that was written for that
    feed is the one printed."""
    blindplay.forget_fight()
    page = blindplay.observe(_strength_attack(None))
    assert blindplay.INTENT_SOURCE_NOTE in page
    assert "no base, no modifier list and no breakdown" in page


def test_the_provenance_half_is_the_same_sentence_either_way():
    """Only the closing clause moves: the figure is the game's and this page
    does no arithmetic on it, on every board."""
    head = "this page has no second source for it and does no arithmetic on it"
    assert head in blindplay.INTENT_SOURCE_NOTE
    assert head in blindplay.INTENT_SOURCE_NOTE_BREAKDOWN


# --------------------------------------- `EB-793`: the deck's own row shape ---

def test_the_master_deck_shares_the_piles_row_builder():
    """`EB-789` routed every pile row through the hand's `BuildCardInfo`; the
    deck is the fourth caller of that builder and the pin is that it stays
    one. A thin builder of its own here is the defect proofs-9 read."""
    text = STATE_BUILDER.read_text(encoding="utf-8")
    call = text[text.index('state["master_deck"]'):]
    assert "BuildPileCardList(" in call[:200]
    assert "player.Deck.Cards, PileType.Deck" in call[:200]


def test_the_page_reads_the_four_fields_off_a_deck_row():
    """The reader half, on a `master_deck` row in the shape that builder
    sends: id, upgrade flag, keywords and enchantment are all asked for."""
    from understudy import blindplay_faces
    row = {"id": "KLEEMOD-GUARD", "name": "Guard+", "cost": "1",
           "star_cost": None, "description": "Gain 8 Block.",
           "type": "Skill", "rarity": "Common", "is_upgraded": True,
           "keywords": ["Retain"], "pile": "Deck",
           "enchantment": {"id": "SHARP", "name": "Sharp", "amount": 2,
                           "shows_amount": True,
                           "description": "Gain 2 more Block."}}
    card = blindplay_faces._deck_card(row)
    assert card["upgraded"] is True
    assert card["key"] == "GUARD"
    assert card["enchantment"]["name"] == "Sharp"


# ------------------------------------- `EB-794`: where a pick is armed, live ---

def _selection_source() -> str:
    """`GitsSelectedCards` and the helpers under it, as source. The C# is not
    reachable from pytest and "the second source quietly went away" is exactly
    the structurally-invisible shape a live look had to catch by eye."""
    return CARD_SELECTION.read_text(encoding="utf-8")


def test_the_selection_read_asks_the_screen_as_well_as_the_grid():
    """Seen to FAIL: the grid's paint list was the only source, so the removal
    screen -- which arms its pick on the screen -- marked no row at all."""
    text = _selection_source()
    body = text[text.index("GitsSelectedCards(Node? screen)"):]
    assert "GitsAddScreenSelection(screen, selected);" in body[:900]
    assert "GItS LOCAL ADDITION" in text       # the vendor-pin lint's rule


def test_the_screen_fields_are_matched_by_name_and_not_by_type():
    """A screen holds `CardModel`s that are not a pick -- the row under the
    cursor, a preview clone -- and reporting one of those as armed is worse
    than the silence this replaces."""
    text = _selection_source()
    rule = text[text.index("GitsNamesASelection(string name)"):]
    assert '"select", StringComparison.OrdinalIgnoreCase' in rule[:400]
    assert '"chosen", StringComparison.OrdinalIgnoreCase' in rule[:400]


def test_a_failed_grid_read_is_still_null_and_not_a_guess():
    """`selection_known` means "the grid could be asked". An empty screen
    field is not evidence that nothing is picked, so the union never turns a
    null into a false."""
    body = _selection_source()
    head = body[body.index("GitsSelectedCards(Node? screen)"):]
    head = head[:head.index("GitsAddScreenSelection")]
    assert "if (field == null) return null;" in head
    assert "if (grid == null) return null;" in head


def test_the_screen_walk_cannot_take_the_read_down():
    """Every failure here adds nothing rather than losing the grid's own
    answer -- `GitsResources`' discipline, kept."""
    text = _selection_source()
    body = text[text.index("GitsAddScreenSelection("):]
    assert "catch (Exception)" in body[:1400]
