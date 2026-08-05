# Fabricator — behavior dossier

- **Class:** `Fabricator`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 3 (`Glory`, act index 2)
- **Encounter:** `FabricatorNormal` — five slots laid out `bot1, bot2, fabricator, bot3, bot4`. Only the Fabricator is placed at combat start; every other body in the fight is one it builds.
- **Proposed fight class:** `mixed`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

The Fabricator's move machine has three moves and two routing nodes. Every move funnels back into the same conditional node, so the whole AI is a single question asked once per turn:

> **Is the enemy side below 4 living creatures?** (the Fabricator itself counts toward that 4)

- **Yes → random branch, 50/50, no repeat limit and no cooldown:**
  - **Fabricate** — pure *summon* intent, no damage. Spawns **two** bots: one from the defensive pool, then one from the aggressive pool.
  - **Fabricating Strike** — shows an *attack* intent **and** a *summon* intent together. Hits, then spawns **one** bot from the aggressive pool.
- **No → Disintegrate** — a plain *single-attack* intent, no summon. The Fabricator does nothing else while its board is full.

Both branches are weighted 1.0 and flagged repeat-forever, so consecutive Fabricates or consecutive Fabricating Strikes are perfectly legal — there is no anti-streak rule anywhere in the kit.

Because the summon icon is part of the telegraph, **the player can always read next turn's board from this turn's intent**: attack-only means the population cap is reached, attack-plus-summon means one more aggro bot is coming, summon-only means two more bots are coming and no damage this turn.

### Population arithmetic

| Enemy-side living count at roll time | Available branch | Result |
| --- | --- | --- |
| 1 (Fabricator alone, turn 1) | Fabricate **or** Fabricating Strike | → 3 alive, or 2 alive |
| 2 | Fabricate **or** Fabricating Strike | → 4 alive, or 3 alive |
| 3 | Fabricate **or** Fabricating Strike | → **5 alive (board full)**, or 4 alive |
| 4 or 5 | Disintegrate only | board unchanged |

The ceiling is the Fabricator plus **four bots**, which exactly consumes the encounter's four bot slots. The check runs against *living* creatures, so **every bot the player kills re-opens the fabricate branch** — the treadmill restarts the moment the board drops back under four.

Fastest realistic saturation is turn 2 (Fabricate → Fabricate). Slowest is a long chain of Fabricating Strikes, which adds one aggro bot per turn while chipping the player.

Note also that **Fabricating Strike is deliberately hidden from the bestiary listing** — the in-game codex shows only Fabricate and Disintegrate, so a player consulting it will under-read the summon rate.

## Numbers

### The Fabricator

| Value | Base | Ascension tier |
| --- | --- | --- |
| HP | **150**, fixed (min = max, no roll) | **155** at the *Tough Enemies* tier |
| Fabricating Strike damage | 18 | 21 at the *Deadly Enemies* tier |
| Disintegrate damage | 11 | 13 at the *Deadly Enemies* tier |
| Fabricate damage | — (0) | — |

It gains no Block, no Strength, and no self-buffs of any kind. Its corpse does not fade after death (cosmetic only).

### The bots

Each spawned bot rolls its own HP inside its band, and the roll prefers a value not already in use by another enemy on the side — so the four bots will generally all show different HP totals. All four read as armored on hit.

**Aggressive pool** (spawned by Fabricating Strike, and as the second half of Fabricate):

| Bot | HP (base / Tough) | Move | Damage (base / Deadly) | Rider |
| --- | --- | --- | --- | --- |
| **Zapbot** | 18–23 / 19–24 | Zap, every turn | 14 / 15 **and rising** | enters play with a **High Voltage** counter at 2 |
| **Stabbot** | 18–23 / 19–24 | Stab, every turn | 11 / 12 | applies **1 Frail** |

**Defensive pool** (only ever spawned as the first half of Fabricate):

| Bot | HP (base / Tough) | Move | Effect |
| --- | --- | --- | --- |
| **Guardbot** | 16–20 / 17–21 | Guard, every turn | grants **15 Block to the Fabricator** (to every Fabricator on its side), never to itself |
| **Noisebot** | 18–23 / 19–24 | Noise, every turn | adds **2 Dazed per player** — one to the discard pile, one shuffled to a random position in the draw pile |

None of the bots has a state machine worth the name: each has exactly one move that loops into itself forever.

**High Voltage is the only true scaler in the fight.** A Zapbot converts its counter into **+2 Strength at the end of every enemy turn**, permanently, and the counter is never spent. A Zapbot alive for four turns is hitting for 14 → 16 → 18 → 20; two Zapbots on the board compound that independently. Nothing else in the encounter escalates.

### Worst-case turn damage (single player, base tier)

| Board | Incoming that turn |
| --- | --- |
| Fabricator + 2 Zapbots + 2 Stabbots (impossible — Fabricate always includes a defensive bot, listed as a bound) | 11 + 28 + 22 = 61, climbing +4/turn |
| Fabricator + 2 Zapbots + 1 Stabbot + 1 defensive bot (realistic aggro-heavy) | 11 + 28 + 11 = **50**, climbing +4/turn |
| Fabricator + 1 Zapbot + 1 Stabbot + Guardbot + Noisebot (realistic mixed) | 11 + 14 + 11 = **36**, climbing +2/turn, plus 15 Block on the Fabricator and 2 Dazed per turn |

## Gimmicks

- **Killing bots is what keeps the fight going.** The fabricate gate reads *living* creatures, so clearing the board is precisely the action that re-arms the summoner. A player who greedily AoEs the bots down every turn re-enters the summon loop indefinitely and never closes the fight. This inverts the normal swarm instinct and is the single most important read in the encounter.
- **Killing the Fabricator ends everything.** The bots carry a minion marker; when the last non-minion enemy dies and only minions remain, the survivors are killed outright. The Fabricator is therefore always a legal race target, and racing it — through a bot wall, while eating chip — is the intended alternative line to grinding.
- **Guardbot is a Fabricator-only wall.** It gives its 15 Block to the Fabricator and never to itself or to other bots, which means it is simultaneously the softest body on the board (16–20 HP) and the thing that most directly taxes the race plan. It converts "kill the summoner" into "kill the summoner *and* out-damage 15 Block per Guardbot per turn."
- **The anti-repeat rule on spawns barely fires.** Spawn selection excludes the most recently spawned model, but the two pools are disjoint and Fabricate always draws defensive-then-aggressive, so the exclusion almost never binds. In practice each pick is a free coin flip, with one exception: **back-to-back Fabricating Strikes are forced to alternate Zapbot / Stabbot**, since only then is the previous spawn from the same pool. A Fabricating Strike chain therefore cannot stack two Zapbots in a row — but two Fabricates can.
- **Noisebot attacks the deck, not the body.** Two Dazed per player per turn, split between discard and a random draw-pile slot, and the draw-pile copy cannot be planned around. Left alive across a long grind it is the bot most likely to actually lose the fight, and it is invisible to any "how much damage is incoming" read.
- **Bots spawn out of nothing, mid-move.** They are dropped into the next free slot at the moment the move resolves (with a fall-in animation), so their intents appear immediately and the player sees the new threat before their own turn.
- No HP-threshold branch, no enrage, no death rattle, no self-heal.

## Scaling by act / ascension

- **Act:** none. The Fabricator is Act 3 content only, and none of its numbers read the act index. The act index is consumed solely by the multiplayer scaler below (Act 3, non-boss → factor 1.2).
- **Ascension:** two independent tier-keyed bumps, both simple flat swaps.
  - *Tough Enemies* tier: Fabricator 150 → 155; Zapbot / Stabbot / Noisebot band 18–23 → 19–24; Guardbot band 16–20 → 17–21.
  - *Deadly Enemies* tier: Fabricating Strike 18 → 21, Disintegrate 11 → 13, Zap 14 → 15, Stab 11 → 12.
  - **Nothing else scales.** The population cap stays at 4 bots, the 50/50 branch weights are fixed, High Voltage stays at 2, Guardbot's Block stays at 15, Noisebot stays at 2 Dazed, Stabbot stays at 1 Frail. Ascension makes the fight sharper but does not make it any wider or any faster to saturate.

## Multiplayer / seat-count adjustments

- **HP scales on every body, including bots spawned mid-fight.** Enemy max HP is multiplied by (player count × act factor); Act 3 non-boss is **1.2**. The Fabricator sits at **360** HP at 2 players and **540** at 3 (155 base → 372 / 558 at the Tough tier). Bots land around 43–55 HP at 2 players and 65–83 at 3 — no longer one-card clears. Scaling is applied at creature creation, so the treadmill produces full-price bodies all fight long.
- **Guardbot's Block does *not* scale.** Its 15 Block is flagged as unpowered, and the multiplayer block multiplier explicitly skips unpowered sources. At 2–3 players the Fabricator's effective HP roughly triples while its per-turn Block shield stays at a flat 15 — the only place seat count works in the party's favor.
- **Damage does not scale, but it lands per seat.** Monster attacks resolve against every opposing player creature, so Fabricating Strike, Disintegrate, Zap and Stab each hit *everyone* for their listed number, and Stabbot's Frail is applied to every player. Party-wide incoming damage therefore grows linearly with seat count on top of the HP inflation.
- **Noisebot is explicitly per-player**: it walks the target list and adds 2 Dazed into each player's own piles. Four seats, four polluted decks, every turn.
- **The population cap is seat-count independent.** Four bots maximum at one player or four, and the 4-alive gate is unchanged — co-op does not widen the board, it only makes each body take longer to remove, which means the summon gate stays *closed* for longer stretches. Co-op perversely reduces the summon rate while raising every other cost.
- High Voltage's +2/turn is likewise seat-count independent, but with fights running much longer at higher seat counts, a surviving Zapbot reaches genuinely dangerous numbers before the Fabricator dies.

## Fight-class reasoning — `mixed`

The per-turn ask changes shape depending on which coin flips landed, and that is the defining property: a Guardbot/Noisebot board demands throughput and deck resilience with almost no damage coming in, while a double-Zapbot board demands hard mitigation *now* against 50-plus escalating damage, and the encounter can hand you either one from the same intent. Layered on top is a decision the player must get right in the first two turns — that killing bots re-opens the summon gate, so the correct line is usually to race the 150 HP primary (whose death kills every minion) through a Guardbot's 15 Block per turn rather than to clear the board — which is a structural puzzle no single-axis label captures. It is not `swarm`, because the cap is four bodies and clearing them is actively counterproductive; it is not `spike`, because the largest single hit in the kit is 18–21 and it is always telegraphed; it is not `attrition`, because the Fabricator's health bar is small for Act 3 and the fight ends the instant it drops. `mixed` is the honest read: AoE, single-target burst, block, and status resilience are all demanded, and which one is demanded on a given turn is decided by a coin flip the player cannot influence.
