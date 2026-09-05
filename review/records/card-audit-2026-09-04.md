Status: RECORD

# The card audit of 2026-09-04: thirteen new rows read by GPT before a tester sees them

Written 2026-09-04, ruled R253. [USER], from a spare minute while away: Tidal
Rhythm "sounds way too good ... that's basically one free energy, which is
equivalent to something like Echo Form"; ask for an adversarial GPT audit of
all of the new cards through the Codex bridge, and only approve what the
reviewer agrees to. The standard behind it, in [USER]'s words: "I just don't
want us to end up gaming the metric of 'can an agent beat the game' by
printing overly strong cards. We know canonical characters still die in the
hands of the same agents, so a successful design phase should not end with
'all agents always win.'" All thirteen rows were written by Claude (Fable), so
the reviewer is GPT through `understudy.seat review` (R217 C, independence by
model family). The reviewer names a clause and a line; it supplies no number
and no remedy, and none was used.

## 1. The verdicts

| # | Row | Kit | First read | Final | Clause named |
|---|---|---|---|---|---|
| 1 | Dodoco Cover | Klee | REQUIRES_MODIFICATION | **FOLLOWS** (pass 3) | C6, against Defend; withdrawn once C6 was corrected (§3) |
| 2 | Careful Now | Klee | FOLLOWS | **FOLLOWS** | C4: Block only after the player chose to cook and keep a Bomb |
| 3 | Fire Safety | Klee | REQUIRES_MODIFICATION | **WITHDRAWN** | C4: 3 Block for 0 energy is on-demand defence before the rider |
| 4 | Safety Lesson | Klee | REQUIRES_MODIFICATION | **WITHDRAWN** | C4: pays on a Mine going off, which is no decision just made |
| 5 | Barbara — Front Row Seat | Klee | REQUIRES_MODIFICATION | **FOLLOWS** (pass 3) | C6, against Defend; withdrawn once C6 was corrected (§3) |
| 6 | Held Tide | Kokomi | REQUIRES_MODIFICATION | **WITHDRAWN** | C1: Retain waits out the dead turns and guarantees the 12 line |
| 7 | Tidal Rhythm | Kokomi | REQUIRES_MODIFICATION | **WITHDRAWN** | C2: 1 repeatable Energy a turn past the card's own cost, no drawback |
| 8 | Tide Chart | Kokomi | FOLLOWS | **FOLLOWS** | C2: draws 0 with nothing written; each draw cost a deferred, paid card |
| 9 | Ripple | Kokomi | FOLLOWS | **FOLLOWS** | C2: the Energy costs the 2 Block now and a turn's wait |
| 10 | Florid Cadenza (arm copy) | Furina | FOLLOWS | **FOLLOWS** | C8: 6 sits in the observed 0 to 15 where 12 sat in 20 to 30 |
| 11 | Dramatic Entrance (arm copy) | Furina | FOLLOWS | **FOLLOWS** | C8, same mapping |
| 12 | Universal Revelry (arm copy) | Furina | FOLLOWS | **FOLLOWS** | C8, 15 of 30 to 8 of 15 |
| 13 | Flood of Emotion (arm copy) | Furina | FOLLOWS | **FOLLOWS** | C8, 20 of 30 to 10 of 15 |

Nine rows go to the testers. Four are withdrawn from the sheet in the same
change: the two Kokomi rows before any build, the two Klee rows after one
read (Klee round 10 ran with them offered; those six records stand as
records of a shelf that no longer exists in that shape, and the round's
packet says so). A withdrawn row is not a queued design question: Fire
Safety was already dead in a mono-Pyro deck on the round-10 read, Safety
Lesson's Mine line is the reviewer's reading of the brief's §6, Held Tide's
Retain is the whole card, and Tidal Rhythm was [USER]'s own call before the
reviewer confirmed it. If the pool wants any of them back it comes back as
a new row through the same door.

## 2. How the reading was run, including the misfire

Four calls through the bridge, meter at 5h 0% / week 14% before the first.

1. **The pair role refused** (`--role pair`): its protocol reads a completed
   blind-QA round and it escalated all thirteen as out of scope. Correct
   behaviour, wrong role; the reply is in §4 for the record.
2. **The doctrine role read all thirteen** against a charter of eight
   clauses (C1 the owner's standard, C2 LAW D3, C3 LAW D2, C4 the Klee
   brief's §6, C5 nothing fires by itself, C6 not strictly better, C7 the
   Kokomi deck-size law, C8 the Furina arm's Fanfare economy). Seven
   FOLLOWS, six REQUIRES_MODIFICATION.
3. **Two of the six were the author's clause, not the row.** C6 as written
   compared a Common to Defend, and every class's Common block card beats
   Defend by design (Iron Wave: 5 Block and 5 damage for 1). A second pass
   corrected C6 to non-basic references; both came back FOLLOWS. That
   pass, though, quoted two pool rows from the author's memory, and one of
   them ("Pounce") does not exist while Melody Loop's text was wrong, so
   its verdict was discarded unread of its reasoning.
4. **A third pass quoted the sheet.** Fish-Flavored Bait (Common, 1: deal
   4, Bomb 4) is Dodoco Cover's twin at the same rarity and cost; Diona's
   Shaken, Not Purred (Common, 1: 6 Block, Cryo twice, 5 more if a Bomb goes
   off) is Front Row Seat's, and Front Row Seat replaces Barbara's own 6
   Block plus Hydro. Both FOLLOWS. This is the verdict the table carries.

The lesson goes to the seat's operations page, not here: a charter prompt
quotes the sheet or it quotes nothing, and a reference row is read from the
YAML before it is typed.

## 3. What R253 rules

- Kokomi round 9 pick 1 (the tempo shelf) is taken at its default AS
  AUDITED: Tide Chart and Ripple are built; Held Tide and Tidal Rhythm are
  not.
- Furina round 2 pick 1 (the riders re-priced arm-only at 6, 6, 8 and 10)
  and pick 2 (Encore absorption kept and printed) are taken at their
  defaults, as [USER] said ("the other two picks sound fine").
- Klee round 9's shelf (R252) is narrowed by the same audit to Dodoco
  Cover, Careful Now and Barbara — Front Row Seat.
- The audit is the door for new rows from here: a Claude-written row is
  read by GPT through the doctrine role before a tester sees it, and a row
  the reviewer rules against is withdrawn, not argued. A misquoted charter
  is the author's defect and is re-read, as §2 shows, never re-worded to
  get the answer.

## 4. The instrument and the replies, verbatim

### 4.1 Call 1: the pair role (refused)


```
The supplied material is not the completed blind-QA record described by the seat protocol. It contains only prototype rows and engine context—not the shipped halves, graders’ verbatim forms, falsifier verdicts, or live-game replays. A fresh card-text audit would cross the author/grader boundary. Therefore every arm must escalate.

1. Dodoco Cover — KEEP or NOT AS WRITTEN: unresolved. No admissible breaking line or comparison is present. **ESCALATE.**

2. Careful Now — KEEP or NOT AS WRITTEN: unresolved. No admissible breaking line or comparison is present. **ESCALATE.**

3. Fire Safety — KEEP or NOT AS WRITTEN: unresolved. No admissible breaking line or comparison is present. **ESCALATE.**

4. Safety Lesson — KEEP or NOT AS WRITTEN: unresolved. No admissible breaking line or comparison is present. **ESCALATE.**

5. Barbara — Front Row Seat — KEEP or NOT AS WRITTEN: unresolved. No admissible breaking line or comparison is present. **ESCALATE.**

6. Held Tide — KEEP or NOT AS WRITTEN: unresolved. No admissible breaking line or comparison is present. **ESCALATE.**

7. Tidal Rhythm — KEEP or NOT AS WRITTEN: unresolved. The owner’s stated concern is not a grader finding, falsifier verdict, or replay result, so it cannot establish the ruling. **ESCALATE.**

8. Tide Chart — KEEP or NOT AS WRITTEN: unresolved. No admissible breaking line or comparison is present. **ESCALATE.**

9. Ripple — KEEP or NOT AS WRITTEN: unresolved. No admissible breaking line or comparison is present. **ESCALATE.**

10. Florid Cadenza — KEEP or NOT AS WRITTEN: unresolved. No shipped/prototype comparison or replay evidence is present. **ESCALATE.**

11. Dramatic Entrance — KEEP or NOT AS WRITTEN: unresolved. No shipped/prototype comparison or replay evidence is present. **ESCALATE.**

12. Universal Revelry — KEEP or NOT AS WRITTEN: unresolved. No shipped/prototype comparison or replay evidence is present. **ESCALATE.**

13. Flood of Emotion — KEEP or NOT AS WRITTEN: unresolved. No shipped/prototype comparison or replay evidence is present. **ESCALATE.**

14. Three most dangerous — **ESCALATE; no evidence-supported ranking can be made.**

15. Three weakest — **ESCALATE; no evidence-supported ranking can be made.**
```

The prompt it refused is the same material as §4.2's, in the pair role's
output shape (KEEP / NOT AS WRITTEN plus two ranked lists); it is not
repeated.

### 4.2 Call 2: the doctrine role, thirteen arms

The prompt:

```
# Doctrine read: thirteen prototype rows against the kit charters

Each numbered card below is ONE ARM. For each arm, in order, give FOLLOWS or
REQUIRES_MODIFICATION and name the clause (C1 to C8) you ruled against, and
quote the line of the card and the arithmetic (energy, Block, damage, turns)
that breaches it, in one sentence. A verdict with no clause named is not a
verdict. Read adversarially: the author is a different model family and the
owner wants the row that should not reach a tester named. Do not soften.

## The charter

- **C1 (owner, 2026-09-04).** "I don't want us to end up gaming the metric
  of 'can an agent beat the game' by printing overly strong cards. Canonical
  characters still die in the hands of the same agents, so a successful
  design phase should not end with 'all agents always win.'" A row that
  removes a losing line the kit is meant to keep, instead of pricing it, is
  out of charter.
- **C2 (LAW D3, binding prices).** A benefit carries a binding price. The
  counterfactual test: there must be a real turn in which the card is worse
  than a plain card of its cost. Repeatable energy or draw at Uncommon or
  below is priced by something past the card's own cost. The owner's own
  reading of one row: "'once per turn, gain 1 Energy' with no drawback is
  one free energy, Echo Form territory for a 1-cost Uncommon Power."
- **C3 (LAW D2, player-controlled leverage).** The card's value is decided
  by a choice the player makes (bank or cash a Bomb; play a Plan now or write
  it; make the stage perform), not by a number that rises while you watch.
- **C4 (Klee brief §6).** "She cannot stall, and she cannot block on demand.
  Her only plain Block is Duck and Cover, 5 for 1. Every other defence she
  has is conditional on the decision she just made." The weakness is
  load-bearing because it is what makes cooking a bet.
- **C5 (Klee brief §3 rule 7; Kokomi brief §2 rule 4).** Nothing fires by
  itself: no automatic free attack, no passive feed; every effect is a card
  the player played and paid for.
- **C6 (not strictly better).** A row may not be a strictly better version
  of a shipped pool row or of a base-game card at the same or lower rarity
  and cost. Base-game reference points you know: Defend (1: 5 Block),
  Flame Barrier (Uncommon, 2: 12 Block), Second Wind, Berserk (Uncommon
  Power, 0: 1 Energy a turn, 2 Vulnerable), Echo Form (Rare, 3), Offering,
  Battle Trance, Adrenaline, Barricade, Calculated Gamble.
- **C7 (Kokomi identity Law 4).** In her pool a Common never increases deck
  size.
- **C8 (Furina reframe §4.1, D2).** Under the arm Fanfare is minted by a
  Salon member performing and by nothing else, 2 per trigger and 5 per
  Evoke, decaying 20% a turn. An arm-only copy of a shipped rider changes
  the threshold only, and the copy's threshold has to sit in the observed
  range (0 to 15 across three rounds) the way the shipped threshold sat in
  the shipped economy's range (20 to 30 reached).

## The engines

**Klee.** Her Attacks apply Pyro. A **Bomb** is a charge on an enemy that
grows by 4 at the start of each of her turns and goes off only when a card
says **Set off** (every Bomb on that enemy, each as its own Pyro hit; not an
Attack; Block absorbs it). A **Mine** also goes off when its enemy attacks
her. **Spark**: 1 at combat start, +1 per Bomb going off, spent by some cards
instead of energy. Starter: 4 Strike, 4 Defend, Ka-pow! (0, Retain, Set off,
deal 4), Jumpy Dumpty (1, Bomb 8; when it goes off, Mine 3 on all enemies).
Energy 3, HP 62. Pool defence for calibration: Dig In (Uncommon, 0 energy, 2
Spark: 5 Block, 6 more if the enemy intends to attack); Run Away! (Common,
0: 3 Block, 4 more if a Bomb went off this turn); Grounded (Uncommon Power,
1: start of turn, if no Bomb went off last turn, 6 Block and 1 Spark);
Sorry, Jean... (Common, 0: remove one of your Bombs, Block equal to its
size); Big Badda Boom (Uncommon, 2: Set off, deal 12, then deal what the
Bombs dealt); Sparks 'n' Splash (Rare Power, 2: end of turn, Pyro damage to
a random enemy equal to its largest Bomb, Bomb not spent).

**Kokomi.** The **Bake-Kurage** is a pet. A card with a **Plan:** line is
played normally (its now-line) or written onto the Kurage; the Plan happens
at the start of your next turn, before you draw, in the order written, cost
paid either way. Plan damage is the Kurage's hit (enemy Vulnerable counts;
her Weak and Strength do not). Energy 3, HP 80. The 30-row pool has a flat
cost curve (0 to 2), no energy gain, two draw cards (Stolen Chapter: draw 2
/ Plan draw 4; Battle Plan: draw 1 / Plan gain 1 Energy and draw 2) and
nothing that Retains. Sango Isshin (Rare Attack, 2): deal 8; if the Kurage
carried out a Plan this turn, deal a quarter of Max HP to ALL enemies
instead. The Moon Overlooks the Waters (Rare Power, 2): Plans also happen
now. Nereid's Ascension (Rare, 2): for 2 turns carry-outs happen twice.
Seats' dead turns were hands of basics with no Plan card and no way to hold
or hurry one.

**Furina.** Under the arm the shipped Burst meter is gone; Fanfare is minted
only by performance (C8). Shipped riders asked 12, 15 and 20 Fanfare.

## The arms

1. **Dodoco Cover** — Klee, Common Skill, 1. Place a Bomb 4. Gain 5 Block.
   Upgrade: Bomb 6, Block 7.
2. **Careful Now** — Klee, Uncommon Skill, 1, Retain. Gain Block equal to
   your largest Bomb when played, up to 10. Upgrade: up to 13.
3. **Fire Safety** — Klee, Common Skill, 0. Gain 3 Block. If a Bomb triggered
   an Elemental Reaction this turn, gain 6 more. Upgrade: 5 and 8.
4. **Safety Lesson** — Klee, Uncommon Power, 1. Whenever one of your Bombs
   goes off, gain 2 Block. Upgrade: 3. Not on Sparks 'n' Splash.
5. **Barbara — Front Row Seat** — Klee companion card, Common, 1. Gain 5
   Block. Apply Hydro twice. Whenever a Bomb goes off this turn, gain 3
   Block. Upgrade: 7 Block, 4 per Bomb. (Hydro under a Pyro Bomb = Vaporize,
   1.5x on one Bomb of the Set off.)
6. **Held Tide** — Kokomi, Uncommon Attack, 1, Retain. Deal 6. If the Kurage
   carried out a Plan this turn, deal 12 instead. Upgrade: 16.
7. **Tidal Rhythm** — Kokomi, Uncommon Power, 1. Once per turn, when the
   Kurage carries out a Plan, gain 1 Energy. Upgrade: Innate.
8. **Tide Chart** — Kokomi, Common Skill, 0. Draw 1 card for each Plan the
   Kurage holds. Upgrade: draw 1 more.
9. **Ripple** — Kokomi, Common Skill, 0. Gain 2 Block. Plan: gain 1 Energy
   and 4 Block. Upgrade: Plan 7 Block.
10. **Florid Cadenza (arm copy)** — Furina, Uncommon Skill, 0. Draw 1. If at
    least 6 Fanfare (was 12), draw 2 more.
11. **Dramatic Entrance (arm copy)** — Furina, Uncommon Attack, 1. Deal 7.
    If at least 6 Fanfare (was 12), deal 7 to ALL enemies.
12. **Universal Revelry (arm copy)** — Furina, Rare Attack, 2. Deal 9 to ALL
    enemies, plus 1 per 2 Fanfare. If at least 8 Fanfare (was 15), deal 6
    more to ALL.
13. **Flood of Emotion (arm copy)** — Furina, Rare Skill, 1. Deal 14. If at
    least 10 Fanfare (was 20), deal 14 more.

Thirteen verdicts, each with its clause and its breaching line. Under 900
words.
```

The reply:

```
1. REQUIRES_MODIFICATION — C6: “Place a Bomb 4. Gain 5 Block” gives Defend’s 5 Block for the same 1 energy plus Bomb 4.

2. FOLLOWS — C4: “Gain Block equal to your largest Bomb when played, up to 10” costs 1 energy and yields 0–10 Block only after the player chooses to cook and preserve a Bomb.

3. REQUIRES_MODIFICATION — C4: “Gain 3 Block” provides unconditional on-demand defence for 0 energy before the reaction rider’s additional 6 Block.

4. REQUIRES_MODIFICATION — C4: “Whenever one of your Bombs goes off, gain 2 Block” also fires when a Mine automatically detonates on an enemy attack, granting 2 Block without a decision just made.

5. REQUIRES_MODIFICATION — C6: “Gain 5 Block. Apply Hydro twice” matches Defend’s 5 Block for 1 energy while adding two Hydro applications and 3 Block per detonated Bomb.

6. REQUIRES_MODIFICATION — C1: “Retain. Deal 6. If the Kurage carried out a Plan this turn, deal 12 instead” lets a 1-energy card wait through dead sequencing turns and guarantees the 12-damage payoff line.

7. REQUIRES_MODIFICATION — C2: “Once per turn, when the Kurage carries out a Plan, gain 1 Energy” produces 1 repeatable Energy per turn after the Power’s own 1-energy cost, with no further drawback.

8. FOLLOWS — C2: “Draw 1 card for each Plan the Kurage holds” costs 0 but draws 0 with no held Plan, while each additional draw requires the player previously to defer one paid card onto the Kurage.

9. FOLLOWS — C2: “Gain 2 Block. Plan: gain 1 Energy and 4 Block” costs 0, but obtaining the 1 Energy requires foregoing the immediate 2 Block and waiting until the next turn.

10. FOLLOWS — C8: “If at least 6 Fanfare (was 12), draw 2 more” maps 12/20 to 6/15, placing the threshold at 6 within the observed 0–15 range.

11. FOLLOWS — C8: “If at least 6 Fanfare (was 12), deal 7 to ALL enemies” maps 12/20 to 6/15, placing the threshold at 6 within the observed 0–15 range.

12. FOLLOWS — C8: “If at least 8 Fanfare (was 15), deal 6 more to ALL” maps 15/30 to approximately 8/15, placing the threshold at 8 within the observed 0–15 range.

13. FOLLOWS — C8: “If at least 10 Fanfare (was 20), deal 14 more” maps 20/30 to 10/15, placing the threshold at 10 within the observed 0–15 range.
```

### 4.3 Call 3: C6 corrected (discarded, see §2)

The prompt:

```
# Doctrine read, second pass: two arms against a corrected clause C6

Your first pass (thirteen arms, same engines and charter as before) ruled two
arms REQUIRES_MODIFICATION on clause C6 by comparing them to Defend. The
author mis-stated C6 and that is the author's defect, not yours: Defend is a
BASIC card, and every class's Common block cards exceed it by design (Iron
Wave, Common, 1: 5 Block and 5 damage; Shrug It Off, Common, 1: 8 Block,
draw 1; Leap, Common, 1: 9 Block; Cloak and Dagger, Common, 1: 6 Block, a
Shiv). Nothing else in the charter changes. Read the two arms again.

## Corrected clause

- **C6 (not strictly better).** A row may not be a strictly better version
  of a shipped POOL row (Klee's pool, listed below) or of a base-game
  non-basic card at the same or lower rarity and cost. Defend and Strike
  are basics and are not reference points. Base-game Commons at 1 energy
  for reference: Iron Wave (5 Block, 5 damage), Shrug It Off (8 Block, draw
  1), Leap (9 Block), Cloak and Dagger (6 Block, add a Shiv), Flame Barrier
  is Uncommon 2 (12 Block, 4 damage to attackers).

All other clauses as in the first pass: C1 (the owner's "not all agents
always win"; a row that removes a losing line the kit is meant to keep,
instead of pricing it, is out), C2 (LAW D3, binding prices), C3 (LAW D2,
player-controlled leverage), C4 (Klee brief §6: "she cannot block on
demand; her only plain Block is Duck and Cover, 5 for 1; every other
defence is conditional on the decision she just made"), C5 (nothing fires
by itself).

## The engine, Klee

Her Attacks apply Pyro. A **Bomb** is a charge on an enemy that grows by 4
at the start of each of her turns and goes off only when a card says **Set
off** (every Bomb on that enemy, each its own Pyro hit; not an Attack; Block
absorbs it). A **Mine** also goes off when its enemy attacks her. **Spark**:
1 at combat start, +1 per Bomb going off, spent by some cards instead of
energy. Starter: 4 Strike, 4 Defend, Ka-pow! (0, Retain, Set off, deal 4),
Jumpy Dumpty (1, Bomb 8; when it goes off, Mine 3 on all enemies). Energy 3,
HP 62. Her pool's Block rows: Duck and Cover (Common, 1: 5 Block, the one
plain Block); Dig In (Uncommon, 0 energy, 2 Spark: 5 Block, 6 more if the
enemy intends to attack); Run Away! (Common, 0: 3 Block, 4 more if a Bomb
went off this turn); Grounded (Uncommon Power, 1: start of turn, if no Bomb
went off last turn, 6 Block and 1 Spark); Sorry, Jean... (Common, 0: remove
one of your Bombs, Block equal to its size). Her pool's Bomb placers at 1
energy: Jumpy Dumpty (above); Pounce (Common Attack, 1: deal 5, Bomb 4).
A companion card is drafted from the shared companion pool, not her pool;
Barbara's other companion rows are Hydro skills (Melody Loop, Uncommon, 1:
apply Hydro to all enemies, gain 4 Block).

## The two arms

1. **Dodoco Cover** — Klee, Common Skill, 1. Place a Bomb 4. Gain 5 Block.
   Upgrade: Bomb 6, Block 7.
2. **Barbara — Front Row Seat** — Klee companion card, Common, 1. Gain 5
   Block. Apply Hydro twice. Whenever a Bomb goes off this turn, gain 3
   Block. Upgrade: 7 Block, 4 per Bomb. (Hydro under a Pyro Bomb = Vaporize,
   1.5x on one Bomb of the Set off.)

For each arm: FOLLOWS or REQUIRES_MODIFICATION, the clause named, and the
breaching line with its arithmetic in one sentence. Under 250 words.
```

The reply:

```
1. FOLLOWS — C6  
2. FOLLOWS — C6
```

### 4.4 Call 4: the sheet quoted

The prompt:

```
# Doctrine read, third pass: the same two arms, the pool quoted from the sheet

Your second pass ruled Dodoco Cover and Barbara — Front Row Seat FOLLOWS on
clause C6 after the author corrected C6's reference set. The author then
found that two pool rows in that pass were quoted from memory and are wrong:
"Pounce" does not exist on the sheet, and Melody Loop's text was misstated.
A verdict resting on a false row is discarded. This pass quotes the sheet.
Read the two arms a third time against C6 as corrected, with these rows.
Nothing else in the charter changes.

## Clause C6 (corrected)

A row may not be a strictly better version of a shipped POOL row (below) or
of a base-game non-basic card at the same or lower rarity and cost. Defend
and Strike are basics and are not reference points. Base-game Commons at 1
energy: Iron Wave (5 Block, 5 damage), Shrug It Off (8 Block, draw 1), Leap
(9 Block), Cloak and Dagger (6 Block, add a Shiv).

The other clauses as before: C1 (owner: a row that removes a losing line the
kit is meant to keep, instead of pricing it, is out; "not all agents always
win"), C2 (LAW D3, binding prices), C3 (LAW D2, player-controlled leverage),
C4 (Klee brief §6: she cannot block on demand; every defence past her plain
Block is conditional on the decision she just made), C5 (nothing fires by
itself).

## The engine, Klee

Her Attacks apply Pyro. A **Bomb** is a charge on an enemy that grows by 4
at the start of each of her turns and goes off only when a card says **Set
off** (every Bomb on that enemy, each its own Pyro hit; not an Attack; Block
absorbs it). A **Mine** also goes off when its enemy attacks her. **Spark**:
1 at combat start, +1 per Bomb going off. Starter: 4 Strike, 4 Defend (the
base game's, her only plain Block under this arm), Ka-pow! (0, Retain, Set
off, deal 4), Jumpy Dumpty (1, Bomb 8; when it goes off, Mine 3 on all
enemies). Energy 3, HP 62.

Pool rows quoted from the sheet, all 1 energy:

- Fish-Flavored Bait (Common Attack): Deal 4 damage. Place a Bomb 4.
- Ammo Scavenging (Common Skill): Place a Bomb 4. Draw 1 card for each of
  your Bombs that went off this turn.
- Chain Fuse (Common Skill): Each Bomb on the enemy grows by 6.
- Coven Errand (Common Skill): Place a Bomb 5. If you played a Hexerei card
  this turn, place it on ALL enemies instead.
- Grounded (Uncommon Power): At the start of your turn, if none of your
  Bombs went off last turn, gain 6 Block and 1 Spark.
- Careful Now (Uncommon Skill, Retain): Gain Block equal to your largest
  Bomb, up to 10.
- Dig In (Uncommon Skill, 0 energy, costs 2 Spark): 5 Block; 6 more if the
  enemy intends to attack.
- Run Away! (Common Skill, 0): 3 Block; 4 more if a Bomb went off this turn.

Companion rows (drafted from the companion pool, Klee-only stand-ins), all
Common, 1 energy:

- Barbara — The Show Begins (the row Front Row Seat REPLACES under this
  arm): Gain 6 Block. Apply Hydro.
- Barbara — Melody Loop (Uncommon): Gain 4 Block. For 3 turns, at the start
  of your turn apply Hydro to the enemy.
- Diona — Shaken, Not Purred: Gain 6 Block. Apply Cryo twice. If a Bomb
  goes off this turn, gain 5 Block.

Hydro under a Pyro Bomb = Vaporize, 1.5x on one Bomb of the Set off; Cryo
under it = Melt, 2x on one Bomb.

## The two arms

1. **Dodoco Cover** — Klee, Common Skill, 1. Place a Bomb 4. Gain 5 Block.
   Upgrade: Bomb 6, Block 7.
2. **Barbara — Front Row Seat** — companion Common, 1. Gain 5 Block. Apply
   Hydro twice. Whenever a Bomb goes off this turn, gain 3 Block. Upgrade:
   7 Block, 4 per Bomb.

For each arm: FOLLOWS or REQUIRES_MODIFICATION, the clause named, and the
line with its arithmetic in one sentence, naming the pool row you compared
it to. Under 200 words.
```

The reply:

```
1. FOLLOWS — C6.
2. FOLLOWS — C6.
```

## 5. Addendum, 2026-09-04: a third misquote, and the Klee pool pass

**The calibration list in call 2 (§4.2) misquoted Dig In.** It gave "Uncommon,
0 energy, costs 2 Spark: Gain 5 Block; 6 more if the enemy intends to attack".
The sheet prints Dig In as a Common Skill, 0 energy, 1 Spark: "Gain 8 Block."
The row was on the list for calibration only; no verdict in §1 names it, and
the three reviewed defence rows were ruled on C4 and C6 against their own
lines, Defend, and later the sheet's rows. The verdicts stand. The lesson in
§2 is repeated because the misquote was found after it was written: every
reference row in a charter prompt is pasted from the YAML, and the census
that pastes it is run, not remembered.

**The Klee pool pass, first two rows, same door.** Klee round 10 left the Spark
deadlock as the pool pass's first question (three seats holding Spark-priced
detonators at 0 Spark, others holding 4 to 7 Sparks with nothing to spend
them on). Two rows were written and read by GPT through the doctrine role
before any tester, this time with the pool census pasted from the sheet:

| Row | Verdict | Clause |
|---|---|---|
| Explosive Spark (Uncommon Attack, 0 energy, X Sparks: 3 damage per Spark spent) | **REQUIRES_MODIFICATION**, withdrawn | C3: its value follows the banked Sparks, not a Bomb decision |
| Countdown (Common Skill, 1 energy: Set off. Draw 1 card.) | **FOLLOWS** | C1 to C6: 1 energy to Set off and draw, beside Sizzle's 1-energy Set off and 6 damage; the losing line stays |

Countdown is built; the sink is not, and the Spark surplus the seats reported
is left for the next round to say again with Countdown in the pool. The
prompt and reply:

```
# Doctrine read: two Klee pool rows against the kit charter

Each numbered card below is ONE ARM. For each, FOLLOWS or
REQUIRES_MODIFICATION, the clause (C1 to C6) you ruled against, and the line
of the card with its arithmetic in one sentence, naming the pool row you
compared it to. Read adversarially; the author is a different model family
and the owner wants the row that should not reach a tester named.

## The charter

- **C1 (owner).** "A successful design phase should not end with 'all agents
  always win.'" A row that removes a losing line the kit is meant to keep,
  instead of pricing it, is out.
- **C2 (LAW D3).** A benefit carries a binding price; there is a real turn on
  which the card is worse than a plain card of its cost.
- **C3 (LAW D2).** The card's value turns on a choice the player makes (bank
  or cash a Bomb), not on a number rising while you watch.
- **C4 (Klee brief §6).** She cannot block on demand; every defence past the
  base game's Defend is conditional on the decision just made.
- **C5 (Klee brief §3 rule 7).** Nothing fires by itself: no automatic free
  attack, no "at N Sparks".
- **C6 (not strictly better).** Not a strictly better version of a shipped
  pool row below, or of a base-game non-basic card at the same or lower
  rarity and cost (Whirlwind is X-cost Uncommon: 5 to ALL per energy;
  Skewer X-cost: 7 per energy to one; Sword Boomerang; Cleave).

## The engine, Klee

Her Attacks apply Pyro. A **Bomb** is a charge on an enemy that grows by 4
at the start of each of her turns and goes off only when a card says **Set
off** (every Bomb on that enemy, one at a time, each its own Pyro hit; not
an Attack). A **Mine** also goes off when its enemy attacks her. **Spark**:
she starts each combat with 1, gains 1 per Bomb going off, and cards that
print a Spark price spend Sparks instead of energy; no cap, lost at the end
of combat. Energy 3, HP 62. Starter: 4 Strike, 4 Defend, Ka-pow! (basic, 0
energy, Retain: "Set off. Deal 4 damage."), Jumpy Dumpty (basic, 1: "Place a
Bomb 8. When it goes off, place a Mine 3 on ALL enemies.").

The round-10 finding these rows answer: three seats sat in a deadlock,
holding Spark-priced detonators at 0 Spark with a fat Bomb on the enemy and
no energy-priced detonator drawn (Ka-pow! is one card in ten); other seats
ended fights holding 4 to 7 Sparks with nothing to spend them on.

Pool rows quoted from the sheet (rarity, energy cost, Spark cost if any):

- Fwoosh! (Common Attack, 0 energy, 1 Spark): Set off. Deal 6 damage.
- Tinder Toss (Common Attack, 0 energy, 1 Spark): Set off and deal 4 damage
  to a random enemy twice.
- Quick Fuse (Common Skill, 0 energy, 1 Spark): Each Bomb on the enemy grows
  by 3. Set off.
- Bang Bang! (Uncommon Attack, 0 energy, 2 Spark): Set off. Deal 8 damage.
  Place a Bomb 4.
- Sugar Rush (Rare Skill, 0 energy, 2 Spark): Gain 2 Energy. Draw 1 card.
  Exhaust.
- Dig In (Common Skill, 0 energy, 1 Spark): Gain 8 Block.
- Powder Charge (Uncommon Skill, 0 energy, 1 Spark): Place a Bomb 6.
- Sizzle (Common Attack, 1 energy): Set off. Deal 6 damage. If a Bomb
  triggered an Elemental Reaction this turn, deal 6 additional damage.
- Perfect Timing (Uncommon Attack, 1): Set off. Deal 8 damage. If a Bomb
  triggered an Elemental Reaction this turn, play this again.
- Flame Dance (Uncommon Attack, 1): Set off each enemy whose aura is not
  Pyro. Deal 5 damage to ALL enemies.
- Big Badda Boom (Uncommon Attack, 2): Set off. Deal 12 damage. Then deal
  damage equal to what the Bombs dealt.
- Rapid Fire (Uncommon Attack, 2): Deal 3 damage to a random enemy 4 times.
  Set off each enemy hit.
- The Big One (Rare Attack, 3): Set off for quadruple damage.
- Pocket Fireworks (Common Attack, 1): Deal 9 damage.
- Ammo Scavenging (Common Skill, 1): Place a Bomb 4. Draw 1 card for each of
  your Bombs that went off this turn.
- Pop (Common Skill, 0 energy): Place a Bomb 5.
- Catalytic Converter (Uncommon Power, 1): Whenever one of your Bombs
  triggers an Elemental Reaction, gain 1 additional Spark.
- Grounded (Uncommon Power, 1): At the start of your turn, if none of your
  Bombs went off last turn, gain 6 Block and 1 Spark.

## The arms

1. **Explosive Spark** — Uncommon Attack, 0 energy, costs all your Sparks
   (X). Spend all your Sparks. Deal 3 damage per Spark spent. Upgrade: 4 per
   Spark. (Does not Set off. At 0 Sparks it does nothing and is not
   playable.)
2. **Countdown** — Common Skill, 1 energy. Set off. Draw 1 card. Upgrade:
   draw 2.

Two verdicts, each with its clause and its line. Under 200 words.
```

```
1. REQUIRES_MODIFICATION — C3. At 1 Spark, Explosive Spark deals 3 damage versus Fwoosh!’s 6 damage plus Set off, but its value scales only with banked Sparks rather than a Bomb decision.

2. FOLLOWS — C1–C6. Countdown costs 1 energy to Set off and draw 1, versus Sizzle’s same 1-energy Set off plus 6 damage, preserving a real losing line.
```

### 5.1 The pool pass, row 2 (same day, later)

Rounds 11 and 12 ended fights with 4 to 9 Sparks unspent, the surplus the
withdrawn sink was written for. A second sink was written whose value
follows the Bomb decision rather than the bank, at Quick Fuse's own rate,
and read through the same door:

| Row | Verdict | Clause |
|---|---|---|
| Stoke the Fuse (Uncommon Skill, 0 energy, X Sparks: your largest Bomb grows by 3 per Spark spent; no Set off) | **FOLLOWS** | C1 to C6: +3 for 1 Spark, Quick Fuse's rate, without its Set off |

The prompt was the row-1 prompt with the earlier verdicts stated and the
single arm below; the reply verbatim:

```
FOLLOWS — C1–C6; “Your largest Bomb grows by 3 per Spark spent” yields +3 for 1 Spark, matching Quick Fuse’s pool-row rate while lacking its Set off.
```

## 5.2 Tide Chart, redesigned under R257 (2026-09-04, evening)

The seat model is now GPT 6 Astra at low effort (the CLI's `gpt-6-astra`,
`model_reasoning_effort="low"`), the first read on it. The reply carried the
verdict and the clause list and no reasoning lines, which the prompt allowed.
Prompt, verbatim:

> # Doctrine read: one redesigned Kokomi row
>
> You are the adversarial reviewer for a Slay the Spire 2 character mod. The owner's rule: a new or redesigned card ships to a tester only if you rule it FOLLOWS. Read the one row below against the clauses and answer in this exact form: first line `FOLLOWS` or `REQUIRES_MODIFICATION`, then the clause ids you weighed, then at most ten lines of reasoning, then (if REQUIRES_MODIFICATION) the smallest modification that would make it FOLLOWS. No other text. You have no repo access; everything you need is here, and every card text below is pasted verbatim from the sheet.
>
> ## Clauses
>
> - **C1 (the owner's "not all agents always win").** A row that removes a losing line the kit is meant to keep, instead of pricing it, is out.
> - **C2 (binding prices).** Every cost printed must bind at the moment it is paid; a card whose cost is routinely free is out.
> - **C3 (player-controlled leverage).** The card's value must follow a decision the player makes, not a state that arrives by itself.
> - **C4 (the kit's own constraint).** Kokomi's defence is Block and prevention only; nothing heals below Rare.
> - **C5 (nothing fires by itself).** No card triggers without a play or a Plan the player wrote.
> - **C6 (not strictly better).** A row may not be a strictly better version of a shipped POOL row (listed below) or of a base-game non-basic card at the same or lower rarity and cost. Strike and Defend are basics and are not reference points. Base-game draw Commons at 0 or 1 energy for reference: Acrobatics (Common, 1: draw 3, discard 1), Backflip (Common, 1: 4 Block, draw 2), Prepared (Common, 0: draw 1, discard 1), Skim (Uncommon, 1: draw 3).
>
> ## The engine, Kokomi (the Plan kit)
>
> A **Bake-Kurage** (jellyfish) is on her field every fight. Some cards print two halves: a now-line ("Apply 1 Weak to ALL enemies") and a **Plan** line ("Plan: Deal 5 damage and apply 1 Weak to ALL enemies"). Playing the card onto the Bake-Kurage *writes the Plan*: it does nothing now, and at the start of her next turn the Bake-Kurage *carries out* every Plan it holds, in order, as its own Hydro hits. Carry-outs take the target's Vulnerable; her Weak and Strength do not fold in. Plans are written by paying the card's energy the turn before. Starter: 4 Strike, 4 Defend, Kurage's Oath, Nereid's Ascension, Slack Water; 3 energy; HP 80. Relic: Tamakushi Casket, 2 Hydro damage to an enemy whenever she applies a debuff to it.
>
> ## The pool rows this one is read against (verbatim)
>
> - Read the Field (Common Skill, 1): "Gain 5 Block. Plan: Gain 10 Block."
> - Treatise (Uncommon Power, 1): "Once per turn, when the Bake-Kurage carries out a Plan, draw 1 card."
> - War Council (Uncommon Skill, 1): "Apply 1 Weak to ALL enemies. Plan: Deal 5 damage and apply 1 Weak to ALL enemies."
> - Nereid's Ascension (Rare Skill, 2, Exhaust): "Exhaust. Plan: for 2 turns, the Bake-Kurage carries out every Plan twice."
> - Change of Plans (Common Skill, 1, Exhaust): "Exhaust. The Bake-Kurage carries out your first Plan now."
> - Tide Chart as shipped today (Common Skill, 0): "Draw 1 card for each Plan the Bake-Kurage holds." — in a targeted blind run it drew zero on three of four plays, because it reads the memory before the Plans are written and after they are written the turn is ending. This row is being replaced.
>
> ## The row under review
>
> - **Tide Chart, redesigned (Common Skill, 0 energy):** "Next turn, after the Bake-Kurage carries out its Plans, draw 1 card for each." Upgrade: draw 1 more (so 1 per Plan, plus 1). Played on the turn the Plans are written; pays at the start of the next turn, after the carry-outs, for the Plans that were actually carried out. With no Plan written it draws nothing (base) or 1 (upgraded).

Reply, verbatim:

> FOLLOWS
> C1, C2, C3, C4, C5, C6

**Outcome:** FOLLOWS. The row builds under `EB-478`.

