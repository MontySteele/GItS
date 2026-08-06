# The Merchant??? — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `FakeMerchantMonster`
- **Kind:** elite
- **Act:** Acts 2–3 (the parent event refuses to appear while the run's act index is below 1)
- **Encounter:** `FakeMerchantEventEncounter` — a **solo** body in a single `merchant` slot. Both the possible-monster pool and the generator contain exactly one entry: no adds, no summons, no variants. The encounter is typed as a normal monster room but carries a custom scene/background and a flat elite-sized purse (300 gold, min = max).
- **Entry:** not a map elite. It is reached only by **throwing a Foul Potion at the fake merchant** during the `FakeMerchant` event; combat is entered without exiting the event and the event does not resume afterwards.
- **Proposed fight class:** `mixed`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

Four moves on a small weighted state machine. The opening state is **Swipe**, and the machine will not transition away from its initial state until a move has actually resolved, so **turn 1 is always Swipe** on every seed.

The moves:

1. **Swipe** — single-attack intent.
2. **Spew Coins** — multi-attack intent, **8 hits**.
3. **Throw Relic** — single-attack intent **plus** a debuff intent (Frail).
4. **Enrage** — buff intent, no damage.

Two different random branch nodes decide what comes next, and which node you land in is decided by the move you just saw:

- **After Swipe, Spew Coins, or Enrage** → the *general* branch: Swipe / Spew Coins / Throw Relic / **Enrage**, equal weight.
- **After Throw Relic** → the *attack-only* branch: Swipe / Spew Coins / Throw Relic, equal weight. **Enrage is not reachable from Throw Relic.**

Two filters trim those lists at roll time:

- **No move repeats back-to-back.** Every branch is registered as non-repeating, so the move that just resolved has its weight zeroed. In practice that means the general branch is a flat **1/3 each** over the three moves that aren't the one you just saw, and the attack-only branch after Throw Relic is a flat **1/2 Swipe / 1/2 Spew Coins** (Throw Relic cannot follow itself).
- **Enrage carries a 3-move cooldown.** If Enrage appears anywhere in the last three logged moves its weight is zero. The fastest legal cadence is therefore **once every four turns**; the general branch is a straight 1/3 chance only when the cooldown has expired, and it is 1/2 Swipe / 1/2 Spew Coins otherwise (or after Throw Relic).

Net read for the player: **the fight never shows the same intent twice in a row, never buffs two turns apart, and never buffs immediately after a Frail turn.** There is no HP threshold, no phase change, no opening-turn skip, and no scripted script beyond the guaranteed Swipe on turn 1. Each move plays a randomly chosen barker line before it resolves, so the flavor text is not a tell.

## Numbers

| Value | Base | Ascension-modified |
| --- | --- | --- |
| Initial HP | 165 flat (min = max, no roll) | 175 flat (Tough Enemies tier and above) |
| Swipe damage (printed) | 13 | 15 (Deadly Enemies tier and above) |
| Spew Coins damage per hit | 2 | 2 (**no** ascension scaling) |
| Spew Coins hit count | 8 | 8 (no scaling) |
| Throw Relic damage (printed) | 9 | 10 (Deadly Enemies tier and above) |
| Throw Relic rider | Frail 1 | Frail 1 (no scaling) |
| Enrage | +2 Strength to itself, permanent | +2 (no scaling) |
| Block gained | none | none |

The printed numbers understate the fight badly, because Strength is added **per hit** and one of the moves has eight of them. Effective damage at a given Strength `S`:

| Move | Effective damage |
| --- | --- |
| Swipe | 13 + S (15 + S at Deadly) |
| Spew Coins | 8 × (2 + S) = **16 + 8S** |
| Throw Relic | 9 + S (10 + S at Deadly) + Frail 1 |

Each Enrage is therefore worth **+2 on a Swipe turn and +16 on a Spew Coins turn**. A worst-case cadence (Enrage taken the instant its cooldown allows) looks like:

| Turn | 1 | 2 | 3–5 | 6 | 7–9 | 10 | 11–13 | 14 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Move | Swipe | Enrage | attacks | Enrage | attacks | Enrage | attacks | Enrage |
| Strength | 0 | → 2 | 2 | → 4 | 4 | → 6 | 6 | → 8 |
| Spew Coins if rolled | 16 | — | 32 | — | 48 | — | 64 | — |
| Swipe if rolled | 13 | — | 15 | — | 17 | — | 19 | — |

Against a 165–175 HP body with no block and no healing, a typical deck spends roughly 6–10 turns in this fight, which is exactly the window in which Spew Coins goes from 16 to 32–48. The average opening-phase output is modest (mean ≈ 11 per turn across the four moves at Strength 0, since Enrage deals nothing), which is precisely why the fight is dangerous: the early turns feel survivable and the late ones are not.

## Gimmicks

- **The whole encounter is opt-in, and it is a heist.** The fight only exists if the player throws a **Foul Potion** (an event-rarity potion, 12 damage in combat / 100 gold if thrown at a *real* shopkeeper) at the fake merchant. Choosing to fight is choosing to convert a potion into an elite.
- **Loot-the-shop reward structure.** On death the player takes the flat **300 gold**, the event relic **Fake Merchant's Rug**, *and a copy of every relic still stocked on the fake merchant's shelf*. The shelf is 6 relics drawn from a pool of 9 fakes at **50 gold each**. Since unsold stock becomes free loot, **buying anything before the fight is strictly a waste of gold** — the purchase removes the item from the reward list in single-player.
- **The stock is a trap in itself.** The nine buyables are degraded knock-offs of familiar relics — 4 block at combat start, 3 block on a condition, heal 1, heal 10% on pickup, +3 max HP, +1 energy on a delayed/one-shot trigger, +1 damage, and a "Snecko" that applies **Confused with none of the draw upside**. A player who spends 300 gold on the shelf has bought six near-dead relics *and* forfeited them as free rewards.
- **Frail × 8-hit is the defensive puzzle.** Throw Relic applies **Frail 1** (block gained cut to 75%, ticking down at the end of the enemy turn), so the very next turn's block is reduced — and there is a 1/2 chance that next turn is the 8-hit Spew Coins. Frail is never applied on the same turn as the buff, but the sequencing consistently lands the reduced-block turn in front of a multi-hit.
- **Multi-hit texture swings mitigation wildly.** 8 × 2 is nearly free against a flat block wall and brutal against per-hit chip strategies or a Frail'd partial block; per-hit triggers (thorns, retaliation, on-hit procs) get eight activations on a Spew turn and one on the others. Any effect that reads "per hit" should be evaluated against this fight twice.
- **Strength removal is the designed lever.** Every escalation routes through one Strength stat, uncapped and never decayed, with no artifact-style protection and no self-block to protect it. Removing 2 Strength is worth 16 damage on a Spew turn. Weak is equally live — nothing in the kit resists debuffs.
- **No defensive kit at all.** No block, no heal, no summon, no revive, no HP-gated second phase. Every point of damage the player lands sticks.

## Scaling by act / ascension

- **Act:** no per-act combat variant — none of the monster's numbers read the act index. The act index only gates *availability* (Acts 2–3 only) and feeds the multiplayer HP scaler. Note the consequence: the same 165 HP / 13-damage statline is offered as an Act 2 detour and as an Act 3 detour, so it is relatively much softer in Act 3.
- **Ascension:** two independent tier bumps.
  - *Tough Enemies tier:* HP 165 → **175** (+6%). Min and max are equal at both tiers, so HP is never rolled.
  - *Deadly Enemies tier:* Swipe 13 → **15**, Throw Relic 9 → **10**.
  - **Spew Coins, the hit count, the Frail stack, and the +2 Enrage are identical at every ascension.** This is unusual and worth flagging: the fight's scariest move and its entire escalation engine take **zero** ascension scaling, so the ascension gap here is far narrower than for most elites. High-ascension difficulty comes from the player's thinner resources, not from the monster.

## Multiplayer / seat-count adjustments

- **The event refuses to spawn in co-op.** The gating check rejects the event outright when the run has more than one player (it also requires every player to hold either 100+ gold or a Foul Potion). As shipped, **this fight is single-seat content.**
- **The plumbing behind it is multi-seat-aware anyway,** which reads as a co-op enable being deliberately held back rather than never designed:
  - The Foul Potion throw fans out to every seat's copy of the event and starts the fight for all of them.
  - The reward loop grants **each player** their own Fake Merchant's Rug plus a copy of the shelf relics — and in multiplayer the "still stocked" filter is bypassed, so **every player is rewarded every shelf relic even if it was bought**.
  - Standard enemy HP scaling would apply: max HP × player count × the act factor (**1.2** in Acts 2 and 3), i.e. roughly **396 HP at 2 players / 594 at 3** (420 / 630 on the Tough Enemies tier).
  - The multiplayer *block* scaler is irrelevant — this monster gains no block.
- If the fight is ever enabled for co-op, the interaction to watch is Enrage against a table: +2 Strength is +16 damage **per seat** on a Spew Coins turn, against an HP wall that grew only 2.4×/3.6×.

## Fight-class reasoning — `mixed`

Turn to turn the demand starts as ordinary attrition: a 165–175 HP body with no block and no heal, dealing 9–16 per turn into a player who must simply keep covering while grinding it down. But the Enrage/Spew Coins interaction converts that baseline into a genuine spike threat on a random schedule — a single buff turn takes the 8-hit move from 16 to 32 to 48 to 64, and the player cannot know whether the turn after an Enrage is the cheap Swipe or the doubled multi-hit. The fight therefore asks two different questions at once: *sustain block through a Frail'd multi-hit for many turns*, and *race an uncapped Strength clock (or strip it) before one intent becomes a burst you cannot cover*. That is attrition body plus spike tail with an opt-in heist wrapper, which no single pure label describes — hence `mixed` rather than `attrition`.
