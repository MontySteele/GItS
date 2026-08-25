"""EB-132: `times:` is not a damage-only field, and the gate now knows it.

THE DEFECT. tier0's `_op_block` reads `times:` and loops the WHOLE Block
gain, exactly the way `_op_damage` loops its hits — so
`{op: block, amount: 2, times: exhaust_pile}` pays `amount x pile` in the
sim. The C# emitter has no hit-count path for Block at all: it writes one
`await CreatureCmd.GainBlock` whatever `times` says. The gate that would have
caught the divergence sat one arm over — the `times` test lived INSIDE
`if op == "damage":` — so a runtime count the generator cannot express was a
NAMED BLOCKER on a damage row and INVISIBLE on a block row.

THE FIX IS A REFUSAL, NOT A LOOP, and the reason is in the row: **no committed
sheet row prints the shape**, so nothing has ever shipped wrong. The grammar is
honestly unavailable in BOTH engines until someone builds the C# loop, and a
named `blocked_reason` line is what that looks like. Building the loop
unasked would have been a behaviour change; blocking moves no number and no
generated file (`gen_roster_cards.py --check` reports all three profiles up to
date across the change).

WHAT IS PINNED HERE:

  * the block shape refuses, for a runtime count AND for a literal count —
    the emitter cannot count either;
  * the damage-arm control still answers exactly as it did: a `RUNTIME_TIMES`
    member and an X formula on an X-cost card still generate, a miss still
    blocks;
  * **the parity pin**: the set of ops whose tier0 resolver actually READS
    `times` is derived from `effects.OPS` source rather than restated, and
    every member is required to have a generator answer. Teaching a sixth op
    to honour `times` turns this file red until the generator has an answer
    for it, which is the whole point — the original defect was one op
    honouring a field that the gate only knew about on another.
"""

from __future__ import annotations

import inspect
import pathlib

import pytest
import yaml

from tier0.engine import effects
from tools import gen_klee_cards as gen

SHEETS = [
    pathlib.Path("docs/klee-cards.yaml"),
    pathlib.Path("docs/furina-cards.yaml"),
    pathlib.Path("docs/kokomi-cards.yaml"),
]


def _walk(effs):
    """Every effect dict reachable from an effect list, sly and modes included
    — the EB-134 walk's own reason for existing applies here too: a shape that
    hides in a nested list is not a shape the sheet does not print."""
    for eff in effs or []:
        if not isinstance(eff, dict):
            continue
        yield eff
        for key in ("effects", "then", "else", "sly"):
            nested = eff.get(key)
            if isinstance(nested, list):
                yield from _walk(nested)
        for mode in eff.get("modes") or []:
            if isinstance(mode, dict):
                yield from _walk(mode.get("effects"))


def _rows():
    for sheet in SHEETS:
        for row in yaml.safe_load(sheet.read_text(encoding="utf-8")):
            if isinstance(row, dict) and "id" in row:
                yield sheet.name, row


# --- the premise the refusal rests on --------------------------------------

def test_no_committed_row_prints_block_with_times():
    """The verification the fix branched on, kept as a fence.

    If this goes red a live card is using the shape, which means the MOD is
    behaving wrong today (one un-looped GainBlock against a looped sim gain)
    and the answer is no longer a `blocked_reason` line — it is the C# loop,
    with the mod-behaviour consequence declared. Read EB-132 before deleting
    this test."""
    offenders = [
        (sheet, row["id"], eff)
        for sheet, row in _rows()
        for eff in list(_walk(row.get("effects"))) + list(_walk(row.get("sly")))
        if eff.get("op") == "block" and "times" in eff
    ]
    assert offenders == [], (
        "a committed row prints block+times; EB-132's refusal is no longer "
        f"the honest fix: {offenders}")


# --- the block arm ---------------------------------------------------------

@pytest.mark.parametrize("times", [
    "exhaust_pile",        # a runtime count, the filing shape
    "salon_members",       # a RUNTIME_TIMES member: legal on damage, not here
    3,                     # a literal count: the emitter cannot loop it either
])
def test_block_times_is_blocked_by_name(times):
    card = {
        "id": "fabricated_block_times", "name": "Fabricated", "cost": 1,
        "type": "skill", "rarity": "common",
        "effects": [{"op": "block", "amount": 2, "times": times}],
    }
    reason = gen.blocked_reason(card, gen.KOKOMI_PROFILE)
    assert reason is not None, "block+times generated silently"
    assert "block" in reason and "times" in reason, reason


def test_block_without_times_still_generates():
    card = {
        "id": "fabricated_plain_block", "name": "Fabricated", "cost": 1,
        "type": "skill", "rarity": "common",
        "effects": [{"op": "block", "amount": 5}],
    }
    assert gen.blocked_reason(card, gen.KOKOMI_PROFILE) is None


# --- the damage-arm control, unmoved by the hoist --------------------------

def _damage_card(times, cost=1):
    return {
        "id": "fabricated_damage_times", "name": "Fabricated", "cost": cost,
        "type": "attack", "rarity": "common",
        "effects": [{"op": "damage", "amount": 3, "target": "enemy",
                     "times": times}],
    }


def test_damage_runtime_times_miss_still_blocks():
    reason = gen.blocked_reason(_damage_card("exhaust_pile"),
                                gen.KOKOMI_PROFILE)
    assert reason is not None and "exhaust_pile" in reason, reason


def test_damage_allows_a_runtime_times_member_and_an_x_formula():
    assert gen.blocked_reason(_damage_card("salon_members"),
                              gen.FURINA_PROFILE) is None
    assert gen.blocked_reason(_damage_card("X", cost="X"),
                              gen.KLEE_PROFILE) is None
    assert gen.blocked_reason(_damage_card(4), gen.KOKOMI_PROFILE) is None


# --- the parity pin --------------------------------------------------------

# The two ops whose `times` refusal lives in their OWN arm of blocked_reason
# rather than in `_times_reason`, and the arm that carries it. Listed rather
# than re-implemented so no shape acquires a second, differently-worded
# refusal — the pin below still requires each of them to refuse.
ELSEWHERE = {
    "apply_power": "APPLY_POWER_FIELDS totality",
    "repeat_this": "literal-int check in the conditional arm",
    "replay_next_companion": "literal-int check in its own arm",
}


def _ops_reading_times() -> set[str]:
    """Derived from the engine, not restated: every registered op whose
    resolver source mentions the `times` field."""
    found = set()
    for name, fn in effects.OPS.items():
        try:
            src = inspect.getsource(fn)
        except OSError:                             # pragma: no cover
            continue
        if 'fx.get("times"' in src or 'fx["times"]' in src:
            found.add(name)
    return found


def test_every_times_honouring_op_has_a_generator_answer():
    honouring = _ops_reading_times()
    assert honouring, "the source probe found no ops; it has rotted"
    # The two the generator answers through _times_reason.
    assert {"damage", "block"} <= honouring
    unaccounted = honouring - {"damage", "block"} - set(ELSEWHERE)
    assert unaccounted == set(), (
        f"ops {sorted(unaccounted)} honour `times:` in tier0 and the "
        "generator has no recorded answer for them — EB-132's defect exactly. "
        "Give each one an arm (or a line in _times_reason) before shipping a "
        "row that prints it.")


@pytest.mark.parametrize("op", sorted(ELSEWHERE))
def test_the_ops_answered_elsewhere_really_do_refuse(op):
    """ELSEWHERE is a claim about other arms; this is the claim under test."""
    bodies = {
        "apply_power": {"op": "apply_power", "power": "strength",
                        "amount": 1, "target": "self", "times": "exhaust_pile"},
        "repeat_this": {"op": "conditional", "if": "killed_target",
                        "then": [{"op": "repeat_this", "times": "exhaust_pile"}]},
        "replay_next_companion": {"op": "replay_next_companion",
                                  "times": "exhaust_pile"},
    }
    card = {
        "id": "fabricated_elsewhere", "name": "Fabricated", "cost": 1,
        "type": "skill", "rarity": "common", "effects": [bodies[op]],
    }
    assert gen.blocked_reason(card, gen.KOKOMI_PROFILE) is not None, (
        f"{op} accepted a runtime `times` the emitter cannot express "
        f"({ELSEWHERE[op]} no longer covers it)")
