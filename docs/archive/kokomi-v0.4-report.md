# Kokomi v0.4 — O4 Salvage + Lore Overlay: EXECUTION REPORT

> **Lifecycle: ARCHIVED** — superseded; kept verbatim as a record and never updated. Status index: `docs/registry/identifiers.md` §15.

**Date:** 2026-07-26. Governing doc: `docs/kokomi-v0.4-plan.md` ([USER]-ratified;
ruling answers in its §7). Rulings logged as R54 (the O-ruling + graded
predictions) and R55 (the rename batch + voice law) in `tier0/DECISIONS.md`.

Suite at close: **664 passed** at repo root (`python -m pytest -q`), up from
654 — the ten new tests are the O4 mechanics. Lints re-run by name and clean:
`lint_unique_names` (220 names unique across 5 sheets), `lint_strict_domination`
(CLEAN on kokomi-cards.yaml), `lint_kokomi_decksize` (in-suite, green).

Every number below is **PROPOSED**. Nothing here is ratified.

> **SUPERSESSION NOTICE.** Sections 2-4 below record the FIRST v0.4 pass: a
> 10-card starter, a `/4` divisor bank read, and the meter bracket that chose
> 20. A same-day [USER] pass rebuilt the starting deck and flipped the bank
> read to a multiplier (R56). **Section 8 is the shipped world**; the act
> numbers in 2.3 and the grades in 3 belong to a superseded world and must
> never be compared unlabeled. Section 4's *finding* survives and was in fact
> confirmed by direct experiment -- see 8.2.

---

## 0. Measurement convention (established in W1 — read this first)

The v0.3 numbers of record are **`--realistic` runs at 500 runs, default
seed**:

```
python -m tier05.runner --character kokomi --archetype <plan> --runs 500 --realistic
```

Under that invocation the committed v0.3 world reproduces its recorded four
pairs **exactly**: priest 32% act-1 / 2.0% run, commander 49% / 1.6%,
generic 26% / 0.4%, assist 20% / 0.0%.

The same committed world at **bare loadout** reads priest 3% / commander 4%
act-1. The relic/potion layer is most of the act-1 clear. Any v0.4 number
compared against the v0.3 record must use `--realistic` or it is comparing
two different worlds. This was nearly a silent error in this sprint and is
now written down.

---

## 1. W1 — priest pilot audit (INSTRUMENT, no card changes)

### 1.1 The headline: most of the regret is the instrument, not misplay

Regret reproduced at 17.4% (300 f/enc battery) / 16.3% (probe, 979 of 5991
plays). Tallying *what* gets regretted rather than assuming:

| chosen when regret fires | n | most often named "better" | n |
|---|---|---|---|
| `vigil_of_the_deep` | 220 | `waters_edge` | 305 |
| `prayer_to_the_moon` | 181 | `waterspout` | 194 |
| `votive_offering` | 142 | `coral_guard` | 90 |
| `exposing_current` | 117 | `pearl_barrage` | 61 |
| `sango_prayer` | 110 | `all_streams_flow` | 57 |

Every dominant "regret" is an **engine or setup card chosen over a repriced
attack**. `_log_regret` compares only immediate damage + effective block, and
Kokomi's whole identity is to not play the biggest immediate number. So the
7.7% → 15.1% doubling at v0.3 tracks **v0.3 making her attacks bigger**
(`waters_edge` 4→6, `waterspout` 7→10 — the two cards that dominate the
"better" column), not the pilot getting worse. The instrument widened because
the gap it measures widened.

**Consequence for the sprint:** priest-32% vs commander-49% is not
meaningfully a misplay gap, and card tuning against this number would have
been tuning against an artifact.

### 1.2 One real defect found and fixed (F1) — LANDED

The pilot could see **no flat per-attack bonus at all**. `_expected_damage`
handled `bonus_formula`, Spotlight, and Shatter, but the engine's entire
flat-bonus block — Bennett's `next_attack_up`, Nicole's `celestial_gift`,
`attack_up_this_turn`, the zero-cost rider, Furina's `fanfare_attack_per10`,
and **Kokomi's Ceremonial Garment Charge read** — was invisible. The pilot
priced every attack at its printed number and played straight through its own
buff windows. Under a Garment at a priest-median bank that is a larger error
than most cards' printed damage.

Fixed by extracting the engine's exact arithmetic into a pure
`effects.flat_attack_bonus()` that both the engine and the pilot call, so the
estimate cannot drift from what resolves. The consuming `pop` and the
`KNOB_READS` tick stay at the real call site.

- Extraction alone verified inert: suite 654 green before and after, regret
  probe identical at 979/5991.
- After the pilot reads it: regret 17.4% → **15.3%** (battery), 16.3% →
  **14.1%** (probe).
- **This is a shared change** — it is the only cross-character item in the
  batch. Measured effect on ratified worlds: nil; all band locks pass.

### 1.3 One arm measured worse and was DROPPED (F2) — binding null result

The plan named "reader/burn ordering" as a suspect. Implemented it exactly
(mirroring the existing bomb-sequencing rule): when the best play is a Charge
reader and the turn can afford both, bank first.

| | priest act-1 | commander act-1 |
|---|---|---|
| F1 only | 33% | 49% |
| F1 + F2 | **27%** | 50% |

*(500 runs/plan, `--realistic`.)* Demoting a damage play to a setup play costs
tempo in precisely the act-1 fights that kill her, and the bank is deep enough
by the time a reader matters. The code is removed rather than left dead, and
the reason is recorded as a comment at the decision site so it is not retried.

**Note on grading F2 honestly:** F2 *raised* measured regret (15.3% → 26.3%),
which is exactly what §1.1 predicts an instrument blind to setup value would
report. Regret was therefore not used to judge it — act-1 clear was.

### 1.4 Re-measured v0.3 baseline (the clean W2 comparator)

500 runs/plan, `--realistic`, committed v0.3 world + the F1 pilot fix:

| plan | act-1 | run | (committed baseline) |
|---|---|---|---|
| priest | 33% | 2.4% | 32% / 2.0% |
| commander | 49% | 1.6% | 49% / 1.6% |
| generic | 26% | 0.6% | 26% / 0.4% |
| assist | 20% | 0.0% | 20% / 0.0% |

Within noise of the committed record — the right outcome for an instrument
fix, and W2 gets a comparator that is still comparable to everything on file.

---

## 2. W2 — the O4 arm

### 2.1 What landed

- **`bake_kurage` is now a persistent summon.** New `summon_kurage` op +
  turn-end pulse hook seated beside `oz_summon`/`witchs_flame`. Holds
  `KURAGE_DURATION` (3) turns; each turn end deals
  `KURAGE_PULSE_BASE` (2) + Charge/`KURAGE_PULSE_DIVISOR` (4) to a random
  enemy with hydro, and grants `KURAGE_PULSE_BLOCK` (2). Stacks ARE turns
  remaining; re-summoning refreshes and never adds. The +1 Charge survives.
- **Garment riders.** Attacks under the Garment also grant
  `GARMENT_ATTACK_BLOCK` (2); casting the Garment while the Kurage is fielded
  refreshes it (the Tamakushi Casket link).
- **Meter 10 → 20.**
- Engine/pilot/drafter support: pilot values the summon (without it, it prices
  Bake-Kurage at its +1 Charge and never fields the card the whole arm rests
  on — the DECISIONS-53 selector lesson, pinned by a test);
  `DRAFTER_VERSION` **7 → 8** (`summon_kurage` priced like Durin at one pulse);
  `bake_kurage`'s upgrade becomes `kurage_turns: +1` (duration is the only
  dial an upgrade owns — the resource-curve law forbids moving Charge).

**Canon check, wiki-verified:** Bake-Kurage canonically *"deals Hydro DMG to
surrounding enemies and heals nearby active characters at set intervals."*
The pulse — damage + hydro + mending-as-Block — is that ability, not an
invention. Tamakushi Casket is canonically the A1 passive that refreshes a
fielded Bake-Kurage on Nereid's Ascension. O4's two mechanics are the two
things canon actually says.

### 2.2 The meter bracket (300 runs/plan, `--realistic`)

| meter | priest act-1 / run | commander act-1 / run | starter A1 vs A2 | median TOO_STRONG |
|---|---|---|---|---|
| 10 *(floor comparator, not an arm)* | 72% / 12.0% | 79% / 13.0% | 4.7 vs 3.3 | **YES** |
| 15 | 48% / 3.7% | 63% / 6.7% | 4.5 vs 3.3 | no |
| **20 (chosen)** | 34% / 0.7% | 48% / 1.7% | 4.4 vs 3.5 | no |
| 25 | 25% / 0.7% | 39% / 1.3% | 4.4 vs 3.4 | no |

Meter 20 is chosen: it is the arm that hits the pre-registered acceptance band
(35–50%), and it gives the healthiest median statline. Meter 15 pushes
commander to 63%, past the Furina-57 ceiling-side reference; meter 25 falls
under band on both plans.

### 2.3 500-run confirm at meter 20

| plan | act-1 | run | vs W1 baseline |
|---|---|---|---|
| priest | 30% | 0.6% | 33% / 2.4% |
| commander | 45% | 1.4% | 49% / 1.6% |
| generic | 26% | 0.4% | 26% / 0.6% |
| assist | 24% | 0.2% | 20% / 0.0% |

The O4 world lands slightly **under** the v0.3 world on act-1 (−3 / −4 points)
and costs priest run winrate (2.4% → 0.6%); assist gains (20% → 24%).

**Archetype median at meter 20:** A1 3.6 / A2 **5.2** / A3 3.8 / A4 0.5 /
A6 3.6 — *"median statline passes heuristic + identity constraints."* At v0.3
the median was A1 4.4 / A2 4.4 / A6 4.4, all ≥4, tripping TOO_STRONG.

### 2.4 Garment uptime (prediction d)

| world | priest uptime (long fights) | commander uptime (long fights) | casts/fight |
|---|---|---|---|
| meter 10 | 56.7% (66.8%) | 75.5% (81.1%) | 1.30 / 2.12 |
| meter 20 | **23.2%** (33.9%) | **50.1%** (58.7%) | 0.57 / 1.28 |

The v0.3 watchlist was real — at meter 10 the commander Garment is up 81% of
long-fight turns, which is a permanent multiplier wearing a Burst's clothes.

---

## 3. Predictions graded (plan §2 — hits AND misses)

**(a) Starter A1 falls below A2 — MISS, at every meter step.**
Starter stays A1 4.4–4.7 vs A2 3.3–3.5. The ruled `A2_scaling>A1_frontload`
constraint is still VIOLATED on the starter deck at every arm.

**(b) TOO_STRONG clears at archetype median — HIT.**
Clears at 15/20/25, and the median goes further than predicted: it now
satisfies A2>A1 outright (5.2 vs 3.6 at meter 20), which the v0.3 median did
not.

**(c) Act-1 lands 35–50% at meter 20–25 — PARTIAL.**
At the 300-run bracket meter 20 read 34%/48%. At the 500-run confirm it reads
priest 30% (under band) and commander 45% (in band). Commander hits; priest
misses by 5 points.

**(d) Garment-uptime watchlist retires by construction — PARTIAL.**
Retires for priest (57% → 23%). For commander it halves but stays live at 50%
overall / 58.7% in long fights. Commander's conscript engine converts exhausts
to burst energy fast enough to keep re-donning the Garment even at meter 20.
**Carried forward as a watchlist, narrowed to the commander lane.**

**Fallback trigger: DID NOT FIRE.** The plan says "misses on (a)/(b) at every
meter step → fall back to O2." (b) hit, so O4 stands as landed and (a) returns
to [USER] as an open ask — see §4.

---

## 4. THE FINDING: prediction (a) failed for a reason the v0.3 report got wrong

The v0.3 report's §6.4 attributed the `A2>A1` violation to the fast-cycle
Garment — *"the fast-cycling Garment measures as FRONTLOAD in tier0's ratio
instrument."* **That diagnosis does not survive this pass.**

At meter 20 the Garment is largely *absent* from the starter battery (uptime
down to 23%, casts/fight 0.57, and the starter deck cannot reliably reach a
20-point meter in a single battery fight at all) — and the starter still reads
A1 4.4 vs A2 3.5. Removing the Garment from the picture did not move the
constraint.

The actual cause is **starter composition**. Her starting deck is
3× `waters_edge` (6), 3× `coral_guard`, `waterspout` (10), `surging_shoal` (7),
`tactical_recall`, `bake_kurage` — and it contains **no Charge reader at all**.
`all_streams_flow` and `nereids_ascension` are package cards. The only bank
reader a starter hand can produce is the Kurage pulse, which is deliberately
tiny (2 + bank/4). A deck of flat-damage basics measures as frontload because
it *is* frontload; that is what R53 (basics at Strike parity) and the v0.3
reprice put there.

**So the O4 arm did the job it was scoped to do** — it fixed the *median*
identity, which is what R51's elite-axes ruling actually governs, and it moved
the metronome onto the summon where canon keeps it. It could not fix the
starter, because the starter's frontload was never the Garment's doing.

**This is a [USER] ask, not a call I should make.** The options, honestly:

1. **Put a reader in the starter** (composition change — a balance decision,
   and the plan's §4 non-goals do not cover it). The cheapest candidate is
   swapping one `waters_edge` for a small Charge reader, which is exactly the
   S3-swap grammar v0.3 already used.
2. **Scope the constraint to the median**, where it now passes cleanly. This
   is honest — the median is the round-3 identity canon — but it is a
   declaration change and therefore smells like O1, which was rejected.
3. **Accept the starter violation as declared and documented**, on the grounds
   that a character whose scaling lives in her *pool* will always have a
   frontload-shaped *starter*.

I did not pick one. Option 1 is a balance change requiring red-pen, and
stacking it onto W2 would have broken one-variable-per-window.

---

## 5. W3 — lore overlay (landed, measurement-neutral)

Display names and comments only; ids stable except the one id-level rename,
which landed **before** W2 so the arm was born with the right name.

| id | was | now |
|---|---|---|
| `all_streams_flow` *(id renamed from `riptide_strike`)* | Riptide Strike | **All Streams Flow to the Sea** |
| `conscription_notice` | Conscription Notice | Call to Arms |
| `mass_mobilization` | Mass Mobilization | Rally the Isles |
| `grand_conscription` | Grand Conscription | General Muster of Watatsumi |
| `jade_bulwark` | Jade Bulwark | Pearl Bulwark |
| `mercy_of_the_deep` | Mercy of the Deep | Mercy of the Currents |
| `epiphany_of_the_deep` | Epiphany of the Deep | **Song of Pearls** |
| `depths_judgment` | Judgment of the Depths | Sango Isshin |
| `tide_reading` | Tide Reading | Stolen Chapter |
| `moon_signal` | Moon Signal | A Moment Alone |
| `undertow_shuffle` | Undertow Shuffle | Daydream of a Quiet Life |
| `sayu_yoohoo_windwheel` | Sayu — Yoo-hoo Windwheel | Sayu — Yoohoo Art: Fuuin Dash |
| relic (hook id unchanged) | Tamakushi Casket | **Pearl of Wisdom** |

`vigil_of_the_deep`, `to_the_front`, `field_promotion`, `reinforcements` keep
their names, as drafted.

**Consequence of the relic ruling:** [USER] gave the relic "Pearl of Wisdom",
so the §3 conditional resolved against `epiphany_of_the_deep`. It takes **"Song
of Pearls"** — her wiki-verified 4th Ascension passive, and a knowledge/insight
name that fits an epiphany card. *This substitution is mine and is the one
naming choice in the batch [USER] has not seen; flagging it for the audit.*

**Voice law, Raiden gloss, and the pool-is-the-peace framing** all landed as
drafted (details in R55).

### 5.1 Wiki re-verify (the header audit ask)

**The audit ask was correct: "The Moon's Beauty" is not a Kokomi name.** It has
been struck from the sheet's verified list. Confirmed canon now in the header:
Kurage's Oath (Elemental Skill), Bake-Kurage, Nereid's Ascension (Burst),
Ceremonial Garment, Tamakushi Casket (A1), Song of Pearls (A4), Princess of
Watatsumi (innate), and C1 At Water's Edge / C5 All Streams Flow to the Sea /
C6 Sango Isshin.

**Trap recorded in the header:** beta-era sources carry "Kaijin Ceremony" for
the Burst and "Haworthia Casket" for the A1 passive. Both are pre-release
names. A search that lands on one of those pages will look authoritative and
be wrong — which is the same failure mode the audit ask was raised about.

---

## 6. Open asks for [USER]

1. **§4 — prediction (a).** The starter constraint violation is a
   starter-composition property, not a Garment property. Which of the three
   options? (This is the sprint's real decision.)
2. **Meter 20 ratification** on the 500-run confirm (plan ask 3). Note the arm
   costs ~3–4 act-1 points and priest run winrate vs v0.3 while buying the
   median statline and the canon structure — confirm that trade is the one you
   want, or name meter 15 (48%/63%, still passes the median heuristic, but
   commander clears past the Furina reference).
3. **`epiphany_of_the_deep` → "Song of Pearls"** — my substitution after the
   relic took "Pearl of Wisdom" (§5).
4. **Watchlist, narrowed:** commander Garment uptime is still 50% (58.7% in
   long fights) at meter 20. Retire, or keep watching?
5. Everything else in plan asks 1–5 is closed and logged as R54/R55.

## 7. Non-goals honoured

No revert of v0.3 numbers outside the meter (R53 basic stays 6; Regent commons
stay; divisor /2 untouched — the pre-registered first-knob-back was not
needed). No healing amendment. No taunt/redirect op. No art/animation. No
act-2/3 weight-setting.


---

# 8. v0.4b -- the starter rework (THE SHIPPED WORLD)

Ruling: **R56**. Driven by the §4 finding: if the starter's frontload is a
composition property, then composition is where you fix it.

## 8.1 What changed

- **Starting deck is TWELVE cards, the Silent shape** — 4 `waters_edge` +
  4 `coral_guard` + 2 companions (Gorou fixed, Sayu-or-Shinobu rolled) +
  `bake_kurage` (Charge) + `tactical_retreat` (exhaust). Her deck self-mills,
  so the extra two cards are both deck-out insurance and a real dilution cost
  that the thinning pays down.
- **`waterspout` and `surging_shoal` leave the starter.** [USER]: *"no one
  starts the game with AoE; if you need it, you draft it."* `surging_shoal`
  was in no package at all, so it is now a priest + commander draft-in — it
  would otherwise have been unreachable (the vigil defect, caught in advance
  this time rather than by a zero row in telemetry).
- **The bank read flips from divisor to multiplier:**
  `KURAGE_PULSE_PER_CHARGE = 4`. `KURAGE_DURATION` 3 → 1,
  `KURAGE_PULSE_BASE` 2 → 4, `KURAGE_PULSE_BLOCK` 2 → 0.
- **`tactical_recall` → `tactical_retreat`** (id-level). A retreat preserves
  the unit, which is the voice law on the exemplar card's own face.
- **Companions buffed off basic-parity:** Gorou to 0-cost + Exhaust (free
  damage that thins itself and feeds the funnel); Shinobu to 0-cost Block 4.
- **New Common power — `kurages_oath` ("Kurage's Oath").**

## 8.2 Prediction (a) flips, and the §4 finding is confirmed

R54 graded *"starter A1 falls below A2"* a **MISS at every meter step**.
Under the 12-card starter it **PASSES: A1 3.2 vs A2 4.8.**

The attribution is not an inference. Isolated at `PER_CHARGE = 0` — bank read
switched fully off — the constraint **already passes at A1 2.8 vs A2 3.5.**
So the fix is the **composition**, not the multiplier: `waterspout` (10 flat)
and `surging_shoal` (7 AoE) were her frontload, exactly as §4 argued. The
multiplier then buys A2 depth and clear rate on top. Median passes too
(A1 3.7 / A2 5.1). Four meter steps could never have reached this.

## 8.3 The x4 objection, withdrawn

I argued x4 was too hot from the internal §2.2 reader hierarchy and from
act-1 clear against the plan's stale anchors. [USER] countered with the StS2
precedent: **Necrobinder starts with a 1-cost "Osty gains 5 HP" and a 1-cost
"deal 3 + Osty's HP damage"** — unbounded starting-deck scaling is something
the actual designers ship. Re-measuring the anchors settled it: **act-1 clear
is not the binding metric** (Klee clears 83% of act 1 and wins 3.4% of runs).

| | run | act1 | act2 | act3 |
|---|---|---|---|---|
| Furina | 13.4% | 56% | 37% | 13% |
| **kokomi/priest** | **6.2%** | 56% | 27% | 6% |
| **kokomi/commander** | **5.8%** | 65% | 37% | 6% |
| real_ironclad | 3.6% | 59% | 21% | 4% |
| Klee | 3.4% | 83% | 28% | 3% |
| kokomi/generic | 2.0% | 46% | 16% | 2% |
| kokomi/assist | 1.6% | 44% | 14% | 2% |
| ref_ironclad | 0.6% | 43% | 13% | 1% |

*500 runs/plan, `--realistic`, DRAFTER v8; anchors re-measured in the same
world rather than quoted from the plan.* She lands above Klee and Ironclad
and below Furina at every stage. **Act 3 at 6% vs Furina's 13% is the answer
to the runaway worry** — uncapped Charge x 4 does not explode late.
[USER]'s own standing caveat: Osty's HP can go *down* with bad play, Charge
only goes up. Watched, not assumed.

Meter 20 re-checked in the new world and **kept**: 15 → 9.3/8.7% run,
20 → 6.7/7.7%, 25 → 4.0/6.0%.

## 8.4 Kurage's Oath — the number is measured, not reasoned

A 1-cost Common power: while it holds, every Kurage pulse also grants Block.
It drafts back the mending half of the canon Bake-Kurage (*"deals Hydro DMG
and heals nearby characters at set intervals"*) after the baseline pulse
Block was zeroed — so the healer fantasy is an opt-in build, not a freebie.
Upgrade buys **Innate only**; the Block does not move.

Drafted at 5 by ratio off the Regent precedent, it measured as a **trap pick**:

| ward Block | priest run | commander run |
|---|---|---|
| *(no card)* | 5.8% | 6.0% |
| 5 (first draft) | **3.8%** | 5.4% |
| 8 | 4.8% | 5.8% |
| **12 (ruled)** | **6.2%** | 5.8% |

The ratio had to go **up** for the cheaper trigger, not down: Regent's
finisher is played reliably, whereas Bake-Kurage is one copy in a growing
deck that pulses **once per play** at duration 1. Correct for frequency and
you land back on essentially the Regent number.

**Shipped at 12 with [USER]'s flag on the record:** *"I feel like that's too
strong, but we can rebalance later."* First knob back.

## 8.5 Carried forward

- **The Burst may need reworking entirely** ([USER]). The Tamakushi Casket
  link is inert at `KURAGE_DURATION 1` — a fielded Kurage is always at
  exactly 1, so refresh-to-full is a no-op. The mechanic stays in code and
  stays test-pinned via a raised duration inside the test, so restoring a
  longer duration is safe. The rework itself is a future conversation.
- **`kurages_oath` at 12** — the flagged rebalance candidate above.
- **Final deck sizes 21.7-24.2** run at or over `DRAFT_DECK_SOFT_CAP` (22),
  a consequence of both the 12-card start and her winning longer runs.
- **Pulse Block baseline is 0** and the code path is guarded, not deleted —
  restoring it is one constant.

Suite at close: **695 passed** at repo root. Lints clean: `lint_unique_names`
(222 names across 5 sheets), `lint_strict_domination`, `lint_kokomi_decksize`.
