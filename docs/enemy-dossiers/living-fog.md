# Living Fog

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `LivingFog`
- **Kind:** normal
- **Act:** 1 (Underdocks, act index 0)
- **Encounter:** `LivingFogNormal` — six slots (`bomb1`–`bomb5`, `livingFog`); only the Living Fog is generated at combat start, the five bomb slots are reserved for the minions it summons
- **Fight class:** **mixed**

> Behavioral notes only — derived from decompiled behavior, no source reproduced.

## Where it appears

Living Fog is an ordinary Act 1 monster encounter in the Underdocks pool. The encounter has a
dedicated background scene, a camera pulled slightly back (0.9× scaling) to fit the bomb row, and it
always spawns exactly one Living Fog into the `livingFog` slot. It preloads the **Smog** affliction
overlay as an extra asset, which is the encounter telling you up front what the fight is actually
about. Its take-damage sound family is "magic", and neither it nor its bombs fade out on death.

## Intent pattern

Fully deterministic. There is no RNG anywhere in the move machine, no HP threshold, no phase change,
and no conditional branch — the state graph is a fixed opener into a hard two-beat alternation.

| Beat | Move | What it does | Intent shown |
|---|---|---|---|
| 1 (always) | **Advanced Gas** | Attack, then applies **Smoggy** to every player | attack + card-debuff |
| 2 | **Bloat** | Summons **1 Gas Bomb** into the next free bomb slot, then attacks | attack + summon |
| 3 | **Super Gas Blast** | Attack only | attack |
| 4 | **Bloat** | as beat 2 | attack + summon |
| 5 | **Super Gas Blast** | as beat 3 | attack |
| … | Bloat / Super Gas Blast alternating forever | | |

Structural consequences worth modelling:

- **Advanced Gas fires exactly once, on turn 1, and never again.** Nothing in the graph routes back
  to it. The Smoggy debuff it applies is a single-stack permanent power that is never removed, so one
  application is all the fight needs — the debuff is front-loaded and then simply *is* the fight.
- **The rest of the fight is a perfectly readable 2-turn metronome:** summon-and-poke, then a bigger
  hit while last turn's bomb goes off. Nothing is hidden and nothing is random, so the player's whole
  planning problem is a known repeating cost, not a guessing game.
- The fog performs its first rolled move without transitioning (standard first-move guard), which is
  what pins Advanced Gas to turn 1.
- **Bloat summons exactly one bomb per cast** (the summon count is a fixed field, set to 1 and never
  modified by anything in the fight). It looks for the first unoccupied slot in the encounter's slot
  list; if every bomb slot were occupied it would silently skip the summon and still throw its
  attack. In practice this never happens — bombs always die on their own next turn, so at most one
  bomb is alive at a time.

## Damage / HP numbers

| Stat | Base | Ascension |
|---|---|---|
| Living Fog HP (min = max, no roll) | **80** | **82** (A8 `ToughEnemies`) |
| Advanced Gas damage | 8 | 9 (A9 `DeadlyEnemies`) |
| Advanced Gas rider | Smoggy (1, single stack) to **all players** | unchanged |
| Bloat damage | 5 | 6 (A9 `DeadlyEnemies`) |
| Bloat rider | +1 Gas Bomb | unchanged |
| Super Gas Blast damage | 8 | 9 (A9 `DeadlyEnemies`) |
| Gas Bomb HP | 7 | 8 (A8 `ToughEnemies`) |
| Gas Bomb explosion | 8 | 9 (A9 `DeadlyEnemies`) |

Living Fog gains **no block at any point**, gains no Strength, and applies no HP-side debuffs. Its
entire kit is three flat attacks plus one card-layer debuff plus a bomb generator. Nothing about it
ramps: the turn-8 numbers are the turn-2 numbers.

Base-difficulty solo projection, assuming the player never kills a bomb:

| Turn | Living Fog | Bomb activity | Damage taken |
|---|---|---|---|
| 1 | Advanced Gas | — | 8 (+ Smoggy for the rest of the fight) |
| 2 | Bloat | bomb A spawns | 5 |
| 3 | Super Gas Blast | bomb A explodes, then dies | 8 + 8 = **16** |
| 4 | Bloat | bomb B spawns | 5 |
| 5 | Super Gas Blast | bomb B explodes | 16 |
| 6 | Bloat | bomb C spawns | 5 |
| 7 | Super Gas Blast | bomb C explodes | 16 |

Steady state is **21 damage per 2 turns (10.5/turn)** ignored, or **13 per 2 turns (6.5/turn)** if the
player spends 7 damage each cycle popping the bomb before it detonates. That is the fight's core
trade and it is priced almost exactly at par: 7 damage buys 8 prevented, every cycle, forever. On A9
the trade is 7 damage for 9 prevented (or 8 for 9 at A8+A9), so it tilts slightly *toward* killing
bombs as ascension rises. Meanwhile the 80 HP body means a deck doing ~15/turn ends this in six
turns; every point diverted to bombs pushes that out.

## Gimmicks

### Smoggy → Smog: one Skill per turn, permanently

The turn-1 debuff is the fight's identity and it operates entirely on the card layer.

- **Trigger:** the moment a player plays a **Skill**, every Skill anywhere in that player's combat
  card pool that has no affliction already gets afflicted with **Smog**.
- **Effect of Smog:** an afflicted card is blocked from being played — the affliction hooks the
  general playability gate, so it is not a cost increase or a discard, it is a hard "no".
- **Leak-proofing:** any Skill that *enters* combat later in the same turn (drawn, created, added) is
  also smogged on arrival, provided a Skill was already played that turn. There is no drawing your
  way out of it.
- **Reset:** all Smog is cleared at the end of the afflicted player's turn.

Net rule in play: **you may play exactly one Skill per turn, every turn, for the whole fight.**
Attacks and Powers are untouched. Smoggy is a single-stack debuff that nothing in the fight removes,
so there is no "wait it out" and no stacking escalation — it is a binary switch flipped on turn 1.

Design consequences:

- Skill-dense decks (block-stacking, draw engines, cheap-utility chains) lose most of their turn.
  Attack-dense and Power-dense decks barely notice.
- Because the block half of most decks lives in Skills, capping Skills at one per turn is
  functionally a *defensive* cap — which is why the raw incoming numbers can stay modest and still
  bite.
- Order of play matters within a turn: the smog fires on the *first* Skill played, so the player must
  pick their one Skill deliberately rather than sequencing into it.

### Gas Bombs: a per-cycle, self-resolving kill target

Each Bloat drops a 7 HP bomb with exactly one move in its whole state machine: explode for 8, then
kill itself. It telegraphs with a distinct **death-blow** intent, so the player always sees the
detonation coming a full turn ahead.

- It carries **Minion**: its death does not trigger the fatal/victory check and it is flagged as a
  secondary enemy, so combat ends when the fog dies regardless of bombs on the board.
- The minion tag survives its own death.
- Killing it early is a pure damage trade (7 in, 8 out) that also denies nothing else — the fog does
  not care, does not retaliate, and summons another one two turns later.
- The bomb dies on its own after detonating, so the board never accumulates. Five bomb slots exist
  but the fight, left alone, uses one at a time.

The two gimmicks interact: the bomb is a second target that must be answered with *damage*, and the
Smog cap means the player cannot substitute extra block for extra damage. Splash and multi-hit decks
handle the bomb for free while single-target decks pay 7 damage or 8 HP every cycle.

## Scaling

**By act:** none. Living Fog exists only in the Underdocks (Act 1) pool; nothing on the model reads
the act index except through the shared multiplayer HP formula.

**By ascension:**

| Level | Effect |
|---|---|
| A8 `ToughEnemies` | Living Fog HP 80 → 82; **Gas Bomb HP 7 → 8** |
| A9 `DeadlyEnemies` | Advanced Gas 8 → 9; Bloat 5 → 6; Super Gas Blast 8 → 9; **bomb explosion 8 → 9** |

Unusually for an add-based fight, the ascension levels touch the *minion* as well as the parent — the
bomb gets both tougher and deadlier. The gimmick load therefore rises with difficulty instead of
staying flat, though only mildly. Smoggy itself never scales; the one-Skill cap is identical at A0 and
A20.

**By seat count (multiplayer):**

- **HP** uses the standard scale: base × players × **1.1** (the Act 1 multiplier).

| Players | Fog HP (base 80) | Fog HP (A8, 82) | Bomb HP (base 7) | Bomb HP (A8, 8) |
|---|---|---|---|---|
| 1 | 80 | 82 | 7 | 8 |
| 2 | 176 | ≈180 | ≈15 | ≈18 |
| 3 | 264 | ≈271 | ≈23 | ≈26 |
| 4 | 352 | ≈361 | ≈31 | ≈35 |

- **The bombs scale too.** Unlike adds that are placed at encounter setup, the bomb is created
  through the normal mid-combat creature-creation path, which applies the multiplayer HP scale at
  creation time. A four-player bomb is a ~31 HP wall that still deals its flat 8. This inverts the
  usual co-op relief: the "buy out the explosion" option gets steadily *worse* per seat (4 players
  spend ~31 damage to prevent 8 per player = 32 party-wide, i.e. par at four seats and a loss at
  fewer), so larger parties are pushed toward simply eating the detonation.
- **Attacks and the debuff are party-wide.** Monster attacks default to hitting all opponents, and
  the Smoggy application is aimed at the full player-creature list, so **every seat** gets the
  one-Skill-per-turn lock on turn 1 and every seat takes the full 5/8/8 numbers undivided.
- Living Fog gains no block, so the multiplayer enemy-block multiplier never applies here.

## Proposed fight class: **mixed**

This fight makes two unrelated demands on every turn and neither one dominates. First, a rules-warping
constraint: from turn 1 onward the player is capped at one Skill per turn for the entire fight, which
guts action economy for Skill-heavy decks and, because block usually lives in Skills, quietly converts
a defensive question into a deckbuilding one — that half is pure gimmick. Second, a recurring
target-priority tax: a 7 HP bomb appears every other turn with a telegraphed 8-damage detonation,
priced almost exactly at par, so the player must re-answer "spend damage or take damage" on a fixed
2-turn metronome while an 80 HP body ticks down — that half is light attrition with a swarm-shaped
cadence, though never more than one add is alive at once. It is not spike (nothing exceeds 9 from a
single source, and the biggest turn is a predictable 16 split across two telegraphed sources), and it
is not pure gimmick (the bomb is a genuine damage-allocation problem, not flavor). For Track B, model
it as a flat ~10.5/turn baseline with a buy-down option at ~7 damage per cycle, *plus* a hard cap of
one Skill per turn applied from turn 1 — and note that the buy-down gets worse, not better, with seat
count.
