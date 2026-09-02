Status: RULED R242 2026-09-02

# Klee overhaul, round four: growth 3, one seat so far

2026-09-02. Round three's applied default was Bombs growing by 3 a turn
instead of 2 (`review/ruled/klee-overhaul-round-3-2026-09-02.md`,
section 3). Round four is that build: PR #265 on top of the round-three
branch, deployed as 0.2.1993+proto.dirty, soaked with no defects (the
soak bot died in its second fight, which is a floor and not a finding).
Also in the build: the seats' page now prints a Spark-priced card's price
(EB-286), the raw-template faces are fixed at the codegen (EB-285 was 24
faces, not one), the Bomb tooltip is prose (EB-287), and the shop and
rest-site readers follow the live shapes (EB-262, EB-263 in part).

Two of round three's rows closed without a change. EB-288 was not a
defect: Weak multiplies by three quarters and the face prints the whole
number, so a 10 prints 7 and a 7 prints 5, and the upgraded copy's 7 is
the base copy's own printed number. The chest with its relics up was
never reached in four captures, so EB-263's chest half stays open.

| Seat | Seed | Actions | Fights | Stopped by |
|---|---|---|---|---|
| Opus | P37JWV4UAQM8 | 100 | 5, alive at 36/68 | its action budget, mid-fight with a Bomb 43 stacked and Ka-pow! in hand |
| GPT (Codex) | owed | | | |

Record: `review/qa/blindplay/klee-overhaul-r4-opus/record.md`. Seat
numbers are floors, not fun claims (Guardrail 7).

## 1. What the Opus seat found under growth 3

1. **The bet is real now.** "Bank or cash, over and over. A bomb left
   alone is worth 3 more damage every turn, so waiting is always nominally
   correct, but detonators do not stay in your hand between turns, so
   waiting is a bet on redrawing the one card that can cash the stack."
   The seat lost that bet three times and ended the session holding a
   Bomb 43 it had spent two turns building. Round three's "growing almost
   never wins" is gone; what replaced it is a gamble on the draw.
2. **The turn shape still settles by fight four:** place every bomb,
   point a detonator at the pile, Dig In with the Sparks, block with the
   rest. The seat says the interesting decisions were all in fights one
   and two, "while I was still working out whether banking was correct."
3. **Duck and Cover is dead a third time.** "5 block for a full energy
   never competes with a card that adds 6 to a bomb." Dead or filler in
   four of five fights.
4. **Spark-priced cards cannot open a fight, by construction.** "Sparks
   exist only after a Bomb goes off; no Bomb can have gone off before your
   first play of a combat." Powder Charge printed its refusal in an
   opening hand. Round three's Spark bootstrapping, now with the price
   visible and the same conclusion.
5. **Flame Dance is a trap in her own deck:** its Set off clause needs a
   non-Pyro aura and nearly every Klee attack applies Pyro.
6. **Weak is a Bomb debuff.** Doubt's Weak shaved a quarter off bombs and
   Mines as well as attacks, and Big Badda Boom's bonus paid the post-Weak
   size while its text and the badge both point at the printed size.

## 2. Defects from the round

- EB-289: a Bomb 8 badge said "Bombs here: 2", the Set off dealt 8 and
  paid one Spark, where the keyword promises one per Bomb that goes off.
- EB-290: the blind render prints a reward relic under a `**Relic**`
  header with its name beneath, and refuses the name; `play` during a
  combat card-chooser answers "you are not in a battle"; the Spark refusal
  ends "; and this costs 1".
- EB-291: Pounding Surprise's text is the Spark keyword's text word for
  word, so it reads as a second Spark source; the Mine tooltip does not
  say "after Weak" the way the Bomb badge now does; Big Badda Boom's
  bonus line points at the printed size, not the size it pays.
- Not ours: the card-select screen carries no selection state (vendor);
  Plating's first decrement, a Gremlin Merc's unlisted Weak, and the
  Steady enchant with no tooltip are the base game's screens.

## 3. Picks, ruled R242 (2026-09-02)

1. **Spark at the start of a combat.** RULED (2): Klee starts every combat
   with 1 Spark. [USER]: Regent starts with 3 stars and has to generate more
   through cards, so 1 is a reasonable compromise. Rule 4 in the brief
   carries the line.
2. **A long fuse.** RULED (1): no rule; growth alone is the reason to wait.
3. **Duck and Cover.** RULED, neither option: the starter takes the
   canonical shape. [USER]: the starting deck already does too much; base
   characters open with four Strikes, four Defends and two good cards of
   their own, and Klee had three, two and five. Draft 4 of the starter
   (slice section 3) is Strike x4, Defend x4, Jumpy Dumpty, and Ka-pow! at 0
   energy with Retain on the upgrade. Strike and Defend are the base game's
   cards; Kaboom! and Duck and Cover leave the sheet.

Ruled in the same breath, for all three characters: where a character's
basics are a renamed Strike or Defend with the same stat line, the base
game's Strike and Defend replace them. Kokomi's Water's Edge and Coral
Guard go the same way; Furina's basics carry register text and are read by
the audit before anything moves.

Growth 3 stays. Round five is the draft-4 starter build; the seats play it
first, then, because rule 4 changed, [USER].
