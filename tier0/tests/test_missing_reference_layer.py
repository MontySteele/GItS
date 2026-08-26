"""A missing `game_ref/` layer fails LOUDLY, at the door, with the fix in it.

BACKLOG `EB-128` (4). `game_ref/` has been destroyed four times. Until this
check existed the loss announced itself in one of two structurally-invisible
ways: an experiment naming a `real_*` arm discovered it by traceback halfway
through a cell, and the suite's only tell was a silent skip-count jump. Neither
names the tree, and neither says how to get it back.

The check lives on `tier05.runner.resolve_plan` because R68 made that the
single source of truth for character -> plan, so every tier-0.5 arm passes
through it before it asks for a card.

HERMETIC. Every test points `loader.GAME_REF_DIR` at a `tmp_path`, so nothing
here reads, writes or notices the real tree -- including on the primary
checkout, where it exists and is not this suite's to touch.
"""

import pytest

from tier0.content import loader
from tier05 import runner

SHEET = "ironclad_pool.yaml"
LAYERS = loader.EXTERNAL_CARD_LAYERS[SHEET]


@pytest.fixture
def game_ref(tmp_path, monkeypatch):
    """A stand-in `game_ref/` the test controls completely."""
    root = tmp_path / "game_ref"
    monkeypatch.setattr(loader, "GAME_REF_DIR", root)
    return root


def _populate(root, skip=()):
    root.mkdir(parents=True, exist_ok=True)
    for name in (SHEET, *LAYERS):
        if name in skip:
            continue
        (root / name).write_text("[]\n", encoding="utf-8")


# ------------------------------------------------------------ the check ----

def test_a_missing_tree_is_named_and_not_tracebacked(game_ref):
    with pytest.raises(loader.MissingReferenceLayer) as exc:
        loader.require_reference_layer("real_ironclad")
    msg = str(exc.value)
    assert "real_ironclad" in msg
    assert "does not exist" in msg
    assert SHEET in msg
    assert str(game_ref) in msg, "the message says WHERE it looked"


def test_the_message_carries_the_restore_point(game_ref):
    """A loud failure that does not say what to do next is just a louder
    failure. `tools/backup_game_ref.py` is the restore point (the vault was
    ruled by [USER] 2026-08-24) and the message names it by module path."""
    with pytest.raises(loader.MissingReferenceLayer) as exc:
        loader.require_reference_layer("real_silent")
    msg = str(exc.value)
    assert "tools.backup_game_ref" in msg
    assert "lint_game_ref_backup" in msg
    assert "EB-128" in msg


def test_the_standing_rule_rides_on_the_message(game_ref):
    """THE ROW'S STANDING RULE: do not fabricate, stub or approximate a
    missing layer to make an anchor load. A stubbed `real_ironclad` produces
    numbers that look like floors and are not, which is worse than absence --
    so the refusal says so at the moment somebody would be tempted."""
    with pytest.raises(loader.MissingReferenceLayer) as exc:
        loader.require_reference_layer("real_ironclad")
    msg = str(exc.value).lower()
    assert "do not stub" in msg
    assert "fabricate" in msg


def test_a_PARTIAL_tree_fails_too_and_says_which_layer(game_ref):
    """The merged pool present and a reviewed layer gone is a real state --
    `_external_cards` already refuses it, but only once something has already
    started loading. Catching it at the door is the point of the check."""
    _populate(game_ref, skip=(LAYERS[0],))
    with pytest.raises(loader.MissingReferenceLayer) as exc:
        loader.require_reference_layer("real_ironclad")
    msg = str(exc.value)
    assert LAYERS[0] in msg
    assert "is missing" in msg
    # The list names what is GONE, not everything the arm reads: a refusal
    # that lists present files too is a refusal nobody can act on.
    listed = msg.split("is missing: ")[1].split(" (looked in")[0]
    assert listed == LAYERS[0]


def test_a_complete_tree_passes_silently(game_ref):
    _populate(game_ref)
    loader.require_reference_layer("real_ironclad")


def test_every_other_character_is_untouched(game_ref):
    """A no-op for the roster and both `ref_*` anchors, which is why it can
    sit on `resolve_plan`'s path unconditionally. `ref_ironclad` in particular
    is the SCORING ANCHOR and reads no local reference at all."""
    for character in ("klee", "furina", "kokomi", "ref_ironclad",
                      "ref_silent", "not_a_character"):
        loader.require_reference_layer(character)


def test_the_two_arms_are_derived_from_the_loader_and_not_retyped():
    """A second table is a second thing to disagree with the first."""
    assert loader.REFERENCE_LAYER_SHEETS == {
        char: sheet for sheet, char in loader.EXTERNAL_CARD_SHEETS.items()}
    assert set(loader.REFERENCE_LAYER_SHEETS) == {"real_ironclad",
                                                  "real_silent"}


# ----------------------------------------------------------- at the door ---

def test_resolve_plan_refuses_a_real_arm_before_a_single_run(game_ref):
    """R68's single source of truth for character -> plan is where every
    tier-0.5 arm passes, so this is the earliest honest moment."""
    with pytest.raises(loader.MissingReferenceLayer):
        runner.resolve_plan("real_ironclad", None)
    with pytest.raises(loader.MissingReferenceLayer):
        runner.resolve_plan("real_silent", "generic")


def test_resolve_plan_still_answers_for_everybody_else(game_ref):
    assert runner.resolve_plan("kokomi", None) == ("priest", "priest")
    assert runner.resolve_plan("ref_ironclad", None) == ("generic", "generic")


def test_the_arm_returns_the_moment_the_tree_is_back(game_ref):
    """The check is about PRESENCE and nothing else -- it must not become a
    second gate somebody has to satisfy after a restore."""
    _populate(game_ref)
    assert runner.resolve_plan("real_ironclad", None) == ("generic", "generic")


def test_the_refusal_is_its_own_class_and_not_a_bare_ValueError():
    """So a table that wants to print "arm unavailable" can catch exactly this
    and keep catching real defects the loud way."""
    assert issubclass(loader.MissingReferenceLayer, RuntimeError)
    assert not issubclass(loader.MissingReferenceLayer, ValueError)
