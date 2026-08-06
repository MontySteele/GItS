# The Adversary Mk 2 — behavior dossier

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `TheAdversaryMkTwo`
- **Kind:** boss
- **Act:** **unassigned in the shipped data.** No act's boss-discovery list, no encounter model, and no other class in the tree references this monster; the only mention outside its own file is the type-registry table. Its power band places it squarely between Mk 1 and Mk 3 (see below), i.e. it reads as the **Act 2 rung of a three-rung boss ladder**, but nothing in code routes a run into it. Treat it as bestiary / test / unshipped content.
- **Encounter:** none. It has no encounter definition, therefore no add roster, no summons, and no companion monsters. If it is ever instantiated it fights alone.
- **Proposed fight class:** `attrition`

*Behavioral notes only — no decompiled source is reproduced here.*

## The Adversary ladder (context)

Three sibling classes exist — `TheAdversaryMkOne`, `TheAdversaryMkTwo`, `TheAdversaryMkThree` — and they are the **same fight three times** with every dial turned up. Identical three-state cycle, identical move construction, identical lack of block/debuff/summon; only HP, the three damage numbers, the Strength tick, and the Artifact count differ. This makes Mk 2 the middle rung of a deliberately linear difficulty ladder rather than a distinct design.

| | Mk 1 | **Mk 2** | Mk 3 |
| --- | --- | --- | --- |
| HP (flat, no roll) | 100 | **200** | 300 |
| Move 1 (single attack) | Smash 12 | **Bash 13** | Crash 15 |
| Move 2 (single attack) | Beam 15 | **Flame Beam 16** | Flame Beam 18 |
| Move 3 (multi-attack) | Barrage 8×2 | **Barrage 9×2** | Barrage 10×2 |
| Strength gained per cycle | +2 | **+3** | +4 |
| Artifact applied on entry | 0 (a no-op) | **1** | 2 |

## Intent pattern

A three-state move machine with **zero randomness** — no random branch, no conditional branch, no HP threshold, no enrage state. Each state hard-wires its follow-up, so the loop is fixed and plays identically on every seed:

1. **Bash** — single-attack intent. This is the **initial** state, so it is what the player sees on turn 1.
2. **Flame Beam** — single-attack intent. Follow-up of Bash.
3. **Barrage** — shows a **multi-attack intent *and* a buff intent side by side** (the only turn the player gets a buff telegraph). Follow-up of Flame Beam; its own follow-up is Bash.

The whole fight is **Bash → Flame Beam → Barrage → Bash → …** forever. The machine will not transition away from its initial state until a move has actually resolved, so the opening Bash is guaranteed — there is no "skips its first turn" behaviour. A player who has seen one cycle knows every future intent, including exactly which turn the self-buff lands.

The buff telegraph is the only decision-relevant signal: turn 3 of every cycle is both the biggest hit *and* the turn the fight gets permanently worse.

## Numbers

| Value | Base | Ascension-modified |
| --- | --- | --- |
| Initial HP | 200 flat (min = max, never rolled) | **200 — unchanged** (the Tough Enemies hook is present but its ascension value equals its fallback, so it is a no-op) |
| Bash damage (printed) | 13 | 13 |
| Flame Beam damage (printed) | 16 | 16 |
| Barrage damage per hit (printed) | 9 | 9 |
| Barrage hit count | 2 | 2 |
| Strength gained, per Barrage | +3, permanent | +3 |
| Artifact on entry | 1 counter | 1 |
| Block gained | none, ever | none |
| Debuffs applied to the player | **none** | none |

The printed numbers are not what the player eats after the first cycle, because Barrage self-buffs. Effective per-turn damage, base values, assuming no Strength removal:

| Turn | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Move | Bash | Beam | Barrage | Bash | Beam | Barrage | Bash | Beam | Barrage | Bash | Beam | Barrage |
| Strength when acting | 0 | 0 | 0 | 3 | 3 | 3 | 6 | 6 | 6 | 9 | 9 | 9 |
| Damage | 13 | 16 | 18 | 16 | 19 | 24 | 19 | 22 | 30 | 22 | 25 | 36 |

Cumulative unblocked damage: 13 / 29 / 47 / 63 / 82 / 106 / 125 / 147 / 177 / 199 / 224 / 260 after turns 1–12.

Two shape facts:

- **Damage per cycle rises by a flat +12.** Cycle totals are 47 / 59 / 71 / 83 / …. Each point of Strength is worth +1 on Bash, +1 on Flame Beam and **+2 on Barrage** (Strength is added per hit), so +3 Strength buys +12 per cycle. The curve is linear, not exponential — the fight gets worse steadily and never suddenly.
- **Barrage is the only move that pulls away.** It starts as the biggest turn (18 vs 13/16) and widens the gap every cycle because it double-dips Strength. By turn 12 it is 36 against Bash's 22. A long fight is lost to Barrages.

Against a boss-slot HP pool this is roughly a **six-to-nine-turn death clock** solo, and the DPS check runs the other way: 200 HP with no block and no healing means the player needs ~25–35 damage per turn to close inside the comfortable window.

## Gimmicks

The kit is deliberately thin. There are exactly two mechanics on top of a plain attack cycle:

- **Artifact 1 on entry (the real gimmick).** On being added to the room it applies **one Artifact counter to itself**, permanently, before the first turn. Artifact zeroes out the *next* incoming visible debuff aimed at the owner and then decrements itself, so exactly **one** Weak / Vulnerable / Strength-down / any other player-applied debuff is eaten and wasted. It only intercepts effects that resolve as debuffs and are visible; non-debuff and hidden effects pass through untouched.
  - Practical consequence: the obvious counterplay to a Strength-ramping body — strip the Strength, apply Weak — has a **one-charge tax on it**. A player whose plan is "one big Weak" gets that plan deleted; a player who can apply debuffs twice barely notices. This is a check on debuff *redundancy*, not on debuff access.
  - The Mk 1 sibling applies Artifact **0**, i.e. the same call with no effect at all; Mk 3 applies 2. The ladder's only qualitative escalation is how many debuffs get eaten.
- **Barrage self-Strength (+3, permanent, no cap, no decay).** Applied *after* the Barrage damage resolves, so the Barrage that grants it does not benefit from it. There is no threshold, no announcement turn beyond the standing buff intent, and nothing removes it but the player.

Things the fight conspicuously **does not** have, all of which matter for planning:

- No block, no thorns, no self-heal, no damage reduction. Every point the player deals sticks; there is no wasted-damage or race-against-block texture.
- No player-facing debuff of any kind. Nothing attacks the hand, the deck, energy, or draw. The player's engine is never disrupted — only their HP bar.
- No adds, no summons, no minions to split targeting.
- **A declared-but-unused status count on Flame Beam.** The model carries a "flame beam status count = 1" value that no shipped code path reads: Flame Beam deals its damage and applies **nothing**. Its intent is a plain single attack with no debuff icon. Read this as a planned Burn-style rider that was never wired up — further evidence this monster is unfinished content. Do not model a Flame Beam debuff.

## Scaling by act / ascension

- **Act:** none. No combat value reads the act index, and no act routes to this monster at all. (The act index does feed the multiplayer HP scaler — see below.) The "scaling by act" for this creature is expressed by *swapping in a different sibling class*, Mk 1 → Mk 2 → Mk 3, not by scaling Mk 2.
- **Ascension: none — and this is a notable gap.** The HP getter goes through the Tough Enemies ascension helper but passes the same value (200) for both branches, so it resolves to 200 at every ascension. The damage numbers, the hit count, the Strength tick and the Artifact count are plain constants with no ascension hook whatsoever. **The Adversary Mk 2 is identical at ascension 0 and at max ascension.** Mk 3 has the same no-op HP hook; Mk 1 does not even have the hook. Contrast a shipped elite like the Byrdonis, which carries two separate ascension bumps — the absence here is a strong signal this fight never went through balance.

## Multiplayer / seat-count adjustments

- **HP scales hard.** With more than one player, enemy max HP is multiplied by (player count × an act factor: 1.1 in Act 1, 1.2 in Act 2, 1.3 for an Act 3 boss room). Because no act owns this fight, the exact figure depends on where it is placed. At the Act 2 factor that is **480 HP at 2 players** and **720 at 3**; if it were dropped into an Act 3 boss slot, 520 / 780.
- **Every move hits every seat for full value.** All three attacks are constructed as monster attacks targeting *all opponents*, and with multiple live targets the damage is dealt to the whole list rather than to one randomly chosen seat. In co-op **each player eats the full Bash, the full Flame Beam and both Barrage hits every cycle** — nothing is split, nothing is rolled. Table-wide incoming damage is a clean linear multiple of seat count (cycle 1 = 94 at 2P, 141 at 3P).
- **Artifact scales with seats: +1 counter per extra player.** Artifact is flagged for multiplayer scaling and gains (player count − 1), so the boss enters with **2 Artifact at 2 players** and **3 at 3 players** — one free debuff negation per seat. This is the single mechanic that gets qualitatively harder in co-op rather than just numerically bigger: a team that pools its debuffs onto one big application loses all of it, and each additional seat adds another wasted application.
- **Strength does not scale with seats,** but its cost to the table does: +3 Strength is +12 damage per cycle *per seat*, so a single Barrage tick is worth 36 team damage at 3 players.
- **Block scaling is irrelevant** — the multiplayer scaler that inflates enemy block only touches enemies that gain block, and this one never does.
- Net co-op read: the HP wall grows ~2.4×/3.6× while per-cycle table damage grows 2×/3× *and* ramps, and the debuff answer costs one extra application per seat. Extra seats buy no slack.

## Fight-class reasoning — `attrition`

Every turn asks the same question with a slowly bigger number attached: cover 13 / 16 / 18 *per seat*, rising by a flat +12 per cycle, while grinding a 200 HP body (480+ in co-op) that never blocks, never heals, never summons, and never touches the player's hand or energy. Within a cycle the damage spread is narrow (13–18 at cycle 1), so there is no turn worth banking a hoard of block for and nothing that resembles a `spike` — the demand curve is a rising line with no gaps, which is the attrition profile. The Artifact charge is a genuine mechanic and it is the fight's only puzzle, but it gates one debuff application rather than posing a lock the player must solve, so `gimmick` overstates it; the Barrage double-dip and the Artifact tax simply mean the sustained-damage race is decided by whether the deck's per-turn output beats a linearly worsening clock. Classify as `attrition`, with the caveat that its numbers are unratified — no ascension scaling exists and no encounter ships it.
