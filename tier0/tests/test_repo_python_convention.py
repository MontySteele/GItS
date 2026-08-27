"""Every native invocation in a build script goes through the EAP helper.

Audit sec.3.4 / sec.4 item 4. Windows PowerShell 5.1 traps native stderr in BOTH
directions when `$ErrorActionPreference` is `'Stop'`:

  * `2>&1` wraps each stderr line in an ErrorRecord and raises
    `NativeCommandError`;
  * **not** redirecting is no safer -- native stderr raises
    `NativeCommandError` *even when the command exits 0*.

Both halves have taken this repo's deploy down. `lint_constant_parity` grew a
reader importing `tier05.relics`, which emits three house-rule `UserWarning`s
on stderr at import: the lint passed, printed "constant parity: OK", and
killed the deploy anyway (2026-07-25). The same shape sat unfixed in
`build_pck.ps1`, where one Godot deprecation warning was enough to kill a pck
build, until the Serenitea Sweep.

The fix is a helper that lowers EAP to `'Continue'` for the duration of the
call. Nothing enforced that new call sites use it -- which is why this file
exists. The convention is only worth having if it cannot be quietly dropped
by the next person who needs to shell out.

This is a source-text lint because there is no way to execute PS 5.1 semantics
from pytest, and because the deploy machine is the only host that runs these
scripts at all (audit sec.3.9): a convention enforced only where it is already
followed is not enforced.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

# Scope: every PowerShell script this repo ships. deploy.ps1 and version.ps1
# have no native call sites today -- they are in scope precisely so that the
# first one added has to answer to this.
SCRIPTS = [
    ROOT / "klee-mod" / "build" / "validate.ps1",
    ROOT / "tools" / "build_pck.ps1",
    ROOT / "klee-mod" / "build" / "deploy.ps1",
    ROOT / "klee-mod" / "build" / "version.ps1",
    # The DEV deploy (R213 B's quarantined prototype surface). In scope for
    # the same reason as the two above it, and unlike them it DOES shell out:
    # it runs `tools/gen_prototype_cards.py --check` before building anything,
    # because validate.ps1's S6a staleness gate reads the ROSTER codegen and
    # cannot see that surface.
    ROOT / "klee-mod" / "build" / "deploy_proto.ps1",
]

# The helpers. A call site inside one of these bodies is the implementation,
# not a violation -- that is the ONE place the raw `& exe ... 2>&1` is correct,
# because it is wrapped in the EAP swap.
HELPERS = ("Invoke-RepoPython", "Invoke-NativeCaptured")


def _lines(path: Path):
    return path.read_text(encoding="utf-8").splitlines()


def _helper_body_lines(lines) -> set[int]:
    """1-indexed line numbers inside a helper function's braces."""
    inside: set[int] = set()
    for i, line in enumerate(lines, 1):
        if not re.match(r"\s*function\s+(" + "|".join(HELPERS) + r")\b", line):
            continue
        depth = 0
        started = False
        for j in range(i, len(lines) + 1):
            depth += lines[j - 1].count("{") - lines[j - 1].count("}")
            started = started or "{" in lines[j - 1]
            inside.add(j)
            if started and depth <= 0:
                break
    return inside


def _is_comment(line: str) -> bool:
    return line.lstrip().startswith("#")


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.name)
def test_no_native_call_site_bypasses_the_helper(script: Path):
    """`& $exe` outside a helper body is the bug, whether or not it redirects.

    Both spellings are caught: the redirect form raises on any stderr line,
    and the bare form raises on any stderr line too. There is no safe way to
    write this inline, so the lint does not try to distinguish them.
    """
    lines = _lines(script)
    exempt = _helper_body_lines(lines)
    offenders = [
        (i, line.strip()) for i, line in enumerate(lines, 1)
        if i not in exempt and not _is_comment(line)
        and re.search(r"&\s*\$\w+", line)
    ]
    assert not offenders, (
        f"{script.name}: native invocation outside {HELPERS}:\n" +
        "\n".join(f"  :{i}  {t}" for i, t in offenders))


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.name)
def test_the_only_stderr_redirect_is_inside_a_helper(script: Path):
    lines = _lines(script)
    exempt = _helper_body_lines(lines)
    offenders = [
        (i, line.strip()) for i, line in enumerate(lines, 1)
        if i not in exempt and not _is_comment(line) and "2>&1" in line
    ]
    assert not offenders, (
        f"{script.name}: 2>&1 outside {HELPERS}:\n" +
        "\n".join(f"  :{i}  {t}" for i, t in offenders))


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.name)
def test_bare_interpreter_names_are_never_invoked(script: Path):
    """`python` / `python3` resolve to whatever is on PATH, not the repo venv.

    Distinct failure from the stderr trap and worth its own assertion: the
    gates measure the repo's pinned environment or they measure nothing.
    Prose is exempt -- the S7 failure message legitimately TELLS the operator
    to run `python -m tools.extract_base_game_pool`, and instructing a human
    is not invoking an interpreter.
    """
    offenders = []
    for i, line in enumerate(_lines(script), 1):
        if _is_comment(line):
            continue
        stripped = re.sub(r'"[^"]*"|\'[^\']*\'', "", line)   # drop string bodies
        if re.search(r"(?<![\w.\\$/-])python3?(\.exe)?\b", stripped):
            offenders.append((i, line.strip()))
    assert not offenders, (
        f"{script.name}: bare interpreter invocation:\n" +
        "\n".join(f"  :{i}  {t}" for i, t in offenders))


def test_both_build_scripts_actually_define_a_helper():
    """Guards the lint against passing by vacuum.

    Every assertion above is "no offenders". Delete the helper and inline
    nothing, and they all pass while the convention no longer exists. The two
    scripts that shell out must each carry one.
    """
    for script in (ROOT / "klee-mod" / "build" / "validate.ps1",
                   ROOT / "tools" / "build_pck.ps1"):
        text = script.read_text(encoding="utf-8")
        assert any(re.search(rf"function\s+{h}\b", text) for h in HELPERS), \
            f"{script.name} shells out but defines no EAP-lowering helper"


@pytest.mark.parametrize(
    "script", [ROOT / "klee-mod" / "build" / "validate.ps1",
               ROOT / "tools" / "build_pck.ps1"],
    ids=lambda p: p.name)
def test_the_helper_lowers_error_action_preference_and_restores_it(script: Path):
    """The helper's whole job, asserted rather than assumed.

    A helper that redirects without the EAP swap is worse than the bare call
    it replaced: it looks like the convention while re-arming the trap.
    """
    text = script.read_text(encoding="utf-8")
    swappers = 0
    for helper in HELPERS:
        if not re.search(rf"function\s+{helper}\b", text):
            continue
        body = text[text.index(f"function {helper}"):]
        body = body[:body.index("\n}") + 2]
        # A helper may either do the swap itself or delegate to a sibling that
        # does (build_pck's Invoke-RepoPython is a thin $py wrapper over
        # Invoke-NativeCaptured). What is NOT allowed is a helper that
        # redirects on its own without the swap -- that looks like the
        # convention while re-arming the trap.
        delegates = any(
            other != helper and re.search(rf"\b{other}\b", body)
            for other in HELPERS)
        if delegates:
            assert "2>&1" not in body, (
                f"{helper} delegates AND redirects; the redirect belongs to "
                "exactly one layer")
            continue
        swappers += 1
        assert "$ErrorActionPreference = 'Continue'" in body, helper
        assert "finally" in body and "$ErrorActionPreference = $prev" in body, (
            f"{helper} must restore EAP in a finally block -- an early return "
            "or a throw inside the call would otherwise leave the whole script "
            "running at 'Continue'")
    assert swappers >= 1, (
        f"{script.name} defines helpers that all delegate and none that swaps "
        "EAP -- the chain has to bottom out somewhere")
