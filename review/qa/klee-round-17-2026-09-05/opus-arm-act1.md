# Klee — blind seat, round 17 (targeted), lane 1

## Identity

- **Model / seat:** Claude Opus (Fable-family), blind TESTER seat, lane 1, `KLEEMOD-KLEE`.
- **Run seed:** `P7B233U14YC5`. **Ascension:** 0. **Act:** 1. **Boss named on the map:** Waterfall Giant (never reached — I stopped 6 floors short).
- **Actions accepted:** 117 of 120.
- **Termination:** action budget. At 117 I was standing in the shop on the floor after the elite with 3 acts left — not enough to open and play a fight, so I stopped rather than start one I could not finish. Wall clock was nowhere near 5400 s.
- **HP trajectory:** 62 → 56 (fight 1) → 54 (fight 1 end) → 46 (event, −8) → 40 (fights 2–3) → 29 (fight 3 end) → **47** (rest, +18) → 40 (fight 5 t1) → 32 (elite t1) → 25 (elite t2) → **22/62** at stop.
- **Gold:** 110 (peaked at 290 before the shop; Bowler Hat was doing work all act).
- **Potions held at stop:** Stable Serum, Fire Potion. (Spent: Potion of Binding and Explosive Ampoule, both into the Sewer Clam.)
- **Relics:** Pounding Surprise (start), Large Capsule, Bowler Hat, Red Mask (all three from Neow), Tiny Mailbox (chest), Anchor (elite).
- **Deck at stop (25):** Bang Bang!, Defend ×5, Dig In, Fish Blasting, Fish-Flavored Bait, Grounded, Jumpy Dumpty, Ka-pow!, Kaeya — Cold-Blooded Strike, Long Fuse, Mine Toss ×3, Pocket Fireworks, Shinobu — Thundergrust, Sparks 'n' Splash, Stoke the Fuse, Strike ×5, The Big One.

**Neow pick: Large Capsule** ("Obtain 2 random Relics. Add an additional Strike and Defend to your Deck"). I took it because two relics is the biggest single swing on offer and the other two options were conditional (Booming Conch only pays in Elites; Fishing Rod pays once every three fights). I knew the round had pre-loaded five extra cards, so I was knowingly making a 17-card starting deck — the dilution turned out to matter, and I say where below.

**The five targeted cards — verdict up front.** I played all five at least once. Grounded and Fish Blasting were good immediately. Long Fuse was good but never a decision (see below). **Sparks 'n' Splash and Stoke the Fuse were dead cards in hand five times between them across the first four fights**, because the deck they arrived in has almost no Bomb source. That is the single loudest thing this round told me.

---

## Fight 1 — Corpse Slug (26 HP) + Corpse Slug (27 HP)

Both wore `Ravenous 4 — When an enemy dies, Corpse Slug immediately eats it, becoming Stunned and gaining 4 Strength`, and Red Mask had already stapled Weak 1 on both.

**Turn 1** (hand: Strike ×3, Defend, Stoke the Fuse). Played Strike ×3 into Slug (1). **Rejected:** Defend + 2 Strikes — incoming was 6 weakened to ~4 and I was at full HP, so racing beat blocking. **Also rejected, and this is the finding:** Stoke the Fuse. It reads `Spend all your Sparks. Your largest Bomb grows by 3 per Spark spent`. I had 1 Spark and **no Bomb**, and nothing in my opening hand could make one. It was a blank card on turn 1 of the run.

**Turn 2.** Drew Fish Blasting, Sparks 'n' Splash, Grounded. Slug (1) at 8. Played **Strike → Fish Blasting → Grounded**: Strike took it to 2, Fish Blasting (`Deal 5 damage to ALL enemies. Add a Confiscated to your draw pile`) killed it *and* put 5 into the survivor. **The real decision was whether to kill Slug (1) at all** — Ravenous means the survivor eats the corpse for +4 Strength permanently, in exchange for a Stun. I took the trade because the survivor was going to live 2–3 more turns either way and a skipped turn was worth more than 4 Strength over that span. **Rejected:** holding both slugs low and killing them together, which would have cost me two extra turns of a debuffer sitting there. Also rejected: Sparks 'n' Splash (2 energy, `deal Pyro damage to a random enemy equal to its largest Bomb`) — again, no Bomb, so it reads as "deal 0". Second dead card of the fight.

Grounded went down instead, and it paid: next screen showed `Block 6` and `Spark 2`, i.e. 6 Block *not* reduced by my Frail 2, because Grounded is a Power and Frail says "less Block **from cards**". That is consistent, but it is a distinction the player has to work out.

**Turn 3.** The Stun resolved silently and correctly — the survivor showed `Strength 4` and no Stun marker, and I took 0 damage between rounds. I briefly thought the screen had eaten the Stun; it had not, the stunned turn simply happened between my screens. Worth knowing that a Stun is only ever visible as damage you did not take. Played Ka-pow! (0 cost) → Long Fuse → Defend ×2. **Rejected:** holding Long Fuse. It prints `Costs 1 more each turn it stays in your hand`, which makes "hold the Retain card" a trap, so Retain on Long Fuse is close to decorative.

**Turn 4.** Slug at 12, two Strikes for exactly 12. **Rejected:** Jumpy Dumpty + Stoke the Fuse to finally see the Bomb loop — I would have been paying HP for a tutorial when lethal was on the table.

**Verdict on the fight:** two real decisions (the Ravenous trade, and Grounded over Defend), both made on the turn. Two dead cards.

## Fight 2 — Sludge Spinner (37 HP)

**Turn 1.** Ka-pow! (free) + Strike ×2 + Long Fuse = 22. **Rejected:** holding Ka-pow! and Long Fuse unplayed so their `Set off` would matter once a Bomb existed. I rejected it because there was no Bomb source in hand and Long Fuse gets more expensive every turn it waits. This is the shape of the problem — the kit's Set-off cards are strictly worse Strikes until a Bomb exists.

**Turn 2.** This is the first turn of the run that felt like Klee. Screen printed on Shinobu: `*Reaction preview: Overloaded* — Pyro meets Electro: 6 damage to ALL enemies and 1 Weak on the reacted enemy`, because Fish Blasting/Long Fuse had left `Pyro Aura 1` on the Spinner. Played **Shinobu → Strike**. Spinner went 15 → 3 on Shinobu alone: 6 (base 8, cut to 6 by the Weak I was wearing — the card face recomputes for Weak, which is excellent) plus 6 Overloaded. Strike finished it. **Rejected:** Grounded, because the fight was ending.

**The decision here was made at the draft, not on the turn** — Shinobu was the card reward I picked one floor earlier specifically because it was the only second element on offer. That pick is what made turn 2 a 12-damage turn instead of a 6.

## Fight 3 — Seapunk (45 HP)

**Turn 1.** Ka-pow! + Strike ×2 + Defend. No decision worth the name; the hand had one line.

**Turn 2.** Drew **Jumpy Dumpty** (`Place a Bomb 8. When it goes off, place a Mine 3 on ALL enemies`) and **Sparks 'n' Splash** together for the first time. Played both (1 + 2 energy), taking 8 to the face rather than blocking. Bomb 8 landed and printed clearly: `Bomb 8 (buff) — Set off here deals 8 Pyro damage. Bombs here: 8, growing each turn. None goes off by itself.` End of turn, Sparks 'n' Splash dealt 8. **Rejected:** Defend ×2 + Strike (10 block, 6 damage) — against a 45 HP enemy the escalating engine out-scales flat blocking, and I had 37 HP of runway to pay for it.

**Turn 3.** Bomb had grown 8 → 12; Sparks 'n' Splash had already taken the Seapunk to 21. Played **Long Fuse** (`Retain. Set off. Deal 6 damage`) → set off the 12, then hit for 6, 21 → 3; Jumpy Dumpty's rider fired and put `Mine 3` on the board exactly as printed. Strike finished it. **Rejected:** letting the Bomb keep growing while Sparks 'n' Splash ticked — the Seapunk was telegraphing `Defensive (Defend)`, and a growing Bomb into a growing Block pile is a losing race.

**This fight is the kit working.** The lethal on turn 3 was obvious, but it was obvious *because* of the two cards I spent turn 2 on. That is a plan paying off, not a dead turn.

## Fight 4 — Two-Tailed Rat ×3 (19, 20, 18 HP)

The best turn of the round, and the only one where I had to think about ordering.

**Turn 1.** Ka-pow! (0) into Rat (1) to lay a Pyro aura and chip 4. Then **Shinobu into the same rat**: 13 damage (I was at 29/62, under half, so the `If you are below half HP, deal 5 additional damage` clause fired — note the card face printed "Deal 8 damage" and did *not* preview the +5, unlike the Weak recomputation) plus Overloaded's 6 to ALL. Rat (1) died; the other two went 20 → 14 and 18 → 12 for free. Then **Jumpy Dumpty on the next rat (Bomb 8) → Long Fuse on the same rat**, which set off the 8 and hit for 6 — exactly 14 into a 14 HP rat. It died, and Jumpy Dumpty's `Mine 3 on ALL enemies` rider landed on the survivor.

**Rejected:** Defend, and spreading the damage. Two rats dead on turn 1 was worth more than any amount of block.

**Turn 2.** The last rat showed `Mine 14 — Bombs here: 7 / 7, including 2 Mines`. Two Mines, because the rat I killed was carrying one and `A kill moves them to a survivor` moved it across. The rat had 12 HP and intended to attack for 8. **I played nothing and ended the turn**, on the printed promise that `A Mine also goes off before this enemy's hit, which lands in full unless the Mine kills`. It killed. I took zero damage and won the fight without spending a card.

That is the single most satisfying thing that happened all round, and it was a genuine decision (spend 2 energy on Strikes for a guaranteed kill, or trust the printed text and bank the energy). The screen and the outcome agreed perfectly.

## Fight 5 — Sewer Clam (56 HP, Block 8, `Plating 8`)

A block wall: `At the end of your turn, gain 8 Block. Plating is reduced by 1 at the start of your turn.`

**Turn 1.** I had all three of my elements in hand (Ka-pow! Pyro, Shinobu Electro, Kaeya Cryo) and the glossary now listed Melt (1.75×), Overloaded (6 AoE + Weak) and **Superconduct** (`The reacted enemy gains 2 Vulnerable, which applies before this hit`). Against one high-block target I picked Superconduct over Melt: **Kaeya first** (8 damage, leaves Cryo), **then Shinobu** (Electro on Cryo → 2 Vulnerable applied *before* the hit, so 8 became 12), then Ka-pow! into the stripped block, then Grounded. Clam went 56 → 44 through 8 Block on the first two cards alone, which is 20 gross — the maths matched the text to the point.

**Rejected:** the Melt line (Ka-pow! → Kaeya = 8 × 1.75 = 14). Same turn-one damage, but Superconduct leaves 2 Vulnerable on the body and Melt leaves nothing. This was the best decision I made all round and it was entirely readable off the screen.

**Turn 2.** Clam back to Block 8, Vulnerable 1 still live. Played Strike + Fish Blasting to spend the Vulnerable window. **Rejected:** Sparks 'n' Splash — third time it was dead in hand, no Bomb anywhere. **Also rejected:** Defend, because the Clam's intent was `Empower (Buff)`, so block would have expired unused.

**Turn 3.** Clam at 30 with 7 Block and `Strength 4`, telegraphing 14. I burned both potions: **Potion of Binding** (Weak 1 + Vulnerable 1 to all) then **Explosive Ampoule** (10 to all) then Strike ×3, which at ×1.5 was exactly 27 into 27 HP. Dead in one turn.

**Where the screen and the outcome disagreed.** The Explosive Ampoule dealt **10, not 15**, into a Vulnerable target (30 → 27 through 7 Block). Two different definitions of Vulnerable were on that same screen: the glossary said *"takes 50% more damage from every hit it takes, a Skill's damage too"*, and the power on the enemy said *"Receive 50% more damage from **Attacks**"*. The outcome matched the narrower one. One of those two lines is wrong, and I had to spend a potion to find out which.

**Smaller disagreement:** `Plating is reduced by 1 at the start of your turn`, but Plating read 8 in round 1, 8 in round 2, and only 7 in round 3. I am not certain enough of the round boundaries to call it a defect, but it did not tick the way I read it.

## Fight 6 (Elite) — Phantasmal Gardener ×4 (31, 27, 28, 29 HP)

Every one carried `Skittish 6 — The first time Phantasmal Gardener is hit each turn, it gains 6 Block`. 115 HP behind 24 Block a turn.

**Turn 1, first act, spent deliberately on a question:** I played Ka-pow! (free, 4 damage) into Gardener (1) purely to learn whether Skittish's Block lands before or after the hit. Answer: after — `HP 27/31, Block 6`. Cheap, and it changed the whole turn.

Then the line: **Mine Toss** (`Place a Mine 4 on ALL enemies`), **Shinobu into Gardener (1)** — the one already wearing Ka-pow!'s Pyro aura — for Overloaded, and **Long Fuse into the same Gardener**.

Three things came out of that which the kit should be proud of:

1. Overloaded's 6-to-ALL went into the other three gardeners and **none of them gained Skittish Block**. Reaction damage is not a "hit" for a when-hit power. That is the same rule `Set off` prints (`no when-hit power fires`) and it is the designed answer to this elite.
2. Long Fuse into a target that had *already* been hit this turn set off its Mine 4 and then hit for 6, and Skittish gave nothing, because "first time each turn" was already spent. Gardener (1) went 19 → 9 in one card.
3. Consequently **hitting a gardener protects it from its own Mine** (the 6 Block eats the Mine 4), so the correct play against three of the four was to *not* attack them. A kit that makes "do nothing to that enemy" the right answer, legibly, is doing something interesting.

**Turn 2 — where I misplayed, and why.** I played Pocket Fireworks to kill Gardener (1) exactly, and then aimed **Kaeya at "Phantasmal Gardener (2)"**. The list had *already renumbered* the moment the first one died, so my Kaeya hit what had been Gardener (3), not the one I meant. I only found out by reading max-HP values off the next screen (`4/28` where I expected `3/27`). The page does warn about this for cards in hand — *"it is re-counted on every screen"* — but it prints that warning under **Your hand**, not under **The other side**, and there is no way to name an enemy that survives a kill inside the same turn. This is a real usability defect in the bridge, not in the kit, but it cost me a targeted 14-damage Melt.

Then **Mine Toss** and **Stoke the Fuse**. Stoke finally had a target: 6 Sparks (4 banked, +2 from Kaeya — companions pay `1 Spark, 1 more if it triggered an Elemental Reaction`) × 3 = **+18 onto the largest Bomb**, which took the far gardener's Mine from 8 to 26 and printed `Mine 30 — Bombs here: 26 / 4`. Exactly as advertised, no rounding surprises.

**Turn 3.** Three of the four gardeners died on their own turn, killed by Mines going off before their hits. I went from four enemies to one, having spent one turn's energy. **Rejected:** attacking the survivor — it had 13 HP and a Mine 8, and hitting it would have handed it 6 Block that would have eaten most of that Mine. So I ended the turn again, took 3, and it went to 5 HP for free.

**Turn 4.** One Strike. Elite down. I finished the fight at 22/62 having taken 18 damage from a four-body elite.

**This fight is the strongest argument for the kit in the whole round,** and every decision in it was a real one: the Ka-pow! probe, Superconduct-vs-Melt-vs-Overloaded target selection, the counterintuitive "don't attack" turns, and the Stoke the Fuse timing.

---

## Offers

**Every companion card I was offered, and what I did:**

| Where | Companion | Took it? | Why |
|---|---|---|---|
| Fight 1 reward | **Shinobu — Thundergrust** [Electro] | **Yes** | Only second element on the screen; my whole deck was mono-Pyro and no reaction was reachable. It paid off two fights later and again in the elite. |
| Fight 2 reward | Dahlia — Sacramental Shower [Hydro] | No | Took Mine Toss instead — I needed a Bomb *source*, not a third element. |
| Fight 3 reward | **Kaeya — Cold-Blooded Strike** [Cryo] | **Yes** | 8 for 1 beat my Strikes, added a third element (Superconduct/Melt), makes Sparks, and its clause `This turn, Grounded counts nothing as having gone off` is the only card I saw that repairs the kit's own anti-synergy. |
| Fight 4 reward | Dahlia — Sacramental Shower [Hydro] | No | Same reason; took Bang Bang! |
| Fight 5 reward | Amber — Explosive Puppet [Pyro AoE retaliate] | No | Took a second Mine Toss. |
| Elite reward | Charlotte — First-Person Shutter (4+4 Block) | No | Tempting at 22/62, but a third Mine Toss is defence too — Mines kill attackers before they swing. |
| Shop shelf | Kaeya — Glacial Waltz (78g), Kaedehara Kazuha — Kazuha Slash (74g) | No | Bought The Big One, Dig In and a Fire Potion instead. |

**Reaction cards I passed for want of a second element:** none, strictly — after fight 1 I always had at least two elements in the deck. The nearest case is **Dahlia (Hydro), passed twice**: I had Pyro and Electro, so Hydro would have been reachable, but no screen ever told me what Pyro+Hydro (Vaporize) does, because the glossary only defines a reaction *"on the first screen that reaches a second element"* — and I never held Hydro. So I was passing a card whose payoff was, by design, unreadable at the moment of the pick. That is worth flagging: **the reaction glossary is reactive, so a reaction card in a card-reward screen is priced blind.**

---

## The kit, after 6 fights

**(a) Which decisions felt like real choices, and what they traded off.**

- **Reaction target-and-order selection — on the turn, and the best thing in the kit.** Fight 5 turn 1 was a three-way read: Melt (1.75× on one hit), Overloaded (6 to all + Weak), Superconduct (2 Vulnerable *before* the hit). Against one big blocker I picked Superconduct because the Vulnerable persists; against three rats I picked Overloaded because the 6 spills. Same three cards, opposite answers, decided by what was on the board. That is a real decision and the screen gave me everything I needed to make it.
- **"Don't hit that enemy" — on the turn, elite fights 4 and 6.** Because Mines detonate before the enemy's swing and do not trigger when-hit powers, but Block *does* stop them, attacking a Skittish enemy actively protects it. I ended two turns having played nothing and it was correct both times. I have not seen another deckbuilder make "pass" the strong play this legibly.
- **The Bomb plant, two turns early — earlier in the fight.** Jumpy Dumpty + Sparks 'n' Splash in fight 3 was a turn of near-zero tempo that made the next two turns lethal. The turn-3 kill looked automatic; it was the plan cashing out.
- **The draft pick that shaped a fight — at the draft.** Shinobu made fight 2's turn 2. Mine Toss made the elite. Neither fight had much on-turn choice; both had a choice, made one floor earlier.
- **Stoke the Fuse timing — on the turn.** Spend 6 Sparks for +18 now, or bank for a bigger multiplier later, against a board that might kill the carrier first. Genuinely tense once a Bomb exists.

**(b) What felt automatic, and what never seemed worth playing.**

- **Long Fuse is never a decision.** It has Retain, but it also has `Costs 1 more each turn it stays in your hand`, so the answer is always "play it now". The Retain is a lie told by the card frame. Ka-pow! has the same problem in reverse — at 0 cost it is always correct to play, never a choice.
- **Strike and Defend turns.** Fights 1 and 3 turn 1, and fight 5 turn 2, had exactly one line. That is a 17-card starting deck's fault as much as the kit's, and Large Capsule was my choice.
- **Sparks 'n' Splash and Stoke the Fuse were not worth playing for four fights.** Both are pure payoff cards that read as "deal 0" and "grow nothing" until a Bomb exists, and the deck I was handed contained exactly **one** Bomb source (Jumpy Dumpty) among 17 cards. Stoke the Fuse sat dead in hand in fights 1, 3 and 4; Sparks 'n' Splash sat dead in fights 1 and 5. **The kit's identity card is a blank three fights out of six.** Once I had drafted two Mine Tosses and Bang Bang! the problem vanished entirely, which tells me it is a deck-composition defect and not a card defect — but a targeted round that adds Stoke the Fuse and Sparks 'n' Splash to a deck with one Bomb source is testing them in the state where they are worst.
- **Confiscated** did what it said (nothing) and did not persist between fights, which is the right call.

**(c) What I could not understand, or that contradicted its own printed text.**

1. **Vulnerable has two contradictory definitions on the same screen.** Glossary: *"takes 50% more damage from every hit it takes, a Skill's damage too."* The power on the body: *"Receive 50% more damage from **Attacks**."* Explosive Ampoule (10 damage to all) dealt **10, not 15**, into a Vulnerable Sewer Clam. The narrower text is the true one; the glossary is wrong or at least misleading, and I paid a potion to learn it.
2. **Shinobu's face does not preview its own conditional.** It printed `Deal 8 damage` while I was at 29/62, and then dealt 13. The same page *does* recompute the base number for Weak (Strike showed 4 instead of 6, Shinobu 6 instead of 8), so a player learns to trust the printed number, and then this card breaks that trust in the player's favour. Melt/Overloaded/Superconduct all got a `*Reaction preview:*` line; the below-half clause got nothing.
3. **`Plating is reduced by 1 at the start of your turn`** — it read 8, 8, 7 across three rounds. Possibly my round-boundary confusion; noting it because I could not make the text and the number agree.
4. **The reaction glossary only appears once you already have the element.** The page says as much (*"Each of the six is defined again on the first screen that reaches a second element"*), and it is a defensible rule, but it means every reaction card in a card-reward screen is priced blind. I passed Dahlia twice without ever being told what Hydro does.
5. **Enemy list numbers re-count mid-turn, and there is no stable way to name an enemy.** Killing "Gardener (1)" mid-turn silently re-labelled the rest, and my next targeted card went to the wrong body. The page prints this warning for cards in hand but not for enemies. This is the bridge, not the kit, but it is the one thing that cost me a play I had reasoned out correctly.
6. **Grounded and the whole Bomb archetype are at war**, and I never resolved it. `At the start of your turn, if none of your Bombs went off last turn, gain 6 Block and 1 Spark` — but the Spark it grants is the fuel for Stoke the Fuse, Bang Bang! and Fireworks Show, all of which exist to make Bombs go off. So the card that pays for the engine turns itself off when the engine runs. I do not know whether that is intended tension or a mistake. Kaeya's `This turn, Grounded counts nothing as having gone off` is evidently the designed patch, which suggests it is intended — but it means the fix lives on a card you may never be offered.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted:** **Stoke the Fuse.** Not because it is weak — its one live play was +18 onto a Bomb, which won the elite — but because for three fights it was a card that could not be played at all, and a 1-Spark price on a blank is still a cost paid in a card slot. Runner-up, **Confiscated**, but that one is honest about it.
- **Happiest to draw:** **Mine Toss.** One energy, hits every enemy, does not trigger when-hit powers, detonates on its own without needing a Set-off card, feeds Pounding Surprise, and turns "the enemy attacks me" into "the enemy kills itself". It made two fights unlosable and it is the only card in the deck that is simultaneously the offence, the defence and the fuel.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, but a poor one, and it was a decision about a card I could not play.** The hand was Strike ×3, Defend, Stoke the Fuse against two Corpse Slugs carrying Ravenous. The live question was Strike ×3 versus Defend + Strike ×2 — a real but thin tempo/safety call at full HP against a weakened 6-damage attack, where racing is obviously right. The interesting text on the screen was Ravenous (kill one, the other gets Stunned but +4 Strength forever), and that decision did not arrive until turn 2. Stoke the Fuse — the one Klee-flavoured card in the opening hand — was unplayable in principle, not merely bad. **So turn 1 presented a Strike-or-Defend decision, and the kit itself presented nothing.** By contrast the elite's turn 1 presented four interlocking ones. The kit's first turn is its weakest turn.

---

## Non-blindness declaration

- **Game commands:** only `GITS_LANE=1 python -m understudy.blindplay observe` and `GITS_LANE=1 python -m understudy.blindplay act "<command>"`. No `harness state`, no `scenario`, no `staged_turn`, no `soak`, no other understudy subcommand.
- **Tools used:** the **Bash** tool throughout, and the **Write** tool once, for this file.
- **Non-game Bash calls:** `mkdir -p review/qa/klee-round-17-2026-09-05`; and shell plumbing wrapped around the two allowed commands only — `| tail -1` / `| tail -2` / `| tail -3` to trim `act` output, `>/dev/null` to discard `act` output when I immediately re-observed, `| sed -n '<range>p'` and `| grep -E '^- \*\*'` to re-read one block of an `observe`, and two `for c in ...; do ... done` loops that issued a series of `act "play ..."` calls. No other program was run.
- **Repo files read: none.**
