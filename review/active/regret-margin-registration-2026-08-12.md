# The regret margins — pre-registration (DRAFT, awaiting countersign)

> **Status: DRAFT. Nothing here has been run.** No number in this document was
> measured, and no number in it is proposed as a threshold. The measurement
> described below produces evidence; what — if anything — becomes a margin is
> [USER]'s call at QUEUE `M13`, after this packet is countersigned and the
> run is graded.
>
> **This packet does not bless `+1.0`.** R164 (2026-08-10) ruled that the
> measurement is pre-registered and that `+1.0` is *not* ratified in the
> meantime. Nothing here changes that. The `1.0` currently in the code is
> reported where it is relevant, always labelled as an unratified literal.
>
> The predictions in §7 are deliberately blank — they are [USER]'s to fill in
> before any seed is run.

**Plain English is a standing requirement for this packet.** Every term is
glossed where it first appears, and nothing assumes you have read the code.

---

## 1. What is unsettled

There are two numbers in the tree that decide when a decision counts as a
*regret*, and neither has a written-down reason for being what it is.

A **regret** here is a bookkeeping idea, not a feeling. After a run finishes,
the sim goes back and re-scores decisions the automatic player made, using
what it knows at the end. If some option it passed over now scores better than
the one it took, the difference between the two scores is the **gap**. A gap
big enough to clear a **margin** is filed as a regret. The margin is the
"big enough" line, and it is the thing with no derivation.

| where | name | value | what it thresholds |
|---|---|---|---|
| `tier05/run_metrics.py` | `ROUTE_REGRET_MARGIN` | `1.0` | route decisions — which lane of the map to walk |
| `tier05/draft.py` | `DRAFT_REGRET_MARGIN` | `1.0` | card-reward screens — which card to take |

A naming note, so the table matches what `M13` was filed against: until
2026-08-12 the draft one had no name at all — it was a bare `+ 1.0` inside the
comparison. `EB-72` gave it one so that the margin-free half of the drafter's
regret could exist as its own function. **Naming a literal derives nothing and
ratifies nothing**; the value is untouched and the test that pins it at its
boundary is untouched.

Both were literals typed into the code. The route one was written as a
deliberate analogy of the draft one, and the draft one was never derived from
anything at all. The route constant's own comment says so plainly: it is "a
literal analogy of a literal", and the two are not even in the same units — a
card score is roughly one card's worth of printed damage or Block, while a
path value is a sum of room desirability over sixteen floors, so a "point" is
a far smaller relative gap on the route side than on the draft side.

**What reads these numbers today: nothing that decides anything.** The counts
they produce (`regretted`, `regret_rate`, `regretted_decisions`) are printed
in the run report and in the A/B summary and are read by no gate, no lint, no
acceptance band and no ruling. That is a fact about the current tree, and it
is stated here because it bounds how urgent this is — and because one of the
options in §6 is to leave it that way.

## 2. What can now be read, and what could not be before

Until 2026-08-12 there was nothing to pre-register *against*, which is why
R164 ordered a printer first. Three things were in the way:

- The pooled route-regret summary emits **no percentiles**, on purpose and
  correctly: it pools one summary per act, and a median of act medians is not
  a median. Its own docstring told any caller wanting the real distribution to
  go and sample the gaps itself.
- The run report prints **no route-regret block at all**, so the route
  sampler's output never reached a human page.
- The drafter's regret function returned **an integer**. It computed the gaps
  and threw them away.

`tools/regret_distribution.py` (BACKLOG `EB-72`, leg 1) fixes all three. It
re-prices a finished cohort of runs on the same dedicated random streams the
live run used, and prints, for both numbers:

- the **margin-free distribution** of gaps — mean, p50, p90, max, plus a full
  percentile ladder, the minimum, and how many gaps are exactly zero;
- the same distribution **conditioned on being positive**, labelled as a
  different denominator and never merged with the first;
- an **accounting line** — how many decisions there were, how many were forced
  (a floor with only one exit is not a choice and is excluded), and how many
  were sampled;
- a **cross-check**: the tool's own arithmetic against the summaries the runs
  already carry. If that line is not zero, the tool is describing a pipeline
  nobody runs, and the read is void (§5, tripwire T1).

The collection loops behind it (`route_regret_gaps`, `draft_regret_gaps`) take
no margin argument at all — structurally, not just by convention — which is
what makes the distribution quotable while the margin is unratified.

**Two properties of the route number you need before reading any of it.**

1. **In the deciding state the route gap is exactly zero, by construction.**
   The route planner picks the highest-valued lane, so at the moment of choice
   nothing can beat the pick. Every positive route gap is therefore produced
   by *hindsight* — the lane was worth taking while the run was healthy and
   was not worth it by the time the run arrived. A large route regret is not
   automatically a bad planner; it can equally be a run whose state moved a
   lot.
2. **The distribution is heavily zero-inflated.** Most sampled decisions come
   back at 0.0. That is the instrument working, not a fault — but it means a
   percentile below the zero share is simply 0.0, which matters a great deal
   in §6.

## 3. One window, one world

**The registered world is `RT10/D14/P7/C9`, `C9` including the X7/X8 rarity
erratum.** A run of this measurement that does not report exactly that stamp
is not this registration's measurement (R68).

What is inside the window: everything currently in HEAD — the restored slot-2
rarity floor and the X7/X8 promotions (`C9`), the R82 enchant events (`RT10`),
the payoff-reach drafter pin (`D14`), and the R176 pilot change (`P7`).

**Nothing in the `EB-72` work moves the world**, and this is worth stating
because a measurement instrument that changes what it measures is worthless:

- The two gap collectors are **splits of existing loops**, not new arithmetic.
  On the ROUTE side the summary it feeds is byte-identical to what that loop
  produced before, which the suite pins. On the DRAFT side the split
  re-associated the comparison (`v > picked + 1.0` became
  `(max - picked) > 1.0`), which differs at the exact-1.0 float boundary — see
  §8. Neither collector feeds anything a run reads.
- Both re-price **finished runs**, after the fact, on **dedicated random
  streams** (the drafter's and the route sampler's own offsets). No run, deck,
  encounter, shop or fight moves because a road not taken got priced
  afterwards. This is the same reading the sample-rate constant already took
  when it was homed, and the same reason it was not a version bump.
- The printer is a **tool**, imported by nothing the sim runs.

So this measurement can be taken on the world as it stands, with no bump and
no re-baseline, and the numbers it produces are comparable to anything else
stamped `RT10/D14/P7/C9`.

**One consequence worth naming.** Because the read is post-hoc and read-only,
**every candidate margin can be evaluated on one set of runs.** The gaps do
not change when the margin does. There is no re-running per candidate and
therefore no temptation to fish across repeated runs — a rare piece of luck in
this repo's measurement history, and it is why §5's cost is small.

## 4. Questions

**Q1 — what does the gap distribution actually look like?** For each arm, the
margin-free read of both numbers: mean, p50, p90, max, the ladder, the zero
share, and the size of the sample it rests on. This is the number R164 already
declared quotable, and it has never been printed.

**Q2 — how much does the *counted* regret rate depend on where the line is
drawn?** The rate as a function of the margin, across the observed range. If
the rate is flat over a wide band of candidate margins, the choice barely
matters; if it falls off a cliff, the current `1.0` is sitting somewhere
specific and it matters a lot which side. This is descriptive: it says how
sensitive the statistic is, not where the line belongs.

**Q3 — is the distribution a property of the pipeline or of the map?** The
same read under both route policies (`hunter` and `cautious`) and across three
characters. If the distributions are near-identical across arms, the number is
mostly describing the map generator, and a margin derived from any one arm
would travel. If they differ, a margin derived from one arm is a statement
about that arm only, and the packet has to say which.

**Q4 — do the two numbers belong on the same scale at all?** The route margin
was set by analogy to the draft margin. Q1's two blocks are in different units
and the analogy has never been checked. If the two distributions have very
different shapes, "the same 1.0" is two different strictnesses wearing one
number.

**Q5 — does the counted rate distinguish a worse pipeline from a better
one?** This is the instrument-validity question, and it is the one that
decides whether a margin is worth having. A regret rate that reads the same
for a deliberately bad decision-maker and for the shipped one is not measuring
decision quality. See §5's controls for what this costs.

**Not asked here.** What the margin should be, whether the current rate is
good or bad, and whether `regretted` / `regret_rate` should exist at all.
Those are [USER]'s, downstream of the grade.

## 5. What is measured, and with what

**Instrument.** `tools/regret_distribution.py`, at the commit this packet
lands in. It reports both numbers on one page; it applies no threshold to
anything except the one clearly-labelled line that reports what the in-tree
literal currently counts.

**Arms** (proposed — [USER]'s to confirm or change). Six cells, one read each:

| arm | character / plan | route policy | draft policy |
|---|---|---|---|
| A1 | `klee` / demolition | `hunter` | `assigned` |
| A2 | `furina` / salon | `hunter` | `assigned` |
| A3 | `kokomi` / priest | `hunter` | `assigned` |
| A4 | `klee` / demolition | `cautious` | `assigned` |
| A5 | `furina` / salon | `cautious` | `assigned` |
| A6 | `kokomi` / priest | `cautious` | `assigned` |

The three characters are the three roster members at their default plans —
the same three the shop cell runs, chosen because they are the arms this repo
already reads everything else on, not because of anything about regret. The
route-policy split is Q3's whole content: it is the only lever in the sim that
changes route decisions without changing anything else.

**n (proposed).** `RUNS = 600` per arm, which is the ratified cell's n and the
only run-count convention this repo has.

**The binding sample is not the run count**, and this is the number to argue
about if any: what the percentiles rest on is the count of *sampled decisions*,
which the printer reports on its accounting line. On the route side every
forked floor is sampled (the route sample rate is 1.0), so 600 runs yields
several thousand gaps per arm. On the draft side only one screen in ten is
sampled in-run, so the same 600 runs yields roughly a thousand. The printer's
`--draft-sample 1.0` re-prices **every** screen off the same finished runs, at
no cost but wall clock and at the price of the drafter cross-check (which
compares against a count taken at the 0.10 rate). **Proposed: run both — the
default-rate read for the cross-check, and the full-census read for the
distribution.** Which one Q1's answer is quoted from is a [USER] slot in §7.

**Seed policy.** `SEED = 11`, the ratified cell's seed, and runs are a pure
function of `seed + i`, so the range is `11 … 610` per arm. Two rules:

- **The registered range is run once.** Because every candidate margin is
  evaluated on the same finished runs (§3), there is no legitimate reason to
  re-run the range, and re-running it after seeing a result is exactly the
  failure this repo pre-registers to avoid.
- **Smoke runs use an excluded seed.** Any run made to check that the tool
  works uses `SEED = 424242`, is labelled as a smoke, and nothing from it may
  be quoted into the report or the grade. (Same device as the `EB-17p` packet's
  `--smoke` flag, and for the same reason.)

**Route.** All six arms walk the real 16-floor map at three acts — the world's
default, unchanged. `hunter` and `cautious` are the two shipped route
policies; nothing is added to that list for the primary arms.

**Controls.**

- **C1 — the deciding-state null (route, zero cost, already proven).** Priced
  in the state it chose in, the route sampler reads exactly zero. The suite
  pins this on sixty generated maps for both policies. It is the instrument's
  calibration: it says the sampler reports nothing when there is nothing to
  report, so every positive in Q1 is the hindsight shift and not a scoring
  drift between the planner and the re-scorer. **Reported in the packet, not
  re-run.**
- **C2 — the decision-time draft read (draft, cheap, property unverified).**
  The drafter's analogue of C1: re-score each screen in the deck as it stood
  *at that screen* rather than in the final deck. The drafter takes the best
  offer by that same scorer, so this should read at or near zero — but it is
  **not** guaranteed to, because the draft policy has two gates that can
  override the top score: a skip threshold (a screen whose best offer scores
  too low is declined, and a decline scores as zero), and a late-run "lean"
  gate that restricts what may be taken at all once the deck is large.
  Whether it reads zero
  is itself a finding, and it is the honest null for the draft side. **Costs a
  small addition to the printer; not built. In scope if [USER] wants it —
  §7 has the slot.**
- **C3 — a deliberately bad decision-maker (needed for Q5, not built).** Q5
  cannot be answered without an arm that decides badly on purpose: a route
  policy that walks a lane at random, and a draft policy that picks at random,
  each priced under the *shipped* value function. Both are a few lines, both
  are measurement-only, and both would have to be fenced so they can never be
  a shipped default. **Cost: roughly an hour of build plus one more pass of
  the six arms. Q5 is dropped if this is not authorised** — and dropping it is
  a legitimate outcome, since Q5 is the question that would justify having a
  margin at all rather than the question of what the margin is.

**Cost ceiling.** The whole primary read is cheap: on this machine 100 runs of
one arm takes about two seconds, so six arms at 600 runs, run twice (default
sample rate and full draft census), is a few minutes of wall clock and no
human time beyond reading the output. **Ceiling: one hour of wall clock for
the primary arms.** If the run has not finished inside that, it stops and
comes back to [USER] rather than being trimmed on the fly — a trimmed n is a
different registration. C3, if authorised, adds its own build time and a
second pass and is costed separately above.

**Tripwires.** T1–T3 are void conditions: if one fires, the read is not this
registration's measurement and nothing from it may be quoted or graded. T4–T6
are stop-and-return conditions, and two of them carry a number that is
[USER]'s to set in §7.

- **T1 — cross-check non-zero.** The printer's route cross-check must read
  `0 mismatched`, and the draft cross-check (at the default sample rate) must
  match the runs' own recorded counts. Any mismatch means the tool has drifted
  off the pipeline it claims to describe. **Void.**
- **T2 — wrong stamp.** Any arm whose report does not read `RT10/D14/P7/C9`.
  **Void.**
- **T3 — the range was re-run.** Any arm run more than once in the registered
  seed range, for any reason including a crash midway. A crashed arm is
  restarted only with this packet amended in writing first. **Void.**
- **T4 — the sample is too small to carry the tail.** A percentile in the
  upper ladder is meaningless on a handful of positive gaps. **[USER] slot in
  §7 sets the floor** on the count of *positive* gaps per arm below which the
  upper ladder is reported as unavailable rather than as a number.
- **T5 — the arms disagree.** If the arms' distributions differ enough that no
  single number describes them, then a margin derived from the pooled read is
  a number about no arm in particular, and the derivation stops and returns to
  [USER]. **[USER] slot in §7 sets what "differ enough" means**; the packet
  reports the spread either way.
- **T6 — the derivation would land at zero.** If the chosen percentile falls
  inside the zero mass (see §2, and §6's caveat), the derivation returns a
  margin of 0.0, at which *every* positive gap is a regret. That is a
  degenerate answer, not a small one. It stops and returns to [USER] rather
  than being rounded up to something that looks reasonable.

## 6. Derivation options — PROPOSED, none recommended

Four ways the evidence in §4 could be turned into a decision. They are laid
out at equal weight. **The packet takes no position among them**, including on
whether any margin should be set at all.

### Option A — an upper percentile of the observed regret (PROPOSED)

Set the margin to the *q*-th percentile of the gaps this measurement observes:
"a regret is a gap in the worst *q* of what we see".

**This option carries a circularity that has to be stated before it is
considered, not after.**

**A(i) — the margin filters the distribution it would be derived from.** The
phrase "observed regret" is ambiguous, and the three readings of it give three
different numbers off the very same run:

| reading | the sample the percentile is taken over | what is wrong with it |
|---|---|---|
| **A1 — all sampled decisions** | every sampled forked decision, zeros included | Heavily zero-inflated. Any *q* below the zero share returns **0.0**, so the derivation can hand back a margin at which every positive gap is a regret (tripwire T6). |
| **A2 — positive gaps only** | the same sample conditioned on being greater than zero | A percentile of the *regrets*, not of the decisions. The denominator is defined by the sampler's own clamp at zero, and it silently drops the decisions the pipeline got right — which is most of them. |
| **A3 — gaps already over the current margin** | the sample conditioned on exceeding `1.0` | **The strict circularity, and it must not be used.** The margin under review selects the subset, the subset produces the percentile, the percentile becomes the margin. Whatever number goes in comes back out, dressed as a measurement. |

**So a derivation under Option A is incomplete unless it names its pipeline in
writing**: which of A1/A2, which of the two numbers (route or draft, different
units — Q4), which arm or pool of arms, at which sample rate, under which
world stamp. A percentile with those unnamed is not reproducible and is not
countersignable.

**A(ii) — a percentile margin fixes its own answer.** If the margin is set at
percentile *q*, then the regret rate the statistic reports is `1 − q` **by
construction**, in this world and in every world, until the margin is
re-derived. A number that cannot move cannot detect anything. Under Option A
the regret rate stops being a reading of the pipeline and becomes a restatement
of the derivation. That is why Q5 exists: if the rate cannot separate a bad
decision-maker from a good one, a margin buys nothing whatever it is set to.

**A(iii) — it ages silently.** The distribution is a property of the current
drafter, route policy, pilot and world (`RT/D/P/C`). A margin derived from
today's distribution and left in place is measuring a pipeline that no longer
exists the moment any of those bumps. If Option A is chosen, it needs a
re-derivation rule attached — on which stamp components, how often — or it
becomes a second undated literal, which is exactly the state `M13` opened to
fix.

### Option B — separation from a deliberately bad decision-maker (PROPOSED)

Choose the margin where the counted rate best separates a random decision-maker
from the shipped one. This is the only option on this page under which the
regret rate means "the pipeline is healthy" rather than "the pipeline is
itself". **Costs control C3** (§5), which is not built, and it still leaves a
judgement — how much separation is enough — that no measurement settles.

### Option C — anchor the margin in the underlying units (PROPOSED)

Express each margin in something interpretable on its own scale: the route
margin as a fraction of one room's contribution to a path value, the draft
margin as a fraction of one card's printed damage or Block. A threshold stated
in units survives a version bump in a way a percentile does not. **Costs**
writing down both unit scales, which nothing in the repo currently does; and no
measurement can pick the multiple — that is design.

### Option D — set no margin (PROPOSED)

Keep quoting the margin-free distribution (which R164 already permits and this
tool now prints), and either retire `regretted` / `regret_rate` or leave them
where they are with their "uncalibrated" labels. Nothing today reads either of
them for any decision (§1), so the cost of this option is currently zero, and
it is not a deferral dressed up: it is a defensible end state.

**A note that belongs to no option.** Whatever is chosen, the route margin and
the draft margin are in different units and are not required to be the same
number. They are the same number today only because one was typed as an
analogy of the other.

## 7. Predictions and settings — [USER] SLOTS, to be filled before any seed is run

Measurement law: predictions are written from design intent, before the
numbers exist, and are never revised against the run that grades them. These
slots are empty on purpose. **Filling them is a [USER] act, and the run does
not start until they are filled and this packet is countersigned.**

> **[USER] SLOT — Q1(a), the route gap distribution.** Expected median route
> gap: `____`. Expected p90: `____`. Expected share of sampled decisions
> coming back at exactly zero: `____ % – ____ %`. Acceptance target or
> diagnostic-only? `____`

> **[USER] SLOT — Q1(b), the draft gap distribution.** Expected median draft
> gap: `____`. Expected p90: `____`. Expected zero share: `____ % – ____ %`.
> Acceptance target or diagnostic-only? `____`

> **[USER] SLOT — Q2, sensitivity.** Prediction: over the ladder this run
> prints, does the counted regret rate change by more than `____` percentage
> points between the p75 and p95 candidate margins? `YES / NO`.

> **[USER] SLOT — Q3, arms.** Prediction: do the six arms' distributions agree
> closely enough that one number describes them? `YES / NO / NO PREDICTION`.

> **[USER] SLOT — Q4, the two units.** Prediction: is the same `1.0` a
> comparably strict line on both sides? `YES / NO / NO PREDICTION`. If no,
> which side is stricter: `ROUTE / DRAFT`.

> **[USER] SLOT — Q5, instrument validity.** Is control **C3** (the
> deliberately bad decision-maker) authorised? `YES / NO`. If yes: prediction
> — does the counted rate separate the random decision-maker from the shipped
> one at the current `1.0`? `YES / NO`. If no, Q5 is dropped and the packet
> says so.

> **[USER] SLOT — control C2.** Is the decision-time draft read authorised?
> `YES / NO`. If yes: prediction — does it come back at or near zero, or do
> the draft policy's gates put it meaningfully above zero? `NEAR ZERO / ABOVE
> ZERO / NO PREDICTION`.

> **[USER] SLOT — which read Q1 is quoted from.** The default-sample-rate read
> (which carries the cross-check) or the full draft census (which carries the
> larger sample)? `DEFAULT / CENSUS / BOTH, reported separately`.

> **[USER] SLOT — n and seed.** `RUNS = 600` per arm, `SEED = 11`, six arms.
> Confirmed, or replaced by: `____`.

> **[USER] SLOT — tripwire T4.** Minimum count of *positive* gaps per arm
> below which the upper ladder is reported as unavailable rather than as a
> number: `____`.

> **[USER] SLOT — tripwire T5.** What counts as the arms disagreeing enough to
> stop the derivation: `____`.

> **[USER] SLOT — the derivation.** Which of §6's options, if any, is on the
> table when the grade lands? `A / B / C / D / undecided until the numbers are
> in`. If **A**: the pipeline the percentile is read off must be named here in
> full — reading (`A1` all sampled / `A2` positive only; **`A3` is
> forbidden**), which number (`ROUTE` / `DRAFT`), which arm or pool, which
> sample rate, which stamp, and the re-derivation rule for later version
> bumps: `____`

> **[USER] SLOT — redesign trigger.** What result, if any, reopens the regret
> instrument itself (rather than merely being recorded)? `____`

## 8. Contamination and known limits

- **Regret is self-consistency, not quality.** Both samplers re-score with the
  *same* scorer that made the decision. They can catch a decision that the
  run's own later state made wrong; they cannot catch a scorer that is wrong
  about the game. If the value function is mis-specified, both numbers can sit
  at zero while the pipeline plays badly.
- **The route number is zero in the deciding state by construction** (§2), so
  every route positive is the hindsight shift. A high route regret is
  ambiguous between "the planner chose badly" and "the run's health moved a
  lot after it chose", and this measurement cannot separate those two.
- **`hunter` and `cautious` are two policies, not a range.** Q3's answer is a
  statement about the distance between those two specific policies. It does
  not establish that any *other* route policy would land inside it.
- **Sampling asymmetry between the two numbers.** The route sampler sees every
  forked floor; the drafter sees one screen in ten unless the census read is
  authorised. The two sample sizes are not comparable and the packet must
  print both.
- **The draft gap can be negative** and is not clamped. A skipped screen
  scores the pick at zero by convention, so a screen where every offer
  re-scored negative gives a negative gap. Negatives are counted separately by
  the printer and are neither zeros nor regrets. This is a convention, not a
  measurement, and it is disclosed because it moves the low ladder rungs.
- **The draft-side regret COUNT moved slightly when the collector was split.**
  The pre-split loop asked `any(v > picked + 1.0)`; the split asks
  `(max - picked) > 1.0`. These differ at the exact-1.0 float boundary, because
  `picked + 1.0` can round below a rival's score. The new form is the faithful
  reading of the MEDIUM-11 invariant ("MORE THAN a full point") and treats a gap
  of exactly 1.0 as not a regret. Measured incidence at census sample rate is
  about one screen in 1,400 (120 runs: 197 -> 196). Nothing gates on the count,
  so this is a reporting difference — but any `draft_regret` figure quoted from
  before 2026-08-12 was taken under the older comparison.
- **The sim models one seat.** Nothing here speaks to co-op.
- **No C# side.** Neither margin exists in the mod; there is no mod-side
  instrument and no prediction here is about the mod's behaviour.
- **Nothing currently depends on the answer.** No gate, lint, band or ruling
  reads either count today (§1). That is a limit on how much this measurement
  can be worth, and it is stated up front rather than discovered afterwards.

## 9. What happens when it is countersigned

1. [USER] fills §7 and countersigns; the filled predictions land as their own
   commit, before any seed in the registered range is run.
2. Controls C2 and C3 are built if and only if §7 authorises them, and that
   build lands before the run.
3. The six arms run at the §5 n and seed, under `RT10/D14/P7/C9`. Each report
   carries its full stamp or it is not citable.
4. The results are published and graded blind against §7.
5. Only then does a derivation under §6 get chosen — or not chosen, which
   Option D makes a legitimate outcome.
6. This packet and its EXPERIMENTS pointer leave HEAD when the grade lands.

---

**Countersign — [USER].**

> Registration approved as written / approved with the changes noted above:
> `____`
>
> Signed: `____`   Date: `____`
