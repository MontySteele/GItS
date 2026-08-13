"""EB-71 (R174), the C# leg: the unified Sly grammar crosses the wall.

The sim leg (tier0/tests/test_eb71_sly_unification.py) proved that `Card.sly`
is one field carrying two shapes -- authored riders a discard RESOLVES, and
the reserved `{op: sly_autoplay}` marker standing for the base game's own
`CardKeyword.Sly`. The codegen path does not go through the tier0 loader, so
none of that reached the mod: `tools/gen_klee_cards.py` read a row's `sly:`
list verbatim as an effect list.

These are the pins for the other side of the wall.

  * the marker is a KEYWORD in the mod, on the CanonicalKeywords rail beside
    Exhaust/Innate/Retain -- never a body, never a second discard hook. The
    game owns the auto-play once the keyword is on the card, and a hook
    resolving it too would play the discarded card twice.
  * authored riders beside the marker still emit their hook, or Kokomi's
    Assist lane would vanish from any card that also printed the keyword.
  * PARITY, the whole point: no committed sheet prints the marker, so every
    generated file must be byte-identical to the pre-EB-71 output. That is
    asserted in the shape the register test uses -- regenerate and diff --
    by `tools/gen_roster_cards.py --check` in CI; here it is the narrower
    claim that the rider split changes nothing for a rider-only card.
"""

from __future__ import annotations

import pytest

from tier0.engine import state
from tools import effect_walk, gen_klee_cards as gen, lint_sly_grammar


BASE = {"id": "eb71_probe", "name": "EB71 Probe", "cost": 1, "type": "skill",
        "rarity": "common", "effects": [{"op": "block", "amount": 5}]}


def _emit(sly):
    card = {**BASE, "sly": sly}
    reason = gen.blocked_reason(card, gen.KOKOMI_PROFILE)
    assert reason is None, reason
    return gen.emit(card, gen.KOKOMI_PROFILE)


# --- the constant is ONE constant ------------------------------------------

def test_the_tools_side_marker_is_the_engines_marker():
    """`tools/` re-spells the op for sheet rows; drift would be silent.

    The generator is deliberately tier0-free (it reads raw yaml, no loader,
    no dataclass), so the word lives twice. This is the lint_constant_parity
    treatment: two copies, one pin.
    """
    assert effect_walk.SLY_AUTOPLAY_OP == state.SLY_AUTOPLAY_OP
    assert state.SLY_AUTOPLAY == {"op": effect_walk.SLY_AUTOPLAY_OP}


# --- the marker is a keyword, not a body -----------------------------------

def test_the_reserved_rider_emits_the_base_game_keyword():
    cs = _emit([{"op": effect_walk.SLY_AUTOPLAY_OP}])
    assert "CardKeyword.Sly" in cs
    assert "AfterCardDiscarded" not in cs
    assert effect_walk.SLY_AUTOPLAY_OP not in cs


def test_the_reserved_rider_does_not_also_print_itself_on_the_face():
    """The keyword renders through the game's auto-keyword pipeline (the A9
    rail). A description line would say the word a second time."""
    cs = _emit([{"op": effect_walk.SLY_AUTOPLAY_OP}])
    assert "[gold]Sly[/gold]:" not in cs


def test_authored_riders_beside_the_keyword_still_emit_their_hook():
    cs = _emit([{"op": effect_walk.SLY_AUTOPLAY_OP},
                {"op": "draw", "amount": 1}])
    assert "CardKeyword.Sly" in cs
    assert "AfterCardDiscarded" in cs
    assert "[gold]Sly[/gold]: Draw 1 card." in cs


def test_a_rider_only_card_is_unchanged_by_the_split():
    """PARITY. The rider-only shape is what every committed Sly card is, and
    it must emit exactly what it emitted before the marker existed."""
    riders = [{"op": "block", "amount": 4}]
    cs = _emit(riders)
    assert "AfterCardDiscarded" in cs
    assert "CardKeyword.Sly" not in cs
    assert "[gold]Sly[/gold]: Gain 4 [gold]Block[/gold]." in cs


# --- the shapes the emitter must REFUSE ------------------------------------

@pytest.mark.parametrize("sly, needle", [
    (True, "not an effect list"),
    ([{"op": "sly_autoplay", "until": "turn_end"}], "takes no other key"),
    ([{"amount": 3}], "not an effect mapping"),
])
def test_unprintable_sly_shapes_block_by_name(sly, needle):
    reason = gen.blocked_reason({**BASE, "sly": sly}, gen.KOKOMI_PROFILE)
    assert reason is not None and needle in reason, reason


def test_the_retired_field_still_blocks_at_the_codegen_wall():
    """`sly_keyword:` is refused sim-side by RETIRED_CARD_FIELDS. The
    generator never sees that registry -- its own total field whitelist is
    what refuses it here."""
    assert "sly_keyword" in state.RETIRED_CARD_FIELDS
    reason = gen.blocked_reason({**BASE, "sly_keyword": True},
                                gen.KOKOMI_PROFILE)
    assert reason == "card field(s) ['sly_keyword'] not understood"


# --- the standing guard ----------------------------------------------------

def test_the_sly_grammar_lint_is_clean_on_this_tree():
    assert lint_sly_grammar.findings() == []


def test_the_lint_catches_a_retired_spelling_reappearing(tmp_path,
                                                         monkeypatch):
    """Not vacuous: plant the dead shape and the guard must fire."""
    sheet = tmp_path / "probe-cards.yaml"
    sheet.write_text(
        "cards:\n  - id: probe\n    name: Probe\n    sly_keyword: true\n",
        encoding="utf-8")
    monkeypatch.setattr(lint_sly_grammar, "SHEETS", (sheet,))
    monkeypatch.setattr(lint_sly_grammar, "REPO", tmp_path)
    bad = lint_sly_grammar._sheet_shapes()
    assert any("RETIRED SLY FIELD" in line for line in bad), bad


def test_the_lint_catches_a_sheet_asking_for_a_turn_scoped_grant(tmp_path,
                                                                monkeypatch):
    sheet = tmp_path / "probe-cards.yaml"
    sheet.write_text(
        "cards:\n  - id: probe\n    name: Probe\n"
        "    sly: [{op: sly_autoplay, until: turn_end}]\n", encoding="utf-8")
    monkeypatch.setattr(lint_sly_grammar, "SHEETS", (sheet,))
    monkeypatch.setattr(lint_sly_grammar, "REPO", tmp_path)
    bad = lint_sly_grammar._sheet_shapes()
    assert any("SLY SHAPE" in line for line in bad), bad
