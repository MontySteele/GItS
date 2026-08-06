# Enemy Dossier — Slumbering Beetle

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `SlumberingBeetle`
- **Kind:** normal
- **Act:** Act 2 (`Hive`, act index 1) — the only act pool it appears in
- **Encounters:** `SlumberingBeetleNormal` only, tagged `Workers`. That encounter is a **fixed trio**
  with no rolled slots: Bowlbug (Rock) in the first slot, Bowlbug (Silk) in the second, and the beetle
  in the third. The beetle never appears alone and never appears in another encounter.
- **Fight class:** `mixed`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

A large armored body that starts the fight **asleep** and does nothing at all for the first stretch of
combat, then wakes up permanently into a single-target attack that gets stronger every turn forever.
It is a two-phase enemy with a player-controllable phase transition: the sleep phase is defensive and
inert, the awake phase is an escalating race. The two bowlbugs standing in front of it supply all of
the early incoming damage while the beetle is the timer.

Everything about it is deterministic. There is no RNG anywhere in its move machine, no HP roll (its
min and max initial HP are the same value), and no branching other than the sleep check.

## 2. Setup on entering the room

Three things happen when it is placed:

1. It applies **Plating 15** to itself (18 with Tough Enemies) — a counter-type buff.
2. It applies **Slumber 3** to itself — a counter-type buff that is its sleep timer.
3. A sleeping VFX and a looping snore SFX start; both are torn down on wake-up or on death.

While asleep it also does not play a hurt reaction — the hit animation is gated on being awake, so it
visually ignores everything until the wake trigger fires.

## 3. Intent pattern / AI

Two moves plus one conditional branch:

| State | Intent shown | Effect |
|---|---|---|
| `SNORE_MOVE` | Sleep | Nothing. Literally a no-op move. |
| `ROLL_OUT_MOVE` | single attack (16) **+** buff | Rolls at one target for 16, then gains **+2 Strength**. |

Flow:

- Opening move is always **Snore**.
- After a snore, a branch asks a single question: *does it still have Slumber?* If yes → Snore again.
  If no → Rollout.
- **Rollout's follow-up is Rollout.** Once awake it never returns to any other state for the rest of
  the fight. There is no re-sleep, no block move, no debuff on the player, no summon, and no low-HP or
  ally-death behavior change.

The rollout intent number is computed through the normal damage-modifier path, so the displayed
damage includes its accumulated Strength — the player sees the escalation coming one turn at a time
(16 → 18 → 20 → 22 → …, unbounded).

## 4. Gimmick A — Slumber (the wake timer, and who controls it)

Slumber 3 ticks down from **two independent sources**:

- **End of the enemy side's turn**, once per turn, while it is a participant. Three enemy turns of
  snoring therefore wake it on their own.
- **Every instance of damage received that is not fully blocked.** Blocked damage does nothing;
  partial mitigation still counts as long as at least 1 HP was lost on that instance. This is
  per-damage-*instance*, not per-turn, so a multi-hit or shiv-style turn can burn the whole counter at
  once.

The two paths to zero differ slightly in presentation and in what the machine does next:

- **Timer path (turn-end tick to 0):** it wakes immediately at end of turn. The branch then routes it
  to Rollout, so the very next enemy turn is a 16-damage roll.
- **Damage path (unblocked hit takes it to 0):** it is **stunned**, with the wake-up performed as the
  stunned turn's "move", and the move after the stun is force-set to Rollout. A stun VFX plays. Net
  tempo is the same shape as the timer path — one dead enemy turn, then rolling — but it arrives
  earlier in the fight.

Practical consequence: **the player chooses when the beetle wakes up**, and waking it early is
strictly a cost in incoming damage but a gain in armor removal (below). A deck that opens with wide
multi-hit chip into the beetle can have it awake and rolling by turn 3; a deck that ignores it and
kills the bowlbugs first gets the natural three-turn grace period.

## 5. Gimmick B — Plating (the armor that dies with the nap)

Plating is a generic enemy-armor counter, and the beetle's copy behaves as follows:

- It grants **Block equal to its current amount at the start of combat** (round 1) and again at the
  **end of every enemy turn** — the end-of-turn grant is scheduled early, before end-of-turn damage
  effects resolve.
- Its amount **decays at the start of each enemy turn from round 2 onward**, by an amount equal to the
  **number of players in the run** (1 in solo).
- **Waking up removes Plating outright.** The wake-up move explicitly strips it.

So in solo the beetle's armor is 15, 15, 14, 13, 12, … per turn, and every point of that wall is
refunded to the player the moment it wakes. This is the fight's real tension: the armor makes it
expensive to kill while asleep, and the cheapest way to remove the armor is to wake the thing that the
armor was protecting.

## 6. Numbers

| Stat | Base | With Tough Enemies (A8) | With Deadly Enemies (A9) |
|---|---|---|---|
| HP (fixed, no roll) | 86 | 89 | — |
| Plating / per-turn Block | 15 | 18 | — |
| Slumber (wake timer) | 3 | — | — |
| Rollout damage (first roll) | 16 | — | 18 |
| Strength gained per rollout | +2 | — | — |

Encounter context (same act, same fight): Bowlbug (Rock) 45–48 HP / 15 headbutt, Bowlbug (Silk)
40–43 HP / 4 thrash. Total encounter HP in solo is roughly 172–177 before any Plating is accounted
for, which is high for an Act 2 normal — the beetle alone is half of it and is the half that fights
back last.

Cumulative rollout damage from the first roll, solo, base: 16 / 34 / 54 / 76 / 100 across rolls 1–5
(18 / 38 / 60 / 84 / 110 on Deadly Enemies). Turn six of the awake phase is a 26-damage single hit.

## 7. Scaling

**By act:** none. Act 2 exclusive, no act-conditional stats.

**By ascension:** two flat levers from the shared ascension helper. Tough Enemies raises HP 86 → 89
*and* Plating 15 → 18 — note that this one level makes both halves of the sleep phase harder, since
the armor and the body both grow. Deadly Enemies raises the rollout base 16 → 18, which compounds:
every subsequent roll is +2 as well because the Strength ramp sits on top of a higher base. Nothing
touches the Slumber count or the +2 per roll.

**By seat count (multiplayer):**

| Players | HP (× players × 1.2) | Plating amount | Plating decay / turn | Rollout |
|---|---|---|---|---|
| 1 | 86 | 15 | 1 | 16, single target |
| 2 | ~206 | 45 | 2 | 16, single target |
| 3 | ~310 | 75 | 3 | 16, single target |
| 4 | ~413 | 105 | 4 | 16, single target |

Three separate things happen in co-op and they do not point the same direction:

- HP scales super-linearly (player count × the Act 2 non-boss factor of 1.2).
- **Plating is explicitly multiplayer-scaled** by a (2·(players−1)+1) multiplier — it triples at two
  seats and *septuples* at four, while the per-turn decay only rises linearly. At four seats the wall
  is 105 Block per turn against a body that is decaying by 4 per turn, i.e. effectively permanent for
  the length of the fight.
- **Slumber does not scale** (still 3) and **rollout damage does not scale** (still one 16-damage hit
  against one seat per turn).

The upshot is that co-op inverts the solo decision. Solo, killing it asleep is a live plan; at three
or four seats the sleeping beetle is nearly unkillable through 75–105 Block per turn, so the table's
correct line is to *wake it deliberately* — three unblocked instances is trivial to arrange across
four seats — strip the Plating, and then race a single-target attacker whose damage never scaled with
the party. Per-seat incoming pressure from this enemy falls off a cliff in co-op even as its effective
HP roughly quintuples.

## 8. Proposed fight class — `mixed`

The demand curve changes shape mid-fight, and the player picks the changeover point. During the sleep
phase the beetle asks for nothing defensively and everything offensively: it is a pure armor-breaking
attrition target (15+ refreshing Block on 86 HP) that simultaneously punishes the exact chip damage
you would use to break it, while the two bowlbugs meter out the actual incoming damage — that is an
`attrition` demand. Once awake it asks the opposite question every turn: a single escalating hit that
grows +2 forever, which is a hard clock with a real failure cliff and demands the player have already
converted their setup into a kill — that is `spike`-shaped pressure, and it never reverts. Neither
label alone captures a fight whose first half rewards patient defense-stripping and whose second half
punishes any turn not spent closing; for Track B this should be modeled as **two concatenated demand
curves with a player-triggered switch**, and it is the cleanest probe in Act 2 for "can this deck
choose its own tempo and then meet the deadline it chose."
