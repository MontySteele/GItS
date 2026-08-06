# Tunneler — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `Tunneler`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 2 (`Hive`, act index 1)
- **Encounters:**
  - `TunnelerWeak` — a **weak** (early-act) encounter containing exactly one Tunneler. This is the only encounter that Act 2's pool actually lists.
  - `TunnelerNormal` — one Tunneler plus one Chomper (the Chomper is flagged to scream first, i.e. it opens with its telegraph move). This encounter is registered in the model database but is **not referenced by any act's encounter list**, so as decompiled it is unrostered/vestigial. Treat the solo Weak fight as the shipping version.
- **Proposed fight class:** `gimmick`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

The Tunneler runs a four-state move machine with **zero randomness**. Every transition is hard-wired; the only branch in the whole fight is player-caused.

The four states:

1. **Bite** (`BITE_MOVE`) — single-attack intent. One hit.
2. **Burrow** (`BURROW_MOVE`) — shows a *buff* intent and a *defend* intent together. Digs under, applies **Burrowed** to itself, and gains a large lump of Block. Deals no damage.
3. **From Below** (`BELOW_MOVE`) — single-attack intent. Attacks from underground; the visual lunges toward the first player, but the damage is a normal monster attack.
4. **Still Dizzy** (`DIZZY_MOVE`) — stun intent. Wakes up, does nothing. **Hidden from the bestiary** — the game explicitly suppresses this move in the compendium listing, so the player is never shown it up front.

Wiring: Bite → Burrow → From Below → **From Below → From Below → …** forever. The machine starts on Bite. Left alone, the Tunneler settles permanently into the underground attack and never resurfaces.

The only exit from that loop is the player breaking its Block (see Gimmicks). When that happens the Tunneler is stunned *immediately*, mid-player-turn: its pending intent is overwritten with a stunned move, it plays the stun animation, and Burrowed is stripped. It then spends one turn doing nothing (the dizzy turn) and is routed explicitly back to **Bite**, restarting the cycle from the top.

Turn table, single player, no ascension:

| Turn | Intent shown | Effect |
| --- | --- | --- |
| 1 | attack | Bite, 13 |
| 2 | buff + defend | Burrows, gains 32 Block, no damage |
| 3 | attack | From Below, 23 |
| 4+ | attack | From Below, 23, every turn, indefinitely |

With the player breaking the shield on turn 2 (i.e. during the burrow turn), the observed loop is instead **Bite → Burrow → dizzy → Bite → Burrow → dizzy → …**: a 3-turn cycle in which the Tunneler lands only its 13-damage Bite.

The declared Still Dizzy state is a formality — the actual stun is installed as a one-off stunned move whose follow-up is pinned to Bite. Either path lands on Bite; there is no way to re-enter the fight mid-cycle.

## Numbers

| Value | Base | Ascension-scaled |
| --- | --- | --- |
| Starting HP | 87 (fixed — min and max are the same, no roll) | **92** at the Tough-Enemies tier |
| Bite damage | 13 | **15** at the Deadly-Enemies tier |
| Burrow Block | 32 | **37** at the Tough-Enemies tier |
| From Below damage | 23 | **26** at the Deadly-Enemies tier |

HP is a fixed 87 — unusual; most normals roll inside a band. There is no Strength gain, no debuff application, no HP-threshold branch, and no summon anywhere in the kit.

**The load-bearing number is the Block, not the HP.** The 32 Block does not decay (see below), so it is a flat 32-damage toll the player must pay *in addition to* the 87 HP, once per cycle, and paying it is the only way to stop the 23-per-turn drip. If the player never pays it, the fight has no natural end: From Below repeats forever while the shield sits untouched.

Rough cost accounting, single player, base numbers: killing it "the clean way" costs 87 HP of damage plus 32 per burrow cycle survived. If the player can produce ≥32 damage inside the burrow turn every cycle, incoming damage is 13 per 3 turns. If the player can produce nothing near 32, incoming damage is 23 per turn with no cap.

## Gimmicks

- **Burrowed is a Barricade for the monster (the headline).** While Burrowed is on it, the Tunneler's Block is not cleared at turn boundaries — the shield persists across turns and can be chipped down over several turns rather than having to be broken in one. It does not re-gain Block while burrowed, because the machine loops on From Below and never re-enters Burrow until it has been stunned. So the shield is a **one-time, persistent 32-point lock per cycle**.
- **Breaking the Block stuns it.** When the Tunneler's Block is reduced to zero by damage, a hook fires: it is stunned on the spot, Burrowed is removed, and its next-move pointer is forced to Bite. Removing Burrowed also wipes any remaining Block outright. The stun overwrites the currently displayed intent, so **breaking the shield during your turn cancels the From Below attack that was already telegraphed** — the reward is immediate, not next-cycle.
- **Refusing the puzzle is a losing line, not a slow line.** Because From Below self-loops, ignoring the shield does not merely delay the kill; it means the fight never leaves its damage phase. The player either produces the burst or takes 23 (26) every turn until one of them dies.
- **Hidden state changes the readability of the fight.** While Burrowed, the Tunneler uses an entirely separate animation set — hidden idle, hidden attack, hidden death — and takes no visible hurt reaction. The dizzy/wake-up state is also suppressed from the bestiary, so a first-time player is not told that breaking the shield is the intended answer; the fight teaches itself only by being played.
- **Block cannot be dodged by killing it burrowed.** Nothing prevents the player from simply killing it through the shield if they out-damage 32 + remaining HP in a window; the burrowed death is a distinct animation, and it is a legitimate (if damage-expensive) line.
- No allies, no respawn, no scaling buff, no enrage. One mechanic, repeated.

## Scaling by act / ascension

- **Act:** none. Tunneler is Act 2 content and its numbers do not read the act index. The only act-derived factor touching it is the multiplayer scaler below (Act 2 factor = 1.2).
- **Ascension:** two independent, tier-keyed bumps.
  - *Tough Enemies* tier: HP 87 → **92**, Burrow Block 32 → **37**. Note both of the "how much damage must I produce" numbers live in this tier: the shield gets 5 points harder to crack at the same time the body gets 5 points fatter.
  - *Deadly Enemies* tier: Bite 13 → **15**, From Below 23 → **26**.
  - Nothing else scales — the cycle length, the stun behaviour, and the number of Burrow uses are identical at every ascension.

## Multiplayer / seat-count adjustments

- **HP scales on creature creation** by (player count × act factor); Act 2 non-boss factor is **1.2**. So roughly **209 HP at 2 players** and **313 HP at 3 players** (base), or ~221 / ~331 at the Tough-Enemies tier.
- **Block scales by the same multiplier**, because the multiplayer scaler inflates block gained by enemies from monster moves. The 32 Burrow Block becomes roughly **77 at 2 players** and **115 at 3 players** (about 89 / 133 at the Tough-Enemies tier). This is the sharpest seat-count effect in the fight: the puzzle's difficulty is multiplied, not divided, by having more people in the room.
- **Damage does not scale, but it is applied per seat.** The Tunneler's attacks are untargeted monster attacks, which resolve against *all* player creatures. Every seat eats the full 13/15 Bite and the full 23/26 From Below. The party does not split the hit.
- **Net effect:** at higher seat counts the burrow window demands a *coordinated* burst (77–115 damage in one or two turns) while the failure state costs the whole party 23–26 each per turn. Co-op makes this fight strictly more of a check and less of a grind, which is the opposite of the usual seat-count effect.

## Fight-class reasoning — `gimmick`

Every turn of this fight is downstream of one binary question: can the party dump ~32 damage (77–115 in co-op) into a persistent shield during the burrow window? Answer yes and the Tunneler is a 13-damage-per-three-turns non-threat that keeps handing you free stun turns; answer no and it becomes an unbounded 23-per-turn loop that never advances to any other phase, because From Below transitions only to itself. That is not attrition — the per-turn defensive ask is flat and modest, and the health pool is small for Act 2 — and it is not a spike, since no single incoming turn is meant to be survived. The fight is a lock-and-key: it demands a specific, repeatable burst threshold on a telegraphed turn, and it converts *failure* to meet that threshold into the grind, rather than being a grind by design.
