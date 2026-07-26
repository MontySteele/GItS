"""The Track C gate repairs, pinned. (audit sec.3.1 / sec.3.3 / sec.3.7 / R70.)

Every rule repaired here failed the same way: it ran, it reported nothing, and
reporting nothing read as passing. S8 walked a directory containing zero .ps1
files for its entire life. S9's precondition was the defect it existed to
catch. L12 hashed a gitignored directory and returned `[]`. None of them ever
went red, so nothing noticed.

That is exactly the class a source-text pin can hold, because the failure is
structural -- a scan aimed at the wrong place, a guard inverted -- rather than
behavioural. What CANNOT be pinned from pytest is PowerShell 5.1 semantics, so
these check the shape of each rule, and the sprint log carries the end-to-end
run (full `validate.ps1`, green, 84.0s).
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATE = (ROOT / "klee-mod" / "build" / "validate.ps1").read_text(
    encoding="utf-8")
BUILD_PCK = (ROOT / "tools" / "build_pck.ps1").read_text(encoding="utf-8")


def code_only(text: str) -> str:
    """Drop comment lines.

    Every repair below is explained in a comment that NAMES the thing it
    stopped doing, so a bare substring check reads the explanation as the
    defect. Same trap the CreatureFacing pins hit.
    """
    return "\n".join(ln for ln in text.splitlines()
                     if not ln.lstrip().startswith("#"))


# --- C1: S8 scans somewhere that has .ps1 files in it --------------------

def test_s8_scans_the_repo_root_not_the_csharp_source_tree():
    """It walked `$SourceDir` (= KleeCode), which holds no PowerShell at all.

    All three .ps1 files live in klee-mod\\build\\ and tools\\. The loop found
    nothing every run, so the mojibake class it was written for -- heredoc
    strings in build_pck.ps1, the only place this repo writes game-visible
    text from PowerShell -- was never checked.
    """
    block = VALIDATE[VALIDATE.index("$asciiExempt = "):]
    block = block[:block.index("# ------", 10)]
    assert "Get-ChildItem $repoRoot -Recurse -Filter *.ps1" in block, block
    assert "$SourceDir" not in code_only(block), (
        "S8 is aimed at the C# source tree again; it contains no .ps1 files")


def test_s8_fails_when_its_sweep_is_empty():
    """The anti-vacuum guard, and the direct lesson of this bug.

    A rule that iterates an empty set reports exactly what a rule that
    iterates a clean set reports. Now zero files is itself the finding.
    """
    assert re.search(r"if \(\$ps1Files\.Count -eq 0\) \{\s*\n?\s*Fail 'S8'",
                     VALIDATE), VALIDATE[VALIDATE.index("$asciiSkip"):][:600]


def test_s8_does_not_police_other_peoples_trees():
    """`.venv` ships Activate.ps1, which is not this repo's to keep ASCII."""
    assert "'*\\.venv\\*'" in VALIDATE.replace("\\\\", "\\") or \
        "*\\.venv\\*" in VALIDATE


# --- C2: S9's inverted guard ---------------------------------------------

def test_s9_fails_when_no_art_is_staged_at_all():
    """The inversion. `Test-Path $stagedArt` was the ENTRY condition.

    deploy.ps1 creates `images\\cards` only when it finds sources, so the one
    case this rule exists for -- art missing entirely -- made the missing-art
    gate silent. A gate whose precondition is the defect is not a gate.
    """
    block = VALIDATE[VALIDATE.index("$cardsRoot = Join-Path"):]
    block = block[:block.index("# ------", 10)]
    assert "-not (Test-Path $stagedArt)" in block, block
    assert "has no images\\cards directory at all" in block


def test_s9_no_longer_stops_at_the_first_portrait_it_finds():
    """One hit per character proved a directory was wired and nothing else.

    No gate anywhere asserted per-card completeness -- art_coverage.py's test
    deliberately does not, because it bills against the sheets rather than
    against the package -- so a partial copy shipped blank cards silently.
    """
    block = VALIDATE[VALIDATE.index("$cardsRoot = Join-Path"):]
    block = block[:block.index("# ------", 10)]
    assert "break" not in code_only(block), (
        "the first-hit break is back; S9 is again proving only that a "
        "directory was wired")
    assert "$missing.Count -gt 0" in block
    assert "did not reach" in block


# --- C3: art_lint is wired in --------------------------------------------

def test_art_lint_is_a_validate_rule():
    """It was the largest lint in the repo and no gate ran it."""
    assert "tools\\art_lint.py" in VALIDATE
    assert "Fail 'S10'" in VALIDATE
    assert "$artOut = Invoke-RepoPython $artLint" in VALIDATE


# --- C4: the derived contract + loud skips -------------------------------

def test_every_copy_block_skip_is_announced():
    """They skipped silently; missing salon art shipped with all gates green.

    Counted rather than spot-checked: each `Note-Skip` is one copy block that
    can now say it did nothing, and the count must not quietly shrink.
    """
    assert BUILD_PCK.count("Note-Skip") >= 5, (
        "a copy block lost its skip announcement")
    assert "copy block(s) SKIPPED" in BUILD_PCK, (
        "the end-of-run summary is gone; a warning buried in 200 lines of "
        "build output is how these were missed the first time")


def test_the_contract_version_moved_with_its_meaning():
    """v2 was hand-written, v3 is derived. That is a contract change."""
    assert "contract=roster-pck-v3" in BUILD_PCK
    assert "roster-pck-v2" not in BUILD_PCK
    assert "contract=roster-pck-v3" in VALIDATE
    # Comment-stripped: the S2 comment legitimately EXPLAINS why a v2 contract
    # is stale by definition, and that sentence is not a v2 check.
    assert "roster-pck-v2" not in code_only(VALIDATE)


# --- C6: the timing attribution ------------------------------------------

def test_the_false_stall_claim_is_gone():
    """R70's note blamed a 0.17s command for an 84s gate.

    Measured this sprint: `tools.build_ironclad_sheet --verify` is 0.17s; the
    full gate is 84.0s, of which the pytest suite is 78.4s. There was no stall
    to bound or cache -- the cost is the suite, and the suite is the point.
    """
    assert "S7's game_ref verification takes minutes" not in VALIDATE, (
        "the unmeasured stall claim is back; it was the stated rationale for "
        "a design decision and it was false")
    assert "C6 CORRECTION" in VALIDATE


def test_the_gate_prints_its_own_timing_breakdown():
    """A number nobody prints is a number somebody will guess."""
    assert "$swTotal = [Diagnostics.Stopwatch]::StartNew()" in VALIDATE
    assert "timing: total" in VALIDATE
    assert "S7 suite" in VALIDATE


def test_static_only_cannot_be_mistaken_for_a_full_pass():
    """A fast mode that could read as a full pass is R70's failure class
    wearing the opposite coat, so it announces itself twice: a banner where
    the suite would have run, and in the final verdict line."""
    assert "[switch]$StaticOnly" in VALIDATE
    assert "S7 DID NOT RUN THE SUITE" in VALIDATE
    assert "STATIC ONLY -- the suite did not run" in VALIDATE


def test_deploy_never_passes_static_only():
    """The fast path is for the inner loop; the deploy gate stays whole."""
    deploy = (ROOT / "klee-mod" / "build" / "deploy.ps1").read_text(
        encoding="utf-8")
    assert "StaticOnly" not in deploy
