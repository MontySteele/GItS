# Blind seat — KLEEMOD-KLEE, lane 1, round 20 (targeted)

## Identity

- **Model / seat:** Opus (Claude Fable 5.1), blind TESTER seat, lane 1.
- **Run seed:** `NPSQQWA2S1ZV`. **Ascension:** 0. **Character:** Klee.
- **Act:** 1. Map named the act boss **The Kin** — not reached.
- **Actions accepted:** 119 of 120. **Termination:** action budget. Stopped
  mid-fight 6 (round 5, one enemy left at 3 HP). Wall clock was not the binding
  constraint; no refusals, no stalls.
- **Floors:** reached floor 8 (the last monster travelled to `(2,8)`).
- **HP trajectory:** 62/62 → 54/62 (fight 1) → **max HP +7 at the Byrdonis Nest
  event** → 61/69 → 58/69 (fight 2) → 58/69 (fight 3, untouched) → 45/69
  (fight 4) → 39/69 (elite) → **35/69 at stop** (fight 6 in progress).
- **Gold at stop:** 101.
- **Potions at stop (3/3):** Stable Serum, Speed Potion, Explosive Ampoule.
- **Relics at stop:** Pounding Surprise (start), Silver Crucible (Neow),
  Tungsten Rod (elite drop).
- **Deck at stop (22):** 4× Strike, 4× Defend, Jumpy Dumpty, Ka-pow!,
  *Tinder Toss, Rapid Fire, Mine Toss, Pop!, Careful Arrangement, Dig In*
  (the six targeted adds), Albedo — Solar Isotoma+, Flash Point+,
  Dodoco Cover+, Razor — Claw and Thunder, Ammo Scavenging, Albedo — Solar
  Isotoma. (Plus 3 transient `Slimed` statuses in the fight at stop.)

**Neow pick: Silver Crucible** ("The first 3 card rewards you see are Upgraded.
The first Treasure Chest you open is empty.") — my only starting relic tied
Sparks to Bomb detonations, so I judged card quality would decide the run more
than potions, and the chest penalty sat 9 floors away where I might never reach
it. (I did not; the treasure floor was never reached, so the drawback cost
nothing.) Rejected Pomander (one upgrade vs three) and Phial Holster (potions
are tempo, and I had no read yet on whether this kit was HP-starved).

---

## Fight 1 — Nibbit [A], 43 HP

**Turn 1** (3 energy, 1 Spark). Played **Jumpy Dumpty** ("Place a Bomb 8. When
it goes off, place a Mine 3 on ALL enemies") → **Tinder Toss** → Defend ×2.

Rejected: banking the Bomb 8 to grow to 12 for a bigger turn-2 set-off; and
**Dig In** (8 Block for my only Spark) instead of the two Defends. I took the
immediate detonation because the relic reads "Whenever a Bomb goes off, gain 1
Spark," and Tinder Toss sets off *twice* — so Jumpy Dumpty's bomb would go off,
place a Mine 3, and the second half would pop that Mine too: two detonations,
two Sparks, for a 1-Spark card. Net Spark-positive, which banking is not.

Outcome matched exactly: 43 → 24 (Bomb 8 + 4 + Mine 3 + 4 = **19**), Spark 1 → 2.
This is the fight's real decision and it was legible from three card faces plus
the relic, with no hidden number.

**Turn 2.** Nibbit 24 HP, telegraphing "Attack 6" *and* "Defend". Played
**Rapid Fire** then **Strike**. Rejected: three Strikes — arithmetically
identical (18 for 3 energy either way, since Rapid Fire with no Bomb under it is
just 12-for-2). I chose Rapid Fire deliberately to get a bomb-less reading of it.
24 → 6, and **Spark did not move** — the relic pays only on an actual
detonation, not on a Set off that finds nothing.

**Turn 3.** Nibbit 6 HP behind 5 Block. Played **Pop!** (Bomb 5) → **Careful
Arrangement** (→ **Bomb 10**) → **Ka-pow!**: set off 10 (5 eaten by Block, 5
through) then 4 = dead. Rejected: Strike + Ka-pow!, which reaches only 5 of the
6 HP behind that Block. This turn was a genuine puzzle — Block "stops them"
applies to Bomb hits, so I had to build a Bomb *bigger than the Block* rather
than just deal 11.

Won turn 3, 54/62.

| Fight 1 | Sparks held at end of turn | Anything go off? |
|---|---|---|
| T1 | 2 | Yes — Bomb 8, then the Mine 3 it spawned (2 detonations) |
| T2 | 2 | No — Rapid Fire found a bare body |
| T3 | 3 (fight ended) | Yes — Bomb 10 |

**Card reward:** companion **Albedo — Solar Isotoma+** offered — **TAKEN** over
Sizzle+, Tinder Toss+, Coven Errand+. A 1-cost power paying 8 damage + 4 Block +
a draw every turn an enemy wears an aura, in a deck where nearly every attack
prints `[Pyro]` and applies one.

---

## Fight 2 — Twig Slime (S) [A] 9 HP, Twig Slime (M) [B] 27 HP, Leaf Slime (S) [C] 13 HP

**Turn 1.** Played **Jumpy Dumpty on B** → **Ka-pow! on B** → **Strike A** →
**Strike C**.

The draft-level decision was made two screens earlier: Jumpy Dumpty's "Mine 3 on
ALL enemies" rider is the multi-body payoff, so B (the 27 HP body) was the right
bomb carrier purely as a *fuse*, not as a target. Rejected: Strike A twice to
kill it outright — I instead left A at exactly 3 so its own Mine 3 would kill it,
because "A Mine also goes off before this enemy's hit, which lands in full unless
the Mine kills." Leaving it at 3 killed A *and* cancelled its 4 damage, and freed
the second Strike for C.

It worked exactly: A died to its own Mine, its attack never landed, I took only
C's 3. Also learned here that **B's Mine did not fire** — B's move was a status
card, not a hit, so the Mine sat and grew 3 → 7. That is consistent with the
printed text and is a real tactical wrinkle (Mines only tax attackers).

**Turn 2.** B 15 HP + Mine 7, C 4 HP. Played **Strike C** (kill) → **Rapid
Fire**. Rejected: Rapid Fire first. The order was the whole decision — killing C
first left B as the only body, so Rapid Fire's "random enemy" could not scatter
off the Mine 7. 7 + 3 + 3 + 3 + 3 = 19 ≥ 15, exact lethal.

Won turn 2, 3 damage taken across the fight.

| Fight 2 | Sparks at end of turn | Anything go off? |
|---|---|---|
| T1 | 2 | Yes — Bomb 8 (Ka-pow!). Mines placed on all three |
| T2 | ~5 (fight ended) | Yes — A's + C's Mines on the enemy turn (+2), then B's Mine 7 via Rapid Fire |

**Card reward:** companion **Shikanoin Heizou — Heartstopper Strike+** [Anemo] —
**declined**. Swirl would have opened Elemental Reactions, but my only reaction
payoff was a minor rider. Took **Flash Point+** (1 energy, Set off, 10) over
Pocket Fireworks+ (12 flat) because Pocket Fireworks does not cash a Bomb, and
cashing Bombs is the kit.

---

## Fight 3 — Shrinker Beetle [A], 39 HP

**Turn 1.** Hand was **Defend + four Strikes**, and the intent was
"Strategic (DebuffStrong)". **This turn presented no decision at all.** Block
does nothing against a debuff intent, so the hand collapsed to "play three
Strikes." No alternative was rejected because none existed. This is the round's
clearest dead turn, and it happened because not one of the six kit cards was in
the opening hand.

**Turn 2.** The debuff landed: `Shrink -1 — While Shrinker Beetle is alive, your
Attacks deal 30% less damage.` **The card faces re-printed themselves with the
reduced numbers** — Flash Point+ now read "Deal 7 damage" (was 10) and Ka-pow!
"Deal 2" (was 4). That is excellent: the printed number was the true number, and
I could plan by adding the faces up.

And the Bomb text says "Not an Attack: only Vulnerable and a cap move it" — so
Shrink should not touch Bomb damage. That turned the debuff into a real
signpost: *under Shrink, route damage through Bombs.* Played **Mine Toss**
(Mine 4) → **Flash Point+** (set off the Mine, 4 + 7) → **Ka-pow!** (2) →
**Albedo — Solar Isotoma+**. Printed sum 4 + 7 + 2 + 8 = 21 = exactly the
Beetle's 21 HP.

Rejected: Defend (5 Block against a 7-damage hit I could instead pre-empt by
killing), and holding Albedo for a later fight. It resolved to the point —
21 → 8 off the three cards (the Mine's 4 unreduced, confirming Bombs are not
Attacks), then Albedo's 8 at end of turn killed it. **Albedo's damage was also
not reduced by Shrink.**

Won turn 2, **zero damage taken**. This was the best turn of the run and its
quality came entirely from reading two keyword boxes against each other.

| Fight 3 | Sparks at end of turn | Anything go off? |
|---|---|---|
| T1 | 1 | No |
| T2 | 2 (fight ended) | Yes — Mine 4 via Flash Point+ |

**Card reward:** companion **Lisa — Violet Arc+** [Electro] — **declined**.
Took **Dodoco Cover+** (Bomb 6 + 7 Block for 1) over Ammo Scavenging+ and
Fireworks Show+, because my deck's gap was Block and Dodoco pays both bills.

### Shop (143 gold)

Bought **Potion of Binding** (78) and **Ammo Scavenging** (24). Binding was
bought *specifically to test a printed rule* — "only Vulnerable and a cap move
it" implies Vulnerable scales Bomb damage, which nothing I owned could otherwise
check. Declined Card Removal (75), Witches' Circle, Jean, Noelle, Bang Bang!,
Pocket Match, and **Kindling** — Kindling reads "Each Bomb on an enemy whose
aura is not Pyro grows by 4," which in a deck where every set-off applies Pyro
appears to switch *itself* off. I did not buy it, so that is a reading of the
face, not a measurement.

---

## Fight 4 — Mawler [A], 72 HP

**Turn 1.** Hand: Albedo, Defend ×2, Strike, **Careful Arrangement with zero
Bombs on the board** — a completely dead card. Played Albedo → Strike → Defend.
Rejected: double Defend (72 HP body, I cannot afford a turn that develops
nothing). Albedo did *not* fire — I had no `[Pyro]` card in hand, so no aura
existed, which is a real and legible constraint on the power rather than a bug.

**Turn 2.** Mawler 66, winding up 14. Played **Mine Toss** → **Tinder Toss** →
**Ammo Scavenging** → **Flash Point+**.

The decision here was *ordering*, and it was a good one: Ammo Scavenging reads
"Draw 1 card for each of your Bombs that went off **this turn**," so playing it
*after* the detonation rather than before converted it from a plain Bomb 4 into
a Bomb 4 + a card. Rejected: Mine Toss → Ammo Scavenging → Tinder Toss, which
deals 4 more immediately (16 vs 12) but draws nothing and leaves no Bomb on the
board. The draw gave me Flash Point+, which I then spent the last energy on for
14 more. Net, the "worse" line was better by 6 damage and a Bomb.

66 → 54 → 40 (+ Albedo 8 = 32). Took 10.

**Turn 3.** Mawler 32, intent Debuff. Played Strike, Strike, **Ka-pow!**.
Rejected: Dig In / Defend — Block is dead against a debuff intent, and I wanted
to bank the Sparks. Ka-pow! was chosen over a third blocker partly because it is
`[Pyro]` and *refreshes the aura*, guaranteeing Albedo fires. Note I had **one
energy I could not spend** — a thin hand.

**Turn 4.** Mawler 8. **Rapid Fire** killed it (4 × 3, no Bomb, 1 body). Careful
Arrangement was in hand and dead **for the second time**.

Won turn 4, 13 damage taken.

| Fight 4 | Sparks at end of turn | Anything go off? |
|---|---|---|
| T1 | 1 | No |
| T2 | 2 | Yes — Mine 4 (Tinder Toss), then Bomb 4 (Flash Point+) |
| T3 | 2 | No |
| T4 | — (fight ended) | No — Rapid Fire on a bare body |

**Card reward:** companion **Razor — Claw and Thunder** [Electro] — **TAKEN**
over Careful Now, All of My Treasures!, Powder Charge. Best rate on offer (8 for
1) and it opens a second element, which would let a Bomb's Pyro hit trigger a
reaction and switch on Flash Point+'s rider.

---

## Fight 5 (ELITE) — Phrog Parasite [A], 62 HP, `Infested 4 — Upon dying, summons... something`

**Turn 1.** Intent was 3 status cards — no attack — so Block was worthless and
this was a free build turn. Played **Ammo Scavenging** (Bomb 4) → **Careful
Arrangement** (→ **Bomb 9**), holding Ka-pow! on its Retain. Rejected: setting
the Bomb off immediately with Ka-pow! for 13 — pointless on a turn that costs me
nothing, since the Bomb grows 4 at my turn start. Also rejected saving Careful
Arrangement for a hand with more Bombs: it does not Retain, so it would simply
be discarded. One energy went unspent (nothing in hand was worth playing).

Bomb 9 → **Bomb 13** at my next turn start, exactly as the growth text says.

**Turn 2.** This was the run's best-planned turn. Used **Potion of Binding**
first (Weak + Vulnerable to ALL) — the entire point of buying it — then
**Tinder Toss** → **Ka-pow!** → **Strike** → **Strike** → **Dig In** →
**Defend**.

Predicted before playing: Bomb 13 × 1.5 = 19, then two 4s at 6 each = **31**.
Observed: 62 → 31. **Vulnerable moves Bomb damage exactly as the keyword box
promises**, and Weak dropped the incoming 4×4 to 3×4. Rejected: skipping Binding
and just attacking (would have been ~21 instead of 31), and skipping Dig In to
bank Sparks — but with 13 Block against a Weakened 12 I took **zero**, and my
Spark income was about to spike anyway.

**Turn 3.** Phrog at 7, back to status cards. Played **Pop!** (Bomb 5) →
**Dodoco Cover+** (Bomb 6, +7 Block) → **Albedo+** → **Defend**, then ended the
turn so that **Albedo's end-of-turn 8 would do the killing**.

This was a deliberate read of "A kill moves them to a survivor": rather than
kill Phrog with an attack and lose the Bombs, I loaded 11 of Bomb onto a body
with 7 HP and let a *scheduled* effect kill it, betting the Bombs would ride
onto whatever Infested summoned. Rejected: Rapid Fire for a clean immediate kill,
which would have wasted both fresh Bombs.

**The bet paid.** Phrog died, four Wrigglers spawned (19/17/20/18), and
Wriggler (2) arrived wearing:

> `Bomb 19 (buff) — Set off here deals 19 Pyro damage, in 2 hits for 2 Sparks.
> Bombs here: 9 / 10, growing each turn.`

Two things worth flagging as *good*: the Bombs stayed **distinct** (my Pop! 5→9
and Dodoco 6→10 never merged — only Careful Arrangement merges), and the readout
volunteers the **hit count and the Spark yield in advance**. That single line let
me plan the next turn precisely.

**Turn 4.** Played **Mine Toss** → **Razor on B** → **Flash Point+ on C**.
Rejected: Flash Point on C first — Mine Toss adds 4 to C's pile, and C had 17 HP
against a 19 Bomb, so the Mine was pure surplus; I played it anyway because it
also lands a Mine on the other three bodies. Razor went on B specifically to
hang an **Electro** aura on it, so B's own Pyro Mine would trigger an Elemental
Reaction on the enemy turn — a reaction caused *by a Bomb*, which is what Flash
Point+'s rider asks for. C died; **its Mine moved to D**, which then read
"Mine 8 ... Bombs here: 4 / 4, including 2 Mines." Transfer confirmed a second
time.

**Turn 5.** B had died on the enemy turn (Albedo's 8 left it at 3, its own Mine 4
killed it and cancelled its attack — the Mine-kills-cancels-the-hit rule paying
off for the second time in the run). D 6 HP, E 12 HP + Mine 8. Played **Mine
Toss** (topping E to exactly 12 and giving D a Mine) → **Flash Point+ on E**
(set off 12 = lethal) → **Ka-pow! on D** (set off Mine 4, then 4 = 8 ≥ 6).
Both died. Rejected: Flash Point on D and Ka-pow on E, which kills neither.

**Elite won**, 39/69, 6 damage taken across five rounds.

| Fight 5 | Sparks at end of turn | Anything go off? |
|---|---|---|
| T1 | 1 | No — built deliberately |
| T2 | 0 (spent on Tinder Toss + Dig In) | Yes — Bomb 13 under Vulnerable |
| T3 | 0 | No — Albedo did the killing |
| T4 | 2 | Yes — C's two Bombs (19). +3 more from Mines on the enemy turn → 5 |
| T5 | — (fight ended) | Yes — E's two Mines, D's Mine |

**Card reward:** companion **Albedo — Solar Isotoma** (unupgraded second copy) —
**TAKEN**. Note the unupgraded face carries **no "Draw 1 card"**, which
retroactively confirms the upgrade adds the draw.

---

## Fight 6 — Twig Slime (M) [A] 28, Leaf Slime (M) [B] 35, Twig Slime (S) [C] 8, Leaf Slime (S) [D] 13 *(stopped on budget)*

**Turn 1.** Only C attacked. Played **Albedo+** → **Razor on C** → **Ka-pow! on
A**. Razor's 8 is exactly C's 8 HP, so the sole attacker died and I took nothing;
Ka-pow! existed only to hang a Pyro aura so Albedo had a legal target. Rejected:
Rapid Fire (2 energy, no Bombs on board, and it would not have killed C cleanly).

**Turn 2.** All three survivors now attacking for 22 total; I was at 39 with no
Block. Played **Dodoco Cover+ on A** → **Mine Toss** → **Defend**. Rejected:
swapping Defend for Strike (26 damage but 11 taken instead of 6) — with the
budget close I valued the HP line. Mine Toss taxed all three for 4 apiece
*before* they swung. Took 4.

**Turn 3.** Nobody attacking. A sat at 4 HP carrying a **Bomb 10**. Played
**Pop! on A** (→ Bomb 15) → **Strike on A** to *kill it deliberately* and
transfer the Bombs → **Strike on D**. Rejected: setting the Bomb off on A, which
would have thrown 15 of Bomb at a 4 HP body.

**The transfer split.** B took the Bomb 10 and D took the Bomb 5 — **one bomb
each to different survivors**, not both to one body. Distinct Bombs pick
survivors independently.

**Turn 4 (final, budget).** B 23 HP + Bomb 14, D 3 HP + Bomb 9. Played **Careful
Arrangement on B** → **Flash Point+ on B** → **Defend**. Careful Arrangement
pulled the Bomb **off D as well**: 14 + 9 = 23, +5 → **Bomb 28** on B, D left
bare. Flash Point+ set off 28 into a 23 HP body and killed it.

Stopped at 119/120 accepted actions with D alive at 3 HP, me at 35/69.

| Fight 6 | Sparks at end of turn | Anything go off? |
|---|---|---|
| T1 | 1 | No |
| T2 | 1 (→ 4 after the enemy turn) | Yes — three Mines, one per attacker |
| T3 | 4 | No |
| T4 | 5 | Yes — the merged Bomb 28 |

---

## Coordinator's three logging asks

### Every Tinder Toss / Rapid Fire play

| # | Card | Fight/turn | Bodies on board | Each hit's body | Bomb on it? |
|---|---|---|---|---|---|
| 1 | Tinder Toss | F1 T1 | 1 | Nibbit ×2 (set off, 4; set off, 4) | **Yes** both times — Bomb 8, then the Mine 3 that Bomb spawned |
| 2 | Rapid Fire | F1 T2 | 1 | Nibbit ×4 (3 each) | **No** — bare body, 12 flat, no Spark |
| 3 | Rapid Fire | F2 T2 | 1 (C killed first, deliberately) | Wriggler-less: Twig Slime (M) ×4 | **Yes** on hit 1 (Mine 7), bare for hits 2–4 |
| 4 | Tinder Toss | F4 T2 | 1 | Mawler ×2 | **Yes** hit 1 (Mine 4); **no** hit 2 |
| 5 | Rapid Fire | F4 T4 | 1 | Mawler ×4 | **No** — bare, 12 flat, lethal |
| 6 | Tinder Toss | F5 (elite) T2 | 1 | Phrog Parasite ×2 | **Yes** hit 1 (Bomb 13, Vulnerable → 19); **no** hit 2 |

Note: I never got to observe the "random enemy picks a Bombed enemy first" clause
under pressure — on every multi-body board I engineered it down to one legal
target first, precisely *because* the randomness was the thing I did not want to
trust. That is itself a finding: the card's random targeting made me play around
it rather than with it.

### Every hand holding Careful Arrangement

| # | Fight/turn | Played? | Bombs available | What I understood it to do |
|---|---|---|---|---|
| 1 | F1 T3 | **Played** | one Bomb 5 (Pop!) | +5 to a single Bomb → Bomb 10. Read the "grows by 5" as *immediate*, not as a change to the per-turn growth rate. Confirmed. |
| 2 | F4 T1 | **Not played** | **none** | Completely dead — nothing to move. |
| 3 | F4 T4 | **Not played** | **none** | Dead again. |
| 4 | F5 (elite) T1 | **Played** | one Bomb 4 | → Bomb 9, which grew to 13 by my next turn. |
| 5 | F6 T4 | **Played** | Bomb 14 on B, Bomb 9 on **D** | **It reaches every Bomb you own, on any body** — 14 + 9 + 5 = Bomb 28 consolidated on B, D left bare. |

**On a Mine specifically: untested.** I never once held Careful Arrangement while
a Mine was on the board, so the clause "a Mine if any of them was" got no reading
from me. What I *expected* from the face was that merging any Mine into the pile
makes the whole consolidated Bomb a Mine — i.e. it would then self-detonate
before the target's hit — which would make Careful Arrangement a *defensive*
card as well as a damage one. I cannot confirm that.

### Companion cards offered

| Offered | Where | Taken? |
|---|---|---|
| Albedo — Solar Isotoma+ | Fight 1 reward | **Yes** |
| Shikanoin Heizou — Heartstopper Strike+ [Anemo] | Fight 2 reward | No |
| Lisa — Violet Arc+ [Electro] | Fight 3 reward | No |
| Razor — Claw and Thunder [Electro] | Fight 4 reward | **Yes** |
| Albedo — Solar Isotoma (unupgraded) | Elite reward | **Yes** |
| *(shop shelf, not a reward offer)* Jean — Lion's Fang, Fair Protector | Shop | No (152g, and its "if none of your Bombs went off last turn" clause is anti-synergy) |
| *(shop shelf)* Noelle — Sweeping Time | Shop | No |

---

## The six targeted cards

- **Mine Toss** — the best of the six, played 5×. It converts every attacking
  body into a body that pays 4 and a Spark before it swings, and when the Mine
  kills, the hit is *cancelled outright*. It won fight 2's turn 1 and blunted
  fight 6's 22-damage turn.
- **Tinder Toss** — played 3×, always with a Bomb loaded, and it is close to
  self-funding: two detonations return two Sparks for its 1-Spark price. Never
  wanted it on a bare board.
- **Careful Arrangement** — played 3×, **dead in hand twice** (both times in
  fight 4, with zero Bombs on the board). At its best (fight 6) it was the most
  interesting card of the six.
- **Pop!** — played 2×. At 0 energy it is never *bad*, but its only genuinely
  clever use was as the kill-transfer payload in fight 6.
- **Rapid Fire** — played 3×, and **twice it was just a vanilla 12-for-2** on a
  bare body. It is the one of the six that most often did nothing kit-shaped.
- **Dig In** — played once (elite T2). It spends the same currency Tinder Toss
  wants, and for most of the run I would rather have had the Spark. It only
  became attractive once Mines were generating 3 Sparks a turn.

---

## The kit, after 6 fights

**(a) Which decisions felt like real choices, and what they traded off.**

The kit's live decision is *when to cash a Bomb*, and it is a genuine one because
three separate pressures pull against each other: Bombs grow 4 a turn (wait),
Pounding Surprise pays a Spark per detonation and Sparks are the fuel for the
best cards (cash early, cash *often* — many small detonations beat one big one),
and a Bomb larger than the target's remaining HP is wasted (don't overgrow).
That triangle produced a real call on most turns.

Named, by where they were made:

- **On the turn.** Fight 1 T1: detonate immediately for two detonations and a
  net Spark gain, versus banking Bomb 8 → 12. Fight 4 T2: the *ordering* choice —
  playing Ammo Scavenging after the detonation instead of before, trading 4
  immediate damage for a card and a Bomb, which paid back 6. Fight 2 T2: kill C
  first so Rapid Fire's random targeting could not scatter off the Mine.
- **Earlier in the fight.** Fight 2 T1: leaving Twig Slime (S) at exactly 3 so
  its own Mine would kill it and cancel its hit, instead of killing it with the
  second Strike. Elite T3: loading 11 of Bomb onto a 7 HP body and letting
  *Albedo's scheduled damage* kill it, so the Bombs would ride onto the summon —
  a two-turn plan whose payoff (a Bomb 19 already sitting on a fresh body) was
  set up before the summon existed. Fight 6 T3: killing my own nearly-dead
  target to relocate its Bomb.
- **At the draft.** Taking Albedo over Sizzle+ shaped every later fight — it
  killed the Beetle, killed Phrog on schedule, and was the reason the elite plan
  existed at all. Buying Potion of Binding was a draft-level bet on one printed
  sentence, and it turned a 21-damage turn into a 31-damage one.

The single best moment was fight 3 T2, where the debuff `Shrink -1` said
"your **Attacks** deal 30% less" and the Bomb keyword said "**Not an Attack**" —
so the counterplay to the debuff was legible from two boxes and worked to the
point. That is the kit at its best: the rules text is the puzzle.

**(b) What felt automatic, and what never seemed worth playing.**

- **Strikes and Defends.** Fight 3 T1 was Defend + four Strikes against a debuff
  intent: zero decisions, no alternative to reject. Fight 4 T3 was nearly the
  same. Every genuinely flat turn I had was a turn with no kit card in hand.
- **Rapid Fire on a bare board** — twice it was arithmetically identical to
  playing Strikes, and I only knew that because I did the arithmetic.
- **Careful Arrangement with no Bombs out** is not "automatic," it is *unplayable*
  — it happened twice in one fight.
- **Dig In** competed with Tinder Toss for the same scarce Spark and lost almost
  every time; 8 Block is rarely worth what Tinder Toss does with the same Spark.
- I twice had **energy I could not spend** (fight 4 T3, elite T1) — a symptom of
  a deck that is half vanilla basics.

**(c) What I could not understand, or that contradicted its own printed text.**

1. **Hexerei's Spark clause never fired, and I cannot tell why.** The keyword
   reads: "A Companion card that prints the word, and Klee herself. Some are
   Klee's own, some are not. Playing one of hers makes 1 Spark, up to 3." In
   fight 6 turn 1 I held 1 Spark, played **Albedo — Solar Isotoma+** and
   **Razor — Claw and Thunder** — both print "Hexerei" — and Spark was still 1
   on the next screen. So either neither is "one of hers," or the clause did not
   fire. **Nothing on either card face distinguishes "hers" from not-hers**, so
   as a reader I have no way to predict which companion pays a Spark. This is
   the clearest thing I could not resolve all round.
2. **"a cap" is never defined.** The Bomb keyword says twice that "only
   Vulnerable and **a cap** move it," and no screen I saw ever explained what a
   cap is. I verified the Vulnerable half; the other half is a term with no
   definition anywhere in the text I was shown.
3. **Albedo's in-play buff line drops a clause.** The upgraded card reads
   "...deal 8 damage to that enemy and gain 4 Block. **Draw 1 card.**" but the
   buff on my status line reads "...deal 8 damage to that enemy and gain 4
   Block." with no draw. Seeing the unupgraded copy later (which genuinely has no
   draw) confirms the *card* is right and the **buff readout is the incomplete
   one**. Minor, but it is the one place where two screens disagreed about the
   same effect.
4. **Flash Point+'s damage appears to vanish when its own Set off kills the
   target.** Elite T4: Wriggler (2) had 17 HP and 23 of Bomb; I set it off and
   the "Deal 10 damage" had nowhere to go. That is probably correct behaviour,
   but the card's text ("Set off. Deal 10 damage.") gives no hint that the first
   half can eat the second, and it makes overkill silently worse than it looks.
5. **`Infested 4 — Upon dying, summons... something`** is deliberately coy. It
   summoned four bodies; I *think* the 4 was the count, but the screen never
   said, and I had to commit a whole turn's plan to a rule I could not read.

**(d) The card I never wanted, and the one I was happiest to draw.**

- **Never wanted: Careful Arrangement** — not because it is weak (its fight 6
  turn was the cleverest thing I did) but because it is the only card in the deck
  that can be *literally blank*, and it was blank in 2 of the 5 hands that held
  it. A card that reads "Move all your Bombs" in a deck that also wants to
  detonate Bombs on sight is fighting its own deck for timing.
- **Happiest to draw: Flash Point+** — 1 energy, cashes any Bomb, and 10 on top.
  Every turn it appeared it was the correct play. Honourable mention to
  **Albedo — Solar Isotoma+**, which was the strongest *card* in the deck; I list
  Flash Point+ because drawing it always felt good, whereas Albedo only felt good
  on turn 1 of a long fight.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, and a good one.** Turn 1 offered Jumpy Dumpty + Tinder Toss to detonate
immediately, versus placing the Bomb and letting it grow 8 → 12, versus spending
my single Spark on Dig In's 8 Block instead of on Tinder Toss. I could work out
the right answer *from the printed faces alone* — the relic pays per detonation,
Tinder Toss sets off twice, and Jumpy Dumpty's rider creates a second thing to
detonate — and the outcome (19 damage, Spark 1 → 2) matched the prediction
exactly. That is a first turn that teaches the kit's core loop by making you
solve it.

The caveat is that fights 3 and 4 then showed the other face of the deck: when
none of the six kit cards is in hand, the turn has no decision in it at all.

---

## Non-blindness declaration

Commands run outside the two allowed ones, all via the Bash tool:

- `mkdir -p "review/qa/klee-round-20-2026-09-05"` — created the record directory.
- One failed scratch-file command: `echo "notes start" > "$TMPDIR/notes.md"`,
  which returned `Permission denied` (`$TMPDIR` was empty in that shell) and
  wrote nothing. I kept no notes file and worked from the transcript instead.
- `sed -n` and `head` filters piped over the output of
  `GITS_LANE=1 python -m understudy.blindplay observe`, to re-read one block of a
  screen without reprinting the whole thing. **One of these filters bit me:** in
  fight 1 turn 3 I cut the enemy block at `/Aura/` and concluded the board showed
  no Bomb after Pop! + Careful Arrangement; a full `observe` showed `Bomb 10`
  sitting there the whole time. That confusion was my filter, not the game's
  screen, and I record it because I briefly wrote the game down for it.

Tools used: **Bash** (the two allowed blindplay commands, plus the above), and
**Write** once, for this record.

I did not run `harness state`, `scenario`, `staged_turn`, `soak`, or any other
understudy command.

**Repo files read: none.**
