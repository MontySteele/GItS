# Soul Nexus

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `SoulNexus` (`MonsterModel`, sealed)
- **Kind:** elite
- **Act:** Act 3 (Glory; act index 2)
- **Encounter:** `SoulNexusElite` — `RoomType.Elite`, a **solo** encounter. Both `AllPossibleMonsters` and `GenerateMonsters` return exactly one body, no slot label, no adds, no camera override.
- **Fight class:** `attrition`

Behavioral notes only, reconstructed from decompiled sources. No code reproduced.

---

## 1. What Soul Nexus is

Soul Nexus is a single mid-size body (234 HP, 254 at Tough Enemies) that runs the **simplest possible three-move random machine**: three attacks, equal weight, no repeats, forever. It has no block, no buff, no summon, no power application to itself, no HP threshold, no death rider, and no scaling of any kind inside the fight. Nothing it does gets bigger on turn 12 than it was on turn 2.

What it has instead is **no downtime**. Every one of its three moves is an attack, so there is no turn on which the player is safe to spend the whole hand on offence. The only variation between turns is *what shape* the ~24–29 incoming damage arrives in, and whether that turn also drops a debuff pair on the party.

The fight's entire personality is: a flat, unrelenting damage tax, plus one move in three that makes the tax hurt more for two turns and makes the player's clock slower for two turns. It is a resource-drain elite, not a puzzle.

## 2. Intent pattern / AI

The move machine is a **three-spoke random hub**. Each of the three attacks hands off to a shared random-branch node, and that node feeds back into all three attacks at weight 1 each, every branch flagged **cannot-repeat**.

```
Turn 1:  SOUL BURN   (always — initial state)
              ↓
         ┌──────────────┐
         │  RAND (hub)  │  weight 1 / 1 / 1
         └──────────────┘
          ↙      ↓      ↘
   SOUL BURN  MAELSTROM  DRAIN LIFE
        └────────┴────────┘  → back to hub
```

Two facts fully describe the AI:

- **Turn 1 is always Soul Burn.** The machine seeds on Soul Burn and suppresses any transition until the monster has performed its first move, so the 29-damage single hit on turn 1 is deterministic at every ascension and every seat count.
- **From turn 2 on, it is a strict 50/50 between the two moves it did not just use.** The cannot-repeat flag zeroes the weight of whichever move was logged last; the remaining two are weight 1 each. There is no cooldown longer than one turn, no use-once move, and no maximum-repeats bookkeeping. So the sequence never contains a doubled move, and over a long fight each of the three lands close to one turn in three.

| Turn | Move | Intent shown | Effect |
| --- | --- | --- | --- |
| 1 (always) | **Soul Burn** | single attack | 29 damage (31 at Deadly) |
| 2+ (~1/3) | **Soul Burn** | single attack | 29 (31) |
| 2+ (~1/3) | **Maelstrom** | multi-attack, ×4 | 6 damage ×4 = 24 (7 ×4 = 28 at Deadly) |
| 2+ (~1/3) | **Drain Life** | *two* intents: attack **and** strong-debuff | 18 damage (19), then **Vulnerable 2** and **Weak 2** to **every** player |

Practical read for a demand model: the intent icon tells the player everything one turn ahead, and the *previous* move tells them which two options are live. After a Drain Life turn the player knows for certain the next hit is either 29 or 6×4 — both amplified 1.5× by the Vulnerable they are now carrying. That is the only place in the fight where the player can plan two turns out.

## 3. Numbers

| Stat | Base | Tough Enemies (asc 8) | Deadly Enemies (asc 9) |
| --- | --- | --- | --- |
| Initial HP | 234 (min == max, no roll) | 254 | — |
| Soul Burn damage | 29 | — | 31 |
| Maelstrom damage per hit | 6 | — | 7 |
| Maelstrom hit count | 4 | — | 4 (unchanged) |
| Maelstrom total | 24 | — | 28 |
| Drain Life damage | 18 | — | 19 |
| Drain Life Vulnerable | 2 | — | unchanged |
| Drain Life Weak | 2 | — | unchanged |
| Block gained, ever | 0 | 0 | 0 |

### 3.1 Per-turn incoming

Ignoring the Vulnerable window, the three moves average **(29 + 24 + 18) / 3 ≈ 23.7 per turn** at base ascension and **26 per turn** at Deadly Enemies. The spread is narrow — 18 to 29 — which is what makes this a flat tax rather than a spike profile. There is no turn where incoming is zero and no turn where it is double the average.

With the Vulnerable window folded in, the number rises. Drain Life lands Vulnerable 2, and the following two attacks are therefore taken at 1.5×:

| Sequence after a Drain Life | Damage taken |
| --- | --- |
| Soul Burn under Vulnerable | 43 (46 at Deadly) |
| Maelstrom under Vulnerable | 36 total, 9 per hit (42 / 10.5 at Deadly) |

Since Drain Life fires roughly every third turn and covers the two turns after it, **the party is Vulnerable for a majority of the fight** unless it can cleanse. Effective long-run incoming is closer to **30–33 per turn at base** and **33–36 at Deadly** than to the printed 23.7.

### 3.2 The clock

234 HP with zero block and zero healing is a short bar for an Act 3 elite — it is the *lowest* solo elite pool in the act. A party doing 40/turn kills it on turn 6 and eats roughly 150–180 total. A party doing 20/turn is there for 12 turns and eats 350+, which no Act 3 HP pool survives without mitigation. **The fight is decided almost entirely by the party's damage rate**, and Weak 2 on one turn in three is the monster's only lever on that rate — see §4.2.

## 4. Gimmicks

Soul Nexus is unusually gimmick-poor. What follows is the complete list.

### 4.1 Maelstrom is hidden from the bestiary

The monster explicitly suppresses the Maelstrom move from its bestiary entry; Soul Burn and Drain Life are listed, Maelstrom is not. A player who has scouted this elite in the bestiary sees a **two-move** attacker and will be surprised by the 4-hit in combat. The in-combat intent is honest — the multi-attack intent shows both the per-hit number and the ×4 — so the concealment is purely a first-encounter / metagame effect, not a hidden-information mechanic during the fight.

This is worth one line in a demand model only as a "first-run tax": players who plan around the bestiary will mis-size their first turn-2 block.

### 4.2 Drain Life is a debuff move that does not drain

Despite the name, **Drain Life heals the monster for nothing**. There is no lifesteal, no HP transfer, and no self-power application anywhere in the move — it deals 18 and then applies Vulnerable 2 and Weak 2. The name is flavour; a demand model that budgets for enemy healing here is wrong.

Both debuffs are applied to the **full player-creature list**, not to a single target. Both are the standard 2-turn-count versions: Vulnerable multiplies damage received by 1.5×, Weak multiplies damage dealt by 0.75×.

The Weak is the more interesting half. On a fight whose only real defence is the player's own clock, cutting party damage by 25% for two turns out of every three effectively **lengthens the fight by roughly 15–20%**, which converts directly into more turns of the flat tax. Weak here is not a defensive debuff, it is the monster's HP bar in disguise.

### 4.3 Multi-hit shape, not multi-target shape

Maelstrom is four separate 6-damage hits from one animation, not one 24. Against pooled Block the two are identical, but the four hits interact differently with anything per-hit: flat damage reduction (worth 4× as much), Thorns and on-hit retaliation (procs 4×), Intangible or Buffer-style effects (much worse per point absorbed), and any "when you are attacked" rider. This is the only move in the kit that asks a structurally different question of the player's defensive package.

### 4.4 Nothing else

No adds, no summons, no split, no revive, no artifact, no self-buff, no HP-threshold phase, no status cards, no card manipulation, no aggro or targeting choice. The corpse does not fade after death and the animation is swapped out on death and on removal from the room — visual only, no mechanical consequence. Whatever the party's AoE is worth, it is worth nothing here.

## 5. Scaling by act / ascension

- **By act:** none intrinsic. `SoulNexus` appears only in Glory (Act 3) and reads no act index directly. Act enters only through the multiplayer scaling constant (§6).
- **By ascension:** two binary gates, both narrow.
  - *Tough Enemies* (asc 8): HP 234 → 254. About +8.5%.
  - *Deadly Enemies* (asc 9): Soul Burn 29 → 31, Maelstrom 6 → 7 per hit (24 → 28 total), Drain Life 18 → 19. About +6–17% per move, ~+10% on average per-turn incoming. The Maelstrom **hit count is coded as an ascension-gated value but both branches are 4** — it does not actually change, and a model should treat the ×4 as constant.
  - **The debuffs never scale.** Vulnerable 2 and Weak 2 are identical at every ascension.
  - *Swarming Elites* (asc 1) changes how many elites the map contains, not this monster.
- **In-fight scaling: none.** No move gains damage, count, or strength over the course of the combat. The turn-20 Soul Burn is the same 29 as the turn-1 Soul Burn. This is the sharpest contrast with the act's other solo elites, whose threat curves rise.

## 6. Multiplayer / seat count

Headcount is absorbed entirely by the monster's HP; the encounter never adds bodies and the monster has no per-seat state.

- **HP scales by `player count × act constant`.** Act 3 **non-boss** uses **1.2**. So from a 234 base: **562** at 2 players, **842** at 3, **1,123** at 4. From the 254 Tough Enemies base: **610 / 914 / 1,219**.
- **Block scaling is irrelevant here** — the multiplayer scaling model also multiplies enemy monster-move block by the same factor, but Soul Nexus never gains block, so this fight gets none of the co-op wall that other Act 3 elites get. Co-op scaling for Soul Nexus is *purely* a longer HP bar.
- **Damage is NOT divided among seats.** All three attacks are built as monster attacks targeting *all opponents*, with the target list refreshed between hits. **Every player takes the full printed number every turn:** 29 each on Soul Burn, 6 ×4 each on Maelstrom, 18 each on Drain Life. A 4-player party absorbs 4× the printed damage.
- **The debuffs are party-wide, not single-target.** Drain Life applies Vulnerable 2 and Weak 2 to *every* player creature at any seat count. There is no per-seat roll and no split.
- No co-op-only moves, no aggro or threat mechanic, no target selection of any kind. The monster does not choose anyone.

Net co-op read: this fight scales **worse than linearly against the party** on the damage axis while gaining nothing defensively. Total incoming rises with headcount (each seat pays the full tax) *and* the bar the party must chew through rises by `headcount × 1.2` — but unlike the block-gaining elites, the party's added damage is not taxed on the way in. The binding constraint at 4 players is whether four separate HP bars can each absorb ~30/turn for the 8–12 turns it takes to clear 1,123 HP, with a party-wide Weak suppressing the clock for two turns in three.

## 7. Proposed fight class: `attrition`

Every move is an attack, the damage range is narrow (18–29 before Vulnerable), and the fight never presents a turn that can be safely skipped or a hit that must be specially prepared for — so the demand is the same demand, every single turn: **cover roughly 24–31 (36–43 while Vulnerable), then push damage with whatever is left.** That is the definition of a per-turn drain curve, and it is the whole fight.

The two debuffs reinforce the attrition reading rather than complicating it: Vulnerable raises the recurring bill the player was already paying, and Weak 2 on one turn in three suppresses the party's clock and therefore *adds turns* of that bill. Neither creates a burst the player must survive or a window the player must exploit. With no in-fight scaling anywhere, the fight also cannot become more dangerous over time — it can only last longer, which is the same thing said in attrition's language.

`spike` is wrong: the largest single number is 29 (43 through Vulnerable), it arrives with no windup, and the floor and ceiling are within a factor of 1.6 of each other. `mixed` is the runner-up on the strength of Maelstrom's 4-hit shape and the Drain Life debuff turn asking a slightly different question, but neither dominates a turn's decision-making the way a genuine second axis would. `swarm` and `gimmick` are trivially wrong — one body, no adds, and the only gimmick in the kit is a bestiary concealment with no in-combat effect.

A Track B demand curve for `SoulNexusElite` should be modeled as a **flat line at ~24 per turn base / ~26 at Deadly, uplifted to ~30–33 by the near-permanent Vulnerable window**, with **no slope**, **no zero-damage turns**, and a **25% player-damage suppression on ~2 turns in 3**. Length is the whole threat: the correct sensitivity parameter for this fight is the party's damage rate, not its peak block.
