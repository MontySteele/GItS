# Enemy Dossier — Slithering Strangler

- **Class:** `SlitheringStrangler`
- **Kind:** normal
- **Act:** Act 1 (`Overgrowth`, act index 0) — the only act pool it appears in
- **Encounters:** `SlitheringStranglerNormal` (one Strangler + one randomly chosen secondary group)
- **Fight class:** `attrition`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

The Slithering Strangler is Act 1's ramping damage-over-time body. It has exactly three moves and it
alternates rigidly between a debuff turn and an attack turn: **every other turn it stacks Constrict on
every player, permanently, forever**, and on the turns in between it either headbutts for modest damage
while turtling behind Block, or tail-lashes for a bigger hit with no defence.

It has no summon, no heal, no on-death effect, no low-HP phase change, no Artifact, and no reaction to
its partner dying. The only randomness in the whole kit is which of the two attacks it picks.

The important structural fact: **Constrict is anchored to the Strangler.** When the Strangler dies,
every stack it applied is removed from every player. That makes target priority in its encounter
non-negotiable — the accumulated clock is refundable in full by killing the source.

## 2. Intent pattern / AI

Three move states in a fixed alternation, with a coin-flip branch on the attack beat.

| State | Intent shown | Effect |
|---|---|---|
| `CONSTRICT` | debuff | Applies **3 Constrict** to *every player creature*. Stacks additively, never decays. |
| `THWACK` | attack + defend | Attack for 7, then gains **5 Block**. |
| `LASH` | attack | Attack for 12. No Block. |

Flow: **Constrict → (Thwack or Lash) → Constrict → (Thwack or Lash) → …** forever.

- The opening move is always **Constrict** — the state machine starts there and cannot transition away
  before its first move, so turn 1 is fully predictable.
- The branch after each Constrict is an even-weight coin flip (weight 1 each) with *no* repeat limit
  and *no* cooldown on either arm, so Thwack or Lash can recur arbitrarily many times in a row. There
  is no "cannot repeat" guard and no escalation of the attack values.
- Both attack states loop straight back to Constrict, so the debuff cadence is exactly every other
  turn regardless of which attack was rolled. The Constrict count on the party is therefore a direct
  clock: `3 × ceil(turn / 2)`.

Expected damage from the attack beat is `(7 + 12) / 2 = 9.5` on attack turns, i.e. **~4.75/turn
averaged** from attacks alone — small, and increasingly irrelevant next to the Constrict term.

## 3. Gimmicks

**Constrict (unique to this enemy).** A visible-count debuff that never decrements on its own. At the
end of the affected side's turn, each afflicted creature takes damage equal to its full Constrict
count. It is typed as regular power damage rather than as unblockable HP loss, so it is not
poison-style attrition in the strictest sense — but it lands at end of turn, after the party has
already spent the turn, so leftover Block is the only thing that could absorb it and the design intent
is clearly that it goes through. Practically: budget it as unavoidable per-turn HP.

**Refundable clock.** Constrict is removed from everyone the moment the Strangler dies (and only for
that reason — nothing else in its kit cleans it up). Every turn you spend hitting the *partner*
instead is a turn the whole party's DoT term ratchets up and stays up.

**Thwack's Block.** The Block half of Thwack (5) is the enemy-move Block that the multiplayer scaler
targets, which is the one number in this kit that grows sharply in co-op (see §5). At one seat it is
almost noise; at four seats a Thwack turn can absorb the better part of a full player's output.

Cumulative Constrict damage taken by each player, single-player, base values:

| Player turn | Stacks | Tick that turn | Cumulative from Constrict |
|---|---|---|---|
| 1 | 3 | 3 | 3 |
| 2 | 3 | 3 | 6 |
| 3 | 6 | 6 | 12 |
| 4 | 6 | 6 | 18 |
| 5 | 9 | 9 | 27 |
| 6 | 9 | 9 | 36 |
| 7 | 12 | 12 | 48 |
| 8 | 12 | 12 | 60 |

Add ~4.75/turn of attack damage on top and the fight is roughly break-even against a starting HP pool
somewhere around turn 8–9. It is not survivable indefinitely.

## 4. Numbers

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP roll (min–max) | 53–55 | 54–56 | — |
| Thwack attack | 7 | — | 8 |
| Thwack Block | 5 | — | — |
| Lash attack | 12 | — | 13 |
| Constrict applied | 3 per cast, to every player | — | — |

- HP is rolled inclusively from the band; the encounter's unique-HP pass pushes same-side bodies onto
  distinct rolls where the band allows.
- Both attacks resolve against all opposing creatures at full value (monster attacks in this game are
  not single-seat), and Constrict is applied to every player creature in one cast.

**Encounter composition.** `SlitheringStranglerNormal` always contains the Strangler plus one of three
equally likely secondary groups:

| Roll | Secondary | Shape |
|---|---|---|
| Snapping Jaxfruit | 1 body, 31–33 HP (34–36 tough) | Attacks for 3 (4 deadly) **and gains 2 Strength every turn** — a second escalating term |
| Medium slime | 1 body, Leaf 32–35 HP / Twig 26–28 HP | Attacks for 8–11 (9–12 deadly), plus periodic status-card dumps |
| Small slimes | 2 bodies, Leaf 11–15 HP / Twig 7–11 HP each | 3–4 damage each (4–5 deadly), Leaf variant alternates in a status move |

So the fight is 2–3 bodies, total enemy HP roughly 70–90 at one seat, with the Strangler always the
largest single pool and always the correct focus target.

## 5. Scaling

**By act:** none. Act 1 only; no act-conditional stats anywhere in the kit.

**By ascension:** three flat levers, no structural changes. Tough Enemies shifts the HP band up by 1 at
both ends (53–55 → 54–56). Deadly Enemies takes Thwack 7 → 8 and Lash 12 → 13. **Constrict's 3 has no
ascension variant**, which means the dominant term of the fight is ascension-invariant — higher
ascensions make the Strangler marginally tankier and its attacks marginally sharper, but do not
accelerate the clock that actually kills you.

**By seat count (multiplayer):**

- *HP* uses the shared formula — base × player count × act factor, with the **Act 1 factor being 1.1**.

| Players | Effective HP band (base roll) |
|---|---|
| 1 | 53–55 (no scaling at 1 player) |
| 2 | ~117–121 |
| 3 | ~175–182 |
| 4 | ~233–242 |

- *Thwack's Block* is enemy move Block and is multiplied by `player count × 1.1` while the Strangler
  occupies a primary/secondary enemy slot: **5 → ~11 at two seats, ~17 at three, ~22 at four.** A
  Thwack turn in a four-seat game meaningfully stalls the kill, which in turn feeds the Constrict clock.
- *Constrict* is applied to every player creature at the full 3, so total party DoT is `3 × seats` per
  cast and the per-seat pressure is **unchanged** by table size. This is one of the rare monster
  effects whose per-player severity does not dilute in co-op.
- *Thwack/Lash* likewise hit every opponent at full value, so per-seat incoming damage is flat across
  seat counts.

Net co-op shape: incoming pressure per player is *identical* to solo, while the enemy HP pool triples
or quadruples and its Block move quadruples with it. The Constrict clock therefore gets many more turns
to run before the party can cash the refund — this fight is materially harsher at four seats than at
one, and the harshness is entirely in the time axis rather than the damage axis.

## 6. Proposed fight class — `attrition`

Per turn this fight asks for a steady, unglamorous amount of throughput and offers no burst turn to
survive: the largest single hit in the whole kit is 12 (13 on Deadly Enemies), fully telegraphed, and
alternating with a turn where the Strangler does nothing but debuff — nothing here spikes, so `spike`
is out; 2–3 low-HP bodies is not a `swarm`; and there is no puzzle state, no threshold, and no
conditional to solve, so it is not `gimmick`. What the fight actually demands is *speed of damage
against a rising floor of unavoidable HP loss*: every turn you do not close, the party's per-turn tax
goes up by 1.5 per seat on average and stays up, and Thwack's Block (huge in co-op) exists precisely to
buy the clock more turns. For Track B this should be modeled as a **race against a linearly-ramping DoT
with a refund condition** — the demand curve is "deal ~55 (or ~120/~180/~240 in co-op) damage before
cumulative chip outpaces your HP," with the sharp non-linearity that killing the Strangler zeroes the
accumulated term instantly, making focus-fire order the single highest-leverage decision in the room.
