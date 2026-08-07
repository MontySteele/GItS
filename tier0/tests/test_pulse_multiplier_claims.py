"""Every live PROSE statement of the Kurage pulse multiplier must match it.

Addendum A7 (Neap Tide, 2026-07-26). `KURAGE_PULSE_PER_CHARGE` moved 4 -> 3
during the sprint, and the number itself was updated in one place. The SENTENCES
about it were updated in none, and there were five of them:

  * the `CONSTANTS_VERSION 4` comment said "4 -> 2" -- naming the ruled value
    over the landed one, which files every current Kokomi number in a world
    that never shipped (A1c);
  * `exp_neap_tide_e1`'s docstring called x2 "the shipped value" -- in the very
    script whose result was that x2 does not ship;
  * `kokomi-playtest-protocol.md` stated x4 twice (as did the since-retired
    `open-playtest-items.md` register), in the standing-flag list and the Q4
    row that playtest three reads.

None of that is catchable by `lint_constant_parity`, which compares C# constants
against Python constants and never reads a sentence. And prose is exactly where
a stale multiplier does its damage: a playtest protocol is a set of instructions
to a person, and a person told to watch for "44 at bank 10" will not notice that
the build hits for 34.

WHY A CURATED CLAIM LIST RATHER THAN A SCAN. A scan for "x4" anywhere near the
word "pulse" would have to distinguish a live claim from a historical record,
and both are legitimate: `DECISIONS.md` SHOULD say 4, the E1 arms ARE x4/x3/x2,
and the WATCH block quotes x5 on purpose. A regex cannot tell a record from a
claim; an author can. So each live claim is registered here as a format string
over the constant, and the test asserts the rendered string is present. When the
knob moves, this fails and names the exact sentence to rewrite -- which is the
whole job, since the failure mode is not "wrong value" but "nobody remembered
this sentence existed".

Both directions, as usual: a registered claim whose file no longer contains it
fails too, so a rewritten paragraph cannot silently drop its own pin.
"""

from __future__ import annotations

import re
from pathlib import Path

from tier0 import constants as C

ROOT = Path(__file__).resolve().parents[2]

# {relative path: [claim templates]}. `{v}` renders the current multiplier.
# Add a row here when you write a NEW sentence that states the live value --
# not when you write one that quotes a historical value.
LIVE_CLAIMS: dict[str, list[str]] = {
    "tier0/constants.py": [
        # A1c: the comparability stamp must name the LANDED value.
        "4 -> {v} (ruled 2; E1 fired the pre-committed x{v} fallback)",
        # A1b: the restored WATCH block's worked example.
        "WORKED EXAMPLE, at the LANDED x{v}",
    ],
    "docs/current/playtest/kokomi-playtest-protocol.md": [
        # The standing-flag list -- what playtest three is told to watch.
        "`KuragePulsePerCharge = {v}`",
        "reads the bank at ×{v}",
    ],
}

# Worked-example rows in the constants comment: "bank 10, x3  pulse 4 + 30 = 34".
# These are arithmetic, so they are checked as arithmetic rather than as text.
# A worked example that has drifted is worse than none: it reads like a check.
WORKED_EXAMPLE = re.compile(
    r"bank (\d+), x(\d+).*?pulse (\d+) \+ (\d+) =\s*(\d+)")


def test_every_live_claim_states_the_current_multiplier():
    missing = []
    for rel, templates in sorted(LIVE_CLAIMS.items()):
        path = ROOT / rel
        assert path.exists(), f"{rel} is registered here but does not exist"
        src = path.read_text(encoding="utf-8")
        for template in templates:
            claim = template.format(v=C.KURAGE_PULSE_PER_CHARGE)
            if claim not in src:
                missing.append(f"{rel}: {claim!r}")
    assert not missing, (
        "KURAGE_PULSE_PER_CHARGE is "
        f"{C.KURAGE_PULSE_PER_CHARGE}, but these registered live claims do not "
        "say so (rewrite the sentence, then the template here if its shape "
        "changed):\n  " + "\n  ".join(missing))


def test_the_worked_example_is_arithmetic_that_still_holds():
    src = (ROOT / "tier0" / "constants.py").read_text(encoding="utf-8")
    rows = WORKED_EXAMPLE.findall(src)
    assert rows, ("the WATCH block's worked example is gone. It is the only "
                  "place a reader can check the reader-hierarchy claim against "
                  "numbers; restore it rather than deleting this test.")

    for bank, mult, base, product, total in rows:
        bank, mult = int(bank), int(mult)
        base, product, total = int(base), int(product), int(total)
        assert base == C.KURAGE_PULSE_BASE, (
            f"worked example row 'bank {bank}, x{mult}' uses base {base}, but "
            f"KURAGE_PULSE_BASE is {C.KURAGE_PULSE_BASE}")
        assert bank * mult == product, (
            f"worked example row 'bank {bank}, x{mult}' claims {product}, "
            f"but {bank} * {mult} = {bank * mult}")
        assert base + product == total, (
            f"worked example row 'bank {bank}, x{mult}' sums to {total}, "
            f"but {base} + {product} = {base + product}")

    # At least one row must be at the LIVE multiplier. Rows above it are there
    # on purpose (a drafted "Before Sun and Moon" stacks the coefficient), so
    # the check is presence of the baseline, not absence of the others.
    assert any(int(m) == C.KURAGE_PULSE_PER_CHARGE for _, m, _, _, _ in rows), (
        f"no worked-example row is at the live multiplier "
        f"x{C.KURAGE_PULSE_PER_CHARGE}; every row shows a stacked or historical "
        "read, so the baseline is undocumented")
