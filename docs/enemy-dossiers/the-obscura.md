# The Obscura — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `TheObscura`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 2 (`Hive`, act index 1)
- **Encounter:** `TheObscuraNormal` — two declared slots (`illusion`, `obscura`) but only **one** creature is spawned at combat start: the Obscura itself, in the `obscura` slot. The `illusion` slot sits empty until the Obscura fills it on turn 1.
- **Also present:** `Parafright` — the summoned illusion. It is never placed by the encounter generator; it only ever exists because the Obscura made it.
- **Proposed fight class:** `gimmick`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

The Obscura runs a **forced opener into a 3-way random rotation**.

**Turn 1 is always Illusion** (shows a *summon* intent). There is no inbound edge back to this state from anywhere in the machine, so the Obscura summons exactly once per fight, on its first turn, and never again — even if you kill what it made.

From then on, every move funnels into a random-branch node that picks uniformly among three moves, each flagged "cannot repeat": the branch will not select the move that was played on the immediately preceding turn, but any move from two turns ago is fair game again. All three carry equal weight and there are no cooldowns.

The rotation:

1. **Piercing Gaze** — *single-attack* intent. One hit, no rider.
2. **Wail** — *buff* intent. Grants **+3 Strength to the entire enemy side**, which is to say to the Obscura *and* to the illusion, permanently.
3. **Hardening Strike** — *single-attack* + *defend* intents shown together. One hit, then gains Block.

So the observed shape is: summon → then a coin-flip-ish stream in which no two consecutive turns are the same move. Over a long fight each of the three lands roughly a third of the time, which means **you should expect a Wail every ~3 turns for the whole fight**.

| Turn | Move |
| --- | --- |
| 1 | Illusion (summon) — always |
| 2 | uniform among Gaze / Wail / Hardening Strike |
| 3+ | uniform among the three, excluding whatever was played last turn |

**The Parafright's own pattern is trivial:** a single move state that loops onto itself. It attacks with **Slam** every single turn, forever, with no variation — except on the turn immediately after it is killed, where it is force-fed a **Revive** move (shows a *heal* intent) and then resumes the loop. A creature summoned mid-turn does not act on the turn it appeared, so the Slam pressure starts on the turn after the summon.

**Bestiary note:** the Obscura deliberately **hides Piercing Gaze from its bestiary entry**. A player who scouts the fight sees the summon, the buff, and the block-attack, but not the enemy's largest direct attack. The bestiary undersells this fight by design.

## Numbers

### The Obscura

| Value | Base | Ascension tier |
| --- | --- | --- |
| Max HP | 123 (fixed — min = max, no roll) | **129** (Tough-Enemies tier) |
| Piercing Gaze damage | 10 | **11** (Deadly-Enemies tier) |
| Hardening Strike damage | 6 | **7** (Deadly-Enemies tier) |
| Hardening Strike Block | 6 | **7** (Deadly-Enemies tier) |
| Wail Strength granted | +3, to every creature on the enemy side | +3 (**not** ascension-scaled) |

### Parafright (the illusion)

| Value | Base | Ascension tier |
| --- | --- | --- |
| Max HP | 21 (fixed) | 21 (**not** ascension-scaled) |
| Slam damage | 16, every turn | **17** (Deadly-Enemies tier) |

Because Wail buffs the whole side, the numbers escalate together. Effective damage after *n* Wails (base tier, before player-side modifiers):

| Wails landed | Slam (illusion, every turn) | Piercing Gaze | Hardening Strike |
| --- | --- | --- | --- |
| 0 | 16 | 10 | 6 (+6 Block) |
| 1 | 19 | 13 | 9 |
| 2 | 22 | 16 | 12 |
| 3 | 25 | 19 | 15 |

The illusion is the damage engine: it hits **every turn** at the larger number, while the Obscura only attacks on roughly two turns in three and its Hardening Strike turn is nearly harmless. Typical incoming per turn is therefore Slam plus either nothing (Wail turn), 10-ish (Gaze) or 6-ish (Hardening Strike) — call it **16–26 in the opening turns, climbing by +6 per Wail** (+3 on each of the two attackers).

Total health that must actually be removed to win: **123 (129)** — the illusion's 21 HP is not part of the win condition and, as below, is not a fixed cost either.

## Gimmicks

- **The illusion cannot be permanently killed (the headline).** The Parafright enters carrying an Illusion buff. When it dies, it is *not* removed from combat: it plays a stun animation, is immediately handed a Revive move, and on its next turn **heals to full 21 HP** and resumes slamming. Killing it buys you exactly **one** Slam-free turn, and costs you 21 HP worth of damage (multiplied in co-op — see below). There is no stack counter and no limit; you can do this all fight and it will come back every time.
- **Killing it is worse than it looks, twice over.** The Illusion buff explicitly *keeps* the creature's buffs through death, while stripping non-temporary **debuffs**. So the Strength it accumulated from Wail survives its death, and any Weak / Vulnerable / poison-style pressure you invested in it is wiped clean by the revive. Killing the illusion launders your debuffs off the target.
- **It is untouchable while reviving.** During the revive turn the illusion refuses to receive powers, so you cannot pre-load debuffs onto it on the turn it is stunned.
- **The illusion is a minion, not a win condition.** It is flagged as a secondary enemy: its death does not end combat and does not trigger fatal-blow effects, and it is exempt from the Doom-style "remove the creature" effects that clear other summons. Combat ends when **the Obscura** dies — and when it does, the illusion goes down with it regardless of its HP.
- **Correct play is target discipline.** The visible, aggressive, low-HP creature is a decoy that regenerates for free; the correct target is the 123-HP caster behind it. Any damage routed at the illusion beyond a deliberate one-turn breather is thrown away. This is the whole fight.
- **Wail is a slow enrage.** Every ~3 turns the side gains +3 Strength, and it is the *illusion's* every-turn Slam that converts that best. A fight that goes long does not just take longer — it takes strictly more damage per turn, forever, with no cap.
- **Hardening Strike is the only Block in the kit,** 6 (7) on roughly one turn in three, and it is small enough that it mostly costs the player a card rather than a plan.
- **Cosmetic tell:** the Obscura uses a distinct "unrevealed" hurt/death animation set until it has summoned, switching to its normal set afterward. It also carries a phobia-skin variant. No mechanical consequence.
- No HP-threshold branch, no second summon, no enrage timer, no additional adds.

## Scaling by act / ascension

- **Act:** none. The Obscura is Act 2 content only and reads no act index. The only act-derived factor touching it is the multiplayer scaler below (Act 2 factor: **1.2**).
- **Ascension:** two independent, tier-keyed bumps.
  - *Tough Enemies* tier: Obscura HP 123 → **129**. The illusion's 21 HP is untouched.
  - *Deadly Enemies* tier: Piercing Gaze 10 → 11, Hardening Strike 6 → 7 damage and 6 → 7 Block, Slam 16 → 17.
  - **Wail's +3 Strength does not scale with ascension**, and neither does the rotation, the summon timing, or the revive. Ascension makes this fight about 5% harder on paper; the mechanics are identical at every level.

## Multiplayer / seat-count adjustments

- **Both bodies scale on HP.** Enemy max HP is multiplied by (player count × act factor) at creature-creation time; Act 2 non-boss factor is **1.2**. So the Obscura is ~123 → **295** at 2 players, **443** at 3 players (129 → 310 / 464 at the Tough-Enemies tier).
- **The illusion is scaled too, and it is scaled on every respawn** — the scaling is applied when the creature is created, and the revive restores it to that scaled maximum. A 21-HP illusion becomes ~50 HP at 2 players and ~76 at 3. The "kill it to buy a turn" option therefore gets dramatically more expensive with each extra seat, while still buying exactly one turn. At 3 players it is essentially never worth doing.
- **Block scales the same way.** Hardening Strike's 6 Block becomes ~14 at 2 players and ~22 at 3 (7 → 17 / 25 at the Deadly-Enemies tier).
- **Damage does not scale, but it is applied per seat.** Monster attacks hit every player creature rather than selecting one, so **each seat eats a full Slam every turn** plus the Obscura's attack — the party's aggregate incoming damage is multiplied by seat count while the printed numbers stay flat.
- **Wail is seat-count independent** — still +3 to the enemy side, but it now buys +3 against *every* seat simultaneously, so its real value scales with party size.
- Net effect: co-op makes this fight much longer (HP × seats × 1.2 on a target you must burn down alone) while the escalating Wail keeps compounding. Longer fight → more Wails → higher per-seat, per-turn damage. Co-op pushes the correct line even harder toward "ignore the illusion completely and race the caster."

## Fight-class reasoning — `gimmick`

The per-turn demand this fight makes is unremarkable — a steady 16–26 incoming, one telegraphed intent per body, no burst window to survive and no wall to break through — right up until you make the wrong call, and then the whole fight changes shape. Everything that determines the outcome is a single knowledge check: the loud 21-HP thing in front is an unkillable decoy that revives to full, laundering your debuffs and keeping its Strength, while the real 123-HP win condition stands behind it Wailing +3 to both attackers every third turn. A player who knows this fights a mild, short attrition curve; a player who doesn't spends turns re-killing a free respawn while the enrage compounds against them, which is the same fight with an unbounded clock. `attrition` under-reads it because the health pool you actually must remove is small and the block in the kit is negligible, `spike` is plainly wrong — there is no single turn to survive — and `mixed` would imply two genuinely different demand phases when the fight only ever asks for one thing, gated on one binary insight.
