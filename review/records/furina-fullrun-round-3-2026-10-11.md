# Furina whole-run round 3, 2026-10-11

This round is the first since [USER]'s winning run on 0.2.4813 ("the first Furina prototype where I think we really nailed it"). It plays the changes built from his notes:
- **The Drain buffer (#1071).** The first Max HP / 4 drained each combat returns after combat, and normal damage never uses it.
- **Three card changes (#1073).** Singer of Many Waters gains Retain; Balance the Books is reworked; Hymn of Many Waters is trimmed to 6 Block, Repay 3.
- **Guests (#1072, #1076).** Repeated Guest Stars act, and an evicted guest bows.
- **Counters (#1075).** Their numbers are outlined so they read on any background.

Round setup:
- Four Sonnet seats on the same seeds as rounds 1 and 2, plus the Ironclad control, on build 0.2.4849+next.
- The packet (`furina-r3-packet.md`), the records and the scripts are in the session scratchpad, which is gitignored.
- A Fable reviewer reviewed the round (`furina-r3-review-fable.md`). The main session accepted the review as written.

## Result: 0 of 4, and no sign that a change caused it

| Seed | Round 3 | Round 2 | Round 1 |
|---|---|---|---|
| JF391WG2NN0X | floor 27, Entomancer elite | floor 33 | floor 27 |
| WDETA8RRGH98 | floor 48, Aeonglass (act-3 boss) | floor 25 | won |
| 0J427L1YQV15 | floor 33, Kaiser Crab | floor 48 | won |
| TYXJLVY31QN7 | floor 33, Knowledge Demon | won | floor 48 |
| Ironclad control | floor 48, the Queen | floor 33 | floor 48 |

The mean floor is 35.25, against 38.5 in round 2 and 42.75 in round 1. Rounds 1 to 2 fell by the same amount with no card change, and the control rose this round. Four seeds cannot separate the kit from the seats.

**Why the act-2 boss number fell (61.9 to 40.8 damage a turn).** Round 2's figure rests on two turns:
- Bravura+ for 210;
- Standing Ovation twice for 150.

Round 3's three act-2 boss fights each had one Spend-all card at 1 damage per point. Lane 3 held Bravura and fired it at 12 Fanfare.

**Why act-2 normal fights cost more HP.** The incoming damage was the same as round 2 (16.7 against 16.4 a turn), and Block cards were played just as often (0.80 against 0.82 a turn). But each Block card gave less, so Block per turn fell from 9.2 to 7.4:
- Usher was played 18 times, against 31 in round 2;
- Hold the Stage 3 times, against 14;
- Defend 87 times, against 76.

**What did not cause it:**
- **The Drain buffer.** Seats drained about the same (5.4 a fight against 6.5). HP lost past the line fell from 119 to 4.
- **The Hymn trim.** Fights with Hymn blocked more, not less.
- **Guest Star drafting.** Seats took 3 of 19 offered, the same rate as before. The two guest changes (#1072, #1076) never fired: no fight had a repeat or a fourth guest. They are untested, not harmful.

## What played well

- **Curtain Rise's choice:** Drain 3 for the bigger effect, or not. Every Furina record named it.
- **Big Fanfare cash-outs:** Rising Applause for 76, Bring the House Down+ for 93, Bravura for 52 to stun the act-1 boss.
- **Overdraft, then a Hydro card:** no net HP lost, and Fanfare gained. The seats called it a readable combo.
- **Lyney's Pyro into a Hydro card:** the Vaporize combo.
- **Exact Block counting** against the incoming line.

## What did not

- **The stranded bank is back, and it has a new shape.** Lane 2 died to Aeonglass holding 86 Fanfare.
  - On 8 of its 11 turns it held a Spend card, but each one could take only 8 or 12 (Crashing Waves+, Hold the Stage+, Spirited Aria+).
  - Every Common Spend card takes 12 or less. The only cards that take the whole bank are the starter Rising Applause and four Uncommon or Rare cards.
  - Seats take a Spend-all card 5 of the 7 times one is offered, so drafting isn't the problem: they are offered about one Spend-all card per act.
- **Block drafts were small.** Seats chose low-Block cards, so each Block play gave less.

## Being built, with no approval needed

These are seat-page lines (the seats' text view of the game), plus telemetry:
- **The Drain counter leads with the buffer.** It now reads "Drain buffer 13 of 19 left: Drain inside it returns after combat; past it, only Repay returns." The old sentence was dense; three lanes said so.
- **Charlotte's log shows its Block.** It reads "Repay 0, +2 Block", where it printed only "Repay 0".
- **"First" is explained.** The incoming line says a hand card's self-hit (such as Wither) lands before the enemies act and is taken by your Block.
- **A note on Vulnerable and Slow.** When an enemy has either, the page says that card numbers in hand leave them out. This is the base game's preview convention.
- **New telemetry:** the buffer left at combat close, Block gained per card, and guest repeats and evictions.

**On the watch list, unchanged:**
- Crescendo: weak on one play.
- Balance the Books: offered once in three rounds and never taken.
- Prima Donna and Hymn: the seats' "never again" picks, both fine on the evidence.

## A fact for your run

The buffer came into play in 2 of 65 fights, so seats almost never meet the Drain line's penalty. If you want players to feel the line, the lever is the buffer's size, which is your ruled number. This is a fact for your run, not a pick.

## For [USER]

1. **The stranded bank.** This is reopened by one new fact: the bank strands with Spend cards in hand, because the Common Spend cards stop at 8 or 12.
   - **(a) Default:** Standing Ovation ("Spend all your Fanfare. Deal that much damage to ALL enemies.") goes back to Common. This undoes the 2026-10-09 move to Uncommon.
   - (b) Spirited Aria and Crashing Waves become "Spend half your Fanfare" instead of "up to 8" and "up to 12". This reopens the 2026-10-10 "Spend up to X" ruling, a ratio in place of a cap.
   - (c) No change. Watch for it in your next run.
