# Queen

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `Queen`
- **Kind:** boss
- **Act:** 3 (Glory, act index 2)
- **Encounter:** `QueenBoss` — two slots (`amalgam`, `queen`), boss room, custom BGM `act3_boss_queen`
- **Fight class:** **mixed**

> Behavioral notes only — derived from decompiled behavior, no source reproduced.

## Where it appears

The Queen is the first of Act 3's three bosses in the act's boss discovery order (ahead of the Test
Subject and Aeonglass). The encounter always spawns **two** creatures, and always in the same order:
the **Torch Head Amalgam** in the `amalgam` slot and the Queen in the `queen` slot. Slot order is
also enemy action order, so the Amalgam resolves its move before the Queen each enemy turn.

The Amalgam is not a summon and cannot be re-summoned; it is present from turn one and carries a
Minion marker, which means **its death does not end the combat and does not propagate a fatal
result** — the fight is explicitly designed around killing it partway through. The Queen's own death
ends the fight.

The boss shares Act 3's music-progress rig: the parameter is pushed to its opening value on entry,
bumped a step when the Amalgam dies, and pushed to the resolution value when the Queen dies. There
is also a purely cosmetic background variant — whether Repy appears behind the fight depends on
whether the player freed Repy at the War Historian event earlier in the run. Neither affects
gameplay.

Both the Queen and the Amalgam take damage with the "armor" sound family. The Queen also plays two
spoken lines: one on her turn-2 debuff move and one the moment the Amalgam dies.

## Intent pattern

The move machine is fully deterministic — no random branches anywhere. It has a **fixed two-move
opening**, then a **conditional lock** on whether the Amalgam is still alive, then a **three-beat
loop** for the rest of the fight.

**Phase 1 — the Amalgam is alive**

| Beat | Move | What it does | Intent shown |
|---|---|---|---|
| 1 | **Puppet Strings** | Applies Chains of Binding 3 to every player | card-debuff |
| 2 | **You're Mine** | Applies Frail / Weak / Vulnerable, 99 each, to every player | debuff |
| 3+ | **Burn Bright For Me** | +1 Strength to every ally (i.e. the Amalgam), Queen gains 20 block | buff + defend |

Burn Bright For Me loops onto itself indefinitely: after each cast the machine re-checks whether the
Amalgam has died, and if it has not, it repeats. **The Queen deals no damage at all while the
Amalgam lives.** Every point of incoming damage in Phase 1 comes from the Amalgam, and the Queen
spends every turn making the Amalgam bigger while walling herself behind block.

**Phase 2 — the Amalgam is dead**

| Beat | Move | What it does | Intent shown |
|---|---|---|---|
| 1 | **Off With Your Head** | 5-hit AoE attack | multi-attack (×5) |
| 2 | **Execution** | single-hit AoE attack | attack |
| 3 | **Enrage** | +2 Strength to herself | buff |

Then straight back to Off With Your Head, forever. Both conditional branch points (the one after
You're Mine, and the one after each Burn Bright) route to Off With Your Head once the Amalgam is
gone, so the Queen enters the damage loop on the very next turn regardless of where in Phase 1 the
Amalgam died.

**The immediate-swap rule.** If the Amalgam dies *while the Queen's already-telegraphed next move is
Burn Bright For Me*, the Queen forcibly re-rolls that queued intent to **Enrage** on the spot and
refreshes her intent display. So a player who kills the Amalgam during their own turn does not get a
free wasted-buff turn out of it — they instead hand the Queen a +2 Strength head start before the
first Off With Your Head. Killing the Amalgam on a turn where the Queen has *already* queued
something else does not trigger this.

**Bestiary display note.** Only You're Mine and Off With Your Head are exposed in the bestiary;
Puppet Strings, Burn Bright For Me, Execution and Enrage are hidden. A player reading the bestiary
therefore sees roughly half the fight, which is deliberate.

## Damage / block numbers

### The Queen

| Stat | Base | Ascension variant |
|---|---|---|
| HP (min = max, no roll) | **400** | **419** at A8 `ToughEnemies` |
| Off With Your Head — damage per hit | 3 | 4 at A9 `DeadlyEnemies` |
| Off With Your Head — hit count | 5 | 5 |
| Execution — damage | 15 | 18 at A9 |
| Enrage — Strength gained | 2 | 2 (not ascension-scaled) |
| Burn Bright For Me — Strength given to each ally | 1 | 1 (not ascension-scaled) |
| Burn Bright For Me — block gained | 20 | 20 (not ascension-scaled) |
| Puppet Strings — Chains of Binding applied | 3 | 3 |
| You're Mine — Frail / Weak / Vulnerable | 99 each | 99 each |

### The Torch Head Amalgam

| Stat | Base | A9 `DeadlyEnemies` |
|---|---|---|
| HP (min = max) | **199** | **211** at A8 `ToughEnemies` |
| Tackle | 18 | 19 |
| Weak Tackle | 14 | 15 |
| Soul Beam — damage per hit | 8 | 8 (unchanged) |
| Soul Beam — hit count | 3 | 3 |

Its own cycle is deterministic and does **not** return to the top: Tackle, Tackle, Soul Beam, Weak
Tackle, Weak Tackle, then it loops on the **last three only** — Soul Beam, Weak Tackle, Weak Tackle,
forever. The two opening 18s never come back. Every point of Strength the Queen feeds it is worth
**three** damage on the Soul Beam beat and one on the tackles, which is why the beam beat is the one
that runs away.

### The Strength curves

Two separate Strength ramps run in this fight, and they never overlap:

- **Phase 1** — the Amalgam gains +1 per Queen turn, starting from the first Burn Bright (turn 3).
  Amalgam damage at Strength *s* is 18+s / 14+s on tackles and (8+*s*)×3 = 24+3*s* on the beam.
- **Phase 2** — the Queen gains +2 every third turn. Her damage at *k* Enrages is 5×(3+2*k*) =
  **15 + 10k** on Off With Your Head and **15 + 2k** on Execution. The multi-hit move absorbs the
  Strength five times over, so essentially the whole Phase 2 escalation lives on that one beat.

Base-difficulty incoming per turn, assuming the Amalgam is killed at the end of turn 8, with
Vulnerable's ×1.5 applied from turn 3 onward (You're Mine lands at the end of turn 2):

| Turn | Amalgam | Queen | Raw | After Vulnerable |
|---|---|---|---|---|
| 1 | Tackle 18 | Puppet Strings | 18 | 18 |
| 2 | Tackle 18 | You're Mine | 18 | 18 |
| 3 | Soul Beam 8×3 | Burn Bright (Str→1) | 24 | 36 |
| 4 | Weak Tackle 15 | Burn Bright (Str→2) | 15 | 22 |
| 5 | Weak Tackle 16 | Burn Bright (Str→3) | 16 | 24 |
| 6 | Soul Beam 11×3 | Burn Bright (Str→4) | 33 | 49 |
| 7 | Weak Tackle 18 | Burn Bright (Str→5) | 18 | 27 |
| 8 | Weak Tackle 19 | Burn Bright (Str→6) | 19 | 28 |
| 9 | — (dead) | Off With Your Head 3×5 | 15 | 22 |
| 10 | — | Execution 15 | 15 | 22 |
| 11 | — | Enrage (Str→2) | 0 | 0 |
| 12 | — | Off With Your Head 5×5 | 25 | 37 |
| 13 | — | Execution 17 | 17 | 25 |
| 14 | — | Enrage (Str→4) | 0 | 0 |
| 15 | — | Off With Your Head 7×5 | 35 | 52 |
| 16 | — | Execution 19 | 19 | 28 |
| 17 | — | Enrage (Str→6) | 0 | 0 |
| 18 | — | Off With Your Head 9×5 | 45 | 67 |

Two shapes fall out of this. First, **stalling in Phase 1 is worse than it looks** — the Amalgam's
beam beat grows by 3 per Queen turn while the Queen sits behind 20 block, so every extra turn spent
not killing the Amalgam costs compounding health for zero progress on the boss's own bar. Second,
**Phase 2 is linear, not quadratic** — +10 per Off With Your Head cycle, three turns apart — so this
boss does not hard-cap fight length the way Aeonglass does. It bleeds you through the debuff floor
instead.

Note also that the Queen's Phase 2 numbers are **small per hit**: 3 (or 4 at A9) per hit, five
times. That is the single most exploitable number on the sheet — per-hit block, thorns, per-hit
mitigation and Buffer-style effects all pay enormously against Off With Your Head, while flat block
pays badly.

## Gimmicks

### Chains of Binding / Bound (the hand lock)

Applied once on turn 1 at a count of 3, and it never ticks down — it is live for the entire fight.
It does two things:

1. **Marks cards on draw.** Each turn, the first 3 cards a player draws that are eligible get the
   **Bound** affliction stamped on them. The count of already-bound-this-turn cards is what gates
   it, so it refills every turn.
2. **Allows only one Bound card to be played per turn.** The moment a player plays one Bound card,
   every other Bound card in their hand becomes unplayable for the remainder of that turn. The lock
   releases at end of turn, and all Bound markers are cleared off every card the player owns before
   the next draw.

The practical effect is a **throughput tax on drawn cards specifically**: on a 5-card draw, 3 of
those cards are mutually exclusive with each other and only one of the three can ever be spent.
Cards already in hand from a previous turn, cards generated mid-turn, and cards that arrive by means
other than draw are untouched, so the fight quietly rewards retain, mid-turn generation and
non-draw-based card access — and punishes the standard "draw a lot, play a lot" Act 3 engine plan.
It is applied to every player independently.

### You're Mine (the permanent triple debuff)

Turn 2, every player, 99 stacks each of Frail, Weak and Vulnerable. All three tick down one per turn
like normal, so 99 is simply "the rest of the fight" — no reasonable combat outlasts it.

| Debuff | Effect | Consequence here |
|---|---|---|
| Vulnerable | damage taken ×1.5 | every number in the table above is 50% larger from turn 3 |
| Weak | damage dealt ×0.75 | 400 + 199 HP of enemies effectively becomes ~800 HP of work |
| Frail | block gained ×0.75 | the 20-block-a-turn defensive plan costs a third more cards |

Applied unconditionally, with no attack roll and no save — there is nothing to dodge. The only
answers are artifact-style debuff prevention held for turn 2, or debuff cleansing. This move is what
converts an otherwise modest damage sheet into a real threat: **the Queen's whole offensive design
assumes a ×1.5 multiplier that she applies to herself, for free, on turn 2.**

### The kill-order puzzle

The Queen gains 20 block every Phase 1 turn (52 at two seats — see below) and is otherwise untouched
by her own Phase 1 moves. Hitting her before the Amalgam dies means clearing that block every turn
through Weak, for zero reduction in incoming damage. Hitting the Amalgam means the Queen's buff move
becomes pure waste — but only until it dies, at which point she immediately begins hurting you and
her Strength ramp starts.

So the fight poses a real timing question rather than a fixed order: kill the Amalgam **fast**
(before its beam scales) and you eat the Queen's Phase 2 ramp for many more turns; kill it **slow**
and you eat a compounding beam while making no progress. The Amalgam's 199 HP against a ×0.75
damage floor is priced to be roughly a 3–5 turn job for a healthy Act 3 deck, which lands the
transition right around the first or second beam.

## Scaling

**By act:** none. The Queen exists only in Act 3; nothing on either model reads the act index except
through the shared multiplayer scaling formula, which uses Act 3's boss-room multiplier.

**By ascension:**

| Level | Effect |
|---|---|
| A8 `ToughEnemies` | Queen HP 400 → 419; Amalgam HP 199 → 211 |
| A9 `DeadlyEnemies` | Off With Your Head 3 → 4 per hit (i.e. 15 → **20** per use before Strength); Execution 15 → 18; Amalgam Tackle 18 → 19, Weak Tackle 14 → 15 |

Notably **nothing** about the gimmick layer moves with ascension: Chains of Binding stays at 3, the
triple debuff stays at 99, Burn Bright stays at +1 Strength and 20 block, Enrage stays at +2. The
A9 change is entirely a flat damage bump, and the largest single piece of it is the +1 per hit on
the 5-hit move — a 33% increase on the Queen's main beat, worth more than any other number in the
table.

**By seat count (multiplayer):**

- **HP** scales by the standard formula: base × players × 1.3 (Act 3 **boss-room** multiplier; other
  Act 3 rooms use 1.2).

| Players | Queen HP | Amalgam HP | Combined |
|---|---|---|---|
| 1 | 400 | 199 | 599 |
| 2 | 1040 | ≈517 | ≈1557 |
| 3 | 1560 | ≈776 | ≈2336 |
| 4 | 2080 | ≈1034 | ≈3114 |

- **Block scales too.** Monster-move block runs through the same multiplier, so Burn Bright For Me's
  20 becomes **52** at two seats, 78 at three, 104 at four. Chip damage will not get through the
  Queen in Phase 1 in co-op at all; the kill-the-Amalgam plan goes from advisable to mandatory.
- **All attacks are AoE.** Both Queen attacks and all three Amalgam attacks are built as monster
  attacks against all opponents, and targets are re-resolved per hit. Every seat takes the full
  listed damage on every hit — Off With Your Head is 5 hits **on each player**, not 5 hits split
  across the party. Party-wide damage taken therefore scales linearly with seats on top of the HP
  scale.
- **Both debuff moves hit every player.** Chains of Binding 3 and the full Frail/Weak/Vulnerable
  package are applied to the whole opposing side, per creature, so each seat independently runs its
  own 3-bound-cards-per-turn lock and its own ×1.5 / ×0.75 / ×0.75 multipliers. Nothing is diluted
  by party size.
- **Burn Bright For Me targets the Queen's teammates excluding herself** — with only one ally in the
  encounter, seat count does not change what it buffs.
- The Amalgam's Minion marker means a dead Amalgam never ends the combat regardless of seat count.

## Proposed fight class: **mixed**

The two phases demand genuinely different things and the transition between them is player-timed, so
no single demand curve covers the fight. Phase 1 is a **race under a soak**: the Queen contributes
zero damage and pure defense while the Amalgam's beam beat grows by three per turn, so the demand is
concentrated output aimed at a specific 199 HP target through a ×0.75 damage floor, with just enough
mitigation to survive the ramp — and a 20-block-a-turn wall that makes attacking the wrong target
actively worthless. Phase 2 flips to a **sustained defensive check**: modest per-hit numbers (3–4)
delivered five at a time, escalating linearly rather than explosively, against a player whose block
is permanently taxed 25% and whose incoming is permanently inflated 50%. Sitting under both phases is
a real gimmick axis — Chains of Binding taxes drawn cards specifically and caps you at one Bound card
per turn, which reshapes deck evaluation rather than just adding damage. For Track B, model this as
two sequential demand vectors joined at a player-controlled breakpoint (burst-on-one-target, then
per-hit mitigation + steady output), with a flat multiplicative debuff floor of ×1.5 incoming /
×0.75 outgoing / ×0.75 block from turn 3 onward and a card-access penalty of roughly "3 drawn cards
collapse to 1 playable" every turn.
