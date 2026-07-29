"""Cross-sheet lint gates (tools/lint_strict_domination.py).

This module holds the lints that sweep every docs card sheet at once.

G1 (Serenitea Sweep, 2026-07-26) moved the comment/number lint here from
`test_furina_sheet`, where it gated ONE sheet of six. Audit sec.3.8: run
against the other five it reported 35 findings -- "real drift the gate's
scope hid". On inspection it is 34 comments legitimately citing numbers
that are not the row's (sibling cards, superseded values, measurement
brackets, worked arithmetic, engine constants, and two SHEET LINE NUMBERS)
plus exactly ONE real drift. Furina's sheet is clean precisely because it
already carries the `(lint-ok: reason)` markers the convention provides;
the other five had never been through the pass.
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


def test_sheet_comments_match_numbers_on_every_sheet():
    """G1: fanned from one sheet to all six.

    Per-line `(lint-ok: <reason>)` markers rather than a blanket suppression:
    a sheet-wide exemption would switch off the drift class this lint exists
    for, and the reasons are what let a reviewer tell "cites a sibling card"
    from "cites a number this row no longer has".
    """
    sheets = [str(loader.DOCS_DIR / s) for s in loader.DOCS_CARD_SHEETS]
    assert len(sheets) >= 6, sheets
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_sheet_comments.py"),
         *sheets],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_the_comment_lint_still_catches_real_drift(tmp_path):
    """The negative half. A gate fanned out and never seen failing is a gate
    whose new scope nobody has tested."""
    sheet = tmp_path / "drift.yaml"
    sheet.write_text(
        '- {id: probe, name: "Probe", cost: 1, type: attack, rarity: common,\n'
        '   effects: [{op: damage, amount: 10, target: enemy}]}\n'
        '   # The ceiling: 8 damage, single target.\n',
        encoding="utf-8")
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_sheet_comments.py"),
         str(sheet)],
        capture_output=True, text=True)
    assert res.returncode == 1, res.stdout
    assert "comment cites 8" in res.stdout


def test_kokomi_decksize_grammar():
    """Kokomi kickoff §1 law 4 (user-authored, machine-checkable → gate):
    Commons in HER pool net card delta <= 0. Scope is her personal sheet
    only — deliberately not the companion pools, not mod-wide."""
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_kokomi_decksize.py"),
         str(loader.DOCS_DIR / "kokomi-cards.yaml")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_furina_register_grammar():
    """Curtain Call sweep (R85): every Furina card carries a register in
    {salon, archon, private}; Fanfare touches are archon, salon_member
    deploys are salon, pure-Encore cards are private, and EXACTLY two rares
    carry the focalors flavor tag. Scope is her personal sheet only; the
    third-instance rule generalizes this when a second character adopts
    registers."""
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_furina_registers.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "0 register violations" in res.stdout


def test_handwritten_cards_match_their_sheets():
    """Addendum A8: the hand-written cards, against the sheets they came from.

    This lint existed and gated DEPLOY only (validate.ps1 S6), so `pytest` had
    nothing to say about it. R74 deleted `ceremonial_garment`'s entry splash
    from the sheet; the hand-written C# kept dealing it for the length of the
    sprint, across a full green suite and a constant-parity run, because the
    only check that could see it was on the far side of a deploy the sprint
    never performed.

    A gate that runs on deploy and nowhere else does not gate development. It
    reports at the last possible moment, after the measurements it invalidates
    have already been taken.
    """
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_handwritten_parity.py")],
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


def test_register_stays_out_of_the_engine():
    """R85's register column is naming and art, never mechanics.

    Cell 1 of the Curtain Call sweep PROVED this empirically -- renames plus
    register assignments landed together and the run was byte-identical, so
    nothing read the new field. That is a measurement, and a measurement only
    speaks for the code that existed when it ran. This converts it into a
    standing guarantee.

    The failure it prevents is the nastiest kind of coupling: with a
    register-aware engine, moving a card from the salon voice to the archon
    one -- an ART decision, taken on art grounds, by whoever is picking
    illustrations -- would silently move win rate, and the next sim run would
    blame whatever else changed that day. Balance and lore have to be able to
    move independently.
    """
    res = subprocess.run(
        [sys.executable,
         str(REPO / "tools" / "lint_register_isolation.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_every_engine_op_has_a_drafter_price():
    """Op parity (sim-hygiene sprint, 2026-07-29): tools/lint_op_parity.py.

    Wired into PYTEST as well as into CI for the same reason the constant
    parity lint is: the moment an op is registered is the moment the author
    knows what it is worth, and that moment is a pytest run, not a push. An
    op with no price is worth nothing to the drafter SILENTLY -- the defect
    class DRAFTER_VERSION 6, 7, 8 and 9 each rediscovered by measuring one
    character and wondering why its plan drafted badly.
    """
    res = subprocess.run(
        [sys.executable, str(REPO / "tools" / "lint_op_parity.py")],
        capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_the_op_parity_lint_still_catches_a_newly_registered_op():
    """The red half. A lint nobody has seen fail is a lint nobody can trust.

    Registers a fictional op in the engine registry, in-process, and asserts
    the lint reports it as a FINDING rather than skipping it. The registry is
    restored in the `finally` -- this test must not leak a fake verb into the
    rest of the session.
    """
    import importlib

    from tier0.engine import effects as _effects
    lint = importlib.import_module("tools.lint_op_parity")

    assert lint.findings() == [], "the lint must be green before it is red"
    _effects.OPS["chorus_of_the_unpriced"] = lambda state, fx, card: None
    try:
        bad = lint.findings()
    finally:
        del _effects.OPS["chorus_of_the_unpriced"]
    assert any("chorus_of_the_unpriced" in line and "UNPRICED OP" in line
               for line in bad), bad
    assert lint.findings() == [], "and green again once the op is gone"
