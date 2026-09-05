"""`EB-521`: Thorns' printed line and Thorns' trigger say one thing.

THE FIND (Kokomi r18 lane 2, fight 1). *"Thorns printed 'When hit by an
attack, deal 2 damage back.' On turn 2 I played Kurage's Oath -- a **skill** --
and Strike into a Thorns-2 body and lost 4 HP, i.e. Thorns fired on the skill
too. Vulnerable and Weak both print the clause 'a Skill's damage too'; Thorns
does not, and behaves as though it did."*

THE ENGINE IS RIGHT AND ONLY THE WORDS WERE WRONG, which is `EB-469`'s and
`EB-481`'s sentence for the third time. `ThornsPower.BeforeDamageReceived`
asks for a dealer and a POWERED attack and nothing else -- it never reads the
`DamageResult`, which is why a fully blocked hit is still thorned. A powered
attack is a property of the HIT rather than of the card, and every damage
clause the generator emits carries `ValueProp.Move` whatever `type:` its sheet
row declares, so a Skill that deals damage is thorned exactly like an Attack.
"An attack" in the game's sentence means an attack HIT.

WHAT THIS FILE READS INSTEAD OF THE DECOMPILE. The mod does not implement
Thorns -- it is the base game's power -- so the trigger cannot be pinned by
calling it. What CAN be pinned is the reference implementation this repo keeps
of it (`tier0/engine/refpowers`, written off the decompile and carrying its
reasoning in comments) and the row the mod merges into the game's own `powers`
table, which is the only printer of the sentence a player reads. Those two are
held together here.
"""

from __future__ import annotations

import re
from pathlib import Path

from tier0.engine import powers, refpowers
from tier0.tests.conftest import make_state, make_enemy

REPO = Path(__file__).resolve().parents[2]
MOD = REPO / "klee-mod" / "KleeCode" / "KleeMod.cs"


def _row(key: str) -> str:
    """The C# literals of one merged row, joined the way the compiler joins
    them -- a sentence written across four `+` continuations is one string to
    the player and must be one string to a pin."""
    src = MOD.read_text(encoding="utf-8")
    start = src.index(f'["{key}"]')
    body = src[start:src.index('",\n', start) + 1]
    return "".join(re.findall(r'"((?:[^"\\]|\\.)*)"', body)[1:])


# ---- the printed line -----------------------------------------------------

def test_the_power_row_is_carried_for_both_of_thorns_printers():
    """`EB-481`'s shape one power over: a description is a table lookup, so
    the only way to correct the game's own line is to carry a row."""
    src = MOD.read_text(encoding="utf-8")

    assert '["THORNS_POWER.description"] =' in src
    assert '["THORNS_POWER.smartDescription"] =' in src


def test_the_line_names_the_case_the_seat_met():
    """The Skill, said in the words Weak and Vulnerable already say it in, so
    three debuffs on one screen do not have three vocabularies."""
    for key in ("THORNS_POWER.description", "THORNS_POWER.smartDescription"):
        row = _row(key)
        assert "Every card hit is one" in row, key
        assert "a Skill's too" in row, key
        assert "a potion's is not" in row, key


def test_the_live_line_keeps_the_amount_hole():
    """The number a player prices the exchange with. The row is the base's own
    sentence with a clause added, holes and BBCode untouched."""
    assert "[blue]{Amount}[/blue]" in _row("THORNS_POWER.smartDescription")


def test_the_rows_are_arm_scoped_like_the_vulnerable_row_beside_them():
    """A release build does not police the base game's English -- the
    self-check says so in as many words -- and this row sits inside the same
    quarantine `EB-481`'s does."""
    src = MOD.read_text(encoding="utf-8")
    start = src.index('["THORNS_POWER.description"]')

    assert src[:start].rindex("#if PROTOTYPE_CARDS") > src[:start].rindex(
        "#endif")


# ---- and the trigger the words are read off -------------------------------

def test_a_powered_hit_is_thorned_whatever_the_card_that_dealt_it():
    """The seat's own case, from the other side of the board: the reference
    implementation asks only whether the HIT was a powered attack."""
    state = make_state()
    enemy = make_enemy(hp=40)
    state.enemies = [enemy]
    powers.apply_power(state, state.player, "thorns", 3)

    refpowers.on_damage_received(state, state.player, 5, enemy,
                                 powered_attack=True)

    assert enemy.hp == 37


def test_an_unpowered_hit_is_not():
    """The other clause on the line, and it is the same gate Vulnerable's
    "a potion's aside" is read off (`EB-497`)."""
    state = make_state()
    enemy = make_enemy(hp=40)
    state.enemies = [enemy]
    powers.apply_power(state, state.player, "thorns", 3)

    refpowers.on_damage_received(state, state.player, 5, enemy,
                                 powered_attack=False)

    assert enemy.hp == 40


def test_the_trigger_never_reads_the_damage_result():
    """Why the sentence says "when hit" and not "when damaged": a fully
    blocked hit is still thorned, which is the shape `FlameBarrier` shares and
    the reason neither line may grow an "unblocked" clause."""
    state = make_state()
    enemy = make_enemy(hp=40)
    state.enemies = [enemy]
    powers.apply_power(state, state.player, "thorns", 3)
    state.player.block = 99

    refpowers.on_damage_received(state, state.player, 0, enemy,
                                 powered_attack=True)

    assert enemy.hp == 37
