# Design brief — the `unheard_confession` rework (2026-07-29)

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

**Status: BRIEF. Nothing here is ruled and nothing here is a recommendation.**
Options are laid out so they can be struck through with a pen rather than
argued with. No number below is PROPOSED — the numbers come after a direction
is picked.

**Trigger:** [USER] ruling 2026-07-29 against `docs/backlog-2026-07-29.md` §3
item 4 — *"on second read, this does way too much"* — recorded as **R87 (2)**.
The card goes to a design pass; **the A7 decay-ordering question is MOOTED**
and withdrawn (see §2). The same-day C# bug-fix pass was fenced off the decay
path and touched nothing there (`docs/sprint-bugfix-log-2026-07-29.md`,
"Still owed" §E).

**World:** RUNTEMPLATE 7 / CONSTANTS 4 / DRAFTER 12, going to DRAFTER 13
(R87 (3)). Every Fanfare number quoted here is post-single-leg (2026-07-28)
and pre-DRAFTER-13.

---

## 1. What the card does today, in full

`docs/furina-cards.yaml`. Rare **Power**, archon register, **cost 2** (1
upgraded), `solve: [block]`, `archetypes: [fanfare, generic]`, `role: payoff`.
Two effects, in this order:

1. `gain_fanfare_floor` **8** — printed as **"Fanfare +8"**: the rare-Power
   full grant, moving **current, floor and cap together**. Permanent for the
   combat, and the floor half means the meter never falls below it again.
2. `apply_power fanfare_delta_block` **1** — **gain 1 Block whenever Fanfare
   CHANGES AMOUNT, in either direction.**

**The order is load-bearing and is asserted on both sides** (A7 sprint §B.4):
the grant is written BEFORE the power installs, so the card does not pay
itself 8 Block for its own grant. Nothing in either engine prevents the
reverse — `note_fanfare_change` would happily pay it — so this is a
*sheet-ordering fact*, not an engine guarantee.

**How the rider actually behaves** (`docs/sprint-art-and-a7-log-2026-07-29.md`
§B.2, parity-pinned in both engines):

- **Flat 1 per change EVENT**, regardless of how far the meter moved. A
  1-point tick and a 40-point crash pay the same.
- **Four funnels pay:** `gain_fanfare`, `gain_fanfare_floor`, `decay_fanfare`,
  `drop_fanfare_to_floor`. `raise_fanfare_cap` is **deliberately excluded and
  pinned as an exclusion** — it moves the ceiling and never the meter, so
  wiring it would pay Block for every "Fanfare Cap +X" Power in the pool,
  twelve cards' worth of value nobody printed.
- **Inert at saturation.** A gain landing entirely at the cap moved nothing,
  so it is not a change. A meter resting on its floor likewise pays nothing
  for a decay that did nothing.
- **Settle points:** after a card play, at turn start, at `AfterPlayerTurnStart`
  for Salon upkeep's spend, at turn end, and — the one that matters for a
  defensive power — **`AfterDamageReceived`, which fires per damage
  instance**, so the Block is on the board before the next hit of the same
  turn.

**What it used to be**, because the rework history is short and relevant: a
1-cost Rare **Exhaust skill** healing 8 and granting 6 Encore. The A7 rework
(RULED 2026-07-28, playtest-2 red-pen) made it the Power above; **Exhaust was
dropped** the same day ("Exhaust on a power is redundant" — it existed only to
satisfy the conjunctive true-heal law, Guardrail 6, and the heal is gone);
`solve` was retagged `sustain -> block`. Track B of the Fanfare rework then
printed the previously-invisible grant as "Fanfare +8" — **not a buff**: a
rare Power received exactly 8 silently before.

---

## 2. Why the A7 decay ruling is mooted

The A7 sprint found (§B.3) that the card's stated reason for existing does not
hold **in either engine**:

> `combat._player_turn` calls `resources.decay_fanfare` at line 424 and clears
> Block at line 430. Six lines.

Decay is the only downward mover in the game, it fires once per turn at the
top of the turn, and its Block is destroyed immediately afterward on every
turn without Barricade. The C# flush sits inside `BeforeSideTurnStart`, the
broadcast `AfterBlockCleared` follows, so both engines lose it identically —
**ported faithfully rather than quietly improved**, because moving the C#
flush one broadcast later looks like a fix and is in fact a C#-only buff worth
~1 Block/turn that the sim never pays and no measurement has ever priced.

So the sheet comment's *"pays on the way down as well as the way up, which is
what makes it a fanfare-archetype engine rather than a second gain-rider"* is
**not what the card does today. It is a gain-rider.**

The question routed to [USER] was: move the sim's turn order, or leave both
engines as they are. **That question is now withdrawn.** It is a question
about which engine should pay for a card that is being rewritten, and its
answer would be an unpriced buff to a card whose problem is that it already
does too much. If a rework wants a decay payout, the turn-order question
returns as a *consequence* of that rework, priced with it — not as its
premise.

**What must survive the rework regardless:** the ordering is pinned by tests
in both engines with the reason written into the C# comment, so nobody
"fixes" it by accident. Do not delete those pins as part of a rework; re-aim
them.

---

## 3. The case that it does too much

Stated as an inventory, because the count is the argument:

1. A **permanent Fanfare +8** — the full rare-Power grant, floor included.
2. An **unbounded per-event Block engine** with no per-turn cap.
3. That reads a meter with **five distinct movers** (card grants, floor
   grants, decay, crash, and every mint from HP loss / Encore spend / Encore
   absorption / Spotlighted plays).
4. **In both directions**, so the card cannot be turned off by playing badly.
5. Firing **per damage instance**, which makes it a *defensive scaling* card
   on top of everything else — a multi-hit enemy pays it repeatedly within
   one turn.
6. At **2 energy**, 1 upgraded, on a Power that leaves the deck when played.

Points 2 and 5 are the ones the sheet never priced: the card's rate is set by
how *busy* the meter is, and the meter got busier in the same week (single-leg
Fanfare added `encore_absorbed` as a fifth generation leg). Nothing about the
card was re-measured after that.

**Countervailing facts, so the pen has both sides:** the fanfare archetype is
under a **pre-registered STOP at 1.8% against its 2.0% floor** (fanfare
compensation sprint), and the reader-density compensation pass did not clear
it. This card is one of the archetype's few payoffs. A rework that only
subtracts makes a dead archetype deader; that is a design outcome someone has
to choose on purpose, not a side effect.

---

## 4. Rework directions — options, not decisions

Each option names what it gives up. None is costed; costs come after a pick.

### Option A — one card, one job: keep the payoff, delete the engine

Keep **Fanfare +8**; drop `fanfare_delta_block` entirely and replace it with a
single legible payoff line (a one-shot conversion, or a static rider that
reads the meter once). The card becomes what its rarity says it is: a rare
Power that *raises the meter*, in a pool where the meter is the archetype.

- **Gives up:** the defensive identity, and the only card that pays for a
  meter *moving* rather than for its level. `solve: [block]` would revert.
- **Watch:** with the engine gone, is there any reason for this to be a Power
  rather than a cheaper skill? R6 (lint) requires `gain_fanfare_floor` to sit
  on a rare POWER, so the answer determines the rarity, not the other way
  round.

### Option B — one card, one job, the other way: keep the engine, drop the grant

Delete `gain_fanfare_floor`; the card is purely *"gain 1 Block whenever
Fanfare changes."* Frees it from the rare-Power fence (R6), so it can drop
rarity and cost and become the fanfare archetype's cheap defensive backbone
instead of one of its scarce payoffs.

- **Gives up:** a rare payoff slot the archetype is already short of, and the
  card's floor contribution to the meter economy (floors per combat fell
  7.9 -> 0.3 when the automatic was deleted; what remains is only what cards
  print).
- **Watch:** at common/uncommon a per-event engine is *more* dangerous, not
  less — multiple copies stack literally. A per-turn cap becomes mandatory
  rather than optional.

### Option C — keep both halves, but price the engine on magnitude and cap it

Keep the shape and change the rate: Block proportional to how far the meter
moved (per N points, not per event), and/or a hard **cap per turn**. This is
the option under which the decay question could genuinely return — a
magnitude-priced decay payout is a real number, though it still lands in the
Block that the turn-start flush clears, so it would need the turn-order ruling
to mean anything at all.

- **Gives up:** simplicity of the printed text, and the "flat per change" edge
  that made the current version cheap to reason about and cheap to pin.
- **Watch:** magnitude pricing re-couples the card to `FANFARE_DECAY` and to
  cap size, which are constants nobody wants this card voting on; and every
  number it produces is un-re-measurable until the DRAFTER 13 re-baseline
  lands.

---

## 5. Open questions for the pen

1. **Which archetype is this card for?** It is tagged `[fanfare, generic]`.
   Under the STOP, does the fanfare tag still buy it anything?
2. **Should the rework wait on the Furina playtest?** R87 (1) deferred the
   strength lever, the dead-archetype question and the salon leak behind one
   playtest whose pre-registered question is *is the pilot better at Salon, or
   does everything feed Salon by construction*. If the answer is "by
   construction", this card's archetype may not survive the answer, and a
   rework taken first is a rework taken twice.
3. **Does the card keep its name?** "Unheard Confession" was written for a
   heal-and-Encore skill two reworks ago. Register is `archon` and R29d's
   naming/lore eyes-on pass is still OWED.
4. **`fanfare_delta_block` has exactly one printer — this card.** (One sheet
   row, one engine hook at `tier0/engine/resources.py:67`, plus
   `tier0/tests/test_a7_port.py` and the C# mirror.) So Options A and C-minus
   do not just change a card, they retire or re-aim an engine op and its
   parity vectors. Do that deliberately, on the Curtain Call precedent —
   delete the hook rather than leave it dormant, because a dormant hook is an
   invitation.
