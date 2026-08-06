"""Errata Batch 2: the sim/C# parity vectors for the NON-CARD rulings.

The sibling of `test_furina_fanfare_parity.py`, built the same way and for the
same reason: there is no C# test project -- the mod DLL only executes inside
the game -- so "run both implementations and diff" is not available. What IS
available is to make the two implementations answer the same question sheet.

  1. This module derives the answers from the SIM, which R116 made the design
     of record for every ruling below, and writes them to
     `docs/noncard-parity-vectors.json`.
  2. `klee-mod/KleeCode/Diagnostics/NonCardParityVectors.cs` carries the same
     tables as C# literals, and `KleeSelfCheck` runs the C# arithmetic against
     them at boot.
  3. `test_csharp_vectors_match_the_sim` (below) parses that C# file and
     asserts its tables are the sim's.

So the Python suite guarantees the two TABLES agree and the in-game self-check
guarantees the C# CODE agrees with its table. Neither half is load-bearing
alone; the composition is the parity claim.

WHY THIS FILE IS SEPARATE FROM THE FANFARE ONE. That fixture is a Furina
resource fixture and its C# mirror lives beside `FurinaResources`. These
vectors are engine-wide -- a companion power's damage, a passive's block, a
status timer -- and belong to no kit. Same idiom, different subject.

THE RULINGS PINNED HERE, and the register they share:

  * `NC-1` (R116, batch item 3) -- power-sourced DAMAGE runs the full damage
    pipeline: Strength, then Weak x0.75, then Vulnerable x1.5.
  * `NC-11` (R116, batch item 4) -- power-sourced BLOCK is RAW: exempt from
    both Dexterity and Frail.

They are adjacent, opposite, and R116 recorded them together precisely
because they will otherwise be misremembered as one rule.

  * `NC-7` (R116, batch item 5) -- Frozen is a DURATION COUNTER, decremented
    once at the end of each enemy side, with stacking extending it. The mod
    already implemented the timer and the sim adopted it; the vectors are the
    shared law rather than one side's answer.
"""

from __future__ import annotations

import json
import random
import re
from pathlib import Path

from tier0 import constants as C
from tier0.engine import powers
from tier0.engine.state import CombatState, Enemy, Player

_VECTORS = (Path(__file__).resolve().parents[2]
            / "docs" / "noncard-parity-vectors.json")
_CSHARP = (Path(__file__).resolve().parents[2] / "klee-mod" / "KleeCode"
           / "Diagnostics" / "NonCardParityVectors.cs")


# --------------------------------------------------------------------------
# NC-1 -- power-sourced damage through the full pipeline
# --------------------------------------------------------------------------
#
# Chosen to hit every branch rather than to look plausible. `amount` 6 and 8
# are Durin's Witch's Flame at base and upgraded (`WITCHS_FLAME` power stacks,
# `docs/mondstadt-companions.yaml`) -- NC-1's own line evidence, which R116
# ruled becomes the regression vector.
#
#   (0,0,0)  no modifier at all -- the identity row. If this one moves, the
#            fix broke the base case rather than the modifiers.
#   strength only     -- additive, and it lands BEFORE the multipliers.
#   weak only         -- x0.75, floored.
#   vulnerable only   -- x1.5 on the target, AFTER the dealer's half.
#   weak + vulnerable -- 0.75 * 1.5 = 1.125, the row that catches a chain
#                        applied in the wrong order or truncated twice.
#   strength + both   -- all three at once, the shape a real buffed fight has.
#   strength 5 on 6   -- 11 * 0.75 = 8.25 -> 8: the truncation is at the END,
#                        so an implementation that truncated after the Weak
#                        step and then multiplied by 1.5 answers differently.
#   negative strength -- the clamp at zero. `powers._floor` exists because the
#                        chain must not deliver negative damage.
_DAMAGE_CASES = [
    (6, 0, 0, 0),
    (6, 3, 0, 0),
    (6, 0, 1, 0),
    (6, 0, 0, 1),
    (6, 0, 1, 1),
    (6, 3, 1, 1),
    (6, 5, 1, 0),
    (6, 5, 1, 1),
    (8, 0, 0, 0),
    (8, 4, 0, 1),
    (8, 0, 1, 1),
    (8, -20, 0, 0),
    (1, 0, 1, 0),
    (1, 0, 0, 1),
    (3, 2, 1, 1),
    (25, 7, 1, 1),
]


def _damage(amount: int, strength: int, weak: int, vulnerable: int) -> int:
    """The sim's own funnels, in the sim's own order.

    `effects.deal_damage_to_enemy` is `modify_damage_dealt` ->  reaction
    amplification -> `modify_damage_taken` -> a single `int()`. Witch's Flame
    passes `element=None` (the aura is consumed, not re-applied), so the
    amplification step is the identity and these two funnels are the whole
    pipeline for this family.
    """
    dealer = Player(character_id="klee", hp=70, max_hp=70)
    dealer.powers["strength"] = strength
    dealer.powers["weak"] = weak
    target = Enemy(hp=999, max_hp=999, name="vector", intents=[])
    target.powers["vulnerable"] = vulnerable
    dmg = powers.modify_damage_dealt(dealer, amount)
    dmg = powers.modify_damage_taken(target, dmg, attacker=dealer,
                                     from_card=False)
    return int(dmg)


# --------------------------------------------------------------------------
# NC-11 -- power-sourced block is raw
# --------------------------------------------------------------------------
#
# The vector's SUBJECT is the exemption, so every row carries a Dexterity and
# a Frail that would move a CARD's block and must not move this one. The
# comparison row is what the card funnel answers for the same inputs: a table
# where raw and funnelled agreed would pin nothing.
#
# Amounts are the three named grants' own numbers -- Metallicize stacks, the
# Ceremonial Garment rider (`GARMENT_ATTACK_BLOCK`) and the Kurage pulse
# (`KURAGE_PULSE_BLOCK` plus ward) -- so a retune of any of them is visible
# here rather than only in play.
_BLOCK_CASES = [
    (5, 0, 0),
    (5, 3, 0),
    (5, 0, 1),
    (5, 3, 1),
    (2, 2, 1),
    (8, -2, 0),
    (0, 4, 1),
    (12, 5, 1),
]


def _block(amount: int, dexterity: int, frail: int) -> tuple[int, int]:
    """(raw, funnelled) for the same inputs.

    RAW is what the three exempt writers do -- `fighter.block += amount`,
    reaching neither funnel. FUNNELLED is `powers.modify_block_gained`, the
    card-block path, and it is here only as the contrast: the ruling is that
    these two numbers may differ and the mod must answer the first.
    """
    fighter = Player(character_id="kokomi", hp=70, max_hp=70)
    fighter.powers["dexterity"] = dexterity
    fighter.powers["frail"] = frail
    return amount, powers.modify_block_gained(fighter, amount)


# --------------------------------------------------------------------------
# NC-7 -- Frozen is a duration counter
# --------------------------------------------------------------------------
#
# (applications, enemy sides elapsed) -> turns of freeze remaining. The whole
# content of the timer half of the ruling, as arithmetic:
#
#   * one application lasts one enemy side -- the old boolean's behaviour,
#     which is why the change is invisible on single freezes;
#   * TWO applications last two, which is the half the sim adopted;
#   * the counter floors at zero and does not go negative, so a long fight
#     after the freeze expired is not carrying a debt;
#   * zero applications is zero at every elapsed count -- the row that would
#     catch a clock that granted a freeze by decrementing an absent one.
#
# The clock is UNCONDITIONAL in both engines: it does not ask whether the
# enemy acted. That is a property of the hook, not of this table, and it is
# pinned behaviourally in `tier0/tests/test_reactions.py`.
_FROZEN_CASES = [
    (0, 0), (0, 1), (0, 3),
    (1, 0), (1, 1), (1, 2),
    (2, 0), (2, 1), (2, 2), (2, 3),
    (3, 1), (3, 5),
]


def _frozen_remaining(applications: int, sides: int) -> int:
    """The sim's own counter, stepped the way `combat._run_rounds` steps it."""
    enemy = Enemy(hp=999, max_hp=999, name="vector", intents=[])
    for _ in range(applications):
        enemy.frozen += 1                      # stacking extends
    for _ in range(sides):
        if enemy.frozen > 0:
            enemy.frozen -= 1
    return enemy.frozen


# --------------------------------------------------------------------------
# NC-7 alpha -- the boss-room substitution is per-creature, minions only
# --------------------------------------------------------------------------
#
# (boss room, target is minion) -> (frozen turns applied, vulnerable stacks).
# Q13 / R117, verbatim "I'd say A": in a boss ROOM, a creature carrying the
# game's MinionPower gets Frozen and every other creature gets the Vulnerable
# substitution. The two boss-room rows are the ruling's own required pair --
# (a) a minion, (b) a non-minion helper (Kaiser Crab's second claw, whose
# R116-stated freezability alpha deliberately overrides). The two non-boss
# rows are the negative control: outside a boss room the substitution never
# fires, minion or not.
#
# The C# side of this one is a PREDICATE, not arithmetic: RoomType == Boss
# and no MinionPower on the target (ReactionEffects.cs). The sim's mirror is
# `any(e.is_boss for e in state.enemies) and not enemy.is_minion`
# (reactions._react), and the derivation below runs that real path.
_FROZEN_BOSS_ROOM_CASES = [
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1),
]


def _frozen_boss_room(boss_room: int, is_minion: int) -> tuple[int, int]:
    """(frozen, vulnerable) after one hydro->cryo freeze on the target.

    The real reaction path: aura up, then the triggering hit through
    `reactions.resolve_hit`, so the vector pins the shipped predicate rather
    than a re-implementation of it.
    """
    from tier0.engine import reactions
    target = Enemy(hp=100, max_hp=100, name="vector_target", intents=[],
                   is_minion=bool(is_minion))
    enemies = [target]
    if boss_room:
        enemies.append(Enemy(hp=200, max_hp=200, name="vector_boss",
                             intents=[], is_boss=True))
    state = CombatState(player=Player(character_id="klee", hp=70, max_hp=70),
                        enemies=enemies, rng=random.Random(0))
    reactions.apply_aura(state, target, "hydro")
    reactions.resolve_hit(state, target, "cryo", 0.0)
    return target.frozen, target.powers.get("vulnerable", 0)


def _derive() -> dict:
    return {
        "_comment": (
            "GENERATED by tier0/tests/test_noncard_parity_vectors.py from "
            "the sim. Do not hand-edit; regenerate. The C# mirror is "
            "klee-mod/KleeCode/Diagnostics/NonCardParityVectors.cs and is "
            "checked against this."),
        "weak_dealt_mult": C.WEAK_DEALT_MULT,
        "vulnerable_taken_mult": C.VULNERABLE_TAKEN_MULT,
        "power_damage": [
            {"amount": a, "strength": s, "weak": w, "vulnerable": v,
             "dealt": _damage(a, s, w, v)}
            for a, s, w, v in _DAMAGE_CASES
        ],
        "power_block": [
            {"amount": a, "dexterity": d, "frail": f,
             "raw": _block(a, d, f)[0], "funnelled": _block(a, d, f)[1]}
            for a, d, f in _BLOCK_CASES
        ],
        "frozen": [
            {"applications": n, "sides": s,
             "remaining": _frozen_remaining(n, s)}
            for n, s in _FROZEN_CASES
        ],
        "frozen_boss_room": [
            {"boss_room": b, "is_minion": m,
             "frozen": _frozen_boss_room(b, m)[0],
             "vulnerable": _frozen_boss_room(b, m)[1]}
            for b, m in _FROZEN_BOSS_ROOM_CASES
        ],
    }


# --------------------------------------------------------------------------
# the tests
# --------------------------------------------------------------------------

def test_fixture_matches_the_sim():
    """The committed fixture is what the sim says today."""
    assert _VECTORS.exists(), f"missing fixture: {_VECTORS}"
    on_disk = json.loads(_VECTORS.read_text(encoding="utf-8"))
    assert on_disk == _derive(), (
        "docs/noncard-parity-vectors.json is stale -- regenerate with "
        "`python -m tier0.tests.test_noncard_parity_vectors`")


def test_power_damage_actually_scales():
    """NC-1's content, stated as behaviour rather than as a table.

    A vector table that happened to be all-identity would pass every
    comparison in this file and pin nothing, so the claim is asserted once
    directly: the modifiers move the number, in the ruled directions.
    """
    base = _damage(6, 0, 0, 0)
    assert base == 6
    assert _damage(6, 3, 0, 0) > base          # Strength adds
    assert _damage(6, 0, 1, 0) < base          # Weak cuts
    assert _damage(6, 0, 0, 1) > base          # Vulnerable amplifies
    # order: the dealer's half resolves before the target's, and the chain
    # truncates once at the end. 11 * 0.75 * 1.5 = 12.375 -> 12; truncating
    # after Weak would give 8 * 1.5 = 12 as well, so the discriminating row
    # is the one where the intermediate is not itself near-integral.
    assert _damage(6, 5, 1, 1) == int((6 + 5) * 0.75 * 1.5)
    assert _damage(8, -20, 0, 0) == 0          # clamped, never negative


def test_power_block_is_exempt_from_both_dials():
    """NC-11's content: the raw answer ignores Dexterity AND Frail, and the
    card funnel does not. The second half is the one that makes the first
    mean something."""
    for amount, dex, frail in _BLOCK_CASES:
        raw, funnelled = _block(amount, dex, frail)
        assert raw == amount
    assert _block(5, 3, 0)[1] != 5      # Dexterity moves card block
    assert _block(5, 0, 1)[1] != 5      # Frail moves card block


_POWERS_DIR = (Path(__file__).resolve().parents[2] / "klee-mod" / "KleeCode"
               / "Powers")


def test_the_three_exempt_block_grants_are_unpowered_in_csharp():
    """NC-11's mod-side fix, pinned as source text.

    The C# cannot be executed from here and the exemption is not arithmetic
    -- it is a FLAG. `ValueProp.Unpowered` is the predicate that Frail's
    multiplicative hook and Dexterity's additive hook both gate on, so the
    whole of the fix is which enum each of the three grants passes. Reading
    the call sites is the achievable check, and the same idiom
    `test_a7_port.py` already uses for an Unpowered claim.

    A grant that goes back to `ValueProp.Move` re-arms exactly the divergence
    R116 ruled against, and would otherwise be invisible until someone
    measured a Frail fight in game.
    """
    companions = (_POWERS_DIR / "CompanionPowers.cs").read_text(encoding="utf-8")
    kurage = (_POWERS_DIR / "KuragePowers.cs").read_text(encoding="utf-8")

    metallicize = companions.split("class MetallicizePower")[1]
    assert "GainBlock(Owner, Amount, ValueProp.Unpowered" in metallicize, (
        "Metallicize's block grant is not Unpowered -- NC-11 (R116) exempts "
        "power-sourced block from Frail and Dexterity")

    assert ("GainBlock(Owner, block, ValueProp.Unpowered" in kurage), (
        "the Kurage pulse's block grant is not Unpowered -- NC-11 (R116)")
    assert ("KokomiConstants.GarmentAttackBlock, ValueProp.Unpowered"
            in kurage), (
        "the Ceremonial Garment rider's block grant is not Unpowered -- "
        "NC-11 (R116). The Attack is its trigger, not its source")


_DMG_ROW = re.compile(
    r"new\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,"
    r"\s*(-?\d+)\s*\)")
_BLK_ROW = re.compile(
    r"new\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\)")
_FRZ_ROW = re.compile(
    r"new\(\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*\)")


def test_csharp_vectors_match_the_sim():
    """The C# mirror carries the same tables.

    A source-text check, deliberately: the C# cannot be executed from here, so
    the achievable guarantee is that the question sheet is identical on both
    sides. KleeSelfCheck does the other half in-game.
    """
    assert _CSHARP.exists(), f"missing C# mirror: {_CSHARP}"
    src = _CSHARP.read_text(encoding="utf-8")
    derived = _derive()

    block = src.split("PowerDamageVectors")[1].split("};")[0]
    got = [tuple(int(g) for g in m) for m in _DMG_ROW.findall(block)]
    want = [(r["amount"], r["strength"], r["weak"], r["vulnerable"],
             r["dealt"]) for r in derived["power_damage"]]
    assert got == want, f"C# power-damage vectors differ\n got={got}\nwant={want}"

    block = src.split("PowerBlockVectors")[1].split("};")[0]
    bgot = [tuple(int(g) for g in m) for m in _BLK_ROW.findall(block)]
    bwant = [(r["amount"], r["dexterity"], r["frail"], r["raw"])
             for r in derived["power_block"]]
    assert bgot == bwant, (
        f"C# power-block vectors differ\n got={bgot}\nwant={bwant}")

    block = src.split("FrozenVectors")[1].split("};")[0]
    fgot = [tuple(int(g) for g in m) for m in _FRZ_ROW.findall(block)]
    fwant = [(r["applications"], r["sides"], r["remaining"])
             for r in derived["frozen"]]
    assert fgot == fwant, (
        f"C# frozen vectors differ\n got={fgot}\nwant={fwant}")

    # Split on the DECLARATION: the array's name also appears in a doc
    # comment's <see cref> above the FrozenVectors table, and splitting there
    # would scan the wrong block.
    block = src.split("FrozenBossRoomVectors =")[1].split("};")[0]
    rgot = [tuple(int(g) for g in m) for m in _BLK_ROW.findall(block)]
    rwant = [(r["boss_room"], r["is_minion"], r["frozen"], r["vulnerable"])
             for r in derived["frozen_boss_room"]]
    assert rgot == rwant, (
        f"C# frozen boss-room vectors differ\n got={rgot}\nwant={rwant}")


def test_frozen_boss_room_substitution_is_alpha():
    """NC-7 alpha's content, stated as behaviour rather than as a table.

    Q13 / R117: minions only. The boss-room minion FREEZES, the boss-room
    non-minion helper takes the Vulnerable substitution instead, and outside
    a boss room the substitution never fires. The helper row is the ruling's
    own overridden example -- Kaiser Crab's second claw takes Vulnerable
    under alpha, not Frozen (R116's stated consequence, deliberately
    overridden; annotated at R116 and on the NC-7 execution note).
    """
    assert _frozen_boss_room(0, 0) == (1, 0)
    assert _frozen_boss_room(0, 1) == (1, 0)
    assert _frozen_boss_room(1, 0) == (0, C.FROZEN_BOSS_VULN)
    assert _frozen_boss_room(1, 1) == (1, 0)


if __name__ == "__main__":
    _VECTORS.write_text(
        json.dumps(_derive(), indent=2) + "\n", encoding="utf-8")
    print(f"wrote {_VECTORS}")
