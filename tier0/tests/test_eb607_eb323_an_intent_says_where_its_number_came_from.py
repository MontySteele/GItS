"""`EB-607` / `EB-323`: an intent part says how its number was arrived at, and
whose side it lands on.

`EB-607`'S FIND (Klee r23 lane 1 (c) 3). "Fossil Stalker read 12 before and
after I gave it Strength 3, while Corpse Slug's number moved." The row's first
half printed the game's own `GetIntentLabel` unchanged and named the pair where
an icon and its sentence disagree -- a detector, which fires after the fact.
The arithmetic is the bridge's: `AttackIntent.GetSingleDamage` calls
`Hook.ModifyDamage` and throws away the `out` list of models it folded, and the
bridge now keeps all three answers.

`EB-323`'S FIND (Klee r7). `Empower (Buff)` -- a heading, a bracketed kind and
nothing else, on a board of three bodies. No intent carries a TARGET (the
bodies arrive at `MoveState.PerformMove` when the move resolves), but the SIDE
is settled by the game's own `IntentType` for twelve of its fifteen values, and
the bridge was dropping it.

WHAT THIS FILE PINS is the page half on a feed shaped as the bridge sends one,
plus the two absent-key states: a bridge older than either row prints exactly
what it printed before.

NOTHING MEASURED HERE IS QUOTABLE (R215 B): shape assertions about a renderer.
"""

import copy
import re

from understudy import blindplay, blindplay_faces

from tier0.tests.test_understudy_blindplay import REPO, combat_state


def _with_intent(**fields) -> dict:
    """The recorded combat state with its first enemy's first intent rewritten.

    The rest of the board is the recorded capture, so anything this file does
    not touch reads as the page has always read it.
    """
    state = copy.deepcopy(combat_state())
    enemy = state["battle"]["enemies"][0]
    intent = dict(enemy["intents"][0])
    intent.update(fields)
    enemy["intents"] = [intent]
    return state


def _breakdown(base=12, folded=12, repeats=1, modifiers=()) -> dict:
    return {"base_damage": base, "folded_damage": folded,
            "repeats": repeats, "total_damage": folded * repeats,
            "modifiers": list(modifiers)}


# --------------------------------------------------------------- `EB-607` ---

def test_the_red_one_an_icon_that_moved_names_what_moved_it():
    """Seen to FAIL: Corpse Slug's icon moved under Strength and no surface
    on the page connected the new figure to the power that made it."""
    page = blindplay.observe(_with_intent(
        type="Attack", label="15",
        breakdown=_breakdown(base=12, folded=15, modifiers=["Strength"])))
    assert ("the game folded **Strength** into that: it is 12 on the move "
            "and 15 after") in page


def test_the_other_half_an_icon_that_did_not_move_says_so():
    """Fossil Stalker read 12 before and after Strength 3. The page could not
    tell that from an icon nothing had been folded into, and those are the two
    readings the r23 seat needed to tell apart."""
    page = blindplay.observe(_with_intent(
        type="Attack", label="12", breakdown=_breakdown(base=12, folded=12)))
    assert ("nothing on the board is folded into that number: it is the 12 "
            "the move itself declares") in page


def test_several_modifiers_are_joined_in_the_pages_own_grammar():
    page = blindplay.observe(_with_intent(
        type="Attack", label="18",
        breakdown=_breakdown(base=12, folded=18,
                             modifiers=["Strength", "Vulnerable"])))
    assert "**Strength** and **Vulnerable**" in page


def test_a_multi_hit_prints_the_product_and_its_factors():
    """The multiplication the `PER_HIT_NOTE` reader is doing by hand. Every
    number on the line is the bridge's; the page multiplies nothing."""
    page = blindplay.observe(_with_intent(
        type="Attack", label="6x3",
        breakdown=_breakdown(base=6, folded=6, repeats=3)))
    assert "6 x 3 is 18 if every hit lands" in page


def test_a_single_hit_prints_no_product():
    page = blindplay.observe(_with_intent(
        type="Attack", label="12", breakdown=_breakdown()))
    assert "if every hit lands" not in page


def test_a_build_with_no_breakdown_is_what_it_was():
    """ABSENT IS ABSENT, this feed's standing rule: a bridge older than the
    row sends no key and the enemy block reads exactly as it read."""
    before = blindplay.observe(combat_state())
    assert "folded" not in before
    assert "if every hit lands" not in before


def test_the_reader_carries_the_five_numbers_the_bridge_sends():
    row = blindplay_faces._intent_breakdown(_breakdown(6, 9, 2, ["Strength"]))
    assert row == {"base": 6, "folded": 9, "repeats": 2, "total": 18,
                   "modifiers": ["Strength"]}
    assert blindplay_faces._intent_breakdown(None) == {}


def test_the_bridge_asks_the_game_rather_than_recomputing():
    """The row's whole posture, asserted against the vendored builder: the
    breakdown is `Hook.ModifyDamage`'s own answer and its own `out` list, which
    is what keeps a printed line from disagreeing with the icon beside it."""
    builder = (REPO / "vendor" / "STS2_MCP" / "McpMod.StateBuilder.cs"
               ).read_text(encoding="utf-8")
    head = builder.index("GitsAttackBreakdown(\n")
    body = builder[head:builder.index("GitsIntentBreakdown.Compose", head)]
    assert "Hook.ModifyDamage(" in body
    assert "out IEnumerable<AbstractModel> modifiers" in body
    # No arithmetic of its own: the product is composed by the gits file from
    # numbers the game handed over, and nothing here multiplies or adds.
    assert not re.search(r"folded\s*[*+]\s*", body)


# --------------------------------------------------------------- `EB-323` ---

def test_a_buff_part_says_whose_side_it_is_on_off_the_wire():
    """Seen to FAIL: `Empower (Buff)` named nobody on a board of three."""
    page = blindplay.observe(_with_intent(
        type="Buff", label="", target_side="its own side"))
    assert "this part lands on its own side" in page
    assert "cannot say which body" in page


def test_a_debuff_part_says_it_is_aimed_at_you():
    page = blindplay.observe(_with_intent(
        type="Debuff", label="", target_side="you"))
    assert "this part lands on you" in page


def test_a_feed_with_no_side_keeps_the_older_buff_clause():
    """ABSENT IS ABSENT. A bridge predating the row sends no `target_side`,
    and the page's locally-derived buff clause is exactly what it was."""
    page = blindplay.observe(_with_intent(type="Buff", label=""))
    assert "strengthens the enemy's own side rather than hitting you" in page
    assert "this part lands on" not in page


def test_the_bridge_refuses_the_three_types_that_settle_nothing():
    """`Escape`, `Sleep`, `Stun`, `Hidden` and `Unknown` name no side, so the
    key stays absent rather than carrying a guess. Pinned on the gits file,
    which is the one place the classification lives."""
    gits = (REPO / "vendor" / "STS2_MCP" / "gits" / "GitsIntentBreakdown.cs"
            ).read_text(encoding="utf-8")
    at_you = gits[gits.index("AtYou = new()"):gits.index("AtItself = new()")]
    for absent in ("Escape", "Sleep", "Stun", "Hidden", "Unknown"):
        assert f'"{absent}"' not in gits
    assert '"Attack"' in at_you and '"DeathBlow"' in at_you
