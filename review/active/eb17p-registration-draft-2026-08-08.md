# EB-17p — force-first-copy PAIRED winrate: pre-registration (COUNTERSIGNED)

> **Lifecycle: COUNTERSIGNED by [USER] on 2026-08-10, with an addendum.**
> The addendum is §6.1b: the report must also compare each card against the
> filler arm, pair by pair. [USER] also accepted `N = 2400` and chose the
> filler (§5.1).
>
> **RUN AND GRADED, 2026-08-10.** Every slot was filled and §8's predictions
> were committed on their own before any seed in the registered range was
> run. The sweep then ran at the pinned stamp and was graded blind against
> them. **The results and the grade are §13, and §1–§12 are the packet as it
> stood before the read** — they were not edited to fit the outcome. The
> mechanism probe in §11 ran on a THROWAWAY seed set that §4 excludes, and no
> number from it appears anywhere in this packet.
>
> One read of registered seeds happened before the sweep and is declared in
> §11.1.

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
| **`kaboom`** | "Kaboom!" | basic | 1 | **deck-size negative control (§5.1)** |

**5.1 The filler arm (negative control) — FILLED, [USER], 2026-08-10.** Every
treated arm adds a card, so every treated arm also *dilutes* the deck by one.
Without a filler arm, dilution and card effect are confounded and a null read
is unreadable. The filler has to be a card whose effect is already understood
and whose value is not what the sweep is about, because picking it is picking
the baseline every other row is read against.

> **FILLER = `kaboom`** — a duplicate of Klee's own starting Strike, the
> §5.1 candidate, chosen by [USER] on 2026-08-10.

`kaboom` ("Kaboom!", basic, cost 1) is Klee's basic Attack and appears four
times in her printed starter (`tier0/content/characters/klee.yaml:45`), one of
which the run-start randomiser replaces. Forcing a fifth copy therefore adds
nothing the deck did not already hold — it changes the deck's *size* and its
*ratio of basics to everything else*, and nothing else. That is exactly the
quantity the other four rows need held up beside them.

A test pins this so it cannot rot: if Klee's starter ever stops containing
`kaboom`, the negative control has quietly become a real card and
`tier05/tests/test_eb17p_force_cards.py` fails.

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

### 6.1b Co-primary (Q1, addendum) — card versus filler

**Added by [USER] on countersign, 2026-08-10.** For each swept card `X` other
than the filler itself:

`delta_vs_filler(X) = winrate(forced(X)) − winrate(forced(FILLER))`

paired by seed index, over the same `N` pairs, using the same machinery as
§6.1: exact McNemar on the discordant pairs for the test, a paired bootstrap
on its own stream for the interval, and the discordant and concordant counts
printed beside the delta.

**Why it is a co-primary and not a secondary.** §6.1 answers "does adding this
card change the run", and every treated arm's answer to that folds in one
extra card of dilution. §6.1b answers the question a redesign actually turns
on: "is this card worth its slot, compared with a card that does nothing new".
Neither question subsumes the other, so both are graded, and neither may be
dropped after the read because the other was more flattering.

**Read the filler row first.** The filler's own §6.1 delta against the control
is the size of pure dilution in this cell. Every §6.1b number is that
subtraction already performed, pair by pair; the filler's §6.1 row is what
tells a reader whether the subtraction was large or negligible in the first
place.

**What this contrast does NOT inherit.** §2.2's byte-identity guarantee is
about the *control* arm: `force_cards=None` is provably the world we already
have, pinned by the S2 test, which is what lets a §6.1 number be set beside
the roster-anchor table. In §6.1b **both arms are treated**, so neither of
them is that world. Two consequences, stated now:

- A §6.1b delta is **internally valid and externally unanchored**. It is a
  clean comparison of two decks, and it may not be quoted against any
  archived winrate, because neither of its arms is a world any archived
  number came from.
- S2 does not certify it. If S2 fires, §6.1 is void; §6.1b would survive as
  a comparison of two treated arms, and the report must say so rather than
  presenting a surviving number as if the tripwire had not fired.

The pairing itself does carry over. Both arms inject at the end of run start,
which consumes no randomness, so `forced(X)` and `forced(FILLER)` enter floor
1 having drawn identically from the run stream — same map, same relics, same
gold, one card different. Pairing by seed index is therefore as legitimate
here as in §6.1. What is weaker is not the pairing but the **anchoring**.

**No multiplicity correction is registered**, for either contrast. Five cards
times two contrasts is ten readings, and the honest reason there is no
adjustment is that the grade is not a hunt for a significant row: each card is
graded against a direction and a threshold [USER] wrote down in §8 before any
number existed. A row that was not predicted, and turns up significant, is a
hypothesis for a new registration — not a finding. Any change to that stance
is a re-registration.

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

> **`N` = 2,400 pairs per card** — the registered default, accepted by [USER]
> on 2026-08-10. 2,400 runs on each of the six arms; 14,400 runs in total.

### 7.1 Sizing the co-primary (§6.1b), honestly

The table above sizes **card versus control**. The card-versus-filler contrast
is a different comparison and gets its own statement rather than borrowing
that one.

**What carries over.** The estimator, the pairing and the arithmetic are
identical: `SE(Δ) = sqrt(d / N)` with `d` the discordant rate, and the same
`2.80 × SE` minimum detectable effect at two-sided α = 0.05 and power 0.80.
`N` is the same 2,400 pairs, because §6.1b reuses the same runs — it costs no
extra sim time.

**What does not carry over is the lower bound on `d`.** The `d ≈ 0.05`
column above is the optimistic half of a bracket, and it is optimistic because
the arms are strongly correlated pair by pair. For card-versus-control there
is a structural reason to expect that correlation: one arm is the other arm's
deck with a card added, so a great many seeds resolve identically in both.
For card-versus-filler, the two decks differ by a **substitution** — `X` in
one slot, `kaboom` in the other — and the packet has nothing that pins how
correlated two treated arms are. Asserting the optimistic column here would be
asserting a number the design does not buy.

So the registered statement for §6.1b is the conservative one only:

| pairs `N` | MDE at `d = 0.11` (conservative) | MDE if the arms are as correlated as §7 hopes |
|---|---|---|
| **2,400** | **1.9 pp** | not registered — see below |

**At `N = 2,400`, §6.1b resolves a card-versus-filler move of about 1.9
percentage points or larger.** Anything smaller than that is inside the noise
this design can see, and a §6.1b null is graded as "no move larger than 1.9
pp", never as "no difference" (§9, S5).

**The realised `d` is reported, not assumed.** The discordant counts `b` and
`c` are printed on every §6.1b row, so a reader can compute the achieved
resolution from the output instead of trusting the bracket. That number is a
*description* of the sweep, and it may not be used to re-plan `N` afterwards —
that is optional stopping, and §9's S4 is the only route from a disappointing
read to more data.

**Limitation stated plainly.** Because the correlation between two treated
arms is unknown before the read, `1.9 pp` is a ceiling on what §6.1b can
resolve, not an estimate of what it will resolve. If the arms turn out to be
strongly correlated the real resolution is better than 1.9 pp; the packet
declines to claim that in advance.

> **COST CEILING = 4 hours wall-clock, stop-and-report** — confirmed by
> [USER] on 2026-08-10.

Stop-and-report means what it says: if the sweep is still running at four
hours it **stops and reports what it has**, and the partial result is graded
as partial. It is not extended, and the arms that finished are not quietly
promoted to the whole answer. A stop at the ceiling names how many pairs each
arm actually completed, and any grade drawn from fewer than the registered
`N = 2,400` pairs quotes its own realised MDE rather than §7's.

This was the last open slot in the packet.

## 8. Predictions — [USER], before any number is read

Per EXPERIMENTS ("pre-registered from design intent … never revised against
the playtest that grades it") and the R121 precedent that predictions are
authored design-side and appended **as their own commit before any
measurement runs**. Drafting them here would be exactly the retro-fit the
payoff-reach authority forbids.

For **each** swept card, [USER] states a direction and a threshold — for
**both** co-primaries, because §6.1b is graded and an ungraded co-primary is
just a number nobody committed to:

**WRITTEN BY [USER], 2026-08-10, before any seed in the registered range was
run.** [USER] adopted an external GPT recommendation for these directions.
The rows below are [USER]'s statements put into the table's columns; the exact
words are in this commit's message, which is where [USER]'s verbatim text
lives.

| card | §6.1 sign of Δ vs control | threshold (pp) that counts as a real move | §6.1b sign of Δ vs filler | confidence |
|---|---|---|---|---|
| `friendly_visit` | **positive** | **+2 pp** — expected to reach or exceed it | **positive**, at or above +2 pp | "likely" |
| `study_buddy` | **positive** | **+2 pp** — expected to land *below* it | **positive**, below +2 pp | "probably" |
| `borrowed_brilliance` | **positive** | **+2 pp** — expected to reach or exceed it | **positive**, at or above +2 pp | "likely" |
| `elemental_ecstasy` ("Sweet Dreams") | **null** | **±2 pp** — expected to land inside the band | **null to slightly positive**, inside ±2 pp | stated flatly |
| `kaboom` (filler, negative control) | **near-null, slightly negative** | **±2 pp** — expected to land inside the band, on the negative side | — (it is the baseline) | "probably" |

**How the §6.1b column was derived, and by whom.** [USER] wrote directions
against the control and one statement about the filler ("near-null, probably
slightly negative through dilution"). The filler column follows from those two
by arithmetic, not by a second judgement: if the filler's own Δ is near zero
or slightly negative, then a card's Δ against the filler is its Δ against the
control plus a small non-negative amount. So every direction carries over, and
the two "at least +2 pp" cards keep their threshold. This derivation is
recorded here so a grader can see that the §6.1b column is not an independent
prediction that could be scored as a separate success.

**One arm, two names.** "Sweet Dreams" and "Elemental Ecstasy" are the same
card. The sheet renamed it for display on 2026-07-20 and kept the id
(`docs/klee-cards.yaml:168-172`: *"ID stays elemental_ecstasy. Future greps:
try BOTH names."*). There is one registered arm here, not two.

### 8.1 The redesign trigger — [USER], 2026-08-10

A card is a **redesign candidate** if **either** clause holds:

- **(a)** the filler-adjusted result is confidently below −2 percentage
  points; **or**
- **(b)** the card performs no better than filler while being dead in hand at
  least 25% of the time.

**Bound to §6's columns, so the grade is mechanical:**

| clause | the column it reads | the reading |
|---|---|---|
| (a) | §6.1b `delta_vs_filler(X)` and its paired-bootstrap interval | fires when the interval's **upper** bound is below −2 pp — that is what "confidently" means here, and it is a stricter test than the point estimate alone |
| (b), first half | §6.1b `delta_vs_filler(X)` | fires when the delta is at or below zero |
| (b), second half | §6.5 `dead_in_hand_rate`, **family-pooled** (`X` + `X+`), over the forced arm | fires at 0.25 or above |

`dead_in_hand_rate` is `dead_in_hand / draws`: of the times the card was
drawn, the share that ended a combat unplayed in hand. "At least 25% of the
time" is therefore read against **draws**, not against fights or runs. The
family-pooled figure is the one that counts, per §5.2, and the sweep script
prints it as its own line so the number is read rather than reconstructed.

**Both clauses are expressible in columns this sweep already measures**, which
is what makes the trigger gradeable as registered. Checked before these
predictions were committed.

**The trigger names a candidate, not a verdict.** Firing it does not redesign
anything. Whether to redesign, reprice or retire a card is a design act,
downstream of the grade, and [USER]'s (§1, "Not asked here").

**A trigger must be expressible in §6's columns.** If a proposed trigger names
a quantity this sweep does not measure, it cannot be graded as registered, and
the fix is a new column in a re-registration — never a metric quietly added at
grading time.

## 9. Grading procedure and stop conditions

**Blind.** The runner writes one report; grading compares it against §8's
committed table **without editing §8**. The predictions commit must exist
before the sweep is launched, and the sweep's report is not opened by the
author of the predictions before the grade is recorded.

**Order of operations:**
1. Countersign this packet. **DONE — [USER], 2026-08-10**, with the §6.1b
   addendum.
2. Land the §10 engineering prerequisites with their byte-identity pins,
   suite green. **DONE.**
3. [USER] fills the §7 cost ceiling. **DONE — [USER], 2026-08-10.** 4 hours
   wall-clock, stop-and-report.
4. §8's predictions are committed — their own commit, nothing else in it.
   **DONE — [USER], 2026-08-10.**
5. Run the sweep at the pinned stamp. Report only; read nothing into it.
6. Blind grade against §8; the grade is its own commit.
7. Any design act (redesign, reprice, retire) is downstream of the grade and
   is [USER]'s.

**Order of reading, at the grade.** The rows are read in this order and no
other, because reading them in any other order lets one number colour the
next:

1. The **compliance census** (§6.3), per card. If a card's assignment did not
   survive, or the control arm drafted it constantly, that card's grade is
   settled here as *underpowered by contamination* and its deltas are not
   graded at all (S4).
2. The **filler's §6.1 row** — the size of pure dilution in this cell.
3. Each card's **§6.1** delta against control, versus its §8 prediction.
4. Each card's **§6.1b** delta against filler, versus its §8 prediction.
5. The §6.2 secondaries, the §6.4 subgroup and the §6.5 card-flow columns, as
   description.

A card is graded **PREDICTED** only if both co-primaries land as §8 said they
would. One right and one wrong is graded **SPLIT**, with which half went wrong
named — not rounded to whichever half agreed.

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
  than the §7 MDE"** — never as "no effect". The MDE is quoted with it, and
  the two co-primaries quote different ones: §6.1 quotes the §7 table's
  bracket, §6.1b quotes the single conservative figure in §7.1 (1.9 pp at
  `N = 2,400`).

## 10. Engineering prerequisites — LANDED 2026-08-10

All five are built and the suite is green (2,401 passed, 12 xfailed). The
seam and its pins live in `tier05/model.py`, `tier05/cells.py`,
`tier05/stats.py`, `tier05/exp_eb17p_forced_copy.py`,
`tier05/tests/test_eb17p_force_cards.py` and
`tier05/tests/test_stats_paired.py`.

One addition the draft did not ask for, made because writing the sweep script
exposed the risk: the script takes a `--smoke` flag that moves every arm onto
the §4-excluded seed base (`424242`). The registered base seed is 11, and
"just check it runs" is exactly how a registered range gets read before the
predictions exist. The safe path is now the flagged one, and the flag prints
a banner saying nothing below it may be quoted.

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

### 11.1 Declared contamination — a 12-pair read on registered seeds

**What happened.** On 2026-08-10, while building the §10 sweep script, the
first "does it run" check was executed with the script's default seed base —
which is the **registered** base, 11. It ran 12 pairs per arm, seeds 11–22,
and its output (winrates, deltas, McNemar counts, compliance and card-flow
rows) was displayed to the engineer who wrote the script.

**Recorded here rather than anywhere else.** No number from that check appears
in any commit, any file, or any part of this packet. It is disclosed because a
grader reading this packet later has no other way to learn of it, and an
undisclosed read is the thing pre-registration exists to prevent.

**Why it does not contaminate the predictions.** §8's predictions and §8.1's
trigger are [USER]'s, and [USER] supplied them in full — in the words quoted
in their commit message — **before** any code in this session ran. They were
fixed before the read and were transcribed unchanged, so no retro-fit was
possible. The read cannot have shaped a prediction that already existed.

**Why it does not contaminate the sweep.** Seeds 11–22 are 12 of the 2,400
registered pairs and will be re-run as part of the full sweep at the pinned
stamp. Nothing about them is excluded, adjusted or re-rolled; excluding them
now would be a post-hoc change to §4's registered range, which would be worse
than the disclosure.

**What changed as a result.** The sweep script gained a `--smoke` flag that
moves every arm onto the §4-excluded seed base (`424242`) and prints a banner
saying nothing below it may be quoted. Every subsequent check ran under it.
The safe path is now the flagged one; the registered range takes a deliberate
act to touch.

**Open to [USER].** Whether this read is material to the grade is [USER]'s
call, not the engineer's. If it is, the remedy is a re-registration of §4's
seed range, not an edit to this section.

**RULED.** [USER] ruled the disclosure **immaterial**, 2026-08-10 (R173); the
sweep proceeded on the registered seed range unchanged.

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
- **The filler contrast is unanchored** (§6.1b). Both of its arms are treated,
  so a §6.1b delta may not be set beside any archived winrate.
- **Two copies look alike.** When a treated run ends holding two copies of the
  swept family, nothing in the record distinguishes the forced copy from a
  drafted one. §6.3's compliance columns are therefore counts of the
  **family**, not of the assigned copy, and are labelled that way in the
  output.

---

## Countersign line — one word, [USER]: COUNTERSIGN / REVISE / DECLINE

`COUNTERSIGN` — [USER], 2026-08-10, with the §6.1b addendum.

Filled on countersign: §5.1 filler (`kaboom`) and §7 `N` (2,400). §8's
predictions and the §8.1 trigger were committed on their own on 2026-08-10.
The §7 cost ceiling was confirmed the same day. **No slot is open; the packet
is cleared to launch.**

— drafted 2026-08-08, branch `eb17p-registration`; amended 2026-08-10 on
branch `sitting-prep-2026-08-08` to record the countersign, fill every slot,
and add the §6.1b co-primary; run and graded the same day. Zero design
authority exercised: every threshold, direction and taste call is [USER]'s,
and the grade in §13 reads the registered columns and stops there. The
redesign trigger fired for two cards; what to do about that is [USER]'s.

---

## 13. Results and grade — sweep run 2026-08-10

**§8 was not edited to produce this section.** The predictions were committed
in `eb67706` on 2026-08-10, before the sweep ran; this section compares the
sweep's output against them and changes nothing above.

**Run.** `PYTHONPATH=. python -m tier05.exp_eb17p_forced_copy --runs 2400
--jobs 0`, at `RT9/D14/P6/C8`, seed base 11, 2,400 pairs on each of six arms,
14,400 runs. Wall clock **2 minutes 57 seconds** against a 4-hour ceiling, so
the stop-and-report rule never engaged and every arm completed its full `N`.
The raw stamped report is `review/active/eb17p-results-2026-08-10.txt`.

**Tripwires, checked at launch.** S1 clear — the stamp was `RT9/D14/P6/C8`, as
pinned. S2 clear — the `force_cards=None` byte-identity pin passed with the
full suite (2,411 passed, 12 xfailed). S3 clear — `DRAFTER_VERSION` was 14, so
the staged D15 change had not landed. S4 is read per card below.

### 13.1 Compliance first (§6.3), because it decides what may be graded

| card | forced family held at end | upgraded | removed at rest | control acquired it on its own |
|---|---|---|---|---|
| `friendly_visit` | 99.04% | 32.83% | 0.00% | 26.04% |
| `study_buddy` | 98.75% | 74.42% | 0.00% | 29.25% |
| `borrowed_brilliance` | 98.79% | 26.92% | 0.00% | 3.96% |
| `elemental_ecstasy` | 97.50% | 26.46% | 0.00% | 15.08% |
| `kaboom` (filler) | 100.00% | 32.42% | 1.58% | 99.92% |

**S4 did not fire for any of the four cards.** Assignment survived to the
final deck in 97.5% of runs or better everywhere, and the control arm's own
acquisition rate — 4% to 29% — attenuates the contrast without collapsing it.

**The filler's two odd-looking columns are structural, not alarming.**
`kaboom` is a starter card, so "the control arm acquired it on its own" is
99.92% by construction: every Klee deck already holds it. For the filler the
compliance question is not *whether* the family is present but *how many
copies*, and the treated arm ends with a mean of 3.92 copies. §6.4's
clean-pairs subgroup for `kaboom` is `n = 2` for the same reason and carries
no information; it is reported and disregarded. Neither is an S4 event.

### 13.2 The filler's row (§6.1) — the size of pure dilution

**`kaboom`: Δ = −1.42 pp**, 95% paired bootstrap [−2.54, −0.25], McNemar
b = 86, c = 120, p = 0.021. Control winrate 6.83% (164/2400); filler arm 5.42%
(130/2400).

**Adding one blank card to a Klee reaction deck costs about 1.4 points of
winrate.** That is what every §6.1 row below has folded into it, and it is why
§6.1b exists.

### 13.3 The primary rows (§6.1, versus control)

| card | Δ vs control | 95% interval | McNemar b/c | p |
|---|---|---|---|---|
| `friendly_visit` | **+3.04 pp** | [+1.71, +4.38] | 173 / 100 | <0.0001 |
| `study_buddy` | **+0.75 pp** | [−0.54, +2.00] | 132 / 114 | 0.278 |
| `borrowed_brilliance` | **−1.58 pp** | [−2.75, −0.42] | 83 / 121 | 0.009 |
| `elemental_ecstasy` | **−1.62 pp** | [−2.75, −0.46] | 82 / 121 | 0.008 |
| `kaboom` (filler) | **−1.42 pp** | [−2.54, −0.25] | 86 / 120 | 0.021 |

### 13.4 The co-primary rows (§6.1b, versus filler)

| card | Δ vs filler | 95% interval | McNemar b/c | p |
|---|---|---|---|---|
| `friendly_visit` | **+4.46 pp** | [+3.25, +5.67] | 164 / 57 | <0.0001 |
| `study_buddy` | **+2.17 pp** | [+1.08, +3.25] | 115 / 63 | 0.0001 |
| `borrowed_brilliance` | **−0.17 pp** | [−1.08, +0.75] | 59 / 63 | 0.786 |
| `elemental_ecstasy` | **−0.21 pp** | [−1.12, +0.67] | 59 / 64 | 0.719 |

**Read together, §6.1 and §6.1b say different things about the same cards, and
the difference is the dilution.** Two cards that look actively harmful against
the control — `borrowed_brilliance` and `elemental_ecstasy`, both about
−1.6 pp — turn out to be indistinguishable from a blank card once dilution is
taken out. They are not hurting the deck; they are *doing nothing*, and doing
nothing costs 1.4 points. That distinction is the whole reason [USER] added
the co-primary on countersign, and it changes the design reading of two of the
four cards.

### 13.5 Achieved resolution, and a note on the §7.1 hedge

`d` is the realised discordant rate; the MDE is `2.80 × sqrt(d/N)` at
`N = 2,400`, computed from the sweep's own counts rather than from §7's
bracket.

| contrast | `d` | achieved MDE |
|---|---|---|
| `friendly_visit` vs control | 0.114 | 1.93 pp |
| `study_buddy` vs control | 0.103 | 1.83 pp |
| `borrowed_brilliance` vs control | 0.085 | 1.67 pp |
| `elemental_ecstasy` vs control | 0.085 | 1.66 pp |
| `kaboom` vs control | 0.086 | 1.67 pp |
| `friendly_visit` vs filler | 0.092 | 1.73 pp |
| `study_buddy` vs filler | 0.074 | 1.56 pp |
| `borrowed_brilliance` vs filler | 0.051 | 1.29 pp |
| `elemental_ecstasy` vs filler | 0.051 | 1.29 pp |

**§7's bracket was right about the range and wrong about which contrast sat
where.** The card-versus-control rows landed near the *conservative* end
(`d ≈ 0.085–0.114` against a conservative bound of 0.11) — the pairing bought
almost nothing there. The card-versus-filler rows landed at or better than the
*optimistic* end (`d ≈ 0.051–0.092` against an optimistic bound of 0.05).

§7.1 declined to register the optimistic column for §6.1b on the grounds that
the correlation between two treated arms was unknown. That refusal was correct
as discipline and wrong as a guess: the contrast it declined to claim
resolution for is the one that resolved best. The registered ceiling of 1.9 pp
held for every row. Recorded here rather than corrected above, because a
sizing section is what was believed before the read.

### 13.6 The grade, against §8

`friendly_visit` predicted "positive, likely at least +2 pp".

- §6.1 **HIT** — +3.04 pp, positive, at or above the +2 pp threshold. The
  interval [+1.71, +4.38] does span +2, so "at least 2 pp" is the point
  estimate's verdict and not the interval's; direction and threshold are both
  as registered.
- §6.1b **HIT** — +4.46 pp, and here the whole interval clears +2.
- **Card grade: PREDICTED.**

`study_buddy` predicted "positive but probably below +2 points".

- §6.1 **HIT** — +0.75 pp, positive, below +2, exactly as registered. Flagged
  honestly: the interval [−0.54, +2.00] includes zero, so the sweep cannot
  establish that the card helps at all against the control. "Positive" is the
  observed sign, not a demonstrated one.
- §6.1b **MISS** — +2.17 pp, which is positive as predicted but **above** the
  +2 threshold the prediction placed it below. The interval [+1.08, +3.25]
  spans +2, so the miss is not decisive either.
- **Card grade: SPLIT** (§9's rule), with the missing half named: the
  magnitude against the filler, not the direction.

`borrowed_brilliance` predicted "positive, likely at least +2 points".

- §6.1 **MISS** — −1.58 pp. Wrong sign, and significantly so (p = 0.009). The
  prediction and the observation are about 3.6 pp apart.
- §6.1b **MISS** — −0.17 pp against a predicted +2 or better. The card is
  indistinguishable from a blank card.
- **Card grade: MISS**, on both co-primaries.

`elemental_ecstasy` ("Sweet Dreams") predicted "null, within ±2 points".

- §6.1 **HIT** — −1.62 pp, inside the ±2 band as registered. Flagged: it is
  significantly below zero (p = 0.008), so "null" is true as a band statement
  and not as a claim that nothing happened. What happened is dilution.
- §6.1b **HIT** — −0.21 pp, inside the band and essentially zero.
- **Card grade: PREDICTED.**

`kaboom` (filler) predicted "near-null, probably slightly negative through
dilution".

- §6.1 **HIT** — −1.42 pp: negative, inside ±2, and the mechanism named in the
  prediction is the one the number shows. Flagged: it is separable from zero
  (p = 0.021), so dilution is real and small rather than absent.
- **Card grade: PREDICTED.**

**Tally: 3 PREDICTED, 1 SPLIT, 1 MISS.** The one MISS is
`borrowed_brilliance`, and it is the largest error in the table.

### 13.7 The redesign trigger (§8.1)

Read exactly as §8.1 binds it, and evaluated per card.

**Clause (a) — §6.1b interval's upper bound below −2 pp: fires for nobody.**
The lowest upper bound in the table is `elemental_ecstasy`'s at +0.67. No card
is confidently worse than the filler.

**Clause (b) — Δ vs filler at or below zero AND family-pooled dead-in-hand at
or above 25%:**

| card | Δ vs filler ≤ 0 | pooled dead-in-hand | fires? |
|---|---|---|---|
| `friendly_visit` | no (+4.46) | 45.87% | **no** |
| `study_buddy` | no (+2.17) | 50.63% | **no** |
| `borrowed_brilliance` | **yes** (−0.17) | **94.95%** | **YES** |
| `elemental_ecstasy` | **yes** (−0.21) | **87.07%** | **YES** |
| `kaboom` (filler) | not applicable — it is the baseline | 37.24% | n/a |

**The trigger fires for `borrowed_brilliance` and `elemental_ecstasy`.**

Both fire on clause (b): they perform no better than a blank card while
sitting dead in hand the overwhelming majority of the times they are drawn.
Neither fires on clause (a) — neither is actively harmful once dilution is
removed. The distinction matters for whatever comes next: the finding is
"these cards do nothing", not "these cards are traps".

**The trigger names a candidate, not a verdict** (§8.1). Whether to redesign,
reprice or retire either card is a design act, downstream of this grade, and
[USER]'s.

### 13.8 One observation that is not a grade, flagged for triage

`borrowed_brilliance` in its **un-upgraded** form was drawn **40,396 times and
played zero times** — 0 of 28,149 combats in which its first copy was drawn.
Its upgraded form, which adds `draw 1`, plays 30% of the time. No other card
in the sweep shows anything like this: the bare forms of `study_buddy` and
`elemental_ecstasy` play 35% and 10% of the time respectively.

An exact zero across forty thousand draws is not a preference, it is a
categorical refusal. The engine op is not the cause — `copy_companion_in_hand`
returns harmlessly when no companion is in hand
(`tier0/engine/effects.py:1867`), so the card is playable and merely does
nothing in that case. Whether the pilot never values it, or never has a
companion in hand when it could, this sweep cannot separate.

**This matters for the grade of that one card.** Its MISS may be measuring a
pilot-valuation fact rather than the card's design, and a redesign argued from
this row alone would be arguing from an instrument reading, not a card
reading. Recorded here, deliberately not filed and deliberately not diagnosed
further: it is an audit finding, and triaging it is not this grade's job.
