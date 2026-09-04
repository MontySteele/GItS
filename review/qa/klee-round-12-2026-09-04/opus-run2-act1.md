# Klee — blind seat, round 12, run 2, act 1

## Identity

- **Model / seat:** Opus (Claude), blind TESTER seat, lane 2 (`KLEEMOD-KLEE`).
- **Run seed:** `Y2NRXL11P8LT`
- **Character:** Klee. **Ascension:** the run opened at ascension 1.
- **Act:** 1. The map named the act boss **Soul Fysh** (16 floors ahead at floor 1).
- **Actions accepted:** 120 of 120.
- **Termination:** the action budget. I stopped mid-elite on floor 8, in the
  enemy-turn-6 position of the Phantasmal Gardener fight, with one Gardener at
  8/26 still up. Not a stall, not a refusal, not a tool block — I had zero
  refused commands all round and never saw the same screen twice running.
- **Floor reached:** 8 (Elite), of 16 to the boss. The boss was never reached.
- **HP trajectory:** 62 → 48 (fight 1) → 33 (fight 2) → 33 (fight 3, untouched)
  → 29 (fight 4) → rest to 47 → 33 (fight 5) → **9** (elite, in progress).
- **Gold:** 75 (15 + 15 + 17 + 16 + 12), never spent — no shop was on my path.
- **Potions held:** Skill Potion (1 of 3 slots), never used.
- **Relics:** Pounding Surprise (*"Whenever a Bomb goes off, gain 1 Spark"*),
  Scroll Boxes.
- **Deck at the stop (19):** Strike ×4, Defend ×4, Jumpy Dumpty, Ka-pow!,
  Fish-Flavored Bait, Sizzle, Witches' Circle, Dig In, Quick Fuse,
  Fischl — Oz, at Your Side, Big Badda Boom, Mine Toss, Pop!
- **Sparks at the stop:** 9, unspent, in a fight where I had two spark-priced
  cards in the deck. See (c).

**Neow pick: Scroll Boxes → the bundle of Fish-Flavored Bait / Sizzle /
Witches' Circle.** Blind, the one thing I could read off the two bundles was
that every card in the *other* bundle placed a Bomb and nothing in it could
make a Bomb go off, and the Bomb reminder said in as many words *"goes off only
when Set off."* I took the bundle that contained a detonator (Sizzle) rather
than the bundle that was three fuses and no match. That turned out to be an
over-cautious read — the starting deck already holds Ka-pow! and Jumpy Dumpty —
but on the printed text alone it was the only bundle that could be shown to
function by itself.

---

## Fight 1 — Seapunk 46/46 (floor 1)

**Turn 1.** Hand: Strike, Jumpy Dumpty, Defend ×3. Played **Jumpy Dumpty**
(Bomb 8) → **Strike** (6) → **Defend** (5 block). *Rejected:* Jumpy Dumpty +
two Defends, which caps the incoming 11 at 1 damage instead of 6. I paid 5 HP
for 6 damage because the bomb text says it *grows 4 a turn*, so the whole
fight's shape is "place early, hold, detonate late", and I wanted the enemy's
HP bar moving while the fuse burned. That is a real decision and the numbers
made it: 5 HP against 6 damage is close enough to be a judgement call.

**Turn 2.** Bomb read **Bomb 12** on the badge — the grow-4 rule is legible on
the enemy, not just on the card, which is good. Enemy at 40, intent 2×4.
Played **Strike ×3** (18). *Rejected:* two Strikes and a Defend. I counted:
40 − 18 = 22, and a turn-3 bomb would be 16, and Sizzle prints 6 on top of the
Set off. 16 + 6 = 22 exactly. I played for the exact lethal and gave up 5 HP of
block to get it. This is the turn of the fight I enjoyed — the arithmetic was
all on-screen and the payoff was a whole turn away.

**Turn 3.** Drew **Ka-pow!** for the first time (0 cost, Retain, Set off, 4).
Enemy intent was **Empower + Defend**, so waiting a turn would have cost me the
kill into a block. Played **Sizzle**: Set off 16, then 6. Exactly 22. Dead.
*Rejected:* Ka-pow! first, then Sizzle — same total, one more card spent, and
Ka-pow!'s Retain makes it the card you *keep*, not the one you burn.

Screen and outcome never disagreed in this fight. The bomb badge predicted its
own damage to the point.

---

## Fight 2 — Corpse Slug 25/25 + Corpse Slug 26/26 (floor 3)

Both wore **Ravenous 4** — *"When an enemy dies, Corpse Slug immediately eats
it, becoming Stunned and gaining 4 Strength."*

**Turn 1.** Hand had no bomb placer at all: Strike ×2, Sizzle, Witches' Circle,
Defend. Played **Strike, Strike, Sizzle** all into Slug (1). *Rejected:*
spreading the 18 across both, and holding Sizzle for a bomb. Sizzle with no
Bomb on the target is a 1-cost 6-damage Strike, and the "Set off" line simply
did nothing — no error, no wasted card, it just quietly resolved as a vanilla
attack. Witches' Circle was unplayable-in-practice: I owned no Hexerei card
and the reminder text does not say which of my cards are Hexerei.

**Turn 2.** Slug (1) at 7, Slug (2) at 26. Played **Ka-pow!** (free, 4) →
**Strike** (kills Slug 1). Then I *observed before committing the rest*, because
I wanted to see whether "immediately eats it, becoming Stunned" meant the
survivor skipped the turn I was still in or the next one. It read
**Intent: Stunned**, Strength 4 — so a kill on my turn buys the whole enemy
turn. That is a genuinely good interaction to discover and the screen told me
plainly. Spent the last energy on **Strike** into the survivor. *Rejected:*
Dig In for 6 block, correctly, since the stun meant zero incoming.

**Turn 3.** Survivor at 20, hitting for 12, me at 42, Frail 1 (Defend printed
**3**, not 5 — the debuff is applied to the printed number on the card face,
which is the single best legibility feature in this whole build). Played
**Jumpy Dumpty** (Bomb 8) + **Fish-Flavored Bait** (4 damage, Bomb 4) +
**Defend**. *Rejected:* double Defend for 6 block and no board. I chose to eat
9 to put 12 of fuse on the body.

**Turn 4.** Badge read **Bomb 20** (2 bombs, grown). Enemy 16. Drew **no
detonator** — hand was Jumpy Dumpty, Dig In, Strike ×2, Defend. Played
**Strike ×2** (12) into a debuff intent. *Rejected:* adding a third bomb with
Jumpy Dumpty; with the bar at 4 afterwards it would have been decoration. This
is the turn where the engine's failure mode shows: 20 points of stored damage
sat on the enemy and I could not reach it, and the correct play was to ignore
the engine and hit with basics.

**Turn 5.** Badge **Bomb 28** against a 4 HP enemy. Played **Quick Fuse**
(1 Spark, 0 energy) for a 31-point detonation into a 4 HP body. *Rejected:*
Strike, which would have done the same job with less waste. There was no
decision here at all — every card in my hand killed it. The engine's output had
outrun the fight by a factor of seven.

---

## Fight 3 — Sludge Spinner 39/39 (floor 4)

**Turn 1.** Hand: Quick Fuse (printed **CANNOT BE PLAYED: no enemy is holding a
Bomb** — an excellent, unambiguous line that I never had to guess at), Defend
×2, Fischl — Oz at Your Side, Dig In. Played **Fischl** + **Defend ×2** (10
block against an 8-damage intent). *Rejected:* Dig In for the block and holding
a Defend; I wanted the Spark banked and the block was already sufficient.

**Turn 2.** The screen changed shape and this was the best moment of the round.
Oz's 5 Electro had left **Electro Aura 1** on the Spinner, and every Pyro card
in my hand had grown a new line: ***Reaction preview: Overloaded — Pyro meets
Electro: 6 damage to ALL enemies and 1 Weak on the reacted enemy.*** I did not
have to know the reaction table; the hand told me.

Played **Jumpy Dumpty** (Bomb 8) → **Ka-pow!** (0 cost, Set off) → **Sizzle**.
The chain: bomb 8 lands as a Pyro hit on the Electro aura → Overloaded (6 to
all, Weak on it) → Ka-pow!'s 3 → Jumpy Dumpty's Mine 3 on all → Sizzle sets the
Mine off and collects its own *"If a Bomb triggered an Elemental Reaction this
turn, deal 6 additional damage"*. 39 → 6, and Spark went 1 → 3 off Pounding
Surprise. *Rejected:* Big Badda Boom, which I did not yet own, and blocking —
with the enemy at 6 and Oz reading 5 Electro into a fresh Pyro aura, I could
count another Overloaded at end of turn.

**Turn 2, end.** Ended turn on the count that Oz's 5 + Overloaded's 6 ≥ 6. It
did. Two turns, zero damage taken. This fight is what the kit is selling.

---

## Fight 4 — Corpse Slug 26 + 27 + 25 (floor 5)

**Turn 1.** Me at 33, incoming 14, hand Strike ×2 / Defend ×2 / Quick Fuse
(dead). Played **Defend, Defend, Strike**. *Rejected:* two Strikes and one
Defend. At 33 HP into 78 HP of slugs I judged I could not win the race, so I
bought HP. Nothing about this turn was interesting; it was Ironclad-basic.

**Turn 2.** Played **Fischl** → **Big Badda Boom** (12, no bombs on the board)
→ **Ka-pow!** (4) → **Dig In** (1 Spark, 6 block under Frail). *Rejected:*
Fischl + Dig In + Defend + Ka-pow!, i.e. 9 block and 4 damage. I spent Big Badda
Boom as a flat 2-cost 12 knowing it was its worst case, because I had no placer
in hand and the alternative was passing. **This is the kit's sharpest tension
and I felt it:** the payoff card is dead weight in exactly the hands where you
are behind, because the thing it multiplies is a board you only build when
you are ahead.

Oz killed a slug at end of turn; **both** survivors ate and both took Strength
4, and both were Stunned. I took **zero** damage that enemy turn. Ravenous
reads as a punishment and behaved half like a reward.

**Turn 3.** Two slugs, Strength 4 each, incoming **26** against my 29 HP, and my
only block was a Frail'd Defend for 3. The line: **Fish-Flavored Bait** (4 +
Bomb 4) → **Sizzle** (Set off 4, then 6) → **Strike** (6) = 20 into a 19 HP
slug. Kill → survivor eats → **Stunned**, and 26 damage never happened.
*Rejected:* blocking, which was arithmetically impossible, and spreading damage
to avoid feeding Strength. Killing *because* the kill stuns is a real decision
and a good one. Note the cost though: the survivor came out at **Strength 8**.

**Turn 4.** Survivor 16 HP, Strength 8, intent 11×2, **Electro Aura 1** left by
Oz. Played **Jumpy Dumpty** (Bomb 8) → **Big Badda Boom**: bomb 8 goes off as a
Pyro hit into Electro → Overloaded 6 → BBB's 12 → *"then deal damage equal to
what the Bombs dealt"* another 8. 34 into 16. Dead in two cards.
*Rejected:* Strike + Defend and surviving another turn, which loses to 22
incoming. This is the fight's answer to turn 2: the same card, two turns apart,
was worth 12 and then worth 34.

---

## Fight 5 — Punch Construct 55/55, Artifact 1 (floor 7)

**Turn 1.** Intent **Defend**. Played **Strike, Strike** (12) and then spent the
third energy on **Witches' Circle** purely as an experiment, because it had been
a dead card in my deck for four fights and its own text would not tell me which
of my cards were Hexerei. *Rejected:* Big Badda Boom + Strike for 18, which is
more damage. I bought information with 6 damage.

**Turn 2.** Construct had **Block 10** and I had Defend ×3, Sizzle, Strike.
Played **Defend, Defend**, ended. *Rejected:* Strike + Sizzle for 12 into 10
block for a net 2. The correct play was to do nothing, which is a legitimate
turn but not an interesting one.

**Turn 3.** Played **Jumpy Dumpty** (Bomb 8) → **Fish-Flavored Bait** (Bomb 4)
→ **Fischl**. The badge then read **Bomb 15 (buff) — Bombs here: 3**. Three.
8 + 4 + **3**. *Witches' Circle had fired on Fischl* — so a Companion card is a
Hexerei card, and I learned that **only by counting bombs on the enemy badge**,
because Fischl's own face never prints the word Hexerei. Then **Quick Fuse**
(1 Spark, free of energy): each bomb +3, set off → 11 + 7 + 6 = 24. 39 → 15.
*Rejected:* letting the bombs grow another turn for +12 while eating a 14. With
Oz about to put Electro on a Pyro-aura'd body I could count the Overloaded.

End of turn: Oz 5 + Overloaded 6 → 4 HP; then its own attack set off the Mine 3
Jumpy Dumpty had scattered → 1 HP. Four separate systems (bomb, mine, companion,
reaction) each did the thing their card said.

**Turn 4.** **Ka-pow!** for 4 into 1 HP. No decision; anything killed it.

---

## Fight 6 — ELITE: Phantasmal Gardener 29 + 26 + 30 + 28 (floor 8)

All four wore **Skittish 6** — *"The first time Phantasmal Gardener is hit each
turn, it gains 6 Block."* I went in at 33/62, which was my own bad call: the
same map floor offered a RestSite and I took the elite for the harder read.

**Turn 1.** Played **Big Badda Boom** (12, boardless again) into Gardener (3),
**Ka-pow!** (4) into a *different* Gardener so its first-hit block would not eat
it, **Defend** + **Dig In** for 13 against a 15 intent. *Rejected:* Ka-pow! on
the BBB target, which Skittish would have swallowed whole. Skittish is a clean
puzzle and the kit has an answer for it; I just did not have the answer in hand.

**Turn 2.** Played **Mine Toss** (Mine 4 on ALL) + **Defend ×2**. *Rejected:*
Strikes, which feed 6 block each. Mine Toss is the right card into four bodies:
three of the four mines detonated on their own attacks for 4 apiece. **But note
what it did not do:** the mine goes off *"before the hit lands"* and still took
none of the damage off me — I ate the full 17. The card reads defensive and is
not.

**Turn 3.** The clearest mechanical finding of the round. Gardener (1) held a
**Mine 8** (grown from 4, because it Empowered instead of attacking — the badge
tracked that correctly). I played **Jumpy Dumpty** (Bomb 8) then **Quick Fuse**
(+3 each, Set off): 11 and 11, resolved *one at a time*, into a body with
Skittish 6 waiting. Result: **25 → 3**. Twenty-two damage. **Neither bomb hit
was reduced by 6, and no Block ever appeared on the badge** — so Set off damage
ignores the enemy's Block *and* does not trip a "first time it is hit"
trigger. The Bomb keyword's *"Not an Attack: only Vulnerable and a cap move it"*
does say this if you read it as exhaustive, but it says it by omission, and
"Not an Attack" is not the same sentence as "ignores Block". I had to run the
experiment to know.

Then **Strike** finished the 3 HP Gardener — and *that* hit was not reduced
either, which means the bombs had already spent Skittish for the turn, or
Skittish does not fire on a lethal. I could not tell which from the screen.

**Turn 4.** Three left (19/14/18), me at 17 against 16 incoming. Played
**Pop!** (0 cost, Bomb 5) → **Sizzle** (Set off 7 + 5, then 6) to kill the
14 HP one and delete its 7 from the intent, then **Fischl** (Oz's 5 Electro
into a Pyro aura → Overloaded, 6 to *all*) and **Defend**. *Rejected:* pure
block, which caps at 5 and loses; and Strike, which Skittish eats. Killing to
reduce incoming, using the free-cost placer as detonation fuel, and taking the
AoE reaction as a fourth-order effect of a card that prints none of that — this
was the best turn I played all round and every input was on a card face.

**Turn 5 (budget).** Two left (13/7), me at 16. **Big Badda Boom** into the
7 HP body to kill it deterministically, then **end turn** — action 120.
*Rejected:* BBB into the 13 to leave it on 1 and gamble on Oz's random target.
Stopped at 9/62 with one Gardener on 8/26.

---

## The kit, after 6 fights

**(a) Which decisions felt like real choices, and what they traded off.**

Three kinds, and all three are good.

1. **When to cash the fuse.** A Bomb grows 4 a turn and does nothing until Set
   off, so every turn asks "another 4, or now?" — paid for in HP taken while you
   wait. Fight 1 turn 2 (count to an exact 22 lethal two turns out) and fight 5
   turn 3 (detonate 24 now rather than 36 next turn) were both genuinely close.
2. **Kill-order against a death trigger.** Ravenous and Skittish both make
   *which* body you hit, and whether you finish it, the whole turn. Fight 4
   turn 3 — kill the 19 HP slug specifically because the survivor's Stun eats a
   26-damage turn, at the price of it coming out at Strength 8 — is the single
   best decision the kit offered me.
3. **Two currencies that don't convert.** Energy and Sparks are separate pools,
   and the cards that cost Sparks (Quick Fuse, Dig In, Powder Charge, Tinder
   Toss) are *off-budget*: a Quick Fuse detonation on two bombs costs 1 Spark
   and Pounding Surprise hands 2 back. Turns where I had both a Spark card and
   three energy had noticeably more in them than turns where I did not.

**(b) What felt automatic, and what never seemed worth playing.**

- **Strike and Defend.** Four of each, and against Block-gaining or
  Skittish enemies they are actively bad. Every turn where my hand was basics
  was a turn with no decision in it — fight 4 turn 1 and fight 5 turn 2 had no
  rejected alternative worth the name.
- **Overkill detonations.** Fight 2 turn 5: a 28-point bomb into a 4 HP slug.
  The engine's stored damage outran the fight and the card choice stopped
  mattering. That happened twice.
- **Witches' Circle was a dead card for four fights**, and only because a card
  reward happened to offer me a Companion did it ever do anything. A Power
  whose enabler is a card type you may own zero of is a mulligan in a starter
  bundle.
- **Big Badda Boom on an empty board** is a 2-cost 12, i.e. two Strikes for two
  energy. Not unplayable, just conspicuously the wrong card at the wrong time —
  and the times it is wrong are the times you are losing.

**(c) What I could not understand, or that contradicted its own printed text.**

1. **Nothing on a Companion card says it is Hexerei.** Fischl — Oz, at Your Side
   prints its effect and nothing else. Witches' Circle says *"Whenever you play
   a Hexerei card"* and the glossary says Hexerei is *"A Companion card from the
   witches' circle"* — "from the witches' circle" is doing silent work, because
   I could not tell from any card face whether *my* Companion qualified. I found
   out by counting bombs on an enemy badge. Later, Noelle's card printed a
   different keyword again — *"Sparks from your Companion — Playing one of
   Klee's own Companions makes 1 Spark"* — so there is apparently a distinction
   between "Companion", "Hexerei", and "Klee's own Companion", and none of the
   three cards involved prints which one it is.
2. **Set off ignores enemy Block, and no card says so.** Two 11-point bombs
   both landed at full value into Skittish 6 (fight 6 turn 3). The Bomb keyword
   says *"Not an Attack: only Vulnerable and a cap move it"*, which I now read as
   meaning this, but "not an Attack" plainly did not stop it from *hitting*
   (Skittish did not fire), and a rule this load-bearing against a whole class of
   enemy should not be an inference from a negative.
3. **The Elemental Reaction glossary entry is four times the length of any card
   on the screen**, including a paragraph in capitals about a relic-driven case
   that cannot arise in a starting deck. Meanwhile the thing I actually needed —
   whether *my* bomb's Pyro hit counts as the reacting hit for Sizzle's bonus —
   is not in it. (It does; I inferred it from a damage total.)
4. **Sparks pile up with nowhere to go.** I ended the elite on **9 Sparks**.
   The resource has no cap, does not carry between fights, and my two sinks cost
   1 each. For most of the run the relic that grants Sparks was generating a
   currency I could not spend.
5. **Mine reads defensive and is not.** *"goes off when its enemy attacks you,
   before the hit lands"* strongly implies interception. It does not reduce the
   incoming hit by anything; it just deals damage first. Mine Toss into four
   attackers still cost me a full 17.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted:** *Witches' Circle*. Dead for four fights, and when it finally
  fired it made a Bomb 3 — 3 — on a random enemy. Runner-up: *Strike*, which
  three of the six fights punished me for playing.
- **Happiest to draw:** *Quick Fuse*. It costs no energy, it turns the whole
  stored board into damage, Pounding Surprise refunds most of its price, and it
  is the card that made "should I wait another turn" a question worth asking.
  Honourable mention to *Ka-pow!* — 0 cost, Retain, Set off — which is the card
  that quietly makes the bomb plan safe to commit to.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, and a real one.** Hand was Strike / Jumpy Dumpty / Defend ×3 against a
46 HP Seapunk telegraphing 11. Jumpy Dumpty places a fuse that pays two turns
later; the third energy was a straight 5 HP for 6 damage trade, and I could
count both sides of it off the screen. It is not a *deep* decision — it is
"tempo or armour" — but it is a decision, it was legible on turn one with zero
prior knowledge of the kit, and the Bomb reminder text told me exactly why the
early placement mattered. That is more than most opening hands manage.

---

## Non-blindness declaration

- **My model family is Opus (Claude). The kit's author is a different Claude
  model.** I have not seen this kit before this round.
- **Repo files read: none.**
- Commands run outside `blindplay observe` / `blindplay act`:
  - `python -m understudy.embark --character KLEEMOD-KLEE --lane 2` — the
    embark, once, as the coordinator instructed. Its output gave me the seed,
    the lane, the floor and the ascension, and nothing about the kit.
  - `mkdir -p <scratchpad>/klee-r12-run2` — created once, never written to.
    No notes file was kept; this record was written from the transcript.
  - `cd "C:/Users/Monty/Documents/GitHub/GItS"` as a prefix on Bash calls, and
    shell `for` loops chaining several `act` calls in one invocation.
  - `head`, `tail`, `sed -n` used to trim `observe` and `act` output for
    reading. On several observes I passed two overlapping `sed` ranges, which
    printed the enemy block twice — that duplication in my reading is my shell,
    not the game.
- Tools used: **Bash** (all of the above) and **Write** (once, this file).
- I ran no `harness state`, no `scenario`, no `staged_turn`, no `soak`, and no
  other understudy subcommand. No pilot recommendation was ever displayed to me.
- Zero refused commands across 120 accepted actions. No `TOOL-BLOCKED` screen.
