# The Lost

- **Class:** `TheLost`
- **Kind:** normal
- **Act:** 3 (Glory, act index 2)
- **Encounter:** `TheLostAndForgottenNormal` — always spawns the pair **The Lost + The Forgotten**; there is no solo appearance and no other encounter references this model
- **Fight class:** **mixed**

> Behavioral notes only — derived from decompiled behavior, no source reproduced.

## Where it appears

The Lost is an ordinary (non-elite, non-boss) monster room in Act 3's Glory encounter pool. It is
never generated alone: the encounter model hard-codes two slots and fills them with The Lost and The
Forgotten every time, with no weighted alternatives. The two are a designed mirror pair — one steals
**Strength**, the other steals **Dexterity** — and the dossier below covers The Lost's own machine
first, then what the pairing does to the fight. Its take-damage sound family is "stone".

## Intent pattern

The move machine is the simplest shape in the game: **two states in a forced two-beat loop, no RNG,
no branch, no HP threshold, no phase change.** The initial state is the debuff, and each state
hard-points at the other as its follow-up.

| Beat | Move | What it does | Intent shown |
|---|---|---|---|
| 1 (always) | **Debilitating Smog** | Removes Strength from **every player**, then gives itself the same amount | debuff + buff |
| 2 | **Eye Lasers** | **2 hits** on **every player** | multi-attack (damage × 2) |
| 3 | Debilitating Smog | … | debuff + buff |
| 4 | Eye Lasers | … | multi-attack |

So: **odd turns are theft, even turns are the attack**, forever, fully telegraphed one turn ahead and
completely predictable from turn 1. Structural consequences worth modelling:

- **Turn 1 is never an attack.** The player gets a free opening turn against the body, but pays for
  it immediately in Strength.
- **The theft *is* the damage scaling.** The Strength taken from players is added to The Lost one for
  one, and monster attack intents run the stolen Strength through the standard damage modification
  hook — so each Smog raises the *next* Eye Lasers by the stolen amount on **each of its two hits**.
  The Strength swing is therefore double-counted: the player loses offense while the enemy gains it,
  and the enemy gain is multiplied by hit count.
- Nothing in the machine can skip, repeat or reorder. Any per-turn model can assume exact alternation.

## Damage / HP numbers

| Stat | Base | Ascension |
|---|---|---|
| HP (min = max, no roll) | **93** | **99** (A8 `ToughEnemies`) |
| Eye Lasers damage per hit | **4** (+ current Strength) | **5** (A9 `DeadlyEnemies`) |
| Eye Lasers hit count | 2 | unchanged |
| Debilitating Smog steal | **2 Strength** from each player | **2** — explicitly unchanged at A9 |
| Debilitating Smog self-gain | +2 Strength (flat, once per cast) | unchanged |
| Block gained | **none, ever** | — |

The Lost applies no block, no Vulnerable/Weak-style debuff, and no status cards. Its whole profile is
the multi-hit attack plus the Strength it has taken.

Base-difficulty solo projection (The Lost's contribution only):

| Turn | Move | Its Strength after | Damage to each player | Player Strength after |
|---|---|---|---|---|
| 1 | Smog | +2 | 0 | −2 |
| 2 | Eye Lasers | +2 | 2 × 6 = **12** | −2 |
| 3 | Smog | +4 | 0 | −4 |
| 4 | Eye Lasers | +4 | 2 × 8 = **16** | −4 |
| 5 | Smog | +6 | 0 | −6 |
| 6 | Eye Lasers | +6 | 2 × 10 = **20** | −6 |
| 7 | Smog | +8 | 0 | −8 |
| 8 | Eye Lasers | +8 | 2 × 12 = **24** | −8 |

The attack grows **+4 per two-turn cycle (+2 per turn averaged)** and it grows forever — nothing caps
the Strength on either side. On A9 the same table reads 14 / 18 / 22 / 26: identical shape, shifted
up by 2 per attack turn.

Player-side, the theft is uncapped in the negative direction: a player is at −2 Strength before their
second turn and −10 by turn 9. Every attack the player throws is reduced by that amount **per damage
instance**, so multi-hit and multi-attack decks — exactly the decks that best handle a 93 HP body —
are punished hardest, while big-single-hit decks barely notice until deep negatives.

## Gimmicks

### Strength theft as a two-way clock

This is the whole enemy. The Smog is not a debuff *and* a buff bolted together; it is one transfer,
and the transfer amount is fixed at 2 while the *payoff* compounds because the receiving side spends
it on two hits per cycle. The practical reading:

- Time is strictly the player's enemy — every cycle the player is 2 Strength weaker and the incoming
  attack is 4 bigger.
- There is no way to interact with the transfer other than killing the enemy or clearing the debuff.
  The Lost gains nothing at combat start beyond the tracker power below, so a fast kill leaves the
  swing at only −2 / +2.

### The stolen Strength comes back when it dies

At combat start The Lost gives itself a single-stack marker power that **tracks every point of
negative Strength it applies to players**. When The Lost dies (unless its removal was prevented), it
refunds each player exactly what it took from them.

Two consequences that matter more than they look:

1. **The Strength loss is a lease, not a sale** — but only for the fight, and only once The Lost is
   dead. It never expires on its own and there is no decay.
2. **Kill order is a real decision in the paired encounter.** Killing The Lost first both stops the
   escalation *and* immediately restores the party's Strength, which is exactly what the party needs
   to kill The Forgotten. Killing The Forgotten first leaves the party fighting the escalating half
   at reduced offense. The refund makes The Lost the correct first target in nearly all cases, and
   makes the fight's difficulty very sensitive to whether the player recognises that.

### The mirror partner

The Forgotten runs the identical two-beat machine with the same "steal then hit" logic on the other
axis, so the pair's beats coincide — theft turns and attack turns line up, giving the fight a
strongly alternating quiet/loud rhythm rather than a smooth stream.

| | The Lost | The Forgotten |
|---|---|---|
| HP | 93 / 99 (A8) | 106 / 111 (A8) |
| Steals | 2 **Strength** per cast | 2 **Dexterity** per cast |
| Debuff move also | (nothing else) | gains **8 block** |
| Attack | 2 × (4/5 + Strength) | 1 × (13/15 + its Dexterity) |
| Refund on death | stolen Strength | stolen Dexterity |

The Lost attacks the party's **offense** (Strength → damage dealt); The Forgotten attacks the party's
**defense** (Dexterity → block gained) while self-blocking 8 a cycle. Combined solo damage on the
attack turns runs roughly **27 → 33 → 39 → 45** on turns 2/4/6/8 at base difficulty, against a total
pool of 199 HP (210 at A8). The player must therefore either kill through ~200 HP inside three to
four cycles or hold a defense that is itself being eroded.

## Scaling

**By act:** none beyond the shared multiplayer formula — the model reads no act index. It exists only
in Act 3's pool.

**By ascension:**

| Level | Effect |
|---|---|
| A8 `ToughEnemies` | HP 93 → 99 |
| A9 `DeadlyEnemies` | Eye Lasers 4 → 5 per hit (i.e. +2 per attack turn) |

Notably the **steal amount is deliberately not scaled** — the ascension code passes 2 for both
branches. High ascension makes the fight hit harder but does not make the debuff spiral steeper, so
the fight's *character* is constant across difficulty; only the race gets tighter.

**By seat count (multiplayer):**

- **HP** uses the standard scale: base × players × **1.2** (Act 3 non-boss multiplier; boss rooms in
  Act 3 use 1.3).

| Players | The Lost HP (93) | A8 (99) | Pair total (base) |
|---|---|---|---|
| 1 | 93 | 99 | 199 |
| 2 | ≈223 | ≈238 | ≈478 |
| 3 | ≈335 | ≈356 | ≈716 |
| 4 | ≈446 | ≈475 | ≈955 |

- **Eye Lasers is party-wide.** Monster attacks default to targeting all opponents, so *every* seat
  takes both hits at full value. No split, no target selection.
- **Debilitating Smog is party-wide on the steal side but flat on the gain side.** It removes 2
  Strength from *each* player, but gives The Lost a flat **+2** regardless of seat count. The enemy's
  escalation curve is therefore **identical in a 4-player game and a solo game**, while the party pays
  four times the Strength. Per seat the pressure is unchanged; in aggregate the party loses far more
  offense than the enemy gains, which — against HP that scaled by 1.2× per seat — makes this fight
  meaningfully harder per seat than the raw HP numbers suggest.
- The refund tracker is keyed per player, so each seat gets back exactly what it individually lost.
- The Lost gains no block, so the multiplayer enemy-block multiplier never touches it (it does touch
  The Forgotten's 8 block, which scales by players × 1.2).

## Proposed fight class: **mixed**

Per turn this fight alternates between two genuinely different demands, and neither one dominates.
On theft turns it asks for *nothing defensive at all* — the correct play is maximum aggression, plus
the target-priority read that killing The Lost first refunds the party's Strength — while on attack
turns it asks for a hard block wall against a party-wide double hit that climbs 12 → 16 → 20 → 24
solo (27 → 45 with the partner) with no ceiling. Underneath both sits a compounding resource-theft
gimmick that makes the player's answer to the race weaker on exactly the axis the race needs, hitting
multi-hit decks hardest. It is not pure **spike** because the big turn is fully telegraphed and every
other turn is free; not pure **attrition** because ~200 HP over three or four cycles is a real clock
rather than a grind; and not pure **gimmick** because the Strength swing is not a puzzle to solve but
a rate the player must outrun. For Track B, model it as a **two-phase demand curve** — alternating
zero-defense and heavy-defense turns — riding on a linearly escalating enemy attack *and* a linearly
decaying player offense multiplier, with a discrete drop in both when The Lost dies.
