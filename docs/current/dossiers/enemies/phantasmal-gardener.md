# Enemy Dossier — Phantasmal Gardener

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `PhantasmalGardener`
- **Kind:** elite
- **Act:** Act 1 (`Underdocks`, act index 0) — the only act pool it appears in
- **Encounters:** `PhantasmalGardenersElite` (four Gardeners, one per slot: `first`, `second`, `third`, `fourth`)
- **Fight class:** `mixed`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

The Phantasmal Gardener never appears alone. Its one encounter spawns **four identical bodies**, each
with ~28 HP, and each entering the fight already carrying **Skittish** — a reflex that converts the
first card-attack it eats each turn into Block. The four run the *same* four-move cycle, but the
encounter starts each of them at a different point in that cycle, so the party's aggregate turn is
always the same shape: one big hit, one medium hit, one flurry of chip, and one permanent buff.

There is no Block move, no summon, no on-death effect, no low-HP phase, and no reaction to a sibling
dying. The threat is entirely the interaction between a **never-ending Strength ramp** and a
**per-body damage-shape tax**.

Cosmetically the bodies use a `tall` skin in slots one and three and a `short` skin in slots two and
four, they grow slightly on each buff (a logarithmic scale bump, purely visual), and they do not fade
out on death — none of that is load-bearing.

## 2. Intent pattern / AI

Four move states in a fixed ring. **Fully deterministic** — the state machine consults no RNG for
this enemy, so once you know each body's slot the entire fight is readable from turn 1.

| State | Intent shown | Effect |
|---|---|---|
| `BITE_MOVE` | single attack, 5 | 5 damage to its target. |
| `LASH_MOVE` | single attack, 7 | 7 damage to its target. |
| `FLAIL_MOVE` | multi-attack, 1 × 3 | Three separate 1-damage hits (one animation). |
| `ENLARGE_MOVE` | buff | Permanent **+2 Strength** to itself, and it grows visibly. |

Ring order: Bite → Lash → Flail → Enlarge → Bite → …

Starting position is chosen by slot on the first turn:

| Slot | Turn 1 | Turn 2 | Turn 3 | Turn 4 |
|---|---|---|---|---|
| `first` | Flail | Enlarge | Bite | Lash |
| `second` | Bite | Lash | Flail | Enlarge |
| `third` | Lash | Flail | Enlarge | Bite |
| `fourth` | Enlarge | Bite | Lash | Flail |

The offsets are exact, so **every turn while all four live, the party sees exactly one Bite, one Lash,
one Flail, and one Enlarge**. There is never a "safe" turn and never a burst turn; the composition is
invariant and only the magnitudes climb. As bodies die the pattern degrades gracefully — the survivors
keep their own phase, so killing the body that is *about to* Enlarge is a real tempo play.

Two engine details worth knowing for a sim port: a monster cannot transition out of the state it
opened in until it has actually performed a move once (so the slot-assigned opener is guaranteed to
fire), and `Flail` deals its three hits as three independent damage events, which matters for Block,
Thorns, and per-hit triggers on both sides.

## 3. Gimmicks

**Skittish (applied to itself on room entry, before turn 1).** The first time each turn that a
**player card attack** deals **non-zero unblocked damage** to a Gardener, that Gardener immediately
gains **6 Block** (retracting into its shell) — once per body per turn. The flag clears at the end of
the player's turn, and the Block itself expires normally.

The precise trigger conditions are the whole puzzle:

- **It is post-hoc.** The Block arrives *after* the triggering hit resolves, so the first hit on a body
  always lands in full. It is every *subsequent* point of card damage that turn which gets eaten.
- **It only reacts to card attacks.** Damage that is not sourced from a card — poison/burn ticks,
  Thorns-style reflection, end-of-turn effects, power procs — does **not** arm the reflex at all, and
  such damage applied while the shell is up is still absorbed by the Block but never causes it.
- **It is per body, not per party.** An AoE that hits all four arms all four shells simultaneously.
  The first AoE of the turn lands clean; a second AoE that turn is reduced by 6 per surviving target
  (up to 24 wasted damage), which is why chip-AoE decks stall badly here and single-target burst does
  not.
- **A hit fully absorbed by existing Block does not re-arm it** (it requires unblocked damage), so
  there is no way to "burn" the reflex cheaply once it is already up — spending a 1-damage card into a
  shelled body does nothing.

Practical shape: **one big hit per body per turn is worth far more than many small ones.** The fight
punishes exactly the multi-hit / wide-chip builds that the four-body layout otherwise invites.

**Enlarge (the ramp).** Each body's Strength is permanent and uncapped, and there is one Enlarge every
turn somewhere on the board. Because Strength applies per *hit*, it lands unevenly across the ring:
Bite and Lash gain +Str once, but **Flail gains +Str three times** (1×3 becomes (1+Str)×3). A body
that has enlarged twice turns its 3-damage flail turn into 15. This is the mechanism by which a fight
that opens at 15 incoming damage becomes lethal if allowed to run.

## 4. Numbers

| Stat (per body) | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP roll (min–max) | 26–31 | 27–32 | — |
| Bite | 5 | — | — |
| Lash | 7 | — | — |
| Flail | 1 × 3 hits = 3 | — | — (repeat count stays 3) |
| Enlarge | +2 Strength (permanent) | — | **+3 Strength** |
| Skittish (start-of-fight) | 6 Block per trigger | **7 Block** | — |

- HP is rolled inclusively from the band, with the encounter's unique-HP pass pushing the four bodies
  onto distinct values where the band allows. Total encounter HP is therefore roughly **114 at A0**
  (four distinct rolls from 26–31) — low per body, which is what makes the Skittish tax bite.
- Party-wide incoming damage per turn, all four alive, no player debuffs, base ascension:

| Turn | Bite | Lash | Flail | Party total |
|---|---|---|---|---|
| 1 | 5 | 7 | 3 | **15** |
| 2 | 7 | 7 | 3 | **17** |
| 3 | 7 | 9 | 3 | **19** |
| 4 | 7 | 9 | 9 | **25** |
| 5 | 7 | 9 | 9 | **25** |
| 6 | 9 | 9 | 9 | **27** |
| 7 | 9 | 11 | 9 | **29** |
| 8 | 9 | 11 | 15 | **35** |

  i.e. **+10 party damage per four-turn cycle (~+2.5/turn), forever**, with the step function
  front-loaded onto whichever body is on Flail. On Deadly Enemies (+3 per Enlarge) the same table runs
  at roughly 1.5× the ramp rate: ~+15 per cycle.

- Effective player damage tax: with all four alive, **up to 24 damage per turn** (28 on Tough Enemies)
  is absorbed by shells if you attack each body more than once — comparable to the entire encounter's
  per-turn output at the start of the fight.

## 5. Scaling

**By act:** none. Act 1 only, no act-conditional stats.

**By ascension:** three flat levers, and note that only two of the six tunable numbers move.

- *Tough Enemies* — HP band up 1 at both ends (26–31 → 27–32) and **Skittish 6 → 7**. The HP change is
  noise; the Skittish change is not, since it is charged once per body per turn.
- *Deadly Enemies* — **Enlarge 2 → 3 Strength**. Bite, Lash, and the flail repeat count all have
  ascension-aware plumbing but the ascended and base values are identical, so nothing changes there.
  This means Deadly Enemies does not make the fight hit harder *now*; it makes the fight run out of
  road faster, converting a comfortable 6-turn clear into a hard 5-turn one.
- *Swarming Elites* (unrelated to this monster's stats) raises the number of elite rooms on the map by
  ~1.6×, so this encounter is seen more often at high ascension.

**By seat count (multiplayer):**

- *HP* uses the shared formula — base × player count × act factor, with the Act 1 non-boss factor
  being **1.1**.

| Players | Effective per-body HP band | Effective encounter HP |
|---|---|---|
| 1 | 26–31 (no scaling at 1 player) | ~114 |
| 2 | ~57–68 | ~250 |
| 3 | ~86–102 | ~376 |
| 4 | ~114–136 | ~501 |

- *Skittish* explicitly scales with the table, on its own multiplier rather than the generic
  enemy-Block scaler (its Block is flagged unpowered, so it is scaled once, not twice). The applied
  amount is `base × (1 + 0.5 × (players − 1))`:

| Players | Skittish Block per trigger (base / Tough Enemies) |
|---|---|
| 1 | 6 / 7 |
| 2 | 9 / 10.5 |
| 3 | 12 / 14 |
| 4 | 15 / 17.5 |

  Critically the reflex is still **once per body per turn**, not once per player — so at four seats the
  four players collectively get one clean hit per body per turn and everything after it pays a 15-Block
  toll. Co-op makes the "who swings at which body, and in what order" conversation the actual fight.
- *Bite / Lash / Flail / Enlarge* do **not** scale. Each attack still targets one seat, so per-seat
  incoming pressure falls off sharply as seats are added while the Strength ramp continues at the same
  absolute rate.

Net co-op shape: HP and the shell grow superlinearly while output stays flat, so the fight becomes a
long coordination puzzle rather than a damage race — but the uncapped Strength ramp means "long" is
still on a timer.

## 6. Proposed fight class — `mixed`

Per turn this fight asks two unrelated questions at once. First, a rising sustain question: incoming
damage is flat-composition but climbs ~2.5/turn forever (~+3.75 on Deadly Enemies) from a modest
15 opener, with no burst turn and no plateau — pure attrition-clock pressure. Second, a damage-shape
question that has nothing to do with blocking: Skittish means only your **first** card hit on each
body lands clean, so the correct play is one large single-target strike per body per turn and the
naive answers to a four-body board (wide AoE, multi-hit chip) are actively taxed up to 24 damage a
turn. Neither half dominates — you cannot out-block the ramp indefinitely, and you cannot out-damage
the shells with the wrong card shapes — which is what makes it `mixed` rather than `attrition` or
`gimmick`, and the four bodies are a delivery mechanism for the shell puzzle rather than a `swarm`
demand in their own right. For Track B, model it as **a rising-damage clock gated by a per-target
once-per-turn damage cap**, where the demand curve is "block ~15 rising to ~35 while landing four
distinct high-value single-target hits per turn," and the counterplay lever is burst concentration
plus non-card damage sources, which bypass the reflex entirely.
