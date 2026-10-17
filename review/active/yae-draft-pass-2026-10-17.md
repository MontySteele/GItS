# Yae: the cards seats refuse, and the starter (2026-10-17)

Yae is a Prototype kit, so her drafted cards are Claude's. The starter
change is [USER]'s pick, ruled here.
- [USER] on round 9's pick: "I agree with the starter change, but let's also
  scan the draft rates and see what cards the seats refuse to take and
  wherever they are bad value or just undervalued by the seats."
- And: "I'll authorize you to run a round on your findings if you have high
  confidence in them - otherwise just the starter change."

## 1. The starter (round 9, pick 1 (a))

| Card | Today | New | Upgrade |
|---|---|---|---|
| **Yakan Evocation** | Plant a Sakura. | Plant a Sakura. **It strikes now.** | cost 0 (unchanged) |

The strike is the flat-value pass's reading: the Sakura acts once at its
planted Level, uses none of its turns, and is not a Tenko. It has no
target, so it picks a random enemy, or Hunting Gaze's.

## 2. The scan

**Source:** card-reward, shop and event offers across rounds 7 to 9
(`tools/telemetry_report.py --offers --character "Yae Miko" --since
2026-10-16T02:30`). A seat sees three cards and takes one, so about 33% is a
normal take rate. Below I list every card offered 10 times or more and taken
at 12% or less, plus every 0-taken card with 8 offers or more.

**What the seats refuse falls into four shapes:**
1. **Cards that wither her own Sakura:** Falling Blossom 0 of 17, Hide
   Behind the Shrine 2 of 16, Fallen Petals 0 of 8. Replanting was a
   never-again pick.
2. **Pure setup that does nothing on the turn:**
   - Dawn Prayer 0 of 18;
   - Fox Fire Draft 3 of 24;
   - Sakura Seal 0 of 10;
   - Kitsune's Blessing 1 of 12;
   - Fox's Mooncall 1 of 15.
3. **Conditional effects that fizzle:** Kitsune Pounce 4 of 32. A seat
   reported it twice for doing nothing with no damaging Sakura.
4. **2-cost attacks:**
   - Publisher's Deadline 2 of 22;
   - Genre Shift 1 of 12;
   - Mikage Thunder 1 of 11;
   - The Seven Glamours 0 of 10;
   - Sacred Thunderbolt 0 of 8.

**What they take:**
- Block: Guardian of Narukami 5 of 6, Torii Ward 8 of 15, Shrine Maiden's
  Guard 15 of 34.
- Damage now: Spiritfox Prank 6 of 8, Thunder Petal 7 of 15.
- Reprint enablers: Galley Proof 6 of 12.

## 3. Bad value: changed (5 cards)

I change a card only where the text loses value on the turn it is played,
not just where the seats undervalue it.

| Card | Today | New | Upgrade | Why it is bad value |
|---|---|---|---|---|
| **Falling Blossom** (C Atk 1) | Deal 7. Your oldest Sakura withers; its Last Bloom strikes this enemy. | Deal 7. **Your oldest Sakura strikes this enemy.** | 10 | The wither throws away the Sakura's remaining turns (about 6 damage) for one aimed strike. Without it, the card is the aimed strike Common the round-7 brief asked for. |
| **Dawn Prayer** (C Skill 0) | Your newest Sakura gains 2 Levels. | Your newest Sakura gains 2 Levels. **It strikes now.** | 3 Levels | 0 damage on the turn; 0 of 18. Now it is 5 damage now at 0 cost, and the Levels after. |
| **Kitsune Pounce** (C Atk 1) | Deal 8. If the enemy is Weak, a Sakura strikes it. | Deal 8. **If the enemy is Weak, deal 5 more.** | 11 (+5) | The bonus needs Weak and a damaging Sakura, and it fizzles silently. The new bonus pays off her Weak (Sly Strike, Fox Trick), as Fox's Bargain does. |
| **Mikage Thunder** (U Atk 2) | Each Sakura gains a Level. Tenko. | **Deal 7.** Each Sakura gains a Level. Tenko. | 2 Levels (unchanged) | An Attack that deals no damage of its own: 0 with an empty shrine, for 2 Energy. |
| **The Seven Glamours** (R Atk, Exhaust) | 2: Deal 12. If this kills, Publish an Annotated card in your hand. | **Costs 1.** Same text. | 16 | A finisher must be cheap enough to finish. 12 for 2 that then Exhausts is under rate even at Common. The Silent's Ritual Dagger is 1. |

## 4. Undervalued: left alone

| Card | Taken | Why it stays |
|---|---|---|
| Hide Behind the Shrine | 2 of 16 | 17 Block a play when played (round 8), the most of her Blocks. Seats dislike the wither, but the Block pays for it. |
| Publisher's Deadline | 2 of 22 | 14 for 2 is the base rate, and 1 Energy after any Edit. Seats skip 2-cost attacks. |
| Serialization, Mischievous Teasing, Editorial Priority, Kitsune Rite | 1, 0, 0 and 1 taken | At or above rate once her Edit or Tenko turns run. Seats draft for the next turn, not the deck. |
| Fox Fire Draft, Sakura Seal, Kitsune's Blessing, Fox's Mooncall | 3 / 0 / 1 / 1 | Setup by design, at 0 or 1 Energy. The starter and Dawn Prayer now give the shrine damage on turn 1, so setup turns cost less. |
| Genre Shift, Sacred Thunderbolt | 1 and 0 taken | A next-pass question. Genre Shift plants up to three, and Sacred Thunderbolt needs a second element she rarely has solo. Not high confidence. |
| The Edit-a-card Uncommons and Rares (Footnote, Author's Copy, Reborn as Guuji Yae, Afterword, Royalties, Serial Novel) | 0 each, 5 to 8 offers | Too few offers to judge. They pay on Reprint and Publish turns. |

## 5. The round

[USER] authorized a round on high-confidence findings. These six changes
share one rule already measured: round 9 brought her turn-1 damage to base
(20.5 against 20) by making planting cards pay on the turn.

Five seats will play the same seeds. The bar is round 9's:
- act-1 normal-fight length nearer base's 3.1 turns (3.67 now);
- act-1 HP lost per fight nearer base's 5.9 (7.3 now);
- the four refused-card shapes taken more often.
