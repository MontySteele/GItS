"""The custom-keyword tooltips have ONE source, and the derived copy is fresh.

THE DEFECT (2026-09-02). Every `KLEEMOD-*` keyword tip existed twice: in
`KleeMod.cs`'s `keywordFallback` dictionary, where the numerals are
interpolated from the constants they quote (`EB-89`), and hand-typed in a
`tools/build_pck.ps1` heredoc, where they were literals. The game merges the
PACKAGED table over the dll's, so the copy a player actually reads was the
copy no constant fed -- and a repricing would have left the pck telling them a
retired number with every gate green, including `lint_prose_constants.py`,
which reads the C#.

`tools/gen_keyword_loc.py` now derives the pck's json from the C# and
`klee-mod/pck-src/` overlays it into the pack. These arms are the gate on that
arrangement, and they are three separate claims:

  1. the derived file is not stale (the generator's own `--check`);
  2. nobody has typed a second copy back into the pck builder;
  3. the derived rows carry the RESOLVED numbers, not `{Expressions}` -- an
     unresolved brace ships to the player as a SmartFormat placeholder against
     a table with no such variable, which renders as nothing at all.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GENERATED = (REPO / "klee-mod" / "pck-src" / "klee" / "localization" / "eng"
             / "card_keywords.json")
BUILD_PCK = REPO / "tools" / "build_pck.ps1"
ENTRY = REPO / "klee-mod" / "KleeCode" / "KleeMod.cs"


def test_the_derived_keyword_table_is_current():
    """`--check`, exactly as CI and the deploy would run it."""
    proc = subprocess.run(
        [sys.executable, "tools/gen_keyword_loc.py", "--check"],
        cwd=str(REPO), capture_output=True, text=True,
        encoding="utf-8", errors="replace")
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_the_pck_builder_types_no_keyword_rows_of_its_own():
    """The second copy must not come back. A substring check over the whole
    file, comments included -- the same shape the prototype quarantine uses --
    because a heredoc reintroduced as a comment is a heredoc one edit away."""
    text = BUILD_PCK.read_text(encoding="utf-8")
    rows = re.findall(r'"KLEEMOD-[A-Z_]+\.(?:title|description)"', text)
    assert rows == [], (
        f"tools/build_pck.ps1 carries {len(rows)} keyword loc row(s) of its "
        f"own again: {sorted(set(rows))[:5]}. The pck's copy wins over the "
        f"dll's, so a second copy here is the copy the player reads. Generate "
        f"it: python tools/gen_keyword_loc.py")
    assert "gen_keyword_loc.py" in text, (
        "build_pck.ps1 no longer names the generator, so a reader has no way "
        "to find where the rows went")


def test_the_generated_rows_carry_numbers_not_placeholders():
    """`{Elements.ReactionConstants.AuraDurationTurns}` must have become `2`.

    An unresolved brace is invisible: SmartFormat renders an unknown
    placeholder as nothing, so the sentence simply loses its number.
    """
    table = json.loads(GENERATED.read_text(encoding="utf-8"))
    assert table, "the derived table is empty"
    for key, value in table.items():
        assert "{" not in value and "}" not in value, (key, value)
    # And the interpolation really did resolve rather than the C# having gone
    # literal: the aura duration is in four rows and is a numeral in all four.
    pyro = table["KLEEMOD-APPLIES_PYRO.description"]
    assert re.search(r"applies Pyro for \d+ turns", pyro), pyro


def test_every_dll_row_with_a_literal_key_reaches_the_pck():
    """The two tables cannot silently drift APART in the other direction
    either: a row added to the C# dictionary with a plain key must appear in
    the derived file. (Rows keyed by a C# constant -- the hover-tip titles
    whose bodies are built live -- are DLL-only by design and are excluded
    here for the reason gen_keyword_loc.py states.)"""
    source = ENTRY.read_text(encoding="utf-8")
    start = source.index("var keywordFallback = new Dictionary<string, string>")
    end = source.index("keywordTable.MergeWith(keywordFallback", start)
    block = source[start:end]

    # Drop the quarantined arms' rows: they are `#if PROTOTYPE_CARDS` and must
    # never reach a release pack.
    kept, skipping = [], False
    for line in block.splitlines():
        stripped = line.strip()
        if stripped.startswith("#if PROTOTYPE_CARDS"):
            skipping = True
            continue
        if skipping and stripped.startswith("#endif"):
            skipping = False
            continue
        if not skipping:
            kept.append(line)

    literal_keys = set(re.findall(r'\[\s*"(KLEEMOD-[^"]+)"\s*\]',
                                  "\n".join(kept)))
    derived = set(json.loads(GENERATED.read_text(encoding="utf-8")))
    missing = sorted(literal_keys - derived)
    assert not missing, (
        f"{len(missing)} row(s) in KleeMod.cs never reach the pck: {missing}. "
        f"Run: python tools/gen_keyword_loc.py")


def test_no_arm_keyword_reaches_the_packaged_table():
    """The quarantine, one resource file over. `Cards/Prototype/**` is
    Compile Remove'd from a release build; a pck is built ONCE and ships in
    the release package, so an arm keyword in it would be the arm's text
    leaking past the compile switch it is quarantined by."""
    table = json.loads(GENERATED.read_text(encoding="utf-8"))
    arm_keys = [k for k in table if k.startswith("KLEEMOD-ARM_")]
    assert arm_keys == [], arm_keys
