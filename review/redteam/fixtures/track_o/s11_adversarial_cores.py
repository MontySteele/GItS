"""SLICE 11 fixture: adversarial decks for the v14 `core_complete` limbs.

Every deck here is a MULTISET of real loader cards (or a deep copy with one
field bent), built to attack one limb of `tier05.draft.core_complete` at
DRAFTER_VERSION 14. Nothing is mutated in the loader index -- `get_card`
already hands out deep copies, and the two bent cards below are copies of
copies.

Run:  PYTHONPATH=. python review/redteam/fixtures/track_o/s11_adversarial_cores.py
"""
from __future__ import annotations

import copy
import random

from tier0 import constants as C
from tier0.content import loader
from tier05 import draft

SALON_ENABLERS = ("salon_debut", "casting_call", "gentilhomme_usher",
                  "usher_the_waves")
SALON_PAYOFF = "grand_salon"
DEMO_ENABLERS = ("jumpy_dumpty", "pop", "mine_toss", "double_pop")
DEMO_PAYOFF = "remote_detonator"


def cards(*ids):
    return [loader.get_card(i) for i in ids]


def bend(card_id, **fields):
    """A deep copy of one card with fields overwritten (unplayability etc)."""
    c = copy.deepcopy(loader.get_card(card_id))
    for k, v in fields.items():
        setattr(c, k, v)
    return c


# --- deck builders -------------------------------------------------------

def deck_n_copies_of_one_enabler(n=4, payoff=True):
    d = cards(*([SALON_ENABLERS[0]] * n))
    if payoff:
        d += cards(SALON_PAYOFF)
    return d


def deck_n_copies_of_one_payoff(n=4):
    return cards(*([SALON_PAYOFF] * n))


def deck_base_plus_upgraded(name=SALON_ENABLERS[0]):
    """Two distinct card IDs, one printed card."""
    return cards(name, name + "+", SALON_PAYOFF, SALON_PAYOFF + "+")


def deck_exactly_threshold():
    return cards(*SALON_ENABLERS[:3], SALON_PAYOFF)


def deck_threshold_minus_one():
    return cards(*SALON_ENABLERS[:2], SALON_PAYOFF)


def deck_unplayable_core():
    """DRAFT_CORE_SIZE on-plan cards that no player could ever cast."""
    d = [bend(i, cost=99, exhaust=True) for i in SALON_ENABLERS[:3]]
    d.append(bend(SALON_PAYOFF, cost=99, exhaust=True))
    return d


def deck_reaction_one_distinct_applier():
    """`appliers >= 2` fed by TWO COPIES of one card."""
    return cards("dahlia_sacramental_shower", "dahlia_sacramental_shower",
                 "sizzle")


def deck_spotlight_one_distinct_companion():
    return cards("lynette_box_trick", "lynette_box_trick", "limelight")


def deck_fanfare_basic_readers_only():
    """Generation + floor closed, readers all basic-rarity."""
    return (cards(*loader.starting_deck("furina"))
            + cards("the_sea_is_my_stage"))


ALL = {
    "n_copies_one_enabler_plus_payoff": (deck_n_copies_of_one_enabler, "salon"),
    "n_copies_one_payoff": (deck_n_copies_of_one_payoff, "salon"),
    "base_plus_upgraded": (deck_base_plus_upgraded, "salon"),
    "exactly_threshold": (deck_exactly_threshold, "salon"),
    "threshold_minus_one": (deck_threshold_minus_one, "salon"),
    "unplayable_core": (deck_unplayable_core, "salon"),
    "reaction_one_distinct_applier": (deck_reaction_one_distinct_applier,
                                      "reaction"),
    "spotlight_one_distinct_companion": (deck_spotlight_one_distinct_companion,
                                         "spotlight"),
    "fanfare_basic_readers_only": (deck_fanfare_basic_readers_only, "fanfare"),
}


def order_scan(deck, archetype, trials=64, seed=0):
    """core_complete must be a function of the MULTISET, not the order."""
    rng = random.Random(seed)
    base = draft.core_complete(deck, archetype)
    prog = draft._core_progress(deck, archetype)
    for _ in range(trials):
        shuffled = list(deck)
        rng.shuffle(shuffled)
        if draft.core_complete(shuffled, archetype) != base:
            return False, "core_complete"
        if draft._core_progress(shuffled, archetype) != prog:
            return False, "_core_progress"
    return True, None


def main():
    print(f"DRAFT_CORE_SIZE={C.DRAFT_CORE_SIZE} "
          f"GENERIC_PAYOFF_COVERAGE={draft.GENERIC_PAYOFF_COVERAGE} "
          f"FANFARE gen/floor/payoff="
          f"{draft.FANFARE_GENERATION_COVERAGE}/"
          f"{draft.FANFARE_FLOOR_COVERAGE}/{draft.FANFARE_PAYOFF_COVERAGE}")
    print()
    for name, (build, arch) in ALL.items():
        deck = build()
        counts = draft._generic_core_counts(deck, arch)
        print(f"{name:38s} arch={arch:9s} n={len(deck):2d} "
              f"generic_counts={counts} "
              f"complete={draft.core_complete(deck, arch)} "
              f"progress={draft._core_progress(deck, arch):.3f} "
              f"order_stable={order_scan(deck, arch)}")
    print()
    # empty deck, every limb
    for arch in ("reaction", "spotlight", "fanfare", "salon", "generic",
                 "no_such_archetype", ""):
        print(f"EMPTY DECK arch={arch!r:20s} "
              f"complete={draft.core_complete([], arch)} "
              f"progress={draft._core_progress([], arch)}")
    print()
    # starters: is any anchor ONLINE before a single card is offered?
    for char, arch in (("klee", "demolition"), ("klee", "spark"),
                       ("klee", "reaction"), ("klee", "generic"),
                       ("furina", "salon"), ("furina", "spotlight"),
                       ("furina", "fanfare"), ("furina", "generic"),
                       ("kokomi", "priest"), ("kokomi", "commander"),
                       ("kokomi", "assist"), ("kokomi", "generic")):
        try:
            starter = cards(*loader.starting_deck(char))
        except Exception as exc:                       # pragma: no cover
            print(f"STARTER {char}/{arch}: unavailable ({exc})")
            continue
        print(f"STARTER {char:7s}/{arch:11s} "
              f"counts={draft._generic_core_counts(starter, arch)} "
              f"complete={draft.core_complete(starter, arch)} "
              f"progress={draft._core_progress(starter, arch):.3f}")


if __name__ == "__main__":
    main()
