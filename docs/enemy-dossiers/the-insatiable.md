# The Insatiable

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `TheInsatiable` (`MonsterModel`)
- **Kind:** boss
- **Act:** Act 2 — the Hive. One of the act's three boss options (`TheInsatiableBoss`), **first** in the act's boss discovery order, with its own act-2 boss BGM, custom background, custom ambience, and a slightly pulled-back camera (0.9× scaling).
- **Fight class:** `gimmick`

Behavioral notes only, reconstructed from decompiled sources. No code reproduced.

---

## 1. Shape of the encounter

A single-body boss. The encounter spawns exactly one Insatiable — no minions, no adds, no
summons, no revives. It has no block move, no artifact/thorns, and gains exactly one power on
itself (Strength). Everything distinctive about the fight lives in a power it puts on **you**.

Move selection is **fully deterministic**: the state machine is a pure follow-up chain with no
random or conditional branch states, so the intent order is byte-identical on every attempt.

## 2. Intent pattern / AI

```
LIQUIFY_GROUND -> THRASH -> LUNGING_BITE -> SALIVATE -> THRASH(2) -+
                    ^                                              |
                    +----------------------------------------------+
```

The machine starts on Liquify Ground and cannot transition away before performing its first
move, so **turn 1 is always Liquify Ground** and it never recurs. After that the fight is a
fixed 4-turn loop: Thrash → Bite → Salivate → Thrash. (Internally the two Thrash turns are
separate states with identical behavior; the second one is what closes the loop.)

| Enemy turn | Move | Telegraphed intent |
| --- | --- | --- |
| 1 | Liquify Ground | buff icon + status-card icon reading 6 |
| 2 | Thrash | multi-attack, 2 hits |
| 3 | Lunging Bite | single attack |
| 4 | Salivate | buff |
| 5 | Thrash | multi-attack, 2 hits |
| 6, 7, 8, 9 | Thrash / Bite / Salivate / Thrash | as above, forever |

Note the loop puts **two Thrash turns back to back** across the seam (turn 5 into turn 6), so
the post-Salivate Strength bump lands on a doubled 2-hit window.

## 3. Numbers

Base values, with the ascension-threshold value in parentheses:

| Stat | Base | At ascension threshold | Threshold |
| --- | --- | --- | --- |
| Initial HP | 321 (min == max, no roll) | 341 | Tough Enemies |
| Thrash | 8 × 2 hits = 16 | 9 × 2 = 18 | Deadly Enemies |
| Lunging Bite | 28 | 31 | Deadly Enemies |
| Salivate Strength gain | +2 | +3 | Deadly Enemies |
| Sandpit counter (Liquify) | 4 | unchanged | — |
| Frantic Escape statuses (Liquify) | 6 | unchanged | — |

Strength applies per hit, so each +2 is worth +4 on a Thrash turn and +2 on a Bite turn.
Cumulative pressure at base ascension, ignoring block:

| Enemy turn | Move | Strength | Damage | Running total |
| --- | --- | --- | --- | --- |
| 1 | Liquify | 0 | 0 | 0 |
| 2 | Thrash | 0 | 16 | 16 |
| 3 | Bite | 0 | 28 | 44 |
| 4 | Salivate | 0 → 2 | 0 | 44 |
| 5 | Thrash | 2 | 20 | 64 |
| 6 | Thrash | 2 | 20 | 84 |
| 7 | Bite | 2 | 30 | 114 |
| 8 | Salivate | 2 → 4 | 0 | 114 |
| 9 | Thrash | 4 | 24 | 138 |
| 10 | Thrash | 4 | 24 | 162 |
| 11 | Bite | 4 | 34 | 196 |
| 12 | Salivate | 4 → 6 | 0 | 196 |
| 13 | Thrash | 6 | 28 | 224 |

Per completed 4-turn loop entering at Strength *S*: `4×(8+S) + (28+S) = 60 + 5S`, with *S*
advancing in twos (threes at the Deadly Enemies threshold, on top of the +1/+3 per-hit bumps).
This is **not** a big-number boss by act-2 standards; the raw damage curve is gentle. The
lethality lives in §4.

## 4. Liquify Ground and the Sandpit — the gimmick

Turn 1 does no damage. It applies, **to every opposing creature**:

- **Sandpit**, a counter-stacking, instanced buff **owned by the boss but targeted at a specific
  player**, starting at **4**. It ticks down by 1 at the start of every *enemy* side turn.
- **Six copies of Frantic Escape**, a status card (cost 1, self-targeted, no upgrade level, and
  flagged so nothing else in the game can generate it). Three go into the draw pile and three
  into the discard pile, each at a random position. The local player gets a preview of the
  insertion.

**When the Sandpit counter reaches 0 the power is removed, and its removal handler kills the
targeted player outright** — a forced kill, along with that player's pets and Osty, with a
dedicated devour animation and finisher sound. This is not damage. It is not blockable, not
reducible, and being a forced kill it is not the ordinary lethal-damage path that
death-prevention effects sit on.

Playing a Frantic Escape does one thing: **+1 to your own Sandpit counter**, i.e. buy one more
enemy turn. Then that specific copy's energy cost permanently rises by 1 for the rest of the
combat. Six copies, all starting at 1, all reshuffled and replayable — so the escape economy is:

| Escapes bought | Cheapest cumulative energy | Enemy turns survivable |
| --- | --- | --- |
| 0 | 0 | 5 |
| 6 (each copy once, 1 each) | 6 | 11 |
| 12 (each copy twice, 1 then 2) | 18 | 17 |
| 18 (each copy three times) | 36 | 23 |

The clock, precisely: Liquify resolves on enemy turn 1 and sets 4. The tick happens at enemy
turn start, so the counter reads 3 on turn 2, 2 on turn 3, 1 on turn 4, and **0 at the start of
enemy turn 5 — you are eaten there** unless you have spent escapes. Baseline that is five player
turns to remove 321 HP, roughly 64 damage per turn, which no honest act-2 deck does. So escapes
are effectively mandatory, and the fight's true cost curve is *energy spent not killing*: the
first extra turn costs 1 energy, the seventh costs 2, the thirteenth costs 3, and so on. Every
purchased turn also feeds the Strength ramp in §3, so stalling is self-punishing at both ends.

Two safety details worth knowing:

- The devour handler no-ops if the boss is already dead or the target is already dead — so
  **killing the boss on the turn the counter would expire is safe**, and killing it at any point
  removes the Sandpit without eating anybody.
- Frantic Escape looks up "the enemy that has a Sandpit" and then the Sandpit instance whose
  target is the card's own owner, so in co-op a player can only extend their *own* timer. There
  is no way to donate turns.

## 5. Other flavor / state

- **Visual creep.** Sandpit continuously re-tweens the affected player (and their pets/Osty)
  toward the boss as the counter falls — the party is physically dragged into the pit, and the
  distance travelled is proportional to counter progress. Playing an escape visibly pushes you
  back out. Cosmetic, but it is the fight's readability layer: you can see how close you are
  without reading the counter.
- **Music telemetry.** A boss-progress music parameter tracks `6 − counter`, clamped to 0–5, so
  the score tightens as the pit closes, and jumps to 10 when the boss dies. Cosmetic.
- **Hurt animation flip.** An internal "has liquified" flag only chooses between two hurt
  animations (pre-liquify vs post-liquify). No mechanical effect.
- **Bestiary.** The devour finisher is injected as an extra bestiary entry ("Devour") even though
  it is not a move state — it is the removal handler, not something the boss telegraphs.
- **Damage SFX type is Insect.**

## 6. Multiplayer / seat count

- **HP scales with the party.** Act-2 multiplayer scaling multiplies boss HP by
  `playerCount × 1.2` (the 1.3 boss bonus applies to act 3 only). So ≈770 at two seats, ≈1156 at
  three, ≈1541 at four, before the Tough Enemies threshold.
- **All attacks hit every seat for full value.** Monster-sourced attacks here target all
  opponents with the list refreshed between hits, and neither Thrash nor Bite is flagged as
  randomly-targeted. Thrash's two hits and Bite's single hit land on everyone; the fight does not
  split damage across the party.
- **Every seat gets its own Sandpit and its own six statuses.** The counters are independent
  instances and tick independently, so seats can be eaten at different times, and a seat that
  runs out of escapes dies while the others fight on — the boss keeps its full HP pool either
  way. A devoured seat takes its pets and Osty with it.
- **No block scaling interaction.** The multiplayer scaling model exists to scale enemy block;
  the Insatiable never gains block, so that lever is inert here.

## 7. Proposed fight class: `gimmick`

The per-turn demand is dominated by one bespoke rule rather than by the damage on the board:
every turn you must decide how much of your energy to spend *not* killing the boss in order to
push back an unblockable countdown, and the price of that decision rises every time you pay it.
The attack numbers are modest for an act-2 boss (16–34 per turn on a gentle Strength ramp) and
block is close to irrelevant to the loss condition — you do not lose to chip damage, you lose to
a counter hitting zero. That makes the fight a bespoke throughput race with a built-in tempo tax:
Track B should model it as demanding raw damage-per-energy and status-pile resilience, not block
or sustain. `attrition` would be the second-best label — the Strength ramp and the escalating
escape cost do grind — but it would mis-state the ask, because the fight explicitly caps how long
you are allowed to grind.
