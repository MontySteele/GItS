# Furina strength battery — findings (2026-07-28)

> # ARCHIVE BANNER — the Furina rows here are pre-CONSTANTS-5
>
> **Appended 2026-08-06 (Track W). Every Furina tier-0.5 number in this
> document was measured under `CONSTANTS_VERSION 4` or earlier and is NOT
> comparable to output taken under 5. Quote these rows only with that label
> attached.**
>
> `CONSTANTS_VERSION` 4 → 5 was **APPROVED by [USER] on 2026-08-06** (reply to
> the Second Wind open one-liner (3),
> `docs/surplus-week-manifest-2026-08-05.md`) for **R110's S-1 erratum, family
> X3**: `encore_performance` lost its `{op: energy}` refund and its printed
> cost moved 1 → 0. A Furina **rare** that changed cost and stopped returning
> energy re-prices the turns of every Furina deck that could ever be offered
> it — her energy curve, not one cell. Under the constant's own comparability
> criterion (stated at the v2 bump, restated at v4: *the size of the edit is
> not what decides, comparability is*) and on the **R87(3) precedent** that a
> stamp bump archives every number the stamp governs, **every Furina row here
> is archive — not a cheaper sample of the same world.**
>
> **Nothing above or below is rewritten** (R101b): the numbers stand exactly as
> published, with this note on top. **Non-Furina rows are untouched by the
> bump** — Klee, Kokomi, `ref_ironclad`, `real_ironclad` and `real_silent`
> draft no Furina card, and neither `DRAFTER_VERSION` nor `RUNTEMPLATE` moves
> (no offer-time price and no map shape changed). The **Furina re-baseline is
> a COMPUTE decision for the next measurement sprint**; nothing was
> re-measured for this banner and none is owed by it. Source of the bump:
> `tier0/constants.py`, the `CONSTANTS_VERSION 5` note.

Input: playtest 3 (`docs/playtest3-notes-2026-07-28.md`) — "trivially crushed
ascension 0", 80-90 Fanfare, 6-7 cards/turn. Three theories were put forward.
Battery: `tier05/exp_furina_strength.py`, 150 realistic runs per cell, seed
20260728, DRAFTER world as shipped. Every sweep runs through the gated
`sweeps` harness, so no row here comes from a knob that was never read.

**Nothing has been changed.** This is R14 diagnostics feeding a ruling.

---

## The short version

| theory | verdict |
|---|---|
| **T1** Fanfare gives too much | **VERDICT REVISED** (see S6/S7). Three cuts at the Fanfare channel came back shallow — but all three were taken in a sim world whose decks run **2.4 powers**, and the real ramp is a per-POWER floor rule. The lever exists; it is `FANFARE_FLOOR_PER_POWER`, not the Focus divisor and not the cap. |
| **T2** Encore is too easy to build | **SUPPORTED, and it is the load-bearing one** — but not for the reason proposed. Encore is not strong because it makes Fanfare; it is strong because it is what PAYS THE STAGE'S BILL. |
| **T3** Archetypes collapse into good-stuff piles | **NOT WHAT IS HAPPENING.** Focused drafting beats good-stuff 3:1. The problem is the opposite shape: **monoculture** — one archetype works and two do not. |

And the calibration that makes "too strong" a measurable claim rather than an
impression:

| arm | winrate | vs ref Ironclad |
|---|---|---|
| **furina / salon** | **16.7%** | **1.7x** |
| ref_ironclad | 10.0% | 1.0x |
| klee | 8.0% | 0.8x |
| real_ironclad | 6.0% | 0.6x |
| furina / spotlight | 2.0% | 0.2x |
| furina / fanfare | 1.3% | 0.1x |
| kokomi | 1.3% | 0.1x |

The table's read is confirmed in the model: salon Furina is the strongest
thing on the roster, 1.7x the frozen reference and 2.1x Klee. Her other two
archetypes are at Kokomi's floor.

---

## S0 — does the sim reach the state that broke?

No, and the gap is large enough to matter.

| arm | act | Fanfare HELD | GENERATED/turn | cards/turn |
|---|---|---|---|---|
| salon | 1 | 11.9 | 4.2 | 3.97 |
| salon | 2 | 21.8 | 6.5 | 4.00 |
| salon | 3 | 28.3 | 8.8 | 4.16 |
| fanfare | 3 | 24.2 | 8.4 | 4.35 |

The table's 80-90 is **2.8x** the sim's held Fanfare and **9.1x** its
generation per turn; 6-7 cards/turn is **1.6x** the sim's 4.2.

**"80-90 Fanfare per turn" is ambiguous and the two readings differ by a
lot.** Held is what the Focus term reads; generated-per-turn is throughput.

> **CORRECTION (same day, after [USER] flagged it).** This section originally
> said only three cards raise the floor or cap, so a HELD 80-90 would need
> ~160 max HP. **That was wrong**, and wrong in the way a census is wrong
> when it counts the wrong thing: the dominant floor source is not a card
> effect at all. **It is a rule — playing any POWER permanently raises the
> floor** by `FANFARE_FLOOR_PER_POWER` (5, or 8 for a rare), and the grant
> raises the floor, the cap AND the current value together. The pool holds
> **17 powers**. A deck that plays ten is +50 to +80 floor and the same
> again on the ceiling, which is the reported band exactly — so the report
> is **HELD**, no unusual max HP required. See S6 and S7.

Consequence for everything below: the sim's ABSOLUTE winrates are not
evidence about the table's game. The deltas are.

---

## S1 / S1B / S1C — three cuts at Fanfare, all shallow (T1)

**S1, the Focus term itself.** `SALON_FOCUS_PER` is the divisor turning held
Fanfare into member numbers; lower means more scaling.

| FOCUS_PER | winrate | dmg/fight |
|---|---|---|
| 5 (2x scaling) | 18.7% | 118.7 |
| **10 (shipped)** | **16.7%** | **115.5** |
| 20 | 15.3% | 114.0 |
| 40 (¼ scaling) | 13.3% | 111.6 |

An **8x** change in the scaling rate moves winrate 5.4 points and damage 6%.
Real, but nothing like the lever T1 describes.

**S1B, the ceiling.** The obvious objection to S1 is that the sim never gets
to high Fanfare, so it understates a term whose value is proportional to
Fanfare held. So raise the ceiling instead:

| CAP_FRACTION | winrate | mean held | reads at cap |
|---|---|---|---|
| **0.5 (shipped)** | **16.7%** | **20.4** | 0.4% |
| 1.0 | 17.3% | 21.1 | 0.0% |
| 2.0 | 17.3% | 21.1 | 0.0% |
| 4.0 | 17.3% | 21.1 | 0.0% |

**An 8x ceiling raise changes nothing.** Held Fanfare goes 20.4 → 21.1 and
then stops moving. The cap is not what limits her; **generation is**. Any
"make the ramp harder to build" ruling has to act on generation, and the cap
is the wrong knob to reach for.

**S1C, where the Fanfare comes from.** Every point of Encore prints Fanfare
twice — once gained, once spent — and 19 of 78 cards grant Encore. So sweep
both channels together, ending at the counterfactual where Encore stops
feeding Fanfare at all:

| per gained | per spent | winrate | mean held |
|---|---|---|---|
| **1** | **1 (shipped)** | **16.7%** | **20.4** |
| 1 | 0 | 16.0% | 18.3 |
| 0 | 1 | 14.7% | 15.9 |
| 0 | 0 | 15.3% | 14.1 |

Cutting the Encore economy out of Fanfare **entirely** removes 31% of her
Fanfare and costs 1.4 points of winrate. The Fanfare channel is not what
makes her strong.

---

## S6 / S7 — the ramp is POWERS, and the sim never builds that deck

**Is the cap still in the shipped build?** Yes, and no. `FanfareCap` is live
at `MaxHp/2 + grants`, but F-A5 **demoted it from a design dial to a safety
rail** — its own doc-comment says so, and says why it was kept rather than
deleted: "so a degenerate floor-stack still has a stop". Because every floor
grant raises the cap in lockstep, it does not bind in practice — 0.0–0.4% of
reads are at cap. So "we removed the cap" is right about the *effect* and
wrong about the *letter*, and the letter is the only thing standing between a
floor-stack and infinity.

**S6, the floor rule's slope.** 150 runs/cell.

| FLOOR_PER_POWER | winrate | mean held | powers/deck |
|---|---|---|---|
| 0 | 15.3% | 16.9 | 2.4 |
| **5 (shipped)** | **16.7%** | **20.4** | 2.4 |
| 10 | 18.7% | 24.3 | 2.5 |
| 20 | 18.0% | 33.0 | 2.5 |

**`powers/deck = 2.4`.** That is the S0 gap in one number. The table's deck
was "heavy on powers"; the drafter builds a quarter of that. **Every Fanfare
cell above was therefore measured in a world where the ramp barely exists**,
which is the honest reason they all came back flat — not proof that the
Fanfare channel is shallow at a real table.

**S7, so hand the deck over instead of drafting it.** Same size, same salon
core, the only difference is nine powers vs none:

| arm | mean Fanfare at read | floor granted/combat | dmg/fight |
|---|---|---|---|
| power-heavy (9 powers) | **36.4** | 30.9 | 143.4 |
| control (0 powers) | 25.5 | 4.3 | 142.1 |

And on a long boss fight specifically (`tank_boss`, 120 fights, mean 8.9
turns): **mean peak held 48.9, max 58, and 0 of 120 fights reached 80.**

So the floor rule is confirmed as the mechanism, and it gets Fanfare into the
right neighbourhood — but the model still lands at roughly half the reported
band. Closing that last gap needs either more powers than nine, longer fights
than nine turns, or something the model does not have. **The floor is
per-combat in both engines** (both rewind it at combat start), so it is
rebuilt every fight — which makes fight LENGTH a direct multiplier on how
high the meter climbs, and makes a long act-3 boss the natural place to see
80-90.

---

## S8 — every source of Fanfare

Four generation sources. That is all of them.

| source | amount | fires on |
|---|---|---|
| `encore_gained` | 1 | per point of Encore **gained**, by any means |
| `encore_spent` | 1 | per point of Encore **spent**, including salon upkeep |
| `hp_lost` | 1 | per point of **true** HP lost (after Block and absorption) |
| `center_stage` | 2 | per card played **while she holds the Spotlight** |

Plus the floor, which is a different thing — it raises floor, cap and current
together and persists for the combat:

| source | amount | printed on the card? |
|---|---|---|
| **playing any POWER** | 5 (rare 8) | **no — it is a rule** |
| `gain_fanfare_floor` op | varies | yes, on the 3 cards that have it |

Decay is 20% per turn, clamped at the floor. Cap is `MaxHp/2 + floor grants`
and does not bind.

**Measured share** (power-heavy deck vs `tank_boss`, 150 fights):

| source | per fight | share of generation |
|---|---|---|
| `center_stage` | 33.3 | 39.8% |
| `encore_gained` | 29.2 | 35.0% |
| `encore_spent` | 14.1 | 16.8% |
| `hp_lost` | 7.1 | 8.4% |
| *floor grants* | *34.3* | *(baseline, not generation)* |

**This is the legibility answer to "I gain it for unclear reasons."** Three of
the four sources are INDIRECT — they fire off Encore movement, damage taken
and Spotlight plays rather than off anything the card says. A card that grants
3 Encore silently prints 3 Fanfare on the way in and 3 more as the stage
spends it: **6 Fanfare from a card whose text never mentions Fanfare.** And
the single largest line in the table, the floor rule, is not written on any
card at all.

---

## S9 — pricing "powers raise the cap, not the floor"

Two things have to be said before this is priced.

**It is not a coding mistake.** The floor-per-power rule is the F-A3
constellation grant, and `constants.py` carries the reasoning: a grant is
STATIC value rather than accrual, which keeps the no-passive-accrual law
(kickoff §4) intact while still rewarding investment. The same comment
records why the `gain_fanfare_floor` op exists alongside it — a power-only
rule structurally excludes the power-light fanfare archetype (measured: 6.7
floors/run against salon's ~51).

**The cap half of the proposal is inert.** F-A5 demoted the cap to a safety
rail; it does not bind (0.0–0.4% of reads, and an 8x cap sweep moved nothing).
So "raise the cap, not the floor" is in effect "powers stop granting
anything", and what is being priced is the removal of the ramp.

Power-heavy deck, 150 fights/encounter:

| FLOOR_PER_POWER | winrate | mean held | peak held | dmg/fight | hp left |
|---|---|---|---|---|---|
| **0 — the ruling** | 100.0% | 29.7 | 35.7 | 167.8 | 52.5 |
| 2 | 100.0% | 33.0 | 40.1 | 167.9 | 52.5 |
| **5 — shipped** | 100.0% | 37.6 | 45.8 | 167.9 | 52.6 |

Winrate saturates at 100% here, so a second cut on the same decks measured
**turns to kill**: 9.05 turns shipped vs **9.46 with the rule removed**, with
HP left identical (53.2 vs 53.1) and peak Fanfare 48.7 → 37.8.

**So the ruling costs about 22% of the visible Fanfare number and about 4% of
her actual power.** It is not a nerf. That is consistent with everything else
here: the Focus term converts 10 Fanfare into +1, so even a large swing in the
meter is a small swing in output.

There is still a good reason to want it, and it is the S8 reason rather than a
balance one: **the rule is invisible.** Nothing on a power says it grants
Fanfare, and it is the single largest line in the source table. Removing it
(or printing it) is a legibility fix that happens to cost ~4% power — which is
a much easier trade to justify than a balance change that does not balance
anything.

---

## S2 — the Encore census (T2)

**19 of 78 cards (24% of the pool) grant Encore. Exactly ONE spends it.**

| rarity | count | cards |
|---|---|---|
| basic | 1 | `aria_of_recompense` |
| common | 5 | `ebb_and_flow`, `lasting_impression`, `macaron_break`, `suffering_for_art`, `surintendante_chevalmarin` |
| uncommon | 7 | `audience_participation`, `curtain_cue`, `curtain_up`, `deep_breath`, `hearts_swelling`, `many_waters_melody`, `overflowing_hospitality` |
| rare | 6 | `grand_gala`, `let_the_people_rejoice`, `rain_of_roses`, `reginas_mercy`, `showstopper`, `the_final_verdict` |
| **spends it** | **1** | `limelight` |

Measured on the salon arm: **11.9 gained vs 8.0 drained per combat** (3.9
spent + 4.0 absorbed), ratio 1.50, ending every combat holding 4.0.

Note what the sinks are. Upkeep is automatic. **Absorption is automatic too**
— it is not a decision the player makes, so every point above what the stage
burns is a free damage buffer that costs no card, no energy and no thought.
Against the Necrobinder comparison (one or two enablers in a deck), a quarter
of the pool is an order of magnitude more access.

*The Necrobinder side cannot be measured here — `game_ref` holds the
Ironclad only, so that half is taken as given rather than checked.*

---

## S3 — specialising vs the good-stuff pile (T3)

`adaptive_policy` drafts by card quality and never sees the archetype label:
the good-stuff pile in policy form.

| arm | winrate | acts | archetype mix of drafted cards |
|---|---|---|---|
| assigned salon | **16.7%** | 1.09 | generic 45% · salon 28% · spotlight 14% · fanfare 13% |
| assigned fanfare | 1.3% | 0.57 | generic 52% · fanfare 20% · salon 14% · spotlight 13% |
| assigned spotlight | 2.0% | 0.95 | generic 45% · spotlight 30% · fanfare 12% · salon 12% |
| adaptive (good stuff) | 5.3% | 0.80 | generic 44% · salon 26% · spotlight 16% · fanfare 13% |

**Specialising pays, decisively — for salon.** The focused salon draft wins
3.1x what undirected drafting wins. And good-stuff drifts INTO salon on its
own (26% salon, its largest non-generic share) while winning a third as
often, which says the salon cards are individually strong but only pay off
when they are the plan.

So T3's collapse is not what the model shows. What it shows is worse in a
different way: **two of the three archetypes are non-functional** (1.3% and
2.0% against salon's 16.7%), so there is nothing to collapse INTO — there is
one plan, and everything else is chaff.

One number does support T3's instinct: **~45% of every deck is
archetype-neutral "generic" cards regardless of the plan.** Nearly half of
each build is the same pile whatever you are doing.

---

## S5 — so what IS the engine? The stage.

| SLOTS | winrate | dmg/fight | dry upkeeps |
|---|---|---|---|
| 1 | 8.7% | 112.8 | 41.8% |
| 2 | 12.0% | 114.3 | 47.7% |
| **3 (shipped)** | **16.7%** | **115.5** | **49.7%** |
| 4 | 14.7% | 113.7 | 52.6% |

Going from one member to three **nearly doubles her winrate** — a far bigger
move than anything in the Fanfare cells. The stage is the engine.

And the fourth slot makes her WORSE in the sim (14.7%), because dry upkeeps
climb to 52.6%: the stage outruns its own fuel.

**That is the synthesis, and it is T2's mechanism rather than T1's.** The
stage is the engine, and Encore is its THROTTLE. In the sim the throttle
binds — half of all upkeeps arrive unable to fund a member, so extra members
starve. At a real table with 19 Encore grantors and one sink, the throttle
does not bind at all, and every added member converts straight into power.
That also explains the sim/table divergence without anything being wrong with
either: they are the same engine at different fuel levels.

It also puts A12 (Box Seats) in a specific light. In the sim it is
self-limiting. In the table's fuel regime it is not, and that is exactly the
condition the playtest was played in.

---

## What a ruling would need to decide

None of this is a proposal. In rough order of what the evidence supports:

1. **The Encore economy is the lever for the STAGE** — either fewer grantors
   (T2's "strip the riders from most cards") or a real sink that competes
   with the stage. Note that absorption being automatic is what makes surplus
   free; a player-facing choice would change the shape as much as the count
   does.
2. **The FLOOR-PER-POWER rule is the lever for FANFARE.** Not the Focus
   divisor (8x = 5 points), not the cap (8x = nothing). 17 of 78 cards are
   powers and each one permanently raises floor and ceiling together, so a
   power-heavy deck ramps its own ceiling — and that is the deck the table
   played. Note the sim cannot size this lever honestly, because its drafter
   will not build that deck; S7 is the closest available substitute.
3. **Two dead archetypes** are their own problem, independent of Furina's
   strength: fanfare 1.3% and spotlight 2.0% against salon's 16.7%.
4. **The table's 80-90** needs disambiguating (held vs generated per turn)
   before the S0 gap can be read as anything.

Standing caveat, unchanged: tier 0.5 models one seat, the table was co-op,
and the D8 Encore divergence from the salon UI sprint is still unruled. The
sim disagreeing with a table is not the sim winning.
