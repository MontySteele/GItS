# EB-81 — Furina: the two remedies, side by side

> **Lifecycle: ACTIVE.** This is the options packet BACKLOG `EB-81` owes QUEUE
> `S4-G7`. Its job is to lay out what each of the two ruled remedies costs,
> what each moves, and what each forecloses. **It takes no position** — the row
> says so verbatim, and nothing below recommends, ranks, or prefers. No design,
> behaviour or money call is made here. No number in this file is new: nothing
> was measured for it except two wall-clock timings, noted where they appear.

---

## 1. The choice, in the ruling's own words

On 2026-08-10, `R153` ruled that **Furina gets three plans**. It also named the
remedy as one of exactly two, and left the pick open:

1. **Rebalance the weak plans until they are viable.**
2. **Expand salon to contain multiple archetypes.**

Those two, and only those two, are compared below.

**One note on framing, so it does not get re-litigated.** An outside review
proposed splitting the decision into "scoring fixes versus card buffs". That is
not a third remedy. It is a split *inside* remedy 1 — two different ways to
raise a weak plan — and it appears there, in §5, as a sub-structure. It is not
used anywhere in this packet as a way of restating the choice.

---

## 2. The numbers you already have, and how far to trust them

This is the standing read quoted by `S4-G7`, taken from
`review/active/sitting-reads-2026-08-08.md` §1. Same recipe, same seed, 3000
runs per arm.

| arm | winrate | 95% interval |
|---|---|---|
| `furina / salon` | **4.70%** | [4.00, 5.52] |
| `furina / spotlight` | **1.50%** | [1.12, 2.00] |
| `furina / fanfare` | **1.30%** | [0.95, 1.77] |
| `real_silent / generic` (floor) | 1.37% | [1.01, 1.85] |
| `real_ironclad / generic` (floor) | 6.13% | [5.33, 7.05] |

**The caveat that governs every use of this table.** It was taken under world
stamp **`RT9/D14/P6/C8`**. The world that ships today is
**`RT10/D14/P7/C9`** — two boundaries later (`RT10` = the enchant events, R82 /
M7; `P7` = the pilot valuation fix, R176). By stamp law (R68) the levels in this
table are **not** today's levels. **Use it for structure, not for level.**

The structure it reports, which is what survived the last boundary crossing:

- Salon separates from both other plans; the intervals do not overlap.
- Spotlight and fanfare **cannot be told apart from each other** at this sample
  size — their intervals overlap, and on the prior read they were identical.
- Fanfare still overlaps the `real_silent` floor. So does spotlight.
- Salon now sits **below** `real_ironclad`, having sat above it before.

**A practical note about re-taking this table.** The two `real_*` floor rows are
built from a local `game_ref/` tree that is gitignored and is only on the main
checkout. On a worktree without it — this one, for instance — those two arms
simply do not print. Any re-baseline that wants the floors has to run where
`game_ref/` lives.

---

## 3. Five facts that bear on both remedies

These are not arguments for either side. They are the conditions any remedy
lands into, and each one is a cost or a constraint on both.

**(a) The pool is drafted, not assigned — so a buff aimed at one plan reaches
the others.** Furina's sheet is 82 rows. **32 of them carry the `generic` tag**,
which means the drafter offers them whatever the plan is. Measured deck
composition from the 2026-07-28 strength battery: **about 45% of every Furina
deck is archetype-neutral regardless of which plan is being drafted.** This was
learned the expensive way once already (§5.3).

**(b) A card-sheet edit carries no version signal today.** The `RT/D/P/C` stamp
does not cover the card sheets, so a change to a card's cost, numbers, rarity, or
whether it exists at all can ship with nothing in the stamp saying the world
moved. Whether that should change is itself an open [USER] call — QUEUE `M15`,
still unratified. Remedy 1's card-side lever sits directly under that question.

**(c) A drafter or pilot change *does* carry a stamp, and the drafter's stamp is
currently pinned.** Measurement law is explicit: a scorer change **is** a version
bump in the same edit (D4). Two live consequences:

- `DRAFTER_VERSION` is **held at 14** by `R121`'s countersigned six-step order.
  Step (5) of that order is the already-staged `D15` (BACKLOG `EB-43`), and it
  **must not land before step (4), the blind-first grading**, or the
  payoff-reach registration is invalidated. No step reorders.
- A pilot bump moves everything for that character. The worked example is three
  days old: `P7` (R176) added one missing valuation and, in the row's own words,
  **"every Klee tier0.5 number moves"**.

**(d) There is no standing definition of "viable".** LAW closes all seven
scorecard axes as reportable-only — never a gate, target, or justification to
move a value — and holds that the simulator's authority is relative deltas and
structural findings, not absolute winrates. Ratified winrate bands change only
by ruling (`R62`). So whichever remedy is picked, **its success test has to be
authored**; the standing informal yardstick has been comparison against the two
anchor floors in §2. The nearest thing to a target that exists is the tentative,
**unratified** Q-C aim list (Furina salon MED / spotlight HIGH / fanfare LOW),
which is itself waiting on your ratification in QUEUE `Q-C`.

**(e) The C# mod never sees archetype tags.** Codegen reads a card's effects, not
its plan tags, and no generated C# carries an archetype. So **re-tagging cards is
sim-side only**, with no mod rebuild and no parity work; **changing what a card
does or costs is a codegen + C# parity job** on top of the sim work.

### Furina's sheet as it stands today

Counted from `docs/furina-cards.yaml` (82 rows). "Exclusive" means the card
carries that plan's tag and no other tag at all — those are the only cards a
change can reach without touching another plan.

| plan | cards touching it | exclusive to it | exclusive by rarity |
|---|---|---|---|
| salon | 28 | 15 | 7 common / 5 uncommon / 2 rare / 1 basic |
| spotlight | 18 | 15 | 3 common / 8 uncommon / 4 rare |
| fanfare | 31 | 14 | 3 common / 5 uncommon / 6 rare |
| `generic` (reaches every plan) | 32 | — | 10 common / 13 uncommon / 5 rare / 4 basic |

Two things fall straight out of that table and are worth having in front of you
whichever way the pick goes. Fanfare's exclusive cards are **rare-heavy** — six
of fourteen — so a change confined to them is a change most decks never draw.
And twelve cards are tagged `[fanfare, generic]`, which is to say they are
fanfare cards the drafter offers to salon decks too.

---

## 4. How much the measurement itself costs

Measured on this machine tonight, and reported only as wall-clock — no game
number from these runs is quoted anywhere:

- The standing twelve-arm table, `tier05.exp_roster_anchors`, at 500 runs across
  the ten arms available without `game_ref/`: **41 seconds**.
- Extrapolating linearly to the published cell (3000 runs, twelve arms):
  **roughly four to five minutes**.

**The compute is not the cost.** Re-baselining the table is minutes. What is
expensive in both remedies is human and procedural: the rulings each needs before
work starts, the LAW amendments, the registration sequencing, and — for anything
that changes a card's behaviour — the C# parity leg.

---

## 5. Remedy 1 — rebalance the weak plans until they are viable

### 5.1 What it is

Leave the three plans as they are, and move spotlight and fanfare up until they
clear whatever bar you set. Salon stays the salon; the sheet keeps its shape; the
twelve-arm table keeps its arms.

### 5.2 The two sub-levers inside it

Stated as a split inside remedy 1, per §1 — not as a reframing of the choice.
Both are drawn from work already filed on the registers, so neither is invented
here.

**Sub-lever A — what the drafter and pilot *value*.** Filed items that already
exist, unstarted:

- `EB-28` — the drafter cannot see salon at all: `tier05/draft.py:_static_power`
  has no `salon_member` term. The same file's own header names the wider version
  of this: `bonus_formula` (20 printed uses, including `1_per_4_fanfare` and
  `2_per_salon_member`) and self-`apply_power` for non-engine powers
  (`salon_member`, 15 uses) are **still priced at zero**, on the record, as this
  sprint's "named still-owed".
- `EB-43` — the staged `D15` spotlight-limb payoff-presence change, with its
  re-baseline sweep. **Held**, and pinned to step (5) of the six-step order.
- `EB-33/34/35` — three pricing exhibits (The Gallery Stirs scoring 0.0 at offer;
  Vulnerable priced as a flat debuff; `_reaction_value` with no defensive term),
  filed as inputs to a repricing session whose pricing calls come back to you.
- `EB-32` — the pilot block-panic rung, which the source itself says "would move
  every tier-0.5 number on one observation", so it lands under a policy bump.

**Sub-lever B — what the cards *do*.** Change costs, numbers, rarities, or add
cards, on the plan-exclusive rows in the §3 table.

### 5.3 What it moves — and there is a precedent, with its number

This exact remedy has been attempted once, on fanfare, on 2026-07-28
(`git show pre-simplification-2026-08-06:docs/archive/sprint-fanfare-compensation-log-2026-07-28.md`).
**Its world was `RT7/D12/P3/C4` — four boundaries behind today. Read the shape,
never the levels.**

| arm | before | after | change |
|---|---|---|---|
| furina **fanfare** (the target) | 0.5% | 1.8% | **+1.3** |
| furina **salon** (not the target) | 7.7% | 10.8% | **+3.1** |
| furina **spotlight** | 2.8% | 2.3% | −0.5 |

Three findings from that pass, each of which is a cost line for remedy 1 today:

1. **The target moved least.** Salon gained more than twice what fanfare gained,
   off a card set aimed at fanfare.
2. **The pass's own stop condition fired.** The brief said: if the fanfare arm is
   still below the floor after this pass, report and stop, because *"a second
   round is a ruling, not a judgment call."* It landed at 1.8% against a 2.0%
   floor, and the battery prints that verdict itself so it cannot be quietly
   missed. **Remedy 1 is that second round.** It is the ruling the stop was
   waiting for.
3. **The ablation says why the leak happened, and it was not the obvious
   suspect.** Removing the starter rider — the first suspect, since the starter
   is in every deck — took **none** of the fanfare repair away, took most of the
   act-1 improvement with it, and left two thirds of the salon leak in place.
   The log's own conclusion: *"A 'fanfare-only' compensation was never available
   through the pool, because the pool is drafted, not assigned."*

### 5.4 What it costs

**Engineering.**

- Sub-lever A is small in lines and large in blast radius: each scorer change is
  a version bump, and a bump makes every arm of the table discontinuous — for
  every character, not just Furina. The re-baseline is therefore always the whole
  twelve-arm table, never the three Furina rows.
- Sub-lever B is sheet work plus codegen plus a C# parity leg (§3e). Furina's
  generated coverage is 81 of 82 today, so the machinery exists and the work is
  routine rather than novel.
- Either way: the affected tests. 16 test files reference salon, 10 fanfare, 6
  spotlight, across a 190-file suite.

**Measurement.** One re-baseline of the standing table per landed change
(minutes of compute; §4), plus whatever instrument the success test in §3d needs.
The plan-level instruments already exist and still import cleanly —
`exp_roster_anchors`, `exp_fanfare_compensation` (which prints the floor verdict
itself), `exp_furina_strength`.

**Sequencing.** Sub-lever A collides with the payoff-reach order: a drafter bump
before step (4)'s blind grading invalidates a countersigned registration. Sub-
lever B collides with `M15`: today it can ship with no stamp signal at all, and
if `M15` is ratified it becomes a `CONSTANTS_VERSION` bump like any other.

### 5.5 What it forecloses

- **Structurally, very little.** The plans, the arms, the sheet shape and the
  LAW text all stay as they are, so the `S4-G7` comparison series continues and
  every future read is comparable in shape to the one in §2.
- **It spends the "report and stop".** The 2026-07-28 stop was explicitly
  waiting for a ruling; picking remedy 1 is that ruling, and the next stop of the
  same kind would have to be written fresh.
- **It commits you to a bar.** "Until they are viable" only terminates once §3d's
  yardstick exists. Without one, the remedy has no stopping condition — which is
  what the 2026-07-28 brief avoided by writing its floor test in advance.
- **It does not, by itself, foreclose remedy 2.** Nothing in remedy 1 makes a
  later widening of salon harder, beyond the cards it re-tunes.

---

## 6. Remedy 2 — expand salon to contain multiple archetypes

### 6.1 One thing this packet cannot settle for you

The ruling's phrase admits two readings, and they cost different things. The
packet does not choose between them — which one is meant is part of the direction
pick, and it is yours.

- **Reading B1 — one home, several textures.** Salon becomes the container. What
  are three plans today become styles *inside* salon, and the sim's plan
  vocabulary shrinks accordingly. R153's "Furina gets three plans" is honoured as
  three ways to play, not three drafter labels.
- **Reading B2 — a wider stage.** Salon's own machinery grows — more member
  slots, or more kinds of member — so that spotlight and fanfare cards have
  somewhere to land on it. The three drafter labels survive.

### 6.2 What it moves

**For B2 there is a directly relevant measurement, and it points at a wall.**
From the 2026-07-28 strength battery (world `RT7`-era; structure only):

| salon member slots | winrate | dry upkeeps |
|---|---|---|
| 1 | 8.7% | 41.8% |
| 2 | 12.0% | 47.7% |
| **3 (shipped)** | **16.7%** | **49.7%** |
| 4 | 14.7% | 52.6% |

Going from one member to three nearly doubled her winrate — *"the stage is the
engine"* — but **the fourth slot made her worse**, because half of all upkeeps
already arrive unable to fund a member. The stage outruns its fuel. The same
battery notes the fuel line, Encore, binds in the sim but did **not** bind at a
real table, so this is one of the places where the sim and the table were
measured to disagree, with the mechanism named rather than guessed.

**For B1 the relevant measurement is the deck-composition read**, same battery:
an assigned salon draft was 45% generic / 28% salon / 14% spotlight / 13%
fanfare, and an undirected "good stuff" drafter drifted into salon on its own
while winning a third as often. The battery's own summary of the three-plan
situation at the time was that there was *"one plan, and everything else is
chaff"*.

### 6.3 What it costs

**Engineering — sim side, and it is mostly authoring rather than code.**

- **Card re-tagging.** The §3 table is the work list. Nothing in codegen or C#
  reads those tags (§3e), so this is a sim-only change — but *which* card belongs
  in which texture is design authoring, not mechanical.
- **The drafter's plan definitions.** `tier05/draft.py:core_complete` carries
  **hand-written limbs for spotlight and for fanfare** — spotlight needs two
  access cards plus one piece of machinery; fanfare needs three limbs
  (generation, floor, drafted readers). Folding or widening plans means deciding
  what happens to those limbs, and any edit there is a `DRAFTER_VERSION` bump,
  which is pinned at 14 until step (5)/(6) of the six-step order (§3c).
- **The declared archetype vocabulary.** `tier0/roster.py` declares Furina's
  three archetypes deliberately, with a comment explaining that they are declared
  precisely so no card can silently invent one. Changing the set is a registry
  change with a lint behind it.
- **The arm list.** `tier05/exp_roster_anchors.ARMS` enumerates twelve
  (character, plan) arms, three of them Furina's.
- **Tests:** same 16 / 10 / 6 files as above, but touched differently — these
  would be definition changes, not number changes.

**Engineering — C# side.** None, under B1 as a pure re-tagging. Under B2, adding
member kinds or slots is real kit work in both engines, plus the visual layer
(next bullet).

**LAW and standing-record cost — this is the part that is [USER]-only.**

- LAW names **Spotlight as a plan** in the delete-test clause: *"Salon and
  Spotlight beat self-carry at median draft quality."* If Spotlight stops being a
  plan, that clause needs amending.
- LAW's Funnel Contract binds the visual layer to **"Salon = 3 slot-index-keyed
  slots"**, and lists salon members as a **bounded meter with its cap read from
  `constants.py`** (`SALON_MEMBER_SLOTS = 3`). Widening the stage moves a
  contracted binding point, which is a stop-work-and-flag condition on the art
  track if it is done casually.
- Two dormant watch items are keyed to plan-level quantities: `W2` (salon power
  level) and `W4` (the fanfare floor). Both would need restating if the plans
  they watch change shape.
- LAW already draws the distinction that makes B1 *possible* without deleting
  anything: Fanfare is **a mechanic, not an axis** (R118 / R138). Folding a plan
  label does not require removing the mechanic — but which of the two is being
  folded has to be said out loud, because the mechanics are LAW and the plan
  labels are the drafter's vocabulary.

**Measurement.** The same minutes of compute (§4) — but see the next section for
what those minutes can and cannot tell you afterwards.

### 6.4 What it forecloses

- **The `S4-G7` comparison series ends for any folded arm.** The numbers in §2
  are per (character, plan). If spotlight and fanfare stop being arms, they have
  no successor rows, and *"did the remedy work?"* cannot be answered by comparing
  to the table that motivated it. A replacement comparison has to be designed
  before the change lands, or the before/after is lost.
- **It changes the shape of the Q-C step you have not taken yet.** Step (2c) of
  the payoff-reach order has you aiming **each roster archetype** high / medium /
  low within a census-derived band. Fewer Furina archetypes means fewer things to
  aim, and the tentative Sp-HIGH / F-LOW aims would have nothing to attach to.
- **It is the harder one to reverse.** Re-tagging cards and rewriting the plan
  vocabulary is a change to what Furina *is* in the drafter, in LAW's identity
  section, and in the registry. Remedy 1's tuning can be tuned again; a folded
  plan has to be un-folded.
- **B2 specifically runs at a measured wall.** The fourth slot made her worse in
  the sim, and the reason given was fuel, not slots — so B2 as "more slots"
  arrives with a fuel question attached (Encore's grantors and sinks) that the
  packet does not attempt to price.

---

## 7. Side by side

| | **Remedy 1 — rebalance the weak plans** | **Remedy 2 — expand salon** |
|---|---|---|
| **What changes** | Card numbers and/or what the drafter values | What the plans *are*, and possibly the stage's size |
| **Sim engineering** | Small edits, wide blast radius | Definition and tagging work; drafter limbs rewritten |
| **C# / parity leg** | Yes, if card behaviour changes | None for re-tagging; real work if the stage grows |
| **LAW amendments** | None identified | Delete-test clause, Funnel Contract, bounded-meter cap, two watch items |
| **Version stamp** | Card side: none today (`M15` open). Scoring side: a bump, hence a whole-roster re-baseline | Drafter side: a bump, and `D14` is pinned until step (5)/(6) |
| **Sequencing collision** | Sub-lever A must not precede the blind grading | Same pin, plus it reshapes the Q-C aiming step |
| **Measurement compute** | ~4–5 min per re-baseline | ~4–5 min per re-baseline |
| **Comparison to §2's table** | Preserved — same arms, same series | Broken for any folded arm; a replacement comparison must be designed first |
| **Known precedent** | Ran once (2026-07-28): target +1.3, salon +3.1, stop condition fired | Slot sweep exists: 3 slots best, 4 worse |
| **Reversibility** | Retunable | Hard to un-fold |
| **What it needs from you first** | A stated bar for "viable" | Which reading — B1 or B2 |

---

## 8. What neither remedy answers

Recorded so they are not mistaken for parts of the pick:

1. **What "viable" means.** No standing definition exists (§3d), and the nearest
   candidate — the Q-C aims — is unratified.
2. **`M15`.** Whether a card-sheet edit is a world change is still open, and
   remedy 1's card lever lands inside that question either way it goes.
3. **Where the work sits in the payoff-reach order.** Both remedies can collide
   with the pinned `D14` window; neither resolves it.
4. **Whether a table ever grades this.** No Furina playtest is scheduled, and
   co-op has no sim backstop, so any remedy graded in the sim alone is graded at
   the fuel level the sim runs at — which is the exact place the 2026-07-28
   battery found the sim and the table disagreeing.

---

## 9. What this packet did not do

- **No new game numbers were measured.** Every percentage here is quoted from a
  published record with its world stamp attached. The only fresh measurements are
  the two wall-clock timings in §4.
- **No live game session, no smoke.** None is owed by this packet; there is
  nothing in it that a running game could verify.
- **No position, no ranking, no recommendation** — per the row.
- **No register edits.** `BACKLOG.md` and `QUEUE.md` are untouched; closing
  `EB-81` and pointing `S4-G7` at this file is the integrator's to do.

---

## 10. Where every claim came from

| claim | source |
|---|---|
| The ruling and the two remedies | `docs/current/QUEUE.md` `S4-G7`; R153 |
| The standing read and its stamp | `review/active/sitting-reads-2026-08-08.md` §1 |
| Stamp law; one variable per window; a scorer change is a bump | `docs/current/EXPERIMENTS.md` |
| `D14` pinned; the six-step order, verbatim | `review/active/payoff-reach-reregistration.md`; R121 |
| `P7` moves every Klee number | `docs/current/STATE.md` stamp table; QUEUE `M17`; R176 |
| Card sheets sit outside the stamp | QUEUE `M15` |
| Axes reportable-only; sim authority is relative deltas; bands change by ruling | `docs/current/LAW.md` §"Design governance & measurement authority"; R62 |
| Spotlight named as a plan; Funnel Contract's 3 salon slots; bounded meter caps | `docs/current/LAW.md` §"Character identity — Furina", §"Art & visual layer", §"Engineering invariants" |
| Watch items `W2`, `W4` | `docs/current/STATE.md` watch register |
| Sheet counts by plan and rarity | `docs/furina-cards.yaml`, 82 rows, counted 2026-08-12 |
| Codegen does not read archetype tags | `tools/gen_roster_cards.py`; no `archetype` field in generated C# |
| `_static_power` has no `salon_member` term; `bonus_formula` / `apply_power` priced at zero | BACKLOG `EB-28`; `tier05/draft.py` header note above the static-power constants |
| Staged `D15`; the repricing exhibits; the block-panic rung | BACKLOG `EB-43`, `EB-33/34/35`, `EB-32` |
| Hand-written spotlight and fanfare limbs | `tier05/draft.py:core_complete` |
| Declared archetype vocabulary | `tier0/roster.py` |
| The twelve arms | `tier05/exp_roster_anchors.py:ARMS` |
| The 2026-07-28 compensation results, stop condition and ablation | `git show pre-simplification-2026-08-06:docs/archive/sprint-fanfare-compensation-log-2026-07-28.md` |
| The slot sweep, deck composition, "the stage is the engine" | `git show pre-simplification-2026-08-06:docs/archive/furina-strength-findings-2026-07-28.md` |
| Wall-clock timings | measured 2026-08-12 on this machine, `tier05.exp_roster_anchors --runs 500 --jobs 0` |
