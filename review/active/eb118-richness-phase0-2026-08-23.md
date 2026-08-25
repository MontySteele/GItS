# EB-118 — Klee, Furina, and Kokomi richness pass: Phase-0 contract

> **Lifecycle: ACTIVE. [USER]-APPROVED DIRECTION, 2026-08-23.** This is the
> implementation handoff produced from the GPT/Claude richness workshop. It
> authorizes the work and sequencing below; it does **not** itself change a
> card, an engine rule, or a world stamp.
>
> Reconciled against HEAD `1213355`, live world `RT12/D14/P7/C11`. The workshop
> was fact-checked at `0782dfc`; this packet replaces its stale pool counts and
> pre-C11 Kokomi assumptions. When this packet conflicts with `LAW.md`, an open
> QUEUE row, or the payoff-reach registration, those governing surfaces win.

---

## 0. Outcome

The pass is successful when the three characters gain **more consequential
choices and more connections between cards**, without simply receiving more
output.

The working model is:

> **Richness = player-controlled state changes × downstream relationships ×
> competing uses.**

This is not a clause-count exercise. A long automatic rider is not rich merely
because it contains several effects. A short chosen discard can be rich because
the discarded card, the discard event, the hand size, the pile it enters, and
later retrieval can all matter.

The three target identities are deliberately different:

| character | target | failure being repaired |
|---|---|---|
| Klee | **controlled chaos** | random placement and automatic Spark cash-out remove decisions |
| Furina | **meaningful flux** | rich resources and a typed Salon queue have too few player-directed verbs; inert/repeated riders dilute meaning |
| Kokomi | **complete and differentiate** | the smallest pool and repeated flat bodies underuse the identity of the chosen card she rotates |

No uniform quota is imposed across the three. Private mechanics are not bad.
The test is whether the player can shape them, whether other cards can care, and
whether using them now forecloses another use.

## 1. Binding rails and existing owners

These are part of the implementation contract, not caveats to apply later.

1. **No new named keyword.** `Burst +5` is a visible effect line or badge, not a
   third Klee keyword. Recycle, Salon manipulation, and modal cards are ordinary
   card text backed by ops/predicates.
2. **No replacement of `skill_tag`.** Its meter contribution remains +5 and its
   card membership remains unchanged. This pass makes the contribution visible.
3. **Klee's scaling never displaces her frontload** (`LAW.md`, Klee A1/A2 rail).
   Connective scaling must stay bounded; the first-per-turn Workshop trigger is
   the explicit guard.
4. **Spotlight remains freely movable and persistent.** This pass rewards
   moving, exploiting, or committing; it never resets or punishes movement.
5. **Kokomi never spends Charge, never self-damages, and never receives a
   healing exception.** Retrieval does not refund or remove banked Charge.
6. **C11 rotation law is binding.** Kokomi's unfiltered chosen-Exhaust and
   Conscript pools never select Status or Curse cards, and those cards never pay
   her Charge or Burst by any route. No richness card may route around
   `Card.is_junk` to regain the retired behavior.
7. **`EB-69` owns Kokomi's pool fill.** The live pool is 62 personal rows
   (5 basic / 27 common / 20 uncommon / 10 rare). The already-ruled fill is 14
   complete cards, not a new 15-card package, and lands at 76
   (5 / 31 / 26 / 14) in one batch with complete upgrade rows. `A3` /
   `discard_dividend` is dropped; the adopted `A4 + A6` package and the
   `S4-G11` name eye-read remain that row's authority.
8. **The richness pass does not delay `EB-69`.** Payoff-reach is explicitly
   settle-first and waits for `EB-69`; therefore putting the fill after the
   payoff grade would deadlock both workstreams. `EB-69` continues on its own
   registered path. R190 still forbids an Assist payoff-supply change before
   the grade. If an adopted `EB-69` body cannot be classified honestly without
   moving that supply, stop and surface that existing collision; do not disguise
   a payoff as glue to make the fingerprint pass.

   > **Annotation, 2026-08-23 (`R197`) — the clause above did its job and is
   > left as written.** The collision was real, it was surfaced rather than
   > engineered around, and [USER] amended R190's fence in answer: the
   > already-adopted `EB-69` batch may move Assist payoff supply (3 → 5), and
   > nothing else may before the post-settle grade. Read "R190 still forbids"
   > above as the state at signing;
   > `review/active/payoff-reach-reregistration.md` §6.8 carries the amended
   > fence and both figures.
9. **The payoff-reach freeze controls sheet landing.** Other than the already
   registered settle-first work (`EB-69`, `EB-70`, and their companions), no
   richness card-body, rarity, role, archetype, id-list, drafter, or policy
   change lands before the payoff-reach experiment grades. The static tool and
   unused staged infrastructure may be built now as described in §3.
10. **`D14` stays pinned — DISCHARGED 2026-08-24.** The pin lifted at the
    payoff-reach grade, and `EB-43` then spent the number it was reserving:
    `DRAFTER_VERSION` is **15** and the spotlight limb is what it means. The
    constraint's live remnant is its arithmetic only — richness op prices are a
    drafter behaviour change, so they take **their own `DRAFTER_VERSION`
    window**, with their own re-baseline. *(Hygiene, 2026-08-24: this clause
    named the integer `D16` outright. Integers are assigned AT integration and
    never reserved in advance — the same rule §3 states as "never hard-code the
    future integer in a staged branch" — and the reservation would have been
    wrong the moment R191 split Phase 2 into three windows that cannot all be
    16. Naming the window instead. The Phase-2 integration window did in fact
    take 16, assigned when it closed.)*
11. **Existing user gates remain existing user gates.** This packet recommends
    Retain as the `encore_performance` upgrade answer but does not close `M27`;
    role/payoff reclassification waits on `M28`; and it neither pulls nor
    rebases the staged `EB-74` Charge lever (`S4-G13`).

## 2. Connectivity measurement — pre-registered, unbuilt, unrun

### 2.1 Status and purpose

This section is the approved static pre-registration. The instrument is not yet
built and no baseline has been read. Its purpose is to answer **what a card
connects to**, which the seven-axis scorecard and the current `decide%` column
do not measure.

The proposed executable is `tools/card_connectivity_report.py`, with suite pins
under `tier0/tests/`. It is deterministic and reads sheets only; it has no run
count or random seed and moves no `RT/D/P/C` version.

The comparison corpus is all eight pools under one frozen classifier:

- canon: Ironclad, Silent, Defect, Necrobinder, Regent;
- mod: Klee, Furina, Kokomi.

The canon sources are the same local `game_ref/` extraction surfaces used by
`tools/canon_role_tempo.py`. If all five canon pools are not present, the tool
may print an explicitly **incomplete, diagnostic** mod-only report, but it must
not print a canon comparison or derive a threshold.

### 2.2 Classifier

Every card emits a machine-readable record with these fields:

| field | meaning |
|---|---|
| `shared_reads` | distinct public/universal states the card reads |
| `shared_writes` | distinct public/universal states the card changes or pays |
| `private_reads` | character-owned states read (Bombs, Sparks, Encore, Fanfare, Salon, Spotlight, Charge, Conscript/Sly) |
| `private_writes` | character-owned states changed |
| `chosen_actions` | non-target play-time selections: discard, Exhaust, pile selection, mode, X allocation, queue manipulation |
| `competing_uses` | a resource/card/state can be held, spent, consumed, moved, or retrieved for more than one downstream use |
| `external_reach` | a companion, colorless card, Ancient, status, or other non-personal card can satisfy or benefit from the hook |
| `automatic_only` | the card's extra value arrives without a play-time choice after the card is selected |

The initial shared-state vocabulary is explicit and versioned with the tool:

- HP lost or paid;
- chosen and random discard, reported separately;
- chosen Exhaust-other, self-Exhaust, and Ethereal, reported separately;
- junk/status/curse creation and removal;
- hand, draw, discard, and Exhaust-pile contents or size;
- Block held, enemy count, enemy intent, aura/reaction state;
- cards, Attacks, Skills, or Companions played this turn/combat;
- card identity, type, cost, upgrade state, and timing fields (X, Retain,
  Innate, Ethereal);
- Powers that modify a universal verb such as playing, drawing, discarding, or
  Exhausting any eligible card.

Character-private visible board state is counted separately, not excluded:
Bomb distribution and damage, Salon member order/type, Spotlight state, and
the five private numeric banks. A high private count is not a failure. The
separate columns prevent a private star graph from masquerading as an external
mesh while still giving credit to genuinely interactive private boards.

Pool output includes:

- share of non-basic cards with at least one shared hook;
- share with a non-target play-time choice;
- shared and private writer:reader ratios by state;
- cross-archetype edges and cards in two non-generic plans;
- share whose only extra value is automatic;
- random-damage and random-placement shares separately;
- external-reach share;
- distribution of distinct hook counts per card.

The scanner must use `tools.effect_walk` for nested `then:` / `else:` trees.
One fixture for each vocabulary entry and a red fixture for false positives are
required. Unknown ops, predicates, formulas, or card-level fields are reported
as **UNCLASSIFIED**, never silently counted as zero.

### 2.3 Baseline and comparison protocol

1. Build and test the classifier without editing a roster sheet.
2. Allow the pre-existing settle-first window, including `EB-69`, to finish.
3. Immediately before the first `EB-118` sheet edit, run all eight pools and
   record the commit, classifier digest, and input-file digests. This is the
   primary baseline. A read taken before `EB-69` may be archived as descriptive
   history but is not the paired baseline for Kokomi.
4. Freeze the classifier for the whole richness batch. If the vocabulary is
   found wrong, revise and re-run **both** sides; never repair only the post
   result.
5. Re-run after each coordinated phase, reporting paired per-card diffs as well
   as pool aggregates.

### 2.4 Committed directional predictions

These are direction-only because no all-five-canon baseline exists yet.

- **Klee:** chosen/controllable Bomb-board interactions and shared-hook share
  rise; random placement falls to zero; the explicit random spray family stays;
  manual Spark competing-use count rises.
- **Furina:** inert Cap and zero-body reader text falls; player-directed Encore
  spending and Salon queue control rise; repeated Fanfare-reader families
  shrink without removing the distinct marquee payoffs.
- **Kokomi:** distinct card signatures and identity-sensitive Exhaust choices
  rise; bridge/shared-decision density rises; ~~Assist payoff supply does not
  rise before the payoff grade~~.

  > **SPOILED 2026-08-23 by an authorized content intervention (`R197`) —
  > struck, not rewritten (`R101b`).** [USER] amended R190's Assist
  > payoff-supply fence to admit the already-adopted `EB-69` batch, and that
  > batch takes Assist payoff supply **3 → 5**. The clause above stands exactly
  > as published and is **not** re-predicted; a spoiled prediction is not a
  > corrected one. The amendment, both supply figures, and the retrieval-rubric
  > route to 6 are recorded at
  > `review/active/payoff-reach-reregistration.md` §6.8. The other two Kokomi
  > clauses on this line are untouched and still live.

### 2.5 No gate yet

There is **no 55–65% target and no pass/fail threshold in this registration**.
The earlier Ironclad-common estimate mixed STS1 hand classification with the
mod sheets and cannot govern STS2 content. An absolute gate may be proposed only
after the same frozen classifier has read all five canon pools.

The existing distinctness gate remains independent and binding: `uniq >= 70`,
`maxclu <= 5`, `neardup <= 0.40`. Connectivity may explain a failure; it does
not waive one.

### 2.6 Registered blind spots

- Current `decide%` sees conditionals/formulas/select keys but misses several
  chosen discard/Exhaust prices. Its result is not a substitute for this tool.
- Tier0's `enemy` target is a lowest-HP heuristic, not human target choice.
- Tier0's chosen-Exhaust pilot uses a highest-cost non-Attack proxy. That proxy
  becomes directionally wrong when the exhausted card's identity determines
  the payout.
- A static hook is opportunity, not proof that a human decision is difficult.
  Live play remains the final check.

## 3. Delivery order and merge fences

### Phase 0 — this packet

Complete when this file, its BACKLOG row, its EXPERIMENTS pointer, and its STATE
workstream pointer are in HEAD. No world version moves.

### Work allowed now

Two kinds of work may start before payoff-reach grades:

1. **The read-only connectivity tool** may be implemented, tested, and merged.
   It changes no pool and no run behavior.
2. **Unused infrastructure** may be built on local staged branches, machine-
   checked, and pushed nowhere, following the settled `EB-74` Route-1
   precedent. Merging a branch that exposes a new op to a shipped card, changes
   a drafter price, or changes policy is the pull and remains fenced.

The staged infrastructure set is:

- `spend_spark`;
- base-card Ethereal plus remove-Ethereal upgrade/codegen/drafter support;
- card-resolution-scoped Exhaust identity/cost/type context;
- `recall_to_draw` with `from: exhaust` and returned-card Exhaust;
- Salon rotate-leftmost-to-back and perform-leftmost-now;
- one generic choose-one/modal effect surface;
- Klee Bomb-placement and Kokomi Exhaust-selection pilot policies;
- C# parity, codegen support, drafter prices, and focused tests for each.

Use separate staged branches where dependencies differ. Do not bundle a policy
bump into a mechanically unused op branch merely because both belong to this
packet.

### Phase 1 — post-grade, existing identity and effect cleanup

After payoff-reach grades, land one coordinated card-body/C# parity batch that
holds card ids, rarities, roles, and archetypes. It contains:

- Klee's Bomb-placement target cut, the two existing-grammar face prices,
  visible `Burst +5`, and Explosives Workshop conversion;
- Furina's sixteen Cap-rider removals and redundant Block-reader cleanup;
- no new cards and no role/archetype movement.

Take the connectivity baseline immediately before this phase. Use one
appropriate `C` bump at integration; never hard-code the future integer in a
staged branch.

### Phase 2 — infrastructure landing and honest policies

Both of this phase's preconditions are **satisfied as of 2026-08-24** — the
`D14` pin lifted at the payoff-reach grade and the reserved `D15`/`EB-43` step
executed — so what follows is takeable, under **a `DRAFTER_VERSION` bump of its
own, the integer assigned when the window closes** (hygiene 2026-08-24: this
line named `D16` in advance; see §1.10. The window closed on 2026-08-24 and the
integer it took is 16). Land new ops with prices and parity. Land the two pilot changes under an explicit
`POLICY_VERSION` bump before using run results to tune Bomb placement or Recycle
cards. One modal prototype is priced before the pattern is copied. Land Big
Badda Boom's Ethereal price here, with the card-level keyword and its drafter
valuation, rather than treating an unpriced downside as a Phase-1 sheet edit.

### Phase 3 — connective card authoring

After payoff-reach grades and `M28` resolves the payoff-label/band question:

- add or convert Klee Bomb-board readers and the 3–4-card Spark sink family;
- add Furina's Salon-control cards, deliberate ordinary-turn Encore spenders,
  Spotlight reward card(s), and payoff-to-glue conversions;
- apply Kokomi's Recycle grammar, Exhaust retrieval, and clone-family rewrites
  to the now-complete `EB-69` pool.

Any id, rarity, role, or archetype movement is isolated here, after the
experiment it would otherwise contaminate.

### Phase 4 — balance and live play

Re-run tier0/tier0.5 only after the pilot can exercise the decisions. Then run
the distinctness and connectivity reports and play the three characters live.
Reduce raw faces only after the new multiplicative/connective structure is in
place. Keep one-variable measurement windows; a structural batch and its later
numeric correction are not one measurement.

## 4. Klee — controlled chaos

### 4.1 Preserve

- start-of-turn Bomb detonation and Attack-triggered early detonation;
- Quick Fuse and the existing detonation schedule;
- Gleeful Barrage's read-before-spend rule;
- the nine current card rows whose explicit `damage` op targets
  `random_enemy`, including Study of Explosions;
- True Spark Knight's threshold-2 interaction.

The rule is: **Klee controls where she prepares explosions; she does not always
control where the spray lands.**

### 4.2 Bomb-placement target cut

All twelve random `place_bomb` rows become one of two existing shapes. Do not
substitute `all_enemies` while retaining `amount: N`; the engine loops amount ×
targets and would create N bombs on every enemy.

| card | new form | amount rule |
|---|---|---|
| `jumpy_dumpty` | concentration, `target: enemy` | keep 1 |
| `ammo_scavenging` | concentration | keep 1 |
| `chain_fuse` | concentration | keep 1 |
| `bomb_voyage` | concentration | keep 3 |
| `sorry_jean` | concentration | keep 1 |
| `bombs_away` | concentration | keep 5 |
| `controlled_demolition` | concentration | keep `X_plus_1` |
| `all_my_treasures` | concentration | keep 6 |
| `mine_toss` | distribution, `target: all_enemies` | set 1 |
| `jumpy_dumpty_mk2` | distribution | set 1 |
| `cluster_charge` | distribution | set 1 |
| `sparkly_explosion` | distribution | set 1; avoids a second target prompt after the kill |

This default keeps the two-enemy median Bomb count stable for the four
distribution cards, while giving them a real width profile. Reprice each card
against one-, two-, and three-enemy cases before landing. Do not restore random
placement to repair a bad number.

Tier0 must gain a placement policy before the balance read is authoritative.
For concentration, enumerate legal enemies and value detonation timing,
existing Bomb stacks, lethal waste, and board readers. Lowest HP alone is not
the decision this pass is adding.

### 4.3 Three direct faces gain readable prices

Keep their base damage for the structural pass; add the second price first.

| card | base change | upgrade direction | delivery |
|---|---|---|---|
| `blast_radius` | after resolving, discard 1 chosen card | keep the current damage upgrade for the first pass | Phase 1 |
| `big_badda_boom` | gains Ethereal | replace `damage: +4` with removal of Ethereal | Phase 2, after Ethereal is priced and mirrored |
| `no_holding_back` | gains Exhaust and adds one `confiscated` to discard | keep the current damage upgrade for the first pass; both prices remain | Phase 1 |

`confiscated` is the already-shipped Klee status-price vocabulary. Do not
invent a card-side Burn injector inline. If the name/face makes that rider read
as a lore mismatch at the implementation eye-read, stop on that one card and
keep the approved shape — **one junk card as price** — rather than silently
dropping the price.

### 4.4 Explosives Workshop

Keep id, rarity Uncommon, `role: payoff`, and `[demolition]`. Replace the flat
`bomb_damage_up 2` install with:

> **The first time each turn you discard or Exhaust a card, your Bombs deal +1
> damage this combat.**

The trigger includes ordinary eligible cards and Klee's status-exhaust route;
the once-per-turn latch is the bound. It increments the same
`bomb_damage_up` value read at detonation, so already-placed and future Bombs
agree. The upgrade raises the per-trigger increment from +1 to +2; it does not
add another trigger per turn.

Build the new Power hook in both engines on a staged branch now. Landing it with
Workshop is Phase 1. Because the card remains a Power with the same metadata,
the existing drafter's zero self-Power credit does not require a `D` bump; pin
that fact in a focused test instead of relying on prose.

### 4.5 Sparks become a resource with a competing use

Add `spend_spark` only after the drafter pin lifts.

- Sinks are **Skills only**, Uncommon or Rare, three or four cards total.
- A sink never silently fires. If the bank is short, normal playability/branch
  rules make the cost visible.
- Price the spend-2 outcome near or below one free Attack: roughly one energy of
  value, not a second payoff stapled on top.
- The primary sink is demolition-flavored: **Spend 2 Sparks; detonate the
  chosen target's Bombs with a bounded bonus.** It joins the Spark choice to
  the Bomb-timing choice and supplies the missing demolition × spark bridge.
- Under True Spark Knight, spending 2 deliberately forfeits the threshold-2
  free Attack. That sharper trade is intended.

The pilot must value hold-versus-spend. Until it does, no tier0.5 Spark-sink
number is citable.

### 4.6 Visibility and later readers

Every one of the fifteen `skill_tag` cards shows `Burst +5` in generated card
text or a non-keyword badge. The tag and meter arithmetic do not move.

After the placement cut, author two or three board readers at different
rarities: concentrated-stack, distributed-board, and detonation-timing shapes.
They are Phase 3 because new ids or payoff-role changes move the fingerprint.

## 5. Furina — meaningful flux

### 5.1 Preserve

- the typed, three-slot FIFO Salon queue and distinct member identities;
- automatic Salon upkeep as a standing commitment;
- Spotlight's two modes and freely movable persistent designation;
- High Tide, Flood of Emotion, and Thunderous Ovation as three distinct payoff
  shapes;
- Crescendo, Florid Cadenza, Universal Revelry, The Final Verdict, and the kit
  Burst as marquee reads.

### 5.2 Remove inert Fanfare Cap riders

Delete `raise_fanfare_cap` from these sixteen cards:

`casting_call`, `lasting_impression`, `grand_salon`, `pit_orchestra`,
`leading_role`, `supporting_cast`, `top_billing`, `standing_ovation`,
`fortissimo_guard`, `courtroom_drama`, `quick_change`, `crowd_work`,
`endless_waltz`, `star_of_the_show`, `prima_donna`, `reginas_mercy`.

Retire the sheet/register lint rule that every non-grant Power must print
`Fanfare Cap +X`. Keep the semantic distinction available: if a future
dedicated card raises the cap, it prints `Fanfare Cap +X`; rare Power full
grants continue to print `Fanfare +X`. Amend the LAW wording with the landing
so it describes an available explicit verb rather than a universal Power rider.

Do not compensate these removals with flat numbers in the same batch. The line
was measured close to inert; removing it is a legibility correction whose value
is that printed riders become trustworthy again.

### 5.3 Collapse the repeated Fanfare-reader families

The five Block readers are:

- `suffering_for_art`: Block 0 + 1 per 4;
- `lasting_impression`: Block 0 + 1 per 4;
- `held_breath`: Block 4 + 1 per 4;
- `hearts_swelling`: Block 3 + 1 per 4;
- `thunderous_ovation`: Block 6 + 1 per 2.

Phase 1 changes:

- delete the zero-base Block rider from `suffering_for_art`;
- delete the zero-base Block rider from `lasting_impression`;
- keep Hearts Swelling's printed Block 3 but remove its Fanfare formula;
- preserve Held Breath as the Common reader and Thunderous Ovation as the Rare
  payoff.

Phase 3 converts `dramatic_entrance` away from being a larger Applause Line and
`standing_room_only` / The House Rises away from being a smaller Universal
Revelry. Their final bodies are authored after `M28`; do not change role tags in
Phase 1 merely to improve a count.

### 5.4 Encore choices

Furina already has three explicit `spend_encore` effects, two `encore_cost`
cards, and automatic Salon upkeep. The missing space is a small number of
**deliberate, player-directed ordinary-turn cash-outs**, not more total drains.

Build one choose-one/modal prototype first. It must support a visible pair such
as "gain Encore" versus "spend Encore for tempo," with C# mode selection and a
drafter price. Do not copy the pattern to four cards until the pilot and price
can distinguish the modes. Later cards should bridge plans rather than create a
fourth Encore-only silo.

### 5.5 Salon queue verbs

Build these over the existing queue; do not replace it with a counter:

1. **rotate leftmost to back** — preserves member identity, performs no tick,
   drains no Encore, and triggers no bow/replacement effect;
2. **perform leftmost now** — calls the same member-action path as a normal
   tick, including its standard Encore/Fanfare/resource consequences, exactly
   once;
3. **read/reward leftmost member or member type** — predicates/formulas that
   let card bodies care which performer is next.

No duplicate Salon-resolution implementation is acceptable. Normal tick,
perform-now, tooltip text, telemetry, and C# must share the member definitions.

### 5.6 Spotlight predicates

- `spotlight_unmoved_this_combat` means whole-combat commitment and may appear
  on **at most one Rare**.
- `spotlighted_card_played_this_turn` means the established star was exploited;
  it is not the logical opposite of moving, because a moved designation can be
  played afterward in the same turn.
- For a true per-turn move/stay branch, use a nested conditional: first require
  `spotlight_set`, then branch on `spotlight_moved_this_turn`; the else is the
  established designation. Nested conditionals already work.

The new stay/reward card is Phase 3. Retain on `encore_performance` remains the
recommended `M27` answer, but this packet does not apply it without that row's
explicit ruling.

## 6. Kokomi — complete and differentiate

### 6.1 Preserve

- chosen Exhaust as rotation, not sacrifice;
- the Common no-deck-growth law;
- Sly and chosen/random discard distinctions;
- uncapped, read-only Charge;
- Vigil of the Deep, Sango Isshin, All Streams Flow to the Sea, and Nereid's
  Ascension as signature ceiling pieces;
- Assist as a real third plan whose job is bridge/velocity before it receives
  any additional payoff supply.

### 6.2 `EB-69` relationship

Do not add a second expansion. Implement the ruled 14-card batch with all
upgrade rows and the name eye-read, then take the richness baseline. The later
Kokomi work rewrites bodies and relationships inside that 76-row pool.

The old frozen brief is not current authority on counts or upgrades. Its useful
design inheritance is the A4/A6 package and the bridge intent; `EB-69`, R157,
R190, and C11 govern the implementation.

### 6.3 Recycle grammar — selected identity determines payout

The best new Kokomi grammar is not "Exhaust N, gain a larger flat number." It is
"the card you chose tells this card what to do." Initial families:

- payout scaled by the exhausted card's printed energy cost;
- Attack exhausted → offensive branch; Skill/Power exhausted → defensive or
  utility branch;
- Companion exhausted → Commander/Assist bridge;
- pile or card-type payout that changes which otherwise-useful card is rotated.

Do **not** add a "Status exhausted" reward. C11 makes Status/Curse ineligible for
Kokomi's ordinary rotation and grants no resource from one.

Implementation contract for context:

- the chosen `exhaust_from` records descriptors for the selection it just
  resolved: id, cost, type, rarity, companion/personal ownership, and upgraded
  state;
- the record is scoped to the resolving card/effect, not a combat-global
  `last_exhausted` value that can leak across cards;
- a second `exhaust_from` replaces/opens its own context explicitly;
- subsequent formulas/conditionals can read total cost and type counts;
- both engines emit the same victim ids and derived values for parity tests.

The drafter's existing neutral formula estimate can accept new count names
without a `D` bump only if its price remains the same generic `base + per`
approximation. Pin that fact. The **pilot does need a bump**: replace
highest-cost-non-Attack with candidate enumeration that weighs the lost card's
future value against this card's immediate payout. Otherwise it will appear
expert by accidentally choosing the highest payout while ignoring the cost.

Use the first three rewrites to break known clone families rather than adding
new rows: `votive_offering`, `cleansing_tide`, and `shell_of_sanctuary` are the
starting candidates. Final bases/slopes are authored only after the chooser can
exercise them and must preserve the no-heal/no-self-damage rails.

### 6.4 Exhaust retrieval

Extend `recall_to_draw` with `from: exhaust`; do not mint a parallel op family.
All six constraints are mandatory:

1. the retrieval card is Uncommon or Rare;
2. the retrieval card Exhausts;
3. it cannot target a kit card or any card that itself retrieves from Exhaust;
4. the target returns to the **top of the draw pile**, never hand;
5. the returned card gains Exhaust for the rest of combat.
6. Status and Curse cards are ineligible targets; ordinary personal and
   Companion cards remain eligible.

The retrieval card and a draw slot are the immediate price. The returned card
is on loan for one more use, then rotates again and grants Charge again under
normal law. Removing it from the pile temporarily weakens only pile readers;
banked Charge does not fall. Run `engine_closure` against the complete effect
graph and pin the self-target/retriever-target exclusions in both engines.

### 6.5 Clone and bridge work

After Recycle/retrieval infrastructure lands:

- break the flat-Block cluster with selected-card identity, next-turn timing,
  or public-state reads rather than larger Block numbers;
- reduce duplication between Uncommon/Rare ward bodies while preserving Vigil
  as the signature prevention Power;
- reduce the four `exhaust_pile` damage readers to distinct jobs rather than
  four slopes over one count;
- make Assist cards feed Priest and Commander decisions; do not create more
  Assist payoff roles until the registered payoff read has graded them.

### 6.6 `EB-74` is balance, not richness

The staged `CHARGE_PER_EXHAUST 1 -> 2` candidate remains unpulled. This pass may
raise Exhaust events per fight by making them worth choosing, which can make
the doubling unnecessary. Re-evaluate the lever only through `S4-G13` after
the required observation. Never merge it as compensation for a Recycle card.

## 7. Acceptance and handoff checklist

### Static and structural

- connectivity instrument runs on all eight pools with a frozen classifier, or
  stops honestly when canon sources are absent;
- Klee random Bomb placement is zero and explicit random damage remains;
- Furina has no incidental `raise_fanfare_cap` carriers and the retired
  every-Power lint is gone;
- Kokomi Status/Curse exclusions remain pinned at every rotation/resource seam;
- distinctness gate is green, or every remaining failure is listed by exact
  clone family and assigned to a later phase — never waived by aggregate hook
  improvement;
- no new named keyword and no silent role/archetype relabel.

### Engine and parity

- every new op/predicate/formula has tier0 behavior, C# behavior, generator
  support, a drafter price or a pinned proof that the existing generic price
  applies, and positive/red tests;
- generated roster output is current;
- Salon perform-now shares the normal member-action path;
- Exhaust context cannot leak between card resolutions;
- retrieval exclusions and `engine_closure` are green;
- `Burst +5` visibility changes text only, not meter arithmetic.

### Measurement

- no richness sheet edit precedes the paired baseline;
- no pre-C11 Kokomi number is used as the post-pass comparator;
- no tier0.5 balance claim precedes the Bomb and Exhaust chooser policies;
- payoff-reach's registered ordering, `D14` pin, R190 supply fence, and existing
  `EB-69`/`EB-70` settle-first work remain intact;
- raw damage/Block reductions happen after structure, in their own window.

### Standard verification

From the repository root:

```sh
.venv/bin/python -m pytest tier0/tests tier05/tests -q
GITS_REFERENCE_MODE=committed-only .venv/bin/python -m pytest tier0/tests -q
.venv/bin/python tools/gen_roster_cards.py --check
.venv/bin/python tools/lint_op_parity.py
.venv/bin/python tools/lint_constant_parity.py
.venv/bin/python tools/lint_handwritten_parity.py
.venv/bin/python tools/card_distinctness_report.py --gate
```

For a branch with C# changes, also run the opt-in headless suite and the normal
build/deploy validation on the Windows host before calling parity complete.

## 8. Definition of done

`EB-118` closes only when:

1. the static baseline and final comparison are recorded;
2. the approved character changes have landed with upgrades and two-engine
   parity;
3. policy can exercise the new decisions;
4. the three pools pass structural gates or carry an explicit [USER]-ruled
   exception;
5. a live play pass confirms that Klee feels controlled rather than random,
   Furina's resources create active tradeoffs, and Kokomi's selected card
   identity matters;
6. no required work remains in this packet. Staged-but-unmerged infrastructure
   is not completion.
