"""`EB-597`: Shrink says it touches Attacks, and it touches a Skill's damage.

WHAT THE SEAT SAW (Kokomi r22, assembled lane, fight 2). Wearing
`Shrink -1 -- While Shrinker Beetle is alive, your Attacks deal 30% less
damage`, every face rewrote itself: Strike 6 to 4, Ambush 5 to 3, and
*Kurage's Oath* -- printed `cost 1, **skill**` -- 3 to 2. "Weak's glossary on
the same screen goes out of its way to say 'a Skill's damage too'; Shrink's
does not, and Shrink hits Skills anyway. That is a contradiction between a
debuff's text and its behaviour."

WHAT THE BASE GAME ACTUALLY DOES, read off the shipped assembly rather than
assumed: `ShrinkPower.ModifyDamageMultiplicative` calls
`ValuePropExtensions.IsPoweredAttack` and nothing else -- the identical gate
`WeakPower.ModifyDamageMultiplicative` uses. So Shrink is not Attack-CARD-only:
it bites any powered hit, which is exactly the class Weak bites, and "Attacks"
in the game's sentence means attack HITS.

SO THE ENGINE IS RIGHT AND ONLY THE WORDS WERE WRONG, which is `EB-469`'s,
`EB-481`'s and `EB-521`'s finding a fourth time. `KleeMod.InjectLocStrings`
merges the corrected `SHRINK_POWER` rows into the game's own `powers` table
and `blindplay_notes.BASE_KEYWORDS` carries the same sentence; the gate itself
is pinned in `Round22Tests`.

WHAT THIS FILE PINS is the sim's half of "the engines agree": a Skill's damage
clause goes through the dealer's percentage funnel exactly as an Attack's, so
the same 30% would land on the same face. Weak is the sim's own member of that
class -- it has no Shrink, because Shrink is an enemy-applied base-game debuff
this engine does not model -- and it is the term whose gate the C# shares.

NOTHING MEASURED HERE IS QUOTABLE (R215 B).
"""

from __future__ import annotations

from understudy import blindplay_notes
from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects, powers
from tier0.tests.conftest import make_enemy
from tier0.tests.test_kokomi_plan import kokomi_state, overhaul  # noqa: F401

OATH = "proto_kk_kurages_oath"


def test_a_skills_printed_damage_takes_the_dealers_cut(overhaul):
    """THE ROW'S ACCEPTANCE, sim side: *Kurage's Oath* is a SKILL, its own
    line prints 3, and a percentage debuff on her cuts it to 2 -- the seat's
    own arithmetic, one debuff over."""
    enemy = make_enemy(hp=40)
    state = kokomi_state(enemies=[enemy])
    card = loader.get_card(OATH)
    assert card.type == "skill"

    state.player.powers["weak"] = 1
    effects.resolve_card(state, card)

    printed = int(card.effects[0]["amount"])
    assert 40 - enemy.hp == int(printed * C.WEAK_DEALT_MULT)


def test_the_funnel_does_not_ask_what_type_the_card_is():
    """WHY the pin above is about a CLASS and not about one row.
    `powers.modify_damage_dealt` takes a fighter and a number: there is no
    card in its signature to read a `type:` off, which is the sim's spelling
    of the C#'s `IsPoweredAttack()` gating on the HIT."""
    import inspect

    params = list(inspect.signature(powers.modify_damage_dealt).parameters)
    assert params == ["attacker", "base"]


def test_the_page_says_which_and_quotes_the_measured_rate():
    """The gloss the row asked for. The rate is the shipped `ShrinkPower`'s
    own `DamageDecrease` var (30, already a percentage), read from the C# side
    by `Round22Tests`; what this pin holds is that the page states the rate
    and the class together."""
    row = blindplay_notes.BASE_KEYWORDS["Shrink"]

    assert f"{blindplay_notes.SHRINK_DEALT_PCT}% less damage" in row
    assert "a Skill's damage too" in row
    # And it says how long it lasts, which is the other half the game's own
    # line carries and the seat quoted back.
    assert "alive" in row
