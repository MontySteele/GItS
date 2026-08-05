"""SLICE 11 fixture: per-limb detail probes.

  (a) fanfare limb: how much of it the Furina STARTER already closes;
  (b) reaction limb: a synthetic card that is BOTH applier and amp payoff
      (zero such cards exist in content today) -- is it double-counted?
  (c) spotlight limb: cards that are both access and spotlight-tagged
      machinery -- is the `not _is_spotlight_access` guard load-bearing?
  (d) purity: does `core_complete` mutate the deck it is handed?
  (e) `time_to_online`'s observed floor, which is what makes
      run_metrics.py's truthiness filter harmless today.

Run: PYTHONPATH=. python review/redteam/fixtures/track_o/s11_limb_details.py
"""
from __future__ import annotations

import copy

from tier0.content import loader
from tier05 import draft, model


def cards(*ids):
    return [loader.get_card(i) for i in ids]


def main():
    # (a) fanfare limb vs the starter
    st = cards(*loader.starting_deck("furina"))
    print("FANFARE starter: generation=%.1f (bar %s)  floor=%.1f (bar %s)  "
          "drafted_readers=%d (bar %d)  complete=%s" % (
              draft._fanfare_generation_total(st),
              draft.FANFARE_GENERATION_COVERAGE,
              draft._fanfare_floor_total(st), draft.FANFARE_FLOOR_COVERAGE,
              draft._drafted_readers(st), draft.FANFARE_PAYOFF_COVERAGE,
              draft.core_complete(st, "fanfare")))
    basic_readers = [c for c in loader._card_index().values()
                     if c.rarity == "basic" and draft._reads_fanfare(c)]
    print("  basic-rarity readers in content (invisible to the limb):",
          sorted(c.id for c in basic_readers))

    # (b) reaction: one card in two roles
    dual = copy.deepcopy(loader.get_card("sizzle"))
    dual.role_c = "applier"          # now an applier AND a reaction payoff
    assert draft._is_applier(dual) and draft._is_amp_payoff(dual)
    deck = [copy.deepcopy(dual), copy.deepcopy(dual)]
    print("REACTION 2 copies of one applier+payoff card: appliers=%d amps=%d "
          "complete=%s (deck size %d)" % (
              sum(1 for c in deck if draft._is_applier(c)),
              sum(1 for c in deck if draft._is_amp_payoff(c)),
              draft.core_complete(deck, "reaction"), len(deck)))
    real_dual = [c.id for c in loader._card_index().values()
                 if draft._is_applier(c) and draft._is_amp_payoff(c)]
    print("  cards in content that are BOTH:", real_dual or "NONE")

    # (c) spotlight: access-and-machinery cards
    both = [c.id for c in loader._card_index().values()
            if draft._is_spotlight_access(c) and "spotlight" in c.archetypes
            and c.role in ("enabler", "payoff")]
    print("SPOTLIGHT cards that are access AND spotlight-tagged e/p:", both)
    if both:
        d = cards(both[0], both[0])
        print("  2 copies of %s -> access=%d machinery=%d complete=%s"
              % (both[0],
                 sum(1 for c in d if draft._is_spotlight_access(c)),
                 sum(1 for c in d if draft._is_spotlight_machinery(c)),
                 draft.core_complete(d, "spotlight")))

    # (d) purity
    probe = cards("salon_debut", "casting_call", "gentilhomme_usher",
                  "grand_salon", "rapturous_applause")
    before = [(c.id, c.role, tuple(c.archetypes), repr(c.effects))
              for c in probe]
    for arch in ("salon", "fanfare", "reaction", "spotlight", "generic"):
        draft.core_complete(probe, arch)
        draft._core_progress(probe, arch)
    after = [(c.id, c.role, tuple(c.archetypes), repr(c.effects))
             for c in probe]
    print("PURITY: deck unchanged by core_complete/_core_progress:",
          before == after)

    # (e) time_to_online floor
    vals = []
    for ch, ar in (("klee", "demolition"), ("furina", "salon"),
                   ("kokomi", "priest"), ("furina", "fanfare")):
        for seed in range(25):
            r = model.run_one(ch, ar, ar, draft.assigned_policy, seed)
            if r.time_to_online is not None:
                vals.append(r.time_to_online)
    print("time_to_online observed: n=%d min=%s (a 0 would be dropped by "
          "run_metrics.py:50's truthiness filter)" % (len(vals),
                                                      min(vals) if vals else None))


if __name__ == "__main__":
    main()
