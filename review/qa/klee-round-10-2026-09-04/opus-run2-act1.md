# Klee round 10, run 2, act 1 — blind seat record

## Identity

- **Model / seat:** Claude Opus (Fable 5.1), blind TESTER seat, lane 2 (`GITS_LANE=2`).
- **Run seed:** not printed on any screen I saw. The bridge never showed a seed.
- **Character:** Klee (never named on screen; inferred only from the card titles the
  bridge printed — Jumpy Dumpty, Ka-pow!, Pop!, Sparks, Bombs).
- **Act:** 1. **Boss named by the map:** *The Kin* (the fight itself was **Kin Priest**
  190 HP with **Kin Follower** 59 and **Kin Follower** 58).
- **Actions accepted:** 249 accepted `act` calls (cap 250). Two further `act` calls were
  emitted and came back as a bare `}` with no `ok` line — both were sent at a moment when
  the screen had already changed under me (see "Refusals" below); I do not count them as
  accepted.
- **Termination reason:** the stop condition was reached, not a budget. The act-1 boss died,
  its reward screen was handled, and the lane now sits on the **act-2 map** (which prints
  *The Insatiable* at the top of act 2). I stopped there and did not enter act 2. The
  action budget was, however, effectively exhausted — I finished on 249 of 250, and I was
  rationing actions from the boss fight onward.
- **HP trajectory:** 62 → 58 (f1) → 46 (f2) → 44 (f3/f4) → 53 (Sapphire Seed heal) →
  37 (elite Byrdonis) → 55 (rest) → 54 (f5) → 50 → 38 (f6) → 28 (f7) → 21 (f8) → 20 (f9) →
  38 (rest) → 30 → 17 → 16 (boss round 6, **last HP the bridge printed**).
  The post-boss HP was never printed: the kill resolved during the enemy turn and the next
  screen was the reward screen, which does not carry HP, and the map screen does not either.
- **Gold:** last figure the bridge printed for my purse was **165** (shop, floor 6), of which
  I spent 102. Everything after that I only saw as reward lines (+45, +15, +16, +10, +10,
  +19, +100). I did not see a running total again, so I will not state one.
- **Potions held at the end:** 1 of 4 slots — **Dexterity Potion**. (I declined the boss's
  Swift Potion to keep an action in reserve.)
- **Deck at the end (19 cards):** Strike ×4, Defend ×4, Ka-pow!, Jumpy Dumpty, Pop! ×2,
  Mine Toss, Barbara — Front Row Seat, **Alice's Recipe+** (upgraded), Fwoosh!, Dig In,
  Perfect Timing, Grounded.
- **Relics at the end:** Pounding Surprise (starting), Phial Holster (Neow), Intimidating
  Helmet (elite), Planisphere (treasure).

**Neow pick: Phial Holster** — "Gain 1 potion slot and procure 2 random Potions." I took it
over Arcane Scroll (a random Rare) because a permanent fourth slot compounds all act, and
over Silken Tress because "Enchant all cards in your first card reward with **Glam**" printed
no definition of *Glam* anywhere on the screen and I refused to buy a keyword I could not read.
Those two potions ended up carrying the run: the Vulnerable Potion won fight 4 outright and
the Poison Potion landed the last 1 HP on the boss.

---

## Fight 1 — Fuzzy Wurm Crawler (55 HP)

**Turn 1** (3 energy; hand Ka-pow!, Defend, Strike ×2, Jumpy Dumpty). Played **Jumpy Dumpty**
(Bomb 8), then **Strike**, **Strike**. *Rejected:* playing Ka-pow! (0 cost, Retain, "Set off")
immediately — a Bomb 8 set off now is 8 damage, and the Bomb keyword printed "grows 4 a turn",
so a turn of patience was worth +4 for free. Also rejected Defend: the enemy's printed intent
was 4 damage against 62 HP.

**Turn 2.** Bomb read **12**, enemy 43/55, intent **Empower (Buff)** — no attack coming. Played
**Ka-pow!** (set off 12 + 4 = 16) then **Strike**, **Strike**. *Rejected:* holding one more turn
to let the Bomb reach 16. The reason I did not was specific and it is the first real decision
this kit gave me: because the enemy was buffing, my two spare energy could only buy Block, and
Block against a no-attack turn is worth zero — so the only thing waiting would have bought me
was +4 on the Bomb, against which detonating now bought a Spark (Pounding Surprise) and the
Mine 3 that Jumpy Dumpty promised. The screen and the outcome agreed exactly: 43 → 21, and
the enemy badge then read "Bomb 3 … Bombs here: 1, including 1 Mine."

**Turn 3.** Enemy 15/55, now **Strength 7** and swinging for 11; Mine at 7. Played **Strike ×3**
(18 ≥ 15). *Rejected:* blocking and letting the Mine (7) do the work on its attack — it would
not have finished the job, and its Empower turn had already shown me the fight gets worse the
longer it runs.

**Reward:** took **Pop!** (0 cost, Bomb 5) over Sizzle, Careful Arrangement and Amber. My whole
Bomb supply was one card (Jumpy Dumpty) and one detonator (Ka-pow!), so the constraint was
Bomb mass, not detonation, and Pop! adds mass for no energy.

## Fight 2 — Nibbit (46 HP)

**Turn 1.** **Pop!** + **Jumpy Dumpty** (Bombs 5 + 8) then **Strike ×2**. *Rejected:* Ka-pow! —
same logic as fight 1, and with two Bombs the growth was now +8 a turn, i.e. more than a Strike
for zero energy.

**Turn 2.** Bomb **21**, enemy 34, intent "Attack for 8 **and also** Defensive (Defend)".
Played **Ka-pow!** (21 + 4 = 25) then **Strike ×2** → 37 ≥ 34, kill.
*Rejected:* one more growth turn. The printed intent decided it: the enemy was about to gain
Block, and the Bomb keyword says "Not an Attack: only their Vulnerable and a cap move it," which
I read as Block *not* being one of the things that moves it — but I did not know whether Block
would still absorb a Bomb hit, and I did not want to find out with my whole payload on the line.
Detonating before the Block existed sidestepped the question.

**Reward:** took **Mine Toss** over Ammo Scavenging. Mines are the only Bomb in the kit that
goes off without spending a card, and this deck had exactly one detonator.

## Fight 3 — Shrinker Beetle (40 HP)

**Turn 1.** Intent was **DebuffStrong**, no attack. **Mine Toss** + **Jumpy Dumpty** + **Strike**;
Defends deliberately left in hand as dead cards against a no-attack turn.

**Turn 2.** The debuff landed: **Shrink −1 — "While Shrinker Beetle is alive, your Attacks deal
30% less damage"**, and my Strikes redrew as **4** instead of 6. The Bombs did not move. That is
the cleanest thing the kit taught me all run and the screen taught it *by itself*: Bombs are not
Attacks, so the anti-Attack debuff simply does not touch the payload. Played **Pop!**, **Strike**,
**Strike**, **Defend**. *Rejected:* two Defends over two Strikes — I priced 8 damage against 2 HP
and took the damage.

**Turn 3.** Bomb 25 vs 18 HP; **Ka-pow!** ended it. No alternative worth naming: a 25-point Bomb
against 18 HP is not a decision.

**Reward:** took **Barbara — Front Row Seat** over Perfect Timing / Tinder Toss / Careful
Arrangement. This was the pick I thought hardest about. Perfect Timing was flatly more damage per
energy than a Strike; Tinder Toss cost no energy at all. I took Barbara because it was the only
card offered that could put a *non-Pyro* aura on a target, which is the only way my deck could
ever make an Elemental Reaction happen, and it patched the one hole the first three fights had
shown (I owned five Block cards).

## Fight 4 — Assassin Raider (21) / Axe Raider (20) / Crossbow Raider (19)

**Turn 1** — the best turn of the run, and the first that felt authored. 15 damage incoming.
Played **Barbara** on Assassin Raider (Hydro aura), then **Jumpy Dumpty** on the same target
(Bomb 8), then **Ka-pow!**. The Bomb went off as a Pyro hit into a Hydro aura → **Vaporize**,
and Assassin Raider read **5/21**: 16 damage from a Bomb 8 and a 4-damage card. **Strike**
finished it. *Rejected:* spreading the Bomb across targets, and rejected killing the Axe Raider
(5 damage) instead of the Assassin (10 damage) — printed intent numbers made that arithmetic easy.
Barbara's rider ("Whenever a Bomb goes off this turn, gain 3 Block") meant the same card that
multiplied the payload also paid for the turn's defence. Took 0 damage.

**Turn 2.** Crossbow Raider: 19 HP, Block 3, **14** incoming, wearing **Bomb 14 (2 Mines)**.
I read the Bomb keyword's "only their **Vulnerable** and a cap move it" as an instruction and
used the **Vulnerable Potion** on it, then **Mine Toss** (stack → 18), then two Defends.
On its turn the Mines went off before its hit, at Vulnerable rates, and **killed it before the
attack landed**. I took 0. *Rejected:* spending the potion on the boss instead — I judged that
converting a whole enemy turn into zero was worth more than a future 50%.

**Turn 3.** Axe Raider 13 HP behind Block 5, wearing a Bomb. **Pop!** → **Ka-pow!** → **Strike**;
dead. (A fourth `act` I sent — a second Strike — returned a bare `}`; the fight had already ended.)

**Reward:** took **Alice's Recipe** ("Your Bombs grow twice each turn") over Sizzle / Yae Miko /
Coven Errand. Growth is the only resource in this kit that costs no cards and no energy, so
doubling it doubles the free half of the deck.

## Sapphire Seed (event, floor 5)

Two options: **Consume** (heal 9, upgrade a card) and **Plant and Nourish** ("Enchant a card with
**Sown**"). *Sown was not defined anywhere on the screen* — no keyword block, no gloss. I took
Consume, partly because heal-plus-upgrade is concrete and partly because I will not pick an
option whose payload is a word the game has not shown me. Upgraded **Alice's Recipe** on a guess
that a 2-cost power upgrades to 1 cost; it did (`Alice's Recipe+ … The cost printed on this card
is 2; it is showing 1 here, because this copy is upgraded`). The upgrade screen showed only the
*unupgraded* text of every candidate, so every upgrade choice in this run was made blind to its
own result.

## Shop (floor 6, an Unknown that turned out to be a shop)

165 gold; **no card-removal option was offered** by the bridge. Bought **Fwoosh!** (1 Spark:
Set off, 6 damage) and **Dig In** (1 Spark: 8 Block) for 51 each. Both cost Sparks rather than
energy, and Pounding Surprise had been handing me a Spark per Bomb all act, so they read as pure
addition. *Rejected:* Flame Dance ("Set off each enemy whose aura is **not** Pyro") — I could not
work out why I would want a card that refuses to detonate the enemies my own Bombs have just
painted Pyro, and Grounded, whose condition ("if none of your Bombs went off last turn") I then
misjudged as anti-synergy; I bought it later once I understood my own play pattern.

## Elite — Byrdonis (84 HP, Territorial: +1 Strength at the end of its turn)

**Turn 1.** **Alice's Recipe+**, **Jumpy Dumpty**, **Barbara** (Hydro + 5 Block). *Rejected:*
Strike instead of Barbara — 6 damage against a 5-Block-plus-a-Hydro-aura that I expected to be
worth ~+50% on a Bomb next turn. Took 12.

**Turn 2.** Bomb had gone 8 → **16** (Alice confirmed). And here the kit's sharpest edge cut me:
**the Hydro aura had 1 turn left and I had drawn no detonator** — hand was Strike, Dig In, Defend,
Strike, Pop!. The multiplier expired unused. Played **Pop!**, **Dig In** (8), **Defend** (5),
**Strike ×2**; 13 Block against 15 incoming, took 2.

**Turn 3.** Bomb **37**, Byrdonis 72, swinging 19 and climbing. Hand: three Defends, Ka-pow!,
Fwoosh!. I played **three Defends and nothing else**, holding Ka-pow! (Retain guarantees it stays)
and deliberately *not* playing Fwoosh!, because Fwoosh! would have detonated the stack for its
6-damage body. *Rejected:* detonating for 37 + 4 = 41. The reason is the structural one: both of
my detonators cost 0 energy, so every energy I own can always go to Block, and a held Bomb grows
+16 a turn for free while a Strike buys 6. Waiting is the correct play whenever I can survive the
turn — which makes "can I survive this turn" the actual decision the kit asks, over and over.

**Turn 4.** Bomb **53**. **Mine Toss** (stack → 57) → **Ka-pow!** (57 + 4 = 61) → **Fwoosh!** (6)
→ **Strike** (6) = 73 against 72 HP. Dead on the nose, at 37/62. This turn was arithmetic, not
judgement, but it was *satisfying* arithmetic — I counted it out before I played it and the game
paid out exactly what the screens said it would.

**Reward:** Intimidating Helmet (relic) + **Perfect Timing**.
Note on the relic: *"Whenever you play a card that costs [Energy][Energy] or more, gain 4 Block."*
My deck contained exactly one 2-cost card, and I had just upgraded it to cost 1. The relic did
nothing for the rest of the run.

## Fight 5 — Leaf Slime (M) (32) / Flyconid (49)

**Turn 1.** **Pop!** + **Strike** into Flyconid, two Defends. Nothing to reject; the hand had
one Bomb card and no reason to split it.

**Turn 2.** **Dig In**, **Barbara** (Hydro on Flyconid), **Defend**, **Strike**: 18 Block against
16 incoming, took 0. *Rejected:* a third Defend for 6 more damage forgone.

**Turn 3.** Here the bridge did something genuinely good: **Fwoosh! printed
`*Reaction preview: Vaporize* — Pyro meets Hydro: this hit deals 1.5x damage`** directly on the
card in my hand. I did not have to remember the aura. **Jumpy Dumpty** (stack → 21) → **Fwoosh!**:
Flyconid 37 → **4**. **Strike** killed it; **Alice's Recipe+** with the spare energy.

**Turn 4.** Leaf Slime carried **Bomb 22, "Bombs here: 2, including 2 Mines"** — see the defect
note below. **Mine Toss** + **Pop!** + **Ka-pow!** = 35 against 32. Dead.

**Reward:** took a **second Pop!** over Grounded. 0-cost Bomb mass compounds with Alice; I
reversed this judgement one fight later and took Grounded anyway, which tells you the two cards
are close.

## Fight 6 — Vine Shambler (61 HP)

**Turn 1.** **Pop! ×2**, **Mine Toss**, **Dig In**, **Strike**. *Rejected:* Jumpy Dumpty (not in
hand) — nothing else to weigh.

**Turn 2.** Barbara came up wearing a different preview:
**`*Reaction preview: Vaporize* — This card deals no damage. Pyro plus Hydro is still consumed,
and there is no hit here for the 1.5x to multiply.`** That is the bridge telling me, unprompted,
that playing my multiplier onto a Pyro-aura'd target would *burn* the reaction for nothing and
leave the enemy bare. I held Barbara and played Strike + Defend ×2 instead. That warning is the
single most useful line the interface printed all run.

**Turn 3.** The enemy's CardDebuff landed: **Tangled — "Attacks cost an additional [Energy] this
turn"**, and Ka-pow! redrew at **cost 1**, Strikes at 2. Bomb 26, enemy 45, incoming 16, and **no
Block card in hand.** I played **Jumpy Dumpty** (stack → 34) and one **Strike**, and ate the full
16 (HP 50 → 38). *Rejected:* the line that kills — Energy Potion, then Jumpy + Ka-pow + Fwoosh +
Strike for 50 against 45 — which would have taken 0 damage. I turned it down because the map
showed a rest site before the boss, which makes HP recoverable and potions not. That was, I think,
correct, and it is the kind of trade the kit asks constantly.

**Turn 4.** Bomb **46**, enemy 39. **Ka-pow!**. Dead.

**Reward:** took **Grounded** — reversing my fight-5 judgement, because turn 3 had just shown me
the failure mode: a whole grow-turn with no Block card in hand. Grounded pays 6 Block for exactly
the turns my strategy already wants to take.

## Fight 7 — Nibbit (46) / Nibbit (42)

**Turn 1.** **Mine Toss**, **Jumpy Dumpty** on the second Nibbit, **Defend**.
**Turn 2.** Split the two **Pop!**s one per enemy, **Strike**, **Defend** (took 9, HP 37 → 28).
*Rejected:* stacking both Pops on one target — with two 40+ enemies and no AoE detonator, I judged
that leaving one of them with no Bomb at all would cost me the fight later.

**Turn 3** — the turn I was closest to losing. HP 28, 22 incoming, one enemy at 42 and one at 28.
Used **Potion of Binding** (1 Weak + 1 Vulnerable to ALL) *because the Bomb keyword told me
Vulnerable is one of the two things that moves a Bomb*, then **Fwoosh!** into the Bomb-25 Nibbit
(dead) and **Ka-pow!** into the other (42 → 15), then two Strikes at Vulnerable rates for the kill.
Whole fight ended in that turn; I took 0. *Rejected:* the pure-Block line (Dig In + Defends,
detonate next turn), which survives but hands both enemies another attack and another Strength tick.

## Fight 8 — Inklet (13) / Inklet (12) / Inklet (16), all with *Slippery*

**Slippery: "The next time Inklet loses HP, it only loses 1 HP instead."** This is the one enemy
mechanic that reads as *designed against* the kit: a Bomb's whole payload arrives as a single hit,
so Slippery eats an entire stack for 1 HP. The answer is legible once you see it — spend a cheap
hit first to strip Slippery, then detonate — and finding that was the most interesting thinking
of the run.

**Turn 1.** **Pop!**, **Alice's Recipe+**, **Grounded**, **Defend**. Took 7.
**Turn 2.** **Mine Toss**, **Barbara** (its rider paid 3 Block per Bomb going off), **Strike** into
the Bomb-13 Inklet *purely to strip Slippery for 1 HP*, then **Fwoosh!** to detonate into the now
unprotected target. Dead. Took 0. *Rejected:* detonating first — which would have converted a
13-point Bomb into 1 damage.
**Turn 3.** Two Strikes killed the 10-damage Inklet, **Defend** covered the rest; took 0.
**Turn 4.** **Pop!** + **Ka-pow!** + **Strike** finished the last one.

Also confirmed here, cleanly: on the turn after a detonation **Grounded gave no Block**, exactly as
its text says ("if none of your Bombs went off last turn"). Correct, legible, and a real cost —
Grounded and Mine Toss actively fight each other, since a Mine going off on the *enemy's* turn is
still "your Bombs went off" and switches Grounded off. I chose not to play Mine Toss in the boss
fight for that reason.

## Fight 9 — Twig Slime (M) 26 / Leaf Slime (M) 32 / Twig Slime (S) 11 / Leaf Slime (S) 12

**Turn 1.** **Pop!** + **Jumpy Dumpty** onto Leaf Slime (M), **Dig In**, **Defend**, and
**Perfect Timing** into a bombless Twig Slime (S) for a flat 8 — the only turn all run where I
spent a detonator as a plain Strike, and it felt like a waste of the card's whole identity.

**Turn 2.** HP 21, **23 incoming, 21 HP** — lethal on the board. **Barbara** onto Leaf Slime (M)
(Hydro), then **Ka-pow!**: 21-point stack Vaporised for **29**, taking a 32 HP enemy to 3, while
Barbara's rider handed me 3 Block per Bomb. Two Strikes then killed the two 3-HP enemies outright.
Incoming dropped from 23 to 11 against 11 Block: **took 0 from a board that was lethal on paper.**
That turn is the best argument for the kit I can make.

**Turn 3.** Defend ×2 + Strike; Leaf Slime (S) then **killed itself** on its own attack, because
its Mine stack (14) exceeded its 12 HP and Mines "go off … before the hit lands."
**Turns 4–5.** Pop! + Fwoosh! for 11, then a Strike for the last 3.

## Boss — Kin Priest (190) + Kin Follower (59) + Kin Follower (58)

The Followers print **"Minion — Minions abandon combat without their leader,"** so the fight is
190 HP on one body. That is precisely the shape this kit wants, and the whole fight was one long
version of the decision the kit is built on: *hold, or spend.*

**Turn 1.** **Grounded** (6 Block a turn for exactly the turns I intend to take), **Defend**,
**Strike**. *Rejected:* **Mine Toss** — and this was a real, considered rejection: mines would have
put ~12 free damage on the board but would have gone off on the enemies' turns, which switches
Grounded off. I gave up the damage to keep the Block engine. Took 8.

**Turn 2.** **Pop!** + **Jumpy Dumpty** onto the Priest, **Strike ×2**. No Block card in hand;
took 13 (HP 30 → 17). *Rejected:* Perfect Timing for 8 — detonating a 13-point stack on turn 2 of
a 190 HP fight would have been the single worst play available.

**Turn 3.** HP 17, 19 incoming. **Dig In** (8) + **Barbara** (5) + **Defend** (5) on top of
Grounded's 6 = 24 Block; **Alice's Recipe+** with the last energy. Took 0. This is the turn where
the kit's structure pays: because both detonators cost 0 energy, a turn spent entirely on Block
costs the plan *nothing*, and the Bomb went 21 → 37 for free.

**Turn 4.** **Pop!** (fourth Bomb) + **Dig In**; deliberately played only two cards to conserve
actions. Bomb 37 → **66**.

**Turn 5.** HP 16, **27 incoming**, and the maths said 11 through. Used the **Speed Potion**
(+5 Dexterity for the turn) to turn Barbara + Defend from 10 Block into 20, plus Grounded's 6:
26 against 27. Took 1. Bomb **66 → 103**.

**Turn 6 — the payoff, and it is enormous.** Bomb 103 across 4 charges, Priest at 172, Hydro
still on it from Barbara. **Energy Potion** (+2), **Jumpy Dumpty** (stack → 111), then
**Perfect Timing**, whose text reads *"Set off. Deal 8 damage. If a Bomb triggered an Elemental
Reaction this turn, play this again."* The first Bomb hit the Hydro aura → Vaporize → the card
replayed itself. **Kin Priest 172 → 23 in one card.** Then **Ka-pow!** (4) and **Strike ×3** (18)
took it to **exactly 1 HP** — one point short, with 0 energy and no 0-cost card left in hand.

I was dead on the board: 22 incoming against 16 HP and 6 Block. So I spent the **Poison Potion**
(6 Poison) on a 1 HP enemy and ended the turn. The Poison killed the Priest on its turn, the
Followers abandoned combat, and the fight ended. *Rejected:* holding the Poison for act 2 —
there was no act 2 to hold it for if this turn resolved.

**Boss reward:** took the 100 Gold and proceeded; declined the Swift Potion and the card in order
to stay inside the action cap. **The lane now sits on the act-2 map** (*The Insatiable*).

---

## The kit, after 10 fights

**(a) Which decisions felt like real choices, and what they traded off.**

One decision recurs and it is a good one: **detonate now, or hold and grow.** It is real because
the two sides are priced in different currencies. Holding buys +4 per Bomb per turn (+8 with
Alice's Recipe) for *zero cards and zero energy*; spending buys the current number plus a small
card body. So the question is never "which is bigger" — holding is almost always bigger — it is
**"can I survive one more turn,"** which turns every turn into a defence puzzle whose stake is a
number I can see growing on the enemy's badge. The elite (turn 3: three Defends and nothing else,
holding a retained Ka-pow!) and boss turn 3 (24 Block, zero damage, Bomb 21 → 37) were the two
purest instances, and both felt like decisions rather than sequencing.

The kit sharpens this well by making **both detonators cost 0 energy** (Ka-pow! is 0 and Retains;
Fwoosh! costs a Spark). That is a real design idea: it means the trigger is never competing with
your Block for energy, so "hold" is always affordable and the only thing that can stop you is
dying. Conversely it means the hold plan has one true enemy — **an enemy turn you cannot block** —
and fight 6 turn 3 (Tangled: Attacks cost +1, no Block card in hand, ate 16) is exactly what
losing that argument looks like.

Three more that were genuinely live:
- **Where to put the Bombs** in a multi-enemy fight — because Bombs are single-target and grow
  per-charge, splitting halves your growth. Fight 7 turn 2 (one Pop! each) versus fight 4 turn 1
  (everything on the 10-damage attacker) were opposite answers to the same question.
- **Aura management.** Barbara is the only aura source I had, and the Vaporize she enables is
  worth ~50% of an entire Bomb stack. But her aura lasts 2 turns and my detonator is a draw away,
  so playing her is a *bet on drawing Ka-pow! in time* — a bet I lost at the elite (turn 2, the
  Hydro expired with no detonator in hand) and won at the boss (turn 6, one card for 149 damage).
- **Vulnerable.** The Bomb keyword tells you outright that Vulnerable is one of only two things
  that moves a Bomb, which turns a generic potion into a payload multiplier. Fight 4 turn 2 —
  Vulnerable Potion, then Mine Toss, and the enemy killed itself on its own attack — is the best
  single play the kit let me find, and I found it *by reading the keyword*.

**(b) What felt automatic, and what never seemed worth playing.**

- **Pop! is never a decision.** 0 cost, place a Bomb — you play it every turn you draw it, always,
  in every board state. It is a good card and a dead choice.
- **Strike and Defend.** By the boss my hand was frequently four vanilla cards and one real one.
  The kit's own cards are interesting; the starter chaff is where the automatic turns live, and
  no removal was ever offered.
- **Intimidating Helmet** ("gain 4 Block whenever you play a card costing 2 or more") was live for
  zero cards in my deck after I upgraded my one 2-cost card down to 1. An elite reward that does
  nothing is worth flagging.
- **Ka-pow!'s own body (4 damage) is noise.** The card is 100% its "Set off" clause; the number
  printed on it never once affected a decision.
- **Mine Toss became unplayable once I owned Grounded**, since a Mine going off on the enemy's turn
  counts as "your Bombs went off last turn" and switches Grounded off. Two cards in the same deck
  that silently cancel each other, with the interaction visible only if you read both riders
  carefully, is the sort of thing worth knowing.
- **Flame Dance in the shop** ("Set off each enemy whose aura is **not** Pyro") I could not
  construct a use for at all: my Bombs go off as Pyro hits and paint targets Pyro, so the card
  appears to refuse to detonate the enemies my own deck has been working on.

**(c) What I could not understand, or that contradicted its own printed text.**

1. **Mines multiply when a bombed enemy dies, and nothing says so.** Three times, after an enemy
   carrying a Mine died, a *surviving* enemy's badge read **"Bombs here: 2, including 2 Mines"**
   when only one Mine had ever been placed on it. Fight 4 round 2 (Crossbow Raider: 2 Mines, 14,
   after Assassin Raider died), fight 5 round 4 (Leaf Slime: 2 Mines, 22, after Flyconid died),
   fight 9 round 3 (Leaf Slime (S): 2 Mines, 14, after Twig Slime (M)'s Mine went off). Either
   Mines migrate off the dead onto the living, or they are being double-placed. Whichever it is,
   **no card and no keyword block on any screen mentions it**, and it materially changed my
   arithmetic each time — always in my favour, which is exactly why I would not have caught it if
   I had not been counting.
2. **Bomb arithmetic is not checkable from the screen.** The badge prints one total ("Bomb 25")
   and a count ("Bombs here: 2"), never the individual charges. So when a Mine goes off mid-stack,
   or a Vaporize multiplies "the first Bomb", I cannot verify what happened — I twice reconstructed
   totals that did not reconcile (fight 3 round 3 read 25 where I computed 21). This matters
   specifically because the *order* of Bombs decides which one gets the 1.5×, and the order is
   invisible.
3. **"Only their Vulnerable and a cap move it"** names a **cap** that is never given a number
   anywhere. I reached Bomb 103 without meeting it, but every hold-versus-spend decision I made was
   made without knowing whether the growth I was banking on was about to stop.
4. **The Sapphire Seed offered to "Enchant a card with Sown"** with no definition of *Sown* on the
   screen and no keyword block for it. I declined an option I could not read.
5. **The Elemental Reaction keyword block is far too long** — it runs to a paragraph with an
   all-caps digression about a relic re-applying an aura inside the same beat, printed in full on
   *every combat screen*. The one thing I actually needed from it (which of my cards will react,
   right now, on this target) is instead delivered beautifully by the **`*Reaction preview*`** line
   on the card itself. The preview is excellent; the wall of text behind it is not.
6. **Upgrade screens show only the un-upgraded card.** I picked Alice's Recipe at a rest-site-style
   upgrade on a *guess* about what upgrading would do. It happened to be the right guess.
7. Minor: Barbara's preview says a Vaporize with "no hit here for the 1.5x to multiply" — but it
   does not say the reaction still **consumes** my aura and leaves the target bare, which is the
   part that would actually cost me the turn. I inferred it; it should be stated.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

*Never wanted:* **Fwoosh!** — not because it is weak, but because it is the only card in the deck
that is **actively harmful to hold**. On every grow-turn it sits in hand as a card I must
deliberately not play, since its 6-damage body would destroy a 40-point stack. A detonator in a
deck whose plan is *not detonating* is a card that spends the whole fight arguing with its owner.
(At the elite, turn 3, I explicitly declined to play it for value and then watched it discard.)

*Happiest to draw:* **Ka-pow!** — 0 cost, **Retain**, sets off everything. Retain is what makes the
whole hold-and-grow plan safe: once it is in hand it cannot be shuffled away, so the payoff is
guaranteed and every subsequent turn is purely a question of whether I can block. Honourable
mention to **Perfect Timing**, which on boss turn 6 detonated a 111-point stack, Vaporized it,
*and replayed itself off the reaction it had just caused* — 149 damage from one card. It is the
only card in the deck that made me say "oh" out loud.

**(e) Did the first turn of the first fight already present a decision?**

**Yes — a genuine one, though a quiet one.** Opening hand: Ka-pow!, Defend, Strike ×2, Jumpy
Dumpty, against 55 HP intending 4 damage. Jumpy Dumpty places a Bomb 8; Ka-pow! sets it off for 8.
The decision is whether to cash the Bomb on the turn you plant it, and the Bomb keyword —
"grows 4 a turn, goes off only when **Set off**" — hands you the reason not to, right there on the
card, in the first hand you are ever dealt. That is a good opening: the deck teaches its central
tension on turn 1 without a tutorial. It is *quiet* only because the correct answer is fairly clear
(the enemy is hitting for 4; there is no pressure to cash early), so it reads more as instruction
than as dilemma. The real version of the same decision arrived on turn 2, when the enemy's Empower
intent made Block worthless and I had to reason about what my spare energy could actually buy.

**One overall note, unsolicited.** The failure mode I kept running into is not the Bombs, it is the
**draw**. The plan needs three things at once — mass (Pop!/Jumpy Dumpty), a trigger (Ka-pow!/
Fwoosh!/Perfect Timing), and enough Block to survive the wait — in an eight-card starter chaff pile.
Twice the kit's best line was unavailable purely because the third piece was in the draw pile
(elite turn 2, the Hydro expiring with no detonator; fight 6 turn 3, no Block on a 16-damage turn),
and both times what I lost was not the fight but *the decision* — the turn collapsed into "play
what you have." Ka-pow!'s Retain is the existing answer to this and it is the right one; there just
is not enough of it.

---

## Non-blindness declaration

**Repo files read: none.**

Every game action was one of the two allowed commands, `GITS_LANE=2 python -m understudy.blindplay
observe` and `... act "<command>"`, run through the Bash tool from
`C:\Users\Monty\Documents\GitHub\GItS`. I ran no `harness state`, no `scenario`, no `staged_turn`,
no `soak`, and no other understudy subcommand.

Everything else I ran, in full:

- **Bash — scratch bookkeeping.** One `mkdir -p` of the session scratchpad directory, and repeated
  `echo "<n> <label>" >> …/scratchpad/klee-r10-run2-actions.txt` to keep the running action count
  the coordinator asked for. That file contains only my own action tally.
- **Bash — output shaping.** Many `observe` calls were piped through `sed -n '<range>p'` or
  `sed -n '/## Your hand/,/## Words/p'` and `| tail -1` / `| tail -2` on `act` calls, purely to trim
  the bridge's own output. No other source was read.
- **Bash — shell loops.** Several turns were issued as `for c in '<cmd>' '<cmd>' …; do
  … blindplay act "$c" …; done`. Each iteration is one ordinary `act` call; the loop is only
  batching.
- **Write tool — once**, to create this file at
  `review/qa/klee-round-10-2026-09-04/opus-run2-act1.md`.

I opened no other file in that directory, no YAML sheet, no C# source, no doc, no packet, and no
other seat's record. No `TOOL-BLOCKED` and no `REFUSED: …leak…` line was ever printed.

**Refusals / anomalies (2, neither consecutive, neither a blocked screen):** two `act` calls
returned a bare `}` with no `ok` line and no refusal text — a fourth `play "Strike"` in fight 4
turn 3 and a `skip` after fight 8's rewards. In both cases the screen had already moved on (the
fight had ended; the card-select overlay was not open). The bare `}` with no message is itself
worth noting: a refused command told me nothing about why it was refused.
