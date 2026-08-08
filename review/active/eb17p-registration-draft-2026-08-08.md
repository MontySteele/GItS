# EB-17p — force-first-copy PAIRED winrate: pre-registration (DRAFT)

> **Lifecycle: DRAFT — [USER] countersign REQUIRED before anything here
> operates.** Pre-registration drafts are a [USER]-gated class
> (`docs/current/EXPERIMENTS.md`, "Pre-registration + blind grading").
> **Nothing below is a prediction that has been graded, a number that has
> been read, or a measurement that has been run.** No measurement was run to
> produce this document. The mechanism probe described in §11 ran on a
> THROWAWAY seed set that §4 excludes from the registration, and no number
> from it appears anywhere in this packet — only the statement that the
> harness executes.

**Provenance.** `docs/current/BACKLOG.md` row `EB-17p`, whose phrase is the
register's own: *"two decks on the same seeds, one with a copy forced in, one
without."* The register is Window D of the Klee survival sprint plan
(`git show pre-simplification-2026-08-06:docs/archive/klee-survival-sprint-plan.md`
§4): *"Do not use raw pick rate as the redesign trigger… First add or run
paired evidence for: … force-first-copy paired winrate. Then consider, one at
a time: `friendly_visit` … `study_buddy` … `borrowed_brilliance` …
`elemental_ecstasy`."*

**What already ships, and what it declines to be.** `metrics.card_flow_profile`
(`tier0/harness/metrics.py:942`, EB-17, commit `b37786a`) is the fight-side
half. Its own docstring fences it (`:960-967`):

> The `force_first_copy` block is the fight-side half of the register's
> "force-first-copy paired winrate". `winrate_first_copy_played` and
> `winrate_first_copy_dead` split the combats that DREW the first copy by
> whether it converted; the delta between them is a within-arm split and is
> deliberately NOT called the paired winrate, because the register's pairing
> is two arms on the same seeds (a deck with the copy forced in against the
> same deck without it) and tier0's kernel neither builds decks nor drafts.
> Forcing the copy is the caller's; this is what the caller reads afterwards.

This registration is the caller. The shipped split is **conditioned on
drafting the card**, so it compares decks that chose it against decks that
chose it and whiffed — a within-arm, self-selected contrast. The registered
experiment removes the selection by *assigning* the copy.

---

## 1. Question

**Q1 (primary).** For a named card `X`, does forcing one copy of `X` into the
deck at run start change the run's winrate, holding the seed fixed?
Estimand: **Δ = P(win | forced) − P(win | not forced)**, paired by seed.

**Q2 (secondary, descriptive).** Within the forced arm, what does the card's
own flow look like once every run holds it — `draws_per_fight`,
`played_when_drawn_rate`, `dead_in_hand_rate`, `force_first_copy_rate`
(`card_flow_profile`, per card id)? This is the read the shipped instrument
was built for; it is reported **beside** Q1 and is not the pairing.

**Q3 (secondary).** Does the assignment survive the run — the **compliance**
census of §6.3. A forced copy can be removed at a rest node
(`tier05/model.py:508`) or rewritten by an upgrade (`:510`, `:425`), so "we
forced it" is a claim that has to be measured rather than assumed.

**Not asked here.** Whether any observed Δ is large enough to justify a
redesign of `X`. That is the design act the register and the instrument both
refuse to make; it is [USER]'s, downstream of the grade.

## 2. Mechanism — how the forced copy enters

Two mechanisms were considered. **The choice is deck-injection at run start.**

### 2.1 Rejected: draft-stream override

Forcing the copy through the draft would mean either a new entry in
`draft.POLICIES` (`tier05/draft.py:1629`) or a change to how offers are rolled
and scored. `POLICY_VERSION` lives in that same file (`:1424`, currently 6)
and is one of the four fields in the run-cell stamp
(`tier05/cells.py:123-130`). Under EXPERIMENTS' "one variable per window"
(D4), a policy change **is** a version bump in the same edit, so this
mechanism would (a) move the `P` stamp, (b) make the change under test a
*drafter behaviour* change rather than a *deck* change, and (c) sit squarely
in the class of edits the R121 six-step order pins. Rejected on all three.

### 2.2 Chosen: deck-injection at run start (`force_cards`)

A new keyword argument `force_cards: list[str] | None = None` on
`model.run_one` / `model.run_many` / `cells.Cell`, applied at the **end** of
`_setup_run` (`tier05/model.py:770-847`), appending the ids to `ctx.deck_ids`
— which is the same list object `RunResult.deck_ids` holds, so the injection
is visible to every downstream deck read without a second write.

**Why the end of `_setup_run`, and not `loader.starting_deck`.** Run-start
relic effects run *between* those two points, and two of them consume the
main RNG stream in a deck-size-dependent way: `_pickup_upgrade` does
`rng.shuffle(cands)` over the upgradable deck indices
(`tier05/relics.py:433-445`), and `grant_random_common` rolls off the same
stream (`:424-430`). Injecting before them would desynchronise the shared
stream at floor zero and destroy the pairing before the first node. Injecting
after them leaves **run start byte-identical between the arms**, so the two
arms enter floor 1 with the same map, the same seeded/Neow relics and the same
gold — differing in exactly one card.

**Why this is not a drafter change, and why the D14 pin does not gate it.**
`DRAFTER_VERSION` (`tier0/constants.py:1126`, currently 14) versions the
scorer's *behaviour*. `force_cards` adds no term to `_static_power`, no
policy, no offer rule; the drafter scores a different deck by the same
function, which is data, not behaviour. Both arms therefore run at the
**same** `RT/D/P/C`, and the R121 six-step order's pin on `DRAFTER 14` is
untouched. **This experiment is NOT gated behind the D14 pin** and does not
reorder any step of R121. (It is also not the staged `EB-43` / D15 change and
must not be run against a tree that has landed it — see §9 stop condition
S3.)

**Byte-identity obligation.** `force_cards=None` must be provably the world we
have: the seam ships with a test in the house shape (`grant_relics` /
`grant_potions` / `slot_mode` precedents, `tier05/model.py:858-891`) pinning
that a `None` batch is element-for-element identical to the pre-seam batch.
Without that pin the control arm is not an anchor. See §10.

### 2.3 Intent-to-treat, stated up front

Assignment is at run start; the run layer may still upgrade the copy (id
becomes `X+`, `upgrades.SUFFIX`) or remove it at a rest node. The registered
estimand is **intent-to-treat**: forced-at-start versus not-forced, whatever
the run subsequently does to it. Compliance is measured (§6.3), never
enforced — enforcing it would require a run-layer behaviour change, which is a
different world and a different registration.

Symmetrically, a **control** run may draft `X` on its own. Those pairs are
**kept** in the primary estimate (that is what intent-to-treat means, and the
contrast the register asks for is "forced in" vs "as the game gives it"). The
natural-acquisition rate in the control arm is reported (§6.3); a
never-acquired-control subgroup is a **pre-registered secondary** (§6.4) and
may not be promoted to primary after the fact.

## 3. World, cell and arms

**Stamp at draft date: `RT9 / D14 / P6 / C8`**
(`RUNTEMPLATE_VERSION = 9`, `CONSTANTS_VERSION = 8`, `DRAFTER_VERSION = 14`,
`tier0/constants.py`; `POLICY_VERSION = 6`, `tier05/draft.py:1424`), read live
via `tier05.cells` and reprinted by `Cell.stamp()` on every table. **Pinned
for this experiment**; a bump in any of the four before execution
re-registers (§9, S1).

**Base cell.** `cells.CANONICAL.but(character="klee", archetype="reaction",
name="eb17p")` — the ratified cell (R68): seed 11, route `hunter`, policy
`assigned`, realistic loadout (relics + potions), all registered acts.
`klee/reaction` because all four register-named cards are Klee cards whose
`archetypes` list is `[reaction]` (`docs/klee-cards.yaml:87, 172, 174, 176`),
and because `assigned` is the policy under which "the deck the plan wanted"
is a well-defined control.

**Arms.** For each swept card `X` (§5), two arms over the same seeds:

| arm | `force_cards` | role |
|---|---|---|
| `control` | `None` | anchor; must be byte-identical to the unmodified world |
| `forced(X)` | `[X]` | one copy of `X` injected at run start |

`control` is run **once** and reused as the paired partner for every `X` —
the same seeds, the same world, one control arm, five treated arms. This is a
deliberate reuse: re-running an identical control per card would burn budget
to reproduce the same list.

## 4. Seeds and pairing

- Base seed **11** (the ratified cell). Run *i* of a batch is a pure function
  of `seed + i` (`tier05/model.py:941-950`), so the pairing is **by index**:
  run *i* of `forced(X)` and run *i* of `control` share seed `11 + i`.
- Registered seed range: `11 … 11 + N − 1` with `N` from §7.
- **Excluded, explicitly:** seeds `424242 … 424249`, the throwaway set the
  §11 mechanism probe used. They are outside the registered range by
  construction; naming them here makes the exclusion auditable rather than
  incidental.
- Pairing is on the **seed**, not on lockstep trajectories. The arms share
  every exogenous roll up to the first point the extra card changes an
  outcome, and diverge thereafter — that divergence *is* the treatment
  effect, not a defect of the design. The claim the design buys is the
  standard one: the two arms face the same distribution of maps, encounters,
  relic and reward rolls, pair by pair.

## 5. The sweep — which cards

The four cards the register names, in its order
(`klee-survival-sprint-plan.md` §4), plus one filler control:

| id | name | rarity | cost | note |
|---|---|---|---|---|
| `friendly_visit` | Friendly Visit | common | 1 | Block 5 + companion cost −1 + draw 1 |
| `study_buddy` | Study Buddy | uncommon | 1 | Block 6 + replay-next-companion |
| `borrowed_brilliance` | Borrowed Brilliance | uncommon | 1 | free temp copy of a companion in hand |
| `elemental_ecstasy` | "Sweet Dreams" | uncommon | 2 | aura refresh + per-aura draw + conditional Block 8 |
| **`FILLER`** | *[USER] slot, §5.1* | — | — | **deck-size negative control** |

**5.1 The filler arm (negative control) — [USER] SLOT.** Every treated arm
adds a card, so every treated arm also *dilutes* the deck by one. Without a
filler arm, dilution and card effect are confounded and a null read is
unreadable. The filler is a card whose effect is understood and whose value is
not what the sweep is about — the obvious candidate is a duplicate of the
character's own starting Strike (`loader.starting_deck`), but *which* card the
filler is, is a **[USER] choice**, because picking it is picking the baseline
every other row is read against.

> **[USER] SLOT — FILLER**: `______________________`

**5.2 Card-id family.** Every read pools `X` with `X+` (`upgrades.SUFFIX`),
because a smith node rewrites the id in place (`tier05/model.py:510`). A read
keyed on the bare id would score an upgraded forced copy as an absent one.

## 6. Metrics

### 6.1 Primary (Q1)
Per card `X`, over the `N` seed-matched pairs:
- `delta_win` = winrate(`forced(X)`) − winrate(`control`), with a **paired**
  interval: exact McNemar on the discordant pairs (`b`, `c`) for the test, and
  a paired bootstrap (resampling *pairs*, own RNG stream, own seed, never the
  run seed — the `exp_reactions_corpus` rule) for the interval on Δ.
- Discordant counts `b` / `c` and the concordant counts are printed. A Δ with
  no discordant count beside it is not citable here.
- Unpaired Wilson intervals per arm (`tier05.stats.wilson95`) are printed for
  continuity with every other roster table, and are explicitly **not** the
  test.

### 6.2 Secondary run-level
`delta_act1` (act-1 clear), `delta_acts` (mean acts completed),
`delta_decksize`, `delta_fights` — same pairing, same reporting shape.

### 6.3 Compliance and contamination census (Q3)
- forced arm: share of runs whose FINAL deck still holds the `X` family;
  share removed at rest; share upgraded.
- control arm: share of runs that drafted the `X` family on their own
  ("natural acquisition"). This number bounds how much of the contrast the
  design can possibly see: if the control arm already holds `X` often, ITT Δ
  is attenuated by construction, and the packet says so *before* the number
  exists.

### 6.4 Pre-registered secondary subgroup
Δ restricted to pairs where the control run never acquired the `X` family.
Reported with its own `n`. **Secondary. It may not be promoted to primary
after the read**, and a Δ that appears only here is a hypothesis for a new
registration, not a finding.

### 6.5 Card-flow read (Q2)
`metrics.card_flow_profile` over the forced arm's `fight_stats`, restricted to
the `X` family: `draws_per_fight`, `played_when_drawn_rate`,
`dead_in_hand_rate`, `force_first_copy_rate`. Printed via
`report.print_card_flow`'s existing shape.

**Instrument visibility (D4), confirmed.** `RunResult.fight_stats` carries the
EB-17 counters through to tier 0.5, and `card_flow_profile` consumes tier-0.5
fight stats unchanged — verified on the throwaway probe (§11). The changed
object (one card in the deck) is seen by a one-seat sim instrument; there is
no C#-only limb in this experiment and no `support` term.

## 7. Sizing — run counts

**Variance model.** The outcome is binary at the run level. For a paired
binary contrast the variance is carried by the **discordant** pairs:
`SE(Δ) = sqrt(d / N)`, `d` = discordant rate, `N` = pairs. Two bounds bracket
`d` without reading anything from this experiment:

- **Conservative (no pairing benefit at all — independence):**
  `d ≈ 2p(1−p)`. At the scale Klee arms are known to sit (single-digit
  percent, roster-anchor table), `d ≈ 0.11`.
- **With pairing:** `d` falls with the seed-level correlation the design
  buys. `d ≈ 0.05` is the optimistic half of the bracket.

Minimum detectable Δ, two-sided α = 0.05, power 0.80 (factor 2.80):

| pairs `N` | MDE at `d = 0.11` | MDE at `d = 0.05` | runs (1 control + 5 treated) |
|---|---|---|---|
| 600 (ratified cell) | 3.8 pp | 2.6 pp | 3,600 |
| 1,200 | 2.7 pp | 1.8 pp | 7,200 |
| **2,400 (registered default)** | **1.9 pp** | **1.3 pp** | **14,400** |
| 4,800 | 1.4 pp | 0.9 pp | 28,800 |

**Registered default: `N = 2400` pairs per card**, i.e. `runs=2400` on each of
the six arms, 14,400 runs total. Rationale: at the ratified 600 the design
cannot separate anything smaller than a ~4 pp move on a base rate of a few
percent — which is most of the moves a single common card could plausibly
make — and the whole point of pairing is to buy resolution the roster-anchor
table does not have. 2,400 is the first rung where the conservative MDE is
under 2 pp.

**`N` is fixed at countersign and may not be extended after a read.** Adding
runs because an interval "almost" excluded a threshold is optional stopping;
the tripwire in §9 (S4) is the only path from a null to more data, and it goes
back through [USER].

> **[USER] SLOT — `N`** (accept 2,400 or set another): `__________`
>
> **[USER] SLOT — cost ceiling** (wall-clock / jobs budget the sweep may
> spend before it must stop and report): `__________`

## 8. Predictions — [USER], before any number is read

Per EXPERIMENTS ("pre-registered from design intent … never revised against
the playtest that grades it") and the R121 precedent that predictions are
authored design-side and appended **as their own commit before any
measurement runs**. Drafting them here would be exactly the retro-fit the
payoff-reach authority forbids.

For **each** swept card, [USER] states a direction and a threshold:

| card | predicted sign of Δ | threshold (pp) that counts as a real move | confidence |
|---|---|---|---|
| `friendly_visit` | ____ | ____ | ____ |
| `study_buddy` | ____ | ____ | ____ |
| `borrowed_brilliance` | ____ | ____ | ____ |
| `elemental_ecstasy` | ____ | ____ | ____ |
| `FILLER` (negative control) | ____ | ____ | ____ |

Plus two statements that are not per-card:

- **[USER] SLOT — the redesign trigger.** The register's rule is "do not use
  raw pick rate as the redesign trigger". What *is* the trigger, in terms of
  the columns in §6? Stated now or the grade is descriptive only.
- **[USER] SLOT — the filler's expected Δ.** A non-zero prediction for the
  filler is a prediction about deck dilution, and it is the number every other
  row is read against.

## 9. Grading procedure and stop conditions

**Blind.** The runner writes one report; grading compares it against §8's
committed table **without editing §8**. The predictions commit must exist
before the sweep is launched, and the sweep's report is not opened by the
author of the predictions before the grade is recorded.

**Order of operations:**
1. Countersign this packet (or revise it).
2. Land the §10 engineering prerequisites with their byte-identity pins;
   suite green.
3. [USER] commits §8's predictions — their own commit, nothing else in it.
4. Run the sweep at the pinned stamp. Report only; read nothing into it.
5. Blind grade against §8; the grade is its own commit.
6. Any design act (redesign, reprice, retire) is downstream of the grade and
   is [USER]'s.

**Stop conditions / tripwires — the run stops and re-registers if:**
- **S1.** Any of `RT/D/P/C` differs at launch from `RT9/D14/P6/C8`.
- **S2.** The `force_cards=None` byte-identity pin (§10) fails — the control
  arm is then not an anchor and nothing in the report is comparable to the
  roster table.
- **S3.** The staged `EB-43` / DRAFTER 15 change has landed. The R121 order
  places D15 at step (5), after blind-first grading of the payoff-reach
  sprint; a sweep run across that landing is a sweep run in two worlds.
- **S4.** Compliance (§6.3) collapses — the forced copy fails to survive to
  the final deck in a large share of runs, or the control arm's natural
  acquisition of `X` is so common that ITT cannot separate the arms. Either
  makes Δ an attenuated estimate of nothing in particular. The report says
  so, the grade is recorded as **underpowered by contamination, not null**,
  and any re-run is a new registration.
- **S5.** A null read at the registered `N` is graded as **"no move larger
  than the §7 MDE"** — never as "no effect". The MDE is quoted with it.

## 10. Engineering prerequisites (before execution, after countersign)

1. `force_cards` on `model.run_one` / `run_many` / `_setup_run` / `Cell`,
   applied at the end of `_setup_run` (§2.2), default `None`.
2. A test pinning `force_cards=None` as element-for-element identical to the
   pre-seam batch — the house `grant_relics` / `grant_potions` / `slot_mode`
   pattern, and the precondition for S2.
3. A test that a forced id appears in `RunResult.deck_ids` at run start and
   that run-start RNG consumption is unchanged by the injection.
4. `tier05/exp_eb17p_forced_copy.py` — the sweep script: one control arm, one
   treated arm per §5 row, `cells.print_header` stamp, the §6 columns,
   McNemar + paired bootstrap on its own stream.
5. Pairing helpers (`mcnemar_exact`, paired bootstrap) belong in
   `tier05/stats.py`, the repo's one home for this arithmetic — not
   hand-rolled in the experiment script, which is how five `_percentile`
   copies happened.

None of the five touches `tier05/draft.py`, `tier0/constants.py`'s drafter
block, or any frozen calibration surface.

## 11. Mechanism probe (throwaway, excluded, numberless)

To settle "is deck-injection implementable without a drafter change", a
scratchpad probe monkeypatched `model._setup_run` to append a card id after
run-start relic effects and ran a handful of `klee/reaction` runs on seeds
`424242 …` — **excluded from §4 by construction**. What it established, and
the only thing quoted from it: **the harness executes.** The control path is
reproducible and is restored unchanged after unpatching; the treated arm runs;
the injected id is present in the treated decks when pooled with its upgraded
form; and tier-0.5 `fight_stats` feed `card_flow_profile` unchanged (§6.5's
D4 confirmation). **No winrate, no rate, no count from that probe appears in
this packet, and none was recorded.**

The probe is also where §5.2 (the `X+` rewrite) and §2.2 (the RNG-consuming
relic pickups) were found rather than assumed.

## 12. Known limits, declared

- **ITT, not per-protocol** (§2.3). A removed or upgraded copy stays in its
  assigned arm.
- **Deck dilution is confounded with the card** without the filler arm (§5.1);
  with it, dilution is measured, not assumed away.
- **One cell.** `klee/reaction`, `assigned`, `hunter`, realistic. Nothing here
  generalises to another plan, another route, or the adaptive policy; a
  robustness arm in another plan is a separate registration.
- **One seat.** The sim models one seat; nothing about co-op is measurable
  here.
- **The shipped within-arm split is not this.** §6.5's `card_flow` columns are
  descriptive companions to Δ, and the instrument's own refusal
  (`metrics.py:960-967`) stands.

---

## Countersign line — one word, [USER]: COUNTERSIGN / REVISE / DECLINE

`__________`

Countersign additionally requires: §5.1 filler, §7 `N` and cost ceiling, and
§8's predictions as their own commit before the sweep launches.

— drafted 2026-08-08, branch `eb17p-registration`. Zero design authority
exercised; every threshold, direction and taste call is a slot above.
