# Furina Spend round 2, 2026-10-10

This is the second round on the Spend paper (PR #1014, build #1016). It adds the round-1 fixes (#1022):
- High Stakes reads net Drained.
- The curtain call shows HP lost past the line.
- Block previews fold in Frail.
- Telemetry logs Fanfare per fight and HP after the curtain call.

**What ran**
- Staging 0.2.4711+next, per-act Sonnet seats, embark `20261010-051818`.
- The same four seeds plus the Ironclad control.
- The fact packet and records are in the session scratchpad (`furina-spend-r2/`), which is gitignored.
- The review below is by a Fable reviewer. The main session accepted it with one correction: card offers are already logged for every character (#980), so the next round reads them rather than building a logger.

## Result

| Seed | Round 2 | Round 1 | Block round |
|---|---|---|---|
| JF391WG2NN0X | floor 33, Kaiser Crab (Crusher at 14) | floor 48 | won |
| WDETA8RRGH98 | floor 46, act-3 normal fight | floor 17 | floor 33 |
| 0J427L1YQV15 | floor 33, Kaiser Crab | floor 33 | won |
| TYXJLVY31QN7 | floor 30, Infested Prism | floor 24 | floor 17 |
| Ironclad control | floor 48, the Queen | floor 17 | floor 48 |

0 of 4 again. The mean death floor is 35.5, against 30.5 in round 1.

**Strength is the same, per fight.**

| Normal fights, against base | Act 1 | Act 2 | Act 3 |
|---|---|---|---|
| Damage a turn | 1.03 | 0.90 | 0.91 |
| HP lost after the return | 0.59 | 1.38 | 0.80 |

- HP lost after the return is 0.94 of base pooled.
- Block a turn is about double base.
- The Spend change neither buffed nor nerfed her measurably.

**Overflow is solved where a spender is drawn.**
- Fanfare at fight close (67 fights): median 5, mean 8.4. 25 fights closed at 0.
- The 11 fights with no Spend at all closed at a median of 22. The other 56 closed at a median of 2.
- Up-to Spends hit their cap 66% of the time.
- Fanfare at death: 4, 9, 21 and 26.
- The caps hold. Paper pick 3 does not fire.

**What kills her is act 2, and its bosses:**

| HP lost, as a share of max | Furina | Base |
|---|---|---|
| Act-2 bosses | 77% | 50% |
| Act-2 elites | 34% | 28% |

- Seed 0J42 has died to Kaiser Crab on floor 33 in four of five rounds.
- In 16 of 67 fights her first turn faced incoming damage and she gained no Block. The control: 2 of 22.
- She takes hits on purpose for Fanfare.
- Long fights push Drains past the line. Six quoted past-line losses total 63 HP, the largest (17 and 23) in Regina fights.
- The four block-gap cards were barely played: Velvet Curtain 5, The Masquerade 2, Private Box 0, The Show Must Go On 0.

## What changes (Claude ships)

1. **High Stakes reads a running total.**
   - New text: "Your Attacks deal 1 additional damage for every 5 HP you have Drained this combat." Upgrade: every 4.
   - Net Drained sat near 0 because Salon Solitaire Repays 1 every turn. The card peaked at +2 in three plays.
   - Expected: about +2 in a normal fight, and +5 to +8 in a nine-turn boss fight. If bosses read under +3, the rate moves to 4 [3].
2. **Gentle Current: the delay folds away.**
   - New text: "Gain 5 Block. Repay 3. Gain 1 Block for any HP it could not Repay." Upgrade: 7 Block, Repay 4.
   - Seats never paid for "next turn": "never beat Defend" three times.
3. **Charlotte's line** counts only Repays from a card you play: "the first time one of your cards Repays each turn, draw 1".
   - Today her own act or Salon Solitaire can fire the draw at end of turn, and the drawn card is discarded.
   - The hook order is to be confirmed in game.
4. **A Drain line of 0 explains itself.** The line hover says "all your Drain returns after combat". A seat read a line of 0 as "every Drain is permanent", which is backwards: at line 0 every Drain is above the line.
5. **Hygiene:**
   - Fix the stale Salon Solitaire comment (`FurinaStage.cs:36-37` says Repay 2 [3]; it is 1 [2]).
   - Give Thunderous Applause its own damage credit in telemetry.

**Base-game rules or seat error:**
- Buffer is eaten by her own Drain. That is Buffer's rule: "Prevent your next HP loss".
- Droplet of Precognition into a full hand sends the card to the discard pile, by the base hand-size rule.
- The Infested Prism is not a kit gap. Powers and Attacks are the escape for every character. Furina has The Masquerade and seven Drain Attacks; the Silent has no non-Skill Block at all. Seed TYXJ entered that elite at 25 and 34 HP with no rest. Another lane beat it from 80 HP in 3 turns.
- No change for Bubble Aria, Sigewinne, Freminet, Navia, Hold the Stage or the four up-to cards.

## Picks for [USER]

1. **Regina's Drain stops at the line, like a guest act.**
   - Regina is her own card, so by the ruling ("her own Drains may go past it, a guest act's stops at it") it goes past the line today. But it fires every turn with no choice, like an act, and it carried the round's two biggest past-line losses.
   - Proposed text: "At the start of your turn, Drain 3, never past your line. If you do, gain 1 Strength."
   - **Default: yes.**
2. **Navia to Uncommon,** so the draw-independent Fanfare sink shows up. Neither round recorded her offered. This moves the ruled 20 / 37 / 21 rarity split.
   - **Default: no. Read the offer logs first.**

## Next round

The same four seeds and the control, with the changes above.

**New telemetry:**
- HP drained past the line and not returned, per fight;
- High Stakes bonus dealt;
- Thunderous Applause damage as its own source;
- whether a Block card was in hand when damage was incoming.

**Also read:**
- the offer logs for Block-card density and for Navia and Hold the Stage;
- the act-2 boss fights, turn by turn.

**Then [USER]'s own run.** "Spend up to X" is a keyword rule and ships after his play.
