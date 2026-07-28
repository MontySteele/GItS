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


# --- damage-modifier purity, swept repo-wide -------------------------------
#
# The test above pins ONE power by naming the commands it must not call. The
# 2026-07-27 co-op soft-lock got underneath exactly that shape of check:
# PreventExhaustWardPower's impurity was a plain FIELD ASSIGNMENT
# (`_usedThisTurn = true; _pendingExhaust = true;`), not a command call, in a
# file no ledger row named. So this sweep is unkeyed -- it visits every
# damage-modifier override in the mod and asks the structural question
# instead of the per-power one.

MODIFIER_HOOKS = ("ModifyDamageAdditive", "ModifyDamageMultiplicative")

# Commands that only LOOK up state. A modifier may call these; anything else
# with a Cmd receiver mutates the board from a hook the UI calls
# speculatively. Curated on purpose (the house pattern): adding a name here
# is a claim that the call is read-only, and it should be checked as one.
READONLY_CMDS = frozenset({"AuraCmd.Find"})

_FIELD_WRITE = re.compile(r"\b(_\w+)\s*(?:=(?!=)|\+\+|--|\+=|-=)")
_CMD_CALL = re.compile(r"\b(\w+Cmd\.\w+)")


def _modifier_bodies():
    """(path, hook, body) for every damage-modifier override in the mod.

    Not method_body(): that returns the FIRST match only, and several files
    declare more than one power class.
    """
    for path in sorted(SOURCE.rglob("*.cs")):
        source = path.read_text(encoding="utf-8")
        for hook in MODIFIER_HOOKS:
            pattern = rf"public\s+override\s+decimal\s+{hook}\s*\("
            for match in re.finditer(pattern, source):
                start = source.index("{", match.end())
                depth = 0
                for i in range(start, len(source)):
                    if source[i] == "{":
                        depth += 1
                    elif source[i] == "}":
                        depth -= 1
                        if depth == 0:
                            yield path.relative_to(SOURCE), hook, source[start:i + 1]
                            break


def test_the_sweep_actually_sees_the_modifiers():
    """A zero-row sweep is a green test that checks nothing."""
    rows = list(_modifier_bodies())
    assert len(rows) >= 8, f"only found {len(rows)} damage modifiers: {rows}"


@pytest.mark.parametrize(
    "rel,hook,body",
    list(_modifier_bodies()),
    ids=[f"{r}::{h}" for r, h, _ in _modifier_bodies()])
def test_damage_modifiers_are_pure(rel, hook, body):
    """Damage modifiers answer questions; they must not change answers.

    The engine calls these outside a play to build damage PREVIEWS -- the
    Beetle Swarm ruling's phrasing, "questions about the current board rather
    than about a cast in progress". Previews are local UI, so they run a
    different number of times on each co-op peer, and any state a modifier
    mutates therefore diverges between them.

    RECEIPT (2026-07-27 co-op playtest, godot.log checksums 576 and 49):
    PreventExhaustWardPower set its once-per-turn latch and armed its exhaust
    from inside ModifyDamageAdditive. A preview on one peer burned the latch
    the other still had, so the two disagreed about whether Vigil of the Deep
    had fired -- and one of them took a roll off the shared
    Rng.CombatTargets stream that the other did not. That desyncs every later
    roll in the run, so the host tripped StateDivergence and disconnected the
    client. Reliable, once per combat, on a rare the deck is built around.
    """
    writes = _FIELD_WRITE.findall(body)
    assert not writes, (
        f"{rel}::{hook} assigns to {writes}: a damage modifier is called "
        "speculatively by preview paths, so per-peer state written here "
        "desyncs co-op. Move the mutation to Before/AfterDamageReceived, "
        "which only run on hits that really landed.")

    assert "await" not in body, (
        f"{rel}::{hook} awaits: issuing a command from a preview applies "
        "effects for a hit that was never thrown.")

    assert not re.search(r"\bRng\.", body), (
        f"{rel}::{hook} draws from an Rng stream. The streams are shared and "
        "advanced in lockstep; a preview-driven draw on one peer poisons "
        "every later roll in the run.")

    bad = [c for c in _CMD_CALL.findall(body) if c not in READONLY_CMDS]
    assert not bad, (
        f"{rel}::{hook} calls {bad}, which is not in READONLY_CMDS. If it is "
        "genuinely a lookup, add it there deliberately; if it mutates, it "
        "belongs one hook over.")


def test_vigil_pays_its_fuel_through_the_reshuffle():
    """tier0 prevent_damage_exhaust reshuffles BEFORE declaring itself out.

    The C# gate counted draw + discard but the exhaust only ever read the
    draw pile and bailed when it was empty, so an empty draw over a stocked
    discard prevented the damage and never paid the card -- free prevention,
    and a second divergence from the sim on the same rare.
    """
    body = method_body(
        (SOURCE / "Powers" / "KuragePowers.cs").read_text(encoding="utf-8"),
        r"public\s+override\s+async\s+Task\s+AfterDamageReceived\s*\(")
    assert "CardPileCmd.ShuffleIfNecessary" in body, body
    # The latch lives here, with the reshuffle -- not in the modifier.
    assert "_usedThisTurn = true" in body, body
