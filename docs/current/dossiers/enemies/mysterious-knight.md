# Mysterious Knight

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `MysteriousKnight` (subclass of `FlailKnight`, which is a `MonsterModel`)
- **Kind:** elite — elite-grade body, but fought in a `Monster`-room encounter (`MysteriousKnightEventEncounter`) reached through an event, not from an elite map node
- **Act:** Act 2 (Hive; act index 1)
- **Encounter:** `MysteriousKnightEventEncounter` — always exactly one monster, no scene overrides, no camera overrides, no tags. Entered from **The Lantern Key** event ("keep the key" → fight).
- **Fight class:** `attrition`

Behavioral notes only, reconstructed from decompiled sources. No code reproduced.

---

## 1. What Mysterious Knight is

Mysterious Knight is a **pre-buffed solo re-skin of Act 3's Flail Knight, dropped into Act 2**. It inherits the parent body wholesale — same HP, same three moves, same random branch, same animation set, same armored damage-taken sound — and overrides exactly one thing: an on-spawn package applied to itself before the first turn.

That package is the whole design:

- **+6 Strength**, permanent.
- **6 Plating**, a decaying self-block engine.

So the player meets an Act 3 elite's body an act early, alone, already two War Chants ahead of schedule, and wearing armour that Flail Knight never has. Nothing else about the kit differs — no new move, no phase, no death rider, no summon, no conditional logic.

It is also the only monster in the game gated behind an *optional* event fight, which matters for a demand model: the party chooses to take it, usually from full-ish resources, and the alternative is 100 gold.

## 2. Intent pattern / AI

Identical machine to `FlailKnight`: a **three-way weighted random branch with repeat limits**, not a fixed cycle. Every move funnels back into the same branch node.

- **Turn 1 is always Ram.** The machine is seeded on the Ram state, and the state machine suppresses transitions until the first move has actually been performed. Opening intent is deterministic.
- From turn 2 on, the branch picks uniformly among **War Chant**, **Flail**, and **Ram** — all three weights are 1, none has a cooldown.
- **Repeat limits** are the only structure:
  - *War Chant* can never be played on two consecutive turns.
  - *Flail* and *Ram* are each capped at **2 consecutive uses**; a third in a row is weighted to zero.
- The repeat check reads the monster's move log; War Chant occupies a log slot, so a chant **breaks** a Flail or Ram streak and resets its counter.

| Move | Intent shown | Effect (at spawn, +6 Strength) |
| --- | --- | --- |
| **Ram** (opener, repeatable ×2) | single attack | **21** damage (23 at Deadly Enemies) |
| **Flail** (repeatable ×2) | multi-attack, 2 hits | **15 × 2 = 30** (16 × 2 = 32 at Deadly) |
| **War Chant** (never twice in a row) | buff | +3 Strength, permanent, uncapped — worth **+3 to Ram, +6 to Flail** |

No HP-threshold phase change, no enrage, no first-turn-only move beyond the seeded Ram, nothing the player can steer. Intent is always visible one turn ahead. The only planning information is negative: *if it just chanted it will not chant again*, and *if it has used the same attack twice, that attack is off the table next turn*.

Consequence for a demand model: the **two-turn worst case is bounded** (Flail+Flail), and no single turn can be a burst. Its scariest number is available on turn 2 and only creeps upward from there.

## 3. Numbers

| Stat | Base | Tough Enemies (asc 8) | Deadly Enemies (asc 9) |
| --- | --- | --- | --- |
| Initial HP | 101 (min == max, no roll) | 108 | — |
| Starting Strength | +6 (self-applied on spawn) | — | unchanged |
| Starting Plating | 6 (self-applied on spawn) | — | unchanged |
| Ram base damage | 15 → **21** with start Strength | — | 17 → **23** |
| Flail base damage | 9 × 2 → **15 × 2** with start Strength | — | 10 × 2 → **16 × 2** |
| War Chant Strength gain | +3 | — | unchanged |

### 3.1 Effective HP

Plating is not a flat +6. It grants Block **equal to its current amount** both once at the start of combat (round 1 only) and at the end of every one of the monster's turns, then decays by 1 at the start of each subsequent turn. Solo, that is 6 up front, then 6 / 5 / 4 / 3 / 2 / 1 at successive turn ends, expiring after ~6 turns:

**≈ 27 block total**, front-loaded, on top of a 101 HP bar — roughly a **128 effective-HP** fight if the party's damage is spread evenly, and rather less if the party can burst through a block layer in one turn (unspent block does not carry).

The block is granted as an unpowered value, so it is not further multiplied by the player's own block-scaling interactions or by the multiplayer block constant; the co-op growth comes from the Plating amount itself (§6).

### 3.2 The Strength ramp

Strength is applied additively per **powered attack hit**, so the 2-hit Flail double-dips every stack:

- Ram at Strength *S* deals `15 + S`.
- Flail at Strength *S* deals `2 × (9 + S)` = `18 + 2S`.

Mysterious Knight starts at *S* = 6 rather than 0. Expected damage per turn at Strength *S*, treating the three branches as equally likely and ignoring the repeat clamps, is **11 + S** — i.e. **17/turn at spawn**, rising by roughly **+1 per turn** as chants land about one turn in three.

Approximate incoming curve: ~21 on turn 1 (deterministic Ram), ~17 average on turn 2, ~22 by turn 7, ~27 by turn 12. Against a 128-effective-HP bar, a party that cannot clear it inside roughly 6–8 turns is losing the race, and the ~27 block it grants over exactly that window is precisely calibrated to lengthen the fight into the ramp.

Comparison anchors for Act 2: this is a single body doing **21–30 per turn from turn 1**, with a defensive layer. That is elite-tier pressure arriving in the act's normal-encounter pool.

## 4. Gimmicks

### 4.1 Spawn package, not a mechanic

There is no unique power here — Strength and Plating are both vanilla. What is unusual is *when* they arrive: applied by the monster to itself immediately on being added to the room, before any intent is rolled. Practically, this means:

- The fight has **no ramp-up phase**. Flail Knight spends its early turns building to numbers Mysterious Knight opens with.
- Anything the player has that strips or reverses Strength is worth far more here than against the parent (a −6 is a full third of the fight's damage output at spawn, and Strength has no floor protection in this kit — it allows negative values).
- Plating is a *counter*, not a duration: reducing or removing the counter kills both the per-turn block and its remaining lifetime at once.

### 4.2 Multi-hit vs. per-hit effects

Flail is two separate damage instances that share one attack animation (the animation is explicitly played once, so it visually reads as a single swing while two hits resolve). Per-hit player effects — thorns, per-hit retaliation, per-hit block erosion — fire twice on Flail turns and once on Ram turns; flat per-hit damage reduction is twice as effective against Flail.

Because Strength scales per hit, the Flail/Ram gap **widens** over the fight: 30 vs 21 at spawn, 36 vs 24 after one chant, 42 vs 27 after two. Unlike the parent (where turn-1 Ram is the bigger number), here Flail is already the more dangerous roll from the first branch onward.

### 4.3 The Lantern Key wrapper

The fight is the second branch of **The Lantern Key**, an Act 2 shared event (all seats resolve it together):

- **Return the key** → 100 gold to the party, event ends. No fight.
- **Keep the key** → a confirmation page, then combat, entered without exiting the event and with no post-combat return to the event.
- Reward: **one `LanternKey` special card per player**, granted as the combat's reward, in addition to normal combat rewards.

`LanternKey` is an unplayable Quest-rarity card with no upgrade level and no cost. Its entire function is map-level and act-delayed: while a player holds it, **in Act 3 (act index 2)** it forces unknown map points to resolve as **Event** rooms, and it replaces the next event with the **War Historian Repy** event. The run tracks separately whether the party freed Repy.

So the demand model should treat this as a **paid-in-blood key to an Act 3 content branch**, not a loot fight. The reason a party takes it is not gold or a card pick — it is access.

## 5. Scaling by act / ascension

- **By act:** none intrinsic. Mysterious Knight is Act 2 only; the parent body is Act 3 only. The monster never reads the act index. Act enters only through the multiplayer HP/block constant (§6), which for Act 2 is **1.2**.
- **By ascension:** two binary gates, both narrow, both inherited unchanged from the parent.
  - *Tough Enemies* (asc 8): HP 101 → 108, about +7%.
  - *Deadly Enemies* (asc 9): Ram 15 → 17, Flail 9 → 10 per hit. With the +6 start, that is 21 → 23 and 30 → 32 — about **+9% and +7%** on the numbers the player actually sees, i.e. the ascension bump is *diluted* by the spawn Strength relative to how it hits the parent.
  - **Neither the +6 Strength, the 6 Plating, nor War Chant's +3 is ascension-gated.** The ramp slope and the armour layer are identical at every ascension; only a thin baseline moves. Ascension shortens the front half of the fight's clock and does nothing to its long-fight behaviour.

## 6. Multiplayer / seat count

- The encounter spawns **one** monster at any seat count. Headcount is absorbed by HP and Plating, never by adds.
- **HP** is multiplied by `player count × 1.2` (the Act 2 constant): **101 solo, ~242 at 2 players, ~364 at 3, ~485 at 4** (Tough Enemies raises the base to 108 first).
- **Plating scales hard, and its decay scales too.** The applied amount is multiplied by `(players − 1) × 2 + 1` — **6 solo, 18 at 2 players, 30 at 3, 42 at 4** — while the per-turn decay rises from 1 to the player count. Net: a much taller but proportionally shorter armour window. At 3 players it is 30 block per turn for ten turns' worth of counter decaying 3/turn; at 4, 42 decaying 4/turn. Total block granted grows roughly with the square of seat count while the party's damage grows only linearly, so **the armour layer is the single most punishing co-op term in the fight.**
- **Strength does not scale with seat count.** It stays +6 on spawn and +3 per chant regardless of party size.
- **Damage is NOT divided among seats.** Both attacks target all opponents, target list refreshed between hits. **Every player takes the full printed number** — Flail is 15 × 2 to each seat independently, Ram is 21 to each seat independently. A 4-player party absorbs 4× the printed damage per turn from this one body, and each chant is worth +24 party-wide on a Flail turn.
- The event itself is **shared** (one resolution for the whole party), and the `LanternKey` reward is minted **per player**, so every seat carries the Act 3 map override independently.
- No co-op-only moves, no aggro/threat mechanic, no per-seat state.

## 7. Proposed fight class: `attrition`

Per turn this fight asks one question and repeats it: *can you cover 21–30 incoming while chewing through a block layer that regenerates every turn?* There is no telegraphed bomb to bank for, no debuff tax, no kill-order or targeting decision, no summons, and — because War Chant can never double and neither attack can triple — no turn that can spike beyond the band the player already saw on turn 1. The variance is in *which* of two similar attack numbers lands, not in magnitude.

What makes it lethal is duration on both sides of the ledger. The +6 spawn Strength removes the parent's ramp-up grace so the pressure floor is high immediately, and War Chant then adds a permanent, uncapped, ascension-invariant **+1/turn slope** on top; meanwhile Plating adds ~27 block solo (and a square-scaling wall in co-op) whose only purpose is to buy the ramp more turns. The two halves of the spawn package are the same lever pointed in opposite directions: one raises the damage the player must survive per turn, the other raises the number of turns they must survive.

`attrition` is the honest label. A Track B demand curve for this fight should be a **high-intercept rising line with low variance** — start the demand near an elite's steady-state number rather than at zero, and slope it upward — with a co-op correction applied to the *required-damage* axis rather than the survival axis, since seat count inflates the wall far faster than it inflates the incoming-per-seat.
