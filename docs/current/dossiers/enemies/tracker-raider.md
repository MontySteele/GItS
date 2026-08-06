# Enemy Dossier — Tracker Raider

> **Lifecycle: REFERENCE** — frozen record; read when cited, not maintained.

- **Class:** `TrackerRubyRaider`
- **Kind:** normal
- **Act:** Act 1 (`Overgrowth`, act index 0) — the only act whose encounter pool contains the Ruby Raiders fight
- **Encounter:** `RubyRaidersNormal` (a normal-monster room; also force-placed at normal-encounter index 5 of the act's discovery order on a player's first run ever)
- **Fight class:** `attrition`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table description of the constants and mechanics.

---

## 1. Where it appears

Tracker Raider is one of five interchangeable Ruby Raider bodies (Axe, Assassin, Brute, Crossbow,
Tracker). The encounter always fields **exactly three** raiders drawn from the pool of five
*without replacement* — each raider is capped at one copy — so Tracker is present roughly 3-in-5
of the time and never appears twice.

It is a plain body: no minion status, no summons, no on-death trigger, no aura on its allies. Its
debuff, however, is the one raider effect that *helps the other two* — see §5.

## 2. Intent pattern / AI

The move machine is **fully deterministic — no RNG, no conditional branches, no HP thresholds.**
It is a two-state chain where the second state loops on itself forever:

| Turn | Move | Intent shown |
|---|---|---|
| 1 | Track | Debuff (generic debuff icon; no number) |
| 2 | Hounds | Multi-attack (damage × hits) |
| 3+ | Hounds, every turn, forever | Multi-attack |

- **Track** is a pure debuff turn: it applies **Frail 2** and deals **zero damage**. It nonetheless
  plays the attack animation and a slashing hit effect on its targets, so it reads visually like an
  attack even though the intent icon says debuff. Track is **hidden from the bestiary entry** — the
  compendium shows only Hounds, so a player reading the bestiary sees the ongoing chip attack but
  not the opening debuff.
- **Hounds** is the terminal state: it is its own follow-up, so once the raider reaches it there is
  no path back to Track. Frail is applied exactly once per fight, on turn one, and never refreshed.
- Because the machine cannot transition away before its current move has been performed at least
  once, a skipped/stunned enemy turn shifts the schedule rather than scrambling it. Track always
  happens first, and Hounds always follows immediately.

## 3. Numbers

| Stat | Base | Ascension variant |
|---|---|---|
| Starting HP | 21–25 (rolled) | 22–26 with *Tough Enemies* |
| Track | Frail 2 to all opposing heroes, 0 damage | unchanged at every ascension |
| Hounds damage per hit | 1 | 1 (unchanged) with *Deadly Enemies* |
| Hounds hit count | 8 | **9** with *Deadly Enemies* |
| Self block | none — it never defends | — |

Derived, single player:

| | Base | Deadly Enemies |
|---|---|---|
| Turn 1 damage | 0 | 0 |
| Damage per turn from turn 2 on | 8 (as 8×1) | 9 (as 9×1) |
| Damage over a 5-turn fight | 32 | 36 |

**Frail semantics.** Frail is a counter-type debuff that multiplies the affected hero's Block from
powered cards and monster moves by **0.75** (a flat −25% on Block gained), and it ticks down by one
at the end of each enemy turn — so Frail 2 covers the player's next two turns of blocking, i.e.
precisely the first two Hounds turns and whatever the other two raiders do in that window.

**Hit-count is the whole design.** 8×1 is not the same as 8: every point of the player's Block
subtracts against each hit individually, so any meaningful Block wall reduces Hounds to zero, while
an unblocked hero eats the full 8. That is why Track comes first — the raider spends its opening
turn making the player's Block 25% worse *before* it starts throwing damage that Block trivially
absorbs. Corollaries worth carrying into the model:

- Per-hit player effects fire 8–9 times a turn: Thorns-style retaliation, per-hit triggers, and
  "when attacked" counters all get maximum value against this body; flat damage reduction / per-hit
  mitigation nullifies it outright.
- Anything that raises the raider's damage *per hit* is multiplied by 8–9. Nothing in this
  encounter does so — the Brute's self-buff is self-targeted and never reaches the Tracker — but a
  relic/curse/modded source that adds enemy Strength would be catastrophic here and nowhere else in
  the raider pool.

## 4. Scaling

**By act:** none. No act-varying stats, and the encounter exists only in Act 1.

**By ascension:** two independent bumps, both small.
- *Tough Enemies* (A8) raises the HP band by exactly 1 at both ends (21–25 → 22–26).
- *Deadly Enemies* (A9) adds **one extra hound hit** (8 → 9). Per-hit damage stays at 1 — this is
  the only raider whose "deadly" bump is a hit-count change rather than a damage change, and
  against a blocking player it is worth almost nothing, while against a naked player it is +1.
- Frail 2 is untouched at all ascensions. No added moves, no cycle change.

**By seat count (multiplayer):**

1. **HP** is multiplied by `players × 1.1` (the Act 1 co-op factor):

   | Players | HP band |
   |---|---|
   | 1 | 21–25 (unscaled) |
   | 2 | ~46–55 |
   | 3 | ~69–83 |
   | 4 | ~92–110 |

2. **Track hits every seat.** The debuff move targets the full list of player creatures, so a
   4-player table takes Frail 2 on *all four* heroes from one enemy turn. There is no split, no
   choice, and no single-target version.
3. **Hounds also resolves against every opposing creature** — each hero eats the full 8×1 (9×1 at
   A9), not a share of it. Table-wide chip therefore scales linearly with seat count on top of the
   HP scaling.
4. **No block scaling applies**, because it never gains Block. Unlike the Axe/Crossbow raiders,
   co-op does not make this body harder to kill beyond the raw HP multiple — it only makes it
   take longer while it keeps chipping four people at once.

## 5. Support role inside the encounter

Frail is the only raider effect that improves the *other* raiders' turns: −25% Block on every hero
for two turns lands exactly when the Axe Raider's ramp and the Crossbow/Assassin big hits are due.
Treat Tracker as the encounter's force multiplier rather than as a damage source — its own lifetime
output in a typical 4–5 turn fight is under 35, but it can convert a comfortable block turn against
a 12–16 damage sibling into 3–4 points of leaked HP.

## 6. Proposed fight class — `attrition`

Reasoning from what the fight demands per turn: after a single zero-damage opening, this body asks
the same modest question every single turn forever — a flat 8 (9 at A9) delivered as eight separate
pinpricks, with no peak to brace for and no window where ignoring it is free. There is nothing to
burst through and nothing to time; the demand is *sustained partial mitigation plus a clock*, and
the Frail rider is a tax on exactly the resource the answer uses (Block), which is what makes the
steady drip actually cost HP instead of being fully absorbed. It is not `spike` (its damage curve
is flat after turn one and its single largest hit is 1), not `swarm` at the individual level (one
body, no summons — the three-raider encounter around it is the swarm layer and Track B should model
that at the encounter level), and not `gimmick` (multi-hit and Frail are both standard vocabulary).
For the demand curve, treat it as **a constant-pressure baseline with a two-turn −25% Block
modifier stamped on the front**, and note that its damage is unusually sensitive to whether the
player's mitigation is per-hit or per-turn.
