# Living Shield — behavior dossier

- **Class:** `LivingShield`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 3 (`Glory`, act index 2)
- **Encounter:** `TurretOperatorWeak` only — a two-body **weak** encounter (one Living Shield + one Turret Operator, both always present, no randomisation). Act 3 seeds 2 weak encounters, so this is a first-or-second-room fight of the act. Living Shield appears in no other encounter and is never summoned.
- **Proposed fight class:** `gimmick`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

Three states, one of them a hidden conditional branch. There is no randomness anywhere in the machine — the Living Shield's entire AI is a single question asked once per turn: **"is anything else on my side still alive?"**

- **Turn 1 — Shield Slam.** The machine starts in the Shield Slam state and the first move never transitions away, so the opener is fixed. Shows a plain single-attack intent for **6**.
- **Every turn after — branch.** Shield Slam's follow-up is a conditional branch (invisible in the intent log) that counts living teammates other than itself:
  - **≥ 1 ally alive → Shield Slam again.** In practice this means "while the Turret Operator lives", and it is the state the fight normally stays in from start to finish.
  - **0 allies alive → Smash.** Shows an attack intent *and* a buff intent together.
- **Smash self-loops forever.** Once the Living Shield is alone it never returns to Shield Slam. Each Smash deals its damage first and then applies **+3 Strength to itself**, permanently, so the solo mode is a hard escalation with no cap and no cooldown turn.

The branch is evaluated when the next intent is rolled, i.e. between the enemy turns — killing the Turret Operator flips the Living Shield to Smash on its very next telegraph, not on some delayed trigger.

**The passive is the real move.** On entering the room the Living Shield applies a **Rampart** counter to *itself* at **25**. Rampart fires at the start of each **player** turn and grants Block equal to its amount **to every living Turret Operator on the enemy side** — never to itself, never to "allies" generically. The filter is by monster type, which makes this a hard-wired partner dependency: the Living Shield exists to shield exactly one other unit in the game.

Two timing consequences worth writing down:

1. The Block lands at *player* turn start, so the turret is wearing it for the whole of the window in which the player is attacking, and it is wiped at the enemy's own turn start before the turret acts. It is perfectly efficient one-way mitigation — none of it is wasted soaking the turret's own turn.
2. The pump is **suppressed while any player is taking an extra turn**. Extra-turn effects therefore do not multiply the shielding, and in co-op the grant fires once per player-side turn regardless of seat count.

Rampart keeps ticking as long as the Living Shield is alive; it does nothing at all once the turret is dead (there is no fallback target, including itself).

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP | 55 (fixed — min and max are equal, no roll) | **65** (Tough-Enemies tier) |
| Shield Slam damage | 6 | 6 (no ascension scaling) |
| Smash damage | 16 | **18** (Deadly-Enemies tier) |
| Smash self-buff | +3 Strength, cumulative | +3 (no ascension scaling) |
| Rampart amount (Block/turn to the turret) | 25 | 25 (no ascension scaling) |
| Block on itself | none, ever | none |

Its damage-SFX category reads as **armor** rather than flesh, and it has **no death SFX** — cosmetically it is a piece of equipment, not a creature.

Solo-mode damage curve, once the turret is dead: **16, 19, 22, 25, 28, 31 …** (18, 21, 24, 27 … at the Deadly-Enemies tier). The telegraphed number climbs with the accumulated Strength, so the escalation is visible a turn ahead.

**The partner, for context** (its own dossier covers it properly): Turret Operator sits at 41 HP (51 at the Tough-Enemies tier) and runs a fixed 3-beat loop — Unload (**5 hits of 3**, 4 at the Deadly-Enemies tier), Unload again, then Reload (**+1 Strength to itself**, worth +5 damage per Unload because Strength applies per hit).

**The arithmetic of the fight, both bodies alive:**

- Incoming per enemy turn: 6 (Shield Slam) + 15 (Unload) = **21**, rising by 5 every third turn as the turret Reloads. On a Reload turn you take only 6.
- Outgoing requirement to remove the turret in one player turn: **25 Block + 41 HP = 66 damage**, and 25 of that is refunded on the next player turn if you fall short. Chipping the turret through the pump is arithmetically impossible with any normal Act-3 turn — the shield is not a soft tax, it is a lockout.
- Outgoing requirement to remove the Living Shield: a flat **55**, unblocked, on a body that never gains Block and never heals. It is by a wide margin the softest 55 HP in the act.

So the intended line is unambiguous: kill the Living Shield first, eat ~21/turn while you do it, then fight a naked 41-HP turret. The Smash branch exists to punish the player who inverts that order with a burst/AoE turn — it is a *penalty state*, not part of the normal fight.

## Gimmicks

- **Block laundering, hard-target variant.** Like the Act 3 Guardbot, the Living Shield converts its own HP bar into recurring mitigation on a partner. Unlike the Guardbot, the exchange rate is not a tempo question but a gate: 25 Block against a 41-HP body means the protected unit is effectively unkillable while the shield stands.
- **It cannot protect itself.** The Rampart filter names the Turret Operator specifically. The Living Shield takes every point of damage on the chin. This is the whole reason the fight has a correct answer.
- **Conditional enrage.** Alone, it stops being a shield and becomes a snowballing bruiser: 16-and-climbing with permanent +3 Strength per turn and a full HP bar (it will not have taken meaningful damage in the line where this triggers). Killing the turret first converts a 21-damage-per-turn fight into a 16 → 19 → 22 → 25 race against 55 HP you have not touched.
- **No debuffs, no summons, no death rattle, no HP-threshold behavior.** The kit is two attacks and one aura.
- **Block-ignoring damage is the only genuine alternative line.** Anything that bypasses the turret's Block (rather than chewing through it) sidesteps the entire gimmick and lets a player kill the turret cheaply — at the cost of walking straight into the enrage. Worth flagging for any of our own kits that lean on unblockable or end-of-turn tick damage: this fight rewards them and then bills them.
- **AoE is the clean answer.** Splitting output across both bodies makes progress on the shield while the turret's Block absorbs the rest; the encounter is one of the act's better arguments for a two-target card.
- **Both bodies are primary enemies.** Neither is a minion — killing one does not clear the other, and there is no free cleanup like the Fabricator's bots.

## Scaling by act / ascension

- **Act:** none. It is Act 3 content only and reads no act index directly; the only act-derived factor that touches it is the multiplayer scaler below.
- **Ascension:**
  - *Tough Enemies* tier: HP 55 → **65** (+18%). The single toughest change, since HP-on-the-shield is exactly the resource the fight measures.
  - *Deadly Enemies* tier: Smash 16 → **18**. Note this touches **only the penalty state** — a player who takes the intended line never sees a Deadly-Enemies difference on this unit at all. Shield Slam's 6 and Rampart's 25 are both flat at every ascension.
  - Net: the ascension curve on this enemy is almost entirely "the gate takes 2 more turns to open", which compounds with the turret's own ascension bump (41 → 51 HP, 15 → 20 per Unload) rather than adding a new threat.

## Multiplayer / seat-count adjustments

- **HP scales.** Enemy max HP is multiplied at creation by (player count × act factor); the Act 3 non-boss factor is **1.2**. Two seats ≈ **132 HP** (158 at the Tough-Enemies tier), three seats ≈ **198** (234).
- **The Rampart amount scales too — and this is the important one.** Rampart is flagged as a multiplayer-scaling power and it is applied to a primary enemy, so the counter itself is multiplied by (player count × 1.2) when it is placed at the start of combat: **25 → 60 at two seats, 90 at three.** The Block it hands out then follows the counter. Note the mechanism: the Block *grant* is issued unpowered and slips past the multiplayer block multiplier entirely (the same quirk that leaves Guardbot's grant flat) — the scaling arrives via the power's amount instead, and it arrives in full.
- **Consequently the gate does not soften with seats; it hardens in step.** At three players the turret is a ~99-HP body behind 90 Block per turn — 189 damage in one turn to remove it early. The lockout is, if anything, more absolute in co-op than in single-player, which is the opposite of how the Guardbot's shield behaves.
- **Damage is not per-seat.** Shield Slam and Smash are ordinary single-target monster attacks; more seats means more total HP on the player side against the same 6-or-16, so the *pressure* half of this enemy dilutes at the same time its *gate* half sharpens. Co-op turns the encounter into an almost pure race against two large HP bars.
- **The enrage is proportionally weaker in co-op.** +3 Strength per turn against a 3-seat player pool is a much slower clock than against one, so the mis-ordering penalty is at its most punishing in single-player.

## Fight-class reasoning — `gimmick`

Per turn this enemy asks for very little: 6 damage from a fixed opener that never varies, no debuff, no status, no summon, and no threshold surprise — the mitigation requirement it contributes to the encounter's demand curve is essentially flat and small. What it demands instead is a **targeting rule**, and it enforces that rule with an on/off lockout rather than a tax: 25 Block per player turn on a 41-HP partner means "kill me first" is not a preference but the only arithmetically available line, and the Smash branch exists purely to bill the player who found a way around it. That is a rules-modifier unit — it changes what *correct* means, not what *surviving the turn* costs. `attrition` is the near-miss (the fight is a slow 21-a-turn grind while you chew the gate open), but the grind is a consequence of the lockout rather than the thing being tested, and the Smash escalation is too conditional — a state most players never see — to justify `spike` or `mixed`.
