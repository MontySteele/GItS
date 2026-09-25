"""Furina, the Stage -- the opus-furina-l2b seat's findings, 2026-09-25.

The record is `review/qa/blindplay/opus-furina-l2b-2026-09-25.md`, sec. "The
kit, after 5 fights", (c). This file pins the PAGE and the CODEGEN halves; the
mod halves are pinned in `klee-mod/KleeTests` (`ModalChoicePinTests`,
`FurinaStageLegibilityTests`, `FurinaStageSeatFixTests`).

  1. A Rapt Audience's face said "on the back performer" and did nothing with
     the Usher alone. The face now says it needs 2 or more performers.
  2. The mode chooser opened with one row when the Spend mode was refused,
     printed every row as "cost 0, skill", and titled a row with the written
     number over a body printing the board's ("Deal 7 damage" / "Deal 5
     damage" under Weak). And the page never said the open chooser refuses
     every other command, which cost the seat two refusals in a row.
  3. The Stage badge never said how many seats there are.
  4. The stage log filed no Raise and no hit on the lead that did not empty
     it, so every Fanfare change was reconstructed by arithmetic.
  5. A lone Gas Bomb printed as "Gas Bomb (2)" (`test_understudy_blindplay`'s
     numbering pins carry that half).

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from understudy import blindplay
from understudy.blindplay_notes import (ARM_KEYWORDS, CHOOSER_ONE_CHOICE_NOTE,
                                        MODE_CHOOSER_PROMPT,
                                        RESOLUTION_NO_HITS,
                                        RESOLUTION_NO_HITS_STAGE, STAGE_ACTS)
from understudy.blindplay_render import _render_stage_log, _resolution_lines

REPO = Path(__file__).resolve().parents[2]
GENERATED = REPO / "klee-mod" / "KleeCode" / "Cards" / "Prototype" / "Generated"


@pytest.fixture(autouse=True)
def _fresh_fight():
    blindplay.forget_fight()
    yield
    blindplay.forget_fight()


# ---------------------------------------------------------------------------
# 1. A RAPT AUDIENCE SAYS IT NEEDS A SECOND PERFORMER.
# ---------------------------------------------------------------------------

def _surface_row(row_id: str) -> dict:
    rows = yaml.safe_load((REPO / "docs" / "prototype-surface.yaml")
                          .read_text(encoding="utf-8"))
    return next(r for r in rows if r.get("id") == row_id)


def test_a_rapt_audience_face_says_it_needs_two_performers():
    face = _surface_row("proto_fs_rapt_audience")["description"]
    # The text pass (2026-09-25) shortened the clause, and kept it.
    assert face.endswith(" Needs 2 performers.")
    # The follow-up dropped "rounded up" from both variants.
    assert "rounded up" not in face
    emitted = (GENERATED / "ProtoFsRaptAudience.cs").read_text(
        encoding="utf-8")
    assert "Needs 2 performers." in emitted


# ---------------------------------------------------------------------------
# 2. THE MODE CHOOSER.
# ---------------------------------------------------------------------------

SPEND_CARDS = ("ProtoFsCurtainRise", "ProtoFsQuickCue", "ProtoFsTidalFlourish",
               "ProtoFsInterposition", "ProtoFsGrandEntrance")


def _mode_classes(stem: str) -> dict[str, str]:
    text = (GENERATED / f"{stem}.cs").read_text(encoding="utf-8")
    out = {}
    for letter in "AB":
        start = text.index(f"class {stem}Mode{letter}")
        end = text.find("public sealed class", start + 1)
        out[letter] = text[start:end if end > 0 else None]
    return out


@pytest.mark.parametrize("stem", SPEND_CARDS)
def test_a_spend_cards_mode_titles_print_no_number(stem):
    """Under Weak the title read the written number and the body the board's.
    A title cannot fold, so it carries none: the plain mode is its own face
    with the figure taken out, the Spend mode is its price."""
    for letter, body in _mode_classes(stem).items():
        title = re.search(r'\("title", "([^"]*)"\)', body).group(1)
        if letter == "B":
            assert re.fullmatch(r"Spend \d+", title), title
        else:
            assert not re.search(r"\d", title), title


@pytest.mark.parametrize("stem", SPEND_CARDS)
def test_a_spend_cards_modes_wear_the_parents_type_and_no_orb(stem):
    """`ModalOptionCard(CardType)`: cost -1 (the orb hidden the base game's
    way) and the parent's type, instead of "cost 0, Skill"."""
    text = (GENERATED / f"{stem}.cs").read_text(encoding="utf-8")
    parent = re.search(r": base\(\d+, (CardType\.\w+),", text).group(1)
    for body in _mode_classes(stem).values():
        assert f": base({parent})" in body


def test_a_modal_card_with_no_rule_gate_keeps_its_bytes():
    """The shipped `deep_breath` has meter prices and no rule gate: its
    options keep their authored titles and the parameterless base."""
    text = (REPO / "klee-mod" / "KleeCode" / "Cards" / "Furina" / "Generated"
            / "DeepBreath.cs").read_text(encoding="utf-8")
    assert ": base(CardType." not in text
    assert '("title", "Spend 3 Encore: draw 3 cards")' in text


def _mode_chooser_state() -> dict:
    """SYNTHETIC, in `BuildChooseCardState`'s shape, with the two mode faces
    Curtain Rise opens under Weak."""
    def face(index, letter, title, text):
        return {"index": index,
                "id": f"KLEEMOD-PROTO_FS_CURTAIN_RISE_MODE_{letter}",
                "name": title, "description": text, "cost": "0",
                "type": "Attack", "card_type": "Attack"}
    return {"state_type": "card_select",
            "player": {"character": "furina", "potions": [], "relics": [],
                       "max_potion_slots": 3},
            "card_select": {"screen_type": "choose",
                            "prompt": "Choose a card.",
                            "can_skip": False, "can_cancel": False,
                            "preview_showing": False, "can_confirm": False,
                            "selection_known": True,
                            "cards": [face(0, "A", "Deal damage",
                                           "Deal 5 damage"),
                                      face(1, "B", "Spend 3",
                                           "Spend 3: deal 10 instead")]}}


def test_a_mode_row_prints_no_cost_and_no_type():
    page = blindplay.observe(_mode_chooser_state())
    assert "- **Deal damage**\n" in page
    assert "- **Spend 3**\n" in page
    assert "cost 0" not in page
    assert "— attack" not in page and "— skill" not in page


def test_a_mode_chooser_says_what_it_is_asking():
    page = blindplay.observe(_mode_chooser_state())
    assert f"# {MODE_CHOOSER_PROMPT}" in page
    assert "# Choose a card." not in page


def test_a_card_chooser_keeps_its_cost_line_and_prompt():
    """Discovery's screen is the same one-press chooser holding REAL cards:
    their cost and type are the card's, and they stay."""
    state = _mode_chooser_state()
    for card in state["card_select"]["cards"]:
        card["id"] = "KLEEMOD-SOME_REAL_CARD"
    page = blindplay.observe(state)
    assert "cost 0" in page
    assert "# Choose a card." in page


def test_the_one_press_note_says_everything_else_is_refused():
    """The seat chained `play` and `end turn` behind an open chooser: two
    refusals in a row. The note said how to answer and never that nothing
    else is taken until then."""
    assert "every other command" in CHOOSER_ONE_CHOICE_NOTE
    assert "`end turn` included, is refused" in CHOOSER_ONE_CHOICE_NOTE
    assert "`confirm`" not in CHOOSER_ONE_CHOICE_NOTE
    page = blindplay.observe(_mode_chooser_state())
    assert CHOOSER_ONE_CHOICE_NOTE in page


# ---------------------------------------------------------------------------
# 3. THE SEAT COUNT.
# ---------------------------------------------------------------------------

def test_the_glossary_says_up_to_three_perform():
    assert STAGE_ACTS.startswith("Up to 3 performers act at the end of your "
                                 "turn")
    assert ARM_KEYWORDS["front performer"].endswith(STAGE_ACTS)
    assert ARM_KEYWORDS["back performer"].endswith(STAGE_ACTS)


def test_the_stage_badge_interpolates_the_law():
    src = (REPO / "klee-mod" / "KleeCode" / "Powers" / "Prototype"
           / "FurinaStageBadges.cs").read_text(encoding="utf-8")
    assert '"Up to " + FurinaStageLaw.Seats + " performers act' in src


# ---------------------------------------------------------------------------
# 4. THE STAGE LOG FILES RAISES AND HITS.
# ---------------------------------------------------------------------------

def _beat(event, member, name, bar, moved, reason="", target=""):
    from understudy.blindplay_board import (STAGE_LEAVE_REASONS,
                                            STAGE_LEFT_UNSAID)
    return {"event": event, "member": member, "name": name, "seat": 0,
            "fanfare": bar, "moved": moved,
            "why": STAGE_LEAVE_REASONS.get(reason, STAGE_LEFT_UNSAID),
            "target": target, "combat_id": "", "each": None}


def _log(*rows):
    return _render_stage_log({"seats": [], "log": list(rows)})


def test_a_raise_prints_what_landed_and_the_bar_either_side():
    lines = _log(_beat("raise", "usher", "Usher", 8, 5))
    # The text pass: "Raise N on X: a → b" became "X gains N Fanfare".
    assert lines == ["  - **Usher** gains 5 Fanfare: 3 → 8."]


def test_the_leads_regen_prints_as_a_regain():
    lines = _log(_beat("regain", "usher", "Usher", 4, 1))
    assert lines == ["  - **Usher** regained 1 Fanfare as the front "
                     "performer: 3 → 4."]


def test_an_enemy_hit_on_the_lead_prints_the_dealer_and_the_bar():
    lines = _log(_beat("hit", "usher", "Usher", 3, 5,
                       target="Living Fog"))
    assert lines == ["  - **Living Fog** hit **Usher** for 5: 8 → 3."]


def test_a_hit_that_empties_the_lead_says_it_leaves_once():
    lines = _log(_beat("hit", "usher", "Usher", 0, 3, target="Sludge Spinner"),
                 _beat("leave", "usher", "Usher", 0, 3, reason="hit"))
    assert lines == [
        "  - **Sludge Spinner** hit **Usher** for 3: 3 → 0, and it leaves "
        "the stage: emptied by a hit, so it takes a Bow."]


def test_a_hit_that_empties_the_lead_then_prints_its_bow():
    """Rule 7, 2026-09-25: the Bow the mod files at the flush after the hit
    prints on its own line, as the Spend exit's does."""
    lines = _log(_beat("hit", "usher", "Usher", 0, 3, target="Sludge Spinner"),
                 _beat("leave", "usher", "Usher", 0, 3, reason="hit"),
                 _beat("bow", "usher", "Usher", 0, 4))
    assert lines[0].endswith("emptied by a hit, so it takes a Bow.")
    assert len(lines) == 2
    assert lines[1].startswith("  - **Usher** took a Bow")


def test_a_rapt_audience_refund_follows_the_hit_it_answers():
    lines = _log(_beat("hit", "usher", "Usher", 2, 2, target="Living Fog"),
                 _beat("raise", "chevalmarin", "Chevalmarin", 2, 1))
    assert lines == ["  - **Living Fog** hit **Usher** for 2: 4 → 2.",
                     "  - **Chevalmarin** gains 1 Fanfare: 1 → 2."]


def test_a_hit_with_no_dealer_is_still_a_line():
    lines = _log(_beat("hit", "usher", "Usher", 1, 2))
    assert lines == ["  - **Usher** was hit for 2: 3 → 1."]


def test_a_raise_card_on_a_stage_board_points_at_the_log():
    """"Rising Applause -- Nothing this page can count landed off it" was
    false: it had raised 5."""
    row = {"card": "Rising Applause", "auto_played": False, "carried": False,
           "overflowed": False, "hits": [], "killed": []}
    assert _resolution_lines([row], stage=True)[1] == RESOLUTION_NO_HITS_STAGE
    assert _resolution_lines([row])[1] == RESOLUTION_NO_HITS
