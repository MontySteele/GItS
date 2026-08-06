# Probe (d) — `Aria of Recompense`'s unreconstructed Block — REGISTRATION

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

> **COUNTERSIGNED 2026-08-06 (10.13 / R120) — REGISTERED, STILL NOT RUN.**
> [USER], verbatim: *"countersigned"*. The registration converts from paper to
> **registered work** under its own terms below: confounder list, cost
> ceiling, stop-and-re-register tripwire all as written. **Results adjudicate
> B2's declared residual and nothing else; Guardrail 7 unchanged.** The run
> itself is Track M's, under this registration as countersigned — the runner
> respects the registration's own harness design. The draft banner below is
> struck, not deleted (R101b).

> ~~**DRAFT — FOR [USER] COUNTERSIGN. NOT RUN.**~~ Nothing below is a measurement.
> No game was launched, no run was taken, no number in this file was read off
> any wire. This document exists so that the question, the method, the
> confounder list and the licensing limits are fixed **before** any reading is
> taken — the same discipline probes (a)/(b) were run under, applied in advance
> rather than written up afterwards. ~~The probe is neither scheduled nor
> resourced; countersign converts it into work, and until then it is paper.~~
> *(Countersigned 2026-08-06 — see the banner above.)*

Date drafted: 2026-08-05. Track P of the "House Lights" batch. Input: the
residual declared and deliberately left unadjudicated by probe B2
(`docs/probe-a-block-offset.md` §"What is NOT explained, and is not C1", plus
its confounder row for the same card). Sibling registrations by structure:
`docs/probe-a-block-offset.md`, `docs/probe-b-fanfare-residual.md`.

**Zero design authority is claimed or exercised.** No constant, card, sheet or
rule is touched by this document, and none may be touched by the probe it
registers. The P1.5 wire is assumed frozen; if it is not frozen when the probe
runs, that is a confounder to log (below), not a licence to change it. Nothing
here re-grades any ratified result, and no outcome of this probe is a balance
finding (Guardrail 7 unchanged).

---

## The pre-registered question, verbatim

> "Does `Aria of Recompense`'s Block divergence close when the recorded
> Fanfare meter is loaded into the reconstruction, the way C1's divergences
> closed when the recorded status strip was?"

---

## Why there is a question at all

Probe B2 measured 38 per-play Block readings across two declared Spotlight
arms. With the recorded status strip loaded, 33 of 38 agreed exactly and
**every one of the 26 positive divergences closed to zero**. The five that
remained are all the same card, and they run the **other way**:

| arm | rnd | frail | engine | `sim_status` | sim − engine |
|---|---|---|---|---|---|
| center | 1 | 0 | 1 | 0 | −1 |
| center | 3 | 3 | 3 | 0 | −3 |
| center | 6 | 4 | 4 | 0 | −4 |
| center | 7 | 3 | 4 | 0 | −4 |
| guest | 7 | 3 | 1 | 0 | −1 |

(Rows quoted from B2's own table; the three remaining `Aria` plays — guest
rounds 1, 3 and 6 — agree at 0 and are not divergences.)

The C1 cluster was **sim over engine**; this is **sim under engine**, on one
card, in both arms. B2 named it and stopped: "the probe was sent for the +2 and
the +2 is answered."

The card's shape is why the mirror image is expected rather than surprising.
`aria_of_recompense` (`docs/furina-cards.yaml:62`) prints
`{op: block, amount: 0, bonus_formula: 1_per_4_fanfare}` — **its entire Block
is a read of the Fanfare meter.** `tools/probe_b2_table.py:57-73` builds a
**fresh** `CombatState` per play and loads only the status strip; a fresh
Furina has `fanfare = 0`, so tier0 returns `1 * (0 // 4) = 0` on every reading
by construction. The engine, meanwhile, was carrying a meter that probe B3
independently recorded climbing 6 → 30 across the same eight rounds
(`docs/probe-b-fanfare-residual.md` Ledger 3, same seed, same fight).

So the leading hypothesis is that this is **another family-B reconstruction
gap** — the same shape as C1, one meter further along — and the probe's job is
to say whether it is only that, or whether an arithmetic residual survives the
reconstruction. **Neither answer is assumed here.**

## The candidate layers this probe must separate

Stated in advance, with what a YES on each would mean. The probe is designed so
that at most one of these can be left standing.

| # | layer | what YES would mean |
|---|---|---|
| 1 | **reconstruction INPUT** — the Fanfare level is absent from the per-card sim state | family B, exactly like C1: the replay never had the reading. Closes all five. |
| 2 | **read timing** — *which* meter value the engine reads: the level as the play was decided, or after the play's own `+2` Fanfare income lands | a resolution-order fact, not an infidelity, but it changes what "the recorded meter" means and must be pinned before layer 1 can be called clean |
| 3 | **arithmetic pipeline** — tier0's `n * (readable // m)` vs the C# `CalculationBaseVar(0m)` / `CalculationExtraVar(1m)` / `CalculatedBlockVar(...).WithMultiplier(ReadableFanfare/4)` composition (`klee-mod/KleeCode/Cards/Furina/Generated/AriaOfRecompense.cs:56-58`), including **where Frail truncation composes relative to the Fanfare division** | a genuine family-C infidelity, small and exactly localizable |
| 4 | **meter-state fields the wire does not carry separately** — `fanfare_floor`, `fanfare_cap`, and whether `readable()`'s clamp-at-zero and the C# `ReadableFanfare`'s `Math.Max(0, …)` were both inert over this corpus | a limit of the instrument, to be declared as such rather than folded into an answer |

## Method

**Nothing new is built if the existing instruments suffice, and the intent is
that they do.** The probe is a third reconstruction column, not a new probe
rig.

1. **Readings.** Re-run `understudy/probe_block.py` unchanged, both arms, same
   seed `TRACKB2`, `--turns 8` — the B2 script verbatim, so the corpus is the
   same corpus and the comparison is against B2's own published table rather
   than against a fresh one. The probe already records `player.resources` at
   every decision point (`understudy/probe_block.py:131`), which is where
   `KLEEMOD_FANFARE` is read; B3 used exactly that channel. **The center arm
   was already re-run with resources recorded (stamp `20260805-132001`); the
   guest arm was not**, so at minimum the guest arm must be re-taken. If both
   stamped logs are still on the machine, the reading half of this probe is a
   file read and no game is launched at all — that possibility is why the cost
   class below has a floor and a ceiling.
2. **The sim side.** Add a third column to `tools/probe_b2_table.py` beside
   `sim_blind` and `sim_status`: `sim_meters` = `sim_status` plus the recorded
   Fanfare level written onto the reconstructed player before
   `effects.resolve_card`. This is **reconstruction, not a rule** — the same
   licence B2 took to load Frail and B3 took to push the recorded selector
   through `effects.SPOTLIGHT_FORCE`. No law is retyped on either side; the
   existing `1_per_4_fanfare` arm of `effects._bonus_formula` is what gets
   exercised, unmodified.
3. **The layer-2 fork is run as two sub-columns, not chosen.** The meter is
   loaded twice — once at the value read *before* the play, once at the value
   read *after* — and both are tabulated. Picking one in advance would decide
   layer 2 by assumption. The B2 script's reading cadence brackets exactly one
   card, so both values exist for every Aria play.
4. **Cap and floor are set explicitly**, not left to `build_player`, so that a
   loaded level cannot be silently clipped by `min(p.fanfare_cap, …)`; whatever
   values are used are printed in the table header.
5. **Output** is the same three-part shape B2 published: the raw per-play
   table, the `sim − engine` distribution per reconstruction, and the arithmetic
   localization. The B2 rows for every other card must reproduce **byte-
   identical** in the new columns' presence — a changed `Regal Bearing` row
   means the instrument moved, and the probe fails rather than reports.

### Instruments

`understudy/probe_block.py` (unchanged), `tools/probe_b2_table.py` (one new
column plus its sub-fork), `tier0/engine/effects.py` and
`tier0/engine/resources.py` as the sim side, read-only. No mod rebuild, no
deploy, no wire change, no new soak corpus. If any of those turn out to be
required, the probe **stops and re-registers** rather than growing.

## Confounders that must be logged

Declared in advance; each is to appear in the write-up with its disposition,
present or absent, the way B2 tabulated its own.

1. **Frail** — present from round 2 in the B2 corpus. Already reconstructed;
   its interaction with the Fanfare division is layer 3 and must be shown as
   arithmetic, not asserted.
2. **The Spotlight arm** — a declared input, not a confounder, but Guest Cast
   generates **no** Fanfare at all (B3 Ledger 2: 27 plays, zero income, both
   instruments), so the guest arm's low meter is the natural control and must
   be read as one rather than as agreement.
3. **The `+2`-per-combat first-Spotlight optimism** (B3 term 3) — tier0 credits
   the play that sets the designation and the engine does not, so the two
   instruments' meters can legitimately differ by 2 for the rest of a fight.
   This is a **known, quantified** offset and must be subtracted explicitly,
   not discovered again.
4. **Encore** — `gain_encore: 5` is Aria's other half and moves a meter whose
   split (absorption vs upkeep) B3 declared unreadable on this wire. It does
   not feed Block, but it must be logged so the row is not later re-read as
   evidence about Encore.
5. **Upgrade state** — `aria_of_recompense+` is `{encore: +3, innate: true}`
   (`docs/furina-upgrades.yaml:42`). Block is unchanged by the upgrade, but
   which copy was in the deck must be recorded, since `innate` changes when it
   is drawn and therefore what the meter reads.
6. **`fanfare_floor` / `fanfare_cap` / the clamp** — layer 4. Whether either
   clamp was ever load-bearing over this corpus is to be stated, and if it
   cannot be determined from the wire, said so.
7. **Salon empty throughout**, as in every measurement to date. Same coverage
   caveat B3 declared.
8. **One character, one card, one encounter, one seed.** Breadth is not the
   point of this probe and no breadth claim may be drawn from it.
9. **Wire freeze.** If the P1.5 wire has moved between B2's stamps and this
   probe's, the two corpora are not the same corpus and the reproduce-B2's-rows
   check in method step 5 is what will say so.

## Expected cost

Stated as a class, since the house has no fixed vocabulary for this yet and
this document should not invent one it cannot honour.

* **Floor — analysis only, no game.** If the stamped B2 logs for *both* arms
  survive on the machine with `resources` recorded, this is a table re-read:
  one new column in `tools/probe_b2_table.py`, one run of it, one write-up.
  **Small — comparable to the desk half of probe (c), which was a code read.**
* **Expected — one short live sitting.** The guest arm is known not to carry
  `resources`, so the likely shape is: re-take two scripted fights at 8 rounds
  on one seed, then the analysis above. **Comparable to probe (a)'s
  measurement half, which is the closest precedent in kind and size** — one
  seed, one floor, a fixed script, no corpus.
* **Ceiling, and the tripwire.** If the divergence does **not** close under
  either sub-column, the remaining question is layer 3, which is a C#-side
  arithmetic read and is a **different and larger instrument** (mod-side
  hook or decompile read, per the B3 precedent for the Encore split). That is
  explicitly **out of scope here**: the probe reports "layer 3 survives" and
  stops. It does not grow into that read without a fresh countersign.

## What each answer would license, and what it would not

**If the divergence CLOSES on the meter-loaded column (layers 1/2):**
* *Licensed:* reclassifying the Aria residual as **family B — a reconstruction
  gap in `understudy/replay.py`'s input**, the same verdict C1 received, and
  saying so in the S7 ledger; recording which meter reading (before-play or
  after-play) the engine matches, as a resolution-order fact.
* *NOT licensed:* any statement about tier0's Fanfare **generation** or
  **decay** (B3 already owns those, and this probe adds nothing to them); any
  claim that other scaling readers — `applause_line`, `crescendo`,
  `dramatic_entrance`, every other `bonus_formula` card — are therefore fine,
  since exactly one card was measured; any change to the fight record's
  contents. Whether the record *should* carry the meter is a ruling, not this
  probe's to make, exactly as B2 left the status-strip question open.

**If a residual SURVIVES (layer 3 or 4):**
* *Licensed:* filing a **named, bounded family-C candidate** with its size per
  play and its arithmetic stated both ways, and routing it — as a candidate,
  not a verdict — to whichever session owns the C-family ledger.
* *NOT licensed:* touching `bonus_formula`, `FRAIL_BLOCK_MULT`, the card sheet,
  the generated C#, or any constant; grading the card; re-opening anything the
  R102 escrow settled; or treating a one-card, one-seed residual as a roster
  property.

**In either case, and stated so it cannot be inferred later:** this probe
grades nothing, re-opens nothing, and moves no escrowed number. It answers one
sentence about one card.

## Proposed exact repro (to be run only on countersign)

```
# readings — the B2 script, unchanged, both arms, same seed
python -m understudy.probe_block --spotlight center --seed TRACKB2 --max-fights 1 --turns 8
python -m understudy.probe_block --spotlight guest  --seed TRACKB2 --max-fights 1 --turns 8

# analysis — the existing table plus the meter-loaded column and its fork
python -m tools.probe_b2_table "understudy/logs/soak/probe-b2-*.jsonl" --meters
```

Readings land in `understudy/logs/soak/probe-b2-<arm>-<stamp>.jsonl`, which is
gitignored per-machine run output — so the stamps must be recorded in the
write-up, and the glob narrowed to them, or a later probe in the same directory
silently widens the corpus. B2 learned that the expensive way and the note is
carried here rather than re-learned.

---

**Status: DRAFT — FOR [USER] COUNTERSIGN, NOT RUN.** The single ask attached to
this document is in the sitting pack at
`docs/sitting-prep-2026-08-05.md` §10.13.
