# Kokomi — blind seat, round 23, lane 1

## Identity

- **Model / seat:** Opus (Claude), blind TESTER seat, lane 1 (`GITS_LANE=1`).
- **Run seed:** none printed. No screen I saw carried a seed.
- **Character:** Kokomi (never named on a screen as such; identified only by the
  relic **Tamakushi Casket** and the Bake-Kurage jellyfish that the combat
  screens are built around).
- **Ascension:** **no screen printed an ascension number.** The first combat
  opened at **64/80 HP**, i.e. 80% of max rather than full, which is the only
  evidence on the point.
- **Act / boss:** Act 1. The map named the act's boss: **The Kin**. Never reached.
- **Actions accepted:** **113 of 120.**
- **Termination:** **action budget.** I stopped at 113 with 7 actions left,
  because no further combat could be started and finished inside 7 accepted
  acts, and I was at 22/80 HP. Wall clock was not close to 5400 s. Not a stall,
  not a refusal cascade, no `TOOL-BLOCKED` screen was ever hit.
- **HP trajectory:** 64/80 (opened) → 61 → 50 (after fight 1) → 41 (fight 2)
  → 36 (fight 3) → 32 (fight 4) → 31 (fight 5) → **rest +24 → 55** → 42 → 22
  (after the Elite). Ended **22/80**.
- **Gold:** 253.
- **Potions held at the end:** Clarity Extract; Attack Potion. (A Poison Potion
  was drawn and spent in fight 4.)
- **Relics at the end:** Tamakushi Casket, Lead Paperweight, Nunchaku,
  Ripple Basin.
- **Deck at the end (≈25 cards).** *Caveat: no screen ever printed a full deck
  list — the map page says outright "the deck is on a fight's data feed and no
  fight of this run has been read," and it never became available afterwards.
  This list is reconstructed from cards I actually saw in hand plus every card
  I added.*
  - Basics: Strike ×4, Defend ×4 (I saw `Strike (1)/(2)/(3)` and
    `Defend (1)/(2)/(3)` simultaneously in hand, so at least 3 of each; the
    17-card opening count implies 4).
  - Kit cards present from the start: Slack Water, Kurage's Oath,
    Sea-Salt Prayer, Ebb Tide, Battle Plan, Undertow, Deep Current,
    Exposed Flank. **Eight** kit cards were in the opening 17 — six of them
    were the granted cards for this round, but nothing on any screen marks
    which, and I could not tell the two base cards from the six grants.
  - Added in play: Volley (Neow), Kaeya — Frostgnaw (f1), Opening Gambit (f2),
    Ambush (f3), Tide Wall (f4), Read the Field (f5), Nereid's Ascension
    (Elite), Ripple + Vanguard (event).

**Neow pick: Lead Paperweight** ("Choose 1 of 2 Colorless cards"). I took it
because it was the only one of the three that led to a further decision rather
than a flat number, and because its own row carried a printed defect worth
probing — the screen said *"this option's own words promise a card and the feed
carried no face for it — no rules text, no cost, no type — so this page can
offer it by name only."* Offered Volley vs Purity, **I took Volley** (cost X,
10 damage X times) because an X-cost attack would tell me what the kit's energy
curve actually supports; it went on to close three of the six fights.

---

## Fight 1 — Fuzzy Wurm Crawler, 57 HP

**Turn 1** (3 energy). Played **Slack Water** on A, then **Kurage's Oath** onto
the **Bake-Kurage** as a Plan, then **Strike**.
*Rejected:* three Strikes for a flat 18. I rejected it because I wanted to read
two unknowns rather than maximise turn-one damage — whether the relic clause
"whenever you apply a debuff to an enemy, it deals 2 Hydro damage" actually
fires off a card's own rider, and what a Plan costs versus what it pays. Both
answered: Slack Water printed *"Deal 4 damage. Apply 1 Weak"* and the enemy went
57→51, i.e. **6 = 4 + 2**, and the intent fell 4→3 from the Weak. Real decision,
made on the turn.

**Turn 2.** Enemy intent was **Empower (Buff)**, no attack. Hand was
Sea-Salt Prayer + three Defends + Ebb Tide. Played **Sea-Salt Prayer** only and
ended with 2 energy unspent.
*Rejected:* playing Defends. Block reads *"Until next turn, prevents damage"*
and the enemy was not attacking, so every Defend in hand was literally worth
zero. **Ebb Tide** (*"Cancel every Plan. Gain 1 Energy and draw 1 card for
each"*) was also dead — I had no Plans written, so it was a 1-energy card that
does nothing. This turn presented a decision only in the negative sense: the
hand offered five cards and four of them were unplayable-for-value.

**Turn 3.** Enemy had buffed to **Strength 7** and swung to 11. Played
**Volley** at X=3 for **30** (36→6).
*Rejected:* Undertow + Deep Current + Defend (13 damage, 5 block), which would
have taken one fewer point of damage that turn but left the enemy at 23 and
risked a third 11-damage hit. Decision made on the turn, but the option only
existed because of the **draft** pick at Neow.

**Turn 4.** Killed with **Strike** into exactly 6 HP.
*Rejected:* Deep Current, which also killed. No decision — this was the Volley
turn paying off, not a dead turn.

**A refusal, and it was a good one.** `play "Volley" on "A"` was refused with:
*"'Volley' does its own aiming, so it takes no `on \"A\"`. The form that
resolves: play \"Volley\""*. That is exactly the right shape of refusal — it
named the working form and cost me one action, not a round.

**Screen vs outcome:** agreed everywhere except one thing. Volley carries **no
element tag**, yet after it resolved the enemy's **Hydro Aura went 1 → 2**. A
colourless card appears to have refreshed a Hydro aura. See (c).

---

## Fight 2 — Nibbit, 42 HP

**Turn 1** (3 energy). Played **Exposed Flank** → **Slack Water** → **Deep
Current**, deliberately in that order.
*Rejected:* the same three cards in any other order, and a Defend line. This was
the fight's real decision and it was about **sequencing, not selection**: put
Vulnerable down first and everything behind it scales. It paid twice over, and
one of the two was a surprise — Exposed Flank alone took the enemy 42→**39**,
which means the **relic's 2 damage was itself boosted to 3 by the Vulnerable
that the same card had just applied**. Then Slack Water and Deep Current landed
9 each (39→21, exactly the predicted 18). 21 damage off 3 energy.

**Turn 2.** Enemy at 21, intent read *"Attack for 6, one part of this move"*
**and also** *"Defensive (Defend) — this part adds Block… the feed carries no
number for how much."* Played **Sea-Salt Prayer** → **Undertow** → **Strike**
(21→3).
*Rejected:* writing a Plan. Rejected specifically because the Bake-Kurage panel
prints *"A Plan is carried out before you play anything, so it lands in whatever
Block the enemy is still standing in from its own turn — you cannot strip that
Block first."* Against a Defend intent that makes Plans strictly worse than
playing now. I also played Sea-Salt Prayer **first** so its Weak would make
Undertow's *"If the enemy has a debuff, deal 10 instead"* live. Decision on the
turn, and the screen told me how to make it.

**Turn 3.** Enemy at 3 behind 5 Block. Played **Kaeya — Frostgnaw** (8 damage)
for exactly lethal through the Block.
*Rejected:* Strike (6 − 5 Block = 1, not lethal) and Volley X=3 (works, but
wastes the X card and its first hit is eaten by Block). Real decision, made on
the turn, and made easy by the Block number being printed. Fight ended taking
**zero damage in its last two turns**.

Notable: on this turn Kaeya had grown a new line — ***"Reaction preview:
Frozen — Hydro meets Cryo"*** — that had not been there when the enemy was
bare. The card face tells you the reaction before you commit. That is the single
best piece of legibility in the kit.

---

## Fight 3 — Shrinker Beetle, 40 HP

**Turn 1.** Intent was **Strategic (DebuffStrong)**, no damage. Wrote
**Kurage's Oath** as a Plan (7 vs the 3 it deals now) and played **Undertow**;
left 1 energy unspent.
*Rejected:* playing Oath now for 3, and playing a Defend. Both rejected for the
same reason — with no incoming damage the turn is free, so banking the bigger
number costs nothing. Decision on the turn.

**Turn 2 — the most interesting screen of the round.** The Beetle had applied
**Shrink -1**: *"While Shrinker Beetle is alive, you deal 30% less damage with
every hit you land, a Skill's damage too."* Two things happened at once:

1. **Every card face in my hand reprinted itself at the reduced number.** Strike
   showed *"Deal 4 damage"* not 6; Slack Water *"Deal 2"* not 4; Opening Gambit
   *"Deal 3"* not 5. I did not have to do the arithmetic. This is excellent.
2. **The planned Kurage's Oath landed for the full 7, not 4.9.** The enemy went
   40→26, which is Undertow 7 + Oath 7, both undiminished.

So **Plans route around your own damage debuffs**, because the Plan panel says
*"Every planned HIT is the jellyfish's."* That is consistent with the printed
text, but it is buried, and the payoff is large: under Shrink the correct play
is to push damage through the jellyfish. I only found it by reading the HP
delta and being surprised.

Played **Opening Gambit** as a Plan, **Slack Water** direct, **Strike** direct.
*Rejected:* three direct cards (all Shrunk), and writing Slack Water's Plan
instead. I wanted Opening Gambit's *"The next Plan deals double damage"* banked.
Real decision on the turn, driven by a rule I had just learned.

**Turn 3.** Enemy at 15, swinging 13. **Volley**, which now printed *"Deal 7
damage"* per hit under Shrink, at X=3 = 21. Lethal.
*Rejected:* Deep Current + Exposed Flank + Undertow, which did not reach 15
under Shrink. Decision on the turn; the reprinted Volley face is what made it
calculable at a glance.

The post-fight page printed the carry-out I never got to see in combat:
*"Bake-Kurage: Opening Gambit, 1 — the 1 is Vulnerable. Inside the same beat:
Tamakushi Casket 3 on Shrinker Beetle."* Good — a Plan that kills still shows
its work.

---

## Fight 4 — Mawler, 72 HP

**Turn 1.** Hand was Defend, Defend, Sea-Salt Prayer, Strike, Strike — **not one
Plan card**. Played Sea-Salt Prayer then both Strikes.
*Rejected:* Defend over a Strike, which trades 6 damage for 2 HP in a 5-turn
race. **This turn presented no real decision** — the hand had no Plan, no
element and no ordering that mattered beyond "debuff first." That is the
finding: a hand of basics turns Kokomi into a vanilla deck.

**Turn 2.** Mawler was on a **Debuff** intent (no damage) and carried a
**Hydro Aura**. Played **Kaeya — Frostgnaw**, then **Volley** at X=2.
*Rejected:* Opening Gambit's Plan, and a block line. I chose the reaction
because the free turn was the window for it. Result, exactly as the text
promised and worth quoting in full: Kaeya took Mawler 58→**48** — 10, not the
printed 8, because **Frozen is a debuff, so the Tamakushi Casket answered with
its own 2 Hydro damage**; and the aura, which the Cryo hit should have consumed,
read **Hydro 2** afterwards. That is precisely the case the Elemental Reaction
paragraph warns about at length:

> "THAT LAST RULE CAN HIDE THE FIRST: where a reaction's own debuff sets off a
> relic that hits with the aura's own element, the aura is consumed and
> RE-APPLIED inside the same beat, so no screen ever shows it gone and the
> reaction looks as though it did not happen."

It is genuinely true, genuinely observable, and I would not have believed the
aura had been consumed without that paragraph. Then Volley X=2 dealt 20 **+ 6
Shatter** = 26 (48→22). One turn took 72→22.

**Turn 3.** Mawler had put **Vulnerable 3 on me** — its 6×2 became 18 against my
34 HP. Used **Poison Potion**, wrote **Ambush** as a Plan (12 vs the 5 it deals
now), played both **Defends** for 10 Block.
*Rejected:* playing Ambush now for 5, and a third Defend over the Plan. This was
the fight's real decision: I gave up damage this turn to bank 12, and covered
the gap with a potion. Note the Casket also fired on the **potion-applied**
Poison (22→20), which I did not expect — the Elemental Reaction text says a
potion applies no element, but the relic's answering hit is still a Hydro hit
and refreshed the aura.

**Turn 4.** Poison 6 + the banked Ambush 12 took Mawler 20→**2** at the start of
turn, before I played anything. Killed with **Strike**.
*Rejected:* nothing — but this is the plan paying off, not a dead turn. Mawler
was intending **21** damage and never got to swing it. The whole fight was
decided on turn 3.

The carry-out log again did its job, including a nice bit of honesty about its
own numbers: *"Under each Plan is the HP each enemy lost while that Plan
resolved — the whole beat, so anything the Plan set off is inside the number."*

---

## Fight 5 — Nibbit (1) 46 HP + Nibbit (2) 43 HP

**Turn 1.** Wrote **Exposed Flank** as a Plan, then **Kurage's Oath** as a Plan,
**in that order deliberately**, then Defend.
*Rejected:* playing either now (3 damage AoE, 1 Vulnerable), and writing them in
the reverse order. I was testing an open question the rules text does not
settle: the Plan keyword says *"the enemy's Vulnerable counts next turn"* —
but does a Vulnerable applied by an **earlier carry-out in the same beat** count
for a **later carry-out in that same beat**? The panel confirmed the queue
before I committed:

> Planned, and carried out at the start of your next turn in this order (2):
>   1. **Exposed Flank**
>   2. **Kurage's Oath**

**It does count.** The log next turn read:

> Bake-Kurage: Exposed Flank, 2 — the 2 is Vulnerable. Inside the same beat:
> Tamakushi Casket 3 on Nibbit (1), Tamakushi Casket 3 on Nibbit (2).
> Bake-Kurage: **Kurage's Oath, 10 — the 10 is damage; the clause asked for 7.**

The screen flagging its own discrepancy — *"the clause asked for 7"* — is the
best single line in the whole interface. **This is the kit's real decision
space: write-order is a combo.** Made at the draft (owning two Plan cards) and
executed on the turn.

**Turn 2.** Both Nibbits Vulnerable 2; B at 30 attacking for 14, A buffing.
Played **Kaeya on B** (30→15, Frozen halved its intent 14→7), then **Strike on
B** — 9 from Vulnerable **plus 6 Shatter** = exactly 15 = dead. Then **Volley**
X=1 into A for 15.
*Rejected:* Volley X=2 as the opener. Rejected because Volley targets *"a random
enemy"* and with two bodies alive it could have dumped both hits into the wrong
one — the randomness makes it a **worse** card in exactly the multi-enemy spot
where big damage matters most. Killing B with a precise 15 instead was the
decision, and it was made possible by Kaeya's face **reprinting itself as "Deal
12 damage"** under Vulnerable so I could count lethal without arithmetic.

**Turn 3.** A at 23, Vulnerable live. **Undertow** (face printed *"Deal 10
damage. If the enemy has a debuff, deal 15 instead"* — both numbers already
Vulnerable-adjusted) for 15, then **Strike** for 9. Lethal.
*Rejected:* Ambush's Plan for 12 next turn, which would have let A's 14 land
first. Correct to take the kill. Fight cost **1 HP total** after turn 1.

---

## Fight 6 (Elite) — Bygone Effigy, 127 HP

New mechanic, printed on the enemy: **Slow 0** — *"Whenever you play a card,
this enemy receives 10% more damage from Attacks this turn. It counts the cards
played BEFORE this one."* It resets to 0 every turn. So cheap cards first, big
attack last.

**Turn 1.** Effigy asleep. Played **Defend** → **Slack Water** → **Strike** in
that order (13 damage, 127→114).
*Rejected:* leading with Strike. The Defend was worthless as Block against a
sleeping enemy and I played it **purely as a Slow counter** — a card whose only
value that turn was being played before something else. Decision on the turn.

**Turn 2.** Effigy buffing, still no attack. Wrote **Ambush** and **Battle
Plan** as Plans, then played **Undertow** last for the Slow bonus.
*Rejected:* playing Ambush now for 5 and Read the Field's Plan for 10 Block.
I took tempo over defence on a free turn. Paid: next turn opened with
*"Ambush, 12"* and *"Battle Plan, 1 — the 1 is Energy"*, giving me **4 energy
and two extra cards**. Decision on the turn, enabled by the draft.

**Turn 3.** Effigy at 90 with **Strength 10**, swinging 23. Played **Sea-Salt
Prayer** → **Exposed Flank** → **Strike** → **Strike** (4 energy).
*Rejected:* four attacks, which reads like the damage line and is not. The two
"non-damage" cards each dealt relic damage (2, then 3 under their own
Vulnerable), applied Weak that cut the 23 to 17, and **raised Slow for the two
Strikes behind them**. Predicted 26, dealt exactly **26** (90→64). Slow printed
a running total — *"Slow 40 … (Receives 40% more damage)"* — which made the
whole stack checkable. Best-designed turn of the round: three separate systems
(relic, Vulnerable, Slow) all rewarding the same ordering.

**Turn 4 — and I got this one wrong, on the screen's own terms.** Effigy 64,
intending 23, me at 42. Played **Kaeya** (Frozen) then **Volley** X=2 for 38
total (64→26). I expected to also keep Frozen's *"next action deals 50% less
damage"* and take ~11. **I did not.** Frozen's text says plainly *"an Attack
Shatters it for 6 unblockable damage **and removes Frozen**."* My own Volley
shattered it, the halving evaporated, and I ate the full 23 → 22 HP.
*Rejected:* Defend + Kaeya + Volley X=1, which is 12 fewer damage but keeps
Frozen and takes ~6. **That was the right line and I missed it.** This is a real
and good tension — Frozen is *either* 6 damage *or* a halved hit, never both —
but I read the card twice and still walked into it, because "Shatter" reads as a
bonus rather than as a cost. Recording it as my mistake, not the kit's.

**Turn 5.** Me 22, Effigy 26, incoming 23 — kill or probably die. Played
**Volley** at X=3 for 30.
*Rejected:* Strike → Undertow → Volley X=1, which I calculated at 6 + 11 + 12 =
29 using the Slow ramp and Undertow's debuff clause. I rejected it **because it
depended on three chained readings being right**, and one misread (exactly like
the previous turn's) meant death. Took the single card that could not be wrong.
Decision on the turn, and the most real one of the round.

Elite down. Rewards: 41 gold, **Nunchaku**, Attack Potion, and a card choice
that included **Nereid's Ascension** — *"At the start of your turn, the
Bake-Kurage carries out every Plan twice."* Took it without hesitation; it is
the card the previous six fights had been teaching me to want.

**Room Full of Cheese (event).** Options were Gorge (2 of 8 random Commons) or
Search (*"Lose 14 HP"*) — at 22 HP that second option is a coin-flip on the run,
and the page states outright *"This room prints no Proceed… If none of them is a
decline, this room has none."* **There was no way to walk away.** Took Gorge,
picked **Ripple** and **Vanguard** — both cost 0, and Ripple's Plan (*"Gain 1
Energy and 4 Block"*) becomes 2 Energy and 8 Block under Nereid's Ascension.
That is a draft decision made entirely on a card I had drawn 3 minutes earlier.

Then a Treasure room: **Ripple Basin**. Stopped at 113 actions.

---

## The kit, after 6 fights

### (a) Which decisions felt like real choices, and what they traded off

Four kinds, and three of them are genuinely good:

1. **Plan write-order, on the turn.** This is the kit's best idea. Writing
   Exposed Flank *before* Kurage's Oath in fight 5 turned a 7 into a 10, and the
   log said so in words. The trade is a full turn of delay against a bigger,
   compounding number. It is a combo you build inside one turn and cash the
   next.
2. **Plan-vs-now, on the turn.** Every Plan card is a small tempo loan: Ambush
   is 5 now or 12 next, Read the Field 5 Block or 10, Riptide 9 AoE or 13. What
   makes this a *decision* rather than a table lookup is that the screen prints
   the two things that flip it — *"a Plan… lands in whatever Block the enemy is
   still standing in"* (so never bank into a Defend intent, fight 2 turn 2) and
   the enemy's intent (so always bank on a free turn, fight 3 turn 1 and fight 6
   turn 2). I made that call five separate times and got a different answer
   depending on the intent line. That is a real axis.
3. **Debuff-first ordering, on the turn.** Vulnerable, the Casket's answering
   hit, and the Elite's Slow all reward playing your "weak" cards first. Fight 6
   turn 3 is the clean example: two skills that look like filler out-damaged two
   Strikes by enabling them. The trade is that you are spending energy on cards
   with small printed numbers and trusting the multipliers.
4. **At the draft.** Kaeya — Frostgnaw was the whole reason fights 2, 4 and 5
   had a shape: one Cryo card in an all-Hydro deck is the only key to the
   reaction system, and the deck cannot make one itself. Nereid's Ascension
   then retroactively rewrote what a good common is (Ripple went from filler to
   a 0-cost 2-energy card). Those two picks did more for the run than any five
   turns of play.

### (b) What felt automatic, and what never seemed worth playing

- **Defend is close to dead.** 5 Block against Act 1 enemies swinging 12–23 is
  not a decision; it is a card you play when the hand offered nothing. Fight 4
  turn 1 — Defend, Defend, Sea-Salt Prayer, Strike, Strike — presented no
  choice at all. The kit is 8 interesting cards sitting on top of 8 cards that
  do nothing interesting, and when the shuffle gives you the bottom half you
  play a generic deck.
- **Ebb Tide never seemed worth playing.** *"Cancel every Plan. Gain 1 Energy
  and draw 1 card for each. Exhaust."* I drew it three times and it was a
  strictly dead card every time, because it is only live in the situation you
  spent the previous turn trying to create. To profit you must write Plans and
  then decide you did not want them — I never once wanted that, and I cannot
  picture the board where I do.
- **Lethal turns were automatic but earned.** Fight 1 turn 4, fight 4 turn 4.
  Both were "play the one card that kills," and both were set up two turns
  earlier. I count those as the plan paying off, not as empty turns.
- **Volley at X=3 became a default finisher** three times. Slightly too good as
  a rescue button, though its random targeting genuinely punished me for
  considering it in fight 5.

### (c) What I could not understand, or that contradicted its own printed text

1. **The Bake-Kurage buff counter is wrong, or its explanation is.** The panel
   says *"the number on its buff is how many are written, not a limit."* The
   buff read **"Bake Kurage 1"** on literally every screen of all six fights —
   with zero Plans written, with one written, and with **two** written (fight 5
   turn 1, where the queue panel below it correctly listed 2). The number never
   moved. Either it does not mean what the sentence says, or it is stuck at 1.
   This is the clearest screen/behaviour contradiction I found.
2. **Volley refreshed a Hydro aura despite carrying no element tag.** Fight 1
   turn 3: aura went 1 → 2 across a Volley. The Elemental Reaction text is
   emphatic that *"An element comes from a CARD that prints one and from nothing
   else."* Volley prints none. (It is possible some other effect re-applied it
   inside the beat, but nothing on screen said so, and no carry-out log covers a
   card you play yourself.)
3. **Shrink's wording versus Plans.** *"you deal 30% less damage with every hit
   you land"* — but a planned carry-out landed at full value. Reconcilable via
   *"Every planned HIT is the jellyfish's,"* which is in a different panel. The
   two sentences are individually true and jointly misleading, and this is a
   large strategic fact (under Shrink, route damage through the jellyfish)
   hidden in the seam between them.
4. **The relic fires on potion-applied debuffs.** Poison Potion triggered the
   Casket for 2. Fine, arguably correct — but it sits oddly beside *"a potion, a
   relic or an enemy applies none [no element] unless its own face says so,"*
   since the resulting Hydro hit did refresh the aura.
5. **Two Neow/event rows admitted they had no card faces to show** — *"the feed
   carried no face for it… so this page can offer it by name only."* Honest, and
   it made both choices partly blind. The Cheese room compounded it by having
   **no decline option at all**, which the page itself flags.
6. **Intent numbers are unexplained by design.** *"the feed carries no base, no
   modifier list and no breakdown."* Workable, but with Strength 10 + Weak +
   Frozen all live at once on the Elite I was reverse-engineering a single
   integer.

### (d) The card I never wanted to play, and the one I was happiest to draw

- **Never wanted: Ebb Tide.** Dead in all three draws (see (b)). **Defend** is
  the more common disappointment, but Ebb Tide is the one I actively resented.
- **Happiest to draw: Kaeya — Frostgnaw.** It is the only card in the deck that
  can start a reaction, and it grew a **"Reaction preview: Frozen"** line on its
  own face exactly when that became possible. Drawing it meant the turn had a
  shape. **Ambush** is the runner-up — 5 now or 12 later off one energy is the
  cleanest expression of what this kit is about. And the card I was happiest to
  *add* was **Nereid's Ascension**, which is the mechanic finally being allowed
  to go off.

### (e) Did the first turn of the first fight already present a decision?

**Yes, though a mild one.** Three energy, a lone 57 HP enemy attacking for 4, a
hand holding three Strikes plus Slack Water plus Kurage's Oath. Flat aggression
(three Strikes, 18) was live and roughly competitive with what I did. The choice
that existed was **whether to spend a card on the jellyfish** — Kurage's Oath
deals 3 now or 7 next turn — and the enemy's harmlessness made banking correct.
So the first turn did ask the kit's central question. What it did **not** do is
make the question urgent: with 4 incoming damage, nearly any line survives, and
I learned the Plan rule by choosing to experiment rather than by being forced.
The kit's actual teeth only appeared in fight 3, when Shrink revealed that Plans
dodge my own debuffs, and in fight 5, when write-order turned 7 into 10.

---

## Non-blindness declaration

**Repo files read: none.**

Every game action was one of the two allowed commands, always with `GITS_LANE=1`,
always through the Bash tool:
`GITS_LANE=1 python -m understudy.blindplay observe` and
`GITS_LANE=1 python -m understudy.blindplay act "<command>"`.
I ran no other `understudy` subcommand — no `harness state`, no `scenario`, no
`staged_turn`, no `soak`.

Other tool calls, in full:

1. **Bash — `mkdir -p` + `echo`** once, creating and writing one line into a
   scratch notes file under the session scratchpad
   (`…\913fe618-…\scratchpad\notes.md`). I never read it back and never added to
   it; in practice it went unused.
2. **Bash — `cd` into the repo working directory** as the prefix of every
   command, in order to run the `understudy` module. No repo file was opened.
3. **Bash — `sed`, `head`, `tail`, `grep`** used only as filters piped from the
   output of the two allowed commands, to re-read one block of a screen (the
   hand, the enemy block, the carry-out log) without reprinting the whole page.
   These never touched a file on disk.
4. **Bash — `>/dev/null`** on some `act` calls to suppress the JSON echo when I
   was chaining several accepted actions and only wanted the screen afterwards.
5. **Write tool — once**, to create this record at
   `review\qa\kokomi-round-23-2026-09-07\opus-cap-act1.md`.

One caveat on my own play, declared for honesty rather than blindness: on
Elite turn 4 I misread Frozen/Shatter and took roughly 11 more damage than I
needed to, which is the direct cause of the run ending at 22/80 rather than
around 33/80. The misread is written up in fight 6 rather than smoothed over.
