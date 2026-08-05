# Enemy Dossier — Twig Slime (M)

- **Class:** `TwigSlimeM`
- **Kind:** normal
- **Act:** Act 1 (`Overgrowth`, act index 0) — the only act pool it appears in
- **Encounters:** `SlimesNormal` (always present: Twig Slime M + Leaf Slime M + two small slimes, four bodies), `SlimesWeak` (one random medium — 50% Twig — plus two different small slimes), `FlyconidNormal` (one random medium + Flyconid), `SlitheringStranglerNormal` (Slithering Strangler plus, on one of three equally likely secondary rolls, one random medium)
- **Fight class:** `mixed`

> Behavioral notes only. No decompiled source is reproduced here; everything below is a prose/table
> description of the mechanics and constants.

---

## 1. What this enemy is

Twig Slime (M) is the **hitter** of the medium-slime pair. It shares its sibling's two-move kit — a
single attack and a status spit — but the dial settings are inverted: it hits for **11** instead of 8,
its status move injects **1 Slimed instead of 2**, and, crucially, it **rolls** between the two moves
instead of alternating. It also carries the smaller HP bar of the two mediums (26–28 vs 32–35), so it is
the medium slime that dies fastest and hurts most while alive.

There is no Block move, no buff, no summon, no split, no on-death effect, no low-HP phase, and no
reaction to allies dying. The only "state" it carries is the recent-move history that its branch rules
read. It has a Phobia-mode alternate skin, which is purely cosmetic and changes no numbers or behavior.

## 2. Intent pattern / AI

Two move states plus a weighted random branch that both moves feed into. The machine's **initial state
is the status move**, and the engine's "don't transition before the first move has been performed" rule
means the opener is never skipped: **turn 1 is always Sticky Shot**. From turn 2 onward the branch rolls
with equal base weight (1:1) between the two moves, subject to two repeat rules:

- **Sticky Shot cannot repeat** — it is never selected if it was the previous move.
- **Clump Shot can repeat at most twice in a row** — after two consecutive Clumps its weight goes to zero.

Because a zeroed weight leaves only one legal option, the "50/50" collapses to a forced move in two of
the three positions:

| Situation | Legal moves | Result |
|---|---|---|
| Combat start | — (initial state) | **Sticky Shot**, guaranteed |
| Previous move was Sticky | Clump only | **Clump Shot**, guaranteed |
| Previous move was one Clump | Sticky or Clump, 50/50 | coin flip |
| Previous two moves were Clumps | Sticky only | **Sticky Shot**, guaranteed |

So the fight is a chain of two shapes, chosen by one coin flip per cycle:

- `Sticky → Clump` (2-turn cycle), 50% of the time
- `Sticky → Clump → Clump` (3-turn cycle), 50% of the time

**The only unpredictable turn is the one right after a single Clump.** Everything else is forced, and the
intent display is honest one turn ahead in all cases.

Steady state over long fights: cycles average 2.5 turns and contain 1 Sticky and 1.5 Clumps, i.e.
**60% attack turns / 40% status turns**. Average output is **6.6 damage per turn** (7.2 on Deadly
Enemies) and **0.4 Slimed per turn**. The worst two-turn window is back-to-back Clumps for **22** damage
(**24** on Deadly Enemies); three Clumps in a row is impossible.

## 3. Gimmicks

**Slimed is an energy tax, not a card-economy tax.** The Slimed status costs 1 energy, exhausts on play,
and **draws 1 card** when played. It replaces itself in hand, so it does not shrink hand size or degrade
future draws — it takes *energy*, one per copy, on the turn the copy surfaces. At 1 copy per cast and
only ~0.4 casts per turn, the Twig's tax is roughly **a quarter of the Leaf's** (which posts 2 copies
every other turn). This slime is not primarily a pollution engine; it converted most of that budget into
attack damage.

**The pollution is deferred.** Slimed lands in the **discard pile**, so turn-1 copies do not bite until
the deck reshuffles. Short rooms pay almost none of it.

**11 is a large Act 1 normal-enemy hit.** It is the biggest single number in the slime family and it can
land twice in a row. Against opening-deck defensive density that is a real Block demand on a specific
turn, not chip damage — but it arrives with a full turn of telegraph and never stacks a third time.

**Party-wide status, party-wide attack.** The status move applies to the full player list, so *every
seat* eats 1 Slimed per cast with no dilution. The attack likewise resolves against all opponents at
full printed value (monster attacks in this engine default to targeting all opponents). Nothing in the
kit is divided by seat count.

**It is a body in a crowd, and the HP rolls are staggered.** All four of its encounters put it next to at
least one other monster; in `SlimesNormal` it is one of four and is guaranteed present. Slime packs
assign each body a distinct HP roll from within its band, so same-species bodies never share an HP total
and AoE cannot clear the pack on one clean tick.

## 4. Numbers

| Stat | Base | Tough Enemies ascension | Deadly Enemies ascension |
|---|---|---|---|
| HP roll (min–max) | 26–28 | 27–29 | — |
| Clump Shot (attack, "Pokey Pounce" state) | 11 | — | 12 |
| Sticky Shot (status) | 1 Slimed to each player's discard | — | — |
| Slimed | cost 1, Status, Exhaust, "Draw 1" | — | — |

- Damage output averages **6.6/turn** (**7.2/turn** on Deadly Enemies). Worst single turn **11** (**12**);
  worst two-turn window **22** (**24**). No multi-hit move exists.
- Status output averages **0.4 Slimed/turn** per seat — about 0.4 energy/turn of deferred tempo once the
  deck reshuffles.
- It never gains Block, so the multiplayer enemy-Block scaler never applies to it.
- Family comparison (medium slimes, base values): Twig **26–28 HP / 11 dmg / 1 Slimed / randomized**;
  Leaf **32–35 HP / 8 dmg / 2 Slimed / strict alternation**. Twig deals ~65% more damage per turn off a
  ~20% smaller HP bar.

## 5. Scaling

**By act:** none. Act 1 only; no act-conditional stats or moves. (`Overgrowth` also forces a `SlimesWeak`
room into an early slot of its weak-encounter set, so a medium slime — Twig on a coin flip — is a very
common first or second fight of a run.)

**By ascension:** two flat levers, both small. Tough Enemies shifts the HP band up by 1 at both ends
(26–28 → **27–29**). Deadly Enemies takes the attack 11 → **12**. The Slimed count (1), the branch
weights, and the repeat rules are *not* ascension-scaled, so the fight's shape is identical at every
ascension — only the clock and the size of the hit move.

**By seat count (multiplayer):**

- *HP* uses the shared formula — base roll × player count × act factor, with the Act 1 factor being **1.1**.

| Players | Effective HP band (base roll 26–28) |
|---|---|
| 1 | 26–28 (no scaling at 1 player) |
| 2 | ~57–62 |
| 3 | ~86–92 |
| 4 | ~114–123 |

- *The attack hits every seat* at full printed value — 11 to each hero, so party-wide damage taken scales
  linearly with seat count while its HP scales at only ~1.1× per seat. In co-op this is the medium slime
  that actually threatens to kill someone.
- *The status hits every seat* at 1 copy each; at four players a single Sticky Shot injects 4 Slimed into
  the party's combined decks.
- No move has a seat-count-conditional branch and no amount is multiplied by player count.

## 6. Proposed fight class — `mixed`

Turn to turn this enemy asks two different questions and does not tell you in advance which one is
coming: on Clump turns it demands roughly 11 points of mitigation *right now* (and can demand it twice
running, for 22–24 across two turns, which is genuine burst pressure for an Act 1 deck), while on Sticky
turns it demands nothing defensively and instead bills about one energy of deferred tempo. Neither demand
dominates — the attack is 60% of its turns and carries most of its threat, but the status is a real,
accumulating economy cost that its sibling's `attrition` label is built around, and this unit runs the
same tax at a quarter rate. It is not `spike` (there is no wind-up turn, no multiplier, and a hard cap of
two consecutive attacks), not `attrition` (the damage is too front-heavy and the tax too thin to make
fight length the governing variable), and not `gimmick` (no puzzle state or special rule). For Track B,
model it as **a 60/40 split between a large blockable single hit and a small recurring resource tax, with
one genuinely random turn per cycle**, and note that in co-op the attack scales linearly across seats
while its HP does not keep pace — making it the priority kill in every slime room it appears in.
