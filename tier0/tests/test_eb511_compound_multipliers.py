"""`EB-511`: a reaction amplifier composes with every other multiplier on the
hit, and the number the page reports is the number that landed.

WHAT THE SEAT SAW (Furina r11, natural lane, (c) 1). Two readings, one turn
apart, that both said an amplifier had gone missing:

  * fight 3 turn 2 -- Chevreuse printed 7 under a Weak stack, carried a
    `Reaction preview: Vaporize 1.5x`, and "dealt 8". 8 is what you get if
    exactly one of the two 1.5s never applied, and nothing on the screen said
    which.
  * fight 4 turn 6 -- Crabaletta's line read "hit Seapunk for 4 Hydro, and
    left no aura on it", which is the glossary's own signature for a reaction
    having consumed the aura, at a number with no 1.5 anywhere in it.

NEITHER ENGINE DROPS THE AMPLIFIER, and this file is the pin that says so. The
pipeline is one product in both: the dealer's Weak, then the amplifier, then
the target's Vulnerable, truncated once
(`effects.deal_damage_to_enemy`; C# `ElementalHit.Deal` and
`SimDamagePipeline.Resolve`). Spotlight is earlier still -- it scales the
card's PRINTED number (`effects._spotlight_scale`, C#
`SpotlightSystem.PrintedDamageDelta`), so it enters as the base the rest
multiply.

WHAT WAS ACTUALLY WRONG was the Salon block's arithmetic, one file over: it
reported a member's act at `salon_tick_amount`, the tick's worth BEFORE the
pipeline, so under Weak a Crabaletta logged at 6 landed for 4 and a Vaporizing
one logged at 4 landed for 6. A seat reconciling the fight's HP against those
rows had no honest total left, and the leftover landed on the card it had just
played. The C# fix is `SalonMemberPower.PerformMember` filing
`ElementalHit.Deal`'s return -- the truncated landed amount it has returned
since `EB-270` for exactly this reason. The sim has no such row: it emits the
`damage` event from inside the pipeline, at the landed number, which is why
this file pins the ARITHMETIC here and the reporting is pinned in the C# suite
(`KleeTests/Prototype/Round17EngineTests.cs`).
"""

from __future__ import annotations

import random

from tier0 import constants as C
from tier0.content import loader
from tier0.engine import effects, powers, reactions
from tier0.engine.state import Card, CombatState
from tier0.tests.conftest import make_enemy

# Chevreuse -- Interdiction Fire's printed base, and the seat's card.
BASE = 7
ENEMY_HP = 400


def _board(spotlit: bool, weak: bool, aura: str | None):
    p = loader.build_player("furina")
    p.energy = 3
    if spotlit:
        p.spotlight = C.SPOTLIGHT_GUEST_CAST
    if weak:
        p.powers["weak"] = 1
    enemy = make_enemy(hp=ENEMY_HP)
    if aura:
        enemy.aura = aura
        enemy.aura_turns_left = C.AURA_DURATION_TURNS
    return CombatState(player=p, enemies=[enemy], rng=random.Random(11))


def _companion_attack() -> Card:
    """The seat's card in the sim's own spelling: a Pyro Companion Attack."""
    return Card(id="eb511_chevreuse", name="chevreuse", cost=1, type="attack",
                character="furina", tags=["companion"], element="pyro",
                effects=[{"op": "damage", "amount": BASE,
                          "applies_element": True}])


def _play(state, card):
    state.player.hand.append(card)
    effects.resolve_card(state, card)


def _dealt(state) -> int:
    return sum(row["amount"] for row in state.log
               if row["event"] == "damage")


def test_the_amplifier_alone_is_the_printed_multiplier():
    """The simple case the seat's fight 1 saw work: 7 -> 10."""
    state = _board(spotlit=False, weak=False, aura="hydro")
    _play(state, _companion_attack())

    assert _dealt(state) == int(BASE * C.VAPORIZE_MULT)


def test_weak_and_the_amplifier_compose():
    state = _board(spotlit=False, weak=True, aura="hydro")
    _play(state, _companion_attack())

    assert _dealt(state) == int(BASE * C.WEAK_DEALT_MULT * C.VAPORIZE_MULT)


def test_the_spotlight_scales_the_base_the_others_multiply():
    """Spotlight is not a hit multiplier: it rewrites the card's printed
    number and truncates there, which is why it is the base below and not a
    third factor in the product."""
    state = _board(spotlit=True, weak=False, aura=None)
    _play(state, _companion_attack())

    assert _dealt(state) == int(BASE * C.SPOTLIGHT_BASE_MULT)


def test_spotlight_weak_and_vaporize_all_three_land():
    """THE COMPOUND CASE, and the row's acceptance: the hit the seat could
    not reconcile, at the number both engines actually deal."""
    printed = int(BASE * C.SPOTLIGHT_BASE_MULT)
    state = _board(spotlit=True, weak=True, aura="hydro")
    _play(state, _companion_attack())

    assert printed == 10
    assert _dealt(state) == int(printed * C.WEAK_DEALT_MULT * C.VAPORIZE_MULT)
    assert _dealt(state) == 11


def test_a_dry_member_still_amplifies():
    """Fight 4 turn 6's shape: the dry three-quarters is applied to the
    TICK, and the amplifier then multiplies what the pipeline is handed.
    A dry Crabaletta on a Pyro aura pays 1.5x like a paid one."""
    state = _board(spotlit=False, weak=False, aura="pyro")
    state.player.salon = ["crabaletta"]
    state.player.powers["salon_member"] = 1
    state.player.encore = 0                       # dry: it cannot pay upkeep

    dry_tick = effects.salon_tick_amount(state, "crabaletta", paid=False)
    effects.salon_member_act(state, "crabaletta")

    assert dry_tick == int(C.SALON_MEMBERS["crabaletta"]["tick"]["damage"]
                           * C.SALON_DRY_DAMAGE_MULT)
    assert _dealt(state) == int(dry_tick * C.VAPORIZE_MULT)


def test_the_pipeline_is_one_product_in_this_order():
    """SOURCE-READ of the order the three tests above depend on, so a
    re-order that happens to keep these totals cannot pass silently: the
    dealer's terms, then the amplifier, then the target's."""
    body = effects.deal_damage_to_enemy.__code__.co_names

    assert body.index("modify_damage_dealt") < body.index("resolve_hit")
    assert body.index("resolve_hit") < body.index("modify_damage_taken")
    assert powers.modify_damage_dealt is not None
    assert reactions.resolve_hit is not None
