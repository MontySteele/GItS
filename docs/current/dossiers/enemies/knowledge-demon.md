# Knowledge Demon

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `KnowledgeDemon` (`MonsterModel`)
- **Kind:** boss
- **Act:** Act 2 — the Hive. One of the act's three boss options (`KnowledgeDemonBoss`), second in the act's boss discovery order, with its own act-2 boss BGM and custom background.
- **Fight class:** `mixed`

Behavioral notes only, reconstructed from decompiled sources. No code reproduced.

---

## 1. Shape of the encounter

A single-body boss. The encounter model spawns exactly one Knowledge Demon, always, with no
minions, no summons, and no adds at any point in the fight. Everything the fight does, it
does through a strictly deterministic four-move cycle plus one escalating buff.

There is **no RNG in the move selection at all**. The move state machine is a pure follow-up
chain gated by one counter, so the intent order is identical on every attempt. The only
randomness a player sees is target selection in multi-seat play, and even that is
non-random here (attacks hit every opponent — see §6).

## 2. Intent pattern / AI

The state machine is built as a linear chain of four move states terminated by a conditional
branch:

```
CURSE_OF_KNOWLEDGE -> SLAP -> KNOWLEDGE_OVERWHELMING -> PONDER -> [branch]
branch: curse count < 3  -> CURSE_OF_KNOWLEDGE
        curse count >= 3 -> SLAP
```

The initial state is Curse of Knowledge, and the machine will not transition away from its
first state before performing it, so **turn 1 is always Curse of Knowledge**. The branch
state is invisible in the move log; it resolves instantly to the next real move.

Concretely, the turn order is:

| Turn | Move | Telegraphed intent |
| --- | --- | --- |
| 1 | Curse of Knowledge (#1) | debuff |
| 2 | Slap | single attack |
| 3 | Knowledge Overwhelming | multi-attack, 3 hits |
| 4 | Ponder | attack + heal + buff (three intent icons) |
| 5 | Curse of Knowledge (#2) | debuff |
| 6–8 | Slap / Overwhelming / Ponder | as above |
| 9 | Curse of Knowledge (#3) | debuff |
| 10–12 | Slap / Overwhelming / Ponder | as above |
| 13+ | Slap / Overwhelming / Ponder, repeating forever | 3-turn loop |

So: three 4-turn "chapters", each opening with a curse, then an endless 3-turn loop of
Slap → 3-hit burst → heal-and-buff. The curse counter is per-combat state on the monster and
only ever increments, so the curses never come back after turn 9.

## 3. Damage, HP, and healing numbers

Base values, with the ascension-threshold value in parentheses:

| Stat | Base | At ascension threshold | Threshold |
| --- | --- | --- | --- |
| Initial HP | 379 (min == max, no roll) | 399 | Tough Enemies |
| Slap damage | 17 | 18 | Deadly Enemies |
| Knowledge Overwhelming | 8 × 3 hits = 24 | 9 × 3 = 27 | Deadly Enemies |
| Ponder damage | 11 | 13 | Deadly Enemies |
| Ponder self-heal | 30 × number of players | (unchanged) | — |
| Ponder Strength gain | +2 | +3 | Deadly Enemies |

The Demon has **no block move**. It never gains block, never gains artifact/thorns, and
gains no power other than Strength.

**Strength is the real clock.** Every Ponder adds Strength permanently, and Strength applies
per hit — so it triples on the Knowledge Overwhelming turn. Per full 3-turn loop at Strength
*S* (base ascension), the Demon deals `(17+S) + 3×(8+S) + (11+S) = 52 + 5S`. Cumulative
damage output, base ascension, ignoring block and the curse cards:

| Turns | Strength during | Damage that chapter | Running total |
| --- | --- | --- | --- |
| 2–4 | 0 | 17 + 24 + 11 = 52 | 52 |
| 6–8 | 2 | 19 + 30 + 13 = 62 | 114 |
| 10–12 | 4 | 21 + 36 + 15 = 72 | 186 |
| 13–15 | 6 | 23 + 42 + 17 = 82 | 268 |
| 16–18 | 8 | 25 + 48 + 19 = 92 | 360 |

At the Deadly Enemies threshold the same table runs on +1/+3/+2 per turn with +3 Strength
steps, i.e. `57 + 5S` per loop with S advancing in threes — noticeably steeper.

Meanwhile the Demon heals 30 per Ponder, so its **effective** health pool is 379 plus 30 per
completed loop (per seat — see §6). A party that cannot out-damage 30 per three turns after
mitigation never finishes the fight; the strength ramp guarantees it eventually kills them.

## 4. Curse of Knowledge — the gimmick

The signature move. It deals no damage. Instead, **every living player is simultaneously
presented with a two-card choice screen** and must take one of two status cards. The choice
is blocking (all seats choose before the fight continues), and unlike normal card rewards
these cards apply their effect **immediately on being chosen** — they are not shuffled into
the deck to be drawn later. They are non-generatable status cards with no upgrade level, so
nothing else in the game can hand them to you.

One option is always Disintegration, at an escalating power. The other option rotates:

| Curse # | Option A | Option B |
| --- | --- | --- |
| 1 | Disintegration, power 6 | Mind Rot |
| 2 | Disintegration, power 7 | Sloth |
| 3 | Disintegration, power 8 | Waste Away |

What each debuff does (all are counter-stacking debuff powers on the player, and all persist
for the rest of the combat):

- **Disintegration** — at the end of your side's turn, you take damage equal to the stacked
  amount. The damage is "unpowered" (not scaled by Strength/Vulnerable and similar), but it
  is not the unblockable/HP-loss category, so leftover block absorbs it. Taking it all three
  times stacks to 6+7+8 = **21 self-damage every turn** for the rest of the fight.
- **Mind Rot** — permanently reduces your hand draw by the stacked amount (1). Flashes when it
  eats a card.
- **Sloth** — caps the number of cards you may play per turn at the stacked amount (3). The
  counter resets at the start of your turn, and the power hard-blocks play attempts past the
  cap, including auto-play effects.
- **Waste Away** — permanently reduces your max energy by the stacked amount (1).

The design intent is legible: Disintegration is the "pay in HP, keep your engine" lane, and
the rotating option is the "keep your HP, lose a piece of your engine" lane. Nothing forces
consistency — a player may mix — but the escalating Disintegration values are tuned so that
stacking it is a genuine race against your own end-step.

Note that the offered pairs are fixed and ordered; the fight cannot present curse #3's pair
first. Players learn all six cards after one full attempt.

## 5. Other flavor / state

- **Burnt state.** Knowledge Overwhelming sets an internal "is burnt" flag; Ponder clears it.
  The flag has **no mechanical effect** — it only swaps which idle/hurt/death animations play
  and drives a boss-progress parameter on the music system. It is a visual tell for "the
  Demon just used its big turn / just reset", not a damage or defense modifier.
- **Music telemetry.** The fight advances a boss-progress music parameter (1 on Overwhelming,
  2 on Ponder, 5 when the Demon leaves the room). Cosmetic.
- **Barks.** Curse of Knowledge plays a start line and a done line as gold speech VFX.
- **Order within Ponder.** The heal and the Strength application both resolve *after* Ponder's
  own damage, so the new Strength stack does not boost the Ponder hit that granted it — it
  first shows up on the following Slap.

## 6. Multiplayer / seat count

This is the one place the fight scales, and it scales in the boss's favor:

- **HP does not scale with seat count.** 379/399 flat, regardless of party size.
- **The Ponder heal does:** 30 **× the number of players** in the combat. In a two-seat run
  that is 60 per loop, in three seats 90. This is the intended offset for a party's higher
  damage throughput, and it is the fight's real difficulty dial in co-op.
- **All three attacks hit every opponent.** Monster-sourced attacks here target all opposing
  creatures with the targeting list refreshed between hits, and none of them are flagged as
  randomly-targeted. So Slap, each of the three Overwhelming hits, and Ponder land on every
  seat for full value — the fight does not split its damage across the party.
- **Curse of Knowledge hits every living seat in parallel.** Each player gets their own choice
  screen, and dead players are skipped. The curse counter advances once for the move, not once
  per player, so a four-player party still only sees three curses. Seats may pick differently,
  which means co-op parties can deliberately split the burden — one player eats the
  Disintegration stacks while another protects their energy curve.

## 7. Proposed fight class: `mixed`

The per-turn demand rotates through three genuinely different asks and never settles on one.
Turn 1 of each chapter demands a *deckbuilding* decision under blocking pressure (accept
escalating end-of-turn self-damage or permanently amputate draw/energy/plays), which is pure
gimmick and applies zero immediate damage. The Overwhelming turn demands a real block spike —
3 hits multiplied by accumulated Strength, the single largest number on the board and the one
that punishes chip-block and thorns math. And the fight as a whole is an attrition race: 379
flat HP plus 30 healing per seat per loop, against a Strength ramp that compounds five points
of damage per loop and never stops, means a party must clear a rising damage-per-turn bar
while its own engine has been permanently shrunk. Labeling it spike would ignore the healing
clock, labeling it attrition would ignore the 3-hit burst and the choice screen, and labeling
it gimmick would understate a boss that will simply out-damage an under-scaled deck; `mixed`
is the honest bucket, and Track B should expect this fight to demand block, sustained damage,
and deck resilience on a 3-turn rotation rather than a flat curve.
