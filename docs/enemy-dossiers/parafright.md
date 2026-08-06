# Enemy Dossier — Parafright

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained. Status index: `docs/registry/identifiers.md` §15.

- **Class:** `Parafright`
- **Kind:** normal
- **Act:** Act 2 (`Hive`, act index 1) — the only act pool it appears in
- **Encounters:** `TheObscuraNormal` (never spawns on its own; the encounter reserves an `illusion`
  slot for it and The Obscura summons it on its first turn)
- **Fight class:** `attrition`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

Parafright is The Obscura's hologram: a 21 HP body with **one move, forever**, that **cannot be
permanently killed**. It is a summon, not a standalone encounter — the room begins with The Obscura
alone, and the boss-shaped opener of that fight is a Summon intent that fills the illusion slot.

Mechanically it is a damage tap wired to the wrong shut-off valve. It hits for 16 (17 on the Deadly
Enemies ascension tier) every single turn with no variation, no RNG, and no telegraph beyond the
number itself. Killing it does not remove it from combat: it slumps, spends its next turn healing to
full, and resumes slamming. Its HP total is therefore not a health bar, it is the **price of buying
one turn of silence**, and the price is bad.

## 2. Intent pattern / AI

The state machine has exactly **one state**, whose follow-up is itself.

| State | Intent shown | Effect |
|---|---|---|
| `SLAM_MOVE` | Single attack | Hits for the Slam number, modified by any Strength it holds. |

Flow: **Slam → Slam → Slam → …** with no branch, no counter, and no RNG draw. Whatever the party
sees on turn 1 is what it sees on turn 20.

The only deviation is death-driven. When Parafright dies:

1. It plays a stun/collapse animation and is flagged **reviving**, but stays on the board.
2. A one-off `REVIVE_MOVE` is jammed in as its immediate next move, showing a **Heal intent**. That
   move is flagged must-perform, so nothing can bump it — the party gets exactly one attack-free
   turn out of the kill.
3. On its next turn it wakes, **heals to full**, and its follow-up returns it to the slam state it
   was in when it died.

So the observed cycle after a kill is: *(killed) → Heal intent turn → Slam → Slam → …*

## 3. Gimmicks

**Undying illusion.** The illusion power sitting on it does four separate things, and each one
closes an obvious line of play:

- *It is not removed from combat on death.* No corpse, no slot freed, no "kill all enemies" progress.
- *It heals to full on the turn after death*, restoring the entire HP bar for free.
- *It cannot be hit or receive powers while reviving.* Damage and debuffs aimed at it during the
  downed turn are wasted; you cannot pre-load Vulnerable onto the body before it stands up.
- *Doom-style removal effects do not clear it either* — it is explicitly flagged not to disappear
  that way.

**Death launders debuffs, but not buffs.** The power keeps the illusion's **buffs** across death and
deliberately drops its **debuffs**. Practical consequence: any Weak/Vulnerable/Strength-down the
party spent on Parafright is **erased the moment they kill it**, while every point of Strength The
Obscura donated survives the death and comes back with the full heal. Killing it is a *debuff reset
button for the enemy*.

**It is a minion, not a primary enemy.** It carries the minion flag, so its death does not trigger
the fight-ending "everything is dead" check, and it counts as a secondary enemy for anything keyed on
that distinction (including enemy-Block multiplayer scaling, which it never uses). The corollary is
the actual win condition: **kill The Obscura and the illusion evaporates with the combat.**

**It inherits the escort's Strength.** The Obscura's Wail move gives **+3 Strength to all of its
teammates**, which includes Parafright, permanently and stacking. That is the only thing in the fight
that makes the illusion's number move — see the scaling table below.

## 4. Numbers

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP (fixed, no roll) | 21 | — | — |
| Slam | 16 | — | 17 |
| Block gained | none — it never defends | — | — |
| Revive heal | to full max HP | — | — |

Context numbers from its escort (`TheObscura`), because they set Parafright's real damage curve:

| Obscura move | Base | Deadly Enemies |
|---|---|---|
| Piercing Gaze (attack) | 10 | 11 |
| Hardening Strike (attack + block) | 6 dmg / 6 block | 7 dmg / 7 block |
| Wail (buff) | **+3 Strength to all teammates** | — |
| Obscura HP | 123 (129 on Tough Enemies) | — |

The Obscura opens with Summon, then picks randomly among Piercing Gaze / Wail / Hardening Strike with
a no-immediate-repeat rule — so Wail can recur roughly every other turn at worst. Parafright's slam
tracks it directly:

| Wails so far | Parafright Slam | Obscura's own attack | Party intake that turn |
|---|---|---|---|
| 0 | 16 | 10 / 6 | 22–26 |
| 1 | 19 | 13 / 9 | 28–32 |
| 2 | 22 | 16 / 12 | 34–38 |
| 3 | 25 | 19 / 15 | 40–44 |

Against that, the kill math on the illusion: **21 damage buys one skipped 16-damage slam** and gives
back nothing else — no permanent progress, no debuff carry-over, and the 21 comes back at full on the
next turn. The trade is net-negative the first time and gets worse every Wail, because the HP price
is fixed at 21 while the damage denied only rises by 3 a stack. It is a genuinely correct play only
in narrow spots: a turn where the party would otherwise die to the slam, or spare damage that
literally has nowhere else to go.

## 5. Scaling

**By act:** none. Act 2 only, no act-conditional stats.

**By ascension:** one lever, and it is small. *Deadly Enemies* moves Slam 16 → 17. Parafright has
**no Tough Enemies HP variant** — it is 21 at every ascension, so the "kill it" trap does not even
get more expensive at high ascension; the escort's HP is what grows (123 → 129).

**By seat count (multiplayer):**

- *HP scales like any other monster* — base × player count × the Act 2 factor of **1.2** — and the
  scaling is applied when the creature is created, so the mid-combat summon is scaled correctly.

| Players | Parafright HP |
|---|---|
| 1 | 21 (no scaling at 1 player) |
| 2 | ~50 |
| 3 | ~76 |
| 4 | ~101 |

- *The revive heals to the scaled maximum*, so the tax repeats at the scaled size every time.
- *Slam targets every opponent.* The attack is built against all opponents rather than one seat, so
  **each player takes the full 16/17**; party-wide intake is 16 × seats, per turn, forever.
- *Its own numbers do not scale.* Slam is flat and it never gains Block, so the enemy-Block
  multiplayer multiplier — the usual co-op inflation route — never touches this creature.
- Net co-op shape: the damage the party must absorb rises linearly with seats while the cost of
  temporarily silencing it rises **super-linearly** (× seats × 1.2). At four seats the "buy one quiet
  turn" price is ~101 damage to deny 16 damage to each of four players. The trap gets sharper the
  bigger the party, and the correct answer — ignore the illusion, focus the Obscura — gets more
  correct.

## 6. Proposed fight class — `attrition`

What this creature demands, every turn without exception, is 16 points of mitigation you can never
stop paying: there is no pattern to read, no window to exploit, and no HP threshold that pays out,
because the health bar is a toll booth rather than a finish line. It is not `spike` — the number is
flat and identical on every single turn, and the only escalation is slow +3 chip donated by its
escort. It is not `swarm` (exactly one body, summoned once) and not `gimmick`: the undying revive is
a striking mechanic but it is *anti-interactive by design*, a rule that removes a line of play rather
than one the player operates, so it changes nothing about what each turn asks. For Track B, model
this as **a fixed per-seat damage floor with an unusable off-switch** — the demand curve is a flat
16-per-turn-per-player tax that the party must eat with Block or lifesteal for the entire duration of
the Obscura fight, and any damage routed into the illusion is, in demand-curve terms, damage the
party did not spend on shortening the fight.
