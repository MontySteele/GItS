# Fontaine Rares & the Banner Goes Live — sprint log

**Executed:** 2026-07-25. **Rulings:** R64, R65, D2 (in `tier0/DECISIONS.md`).
**Origin:** shop-companion-channel close-out, open item 7 — the coverage lint's
live finding that Fontaine designed zero Rare companions, graded by [USER] as a
roster gap rather than a fallback quirk.

Gates at close: suite **828 passed**, mod builds 0 errors, `constant parity: OK
(73 mirrored, 13 declared unmirrored)`, upgrade coverage OK, companion shop
coverage OK, strict domination clean on the character sheets, `art_lint: plan
OK`, art bill **264/264 covered, 0 missing**.

---

## Track A — the four designs

All numbers were PROPOSED; two took [USER] red-pen inside the sprint.

| Card | Elem | Cost/Type | Effect |
|---|---|---|---|
| Navia — Cannon Fire Support | Geo | 1 power | Companion played → 3 Block |
| Clorinde — Impale the Night | Electro | 2 attack | 20 damage, +6 vs aura'd enemies |
| Neuvillette — Heir to the Ancient Sea's Authority | Hydro | 1 power | auras you apply last +1 turn |
| Arlecchino — Masque of the Red Death | Pyro | 1 power | +1 Strength/turn; Bond of Life eats 5 Block/turn |

All four are §4.3 SUPPORT payoffs — buffs, a conditional payoff, aura
manipulation. None is an independent damage engine; none self-scales except
Arlecchino's Strength, which is a per-turn ratchet paid for by the Bond. The
healing law is satisfied vacuously: no card here heals.

### Three things that came from reading rather than inventing

1. **The name check earned its keep before a single name was written.**
   "O Tides, I Have Returned" was the obvious Neuvillette pick and is RESERVED
   four lines above where it would have gone, for his future playable
   kit-Burst. Every new entry now records the Burst name it is deliberately not
   taking, so the next pass inherits the reservation instead of rediscovering
   it.

2. **Neuvillette is deliberately NOT mass-Hydro**, which was the obvious
   design. The sheet already prices that shape: the watchlist note on
   `guest_neuvillette_judgment` records mass-Hydro + the Cryo pair as
   mass-Frozen potential and names that card's 3 self-damage as "the intended
   brake: spamming judgment to fish freezes costs HP". A free mass-Hydro
   applier at Rare would have deleted the brake while leaving the note
   standing. Extending aura DURATION adds no application, so it cannot initiate
   a freeze that was not already going to happen.

3. **Navia avoids Crystallize by construction.** Her trigger is a CARD TYPE,
   not an element — no Geo applied, no shards, no Crystallize rider — so
   nothing here pre-commits how Zhongli's slot-4 archetype will scale. Flagged
   but not resolved: Albedo's `solar_isotoma` is already a Geo defensive
   engine. Different trigger, so they stack without duplicating; if red-pen
   reads two as one too many, Navia is the one to move, because Albedo predates
   her and anchors Mondstadt.

### Red-pen inside the sprint

- **Clorinde 10/+3 → 20/+6.** Recorded consequence: at 2 cost she now out-hits
  Raiden's Musou no Hitotachi (18 — the sheet's stated "biggest one-card hit")
  AND carries a permanent power, where Raiden is deliberately shapeless to pay
  for her number. **`lint_strict_domination` does not see this**: it compares
  within a sheet, and the two live in different nations' files. Flagged in the
  sheet for the red-pen session. Her upgrade was NOT re-scaled — the ruling
  named the base only. **Closed by the Raiden buff below.**
- **Arlecchino: heal-denial → Bond of Life.** The first draft was "+4 on
  Attacks, you can no longer be healed", and it had two defects the redesign
  dissolves:
  - it priced to **ZERO for Kokomi** (LAW 2 forbids her heals outright), making
    it pure upside for exactly one character;
  - it was **not fully buildable** — the engine exposes no heal hook on
    `PowerModel` (checked against `sts2.dll`: the only heal-modifying members
    are rest-site specific).

  The Kokomi interaction is now the good kind: LAW 3 converts her Strength to
  Charge, so Arlecchino pays her in a different currency instead of a dead
  line, and she still owes the Bond in full. That falls out of routing Strength
  through the standard `apply_power` chokepoint rather than writing the power
  dict directly.

**The Bond is paid at turn end, and that is not a shortcut.** Eating the first
N at the gain site would need a funnel neither layer has — Block is added at
~15 places and `modify_block_gained` deliberately covers card block only (Frail
exempts passive/power Block by design). Turn-end deduction is arithmetically
identical (both leave `max(0, gained − N)`) and it is universal, so Navia's
Block and Crystallize cannot dodge the Bond the way a card-only funnel would
let them. The single case where the two differ is a card that reads current
Block mid-turn (the `player_block` token, Body Slam) — reference-pool only, and
refs take no companions, so it is unreachable. Recorded in both layers.

---

## Track B — the banner

**The bug the call-site audit found, which predates the sprint.** See R64. One
line summary: every run of every character rolled a Mondstadt-only banner, so
Itto and Raiden were unreachable in Kokomi's own runs. Measured, fixed, and the
nation set is now derived from the sheets rather than listed.

**C# banner** (`CompanionBanner`) is a pure function of the player's rng seed
via `Rng(seed, name)`, so it needs no persistence, survives save/load for free,
and is per-player in co-op by construction (`PlayerRngSet.Seed` is per player).
Wired into the reward slot and shop slot 1 in the same change, as the standing
ruling required.

**Instruments.** `lint_companion_shop_coverage` now models banner state — while
the banner was a no-op the roster and the drawable pool were the same number,
and they are not any more. It also gained a source tripwire that BOTH channels
still call the filter.

> **The tripwire's first version was inert, and a negative test caught it.**
> It searched for the string `CompanionBanner`, and passed against a file whose
> filter had been deleted — because both files also name the class in a
> comment. Now matched on the CALL. This is the second time in two days that an
> instrument written to catch a defect needed a deliberate break to prove it
> worked (validate S9 was the first). Assume a new tripwire is inert until seen
> to fire.

---

## Track C — measurement (R14: diagnostics, never acceptance targets)

600 Furina/salon runs, realistic loadout (relics + potions).

**C1 — slot-1 Rare availability, banner live.** 1454 slot-1 offers: 1261
uncommon, 193 rare, **all 193 from Fontaine**. Nation-widening rung fired
**0 times (0.0%)** — the registered expectation was "drops to ~0 now that she
has four Rares", and it did; before this sprint it was her everyday path.
Exclusion is near-uniform across the four (23.2% / 25.5% / 23.5% / 27.8%
against a 25% ideal) and every one of the four gets excluded — none is
permanently featured.

**C2 — winrate spread across banner rolls.** Spread **0.033** on an overall
winrate of 0.168, against a computed noise band of **0.076** (~2.5 sd of the
range at 150 runs per group). **Within the band**: consistent with the
registered expectation that no single Rare swings a run, and explicitly NOT
evidence of a real effect. Corroborated by the spread shrinking from 0.077 at
n=300 to 0.033 at n=600, which is what a true effect of ~0 looks like.

> **The first C2 run was worthless and looked clean.** In the bare loadout
> Furina's winrate is ~0, so all four banner groups lost every run and the
> spread was a perfect 0.000 — a cell that reads as a pass while measuring
> nothing. The tool now forces the realistic loadout and prints the noise band,
> so "the spread is small" is graded against what identical groups would
> produce by chance instead of against a feeling.

**Dedicated rng stream:** already satisfied before the sprint —
`random.Random(seed + 2 * 10**9)` sim-side, and a named derived stream C#-side.
Confirmed, not added.

---

## Track D — art

Four shortlists, three ranked candidates each, every `wiki_title` verified with
`art_hunt.py` before being written. Provisional rank-1 picks are live;
`art/contact_sheet_companions.html` is the artifact for the [USER] pick.

Neuvillette's three obvious sources are already claimed at rank 1 by his Guest
Star cameos — which is **D2 working**, not a problem: the shared Rare is a
different card and should not wear the cameo's face. His Rare takes the promo
Card render at `y0.28`, an anchor chosen by eye because `cover_autocrop` took a
torso band with no face, and higher anchors pull in the GENSHIN IMPACT wordmark
(the same caveat already recorded for Kokomi Card).

---

## Red-pen pass 2 — 2026-07-25, and it reached outside the sprint

The remaining numbers went to [USER] as a set. The verdicts:

- **Navia — ACCEPTED as designed.** "Very powerful combo pieces within a
  niche." No change.
- **Neuvillette — WEAK, DEFERRED.** "Aura extension doesn't seem like much of
  a payoff." Explicitly *revisit later* rather than retune now, so the card
  ships at 1 cost / +1 turn and the weakness is on the record instead of in
  someone's head. **This is the live design question the set leaves open:**
  duration is the one Hydro-Sovereign facet nothing else touches, and if it
  cannot be made to pay, his Rare needs a different facet — not a bigger
  number on this one.
- **Raiden — BUFFED, and this is the interesting one.** `2 cost / 18 damage`
  → **`3 cost / 40 damage / Vulnerable 2 / applies Electro / Exhaust`**.
  [USER]: "massive payoff for a very high cost. Rares in general tend to be
  undertuned, so I think this is fine for a front-loaded rare, and has natural
  Kokomi exhaust synergy."

**The Raiden buff closes open item 2 by taking its third option.** The
Clorinde/Raiden pair was flagged BY HAND because no lint could see it, and the
resolution was not "accept the domination" or "move Clorinde" but *move the
other card*. They no longer share a cost or a shape: 2 cost for 20 + a
permanent power, versus 3 cost for 40 + Vulnerable and then she is gone.

Three consequences worth having on the record:

1. **Exhaust changes her class, not just her cost.** She goes from a
   repeatable jackpot to a one-shot, which is what pays for 40. It is also the
   first companion Exhaust that is a *payoff* rather than a brake — every
   other one in the pool (Bennett, Gorou, Sucrose) exists to stop the card
   from recurring. Kokomi's declared exhaust voice is ROTATION, and her deck
   already runs nine Exhaust cards, so a card that leaves after firing is
   thinning on purpose.
2. **3 cost is precedented but new here.** The only other 3-costs in the mod
   are Klee's `bombs_away`, `all_my_treasures`, `playtime_forever`. Raiden is
   the first in the shared companion pool, and 3 is a full turn's energy for
   every character who can draw her.
3. **Her upgrade delta was carried forward unchanged, then answered.** The buff
   ruling named the base only, so `+4` was left standing and *flagged* in
   `kokomi-upgrades.yaml` rather than silently inferred — it was ~22% of the
   old body and ~10% of the new one, thin against every other line on that
   sheet, and Exhaust means it pays exactly once per combat where every other
   companion upgrade compounds on redraw. [USER] answered the flag the same
   session: **`+4` → `+10`** (40→50, a 25% delta, back in line with the
   sheet). Recorded because the two-step is the point — the delta was never
   guessed at, it was flagged and then ruled.

Gates re-run after the buff and again after the upgrade delta: suite **828
passed**, mod builds **0 errors**, strict domination clean across all six
sheets, companion shop coverage OK, upgrade coverage OK.

## Open, and owned by [USER]

1. ~~Red-pen on all four cards' numbers.~~ **DONE** across two passes — see
   above. Carried forward, not closed: **Neuvillette is graded weak and
   deferred.** Raiden's upgrade delta was the other carry-forward and is now
   ratified at `+10`.
2. ~~The Clorinde/Raiden domination pair.~~ **CLOSED** — Raiden moved.
3. **Lore/naming eyes-on audit** (v1.7, non-delegable, not yet done).
4. **Art picks** from the contact sheet.
5. **C2 expectation grading countersign** — the cell is graded WITHIN band
   above; the countersign is that the grading itself is accepted.
6. **Close-out ratification.**

### A note on where the domination flag actually lived

`lint_strict_domination` sweeps **all six sheets** in the pytest gate
(`test_no_strict_domination_on_docs_sheets` passes `loader.DOCS_CARD_SHEETS`),
so within-sheet coverage was never the gap — the gap was and remains
**cross-sheet**, and nothing checks it. Note also that running the tool BY HAND
with no arguments defaults to `klee-cards.yaml` + `furina-cards.yaml` only and
prints a confident `CLEAN` for two sheets out of six. The gate is the honest
instrument; the bare command line is not.

## Cross-session note

`CompanionSlot.Roll` and `CompanionPool.Eligible` gained banner awareness.
**Klee's and Kokomi's reward slots inherit banner behaviour the moment
Mondstadt or Inazuma exceeds three Rares** — Mondstadt sits at exactly the cap
today, so it is one card away. Any workstream adding a 5-star to either nation
is turning the banner on for that nation.
