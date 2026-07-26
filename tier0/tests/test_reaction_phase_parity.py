"""C# reaction PHASE parity — the axis the constant-parity lint cannot see.

Audit sec.4 item 1. The three reaction fixes of the 2026-07-21 bug hunt
(`git show --stat cdd2aff`: 13 files, 0 tests) each corrected *which hook a
piece of damage rides*, not what it was worth. Each was a 30-50% divergence
from tier0. Each shipped unpinned.

S6e (`lint_constant_parity.py`) is green on `ShatterDamage`,
`VulnerableTakenMult` and the aura duration — the three *numbers* — which
reads as coverage of the three *phases* it does not touch at all. A future
edit that moves Shatter back into `ModifyDamageAdditive` keeps every constant
correct and re-opens a sim-21/game-24 divergence with the whole lint suite
green.

CURATED LEDGER, the house pattern (`lint_pool_membership`, `art_lint`'s
KNOWN sets). Each row is a phase decision that was PAID FOR by a measured
divergence, with the divergence recorded next to it. A row is not "where the
code happens to be today" — it is a decision with a receipt. Adding a row
means a new phase decision was made; deleting one means it was reversed, and
that needs the same kind of evidence the original did.

These are source-text assertions on purpose. The failures they guard live in
hook dispatch inside a compiled Godot run and are invisible to the simulator,
so there is nothing to execute; what can be checked is that the override the
fix chose is still the override the code declares.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "klee-mod" / "KleeCode"


def method_body(source: str, signature_re: str) -> str:
    """The braced body of the first method whose signature matches.

    Brace-counting rather than regex-to-closing-brace: these bodies contain
    nested blocks and object initializers, and a lazy match would silently
    truncate to the first `}` and make every "must not appear" assertion below
    pass by looking at less code than it claims to.
    """
    match = re.search(signature_re, source)
    assert match, f"no method matching {signature_re!r}"
    start = source.index("{", match.end())
    depth = 0
    for i in range(start, len(source)):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                return source[start:i + 1]
    raise AssertionError(f"unbalanced braces after {signature_re!r}")


# file, hook, signature regex
_AURA = ("Powers/AuraPower.cs",)
_FROZEN = ("Powers/FrozenPower.cs",)

# Each row: (id, file, the hook the decision put it IN, signature regex,
#            tokens that MUST appear in that body,
#            tokens that must appear in NO OTHER hook of the same file,
#            the measured divergence that bought the decision)
PHASE_LEDGER = [
    (
        "superconduct-vulnerable-is-multiplicative",
        "Powers/AuraPower.cs",
        "ModifyDamageMultiplicative",
        r"public\s+override\s+decimal\s+ModifyDamageMultiplicative\s*\(",
        ["Reaction.Superconduct", "ReactionConstants.VulnerableTakenMult"],
        ["ReactionConstants.VulnerableTakenMult"],
        "card-triggered Superconduct dealt 10 where the sim dealt 15, while "
        "the same reaction off a bomb correctly dealt 15 -- one reaction, two "
        "payouts. The sim's modify_damage_taken is a flat x1.5 in the "
        "multiplicative phase.",
    ),
    (
        "shatter-is-dealt-from-after-damage-received",
        "Powers/FrozenPower.cs",
        "AfterDamageReceived",
        r"public\s+override\s+async\s+Task\s+AfterDamageReceived\s*\(",
        ["ReactionConstants.ShatterDamage", "CreatureCmd.Damage"],
        ["ReactionConstants.ShatterDamage"],
        "as a ModifyDamageAdditive override the bonus scaled with Vulnerable "
        "AND was absorbed by enemy Block; the sim does neither (raw "
        "`enemy.hp -=` after block subtraction). Frozen + Vulnerable 2 on a "
        "10-damage attack: sim 21, game 24. Into 12 Block: sim 6, game 4.",
    ),
    (
        "aura-ticks-after-side-turn-start",
        "Powers/AuraPower.cs",
        "AfterSideTurnStart",
        r"public\s+override\s+async\s+Task\s+AfterSideTurnStart\s*\(",
        ["PowerCmd.TickDownDuration"],
        ["PowerCmd.TickDownDuration"],
        "ticking in AfterSideTurnEnd(Enemy) put the expiry BEFORE "
        "BombPower.BeforeSideTurnStart, exactly backwards from tier0's "
        "'bombs detonate -> auras tick'. An aura on its last turn expired "
        "before the start-of-turn detonation could react with it: a Hydro "
        "aura + a bomb lost its Vaporize, and the detonation then left a "
        "fresh Pyro aura the sim never creates.",
    ),
]

# Every hook override this repo's powers can plausibly ride. Used to prove a
# token appears in the ledger's hook and in NO other one -- the check that
# actually fails when a fix is reverted by moving code to a sibling override.
ALL_HOOKS = [
    "ModifyDamageAdditive", "ModifyDamageMultiplicative",
    "AfterDamageReceived", "BeforeDamageReceived",
    "BeforeSideTurnStart", "AfterSideTurnStart",
    "BeforeSideTurnEnd", "AfterSideTurnEnd",
]


@pytest.mark.parametrize(
    "row", PHASE_LEDGER, ids=[r[0] for r in PHASE_LEDGER])
def test_phase_decision_still_rides_the_hook_it_was_fixed_into(row):
    _id, rel, hook, sig, must_have, _exclusive, receipt = row
    body = method_body((SOURCE / rel).read_text(encoding="utf-8"), sig)
    for token in must_have:
        assert token in body, (
            f"{rel}::{hook} no longer contains {token!r}.\n"
            f"That phase decision was paid for by: {receipt}"
        )


@pytest.mark.parametrize(
    "row", PHASE_LEDGER, ids=[r[0] for r in PHASE_LEDGER])
def test_phase_decision_did_not_migrate_to_a_sibling_hook(row):
    """The revert this actually guards: same constant, different override.

    A move back to the pre-fix hook keeps every S6e constant green, so the
    'must appear here' assertion above is only half the pin. This is the
    other half.
    """
    _id, rel, hook, _sig, _must, exclusive, receipt = row
    source = (SOURCE / rel).read_text(encoding="utf-8")
    for other in ALL_HOOKS:
        if other == hook:
            continue
        pattern = rf"public\s+override\s+\S+(?:\s+\S+)?\s+{other}\s*\("
        if not re.search(pattern, source):
            continue
        body = method_body(source, pattern)
        for token in exclusive:
            assert token not in body, (
                f"{rel}::{other} now contains {token!r}, which belongs to "
                f"{hook} alone.\nThat phase decision was paid for by: {receipt}"
            )


def test_shatter_is_emitted_unblockable_and_unpowered():
    """The two flags are the whole parity argument, not decoration.

    Unblockable mirrors the sim's raw `enemy.hp -=` (dealt AFTER the main
    hit's block subtraction). Unpowered keeps the Shatter from re-entering
    this same hook or early-detonating bombs -- which is what the sim's
    `source == "attack"` gate prevents on its side. Dropping either one
    re-opens a divergence while `ShatterDamage` stays correct.
    """
    body = method_body(
        (SOURCE / "Powers" / "FrozenPower.cs").read_text(encoding="utf-8"),
        r"public\s+override\s+async\s+Task\s+AfterDamageReceived\s*\(")
    call = body[body.index("CreatureCmd.Damage"):]
    assert "ValueProp.Unblockable" in call
    assert "ValueProp.Unpowered" in call
    # No dealer and no card source: the Overload-splash idiom. A dealer here
    # would let dealer-keyed powers (Vermillion Pact's amp) ride a bonus the
    # sim adds unamplified.
    assert re.search(r"dealer:\s*null", call), call
    assert re.search(r"cardSource:\s*null", call), call


def test_shatter_mirrors_the_sims_alive_gate():
    """`effects.py` only Shatters a living enemy: a hit that kills does not."""
    body = method_body(
        (SOURCE / "Powers" / "FrozenPower.cs").read_text(encoding="utf-8"),
        r"public\s+override\s+async\s+Task\s+AfterDamageReceived\s*\(")
    remove = body.index("PowerCmd.Remove")
    dead = body.index("IsDead")
    damage = body.index("CreatureCmd.Damage")
    # Frozen comes off even on a killing blow; the damage does not follow.
    assert remove < dead < damage, body


def test_aura_tick_is_gated_on_the_player_side():
    """AfterSideTurnStart fires for both sides; the sim ticks once per round."""
    body = method_body(
        (SOURCE / "Powers" / "AuraPower.cs").read_text(encoding="utf-8"),
        r"public\s+override\s+async\s+Task\s+AfterSideTurnStart\s*\(")
    assert "CombatSide.Player" in body, body


def test_superconduct_multiplier_is_pure():
    """ModifyDamageMultiplicative runs in preview and tooltip paths too.

    Consuming an aura or issuing a command from a phase the UI calls
    speculatively would apply reaction side effects for a hit that was never
    thrown. Consumption belongs in AfterDamageReceived, one hook over.
    """
    body = method_body(
        (SOURCE / "Powers" / "AuraPower.cs").read_text(encoding="utf-8"),
        r"public\s+override\s+decimal\s+ModifyDamageMultiplicative\s*\(")
    for forbidden in ("PowerCmd.Remove", "PowerCmd.ModifyAmount",
                      "ReactionEffects.Resolve", "CreatureCmd.Damage"):
        assert forbidden not in body, (
            f"{forbidden} in the multiplicative phase: this hook is called "
            "speculatively by preview/tooltip paths and must stay pure")
