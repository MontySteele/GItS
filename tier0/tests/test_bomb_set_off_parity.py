"""Two Bomb rulings of 2026-10-04, pinned in both engines.

* THE BIG ONE'S x4 LAPSES WHEN ITS SET OFF FINDS NO BOMB. The card reads
  "Set off the enemy. Your Bombs deal quadruple damage.": the x4 belongs to
  that Set off. It used to stay armed, and a Mine answering the enemy's
  attack later that round peeked it.
* BIG BADDA BOOM'S "WHAT YOUR BOMBS DEALT" COUNTS THE BLOCK THEY REMOVED, as
  base-game "damage dealt" does. The C# banked the pre-Block hit
  (`ElementalHit.Deal` returns it) and the sim banked HP only, so the two
  disagreed whenever the target had Block.

Plus Hand Drill's half, C# only (the sim models no Hand Drill): a Bomb's hit
reports the Block it breaks to its applier's relics, the base relic's own
condition being "the breaker is my owner", not "a card attacked".

The sim halves run; the C# halves are source pins, the house pattern of
`test_reaction_phase_parity.py`, because an explosion needs a live combat.
"""

from __future__ import annotations

from pathlib import Path

from tier0.engine import combat, effects, klee_overhaul
from tier0.tests.conftest import make_enemy
from tier0.tests.test_klee_overhaul_rules import (  # noqa: F401 (fixture)
    ATTACKER, klee_state, load, overhaul)
from tier0.tests.test_reaction_phase_parity import DEAL_SIGNATURE, method_body

ROOT = Path(__file__).resolve().parents[2]
POWERS = ROOT / "klee-mod" / "KleeCode" / "Powers"
BOMB = (POWERS / "Prototype" / "ProtoBombPower.cs").read_text(encoding="utf-8")
HIT = (POWERS / "ElementalHit.cs").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# The Big One
# ---------------------------------------------------------------------------

def test_the_big_one_into_a_bombless_enemy_spends_its_multiplier(overhaul):
    bare = make_enemy(hp=200, name="bare", intents=ATTACKER)
    mined = make_enemy(hp=200, name="mined", intents=ATTACKER)
    state = klee_state([bare, mined])
    klee_overhaul.place(state, mined, 5, is_mine=True)

    with klee_overhaul.aimed_at(state, bare):
        effects.resolve_card(state, load("proto_ko_the_big_one"))

    assert klee_overhaul.peek_multiplier(state) == 1
    combat._enemy_turn(state, mined)
    assert [e["size"] for e in state.log
            if e["event"] == "ko_explosion"] == [5], "the Mine goes off at x1"


def test_a_set_off_largest_into_an_empty_board_spends_it_too(overhaul):
    enemy = make_enemy(hp=200)
    state = klee_state([enemy])
    klee_overhaul.arm_multiplier(state, 4)
    assert klee_overhaul.set_off_largest(state, enemy) == 0
    assert klee_overhaul.peek_multiplier(state) == 1


def test_the_csharp_set_off_takes_the_multiplier_before_its_empty_checks():
    set_off = method_body(
        BOMB, r"public\s+static\s+async\s+Task<int>\s+SetOff\s*\(")
    assert set_off.index("TakeMultiplier()") < set_off.index("taken.Count == 0")
    assert set_off.index("TakeMultiplier()") < set_off.index("target == null")
    largest = method_body(
        BOMB, r"public\s+static\s+async\s+Task<int>\s+SetOffLargest\s*\(")
    empty = largest[largest.index("bestPile == null"):]
    assert empty.index("TakeMultiplier();") < empty.index("return 0;"), \
        "the no-charge return spends it too"


# ---------------------------------------------------------------------------
# Big Badda Boom
# ---------------------------------------------------------------------------

def test_big_badda_boom_counts_the_block_its_bombs_removed(overhaul):
    enemy = make_enemy(hp=400)
    enemy.block = 10
    state = klee_state([enemy])
    klee_overhaul.place(state, enemy, 8)
    klee_overhaul.place(state, enemy, 9)

    effects.resolve_card(state, load("proto_ko_big_badda_boom"))

    explosions = [e for e in state.log
                  if e["event"] == "damage" and e["source"] == "set_off"]
    assert sum(e["amount"] for e in explosions) == 7, "10 Block ate the rest"
    assert sum(e["blocked"] for e in explosions) == 10
    hits = [e for e in state.log
            if e["event"] == "damage" and e["source"] == "attack"]
    assert len(hits) == 2
    assert hits[1]["base"] == 17, "what the Bombs dealt, Block included"


def test_the_csharp_bank_is_the_pre_block_hit():
    """`ElementalHit.Deal` hands `CreatureCmd.Damage` the number it returns,
    so the C# bank is the hit before Block; `Explode` banks that return."""
    deal = method_body(HIT, DEAL_SIGNATURE)
    assert "return landed;" in deal
    assert "await CreatureCmd.Damage(\n            choiceContext, target, landed," \
        in deal.replace("\r\n", "\n")
    explode = method_body(
        BOMB, r"private\s+static\s+async\s+Task<Element>\s+Explode\s*\(")
    assert "ledger.NoteExplosion(reacted, dealt, vulnerablePaid);" in explode


# ---------------------------------------------------------------------------
# Hand Drill
# ---------------------------------------------------------------------------

def test_every_elemental_hit_credits_the_block_break_to_its_applier():
    credit = method_body(
        HIT, r"private\s+static\s+async\s+Task\s+CreditBlockBreak\s*\(")
    assert "WasBlockBroken" in credit
    assert "relic.AfterBlockBroken(choiceContext, target, applier)" in credit
    assert HIT.count("await CreatureCmd.Damage(") == 3
    assert HIT.count(
        "await CreditBlockBreak(choiceContext, target, applier, results);") == 3, \
        "every hit of the funnel reports its break"
