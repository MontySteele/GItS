"""EB-85 — Corrupted's damage PRECONDITION, pinned across both engines.

The EB-84 sweep closed five sim-side enchantment divergences and emptied
`lint_enchant_parity.KNOWN_DIVERGENCES`. Its sixth finding was deliberately
left out of that batch because it is not an ELIGIBILITY question at all:

    MegaCrit.Sts2.Core.Models.Enchantments.Corrupted
        public override decimal EnchantDamageMultiplicative(DamageProps props)
        {
            if (!props.IsPoweredAttack()) return 1m;

Eligibility says WHICH CARD may take the enchantment (Corrupted:
`CanEnchantCardType == Attack`, already held by `lint_enchant_parity`).
This says WHICH HIT the enchantment is willing to pay on, and the two are
independent -- an eligible card can still deal hits the hook refuses, and
Corrupted's own 2 HP self-damage row is exactly such a hit.

tier0 agrees today, but it agrees by ACCIDENT OF PLACEMENT: its multiplier
happens to sit inside `engine/effects._op_damage`'s `card.type == "attack"`
branch. Nothing said it had to, and either side could move alone -- the
multiplier hoisted above the branch in a refactor, or the game's guard
changing on a version bump -- and the sim would start paying Corrupted on a
hit the game refuses, silently, in the one place (damage) where the number is
never obviously wrong.

WHAT THIS FILE PINS, and how each half can go red:

  1. The C# transcription itself lives in ONE place --
     `lint_enchant_parity.GAME_DAMAGE_PRECONDITIONS` -- next to the
     eligibility table a human already re-checks when the game updates. The
     expected guard line is hard-coded HERE as well, so re-transcribing after
     a re-decompile reddens this file until somebody re-derives the sim side
     against the new guard. That is the whole point of the row: the two must
     not move independently.
  2. tier0's side is read STRUCTURALLY, off the `effects.py` AST rather than
     off behaviour, so a rider read that escapes the branch reddens even if no
     shipped card happens to exercise it yet. Every reference to the rider
     field must sit under an `if` whose test is the transcribed branch, and
     there must be at least one.
  3. Behaviour backs the structure up on the three cases the guard splits:
     an Attack pays the multiplier, a non-Attack does not, and the
     self-damage row (Corrupted's own printed cost) never does.

THE C# HALF IS A TRANSCRIPTION, NOT A LIVE READ, and that is the same bargain
`tools/lint_enchant_parity.py` already takes for `GAME_RULES`: decompiling
`sts2.dll` needs the game installed plus ilspycmd
(`tools/extract_base_game_pool.py` does it and says so), and these gates run
on a runner that has neither. The build the transcription was read against is
pinned in STATE (`sts2.dll` v0.107.1, re-decompiled 2026-08-13).
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from tier0.content import enchantments
from tier0.engine import effects
from tier0.engine.state import Card
from tier0.tests.conftest import make_enemy, make_state

REPO = Path(effects.__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools"))

import lint_enchant_parity as lep        # noqa: E402

PIN = lep.GAME_DAMAGE_PRECONDITIONS["corrupted"]

# The table states the branch in the source's own quoting; `ast.unparse`
# normalises quotes, so both sides go through the parser before comparison.
# Round-tripping the table entry also proves it is a parseable expression
# rather than a slogan.
SIM_BRANCH = ast.unparse(ast.parse(PIN["sim_branch"], mode="eval").body)


# ---------------------------------------------------------------------------
#  1 -- the C# side, transcribed once and asserted here
# ---------------------------------------------------------------------------

def test_the_game_side_guard_is_the_one_this_pin_was_derived_against():
    """Hard-coded on purpose. If a re-decompile moves the guard, the table is
    edited and THIS goes red -- which is the prompt to re-derive tier0's
    branch rather than quietly re-baseline the transcription."""
    assert PIN["cs_class"].endswith(".Enchantments.Corrupted")
    assert PIN["cs_hook"] == "EnchantDamageMultiplicative"
    assert PIN["cs_guard"] == "if (!props.IsPoweredAttack()) return 1m;"
    assert PIN["cs_predicate"] == "IsPoweredAttack"
    assert PIN["cs_predicate"] in PIN["cs_guard"]
    # A correspondence with no stated reason is a coincidence somebody wrote
    # down; the house rule for the neighbouring divergence table is the same.
    assert len(PIN["why"].split()) >= 20


def test_the_pin_names_a_live_enchantment_and_a_live_rider_field():
    assert "corrupted" in enchantments.CATALOG
    assert PIN["sim_field"] in enchantments.ENGINE_EXTENSIONS
    # The rider the CATALOG row actually writes is the field the pin guards.
    rider = enchantments.CATALOG["corrupted"].rider(None)
    assert PIN["sim_field"] in rider
    assert rider[PIN["sim_field"]] == 1.5


# ---------------------------------------------------------------------------
#  2 -- the sim side, read off the AST
# ---------------------------------------------------------------------------

def _rider_reads_and_their_guards() -> list[list[str]]:
    """Every read of the rider field in `effects.py`, with the `if` tests it
    sits under (innermost last), each unparsed to source text."""
    tree = ast.parse((REPO / "tier0" / "engine" / "effects.py")
                     .read_text(encoding="utf-8"))
    out: list[list[str]] = []

    def walk(node, guards: list[str]) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.Attribute) \
                    and child.attr == PIN["sim_field"]:
                out.append(list(guards))
            if isinstance(child, ast.If):
                walk_if(child, guards)
            else:
                walk(child, guards)

    def walk_if(node: ast.If, guards: list[str]) -> None:
        test = ast.unparse(node.test)
        walk(node.test, guards)
        for stmt in node.body:
            walk(stmt, guards + [test])
        for stmt in node.orelse:          # the else arm is NOT under the test
            walk(stmt, guards)

    walk(tree, [])
    return out


def test_every_read_of_the_multiplier_sits_under_the_card_type_branch():
    reads = _rider_reads_and_their_guards()
    assert reads, (
        f"no read of {PIN['sim_field']!r} found in effects.py at all -- the "
        "rider was renamed or removed, and this pin now checks nothing.")
    for guards in reads:
        assert SIM_BRANCH in guards, (
            f"a read of {PIN['sim_field']!r} in effects.py is not enclosed by "
            f"`if {PIN['sim_branch']}:` (its guards were {guards}). The game "
            f"gates the same multiplier on `{PIN['cs_guard']}`, and the card-"
            f"type branch is tier0's whole statement of that precondition. "
            f"Moving the read out of the branch moves tier0's precondition "
            f"independently of the game's -- which is the divergence EB-85 "
            f"exists to catch. If the game's guard moved, edit "
            f"lint_enchant_parity.GAME_DAMAGE_PRECONDITIONS and re-derive "
            f"this side deliberately.")


# ---------------------------------------------------------------------------
#  3 -- behaviour, on the three cases the guard splits
# ---------------------------------------------------------------------------

def _card(ctype: str, effs: list[dict]) -> Card:
    card = Card(id="probe", name="probe", cost=1, type=ctype, effects=effs)
    enchantments.apply(card, "corrupted", None)
    return card


def test_an_enchanted_attack_pays_the_multiplier():
    enemy = make_enemy(hp=100)
    state = make_state([enemy])
    effects.resolve_card(state, _card(
        "attack", [{"op": "damage", "target": "enemy", "amount": 10}]))
    # 10 * 1.5 = 15, truncated -- the engine's convention for a fractional
    # damage term. The 2 HP self-damage row rides along and is checked below.
    assert enemy.hp == 85


def test_an_enchanted_non_attack_does_not():
    """The card type could not carry Corrupted through `eligible` today, but
    the RIDER is per-instance and the branch is what refuses it. This is the
    case that goes wrong first if the read is hoisted."""
    enemy = make_enemy(hp=100)
    state = make_state([enemy])
    effects.resolve_card(state, _card(
        "skill", [{"op": "damage", "target": "enemy", "amount": 10}]))
    assert enemy.hp == 90


def test_the_self_damage_row_is_never_multiplied():
    """Corrupted's printed cost is `lose 2 HP`, dealt Unblockable | Unpowered
    | Move in game and so refused by the same `IsPoweredAttack` guard. In
    tier0 a `target: self` damage op returns before the branch."""
    state = make_state([make_enemy(hp=100)])
    before = state.player.hp
    effects.resolve_card(state, _card(
        "attack", [{"op": "damage", "target": "enemy", "amount": 10}]))
    assert before - state.player.hp == 2
