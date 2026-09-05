"""`EB-481` / `EB-497`: Vulnerable's three printers say one rule, and it is
the engines' rule.

`EB-481`, REOPENED 2026-09-05. The row was closed once on the TIPS, and a tip
is not where a player meets Vulnerable: the seat meets it on the ENEMY, whose
status line is the base game's own `VULNERABLE_POWER` row and read "Receive
50% more damage from Attacks" while the glossary and the numbers said every
card hit. Two texts disagreeing about whether a Skill is safe is a player
sequencing badly (Kokomi r16/r17 lane 2: the Casket's Skill hit took the
1.5x). The mod now carries a `powers`-table row so the enemy's own line reads
what the box reads.

`EB-497`, THE SAME SENTENCE ONE CASE NARROWER. "Every hit" was one case too
wide: Explosive Ampoule dealt 10, not 15, into a Vulnerable Sewer Clam (Klee
r17 lane 1). The rule is READ OFF THE ENGINE rather than picked --

  * C#: `VulnerablePower.ModifyDamageMultiplicative` gates on
    `ValueProp.IsPoweredAttack()`, which every damage clause the generator
    emits carries and a potion's damage does not.
  * tier0: `potions.fire_potion` goes through `refpowers.unpowered_damage`,
    whose own docstring says it is "deliberately NOT
    effects.deal_damage_to_enemy", and `modify_damage_taken` is never reached.

-- so a card's hit is amplified whatever its `type:`, a potion's is flat, and
all three printed surfaces say exactly that.

THE THIRD PRINTER is `understudy.blindplay_notes.BASE_KEYWORDS`, already held
in step with the C# tip by `test_understudy_blindplay
.test_the_base_keyword_glossary_is_the_mods_own_tooltip_text`. What this file
adds is the surface that pin cannot see: the game's own status line.
"""

from __future__ import annotations

import random
from pathlib import Path

from tier0 import constants as C
from tier0.engine import effects, potions, powers, refpowers
from tier0.tests.conftest import make_state, make_enemy

from understudy import blindplay_notes

REPO = Path(__file__).resolve().parents[2]
MOD = REPO / "klee-mod" / "KleeCode" / "KleeMod.cs"


def _mod_source() -> str:
    return MOD.read_text(encoding="utf-8")


# ---- the enemy's own status line ------------------------------------------

def test_the_power_row_is_carried_and_says_cards():
    """The row `EB-481` reopened for. Keys are the shipped ones off
    `SlayTheSpire2.pck` v0.111.0."""
    src = _mod_source()

    assert '["VULNERABLE_POWER.description"] =' in src
    assert '["VULNERABLE_POWER.smartDescription"] =' in src
    assert '"Vulnerable creatures take [blue]50%[/blue] more "' in src
    assert '"damage from cards, a potion\'s aside."' in src


def test_the_status_line_no_longer_says_from_attacks():
    """The word the seat read. Both rows are the base's own sentence with one
    word moved, so "Attacks" must not survive in either."""
    src = _mod_source()
    start = src.index('["VULNERABLE_POWER.description"]')
    row = src[start:src.index("#endif", start)]

    assert "from Attacks" not in row
    assert "more damage from cards for [blue]{Amount}[/blue] " in row


def test_the_rows_are_arm_scoped_like_the_glossary_they_agree_with():
    """A release build does not police the base game's English -- the
    self-check says so in as many words -- and the glossary these words agree
    with is itself arm-only."""
    src = _mod_source()
    start = src.index('["VULNERABLE_POWER.description"]')

    assert "#if PROTOTYPE_CARDS" in src[:start]
    assert src[:start].rindex("#if PROTOTYPE_CARDS") > src[:start].rindex(
        "#endif")


def test_the_status_line_and_the_glossary_name_the_same_two_cases():
    """One rule, three printers: the two cases the seats actually met -- a
    Skill's damage counts, a potion's does not -- are on the enemy's line and
    in the glossary alike."""
    src = _mod_source()
    glossary = blindplay_notes.BASE_KEYWORDS["Vulnerable"]

    assert "cards" in src[src.index('["VULNERABLE_POWER.description"]'):]
    assert "card hit" in glossary
    assert "Skill's" in glossary
    assert "potion's does not" in glossary


# ---- and the engine the words are read off --------------------------------

def test_a_potions_damage_takes_no_vulnerable():
    """`EB-497`'s own case, and the reason the sentence says "cards"."""
    state = make_state(enemies=[make_enemy(hp=50)])
    state.rng = random.Random(0)
    state.enemies[0].powers["vulnerable"] = 5

    refpowers.unpowered_damage(state, state.enemies[0],
                               C.POTION_FIRE_DAMAGE)

    assert state.enemies[0].hp == 50 - C.POTION_FIRE_DAMAGE


def test_a_cards_hit_does_take_it_whatever_the_card_type():
    """The other half, and `EB-481`'s: a Skill's damage clause is a hit."""
    state = make_state(enemies=[make_enemy(hp=200)])
    state.enemies[0].powers["vulnerable"] = 1

    effects.deal_damage_to_enemy(state, state.enemies[0], 10, source="card")

    assert state.enemies[0].hp == 200 - int(10 * C.VULNERABLE_TAKEN_MULT)


def test_the_potion_path_is_the_one_that_skips_the_taken_hooks():
    """SOURCE-READ of why, so a re-route that quietly starts amplifying a
    potion fails here rather than making the printed sentence a lie."""
    fire = potions._op_fire_potion if hasattr(potions, "_op_fire_potion") \
        else None
    body = refpowers.unpowered_damage.__code__.co_names

    assert "modify_damage_taken" not in body
    assert powers.modify_damage_taken is not None
    assert fire is None or "unpowered_damage" in fire.__code__.co_names
