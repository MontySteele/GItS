# Charge reads per turn — a descriptive distribution: SLATE DRAFTED, UNRUN

> **STATUS: SLATE DRAFTED. NOT COUNTERSIGNED. UNRUN.** §5 is the slate
> `X9READ-S1`, **DRAFTED by Claude from written intent under R212(2) and
> committed before any run**, with §5.4's `W9` watch trigger and its number for
> *dominant* travelling with it. Nothing in this packet may be run until the
> **batch countersign** lands — the same gate every registration in
> `docs/current/EXPERIMENTS.md` sits behind. §4's `n`, seed and cost ceiling are
> still [USER]'s PROPOSED slots (§5.2).
>
> Owner of the countersign: [USER]. Register row: BACKLOG `EB-78` (2).

---

## 0. Plain English, first

Kokomi banks a resource called Charge. Nothing ever spends it — several things
*read* it and convert what they see into damage or Block. On 2026-08-13 [USER]
ruled (R188) that there will be **no budget on how many times a turn may read
the bank**, and that a card which reads the bank while her Burst state is up —
reading it twice, once through its own printed text and once through the state
— is **intended stacking**, not a bug.

That ruling is a **deferral, not an endorsement**: the question comes back if a
reads-per-turn reading, or a live playtest, shows repeatable reads dominating.
Which means somebody has to be able to say **how many reads a normal turn
actually contains** — and until 2026-08-13 that number was recorded nowhere at
all. The workshop packet said so twice, at its §7 and again at its §8.

This packet registers the measurement that produces that number. It is
**descriptive**: it changes nothing, it grades no design, and it cannot on its
own justify a nerf. It exists so the watch trigger has a quantity to be set
against instead of an impression.

---

## 1. Provenance

- **The ruling that asks for it:** R188 (2026-08-13), closing QUEUE `M25` on
  workshop axis **G** (the null option) with axis **F** resolved as *intended
  texture*.
- **The workshop that located the readers:**
  `review/active/eb78-charge-read-budget-workshop.md` §3 (the four kinds of
  reader, with file and line on both engines), §6 (the unsettled scope
  boundary), §7 (*"what is not recorded anywhere today is how many reads a turn
  actually contains"*), §8 (*"no distribution of reads per turn"*).
- **The parent finding:** R163, which left the shape of an X9 read budget open
  and required the workshop to be numberless.
- **The pin that watches the mechanism:**
  `tier0/tests/test_s13_exploit_pins.py::test_x9_kokomi_charge_bank_is_uncapped_and_never_spent`.

## 2. The instrument — BUILT 2026-08-13, before any number was read

`tier0/engine/resources.py::note_charge_read` and the per-turn sample emitted
at `tier0/engine/combat.py`'s `turn_close` site. Emit-only and count-only: the
tally lives on `CombatState.charge_reads_this_turn`, and **no engine, pilot or
drafter path reads it back**. It is not a budget and cannot become one by
accident — R188 ruled there is none.

Two events:

| event | when | fields |
|---|---|---|
| `charge_read` | at each resolved read | `kind`, `card`, `bank`, `turn` |
| `charge_reads_turn` | once per completed player turn | `total`, `by_source` |

**Three counted sources**, tagged rather than pooled, so the distribution can be
reported under **either** reading of the workshop's unsettled §6 scope boundary
without the instrument having settled it:

- `garment` — the Ceremonial Garment rider, once per attack play per target
  while the state holds (workshop §3.1; the tick shares the `KNOB_READS`
  condition already established there as the site of a *real* read).
- `kurage_pulse` — the fielded jellyfish's end-of-turn whole-bank conversion,
  once per turn while the summon stands (§3.2).
- `bonus_formula` — a card's own printed `N_per_M_charge` rider (§3.3).

**Deliberately NOT counted**, and this is a registered choice rather than an
omission: the two pilot valuation sites (`tier0/pilot/policy.py`, workshop
§3.4). Those are the pilot's estimates of what a card is worth, not
resolutions. Counting them would report deliberation as if it were play. The
threshold reader is likewise absent because it is not a proportional read (§3.3)
and never enters the `N_per_M_charge` branch.

**A card that prints its own read and also collects the Garment rider tallies
TWO reads on one play.** That is the R188-ruled double read, and the instrument
is built to see it rather than to hide it.

### 2.1 Declared blind spot

The per-turn sample rides `turn_close`, which a turn ending in the last enemy's
death or the player's own does not reach. **The final turn of most fights
therefore contributes no sample**, and the truncation is toward the BUSY end —
a killing turn is rarely a quiet one. Every reading of this measurement states
this, and §6's grading may not quietly report a mean as if it covered all turns.
The `charge_read` stream is unaffected and is the cross-check: comparing its
count against the summed `charge_reads_turn` totals measures exactly how much
the truncation drops.

## 3. Questions

**Q1 — What is the distribution of reads per player turn?** Reported as mean,
p50, p90, p99 and max, over all sampled player turns, split by archetype.

**Q2 — How is that total composed?** The same statistics per `kind`, so
"repeatable reads" can be attributed to the reader that produces them rather
than to the bank.

**Q3 — How often does one card play tally two reads?** The count of plays
carrying both a `bonus_formula` and a `garment` read, as a share of all attack
plays — the R188 double read, measured for the first time.

**Q4 — Does the distribution's tail move with the fight's length or the act?**
Descriptive; the bank only grows, so a per-turn read count that rises with turn
number is the shape the standing caveat *"watch act 3"* was written about.

**None of these grades a design.** No question here can fire a nerf; the
firing condition is R188's, and it names a *reading* plus [USER]'s judgement.

## 4. World, cell and sample plan

- **Cell:** **`RT12/D18/P11/C21`**, with `PILOT_WEIGHTS_VERSION` **6** — the
  live cell, read off `docs/current/STATE.md` on 2026-08-30. *Revised
  2026-08-30 on the pair review's correction: the packet was stamped
  `RT10/D14/P7/C9` at drafting (2026-08-13) and the world has moved four
  stamps since, so it is re-stamped here — before the freeze and before any
  run, as this bullet's own rule requires — and no number in §5 was read off a
  run at either cell, so nothing is re-graded and the slate is not re-signed.*
  Stamp law still applies: **if the open `RT`/`C` window moves again before
  this runs, the packet is re-stamped before the freeze, not after the read.**
- **Character:** `kokomi` only; the bank is hers. All three archetypes
  (`priest`, `commander`, `assist`), reported separately, since exhaust rate
  and reader density differ per plan.
- **Pilot / drafter:** the standing values for the cell, unchanged. This
  measurement moves no version and opens no window.
- **`n` per archetype — [USER] slot.** PROPOSED at **600 runs per archetype**,
  the ratified cell's figure and **unchanged at the re-stamped cell**, giving three arms and 1,800 runs. The quantity is
  per-TURN, so the turn count is roughly two orders of magnitude larger than the
  run count and the tail statistics are the binding constraint, not the mean.
- **Seed — [USER] slot.** PROPOSED at the cell's standing seed, recorded in the
  fill.
- **Cost ceiling — [USER] slot.** PROPOSED at **1 hour wall-clock,
  stop-and-report.** A partial result is graded as partial and quotes the turns
  it actually covered.

## 5. The slate — `X9READ-S1`, DRAFTED under R212(2)

**REGISTRATION. Drafted from written intent and committed BEFORE any run**
(R212(2), EXPERIMENTS *Pre-registration + blind grading*). Every threshold below
is derived from §0–§4, from R188's own words, from the workshop packet, and from
constants and card rows that were on the sheet before this section was written.
**No number in this section was read off a run, a probe or a scratch pass — no
run of this instrument has ever been taken.** The gate is the **batch
countersign**; signed once, since a moved world means re-draft and disclose,
never re-sign.

**This supersedes the DRAFT banner's "§5's prediction slots are [USER]'s and are
blank."** That banner was written on 2026-08-13, before R212 moved prediction
slates onto the delegation ladder: *"prediction slates (DRAFTED from written
intent, committed before any run, batch-countersigned)"*. §5.4's watch trigger
travels with the slate under the same clause and is drafted here too, with its
one judgement call flagged in place. What is **still [USER]'s** is unchanged and
is named at §5.2: the countersign, `n`, the seed, the cost ceiling, and every
design act downstream of a fired trigger.

### 5.0 Three instrument facts, read off the code BEFORE any run

They are stated here because each one changes what a number below *means*, and
because a registered read may not discover its own instrument at grading time.
All three are corrections to §2's prose, not to the instrument; the instrument
is unchanged and untouched by this commit. *Re-verified against code
2026-08-30 at the re-stamped cell: all three facts still hold, and the two line
numbers moved (`effects.py:4628` → **`:4664`**, `:4627` → **`:4657`**,
`:5071` → **`:5107`**) — cited below at their current lines. `note_charge_read`
is `tier0/engine/resources.py:270` and the per-turn emit is
`tier0/engine/combat.py:1049`.*

1. **The Garment tallies once per attack PLAY, not per target.** §2's table says
   *"once per attack play per target"*. The tick at
   `tier0/engine/effects.py:4664` sits on the per-card resolution path, outside
   any target loop, so an attack that hits every enemy tallies **one** read.
   Every count below is therefore a count of *resolutions*, not of damage
   applications, and an AoE Garment turn does not inflate it.
2. **The Garment tick is gated on a non-empty bank** (`and p.charge` at
   `effects.py:4657`). A turn played at bank 0 tallies **no** `garment` read
   even though the rider resolved — as zero. The pulse tick
   (`effects.py:5107`) carries **no such gate** and fires every turn the summon
   stands, at bank 0 included. The asymmetry biases the `garment` share
   **downward** on early turns and is a one-way error direction.
3. **`KURAGE_ALWAYS_ON = True` is the shipped v4 base kit.** The jellyfish is
   installed at the start of every one of her combats and never expires, so the
   `kurage_pulse` read is present on **essentially every sampled player turn**
   and is the floor of the distribution, not an occasional term. Every
   prediction below is drafted against that floor. *Re-verified 2026-08-30:
   `KURAGE_ALWAYS_ON = True` (`tier0/constants.py:700`) and the Kurage Memory
   rework is still quarantined OFF (`KURAGE_MEMORY = False`, `:695`), so the
   per-turn pulse this slate is drafted against is the shipped one.*

### 5.1 The derived ceiling — **5 reads per turn**, and how it is derived

The whole slate and the watch trigger hang off one number, so it is derived in
the open, from four things that were all written down before this section:

| the term | the bound | where it is written |
|---|---|---|
| the Kurage pulse | **exactly 1** read per turn while the summon stands | workshop §3.2, *"once per turn while the summon stands. That is already a natural bound"*; `KURAGE_ALWAYS_ON = True` |
| the Garment rider | **at most 1** read per attack **play** | §5.0(1), the tick's own site |
| plays available in a turn | **at most 3**, at base energy on cost-1 cards | `tier0/constants.py:9`, `BASE_ENERGY_PER_TURN = 3` |
| printed proportional readers compatible with three cost-1 plays | **at most 1** | the pool prints exactly three `N_per_M_charge` riders — `all_streams_flow` (cost 1, uncommon, attack), `nereids_ascension` (cost 2, rare, Exhaust, attack), `gyorin_formation` (cost 2, rare, **skill** — no Garment). Only the cost-1 one fits beside two other cost-1 plays |

**Ceiling = 1 + 3 + 1 = 5.** A turn of five reads is the most the printed kit can
produce at base energy with the summon standing, the Garment up, a non-empty
bank and the pool's one on-curve reader in hand. **A turn above five is a turn
whose reads the printed kit's own rate limits do not explain** — it took extra
energy, a cost reduction, or a free play. That is the arithmetic meaning of
"repeatable reads dominating a turn", and it is derived, not picked: change any
of the four rows above and the 5 moves with it.

*Re-verified against code and sheet 2026-08-30 at the re-stamped cell:
`BASE_ENERGY_PER_TURN = 3` still sits at `tier0/constants.py:9`, and
`docs/kokomi-cards.yaml` still prints exactly three `bonus_formula:
1_per_2_charge` rows — `all_streams_flow` (`:416`), `nereids_ascension`
(`:700`), `gyorin_formation` (`:850`) — so all four rows of the table above,
and therefore the **5**, are unmoved by the stamp move.*

### 5.2 What is still [USER]'s

Unchanged by R212 and unchanged here. §4's three PROPOSED slots — **`n` per
archetype (600), the seed, the 1-hour cost ceiling** — are [USER]'s and are
still proposals. The **countersign** is [USER]'s. Every act downstream of a
fired trigger is [USER]'s: §5.4 fires a *candidate*, and nothing in this packet
may nerf, cap, dedupe or budget anything.

### 5.3 The slate — seven slots, one per row of the packet's original §5 table

Every predicate is **pooled across the three archetypes**, which is what the
original table's own rows say (*"pooled"*); the same statistic **per archetype**
is reported beside each and is **graded by nothing**. Every slot names the event
it reads. `charge_reads_turn` carries `total` and `by_source`; `charge_read`
carries `kind`, `card`, `bank`, `turn`. No slot reads a field that does not
exist today.

*Revised 2026-08-30 on the pair review's correction — the share slots read
COMPLETED turns.* `X4`, `X5` and §5.4's composition share previously divided
raw `charge_read` events by raw `charge_read` events, which is **not** a
sample of turns: §2.1's truncation drops the turn that killed the last enemy,
and that turn's attack-side (`garment`, `bonus_formula`) reads still land in
the raw stream while its `kurage_pulse` never does — the pulse rides
`turn_close` behind the same door as the sample. A raw proportion therefore
**over-states the repeatable share by an unknown amount and is a floor on
nothing**. All three now sum `charge_reads_turn`.`by_source` across sampled
(i.e. completed) player turns, so numerator and denominator come from the same
turns. **Instrument fact, verified against code before this revision was
written, requiring no build:** the `by_source` field already exists and is
already per-completed-turn — `tier0/engine/combat.py:1049-1051` emits
`charge_reads_turn` with `total=sum(state.charge_reads_this_turn.values())`
and `by_source=dict(state.charge_reads_this_turn)`; `note_charge_read` tallies
that dict per source (`resources.py:313`) and the turn boundary clears it
(`combat.py:811`). Nothing is added to the emit; the grader sums a field that
ships today. The raw `charge_read` stream keeps exactly two jobs here —
`X7`'s truncation cross-check and `X6`'s play-boundary segmentation, neither of
which is a per-turn share.

| # | slot | prediction, and the intent it is drafted from | falsifier, mechanically | data source | UNREACHED when | the decision the outcome changes |
|---|---|---|---|---|---|---|
| `X1` | **Q1 mean reads per turn, pooled.** The pulse is a floor of 1 on essentially every turn (§5.0(3)); everything above 1 is the repeatable machinery. The Garment holds for only a few turns of a fight and the pool prints one on-curve reader, so the mean should sit just above the floor. | **≥ 1.0 and < 2.0.** | Mean of `charge_reads_turn`.`total` over all sampled player turns. **≥ 1.0 and < 2.0 = PREDICTED; 2.0 to < 3.0 = SPLIT; ≥ 3.0 or < 1.0 = MISS.** | `charge_reads_turn`.`total` | fewer than 5,000 sampled player turns | **PREDICTED**: the typical turn is a pulse turn and the repeatable readers are texture on top — the descriptive number R188's trigger was missing now exists and reads quiet. **MISS high**: the repeatable readers add more than two reads to the average turn, and §5.4's level limb is the thing to look at. **MISS low** (< 1.0): the instrument is not seeing the pulse and the read is INVALID, not quiet — see `X7`'s cross-check. |
| `X2` | **Q1 p90 reads per turn, pooled.** A busy turn is a Garment turn with two attacks landing beside the pulse. That is 3. The ninetieth percentile should reach a busy turn and stop short of the §5.1 ceiling. | **≤ 3.** | p90 of `charge_reads_turn`.`total`. **≤ 3 = PREDICTED; 4 to 5 = SPLIT; > 5 = MISS.** | `charge_reads_turn`.`total` | fewer than 5,000 sampled player turns | **PREDICTED**: nine turns in ten sit at or under a pulse-plus-two-attacks turn. **SPLIT**: the busy turn reaches the printed ceiling but does not pass it — inside what the kit explains. **MISS**: one turn in ten is above what base energy and the printed pool can produce, which is the first evidence the level limb of §5.4 is live. |
| `X3` | **Q1 max reads per turn observed.** The ceiling is 5 at base energy (§5.1). The cell runs a realistic loadout, so one energy potion or relic proc can roughly double the plays in a turn; twice the play budget is `1 + 6 + 1 = 8`, and a doubled-energy turn spending every point on cost-1 attacks with both printed attack readers drafted is about 13. | **≤ 8.** | Max of `charge_reads_turn`.`total`. **≤ 8 = PREDICTED; 9 to 13 = SPLIT; > 13 = MISS.** | `charge_reads_turn`.`total` | never — a max is defined on any non-empty sample | **PREDICTED**: the extreme turn is a one-potion turn and nothing else. **SPLIT**: the extreme turn is inside the doubled-energy envelope; recorded, not escalated. **MISS**: a turn exists that neither base energy nor a doubled-energy turn explains, i.e. a cost-reduction or free-play route is multiplying reads. That is a **BACKLOG** finding about the route, filed with the run's own seed and turn, and it is NOT by itself a Charge finding — the bank did nothing. |
| `X4` | **Q2 share of reads from `garment`, pooled.** The Garment holds for a few turns of a fight and the pulse holds for all of them (§5.0(3)), and the tick is bank-gated (§5.0(2)). The pulse should carry the plurality of all reads. | **< 50%.** | `garment` reads ÷ all reads, **both summed from `charge_reads_turn`.`by_source` over sampled (completed) player turns** — not off the raw `charge_read` stream, which mixes truncated turns' attack-side reads with completed turns' pulses (§5.3's revision note). **< 50% = PREDICTED; 50% to 65% = SPLIT; > 65% = MISS.** | `charge_reads_turn`.`by_source` | fewer than 5,000 reads summed across sampled turns' `by_source` | **PREDICTED**: the naturally-bounded reader is the bulk of the reads, and the composition limb of §5.4 is not live. **MISS**: the Garment — the one unbounded-within-the-turn reader — is most of what reads the bank, which is precisely the composition R188's "repeatable" names. |
| `X5` | **Q2 share of reads from `bonus_formula`, pooled.** Three printed riders in a pool of that size, one uncommon and two rares (one of them a skill), each needing to be drafted and then drawn. This should be the smallest of the three sources by a distance. | **< 15%.** | `bonus_formula` reads ÷ all reads, **both summed from `charge_reads_turn`.`by_source` over sampled (completed) player turns** (§5.3's revision note). **< 15% = PREDICTED; 15% to 30% = SPLIT; > 30% = MISS.** | `charge_reads_turn`.`by_source` | fewer than 5,000 reads summed across sampled turns' `by_source` | **PREDICTED**: the printed readers are a deckbuilding flavour, and the workshop's §6 scope boundary — whether they belong with the kit sources — is worth little either way, which is a finding the boundary question can be closed with. **MISS**: the printed readers are a third of all reads, the §6 boundary is load-bearing after all, and it returns to [USER] as a numbered pick about scope, never as an edit made here. |
| `X6` | **Q3 double-read share of attack plays.** The R188 stack needs one of exactly **two** printed attack readers drafted AND drawn AND played while the Garment holds AND the bank non-empty. Four conditions, each independently unlikely. | **< 5% of attack plays.** | Attack plays carrying **both** a `bonus_formula` and a `garment` `charge_read` inside the same `play` segment, ÷ all attack plays. **< 5% = PREDICTED; 5% to 15% = SPLIT; > 15% = MISS.** | `charge_read` events segmented by `play` boundaries — **NOT by `card` id**, since a card played twice in a turn would collide. The grader must do the segmentation and it is an owed pre-run build (§5.5) | fewer than 1,000 attack plays | **PREDICTED**: the double read is the rare deckbuilding reward R188 ruled it, measured for the first time and behaving like one. **MISS**: the intended stack is a routine event rather than a reward, which is the exact reading R188's deferral said would bring the question back — §5.4's Limb B. |
| `X7` | **Q4 direction of the tail against turn number.** The bank only grows, but the read COUNT is play-shaped, not bank-shaped — so intent says the count rises only through the bank gate of §5.0(2) opening on early turns, and then flattens. A count that keeps climbing with turn number is the shape *"watch act 3"* was written about. | **Mean reads/turn on turns ≥ 6 exceeds turns 1–5, and the gap is < 1.0 read.** | `charge_reads_turn`.`total` bucketed by `turn`. **Rises and gap < 1.0 = PREDICTED; rises and gap ≥ 1.0 = SPLIT; flat or falls = MISS.** Reported beside it, graded by nothing: the same split per act, and **the §2.1 truncation cross-check** — total `charge_read` events against summed `charge_reads_turn`.`total`, which measures exactly how much the killing-turn truncation drops. | `charge_reads_turn`.`total`, `charge_read` | fewer than 2,000 sampled turns at turn number ≥ 6 | **PREDICTED**: reads do not scale with the fight the way the bank does, and the standing *"watch act 3"* caveat is about the SIZE of a read, not the number of them — a distinction that has never been on the record. **SPLIT**: late turns carry a whole extra read; recorded against the act-3 caveat and carried to whoever reads the pulse-size telemetry beside it. **MISS**: the intent is wrong in the direction that matters least (fewer reads late), and §5.4's limbs are unaffected. |

**RECORDED AND NOT GRADED**, in the same report, with no threshold and no
decision attached:

- `R1` the full per-archetype tables for `X1`–`X7`, and the `mean / p50 / p90 /
  p99 / max` set §3's Q1 asks for in full rather than at `X1`–`X3`'s three
  points.
- `R2` the same statistics per `kind`, which is §3's Q2 in full.
- `R3` the bank size at read time (`charge_read`.`bank`) — its distribution, and
  its median at a `garment` read against a `kurage_pulse` read. **This is a size,
  not a count. No slot grades it and no trigger reads it**; it is here because
  the pulse-size telemetry of workshop §3.2 already exists beside it and a
  reader of this report will ask.
- `R4` the §2.1 truncation magnitude as an absolute count of dropped turns.

**Contamination and blind spots, stated before the run.**

1. **§2.1's truncation.** The final turn of most fights contributes no sample and
   the loss is toward the BUSY end. Every **count** above — `X1`–`X3`'s levels
   and `X7`'s buckets — is therefore a **floor**, and `X7`'s cross-check is the
   only measurement of how much of a floor. *Revised 2026-08-30 on the pair
   review's correction: **the SHARES are not floors in either direction.**
   `X4` and `X5` are proportions, and a proportion moves both ways when a turn
   is dropped — which is also why they now read completed turns' `by_source`
   rather than the raw stream (§5.3). A dropped turn removes its pulse and its
   attack-side reads together, so a share computed on completed turns is an
   estimate with an unsigned error, not a bound; only its inputs are bounded.*
2. **Pilot-shaped, not player-shaped** (§8). The pilot does not steer toward a
   Garment turn, does not hold a printed reader for a Garment window, and does
   not sequence attacks to stack reads. A human who plays toward the double read
   can only make `X4` and `X6` larger. Every slot's MISS is therefore worth more
   than its PREDICTED, and `X6` most of all.
3. **One seat, and the sim is not the mod** (§8). Nothing here is a claim about
   co-op or about the C# Kokomi.
4. **No number taken off this read is quotable as balance** (R213 B / R215 B,
   Guardrail-7). This measurement grades no design and cannot fire a nerf; §5.4
   fires a *candidate*.
5. **The three archetypes differ in exhaust rate and reader density** (§4), so
   the pooled predicates can be carried by one arm. `R1` is the check on that
   and is why the per-archetype tables are reported even though nothing grades
   them.

### 5.4 `W9` — the watch trigger, made a number

R188 returned `X9` to the watch register with its trigger in words: *X9 returns
only after a reads-per-turn reading or a live playtest shows repeatable reads
dominant.* This is the section that makes "dominant" a number.

**"Repeatable reads" is defined by the workshop, not chosen here.**
`kurage_pulse` is **not** repeatable — workshop §3.2 calls its once-per-turn
frequency *"already a natural bound"*. `garment` (*"unbounded within the turn"*,
§3.1) and `bonus_formula` (one per play of a reader card, §3.3) **are**. So
**repeatable = `garment` + `bonus_formula`**, and that is a reading of the
workshop's own words rather than a pick.

**`W9` FIRES — `X9` returns to [USER] at QUEUE as a numbered pick — if EITHER
of the following holds on the graded report. Nothing else fires it.**

**Limb A — the composition is dominated. ONE condition, and it fires by
itself:**

- **A, the composition: `garment` + `bonus_formula` together are `> 50%` of all
  reads, summed from `charge_reads_turn`.`by_source` over sampled (completed)
  player turns** (§5.3's revision note — not the raw `charge_read` stream).
  "Dominant" in plain English is *more than half*, and there is exactly one
  non-repeatable reader for them to be more than half of.

**Reported alongside any firing, as a SEVERITY INDICATOR and not as a
condition: `p50` reads per sampled player turn, and whether it exceeds §5.1's
derived ceiling of 5.** A firing with `p50 > 5` is a loud one — the *median*
turn contains more reads than the printed kit can produce at base energy with
everything live. A firing with `p50 ≤ 5` is a quiet one: the composition has
tipped while the level has not. Both fire; the indicator tells [USER] which
kind of question is coming back, and it grades nothing on its own.

*Revised 2026-08-30 on the pair review's correction: `p50 > 5` was a mandatory
conjunct beside the composition share, and the conjunction carried far too much
false-negative risk for what firing actually does. **Firing merely returns the
question to [USER] as a numbered pick** — it nerfs nothing (see "A candidate,
not a verdict" below) — so a trigger that stays silent while the repeatable
readers carry most of the bank's reads, purely because the median turn is
short, fails at the one job R188 gave it. The old defence of the conjunction
was that A2 alone "fires on any run where the summon happened not to stand";
that is now handled where it belongs, in the reading rather than the predicate:
a firing report states the `kurage_pulse` share and the count of sampled turns
carrying no pulse, so a composition tipped by an absent summon is visible on
its face. The level survives as the severity indicator above, unchanged in
definition and still the pooled `p50` of §3's Q1, recorded at `R1`.* `X4` and
`X5` carry the firing quantity; §3's Q1 statistics carry the indicator.

**Limb B — the ruled double read has become the baseline: the `X6` share of
attack plays is `> 50%`.** R188 ruled the double read *intended stacking*
because it is a deckbuilding reward — two cards, drafted and drawn, played
inside a Burst window. A stack that lands on **most** attack plays is no longer a
reward; it is the default, and the thing R188 ruled on has changed shape. Fifty
percent is the same plain-English *dominant*, applied to the quantity R188's own
sentence is about.

**Expressible in §3's columns, as the packet requires.** Limb A is §3's Q2
shares; Limb B is §3's Q3; the severity indicator is §3's Q1 `p50`. No limb
names a quantity this measurement does not produce, and nothing is added at
grading time.

**A candidate, not a verdict.** Firing `W9` mints a QUEUE row and reopens the
question. It nerfs nothing, caps nothing, dedupes nothing and budgets nothing.
Whether Charge changes is a design act, downstream, and [USER]'s — and the
`strict=True` xfail on `EB-78`'s row is what stops the suite if a cap, a dedupe
or a late budget ever lands without one.

**THE ONE JUDGEMENT CALL, flagged in place** (*restated 2026-08-30 with the
`p50` demoted — the call moved with it, it did not disappear*). The **5** is
derived (§5.1) and the **50%**s are the plain meaning of *dominant*. What is
**judged** is that the **severity indicator** rides the `p50` rather than the
mean, the `p90` or the `p99`. §2.1's truncation drops the final turn of most
fights and drops it toward the **busy** end, so the observed upper tail is the
least trustworthy part of this distribution and the median is the statistic the
truncation corrupts least — which is why the median is the honest thing to
report beside a firing. **What is no longer judged is the trigger's own
sensitivity:** the median used to gate the firing, and hanging the gate on the
most truncation-resistant statistic made `W9` harder to fire in a direction
nobody had priced. Now the level cannot suppress a firing at all; it only
labels one. **If [USER] prefers the level back as a conjunct, or a tail
statistic as the indicator, that is a revision at the countersign and this is
the paragraph to revise.**

### 5.5 What is owed BEFORE the run, in this order

Nothing here has been built and nothing has been run.

1. **The countersign** (batch), on §5.3, §5.4 and §4's three PROPOSED slots.
2. **The grader**, committed in its own commit before the run: every falsifier
   above must be one of its printed fields, including `X6`'s `play`-boundary
   segmentation, which the instrument does not do for it (§5.3, `X6`'s data
   source). *Added 2026-08-30 with the share revision:* the grader sums
   `charge_reads_turn`.`by_source` over completed turns for `X4`, `X5` and
   §5.4's Limb A — a field that already ships, so no emit-side build is owed —
   and it prints, beside any `W9` firing, the `p50` severity indicator, the
   `kurage_pulse` share, and the count of sampled turns carrying no pulse.
3. **The stamp check** (§4): if the open `RT`/`C` window moved since drafting,
   the packet is re-stamped **before** the freeze and the move is disclosed.
4. **The run**, then **blind grading** against §5.3 without editing it, in §6's
   fixed order. If `W9` fires, a QUEUE row is minted and nothing else happens.

---

## 6. Grading

**Blind.** The runner writes one report; grading compares it against §5 without
editing §5. The predictions commit exists before the run is launched, and the
report is not opened by the author of the predictions before the grade is
recorded.

Order: (1) the batch countersign, (2) the grader lands as its own commit — the
predictions themselves already stand, drafted from written intent and committed
under R212(2) before anything ran, (3) run,
(4) grade blind, (5) the grade goes on the `EB-78` row and, if §5.4's trigger
fires, a QUEUE row is minted. Nothing reorders.

## 7. Sequencing — when this may run

It takes its slot **after** the payoff-reach sprint's graded read, on the same
settle-first plan every other queued registration honours
(`EXPERIMENTS.md`, §6.6's approved `P12`). It moves no version and opens no
window, so it does not compete for the `RT`/`C` window itself — but it must not
run *inside* the payoff-reach freeze either, because its runs are sim time on
the same machine and the freeze's dependency re-check is what establishes the
world it would be stamped against.

## 8. Known limits, declared

- **One seat.** The sim models one player. Co-op read counts are unmeasurable
  here and no co-op claim may be drawn from this.
- **The sim is not the mod.** The C# counterparts of all three readers are
  named in workshop §3 and the constants are compared by value by the parity
  lint, but this instrument exists sim-side only. A distribution measured here
  is a claim about the sim's Kokomi.
- **Pilot-shaped, not player-shaped.** Reads per turn are produced by the
  pilot's play, and the pilot is not a person. Guardrail-7's shape applies: a
  number here is a floor on what a competent player would produce, not a
  description of one.
- **§2.1's truncation.** Stated again here so a reader who starts at §8 meets
  it.

## Countersign line — one word, [USER]: COUNTERSIGN / REVISE / DECLINE

> **[ ]**
