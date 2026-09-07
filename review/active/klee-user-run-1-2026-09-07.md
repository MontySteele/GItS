Status: OPEN (two picks, §5; four D and E defaults applied, §6)

# Klee, [USER]'s first act-1 run under the overhaul: the concept reads as sound, seven notes triaged

Written 2026-09-07. [USER] played Klee through act 1 and into act 2 on
`0.2.2888+proto` (main `da0e5846`: the R262 starter, Jumpy Dumpty Innate
and one detonator; the round-23 pool of 45; the six audited rows of
`review/records/card-audit-2026-09-07.md`). This is the play the loop was
waiting for, the first read of the kit's rules by [USER] since the R261 and
R262 rulings, and the Prototype stage is graded on it (stage-gate, *The
loop inside Prototype*). Evidence: [USER]'s notes, quoted in the commit that
carries this packet, and the game's own `godot.log` of the run (ten card
picks, thirty-five rarity rolls).

## 1. The verdict

**The concept is sound and this is working.** Early fights felt fragile; by
act 2 the Powers were making big numbers, and every turn was still a puzzle
about where the Block was coming from and whether going all-in would kill
the enemy now. That is the brief's tension read as designed (§6: she cannot
block on demand, every defence is conditional on the decision just made),
and the fragile opening is the R262 starter doing what the rounds said it
does. **The stage holds at Prototype**: the loop continues on the adjusted
rows below, and nothing here moves to Balance.

## 2. The notes, one at a time

**Sparks need a badge, like the Regent's Stars.** Right: Sparks live in the
power row as a buff icon, and a bank read next to the price it pays is the
base game's own idiom. Engineering, `EB-621`, applied (§6).

**The Hexerei tip is confusing.** Two things in one sentence. *"It never
costs Spark"* was defensive text against the r22 and r23 seats reading
"pay" as a surcharge; [USER] read it the other way round, and the card's
cost slot is where a cost belongs. Hygiene, `EB-619`, applied. *"Playing one
marked Klee's own"* is the second mark `EB-554` added so a Universal
printing Hexerei (Razor) and a Personal printing it could be told apart,
because only Personals pay the Spark. [USER]: the "Klee's own" text on the
Personals is not needed. That is a rule question, not a text one, and it is
pick 1.

**The Hexerei tag never came together.** Three cards read it (Coven Errand,
Witches' Circle, Venti's stand-in) in a pool of 45, and the run's ten picks
met none of them (`godot.log`). A family mark with no reader on the table is
a word that does nothing, which is what [USER] saw. Pick 2.

**Sucrose — Catalyst Conversion losing Exhaust on upgrade is too good.**
Right: a 0-cost "gain 1 Energy, draw 1" that does not Exhaust is four
Energy on the turn you draw it. The Prototype-default upgrade rule chose
"Exhaust comes off" because the row had no printed number; [USER] offered
Retain or a second draw. Taken as the second draw: the upgrade keeps
Exhaust and draws 2. D default, `EB-622`, applied.

**Grounded gives too much Block.** [USER] not confident; the seats (r19)
read the adjusted Grounded as a decision. Both are right about different
halves: the decision is real (a Bomb has to be on the field, and cashing it
ends the income), the rate is high (6 Block and a Spark every turn for one
Energy once, against Metallicize's 3). Taken at 4 Block, upgrade 6, the
Spark unchanged. D default, `EB-622`, applied; the next rounds read it.

**Mona — Stellaris Phantasm can do more.** Right: a 2-cost Rare that
Exhausts to put Hydro on everyone and 1 Vulnerable next turn is a Common's
worth of effect. The Omen now applies 2 Vulnerable. D default, `EB-622`,
applied.

**A lot of Rares.** The game's own roll says otherwise for the card slots:
thirty-five rolls in the log, two of them under the rare threshold. The run
still took four Rares in ten picks (Alice's Introduction Magic, Mona, Jean
— Lion's Fang, Sparks 'n' Splash), and the difference is the fourth reward
slot: Klee's Companion rows are 11 Rare of 47, and the slot draws from that
roster with no rarity roll at all, so a Rare Companion is on offer in about
one reward in four. `EB-620`: the slot rolls rarity the way the card slots
do. D default, applied.

## 3. What the run did not test

Act 2 past its first fights; the boss; the Spark loop under a deck built
to spend Sparks (round 23's deadlock). Nothing here is a strength reading.

## 4. What the next rounds carry

Round 24 (the React deck) and round 25 (an Energy-priced detonator beside
the Spark-priced ones) run on the adjusted rows, and each reads Grounded at
4 and the Companion slot's offer as part of its record.

## 5. Picks

**Pick 1 — the Hexerei ownership rule.** Today a Hexerei card pays Klee a
Spark only if it is one of her own Personals; a Universal printing the same
word pays nothing, and the faces carry "Klee's own" so a player can tell
which is which. [USER] read that mark as noise.

1. **(default)** Every Hexerei card pays the Spark, Universals included.
   "Klee's own" leaves the faces and the tip; the tip becomes "A Companion
   card whose face prints the word. Playing one gives Klee 1 Spark, up to 3
   a play." One word, one rule. The cost is that a Universal met in a shop
   or event pays like a Personal, which is a small gain of Sparks on a
   channel the rounds have not found scarce. Both engines and LAW:145's
   kit declaration move with it, so this is the rule change that the kit
   plays once more.
2. Keep the rule, drop the face text, and let the tip say "a Companion
   from Klee's coven". Readable only by a player who already knows which
   companions are in her coven; the r20 lane-1 defect returns.
3. Keep both the rule and the mark as they are.

**Pick 2 — whether the Hexerei tag earns its place.** A family mark that no
card on the table reads is invisible, and one act-1 run met none of its
three readers.

1. **(default)** Keep the tag; two Common readers join the pool in pool
   pass two (authored by Claude, through the audit door), so an act-1 run
   meets one. The pool grows to 47 and the pass says what they displace.
2. Keep the tag as it is and read again after rounds 24 and 25 and
   [USER]'s next run; the readers may simply not have been rolled.
3. Drop the tag. The three readers leave or are rewritten without it, and
   the Spark pays on every Companion play.

## 6. Defaults applied (D and E), disclosed

- **`EB-619`** the tip's "it never costs Spark" clause dropped, both
  surfaces (E).
- **`EB-620`** the Companion reward slot rolls rarity with the game's own
  roll and offset (D).
- **`EB-621`** a Spark badge beside Energy on Klee's seat (E).
- **`EB-622`** Sucrose's upgrade keeps Exhaust and draws 2; Mona's Omen
  applies 2 Vulnerable; Grounded pays 4 Block, upgrade 6 (D).
- No shipped-sheet number moves; no stamp moves; nothing measured.
