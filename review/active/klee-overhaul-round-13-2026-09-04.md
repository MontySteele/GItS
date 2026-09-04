Status: OPEN (no pick; the defaults in §4 are applied)

# Klee round thirteen: don't use your big spell, and the queue nobody can see

Written 2026-09-04. One blind Opus seat played the Bomb kit on
`0.2.2547+proto`, the build with Stoke the Fuse in the pool (35 rows), the
Mine tip saying the hit lands in full (`EB-436`), the Set off tip's walk
(`EB-432`, `EB-443`), and the Hexerei mark on every face (`EB-392`).
Record: `review/qa/klee-round-13-2026-09-04/opus-act1.md`. Prototype stage,
Guardrail-7. No pick.

## 1. The run in one paragraph

Seed `UN45MXM68EHD`, Ascension 0 (from the embark sidecar; the seat was not
told either). Eight fights, eight won, three of them at zero damage; floor 14
of 16 cleared with the rest site and Lagavulin Matriarch unplayed; 41 of 62
HP. **The seat overran the budget:** it kept no running count and
reconstructed 155 to 160 accepted actions against 120, then stopped. Fights
7 and 8 are past the cap and read with that caveat; the round is not void
(the record declares it in Identity and again at the end). Neither Countdown
nor Stoke the Fuse was drawn; Countdown was offered at the first reward and
passed over for Dodoco Cover, so it has now been offered once and drawn
never in six runs.

## 2. What the round found

**The kit's best decision is not detonating.** "Kills move it on" against
"Set off": kill a bombed enemy by other means and the whole stack moves to
a survivor; set it off and it is spent. Fight 2 turned a 7-HP slug into a
free 24-damage transfer (Duplicator on a Strike, then Ka-pow! for 28 into the
second slug); fight 7 did it mid-queue on the game's own initiative, a
Seapunk dying partway through a 45-Bomb walk and the unfired charges
landing on the Cultist as Bomb 23. The seat: "I have not seen another
deckbuilder where 'don't use your big spell' is this often correct," and
every step was derivable from printed text. This is the third round in a
row to call ordering the puzzle; the wording of the two tips did that work.

**The queue is invisible and the enemy-turn Melt is too.** The badge prints
`Bomb 45 (4 bombs)`, a sum, while the tip says the oldest fires first and
takes the aura, so which charge Melts is memory work. And a Mine that fired
on the rat's turn into a Cryo aura dealt 12 where 7 was printed, with no
line naming the reaction; the seat confirmed it by HP arithmetic, "the one
place the kit asked me to trust arithmetic over the screen" (`EB-450`).

**Smoggy switches Klee off.** One Skill per turn against a kit whose bomb
placement, Block and Spark generation are all Skills: a wasted energy, The
Big One dead in hand. A reading, not a row: the pool's Skill density is a
design fact of the brief (placers are Skills by rule), and one base-game
debuff finding it is what a debuff is for. Carried to the pool pass as a
question about whether one placer should be an Attack.

**Dig In and Fwoosh! are the structural answer.** Spark-priced Block and a
Spark-priced detonator ended the block-or-build bidding for the same three
energy; the seat called Dig In "the first card that made a defensive turn
feel like a choice rather than a tax." R219's price is doing what the brief
said it would.

**Two events never named the card they gave or upgraded.** Trash Heap's
random card was identified as Caltrops two fights later; Endless Conveyor's
upgrade was found as Strike+ in the shop's removal list. A bridge page gap,
not a kit one (`EB-448`).

**The starter's bottom, again.** Defend was "flatly outclassed by three
other cards in my own deck by floor 10" and Strike's one real job was the
kill-without-set-off line, which the card does not hint at. Same finding as
rounds 11 and 12.

**Turn one.** Jumpy Dumpty placed on faith with no Set off in hand and no
way to know one existed: a real decision on turn one, and a bet a new
player can lose without knowing they made it. The starter carries Ka-pow!,
so the bet is safe; whether the Bomb tip should say "your deck starts with a
Set off card" is a one-line question for the next tip pass, not a row.

## 3. What the round did not test

Countdown; Stoke the Fuse; the boss (two floors short); act 2. Fights 7 and
8 are over budget. One run. Nothing here is a strength reading.

## 4. Defaults applied (D and E), disclosed

- **`EB-448`, `EB-450` minted.**
- **The seat brief's count rule gets a mechanism** (E): the seat is told to
  count and this one did not; the next round's coordinator notes ask for the
  count to be appended to the scratch file after every act, and a lane
  above zero stays disposable so the overrun cost nothing but the caveat.
- **Countdown's sixth non-draw** is recorded, not acted on: it has been
  offered once. The pool pass keeps its row.
