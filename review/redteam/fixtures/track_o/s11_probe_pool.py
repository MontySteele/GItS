"""SLICE 11 fixture: pool census for the v14 `core_complete` limbs.

Read-only. Answers the questions the adversarial decks are built from:
which archetypes have a payoff at all, which cards fill two roles, which
non-playable rarities carry a role/archetype tag.
"""
from collections import Counter, defaultdict

from tier0.content import loader
from tier05 import draft


def census():
    idx = loader._card_index()
    by_arch = defaultdict(Counter)
    dual = []
    weird_rarity = []
    for c in idx.values():
        for a in c.archetypes:
            by_arch[a][c.role] += 1
        if getattr(c, "role_c", None) == "applier" and c.role == "payoff" \
                and "reaction" in c.archetypes:
            dual.append(c.id)
        if c.rarity in ("status", "curse") and (c.archetypes or
                                                c.role in ("enabler",
                                                           "payoff")):
            weird_rarity.append((c.id, c.rarity, c.role, c.archetypes))
    return by_arch, dual, weird_rarity


def draftable_census(character):
    """Payoffs reachable through the DRAFT pool, per archetype."""
    out = defaultdict(Counter)
    for c in loader._card_index().values():
        for a in c.archetypes:
            out[a][c.role] += 1
    return out


if __name__ == "__main__":
    by_arch, dual, weird = census()
    for a in sorted(by_arch):
        print(a, dict(by_arch[a]))
    print("DUAL applier+amp_payoff:", dual)
    print("status/curse with role/arch:", weird)
    print("DRAFT_CORE_SIZE", draft.C.DRAFT_CORE_SIZE,
          "GENERIC_PAYOFF_COVERAGE", draft.GENERIC_PAYOFF_COVERAGE)
