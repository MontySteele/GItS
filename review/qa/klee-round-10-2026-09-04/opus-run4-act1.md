# Blind seat record — KLEEMOD-KLEE, lane 2, round 10 run 4, act 1

## Identity

- **Model / seat:** Claude Opus (Fable-family), blind TESTER seat, lane 2.
- **Run seed:** not printed by the bridge on any screen I saw; I never ran a
  command that would show it.
- **Character:** Klee (bomb / Spark kit; starting relic **Pounding Surprise**).
- **Act:** 1. Map header named the act boss up front: **The Kin**.
- **Actions accepted:** 220 accepted `act` calls (cap 250). Running count kept in
  a scratch file; see the declaration section.
- **Termination reason:** the coordinator's stop condition, not a budget. The
  act-1 boss (Kin Priest) died, its reward screen was handled (100 Gold,
  Duplicator, Alice's Recipe), and the lane now sits on the act-2 map. I did not
  enter act 2. No `TOOL-BLOCKED`, no `REFUSED: ...leak...`, no refusal at all in
  220 calls, no stall.
- **HP trajectory:** 62/62 → 60 (f1) → 55 (f2/f3) → 51 → 50 (f4) → 48 (f5) →
  46 (elite start, after a Smith + full rest) → 40 (elite end) → 20 (f7, worst
  point) → 38 (rest) → 15 (boss). **Ended 15/62.**
- **Gold:** 100 from the boss plus what was unspent going in; the act-2 map
  screen prints no gold line, so I cannot quote an exact ending figure without
  a screen that shows one. Gold spent en route: 122 at the one shop.
- **Potions held:** the boss reward screen printed "1 of 3 slots are full" but
  did not name the potion (both the Colorless Potion and the Poison Potion were
  spent). The act-2 map prints no potion list.
- **Relics at the end:** Pounding Surprise (starter), Winged Boots (all 3 charges
  spent), Gremlin Horn, Bronze Scales, Juzu Bracelet, Duplicator.
- **Deck at the end (23 cards):** Strike ×4 (one carrying the enchantment
  *Slither*), Defend ×4, Jumpy Dumpty+ (upgraded), Ka-pow!, Dig In ×2, Pop! ×2,
  Careful Now, Mine Toss, Fwoosh!, Fish-Flavored Bait, Big Badda Boom ×2,
  Dodoco Cover, Alice's Recipe, Clumsy (curse).

**Neow pick: Winged Boots** ("You may ignore paths when choosing the next rooms
to travel to 3 times"). I took it because the other two both wrote on the deck —
Kaleidoscope would have put *two other characters'* card rewards into a deck I
was being asked to read blind, and Dowsing Rod adds a card the screen never
described — and route freedom costs the read nothing.

---

## Fight 1 — Shrinker Beetle (38 HP)

**Turn 1** (3 energy, hand: Jumpy Dumpty, Strike ×2, Defend ×2). Played **Jumpy
Dumpty** ("Place a Bomb 8. When it goes off, place a Mine 3 on ALL enemies")
then both Strikes. *Rejected:* both Defends — the intent line read "Strategic
(DebuffStrong) — This enemy intends to apply a Debuff to you", so block would
have been spent on nothing. A real decision, and the screen gave me exactly the
information to make it.

**Turn 2.** The debuff landed as **Shrink -1 — "While Shrinker Beetle is alive,
your Attacks deal 30% less damage"**, and my Strikes' printed faces changed from
6 to 4. The Bomb had grown 8 → 12 and the badge read "Bomb 12 … Bombs here: 1.
Each grows at the start of your turn. None goes off by itself." Drew **Ka-pow!**
("Retain. Set off. Deal 2 damage" — printed at 2, i.e. also shrunk). Played
Ka-pow → 26 HP fell to 12, exactly Bomb 12 + Ka-pow 2. **This is the moment the
kit taught itself:** Bomb damage is not an Attack, so the enemy's own debuff did
not touch it. Then Strike ×2 and one Defend. *Rejected:* holding Ka-pow another
turn for a Bomb 16 — +4 damage was not worth a turn against a 7-damage attacker.

**Turn 3.** Beetle at 1 HP: the Mine 3 the Jumpy Dumpty rider had planted went
off when it attacked, as printed. One Strike ended it. *No rejected
alternative — a 1-HP enemy is not a decision.*

Reward: took **Dig In** (cost 1 **Spark**, gain 8 Block). *Rejected:* Chain Fuse
(each Bomb grows by 6 — dead with only one planter in a 10-card deck), Pocket
Fireworks (9 damage, vanilla, and Attacks are what enemies shrink), Mika (an
off-character card that would muddy the read).

## Fight 2 — Leaf Slime (S) 15, Twig Slime (M) 27, Twig Slime (S) 11

**Turn 1.** Ka-pow with no bomb on the board is 4 damage for 0 energy. Played it
plus 2 Strikes into Leaf Slime (16 ≥ 15, dead), last Strike into Twig (S).
*Rejected:* killing Twig (S) first, the only attacker — but both Slimes' intents
read "intends to give you 1 Status card", and cutting off future status
generation beat saving 4 damage.

**Turn 2.** The turn Dig In justified itself: **Dig In (8 Block for 0 energy and
1 Spark) + Strike (killed Twig (S), removing 4 incoming) + Defend ×2** = 18
block against 11 incoming, on 3 energy. The Spark price buys a fourth card play
in a three-energy turn; that is a genuinely different resource, not a reskin.
*Rejected:* spending the energy on damage and eating 11.

**Turn 3.** Twig (M) 27 alone, attacking for 11. Planted Jumpy Dumpty and set it
off in the same turn (Bomb 8 + Ka-pow 4 = 12), then double Defend. *Rejected:*
holding for Bomb 12 next turn. The Mine 3 rider firing on its attack (3 more)
made same-turn detonation the better tempo.

**Turn 4.** Intent was StatusCard, so no block; 2 Strikes finished it.

Reward: took **Pop!** (cost 0, place a Bomb 5). *Rejected:* Careful Arrangement
and Sorry Jean (both want a board of bombs I did not yet have), Barbara
(off-character).

## Fight 3 — Fuzzy Wurm Crawler (56 HP)

The fight that showed the kit's actual shape.

**Turn 1.** Jumpy Dumpty (Bomb 8) + 2 Strikes. Held Ka-pow (Retain). *Rejected:*
Defend — 4 incoming is cheap rent on a bomb that grows 4 a turn.

**Turn 2.** Enemy intent "Empower (Buff)" — no attack. Played **Pop!** for a
second bomb and ended the turn with 3 energy unspent, because the whole rest of
my hand was Defend against an enemy that was not attacking. **This turn
presented no decision at all** beyond "plant the free bomb"; that is a finding,
not a complaint about the enemy.

**Turn 3.** The buff resolved as **Strength 7** and the badge read **Bomb 25 —
"Bombs here: 2"**. Ka-pow set off 25 + 4 = 29, then three Strikes (18) finished
56 HP exactly. Screen and outcome agreed to the point.

**Where the screen and the outcome disagreed:** after that Ka-pow the enemy's
badge line was *gone entirely* — no "Bomb 3 … including 1 Mine" as in fight 1,
even though the stack that went off contained the Jumpy Dumpty bomb whose text
says "When it goes off, place a Mine 3 on ALL enemies." In fight 1 (a single
bomb) the Mine badge appeared. In fight 5 (single bomb, four enemies) it
appeared on all four. Here, with a Jumpy Dumpty bomb and a Pop! bomb merged into
one "Bomb 25 / Bombs here: 2" badge, **no Mine appeared.** I could not tell from
any printed face whether the rider silently failed when its bomb was stacked
with another, or whether it fired and something consumed it in the same beat.

Reward: took **Careful Now** (Retain; Block equal to your largest Bomb, up to 10)
— the card that pays for the stalling the engine wants. *Rejected:* Rapid Fire
(2 energy, "random enemy 4 times" — against one enemy the first hit consumes the
stack and the rest are 3s, strictly worse than a 0-cost Ka-pow), Dig In #2,
Sucrose.

## Interlude — event, shop, event

Brain Leech → Share Knowledge → took **Mine Toss** (Mine 4 on ALL enemies) over
Coven Errand ("If you played a **Hexerei** card this turn" — I had no companion
cards, so the clause was dead), Ammo Scavenging, Dig In, Rapid Fire.

Shop (141 gold): bought **Fwoosh!** (1 Spark: Set off + 6 — an energy-free
detonator), **Pop! #2**, **Fish-Flavored Bait** (25g: 4 damage + Bomb 4).
*Rejected:* Explosives Workshop at 77 ("your Bombs grow by 1 more") — +1 per bomb
per turn read small beside a whole extra planter; Card Removal at 75; the three
relics all out of reach.

Dense Vegetation → chose **Rest** ("Heal 18 HP. Fight some enemies") over 83 gold
for 8 HP, because a fourth fight is worth more to this seat than gold with no
shop in view.

## Fight 4 — 4× Wriggler (21, 20, 17, 18)

**Turn 1.** Jumpy Dumpty on Wriggler (1), then Ka-pow. **Confirmed the rider
works with a single bomb: "Bomb 3 … Bombs here: 1, including 1 Mine" appeared on
all four Wrigglers.** Then Pop! onto Wriggler (3) and 2 Strikes to finish
Wriggler (1). *Rejected:* stacking the Pop! bomb onto the same target — with no
second detonator in hand, spreading was worth more.

**Turn 2.** Two attackers at 8 each with Mine 7 apiece. Played **Mine Toss**
(Mine 4 on all) + Defend ×2. *Rejected:* Fish-Flavored Bait for 4 damage — 5
extra damage taken to deal 4 is a bad trade.

**Turn 3.** Sparks were at **8** — mines going off feed Pounding Surprise fast.
Fwoosh! (1 Spark, 0 energy) plus a Pop! bomb killed Wriggler (1) outright
(5 + 6 ≥ 9). Struck the 7-HP one, Dig In + Defend for 13 block. *Rejected:*
touching the Wriggler carrying **Bomb 21** at 11 HP — its own Mine was going to
detonate on its attack and do the work for me.

**The rule I got wrong, and the screen corrected me.** I had inferred from turn
2 that a Mine trigger sets off *the whole stack* (a Bomb-11 enemy took exactly
11). Turn 4 disproved it: the Bomb-21 enemy took only 8 and kept a Bomb 13
(shown next turn, grown, as Bomb 17). Both readings fit the earlier screen
because in that case *both* charges in the stack happened to be Mines. So: only
Mines self-trigger, plain bombs in the same stack do not — correct, legible, and
the aggregated "Bomb 21 / Bombs here: 2, including 1 Mine" badge is exactly
enough to work it out **if** you notice the "including 1 Mine" clause. I did
not, at first.

**Turn 4–5.** Killed the 1-HP attacker, then the last Wriggler. Status card
**Infection** ("Unplayable. At the end of your turn, if this is in your Hand,
take 3 damage") appeared in hand — the only place the status cards those
Wrigglers kept announcing ever became visible.

Reward: **Big Badda Boom** (2 energy: "Set off. Deal 12 damage. Then deal damage
equal to what the Bombs dealt"). Obvious take: it is the multiplier the growth
engine is built for.

## Fight 5 — Fogmog (74) + Eye with Teeth (6, Illusion, Minion)

**Turn 1.** Jumpy Dumpty + Fish-Flavored Bait onto Fogmog (Bomb 12 total),
Defend. *Rejected:* playing Big Badda Boom early — 12 + 12 + 12 is a fraction of
what the same card does three turns later.

**Turn 2.** Struck the Eye (6 HP) dead: **Gremlin Horn** refunded the energy and
drew a card, so killing a minion was free. *Rejected:* ignoring it — its intent
read "intends to give you 3 Status cards", and status cards are what stops you
drawing the payoff.

**Turns 2–4 were the stall.** Careful Now printed exactly 10 block off a Bomb 20+
(capped), Defends and Dig In covered the rest, Pop! kept adding charges for free,
and the badge climbed **20 → 28 → 45 → 66**. The Eye revived each turn (Illusion)
and I killed it each time it was cheap to. Meanwhile Fogmog's own buffs pushed
its attack from 8 to 16. *The rejected alternative every one of those turns was
"cash out now with Ka-pow", and the reason not to was arithmetic I could do from
the printed badge: +4 per bomb per turn against a 9–16 damage attacker I could
block.*

**Turn 5.** Drew Big Badda Boom into a **Bomb 66** and played it. 54 HP
evaporated. The Eye, "Minion 1 — Minions abandon combat without their leader",
left with it. That was the single most satisfying turn of the run.

Reward: **Dodoco Cover** (Bomb 4 + 5 Block for 1 energy). *Rejected:* a second
Big Badda Boom — Ka-pow retains and always comes back, so detonation was never
my scarce resource; surviving while bombs grow was. *Also rejected:* Careful
Arrangement ("Move all your Bombs onto the enemy as one Bomb. It grows by 5") —
**I could not work out what this buys**, since a stack on one enemy already
detonates together and the badge already aggregates it.

## Interlude — Treasure, Smith, Wood Carvings, Rest

Chest: **Bronze Scales** (3 Thorns). Smith: upgraded **Jumpy Dumpty → Jumpy
Dumpty+** (Bomb 8 → 11, Mine 3 → 4) over Ka-pow, on the reasoning that the
biggest single charge is what Big Badda Boom multiplies.

**Wood Carvings — the one screen I had to gamble on.** Three options: "Choose 1
starter card to Transform into **Peck**", "Enchant 1 card with **Slither**",
"Choose 1 starter card to Transform into **Toric Toughness**". *None of the three
results was described anywhere on the screen.* I picked Snake/Slither and then,
on the card-selection screen, put it on a **Strike** rather than on Jumpy
Dumpty+ — purely because I was buying something whose text I could not read and
did not want it landing on my engine card. Only later, when the card came up in
hand, did the game print what I had bought: *"Slither — When you draw this card,
randomize its cost from 0 to 3."* It drew at cost 0 once and cost 2 once. The
enchantment itself is fine; the event that sells it blind is the finding.

## Fight 6 (Elite) — Phrog Parasite (62) → 4× Wriggler on death

**Turn 1.** Hand was Strike + three Defends + Dig In against an enemy whose
intent was "give you 3 Status cards". Played one Strike and ended. **A turn with
no decision in it at all** — nothing in hand did anything the board wanted.

**Turn 2.** 4×4 incoming, so Bronze Scales' Thorns paid 12 back. Played Strike
(Slither, rolled to 0), Big Badda Boom (with no bombs down — just 12 damage) and
Fwoosh!, for 24 + 12 thorns. *Rejected:* holding Big Badda Boom, which is not
Retain and would simply have been discarded.

**Turn 3.** The whole kit in one turn on 3 energy: **Dodoco Cover** (Bomb 4 +
block) → **Fish-Flavored Bait** (4 damage + Bomb 4) → **Ka-pow!** (set off 8, +4)
→ **Strike**, for exactly the 20 HP left. Then the Parasite split into four
Wrigglers, all Stunned, and Gremlin Horn handed back energy and a card.

**Turns 4–6.** Mine Toss onto all four while they were stunned; the mines grew
and each attacker detonated its own on the way in. Killed the biggest stack with
Ka-pow (25 into a 21-HP Wriggler), let Thorns finish another.

**A second thing I could not account for.** After that exchange one Wriggler
remained at HP 9/20 — the one I had just planted Jumpy Dumpty+ (Bomb 11) on —
and its badge read **"Bomb 36 … Bombs here: 3"**. Grown, my Bomb 11 should have
been 15; the other 21 was the exact figure the *dead* Wriggler had been carrying.
Whether bombs migrated off the corpse, or the badge aggregated something stale,
no screen said. Big Badda Boom then ended it.

Rewards: 39 gold, Poison Potion, **Juzu Bracelet**, and a second **Big Badda
Boom** (taken this time specifically to raise the odds of drawing a finisher at
the boss).

## Fight 7 — Leaf Slime (M) 34 + Flyconid 48 — the near-death

**Turn 1.** Jumpy Dumpty+ then Ka-pow at once (Bomb 11 + 4), spreading Mine 4
onto both, then two Strikes into the Flyconid. *Rejected:* growing the bomb —
with two enemies, the mine-on-all rider is worth more now than four more points
later.

**Turns 2–3 are where the deck's fault line opened.** I drew **Defend, Defend,
Defend, Pop!, Pop!** against a Flyconid at 4 HP that was telegraphing 16 damage,
and **not one card in my hand could deal damage.** Frail cut the block by a
quarter; Vulnerable then multiplied the incoming by half again. 27 HP → 20 → the
enemies at 12 and 12 with me Vulnerable, i.e. 36 incoming against 20 HP.

**Turn 4 was the best turn of the run and it was pure kit.** Strike killed the
1-HP Flyconid (Gremlin Horn refunded the energy), and Big Badda Boom set off the
**Bomb 18** I had quietly Popped onto the Leaf Slime two turns earlier: 18 + 12 +
18 = 48 into a 23-HP enemy. Both dead on the turn that would otherwise have
killed me. *Rejected:* blocking and surviving at ~4 HP — killing both was
strictly better and the printed numbers said it was available.

Reward: **Dig In #2** over **The Big One** ("cost 3. Set off for quadruple
damage"). The Big One is plainly the more exciting card and I did not take it:
at 20/62 with a 190-HP boss ahead, an 8-block card that costs no energy was the
one that addressed what had nearly killed me. That is the trade the kit keeps
putting in front of you and I think it is a good one.

## Fight 8 (Boss) — The Kin: Kin Priest 190 + Kin Follower 59 + Kin Follower 58

Both Followers print "Minion 1 — Minions abandon combat without their leader", so
the fight is 190 HP on the Priest and nothing else.

**Turn 1.** Dodoco Cover (Bomb 4 + 5 block) + Pop! (Bomb 5) + Dig In (8 block,
0 energy) + Strike = 13 block against 13 incoming, 9 bombs down, 0 damage taken.
*Rejected:* leading with a detonator. The whole plan was to bank.

**Turn 2.** Jumpy Dumpty+ (Bomb 11 → stack 17), Defend, and the **Poison Potion**
onto the Priest (6 Poison, ticking down 6/5/4/3 = free chip on a 190-HP body).
Took 16. *Rejected:* Strike (Slither) which had rolled to cost 2 — unaffordable
alongside the plant.

**Turn 3 — the tension the kit is built on, stated plainly.** At 22 HP with 17
incoming, my hand held **Dig In** and **Fwoosh!**, both marked *"CANNOT BE
PLAYED: you have no Spark, and this costs 1."* Sparks come from bombs going off;
my entire plan was to *not* set bombs off. The engine starves its own defensive
half exactly while it is winning. I played Mine Toss (mines on all three, which
do self-trigger and do pay Sparks) + Defend ×2 and took 7. *Rejected:* cashing
the Bomb 40 with Ka-pow for 43 — it would have bought Sparks and safety, and I
turned it down for the Big Badda Boom multiplier. That was the run's real
decision and I am still not certain it was right.

**Turn 4.** Priest's intent was "Empower (Buff)" — the cheap turn to stall — and
the badge read **Bomb 52**. Played **Careful Now first** (block equal to largest
bomb, capped at 10 — it reads off the stack *before* you detonate, which matters
and which the card does not spell out) and then **Big Badda Boom**: 154 → 34, a
120-damage turn. *Rejected:* holding one more turn for a Bomb 72 and a 156-point
kill shot — Big Badda Boom is not Retain, the draw pile was two cards deep, and
a coin-flip on redrawing it at 15 HP was not a bet worth taking.

**Turn 5.** Priest at 34, three attackers telegraphing 27 against my 15 HP.
Spent the **Colorless Potion**, which offered **Salvo** (12 damage, free to play
this turn). Planted Jumpy Dumpty+ + Pop! + Dodoco Cover onto the Priest (badge
**Bomb 28**), **Ka-pow!** for 32, and **Salvo** for the last 2. The Priest died,
both Followers abandoned the fight, and I never took the 27.

Boss rewards: 100 Gold, **Duplicator**, and **Alice's Recipe** ("Your Bombs grow
twice each turn") — taken over Chained Reactions, Sugar Rush and Mona, because
doubling growth is the multiplier on the one number this whole deck is trying to
make large.

---

## The kit, after 8 fights

**(a) Which decisions felt like real choices, and what they traded off.**

The kit has one excellent recurring decision and it is *when to cash the stack*.
Every turn with a bomb on the board asks: set off now for what the badge says, or
block for a turn and set off for +4 per bomb. The badge prints the exact number,
the enemy prints its intent and its damage, so the arithmetic is fully available
and still genuinely close — I got it right at Fogmog (waited to 66), got it right
at the boss turn 4 (took 120 rather than gamble on a redraw), and I am still
unsure about boss turn 3, where I refused a 43-damage Ka-pow that would also have
bought me the Sparks I spent the next turn missing.

Underneath that sits a second, quieter trade that I liked more the longer I
played: **energy and Sparks are different currencies and the good turns spend
both.** Dig In and Fwoosh! cost no energy at all, so a three-energy turn can be
five cards — but Sparks only come from bombs going off, which is the thing the
stall plan refuses to do. That is a real, self-inflicted tension and it is the
best thing in the kit.

Third: **where** to plant. Jumpy Dumpty's "place a Mine 4 on ALL enemies when it
goes off" makes a single-target bomb into an AoE detonator, so in a four-enemy
fight the question of which body to charge, and whether to spread Pop!s or stack
them, had a real answer every time.

**(b) What felt automatic, and what never seemed worth playing.**

Strike and Defend. Every turn where my hand was mostly starter cards against a
non-attacking enemy was a null turn — fight 3 turn 2, and the elite's first turn,
I spent three energy on nothing because the board wanted damage and my hand held
block. The kit's own cards never did this to me; the starters did.

Ka-pow with no bomb on the board is "0 energy, deal 4" — not bad, but it is the
kit's centrepiece doing nothing. Same for Careful Now with no bomb (0 block) and
Big Badda Boom with no bomb (12 damage for 2 energy, worse than a Strike per
energy). All three are fine cards that are simply blank until the engine is
running, which is an honest cost and I did not resent it — but it is why the
first two turns of a fight are the flattest.

The one card I could not find a use for is **Careful Arrangement** (declined
twice): "Move all your Bombs onto the enemy as one Bomb. It grows by 5." A stack
on one enemy already goes off together and the badge already sums it, so I could
not see what the consolidation buys beyond +5.

**(c) What I could not understand, or that seemed to contradict its own text.**

1. **The Jumpy Dumpty Mine rider did not appear when its bomb was stacked with
   another** (fight 3). With one bomb it fired every time (fights 1, 4, 5, 8);
   with a Jumpy Dumpty bomb and a Pop! bomb merged into "Bomb 25 / Bombs here: 2",
   the enemy came out of the detonation with no Mine badge at all. Either it did
   not fire or nothing printed that it had.
2. **A dead enemy's bombs appeared on a survivor** (elite fight). I planted Bomb
   11 on a 9-HP Wriggler; next screen it read "Bomb 36 / Bombs here: 3", and the
   surplus 21 was exactly what the Wriggler that had just died was carrying.
3. **The Mine-vs-Bomb trigger rule is legible but easy to misread.** "A Mine also
   goes off when this enemy attacks you" plus an aggregated total means a
   Bomb-21 badge can pay out 21 (both charges are Mines) or 8 (only one is), and
   the only thing distinguishing them is the clause "including 1 Mine" buried in
   the same line as the total. I got it wrong for a full turn.
4. **Careful Now's timing is unstated.** It reads off the largest bomb *at the
   moment you play it*, so playing it before a detonation gives 10 and after
   gives 0. That is a whole turn's block riding on card order and the card does
   not say so.
5. **The Wood Carvings event sells three unexplained things** (Peck, Slither,
   Toric Toughness). I bought Slither without being told it randomises the card's
   cost from 0 to 3, and hedged by putting it on a Strike.
6. **Enemy status-card intents are invisible until the card is drawn.** Enemies
   announced "intends to give you 1 Status card" perhaps eight times; the only
   evidence I ever saw was an **Infection** appearing in hand two fights later.
7. Small one: the **Spark** line disappears from the status block at 0 rather
   than printing "Spark 0", so "do I have a Spark" is answered by an absence.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

Never wanted: **Defend**. Four copies of 5 block in a deck whose real defensive
cards (Dig In at 8 for no energy, Careful Now at 10, Dodoco Cover at 5 *and* a
bomb) are all strictly better, and it was the card clogging my hand on both of
the turns where I could not answer the board.

Happiest to draw: **Big Badda Boom**, without hesitation, and specifically the
copy I drew on turn 5 of the Fogmog fight into a Bomb 66. "Set off. Deal 12
damage. Then deal damage equal to what the Bombs dealt" is a promise you can
watch getting larger on the enemy's own badge for three turns, and then it pays
in full. Honourable mention to **Dig In**, which is the card that let the stall
happen at all.

**(e) Did the first turn of the first fight already present a decision?**

Yes, and a clean one. Five cards, three energy, one enemy printing "intends to
apply a Debuff to you" — so block was visibly worthless, and the choice was
Jumpy Dumpty plus two Strikes versus three Strikes' worth of immediate damage.
Planting into an enemy with 38 HP and no incoming attack is exactly the trade the
kit is about, and the screen gave me everything needed to make it on turn one.
The kit's first *interesting* turn, though, was turn 2, when the enemy's Shrink
debuff cut my Strikes from 6 to 4 and the Bomb 12 went off for 12 anyway.

---

## Non-blindness declaration

Commands run outside the two allowed `observe` / `act` forms, all via the Bash
tool, all against my own scratch directory or the output of an allowed command:

- `mkdir -p` on the session scratchpad directory, once.
- `echo "<n>" > .../scratchpad/actcount.txt` after most `act` batches, to keep
  the running count of accepted actions against the 250 cap; and `cat` of that
  same file once, at the start.
- `sed -n '<range>p'`, `head`, `tail`, and `grep` applied **only to the stdout of
  `python -m understudy.blindplay observe`**, to re-read one block of a screen
  without reprinting the whole thing.
- `>/dev/null` on many `act` calls to suppress the JSON echo.

Tools used: **Bash** (as above) and **Write** (once, for this file). No other
tool was used. I ran no `harness state`, no `scenario`, no `staged_turn`, no
`soak`, and no understudy command other than `blindplay observe` and
`blindplay act`.

**Repo files read: none.**
