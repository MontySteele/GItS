# M7 Rulings & Directives (chat → Code)

**Date:** 2026-07-20. **Input:** tier05-m7-report.md (all sections + asks), user
ruling on real-game campfire economy (§R7, verbatim). Principles v1.9,
CONSTANTS_VERSION 2 baseline.

**Headline rulings:** the assigned-vs-adaptive evidence embargo is lifted and
closed — the gap decomposed into threshold + truncated scaling + reaction
scorer, none of which is "archetypes are weak," and nothing may cite the old
gap for buffs/nerfs because there is no gap left to cite. Demolition 95.7 did
not re-break 97; the Burst-energy-gain conversation stays sealed. Klee v1 is
numerically validated pending playtest. The work below is verification,
calibration, and instrument improvement — not balance changes.

---

## R1 — Spark margin supply (report §5, ask 1): content fix first, definition fix only if earned

The decomposition's finding stands as measured: 81% of never-online runs are
1–2 on-plan cards short; engines convert at 87% when offered and are not the
bottleneck; supply is 0.46 on-plan offers/screen.

- **Ruled: the primary fix is content — designed and signed off. Sheet delta
  ships with this doc, verbatim:**

  ```yaml
  # Spark (10) — v0.6 addition per M7 §5 ruling R1 (margin-supply content fix)
  - {id: snap, name: "Snap!", cost: 1, type: attack, rarity: common, solve: [frontload, velocity], archetypes: [spark], role: enabler,
     effects: [{op: damage, amount: 5, target: enemy}, {op: gain_spark, amount: 1}]}
  ```

  Upgrade sheet entry: `snap: {damage: 8}` (standard common-attack +3; Spark
  rider untouched so the upgrade doesn't move the resource curve).

  Design rationale (for the record): spark had **no common attack that
  generates Sparks** — every common Spark-gain is a skill, and the first
  spark-gaining attack in the pool was Da-da-da! at rare. A spark drafter at
  3-on-plan facing an attack-heavy reward screen had nothing on-plan to take.
  Pricing comp: Fish-Flavored Bait with the rider swapped (Bomb → Spark,
  both ≈⅓ energy of value). Single-tag spark, targeted for drafter
  reliability, catalyst cadence applies Pyro as normal — reaction-neutral,
  no cross-archetype warp.

  **Re-measure directive:** after the delta lands (and once R2's drafter
  model is stamped — run under both models if convenient, labeled), re-run
  the spark grid under v2 constants: watch P(≥4 on-plan drafted), the 43.4%
  online rate, and on-plan offers/screen (expect ~0.27 → ~0.29 at common;
  ~half an extra sighting per run — modest by construction).

- **Held in reserve, NOT authorized yet: Crackle buff.** Crackle (0-cost, 3
  random damage, no Spark) is under-statted and the power-aware drafter will
  correctly skip it. If the Snap! re-measure still shows the margin binding,
  the next lever is `crackle: + gain_spark 1` — improving conversion of
  existing supply rather than further diluting screens. One variable at a
  time: do not ship both in the same measurement window, or the result can't
  attribute the fix.
- **The any-engine core-widening is a definitional change and is NOT
  authorized yet.** Validation gate: measure winrate of decks at exactly
  3-on-plan + any engine vs decks at ≥4-on-plan (the current online
  definition). If engine+3 performs at online-like rates, the widening is
  honest — report and we'll ratify. If not, the current definition was
  correct and stands.
- Do not sequence the validation gate behind the content fix; they're
  independent measurements.

## R2 — Drafter model: adopt the power term into assigned mode; reaction weights pass authorized

Hybrid beat both parents in all three archetypes (report §4), and reaction's
scorer is convicted twice independently (§4 residual +15.5; §6 gap persisting
under dose-control). Ruled:

1. **Assigned mode adopts hybrid's raw-power term as the standard drafter
   model.** A plan-committed drafter with zero power awareness is an
   implausible human; the acceptance law requires plausible drafts. Share
   synergy stays excluded, as the hybrid already does.
2. **Reaction scorer weights pass authorized** — applier/amp valuation, AND
   fold in §3's finding that reaction uniquely prefers lean decks (its
   drafter should be willing to skip harder than the global 0.5 threshold;
   whether that's a per-archetype threshold or a scorer behavior is Code's
   call — pick the one that doesn't fork the constants namespace).
3. **This is a model change.** New version stamp (DRAFTER_VERSION or
   equivalent), archive all pre-change snapshots, never overwrite. Post-change
   numbers are not comparable to M7's without saying so — same discipline as
   CONSTANTS_VERSION.

## R3 — Loose relevance (report §2, ask 4): report-as-measured stands

Keep reporting the collapsed two-clause secondary as measured; the re-spec of
"worth engaging" as a policy-facing question is parked. Nothing enforced
hinges on it, and the hybrid/assigned-with-power drafter already embodies
"would a competent drafter engage." Revisit only if a future ruling needs the
60–75-band construct.

## R4 — Sheet asks (ask 5): approved as routine

- barbara_shining_idol exhaust-policy audit: proceed.
- Structured fields: albedo_solar_isotoma `consumes_aura`, fischl_oz element
  on summon effects — proceed; derived reaction tags must come from the
  structured fields once they exist (no hand-tags surviving that migration).

## R5 — C3 obligation (ask 6): logged

Kit-Burst grant behavior (granted-on-charge, not draftable; Retain; re-grant
on refill; returns to kit on cast) is owed in C# and joins the C3 sweep list.
No further action this milestone.

## R6 — NEW: matched-dose verification cell before explanation 3 becomes lore

§6's dose-controlled test pre-upgrades **on-plan picks only**. Adaptive drafts
fewer on-plan cards by construction, so the two policies received different
upgrade doses — the inversion could be partly "assigned got more free
upgrades." Same error-class as the M6 starter-deck confound: an artifact
wearing a finding's clothes.

**Directive:** run the clean cell — **matched upgrade count, each policy
upgrading its own top-N drafted cards** (adaptive upgrades its goodstuff
picks; assigned upgrades on-plan; N identical, swept if cheap). 1000
runs/cell, v2 constants, current drafter model (run before R2's model change
lands, or run under both and say which is which).

- If assigned still wins: explanation 3 is airtight; quote it freely.
- If the inversion shrinks or vanishes: the truncated-scaling story is
  partly dose artifact — report the split; the embargo-closure rulings above
  are unaffected (they rest on §7's decomposition, not on the inversion's
  magnitude), but the lore gets corrected before it hardens.

## R7 — Run-template recalibration: real StS2 node economy (ask 3 superseded)

**User ruling on the real game, verbatim:**

> You are given one campfire before the end-of-act boss, and typical pathing
> through an act will give 1 to 3 additional campfires. I'd roughly guess
> that an act's busiest path averages 7 'cool things' between Shops, Elites
> and campfires, including the guaranteed campfire at the end.

The template's 2 rest nodes per run vs a real economy of 2–4 campfires per
act (≈6–12 per three-act run) means M7's natural-uptake finding (0.06
smiths/run) measured a world with ~3–6× less upgrade access than reality.
**All mod-content options for upgrade access — post-elite upgrade rewards,
cheaper smithing, smith+heal hybrids, Talent Training — are PARKED** until
the calibrated re-measure reports. We do not design content to fix a
simulator artifact.

**Directives:**

1. Recalibrate the run-template node economy to the numbers above, scaled to
   whatever run-length the template models (if it's a single-act proxy: 1
   guaranteed campfire + 1–2 pathed, ~7 shop/elite/campfire nodes on the
   busy path). Implementation shape is Code's call; the user's numbers are
   the spec.
2. Audit HP attrition alongside count: 95% of rest arrivals under the 40%
   danger line is suspicious as a template artifact. Sweep attrition (or
   pre-rest heal pacing) jointly with rest density — a 2D sweep, modest
   grid, so we can see which knob moves smith uptake.
3. Re-measure under calibrated economy: natural smith uptake, archetype
   winrates (assigned/adaptive/hybrid), and **upgrade-timing distribution**
   (when in the run upgrades actually land — the dose-controlled test
   delivered them on-draft; real smithing arrives late, and late scaling may
   miss the fights that need it).
4. Report the residual: how far natural uptake under real economy falls
   short of the dose-controlled scaling benefit. That residual — not M7's —
   is the true size of any design-layer gap, and the parked content options
   compete to fill only that.
5. This is an environment change: version stamp (RUNTEMPLATE_VERSION or fold
   into CONSTANTS_VERSION 3), archive pre-change snapshots, never overwrite.

**Registered predictions** (for calibration honesty, not as directives):
smith uptake rises substantially but remains below dose-controlled benefit
because timing is late; attrition proves to be the stronger knob of the two.
Null or contrary results are binding and get documented per house rules.

## Sequencing note

R6 (matched-dose cell) and R7 (recalibration) both touch the upgrade story;
run R6 first under the current template so the confound check isn't itself
confounded by the environment change. R1's validation gate and R2's model
change are independent and may interleave as convenient. Report format as
M7: decision-ready, knob trails, decompositions.

## Chat-side queue (ours, not Code's — for the record)

1. ~~Spark common-tier enabler design session~~ — done; Snap! ships in R1
   above (Crackle buff held in reserve pending re-measure).
2. Furina kickoff doc (statline, Spotlight/Fanfare/Encore rulings to date,
   Fontaine 4-star set scoping) — in progress this thread.
3. Playtest debrief when the user's Klee run completes; RunHistory telemetry
   as usual.
