Status: RECORD

# Prototype balance read — both overhaul arms, 2026-09-02

A READ, not a ruling; nothing here changes a number, and none of it is quotable
as a statement about the design (R215 B). Rows: `docs/prototype-surface.yaml`
(`proto_ko_` 30, `proto_kk_` 28); world `RT12/D18/P11/C21`, `main` `c61bc826`.

**The Klee arm does not run in this engine.** Its eight Bomb ops are registered
in `tier0/engine/effects.OPS` as `_op_klee_overhaul_unbuilt`, which raises by
design — that arm is C# first. Every Klee number below is arithmetic off the
sheet; no Klee row has offered / picked / played / winrate data.

## 1. Card in a vacuum

Assumptions, both arms: Strength 0, nothing already applied, no relic but the
arm's own starter, one enemy unless a row says every enemy (a `/ 3` column is
the three-enemy value). Yardsticks: **Strike 6 per energy**, **Defend 5**.
**Klee.** A Bomb grows **3** at the start of her turn
(`C.KLEE_OVERHAUL_BOMB_GROWTH`) and goes off only when a *Set off* card says
so; each explosion pays 1 Spark; she opens with 1. **Ka-pow! costs 0 energy**,
so a Bomb is always cashable free and its damage is credited to the card that
planted it. `now` = cashed the turn planted, `+1` / `+2` = after one or two
dawns; `B` = bomb total on the target, `n` = bombs on it.

| card | cost | now | +1 dawn | +2 dawn |
|---|---|---|---|---|
| Ka-pow! (basic) | 0 | 4 + B | — | — |
| Jumpy Dumpty (basic) | 1 | 8, then a Mine 3 per enemy | 11 | 14 |
| Fish-Flavored Bait C | 1 | **10** | 13 | 16 |
| Pocket Fireworks C | 1 | 9 | 9 | 9 |
| Pop! C | 0 | 5 | 8 | 11 |
| Mine Toss C | 1 | 4 / 12 | 7 / 21 | 10 / 30 |
| Chain Fuse C | 1 | 3n | 3n | 3n |
| Sizzle C | 1 | 6 + B (12 + B after a bomb reaction) | | |
| Ammo Scavenging C | 1 | 4 + a draw per bomb set off | 7 | 10 |
| Run Away! C | 0 | 3 Block (7 if a bomb went off) | — | — |
| Sorry, Jean… C | 1 | Block = the bomb's size (8 off Jumpy) | 11 | 14 |
| Fwoosh! C | 0, 1 Spark | 5 + B, random enemy | | |
| Tinder Toss C | 0, 1 Spark | 8 over two random enemies + their B | | |
| Quick Fuse C | 0, 1 Spark | B + 3n | | |
| Dig In C | 0, 1 Spark | 8 Block | — | — |
| Explosives Workshop U | 1 | +1 per bomb per turn, forever | | |
| Careful Arrangement U | 1 | +2, and every bomb onto one enemy | | |
| Big Badda Boom U | 2 | (12 + 2B)/2 → 6 alone, **14** on a Bomb 8 | 17 | 20 |
| Bang Bang! U | 0, 2 Sparks | 8 + B, then a Bomb 4 | | |
| Rapid Fire U | 2 | 6 (12 spread) + B on each enemy hit | | |
| Perfect Timing U | 1 | 8 + B (16 + 2B after a bomb reaction) | | |
| Flame Dance U | 1 | 5 / 15, + Set off any non-Pyro aura | | |
| Catalytic Converter U | 1 | +1 Spark per reacting explosion | | |
| Powder Charge U | 0, 1 Spark | 6 | 9 | 12 |
| Grounded U | 1 | 6 Block/turn, only if nothing went off | | |
| The Big One R | 3 | (10 + 2B)/3 → 3.3 alone, 8.7 on a Bomb 8 | 12.7 | **22** on two Bombs 14 |
| Alice's Recipe R | 1 | +1 per bomb per turn (see §4b) | | |
| Chained Reactions R | 1 | a Bomb 3 per explosion, compounding | | |
| Sparks 'n' Splash R | 2 | one free Set off every turn | | |
| Sugar Rush R | 0, 2 Sparks | +2 energy and a card, exhaust | — | — |

## 2. Kokomi — the vacuum and the sim, one table

A Plan is written by playing the card on the jellyfish and carried out at the
start of her next turn; taking the Plan gives up the now-line entirely. The
**Tamakushi Casket** adds 2 Hydro per debuff *application* — one per enemy, not
per stack (`kokomi_plan.casket_strike`) — counted in every debuff row. Weak is
priced at the base game's 25% and Vulnerable at 50% of a 7-damage intent, so
**1 Weak = 1.75**, **1 Vulnerable = 3.5**; Max HP 80, so a quarter is 20; Mend
counts 1:1.
Sim: `tools/prototype_card_read.py` (new, with
`tier0/tests/test_prototype_card_read.py`), setting `C.KOKOMI_OVERHAUL` in
process the way the arm's own test fixture does. **1,500 runs, seed 42, act-1
instrument** — the three-act win rate is 0.008, which would flatten every split
to zero. `off` = share of runs the row reached a reward screen; `pick` = picks
per offer; `play` = plays per draw (draws bracketed where thin); `wr` = act-1
clear of runs that finished carrying it vs runs that did not, **correlational
only**: drafter and shop choose in response to how the run is already going.

| card | cost | now (1 / 3) | dawn (1 / 3) | off | pick | play | wr carry / not |
|---|---|---|---|---|---|---|---|
| Kurage's Oath (basic) | 1 | — | **5** / 15 | — | — | 0.542 | 0.386 / 0.765 |
| Slack Water (basic) | 1 | 7.75 | 5.5 / 16.5 | — | — | 0.569 | 0.439 / (n=7) |
| Salt Line C | 1 | 8 Blk, exhaust | — | 0.473 | **0.623** | 0.452 | 0.614 / 0.323 |
| Deep Current C | 1 | 4 / 12 | — | 0.474 | 0.385 | 0.536 | 0.534 / 0.402 |
| Coral Bulwark C | 1 | 6 Blk | 9.75 | 0.476 | 0.333 | 0.528 | 0.629 / 0.373 |
| Sea-Salt Prayer C | 1 | 7.75 | — | 0.489 | 0.323 | 0.516 | 0.657 / 0.361 |
| Cleansing Wave U | 1 | 5 Blk, a debuff off her | 10 Blk | 0.453 | 0.220 | 0.305 | 0.648 / 0.389 |
| The Clouds Like Waves R | 2 | 2 Blk per debuff applied | — | 0.159 | 0.138 | 0.157 | 0.776 / 0.429 |
| Read the Field C | 1 | 4 Blk | 10 Blk | 0.483 | 0.114 | 0.222 | 0.643 / 0.410 |
| The General's Banner U | 1 | 3.75 per Companion | — | 0.480 | 0.087 | 0.274 | 0.840 / 0.404 |
| The Moon Overlooks the Waters R | 2 | every Plan now **and** at dawn | — | 0.141 | 0.084 | 0.075 | 0.806 / 0.431 |
| Treatise U | 1 | draw 1 per Plan | — | 0.441 | 0.071 | 0.315 | 0.814 / 0.413 |
| Stolen Chapter C | 1 | draw 1 | draw 3 | 0.479 | 0.069 | 0.246 | 0.697 / 0.422 |
| Song of Pearls U | 1 | 3 Blk per Plan | — | 0.436 | 0.058 | **0.761** | 0.785 / 0.421 |
| Feint C | 1 | 4 | 9 | 0.488 | 0.038 | 0.509 | 0.522 / 0.436 |
| Rally C | 1 | 3.75, next Companion −1 | — | 0.487 | 0.018 | 0.252 | 0.548 / 0.437 |
| Exposed Flank C | 1 | 5.5 | 9 / **27** | 0.471 | 0.011 | 0.212 | 0.500 / 0.439 |
| Ambush C | 1 | — | 12 | 0.465 | **0.000** | — (2) | — |
| War Council U | 1 | — | 7.75 / **23.25** | 0.462 | **0.000** | 0.200 (5) | — |
| Chain of Command U | 1 | — | 4 per Companion that turn | 0.476 | **0.000** | 0.000 (18) | — |
| Battle Plan U | 1 | — | +2 energy, a card | 0.459 | **0.000** | 0.262 (65) | — |
| Change of Plans C | 0 | carries out the front Plan now | — | 0.480 | **0.000** | 0.000 (39) | — |
| Moon's Reflection U | 1 | replays a Plan from exhaust | — | 0.474 | **0.000** | 0.000 (58) | — |
| Undertow C | 1 | 7 (10 vs a debuff) | — | 0.477 | **0.000** | 0.167 (6) | — |
| Vanguard C | 0 | — | **9.25** at no energy | 0.470 | **0.000** | **1.000** (13) | — |
| Nereid's Ascension R | 2 | — | every Plan twice, 2 turns | 0.137 | **0.000** | 0.000 (25) | — |
| Sango Isshin R | 2 | 10 | 10 / **30** | 0.133 | **0.000** | 0.000 (11) | — |
| The Moon, A Ship R | 2 | Mend 10 → 5, exhaust | Mend 15 → 7.5 | 0.148 | **0.000** | 0.000 (14) | — |

Run level, from a second cohort of **600 runs, seed 1042, all three acts**: win
rate **0.008**; reached / cleared 1.000 / 0.462, 0.462 / 0.105, 0.105 / 0.008;
deaths by act **323 / 214 / 58** (595 of 600 died); average fight **5.91
turns** over 5,639 fights, 9.4 a run. The act-1 cohort clears **0.440** at 5.33.

## 3. Dead, automatic, weak, over

**The zero pick rates are the drafter, not the cards.** `draft._static_power`
prices a row's `effects:` list and never its `plan:` list, and has no price for
`mend`, `damage_quarter_max_hp`, a bare `conditional` or the queue verbs. Sixteen
of the 28 rows therefore score **0.00**, under `DRAFT_SKIP_THRESHOLD` 0.5, so they
reach a deck only through the late-deck hatch that passes a Power or a draw/energy
card regardless of score — which is why the five Powers and Stolen Chapter show
6–14% and the other eleven zero. `STATE.md` already records the state in a line
of its own: every drafter price on this arm is still ZERO.

- **Dead (never picked), 11 rows:** ambush, war council, chain of command,
  battle plan, change of plans, moon's reflection, undertow, vanguard, nereid's
  ascension, sango isshin, the moon a ship — all priced 0.00, nine Plan-carrying.
  Six are dead in hand too (chain of command 0/18, change of plans 0/39, moon's
  reflection 0/58, nereid's ascension 0/25, sango isshin 0/11, the moon a ship
  0/14), the pilot reading them zero for the drafter's reason. Undertow proves
  it is the instrument: 7 damage rising to 10 against a debuff, above Strike,
  priced 0 because its body is a `conditional`.
- **Automatic:** vanguard, 13 plays on 13 draws — 0 energy, exhaust, all
  upside. Song of Pearls 0.761. Then the six 1-cost staples at 0.51–0.57 (slack
  water, kurage's oath, deep current, coral bulwark, sea-salt prayer, feint),
  the ceiling a 1-energy card can reach in a 5-card hand on 3 energy. *Play
  order is not instrumented; play-per-draw is the proxy.*
- **Weak (under the yardstick on every column):** *Kokomi* — Kurage's Oath (5
  per energy single-target against Strike's 6, a turn late, and it spends the
  whole play); Feint's now-line (4 vs 6); Read the Field's now-line (4 Block vs
  5); Rally (3.75 plus a conditional discount). *Klee* — Chain Fuse on one Bomb
  (3, half a Strike; two Bombs to match); Careful Arrangement (+2 for 1);
  Grounded (6 Block a turn, but only in turns she set nothing off, so it pays
  her not to use the kit); Sorry, Jean… (1 energy to turn a Bomb into the same
  number of Block, when Ka-pow! cashes it as damage for nothing).
- **Over (more than double on the first column):** *Kokomi* — Vanguard (9.25 at
  no energy); Change of Plans (0 energy, turning Ambush's 12 into a same-turn
  12); The Moon Overlooks the Waters (2 energy, doubling every Plan card for
  the fight). Ambush at 12 and Read the Field at 10 Block sit exactly on 2×,
  the boundary rather than over. *Klee* — Big Badda Boom on a grown Bomb (14 on
  a Bomb 8, 20 on a Bomb 14); The Big One on two Bombs 14 (22); Fish-Flavored
  Bait reaching 16 by the second dawn. **And the shape: ten of Klee's thirty
  rows cost no energy at all** (three free, seven priced in Sparks) against two
  of Kokomi's twenty-eight — a third of that pool is off the energy curve,
  priced in a currency the Bombs mint.

## 4. The two known reads

**(a) Kurage's Oath — CONFIRMED.** 1 energy for 5 to every enemy one turn
later, with no now-line, so planning it costs the turn: behind Strike's 6 at
one enemy, ahead only from two. The sim agrees from a second direction — she
plays it on 54% of draws and it dies in hand 8,035 times, and act-1 clear was
**38.6%** across the 1,287 runs that finished carrying it against **76.5%**
across the 213 that had removed it. That split is correlational, but the
*removal preference* is not: offered the same shop removals, the sim binned
Kurage's Oath 213 times and Slack Water 7.

**(b) Chain Fuse / Explosives Workshop / Alice's Recipe — CONFIRMED, and the
Rare is the weaker card.** `ProtoBombPower.GrowthFor` computes `base +
workshop`: `base` is 4 with Alice's Recipe and 3 without, `workshop` adds 1 per
Workshop stack. One Workshop gives growth 4; one Alice's Recipe gives growth 4.
Same effect, same cost 1, same type, one Uncommon and one Rare — and the Rare
is strictly behind, because a second Workshop reaches 5 and a second Alice's
Recipe still reads 4. Chain Fuse buys the same 1 energy for a **one-off** +3
per Bomb on one enemy, so it leads either Power for three turns and trails it
forever after, at any Bomb count.

**(c) Fish-Flavored Bait as the auto-pick — CONFIRMED on paper.** 5 damage now
plus a Bomb 5 the free Ka-pow! cashes the same turn: **10 per energy** on the
turn it lands, 13 and 16 at the next two dawns. The rest of the 1-cost Common
slot — Pocket Fireworks 9, Sizzle 6 (12 conditional), Ammo Scavenging 4 plus
draws, Chain Fuse 3 per Bomb, Mine Toss 4, Sorry Jean Block only — trails it on
every column. Unconfirmable in the sim, which cannot run the arm.

## 5. What the instrument cannot see

The Klee arm never ran, so §2 covers no `proto_ko_` row — there is no Bomb rule
in this engine to misplay. On the Kokomi side the two rules deciding what the
numbers mean are the **sim's own, written nowhere on a sheet**:
`kokomi_plan.plan_aimed_at_pet` decides *when* to plan (when the now-line is
empty, or when no living enemy intends to attack this turn) and
`pilot/policy._active_effects` values a planned clause **at face, with no
discount for the turn of delay**. A player who plans on a different rule plays
a different arm. That covers all sixteen rows carrying a `plan:` list — the
seven Plan-only ones most of all, since they always plan by construction —
plus `change_of_plans` and `moons_reflection`, which act on the queue. The
drafter's blindness to `plan:` covers the same sixteen from the other end, so a
row reading dead here may be one the sim cannot price; three more (Rally, The
General's Banner, Chain of Command) read low only because the priest plan
drafts few Companions. Reproduce: `PYTHONPATH=. python -m
tools.prototype_card_read --arm kokomi --runs 1500 --seed 42 --acts 1`.
