"""S12's portable half: the deferred-art allowlist cannot go stale.

Kokomi playtest, 2026-07-26. Her starter relic rendered the base-game
placeholder and her Burst gauge had no cap icon, because two PNGs were
referenced and never made. The game logged both misses once per session and no
gate said anything, because S6c -- the rule that looks like it covers this --
inspects only `: CustomCharacterModel` classes and only `.tscn|.tres`. No PNG
in the pck had ever been checked by any rule.

validate.ps1 S12 now sweeps every C# pck reference against the STAGED CONTRACT,
which is the honest place to ask the question: the contract is the manifest of
what the exporter actually packed. That check cannot live here, because the
contract and the art are both gitignored Tier F and absent on a clean machine.

What IS portable is allowlist hygiene, and that is the half that rots. The
deferred list is the only part of S12 that can silently stop describing
reality: art lands, or the last reference to it is deleted, and the entry sits
there exempting nothing. Since a stale exemption is how the NEXT missing asset
gets waved through, it is worth a test that runs everywhere -- including on
machines that have no pck to validate against.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "klee-mod" / "KleeCode"
VALIDATE = (ROOT / "klee-mod" / "build" / "validate.ps1").read_text(
    encoding="utf-8")


def _deferred_paths() -> list[str]:
    """The keys of validate.ps1's $pckDeferred hashtable."""
    start = VALIDATE.index("$pckDeferred = @{")
    body = VALIDATE[start:VALIDATE.index("\n}", start)]
    return re.findall(r"^\s*'([^']+)'\s*=", body, re.MULTILINE)


def _cs_text() -> str:
    return "\n".join(
        p.read_text(encoding="utf-8") for p in SOURCE.rglob("*.cs"))


def test_the_gate_is_wired():
    """S12 exists and sweeps the whole mod, not one class shape.

    The defect it replaces was a rule that scanned the wrong scope and passed
    for its entire life, so 'the rule is present' is worth asserting directly.
    """
    assert "S12" in VALIDATE, "validate.ps1 has no S12 rule"
    assert "$pckDeferred" in VALIDATE, "S12 lost its deferred-art allowlist"
    # Derived namespaces, not a hardcoded list: a new top-level pck directory
    # must be swept the day it appears.
    assert "$nsAlt" in VALIDATE and "namespaces" in VALIDATE, (
        "S12 must derive pck namespaces from the contract; a literal list "
        "would silently stop covering a new character's directory")


def test_deferred_entries_are_still_referenced():
    """Every exemption still names art some C# file actually asks for.

    If the last reference goes away, the entry is exempting nothing and must
    be deleted. S12 fails on this too, but only where a staged pck exists;
    this is the copy that runs on a clean checkout.
    """
    # The list may legitimately be EMPTY -- it was, from EB-65 on 2026-09-02,
    # when the last seven entries' art landed. Emptiness is the goal state of
    # a deferral list, not a parse failure, so this asserts the hashtable is
    # still THERE (test_the_gate_is_wired) and that whatever it holds is live.
    assert "$pckDeferred = @{" in VALIDATE, (
        "the deferred hashtable moved or was renamed; _deferred_paths parses "
        "it by that literal and would silently return [] for a real list")
    deferred = _deferred_paths()

    cs = _cs_text()
    orphans = [p for p in deferred if p not in cs]
    assert not orphans, (
        "deferred pck art that no C# file references any more: "
        f"{orphans}. Drop the entry from validate.ps1's $pckDeferred -- an "
        "exemption that exempts nothing is how the next missing asset gets "
        "waved through.")


def test_every_deferred_entry_carries_a_reason():
    """An allowlist of bare paths is a mute list.

    The reason is what lets a later reader tell 'deliberately deferred, safe'
    from 'somebody silenced the gate'.
    """
    start = VALIDATE.index("$pckDeferred = @{")
    body = VALIDATE[start:VALIDATE.index("\n}", start)]
    for path in _deferred_paths():
        entry = body[body.index(f"'{path}'"):]
        entry = entry[:entry.index("\n    '")] if "\n    '" in entry else entry
        assert len(entry) > len(path) + 40, (
            f"{path} is deferred with no stated reason")
