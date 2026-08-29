THE PROTOCOL FOR THIS SEAT. It overrides anything below that conflicts with
it.

You are reading a proposal against a written charter or brief. Your output is,
PER ARM:

  * FOLLOWS, or REQUIRES_MODIFICATION; and
  * the CLAUSE you ruled against, named.

That is the whole output. You may NOT supply card text, a number, a mode, a
rewritten row, or any other remedy. A remedy you volunteer is DISCARDED
unread, and the reasoning that produced it is discarded with it -- so a
verdict that leans on your remedy is a verdict that gets thrown away. Where a
number has to be chosen it is derived by lifting a value off a shipped card,
and your only part in that is confirming that the derived row FOLLOWS.

WHY. Independence here is by MODEL FAMILY, author against grader (R217 C).
A seat that writes part of a row and then reads it has read its own work, and
the reading is not evidence. Naming the clause keeps you on the reading side
of that line; naming the fix moves you across it.

You are the DOCTRINE SEAT for a card game modification. You did not write the
proposal below, you are not being asked whether it is good, fun or balanced,
and you are NOT being asked to design anything.

THE PROTOCOL YOU ARE UNDER, verbatim from the repository's OPERATIONS.md:

    The seat's other job -- reading a slice proposal against the character
    charter before anything is built -- answers FOLLOWS or
    REQUIRES_MODIFICATION per arm and NAMES THE CLAUSE it ruled against. That
    is the whole output. It may not supply card text, a number, a mode or a
    rewritten row: a remedy it volunteers is DISCARDED, and Claude re-derives
    from the named clause.

So: name clauses, not remedies. If you find yourself writing a number, a card
face, or "you should instead...", stop and name the clause that forced it. Any
remedy you volunteer anyway will be recorded and marked DISCARDED, and it will
disqualify your model family from grading the row later, so it costs the
process something real.

WHY YOU: independence is by MODEL FAMILY, author against grader. Claude
authored this proposal. You are the other family. A seat that writes a row and
then grades it has graded its own work.

THE SANDBOX. You are read-only and previous runs of this seat found the command
policy on this machine rejects every file read. DO NOT TRY TO READ THE
REPOSITORY. Everything you need is pasted below verbatim and nothing has been
summarised for you: the full proposal, the governing LAW sections (Kokomi's
character identity, the D1-D9 design charter, the card-sheet rules), the
character's kickoff charter sections, and her entire card sheet.

============================================================================
WHAT YOU ARE ASKED
============================================================================

The proposal redesigns one resource. Read it against the doctrine below and
answer for EACH of these FIVE ELEMENTS, and then OVERALL:

  E1  THE QUEUE      -- the Bake-Kurage remembers a copy of every Companion
                        card Kokomi plays, in play order, for the fight.
  E2  THE FUEL       -- Charge accrues only from Kokomi's own non-Companion
                        cards; Companions (including Mustered ones) pay none.
  E3  THE THRESHOLD  -- at >= T Charge the jellyfish PLAYS the front of that
                        memory for 0 energy and pays T. Automatic, one card
                        per turn. This means Charge is SPENT, which the
                        shipped law (R80) forbids.
  E4  THE PULSE      -- the jellyfish's end-of-turn action stops reading the
                        Charge bank and is keyed to the TYPE of the last card
                        played (Attack -> damage, Skill -> Block, Power -> an
                        open pick).
  E5  THE UI         -- a visible strip on the jellyfish showing the queued
                        cards in order, the Charge meter moved onto it with
                        the threshold marked, and an indicator of what the
                        pulse will do.

For each element, answer these three, numbered, in this order:

  1. DOES IT ADDRESS THE NOTED ISSUES? -- YES / NO / PARTLY, with reasons.
     The three noted issues are: (a) the player waits for Charge rather than
     deciding anything with it; (b) defence feeds the finisher, so blocking
     with Companions is also how you win; (c) Companions are boring bodies.
  2. DOCTRINE: FOLLOWS or REQUIRES_MODIFICATION -- and NAME THE CLAUSE, by its
     identifier (D1..D9, a LAW bullet, R80, a sheet rule) and by quoting the
     sentence you ruled against. Two clauses are EXPECTED to come back
     REQUIRES_MODIFICATION -- R80 "Charge is never spent" and the starter
     relic's printed text -- and that is the point of the exercise, not a
     failure: those amendments belong to the human owner. Say so plainly if
     you agree, and say plainly if you think MORE clauses must move.
  3. RISK. Anything you see that the proposal has not.

Then OVERALL, four things:

  A. Does the proposal as a whole address the three noted issues? YES / NO /
     PARTLY.
  B. FOLLOWS or REQUIRES_MODIFICATION overall, and the COMPLETE LIST of
     clauses you say must move for it to be legal. This list is the single
     most useful thing you produce.
  C. THE D2/D4 QUESTION, asked directly: the jellyfish fires AUTOMATICALLY --
     the player cannot choose when, cannot decline, cannot pick which card.
     The proposal's defence is that the queue is VISIBLE and ordered by the
     player's own play order, so the steering happens earlier. Does a visible
     queue satisfy D2's "must feed a decision the player can steer" and D4's
     "at the decision point the player can perceive and forecast the
     consequences that matter"? Or is an automatic action still an automatic
     action? Name the clause either way.
  D. Anything in the proposal that is INTERNALLY INCONSISTENT with the
     doctrine pasted below -- a claim it makes about the law that the law does
     not support.

Keep each answer to a short paragraph. Quote the clause text you rule on.



############################################################################
## THE PROPOSAL (review/active/kokomi-kurage-memory-2026-08-29.md)
############################################################################

# Kokomi — the Kurage's memory: a Charge redesign

**2026-08-29. Branch `kokomi-kurage-memory`, cut from
`origin/process-review-2026-08-29` at `e352db4`.** This is a document and a
review. **No engine code, no card row, no LAW line moves on this branch** — not
one shipped file is edited by it. It supersedes `review/active/kokomi-slice-2-2026-08-29.md`
§9 PICK 2, which asked you to choose among five ways to change the Charge rule.
[USER] proposed a sixth on 2026-08-29, and it is better than the five, so the
five are withdrawn and this is the proposal that replaces them.

**I authored this, so I am not allowed to say whether it is good.** §7 carries
the independent seat's read, which is the only judgement in the file, and even
that is a doctrine read (FOLLOWS / REQUIRES_MODIFICATION and the clause it
names) and never an approval.

---

## 1. The question, and the evidence

### [USER]'s words — this is the spec

> "Perhaps Kurage stores a 'memory' of played companion cards (building up a
> stack) and then auto-plays them (one card per turn, costing Charge) when your
> Charge (now derived from Kokomi's own cards) hits some target threshold? So
> building Charge becomes an energy cheating mechanic. Kurage's own off-turn
> actions could still follow the proposed pattern based on the type of card you
> last [played or exhausted] based on whether it was a skill, power or attack?"

> "We need to add a UI element that shows the bank of cards queue'd for Kokomi
> and move the Charge meter there."

And on the automatic firing, against the Klee precedent: Klee's Sparks are a
different problem — *"sparks are spent when you don't want them to"* — *"but
this one can be made legible."* Firing stays automatic. **The visible queue is
what makes it steerable**, because what you put in the queue, and in what
order, is the whole decision.

### What slice 2 found, and what [USER] said about it

Slice 2 built four ways to give the bank a second use and ran them through the
funnel: two ADVANCE, two RETURN. [USER]'s verdict on the four shapes closes
that line of enquiry rather than continuing it:

- the **threshold** arm is *"glorified power scaling with extra steps … Furina's
  Fanfare pattern"*;
- the **mode** arm *"forces an extra selector step"* on every play;
- the **spend** and **formation** arms are *"Furina's Encore pattern"*.

That is three of the mod's existing resource grammars re-run on a fourth
character, which is the one thing the roster does not need. Charge was
inspired by the Regent's Forge in the first place, and Muster already borrows
his card-to-minion idea; a spend that looks like Encore would make Kokomi the
third character whose meter is a bar you fill and cash.

### The blind tester, on the shipped character

Run `20260829-065208`, `gpt-5.6-sol`, build 0.2.1269 on game v0.111.0, in its
own words at run end:

> "The character seems to bank Charge through utility cards, then convert it
> into large end-turn Bake-Kurage pulses. … Kokomi Burst accumulated
> constantly, but I never saw how to spend it."

> "The recurring tension was whether to spend energy on safe Block or accelerate
> damage and Charge."

> "Play became repetitive when hands filled with several identical Coral Guards
> or Water's Edges. **Many turns reduced to covering the printed attack exactly,
> playing every free card, then using Bake-Kurage or waiting for Raiden.**"

The last sentence is the finding. A blind reader with no idea what any of it was
for described the loop as *cover, dump, wait*.

### The diagnosis — three shipped facts that make one plan correct

1. **The bank is permanent and never spent** (R80). It only rises, so every
   Charge point is strictly better than no Charge point and there is never a
   moment where holding costs anything.
2. **The pulse is unbounded and reads that bank live.** A starter basic —
   `bake_kurage`, cost 1, basic rarity — puts a jellyfish on the field whose
   turn-end pulse is `KURAGE_PULSE_BASE + Charge × KURAGE_PULSE_PER_CHARGE`,
   shipped at `4 + 3 × Charge`, and `before_sun_and_moon` raises the multiplier
   permanently and stacks.
3. **Defence feeds the finisher.** Muster's subsidy (R216 D): a Mustered
   Companion costs 1 less and Exhausts, and the Exhaust pays 1 Charge through
   the universal funnel. So blocking with a Companion *also* advances the
   finisher.

Put together, "block with Companions until the jellyfish is lethal" is not a
degenerate line a player discovered. It is the correct line **by
construction** — the three rules jointly build it, and the playtest found it
because it was there to find:

> [USER], 2026-08-26: *"Kokomi's Charge mechanic is ridiculously powerful (often
> hitting for 100+) but otherwise suffers from low numbers … her best turn is
> usually 'spam companion cards to block until you can hit with the Charge'."*

Against LAW D2 that is the named anti-pattern in as many words: *"'Watch it rise
until the number is large' is not a decision."*

### What this proposal does about it

It removes all three facts at once and puts one decision in their place.
Charge stops being a damage multiplier and becomes **an energy-cheating clock**:
the number you are building is not how big the hit will be, it is *how soon the
jellyfish plays a card for you*. The Companions stop being interchangeable
blocking bodies and become **the contents of the queue** — the thing you are
choosing when you decide which one to play and when.

---

## 2. The mechanic, stated exactly

### The queue — the Kurage's memory

- **What enters it.** When Kokomi **plays a Companion card**, the Bake-Kurage
  remembers it: a **copy** of that card is appended to the queue. The played
  card itself resolves and goes wherever its own rules send it — and for a
  Mustered Companion that is the Exhaust pile, which is exactly why the memory
  has to be a copy rather than the card. A remembered copy carries the printed
  face it was played with, including its upgrade state and any Muster cost
  reduction, because the memory is of *the card you played*, not of a pool row.
- **Order.** Play order. The **front** of the queue is the oldest remembered
  card and the next one to fire. Nothing reorders it; there is no selector, and
  that is deliberate — the ordering decision happens when you play, not when it
  fires (the mode arm's "extra selector step" is the thing [USER] rejected).
- **Scope.** Per fight. The memory empties when the fight ends. It is not a
  deck, it does not persist across a run, and no reward, relic or event writes
  to it.
- **Bound.** The queue is uncapped by default; a cap is **TBD-by-sim**. Note
  honestly that a queue is *self-bounding in a way the shipped bank is not* —
  every fire removes one — so an uncapped queue is not the shipped unbounded
  bank wearing a new hat. If sim finds an unfireable backlog, a cap is the
  first knob.

### The fuel — Charge, from Kokomi's own cards

- Charge is now accrued **only from Kokomi's own non-Companion cards**. A
  Companion card — Mustered, drafted or granted — pays **no Charge** by any
  route. The rotation law's existing definition extends by one clause: a Status
  or a Curse is not one of her cards, and now neither is a Companion.
- Whether the funnel is her **Exhausts only** or **any play or Exhaust** is
  **PICK A**. The recommendation is Exhausts only, which keeps the shipped
  `CHARGE_PER_EXHAUST = 1` funnel and the kickoff's own decision loop — *"every
  card kept is engine; every card burned is Charge"*, the deck as her second HP
  bar — intact.
- Printed `gain_charge` lines on her cards are unchanged in kind: they remain
  the §2.1 premium bonuses on top of the funnel. Their **numbers** are a
  re-derivation question (§4), because they were sized against a bank that never
  drained.
- **Flawless Strategy is untouched.** Strength she would gain still becomes
  Charge (LAW 3), and under this proposal that conversion now buys tempo instead
  of a multiplier — which is a strictly better reading of the −100%-crit trade.

### The threshold — the fire

- At **the start of Kokomi's turn** (PICK B; the alternative is end of turn,
  with the pulse), if Charge ≥ **T**, the Bake-Kurage **plays the front card of
  its memory for 0 energy** and Charge is reduced by **T**.
- **One card per turn, maximum.** The bank does not fire twice in a turn no
  matter how large it is; surplus Charge stays banked toward the next turn.
  That is the clause that stops a large bank from becoming a burst-damage
  multiplier by another name.
- **T is TBD-by-sim.** The derived candidate is **5**: that is the total Charge
  a single shipped card already yields on one play — `ritual_purification`
  (common, cost 1) is `exhaust 1 → gain 4 Charge, draw 1`, and with the funnel's
  1 that is 5 on one card. A threshold of one card's worth means the engine
  fires roughly as often as she rotates, which is the cadence the kickoff's
  decision loop already describes. It is a candidate, not a pick, and it is the
  first thing a sim arm should move.
- **Targeting** of an auto-played attack is **PICK E**.
- **Empty queue at threshold** is **PICK D**.

### The pulse — keyed to the last card played

The jellyfish's own end-of-turn action stays, and stops reading the bank
entirely. It is keyed to the **type of the last card Kokomi played this turn**:

| last card | pulse |
|---|---|
| **Attack** | damage, `KURAGE_PULSE_BASE` — **shipped**, 4, flat, no Charge term |
| **Skill** | Block, 5 — **shipped**: that is `kurage_ward`'s printed grant on Kurage's Oath |
| **Power** | **PICK C** — Hydro application (reaction enabler), or refresh/extend the jellyfish, or draw |

- **The per-Charge multiplier is gone.** `KURAGE_PULSE_PER_CHARGE = 3` retires,
  and with it `kurage_amp` / `before_sun_and_moon`, which exists only to raise
  it. That constant is the whole "100+ hit" the playtest named, and it is the
  reason the shipped bank can only be watched.
- Hydro application on the damage pulse is **shipped behaviour** and stays.
- If Kokomi played no card at all this turn, the pulse does not fire. That is a
  price on a wasted turn rather than a free tick, and it is the D3 half of the
  pulse.

### What the jellyfish is now

**Persistent for the fight, summoned once.** The shipped summon holds for
`KURAGE_DURATION` turns (shipped: 1) and a second cast *refreshes rather than
stacks* — the `oz_summon` stacks-are-turns grammar. That made sense for a
metronome whose only job was to tick. It does not survive contact with a memory
queue: a queue that evaporates when a 1-turn summon lapses is a resource the
player loses by not re-casting a basic, which is a D4 invisible-feed defect
waiting to happen, and re-casting a basic every turn to keep your own bank alive
is not a decision.

So: `bake_kurage` **summons the jellyfish once and it stays for the fight**;
further copies of the card need a second job, which is a re-authoring question
(§4), not a number. `KURAGE_DURATION` retires as a live constant. The Garment's
Tamakushi Casket refresh link retires with it.

### Why this is not the three patterns [USER] rejected

- It is not Fanfare: the bank is not read proportionally by anything, ever. No
  card scales on it. There is no "+1 per 2 Charge" left in the design.
- It is not Encore: the player never chooses to spend it, never pays it as a
  printed price on a face, and never trades it against another currency at the
  moment of play.
- It is not a mode selector: there is no extra step at play time. The steering
  happens by *which Companion you play, and when* — a decision you were already
  making for its own reasons.

What the bank buys is **energy**, which is the one currency Kokomi's Commander
lane has never had enough of, and the thing a queue of already-played Companions
is uniquely able to hand back.

---

## 3. The UI element

[USER]'s requirement: *"We need to add a UI element that shows the bank of cards
queue'd for Kokomi and move the Charge meter there."*

### The strip

A horizontal **memory strip** anchored to the Bake-Kurage on the field:

- **The queued cards, in order, front first.** Miniature faces, left to right,
  oldest at the left. The front card is drawn larger or ringed — it is the one
  that fires next — and hovering any of them shows the full face it was
  remembered with, upgrade state included.
- **The Charge meter moves onto the strip**, under the queue, **as a bar with
  the threshold marked** — and this is the fix to a defect the shipped gauge
  documents about itself. `GaugeBridge`'s Charge spec is *"THE ONE GAUGE WITH NO
  BAR"* because *"there is no ceiling to draw against and no threshold to cross
  … a bar would invent a target, and her whole design question is how long a
  player is willing to keep banking with no target in sight."* Under this
  proposal **there is a target**, it is T, and the bar becomes the honest render
  rather than the invented one. The bar fills 0→T and resets by T on each fire;
  Charge above T is shown as the overflow it is.
- **The last-card-type indicator** sits at the strip's right: one glyph — blade
  / shield / spiral — showing what the pulse will do at this turn's end, updating
  live as she plays. Under PICK C's Hydro option it also shows the element it
  will apply.

### What the bridge must expose

This is `EB-181`'s class of gap and the same fix belongs upstream in the
vendored bridge, not in the blind render. The blind seat today cannot read any
of it, and under this design a seat that cannot read the queue cannot play the
character at all:

1. **The queue** — an ordered list of card faces (the existing `BuildCardInfo`
   shape: `name`, `type`, `cost`, `description`, `rarity`, `is_upgraded`,
   `keywords`), front first, on the combat state.
2. **The bank and its threshold** — the resource snapshot in
   `vendor/STS2_MCP/gits/GitsResources.cs` reflects an `Id` and an `Amount`
   only, which is exactly `EB-181`'s second half ("a meter has no maximum").
   Charge needs `amount`, `threshold`, and whether it fires this coming turn.
3. **The pulse** — the summon's entry needs the pulse *type* (attack / skill /
   power branch) and its *amount*, not just a stack count, so the seat can
   forecast the end of its own turn.

### D4, in one sentence

**Everything that will fire next turn is readable this turn**: the card that
will be played, the fact that it will be played, and what the pulse will do.
Under this design that is not a nice-to-have — an automatic action whose input
the player cannot see is precisely the D4 defect ("invisible feeds"), and the
strip is the whole reason [USER] judged this legible where Sparks are not.

---

## 4. What it retires or re-derives

### LAW deltas — [USER]'s to make, quoted verbatim, old → new

**(i) `docs/current/LAW.md`, "Character identity — Kokomi", the Charge bullet.**

Old, verbatim:

> - **Charge is never spent** — uncapped, read but never consumed, card-event-driven
>   with no passive accrual *(Ancient carve-out: R127, see card-sheet rules)*.
>   The engine is kit-level (relic + starter), never
>   draft-gated; the relic holds only bookkeeping, all payoff magnitude lives in
>   cards. (kokomi §0, §2.1; R80; R16)

Proposed new:

> - **Charge is spent by the Bake-Kurage and by nothing else** — uncapped,
>   accrued only from Kokomi's own non-Companion cards, card-event-driven with no
>   passive accrual *(Ancient carve-out: R127, see card-sheet rules)*. It has
>   exactly one destination: at the threshold the jellyfish pays it to play the
>   front of its memory for 0 energy, one card per turn. **No card prints a
>   Charge price and no card reads the bank proportionally** — the firewall R80
>   built against Regent-Stars convergence moves from "never spent" to "spent one
>   way, by the kit, on tempo and never on magnitude." The engine is kit-level
>   (relic + starter), never draft-gated; the relic holds only bookkeeping, all
>   payoff magnitude lives in cards. (kokomi §0, §2.1; R80 amended; R16)

**(ii) `docs/kokomi-cards.yaml`, the R80 standing-law header block.**

Old, verbatim:

> `# R80 (STANDING LAW, healing-law register — Neap Tide v2.1): CHARGE IS NEVER SPENT. Read or thresholded, never`
> `#   expended. Not a current implementation detail to be revisited: it is the structural firewall against`
> `#   Regent-Stars convergence, and it is what every scaling number on this sheet was measured against. A bank`
> `#   that can be spent is a different resource wearing the same name, and every per-point read here would be`
> `#   describing a curve that no longer exists. Already true on both sides by construction — ChargeResource.Spend`
> `#   is a documented no-op and tier0 has no spend_charge — and recorded so it stays that way.`

R80's own warning is the correct description of what this proposal does:
**"a bank that can be spent is a different resource wearing the same name, and
every per-point read here would be describing a curve that no longer exists."**
That sentence is why §4's reader list exists and why every number below is
marked re-derive rather than kept. The replacement block states the new rule,
names the one door (the kit's threshold fire), and keeps the anti-convergence
clause explicitly: no card prints a Charge cost, so no Encore-shaped face can
enter her pool by precedent.

**(iii) The rotation law**, same LAW section, gains one clause: *a Companion
card is not one of her cards for Charge accrual.* The existing sentence — "A
Status or a Curse is never one of her cards" — is the shape to extend.

**(iv) The starting relic, `PearlOfWisdomRelic`.** Shipped printed text,
verbatim:

> "Whenever a card is [gold]Exhausted[/gold], gain 1 [gold]Charge[/gold] and N
> Burst Energy."

Proposed:

> "Whenever one of your own cards is [gold]Exhausted[/gold], gain 1
> [gold]Charge[/gold] and N Burst Energy. Companions do not pay Charge."

The second sentence is the R216 D subsidy being removed **on the face**, which
is where it has to be visible for D4. The numbers do not move; the funnel
narrows. Note the shipped implementation detail that makes this cheap: the relic
*"has no hook of its own"* — the accrual lives in `KokomiResourceHooks
.AfterCardExhausted`, gated on character identity — so the relic edit is text
and the mechanism edit is one predicate.

### Every reader row in the sheet, and what I propose for each

A **reader** is a row whose number is computed from the bank. Every one of them
was sized against a bank that only rises. Against a bank that drains by T on a
schedule, none of their curves survive as written.

| id | printed effect today | proposal |
|---|---|---|
| `all_streams_flow` (uncommon, 1) | Deal 5 damage, **+1 per 2 Charge** | **Re-author.** It was authored as *"the sub-Rare reader"* precisely to put a proportional read on curve. Under the new rule there are no proportional reads; the row's job — a repeatable single-target attack that grows with the engine — is best served by reading the **queue** rather than the bank. Text and number TBD. |
| `read_the_current` (uncommon, 1) | Deal 7; **if Charge ≥ 10**, deal 6 more | **Retire the threshold, keep the card.** A second Charge bar competing with the jellyfish's own bar is the one thing that makes the new meter unreadable — the strip shows one target and one number. Re-author the conditional onto a predicate that is not the bank. |
| `nereids_ascension` (rare, 2) | Deal 12 to ALL, **+1 per 2 Charge**, Exhaust | **Re-author.** This is Shape A, the §2.2 finisher, and it is the biggest proportional read on the sheet; at a banked 20 it is 20-to-all. It cannot survive a draining bank as arithmetic, and it should not: "the finisher is a number you waited for" is the pattern being removed. Its canon link (casting it refreshes a fielded Bake-Kurage) becomes the interesting half now that the jellyfish is persistent. |
| `gyorin_formation` (rare, 2) | Gain 6 Block **+1 per 2 Charge**, and 6 Block at the start of your next turn | **Re-author.** Its own comment names the problem out loud: it is Block *"on a character whose Charge bank fills every time she rotates a card off and is NEVER SPENT (R80)."* That premise is gone. |
| `ceremonial_garment` (rare, kit Burst, cost 0) | Enter the state for `CEREMONIAL_GARMENT_TURNS` (3); her attacks read Charge at `GARMENT_CHARGE_DIVISOR` (2) while it holds | **Re-derive, and it is the hardest one.** It is kit, granted on a full Burst meter, so it cannot simply retire. Its natural new job is to act on the *clock* rather than the magnitude — the Burst making the jellyfish fire faster or more than once while it holds. Exact shape and number TBD-by-sim; it is the one row where "re-author" is a design question of its own. |
| `before_sun_and_moon` (common, power) | +1 to the Kurage pulse **multiplier**, stacking | **Retires with the multiplier.** Its sole effect is `kurage_amp`, and `kurage_amp`'s sole effect is `KURAGE_PULSE_PER_CHARGE + amp`. When the per-Charge term goes, the card has no body. The slot is free for the pulse-side card the new design wants (something that acts on T, on the queue, or on the pulse's type branch). |
| the pulse itself (`bake_kurage`'s engine, not a row) | `4 + Charge × 3` per turn-end, Hydro, plus `kurage_ward` Block | **Re-derived above:** flat 4 (shipped) or 5 Block (shipped) or PICK C, keyed to the last card's type; no Charge term. |
| `tighten_the_cords` (common, 1) | Block 5; **if the exhaust pile ≥ 3**, gain Metallicize 1 | **Unaffected.** It reads the exhaust pile, not the bank — and the sheet already says so explicitly ("an exhaust-pile bar is not a Charge bar"). |

**The granters** — `bake_kurage`, `ritual_purification`, `pulsing_current`,
`pearl_diver`, `mass_mobilization`, `shell_of_sanctuary`, `open_the_stores`,
`grand_conscription`, `prayer_to_the_moon`, `all_hands` — all keep their printed
`gain_charge` lines in kind. Their **magnitudes** are a single re-derivation
question against T rather than ten separate ones: under the shipped rule a
Charge point was worth a slice of a multiplier forever; under the new one it is
worth a fraction of one free card, once. `prayer_to_the_moon`'s 7 (8 with the
funnel) is the row to derive T against, because at a T of 5 it is more than one
whole fire on one card — which may be correct for a rare, and may not.

### Muster's Charge line

R216 D — deferred rather than settled by slice 2 — is **settled by this
proposal, in the direction of removal**: a Mustered Companion costs 1 less and
Exhausts, and pays **no** Charge. Muster's compensation is that the Companion
you play is the Companion the jellyfish will replay for free. That is a strictly
more interesting subsidy than a Charge tick, and it is the answer to
"Companions are boring bodies": what you Muster is now a decision with a second
consequence.

### The slice-2 arms

All four prototype rows on `docs/prototype-surface.yaml` (arms 1–4: Sounding
Line, Fathom the Tide, Twin Tides, Watatsumi Levy) **retire under the surface's
own deletion rule** if this proposal is taken. Every one of them prices or banks
Charge as a card-printed cost, and the new rule forbids exactly that. The two
ADVANCE verdicts stand as recorded evidence about the *question*; they were
never approvals, and their whole-fight gate never ran. The round-2 boards
drafted on `kokomi-slice-2-round-2` retire with them.

**What survives from slice 2 and is worth keeping**: the engine machinery — a
real `spend_charge` on `spend_spark`'s rail in both engines, `ChargeResource
.Spend` reached through one named door, `combat.charge_cost` / `IsPlayable`, and
the Charge hover keyword (`KokomiRiderTips.ForCharge`, attached by op) — is
directly reusable, because the kit's threshold fire is a spend. That is most of
the plumbing this design needs, already built and already quarantined.

### The pilot's Charge valuation — M49

`PILOT_GARMENT_CHARGE_VALUE = 1.2` per turn per banked-Charge read and
`PILOT_GARMENT_BASE_VALUE = 2.0` price the bank as *a multiplier the pilot is
holding*. Under this design a banked Charge is worth a fraction of a free card
play, with a hard per-turn cap on realising it — a completely different term
with a completely different shape. **M49 as written is superseded**: the pick it
asks (build the hold-versus-spend term, or keep reading Charge turns with the
caveat) is about a currency the player spends at a moment of their choosing, and
here they never do. What the pilot needs instead is a *tempo* term, and that is
a new derivation, not the one M49 has queued.

---

## 5. The picks — numbered, [USER]'s

Recommendation first on each, then why in one sentence.

### PICK A — the fuel source

1. **Exhausts only, of her own non-Companion cards. ← recommended.** It keeps
   the shipped funnel (`CHARGE_PER_EXHAUST = 1`) and the kickoff's own decision
   loop — the deck is her second HP bar, and every card burned is Charge — so
   the redesign changes what Charge *does* without changing what pays for it.
2. Play or Exhaust of her own non-Companion cards. Fires far more often, makes
   the queue the dominant engine rather than a payoff, and severs the
   deck-as-resource identity that Law 4's deck-size grammar exists to protect.

### PICK B — the threshold timing

1. **Start of her turn. ← recommended.** The free card lands *before* she acts,
   so it changes the turn she is planning rather than tacking a bonus onto a
   turn already spent; it is also the only timing under which the strip's
   "this will fire" indicator is a forecast the player can plan against.
2. End of turn, with the pulse. One jellyfish moment instead of two and simpler
   to read, but the free card arrives after every decision it could have
   informed — which is a D2 problem, not a taste one.

### PICK C — the Power pulse

1. **Hydro application. ← recommended.** It is the only branch that pays in
   *set-up* rather than in a number, it is already shipped behaviour on the
   damage pulse (so it is a re-use, not an invention), and the blind tester
   found the reaction lane unprompted — *"Hydro sets up reactions with Electro
   companions or Raiden."*
2. Refresh or extend the jellyfish. Circular now that the summon is persistent,
   and it makes Powers the branch that does nothing visible.
3. Draw. Clean and strong, but it puts card velocity on an automatic engine the
   player does not steer, which is the exact D2 shape the redesign is removing.

### PICK D — the empty queue at threshold

1. **Nothing fires; the bank holds and keeps growing. ← recommended.** It makes
   an empty queue a *cost you can feel* — you over-invested in Kokomi's own
   cards and had no Companion banked — and the surplus is not lost, so the
   punishment is tempo rather than deletion.
2. The pulse fires twice instead. Softer and never a wasted turn, but it
   restores exactly the thing being removed: a bank that pays damage on its own
   with nothing in the queue.

### PICK E — targeting for an auto-played attack

1. **The enemy Kokomi's own last attack hit; if that enemy is dead or she has
   attacked nobody, the enemy with the most current HP. ← recommended.** The
   jellyfish follows her lead, which makes targeting a thing the player steers
   through their own play (D2 names targeting explicitly) and is deterministic
   enough for the strip to *show* the target before it fires.
2. Random among living enemies. Matches the shipped pulse's behaviour and needs
   no new rule, but an automatic action with a random target is unforecastable —
   a D4 problem on a design whose whole defence is legibility.
3. Player picks at fire time. Maximum control, and it is the selector step
   [USER] rejected — an interrupt at the start of every threshold turn.

**One interaction to note between B and E**: under B1 (start of turn) "her last
attack" means *last turn's*. That is still forecastable — the strip can show it
all through the previous turn — but if you take B2 (end of turn) then E1 reads
within the same turn and gets sharper. B2 + E1 is a coherent pair; I still
recommend B1 + E1 because the free card arriving before the turn is the larger
gain.

---

## 6. How it is tested

### The prototype arm

**A rule prototype behind a quarantine flag in BOTH engines.** This is a rule
change, not a card, so the prototype surface's card-row grammar is not the whole
door — but the principle is the same one R213 B set and R215 B enforces: the
quarantined surface exists to be *played*, not measured, and **no number taken
off this arm is quotable anywhere** except the decision-closeness falsifier,
which reads the turn and not the row.

**Flag name: `KURAGE_MEMORY`.** Default **off**, and with it off **not one byte
of shipped behaviour changes** — that is the acceptance condition on the flag
itself, checked by running the existing suite unflagged and expecting zero
diffs.

- **tier0** — `tier0/constants.py` (the flag, `KURAGE_MEMORY_THRESHOLD`, the
  pulse-by-type table); `tier0/engine/state.py` (the queue field beside the
  Charge field, ~line 580); `tier0/engine/effects.py` (`_op_summon_kurage`
  ~3417, the turn-end pulse block ~4136, `_op_conscript` ~3435 for the Companion
  accrual predicate); `tier0/engine/combat.py` (the turn-start fire, beside the
  existing turn-end trigger comment ~858); `tier0/engine/relics.py`
  (`tamakushi_casket`'s funnel predicate); `tier0/engine/resources.py`
  (`note_charge_read`'s source tags — `kurage_pulse` and `garment` stop being
  reads).
- **C#** — `klee-mod/KleeCode/Powers/KokomiResources.cs` (the funnel predicate;
  `SpendCharge` is already built and is the fire's mechanism);
  `Powers/KuragePowers.cs` (`KurageSummonPower.FirePulse` and the persistent
  summon, a new queue power beside it); `Kokomi.cs` (turn-start hook);
  `Cards/Kokomi/Generated/BakeKurage.cs` (regenerated); `Vfx/GaugeBridge.cs`
  (the Charge spec gains a `VisualSpan` / `LabelMax` — it is currently the one
  gauge with neither) and a new strip bridge beside it; `Cards/KokomiRiderTips.cs`
  (the Charge tip's body now has a threshold to quote).
- **The bridge** — `vendor/STS2_MCP/McpMod.StateBuilder.cs` (the queue on the
  combat state, reusing `BuildCardInfo`) and `vendor/STS2_MCP/gits/GitsResources.cs`
  (threshold/maximum on the resource snapshot). **A bridge change is a pin
  move**, per `EB-181`'s own gate, and this proposal should ride that row rather
  than open a second one.

### The route through the funnel

1. A `+proto` **dev build** (`dotnet build -p:PrototypeCards=true`) with
   `KURAGE_MEMORY` on.
2. **Sealed whole-fight blind play** through `EB-188`'s door — the `--arm`
   flag or the dev grant that puts a named arm into the starting deck. This is
   the first arm for which whole-fight play is not optional: **a per-turn clock
   and a queue cannot be read on a staged turn at all.** Slice 2 said the same
   thing about a resetting bank; it is doubly true of a queue that has to be
   filled before it can fire.
3. The seat's read against **D2** (is the queue a decision the player steers, or
   a conveyor she watches) and **D4** (could the tester see what was about to
   fire, before it fired).

### What the record must show

Everything `review/qa/blindplay/<session>/record.md` already carries — model,
codex version, the mod build and game build each read off disk and labelled with
the file, the run seed read back off the wire, prompt sha256, action count,
termination reason, the tester's records verbatim under R217 G — **plus** three
things specific to this arm:

- the arm was actually reached, named (the `EB-188` acceptance clause);
- the flag state and the value of T the build carried;
- and, for the D4 read, at least one turn where the tester **stated in advance**
  what the jellyfish was about to play. If no transcript contains that sentence,
  the legibility claim is unevidenced regardless of how the fights went.

The author's own model family is refused as tester (R217 C), and `EB-190`'s
`authored_by:` rule applies: this design is `claude`, and a seat that supplies
any part of it adds its family to the row and disqualifies itself from grading
it.

### Honest engineering estimate, by piece

Sittings, not hours, and each assumes the picks are settled first.

| piece | estimate | why |
|---|---|---|
| tier0 rule arm | **1–2 sittings** | The queue is a new list on the state and one turn-start hook; the pulse rewrite is a branch on last-card-type. The spend path exists. |
| C# rule arm | **2–3 sittings** | Harder than tier0 every time: the turn-start ordering is decompile-settled ground, the persistent summon changes a power's stack grammar, and the parity vectors have to move with it. |
| the UI strip | **2–4 sittings, and the widest error bar in the table** | `GaugeBridge` can host the bar (its spec already has `VisualSpan`/`LabelMax` and Charge is the one tenant that sets neither), but a strip of live card miniatures anchored to a creature is new scene work, not a gauge, and nothing in the mod does it today. |
| bridge fields | **~1 sitting** | Three additive fields on shapes that exist; the cost is the **pin move**, not the code. |
| sim numbers (T, the granters, the re-derived rows) | **2–3 sittings** | Only after the arm runs; every number here is TBD-by-sim by construction, and the re-derived reader rows land as a batch under a `CONSTANTS_VERSION` bump. |
| the sheet re-authoring (§4's table) | **not estimated** | Six rows to re-author is a design pass, and it is gated on this proposal being accepted at all. |

**Total, to a playable blind arm: roughly 6–10 sittings**, of which the UI strip
is the piece most likely to be wrong.

---

## 7. The doctrine seat's read

*Pending — the seat runs on this document as committed, under the clause-only
protocol (`docs/current/OPERATIONS.md`, "Doctrine seat protocol"). Its reply
lands verbatim at
`review/qa/kokomi-kurage-memory-doctrine-review-codex-gpt-5.6-sol.md` and is
quoted here, with the list of clauses it says must move.*

---

## 8. Revert

Branch `kokomi-kurage-memory`, from `origin/process-review-2026-08-29` at
`e352db4`. Three commits, all under `review/`: the proposal, the seat's reply
verbatim, and this file's §7 and §9. `git revert` of the range, or simply not
merging the branch, restores the tree exactly — **no shipped row, constant,
sheet, engine file or LAW line is touched by any of them.**

Nothing here changes until [USER] amends LAW. R80 and the relic text are the two
amendments this design needs, and both are [USER]'s alone: the delegation ladder
puts LAW amendments, one-way doors and picks between genuinely different design
directions on his side of the line, and this is all three.



############################################################################
## LAW.md -- Character identity: Kokomi
############################################################################

## Character identity — Kokomi

- **No self-damage anywhere** in her kit or personal pool (extends to shared-pool
  errata); her risk axis is tempo and card economy only. (Law 1)
- **No healing exception:** the conjunctive healing law stands unmodified for
  her; her healer fantasy is Block, Charge, and prevention — no healing
  amendment, ever. (Law 2; R52 ask 1)
- **Flawless Strategy: Kokomi cannot gain Strength** — any Strength she would
  gain becomes Charge. (Law 3)
- **Deck-size grammar:** in her personal pool, Common cards never increase deck
  size (net delta ≤ 0); only Uncommon/Rare may create cards. Machine-checked;
  her personal pool only. (Law 4)
- **Charge is never spent** — uncapped, read but never consumed, card-event-driven
  with no passive accrual *(Ancient carve-out: R127, see card-sheet rules)*.
  The engine is kit-level (relic + starter), never
  draft-gated; the relic holds only bookkeeping, all payoff magnitude lives in
  cards. (kokomi §0, §2.1; R80; R16)
- **Elite pair A2 Scaling + A6 Utility;** acceptance signature is HP-trajectory
  flatness (the stability band); ward prevention stays reported telemetry, never
  axis-credited. Canonical archetypes: priest / commander / assist (+ generic).
  (R51; R66)
- **Rotation law: Kokomi only Exhausts her own cards.** A Status or a Curse is
  never one of her cards: Muster and every chosen-Exhaust card never select
  one, and no Charge (or Burst particle) accrues from a Status/Curse exhaust
  by any route. Discard is unchanged. An explicit `filter:` on a card is the
  opt-in (Dodge Roll's shape); a dedicated Uncommon/Rare that can eat those
  types is reserved future design space. ([USER] 2026-08-23)
- **VOICE LAW: Exhaust is rotation, never sacrifice.** Weak/Vulnerable enter her
  pool only as riders on exhaust/Sly engine pieces. Conscripted companions count
  as self-sourced kit for `SUPPORT_CARRY`; drafted Inazuma-pool cards count
  normally. (R55; R51; R52 ask 7)

## Roster



############################################################################
## LAW.md -- the D1-D9 design charter (R217)
############################################################################

construction: each is a question a reader answers about a card, a package or a
pool, not a number a report computes.

1. **D1 — Character brief before pool construction.** No pool is built before
   its character has a short [USER]-owned brief: the player promise; two or
   three core verbs; one or two recurring tensions; the three archetype loops;
   the bridges among them; the intended weakness; what the starting relic and
   starter deck teach; and the failure modes to avoid, named. A tension
   sentence *summarises* the character — it does not mandate that every card
   serve one mechanic. Zhongli's brief is the entry gate of his deep dive.
2. **D2 — Player-controlled leverage.** Every persistent resource and every
   automatic engine must feed a decision the player can steer: timing,
   targeting, placement, acquisition, conversion, or forgoing. "Watch it rise
   until the number is large" is not a decision. The control must be reachable
   early and reliably — starter kit, starting relic, base system, or the
   ordinary pool — not only through a rare.
3. **D3 — Benefits carry binding prices.** Defence and engine advancement may
   share a card, but not both at full rate without a binding cost: energy or
   tempo, a below-rate half, mutually exclusive outcomes, target or timing
   awkwardness, a card or resource spent, identity position, a future draw or
   deck cost, or the loss of another action. The counterfactual test: remove
   the defence — is what remains still a full-rate play the player already
   wanted? If yes, the defence was a subsidy.
4. **D4 — Visible and live effects.** At the decision point the player can
   perceive and forecast the consequences that matter, through the card, a
   keyword, a persistent UI element or a character rule — not necessarily
   verbatim on every face. Text that cannot bind in the shipped world,
   invisible feeds and misleading calculated displays are defects. A rare
   intentional edge case is not removed for being rare.
5. **D5 — Simple surfaces, deep interactions.** Richness comes from
   interactions — between cards, enemies, energy, draw order, piles, targets
   and future turns — not from clauses on faces. Commons establish the verbs
   and stay concise. Any added line of text must alter a decision.
6. **D6 — Every card has a place.** Each card has one primary decision home:
   acquisition and build; combat (sequencing, targeting, holding, conversion,
   timing); teaching or utility, deliberately plain; or bridge. Plain cards are
   legal and necessary, and a pool of them is not a defect to be edited away.
7. **D7 — Mesh without preassembly.** Each pool carries linear signposts AND
   modular tools. No preassembled deck; no archetype written in a private
   language only its own cards speak; bridges exist so combinations arrive
   unexpectedly. Shared-verb and hook counts describe a pool — they are never
   acceptance bands.
8. **D8 — Distinct play patterns.** Archetypes differ in how turns and drafts
   unfold, not in the label on a bigger number. Damage may stay terminal; the
   route, cadence, constraint, targeting, transformation, control or economy
   must differ. One non-scalar payoff does not rescue an otherwise automatic
   loop.
9. **D9 — Shared layer and starting tutorial.** Companion packages connect to
   both character verbs and universal verbs; not every Companion card needs a
   hook, but every package needs a distinctive identity. The starting relic and
   starter deck introduce the central verbs and one recurring tension from
   fight one, with visible triggers and no invisible feed.

**Provisional through the Klee slice**, then reviewed. **Nothing here is a
numeric band and nothing here gates:** hook share, bridge %, payoff-role %,
scalar-payoff %, random-target %, Powers-per-universal-verb count, plain-card
%, word count and "turns with a named alternative" rate are descriptive only.
No subjective front-matter fields enter card YAML, and there is no waiver
mechanism. Decision closeness (R213 F) remains the only numeric design
falsifier, and it falsifies one way. (R217 — drafted by GPT, sharpened by
Claude, ratified by [USER].)

## Engineering invariants


############################################################################
## LAW.md -- content authoring, card-sheet rules
############################################################################


- **True in-combat healing is Rare-tier AND Exhausts (conjunctive R8 law);**
  below Rare, sustain routes through Block or buffer pools; no 4-star companion
  true-heals (potions and relic-scale trickles exempt). A rider otherwise banned
  is legal only conjunctively — dropping one half is not a "simplification."
  (principles Guardrail 6; R8; R79/B4)
- **No card starts the game with AoE;** AoE must be drafted, never in any
  starter. (R56)
- **Ancient carve-out (R127, 2026-08-07):** an Ancient-rarity card — Dusty
  Tome's single acquisition door, one visible Ancient per roster character —
  may grant per-turn accrual that its owner's resource laws otherwise ban
  (Kokomi's no-passive-accrual Charge; Furina's no-per-turn-Encore trickle).
  A bounded, opt-in, once-per-run power spike is the rarity's design: the one
  door out of the character's central bargain. Scoped to Ancient rarity
  exactly — no other rarity, no relic, and no event may inherit the
  exception. (EB-30q)
- **Strict-domination is scoped to adjacent rarities:** a card must not be a
  strictly-better superset of another at similar weight; two-step gaps are
  informational. Self-damage/discard/spend_encore count as costs; prefer base-StS
  "twist" shapes over pure supersets. (R26/R77)
- **Threshold predicates pay a flat printed bonus once, not proportional reads;**
  charge/meter bars are Uncommon+; thresholds encode base-plus-bonus so the
  always-live half moves on upgrade and the bar cannot drift down (lowering a
  threshold is forbidden). (R58, invoking R1)
- **A meter-reading damage card is tagged `scaling`, and also `frontload` only if
  it deals damage at meter zero.** `sustain` = healing/prevention of your own HP
  only; zero sustain is a legal identity and `sustain` is never linted. (R91 2c,
  2d)
- **≤2 new keywords per character beyond the shared element system;**
  support-protagonists may carry one extra via logged amendment with compensating
  cuts. Muster's definition attaches from the card's OP. (principles Guardrail 5;
  furina §6; R78)
- **Every card carries a per-character `register` field** (shared schema column,
  per-character vocabulary; Focalors register caps at two Rares). **The register
  guides art selection only** — nothing under `tier0/engine` or `tier05` may read
  it, codegen ignores it, and moving a card between registers must never move win
  rate. (R85; R86)
- **Upgraded starters get a distinct name, not a "+" suffix;** display names live
  in the unique-names namespace, reserved names annotated with the owning kind. A
  full-sheet reserved-names lint runs before any C-milestone; the naming/lore
  audit is [USER]-only and eyes-on. (R69; R29d)
- **Distinctness gate (red test):** uniq ≥ 70, maxclu ≤ 5, neardup ≤ 0.40/card;
  `top%`/`vocab` carry no permanent gate; a partial-pool anchor can only loosen a
  threshold, never certify it. (R81)
- **Enchantment support is a minimal per-card rider;** the run-wide enchantment
  subsystem stays outside the parity world. Encore Performance is 0-cost with no
  energy-positive loop; copies inherit printed bounds; kit cards are not legal
  copy targets. `replay_next_companion` / cost-delta accumulators are
  writing-turn-scoped. (R82; R110 X3/X11; R114 FLAG-1/2; R118 Q9)
- **Ancient-tier pool gaps are fixed with real content, never option removal;**
  each character needs one Ancient card, gated by a deploy lint that fails on an
  empty ledger. (klee-mod Ancient ruling)
- **A material card-sheet edit is a world change and lands under a
  `CONSTANTS_VERSION` bump.** *"A card-sheet edit that materially changes the


############################################################################
## kokomi-kickoff-v1.md -- sections 1 through 3 (identity, Charge, finisher, Commander, prevention power, the starting relic, archetypes)
############################################################################

  relic-trickle exemptions. Read it there. This charter takes no exception to
  it; §2's "no healing exception taken" below is the whole of Kokomi's
  disposition. Pointer substituted for the restatement 2026-08-06 (docs diet,
  Track Z / Z-6); no word of the law changed, and the canonical text is
  untouched.
- Volatility/stability axis (standing): Furina = HP volatility, Kokomi = HP
  stability. Element spread accepted (second Hydro).
- SUPPORT_CARRY / enabler-not-carry, control_uptime detector, KNOB_READS law,
  one-variable-per-window discipline, dose/oracle-cells-are-diagnostics
  (R14), reserved-card-names lint, [USER]-only closure of gated items — all
  binding as usual.
- Klee lesson applied: kit-critical mechanics live at kit level, not as
  draftable rares (Burst ~10% acquisition → burst-as-kit ruling). Kokomi's
  Charge engine is therefore kit-level (relic + starter), never draft-gated.
- R16 spirit respected: power in the cards, not the relic. Kokomi's relic
  carries bookkeeping and conversion rules (Charge accrual, Strength
  conversion); all payoff magnitude lives in cards.

## 1. Identity declaration

Sangonomiya Kokomi — Hydro. General and priest of Watatsumi Island.

Identity sentence: Kokomi converts card economy into damage. She pays in
cards, never in HP.

Binding character laws:

1. No self-damage anywhere in her kit or personal pool. Her risk axis is
   tempo and card economy exclusively. The moment a Kokomi card costs HP,
   the Furina boundary blurs. (Extends to shared-pool errata below:
   Shinobu.)
2. No healing exception taken. This thread's healing-amendment output is: no
   amendment. The conjunctive law stands unmodified. Kokomi builds Block and
   Charge, not HP. Her "healer" fantasy is expressed through damage
   prevention, Block, and the fact that the law's Rare+Exhaust heals are
   themselves premium Charge events (§2.1).
3. Flawless Strategy (the Genshin twist): Kokomi cannot gain Strength. Any
   Strength she would gain becomes Charge instead. This is the −100% crit
   trade translated: all damage scaling routes exclusively through the
   priest identity. It is simultaneously the lore wink and the balance
   guardrail — no Strength-stacking on an uncapped-meter finisher, ever.
4. Deck-size grammar (user ruling, this thread): In Kokomi's personal pool,
   Common cards may not increase deck size — they may only reduce it or
   replace themselves (net card delta ≤ 0). Uncommon and Rare may create
   cards (e.g. "2 energy: Exhaust 1, create 2"), priced so that a
   positive-sum engine requires Rare payoffs plus solved draw/energy
   velocity, and is not guaranteed to assemble in any given run. Scope:
   Kokomi's personal pool only (not mod-wide, not companion pools).
   → Lint: lint_kokomi_decksize.py — fail any Common in her pool whose
   effect list nets card-creation > card-consumption. Catch→lint culture:
   this law is machine-checkable, so it ships with a gate, not a convention.

The decision loop (analogue of Furina's "every point held is safety, every
point spent is tempo"):

> Every card kept is engine; every card burned is Charge.

Cycle the engine (discard/Sly/support velocity) or spend the deck down for
Exhaust payoffs. The deck is her second HP bar — defense literally spends
future draws.

## 2. Core systems

### 2.1 Charge (the Bake-Kurage meter)

- Accrual (proposed base rule): Whenever one of your cards is Exhausted,
  gain 1 Charge. Universal across routes — includes Commander-consumed
  conscripts, the law-mandated Exhaust on every legal heal (Qiqi/Sigewinne
  become premium Charge events — the healing law is her enabler, not her
  obstacle), and prevention-power procs. A Status or a Curse is NOT one of
  her cards ([USER] rotation law, 2026-08-23): Muster and chosen Exhaust
  never select one, and a Status/Curse exhaust pays no Charge or Burst
  particle by any route; a card that may eat those types says so with an
  explicit filter, reserved Uncommon/Rare design space.
- Alternative considered: tag-gated accrual ("Consumed" keyword only).
  Rejected in draft for rules-weight; revisit only if sim shows universal
  accrual makes non-priest decks accidentally elite on A2.
- Knob: CHARGE_PER_EXHAUST = 1. Premium cards may grant bonus Charge as
  explicit effect lines (KNOB_READS applies).
- Properties: uncapped; never expended; read (not consumed) by finisher
  effects; card-event-driven only — no per-turn passive accrual.
- Anti-stall argument (pre-registered for the inevitable challenge): Charge
  cannot be stalled into. Accrual events shrink the deck; fuel is finite per
  fight; the Exhaust economy is self-milling and imposes a natural fight
  clock. The genuine risk is not stall but multiplicative finisher reads
  (uncapped meter × repeated reads) — mitigated in §2.2 and by Flawless
  Strategy.

### 2.2 Finisher — two shapes, [USER]-gated choice

- Shape A — Nereid's Ascension as nuke: single large attack reading Charge.
  Rate limits mandatory: Rare, low copy count, Exhaust on the finisher
  itself, cost ≥ 2.
- Shape B — Ceremonial Garment as duration state (recommended): enter a
  transformed state for N turns; her attacks during it read Charge (scaled
  down per hit). Truer to the burst (a stance, not a hit), converts the
  one-shot balance cliff into repeated-but-bounded payoff, and hands the
  animation pipeline a showpiece. Interacts cleanly with Shape-A-style cards
  as the state's capstone if we want both.
- Either shape: finisher magnitude constants are knobs, [USER]-gated at
  first battery.

### 2.3 Commander — conscription

- Transform verb (working keyword: Conscript): transform a card in hand into
  a random Inazuma Companion card; it costs 1 less and gains Exhaust. Pays
  card identity; feeds Charge on consumption.
- Discard verb: discard-based generation and Sly triggers — pays tempo,
  synergizes with the Assist lane. Two distinct costs give the archetype
  internal texture (spark/demolition precedent).
- Differentiation from Furina (on record): Furina's companion grammar is
  additive and empowering (Guest Stars from outside the deck; Spotlight
  makes them the payoff). Kokomi's is transformative and consumptive
  (conscripts existing cards, burns them as fuel; the payoff routes through
  her own finisher). Kokomi does not get a Guest Star mechanic.

### 2.4 Damage-prevention power (the "healing" slot)

Sample (user, this thread): "If an attack would inflict damage, Exhaust a
random card from your draw pile" — prevention priced in future draws.

- Draft shape: Rare power, procs limited (first unblocked hit per turn),
  prevention magnitude a knob. Rationale: prevention + positive-sum engine
  is an invincibility loop; the deck-size grammar breaks the loop
  structurally at Common, and the rate limit + Rare gating breaks it at the
  power. Both guards ship; neither alone is trusted.
- Each proc is an Exhaust event → Charge. Getting attacked fuels the
  finisher. This is the stability identity as mechanic: her HP bar doesn't
  move; her deck does.

### 2.5 Starting relic (working name: Tamakushi Casket)

Carries the two conversion laws, no payoff magnitude (R16-compliant):

> Whenever you would gain Strength, gain that much Charge instead.
> Whenever one of your cards is Exhausted, gain 1 Charge.

Charge engine is thereby kit-guaranteed (Klee burst lesson). Name pending
lore/naming audit ([USER]-gated, as always).

## 3. Archetypes (bands declared at battery time, per A3 convention)

- Commander — conscription engine: transform/discard into companion fuel;
  Uncommon+ card creation lives here; the archetype that can attempt the
  (deliberately difficult) engine.
- Priest — Charge scaling and finisher payoff; wants Exhaust density, Rare
  heals as premium Charge, the prevention power.
- Assist — Sly/discard glue: draw and energy velocity, low internal payoff
  by design (Bogglecat Box philosophy: honest glue no archetype warps around).
  Feeds both other lanes.

Elite-axis declaration (proposed, [USER]-gated): A2 Scaling + A4 Utility.
This forces the invariant question: is A1>A2 mod-wide or Klee-scoped? If
mod-wide, it needs a per-identity amendment before any Kokomi battery is
meaningful — she is a declared scaler and will breach by design. Ruling ask
§6.3.


############################################################################
## docs/kokomi-cards.yaml -- her ENTIRE card sheet, header comments included
############################################################################

# Lifecycle: LIVING — expected to change; read it to work on the project. Status index: docs/registry/identifiers.md §15.  (lint-ok)
# Kokomi card pool — v0.2 SHEET PASS (Tier 0 simulator schema). docs/kokomi-kickoff-v1.md governs; every kickoff
# gate is CLOSED (R51 elite axes + debuff texture, R52 batch closure — 2026-07-24). EVERY number remains PROPOSED;
# v0.4 LORE OVERLAY (2026-07-26): the naming audit ran; the names below are [USER]-ruled, not placeholders.
# WIKI-VERIFIED canon names (re-verified against the Genshin wiki this pass — the wiki is the instrument, not
#   anyone's memory): Kurage's Oath (Elemental Skill, which summons the Bake-Kurage), Bake-Kurage,
#   Nereid's Ascension (Elemental Burst), Ceremonial Garment (the state it dons), Tamakushi Casket (1st Ascension
#   passive: casting Nereid's Ascension REFRESHES a fielded Bake-Kurage — the link this sheet now models),
#   Song of Pearls (4th Ascension passive), Princess of Watatsumi (innate passive), and the constellations
#   C1 At Water's Edge / C5 All Streams Flow to the Sea / C6 Sango Isshin.
# CORRECTION: the previous header listed "The Moon's Beauty" as verified. It is NOT a Kokomi name and did not
#   corroborate — struck. The real Moon constellations are C3 "The Moon, A Ship O'er the Seas" and C4 "The Moon
#   Overlooks the Waters". (Beware beta-era sources: they carry "Kaijin Ceremony" for the Burst and "Haworthia
#   Casket" for the A1 passive. Both are pre-release names; the release names are the ones above.)
# EVERY number remains PROPOSED. Names not in the verified list are authored flavor, now ruled.
# B2 / G3 (FLAVOR-TEXT CONVENTION, Neap Tide v2.1): flavor text is VISUALLY SEGREGATED from rules text where the
#   card's text budget allows, and OMITTED entirely when the card is at budget. Rules text never competes with
#   flavor for the same line — a player reading a card to decide a turn must never have to parse which half is
#   binding. STATUS: currently vacuous, and said so rather than left to look implemented. No card in this repo
#   carries flavor text; there is no `flavor` field on the sheet and no renderer for one. This is the rule that
#   governs the moment one is added, recorded now because R78 just freed a large amount of face budget on nine
#   cards and "there is room now" is exactly when the convention gets decided by accident.
# VOICE LAW (v0.4 §3): Exhaust in her fiction is ROTATION, never sacrifice. Units rotate off the field rested and
#   whole; Charge is the strategic position each executed maneuver buys. Her doctrine is minimal casualties — the
#   sacrifice voice is the one reading that breaks the character. tactical_recall is the exemplar; the old
#   grand_conscription line ("the army becomes fuel") was the marked counter-example and is fixed below.
#   Forced service is Shogunate behaviour and the resistance were volunteers, so the display family is
#   Muster/Enlist/Rally; the internal op name `conscript` stays.
# Identity (kickoff §1): Kokomi converts card economy into damage. She pays in cards, never in HP.
#   LAW 1: no self-damage anywhere in this pool (grep-clean: no {target: self} damage op may ever appear here).
#   LAW 2 (R52, ask 1): NO heals in this pool, period. No amendment taken and NONE PLANNED — Furina holds the mod's
#          one healing amendment; Kokomi's rares pay off a different way. The conjunctive mod law (Rare AND
#          Exhaust) stands, but she takes ZERO slots under it: the healer heals no HP. Her sustain fantasy is
#          prevention (the ward) + the stability band. sango_prayer's v0.1 heal is GONE (reworked below).
#   LAW 3 (Flawless Strategy): she cannot gain Strength (engine converts to Charge at the apply_power chokepoint);
#          this sheet accordingly designs NO strength-granting cards.
#   LAW 4 (deck-size grammar, user-authored): Commons net card delta <= 0 (reduce or replace, never create).
#          Machine-checked by tools/lint_kokomi_decksize.py (in-suite). Uncommon+ may create (reinforcements).
#   LAW 5 (R79/G7, verb partition — Neap Tide v2.1): Discard/Sly holds the MONOPOLY on card/energy economy
#          riders (draw, energy, cycling, selection). Exhaust cards may carry riders — Block and other
#          identity/defense riders are explicitly legal — but an economy rider on an exhaust card is legal
#          ONLY as a deliberate one-time velocity piece: RARE **AND** self-Exhaust.
#          Template: "Gain 1 (2) energy, draw 1 (2), exhaust 2. Exhaust."  (moonlit_offering was the sheet's one
#          instance; swift_currents was merged into it at G8 rather than promoted alongside it.)
#          TWO INSTANCES AS OF EB-69 (R198, [USER] 2026-08-23), and the second is a DELIBERATE YES, not a
#          discovery: `the_gunbai_turns` is Rare AND self-Exhaust and carries a chosen `discard`, which is
#          selection, which LAW 5's monopoly list names. It is therefore LEGAL under the conjunctive shape
#          below, and the defect was that this header claimed exactly one instance while the fill added a
#          second. The header now says two. B4's point stands unchanged: the PAIR (Rare AND self-Exhaust)
#          is what makes each of them a one-time purchase, and a third instance is a fresh [USER] act, not
#          a precedent this line has granted.
#   B4 — THE CONJUNCTIVE SHAPE, stated once for BOTH laws that use it. LAW 2 admits a heal only at Rare AND
#          Exhaust; LAW 5 admits an economy rider only at Rare AND self-Exhaust. In both cases the PAIR is the
#          point: either half alone is exactly the shape the law exists to prevent — a Rare that heals is a
#          payoff, an Exhaust card that draws is an engine — and it is the conjunction that makes the effect a
#          one-time purchase instead of a repeatable one. A future pass that "simplifies" either law to a single
#          condition has not simplified it; it has repealed it. Kokomi takes ZERO slots under LAW 2 (the healer
#          heals no HP) and exactly TWO under LAW 5 (moonlit_offering, the_gunbai_turns) -- see the LAW 5
#          note above for why the second is a deliberate yes.
#   LAW 6 (rotation law, [USER] 2026-08-23): Kokomi only Exhausts HER OWN cards. A Status or a Curse is never
#          one of her cards: Muster and every chosen-Exhaust card never select one, and NO Charge (or Burst
#          particle) accrues from a Status/Curse exhaust by any route. Discard is unchanged. A card that may
#          eat those types says so on its face with an explicit filter (Dodge Roll's shape) — a dedicated
#          Uncommon/Rare junk-eater is reserved future design space, and no card on this sheet is one.
# Element: hydro | Cadence: CATALYST (RULED R52, ask N1): every attack applies hydro — the pool's co-op/reaction
#   voice, and the structural third of elite A6 (application uptime comes from the cadence, not authored lines).
# Archetypes (kickoff §3): commander (conscription engine) | priest (Charge/exhaust density) | assist (Sly/discard
#   glue, LOW INTERNAL PAYOFF BY DESIGN — Bogglecat Box philosophy) | generic.
# Statline this sheet targets (R51): A1 weak ~1.5-2, A2 ELITE, A6 ELITE (the ruled second axis — Weak/Vulnerable
#   ONLY as riders on exhaust/Sly engine pieces, never a spammable cheap AoE debuff like Furina's commanding_gaze;
#   uncommon-gated so no such shape exists at common), A4 LOW BY DESIGN (the stability band owns the healer
#   fantasy in the act sims), A7 mid (engine assembly tax).
# R80 (STANDING LAW, healing-law register — Neap Tide v2.1): CHARGE IS NEVER SPENT. Read or thresholded, never
#   expended. Not a current implementation detail to be revisited: it is the structural firewall against
#   Regent-Stars convergence, and it is what every scaling number on this sheet was measured against. A bank
#   that can be spent is a different resource wearing the same name, and every per-point read here would be
#   describing a curve that no longer exists. Already true on both sides by construction — ChargeResource.Spend
#   is a documented no-op and tier0 has no spend_charge — and recorded so it stays that way.
# Charge grammar: the universal exhaust->Charge accrual lives on the relic (engine funnel), NEVER as card text;
#   gain_charge lines here are the §2.1 "premium" bonuses on top. Charge is read, never spent — readers are
#   rate-limited per §2.2 (Rare / Exhaust / cost >= 2 on the nuke; the garment state is the kit).
#
# ============================ v0.5 PARTIAL FILL (2026-07-25) ============================
# WHY THIS BLOCK EXISTS. [USER] sanity-checked the pool against the shipped rosters and found it half-sized:
#   Kokomi 38 personal cards against Klee 76 and Furina 78, short at EVERY rarity (common 13 vs ~32,
#   uncommon 12 vs 25, rare 8 vs 15). Nothing regressed — the sheet has been 38 rows since the v0.2 pass and
#   every R56/R57 number was measured against it — but a thin pool is felt by a HUMAN in a way the run sim
#   does not report: fewer distinct options per draft screen, more forced picks, and a novelty budget that
#   runs out well before act 3. That would contaminate every other answer the playtest protocol is asking for.
# RULING ([USER], this sprint): fill PARTWAY with cards that make logical sense, and carry the remaining gap
#   forward as an explicit design pass AFTER the early playtest results. This block is that partial fill:
#   +12 common (13 -> 25) and +8 uncommon (12 -> 20). RARES ARE DELIBERATELY UNTOUCHED at 8 — draft variety
#   is felt hardest where the offers actually come from, and rares are the slot most likely to be redesigned
#   once play tells us which of her lanes is real.
# STILL OPEN after this block, for the post-playtest pass: common 25/~32, uncommon 20/25, rare 8/15 — call it
#   ~20 cards short of roster parity. Recorded in DECISIONS (R58) and in the sprint log, not just here.
# FREEZE-RULE STATUS: the sprint's freeze rule ("R56 numbers ship untouched; blocker-class fixes only") is NOT
#   violated and NOT quietly widened. Not one existing row is edited by this block. New rows carry new numbers,
#   which is unavoidable, so this is logged as an explicit [USER]-directed EXCEPTION rather than folded in.
# EVERY NUMBER BELOW IS PROPOSED and every NAME below is AUTHORED, NOT AUDITED. The v0.4 lore overlay ruled the
#   names that existed then; the naming audit is [USER]-only and has not run on this block. Treat these display
#   names as drafts, especially against external collisions (docs/reserved-card-names.txt is the record of a
#   class of bug the repo structurally cannot see).
# GRAMMAR: this block introduces no new verb. Every row is built from ops she already ships — conscript,
#   exhaust_from, gain_charge, summon-adjacent riders, Sly, block_next_turn, cost_mod, copy_companion_in_hand —
#   plus two THRESHOLD predicates (charge_at_least_N, exhaust_pile_at_least_N). A threshold is not a §2.2
#   proportional read: it pays a flat printed bonus once a bar is cleared, so it cannot feed the
#   multiplicative-read risk the per-point readers are rate-limited for. Charge thresholds are UNCOMMON+ only.
# =======================================================================================

# ---------- BASIC (5) ----------
- {id: waters_edge, name: "Water's Edge", cost: 1, type: attack, rarity: basic, solve: [frontload], tempo_band: {fight: [early], run: [early]}, archetypes: [generic], role: glue,
   effects: [{op: damage, amount: 6, target: enemy}]}
   # Her normal attack: a ribbon of water. v0.3 charge-curve pass: 4 -> 6, STRIKE PARITY — and no further.
   # USER RULING (R53, 2026-07-24): the kaboom-parity 7 arm is REJECTED; her basic attack stays at basic-Strike (lint-ok: rejected arm's value, on record)
   # parity. The v0.2 diagnosis stands (sub-Strike basics made act-1 bills unpayable at any scaling setting),
   # but A1-weak lives in the pool's SHAPE and the basics stop at parity. The 7 arm measured ~5 act-1 points (lint-ok: rejected arm + its measurement)
   # above this world (report §6) — that gap is bought elsewhere or not at all.
- {id: coral_guard, name: "Coral Guard", cost: 1, type: skill, rarity: basic, solve: [block], tempo_band: {fight: [early], run: [early]}, archetypes: [generic], role: glue,
   effects: [{op: block, amount: 5}]}
   # Standard Defend. Her distinctive durability comes from the ward/Charge economy, not inflated basics.
- {id: bake_kurage, name: "Bake-Kurage", cost: 1, type: skill, rarity: basic, solve: [block, frontload, scaling], tempo_band: {fight: [early], run: [early]}, archetypes: [generic], role: enabler, tags: [skill_tag],
   effects: [{op: summon_kurage, amount: 1}, {op: gain_charge, amount: 1}]}
   # Signature basic: the jellyfish takes the field — and STAYS there. v0.4 O4 salvage (plan §1.1): the one-shot
   # body is replaced by a persistent summon that holds for KURAGE_DURATION turns and pulses at each turn end
   # for KURAGE_PULSE_BASE + Charge x KURAGE_PULSE_PER_CHARGE damage, hydro application, and KURAGE_PULSE_BLOCK
   # Block. The old body's three lines all survive inside the pulse — application, Block, and the meter — but
   # now they repeat and they SCALE, which is the point: v0.3 bought its act-1 clear by making the BURST a
   # metronome (meter 10), and the ratio instrument correctly read that as frontload. Canon keeps the metronome
   # on the summon, so this is where it goes. Small at Charge 0, real by node 4: an A2 signature carrying the
   # fight-1 survival math that meter 10 was buying. The `amount: 1` mirrors KURAGE_DURATION (test-pinned;
   # the v0.4 starter rework took the duration 3 -> 1, and this row followed it).
   # skill_tag = burst particles. The meter is NAMED for this card (kickoff §2.1).
   # v0.3: +1 Charge — the signature basic TEACHES the meter from fight 1 (the Regent-common lesson: the
   # scaling currency rides on ordinary plays, it is not a separate purchase). Kept verbatim.
- {id: tactical_retreat, name: "Tactical Retreat", cost: 0, type: skill, rarity: basic, solve: [velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [generic], role: enabler,
   effects: [{op: draw, amount: 1}, {op: discard, amount: 1}]}
   # G6 (Neap Tide v2.1): migrates to the SLY-TEACHER basic. Draw 1, discard 1; upgrade draws and discards 2.
   # [USER] VERBATIM INTENT, recorded because the card will read like an engine piece to anyone who meets it
   # cold: this is NOT a true cycling effect. It is a STARTER CARD and must never be tuned into a solo engine
   # piece. If a later pass wants a cycling engine, it authors one; it does not grow this.
   # Gorou keeps the exhaust-teaching role in the starter, so the starter still teaches both verbs -- this one
   # stops being the second exhaust outlet and becomes the first discard one.
   # ACCRUAL SIDE EFFECT, on the record per §5: removing `exhaust_from 1` removes a starter EXHAUST, which is
   # Charge and Burst income (CHARGE_PER_EXHAUST, KOKOMI_BURST_PER_EXHAUST). §5 holds accrual otherwise fixed
   # and names this as its one sanctioned exception; P9 predicts it shows up as an act-1 accrual slowdown and
   # says to suspect THIS before re-touching the multiplier.
   # The exhaust-teacher: pull a unit off the line, turn the page. Net delta -1 (reduces the deck — LAW 4
   # poster child). With the relic this is the decision loop in one basic: every card rotated out is Charge.
   # v0.4 RENAME ([USER]): "Recall" -> "Retreat". A retreat is a maneuver that PRESERVES the unit, which
   # is the voice law exactly — rotation, never sacrifice. The exemplar card now says so on its face.
- {id: tide_reading, name: "Stolen Chapter", cost: 1, type: skill, rarity: basic, solve: [block, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [generic], role: glue,
   effects: [{op: block, amount: 2}, {op: draw, amount: 1}]}
   # Fifth basic (template allows 4-5): the strategist reads the field. Poise + a look ahead.

# ---------- COMMON (12: +surging_shoal at kickoff review) ----------
# Commander (2)
- {id: conscription_notice, name: "Call to Arms", cost: 1, type: skill, rarity: common, solve: [block, frontload, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [commander], role: enabler,
   effects: [{op: conscript, amount: 1}, {op: draw, amount: 1}]}
   # THE Commander verb at common: transform a card in hand into a random Inazuma recruit (costs 1 less, gains
   # Exhaust — kickoff §2.3 grammar verbatim). Net delta 0: transform, never create (LAW 4). Replaces itself.
- {id: to_the_front, name: "To the Front!", cost: 0, type: skill, rarity: common, solve: [block, frontload, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [commander], role: enabler,
   effects: [{op: conscript, amount: 1}]}
   # The free order. Pays only card identity — the archetype's cheapest enable, and its texture: what will
   # the draft pile give you today?
# Priest (4)
- {id: votive_offering, name: "Votive Offering", cost: 1, type: skill, rarity: common, solve: [block, frontload, scaling, utility], tempo_band: {fight: [early], run: [early]}, archetypes: [priest], role: glue,
   effects: [{op: exhaust_from, amount: 1, select: chosen}, {op: block, amount: 5}]}
   # Burn a card for safety: Defend-grade Block whose rider is fuel with the Casket, pure loss without a payoff —
   # the priest lane's honest price.
- {id: ritual_purification, name: "Ritual Purification", cost: 1, type: skill, rarity: common, solve: [block, frontload, scaling, utility, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [priest], role: enabler,
   effects: [{op: exhaust_from, amount: 1, select: chosen}, {op: gain_charge, amount: 4}, {op: draw, amount: 1}]}
   # The premium Charge common (§2.1 explicit-bonus grammar): exhaust 1 -> 5 total Charge (1 funnel + 4 line),
   # replaces itself. The engine's metronome. v0.3: line 2 -> 4 — the benchmark common Forges 7 while dealing 7; (lint-ok: benchmark common's numbers)
   # her dedicated charger paying a card for 3 total was under HALF that on one axis and zero on the other.
- {id: waterspout, name: "Waterspout", cost: 1, type: attack, rarity: common, solve: [frontload], tempo_band: {fight: [early], run: [early]}, archetypes: [priest, generic], role: glue, exhaust: true,
   effects: [{op: damage, amount: 10, target: enemy}]}
   # Self-consuming swing: v0.3 7 -> 10 — a card of the deck-as-HP-bar is a real price and must buy a real hit (lint-ok: v0.3 history)
   # (the v0.2 world priced the burn at +1 damage over a plain swing). One hit, one Charge, one fewer draw.
- {id: cleansing_tide, name: "Cleansing Tide", cost: 2, type: skill, rarity: common, solve: [block, frontload, scaling, utility], tempo_band: {fight: [mid], run: [early]}, archetypes: [priest], role: glue,
   effects: [{op: exhaust_from, amount: 2, select: chosen}, {op: block, amount: 10}]}
   # The big burn: two cards for a real wall. Double fuel with the Casket; steep deck cost without it.
   # (v0.3 considered 12 and REVERTED in the same pass: it strictly dominated shell_of_sanctuary's 11 under (lint-ok: sibling card's number)
   # the exhaust-as-benefit convention, and the act diagnosis proved Block is not her binding constraint —
   # the reprice concentrates on output and meter, not walls.)
# Assist (3)
- {id: undertow_shuffle, name: "Daydream of a Quiet Life", cost: 1, type: skill, rarity: common, solve: [velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [assist], role: glue,
   effects: [{op: draw, amount: 3}, {op: discard, amount: 2}]}
   # Assist's churn: see three, lose two at random — more raw velocity than Communion of Tides but wilder, and it
   # rings the Sly bell TWICE. (First-draft draw-2/discard-1 was a strict-domination lint catch vs Communion —
   # the CCM remedy applied: each card is now a real choice, churn-vs-fuel.)
- {id: moon_signal, name: "A Moment Alone", cost: 0, type: skill, rarity: common, solve: [velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [assist], role: enabler,
   sly: [{op: draw, amount: 1}],
   effects: [{op: discard, amount: 1, select: chosen},
             {op: recall_to_draw, amount: 1}]}
   # RATIFIED REDESIGN (R202, EB-125). The free cycle is now a free REORDER: throw a card you pick, then put a
   # card from your discard pile on top of your draw pile. The draw moved onto the Sly rider, so the cheapest
   # bell in the lane still rings — it just rings when the card is THROWN rather than when it is played.
   # WHY IT MOVED: the old draw-1 body was dominated by several separate uncommons (raise_the_sashimono,
   # sayu_naptime, sucrose_gust), each of which gave the same draw and paid nothing. R200 named the Common's
   # own rate as the defect rather than the newest card that exposed it. `recall_to_draw` is a benefit key none
   # of them carry, which is what clears every one of those pairs — verified WITH and WITHOUT the Sly rider, so
   # the rider is identity, not the mechanism.
   # THE HAND ECONOMY IS DELIBERATELY NEGATIVE: you lose the card you play AND the card you throw, and nothing
   # arrives in hand. That is the property the upgrade must not flatten, and it is why the upgrade buys Retain
   # instead of a draw (kokomi-upgrades.yaml).
   # KNOWN CONSEQUENCE, recorded rather than discovered: the discard branch of `recall_to_draw` is UNFILTERED
   # (the D3 self-recall contract, R198), so on an otherwise empty discard pile the card you just threw is the
   # only candidate and comes straight back to the top of your draw pile. `_best_card` prefers a real Attack,
   # so that line is a fallback, not the rule.
   # Recursion-at-common was the standing objection (the fill put recall at uncommon on purpose). The answer is
   # that this is a SWAP, not an engine: the discard pays for the recall in the same breath and the hand is down
   # two cards to move one card's position.
- {id: drifting_lantern, name: "Drifting Lantern", cost: 1, type: skill, rarity: common, solve: [block], tempo_band: {fight: [early], run: [early]}, archetypes: [assist, generic], role: glue,
   sly: [{op: block, amount: 4}],
   effects: [{op: block, amount: 4}]}
   # THE Sly teaching card: 4 Block played, 4 Block when a card effect discards it — the lantern shines either
   # way. First sly row on any sheet (engine: card-effect discards only; the hand flush pays nothing).
# Generic (3)
- {id: surging_shoal, name: "Surging Shoal", cost: 1, type: attack, rarity: common, solve: [frontload], tempo_band: {fight: [early], run: [early]}, archetypes: [generic, priest], role: glue,
   effects: [{op: damage, amount: 6, target: all_enemies}]}
   # R77 (Neap Tide v2.1): 7 -> 6 (upgrade 8), predicated on the B1 Skittish errata below. (lint-ok: supersession record + upgrade value)
   # B1 SKITTISH ERRATA. The v0.3 note this replaces said Skittish 6 "ZEROED the 4-damage version". That is
   # not what the mechanic does. tier0 `deal_damage_to_enemy` adds the Block AFTER the whole hit resolves,
   # with the engine comment "so the triggering attack is never mitigated by it", and act1_pool's own line
   # reads "first hit/turn: +6 Block after". A 4-damage hit landed in FULL; what Skittish 6 did was put 6
   # Block up against the NEXT hit that turn. The v0.3 repricing was therefore argued from a misread of the
   # rule, even though the direction it chose may still have been right for other reasons.
   # WHAT IT ACTUALLY GATES, and this is a live consideration rather than a settled one: against Gardener x4
   # the FIRST AoE each turn always lands full, and a SECOND AoE that turn does (dmg - 6) per body. At 7 that (lint-ok: worked arithmetic at the superseded value)
   # second wave did 1; at 6 it does 0; upgraded to 8 it does 2. So R77 buys a cleaner number at the cost of (lint-ok: upgrade value in worked arithmetic)
   # making the double-AoE turn strictly dead against this one elite. FLAGGED for the E2 read -- it was not
   # part of the errata as ratified, and if the act-1 AoE lane reads weak this line is the first suspect.
   # THE GARDENER-LESSON CARD (Furina 3-act diagnosis §10.8.2: a starter/common pool with no cheap AoE dies to the
   # act-1 AoE wall regardless of assembled-deck quality; standing_room_only is the ratified precedent). Added at
   # kickoff REVIEW after the first battery — deliberately NOT in any measured package, so the v0.1 battery numbers
   # stand unlabeled; packaging it is sheet-pass material. Catalyst cadence makes this mass hydro application —
   # but NOT a convergence-cell member: M12(a) RULED 2026-08-10 (R147) that the cell is
   # TWO -- {rain_of_roses, guest_neuvillette_judgment} -- and undercurrent/standing_room_only both departed. PROPOSED.
- {id: jade_bulwark, name: "Pearl Bulwark", cost: 1, type: skill, rarity: common, solve: [block], tempo_band: {fight: [early], run: [early]}, archetypes: [generic], role: glue,
   effects: [{op: block, amount: 6}]}
   # Graceful Retreat parity exactly (6 at common, under Klee's Hide and Seek) — the stability character does NOT
   # get a hidden block subsidy; her edge is the ward and the buffer of future draws. (lint-ok: Furina comp)
- {id: pulsing_current, name: "Pulsing Current", cost: 1, type: attack, rarity: common, solve: [block, frontload, scaling], tempo_band: {fight: [early], run: [early]}, archetypes: [generic, priest], role: glue,
   effects: [{op: damage, amount: 7, target: enemy}, {op: gain_charge, amount: 1}]}
   # v0.3: her Regent-common analogue — deal 7 AND feed the meter 1. The v0.2 stance ("deliberately UNDER
   # Klee's 7") is SUPERSEDED by the charge-curve ruling direction: the scaling currency rides on ordinary
   # damage plays, and the plain swing meets Klee's 7 instead of undercutting it. (lint-ok: Klee comp)

- {id: kurages_oath, name: "Kurage's Oath", cost: 1, type: power, rarity: common, solve: [block, frontload, scaling], tempo_band: {fight: [late], run: [early, late]}, archetypes: [priest, generic], role: payoff,
   effects: [{op: apply_power, power: kurage_ward, amount: 5, target: self}]}
   # v0.4 ([USER]): the jellyfish's canon SECOND job. Bake-Kurage in the game deals Hydro DMG *and heals nearby
   # characters at set intervals* — the pulse ships the damage half baseline, and this power drafts the mending
   # half back in as Block (R52 healing law: her HP bar never moves, the incoming does). While it holds, every
   # Kurage pulse also grants 5 Block (7 upgraded). Priced off the Regent precedent [USER] named: a 2-cost (lint-ok: Regent precedent's number)
   # power paying 13 Block per 2-cost finisher play. Hers triggers off a 1-cost summon, and the summon only (lint-ok: Regent precedent's number)
   # pulses once per play at KURAGE_DURATION 1 — so the honest read is "5 Block per Bake-Kurage", doubled
   # once the summon is upgraded to two turns.
   # COUPLING PIN (playtest sprint P1). This card's value is (ward x pulses per play), and it owns only the
   # first factor. The second lives in KURAGE_DURATION (1) and the bake_kurage `kurage_turns: +1` delta —
   # both outside this row, neither guarded by this card's own tests. Moving either reprices the Oath without
   # touching it. `test_oath_ward_is_pinned_to_the_pulse_frequency_it_was_measured_at` fails if that is
   # attempted silently: re-measure at the new frequency, then move the pin and this note in the same change.
   # THE MEASURED HISTORY, ON THE RECORD. The first draft was 5, priced by ratio off Regent (13 Block off a (lint-ok: ward-bracket measurement)
   # 2-cost finisher, so ~5 off a 1-cost summon). That measured as a TRAP PICK — priest run winrate 5.8% with no (lint-ok: ward-bracket measurement)
   # card at all vs 3.8% with it, i.e. drafting it made her worse. Bracket at 500 runs/plan --realistic: (lint-ok: run count + winrates)
   # ward 5 -> priest 3.8% / commander 5.4%; ward 8 -> 4.8% / 5.8%; ward 12 -> 6.2% / 5.8% (no-card baseline (lint-ok: ward-bracket measurement)
   # 5.8% / 6.0%). That bracket landed 12, and it is why the card shipped at 12. (lint-ok: ward-bracket winrates)
   # R130 OVERRIDES IT TO 5 (7 upgraded), 2026-08-07, on [USER]'s live-playtest read (lint-ok: the upgraded
   # statline, which lives in kokomi-upgrades.yaml): the card stood out in
   # play, and MULTIPLE COPIES turn it into a block solve. That is the stacking failure mode the bracket's
   # instrument never priced — every arm above measured ONE copy in the deck, so the whole table is silent
   # about the shape [USER] saw. A single-copy measurement cannot outrank a multi-copy observation about
   # multi-copy behaviour; the numbers are not wrong, they answered a narrower question. The old trap-pick
   # reading of 5 is now the thing to watch (playtest protocol), not the too-strong reading of 12. (lint-ok: retired number)
   # The [USER] WATCHLIST flag from 2026-07-26 ("I feel like that's too strong, but we can rebalance later")
   # is hereby SPENT: this was the rebalance, and 12 was the first knob back exactly as recorded. (lint-ok: retired number)
   # NAME: "Kurage's Oath" is her actual Elemental Skill (wiki-verified) and was unused
   # by this pool; the oath is that she mends. [USER]-only naming audit as ever.
- {id: before_sun_and_moon, name: "Before Sun and Moon", cost: 1, type: power, rarity: uncommon, solve: [block, frontload, scaling], tempo_band: {fight: [late], run: [late]},
   archetypes: [priest, generic], role: payoff,
   effects: [{op: apply_power, power: kurage_amp, amount: 1, target: self}]}
   # R73 (Neap Tide v2.1). SOLE EFFECT: +1 to the Kurage pulse MULTIPLIER. The one sanctioned way back up
   # from R73's cut of KURAGE_PULSE_PER_CHARGE (4 -> 3), and deliberately a DRAFT cost rather than a free
   # baseline: the cut lowered what everyone gets, this sells the slope back to decks that commit a card slot.
   # STACKING, [USER]-ratified at G2 over a ban on the effect class. Two copies read the bank at +2, and the
   # objection ("multiple copies compound on an uncapped bank") was heard and overruled: draft dilution
   # self-corrects at full roster. It is a C4 telemetry WATCH -- stack counts are reported, with no threshold
   # (R14) -- not a rule. The pair is the thing to look at first if the priest lane runs hot.
   # WHY THIS IS THE STEEPEST CARD ON THE SHEET, said plainly so nobody re-prices it casually: it multiplies a
   # bank that is uncapped and never spent (R80), so its value is unbounded in run length. Every other scaling
   # card here adds a term; this one moves a coefficient.
   # NAME: Enkanomiya, the sunless realm the Watatsumi people fled — its history is the forbidden knowledge she
   # is heir to, and "before sun and moon" is when it was written. A1O reserved the name via lint_unique_names.
   # COST 1 IS PROPOSED, matching the other Uncommon powers on this sheet (mercy_of_the_currents, pearl_current).
   # R73 ratified the EFFECT and the rarity; the cost is this pass's proposal and is a first knob if E2 reads hot.

# ---------- COMMON, v0.5 PARTIAL FILL (+12: 13 -> 25; +2 F4 bridge: 25 -> 27) ----------
# Balanced 3 per lane so the fill does not quietly re-weight the archetypes; attack-weighted (4 of 12) because
# the pre-fill commons ran 3 attacks in 13, and act 1 is bought with commons.
# Commander (3)
- {id: standing_orders, name: "Standing Orders", cost: 1, type: skill, rarity: common, solve: [block, frontload, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [commander], role: enabler,
   effects: [{op: conscript, amount: 1}, {op: block, amount: 4}]}
   # The order goes out and the line holds while it is answered. Net delta 0 (transform, never create — LAW 4).
   # The third face of the common conscript: notice replaces itself, to_the_front is free, this one is armoured.
- {id: signal_arrow, name: "Signal Arrow", cost: 1, type: attack, rarity: common, solve: [block, frontload, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [commander], role: glue,
   effects: [{op: damage, amount: 5, target: enemy}, {op: conscript, amount: 1}]}
   # The shot that calls the muster: a real swing that is also an order. Under pulsing_current's 7 because the (lint-ok: sibling card's number)
   # muster is worth more than the premium point it trades away.
- {id: shoulder_to_shoulder, name: "Shoulder to Shoulder", cost: 1, type: skill, rarity: common, solve: [block, frontload, scaling, utility, velocity], tempo_band: {fight: [early], run: [early, late]}, archetypes: [commander], role: payoff,
   effects: [{op: exhaust_from, amount: 1, select: chosen}, {op: copy_companion_in_hand, amount: 1}]}
   # Rotate one card off the line and the unit beside it steps up twice. The Commander's only common PAYOFF:
   # it whiffs with no companion in hand, which is exactly the archetype tax — you must have mustered first.
   # Net delta 0 (burn 1, copy 1). LAW-4 NOTE: the copy op was invisible to tools/lint_kokomi_decksize.py until
   # this row wanted it; the lint's CREATE_OPS now enumerates the copy family, so the accounting is real.
# Priest (3)
- {id: vow_of_tides, name: "Vow of the Tides", cost: 1, type: attack, rarity: common, solve: [frontload], tempo_band: {fight: [early], run: [early]}, archetypes: [priest, generic], role: glue, exhaust: true,
   effects: [{op: damage, amount: 8, target: all_enemies}]}
   # The self-consuming wave: waterspout's grammar aimed wide. Its burn is itself a Charge, which is the whole
   # priest bargain in one card.
   # R77 (Neap Tide v2.1) CONFIRMED this card unchanged: 8 (11 upgraded), Exhaust stays. Recorded rather than (lint-ok: upgrade value)
   # left silent, because "confirmed" and "nobody looked" are indistinguishable a month later.
   # The old note priced it "ABOVE surging_shoal's 7 by one point" — that gap is now 2 (shoal is 6 per R77), (lint-ok: quoted superseded note, corrected in the same line)
   # and the pricing sentence is struck rather than re-derived: the ratified numbers are 6 and 8, and inventing
   # a fresh justification for a gap nobody ruled on would be reasoning backwards from the answer.
- {id: pearl_diver, name: "Pearl Diver", cost: 0, type: skill, rarity: common, solve: [block, frontload, scaling, utility], tempo_band: {fight: [early], run: [early]}, archetypes: [priest], role: enabler,
   effects: [{op: exhaust_from, amount: 1, select: chosen}, {op: gain_charge, amount: 2}]}
   # The free fuel line: burn one, bank 3 total (2 line + 1 funnel). ritual_purification is the 1-cost engine
   # common that also replaces itself; this is the cheap one that does not. Watatsumi's divers, on the nose.
- {id: tideline_watch, name: "Tideline Watch", cost: 1, type: skill, rarity: common, solve: [block, frontload, scaling, utility], tempo_band: {fight: [early], run: [early]}, archetypes: [priest], role: glue,
   effects: [{op: exhaust_from, amount: 1, select: chosen}, {op: block_next_turn, amount: 8}]}
   # The guard posted for TOMORROW: nothing this turn, a real wall the next. Deliberately not votive_offering
   # with a bonus (that would be a strict domination at the same cost) — it is the same price for a different
   # shape, and it reads the enemy's telegraph instead of the current hit.
# Assist (3)
- {id: whispered_word, name: "A Whispered Word", cost: 0, type: skill, rarity: common, solve: [block, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [assist], role: glue,
   sly: [{op: draw, amount: 1}],
   effects: [{op: discard, amount: 1}, {op: block, amount: 3}]}
   # Free, small, and it rings its own bell: the discard can be this card's own trigger later. moon_signal buys
   # the look immediately; this one buys cover now and the look only if the word gets passed along.
- {id: driftwood_charm, name: "Driftwood Charm", cost: 1, type: skill, rarity: common, solve: [block, frontload, scaling, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [assist, generic], role: glue,
   sly: [{op: gain_charge, amount: 2}],
   effects: [{op: block, amount: 3}, {op: draw, amount: 1}]}
   # The Sly bell that feeds the meter — a §2.1 premium on the discard lane, which had none. Charge ACCRUAL,
   # not a read: nothing here scales off the bank, so §2.2's rate limits do not apply.
- {id: scattering_spray, name: "Scattering Spray", cost: 1, type: attack, rarity: common, solve: [frontload, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [assist, generic], role: glue,
   effects: [{op: damage, amount: 5, target: all_enemies}, {op: discard, amount: 1}, {op: draw, amount: 1}]}
   # The assist lane's own AoE: less than surging_shoal's 6, and it churns. The draw is not decoration — without (lint-ok: sibling card's number)
   # it this is strictly worse than the shoal at the same cost, which the domination lint would (rightly) call.
   # The correction that put the sibling's REAL number in that sentence is RETROACTIVELY BLESSED (R130,
   # 2026-08-07): a comment misquoting the card it compares against is a defect, and fixing it needed no ruling.
# Assist, F4 BRIDGE (+2 — the ratified Sly-lane direction, first rows to land)
# THE GAP F4 CLOSES, stated once for all three bridge rows. Her Charge and Burst meters BOTH pay on the
# EXHAUST verb and only on it (CHARGE_PER_EXHAUST, KOKOMI_BURST_PER_EXHAUST — see the double-wage note in
# constants.py). The Sly lane makes DISCARDS. A discard is not an exhaust, so the assist lane ran a churn
# engine wired to nothing: every bell it rang paid a local rider and none of it reached the meters the rest
# of the character is built on. That is why assist sat at 0.5–2.0% run winrate at EVERY value of the pulse
# multiplier in E1 — it is P9's finding applied to a whole lane, and no payout knob was ever going to move it.
# These rows do not buff the lane. They CONNECT it: discard -> exhaust -> meter -> the payoff that reads the
# pile the churn has been filling. P7 could not grade before they existed; the E1 assist column is its
# pre-F4 baseline.
- {id: ebb_tide, name: "Ebb Tide", cost: 0, type: skill, rarity: common, solve: [block, frontload, scaling, utility, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [assist], role: enabler,
   effects: [{op: discard, amount: 1}, {op: exhaust_from, amount: 1, select: chosen}]}
   # THE CONVERTER, in its plainest form: the random discard rings whatever Sly bell is in hand, and the chosen
   # exhaust turns the churn into Charge and Burst. Two cards leave your hand for zero energy and no immediate
   # board effect, which is the price — this is a card that buys ENGINE, not tempo, and a deck with no bells
   # and no exhaust payoff should never take it.
   # The exhaust is CHOSEN, not random, and that is the ruling that makes the card a decision instead of a
   # slot machine: you feed the meter the card you least want, which is the whole fantasy of a rotation lane.
   # It is also the only expressible shape — an unfiltered RANDOM exhaust_from has no C# path (the any-card
   # pool was never built; see the codegen guard), so a random version would be sim-only and unshippable.
   # LAW 4: nothing is created (a discard moves a card, an exhaust removes one from combat, neither touches
   # deck size), so the Common net delta is 0. LAW 5: no economy rider — the exhaust is the payment, not a (lint-ok: law number, not a value)
   # draw or an energy stapled to one.
- {id: salt_line, name: "Salt Line", cost: 1, type: skill, rarity: common, solve: [block, frontload, scaling, utility], tempo_band: {fight: [early], run: [early]}, archetypes: [assist, generic], role: glue,
   sly: [{op: exhaust_from, amount: 1, select: chosen}],
   effects: [{op: block, amount: 5}]}
   # THE BELL THAT RINGS INTO THE EXHAUST PILE. drifting_lantern taught that Sly pays either way; this teaches
   # that the discard lane can pay the METER. Played it is a fair common wall; thrown overboard by someone
   # else's churn it hands you an exhaust — so the lane's own noise starts feeding Charge and Burst without a
   # single card being spent on the conversion.
   # Deliberately NOT a strict upgrade of drifting_lantern: 5 Block played against the lantern's 4, but the
   # lantern's bell is 4 more Block (immediate, unconditional) where this one is an exhaust (deferred, and
   # worth nothing in a deck with no meter payoff). Different shapes at the same cost, which is what the
   # domination lint is for.
# Generic (3)
- {id: slack_water, name: "Slack Water", cost: 1, type: skill, rarity: common, solve: [block], tempo_band: {fight: [early], run: [early]}, archetypes: [generic], role: glue,
   effects: [{op: block, amount: 4}, {op: block_next_turn, amount: 4}]}
   # Half now, half later — Sayu's daruma shape in her own hands. Total 8 beats jade_bulwark's 6, and the split
   # is the price: it is worse against burst and better against a long grind.
   # NAME/ID: drafted as "Ebb and Flow" and CHANGED by lint_unique_names — Furina already owns that name and
   # that id, and a duplicate id would have taken the whole loader down. Slack water is the still moment at the
   # turn of the tide, which is the card.
- {id: tideturn, name: "Tideturn", cost: 1, type: attack, rarity: common, solve: [frontload, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [generic], role: glue,
   effects: [{op: damage, amount: 5, target: enemy}, {op: draw, amount: 1}]}
   # The swing that keeps the hand moving. Two points under pulsing_current, and the two points are the draw.
- {id: steady_the_line, name: "Steady the Line", cost: 0, type: skill, rarity: common, solve: [block, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [generic, assist], role: glue,
   effects: [{op: block, amount: 4}, {op: discard, amount: 1}]}
   # Free cover paid for in tempo — and the tempo it pays rings the Sly bell, so the assist lane wants it too.
   # The 0-cost block slot the pool did not have.

# ---------- UNCOMMON (12: +the R51 texture pair; +all_streams_flow, v0.3 charge-curve pass) ----------
# v0.3 (user-directed 2026-07-24): the meter gets an ON-CURVE reader. The v0.2 world rate-limited every Charge
# read to Rare/kit — the engine made fuel it could not spend, and the act-1 elite checks arrive at node 4, long
# before the rarity ladder does. The StS curve this pool now follows: big numbers clear act 1, multipliers and
# velocity clear act 3 (the Silent shiv package is the genre proof: a flat DOUBLING lives at uncommon).
- {id: all_streams_flow, name: "All Streams Flow to the Sea", cost: 1, type: attack, rarity: uncommon, solve: [frontload, scaling], tempo_band: {fight: [early, mid, late], run: [late]}, archetypes: [priest, generic], role: payoff,
   effects: [{op: damage, amount: 5, target: enemy, bonus_formula: 1_per_2_charge}]}
   # The sub-Rare reader: 5 + 1 per 2 Charge, single target, repeatable. At a node-4 bank of ~10 it is a 10-point
   # swing; at a priest-median 24 it is 17 — act-appropriate at both ends. Bounded by fuel (Charge costs cards), (lint-ok: priest-median worked example)
   # single-target (the AoE reads stay Rare/kit), and the Rare nuke keeps its premium by hitting ALL enemies.
# Commander (3)
- {id: mass_mobilization, name: "Rally the Isles", cost: 2, type: skill, rarity: uncommon, solve: [block, frontload, scaling, velocity], tempo_band: {fight: [mid], run: [early]}, archetypes: [commander], role: enabler,
   effects: [{op: conscript, amount: 2}, {op: gain_charge, amount: 1}]}
   # Two transforms in one order + a premium point. The engine's mid-game shove.
- {id: field_promotion, name: "Field Promotion", cost: 1, type: skill, rarity: uncommon, solve: [block, frontload, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [commander], role: enabler,
   effects: [{op: conscript, amount: 1, cost_override: 0}, {op: draw, amount: 1}]}
   # The recruit serves TODAY: conscript at cost 0 (this copy). Tempo face of the verb.
- {id: reinforcements, name: "Reinforcements", cost: 2, type: skill, rarity: uncommon, solve: [block, frontload, scaling, utility, velocity], tempo_band: {fight: [mid], run: [late]}, archetypes: [commander], role: payoff,
   effects: [{op: exhaust_from, amount: 1, select: chosen}, {op: conscript, amount: 2, mode: create}]}
   # THE kickoff §1.4 sample verbatim ("2 energy: Exhaust 1, create 2"): net +1 card — creation is legal at
   # Uncommon and priced so the positive-sum engine needs Rare payoffs + solved velocity to matter (LAW 4 scope).
# Priest (3)
- {id: mercy_of_the_deep, name: "Mercy of the Currents", cost: 1, type: power, rarity: uncommon, solve: [block], tempo_band: {fight: [late], run: [late]}, archetypes: [priest], role: payoff,
   effects: [{op: apply_power, power: feel_no_pain, amount: 3, target: self}]}
   # Block-per-exhaust (the Feel No Pain rail, already engine-proven): every burn is also a guard. With the
   # ward this is the stability loop closing — getting hit exhausts, exhausting blocks.
- {id: pearl_barrage, name: "Pearl Barrage", cost: 1, type: attack, rarity: uncommon, solve: [block, frontload, scaling, utility], tempo_band: {fight: [early], run: [late]}, archetypes: [priest], role: payoff,
   effects: [{op: exhaust_from, amount: 1, select: chosen},
             {op: damage, amount_formula: {base: 5, per: 3, count: exhaust_selection_cost}, target: enemy}]}
   # BODY RULED BY [USER] 2026-08-25 (R211), the EB-118 Phase-3 W3-Kokomi slate. It DEFERRED OUT OF W2b into
   # this window (R208) because the body and the chooser it needs are ONE DESIGN UNIT, and this is that
   # landing. Ashen-Strike is gone: the card no longer reads the PILE, it reads THE CARD YOU CHOSE.
   # THE ID IS KEPT (R211 item 5, the R69 pattern) and so is the display name -- only the body moves here.
   # WHY THE PILE READ HAD TO GO, and it is a distinctness fact rather than a taste one: this row was the
   # fifth member of the `damage@one~` clone family and one of FIVE cards reading the exhaust-pile count.
   # W2b took the family five -> three with this row's old body still present; this rewrite is what
   # completes R208's five -> two, and the pile readers go five -> three in the same slate (R2 drops the
   # other one).
   # THE PRICE RISE IS THE DRAFTER BECOMING HONEST, NOT THE CARD BECOMING STRONGER, and both halves are
   # true and sign together. The drafter evaluates a formula at ONE UNIT of the live count, so it read the
   # old body as 5+1=6 against a measured mean of 9.72 -- a 38% under-valuation -- and reads this one as (lint-ok: measured mean)
   # 5+3=8 against a measured 8.07, to within about 1%. So the offer-screen number goes UP (6.0000/7.0000 (lint-ok: measured mean)
   # -> 8.5000/11.5000) while the REALISED damage goes DOWN by about 1.6 points. (lint-ok: measured realised value)
   # THE LADDER IS 5 / 8 / 11 and it lands on 8 roughly three quarters of the time: Kokomi's sheet has no (lint-ok: payout ladder)
   # card above cost 2, so {0, 1, 2} is the entire live range, and the live chooser's mean victim cost is
   # 1.02. That bounded range is R211's reason for keeping `per: 3` rather than steepening -- base 4 / (lint-ok: measured mean)
   # per 5 turns the ladder into 4 / 9 / 14 over a distribution 88% concentrated on two values, and makes (lint-ok: measured distribution)
   # every chooser mistake far more expensive.
   # EMPTY HAND IS A READING, NOT A CRASH: the selection row still emits with size 0 and cost 0 and the
   # card deals its base 5.
   # UPGRADE `{formula_base: +3}` (was `{formula_per: +1}`, which has no pile slope left to bump): 5 -> 8, (lint-ok: payout ladder)
   # keeping the slope. On a BOUNDED count, bumping the base is the honest half -- the per-term ruling
   # belongs to counts that only grow.
- {id: communion_of_tides, name: "Communion of Tides", cost: 1, type: skill, rarity: uncommon, solve: [block, frontload, scaling, utility, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [priest, assist], role: glue,
   effects: [{op: exhaust_from, amount: 1, select: chosen}, {op: draw, amount: 2}]}
   # Burn one, see two: the lane-bridge card (priest fuel, assist velocity).
# Assist (2 + 1 F4 bridge)
- {id: rearguard_action, name: "Rearguard Action", cost: 1, type: skill, rarity: uncommon, solve: [block, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [assist], role: glue,
   effects: [{op: discard, amount: 1}, {op: block, amount: 7}]}
   # Cover the retreat: a real wall whose price rings the Sly bell.
# swift_currents: MERGED INTO moonlit_offering (G8, [USER], this pass). It was 1-cost Uncommon, self-Exhaust,
#   +2 energy, discard 1 -- an economy rider on an exhaust card below R79's Rare bar, and the F1 census found a
#   SECOND card in exactly that shape (moonlit_offering). Rather than promote two near-duplicates, the two are
#   one card at the R79 template. See moonlit_offering.
# Generic (0 since W3 -- shell_of_sanctuary's generic tag left with its body; the retrieval carrier
#              below is [priest, assist] now, and this heading is kept as the slot's history)
- {id: shell_of_sanctuary, name: "Salvage the Line", cost: 1, type: skill, rarity: uncommon, solve: [block, frontload, scaling, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [priest, assist], role: glue, exhaust: true,
   effects: [{op: draw, amount: 1},
             {op: recall_to_draw, amount: 1, from: exhaust},
             {op: gain_charge, amount: 2},
             {op: block, amount: 4}]}
   # BODY RULED BY [USER] 2026-08-25 (R211), W3-Kokomi. THE ID IS KEPT and the DISPLAY NAME CHANGES --
   # the R69 pattern: the identifier freezes, the string renames, and the retired name is reserved at
   # landing (docs/reserved-card-names.txt). Keeping the id saves the generated C# class name, the
   # upgrade row, the art path and the manifest entry; the cost is that the id no longer describes the
   # card, and R211 accepts that explicitly.
   # THE FIRST EXHAUST-RETRIEVING ROW IN THE REPO. `lint_recall_exhaust.py` reported zero retrieving
   # rows on every sheet until this one; the shape rules it enforces are satisfied BY CONSTRUCTION --
   # Uncommon (a Common retriever is refused by name) and it Exhausts itself (a retriever that does not
   # is refused by name), both checked on the codegen side and again at load.
   # THE EFFECT ORDER IS THE RULED CORRECTION AND IT IS LOAD-BEARING. Traced on the real resolver: with
   # recall BEFORE draw, the recall puts the card at index 0 of the draw pile and the draw pops index 0,
   # so the rescued card goes STRAIGHT INTO HAND -- which defeats the rule that a retrieved card goes to
   # the TOP OF THE DRAW PILE and never to hand. draw -> recall -> gain_charge is the order that reads
   # correctly: you draw off your existing pile, and the rescued card sits on top for NEXT draw.
   # An EMPTY Exhaust pile is a clean no-op with the draw, the Charge and the Block all still paying.
   # WHAT THE POOL LOSES, said plainly: 11 Block at cost 2 was Kokomi's largest single defensive face. (lint-ok: retired base face)
   # Her remaining flat Block runs rearguard_action 7, jade_bulwark 6, coral_guard 5, drifting_lantern (lint-ok: neighbour Block faces)
   # 4+4. This prints 4, which gives a little of it back but not most of it. If she feels defensively
   # thin after this window, that is where it came from.
   # WHY THIS DONOR: it is the least distinctive body she owns -- a bare Block number with no rider, no
   # condition and no archetype identity -- and it is a member of the EIGHT-CARD flat-Block clone (lint-ok: clone-cluster size)
   # cluster, so rewriting it takes that standing curated debt to seven. Measured, not hoped. (lint-ok: clone-cluster size)
   # WHY THE BASE BLOCK IS 4 AT ALL: without it the card prices 2.0000/7.0000, and the slot's price (lint-ok: drafted prices)
   # barely moving (5.5000/7.5000 -> 6.0000/10.0000) is the good outcome. (lint-ok: drafted prices)
   # ONE DISCLOSURE ABOUT INTENT: the approved plan names this row as a candidate for a RECYCLE rewrite
   # ("the card you chose tells this card what to do"). It is used for RETRIEVAL instead, because Block
   # scaled off a selection count needs a CalculatedVar the mod does not have -- the selection riders
   # are damage-only -- so Recycle bodies must be damage-shaped. That is a reading of the plan, flagged
   # rather than assumed.
   # HONEST FAILURE MODES: the returned card gains Exhaust for the rest of combat, so a rescued engine
   # piece is on a one-use loan; the sim's recall is the engine's own "best card" pick, not the
   # player's; and a second copy can never fetch the first, because retrievers exclude each other --
   # two copies are worse than one.
   # UPGRADE: NO SHEET EDIT AT ALL. The live delta is already `{block: 4}`, which is exactly what R211
   # wants (4 -> 8), so the row carries over untouched. (lint-ok: upgraded face)
# R51 texture pair (2)
- {id: exposing_current, name: "Exposing Current", cost: 1, type: attack, rarity: uncommon, solve: [frontload, utility], tempo_band: {fight: [early], run: [early]}, archetypes: [priest, generic], role: enabler, exhaust: true,
   effects: [{op: damage, amount: 8, target: enemy}, {op: apply_power, power: vulnerable, amount: 2, target: enemy}]}
   # The strategist marks the flaw: one self-consuming read of the enemy line (its burn is a Charge), and the
   # target stands exposed. Vulnerable rides an EXHAUST piece per R51 — one shot per copy, the priest lane's
   # setup swing. Uncommon-gated: no repeatable cheap applier exists below this line.
- {id: tidal_lure, name: "Tidal Lure", cost: 1, type: skill, rarity: uncommon, solve: [block, utility], tempo_band: {fight: [early], run: [early]}, archetypes: [assist, generic], role: glue,
   sly: [{op: apply_power, power: vulnerable, amount: 1, target: random_enemy}],
   effects: [{op: block, amount: 4}]}
   # Drifting Lantern's cousin with teeth: 4 Block played — but DISCARDED by a card effect, it baits an enemy
   # into the open (Vulnerable 1, random). The Sly bell as debuff: R51's second prescribed home. Assist stays
   # the glue lane — the payoff goes to whoever swings next, not to this card. (No domination pair: the lantern
   # is common with a bigger Sly number; this trades Sly magnitude for Sly quality.)

# ---------- UNCOMMON, v0.5 PARTIAL FILL (+8: 12 -> 20) ----------
# 2 per lane. This is where the two THRESHOLD predicates live (charge_at_least_N is UNCOMMON+ by grammar);
# all_streams_flow already broke the seal on sub-Rare Charge reads, and a flat bar is milder than its
# per-point slope, so the ladder stays monotone.
# Commander (2)
- {id: honor_guard, name: "Honor Guard", cost: 0, type: skill, rarity: rare, solve: [velocity], tempo_band: {fight: [mid], run: [late]}, archetypes: [commander], role: payoff, exhaust: true,
   effects: [{op: cost_mod, scope: companion_cards, delta: -1, duration: this_turn}]}
   # Every unit already standing costs 1 less THIS TURN, then the order is spent. The Commander's tempo
   # payoff: the archetype's failure mode is a hand full of recruits it cannot afford to play.
   # R75 (Neap Tide v2.1): the conscript half is DROPPED and the card gains Exhaust. The playtest carry combo
   # ran on the old version, and R75 removes its loop half first -- a card that both makes recruits and
   # discounts them is its own engine.
   # RARE AND 0-COST ([USER], this pass) -- and the promotion is REQUIRED, not cosmetic. R79 gives Discard/Sly
   # the monopoly on economy riders and permits one on an exhaust card only as "Rare AND self-Exhaust". A
   # blanket cost reduction is energy economy through a different door, so R75's own output (cost-reduction +
   # Exhaust) would have landed at Uncommon in violation of R79 in the same sprint that ratified R79. Rare is
   # the carve-out this card has to sit in. Recorded because the collision was found by the F1 census, not by
   # the ruling, and a later reader should not have to rediscover why a tempo skill is Rare.
   # NOTE THE SHAPE: with the conscript gone this no longer creates cards, so it is not a deck-size event
   # under LAW 4 either.
- {id: press_the_advantage, name: "Press the Advantage", cost: 1, type: attack, rarity: uncommon, solve: [block, frontload, velocity], tempo_band: {fight: [early], run: [late]}, archetypes: [commander], role: payoff,
   effects: [{op: damage, amount: 7, target: enemy}, {op: conscript, amount: 1, cost_override: 0}]}
   # The hit that makes the opening, and the recruit who walks through it TODAY (cost 0, this copy).
   # field_promotion is the same reach as a skill that replaces itself; this one is the reach on an attack.
# Priest (2)
- {id: moonlit_offering, name: "Moonlit Offering", cost: 0, type: skill, rarity: rare, solve: [velocity], tempo_band: {fight: [early], run: [late]}, archetypes: [priest, assist], role: enabler, exhaust: true,
   effects: [{op: energy, amount: 1}, {op: draw, amount: 1}, {op: discard, amount: 1}]}
   # G8 ([USER], this pass): THE ONE-TIME VELOCITY PIECE, and the merge target for swift_currents.
   # R79's carve-out has a template -- "Rare AND self-Exhaust" -- and the F1 census found TWO Uncommon cards
   # already wearing its shape (swift_currents: +2 energy, discard 1, Exhaust; this card: draw 2, exhaust 2,
   # Charge 3, Exhaust). Promoting both would have put two near-duplicate velocity Rares in one pool, so
   # [USER] folded them together: this id and name survive, the shape is the template's.
   # 0-cost is the [USER] call; the Rare is forced by R79 rather than chosen.
   # WHAT THIS CARD LOST, said plainly because it is an accrual change and §5 pins accrual:
   #   - `exhaust_from 2` is gone -> two fewer exhaust events, i.e. less Charge AND less Burst
   #   - `gain_charge 3` is gone -> the priest lane's single biggest Charge line
   # That is the SECOND accrual-side reduction riding in this batch (G6's starter migration is the first, and
   # §5 named only that one as sanctioned). Both are on the record for E2's read; if act-1 Charge over-drops
   # against P9's expectation, these two are the suspects before the multiplier is touched again.
   # The old note called this "the sheet's clearest statement that her deck IS her resource bar". That
   # statement now has no card carrying it -- worth knowing before someone reads the pool and concludes the
   # priest lane was always this lean.
- {id: read_the_current, name: "Read the Current", cost: 1, type: attack, rarity: uncommon, solve: [frontload, scaling], tempo_band: {fight: [early, mid, late], run: [late]}, archetypes: [priest, generic], role: payoff,
   effects: [{op: damage, amount: 7, target: enemy},
             {op: conditional, if: charge_at_least_10, then: [{op: damage, amount: 6, target: enemy}]}]}
   # THE THRESHOLD SHAPE, and the reason it exists: all_streams_flow's per-point slope is the only sub-Rare read
   # she has, and a slope is the shape that makes late Charge frightening. A bar does not — it pays once, it is
   # printed, and it stops. 10 is roughly her node-4 bank, so this comes online exactly when act 1 turns into
   # act 2. Off the bar it is a playable 7; on it, 13 — an uncommon-priced spike that never grows further.
   # Written as base-plus-bonus rather than a two-branch either/or ON PURPOSE: the upgrade then moves the half
   # that is always live, and the bar itself cannot drift downward as a side effect (resource-curve law).
# Assist (2 + 1 F4 bridge)
- {id: quiet_harbor, name: "Quiet Harbor", cost: 1, type: skill, rarity: uncommon, solve: [block, velocity], tempo_band: {fight: [early], run: [late]}, archetypes: [assist], role: payoff,
   sly: [{op: draw, amount: 2}],
   effects: [{op: block, amount: 5}]}
   # The Sly lane's velocity payoff: a fair wall when you play it, two cards when the churn throws it away.
   # drifting_lantern teaches that Sly pays either way; this is the uncommon that makes the discard the BETTER
   # half, which is the whole reason the assist lane accepts a low internal payoff elsewhere.
- {id: driftglass, name: "Driftglass", cost: 1, type: attack, rarity: uncommon, solve: [frontload], tempo_band: {fight: [early], run: [early]}, archetypes: [assist, generic], role: glue,
   sly: [{op: damage, amount: 5, target: random_enemy}],
   effects: [{op: damage, amount: 8, target: enemy}]}
   # The first Sly ATTACK on any sheet: 8 aimed, or 5 at whoever is nearest when it goes over the side. Nothing
   # else in her pool makes a random discard into damage, and the assist lane needed a reason to be in a fight.
- {id: undertow, name: "Undertow", cost: 1, type: attack, rarity: uncommon, solve: [frontload, scaling, velocity], tempo_band: {fight: [early, mid, late], run: [late]}, archetypes: [assist], role: payoff,
   sly: [{op: energy, amount: 1}],
   effects: [{op: damage, amount_formula: {base: 5, per: 1, count: exhaust_pile}, target: enemy},
             {op: conditional, if: exhaust_pile_at_least_3, then: [{op: draw, amount: 1}]}]}
   # F4's third bridge row, and the one that closes the loop: the payoff that READS the pile the lane has been
   # filling. Every other exhaust-pile scaler she owns is priest or generic (cleansing_tide, epiphany_of_the_
   # deep) — the assist lane fed that pile and had nothing that looked at it.
   # REVISED BY [USER] 2026-08-25 (R208), EB-118 Phase-3 W2b. EXACTLY TWO CHANGES: formula base 4 -> 5, and a
   # new `exhaust_pile_at_least_3` branch that draws. The card keeps its slope, its Sly energy rider, its
   # `{formula_base: +3}` delta, its `solve` and its labels. The access rewrite that would have replaced the
   # slope with a label was REJECTED under R199's guardrail -- no label-for-count.
   # THE BAR IS 3 BECAUSE THE PILE IS SHALLOW HERE, and that is a measurement. In kokomi/assist_weighted the
   # exhaust pile at attack plays has mean 0.90 and MEDIAN ZERO; the bar fires 15.3% of attack plays at 3, (lint-ok: measured rate)
   # 5.9% at 4 and 0.5% at 6. A deeper bar would be decoration on this lane.
   # LABELS DELIBERATELY UNMOVED: `role: payoff` and `archetypes: [assist]` stay, so kokomi/assist payoff
   # supply holds at 5. R199 guardrail (3) rules assist's problem to be ACCESS, not saturation -- cutting its
   # supply makes it worse -- so this rewrite adds reach without touching a count.
   # THE SLY RIDER IS ENERGY, and that is a LAW 5 statement rather than a number. R79 hands the card/energy (lint-ok: law number, not a value)
   # economy to Discard/Sly as a MONOPOLY, and nothing on this sheet had actually exercised the energy half of
   # it: moonlit_offering pays energy as a Rare AND self-Exhaust, i.e. under the law's one narrow exception,
   # not under the rule. This is the rule. Discarded, the card gives the turn back.
   # PRICING, PROPOSED. base 4 is under driftglass's aimed 8 on purpose — this card is bought for its slope, (lint-ok: sibling card's number)
   # and a card that is also the best turn-one attack in the lane makes the slope free. +1 per exhausted card
   # matches cleansing_tide's per-term at one rarity lower base (5), which is the intended read: same engine, (lint-ok: sibling card's number)
   # earlier, smaller.
   # NOT A DOMINATION PAIR with driftglass: driftglass is larger on an empty pile and its bell is damage; this
   # is larger on a full one and its bell is tempo. They cross somewhere around four exhausted cards, which is
   # a real drafting question rather than a strictly-better answer.
# Generic (3)
- {id: pearl_current, name: "Pearl Current", cost: 1, type: power, rarity: uncommon, solve: [block], tempo_band: {fight: [late], run: [late]}, archetypes: [generic], role: payoff,
   effects: [{op: apply_power, power: metallicize, amount: 3, target: self}]}
   # Standing guard: 3 Block at the start of every turn, forever. The generic lane's only power, and the one
   # card in the pool that pays a player who does nothing — deliberate, because every other engine she has
   # demands cards, and a deck that runs out of cards should not immediately run out of defence.
- {id: watch_of_the_shallows, name: "Watch of the Shallows", cost: 1, type: power, rarity: uncommon, solve: [sustain], tempo_band: {fight: [late], run: [late]}, archetypes: [generic], role: payoff,
   effects: [{op: apply_power, power: prevent_exhaust_ward, amount: 3, target: self, max_stacks: 6, never_reduces: true, note: "first unblocked hit each turn: prevent up to 3, Exhaust a random draw-pile card"}]}
   # P4, the LESSER WARD (EB-26; kickoff §2.4 band; sheetpass v0.2 §4 asked for an uncommon lesser ward, same
   # latch, so the stability identity exists before a Rare shows). Same power, same once-per-turn latch, same
   # price in future draws — half the magnitude of vigil_of_the_deep and a cost step under it, so the Rare keeps
   # the premium read and this is the on-curve one. The proc is still an Exhaust -> Charge: getting attacked
   # fuels the finisher from act one, not from whenever a Rare shows.
   # max_stacks 6 is the POOL'S ward ceiling, not this row's amount, and `never_reduces` is what makes that safe:
   # apply_power clamps the running TOTAL, so without the floor mode this card would LOWER a standing upgraded
   # Vigil when played after it. With it, the application only ever tops the ward up toward 6 and a bigger
   # standing ward is left alone. [USER] ruled the mode 2026-08-10 (EB-26 D2, option (d)).
   # TEMPO BANDS ARE THE CLASSIFIER'S, not the draft's. The packet (D5) proposed fight [mid, late] / run [early,
   # late] on the strength of the cost step under the Rare; tempo_band is a LANDED tag (R91) and the drift gate
   # requires it to equal suggest_role_tempo_tags' output, which reads this row exactly as it reads every other
   # Kokomi power. Moving the band means moving the classifier rule, which is a design call, not a landing.
   # NAME (D1, STILL OPEN): "Watch of the Shallows" is AUTHORED FLAVOR, not wiki-verified canon — built as the
   # lesser twin of Vigil of the Deep (shallows/deep, watch/vigil). Unique against the internal and reserved
   # namespaces, but S4-G11 (names read by eye before they ship) has no substitute: the eye-read is [USER]'s.
- {id: the_tide_remembers, name: "Tide of Names", cost: 2, type: attack, rarity: uncommon, solve: [block, frontload, scaling, utility], tempo_band: {fight: [mid], run: [late]}, archetypes: [priest, generic], role: payoff,
   effects: [{op: exhaust_from, amount: 1, select: chosen},
             {op: damage, amount_formula: {base: 5, per: 2, count: exhaust_selection_cost}, target: all_enemies}]}
   # BODY RULED BY [USER] 2026-08-25 (R211), W3-Kokomi. THE ID IS KEPT and the DISPLAY NAME CHANGES --
   # the R69 pattern again; the retired name is reserved at landing.
   # ITS LADDER IS DELIBERATELY DIFFERENT FROM PEARL'S. pearl_barrage is AIMED AND STEEP (5 / 8 / 11); (lint-ok: payout ladder)
   # this is WIDE AND SHALLOW (5 / 7 / 9). Two cards reading the same count with the same shape would be (lint-ok: payout ladder)
   # a clone; different targets, different costs and different slopes are two jobs.
   # WHY THIS DONOR: it is the same slot -- a cost-2 wide priest payoff -- so the replacement is like for
   # like and `kokomi/priest` payoff supply holds at 12; it carries the same tags, so the guardrail (lint-ok: payoff supply counts)
   # arithmetic comes out at zero; and it comes out of the more crowded family. She had FIVE cards
   # reading the exhaust-pile count against three reading Charge, and this slate takes the pile readers
   # to three.
   # THE TAGS ARE THE HONEST ONES (R211): [priest, generic], exactly what the row already carried. An
   # earlier draft dropped `priest` for `commander` and said in terms that it did so because tagging it
   # priest would take supply 12 -> 13. That is choosing a label to improve a count, which R199 (lint-ok: payoff supply counts)
   # guardrail (1) forbids outright. Three facts settle that the body is priest: commander is the
   # CONSCRIPTION engine (fourteen of its sixteen rows touch conscription or companions and NONE reads a (lint-ok: pool census)
   # card's cost); pearl_barrage is the identical cost-cash-out mechanic and is tagged [priest]; and the
   # earlier draft's own stated reason was the count and nothing else.
   # THE DRAFTED PRICE GOES DOWN, by 19%: 9.0000/12.0000 -> 7.2500/9.2500. Realised output goes UP about (lint-ok: drafted prices)
   # 9% with today's chooser and about 19% once W3's formula-aware chooser is live -- measured at each (lint-ok: measured deltas)
   # card's OWN plays, not deck-wide. Both directions are real and they are not in tension: the old body
   # was over-priced by the drafter reading a flat 4-to-all plus a bar it credits, and under-realised
   # because a cost-2 card is played late and its own pile is bigger than the deck-wide mean.
   # HONEST FAILURE MODE, and it makes the simulated number a FLOOR: the pilot cannot see this card's
   # payout when it decides whether to PLAY it -- it reads no selection count at all -- so it scores the
   # card against an EMPTY selection, base only. It will be under-played.
   # UPGRADE `{formula_base: +2}` (was `{damage: +3}`, which has no matching effect on the new body):
   # 5 -> 7, so the ladder becomes 7 / 9 / 11. (lint-ok: payout ladder)

# ---------- RARE (7 draftable + 1 kit) ----------
- {id: ceremonial_garment, name: "Ceremonial Garment", cost: 0, type: skill, rarity: rare, solve: [scaling], tempo_band: {fight: [late], run: [late]}, archetypes: [generic], role: payoff, tags: [burst], kit_card: true,
   requires: burst_energy_full,
   effects: [{op: apply_power, power: ceremonial_garment, amount: 3, target: self}]}
   # R74 (Neap Tide v2.1): THE ENTRY SPLASH IS GONE. Pure state-entry now. The Burst's job is to open the
   # window her attacks then read Charge through; the splash was a second, unrelated payment stapled to the
   # front of it, and it let the Burst read as a damage button rather than as a state. burst_max UNTOUCHED --
   # the meter still fills at the same rate, so this is a payout change, not an economy one.
   # The old "entry splash 5 -> 7 (clears Skittish 6)" justification is doubly dead: the card no longer has a (lint-ok: quoted dead justification)
   # splash, AND the Skittish reading it rested on was wrong (see the B1 errata on surging_shoal).
   # HER BURST (kit, v1.9: granted on charge, Retain, never in pool) — SHAPE B, the kickoff recommendation: enter
   # the state for 3 turns (CEREMONIAL_GARMENT_TURNS; test-pinned to the constant); while it holds, her attack
   # cards read Charge (+1 damage per GARMENT_CHARGE_DIVISOR=2 Charge, per play — v0.3 charge-curve pass: /4 was
   # decoration, /2 makes a priest-median bank a Burst-tier window). There is NO entry splash — R74 removed it
   # (see the note above); the state IS the whole card.
   # Cost 0: the charged meter IS the cost (Klee/Furina precedent). Meter 20 (lint-ok: engine constant burst_max)
   # — v0.4 O4 salvage, PROPOSED: burst_max 10 -> 20 once the Kurage took over the periodic output, and the W2 (lint-ok: engine constant burst_max)
   # bracket lives on that constant in tier0/content/characters/kokomi.yaml.
   # It is a real Burst WINDOW again, not the fast-cycling metronome the
   # v0.3 meter made it — that reading was the §6.4 frontload tension O4 exists to answer. Particles:
   # skill tags (5), reactions (5), exhaust events (KOKOMI_BURST_PER_EXHAUST=2). Four bake plays fill it. (lint-ok: engine constants, not this row)
   # FINISHER SHAPE IS RULING ASK 6: this roster ships the recommended both-with-capstone world (state as kit,
   # nuke as rate-limited Rare below) so the early sims can inform the ruling, not preempt it.
- {id: nereids_ascension, name: "Nereid's Ascension", cost: 2, type: attack, rarity: rare, solve: [frontload, scaling], tempo_band: {fight: [mid, late], run: [late]}, archetypes: [priest, generic], role: payoff, exhaust: true,
   effects: [{op: damage, amount: 12, target: all_enemies, bonus_formula: 1_per_2_charge}]}
   # SHAPE A as the state's capstone: one great wave reading the meter (+1 per 2 Charge, to ALL). Every §2.2
   # rate limit ships: Rare, Exhaust (which is itself one more Charge), cost 2. At a banked 20 Charge: 20-to-all, (lint-ok: banked-Charge worked example)
   # once. The multiplicative-read risk lives HERE and only here — watchlist cell in the report.
- {id: sango_prayer, name: "Sango Prayer", cost: 1, type: skill, rarity: rare, solve: [block, utility], tempo_band: {fight: [early], run: [late]}, archetypes: [priest, generic], role: glue, exhaust: true,
   effects: [{op: apply_power, power: weak, amount: 2, target: all_enemies}, {op: block, amount: 5}]}
   # R52 REWORK (ask 1: the v0.1 heal-12 is GONE — no amendment taken, none planned; "make her rares pay off a (lint-ok: removed v0.1 value, on record)
   # different way"). The prayer now stills the spears: Weak 2 to ALL + a moment's calm. R51 texture verbatim —
   # a debuff earned on an Exhaust piece (Rare, one cast per fight, and its burn is itself a Charge), NOT a
   # spammable cheap AoE weaken. Same sustain fantasy, zero HP restored: the axis it feeds is the stability band.
- {id: vigil_of_the_deep, name: "Vigil of the Deep", cost: 2, type: power, rarity: rare, solve: [sustain], tempo_band: {fight: [mid, late], run: [late]}, archetypes: [priest, generic], role: enabler,
   effects: [{op: apply_power, power: prevent_exhaust_ward, amount: 6, target: self, max_stacks: 6, note: "first unblocked hit each turn: prevent up to 6, Exhaust a random draw-pile card"}]}
   # THE §2.4 prevention power (user's sample made card): her HP bar doesn't move; her deck does. Every proc is
   # an Exhaust -> Charge: getting attacked fuels the finisher. Both structural guards ship (LAW 4 breaks the
   # loop at Common; Rare gating + the once-per-turn latch break it here). max_stacks 6: does NOT stack — the
   # magnitude is the knob, not the copy count. Prevention is REPORTED, not yet axis-credited (ask 4).
- {id: grand_conscription, name: "General Muster of Watatsumi", cost: 2, type: skill, rarity: rare, solve: [block, frontload, scaling, velocity], tempo_band: {fight: [mid], run: [late]}, archetypes: [commander], role: payoff, exhaust: true,
   effects: [{op: conscript, amount: 3}, {op: gain_charge, amount: 2}]}
   # The full muster: three call-ups in one order, and the order itself is stood down once answered. The
   # Commander's rare swing — the hand becomes an army, and the army rotates off the field having WON its
   # position. VOICE LAW (v0.4 §3): rotation, never sacrifice. Watatsumi's doctrine is minimal casualties;
   # nobody here is fuel. This comment is the marked example the sweep was written against.
- {id: depths_judgment, name: "Sango Isshin", cost: 2, type: attack, rarity: rare, solve: [block, frontload], tempo_band: {fight: [mid, late], run: [late]}, archetypes: [priest], role: payoff,
   effects: [{op: damage, amount: 14, target: enemy},
             {op: conditional, if: exhaust_pile_at_least_8, then: [{op: block, amount: 8}]}]}
   # BODY RULED BY [USER] 2026-08-25 (R208), EB-118 Phase-3 W2b. The Rare leaves the five-member (lint-ok: clone-family size)
   # `damage@one~` clone family and takes the DIVIDEND job: make the pile pay something other than damage. A
   # deep pile is the record of everything she has burned, and at Rare that record buys her a wall. `solve`
   # swaps `scaling` for `block` -- the classifier's own derivation, written by `suggest_role_tempo_tags.py
   # --land`, not by hand. `role: payoff` and `archetypes: [priest]` do not move, so kokomi/priest payoff
   # supply holds at 12. (lint-ok: supply count)
   # THE BAR IS 8, RULED BY [USER] 2026-08-25 (R209). R208 ratified the bar at 6 against rates later shown
   # contaminated (12.8% / 7.4%, taken through `score_config`'s anchor battery) -- struck rather than (lint-ok: measured rate)
   # rewritten at the C17 block in `tier0/constants.py`, R101b, under two dated forward corrections; read
   # them before quoting any rate here. Clean and well-sampled, bar 6 fires 38.4% of priest attack plays (lint-ok: measured rate)
   # -- a regular feature, not a dividend -- and bar 8 fires 24.2%, roughly one attack play in four: the (lint-ok: measured rate)
   # earned-moment shape the ratification wanted. Under R58 the bar may rise again and may never come
   # down: 6 is gone for good. (lint-ok: measured rate)
   # THE DRAFTER PAYS FOR THIS BRANCH, unlike almost every conditional in the window: `_static_condition`
   # waves the `exhaust_pile_at_least_` prefix through, so the 8 Block is credited at full face against a
   # 24.2% fire rate. The over-credit is bounded at 4.0 (8 Block / cost 2) and is disclosed, not tuned out. (lint-ok: measured rate)
- {id: epiphany_of_the_deep, name: "Song of Pearls", cost: 2, type: power, rarity: rare, solve: [velocity], tempo_band: {fight: [mid, late], run: [late]}, archetypes: [priest, assist], role: payoff,
   effects: [{op: apply_power, power: dark_embrace, amount: 1, target: self}]}
   # Draw-per-exhaust (the Dark Embrace rail): the burned page turns itself. In HER deck every lane rings it —
   # priced at the base game's rare rate for exactly that reason.
   # ROLE DEBT, RECORDED (Phase 3, ADOPTED 2026-08-24). This card's body is
   # draw-per-Exhaust, which the Phase-3 rubric classifies as ACCESS, not
   # payoff. It is held at role: payoff ONLY because it is one of five cards (lint-ok: an arm's supply count, not this row)
   # in kokomi/assist's payoff supply and R199's third guardrail forbids
   # cutting that arm mechanically. The hold is a guardrail consequence, not
   # a classification. When Assist's ACCESS problem is fixed -- by carriers,
   # not by labels -- this card is reclassified as enabler without a further
   # ruling being needed.
- {id: prayer_to_the_moon, name: "Prayer to the Moon", cost: 1, type: skill, rarity: rare, solve: [block, frontload, scaling], tempo_band: {fight: [early], run: [late]}, archetypes: [priest, generic], role: enabler, exhaust: true,
   effects: [{op: gain_charge, amount: 7}, {op: block, amount: 4}]}
   # The pure offering: one card, eight Charge (7 line + 1 funnel) and a moment's calm. The meter's rare (lint-ok: 7 line + 1 funnel arithmetic)
   # accelerant. v0.3: 4 -> 7 — the v0.2 audit found this RARE generating less meter than the benchmark
   # COMMON Forges; a rare accelerant must out-accelerate a common by more than politeness.

# ======================= EB-69 POOL FILL (+14: 62 -> 76) — R198, [USER] 2026-08-23 =======================
# WHY THIS BLOCK EXISTS. R58 carried the v0.5 partial fill's remaining gap forward as an explicit design pass
#   "AFTER the early playtest results". This is that pass, and it closes the gap in ONE batch: +4 rare,
#   +6 uncommon, +4 common, taking the sheet to 76 rows at 5 basic / 31 common / 26 uncommon / 14 rare —
#   Klee's shape. Draftable reward pool = 70 (`ceremonial_garment` is `kit_card: true` and never draftable).
#   The batch ships with a complete upgrade row for every one of the 14 (docs/kokomi-upgrades.yaml); EB-69 may
#   not ship without them, and nothing is held out.
# PROVENANCE. Bodies from the frozen 2026-07-29 brief (docs/archive/brief-kokomi-pool-fill.md, 15 proposals),
#   minus A3 `tideborne_discipline` — the one engine ask, DROPPED with its `discard_dividend` power, leaving the
#   brief's own declared A4+A6 fallback. Names are the S4-G11 eye-read's, [USER]-ruled 2026-08-23 over the
#   Japanese military register. `role` / `solve` / `tempo_band` did not exist when the brief was written:
#   `role` is ruled here, and `solve` / `tempo_band` are the CLASSIFIER'S per R91 — the drift gate requires
#   them to EQUAL suggest_role_tempo_tags' output, so moving a band means moving the classifier rule, which is
#   a design call and not a landing (watch_of_the_shallows' note is the standing statement of this).
#   THE EYE-READ SHEET'S PROPOSED solve/tempo_band VALUES ARE NOT WHAT LANDED, and that is the rule working
#   rather than failing: eleven of the fourteen differ from the v3 proposals, which were drawn by hand from
#   each card's nearest shipped analogue before the classifier was run. `--land` wrote the derived values.
#   SIX PRE-EXISTING ROWS ALSO MOVED for the same reason and are in this commit's diff --
#   ritual_purification, pulsing_current, shoulder_to_shoulder, pearl_diver, ebb_tide, communion_of_tides all
#   gained `block`, because gyorin_formation and tighten_the_cords give Charge and the exhaust funnel a
#   block-shaped payoff they did not have, and a carrier inherits the roles its meter cashes into (charter
#   A0.1). No hand edit was made to any of the six; the tag-through table is derived from the pool, and the
#   pool changed.
# THE R190 COLLISION IS NOT HIDDEN. Two of these rows classify `role: payoff` AND carry `assist`
#   (`what_the_tokoyo_took`, `the_gunbai_turns`), which moves Assist payoff supply 3 -> 5. That fence was
#   [USER]'s and [USER] amended it (R197) BEFORE this block landed, in the registration it protects:
#   review/active/payoff-reach-reregistration.md §6.8. Phase-0 item 8 forbids the alternative in so many words
#   — "do not disguise a payoff as glue to make the fingerprint pass" — so the honest tags are the tags.
#   `what_the_tokoyo_returns` is the borderline one and is ruled `role: glue`: retrieval and repair cash no
#   resource into output. If a later rubric rules retrieval IS payoff, the supply reads 6 by that rubric,
#   transparently, and no body here changes.
# EVERY NUMBER IN THIS BLOCK IS PROPOSED, as everywhere else on this sheet. The names are RULED.
# NO VERSION INTEGER MOVES WITH THIS BLOCK. EB-69 is registered settle-first content; RT/D/P/C are untouched.

# ---------- RARE, EB-69 (+4: 10 -> 14) ----------
# The priority the brief named: the assist lane had NO rare of its own (its two were priest cards wearing an
# assist tag), and a lane with no payoff at its top rarity has no reason to be drafted after the third pick.
- {id: the_gunbai_turns, name: "The Gunbai Turns", cost: 1, type: skill, rarity: rare, solve: [velocity], tempo_band: {fight: [early], run: [late]}, archetypes: [assist], role: payoff, exhaust: true,
   effects: [{op: grant_sly_this_turn, card_type: skill},
             {op: grant_sly_this_turn, card_type: skill},
             {op: grant_sly_this_turn, card_type: skill},
             {op: discard, amount: 3, select: chosen}]}
   # THE ASSIST LANE'S FIRST RARE OF ITS OWN, and it pays off cards already drafted rather than adding an
   # engine: three Skills in hand become Sly, then a chosen discard-3 fires all three riders at once.
   # `grant_sly_this_turn` filters to Skills not already Sly this turn, so the three ops pick three different
   # cards instead of stacking on one. Cost 1 + Exhaust keep it a one-shot detonation of a hand, not a loop.
   # FIRST PRINTED USE OF `grant_sly_this_turn` — the verb was implemented, tested and priced, and unreachable
   # because no card row used it (the surging_shoal vigil defect one level down: a verb in no card is a verb
   # that does not exist).
   # ROLE. `payoff`, honestly: it prints no damage and no Block, which is a tempting enabler argument, but its
   # entire function is cashing the lane's drafted Sly riders in one turn, at Rare, exclusively for assist.
   # That is a payoff wearing an enabler's effect list. See the R190 note in the block header.
   # LAW 5, DELIBERATE YES ([USER], D5) (lint-ok: law number, not a value): Rare AND self-Exhaust carrying a
   # chosen `discard` — selection, which that law's monopoly list names — is legal under the conjunctive
   # carve-out (lint-ok: the sentence above cites the law, not a card number), and this is the sheet's SECOND
   # instance. The header said "one" and now says two; the yes is recorded rather than inherited silently.
   # VOICE LAW: the gunbai is the commander's iron war fan and a turn of the fan is a signal, not a fall.
- {id: all_hands, name: "All Hands", cost: 2, type: skill, rarity: rare, solve: [block, frontload, scaling, velocity], tempo_band: {fight: [mid], run: [late]}, archetypes: [commander], role: payoff, exhaust: true,
   effects: [{op: conscript, amount: 2, mode: create},
             {op: cost_mod, scope: companion_cards, delta: -1, duration: this_turn},
             {op: gain_charge, amount: 2}]}
   # NAME RULED BY [USER] at the v1 eye-read (was "Beat to Quarters"); the register-shift alternate
   # "Sound the Horagai" was offered beside it at v2 and NOT taken. Ships as ruled.
   # COMMANDER'S SINGLE-CARD PAYOFF TURN. The lane's best turn currently needs two rares in hand —
   # grand_conscription makes the bodies and honor_guard discounts them, and nothing did both. `mode: create`
   # is Uncommon+ only under LAW 4 and the Exhaust pays one card back, so the net is +1 on a Rare, which is
   # what the law prices Rares for.
- {id: what_the_tokoyo_took, name: "What the Tokoyo Took", cost: 1, type: attack, rarity: rare, solve: [frontload], tempo_band: {fight: [mid], run: [late]}, archetypes: [assist], role: payoff,
   effects: [{op: damage, amount_formula: {base: 6, per: 4, count: discards_this_turn}, target: enemy}]}
   # THE ASSIST LANE'S ONLY SELF-READING ATTACK. Every damage card the lane could draft either reads the
   # EXHAUST pile (undertow, pearl_barrage, depths_judgment — priest's resource) or is flat (scattering_spray,
   # driftglass). A lane whose whole verb is discarding had no card that asked how much it discarded.
   # FIRST PRINTED USE of the `discards_this_turn` count.
   # [USER]-RULED REPRICE (v2 ruling (b)): cost 2 -> 1 and 3-per -> 4-per. The brief's version was ruled too
   # weak. Benchmarked against Strangle (1 energy, 8 + 2 per OTHER CARD PLAYED, considered unpickable — (lint-ok: the benchmark card's numbers)
   # lint-ok: Strangle's numbers, not this row's): this card's floor is worse (6 cold vs Strangle's 8, (lint-ok: benchmark comp)
   # lint-ok) and its ceiling much higher, and the counts are deliberately NOT
   # equally easy to hit — Strangle counts any card played, which happens for free every turn; this counts
   # cards discarded BY AN EFFECT, which only happens if the deck bought discard cards. So it stays a payoff
   # rather than a staple.
   # WATCH — POWER INCREASE, NOT A RE-RATE. Three discards is ONE CARD'S WORTH inside this very pool:
   # the_gunbai_turns discards 3 by itself and does so AFTER marking three Skills Sly, so those riders fire and
   # can discard more; open_the_stores adds 2; wheel_the_ranks adds 1; the upgraded send_the_runner adds 1; and
   # the five existing assist 0-cost random-discard commons add on top (lint-ok: a card count, not a value).
   # A chained turn reaching 6+ discards is
   # reachable inside this pool, and at 6 discards this is 30 damage for 1 energy, 33 upgraded (lint-ok:
   # worked arithmetic over the formula, not printed values).
   # THE POST-FILL BASELINE MUST REPORT THE UPPER TAIL, NOT A WORKED EXAMPLE: p90/p99 per-turn discard count
   # and the realized damage distribution of this card. A mean is not the instrument here; the tail is the
   # whole question. Carried durably as `W7` in STATE's watch register, not only here.
- {id: gyorin_formation, name: "Gyorin Formation", cost: 2, type: skill, rarity: rare, solve: [block], tempo_band: {fight: [mid, late], run: [late]}, archetypes: [generic, priest], role: payoff,
   effects: [{op: block, amount: 6, bonus_formula: 1_per_2_charge},
             {op: block_next_turn, amount: 6}]}
   # THE FLATNESS CARD, and the only one in this fill whose case is a MEASUREMENT. The 2026-07-29 stability
   # reading found that on the instrument R51 made the home of her healer fantasy, Kokomi reads mid-pack to
   # worst on every column — and that Klee, her declared opposite on the volatility axis, reads FLATTER than
   # she does. Her pool's reason is visible: pre-emptive Block is printed on exactly two commons (slack_water
   # 4/4, tideline_watch 8-next — lint-ok: sibling cards' numbers) and per-turn Block on one uncommon
   # (pearl_current). This is the two flatness
   # verbs at rare rate, with the Charge bank finally buying DEFENCE instead of only damage — the kickoff's
   # stated identity ("her HP bar doesn't move; her deck does") as arithmetic rather than as flavour.
   # ARITHMETIC, STATED EXACTLY, because the v2 eye-read got it wrong and said "twelve Block on the turn it is
   # played": it is 6 now (+1 per 2 Charge) and 6 at the START OF YOUR NEXT TURN — 12 across two turns, not 12
   # on one. At 8 Charge it is 10 now + 6 next (lint-ok: worked arithmetic over the Charge rider).
   # WATCH — POSSIBLE OVER-STRONG BLOCK ENGINE, DELIBERATELY DEFERRED BY [USER] 2026-08-23. The concern is not
   # a single-turn spike; it is a RATE — 6 pre-emptive Block every turn for as long as the card keeps coming
   # around, on a character whose Charge bank fills every time she rotates a card off and is NEVER SPENT (R80).
   # That is the thing to read in the post-fill baseline, and if her stability number moves a lot, this is the
   # first card to look at. Recorded so the deferral is visible when that baseline lands, not to reopen it.
   # Carried durably as `W6` in STATE's watch register.

# ---------- UNCOMMON, EB-69 (+6: 20 -> 26) ----------
- {id: council_at_bourou, name: "Council at Bourou", cost: 1, type: skill, rarity: uncommon, solve: [block, frontload, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [commander, assist], role: enabler,
   effects: [{op: conscript, amount: 1, mode: create},
             {op: draw, amount: 1},
             {op: discard, amount: 1, select: chosen}]}
   # THE LANE BRIDGE. The kickoff says assist "feeds both other lanes" and no card actually bridged them. This
   # one does it in one direction: velocity in, a body out, and the chosen discard means the card it draws into
   # can be thrown to a Sly rider.
   # D5 ([USER] 2026-08-23) — LAW 5 FIX AND RATE REDUCTION, both (lint-ok: law number, not a value). As the
   # brief printed it this card was
   # Uncommon, self-Exhaust, and drew 2 (lint-ok: the brief's superseded body, on record): an ECONOMY rider on
   # an exhaust card below LAW 5's Rare bar (lint-ok: law number, not a value), which the law admits only as
   # "RARE AND self-Exhaust". The brief predates that law (lint-ok: law reference), so it was an inherited defect rather
   # than a new proposal. [USER] took fix (1) of the three on offer — DROP THE EXHAUST — and reduced the draw
   # 2 -> 1 with it. Uncommons may create (reinforcements precedent), so the net-0 argument the brief used to
   # justify the Exhaust was never needed at this rarity; without the Exhaust the card is +1 net, which is
   # exactly what LAW 4 permits above Common. The alternatives are on the record as NOT taken: dropping the
   # draw would have killed the card's reason to exist (draw IS the bridge), and promoting it to Rare would
   # have taken a rare slot the fill did not budget and moved the pool tuple.
- {id: wheel_the_ranks, name: "Wheel the Ranks", cost: 0, type: skill, rarity: uncommon, solve: [block, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [assist], role: glue,
   sly: [{op: block, amount: 4}],
   effects: [{op: discard, amount: 1, select: chosen},
             {op: draw, amount: 2}]}
   # The lane's four 0-costs (moon_signal, whispered_word, ebb_tide, steady_the_line) are all COMMONS at common
   # rate, so a big-energy assist turn had nothing to spend on. A chosen discard into draw-2 at 0 is the
   # uncommon rate, and the Sly rider makes it pay when it is itself the card thrown.
   # NAME: kuruma-gakari, the rotating wheel formation where tired ranks turn off the line and fresh ones turn
   # on — the Exhaust/rotation voice rule applied to a cycler.
- {id: open_the_stores, name: "Open the Stores", cost: 1, type: skill, rarity: uncommon, solve: [block, frontload, scaling, utility, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [assist, priest], role: enabler,
   sly: [{op: exhaust_from, amount: 1, select: chosen}],
   effects: [{op: discard, amount: 2, select: chosen},
             {op: gain_charge, amount: 4}]}
   # THE ASSIST -> PRIEST BRIDGE, in the other direction from council_at_bourou: it converts a discarded hand
   # into Charge, the only currency both lanes read. Two chosen discards fire two Sly riders, and its own Sly
   # rider feeds the exhaust funnel, so the card pays whether it is played or thrown.
   # NAME: hyoro, an army's provisions — the depot thrown open and spent all at once for position.
- {id: what_the_tokoyo_returns, name: "What the Tokoyo Returns", cost: 1, type: skill, rarity: uncommon, solve: [block], tempo_band: {fight: [early], run: [early]}, archetypes: [assist], role: glue,
   sly: [{op: recall_to_draw, amount: 1}],
   effects: [{op: recall_to_draw, amount: 1},
             {op: block, amount: 4}]}
   # THE LANE'S STRUCTURAL WEAKNESS, ANSWERED: it discards at volume and could not get a payoff back.
   # FIRST PRINTED USE of `recall_to_draw`. Uncommon rather than common because recursion plus a lane built on
   # random discards is a real engine.
   # THROWN, IT RETURNS ITSELF — DELIBERATE, PINNED, AND SAID OUT LOUD (D3, [USER] 2026-08-23, R198). When a
   # card effect discards this card, only the `sly` list resolves (the played effects do NOT fire), and the
   # discard branch of `_op_recall_to_draw` reads the raw pile with no self-exclusion — so on an empty or
   # Skill-only pile the thrown copy recalls ITSELF to the top of the draw pile. That is now the DOCUMENTED
   # CONTRACT, not an accident: the brief's own rationale said "the Sly rider deliberately makes the THROWN
   # copy the better one", and the engine delivers it literally. It is a FALLBACK, not a rule — `_best_card`
   # ranks (is attack, printed power), so a decent Attack anywhere in the discard pile wins and this card
   # prints 0 damage. The played face cannot self-recall (it is resolving, not in a pile). The exhaust branch
   # (`recall_exhaust_pool`) DOES exclude self, kit, junk and other retrievers, because EB-118 §6.4 required
   # it; the asymmetry is real, is now intentional on both sides, and is pinned by
   # tier0/tests/test_eb69_tokoyo_returns_selfrecall.py.
   # ROLE: `glue`, and it is the borderline call in this fill rather than a comfortable one — retrieval and
   # repair cash no resource into output, but the two nearest live analogues in the same lane and rarity
   # (undertow, quiet_harbor) both carry `role: payoff`. Ruled glue (D1/R197). If a later payoff rubric rules
   # retrieval IS payoff, Assist payoff supply reads 6 instead of 5 by that rubric, and nothing here changes.
- {id: raise_the_sashimono, name: "Raise the Sashimono", cost: 0, type: skill, rarity: uncommon, solve: [velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [assist, commander], role: enabler,
   effects: [{op: grant_sly_this_turn, card_type: skill},
             {op: draw, amount: 1}]}
   # THE ON-RAMP, and the reason the_gunbai_turns is draftable at all: one card becomes Sly, one card is drawn,
   # free. Without something at this rarity the "make a card Sly" verb would exist on exactly one Rare and the
   # lane's rare payoff would have no ladder up to it.
   # NAME: sashimono, the small back-banners a Sengoku unit was identified and directed by — one banner up, one
   # unit marked, which is literally what the card does to one Skill.
- {id: crane_wing, name: "Crane Wing", cost: 1, type: skill, rarity: uncommon, solve: [block, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [commander], role: glue,
   effects: [{op: block, amount: 4},
             {op: cost_mod, scope: companion_cards, delta: -1, duration: this_turn}]}
   # RATIFIED REDESIGN (R202, EB-125): the printed Block drops so the card separates from jade_bulwark on what
   # it is FOR rather than on a number. It was Pearl Bulwark plus a rider (lint-ok: superseded printed Block 6),
   # the textbook shape the domination lint exists to catch. Pearl Bulwark stays the pool's clean Block-rate
   # anchor; Crane Wing surrenders immediate Block to keep its companion-discount identity. Upgraded it lands
   # exactly level with Pearl Bulwark's PRINTED face and two under Pearl Bulwark upgraded (lint-ok: sibling
   # card's numbers), which is the separation R200 asked for. `role: glue` is unchanged, so R199's third
   # guardrail (no mechanical supply cut on commander) is untouched.
   # Commander's only discount was a Rare (honor_guard), so the lane could not defend on the turn it mustered —
   # it either played bodies or played Block. Block-plus-discount at uncommon is the lane's missing tempo turn.
   # NAME: kakuyoku, the crane-wing formation — the line spreading its arms around what it is protecting.
   # Pairs with gyorin_formation as a two-card formation family, which reads as intentional rather than
   # repetitive at exactly two.

# ---------- COMMON, EB-69 (+4: 27 -> 31) ----------
# Each nets card delta <= 0 and is checked against LAW 4 by tools/lint_kokomi_decksize.py.
- {id: send_the_runner, name: "Send the Runner", cost: 0, type: skill, rarity: common, solve: [block, frontload, scaling, utility, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [priest, assist], role: glue,
   effects: [{op: draw, amount: 1},
             {op: exhaust_from, amount: 1, select: chosen}]}
   # [USER]-RULED BODY (v2 ruling (d), CONFIRMED at D2a 2026-08-23 against a reviewer's proposed reopen).
   # The brief's body (draw 1, discard 1 chosen, gain 1 Charge) was strictly better than Silent's Prepared,
   # which is already an excellent card — i.e. strictly-better-than-excellent at common rate.
   # WHAT THE VERBATIM WAS ABOUT, recorded the right way round. [USER]'s "becomes hand-size-neutral at common
   # rarity" is the CRITICISM OF THE REVIEWER'S Prepared-parity ALTERNATIVE — the reason that version was
   # REJECTED — not a property of the body held here. Both faces of the held body are deliberately net −1,
   # counting the played card: base = −1 play +1 draw −1 exhaust = −1; upgrade = −1 play +2 draw −1 discard
   # −1 exhaust = −1. A 0-cost common that costs nothing in cards is exactly what the ruling refused.
   # THE CHARGE DID NOT GO AWAY. CHARGE_PER_EXHAUST = 1, so the exhaust earns exactly the 1 Charge the printed
   # line used to grant: net zero on Charge.
   # WATCH — POWER, burst-particle cadence. It ALSO now pays KOKOMI_BURST_PER_EXHAUST = 2 burst particles the
   # discard body never paid, at Common, at cost 0, repeatable. Small but real, and it is an addition to her
   # burst cadence across a run rather than to any one turn. Carried durably as `W8` in STATE's watch
   # register, not only here.
   # IT CHANGED LANES, and that consequence is ACCEPTED EXPLICITLY rather than inherited: chosen Exhaust is the
   # PRIEST verb, so the archetypes are [priest, assist] (pearl_diver's neighbourhood — Common, cost 0, chosen
   # Exhaust) and `solve` gains scaling, because it feeds Charge and the Burst meter through the funnel.
   # THE COST, NAMED: the assist lane therefore ends this fill with NO common-rate chosen-discard cycler. That
   # was this card's entire declared job in the brief, and only the UPGRADED face discards. Every other assist
   # 0-cost discards at RANDOM. [USER] took that trade knowingly.
   # LAW 6 (rotation law) covers the exhaust: an unfiltered chosen-Exhaust never offers a Status or a Curse, by
   # construction in the engine, so this card cannot be used to eat junk and stays out of the reserved
   # junk-eater design space.
   # NAME: tsukai-ban, the Sengoku messenger corps. [USER] reverted the proposed "Relieve the Post" swap on
   # 2026-08-23, verbatim: "I do actually prefer 'Send the Runner', so yes, let's revert the name change."
- {id: massed_volley, name: "Massed Volley", cost: 1, type: attack, rarity: common, solve: [frontload], tempo_band: {fight: [early], run: [early]}, archetypes: [assist, generic], role: glue,
   sly: [{op: damage, amount: 4, target: random_enemy}],
   effects: [{op: damage, amount: 5, target: all_enemies}]}
   # The lane's only AoE was scattering_spray (5 AoE plus a random discard). This is the same rate with the
   # payoff moved onto the Sly rider, so it rewards being THROWN rather than charging for it — and R56's "no
   # one starts the game with AoE; if you need it, you draft it" is respected because it is a draft-in, not a
   # starter. Delta 0.
   # NAME: the massed-volley doctrine the Sengoku field armies were built around. (`ashigaru` was considered
   # and dropped: levied foot soldiers brush the forced-service reading the voice law keeps out of her pool.)
- {id: hold_the_narrows, name: "Hold the Narrows", cost: 1, type: skill, rarity: common, solve: [block, frontload, velocity], tempo_band: {fight: [early], run: [early]}, archetypes: [commander], role: glue,
   sly: [{op: conscript, amount: 1}],
   effects: [{op: block, amount: 5}]}
   # The only card in the pool where the COMMANDER verb fires off the ASSIST verb, at the rarity where the two
   # lanes actually meet in a deck. `conscript` in default transform mode is delta ZERO, which is precisely why
   # LAW 4 lets it sit on a Common.
   # NAME. Coupled swap ([USER], D4): council_at_bourou took the Bourou place-name, and "Bourou" on two cards is
   # the adjacency problem the eye-read exists to prevent — so this card, drafted "Guard at Bourou", takes its
   # alternate. RATIONALE CORRECTION CARRIED WITH IT: the v2 claim that "Bourou means watchtower" is WRONG and
   # withdrawn — Bourou Village is the resistance's own village on Watatsumi, which is canon and is why the
   # name works, but the etymology claim was false and is struck rather than re-derived.
- {id: tighten_the_cords, name: "Tighten the Cords", cost: 1, type: skill, rarity: common, solve: [block], tempo_band: {fight: [early, mid, late], run: [early, late]}, archetypes: [priest], role: payoff,
   effects: [{op: block, amount: 5},
             {op: conditional, if: exhaust_pile_at_least_3,
              then: [{op: apply_power, power: metallicize, amount: 1, target: self}]}]}
   # RATIFIED REDESIGN (R202, EB-125), body and labels together. It was a DIRECT CLONE of Gorou — Forward Unto
   # Victory: same printed Block, one less Metallicize, and its old upgrade took the Common to the uncommon's
   # printed face exactly. The Metallicize is now GATED on the exhaust pile, so the two cards carry different
   # benefit keys and neither set contains the other.
   # THE LABELS FOLLOW THE BODY (Fork A, R202). Reading the exhaust pile — priest's public state — is a payoff
   # under the Phase-3 rubric, and every other reader of that pile on this sheet is `[priest]`
   # (mercy_of_the_deep, pearl_barrage, the_tide_remembers, depths_judgment). So `[priest] / payoff`, and
   # `generic` is DROPPED under one-role honesty rather than kept as a hedge. The cost is named, not hidden:
   # priest is the most over-supplied arm on the sheet and this adds a payoff to it. R199 ruled the bands
   # directional, and Guardrail 1 forbids relabelling a card to keep a count tidy.
   # It now READS her own engine instead of printing a larger Block number, which is what Phase-0 §6.5 asks
   # for, and it keeps the card's stated identity — bought for the trajectory, not for the turn — while making
   # the trajectory something you build.
   # The threshold is legal at Common: the grammar note above fences CHARGE bars to Uncommon and above, and an
   # exhaust-pile bar is not a Charge bar. Per-turn Block is still printed on exactly one other card in her
   # pool (pearl_current, uncommon, metallicize 3).
   # NAME: the Sengoku proverb katte kabuto no o wo shimeyo — "after the victory, tighten the cords of your
   # helmet." A card bought for the trajectory could not ask for a better name. The v1 name (Slackwater Drill)
   # echoed the shipped `slack_water` and is gone: no shared word, no shared shape.



END OF PASTED MATERIAL. Answer now, in the order given: E1..E5, then OVERALL A-D.
