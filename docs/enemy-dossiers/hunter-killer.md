# Enemy Dossier — Hunter Killer

- **Class:** `HunterKiller`
- **Kind:** normal
- **Act:** Act 2 (`Hive`, act index 1) — the only act pool it appears in
- **Encounters:** `HunterKillerNormal` (one Hunter Killer, alone — it is the whole fight)
- **Fight class:** `attrition`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

A solo bruiser with a fat HP pool, no Block, no summons, no buffs, no on-death effect and no low-HP
phase change. It opens with a single debuff turn — the "tenderizing goop" — and then does nothing but
alternate two attacks for the rest of the fight. Everything interesting about it lives in that one
opening debuff, **Tender**, which is a permanent tax on *how many cards you play per turn* rather than
on any single stat.

At 121 HP (126 on Tough Enemies) it is one of the chunkier Act 2 normals for a single body, and it
deals no damage at all on turn 1, so the fight is a long, fully-telegraphed exchange.

## 2. Intent pattern / AI

Three move states plus one random branch. The first move is fixed; every subsequent turn is a weighted
coin flip with repeat guards.

| State | Intent shown | Effect |
|---|---|---|
| `TENDERIZING_GOOP_MOVE` | debuff | Applies **1 Tender** to *every player*. Cast animation, no damage. |
| `BITE_MOVE` | single attack, 17 | One attack hit of 17 (19 on Deadly Enemies). |
| `PUNCTURE_MOVE` | multi-attack, 7 × 3 | Three attack hits of 7 (8 on Deadly Enemies) = 21 (24). Animation plays once, hits land three times. |

**Flow.** Turn 1 is always the goop. Nothing ever routes back to it, so Tender is applied exactly once
per fight and never re-applied or re-stacked. From turn 2 onward the enemy sits in a random branch
between Bite and Puncture, both at weight 1, with two repeat guards:

- **Bite cannot repeat** — it may never be chosen twice in a row.
- **Puncture may repeat at most twice** — it may never be chosen three times in a row.

Those two guards make the chain much tighter than a 50/50 looks:

- After a **Bite**, Bite is weighted to zero, so the next turn is **always Puncture**.
- After a **single Puncture**, it is a true 50/50 between Bite and a second Puncture.
- After **two Punctures in a row**, Puncture is weighted to zero, so the next turn is **always Bite**.

So the legal move strings are just `…P B P…` and `…P P B…`: Bite is always isolated, Puncture never
appears three deep. Practical patterns look like `Goop, P, P, B, P, B, P, P, B, …`.

Stationary mix of that chain is **40% Bite / 60% Puncture**, which is the number to use for
expected-damage math (see §4). The branch itself does not appear in the move log — only the three
real moves do — so the repeat guards are counting *performed moves*, not branch visits.

There is no low-HP trigger, no enrage, no reaction to player buffs, and no move that gains Block, so
the enemy-Block multiplayer scaler never applies to it.

## 3. Gimmicks

**Tender (the whole enemy, mechanically).** A permanent counter-style debuff applied to every player on
turn 1. It is never removed and never re-applied, and its displayed number is not a stack count — it is
a live readout of *how many cards you have played this turn*.

How it actually works, per player, per turn:

1. Each time that player plays a card, they immediately take **−1 Strength and −1 Dexterity** (applied
   silently, without the usual debuff flash).
2. At the end of that side's turn, the full amount is **refunded** — the player gets back exactly as
   much Strength and Dexterity as they lost — and the counter resets to zero for the next turn.

So the penalty never accumulates across turns; it accumulates *within* a turn and then unwinds. The
consequences are what matter:

- The **first card each turn is at full power.** The Nth card of a turn is played at −(N−1) Strength
  and −(N−1) Dexterity.
- It punishes **wide, cheap turns symmetrically on offense and defense**: a five-card block turn loses
  0+1+2+3+4 = 10 Block off the top, and the same arithmetic eats an attack chain.
- It rewards **few, expensive, high-impact cards**, and it is close to a hard counter to
  many-small-hits and cost-reduction/free-card engines. Retain/hold strategies are not penalized;
  only the act of playing is.
- Because the loss is applied *after* each card resolves, ordering matters: front-load the cards whose
  numbers scale with Strength/Dexterity and dump the flat-effect or zero-scaling cards at the end of
  the turn.
- Multi-hit attacks the player owns suffer the Strength penalty **per hit**, so they degrade fastest.

Each player's counter tracks only their own card plays, and only cards they own trigger it.

**Puncture's hit-splitting.** 7 × 3 is the same total as 21 against a plain Block pool, but it is a
different number against anything that resolves per hit — Intangible reduces it to 3 instead of 1, and
it triples any player Thorns / on-hit-when-attacked payout. It is the only per-hit texture in the
fight.

## 4. Numbers

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP (fixed, no roll) | 121 | 126 | — |
| Tenderizing Goop | 1 Tender to every player | — | — |
| Bite | 17 | — | 19 |
| Puncture | 7 × 3 hits = 21 | — | 8 × 3 hits = 24 |

Derived per-turn damage, using the 40/60 Bite/Puncture stationary mix:

| Ascension state | Avg damage per attack turn | Turn 1 |
|---|---|---|
| Base | **19.4** | 0 (goop only) |
| Deadly Enemies | **22.0** | 0 (goop only) |

- Damage band per turn is narrow: 17–21 base, 19–24 on Deadly Enemies. There is no turn that spikes
  above that and no turn (after turn 1) that falls below it.
- Time-to-kill at a typical Act 2 clip of ~22 damage/turn is roughly 6 attack turns, i.e. about
  **115–130 total incoming damage** to mitigate in single-player, and every point of that mitigation
  has to be generated under the Tender tax.

## 5. Scaling

**By act:** none. Act 2 only, no act-conditional stats or moves.

**By ascension:** two flat levers, no behavioral change. Tough Enemies raises HP 121 → 126. Deadly
Enemies raises Bite 17 → 19 and each Puncture hit 7 → 8 (21 → 24 per puncture turn). The Tender
application (1, once) has no ascension variant, and the branch weights and repeat guards do not change
at any ascension.

**By seat count (multiplayer):**

- *HP* uses the shared formula — base × player count × act factor, with the Act 2 non-boss factor
  being **1.2**:

| Players | Effective HP (base 121) | Effective HP (Tough Enemies, 126) |
|---|---|---|
| 1 | 121 | 126 |
| 2 | ~290 | ~302 |
| 3 | ~436 | ~454 |
| 4 | ~581 | ~605 |

- *Both attacks hit every seat.* Monster attacks here target all opponents, and the target list is
  refreshed between hits, so Bite lands 17 on each player and Puncture lands 7 three times on each
  player. Incoming pressure per seat does **not** dilute as the table grows — total damage output
  scales linearly with seat count while HP scales by 1.2× per seat, so a fuller table is *net harder*
  per unit of HP.
- *Tender* is applied to every player on turn 1 — nobody is exempt and there is no per-seat amount
  change. Each player's counter is driven only by their own plays, so the tax is felt individually but
  universally.
- It never gains Block, so the enemy-Block multiplayer scaler is inert here.

Net co-op shape: this is one of the fights that gets *worse* with seats rather than better. Everyone
eats a full-size hit every turn, everyone is under the Tender tax, and the only thing the extra seats
buy is more damage into a pool that grew by 1.2× per player.

## 6. Proposed fight class — `attrition`

Per turn this fight asks the same thing repeatedly: absorb a flat 17–21 (19–24 on Deadly Enemies) with
**as few card plays as you can manage**, for six-plus turns, against a body big enough that no
realistic Act 2 deck bursts it down. Nothing spikes — the damage band is narrow, fully telegraphed one
turn ahead, and never escalates — so `spike` is wrong; it is one body, so not `swarm`; and there is no
second demand type layered on, so not `mixed`. The case for `gimmick` is Tender, but Tender is not a
puzzle with a solution state — it is a per-turn efficiency tax that makes the grind more expensive
without changing what the grind is. For Track B, model this as a **long flat-pressure grind with a
convexity penalty on cards-per-turn**: the demand curve is "sustain ~20/turn for 6+ turns," and the
correct counterplay is condensing your turn into one or two big plays rather than spreading across a
wide hand — a deck that wins this fight is one whose block and damage come from few cards, not cheap
ones.
