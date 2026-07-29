"""The Salon counter's cap clamp must bound the RESULT, not the delta.

THE BUG THIS EXISTS FOR (2026-07-29). `SalonMemberPower` mirrors the company
list: the list is authoritative and the power's `Amount` follows it, so both
`Deploy` (positive delta) and `BowLeftmost` (always-negative delta) apply a
delta through `PowerCmd.Apply<SalonMemberPower>`. The cap was enforced with

    modifiedAmount = Math.Max(0m, Math.Min(amount, SlotsFor(target) - Amount));

which is a clamp on the DELTA. It reads correctly for a deploy and silently
destroys every bow: `Math.Max(0m, ...)` turns any negative delta into 0, so the
counter could never go down. Take Your Bow (shipped) removed members from the
list, the counter stayed put, and for the rest of that combat the badge, the
stage and every per-member payer (Dinner Service, House Call) kept counting
performers who had already left.

WHY A SOURCE LINT. `TryModifyPowerAmountReceived` needs a live `Creature` and a
live `PowerModel` to call, so it is unreachable from the Python sim and from the
mod's bite-check harness (which only patches and reports — it cannot touch a
Godot object). The expression itself is the artefact that can be checked.

WHAT THIS CHECKS. The clamp names `Amount + amount` — i.e. it bounds the
resulting counter — and the old delta-clamping shape does not reappear.
"""

from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
_SALON = _ROOT / "klee-mod" / "KleeCode" / "Powers" / "SalonPowers.cs"

# The shape that shipped the bug: Math.Max(0m, Math.Min(amount, ...)).
_DELTA_CLAMP = re.compile(r"Math\.Max\(\s*0m\s*,\s*Math\.Min\(\s*amount\s*,")


def _body() -> str:
    """SalonMemberPower.TryModifyPowerAmountReceived, source text."""
    source = _SALON.read_text(encoding="utf-8")
    start = source.index("public override bool TryModifyPowerAmountReceived")
    end = source.index("\n    }\n", start)
    return source[start:end]


def test_clamp_bounds_the_resulting_counter() -> None:
    body = _body()
    assert "Amount + amount" in body, (
        "SalonMemberPower's cap clamp no longer bounds the RESULTING counter. "
        "Clamping the DELTA is what zeroed every bow's negative apply and "
        "desynced the counter from the company list for a whole combat."
    )


def test_old_delta_clamp_is_gone() -> None:
    body = _body()
    assert not _DELTA_CLAMP.search(body), (
        "Math.Max(0m, Math.Min(amount, ...)) is back in "
        "SalonMemberPower.TryModifyPowerAmountReceived. That expression floors "
        "the DELTA at zero, so BowLeftmost's (always-negative) mirror apply "
        "never lands."
    )
