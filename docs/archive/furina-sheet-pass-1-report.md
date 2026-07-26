# Furina Sheet Pass 1 — Report ("The Card Pass")

**Date:** 2026-07-20. **Plan:** furina-sheet-pass-1-plan.md. **Governing:**
kickoff v0.1 (statline CLEARED), principles v1.10, DECISIONS 61–68.
**Environment:** CONSTANTS_VERSION 2, DRAFTER_VERSION 2,
RUNTEMPLATE_VERSION 2. Suite: 220 green. Official numbers at 1000
fights/encounter, seed 20260720.

## 1. Shipped (all behind tests)

- **furina-cards.yaml v0.1** — 76 cards (5 basics, 31 commons, 25
  uncommons, 15 rares; kit Burst → 14 draftable rares). Numbers iterated
  through four tuning rounds against the scorecard; ALL PROPOSED pending
  red-pen. Naming: talent/summon names verified; the rest is authored
  theatrical flavor — v1.7 lore audit before ship.
- **Salon Members** on the summon rails: `salon_member` stacking power,
  hydro tick per member at START of player turn, 1 Encore upkeep/tick,
  true-HP overdraw when dry. Start-of-turn timing is a measured decision
  (DECISIONS 65): end-of-turn upkeep drained the buffer before enemy hits
  and zeroed the default archetype's elite A4.
- **Burst**: "Let the People Rejoice" (kit, v1.9) — mass hydro scaling
  +1 per 4 Fanfare, +6 Encore. Meter 70; particles from skill tags (5),
  reactions (5), Salon ticks (2/member/turn), Encore spend (1/point).
- **Fanfare payoffs**: `N_per_M_fanfare` damage formulas, threshold
  predicates, `fanfare_attack_per10` power, `raise_fanfare_cap` uncapper
  (rare, blood-priced). No passive accrual path exists; test enforces no
  card may launder one (a per-turn Encore trickle would).
- **Guest Star generators**: `generate_guest_star` under all four
  guardrails, each structural (equal-rarity filter; Exhaust on sheet;
  tokens die with the combat; pool = shared companions + Guest Star set
  only — playable-character cards absent by construction).
- **Encore Performance**: `copy_spotlighted_in_hand` — dead without a
  designated star and a drafted target, by design.
- **Spotlight texture**: `spotlight_discount` / `spotlight_draw`
  (first-Spotlighted-card riders, the two ratified lines verbatim),
  `spotlight_encore` (per play), `spotlight_flat_damage` (numbers-only
  rare rider). Selector-payoff predicates (moved-this-turn /
  unmoved-this-combat).
- **Selector aiming v2** (DECISIONS-worthy, measured): v1's
  companions-always-preferred rule let a single generated guest hijack
  the Spotlight from a 20-card self-kit, HALVING Ovation throughput.
  v2 runs a depth contest with self on equal footing; companions win
  ties (full rate beats reduced at equal depth).
- **furina-upgrades.yaml** per the mined grammar (applier now
  multi-sheet), including the previously-missing Fontaine companion
  upgrade section. Generator upgrades use the kickoff §9 grammar
  (guest costs 0, Discovery parity).
- **Pilots**: salon / spotlight / fanfare weight files; policy learns
  Encore value, Spotlight-machinery value, and sees the Spotlight
  multiplier in expected damage (the DECISIONS-53 lesson applied).
- **Wiring**: sheet into DOCS_CARD_SHEETS; `character_pool` gains the
  personal-sheet filter (DECISIONS 68 — Klee's rewards would have
  offered Furina's cards). Klee's world verified unchanged: all
  ratified bands + fragility locks pass throughout.

## 2. Statline vs declaration (1000 fights; kickoff §2 targets)

| Axis | Target | Starter | Median | Verdict |
|---|---|---|---|---|
| A1 Frontload | 1.0–1.5 | **1.2** | 2.6 | Starter EXACT; median reads higher because engines ramp (see A2 note) |
| A2 Scaling | ~3.0 | 4.9 | 4.2 | OVER — instrument artifact in part; deck-bands proposal below |
| A3 Block | ~2.5 | 3.7 | **2.4** | Median on target |
| A4 Sustain | **4.3** | **4.4** | 5.2 | Starter EXACT; median a shade hot (fanfare deck saturates) |
| A5 Velocity | 3.7 | 3.0 | 3.1 | UNDER by ~0.6 — ask 5 |
| A6 Utility | **4.2** | 1.5 | 3.6 | UNDER — but the instrument cannot see her declared A6 sources (ask 4) |
| A7 Setup tax | ~2.0 | 1.0 | 1.5 | More taxed than declared (weakness over-delivers; acceptable direction?) |

Shape heuristic passes on starter AND median; A4>A1 constraint holds
hard everywhere it must. Curve exponents 0.07–0.28 (no superlinearity).

**A2 finding:** the ratio instrument (t8-10 / t2-4) structurally inflates
any A1-dreadful engine character — her low early window is the
denominator. Salon deck reads 7.3 with curve exponent 0.28 (i.e., not
actually superlinear; it's lag, not growth). Klee precedent: per-deck A2
bands govern this (hers reach 4.8). **Proposed deck bands (red-pen):**
salon_weighted 7.6, spotlight_weighted 4.6, fanfare_weighted 4.2.

**A6 finding (instrument gap):** her declared A6 sources are "hydro aura
uptime, party buffs, debuff texture" — the A6 instrument measures swarm
DPT + debuff stacks only. Aura uptime has NO axis credit anywhere, and
her co-op value (Klee's dream partner) is Tier-2-invisible by
construction. Measured 3.6 with the gap known. Ask 4.

## 3. Pre-registered experiments (null results binding)

### A. Spotlight baseline delta (DECISIONS 63) — measured in points

Mean delta across the four core encounters, relic on vs off:
salon **−0.2pt** (self-mult on modest numbers ≈ nothing), spotlight
**+7.2pt** (attrition +26.0), fanfare **+9.1pt**, self_carry +9.2pt,
companions-only probe +10.4pt. Notable decomposition: for her solo decks
the relic's value is mostly the **Ovation-Fanfare economy** (fanfare deck
punisher 36.3% with relic vs 2.0% without), not the damage multiplier.
The relic is load-bearing for the Fanfare archetype.

### §8 criterion 1 — PASSES

self_carry never beats the archetype max on any encounter (punisher:
36.3% vs salon 92.8%; tank_boss 1.4% vs 61.0%).

### §8 criterion 2 delete-test — **FAILS. Headline finding.**

The companions-only probe BEATS the full Spotlight deck on every
encounter (punisher 6.2% vs 2.5%, attrition 98.5% vs 95.9%, tank_boss
1.3% vs 0.4%). Her Spotlight-machinery cards (generators, EP, texture
powers) are currently **negative-value slots** vs just-more-companions.
Per the redpen delete-test note this is the real signal, no carve-outs:
either her Spotlight payoffs get stronger, or the archetype moves toward
card-mediated boosting (the Columbina shape). **Ask 2 — this gates the
Spotlight archetype's card list at pass 2.**

### B. EP + GS combat-coupled (DECISIONS 64)

Committed-Chevreuse drafted runs (400) then real fights. Drafted depth:
median 2 (consistent with sprint 1's P(≥4)=0.20 — the slot is luck-gated
as declared).

- **Registration (i), duplication median-vs-ceiling: STILL OPEN —
  instrument saturated.** The 4-encounter battery quantizes run winrate;
  median AND P90 pin at 0.500 for every arm. Needs a finer instrument
  (more fights/run or graded encounters) at pass 2. Not retried.
- **Registration (ii), GS floor: NULL under current policy** — +GS costs
  ~2pt mean winrate and lifts nothing. Root cause found and fixed
  mid-experiment (aiming v1 hijack, above); post-fix the arms remain flat
  (base 0.477, +EP 0.439, +GS 0.450, +EP+GS 0.409): at median depth 2
  the machinery dilutes. Coherent with criterion-2's failure: the
  machinery must earn slots before generation can show a floor.
- **Bonus structural finding:** at median drafted depth the depth
  contest RATIONALLY self-spotlights (~125 spotlighted plays/run —
  mostly her own cards). The companion-directed fantasy only exists at
  the depth-4+ ceiling. This is arguably the luck-gated slot working,
  but it means "Spotlight archetype" at median = self-Spotlight + salon
  glue. Red-pen worthy framing question (ask 2).

### C. Placeholder sweeps (defaults did not move)

**FANFARE_CAP_FRACTION** (fanfare deck): punisher 2.4% / **37.6%** /
63.0% and tank_boss 0.0% / **2.0%** / 8.0% at 0.25 / **0.50** / 0.75.
The cap is a first-order power dial. **User pick, ask 3.**

**SPOTLIGHT_SELF_MULT** (self_carry deck): punisher 2.6% / **38.0%** /
93.4% and tank_boss 0.0% / **2.0%** / 39.0% at 1.00 / **1.25** / 1.50.
At 1.5× (parity with companions) self-carry ≈ salon on punisher —
**criterion 1 borderline-fails; the reduced rate IS the load-bearing
anti-self-buff lever, empirically.** 1.25 holds it comfortably. Ask 3.

## 4. Incidents & world notes

- **Parallel-session schema conflict (needs ruling, ask 6):** a parallel
  M9 session added inline `upgrade:` fields to klee-cards.yaml rows
  mid-day; Card.from_dict hard-failed and the loader bricked for every
  session. Fixed with an IGNORED tolerance field (DECISIONS 67). The
  inline entries duplicate existing klee-upgrades.yaml deltas
  (sparkly_treasure/spark_collection, same +1 semantics). Two upgrade
  conventions now exist; reconcile by ruling. I did not touch their file
  and am not committing it.
- Klee's draft/reward world is UNCHANGED by this pass (personal-pool
  filter; bands and fragility locks green throughout).
- Winrate bands for Furina are deliberately NOT declared in her yaml —
  bands are ratified artifacts. Proposals: salon_weighted punisher
  [0.85, 0.97], tank_boss [0.50, 0.75], swarm/attrition floor 0.95.
  Spotlight/fanfare bands HELD BACK until the criterion-2 fix lands
  (banding a known-broken archetype would freeze the wrong world).

## 5. Honest gaps

- Spotlight deck's heavy-hitter floors are dire (punisher 2.5%,
  tank_boss 0.4%) — thin defense + dead machinery slots. Fix rides with
  ask 2.
- A5 3.1 vs 3.7 and A7 1.5 vs 2.0: short; levers exist (cantrip density,
  encore_cost easing, member timing) but were not spent this pass —
  each interacts with the A4/A2 corrections already made.
- Selector aiming v2 is still a heuristic (raw depth count, not value);
  her real aiming policy remains open scope.
- Amp-cap watch-items (bursting_grenades, neuvillette_judgment under
  1.5×): no amp_stack warnings observed; note the Spotlight multiplier
  scales printed numbers BEFORE the amp detector's base, so the detector
  wasn't exercised by it — by design (printed numbers), logged for
  awareness.
- Combat-coupled achievability used the committed strategy only;
  adaptive-drafter integration for her archetypes is tier05 milestone
  scope.

## 6. Asks (decision-ready)

1. **Sheet red-pen** — furina-cards.yaml + furina-upgrades.yaml (all
   numbers proposed; naming audit list included in sheet header).
2. **Criterion-2 ruling** — the delete-test fails: strengthen her
   Spotlight payoffs, or steer the archetype toward card-mediated
   boosting (Columbina shape)? Direction gates pass 2's card work.
3. **Knob picks** — FANFARE_CAP_FRACTION (sweep above; 0.5 default
   defensible), SPOTLIGHT_SELF_MULT (sweep argues 1.25 stands), hp 60,
   burst_max 70.
4. **A6 instrument ruling** — extend A6 with an application-uptime
   component (instrument change = ruling + re-anchor), or accept
   measured A6 ~3.6 with the documented gap.
5. **A2 deck-bands ratification** — proposed bands in §2; median A2 4.2
   vs declared ~3.0 accepted under the same reading as Klee's.
6. **Upgrade-convention reconciliation** — inline `upgrade:` fields vs
   *-upgrades.yaml sheets (DECISIONS 67); one convention must win.
7. **Registration (i) instrument** — approve a finer-grained coupled
   experiment at pass 2 (graded encounter set), keeping the EP
   registration open rather than force-closing it.
