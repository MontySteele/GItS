# Seat round: Kokomi, Varka and Furina on 0.2.4162 (2026-10-01)

Build 0.2.4162:
- Kokomi: her status batch (#801), Riptide Ruin and "Or plan:" only under a
  now line (#806).
- Varka: his Anemo defence (#805) and the Knight's Commission re-aim (#808).
- Furina: her rules pass (#797) and the Spend warning (#804).
- Every seat: brief mode defines each word the first time it is printed (#807).

Six Sonnet seats, one act per seat with handoff notes, ascension 0,
game-rolled seeds. Raw records are gitignored (session scratchpad `w9-lane1`
to `w9-lane4`, `w9b-lane1`, `w9b-lane2`). The base-game yardstick is
`base-sonnet-baseline-2026-10-01.md`: Silent won and Ironclad died to the act-3
boss.

## Results

| Seat | Act 1 | Act 2 | Act 3 |
|---|---|---|---|
| Kokomi 1 | died to Ceremonial Beast (53/252) | | |
| Kokomi 2 | died to Lagavulin Matriarch (78/222) | | |
| Varka 1 | Waterfall Giant beaten, 77/80 | Kaiser Crab beaten, 21/87 | died to Test Subject phase 2 (162/200) |
| Varka 2 | Vantom beaten, 46/80 | The Insatiable beaten, 57/90 | died to Test Subject phase 2 (about 63/200) |
| Furina 1 | Lagavulin Matriarch beaten, 59/78 | died to The Insatiable (117/321) | |
| Furina 2 | Ceremonial Beast beaten, 49/78 | Knowledge Demon beaten, 4/88 | died to Test Subject phase 2 (about 90/200) |

All three act-3 deaths came at Test Subject's phase 2, which adds a 10-damage
hit every turn (3, 4, 5, 6 hits). The base Ironclad died to the act-3 boss too,
so the act-3 wall is partly the game's.

## What played well

- **Varka's reaction engine.** Electro, then Pyro, then a free Four Winds'
  Ascension Swirl decided fights. One-turn Exoskeleton clears; 125 damage on
  The Insatiable's first turn. Violet Storm+ hit for 32 to 119 and carried
  every run. The Fang's turn-one element ended the element-less dead hands
  (none reported this round).
- **Furina's Spend.** Curtain Rise's Spend choice and Bravura "drove nearly
  every real decision." Exact-lethal arithmetic from the forecast (stripping 32
  Block to cancel a 23-damage attack) was the best play of her runs.
- **Kokomi's Plan order.** Opening Gambit into a damage Plan, and Open the
  Casket into Sango Isshin (three enemies with two cards), were the best turns
  either Kokomi seat had.

## What did not

- **Kokomi dies at the act-1 boss: 4 of 4 today.** Plans never answer the attack
  in front of her, and Dexterity loss shut off her flat Block. Ruled fix: a Plan
  stays open (`review/active/kokomi-delay-pays-2026-10-01.md`), building.
- **Varka and Furina have no answer to a scaling multi-hit.** Both Varka seats
  made 13 to 14 Block a turn against 40 to 60 incoming. Furina's front
  performer soaks about 3 per hit. Varka seat 1 died with no Block card in hand
  on the turn it needed 40.
- **Skill taxes.** The Infested Prism (Tainted) and the boss's Enrage punish
  Skill-heavy decks; Kokomi and Furina are mostly Skills. Base Silent took the
  same hit, so this is a known base-game counter, not a kit hole.
- **Readability.** Fixed in #817:
  - Furina's Bow forecast omitted the Bow's damage.
  - Vigor on a per-target AoE paid only the first enemy.

  Building in fix batch two:
  - Varka's Overload hit Varka himself.
  - Star Billing missed two summon paths.
  - The Spend tip doesn't say "back first."
  - Arkhe Alignment's stacking.
  - Kaeya printed Frozen through Artifact.
  - Potions vanished after the Drowning Beacon event.
  - The `use potion 1` ambiguity.

## What to change

1. **Kokomi:** the open-Plan rule (ruled), then two seats and [USER]'s run.
2. **Varka defence, part two:** a defensive cash-out that scales the way his Oath
   damage does, not bigger flat Block. A short paper.
3. **Watch list:**
   - Violet Storm+ (carried every Varka run).
   - Knights' Roll Call+ (any Knight at 0 cost).
   - Arkhe Alignment's Ousia (chosen 6 of 7 times).
   - Furina's draw outrunning her Energy.
4. **Never-again cards named:** Short Circuit, Stolen Chapter and Rising Applause;
   Final Bow was called "the dud".
