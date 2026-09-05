# Blind seat record — KLEEMOD-KLEE, lane 2, natural draft, Act 1

## Identity

- **Model / seat:** Opus (Claude Fable 5.1 subagent), blind TESTER seat, lane 2.
- **Run seed:** `812HKEALVT9P`. **Character:** KLEEMOD-KLEE. **Ascension:** 1.
- **Act:** 1. The map named the act boss as **Waterfall Giant** from the first
  map screen onward.
- **Actions accepted:** 117 of 120.
- **Termination:** action budget. I stopped standing on the map at floor 9 with
  three accepted acts left; the only node offered was `Monster (path 1)`, and
  three acts cannot open and play a combat. I did not start it. No refusals, no
  stalls, no `TOOL-BLOCKED` screen at any point.
- **HP trajectory:** 62 → 54 → 53 (fight 1) → 47 → 46 (fights 2–3) → 46 (fight 4,
  zero damage taken) → rested to 62 → 53 → 51 (elite). **Ended 51/62.**
- **Gold:** 195. **Potions:** Radiant Tincture, Dexterity Potion (Strength Potion
  spent in fight 4).
- **Relics:** Pounding Surprise (start), Hefty Tablet, Book of Five Rings.
- **Deck at the last fight read (floor 8):** Alice's Recipe, Bombs Away!,
  Defend ×4, Dig In, Fischl — Oz at Your Side, Grounded, Jumpy Dumpty, Ka-pow!,
  Strike ×4. Rapid Fire was taken after that fight and so is not in that list.
  Injury (from Hefty Tablet) was removed at the Doors of Light and Dark event.
- **Floors played:** Monster, Unknown (Doors of Light and Dark), Monster,
  Monster, Monster, RestSite, Elite. Five fights, one event, one rest, one elite.

**Neow pick: Hefty Tablet** — "Choose 1 of 3 Rare cards to add to your Deck. Add
1 Injury to your Deck." I took it over Precise Scissors (remove 1) and Scroll
Boxes (a pack) because a Rare is the fastest way to see what the kit's ceiling
actually is, and one unplayable curse at A1 is affordable — a bet that paid off
twice, since the very next event let me remove the Injury for free.

**The rare I chose: Alice's Recipe** ("Your Bombs grow twice each turn") over
The Big One (cost 3, "Set off for quadruple damage") and Sugar Rush (2 Sparks,
2 Energy + draw, Exhaust). I reasoned that a growth multiplier improves every
Bomb the deck will ever place, where The Big One is one button. The risk I
took knowingly: at that moment I had not yet seen a single card that could
*Set off* a Bomb, and the Bomb keyword says a Bomb "goes off only when Set off,
or as a Mine." If the base deck had contained no detonator, Alice's Recipe
would have been a blank and the kit would have been broken. Ka-pow! showed up
on turn 2 of fight 1 and settled it.

---

## Fight 1 — Sludge Spinner [A], HP 39/39

**Opening hand:** Jumpy Dumpty, Strike, Defend, Strike, Strike.
**Bomb-placing card in hand:** yes — Jumpy Dumpty, and it is **Innate**, so it
is in the opening hand of every fight by construction.

**Turn 1.** Played Jumpy Dumpty on A ("Place a Bomb 8. When it goes off, place a
Mine 3 on ALL enemies"), then Strike, Strike. **Why:** the Bomb grows 4 a turn
and only pays when set off, so the earliest possible placement is the largest
possible payoff — placing it turn one is the whole point of the card.
**Rejected:** opening Defend + two Strikes and holding Jumpy Dumpty. Rejected
because a held placer is a turn of growth thrown away, and against a 39 HP body
with an 8-damage intent I could afford the 8.

*This is the answer to (e) below in miniature: the first turn of the first fight
did present a decision, but a shallow one. With three Strikes, a Defend and an
Innate placer, the placer is obviously first and the only live question was
whether the last two energy went to damage or block.*

**Turn 2** (HP 54, Weak 1 on me from the Spinner's debuff). Hand: Defend ×2,
Injury, Strike, **Ka-pow!** ("cost 0, attack. Retain. Set off. Deal 3 damage" —
the 3 was 4 reduced by my own Weak; it printed 4 the next turn). Enemy showed
`Bomb 12`, having grown from 8.

Played Ka-pow! on A (Bomb 12 + 4 = 15, exact: 27 → 12), then Strike, then
Defend, Defend. **Why:** I had first talked myself into *holding* Ka-pow! —
it Retains, so waiting costs nothing and the Bomb would be 16 next turn — and
then noticed the hand was three Defends and a Strike, i.e. only 3 energy of
things to spend anyway. Ka-pow! costs **0**. Holding it bought a bigger Bomb
but cost nothing else, so playing it was strictly free damage on top of a full
turn. **The rejected alternative was the wrong analysis, and noticing that is
the decision.** That the card is 0-cost *and* Retain removes almost all the
tension it looks like it has.

Jumpy Dumpty's rider fired: Mine 3 landed on A. The screen then printed the
Mine's own rule — "A Mine also goes off before this enemy's hit, which lands in
full unless the Mine kills."

**Turn 3.** A at 5 (the Mine had gone off for 3 during its turn). Played Strike
for the kill. **Rejected:** Ka-pow! (4) — one short of lethal on 5 HP. No real
decision; this was the plan from turn 2 paying off.

**Spark at end of fight: 3, spent on nothing.** I had one Spark at combat start
and Pounding Surprise ("Whenever a Bomb goes off, gain 1 Spark") added two. My
deck at that point contained no card with a Spark price, so the entire resource
was decorative for the whole fight. This is the single clearest thing the first
fight taught me and it taught it by absence.

**Verdict:** one real decision (turn 2's hold-or-spend, which dissolved on
inspection), one plan paying off. Draft-level, not turn-level.

---

## Fight 2 — Corpse Slug (1) [A] 26/26, Corpse Slug (2) [B] 27/27

Both carried `Ravenous 4` — "When an enemy dies, Corpse Slug immediately eats
it, becoming Stunned and gaining 4 Strength."

**Opening hand:** Jumpy Dumpty, Strike, Strike, Ka-pow!, Defend.
**Bomb-placing card in hand:** yes (Jumpy Dumpty, Innate).

**Turn 1.** Jumpy Dumpty on A, then Strike, Strike into A. **Why:** concentrate
on one body so that the Bomb's eventual detonation is also the kill, which
turns Ravenous from a threat into a tempo gift. **Rejected:** splitting the
Strikes onto B to keep both bodies even — rejected precisely because Ravenous
rewards a clean, chosen kill order and punishes a race.

**Turn 2.** A at 14 with `Bomb 12`; B untouched at 27; I had Frail 2, so Defend
printed 3 instead of 5. Played **Ka-pow! on A**: 12 + 4 = 16 into a 14 HP body.
**Why:** killing A did three things at once — it denied A's 6-damage attack, it
placed Mine 3 on B via Jumpy Dumpty's rider, and it triggered Ravenous so B ate
A and was **Stunned**, denying B's 8 as well. **Rejected:** holding Ka-pow! to
grow the Bomb to 16 — rejected because the Bomb was already lethal and a turn
of growth was worth less than two denied attacks.

The result was better than I had modelled, and the screen explained why in
words I had read but not connected: B showed `Mine 6 ... Bomb sizes here: 3 / 3,
including 2 Mines`. **The Mine 3 that had been on A moved to B when A died** —
the Bomb keyword's "Kills move it on." I had read that line four times without
realising it applied to Mines placed by a rider.

Spent the rest on Strike, Strike into B (27 → 15).

**Turn 3.** B at 15, `Mine 14` (7 / 7 — the Mines had grown while B was stunned
and therefore never hit), intent 12. Played Strike (B → 9), then **Dig In**
("cost 1 Spark. Gain 6 Block" — 8 reduced by Frail). **Why:** 14 of Mine into a
9 HP body was lethal before its hit landed, and Dig In was pure insurance
bought with a Spark I would otherwise have thrown away at end of combat. That
insurance calculus is the first moment Sparks meant anything.
**Rejected:** ending the turn on the Strike alone to save the action — rejected
because the Spark was free and being wrong about the Mine would have cost 12.

The Mines killed B before it hit. **Fight taken for 6 HP total.**

**Spark at end of fight: 2 held, 1 spent on Dig In.**

**Verdict:** the best fight of the round for decisions, and all of them were
*on the turn*: which body to kill, when to detonate, and whether to buy
insurance with a resource that expires.

---

## Fight 3 — Seapunk [A], HP 45/45

**Opening hand:** Jumpy Dumpty, Defend, Strike, Defend, Ka-pow!.
**Bomb-placing card in hand:** yes (Jumpy Dumpty, Innate).

**Turn 1.** Jumpy Dumpty on A, Defend, Defend. **Why:** 45 HP with an 11-damage
intent is a long fight, and against a long fight the Bomb wants turns more than
the enemy wants to be Struck for 6. **Rejected:** Jumpy Dumpty + Strike +
Defend — the trade was 6 damage now against 5 HP of mine, and against a body
this size I judged the Bomb's compounding worth more than the Strike.

**Turn 2.** Enemy `Bomb 12`, intent 2×4. Played **Alice's Recipe**, then Strike,
then Dig In (8 Block, exactly the 8 incoming). **Why:** the enemy's turn was
2 damage four times, which Dig In eats entirely for a Spark, freeing all three
energy — so the 2-cost Power cost me nothing defensively. That is the cleanest
"the Spark economy bought me a tempo turn" moment in the round.
**Rejected:** Ka-pow! for 12 + 4 = 16 now. Rejected because Alice's Recipe
turns every later turn of growth from +4 into +8, and I had a free turn to
install it.

**Turn 3.** The Bomb read `Bomb 20` — Alice's Recipe visibly paid (+8, not +4).
Enemy intent was Empower + Defensive, i.e. **no attack**. Played
**Fischl — Oz, at Your Side**, then a second Jumpy Dumpty, then Strike.
**Why:** a turn where nothing is incoming is a turn to install engines; and
`Set off` says "Block stops them", so detonating into a body that is *about to
gain Block* is the worst timing available. **Rejected:** setting off for 20 + 4
right then, before the Block landed. This was the closest decision of the
fight and I want to record that I was not sure: the printed rule cuts both ways
(its Block is up during my next turn too), and I gambled that two more Bombs
growing at 8 each would outrun whatever Block a single Defensive intent buys.

**Turn 4.** The gamble paid, visibly and in printed text. The board read
`Bomb 44 ... Bomb sizes here: 28 / 16` against `HP 28/45, Block 7`, and
Ka-pow! itself now carried a line it had never printed before:

> *Reaction preview: Overloaded* — Pyro meets Electro: 6 damage to ALL enemies
> and 1 Weak on the reacted enemy.

Oz's Electro hit at the end of turn 3 had left `Electro Aura 1` on the body, and
the card face told me — unprompted, on the card, before I committed — exactly
what my Pyro would do to it. Played Ka-pow!. 44 through 7 Block, plus 4, plus
the Overload, killed it outright.

**Spark at end of fight: 0 held; 1 spent on Dig In (turn 2).**

**Verdict:** two real decisions, both *earlier in the fight* rather than on the
turn — install Alice's Recipe on the free turn, and refuse to detonate into an
incoming Block. The kill itself was a plan paying off, not a dead turn.

---

## Fight 4 — Corpse Slug (1) [A] 25, Corpse Slug (2) [B] 26, Corpse Slug (3) [C] 27

Three bodies, all `Ravenous 4`. 78 HP total, 14 incoming on turn 1.

**Opening hand:** Jumpy Dumpty, Ka-pow!, Strike, Strike, Defend.
**Bomb-placing card in hand:** yes (Jumpy Dumpty, Innate).

**Turn 1.** Jumpy Dumpty on A → **Ka-pow! on A immediately** → Strike, Strike
into A. **Why:** this is the reverse of every other fight and it is the fight's
one real draft-shaped decision. With three bodies, Jumpy Dumpty's rider is not
a footnote — "place a Mine 3 on ALL enemies" is three Mines, each of which
grows and then fires *on that enemy's own turn*, outside my energy entirely.
Detonating an 8 immediately, at its smallest, to buy that spread was worth more
than growing one Bomb on one body. **Rejected:** the line I had played in every
previous fight — hold Ka-pow!, let the single Bomb reach 20+. Rejected because
against three bodies the rider is the card.

Ended with A on 1 HP and Mine 3 on all three, deliberately: A's own Mine would
fire before A's hit and kill it. **Rejected:** spending the last energy on
Defend for 5 Block instead of the Strike that set that up.

It worked, and the payoff was larger than I predicted. A died to its own Mine,
which meant A's attack never landed; **both** survivors ate A, so both were
Stunned and neither of their attacks landed either. **I took 0 damage on a turn
that had 14 incoming.**

**Turn 2.** B and C at full, Mine 7 each, Strength 4 each, C intending 7×2.
Dig In (8) + Defend + Defend (18 Block) + Strike into C. Took 0 again.
**Rejected:** a third Defend over the Strike — 18 Block already covered the 14.

**Turn 3.** B on 26 with `Mine 11`, C on 14, both Strength 4, 26 incoming, and
**no Defend in hand** — hand was Fischl, Grounded, Strike, Alice's Recipe,
Ka-pow!. This was the hardest turn of the round. I could block almost nothing,
so I looked for a kill instead: killing C would Stun B and zero the turn.

C was on 14. Ka-pow! (4) + Strike (6) = 10. Four short. So I spent the
**Strength Potion** (+2 Strength, "Adds its amount to every Attack hit"),
making it 6 + 8 = **exactly 14**. C died, B ate it, B was Stunned, and the
26 incoming became 0.
**Rejected:** playing Grounded + Fischl + Strike and eating 26 to 20 HP. The
potion was worth more than 26 HP and I was never going to find a better turn
for it. Then spent the freed energy on Grounded and Fischl.

**Turn 4.** Grounded had paid on schedule — the buff line reads
`Grounded 6 — This turn a Bomb was on the field: paid 6 Block and 1 Spark`,
which is unusually good status text: it says what it did *and why it was
allowed to*. B on 19 with `Mine 15`. Strike (8, with the potion's Strength) put
B on 11; Oz's end-of-turn hit did **7**, not 5 — Strength applies to Oz — and
the Mine 15 finished it before its 11×2 could land.

**Fight taken for 0 HP. Four turns, 78 enemy HP, no damage received.**

**Spark at end of fight: 4 held, 1 spent on Dig In (turn 2).** Sparks
accumulated faster than the one Spark-priced card in my deck could spend them.

**Verdict:** the round's best fight. Real decisions at every level — a draft
decision (Bombs Away!/placer scarcity, see below), an on-the-turn reversal of
my own detonation habit, and a genuinely tight lethal-arithmetic turn.

---

## Fight 5 (Elite) — Skulking Colony [A], HP 75/75

The reason to record this fight in full is one line on the enemy:

> **Hardened Shell 20 of 20 left this turn** — Skulking Colony cannot lose more
> than 20 HP each turn.

And the Bomb keyword, which I had been reading past for five floors:
"Not an Attack: only **Vulnerable and a cap on the enemy's HP loss** move it."
This elite is built specifically to punish the one-enormous-Bomb plan the rest
of the kit teaches. That is good design and it is *legible in advance* — the
counter is printed on the keyword before you ever meet the enemy.

**Opening hand:** Jumpy Dumpty, Bombs Away!, Defend, Strike, Defend.
**Bomb-placing card in hand:** yes — two of them, Jumpy Dumpty (Innate) and
Bombs Away!.

**Turn 1.** Jumpy Dumpty, Bombs Away! ("Deal 3 damage to ALL enemies. Place a
Bomb 2 on ALL enemies"), Defend. **Why:** against a 20/turn cap, one big Bomb is
a waste and what I want is a *rate*. Two Bombs growing is closer to a rate.
**Rejected:** Strike for 6 — under a cap, raw single-target Strike damage is the
least valuable thing in the hand. Took 9.

**Turn 2.** Grounded + Fischl + Dig In + Defend, 13 Block against 14. **Why:**
no detonator in hand, so the turn was for installing the two engines and paying
for them with a Spark. **Rejected:** Strike instead of Defend, for 6 damage at
the cost of 5 HP. Took 1.

**Turn 3.** Board: `Bomb 26 ... 12 / 6`, enemy 61, cap full. Set off with
Ka-pow!. The board then read **`Hardened Shell 0 of 20 left this turn`** and
61 → 41 — exactly 20, with 10 of Bomb and all 4 of Ka-pow!'s own damage
silently eaten. The screen showing the *remaining* cap, and updating it, is the
clearest single piece of feedback in this kit. **Rejected:** waiting a turn for
`34`, which would have wasted 14 instead of 10; and rejected Strikes after the
detonation, since the cap was visibly at 0 and further damage was provably
worthless. Spent the freed energy on Alice's Recipe + Defend and took 0.

**Turn 4 — the fight's one genuine trap, and I walked into it.** The status
line read:

> **Grounded 6** — No Bomb on the field this turn, so nothing was paid. It pays
> at the start of the next turn one is standing.

Setting off *every* Bomb on turn 3 left the field bare, and Grounded — my
6 Block and 1 Spark a turn — paid nothing. **The kit's two halves want opposite
things: Grounded pays you for leaving Bombs standing, and every detonator you
own clears the field.** That is a real, legible tension and I like it; I record
it as a trap only because I did not see it coming, not because the text hid it.
Replayed Jumpy Dumpty to re-arm Grounded, plus Defend, Defend. Took 8.
**Rejected:** Strike over the second Defend.

**Turn 5.** Enemy on 27 with `Bomb 16` **and no detonator in my hand**. Strike,
Strike, Dig In, Defend — 19 Block against 16, took 0, enemy to 10 after Oz.
This turn is the clearest statement of the deck's structural flaw: a 16-point
Bomb sat on the board doing nothing because my whole deck contains exactly
**one** card that can set it off. There was no decision here; there was an
absence.

**Turn 6.** Drew Ka-pow!, set off `Bomb 24` into a 10 HP body. Dead.

**Elite taken for 11 HP (62 → 51), six turns.**

**Spark at end of fight: 5 held, 2 spent on Dig In.** Again the resource
outran the sinks.

**Verdict:** a fight whose decisions were almost entirely *at the draft* — one
detonator, one Spark sink, no way to raise my damage rate under a cap. The
per-turn play was mostly forced. But the fight was interesting anyway, because
the cap forced me to think about damage as a rate for the first time, and
because the Grounded-versus-detonation tension is a real choice the kit will
keep asking.

---

## The kit, after 5 fights

**(a) Which decisions felt like real choices, and what they traded off.**

- **When to set off — on the turn, every fight.** This is the kit's spine and it
  is a good one. A Bomb grows 4 a turn (8 with Alice's Recipe) and pays nothing
  until you spend it, so every turn is "cash it or let it ride." What made it a
  real decision rather than a treadmill is that the printed rules give the
  *enemy* a vote: `Set off` says "Block stops them," so an incoming Defensive
  intent is a reason to detonate early (fight 3, turn 3, where I chose the
  opposite and had to argue myself into it); Hardened Shell's cap is a reason
  to detonate *often and small* rather than once and huge (fight 5); and three
  bodies plus Jumpy Dumpty's Mine rider is a reason to detonate an 8 at its
  smallest size (fight 4, turn 1). Three different fights pushed the same
  decision three different ways. That is the best thing about this kit.
- **Kill order against Ravenous — on the turn, fights 2 and 4.** "When an enemy
  dies, Corpse Slug immediately eats it, becoming Stunned" turns a kill into a
  denied turn, and Bombs "move on" to a survivor on a kill, so choosing *which*
  body dies decides both the damage and the incoming. Fight 4 turn 3 — spending
  a Strength Potion to make 6 + 8 hit exactly 14 and zero out 26 incoming — was
  the most satisfying turn of the round.
- **Whether to buy insurance with a Spark — on the turn, fights 2 and 5.**
  Sparks vanish at end of combat, so an unspent Spark is a wasted one, and
  Dig In lets you convert them into Block *without energy*. That is a genuinely
  good little decision, and the only thing wrong with it is that I had exactly
  one card that could make it.
- **Grounded versus detonation — at the draft, felt on the turn (fight 5).**
  Grounded pays 6 Block and 1 Spark "if you have a Bomb on the field"; every
  detonator clears the field. Picking Grounded up put a real, recurring tension
  into the deck.
- **Rest versus Smith — at the rest site.** 16 HP against one upgrade, before an
  Elite, at 46/62 after three fights that cost 1, 0 and 0 HP. I took Rest and I
  am still not certain it was right; the last two fights had suggested my
  defensive floor was high enough that the upgrade would have compounded more.

**(b) What felt automatic, and what never seemed worth playing.**

- **Jumpy Dumpty on turn one is not a decision, it is a ritual.** It is Innate,
  so it is in hand every single fight, and it is the only unconditional way to
  start the engine. In five fights I opened with it five times and never once
  considered anything else. The rider ("Mine 3 on ALL enemies") is what makes
  the *detonation* interesting, but the *placement* is automatic.
- **Ka-pow! is less of a decision than it looks.** It costs **0** and it
  **Retains**. Both of those, together, delete the cost of holding it and most
  of the cost of playing it, so it is almost never wrong to play it the moment
  the Bomb is worth more than the enemy's next Block. I talked myself through
  "hold or spend" in fight 1 and then realised the question was empty.
- **Strike and Defend are what you play when the kit has stopped asking you
  anything.** Under the elite's cap, Strike was provably worthless on any turn
  the Bomb had already filled the 20.
- **Nothing in my deck was never worth playing** — but that is partly because I
  removed the only card that qualified (Injury) at the first event.

**(c) What I could not understand, or that seemed to contradict its own text.**

1. **A card-reward face referred to a rule its own subject does not print.**
   *Kaeya — Cold-Blooded Strike* reads "Deal 8 damage. Apply Cryo. **This turn,
   Grounded counts nothing as having gone off.**" But *Grounded*, on the very
   same screen, reads "At the start of your turn, **if you have a Bomb on the
   field**, gain 6 Block and 1 Spark." Grounded's own text has no notion of
   anything "going off"; it is a field check. One of those two faces is
   describing a different version of Grounded. This is the one place in the
   round where two printed texts could not both be true, and I did not take
   Kaeya, so I could not test which one the game actually runs. **Flagging it
   as the single highest-value legibility defect I saw.**
2. **"Kills move it on" is doing much more work than its five words suggest.**
   It governs Mines placed by a rider, not just Bombs you aimed. In fight 2 the
   Mine on A migrated to B on A's death and doubled B's Mine — a swing I did
   not predict from the text, though the text does technically cover it.
3. **Strength silently applies to Oz.** Fischl's face says "Oz deals 5 Electro
   damage"; with Strength 2 he dealt 7. Correct, presumably, but nothing on
   either face says a Companion's hit is *your* Attack for Strength purposes.
4. **The Spark counter has no printed ceiling and no printed sinks.** "no cap"
   is stated; what a Spark is *for* is discoverable only by drafting a card
   that prices in them. I finished three of five fights holding 3, 4 and 5
   unspent Sparks. See finding 2 below.
5. **Minor, and it did not cost me anything:** Ka-pow! printed "Deal 3 damage"
   on a turn I wore Weak 1 and "Deal 4 damage" the turn after. That is correct
   behaviour (the face shows the real number), but for a blind reader it briefly
   looks like the card changed.

Everything else I met was clearer than I expected. The *Reaction preview* line —
"Pyro meets Electro: 6 damage to ALL enemies and 1 Weak" — appearing on the card
face only once the target actually wore a reactable aura is excellent design:
it teaches the reaction system exactly when the teaching is actionable. The
`Hardened Shell 20 of 20 left this turn` → `0 of 20 left this turn` counter is
the other standout.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted:** *Strike*. Four copies of "Deal 6 damage" in a deck whose
  actual damage arrives in lumps of 20 and 44, and which met an elite that caps
  HP loss at 20 a turn. On several turns a Strike was provably worth zero.
  (*Injury* was worse, but it is a curse, so it does not count.)
- **Happiest to draw:** *Dig In* — "cost 1 Spark. Gain 8 Block." It costs **no
  energy**, so it does not compete with anything; it turns a resource that
  otherwise evaporates into the thing I always needed; and it is the reason
  fights 2, 3 and 4 cost me 6, 1 and 0 HP. The close runner-up is *Grounded*,
  for the same reason plus the tension it introduces.

**(e) Did the first turn of the first fight already present a decision?**

**Partly — and the honest answer is "one and a half."** The hand was Jumpy
Dumpty, three Strikes and a Defend. Jumpy Dumpty is Innate and is the only
engine starter, so playing it first was not a choice; the choice was what the
remaining two energy did, and "two Strikes or one Strike and a Defend" against a
39 HP body with an 8-damage intent is a real but very small question. The kit's
actual first decision arrived on **turn 2**, when Ka-pow! appeared and the
question became *when* to cash a Bomb — and even that one dissolved once I
noticed Ka-pow! costs 0 and Retains.

Compare fight 4, where turn 1 was a genuinely interesting decision (detonate an
8 at its smallest to spread three Mines, versus grow one Bomb) — the difference
is that the *board* had three bodies. **The kit's turn-one decision quality is
supplied by the enemy layout, not by the opening hand.** With one enemy, turn
one is a ritual.

---

## Three highest-value findings

1. **The deck ships with one detonator and the whole kit is downstream of it.**
   Ka-pow! was the only card in fourteen that could `Set off`. On elite turn 5 a
   `Bomb 16` sat on the board doing nothing, and there was no decision to make,
   only a card to wait for. The Bomb engine's payoff is gated on a single copy
   while its *placer* (Jumpy Dumpty) is Innate and guaranteed. That asymmetry is
   backwards: the guaranteed half is the boring half. I corrected it at the
   first opportunity by drafting Rapid Fire, but four card rewards passed before
   one was offered that I judged worth the slot over an engine piece.
2. **Sparks generate faster than anything can spend them.** Pounding Surprise
   grants one per Bomb that goes off, combats start with one, Grounded adds one
   a turn, and the whole resource is deleted at end of combat. I ended fights
   holding 3, 4 and 5 unspent. For the first entire fight the counter was
   decorative — it ticked up and nothing in my deck could read it. A resource
   whose default state is "wasted" reads as noise until the draft happens to fix
   it, and the fix is one uncommon.
3. **Hardened Shell is the best thing that happened to this kit in five fights,
   and its counter-play is printed in advance.** The Bomb keyword warns that "a
   cap on the enemy's HP loss" moves Bomb damage; Skulking Colony caps HP loss
   at 20 a turn and displays the remaining budget live. It converted the whole
   kit from "stack one enormous number" into "manage a damage *rate*," which is
   a much more interesting problem, and it did so without a single surprise —
   I could read the counter, see 10 points of Bomb evaporate, and adjust. More
   enemies that argue with the Bomb's shape rather than its size would make the
   detonation decision live in every fight rather than in every third one.
   The natural companion to this is the **Grounded-versus-detonation tension**
   discovered on elite turn 4: emptying the field to deal damage switches off
   the card that was paying for your defence.

---

## Non-blindness declaration

**Repo files read: none.**

- **Tools used:** `Read` (once, for my own brief at
  `…\scratchpad\brief-klee-l2.md`, which is not a repo file), `Bash`, and
  `Write` (once, for this record).
- **Commands run outside the two allowed ones:** exactly one —
  `mkdir -p "C:/Users/Monty/Documents/GitHub/GItS/review/qa/klee-round-21-2026-09-06"`,
  to create the record directory the coordinator named, which was missing.
  (Declared as the coordinator asked.)
- **Every other Bash call** was either
  `GITS_LANE=2 python -m understudy.blindplay observe` or
  `GITS_LANE=2 python -m understudy.blindplay act "<command>"`, both run with a
  leading `cd` into the working directory the coordinator gave me. Several
  `observe` calls were piped through `sed`, `grep` or `head` to re-read one
  block of the screen I had already been shown; those filters read only the
  tool's own stdout and no file. Two calls combined one `act` with a following
  `observe` in a single shell line (`act 'proceed' && observe`); no shell call
  ever contained two `act` invocations.
- **I ran no other `understudy` subcommand** — no `harness state`, no
  `scenario`, no `staged_turn`, no `soak`.
- **Refusals:** none. No command I issued was rejected, so there is no refusal
  to report as a finding.
