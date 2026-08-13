# Charge reads per turn — a descriptive distribution: DRAFT

> **STATUS: DRAFT. NOT COUNTERSIGNED. UNRUN.** §5's prediction slots are
> [USER]'s and are **blank**. Nothing in this packet may be run until they are
> filled and the packet is countersigned — the same gate every registration in
> `docs/current/EXPERIMENTS.md` sits behind.
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

- **Cell:** `RT10/D14/P7/C9` at the time of drafting. Stamp law applies —
  **if the open `RT`/`C` window moves before this runs, the packet is
  re-stamped before the freeze, not after the read.**
- **Character:** `kokomi` only; the bank is hers. All three archetypes
  (`priest`, `commander`, `assist`), reported separately, since exhaust rate
  and reader density differ per plan.
- **Pilot / drafter:** the standing values for the cell, unchanged. This
  measurement moves no version and opens no window.
- **`n` per archetype — [USER] slot.** PROPOSED at **600 runs per archetype**,
  the ratified cell's figure, giving three arms and 1,800 runs. The quantity is
  per-TURN, so the turn count is roughly two orders of magnitude larger than the
  run count and the tail statistics are the binding constraint, not the mean.
- **Seed — [USER] slot.** PROPOSED at the cell's standing seed, recorded in the
  fill.
- **Cost ceiling — [USER] slot.** PROPOSED at **1 hour wall-clock,
  stop-and-report.** A partial result is graded as partial and quotes the turns
  it actually covered.

## 5. Predictions — **BLANK. [USER]'s, before any number is read**

Per `docs/current/EXPERIMENTS.md`: a measurement is *"pre-registered from design
intent"* and *"never revised against the playtest that grades it"*, and
predictions are authored design-side and appended **as their own commit before
any measurement runs**. The house precedent for a *descriptive* measurement is
`review/active/regret-margin-registration-2026-08-12.md`, whose prediction slots
are likewise explicit [USER] slots and likewise blank. Drafting them here would
be the retro-fit the law forbids, so the cells below are empty.

| quantity | [USER]'s prediction | the threshold that would count as a real move |
|---|---|---|
| Q1 mean reads/turn, pooled | **[USER]** | **[USER]** |
| Q1 p90 reads/turn, pooled | **[USER]** | **[USER]** |
| Q1 max reads/turn observed | **[USER]** | **[USER]** |
| Q2 share of reads from `garment` | **[USER]** | **[USER]** |
| Q2 share of reads from `bonus_formula` | **[USER]** | **[USER]** |
| Q3 double-read share of attack plays | **[USER]** | **[USER]** |
| Q4 direction of the tail vs turn number | **[USER]** | **[USER]** |

### 5.1 The watch trigger — **[USER] slot**

R188 returns X9 to the watch register and names its trigger in words: *X9
returns only after a reads-per-turn reading or a live playtest shows repeatable
reads dominant.* **"Dominant" is not yet a number, and this is the slot that
makes it one.** [USER] writes the reading of this measurement that would reopen
X9 — a level, a tail, a share, or an explicit "none of these, it takes a
playtest."

Two constraints, the standard ones:

- **A trigger must be expressible in §3's columns**, or it cannot be graded as
  registered. A trigger naming a quantity this measurement does not produce
  needs a re-registration, never a metric added at grading time.
- **The trigger names a candidate, not a verdict.** Firing it reopens the
  question at QUEUE; it nerfs nothing by itself. Whether Charge changes is a
  design act, downstream, and [USER]'s.

## 6. Grading

**Blind.** The runner writes one report; grading compares it against §5 without
editing §5. The predictions commit exists before the run is launched, and the
report is not opened by the author of the predictions before the grade is
recorded.

Order: (1) countersign, (2) predictions land as their own commit, (3) run,
(4) grade blind, (5) the grade goes on the `EB-78` row and, if §5.1's trigger
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
