# Enemy Dossier — Flyconid

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `Flyconid`
- **Kind:** normal
- **Act:** Act 1 (`Overgrowth`, act index 0) — the only act pool it appears in
- **Encounters:** `FlyconidNormal` (one Flyconid + one random medium slime: Leaf or Twig), `SnappingJaxfruitNormal` (one Snapping Jaxfruit + one Flyconid)
- **Fight class:** `mixed`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

The Flyconid is Act 1's spore-thrower: a small-HP mushroom that alternates unpredictably between a
heavy blunt smash, a lighter spore attack that also applies Frail, and a pure-debuff puff that applies
Vulnerable and does no damage at all. Its whole design is *tempo interference* — it makes your Block
worth less and the next incoming hit worth more, while a partner monster (always present; it never
spawns alone in either of its encounters) supplies the steady damage.

It has no Block move, no buff for itself or its ally, no summon, no on-death effect, no low-HP phase
change, and no reaction to its partner dying. There is no ramp of any kind: the same three moves at
the same numbers, forever, in randomized order.

## 2. Intent pattern / AI

Three move states hanging off a single random branch, plus a separate opening branch. Weights are all
equal (1); the shaping comes entirely from **per-move cooldowns**, not from weighting.

| Move | Intent shown | Effect | Availability rule |
|---|---|---|---|
| Vulnerable Spores | debuff only (no damage number) | **Vulnerable 2** to every player | cooldown 3 — cannot be used if it appeared in the last 3 moves |
| Frail Spores | attack + debuff | **8 damage**, then **Frail 2** to every player | cooldown 2 — cannot be used if it appeared in the last 2 moves |
| Smash | attack | **11 damage** | no cooldown, but cannot repeat back-to-back |

**Opening turn** uses a separate branch that excludes Vulnerable Spores entirely: turn 1 is a coin
flip between **Frail Spores (50%) and Smash (50%)**. You are never Vulnerable on turn 1, and you are
never hit for zero on turn 1.

**Every turn thereafter** re-rolls uniformly among whichever of the three are off cooldown. Because
the branch is uniform-over-available, the cooldowns do all the shaping:

- No move ever repeats on consecutive turns.
- Vulnerable Spores appears at most once per four turns; Frail Spores at most once per three.
- Turn 2 is heavily weighted toward the Vulnerable puff — **~50% Vulnerable, ~25% Frail, ~25% Smash**
  — because whichever move opened turn 1 is on cooldown and Vulnerable is freshly legal.
- There is a degenerate case the engine handles quietly: the exact history `Vulnerable → Frail →
  Smash` leaves all three moves blocked, and the branch falls back to the **first-registered branch,
  which is Vulnerable Spores**. So that particular three-turn run *forces* a Vulnerable puff on the
  fourth turn. This is the only deterministic beat in the whole pattern.

**Steady-state move mix** (simulated over the cooldown chain): Smash **~43%**, Frail Spores **~29%**,
Vulnerable Spores **~28%**. Roughly three turns in ten are damage-free.

## 3. Gimmicks

**Frail before Block, Vulnerable before damage.** The two spore moves attack the player's *defensive
math* rather than their HP. Frail multiplies Block gained by **0.75**; Vulnerable multiplies damage
received by **1.5**. Both land at **2 stacks**, i.e. they cover the next two of your turns, which is
exactly wide enough to catch the next Smash regardless of what the branch rolls in between. A Smash
into Vulnerable is **~16** instead of 11 (**18** on Deadly Enemies), and a Frail turn shaves a quarter
off whatever Block you were planning to answer it with.

**The zero-damage turn is not a free turn.** Vulnerable Spores shows a debuff intent with no number,
so a defensive player reads "nothing incoming" and skips blocking — which is correct that turn and
punished the next one. The intent display is honest; the trap is purely in the sequencing.

**Both spore moves are party-wide, and so are the attacks.** The debuffs are applied to the full
player list. Monster attacks in this engine target *all opponents* by default, so the 8 and the 11
also land on every seat at full value. There is no per-seat dilution anywhere in the kit.

**Small body, shared room.** At 47–49 HP it is the softer half of both its encounters. It is a
priority-kill target on tempo grounds rather than a damage-race one: killing the Flyconid removes the
debuff engine that is inflating the *partner's* damage and deflating your Block.

## 4. Numbers

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP roll (min–max) | 47–49 | 51–53 | — |
| Smash | 11 | — | 12 |
| Frail Spores | 8 damage + Frail 2 | — | 9 damage + Frail 2 |
| Vulnerable Spores | Vulnerable 2, no damage | — | — |
| Vulnerable multiplier | ×1.5 damage taken | — | — |
| Frail multiplier | ×0.75 Block gained | — | — |

- **Raw** average output, ignoring its own Vulnerable, is about **7.1 damage/turn** (≈7.8 on Deadly
  Enemies).
- **Effective** average output, counting the Vulnerable it applies to itself-amplified follow-ups, is
  about **9.6 damage/turn** (≈10.6 on Deadly Enemies) — roughly a third of its damage comes from the
  amplifier rather than the attacks.
- Worst realistic single turn: **16** (Smash under Vulnerable), **18** on Deadly Enemies. There is no
  multi-hit move and no burst above that.
- It never gains Block, so the enemy-Block multiplayer scaler never touches it.

## 5. Scaling

**By act:** none. Act 1 only, no act-conditional stats.

**By ascension:** two flat levers, both small. Tough Enemies moves the HP band up by 4 at both ends
(47–49 → **51–53**). Deadly Enemies takes Smash 11 → **12** and the spore attack 8 → **9**. Neither
debuff amount (2 and 2) nor either cooldown has an ascension variant, so the *shape* of the fight is
identical at every ascension — only the clock length and the chip size move.

**By seat count (multiplayer):**

- *HP* uses the shared formula — base × player count × act factor, with the Act 1 factor being **1.1**.

| Players | Effective HP band (base roll) |
|---|---|
| 1 | 47–49 (no scaling at 1 player) |
| 2 | ~103–108 |
| 3 | ~155–162 |
| 4 | ~207–216 |

- *Both attacks hit every seat* at full printed value (monster attacks default to targeting all
  opponents). Per-seat damage pressure therefore does **not** fall off as seats are added.
- *Both debuffs are applied to every seat* at the full 2 stacks. Vulnerable 2 on four players is four
  amplified bodies, not one.
- No move has any seat-count-conditional branch, and no amount is multiplied by player count, so the
  co-op version of this enemy is exactly the single-player version with a fatter HP bar and the same
  full-strength pressure on each seat. Relative to enemies whose single-target damage dilutes across
  the party, the Flyconid gets **harder** in co-op, and its 2-stack debuffs are correspondingly harder
  for the party to cleanse.

## 6. Proposed fight class — `mixed`

Turn to turn this enemy demands three genuinely different things and refuses to tell you which is
coming: a raw 11 that wants Block, a defensive-math turn (Frail) that makes Block a worse answer than
it was last turn, and a damage-free turn that is really a bill for the following turn (Vulnerable).
Nothing here is a spike — 16 is the ceiling and there is no telegraphed nuke or threshold — and the HP
pool is far too small (47–49) for an attrition read; it is a two-body room, not a `swarm`, and there
is no special rule or puzzle state to solve, which rules out `gimmick`. For Track B the demand curve
should be modeled as **randomized, low-magnitude, multi-type pressure against a short clock**: the
correct counterplay is holding a generic answer and killing the debuffer first rather than
pre-committing Block to a predicted number, and the fight's real difficulty lives in how the Flyconid
amplifies whatever it is standing next to.
