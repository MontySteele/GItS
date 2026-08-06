# Enemy Dossier — Battle Friend V3.0

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `BattleFriendV3`
- **Kind:** normal (monster model; appears as the sole combatant of an event encounter)
- **Act:** Act 3 (`Glory`, act index 2) — the only act whose event pool contains the Battleworn Dummy event
- **Encounter:** `BattlewornDummyEventEncounter`, setting 3 of 3
- **Fight class:** `gimmick`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table description of observed mechanics and constants.

---

## 1. What this fight is

Battle Friend V3.0 is not a combat enemy in the normal sense. It is the hardest of three
selectable *training dummies* offered by the Battleworn Dummy event. The event presents three
settings; each starts a real combat against one dummy with a fixed HP total, and each pays a
different reward if you kill it in time:

| Setting | Monster | HP (single player) | Reward on kill |
|---|---|---|---|
| 1 | Battle Friend V1.0 | 75 | A random potion (character pool + shared pool) |
| 2 | Battle Friend V2.0 | 150 | Upgrade 2 random upgradable cards in your deck |
| 3 | **Battle Friend V3.0** | **300** | The next relic off the front of your relic queue |

The event advertises the three HP numbers up front (and shows them already adjusted for
multiplayer/act scaling), so the choice is an informed damage-per-turn bet, not a gamble.

## 2. Intent pattern / AI

There is none, in the meaningful sense. The move state machine has exactly one state — a
do-nothing move — and that state's follow-up is itself. It therefore telegraphs the same
"does nothing" intent every turn, forever, and never transitions.

- **Attacks:** none.
- **Block:** none. It never gains Block, so multiplayer enemy-Block scaling never applies to it.
- **Debuffs/buffs applied to the player:** none.
- **Powers it starts with:** one — a self-applied counter buff, the Battleworn Dummy time limit,
  at **3 stacks**, applied when it is added to the room.

## 3. The time limit (the entire gimmick)

The time-limit power is a counter-stacked buff on the dummy. At the end of each turn in which
the dummy participated, it decrements by 1; when it would go below 1 instead of decrementing,
the dummy **escapes** the combat and the encounter is flagged as "ran out of time."

Practical reading: **you get 3 player turns to deal 300 damage.** There is no partial credit —
escaping ends the fight with the event's defeat page and no reward at all. The encounter is
also flagged to give no normal combat rewards, so the *only* payout is the event's relic.

Consequences worth noting for balance work:

- The player is never in danger. Zero incoming damage, zero HP risk, zero attrition. The only
  cost of failure is the opportunity cost of the event slot.
- Effects that trigger on "enemy attacks," on taking damage, on being debuffed, or on blocking
  are all dead here. Thorns, retaliation, block-scaling, and defensive relics contribute
  nothing.
- The dummy leaves by escaping, not by dying, when the timer expires — so on-death triggers do
  not fire on a failure, and on-escape/on-flee interactions are the ones to watch.
- Because it is the primary enemy and never blocks, the effective demand is a raw
  **100 damage per turn averaged over 3 turns**, with front-loading permitted (a single 300-damage
  turn wins just as well).

## 4. Scaling

**By act:** the enemy has no act-varying stats. Its HP is a hard constant (min = max = 300), and
because the event only appears in Act 3, there is no cross-act variation to model. The turn
budget (3) is likewise fixed.

**By ascension:** no ascension-conditional behavior exists on this model — no HP bump, no timer
reduction, no added moves. The difficulty of the check is entirely a function of how much damage
the player's Act 3 deck can produce in three turns.

**By seat count (multiplayer):** the dummy's HP is scaled by the shared multiplayer HP formula —
base HP multiplied by the number of players and by an act-dependent factor. For Act 3 non-boss
encounters that factor is **1.2**. So:

| Players | Battle Friend V3.0 effective HP |
|---|---|
| 1 | 300 (no scaling applied at 1 player) |
| 2 | 720 |
| 3 | 1080 |
| 4 | 1440 |

The event text is regenerated with these scaled numbers before the options are shown, so the
displayed HP is already the true target. Note the scaling is *super-linear per seat* (players ×
1.2), which makes setting 3 measurably harder per-player in co-op than solo — the group needs
360 damage per player over the same 3 turns rather than 300. The enemy-Block multiplayer scaling
in the same system never applies, since the dummy gains no Block.

## 5. Cosmetic / presentation notes

The three Battle Friends are the same skeleton with different skins (v1/v2/v3); V3.0 selects the
"v3" skin. Its animation set is idle / hurt / die only — there is no attack animation, which is
consistent with a monster that has no offensive move. The event is shared across seats in co-op
(one choice for the table, not per-player).

## 6. Proposed fight class — `gimmick`

The fight makes exactly one demand and it is not a combat demand: produce 300 (or 360/player in
co-op) damage inside a hard 3-turn window, against a target that never attacks, never blocks,
and never changes intent. Nothing about defense, sequencing around incoming damage, or HP
attrition is tested, which rules out `spike` and `attrition`; there is one body, which rules out
`swarm`; and the single rule is unusual enough — a race timer with all-or-nothing payout — that
it is not a `mixed` blend of ordinary combat pressures. For Track B's demand curve this should
be treated as a pure **burst-throughput check with zero defensive load**, and it is a useful
calibration probe precisely because it isolates the offense axis: whether a deck clears setting 3
is a direct readout of its 3-turn damage ceiling at that point in Act 3.
