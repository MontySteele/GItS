# Furina Sheet Pass 4 — Plan (pre-registered)

> **Lifecycle: ARCHIVED** — superseded; kept verbatim as a record and never updated. Status index: `docs/registry/identifiers.md` §15.

**Date:** 2026-07-24. **Source:** the 2026-07-24 playtest workshop queue
(Q1/Q2/Q3, USER-ratified directions marked there). **Governing:** kickoff
v0.1 (§4 amendment proposed in Q2), principles v1.6+ (Regent-star Encore /
capped Fanfare), `furina-salon-rework-plan.md` (Salon v2 — every cell runs
in that world), sheet-pass-1..3 reports.
**Environment stamps at registration:** CONSTANTS_VERSION 2,
DRAFTER_VERSION 7, RUNTEMPLATE_VERSION 5, SPOTLIGHT_SELECTOR_VERSION 5.
Fanfare constants at registration: `FANFARE_CAP_FRACTION 0.5`,
`FANFARE_PER_HP_LOST 1`, `FANFARE_PER_ENCORE_GAINED 1`,
`FANFARE_PER_ENCORE_SPENT 1`, `FANFARE_PER_SPOTLIGHT_CARD 2`,
`SALON_FOCUS_PER 10`.
**Seed:** 20260724 throughout; deterministic.
Registered BEFORE running. **Null results binding.** Every number below is
PROPOSED; nothing here is a balance change until red-penned.

**Sequencing law (from the queue, recorded so it survives the session):**
Q1's telemetry lands and Q1 is READ before Q2's cells are interpreted.
Rationale: the playtest finding ("Fanfare is basically always maxed unless
you've got a payoff card") says we are measuring in a saturated-Fanfare
world, and card valuations taken in that world may not survive a flux fix.
Q3 is independent of both and may land in parallel.

**Legibility items are NOT in this pass** — they shipped sim-silent under
`docs/furina-legibility-sprint-log.md`.

---

## Q1 — Fanfare saturation (diagnosis + remedy sweep)

**USER PLAYTEST FINDING (2026-07-24, verbatim):** "Fanfare is basically
always maxed unless you've got a payoff card."

Design stakes: Salon v2 makes Fanfare the Focus analogue
(`SALON_FOCUS_PER` member scaling). A pinned-at-cap Fanfare collapses that
scaling into a flat bonus and the kickoff's drain→refill→spend flux
identity into a binary. Mechanic-identity question, not a tuning nit.

### Q1a — telemetry (precondition for everything below and for Q2)

Instrumentation only; no constant moves. Registered metric definitions, so
later cells cannot redefine them mid-pass:

- **time-at-cap** = fraction of PLAYER TURNS whose start-of-turn snapshot
  has `fanfare == fanfare_cap`. Snapshot is emitted after turn-start
  triggers, upkeep and draw, i.e. the state the pilot actually decides in.
- **overflow-waste** = `sum(wasted) / sum(requested)` over all
  `gain_fanfare` calls in the combat, where `wasted = requested − applied`.
  This is generation thrown away at the cap. Before this pass the clamp was
  silent — `gain_fanfare` emitted only the applied amount — which is the
  mechanical reason no earlier sweep could see saturation.
- **spend events / amount** = count and total of `fanfare_spent`.
- **peak / mean held** = max and mean of the per-turn snapshots.

Reported per archetype weighting. Primary read: `fanfare_weighted`.
`salon_weighted` is a co-primary this pass (member scaling reads the meter);
`spotlight_weighted` and `self_carry` are reported as context.

### Q1b — baseline (current constants, no changes)

Establishes time-at-cap and overflow-waste in the shipping world.
**Registered divergence clause:** if baseline saturation is LOW in sim but
was high in playtest, that divergence is itself the finding (sim decks
under-generate versus human piloting) and it goes to [USER] before any
remedy cell is trusted. No remedy is adopted off a sim that disagrees with
the eyes.

### Q1c — remedy cells (one variable each, house norm)

1. **Spend-outlet expansion** — extend the `fanfare_cost` grammar (today
   ~`universal_revelry` 20, `dramatic_entrance` 5, `thunderous_ovation` 5)
   to 2–3 further cards as costed upside. Candidate slots are proposed at
   the point of running, listed in the report, not pre-chosen here.
2. **Generation trim** — flat percentage haircut on fanfare-per-flux-event
   (constant, not per-card surgery).
3. **Cap raise** — `FANFARE_CAP_FRACTION` up-sweep: accept saturation as a
   late-game state but move the ceiling so payoffs and member scaling keep
   a gradient longer.

### Q1d — read

Time-at-cap in a healthy band — **PROPOSED: 20–50% of turns in
fanfare-weighted decks by act 3** (the BAND ITSELF wants red-pen) — with
the A4/A6 statline held. The winning remedy becomes Q2's "fixed world" arm.

---

## Q2 — `the_sea_is_my_stage` reprice (+ kickoff §4 amendment)

**USER DIRECTIVE (2026-07-24):** true HP damage on a character with no
healing is too high a price for this rare; 6 Encore might be fair, 6 HP is
too much. Ecosystem anchor supplied: a strong Silent power (2-cost,
upgrades to 1; all Weak enemies take 50% more damage; copies stack
additively) was recently NERFED from 100% — and it is immediately live and
self-enabled, where +15 Fanfare cap is doubly conditional (needs
above-cap generation AND drafted payoffs that read Fanfare). General
direction ratified: the process has been over-pricing scaling effects
against degenerate ceilings rather than median drafts (precedent: the v2
energy reprice, rare avg 1.93→1.43; the Frozen episode is the logged
lesson — sims check our math, players check our fit).

Recorded for the file: the pass-1 red-pen flag-3 rationale ("self-damage
that feeds Fanfare self-subsidizes, so cut deeper") priced the refund,
never the effect. The Encore-cost variant keeps a real setup cost in a
house resource, uses the existing "Spend N Encore:" grammar, and is
flux-positive by design.

**Q2a — variant matrix.** All cells run in BOTH the current-constants world
and Q1's winning-remedy world; the ruling is made on the fixed world, the
current world is the control.

| variant | cost line |
|---|---|
| V0 (current) | 1 energy, 6 self-damage (10% maxHP) |
| V1 | 1 energy, 3 self-damage |
| V2 | 1 energy, no rider |
| V3 (user proposal) | 1 energy, Spend 6 Encore |

**Q2b — metrics.** Drafter pick rate; win-rate delta CONDITIONAL on
fanfare-payoff count in deck (an uncapper's value flows through payoff
density — an unconditioned average will wash it out); HP trajectory
(V0/V1); Encore trajectory + dead-hand incidence (V3 — a spend-gated rare
must not recreate the "no Encore, card doesn't work" failure Q3 exists to
fix); time-at-cap shift (does the uncapper restore a gradient, or is +15
immediately re-saturated — if the latter, the card is weaker than every
variant prices it).

**Q2c — kickoff §4 amendment (PROPOSED text, pending [USER] ratification,
required for V2/V3):** "Rare uncappers carry a setup cost" → "Rare
uncappers carry a setup cost in a house resource, priced at ecosystem
parity; true-HP costs require a specific degeneracy finding, not category
membership." Logged beside the Frozen lesson in principles.

**Q2d — SUPPORT_CARRY / degeneracy re-check** on the winning variant: the
uncapper plus Q1's spend-outlet world is a new combined economy; check the
spend loops cannot self-sustain (standing Encore-loop audit language).

---

## Q3 — Innate-on-upgrade Encore card (dead-hand fix)

**USER DIRECTIVE (2026-07-24):** one Encore card should upgrade to Innate,
to solve "I have no Encore, so half my cards don't work."

**Q3a — engine check first.** Does the upgrade pipeline support granting
Innate? (`furina-upgrades.yaml` has no precedent; Klee's
`sparks_n_splash` innate-on-charge is grant-to-hand machinery, not an
upgrade flag.) If unsupported, the engine work is a small pre-item with its
own DECISIONS entry.

**Q3b — candidate:** `aria_of_recompense` (basic, gain 5 Encore). Basics
are guaranteed in every deck, so Innate-on-upgrade here makes the fix a
campfire decision available in every run rather than a draft lottery —
the shape of the complaint. Common-tier alternates (`curtain_up`) accepted
at the point of running if the basic reads as too automatic an upgrade.

**Q3c — A1 statline check (the honest cost of this fix).** A1 is DECLARED
dreadful (1.0–1.5). Guaranteed turn-1 Encore-on-demand after one campfire
is exactly the quiet A1 repair that declaration exists to catch. Measure A1
with and without the upgrade taken; if it moves, the result goes to [USER]
as a statline amendment decision ("dreadful but campfire-fixable" may well
be the intended identity — but it gets decided, not drifted into).

**Q3d — upgrade-priority interaction.** Campfire economy is 1 guaranteed +
1–3 fires per act. If this upgrade dominates the first fire in sim pilot
logic, note it — a mandatory first upgrade is a tax wearing a fix's
clothes, and the base card may want its numbers shaved in trade.

---

## Explicitly out of scope for pass 4

- Anything the legibility sprint owns (text, tooltips, gauges, previews).
- The general card-pool quirk sweep flagged as "after legibility" — that is
  pass-5 material, once players can read the pool they are evaluating.

---

## Execution log

_(appended as blocks land; every cell records its seed and version stamps)_

### Q1a — telemetry LANDED (2026-07-24)

Instrumentation only; no constant moved, no sheet touched.

- `tier0/engine/resources.py` — `gain_fanfare` now emits `requested` and
  `wasted` alongside `amount`. **The clamp used to be silent**: only what
  landed was emitted, so generation thrown away at the cap left no trace at
  all. That is the mechanical reason no earlier `FANFARE_CAP_FRACTION` sweep
  could see saturation — those cells read win rate, and a pool pinned at its
  ceiling is invisible in win rate.
- `tier0/engine/combat.py` — one `fanfare_turn` snapshot per player turn,
  taken after turn-start triggers, Salon upkeep, energy and draw, i.e. the
  state the pilot decides in. Gated on `fanfare_cap`, so non-Fanfare rosters
  pay nothing.
- `tier05/fanfare_telemetry.py` — the registered metrics, pooled by
  numerator/denominator rather than by averaging per-combat ratios (a
  2-turn combat must not weigh as much as a 20-turn one).
- `tier05/model.py` — `RunResult.fanfare_traces`: `(act_index, trace)` per
  fight, so the "by act 3" read is answerable. Full suite 648 green.

### Q1b — baseline READ (2026-07-24, seed 20260724, 200 runs/arm)

Assigned-archetype runs, `grant_relics`/`grant_potions` on. Note on arms:
in RUN mode the archetype weighting IS the assigned archetype (the deck is
drafted toward it), so a fixed "self_carry" package label would have been
inert — it was dropped rather than reported as a duplicate arm.

| arm | run wr | act | at-cap | overflow | held | peak | spends/combat | n |
|---|---|---|---|---|---|---|---|---|
| fanfare | 0.0% | all | 12.7% | 20.7% | 35.3% | 71.1% | 1.1 (8.9) | 1739 |
| | | 1 | 11.7% | 20.1% | 33.5% | 67.5% | 0.8 (6.1) | 1242 |
| | | 2 | 14.5% | 19.1% | 40.0% | 80.5% | 1.7 (15.8) | 467 |
| | | **3** | **20.0%** | **46.7%** | 36.4% | 77.8% | 1.4 (16.3) | **30** |
| salon | 11.5% | all | 22.8% | 36.3% | 43.4% | 81.8% | 0.5 (5.6) | 2415 |
| | | 1 | 14.5% | 26.9% | 36.0% | 71.8% | 0.2 (2.0) | 1285 |
| | | 2 | 30.9% | 39.3% | 51.7% | 92.3% | 0.8 (9.0) | 783 |
| | | **3** | **32.1%** | **46.4%** | 52.0% | 95.2% | 1.0 (10.9) | 347 |
| spotlight | 0.0% | all | 15.0% | 27.2% | 33.6% | 64.5% | 0.4 (3.0) | 2203 |
| | | 1 | 8.8% | 17.8% | 27.3% | 55.5% | 0.2 (1.8) | 1302 |
| | | 2 | 22.1% | 30.7% | 42.8% | 76.6% | 0.6 (4.7) | 762 |
| | | **3** | **24.8%** | **48.2%** | 42.4% | 82.6% | 0.6 (4.8) | 139 |

**THE FINDING: the two saturation metrics disagree, and the registered band
was written against the one that says "healthy".**

- **time-at-cap says moderate.** By act 3: fanfare 20.0%, spotlight 24.8%,
  salon 32.1% — all inside the PROPOSED 20–50% band. Read on this metric
  alone, the shipping world needs no remedy at all.
- **overflow says saturated.** By act 3 every arm throws away **46–48% of
  all Fanfare it generates**. Nearly half the generation is hitting a full
  meter. The two are consistent with each other: the pool is not *pinned*
  at the start of turns, it refills to the ceiling *during* them and spills.
  A start-of-turn snapshot cannot see that; the overflow counter can.
- Which one matches the playtest report ("basically always maxed unless
  you've got a payoff card")? Overflow does — and note the second half of
  that sentence: spends are **0.2–1.7 per combat**. The player is describing
  a meter with no outlet, which is exactly a high-overflow / low-spend world.
- The salon arm is both the most saturated AND the only arm winning (11.5%)
  — the arm whose scaling reads the meter is the arm most flattened by it.

**Registered divergence clause FIRES.** Baseline saturation is not
unambiguously high or low in sim; it depends on which registered metric is
read, and the Q1d acceptance band was defined on time-at-cap. That question
goes to [USER] before any Q1c remedy cell is trusted. Two decisions are
needed: (1) which metric the band governs — PROPOSED: overflow-waste
becomes the primary, with time-at-cap kept as a secondary; (2) if overflow
is primary, what band is healthy — PROPOSED: 15–25% by act 3, i.e. some
spill is fine, half is not.

**Caveat recorded:** the act-3 fanfare row is **n = 30 combats**. The
fanfare and spotlight arms win 0% of runs, so few reach act 3 at all; those
act-3 rows are thin and directionally read only. The salon act-3 row
(n = 347) is the solid one.

### Q3a — engine check GREEN (2026-07-24). No pre-item needed.

The queue's premise ("`furina-upgrades.yaml` has no precedent") is right
about Furina but the ENGINE precedent exists and the path is complete:

- **sim** — `tier0/content/upgrades.py` applies `{innate: true}` to
  `card.innate` (only `true` is a ruling, R37); `combat.surface_innate`
  prepends innate cards to the shuffled draw pile at combat start.
- **codegen** — `build_upgrade` emits `AddKeyword(CardKeyword.Innate)` for
  the same delta, under the same only-`true` rule.
- **precedent** — `klee-upgrades.yaml`: `catalytic_conversion {innate: true}`.
- **semantics worth knowing before pricing it:** Innate here is "top of the
  shuffled draw pile", not a reserved hand slot. With 5 cards drawn it
  reaches the opening hand as long as fewer than 5 innate cards exist.

### Q3b/Q3c/Q3d — measured (2026-07-24, seed 20260724, 400 fights/encounter)

One variable per arm: same deck, same seeds, `aria_of_recompense`
unupgraded / upgraded as ruled today (`encore +3`) / upgraded with
`innate: true` added. The innate delta was applied as a RUNTIME override of
the upgrade index — the sheet is a ratified artifact and this is a
diagnostic (R14). **Validity gate checked:** the override flips
`card.innate` and `surface_innate` does put `aria_of_recompense+` on top of
the pile, so the arm exercises the flag rather than silently no-opping.

| arm | A1 | A3 | A4 | A7 | fight wr |
|---|---|---|---|---|---|
| base (aria unupgraded) | 0.91 | 5.16 | 10.00 | 0.68 | 62.1% |
| aria+ as ruled today (encore +3) | 0.91 | 5.10 | 10.00 | 0.67 | 65.7% |
| aria+ WITH innate (proposal) | 0.90 | 5.05 | 10.00 | 0.66 | 66.1% |

**Q3c answer: A1 does not move.** 0.91 → 0.90 is noise, and it moves the
wrong way. The A1 statline amendment Q3c was written to catch is NOT
triggered: "dreadful A1" survives the fix, so the fix can ship without
reopening the statline declaration. Winrate gains +0.4pt over the ordinary
upgrade — small, and consistent with "this is a feel fix, not a power fix".

**Limitation, stated rather than buried:** this battery runs the STARTER
deck. The dead-hand complaint is about mid-run decks stuffed with
Encore-gated cards, where a turn-1 Encore source is worth most. The measured
+0.4pt is therefore a floor, not the effect size the complaint describes.
Measuring it properly needs an Encore-gated deck arm — a registered
addition, not something to slip in unregistered.

**Q3d — read from code, not measured:** `rest_action` smiths an ON-PLAN
card, payoffs before enablers. `aria_of_recompense` is `role: enabler`, so
it is taken only once no on-plan payoff is upgradable — it does not
automatically dominate the first fire, and the "tax wearing a fix's
clothes" failure does not appear. Worth re-reading if the fanfare payoff
set ever shrinks.
