# Tier 0.5 M8 — Report (m7-rulings execution: R1–R7)

**Date:** 2026-07-20. **Input:** m7-rulings.md (all rulings + directives).
**World stamps this report spans:** CONSTANTS_VERSION 2 throughout;
DRAFTER_VERSION 1→2 (R2, mid-report, always labeled); RUNTEMPLATE_VERSION
1→2 (R7, mid-report, always labeled); sheet v0.6 (Snap!, structured
reaction fields). 1000 runs/cell at seed 42 unless noted. 162 tests green
at each landing.

**Headline: both "uncomfortable finding" storylines resolved this
milestone — in opposite directions.** R6's matched-dose cell shows M7's
celebrated upgrade-scaling inversion was a dose artifact (the lore is
corrected before hardening). And the R2 drafter-model change shows the
assigned-vs-adaptive gap was never about the archetypes at all: with the
power term adopted, **assigned beats adaptive in all three archetypes**
— the first grid in the project's history where the committed plan wins
naturally.

---

## 1. R6 — matched-dose verification: M7's inversion was a dose artifact ✗→✓

The clean cell the ruling ordered: each policy upgrades its own first-N
eligible picks (assigned/hybrid: on-plan; adaptive: its goodstuff picks),
N swept, realized dose reported. Current-world basis as directed
(drafter v1, template v1, pre-Snap). One basis caveat the review pass
caught: R4's derived-tag migration (albedo/oz gain the reaction tag)
had already landed, so the reaction cells are not bit-identical to
M7's dose-cell world — demolition/spark replay M7's assigned numbers
exactly (47.4/58.2 at N=8), reaction differs by 0.4 (40.5 vs 40.9).
Nothing in the verdict turns on it.

| N | demolition asgn/adpt (dose) | spark | reaction |
|---|---|---|---|
| 2 | 39.0 / 44.2 (1.98/2.00) | 39.7 / 45.5 | 22.4 / 40.1 |
| 4 | 43.9 / 55.9 (3.72/3.99) | 52.0 / 57.3 | 33.8 / 50.4 |
| 8 | 47.4 / 68.9 (5.11/7.73) | 58.2 / 69.9 | 40.5 / 64.1 |

- **At genuinely matched dose (N=2), the inversion is gone**: adaptive
  leads by +5.2/+5.8/+17.7 — right at the natural-world gaps. M7 §6's
  "committed drafting beats goodstuff by 13–17 under scaling" does not
  survive; what M7 measured was assigned receiving more free upgrades.
- The mechanism is visible in the dose columns: at N=8 assigned can only
  absorb 5.1–5.9 upgrades (it runs out of on-plan upgradable picks)
  while adaptive absorbs 7.7 — and the gap widens with the asymmetry,
  which is exactly the shape of M7's uncapped on-plan cell.
- Upgrades DO scale hard for everyone (+14 pts for assigned-demolition
  at dose 2 vs natural): the truncated-scaling *mechanism* is real; the
  *differential* claim was the artifact. §7's decomposition survives per
  the ruling (it rests on the threshold + scorer findings, not this).
- Footnote: per-dose efficiency at N=2 puts hybrid first everywhere
  (48.5/50.6/49.6) — consistent with R2's outcome below.

## 2. R1 — Snap! lands; the margin-supply fix delivers; validation gate says the widening is honest

**Content fix (shipped verbatim; one notation flag).** Snap! is in sheet
v0.6 with the ruled row. The upgrade entry landed as `{damage: +3}`
(5→8): the ruling wrote `{damage: 8}` but names it "standard
common-attack +3", and the grammar authority treats values as deltas —
flagging the discrepancy here rather than silently applying +8.

**Re-measure, both drafter models, labeled:**

| spark cell | v1 no-Snap (M7) | v1 + Snap | v2 + Snap |
|---|---|---|---|
| online rate | 43.4% | 52.0% | 54.5% |
| common on-plan offers/screen | 0.269 | 0.314 | 0.314 |
| assigned winrate | 26.9% | 24.3% | **35.7%** |

- Supply moved more than predicted (~0.29 expected, 0.314 measured);
  snap shows up 0.045/screen and gets drafted in 25–28% of runs.
- The division of labor is clean: **Snap! bought achievability (+8.6
  online), the R2 power term converted it into wins (+11.4)**. Under the
  power-blind drafter the extra supply became deck composition, not
  winrate — worth knowing before crediting either change alone.
- P(≥4 on-plan) = online rate still, by definition; the margin now
  clears in 54.5% of runs. **Crackle stays in reserve** — the margin
  still binds in ~45% of runs, but the ruling's one-variable-at-a-time
  window means that call comes after this report is digested.

**Validation gate (independent, measured pre-change, 4000 natural
assigned-spark runs):**

| final-deck group | n | winrate | died <5 screens |
|---|---|---|---|
| ≥4 on-plan (online) | 1842 | 29.4% | 0.7% |
| ==3 on-plan + engine | 402 | **32.6%** | 8.0% |
| ==3 on-plan, no engine | 562 | 29.4% | 7.5% |
| ≤2 on-plan | 1194 | 21.9% | 29.3% |

Engine+3 performs at (slightly above) online rates, so **the any-engine
widening passes the ruled gate** — ratification is yours. Honesty
caveats: deck composition is endogenous (early deaths stop drafting —
visible in the died-early column, which means the 3-on-plan groups clear
the bar while carrying a survivorship handicap, strengthening the
result); and the no-engine control ALSO matches online winrate, so the
gate arguably indicts the ≥4 line itself, not just its engine
blindness. Both readings reported; neither acted on.

## 3. R2 — DRAFTER_VERSION 2: the gap inverts; reaction's conviction is explained

**R2.1 (power term).** score_offer adopts the hybrid experiment's
raw-power term (share-synergy stays out, as ruled); hybrid_policy is now
an alias of assigned_policy — the diagnostic graduated. The generic
anchor's private power line dissolved into the universal term.

**R2.2 (reaction weights sweep, 1000 runs/cell).** The twice-convicted
reaction scorer was guilty of exactly one thing: power blindness.

| variant | winrate | avg deck |
|---|---|---|
| power term only | 34.4% | 18.7 |
| + lean line (cap 13 × 0.4) | **36.3%** | 18.0 |
| + applier 4.5 | 33.4% | 18.6 |
| + amp offline 2.5 | 33.4% | 18.6 |
| + all three | 33.5% | 17.9 |
| lean strong (× 0.8) | 34.0% | 16.6 |

The power term alone took assigned-reaction 10.7% → 34.4% (past
adaptive). Raising applier/amp valuations — the tuning pass everyone
expected — measures WORSE. The one keeper is the lean-deck line (§3's
density finding as scorer behavior; the skip threshold stays one global
constant, no namespace fork). ×0.8 overshoots into 16.6-card decks.

**The v2 grid (template v1, natural world — the new baseline):**

| target | assigned v1 (M7) | assigned v2 | adaptive | gap now |
|---|---|---|---|---|
| demolition | 25.0% | **37.6%** | 28.0% | asgn +9.6 |
| spark | 26.9% | **35.7%** | 30.3% | asgn +5.4 |
| reaction | 10.7% | **36.3%** | 24.2% | asgn +12.1 |

All relevance floors clear (43–47% assigned), no divergence alarms
(reaction 37–38% dominant share, goodstuff 5.6–7.4%), online rates
demolition 92.9 / spark 54.5 / reaction 77.5, TTOs 4/7/5 (spark at the
alarm line, not over). Assigned draft-regret dropped ~5× (56–73 vs
adaptive's 227–394): the power-aware committed drafter is also the
self-consistent one. **The M6-era "assigned loses to no plan at all"
storyline ends here** — it was deck volume (fixed, CONSTANTS v2) plus
power blindness (fixed, DRAFTER v2), never the archetype designs.
Adaptive remains in the harness as the divergence instrument, which is
what it was always for.

## 4. R3 — loose relevance: unchanged by ruling

Reported as measured, still collapsed onto strict (engaging ≈ relevance
in every v2 cell above, same subsumption as M7 §2). Parked per R3.

## 5. R4 — structured fields landed; barbara audit is a real finding

- `albedo_solar_isotoma` carries `consumes_aura: true` and `fischl_oz`
  carries `summon_element: electro` (pinned by test to the engine's
  literal); `_is_reaction_fuel` derives from the structured fields — the
  two prose-only "deliberate misses" are now honestly tagged. No
  hand-tags survived the migration (there were none to survive: all
  companion reaction tags remain derived).
- Effect: both now count as reaction fuel in shares/scoring — folded
  into the DRAFTER_VERSION 2 measurement window above, noted here so no
  one attributes their small share shift to the drafter change alone.
- **barbara_shining_idol audit (measurement only, no sheet edit):** one
  non-exhausting idol in a starter deck is played **4.5×/fight in
  attrition, delivering mean 24 HP/fight (max 44)**; two copies reach
  37.5 HP/fight. The v0.3.1 errata's "played once each ≈ 6 HP" premise
  does not hold in long fights. As an uncommon, repeatable, true heal it
  sits outside the v1.5 healing-grade law (rare-tier or Exhausts).
  Options for chat: Exhaust (melody-consistent), rare-tier it, or route
  through a buffer pool. Not shipped — this phase is not balance changes.

## 6. R5 — C3 obligation

Logged in the C3 sweep list (kit-Burst grant behavior in C#). No action
this milestone, per ruling.

## 7. R7 — run-template recalibration (RUNTEMPLATE_VERSION 2)

**The stamped world.** `RUN_NODE_TEMPLATE = "NNNENRNNENRNRB"`: 3 rests
with the pre-boss campfire GUARANTEED (your numbers: 1 guaranteed + 1–2
pathed; shopless single-act proxy = 2 elites + 3 rests ≈ 5 cool nodes).
Fight count (11) and screen count (10) deliberately unchanged from v1,
so the change is purely rest economy. v1 grids (all reports through §3
above) are the archive.

**Directive 2 — the 2D sweep** (assigned-demolition, 1000 runs/cell;
attrition = attack scaling on plain normals only):

| rests | attr | winrate | smiths/run | arrival HP | under danger |
|---|---|---|---|---|---|
| 2 (v1) | 1.0 | 37.6% | 0.08 | 18.5% | 94.9% |
| 2 | 0.7 | 65.8% | 0.51 | 28.6% | 73.4% |
| **3 (v2)** | **1.0** | **59.1%** | **0.24** | 22.8% | 88.6% |
| 3 | 0.7 | 85.0% | 0.95 | 32.3% | 66.4% |
| 4 | 1.0 | 53.5% | 0.94 | 29.9% | 67.4% |
| 4 | 0.7 | 82.3% | 1.83 | 37.0% | 51.4% |

- The guaranteed pre-boss campfire alone is worth ~+21 winrate points
  (37.6 → 59.1) — mostly as boss-prep healing, which is a template-v1
  indictment all by itself: v1 sent runs into the boss off a fight.
- **The 95%-under-danger finding is confirmed as substantially an
  attrition artifact**: at 0.7× normal damage it falls to 66–73%.
- **Registered prediction 2 ("attrition is the stronger knob") —
  PARTLY confirmed, with a cleaner split than predicted:** attrition is
  the stronger *rate* knob (it moves arrival HP and the healthy-rest
  share), density the *count* knob (more chances at a similar rate).
  Per-rest smith yield: attr 0.7 at 2 rests = 0.26/rest vs 4 rests at
  1.0 = 0.24/rest — nearly interchangeable at the margin.
- Honesty note: the exploratory 4-rest template accidentally carries a
  12th fight (one extra N), so its rows are mildly confounded (more
  attrition AND one more draft screen). The stamped 3-rest template is
  exact; the 4-rest rows are directional only.
- Review-pass correction, validated by re-run: the attrition knob
  originally scaled `amount` but not `ramp` (punisher_lite, ⅓ of
  normals), understating the labeled 0.7× on late turns. Fixed to the
  sibling-scaler convention and the whole grid re-swept (post-R8 pool):
  **every cell reproduces within noise** (e.g. 37.9 vs 37.6, 84.7 vs
  85.0) — because punisher_lite's ramp is 1 and integer rounding keeps
  it at 1 under any scale, the defect was real in convention but nil in
  effect at current statlines. Knob verdicts stand on the current world.

**Directive 3 — re-measure under the calibrated economy** (drafter v2,
template v2 — the new standing baseline):

| target | assigned | adaptive | smiths/run (asgn) | ≥1 upgrade |
|---|---|---|---|---|
| demolition | 59.1% | 52.9% | 0.24 | 22.5% |
| spark | 56.9% | 54.1% | 0.28 | 25.5% |
| reaction | 60.4% | 46.7% | 0.27 | 24.5% |

Assigned's lead survives the environment change (+6.2/+2.8/+13.7).
Natural smith uptake rises 4× from M7's 0.06 to 0.24–0.28/run — the
run template was indeed starving it, as ruled.

**The upgrade-TIMING distribution is the sharpest finding of the
milestone:** ~68% of natural smiths land on node 12 — the guaranteed
pre-boss campfire (demolition: 167 of 244; node 5 takes most of the
rest; node 10, where runs arrive bruised, almost none). Natural
upgrades arrive one fight before the boss and scale exactly one
encounter. The dose-controlled cells deliver upgrades on-draft; real
smithing delivers them at the door of the final fight.

**Directive 4 — the residual** (matched-dose cells re-run in THIS
world, assigned, own on-plan picks):

| target | natural | dose 2 (on-draft) | dose 4 | residual at dose 2 |
|---|---|---|---|---|
| demolition | 59.1% | 70.0% | 72.3% | **−10.9** |
| spark | 56.9% | 70.0% | 78.0% | **−13.1** |
| reaction | 60.4% | 74.8% | 79.8% | **−14.4** |

**This 11–14 points — not M7's — is the true size of the design-layer
upgrade-access gap**, and per the ruling the parked content options
(post-elite upgrade rewards, cheaper smithing, smith+heal, Talent
Training) compete to fill only this. **Registered prediction 1 —
CONFIRMED**: uptake rose substantially (4×) and remains far below
dose-controlled benefit, and timing is the reason, measured directly
above. The timing distribution is itself a design argument: more
campfires mostly add pre-boss smiths; access that lands MID-RUN
(post-elite rewards are the StS1-shaped candidate) attacks the residual
where it lives.

---

## 8. R8 — healing-policy tightening (mid-sprint amendment): landed

**The law** (conjunctive: true in-combat healing is Rare-tier AND
Exhausts; below Rare, sustain routes through Block or buffer pools; no
4-star companion may true-heal) is now **enforced by test over the whole
sheet** — `test_healing_law_is_conjunctive` fails the next heal that
lands anywhere below Rare-and-Exhausts, so future cards answer to the
law rather than to a review. The three ruled conversions landed verbatim
(melody → block 4 + meter 4; shining_idol → block 5 + aura + cantrip;
fantastic_voyage → block 4 + courage, Exhaust removed). This resolves
§5's shining_idol audit by conversion, as ruled.

**Consequential edits under your red pen:**
- Upgrade deltas for the three converted cards re-pointed at their new
  numbers (melody/idol `{block: +2}`; voyage keeps `{buff: +1}`) —
  proposed designs, modest-single-bump guardrail respected.
- The v0.3.1 errata test (asserted heals Exhaust) is superseded and was
  rewritten as the law test above plus a conversion pin.

**A4 instrumentation (directive executed; NUMBERS ARE DISCONTINUOUS BY
DESIGN).** The barbara_injection probe died with its heals. Replacement
instrument: the anchor's exempt relic trickle (`heal_after_won_fight`,
Burning Blood — the same hook anchoring ref_ironclad's A4 baseline at
3.0), injected probe-only via a new `package_relic_hooks` mechanism
(never on starter, never in Tier 0.5 runs, leak-guarded by test). The
probe (`sustain_probe`, same 12-card deck) reads raw ~6 healing/fight vs
the old card-based ~10–12: **A4 numbers do not continue across R8.**
Klee solo A4 = 0.5 re-derived under the new world (still the floor — now
ecosystem-wide by law, not merely by draft). DECISIONS entry 60.

**Tier 0 exposure:** none of the weighted/watchlist decks contain the
converted cards (only the probe did), so the ratified winrate bands and
the snapshot-locked scorecard are structurally untouched — confirmed by
the full suite at 1000-fight regression locks (163 green).

**Tier 0.5 grid under the post-R8 pool** (drafter v2, template v2 — the
standing baseline, re-stamped because companion valuations changed):

| target | assigned | adaptive | vs pre-R8 (asgn/adpt) |
|---|---|---|---|
| demolition | 59.1% | 45.8% | ±0.0 / −7.1 |
| spark | 57.1% | 45.8% | +0.2 / −8.3 |
| reaction | 49.0% | 39.9% | **−11.4** / −6.8 |

Assigned's lead holds everywhere (+13.3/+11.3/+9.1); all floors clear;
no divergence alarms (reaction 38.6–40.6% dominant, goodstuff 7.7–9.5%).
**The across-the-board winrate drop is the law working, priced:** the
converted heals were RUN-level sustain (HP persists across fights;
Block evaporates end of turn), and the archetypes that draft buffers
and grind long fights paid most — reaction assigned −11.4. This is
real difficulty added to the run economy, not noise. If the drop reads
as too steep, the law-compliant levers are rest economy or a designed
5-star Rare healer (Qiqi-shaped — the corollary's native slot), not
softening the law.

---

## Asks

1. **R1 validation gate — ratify or note (§2):** engine+3 clears the
   gate (32.6% vs online's 29.4%, carrying an early-death handicap).
   Ratify the any-engine widening — or note that the 3-no-engine control
   ALSO matching online winrate reads as the ≥4 line being one card
   strict in general, which is a different (bigger) definitional call.
2. **Crackle reserve (§2):** the margin still binds in ~45% of runs
   post-Snap. Next window: authorize `crackle: + gain_spark 1`, or hold.
3. **Upgrade access, now unparked with a number (§7):** the residual is
   11–14 pts and the timing distribution says mid-run access beats more
   campfires. Pick the content lever (post-elite upgrade reward is the
   evidence-shaped one); it re-enters as designed content, not a sim fix.
4. **Snap upgrade notation (§2):** landed as `{damage: +3}` per the
   grammar and your own "+3" gloss; confirm, or correct me to literal +8.
5. **barbara_shining_idol (§5):** 24 HP/fight from one non-exhausting
   copy breaks the healing law's premise. Exhaust / rare-tier / buffer
   pool — your call; nothing shipped.
6. **Divergence watch, informational:** adaptive-reaction dropped to
   46.7% under the calibrated economy while assigned hit 60.4 — the
   instrument still shows no alarms, and adaptive's numbers moved with
   the pool changes (Snap + derived tags), all labeled in §3.
7. **R8 aftermath (§8):** removing pool sustain cost 7–11 winrate pts
   (reaction assigned worst). Accept as the law's price, or authorize
   the 5-star Rare healer design (Qiqi-shaped — the corollary's native
   slot) to restore premium sustain through the front door? The upgrade
   deltas for the three conversions also await your red pen.

## Not in this milestone

Slot modes beyond pity, signature-companion event, dream-team stats,
Wish-banner economy, relic modeling beyond the compensator, multi-act
structure. Talent Training stays v2. Tier 0 bands unaffected (no engine
or statline changes; the battery world is untouched by R2/R7, which are
draft- and run-layer only).
