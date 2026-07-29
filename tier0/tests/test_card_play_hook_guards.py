"""Unguarded `cardPlay.Card.Owner` in a card-played broadcast — the black-screen class.

THE BUG THIS EXISTS FOR (2026-07-29). `FurinaResourceHooks.BeforeCardPlayed`
and `AfterCardPlayed` walked `cardPlay.Card.Owner.Creature` seven times with no
null check. `Owner` is null on real paths — autoplay and token plays hand a card
to this broadcast with no Player attached — and these two hooks fire for EVERY
card EVERY player plays. The NRE lands inside CombatManager's async
continuation, so the queue never completes: the player does not get a crash or
an error dialog, they get a black screen and a dead run. The same file already
took exactly this guard one method away (`FurinaBurstResource.DrainOnPlay`),
which is what makes it a slip rather than a judgement call.

WHY A SOURCE LINT. There is no C# test project (docs/coop-no-sim-backstop.md),
the mod's bite-check harness only patches and reports (it cannot construct a
Godot `CardPlay`), and the tier0 sim has no notion of a null owner because it
never models one. So the only place this class of defect is visible before a
playtest is the source text. Same reasoning as
tier0/tests/test_canonical_model_misuse.py and tier0/tests/test_coop_ownership.py.

WHAT THIS CHECKS. Inside klee-mod, no `.Card.Owner.` (or `.Card!.Owner.`)
member access that is not null-guarded — `?.` on both links, or an `is { }`
pattern that binds first. Assignment to a local and then dereferencing the local
is the shape the fixed hooks use, and it passes because the local dereference no
longer names `.Card.Owner`.
"""

from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_CS = _ROOT / "klee-mod" / "KleeCode"

# `.Card.Owner.` / `.Card!.Owner.` -- an unguarded two-link walk. The guarded
# forms all put a `?` before at least one `.`, so they do not match.
_UNGUARDED = re.compile(r"\.Card!?\.Owner\.")

# Sites where the walk is provably safe and the guard would be noise. Curated
# rather than pattern-matched: "is Owner reachable here" is a fact about the
# caller, not about this line, so it gets written down when it is decided.
# Format: "<relative path>:<line text fragment>" -> why.
_ALLOWED: dict[str, str] = {}


def _sources() -> list[Path]:
    return [
        path
        for path in sorted(_CS.rglob("*.cs"))
        if not any(part in ("bin", "obj") for part in path.parts)
    ]


def test_no_unguarded_card_owner_walk() -> None:
    offenders: list[str] = []
    for path in _sources():
        rel = path.relative_to(_ROOT).as_posix()
        for number, line in enumerate(
            path.read_text(encoding="utf-8").splitlines(), start=1
        ):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("///"):
                continue
            if not _UNGUARDED.search(stripped):
                continue
            if any(
                key.startswith(rel) and key.split(":", 1)[1] in stripped
                for key in _ALLOWED
            ):
                continue
            offenders.append(f"{rel}:{number}: {stripped}")

    assert not offenders, (
        "unguarded cardPlay.Card.Owner walk (null on autoplay/token plays; "
        "an NRE here soft-locks the run inside CombatManager's continuation).\n"
        "Guard with `?.` on both links, or bind the owner first:\n"
        "    if (cardPlay.Card?.Owner?.Creature is not { } owner) return;\n"
        + "\n".join(offenders)
    )
