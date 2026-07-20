# Furina Sheet Pass 1 — Rulings (chat → Code)

**Date:** 2026-07-20. Independently verified: 220 green locally; sheet at
76 cards; healing law (2 heals, both rare) and off-element guardrail
(zero non-hydro applications) confirmed at source. Rulings on asks 1–7;
ask 2 is the centerpiece and shapes pass 2.

## R16 — Criterion-2 direction (ask 2): CARD-MEDIATED BOOSTING — RATIFIED BY USER ("power in the cards, not the relic")

The report's own §3A decomposition decides this. The relic's measured
value for *her* archetypes is the **Ovation-Fanfare economy** (fanfare
punisher 36.3% with relic vs 2.0% without; salon damage-mult delta
−0.2pt ≈ nothing) — while the **damage multiplier's biggest beneficiary
is the companions-only probe (+10.4pt), the exact deck the delete-test
convicts.** The always-on multiplier is, empirically, a subsidy paid to
the failure mode. Strengthening her machinery cards to out-compete
subsidized companions (option 1) would be an arms race against her own
relic.

**Ruled: move the empowerment into her cards.**

1. **The relic keeps:** selector delivery, the designation registry, and
   the Ovation-Fanfare hooks — the parts §3A proved load-bearing.
2. **The relic's passive multiplier is reduced or removed:**
   SPOTLIGHT_BASE_MULT swept over {1.0, 1.25} at pass 2; her cards grant
   the rest. Ship the sweep, don't guess.
3. **Her cards become the boost source:** commons/uncommons that raise
   the Spotlighted character's multiplier or grant flat Spotlighted
   riders for the turn/combat (stacking through the existing
   spotlight_mult plumbing — no new keyword, no new subsystem; §2.2a
   numbers-only enforcement applies identically since it is the same
   pipe). Generators/EP/texture get re-costed in this world, where a
   machinery slot buys multiplier instead of administration.
4. **Why this is right beyond the numbers:** the delete-test passes by
   construction (remove her cards → the mult goes with them → companions
   revert to colorless-discount rates); the machinery slots stop
   competing with companions and start powering them; and it IS
   Columbina's driver machinery, which was the strategic reason Furina
   exists. The failure mode taught the intended lesson one character
   early — the staircase is working.
5. **Median self-Spotlight framing (the §3B bonus finding): ACCEPTED as
   the fallback working.** At median depth-2, self-Spotlight + salon glue
   is Appendix A.4's floor doing its job; the companion-directed fantasy
   living at depth-4+ is what "draft-gated high-ceiling" means. Re-measure
   under card-mediation before any further framing worry — card-granted
   boosts change the per-slot math of aiming at companions.

Pass 2's Spotlight card list is authored under this ruling. Salon and
Fanfare card lists are NOT gated on it.

## R17 — Knob picks (ask 3): ALL RATIFIED BY USER

- **SPOTLIGHT_SELF_MULT = 1.25×: RATIFY.** The sweep proved it
  load-bearing (1.5× borderline-fails criterion 1). No longer a
  placeholder — this is now a measured design constant. (RATIFIED.)
- **FANFARE_CAP_FRACTION = 0.5: RECOMMEND.** The sweep brackets it
  (0.25 cripples punisher at 2.4%, 0.75 overheats at 63%); 0.5's 37.6%
  is the sane middle. RATIFIED by user. Note for pass 2: re-check under R16, since Ovation
  economics shift with card-mediation.
- **hp 60, burst_max 70: RATIFIED** (unremarkable, consistent with her
  A1-dreadful frontload and a 70-grade meter between Klee's 60 and a
  nuke-90).

## R18 — A6 instrument (ask 4): EXTEND. Instrument v2, with the R8 discontinuity discipline.

Aura uptime having no axis credit anywhere is not a Furina problem — it
is the mod's core system being invisible to the utility axis, and every
applier-identity character after her will misread the same way. Fix it
at character #2, not character #5. **Authorized: A6 v2 adds an
application-uptime component.** Requirements: ref_ironclad stays the
3.0 anchor (he applies nothing — component weighting must be defined so
the anchor is preserved; Code designs the composite); Klee's A6
re-derived under v2; **numbers discontinuous by design, labeled, old
snapshots archived** — the exact A4-probe-v2 pattern from R8. Furina's
declared 4.2 is then re-scored against an instrument that can actually
see her.

Co-op value remaining Tier-2-invisible: accepted, known scope.

## R19 — A2 deck bands (ask 5): reading RATIFIED; spotlight band HELD

The lag-not-growth reading is ratified (curve exponents 0.07–0.28
confirm no superlinearity; the ratio instrument structurally inflates
A1-dreadful engines; Klee deck-band precedent applies). **Ratify
salon_weighted 7.6 and fanfare_weighted 4.2. HOLD spotlight_weighted's
band** — the report itself held the winrate bands because banding a
known-broken archetype freezes the wrong world; the same logic applies
to its A2 band. It gets banded at pass 2 under R16.

A5 3.1 vs 3.7 and A7 1.5 vs 2.0: leave un-spent this pass, as the
report chose — the levers interact with R16's re-costing, so spending
them now tunes a world about to change. A7 over-delivering its weakness
is the acceptable direction (a weakness deeper than declared violates
nothing; a weakness shallower would).

## R20 — Upgrade convention (ask 6): SEPARATE UPGRADE SHEETS WIN

`*-upgrades.yaml` is the convention; inline `upgrade:` fields in card
sheets are deprecated. Reasons: the established machinery is built on
the sheets (tier0 upgrade dispatch, exhaustiveness tests, the mined
grammar doc, M7's UNAPPLIABLE discipline); the C# codegen already
consumes them (M9 shipped that way); card rows stay single-purpose; and
two sources of truth for the same delta is drift waiting to happen —
the inline entries ALREADY duplicate klee-upgrades.yaml deltas.

Directives:
1. The Klee session reverts its inline fields from klee-cards.yaml
   (their file, their revert; the deltas already live in
   klee-upgrades.yaml, so nothing is lost).
2. The loader tolerance field STAYS but is promoted from silent-ignore
   to **loud deprecation warning**, plus a test asserting no sheet
   carries inline upgrades once the revert lands — silent-ignore risks
   someone authoring an inline-only upgrade that never applies.
3. Working-agreement for DECISIONS: **schema changes to shared loaders
   require a cross-session note before landing.** Today's brick was
   cheap; the next one might eat a measurement day.

## R21 — Registration (i) instrument (ask 7): APPROVED

Graded encounter battery at pass 2; the EP median-vs-ceiling
registration stays open rather than force-closed. Holding a registration
open across two instruments-too-coarse results is exactly right — do
not let anyone summarize it as "EP showed no effect."

## R22 — Sheet red-pen (ask 1): SEQUENCED, not skipped

Law compliance is already test-enforced (verified). The card-by-card
pricing/taste pass is deferred and split: **salon + fanfare + basics
red-pen happens next chat session** (they are stable worlds); **the
Spotlight card list is not red-penned as-is** — it gets re-authored
under R16 and reviewed then. Pricing an archetype scheduled for
redesign would be wasted pen. Naming/lore audit rides with the user's
pass per v1.7.

## Commendations for the record

The aiming-v1 hijack: root-caused mid-experiment, fixed, re-run, and the
GS null honestly re-reported post-fix. Winrate bands held back for the
broken archetype instead of frozen wrong. DECISIONS 68 (Klee's rewards
would have offered Furina's cards) — the second cross-character
containment catch this project; the personal-sheet filter earns its
test. And the §3A decomposition that decided R16 — the experiment we
pre-registered to price the passive ended up choosing the architecture.
That is the instrument stack working exactly as built.
