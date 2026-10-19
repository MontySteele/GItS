# Kokomi and Yae seat round, 2026-10-19

Build: main 8df9ea464, deployed 0.2.5962. Changes under test: Kokomi's Ward
(draws instead of Blocks) and Tamakushi Casket (1 Block per Plan card or
Companion played), #1453; the pool sweep (`review/active/pool-sweep-2026-10-18.md`,
#1454: Daisesshou per Level, Eternity "Levels count twice", number fixes);
Musou no Hitotachi, Euthymia and Hold the Presses, #1455. Four Sonnet seats,
whole runs, A0, seeds rolled. Lane 2 was briefed to prefer Nereid's Ascension
and Sango Isshin. Raw records: scratchpad `seats-1019/seat-laneN/record.md`
(local).

| Lane | Kit | End | Cause |
|---|---|---|---|
| 1 | Kokomi | floor 33, act 2 boss (Knowledge Demon) | HP drained over ~15 floors; one Mend in the deck |
| 2 | Kokomi | floor 48, act 3 boss (Queen + Torch Head), Queen at 23 | Frail/Weak 99 cut Block to 4-6 a card; an all-offence deck |
| 3 | Yae | floor 31, act 2 elite (Decimillipede) | entered at 4 HP, one Block short |
| 4 | Yae | floor 17, act 1 boss (The Kin) | no Block in hand at the end, 28 incoming |

## What played well

- **Kokomi's plan-several-cards deck scaled** (lane 2, 27 fights won):
  five Stings planned at once did 45 to each of four enemies; Second Wave into
  Masterstroke did 82; planning Masterstroke and cashing it early with Change
  of Plans killed three bosses and elites.
- Kokomi's real decisions were plan-or-play-now and writing order (Second
  Wave must go before the Plan it doubles), plus timing a Plan around enemy
  tells (lane 1 landed one exactly as Spiny Toad's Thorns ended).
- **Yae's Reprint engine** carried both Yae seats: Proofread on a planter
  filled the shrine in one turn (lane 3); Reprinted Petal Storm at 4 per Sakura
  carried lane 4's act 1 (24 to ALL on turn 1 of one fight).

## What did not

- **Both kits run short of Block and recovery in long runs.** Three of the
  four deaths were HP attrition or a Block shortfall, not a lost race. For Yae
  this is the act-1 HP gap already known (`yae-tempo-fix`); for Kokomi it is
  new since Ward lost its Block, but lane 2 still reached the act 3 boss.
- **Nereid's Ascension and Sango Isshin were never offered** to lane 2 in 48
  floors (Nereid's once, from a Power Potion). The scaling question stays
  open; the plan-several-cards deck scaled without them.
- **The Casket's +1 is invisible:** lane 2 "could not tell from the screen
  whether it fired." The code pays on planning too (`TamakushiCasket.AfterCardPlayed`;
  a planned card is a play aimed at the Bake-Kurage, the hook Treatise reads).
- Ward, Daisesshou, Eternity, Musou, Euthymia and the new Hold the Presses
  were never drafted, so this round says nothing about them.
- Yae, lane 4: Sakura strikes and Tenko pick random targets and kept landing on
  The Kin's Followers instead of the Priest.

## What to change

1. **Show the Casket's Block** on the page (a "Since last page" line or a
   flash the seat page reads). One BACKLOG line.
2. **Nothing on numbers yet.** None of the changed cards was drafted; the
   next round should brief one seat per kit toward them (Ward makers and
   Kurage Canopy; Daisesshou plus a Level source, Eternity).
3. Watch Yae's random Sakura targeting against summoner bosses (The Kin): a
   targeting question for a design pass, not a number.
