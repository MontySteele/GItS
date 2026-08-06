# Lagavulin Matriarch

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `LagavulinMatriarch` (`MonsterModel`)
- **Kind:** boss (sole monster of the `LagavulinMatriarchBoss` encounter)
- **Act:** Act 2 — Underdocks (act index 1; one of the act's three boss options, third in the boss discovery order behind Waterfall Giant and Soul Fysh)
- **Fight class:** `mixed`

Behavioral notes only, reconstructed from decompiled sources. No code reproduced.

---

## 1. Shape of the fight

A single boss on a custom background, camera pulled slightly out (0.9× scaling), always
generated alone — no adds, no summons, no second body. The fight has two clearly separated
phases welded together by one power:

1. **Armored sleep** (opening, up to 3 enemy turns): she does literally nothing offensive
   while sitting behind a self-refreshing block engine.
2. **Awake cycle** (rest of the fight): a fixed 4-move rotation with a self-buff/player-debuff
   beat that compounds every lap.

The player controls when phase 2 starts, and the mechanism for starting it early is
"hit her hard enough to matter". That is the whole design.

## 2. Opening state: Asleep + Plating

On being added to the room she immediately puts herself to sleep. Two powers land on her
before the first player turn:

| Power | Amount | Behavior |
| --- | --- | --- |
| Plating | 12 | Counter-style buff. Grants block equal to its amount at the start of combat, and again at the end of every one of her turns. Ticks down by 1 per turn (per *player*, in co-op) starting from round 2. |
| Asleep | 3 | Counter-style buff. Ticks down at the end of each enemy turn. At 0 she wakes on her own. |

Presentation cues that read as mechanics but are not: closed-eye spine tracks, a sleeping
VFX plume, and a distinct "armor" damage sound. The sleep VFX is torn down the moment she
takes any damage at all, blocked or not — so the plume vanishing is *not* a reliable
"she woke up" signal.

A genuine tell does exist: **when her HP first drops to 50% or below she opens her eyes**
and stays eyes-open for the rest of the fight. This is a one-way visual latch, not a phase
change — no stats, moves, or numbers key off it.

### The wake condition

Sleep breaks on **unblocked damage**, not on damage. A hit that is fully eaten by her block
does nothing except cancel the sleep plume. The instant any damage gets through:

- her Plating is removed outright (the whole block engine, not one stack),
- she plays a wake sting and animation,
- she is **stunned for that turn** (a STUNNED move with a stun intent replaces whatever she
  had queued — which was the do-nothing Sleep move anyway, so she loses nothing),
- the move after the stun is forced to Slash,
- Asleep is removed.

If instead the Asleep counter simply expires, one further wrinkle fires: on the turn where
Asleep would drop to its last point, Plating is stripped at end of turn regardless. Either
route lands in the same place — she wakes with no armor and opens with Slash.

**Net player-facing rule:** chip damage into a sleeping Matriarch is pure waste (it is
absorbed by ~12 block that regenerates every turn), while a single burst over the block
threshold buys you nothing but an earlier start to her attack rotation. Since the Sleep move
deals zero damage, the optimal line is usually *not to attack her at all* for three turns and
spend them assembling a scaling engine. This is an inversion of the classic
"break the armor to stop the debuff" instinct — there is no passive penalty for letting her
sleep.

## 3. Intent pattern / move cycle

The state machine is deterministic — no RNG anywhere in her move selection.

Initial state is Sleep, whose follow-up is a conditional branch:

- if she still has Asleep → Sleep again
- if she does not → Slash

and from Slash the rotation is a fixed ring:

```
SLEEP → (branch) → SLASH → DISEMBOWEL → SLASH 2 → SOUL SIPHON → SLASH → ...
```

| Move | Intent shown | Effect |
| --- | --- | --- |
| Sleep | Sleep intent (hidden from the bestiary move list, but shown in combat) | nothing |
| Slash | single attack | one heavy hit |
| Disembowel | multi-attack (n × 2) | two hits, one animation |
| Slash 2 | single attack **+** defend | one hit, then she gains block |
| Soul Siphon | debuff **+** buff | −2 Strength and −2 Dexterity to the players, +2 Strength to herself |

Because the rotation is a ring with no re-entry into Sleep, she never sleeps again once
awake. The player therefore faces exactly one Soul Siphon per four turns, forever.

## 4. Numbers

Base (Ascension 0, single player):

| Stat | Value |
| --- | --- |
| Initial HP | 222 (min == max — no roll) |
| Slash damage | 19 |
| Disembowel | 9 × 2 hits (18 total) |
| Slash 2 damage | 12 |
| Slash 2 block | 12 |
| Soul Siphon | −2 Str / −2 Dex to players, +2 Str to self |
| Plating | 12 (≈12 block at combat start and at the end of each sleeping turn) |
| Asleep | 3 turns |

Every attack targets **all opponents** (see §6), and all attack numbers are pre-Strength —
her own Strength climbs by 2 per Soul Siphon, so the printed values are only the first lap.

Damage taken per rotation, single player, assuming Soul Siphon lands each lap:

| Lap | Slash | Disembowel | Slash 2 | Lap total | Player Str / Dex penalty carried |
| --- | --- | --- | --- | --- | --- |
| 1 | 19 | 9 × 2 = 18 | 12 | 49 | −2 / −2 |
| 2 | 21 | 11 × 2 = 22 | 14 | 57 | −4 / −4 |
| 3 | 23 | 13 × 2 = 26 | 16 | 65 | −6 / −6 |
| 4 | 25 | 15 × 2 = 30 | 18 | 73 | −8 / −8 |

Note the Disembowel line: because Strength applies per hit, her multi-attack grows twice as
fast as her single hits. By lap 3 the "small" move is her biggest turn.

## 5. Ascension scaling

Two ascension gates touch her, and neither is a modifier — each is a flat alternate value:

| Ascension gate | What changes | 0 → gated |
| --- | --- | --- |
| Tough Enemies | Initial HP | 222 → 233 |
| Tough Enemies | Slash 2 block | 12 → 14 |
| Deadly Enemies | Slash damage | 19 → 21 |
| Deadly Enemies | Slash 2 damage | 12 → 14 |
| Deadly Enemies | Disembowel per-hit damage | 9 → 10 (18 → 20 per use) |

Not scaled by ascension: Plating (12), Asleep duration (3), Disembowel hit count (2), and the
entire Soul Siphon package. The sleep puzzle and the compounding debuff are the same at every
ascension; only the raw pressure moves, and modestly — about +8% on the lap-1 damage total.

There is also a `Double Boss` ascension gate in the ladder generally; nothing in this
monster's own definition reacts to it, so any doubling is an encounter-layer concern rather
than a change to her behavior.

## 6. Multiplayer / seat count

This boss scales along four independent axes in co-op, and they compound:

- **HP.** Boss HP is multiplied by seat count *and* by the act's multiplayer factor. Underdocks
  is act index 1, factor **1.2**. So 222 → ~533 at 2 seats, ~799 at 3, ~1066 at 4 (Tough
  Enemies HP scales the same way from 233).
- **Attacks hit everyone.** Her attacks are built as monster attacks targeting all opponents,
  so Slash, Disembowel, and Slash 2 each land on *every* seat at full value — party-wide
  damage does not get divided.
- **Soul Siphon hits everyone.** The −2 Strength / −2 Dexterity is applied to the full target
  list, so each seat eats the full debuff each lap while she banks a single +2 Strength that
  then multiplies across all those targets.
- **Plating gets much bigger, and drains faster.** Plating is one of the powers that scales in
  multiplayer, using a (seats − 1) × 2 + 1 multiplier: 12 at 1 seat, **36** at 2, **60** at 3,
  **84** at 4. Its per-turn tick-down is also raised to the number of players, so the counter
  still burns at the same relative rate — but the block wall you would have to punch through to
  wake her early roughly triples per additional seat. Slash 2's move-block additionally passes
  through the general multiplayer block multiplier (seats × 1.2); Plating's own block grant does
  not double-dip, since the scaling is already baked into the amount.

Practical co-op consequence: waking her early goes from "a burst check" to "essentially
impossible at 3–4 seats", so co-op parties get the three free setup turns whether they want
them or not, then face a rotation that hits every seat for full.

## 7. Bestiary presentation

Her bestiary entry is hand-edited: the Sleep move is suppressed from the auto-generated move
list, and two entries are spliced in at the top — a "Sleep" demo that runs the actual
falling-asleep routine, and a "Wake Up" demo driven by the non-state wake action. The
remaining four moves come through normally. Worth noting because it means the sleep/wake pair
is authored as *presentation-visible content*, i.e. the designers expect the player to learn
the puzzle by looking at it.

## 8. Proposed fight class: `mixed`

The fight demands two different things at two different times, and neither dominates the
other. Turns 1–3 demand **zero** defense and pose a single burst-threshold question — clear
her block in one turn or don't bother — which is pure `gimmick` behavior with a
counterintuitive answer (attacking is usually the wrong play). From the wake onward it becomes
straightforward `attrition`: a deterministic, fully telegraphed 4-move ring that never varies,
delivering roughly 49 damage per 4 turns to start and growing ~8 damage per lap on her side
while stripping 2 Strength and 2 Dexterity per lap from yours, so the player's mitigation
budget shrinks on the same clock her damage grows. Labeling it `spike` would misread her —
no single hit is the threat; labeling it `gimmick` would drop the compounding-clock demand
that actually kills players. `mixed` is the honest bucket, and Track B should model it as a
flat-zero demand window followed by a super-linear attrition ramp rather than an average of
the two.
