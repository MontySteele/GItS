# Klee round 10, run 4, act 2 — blind seat record

## Identity

- **Model and seat:** Opus, blind TESTER seat, KLEEMOD-KLEE, lane 2.
- **Run seed:** never printed. No screen the bridge showed me carried a seed.
- **Character:** Klee. **Act:** 2. **Boss named on the map:** Kaiser Crab — never reached.
- **Chained seat:** I inherited the deck, relics and potions from the act-1 seat and made no
  Neow pick. **Neow pick: none, inherited.**
- **Actions accepted:** 187 `act` calls. One refusal (below).
- **Termination reason:** **death, not a budget.** The final `end turn` returned
  `TOOL-BLOCKED: game_over` / "the run is over; there is nothing left to play" /
  "The run ended on floor 31." I stopped there, as instructed. Budget at stop: 187 of 250
  actions, well inside the wall clock.
- **HP trajectory:** 62/62 at the first fight (see the discrepancy note below) → 49 → 46 →
  43 (event) → 28 → rest 46 → rest 62 → 38 → 21 → 9 → 1 → dead.
- **Gold at death:** ~129 (269 at the act-2 shop, 253 spent, then +44, +35, +20, +14).
- **Potions held at death:** none. Belt was empty from the Hunter Killer fight onward.
- **Relics at the end:** Pounding Surprise, Winged Boots, Gremlin Horn, Bronze Scales,
  Juzu Bracelet, Pael's Wing, Pantograph, Lasting Candy, Unsettling Lamp.
- **Deck at the end:** I never got a full deck printout — the only list I saw was the
  card-removal screen, and it was cut off partway. From cards I actually saw drawn, played
  or listed: Strike ×4 (one carrying *Slither*), Defend ×3, Alice's Recipe, Pop! ×3,
  Mine Toss, Dodoco Cover, Jumpy Dumpty+, Careful Now, Dig In ×2, Dig In+, Fwoosh!,
  Ka-pow!, Big Badda Boom ×2, Fish-Flavored Bait, Quick Fuse, Bang Bang!,
  Ammo Scavenging, Glitterstream, Barbara — Front Row Seat, Safety Lesson+. Roughly 27
  cards. Treat this as incomplete, not authoritative.

**Discrepancy on arrival.** The coordinator told me the previous seat left the lane at
15/62. The first combat screen printed **HP 62/62**. I never saw anything that explained
the gap, and I did not go looking. Every later HP number in this record is what the screen
printed.

**Non-combat picks, one line each.**

- *Pael (Ancient), floor 1:* took **Pael's Wing** (sacrifice card rewards, a relic every 2)
  over Pael's Horn (2 unknown "Relax" cards) and Pael's Legion (doubles Block from a card,
  then sleeps 2 turns) — I had not yet seen my deck and a relic that thins beats two
  unknown cards.
- *Shop:* bought Bang Bang!, Ammo Scavenging, a Card Removal (removed the Clumsy curse),
  and a second Pop!. Rejected Ice Cream at 259 because it would have eaten the whole purse
  and left the curse and four vanilla Strike/Defends in a 26-card deck; rejected the
  Strength and Flex potions outright because the Bomb badge says only Vulnerable and a cap
  move Bomb damage, so Strength does nothing for my main damage source.
- *Slippery Bridge:* rerolled once (3 HP) rather than lose Fwoosh!, hit a Defend, took it.
  The reroll price escalated 3 → 4 HP between offers.
- *Colorful Philosophers:* **no skip was offered** — three forced foreign-class cards.
  Chose Orange (Regent) on a guess. The three rewards then turned out to be three separate
  reward screens I could decline, so I took only Glitterstream and skipped two.
- *Rest sites:* rested both times (28→46, 46→62) rather than Smith, because an Elite was
  the only exit each time.
- *Treasure:* took Lasting Candy (free relic).

---

## Fight 1 — Tunneler, 87 HP

**Turn 1.** Played **Alice's Recipe** (2) then **Mine Toss** (1).
*Rejected:* the Strike + Defend tempo line. Against a single 87 HP body with time to spare,
doubling all future Bomb growth beats 6 damage and 5 Block now.

Then, with 0 Energy left, I noticed **Fwoosh!** prices in Spark, not Energy, and played it.
It read *"Set off. Deal 6 damage"* for 1 Spark; the Mine went off for 4 and **Pounding
Surprise refunded the Spark**, so Spark stayed at 1 and I got 10 damage for free. That is
the first thing in this kit that felt like a discovery rather than an instruction.

*Learned here and never printed anywhere:* a Mine "grows at the start of your turn" but
"goes off when its enemy attacks you." Those two clocks mean a Mine can **never** grow
before the thing that detonates it. A Mine placed on an attacking enemy is always spent at
its printed size. Nothing on the screen says this; you have to derive it.

**Turn 2.** Enemy intent was Empower + Defend — no attack. Played **Pop!** (Bomb 5) and two
**Strikes**.
*Rejected:* Defend, worthless against a turn with no attack; and rejected playing **Ka-pow!**,
which *Retains*, so holding it cost nothing and banked a guaranteed detonator.

**Turn 3.** Tunneler showed Block 32 and **Burrowed** — "Stunned if all Block is removed."
Played **Pop!**, **Dodoco Cover**, **Big Badda Boom**.
*Rejected:* letting the bombs grow another turn. Growth was worth less than the stun, which
denied a 23-damage attack outright.
The arithmetic was fully predictable from the screen: bombs 13+5+4 = 22 raw, set off as
three separate hits, then BBB's 12, then *"damage equal to what the Bombs dealt"* = 22.
56 raw − 32 Block = **24 through, and 62→38 is exactly what happened.** The echo used the
bombs' **raw** total, not the amount that survived Block. Screen and outcome agreed
precisely. Spark went 1→4 (three detonations, three refunds).

**Turn 4.** Enemy at 38, stun had eaten its attack (I took 0). Played **Jumpy Dumpty+**
(Bomb 11) → **Big Badda Boom** (11+12+11 = 34, leaving 4) → **Ka-pow!**, which set off the
Mine 4 that Jumpy Dumpty leaves behind when its bomb goes off. Kill.
*Rejected:* Dig In for 8 Block — playing for the kill beats blocking 13 when the kill is
exactly on the table.

Won in 4 turns, 62 → 49.

---

## Fight 2 — three Exoskeletons, 24 / 25 / 27 HP

Every one carried **Hard To Kill 9**: "Reduce all damage taken and HP lost by Exoskeleton
to 9." This is the "cap" the Bomb glossary alludes to, and it **inverts the entire kit**:
one big bomb is worthless, many small ones are not, because *Set off* makes each Bomb a
**separate** hit and each is capped separately.

**Turn 1.** Played **Pop!** → **Ammo Scavenging** → **Big Badda Boom**, all on the 25 HP
body: bombs 5 and 4 as two capped hits (9 total), BBB's 12 capped to 9, echo 9. 27 ≥ 25.
Kill, and Gremlin Horn refunded Energy and a card.
*Rejected:* playing Ammo Scavenging *after* the detonation for its draw. Its text is
"Place a Bomb 4. Draw 1 card for each of your Bombs that went off **this turn**," which
pulls in two directions — place-before-detonation to add to the stack, or play-after to get
the draw. Here the Bomb 4 was needed for lethal, so I forfeited the draw. That tension is
the most interesting thing on the card and it recurred in every fight.

Then **Jumpy Dumpty+** and **Fwoosh!** into the 27 HP buffer.
*Rejected:* holding Jumpy Dumpty's Bomb 11 to grow. Under a 9-cap, growth is **entirely
dead** — a Bomb 11 and a Bomb 99 both hit for 9 — so the correct play is to detonate at
once, purely for the Mine spray it leaves on all enemies. Klee's central mechanic was
switched off by one enemy keyword, and the right response was the exact opposite of the
kit's instincts.

**Turn 2.** Confirmed the Mine rule from the other side: the 1×3 attacker had taken 9 from
Thorns plus 4 from its Mine — 13 — without me spending a card on it. Its Empower had
resolved into Strength 2.
No detonator in hand. Played **Careful Now**, **Dig In**, **Fish-Flavored Bait**: 16 Block
against 18 incoming.
*Rejected:* Alice's Recipe, which was in the deck and is normally the centrepiece — under
Hard To Kill its doubling does *literally nothing*, so a 2-cost Power was strictly dead.
The bomb-carrying Exoskeleton then killed itself on my Mine (8) plus Thorns (9). I took 0.

**Turn 3.** One left at 4. **Bang Bang!** finished it.

Won in 3 turns, 49 → 46. My hand on the last turn was three vanilla Defends and a
detonator, which is the first time deck bloat showed.

---

## Fight 3 (Elite) — three Decimillipede segments, 42 / 46 / 40 HP

All three had **Reattach 25** — "If other segments are still alive, revives in 2 turns with
25 HP." 24 incoming on turn 1 against 43 HP.

**Turn 1.** **Dodoco Cover** + two **Defends** — 15 Block.
*Rejected:* opening with Big Badda Boom. Reattach means damage poured into one segment is
partly refunded to them, so front-loading a single body throws it away; and eating 24
unblocked at 43 HP starts a race I lose. Took 9.

**Turn 2.** Weak 1 landed on me. Ka-pow! printed 4→3 and Strike 6→4, but the Bomb badge
still read 8. Used **Duplicator on Glitterstream** (22 Block, and the delayed half doubled
to 10 as well), then **Ka-pow!** + **Strike**.
*Rejected:* Block Potion as well — 22 Block already covered 28 incoming, and I wanted the
potion banked.
**The segment took exactly 15: the Bomb dealt its full 8 while Weak cut only Ka-pow!'s
attack half from 4 to 3.** So Weak does not touch Bomb damage, exactly as
"only their Vulnerable and a cap move it" promises. Screen and outcome agreed.

**Turn 3.** 30 incoming, no Block cards drawn, 28 HP. Committed **Dexterity Potion** +
**Dig In** + **Block Potion** for 32 Block, then dumped Pop! / Fish Bait / two Strikes into
the weakest segment.
*Rejected:* racing on damage. 89 enemy HP remained against my ~15 a turn; Thorns was
chipping 12 a turn for free, so surviving *was* the win condition and full defensive
commitment was correct. Took 0.

**Turn 4.** The turn the fight turned. 32 incoming, 28 HP, **no Block cards and no potions
left** — I was dead on board unless I removed attackers.
Played **Quick Fuse** first (Spark-priced, kills the 8 HP segment), *specifically* so that
**Ammo Scavenging** — played second — would see two Bombs already gone off and draw 2.
Then Pop! and Mine Toss to build a 13-bomb stack on the 14-damage attacker, then
**Big Badda Boom** for 35 to kill it. Gremlin Horn refunded Energy on both kills, which is
what made a 4-Energy turn possible on 3 Energy.
*Rejected:* killing the 10-damage segment instead — removing the 7×2 attacker denied more.

**Two things here I could not explain and did not go looking for:**
1. After Quick Fuse killed the 8 HP segment, a **Bomb 11 appeared on a segment I had never
   bombed**. The dying body had two bombs; one killed it and the second, size 11, seems to
   have relocated. Nothing on any screen says bombs migrate when their host dies.
2. **Pounding Surprise granted no Spark for those two detonations.** Spark went 1 → 0
   (paid 1, gained 0), where every other detonation in the run refunded 1 per bomb. Three
   detonations later in the same turn it worked normally (Spark 0 → 4). I have no account
   of the difference.

**Turn 5.** Last segment at 21 with a Bomb 24 grown on it. **Fwoosh!** for the kill.

Won in 5 turns, 43 → 28. Reward: Barbara — Front Row Seat.

---

## Fight 4 (Elite) — Entomancer, 145 HP

Intent 3×7, and **Personal Hive**: "Whenever this enemy is hit by an **Attack**, add 1
Dazed into your Draw Pile." Bombs are explicitly *not* Attacks, and **Quick Fuse is a
skill** — so Klee's whole engine walks past this keyword untouched, while Strike and the
attack-detonators each pay a Dazed. This is the best-designed interaction I met all act:
the kit's oddest rules text ("Not an Attack") suddenly became the point.

Also: 7 hits × Thorns 3 = **21 free damage a turn**, so damage was never the constraint —
Block was.

**Turn 1.** Two **Pop!**s and a **Defend**.
*Rejected:* Strike, for 6 damage and a Dazed. My binding constraint was drawing Block, and
clogging the draw pile directly attacks that. I accepted 1 idle Energy to keep the deck
clean, and I think that was right.
Thorns did exactly 21. 62 → 46.

**Turn 2.** Intent dropped to a single 18, so Thorns only returned 3 — the free income
swings hugely with the attack pattern. **Pop!**, **Dodoco Cover**, **Defend**. 38 HP.

**Turn 3.** Enemy Empowering — no attack. Bombs stood at 43 across 4.
**This was the decision of the run.** *Set off* detonates the stack, and BBB's echo is
"damage equal to what the Bombs dealt," so **Big Badda Boom must go first, on the biggest
stack** — after a Quick Fuse there is nothing left for the echo to copy.
- Order I rejected: Quick Fuse (55) then BBB on scraps (20) = 75.
- Order I played: **BBB first = 98** (43 + 12 + 43), then Bang Bang! (8), then Quick Fuse
  on the Bomb 4 it left (7), then Strike (6), then Ka-pow! (4).
121 → 23 on the first card, exactly as computed, and the fight ended on the same turn.
Ordering four detonators correctly was worth ~44 damage. That is a real skill expression
and nothing on any card tells you about it.

Won in 3 turns for 24 HP. 62 → 38.

---

## Fight 5 — Spiny Toad, 119 HP

**Turn 1.** Empower, no attack. **Dodoco Cover** + **Ammo Scavenging**, purely to seed.
*Rejected:* detonating anything on a free turn.

**Turn 2.** It gained **Thorns 5** — so every *Attack* I play costs me 5, and once again
Bombs and the skill-detonator dodge it. 23 incoming at 38 HP, no detonator in hand.
Played two **Defends** and **Pop!**.
*Rejected:* Alice's Recipe. It compounds, but 5 more Block mattered more when 23 a turn was
landing on 38 HP. *Also rejected:* Strike — 6 damage for 5 Thorns back is a losing trade,
and this is the second enemy in a row that punishes the vanilla starter cards specifically.

**Turn 3.** Bombs at 33 across 3. Played **Pop!** then **Big Badda Boom** for **88**
(116 → 28, exact). Then **Clarity Extract** to dig, then **Dig In** + **Defend**.
*Rejected:* holding BBB for a bigger stack next turn. An unplayed card goes to discard and
would not come back in time — so "save the nuke for the perfect stack" is not actually
available. That is a genuine constraint on the archetype: BBB wants a huge stack, but you
must fire it the turn you draw it.
*Rejected:* spending the retained **Ka-pow!** for 4 — Retain means holding is free and
guarantees a detonator next turn.

**Turn 4.** Empower again, free turn. **Safety Lesson+**, **Pop!**, **Mine Toss**,
**Fish-Flavored Bait**, holding Ka-pow!. Enemy 25, bombs 25 and growing.

**Turn 5.** Bombs at 25 against 21 HP, but **Thorns 5 was back**. Played **Quick Fuse** —
a *skill* — for 34. It detonates without ever "hitting," so I took **zero** Thorns where
Ka-pow! would have cost me 5.
*Rejected:* the retained Ka-pow!, which was also lethal but would have cost 5 HP at 21 HP.

Won in 5 turns, 38 → 21.

---

## Fight 6 — Hunter Killer, 121 HP

**Turn 1.** Debuff intent, no attack. **Dodoco Cover** + **Strike**.
*Rejected:* Big Badda Boom on a Bomb 4. BBB's value is proportional to the stack it
detonates; firing it on a 4 throws away the whole card.

**Turn 2.** **Tender**: "Whenever you play a card, lose 1 Strength and 1 Dexterity this
turn." So Block cards must be front-loaded. I played them in order and measured:
**Block 12 = Dig In's 8 at Dex 0 + Defend's 4 at Dex −1.** The penalty bites per card as it
resolves and does **not** retroactively strip Block already banked — worth knowing, and not
stated. I then played Pop! and Jumpy Dumpty+ *after* the Block cards, since bombs take no
Strength penalty. 21 → 16.

**Turn 3.** 7×3 = 21 into 16 HP with a single Defend in hand — exactly lethal. Used
**Clarity Extract**, drew Ammo Scavenging, and ran the combination the kit is built for:
**Ka-pow! first** (detonating 3 bombs, refunding 3 Spark via Pounding Surprise), **then
Ammo Scavenging**, which now saw 3 bombs gone off and **drew 3** — finding Dig In and
Glitterstream. Played the Block cards first (14 Block under Tender), free Pop! last.
*Rejected:* holding the 36-bomb stack for BBB's doubling (84 instead of 40). Survival
forced me to spend the stack on the weaker detonator purely to turn on Ammo Scavenging's
draw. That is the Ammo Scavenging tension again, and this time it cost me roughly 44
damage. 16 → 9.

**Turn 4.** 9 HP, 21 incoming, Block 3. Enemy at 59. I needed a kill or a near-total block,
and found a line that did both: **Barbara — Front Row Seat** applies Hydro (so the first
Pyro bomb of the detonation **Vaporizes** for 1.5×) *and* pays 3 Block per Bomb that goes
off. Then **Pop!**, then **Big Badda Boom**. The Vaporize bonus carried it past 59 and the
Toad-style backstop of 14 Block was never needed.
*Rejected:* playing BBB without Barbara first — it computed to 56 against 59, i.e. three
short. Barbara was the difference between a kill and a death.

Won, 21 → 9. **One refusal here:** my queued `play "Strike"` came back with a bare `}` and
no `ok` line, because the fight had already ended. Not a tool problem — I had queued a
fourth card that was no longer needed.

---

## Fight 7 (Elite) — Infested Prism, 161 HP — the death

The map offered **one node**: Elite. At 9/62 with no potions there was no alternative path.

The Prism carried **Vital Spark 2: "ALL Skills are Tainted 2,"** and every skill in my hand
repainted itself to read "Gain 2 Tainted."

**This is the clearest legibility defect I hit.** I looked "Tainted" up in the screen's own
glossary before committing, and it said, in full:

> **Tainted** — Gain 2 Tainted when played.

That is circular. It defines the word as the act of gaining it and never says what it does.
Only *after* I had spent three skills did the debuff row on my own status line finally tell
me:

> Tainted 6 (debuff) — Take 6 additional damage from Attacks this turn.

**Turn 1.** Played **Pop!**, **Careful Now**, **Dig In**, **Alice's Recipe** for 13 Block
against a printed 15. With the six Tainted I had unknowingly bought, it was 21. 9 → **1**.
Had the glossary said what the status row says, I would not have played **Pop!** at all —
it is a 0-cost skill that gained me **no Block and +2 damage taken**, a strictly negative
card under this keyword. I lost roughly 2 HP to a definition.

**Turn 2.** 1 HP, 11 incoming, every card in hand a skill. **Glitterstream** + **Barbara**
= 16 Block against 11 + 4 = 15. Survived by one point.
*Rejected:* the free **Pop!** — playing it would have added 2 damage for 0 Block and killed
me. A 0-cost card being actively lethal is a genuinely good tactical moment, and it only
exists because I had already paid to learn the rule.

**Turn 3.** 1 HP, Block 5, 5×3 incoming, Spark 1. Attacks and Powers are untainted, Skills
are not, so I ran **Ka-pow!** (attack, detonate for Spark) → **Ammo Scavenging** (draw) →
drew **Safety Lesson+**, a **Power**, which dodges Tainted entirely → **Bang Bang!**
(attack) to detonate into Safety Lesson's 3 Block → **Defend**.
Best reachable total: **13 Block against 15 + 4 = 19.** I worked out before ending the turn
that every available line came up short by roughly 6, and said so. It did.

`TOOL-BLOCKED: game_over` — "the run is over; there is nothing left to play. The run ended
on floor 31."

**Was it losable earlier?** Yes, and I'll name it: I took the *first* elite at 43/62 when a
safe Unknown was offered alongside it, and that elite cost me 15 HP and every potion. From
the Spiny Toad onward I was never above 38, and the map then offered no rest before a
forced elite. The kit did not kill me; the route did.

---

## The kit, after 7 fights

### (a) Which decisions felt like real choices, and what they traded off

Four kinds, and they are genuinely good:

1. **Detonator ordering.** *Set off* + "damage equal to what the Bombs dealt" means Big
   Badda Boom must fire **first**, on the largest stack. Against the Entomancer the correct
   order was worth 98 instead of 75 on one card. Nothing tells you this; you derive it from
   two lines of rules text and it feels excellent when it lands.
2. **Detonate now vs. grow.** The whole kit is a bank account. Bombs grow only on your turn,
   Alice's Recipe doubles the rate, and every enemy turn is a bet. The counter-pressure is
   real: an unplayed BBB goes to discard, so "wait for the perfect stack" is often not
   available.
3. **Which detonator, for reasons other than damage.** This is the kit's best trick. Quick
   Fuse is a *skill* and Ka-pow! is an *attack*, and three separate enemies made that
   distinction decide the turn — Personal Hive (attacks add Dazed), Spiny Toad's Thorns 5
   (attacks cost 5), Vital Spark (skills cost 2 damage taken). The same 30 damage costs a
   different price depending on the word in the card's corner.
4. **Sequencing within a turn.** Ammo Scavenging draws per Bomb that has *already* gone off,
   Barbara must precede the detonation it pays out on, Careful Now wants a big bomb alive,
   and under Tender the Block cards must be played first. Turn order mattered in five of
   seven fights.

The through-line: **Bombs are not Attacks**, so they ignore Strength, Weak and Thorns and
trip no "when hit by an Attack" clause. I verified that twice against the printed numbers
(Weak cut Ka-pow! 4→3 while the Bomb dealt its full 8). It is the most rewarding rule in
the kit.

### (b) What felt automatic, and what never seemed worth playing

- **The vanilla starter cards.** Strike and Defend were dead weight from fight 2 onward. On
  turn 3 of fight 2 my whole hand was three Defends and a detonator. Worse, three separate
  enemies punished Strike *specifically* — Dazed on attack, 5 Thorns on attack, and a
  Slither roll that made it cost 3. I never once wanted to draw one.
- **Pop!** is automatic. It's 0-cost, it does one thing, there is never a reason not to
  play it — until Vital Spark, where it silently became a card that kills you.
- **Free turns are automatic.** When the intent said Buff or Debuff, the turn played
  itself: place everything, detonate nothing. No decision at all.
- **Alice's Recipe** looked like the centrepiece and was the least useful card I owned. It
  is dead against a damage cap, dead when you detonate immediately, and it costs 2 Energy
  on exactly the turns Block is scarce. I played it twice in seven fights and it never
  clearly paid.
- **The Elemental Reaction glossary.** Six reactions are defined on every screen and a
  mono-Pyro Klee deck can trigger **none** of them — a Pyro hit on a Pyro aura just
  refreshes it. Two shop cards (Perfect Timing, Catalytic Converter) and one reward card
  (Sizzle) key off reactions and were unbuyable for that reason. The only reaction I ever
  saw fire came from Barbara, an off-class Hydro card I picked up by chance in act 2. A
  large block of always-on rules text describes a system the character cannot reach on her
  own.

### (c) What I could not understand, or that contradicted its own printed text

1. **"Tainted" is defined as itself.** The glossary says "Tainted — Gain 2 Tainted when
   played." The actual effect ("Take N additional damage from Attacks this turn") appears
   only on the status row after you have already paid. I made a strictly-losing play at
   1 HP because of it. This is the single most costly unclear thing in the run.
2. **A Bomb 11 moved to a segment I never bombed** when its host died to Quick Fuse. No
   rules text mentions bombs relocating.
3. **Pounding Surprise silently did not fire** for two detonations in that same beat —
   Spark went 1 → 0 where it should have gone 1 → 2 — then behaved normally three
   detonations later in the same turn.
4. **"Careful Now — Gain Block equal to your largest Bomb, up to 10"** is unreadable,
   because the badge only ever prints the **sum**: "Bomb 15 … Bombs here: 2." I could not
   tell whether "largest" meant 15 or the largest individual bomb, and the screen never
   shows individual sizes.
5. **The Mine's two clocks contradict in practice.** "Grows at the start of your turn" and
   "goes off when its enemy attacks you" together mean a Mine on an attacking enemy can
   never grow at all. Both halves are printed; the consequence is not, and it makes Mine
   Toss much weaker than it reads.
6. **The *Hexerei* glossary is opaque:** "A Companion card from the witches' circle. It does
   nothing by itself; Klee is one too, and her own cards pay when you play one." I read that
   several times and still cannot say what it means or what would have happened had I taken
   Alice's Introduction Magic.
7. **"Gain [star icon]"** — the Regent cards printed an unnamed resource icon, so two of
   three options in a forced reward were impossible to evaluate.
8. **Pael's Wing makes `skip` unreadable.** The bridge says outright it cannot tell whether
   the button is a plain skip or the sacrifice. I skipped three card rewards and **never
   learned** whether I banked sacrifices toward a relic. I never saw a relic arrive from it.

### (d) The card I never wanted to play, and the one I was happiest to draw

- **Never wanted:** **Strike.** Six damage in a deck whose good turns deal 98, and three
  separate enemies taxed it specifically. Its one good moment was a *Slither* roll to 0 for
  exact lethal, which is an accident, not a design. (Honourable mention: Alice's Recipe, the
  card I most wanted to *want*.)
- **Happiest to draw:** **Big Badda Boom.** It converts the bank account into a number, and
  because the echo copies the bombs' raw total it roughly doubles the whole turn. Drawing it
  with a grown stack was the only time this kit felt genuinely powerful — 98 damage in one
  card. I took the second copy over a defensive card at 21 HP and did not regret it.
  Runner-up: **Quick Fuse**, for being a *skill*, which turned out to matter three times.

### (e) Did the first turn of the first fight already present a decision?

**Yes, and a good one — but not the one on the card faces.** The face-value choice
(engine vs. tempo: Alice's Recipe + Mine Toss vs. Strike + Defend) is real but conventional.
The turn became interesting when I noticed that **Fwoosh! prices in Spark, not Energy**, so
it was still playable at 0 Energy, and that Pounding Surprise refunded the Spark the
detonation spent — making it free. Finding a fifth action on a turn I thought was over, from
reading a cost line carefully, is a strong first impression.

The caveat: I inherited a mid-run deck with Alice's Recipe, Mine Toss, Fwoosh! and a relic
already in hand. A genuine turn-1 opener would not have had that, so this is not evidence
about the kit's real opening.

---

## Non-blindness declaration

**Repo files read: none.**

I used only `GITS_LANE=2 python -m understudy.blindplay observe` and
`GITS_LANE=2 python -m understudy.blindplay act "<command>"` to drive the game. I ran no
`harness state`, `scenario`, `staged_turn`, `soak`, or any other understudy subcommand.

Commands and tools used outside the two allowed game commands, all of them scratch or
plumbing:

- **Bash tool**, for scratch only: `mkdir -p` and `echo`/`cat` on a counter file in the
  session scratchpad; a heredoc (`cat > ob.sh`) writing a small helper script into the
  scratchpad, and `sh ob.sh` to run it. That helper does nothing but pipe an `observe`
  through `awk` to hide the standing glossary block so I could re-read the state and hand
  without re-printing the same rules text every turn.
- **Text filters** applied to `observe` output only: `sed`, `awk`, `grep`, `head`, `tail`,
  and shell `for` loops used to issue several already-decided `act` calls in one go.
- **Write tool**, used once, for this record — as permitted.

Nothing I read came from the repository, the mod source, any YAML sheet, any doc, any
review material, or another seat's record. Every number, card face, keyword and glossary
line quoted above was printed to me by the bridge.

One refusal, declared: a queued `play "Strike"` at the end of the Hunter Killer fight
returned a bare `}` with no `ok` line, because the enemy had already died to the previous
card. That was my own over-queueing, not a tool failure, and it was not repeated.

Termination line, verbatim:

```
TOOL-BLOCKED: game_over

the run is over; there is nothing left to play

The run ended on floor 31.
```

I did not tear the lane down.
