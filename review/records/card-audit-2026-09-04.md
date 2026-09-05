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



## 5.3 The Klee pool pass, ten rows (2026-09-05, morning)

The pass packet (`review/active/klee-pool-pass-2026-09-05.md`) put ten rows
through the doctrine role on GPT 6 Astra at low effort, the second read on
it, with the pool census pasted from the sheet by a script (37 rows) and
two precedents stated in the prompt: a Rare may break the rule its loop
names (the brief §5), and a reader Power may be dead alone (R244 pick 2).
All ten came back FOLLOWS, each with a clause and an arithmetic line naming
a pool row; the Vermillion Pact verdict names C5 as the Rare exception the
prompt allowed. Nothing withdrawn. Prompt, then reply, verbatim:

```
# Doctrine read: ten Klee pool-pass rows against the kit charter

Each numbered card below is ONE ARM. For each, FOLLOWS or
REQUIRES_MODIFICATION, the clause (C1 to C6) you ruled against, and the line
of the card with its arithmetic in one sentence, naming the pool row you
compared it to. Read adversarially; the author is a different model family
and the owner wants the row that should not reach a tester named. Two
precedents you may cite: the kit's three Rares each break one of its rules
by design (the brief, section 5), so a Rare breaking the rule its loop names
is not a C5 failure by itself; and R244 pick 2 ruled a reader Power dead
alone on purpose (drafted only by a deck that already holds what it reads),
so "dead in a deck with no applier" is not by itself a failure either.

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
an Attack). Each Bomb grows separately. A **Mine** also goes off when its
enemy attacks her. **Spark**: she starts each combat with 1, gains 1 per
Bomb going off, and cards that print a Spark price spend Sparks instead of
energy; no cap, lost at the end of combat. **Retain** keeps a card in hand
at the end of the turn. A Confiscated is an unplayable status card. Energy
3, HP 62. Starter: 4 Strike, 4 Defend, Ka-pow! (basic, 0 energy, Retain:
"Set off. Deal 4 damage."), Jumpy Dumpty (basic, 1: "Place a Bomb 8. When
it goes off, place a Mine 3 on ALL enemies.").

The readings these rows answer, from rounds 13 to 16: Ka-pow! is the only
Retained detonator, so with it undrawn "hold the Bomb" means "throw the
detonator away", and with it in hand the last turn of a fight is
automatic; a debuff that limits Skills per turn switches the kit off
because every placer is a Skill; the React shelf is four rows and its
reader Power is dead in a mono-Pyro deck.

## The pool, every row pasted from the sheet (rarity, type, price)

- Ka-pow! (Basic Attack, 0 energy, Retain): Set off. Deal 4 damage.
- Jumpy Dumpty (Basic Skill, 1 energy): Place a Bomb 8. When it goes off, place a Mine 3 on ALL enemies.
- Fish-Flavored Bait (Common Attack, 1 energy): Deal 4 damage. Place a Bomb 4.
- Pocket Fireworks (Common Attack, 1 energy): Deal 9 damage.
- Chain Fuse (Common Skill, 1 energy): Each Bomb on the enemy grows by 6.
- Explosives Workshop (Uncommon Power, 1 energy): At the start of your turn, your Bombs grow by 1 more.
- Careful Arrangement (Uncommon Skill, 1 energy): Move all your Bombs onto the enemy as one Bomb. It grows by 5.
- Big Badda Boom (Uncommon Attack, 2 energy): Set off. Deal 12 damage. Then deal damage equal to what the Bombs dealt.
- The Big One (Rare Attack, 3 energy): Set off for quadruple damage.
- Alice's Recipe (Rare Power, 2 energy): Your Bombs grow twice each turn.
- Pop! (Common Skill, 0 energy): Place a Bomb 5.
- Mine Toss (Common Skill, 1 energy): Place a Mine 4 on ALL enemies.
- Fwoosh! (Common Attack, 0 energy, 1 Spark): Set off. Deal 6 damage.
- Tinder Toss (Common Attack, 0 energy, 1 Spark): Set off a random enemy and deal 4 damage to it, twice.
- Quick Fuse (Common Skill, 0 energy, 1 Spark): Each Bomb on the enemy grows by 3. Set off.
- Bang Bang! (Uncommon Attack, 0 energy, 2 Spark): Set off. Deal 8 damage. Place a Bomb 4.
- Rapid Fire (Uncommon Attack, 2 energy): Set off a random enemy and deal 3 damage to it, 4 times.
- Chained Reactions (Rare Power, 1 energy): Whenever one of your Bombs goes off, place a Bomb 3 on a random enemy.
- Sparks 'n' Splash (proto) (Rare Power, 2 energy): At the end of your turn, deal Pyro damage to a random enemy equal to its largest Bomb.
- Sizzle (Common Attack, 1 energy): Set off. Deal 6 damage. If a Bomb triggered an Elemental Reaction this turn, deal 6 additional damage.
- Perfect Timing (Uncommon Attack, 1 energy): Set off. Deal 8 damage. If a Bomb triggered an Elemental Reaction this turn, play this again.
- Flame Dance (Uncommon Attack, 1 energy): Set off each enemy whose aura is not Pyro. Deal 5 damage to ALL enemies.
- Catalytic Converter (Uncommon Power, 1 energy): Whenever one of your Bombs triggers an Elemental Reaction, gain 1 additional Spark.
- Ammo Scavenging (Common Skill, 1 energy): Place a Bomb 4. Draw 1 card for each of your Bombs that went off this turn.
- Powder Charge (Uncommon Skill, 0 energy, 1 Spark): Place a Bomb 6.
- Dig In (Common Skill, 0 energy, 1 Spark): Gain 8 Block.
- Sugar Rush (Rare Skill, 0 energy, 2 Spark, Exhaust): Gain 2 Energy. Draw 1 card. Exhaust.
- Run Away! (Common Skill, 0 energy): Gain 3 Block. If a Bomb went off this turn, gain 4 additional Block.
- Grounded (Uncommon Power, 1 energy): At the start of your turn, if none of your Bombs went off last turn, gain 6 Block and 1 Spark.
- Sorry, Jean... (Common Skill, 0 energy): Remove one of your Bombs. Gain Block equal to its size.
- Dodoco Cover (Common Skill, 1 energy): Place a Bomb 4. Gain 5 Block.
- Careful Now (Uncommon Skill, 1 energy, Retain): Gain Block equal to your largest Bomb when played, up to 10.
- Coven Errand (Common Skill, 1 energy): Place a Bomb 5. If you played a Hexerei card this turn, place it on ALL enemies instead.
- Witches' Circle (Uncommon Power, 1 energy): Whenever you play a Hexerei card, place a Bomb 3 on a random enemy.
- Alice's Introduction Magic (Rare Skill, 1 energy): All cards in your hand count as Hexerei cards this turn.
- Countdown (Common Skill, 1 energy): Set off. Draw 1 card.
- Stoke the Fuse (Uncommon Skill, 0 energy, all Spark): Spend all your Sparks. Your largest Bomb grows by 3 per Spark spent.

## The arms

1. **Long Fuse** — Common Attack, 1 energy, Retain. Set off. Deal 6 damage.
   Retain. Costs 1 more each turn it stays in your hand. Upgrade: 9 damage.
2. **All of My Treasures!** — Rare Skill, 1 energy, Exhaust. Place a Bomb
   on the enemy equal to your largest Bomb.
3. **Fish Blasting** — Common Attack, 1 energy. Deal 5 damage to ALL
   enemies. Shuffle a Confiscated into your draw pile. Upgrade: 8 damage.
4. **Pocket Match** — Common Attack, 0 energy, 1 Spark, Retain. Set off.
   Deal 5 damage. Upgrade: 7 damage.
5. **Bombs Away!** — Common Attack, 1 energy. Deal 3 damage to ALL enemies.
   Place a Bomb 2 on ALL enemies. Upgrade: Bomb 4.
6. **Fireworks Show** — Uncommon Skill, 0 energy, 2 Sparks. Set off ALL
   enemies. Upgrade: 1 Spark.
7. **Kindling** — Common Skill, 0 energy. Each Bomb on an enemy whose aura
   is not Pyro grows by 4. If there is none, your largest Bomb grows by 2.
   Upgrade: 6 and 3.
8. **Flash Point** — Uncommon Attack, 1 energy. Set off. Deal 7 damage. If
   a Bomb triggered an Elemental Reaction this turn, gain 1 Spark and draw
   1 card. Upgrade: 10 damage.
9. **Vermillion Pact** — Rare Power, 2 energy. Whenever one of your Bombs
   triggers an Elemental Reaction, the Attack that Set it off triggers one
   too. Upgrade: 1 energy.
10. **Split Charge** — Uncommon Skill, 1 energy. Split your largest Bomb
    into two halves on random enemies. Upgrade: each half grows by 2.

Ten verdicts, each with its clause and its line. Under 400 words.
```

```
1. **FOLLOWS — C2.** Long Fuse’s 6 damage matches Sizzle’s floor, but retaining it once raises its cost from 1 to 2 energy: keeping the detonator carries a binding price.

2. **FOLLOWS — C3.** All of My Treasures! makes one largest Bomb’s banked value into twice that value across two charges; unlike The Big One’s quadruple cash-out, it leaves detonation pending.

3. **FOLLOWS — C6.** Fish Blasting deals 5 per enemy against Pocket Fireworks’ 9 to one, while adding a Confiscated; against Cleave’s 8 to ALL, it loses 3 per enemy and adds the status.

4. **FOLLOWS — C6.** Pocket Match buys Retain by dealing 5 rather than Fwoosh!’s 6 at the same Spark price.

5. **FOLLOWS — C6.** Bombs Away! delivers 3 immediate plus Bomb 2 per enemy, below Fish-Flavored Bait’s 4 plus Bomb 4 against one enemy; breadth costs concentrated output.

6. **FOLLOWS — C2.** Fireworks Show spends 2 Sparks for field-wide detonation; against one enemy, Fwoosh! spends 1 and adds 6 damage, establishing a worse turn.

7. **FOLLOWS — C2.** Kindling adds only 2 with exclusively Pyro auras, or 4 to one eligible Bomb, versus Pop!’s new Bomb 5; without existing Bombs it adds nothing.

8. **FOLLOWS — C6.** Flash Point’s reaction payoff adds 1 Spark and 1 draw to 7 damage, while Sizzle reaches 6 + 6 = 12; the utility trades away 5 immediate damage.

9. **FOLLOWS — C5.** Vermillion Pact’s automatic reaction is its named Rare exception; its 2-energy investment, compared with Catalytic Converter’s 1, produces zero payoff without a qualifying Bomb reaction.

10. **FOLLOWS — C2.** Split Charge preserves the initial total across two halves and increases subsequent combined growth from 4 to 8, but random placement sacrifices targeting and supplies none of Careful Arrangement’s immediate +5.
```


## 5.4 The Kokomi pool pass, six rows in four reads (2026-09-05, morning)

The pass packet (`review/active/kokomi-pool-pass-2026-09-05.md`) put six
rows through the doctrine role on GPT 6 Astra at low effort with the pool
census pasted from the sheet by a script (32 rows). Read one passed Flank,
Well Laid and Feigned Retreat and ruled Riptide, Pincer and the redesigned
Nereid's Ascension REQUIRES_MODIFICATION on C6 with no comparison line.
Reads two and three asked for the comparison; the second also asked for
"the smallest modification", which the seat's protocol forbids, and both
came back as bare verdicts. The comparisons were derived by the author off
shipped cards (Riptide against Kurage's Oath, Pincer against Feint, the
new Nereid's against the printed row it replaces), the three rows were
re-priced (Riptide to 2 energy at 9 and 13; Pincer to 3 per hit; the old
Nereid's row struck from the census as replaced, with The Moon Overlooks
the Waters named as the standing Rare Power), and read four passed all
three. **Outcome:** six FOLLOWS; the pass builds under `EB-492`. Lesson:
a C6 verdict is asked for its comparison row in the first prompt and
never for a modification. The four prompts and replies, verbatim:

### Read 1

```
# Doctrine read: six Kokomi pool-pass rows against the kit charter

You are the adversarial reviewer for a Slay the Spire 2 character mod. The
owner's rule: a new or redesigned card ships to a tester only if you rule it
FOLLOWS. Each numbered card below is ONE ARM. For each, FOLLOWS or
REQUIRES_MODIFICATION, the clause ids you weighed, and one sentence with the
card's arithmetic naming the pool row you compared it to; for a
REQUIRES_MODIFICATION, the smallest change that would make it FOLLOWS. Read
adversarially; the author is a different model family and the owner wants
the row that should not reach a tester named. One precedent you may cite:
the brief names Nereid's Ascension as the one Rare that breaks the kit's
rule 3 ("carried out once, in order"), so its doubling is not a C5 failure
by itself. You have no repo access; every card text below is pasted
verbatim from the sheet.

## Clauses

- **C1 (the owner's "not all agents always win").** A row that removes a
  losing line the kit is meant to keep, instead of pricing it, is out.
- **C2 (binding prices).** Every cost printed must bind at the moment it is
  paid; a card whose cost is routinely free is out.
- **C3 (player-controlled leverage).** The card's value must follow a
  decision the player makes (write the Plan or play it now; aim it), not a
  state that arrives by itself.
- **C4 (the kit's own constraint).** Kokomi's defence is Block and
  prevention only; nothing heals below Rare.
- **C5 (nothing fires by itself).** No card triggers without a play or a
  Plan the player wrote.
- **C6 (not strictly better).** A row may not be a strictly better version
  of a shipped POOL row (listed below) or of a base-game non-basic card at
  the same or lower rarity and cost. Strike and Defend are basics and are
  not reference points. Base-game Commons for reference: Cleave (1: 8 to
  ALL), Twin Strike (1: 5 twice), Pommel Strike (1: 9, draw 1), Iron Wave
  (1: 5 Block and 5 damage), Sword Boomerang (1: 3 to a random enemy three
  times), Thunderclap (1: 4 to ALL and Vulnerable).

## The engine, Kokomi (the Plan kit)

A **Bake-Kurage** (jellyfish) is on her field every fight. Some cards
print two halves: a now-line and a **Plan** line. Playing the card onto the
Bake-Kurage *writes the Plan*: it does nothing now, and at the start of her
next turn, before she draws, the Bake-Kurage *carries out* every Plan it
holds, in the order written, as its own Hydro hits. A planned
single-target line is aimed at an enemy when it is written (R250). Carry-outs
take the target's Vulnerable; her Weak does not fold in. The energy is paid
the turn before. Starter: 4 Strike, 4 Defend, Kurage's Oath, Slack Water;
3 energy; HP 80. Relic: Tamakushi Casket, 2 Hydro damage to an enemy
whenever she applies a debuff to it. "This morning" means the carry-outs
at the start of the current turn.

The readings these rows answer, rounds 10 to 16: seats draft the Attacks
they are offered and the pool's Attacks mostly carry no Plan line, so the
jellyfish stands empty on most turns; Nereid's Ascension as printed "reads
like the kit's payoff and behaves like a tax" (two energy, Exhaust, and a
Plan slot for two turns of doubling in a deck with two Plan cards).

## The pool, every row pasted from the sheet (rarity, type, price)

- Kurage's Oath (Basic Skill, 1 energy): Deal 3 damage to ALL enemies. Plan: Deal 7 damage to ALL enemies.
- Slack Water (Basic Attack, 1 energy): Deal 4 damage. Apply 1 Weak. Plan: Apply 1 Weak to ALL enemies.
- Feint (Common Attack, 1 energy): Deal 6 damage. Plan: Deal 10 damage.
- Ambush (Common Skill, 1 energy): Deal 5 damage. Plan: Deal 12 damage.
- Read the Field (Common Skill, 1 energy): Gain 5 Block. Plan: Gain 10 Block.
- Exposed Flank (Common Skill, 1 energy): Apply 1 Vulnerable. Plan: Apply 2 Vulnerable to ALL enemies.
- Treatise (Uncommon Power, 1 energy): Once per turn, when the Bake-Kurage carries out a Plan, draw 1 card.
- Song of Pearls (Uncommon Power, 1 energy): Once per turn, when the Bake-Kurage carries out a Plan, gain 3 Block.
- War Council (Uncommon Skill, 1 energy): Apply 1 Weak to ALL enemies. Plan: Deal 5 damage and apply 1 Weak to ALL enemies.
- Nereid's Ascension (Rare Skill, 2 energy, Exhaust): Exhaust. Plan: for 2 turns, the Bake-Kurage carries out every Plan twice.
- The Moon Overlooks the Waters (Rare Power, 2 energy): Plans also happen now, as you write them.
- Sea-Salt Prayer (Common Skill, 1 energy): Gain 4 Block. Apply 1 Weak.
- Deep Current (Common Attack, 1 energy): Deal 6 damage to ALL enemies.
- Coral Bulwark (Common Skill, 1 energy): Gain 6 Block. Plan: Gain 8 Block and apply 1 Weak.
- Cleansing Wave (Uncommon Skill, 1 energy): Gain 5 Block. Remove one of your debuffs. Plan: Gain 10 Block.
- Tide Wall (Uncommon Skill, 1 energy): Gain 4 Block. Plan: Gain 3 Block for each Plan the Bake-Kurage carries out this morning.
- Shell Guard (Uncommon Skill, 1 energy): Gain 5 Block. Until your next turn, whenever the Tamakushi Casket strikes, gain 3 Block.
- The Clouds Like Waves Rippling (Rare Power, 2 energy): Whenever you apply a debuff to an enemy, gain 2 Block.
- The Moon, A Ship O'er the Seas (Rare Skill, 2 energy, Exhaust): Exhaust. Mend 3. Plan: Mend 6.
- Sango Isshin (Rare Attack, 2 energy): Deal 8 damage. If the Bake-Kurage carried out a Plan this turn, deal a quarter of your Max HP to ALL enemies instead.
- Rally (Common Skill, 1 energy): Apply 1 Weak. The next Companion card you play this turn costs 1 less.
- Vanguard (Common Skill, 0 energy, Exhaust): Exhaust. Apply 1 Vulnerable. Plan: Apply 1 Vulnerable and 1 Weak.
- The General's Banner (Uncommon Power, 1 energy): Once per turn, when you play a Companion card, apply 1 Weak to the front enemy.
- Chain of Command (Uncommon Skill, 1 energy): Deal 3 damage for each Companion you played this turn. Plan: Deal 6 damage for each Companion you played last turn.
- Stolen Chapter (Common Skill, 1 energy): Draw 1 card. Plan: Draw 4 cards.
- Change of Plans (Common Skill, 1 energy, Exhaust): Exhaust. The Bake-Kurage carries out your first Plan now.
- Undertow (Common Attack, 1 energy): Deal 4 damage, already including 3 if the enemy has a debuff.
- Salt Line (Common Skill, 1 energy, Exhaust): Exhaust. Gain 8 Block.
- Battle Plan (Uncommon Skill, 1 energy): Draw 1 card. Plan: Gain 1 Energy and draw 2 cards.
- Moon's Reflection (Uncommon Skill, 1 energy, Exhaust): Exhaust. Choose a card in your Exhaust Pile. Next turn, the Bake-Kurage carries out its Plan line, or plays it if it has none.
- Tide Chart (Common Skill, 0 energy): Next turn, after the Bake-Kurage carries out its Plans, draw 1 card for each.
- Ripple (Common Skill, 0 energy): Gain 2 Block. Plan: Gain 1 Energy and 4 Block.

## The arms

1. **Riptide** — Common Attack, 1 energy. Deal 5 damage to ALL enemies.
   Plan: Deal 9 damage to ALL enemies. Upgrade: 7 and 12.
2. **Pincer** — Common Attack, 1 energy. Deal 4 damage twice. Plan: Deal 4
   damage three times. Upgrade: 5 per hit.
3. **Flank** — Uncommon Attack, 1 energy. Deal 8 damage. Plan: Deal 8 damage
   to each enemy that intends to attack. (The set of enemies is fixed when
   the Plan is written, from the intents shown then.) Upgrade: 11.
4. **Well Laid** — Common Attack, 0 energy. Deal 2 damage. Deals 3 more for
   each Plan the Bake-Kurage carried out this morning. Upgrade: 3 and 4.
5. **Feigned Retreat** — Common Skill, 1 energy. Gain 4 Block. Plan: Gain 4
   Block and deal 6 damage. Upgrade: 6 Block; 6 Block and 8 damage.
6. **Nereid's Ascension, redesigned** — Rare Power, 2 energy. The
   Bake-Kurage carries out every Plan twice. Upgrade: costs 1. (Replaces the
   pool row of the same name above: no longer Exhaust, no longer a Plan, no
   longer two turns.)

Six verdicts, each with its clauses and its line. Under 300 words.
```

```
1. **REQUIRES_MODIFICATION — C6 (not strictly better).**
2. **REQUIRES_MODIFICATION — C6 (not strictly better).**
3. **FOLLOWS — C1–C6.**
4. **FOLLOWS — C1–C6.**
5. **FOLLOWS — C1–C6.**
6. **REQUIRES_MODIFICATION — C6 (not strictly better).**
```

### Read 2 (the ask for a modification, refused by protocol)

```
# Doctrine read: six Kokomi pool-pass rows against the kit charter

You are the adversarial reviewer for a Slay the Spire 2 character mod. The
owner's rule: a new or redesigned card ships to a tester only if you rule it
FOLLOWS. Each numbered card below is ONE ARM. For each, FOLLOWS or
REQUIRES_MODIFICATION, the clause ids you weighed, and one sentence with the
card's arithmetic naming the pool row you compared it to; for a
REQUIRES_MODIFICATION, the smallest change that would make it FOLLOWS. Read
adversarially; the author is a different model family and the owner wants
the row that should not reach a tester named. One precedent you may cite:
the brief names Nereid's Ascension as the one Rare that breaks the kit's
rule 3 ("carried out once, in order"), so its doubling is not a C5 failure
by itself. You have no repo access; every card text below is pasted
verbatim from the sheet.

## Clauses

- **C1 (the owner's "not all agents always win").** A row that removes a
  losing line the kit is meant to keep, instead of pricing it, is out.
- **C2 (binding prices).** Every cost printed must bind at the moment it is
  paid; a card whose cost is routinely free is out.
- **C3 (player-controlled leverage).** The card's value must follow a
  decision the player makes (write the Plan or play it now; aim it), not a
  state that arrives by itself.
- **C4 (the kit's own constraint).** Kokomi's defence is Block and
  prevention only; nothing heals below Rare.
- **C5 (nothing fires by itself).** No card triggers without a play or a
  Plan the player wrote.
- **C6 (not strictly better).** A row may not be a strictly better version
  of a shipped POOL row (listed below) or of a base-game non-basic card at
  the same or lower rarity and cost. Strike and Defend are basics and are
  not reference points. Base-game Commons for reference: Cleave (1: 8 to
  ALL), Twin Strike (1: 5 twice), Pommel Strike (1: 9, draw 1), Iron Wave
  (1: 5 Block and 5 damage), Sword Boomerang (1: 3 to a random enemy three
  times), Thunderclap (1: 4 to ALL and Vulnerable).

## The engine, Kokomi (the Plan kit)

A **Bake-Kurage** (jellyfish) is on her field every fight. Some cards
print two halves: a now-line and a **Plan** line. Playing the card onto the
Bake-Kurage *writes the Plan*: it does nothing now, and at the start of her
next turn, before she draws, the Bake-Kurage *carries out* every Plan it
holds, in the order written, as its own Hydro hits. A planned
single-target line is aimed at an enemy when it is written (R250). Carry-outs
take the target's Vulnerable; her Weak does not fold in. The energy is paid
the turn before. Starter: 4 Strike, 4 Defend, Kurage's Oath, Slack Water;
3 energy; HP 80. Relic: Tamakushi Casket, 2 Hydro damage to an enemy
whenever she applies a debuff to it. "This morning" means the carry-outs
at the start of the current turn.

The readings these rows answer, rounds 10 to 16: seats draft the Attacks
they are offered and the pool's Attacks mostly carry no Plan line, so the
jellyfish stands empty on most turns; Nereid's Ascension as printed "reads
like the kit's payoff and behaves like a tax" (two energy, Exhaust, and a
Plan slot for two turns of doubling in a deck with two Plan cards).

## The pool, every row pasted from the sheet (rarity, type, price)

- Kurage's Oath (Basic Skill, 1 energy): Deal 3 damage to ALL enemies. Plan: Deal 7 damage to ALL enemies.
- Slack Water (Basic Attack, 1 energy): Deal 4 damage. Apply 1 Weak. Plan: Apply 1 Weak to ALL enemies.
- Feint (Common Attack, 1 energy): Deal 6 damage. Plan: Deal 10 damage.
- Ambush (Common Skill, 1 energy): Deal 5 damage. Plan: Deal 12 damage.
- Read the Field (Common Skill, 1 energy): Gain 5 Block. Plan: Gain 10 Block.
- Exposed Flank (Common Skill, 1 energy): Apply 1 Vulnerable. Plan: Apply 2 Vulnerable to ALL enemies.
- Treatise (Uncommon Power, 1 energy): Once per turn, when the Bake-Kurage carries out a Plan, draw 1 card.
- Song of Pearls (Uncommon Power, 1 energy): Once per turn, when the Bake-Kurage carries out a Plan, gain 3 Block.
- War Council (Uncommon Skill, 1 energy): Apply 1 Weak to ALL enemies. Plan: Deal 5 damage and apply 1 Weak to ALL enemies.
- Nereid's Ascension (Rare Skill, 2 energy, Exhaust): Exhaust. Plan: for 2 turns, the Bake-Kurage carries out every Plan twice.
- The Moon Overlooks the Waters (Rare Power, 2 energy): Plans also happen now, as you write them.
- Sea-Salt Prayer (Common Skill, 1 energy): Gain 4 Block. Apply 1 Weak.
- Deep Current (Common Attack, 1 energy): Deal 6 damage to ALL enemies.
- Coral Bulwark (Common Skill, 1 energy): Gain 6 Block. Plan: Gain 8 Block and apply 1 Weak.
- Cleansing Wave (Uncommon Skill, 1 energy): Gain 5 Block. Remove one of your debuffs. Plan: Gain 10 Block.
- Tide Wall (Uncommon Skill, 1 energy): Gain 4 Block. Plan: Gain 3 Block for each Plan the Bake-Kurage carries out this morning.
- Shell Guard (Uncommon Skill, 1 energy): Gain 5 Block. Until your next turn, whenever the Tamakushi Casket strikes, gain 3 Block.
- The Clouds Like Waves Rippling (Rare Power, 2 energy): Whenever you apply a debuff to an enemy, gain 2 Block.
- The Moon, A Ship O'er the Seas (Rare Skill, 2 energy, Exhaust): Exhaust. Mend 3. Plan: Mend 6.
- Sango Isshin (Rare Attack, 2 energy): Deal 8 damage. If the Bake-Kurage carried out a Plan this turn, deal a quarter of your Max HP to ALL enemies instead.
- Rally (Common Skill, 1 energy): Apply 1 Weak. The next Companion card you play this turn costs 1 less.
- Vanguard (Common Skill, 0 energy, Exhaust): Exhaust. Apply 1 Vulnerable. Plan: Apply 1 Vulnerable and 1 Weak.
- The General's Banner (Uncommon Power, 1 energy): Once per turn, when you play a Companion card, apply 1 Weak to the front enemy.
- Chain of Command (Uncommon Skill, 1 energy): Deal 3 damage for each Companion you played this turn. Plan: Deal 6 damage for each Companion you played last turn.
- Stolen Chapter (Common Skill, 1 energy): Draw 1 card. Plan: Draw 4 cards.
- Change of Plans (Common Skill, 1 energy, Exhaust): Exhaust. The Bake-Kurage carries out your first Plan now.
- Undertow (Common Attack, 1 energy): Deal 4 damage, already including 3 if the enemy has a debuff.
- Salt Line (Common Skill, 1 energy, Exhaust): Exhaust. Gain 8 Block.
- Battle Plan (Uncommon Skill, 1 energy): Draw 1 card. Plan: Gain 1 Energy and draw 2 cards.
- Moon's Reflection (Uncommon Skill, 1 energy, Exhaust): Exhaust. Choose a card in your Exhaust Pile. Next turn, the Bake-Kurage carries out its Plan line, or plays it if it has none.
- Tide Chart (Common Skill, 0 energy): Next turn, after the Bake-Kurage carries out its Plans, draw 1 card for each.
- Ripple (Common Skill, 0 energy): Gain 2 Block. Plan: Gain 1 Energy and 4 Block.

## Your verdicts on the first read, and what is missing

You ruled Riptide, Pincer and the redesigned Nereid's Ascension
REQUIRES_MODIFICATION on C6 and gave no line. The owner records the row you
compared each to, its arithmetic, and the smallest modification; a verdict
without them cannot be acted on. For EACH of the three arms below, write
exactly three lines: (a) the pool row or base-game card it is strictly
better than, with both cards' numbers; (b) whether "strictly better" holds
on every line (now-line, Plan line, cost, rarity, drawback) or only some;
(c) the smallest modification that makes it FOLLOWS.

## The arms

1. **Riptide** — Common Attack, 1 energy. Deal 5 damage to ALL enemies.
   Plan: Deal 9 damage to ALL enemies. Upgrade: 7 and 12.
2. **Pincer** — Common Attack, 1 energy. Deal 4 damage twice. Plan: Deal 4
   damage three times. Upgrade: 5 per hit.
6. **Nereid's Ascension, redesigned** — Rare Power, 2 energy. The
   Bake-Kurage carries out every Plan twice. Upgrade: costs 1. (Replaces the
   pool row of the same name above: no longer Exhaust, no longer a Plan, no
   longer two turns.)

Nine lines total. No other text.
```

```
1. REQUIRES_MODIFICATION — C6 (not strictly better).
2. REQUIRES_MODIFICATION — C6 (not strictly better).
6. REQUIRES_MODIFICATION — C6 (not strictly better).
```

### Read 3 (the ask for the comparison only, still bare)

```
# Doctrine read: six Kokomi pool-pass rows against the kit charter

You are the adversarial reviewer for a Slay the Spire 2 character mod. The
owner's rule: a new or redesigned card ships to a tester only if you rule it
FOLLOWS. Each numbered card below is ONE ARM. For each, FOLLOWS or
REQUIRES_MODIFICATION, the clause ids you weighed, and one sentence with the
card's arithmetic naming the pool row you compared it to; for a
REQUIRES_MODIFICATION, the smallest change that would make it FOLLOWS. Read
adversarially; the author is a different model family and the owner wants
the row that should not reach a tester named. One precedent you may cite:
the brief names Nereid's Ascension as the one Rare that breaks the kit's
rule 3 ("carried out once, in order"), so its doubling is not a C5 failure
by itself. You have no repo access; every card text below is pasted
verbatim from the sheet.

## Clauses

- **C1 (the owner's "not all agents always win").** A row that removes a
  losing line the kit is meant to keep, instead of pricing it, is out.
- **C2 (binding prices).** Every cost printed must bind at the moment it is
  paid; a card whose cost is routinely free is out.
- **C3 (player-controlled leverage).** The card's value must follow a
  decision the player makes (write the Plan or play it now; aim it), not a
  state that arrives by itself.
- **C4 (the kit's own constraint).** Kokomi's defence is Block and
  prevention only; nothing heals below Rare.
- **C5 (nothing fires by itself).** No card triggers without a play or a
  Plan the player wrote.
- **C6 (not strictly better).** A row may not be a strictly better version
  of a shipped POOL row (listed below) or of a base-game non-basic card at
  the same or lower rarity and cost. Strike and Defend are basics and are
  not reference points. Base-game Commons for reference: Cleave (1: 8 to
  ALL), Twin Strike (1: 5 twice), Pommel Strike (1: 9, draw 1), Iron Wave
  (1: 5 Block and 5 damage), Sword Boomerang (1: 3 to a random enemy three
  times), Thunderclap (1: 4 to ALL and Vulnerable).

## The engine, Kokomi (the Plan kit)

A **Bake-Kurage** (jellyfish) is on her field every fight. Some cards
print two halves: a now-line and a **Plan** line. Playing the card onto the
Bake-Kurage *writes the Plan*: it does nothing now, and at the start of her
next turn, before she draws, the Bake-Kurage *carries out* every Plan it
holds, in the order written, as its own Hydro hits. A planned
single-target line is aimed at an enemy when it is written (R250). Carry-outs
take the target's Vulnerable; her Weak does not fold in. The energy is paid
the turn before. Starter: 4 Strike, 4 Defend, Kurage's Oath, Slack Water;
3 energy; HP 80. Relic: Tamakushi Casket, 2 Hydro damage to an enemy
whenever she applies a debuff to it. "This morning" means the carry-outs
at the start of the current turn.

The readings these rows answer, rounds 10 to 16: seats draft the Attacks
they are offered and the pool's Attacks mostly carry no Plan line, so the
jellyfish stands empty on most turns; Nereid's Ascension as printed "reads
like the kit's payoff and behaves like a tax" (two energy, Exhaust, and a
Plan slot for two turns of doubling in a deck with two Plan cards).

## The pool, every row pasted from the sheet (rarity, type, price)

- Kurage's Oath (Basic Skill, 1 energy): Deal 3 damage to ALL enemies. Plan: Deal 7 damage to ALL enemies.
- Slack Water (Basic Attack, 1 energy): Deal 4 damage. Apply 1 Weak. Plan: Apply 1 Weak to ALL enemies.
- Feint (Common Attack, 1 energy): Deal 6 damage. Plan: Deal 10 damage.
- Ambush (Common Skill, 1 energy): Deal 5 damage. Plan: Deal 12 damage.
- Read the Field (Common Skill, 1 energy): Gain 5 Block. Plan: Gain 10 Block.
- Exposed Flank (Common Skill, 1 energy): Apply 1 Vulnerable. Plan: Apply 2 Vulnerable to ALL enemies.
- Treatise (Uncommon Power, 1 energy): Once per turn, when the Bake-Kurage carries out a Plan, draw 1 card.
- Song of Pearls (Uncommon Power, 1 energy): Once per turn, when the Bake-Kurage carries out a Plan, gain 3 Block.
- War Council (Uncommon Skill, 1 energy): Apply 1 Weak to ALL enemies. Plan: Deal 5 damage and apply 1 Weak to ALL enemies.
- Nereid's Ascension (Rare Skill, 2 energy, Exhaust): Exhaust. Plan: for 2 turns, the Bake-Kurage carries out every Plan twice.
- The Moon Overlooks the Waters (Rare Power, 2 energy): Plans also happen now, as you write them.
- Sea-Salt Prayer (Common Skill, 1 energy): Gain 4 Block. Apply 1 Weak.
- Deep Current (Common Attack, 1 energy): Deal 6 damage to ALL enemies.
- Coral Bulwark (Common Skill, 1 energy): Gain 6 Block. Plan: Gain 8 Block and apply 1 Weak.
- Cleansing Wave (Uncommon Skill, 1 energy): Gain 5 Block. Remove one of your debuffs. Plan: Gain 10 Block.
- Tide Wall (Uncommon Skill, 1 energy): Gain 4 Block. Plan: Gain 3 Block for each Plan the Bake-Kurage carries out this morning.
- Shell Guard (Uncommon Skill, 1 energy): Gain 5 Block. Until your next turn, whenever the Tamakushi Casket strikes, gain 3 Block.
- The Clouds Like Waves Rippling (Rare Power, 2 energy): Whenever you apply a debuff to an enemy, gain 2 Block.
- The Moon, A Ship O'er the Seas (Rare Skill, 2 energy, Exhaust): Exhaust. Mend 3. Plan: Mend 6.
- Sango Isshin (Rare Attack, 2 energy): Deal 8 damage. If the Bake-Kurage carried out a Plan this turn, deal a quarter of your Max HP to ALL enemies instead.
- Rally (Common Skill, 1 energy): Apply 1 Weak. The next Companion card you play this turn costs 1 less.
- Vanguard (Common Skill, 0 energy, Exhaust): Exhaust. Apply 1 Vulnerable. Plan: Apply 1 Vulnerable and 1 Weak.
- The General's Banner (Uncommon Power, 1 energy): Once per turn, when you play a Companion card, apply 1 Weak to the front enemy.
- Chain of Command (Uncommon Skill, 1 energy): Deal 3 damage for each Companion you played this turn. Plan: Deal 6 damage for each Companion you played last turn.
- Stolen Chapter (Common Skill, 1 energy): Draw 1 card. Plan: Draw 4 cards.
- Change of Plans (Common Skill, 1 energy, Exhaust): Exhaust. The Bake-Kurage carries out your first Plan now.
- Undertow (Common Attack, 1 energy): Deal 4 damage, already including 3 if the enemy has a debuff.
- Salt Line (Common Skill, 1 energy, Exhaust): Exhaust. Gain 8 Block.
- Battle Plan (Uncommon Skill, 1 energy): Draw 1 card. Plan: Gain 1 Energy and draw 2 cards.
- Moon's Reflection (Uncommon Skill, 1 energy, Exhaust): Exhaust. Choose a card in your Exhaust Pile. Next turn, the Bake-Kurage carries out its Plan line, or plays it if it has none.
- Tide Chart (Common Skill, 0 energy): Next turn, after the Bake-Kurage carries out its Plans, draw 1 card for each.
- Ripple (Common Skill, 0 energy): Gain 2 Block. Plan: Gain 1 Energy and 4 Block.

## What the owner needs from this read

You ruled Riptide, Pincer and the redesigned Nereid's Ascension
REQUIRES_MODIFICATION on C6 (not strictly better). A C6 verdict is a
comparison, and the comparison is part of the reading, not a remedy: for
EACH of the three arms, restate the verdict and the clause, then name the
pool row or base-game card the arm is a strictly better version of, quoting
both cards' printed numbers on every line you compared (now-line, Plan line,
cost, rarity, drawback). Do not propose any change; the owner derives the
fix by lifting a value off a shipped card.

## The arms

1. **Riptide** — Common Attack, 1 energy. Deal 5 damage to ALL enemies.
   Plan: Deal 9 damage to ALL enemies. Upgrade: 7 and 12.
2. **Pincer** — Common Attack, 1 energy. Deal 4 damage twice. Plan: Deal 4
   damage three times. Upgrade: 5 per hit.
6. **Nereid's Ascension, redesigned** — Rare Power, 2 energy. The
   Bake-Kurage carries out every Plan twice. Upgrade: costs 1. (Replaces the
   pool row of the same name above: no longer Exhaust, no longer a Plan, no
   longer two turns.)

Three verdicts, each with its clause and the comparison it rests on.
```

```
1. Riptide — REQUIRES_MODIFICATION; C6 (not strictly better).
2. Pincer — REQUIRES_MODIFICATION; C6 (not strictly better).
6. Nereid’s Ascension, redesigned — REQUIRES_MODIFICATION; C6 (not strictly better).
```

### Read 4 (the three rows re-priced)

```
# Doctrine read: three re-priced Kokomi pool-pass rows against the kit charter

You are the adversarial reviewer for a Slay the Spire 2 character mod. The
owner's rule: a new or redesigned card ships to a tester only if you rule it
FOLLOWS. Each numbered card below is ONE ARM. For each, FOLLOWS or
REQUIRES_MODIFICATION, the clause you ruled against, and the line of the
card with its arithmetic in one sentence, naming the pool row you compared
it to. Read
adversarially; the author is a different model family and the owner wants
the row that should not reach a tester named. One precedent you may cite:
the brief names Nereid's Ascension as the one Rare that breaks the kit's
rule 3 ("carried out once, in order"), so its doubling is not a C5 failure
by itself. You have no repo access; every card text below is pasted
verbatim from the sheet.

## Clauses

- **C1 (the owner's "not all agents always win").** A row that removes a
  losing line the kit is meant to keep, instead of pricing it, is out.
- **C2 (binding prices).** Every cost printed must bind at the moment it is
  paid; a card whose cost is routinely free is out.
- **C3 (player-controlled leverage).** The card's value must follow a
  decision the player makes (write the Plan or play it now; aim it), not a
  state that arrives by itself.
- **C4 (the kit's own constraint).** Kokomi's defence is Block and
  prevention only; nothing heals below Rare.
- **C5 (nothing fires by itself).** No card triggers without a play or a
  Plan the player wrote.
- **C6 (not strictly better).** A row may not be a strictly better version
  of a shipped POOL row (listed below) or of a base-game non-basic card at
  the same or lower rarity and cost. Strike and Defend are basics and are
  not reference points. Base-game Commons for reference: Cleave (1: 8 to
  ALL), Twin Strike (1: 5 twice), Pommel Strike (1: 9, draw 1), Iron Wave
  (1: 5 Block and 5 damage), Sword Boomerang (1: 3 to a random enemy three
  times), Thunderclap (1: 4 to ALL and Vulnerable).

## The engine, Kokomi (the Plan kit)

A **Bake-Kurage** (jellyfish) is on her field every fight. Some cards
print two halves: a now-line and a **Plan** line. Playing the card onto the
Bake-Kurage *writes the Plan*: it does nothing now, and at the start of her
next turn, before she draws, the Bake-Kurage *carries out* every Plan it
holds, in the order written, as its own Hydro hits. A planned
single-target line is aimed at an enemy when it is written (R250). Carry-outs
take the target's Vulnerable; her Weak does not fold in. The energy is paid
the turn before. Starter: 4 Strike, 4 Defend, Kurage's Oath, Slack Water;
3 energy; HP 80. Relic: Tamakushi Casket, 2 Hydro damage to an enemy
whenever she applies a debuff to it. "This morning" means the carry-outs
at the start of the current turn.

The readings these rows answer, rounds 10 to 16: seats draft the Attacks
they are offered and the pool's Attacks mostly carry no Plan line, so the
jellyfish stands empty on most turns; Nereid's Ascension as printed "reads
like the kit's payoff and behaves like a tax" (two energy, Exhaust, and a
Plan slot for two turns of doubling in a deck with two Plan cards).

## The pool, every row pasted from the sheet (rarity, type, price)

- Kurage's Oath (Basic Skill, 1 energy): Deal 3 damage to ALL enemies. Plan: Deal 7 damage to ALL enemies.
- Slack Water (Basic Attack, 1 energy): Deal 4 damage. Apply 1 Weak. Plan: Apply 1 Weak to ALL enemies.
- Feint (Common Attack, 1 energy): Deal 6 damage. Plan: Deal 10 damage.
- Ambush (Common Skill, 1 energy): Deal 5 damage. Plan: Deal 12 damage.
- Read the Field (Common Skill, 1 energy): Gain 5 Block. Plan: Gain 10 Block.
- Exposed Flank (Common Skill, 1 energy): Apply 1 Vulnerable. Plan: Apply 2 Vulnerable to ALL enemies.
- Treatise (Uncommon Power, 1 energy): Once per turn, when the Bake-Kurage carries out a Plan, draw 1 card.
- Song of Pearls (Uncommon Power, 1 energy): Once per turn, when the Bake-Kurage carries out a Plan, gain 3 Block.
- War Council (Uncommon Skill, 1 energy): Apply 1 Weak to ALL enemies. Plan: Deal 5 damage and apply 1 Weak to ALL enemies.
- The Moon Overlooks the Waters (Rare Power, 2 energy): Plans also happen now, as you write them.
- Sea-Salt Prayer (Common Skill, 1 energy): Gain 4 Block. Apply 1 Weak.
- Deep Current (Common Attack, 1 energy): Deal 6 damage to ALL enemies.
- Coral Bulwark (Common Skill, 1 energy): Gain 6 Block. Plan: Gain 8 Block and apply 1 Weak.
- Cleansing Wave (Uncommon Skill, 1 energy): Gain 5 Block. Remove one of your debuffs. Plan: Gain 10 Block.
- Tide Wall (Uncommon Skill, 1 energy): Gain 4 Block. Plan: Gain 3 Block for each Plan the Bake-Kurage carries out this morning.
- Shell Guard (Uncommon Skill, 1 energy): Gain 5 Block. Until your next turn, whenever the Tamakushi Casket strikes, gain 3 Block.
- The Clouds Like Waves Rippling (Rare Power, 2 energy): Whenever you apply a debuff to an enemy, gain 2 Block.
- The Moon, A Ship O'er the Seas (Rare Skill, 2 energy, Exhaust): Exhaust. Mend 3. Plan: Mend 6.
- Sango Isshin (Rare Attack, 2 energy): Deal 8 damage. If the Bake-Kurage carried out a Plan this turn, deal a quarter of your Max HP to ALL enemies instead.
- Rally (Common Skill, 1 energy): Apply 1 Weak. The next Companion card you play this turn costs 1 less.
- Vanguard (Common Skill, 0 energy, Exhaust): Exhaust. Apply 1 Vulnerable. Plan: Apply 1 Vulnerable and 1 Weak.
- The General's Banner (Uncommon Power, 1 energy): Once per turn, when you play a Companion card, apply 1 Weak to the front enemy.
- Chain of Command (Uncommon Skill, 1 energy): Deal 3 damage for each Companion you played this turn. Plan: Deal 6 damage for each Companion you played last turn.
- Stolen Chapter (Common Skill, 1 energy): Draw 1 card. Plan: Draw 4 cards.
- Change of Plans (Common Skill, 1 energy, Exhaust): Exhaust. The Bake-Kurage carries out your first Plan now.
- Undertow (Common Attack, 1 energy): Deal 4 damage, already including 3 if the enemy has a debuff.
- Salt Line (Common Skill, 1 energy, Exhaust): Exhaust. Gain 8 Block.
- Battle Plan (Uncommon Skill, 1 energy): Draw 1 card. Plan: Gain 1 Energy and draw 2 cards.
- Moon's Reflection (Uncommon Skill, 1 energy, Exhaust): Exhaust. Choose a card in your Exhaust Pile. Next turn, the Bake-Kurage carries out its Plan line, or plays it if it has none.
- Tide Chart (Common Skill, 0 energy): Next turn, after the Bake-Kurage carries out its Plans, draw 1 card for each.
- Ripple (Common Skill, 0 energy): Gain 2 Block. Plan: Gain 1 Energy and 4 Block.

Note on the census: the printed Nereid's Ascension (Rare Skill, 2, Exhaust:
"Plan: for 2 turns, the Bake-Kurage carries out every Plan twice") is the
row arm 3 REPLACES; it leaves the sheet in the same commit and is not a C6
reference. The nearest standing Rare Power is The Moon Overlooks the Waters
(2: "Plans also happen now, as you write them").

## The arms

1. **Riptide** — Common Attack, 2 energy. Deal 9 damage to ALL enemies.
   Plan: Deal 13 damage to ALL enemies. Upgrade: 12 and 17.
2. **Pincer** — Common Attack, 1 energy. Deal 3 damage twice. Plan: Deal 3
   damage three times. Upgrade: 4 per hit.
3. **Nereid's Ascension, redesigned** — Rare Power, 2 energy. The
   Bake-Kurage carries out every Plan twice. Upgrade: costs 1.

Three verdicts, each with its clause and its line. Under 150 words.
```

```
1. FOLLOWS — C6 (not strictly better).
2. FOLLOWS — C6 (not strictly better).
3. FOLLOWS — C5 (nothing fires by itself); C6 (not strictly better).
```


## 5.5 The Furina pool pass, four arm-only Commons (2026-09-05, morning)

The pass packet (`review/active/furina-pool-pass-2026-09-05.md`) put four
arm-only Commons through the doctrine role on GPT 6 Astra at low effort,
each replacing one shipped Common at the same rarity through the pool seam.
The census was the shipped sheet's twenty-three Commons rendered from their
effects by a script (the shipped rows carry no prose) and the arm's ten
rows from the surface; the prompt stated that a replaced row is not a C6
reference, the lesson of the Kokomi reads (5.4). All four came back
FOLLOWS with clauses and no line. **Outcome:** four FOLLOWS; the pass
builds under `EB-493`. Prompt, then reply, verbatim:

```
# Doctrine read: four Furina arm-only Common rows against the kit charter

You are the adversarial reviewer for a Slay the Spire 2 character mod. The
owner's rule: a new or redesigned card ships to a tester only if you rule it
FOLLOWS. Each numbered card below is ONE ARM. For each, FOLLOWS or
REQUIRES_MODIFICATION, the clause you ruled against, and the line of the
card with its arithmetic in one sentence, naming the pool row or base-game
card you compared it to. Read adversarially; the author is a different
model family and the owner wants the row that should not reach a tester
named. You have no repo access; every card below is pasted from the sheet.

## Clauses

- **C1 (the owner's "not all agents always win").** A row that removes a
  losing line the kit is meant to keep, instead of pricing it, is out.
- **C2 (binding prices).** Every cost printed must bind at the moment it is
  paid; a card whose cost is routinely free is out.
- **C3 (player-controlled leverage).** The card's value must follow a
  decision the player makes (which member, when to deploy, hold Encore or
  spend it), not a state that arrives by itself.
- **C5 (nothing fires by itself).** No card triggers without a play. Under
  the arm a member performs only on a deploy, on a Companion play, on an
  Evoke, or when a kit card says she performs; nothing ticks on its own.
- **C6 (not strictly better).** A row may not be a strictly better version
  of a standing pool row (listed below) or of a base-game non-basic card at
  the same or lower rarity and cost. Strike and Defend are basics and not
  reference points. **Each arm below REPLACES one shipped Common at the same
  rarity (named on the arm); the replaced row leaves the offer under the
  arm and is not a C6 reference.** Base-game Commons for reference: Defect's
  Ball Lightning (1: 7 damage, channel a Lightning orb), Cold Snap (1: 6
  damage, channel a Frost orb), Coolheaded (1: channel Frost, draw 1),
  Claw (0: 3 damage), Sweeping Beam (1: 6 to ALL, draw 1); Ironclad's Cleave
  (1: 8 to ALL), Iron Wave (1: 5 Block, 5 damage), Twin Strike (1: 5 twice).
- **C8 (Furina reframe section 4.1).** Under the arm Fanfare is minted by a
  Salon member performing and by nothing else, 2 per trigger and 5 per
  Evoke, decaying 20% a turn; a kit card that makes a member perform mints
  the trigger amount, bounded by the kit's own declaration.

## The engine, Furina under the reframe arm

The **Salon** is a stage of three slots on her side. **Deploy** puts a named
member on stage and she **performs** once as she arrives; deploying onto a
full stage Evokes the front member to make room (automatic, front only, by
ruling). A member performs when Furina plays a **Companion card** (a card
from the companion sheets, drafted from their own reward slot; the starter's
An Invitation adds one to hand). **Evoke** makes the named member perform
with her Focus term applied three times and leave the stage; it is priced
in Encore. Members: Mademoiselle Crabaletta performs 6 Hydro damage to a
random enemy (Evoke: 14); Gentilhomme Usher performs 3 Block (Evoke: 9);
Surintendante Chevalmarin performs 2 damage and applies Hydro (Evoke: Hydro
to ALL and 3 Encore). Member numbers gain +1 per 10 Fanfare held. **Encore**
absorbs damage after Block and is the Evoke price; she starts each combat
with 2 (R258). Energy 3, HP 78. Starter: 3 Soloist's Solicitation (Attack
1: 6), 3 Stage Presence (Skill 1: 6 Block), Regal Bearing (Skill 1: 3 Block,
1 Weak), Aria of Recompense (Skill 1: 5 Encore, 5 more at 3 Fanfare), Salon
Debut (Skill 1: Deploy Mademoiselle Crabaletta), An Invitation (Skill 0,
Exhaust: add a random common Companion card to your hand).

The readings these rows answer, rounds 7 to 10: with one Deploy in the deck
(the starter's), the Salon was furniture for most of a run and most
Companion plays printed "No member on stage: performs nobody"; one dead
turn with a member idle and no legal way to make her act; Casting Call
unplayable with one Deploy; the seats asked for Deploy density, a second
Deploy shape, and the Companion-card density the stage needs.

## The standing pool, Commons pasted from the shipped sheet (offered unchanged under the arm except where an arm below replaces one)

- Casting Call (Common Power, 1 energy): apply 1 salon_cap_up to self.
- Gentilhomme Usher (Common Skill, 1 energy): deploy usher; gain 4 Block.
- Surintendante Chevalmarin (Common Skill, 1 energy): deploy chevalmarin; gain 3 Encore.
- Mademoiselle Crabaletta (Common Skill, 1 energy): deploy crabaletta.
- Dinner Service (Common Skill, 1 energy): gain 2 Block plus 2 per salon member.
- Usher the Waves (Common Attack, 1 energy): deal 5 damage to enemy; apply 1 weak to enemy.
- House Call (Common Attack, 1 energy): deal 6 damage to enemy plus 2 per salon member.
- Suffering for Art (Common Skill, 0 energy): deal 1 damage to self; gain 3 Encore.
- Lasting Impression (Common Skill, 1 energy, Exhaust): gain 4 Encore.
- Stage Combat (Common Attack, 0 energy): deal 3 damage to enemy; if enemy_intends_attack: gain 3 Block.
- Ebb and Flow (Common Skill, 1 energy, 1 Encore): gain 3 Encore; draw 1.
- Applause Line (Common Attack, 0 energy): deal 3 damage to enemy plus 1 per 4 fanfare.
- The House Holds Its Breath (Common Skill, 1 energy): gain 4 Block plus 1 per 4 fanfare.
- Breathless (Common Attack, 1 energy): spend 4 Encore; deal 9 damage to enemy.
- An Invitation (Common Skill, 0 energy, Exhaust): add a random common Companion card to your hand.
- Shared Billing (Common Skill, 1 energy): apply_aura {"element": "hydro", "target": "random_enemy"}; apply 25 spotlight_mult_bonus_turn to self; energy {"amount": 1}.
- Blocking Notes (Common Skill, 1 energy): gain 5 Block plus 2 per companion played this turn.
- Stage Lights (Common Skill, 1 energy): apply 2 spotlight_flat_damage_turn to self; apply 1 weak to all_enemies; draw 1.
- Slip Backstage (Common Skill, 1 energy): spend 5 Encore; gain 10 Block.
- Commanding Gaze (Common Skill, 1 energy): gain 2 Block; apply 1 weak to all_enemies.
- Macaron Break (Common Skill, 1 energy): gain 2 Encore; gain 2 Block.
- Compose Herself (Common Skill, 1 energy): draw 2; if encore_at_least_8: draw 1.
- Undercurrent (Common Attack, 2 energy): deal 2 damage to all_enemies x3.

## The arm's own rows, pasted from the surface

- Salon Début (Basic Skill, 1 energy): Deploy Mademoiselle Crabaletta.
- Curtain Call (Common Skill, 1 energy, 2 Encore): Evoke the front Salon member.
- Exit Stage Left (Uncommon Skill, 1 energy, 1 Encore): Evoke Surintendante Chevalmarin, or the front member if she is not on stage.
- Let the People Rejoice (Rare Attack, 2 energy): Drain your Fanfare. Deal 8 damage to ALL enemies, plus 1 per Fanfare drained.
- Intermission (Rare Skill, 1 energy): Drain your Fanfare. Gain Block equal to the Fanfare drained.
- Florid Cadenza (proto) (Uncommon Skill, 0 energy): Draw 1 card. If you have at least 6 Fanfare, draw 2 more.
- Dramatic Entrance (proto) (Uncommon Attack, 1 energy): Deal 7 damage. If you have at least 6 Fanfare, deal 7 damage to ALL enemies.
- Universal Revelry (proto) (Rare Attack, 2 energy): Deal 9 damage to ALL enemies, plus 1 per 2 Fanfare. If you have at least 8 Fanfare, deal 6 more to ALL enemies.
- Flood of Emotion (proto) (Rare Skill, 1 energy): Deal 14 damage. If you have at least 10 Fanfare, deal 14 more.
- Aria of Recompense (proto) (Basic Skill, 1 energy): Gain 5 Encore. If you have at least 3 Fanfare, gain 5 more.

## The arms

1. **Curtain Rises** — Common Attack, 1 energy; replaces House Call. Deal 6
   damage. Deploy Gentilhomme Usher. Upgrade: 9 damage.
2. **Second Course** — Common Skill, 1 energy; replaces Dinner Service.
   Spend 3 Encore. Deploy Mademoiselle Crabaletta. She performs once more.
   Upgrade: spend 2 Encore. (Unplayable below 3 Encore.)
3. **Rolling Tide** — Common Attack, 2 energy; replaces Undercurrent. Deal 2
   damage to ALL enemies twice. The front Salon member performs. Upgrade: 3
   damage.
4. **Guest List** — Common Skill, 1 energy; replaces Blocking Notes. Gain 3
   Block. Add a random common Companion card to your hand. Upgrade: 5 Block.

Four verdicts, each with its clause and its line. Under 200 words.
```

```
- **Curtain Rises — FOLLOWS.** Clause: C6.
- **Second Course — FOLLOWS.** Clauses: C2, C5, C8.
- **Rolling Tide — FOLLOWS.** Clauses: C3, C5, C8.
- **Guest List — FOLLOWS.** Clauses: C1, C6.
```


### 5.5a Correction (2026-09-05, GPT review item 2): Second Course's price

The prompt in 5.5 priced Second Course as "two performances (12 random
Hydro) for an energy and three Encore". That arithmetic came from a resolve
that never paid the printed price. In play the printed 3 is spent at the
cost line and the shipped Salon rule then charges 1 Encore per performance
or performs dry at three quarters (`SALON_TICK_ENCORE_COST`,
`SALON_DRY_DAMAGE_MULT`), so the card's full value costs five Encore: 8
damage at 3, 10 at 4, 12 at 5, the pool empty afterwards in every case,
which is the reproduction GPT reported and
`test_second_course_at_the_affordability_boundary` now pins. The verdict
(FOLLOWS on C2, C5, C8) is kept with this caveat: the corrected price binds
harder than the one the reviewer read, so no clause it weighed loosens; the
row is not re-read. The face is unchanged and the pass packet's section 2
carries the corrected arithmetic.

### 5.5b Process (2026-09-05, GPT review item 1)

`REVIEW_PROTOCOL` (`understudy/seat.py`) now requires each verdict to carry
the comparison or counterexample it rests on and calls a bare verdict
INCOMPLETE; the remedy ban is unchanged. The three bare Kokomi verdicts in
5.4 were the seat obeying the old text. The comparisons written into the
Kokomi pass packet are the author's derivations and are labelled so there.


## 5.6 Klee round 18: two card adjustments (2026-09-05, morning)

The first read under the amended protocol (a verdict carries its
comparison). Two arms from `review/active/klee-overhaul-round-18-2026-09-05.md`
§4: Grounded's condition moved from "nothing went off" to "a Bomb is on the
field", and a random Set off preferring a bombed enemy (Tinder Toss, Rapid
Fire). Both FOLLOWS, each with the standing line, the adjusted line and the
turn on which the adjustment is worse for the player, which is what the
protocol now asks. **Outcome:** both build under `EB-516`. Prompt, then
reply, verbatim:

```
# Doctrine read: two Klee card adjustments from round 18

Each numbered arm below is ONE ARM: an ADJUSTMENT to a row that stands on the
sheet, with the standing text and the adjusted text both printed. For each,
FOLLOWS or REQUIRES_MODIFICATION, the clause you ruled against, and the
comparison the verdict rests on: the standing row's line against the adjusted
line with the numbers, and the turn on which the adjustment is better or worse
for the player. Read adversarially; the author is a different model family.
The comparison is reading; a remedy is not, and none is asked for.

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
an Attack). Each Bomb grows separately. A **Mine** also goes off when its
enemy attacks her, before the hit. **Spark**: she starts each combat with 1,
gains 1 per Bomb going off (the relic, Pounding Surprise), and cards that
print a Spark price spend Sparks instead of energy; no cap, lost at the end
of combat. Energy 3, HP 62. Starter: 4 Strike, 4 Defend, Ka-pow! (basic, 0,
Retain: Set off, 4 damage), Jumpy Dumpty (basic, 1: Bomb 8; when it goes
off, a Mine 3 on ALL enemies).

## What two rounds of seats said, verbatim

Round 17, assembled Cook deck: "Grounded and the whole Bomb archetype are at
war: it pays Sparks only while no Bomb goes off, and Sparks exist to set
Bombs off." Round 18, assembled Cook deck, Sparks logged every turn: "Grounded
is a trap in its own deck. 'If none of your Bombs went off last turn' pays you
for skipping the kit's entire loop. In five fights it triggered once, and
that was a turn I had already conceded." The ledger: something went off on
10 of 19 turns of a Cook deck, seven of them a Mine on the enemy's beat.
Round 17 natural: "Rapid Fire never once earned 2 energy: 'Set off a random
enemy' means it cannot be pointed at the body I have spent two cards
bombing." Round 18 Spray: "Tinder Toss is the one I never wanted: every other
Spark card lets me aim at a bomb and get the Spark back; Tinder Toss gambles
that, and when it loses the next card in hand prints CANNOT BE PLAYED."

## The pool, every row pasted from the sheet (rarity, type, price)

- Ka-pow! (Basic Attack, 0 energy, Retain): Set off. Deal 4 damage.
- Jumpy Dumpty (Basic Skill, 1 energy): Place a Bomb 8. When it goes off, place a Mine 3 on ALL enemies.
- Fish-Flavored Bait (Common Attack, 1 energy): Deal 4 damage. Place a Bomb 4.
- Pocket Fireworks (Common Attack, 1 energy): Deal 9 damage.
- Chain Fuse (Common Skill, 1 energy): Each Bomb on the enemy grows by 6.
- Explosives Workshop (Uncommon Power, 1 energy): At the start of your turn, your Bombs grow by 1 more.
- Careful Arrangement (Uncommon Skill, 1 energy): Move all your Bombs onto the enemy as one Bomb. It grows by 5.
- Big Badda Boom (Uncommon Attack, 2 energy): Set off. Deal 12 damage. Then deal damage equal to what the Bombs dealt.
- The Big One (Rare Attack, 3 energy): Set off for quadruple damage.
- Alice's Recipe (Rare Power, 2 energy): Your Bombs grow twice each turn.
- Pop! (Common Skill, 0 energy): Place a Bomb 5.
- Mine Toss (Common Skill, 1 energy): Place a Mine 4 on ALL enemies.
- Fwoosh! (Common Attack, 0 energy, 1 Spark): Set off. Deal 6 damage.
- Tinder Toss (Common Attack, 0 energy, 1 Spark): Set off a random enemy and deal 4 damage to it, twice.
- Quick Fuse (Common Skill, 0 energy, 1 Spark): Each Bomb on the enemy grows by 3. Set off.
- Bang Bang! (Uncommon Attack, 0 energy, 2 Spark): Set off. Deal 8 damage. Place a Bomb 4.
- Rapid Fire (Uncommon Attack, 2 energy): Set off a random enemy and deal 3 damage to it, 4 times.
- Chained Reactions (Rare Power, 1 energy): Whenever one of your Bombs goes off, place a Bomb 3 on a random enemy.
- Sparks 'n' Splash (proto) (Rare Power, 2 energy): At the end of your turn, deal Pyro damage to a random enemy equal to its largest Bomb.
- Sizzle (Common Attack, 1 energy): Set off. Deal 6 damage. If a Bomb triggered an Elemental Reaction this turn, deal 6 additional damage.
- Perfect Timing (Uncommon Attack, 1 energy): Set off. Deal 8 damage. If a Bomb triggered an Elemental Reaction this turn, play this again.
- Flame Dance (Uncommon Attack, 1 energy): Set off each enemy whose aura is not Pyro. Deal 5 damage to ALL enemies.
- Catalytic Converter (Uncommon Power, 1 energy): Whenever one of your Bombs triggers an Elemental Reaction, gain 1 additional Spark.
- Ammo Scavenging (Common Skill, 1 energy): Place a Bomb 4. Draw 1 card for each of your Bombs that went off this turn.
- Powder Charge (Uncommon Skill, 0 energy, 1 Spark): Place a Bomb 6.
- Dig In (Common Skill, 0 energy, 1 Spark): Gain 8 Block.
- Sugar Rush (Rare Skill, 0 energy, 2 Spark, Exhaust): Gain 2 Energy. Draw 1 card. Exhaust.
- Run Away! (Common Skill, 0 energy): Gain 3 Block. If a Bomb went off this turn, gain 4 additional Block.
- Grounded (Uncommon Power, 1 energy): At the start of your turn, if none of your Bombs went off last turn, gain 6 Block and 1 Spark.
- Sorry, Jean... (Common Skill, 0 energy): Remove one of your Bombs. Gain Block equal to its size.
- Dodoco Cover (Common Skill, 1 energy): Place a Bomb 4. Gain 5 Block.
- Careful Now (Uncommon Skill, 1 energy, Retain): Gain Block equal to your largest Bomb when played, up to 10.
- Coven Errand (Common Skill, 1 energy): Place a Bomb 5. If you played a Hexerei card this turn, place it on ALL enemies instead.
- Witches' Circle (Uncommon Power, 1 energy): Whenever you play a Hexerei card, place a Bomb 3 on a random enemy.
- Alice's Introduction Magic (Rare Skill, 1 energy): All cards in your hand count as Hexerei cards this turn.
- Countdown (Common Skill, 1 energy): Set off. Draw 1 card1.
- Stoke the Fuse (Uncommon Skill, 0 energy, all Spark): Spend all your Sparks. Your largest Bomb grows by 3 per Spark spent.
- Long Fuse (Common Attack, 1 energy, Retain): Set off. Deal 6 damage. Costs 1 more each turn it stays in your hand.
- All of My Treasures! (proto) (Rare Skill, 1 energy, Exhaust): Place a Bomb on the enemy equal to your largest Bomb.
- Fish Blasting (proto) (Common Attack, 1 energy): Deal 5 damage to ALL enemies. Add a Confiscated to your draw pile.
- Pocket Match (Common Attack, 0 energy, 1 Spark, Retain): Set off. Deal 5 damage.
- Bombs Away! (proto) (Common Attack, 1 energy): Deal 3 damage to ALL enemies. Place a Bomb 2 on ALL enemies.
- Fireworks Show (Uncommon Skill, 0 energy, 2 Spark): Set off ALL enemies.
- Kindling (Common Skill, 0 energy): Each Bomb on an enemy whose aura is not Pyro grows by 4. If there is none, your largest Bomb grows by 1.
- Flash Point (Uncommon Attack, 1 energy): Set off. Deal 7 damage. If a Bomb triggered an Elemental Reaction this turn, gain 1 Spark and draw 1 card.
- Vermillion Pact (proto) (Rare Power, 2 energy): Whenever one of your Bombs triggers an Elemental Reaction, the Attack that set it off triggers one too.
- Split Charge (Uncommon Skill, 1 energy): Split your largest Bomb into two halves on random enemies.1

## The arms

1. **Grounded, adjusted** (Uncommon Power, 1 energy). Standing: "At the start
   of your turn, if none of your Bombs went off last turn, gain 6 Block and 1
   Spark." Adjusted: "At the start of your turn, if you have a Bomb on the
   field, gain 6 Block and 1 Spark." Upgrade unchanged (8 Block). The
   condition moves from "nothing was cashed" to "something is cooking"; it
   still pays nothing on a turn with an empty board, so it stays conditional
   (C4) and it stops paying the player for not playing the kit.
2. **A random Set off aims a bombed body first** (a rule on Tinder Toss and
   Rapid Fire, no face text change beyond the tip): "Set off a random enemy"
   picks among enemies carrying a Bomb; if none carries one, any enemy.
   Tinder Toss (Common Attack, 0, 1 Spark: Set off a random enemy and deal 4
   damage to it, twice) and Rapid Fire (Uncommon Attack, 2: Set off a random
   enemy and deal 3 damage to it, 4 times) keep their numbers.

Two verdicts, each with its clause and its comparison. Under 200 words.
```

```
1. **FOLLOWS — C2, C3, C4, C6.** Standing Grounded: **1 energy; 6 Block + 1 Spark** if no Bomb went off last turn. Adjusted: **1 energy; 6 Block + 1 Spark** if a Bomb remains. On turn 2 with an empty field and no turn-1 detonation, adjusted yields **0 Block, 0 Spark**, losing **6 Block and 1 Spark** against standing; retaining a Bomb enables its benefit but postpones cashing that Bomb.

2. **FOLLOWS — C1, C2, C6.** Standing and adjusted Tinder Toss both cost **1 Spark** for **4 damage twice**; Rapid Fire both cost **2 energy** for **3 damage four times**. With two enemies—one bombed and healthy, the other unbombed and attacking at **4 HP** (Tinder) or **3 HP** (Rapid)—the adjustment reduces the first hit’s chance of killing the attacker from **½ to 0**: that turn’s first hit delivers **4 or 3 less damage** to the urgent target. Guaranteed access to a Bomb therefore carries a targeting disadvantage; it does not dominate the standing rule.
```


## 5.7 Furina round 12: two card adjustments (2026-09-05, morning)

Two arms from `review/active/furina-reframe-round-12-2026-09-05.md` §4:
Rolling Tide at 1 energy, and Curtain Rises fielding Chevalmarin instead of
the Usher. Both FOLLOWS with comparisons. The reviewer also caught an error
in the prompt: the arm said Undercurrent costs 1 energy; the census pasted
below it says 2, and the census is right (the shipped Undercurrent is a
2-cost Attack). The verdict rested on Cleave and on the replaced-row rule,
not on that line, so it stands; the packet's own arithmetic is corrected.
**Outcome:** both build under `EB-530`. Prompt, then reply, verbatim:

```
# Doctrine read: two Furina card adjustments from round 12

Each numbered arm below is ONE ARM: an ADJUSTMENT to an arm-only row that
stands on the surface, with the standing text and the adjusted text both
printed. For each, FOLLOWS or REQUIRES_MODIFICATION, the clause you ruled
against, and the comparison the verdict rests on: the standing row's line
against the adjusted line with the numbers, and the turn on which the
adjustment is better or worse for the player. Read adversarially; the author
is a different model family. The comparison is reading; a remedy is not, and
none is asked for.

## Clauses

- **C1 (the owner's "not all agents always win").** A row that removes a
  losing line the kit is meant to keep, instead of pricing it, is out.
- **C2 (binding prices).** Every cost printed must bind at the moment it is
  paid; a card whose cost is routinely free is out.
- **C3 (player-controlled leverage).** The card's value must follow a
  decision the player makes (which member, when to deploy, hold Encore or
  spend it), not a state that arrives by itself.
- **C5 (nothing fires by itself).** No card triggers without a play. Under
  the arm a member performs only on a deploy, on a Companion play, on an
  Evoke, or when a kit card says she performs; nothing ticks on its own.
- **C6 (not strictly better).** A row may not be a strictly better version
  of a standing pool row (listed below) or of a base-game non-basic card at
  the same or lower rarity and cost. Strike and Defend are basics and not
  reference points. **Each arm below REPLACES one shipped Common at the same
  rarity (named on the arm); the replaced row leaves the offer under the
  arm and is not a C6 reference.** Base-game Commons for reference: Defect's
  Ball Lightning (1: 7 damage, channel a Lightning orb), Cold Snap (1: 6
  damage, channel a Frost orb), Coolheaded (1: channel Frost, draw 1),
  Claw (0: 3 damage), Sweeping Beam (1: 6 to ALL, draw 1); Ironclad's Cleave
  (1: 8 to ALL), Iron Wave (1: 5 Block, 5 damage), Twin Strike (1: 5 twice).
- **C8 (Furina reframe section 4.1).** Under the arm Fanfare is minted by a
  Salon member performing and by nothing else, 2 per trigger and 5 per
  Evoke, decaying 20% a turn; a kit card that makes a member perform mints
  the trigger amount, bounded by the kit's own declaration.

## The engine, Furina under the reframe arm

The **Salon** is a stage of three slots on her side. **Deploy** puts a named
member on stage and she **performs** once as she arrives; deploying onto a
full stage Evokes the front member to make room (automatic, front only, by
ruling). A member performs when Furina plays a **Companion card** (a card
from the companion sheets, drafted from their own reward slot; the starter's
An Invitation adds one to hand). **Evoke** makes the named member perform
with her Focus term applied three times and leave the stage; it is priced
in Encore. Members: Mademoiselle Crabaletta performs 6 Hydro damage to a
random enemy (Evoke: 14); Gentilhomme Usher performs 3 Block (Evoke: 9);
Surintendante Chevalmarin performs 2 damage and applies Hydro (Evoke: Hydro
to ALL and 3 Encore). Member numbers gain +1 per 10 Fanfare held. **Encore**
absorbs damage after Block and is the Evoke price; she starts each combat
with 2 (R258). Energy 3, HP 78. Starter: 3 Soloist's Solicitation (Attack
1: 6), 3 Stage Presence (Skill 1: 6 Block), Regal Bearing (Skill 1: 3 Block,
1 Weak), Aria of Recompense (Skill 1: 5 Encore, 5 more at 3 Fanfare), Salon
Debut (Skill 1: Deploy Mademoiselle Crabaletta), An Invitation (Skill 0,
Exhaust: add a random common Companion card to your hand).

The readings that led to the pass (rounds 7 to 10): with one Deploy in the deck
(the starter's), the Salon was furniture for most of a run and most
Companion plays printed "No member on stage: performs nobody"; one dead
turn with a member idle and no legal way to make her act; Casting Call
unplayable with one Deploy; the seats asked for Deploy density, a second
Deploy shape, and the Companion-card density the stage needs.

## The standing pool, Commons pasted from the shipped sheet (offered unchanged under the arm except where an arm below replaces one)

- Casting Call (Common Power, 1 energy): apply 1 salon_cap_up to self.
- Gentilhomme Usher (Common Skill, 1 energy): deploy usher; gain 4 Block.
- Surintendante Chevalmarin (Common Skill, 1 energy): deploy chevalmarin; gain 3 Encore.
- Mademoiselle Crabaletta (Common Skill, 1 energy): deploy crabaletta.
- Dinner Service (Common Skill, 1 energy): gain 2 Block plus 2 per salon member.
- Usher the Waves (Common Attack, 1 energy): deal 5 damage to enemy; apply 1 weak to enemy.
- House Call (Common Attack, 1 energy): deal 6 damage to enemy plus 2 per salon member.
- Suffering for Art (Common Skill, 0 energy): deal 1 damage to self; gain 3 Encore.
- Lasting Impression (Common Skill, 1 energy, Exhaust): gain 4 Encore.
- Stage Combat (Common Attack, 0 energy): deal 3 damage to enemy; if enemy_intends_attack: gain 3 Block.
- Ebb and Flow (Common Skill, 1 energy, 1 Encore): gain 3 Encore; draw 1.
- Applause Line (Common Attack, 0 energy): deal 3 damage to enemy plus 1 per 4 fanfare.
- The House Holds Its Breath (Common Skill, 1 energy): gain 4 Block plus 1 per 4 fanfare.
- Breathless (Common Attack, 1 energy): spend 4 Encore; deal 9 damage to enemy.
- An Invitation (Common Skill, 0 energy, Exhaust): add a random common Companion card to your hand.
- Shared Billing (Common Skill, 1 energy): apply_aura {"element": "hydro", "target": "random_enemy"}; apply 25 spotlight_mult_bonus_turn to self; energy {"amount": 1}.
- Blocking Notes (Common Skill, 1 energy): gain 5 Block plus 2 per companion played this turn.
- Stage Lights (Common Skill, 1 energy): apply 2 spotlight_flat_damage_turn to self; apply 1 weak to all_enemies; draw 1.
- Slip Backstage (Common Skill, 1 energy): spend 5 Encore; gain 10 Block.
- Commanding Gaze (Common Skill, 1 energy): gain 2 Block; apply 1 weak to all_enemies.
- Macaron Break (Common Skill, 1 energy): gain 2 Encore; gain 2 Block.
- Compose Herself (Common Skill, 1 energy): draw 2; if encore_at_least_8: draw 1.
- Undercurrent (Common Attack, 2 energy): deal 2 damage to all_enemies x3.

## The arm's own rows, pasted from the surface

- Salon Début (Basic Skill, 1 energy): Deploy Mademoiselle Crabaletta.
- Curtain Call (Common Skill, 1 energy, 2 Encore): Evoke the front Salon member.
- Exit Stage Left (Uncommon Skill, 1 energy, 1 Encore): Evoke Surintendante Chevalmarin, or the front member if she is not on stage.
- Let the People Rejoice (Rare Attack, 2 energy): Drain your Fanfare. Deal 8 damage to ALL enemies, plus 1 per Fanfare drained.
- Intermission (Rare Skill, 1 energy): Drain your Fanfare. Gain Block equal to the Fanfare drained.
- Florid Cadenza (proto) (Uncommon Skill, 0 energy): Draw 1 card. If you have at least 6 Fanfare, draw 2 more.
- Dramatic Entrance (proto) (Uncommon Attack, 1 energy): Deal 7 damage. If you have at least 6 Fanfare, deal 7 damage to ALL enemies.
- Universal Revelry (proto) (Rare Attack, 2 energy): Deal 9 damage to ALL enemies, plus 1 per 2 Fanfare. If you have at least 8 Fanfare, deal 6 more to ALL enemies.
- Flood of Emotion (proto) (Rare Skill, 1 energy): Deal 14 damage. If you have at least 10 Fanfare, deal 14 more.
- Aria of Recompense (proto) (Basic Skill, 1 energy): Gain 5 Encore. If you have at least 3 Fanfare, gain 5 more.

## What two rounds of seats said, verbatim

Rolling Tide (2 energy: 2 to ALL twice, the front member performs). Round 11
assembled: "never played, drawn in four of six fights and rejected every
time; 2 energy for 4 damage per body, the worst rate in the deck." Round 12
assembled, asked to log every hand holding it: "6 hands, played 2, held 4;
filler at 2 energy against single targets; at 1 energy I'd have played it in
4 of 6 and it would be a staple." Round 12 natural, offered it: "did not want
it at 2 energy, less than Chevreuse for the same cost; would take it at 1."

Curtain Rises (1 energy: 6 damage, Deploy Gentilhomme Usher). Round 11
natural: "a draft trap with no warning: it reads as an Attack but puts a
Block member into the rotation, so on a stacked stage only the first
Companion card each turn reaches your damage member and the rest give 3
Block." Round 12 assembled: "held 4 times because the Usher it fields is a
Block member who then holds the front." Round 12 natural: "the card I never
wanted to play, because it puts the Usher at the front and converts the
damage engine into a block engine; Gentilhomme Usher is below a basic
Defend (3 Block a trigger, 2 dry)."

## The arms

1. **Rolling Tide, adjusted** (Common Attack, replaces Undercurrent). Standing:
   2 energy, "Deal 2 damage to ALL enemies twice. The front Salon member
   performs." Adjusted: **1 energy**, same text, upgrade unchanged (3 damage).
   Against Undercurrent (1 energy: 2 to ALL three times, no performance): one
   hit fewer for a performance, at the same price.
2. **Curtain Rises, adjusted** (Common Attack, replaces House Call). Standing:
   1 energy, "Deal 6 damage. Deploy Gentilhomme Usher." Adjusted: 1 energy,
   "Deal 6 damage. **Deploy Surintendante Chevalmarin.**" Upgrade unchanged (9
   damage). Chevalmarin performs 2 damage and applies Hydro as she arrives
   (Usher: 3 Block); a deploy that fields an applier on an Attack. Against
   the shipped Surintendante Chevalmarin (Common Skill, 1: deploy her, gain 3
   Encore): 6 damage in place of 3 Encore.

Two verdicts, each with its clause and its comparison. Under 200 words.
```

```
1. **FOLLOWS — C2, C6.** Standing Rolling Tide costs 2 energy for 2 damage to ALL twice plus one front-member performance; adjusted costs 1 for the identical effects. On the turn played, it saves 1 energy; the remaining energy cost binds. Against Cleave (Common, 1 energy: 8 to ALL), adjusted Tide deals 4 to ALL: with an empty Salon, it is worse by 4 damage per enemy that turn. Its performance benefit depends on stage composition. The shipped pool lists Undercurrent at **2 energy**, contradicting the arm’s comparison; Undercurrent is excluded as the replaced row.

2. **FOLLOWS — C6.** Standing Curtain Rises costs 1 energy for 6 damage and Usher’s deploy performance of 3 Block; adjusted costs 1 for 6 damage and Chevalmarin’s 2 damage plus Hydro. At zero Fanfare, the adjustment adds 2 damage and Hydro but loses 3 Block that turn, exchanging defensive value for offense. Against shipped Surintendante Chevalmarin (Common, 1 energy: deploy her, gain 3 Encore), both deploy the same member; adjusted Curtain Rises gains 6 damage but loses 3 Encore that turn. Neither comparison establishes strict superiority.
```


## 5.8 Furina round 13: Second Course at a printed price of 1 (2026-09-05, afternoon)

One arm from `review/active/furina-reframe-round-13-2026-09-05.md` §4:
Second Course's printed Encore price from 3 to 1 (full value 3 with the
shipped per-performance drain instead of 5), after three rounds in which
it was unplayable at the opening Encore of 2. FOLLOWS on C2 and C6 with the
comparison (turn one at 2 Encore: standing unplayable, adjusted 6 + 4 for
all the Encore; against the shipped Mademoiselle Crabaletta, 4 more damage
for the last Encore). **Outcome:** builds under `EB-552`, with Rolling
Tide's withdrawal from the arm's offer (a D default, no read needed: a row
leaving the arm is not a card reaching a tester) and Aria+ dropping Innate
(`EB-550`, a D default on the upgrade). Prompt, then reply, verbatim:

```
# Doctrine read: one Furina card adjustment from round 13

The numbered arm below is ONE ARM: an ADJUSTMENT to an arm-only row that
stands on the surface, with the standing text and the adjusted text both
printed. FOLLOWS or REQUIRES_MODIFICATION, the clause you ruled against, and
the comparison the verdict rests on: the standing row's line against the
adjusted line with the numbers, and the turn on which the adjustment is
better or worse for the player. Read adversarially; the author is a
different model family. The comparison is reading; a remedy is not, and none
is asked for.

## Clauses

- **C1 (the owner's "not all agents always win").** A row that removes a
  losing line the kit is meant to keep, instead of pricing it, is out.
- **C2 (binding prices).** Every cost printed must bind at the moment it is
  paid; a card whose cost is routinely free is out.
- **C3 (player-controlled leverage).** The card's value must follow a
  decision the player makes (which member, when to deploy, hold Encore or
  spend it), not a state that arrives by itself.
- **C5 (nothing fires by itself).** No card triggers without a play. Under
  the arm a member performs only on a deploy, on a Companion play, on an
  Evoke, or when a kit card says she performs; nothing ticks on its own.
- **C6 (not strictly better).** A row may not be a strictly better version
  of a standing pool row (listed below) or of a base-game non-basic card at
  the same or lower rarity and cost. Strike and Defend are basics and not
  reference points. **Each arm below REPLACES one shipped Common at the same
  rarity (named on the arm); the replaced row leaves the offer under the
  arm and is not a C6 reference.** Base-game Commons for reference: Defect's
  Ball Lightning (1: 7 damage, channel a Lightning orb), Cold Snap (1: 6
  damage, channel a Frost orb), Coolheaded (1: channel Frost, draw 1),
  Claw (0: 3 damage), Sweeping Beam (1: 6 to ALL, draw 1); Ironclad's Cleave
  (1: 8 to ALL), Iron Wave (1: 5 Block, 5 damage), Twin Strike (1: 5 twice).
- **C8 (Furina reframe section 4.1).** Under the arm Fanfare is minted by a
  Salon member performing and by nothing else, 2 per trigger and 5 per
  Evoke, decaying 20% a turn; a kit card that makes a member perform mints
  the trigger amount, bounded by the kit's own declaration.

## The engine, Furina under the reframe arm

The **Salon** is a stage of three slots on her side. **Deploy** puts a named
member on stage and she **performs** once as she arrives; deploying onto a
full stage Evokes the front member to make room (automatic, front only, by
ruling). A member performs when Furina plays a **Companion card** (a card
from the companion sheets, drafted from their own reward slot; the starter's
An Invitation adds one to hand). **Evoke** makes the named member perform
with her Focus term applied three times and leave the stage; it is priced
in Encore. Members: Mademoiselle Crabaletta performs 6 Hydro damage to a
random enemy (Evoke: 14); Gentilhomme Usher performs 3 Block (Evoke: 9);
Surintendante Chevalmarin performs 2 damage and applies Hydro (Evoke: Hydro
to ALL and 3 Encore). Member numbers gain +1 per 10 Fanfare held. **Encore**
absorbs damage after Block and is the Evoke price; she starts each combat
with 2 (R258). Energy 3, HP 78. Starter: 3 Soloist's Solicitation (Attack
1: 6), 3 Stage Presence (Skill 1: 6 Block), Regal Bearing (Skill 1: 3 Block,
1 Weak), Aria of Recompense (Skill 1: 5 Encore, 5 more at 3 Fanfare), Salon
Debut (Skill 1: Deploy Mademoiselle Crabaletta), An Invitation (Skill 0,
Exhaust: add a random common Companion card to your hand).

The readings that led to the pass (rounds 7 to 10): with one Deploy in the deck
(the starter's), the Salon was furniture for most of a run and most
Companion plays printed "No member on stage: performs nobody"; one dead
turn with a member idle and no legal way to make her act; Casting Call
unplayable with one Deploy; the seats asked for Deploy density, a second
Deploy shape, and the Companion-card density the stage needs.

## The standing pool, Commons pasted from the shipped sheet (offered unchanged under the arm except where an arm below replaces one)

- Casting Call (Common Power, 1 energy): apply 1 salon_cap_up to self.
- Gentilhomme Usher (Common Skill, 1 energy): deploy usher; gain 4 Block.
- Surintendante Chevalmarin (Common Skill, 1 energy): deploy chevalmarin; gain 3 Encore.
- Mademoiselle Crabaletta (Common Skill, 1 energy): deploy crabaletta.
- Dinner Service (Common Skill, 1 energy): gain 2 Block plus 2 per salon member.
- Usher the Waves (Common Attack, 1 energy): deal 5 damage to enemy; apply 1 weak to enemy.
- House Call (Common Attack, 1 energy): deal 6 damage to enemy plus 2 per salon member.
- Suffering for Art (Common Skill, 0 energy): deal 1 damage to self; gain 3 Encore.
- Lasting Impression (Common Skill, 1 energy, Exhaust): gain 4 Encore.
- Stage Combat (Common Attack, 0 energy): deal 3 damage to enemy; if enemy_intends_attack: gain 3 Block.
- Ebb and Flow (Common Skill, 1 energy, 1 Encore): gain 3 Encore; draw 1.
- Applause Line (Common Attack, 0 energy): deal 3 damage to enemy plus 1 per 4 fanfare.
- The House Holds Its Breath (Common Skill, 1 energy): gain 4 Block plus 1 per 4 fanfare.
- Breathless (Common Attack, 1 energy): spend 4 Encore; deal 9 damage to enemy.
- An Invitation (Common Skill, 0 energy, Exhaust): add a random common Companion card to your hand.
- Shared Billing (Common Skill, 1 energy): apply_aura {"element": "hydro", "target": "random_enemy"}; apply 25 spotlight_mult_bonus_turn to self; energy {"amount": 1}.
- Blocking Notes (Common Skill, 1 energy): gain 5 Block plus 2 per companion played this turn.
- Stage Lights (Common Skill, 1 energy): apply 2 spotlight_flat_damage_turn to self; apply 1 weak to all_enemies; draw 1.
- Slip Backstage (Common Skill, 1 energy): spend 5 Encore; gain 10 Block.
- Commanding Gaze (Common Skill, 1 energy): gain 2 Block; apply 1 weak to all_enemies.
- Macaron Break (Common Skill, 1 energy): gain 2 Encore; gain 2 Block.
- Compose Herself (Common Skill, 1 energy): draw 2; if encore_at_least_8: draw 1.
- Undercurrent (Common Attack, 2 energy): deal 2 damage to all_enemies x3.

## The arm's own rows, pasted from the surface

- Salon Début (Basic Skill, 1 energy): Deploy Mademoiselle Crabaletta.
- Curtain Call (Common Skill, 1 energy, 2 Encore): Evoke the front Salon member.
- Exit Stage Left (Uncommon Skill, 1 energy, 1 Encore): Evoke Surintendante Chevalmarin, or the front member if she is not on stage.
- Let the People Rejoice (Rare Attack, 2 energy): Drain your Fanfare. Deal 8 damage to ALL enemies, plus 1 per Fanfare drained.
- Intermission (Rare Skill, 1 energy): Drain your Fanfare. Gain Block equal to the Fanfare drained.
- Florid Cadenza (proto) (Uncommon Skill, 0 energy): Draw 1 card. If you have at least 6 Fanfare, draw 2 more.
- Dramatic Entrance (proto) (Uncommon Attack, 1 energy): Deal 7 damage. If you have at least 6 Fanfare, deal 7 damage to ALL enemies.
- Universal Revelry (proto) (Rare Attack, 2 energy): Deal 9 damage to ALL enemies, plus 1 per 2 Fanfare. If you have at least 8 Fanfare, deal 6 more to ALL enemies.
- Flood of Emotion (proto) (Rare Skill, 1 energy): Deal 14 damage. If you have at least 10 Fanfare, deal 14 more.
- Aria of Recompense (proto) (Basic Skill, 1 energy): Gain 5 Encore. If you have at least 3 Fanfare, gain 5 more.

## The rule behind the price, and what three rounds of seats said

Under the arm every member performance spends 1 Encore, or performs at
three quarters if the pool is empty (the shipped Salon rule, printed on the
member tips). She opens every combat with 2 Encore (R258). Second Course's
printed price is on top of that drain, so its full value costs the printed
price plus 2.

Round 11 assembled (printed price 3): "locked out three separate times at
Encore 2; strictly an after-Aria card, it never once was castable off the
fight's opening Encore of 2." Round 12 assembled: "it is unplayable on turn
1 of every fight, which leaves only two reliable Deploys"; two plays logged
10 to 5 Encore for 6 and 6, and 4 to 0 for 6 and 4 dry. Round 13 assembled:
"never once playable: four appearances, four CANNOT BE PLAYED: you have no
Encore, and this costs 3." The stage was empty on turn one of every fight
in all three rounds.

## The arm

1. **Second Course, adjusted** (Common Skill, 1 energy, replaces Dinner
   Service). Standing: "Spend 3 Encore. Deploy Mademoiselle Crabaletta. She
   performs once more." (upgrade: spend 2). Adjusted: **"Spend 1 Encore.
   Deploy Mademoiselle Crabaletta. She performs once more."** (upgrade: spend
   0). Everything else unchanged. With the drain, the full-value cost becomes
   3 Encore (1 printed, 2 performances) instead of 5; at the opening 2 Encore
   it is playable, pays 1, and performs once paid (6) and once dry (4). Against
   the shipped Mademoiselle Crabaletta (Common Skill, 1: deploy her, which
   performs once, 1 Encore by the drain): one more Encore for one more
   performance.

One verdict, its clause and its comparison. Under 120 words.
```

```
1. **FOLLOWS — C2 (binding prices), C6 (not strictly better).** Standing Second Course costs 1 energy + 3 printed Encore, 5 including both performances; adjusted costs 1 energy + 1 printed Encore, 3 including both performances. On turn 1 with an empty stage and 2 Encore, standing is unplayable; adjusted deals 6 + 4 = 10 damage and leaves 0 Encore. Shipped Mademoiselle Crabaletta costs 1 energy, deals 6 on deploy, and leaves 1 Encore: adjusted gains 4 immediate damage but sacrifices that remaining Encore, so its advantage has a binding price.
```

## 5.9 Kokomi round 20: The Moon Overlooks the Waters, two readings, withdrawn (2026-09-05, night)

One arm from `review/active/kokomi-overhaul-round-20-2026-09-05.md` §4
item 1, read at the door twice. First reading: the now-copy at half.
**REQUIRES_MODIFICATION on C1**, with the Battle Plan counterexample (play
draws 1; Plan gains 1 Energy and draws 2; at half the now-copy still draws
1, so writing matches playing this turn and adds the morning). Second
reading: a one-turn Exhaust Skill ("This turn, Plans also happen now"),
asked plainly whether a one-turn window is C1's concern. **REQUIRES_MODIFICATION
on C1 again**: removing waiting's price for one turn still removes the
losing line on that turn. The author agrees: the card's concept ("Plans
also happen now") cannot survive C1 in any duration once a Plan line is
double its play line. **Outcome:** withdrawn from the arm's offer as Rolling
Tide was (`EB-570`, D default; the row and its upgrade deleted with their
pins under R213 B); Nereid's Ascension stays the one rule-breaking Rare.
First prompt, then its reply, then the second prompt's arm and its reply,
verbatim:

```
# Doctrine read: one Kokomi card adjustment from round 20

The one numbered arm below is an ADJUSTMENT to a row that stands on the
sheet, with the standing text and the adjusted text both printed. FOLLOWS
or REQUIRES_MODIFICATION, the clause you ruled against, and the comparison
the verdict rests on: the standing row's line against the adjusted line
with the numbers, and the turn on which the adjustment is better or worse
for the player. Read adversarially; the author is a different model family.
The comparison is reading; a remedy is not, and none is asked for.

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

## The engine, Kokomi

The **Bake-Kurage** is on her side of the field for the whole combat; it
is not a fighter and enemies cannot touch it. Some cards carry a **Plan:**
line: what the jellyfish does at the start of her next turn, before she
draws, if the card is played on the jellyfish instead of where it would
normally go. The cost is paid now either way; a planned card leaves the
hand like any played card. A planned Attack strikes the front enemy; a
planned Skill acts on her; Plans are carried out in the order written, once
each; her Strength and Dexterity count. Nothing happens by itself. The
brief's decision (section 3): "Every Plan card in hand asks the same
question: now, or next turn for more. The enemy's intent this turn is the
price of waiting." The one sanctioned rule-breaking Rare is Nereid's
Ascension (Power, 2: the jellyfish carries out every Plan twice), which
breaks "once, in order". Energy 3, HP 80.

## What the seats said, verbatim

Round 17, assembled: "Battle Plan under the Moon refunds itself, the best
of the six." Round 20, natural, after Moon+ from an event: "writing is never
worse than playing, so the tension the kit is built on stops being asked;
the strongest card I drew and the one that flattened my turns."

## The pool, every row pasted from the sheet (rarity, type, price)

- Kurage's Oath (proto) (Basic Skill, 1 energy): Deal 3 damage to ALL enemies. Plan: Deal 7 damage to ALL enemies.
- Slack Water (proto) (Basic Attack, 1 energy): Deal 4 damage. Apply 1 Weak. Plan: Apply 1 Weak to ALL enemies.
- Feint (Common Attack, 1 energy): Deal 6 damage. Plan: Deal 10 damage.
- Ambush (Common Skill, 1 energy): Deal 5 damage. Plan: Deal 12 damage.
- Read the Field (Common Skill, 1 energy): Gain 5 Block. Plan: Gain 10 Block.
- Exposed Flank (Common Skill, 1 energy): Apply 1 Vulnerable. Plan: Apply 2 Vulnerable to ALL enemies.
- Treatise (Uncommon Power, 1 energy): Once per turn, when the Bake-Kurage carries out a Plan, draw 1 card.
- Song of Pearls (proto) (Uncommon Power, 1 energy): Once per turn, when the Bake-Kurage carries out a Plan, gain 3 Block.
- War Council (Uncommon Skill, 1 energy): Apply 1 Weak to ALL enemies. Plan: Deal 5 damage and apply 1 Weak to ALL enemies.
- Nereid's Ascension (proto) (Rare Power, 2 energy): At the start of your turn, the Bake-Kurage carries out every Plan twice.
- The Moon Overlooks the Waters (Rare Power, 2 energy): Plans also happen now, as you write them.
- Sea-Salt Prayer (Common Skill, 1 energy): Gain 4 Block. Apply 1 Weak.
- Deep Current (Common Attack, 1 energy): Deal 6 damage to ALL enemies.
- Coral Bulwark (Common Skill, 1 energy): Gain 6 Block. Plan: Gain 8 Block and apply 1 Weak.
- Cleansing Wave (Uncommon Skill, 1 energy): Gain 5 Block. Remove one of your debuffs. Plan: Gain 10 Block.
- Tide Wall (Uncommon Skill, 1 energy): Gain 4 Block. Plan: Gain 3 Block for each Plan the Bake-Kurage carries out this morning.
- Shell Guard (Uncommon Skill, 1 energy): Gain 5 Block. Until your next turn, whenever the Tamakushi Casket strikes, gain 3 Block.
- The Clouds Like Waves Rippling (Rare Power, 2 energy): Whenever you apply a debuff to an enemy, gain 2 Block.
- The Moon, A Ship O'er the Seas (Rare Skill, 2 energy, Exhaust): Exhaust. Mend 3. Plan: Mend 6.
- Sango Isshin (proto) (Rare Attack, 2 energy): Deal 8 damage. If the Bake-Kurage carried out a Plan this turn, deal a quarter of your Max HP to ALL enemies instead.
- Rally (Common Skill, 1 energy): Apply 1 Weak. The next Companion card you play this turn costs 1 less.
- Vanguard (Common Skill, 0 energy, Exhaust): Exhaust. Apply 1 Vulnerable. Plan: Apply 1 Vulnerable and 1 Weak.
- The General's Banner (Uncommon Power, 1 energy): Once per turn, when you play a Companion card, apply 1 Weak to the front enemy.
- Chain of Command (Uncommon Skill, 1 energy): Deal 3 damage for each Companion you played this turn. Plan: Deal 6 damage for each Companion you played last turn.
- Stolen Chapter (proto) (Common Skill, 1 energy): Draw 1 card1. Plan: Draw 4 cards.
- Change of Plans (Common Skill, 1 energy, Exhaust): Exhaust. The Bake-Kurage carries out your first Plan now.
- Undertow (proto) (Common Attack, 1 energy): Deal 1 damage, already including 1 if the enemy has a debuff.
- Salt Line (proto) (Common Skill, 1 energy, Exhaust): Exhaust. Gain 8 Block.
- Battle Plan (Uncommon Skill, 1 energy): Draw 1 card. Plan: Gain 1 Energy and draw 2 cards.
- Moon's Reflection (Uncommon Skill, 1 energy, Exhaust): Exhaust. Choose a card in your Exhaust Pile. Next turn, the Bake-Kurage carries out its Plan line, or plays it if it has none.
- Tide Chart (Common Skill, 0 energy): Next turn, after the Bake-Kurage carries out its Plans, draw 1 card for each1.
- Ripple (Common Skill, 0 energy): Gain 2 Block. Plan: Gain 1 Energy and 1 Block.
- Riptide (Common Attack, 2 energy): Deal 9 damage to ALL enemies. Plan: Deal 13 damage to ALL enemies.
- Pincer (Common Attack, 1 energy): Deal 3 damage twice. Plan: Deal 3 damage three times.
- Flank (Uncommon Attack, 1 energy): Deal 8 damage. Plan: Deal 8 damage to each enemy that intends to attack.
- Well Laid (Common Attack, 0 energy): Deal 1 damage.
- Feigned Retreat (Common Skill, 1 energy): Gain 4 Block. Plan: Gain 4 Block and deal 6 damage.

## The arm

1. **The Moon Overlooks the Waters, adjusted** (Rare Power, 2 energy).
   Standing: "Plans also happen now, as you write them." Adjusted: "Plans
   also happen now at half strength, as you write them." The now-copy
   carries out the Plan line at half its numbers, rounded down (a planned
   Deal 10 deals 5 now and 10 next morning; a planned Gain 8 Block gains 4
   now and 8 next morning); the morning copy is unchanged. The intent: under
   the standing card writing is never worse than playing (the card gives
   now AND later), which deletes the brief's decision; at half, playing the
   card is better than writing it on the turn the whole number is needed
   now (a lethal, a Block against a big hit), and writing is better
   otherwise, which is the ordinary Plan trade with waiting's price halved.

One verdict, its clause and its comparison. Under 150 words.
```

```
1. **REQUIRES_MODIFICATION — C1 (owner), removing the losing line of waiting.** Counterexample: Moon is active, you have 2 Energy, Battle Plan is your only card, the next draw is Defend, and the enemy attacks this turn. Battle Plan costs 1: playing draws 1 now; its Plan grants 1 Energy and draws 2. Standing Moon gives that full Plan now and next morning; adjusted Moon gives 0 Energy and 1 card now, then 1 Energy and 2 cards next morning. The adjustment loses 1 immediate Energy and 1 immediate card versus standing Moon, but writing still matches playing’s draw and energy expenditure this turn—allowing the same Defend—and adds 1 Energy and 2 cards next turn, preserving a line where waiting has no price.
```

```
## The arm (second reading; the first, the now-copy at half, was returned REQUIRES_MODIFICATION on C1 with the Battle Plan counterexample: its Plan line is double its play line, so any fraction of a now-copy removes waiting's price)

1. **The Moon Overlooks the Waters, reshaped** from a Rare Power (2: "Plans
   also happen now, as you write them", a combat-long effect) to a **Rare
   Skill, 1 energy, Exhaust: "This turn, Plans also happen now, as you
   write them."** Upgrade: costs 0. On the one turn it is played, every Plan
   written is carried out now in full and again next morning in full; on
   every other turn of the combat the ordinary trade stands (now, or next
   turn for more). The intent: the card stops being a standing rule that
   makes writing free for the rest of the fight and becomes one burst turn
   the player chooses, the tempo version of Nereid's Ascension (which
   doubles every morning, permanently, as the one sanctioned rule-breaking
   Rare). The decision it adds: which turn is the Moon turn, and how many
   Plans to hold in hand for it against the enemy's intent that turn.

One verdict, its clause and its comparison; say plainly whether a one-turn
window that removes waiting's price on that turn only is C1's concern or
not, against the Battle Plan counterexample you gave. Under 150 words.
```

```
1. **REQUIRES_MODIFICATION — C1 (owner).** Yes: removing waiting’s price for one turn still removes the losing line on that turn; limiting its duration does not preserve that line.

   **Comparison and counterexample:** Standing Moon costs **2**, granting immediate Plans combat-long; adjusted Moon costs **1**, upgraded **0**, granting immediate Plans this turn. Battle Plan costs **1**: play draws **1**; Plan gains **1 Energy** and draws **2**. On a Moon+ turn with **3 Energy**, Battle Plan in hand, and an enemy attacking, writing Battle Plan leaves **3 Energy** and draws **2** immediately; playing it leaves **2 Energy** and draws **1**. Writing is therefore ahead **1 Energy and 1 card this turn**, with another **1 Energy and 2 cards next morning**. The attack intent imposes no waiting price on that choice.
```
