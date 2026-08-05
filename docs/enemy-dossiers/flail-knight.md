# Flail Knight

- **Class:** `FlailKnight` (`MonsterModel`)
- **Kind:** elite — one of three bodies in the `KnightsElite` encounter
- **Act:** Act 3 (Glory; act index 2). Its subclass `MysteriousKnight` also appears in **Act 2** (Hive) as the combat half of the `TheLanternKey` event — see §4.2.
- **Encounter:** `KnightsElite` — always spawns exactly three monsters in fixed slots: `FlailKnight` (first), `SpectralKnight` (second), `MagiKnight` (third). Custom scene, camera at 0.87× scale pulled 50px down. Tagged `Knights`.
- **Fight class:** `attrition`

Behavioral notes only, reconstructed from decompiled sources. No code reproduced.

---

## 1. What Flail Knight is

Flail Knight is the plain-bodied bruiser of the Act 3 knight elite trio. It has the largest HP pool of the three, an armored damage-taken sound profile, and a kit with **no block, no debuff, no summons, and no conditional logic** — three moves, one of which is a permanent self-Strength buff, and that is the whole monster.

Read next to its packmates, the division of labour is clear: `SpectralKnight` supplies the debuff (Hex) and the 3-hit chip; `MagiKnight` supplies the defensive wall, the Dampen debuff, and the fight's single genuine spike (a 35/40 telegraphed bomb behind a Prep turn); `FlailKnight` supplies the **floor** — a damage number that is always present, never zero for two turns running, and quietly rising.

It is also the only one of the three that is reused elsewhere, via subclass.

## 2. Intent pattern / AI

The move machine is a **three-way weighted random branch with repeat limits**, not a fixed cycle. Every move funnels into the same branch node, and the branch picks the next move.

- **Turn 1 is always Ram.** The machine is seeded on the Ram state and the state machine suppresses transitions until the first move has actually been performed, so the opening intent is deterministic: a single 15 (17 Deadly) attack.
- From turn 2 on, the branch chooses uniformly among **War Chant**, **Flail**, and **Ram** — all three branches carry weight 1, and no branch has a cooldown.
- **Repeat limits** are the only structure:
  - *War Chant* is `CannotRepeat` — it can never be played on two consecutive turns.
  - *Flail* and *Ram* are each capped at **2 consecutive uses**; a third in a row is weighted to zero.
- The repeat check reads the monster's own move log, and War Chant occupies a slot in that log. So a War Chant **breaks** a Flail or Ram streak and resets its counter.

| Move | Intent shown | Effect |
| --- | --- | --- |
| **Ram** (opener, and repeatable ×2) | single attack | 15 damage (17 at Deadly Enemies) |
| **Flail** (repeatable ×2) | multi-attack, 2 hits | 9 damage × 2 (10 × 2 at Deadly) |
| **War Chant** (never twice in a row) | buff | gains **+3 Strength**, permanent, unbounded |

There is no HP-threshold phase change, no enrage, no first-turn-only move, and nothing the player can do to steer the roll. The intent is always visible one turn ahead, and the only planning information it gives you is negative: *if it just chanted, it will not chant again next turn*, and *if it has attacked with the same move twice, that move is off the table*.

Practical consequence for a demand model: the **worst two-turn window is bounded**. Because War Chant can't double and the attacks can't triple, the maximum incoming across any two consecutive turns is Ram+Ram or Flail+Flail — there is no way for this monster to produce a genuine burst turn.

## 3. Numbers

| Stat | Base | Tough Enemies (asc 8) | Deadly Enemies (asc 9) |
| --- | --- | --- | --- |
| Initial HP | 101 (min == max, no roll) | 108 | — |
| Ram damage | 15 | — | 17 |
| Flail damage | 9 × 2 hits | — | 10 × 2 hits |
| War Chant Strength gain | +3 | — | unchanged |
| Block gained, ever | none | — | — |

Sibling reference for the same encounter: `SpectralKnight` 93 HP (97 Tough), `MagiKnight` 82 HP (89 Tough). Pack total is **276 HP solo** (294 at Tough Enemies), of which Flail Knight is the largest single bar — roughly 37%.

### 3.1 The Strength ramp is the whole scaling story

Strength is applied additively per **powered attack hit**, so the 2-hit Flail double-dips every stack:

- Ram at Strength *S* deals `15 + S`.
- Flail at Strength *S* deals `2 × (9 + S)` = `18 + 2S`.

Each War Chant is therefore worth **+3 to Ram and +6 to Flail**, permanently, and Strength is never removed or capped by anything in the kit.

Expected damage per turn at Strength *S*, treating the three branches as equally likely and ignoring the repeat clamps:

`(0 + (18 + 2S) + (15 + S)) / 3` = **11 + S** per turn (base ascension), or **12.3 + S** at Deadly Enemies.

Because War Chant comes up roughly one turn in three and pays +3, Strength climbs by about **+1 per turn on average**. So the expected incoming curve is approximately **11 + n** on turn *n*: ~12 on turn 2, ~16 by turn 5, ~21 by turn 10. This monster does not spike — it *drifts upward until it kills you*. A party that cannot kill 101 HP inside roughly 6–8 turns is fighting a materially different monster by turn 12.

The repeat clamps flatten the curve slightly relative to the naive average: they suppress long attack streaks (mildly reducing damage) and also suppress consecutive chants (mildly reducing the ramp), and roughly cancel.

## 4. Gimmicks

### 4.1 None, in the strict sense

Flail Knight has no unique power, no positional rule, no death rider, no summon, no shared resource with its packmates, and no interaction with the encounter's `Hexed` affliction (that overlay is preloaded by the encounter for `SpectralKnight`'s Hex). It applies exactly one power in its entire kit, to itself, and that power is vanilla Strength.

Two soft mechanical textures are worth carrying into a model anyway:

- **Multi-hit vs. per-hit effects.** Flail is two separate damage instances that share one attack animation (the animation is explicitly played only once, so the visual reads as a single swing while two hits resolve). Anything the player has that triggers per incoming hit — thorns, per-hit retaliation, per-hit block loss — fires twice on Flail turns and once on Ram turns. Conversely, flat per-hit damage reduction is twice as effective against Flail.
- **Ramp asymmetry punishes multi-hit-mitigation planning.** Because Strength scales per hit, the gap between Flail and Ram *widens* over the fight: at Strength 0 they are 18 vs 15; at Strength 9 they are 36 vs 24. Late in a long fight, Flail is by far the more dangerous roll, which inverts the early-fight read where Ram is the bigger number.

### 4.2 `MysteriousKnight` — the Act 2 event variant

`MysteriousKnight` is a direct subclass of `FlailKnight`. It inherits the HP, the three moves, and the branch structure unchanged, and adds an on-spawn package applied to itself before the first turn:

- **+6 Strength** at combat start. Turn-1 Ram is therefore **21** (23 at Deadly), and Flail is **15 × 2 = 30**. It effectively begins the fight two War Chants ahead, and continues to chant on top of that.
- **6 Plating.** Plating grants block equal to its current amount at combat start *and* at the end of every one of the monster's turns, then decays. Solo, it decays by 1 per turn, so it supplies 6, 5, 4, 3, 2, 1 block on successive turns — about **21 block total** spread across the first six turns, which is meaningful against a 101 HP bar.

It is fought alone (single-monster encounter, `Monster` room type) as the "keep the key" branch of **The Lantern Key**, an Act 2 (Hive) shared event; declining hands the party 100 gold instead, and taking the fight rewards a `LanternKey` special card per player. So the same body appears an act early, solo, pre-buffed, and with a defensive layer it otherwise never has.

## 5. Scaling by act / ascension

- **By act:** none intrinsic. `FlailKnight` is Act 3 only; `MysteriousKnight` is Act 2 only. Neither reads the act index directly — act only enters through the multiplayer HP/block constant (§6).
- **By ascension:** two binary gates, both narrow.
  - *Tough Enemies* (asc 8): HP 101 → 108. Roughly +7%.
  - *Deadly Enemies* (asc 9): Ram 15 → 17, Flail 9 → 10 per hit (18 → 20 per turn). Roughly +13% on both attacks.
  - **War Chant's +3 is not ascension-gated.** The ramp *slope* is identical at every ascension; only the baseline moves. This is the opposite of several Act 2 elites/bosses whose buff move gets bumped — Flail Knight's long-fight behaviour is ascension-invariant, and the ascension gates only shorten the clock on the front half of the fight.
  - *Swarming Elites* (asc 1) affects how many elites the map contains, not this monster's stats.

## 6. Multiplayer / seat count

- The encounter spawns exactly **three** monsters at any seat count. Headcount is absorbed by HP, not by adds.
- **HP** is multiplied by `player count × act constant`. Act 3 non-boss encounters use **1.2**. So Flail Knight is 101 solo, ~242 at 2 players, ~364 at 3, ~485 at 4 (Tough Enemies raises the base to 108 first). The whole knight pack runs ~276 solo to ~1,325 at 4 players.
- **Block scaling does not apply to this monster** — it never gains block. (Its packmate `MagiKnight`'s Power Shield block *is* scaled by the same factor, so the pack's effective wall grows with seat count even though Flail Knight's does not.)
- **Damage is NOT divided among seats.** Both attacks are built as monster attacks targeting *all opponents*, with the target list refreshed between hits. **Every player takes the full printed number.** Flail deals 9 × 2 to each seat independently; Ram deals 15 to each seat independently. A 4-player party absorbs 4× the printed damage per turn from this one body.
- **Strength is shared across all of that.** One War Chant is worth +3 to every seat's Ram and +6 to every seat's Flail — i.e. **+24 party-wide damage per chant at 4 players** on a Flail turn. The ramp is the single most seat-count-sensitive thing in the fight, and it is exactly the thing ascension does not touch.
- `MysteriousKnight`'s Plating scales up hard in co-op: its granted block is multiplied by `(players − 1) × 2 + 1` (6 → 18 at 2 players, 30 at 3, 42 at 4), while its per-turn decay increases to the player count. Net: a much taller but much shorter-lived armour window at high seat counts.
- No co-op-only moves, no aggro/threat mechanic, no per-seat state of any kind.

## 7. Proposed fight class: `attrition`

Per turn, Flail Knight asks the player exactly one question — *can you cover 11 + n incoming, this turn and every turn* — and it never asks anything else. There is no defensive wall to break through, no debuff tax on the player's output, no telegraphed burst to bank block for, no kill-order trap, and no positional or targeting decision. The move roll is random but the *magnitude band is narrow*: the repeat clamps guarantee no move triples and War Chant never doubles, so the two-turn worst case is bounded and no single turn can be a spike.

What makes it dangerous is duration, not any one turn. The +3 Strength on roughly a third of its turns is permanent, uncapped, applied per hit (so the 2-hit Flail doubles it), and — uniquely — not gated behind any ascension. That converts a flat ~11/turn floor into a slope of roughly +1/turn, and in co-op multiplies straight across all seats since every attack hits the whole party for full.

`attrition` is the honest label: this is a sustained-mitigation-or-race-the-clock body, and a Track B demand curve for it should be a rising line with low variance, not a sawtooth. The caveat to carry forward is that the *encounter* it lives in is `mixed` — `MagiKnight`'s 35/40 bomb supplies the spike beat and `SpectralKnight` supplies the debuff tax — so a per-fight-class curve built from `KnightsElite` as a whole should not inherit this monster's label. Flail Knight is the encounter's baseline, and the baseline is pure attrition.
