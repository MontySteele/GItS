# Enemy Dossier — Crossbow Raider

- **Class:** `CrossbowRubyRaider`
- **Kind:** normal
- **Act:** Act 1 (`Overgrowth`, act index 0) — the only act whose encounter pool contains the Ruby Raiders fight
- **Encounter:** `RubyRaidersNormal` (a normal-monster room; also force-placed at normal-encounter index 5 of the act's discovery order)
- **Fight class:** `spike`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table description of the constants and mechanics.

---

## 1. Where it appears

Crossbow Raider is one of five interchangeable Ruby Raider bodies (Axe, Assassin, Brute, Crossbow,
Tracker). The Ruby Raiders encounter always fields **exactly three** raiders drawn from the pool of
five *without replacement* — each raider is capped at one copy per fight — so Crossbow Raider is in
the fight roughly 3-in-5 of the time and never appears twice.

It is a plain ranged body: no minion status, no summoning, no on-death effect, no aura or buff on
its allies. Everything below concerns its own turn only.

## 2. Intent pattern / AI

The move machine is **fully deterministic — no RNG, no conditional branches, no HP-threshold
transitions, no lead-in variation.** It is a two-state ring and it always starts on the *reload*
state, meaning **its first turn of the fight is always the defensive one**:

| Turn | Move | Intent shown |
|---|---|---|
| 1 | Reload | Defend |
| 2 | Fire | Attack (single, large) |
| 3 | Reload | Defend |
| 4 | Fire | Attack |
| … | strict alternation forever | — |

So the big shot lands on turns 2, 4, 6, … — every even turn, forever, with no variance to hedge
against. Two properties of the state machine matter for planning:

- A move state cannot be left before its move has been performed at least once, so effects that
  merely *delay* an enemy turn shift the cycle rather than scramble it; the player can never be
  surprised by two Fires back-to-back.
- Reload and Fire are separate turns (unlike the Axe Raider, whose Block rides along with its
  attack). There is a genuine **dedicated defend turn** here, which is the natural window to spend
  burst into.

## 3. Numbers

| Stat | Base | Ascension variant |
|---|---|---|
| Starting HP | 18–21 (rolled) | 19–22 with *Tough Enemies* |
| Fire damage | 14 | 16 with *Deadly Enemies* |
| Reload block (self) | 3 | unchanged (no ascension variant) |

Derived, per full two-turn cycle (single player):

| | Base | Deadly Enemies |
|---|---|---|
| Damage dealt | 14 | 16 |
| Block gained | 3 | 3 |
| Damage per turn (averaged) | 7.0 | 8.0 |

For context inside its own encounter, Crossbow Raider's 14 is the **largest single hit in the
raider pool** — bigger than the Axe Raider's telegraphed 12 payoff, the Assassin's 10 killshot, and
the Tracker's 8×1 flurry — and it sits on the **joint-lowest HP band** of the five. It is the
glass-cannon seat of the trio: highest per-hit output, cheapest to remove.

The 3 Block is deliberately small — roughly one sixth of its own HP band. It is a chip-tax, not a
wall; it makes single-point pings and small multi-hit tools slightly worse but does not meaningfully
protect against a real burst turn.

## 4. Gimmicks

There is exactly one, and it is **cosmetic rather than mechanical**: the model tracks a
loaded/unloaded flag that is flipped true by Reload and false by Fire, and that flag selects between
two complete visual sets — a "loaded" idle/hurt/death set and an "empty" idle/hurt/death set. The
enemy's *body* therefore telegraphs the cycle independently of the intent icon: a crossbow shown
empty means the next turn is a Reload, a crossbow shown loaded means the shot is coming. It also has
an armored take-damage sound profile.

No hidden state, no charge counter that can be pushed past 1, no interaction that lets the player
"unload" the weapon or otherwise cancel the pending shot. The flag reads only into animation
selection, so a mod or sim that ignores it loses nothing mechanical — but a *player-facing* clone
loses a real second telegraph.

## 5. Scaling

**By act:** none. The model has no act-varying stats and the encounter only exists in Act 1, so
there is nothing to model cross-act.

**By ascension:** two independent bumps, both flat and both small.
- *Tough Enemies* raises the HP band by exactly 1 at both ends (18–21 → 19–22).
- *Deadly Enemies* raises Fire damage 14 → 16. The Reload block is **not** touched.
There are no ascension-added moves, no cycle changes, and no extra bodies in the encounter.

**By seat count (multiplayer):** two multipliers apply, both using the Act 1 factor of **1.1**.

1. **HP** is multiplied by `players × 1.1` when there is more than one player.

   | Players | HP band |
   |---|---|
   | 1 | 18–21 (unscaled) |
   | 2 | ~40–46 |
   | 3 | ~59–69 |
   | 4 | ~79–92 |

2. **Block** from its Reload is multiplied by the same `players × 1.1`, because monster-move block
   qualifies for the scaling and Crossbow Raider is a primary enemy (never a minion/illusion, so it
   is never excluded). Its 3 Block becomes ~6.6 at 2 players, ~9.9 at 3, ~13.2 at 4. Even at a full
   table this stays under a single starter Defend, so the chip-tax reading holds at every seat
   count — the raider that *gets meaningfully tankier* in co-op is the Axe, not this one.

3. **Damage is *not* divided among seats.** The shot targets all opponents, so **every hero eats the
   full 14 (or 16)** on the same turn. Table-wide damage output therefore scales linearly with seat
   count on top of the HP scaling, and at 4 players a single Fire turn is 56–64 damage across the
   table. This is the sharpest single beat in the whole raider encounter.

## 6. Proposed fight class — `spike`

Reasoning from what the fight demands per turn: the demand curve is a clean square wave — a turn
that asks nothing, then a turn that asks for ~14 points of mitigation or a corpse, repeating with
zero variance. Because the shot is the biggest single number in the encounter and the body carrying
it has the lowest HP and only 3 Block, the correct play is almost always *race*: the Reload turn is
a free window to dump burst, and killing the Crossbow before its second even turn removes 7 damage
per turn permanently. It is not `attrition` (the body is ~20 HP and the pressure is concentrated in
alternating beats rather than ground out), not `swarm` at the individual level (one body, no
summons — the three-body *encounter* around it is a swarm, which Track B should model at the
encounter layer, not here), and not `gimmick` (its only special state is a purely visual loaded/empty
tell). For the demand curve, treat it as a **2-turn square wave: one zero-demand turn, one
burst-or-block check**, with the checks at 14/16 per seat and a negligible anti-chip tax on the
off-turn.
