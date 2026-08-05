# Zapbot — behavior dossier

- **Class:** `Zapbot`
- **Kind:** normal (non-elite, non-boss)
- **Act:** Act 3 (`Glory`, act index 2)
- **Encounter:** none of its own. Zapbot has **no encounter that generates it** — it exists only as a `Fabricator` spawn inside `FabricatorNormal`, where it is one of the two members of the Fabricator's *aggro* spawn pool (the other is Stabbot). It appears in that encounter's possible-monsters set for bestiary purposes only.
- **Proposed fight class:** `spike`

*Behavioral notes only — no decompiled source is reproduced here.*

## Intent pattern

Structurally the same one-line state machine as its aggro-pool twin: **one move, wired to follow itself**, no branch, no randomness, no opener exception.

- **Zap** — a plain *single-attack* intent. No rider, no debuff, no status card, no second intent icon.

What makes Zapbot different from Stabbot is not the move list, it is what happens *between* moves. On being added to the room, Zapbot immediately gains **High Voltage 2** — a counter-style self-buff that, at the end of every enemy-side turn it takes part in, grants it **Strength equal to that counter (2)**. The counter itself never decays or spends, so Zapbot gains **+2 Strength every single turn, forever, from the turn it lands**.

Consequently the intent number the player reads is not a constant. It is an arithmetic ramp, and it is honest about it — the attack intent is computed live off current Strength, so the escalating number is fully telegraphed on the enemy's intent icon before each player turn.

**Arrival timing.** The enemy turn processes creatures from a snapshot, so a Zapbot fabricated *during* the enemy turn does **not** attack on the turn it appears; it falls into its bot slot and telegraphs. But the enemy-side turn-end participant list is gathered *at the end* of that turn, so the newly-arrived Zapbot **does** collect its first Strength tick before ever swinging. Its very first Zap therefore already lands at base + 2, and the player's one free turn of grace is also the one turn where it is cheapest to kill.

**How Zapbots arrive (the Fabricator's side of the contract):**

- The Fabricator can fabricate only while **fewer than 4 living teammates** are on the board — four bot slots, hard cap.
- Under the cap it randomly picks (50/50) between **Fabricate** (one *defensive* bot — Guardbot or Noisebot — **and** one *aggro* bot) and **Fabricating Strike** (attack, then one *aggro* bot). Either branch produces **one aggro bot per Fabricator turn**.
- The spawner **excludes whatever it spawned last** from the pool it is drawing from. With a two-entry aggro pool that makes aggro spawns a strict alternation — Zapbot, Stabbot, Zapbot, Stabbot… A player who just watched a Stabbot drop knows the next add is a Zapbot.
- At the 4-bot cap the Fabricator falls back to Disintegrate (attack only) until a slot frees. **Killing a Zapbot re-opens the spawner.**

## Numbers

| Value | Base | Ascension tier |
| --- | --- | --- |
| Starting HP roll | 18–23 | **19–24** (Tough-Enemies tier) |
| Zap damage (printed) | 14 | **15** (Deadly-Enemies tier) |
| High Voltage counter | 2 | 2 (no ascension scaling) |
| Strength gained per enemy turn end | +2 | +2 |
| Block | — | never gains any |

**Effective Zap by turn** (single-player, no player-side modifiers; the Strength tick lands at the end of the enemy turn *including* its arrival turn):

| Its swing | Base run | Deadly-Enemies tier |
| --- | --- | --- |
| 1st | 16 | 17 |
| 2nd | 18 | 19 |
| 3rd | 20 | 21 |
| 4th | 22 | 23 |
| *n*-th | 14 + 2*n* | 15 + 2*n* |

HP is rolled inside the band per body, with a preference for a distinct max-HP value per enemy currently on that side where the band allows — so two Zapbots usually will not share a damage breakpoint.

Damage feedback reads as armor rather than flesh — cosmetic, consistent with the Act 3 construct bestiary.

## Gimmicks

- **A ramp on a body that cannot afford one.** Zapbot pairs the highest per-hit number in the bot family (14, versus Stabbot's 11) with a permanent +2/turn escalator, on an ~20 HP frame with zero block and zero self-protection. The design reads as a **kill-me-now** unit: every turn it survives is worth +2 permanent damage to the enemy team, and the Strength is on the *bot*, so killing it deletes the accumulated ramp entirely. There is no "the buff transfers" clause.
- **It is a minion, not a monster.** The Fabricator marks each bot with a minion-style buff making the bearer a *secondary enemy*, and when the last primary enemy dies, remaining secondary enemies die with it. **Kill the Fabricator and every Zapbot on the board dies too, ramp and all.** That is the standing argument against spending removal on the adds — except that Zapbot is the one add whose growth curve can make that argument wrong.
- **Its death un-gates the spawner.** Freeing a bot slot returns the Fabricator to its fabricate branch. Killing Zapbot buys you damage relief but also buys the enemy another spawn — and half the time that spawn is a *fresh* Zapbot at 16 rather than the 22 you just removed. The reset is real, but it is a reset, not a win.
- **Two Zapbots ramp independently.** Nothing about the buff is shared or capped. With alternation, the board can hold two Zapbots at different points on their curves at once (the older one always ahead by an even number).
- **No status, no debuff, no block, no utility.** Zapbot contributes exactly one thing: an attack number that only ever goes up. Its whole read is arithmetic.
- **Fully honest intent.** Nothing about Zapbot is hidden from the bestiary and nothing is hidden mid-fight; the escalating number is displayed before every player turn.

## Scaling by act / ascension

- **Act:** none. Zapbot is Act-3-only content, reachable only through `FabricatorNormal`. Its numbers do not read the act index; the act index enters only through the multiplayer scaler below.
- **Ascension:** two independent, tier-keyed, single-point bumps.
  - *Tough Enemies* tier: HP band 18–23 → **19–24**.
  - *Deadly Enemies* tier: Zap 14 → **15**.
  - The High Voltage counter (2) does **not** scale — the *slope* of the ramp is fixed across all ascensions; only the intercept moves by one. Spawn cadence, the 4-slot cap and the alternation rule are likewise unscaled.
- Practically, ascension makes Zapbot arrive one point sharper and take one more point to kill; the Fabricator's own ascension bumps reshape the surrounding fight far more.

## Multiplayer / seat-count adjustments

- **HP scales hard, and it scales on spawn.** Enemy max HP is multiplied by (player count × an act factor); for a non-boss Act 3 room that factor is **1.2**. Scaling is applied at creature creation, so **every fabricated Zapbot is scaled** — mid-combat adds are not cheap copies. A 2-player Zapbot is roughly **43–55 HP** (2 × 1.2 × an 18–23 roll), a 3-player Zapbot roughly **65–83**.
- **The ramp does not scale, and that is the co-op problem.** High Voltage is not one of the powers flagged for multiplayer amount scaling, so it stays at +2/turn regardless of seat count — while the body it sits on gets 2.4×/3.6× tankier. The kill window that a solo player closes in one card takes a co-op party two or three, and each turn of slippage is another permanent +2.
- **Damage does not scale, but it lands on every seat.** Monster attacks target the whole opposing player list rather than picking a victim, so Zap hits **each** player for its current value. A single Zapbot on its fourth swing at a 3-player table is 22 damage × 3 seats = 66 party damage in one intent, off one ~70 HP body.
- **Block scaling is irrelevant here** — Zapbot never gains block. (It matters enormously for the Guardbot that can be fabricated alongside it.)
- Net co-op effect: the enemy that most needs to die on schedule is precisely the enemy whose time-to-kill inflates with seat count, while its threat curve does not deflate. Zapbot is the sharpest seat-count outlier in the bot family.

## Fight-class reasoning — `spike`

Zapbot's per-turn demand is not "clear the board" and not "survive a long grind" — it is **close a specific damage window before the number outruns your block curve**. A fixed 14 would be swarm arithmetic like its twin Stabbot, but the permanent +2/turn means the correct play is time-boxed: burst this body down inside two or three turns, or accept a hit that keeps growing past every block card in the deck for the rest of the encounter. The demand is therefore concentrated single-target damage on a deadline, plus one big defensive turn if the deadline is missed — the signature of a spike, and it is the reason a party can lose a Fabricator fight it was winning on paper. The parent encounter around it is a `swarm` (see `fabricator.md`), and Zapbot is the element that punishes the swarm's usual answer of ignoring the adds; classed alone, its own curve is a spike.
