"""The role x tempo taxonomy and its floors-only coverage gate.

Track A of the Axis-Validity session. Everything here runs on a fresh clone:
the floors are a COMMITTED percentages-only file, the tags are a COMMITTED
review file, and nothing in this module touches game_ref/ -- which is the
whole reason the floors were committed as percentages rather than recomputed
from the dll on demand.
"""

import subprocess
import sys
from pathlib import Path

import yaml

from tier0.content import loader

REPO = Path(loader.__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from tools import role_tempo as rt        # noqa: E402


def _run(script, *args):
    return subprocess.run(
        [sys.executable, str(REPO / "tools" / script), *args],
        capture_output=True, text=True)


# --- the gate ---------------------------------------------------------------

def test_the_coverage_gate_finds_exactly_the_pinned_debt():
    """A NEW finding is a coverage regression; a STALE pin is a cell that
    moved without anybody saying so. The gate fails on either, which is what
    makes a green suite mean something while P1's null is open."""
    res = _run("lint_role_tempo_coverage.py", "--gate")
    assert res.returncode == 0, res.stdout + res.stderr
    assert "gate ok" in res.stdout, res.stdout


def test_the_gate_says_out_loud_that_its_tags_are_provisional():
    """[USER] gate A-G1 has not closed. A run whose output reads like a
    verdict on the pools, when no tag has landed on a sheet, is the exact
    misreading the charter's gate exists to prevent."""
    res = _run("lint_role_tempo_coverage.py", "--gate")
    assert "PROVISIONAL" in res.stdout, res.stdout
    assert "A-G1" in res.stdout, res.stdout


def test_the_lint_can_never_name_a_card():
    """Charter A0.2(1): floors only. No card can EVER fail -- not for being
    unclassifiable, not for being hybrid, not for being strange. The unit of
    failure is (character, archetype, cell) and nothing smaller, so no card id
    from any sheet may appear anywhere in a full run's output."""
    res = _run("lint_role_tempo_coverage.py")
    ids = {row["id"] for path in rt.SHEETS.values()
           for row in rt.load_rows(path)}
    leaked = sorted(i for i in ids if i in res.stdout)
    assert not leaked, f"the floors-only lint named cards: {leaked}"


def test_the_review_and_tagthrough_artifacts_are_current():
    res = _run("suggest_role_tempo_tags.py", "--check")
    assert res.returncode == 0, res.stdout + res.stderr


# --- the floors -------------------------------------------------------------

def test_utility_and_support_are_never_linted():
    """`utility` is protected free space (A0.2(2)) and `support` is graded by
    play only, because the sim is one-seat (D4). Neither may acquire a floor
    by someone regenerating the file on a day canon happens to be non-zero
    everywhere."""
    floors = yaml.safe_load(
        (REPO / "docs" / "role-tempo-floors.yaml").read_text(encoding="utf-8"))
    assert set(floors["never_linted"]) == {"utility", "support"}
    for cell in floors["mandatory"]:
        assert cell.split("|")[0] not in ("utility", "support"), cell


def test_every_floor_is_a_percentage_and_nothing_else_is_committed():
    """PERCENTAGES ONLY. game_ref/ is gitignored (.gitignore:28) and the
    committed deliverable is the shape, never the material."""
    text = (REPO / "docs" / "role-tempo-floors.yaml").read_text(
        encoding="utf-8")
    floors = yaml.safe_load(text)
    for cell, value in floors["mandatory"].items():
        assert isinstance(value, float), cell
        assert 0.0 < value <= 100.0, (cell, value)


# --- the vocabulary ---------------------------------------------------------

def test_the_vocabulary_is_the_charters_amended_one():
    """A0: `support` joins, `aoe` leaves for the modifier list."""
    assert "support" in rt.SOLVE
    assert "aoe" not in rt.SOLVE
    assert "aoe" in rt.MODIFIERS


def test_every_sheet_declares_its_archetypes_and_the_header_wrap_is_read():
    """R66 makes the sheet HEADER canonical for the archetype vocabulary, and
    two of the three headers wrap mid-parenthetical. A naive single-line read
    silently dropped `generic` from Kokomi's list -- i.e. deleted an identity
    from the floors without failing anything."""
    for name, path in rt.SHEETS.items():
        declared = rt.declared_archetypes(path)
        assert len(declared) >= 3, (name, declared)
        assert "generic" in declared, (name, declared)


def test_every_card_lands_in_at_least_one_band_on_both_scales():
    """A card with no band is invisible to every cell, which would let a pool
    pass by having cards the taxonomy cannot place."""
    for name, path in rt.SHEETS.items():
        rows = rt.load_rows(path)
        scans, _ = rt.classify_pool(rows, name)
        for row in rows:
            scan = scans[row["id"]]
            assert scan["fight"], (name, row["id"])
            assert scan["run"], (name, row["id"])


def test_tag_through_entities_all_carry_their_provenance():
    """ENTITY_PAYOFFS is the hand-authored half of A0.1 and the artifact A-G1
    reviews. An entry without a reason is a design claim nobody can argue
    with, which is the one thing it must never be."""
    for token, (roles, bands, why) in rt.ENTITY_PAYOFFS.items():
        assert roles, token
        assert set(roles) <= set(rt.SOLVE), token
        assert set(bands) <= set(rt.FIGHT_BANDS), token
        assert len(why) > 60, token
    for power, (token, roles, why) in rt.TOKEN_PAYOFF_POWERS.items():
        assert set(roles) <= set(rt.SOLVE), power
        assert len(why) > 60, power
