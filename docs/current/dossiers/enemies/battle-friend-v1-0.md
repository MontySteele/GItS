# Battle Friend V1.0

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `BattleFriendV1`
- **Kind:** normal
- **Act:** 3 (Glory, act index 2) — event-only
- **Encounter:** `BattlewornDummyEventEncounter` (event `BattlewornDummy`, "Battleworn Dummy")
- **Fight class:** **gimmick**

> Behavioral notes only — derived from decompiled behavior, no source reproduced.

## Where it appears

Battle Friend V1.0 is never rolled into the normal/elite encounter pools. It exists solely as the
lowest of three difficulty settings for the Act 3 event *Battleworn Dummy*. The event offers three
options; each one starts a combat against exactly one dummy, and the dummy chosen is the option's
tier:

| Setting | Monster | Base HP | Reward on success |
|---|---|---|---|
| 1 | **Battle Friend V1.0** | 75 | a random potion (character pool + shared pool) |
| 2 | Battle Friend V2.0 | 150 | 2 random upgradable cards in the deck are upgraded |
| 3 | Battle Friend V3.0 | 300 | the next relic off the front of the relic queue |

The event text quotes the three HP totals live — the numbers shown are already multiplayer-scaled
before the option list is rendered, so the player is told the real target number.

The encounter itself grants no combat rewards (no gold, no card reward). Everything is paid out by
the event when it resumes. The dummy is a solo spawn; there is never a second monster.

## Intent pattern

There is none, in the literal sense. The move state machine holds a single state that does nothing
and loops back to itself forever. Every turn the dummy takes is a no-op: no attack, no block, no
buff, no debuff, no summons. Its animator only has idle / hurt / die states — it has no attack
animation at all, and its only VFX hook is a chip-spray particle burst fired off the hit animation.

The player therefore takes **zero damage** from this fight under all circumstances.

## Damage / block numbers

| Stat | Value |
|---|---|
| HP (min = max, no roll) | **75** |
| Damage dealt per turn | 0 |
| Block gained per turn | 0 |
| Powers applied to the player | none |
| Powers on itself | Time Limit, 3 |

## The gimmick: Time Limit 3

On entering the room, the dummy applies a counter-type buff to itself with 3 stacks. At the end of
each side turn in which the dummy participated, the counter drops by one. When it would tick below
1, the dummy does not die — it **escapes**, and the encounter is flagged as "ran out of time".

Consequences:

- The player gets **three turns of attacks** to remove 75 HP. Turn 3 is the last turn; failing to
  finish on it ends the fight immediately with the dummy fleeing.
- Failure is not a loss — the run continues, no HP is lost, no curse is taken. The event simply
  resolves to its defeat page and pays out nothing. The cost of failure is purely the forgone
  reward plus whatever consumables the player burned trying.
- Because the dummy escapes rather than dies, effects keyed on "enemy dies" / kill triggers do not
  fire on the timeout branch. Effects keyed on the enemy *escaping* would.
- Any player effect that reduces the number of turns available (self-inflicted end-turn effects) or
  that needs ramp time is actively punished; the fight rewards front-loaded burst and pre-combat
  setup, not engine building.

Note the timer is a decrementing counter on the monster, not a global room timer: it is in principle
manipulable by anything that removes or reduces enemy buff counters, and lengthening it would extend
the window. Nothing in the base game's Act 3 pool is obviously built to do this, but it is the one
exploit surface the fight has.

## Scaling

**By act:** none. The monster's HP is a fixed 75, not a range, and there is no act-based tuning on
the model. It only ever appears in Act 3, so no cross-act comparison exists.

**By ascension:** none present on this monster. No ascension branch touches its HP, its timer
length, or its (nonexistent) moves. The fight is identically hard at every ascension level — which
in practice means it gets *relatively* easier as decks get stronger and *relatively* harder only
insofar as ascension-driven deck constraints reduce burst.

**By seat count (multiplayer):** the dummy's HP goes through the standard multiplayer HP scale —
base HP × number of players × the act multiplier, which for a non-boss room in Act 3 is 1.2×. The
timer stays at 3 regardless of seat count.

| Players | Battle Friend V1.0 HP | Required damage/turn over 3 turns |
|---|---|---|
| 1 | 75 | 25 |
| 2 | 180 | 30 |
| 3 | 270 | 45 |
| 4 | 360 | 60 |

Because the timer does not scale but HP scales super-linearly with seat count (the 1.2× rides on top
of the per-player multiply), the per-seat damage requirement *rises* with party size: 25/turn solo
versus 30/turn per seat at four players. Co-op parties are held to a modestly stricter check than
solo, and a party with one under-scaled seat can fail a setting a solo player of the same power
would clear. Worth flagging for any co-op difficulty modelling: this is one of the few rooms where
the seat-count math changes the *pass/fail* answer rather than the damage-taken answer.

## Proposed fight class: **gimmick**

The fight demands nothing that a normal encounter demands. It asks for zero defense — no block, no
debuff mitigation, no HP management, because incoming damage is structurally zero — and instead
imposes a single inverted constraint: produce 25 damage per turn (more per seat in co-op) for three
turns or forfeit the reward. That is a rules-replacement, not a combat difficulty curve, so it
belongs in the gimmick bucket rather than spike (which implies incoming burst the player must
survive) or attrition (which implies a resource drain over time). For Track B's demand curve it
should be modelled as a pure output threshold with a hard turn cap and no defensive term at all —
and as a *choice* node, since the player picks which of the three thresholds to attempt.
