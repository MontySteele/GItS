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
        "courtroom-drama-vulnerable-is-multiplicative",
        "Powers/AuraPower.cs",
        "ModifyDamageMultiplicative",
        r"public\s+override\s+decimal\s+ModifyDamageMultiplicative\s*\(",
        ["CurtainCallHooks.CourtroomDramaWillAmplify",
         "ReactionConstants.VulnerableTakenMult"],
        ["CurtainCallHooks.CourtroomDramaWillAmplify"],
        "EB-19/M1, the Superconduct shape one power over. Courtroom Drama's "
        "Vulnerable is applied from CurtainCallHooks.NoteFirstReaction, which "
        "ReactionEffects.Resolve reaches from AfterDamageReceived -- one hook "
        "after the triggering hit's number is final. The sim applies it "
        "inside reactions._react (the `reactions_this_turn == 1` block) and "
        "runs modify_damage_taken afterwards, so tier0's triggering hit is "
        "itself x1.5. Same two-payout tell as Superconduct: the bomb path "
        "already amplified, because ElementalHit.Deal resolves the reaction "
        "before SimDamagePipeline.TargetMods reads Vulnerable.",
    ),
    (
        "boss-frozen-vulnerable-is-multiplicative",
        "Powers/AuraPower.cs",
        "ModifyDamageMultiplicative",
        r"public\s+override\s+decimal\s+ModifyDamageMultiplicative\s*\(",
        ["ReactionEffects.FrozenBossVulnWillApply",
         "ReactionConstants.VulnerableTakenMult"],
        ["ReactionEffects.FrozenBossVulnWillApply"],
        "EB-19/M1b, the same shape one reaction over. Under the NC-7 alpha "
        "substitution (R117) a Frozen reaction in a boss room on a non-minion "
        "applies Vulnerable instead of Frozen. The sim applies it INSIDE "
        "reactions._react (reactions.py:147-150, `boss_room and not "
        "enemy.is_minion`) and only then runs modify_damage_taken via "
        "effects.deal_damage_to_enemy, so tier0's triggering hit is itself "
        "x1.5; C# lands it from ReactionEffects.Resolve, reached from "
        "AfterDamageReceived, one hook after that number is final. "
        "UNCONDITIONAL, unlike Courtroom Drama -- the boss branch carries no "
        "first-reaction gate, so EVERY qualifying boss-room Frozen was short "
        "by a third of its own hit.",
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


# A real assignment, not `==`, `!=`, `<=`, `>=`, `+=` or a lambda arrow.
_ASSIGNMENT = re.compile(r"(?<![=!<>+\-*/%&|^])=(?![=>])")


def test_the_reaction_vulnerables_share_one_multiplier():
    """Two of these on one hit is x1.5, not x2.25.

    All three sim sites write the SAME `vulnerable` stack, and
    powers.modify_damage_taken is a flat multiply on any nonzero stack rather
    than one per source. Two separate `mult *=` statements in this hook would
    be correct on either source alone and wrong on the hit that is both --
    and both live combinations exist: Superconduct as the turn's first
    reaction with Courtroom Drama installed (Cryo aura + Electro attack), and
    a boss-room Frozen (Cryo attack into a Hydro aura, no MinionPower) that is
    also the turn's first reaction.
    """
    body = method_body(
        (SOURCE / "Powers" / "AuraPower.cs").read_text(encoding="utf-8"),
        r"public\s+override\s+decimal\s+ModifyDamageMultiplicative\s*\(")
    assert body.count("ReactionConstants.VulnerableTakenMult") == 1, body


def test_the_reaction_vulnerable_mirror_cannot_double_pay_the_bomb_path():
    """The bomb path amplifies for real; this hook must not amplify it again.

    ElementalHit.Deal applies the reaction's Vulnerable through
    ReactionEffects.Resolve and only then reads it back in
    SimDamagePipeline.TargetMods, so a bomb-triggered Superconduct or first
    reaction already gets its x1.5 from the target's real VulnerablePower. The
    hit is emitted Unpowered, and the IsPoweredAttack gate at the top of the
    modifier is what keeps the mirror off it. Drop either and the bomb pays
    twice -- the exact defect EB-19/M1 fixed, with the sign flipped.
    """
    aura = method_body(
        (SOURCE / "Powers" / "AuraPower.cs").read_text(encoding="utf-8"),
        r"public\s+override\s+decimal\s+ModifyDamageMultiplicative\s*\(")
    gate = aura.index("IsPoweredAttack()")
    assert gate < aura.index("ReactionConstants.VulnerableTakenMult"), aura

    hit = (SOURCE / "Powers" / "ElementalHit.cs").read_text(encoding="utf-8")
    deal = method_body(hit, r"public\s+static\s+async\s+Task\s+Deal\s*\(")
    assert "ValueProp.Unpowered" in deal, deal
    # ...and the order that makes the bomb path's amplification real.
    assert deal.index("ReactionEffects.Resolve") < deal.index(
        "SimDamagePipeline.TargetMods"), deal


def test_the_courtroom_drama_forecast_is_a_read():
    """The predicate the pure modifier calls must itself be pure.

    ModifyDamageMultiplicative runs in preview and tooltip paths, so a
    forecast that CONSUMED the once-per-turn window would spend Courtroom
    Drama on a hit that was never thrown. The single increment site stays in
    ReactionEffects.Resolve.
    """
    # Both forecasts are expression-bodied on purpose -- a `=>` member cannot
    # hold a statement, so "it only reads" is enforced by the shape as well as
    # by the text below. method_body() would run past a `=>` member's end, so
    # these are matched as expressions.
    curtain = (SOURCE / "Powers" / "CurtainCallPowers.cs").read_text(
        encoding="utf-8")
    forecast = re.search(
        r"public\s+static\s+bool\s+CourtroomDramaWillAmplify\s*\([^)]*\)\s*=>"
        r"(.*?);", curtain, re.S)
    assert forecast, "CourtroomDramaWillAmplify is no longer expression-bodied"
    for forbidden in ("Cmd.", "await"):
        assert forbidden not in forecast.group(1), (
            f"CourtroomDramaWillAmplify contains {forbidden!r}; it is called "
            "from a speculative damage-preview path and must only read.")
    assert not _ASSIGNMENT.search(forecast.group(1)), forecast.group(1)

    reactions = (SOURCE / "Powers" / "ReactionEffects.cs").read_text(
        encoding="utf-8")
    inner = re.search(
        r"public\s+static\s+bool\s+NextReactionIsFirstFor\s*\([^)]*\)\s*=>"
        r"(.*?);", reactions, re.S)
    assert inner, "NextReactionIsFirstFor is no longer expression-bodied"
    assert "DealerReactionsThisTurn" in inner.group(1)
    # One write site, still in Resolve.
    assert reactions.count("DealerReactionsThisTurn[dealer] =") == 1, reactions


def _frozen_boss_forecast() -> str:
    """The expression body of ReactionEffects.FrozenBossVulnWillApply."""
    reactions = (SOURCE / "Powers" / "ReactionEffects.cs").read_text(
        encoding="utf-8")
    match = re.search(
        r"public\s+static\s+bool\s+FrozenBossVulnWillApply\s*\([^)]*\)\s*=>"
        r"(.*?);", reactions, re.S)
    assert match, "FrozenBossVulnWillApply is no longer expression-bodied"
    return match.group(1)


def test_the_boss_frozen_forecast_is_a_read():
    """The predicate the pure modifier calls must itself be pure (EB-19/M1b).

    ModifyDamageMultiplicative runs in preview and tooltip paths, so a
    forecast that APPLIED the substitution -- or cached anything about it --
    would put Vulnerable on a boss for a hit that was never thrown. The
    PowerCmd.Apply stays in ReactionEffects.Resolve; this only reports.

    Expression-bodied on purpose: a `=>` member cannot hold a statement, so
    "it only reads" is enforced by the shape as well as by the text below.
    """
    body = _frozen_boss_forecast()
    for forbidden in ("Cmd.", "await"):
        assert forbidden not in body, (
            f"FrozenBossVulnWillApply contains {forbidden!r}; it is called "
            "from a speculative damage-preview path and must only read.")
    assert not _ASSIGNMENT.search(body), body


def test_the_boss_frozen_forecast_is_null_tolerant():
    """Preview enumeration can ask before there is a combat to answer from.

    The reads walk target -> CombatState -> Encounter -> RoomType, any link of
    which is absent outside a live boss encounter (and `target` itself is
    nullable on the hook's signature). A hard dereference here throws from a
    tooltip, so every hop is guarded and the answer outside combat is `false`
    -- which is also the correct answer: no boss room, no substitution.
    """
    body = _frozen_boss_forecast()
    assert re.search(r"target\s*!=\s*null", body), body
    assert "CombatState?." in body, body
    assert "Encounter?." in body, body


def test_the_boss_frozen_mirror_exempts_minions_and_non_boss_rooms():
    """The negative half of the sim predicate, which is where it earns its keep.

    `boss_room and not enemy.is_minion` (reactions.py:147-148): a minion in a
    boss room, or anything at all outside one, takes FrozenPower and no
    Vulnerable -- so the mirror must not amplify those hits either. Both
    clauses live in the forecast, and the substitution reads it rather than
    keeping a second copy that could drift from the one the pipeline asks.
    """
    body = _frozen_boss_forecast()
    assert "RoomType.Boss" in body, body
    assert re.search(r"!\s*target\.Powers\.OfType<MinionPower>", body), body

    reactions = (SOURCE / "Powers" / "ReactionEffects.cs").read_text(
        encoding="utf-8")
    # Exactly one copy of the predicate in the file: the forecast. A second
    # `RoomType.Boss` test would be a fork between what the preview forecasts
    # and what Resolve then does.
    assert reactions.count("RoomType.Boss") == 1, reactions
    assert reactions.count("FrozenBossVulnWillApply(target)") == 1, reactions

    # ...and the mirror only fires on the reaction that substitutes.
    aura = method_body(
        (SOURCE / "Powers" / "AuraPower.cs").read_text(encoding="utf-8"),
        r"public\s+override\s+decimal\s+ModifyDamageMultiplicative\s*\(")
    assert re.search(
        r"reaction\s*==\s*Reaction\.Frozen\s*\r?\n?\s*"
        r"&&\s*ReactionEffects\.FrozenBossVulnWillApply", aura), aura


def test_the_boss_frozen_mirror_cannot_double_pay_the_bomb_path():
    """Same sign-flipped defect as M1, one reaction over.

    A bomb-triggered boss-room Frozen already gets its x1.5 for real:
    ElementalHit.Deal routes through ReactionEffects.Resolve (which applies
    the substituted VulnerablePower) before SimDamagePipeline.TargetMods reads
    it back. That hit is Unpowered, so the IsPoweredAttack gate at the top of
    the modifier is what keeps this mirror off it.
    """
    aura = method_body(
        (SOURCE / "Powers" / "AuraPower.cs").read_text(encoding="utf-8"),
        r"public\s+override\s+decimal\s+ModifyDamageMultiplicative\s*\(")
    gate = aura.index("IsPoweredAttack()")
    assert gate < aura.index("ReactionEffects.FrozenBossVulnWillApply"), aura

    hit = (SOURCE / "Powers" / "ElementalHit.cs").read_text(encoding="utf-8")
    deal = method_body(hit, r"public\s+static\s+async\s+Task\s+Deal\s*\(")
    assert "ValueProp.Unpowered" in deal, deal
    assert deal.index("ReactionEffects.Resolve") < deal.index(
        "SimDamagePipeline.TargetMods"), deal


def test_the_boss_frozen_mirror_matches_the_sim_predicate_verbatim():
    """The receipt: the sim site the ledger row cites still says what it says.

    Source-text on the SIM side, unusually -- the row's claim is a
    correspondence between two files, and pinning only the C# half lets the
    sim move out from under it. Two things must hold: the predicate is
    `boss_room and not enemy.is_minion`, and it is UNCONDITIONAL (no
    first-reaction gate like Courtroom Drama's), which is why the C# mirror
    has no NextReactionIsFirstFor in its Frozen clause.
    """
    sim = (ROOT / "tier0" / "engine" / "reactions.py").read_text(
        encoding="utf-8")
    react = sim[sim.index("def _react("):sim.index("def _splash(")]
    frozen = react[react.index('name = "frozen"'):]
    apply_line = frozen.index("C.FROZEN_BOSS_VULN")
    guard = frozen.index("if boss_room and not enemy.is_minion:")
    assert guard < apply_line, frozen
    # No gate between the guard and the write.
    between = frozen[guard:apply_line]
    assert "reactions_this_turn" not in between, between

    # And the sim really does apply it before the vulnerable multiply: the
    # whole reason the C# hook is one phase too late.
    effects = (ROOT / "tier0" / "engine" / "effects.py").read_text(
        encoding="utf-8")
    pipeline = method_body_py(effects, "def deal_damage_to_enemy(")
    assert pipeline.index("reactions.resolve_hit") < pipeline.index(
        "powers.modify_damage_taken"), pipeline


def method_body_py(source: str, signature: str) -> str:
    """Crude python-function slice: from the def to the next top-level def."""
    start = source.index(signature)
    nxt = source.find("\ndef ", start + 1)
    return source[start:nxt if nxt != -1 else len(source)]


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
        # Build output can hold copies of these files, and this sweep is
        # parametrized at COLLECTION time -- so without this filter the test
        # count is a function of the build state, not the source. That
        # phantom has now shown up twice as "+9 tests" in sprint gate counts
        # (1305-vs-1296, 1359-vs-1350) and made suite totals unusable as
        # evidence between machines. Same idiom as test_canonical_model_misuse.
        if any(part in ("bin", "obj") for part in path.parts):
            continue
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


# --- broadcast co-tenancy, swept repo-wide (EB-19/L) ------------------------
#
# PHASE_LEDGER pins WHICH hook a decision rides. This ledger pins the other
# axis the EB-2 / EB-19/races-* class lives on: WHO ELSE rides the same
# turn-lifecycle broadcast. The engine guarantees allies-before-enemies across
# listener iteration (R35, DetonationSplashPower's ordering proof) but gives
# SAME-SIDE co-tenants of one broadcast no relative order, while the sim's
# turn structure is strictly sequential -- so two same-side tenants that touch
# one resource are a nondeterministic divergence FIXED-SEED PARITY CANNOT
# CATCH: the C# can match the sim's order on every replayed seed and still
# not guarantee it. Four races of this shape were filed and each was found by
# hand; all four were closed on 2026-08-07 and their tenants have moved, which
# is why no row below cites one any more.
#
# TWO FIX IDIOMS, and the second is new. Where the racing tenants can be
# separated by BROADCAST, they are: the Ancient income powers moved to
# BeforeSideTurnStart (strictly earlier than the Salon upkeep that spends what
# they mint), and the Standing Ovation spend-boost's clear moved to
# AfterSideTurnEnd (the sim's own expiry site). Where they cannot -- turn end
# offers only two broadcasts and the four end-of-turn tenants needed four
# positions -- one listener now DRIVES them in the sim's order instead:
# TurnEndSequencer. A sequencer is the heavier idiom and should stay the
# exception; prefer staging while staging can express the order.
#
# The structural catch is registration: the sweep below finds every override
# of a turn broadcast, and each must hold a row here. A new tenant landing in
# an occupied broadcast fails the test and forces the question "does the sim
# order you against your co-tenants?" before the code ships. Same curation
# rule as PHASE_LEDGER: a row is an examined tenant, not "where the code is
# today" -- adding one means the question above was answered; a row whose
# annotation names a filed race retires WITH that race's BACKLOG row when the
# fix idiom (stage into a strictly earlier/later broadcast) moves the tenant
# out, because moving it breaks the sweep match.
#
# Annotations state what the tenant does in the broadcast and cite the filed
# race where one is filed. They are roles and receipts, not a pairwise
# commutativity proof -- the registration is the guarantee.

TURN_BROADCASTS = (
    "BeforeSideTurnStart", "AfterSideTurnStart", "AfterPlayerTurnStart",
    "BeforeSideTurnEnd", "AfterSideTurnEnd",
)

# --- resolved turn-start broadcast order (EB-19/M7) -------------------------
#
# The fix idiom the co-tenancy ledger prescribes -- "stage into a strictly
# earlier/later broadcast" -- is only as good as the repo's belief about which
# broadcast IS earlier. Two in-repo docs asserted incompatible orders:
# refpowers.py's site table put AfterPlayerTurnStart and AfterSideTurnStart
# AFTER the hand draw, in that order; AuraPower.cs's phase-correction comment
# claimed AfterSideTurnStart ran "strictly before energy reset and the hand
# draw". Settled by decompile, not by argument (StS2 v0.107.1, commit
# 59260271, ilspycmd 8.2.0.7535). refpowers.py was right; the AuraPower.cs
# clause was corrected in place and now cites this tuple.
#
# CombatManager.StartTurn, decompiled:
#   :454  Creature.BeforeTurnStart          (snapshots power amounts)
#   :459  await Hook.BeforeSideTurnStart
#   :497  await Creature.AfterTurnStart     -> ClearBlock (Creature.cs:696,
#                                             Hook.ShouldClearBlock :725)
#   :505  await Hook.AfterBlockCleared
#   :516  await SetupPlayerTurn(player, ctx), whose body is
#           :642  Hook.ShouldPlayerResetEnergy / ResetEnergy
#           :651  await Hook.AfterEnergyReset
#           :653  await Hook.BeforeHandDraw
#           :655  Hook.ModifyHandDraw  (+ :656 AfterModifyingHandDraw)
#           :674  await CardPileCmd.Draw(..., fromHandDraw: true)
#           :676  await Hook.AfterPlayerTurnStart
#   :523  await Hook.AfterSideTurnStart
#
# So AfterSideTurnStart is the LAST turn-start broadcast, not the first, and
# AfterPlayerTurnStart is strictly earlier than it -- the opposite of the
# reading a "side-wide before per-player" intuition gives. Anything staged
# out of AfterPlayerTurnStart to land LATER goes to AfterSideTurnStart;
# anything staged EARLIER goes to BeforeSideTurnStart, which is the only
# broadcast that precedes the block clear.
#
# ONE CAVEAT, and it is load-bearing for the fix idiom. :516 awaits
# SetupPlayerTurn through WaitForPauseOrCompletionWithoutAssigningTask
# (HookPlayerChoiceContext.cs:129), which returns on the task completing OR on
# the setup pausing for a player choice. A turn-start hook that opens a choice
# therefore lets :523 AfterSideTurnStart run while that player's
# AfterPlayerTurnStart is still pending -- the setup task is only rejoined at
# :569. The order below is the no-choice order: it holds for every tenant in
# CO_TENANCY_LEDGER (none of them prompt), and a future tenant that DOES
# prompt during turn-start setup breaks it and must not be used as a staging
# target.
TURN_START_BROADCAST_ORDER = (
    "BeforeSideTurnStart",
    "block clear",
    "AfterBlockCleared",
    "energy reset",
    "hand draw",
    "AfterPlayerTurnStart",
    "AfterSideTurnStart",
)


def test_the_resolved_order_covers_every_registered_turn_start_broadcast():
    """A staging target absent from the resolved order is an unsettled one."""
    start_broadcasts = [
        h for h in TURN_BROADCASTS
        if h in ("BeforeSideTurnStart", "AfterSideTurnStart",
                 "AfterPlayerTurnStart")]
    for hook in start_broadcasts:
        assert hook in TURN_START_BROADCAST_ORDER, hook
    assert (TURN_START_BROADCAST_ORDER.index("AfterPlayerTurnStart")
            < TURN_START_BROADCAST_ORDER.index("AfterSideTurnStart"))


def test_no_doc_reasserts_the_refuted_pre_draw_order():
    """The losing assertion, pinned so it cannot come back by paraphrase.

    AuraPower.cs claimed AfterSideTurnStart ran before the draw for a year.
    The correction only sticks if re-adding it fails a test.
    """
    aura = (SOURCE / "Powers" / "AuraPower.cs").read_text(encoding="utf-8")
    assert not re.search(r"strictly before\s+(?:\S+\s+){0,4}energy reset",
                         aura), (
        "AuraPower.cs re-asserts an AfterSideTurnStart-before-energy/draw "
        "order. The decompile (CombatManager.cs:516 vs :523) says the "
        "per-player setup -- energy reset, hand draw, AfterPlayerTurnStart "
        "-- is awaited FIRST. See TURN_START_BROADCAST_ORDER.")
    refpowers = (ROOT / "tier0" / "engine" / "refpowers.py")\
        .read_text(encoding="utf-8")
    assert "E/F are AFTER the draw" in refpowers, (
        "refpowers.py's site table is the doc that won EB-19/M7; its "
        "post-draw claim is the ground truth this file records.")

CO_TENANCY_LEDGER = {
    "BeforeSideTurnStart": {
        ("Powers/BombPower.cs", "BombPower"):
            "turn-start detonation of last turn's bombs (enemy-attached; "
            "sim: combat.py detonate_bombs)",
        ("Powers/DemolitionPowers.cs", "DetonationSplashPower"):
            "zeroes the Blazing Delight splash-proc cap. Ordered before any "
            "enemy BombPower detonation by allies-before-enemies iteration "
            "(R35 -- the ordering proof in the class comment), matching the "
            "sim's reset-then-detonate (combat.py:501 vs :511)",
        ("Powers/DemolitionPowers.cs", "ExplosivesWorkshopPower"):
            "clears its own once-per-turn latch (EB-118 sec.4.4). THE "
            "ORDERING QUESTION, answered rather than assumed: it shares "
            "`BombDamageUpPower` with BombPower's turn-start detonation, "
            "which is a co-tenant of this same broadcast -- but it only "
            "RESETS a private bool here and writes the shared stat from the "
            "discard/exhaust hooks, which fire inside the player's turn, "
            "strictly after every tenant of this broadcast has run. So no "
            "co-tenant can observe a different bomb-damage number depending "
            "on order. The sim orders it the same way and for the same "
            "reason: `discards_this_turn` / `cards_exhausted_this_turn` are "
            "zeroed at the player turn start and only card play moves them",
        ("Powers/FurinaResources.cs", "FurinaResourceHooks"):
            "purges the Salon company map, clears Curtain Call per-turn "
            "windows; touches nothing its co-tenants read",
        ("Relics/EtherealSpotlightRelic.cs", "EtherealSpotlightRelic"):
            "grants the Ethereal Spotlight selector PRE-draw (R123 moved it "
            "here from AfterPlayerTurnStart; random discard only on a full "
            "retained hand -- the X14(b) softlock safety). No co-tenant "
            "touches the hand",
        ("Powers/FurinaResources.cs", "EncorePerTurnPower"):
            "All the World's a Stage Encore mint. STAGED HERE from "
            "AfterPlayerTurnStart to settle the Salon-income race: the upkeep "
            "SPENDS Encore from AfterPlayerTurnStart, and the sim sources the "
            "income above it (effects.player_turn_start_triggers, pinned by "
            "tier0/tests/test_eb30m_ancients.py::"
            "test_ancient_income_is_sourced_above_the_salon_upkeep plus the "
            "behavioural half test_the_stage_funds_the_same_turn_s_salon_"
            "ticks). Pre-draw and pre-block-clear are inert for it: GainEncore "
            "prints no Fanfare, grants no Block and reads no hand, so it "
            "shares nothing with the decay/delta-block settle that also lives "
            "in this broadcast",
        ("Powers/KokomiResources.cs", "ChargePerTurnPower"):
            "Princess of Watatsumi Charge mint. Staged here for the same "
            "reason and by the same pin: the sim reads charge_per_turn above "
            "the upkeep and above the whole per-turn income group, and every "
            "consumer of the meter (KokomiResourceHooks' kit-grant check) is "
            "an AfterPlayerTurnStart tenant. Moves a meter only",
    },
    "AfterSideTurnStart": {
        ("Diagnostics/PlayTelemetry.cs", "PlayTelemetryHooks"):
            "diagnostics observer; reads, never writes board state",
        ("Powers/AuraPower.cs", "AuraPower"):
            "aura duration tick (PHASE_LEDGER "
            "aura-ticks-after-side-turn-start); only the observer shares "
            "the broadcast",
    },
    "AfterPlayerTurnStart": {
        ("Powers/CompanionPowers.cs", "CelestialGiftPower"):
            "per-turn Strength + Block mint; its body notes the sim's "
            "Strength-then-Block order is bookkeeping, not a dependency",
        ("Powers/CompanionPowers.cs", "MetallicizePower"):
            "raw per-turn Block mint (R116)",
        ("Powers/DemolitionPowers.cs", "BombAndSparkPerTurnPower"):
            "per-turn bomb + Spark mint",
        ("Powers/ElementalApplication.cs", "KleeElementalHooks"):
            "Klee kit-grant check: adds a card to the hand when the meter "
            "is charged",
        ("Powers/FontainePowers.cs", "MasqueRedDeathPower"):
            "per-turn Strength mint",
        ("Powers/FurinaResources.cs", "FurinaResourceHooks"):
            "SpotlightSystem.ResetTurn (the MOVED and PLAYS windows only -- "
            "the sim zeroes those at the top of the player turn) + "
            "pending-draw flush + fanfare-delta settle. The spend-boost clear "
            "that used to sit in ResetTurn has moved to this class's "
            "AfterSideTurnEnd override, so nothing here reads or writes a "
            "resource the Salon upkeep touches",
        ("Powers/KokomiResources.cs", "KokomiResourceHooks"):
            "Kokomi kit-grant check: adds a card when charged. Its input, the "
            "Charge meter, is minted a broadcast earlier (see "
            "ChargePerTurnPower under BeforeSideTurnStart), so the grant "
            "cannot see a half-paid bank",
        ("Powers/KuragePowers.cs", "PreventExhaustWardPower"):
            "resets the Vigil once-per-turn latch; consumed only from "
            "damage hooks, never by a co-tenant",
        ("Powers/SalonPowers.cs", "SalonMemberPower"):
            "Salon upkeep: spends Encore, ticks stage damage, mints the "
            "Standing Ovation spend-boost. Both resources it touches are now "
            "ordered against it by BROADCAST rather than by luck -- the "
            "Encore income is minted in BeforeSideTurnStart and the "
            "spend-boost is cleared in AfterSideTurnEnd, so the upkeep is the "
            "only tenant of THIS broadcast that reads either",
        ("Powers/SparkKitPowers.cs", "SparkPerTurnPower"):
            "per-turn Spark mint",
        ("Powers/SpotlightSystem.cs", "SpotlightDiscountPower"):
            "resets its qualifying-plays latch; consumed only from card "
            "plays",
        ("Relics/UpgradedStarterRelics.cs", "ExplosiveFrags"):
            "turn-1-only opening Spark windfall (the sim's combat_start "
            "site)",
        ("Powers/TurnEndSequencer.cs", "TurnEndSequencer"):
            "EB-53/N1: redraws the end-of-turn attribution docket, nothing "
            "else. It has NO stake in this broadcast's order because it "
            "writes no game state at all -- it reads the same accessors the "
            "resolution reads (KurageSummonPower.PulseDamage and the volley "
            "constants) and pushes text into Godot nodes. Whatever order it "
            "lands in relative to the mints above, the numbers it draws are "
            "re-read on the next redraw; the sim has no counterpart because "
            "there is nothing here to model",
    },
    "BeforeSideTurnEnd": {
        ("Powers/CompanionPowers.cs", "SolarIsotomaPower"):
            "duration tick-down of itself, player side",
        ("Powers/ElementalApplication.cs", "KleeElementalHooks"):
            "kit-grant check, turn-end site; its body documents the "
            "models-after-powers broadcast order it leans on",
        ("Powers/FurinaResources.cs", "FurinaResourceHooks"):
            "last-chance pending-draw flush, so an end-of-turn spend "
            "cannot strand into the next turn",
        ("Powers/KokomiResources.cs", "KokomiResourceHooks"):
            "Kokomi kit-grant check, turn-end site",
        ("Powers/TurnEndSequencer.cs", "TurnEndSequencer"):
            "THE ONLY ORDERED TENANT, and the reason four powers no longer "
            "override this broadcast at all. It drives, per player-side "
            "creature and in this order: MasqueRedDeathPower.PayBondOfLife, "
            "SparksNSplashPower.FireVolley (Pyro), OzSummonPower.FireVolley "
            "(Electro), KurageSummonPower.FirePulse (Hydro + Block) -- the "
            "top-to-bottom reading of tier0 effects.player_turn_end_triggers. "
            "Two things depended on that order and neither could be expressed "
            "by staging, because turn end has only two broadcasts and "
            "AfterSideTurnEnd is already spoken for (WitchsFlamePower eats "
            "what the volleys applied): the Bond consumes the turn's first 5 "
            "Block while the Hydro pulse GRANTS Block, and the three volleys "
            "both pick which reactions fire and draw in sequence from the "
            "shared Rng.CombatTargets stream. The four steps are now the "
            "Resolve delegates of TurnEndAttribution.Order and this tenant "
            "WALKS that table (EB-53/N1) -- the order is written down once so "
            "the end-of-turn attribution docket cannot name the four in an "
            "order they are not fired in. See "
            "test_the_turn_end_sequence_is_the_sims_order and "
            "test_the_sequencer_walks_the_table",
    },
    "AfterSideTurnEnd": {
        ("Diagnostics/PlayTelemetry.cs", "PlayTelemetryHooks"):
            "diagnostics observer; reads, never writes board state",
        ("Powers/CompanionPowers.cs", "CompanionCostThisTurnPower"):
            "self-expiry of the per-turn cost-discount accumulator (R114 "
            "boundary)",
        ("Powers/CompanionPowers.cs", "ReplayNextCompanionPower"):
            "self-expiry at the end of the turn that wrote it (R110)",
        ("Powers/CompanionPowers.cs", "WitchsFlamePower"):
            "consumes Pyro auras for damage + Burst, player side; runs "
            "after the BeforeSideTurnEnd volleys by broadcast order, so it "
            "eats what they applied",
        ("Powers/CompanionPowers.cs", "AttackUpThisTurnPower"):
            "self-expiry of a this-turn attack buff",
        ("Powers/ElementalApplication.cs", "KleeElementalHooks"):
            "MarkTurnStart on the enemy side: opens the next reaction "
            "window",
        ("Powers/FrozenPower.cs", "FrozenPower"):
            "duration tick-down, enemy side",
        ("Powers/FurinaResources.cs", "FurinaResourceHooks"):
            "closes the this-turn Spotlight windows: clears the Standing "
            "Ovation spend-boost resource. AfterSideTurnEnd is StS2 site M, "
            "which is where the sim's powers.on_turn_end pops powers.EXPIRING "
            "(tier0/engine/powers.py:23, :156) -- and "
            "SpotlightSpendBoostResource is the C# twin of "
            "spotlight_mult_bonus_turn, one of that tuple's two members. It "
            "used to be cleared from the turn-START broadcast whose Salon "
            "upkeep mints it, which is the race this move closes. Its two "
            "POWER-shaped siblings below expire in the same broadcast; no "
            "co-tenant reads the Spotlight multiplier, which only modifies "
            "printed values on CARD plays",
        ("Powers/KuragePowers.cs", "CeremonialGarmentPower"):
            "duration tick-down, player side",
        ("Powers/SpotlightSystem.cs", "SpotlightMultBonusTurnPower"):
            "self-expiry of a this-turn Spotlight bonus",
        ("Powers/SpotlightSystem.cs", "SpotlightFlatDamageTurnPower"):
            "self-expiry of a this-turn Spotlight bonus",
        ("Powers/TurnEndSequencer.cs", "TurnEndSequencer"):
            "EB-53/N1: redraws the attribution docket after the volleys have "
            "fired and ticked down, so the numbers the player looks at next "
            "are the new ones. Pure draw, writes no game state, reads only "
            "accessors the resolution already called -- so it shares nothing "
            "with WitchsFlamePower's aura consumption or the this-turn "
            "expiries in this broadcast, and has no position to defend in "
            "their order",
    },
}

_CLASS_DECL = re.compile(r"\bclass\s+(\w+)")


def _class_spans(source: str) -> list[tuple[str, int, int]]:
    """(name, body_start, body_end) for every class declaration."""
    spans = []
    for match in _CLASS_DECL.finditer(source):
        try:
            start = source.index("{", match.end())
        except ValueError:
            continue
        depth = 0
        for i in range(start, len(source)):
            if source[i] == "{":
                depth += 1
            elif source[i] == "}":
                depth -= 1
                if depth == 0:
                    spans.append((match.group(1), start, i))
                    break
    return spans


def _broadcast_tenants() -> set[tuple[str, str, str]]:
    """(hook, file, class) for every turn-broadcast override in the mod."""
    found = set()
    for path in sorted(SOURCE.rglob("*.cs")):
        if any(part in ("bin", "obj") for part in path.parts):
            continue
        source = path.read_text(encoding="utf-8")
        spans = _class_spans(source)
        for hook in TURN_BROADCASTS:
            pattern = rf"public\s+override\s+\S+(?:\s+\S+)?\s+{hook}\s*\("
            for match in re.finditer(pattern, source):
                covering = [s for s in spans if s[1] <= match.start() <= s[2]]
                assert covering, (
                    f"{path}: {hook} override outside any class body")
                name = min(covering, key=lambda s: s[2] - s[1])[0]
                # as_posix, not str: the ledger keys are written with forward
                # slashes, and on Windows str() yields backslashes -- which
                # made every registered tenant read as unregistered AND every
                # ledger row read as stale, i.e. the whole sweep was red on
                # one platform and told you nothing on it.
                found.add((hook, path.relative_to(SOURCE).as_posix(), name))
    return found


def test_the_sweep_actually_sees_the_broadcast_tenants():
    """A zero-row sweep is a green test that checks nothing."""
    rows = _broadcast_tenants()
    assert len(rows) >= 30, f"only found {len(rows)} broadcast tenants"


@pytest.mark.parametrize("hook", TURN_BROADCASTS)
def test_broadcast_co_tenancy_is_registered(hook):
    found = {(f, c) for h, f, c in _broadcast_tenants() if h == hook}
    ledger = set(CO_TENANCY_LEDGER[hook])
    unregistered = found - ledger
    assert not unregistered, (
        f"unregistered tenant(s) of {hook}: {sorted(unregistered)}.\n"
        "Same-side co-tenants of one broadcast have no guaranteed relative "
        "order, and the sim's turn structure is strictly sequential -- the "
        "EB-2 / EB-19/races-* class, which fixed-seed parity cannot catch. "
        "Before registering: does the sim order this tenant against any "
        "co-tenant it shares a resource with? If yes, stage it into a "
        "strictly earlier/later broadcast (the in-repo fix idiom) or file "
        "the race in BACKLOG; then add the row with that answer as its "
        "annotation.")
    stale = ledger - found
    assert not stale, (
        f"ledger row(s) for {hook} match no override: {sorted(stale)}.\n"
        "The tenant moved or died. If it staged out of the broadcast to fix "
        "a filed race, retire that BACKLOG row in the same commit.")


def test_filed_race_citations_in_the_ledger_are_live():
    """A ledger row citing a race that BACKLOG no longer files is stale --
    either the race was fixed (then the tenant should have moved and the
    sweep test above should be failing too) or the row id is wrong."""
    backlog = (ROOT / "docs" / "current" / "BACKLOG.md")\
        .read_text(encoding="utf-8")
    for rows in CO_TENANCY_LEDGER.values():
        for key, note in rows.items():
            for row_id in re.findall(r"EB-19/races-[a-z]|EB-2(?![0-9])",
                                     note):
                assert f"`{row_id}`" in backlog, (
                    f"{key} cites {row_id}, which BACKLOG.md no longer "
                    "files")


# --- the turn-end sequence, pinned ------------------------------------------

# (call the sequencer makes, the sim line that puts it here)
TURN_END_SEQUENCE = (
    ("PayBondOfLife",
     "effects.player_turn_end_triggers pays masque_red_death's Bond FIRST, "
     "at the top of the function, so it eats the Block the turn produced "
     "rather than the Kurage pulse's mending"),
    ("SparksNSplashPower",
     "sparks_n_splash, the Pyro volley, is the first of the three"),
    ("OzSummonPower",
     "oz_summon, the Electro volley, is the second"),
    ("KurageSummonPower",
     "kurage_summon, the Hydro pulse, is the last -- and its Block grant is "
     "therefore strictly after the Bond payment"),
)


def _sequencer_body() -> str:
    return method_body(
        (SOURCE / "Powers" / "TurnEndSequencer.cs").read_text(encoding="utf-8"),
        r"public\s+override\s+async\s+Task\s+BeforeSideTurnEnd\s*\(")


def _order_table() -> str:
    """The ordered table itself (EB-53/N1).

    The four calls used to sit in the sequencer's own body, and this gate read
    that body. They moved into `TurnEndAttribution.Order` when the end-of-turn
    attribution docket landed, because the display has to NAME the four in
    firing order and a display built from a second hand-written list would be
    able to disagree with the resolution. Reading the table is reading the
    single source both halves now use, so the gate got STRONGER rather than
    looser: it now pins the order the player is shown as well as the order
    that fires. test_the_sequencer_walks_the_table below is the other half.
    """
    text = (SOURCE / "Powers" / "TurnEndAttribution.cs").read_text(
        encoding="utf-8")
    start = text.index("Order = new TurnEndSource[]")
    end = text.index("public static IReadOnlyList<TurnEndSource> Standing")
    return text[start:end]


def test_the_turn_end_sequence_is_the_sims_order():
    """Bond -> Pyro -> Electro -> Hydro, top to bottom.

    This is the whole content of the fix: the four used to be independent
    BeforeSideTurnEnd overrides with no relative order, and a fixed-seed
    parity run passes either way because the C# happens to iterate listeners
    in SOME order on any given replay. Only the source can say the order is
    guaranteed.
    """
    body = _order_table()
    positions = []
    for token, why in TURN_END_SEQUENCE:
        assert token in body, (
            f"TurnEndAttribution.Order no longer fires {token}: {why}")
        positions.append(body.index(token))
    assert positions == sorted(positions), (
        "TurnEndAttribution.Order reordered. The sim's order is "
        + " -> ".join(t for t, _ in TURN_END_SEQUENCE)
        + " (tier0/engine/effects.py player_turn_end_triggers, read top to "
        "bottom).")


def test_the_sequencer_walks_the_table():
    """The order table is only law if the sequencer actually reads it.

    Without this, a future edit could leave TurnEndAttribution.Order correct
    (and the gate above green) while the sequencer went back to four
    hand-written statements -- which is exactly the arrangement that let the
    display and the resolution drift apart in the first place.
    """
    body = _sequencer_body()
    assert "TurnEndAttribution.Order" in body, (
        "TurnEndSequencer stopped walking TurnEndAttribution.Order. The order "
        "is defined there ONCE so the attribution docket and the resolution "
        "cannot disagree; a hand-written sequence here re-opens that gap.")
    assert "source.Resolve" in body, (
        "TurnEndSequencer iterates the table but no longer resolves through "
        "it. Each entry's Resolve delegate IS the step it fires.")


@pytest.mark.parametrize("rel,cls", [
    ("Powers/FontainePowers.cs", "MasqueRedDeathPower"),
    ("Powers/KitBurst.cs", "SparksNSplashPower"),
    ("Powers/CompanionPowers.cs", "OzSummonPower"),
    ("Powers/KuragePowers.cs", "KurageSummonPower"),
])
def test_the_sequenced_powers_do_not_take_the_broadcast_back(rel, cls):
    """The revert this guards: re-adding `override BeforeSideTurnEnd`.

    A power that overrides the broadcast AND is driven by the sequencer fires
    twice, in an order that is once again undefined. The co-tenancy sweep
    would also fail (unregistered tenant) -- this names the class so the
    failure reads as the reverted decision rather than as a bookkeeping miss.
    """
    assert (rel, cls) not in CO_TENANCY_LEDGER["BeforeSideTurnEnd"]
    source = (SOURCE / rel).read_text(encoding="utf-8")
    spans = _class_spans(source)
    mine = [s for s in spans if s[0] == cls]
    assert mine, f"{cls} not found in {rel}"
    start, end = mine[0][1], mine[0][2]
    hit = re.search(
        r"public\s+override\s+\S+(?:\s+\S+)?\s+BeforeSideTurnEnd\s*\(",
        source[start:end])
    assert not hit, (
        f"{cls} overrides BeforeSideTurnEnd again. TurnEndSequencer already "
        "drives it; both would fire, unordered.")


# --- the card-play broadcasts (EB-19/M5, EB-19/M8) --------------------------
#
# The turn-lifecycle ledgers above pin WHICH broadcast a decision rides and WHO
# ELSE rides it. Card play has a third failure mode, and both rows below are
# instances of it: the sim's play_card is a single straight-line function, and
# the mod splits it across BeforeCardPlayed / OnPlay / AfterCardPlayed. Where
# the split falls decides what a line can SEE.
#
# ENUMERATION POINT, settled by decompile (StS2 v0.107.1, commit 59260271,
# ilspycmd 8.2.0.7535), because M5 turns on it. CardModel's play loop is:
#
#     await Hook.BeforeCardPlayed(combatState, cardPlay)
#     await OnPlay(choiceContext, cardPlay)          // the card resolves here
#     await Hook.AfterCardPlayed(combatState, choiceContext, cardPlay)
#
# per index in the playCount loop, with a fresh CardPlay object each index.
# Both Hook methods `foreach` over CombatState.IterateHookListeners(), an
# ITERATOR whose List<AbstractModel> (creature Powers, relics, potions, every
# pile's cards, modifiers, badges) is built inside its FIRST MoveNext -- i.e.
# when the foreach starts, not when the play started. Hook.BeforeCardPlayed
# goes through IterateCombatHookListeners, which is the same enumeration behind
# a combat-is-over guard.
#
# So: a power ADDED during OnPlay is absent from the BeforeCardPlayed listener
# list and PRESENT in the AfterCardPlayed one. That asymmetry is the whole of
# M5 -- it is why Navia's own play paid itself in C# and does not in the sim --
# and it is also the fix, used as a presence snapshot.

def test_navias_own_play_does_not_pay_itself():
    """EB-19/M5. The sim states the rule; the C# had to be taught it.

    combat.play_card reads `cannon_fire_support` beside the companions_played
    record site, BEFORE resolve_card, and says so in-line: "Sitting before
    resolve_card also means Navia's own play does not pay itself: the power is
    not up yet." The C# equivalent is not a power read but a listener
    enumeration, and AfterCardPlayed enumerates after OnPlay installed the
    power -- so she paid. BeforeCardPlayed is the only broadcast that
    enumerates early enough to answer "was this power already up", and it
    cannot award Block (no PlayerChoiceContext), which is why the pay still
    settles at AfterCardPlayed off a snapshot.
    """
    source = (SOURCE / "Powers" / "FontainePowers.cs").read_text(
        encoding="utf-8")
    spans = _class_spans(source)
    mine = [s for s in spans if s[0] == "CannonFireSupportPower"]
    assert mine, "CannonFireSupportPower not found"
    start, end = mine[0][1], mine[0][2]
    body = source[start:end]

    assert re.search(
        r"public\s+override\s+Task\s+BeforeCardPlayed\s*\(", body), (
        "CannonFireSupportPower no longer snapshots at BeforeCardPlayed, the "
        "only card-play broadcast that enumerates before OnPlay installs a "
        "power. Without it her own play pays itself again.")

    after = method_body(
        body, r"public\s+override\s+async\s+Task\s+AfterCardPlayed\s*\(")
    # The pay is gated on the snapshot, and the snapshot check comes first.
    assert "_presentAtPlayStart.Remove(cardPlay)" in after, after
    assert after.index("_presentAtPlayStart") < after.index(
        "CreatureCmd.GainBlock"), after

    sim = (ROOT / "tier0" / "engine" / "combat.py").read_text(encoding="utf-8")
    assert "Navia's own play does not pay itself" in sim, (
        "combat.py no longer states the rule this mirrors; if the sim moved, "
        "this decision needs re-deriving, not re-pinning.")


def test_the_navia_snapshot_survives_nested_plays():
    """A field would be clobbered by a card that plays a card.

    Order for a nested play is Before(A), OnPlay(A) -> Before(B), OnPlay(B),
    After(B), After(A). A single `_lastSeen` field holds B by the time After(A)
    runs, so A silently stops paying. CardPlay is a class with reference
    identity and one fresh instance per play index, so a set keyed on it is
    exact.
    """
    source = (SOURCE / "Powers" / "FontainePowers.cs").read_text(
        encoding="utf-8")
    assert "HashSet<CardPlay>" in source, source


def test_furina_spends_the_encore_cost_before_draining_burst():
    """EB-19/M8. The sim's play_card order, which the comment used to invert.

    tier0 spends the "Spend N Encore:" cost line at the top of play_card,
    right after the energy debit, and empties Burst for a requires-full card
    near the bottom -- cost, THEN drain, THEN the skill-tag bonus. The mod ran
    drain -> skill-tag -> cost under a comment claiming that was the sim's
    order. Latent (no sheet card carries encore_cost on a requires-full Burst
    card) and fixed anyway, because the thing that makes it reachable is a
    SHEET edit, which is not where anyone checks a C# hook's statement order.
    """
    body = method_body(
        (SOURCE / "Powers" / "FurinaResources.cs").read_text(encoding="utf-8"),
        r"public\s+override\s+Task\s+BeforeCardPlayed\s*\(")
    spend = body.index("FurinaResources.SpendEncore")
    # The owner-guarded drain, not the ownerless early-return one.
    drain = body.index("FurinaBurstResource.DrainOnPlay(card)")
    skill_tag = body.index("BurstPerSkillTag")
    assert spend < drain < skill_tag, (
        "FurinaResourceHooks.BeforeCardPlayed no longer runs cost -> drain -> "
        "skill-tag. tier0 combat.play_card does, in that order.")


def test_no_comment_reasserts_the_refuted_drain_first_order():
    """The losing claim, pinned so it cannot come back by paraphrase."""
    source = (SOURCE / "Powers" / "FurinaResources.cs").read_text(
        encoding="utf-8")
    assert "the requires-full drain first" not in source, (
        "FurinaResources.cs re-asserts a drain-before-Encore-cost sim order. "
        "combat.play_card spends the cost line first; see "
        "test_furina_spends_the_encore_cost_before_draining_burst.")


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
