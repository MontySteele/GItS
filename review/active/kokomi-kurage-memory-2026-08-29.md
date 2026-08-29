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

## 6.1 What the sim build found

**Built 2026-08-29 on this branch: the tier0 half of §6's first row, behind
`KURAGE_MEMORY`, default off.** Python only — no C#, no bridge, no UI, no game.
The full tier0 suite (3537), the tier05 suite (794), the 27 `--lane ci` lints,
`gen_roster_cards --check` and the pinned `KleeCode` build are all green, and
the flag being off is why: every read of every constant below sits inside an
`if C.KURAGE_MEMORY` branch, so the shipped engine cannot reach any of it. No
sheet row, card yaml, LAW line or register moved, so **no drafted number moved
and `DRAFTER_VERSION` did not**.

### The constants, and what each one's alternative is

Every §5 pick is one named constant in `tier0/constants.py`, shipped at the
proposal's recommendation:

| constant | default | alternatives |
|---|---|---|
| `KURAGE_MEMORY` | `False` | the master flag |
| `KURAGE_FUEL_MODE` | `"exhaust_own"` (A1) | `"play_or_exhaust"` (A2) — **implemented** |
| `KURAGE_THRESHOLD` | `5` | **DERIVED, not picked** (§2's `ritual_purification` 4 + the funnel's 1) |
| `KURAGE_FIRE_TIMING` | `"turn_start"` (B1) | `"turn_end"` (B2) — **implemented** |
| `KURAGE_TARGET_RULE` | `"follow_her_last_attack"` (E1) | `"random"` (E2) — **implemented** |
| `KURAGE_POWER_PULSE` | `"hydro"` (C1) | C2 / C3 **not implemented** (§5 argues both away) |
| `KURAGE_EMPTY_QUEUE` | `"hold"` (D1) | D2 **not implemented** (it restores the thing being removed) |
| `KURAGE_MEMORY_PULSE_BLOCK` | `5` | see (1) below — this constant is new |
| `KURAGE_QUEUE_CAP` | `0` = uncapped | the first knob if sim finds a backlog |

`KURAGE_DURATION` and `KURAGE_PULSE_PER_CHARGE` are **not read** under the flag.

Where the rule lives: `effects.note_kurage_play` (the queue, the pulse key, A2's
play-side fuel), `effects.kurage_fire` (the threshold fire, on slice 2's
`resources.spend_charge` rail), `effects.kurage_memory_pulse` (the pulse),
`effects.kurage_target` + a first branch in `effects.bind_card_aim` (the aim),
`_op_summon_kurage` (persistence), `refpowers.after_card_exhausted` (the fuel's
one clause), `combat._finish_play` (the one call site for "she played a card")
and `combat._player_turn` (B1's fire and the per-turn clears).

### The holes the build had to fill, which the proposal did not answer

Each of these is a decision taken to make the code run, **not a ruling**, and
each returns to [USER] with the picks.

1. **The Skill pulse's 5 is not `KURAGE_PULSE_BLOCK`.** §2's table calls the
   Skill branch "shipped: 5", but the shipped `KURAGE_PULSE_BLOCK` is **0** —
   it was turned off at the v0.4 starter rework. The 5 is `kurages_oath`'s
   printed `kurage_ward` grant, which is a *drafted* Common power and not the
   pulse's own number. Built as a **new** constant, `KURAGE_MEMORY_PULSE_BLOCK
   = 5`, so the shipped 0 stays reachable byte-for-byte with the flag off; the
   Oath's ward still stacks on top of it. If [USER] means "the Skill pulse is
   the Oath and only the Oath", this constant should be 0 and the row unmoved.
2. **The queue is per FIGHT and lives on `CombatState`**, beside
   `companions_played`, not on `Player` beside `charge`. That makes the reset
   structural (`run_fight` builds a fresh state) instead of a line someone must
   remember. §2's "per fight" is satisfied either way; this is the cheaper way.
3. **The memory fills without a jellyfish; only the FIRE needs one.** §2 says
   "the Bake-Kurage remembers", which could mean the queue does not start until
   the summon is out. Built the other way: Companions played before the first
   `bake_kurage` are remembered, and the summon is what acts on the memory. The
   opposite reading punishes a turn-1 Companion for a card she had not drawn.
4. **The new pulse aims by `KURAGE_TARGET_RULE`, like the replay.** The shipped
   pulse rolls a random living enemy; §2 names a "pulse target" for PICK C1 and
   never says which. Built so the Attack pulse, the Power pulse's Hydro and the
   replay all land on the same forecastable body — which is the only version
   the strip can draw.
5. **Only the Charge funnel narrows; the Burst wage does not.** `CHARGE_PER_
   EXHAUST` and `KOKOMI_BURST_PER_EXHAUST` are documented as one wage in two
   currencies, and §4 removes the Muster *Charge* subsidy without mentioning
   Burst. A Mustered Companion's Exhaust therefore still pays her burst
   particles and pays no Charge.
6. **The upgrade, the second copy, and the Casket link all go inert together.**
   §2 retires `KURAGE_DURATION` and asks what the upgrade's +1 turn does; the
   answer the code gives is *nothing* — a persistent summon has no turn to add,
   so an upgraded `bake_kurage` is mechanically identical to a base one, a
   second copy is a no-op, and the Garment's Tamakushi Casket refresh maxes a 1
   against a 1. Giving the upgrade a second job is the re-authoring question
   §4 already books.
7. **`before_sun_and_moon` still drafts, and now does nothing.** §4 retires the
   card with the multiplier, but the sheet is untouched on this branch, so
   under the flag the row is a live draftable Common with no body. That is a
   *sheet* edit, and it is [USER]'s.
8. **`read_the_current`'s `charge_at_least_10` now reads a draining bank.**
   Same cause: the sheet is untouched, so the one shipped Charge threshold
   still fires against a bank the jellyfish is spending down. §4 already says
   to re-author it; the flagged arm will simply show the interaction.
9. **A non-jellyfish free play still counts as "she played it".** The recursion
   rules are keyed to `state.kurage_autoplaying`, which is set only by the
   memory fire — so a Sly or Havoc-style auto-play would enter the queue and
   set the pulse key. Nothing in Kokomi's pool does that today, and narrowing
   the exclusion to the jellyfish is what §7's finding actually asks for.
10. **Study Buddy's replay is one play, not two.** The memory hook sits ahead
    of `_finish_play`'s replay loop, so a replayed Companion is remembered once.
11. **On the STARTER DECK the engine never fires, and that is a finding about
    `T`, not a defect.** Across five whole fights the jellyfish is fielded and
    pulses every turn, the memory fills (1–2 Companions), and the bank tops out
    at **2** — so a threshold of 5 is never reached and the queue is still full
    at fight end. The cause is arithmetic and it is exactly PICK A1: her
    starter deck contains no card that Exhausts one of her own non-Companion
    cards, so under "Exhausts only" a starter Kokomi has almost no fuel at all,
    and the two Charge she does bank come from `bake_kurage`'s printed
    `gain_charge`. This is the first thing a sim arm must move, and it moves in
    one of three directions, all [USER]'s: lower `T`, take A2
    (`play_or_exhaust`), or accept that the engine is a *drafted* engine that
    the opening deck deliberately cannot run. **No number here is quotable** —
    it is reported as the shape of a hole, not as a measurement.

### What the pilot sees, stated so nobody mistakes this arm for a measurement

`pilot/policy.py` no longer prices a retired multiplier: under the flag the
summon is valued at one flat pulse, which badly understates a persistent
jellyfish and is the declared safe direction to be wrong. **The pilot does not
value the queue at all** — it does not know that playing a Companion banks a
free replay, does not know a fire is a turn away, and does not steer play
order. So the flagged sim arm exercises the *rule* end to end and never the
*decision* the rule exists for, which is exactly why §6 routes acceptance
through whole-fight blind play and forbids quoting a number off this arm.
`M49`'s Charge valuation is untouched and stays superseded (§4).

### The two recursion rules, as code

Both are one line — `state.kurage_autoplaying` — and both are tested
separately because they are two different claims, and both were verified
**red-first** (removing the line fails four tests):

- a card the jellyfish plays does **not** re-enter the memory, which is the
  only reason §2's "self-bounding" claim is true;
- an auto-played card is **not** "the last card Kokomi played", so the
  turn-start replay cannot determine or overwrite the pulse before she acts.

Both were owed to the doctrine seat's §7 findings rather than to the proposal.

---

## 7. The doctrine seat's read

The repo-visible seat — Codex CLI `0.150.1`, `gpt-5.6-sol`, independent by model
family (R217 C) — read this document as committed at `531918d`, under the
clause-only protocol. Reply verbatim:
`review/qa/kokomi-kurage-memory-doctrine-review-codex-gpt-5.6-sol.md`; prompt
kept beside it, sha256
`f634d108a796e0bbd8c2c58e3491eb636104cfa39ad3a96aed5e547c4d8dc3f4`.

**It volunteered no remedy.** Nothing in its reply is marked DISCARDED, and its
family therefore stays eligible to grade this row later (`EB-190`). It named
clauses and nothing else, which is what the protocol asks for.

### The verdicts

| element | addresses the noted issues? | doctrine |
|---|---|---|
| E1 the queue | **PARTLY** | **FOLLOWS** — D2 |
| E2 the fuel | **YES** on defence-feeds-the-finisher, **PARTLY** overall | **REQUIRES_MODIFICATION** — rotation/accrual law + relic |
| E3 the threshold | **PARTLY** | **REQUIRES_MODIFICATION** — R80 + the LAW Charge bullet |
| E4 the pulse | **PARTLY** | **REQUIRES_MODIFICATION** — kickoff identity/finisher + printed rows |
| E5 the UI | **PARTLY** | **FOLLOWS** — D4 |
| **overall** | **PARTLY** | **REQUIRES_MODIFICATION** |

On the queue: *"It directly gives Companions a second identity beyond 'boring
bodies' and makes their play order consequential. It indirectly adds a decision
around Charge, but does not by itself separate defence from advancement or let
the player decide when Charge converts."* Doctrine **FOLLOWS**, on D2:
*"Choosing which Companion enters the visible queue and when is player-steered
acquisition and ordering, provided the queued face and downstream target are
forecastable under D4."*

On the fuel: **YES** on the second noted issue, in its words — *"Companion
defence no longer also supplies Charge"* — and PARTLY overall because *"Charge
generation still culminates automatically."*

On the threshold: *"Spending makes Charge cyclical instead of a number watched
forever, and replaying queued Companions gives them consequential afterlife. The
conversion itself remains compulsory, so the player still waits for the clock
once queue order has been established."*

On the pulse: *"It breaks the direct defence-to-ever-larger-finisher loop and
makes sequencing card types matter. It does not itself improve Companions, and
its automatic payoff can still become 'play the desired type last, then watch'
if the branches do not create materially different choices."*

On the UI: **FOLLOWS**, D4 — *"The ordered faces, marked threshold, firing
indication, pulse indication, and forecast target are the appropriate doctrinal
surface, contingent on unresolved targeting and pulse semantics being
displayed."*

Overall (A): *"The proposal substantially addresses boring Companions and removes
Companion defence as Charge fuel. It replaces passive permanent scaling with an
ordered tempo clock, but does not fully resolve 'waiting rather than deciding'
because firing, payment, and card selection remain automatic."*

### The clauses it says must move — the full list, and the correction it makes to §4

Its (B), verbatim in the reply, is the most useful thing it produced, and it
**corrects this document**. §8's original closing sentence said R80 and the
relic were *"the two amendments this design needs"*; the seat's (D) names that
as the proposal's one internal inconsistency with doctrine:

> "The proposal is internally inconsistent with doctrine when it claims, 'R80 and
> the relic text are the two amendments this design needs.' The pasted law also
> binds universal Companion accrual, Charge-reading finishers, the Commander
> consumption link, the kickoff decision loop, summon duration/refresh, and
> several printed reader and pulse rules."

It is right, and §8 is corrected below rather than defended. The complete set it
names:

1. the LAW Charge bullet, *"Charge is never spent"*;
2. R80 in the sheet header, *"CHARGE IS NEVER SPENT"*;
3. the LAW rotation/accrual definition, *"insofar as Companions currently count
   as her own cards"*;
4. kickoff §1's decision loop, *"Every card kept is engine; every card burned is
   Charge"*;
5. kickoff §2.1's universal accrual and its *"never expended"* property;
6. kickoff §2.2's Charge-reading finisher requirement;
7. kickoff §2.3's *"feeds Charge on consumption"* (the Commander link);
8. kickoff §2.4's *"Each proc is an Exhaust event → Charge"*, where the
   ownership exclusion applies;
9. kickoff §2.5 and the shipped starter relic text;
10. the printed rules for `bake_kurage`, `before_sun_and_moon`, `kurages_oath`,
    `ceremonial_garment`, `nereids_ascension`, `all_streams_flow`,
    `read_the_current`, `gyorin_formation`;
11. **Tamakushi Casket's refresh link** — the Burst's canon *"REFRESHES a
    fielded Bake-Kurage"*.

Items 1, 2, 9 and 10 are already in §4. **Items 3–8 and 11 are new**, and six of
them are the *kickoff charter* rather than LAW — the seat is saying that a
character's charter document is itself a clause set that a redesign has to amend
in the open, not quietly outgrow. `kurages_oath` in item 10 is a row §4's table
missed: it is priced against the shipped pulse frequency, so a persistent
jellyfish moves it whether or not its text changes. I have not amended anything;
this list is what [USER] is being handed alongside the picks.

### The D2/D4 question on automatic firing

Asked directly — the jellyfish fires automatically, the player cannot choose
when, cannot decline, cannot pick the card; does a visible queue rescue that?
Its (C), verbatim:

> "A visible ordered queue can satisfy D2 even though execution is automatic,
> because D2 does not require control at execution; it requires that the
> automatic engine 'feed a decision the player can steer,' and play order
> supplies timing/acquisition steering. D4 is also measured 'At the decision
> point,' which here is the earlier Companion play. **This passes only if that
> point exposes the remembered face, firing conditions, target, recursion rule,
> and relevant pulse consequence. Visibility alone does not rescue an outcome
> whose consequential semantics remain unresolved.**"

That is a conditional pass, and the condition is a list of five things the strip
must show. Four of the five are already §3's job. The fifth — the **recursion
rule** — is a genuine hole it found and this document does not answer:

> "An automatically replayed Companion may itself satisfy 'When Kokomi plays a
> Companion card,' append another copy, and prevent the queue from shrinking.
> The proposal does not specify whether remembered plays can remember
> themselves."

It repeats the point against §2's own claim that the queue is self-bounding:
*"the proposal contains no exclusion supporting that claim."* Correct on both
counts. §2's "uncapped is fine because every fire removes one" is **only true if
a jellyfish-played Companion does not re-enter the memory**, and this document
never said so. That is a rule the design owes, not a number, and it is recorded
here as owed rather than settled by me inside the seat's own finding.

Two further risks it names, recorded without remedy: the ownership vocabulary
(*"the LAW presently treats conscripted Companions as self-sourced kit for
`SUPPORT_CARRY`, while the proposal excludes them for Charge"* — one word,
"own", carrying two different meanings in two laws, which it reads as a D4
invisible-feed exposure); and the pulse/replay ordering (*"the proposal does not
define whether the jellyfish's turn-start replay becomes 'the last card Kokomi
played,' potentially determining or overwriting the pulse before the player
acts"* — a PICK B interaction §5 did not see).

### What I take from it, and what I have not done

I have changed nothing in §2–§6 in response. The seat's read is doctrine
evidence, not an instruction, and every hole it found is either a [USER] pick or
a rule this proposal owes before an engine arm is written. What it establishes:
the design is **legal in shape** (D2 and D4 both pass on the two elements that
carry the new player-facing surface) and **illegal until amended** on a clause
list three times longer than §4's — which is exactly the answer the exercise was
run to get, before anybody built anything.

---

## 8. Revert

Branch `kokomi-kurage-memory`, from `origin/process-review-2026-08-29` at
`e352db4`. Three commits, all under `review/`: the proposal, the seat's reply
verbatim, and this file's §7 and §9. `git revert` of the range, or simply not
merging the branch, restores the tree exactly — **no shipped row, constant,
sheet, engine file or LAW line is touched by any of them.**

Nothing here changes until [USER] amends LAW. **The amendment list is §7's
eleven items, not the two this section originally claimed** — the seat's (D)
caught that and it is corrected rather than argued with. All of them are
[USER]'s alone: the delegation ladder puts LAW amendments, one-way doors and
picks between genuinely different design directions on his side of the line, and
this is all three.

---

## 9. Register moves I think are due

**I have minted and closed nothing, and I have edited no register.** This is a
list for the sitting, not an action. Next free ids for reference: `EB-191`,
`M51`, `R219`.

**Amend in place:**

- **`M50`** — its text points at `review/active/kokomi-slice-2-2026-08-29.md` §9
  PICK 2 and offers five options. Those five are withdrawn: the ask should point
  at **this** proposal, and the pick it puts is no longer "choose an accrual
  rule" but "take the Kurage-memory redesign, with picks A–E, or don't." It
  stays HELD and it stays [USER]'s.
- **`M49`** — supersede rather than answer. The pilot term it queues prices a
  bank the player spends at a moment of their choosing; under this design they
  never do (§4). If the proposal is taken, M49 closes and a new row asks for a
  *tempo* term instead.

**Mark superseded:**

- `review/active/kokomi-slice-2-2026-08-29.md` **§9 PICK 2** — superseded by
  this document, in [USER]'s own direction of 2026-08-29.
- The four slice-2 prototype rows on `docs/prototype-surface.yaml`, and the
  round-2 boards on `kokomi-slice-2-round-2`, retire under the surface's
  deletion rule **if** the proposal is taken (§4). Not before.

**Mint, if the proposal is taken** — three engineering rows, one per §6 piece,
because they gate on each other in that order:

- the **engine flag** `KURAGE_MEMORY` in both engines, default off, acceptance =
  the suite unflagged shows zero diffs and the flagged arm plays a whole fight;
- the **UI strip** — the queue faces, the Charge bar with T marked, the
  last-card-type indicator; the widest estimate in §6 and the piece with no
  precedent in the mod;
- the **bridge fields** — queue, threshold/maximum, pulse type and amount.
  This one should **ride `EB-181`** rather than open a second row: it is the
  same pin move and the same class of gap (a meter with no maximum), and
  `EB-181`'s acceptance clause already covers half of it.

**And one row the seat's read earns on its own**, whether or not the proposal is
taken as a whole: the **recursion rule** — whether a card the jellyfish plays
re-enters the memory — is an unanswered semantic the design owes, and §2's
self-bounding claim depends on it (§7).

A ruling id (`R219`) is due if [USER] takes the design, because the LAW
amendments in §7's list are a slate, not eleven separate calls.
