"""Cross-sheet lint gates (tools/lint_strict_domination.py).

The per-sheet comment/number lint gate lives with its sheet's tests
(test_furina_sheet.test_sheet_comments_match_numbers); this module holds
the lints that sweep every docs card sheet at once.
"""

import subprocess
import sys
from pathlib import Path

from tier0.content import loader

REPO = Path(loader.__file__).resolve().parents[2]


def test_no_strict_domination_on_docs_sheets():
    sheets = [str(loader.DOCS_DIR / s) for s in loader.DOCS_CARD_SHEETS]
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_strict_domination.py"),
         *sheets],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_kokomi_decksize_grammar():
    """Kokomi kickoff §1 law 4 (user-authored, machine-checkable → gate):
    Commons in HER pool net card delta <= 0. Scope is her personal sheet
    only — deliberately not the companion pools, not mod-wide."""
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_kokomi_decksize.py"),
         str(loader.DOCS_DIR / "kokomi-cards.yaml")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_every_draftable_card_can_be_upgraded():
    """G-C1. A card with no upgrade is a dead campfire choice.

    Two layers, because the 2026-07-25 playtest's actual defect was in the
    second: a card can have a perfectly good sheet delta that the GENERATOR
    cannot express, in which case the sim upgrades it and the live game does
    not. A lint that only checked the sheet would have reported all-clear on
    exactly the card that was reported broken.

    Wired here rather than left as a tool so that a missing upgrade is red,
    not a playtest note.
    """
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_upgrade_coverage.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_card_names_are_unique():
    """Display names: unique internally, and clear of docs/reserved-card-names.txt.

    The reserved list exists because this class of bug is STRUCTURALLY
    INVISIBLE to the repo -- we ship alongside base-game and third-party
    cards whose name lists we cannot read, and the engine resolves a clash
    unpredictably. It was a human who noticed our "Grand Finale" was also
    the Silent's. No instrument here could have. The list is the record of
    those catches; append to it, and don't prune without a reason on file.
    """
    sheets = [str(loader.DOCS_DIR / s) for s in loader.DOCS_CARD_SHEETS]
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_unique_names.py"),
         *sheets],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    # R69: relics are in the namespace too, and the lint must be SEEING them
    # -- a gate that scans zero relic files reports the same clean line as one
    # that scans them all (the §3.1/§3.7 dead-gate class).
    assert "relic names unique" in res.stdout
    assert " 0 relic " not in res.stdout


def test_a_card_relic_name_collision_fails_the_lint(tmp_path):
    """R69's negative test.

    Until R69 this exact collision existed and the lint was green: the Klee
    Rare Power card `explosive_frags` and Klee's Orobas relic upgrade both
    displayed "Explosive Frags", with unrelated effects, both reachable in
    one run. The lint read card sheets only, so relics were outside its
    scope while being squarely inside its purpose.

    Built as a synthetic sheet against the REAL relic sources, so it fails
    if the relic reader stops finding relics -- which is the way a gate like
    this dies.
    """
    lint = str(REPO / "tools" / "lint_unique_names.py")
    sheet = tmp_path / "collide.yaml"
    # "Dodoco Tales" is a real, live relic name. Minting a card with it is
    # precisely the mistake the extended lint exists to refuse.
    sheet.write_text(
        'cards:\n'
        '- {id: fake_collider, name: "Dodoco Tales", cost: 1, type: skill,\n'
        '   rarity: common}\n', encoding="utf-8")

    res = subprocess.run([sys.executable, lint, str(sheet)],
                         capture_output=True, text=True)
    assert res.returncode == 1, (
        "a card taking a live relic's display name must fail the lint\n"
        + res.stdout + res.stderr)
    assert "Dodoco Tales" in res.stdout
    assert ("CROSS-KIND NAME COLLISION" in res.stdout
            or "RESERVED NAME" in res.stdout), res.stdout


def test_the_reserved_list_does_not_fail_the_names_it_protects(tmp_path):
    """The other half of R69's reserved-both-sides rule.

    "Explosive Frags" and "Dodoco Tales" are BOTH reserved, so a naive
    reserved check would fail the card and the relic that legitimately hold
    them -- and the usual fix for that (drop the entries) is exactly what
    lets the collision re-form from the other side. The kind annotation is
    what makes reserving both sides survivable, so it needs its own pin.
    """
    lint = str(REPO / "tools" / "lint_unique_names.py")
    sheet = tmp_path / "owner.yaml"
    sheet.write_text(
        'cards:\n'
        '- {id: explosive_frags, name: "Explosive Frags", cost: 1,\n'
        '   type: power, rarity: rare}\n', encoding="utf-8")

    res = subprocess.run([sys.executable, lint, str(sheet)],
                         capture_output=True, text=True)
    assert res.returncode == 0, (
        "the card that OWNS a card-owned reserved name must pass\n"
        + res.stdout + res.stderr)


def test_mirrored_constants_match_the_sim():
    """C# balance constants vs tier0, the source of truth.

    Every balance number lives twice -- once in tier0 where it was MEASURED,
    once in C# where it is PLAYED -- and the C# copies were kept in step by
    discipline alone until 2026-07-25. That failure mode is silent in the
    worst way: a sim-side retune nobody mirrors leaves the build green, the
    tests green, and the tuning report describing a game nobody is playing.

    It is wired into PYTEST as well as into validate.ps1 (S6e) on purpose.
    The retune happens HERE, in Python, and the person doing it runs the
    suite; making them wait for a deploy to learn they left the mod behind
    is one round trip too late. There is no C# test project to pin this at
    runtime, so this static comparison is the whole gate.
    """
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_constant_parity.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_companion_roster_can_fill_both_shop_slots():
    """§4.7 shop channel: instance TWO of the empty-draw class.

    Wired here rather than left as a tool for the same reason as the upgrade
    lint above: the failure it prevents is a black-screen softlock on shop
    entry (finding 24's shape), and the roster corner that causes it moves
    every time someone edits a companion sheet. A thin nation is survivable --
    both implementations carry a fallback ladder -- but every rung the ladder
    takes is a slot that silently stopped honouring §4.7, which is invisible
    at the table and visible here.
    """
    res = subprocess.run(
        [sys.executable,
         str(REPO / "tools" / "lint_companion_shop_coverage.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
