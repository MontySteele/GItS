# Furina's Guest Stars: a priced package, 2026-10-13

Design review only; nothing here is built. Sources: the pool review on
`origin/furina-pool-review-2026-10-13` (sec.2 table), `FurinaStageBadges.cs`
(`ActText`), `FurinaStageLaw.cs`, `FurinaStageDirector.cs` (Drain, Repay,
act and Showstopper paths), `docs/prototype-surface.yaml` (Furina rows),
`review/records/furina-wave-2026-10-13.md`, `review/ruled/furina-review-2026-10-12.md`.

A guest costs 1 Energy, Exhausts, does nothing on summon, and acts at the end
of the same turn and every turn after (`EndOfTurn` calls `ActAll` first). Three
seats; a fourth summon pushes the oldest off after one last act. That is an
orb slot: the Defect's fourth channel evokes the oldest orb.

## 1. The yardstick

**Orb numbers, checked** (decompiled from `klee-mod/KleeTests/bin/Debug/sts2.dll`,
`MegaCrit.Sts2.Core.Models.Orbs.*`):

| Orb | Passive, each turn | Evoke |
|---|---|---|
| Lightning | 3 to a random enemy | 8 |
| Frost | 2 Block | 5 |
| Dark | stores 6 | 6 plus the store, to the lowest-HP enemy |
| Glass | 4 to ALL, 1 less each turn (4, 3, 2, 1, 0) | twice the current passive |
| Plasma | 1 Energy at turn start | 2 Energy |

Orb hits ignore Strength and Vulnerable (seat record `control2-lane3.md`,
fight 7); a guest's act takes no Strength either, so the comparison is clean.

**Channel cards, cost and rarity checked in `game_ref/defect.json`;** the
immediate effects are its `vars` where present, my recollection where marked:

| Card | Cost, rarity | Immediate | Orb |
|---|---|---|---|
| Zap | 1, Basic | nothing | Lightning |
| Ball Lightning | 1, Common | 7 damage | Lightning |
| Cold Snap | 1, Common | 6 damage | Frost |
| Coolheaded | 1, Common | draw 1 | Frost |
| Lightning Rod | 1, Common | 4 Block (plus its power, recollection) | Lightning |
| Glasswork | 1, Uncommon | 5 Block | Glass |
| Darkness | 1, Uncommon | nothing (upgrade triggers Dark passives, recollection) | Dark |
| Fusion | 1, Uncommon, Exhaust | nothing | Plasma |
| Chill | 0, Uncommon, Exhaust | nothing | Frost per enemy (recollection) |
| Glacier | 2, Uncommon | 6 Block | 2 Frost (recollection) |
| Rainbow | 2, Rare, Exhaust | nothing | Lightning, Frost, Dark |
| Defragment | 1, Rare Power | +1 Focus: every passive +1 | |

**What a fight pays.** Count a normal fight as 4 turns with 1.5 enemies, an
elite or boss as 8 turns with 1. A Lightning orb channelled on turn 1 pays
12 over a normal fight (20 with its evoke); Frost 8 Block (13); Glass 10 per
enemy, 15 at 1.5; Dark 24 if evoked on turn 4; Plasma 4 Energy, which StS
prices at about 25 damage-equivalent.

**The one Defect card that IS a Guest Star** is Fusion: 1 Energy, Exhaust,
nothing now, a persistent summon worth 6 to 7 a turn, at Uncommon. Chill and
Rainbow are the same shape at 0 and 2. So the bands, as damage-equivalent a
turn (1 Block = 1; 1 Repay = 1 HP plus 1 Fanfare; 1 Fanfare = 0.75, since
Rejoice pays 1 to ALL per point at 2 Energy, Bravura 2.3 per point, Hold the
Stage 1 Block per point, and 31% is never spent; 1 draw = 3; 1 Vulnerable on
one enemy = 3):

| Rarity | A turn | A normal fight (4 turns) | Anchor |
|---|---|---|---|
| Common | 5 to 6 | 20 to 24 | Ball Lightning: 7 now plus 12 to 20 from the orb; a guest with nothing now must earn the 7 across the fight |
| Uncommon | 7 to 9, or scaling that passes 9 by turn 3 | 28 to 36 | Fusion (Plasma, ~6.5 a turn), Glasswork (5 Block plus 15 to ALL), Darkness (24 by turn 4) |
| Rare | 10 to 13 alone, more with company | 40 to 52 | Rainbow (~50 for 2 Energy), Defragment (an engine: +3 to +5 a turn that grows with every orb) |

A Common should make the band on its own in any Furina deck. An Uncommon may
need one of her mechanics (Drain, Repay, Spend) to reach it. A Rare may need
company.

**Today against the bands** (the user's reading, now with numbers; typical
deck = Drain 4 a turn, Repay 3, one Spend, bank 18): Charlotte 3.5 (C, under),
Wriothesley 4 alone / 8 draining (C, under alone), Lynette 3 plus a bank of
8 to 10 Fanfare (U, invisible), Chevreuse 7 (U, under), Freminet 7.5 Block
(U, at band), Sigewinne 5 (U, under), Lyney 14 (U, far over), Navia 9 (U, at
band but eats the bank), Clorinde 8 alone / 16 repaying (R, under alone),
Neuvillette 20+ (R, over), Escoffier 6 to ALL plus Repay 3 = 9 plus 4.5 (R,
at the bottom). The user's quote holds: it is not a rarity ladder.

## 2. The package

Lines are passives while the guest is on stage; acts fire at the end of each
of her turns. Upgrades in brackets; each upgrade raises the line or the act,
never the cost (the pool-to-75 rule).

| Guest | R | Line | Act | Upgrade | Lore hook | A turn vs band |
|---|---|---|---|---|---|---|
| Charlotte | C | The first time each turn one of your cards Repays, draw 1 card. | Repay 3. Gain 1 Block for any HP it could not Repay. | act 5 | The Steambird's reporter: her Kamera burst heals the party and she keeps the story moving | 3 Repay or 3 Block, plus a draw on half her turns: **5.5 [7.5]**, band 5 to 6 |
| Wriothesley | C | Whenever you Drain, deal that much Cryo damage to a random enemy. | Deal 5 Cryo damage to a random enemy. | act 8 | Duke of Meropide: Chilling Penalty spends his own HP above half for harder punches | 5 alone, 9 draining 4: **5 to 9 [8 to 12]**, band 5 to 6 |
| Lynette | U | The first time each turn you lose HP to an enemy, gain that much Fanfare again. | Deal 5 Anemo damage to an enemy, one with an aura if able. | act 8 | Lyney's assistant: the Bogglecat Box taunts and absorbs the element it is hit with | 5 plus 8 to 10 Fanfare a turn (6 to 7): **11 [14]** in a Spend deck, 5 in none, band 7 to 9 |
| Chevreuse | U | Whenever you Spend, apply 1 Vulnerable to a random enemy. | Deal 5 damage to a random enemy. | line also 1 Weak | Captain of the Special Security and Surveillance Patrol: her cannon shreds resistances for the team | 5 plus 1 to 1.5 Vulnerable (3 to 4): **8 to 9 [11]**, band 7 to 9 |
| Freminet | U | Whenever you Drain, gain that much Block. | Gain 4 Block, then Spend a quarter of your Fanfare for that much more. | act 7 | The diver: Pers and the pressure suit hold the deep at bay | 4 plus 4 (bank 18) plus 4 draining: **8 to 12 Block [11 to 15]**, band 7 to 9 |
| Sigewinne | U | Whenever you Repay, gain that much Block. | Repay 3. Gain 1 Block for any HP it could not Repay. | act 5 | Head nurse of Meropide: Bolstering Bubblebalm heals whoever it bounces to | 3 Repay plus 3 Block from her own line, plus 3 on Repay cards: **6 to 9 [8 to 12]**; 3 Block floor, band 7 to 9 |
| Lyney | U | Your Drain buffer is 10 HP larger. | Drain 2, deal 3 Pyro damage to ALL enemies. It deals 1 more each turn he is on stage. | act 5 | The magician: Prop Arrows cost HP, Prop Surplus stacks, Bewildering Lights cashes them in | 3, 4, 5, 6 to ALL over a normal fight (4.5 x 1.5 = 7) plus 2 Fanfare: **8.5 [11.5]**; an 8-turn boss averages 6.5 [8.5] single, band 7 to 9 |
| Navia | U | Your first Spend each turn costs 2 less. | Spend a third of your Fanfare, rounded down: deal twice that much Geo damage to a random enemy. | line 3 less | President of the Spina di Rosula: the Rosula Dorata fires Crystal Shrapnel she has banked | bank 18: spends 6, deals 12 (net 7.5) plus 1.5 from the line: **9 [10]**, band 7 to 9; bank 36: 24 for 12 |
| Clorinde | R | Whenever you Repay, deal twice that much Electro damage to a random enemy. | Deal 6 Electro damage to a random enemy. | act 9 | Champion Duelist: she fights under a Bond of Life, an HP debt that pays out as damage when cleared | 6 plus 2 from Salon Solitaire's Repay 1: 8 alone; 14 to 18 repaying 3 to 5: **8 to 18 [11 to 21]**, band 10 to 13 with company |
| Neuvillette | R | Your Hydro damage deals 2 more. | Deal Hydro damage to ALL enemies equal to the HP you lost since your last turn. | line 3 | The Iudex: Equitable Judgment drains his own HP while the beam runs; the verdict lands on everyone | line: +2 per hit, ~3 Hydro hits a turn = 6 (Bravura at 36 Fanfare is 12 hits: +24); act: 10 to 14 lost x 1.5 = 15 to 20: **21 to 26 [24 to 29]**, over band |
| Escoffier | R | Your guests' acts deal 2 more damage. | Deal 4 Cryo damage to ALL enemies. | line 3, act 6 | Fontaine's chef: she cooks for the whole company, and her dishes cut the enemy's resistance to every element the party brings | her own act 6 [9] to ALL = 9 [13.5] alone; +2 on two more damaging guests at 1.5 enemies = +5 to +7: **14 to 16 [19 to 22]**, band 10 to 13 with company |

Rarities unchanged: 2 Common, 6 Uncommon, 3 Rare. A line on star ratings is
in sec.6.

## 3. Changes from today, one line each

- **Charlotte, act 2 [4] to 3 [5].** Skipped 8 of 10: at 2 she is a Frost orb
  that needs drained HP; at 3 she is a Frost orb plus one, with the draw on
  top, and she now sits in the Common band.
- **Wriothesley, act 4 [7] to 5 [8].** Alone he was a Lightning orb plus one;
  the Common band is Ball Lightning's 7 spread over the fight. His line is the
  Drain-offence hook and is unchanged.
- **Lynette, act 3 [6] to 5 [8]; line reworded** ("gain that much Fanfare
  again" says what "double Fanfare" does). Passed 4 of 4 because 3 reads
  small; her line is already a bank engine (sec.5).
- **Chevreuse, act 4 to 5.** She was a Lightning orb plus a conditional
  debuff; 5 plus Vulnerable on every Spend is the Uncommon band.
- **Freminet, act 3 [6] to 4 [7].** One more Block a turn; he is the kit's
  one repeatable Block source and the pool's Block is the smallest of any
  character (41 printed). The quarter-Fanfare rider stays: it is an Uncommon,
  not the Common the 2026-10-12 ruling closed.
- **Sigewinne, act 2 [4] to 3 [5].** Her act feeds her own line, so every
  point is worth two; at 3 she makes the band in a Repay deck and never prints
  less than 3 Block.
- **Lyney, act 8 [11] to ALL becomes 3 [5] to ALL, growing by 1 each turn he
  is on stage.** The user: "clearly extremely strong" (64 to two enemies over
  four turns today; 36 [52] with this). He becomes the company's Dark orb:
  weak the turn he lands, the best act in the cast by turn 4, and pushing him
  off the stage costs something. Drain 2 and the buffer line stay.
- **Navia, act "Spend half, deal that much" becomes "Spend a third, deal
  twice that much."** A ratio, not a cap (ruled 2026-10-10). Today she pays 1
  damage per Fanfare, the floor rate of every Spend card, and empties half
  the bank a turn; now 2 per point from a third of it, so the prima-donna
  keeps her finale.
- **Clorinde, no number change.** Her line is the Repay payoff and already
  Rare-sized with company; the 2026-10-12 review's +2 is not needed once
  Charlotte and Sigewinne Repay 3.
- **Neuvillette, no number change.** The line reads low but is paid per hit:
  Bravura is `WithHitCount(spent / 3)` separate hits
  (`ProtoFsBravura.cs`), Crashing Waves 2 to 6 hits, four of her Hydro cards
  hit ALL. +2 is +6 on an ordinary turn and +24 on a Bravura turn; his act is
  already the biggest in the cast. Alternative in sec.6.
- **Escoffier, line "Whenever a guest acts, Repay 1" becomes "Your guests'
  acts deal 2 [3] more damage"; act 4 [6] to ALL unchanged but reads 6 [9]
  through her own line.** The user: "still looks a bit underpowered", and the
  Repay line is dead with nothing drained (the Fountain of Lucine problem).
  This is Defragment for the stage: a Rare that makes the other guests worth
  seating, which is what the guest style lacks.

## 4. Loops and snowballs

Repay is bounded by HP drained this combat (`Repay` returns 0 when
`RepayRoom` is 0), Drain by her HP and the buffer, Spend by the bank. Nothing
in the package makes a resource from itself. The chains to watch:

1. **Escoffier's +2 with the act-repeaters.** Tutti! (Common, 1: each guest
   acts, draw 1) with three boosted guests is 20 to 30 damage for 1 Energy;
   Showstopper (Rare Power, Spend 5 a turn) doubles every act. That is the
   intended payoff (the 2026-10-12 review: "the Rare payoffs then have
   something to multiply"), paid for by three summons, 3 Energy and three
   exhausted cards. Closed by the seat count: three acts a turn, four with
   Ensemble Cast, and Showstopper costs 5 Fanfare a turn.
2. **Lyney's growth with the act-repeaters.** Written as "each turn he is on
   stage", not "each time he acts", so Showstopper, Tutti!, Encore! and Final
   Bow double his act but do not accelerate it. (Act-counted, Showstopper
   would take him to 18 to ALL by turn 8; turn-counted he is 10 [12].)
3. **Escoffier's old Repay-per-act line with Clorinde.** Gone with the line.
   The remaining Repay engine is Charlotte 3 + Sigewinne 3 + Salon Solitaire 1
   = 7 Repay a turn = 14 Electro from Clorinde, 7 Block from Sigewinne, 7
   Fanfare, and it needs 7 HP drained every turn to run: a Drain deck's whole
   budget. Self-limiting, and the one deck where Lyney's Drain 2 a turn is a
   gift.
4. **Neuvillette's act with self-Drain.** The Deluge (Drain 8) is +8 to ALL
   at his act; All In, Regina, Lyney's Drain 2 likewise. Showstopper re-reads
   the same window (`HpLostSinceLastTurn` closes at `CloseTurn`), so his act
   lands twice. Bounded by HP: every point he converts was lost first. This is
   the "swings her HP violently and gets rewarded" line, and it is the number
   to read in the next round, not to pre-cut.
5. **Navia's Spend with the Spend readers.** Her act is a Spend, so Thunderous
   Applause (3 to ALL), Chevreuse (1 Vulnerable) and Full House answer it
   every turn. A third of the bank converges (18, 12, 8, ...), so it cannot
   run away; the readers fire once per act.
6. **Lynette and Freminet.** Her line wants HP lost to enemies, his Block
   stops it. Anti-synergy, no loop.
7. **Encore! on Escoffier.** 0-cost "oldest guest acts" on her is 6 [9] to ALL
   for nothing; Final Bow on her is 18 [27] to ALL and loses her. Both need a
   Rare on stage and the seat order to line up; the same as evoking a full
   Dark orb.

## 5. The two decks

**The stars are the offence.** Three guests on stage by turn 3: Wriothesley
(5 plus his Drain line), Lyney (3 growing) and Escoffier (6 to ALL and +2 on
the others) deal 7 + 7 + 9 = 23 a turn at 1.5 enemies on turn 1, 30 by turn
4, for three exhausted cards; her own hand then plays the multipliers:
Tutti!, Encore!, Final Bow, Showstopper, Bring the House Down, Full House,
and the counters Headliner, Leading Lady, Private Box. Drain cards feed
Wriothesley and Lyney's buffer; Casting Call and Ensemble Cast find the third
seat. Clorinde with Charlotte and Sigewinne is the second build (the Repay
trio, sec.4 item 3): 14 Electro and 7 Block a turn off 7 drained HP. Base
damage a turn is 19.5 / 30 / 49 by act (the 2026-10-12 review); the three-guest
stage alone makes act 2's number from turn 1 of the fight, which is what
"main offence" has to mean.

**The prima donna** still takes four guests as support: Lynette (the bank
doubles the first hit each turn), Navia (the first Spend costs 2 less and a
third of the bank becomes 2-for-1 damage), Chevreuse (Vulnerable on every
Spend), Freminet (Block plus a quarter of the bank, the one repeatable Block
in the pool). Neuvillette sits in both: +2 on every Bravura hit for her, the
ALL act for the stage.

## 6. For the user

1. **Escoffier's line.** (a) Default: "Your guests' acts deal 2 [3] more
   damage." (b) Keep the Repay shape at Rare size: "Whenever a guest acts,
   Repay 2 [3]", dead with nothing drained but 6 Repay a turn with three
   guests, 12 under Showstopper, and 12 to 24 Electro with Clorinde.
2. **Neuvillette's line.** (a) Default: 2 [3], per hit. (b) 3 [4]: +36 on a
   12-hit Bravura. (c) If Hydro damage does not already apply a Hydro aura in
   the element engine, "Your Hydro damage deals 2 more and applies Hydro"
   would hand Lynette her aura target and Escoffier her Freeze; I could not
   confirm the aura rule from the files read and did not price it.
3. **Lyney's shape.** (a) Default: 3 [5] to ALL growing 1 a turn. (b) The
   branch's flat 5 [7] to ALL (20 [28] to each enemy over four turns against
   18 [26]; the same on a boss by turn 8, 40 against 52).
4. **Rarity by star rating.** Genshin's 4-stars are Charlotte, Lynette,
   Chevreuse, Freminet; the rest are 5-stars. Wriothesley (5-star) is the
   Common damage star by the diversity-pass ruling and Lynette (4-star) the
   Uncommon passed 4 of 4. Default: leave both; the numbers above fix the
   take rate. Option: swap them (Lynette Common at act 4 [6], Wriothesley
   Uncommon at act 6 [9]).
5. **Clorinde's target.** "The enemy with the most HP" instead of random
   would make the duelist read as one and steady the Repay deck's damage; no
   number change, a small target-rule addition in `StageTarget`. Default: no.
6. **Chevreuse's act has no upgrade number** today (the upgrade is her Weak).
   Kept that way here; say if every guest should upgrade on the act.

After a build, the five-seat round reads: the guests' share of damage, how
many stages reach three seats by act 2, and Neuvillette's act size at elites.
