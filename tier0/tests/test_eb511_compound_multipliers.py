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
`SimDamagePipeline.Resolve`).

What was actually wrong was the shipped Salon block's reporting, one file
over; the Salon and the Spotlight left the sim on 2026-10-08, and the tests
that pinned them left with them. The sim emits the `damage` event from inside
the pipeline, at the landed number, which is why this file pins the
ARITHMETIC.
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


def _board(weak: bool, aura: str | None):
    p = loader.build_player("furina")
    p.energy = 3
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
    state = _board(weak=False, aura="hydro")
    _play(state, _companion_attack())

    assert _dealt(state) == int(BASE * C.VAPORIZE_MULT)


def test_weak_and_the_amplifier_compose():
    state = _board(weak=True, aura="hydro")
    _play(state, _companion_attack())

    assert _dealt(state) == int(BASE * C.WEAK_DEALT_MULT * C.VAPORIZE_MULT)


def test_the_pipeline_is_one_product_in_this_order():
    """SOURCE-READ of the order the tests above depend on, so a
    re-order that happens to keep these totals cannot pass silently: the
    dealer's terms, then the amplifier, then the target's."""
    body = effects.deal_damage_to_enemy.__code__.co_names

    assert body.index("modify_damage_dealt") < body.index("resolve_hit")
    assert body.index("resolve_hit") < body.index("modify_damage_taken")
    assert powers.modify_damage_dealt is not None
    assert reactions.resolve_hit is not None
