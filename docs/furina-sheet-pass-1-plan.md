# Furina Sheet Pass 1 — Plan ("The Card Pass")

**Date:** 2026-07-20. **Authorized:** furina-sprint-1-redpen.md ("Sheet
pass 1 is now fully unblocked") + user go. **Governing docs:** kickoff
v0.1 (statline CLEARED), principles v1.10, DECISIONS 61–64.
**Environment:** CONSTANTS_VERSION 2, DRAFTER_VERSION 2,
RUNTEMPLATE_VERSION 2, post-v1.10 world.

## Scope (per redpen closing section)

1. **furina-cards.yaml v0.1** — 75-card pool (4 basics, 31 commons,
   25 uncommons, 15 rares incl. the kit Burst → 14 draftable rares,
   Klee-shape). Archetypes: salon | spotlight | fanfare | generic.
   All numbers are PROPOSED pending user red-pen (house rule: card
   conversions/balance numbers are user calls; this pass ships the sheet
   + measurements + asks).
2. **Burst design + meter** — kit card per v1.9 (Retain, innate-on-charge,
   never in pool); meter size declared here; particle economy = skill
   tags + reactions + Salon ticks + Encore spend (kickoff §1).
3. **Salon grammar** — salon_member power on the oz_summon end-of-turn
   rails (audit verdict: SOLVED); tick costs Encore, overdraws into true
   HP (the priced-greed identity).
4. **Encore Performance + Guest Star generators** — new ops
   (copy_spotlighted_in_hand, generate_guest_star) under the four
   binding generator guardrails.
5. **Fanfare payoffs + uncapper** — per-fanfare damage formulas,
   threshold predicates, raise_fanfare_cap at nasty setup cost.
   NO passive accrual path, direct or laundered (a per-turn Encore
   trickle would launder passive Fanfare through the gain hook —
   deliberately not designed).
6. **Upgrades** — docs/furina-upgrades.yaml per upgrade-conventions.md;
   applier extended to multi-sheet.
7. **Pilot weights** — salon/spotlight/fanfare pilots; policy learns
   encore/selector/generator value (M5's anchor-drafted-nothing lesson).
8. **Wiring** — furina-cards.yaml into DOCS_CARD_SHEETS; character_pool
   gains the personal-sheet filter (latent cross-character card-reward
   bug, same class as the Prune catch).

## Measurements (pre-registered; null results binding)

- **Statline scorecard** vs kickoff §2 targets: starter + archetype-deck
  median at 1000 fights (A1 1.0–1.5, A2 ~3.0, A3 ~2.5, A4 4.3, A5 3.7,
  A6 4.2, A7 ~2.0; constraint A4>A1 hard on starter+median).
- **Spotlight baseline delta** (DECISIONS 63, MUST): archetype decks,
  relic disabled vs enabled, winrate delta in points. Watch-items:
  chevreuse_bursting_grenades, guest_neuvillette_judgment under 1.5×.
- **Acceptance criteria (kickoff §8):** #1 self-carry package must not
  beat Salon/Spotlight at median; #2 delete-test (companions-only probe
  vs the full Spotlight deck); #3 relevance/bands/identity floors.
- **EP + GS combat-coupled experiment** (DECISIONS 64, ONE experiment):
  real Encore Performance card; measures duplication median-vs-ceiling
  AND the Guest Star in-combat draw-variance floor that offer geometry
  cannot see.
- **Placeholder sweeps** (redpen ruling c): FANFARE_CAP_FRACTION
  {0.25, 0.5, 0.75}, SPOTLIGHT_SELF_MULT {1.0, 1.25, 1.5} — sweep data
  for the user's pick; stamped defaults do not move without a ruling.

## Out of scope

Winrate-band ratification (bands are PROPOSED from measurements, ratified
by user later — pass-3 pattern); cross-player selector passing; co-op
Fanfare audit (Tier 2); Fontaine 5-star Rares; tier05 full-run archetype
integration for Furina (draft-layer milestone scope); C# handoff.

## Gates

Sheet numbers + proposed bands + knob picks (Fanfare cap, self-rate,
HP, burst_max) → user red-pen at pass end. Placeholders remain sweep
anchors only until then.
