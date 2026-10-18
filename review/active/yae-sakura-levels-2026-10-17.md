# Yae: Sakura Levels across kinds, 2026-10-17

The user, from a co-op run, asked whether Levels transfer when a plant replaces a Sakura of
another kind. They don't today: the old one withers and the new one arrives at its printed
Level (review r3, `review/active/yae-review-r3-2026-10-14.md`: "changing the board's mix costs
you an established Sakura"). The user's answer:

> "I think that we should let levels carry over so that mixing types doesn't brick you, but the
> value of a level can't be 1 for both of them. 1 block is a meaningful amount, but 1 damage is
> not. This might need a deeper analysis."

So the direction is settled: Levels carry over. This paper is about what a Level should be worth
for each kind once they do.

## 1. What a Level is worth today

A Sakura acts at the end of every turn. What it does is its kind's base plus its Level
(`tier0/engine/yae_shrine.py` `kind_base`, C# `YaeShrineLedger.ActSize`):

| Kind | Action | Level 1 | Level 3 | Level 5 | What one Level adds, every turn |
|---|---|---|---|---|---|
| Sakura (Thunder) | 2 + Level damage to one enemy | 3 | 5 | 7 | 1 damage |
| Foxfire | 1 + Level damage to ALL enemies | 2 | 4 | 6 | 1 damage per enemy |
| Kitsune | 2 + Level Block | 3 | 5 | 7 | 1 Block |

The actions are unpowered: no Strength, Dexterity, Weak or Frail on any of them.

**The exchange rate.** The base starters price 1 Energy at 6 damage (Strike) or 5 Block
(Defend), so **1 Block ≈ 1.2 damage**. Block is also the scarcer resource for Yae: act-1 HP
lost per fight is her one remaining gap (7.8 against base 5.9,
`review/records/yae-round-10-2026-10-17.md`). The tier05 encounter pools average about
**1.5 enemies a fight** (2.0 in act-1 easy fights, 1.0–1.3 in hard ones, 1.0–1.5 in boss fights:
`tier05/content/act*_pool.yaml`). So per Level, per turn:

| Kind | One Level | In damage-equivalent |
|---|---|---|
| Thunder | 1 damage | **1.0** |
| Foxfire | about 1.5 damage (1 × each enemy; less when a small one dies) | **about 1.4** |
| Kitsune | 1 Block, the scarce one | **about 1.2, more in act 1** |

That bears out the user's sense. **A Thunder Level is the weakest point in the kit.** Thunder is
also the kind nearly every planter makes: 7 of the ~10 planting cards make Thunder, 2 make
Kitsune (Shrine Maiden's Guard, Guardian of Narukami), and Foxfire comes from Foxfire Sweep and
Sesshou Sakura.

## 2. What carry-over changes

The replace happens only into a full shrine, onto the Sakura closest to withering (the 2026-10-17
rule). With Levels carried 1:1 at today's rates:
- **Thunder → Kitsune** turns L5 (7 damage a turn) into L5 (7 Block a turn), a free upgrade worth
  about +20%.
- **Thunder → Foxfire** turns L5 (7 to one) into L5 (6 to ALL), +30% on an average fight and
  double in a three-enemy fight.
- **Kitsune → Thunder** is the only downgrade, and nobody would do it on purpose.

So carry-over alone makes switching away from Thunder strictly good. Because the Thunder Level is
worth least, a switch always lands on a better rate. The fix is to make a Level worth about the
same for every kind.

## 3. Options

**(a, default) Thunder gains 2 per Level; the base drops by 1.** Thunder: **1 + 2 per Level**
(L1 3, L3 7, L5 11). Foxfire and Kitsune unchanged. A Level is then worth 2 / about 1.4 / about
1.2, and Thunder is the highest. That's deliberate: Thunder is single-target, and single-target
damage is the kit's main job. A Level 1 Sakura still strikes for 3, so the first turns of a fight,
which the round-10 numbers just brought to base, don't move. What moves is the late fight. Her
act-3 damage is her weakest ratio (0.86 of base, round 10), and Levels pile up late, so the change
lands where she is short.
- Risk: every Level source gets stronger on Thunder (Sakura Grove "+1 Level each turn", Mikage
  Thunder, Narukami Ray, Dawn Prayer, Fox's Mooncall). **Sakura Grove** (Rare) on three Thunder
  Sakura becomes +6 damage a turn, every turn. Grove may need to drop to "every other turn" or
  "your newest Sakura"; I'd measure first, not pre-cut.
- Carry-over is then roughly even, Thunder L5 (11) → Kitsune L5 (7 Block): the Block is scarcer
  and the damage bigger, so switching is a real choice, not a free upgrade.

**(b) Carry over, rates unchanged.** The simplest text, and nothing else moves. Switching away from
Thunder is always a gain (sec.2), so a pure Thunder shrine is never the best plan once you have a
second kind.

**(c) Carry over at the target kind's rate.** For example, a Thunder Level becomes half a Kitsune
Level. That keeps value flat across a switch, but it puts fractions in the text and needs a
conversion rule the player has to learn. I don't recommend it.

## 4. What building (a) touches

- The rule: `KindBase` / `ActSize` in `YaeShrine.cs` and the sim twin `kind_base` / `act_size`
  (per-kind per-Level factor), and carry-over in `YaeShrineLedger.Plant` / `yae_shrine.plant`:
  the new Sakura keeps the replaced one's Level when that is higher than its printed Level.
- The text: the Sakura tip ("strikes an enemy for 1 + 2 per Level"), the Full shrine tip ("If not,
  it withers and the new one takes its place, keeping its Level"), and the card previews that
  print Sakura damage (Thunder Rite's "Tenko (Sakura: N damage)", Sesshou Fang's Level-3 check
  does not change).
- A rule change, so a Yae seat round follows (five runs, the round-10 seeds), and a run of yours
  at the finish.

## Picks

1. **How a Level is valued once Levels carry over.**
   - **(a, default)** Thunder 1 + 2 per Level; Foxfire and Kitsune unchanged.
   - (b) Carry over at today's rates.
   - (c) Convert at the target kind's rate.
2. **Sakura Grove under (a).**
   - **(a, default)** Unchanged until the seat round shows it.
   - (b) Pre-trim to "At the start of your turn, your newest Sakura gains a Level."
