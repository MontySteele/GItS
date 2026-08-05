"""Track O / slice 08 reproducer 3 -- GRANTED PLAYS against every NEW field.

The stressor: a play granted by another card/effect (`combat.resolve_free_play`,
reached from `effects._free_play` / `autoplay_from_draw` / the on-exhaust sweep)
rather than played from hand. Family A dropped exactly these because its gate
sampled the state AFTER the play resolved.

This drives the same card three ways -- played from hand, granted, and granted
N times by one grantor -- and prints every Track D (D1/D2) and Track H (H1/H2)
counter `metrics.extract` produces, so a difference is a number and not a read.

Run:  PYTHONPATH=. python review/redteam/fixtures/track_o/s08-granted-plays.py
"""
from __future__ import annotations

import random

from tier0.engine import combat, reactions
from tier0.engine.state import Card, CombatState, Enemy, Player
from tier0.harness import metrics

FIELDS = ("cards_played", "total_damage_dealt", "reactions",
          "reaction_damage_amp", "reaction_damage_splash",
          "reaction_damage_dot", "energy_spent")
DICTS = ("aura_ops", "aura_applications_by_source", "reactions_by_name",
         "conditional_evaluated", "conditional_fired")


def _card(cid="probe") -> Card:
    """One attack that reacts (pyro into a hydro aura), puts an aura up with
    an explicit aura verb, and carries a conditional rider."""
    return Card(id=cid, name=cid, type="attack", cost=1, element="pyro",
                effects=[
                    {"op": "damage", "amount": 8, "target": "enemy",
                     "applies_element": True},
                    {"op": "apply_aura", "element": "hydro",
                     "target": "enemy"},
                    {"op": "conditional", "if": "reaction_triggered_by_this",
                     "then": [{"op": "block", "amount": 3}]},
                ])


def _state(hp=10_000, energy=3):
    st = CombatState(player=Player(hp=80, max_hp=80),
                     enemies=[Enemy(hp=hp, max_hp=hp, name="dummy",
                                    intents=[{"kind": "attack",
                                              "amount": 0}])],
                     rng=random.Random(0))
    st.player.energy = energy
    st.player.element = "pyro"
    st.player.cadence = "catalyst"
    return st


def _report(label, st):
    s = metrics.extract(st, hp_start=80)
    print(f"  {label}")
    print("    " + "  ".join(f"{f}={getattr(s, f)}" for f in FIELDS))
    for d in DICTS:
        v = getattr(s, d)
        if v:
            print(f"    {d}={v}")
    plays = [e for e in st.log if e["event"] == "play"]
    print(f"    `play` events: {[(e['card'], e['cost'], e.get('free', False)) for e in plays]}")
    return s


def one_play_each_way():
    print("A. one card, played from hand vs granted")
    st = _state()
    reactions.apply_aura(st, st.enemies[0], "hydro")
    c = _card()
    st.player.hand = [c]
    combat.play_card(st, c)
    manual = _report("manual", st)

    st = _state()
    reactions.apply_aura(st, st.enemies[0], "hydro")
    c = _card()
    combat.resolve_free_play(st, c)          # the granted path
    granted = _report("granted", st)

    diff = {f: (getattr(manual, f), getattr(granted, f))
            for f in FIELDS if getattr(manual, f) != getattr(granted, f)}
    print(f"    DIFF (manual, granted): {diff or 'none'}\n")


def n_grants_from_one_card():
    print("B. one grantor card that grants THREE plays "
          "(autoplay_from_draw, amount 3)")
    st = _state()
    reactions.apply_aura(st, st.enemies[0], "hydro")
    st.player.draw_pile = [_card(f"granted{i}") for i in range(3)]
    grantor = Card(id="grantor", name="Grantor", type="skill", cost=1,
                   effects=[{"op": "autoplay_from_draw", "amount": 3}])
    st.player.hand = [grantor]
    combat.play_card(st, grantor)
    _report("grantor + 3 granted", st)
    print()


def granted_killing_blow():
    print("C. the granted play lands the KILLING BLOW (Family A's case)")
    st = _state(hp=6)
    c = _card("finisher")
    combat.resolve_free_play(st, c)
    print(f"    fight over: {st.over}")
    _report("granted killing blow", st)
    print()


def grant_after_the_kill():
    print("D. a grantor whose FIRST granted play kills -- the remaining "
          "grants are never made")
    st = _state(hp=6)
    st.player.draw_pile = [_card(f"granted{i}") for i in range(3)]
    grantor = Card(id="grantor", name="Grantor", type="skill", cost=1,
                   effects=[{"op": "autoplay_from_draw", "amount": 3}])
    st.player.hand = [grantor]
    combat.play_card(st, grantor)
    _report("grantor + 1 of 3 granted", st)
    print(f"    cards left in draw pile: {[c.id for c in st.player.draw_pile]}")
    print()


if __name__ == "__main__":
    one_play_each_way()
    n_grants_from_one_card()
    granted_killing_blow()
    grant_after_the_kill()
