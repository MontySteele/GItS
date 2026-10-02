# Klee final pass: HP, Kitchen Alchemy's slot, a Spark sink (2026-10-02)

Status: RULED 2026-10-02 (see "Ruled" at the end). After the build, there is
one seat round on fixed seeds with no forced cards, then Balance.

## Why now

Klee has lost all nine seat runs since the status package:
- w10: `klee-kokomi-round-2026-10-01.md`
- w12: `casket-and-klee-defence-round-2026-10-02.md`
- w13: `klee-forced-defence-round-2026-10-02.md`
- w14: `klee-tune-and-smoke-round-2026-10-02.md`

Three runs reached the act-2 boss, and all three died to it. The losses look
alike: the damage is there, and the Block runs out on one boss turn.
- In w14, lane 2 died to Kaiser Crab 4 Block short.
- In w14, lane 1 died with Living Fog on 1 HP, after an elite took it from
  73 to 11.

The same four records name two loose ends in the kit:
- **Kitchen Alchemy is dead.** It was played 2 times in about 26 hands
  across w13 and w14, and two seats named it NEVER AGAIN.
- **Sparks pile up.** Two to eight sit unspent at the end of most fights,
  and seats spend them only after drafting Fireworks Finale. Your own run
  read the same way: Sparks "only really matter if you're trying to let your
  bombs cook ... I never really felt pressed for them."

Your verdict on the loop stands ("the core gameplay loop was indeed fun").
So this pass touches three numbers and two rows, not the rules.

## 1. Her HP

| Character | HP | Source |
|---|---|---|
| Ironclad | 80 | `game_ref/ironclad_char_facts.yaml` |
| Defect, Regent | 75 | `game_ref/defect_char_facts.yaml`, `regent_char_facts.yaml` |
| Silent | 70 | `game_ref/silent_char_facts.yaml` |
| Necrobinder | 66 (Osty soaks hits) | `game_ref/necrobinder_char_facts.yaml` |
| Kokomi, Varka / Furina | 80 / 78 | `Kokomi.cs`, `Varka.cs`, `Furina.cs` |
| **Klee** | **62** | `Klee.cs:83` |

Klee is 8 below the lowest base character with no pet. She also has the
weakest plain Block on purpose (brief §6: "She cannot stall, and she cannot
block on demand"). The brief means that weakness to make cooking a bet. At
62 HP it decides runs before the bet does: the act-2 deaths above came down
to 4 Block and 1 enemy HP.

## 2. Kitchen Alchemy's slot

Today's text: "ALL enemies lose 1 Strength. Exhaust every status in your
hand; they lose 1 more for each." It costs 1, Exhausts, and its upgrade adds
Retain.

Losing 1 Strength does work against an enemy at 0 Strength, but only as 1
less damage per hit. The status bonus needs a status in hand, which is rare
(w12 record, "What did not"). You asked for an alchemy-flavoured Strength
reduction, and the card should stay that. The fix is to make it answer the
turn she dies on.

The base game's closest card is Silent's Piercing Wail: Common, cost 1,
Exhaust, ALL enemies lose Strength **this turn**. It is 6 [8] in the first
game; our extract, `game_ref/silent.json`, does not carry its number.

## 3. Something to spend Sparks on that keeps her alive

The Spark→Block cards today:
- **Dig In** (Common): 0 Energy and 1 Spark for 8 Block, once.
- **Sit Tight** (Uncommon): 1 Spark.
- **Blast Shield** (Uncommon): 0 Energy and 1 Spark for 6 [8] Block, and it
  "Return[s] this card to your hand". It is the only repeatable sink, so it
  is the card that turns a pile of Sparks into a boss turn survived. In w13
  the lane-1 seat that had it played it four times in the boss fight.

It sits at Uncommon, so seats rarely see it. (This paper first proposed
moving Playdate to Uncommon on the grounds that companions are rare. That
was wrong: every post-fight reward offers one, as its fourth choice
(`PoundingSurprise.TryModifyCardRewardOptions`). The "one card reward in
twenty" line in the mod's manifest description was stale.)

## Picks

1. **Klee's HP.** (a, default) **70**, Silent's. (b) 66, Necrobinder's.
   (c) Keep 62.
2. **Kitchen Alchemy.** (a, default) "ALL enemies lose 5 [7] Strength this
   turn. Exhaust every status in your hand." Cost 1, Exhaust, Uncommon. It
   is a boss-turn answer one rarity above Piercing Wail, with the status
   clause turned from a condition into a free bonus. (b) "ALL enemies lose
   2 [3] Strength. Exhaust." That is permanent and smaller, so it still
   reads weak in act 1. (c) Cut it, and the pool goes to 77 until a
   replacement is designed.
3. **The Spark sink.** (a, default) Blast Shield becomes a Common and
   Playdate becomes an Uncommon. The pool stays 78 at 24 / 33 / 21, with no
   new card and no rule change. (b) Pounding Surprise also gives 1 Block per
   unspent Spark at the end of your turn. This is a starter-relic change,
   and it breaks rule 7 ("Nothing fires by itself"), so it is listed only to
   be refused. (c) Leave it: the pile is the reward Fireworks Finale and
   Stoke the Fuse cash in.

All three at their defaults are one change each: `Klee.cs`'s HP, one row's
text and numbers, and two rows' rarity. Both engines get them; then the seat
round.

## Ruled (2026-10-02)

[USER]:

1. "Makes sense, we can adjust up. Let's try 70 like Silent." **Klee's HP is 70.**
2. "I think that I prefer the permanent decrease, but what if we separate this
   into two cards? One remains the permanent strength reducer tied to statuses
   (-1, and another -1 per status exhausted, upgrades to retain), and another
   becomes a Star card that gives a temporary debuff."
   - **Kitchen Alchemy stays as it is.** It is already that card: "ALL
     enemies lose 1 Strength. Exhaust every status in your hand; they lose 1
     more for each.", and its upgrade adds Retain.
   - **A new Spark-priced card does the temporary debuff.** I read "Star
     card" as Klee's Stars, the Sparks (brief §18: Spark is "a currency ...
     Regent's Stars the comparison"). The new card is **Cover Your Ears!**
     (Uncommon Skill, 0 Energy and 2 Sparks, Exhaust): "ALL enemies lose 6
     [8] Strength this turn." Two Sparks is the pool's price for an Energy's
     worth (Sparkling Burst, Boom Badge), and the numbers are Piercing
     Wail's. It is also the second Spark sink, and it fires on the boss turn
     this paper is about.
3. "Agreed on Blast Shield. But Companion cards come in the 4th reward slot -
   you should be offered one every single reward." **Blast Shield becomes a
   Common.** Playdate stays a Common, since its premise holds.

**Keeping the pool at 78 and 24 / 33 / 21.** Blast Shield up and Cover Your
Ears! in leave one Common too many. **Where Did I Put It?** is cut: the w14
act-2 seat named it NEVER AGAIN ("it found a Set off card 1 time in 5 and gave
no reason when it didn't"), and Countdown, Treasure Map and Once More! already
fetch Set off cards. This is the main session's call, not a ruled pick; it
reverses with one row if [USER] would rather cut something else.
