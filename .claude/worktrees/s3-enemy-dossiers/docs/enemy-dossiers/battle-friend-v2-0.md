# Battle Friend V2.0

- **Class:** `BattleFriendV2`
- **Kind:** normal
- **Act:** Act 3 (`Glory`, act index 2) — event-only
- **Encounter:** `BattlewornDummyEventEncounter`, spawned from the `BattlewornDummy` event ("Battleworn Dummy"), setting 2 of 3
- **Fight class:** `gimmick`

Behavioral notes only — derived from decompiled behavior, no source reproduced.

## Where it appears

Battle Friend V2.0 is not a map encounter. It is one of three difficulty settings of the Battleworn Dummy event, which sits in Act 3's event pool. Choosing setting 2 starts a combat containing exactly one monster: this dummy. The encounter is flagged as giving no standard combat rewards — the payout is handled by the event when combat resolves.

The event is a *shared* event in multiplayer (all seats resolve the same page), and the three options are presented with each dummy's HP number pre-computed and interpolated into the option text, so the player picks a difficulty knowing the exact HP bar they are signing up for.

Siblings, same behavior in every respect but HP and skin:

| Setting | Monster | HP (solo) | Reward on win |
|---|---|---|---|
| 1 | Battle Friend V1.0 | 75 | 1 random potion (character pool + shared pool) |
| **2** | **Battle Friend V2.0** | **150** | **Upgrade 2 random upgradable cards in your deck** |
| 3 | Battle Friend V3.0 | 300 | Next relic off the run's relic queue |

## Statline

- **HP:** 150, fixed (min and max initial HP are the same value — no roll, no variance).
- **Damage dealt:** none, at any point, ever.
- **Block gained:** none.
- **Powers applied to the player:** none.
- **Debuffs/status inflicted:** none.

## Intent pattern

There is effectively no AI. The move state machine has a single state, a do-nothing move, whose follow-up is itself — so the machine loops on that one state for the whole combat and the dummy performs a no-op on every one of its turns. Because the move state is constructed without any intent descriptors attached, the creature displays no intent icon above it; the player sees a health bar and nothing else.

The only dynamic element is a counter power applied to the dummy the moment it enters the room, starting at **3**. At the end of each side turn in which the dummy participated, the counter ticks down by one. When it would tick below one, the dummy **escapes** (it does not die, it leaves), and the encounter records that the player ran out of time.

Net effect: the player has **three turns** to deal **150 damage** to a target that never retaliates. Turn one is not free — the counter is already ticking when the first player turn ends.

## Gimmicks

1. **Timer, not a threat.** The entire fight is a hidden-clock DPS check. The dummy's only mechanic is the countdown power, which the player can read as a counter on the dummy.
2. **Escape, not death, on failure.** Running the clock out ends the combat with the dummy fleeing intact. The encounter sets its "ran out of time" flag, and the event then shows a defeat page and awards nothing. Nothing punishes the player beyond the opportunity cost — no HP is lost, no curse is added, no relic is taken.
3. **Zero defensive demand.** Block, thorns, artifacts, and healing are all dead weight in this fight. Only raw output per turn matters, and only three turns of it.
4. **Self-selected difficulty.** The player chooses the HP wall (75 / 150 / 300) against a fixed three-turn budget, so the fight is really a self-assessment: "can my deck do 50 per turn right now?" V2.0 is the middle rung, roughly 50 damage/turn, paying two upgrades.
5. **No rewards from the combat itself.** The encounter suppresses normal combat rewards; the payout arrives only through the event's resume path.

## Scaling

**By act:** none intrinsic. The monster's HP is a hard constant and the event only exists in Act 3, so there is no act-dependent statline. The act index does enter the HP formula, but only through the multiplayer multiplier below.

**By ascension:** no ascension-specific behavior is present on this monster — no HP bump, no extra timer pressure, no move changes. Any ascension effect would have to come from global systems, not from this fight.

**By seat count (multiplayer):** HP scales, the timer does not. The shared scaling helper leaves HP untouched at one player; with two or more it multiplies base HP by the player count and then by an act-index factor (1.1 in Act 1, 1.2 in Act 2, 1.2 in Act 3 for non-boss rooms, 1.3 only for Act 3 bosses). Since this encounter is a monster room in Act 3, the factor is **1.2**.

| Players | V2.0 HP | Damage needed per player-turn (3 turns) |
|---|---|---|
| 1 | 150 | 50 |
| 2 | 360 | 60 per seat |
| 3 | 540 | 60 per seat |
| 4 | 720 | 60 per seat |

The same numbers are pre-computed for the event's option text, so the co-op party sees the scaled wall before committing. Note the per-seat requirement *rises* from 50 to 60 the moment a second player joins and then stays flat: the fight is meaningfully harder in co-op than solo, and the countdown does not get more turns to compensate. The reward does not scale — setting 2 still upgrades two cards for the player who owns the event resolution.

## Proposed fight class: `gimmick`

Every turn of this fight asks exactly one question — "how much damage can you put out right now?" — and asks nothing else. There is no incoming damage to block, no debuff to play around, no positioning or target priority, and no threat curve, so the standard demand model (survive-while-you-kill) has no purchase here; what governs is a single non-standard rule, a three-turn escape timer bolted onto an inert 150 HP target. It is not `spike`, because a spike fight demands defensive readiness against a burst the enemy delivers, and this enemy delivers nothing; it is not `attrition`, because the fight is hard-capped at three turns and resource grind never enters. The correct read for Track B is a fight whose demand curve is a flat, pure-offense line terminated by a hard deadline, with the failure penalty paid in foregone reward rather than HP — a `gimmick` fight in the truest sense, and one whose difficulty the player selects for themselves.
