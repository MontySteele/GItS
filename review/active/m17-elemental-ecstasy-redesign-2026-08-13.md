# M17 — "Sweet Dreams" (`elemental_ecstasy`): redesign options for red-pen

> **Lifecycle: DRAFT, awaiting [USER]'s red-pen at QUEUE `M17`.** This is the
> first of the two drafts `M17` says do not exist yet. It is an **options
> packet**: it lays out what the card is, what the measurement established
> about it, and **four** redesign directions side by side. **It takes no
> position between them** and ranks nothing. Every number in every sketch is
> **PROPOSED** and none of them has been measured.
>
> **R101b holds.** The frozen `EB-17p` registration
> (`review/active/eb17p-registration-draft-2026-08-08.md`) and its results file
> (`review/active/eb17p-results-2026-08-10.txt`) are **not edited** by this
> packet. Every figure below is quoted from them; nothing is re-graded.

---

## 0. Plain-English summary

Klee has a card called **"Sweet Dreams"**. It costs 2 energy. It does three
things, and **all three of them only work if the enemies already have an
elemental aura on them**: it refreshes those auras, it draws you one card per
aura'd enemy, and it gives you 8 Block — but only if one of those auras is
*not* Pyro.

The measurement found what that adds up to. When we forced a copy of the card
into 2,400 Klee reaction runs and compared them against the same 2,400 runs
with a *blank* card forced in instead, the card came out **0.21 points of
winrate behind the blank card** — which, given how precise the test was, means
"we cannot tell it apart from a card that does nothing". And when you drew it,
**87% of the time it was still sitting in your hand when the fight ended**. The
plain, un-upgraded version got played about **10%** of the times it was drawn.

So the card is not a trap and it is not hurting anyone. It is simply **not
doing anything**, most of the time, and taking a deck slot to not do it.

The structural reason, read off the sheet and the engine rather than off a new
measurement: **the card has no floor.** If nothing on the board has an aura
when you draw it, the card costs 2 and produces literally zero — no refresh, no
draw (the draw is "one per aura'd enemy", so zero enemies with auras means zero
cards), and no Block. And the Block clause is worse than that: it only fires on
a **non-Pyro** aura, while Klee is the Pyro character whose attacks apply Pyro.
The one clause with a real number on it is switched off by Klee's own way of
playing.

Below are **four directions** you could take. They are deliberately different
in kind, not four flavours of the same idea:

- **Option A — leave the card alone and change the price.** Cheapest edit.
- **Option B — give it a floor**, so it is never a completely blank card.
- **Option C — let it turn its own condition on**, so Klee's own play pattern
  satisfies it.
- **Option D — cut it** and use the slot for something else.

Two housekeeping facts you will want before choosing:

1. **Any of these four is a "world change".** Changing a cost, changing a
   number, or removing a card all bump `CONSTANTS_VERSION` under LAW's
   card-sheet rule (R179), which means every Klee number measured before the
   change stops being comparable to every number measured after it.
2. **There is a second draft in this pair** — the re-registered five-card
   sweep (`m17-sweep-reregistration-p7-2026-08-13.md`). Whether that runs
   *before* the redesign lands or *after* it is a real choice with real
   consequences, and §6 lays both out. `M17`'s own ruling permits the design
   act to be deferred behind the re-measure, so **both routes are faithful.**

---

## 1. What the card is today

Sheet row (`docs/klee-cards.yaml:182-183`):

| field | value |
|---|---|
| id | `elemental_ecstasy` |
| display name | **"Sweet Dreams"** (display rename 2026-07-20; the id was kept — greps must try both names, per the sheet's own comment at `:178-181`) |
| cost | **2** |
| type | skill |
| rarity | uncommon |
| archetypes | `[reaction]` |
| role | **`glue`** (not `payoff` — this matters, §5.4) |
| solve | `[block, utility, velocity]` |
| tempo band | fight `[mid, late]`, run `[early, late]` |

Effects, in order:

1. `refresh_all_auras` — every living enemy that **already has** an aura has
   its `aura_turns_left` reset to `aura_duration(state)`
   (`tier0/engine/effects.py:1083-1090`; base duration
   `AURA_DURATION_TURNS = 2`, `tier0/constants.py:44`). Enemies with no aura
   are untouched — the op does not *apply* anything.
2. `draw` with `amount_formula: per_aura` — draws
   `sum(1 for e in living_enemies if e.aura)` (`effects.py:770-777`). One
   aura'd enemy on the board means **draw 1**.
3. `conditional` on `target_has_nonpyro_aura` → `block 8`. The predicate reads
   a snapshot taken at card start (`effects.py:1786-1789`), and it is
   specifically **non-Pyro**.

Upgrade row (`docs/klee-upgrades.yaml:66`): `elemental_ecstasy: {cost: -1}` —
the upgrade is **cost 2 → 1** and nothing else.

**Where it sits.** Klee's reaction archetype prints 13 cards on the sheet;
`elemental_ecstasy` is one of six uncommons there, and one of the four the
survival-sprint register named for paired evidence. **The R185-ruled aim for
Klee Reaction is `HIGH`** — the highest of Klee's three archetypes, ruled
2026-08-12 as the Q-C answer of the payoff-reach registration
(`review/active/payoff-reach-reregistration.md` §6.2). Reaction is the plan
that is *supposed* to be Klee's strong one, which is the frame this card's
"does nothing" reading lands into.

---

## 2. What the measurement established — and what it did not

All from the frozen `EB-17p` packet, run at **`RT9/D14/P6/C8`**, 2,400
seed-matched pairs, `klee/reaction`, `assigned` policy, `hunter` route,
realistic loadout.

| reading | value | where |
|---|---|---|
| Δ vs **control** (§6.1) | **−1.62 pp** [−2.75, −0.46], p = 0.008 | §13.3 |
| Δ vs **filler** (§6.1b) | **−0.21 pp** [−1.12, +0.67], p = 0.719 | §13.4 |
| pooled dead-in-hand (§6.5) | **87.07%** | §13.7 / results `:124` |
| pooled played-when-drawn | **12.59%** | results `:124` |
| bare form played-when-drawn | **10%** (4,313 plays / 42,993 draws) | results `:122` |
| upgraded form played-when-drawn | **28%** (2,099 / 7,534) | results `:123` |
| compliance | family held to the end in **97.50%** of forced runs; control drafted it on its own in 15.08% | §13.1 |
| grade against §8 | **PREDICTED** — [USER] predicted "null within ±2 pp" on both co-primaries, and both landed inside | §13.6 |
| redesign trigger §8.1 | **FIRES**, on clause (b): Δ vs filler ≤ 0 **and** dead-in-hand ≥ 25% | §13.7 |

**What that means in one sentence, in the results' own words:** the card is
*"not hurting the deck; it is doing nothing, and doing nothing costs 1.4
points"* (§13.4 — 1.4 pp being the measured cost of pure deck dilution, the
filler's own row, §13.2).

**Three things the measurement did NOT establish, stated so no option below
can lean on them:**

- **Not a diagnosis.** Nothing in the sweep says *why* the card sits in hand.
  The 87% dead-in-hand is a count, not a cause. The structural reading in §3
  is read off the sheet and the engine, not off the sweep.
- **Not a P7 reading.** Every figure above is a **`P6`** read. `P7` (R176)
  changed what the pilot values and **moves every Klee tier-0.5 number**. The
  Δ figures above are therefore historical, and the second draft in this pair
  exists precisely to take them again.
- **Not causal about the upgrade.** The bare form plays 10% and the
  cost-1 upgraded form plays 28%. That is suggestive about price, and it is
  **confounded**: upgraded copies also arrive later in runs, in decks that
  chose to smith them. It may not be quoted as "halving the cost triples the
  play rate".

### 2.1 One flag on the `M17` row's own wording, for [USER]

`M17` (R180) reads the card's evidence as *"−0.21 with **87.07%
play-when-offered**, so the pilot wants it and it still loses ground"*. In the
results file, **87.07% is the pooled dead-in-hand rate** (results `:124`, and
it is the column §8.1 clause (b) reads); the pooled **played**-when-drawn rate
is **12.59%**. Flagged, not corrected — the row is [USER]'s ruling text and
this packet does not edit it.

**It does not change the ruling's conclusion**, and the reason is worth stating
because it is the actual contrast R180 was drawing: `elemental_ecstasy` **does**
get played sometimes (10% bare, 28% upgraded), whereas `borrowed_brilliance`
was played **exactly zero times in 40,396 draws** — the pilot-refusal signature
that P7 later resolved. So the distinction R180 rests on — one card has real
table evidence and the other had an instrument artefact — survives the
mislabel. But if the ruling's "the pilot wants it" clause was load-bearing for
the redesign *direction*, [USER] may want to re-read it: on the numbers, the
pilot mostly **declines** to play this card.

---

## 3. The structural reading — why a card can be "doing nothing"

Not measured. Read off `docs/klee-cards.yaml:182-183` and
`tier0/engine/effects.py`, and offered as the frame the options address.

**Every clause is conditional on an aura that already exists.** The card
applies nothing. On an auraless board it costs 2 and returns: no refresh (the
op skips enemies with no aura), **draw 0** (the formula counts aura'd enemies),
and **no Block** (the predicate is false). There is no floor at all — this is
the only card in the four the register named whose *entire* body can evaluate
to nothing.

**The Block clause is switched off by Klee's own play.** `block 8` is gated on
`target_has_nonpyro_aura`. Klee is Pyro, catalyst-grade — *all* her attacks
apply Pyro (STATE, roster table). So the aura Klee herself puts on the board
is exactly the aura that fails this predicate. The 8 Block — the largest and
most legible number on the card — is reachable only when something *other than
Klee's own attacks* has put a non-Pyro aura up.

**The scaling is thin where it fires.** Against a single aura'd enemy, the draw
is **1**. The card's velocity clause pays its best in wide fights and pays
almost nothing in the single-target fights that end runs.

**So the card asks the board to already be in the state it wants to reward.**
Every option below is a different answer to that one sentence.

---

## 4. What is fixed no matter which option is chosen

- **Identity to preserve, as the sheet states it.** The 2026-07-20 rename
  comment (`:178-181`) is explicit about what the card is *for*: *"the nap IS
  the aura refresh, the draws are the dreams"*, and it records that the old
  name *"implied reaction-rapture the card never delivers"*. Whatever lands,
  the display name "Sweet Dreams" and the id `elemental_ecstasy` are load-bearing
  history, and a rename is **not** a free cosmetic act (R179's rename amendment
  — the burden is on the renamer to show neither id nor display name is read
  mechanically, and `card_name_damage_bonus` reads both).
- **The C-bump (R179 / M15).** *"A card-sheet edit that materially changes the
  drafted or combat world — card additions or removals, cost changes,
  effect-number changes, rarity moves — is a world change. It lands under a
  `CONSTANTS_VERSION` bump like any other balance constant, and numbers are not
  comparable across it."* **All four options below trip this**, including
  Option A (a cost change) and Option D (a removal). There is no
  no-bump redesign of this card.
- **The mod side follows.** Klee's C# cards are generated
  (`tools/gen_klee_cards.py`, `tools/gen_roster_cards.py`); a sheet edit means
  regenerating, rebuilding the PCK, and redeploying before any live-game check.
  That is engineering cost, identical across the four, and it is not a reason
  to prefer any of them.
- **Nothing here is a measurement.** Whatever lands, its effect on winrate is
  unknown until something measures it, and that measurement is a registration,
  not an assertion in this packet.

---

## 5. The four options

Presented in no order of preference. Each carries the same five headings so
they can be read against each other. **Every number is PROPOSED.**

### Option A — Reprice: the card is right, the price is wrong

**Mechanical sketch.** Base cost **2 → 1**. Effects unchanged
(`refresh_all_auras`, draw per aura, conditional Block 8 on a non-Pyro aura).
The upgrade row must then become something other than `{cost: -1}`, because
cost 1 → 0 is a different card class; the two obvious replacements, both
PROPOSED and both needing their own red-pen, are `{block: +4}` (8 → 12 on the
conditional) or `{add: {op: draw, amount: 1}}` (a flat +1 draw on top of the
per-aura draw, which is also a partial Option B).

**What it preserves.** Everything. The body, the fantasy, the name, the role,
the archetype position. This is the minimal edit in the packet.

**What measured problem it addresses.** The price of being conditional. The one
number in the frozen results that points at cost is the bare-vs-upgraded play
split — **10% at cost 2, 28% at cost 1** (results `:122-123`) — and the
upgrade's only difference *is* the cost. It addresses the "why is it still in
my hand" half of the trigger and does not touch the "it does nothing" half.

**Instrument visibility (D4).** **Yes, fully.** A cost change is visible to the
tier-0.5 drafter and to `card_flow_profile`; the re-registered five-card sweep
(deliverable 2) grades it with no new column. `dead_in_hand_rate` and
`played_when_drawn_rate` are exactly the columns that would move if this works.

**Cost and risk.** Cheapest edit on the sheet — two lines, one of them the
upgrade row. **Risk:** it may not touch the real failure at all. If the card
sits in hand because the *board* is auraless rather than because the energy is
unaffordable, a cheaper blank card is still a blank card, and the measured
outcome is a smaller version of the same −0.21. Second risk: the replacement
upgrade line is itself an unpriced design act, so "cheapest edit" understates
what red-pen has to cover.

---

### Option B — Give it a floor: never a completely blank card

**Mechanical sketch.** Keep cost **2**. Prepend an unconditional clause so the
card always does *something*. Two shapes, both PROPOSED, not to be combined
without repricing:

- **B1 (velocity floor):** `draw 1` unconditionally, **plus** the existing
  per-aura draw. On an auraless board the card is "2 energy, draw 1, refresh
  nothing" — weak, but not zero. On a two-aura board it is draw 3.
- **B2 (block floor):** make the Block unconditional at a lower number —
  `block 4` always, `block 8` when a non-Pyro aura is present (i.e. the
  existing conditional becomes `+4` on top of a flat 4). The card is then a
  small Block card that gets much better in the state it wants.

**What it preserves.** The whole body and the whole fantasy — this is still the
aura-refresh, draw-your-dreams card. It changes the card's *shape* (from pure
amplifier to floor-plus-amplifier) without changing what it is amplifying.

**What measured problem it addresses.** The trigger's clause (b) directly:
**87.07% dead-in-hand**. A card with an unconditional clause has a reason to
be played on a turn when the board is not cooperating, which is the exact
turn it currently sits out.

**Instrument visibility (D4).** **Yes, fully.** Both sketches are ordinary
`draw` / `block` ops the tier-0 kernel already runs and the sweep already reads.
The predicted movement is in `played_when_drawn_rate` and `dead_in_hand_rate`,
with Δ-vs-filler as the outcome.

**Cost and risk.** One sheet line; no new engine op; no new grammar. **Risk:**
it makes the card *more generic*. A flat draw-1 or a flat block-4 is glue that
any archetype would take, which pulls the card away from being a reaction card
at all and toward being a colourless filler — the opposite complaint from the
current one, and one the sheet's own rename comment shows this card has a
history of ("the name implied something the card never delivers"). Second risk:
adding an unconditional clause at unchanged cost is a straight power increase,
and nothing here says how much.

---

### Option C — Let it turn its own condition on

**Mechanical sketch.** Make the card create the state it rewards, rather than
requiring it. Two shapes, both PROPOSED:

- **C1 (self-enabling refresh):** `refresh_all_auras` becomes
  refresh-or-apply — enemies with an aura are refreshed, enemies **without**
  one gain Pyro. The draw then always counts at least the enemies you just
  aura'd, and the card has a guaranteed body against any board. **This needs a
  new engine op or a widening of `_op_refresh_all_auras`
  (`effects.py:1083-1090`) — the only option in the packet that does.**
- **C2 (fix the anti-synergy):** change the Block predicate from
  `target_has_nonpyro_aura` to **any aura** (an existing-style predicate), so
  the 8 Block is reachable by Klee's own Pyro application instead of requiring
  a non-Pyro source Klee does not print. Optionally with the Block number
  moved down to compensate — PROPOSED at `block 5`.

**What it preserves.** The fantasy is intact and arguably *strengthened*: the
nap still refreshes the auras, the dreams are still the draws. C2 in particular
changes one word of a condition and no numbers, if the Block value is held.

**What measured problem it addresses.** The structural reading in §3 — no
floor (C1) and a headline clause that Klee's own play switches off (C2). Like
Option B it attacks dead-in-hand, but by making the *condition* reachable
instead of by adding an unconditional rider.

**Instrument visibility (D4).** **Yes for the outcome, with one caveat.** Both
sketches are sim-visible and the sweep grades them. **C1's caveat:** widening
the op is an engine change, so it needs its own test and its own byte-identity
argument for every other card that uses `refresh_all_auras`; it is the only
option whose blast radius reaches outside the sheet.

**Cost and risk.** *(Corrected 2026-08-13 — the original draft called C2 "a
one-token sheet edit"; that understated it.)* C2 needs a new predicate: the
condition vocabulary is a closed frozenset (`tier0/engine/effects.py:1730-1747
PREDICATE_NAMES`) with no any-aura member, enforced both directions by
`test_content_boundaries.py`, with name-switch sites at `effects.py:1786`,
`tier0/pilot/policy.py:136`, `tier05/draft.py:82,98`, and
`tier0/harness/metrics.py:857`; and the card is hand-written in C#
(`Cards/Generated/manifest.json:125`, `ElementalEcstasy.cs:28`), so the C#
behavior + tooltip move by hand too. So C2 = predicate vocabulary + C# behavior
+ tooltip + tests — still the smallest option after A, but not one token. C1 is
all of that plus the engine widening. **Risk, and it is the largest in the packet:** C1 turns
the card into an aura *generator*, which is what `combustion_study` (the
archetype's `enabler`) is for — so C1 may make the card step on a neighbour's
job, and it plausibly changes the card's **`role:`** field, which has a
downstream consequence spelled out in §5.4 below. C2's risk is smaller and
different: making the Block reachable by Klee's own Pyro is a straight buff to
the clause with the biggest number on the card, and 8 Block on a 2-cost
uncommon that also draws may simply be over-priced upward.

---

### Option D — Cut it, and use the slot

**Mechanical sketch.** Remove `elemental_ecstasy` from `docs/klee-cards.yaml`
and its row from `docs/klee-upgrades.yaml`; either leave Klee's uncommon
reaction pool one card lighter, or print a replacement uncommon reaction card
in the slot (a fresh design, out of scope for this packet — it would need its
own proposal).

**What it preserves.** Nothing of the card. It preserves the *slot*, and it
preserves the sheet's total shape if a replacement is printed.

**What measured problem it addresses.** All of it, by construction — the
measured problem is that this card occupies a deck slot without earning it, and
removal is the one direction guaranteed to stop that. It is also the honest
reading of "doing nothing costs 1.4 points": a card that cannot be
distinguished from a blank is, for the deck, a blank.

**Instrument visibility (D4).** **Yes, but differently.** A removal is not
gradeable *as an arm of the five-card sweep* — you cannot force a copy of a
card that does not exist. Grading a removal means a pool-level read (Klee's
reaction winrate before and after), which is a different instrument and a
different registration. **This is the only option the deliverable-2 sweep
cannot grade**, and that is a real asymmetry between the options, stated here
rather than buried.

**Cost and risk.** Sheet edit plus codegen plus mod regeneration; if a
replacement is printed, add art and a new C# card. **Risks:** Klee's uncommon
count drops (the sheet currently reads 29 Common / 28 Uncommon after the X7/X8
promotions, per STATE's `C9` note), which moves rarity-shape arithmetic and
every derived add-pool that counts uncommons; the archetype loses a `glue`
card while being the one aimed **HIGH** (R185); and the 2026-07-20 rename work
and the card's art are written off. Also worth naming plainly: a cut is the one
option that cannot be walked back by a follow-up tuning pass.

---

### 5.4 One interaction that applies to Option C (and to any option that moves `role:`)

The sheet's **`role:`** field is authored data that `tier05/draft.py` reads,
and it is what the payoff census counts (`review/active/payoff-census-2026-08-08.md`
§"What a payoff is"; `tools/payoff_census.py`). `elemental_ecstasy` is
currently **`role: glue`**.

The payoff-reach registration's band-hit criterion **P5** grades Klee Reaction
on exactly two static quantities read off this sheet: **(a)** the archetype's
draftable payoff-card count, and **(b)** its `Σ_r RARITY_ODDS[r] × payoffs_at_r
/ pool_size_at_r` offer figure (`payoff-reach-reregistration.md` §6.2). So:

> **Flipping `role: glue` → `role: payoff` on this card changes a graded input
> of a registration whose predictions are already committed (R186) and whose
> world is under a proposed freeze.**

Option D has the same property from the other side — removing an uncommon
changes `pool_size_at_r` in the offer denominator. Options A and B, as
sketched, do not touch `role:` and do not have this problem. This is a
sequencing constraint, not an argument against any option; §6 is where it
lands.

---

## 6. Sequencing — this redesign and the re-registered sweep

The second draft in this pair is
**`review/active/m17-sweep-reregistration-p7-2026-08-13.md`**: the same five
arms as the frozen `EB-17p` registration, re-stamped to `RT10/D14/P7/C9`.
`M17` (R180) permits the design act to be deferred behind the re-measure, so
**both orderings below are faithful to the ruling.** No position is taken.

**A constraint that binds before either ordering.** The payoff-reach
registration's §6.6 **P12** freeze is approved on the **settle-first** plan
(EXPERIMENTS, "Active registrations"): the open `RT`/`C` window lands, a
dependency re-check passes, §6 is re-stamped if the world moved, *then* the
freeze begins and the payoff-reach sprint runs. **A `CONSTANTS_VERSION` bump —
which every option in §5 is — cannot land inside that freeze window.** So the
redesign lands either *before* the freeze begins or *after* the payoff-reach
graded read, and never during. The sweep in deliverable 2 sits in the same
queue and takes its slot from the same order.

**Route 1 — measure first, redesign after (the ruling's default reading).**

- The `P7` sweep runs against **today's** sheet. The `elemental_ecstasy` arm
  re-reads the card as it currently stands, in the world that ships, alongside
  the `borrowed_brilliance` arm — which is the thing R180 actually wants
  re-measured.
- **One variable per window (D4) is respected**: the only thing that changed
  between the `EB-17p` read and this one is the world stamp, so the two reads
  are about the same card.
- **Consequence:** the design act waits, and the sweep spends one of its six
  arms re-measuring a card already ruled to be redesigned. That is the cost of
  this route, and it is not free — it is roughly three minutes of sim time and
  one more decision cycle of delay.
- **Consequence:** if the `P7` read moves `elemental_ecstasy`'s Δ-vs-filler
  materially, the redesign brief in this packet changes with it, and §5's
  options would want re-reading against the new number before red-pen is spent.

**Route 2 — redesign first, then measure the new card.**

- The chosen option lands under a `CONSTANTS_VERSION` bump (`C9` → `C10`), and
  the sweep is re-stamped to `RT10/D14/P7/C10` before it runs.
- **Consequence:** the sweep's `elemental_ecstasy` arm is then measuring a
  **different card**. The arm set is unchanged — R180's "never a narrowed set"
  is satisfied — but the arm's *meaning* changes, and its result may not be
  compared against §13.4's −0.21 pp, because that comparison would span a `C`
  boundary and a card edit at once.
- **Consequence for the other card:** the `borrowed_brilliance` re-measure now
  carries **two** changed variables relative to `EB-17p` (`P6`→`P7` and the
  sheet edit) instead of one. Under D4 that is a weaker read of the question
  R180 asked, and the packet says so rather than leaving it to be discovered at
  the grade.
- **Consequence:** the design act happens sooner, and the redesigned card gets
  its first measurement immediately rather than needing a third registration
  later.

**What each route costs, in one line each.** Route 1 costs delay and one
redundant arm; Route 2 costs the like-for-like comparison on both cards. The
choice is [USER]'s and is recorded on the `M17` row.

---

## 7. What [USER] is being asked for

1. **Red-pen the options.** Pick one of A / B / C / D, pick a sub-shape where
   one is offered (A's replacement upgrade line; B1 vs B2; C1 vs C2), or send
   the packet back for a fifth direction.
2. **Ratify the numbers, or move them.** Every number in §5 is PROPOSED and
   none is measured. Nothing lands until they are signed.
3. **Choose the route** in §6 — measure-first or redesign-first.
4. **Optionally, re-read §2.1** — whether the "the pilot wants it" clause of
   R180 was load-bearing for the direction you want.

No design, taste or money call is made anywhere above.
