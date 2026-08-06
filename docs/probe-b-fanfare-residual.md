# Probe B3 (S7 probe (b)) — the Fanfare accounting residual

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

Date: 2026-08-05. Authority: R103, probe order (c) → (a) → **(b)**. Input: the
S7 audit's C2 cluster (`docs/s7-fidelity-audit.md` §4.1,
`docs/s7-classification.md` family C, C2). This is a **live measurement**: the
game was launched, five runs on chosen seeds were recorded with the P1.5
selector channel live, and the same actions were replayed through tier0.

**Zero design authority was exercised.** No constant, card, sheet or rule was
touched. No mod behaviour was changed; the P1.5 wire was frozen for this pass.
No escrowed number was moved, and none is moved by anything below.

---

## The pre-registered question, verbatim

> "Where does the Fanfare income residual come from?"

## The answer

**LOCALIZED — and S7's residual was almost entirely a reconstruction artifact
of the unrecorded Spotlight selector.**

The residual splits into three named terms, in descending size:

| # | term | size | side |
|---|---|---|---|
| 1 | **the selector** — the replay let tier0's own designation heuristic stand in for the answer the run actually gave | the whole of the direction, and ~64% of the total income | reconstruction INPUT |
| 2 | **the sampling seam** — the engine samples `meters_by_turn` at the turn OPENING, so its next reading contains the top-of-turn decay AND the enemy turn's income; the replay's turn contains neither | median −2 to −2.5 of what remains | sampling seam |
| 3 | **the fight's first Spotlight** — tier0 credits the play that SETS the designation, the engine does not | exactly +2 once per combat, tier0-optimistic | genuine, small |

**DIRECTION, plainly: with the selector known, tier0 is NOT pessimistic about
Fanfare.** S7 measured sim under engine, median −3.0. The same instrument on a
fresh corpus with the selector reconstructed measures **median +1.0, mean
+0.32** on the raw end-of-turn comparison — neutral to marginally
**optimistic**. The sign flipped.

**Income and decay are both at parity where they can be isolated.** Per-card
income is exact (`FANFARE_PER_SPOTLIGHT_CARD = 2`, and 0 for a card the
designation does not cover) on 26 of 27 measured plays. The decay law
(`FANFARE_DECAY_FRACTION = 0.20`, `max(1, round(...))`) predicts the engine's
turn boundary **exactly** on 4 of 7 measured boundaries, and the other three
are explained to within 1–2 by the Encore-absorption income channel.

So: **not the income side, not the decay side.** Term 1 is a reconstruction
gap, term 2 is a sampling seam, term 3 is a real but bounded tier0 optimism of
2 Fanfare per fight.

---

## Why S7 could not see this and this probe could

Furina's starter relic grants an Ethereal Spotlight every turn. Playing it
opens a Center Stage / Guest Cast selector, and that answer is the whole of
that turn's Fanfare posture:

* **Center Stage** — her own cards generate Fanfare, Companions do not, nobody
  is numerically empowered;
* **Guest Cast** — Companions are empowered ×1.5, and **nothing generates
  Fanfare at all**.

Before P1.5 that answer was not on the wire. `understudy/replay.py` therefore
fell through to `effects._op_spotlight_designate`, tier0's own heuristic, which
takes Guest Cast whenever a Companion is in hand. **A policy was standing in
for a recording**, and on every turn where the two disagreed the sim generated
zero Fanfare against an engine that generated some — which is exactly the
shape S7 filed (51 turn-1 rows, sim 0 against engine 1–11).

P1.5 put `fight.selectors` on the wire. This pass added `--use-selectors` to
`understudy/replay.py`: the recorded answer is pushed through
`effects.SPOTLIGHT_FORCE`, the diagnostic switch tier0 already carries for
controlled Center/Guest comparisons. **Reconstruction, not rules** — no law is
retyped, and the switch is restored in a `finally` so a raise cannot leak a
forced designation into the next fight (pinned by test).

---

## Corpus

Five runs, chosen seeds, all recorded 2026-08-05 with the P1.5 bridge:

| seed | fights | outcome | defects |
|---|---|---|---|
| `TRACKB3A` | 4 | bounded | 0 |
| — | 0 | `unexpected_start_state` (harness-side: `--max-fights` leaves the previous run parked on `rewards`; the driver restarted and continued) | 1 |
| `TRACKB3C` | 4 | bounded | 0 |
| `TRACKB3D` | 5 | died | 0 |
| `TRACKB3E` | 6 | bounded | 0 |

**19 fights replayed, 104 turns with a Fanfare comparison, 123 selector answers
recorded.** Every one of the 123 was a Center Stage / Guest Cast pair; the bot
answered `self` on 102 of the compared turns and `companion` on 2.

Plus the two probe-B2 scripted fights, where the selector was a **declared
input** rather than a policy output — those supply the per-play and
per-boundary resolution below.

---

## Ledger 1 — the per-turn residual, blind vs selector-aware

`residual_raw` = tier0's end-of-turn Fanfare minus the engine's NEXT turn-open
reading. `residual_full` = the same after applying tier0's own decay AND
crediting the between-turn HP loss (`FANFARE_PER_HP_LOST`), read off
`hp_trajectory`.

| reconstruction | cut | n | residual_raw median | mean | sim under / over | residual_full median | mean |
|---|---|---|---|---|---|---|---|
| **BLIND** (S7's position) | turn 1 | 19 | **−4.0** | −3.95 | — | −3.0 | −1.95 |
| **BLIND** | turn ≥ 2 | 85 | −2.0 | −2.12 | — | −5.0 | −4.24 |
| **BLIND** | all | 104 | **−2.0** | −2.45 | 70 / 22 | −4.0 | −3.82 |
| **SELECTOR-AWARE** | turn 1 | 19 | **0.0** | −1.95 | — | +1.0 | +0.05 |
| **SELECTOR-AWARE** | turn ≥ 2 | 85 | +2.0 | +0.82 | — | −2.0 | −1.92 |
| **SELECTOR-AWARE** | all | 104 | **+1.0** | **+0.32** | 26 / 66 | −2.0 | −1.56 |

Read three things off that table:

1. **S7's headline direction is gone.** Median −2.0 → +1.0; the under/over
   split inverts from 70/22 to 26/66.
2. **The turn-1 family is gone specifically.** Family B's 51 selector-blind
   turn-1 rows were the loudest cluster in the audit; turn-1 median moves
   −4.0 → 0.0.
3. **The decay seam is real and it is term 2.** `residual_raw` (+1.0) is
   better-centred than `residual_full` (−2.0). S7 recorded that applying
   tier0's own decay *widened* disagreement 16% → 5% and declined to pick a
   position; **that widening is the seam telling the truth**, not evidence
   that tier0 decays harder.

Total income over the corpus: sim **161** blind, sim **449** selector-aware,
against an engine NET delta of **+416** (net = income − decay, so engine income
is at least 416). Income by source, selector-aware: `center_stage` 437,
`encore_spent` 7, `hp_lost` 5.

---

## Ledger 2 — per-play income, at full resolution

From probe B2's scripted fight, seed `TRACKB2`, Center Stage declared on every
turn, `player.resources` read at every decision (`KLEEMOD_FANFARE`,
`KLEEMOD_ENCORE`). Engine delta is the meter's own movement across one play.

| round | card | engine ΔFanfare | tier0 |
|---|---|---|---|
| 1 | **Ethereal Spotlight** | **+0** | **+2** ← the one mismatch |
| 1 | Stage Presence | +2 | +2 |
| 1 | Stage Presence | +2 | +2 |
| 1 | Aria of Recompense | +2 | +2 |
| 2–8 | Ethereal Spotlight (×7) | +2 | +2 |
| 2–8 | Stage Presence (×7) | +2 | +2 |
| 2–8 | Regal Bearing (×4) | +2 | +2 |
| 2–8 | Aria of Recompense (×3) | +2 | +2 |
| 4,5,8 | Charlotte — Enduring Frosthelm (×3) | **+0** | **+0** |

And the Guest Cast arm, same seed, same script: **every play, every card,
engine +0 — and tier0 +0.** Twenty-seven plays, zero income, both instruments.

**26 of 27 plays agree exactly. The single mismatch is term 3**: the fight's
FIRST Ethereal Spotlight. The engine credits a play against the designation
that was standing when it resolved, and on the first Spotlight of a combat
there is none; every later Spotlight is covered by the designation it already
set. tier0 credits it. That is **+2 Fanfare per combat, once, in tier0's
favour** — and it is the size of the corpus-wide mean residual (+0.32 per turn
× ~5.5 turns per fight ≈ +1.8 per fight).

---

## Ledger 3 — the decay seam, at full resolution

Same fight. `fan_end` is the meter as the player ended the turn; `fan_next` is
the engine's own next turn-opening sample. `predicted` applies tier0's decay
law to `fan_end` and then credits tier0's own two between-turn income
channels — HP lost, and Encore absorbed — both read off the wire.

| boundary | fan_end | encore_end | fan_next | encore_next | hp drop | encore drop | tier0 decay | predicted | diff |
|---|---|---|---|---|---|---|---|---|---|
| 1→2 | 6 | 5 | 5 | 5 | 0 | 0 | 1 | 5 | **0** |
| 2→3 | 9 | 5 | 10 | 1 | 0 | 4 | 2 | 11 | +1 |
| 3→4 | 16 | 6 | 18 | 0 | 1 | 6 | 3 | 20 | +2 |
| 4→5 | 24 | 0 | 19 | 0 | 0 | 0 | 5 | 19 | **0** |
| 5→6 | 25 | 0 | 20 | 0 | 0 | 0 | 5 | 20 | **0** |
| 6→7 | 26 | 5 | 22 | 3 | 0 | 2 | 5 | 23 | +1 |
| 7→8 | 30 | 8 | 24 | 8 | 0 | 0 | 6 | 24 | **0** |

* **Every boundary on which the Encore buffer did not move is predicted
  EXACTLY** by tier0's own decay law. 24 → 19 is `max(1, round(24×0.20)) = 5`;
  25 → 20 and 30 → 24 the same. **The decay law is at parity and this is the
  measurement that says so.**
* The three boundaries that miss are exactly the three on which Encore fell,
  and they miss by +1, +2, +1 — tier0 credits the whole Encore drop as
  Fanfare income where the engine credits `drop − 1` or `drop − 2`. **The wire
  carries the Encore LEVEL, not the events that moved it**, so absorption
  cannot be separated from upkeep here. That is a limit of the instrument, not
  a to-do: separating them needs a mod-side hook, and the wire was frozen for
  this pass.
* **What the replay's per-turn comparison omits is now named**: between the
  sim's end-of-turn number and the engine's next turn-open sample sit a decay,
  an HP-loss income and an Encore-absorption income. S7's `l2.fanfare_*` rows
  compare across all three.

---

## Mechanically, what it means

* tier0's Fanfare **generation** is faithful, per play, in both Spotlight
  modes, on the cards this corpus exercised.
* tier0's Fanfare **decay** is faithful — same fraction, same rounding, same
  floor of 1 — and lands on the engine's number to the point on every boundary
  where nothing else moved.
* tier0 is **optimistic by exactly 2 Fanfare per combat**, on the play that
  sets the fight's first designation.
* The audit's `l2.fanfare_after_turn` and `l2.fanfare_next_open_post_decay`
  columns **compare across a seam containing two income channels the replayed
  turn does not contain**. Neither column is the "fair" one S7 was looking for;
  the fair comparison needs the enemy turn reconstructed as well, which the
  replay does not do.
* **NOT REPRODUCED as a family-C infidelity.** C2's stated mechanism — "tier0
  may decay harder or generate later than the C# engine" — is not what the
  measurement found. Both halves are at parity.

## Confounders and limits, declared

1. **Bot-limited (Guardrail 7).** Every engine number here came from a bot or
   from a fixed script. Nothing is a balance finding.
2. **The Encore split is unreadable.** Absorption vs upkeep, above. Bounds the
   boundary reconciliation at ±2.
3. **Salon is empty throughout** — every `salon_members` reading is 0, as in
   every measurement to date. Fanfare interactions with a populated salon are
   untested by this corpus, as they were by S7's.
4. **`Aria of Recompense`'s Block is unreconstructed** (probe B2's residual);
   its Fanfare income is not, and reads +2 like everything else.
5. **One character.** Furina only. Fanfare is hers, so this is not a coverage
   gap for the question asked, but no claim is made about any other kit.
6. **The engine's income and decay cannot be separated on a bot turn** — only
   the net is on the wire. The isolation above comes from the SCRIPTED fight,
   where the plays were declared in advance; the 104-turn soak ledger is the
   breadth and the scripted fight is the resolution.

## Exact repro

```
# corpus
python -m understudy.soak --runs 3 --seed TRACKB3A --seed TRACKB3B --seed TRACKB3C --max-fights 4
python -m understudy.soak --runs 1 --seed TRACKB3D --max-fights 6
python -m understudy.soak --runs 1 --seed TRACKB3E --max-fights 6

# the two readings of it
python -m understudy.replay --logs "understudy/logs/soak/soak-2026080*-13*run*.jsonl" \
    --out /tmp/blind.tsv --ledger /tmp/blind-ledger.tsv
python -m understudy.replay --logs "understudy/logs/soak/soak-2026080*-13*run*.jsonl" --use-selectors \
    --out /tmp/aware.tsv --ledger /tmp/aware-ledger.tsv

# ledgers 2 and 3 (full resolution) come from probe B2's readings
python -m understudy.probe_block --spotlight center --seed TRACKB2 --max-fights 1 --turns 8
```

Soak stamps of record: `20260805-130311` (TRACKB3A/B/C),
`20260805-130818` (TRACKB3D), `20260805-131234` (TRACKB3E); probe stamps
`20260805-125753` / `-125933` / `-132001`. Soak logs are gitignored per-machine
run output; the glob above must be narrowed to those stamps to reproduce the
exact ledger, since a later soak in the same directory would widen the corpus.

Block, as a bonus of the same two readings: `l2.block_at_turn_end` divergences
fall **55/107 → 29/107** when the selector is consumed, and probe B2 shows the
remaining 29 are Frail. See `docs/probe-a-block-offset.md`.

---

## For the ruling session

**Escrow implications are a ruling, not this probe's to draw.**

The four conclusions escrowed at R102 pending this probe, by name, so the
ruling session finds them:

1. **the threshold-reach table** (94.1% at 10, 80.8% at 15, 64.8% at 20, 40.8%
   at the cap) — R44, annotated in place in `tier0/DECISIONS.md`;
2. **the compensation STOP at 1.8%** against the 2.0% floor — R87(1),
   annotated in place;
3. **the Fanfare early-half grade "prediction NOT SUPPORTED"** —
   `docs/sprint-track-b-gate-log-2026-08-05.md` GRADE (a), annotated in place;
4. **the R91/2b revisit posture** — R99(4), annotated in place.

This probe reports numbers against them and moves none of them.
