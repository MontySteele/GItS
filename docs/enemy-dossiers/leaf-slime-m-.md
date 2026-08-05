# Enemy Dossier — Leaf Slime (M)

- **Class:** `LeafSlimeM`
- **Kind:** normal
- **Act:** Act 1 (`Overgrowth`, act index 0) — the only act pool it appears in
- **Encounters:** `SlimesNormal` (always present: Twig Slime M + Leaf Slime M + two small slimes, four bodies), `SlimesWeak` (one random medium — 50% Leaf — plus two different small slimes), `FlyconidNormal` (one random medium + Flyconid), `SlitheringStranglerNormal` (Slithering Strangler plus, on one of three equally likely secondary rolls, one random medium)
- **Fight class:** `attrition`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

The medium Leaf Slime is Act 1's **deck-pollution metronome**. It has exactly two moves and it strictly
alternates between them forever: a status move that jams two Slimed into every player's discard pile,
and a single-target-per-seat 8-damage spit. It opens on the status move, so the very first thing it does
in a fight is make your deck worse, and the damage only starts on turn two.

There is no Block move, no buff, no summon, no split, no on-death effect, no low-HP phase, no reaction
to allies dying, and — unusually — **no randomness at all** in its AI. Its small cousin (`LeafSlimeS`)
picks between its two moves at random with a no-repeat rule; the medium does not roll dice. Once you
have seen one turn of it you know every turn of the rest of the fight.

## 2. Intent pattern / AI

Two move states wired into a closed two-node loop, each naming the other as its follow-up. The machine's
initial state is the **status** move, and the engine's "don't transition before the first move has been
performed" rule means the opener is not skipped.

| Turn | Move | Intent shown | Effect |
|---|---|---|---|
| 1 | Sticky Shot | status-card intent, count **2** | Adds **2 Slimed** to the **discard pile of every player** |
| 2 | Clump Shot | attack, single | **8 damage** (9 on Deadly Enemies) |
| 3 | Sticky Shot | status-card intent, count 2 | 2 Slimed to every player again |
| 4 | Clump Shot | attack | 8 damage |
| … | strict alternation, indefinitely | | |

**Odd turns are always status, even turns are always damage.** There is no cooldown table, no weighting,
no opening special case beyond "the status move is the opener", and no state that can break the cycle.
The intent display is fully honest and fully predictive: you can plan the entire fight from turn 1.

Steady-state output is therefore **8 damage every other turn and 2 Slimed every other turn** — an average
of 4 damage and 1 Slimed per turn (4.5 damage/turn on Deadly Enemies).

## 3. Gimmicks

**Slimed is an energy tax, not a card-economy tax.** The Slimed status costs 1 energy, exhausts on play,
and **draws 1 card** when played. Because it replaces itself in hand, it does not shrink your hand or
choke your draw quality after the fact — what it takes is *energy*, one per copy, on whatever turn the
copy surfaces. Two copies is roughly two-thirds of a standard turn's energy for a three-energy deck, and
the slime posts that bill every other turn for as long as it lives. Simply refusing to play them is also
a real option (they clog hand size instead), which is what makes this an economy decision rather than a
hard cost — but the decision recurs every two turns.

**The pollution is deferred and compounding.** Slimed lands in the **discard pile**, not the hand, so the
copies from turn 1 do not bite until the deck reshuffles. A fight that ends in four or five turns pays
almost none of the tax; a fight that runs eight-plus turns pays it repeatedly and with interest, because
by then eight or ten Slimed are circulating in a small Act 1 deck. The enemy's threat is a direct
function of how long the *room* lives, not of how long the slime lives — and it is almost always the
last thing in the room worth killing, which is exactly the trap.

**Party-wide status, per-seat attack.** The status move applies to the full player list, so *every seat*
eats 2 Slimed per cast with no dilution. The attack likewise resolves against all opponents at full
printed value (monster attacks in this engine default to targeting all opponents). Nothing in the kit is
divided by seat count.

**It is a body in a crowd.** All four of its encounters put it next to at least one other monster, and in
`SlimesNormal` it is one of four. Slime packs assign each body a distinct HP roll from within the band,
so the two mediums in `SlimesNormal` never have identical HP bars — the pack is deliberately staggered
so that AoE does not clear it in one clean tick.

## 4. Numbers

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP roll (min–max) | 32–35 | 33–36 | — |
| Clump Shot (attack) | 8 | — | 9 |
| Sticky Shot (status) | 2 Slimed to each player's discard | — | — |
| Slimed | cost 1, Status, Exhaust, "Draw 1" | — | — |

- Raw damage output averages **4.0/turn** (**4.5/turn** on Deadly Enemies). Worst single turn is **8**
  (**9**). There is no multi-hit move and no burst of any kind.
- Effective pressure is higher than the damage number suggests: the ~1 Slimed/turn is worth roughly
  1 energy/turn of lost tempo once the deck reshuffles, which in Act 1 terms is comparable to the 4
  damage itself.
- It never gains Block, so the multiplayer enemy-Block scaler never applies to it.

## 5. Scaling

**By act:** none. Act 1 only; no act-conditional stats or moves.

**By ascension:** two flat levers, both small. Tough Enemies shifts the HP band up by exactly 1 at both
ends (32–35 → **33–36**) — the smallest ascension HP bump in the slime family. Deadly Enemies takes the
attack 8 → **9**. The Slimed count (2) is *not* ascension-scaled, and neither is the alternation pattern,
so the fight's shape is identical at every ascension: the tax is fixed and only the clock and the chip
move.

**By seat count (multiplayer):**

- *HP* uses the shared formula — base roll × player count × act factor, with the Act 1 factor being
  **1.1**.

| Players | Effective HP band (base roll 32–35) |
|---|---|
| 1 | 32–35 (no scaling at 1 player) |
| 2 | ~70–77 |
| 3 | ~106–116 |
| 4 | ~141–154 |

- *The attack hits every seat* at full printed value; per-seat damage does not fall off as seats are added.
- *The status hits every seat* at the full 2 copies. At four players a single Sticky Shot injects **8
  Slimed into the party's combined decks**, and there is no shared-clear mechanic — each seat pays its own
  energy to dig out. The pollution scales linearly with the party while the HP bar scales only ~1.1× per
  seat, so **in co-op the tax outpaces the kill clock**: the slime lives proportionally longer per point of
  party damage output while taxing proportionally more decks.
- No move has a seat-count-conditional branch and no amount is multiplied by player count.

## 6. Proposed fight class — `attrition`

What this enemy demands, turn by turn, is *endurance and economy discipline*, never a burst answer: 8 is
trivially blockable and arrives on a schedule you can read from turn 1, so no turn ever asks for a spike
of Block or a panic kill. The real cost is cumulative — one Slimed per turn of energy tax, deferred into
the discard pile so it only lands once the fight has gone long — which means the fight punishes slow
clears and rewards killing the room fast, the defining shape of an attrition demand curve. It is not a
`gimmick` (there is no puzzle state or special rule, only a status drip), and although it lives in
multi-body slime rooms, the swarm pressure belongs to the encounter's headcount rather than to this unit,
whose own contribution is a flat two-turn loop. For Track B, model it as **low, perfectly predictable
per-turn damage plus a linearly accumulating resource tax whose bite is a function of fight length** —
and note that in co-op the tax scales with seats while its HP does not keep pace, so its attrition weight
should rise with party size.
