Status: OPEN (three picks for [USER]; paper only, no build, no row)

# Dendro, and the elemental reaction sweep: what the table is, what the seats saw, and what to do about it

Written 2026-09-05, overnight, at [USER]'s request ("integrating dendro now
or later, and whether we should do a full elemental reaction design sweep;
it began as a placeholder system and then got ignored"). Paper only. Every
claim below is checkable against the file it names.

## 1. What the table is today

Four elements leave an **aura** on an enemy (Pyro, Hydro, Electro, Cryo);
two only **trigger** (Anemo, Geo). One aura per enemy, two player turns,
refreshed by a same-element hit (`LAW.md` §Combat, `tier0/engine/reactions.py`).
Eight reactions, with their numbers from `tier0/constants.py`:

| pair | reaction | what it does | the decision it asks |
|---|---|---|---|
| Pyro + Hydro | Vaporize | that hit ×1.5, aura consumed | which hit carries it |
| Pyro + Cryo | Melt | that hit ×1.75, aura consumed | which hit carries it |
| Pyro + Electro | Overload | 6 to ALL through Block, 1 Weak | none: a number |
| Electro + Cryo | Superconduct | 2 Vulnerable | none: a number |
| Hydro + Electro | Electro-Charged | 4 damage a turn for 2 turns | none: a number |
| Hydro + Cryo | Frozen | next action halved, Shatter; bosses take 2 Vulnerable | which enemy to freeze |
| Anemo on any | Swirl | the aura spreads to every enemy | which aura to spread, and when |
| Geo on any | Crystallize | 4 Block | none: a number |

Two things the table settles by law and should keep: no character card
applies an off-element aura (companions and a co-op partner are the only
sources), and no reaction produces a persistent or compounding multiplier
(the iron rule). Both are in `LAW.md` and both have held every kit to the
same discipline.

## 2. What the seats saw, sixteen rounds in

Reactions are named in most seat records (Vaporize in 44 record files,
Swirl 40, Melt 37, Frozen 34, Electro-Charged 33, Overload 31,
Superconduct 19, Crystallize 6), so the machinery runs and the seats meet
it. What they say about it splits cleanly:

- **The amplifiers are the best thing the reaction layer does.** Klee
  round 16: "which of two hits carries Melt's 1.75x" was called the
  puzzle four rounds running, and the inline reaction preview "did the
  whole teaching job that the four-sentence keyword box could not". Melt
  and Vaporize ask a real question because the aura is consumed by the
  first hit, so ordering matters.
- **The transformative reactions are numbers that arrive.** Overload,
  Superconduct, Electro-Charged and Crystallize were never named as a
  decision in any record; they were found by HP arithmetic (Superconduct's
  order was a defect, `EB-472`; a Mine into Cryo dealt 12 where 7 was
  printed, `EB-450`). Crystallize is the one reaction Geo companions make,
  and 4 flat Block is the least interesting outcome on the table.
- **A mono-element deck cannot read the table.** The glossary fills about
  40% of every page and ends "NO REACTION IS REACHABLE HERE" on a
  mono-Pyro run (`EB-428`, widened twice); the page never names a reaction
  when it fires (`EB-410`); Kokomi round 10 read the nine-line gloss "five
  or six times looking for the thing they were meant to do with it". The
  display debt is the first thing in the way of any sweep: a rule the seats
  cannot see cannot be tested.
- **Access is the companion slot.** Off-element comes only from companions.
  Their sheets carry every element (Mondstadt 17: Hydro 4, Pyro 4, Anemo 4,
  Electro 2, Cryo 2, Geo 1; Inazuma 15: Electro 6, Geo 4, Anemo 3, Pyro 2;
  Fontaine 19: Cryo 6, Pyro 4, Hydro 4, Anemo 3, Geo 1, Electro 1), so a
  Pyro Klee with Mondstadt companions reaches Vaporize and Melt, and the
  two Hydro characters reach Vaporize through a Pyro companion. That is the
  acquisition question GPT's roadmap note raised, and it is measurable from
  the records before any rule moves.

## 3. Dendro: what it would cost, and why later

Dendro's reactions are the most decision-shaped in the source game, which
is exactly why they tempt: **Bloom** (Dendro on Hydro) leaves a **Dendro
Core** on the field, a thing that sits there and explodes when Pyro
(Burgeon, to all) or Electro (Hyperbloom, aimed) touches it; **Burning**
(Dendro on Pyro) is a self-sustaining damage-over-time; **Quicken** (Dendro
on Electro) sets a state in which Electro hits (Aggravate) and Dendro hits
(Spread) deal a flat bonus for its duration. Anemo and Geo do not react
with Dendro. A Core is Klee's Bomb as a shared-layer object anyone can
plant and anyone can pop, and Quicken is Superconduct's shape (a two-turn
state that changes what hits do) with a decision attached (which element
pops it).

Three facts decide the timing:

1. **There is no Dendro source in the game.** No character and no companion
   in the three nation sheets is Dendro. Under the law that off-element
   comes only from companions, Dendro needs a Sumeru companion sheet (or a
   Sumeru character) before a single reaction could fire. The cost of Dendro
   is a nation, not a table row. That is also the honest reason it is
   later: the three character overhauls are mid-Prototype and a fourth
   nation's companion workshop is the same kind of work as the Mondstadt
   and Inazuma ones that are still landing.
2. **Quicken does not break the iron rule as long as it is flat and
   timed.** Superconduct already applies a two-turn debuff; Aggravate as
   "+N damage on Electro hits while the enemy is Quickened" is that shape,
   not a multiplier. No LAW amendment is needed to write it; a multiplier
   version would need one and should not be written.
3. **The Core is a new object class.** The engine has enemy-side charges
   (Bombs), a player-side pet (the Bake-Kurage) and a player-side stage
   (the Salon). A Core would be the first neutral field object. That is a
   build the size of Mines, and it wants the display work of `EB-428` and
   `EB-410` done first, or the seats will find Cores by HP arithmetic too.

**Recommendation: Dendro later, with Sumeru, and with the Core as its first
mechanic.** Not never: Bloom is the single most Slay-the-Spire-shaped
reaction in the source game, and a fourth nation is on the roadmap anyway.

## 4. The sweep: what it should be, and what it should not

Not a table rewrite before evidence. The new Prototype loop
(`operations/stage-gate.md`, *The loop inside Prototype*) applies to the
shared layer as much as to a kit: one hypothesis per change, tested by an
assembled deck and a natural route, the smallest intervention. The sweep in
that shape:

1. **The reaction brief.** The layer never had the document every character
   has: the promise, the rules in seven sentences, what each reaction asks
   the player, what fight one of each character teaches about it, the
   failure modes ("a number that arrives", "a glossary nobody can act
   on"). Two pages, written against the kit checklist, GPT-audited. Mine.
2. **The census.** A script over the seat records: which reaction fired,
   what triggered it (a kit card, a companion, a Mine, a Plan, a
   performance), on what turn, and whether the record names it as a
   decision. This turns the counts in §2 into a table and answers the
   acquisition question (how many turns from a reaction card in hand to an
   applier drafted) from data already on disk. Opus, one row.
3. **The display debt first.** `EB-428` and `EB-410` are prerequisites: a
   glossary sized to the elements in the deck, and a fired reaction named on
   the page. Nothing in the table can be graded until the seats can see it.
4. **Then the hypotheses, one per round, as rule changes under a flag.**
   The three the evidence already points at: (a) Crystallize asks nothing;
   a version that reads the aura it crystallised (Block, plus the aura's own
   effect once) would give Geo companions a reason to exist beyond a
   number. (b) Overload's 6 through Block is flat; splashing the *aura's*
   damage instead would make it scale with the hit that caused it and give
   Klee's Bomb-into-Electro a reason to be large. (c) Superconduct
   duplicates Exposed Flank; a Cryo-shaped outcome (the next hit on the
   target is Shatter-sized) would make it Cryo's, not a generic debuff.
   Each is a flag, an assembled-deck run and a natural run, and the
   smallest intervention wins, which may be "leave it".

What the sweep should not do: touch the amplifiers (they work and the seats
say so), the aura duration, the one-aura rule, or either law.

## 5. Picks

1. **Dendro.** (1) *Later, with a Sumeru companion sheet, the Core first,
   after the sweep's display debt is paid* [default]. (2) Now, as a fifth
   aura element with a Dendro-tagged stand-in on one existing companion
   per nation; the Core built beside Mines. (3) Never; four auras and two
   triggers is the table.
2. **The sweep's shape.** (1) *The brief, the census and the two display
   rows now; rule changes only as round hypotheses under a flag, one per
   round, from round 18* [default]. (2) A full table redesign on paper
   before any more rounds. (3) Leave the table until the three kits reach
   Balance.
3. **Quicken and the iron rule.** (1) *No amendment: a flat, timed bonus is
   Superconduct's shape and is legal as written* [default, a reading of
   LAW, not a change]. (2) Amend the iron rule to name Dendro's additive
   bonus explicitly. (3) Refuse Quicken outright when Dendro comes.
