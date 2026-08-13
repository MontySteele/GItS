# Workshop packet — a bounded per-turn read budget for Kokomi's Charge bank

**Item:** `X9`, the Charge bank. **Register row:** `BACKLOG` `EB-78`.
**Authority:** none. This packet takes no position, names no number, and
recommends nothing. It exists so the workshop opens with the mechanism already
taken apart, which is what the standing note asked for: *"probably too strong
as-is and needs to be parsed carefully."*

**The ruling this packet serves (R163, 2026-08-10):** workshop a bounded
per-turn read budget for the bank. **State no number — the workshop sets the
shape, [USER] prices it.** In scope: the Ceremonial Garment, the Bake-Kurage
pulse, and the two places the pilot puts a value on a bank read. The bank
itself stays uncapped and never spent; that is standing law and is not
reopened here.

Everything below is either an observed fact about the code and the sheet, or a
question. Where a question has options, the options are laid out with what each
one closes off. No option is preferred, and "leave it alone" is on the list
because it is a real answer.

---

## 1. What Charge is, in plain words

Charge is Kokomi's meter. Three things are true about it at once, and the third
is what makes the first two interesting:

- **It only ever goes up.** Nothing decays it, nothing spends it. The law says
  so on purpose — it is written into her sheet header, and it is enforced on
  both sides of the build (the sim has no "spend charge" verb at all, and the
  mod's Charge resource implements "spend" as a documented no-op that returns
  success without subtracting). Every scaling number on her sheet was measured
  against a bank that only grows.
- **It has no ceiling.** It is registered as an unbounded meter alongside her
  Burst and the exhaust pile.
- **Several different things read it, as often as they like.** A read takes the
  current size of the bank, converts it into damage (or, once, into a yes/no),
  and leaves the bank exactly where it was. Reading is free and repeatable.

So the bank is a number that climbs all fight and can be cashed as many times
per turn as the player has ways to cash it. Nothing in the kit currently limits
how many times per turn that happens. That absence is the subject of the
workshop.

---

## 2. What fills the bank

Worth stating because a budget on reads does nothing about accrual, and someone
in the room will ask.

- **The universal funnel.** Exhausting a card mints Charge. This lives on the
  relic, as engine machinery, and deliberately never as card text.
- **Printed Charge lines.** A set of her cards grant Charge outright as a
  bonus on top of the funnel. They span the rarities.
- **Her defensive power.** Her prevention ward pays for each proc with a random
  Exhaust, which routes through the funnel — so being attacked accrues Charge
  without her taking any action at all.

Two consequences of that last one are already on the record from the red-team
pass and both are facts, not claims: a long fight where she does nothing
converts into a large bank, and there is no per-turn ceiling on accrual
anywhere. A read budget would not touch either.

---

## 3. What reads the bank today

This is the "parse carefully" part. There are four kinds of reader and they
behave very differently.

### 3.1 The Garment (in scope)

Her Burst puts her into a state for a few turns. While it holds, **every attack
card she plays reads the bank** and adds a share of it to that attack's damage,
per target. The state's stack count is turns remaining, not magnitude, so
re-entering the state extends the window rather than doubling the read.

Frequency: **once per attack play, per target, unbounded within the turn**. A
turn with many cheap attacks is a turn with many reads.

Both engines implement it in the same phase: sim
`tier0/engine/effects.py:2546-2549` (`flat_attack_bonus`) with the read counter
ticked at the real resolution site, `effects.py:2461-2466`; mod
`klee-mod/KleeCode/Powers/KuragePowers.cs:305-337`
(`CeremonialGarmentPower.ModifyDamageAdditive`, plus the public `ChargeBonus`
that the hover tip reads so preview and effect cannot disagree).

### 3.2 The Kurage pulse (in scope)

The fielded jellyfish pulses at the end of the turn. The pulse is a small flat
amount **plus the whole bank multiplied by a rate**, and one drafted card
raises that rate — permanently, and it stacks with itself. The sim comment at
the site says outright that this multiplies an uncapped, never-spent bank and
is therefore the steepest term the sheet can offer.

Frequency: **once per turn while the summon stands**. That is already a natural
bound. Whether a budget should apply to something that is already once-per-turn
is one of the questions in §5.

Sites: sim `tier0/engine/effects.py:2795-2820`; mod
`klee-mod/KleeCode/Powers/KuragePowers.cs:28-71`. The pulse already emits its
size, the bank that produced it, and the bought rate, so the shape of this term
is observable without new instrumentation.

### 3.3 Printed card readers (adjacent — see the boundary question in §6)

Two cards print a proportional read of the bank in their own text: an uncommon
single-target attack, and a rare that reads the bank to every enemy and carries
every rate limit the sheet's own grammar demands (rare, self-exhaust, high
cost). A third card reads the bank as a **threshold** — a flat printed bonus
once the bank clears a bar, which the law explicitly classifies as *not* a
proportional read and therefore not part of the multiplicative-read risk.

These are named here because of one measured fact, not to widen the scope: **an
attack that prints its own bank read, played while the Garment is up, reads the
bank twice** — once through its printed formula and once through the Garment
rider — and nothing dedupes the two paths. The read arithmetic is at
`tier0/engine/effects.py:604-605` (printed formula) and `:619` (the Garment's
contribution, via `current_attack_bonus`). The docket's one-line statement of
the mechanism says exactly this: *the pulse converts the whole bank every turn,
and the bank is read twice.*

Whether that double read is a defect to dedupe or a shape to budget is a
question in §5, not a finding this packet resolves.

### 3.4 The two pilot valuation sites (in scope)

These are not game effects. They are the sim pilot's estimates of what a card
is worth, and both of them **read the live bank at decision time**:

- `tier0/pilot/policy.py:241-254` — when the pilot considers fielding the
  jellyfish, it prices the coming pulses off the bank as it stands right now.
  The comment records that this understates a late-fight summon deliberately,
  because the pilot cannot see its own future accrual.
- `tier0/pilot/policy.py:592-600` — when the pilot considers entering the
  Garment state, it prices the state at its remaining turns times the current
  bank read.

A third site is worth naming as a **contrast, not a target**: the drafter
(`tier05/draft.py`) deliberately does *not* read the bank when pricing either
the summon or a Charge-granting card, on the stated grounds that the bank is
invisible at offer time. So the offer layer already behaves as if the bank does
not exist, and only the in-combat pilot looks at it.

The relevance to a read budget is direct and unavoidable: **if the game starts
limiting how many reads a turn contains, an estimator that prices every read as
if it will land is valuing something the player will not get.** Any shape
chosen in §5 lands a matching question here, and §7 records what that costs.

---

## 4. What is already fenced, and stays fenced

Naming these so the workshop does not spend its time relitigating them.

- **Charge is never spent, and the bank has no cap.** Standing law. Not
  reopened by R163 and not reopened here.
- **The pulse rate, the Burst meter size, and the ward magnitude** carry their
  own standing flags in the Kokomi playtest protocol. They are table questions
  with their own venue; this is a kit question. They will want to be read
  together eventually, which is a reason to keep them separate until someone
  reads them.
- **Thresholds cannot be lowered.** A bar, once printed, may not drift
  downward; that is resource-curve law.
- **The upgraded velocity rare's unbounded loop** is a termination-hygiene
  defect, handled on its own row. It is not part of the budget question, and a
  budget would not fix it — that loop mints Charge, it does not read it.
- **Accrual is not on the table under R163.** The ruling names a *read* budget.
  A cap on accrual is a different mechanism with different consequences and is
  not one of the options below.

---

## 5. The shape question, decomposed

A "bounded per-turn read budget" is not one decision. It is at least six, and
they are close to independent — a room can answer them in any order, but it has
to answer all of them before anything can be priced.

### Axis A — what counts as a read

- **Every resolved read of the bank, whatever the source.** Forecloses treating
  the Garment and the pulse as separate systems; makes the double-read case in
  §3.3 automatically part of the budget rather than a separate defect.
- **Only proportional reads, thresholds excluded.** Matches the law's existing
  distinction between a slope and a bar. Forecloses any later argument that a
  threshold should be budgeted, and locks the bar cards outside the mechanism
  permanently.
- **Only the card-play readers; the turn-end pulse sits outside.** Forecloses
  using the budget to touch the steepest term on the sheet, and makes the
  budget a hand-tempo mechanism rather than a bank mechanism.

### Axis B — where the budget lives

- **One shared allowance across all readers.** The player chooses which reads
  to spend it on; the Garment and the pulse compete. Forecloses tuning the two
  independently and creates an ordering decision inside every turn.
- **One allowance per source.** Each reader carries its own. Forecloses a
  single knob and multiplies the surface [USER] has to price, but keeps the
  jellyfish's behaviour independent of what her hand did.
- **One allowance per card.** The finest grain. Forecloses using the budget to
  bound a turn at all, since more cards means more allowance.

### Axis C — what happens when the allowance is gone

- **Later reads see a frozen bank** — the bank as it stood at the turn's first
  read, or at the moment the allowance ran out. The reads still happen and
  still pay; they just stop tracking growth within the turn.
- **Later reads pay the printed base only** — the bank contributes nothing past
  the boundary. A sharper edge, and easier to explain on a card.
- **Later reads pay a reduced share.** Softer, and introduces a second quantity
  to price on top of the budget itself.
- **Later reads are refused** — the card cannot be played. Forecloses a clean
  presentation story and creates a dead-card state mid-turn; named for
  completeness because a room should reject it explicitly rather than never
  consider it.

Each of these forecloses a different thing about how the turn *feels*: the
first keeps the turn smooth and makes the limit nearly invisible; the second
makes the limit the most legible thing in the turn; the third makes it a slope
nobody can read off the screen.

### Axis D — when the allowance refreshes

- **At the start of her turn.**
- **At the end of her turn**, which decides whether the turn-end pulse draws
  from the turn that is closing or the one about to open.
- **Once per fight**, which is not a per-turn budget at all and is named only
  so the room can say no to it on the record.

Whichever is chosen, it settles a second question by implication: whether the
pulse — which fires at end of turn — is inside or outside the window that just
closed.

### Axis E — how wide the rule reaches

- **Kokomi's kit only.** Forecloses reuse and leaves the repo with a
  one-character mechanism.
- **Any unbounded meter that is read proportionally.** Her Charge is not the
  only bank in the roster that is read and never spent; the other characters'
  meters have readers of the same shape. Choosing this forecloses ever tuning
  Charge's budget without moving theirs, and turns a kit workshop into a
  cross-character rule.

### Axis F — whether the double read in §3.3 is inside or outside

- **Inside the budget:** an attack that reads twice spends twice, and the
  stacking question answers itself.
- **Outside, as a dedupe defect:** the two paths are collapsed to one on their
  own row, and the budget is designed against a world where one card play is
  one read.
- **Neither — the double read is intended texture.** Legitimate, and the only
  one of the three that requires a positive statement rather than a fix.

The three are mutually exclusive and the choice changes what a budget of any
given size means, which is why it has to be settled before anything is priced.

### Axis G — the null option

**No budget.** The workshop can conclude that the bank's growth is bounded well
enough by the things that already bound it — Charge costs cards, the widest
reader is rare and self-exhausting, the pulse is once per turn — and that what
looks steep is the intended shape of a scaling character. What this forecloses
is nothing structural; it returns `X9` to the watch register with a named
trigger, and the standing playtest flags on the rate and the meter carry the
question instead. It is on this list because a packet that omits "leave it
alone" is arguing.

---

## 6. Boundary question the row does not settle

R163 names the Garment, the Kurage pulse, and the two pilot sites. It does not
name the printed card readers of §3.3. Those cards read the same bank, in the
same proportional way, and one of them is the reason the double read exists —
so a room could reasonably read the scope either way.

This is asked, not answered: **does the budget apply to the printed card
readers, or only to the two kit sources the row names?** If only the kit
sources, then a hand of printed readers is unaffected by the budget entirely,
and that should be a stated outcome rather than a side effect of how the scope
line was written.

---

## 7. What follows from any shape at all

These are costs the room should know about before it picks, and they apply to
every option in §5 except the null one.

- **Two engines, one behaviour.** Charge lives in both the sim and the mod, and
  the constants are compared by value by the parity lint. A budget is a new
  quantity plus a per-turn counter in both engines, and the counter must reset
  at the same moment in each. The Garment and the pulse are already mirrored
  pairs, so there is a pattern to follow, not a new one to invent.
- **The pilot moves, and moving the pilot moves numbers.** Teaching the
  estimator about the budget is a pilot-policy change, which lands under a
  policy version bump — and a policy bump moves every one of her run-level
  numbers, so nothing measured before it is comparable to anything after it
  without a label. Leaving the pilot ignorant of the budget is also an option,
  and its cost is that the pilot systematically over-values her two most
  expensive engine pieces.
- **The exploit pin needs rewording, whatever lands.** The regression pin for
  this family is named for the bank *being spent*, and asserts the bank is not
  converted whole. Under R163 the bank explicitly stays unspent, so the pin's
  name and its assertion no longer describe the thing the workshop is deciding.
  Whoever lands a budget will have to restate that pin against the budget's own
  behaviour; whoever lands nothing should still consider restating it, because
  as written it will read as a licence to cap the bank.
- **Presentation is not optional.** The repo has already paid once for a
  preview that computed separately from the effect. A budget that is invisible
  on screen is a budget the player discovers by being surprised, and the
  Garment's hover tip currently promises arithmetic that a budget would change.
- **Telemetry mostly exists.** The pulse already reports its size, its bank and
  its bought rate; the Garment's read site already ticks a counter. What is
  *not* recorded anywhere today is **how many reads a turn actually contains**,
  which is the exact quantity a budget would bound. Producing that distribution
  is a measurement, it belongs under the measurement law, and it is not part of
  this packet.

---

## 8. What the workshop still does not have

Stated so nobody mistakes this packet for a complete input.

- **No live observation.** Every mechanism above is read from the sim, the mod
  source and the sheet. The Kokomi playtest has not run, and no live smoke was
  taken for this packet.
- **No distribution of reads per turn.** See the last bullet of §7. Nobody
  currently knows what the typical turn looks like, only what the extreme turns
  can do.
- **No opinion on whether the bank is too strong.** The note that opened `X9`
  says *probably*. Nothing in this packet upgrades that word.
