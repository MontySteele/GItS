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

## Round 4, pooled (2026-10-11, 06:51)

Round 4 used the same seeds on build 0.2.4872+next. No card changed. The round added the seat-page fixes and the new telemetry fields: buffer left, Block per card, and guest repeats and evictions. The packet is `furina-r4-packet.md` in the scratchpad.

| Seed | Round 4 |
|---|---|
| JF391WG2NN0X | floor 33, Kaiser Crab |
| WDETA8RRGH98 | **won** |
| 0J427L1YQV15 | floor 48, Aeonglass |
| TYXJLVY31QN7 | floor 33, Knowledge Demon |
| Ironclad control | floor 33, Knowledge Demon |

**Pooled results.** Rounds 3 and 4 won 1 of 8; rounds 1 to 4 won 4 of 16. The control has won 0 of 4.

**Act-2 boss damage a turn** was 49.9 in round 4 and 45.8 pooled with round 3 (n=7), against 40.8 in round 3 alone. Round 3's drop was mostly variance.

**What the new telemetry shows:**
- **The buffer** emptied in 6 of 77 fights, and HP was lost past the line in 4 fights (12 HP in all). Players will rarely meet the line's penalty.
- **Block per play:**

  | Card | Block per play | Plays |
  |---|---|---|
  | Hymn of Many Waters | 6.0 | 2 |
  | Hymn of Many Waters, upgraded | 9.3 | 3 |
  | Usher | 10.8 | 25 |
  | Defend | 5.0 | 41 |

  Hymn is where the trim aimed.
- **Guest repeats and evictions:** 0 in 77 fights. The two guest rules are still untested by seats.

**The stranded bank.**
- Thirty-nine turns started with 20 or more Fanfare and played no Spend card. On 31 of them, no Spend card was in hand.
- When a capped Spend card was played with a bank of twice its cap or more, it spent exactly the cap every time.
- So both causes are real, but the larger one in this round is that the Spend-all cards are too rare to be drawn. Pick 1 (a) addresses exactly that, and stays the default.

**Flutter.** Thieving Hopper's Flutter halves any hit the game treats as an attack. Mod card damage, Skills included, is dealt as an attack. So Rising Applause and Kokomi's Opening Gambit, both Skills, are halved by it. This is on BACKLOG; it applies to every mod Skill that deals damage.

## Ruled (2026-10-11)

[USER]: "On Furina - let's try standing ovation at Common but only for half your Fanfare and see how that goes."

Pick 1 is a new option, a mix of (a) and (b): Standing Ovation goes back to Common and reads "Spend half your Fanfare. Deal that much damage to ALL enemies." Half rounds down. It no longer Spends all, so it no longer triggers Bis!.

## For [USER]

1. **The stranded bank.** This is reopened by one new fact: the bank strands with Spend cards in hand, because the Common Spend cards stop at 8 or 12.
   - **(a) Default:** Standing Ovation ("Spend all your Fanfare. Deal that much damage to ALL enemies.") goes back to Common. This undoes the 2026-10-09 move to Uncommon.
   - (b) Spirited Aria and Crashing Waves become "Spend half your Fanfare" instead of "up to 8" and "up to 12". This reopens the 2026-10-10 "Spend up to X" ruling, a ratio in place of a cap.
   - (c) No change. Watch for it in your next run.

## Round 5: Standing Ovation spends half (2026-10-11, 13:10)

The round tests the pick 1 ruling: Standing Ovation at Common, "Spend half your Fanfare." It ran on the same seeds as rounds 1 to 4, on build 0.2.4897+next. The packet (`furina-r5-packet.md`) and the Fable review (`furina-r5-review-fable.md`) are in the session scratchpad.

| Seed | Round 5 | Round 4 |
|---|---|---|
| JF391WG2NN0X | floor 33, Kaiser Crab | floor 33, Kaiser Crab |
| WDETA8RRGH98 | floor 48, Aeonglass | won |
| 0J427L1YQV15 | floor 33, Kaiser Crab | floor 48 |
| TYXJLVY31QN7 | **won** | floor 33 |
| Ironclad control | floor 48, the Queen | floor 33 |

Furina won 1 of 4, with a mean floor of 40.5, the same as round 4. Pooled over rounds 1 to 5 she has won 6 of 20; the control has won 0 of 5.

**Standing Ovation, as drafted and played:**
- Offered 9 times and taken 4 times. All four Furina decks ended with it, against 1 of 4 in round 4.
- It was played in only 10 of the 64 fights held after the take (16%). At "Spend all" in round 4 that was 36%.
- A play spent 13.5 Fanfare on average, from a bank of 27.5.

**The stranded bank:**

| | Round 3 | Round 4 | Round 5 |
|---|---|---|---|
| Turns starting at 20+ Fanfare with no Spend played | 30% | 48% | 34% |
| Of those, turns with no Spend card in hand | — | 31 | 13 |

- Making the card easier to find worked: far fewer turns had no Spend card in hand.
- How often the bank strands is back to round 3's level, not below it.
- Seats price the card per point of bank ("always worse than Bravura"). It keeps half the bank, and a seat planning a one-turn lethal values that at nothing.

**Other findings:**
- **The act-2 boss is the wall.** In rounds 3 to 5 it cost 51.6 HP a fight, with 6 deaths in 11 fights. Kaiser Crab killed both of this round's dead seats, on the same two seeds. No number moves for it on seat evidence alone.
- **Not a Block call.** Block a turn in normal fights fell from 8.9 to 5.0, but HP lost after the Drain return held at 7.4 (round 4: 6.8). The seats raced, and the one that raced hardest won.
- **The guest rules** (repeats and evictions, #1072 and #1076) are still untested after 231 fights.

**Being built, with no approval needed:**
- The seat page now logs Freminet's act as the Block it gives, not as Cryo damage.
- The Drain counter at zero uses the buffer wording.
- Lyney's badge and face describe the buffer, and the face shows his act's Drain 2.
- Telemetry records the Spend cards in hand at each turn start and the enemies alive when a Spend card is played.

**Not defects:**
- "Not enough HP" at 2 HP: Drain never takes her to 0.
- Surrounded, Hard To Kill and the other enemy rules: these are base-game rules.

## For [USER], round 5

1. **Standing Ovation's Spend.**
   - **(a) Default:** keep "Spend half" through your own run. You asked to "see how that goes", and seats undervalue a bank they keep.
   - (b) Common at "Spend all", which was this record's round-3 default.
