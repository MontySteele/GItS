# EB-74 — Kokomi's lever 2: the candidates, side by side

> **Lifecycle: ACTIVE.** This is the options packet BACKLOG `EB-74` owes QUEUE
> `S4-G13`, written in the shape `EB-81` established. Its job is to discharge
> R154's **"construct"** verb without making the pick R154 reserved. **It takes
> no position.** Nothing below recommends, ranks, or prefers. No design,
> balance or money call is made here. **Nothing was built and nothing was
> pulled.** No new game number was measured; every percentage is quoted from a
> published record with its stamp attached. The handful of counts computed for
> this packet are labelled where they appear and are **PROPOSED** in the sense
> that they are fresh reads of live files, not ratified artifacts.

---

## 0. In plain English, first

R154 said Kokomi needs a general power lift, and told us to **build a lever-2
candidate and pull nothing** until the post-wave observation. A build attempt on
2026-08-12 stopped without writing code, and it was right to stop: "a legal
lever-2 candidate" is not one thing. It is at least four, and this packet found
a fifth.

The short version of each:

- **Option A — give her another starter card that exhausts.** Her opening deck
  has exactly one exhaust outlet today. Adding a second, with no draw/energy
  rider on it, gives the accrual back at the only slot the old measurement says
  is worth anything: the starter, which every deck holds from turn one.
- **Option B-alone — turn the universal dial up: `CHARGE_PER_EXHAUST` 1 → 2.**
  Every exhaust in the game pays her double Charge. One line. But the in-tree
  note at that exact line says Charge and Burst are one wage in two currencies
  and move together *or the reason moves with them* — so moving only Charge is
  legal but owes a written reason.
- **Option B-paired — move both: Charge 1 → 2 and Burst 2 → 4.** The note's
  default reading. Twice the dial movement, and it lands on her Burst meter as
  well, which was itself tuned by measurement (meter 20, R139).
- **Option C — build assist its missing payoffs.** This is what R154 actually
  *suspected* ("she really has two archetypes not three"). It is **not** lever
  2 by the tag's definition, which only knows about universal accrual. It is a
  card-sheet and/or drafter object, and it collides head-on with the 14-card
  `EB-69` batch already adopted for that sheet.
- **Option E — packet-added: move the dial for one exhaust source only.** The
  funnel already splits `exhaust` from `exhaust_muster` in code. Nobody has
  written this down as a candidate; it is legal under lever 2's text and it
  changes texture differently from B.

Then two things that are not options but must be decided alongside:

- **How to hold a built-but-unpulled change.** The `EB-74` row says the repo has
  no precedent. **That is not quite right, and the packet corrects it** — see §7.
- **A tension only [USER] can resolve.** R154 says assist's payoffs are missing.
  R185 ruled assist's aim is **LOW** — deliberately the lowest of her three. Both
  are live. See §6.

---

## 1. What lever 2 actually says

Lever 2 has exactly one definition, and it is at the tag. `git show
pre-simplification-2026-08-06:klee-mod/DECISIONS.md`, §"The standing question:
levers, annotated", item 2, **verbatim**:

> 2. **Give the accrual back elsewhere.** E2b's frequency finding constrains
>    this to HIGH-FREQUENCY slots only: an uncommon's accrual is worth ~nothing,
>    so this means either a pure-verb starter exhaust outlet (no economy rider,
>    R79-legal) or the universal funnel, `CHARGE_PER_EXHAUST` 1 -> 2 -- one
>    constant, its own E-cell, and a real texture change (fewer outlets, chunkier
>    gains). Note A9: that constant and `KOKOMI_BURST_PER_EXHAUST` are one wage
>    in two currencies and should move together or with a stated reason.

Three things in that paragraph do work later in this packet.

**(a) The frequency finding is the whole reason lever 2 is shaped this way.**
From the same section's preamble: *"E2b showed G6 (starter accrual) is
empirically ~the entire cost: 10.5-14.3 points, against G8's 0.0-1.0."* Those
are act-1-clear points, taken in a long-dead world — **read the shape, never the
level**. The shape is: starter-slot accrual mattered enormously; an uncommon's
did not. Any candidate that puts the accrual somewhere infrequent is, on that
finding, spending effort at a slot the measurement already said is worth ~zero.

**(b) "One constant, its own E-cell."** The definition itself asks for an
isolated measurement cell, which is the same discipline `EXPERIMENTS.md` states
as one-variable-per-window (D4).

**(c) Note A9 is not a prohibition.** It says *move together **or** with a
stated reason*. B-alone is therefore legal; what it owes is prose, not
permission.

**Scope boundary, recorded so it is not accidentally widened.** Levers 1 and 3
exist in the same list and are **not** in scope here: lever 1 is "revert or
soften G6" (which the tag notes carries a **LAW conflict** — the old
`tactical_retreat` was exhaust-plus-a-draw-rider at Basic, which R79 as ratified
forbids), and lever 3 is "re-anchor her band" (whose own annotation says the
floor anchor used at the time was contaminated). R154 named lever 2. This packet
stays there.

**One naming trap, cleared.** "Lever 2" here is **not** the roster-hardness lever
from the difficulty-calibration work. Those are a different sprint's numbered
list, about the battery-versus-roster instrument, and their numbered lever 3 was
ruled OUT in 2026-07-21. There is no shared numbering, no shared owner, no shared
artifact, and the `scratchpad/roster_hardness.py` that produced the hardness
table is not in the tree.

---

## 2. The numbers you already have, and how far to trust them

The standing read quoted by `S4-G13`, from
`review/active/sitting-reads-2026-08-08.md` §2. n=3000, seed 20260729.

| arm | winrate | 95% interval | k/n |
|---|---|---|---|
| `kokomi / priest` | **1.10%** | [0.78, 1.54] | 33/3000 |
| `kokomi / commander` | **2.20%** | [1.73, 2.79] | 66/3000 |
| `kokomi / assist` | **0.57%** | [0.35, 0.91] | 17/3000 |
| `real_ironclad / generic` (floor) | 6.13% | [5.33, 7.05] | 184/3000 |
| `real_silent / generic` (floor) | 1.37% | [1.01, 1.85] | 41/3000 |

Act-1 clear from the same cell: priest 42.20%, commander 51.83%, assist 35.37%.

**The caveat that governs every use of this table.** Stamp **`RT9/D14/P6/C8`**.
What ships today is **`RT10/D14/P7/C9`** — two boundaries later. By stamp law
(R68) these are not today's levels. **Use it for structure, not for level.**

The structure, which is what survived the last crossing (the packet's own §2
verdict: *Structure: HELD*):

- All three plans below `real_ironclad`, no interval overlap.
- Assist below `real_silent`, no interval overlap.
- Priest overlaps `real_silent` — it did on the prior read too.
- Act-1 clear rates were essentially unmoved across the boundary even though the
  run winrates fell.

**The `real_*` floors need `game_ref/`,** which is gitignored and lives only on
the primary checkout. Any re-baseline that wants floors has to run where it lives.

---

## 3. Conditions every candidate lands into

Not arguments for any option. Constraints all of them share.

**(a) Her starter deck has exactly ONE exhaust outlet.** Counted 2026-08-13 from
`tier0/content/characters/kokomi.yaml:82-93` against
`docs/inazuma-companions.yaml`: twelve cards — 4 `waters_edge`, 4 `coral_guard`,
`gorou_inuzaka_charge`, the support slot, `bake_kurage`, `tactical_retreat`. Only
`gorou_inuzaka_charge` carries `exhaust: true`
(`docs/inazuma-companions.yaml:29`). `tactical_retreat` was **deliberately**
converted from the second exhaust outlet to the first discard outlet at G6, and
the sheet comment at `docs/kokomi-cards.yaml:131-134` names the consequence in
advance: *"removing `exhaust_from 1` removes a starter EXHAUST, which is Charge
and Burst income… P9 predicts it shows up as an act-1 accrual slowdown and says
to suspect THIS before re-touching the multiplier."* That prediction is the
origin of this entire lever list.

**(b) The support starter slot is a coin flip.** `randomized_starter` swaps
`sayu_daruma_gift` for `shinobu_grass_ring_bond` at run start
(`kokomi.yaml:104-105`), so any starter-slot candidate has to say which of the
thirteen-or-twelve positions it occupies and whether it is randomized.

**(c) A balance-constant edit is a world change and lands under a
`CONSTANTS_VERSION` bump.** LAW is explicit for card sheets (*"…lands under a
`CONSTANTS_VERSION` bump like any other balance constant, and numbers are not
comparable across it"*, R179/M15 as ratified), and `EXPERIMENTS.md` puts
`CONSTANTS_VERSION` in the run-cell stamp. `C` is at **9**. Every option in §5
except the drafter half of C moves it to **C10 (PROPOSED)**.

**(d) A drafter edit is pinned.** `DRAFTER_VERSION` is held at **14** by R121's
countersigned six-step order; step (5) is the already-staged `D15` (`EB-43`) and
**must not land before step (4)'s blind-first grading**, or the payoff-reach
registration is invalidated. No step reorders. Only Option C's drafter branch
touches this.

**(e) `game_ref/`-dependent floors and the settle-first freeze.** The
payoff-reach registration's predictions were committed 2026-08-13 (R186) and its
approved P12 is **settle first**: the freeze starts only after the open `RT`/`C`
window lands — a window that explicitly names `EB-69`. Anything in §5 that moves
`C` moves that window with it.

**(f) The two constants are mirrored into C#, but their doubled twins are not —
and this is the sharpest technical fact in the packet.** `CHARGE_PER_EXHAUST` and
`KOKOMI_BURST_PER_EXHAUST` are MIRRORED in the parity gate
(`tools/lint_constant_parity.py:186-187`) against
`KokomiConstants.ChargePerExhaust` / `.BurstPerExhaust`. But the **upgraded
starter's** doubled rates are handled differently on each side:

- **C# side:** `PearlOfInsightRelic.ChargePerExhaust` is *derived* —
  `KokomiConstants.ChargePerExhaust * 2`, an **expression**. The parity lint
  lists both as `UNMIRRORED` precisely because `parse_number` cannot read an
  expression (`tools/lint_constant_parity.py:219-236`).
- **Sim side:** the same values are **literals** in
  `tier05/content/relics.yaml:245-246` — `{hook: charge_per_exhaust, amount: 2}`
  and `{hook: burst_per_exhaust, amount: 4}` — read at the funnel by
  `tier0/engine/relics.py exhaust_accrual`, which **replaces** rather than adds.

**Consequence for Options B-alone / B-paired / E:** bumping the base constant
moves the C# upgraded-starter rate automatically (1→2 makes the C# Pearl of
Insight 4) while the sim's `relics.yaml` literal stays at 2 — **and the parity
gate is structurally blind to it**, by its own recorded reasoning. The lint's own
note already flags the fix: *"Make it one [a literal] and this becomes MIRRORED
against `_ancient_hook('touch_of_orobas_kokomi', 'charge_per_exhaust')`."* Any B
or E candidate that does not decide what happens to the upgraded starter ships an
engine divergence.

**(g) The funnel is already split by source.** `tier0/engine/refpowers.py:301-308`
stamps every exhaust as `exhaust` or `exhaust_muster` (mustered recruits rotate
separately, for C5/P8), and the constants comment says the split exists *"precisely
so the wage can be read per-source before anyone touches it"*. This is what makes
Option E constructible at all.

---

## 4. Kokomi's sheet as it stands today

Counted 2026-08-13 from `docs/kokomi-cards.yaml` (62 rows: 5 basic / 27 common /
20 uncommon / 10 rare — matching `EB-69`'s own count). Rows carry more than one
tag, so the tag column sums above 62.

| tag | rows | of which `role: payoff` | payoff rarities |
|---|---|---|---|
| generic | 33 | 12 | 1 c / 6 u / 5 r |
| priest | 25 | 13 | 1 c / 6 u / 6 r |
| commander | 11 | 5 | 1 c / 2 u / 2 r |
| **assist** | **17** | **3** | **0 c / 2 u / 1 r** |

Exact tag-sets: priest+generic 14, generic-only 12, commander-only 11,
priest-only 8, **assist-only 7**, assist+generic 7, assist+priest 3.

**The seven assist-exclusive rows** — 4 common, 3 uncommon, **0 rare**:
`undertow_shuffle` (glue), `moon_signal` (enabler), `whispered_word` (glue),
`ebb_tide` (enabler), `rearguard_action` (glue), `quiet_harbor` (**payoff**),
`undertow` (**payoff**).

Two facts fall straight out and bear on Options A and C. **Assist is the only
one of her three archetypes with no common-rarity payoff** — its three payoffs
are two uncommons and one rare shared with priest (`epiphany_of_the_deep`). And
the sheet's own design comments already say the lane was built knowing this:
`quiet_harbor` at `:484-486` is *"the uncommon that makes the discard the BETTER
half, which is the whole reason the assist lane accepts a low internal payoff
elsewhere"*, and `undertow` at `:495-497` is *"the payoff that READS the pile the
lane has been filling. Every other exhaust-pile scaler she owns is priest or
generic… the assist lane fed that pile and had nothing that looked at it."*

**The drafter has no assist limb.** `tier05/draft.py` hand-writes limbs only for
`reaction`, `spotlight`, `fanfare` and `generic` (`core_complete` at `:281-321`,
`_core_progress` at `:395-424`). `assist`, `priest` and `commander` appear
nowhere in the module and fall through to `_generic_core_counts` (`:383-391`):
on-plan = cards where the archetype tag is present **and** `role` is
`enabler`/`payoff`; the gate is `on_plan >= DRAFT_CORE_SIZE` (4) and
`payoffs >= GENERIC_PAYOFF_COVERAGE` (1). **That pair is the entire in-code
definition of an "internal payoff" for assist.** Her Sly machinery is priced only
generically (`STATIC_SLY_SHARE = 0.5`, `tier05/draft.py:60`, applied `:737-751`).

---

## 5. The candidates

### 5.1 Option A — a pure-verb starter exhaust outlet

**What it is.** Add (or convert to) a starter-slot card whose only content is the
exhaust verb. Block and identity riders are explicitly legal under R79; a
draw / energy / cycling / selection rider is **not**, unless the card is Rare
**and** self-Exhaust — which a starter cannot be. Lever 2's own words:
*"pure-verb starter exhaust outlet (no economy rider, R79-legal)"*.

**What it touches.** `docs/kokomi-cards.yaml` (one new row, or one rewritten
row), `tier0/content/characters/kokomi.yaml` `starting_deck` (and possibly
`randomized_starter`), the three `packages` lists if the card is also draftable,
plus codegen + a C# parity leg if the card is new behaviour
(`klee-mod/KleeCode/Cards/Kokomi/Generated/manifest.json` currently reads 61 of
62 generated). **It does not touch `tier0/constants.py`.**

**A sub-fork inside A that has to be decided.** *Add a thirteenth card, or
convert an existing one?* The deck is twelve by [USER] ruling, and the ruling's
recorded reasons are specific — the buffer against decking out, and *"starters
are SUPPOSED to be bad and supposed to leave"* (`kokomi.yaml:67-74`). Adding a
thirteenth re-opens that ruling; converting one spends a slot that is currently
doing another job. Neither is chosen here.

**Mechanical effect at the three archetypes.** A starter card reaches **all
three** plans equally — it is in every deck from turn one, which is exactly the
E2b frequency property lever 2 was written around. So it moves priest (1.10%),
commander (2.20%) and assist (0.57%) together, and **does not close the gap
between them**. If R154's suspicion is that assist specifically is short, A
addresses the general lift and not the suspicion.

**Stamp movement.** `CONSTANTS_VERSION` 9 → **10 (PROPOSED)** under LAW's
material-card-sheet-edit clause. No `D`, no `P`, no `RT`.

**Reversibility.** High for the sheet row; the ratified-artifact edit to
`starting_deck` is one line. What is *not* cheaply reversible is the
twelve-card ruling if the add-a-thirteenth branch is taken.

**Interaction with `EB-69`.** Low but real. `EB-69` lands 14 cards as **one
batch** and then rebaselines; a starter card is not in that 14 and its rarity is
basic, so it does not change `EB-69`'s 76-row target (5/31/26/14). It does change
the world `EB-69` rebaselines *against*, so the two want to be ordered rather
than interleaved.

**What a post-wave observation could tell [USER].** Directly relevant: whether
the starter deck *feels* accrual-starved in the opening turns, and whether a
second exhaust outlet would read as texture or as clutter. This is the one option
whose object a player physically holds in the opening hand on turn one, so it is
the most observable of the five.

---

### 5.2 Option B-alone — `CHARGE_PER_EXHAUST` 1 → 2, Burst untouched

**What it touches.** `tier0/constants.py:327` (one integer), its C# mirror
`klee-mod/KleeCode/Powers/KokomiResources.cs:56`, and — per §3(f) — a decision
about `tier05/content/relics.yaml:245`, because the C# upgraded-starter rate is
derived and the sim's is a literal. Also the tests that assert against the
constant: `tier0/tests/test_kokomi.py`, `test_pin_cards_kokomi_1.py`,
`test_pin_cards_kokomi_2.py`, `test_orobas_upgraded_starters.py` — most assert
symbolically (`== C.CHARGE_PER_EXHAUST`), but `test_orobas_upgraded_starters.py:104`
pins the literal `== 1`.

**What Note A9 requires.** Not a veto. The in-tree restatement at
`tier0/constants.py:347-357` says *"These two constants are one wage in two
currencies, so they move together **or the reason moves with them**; halving this
alone is not 'a small burst nerf', it is a partial repeal of the payment R79
obliges."* B-alone is therefore the branch that **owes a written reason** —
which is itself a design act, not an engineering one.

**Mechanical effect at the three archetypes.** Charge is her declared scaling
identity (A2), read by `GARMENT_CHARGE_DIVISOR = 2` — the Ceremonial Garment
window gives +1 attack damage per 2 Charge. Doubling accrual doubles the bank
that window reads. The size of the effect per plan scales with **how much each
plan exhausts**, and the funnel is universal (statuses and curses count, an
accepted quirk, kickoff §2.1). No published per-plan exhaust-rate table exists in
HEAD, so the packet states the mechanism and declines to guess the split. What
*is* on the record is the frequency finding in §1(a) and the constants comment's
own texture claim: *"a real texture change (fewer outlets, chunkier gains)"*.

**Stamp movement.** `CONSTANTS_VERSION` 9 → **10 (PROPOSED)**. Lever 2's text
asks for *"its own E-cell"*, i.e. an isolated measurement window, which is
D4's one-variable rule.

**Reversibility.** Highest of the five as a code change — one integer, revert it.
Lowest as a *record* change: every number published under C10 is archived by the
revert, and the reason-prose A9 obliges becomes part of the standing record.

**Interaction with `EB-69`.** Direct collision on the *window*, not the code.
`EB-69` also moves `C`, and `EXPERIMENTS.md` names `EB-69` as one of the four
things that must settle before the payoff-reach freeze. Landing B and `EB-69` in
the same window makes the E-cell lever 2 asks for impossible; landing them in
separate windows costs two rebaselines.

**What a post-wave observation could tell [USER].** Less than for A. Charge
accrual is a meter reading, not a card in hand; the recorded history of this
exact question is *"I don't remember seeing the card during the playtest, so it
did not stand out one way or another"* — the verbatim clarification that turned
playtest three's read into **INCONCLUSIVE BY NON-OBSERVATION**. A post-wave
observation can say whether the Charge bank *feels* like it arrives too slowly;
it cannot distinguish 1 from 2 by eye.

---

### 5.3 Option B-paired — Charge 1 → 2 **and** Burst 2 → 4

**What it touches.** Everything B-alone touches, plus
`KOKOMI_BURST_PER_EXHAUST` at `tier0/constants.py:329` and its C# mirror at
`KokomiResources.cs:57`, plus `tier05/content/relics.yaml:246` under the same
§3(f) question (C#'s derived Pearl of Insight would go to 8).

**Why it exists as a separate option.** It is Note A9's default reading — *"one
wage in two currencies"* — and it is the branch that owes **no** extra prose.

**Mechanical effect at the three archetypes.** Adds a second axis to B-alone: her
Burst meter. `burst_max: 20` is **not** an arbitrary number — it is the arm that
hit the pre-registered acceptance band in the W2 bracket and was **RATIFIED as
R139** on the fresh `RT9/D14/P6/C8` read, with STATE recording that *"the current
build is the comparison baseline from now on"*. Doubling burst-per-exhaust
halves the exhausts needed to fill a ratified meter. Whether that re-opens R139
is a [USER] question this packet does not answer; it flags it.

**Stamp movement.** `CONSTANTS_VERSION` 9 → **10 (PROPOSED)** — the same single
bump, two constants inside it. Note the tension with lever 2's own *"one
constant, its own E-cell"* phrasing: A9's pairing and lever 2's isolation
instruction pull in opposite directions, and the packet does not resolve which
governs.

**Reversibility.** Same as B-alone in code. Higher record cost, because a meter
ratified by R139 is in the blast radius.

**Interaction with `EB-69`.** Identical to B-alone.

**What a post-wave observation could tell [USER].** More than B-alone, because
Burst is a visible meter with a visible fill rate, and the Ceremonial Garment
window is a discrete event a player notices firing. Still not a 2-versus-4
discrimination; a *"her Burst comes up about twice as often"* read at best.

---

### 5.4 Option C — the assist-shaped third object

**What it is, and why it is listed even though it is not lever 2.** R154's
suspected cause is assist's missing internal payoffs — *"she really has two
archetypes not three."* The lever-2 definition reaches universal accrual only; it
does not reach a per-archetype payoff shortage. `EB-74`'s own row says so:
*"R154's own suspected target… names a third object that the universal-accrual
definition does not reach."* Listing it is not proposing it. **Choosing to treat
C as in-scope is itself a [USER] act**, because it widens what R154 authorised.

**What it touches — and it splits into two sub-branches with very different
costs.**

- **C-sheet.** Add or re-role `role: payoff` rows carrying the `assist` tag in
  `docs/kokomi-cards.yaml`. Today: 3 payoffs total (2 exclusive uncommon, 1 shared
  rare), **no common payoff** — the only one of her three archetypes in that
  position (§4). Sheet + codegen + C# parity leg. `CONSTANTS_VERSION` bump.
- **C-drafter.** Give assist a hand-written limb in
  `tier05/draft.py:core_complete` / `_core_progress`, the way spotlight and
  fanfare have one, instead of falling through `_generic_core_counts`. This is a
  `DRAFTER_VERSION` bump — **and `D` is pinned at 14 until step (5)/(6) of R121's
  six-step order.** C-drafter is not landable inside the pin; C-sheet is.

**Mechanical effect at the three archetypes.** The most targeted of the five —
it is the only option that can move assist (0.57%) without equally moving priest
(1.10%) and commander (2.20%). Two counterweights, both on the record. Assist's
tags are not exclusive: 7 of her 17 assist rows also carry `generic` and 3 also
carry `priest`, so a change to a shared row reaches other plans. And the drafted-
not-assigned lesson is already paid for once on Furina: *"A 'fanfare-only'
compensation was never available through the pool, because the pool is drafted,
not assigned"* — the 2026-07-28 pass moved its target +1.3 and the non-target
+3.1.

**Stamp movement.** C-sheet: `C` 9 → **10 (PROPOSED)**. C-drafter: `D` 14 → 15,
which the pin forbids until the blind grading.

**Reversibility.** C-sheet is retunable like any card. C-drafter is a definition
change, closer to Furina's remedy-2 shape than to a tuning knob.

**Interaction with `EB-69` — this is the sharpest collision of the five, and the
row names it.** `EB-69` is **already adopted** (R157, REVISE-ADOPT): the A4+A6
package, 14 cards, `discard_dividend`/A3 dropped, sheet 62 → **76** (5/31/26/14),
complete upgrade rows required, **land as one batch, then rebaseline**. Any
assist-shaped candidate is authoring cards into the same sheet the same batch is
authoring into. Three consequences, all factual: (1) a collision re-check is
already part of `EB-69`'s definition and would have to re-run against a moving
target; (2) `EB-69` changes every denominator in the payoff-reach static leg, so
an assist payoff count taken before it is stale after it; (3) `EB-69` sits inside
the settle-first window ahead of the payoff-reach freeze, so interleaving a
second sheet change extends that window. The sequencing question — *C before
`EB-69`, C inside `EB-69`, or C after `EB-69`'s rebaseline* — is not answered
here.

**What a post-wave observation could tell [USER].** The most, of any option. The
suspicion R154 recorded is a *play* observation ("two archetypes not three"), and
whether an assist deck ever finds something to do with the pile it has been
filling is exactly the kind of thing a table reports and a Monte-Carlo does not.
The counterpart caution is that assist's own protocol reading is currently
provisional and the post-wave run is **exploratory** — per R175 it fills no
Answers block and consumes nothing.

---

### 5.5 Option E — **packet-added** — move the funnel for one source only

**Marked packet-added.** Not in the `EB-74` row, not in the tag's lever list.
Included because it is legal under lever 2's own text ("the universal funnel")
read narrowly, and because the machinery to do it already exists and is
documented as existing for this purpose.

**What it is.** `tier0/engine/refpowers.py:301-308` already stamps each exhaust
as `exhaust` or `exhaust_muster` (a mustered recruit's rotation), and
`tier0/constants.py:352-357` says the split exists *"precisely so the wage can be
read per-source before anyone touches it — see `tier05/burst_telemetry.py`, which
is a trace and not an allowlist for the same reason."* E is: raise the rate for
one source and not the other, rather than raising the universal dial.

**What it touches.** `tier0/constants.py` (a new named constant, PROPOSED — the
existing pair is unsplit today), `tier0/engine/relics.py exhaust_accrual` or its
caller, the C# mirror in `KokomiResources.cs`, and a new `MIRRORED` entry in
`tools/lint_constant_parity.py`. The upgraded-starter question from §3(f) applies
here too.

**Mechanical effect at the three archetypes.** This is the one option that is
*intrinsically* per-plan, because the source split is per-plan by construction:
`exhaust_muster` is the conscript lane, which is **commander's** income —
P8 is a claim specifically about *"mustered-companion exhausts, top-two in
commander decks"*. So raising the muster rate concentrates on commander (already
her strongest at 2.20%) and raising the non-muster rate concentrates away from
it. Whether either direction is wanted is a design call, untaken.

**Stamp movement.** `CONSTANTS_VERSION` 9 → **10 (PROPOSED)**.

**Reversibility.** Lower than B: it adds a constant and a branch rather than
changing a value, so reverting means deleting machinery, and any number published
under the split is archived either way.

**Interaction with `EB-69`.** Same window collision as B. Additionally, `EB-69`'s
14 cards are the A4+A6 package — whether any of them are conscripts changes which
source E's split lands on, so E is more `EB-69`-sensitive than B is.

**What a post-wave observation could tell [USER].** Narrow. It could report
whether the conscript lane feels differently-fuelled from the rest of her
exhausting, which is the distinction E is built on. Nothing about the rate.

---

## 6. Assist's missing internal payoffs — the evidence, and the tension

R154 named a suspected cause, not a finding. This section reports what the record
says about it. **It resolves nothing.**

### 6.1 What the supply actually is

From §4, counted 2026-08-13: assist has **3** `role: payoff` cards (2 exclusive
uncommon — `quiet_harbor`, `undertow`; 1 rare shared with priest —
`epiphany_of_the_deep`) against priest's 13 and commander's 5. It is the only one
of the three with **no common-rarity payoff**. Its 7 exclusive rows are 4 common
/ 3 uncommon / 0 rare, and all but `undertow` are `tempo_band.fight: [early]`.

The drafter's own definition of an internal payoff for assist is the
`role: payoff` string plus the tag, gated at `GENERIC_PAYOFF_COVERAGE = 1` and
`DRAFT_CORE_SIZE = 4` (§4). By that definition assist **clears the gate** — it
has three payoffs where one is required.

### 6.2 What the static leg reads

Computed 2026-08-13 by a read-only pass of `tier05.exp_payoff_reach.static_leg`
over the live sheet. **PROPOSED** — these are fresh reads, not ratified numbers,
and `EB-69` will move every one of them. Reward-pool sizes are 27 common / 20
uncommon / **9** rare (`ceremonial_garment` is `kit_card: true` and out of pool).

| arm | payoffs (c/u/r) | supply | offer | ruled aim (R185) |
|---|---|---|---|---|
| kokomi / priest | 1 / 6 / 6 | 13 | 0.16056 | MEDIUM |
| kokomi / commander | 1 / 2 / 2 | 5 | 0.06833 | HIGH |
| **kokomi / assist** | **0 / 2 / 1** | **3** | **0.04056** | **LOW** |

For scale, the canon bands the aims are placed against (payoff census §5.1–5.2,
post-R178): LOW `[0, 0.0058)`, MEDIUM `[0.0058, 0.0097)`, HIGH
`[0.0097, 0.0214]`, with TOP = 0.0214 the observed canonical ceiling.

**Read that comparison carefully, because it cuts both ways.** Assist's offer
figure is the **smallest of her three** — roughly a quarter of priest's — which is
consistent with "assist is the short one". It is also **far above the canonical
TOP**, as are all three of her arms, because her 62-card sheet is about a quarter
the size of an 82-card canon pool and offer is a per-draw density. The census's
own instruction governs: *"Aims are placed against the band NAMES and their
brackets, never against the third decimal of an offer figure."* So the honest
statement is: **relative to her own other archetypes, assist's payoff supply is
thin; relative to the canon band its LOW aim was drawn from, it is not thin at
all.** Both sentences are true of the same table.

### 6.3 What the census does and does not contain

`review/ruled/payoff-census-2026-08-08.md` contains **zero GItS roster
numbers**. Its §0 says so — it reads canonical content only, the extracted pools
under `game_ref/` — and its closing note repeats it. The only occurrence of
"Assist" in the file is the aims table. **So the census is evidence about the
canonical bands, and is not evidence about Kokomi's assist supply.** Anyone
citing it for the latter is citing the wrong document; §6.2's arithmetic is.

R178 (`96d8a84`) re-extracted the pools and moved exactly **one** band:
MEDIUM's offer 0.0097 → 0.0058 (N=20 floor 0.19 → 0.12). **LOW, HIGH and TOP are
unchanged on both axes**, and `canon_role_tempo` reported **zero** sighting
changes — `role-tempo-baseline.md` and `role-tempo-floors.yaml` regenerated
byte-for-byte. So the role-tempo layer says nothing new about assist, and the
band assist's aim points at did not move at R178.

### 6.4 The tension, stated and left open

Two live rulings point in different directions, and this packet surfaces rather
than reconciles them.

- **R154 (2026-08-10)** — Kokomi needs a **general power lift**; suspected cause
  is assist's **missing internal payoffs**, *"she really has two archetypes not
  three."*
- **R185 (2026-08-12)** — the Q-C aims are ruled as the census packet's §7.2
  table, adopted as written over a conflicting relayed ordering. **Kokomi /
  Assist = LOW.** It is one of three LOWs — one per character, alongside Furina's
  Fanfare and Klee's Spark — and the registration's own gloss is *"three MEDIUM,
  three HIGH, three LOW — one of each per character."* Committed as predictions
  by R186 on 2026-08-13, hard-coded at `tier05/exp_payoff_reach.py:71`.

**The question neither ruling answers:** is assist's thin payoff supply the
**defect** R154 suspects, or the **design** R185 ruled? A LOW aim is a
deliberate statement that this archetype shows you its reader rarely; the census
glosses LOW as *"a statement about how rarely canon shows you the reader, not
about how weak the plan is."* Meanwhile assist sits below the `real_silent`
floor with no interval overlap, which is a statement about winning.

Two further facts that bear on it, recorded as facts:

- **The sheet already says the low supply was intentional.** `quiet_harbor`'s
  comment: *"the whole reason the assist lane accepts a low internal payoff
  elsewhere"* (`docs/kokomi-cards.yaml:484-486`).
- **The aim is a prediction, not a target.** R186 committed the aims as the
  payoff-reach registration's §6, and grading rule P5 grades **supply** (band
  figure ±1) and **offer** (half-open brackets) *statically*. Under grading rule
  P5(a), a LOW aim expects supply ≈ 1 (so 0–2); assist reads **3**. That is a
  prediction that may already be off, and the registration is **UNRUN** and
  frozen behind settle-first. **Moving assist's payoff count is therefore also
  moving a committed prediction's subject** — which is a registration-law
  question, not just a balance one.

Nothing above is resolved here. The reconciliation — including whether "power
lift" and "LOW aim" are even about the same quantity — is [USER]'s.

---

## 7. The staging mechanism — its own question, and a correction

R154 says **build, do not pull**. That needs a place to put a built-but-unpulled
change. The `EB-74` row records that *"the repo has no staging mechanism for
inert code… `D15`/`EB-43`'s 'STAGED, HELD' is described-and-pinned prose, not
dormant code."*

**Correction, packet-added and verified 2026-08-13.** That is not accurate, and
the difference matters because it is exactly the precedent the row says is
missing. `staged/d15-spotlight-payoff` **exists as a real branch, locally and on
`origin`** (`f43049053c9c492d50abb09b777e573f04e1f818`), it holds **real code**,
and **it touches `tier0/constants.py`**:

```
tier0/constants.py      | 17 ++++++++++++++++-
tier05/draft.py         | 29 +++++++++++++++++++++++++++--
tier05/tests/test_m5.py | 20 ++++++++++++++++++--
```

Its constants hunk is `DRAFTER_VERSION = 14` → `15` with a fifteen-line comment
carrying the ruling, the reason the bump is not optional, and the sequencing rail
verbatim — including *"this change sits on `staged/d15-spotlight-payoff` and
LANDS ONLY after queue row 10.7 resolves."* The sibling precedent
`staged/f14-siblings` is the same shape, and was ultimately merged by [USER]
ruling at `Q3`.

So the honest statement is: **the repo has a staging precedent for a version-
stamped change, it is a branch, and it has been exercised twice.** What it has
never done is stage a change to a *balance* constant, and the branch route has a
specific known cost recorded in the house norms (one worktree per workstream,
sibling directories only). The three routes below are laid out position-free.

### Route 1 — a staged branch (the `D15` precedent)

Build the candidate on `staged/eb74-lever2-<name>`, push it, land nothing.

- **For:** exercised twice; the whole change is visible as a diff; the suite runs
  on it, so "complete and machine-checked" is literally true and provable;
  nothing in HEAD moves, so `C` does not move and no window opens; reverting is
  deleting a branch.
- **Against:** it rots against a moving `main` — and `EB-69`, `EB-70`, `EB-82`,
  `EB-85` are all in flight in the same window, several of them touching the same
  sheet; the CI on a staged branch is a snapshot, not a standing guarantee;
  discovering it requires knowing it exists (both prior instances needed a
  register row pointing at them).

### Route 2 — a staged file plus an apply script

Keep the candidate as data in-tree (e.g. a patch or an overlay file under a
`staged/` path) with a script that applies it on demand.

- **For:** it lives in HEAD, so it is discoverable by anyone reading the tree and
  it moves forward with the repo; the diff never rots because it is applied at
  use time; it can carry its own README and its own lint.
- **Against:** **no precedent at all** — this is the genuinely new mechanism; an
  unapplied patch that nothing runs is not machine-checked in any meaningful
  sense, so "complete and machine-checked" would need a test that applies it in a
  fixture and asserts on the result, which is new machinery; and a `staged/`
  directory in HEAD invites a future reader to treat its contents as live.

### Route 3 — a guarded constant in HEAD

Land the candidate behind an off-by-default flag or an alternate constant that
nothing reads at default settings.

- **For:** fully in HEAD, fully tested by the standing suite, no rot, and the
  flip is a one-line change when the pull decision comes.
- **Against:** it puts a second value for a balance constant into the shipping
  tree, and the parity gate's own history is a warning about exactly that shape —
  `PearlOfInsightRelic`'s doubled constants once existed C#-side, *"read by
  nothing except the relic's own description string"*, so the panel promised
  doubled accrual and the funnel granted base (§3f). Dormant balance numbers that
  nothing reads are how the two engines came to disagree. It also raises the
  question of whether a guarded-but-present constant is itself a world change for
  stamp purposes, which nothing in LAW currently answers.

**Why this section is [USER]-adjacent.** Whichever route is taken becomes the
precedent for every future "build it, do not pull it" instruction. That is a
process call with a standing effect, and the packet takes no position on it.

---

## 8. Side by side

| | **A — starter outlet** | **B-alone — Charge 1→2** | **B-paired — Charge + Burst** | **C — assist-shaped** | **E — split funnel (packet-added)** |
|---|---|---|---|---|---|
| **Is it lever 2?** | Yes, disjunct 1 | Yes, disjunct 2 | Yes, disjunct 2 + A9 | **No** — outside the definition | Narrow reading of disjunct 2 |
| **What it edits** | `kokomi-cards.yaml` + `starting_deck` | `constants.py:327` (+ C# mirror) | `:327` and `:329` (+ mirrors) | sheet rows and/or `draft.py` limb | new constant + funnel branch |
| **Reaches which plans** | all three equally | all three, weighted by exhaust rate | all three, plus the Burst meter | assist preferentially (but 10/17 rows are shared) | commander vs the rest, by source |
| **Stamp** | `C` 9→10 | `C` 9→10 | `C` 9→10 | sheet: `C` 9→10 · drafter: `D` 14→15, **pinned** | `C` 9→10 |
| **Extra prose owed** | none | **A9's stated reason** | none | widening R154's scope | naming a new constant |
| **C# parity leg** | yes if new behaviour | mirror + the §3f upgraded-starter question | same, doubled | yes for C-sheet; none for C-drafter | mirror + a new `MIRRORED` entry |
| **`EB-69` interaction** | ordering only | same-window collision | same-window collision | **direct sheet collision** | same-window + conscript-composition sensitivity |
| **Reversibility** | high (sheet); the 12-card ruling is not | highest in code, record archived | same, plus R139's meter in blast radius | C-sheet retunable; C-drafter is a definition | lower — deletes machinery |
| **Post-wave observability** | highest — it is in the opening hand | lowest — a meter rate | moderate — Burst frequency | high — it is the thing R154 saw | narrow — lane texture only |

---

## 9. What this packet did not do

- **No candidate was built.** No code, no sheet row, no constant moved. `git
  status` shows only register edits and this file.
- **No pick was made**, on any of: A / B-alone / B-paired / C / E; the
  add-versus-convert sub-fork inside A; whether C is in scope at all; the
  staging route; or the `EB-69` sequencing.
- **No new game number was measured.** The percentages in §2 are quoted with
  their stamp. The counts in §3, §4 and the static-leg table in §6.2 are fresh
  read-only passes over live files, labelled PROPOSED, and `EB-69` will move the
  §6.2 figures.
- **No live game session, no smoke, no `tools/art_fetch`.** Nothing here is
  verifiable by a running game.
- **The two engines were not reconciled.** §3(f)'s upgraded-starter divergence is
  reported as a constraint on options B and E, not repaired.

---

## 10. Where every claim came from

| claim | source |
|---|---|
| R154, the standing read, "build and pull nothing" | `docs/current/QUEUE.md` `S4-G13`; commit `3d6964c` |
| The three-way fork, the `EB-69` collision, the absent staging mechanism | `docs/current/BACKLOG.md` `EB-74` |
| Lever 2 verbatim; the E2b frequency finding; levers 1 and 3 | `git show pre-simplification-2026-08-06:klee-mod/DECISIONS.md` §"The standing question: levers, annotated" |
| The pre-registered fork; "INCONCLUSIVE BY NON-OBSERVATION" | same file, §"PRE-REGISTERED FORK for playtest three" |
| R79's verb-partition law and its Rare+self-Exhaust carve-out | `docs/kokomi-cards.yaml:39-44`; `docs/current/LAW.md:266-270` |
| Note A9, the double wage, the source split's purpose | `tier0/constants.py:327-357` |
| The standing winrate table and its stamp | `review/active/sitting-reads-2026-08-08.md` §2 |
| Starter deck, the 12-card ruling, `randomized_starter` | `tier0/content/characters/kokomi.yaml:60-105` |
| `tactical_retreat`'s G6 conversion and the P9 prediction | `docs/kokomi-cards.yaml:123-138` |
| Gorou is the only `exhaust: true` starter | `docs/inazuma-companions.yaml:29` |
| The funnel, the source split, `exhaust_accrual`'s replace semantics | `tier0/engine/refpowers.py:275-315`; `tier0/engine/relics.py:195-233` |
| Sim's doubled literals; C#'s derived expression; the lint's blind spot | `tier05/content/relics.yaml:245-246`; `tools/lint_constant_parity.py:186-187, 219-236`; `klee-mod/KleeCode/Powers/KokomiResources.cs:56-57, 318-324` |
| Sheet counts by tag, role and rarity | `docs/kokomi-cards.yaml`, 62 rows, counted 2026-08-13 |
| No assist limb; `_generic_core_counts`; the two gate constants | `tier05/draft.py:281-321, 383-424, 1219`; `tier0/constants.py:1205` |
| `EB-69`'s adopted shape, 62 → 76, one batch | `docs/current/BACKLOG.md` `EB-69`; R157 |
| `D14` pinned; the six-step order | `review/active/payoff-reach-reregistration.md`; R121; `docs/current/BACKLOG.md` `EB-43` |
| `C` = 9; the stamp table | `docs/current/STATE.md` |
| Card-sheet edits are `CONSTANTS_VERSION` bumps | `docs/current/LAW.md:318-331`; R179 / M15 |
| One variable per window; settle-first; the open `RT`/`C` batch | `docs/current/EXPERIMENTS.md` |
| R185's ruled aims; Assist LOW | `review/ruled/payoff-census-2026-08-08.md:774-791`; `review/active/payoff-reach-reregistration.md` §6.2; commit `02cd295` |
| R186 committing the aims as predictions; grading rule P5 | `review/active/payoff-reach-reregistration.md` §6; commit `825d302`; `tier05/exp_payoff_reach.py:58-71` |
| R178 moved only MEDIUM; role-tempo byte-identical | commit `96d8a84` |
| Canon bands LOW/MEDIUM/HIGH/TOP; "band NAMES, not the third decimal" | `review/ruled/payoff-census-2026-08-08.md` §5.1-5.2, §7.2 |
| The census contains no roster number | same, §0 and closing note |
| Static-leg figures for her three arms | `tier05.exp_payoff_reach.static_leg`, read-only pass, 2026-08-13 |
| `burst_max: 20` ratified as R139 | `tier0/content/characters/kokomi.yaml:26-45`; `docs/current/STATE.md` Lifecycle |
| The drafted-not-assigned lesson and its numbers | `git show pre-simplification-2026-08-06:docs/archive/sprint-fanfare-compensation-log-2026-07-28.md` |
| `staged/d15-spotlight-payoff` exists with real code | branch `f430490`; diff vs `0189e46` |
| `staged/f14-siblings` precedent, merged at `Q3` | retired user-queue at tag `pre-simplification-2026-08-06` |
| Post-wave run is exploratory; two events not one | `docs/current/QUEUE.md` `S4-G14`; R175 |
| Suite state at packet time | `python -m pytest tier0/tests -q` → 2076 passed, 12 xfailed, 2026-08-13 |
