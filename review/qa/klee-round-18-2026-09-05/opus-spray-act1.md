# Klee — round 18, lane 2, blind seat (targeted "spray" deck)

## Identity

- **Model / seat:** Opus, blind TESTER seat, lane 2.
- **Seed:** `PYX0CB1JAWPK`. **Ascension:** 1. **Character:** Klee (Pyro / Bomb / Spark).
- **Act:** 1. The map named the boss at the top of the act: **Soul Fysh**. I did not reach it.
- **Actions accepted:** 120 of 120.
- **Termination:** action cap. The bridge's counter hit `actions: 120 of 120` on the
  reward screen after fight 6; I stopped on the following map screen. Not a stall,
  not a refusal chain, and the run was alive and healthy at the stop.
- **Floor reached:** 12 of 16 (the map read "5 floors ahead: Boss" at the stop).
- **HP trajectory:** 62/62 start → 53 (fight 1) → 49 (fight 2) → 38 (fight 3) →
  29 (fight 4) → 21 (fight 5) → **rest, 39** → 26 (fight 6). Ended **26/62**.
- **Gold:** 149 at the stop (spent 73 on Powder Charge and 25 on Sizzle across two shops).
- **Potions held:** all 4 slots full — Skill Potion, Flex Potion, Block Potion,
  Colorless Potion. **I used none all act**, which is itself a finding: I was never
  in a spot where a potion beat a card, because the bomb engine kept turning
  lethal a turn early.
- **Relics:** Pounding Surprise (start), Phial Holster (Neow), Bag of Preparation (chest).
- **Deck at the end** (as the map printed it from the floor-12 fight, plus Careful Now
  taken after it): Amber — Fiery Rain, Bombs Away!, Careful Now, Dazed ×5, Defend ×4,
  Diona — Shaken Not Purred, Fish-Flavored Bait, Fwoosh!, Jumpy Dumpty, Ka-pow!,
  Mine Toss ×3, Pocket Match, Pop!, Powder Charge, Raiden Shogun — Musou no Hitotachi,
  Sizzle, Stoke the Fuse, Strike ×4, Tinder Toss. (The 5 Dazed are the Haunted Ship's.)

**Neow pick: Phial Holster** (1 potion slot + 2 random potions). I took it over
Kaleidoscope because two card rewards from *other* characters would dilute the one
thing I was there to read — Klee's own cards — and over Neow's Bones because a blind
curse in a deck I could not yet evaluate is a bet I could not price.

### The six targeted cards, up front

All six were in the opening hand or first shuffle and all six got played.

| card | verdict |
|---|---|
| Mine Toss ×2 | The best cards in the deck. Bought a third at the Gorge event on purpose. |
| Fwoosh! | Good, and free — aimed at a bomb it costs 1 Spark and refunds 1. |
| Pocket Match | Fine. Retain is the wrong word for what it does (see (c)). |
| Pop! | Honest 0-cost bomb; needs someone else to detonate it. |
| Tinder Toss | **The one I never wanted.** Its randomness breaks the Spark loop. |
| Fwoosh!/Pocket Match/Tinder Toss together | Too many Spark prices for one Spark income. |

---

## Fight 1 — Corpse Slug (1) [A] 27, Corpse Slug (2) [B] 26

Opening screen, opening hand: Defend, Pocket Match, Fwoosh!, Mine Toss, Tinder Toss.
Energy 3, Spark 1. Both slugs printed *Ravenous 4 — "When an enemy dies, Corpse Slug
immediately eats it, becoming Stunned and gaining 4 Strength."*

**Turn 1.** Mine Toss → Fwoosh! on A → Tinder Toss → Defend.

The decision was the *order*, and it was a real one. Four of my five cards priced
themselves in Sparks and I had exactly one Spark. Reading *Pounding Surprise —
"Whenever a Bomb goes off, gain 1 Spark"* against *Set off — "The target's Bombs go
off first"*, the inference was that a set-off card aimed at an enemy who is already
carrying a Bomb costs nothing net. So Mine Toss first (Mine 4 on both), then Fwoosh!
on A. It worked exactly as read: A went 27 → 17 (4 from the Mine, 6 from Fwoosh) and
**Spark stayed at 1**. That is a good, legible, discoverable engine and I found it on
turn one without being told.

The alternative I rejected: opening Fwoosh! on a bare slug for 6 and dropping to
Spark 0. Correctly rejected — that is what Tinder Toss then did to me anyway.

Then **Tinder Toss**, whose text is *"Set off a random enemy and deal 4 damage to it,
twice."* Both random picks landed on A, who no longer had a Bomb. So: 8 damage, **no
bomb set off, no refund, Spark 1 → 0**, and B's Mine 4 sat untouched. Pocket Match
immediately printed **`CANNOT BE PLAYED: you have no Spark, and this costs 1`**. That
is the whole finding about Tinder Toss in one screen: a card that is priced like the
rest of the Spark suite but cannot be aimed, and so cannot be part of the loop the
rest of the suite is built on. I played Defend (5 block) with 1 energy left idle and
ended the turn.

**Turn 2.** Ka-pow! on A → Strike on A (A dies) → Jumpy Dumpty on B → Pocket Match on B
→ Strike on B.

Killing A first was a genuine choice with a cost printed on the screen: Ravenous hands
the survivor **+4 Strength permanently** in exchange for **one Stun**. I took the trade
because B was the 8-damage body and a skipped turn now was worth more than a bigger hit
later; B duly came up "Intent: Stunned" with Strength 4. Rejected: grinding B down
first and leaving the 3x2 slug alive, which trades a whole extra turn of chip for nothing.

Then Jumpy Dumpty (*"Place a Bomb 8. When it goes off, place a Mine 3 on ALL enemies"*)
into Pocket Match, which set off the 8 for 8 Pyro, refunded the Spark, and planted the
Mine 3 rider. B: 22 → 9. Strike took it to 3.

**Turn 3.** The Mine had grown 3 → 7 at my turn start, exactly as the badge said
(*"growing at your turn's start"*). No set-off in hand, so I killed the 3-HP slug with
a Strike. **No rejected alternative — this turn presented no decision.** It was the
tail of a plan that had already been made, not a dead turn, but it was a turn where the
game played itself.

| turn | Sparks at end | anything go off |
|---|---|---|
| 1 | 0 | yes (A's Mine 4, via Fwoosh!) |
| 2 | 1 | yes (Bomb 8 via Pocket Match, + the Mine 3 rider) |
| 3 | 1 | no |

**Card reward:** took **Raiden Shogun — Musou no Hitotachi** (3 energy, *"Deal 20 damage.
Deals 5 additional damage for each Companion card you played this combat"*), nearly took
Sizzle. What I was looking for: **an energy sink**. Fight 1 ended with idle Energy on
two of three turns because every attack in the starting deck is priced in Sparks.
Raiden also reads Electro against a deck that paints Pyro auras on everything, and the
screen's own glossary promised *Overloaded — "Pyro on an Electro aura, or Electro on a
Pyro aura. 6 damage to ALL enemies and 1 Weak on the reacted enemy."* (Companion
offered: Raiden. Taken: yes.)

---

## Interlude — shops and the Gorge

**Shop (floor 2), 116 gold.** Bought **Powder Charge** (73g, 1 Spark → Bomb 6). Rejected
Bang Bang! at 2 Sparks, because my measured Spark income was one per bomb and a
2-Spark price is a card you cannot open on. Rejected Noelle — Sweeping Time (*damage
equal to your Block*) as a dead card in a deck whose best block card was a 5.

**Room Full of Cheese → Gorge**, choosing 2 of 8 commons. This was the most useful
screen of the round for reading the kit: Pocket Match, Fish Blasting, Coven Errand,
Tinder Toss, Long Fuse, Fish-Flavored Bait, Mine Toss, Chain Fuse. **Took Mine Toss and
Fish-Flavored Bait.** What I was looking for: cards that spend **Energy** to make
**Bombs**, because bombs are how Sparks are made, and my Energy was the idle resource.
Nearly took Long Fuse (*"Retain. Set off. Deal 6 damage. Costs 1 more each turn it stays
in your hand"*) — an energy-priced detonator, which is the hole in the deck — and passed
only because Retain plus an escalating cost is a card that punishes the exact hand-holding
the rest of the kit rewards.

**Refusal (1 of the round):** after toggling both picks I sent `confirm`, and the bridge
answered `there is nothing waiting to be confirmed`. The two toggles had already resolved
the screen. Not three in a row, so not a stop; recorded as a finding about the screen,
which gives no signal that the second toggle is also the commit.

**Shop (floor 3), 43 gold.** Bought **Sizzle** (25g, 1 energy, *"Set off. Deal 6 damage"*)
— the energy-priced detonator I had just declined at the Gorge, at a third of the price.
It went on to be the single most important card in the deck.

---

## Fight 2 — Toadpole (1) [A] 25, Toadpole (2) [B] 21

**Turn 1.** Jumpy Dumpty on A (Bomb 8) → Fish-Flavored Bait on B (4 + Bomb 4) → Tinder
Toss → Defend.

The decision, made before playing anything: **put a bomb on both bodies specifically so
Tinder Toss cannot whiff.** That is a real, kit-shaped decision — the random card stops
being random once every target is a legal target. Rejected: stacking both bombs on A for
a bigger single detonation, which is more damage but leaves the Tinder Toss coin-flip
live. Tinder Toss then hit B twice for 4 + 4 + 4 (Bomb) = 12; B went 21 → 5 and the
Spark came back.

**Turn 2** — the best-designed turn of the act, and every piece of it was a read off the
screen. A had bought *Thorns 2 — "When hit by an attack, deal 2 damage back"* and its
Bomb had grown 8 → 12; B sat at 5.

Strike on B (kill) → Powder Charge on A → Sizzle on A → Mine Toss.

- **Kill B first**, so A eats it and spends its Ravenous Stun on a turn where I am about
  to kill A anyway. Rejected: killing A first, which hands B the Strength.
- **Powder Charge before Sizzle**: adding a Bomb 6 under the existing Bomb 12 so that one
  set-off pays 18, not 12. Rejected: saving the Spark, which leaves 6 damage on the floor.
- **Sizzle rather than a Spark attack**, because *Set off* prints *"Block stops them, no
  when-hit power fires"* — bombs are not attacks and **do not wake Thorns**. Only Sizzle's
  own 6 came back at me for 2. That is a genuinely good rule and the screen taught it.
- Result: 12 + 6 + 6 = 24 into a 25-HP body. **A survived on exactly 1 HP** — I had done
  the arithmetic and knew I would be one short.
- **Mine Toss into the 1 HP**, reading *"A Mine also goes off before this enemy's hit,
  which lands in full unless the Mine kills."* The Mine killed it, so the 3x3 never landed
  and I took **zero** on the enemy turn.

That last beat is the kit at its best: a printed clause I read, believed, and got paid on.

| turn | Sparks at end | anything go off |
|---|---|---|
| 1 | 1 | yes (B's Bomb 4) |
| 2 | 2 | yes (Bomb 12 + Bomb 6 via Sizzle; then the Mine on the enemy turn) |

**Card reward:** took **Diona — Shaken, Not Purred** (1 energy, 6 Block, Cryo twice, +5
Block if a Bomb goes off), nearly took Ammo Scavenging. Looking for: **block**. Four
Defends at 5 apiece against enemies swinging 14 a turn is not a defence, and Diona also
prints *"Sparks from your Companion — Playing one of Klee's own Companions makes 1 Spark,
1 more if it triggered an Elemental Reaction."* (Companion offered: Diona. Taken: yes.)

---

## Fight 3 — Seapunk [A] 44

Single big body, hitting for 11. Hand was Strike ×3, Fwoosh!, Jumpy Dumpty.

**Turn 1.** Jumpy Dumpty (Bomb 8) → Strike → Strike → Fwoosh! (sets off the 8, +6).
26 damage; Seapunk 44 → 18; Spark back to 1; Jumpy's rider planted a Mine 3.

The decision was **detonate now or let the 8 grow to 12**. I detonated, because holding
means either not playing Fwoosh! at all or playing it for 6 into a bare body at the cost
of my only Spark — the growth is +4, the refund is worth more. Rejected explicitly and
for a reason I could state from the screen. The third Strike sat unplayable at 0 energy,
which is the *opposite* of the fight-1 problem and worth noting: this kit's energy is
either all idle or badly short, depending on which half of the deck you drew.

I also declined the **Block Potion** here against an 11-damage hit, on the read that I
would kill it next turn and would rather hold the potion for an elite. Correct, as it
turned out, though it cost me 11 HP.

**Turn 2.** Mine 3 → the enemy turn had taken it to 15. Pop! (Bomb 5) → Pocket Match
(sets off 5, +5) → Strike (6) = 16 into 15. Lethal, and the lethal was **assembled**:
a 0-cost bomb specifically to give the Spark card something to refund off. Rejected:
two Defends and a slow turn, which was pure loss with lethal on the table.

| turn | Sparks at end | anything go off |
|---|---|---|
| 1 | 1 | yes (Bomb 8 via Fwoosh!) |
| 2 | 2 | yes (Bomb 5 via Pocket Match) |

**Card reward:** took **Bombs Away!**, nearly took a second Fwoosh!. Looking for: more
energy-priced bomb placement, and specifically an AoE one, since every bomb that goes off
is a Spark and multiple bodies means multiple Sparks. (Companion offered:
**Barbara — Melody Loop**. Taken: **no** — 4 Block and an Exhaust, and the Hydro it
applies had nothing in my deck to react with.)

---

## Fight 4 — Corpse Slug ×3: [A] 26, [B] 25, [C] 27

78 HP across three bodies, ~14 incoming a turn, and I was at 38.

**Turn 1.** Mine Toss (Mine 4 on all three) → Jumpy Dumpty on B (Bomb 8) → Pocket Match
on B → Tinder Toss → Defend.

Target choice was the decision: B, because it was the 8-damage body and because Jumpy's
rider (*Mine 3 on ALL*) turns one detonation into three new bombs. Pocket Match on B set
off Mine 4 **then** Bomb 8 for 12, gave **2** Sparks, and planted Mine 3 on everyone; B
went 25 → 8. Rejected: spreading Jumpy onto the fresh 27-HP body, which is more total HP
removed but gets me hit harder while I do it.

Here the screen taught me something new and printed it clearly:
`Mine 7 (buff) — Set off here deals 7 Pyro damage. Bombs here: 4 / 3, including 2 Mines`.
Two separate mines stacked under one headline number, and setting them off paid **two**
Sparks, not one. Tinder Toss then hit a body carrying two bombs and I came out of the turn
on **Spark 4** — spent 1, gained 3. This is the first turn where the engine visibly ran
away, and it felt good.

**Turn 2 — the contradiction.** A had Pyro Aura 1; the glossary had promised Overloaded.
I played **Raiden Shogun on A**: 20 Electro into a 15-HP body wearing a Pyro aura.

A died. **Overloaded did not happen.** B was sitting on 1 HP and survived; C took nothing.
Six damage to ALL enemies would have killed B outright and been the play of the fight. The
screen said the reaction was there, the outcome says it was not. I cannot tell from any
screen whether the kill pre-empted the reaction or the reaction simply did not fire, and
nothing printed anywhere says a killing hit skips its reaction. **This is the round's
clearest screen-vs-outcome disagreement.**

The consolation was a second surprise: *one* death fed *both* survivors — B and C each
came up "Intent: Stunned" with Strength 4. Ravenous reads singular ("Corpse Slug
immediately eats it") and behaved plural. It meant I took zero damage that enemy turn,
so I am not complaining, but I could not have predicted it.

I ended that turn holding **Spark 4 and a hand of nothing but energy cards** — Strike,
Fish-Flavored Bait, Sizzle, Defend. No decision available: 0 energy, a full Spark battery,
and nothing that spends it. That is the shape of the kit's worst turn.

**Turn 3.** C's mines had grown to **Mine 23** and C intended 7x2, so the mines were going
to fire on their own. The decision: **spend a detonation on the free one, or the other
one?** I put **Fwoosh! on C** — 23 + 6 = 29 into a 27-HP body — killing it outright rather
than letting the mine fire for 23 and leaving 4 HP standing. Rejected: Fwoosh! on the
1-HP B, which kills a body that was already stunned and lets C's 23 do the work; that is
a turn slower and leaves me eating 14. Then Pop! on B (a bomb to detonate next turn) and
Diona, who paid **1 Spark for being a Companion and 1 more for the reaction** (Spark 4 → 6)
and 9 Block.

**Turn 4.** Ka-pow! (0 cost) set off the Bomb 9 into the 1-HP slug. No decision; the fight
had been decided on turn 3.

| turn | Sparks at end | anything go off |
|---|---|---|
| 1 | 4 | yes (Mine 4 + Bomb 8 + three more via Tinder Toss) |
| 2 | 4 | **no** (Raiden is not a set-off; nothing detonated all turn) |
| 3 | 6 | yes (C's two mines, 12 + 11) |
| 4 | 6 | yes (Bomb 9 via Ka-pow!) |

**Card reward:** took **Amber — Fiery Rain** (1 energy, 4 damage to ALL three times),
nearly took Perfect Timing. Looking for: **raw damage priced in Energy**. 12 damage for
1 energy in a deck whose 1-energy attacks deal 6 is not a close call. (Companion offered:
Amber. Taken: yes.)

---

## Fight 5 — Living Fog [A] 80, then Gas Bomb [B] 7

80 HP, and I walked in on 29. This is the fight the kit is built for and the fight where
it is most obviously a *kit* and not a pile of cards.

**Turn 1 — bank, detonate nothing.** Jumpy Dumpty (Bomb 8), Pop! (Bomb 5), Powder Charge
(Bomb 6), Mine Toss (Mine 4). Zero damage dealt by choice, 8 to the face taken by choice.

The rejected alternative was the tempo line — Fwoosh! for 13 + 6 on the spot — and I
rejected it on the printed clause *"grows 4 a turn"*: three bombs held one turn is +12,
which is more than the whole tempo line pays. This is the single most interesting decision
of the round and it is made entirely off card text, on turn one, at 29 HP, against a clock.

It also cost me: the Fog answered with `Smoggy 1 — You can only play 1 Skill per turn`,
which in a deck that is mostly skills is a well-aimed punish, and I dropped to 21.

**Turn 2 — the payoff, and the ordering.** The badge read `Bomb 31 — Bombs here: 12 / 9 / 10`.
I had Diona and Sizzle and one obvious question: which first?

I played **Diona first**, to put a **Cryo** aura on a Pyro-aura'd body, so that when Sizzle
set off three **Pyro** bombs the first one would land on Cryo and react. Then Sizzle.
Result: **76 → 24, fifty-two damage in one card**, Spark 1 → 6, and Diona's block came in
at 11. The reaction bonus was real and larger than Sizzle's printed "+6" — 31 + 6 + 6 = 43
against 52 actually dealt — so something in the reaction (a Melt-shaped multiplier, I
assume; the screen never named it) paid about 9 more than I could compute.

Rejected: Sizzle first and Diona for block afterwards. Same block, ~9 less damage, and I
would never have known.

**Turn 3.** The Fog summoned a **Gas Bomb** (7 HP, `Death Blow` for 8 — it hits and dies)
and sat at 15. Amber — Fiery Rain, played bare: 4 damage to all, three times. The Gas
Bomb died on the second tick and the Fog dropped to 3; Strike finished it. **Zero damage
taken.** The decision was recognising that one AoE card answers both the summon and the
boss body, rather than spending a card each. Rejected: Bombs Away! (3 to all) which does
not kill the 7-HP minion, and the Death Blow lands.

| turn | Sparks at end | anything go off |
|---|---|---|
| 1 | 0 (→1 after the Mine fired on its turn) | yes, on the enemy turn only |
| 2 | 6 (→7 after the rider Mine fired) | yes (three bombs, 12 + 9 + 10) |
| 3 | 7 | no |

I finished this fight on **7 unspent Sparks** which then evaporated (*"Gone after combat"*).

**Card reward:** took **Stoke the Fuse** (*"Spend all your Sparks. Your largest Bomb grows
by 3 per Spark spent"*), nearly took Razor — Claw and Thunder. Looking for: **a sink for
the Spark surplus**, which by this point was the deck's clearest structural problem — I had
ended two fights with 4–7 Sparks and nothing to spend them on. (Companion offered:
**Razor — Claw and Thunder**. Taken: **no**, despite being an Electro Hexerei that would
have made Sparks — I picked the fix over the synergy.)

**Chest:** Bag of Preparation. **Rest site at 21/62:** rested for 18 rather than smithing.
No decision worth the name; at 21 HP with two Elites signposted, Smith is a fantasy.

---

## Fight 6 — Haunted Ship [A] 63

Opens by handing me **5 Dazed** and a Weak 3.

**Turn 1.** Fish-Flavored Bait (4 + Bomb 4) → Strike → Strike → Pocket Match (sets off the
4, +5) → Tinder Toss (8). 33 damage, 63 → 30, and I emptied to Spark 0 on purpose.

The decision: **spend everything now, before the status cards arrive**, because the intent
line said 5 Status cards were coming and every one of them makes my draws worse. Rejected:
banking bombs as in fight 5 — the right idea against the Fog and the wrong one here,
because the Fog was punishing my *tempo* and the Ship punishes my *deck*. Same kit,
opposite correct answer, off two intent lines. That is good design.

**Turn 2.** Weak landed and the screen adjusted the card faces honestly — Fwoosh! printed
"Deal 4 damage" instead of 6 and Amber printed "3 damage to ALL enemies 3 times". Fwoosh!
also printed `CANNOT BE PLAYED: you have no Spark`. I played Mine Toss, Mine Toss, Amber:
two mines that would fire before the Ship's 13 and pay 2 Sparks, plus 9 now.

Rejected: Mine Toss + Amber + Defend, which saves 5 HP and gives up a Spark and 4 damage.
At 39 HP with the fight nearly won I took the damage. I dropped to 26.

**Turn 3 — the close.** Ship at 13, intent 4x3. Mine Toss (Mine 4) → **Stoke the Fuse**
(Mine 4 → **10**) → Strike (4, Ship → 9) → Diona (block, Cryo).

The Mine was now bigger than the Ship's remaining HP, so it fired before the Ship's hit,
killed it, and the 4x3 never landed. **Zero damage taken.** This is the same pattern as
fight 2's finish, arrived at deliberately, and it is the most satisfying thing the kit does:
the defensive play and the killing play are the same card.

| turn | Sparks at end | anything go off |
|---|---|---|
| 1 | 0 | yes (Bomb 4 via Pocket Match) |
| 2 | 0 (→2 after the two mines fired) | no during my turn; yes on the enemy turn |
| 3 | 2 (Stoke did not consume them — see (c)) | no during my turn; yes on the enemy turn (Mine 10, lethal) |

**Card reward:** took **Careful Now** (*"Retain. Gain Block equal to your largest Bomb when
played, up to 10"*), nearly took Sucrose. Looking for: **block that scales with the engine**
— my bombs pass 10 routinely, so this is a 10-block card for 1 energy in a deck whose
Defends print 5. (Companion offered: **Sucrose — Astable Anemohypostasis**, 0-cost Swirl.
Taken: **no**.) This was action 119; action 120 was the `proceed` back to the map, and I
stopped there.

---

## The kit, after 6 fights

### (a) Which decisions felt like real choices, and what they traded off

**On the turn:**
- **Fight 5, turn 1: bank or spend.** Place three bombs and deal nothing, taking 8 to the
  face, so that turn 2's single card hits for 52. That is a genuine, legible, high-stakes
  trade (tempo vs. `grows 4 a turn`) made at 29 HP with an 80-HP body in front of me. Best
  decision in the round.
- **Fight 5, turn 2: card order.** Diona before Sizzle so the Cryo aura is up when the
  Pyro bombs land, converting a detonation into a reaction. Nine extra damage for
  re-ordering two cards I was playing anyway.
- **Fight 2, turn 2: Thorns routing.** *Set off* prints "no when-hit power fires", so
  bombs go through Thorns and attacks do not. Choosing which half of the damage to lead
  with is a decision the screen taught me.
- **Fight 4, turn 3: which detonation to spend.** The 23-mine was going to fire for free
  on the enemy's own attack; spending Fwoosh! on it *anyway* converted "23 damage and a
  survivor" into "dead". Counting whether the free version is enough is a real question
  every turn there is a Mine on an attacking body.
- **Killing a body with a Mine so its hit never lands** (fights 2 and 6). Choosing to
  leave an enemy at 1–9 HP *on purpose* because the Mine will finish it before it swings
  is the kit's signature move and I made it twice on purpose.

**Earlier in the fight:**
- **Fight 2, turn 1: spreading bombs so Tinder Toss cannot whiff.** Paying tempo to
  de-randomise a random card.
- **Fight 4, turn 1: target selection for Jumpy Dumpty**, whose rider turns one detonation
  into a bomb on every body.
- **Fight 6, turn 1: spend now because the deck is about to get worse.** The mirror image
  of fight 5's banking decision, and I could name why from the intent line.

**At the draft:**
- **Buying Sizzle for 25 gold.** The starting kit has no energy-priced detonator; every
  set-off costs a Spark, so on a Spark-0 turn the bombs on the board are inert. Sizzle
  fixed the deck's one structural hole and won three fights.
- **Taking Raiden, then Amber.** Both bought purely to answer "my Energy is idle".
- **Taking Stoke the Fuse over Razor.** Answering "my Sparks have nowhere to go".
- **Taking Mine Toss at the Gorge.** Deliberately over-drafting the best card.

The draft, notably, was where the *sharpest* decisions were, because the deck arrives with
a visible economic flaw (all attacks priced in Sparks, one Spark of income) and every reward
screen is a chance to fix it a different way.

### (b) What felt automatic, and what never seemed worth playing

- **Defend.** 5 Block against 12–14 incoming. I played it as an energy dump on turns where
  nothing else was legal, never as a plan. Under Frail it printed 3. It is the least
  interesting card in the deck by a distance, and Careful Now (10 block off a bomb I already
  wanted to make) shows what it should have been.
- **Strike** is filler, but honest filler — it closed three fights as the last 6 damage,
  and in a Spark-starved hand it is the only thing you can do with Energy.
- **Tinder Toss** never seemed worth playing after fight 1. Every other Spark card lets me
  aim at a bomb and get the Spark back; Tinder Toss gambles that, and when it loses the
  next card in hand prints CANNOT BE PLAYED. I played it three times and only once was I
  glad.
- **The genuinely dead turns** were the ones where I held 4–7 Sparks and a hand of Energy
  cards (fight 4 turn 2; the end of fight 5). Nothing to decide, and a full battery
  visibly evaporating at the end of combat. Also fight 1 turn 3 and fight 4 turn 4: single
  obvious lethals, but those were plans paying off, not dead design.
- **Idle Energy in the first two turns of most fights** is the mirror complaint. The
  starting deck's attacks cost Sparks and its Energy cards are all bomb-placers and Defends,
  so turn one routinely leaves 1 energy unspent while the Spark card sits unplayable.

### (c) What I could not understand, or that contradicted its own printed text

1. **Overloaded did not fire.** Fight 4, turn 2. `Corpse Slug (1) [A] — Pyro Aura 1` +
   Raiden Shogun, `[Electro]`, on the same screen that printed *"Overloaded — Pyro on an
   Electro aura, or Electro on a Pyro aura. 6 damage to ALL enemies and 1 Weak on the
   reacted enemy."* A took 20 and died; **B stayed on 1 HP and C took nothing**. No AoE,
   no Weak. Either the kill cancelled the reaction — which nothing on any screen says — or
   it did not happen. The Elemental Reaction glossary goes out of its way to warn about a
   reaction that *looks* like it did not happen but did; this is the opposite case, and I
   have no way to tell them apart.
2. **Stoke the Fuse did not spend my Sparks.** Fight 6, turn 3. Card text: *"Spend all your
   Sparks. Your largest Bomb grows by 3 per Spark spent."* I had Spark 2. The Mine went
   4 → 10, i.e. +6, i.e. 3 × 2 Sparks — so both Sparks were counted as spent. The very next
   screen still read **`Spark 2`**. The effect billed me and the counter did not.
3. **Frail applied to Defend but not to Diona.** Same turn, fight 4: `Frail 1 — Gain 25%
   less Block from cards` was up; Defend's face had been rewritten to "Gain 3 Block"
   (from 5), while Diona still printed "Gain 4 Block ... gain 5 Block" and delivered the
   full 9. Either Diona is immune and does not say so, or her face is not being adjusted
   the way Defend's is.
4. **The stacked-Mine headline is ambiguous.** `Mine 7 (buff) — Set off here deals 7 Pyro
   damage. Bombs here: 4 / 3, including 2 Mines`. Reading only the headline I would have
   budgeted one Spark of refund and one hit; it is actually two hits and two Sparks, which
   matters enormously for whether a set-off is free. The information is in the second
   sentence but the number I plan against is in the first.
5. **Pocket Match's Retain reads as a feature and behaved as a liability.** A retained
   card I cannot pay for is not "saved for a better moment", it is a dead card occupying a
   slot; in fight 1 it sat in hand across a turn printing CANNOT BE PLAYED. Retain on a
   Spark-priced card in a Spark-starved deck is doing the opposite of what the word promises.
6. **Ravenous fed two survivors off one corpse.** *"When an enemy dies, Corpse Slug
   immediately eats it"* — one death, both remaining slugs Stunned and at Strength 4. It
   was in my favour so I am reporting it as unpredictable, not as unfair.

### (d) The card I never wanted to play, and the one I was happiest to draw

- **Never wanted: Tinder Toss.** It is priced like a member of the Spark engine and cannot
  be aimed, so it is the one card that can break the engine's only rule (aim at a bomb, get
  the Spark back). Fight 1's whiff cost me the turn and stranded Pocket Match.
- **Happiest to draw: Mine Toss** — cheap, hits everything, makes Sparks, and its damage
  arrives at the exact moment that also cancels an attack. **Sizzle** is the honourable
  mention and the card the deck could not function without; it is the only detonator that
  works on a turn when the Spark counter is at zero.

### (e) Did the first turn of the first fight already present a decision?

**Yes, and a good one.** The opening hand was Defend, Pocket Match, Fwoosh!, Mine Toss,
Tinder Toss — four cards, three of them priced in Sparks, and exactly one Spark. The
decision was whether to lead with Mine Toss so that the Spark attacks would have a bomb to
detonate and refund off, or to lead with an attack and go to Spark 0. The relic text
(*"Whenever a Bomb goes off, gain 1 Spark"*) and the Set off glossary contain everything
needed to work it out, and I worked it out and was rewarded on the same turn: Fwoosh! cost
me nothing net.

The same turn also delivered the kit's sharpest negative lesson — that the third Spark card
in hand could not be aimed and broke the loop — which is a lot of teaching for turn one.

---

## Non-blindness declaration

**Repo files read: none.**

Commands run outside the two allowed forms, all through the Bash tool:

- `mkdir -p` twice: once to create a scratch directory under the session scratchpad
  (which I then never used), once to create
  `review/qa/klee-round-18-2026-09-05/` for this record.
- `cd` into the working directory as the prefix of every command.
- `sed -n '<ranges>p'`, `grep -v`, and `tail -n` used **only** to trim the output of
  `GITS_LANE=2 python -m understudy.blindplay observe` and `... act` down to the blocks I
  needed (battle header, hand, enemy list, the last lines of an act result). No other
  source was filtered or read.
- `for c in '<command>' ...; do ... done` shell loops used to send several
  `blindplay act` calls in one Bash invocation. Every command inside those loops was one
  of the allowed `act` forms; the loop is a typing convenience, not a different interface.
- `echo ok` / `echo made` to confirm the two `mkdir`s.

Tools used: **Bash** (as above), **Write** (once, this file). No Read, no Grep, no Glob,
no Agent, no other understudy subcommand — in particular no `harness state`, `scenario`,
`staged_turn`, or `soak`. I did not look at any YAML sheet, C# source, doc, packet, or any
other seat's record, before or during the round.
