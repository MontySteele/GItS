# Sprint log — the Fanfare compensation (2026-07-28)

Brief: `docs/sprint-fanfare-compensation-2026-07-28.md`. Parent: the Fanfare
rework (`a197294`) and its log. Delegated BALANCE pass; every direction RULED
by [USER], every number PROPOSED unless marked otherwise.

World: **RT7/D12/P3/C4**, seed 11, 600 runs/arm, hunter route, assigned policy,
relics + potions. Batteries: `python -m tier05.exp_fanfare_compensation`
(NEW, registered here), `python -m tier05.exp_pilot_gap p1` and
`python -m tier05.exp_roster_anchors --runs 600 --jobs 0`. Each was run BEFORE
at `a197294` and AFTER at this commit, so no row in this log is quoted across
a version bump.

---

## The headline: the stop condition FIRES

The brief registered two before-numbers and said the sprint's success
question is whether **they** move.

| registered number | before | after | verdict |
|---|---|---|---|
| **fanfare arm winrate** | 0.5% | **1.8%** | 3.6x, and **still under the 2.0% roster floor** |
| **fanfare arm act-1** | 44.7% | **55.3%** | +10.6 points |

> **REPORT AND STOP.** The brief's own clause: *"If the fanfare arm still sits
> below the 2.0% floor after this pass, REPORT AND STOP — a second round is a
> ruling, not a judgment call."* It sits at 1.8% against real_silent's 2.0%.
> Nothing further ships from this brief. The gap is now 0.2 points rather than
> 1.5, which is a different conversation from the one the brief opened with,
> but it is [USER]'s conversation.

The battery prints this verdict itself rather than leaving it to prose —
`exp_fanfare_compensation.c1` evaluates the floor test and says which way it
went, so the stop condition cannot be quietly not-noticed by a later reader.

## The leak is real, and it is bigger than the winrate repair

The brief flagged one card as dangerous — `aria_of_recompense`, the STARTER,
which is in every Furina deck — and asked for all three arms so a
compensation aimed at one archetype could be seen landing on the others.
It landed on the others.

| arm | before | after | Δ |
|---|---|---|---|
| furina **fanfare** | 0.5% / 44.7% | 1.8% / 55.3% | +1.3 / +10.6 |
| furina **salon** | 7.7% / 51.7% | **10.8%** / 58.3% | **+3.1** / +6.6 |
| furina spotlight | 2.8% / 57.7% | 2.3% / 57.5% | −0.5 / −0.2 |
| furina salon *(stoker)* | 14.5% / 76.8% | **20.3%** / 77.5% | +5.8 / +0.7 |

**Salon gained more than twice what the target archetype gained.** It was
sitting on real_ironclad's 7.8% anchor — the landing the rework ruled
acceptable — and is now above ref_ironclad's 10.2%, the highest non-Klee row
on the board. Under the stoker it is 20.3%. Whatever else this pass did, it
moved the arm it was told not to move.

Every **non-Furina** row is byte-identical across the change (klee 7.5 / 6.8 /
11.7, kokomi 2.8 / 2.5 / 0.0, ref_ironclad 10.2, real_ironclad 7.8,
real_silent 2.0), which is the standing proof the change is Furina-only.

### The ablation: which half of the pass did it

Not asked for by the brief. Run because "the starter is the first suspect" is
a hypothesis, and one battery turns it into an attribution. The arm below is
the full pass with **only** the `aria_of_recompense` rider removed.

| arm | before | ablated (no starter rider) | full pass |
|---|---|---|---|
| fanfare win | 0.5% | **1.8%** | 1.8% |
| fanfare act-1 | 44.7% | 47.5% | **55.3%** |
| salon win | 7.7% | **9.8%** | 10.8% |
| salon act-1 | 51.7% | 52.2% | **58.3%** |

Three things fall out, and none of them was predictable from the brief:

1. **The starter rider contributes ZERO of the fanfare winrate repair.** All
   of 0.5% -> 1.8% comes from the three new commons and the two conversions.
2. **The starter rider is almost the entire act-1 movement** — +7.8 points on
   fanfare and +6.1 on salon. The brief called it "the act-1 lever" and it is
   exactly and only that.
3. **The starter rider is NOT the main leak.** Salon moved +2.1 points before
   the starter is added and +1.0 after it. The larger share is the reader
   density itself reaching salon decks: `hearts_swelling` is tagged
   `[fanfare, salon]`, and the three new commons carry `generic` so the
   drafter offers them to every plan. A "fanfare-only" compensation was never
   available through the pool, because the pool is drafted, not assigned.

So the obvious red-pen move — pull the starter rider to protect the anchor —
would cost 8 points of act-1 and keep two thirds of the leak. That is the
trade, stated before anyone has to re-derive it.

---

## Track 1 — Fanfare Cap +X on every Power

RULED, reversing the rework's short list. Twelve Powers gained
`raise_fanfare_cap`; the three rare-Power `Fanfare +X` payoffs are untouched.
Magnitudes PROPOSED, and chosen to restore the retired invisible rule as
printed text: **+5 at common/uncommon, +8 at rare**.

| | carriers |
|---|---|
| `Fanfare +X` (full grant, R6) | unheard_confession, the_sea_is_my_stage, rapturous_applause |
| `Fanfare Cap +X`, already carried | courtroom_drama, crowd_work |
| `Fanfare Cap +X`, **added here** | casting_call, grand_salon, pit_orchestra, leading_role, supporting_cast, top_billing, standing_ovation, fortissimo_guard, quick_change, endless_waltz (8), star_of_the_show (8), prima_donna (8) |
| non-Powers that may carry the cheap half | lasting_impression, reginas_mercy |

**Known and accepted, per the brief: this is mostly legibility.** Read-at-cap
measured 0.1–0.2% across every arm. The cap is not a binding number and this
pass did not try to make it one.

### The lint had to move, and it moved forward rather than sideways

R2 sends Fanfare **reads** to the archon register. `raise_fanfare_cap` joined
R2 at the rework, where it did real work: the keyword went on a short list and
R2 *was* the selector that produced it. Under this ruling every Power prints
it — so the rule now selects nothing, and left in place it would have forced
twelve salon and private Powers to rename into a voice they do not speak.

It was **released from R2** and replaced by **R7**, which is the ruling stated
positively: *every Power prints exactly one Fanfare keyword.* That is a rule
about card TYPE, which is what the ruling actually made it, and it is the
first time this property has been checkable at all:

- before the rework, every Power granted floor and no card said so;
- after the rework, four Powers granted and twelve granted nothing — also
  invisible, because "which Powers grant" was a curated list;
- now the card type decides, the face says so, and the next Power authored
  without a keyword is a blocker.

### lasting_impression: no reprice shipped

The brief invited one *if it fell out naturally*. It does not. Every candidate
is either more blind Encore — the exact disease this pass's diagnosis names —
or a reader clause, which is a redesign and out of scope by the brief's own
words. What the card needs is a body, and that is a ruling. Recorded on the
card so the next reader does not re-derive the dead end.

---

## Track 2 — reader density at the bottom of the curve

Pool 79 -> 82. Commons 20 -> 23. `blocked` held at 2.

### The three new commons (2.1 and 2.3)

| card | register | cost | body |
|---|---|---|---|
| **Applause Line** `applause_line` | archon | 0 | Deal 3 damage. +1 per 4 Fanfare. |
| **The House Holds Its Breath** `held_breath` | archon | 1 | Gain 4 Block. +1 per 4 Fanfare. |
| **Breathless** `breathless` | private | 1 | Spend 4 Encore. Deal 9 damage. |

`1_per_4` is the commons' tier and it is a rule, not taste: the rares own
`1_per_2` (crescendo, high_tide, thunderous_ovation) and a common on the rare
rate makes the rare's steeper number worthless. Pinned as a test.

Two judgment calls inside these rows:

- **Applause Line is cost 0 because `dramatic_entrance` exists.** Same rate,
  same rail, one rarity up. A 1-cost common body would have been its strictly
  worse twin; at 0 cost it is a different card, and it is the act-1 shape the
  diagnosis asks for — the thing you play *alongside* the battery that already
  ate your energy. It is a PLAIN attack, so no hydro: a 0-cost damaging skill
  would hand the archetype free application every turn, which is a
  reaction-economy buff wearing a reader's clothes and would have confounded
  this sprint's own measurement.
- **Breathless converts to DAMAGE, not Block.** The brief named the Slip
  Backstage shape, but `graceful_retreat` is already the Encore->Block
  converter *and already common*, so a second one is the same card twice. Act 1
  is lost by not killing things, and a second wall does not kill anything.

### The two conversions (2.2)

- **`suffering_for_art`** gains `Gain 1 Block per 4 Fanfare` (base 0). It
  already self-damages, and HP loss is the meter's largest source, so the card
  now closes its own loop on one face — take the wound, print the meter, read
  the meter. It is the only card in the pool that both pays Fanfare and cashes
  it. Base 0 is the price: a printed base on a 0-cost common the archetype
  plays every turn would be a free repeatable wall.
- **`hearts_swelling`** gains `Gain 3 Block. +1 per 4 Fanfare.` The base 3 is
  the fix, not decoration: this card is INNATE, so its guaranteed play is turn
  one into an empty meter, and a pure scaling clause would have been a printed
  reader with a near-zero fire rate on the one turn the card is promised to be
  in hand. That is the D4 mistake the brief warns against re-shipping.

Both flipped register private -> archon, and **the lint forced it**: R4 held
them private only while every leaf op was Encore, and R2 sends any Fanfare
read to the archon voice. Two rules changed their answer on the same edit.

### The starter (2.4)

`aria_of_recompense`: `Gain 5 Encore. Gain 1 Block per 4 Fanfare.` Register
private -> archon by the same pair of rules.

**Why the rider and not the brief's other option, the "Fanfare +2"
front-load:** +2 floor is below the granularity of every reader on the sheet.
They are all per-2 or per-4, so a permanent 2 buys one point on the steepest
rate in the pool and literally zero on the common tier this pass just built.
It would have shipped as a printed no-op. (It would also have needed R6
amended to let a basic print a keyword ruled to be a rare-POWER payoff one day
earlier.)

---

## Track 3 — the measurement

### Fire-rates: no reader under 10%, so no D4 re-ship

The brief asked for a fire-rate on every new or changed reader and named 10%
as the re-ship threshold. The conditional telemetry cannot answer this: a
`bonus_formula` always evaluates, so "did it run" is the wrong question.
**PAID** is the right one — did the slope return at least 1
(`max(0, read) // step >= 1`). Per-card read samples were added to the Fanfare
telemetry to make it answerable at all.

| card | fanfare arm | fanfare (stoker) | salon arm |
|---|---|---|---|
| applause_line | 70.4% | 62.5% | 66.3% |
| held_breath | 82.9% | 78.1% | 81.5% |
| suffering_for_art | 76.2% | 67.6% | 77.4% |
| hearts_swelling | 51.7% | 45.6% | 50.9% |
| aria_of_recompense | 75.7% | 61.9% | 70.9% |

The lowest is `hearts_swelling` at 45.6%, and it is low for the reason its own
card comment predicts — it is innate, so a large share of its reads are the
turn-one read into a cold meter. That is what the base 3 is for.

### The meter is being read now

Reads per fight, fanfare arm: **24.2**. Mean at read 10.4. Read-at-cap 0.2%
(the cap is still not binding). Read-empty 22.6% — roughly a fifth of reads
still land on nothing, which is the residue of the act-1 problem rather than
its cure.

Generation by source, fanfare arm: hp_lost 43.0%, center_stage 25.9%,
encore_absorbed 22.0%, encore_spent 9.0%. Under the stoker the spend leg
roughly doubles (16.0%) and center_stage collapses (7.7%) — the stoker holds
the Spotlight differently, which is a known pilot property, not a card effect.

---

## Gates

| gate | result |
|---|---|
| full-repo pytest | **1400 passed** (1385 before) |
| regen | clean, `blocked` **held at 2** |
| register lint | 0 violations across 82 cards, R7 live |
| structural lint L1/L2/L3 | CLEAN, 208 generated cards |
| constant parity | OK (71 mirrored, 16 declared unmirrored) |
| strict domination | CLEAN (one informational rare-over-common, R26) |
| distinctness gate | no new breaches |
| upgrade coverage | OK, 264 draftable cards, 0 codegen debt |
| sheet comments / unique names / pool membership | CLEAN |
| art_lint | plan OK |
| art_coverage | 266/271 — 5 owed (casting_call, take_your_bow + the 3 new) |
| `dotnet build` | 0 errors |
| `validate.ps1` | **validate: OK**, deployed |
| bite-check | **14 patch classes armed** |

**No new codegen surface.** Every card this pass added or rewrote is built
from ops the generator already emits — which is what "reader density" means
mechanically: more cards on the rails the rework built, not more rails.

### Mutations run (each reverted, each seen to fail)

1. Strip `raise_fanfare_cap` off a Power -> R7 fires and names the card. (This
   one is a permanent red test, not a one-off: it builds its mutation itself
   and asserts the message, so it fails for the right reason.)
2. Drop the `rarity != basic` filter in `draft._drafted_readers` -> the drafter
   test and the m5 core test both go red.
3. `hearts_swelling` base block 3 -> 0 -> the innate-turn test goes red.
4. Readers read the raw field instead of `resources.readable` -> the clamp test
   plus eleven others go red.

---

## Judgment calls made without red-pen

1. **R2 released `raise_fanfare_cap`; R7 replaces it.** The brief said "re-derive
   or relax, do not leave the lint fighting the ruling". Relaxing alone would
   have left the ruling unenforced, so it was re-derived as a positive rule.
2. **Cap magnitudes restore the retired invisible rule** (+5 / +8) rather than
   proposing fresh numbers. It is the most red-pennable choice: the reader can
   compare against something.
3. **`lasting_impression` got no reprice**, with the dead end recorded.
4. **Breathless converts to damage rather than Block** (distinctness + act-1).
5. **Applause Line is 0-cost and a plain attack** (distinctness + not smuggling
   an application buff into the measurement).
6. **The fanfare deck package was swapped one-for-one, not grown.** Out:
   one `curtain_up`, `ebb_and_flow`, `tempo_change`. In: the three new commons.
   Growing 17 -> 20 would have moved every seven-axis score by deck size and
   credited the new cards for it. This does move the `fanfare_weighted` A2
   band, which is already flagged stale and stays stale. It does **not** move
   the run-level fanfare arm: that arm drafts from the pool.
7. **The ablation arm was run although the brief did not ask for it**, because
   "first suspect" is worth converting into an attribution before it is quoted
   as a fact.
8. **`aria_of_recompense` and `hearts_swelling` are now a measured neardup
   pair** (`block~`). The distinctness gate passes and the bodies differ
   substantially — 5 vs 7 Encore, basic vs innate uncommon, base 0 vs base 3 —
   but the instrument sees one clone pair that this pass created, and that is
   said here rather than left in a report nobody re-reads.
9. **A test that asserted `suffering_for_art` is a blind generator was rewritten
   to name `ebb_and_flow` instead.** Standing on it would have been asserting
   that this sprint had not happened.
10. **Per-card read telemetry was added to `fanfare_telemetry`** to answer the
    brief's fire-rate question at all. The pooled `read_values` bag cannot: a
    dead reader and a live one average into a healthy-looking number.

## A process note that cost real time

Mid-sprint I reverted a mutation with `git checkout <file>` and destroyed my
own uncommitted work in `docs/furina-cards.yaml` and `tier05/draft.py`. Both
were reconstructed and verified — regen produced the identical generated set,
the register lint and all 1400 tests pass — but the correct method for a
mutation on a dirty tree is a backup copy, and every mutation after that one
used `cp`. Recorded because the failure mode is silent: `git checkout` reports
success while deleting an hour of edits.

---

## Still owed / routed onward

- **The fanfare arm at 1.8%, still under the 2.0% floor.** Report and stop; a
  second round is a ruling.
- **The salon arm at 10.8%, off the anchor it was ruled onto.** The ablation
  above is the attribution; the lever choice is [USER]'s.
- **Every X in this pass is PROPOSED and unswept** — the twelve cap numbers,
  the three new commons' bodies, both conversion clauses, the starter's rate.
- **Art is owed for five cards**: casting_call, take_your_bow, applause_line,
  held_breath, breathless.
- The `fanfare_weighted` A2 band is now doubly stale (the package moved).
- Spotlight at 2.3% remains the roster's structural problem and no card in
  this pass was aimed at it.

## What must be said when quoting any of this

Every table is stamped and names its pilot. Track 1 and Track 2 were measured
**together** — there is no arm that isolates the cap keyword, and the fire-rate
table shows why one was not flown: the cap binds 0.2% of reads, so an ablation
would have measured noise. The one ablation that exists isolates the STARTER
RIDER and nothing else; it does not license any claim about the three new
commons individually.
