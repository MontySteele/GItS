# Kokomi — the Kurage's memory: a Charge redesign

**2026-08-29. Branch `kokomi-kurage-memory`, cut from
`origin/process-review-2026-08-29` at `e352db4`.** This is a document and a
review. **No engine code, no card row, no LAW line moves on this branch** — not
one shipped file is edited by it. It supersedes `git show 1f07d94a:review/active/kokomi-slice-2-2026-08-29.md`
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

> **SUPERSEDED IN PART BY §11 (v3, 2026-08-29).** This section is the v2
> mechanic and is kept as history. Where §11 disagrees with it, §11 wins.

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

> **COUNTERSIGNED (R226, 2026-08-30): SIGNED AS AMENDED BY §11.7 v3, AS PROSPECTIVE TEXT (R213).** (i) the Charge bullet lands in `LAW.md` in v3's wording ("Companions included, Status and Curse excluded"), (ii) the R80 header block in `docs/kokomi-cards.yaml` is rewritten, and v3's **two new clauses** are added to the same LAW section — the memory may hold one of her own non-Companion cards, and a memory copy is removed from combat and is **not** an Exhaust. **(iii)'s Companion-exclusion rotation clause and (iv)'s relic-face edit are NOT applied** — v3 withdrew both. Every line is marked PROSPECTIVE and binds when `C.KURAGE_MEMORY` flips; until then the shipped rule is "Charge is never spent".

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

- **`M50`** — its text points at `git show 1f07d94a:review/active/kokomi-slice-2-2026-08-29.md` §9
  PICK 2 and offers five options. Those five are withdrawn: the ask should point
  at **this** proposal, and the pick it puts is no longer "choose an accrual
  rule" but "take the Kurage-memory redesign, with picks A–E, or don't." It
  stays HELD and it stays [USER]'s.
- **`M49`** — supersede rather than answer. The pilot term it queues prices a
  bank the player spends at a moment of their choosing; under this design they
  never do (§4). If the proposal is taken, M49 closes and a new row asks for a
  *tempo* term instead.

**Mark superseded:**

- `git show 1f07d94a:review/active/kokomi-slice-2-2026-08-29.md` **§9 PICK 2** — superseded by
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

---

## 11. Version 3 (2026-08-29)

**§2–§7 above are HISTORY and are not rewritten.** This section is the design
as it now stands. Where v3 and §2 disagree, v3 wins; where §11 is silent, §2
still holds. Built on `kokomi-kurage-memory-v3`, Python only, still behind
`C.KURAGE_MEMORY`, still default off.

### 11.1 [USER]'s words — this is the spec

> "Cards must play against the same target the second time, unless that target
> no longer exists, in which case they play randomly against eligible targets.
> Companion cards only enter Memory when they themselves exhaust or are
> Transformed via Muster (so cards with Exhaust get played twice, otherwise you
> have to manually exhaust them) — thus you cannot just spam Raiden over and
> over, you get a free Raiden when you Exhaust or Muster her. This would also
> create natural synergy space for deliberately adding the Exhaust or Ethereal
> tag to cards. Charge now builds at a rate of '1 Exhaust = 1 Charge' and cards
> cost Charge equal to 3x their Cost. So 0-cost cards can autoplay for free
> (e.g. Gorou in the starter deck) and otherwise the presumption is you need to
> build Charge externally, such as through Kokomi's Skills or playing Exhaust
> cards. Sticking a card you can't afford into Memory blocks Memory until it's
> played. I don't think we need to cap this. If you load Memory with 20 cards,
> they slow-play over 20 turns … if you have the Charge. If you stack infinite
> Charge, then you still get only one play per turn. … infinites are fine as
> long as they are not trivial to pull off. Memory / Order spam is a fine win
> con as long as it's not literally the only thing Kokomi always does."

Four further rulings, taken the same day, in [USER]'s words:

> "We would be adding the card that was sacrificed for the Muster, not the new
> card - so the original face."

> "No, if the Muster prints a card that Exhausts, then it gets added as well."

> "Those should be independent mechanics."

> "Sacrificing a power seems like a bigger deal than sacrificing anything
> else." *(the Power pulse grants Charge, not Hydro)*

And the Skill pulse is **5**, on its own constant, as built.

### 11.2 Design input (advisor)

[USER]'s advisor (GPT) wrote the rule statement below and [USER] forwarded it
as the design to build. It is quoted verbatim and implemented exactly, except
where the four rulings above moved it (the Muster clause, chiefly).

> "When a Companion not originating from Memory Exhausts, remember it. A
> remembered card retains its original target and choices. At the start of
> Kokomi's turn, if she can afford the front Memory, spend its Charge cost and
> play it. Then remove that Memory from combat."

Its consequences, also verbatim: a Memory-originated play never creates another
Memory; its removal does not count as an Exhaust for Charge; it still triggers
ordinary "when you play a Companion" effects; it must not program Kurage's
Attack/Skill/Power pulse; a manually-Exhausted non-Exhaust Companion's copy is
ephemeral — after autoplay it disappears rather than entering the discard pile.
Same-target: a card played before entering Memory stores its original target;
if dead/ineligible, random eligible. Cards entering Memory without having been
played (Ethereal, manual Exhaust, Muster-direct) have no target → random
fallback. Price: three times the card's base cost on its remembered face,
including permanent upgrade changes, ignoring temporary combat discounts;
X-cost Companions ineligible for now. Status/Curse exclusion retained. Original
Companion Exhausts generate their one Charge; Memory copies do not.
Acceleration: explicit Skills "Play the front Memory" preferred over a passive
rate Power.

**Authorship of the rule**: `authored_by: [user, claude, gpt]`. The RULE is
jointly authored — [USER] specified it, the advisor wrote the statement, this
build made it total. Row-level independence is unchanged: no card row was
authored here, and nothing on any sheet moved.

### 11.3 The rule as implemented

**Two entry rules, and they are independent.** Neither function mentions the
other; neither reads what the other did. That is [USER]'s "Those should be
independent mechanics" taken as a construction rule rather than as a comment.

**RULE 1 — MUSTER** (`effects.note_kurage_muster`, called from
`effects._op_conscript`). The card **sacrificed** to the Muster enters the
memory at the moment of transformation, on its own original face, with **no
stored target** (it was never played). It does not matter what the Muster
produced or what becomes of it. Create-mode conscription sacrifices nothing and
so remembers nothing.

Consequence [USER] asked for explicitly: the memory can hold one of **her own
non-Companion cards**, because that is what a Muster usually eats. A remembered
non-Companion replays by exactly the same rules — 0 energy, price paid, stored
target or fallback — and its replay still never keys the pulse, never pays
Charge and never enrols.

**RULE 2 — EXHAUST** (`effects.note_kurage_exhaust`, called from
`refpowers.after_card_exhausted`, the one funnel every exhaust route passes
through). A Companion that did not originate from the memory enters when it
**Exhausts**, however it came to exist — drafted, Mustered or created. A
Companion that does not print Exhaust must be burned by hand (or by Ethereal)
to enrol, which is the synergy space [USER] named for the Exhaust and Ethereal
tags.

**One Muster can therefore produce TWO memories**, in order: the sacrifice at
the transformation, then the recruit when it burns. Ruled intended.

**The one enrolment door** (`effects._enrol_memory`) is the only writer of the
queue and carries the shared refusals: a card already enrolled, a memory copy,
a Status or a Curse, and an X-cost card (ineligible for now — "X" has no cost
to multiply, and pricing it off a finished turn's energy would be worse than
refusing). The **once-only guard is general**: `Card.kurage_remembered`, one
instance, one enrolment. It is the only such guard v3 keeps.

**Each entry records** (`state.KurageMemory`): card id (upgrade state
included), the remembered face's cost, the price, the stored target or `None`,
`ephemeral`, and which rule filed it.

**PRICE**: `3 × the remembered face's cost`, computed once at entry so the
strip can show it for as long as the memory is queued. Permanent upgrade
changes count. A Muster's own −1 counts on the **recruit's** entry, because the
recruit is the card that Exhausted. Temporary combat discounts are ignored by
construction — the price is read off the card, never off `combat.card_cost`.

**FUEL**: `CHARGE_PER_EXHAUST` on every Exhaust of an **original** card of
hers, her own **and** original Companions — the shipped funnel unnarrowed,
which retires v2's PICK A1. Status and Curse still pay nothing (the 2026-08-23
rotation ruling, untouched). A **memory copy pays nothing and is not an Exhaust
event at all**: `kurage_fire` clears the copy's own `exhaust` flag, so the copy
never reaches the funnel, and nothing hanging off that funnel — Burst,
`exhausts_this_turn`, the rotation latch, a relic's `damage_per_exhaust` —
pays out for a card that was never burned.

**FIRE** (`effects.kurage_fire`, called from `combat._player_turn` at turn
start): if the front's price ≤ the bank, spend it, play the front for 0 energy
through `combat.resolve_free_play` against its stored target, and remove it. At
most **one per turn**, however large the bank. A fire triggers ordinary "when
you play a Companion" effects but does **not** fill the queue, pay Charge, or
key the pulse (`state.kurage_autoplaying` plus the copy's own
`from_kurage_memory` stamp).

**BLOCK**: if the front is unaffordable, **nothing behind it fires** and the
bank holds — unspent, not lost, not applied to something cheaper. That is
[USER]'s clause, and it is distinct from an EMPTY memory, which also pays
nothing but is not a block.

**TARGET** (`effects._memory_aim`): the stored body whenever it is still alive,
even when a fresh bind would now pick another — that is the whole content of
"the same target the second time". Otherwise the fallback, and the default
fallback is **random**, expressed as `None` so the shipped forced-random roll
stays the one roll. A memory with no stored target takes the fallback by the
same line, because absence and death are the same thing to a card that has to
aim at something.

**EPHEMERAL / removal from combat** (`effects._remove_from_combat`): **every**
copy is removed from combat and reaches no pile. The advisor's statement ends
"Then remove that Memory from combat", and that is taken literally for both
kinds. This is a decision worth naming: for a copy whose original **did** print
Exhaust, the alternative is that it Exhausts again — and an Exhaust pays
Charge, which the same rule statement forbids. So `ephemeral` is **recorded and
currently behaviour-free**. It is kept because it is what the strip must show
and what a later ruling would attach behaviour to. **This goes back to [USER].**

**THE ACCELERATION KEYWORD'S HOOK** (`effects._op_play_front_memory`, OPS row
`play_front_memory`): a quarantined prototype-surface op, registered exactly
the way `spend_charge` is — no card, no sheet row, no C#. It fires the front
**outside** the automatic rhythm (it neither reads nor sets the per-turn latch)
and still pays the price, because the keyword buys rhythm and never the card.
**Provisional keyword name: "Stir"** (R179 — an ordinary word, cosmetic, listed
here as provisional and renameable for free). No card is authored, per the
brief; a Rare Power that raises the rate is likewise not authored.

### 11.4 Every constant, and its alternative

| constant | value | alternatives |
|---|---|---|
| `KURAGE_MEMORY` | `False` | the master quarantine flag |
| `KURAGE_MEMORY_COST_PER_ENERGY` | `3` | [USER]'s "3x their Cost" |
| `KURAGE_MEMORY_COST_BASIS` | `"remembered_face"` | **one basis only.** v2's `"original_print"` is RETIRED by the Muster ruling: the sacrifice enters on its own original face, so the two readings no longer differ |
| `KURAGE_MEMORY_TARGET_FALLBACK` | `"random"` | `"most_hp"` — **implemented** (v2's PICK E1 fallback; more forecastable, less what v3 asks for) |
| `KURAGE_FIRE_TIMING` | `"turn_start"` | `"turn_end"` — **implemented** |
| `KURAGE_QUEUE_CAP` | `0` = uncapped | [USER]: "I don't think we need to cap this" |
| `KURAGE_MEMORY_KEYWORD_NEEDS_SUMMON` | `True` | `False` — **implemented**. NOT a [USER] pick; a hole the build filled (see 11.7) |
| `KURAGE_FUEL_MODE` | `"exhaust_any"` | `"play_or_exhaust"` (v2's A2) — **implemented**. v2's `"exhaust_own"` (A1) is RETIRED by v3's fuel |
| `KURAGE_POWER_PULSE` | `"charge"` | `"hydro"` (v2's C1) — **implemented**. The AMOUNT is DERIVED, not picked (R212): `CHARGE_PER_EXHAUST`, i.e. a Power pulse is worth exactly one burnt card |
| `KURAGE_MEMORY_PULSE_BLOCK` | `5` | RULED. A separate constant, so the shipped `KURAGE_PULSE_BLOCK = 0` stays reachable byte-for-byte with the flag off; the Oath's `kurage_ward` still stacks on top |
| `KURAGE_EMPTY_QUEUE` | `"hold"` | an empty memory pays nothing; a *blocked* memory is v3's own clause and is separate |
| `KURAGE_TARGET_RULE` | `"follow_her_last_attack"` | governs the **pulse's** aim only now; `"random"` implemented |
| `CHARGE_PER_EXHAUST` | shipped `1` | [USER]'s "1 Exhaust = 1 Charge" is the shipped rate; the constant did not move |
| `KURAGE_THRESHOLD` | `5` | **RETIRED and unread.** v3's per-card price replaces it. Kept only so a revert to the v2 arm is a flag flip |
| `KURAGE_DURATION`, `KURAGE_PULSE_PER_CHARGE` | — | **not read** under the flag |

Where the rule lives, file and function: `effects._enrol_memory` (the one
writer), `effects.note_kurage_muster` (Rule 1) called from
`effects._op_conscript`, `effects.note_kurage_exhaust` (Rule 2) called from
`refpowers.after_card_exhausted`, `effects._remembered_price` (the 3× and the
X-cost refusal), `effects.kurage_fire` (fire, block, one-per-turn),
`effects._memory_aim` (same target / fallback), `effects._remove_from_combat`
(no pile), `effects.kurage_memory_pulse` (the pulse, Power branch now Charge),
`effects.note_kurage_play` (the pulse key and recursion rule 2 only — the queue
is gone from it), `effects._op_play_front_memory` + its OPS row (the keyword
hook), `effects.resolve_card` (the per-card target record),
`refpowers.after_card_exhausted` (the fuel), `combat._player_turn` (the
turn-start fire), `state.KurageMemory` / `state.CombatState.kurage_queue` /
`kurage_play_targets` / `Card.kurage_remembered` / `Card.from_kurage_memory`.

### 11.5 The strip's new reading

§3's strip design stands; **what it renders changes**, because the bank no
longer has one threshold.

- The Charge bar's **target is now the front memory's own price**, not a global
  T. The strip reads `Charge 5 / 9 — Raiden blocked`: the bank, the front's
  price, and the fact that the queue is blocked behind it. When the front is
  affordable the same line reads as a forecast — *this fires next turn*.
- **Each queued face carries its own price and its own target.** Under v2 every
  memory cost the same and the strip only had to draw one number; under v3 the
  strip must draw a price per card and, for a card that stored one, the body it
  will hit. A 0-cost memory should read as free, because it is.
- **The block is a state the strip must show**, not just a number that happens
  to be too small. "Blocked" is a decision the player made (they banked a card
  they cannot yet afford) and the whole legibility defence requires it be
  visible and attributable.
- **The last-card-type indicator gains a fourth reading**: the Power branch now
  shows *Charge*, not an element.

**What the bridge must expose** — §3's list, with v3's additions in bold:

1. **The queue** — an ordered list of faces, front first, **each with its
   price and its stored target**.
2. **The bank** — `amount`, and **the front's price** in place of a global
   threshold (still `EB-181`'s "a meter has no maximum" gap), plus **whether
   the queue is blocked**.
3. **The pulse** — type and amount, with **Charge** as a possible amount-kind.

### 11.6 What v3 supersedes in §5's picks

- **PICK A (the fuel source) — SUPERSEDED.** v3 is neither A1 nor A2: the fuel
  is the shipped funnel, unnarrowed, on her own cards **and** original
  Companions, at 1 per Exhaust. A1's Companion carve-out is gone. §4's "Muster's
  Charge line", which settled R216 D in the direction of removal, is
  **reversed by v3**: a Mustered Companion's Exhaust pays its Charge like any
  other. A2 stays implemented as a sweepable arm and nothing more.
- **PICK E (targeting) — SUPERSEDED for the replay.** The replay aims at the
  body its original hit; the fallback is random. E1's "most HP" survives only as
  the implemented alternative. `KURAGE_TARGET_RULE` still governs the pulse.
- **T (the threshold) — SUPERSEDED and retired.** There is no threshold. Each
  memory carries its own price at 3× its cost, so the derivation §5 asked for is
  moot and `KURAGE_THRESHOLD` is unread.
- **The starter-deck hole (§6.1 finding 11) — CLOSED.** Under v2 the starter
  deck banked at most 2 Charge against a threshold of 5 and the engine never
  fired. Under v3 it fires: see 11.8.
- **PICK B (timing) — STANDS at turn start**, now on [USER]'s own words rather
  than on a recommendation.
- **PICK C (the Power pulse) — RULED, and not as §5 recommended**: Charge, not
  Hydro.
- **PICK D (the empty queue) — STANDS at "hold"**, and gains a sibling: the
  *blocked* queue, which is v3's own clause and also pays nothing.

**RULED (R224), all three.** Nothing in the cost basis was outstanding (v3
collapsed it), and these three went to [USER] on the sitting slate — items 10
and 11, and item 5 via `M50` pick 4 — and were signed at the Claude column:

1. **`ephemeral` is recorded and inert** (11.3). Should a copy whose original
   printed Exhaust behave differently from one that did not? Every option that
   distinguishes them either pays Charge (forbidden) or files the copy in a pile
   (which "remove from combat" forbids), so the build chose uniform removal.
   **RULED (R224): keep uniform removal** — `ephemeral` stays recorded and
   behaviour-free. It is the packet's own lean and the reversible branch;
   authoring a distinguishing rule would need a new answer to the Charge
   clause first.
2. **`KURAGE_MEMORY_KEYWORD_NEEDS_SUMMON`** — does "Stir" work with no
   jellyfish on the field? Built `True` (one rule for what may act on the
   memory); `False` is one edit and makes a card printing it never dead.
   **RULED (R224): option (2) at §12.4 PICK 5 — DELETE the constant and the
   branch.** Under the base kit there is never no jellyfish, so both branches
   read the same; the stated cost is that the v3 fallback stops being one flip
   away, and that fallback is dead once the base kit is the design.
   Engineering: `EB-217`.
3. **The Skill pulse's 5 and the Power pulse's derived 1** are now ruled, but
   the *pulse as a whole* is still keyed to a type branch that no sim arm has
   moved. It is the first thing a sweep should touch after the price.
   **RULED (R224): leave the branch as built** and let the next sweep touch it
   after the price, which is the packet's own sentence. Collapsing it now would
   be a design change with no measurement behind it.

### 11.7 LAW and charter deltas v3 adds or changes against §4

§4's list stands except where v3 moved it. The deltas:

- **§4(i), the Charge bullet.** §4's proposed new text says Charge is "accrued
  only from Kokomi's own **non-Companion** cards". **v3 strikes that clause.**
  The correct new text is: *Charge is spent by the Bake-Kurage and by nothing
  else — uncapped, accrued at 1 per Exhaust of one of her own cards, Companions
  included, Status and Curse excluded; card-event-driven with no passive
  accrual (Ancient carve-out: R127).*
- **The relic's printed face.** §4 proposed adding "Companions do not pay
  Charge." **v3 deletes that sentence from the proposal**: the funnel does not
  narrow, so the face does not change at all. The relic edit §4 booked is no
  longer owed.
- **R216 D (Muster's Charge subsidy)** is settled in the direction of
  **retention**, not removal — the opposite of §4. Muster's *new* consequence is
  larger and different: a Muster now creates a memory of the card it ate, and
  the recruit creates a second when it burns.
- **A new LAW clause is owed that §4 did not book**: *the Bake-Kurage's memory
  can hold one of her own non-Companion cards.* Every existing Companion-only
  reading of the memory (including §2's) is wrong under Rule 1.
- **A second new clause**: *a memory copy is removed from combat and is not an
  Exhaust.* This is a lifecycle statement with consequences for every
  exhaust-counting row on her sheet, and it belongs in LAW rather than in a
  code comment.
- **Unchanged from §4**: the reader-row table (every proportional read still
  dies with the multiplier), `before_sun_and_moon` retiring with `kurage_amp`,
  the slice-2 arms retiring under the surface's deletion rule, and M49 being
  superseded. `read_the_current`'s `charge_at_least_10` is if anything *more*
  urgent under v3, because the bank now drains at an irregular rate.

> **COUNTERSIGNED (R226, 2026-08-30): §4's slate is signed AS AMENDED BY THIS SECTION, as PROSPECTIVE text** — v3's Charge wording and both new clauses are now in `LAW.md`; §4's Companion-exclusion rotation clause and its relic-face edit are withdrawn and NOT applied. See the line under §4.

### 11.8 What the smoke found

Five whole fights, starter deck, commander weights, seeds 1–5, flag on. **The
shape only. No number here is quotable and none is claimed** (R213 B / R215 B):
the pilot does not value the memory, so this exercises the rule and never the
decision.

- **It fires now.** Under v2 the engine never fired on the starter deck at all.
  Under v3 every one of the five fights fires — the memory rule reaches the
  opening deck for the first time.
- **The card that fires is Gorou** (`gorou_inuzaka_charge`), and it fires
  because it is cost 0 and prints Exhaust: it enrols by Rule 2 the turn it is
  played and costs **nothing** to replay. That is exactly the case [USER]
  named, and it is the whole reason the engine is now reachable at turn 1.
- **Memory plays per fight: one.** Not one per turn — one per fight. The starter
  deck contains a single Companion that Exhausts, so the queue is fed once, is
  emptied the next turn, and then reports an empty memory for the rest of the
  fight (six to fourteen such turns per fight).
- **Peak bank: two to five Charge**, and it is never spent, because the only
  memory the deck ever produces is free. The bank ends the fight holding what it
  banked.
- **Nothing was ever blocked**, because nothing priced above 0 ever entered.

**What this says, as a shape rather than a number**: v3 fixes v2's "the starter
deck cannot run the engine" hole, but it fixes it at the floor — one free replay
per fight, of the one free card. The *interesting* half of the design (banking
toward a card you cannot yet afford, and the block that punishes over-banking)
is entirely **drafted**, not printed: the starter deck cannot reach it. Whether
that is correct — a floor that teaches the mechanic and a draft that deepens it
— or too thin is a design read and it is [USER]'s.

### 11.9 What the pilot sees

Unchanged from §6.1 and worth restating because v3 does not fix it: the pilot
does not value the memory. It does not know that Exhausting a Companion banks a
free replay, does not know a Muster banks the card it ate, does not know a fire
is a turn away, does not know a front is blocked, and does not steer play order
or Muster targets to feed the queue. Under the flag the summon is priced at one
flat pulse, which understates a persistent jellyfish — the declared safe
direction to be wrong. So the flagged arm exercises the **rule** end to end and
never the **decision** the rule exists for, which is why §6 routes acceptance
through whole-fight blind play and forbids quoting a number off this arm.

### 11.10 Green

Full tier0 suite, tier05 suite, the 27 `--lane ci` lints, `gen_roster_cards
--check` (no sheet moves) and the pinned `KleeCode` build, all green, with the
flag off — which is the acceptance condition on the flag itself. No sheet row,
card yaml, LAW line or register moved, so **no drafted number moved and
`DRAFTER_VERSION` did not**. The new op is priced at a deliberate ZERO in
`tier05.draft.STATIC_OP_PRICING` with its reason, and carries its row in the
connectivity table, because both tables are total by construction.

## 12. Version 4 (2026-08-29) — the base kit

**§11 stands.** This section adds one thing to it: the jellyfish is always
there, and the starter deck carries a Muster. Everything is still behind
`C.KURAGE_MEMORY` and still default off, so nothing here has shipped.

### 12.1 [USER]'s words — this is the spec

> "I think that we will want to make Bake-Kurage part of the base kit (always
> on) rather than a separate card. So yes, we could add one Muster card to the
> base deck to teach the pattern."

That answers the question §11.8 asked. The v3 smoke found the memory rule
*working* at the starter floor and *thin*: the only card in the opening deck
that could ever enter the memory was Gorou, he is free to replay, and so the
bank was never spent and the queue was never blocked. The interesting half of
the design — bank toward a card you cannot yet afford, and be blocked when you
over-bank — was drafted, not printed.

### 12.2 What was built

**The jellyfish is on the field from the first moment of every fight and stays
for the whole fight.** No duration, no expiry, nothing to summon. It is
installed at true combat start, next to the Charge meter, because the two now
have the same lifetime — one fight. Its pulse therefore fires at every turn
end from turn 1 onward, with no card played.

**Bake-Kurage leaves the starter deck and one Muster card takes its seat.** A
card that summons what is always on the field is a card that does nothing, so
it goes; the Muster comes in so that **Rule 1** — *the card you sacrifice to a
Muster enters the jellyfish's memory, priced at three times its cost* — is
something she meets in fight 1 instead of something she has to draft into.
The deck is still twelve cards.

**The card chosen is "To the Front!"** — 0 energy, a Skill, one Muster and
nothing else printed on it. Two reasons: it is the plainest Muster on the
sheet, so what the player learns is the *rule* and not a rider; and at 0 cost
it can be played on any turn of any hand, so fight 1 always shows the pattern
rather than showing it whenever the energy happens to be spare.

**Nothing on any sheet moved.** The swap lives in code (`loader._starter_ids`),
which both the tier-0 battery and the tier-0.5 run read, so the printed
starter in `kokomi.yaml` still says Bake-Kurage and turning the flag off gives
today's deck back exactly. **No convention was bent:** "To the Front!" is a
Common, and Furina's printed starter already carries a Common
(`an_invitation`), so no Basic twin was needed and none was written. Her
starter-reserved Companion trio (Gorou plus the Sayu-or-Shinobu roll) is
untouched and still rolls normally.

`KURAGE_ALWAYS_ON = True` is the new constant. `KURAGE_DURATION` and
`KURAGE_MEMORY_KEYWORD_NEEDS_SUMMON` are now unread while the flag is on, and
are marked RETIRED-under-flag in their comments — kept at their shipped values
so that turning the base kit off restores the v3 arm whole.

### 12.3 The starter deck as it now stands (flag on)

Twelve cards, the same twelve slots:

| # | card | what it is |
|---|---|---|
| 1–4 | Water's Edge ×4 | her Strike |
| 5–8 | Coral Guard ×4 | her Defend |
| 9 | Gorou, Inuzaka All-Round Defense | Companion, 0 cost, Exhausts |
| 10 | Sayu **or** Kuki Shinobu (run-start roll) | Companion, support slot |
| 11 | **To the Front!** | **NEW** — 0 cost, Muster one card |
| 12 | Tactical Retreat | draw 1, discard 1 |

The one change is slot 11: **Bake-Kurage out, To the Front! in.**

The three Muster cards that were NOT chosen, listed so the pick is a pick:
**Call to Arms** (1 energy, Muster + draw 1 — replaces itself, but costs a
turn's energy in fight 1), **Standing Orders** (1 energy, Muster + 4 Block —
teaches the Muster while also being a Defend, which muddies what the player
learns), **Signal Arrow** (1 energy Attack, 5 damage + Muster — the same
muddying, plus it makes the Muster a rider on an attack).

### 12.4 The picks — numbered, and all five are [USER]'s

> **RULED (R224, 2026-08-30)** on the sitting slate, as `M50`, which closes:
> **PICK 1 = (2)** retire the row, *under the re-authoring*; **PICK 2 = (2)**
> retire the delta with it; **PICK 3 = (2) by way of `M60` `KO2`(1) under
> `KO1`(a)** — re-key the Casket refresh to an immediate extra pulse;
> **PICK 4** stands as [USER] ruled it (3/5 placeholder), with `EB-213` filed
> for the missing upgrade channel; **PICK 5 = (2)** delete the constant
> (`EB-217`). The two retirements attach to the Burst-fold rows `EB-199` /
> `EB-200` rather than minting their own.

Five rows still print or ride "summon the Bake-Kurage" and now mean something
different. Each one was built the **least invasive** way — nothing was
re-authored, nothing was deleted — and each is a real decision that belongs to
[USER]. The alternatives are listed, not built.

**PICK 1 — Bake-Kurage, the card itself.**
*Built:* the summon does nothing (the jellyfish is already there), so the card
is a 1-cost Skill that gains 1 Charge. It has left the starter deck, and
Basics are not draftable, so **with the flag on the row cannot be reached in a
run at all.**

1. **Leave it** (what is built): the row survives on paper, unreachable.
2. **Retire the row.** Honest — the card's job is gone. Costs her a Basic and
   a name. **RULED (R224)**, with one word added: retire **under the
   re-authoring**. With `C.KURAGE_MEMORY` off the row is still the shipped
   Basic, so this is not a deletion today; it lands with the fold (`EB-199`).
3. **Re-key it to "the jellyfish acts now"**: playing it fires an immediate
   extra pulse. Keeps the card and the fantasy, but it is a new card in an old
   row's clothes and needs authoring.
4. **Give it a new job on the memory** — e.g. make it the acceleration card
   ("play the front Memory now"), the keyword §11.3 built the hook for and
   authored no card for.

**PICK 2 — the Bake-Kurage upgrade (`kurage_turns: +1`).**
*Built:* inert, as it already was under v3 — an upgraded copy is identical to
a base one.

1. **Leave it inert** (built).
2. **Retire the delta** with the row, under pick 1. **RULED (R224)** — the
   only answer that leaves no dead upgrade row behind pick 1, and the delta is
   already inert.
3. **Give the upgrade a memory-side job** instead of a duration one.

**PICK 3 — the Tamakushi Casket link (casting her Burst refreshes the
jellyfish).**
*Built:* unchanged in code, and it now pays nothing — refreshing something
that never expires is nothing. This is her canon E-into-Q loop, and under the
base kit it is silent.

1. **Leave it silent** (built).
2. **Re-key the refresh to an immediate extra pulse**, so the Burst still
   visibly wakes the jellyfish. **RULED (R224), by way of `M60` `KO2`.** The
   pick was folded into `KO1`, and `KO1` resolved to **(a)** — under (a) the
   fold's own text says re-key the refresh to an immediate extra pulse, so
   this option is what the ruling lands on. It was recorded as CONDITIONAL
   until `KO1` was answered, never as a flat "immediate pulse".
3. **Retire the link** and say so on the relic's face.

**PICK 4 — Kurage's Oath (the `kurage_ward` Block). RULED, and BUILT.**
[USER], 2026-08-29, verbatim:

> "Let's rewrite it to '3 block per memory played, upgrade to 5' as a
> placeholder and see if it needs adjusting later."

*What the pick was:* under the base kit the pulse fires at every turn end, so
a ward that rode the pulse turned "5 Block per Bake-Kurage play" into 5 Block
per turn for free.

*What is now built:* the ward is keyed to a **memory play** and no longer to
the pulse. Every time the jellyfish plays a card out of its memory — the
automatic fire at turn start, and the acceleration keyword's ("Stir") extra
fire alike — the Oath pays. A turn where the memory is empty pays nothing, and
a turn where the front is **blocked** pays nothing either, which is the point:
a memory play is something she has to earn and can be shut out of, and a pulse
is not.

*The numbers are a placeholder, in [USER]'s own word:* **3 Block, 5 upgraded.**
No measurement is attached to either and none may be quoted from this arm.

*The mechanism, in two halves.* The **trigger** is engine, behind
`C.KURAGE_MEMORY`, at one site (`effects.kurage_fire`) that both doors pass
through — so "per memory played" is one sentence and cannot drift between
them. The **numbers** are the card's: the ward pays whatever stacks are
standing, so there is no code-side override that could disagree with a printed
face. The face itself is staged as a prototype row,
`proto_kurages_oath_memory`, on `docs/prototype-surface.yaml` — the repo's
established way to try a card face under an R213 flag. The shipped
`kurages_oath` row is untouched, and **with the flag off the ward still rides
the pulse at 5, exactly as it ships** (test-pinned as a hard requirement).

*Two things about the surface that are worth saying plainly.* It carries **no
upgrade channel** — no row on it has ever had one, the schema has no field for
it and the generator has no path for it, because upgrades live in
`docs/<character>-upgrades.yaml` keyed by shipped id. So the upgraded 5 is
recorded on the row itself and is owed to the upgrades sheet at the moment
this arm is re-authored onto her real sheet. And its authorship is recorded in
two places, because `authored_by:` is a list of model **families** (EB-190) and
[USER] is not one: the field on the row reads `[claude]`, the family that wrote
it, and the row's comment block carries the fact that matters — **numbers and
rule [USER], implementation and wording Claude**, no doctrine-seat involvement,
nothing graded.

*The shipped twin is no longer offerable under the flag, and this is the
answer to [USER]'s question about it.* He asked: **"Why does the power print 5
instead of 3, exactly?"** Because the ward's amount is read off whatever card
applied it, and the **shipped** `kurages_oath` — 5, 7 upgraded, face "per
Bake-Kurage play" — was still in Kokomi's draft pool with the flag on. A
flagged run that drafted it therefore paid 5 per memory play under text that
cannot bind, which is a defect (D4), not a balance question. Neither sheet may
move, so the fix is on the **offer** side: under `C.KURAGE_MEMORY` the shipped
id is substituted for `proto_kurages_oath_memory` in her offerable pool, at the
same rarity and the same weight. The seam is one function next to the starter
swap (`loader._pool_substitutions`, the twin of `_starter_ids`) applied at the
single source of truth for what a character can be handed
(`rewards.character_pool`), which fight rewards, the shop, every event card
screen and the tier 0.5 drafter all read and nothing bypasses. With the flag
off it returns `{}` and the pool is byte-identical, test-pinned. The one thing
this costs: the prototype has no upgrade row, so the substituted Oath cannot be
upgraded at a campfire — which is honest while the upgraded 5 is still owed to
a sheet, and it goes away when the arm is re-authored. **Filed by R224 as
`EB-213`**, so the gap is a row rather than a paragraph: any rerun that wants
to see the upgraded 5 needs it fixed first.

*Still open, and small:* whether 3/5 wants adjusting, which is what [USER]
reserved.

**PICK 5 — `KURAGE_MEMORY_KEYWORD_NEEDS_SUMMON`.**
*Built:* retired-under-flag. It asked "does the acceleration keyword work with
no jellyfish?", and under the base kit there is never no jellyfish, so both
answers read the same.

1. **Leave it retired-under-flag** (built).
2. **Delete the constant** and the branch with it, accepting that the v3 arm
   is then no longer one flip away. **RULED (R224)** — the stated cost is
   accepted, because the v3 fallback is dead once the base kit is the design.
   Engineering: `EB-217`.

*(Nereid's Ascension is named as a "refresh" row in the brief; on the sheet it
carries no summon leg at all — its only Kurage-adjacent term is a Charge read,
which §11.7 already books. Nothing is owed there.)*

### 12.5 The smoke, and it is a SHAPE

Five whole fights, the new starter deck, commander weights, seeds 1–5, flag
on. **No number below is quotable and none is claimed** (R213 B / R215 B): the
pilot still does not value the memory, so this exercises the rule and never
the decision.

- **Rule 1 fires in fight 1, in all five.** The Muster ate one of her own
  cards and that card entered the memory at three times its cost — as early as
  turn 1 in three of the five, and by turn 8 in the other two. This is the
  thing the base kit exists to do, and it does it.
- **The block now happens.** Four of the five fights hit at least one blocked
  turn — a front priced at 3 against a bank of 0 to 2 — and one fight was
  blocked on eight separate turns. Under v3 the starter deck could not be
  blocked at all.
- **The bank is now spent.** Peak bank across the five was three to four
  Charge, and every fight spent at least once (one spent twice). Under v3 the
  bank was never spent, because the only memory the deck could produce was
  free.
- **Memory plays per fight: two to six**, against v3's flat one. The queue
  fills from both rules now — roughly two to five Muster entries and three to
  six Exhaust entries per fight — and empties at one card per turn.
- **The prices the deck produces are 0 and 3.** Gorou and the Companions it
  Musters up are free or cheap; a sacrificed Water's Edge or Coral Guard is a
  3. One entry priced at 6 appeared once across the five.

**What this says, as a shape:** the base kit does exactly what §11.8 said the
starter was missing — the bank, the afford and the block are all printed now.
Whether *one* Muster is the right dose, and whether the block should bite this
often in fight 1, are design reads and they are [USER]'s.

### 12.6 What the C# mirror must change — a checklist

For the parallel arm on `kokomi-kurage-memory-cs`. Every item is behind the
same quarantine flag.

1. **Install the jellyfish at combat start**, not on a card. Mirror of
   `combat.run_fight`: at true fight start, for Kokomi only, put the
   Bake-Kurage on the field with no duration. It must be there before the
   first turn opens and must not be removable.
2. **Never expire it.** Remove every decrement / countdown path under the
   flag; the turn-end pulse must not spend a turn of anything.
3. **Fire the pulse at every turn end** from turn 1, with nothing played and
   nothing summoned.
4. **Emit its own signal, not a summon.** The install is not a summon, and a
   listener counting summons must not see one that no card paid for.
5. **Swap the starter deck in code, not on the sheet.** Bake-Kurage out, "To
   the Front!" (`to_the_front`) in — one card for one card, twelve cards
   total, at whatever the C# equivalent of a single starter-list seam is, and
   it must be the *only* such seam so the mod and the sim cannot disagree. The
   support-Companion roll must still compose with it.
6. **Leave the printed sheet alone.** The generated card row for Bake-Kurage
   stays; the mod's starter list is what moves, under the flag.
7. **Make the summon op idempotent under the flag** (it sets a bit that is
   already set) and keep the card's second leg, `gain 1 Charge`.
8. **Neutralise the duration upgrade** (`kurage_turns +1`) under the flag.
9. **Neutralise the Tamakushi Casket / Garment refresh** under the flag — it
   must not extend, re-arm, or re-summon anything.
10. **Do not touch Kurage's Oath's number**, but treat its face as owed: the
    ward is now paid per turn, not per play, and the C# face still says
    otherwise. The face fix waits on pick 4.
11. **The strip** (§11.5) gains one reading: there is no "no jellyfish" state
    any more, so the strip is always live for Kokomi and must never render an
    absent-summon state.
12. **The bridge** must expose the install as a fight-start fact, so a blind
    run can see the jellyfish before turn 1 rather than inferring it from the
    first pulse.
13. **Move Kurage's Oath's ward off the pulse and onto the memory play**
    (§12.4 pick 4, RULED). One trigger site covering both doors — the
    automatic turn-start fire and the "Stir" fire — paid when the memory
    actually plays, so an empty or blocked memory pays nothing. Under the
    flag only: with the flag off the ward must still ride the pulse.
14. **Give the prototype Oath its own face text**, which the sim's codegen
    cannot do from here: `gen_klee_cards` renders a Power's description per
    POWER ID, so `kurage_ward` prints one string shared with the shipped
    Oath, and moving it would move a shipped release face and make it false
    with the flag off. The mirror needs its own power (or its own
    description channel) for the prototype row. The face must read:
    **"Whenever the Bake-Kurage plays a card from its memory, gain 3 Block."**
    — 5 upgraded. Until it does, the generated prototype card carries the
    shipped pulse wording and is wrong on its face.
15. **Substitute the prototype Oath for the shipped one on every offer
    surface**, under the flag only (§12.4 pick 4). Same seam pattern as the
    starter swap at item 5: ONE gate, in code, with both sheets untouched, and
    it must be the only one — the mod's reward roll, its shop stock and any
    other place a card is offered must read the same substituted pool, or the
    mod and the sim will disagree about which Oath a flagged run can draft.
    The substitution keeps the card's **rarity slot and weight**; it is a face
    swap, never a tier move. With the flag off the shipped Oath is the only
    Oath offered and the prototype is unreachable, exactly as today.

### 12.7 Green

`python -m tools.run_lints --lane ci` — **OK: 27 lint(s) passed**. Full tier 0
suite **3556 passed, 46 skipped, 12 xfailed**; full tier 0.5 suite **794
passed** — both with the flag off, which is the acceptance condition on the
flag. `gen_roster_cards --check` reports **all three profiles up to
date** -- no sheet moved, because the starter swap is code and every YAML
file is byte-identical. Twelve
mutations were run against the new test file and all twelve were caught. No
LAW line, register row, sheet row or drafted number moved, so no stamp moved.

**Pick 4's build (step P) re-ran all of it**: the ci lane again reports OK on
27 lints, and the prototype-codegen lint required the surface's generated C#
to be regenerated for the new row, which was done with the tool rather than
by hand. Eight further mutations were run against the ward tests and all
eight were caught. **The §12.5 smoke was not re-run and does not move**: no
card in the starter deck grants `kurage_ward`, so the Oath cannot appear in
a starter fight by any route.

## 13. The DRAFT prediction slate for the sealed blind run

**DRAFTED, UNRUN, UNCOUNTERSIGNED.** Drafted by Claude from written design
intent — §11.1 and §12.1 are [USER]'s words and are the spec, §11.3 is the rule
as built, §12.4 pick 4 is [USER]'s ruling on the Oath — and committed as its own
commit, labelled DRAFTED, **before any seed run**, per R212(2) and
`EXPERIMENTS.md`'s pre-registration rule. It is offered for batch countersign.
The grade goes in blind. Nothing below may be revised against the run that
grades it (D5, R101b): a moved world means re-drafting the affected slots and
disclosing the diff, never re-signing.

*Pointer, added 2026-08-30: this slate is no longer unrun — §13.8, THE SEALED
RUN — GRADED 2026-08-29, is its grade, and §13.9 carries `KURAGEMEM002`'s
rerun. The banner above is the pre-registration as registered and is not
edited (R101b).*

The arm has no card row and never had one (`docs/prototype-surface.yaml`, the
declared-not-rowed block), so nothing here bumps a stamp, moves a sheet or
touches a drafted number.

### 13.0 DISCLOSURE — the world moved between the draft and the run (R212)

Written before the first sealed seed was embarked, and committed before it.

The slate was drafted against an earlier `+proto` build. Three defects were
found and fixed after the draft and before the run, and the build the sealed
run executes on is **`0.2.1456+proto`**, not the build the slate was written
against:

1. **`EB-194`** — the loc merge called `PrototypeCards.For` from a Harmony
   postfix on `LocManager.Initialize`, which forced the eager `PrototypeRoster`
   initializer against an empty `ModelDb` and poisoned the type for the
   process, so no run of any character could start. Fixed by moving the merge to
   `KokomiOffPoolCards.InjectPrototypeLoc` and making the generated roster lazy.
2. **`EB-196`** — `KurageMemory.ResetForCombat` was called from
   `KokomiResourceHooks.Subscribe`, which a combat re-invokes on every hook
   broadcast, so the memory was cleared between every pair of hooks and an entry
   filed by one hook was gone before the next could read it. Fixed by moving the
   per-fight clear to `BeforeCombatStart`, plus a `SafeTitle`-style guard on the
   `ephemeral` read in `Enrol`.
3. **`EB-197`** — the Bake-Kurage's buff printed *"Lasts {Amount} more turn"*,
   a countdown nothing under the flag ticks. Under `PROTOTYPE_CARDS` it now
   prints the lifetime it has. The release face is byte-identical.

**P1 through P6 STAND AS WRITTEN, and are not re-drafted.** Each slot describes
the arm's DESIGNED behaviour — the strip's front entry and its price (P1), the
`blocked` / `fires_next` pair (P2), Rule 1's sacrifice-enters (P3), the blocked
state read as a state (P4), the Oath's per-Memory-play condition (P5), and the
stored-target aim (P6). None of the three fixes changes a stated mechanism:
`EB-194` was a boot-order regression that let no run start at all, `EB-196`
restored a queue that could never hold anything to the rule §11.3 already
states, and `EB-197` corrected a face no slot grades. The fixes made the
predicted behaviour **observable**; they did not alter what was predicted. Under
R212 that is a disclosure, not a re-signature: nothing below is re-signed, no
threshold, denominator or falsifier is touched, and the slate remains the one
committed DRAFTED before any seed run.

One consequence worth naming so it is not read as a revision: §13.6's first Gate
B run could not reach the BLOCKED or FIRES-NEXT states, so P4 was recorded there
as UNGRADEABLE. On `0.2.1456+proto` all three strip states were observed (Gate B
re-run, fresh seed `YU4EBKU3XHEG`, which is **not** one of the sealed seeds —
`KURAGEMEM001/002/003` were UNSPENT at the moment this block was written). P4's
prediction, threshold and unreached branch are exactly as drafted; only its
reachability changed.

### 13.1 The decisive question

**Can a blind reader, from the page alone — the strip, the hand, the bank —
plan a Muster or an Exhaust toward a Memory play they can afford, see when the
front is blocked and what would unblock it, and treat spending versus holding
Charge as a decision rather than an odometer?**

That is a D2 question (*every persistent resource and every automatic engine
must feed a decision the player can steer: timing, targeting, placement,
acquisition, conversion, or forgoing*) welded to a D4 one (*at the decision
point the player can perceive and forecast the consequences that matter*). The
queue is an automatic engine. If the player only watches it, D2 fails and the
mechanic is v2's threshold with more arithmetic.

**The falsifier, stated so it can bite:** the run is a MISS on the decisive
question if the tester's own transcript, over a whole fight, never once names
the front memory *before* it fires and never once attributes a play of theirs
(a Muster, a deliberate Exhaust, a held Charge) to the queue — that is, if
every mention of the jellyfish is a report of something that already happened.
A tester who reads the strip accurately but never acts on it falsifies D2 while
leaving D4 standing, and the slate is built to tell those two apart: P1, P2, P4
and P6 are D4 slots, P3 and P5 are D2 slots.

**What the instrument can see.** Whole-fight blind play only. A staged turn
cannot see this arm at all: a per-turn clock, a queue that must be filled before
it can fire, and a block that is a consequence of an earlier turn's banking are
all cross-turn objects. The sim cannot see it either — §11.9 and §12.5 say why:
the pilot does not value the memory, does not know a fire is a turn away and
does not steer Muster targets, so the flagged sim arm exercises the RULE and
never the DECISION. **No sim prediction is registered here and no number from
either smoke is quotable** (R213 B / R215 B).

### 13.2 The six slots

Each slot names the prediction, the threshold that grades it, what falsifies
it, the one-way error direction where there is one, and the decision the
outcome changes (R206). "Graded turn" means a player turn in the sealed
transcript on which the tester wrote anything at all; the denominators are
fixed here, before the run, and are not renegotiated afterwards.

| # | slot | prediction, with its threshold | falsifier / one-way error direction | the decision each outcome changes |
|---|---|---|---|---|
| **P1** | **The front entry and its price, off the page, without a rules box.** Can the tester name the card at the head of the memory and what it will cost, from the strip alone? | **YES on at least 4 of the first 5 graded turns with a non-empty queue.** The strip prints `Charge {bank} / {price} — {name} {state}` and then one numbered line per entry with its own price and its aim; a 0-cost memory prints `free`. Naming is cheap when the line is drawn. | **Falsified** by a stated price that disagrees with `queue[0].price`, or by "I cannot tell what is queued", on 2 or more of those 5. **One-way:** err toward printing MORE — a price shown on both the reading and the queue line is redundancy, a price shown on neither is D4. | Below threshold, the strip is re-drawn before anything else in the arm is judged, and the pair read is suspended: a rule read off an illegible strip grades the strip. |
| **P2** | **Fires next turn, or blocked.** Asked to say what the jellyfish will do at the start of her next turn, does the tester get it right? | **CORRECT on at least 5 of 6 graded turns where the queue is non-empty**, counting a turn as correct when the tester's stated expectation matches the `blocked` / `fires_next` pair the bridge carried for that turn. | **Falsified** by 2 or more wrong calls, and *especially* by a wrong call in the FIRES direction — predicting a fire that did not happen. **One-way:** a tester who wrongly expects a block is pessimistic and loses nothing; a tester who wrongly expects a fire has been promised something the engine did not owe, which is D4's "misleading calculated display". | A miss in the FIRES direction sends the reading string back (the state word, and whether "fires next turn" should carry the card's aim). A miss only in the BLOCKED direction is a smaller finding and goes to the strip's wording, not to the rule. |
| **P3** | **Planning INTO the memory.** Does the tester plan a Muster or a deliberate Exhaust *and state the Memory consequence* — "this puts X in the queue at price Y", "I burn this to bank the Charge for the front" — rather than playing the card for its printed body alone? | **At least 3 of 10 graded turns** carry such a plan, and **at least one of them is a Muster** (Rule 1: the sacrifice enters, not the recruit — the half of the rule nothing on the card's face says). | **Falsified at 0**: a run where the tester never once plays toward the queue is the conveyor reading, and D2 fails on the arm as built. **One-way:** none — this slot is symmetric and is the arm's central bet. | 0 of 10 reopens the teaching surface, not the rule: the starter Muster's dose (§12.3 slot 11, and the three Musters not chosen), and whether Rule 1 needs a printed line anywhere. 3 or more says the base kit teaches the pattern and the next question is dose, which is [USER]'s. |
| **P4** | **The block, and what unblocks it.** On a turn where the front is unaffordable, does the tester (a) say the memory is BLOCKED, distinctly from empty, and (b) name a play that would unblock it — Exhaust something for Charge, Muster, or hold and bank? | **YES on the FIRST blocked turn of the run**, both halves. One occurrence, not a rate: the block is a state the strip prints by name (`(blocked)` on the front line, and the state word in the reading), so the first one either lands or the display does not work. | **Falsified** by "not enough Charge yet, I will wait" with no named source of Charge — that is the odometer reading of a block, and it is the exact failure D2 names. Also falsified by conflating blocked with empty. **One-way:** err toward the block being LOUDER; an over-marked block costs a line of text, an unmarked one costs the whole legibility defence. | Half (a) failing sends the empty-vs-blocked distinction back to the strip. Half (b) failing is the more serious of the two: it says the Charge sources are not discoverable from the page, and the acceleration keyword ("Stir", §11.3, provisional under R179) stops being optional. |
| **P5** | **The Oath reads per-Memory-play, not per turn.** With `proto_kurages_oath_memory` in the deck, does the tester expect Block on a turn the memory FIRES and expect NOTHING on a turn it is empty or blocked? | **The tester states the no-pay case at least once** — an empty or blocked turn on which they do not expect the Oath's 3 Block — across the whole run. | **Falsified** by an expectation of Block on an empty or blocked turn, at any point. That is the pulse reading surviving in the player's head, and it is the defect the whole pool substitution exists to prevent. **One-way:** err toward the face being explicit; the card may over-state the condition, it may never under-state it. | A falsified P5 with the CORRECT face deployed says the wording is wrong and §12.6 item 14's string goes back. A falsified P5 with the SHIPPED pulse string deployed (see 13.5's eyes-on) grades nothing and the slot is void — the run did not carry the card the slot is about. |
| **P6** | **The automatic play's aim.** Over the whole fight, does the tester predict the target of an automatic Memory play correctly at least once — the same body the card originally hit while that body lives, and a random eligible body otherwise? | **At least ONE correct advance call**, and it must be an advance call: the aim named before the fire, not recognised after it. The strip prints the aim on every queue line, `random` where the memory stored none. | **Falsified** by no advance call at all across the run (the rule is invisible), or by a stated expectation of a *fresh* bind — "it will hit whatever I would hit now" — on a memory whose stored target is still alive. **One-way:** none. | No advance call anywhere sends the aim to the strip's front line rather than the queue lines. A wrong-direction call (fresh bind expected) says `KURAGE_MEMORY_TARGET_FALLBACK`'s alternative, `most_hp`, is worth its own arm — more forecastable, less what [USER] asked for — and that is a design pick for [USER], not an integration's. |

**Slot dependencies, declared in advance.** P2 and P4 are only gradable on turns
the queue is non-empty, and P5 only if the Oath is drawn and played. If a run
produces no blocked turn at all, **P4 is UNREACHED, not PASSED** — and an
unreached P4 is itself a finding about the base kit's dose, since §12.5's shape
says four of five starter fights hit at least one block. The same holds for P5
if the card is never drawn: unreached, never inferred.

### 13.3 Contamination

**Two starter smokes have already been read by the drafter**: §11.8 (v3, five
fights, starter deck, seeds 1–5) and §12.5 (v4 base kit, five fights, new
starter deck, seeds 1–5). Both are disclosed here in full because reading them
is what makes this paragraph owed.

**No slot's PREDICTION is set by either smoke, and neither could set one.** Both
are pilot runs, and §11.9 is the reason: the pilot does not value the memory, so
neither smoke contains a single instance of the thing every slot above grades —
a reader looking at a strip and saying what will happen. A smoke that cannot
produce the observable cannot foretell it.

**What the smokes DO inform, named exactly, and why it is not contamination.**
Three thresholds take their DENOMINATORS from §12.5's shape, and nothing else:

- **P3's "10 graded turns" and "at least 3".** §12.5 found two to six memory
  plays per fight and roughly two to five Rule-1 entries, so ten graded turns is
  a window in which the opportunity to plan into the queue exists several times
  over. The smoke sets the *window*, not the *rate*: it says the tester will be
  offered the chance, and says nothing about whether a human reader takes it.
- **P4's "the FIRST blocked turn", and its declared-unreached case.** §12.5
  found four of five fights hitting at least one blocked turn (one hit eight).
  That is why P4 is written as a single occurrence rather than a rate, and why
  its unreached branch is declared rather than left to be argued afterwards.
- **P2's "6 graded turns with a non-empty queue".** §12.5's queue empties at one
  card per turn and refills from both rules, so a six-turn window is reachable.

Those are reachability facts about the RULE — does the event occur at all —
taken from a source that cannot see the DECISION being graded. Deriving a
denominator from them is the opposite of the harm pre-registration guards
against: it stops a slot being written that the run could not reach, and it is
written down here, before the run, rather than discovered afterwards. **No
number from either smoke is quotable** (R213 B / R215 B), none is repeated as a
prediction, and no smoke number appears in any threshold above — the
denominators are round numbers chosen to sit inside the smoke's shape, not
copied off it.

**One further disclosure.** The drafter also read §12.4 pick 4's full build
narrative, including the pool substitution and the fact that the generated
prototype face currently carries the shipped pulse wording. That is what P5's
void branch is for: the slot names its own invalidation condition rather than
being quietly graded against the wrong card.

### 13.4 Graders, and where independence actually holds

Independence is by MODEL FAMILY, author against grader (R217 C, EB-190). The
roles are fixed at two — Claude authors, GPT grades and reviews — and this arm
is the awkward case, so it is written out rather than asserted.

**The two halves have different authorship, and the surface already records it.**

- **The card row** `proto_kurages_oath_memory` carries `authored_by: [claude]`.
  Numbers and rule [USER]'s, implementation and wording Claude's, no seat
  contribution. So **the Codex seat (GPT) is a clean independent grader on P5**,
  and `seat.py`'s refusal permits it because the row does not list the seat's
  family. The C# specifics — the strip's strings, the bridge fields, the face
  override — are likewise Claude-authored, so the GPT seat is independent on
  every display slot: **P1, P2, P4, P6**.
- **The RULE arm** carries `authored_by: [claude, gpt]` in its declaration
  block: [USER] specified it and made four rulings, Claude implemented it and
  made it total, and [USER]'s advisor (GPT) wrote the rule statement that was
  forwarded as the design. **Both families are inside the rule.** The arm has no
  row, so `seat.py` has nothing to key on and will refuse nobody — the
  separation here is doctrinal, not mechanical, and it has to be stated.

**Therefore, and this is the whole protocol:**

1. **The tester is the Codex seat (GPT).** The author's own model family is
   refused as tester (R217 C) and the design is Claude's, so a Claude-family
   model may not play this run.
2. **The GPT seat grades P1, P2, P4, P5 and P6** — the display and row slots its
   family did not write.
3. **A fresh Claude reads P3** — the rule-level slot, where the GPT family
   supplied the rule statement — against the sealed transcript, **with its
   family marked in the record** and with the honest limit written beside it:
   Claude implemented that rule, so this read is independent of the *statement*
   and not of the *implementation*.
4. **Both reads are recorded, each labelled with its family**, and neither is
   presented as clean. **"Fresh Opus grades it" is not the general rule and must
   never be written down as one** — it is this arm's least-bad allocation given
   that no third family exists and none is being added.
5. Seat testimony is iteration feedback, never validation, never balance
   evidence, never approval (R217 G).

### 13.5 The run recipe

For the agent who runs this once the game is free. **Everything below runs from
the art-bearing main checkout, with the game closed at the start; none of it
runs from a worktree.** This packet's own branch touches no build.

**1 — the `+proto` dev deploy.** The arm is quarantined behind the mod's
prototype compile switch, and the rule's C# seams sit inside `#if
PROTOTYPE_CARDS`, so an ordinary build does not contain the rule at all.

```
.venv/Scripts/python tools/gen_prototype_cards.py --check
klee-mod\build\deploy_proto.ps1
```

`deploy_proto.ps1` is `deploy.ps1` plus the staleness gate,
`-p:PrototypeCards=true`, and a package stamped `MAJOR.AUTO+proto`
(`+proto.dirty` when dirty). It runs the same `validate.ps1` whole;
`-PrototypeBuild` relaxes exactly one rule, S3's acceptance of the `+proto`
mark. **The `+proto` mark in the in-game version is the confirmation that the
rule is present** — `embark --arm` refuses a build without it. **Restore the
release build with `klee-mod\build\deploy.ps1` before any measured run, handoff
or co-op session**; the absence of `+proto` is that confirmation.

**2 — the arm id.** The Kurage's memory is **declared, not rowed**: it authors
no card, so it has no `proto_` id and cannot be named to `--arm`. It is carried
by the `+proto` build itself. The one row this chain adds is the Oath:

```
--arm proto_kurages_oath_memory
```

`--arm` grants that row into the STARTING DECK (`give_card` `pile: "deck"`), so
the tester meets the card the pools quarantine. It is what makes P5 reachable
rather than left to a reward roll; without it the pool substitution would still
make the Oath draftable under the flag, but on a roll nobody can pin.

**3 — the embark.**

```
python -m understudy.seat check
python -m understudy.embark --character kokomi --arm proto_kurages_oath_memory --seed <pinned>
python -m understudy.blindplay observe
python -m understudy.blindplay session --max-actions 60 --max-wall-s 5400
python -m understudy.embark --teardown
```

**4 — the seeds, pinned here, before the run.** Three, in this order, one run
each, taken in order and not re-rolled:

| order | seed | what it is for |
|---|---|---|
| 1 | `KURAGEMEM001` | the graded run — P1 through P6 |
| 2 | `KURAGEMEM002` | the second run, taken only if run 1 terminates before P4 is reachable (no blocked turn) or before the Oath is drawn |
| 3 | `KURAGEMEM003` | reserve, same condition |

The read-back still decides what is recorded (R95): `embark` reads the run seed
BACK off the wire and that is what the sealed record carries. **If the game
refuses a chosen seed**, the operator embarks without `--seed`, records the
rolled seed and **discloses the deviation in the record before any observation
is read** — a rolled seed disclosed up front is honest; a rolled seed
discovered afterwards is not.

**5 — what "sealed" means.** Nobody reads the record before the grade is in.
The session lands in `understudy/logs/blindplay/` (gitignored — the prompts
inline the screens and the rollout carries a third party's system prompt); the
committed artifact is `review/qa/blindplay/<session>/record.md`, and it is
written and committed **before any grader opens it**. The identity block carries
model, codex version, the deployed mod build and the game build each read OFF
DISK and labelled with the file it came from (`mods\klee\manifest.json` and
`release_info.json` — never the bridge's health payload, which reports the
vendored bridge's version and not ours), the run seed read back off the wire,
the prompt sha256, the action count and the termination reason, with the
tester's records verbatim under the R217 G label.

**Three things the record must carry that are specific to this arm** (§6's list,
restated because the slate depends on them):

- **the arm was actually reached, named** — the `--arm` grant report, and the
  Oath appearing in the tester's hand or deck;
- **the flag state the build carried.** Note that **T no longer exists**: v3
  retired `KURAGE_THRESHOLD` and each memory carries its own price at 3× its
  cost, so what the record pins in T's place is `KURAGE_MEMORY` on (the `+proto`
  mark), `KURAGE_ALWAYS_ON` on, `KURAGE_MEMORY_COST_PER_ENERGY = 3` and
  `KURAGE_MEMORY_PULSE_BLOCK = 5`;
- **at least one turn where the tester stated IN ADVANCE what the jellyfish was
  about to play.** If no transcript contains that sentence, the legibility claim
  is unevidenced however the fights went — which is P2 and P6 restated as a
  record requirement.

**6 — the pair read.**

```
python -m understudy.seat review <prompt-file> --out review/qa/<name>.md
```

Not blind, read-only at the repo root: the sealed record and this §13 go to the
seat as the prompt, slot by slot, with the prompt kept beside the reply and its
sha256 recorded, the way the slice-1 pair read was. The seat answers the slots
its family may grade (13.4); the fresh-Claude read of P3 is taken separately and
filed beside it with its family marked. **A replay that contradicts a form is
the finding, not a correction** — nothing is re-graded and no answer is edited.

**7 — the two eyes-on items owed at that deploy.** Both are [USER]'s, both are
looked at once the dev build is up and before the tester is let in:

- **The prototype Oath's face.** `gen_klee_cards` renders a Power's description
  per POWER ID, so `kurage_ward` prints one string — *"Each Bake-Kurage pulse
  also grants {X} Block."* — shared with the shipped Oath, and moving it would
  move a shipped release face and make it false with the flag off. §12.6 item 14
  owes the mirror its own power or its own description channel. **What must be
  seen on the deployed card:** *"Whenever the Bake-Kurage plays a card from its
  memory, gain 3 Block."* If the deployed card still prints the pulse string,
  **P5 is VOID** (13.2) and the run grades the other five slots. This is also
  the BaseLib string-order trap in its usual clothes: a description override is
  not trusted until it has been seen to FAIL — confirm the shipped `kurages_oath`
  still prints the pulse string on a release build in the same sitting, or the
  override has proved nothing.
- **The strip's look.** The gauge draws `Reading()` — `Charge {bank} /
  {price} — {name} fires next turn|blocked`, or `Charge {bank} — memory empty`
  on an empty queue — and then `StripText()`'s numbered lines, one per entry:
  `{n}. {name} — {price} Charge|free — {aim}`, with `  (blocked)` on the front
  when the bank cannot pay it. Every slot above assumes those lines are on
  screen and legible at the size they are drawn. Eyes-on is whether the block
  mark reads as a STATE rather than as punctuation, and whether `memory empty`
  and a blocked front are distinguishable at a glance — P4 grades the tester on
  exactly that distinction, so a strip that fails it here fails the slot before
  the run starts.

### 13.6 Pre-tester gates — RUN 2026-08-29

Run on the re-verified pin (`release_info.json` v0.111.0 / `41cef1ea`;
`appmanifest` buildid `24724944`, `BetaKey public-beta`; Workshop `3737335127`
BaseLib v3.4.5), game closed at the start, from the art-bearing main checkout.
**Installed stamp: `0.2.1441+proto`, `validate: OK` on the full gate.** No
sealed run was started and the pinned seeds `KURAGEMEM001/002/003` are unspent.

**The first attempt at this deploy could not start a run at all**, for any
character: §12.6 item 14's loc merge called `PrototypeCards.For` from
`InjectLocStrings`, a Harmony postfix on `LocManager.Initialize` that runs
before any mod card model exists, which forced the eager `PrototypeRoster`
initializer against an empty `ModelDb` and poisoned the type for the process.
That is `EB-194`, fixed before these gates ran: the merge moved to
`KokomiOffPoolCards.InjectPrototypeLoc` (models present, R4's read-back kept)
and the generated roster became lazy per character. Both locks were **seen to
FAIL against the pre-fix build first** —
`The_prototype_roster_survives_a_touch_with_an_empty_model_db` reproduced
`TypeInitializationException ---> KeyNotFoundException: The given key
'CARD.PROTO_ITTO_SUPERLATIVE_SUPERSTRENGTH_EITHER' was not present in the
dictionary`, and `Loc_injection_never_touches_the_prototype_surface` reported
`Assert.DoesNotContain() Failure: Filter matched in collection … "PrototypeCards.For"`
— then green on the fix. **The §12.7 smoke was re-run this time**, which is the
step whose absence let the regression ship: 213 C# tests with the flag on, 163
with it off, tier 0 **3752 passed / 12 xfailed**, **28 lints OK**,
`gen_prototype_cards --check` up to date.

#### Gate A — the prototype Oath's face: **PASS**

Read where the player reads it: the card in hand, on a Kokomi run embarked
`--arm proto_kurages_oath_memory` (seedless; a gate check, not the sealed run).
Verbatim, from `review/qa/eb194-gates/gateA-oath-in-hand.md`:

```
- **Kurage's Oath** — cost 1, power
    Whenever the Bake-Kurage plays a card from its memory, gain 3 Block.
```

That is 13.5 item 7's required string exactly, so **P5 is not VOID**. The
override is now trusted in the way the Klee protocol asks for: it was seen to
FAIL — on the pre-fix build it never ran at all — and is now seen to run.

The control side holds. The shipped `kurages_oath` still prints the pulse
string, `"Each [gold]Bake-Kurage[/gold] pulse also grants {PowerAmount:diff()}
Block."` (`Cards/Kokomi/Generated/KuragesOath.cs:41-45`), and the generator
emits that identically in both builds. It was read from the release-build
generated source rather than from a rendered card, because under item 15's
substitution the shipped Oath is unofferable on a `+proto` build and cannot be
brought on screen there.

#### Gate B — the strip: **PARTIAL. One state of three observed.**

**Observed, verbatim** (`review/qa/eb194-gates/gateB-state1-strip-empty.md`),
present from turn 1 with nothing played, on the base kit:

```
## The Bake-Kurage's memory

- The Bake-Kurage is on the field for the whole fight. Nothing summons it and nothing removes it.
- Charge 0 — memory empty
- (the memory is empty)
```

**The base-kit wire facts are confirmed** (`gateB-wire-basekit.json`, off
`/api/v1/singleplayer`, `player.kurage_memory`): `base_kit: true`,
`summon: true` at fight start, `empty: true`, `queue: []`,
`reading: "Charge 0 — memory empty"`. The starter reads twelve cards plus the
granted Oath; `to_the_front` is in it and `bake_kurage` is not — the swap at
item 5 is live.

**The other two states were NOT reached, and that is the finding.** Across two
whole fights the queue never took a single entry. The plays that should have
fed it did not: **Gorou — Inuzaka All-Round Defense** ("Deal 4 damage.
Exhaust.") moved the bank `Charge 0 → 1` and left `memory empty`; the starter
Muster **To the Front!** transformed Coral Guard+ into **Raiden Shogun — Musou
no Hitotachi** ("Exhaust") and playing it also left the queue empty. So
`fires next turn` and `(blocked)` were never rendered, and **P4's question —
whether a blocked front reads differently from `memory empty` at a glance —
is UNGRADED**. On the evidence here the C# mirror prints the strip but nothing
enters the memory; §12.6's entry rules (items 1–4, 13) are the place to look.
Stated as observation, not diagnosis: I did not read the C# entry path.

Two smaller things seen on the same screens, both eyes-on calls rather than
defects I should rule:

1. The Bake-Kurage's buff still prints **"Lasts 1 more turn."** §12.6 item 2
   says never expire it and item 8 says neutralise the duration upgrade; the
   strip's own line says the opposite in the same frame ("on the field for the
   whole fight"). Two surfaces disagree about the same creature.
2. The strip prints **"At the end of this turn the jellyfish will do nothing,
   because you have played no card this turn"** on turns where cards *had*
   been played.

#### Gate C — the Sparks badges (new, captures only)

Klee embarked on the same build, `--arm proto_spark_priced_strike --arm
proto_spark_priced_draw`. One hand carried both wanted states at once, with the
bank at 1 Spark: **Ka-pow!+** — *"Spend 1 Spark. Deal 7 damage."* — affordable,
and **Rummage** — *"Spend 3 Sparks. Draw 3 cards."* — short. A second frame was
taken after spending the bank to 0.

- `review/qa/eb194-gates/frame-20260829-160116-gatec-spark-badges.png`
- `review/qa/eb194-gates/frame-20260829-160129-gatec-spark-bank-zero.png`

3842×2160, `printwindow` route. **These are MATERIAL, not evidence**: whether
the spark glyph reads as a blob at badge size, and whether the short state
reads as a state, are [USER]'s eyes only (Guardrail-7). Nothing is claimed here
about how they look.

#### VRAM

`nvidia-smi --query-gpu=memory.used`, 32607 MiB card, same method throughout.

| when | used | delta over idle |
|---|---|---|
| idle, game closed | 2947 MiB | — |
| menu / character select | 3933 MiB | 986 MiB |
| **in a Kokomi fight** | **4410 MiB** | **1463 MiB** |
| Kokomi reward screen | 4354 MiB | 1407 MiB |
| **in a Klee fight** | **4432–4498 MiB** | **1485–1551 MiB** |

The in-fight figure is the one to budget against: **~1.5 GiB**, and it is
~0.5 GiB above the menu reading, so the menu sample taken on the blocked
attempt understated it by a third. With the game in a fight, roughly **28.1
GiB** stayed free on this card.

#### A finding for [USER] — the prototype rows DO have a per-row description channel

§12.6 item 14 and the sheet comment at `docs/prototype-surface.yaml:581-588`
both say the generated face "cannot be fixed from here". That reasoning is
about `gen_klee_cards`, whose Power descriptions are keyed per POWER ID and are
shared with the shipped card. It does not hold for a prototype row:
`gen_prototype_cards.py` emits each row as its own class with its own
`Localization` list (`ProtoKuragesOathMemory.cs:41-45`), which BaseLib reads off
the model — a per-row channel that moves no shipped face. The loc merge now
overrides that list at pool-build time, so **two channels describe one card**
and the generated one is wrong on its face until the override runs.

Nothing was changed about this: adding a `description:` field to the prototype
surface is a **generator contract change** and returns to [USER]. The pick:

1. **Keep the loc merge as it is.** One mechanism, already proven live; the
   generated face stays wrong in the file and is corrected at runtime.
2. **Take the `Localization` channel** — add an optional `description:` to the
   prototype surface row, let `gen_prototype_cards.py` emit it, and delete the
   merge. The face is then right in the generated source, with no boot-order
   surface at all — which is the class of bug `EB-194` just was.
3. **Both** — emit the row's own description AND keep the merge as a belt-and-
   braces override.

My read, offered as a read and not a decision: (2) removes a moving part on the
boot path, and the defect this sitting spent itself on came from that part
existing. But it widens a generator contract, which is [USER]'s to widen.

**RULED (R224): option (2)** — take the `Localization` channel, add the
optional `description:`, delete the merge. The contract is widened. The
recorded reason is DUPLICATION, not risk: the boot-path danger is not live any
more (`EB-194` is closed and the merge already moved to pool-build time behind
two locks seen to FAIL first), so the surviving argument is that two channels
describe one card and (2) leaves one fewer moving part. Engineering: `EB-215`.

#### State left on disk

`mods\klee` carries **`0.2.1441+proto`** — installed, validated, and now
**proven to start runs** (Kokomi and Klee both embarked and fought on it). The
bridge and `steam_appid.txt` were removed by `embark --teardown`, all four
ledger rows REVERTED; no game process is running. Seeds unspent. Nothing under
`review/qa/blindplay/` was read or written.


#### Gate B — DIAGNOSED and RE-RUN 2026-08-29: **PASS, all three states**

The record above stands as published (R101b). What it observed was real; what
it could not say is the cause, and the cause was neither entry rule and neither
reader.

**`EB-196` — the memory was cleared between every pair of hooks.**
`KurageMemory.ResetForCombat` was called from `KokomiResourceHooks.Subscribe`,
on the reading that the subscription delegate is handed a fresh combat once per
fight. It is not. `CombatState.IterateHookListeners` is an iterator over
`ModHelper.IterateAllCombatStateSubscribers(combatState)`, which re-invokes
every mod's delegate, and a combat enumerates its hook listeners on EVERY hook
broadcast — so the clear ran between every pair of hooks and an entry filed by
one hook was gone before the next could read it. That is verdict **(a)** in the
strict sense that the arm shipped with a memory that could never HOLD anything,
and it is why both rules looked broken at once: they share nothing except the
queue that was being wiped. The same line clears `PlayedAnything`, which is the
strip's second wrong sentence — "you have played no card this turn" after cards
were played. One cause, both symptoms.

The fix: the per-fight clear moved to `BeforeCombatStart` (the hook the game
raises once per combat, already proven to fire because it is where the base
kit's jellyfish is installed), `Subscribe` keeps only the stash it exists for,
and `ResetForCombat` gained an identity guard. Also in `Enrol`:
`CardModel.Keywords` walks `Pile -> CombatState` and throws for a card that is
not in a pile, which a card reaching the exhaust funnel can be — the `ephemeral`
read is now `SafeTitle`'s try/catch idiom, because an enrolment must not be lost
to a read that only decorates the strip.

**`EB-197` — the buff printed a countdown it does not have.** Nothing under the
flag ticks the Bake-Kurage down (§12.6 items 1, 2 and 8), but its face kept the
shipped "Lasts {Amount} more turn". Under `PROTOTYPE_CARDS` it now prints the
lifetime it has. The release face is byte-identical.

**Locks, all seen to FAIL against the pre-fix build first**, in
`klee-mod/KleeTests/Prototype/`: `KurageMemoryLifecycleTests` — the two entry
rules PLAYED rather than declared unreachable (a `Seat` carries a real
`Creature`, which is all `Enrol` reads); the bite,
`The_memory_survives_the_subscriber_list_being_re_enumerated`, which files one
Muster and one Exhaust — the two the live gate played and lost — and re-hands
the same combat; `The_pulse_key_survives_the_same_re_enumeration`; and two
structural pins on where the clear lives, plus one that reads the
re-enumeration off `sts2.dll` rather than trusting a comment. Pre-fix output,
verbatim: `Assert.DoesNotContain() Failure: Item found in set … Found:
"KurageMemory.ResetForCombat"`, `Assert.Contains() Failure: Item not found in
set … Not found: "KurageMemory.ClearForNewCombat"`, and both entry-rule tests
`System.NullReferenceException … CardModel.get_Keywords`. `KurageBuffFaceTests`
failed pre-fix on `Found: "Lasts"` and `Not found: "whole fight"`.

**THE RE-RUN**, from the art-bearing main checkout on the same pin, installed
stamp **`0.2.1456+proto`, `validate: OK`** on the full gate. A fresh Kokomi run
(seed `YU4EBKU3XHEG`, seedless of the sealed slate — the pinned
`KURAGEMEM001/002/003` are still UNSPENT), first fight, base kit only, no
prototype arm granted. Captures in `review/qa/eb196-gateb/`.

| state | file | the strip, verbatim |
|---|---|---|
| EMPTY | `gateB-state0-turn1-empty.md` | `Charge 0 — memory empty` |
| BLOCKED | `gateB-state2-blocked.md` | `Charge 0 / 3 — Coral Guard blocked` + `1. Coral Guard — 3 Charge — aims at random — BLOCKED: nothing behind it fires` |
| a QUEUE | `gateB-state3-two-entries.md` | the blocked front with a `free` memory behind it |
| FIRES NEXT | `gateB-state4-fires-next.md` | `Charge 4 / 3 — Coral Guard fires next turn` |
| FIRED | `gateB-state5-after-fire.md` | front gone, bank 4 -> 1, Block 5 on the board |

**So P4 is now GRADEABLE**: a blocked front does not read like an empty memory
— the empty state says `memory empty` and lists nothing, the blocked state
prints the bank against the front's own price, names the card and says
`BLOCKED: nothing behind it fires`. Whether that is legible ENOUGH is the
tester's answer to give, and it is not given here.

Everything else the gate proves in passing, none of it a measurement: **Rule 1**
filed the SACRIFICE (`Coral Guard`, price 3) and not the recruit; **Rule 2**
filed the recruit when it burned, so one Muster produced two memories, as ruled;
a 0-cost memory printed `free`; the ONE-PER-TURN latch held (the free memory
behind the front did not also fire); the BLOCK held the bank across a whole turn
rather than spending it on something cheaper; and the TARGET rule showed both
faces on one screen — `aims at Sludge Spinner` for a memory that was played at a
body, `aims at random` for one that never was. The wire agrees field for field
(`gateB-wire-after-fire.json`, `rule: "muster"` / `rule: "exhaust"` per row).

One observation, not a defect and not fixed: a Muster recruit enrols with
`ephemeral: true`, i.e. the rule does not see the Exhaust the Muster grants it
at the moment it files. `ephemeral` is RECORDED AND BEHAVIOUR-FREE by
construction (§11.3), so nothing today reads it; whoever attaches behaviour to
it under §11.6 item 1 has to fix this first, and [USER]'s ruling on that field
is where it belongs.

**State left on disk.** `mods\klee` carries **`0.2.1456+proto`** — installed,
validated, and proven to start and play a run. All four `embark` ledger rows
REVERTED, no game process, seeds unspent.

### 13.7 What this run cannot answer

Written down so nobody overclaims off it.

- **Balance.** Nothing here is a balance measurement and no number from the run
  is quotable (R213 B / R215 B, R217 G). The Oath's 3 and 5 are [USER]'s
  placeholder in his own word — *"see if it needs adjusting later"* — and this
  run does not adjust them, cannot support adjusting them, and is not evidence
  either way about whether 3× cost is the right price.
- **The cadence of Memory plays across a RUN.** This is whole-fight play, at
  most an Act-1 run on a starter deck. How often the memory fires over sixteen
  floors, how the queue behaves once a deck has drafted Exhaust and Ethereal
  cards into it, and whether Memory/Order spam becomes the only thing she does
  are all questions about accumulated decks, and none of them is in scope.
- **The drafted-pool tension.** §11.8 said it and §12.5 did not repeal it: the
  base kit prints the bank, the afford and the block, but the *interesting* half
  — banking toward a card you cannot yet afford out of a deck you chose — lives
  in the draft. A run granted one prototype row into a twelve-card starter tests
  the teaching surface, not the built deck, and cannot say whether one Muster is
  the right dose.

### 13.8 THE SEALED RUN — GRADED 2026-08-29

Run and graded on the branch `kokomi-blind-run`, from the art-bearing main
checkout, on the disclosed build (13.0). No grade below was read by anybody
before it was written, and none has been edited since.

#### What was spent

| | |
|---|---|
| seeds spent | **`KURAGEMEM001` only** |
| seeds still UNSPENT | `KURAGEMEM002`, `KURAGEMEM003` |
| build | `0.2.1456+proto`, off `mods\klee\manifest.json` |
| game | v0.111.0, off `release_info.json` |
| run seed, read back off the wire (R95) | `KURAGEMEM001` — the chosen seed was accepted, no deviation to disclose |
| arm granted | `KLEEMOD-PROTO_KURAGES_OATH_MEMORY` into the starting deck |
| actions | 60, stopped on `max_actions`; five fights and the run record written |
| sealed record | `review/qa/blindplay/kuragemem001/record.md`, committed before any grader opened it |
| leak audit | 66 observations, **1 hit**, and it is the blind prompt's own sentence *"no card list, no score, no recommendation"* matching the `pilot-vocabulary-score` rule. Not a leak; recorded rather than filtered |
| Codex calls | **67** — 60 observations + 6 record prompts inside the one session thread, plus 1 pair read. No rate limit was hit |

**Why 002 and 003 were not run, on the slate's own rule.** §13.5 pins them as
conditional: run 2 is taken *"only if run 1 terminates before P4 is reachable
(no blocked turn) or before the Oath is drawn"*. Neither condition holds — the
observation pages carry a blocked front on eleven turns and the Oath on
thirty-six — so the reserve seeds stay unspent. That is the registration being
obeyed, not a budget decision, and it happens also to spend no Codex.

#### The grades, slot by slot

Graders as §13.4 fixes them: the Codex seat (GPT family) on P1, P2, P4, P5, P6;
`opus-5-fresh` (Claude family, with the stated limit recorded beside it) on P3.
Verbatim reads at `review/qa/kokomi-kurage-blind-001-pair-review-codex-gpt-5.6-sol.md`
and `review/qa/kokomi-kurage-blind-001-p3-read-opus-5-fresh.md`; the prompts
they were handed are committed beside them.

| slot | grader | verdict | pair read | the count against the slot's own threshold |
|---|---|---|---|---|
| **P1** | seat (GPT) | **SPLIT** | RETURN | Front entries were named (`turn-006`, "the jellyfish is already set to replay Gorou next turn") but the paired card-AND-price read the threshold asks for is not in the record on 4 of the first 5 non-empty-queue turns; the falsifier's two wrong prices are not established either |
| **P2** | seat (GPT) | **SPLIT** | RETURN | Advance fire calls exist on `turn-006`, `turn-009`, `turn-019`; neither 5 correct nor 2 wrong can be counted, because the record does not carry the `blocked` / `fires_next` pair to count them against. No FIRES-direction miss is established |
| **P3** | `opus-5-fresh` (Claude) | **SPLIT** | RETURN | **0 of 10** qualifying turns, and **0 of six Musters** state a Memory consequence — every Muster target was chosen *because the card was dead*, the exact inverse of Rule 1, and the run record concludes that Exhaust builds Charge. The falsifier as written ("never once plays toward the queue") does not fire: `turn-005` and `turn-010` play a free card explicitly to give the jellyfish something to remember |
| **P4** | seat (GPT) | **MISS** | RETURN | Half (a) landed on the first evidenced block — the tester read `Coral Guard blocked` as a block and said nothing behind it fires. Half (b) failed: no play was named that would supply the Charge to unblock it |
| **P5** | seat (GPT) | **SPLIT** | RETURN | Gradable, not VOID — Gate A's face held and the Oath was drawn and played (`turn-006`). The required no-pay statement never occurs; a contrary expectation is not conclusively established either |
| **P6** | seat (GPT) | **SPLIT** | RETURN | Advance target calls exist (`turn-019`, `turn-025`, `turn-034`), so the "no advance call at all" falsifier does not fire and no fresh-bind expectation is stated; but no call can be verified correct, because the record does not carry what the automatic play actually hit |

**The pair read: 0 ADVANCE / 6 RETURN / 0 ESCALATE.** The seat's closing
paragraph: *"the run shows that the reader sometimes planned around an
anticipated replay, block, and target, but it does not demonstrate reliable
planning with the queue at the committed thresholds. The evidence is incomplete
rather than internally irreconcilable, so nothing warrants ESCALATE."*

**The decisive question (13.1) is not carried.** Its falsifier — that every
mention of the jellyfish is a report of something that already happened — does
NOT fire: the tester names the front before it fires and twice plays toward the
queue on purpose. But P3 at 0 of 10 says D2's steering is not there on the base
kit as built, and P4's half (b) says the Charge sources are not discoverable
from the page. D4 stands better than D2, which is the split the slate was built
to tell apart, and it read the way the slate said it would read if D2 failed.

**`P3` is RULED (R224) as `M54`: option (1).** Rule 1 prints as the **Muster
KEYWORD** — hover text is that keyword's detail, and "tooltip" is not a third
surface — and the gate is then re-run on `KURAGEMEM002`, which is unspent. The
diagnosed failure is **wording, not dose**, so option (2) (change the starter
Muster's dose) is not taken and the arm is not re-scoped to Rule 2 only.
Engineering: `EB-214`. Nothing above is re-graded (R101b).
**`P4`'s half (b) is NOT closed here** — where the Charge-source line goes is
`M55`, held as item 7 of `review/active/sitting-2026-08-30.md`, because the
persistent-display surface option (5) named was retired by `M61` option 3.

#### An instrument finding this run made, recorded and NOT acted on

Two of the six thresholds name an objective side the committed record cannot
carry. P2 counts a call *"against the `blocked` / `fires_next` pair the bridge
carried for that turn"* and P6 asks whether an advance aim call was *correct* —
both need the wire or the replay beside the tester's sentence, and
`record.md` carries the tester's words only. The seat said so itself on both
slots, and both are SPLIT partly for that reason.

**Nothing was re-graded and nothing was added to the record to fix it.** A
replay that contradicts a form is the finding, not a correction (§13.5 item 6,
R101b). The gap is written down here and returned as a numbered pick below.

**RULED (R224) as `M56`: option (1).** Carry a per-turn wire snapshot in future
records; **these grades stand** and nothing is re-registered or re-graded.
Option (2)'s re-registration is explicitly NOT taken, because `M54`'s rerun on
`KURAGEMEM002` (`EB-214`) carries the snapshot anyway — the objective side
arrives free. Engineering: `EB-216`.

One thing WAS fixed, before the run and disclosed here rather than after it:
the blind prompt requires a per-turn sentence and the reply schema enforces one,
but nothing carried it out of the gitignored turn pages into the committed
record — so the record could not evidence §13.5's own requirement that some turn
state IN ADVANCE what the jellyfish was about to play. `blindplay notes` now
carries that channel, with `_splice` stopping the leak audit truncating it;
five locks in `tier0/tests/test_blindplay_turn_notes.py`. Hygiene on the
instrument, committed before the seed was embarked, changing no prediction, no
threshold and no denominator.

#### Two observations from the record, neither diagnosed here

Both are the tester's words, both concern the strip, and neither is a defect I
should rule from a play record:

1. Fight 1: *"after Gorou it showed 'Charge 1 / 0,' then later said the memory
   was empty despite Charge remaining."*
2. Fight 2: *"The memory's 'Coral Guard blocked' entry also said nothing behind
   it fires, yet Sayu remained listed behind it, so I could not tell exactly
   what would replay."* — and the P3 read notes that this line is Rule 1 having
   worked, read by the tester as a display bug.

#### State left on disk

`mods\klee` carries `0.2.1456+proto`, installed and validated. All five embark
ledger rows REVERTED, no game process, `steam_appid.txt` and the bridge removed.
`KURAGEMEM002` and `KURAGEMEM003` unspent.

### 13.9 `KURAGEMEM002` — the rerun

**DRAFTED, REGISTERED, UNRUN, and committed before the deploy that runs it.**
Drafted by Claude under R212(2) from written intent that already exists — §13.2
is the slate this re-poses, R224 `M54`(1), `M55` and `M56` are [USER]'s
rulings, and `EB-214`'s own acceptance line is the cell's shape — and
countersigned in batch. **Nothing here is re-signed and no threshold is
touched:** every re-posed slot carries §13.2's prediction, denominator,
falsifier and one-way error direction character for character. What this
section adds is which slots are asked again, why, what each grade permits, and
what the round is contaminated by.

**Nothing in §13.8 is re-read, re-scored or withdrawn (R101b).** `KURAGEMEM001`
stands as published, including the two slots below that are NOT re-posed.

> **COUNTERSIGNED (R227, 2026-08-30): this cell is SIGNED**, in the batch of
> three, at PICK 3 option (1) — none vetoed. The cell had already RUN when the
> signature landed, and that is regular: R212 item 2 locates pre-registration
> in committing the slate BEFORE the run, which this section was, so there is
> no separate signature class for a countersign that arrives after the grade.

#### 13.9.1 What changed under the slate, and therefore what may be asked again

Three builds landed between the sealed run and this one, and between them they
replaced the surface four of the six slots are read off.

1. **The Muster keyword states Rule 1** (`EB-214` item 6, `M54`(1)).
   `KokomiRiderTips.ForMuster`'s body gains, under `#if PROTOTYPE_CARDS`, *"A
   Muster creates a memory of the card it ate, and the recruit creates a second
   when it burns. A memory replays for Charge equal to 3x its Cost."* It is the
   keyword's own body and not a second tip beside it — hover text is that
   keyword's detail, and "tooltip" is not a third surface. The blind page
   prints keyword bodies under every card in hand (`_render_card`), so the
   sentence reaches a tester who cannot hover.
2. **The strip is gone and the memory is an element** (`M61` option 3,
   §14.9–§14.11). The page section was rewritten with it: the bank, the front
   entry with its price and its state, the queue with its aims, and the run-out
   sentence are now **one fact per line** where the strip put three grammars in
   one sentence (`Charge 1 / 0`) — which is the frame the sealed tester read as
   a contradiction and reported as a display bug.
3. **The pile view says where Charge comes from** (`EB-214` item 7, `M55`
   re-scoped). *"Gain 1 Charge when a card of yours Exhausts"* heads the
   click-through view.

**One instrument repair, done here, before the run, and disclosed rather than
discovered afterwards.** Item 3 was a Godot `Label` and nothing else: a sighted
player reads it on a click and **a blind tester has no click**, so `P4`'s half
(b) would have been re-posed against a line the tester was never shown. The
page now carries the screen's sentence verbatim at the head of the same queue
block it already renders as "the queue, as the pile view shows it on a click"
(`understudy/blindplay.CHARGE_SOURCE_LINE`, one lock, seen to FAIL first). The
rate is spelled rather than imported, because `blindplay` may not reach `tier0`
at all — the no-leak pin — so the test holds the two in step from the other
side, the way `lint_constant_parity` holds the C# copy. **This changes no
prediction, no threshold and no denominator**; it makes a registered surface
reachable by the instrument that grades it, which is §13.8's own precedent
(`blindplay notes`, fixed before the sealed seed was embarked and disclosed in
the same place).

#### 13.9.2 The re-posed slots — four of six, and the two that are not

| slot | re-posed? | why |
|---|---|---|
| **P1** — the front entry and its price, off the page | **YES** | The surface it grades no longer exists. `P1` was written against the strip's `Charge {bank} / {price} — {name} {state}`; the page now prints `- Charge: N` and `- Next to fire: **X** — costs N Charge — …` as separate facts. A slot whose display was replaced has not been asked on the display it now has. |
| **P2** — fires next turn, or blocked | **YES** | Same surface, same reason: the state is now a full clause on the front line rather than a word at the end of a fraction. And `EB-216`'s snapshot carries the `blocked` / `fires_next` pair for the turn the call was made on, so **the threshold is countable for the first time** — §13.8 graded it SPLIT partly because the record could not count it. |
| **P3** — planning INTO the memory (Rule 1) | **YES** | `EB-214`'s own acceptance, and the reason the row exists. `M54`(1) ruled the 0-of-10 a WORDING failure; the wording is now printed and the claim is falsifiable. |
| **P4** — the block, and what unblocks it | **YES, both halves** | Half (b) is what `M55`'s line addresses and is the half §13.8 recorded as failed. Half (a) is re-posed **with it and not separately**, because the empty-versus-blocked distinction it grades is drawn by the rebuilt element and its rebuilt page section — the same replacement that re-poses `P1`. A repeat of half (a)'s landing is not new evidence about the rule; it is the check that the rebuild did not lose what the strip had. |
| **P5** — the Oath reads per-Memory-play | **NO** | Nothing in the pass touches the Oath's face, its condition or its wording. §13.8's **SPLIT stands as published** (R101b) and is not re-asked on a build that changed nothing about it. `EB-213`'s upgrade channel is in this build but the slot is about the base face, not the upgrade. |
| **P6** — the automatic play's aim | **NO** | Nothing in the pass touches aim. The queue lines print `aims at {target}` exactly as the strip's queue lines did, so the surface is unchanged, and §13.8's **SPLIT stands as published** (R101b). It is not re-posed merely because `EB-216` would now make it gradable: a slot is re-asked when the thing it grades has moved, not when the instrument improves. **Recorded and NOT graded** below instead. |

**`P6` is RECORDED AND NOT GRADED, and that is a registered outcome, not a
grade.** §13.8's instrument finding was that `P6` needs the aim the automatic
play actually took, and `record.md` held words only. This run's snapshot holds
it. So every advance aim call in this record is **counted and filed** in the
results, against the snapshot, with no verdict attached and no entry in any
tally — the shape `KLEESPARK-W2` gave `W5'`. It is evidence for whoever
registers `P6`'s own rerun; it decides nothing here, and it may not be read
back as `P6` having been re-graded.

**A blind spot, declared.** The re-posed set is chosen from §13.8's grades,
which the drafter has read. **No threshold, denominator, falsifier or error
direction is taken from them** — every one is §13.2's, unmoved — and WHICH
slots are asked is R224's ruling and `EB-214`'s acceptance rather than a choice
made against the numbers. The honest cost is that the four re-posed slots are
the four that did not come in, so this round cannot say the display is good in
general; it can only say whether the named repairs carried.

#### 13.9.3 Thresholds, unchanged, and the condition on each grade

The prediction, the threshold, the falsifier and the one-way error direction of
each slot below are §13.2's, unaltered. What is new is only the third column:
what the round is permitted to conclude.

| slot | threshold (§13.2, unchanged) | ADVANCE | RETURN | ESCALATE |
|---|---|---|---|---|
| **P1** | YES on at least **4 of the first 5** graded turns with a non-empty queue — the tester names the head of the memory AND what it will cost | 4 or 5 of 5 | 3 or fewer of 5, **or** the falsifier fires (a stated price disagreeing with the snapshot's `front_price`, or "I cannot tell what is queued", on 2 or more of those 5) | the two recorded reads reach opposite verdicts on the same five turns |
| **P2** | CORRECT on at least **5 of 6** graded turns with a non-empty queue, counted against the `blocked` / `fires_next` pair the wire carried for that turn | 5 or 6 of 6 | 4 or fewer, **or** 2+ wrong calls, and a wrong call in the FIRES direction is the serious one | as above |
| **P3** | at least **3 of 10** graded turns carry a plan naming the Memory consequence, **and at least one of them is a Muster** | 3 or more of 10 with a qualifying Muster | 0, 1 or 2 of 10, **or** 3+ with no Muster among them | as above |
| **P4** | YES on the **FIRST blocked turn of the run**, **both halves**: (a) says BLOCKED, distinctly from empty, and (b) names a play that would unblock it | both halves on the first blocked turn | either half missing on the first blocked turn; "not enough Charge yet, I will wait" with no named source is the registered example of (b) failing | as above |

**UNREACHED, and it is not a pass.** §13.2's slot dependencies carry over
whole: `P2` and `P4` are gradable only on turns the queue is non-empty, and a
run producing **no blocked turn** leaves `P4` **UNREACHED, not PASSED** — which
is itself a finding about the base kit's dose. `P1` needs five non-empty-queue
graded turns and `P3` needs ten graded turns; short of those denominators the
slot is UNREACHED and says so. Nothing is inferred from an absence.

**ESCALATE, defined once.** A slot ESCALATES where its two recorded reads —
the deciding grader's and the second read filed beside it — reach opposite
verdicts on the same evidence. That is R213's guard in its own words (two seats
materially disagreeing ESCALATES); it is not a third outcome a single grader
can reach alone.

#### 13.9.4 The decision each grade permits (R206)

**Every re-posed slot ADVANCEs** — and `P3` is the one that must, because it is
the row's acceptance. Then **the teaching pass is CONFIRMED**: `EB-214` closes,
`M54`(1)'s diagnosis (wording, not dose) is carried, `M55`'s line and `M61`'s
element are answered on the base kit, and the arm's next question is the one
§13.7 declared out of scope — **the drafted pool**, banking toward a card you
cannot yet afford out of a deck you chose. That needs its own registration and
its own deck, and it is not taken here.

**`P3` RETURNs** — 0, 1 or 2 of 10, or no qualifying Muster. Then `M54`(1) has
been TRIED AND HAS NOT CARRIED, and the diagnosis "wording, not dose" is
falsified on its own terms: the rule was printed on the surface the tester
reads and the tester still did not plan into the queue. **That is the pick that
returns to [USER], and it is a numbered pick list, not a blank:**

1. **Take `M54`(2) after all** — change the starter Muster's DOSE (§12.3 slot
   11, and the three Musters not chosen), on the reading that one Muster in a
   twelve-card starter is too few occasions to learn a rule from.
2. **Re-scope the arm to Rule 2 only** — the recruit's burn creates the memory,
   the sacrifice does not; one rule instead of two, at the cost of the half
   [USER] specified.
3. **Keep the rule and concede D2 on this arm** — the queue is an automatic
   engine the player watches, priced as one, with no claim that it is steered.
4. **Retire the memory queue** and return to v2's threshold, which is the
   design this replaced.

**`P4` half (b) RETURNs.** The Charge sources are still not discoverable from
the page with the line printed on it, which is the second time that half has
failed. §13.2's registered consequence is that **the acceleration keyword
("Stir", §11.3, provisional under R179) stops being optional** — a design call,
so it joins the pick list above as its own numbered item rather than being
taken by an integration.

**`P1` or `P2` RETURNs.** The rebuilt element and page do not carry the front
entry, its price or its state, and that is engineering on `EB-198`/`M61`'s
element rather than a [USER] pick: the row goes back to BACKLOG with the
failing frame named. **If BOTH return**, the display has now failed twice on
two different shapes, and the third attempt is a direction question for [USER]
rather than another integration's redraw.

**`P4` half (a) RETURNs alone.** The rebuild LOST what the strip had — §13.8
recorded half (a) landing — and that is a straight regression report against
the element, filed and fixed, with no design question attached.

#### 13.9.5 Contaminations

Stated before the run, in full.

- **The build is a `+proto` INTEGRATION of two unmerged branches and exists
  nowhere else.** `kuragemem002-rerun` merges `eb216-wire-snapshot` into
  `eb214-muster-keyword` at **`b49de52`**, with this registration and the
  §13.9.1 page repair on top; neither parent is on `main`. Nothing measured
  here is comparable to any other build, and a defect found here is this
  integration's until it is seen elsewhere. The exact deployed commit and the
  installed stamp are recorded in §13.9.7 before any observation is read.
- **The memory kit is ON under the flag.** `-p:PrototypeCards=true` in C#,
  `C.KURAGE_MEMORY` in sim. The rows are off-pool by construction, no shipped
  number moved, and the release build was proven byte-identical when the
  keyword landed. **Nothing here is a balance measurement and no number from it
  is quotable** (R213 B / R215 B, R217 G).
- **One seed, one session.** `KURAGEMEM002`, pinned in §13.5's table and
  UNSPENT, taken in order. Every threshold is a **within-run rate** and
  **nothing is compared with `KURAGEMEM001`** — different build, different
  display, different page. Where a §13.8 figure appears in the results it is
  context for a reader, never an arm.
- **The deck is `KURAGEMEM001`'s.** `--arm proto_kurages_oath_memory` is
  granted into the starting deck exactly as §13.5 pins it, even though `P5` is
  not re-posed: the recipe is the registered one, and removing the card would
  make this a different cell for no gain.
- **Seat policy, `M64`, and the one place §13.4 overrides it.** This round
  **can ADVANCE an arm**, so `M64`(1) applies and **the DECIDING read is the
  Codex seat**. The tester is the Codex seat too (R217 C: the author's own
  family may not play). **`P3` is the exception, and it is §13.4's, registered
  before `M64` existed and stricter than it:** the GPT family supplied the rule
  statement `P3` grades, so a GPT read of `P3` would be that family grading its
  own clause. `P3` is read by **fresh Opus**, with its family marked in the
  record and the honest limit written beside it — Claude implemented the rule,
  so the read is independent of the *statement* and not of the
  *implementation*. Neither read is presented as clean. **"Fresh Opus grades it"
  is not a general rule** (§13.4 item 4).
- **The local (Qwen) seat rides in SHADOW.** It may read the record; its
  reading is filed, labelled, and **never graded, never tallied, never
  replayed**. The `local` family is recognised and not authorable.
- **`EB-216`'s snapshot is carried for the first time, and it is the GRADER'S
  and never the tester's.** One row per `play` and per `end turn`, taken off
  the state the command was resolved against; it lands gitignored as
  `wire.jsonl` and beside the sealed record as `wire.json`, and `record.md`
  names it and its row count and inlines nothing. Nothing in `observation()`,
  `render()` or the feedback line reads a snapshot, and a test pins that no
  card id and no `entity_id` from one reaches any prompt. The per-play meter
  ledger rides with it.
- **The drafter has read §13.8 in full**, and §13.9.2's blind spot says what
  that costs.

#### 13.9.6 The Codex call budget, and the guard

**Cap: 70 Codex calls.** Up to 60 observation turns inside the one session
thread (`--max-actions 60`, §13.5's recipe), up to 6 record prompts, 1 pair
read, and 3 spare. `KURAGEMEM001` spent 67 on the same recipe.

`python -m understudy.codex_usage` is **read before the first call and again
after the last, and both lines are recorded verbatim in §13.9.7.** The stop
lines are **85% of the five-hour window and 50% of the week**; `EB-227` makes
the seat read its own window before every call and refuse past them. **If the
guard refuses, the run stops cleanly and the round grades what ran** — an
unrun slot is UNREACHED, an unread record is not a grade, and no board is
re-read on a repaired copy.

#### 13.9.7 THE RERUN — GRADED 2026-08-30

Run and graded from the art-bearing main checkout on the integration branch
`kuragemem002-rerun`. No grade below was read by anybody before it was written,
and none has been edited since. **Nothing in §13.8 is re-read, re-scored or
withdrawn (R101b).**

##### What was spent

| | |
|---|---|
| seeds spent | **`KURAGEMEM002`** (`KURAGEMEM001` was spent by §13.8) |
| seeds still UNSPENT | `KURAGEMEM003` |
| world | `kuragemem002-rerun` at **`10799139`** — the merge `b49de52`, the registration `142f0f1`, and the `EB-213` recursion fix on top |
| build | **`0.2.1627+proto.dirty`**, off `mods\klee\manifest.json`; `validate.ps1` **OK** on the whole gate (S7 suite 333.4 s) |
| the dirty mark | another workstream's untracked scratch under `review/qa/local-sanity-2026-08-29*/`, `review/qa/two-instance/` and `understudy/logs/*.log` — not this branch's to commit, so a clean stamp was not reachable and the mark is honest rather than incidental |
| R225 soak gate | `bounded seed=XAK56TVB9QDL actions=56 **fights=3 defects=0**`, reversibility log all REVERTED |
| game | v0.111.0, off `release_info.json` |
| run seed, read back off the wire (R95) | `KURAGEMEM002` — the chosen seed was accepted, **no deviation to disclose** |
| arm granted | `KLEEMOD-PROTO_KURAGES_OATH_MEMORY` into the starting deck |
| actions | 60, stopped on `max_actions`; four fights and the run record written |
| sealed record | `review/qa/blindplay/20260830-083819/record.md`, committed at `397c8266` **before any grader opened it** |
| the objective side, first time | `wire.json` beside it — **32 snapshots**, one per `play` and per `end turn`, machine-written and never shown to the tester (`EB-216`). Of the 32: **12 EMPTY, 12 FIRES-NEXT, 8 BLOCKED** |
| leak audit | **66 observations, 1 hit**, and it is the same false positive `KURAGEMEM001` recorded — the blind prompt's own sentence *"no card list, no score, no recommendation"* matching `pilot-vocabulary-score`. Not a leak; recorded rather than filtered |
| Codex calls | **67** — 66 prompts inside the one session thread (60 actions plus the four fight records and the run record, one of which took a second prompt) plus 1 pair read. Cap was 70 (§13.9.6); `KURAGEMEM001` spent 67 on the same recipe |
| guard before | `codex: 5h 41% (resets 04:40 EDT) · week 17% (resets Sep 05 17:58)` |
| guard after | `codex: 5h 6% (resets 09:40 EDT) · week 18% (resets Sep 05 17:58)` — the five-hour window rolled over mid-run, which is why the second number is smaller; **neither stop line (85% / 50%) was approached and the guard never refused** |
| shadow | the local (Qwen) seat read the same prompt at temperature 0, `review/qa/kuragemem002-shadow-read-local-qwen3.md`, **recorded and never graded** |

##### The grades, slot by slot

Graders as §13.9.5 fixes them: **the Codex seat (GPT family) DECIDING on P1, P2
and P4** under `M64`(1), and **`opus-5-fresh` (Claude family) on P3** under
§13.4's stricter family rule, with its limit recorded beside it. Verbatim reads
at `review/qa/kuragemem002-pair-review-codex-gpt-5.6-sol.md` and
`review/qa/kuragemem002-p3-read-opus-5-fresh.md`; the prompts they were handed
are committed beside them, and the wire table both were given is
`review/qa/kuragemem002-wire-table.md`.

| slot | grader | verdict | judgment | the count against the slot's own threshold |
|---|---|---|---|---|
| **P1** | seat (GPT) | **UNREACHED** | RETURN | Zero assessable front-and-price statements in the first five graded turns with a non-empty queue, against a threshold of 4. **The falsifier did not fire either** — no stated price disagrees with `queue[0].price` and the tester never said it could not tell what was queued. The observable was never produced, so it is neither PREDICTED nor MISS |
| **P2** | seat (GPT) | **UNREACHED** | RETURN | Zero assessable fire-versus-blocked calls against the six wire states (five FIRES-NEXT then one BLOCKED). Neither five correct nor two wrong can be counted, and **no FIRES-direction miss is established** |
| **P3** | `opus-5-fresh` (Claude) | **PREDICTED** | **ADVANCE** | **5 of 10** qualifying turns, threshold 3, **with 2 Musters** among them against a threshold of 1 — `turn-014` and `turn-058` (Rule 1), `turn-018`, `turn-036` and `turn-052` (Rule 2), spread across three fights. The falsifier at 0 is nowhere near firing. The count still clears at 4 and 1 if the weakest qualifier is struck |
| **P4** | seat (GPT) | **UNREACHED** | RETURN | The first blocked state is snapshot 009 (`turn-021`) and the tester's sentence there is about Block against Thorns damage: it neither names the memory as blocked-rather-than-empty nor names a play that would unblock it. **Neither registered falsifier fired** — the tester did not say "not enough Charge yet, I will wait" and did not conflate blocked with empty. Later retrospective evidence shows the understanding (the run record: an expensive memory *"stopped every card behind it"*), but P4 grades the FIRST blocked turn only |

**Tally: 1 PREDICTED / 0 SPLIT / 0 MISS / 3 UNREACHED**, and P6 RECORDED AND
NOT GRADED below. **Judgment: 1 ADVANCE (P3) / 3 RETURN (P1, P2, P4) / 0
ESCALATE.** The seat's closing paragraph: *"the retrospective records suggest
the tester could reason about Charge, an expensive front entry, and memories
held behind it, but the assigned turn-level boards did not collect the
observations needed to show that the tester could plan with the queue
prospectively. … Nothing warrants ESCALATE: the problem is missing evidence,
not irreconcilable evidence."*

##### The shadow read, recorded and not graded

The local (Qwen) seat was handed the SAME prompt as the deciding read, at
temperature 0, and answered **SPLIT / SPLIT / MISS** on `P1` / `P2` / `P4`,
RETURN on all three. **Verdict agreement with the deciding read: 0 of 3.** That
number is filed and nothing else: R222 B says a shadow reading is recorded,
never graded, enters no tally and is never replayed, and this one decides
nothing about the slots or about the seat's chair — three boards is not one of
`M62`'s rounds. The disagreement is instructive rather than damning, and it is
the same disagreement the deciding read describes: where the observable was
never produced the shadow scored the ABSENCE as evidence against the tester
(SPLIT, MISS) and the deciding read scored it as no evidence at all
(UNREACHED), which is what the slate's own UNREACHED clause requires.

##### `P3` carried, and that is the row's acceptance

`EB-214`'s acceptance is *"`P3` is re-posed at its published threshold on a
record carrying `EB-216`'s snapshot"*. It was, and it came in at **5 of 10 with
two Musters** where §13.8 read **0 of 10 with 0 of six Musters**. `M54`(1)'s
diagnosis — the failure is WORDING and not dose — is **carried on its own
terms**: the sentence was printed on the surface the tester reads, and the
tester planned into the queue by both rules.

**Two honest qualifications, both from the grader's own read, neither changing
the verdict.**

1. **The comprehension is retrospective, not prospective.** At both Muster
   SELECTION screens (`turn-016`, `turn-060`) the sacrifice was still picked for
   being the most useless card in hand, with no memory reasoning printed. The
   tester states Rule 1 correctly — *"transforming it created a 3-Charge memory
   at the front of the queue that blocked free memories behind it"* — in the RUN
   record, after the fact, and as a regret. The wire agrees it is fact
   (snapshots 029–032: `Before Sun and Moon @3` front, BLOCKED, `Sayu @0` held
   behind it). So the record shows the pattern being **learned across the run**
   rather than held before the first Muster. `P3`'s threshold does not ask for
   the sacrifice-versus-recruit half to be priced at the moment of choosing, and
   it is not graded on it.
2. **This is one run on one seed.** Every threshold is a within-run rate and
   nothing here is compared with `KURAGEMEM001` (§13.9.5).

##### The three UNREACHED are an INSTRUMENT finding, and the display is not what returned

**The display was on the page, correct, and legible.** Thirty-four of the sixty
observation pages carry the memory section, and the blocked page the seat graded
`P4` on printed, in full:

> - Charge: 2
> - Next to fire: **Coral Guard** — costs 3 Charge — you cannot pay it, so NOTHING in the memory fires next turn.
> - Opening the memory shows "Gain 1 Charge when a card of yours Exhausts", and then the whole memory, front first:
>   1. **Coral Guard** — 3 Charge — aims at random
>   2. **Gorou — General's War Banner** — free — aims at random
> - Charge runs out at #1 (**Coral Guard**): that one and everything behind it are held until the bank catches up.

Both halves of `P4` are answerable off that page, and `P1`'s and `P2`'s
observables are printed on it verbatim. **What is missing is the QUESTION.**
`blindplay session`'s reply schema is exactly two fields, `command` and
`thinking` (`turn-*/schema.json`), so the tester writes the reason for the play
it is making and is never asked what the jellyfish will do next turn. §13.5's
own third record requirement — *"at least one turn where the tester stated IN
ADVANCE what the jellyfish was about to play"* — is a requirement on the record
that **nothing in the harness enforces**, and `KURAGEMEM001` met it by accident
rather than by construction.

That is the same class of finding `M56` fixed for the objective half: a
threshold whose evidence the instrument does not collect. `EB-216` gave this run
the wire's side of `P2` and `P6`; it did not, and was never scoped to, make the
tester produce the stated side. **Filed as `EB-229`.** Under §13.9.3 an UNREACHED
slot is not a pass and **nothing is inferred from an absence** — and, symmetrically,
nothing is inferred against the display, which no reading of this record faults.

##### `P6` — RECORDED AND NOT GRADED

Registered as such at §13.9.2, so this decides nothing and enters no tally.

**What the wire carried.** Twenty front-entry rows across the run name an aim:
`Gorou — Inuzaka All-Round Defense` aiming at `Toadpole` (snapshot 004), then
`random` for four snapshots, `Seapunk` (014–017), `Sludge Spinner` (023–025);
`Coral Guard` and `Before Sun and Moon` at `random` throughout their blocked
spells. So the stored-target rule and its random fallback were both live and both
printed.

**What the tester said.** Two advance statements name what the memory will DO —
`turn-040`, *"The jellyfish will deal 4 damage and Kurage's Oath should add 3
Block"*, and `turn-064`, *"The jellyfish will reduce the enemy to 5 HP"* — and
neither names WHICH BODY on a board carrying more than one. No fresh-bind
expectation is stated anywhere. That is the whole of it, filed for whoever
registers `P6`'s own rerun; it is not a grade and may not be read back as one.

##### What returns to [USER]: nothing

§13.9.4's numbered pick list fires on a **`P3` RETURN** or a **`P4` half-(b)
RETURN**. `P3` ADVANCED, so its four-item list is not opened. `P4` is
**UNREACHED, not RETURNED on its threshold** — the deciding grader found the
question was never asked rather than answered badly, and §13.9.3 forbids
inferring either way from an absence — so the acceleration keyword ("Stir")
does **not** become non-optional on this run and no item of that list opens
either. **No [USER] row opens on this round.** The one thing owed is
engineering: `EB-229`.

##### Register moves this run makes

- **`EB-214` CLOSES.** Its acceptance is met on its own words and its row leaves
  HEAD. `214` comes out of `lint_register_ids.OPEN_IDS` in the same commit,
  because the lint refuses a manifest entry that outlives its row — **and only
  214 was removed.**
- **`EB-229` is MINTED** for the elicitation gap above.
- **`EXPERIMENTS.md`** moves the registration from *Active* to *Graded*.
- Nothing else. No stamp moved, no sheet moved, no shipped number moved, and
  **no number from this run is quotable** (R213 B / R215 B, R217 G).
  Guardrail-7: floors.

##### Two observations from the record, neither diagnosed here

Both are the tester's words and neither is mine to rule from a play record.

1. **The end-of-turn pulse preview.** Fight 1: *"its end-of-turn preview changed
   from granting Block to dealing Hydro damage depending on the latest card
   played"*; fight 4: it *"continued to alternate between copying a card's effect
   and its printed pulse behavior in a way that was difficult to reconcile"*.
   This is `KURAGEMEM001`'s fight-1 and fight-3 observation again, on a rebuilt
   display that did not touch the pulse line.
2. **A harness sequencing report.** Fight 2 and fight 4 both say the fight-record
   prompt arrived before the Muster selection and confirmation screens had
   resolved — *"the game asked for a fight record before that interaction and the
   fight itself had actually finished"*.


---

## 14. The memory gauge — [USER]'s direction (2026-08-29)

This section supersedes `EB-198` as it was filed. `EB-198` was a *diagnosis*
row: reproduce the two frames the blind tester misread, and file whatever
turned out to be broken. The diagnosis is done and it found nothing broken.
What it found instead is that the display is the wrong shape for the job, and
[USER] has said so and said what to build in its place. The wording pick the
diagnosis was heading toward — three re-phrasings of the strip's first line —
is moot and is not carried anywhere.

### 14.1 The words, in the order they were given

First, the direction that retires the strip:

> "I think that the strip is insufficiently ambitious. Downfall already has an
> example of what I'm thinking for the Awakened - a new UI element that shows
> the Charge gauge, how much will be spent next turn, a color based on whether
> there is enough to play, and the ability to open a list to see what's
> queued."

Then the placement and the shape:

> "Too many words. Make it a vertical bar on the left side of the screen (not
> below Kokomi), color blue for 'fires next turn' and red for 'blocked' - big
> number for current charge, small number in parentheses for the queued spend,
> with a graphic for say the icons of the next 3 queued cards up (bottom is
> next-to-play) that can be clicked into like the deck list."

Then the removal of the meter:

> "On the gauge - let's do one better and actually remove the bar. Color the
> cards with a highlight instead (blue if they can be afforded, bottom to top)
> so you see where you will run out of charge, and take back the real estate of
> the gauge bar."

Then the cut to the smallest honest element, answering three of the mock's own
picks in passing:

> "2) Let's drop the small number 3) Hide everything but the charge count 4)
> Let's actually reduce the footprint - show the first currently queue'd card,
> the rest would be in the pile selector"

And finally the last look, which is conditional and therefore also a question
back to engineering:

> "1) is 'also red' possible in the pile view? If so, let's do that, otherwise
> dimmed is fine"

Read as one move, the five quotes walk the design steadily *down*. It began as
a gauge with a list attached; it became a coloured stack that replaced the
gauge; it ends as **one card and one number**, with everything else behind a
click. Every step removed something rather than adding it, and the last
removals are the largest: the queue's whole shape, which the strip printed in
full and which nobody could read, is now something you ask for.

### 14.2 Why the strip fell short, which is not the same as being wrong

The blind run (§13.8) surfaced two tester sentences about the strip. Both were
diagnosed against the code, and **both frames are true as drawn**:

1. *"after Gorou it showed 'Charge 1 / 0,' then later said the memory was empty
   despite Charge remaining."* — `KurageMemory.Reading()`
   (`klee-mod/KleeCode/Powers/Prototype/KurageMemory.cs:1066-1076`) prints
   `Charge {bank} / {front.Price}`, so a free front prints a literal `/ 0`.
   Later, with the queue drained, the same function takes its empty branch and
   prints `Charge 1 — memory empty` (`:1072`). Both lines are correct. The
   tester read them as contradicting one another because the first looks like a
   fraction over a zero denominator and the second looks like it is denying the
   Charge the first just showed. Nothing is broken. The *form* — one line of
   running prose carrying three unrelated facts in three different grammars —
   is what turned two correct readings into one apparent error.

2. *"The memory's 'Coral Guard blocked' entry also said nothing behind it
   fires, yet Sayu remained listed behind it, so I could not tell exactly what
   would replay."* — this is Rule 1 working exactly as ruled. A front the bank
   cannot pay holds everything behind it and nothing is spent (`kurage_fire`,
   `tier0/engine/effects.py:3722-3781`; the C# twin `KurageMemory.Fire`,
   `KurageMemory.cs:744-767`). Sayu is still queued because Sayu has not fired.
   The P3 read already noted that the tester took this for a display bug.

So `EB-198`'s finding stands as a record — **two frames, both true, both
misread** — and its next action is not a fix. It is a rebuild, because a
display that is correct and still unreadable has failed at the only thing it
exists for. It is worth saying why the strip ended up like this, because it was
not carelessness: it was built under an explicit "NO NEW ART" constraint, which
meant drawing an entire list into the single `%ValueLabel` of the shared gauge
scene (`klee-mod/KleeCode/Vfx/GaugeBridge.cs:257-263`). It was the cheapest
thing that could carry the facts, and it did carry them.

### 14.3 The element as specified

Mock: <https://claude.ai/code/artifact/7f4b1180-306a-4740-a091-95b70020ad20>

The resting element, at the **left edge of the screen** as HUD — not at the
second-row anchor above Kokomi where the strip lives today
(`GaugeBridge.cs:63`, `SecondRowAnchor = (0, -340)`):

- **One card**: the front of the memory queue, the one that fires next turn,
  drawn at roughly deck-list thumbnail size.
- **A ring on it**: **blue** when the bank can pay that card's price, **red**
  when it cannot. That is the whole state, and it is `bank >= front.Price` —
  one comparison, no projection.
- **The Charge count** as a large number beneath it.
- **Nothing else.** No bar, no track, no fill, no `(price)` number, no second
  and third card. An empty queue draws the Charge count alone.

Clicking opens **the whole queue** as a card list, in the shape of the deck /
discard viewer:

- every queued memory, front first, with its price and the body it will hit;
- rings coloured by the **running subtraction** from the front — blue while the
  bank can still reach that card, **red at the card where the Charge runs
  out**;
- and the cards the red one holds up are **also red**, per the last quote,
  which §14.5 confirms is buildable.

The division of labour is the point and worth stating plainly: **the HUD
answers "does the next one fire", the pile answers "how far do I get".** The
first is a fact and needs no forecast. The second is a forecast, and is
therefore kept off the always-on surface, where a wrong prediction would be
read as a lie.

### 14.4 The affordability run, and where it lives

The pile view needs one thing the code does not have: a running subtraction
over the queue against the bank, producing a per-entry `affordable` flag and
the index of the first entry that is not payable.

    remaining = KokomiResources.GetCharge(creature)
    for entry in queue:
        if entry.Price <= remaining:
            entry.affordable = True
            remaining -= entry.Price
        else:
            entry.affordable = False
            break            # and everything behind it is held, and also red

It belongs as a **pure function beside `KurageMemory.Queue`**
(`KurageMemory.cs:438`) — no mutation, no RNG, nothing read but the bank and
the queue — with a **twin in tier0 beside `kurage_fire`**
(`tier0/engine/effects.py:3722`) so the existing parity lint covers it. It must
not be inlined into the drawing code. The reason the strip's numbers never
drifted is that they come from the same expressions the resolution uses, and
this is the first display fact with no resolution-side expression to borrow;
giving it one function with a twin is how it stays that way.

**It is a forecast, and three separate things falsify it** before the cards it
colours ever fire:

- Only **one memory fires per turn** (the `kurage_fired_this_turn` latch,
  `effects.py:3754-3755`), so the second blue card is a *next turn plus one*
  claim, not a next-turn one.
- **Charge accrues at 1 per Exhaust**, and a player who keeps playing will
  normally bank more before then, which moves the red card further up.
- A **blocked front holds and pays nothing**, so the bank does not drain past
  the red card — the red boundary is exactly where the projection stops being a
  prediction and becomes a wall.

The honest framing is "where you run out **if you bank nothing more**", and the
same principle the shipped gauge already states about itself applies: *"a meter
that lies about its own ceiling is worse than no meter"*
(`GaugeBridge.cs:99-102`). [USER]'s fourth quote happens to protect this by
construction — the forecast is only ever drawn on a surface the player opened
on purpose. Both surfaces must **re-evaluate on every Charge change and every
queue change**, which is the refresh discipline `GaugeBridge.Refresh` already
runs on (`GaugeBridge.cs:345-379`, its funnels enumerated at `:342-343`).

### 14.5 What the engine gives us

**A citation caveat, first, because it bounds every base-game fact below.** The
brief assumed decompiled game source at `game_ref/`. There is none:
`C:\Users\Monty\Documents\GitHub\GItS\game_ref\` is 29 flat balance-data files
with zero `.cs` and zero `.tscn`, and `docs/current/OPERATIONS.md:172` describes
it as decompile-*derived* — extracted numbers, not code. The real decompile
target, `sts2_decompiled/`, is gitignored (`.gitignore:47`) and **does not exist
on this machine**. The base-game facts below were therefore read straight out of
the shipped assembly with `ilspycmd -t <FullTypeName> "<GameDataDir>\sts2.dll"`,
decompiling to stdout with nothing written. **Their line numbers are relative to
that per-type stdout and are reproducible only by rerunning that command** —
they are not file:line into any tree that exists. Every mod-side citation IS
exact. Two hygiene observations fell out of the same work and are recorded here
rather than filed, since neither is this branch's business: pinning a decompile
output directory would give this study stable citations, and `.sentinel/dll.json`
pins `sha256 a1f9e653…` at 9,364,480 bytes while the live dll is 9,757,184 bytes
dated 2026-08-28 — **the sentinel pin is stale against the installed game.**

With that said, every hard part of this design turns out to be already solved.

**A card thumbnail is one property.** `CardModel.Portrait` returns a `Texture2D`
directly, with no node instantiation at all:

    public Texture2D Portrait => ResourceLoader.Load<Texture2D>(
        PortraitPath, null, ResourceLoader.CacheMode.Reuse);   // CardModel :157

with `PortraitPath` at `:143` and `HasPortrait` at `:153`. It is `CacheMode.Reuse`,
so repeat loads are cheap, and `NCard.UpdatePortrait()` (`NCard :1244`) confirms
this is the same texture the real card face uses. A mod can write
`new TextureRect { Texture = entry.Card.Portrait }` and be finished. **This also
removes the option-2 gap I expected**: it works for base-game cards in the queue
as well as ours, which `RosterArt.CardPortrait` (`klee-mod/KleeCode/KleeArt.cs:54-83`)
does not.

Two things NOT to use. `NTinyCard` looks like the obvious miniature and is the
wrong picture — `SetCardPortraitShape(card.Type)` assigns one of three generic
silhouettes (`attack_portrait.png` / `skill_portrait.png` / `power_portrait.png`,
`NTinyCard :120-129`), so it says "an Attack", never "*Coral Guard*". And
`NCard.Create(CardModel, ModelVisibility)` (`NCard :772`) builds the full
playable card node, pulling five assets including three blur/mask materials and
a `CanvasGroup` (`:666`) — far too heavy for a HUD element that draws one
picture.

**The pile viewer takes an arbitrary card list.** This was the biggest unknown
and the answer is clean. `CardPile` has a public constructor and a public adder:

    public CardPile(PileType type)                                      // CardPile :43
    public void AddInternal(CardModel card, int index = -1, ...)        // :90
    public IReadOnlyList<CardModel> Cards => _cards;                    // :25
    public event Action? ContentsChanged;                               // :33

and the viewer's open method takes one:

    public static NCardPileScreen ShowScreen(CardPile pile, string[] closeHotkeys)
                                                          // NCardPileScreen :211

So: build a `CardPile`, `AddInternal` the queue's `CardModel`s in order, call
`ShowScreen`. Two caveats to carry: `NCardPileScreen._Ready` switches on
`Pile.Type` for its bottom info text and logs *"CardPileScreen has no info
text."* on a type it does not recognise; and it subscribes to
`Pile.ContentsChanged` in `_EnterTree`, so our `CardPile` must stay alive for
the screen's lifetime. Two alternatives exist if that screen proves awkward —
`NSimpleCardSelectScreen.Create(IReadOnlyList<CardModel>, CardSelectorPrefs)`
(`:123`) and the raw grid widget `NCardGrid.SetCards(IReadOnlyList<CardModel>,
PileType, List<SortingOrders>, Task?)` (`:832`).

Note this is **not** the `CardSelectCmd` route. `CardSelectCmd.FromSimpleGrid` /
`FromChooseACardScreen`, which the mod already calls from card resolution
(`Cards/Furina/Generated/CurtainUp.cs:67-69`,
`Cards/Furina/SpotlightCards.cs:63-64`), are `await`ed *choices* against a
`PlayerChoiceContext` that a HUD click does not have — and opening a selection
screen outside resolution in a lockstep co-op game is the class of thing this
repo has been careful about (`CardSelectCmd.PushSelector` / `UseSelector` is
banned mod-wide for a neighbouring reason,
`docs/current/atlas/klee-mod-runtime.md:82-89`,
`tier0/tests/test_eb14_selection_hook.py`). `NCardPileScreen.ShowScreen` is the
read-only cousin and is the correct door.

**"Also red" in the pile view is POSSIBLE, and here is the mechanism.** The last
quote made this conditional, so it is answered directly. The pile screen renders
each entry as a real `NCard` node through `NCardGrid`, and this repo already
ships a working per-card overlay on exactly that class: `SparkCostBadge`
(`klee-mod/KleeCode/Vfx/Prototype/SparkCostBadge.cs`) is a Harmony postfix on
`NCard.UpdateStarCostVisuals` (`:153-158`) that reads `nCard.Model` (`:97-99`)
and paints a badge onto live card nodes **on every surface a card renders**. The
same hook, keyed on whether that `CardModel` instance is in the memory queue and
unaffordable under §14.4's run, colours the ring red per entry. Identity
matching is sound because a queue `Entry` holds the live `CardModel` instance
rather than an id, deliberately (`KurageMemory.cs:155-164`). The colours are the
game's own: `StsColors.red` with `StsColors.unplayableEnergyCostOutline` is
`CardCostHelper.GetStarCostColor`'s InsufficientResources arm
(`SparkCostBadge.cs:41-43`, `:134-139`) — literally the engine's "you cannot pay
this". **So the answer to [USER]'s question is yes, and the dimmed fallback is
not needed.**

**The HUD anchor exists, and the left edge is crowded.** There is no dedicated
`CanvasLayer` for combat UI — it is a plain `Control` tree. `NCombatUi._Ready()`
(`:283-294`) resolves every HUD child by Godot unique name (`%EndTurnButton`,
`%CombatPileContainer`, `%Hand`, `%EnergyCounterContainer`, …), so arbitrary
`Control` children under `%CombatUi` are an anticipated shape; `NCombatUi._Ready`
at `:299-306` even iterates `GetChildren().OfType<Control>()`. Two candidate
parents: **`NCombatRoom.Instance.Ui`** (`%CombatUi`), which inherits the combat
show/hide and `AnimIn`/`AnimOut` (`:416`, `:426`); or **`NRun.Instance.GlobalUi`**
(`%GlobalUi`), which survives room transitions and is where the game puts
persistent chrome.

The left edge, top to bottom, is: **relic inventory** (top-left, and it *grows
downward as relics accumulate* — `NRelicInventory.GetBottomOfInventory()` returns
a position derived from `lineCount`), then in co-op the **player state cards**
(`NMultiplayerPlayerStateContainer.GetTargetPosition()` returns exactly
`GlobalUi.RelicInventory.GetBottomOfInventory()`), then a gap, then at the bottom
the **energy orb** (repositioned to `(100, 806)` for star characters,
`NCombatUi.Activate :314`; hides by sliding to `(-480, 128)`, off the left) and
the **draw pile** (`NDrawPileButton` hides to `Position + (-150, 100)`). Discard
and exhaust are bottom-*right*.

**The mid-left band is the only free vertical space, and its top boundary moves
during a run.** The low-risk pattern is the one the game already uses for the
same problem: position relative to `RelicInventory.GetBottomOfInventory()` and
subscribe to the same two signals `NMultiplayerPlayerStateContainer` does —
`RelicsChanged` and `Viewport.SizeChanged`. This is the largest remaining piece
of real work in the whole build, and it is copying an existing pattern rather
than inventing one.

**Co-op: the HUD is shared, single-instance, and local-seat only.** There is
exactly one `NCombatUi`, and `Activate(CombatState)` binds it with
`Player me = LocalContext.GetMe(_state)` (`:319`), which propagates into
`_combatPilesContainer.Initialize(me)` (`:320`), `_starCounter.Initialize(me)`
(`:321`) and `NEnergyCounter.Create(me)` (`:327`). The accessor is
**`LocalContext`** — `GetMe(ICombatState)` (`:52`), `IsMe(Player)` (`:88`),
matching on `player.NetId` (`:70`). There is no `CombatState.LocalPlayer` and no
`Player.IsLocal`. Teammates get a compact `NMultiplayerPlayerState` widget each
under `%MultiplayerPlayerContainer`, not a duplicated HUD — and that container
renders nothing at all when `Players.Count <= 1`.

**This confirms a real regression and it should be named, not discovered.**
Today every creature-tracked display is built for EVERY seat:
`NCombatUi.Activate`'s postfix loops `state.Players` and calls `Setup` per
player, deliberately — *"EVERY seat, not only the local one -- the whole point
of the docket is that a partner's end of turn is legible"*
(`GaugeBridge.cs:504-513`). Position is the attribution. The new element has one
slot on a shared HUD and therefore **shows the local player's memory only**. At a
Kokomi + Kokomi table the partner's queue becomes unreadable where today it is
legible over her head. That is the price of moving off the creature. If it
matters, the game's own answer is the `NMultiplayerPlayerStateContainer` pattern
— a small per-seat widget — but that is a second display, and this whole
direction is a move away from having two.

**What the pck can carry**, for completeness, though the recommendation needs
none of it: `.tscn` and `.tres` overlaid verbatim from `klee-mod/pck-src/`
(`tools/build_pck.ps1:730-737`) plus PNGs from the gitignored ImageGen tree, with
the contract line DERIVED from what landed (`:795-823`) so a new scene needs no
contract edit. **No fonts** — nothing in the pipeline imports one, and every
label in `gauge.tscn` and `turn_end_docket.tscn` uses `theme_override_font_sizes`
against the project font. And the standing rule: **no scripts in pck scenes**,
because the assembly has no ScriptPath mapping, so behaviour attaches from C#
only (`klee-mod/pck-src/README.md:14-17`).

**Nothing material was left undetermined.** The three unknowns this study opened
with — how to get a thumbnail, whether the viewer takes an arbitrary list, and
where a screen-space Control parents — are all answered above. The one soft spot
is that none of it can be re-checked by opening a file, only by rerunning
`ilspycmd -t`.

### 14.6 Three ways to build it

Costed in engineering days as S (≤1), M (2–4), L (5+), against
`SalonVisualsBridge` at 649 lines and `TurnEndPreviewBridge` at 394 — both
custom visual bridges built and playtested in this repo — as the calibration.

---

**Option 1 — recolour and relabel the existing gauge. Size: S.**

Keep `shared/gauge.tscn` at the second-row anchor. Put the state colour on
`%BarFill` / `%ValueLabel` through the existing `GaugeSkin` path
(`GaugeBridge.cs:401-435`), and cut `StripText()` from a paragraph to the bank
plus a coloured front line. Queue detail moves to the Bake-Kurage power's
tooltip, via `NHoverTipSet.CreateAndShow` in the shape
`TurnEndPreviewBridge.RefreshSlotHover` already uses (`:347-393`). Files:
`GaugeBridge.cs`, `KurageMemory.cs`. No new scene, no new texture, no new hook,
no HUD anchor, no co-op question — every seat keeps its own display as today.

**What it gives up: the direction, all of it.** Not at the left edge, no card,
no click, no queue view. It is carried here as the honest baseline — this is
what the cheapest thing buys — and as the fallback if the HUD anchor turns out
to be closed. It does answer `EB-198`'s two frames, since colour separates
"free" from "empty" without either printing `/ 0`.

---

**Option 2 — a pck scene at the screen edge, with our own popup. Size: M.**

A new script-less `pck-src/shared/kurage_memory.tscn`: a `TextureRect` for the
front card's portrait, a `ColorRect` ring behind it, a `Label` for the bank —
`turn_end_docket.tscn` reduced to one slot, and that scene already ships an
`IconN` sprite, a `ChipN` plate, a `ChipLabelN` and a `HoverN` Control per slot
(`:145-214`). A new `KurageMemoryBridge` on the `TrackedDisplayBridge` skeleton,
parented to a screen-space node instead of tracked to a creature. The queue
popup is ours: an `NHoverTipSet` over a `HoverN`-style Control, or a second
scene we show and hide.

**What it gives up:** the queue view will not be the pile selector, because it
is not one — [USER] said "the rest would be in the pile selector", and this
approximates it. It owns its own popup lifecycle, dismissal and z-order, which
is the fiddly part; and "also red" would have to be re-implemented inside our
own popup rather than falling out of the `NCard` postfix that already works.
Given that §14.5 found the real viewer takes an arbitrary `CardPile`, this
option now buys nothing that option 3 does not, and costs a pck rebuild per
iteration.

---

**Option 3 — a C# HUD element over the game's own pile viewer. Size: S–M.**

No new scene and no new art. The element is a `Control` under `%CombatUi` (or
`%GlobalUi`) holding a `TextureRect` fed by `entry.Card.Portrait`, a ring
`ColorRect`, and a `Label` for `KokomiResources.GetCharge`. Built and torn down
on a postfix of `NCombatUi.Activate` / `Deactivate` — the hook `GaugeBridge`
already patches (`GaugeBridge.cs:489-495`) — with the seat resolved by
`LocalContext.GetMe(state)`, exactly as `NCombatUi.Activate` itself does.
Refreshed on the same funnels `GaugeBridge.Refresh` uses. Click is
`NClickableControl`'s `_GuiInput` / `OnRelease`, opening
`NCardPileScreen.ShowScreen(pile, hotkeys)` over a `CardPile` we build from the
queue. Per-entry red comes from the `SparkCostBadge` postfix on `NCard`.

**What it gives up:** it is the most exposed to base-game internals — `NCard`'s
visual-update contract, `NClickableControl`'s signals, `NCardPileScreen`'s
`Pile.Type` switch and its `ContentsChanged` subscription. All three are
characterised in §14.5 and none is a blocker. The residual risk is the left-edge
band, which it shares with option 2.

---

### 14.7 Recommendation

**Option 3, and after the engine read it is no longer a close call.**

Every piece the direction asks for turns out to be a thing the engine hands
over: the thumbnail is one cached property (`CardModel.Portrait`), the pile
viewer takes a `CardPile` we construct (`NCardPileScreen.ShowScreen`), the click
base is the same one the pile buttons use, the HUD parent is a plain `Control`
tree that already resolves children by name, the seat accessor is
`LocalContext.GetMe`, and per-entry red is the `SparkCostBadge` pattern this
repo has already shipped on this exact class. Option 3 needs **no new scene, no
new texture, no pck rebuild** — which also means no rebuild-and-validate cycle
between iterations on a display that will want several. Option 2 now buys
nothing option 3 does not, and pays a pck round trip for it. Option 1 remains
the fallback only.

**One thing to spike first, inside an hour, before the estimate is trusted:**
park a coloured rectangle in the mid-left band under `%CombatUi`, positioned off
`RelicInventory.GetBottomOfInventory()`, and confirm it survives a turn
boundary, a relic pickup and a window resize. That is the only piece of this
build the mod has never done, and everything else is characterised.

**And one thing to flag back rather than decide: the co-op regression in
§14.5.** Moving from the creature to a shared HUD trades a partner's legibility
for the local player's, because there is exactly one `NCombatUi` and it is bound
to `LocalContext.GetMe`. Nothing in the direction contemplates a co-op table and
it may simply not matter — but it is a real loss against today's display, and it
should be a known one rather than a surprise.

### 14.8 The picks — `M61`

**One pick, and it is the build.** The mock's four looks are all answered: the
small number is dropped, the empty state shows the Charge count alone, the
footprint is one card, and the held cards behind the red one are **also red** —
which §14.5 proves is buildable via the `SparkCostBadge` postfix on `NCard`, so
the "dimmed" fallback [USER] conditionally accepted is not needed and is not
carried.

1. **Option 3** — a C# HUD element over the game's own pile viewer.
   **Recommended**, §14.7. No new scene, no new art, no pck rebuild.
2. Option 2 — a pck scene at the screen edge with our own popup.
3. Option 1 — recolour today's on-creature gauge. The fallback if the HUD
   anchor turns out to be closed to mods.

### 14.9 As built

`M61` came back as **option 3**, and the co-op question §14.5 flagged came back
with it: the element is **local-seat only**. Built on branch
`kurage-memory-card`, stacked on the direction branch. Not deployed and not
seen live — a blind run held the game.

**Files.**

| File | What it carries |
|---|---|
| `klee-mod/KleeCode/Vfx/Prototype/KurageMemoryCard.cs` (new) | the element, the click, the pile ring patch, the teardown patch |
| `klee-mod/KleeCode/Powers/Prototype/KurageMemory.cs` | `EntryState`, `Affordability`, `RunOutIndex`, `Wire`, `Combat`; `run_out_index` and per-row `state` on the snapshot |
| `klee-mod/KleeCode/Vfx/TrackedDisplayBridge.cs` | `Registry<TKey, TNode>`; the old `Registry<TKey>` is now its Node2D subclass |
| `klee-mod/KleeCode/Vfx/GaugeBridge.cs` | the `kokomi_memory` spec deleted; Setup and Refresh call the element |
| `tier0/engine/effects.py` | `kurage_affordability` / `kurage_run_out_index`, beside `kurage_fire` |
| `docs/kurage-affordability-vectors.json` (new) | the parity table both suites read |
| `tier0/tests/test_kurage_affordability.py` (new) | the sim's rule, two properties, and the fixture derivation |
| `klee-mod/KleeTests/Prototype/KurageMemoryPinTests.cs` | six new pins (four cases, the parity run, two structural) |
| `understudy/blindplay.py`, `tier0/tests/test_understudy_blindplay.py` | the page section and its lock |
| `tools/lint_constant_parity.py` | seven new geometry constants declared UNMIRRORED |

**The colours, and all four are the game's own.** Blue is **`StsColors.blue`**
(`87CEEB`) with **`StsColors.defaultStarCostOutline`** (`175561DC`) behind it.
The engine has no "affordable" colour to borrow — affordability is drawn in
`cream` on a cost badge — so `blue` is the closest existing one and it is the
colour the direction names. Red is **`StsColors.red`** (`FF5555`) with
**`StsColors.unplayableEnergyCostOutline`** (`501717`), which is literally
`CardCostHelper.GetStarCostColor`'s InsufficientResources arm and the pair
`SparkCostBadge` already uses. The empty state draws the count in
**`StsColors.cream`**: no card, no affordability, so no state colour.

**The refresh path is the strip's, unchanged.** `KurageMemory.RefreshStrip` →
`GaugeBridge.Refresh(creature)` → `KurageMemoryCard.Refresh(creature)`. The
element is a screen-space `Control`, not a creature-tracked `Node2D`, so it is
a call at the end of `Refresh` rather than one more `GaugeSpec` — but it rides
the same funnels, and there is no polling and no `_Process` anywhere in it.
Build and teardown are the `NCombatUi.Activate` postfix `GaugeBridge` already
owned, plus a new `Deactivate` postfix.

**Three decisions taken inside the option, each cheaper than what §14.5
characterised.**

1. **The anchor is the left edge, vertically centred** — not
   `RelicInventory.GetBottomOfInventory()` with `RelicsChanged` and
   `Viewport.SizeChanged` subscriptions. Centring puts it in the middle of the
   free band by construction and follows a resize through Godot's own anchor
   propagation, with no base-game type and no signal. The relic-relative
   pattern remains the known upgrade if the live check finds a collision.
2. **`PileType.None`** for the queue pile. `Draw` re-sorts by rarity in
   `OnPileContentsChanged`, which would destroy the one thing the view is for;
   `Discard` / `Exhaust` would print another pile's explanatory sentence.
   `None` hides the label and logs one benign *"CardPileScreen has no info
   text."*.
3. **A plain `Control.GuiInput` handler** for the click rather than
   `NClickableControl`. The type did not resolve under any namespace tried with
   `ilspycmd -t`, and a Godot input event needs no base-game class at all — one
   fewer internal to be exposed to.

**What could not be pinned headless, stated rather than faked past.**

- **That a partner's screen carries nothing.** The element is a Godot node and
  no test in `KleeTests` may touch one. What IS pinned is that both entry
  points resolve the seat through `LocalContext` rather than looping
  `state.Players` the way the three creature-tracked bridges deliberately do.
- **Every pixel of it**: the anchor clearing a deep relic column, the thumbnail
  reading at 104px, the ring being legible, the badge not colliding with the
  portrait, the pile ring covering an `NCard`'s rect under its own `Scale`.
- **The pile viewer accepting `PileType.None`** end to end, and the ring
  disarming when the screen closes.

All of that is `EB-198`'s live acceptance: a `+proto` dev deploy, the four
states of the mock on a live frame, blind-read.

**Locks, each seen to FAIL before it passed.** Neutering the sim's held branch
gives `assert ['payable','runs_out','payable'] == [..., 'held']` at index 3;
the same neuter on the C# side fails three xUnit pins including the parity run;
replacing `Snapshot`'s call to `Affordability` fails
`The_element_draws_the_projection_rather_than_re_deriving_it`; swapping
`LocalContext.GetMe` for `state.Players[0]` fails
`The_memory_card_resolves_the_local_seat_and_only_the_local_seat`; renaming the
page's run-out sentence fails the page lock.

### 14.10 Live acceptance

Run 2026-08-29 from the art-bearing main checkout on branch
`kurage-memory-card`, game closed for both deploys. Two builds, because the
first live frame found a defect and the fix is in this section:

- **`0.2.1506+proto`** is what is installed and what every capture below except
  the first is taken on. It carries the `Portrait` fix described under "what
  the frame found". Its predecessor `0.2.1495+proto` is the branch as `M61`
  left it. Both stamped `+proto.dirty` — the working tree carried another
  workstream's untracked scratch under `review/qa/local-sanity-2026-08-29*/`,
  which is not this branch's to commit, so a clean stamp was not reachable and
  the dirty mark is honest rather than incidental.
- Game **v0.111.0**, the pinned build. `validate.ps1` OK on both deploys, whole
  gate, nothing skipped.

**The boards.** A live Kokomi run in each case (`understudy.embark`), first
fight of act 1, seeds `AEKL4GL2CCNF` and `8BRS1D2FEWTG` — read back off the
wire, and named here for provenance only. Nothing on them is a measurement:
the queue was filled by granting `Call to Arms` through the dev door and the
bank was moved with `set_resource`, so `bridge.GRANT_GUARDRAIL` applies to
every frame in this section. No existing `understudy/turns/` file stages a
memory queue, and none was written: this is a display acceptance, not a graded
turn.

**What rendered.** Captures in `review/qa/eb198-live/`.

| State | Board | Result |
|---|---|---|
| Empty queue | round 1, Charge 0, nothing enrolled | **RENDERS.** The count alone at the left edge, cream, no ring and no thumbnail — the state the blind tester could not tell from a block. `state-a-empty-queue.png` |
| Blocked front | Water's Edge queued at 3 Charge, bank 0 | **RENDERS.** Red ring, the card's own portrait, the price badge `3`, the count `0` in red. `state-b-blocked-red.png` |
| Payable front | three entries (3 / free / 3), bank 7 | **RENDERS.** Blue ring, portrait, badge, the count `7` in blue. `state-c-affordable-blue.png` |
| The click | left-click on the element | **WORKS.** The game's pile viewer opens on our `CardPile`, the queue front first in the order the page prints, each card at full size with its real face, dimmed combat behind it and the base game's own back button. One benign `CardPileScreen has no info text.` in the log, exactly as `PileType.None` was expected to produce. `state-d-pile-view.png` |
| The pile projection | bank 7 covering the queue, then bank 3 running out at #3 | **DOES NOT RENDER.** No affordability ring appears on any entry in either case — the cards show only their own frame colours, and the two frames are indistinguishable. `state-d-pile-view.png`, `state-e-pile-view-runs-out.png` |

**The anchor clears.** Left edge, vertically centred, no collision with the
relic row above or the energy orb and draw pile below at 3842x2160. The
thumbnail reads at 104px and the ring is legible at a glance. Whether the
anchor still clears a DEEP relic column is untested — this run held two relics.

**What the frame found, and what was fixed.** §14.5 read `CardModel.Portrait`
off the decompile and concluded it "works for base-game cards in the queue as
well as ours". That is exactly backwards for OUR cards and the first live
frame drew an empty ring: a mod card has no `PortraitPath` to load, because its
art is a runtime `ImageTexture` handed to BaseLib's portrait patch as
`CustomCardModel.CustomPortrait` (`RosterArt.CardPortrait`, `KleeArt.cs`) and
never reaches the base property at all. `KurageMemoryCard.Portrait` now prefers
the override and falls back to the base property, which keeps the half of §14.5
that was right — a base-game card in the queue still draws its own face with no
per-roster art table. Rebuilt, redeployed and re-captured; every capture in the
table above except the empty state is on the fixed build.

**What did not work, and is NOT mine to fix.** The pile view's affordability
rings never paint. `KurageMemoryPileRing.Paint` is armed off a Harmony postfix
on the private `NCard.UpdateStarCostVisuals`; the mod loads with no Harmony
error, our pile demonstrably opens, and no exception is raised — the ring
simply never appears, on a bank that covers the whole queue or one that runs
out at #3. Two candidates and the frame cannot separate them: that hook does
not run for an `NCard` the pile grid builds, or the ring Panel is drawn beneath
the card's own art. This is §14.9's own open question — "the pile ring covering
an `NCard`'s rect under its own `Scale`" — answered NO, and picking the
replacement hook needs the decompile rather than a guess, so it is filed rather
than patched. **The consequence for the design is the whole point of the pile
view**: the HUD's half (does the next one fire) is live and correct, and the
pile's half (how far do I get) is not shipped. §14.3's division of labour is
therefore half-built.

**A diagnostic caveat, not a defect.** `set_resource` writes the bank straight
past `KokomiResources`, so it does not run `RefreshStrip` and the element keeps
its previous reading until something else refreshes it. Every Charge change
through real play does go through that funnel, and was seen to repaint the
element live (an Exhaust took the count from 0 to 1 and a Muster redrew the
ring). Read the dev door's staleness as the door's, not the element's.

**The page.** `understudy.blindplay observe` carries the run-out sentence on a
blocked front — "Charge runs out at #1 (**Water's Edge**): that one and
everything behind it are held until the bank catches up" — and its covering
twin, "Your Charge covers every memory queued, if you spend none of it
elsewhere", on a bank that reaches the end.

**`godot.log`.** No exception, no error and no warning from `KurageMemoryCard`,
`KurageMemory` or `NCardPileScreen` across either session. The only line either
class produced is the expected `[INFO] CardPileScreen has no info text.`, once
per pile open. The `[WARN] [klee] No card art at …` block and the
`pck resource missing` block both predate this branch and name unrelated rows.

**Still owed, and it is [USER]'s eyes-on.** Whether the badge reads against a
light portrait (it is cream on white here, and low-contrast on Water's Edge);
whether 104px is the right size; whether the left edge is the right home. Those
are taste, not correctness, and §14.1's five quotes are the only spec they have.

### 14.11 The pile rings (`EB-201`)

Run 2026-08-29 on **`0.2.1517+proto.dirty`** from the art-bearing main checkout
at `eb201-pile-rings` (detached), game v0.111.0, `validate.ps1` OK on the whole
gate (S7 suite 325.9s). The dirty mark is the same untracked scratch under
`review/qa/local-sanity-2026-08-29*/` and `review/qa/two-instance/` that §14.10
carried; it is another workstream's and not this branch's to commit.

**The cause, settled off the decompile.** §14.10 left two candidates. The
first — that the hook does not run for a pile-grid `NCard` — is **false, by
construction**: `NCardGrid.InitGrid` builds each entry with `NCard.Create` and
`NGridCardHolder.Create`, adds the holder to the live scroll container, and
then calls `nCard.UpdateVisuals(_pileType, CardPreviewMode.Normal)`, which
calls `UpdateStarCostVisuals` unconditionally; the scrolled-window reuse path
`NCardHolder.ReassignToCard` calls the same `UpdateVisuals` again.

The defect was the **rect**. An `NCard` is a `Control` whose own rect is not
the card face: `NCardHolder.ConnectSignals` pins `CardNode.Position` to
`Vector2.Zero` and `NCardGrid.UpdateGridPositions` places each holder at the
CELL CENTRE, so the face is drawn centred on the node's origin — and
`NCard.GetCurrentSize` returns the constant `defaultSize * Scale` rather than
reading `Size`, carrying the base game's own warning that you want the HOLDER's
size instead. The `FullRect` anchor preset therefore sized the ring to that
rect: a `Panel` correctly parented, correctly coloured, and zero pixels wide.
No exception, no ring — the frame §14.10 captured. (These line numbers do not
exist: the decompile is `ilspycmd -t <FullTypeName>` to stdout, per §14.5.)

**The fix is a rect and a draw order, and the hook is unchanged.** The ring
takes `NCard.defaultSize` centred on the origin, re-applied on every paint
because a pooled `NCard` arrives carrying whatever the last screen left on it,
and is moved to last child so it draws over `%CardContainer` rather than under
it. One INFO line per pile open now names how many entries were painted, so the
next reading of this can tell a dead hook from an invisible ring without a
second deploy.

**What rendered.** Live Kokomi run, seed `V0BBVV03WPJ2`, first fight of act 1.
The queue was built through the dev door and the bank moved with
`set_resource`, so `bridge.GRANT_GUARDRAIL` applies to every frame here and
nothing in this section is a measurement. Queue: Coral Guard (price 3), Gorou
(0), Water's Edge (3), read back off the wire.

| State | Board | Result |
|---|---|---|
| Covering bank | bank 7, queue 3 / 0 / 3 | **RENDERS.** Three blue rings. `state-f-pile-view-covering.png` |
| Runs out | bank 3, same queue | **RENDERS.** Blue, blue, **red** on Water's Edge — the wire agrees (`run_out_index` 2). `state-e-pile-view-runs-out.png` |
| Disarm | our pile closed, the base game's DRAW pile opened | **NO RINGS.** Its Coral Guard and Water's Edge are different instances of the same faces and carry nothing. `state-g-drawpile-disarmed.png` |

**`godot.log`.** Two pile opens, each `[INFO] CardPileScreen has no info text.`
followed by `[INFO] [klee] kurage pile ring: painted 3 of 3 entries at
300x422.` No exception, no error and no warning from `KurageMemoryCard`,
`KurageMemory` or `NCardPileScreen`.

**Not covered.** A queue long enough to scroll — the reuse path is decompiled,
not witnessed. Whether the ring reads against every card frame colour is
[USER]'s eyes-on, like §14.10's other three.

### 14.12 The memory reached a Klee page (`EB-207`)

The Klee Sparks whole-fight blind run (`klee-sparks-2026-08-29.md` §12.8 item
2) reported that every combat page in its session carried a *"The Bake-Kurage's
memory"* block, and that the block repeatedly said it had played no card after
several cards had been played — the tester's most confusing item on the screen,
on a **Klee** run. The C# element was never the leak: `KurageMemoryCard.Setup`
has asked `LocalContext.GetMe` **and** `KokomiResources.IsKokomi` since it was
built, so no non-Kokomi seat has ever drawn it on any build. The leak was the
reader. `vendor/STS2_MCP/gits/GitsKurageMemory.cs` spells three wire states —
an ABSENT `kurage_memory` key is a build with no memory rule compiled in, an
EMPTY MAP is the rule present on a seat that is not hers (what
`KurageMemory.Snapshot` returns off a failed `IsLive`), and a populated map is
a memory — and `blindplay.kurage_memory` only ever split the first from the
rest, so `{}` was rebuilt into a whole section out of `_int`/`_text` defaults:
Charge 0, an empty queue, and a `none` pulse rendered as "you have played no
card this turn". The scope rule is now the same one in both engines: the
element and the page draw the memory **only for the local seat when that seat's
character is Kokomi**, a Kokomi *partner* included in the exclusion under
§14.5's ruled local-only loss. `Refresh` gained the character test `Setup`
already had, so the rule is spelled at both doors rather than at one and
inherited at the other. Both locks were seen to FAIL before the fix and pass
after
(`test_an_empty_map_is_a_seat_that_is_not_kokomi_and_gets_no_section`;
`KurageMemoryPinTests.Both_doors_into_the_element_ask_whether_the_seat_is_hers`).
**Live, on `0.2.1543+proto.dirty`:** a Klee run (seed `NWTJYHNQF50C`, act 1
first fight, two cards played) whose page carries no memory section and whose
left edge is empty —
`understudy/logs/frames/frame-20260829-204611-eb207-klee-no-memory-element.png`
— and a Kokomi run (seed `P36RUZK9MLEA`, same floor) whose page still carries
the section and whose left edge still carries the element, drawn in its
documented empty-queue state of the Charge count alone —
`frame-20260829-204721-eb207-kokomi-memory-element-present.png`. Frames are
MATERIAL under the capture guardrail, not measurements. Unproven: the co-op
half. A Kokomi partner beside a Klee local seat was not played, so that the
partner's memory reaches neither the local element nor the local page is
argued from `LocalContext` and the wire's per-player scoping, not witnessed.

---

## 15. `KURAGECAD-S1` — the memory's CADENCE across a drafted deck, in the sim

**REGISTRATION. Drafted from written intent and committed BEFORE any run**
(R212(2), EXPERIMENTS *Pre-registration + blind grading*). Nothing in §15.1 to
§15.4 was written after a number was seen: the instrument that produces the
numbers is a SEPARATE, LATER commit and the run is a third. R101b binds —
nothing published in §11–§14 is re-read, re-graded or rewritten here.

This is the FIRST leg of `EB-234` and it is the SIM leg. The whole-fight leg is
registered as owed at §15.7 and is not taken tonight.

### 15.1 Intent — why this read exists, quoted

**§13.7, the deferral this discharges, verbatim:**

> - **The cadence of Memory plays across a RUN.** This is whole-fight play, at
>   most an Act-1 run on a starter deck. How often the memory fires over sixteen
>   floors, how the queue behaves once a deck has drafted Exhaust and Ethereal
>   cards into it, and whether Memory/Order spam becomes the only thing she does
>   are all questions about accumulated decks, and none of them is in scope.

> - **The drafted-pool tension.** §11.8 said it and §12.5 did not repeal it: the
>   base kit prints the bank, the afford and the block, but the *interesting*
>   half — banking toward a card you cannot yet afford out of a deck you chose —
>   lives in the draft.

**The four levers `EB-234` names, and where each is written down:** the **3×
stored cost** (`KURAGE_MEMORY_COST_PER_ENERGY = 3`, [USER]: *"cards cost Charge
equal to 3x their Cost"*), **one fire per turn** ([USER]: *"If you stack
infinite Charge, then you still get only one play per turn"*), **blocking**
([USER]: *"Sticking a card you can't afford into Memory blocks Memory until
it's played"*), and the **free replay** — the 0-cost memory that costs 0 Charge
([USER]'s own named example, *"Gorou in the starter deck"*). §11.4 carries all
four as constants.

**What this read is FOR, stated as the act it selects between.** §6.1 item 11
and §13.7 say the same thing in different words: every observation this rule has
ever produced was taken on a TWELVE-CARD STARTER, and the rule is a *drafted*
engine. The sim is the one instrument that can walk sixteen floors three times
over at no game cost, so it answers — at the level of counts, and of nothing
else — whether the memory has a cadence at all on a deck the drafter built, what
ends up sitting in it, whether the block jams it, and whether the replay
swallows her turn. **It selects between two things the whole-fight leg can do:**
stage a fight that watches a *rhythm* (if the memory fires on a regular beat and
the queue stays short), or stage one that watches a *jam* (if the block
dominates, or the backlog runs away under the uncapped queue). It cannot and
does not say whether any of that is fun.

### 15.2 The arm, exactly

**The shipped Kokomi pool with `C.KURAGE_MEMORY` set true, and nothing else.**
No card is granted, injected or forced; `force_cards` is `None`. What the flag
turns on is exactly what §11.4 and §12 say it turns on, and all of it is already
built and tested:

1. **`KURAGE_ALWAYS_ON` (the v4 base kit, default `True`)** — the jellyfish is
   installed at the start of every one of her combats and never expires.
2. **The starter substitution** (`loader._starter_ids`): `bake_kurage` leaves,
   `to_the_front` — the plain 0-cost Muster — takes its slot, so RULE 1 is
   printed in fight 1. Twelve cards either way.
3. **The offerable-pool substitution** (`loader._pool_substitutions`): the
   shipped `kurages_oath` leaves Kokomi's pool and `proto_kurages_oath_memory`
   takes its slot at the same rarity, so a flagged run can only be offered the
   ruled 3-Block face.
4. **The rule itself** — both entry doors, the 3× price, the fire, the block,
   the one-per-turn latch, the uncapped queue and the rewritten pulse.

**Archetype `commander`.** It is Kokomi's Companion/Muster plan, so it is the
plan under which both entry doors are reachable by draft; `priest` and `assist`
are NOT run and nothing below speaks about them.

**THREE REPAIRS LANDED BEFORE THIS SECTION AND ARE DISCLOSED HERE**, in the
commit `EB-234 prep` immediately preceding it. Each killed the run outright, so
without them there is no read at all: the memory-branch pulse did not print the
bank its own telemetry reduction reads; `_enrol_memory`'s Status/Curse refusal
missed the half of the Status family the engine synthesizes (`rarity="basic"`);
and `kurage_fire` rebuilt the front through `loader.get_card` rather than
`effects.token_card`, which is `EB-123`'s seam. All three sit under the flag,
none moves a shipped byte, and each has a test whose red state was confirmed
first. **They are named before the numbers because they change what the arm
does** — without repair 2 a Toxic could sit in the memory, which is not the rule
§11.3 states.

**STRUCK by `C9`'s MISS — see §15.6. The paragraph stands as published and is
not rewritten (R101b); what it got wrong is the DECK half, and the enrolment
half held at 0.**

**ETHEREAL IS UNREACHABLE IN THIS ARM, and this is a seam fact read off the
sheets BEFORE the run, not a result.** `EB-234` asks how the queue behaves once
*Exhaust and Ethereal* cards are drafted into it. The Exhaust half is reachable
and is slot `C8`. The Ethereal half is not: the only draftable Ethereal card in
the repository is Klee's `big_badda_boom`, and the two other carriers of the
keyword are the `clumsy` CURSE and Furina's `ethereal_spotlight` token, both of
which the memory's own door refuses (junk, and a token in no Kokomi pool). Slot
`C9` registers that as an instrument check and names the decision it changes:
**the Ethereal half of `EB-234` cannot be answered in the sim at all and belongs
to authoring or to the whole-fight leg.**

**Definitions, fixed here so no later run can redefine them.**

- A **player turn** is one `turn_open` event in a fight's log.
- The memory's **state** on a player turn is exactly one of **FIRE**
  (`kurage_memory_fire`), **BLOCKED** (`kurage_memory_blocked`) or **EMPTY**
  (`kurage_memory_empty`) — `combat._player_turn` emits precisely one of the
  three per turn while the rule is live, which is what makes a share of turns a
  legitimate denominator.
- An **enrolment** is one `kurage_remember` event, carrying the rule that filed
  it (`muster` / `exhaust`), the price and the remembered face's cost.
- The **queue length** at a turn is the authoritative `queued` / `remaining`
  field on that turn's own state event, never a reconstruction.
- **Her own plays** on a turn are that turn's `play` events minus that turn's
  fires. Any other free-play route (a Study Buddy replay, say) counts as HERS,
  which is the conservative direction for `C5`: it can only make the memory's
  share look SMALLER.
- A **drafted deck** is the run's `deck_ids` as they stood when the fight was
  fought (`_RunCtx.deck_ids`), and the **final deck** is `RunResult.deck_ids`.

### 15.3 The cell, the control, and the budget

| | |
|---|---|
| cell | `cells.CANONICAL.but(name="kuragecad-s1", character="kokomi", archetype="commander", jobs=1)` — **600 runs, seed 11, route `hunter`, `assigned` policy, realistic loadout (relics + potions), every act**, i.e. sixteen floors three times over |
| world stamp | read live off `tier05.cells.world_stamp()` and printed in the record's header. **The tree reads `RT12/D18/P11/C21`** as this section is written (`STATE.md`'s Live cell was corrected to C21 by `KLEESPARK-S1`). A stamp that differs at run time is DISCLOSED in §15.5 and the read is not published against a moved world |
| stamps this read moves | **NONE.** The instrument is a new module plus its test; no constant, no drafter dial, no policy branch, no engine rule. `C.KURAGE_MEMORY` is flipped at run time and restored in a `finally`, with the three loader/reward caches cleared on both edges |
| arms | **TWO. `flag ON` is the arm.** `flag OFF` — today's shipped Kokomi, same cell, same seeds — is a paired CONTROL, **RECORDED and NOT GRADED**. No slot below is registered on it; it exists so a reader can see what the same 600 runs do without the rule |
| jobs | **1 (serial, in-process).** The observer wraps `model.run_one` and `model._RunCtx._record_traces`, and a batch spread over worker PROCESSES reaches neither. `main` REFUSES anything else rather than printing a silent zero |
| compute budget | **≤ 30 minutes for both arms.** Sized before the run off a 20-run feasibility probe on this tree: 1.9 s for 20 instrumented runs, so 1,200 runs has ample headroom. If the driver exceeds 30 minutes it is stopped and the record publishes what completed, with the completed run count as the denominator |
| what the probe was allowed to see | **timing, and whether each event type is emitted at all** — the D4 instrument-visibility check, that the instrument can SEE the changed object. Five of the six memory events were present and `kurage_memory_full` was absent, which is what an uncapped queue must produce. **No rate, share, count or distribution was read**, and every threshold below is drafted from §11's written intent, not from the probe |
| grader | `tier05/exp_kurage_cadence_s1.py`, committed BEFORE the run in its own commit. Every falsifier below is one of its printed fields; no grade reads a judgement |

### 15.4 The slate — nine predictions, drafted from §11's written intent

| # | slot | prediction | falsifier, mechanically | UNREACHED when | the decision the outcome changes |
|---|---|---|---|---|---|
| `C1` | **The fire rate.** Share of player turns whose memory state is FIRE. The rule's whole claim is that Exhaust cards "get played twice"; a rule that fires on fewer than one turn in twenty is decoration, and one turn in five is the loosest reading of a beat. | **≥ 20% of player turns.** | FIRE turns ÷ all player turns, pooled over the arm. **≥ 20% = PREDICTED; 5% to < 20% = SPLIT; < 5% = MISS.** | fewer than 500 player turns are recorded | **PREDICTED**: the memory has a cadence on a drafted deck, and the whole-fight leg is staged to watch a RHYTHM — is the replay legible, is it forecastable, is it hers. **MISS**: the drafted engine barely runs, and the first question for [USER] is the dose (more Musters, a cheaper price, or the accelerator keyword), not the display. **SPLIT**: the whole-fight leg still watches the rhythm, and the dose question is recorded rather than raised. |
| `C2` | **Cadence across a DEVELOPING deck.** The fire rate by act. A drafted deck adds Companions, Musters and Exhaust rows, so the intent's own arithmetic says the rate RISES as the run develops. This is the slot `EB-234`'s "over 16 floors" is really about. | **The act-3 fire rate exceeds the act-1 rate, AND act 3 ≥ 1.25 × act 1.** | Per-act FIRE share over per-act player turns. Both halves = **PREDICTED**; one = **SPLIT**; neither = **MISS**. | fewer than 200 act-3 player turns | **PREDICTED**: the engine is a drafted engine as designed, and the starter-deck reads of §6.1/§13 are correctly labelled teaching-surface reads. **MISS**: the deck she drafts feeds the memory no better than the starter does, which is a POOL question — it goes to [USER] as a pick list about what Kokomi's pool prints, and no number here settles it. |
| `C3` | **What actually sits in the memory.** The two entry doors are independent by construction; on a drafted deck the Exhaust door should carry the queue and the Muster door should still be visible. | **Rule 2 (Exhaust) files ≥ 50% of enrolments, AND Rule 1 (Muster) files ≥ 20%.** | Share of `kurage_remember` events by `rule`. Both = **PREDICTED**; one = **SPLIT**; neither = **MISS**. | fewer than 200 enrolments | **PREDICTED**: both doors are live and the whole-fight leg may treat the queue as mixed. **MISS toward Muster**: the printed starter Muster does nearly all the work and the Exhaust synergy [USER] named is not being drafted — a pool finding. **MISS toward Exhaust**: Rule 1 is nearly invisible on a drafted deck, and whether the starter Muster earns its slot is [USER]'s. |
| `C4` | **How often the memory is DEAD, and which kind of dead.** The block is [USER]'s own clause and the failure mode nobody has measured: an unaffordable front holds everything behind it. | **BLOCKED ≤ 25% of player turns.** | BLOCKED turns ÷ all player turns. **≤ 25% = PREDICTED; > 25% to 50% = SPLIT; > 50% = MISS.** EMPTY is reported beside it and graded by nothing. | never — the same denominator as `C1` | **PREDICTED**: the block is an occasional tempo cost and the whole-fight leg watches the rhythm. **MISS**: the block is the dominant state, the jam is the thing to watch live, and *whether an unaffordable front should ever be skippable* becomes a real design pick for [USER] — one this read may not settle. |
| `C5` | **Memory/Order spam — is replaying the memory all she does?** §13.7's third question, made countable. | **Memory copies are ≤ 25% of all cards that entered play, AND ≤ 10% of player turns are turns on which the ONLY card played was the memory's.** | Both off the per-turn segmentation. Both = **PREDICTED**; one = **SPLIT**; neither = **MISS**. | fewer than 500 player turns | **PREDICTED**: the memory is a beat inside her turn rather than the turn, and the spam worry is retired *for the sim seat*. **MISS**: the spam worry is CONFIRMED at the level of counts, and the whole-fight leg is staged to ask a reader whether it FEELS like spam — which is the only instrument that can answer that. |
| `C6` | **The 3× price, and the free replay.** A 0-cost memory costs 0 Charge and fires the moment it reaches the front. If nearly every fire is free, the price rule is not the governor and "3×" is priced against almost nothing. | **≤ 50% of fires are at price 0.** | Share of `kurage_memory_fire` events with `price == 0`. **≤ 50% = PREDICTED; > 50% to 75% = SPLIT; > 75% = MISS.** Median fired price and median bank at fire ride beside it, graded by nothing. | fewer than 100 fires | **PREDICTED**: the 3× price binds on most replays and the lever is real. **MISS**: the engine is mostly a free-replay engine; the price is not what governs the cadence, and any later proposal to move the 3 must say what it is actually moving. Either way **no number here re-prices anything** — the 3 is [USER]'s placeholder and this read does not adjust it. |
| `C7` | **The uncapped queue.** [USER] declined a cap — *"I don't think we need to cap this"* — on the argument that the one-fire-per-turn clause and the bank bound it. This is that argument's instrument. | **Median queue length at a player turn ≤ 3, AND the 95th percentile ≤ 8.** | Queue length off each turn's own state event. Both = **PREDICTED**; one = **SPLIT**; neither = **MISS**. Max observed rides beside it. | fewer than 500 player turns | **PREDICTED**: the no-cap decision is supported at the level of counts and `KURAGE_QUEUE_CAP` stays 0. **MISS**: a backlog forms that the fire rate cannot drain, which is the first evidence for the cap knob — and it returns to [USER] as a numbered pick, never as an edit made here. |
| `C8` | **The Exhaust fuel a drafted deck actually holds.** The enrolment door and the Charge funnel both run on Exhaust; `EB-234` asks what happens once Exhaust cards are drafted in, and this is the deck-side half of that question. | **The median FINAL deck holds ≥ 4 cards that print Exhaust.** | Sheet read (`Card.exhaust`) over `RunResult.deck_ids`, median over runs. **≥ 4 = PREDICTED; 2 to < 4 = SPLIT; < 2 = MISS.** | never | **PREDICTED**: the fuel is drafted and `C1`'s cadence is attributable to the deck. **MISS**: the drafter does not take Exhaust rows, which is a SCORER finding rather than a rule finding — it goes to `BACKLOG` as an instrument row and the whole-fight leg must GRANT its Exhaust cards rather than expect a draft to find them. |
| `C9` | **Ethereal — an INSTRUMENT CHECK, not a reading about the keyword.** | **EXACTLY 0** drafted decks hold an Ethereal card, and **exactly 0** enrolments come from one. | Share of final decks containing a card with `Card.is_ethereal`. **Exactly 0 = PREDICTED; anything > 0 = MISS**, which would mean §15.2's seam read is wrong and its Ethereal paragraph would be withdrawn. | never | **PREDICTED**: the Ethereal half of `EB-234` is unanswerable in the sim, is recorded as such, and is carried to the whole-fight leg or to authoring. **MISS**: the seam read is wrong and §15.2's Ethereal paragraph is struck, not rewritten (R101b). |

**RECORDED AND NOT GRADED**, in the same record, with no threshold and no
decision attached — they are context for whoever reads the graded nine:

- `R1` fires per RUN and per FIGHT (mean, median, max), and the fire rate by act
  in full rather than as `C2`'s two endpoints.
- `R2` the refusal ledger by reason (`already` / `copy` / `junk` / `x_cost`) and
  the count of `kurage_memory_full` events, which must be 0 under an uncapped
  queue.
- `R3` **the whole flag-OFF control arm**, same cell and seeds.
- `R4` win rate and mean deck size on both arms. **Diagnostics only. NOT A
  BALANCE CLAIM and not quotable** (R213 B / R215 B, Guardrail-7).

**Contamination and blind spots, stated before the run.**

1. **The pilot does not value the queue at all.** §6.1 says it in terms this
   read inherits whole: `pilot/policy.py` does not know that playing a Companion
   banks a replay, does not know a fire is a turn away, and does not steer play
   order. So every number below is a **FLOOR** produced by a pilot that is not
   trying — a human who plays toward the memory can only make the cadence
   higher, the queue longer and the spam worse.
2. **`C5` is therefore the weakest slot on this instrument**, and its MISS is
   worth more than its PREDICTED: a PREDICTED says a pilot that ignores the
   memory does not spam it, which is nearly a tautology, while a MISS says the
   spam appears even without anyone trying.
3. **The sim has no display.** Nothing here measures legibility, the strip, the
   gauge, a badge or a player's understanding. §14's element is not on trial.
4. **Three repairs landed immediately before this section** (§15.2). They are
   the difference between a crash and a run, so the arm measured is the repaired
   one and nothing taken before them is comparable to it — nothing was.
5. **No number taken off this arm is quotable as balance** (R213 B / R215 B).
   The quarantined surface exists to be PLAYED, not measured; what is measured
   here is a CADENCE — counts of events per turn — and never whether the rule is
   any good.
6. **One character, one archetype, one route, one policy, one seed base.** Six
   hundred runs is a sample of one cell, not of the game.

### 15.5 What actually ran

**RUN 2026-08-30.** `PYTHONPATH=. python -m tier05.exp_kurage_cadence_s1 --json
review/qa/kuragecad-s1/record.json`, 600 runs per arm at seed 11, `jobs=1`,
**about two and a half minutes for both arms** — far inside §15.3's registered
thirty. The record, the raw JSON and the driver's unedited stdout are under
`review/qa/kuragecad-s1/`.

**The stamp is the one §15.3 declared: `RT12/D18/P11/C21`**, read live off
`cells.world_stamp()` at run time and printed in the record's header. The world
did not move under this read, so there is nothing to disclose and nothing to
re-run.

**One instrument note, and it is a reading of §15.2's own definition rather than
a change to it.** A FIRE turn's queue length is that turn's
`kurage_memory_fire`.`remaining` **plus one**, because `remaining` is counted
after the front has been popped and the definition is the length *at the turn*.
BLOCKED and EMPTY take their event's `queued` unmodified. This is in the
instrument's pin (`test_a_turns_state_is_its_one_memory_event`), which was
committed before the run.

**0.03% of the arm's player turns carry no memory state event at all** (26 turns
of 78,126). They are reported in the record as `no_state_share` and are **not
diagnosed here** — at that size they move no slot in either direction, and
guessing at a cause after the fact is exactly what a registered read is for
avoiding.

### 15.6 The slate, graded

**5 PREDICTED / 3 SPLIT / 1 MISS / 0 UNREACHED.** Every grade is the committed
grader's own output against §15.4's registered thresholds and no others.

| slot | grade | the read | the registered threshold |
|---|---|---|---|
| `C1` the fire rate | **PREDICTED** | **60.90%** of 78,126 player turns end in a FIRE | ≥ 20% PREDICTED, 5–20% SPLIT, < 5% MISS |
| `C2` cadence act 1 → act 3 | **PREDICTED** | act 1 **47.14%** (n=26,491) → act 3 **71.24%** (n=18,232) | act 3 > act 1 AND act 3 ≥ 1.25 × act 1 |
| `C3` what sits in the memory | **PREDICTED** | Exhaust **61.0%** / Muster **39.0%** of 108,177 enrolments | Exhaust ≥ 50% AND Muster ≥ 20% |
| `C4` how often it is dead | **PREDICTED** | BLOCKED on **10.78%** of turns; EMPTY **28.29%** (ungraded) | ≤ 25% PREDICTED, 25–50% SPLIT, > 50% MISS |
| `C5` Memory/Order spam | **PREDICTED** | memory copies **12.02%** of 395,926 plays; memory-only turns **1.73%** | copies ≤ 25% of plays AND memory-only ≤ 10% of turns |
| `C6` the 3× price and the free replay | **SPLIT** | **57.2%** of 47,577 fires are free; median fired price **0**, median bank at fire **5** | ≤ 50% PREDICTED, 50–75% SPLIT, > 75% MISS |
| `C7` the uncapped queue | **SPLIT** | median queue **2.0**, **p95 9.0**, max **31**; 0 queue-full events | median ≤ 3 AND p95 ≤ 8 |
| `C8` drafted Exhaust fuel | **SPLIT** | median **3.0** Exhaust cards per final deck (mean 3.26) | ≥ 4 PREDICTED, 2–4 SPLIT, < 2 MISS |
| `C9` Ethereal — instrument check | **MISS** | **165** of 600 final decks hold an Ethereal card; **0** enrolments do | exactly 0 and 0 PREDICTED, anything > 0 MISS |

**The two arms side by side.** The flag-OFF column is `R3`, the paired control,
and it is **RECORDED, NOT GRADED**.

| | flag OFF (control) | flag ON (the arm) |
|---|---|---|
| runs / fights / player turns / card plays | 600 / 7,457 / 39,003 / 156,431 | 600 / 13,587 / 78,126 / 395,926 |
| turn state FIRE / BLOCKED / EMPTY | — (no rule) | **60.90% / 10.78% / 28.29%** |
| fire rate act 1 / 2 / 3 | — | **47.14% / 66.16% / 71.24%** |
| enrolments (Exhaust / Muster) | 0 | **108,177 (61.0% / 39.0%)** |
| fires (share free) | 0 | **47,577 (57.2%)** |
| fires per run, mean / median / max | 0 | **79.3 / 81 / 141** |
| queue length median / p95 / max | 0 | **2.0 / 9.0 / 31** |
| refusals by reason | — | `already` 1,314, `junk` 895; no `x_cost`, no `copy` |
| median Exhaust cards in the final deck | 2.0 (mean 2.52) | **3.0 (mean 3.26)** |
| mean deck size | 23.9 | 31.3 |
| runs won — diagnostic, NOT A BALANCE CLAIM (R215 B) | 4.3% | 26.7% |

**What each registered decision now says, quoted from §15.4 and applied.**

- **`C1` and `C2` PREDICTED, and they are one finding.** §15.4: *"the memory has
  a cadence on a drafted deck, and the whole-fight leg is staged to watch a
  RHYTHM."* Taken. The memory fires on **three turns in five**, and the rate
  climbs from just under half of act-1 turns to just over seven in ten by act 3
  — the drafted engine behaves like a drafted engine. **`KURAGECAD-W1` is
  therefore staged as a RHYTHM fight**, which is the one thing §15.7 said this
  leg hands it.
- **`C3` PREDICTED.** Both doors are live on a deck the drafter built — the
  Exhaust door carries the queue at 61% and the Muster door is a full 39%, so
  the whole-fight leg may treat the queue as mixed and the printed starter Muster
  is not carrying the rule by itself.
- **`C4` PREDICTED**, and the shape underneath it is worth naming: the block is
  an act-1 phenomenon (19.16% of act-1 turns) that **falls to 3.81% by act 3**
  as the bank outgrows the prices. The jam is a *teaching-stage* state, not a
  late-run one. §15.4's PREDICTED branch is taken: the block is an occasional
  tempo cost, and the whole-fight leg watches the rhythm rather than the jam.
- **`C5` PREDICTED, and §15.4's own blind spot 2 applies to it.** Memory copies
  are an eighth of what she plays and she almost never plays *only* the copy
  (1.73% of turns). But the registration wrote before the run that a PREDICTED
  here is nearly a tautology — the pilot never plays toward the queue — so this
  retires the spam worry **for the sim seat only**, and the whole-fight leg still
  has to ask a reader whether it FEELS like spam.
- **`C6` SPLIT.** The free replay is the **majority** of fires (57.2%) and the
  median fired price is **0**. §15.4's SPLIT branch carries no decision beyond
  recording it, and this section takes none: what the number says is that the 3×
  price governs a large minority of replays rather than most of them, and **no
  re-price is proposed, derived or implied** — the 3 is [USER]'s placeholder and
  this read does not adjust it (§13.7's first bullet).
- **`C7` SPLIT, and this is the slot that returns to [USER].** The median queue
  is short (2) and the tail is not: **p95 9, max 31**. §15.4 registered a MISS as
  the first evidence for the cap knob; a SPLIT is half of that, and it goes back
  as a numbered pick and not as an edit — *does an uncapped memory that reaches
  thirty entries in the tail want a cap, a drain, or nothing?* [USER]'s words
  were *"If you load Memory with 20 cards, they slow-play over 20 turns … if you
  have the Charge"*, and the tail says that is a real state and not a
  hypothetical.
- **`C8` SPLIT.** The median drafted deck holds **3** Exhaust cards against the
  control's 2. The fuel is drafted, but thinly; §15.4's MISS branch (grant the
  Exhaust cards live) is NOT triggered, and the SPLIT means `KURAGECAD-W1` may
  draft or grant its Exhaust rows, with the choice made when its board is staged.
- **`C9` MISS, and §15.2's Ethereal paragraph is STRUCK as the slate said it
  would be** (R101b: struck, never rewritten). What was wrong is narrower than
  the paragraph: the sheet read missed **`curse_clumsy`**, a CURSE that carries
  `tags: [ethereal]` and reaches a deck through an event, which is why 165 of 600
  final decks hold an "Ethereal card" and 87 of the control's do. **The enrolment
  half held exactly as written: 0 of 108,177 enrolments came from an Ethereal
  card**, because the memory's door refuses junk. So the registered conclusion
  stands on its own terms — **`EB-234`'s Ethereal question is unanswerable in the
  sim** — but for a different reason than the one §15.2 gave: the only Ethereal
  cards a Kokomi run can hold are ones the memory is not allowed to remember.

**What this read does NOT establish. Named so the next registration cannot
borrow more:**

1. **No balance claim of any kind** (R213 B / R215 B, Guardrail-7). The flagged
   arm's runs are longer and win far more often than the control's — 13,587
   fights against 7,457, 26.7% against 4.3% — and **that comparison is not a
   measurement and may not be quoted as one.** It is recorded because it is a
   **denominator fact**: every share in the arm column is taken over the turns of
   longer runs, so ON and OFF are not two samples of one population.
2. **Nothing about legibility.** The sim has no display; §14's element, the
   strip and the gauge were not on trial and are not graded by anything here.
3. **Nothing about the dose.** `C1` says the rule fires often; it does not say
   that is the right amount, and no constant is moved by this section.
4. **One character, one archetype, one route, one policy, one seed base.**

**Findings for the next sitting — written down, NOT settled here.**

- **`F1`** The `is_junk` predicate is a RARITY test and the engine synthesizes
  its Statuses at `rarity="basic"`. Repair 2 fixed the memory's door; the same
  blindness still sits on the **shipped** conscript pool and Charge funnel, which
  share the predicate. Narrowing it would move shipped numbers, so it is
  [USER]'s, not hygiene. The arm refused 895 such enrolments, so the case is not
  rare.
- **`F2`** The arm's survival and deck size diverge sharply from the control's.
  Whatever that is, it is not measured here and this section makes no claim about
  it; it is flagged because anyone reading the two columns will want to.
- **`F3`** `C7`'s tail (p95 9, max 31) is the cap question, and it is a pick for
  [USER] as written above.
- **`F4`** The Ethereal keyword has exactly one draftable carrier in the whole
  repository and it is Klee's. Whether Kokomi's pool should print one at all —
  which is what would make `EB-234`'s Ethereal half answerable anywhere — is a
  design question nobody has asked yet.

### 15.7 THE SECOND LEG, OWED: `KURAGECAD-W1`, the whole fight

**NOT TAKEN TONIGHT, and named here so the sim leg cannot be mistaken for the
whole of `EB-234`.** The row's own next action is *"sim first, then a whole
fight"*, and this is the whole fight, registered as owed:

- **Unit:** one complete fight on a DEVELOPED Kokomi deck under the memory flag,
  through `understudy.blindplay session`, with `EB-229`'s forecast channel
  available and its error direction to be declared at drafting.
- **Gate: GAME TIME.** It needs a `+proto` build, a staged deck and an operator;
  none of that is spent here.
- **What it inherits from this leg, and only this:** the STAGING SHAPE — a
  rhythm fight or a jam fight, per `C1`/`C4` — and, if `C8` MISSES, the
  instruction to GRANT the Exhaust cards rather than draft them.
- **What it may NOT inherit:** any threshold. Every slot it carries is drafted
  fresh from written intent when it is drafted, because a sim count and a
  reader's page are not the same evidence, and a number borrowed across that
  line would be a threshold wearing a measurement's clothes.
- **The Ethereal half of `EB-234` rides on this leg or on authoring**, per `C9`:
  the sim cannot reach it.

Its slate is **not drafted in this section** — drafting it before the sim leg
named the staging shape would be a slate against an unknown board. R231 named
that shape (a RHYTHM fight) and authorised the drafting, so **the slate is
§15.8**, and it is registered there, not run.

### 15.8 `KURAGECAD-W1` — THE RHYTHM FIGHT, the slate

**REGISTERED — NOT RUN. Drafted by Claude from written intent under R212 item
2 and committed BEFORE anything is staged, deployed, launched or read.
[USER] countersigns in BATCH, or vetoes.** Nothing in this section has been
run: no build has been made, no deck granted, no seat called, the game has not
been launched, and no number below was chosen after seeing a result. **R231
authorises the drafting and the staging shape — *"authorize drafting and
staging it as a rhythm fight, but do not countersign a blank registration"* —
and the countersign is a separate act that has not happened.**

> **COUNTERSIGNED (R233, 2026-08-30): `KURAGECAD-W1` is SIGNED**, in the batch
> of three, on the pair review's narrow revision — [USER]'s *"REVISE all three
> on the narrow points above; countersign immediately afterward"*. The
> revision this slate carried is that **the granted deck is relabelled an
> intentionally enriched stress deck and the jam-is-a-floor claim is
> WITHDRAWN**; nothing else in the slate moved. Signed once and never
> re-signed (R212, `EXPERIMENTS.md` *Countersign once*). R233 released it to
> run at its own gate, game time — **and it HAS RUN: see §15.9,
> `KURAGECAD-W1` — RUN AND GRADED, 2026-08-30** on `0.2.1786+proto.dirty`,
> sealed record `review/qa/blindplay/20260831-023544/`. The registration text
> above stands as registered and is not edited by either act (R101b).

**One hygiene edit is disclosed with this section.** §15.7's closing sentence
said the slate was not drafted there because its gate was undischarged; R231
discharged the shape question, so that sentence now points here. Nothing else
in §15.1–§15.7 is touched, and no grade, threshold or number published in §15.6
is re-read, re-graded or rewritten (R101b).

**Two R231 rulings BIND this draft and are quoted before anything is written
against them:**

1. **The queue stays UNCAPPED.** `KURAGE_QUEUE_CAP` is 0 and stays 0 through
   this cell. `C7`'s SPLIT (median 2, p95 9, max 31) is NOT a cap case being
   built here: `K3` below examines the tail for **READABILITY and JAM on a live
   page**, and its MISS opens a numbered pick for [USER] rather than a knob.
   **No result in this section licenses a cap, a drain, or any edit to that
   constant.**
2. **Ethereal is DEFERRED.** No slot below may demand an Ethereal carrier, no
   board may be shaped to produce one, and nothing granted carries the keyword.
   `C9`'s finding stands as published: `EB-234`'s Ethereal half is unanswerable
   in the sim, and it is not answered here either — it rides on authoring.

#### 15.8.1 The shape, and why it is a RHYTHM fight and not a jam fight

§15.7 registered exactly one inheritance from the sim leg — **the staging
SHAPE** — and §15.6 discharged it: `C1` and `C2` PREDICTED (the memory fires on
three turns in five, climbing 47.1% → 71.2% act 1 → act 3) and `C4` PREDICTED
with the block fading 19.2% → 3.8%. So the live leg watches whether that beat
is **legible, forecastable and hers**, not whether the block jams her.

**What that inheritance is NOT.** Not a threshold. Every number in §15.6 is a
sim count taken by a pilot that does not know the memory exists; every
threshold below is drafted fresh from §11's written intent and from the
element's own printed page (§14.9), and where a sim number appears at all it
appears as a **COMPARATOR, never a threshold** and never a falsifier.

#### 15.8.2 The unit, the build, the deck

| | |
|---|---|
| unit | ONE `understudy.blindplay session` on a live dev build, Codex seat, the whole fight and any fights the action budget reaches. A run, not a staged turn: a rhythm is a property of consecutive turns and no `understudy/turns/` board can hold one |
| build | a `+proto` build carrying the memory rule and §14's element, deployed with `validate.ps1` whole, game v0.111.0 (the pin). The exact version string is read off the deploy and printed in the results header; a build that is not `+proto` REFUSES the granted prototype row and the session does not start |
| character | Kokomi, `understudy.embark --character kokomi` |
| the deck | the twelve-card starter under the flag (`to_the_front` substituted in, per §15.2) **plus five GRANTED rows**, below |
| gate | **GAME TIME**, undischarged as this is written: a build, a deploy, an operator and the seat's window |
| forecast channel | **ON** (`--forecast`), three questions, §15.8.5 |
| budget | `--max-actions 40`, `--max-refusals 2`, one fight record and one run record — worst case **45 Codex calls**, which is `KLEESPARK-W3`'s shape and its actual spend. **Cap 45** |

**THE GRANT, named before the run, and its direction declared.** `C8` came back
SPLIT — the median drafted deck holds **3** Exhaust rows — and §15.6 read that
as leaving this leg free to draft or to grant. **It grants**, because a blind
session cannot be asked to draft its way to a developed deck inside 40 actions.
**What it grants is an INTENTIONALLY ENRICHED STRESS DECK** — it stresses the
queue on purpose, and it is kept for exactly that reason:

| granted | why it is there | the door it opens |
|---|---|---|
| `proto_kurages_oath_memory` ×1 | the ruled 3-Block face; the only prototype row in the grant, and the reason the build must be `+proto` | reads the memory, grades nothing |
| `conscription_notice` ×1 | a second Rule 1 door beyond the printed starter Muster | **Muster** |
| `sucrose_astable` ×1 | a **0-cost** Companion that prints Exhaust — the free-replay case ([USER]'s own Gorou example) at price 0 | **Exhaust**, price 0 |
| `bennett_fantastic_voyage` ×1 | a **1-cost** Companion that prints Exhaust, so a PRICED memory at 3 Charge exists and the 3× rule can bind at all | **Exhaust**, price 3 |
| `waterspout` ×1 | a non-Companion Exhaust row: it pays 1 Charge and it does **not** enrol | income, and the readability case that separates the two |

**The deck is ENRICHED, and no error direction may be claimed from it.**
*Revised 2026-08-30 on the pair review's correction: this paragraph previously
said three granted Exhaust rows made the live deck "no richer" than a drafted
one, that a queue running long here could only run longer on a drafted deck,
and that a jam observed was therefore a FLOOR. **All three claims were wrong at
their first premise** — they counted only the grant and forgot the starter.*
Kokomi's twelve-card starter already prints an Exhaust row: `gorou_inuzaka_charge`
(cost 0, `exhaust: true`, `tier0/content/characters/kokomi.yaml:104`), the very
card [USER]'s free-replay example names. Sucrose, Bennett and Waterspout make
**FOUR Exhaust printers** in the live deck against the sim's drafted median of
**three** — richer, not equal — and `conscription_notice` is a second Muster
door that can enrol *further* rows mid-fight, above whatever the deck printed.
So:

- **This deck OVER-SAMPLES enrolment pressure.** It is a stress deck, staged
  deliberately, and every queue observation on it is taken under more fuel than
  a median drafted deck carries.
- **A jam observed here is NOT a floor and licenses NOTHING beyond returning
  the pick** §15.6 already opened. It is not evidence that a drafted deck jams,
  it does not bound how a drafted queue behaves, and no monotonic extrapolation
  runs from this deck to a typical one in either direction.
- **A clean run here does NOT clear a drafted deck either.** One fight, one
  deck, one seat: absence of a jam under this much fuel is not a result about
  less fuel — the fight sampled a different deck, not a milder one.

Two Companions against two Musters is the thinner half of §15.6's 61/39 door
split, which is a fact about the door mix and is not a compensating discount on
any of the above.

#### 15.8.3 What refuses a slot, and what refuses the session

**These refuse the SESSION before a page is read** — the round stops, nothing
is graded, and the failure is reported as a staging failure and never as a
result: the game lock absent; Steam running at deploy; the installed build not
proven `+proto` and read-only for the granted row; R225's soak gate (`fights=3
defects=0`) not green; `EB-227`'s window guard at 85% of the five-hour window
or 50% of the week; the pck contract check non-empty; `embark` half-granting
its arms (`grant_arms` raises rather than carrying on); or the run's seed not
re-read off the wire into the sidecar (`EB-191`).

**These refuse a SLOT, written before the run so an absence cannot be read as a
pass.** Every UNREACHED rule below is a denominator rule. **An UNREACHED slot
is not a pass and not a fail**: nothing is inferred from it, no [USER] row
opens on it, and the act it licenses is another fight, never a reading.

**Definitions, fixed here, all read off the run's own artefacts** — the sealed
record's combat pages, the per-page `wire.json` snapshots (`EB-216`) and the
forecast rows (`EB-229`). None is read off prose written after the fact.

- A **combat page** is one page of the sealed record whose screen is combat and
  which carried a command. Page count is the denominator of every share below.
- A **QUEUED page** is a combat page whose snapshot shows a non-empty memory.
- **FIRES-NEXT truth** is that page's snapshot `fires_next` / `blocked` pair;
  **RUN-OUT truth** is its `run_out_index` (`-1` meaning the bank covers the
  queue). Both are the wire's, never a reconstruction and never the page prose.
- A **FIRE** on a page is that page's fight log carrying the memory's own play
  at the start of the turn the page opens.
- A **JAM EPISODE** is **three or more consecutive combat pages** all showing
  `blocked` true with a queue length that never decreases across them.
- A **STEER** is a `thinking` or forecast sentence naming what this turn will
  put into the memory, or what the Charge is being kept for — the player's own
  words, judged only for whether they name the memory as an input to the line.

#### 15.8.4 The slate — five graded slots and one recorded

| # | slot | prediction | falsifier, mechanically | UNREACHED when | the decision the outcome changes |
|---|---|---|---|---|---|
| `K1` | **READABILITY — can the blind player read the memory off the live frame?** Two halves, the two facts §14's element prints as separate lines: (a) does anything fire at the start of the next turn, and (b) where does the Charge run out. Asked BEFORE the line is played, so it is a forecast and not a description. | **Half (a) correct on ≥ 5 of the first 6 QUEUED pages, AND half (b) correct on ≥ 5 of the first 6 QUEUED pages.** | Each answer against that page's own snapshot: (a) against `fires_next` / `blocked`, (b) against `run_out_index` — naming the entry, or saying the bank covers the queue. Both halves = **PASS**; one = **SPLIT**; neither = **MISS**. **A wrong call in the FIRES direction is the serious one** and is reported separately. | fewer than 6 QUEUED pages. Half (b) is separately UNREACHED where **no** page carries `run_out_index ≥ 0` — the bank never ran out, which is a DOSE observation and not a display result | **PASS**: the element reads on a live page, and `EB-198`'s acceptance is discharged **for the page mirror** (§15.8.6 — the tie is folded in deliberately and its limit is stated there). **MISS**: the rebuild §14 shipped is still not readable, which is a DISPLAY finding, filed to `BACKLOG` as a page or element row, and **never** a re-price and never a dose change. |
| `K2` | **THE CADENCE, live.** Does the memory fire on a regular beat when a player, not a pilot, is steering? This is the slot §15.6's `C1` / `C2` staged, asked where a reader is looking. | **The memory fires on ≥ 25% of combat pages.** | FIRE pages ÷ combat pages. **≥ 25% = PASS; 10% to < 25% = SPLIT; < 10% = MISS.** | **fewer than 8 combat pages** — the honest small-denominator rule: one fight is one fight | **PASS**: the beat survives contact with a player and the rhythm is real on the page as well as in the counts. **MISS**: the live beat is nothing like the sim's, and the FIRST question is which of the two seats is wrong — an instrument question before a design one, and no constant moves on it. **THE BAND IS DELIBERATELY WIDE AND ONE FIGHT CAN NEITHER CONFIRM NOR REFUTE 60.9%.** §15.6's rates ride beside this slot as a COMPARATOR and are not its threshold: a live share inside the band is not evidence the sim number is right, and one outside it is not evidence it is wrong. |
| `K3` | **THE TAIL, and whether it JAMS — R231's live re-read of the uncapped queue.** `C7` was a SPLIT about a distribution; this is about a page. Two clauses, both required. | **(i) ZERO jam episodes, AND (ii) on the LONGEST-QUEUE page of the session, `K1`'s two halves are both correct.** | (i) counted off consecutive snapshots by §15.8.3's definition; (ii) that page's forecast answers against its own snapshot. Both = **PASS**; one = **SPLIT**; neither = **MISS**. Peak queue length, and the queue length at every page, ride beside it and are graded by nothing. | fewer than 8 combat pages, or no page with a queue of ≥ 4 — a tail that never appeared was not examined, and **the absence of a long queue in one fight is not evidence that the tail is fine** | **PASS**: the uncapped queue is readable and does not jam **on this deck's live pages**; **no cap is proposed, derived or implied in either direction** (R231 A2), and — *revised 2026-08-30 on the pair review's correction* — a PASS on §15.8.2's INTENTIONALLY ENRICHED deck (four Exhaust printers against the sim's drafted median of three, plus a second Muster door) **does NOT clear a drafted deck**: this fight over-sampled enrolment pressure, and a clean read under extra fuel is not a reading about less. **MISS**: the tail is where the rule stops being legible, and it goes back to [USER] as the numbered pick §15.6 already opened — *cap, drain, or nothing* — as a pick and never as an edit made here. **A jam here is not a floor and extrapolates to nothing**: what it licenses is exactly the return of that pick. |
| `K4` | **IS IT HERS? — steering INTO the memory.** The `P3`-shaped question `KURAGEMEM002` could only ask backwards. A rhythm nobody plays toward is weather, not an engine. | **≥ 3 of the first 10 combat pages carry a STEER, AND at least one of them names a Muster-door play** (sacrificing a card to a Muster, in the player's own words, whatever they call it). | Both off the forecast rows and `thinking`. Both = **PASS**; one = **SPLIT**; neither = **MISS**. | fewer than 10 combat pages | **PASS**: the memory is an input to her turns, and §15.6's `C5` spam worry is answered in the right direction — she plays toward it rather than being played by it. **MISS**: the beat happens TO the player, which is a legibility-and-teaching finding (page and wording), filed to `BACKLOG`; it is **not** licence to change the dose, the 3× price or the one-per-turn latch. |
| `K5` | **THE BLOCK, named and unblocked.** [USER]'s own clause, on the first page it bites. §15.6 says the block is an act-1 state; a live fight is act 1. | **On the FIRST blocked page of the session, both halves: (a) the player says the memory is BLOCKED, distinctly from empty, and (b) names a play or a source that would unblock it.** | That page's answers against its snapshot's `blocked`. Both = **PASS**; one = **SPLIT**; neither = **MISS**. *"Not enough Charge yet, I will wait"* with no named source is the registered example of (b) failing. | **no blocked page occurs** — itself an observation about the dose at the granted deck's size, and inferred from in neither direction | **PASS**: the block teaches itself on the page, as §14's rebuild intended. **MISS**: the block is still the state the display loses, and it reopens the display row — **not** the question of whether an unaffordable front should be skippable, which is [USER]'s and is not on trial here. |

**`K6` — RECORDED AND NOT GRADED**, in the same record, with no threshold, no
falsifier and no decision attached. These are the four levers `EB-234` names,
and **one fight cannot ground any of them** — they are written down so the next
cell has a live reading to sit beside the sim's, and for no other purpose:

- **the 3× price and the free replay** — every fire's price and the bank it
  fired against, and the share of fires at price 0. Beside §15.6's 57.2% and
  **NOT a comparison**: a comparator, never a threshold.
- **the one-fire-per-turn latch** — pages where the queue held two or more
  payable entries and exactly one fired.
- **the block's incidence** — blocked pages as a share, beside `C4`'s 10.78%,
  same caveat.
- **the two doors** — enrolments by rule, beside `C3`'s 61 / 39, same caveat.
- **peak queue, fires per fight, and the granted rows' fate** — whether the
  granted Exhaust rows actually reached the memory.

**No number in `K6` may be quoted as balance, as a comparison against the sim
arm, or as evidence for or against any constant** (R213 B / R215 B,
Guardrail-7).

#### 15.8.5 `EB-229`'s forecast channel is ON, and its bias runs ONE WAY

Three questions, asked before the command on every combat page. They are
prospective on purpose: `KURAGEMEM002` graded slots on answers given after the
line was chosen, and §13.9 recorded that the prospective ask was never made.
The questions carry no design vocabulary and name no card, keyword, id or
ruling — `qa_packet.leaks` refuses the session otherwise, before a page is
written.

1. *"At the start of your next turn, will anything the jellyfish remembers play
   itself? Answer YES, NO, or NOTHING REMEMBERED — and if YES, name the card."*
2. *"Does your Charge cover everything the jellyfish is holding? If it does not,
   name the first one it does not reach."*
3. *"On the line you are about to play, what will this turn hand to the
   jellyfish to remember, and what are you keeping Charge for? If neither,
   write 'neither'."*

**THE ERROR DIRECTION, DECLARED BEFORE THE RUN, AND IT RUNS ONE WAY.** Asking
questions 1 and 2 on every page **points the player at the element every turn**,
and question 3 invites a plan the silent page never asked for. So the channel
makes `K1`, `K3`(ii), `K4` and `K5` **EASIER to satisfy**, and it can raise
`K2`'s share by making a player steer toward the memory who otherwise would
not have. Therefore:

- **a PASS on `K1`, `K3`, `K4` or `K5` is a CEILING**, not a floor — the best
  the display and the rule do when the player is prompted to attend to them
  every single turn, which no shipped game does;
- **a MISS on any of them is correspondingly STRONG**: they could not read it,
  or did not steer by it, even while being asked about it every page;
- **`K2` is inflated in the PASS direction** by the same mechanism, which is one
  more reason its band is wide and its comparator is not its threshold;
- **`K3`(i), the jam clause, runs the other way *for this contamination*:** a
  prompted player avoids jams a silent one walks into, so the forecast channel
  alone would make an observed jam a floor. *Revised 2026-08-30 on the pair
  review's correction: **that floor does not survive the deck.** §15.8.2's
  grant is an intentionally enriched stress deck — four Exhaust printers
  against the sim's drafted median of three, plus a second Muster door — and it
  pushes the jam clause the opposite way, over-sampling enrolment pressure. The
  two contaminations point in opposite directions with no way to net them on
  one fight, so **`K3`(i) carries NO declared error direction**: an observed
  jam is neither a floor nor a ceiling, and it licenses only the return of
  §15.6's pick.*

That trade is taken for the reason `KLEESPARK-W5` took it: the alternative is
mining `thinking` prose for a pre-commitment nobody was asked to make, which is
how `KURAGEMEM002` lost three slots to UNREACHED.

#### 15.8.6 The `EB-198` tie — folded in DELIBERATELY, and its limit stated

`EB-198`'s acceptance reads: *"a blind tester says off a live frame whether the
next memory fires, and where the Charge runs out."* That is `K1`'s two halves
word for word, and **the tie is folded in rather than kept separate**, because
asking the same question twice on two seats would spend game time to learn
nothing new.

**What the fold does NOT buy, and this is the honest half.** The blind seat
reads the record's **page**, which is a TEXT MIRROR of the element (§14.9's
one-fact-per-line rewrite), not the element on screen. A `K1` PASS says the
FACTS are readable in the order the element prints them; it does **not** say the
ring, the count and the pile view are readable as pixels — §14.10 and §14.11
took that half with sighted captures. So:

- **`K1` PASS ⇒ `EB-198`'s acceptance is discharged for the page mirror**, and
  the row's closure is a call [USER] makes at the countersign, on a record that
  says exactly which half was read.
- **`K1` MISS ⇒ `EB-198` stays OPEN**, and its next action becomes whatever the
  MISS names — wording, ordering, or a fact the page does not print.

#### 15.8.7 Contaminations, blind spots, and what this cell does NOT license

1. **The deck is GRANTED, not drafted, and it is ENRICHED**, as §15.8.2 lists.
   Nothing here is a drafted-economy reading, and `C8`'s SPLIT is not re-opened
   by it. *Revised 2026-08-30 on the pair review's correction: the starter's own
   `gorou_inuzaka_charge` prints Exhaust, so the granted deck carries FOUR
   Exhaust printers against the sim's drafted median of three, and
   `conscription_notice` can enrol more mid-fight. **This cell over-samples
   enrolment pressure by construction. No result on it extrapolates to a
   typical drafted deck in either direction** — a jam here is not a floor and
   is not evidence a drafted queue jams; a clean run here does not clear a
   drafted deck.*
2. **`+proto` build, prototype surface.** Every observation is about a prototype
   row and a flagged engine rule (R215 B). Nothing is quotable as balance.
3. **One fight, one seat, one deck, one build.** Every denominator below ten is
   named as such in the results; §15.8.4's UNREACHED rules exist because a
   fight that never posed a question measured the generator, not the rule.
4. **R217 G rides on every sentence the tester writes.** One model's account —
   never validation, never balance evidence, never approval.
5. **Neow.** `embark` leaves the run on the Neow screen, which cannot be skipped
   and two of whose three boons rewrite the deck. The operator takes **the only
   deck-neutral boon offered**, by `KLEESPARK-W4` §19.5's registered rule, and
   names which one it was in the results.
6. **`EB-191`** — the run seed is re-read off the wire from the same process
   before the session starts and written into the sidecar.
7. **`F1` is NOT folded in.** The `is_junk` rarity blindness §15.6 filed stays
   [USER]'s; nothing here grades it, and no refusal observed live settles it.
8. **The sim arm is not a control for this cell.** §15.6's ON / OFF columns are
   not two samples of one population, and a live page is a third thing again.

**This cell licenses NONE of the following, registered before the run so it
cannot be argued after** (*and, revised 2026-08-30 on the pair review's
correction, the list now explicitly includes any extrapolation from this
enriched deck to a drafted one — in either direction, from a jam or from a
clean run*)**:** a cap, a drain or any move to `KURAGE_QUEUE_CAP`
(R231 A2); a move to `KURAGE_MEMORY_COST_PER_ENERGY`, to the one-per-turn latch
or to any dose constant; a change to the memory's entry doors; an Ethereal
carrier anywhere (R231, deferred); a sheet move or an accept-to-sheet signoff
for `proto_kurages_oath_memory`; any LAW or measurement-law change; and any
claim about win rate, balance or fun (R215 B, Guardrail-7).

---

## 15.9 `KURAGECAD-W1` — RUN AND GRADED

**RUN 2026-08-30 on `0.2.1786+proto.dirty`** (`-p:PrototypeCards=true`, game
v0.111.0 `public-beta`), branch `bt3-w5-run`. Sealed record
`review/qa/blindplay/20260831-023544/record.md`, wire snapshots `wire.json`
beside it. Run seed `0EEMNL2RE8UY`, read back off the wire (`EB-191`). 40
actions, termination `max_actions`, 0 refusals, **22 combat pages**, forecast
channel ON with all three questions and **0 answered short**. Codex meter,
unsmoothed: **5h 1% / week 0%** before, **5h 8% / week 1%** after.

### 15.9.0 The build was PROVEN to carry the arm before the session, read-only

§15.8.3 refuses the session where the installed build is not proven `+proto`
and read-only for the granted row. Five checks, none of them assumed:

1. The deployed `mods\klee\manifest.json` reads **`0.2.1786+proto.dirty`**.
2. `embark --arm proto_kurages_oath_memory` was **accepted** — `--arm` refuses a
   prototype id unless the deployed build is `+proto`, so the acceptance is
   itself the proof, taken live.
3. `Kokomi.StartingDeck` slot eleven is `#if PROTOTYPE_CARDS →
   KurageMemory.StarterSlotEleven()` with `ModelDb.Card<BakeKurage>()` in the
   `#else`, so §15.2's starter substitution is in the deployed build **by
   construction**.
4. `KurageMemory` (the rule) and `KurageMemoryCard` (§14's element) both appear
   in the deployed `klee.dll`; `KurageMemoryLaw.AlwaysOn` is `true` in the
   source those types were compiled from.
5. Confirmed on the wire once the run opened: every one of the 22 snapshots
   carries a populated `kurage_memory` block with `base_kit: true` and
   `summon: true`.

**Nothing the slate assumes was dead in the world that ran.** All five granted
rows reached play and four of the five touched the memory as §15.8.2 said they
would — including *Waterspout*, which paid its Charge and did **not** enrol,
which is the readability case that separates income from enrolment and it
behaved exactly as written.

**Neow.** Three boons — *Neow's Torment* (add 1 Neow's Fury to your Deck),
*Golden Pearl* (gain 150 Gold), *Neow's Bones* (2 random Neow Relics, add 1
random Curse). The operator took **Golden Pearl**, the only deck-neutral boon
offered, by `KLEESPARK-W4` §19.5's registered rule.

### 15.9.1 The definitions, counted off the wire

| | count | how it was counted |
|---|---|---|
| combat pages | **22** | pages whose screen is combat and which carried a command; one snapshot each |
| QUEUED pages (`empty: false`) | **17** | snapshots 3–5, 7–9, 11–14, 16–22 |
| pages with `blocked: true` | **0** | the wire's own field, on every page |
| pages with `run_out_index ≥ 0` | **0** | `-1` on all 22 — the bank never ran out |
| peak queue length | **3** (fight 1), **2** (fight 2) | the `queue` array |
| FIRES | **3** | see the disclosure below |
| enrolments, by rule | **6 `exhaust` / 1 `muster`** | Sucrose, Bennett ×2, Gorou ×2, Thoma / Tactical Retreat |
| turns | **5** | fight 1 turns 1–3, fight 2 turns 1–2 |

**A DISCLOSED SUBSTITUTION in how FIRES were counted.** §15.8.3 defines a FIRE
as *"that page's fight log carrying the memory's own play at the start of the
turn the page opens."* **The sealed record carries no per-page fight log**, so
the fires were read off the wire instead — a turn-opening page whose queue is
shorter than the previous turn's last page, with the departed entry being that
page's front. It is a stricter reading, not a looser one (a fire that left no
queue transition would be missed, never invented), and each of the three is
named: snapshot **6** (Sucrose, front price 0, queue 1 → 0), snapshot **10**
(Bennett, front price 3, queue 1 → 0), snapshot **20** (Gorou, front price 0,
queue 2 → 1). The substitution is disclosed because a definition read off a
different artefact than the one registered is a change to the instrument, even
when it points the safe way.

### 15.9.2 The slate, graded mechanically

| slot | grade | the reading, and the rule it comes from |
|---|---|---|
| `K1` READABILITY | **half (a) PASS at 6 of 6; half (b) UNREACHED** | (a) On the first six QUEUED pages (snapshots 3, 4, 5, 7, 8, 9) the tester's answer 1 matched that page's own `fires_next` **and named the front card**, six times out of six — *"YES — Sucrose — Astable Anemohypostasis"* ×3, then *"YES — Bennett — Fantastic Voyage"* ×3, against a front of exactly that. The threshold is ≥ 5 of 6. **No wrong call in the FIRES direction on any page of the session.** (b) is UNREACHED by its own separate rule: **no page carries `run_out_index ≥ 0`** — the bank never ran out, which the registration calls *"a DOSE observation and not a display result"*. The tester answered *"YES"* (the Charge covers everything) on all 22 pages and was right on all 22, and that is exactly the answer the rule declines to count. |
| `K2` THE CADENCE, live | **SPLIT** | 3 FIRE pages ÷ 22 combat pages = **13.6%**, inside the registered band *"10% to < 25% = SPLIT"*. `S1`'s 60.9% rides beside it as a **COMPARATOR and not its threshold**, and the registration says in advance that one fight can neither confirm nor refute it. **The denominator asymmetry is recorded, not argued**: a fire is a property of a TURN and a page is a PLAY, so a turn with four plays offers one fire against four pages. On the per-TURN denominator the session read 3 of 5, and that number is a comparator too and grades nothing. |
| `K3` THE TAIL | **UNREACHED** | *"UNREACHED where … no page with a queue of ≥ 4."* The peak was **3**. Clause (i) would have held — **zero jam episodes**, `blocked` false on every page — but the tail this slot exists to examine never appeared, and the registration is explicit that *"the absence of a long queue in one fight is not evidence that the tail is fine."* **No cap, drain or dose is proposed, derived or implied in either direction** (R231 A2), and §15.6's pick does not return on this. |
| `K4` IS IT HERS? | **SPLIT** | Clause 1 **holds**: 3 of the first 10 combat pages carry a STEER (actions 4, 9, 13 — *"Sucrose …; keeping Charge for later costlier memories"*, *"Bennett …; keeping Charge for its replay"*, *"Gorou …; keeping Charge for later paid memories"*), against a threshold of 3. Clause 2 **fails**: none of those three names a Muster-door play. The session's one Muster STEER — *"the card Call to Arms Musters; keeping Charge for that new memory"* — is at action 15, the **twelfth** combat page, outside the window the slot registered. Both = PASS, one = SPLIT. |
| `K5` THE BLOCK | **UNREACHED** | *"UNREACHED where no blocked page occurs."* **None did**, on any of 22 pages. The registration calls that *"an observation about the dose at the granted deck's size, and inferred from in neither direction"*, and nothing is inferred from it here. |

**ONE CAUSE, THREE UNREACHEDS, and it is worth saying plainly.** `K1`(b), `K3`
and `K5` are all UNREACHED for the same reason: **the Charge was never scarce.**
The bank climbed to 8 while the longest queue was 3 and the most expensive front
cost 3, so nothing was ever blocked, nothing ever ran out and no tail formed.
§15.8.2 declared the deck **INTENTIONALLY ENRICHED** and warned it over-samples
enrolment pressure; what this fight shows is that the same grant **under-samples
SCARCITY**, and scarcity is what three of the five slots were about. That is a
fact about the deck, not about the rule: **no result here extrapolates to a
drafted deck in either direction** (§15.8.7 item 1), and a clean, unblocked,
never-exhausted queue on four Exhaust printers and a second Muster door clears
nothing at all.

### 15.9.3 `K6` — RECORDED AND NOT GRADED

No threshold, no falsifier, no decision attached, and **no number below may be
quoted as balance or as a comparison against the sim arm** (R213 B / R215 B).

- **The 3× price and the free replay.** Of the three fires, the fronts cost
  **0** (Sucrose), **3** (Bennett) and **0** (Gorou) — **2 of 3 at price 0**.
  Beside §15.6's 57.2% and **NOT a comparison**.
- **The one-fire-per-turn latch.** One instance: fight 2's turn-2 opening, where
  the queue held two payable entries (Gorou at 0, Bennett at 3) and exactly one
  fired.
- **The block's incidence.** **0 of 22 pages**, beside `C4`'s 10.78%, same
  caveat.
- **The two doors.** **6 `exhaust` / 1 `muster`**, beside `C3`'s 61 / 39, same
  caveat.
- **Peak queue, fires per fight, and the granted rows' fate.** Peak 3 and 2;
  fires 2 and 1. All five granted rows reached play: *Sucrose*, *Bennett* and
  *Gorou* enrolled by Exhaust, *Call to Arms* (`conscription_notice`) enrolled
  *Tactical Retreat* by Muster, *Kurage's Oath* (`proto_kurages_oath_memory`)
  was played, and *Waterspout* paid its Charge and did **not** enrol.

### 15.9.4 The `EB-198` tie — HALF discharged, and the row STAYS OPEN

`EB-198`'s acceptance is *"a blind tester says off a live frame whether the next
memory fires, **and** where the Charge runs out."* `K1` answers the first half
at **6 of 6** and the second half was **never posed** — the bank never ran out,
so there was nothing to point at. §15.8.6 gives the row's closure to [USER] *"on
a record that says exactly which half was read"*, and this is that sentence:
**the fires half is read and clean; the run-out half is unread.** `EB-198`
therefore **stays OPEN**, and its next action is a fight in which the Charge is
actually short of the queue — which this deck, by its own enrichment, could not
produce.

### 15.9.5 Out of slot — recorded, and two rows filed

Both are **display and wording** findings, which is the destination `K1`'s and
`K4`'s decision columns name; neither is a re-price, a dose change or a move to
any constant, and neither grades a slot.

- **The jellyfish's own text disagrees with what it does** (`EB-247`). Both
  fight records name it independently and unprompted: *"its persistent buff said
  it dealt damage scaling with Charge, but the memory forecast sometimes said it
  would give Block or deal only 4 damage"*, and again *"Its main text promised
  damage scaling with Charge, while the turn forecast often showed only 4 damage
  or 5 Block depending on the last card played."* The wire agrees with the
  tester: `pulse_kind` alternates `attack 4 damage` / `skill 5 block` page by
  page with the last card played, while the power's printed text promises
  Charge-scaled damage.
- **The memory's price cannot be derived from the printed face** (`EB-248`).
  The tester: *"Thoma's replay cost was 3 Charge despite text suggesting replay
  cost was based on the card's printed cost of 2."* The wire confirms it and
  explains it: `thoma_crimson_ooyoroi` prints **cost 2** on the sheet, the
  Muster that produced this copy discounted it, and the queue entry reads
  `cost: 1, price: 3`. The 3× rule is applied correctly to the card's EFFECTIVE
  cost; what the player cannot do is get from the printed 2 to the queued 3.
  **This is legibility, not arithmetic** — the rule is right and the page cannot
  be read.

Also recorded and grading nothing: the tester reports *"Bennett granted Strength
without an obvious visible Strength status or increased Water's Edge damage"*,
which is a Companion-face question outside this cell's scope and is left where
it lies rather than filed on one unreplicated sentence.

### 15.9.6 What this leaves

- **The element reads.** Six of six on the fires half, with the front card named
  every time, is the strongest thing this fight bought — and it is a **CEILING**
  by §15.8.5's declared error direction, taken with the player pointed at the
  memory every single page.
- **The beat is real but thin on this denominator**, and `K2`'s SPLIT is what a
  wide band on one fight was written to produce. Nothing about `S1`'s 60.9% is
  confirmed or refuted, exactly as registered.
- **The memory is an input to her turns, but the MUSTER door is not** — `K4`'s
  SPLIT is precisely that shape, and the one Muster steer arriving two pages
  late is a fact about when the door was drawn, not a reading about the door.
- **`K3` and `K5` are UNREACHED and license nothing.** §15.6's cap pick does not
  return, no dose moves, and the uncapped queue is neither cleared nor
  questioned by a fight that never filled it.
- **`EB-234`'s live half is answered only in part.** The rhythm is legible; the
  scarcity half of it was never posed. **The act that follows is another fight
  on a deck that can run the Charge out — not a reading, and not a constant.**
- **No [USER] row opens on this cell**, and no number, threshold or constant
  moved.
