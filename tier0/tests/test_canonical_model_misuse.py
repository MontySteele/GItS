"""Handing a CANONICAL model to a command that mutates it — the softlock class.

THE BUG THIS EXISTS FOR (2026-07-26, Bake-Kurage). `KurageSummon.Field` called
the non-generic `PowerCmd.Apply` and passed it
`ModelDb.Power<KurageSummonPower>()` — the canonical prototype, which is
immutable. That overload's second statement is `power.AssertMutable()`, which
throws `CanonicalModelException`. The generic `Apply<T>` is the overload that
does the missing `powerModel.ToMutable()` first.

WHY IT COST A PLAYTEST RATHER THAN A COMPILE. Every layer of the build is
happy: it compiles, the boot self-check passes (this is a play-time path, not a
registration one), and there is no C# test project to execute it. The exception
lands inside an awaited action in the command queue, so the queue never
completes and the game **softlocks** — it does not crash, and nothing in the log
names a card. The only detector was a person playing the card.

WHAT THIS CHECKS. A `ModelDb.Xxx<T>()` lookup passed as an argument, or
assigned and then passed, to a command that mutates it, without `.ToMutable()`.
Vanilla's own code shows the correct idiom in both directions:

    TouchOfOrobas t = (TouchOfOrobas)ModelDb.Relic<TouchOfOrobas>().ToMutable();
    power = ModelDb.Power<T>().ToMutable();

Source-level, because there is no runtime here to catch it in. See
tier0/tests/test_coop_ownership.py for the same reasoning applied to co-op.
"""

from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_CS = _ROOT / "klee-mod" / "KleeCode"

# `ModelDb.Power<X>()` / `ModelDb.Relic<X>()` / `ModelDb.Card<X>()` etc.
_LOOKUP = re.compile(r"ModelDb\.\w+<\s*\w+\s*>\s*\(\s*\)")

# Commands whose non-generic overloads call AssertMutable on the model they are
# handed. Add to this as the assembly reaches for more of them; the point is
# the LIST is curated and visible, not that it is exhaustive today.
_MUTATING_CALLS = (
    "PowerCmd.Apply(",
    "PowerCmd.ModifyAmount(",
    "RelicCmd.Replace(",
)

# Call sites where a canonical lookup is CORRECT because the callee only reads
# identity (pool membership, id comparison, ledger entries) and never mutates.
# Curated rather than pattern-matched: "does this callee mutate" is not
# derivable from the call site, so it is a decision that gets written down.
_READ_ONLY_OK: dict[str, str] = {}


def _sites() -> list[tuple[Path, int, str]]:
    out = []
    for path in _CS.rglob("*.cs"):
        if any(part in ("bin", "obj") for part in path.parts):
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        for n, line in enumerate(lines, 1):
            out.append((path, n, line))
    return out


def test_no_canonical_model_reaches_a_mutating_command():
    """A canonical lookup passed to a mutating command, without .ToMutable().

    Scans the call and the two lines after it, because these calls are
    routinely wrapped across lines by the formatter -- the Bake-Kurage bug was
    spelled across three.
    """
    offenders = []
    sites = _sites()
    by_file: dict[Path, list[str]] = {}
    for path, _n, line in sites:
        by_file.setdefault(path, []).append(line)

    for path, lines in by_file.items():
        for i, line in enumerate(lines):
            if not any(call in line for call in _MUTATING_CALLS):
                continue
            window = "\n".join(lines[i:i + 3])
            for match in _LOOKUP.finditer(window):
                tail = window[match.end():match.end() + 16]
                if tail.lstrip().startswith(".ToMutable()"):
                    continue
                key = f"{path.relative_to(_ROOT)}:{i + 1}"
                if key in _READ_ONLY_OK:
                    continue
                offenders.append(
                    f"{key}: {match.group(0)} passed to a mutating command "
                    f"without .ToMutable() -- AssertMutable will throw and "
                    f"the action queue will softlock\n      {line.strip()}")

    assert not offenders, (
        "canonical model handed to a mutating command:\n  "
        + "\n  ".join(offenders)
        + "\n\nUse the GENERIC overload (PowerCmd.Apply<T>) which calls "
          "ToMutable() for you, or call .ToMutable() explicitly.")


def test_kurage_uses_the_generic_apply():
    """The specific regression, pinned by name.

    The general scan above would catch a literal repeat, but not somebody
    'fixing' this by reintroducing the non-generic call with a mutable local
    obtained some other way. This card is the one we know softlocks.
    """
    src = (_CS / "Powers" / "KuragePowers.cs").read_text(encoding="utf-8")
    assert "PowerCmd.Apply<KurageSummonPower>(" in src, (
        "KurageSummon.Field no longer uses the generic PowerCmd.Apply<T>; "
        "the non-generic overload asserts mutability on the model it is "
        "handed and softlocks on the first Bake-Kurage of a combat")
