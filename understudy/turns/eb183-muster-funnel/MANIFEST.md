# EB-183 — the map from turn id to arm

**R213 E1; R216 D.** Two turns in ONE matched pair — the **fifth** pair of a
question Kokomi slice 2's four could not finish asking. The ids are opaque on
purpose: they are printed into the design-blind packet a grader reads, so
nothing in one may say which arm it belongs to. This file is the map, and it is
not shown to a grader.

**NOTHING IS STAGED.** Both files read no `seed:` and the table below says
`pending`. Staging needs the live game and a dev build carrying the prototype
row; this work was done in a sibling worktree, which by house rule may not
launch the game, install the bridge or deploy. What exists today is the
DECLARED board and its closeness reading, which need no game.

**The seed rule.** Within a pair, the first half staged rolls a seed and
`stage` records it; the other half must then be staged with `--seed <that
value>`. Two halves on two seeds are two different fights, and the pair has
measured the encounter instead of the card. If the seed's fight telegraphs
anything but an attack, re-roll — the intent is the question here.

## The map

| turn | file | card under test | seed | staged |
|---|---|---|---|---|
| `kokomi-eb183-t09` | `subsidy-shipped.yaml` | `mass_mobilization` (shipped) | — | pending |
| `kokomi-eb183-t10` | `subsidy-prototype.yaml` | `proto_muster_subsidy_funnel` | — | pending |

The numbering continues slice 2's `t01`–`t08` deliberately: this is that
question's fifth pair, not a new slice.

## What the pair asks

R216 D deferred Muster's Charge subsidy into R213 E1 in these words: *a
Mustered Companion costs 1 less, Exhausts, and pays 1 Charge, so blocking with
one also advances Kokomi's finisher*. Two readings live in that sentence.

Slice 2 asked the first — the subsidy's **sign**, put on a card, the order
SPENDING Charge instead of paying it. Those four arms **retired** under R227 /
M67 (1), which retired every arm that priced Charge on a card; the spend
plumbing stayed.

This pair asks the second, and no effect list can express it: *the recruits of
an order that paid for them pay no Charge when they Exhaust.* That is a
property of the exhaust **funnel** — a flag on the recruit and a check where
the wage is paid — which is why it is a fifth pair and not a fifth card row on
slice 2's sheet.

|  | shipped half (`t09`) | prototype half (`t10`) |
|---|---|---|
| card | `mass_mobilization` — *Rally the Isles* | `proto_muster_subsidy_funnel` — *Bounty of the Isles* |
| cost / type / rarity | 2, Skill, Uncommon | 2, Skill, Uncommon |
| Muster count | 2 | 2 |
| the Charge line | the order pays 1 Charge, and each recruit pays another when it rotates out | the order pays nothing, and the units it musters pay no Charge when they Exhaust |

**This is not a retired arm.** The prototype half prints no Charge PRICE and
reads the bank at no point, so R226's signed Charge LAW — *no card prints a
Charge price, no card reads the bank proportionally* — is untouched. What moves
is an accrual the order already paid for.

## The board, and the one deviation from slice 2's four

Both halves: player 48/70, no Block, turn 3, **four energy**, a Charge bank of
8, one enemy telegraphing an attack, `exact_hand: true`.

**Four energy, where slice 2's arm 4 took three, and the reason is the arm.**
Arm 4's difference landed AT the order, so three energy reached it. This pair's
difference lands one play LATER — on a recruit's rotation — so the turn must
afford the order AND a recruit's play. A recruit costs its printed cost less
one, which the Inazuma pool puts at anything up to two, so at three energy
whether the arm was askable at all would have depended on the game's roll.

**The bank is 8, unmoved from slice 2's three pairs.** Nothing here spends
Charge, so the bank's only job is to keep the shipped readers live on both
halves; 8 is what they were read at there and moving it would make this pair
incomparable to the four it continues.

**Coral Guard, and only Coral Guard.** The one standalone Block, in hand on
both halves, because a Charge payoff that nothing competes with is not a
decision. A second flat-Block card would make "defend" the answer by arithmetic
rather than by choice. Pair 1 and pair 3 of slice 2 carried Water's Edge and
All Streams Flow beside it for the same reason, and so does this one.

### The arithmetic that says no line is lethal

Kokomi has no Strength on this board and the enemy carries no aura, so every
number below is the printed number. All Streams Flow to the Sea reads
`5 + charge // 2`.

| turn | energy | Charge | enemy HP | largest damage the board can produce | headroom |
|---|---|---|---|---|---|
| `t09` | 4 | 8 | 37 | Water's Edge (**6**) + All Streams Flow at 8 Charge (**9**) = **15**; or the order plus one recruit, and the largest single Inazuma Companion hit is **14** | 22 |
| `t10` | 4 | 8 | 37 | the same **15**; or the order plus one recruit at **14** | 22 |

The recruit's identity is the game's roll, so the "largest single hit" column
is the pool's ceiling rather than a number this file can write. **37 HP is the
body slice 2's arm 4 settled on after ten rolls** and it is what this pair
declares; `set_hp` clamps at a creature's maximum, and in those ten rolls the
only single Act-1 body reaching 46 telegraphed 4 damage, against which the
defensive half of the question is not asked at all.

## Closeness (`staged_turn closeness`, 2026-08-30, DECLARED boards)

| turn | gap | top1 / top2 | lines |
|---|---|---|---|
| `t09` | 0.2850 | 20.700 / 14.800 | 14 |
| `t10` | 0.2850 | 20.700 / 14.800 | 14 |

**Both SURVIVE** against a dominance threshold of 0.5. Read this as a refusal
that did not fire, and nothing else (R213 F).

**The two halves read IDENTICALLY, and neither top line contains the card under
test.** That is not a surprise and it is not a defect in this pair — it is the
same disclosure slice 2 made about its arm 4, one step worse. The pilot values
a Muster order by what it puts in hand, not by what the recruits do a turn
later, and this arm's whole difference is what a recruit's rotation PAYS a turn
later. So the instrument cannot separate these halves, and **the blind seat is
the only reading this pair has.** If the seat cannot separate them either, that
is itself the arm's answer.

The second standing disclosure applies unchanged: the pilot has no Charge
hold-versus-spend term, so on these boards Charge income looks free. Here the
error direction is if anything the reverse of slice 2's — the prototype half
*loses* income the pilot is not pricing — and in both directions the falsifier
is only being asked to refuse, which it did not do.
