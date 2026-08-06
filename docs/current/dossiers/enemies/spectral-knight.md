# Spectral Knight

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `SpectralKnight` (`MonsterModel`, sealed)
- **Kind:** elite — one of three bodies in the `KnightsElite` encounter
- **Act:** Act 3 (Glory; act index 2). Appears nowhere else — no subclass, no event variant, no second encounter references it.
- **Encounter:** `KnightsElite` — always spawns exactly three monsters in fixed slots: `FlailKnight` (first), `SpectralKnight` (second), `MagiKnight` (third). Custom scene, camera at 0.87× scale pulled 50px down. Tagged `Knights`. The encounter preloads the `Hexed` affliction overlay art specifically for this monster.
- **Fight class:** `mixed`

Behavioral notes only, reconstructed from decompiled sources. No code reproduced.

---

## 1. What Spectral Knight is

Spectral Knight is the **debuff carrier** of the Act 3 knight trio, and the only body in the encounter that attacks the player's *deck* rather than the player's *HP bar*. Its entire identity is the opening move: a one-shot, never-repeated Hex that makes the party's cards Ethereal for the rest of the fight. After that it settles into a two-move attack rotation with no ramp, no block, no summons, no heal, no death rider, and no HP-threshold logic.

Its damage-taken sound profile is `Armor`, same as its packmates, so it reads as armoured despite gaining zero block.

Read against the pack: `FlailKnight` supplies the rising damage floor (Strength ramp), `MagiKnight` supplies the wall and the fight's one real spike (a 35/40 telegraphed bomb behind a Prep turn), and `SpectralKnight` supplies **the tax** — a permanent modifier on how the player is allowed to play, plus a mid-sized flat attack every turn.

## 2. Intent pattern / AI

Three moves, arranged as a **fixed two-turn opening followed by a two-way weighted branch**.

- **Turn 1 is always Hex.** The move machine is seeded on the Hex state and suppresses transitions until the first move has actually resolved, so the opening intent is deterministic: a Debuff intent, zero damage.
- **Turn 2 is always Soul Slash.** Hex's follow-up is hard-wired to Soul Slash — it is not a random branch. So the first attack always lands on turn 2 for the full single-hit number.
- **Turn 3 onward** both attacks funnel into a shared random branch that picks between them. Both branches carry **weight 1** and neither has a cooldown, so it is a flat 50/50 roll modified only by repeat limits:
  - *Soul Slash* is capped at **2 consecutive uses** — a third in a row is weighted to zero.
  - *Soul Flame* is `CannotRepeat` — it can never be played on two consecutive turns.
- **Hex is never reachable again.** Nothing in the machine branches back to the Hex state, and Hex is not in the random branch's option list. It fires exactly once per combat, on turn 1, and only that once. There is no re-application even if the player somehow clears the power.

| Move | Turn | Intent shown | Effect |
| --- | --- | --- | --- |
| **Hex** | 1 only, always | debuff (weak debuff icon, not "strong") | applies `HexPower` to **every player creature** |
| **Soul Slash** | 2 always, then repeatable ×2 | single attack | 15 damage (17 at Deadly Enemies) |
| **Soul Flame** | turn 3+, never twice in a row | multi-attack, 3 hits | 3 damage × 3 = 9 (4 × 3 = 12 at Deadly) |

The intent is always visible one turn ahead. The only planning information the branch gives is negative — *if it just flamed, it will slash next*; *if it has slashed twice, it will flame next* — which means the player can pin the next turn exactly **whenever the previous turn was Soul Flame or the second consecutive Soul Slash**. Roughly half the fight's turns are fully predictable one turn out.

Practical consequence for a demand model: **the damage band is extremely narrow and flat**. Once the fight is running, this body deals either 15 or 9 (17 or 12 at Deadly) and nothing else, forever, with no ramp of any kind. Expected damage per turn from turn 3 on is **12** (base) or **14.5** (Deadly). There is no burst turn and no scaling turn.

## 3. Numbers

| Stat | Base | Tough Enemies (asc 8) | Deadly Enemies (asc 9) |
| --- | --- | --- | --- |
| Initial HP | 93 (min == max, no roll) | 97 | — |
| Soul Slash damage | 15 | — | 17 |
| Soul Flame damage | 3 × 3 hits (9) | — | 4 × 3 hits (12) |
| Hex value applied | 2 | — | unchanged |
| Block gained, ever | none | — | — |
| Self-buffs, ever | none | — | — |

Sibling reference for the same encounter: `FlailKnight` 101 HP (108 Tough), `MagiKnight` 82 HP (89 Tough). Pack total is **276 HP solo** (294 at Tough Enemies); Spectral Knight is the **middle bar** at roughly 34%.

### 3.1 There is no scaling story

This is the flattest kit in the encounter. It gains no Strength, no Plating, no block, and it has no move whose value changes with turn count, HP remaining, seat count, or anything else. Every number above is a constant for the whole fight. A demand curve for this body alone is a horizontal line at ~12/turn after a zero-damage turn 1 and a 15 on turn 2.

The only thing that *does* change over the fight is the cumulative cost of the Hex, which is paid by the player's deck rather than the player's HP (§4).

## 4. Gimmicks

### 4.1 Hex — the whole monster

Hex applies a power to **each player creature independently** (the move iterates the full player-creature list, so in co-op every seat is hexed on turn 1). The power is a hidden-amount "Single" power — it is applied with a value of 2, that value propagates to the display amount on each afflicted card, but none of the observed logic reads the number. Treat Hex as **binary on/off**, not as a countdown or a stacking debuff.

What the power does:

- **On application, it afflicts every card the hexed player owns** — hand, draw, discard, exhaust, the entire card collection — with the `Hexed` affliction. Cards created or added to combat *afterwards* are afflicted as they enter, so there is no escaping it by generating fresh cards.
- **It only afflicts cards that have no affliction already.** A card already carrying some other affliction is skipped and stays un-hexed. This is the single exploitable seam in the mechanic: pre-existing afflictions act as Hex immunity for those specific cards.
- **Every Hexed card gains `Ethereal`** while the power exists. The keyword is granted dynamically by the power, not stamped onto the card, and it is gated per card on that card still carrying the Hexed affliction, and per player on ownership — so a hexed player's cards are Ethereal and nobody else's are.
- **Ethereal means: exhausted at end of turn if still in hand.** One nuance from the turn-end resolution order — cards that have their own end-of-turn-in-hand effect are handled on that branch instead and are *not* exhausted by Ethereal. Everything else left in hand is destroyed for the rest of the combat.
- **The power is removed when the Spectral Knight dies** (it self-removes on its applier's death, unless the death was prevented). Removal is clean and total: every Hexed affliction is cleared from every card, and because the Ethereal was granted dynamically, it evaporates with it — including on cards that were Ethereal from another source only by way of Hex. Ethereal from a genuinely independent source (a relic, a card's own printed keyword) is untouched.

### 4.2 What this actually demands of the player

- **Hand retention becomes impossible.** Any card held for a future turn is destroyed. Cost-reduction setups, "hold the big card until you have energy", retain-style planning, and drawing wide to bank options all stop working from turn 1 until this body is dead.
- **It is deck destruction, not just tempo.** Exhausted cards are gone for the whole combat, so every wasted card permanently thins what the player can draw on later turns of a three-body elite fight. The cost compounds even though the debuff itself never grows.
- **It creates a hard kill-order.** Killing the Spectral Knight is the only in-kit way to lift Hex, and doing so also restores the surviving cards to normal. That is a genuine target-priority puzzle — 93 HP is the middle bar, and the player must weigh burning it down early (stopping the card bleed but leaving Flail Knight free to ramp Strength) against killing Flail Knight first (capping the damage slope but paying Hex for longer).
- **It punishes wide draw and rewards dumping the hand.** The optimal play pattern under Hex is to empty the hand every turn, which pushes the player into low-value plays and away from setup — a real per-turn decision cost even on turns where the incoming damage is trivially blockable.

### 4.3 Multi-hit texture

Soul Flame is three separate damage instances that share **one** attack animation (the animation is explicitly played only once, so it reads visually as a single burst). Anything that triggers per incoming hit — thorns, per-hit retaliation, per-hit block erosion — fires three times on Flame turns and once on Slash turns. Conversely, flat per-hit damage reduction is dramatically more effective against Soul Flame: at 3 per hit, 2 points of per-hit reduction cuts the move from 9 to 3.

## 5. Scaling by act / ascension

- **By act:** none intrinsic. Act 3 only, and the monster never reads the act index. Act enters only through the multiplayer HP constant (§6).
- **By ascension:** two binary gates, both narrow, and **Hex is not one of them**.
  - *Tough Enemies* (asc 8): HP 93 → 97. About +4%, the smallest HP bump of the three knights.
  - *Deadly Enemies* (asc 9): Soul Slash 15 → 17 (+13%), Soul Flame 3 → 4 per hit, i.e. 9 → 12 per turn (+33%). Soul Flame takes the largest proportional ascension bump in the encounter, because a +1 on a 3-damage hit is a third more.
  - **The Hex value and its behaviour are ascension-invariant.** The defining mechanic is identical at ascension 0 and ascension 20; only the chip damage moves. Whatever difficulty this monster adds through Hex, it adds equally at every ascension.
  - *Swarming Elites* (asc 1) affects how many elites the map contains, not this monster's stats.

## 6. Multiplayer / seat count

- The encounter spawns exactly **three** monsters at any seat count. Headcount is absorbed by HP, not by adds.
- **HP** is multiplied by `player count × act constant`. Act 3 non-boss encounters use **1.2**. So: 93 solo, ~223 at 2 players, ~335 at 3, ~446 at 4 (Tough Enemies raises the base to 97 first, giving ~233 / ~349 / ~466). The whole knight pack runs ~276 solo to ~1,325 at 4 players.
- **Block scaling does not apply to this monster** — it never gains block. (Its packmate `MagiKnight`'s Power Shield block *is* scaled by the same factor.)
- **Damage is NOT divided among seats.** Both attacks are built as monster attacks targeting *all opponents*. **Every player takes the full printed number.** Soul Slash deals 15 to each seat independently; Soul Flame deals 3 × 3 to each seat independently. A 4-player party absorbs 4× the printed damage per turn from this one body.
- **Hex hits every seat.** The Hex move iterates all player creatures and applies a separate `HexPower` to each, so all seats are hexed on turn 1 and each seat's own card collection is afflicted. The Ethereal grant is ownership-gated per player, so the effects are parallel and independent rather than shared.
- **One kill lifts Hex for the entire party.** Every seat's `HexPower` names the same applier, so all of them self-remove the moment the Spectral Knight dies, and every hexed card in the party is cleared at once. This makes focus-firing this body a **party-wide** payoff that scales with seat count — the single most seat-count-sensitive decision in the encounter.
- The HP scaling therefore cuts both ways in co-op: the party wants this body dead early to stop four decks bleeding, but the bar it must chew through is ~4.8× as tall at 4 players while the reward for killing it (lifting Hex) does not scale.
- No co-op-only moves, no aggro/threat mechanic, no per-seat monster state.

## 7. Proposed fight class: `mixed`

Per turn, Spectral Knight asks two structurally different questions at once, and neither dominates. The damage question is pure `attrition` and unusually mild: a flat 9-or-15 band with no ramp, no spike, no block to punch through, and a turn-1 freebie — a demand curve for the attack half alone is a horizontal line at ~12/turn. But the Hex question is pure `gimmick`, and it is the reason the monster exists: from turn 1 the player loses hand retention entirely, every held card is permanently exhausted, and the deck thins for the rest of a three-body elite fight.

The gimmick also converts the encounter into a target-priority puzzle rather than a damage race, which is a per-turn decision cost the attack numbers completely fail to express. Killing this 93 HP body is the only way to lift the tax, and it competes directly against killing `FlailKnight` before its uncapped Strength ramp gets going — a genuine branching choice that a single-axis label would erase.

`mixed` is the honest call: a low, flat attrition floor bolted to a fight-defining deck-economy gimmick that fires once and never decays. A Track B curve for this body should carry a modest, low-variance damage line **plus** a step-function card-economy penalty starting at turn 1 and ending only on its death — not an averaged single number. Note also that the encounter it lives in is `mixed` for different reasons (`MagiKnight`'s 35/40 bomb supplies the spike beat, `FlailKnight` the rising floor), so the encounter-level label and this monster's label agree by coincidence, not by inheritance.
