# Shop companion channel — re-run registration (DRAFT, awaiting countersign)

> **Status: DRAFT. Nothing here has been run.** No number in this document was
> measured. The instrument was repaired and the shop world was changed on
> 2026-08-10; this packet asks to re-run the measurement in the new world.
> **That world is `RT10/D14/P6/C9`, `C9` including the X7/X8 rarity erratum
> — §2 enumerates it in full, and it is the world the re-run measures.**
> The predictions in §5 are deliberately blank — they are [USER]'s to fill in
> before any seed is run.

**Plain English is a standing requirement for this packet.** Terms are glossed
where they first appear.

---

## 1. Why re-run at all

The shop sells companions from two slots. In July we measured how that channel
behaves and wrote down three predictions (P1, P2, P3). Two things have since
gone wrong with that measurement, and both were confirmed on 2026-08-10.

**The world changed.** [USER] restored the *rarity floor* on slot 2. A rarity
floor means the slot will not offer a card below a set quality band — here,
nothing below Uncommon. Between R116 and 2026-08-10 slot 2 had no floor, so
roughly six offers in ten were Commons at 50 gold. Now both slots offer
Uncommon or better, and the cheapest companion in the shop is 75 gold. A shelf
that stops selling cheap cards changes what a purse buys at every visit, so
the old numbers describe a shop that no longer exists. The world stamp moved
from `CONSTANTS_VERSION` 8 to 9 to record that.

**The instrument was broken.** Two defects, both in
`tier05/exp_shop_companion_channel.py`:

- **It credited purchases to the wrong shop visits.** A run walks into several
  shops. The record of what was *offered* and the record of what was *bought*
  are both kept as one flat list per run, and the old code matched a purchase
  to an offer by slot number alone. So one purchase at the third shop was
  counted as a purchase at the first and second shops too. The reported
  "slot-1 buy rate" (P1) therefore counted the visits where the player
  *declined* as visits where they bought. It was too high, and by an amount
  that grows with the number of shops a run enters.
- **It guessed the rarity of what was bought.** For slot 2 it inferred rarity
  from the price paid — "150 gold means Rare, anything else means Uncommon" —
  with a comment claiming rarity was recoverable from the price. It was not:
  while slot 2 could sell Commons at 50 gold, every Common purchase was filed
  as an Uncommon. That is precisely the bucket P3 grades, so P3 graded a
  number it had partly invented.
- **It said "gold was never the constraint" when it did not know that**
  (found 2026-08-11). The shop wrote down whether each companion offer was
  affordable *when the player walked in*, and nothing else. But a card can be
  inside the purse at the door and outside it a moment later, once the same
  visit has bought something else — and the shop had two exits that recorded
  nothing at all: the buy loop dropping a card the pilot wanted but could no
  longer pay for, and the visit ending the instant the purse fell below the
  cheapest thing left on the shelf. With no offer unaffordable *on arrival*,
  the report printed "gold was never the constraint" even if both of those
  had happened at every shop in the run. That line asserted a conclusion the
  data could not support.

All three are fixed. The purchase and offer records now carry a *visit index* (a
plain counter: which shop of this run is this), so a purchase is joined to the
offer it actually answered; the purchase record carries the card's true
rarity instead of a guess from its price; and the shop now keeps a
*priced-out log* — one line every time gold could not reach a card, written at
the moment it could not — so the money question is answered by counting
events rather than by asserting that none occurred.

## 2. One window, one world

**The registered world is `RT10/D14/P6/C9`, including the X7/X8 rarity
erratum.** In plain English, and as the standing requirement for this
re-run: this is the world the re-run measures. Everything listed below is
inside one window, and a run of this instrument that does not report this
exact stamp is not the registered measurement.

What that one window contains, in full:

1. **The slot-2 rarity floor, restored** ([USER] 2026-08-10, S4-G10). The
   shop's wildcard companion slot rolls Uncommon-or-better in both engines;
   Commons leave the paid channel and the 50-gold band is unreachable.
2. **The instrument fixes** to `exp_shop_companion_channel` — per-visit
   purchase attribution, true slot-2 purchase rarity, the
   gold/affordability/crowd-out logging, and (2026-08-11) the priced-out log
   described below.

   The priced-out log is what makes Q2 answerable, so here is what it
   records. Every time the shop cannot reach a card, it writes one line. Each
   line says which shop of the run it was (`visit`), which card and at what
   price (`id`, `price`, `rarity`), which door it came from (`channel`:
   the character shelf or the companion channel, and `slot` for the two
   companion slots), the gold held at that instant (`gold_now`), the gold
   held when the visit began (`gold_at_visit`), and how much of it had
   already been spent at this shop (`spent_before`). Lines come in two kinds,
   marked by `residual`:

   - **the pilot's preferred pick** — it named a card and could not pay for
     it. `spent_before` of 0 means the card was out of reach the moment it
     walked in; anything higher means *this visit's own earlier purchases*
     put it out of reach, which is the case the arrival check structurally
     cannot see.
   - **the stranded shelf** — what was still for sale, and still out of
     reach, when the visit ended. A field named `exit` says whether the visit
     ended because the purse fell below the cheapest remaining card
     (`guard`) or because the pilot stopped wanting anything (`skip`); on a
     skip, only cards gold could not have covered anyway are written down, so
     "stranded" never counts a card that was merely declined.

   **This changes nothing about how a run plays.** All randomness in a run
   comes from one random number generator, and the draft policies sort rather
   than draw from it; writing a line into a list draws nothing. The proof is
   an equality, not an argument: the same seeds produce byte-identical runs
   before and after the log was added.
3. **The five R82-reopen enchant events**, which arrived with
   `RUNTEMPLATE_VERSION` 10 and move the event-pool odds in every act for
   every character. This is why the stamp reads RT10 and not RT9, and it is
   why no number from the original cell is a cheaper sample of this one.
4. **The three rarity promotions** (R161/R162): `friendly_visit`,
   `chain_fuse` and `careful_arrangement` move Common → Uncommon. They joined
   `C9` under its own open-window clause, before any number was published
   under `C9`. They are named here because they change what Klee's draft
   offers, and Klee is one of the three characters this cell runs — the
   companion channel is not the only thing competing for the purse.

The floor restoration, the instrument repair and the rarity erratum land
together, in the same commit range, under one stamp (`CONSTANTS_VERSION` 9).

On the one-variable rule (EXPERIMENTS, D4: one measurement window contains
one change to the *world*), stated without softening:

- The **instrument repair** is not a world change at all. It changes only
  what we write down about a game that plays identically either way. The new
  fields are additive: nothing reads them to make a decision and none of them
  draws from the run's random number stream, so a run plays out the same
  whether or not they are recorded. That was checked by re-running the cell's
  own arms on the same seeds and comparing the results before and after: they
  match exactly.
- The **slot-2 floor** is the world change this cell is *about*, and it is
  the only change inside the channel under measurement.
- The **enchant events** and the **rarity promotions** are world changes
  outside the channel. They are not variables this cell manipulates — they
  are the same in both arms, and the arms differ only by the `companions`
  flag — but they are honestly part of the world, and that is why they are
  named above rather than left to the stamp to imply. The cost of carrying
  them is that this cell's absolute numbers are not comparable to any
  pre-C9 read; the within-cell arm contrast, which is what Q1–Q4 ask, is
  unaffected because both arms sit in the same world.

Landing them apart would be worse, not better. It would mean either measuring
the new world with a broken instrument, or measuring the old world with the
fixed one — and the old world is already archive. One window is the honest
shape.

**What this costs:** every §4.7 shop number published under C6, C7 or C8 —
including the whole original SHOP-P1/P2/P3 cell — is archive. Archived numbers
are banner-marked where they were published and are never rewritten (R101b).

## 3. Questions

**Q1 — the true slot-2 purchase mix under the floor.** Of the slot-2
companions actually bought, what fraction are Uncommon and what fraction are
Rare? This is P3 asked honestly for the first time: with true rarities off the
purchase record, and in a world where Common is not on the shelf at all.

**Q2 — the money question.** Was a preferred purchase ever priced out? S4-G10
raises this because runs end with roughly 220 gold unspent, which suggests
money is *not* the constraint. A purchase log cannot settle it, since a
purchase log only records what the purse could already reach.

The question is now answerable, and in three separate parts rather than one.
The instrument reports each of them as a count:

1. **Priced out at the door.** How many companion offers cost more than the
   gold held when the visit began. This is the arrival check that already
   existed.
2. **Priced out during the visit.** How many times the pilot named a card it
   then could not pay for — and, of those, how many were affordable when it
   walked in and stopped being affordable because it had already bought
   something else at that same shop. Until 2026-08-11 this event was dropped
   on the floor; it is now the priced-out log's first kind of line
   (`spent_before` greater than zero is the "priced out by its own earlier
   buys" case).
3. **Left on the shelf.** How many cards were still for sale and still out of
   reach when the visit ended — the purse having run below the cheapest thing
   left. This exit was also silent before; it is the log's second kind of
   line.

Together these are what "was a preferred purchase ever priced out?" actually
means. Note that part 2 is the *narrowest* reading of "preferred": it is the
pilot's own top pick at that moment, not merely something on the shelf.

**Q3 — the true P1 buy rate.** With purchases joined to their own visit, what
fraction of the visits that offered slot 1 ended in a slot-1 purchase? The
pre-registered band for P1 was 10–35% of visits. The old figure was inflated
by the attribution defect, so this is a first honest read rather than a
comparison.

**Q4 — crowding out, at visit resolution (descriptive).** Within a single
visit, companions are resolved before the relic shelf is offered, so a
companion purchase always comes first in time. The question is whether it
leaves the purse too thin for the relic: what is the relic buy rate in visits
where a companion was bought, against visits where none was? The existing
crowd-out block compares run totals across two arms; this is the same question
at the resolution where the trade-off actually happens.

**Not asked here.** Whether any of these numbers is good or bad, and whether
the channel should be re-priced or re-stocked. That is a design call and it is
[USER]'s, downstream of the grade.

## 4. What is measured, and with what

- Instrument: `tier05/exp_shop_companion_channel.py`, as repaired 2026-08-10
  and extended with the priced-out log 2026-08-11.
- Arms: unchanged — `companions` off against `companions` on. That flag is the
  only difference between the two arms; same seeds, same characters, same
  policy, same everything else.
- Characters: unchanged — `klee`/demolition, `furina`/salon, `kokomi`/priest.
- World: **`RT10/D14/P6/C9`**, `C9` including the X7/X8 rarity erratum — the
  world enumerated in §2. The report must carry the full run-cell stamp
  (`RT/D/P/C`) or it is not citable (R68), and it must read `RT10/D14/P6/C9`
  or it is not *this* registration's measurement.
- Every output line the instrument printed before the repair still prints, so
  the pre-existing reads stay reproducible. The new reads are printed on lines
  labelled `NEW`.

**Proposed n and seed** — from the prior run's own convention, which is the
only convention this cell has:

- `RUNS = 500` per arm per character (3 characters × 2 arms = 3000 runs).
- `SEED = 20260725`, unchanged.

Keeping the seed does not make the old and new numbers comparable — the world
moved, and switching the channel on consumes randomness, so runs diverge
rather than pairing. It is kept because changing it would buy nothing and
would remove the one thing still held fixed. **If [USER] wants tighter
intervals on the slot-2 mix (Q1), raising `RUNS` is the lever; slot-2
purchases are a small fraction of runs, so that count is the binding sample,
not the run count.** Both numbers are [USER]'s to confirm or change before the
run.

## 5. Predictions — [USER] SLOTS, to be filled before any seed is run

Measurement law: predictions are written from design intent, before the
numbers exist, and are never revised against the run that grades them. The
slots below are left empty on purpose. **Filling them is a [USER] act and the
run does not start until they are filled and this packet is countersigned.**

> **[USER] SLOT — Q1, slot-2 purchase mix.** Expected share of slot-2
> purchases that are Uncommon (rather than Rare), as a band:
> `____ % – ____ %`. Acceptance target or diagnostic-only? `____`
>
> *Context for the call, not a prediction:* the old P3 band was "≥ 60%
> Uncommon", graded as a diagnostic under R14 discipline. Under the restored
> floor the offer table is 87.5% Uncommon / 12.5% Rare, and Rares cost twice
> as much, so both the shelf and the purse point the same way. Whether the
> old band is still the right one is the call.

> **[USER] SLOT — Q2, the money question.** Prediction: is gold ever the
> binding constraint on a companion purchase? `YES / NO`, and the band for
> the share of offers that are unaffordable on arrival: `____ % – ____ %`.
> What result would count as "price is not governing this channel"? `____`
>
> *Note on the slot, not a prediction:* the YES/NO stays exactly as written,
> and the instrument now supports it. Before 2026-08-11 it did not — a `NO`
> could only ever have been read off the arrival check, which is blind to a
> card that goes out of reach mid-visit, so the honest answer would have been
> "unmeasured" no matter what the run printed. The priced-out log closes that
> gap: `YES` is now falsifiable against three counts (the three parts of Q2
> in §3), and the run reports all three. The band above still refers to the
> arrival share specifically; if you want bands on the other two counts as
> well, write them in here.

> **[USER] SLOT — Q3, true P1 buy rate.** Expected slot-1 buy rate, as a
> share of the visits that offered slot 1: `____ % – ____ %`. Does the
> original 10–35% band stand as the acceptance band in the new world, or is
> it replaced? `____`

> **[USER] SLOT — Q4, crowding out.** Expected direction: does buying a
> companion reduce the relic buy rate in the same visit? `YES / NO /
> NO PREDICTION (descriptive)`. If yes, by how much: `____ pp`.

> **[USER] SLOT — P2 (winrate delta), carried forward.** The original band
> was "positive and no more than +2.0 percentage points". Does it stand under
> the restored floor? `STANDS / REPLACED BY ____`. The floor removes the
> cheap tier, so the channel is now strictly more expensive per card, which
> pushes the delta in an unobvious direction: fewer purchases, better ones.

> **[USER] SLOT — redesign trigger.** What result, if any, reopens the shop
> design rather than merely being recorded? `____`

## 6. Contamination and known limits

- **The sim models one seat.** Co-op shop behaviour is not measured here and
  cannot be; nothing in this packet speaks to it.
- **The arms are not strictly paired.** Turning the channel on consumes
  randomness, so run *N* in the on-arm is not run *N* in the off-arm with one
  thing changed — it is a different run. The read is a distribution over many
  runs, not a per-seed difference. Unchanged from the original cell.
- **Companions get first claim on the purse** by construction: the shop buys
  cards before the relic and potion shelves are offered. Q4 measures the
  consequence; it does not remove it.
- **Affordability is measured at the door *and* during the visit** (this
  limit was partly lifted on 2026-08-11). The `affordable` flag on each
  companion offer still means only what it always meant: the price was within
  the gold held when the visit began, before anything else was bought. What
  is no longer missing is the rest of the visit — the priced-out log records
  a card the pilot wanted and could not pay for after its own earlier
  purchases, and a card still for sale and still out of reach when the visit
  ended. So "was there change left afterwards" is now measured too, and it is
  reported separately from the arrival figure rather than folded into it.

  What remains unmeasured is narrower: the log records the *moments the shop
  actually reached for a card*. A card the pilot never wanted and could not
  have afforded either way is counted only if it is still on the shelf at the
  end; and no counterfactual is computed — nothing says what the run would
  have bought with more gold.
- **The drafter is a pilot, not a player.** It buys what its valuation ranks
  highest and it does not save for later. A low buy rate is evidence about
  the drafter as much as about the shop, and that limit applies to P1 and Q3
  as it always did.
- **No C# side.** The mod moved with the sim (same floor, same omission
  behaviour), but there is no C# test project and no mod-side instrument.
  Nothing in this packet is a prediction about the mod's behaviour.

## 7. What happens when it is countersigned

1. [USER] fills §5 and countersigns; the filled predictions land as their own
   commit, before any seed in the registered range is run.
2. The cell runs at the §4 n and seed, under `CONSTANTS_VERSION` 9.
3. The report is published with its full stamp, graded against §5 blind.
4. This packet and its EXPERIMENTS pointer leave HEAD when the grade lands.
