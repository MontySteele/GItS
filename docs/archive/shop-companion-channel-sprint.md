# Sprint Plan — Shop Companion Channel (§4.7 build-out)

> **Lifecycle: ARCHIVED** — superseded; kept verbatim as a record and never updated. Status index: `docs/registry/identifiers.md` §15.

**Status: PRE-REGISTERED 2026-07-25. Rulings R59–R62 ratified.**
**EXECUTED 2026-07-25 — outcome in `docs/shop-companion-channel-sprint-log.md`.**
This document supersedes the DRAFT-FOR-RED-PEN plan
(`docs/shop-companion-channel-plan.md`); that doc is retained as the decision
record and is not a build input.

> Filed into the repo at execution time, verbatim as authored. The §3
> predictions only mean anything if they were written down before the numbers
> were read, so they live here rather than in a chat log.

**Governing inputs:**
- `docs/teyvat-spire-design-principles.md` §4.7 (v1.11/v1.11a) — the ratified
  design, UNBUILT banner to be retired by this sprint's close-out.
- `docs/companion-value-vs-colorless-study.md` — empirical backing (esp. §7).
- `docs/shop-companion-channel-plan.md` — feasibility findings; factual table
  independently verified against the tree 2026-07-25 (all claims held).
- Rulings R59–R62 (below), ratified by Monty 2026-07-25.

---

## 1. Ratified rulings (pre-closed inputs — not open questions)

Paste-ready for `tier0/DECISIONS.md`; collision-renumber if another session
lands first.

### R59 — Shop slot 2 floor: Uncommon (D1 = option a)
Slot 2 is wildcard-nation, **Uncommon-or-Rare** at renormalized reward odds.
Rationale: preserves the premium-paid-channel thesis (base slot 2 is a
guaranteed Rare; a ~60%-Common wildcard would make the mod's shop *worse* than
base), matches study §7's finding that StS2 colorless has no common tier, and
— the tiebreaker — is robust to the nation-scoped banner. A guaranteed-Rare
slot 2 would interact with banner gating badly: runs where the banner thins a
nation's Rare tier leave a guaranteed-Rare slot drawing from a near-empty
eligible set. Base StS2 never had this problem because base colorless has no
banner. Guaranteed-Rare (b) rejected as brittle; as-written (c) rejected as
self-contradicting.

### R60 — Base colorless pool: shop-only override now; removal is a separate, [USER]-gated follow-up (D2 = option c, phased)
Phase 1 (this sprint): patch the merchant's colorless-entry population to draw
from the companion pool. `ColorlessCardPool` **stays populated** for its six
non-shop consumers, including all three `GetDistinctForCombat` sites.
Rationale: emptying the pool is the exact empty-draw softlock class already
paid for once (Dusty Tome → `lint_ancient_coverage.py`); full removal demands
a seven-consumer audit plus per-site invariant tests — a sprint of its own.
§4.7's additive-model rejection argued *reward-economy* fantasy dilution,
which does not automatically extend to Discovery-style in-combat generation
the player never drafts.
**Deferred, not rejected:** whether base colorless surfacing via in-combat
generation is a fantasy leak worth phase 2's blast radius is a taste call —
`[USER]` grades it after phase 1 is live at the table. Until graded, phase 2
is not scheduled.

### R61 — The sim models the shop channel (D3 = option a)
Companions become shoppable in `tier05/shop.py` (slot 1 nation-filtered +
Uncommon floor, slot 2 per R59, gold pricing by drawn rarity). Rationale:
§4.7's thesis is *pricing is the balance governor*; an unmeasured governor is
a design claim with no instrument attached. Distinguished from R2's relic
exemption: that is a static effect, this is an economy channel. This ruling
also answers the compounding question raised in the plan doc — the exemption
series stops at two; tier 0.5 models economy channels.

### R62 — `sucrose_astable`: cost 0 + Exhaust (v1.11a numbers restored)
Card goes to **0-cost, Exhaust: true** (from main's interim 1-cost,
no-Exhaust). Monty's grading: Bursts are not currently priced strongly enough
for the multi-copy-battery worry to bind — playing the card 4× to buy a Burst
at 4 total cost is not worth it — so the guard costs nothing to keep and the
0-cost reprice stands. Main's 2→1-no-Exhaust rebalance is **superseded**; the
§4.7 v1.11a changelog text ("2→0 cost + Exhaust") is restored as accurate. No
spec errata needed beyond a changelog note recording the supersession.
Mechanical changes: `docs/mondstadt-companions.yaml` line for
`sucrose_astable`: `cost: 1` → `cost: 0`, add `exhaust: true`.
`docs/klee-upgrades.yaml` comment "base cost is now 1" → "base cost 0,
Exhaust". Sheet is sole source of truth; no codegen defaults.

---

## 2. Tracks

Ordering: A is the prerequisite for B and C; D rides alongside B; E is
independent and can land first (it is two YAML lines and a changelog note).

### Track A — Companion `CardPoolModel` (size L, the prerequisite)
Build the companion pool class with `IsColorless => true`, loading both
companion sheets (Mondstadt + Fontaine), banner-aware.
- **Hard constraint:** the existing free-reward-slot path
  (`CompanionSlot.Roll` → `TryModifyCardRewardOptions`) is **untouched** this
  sprint. It does not go through a pool today and continues not to. Migrating
  it onto the new pool is a possible follow-up, not a ride-along.
- **Acceptance gate:** paired-seed comparison — reward-slot offers across a
  battery of seeds are byte-identical pre/post Track A. Any diff fails the
  track.
- **Cross-session note required before landing** (shared-schema rule): the
  pool class touches the shared loader surface all three character
  workstreams sit on.

### Track B — Merchant override (size M)
Harmony patch on the merchant's colorless-entry population
(`PopulateColorlessCardEntries` or the nearest patchable surface — precedent:
`CardFactory_CreateForMerchant_TypeFallback_Patch`).
- Slot 1: home-nation filter + Uncommon floor; 5-star Rares banner-gated per
  §4.2 (wiring, not design); falls through to Uncommon if the banner has
  emptied the nation's Rare tier (spec already defines this).
- Slot 2: per R59 — wildcard nation, Uncommon floor, renormalized odds,
  banner-gated 5-stars.
- **Verify before reuse:** confirm `MerchantCardEntry` actually prices off
  rarity in the decompile before assuming the base gold bands apply. If it
  does not, pricing becomes its own small item; do not invent bands silently.

### Track C — Sim channel (size M)
Extend `tier05/shop.py` per R61: companion stock in both slots, gold pricing
by drawn rarity, drafter allowed to buy. Remove (or route around) the
`character_pool` reuse and its ownership filter for the companion slots.
- **One variable per cell:** the shop channel lands in its own measurement
  window; no other draft-model change rides in the same battery.
- Predictions in §3 are registered now and graded in writing before results
  are read.

### Track D — Invariant tests (size M)
- Curated empty-draw-site list per house pattern: every site Track B touches
  gets a check that the companion pool cannot present an empty or
  under-N eligible set (nation × rarity × banner-state corners — the
  slot-1 worst case is a nation whose Uncommon+ tier is banner-thinned).
- Extend `lint_ancient_coverage.py` (or sibling) to know the companion pool
  as a rolled-from surface. Catch → generalize: this is instance two of the
  empty-draw class; the third mints the general lint if the pattern differs.
- Fallback behavior when a slot cannot fill: define it (skip entry? base
  fallback?) as part of this track — **an empty shop slot must be a decision,
  never a crash.** Proposed default: slot silently falls through to base
  colorless entry for that slot only (a bounded, shop-scoped use of the
  still-populated base pool per R60). Flag in close-out for [USER] taste
  grading alongside the R60 deferred item.

### Track E — R62 mechanical landing (size S, independent)
The two YAML edits + upgrade-sheet comment + §4.7 changelog supersession
note. Re-run the affected sim cells only if `sucrose_astable` sits in a
registered watchlist cell; otherwise no battery required (cost/Exhaust change
to an enabler-grade one-shot).

---

## 3. Pre-registered predictions (Track C — graded in writing before results are read)

P1. **Slot-1 buy-rate** (share of shop visits where the drafter buys slot 1)
    lands in **10–35%**. Below 10% = pricing over-governs (premium slot
    unbought); above 35% = under-priced relative to card-remove/relic
    competition for gold.
P2. **Winrate delta** from enabling the channel (paired-seed, channel on/off)
    is **positive but ≤ +2.0pp** overall. The channel is targeted access, not
    a power injection; pricing-as-governor predicts a small edge.
P3. **Slot-2 realized rarity mix** under R59 renormalization lands near the
    Uncommon-heavy end (directionally ≥60% Uncommon of purchases), because
    gold pressure biases toward the cheaper tier. This is a *diagnostic*, not
    an acceptance target (R14 discipline).

Null or out-of-band results are binding and logged; the knob order for any
retune is: gold bands first, floors second, odds last. Floors are ratified
(R59) and do not move inside this sprint's window.

## 4. Non-goals (carried verbatim from the plan doc, plus one)

- The Wish banner (§4.6) — still deferred.
- Card-removal shop *service* — unaffected; not a colorless card.
- Re-opening §4.3 enabler-not-carry — channel and pricing carry the balance.
- Any change to the free reward slot (enforced by Track A's acceptance gate).
- **Base-pool full removal (D2 phase 2)** — deferred behind the [USER]
  fantasy-leak grading; explicitly not in this sprint even as prep work.

## 5. [USER]-gated items

1. Close-out ratification of the sprint as a whole.
2. Fantasy-leak grading for R60 phase 2 (after live table time with phase 1).
3. Track D fallback-behavior taste check (empty-slot handling).
4. Prediction grading sign-off for P1–P3 (Claude grades in writing; Monty
   countersigns before any retune).

## 6. Handoff notes for the Code session

- Fresh clone; read this doc in full, then the plan doc §2 table for the
  file-level map. Do not read §4.7's prose as behavior — the UNBUILT banner
  comes down only at close-out, as this sprint's last commit.
- DECISIONS entries in §1 are paste-ready; collision-renumber if needed and
  note the collision in the commit message.
- Cross-session note for Track A goes out **before** the pool class lands,
  not with it.
- Suite must stay green at every track boundary
  (`python3 -m pytest tier0/tests tier05/tests -q` + C# build).
