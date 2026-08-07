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
# not guarantee it. All four filed races (EB-2, EB-19/races-a/b/c) are this
# shape, and each was found by hand.
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
        ("Powers/FurinaResources.cs", "FurinaResourceHooks"):
            "purges the Salon company map, clears Curtain Call per-turn "
            "windows; touches nothing its (Klee-side, co-op-only) "
            "co-tenants read",
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
            "SpotlightSystem.ResetTurn + pending-draw flush. RACE "
            "EB-19/races-b: clears the Standing Ovation spend-boost the "
            "Salon upkeep mints in this same broadcast",
        ("Powers/FurinaResources.cs", "EncorePerTurnPower"):
            "All the World's a Stage Encore mint. RACE EB-2: the Salon "
            "upkeep spends Encore in this same broadcast",
        ("Powers/KokomiResources.cs", "KokomiResourceHooks"):
            "Kokomi kit-grant check: adds a card when charged",
        ("Powers/KokomiResources.cs", "ChargePerTurnPower"):
            "per-turn Charge mint",
        ("Powers/KuragePowers.cs", "PreventExhaustWardPower"):
            "resets the Vigil once-per-turn latch; consumed only from "
            "damage hooks, never by a co-tenant",
        ("Powers/SalonPowers.cs", "SalonMemberPower"):
            "Salon upkeep: spends Encore, ticks stage damage, mints the "
            "spend-boost. RACE EB-2 + EB-19/races-b (the other half of "
            "both)",
        ("Powers/SparkKitPowers.cs", "SparkPerTurnPower"):
            "per-turn Spark mint",
        ("Powers/SpotlightSystem.cs", "SpotlightDiscountPower"):
            "resets its qualifying-plays latch; consumed only from card "
            "plays",
        ("Relics/EtherealSpotlightRelic.cs", "EtherealSpotlightRelic"):
            "grants the Ethereal Spotlight to the hand (random discard at "
            "hand-full). Shares the HAND with the pending-draw flush; that "
            "seam belongs to the deferred-settle machinery's SKIP-10.9 "
            "caveat (C#-only structure, parity rests on flush sites)",
        ("Relics/UpgradedStarterRelics.cs", "ExplosiveFrags"):
            "turn-1-only opening Spark windfall (the sim's combat_start "
            "site)",
    },
    "BeforeSideTurnEnd": {
        ("Powers/CompanionPowers.cs", "OzSummonPower"):
            "Electro volley. RACE EB-19/races-c: unordered vs the sim's "
            "fixed Pyro->Electro->Hydro (effects.py:2596-2658)",
        ("Powers/CompanionPowers.cs", "SolarIsotomaPower"):
            "duration tick-down of itself, player side",
        ("Powers/ElementalApplication.cs", "KleeElementalHooks"):
            "kit-grant check, turn-end site; its body documents the "
            "models-after-powers broadcast order it leans on",
        ("Powers/FontainePowers.cs", "MasqueRedDeathPower"):
            "Bond-of-Life payment. RACE EB-19/races-a: vs the Kurage "
            "pulse's Block grant (sim pays strictly first, "
            "effects.py:2588)",
        ("Powers/FurinaResources.cs", "FurinaResourceHooks"):
            "last-chance pending-draw flush, so an end-of-turn spend "
            "cannot strand into the next turn",
        ("Powers/KitBurst.cs", "SparksNSplashPower"):
            "Pyro volley. RACE EB-19/races-c",
        ("Powers/KokomiResources.cs", "KokomiResourceHooks"):
            "Kokomi kit-grant check, turn-end site",
        ("Powers/KuragePowers.cs", "KurageSummonPower"):
            "Hydro pulse: Block grant + volley. RACE EB-19/races-a + "
            "EB-19/races-c (a tenant of both)",
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
        ("Powers/KuragePowers.cs", "CeremonialGarmentPower"):
            "duration tick-down, player side",
        ("Powers/SpotlightSystem.cs", "SpotlightMultBonusTurnPower"):
            "self-expiry of a this-turn Spotlight bonus",
        ("Powers/SpotlightSystem.cs", "SpotlightFlatDamageTurnPower"):
            "self-expiry of a this-turn Spotlight bonus",
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
                found.add((hook, str(path.relative_to(SOURCE)), name))
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
