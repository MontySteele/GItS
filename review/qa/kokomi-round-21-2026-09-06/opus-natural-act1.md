# Blind seat record — KLEEMOD-KOKOMI, lane 2, natural draft, Act 1

## Identity

- **Model / seat:** Claude Opus (Fable-family), blind TESTER seat, lane 2.
- **Run seed:** `BG35Z1K5Z8LZ`. **Character:** KLEEMOD-KOKOMI. **Ascension 3.**
- **Act 1.** The map named the act's boss: **Ceremonial Beast**. I never reached it.
- **Actions accepted:** 120 of 120.
- **Termination:** action budget. The 120th accepted act was `end turn` on
  round 1 of fight 6; the run is alive and mid-fight. Not a stall, not a
  refusal cascade, not a tool block. Two refusals happened (both recorded
  below); neither was consecutive with a third.
- **HP trajectory:** 64/80 start → 48 (after F1) → 72 (event heal) → 52 (after
  F2/F3) → 47 → 73 (campfire rest, max HP now 87) → 63 (after F5) → **59/87 at
  the stop**. Max HP went 80 → 87 (Byrdonis egg eaten).
- **Gold at stop:** 43. (I had 149 and spent all of it at Morphic Grove.)
- **Potions held:** Skill Potion, Attack Potion. I used neither — I never hit a
  turn where I would have died without one, and the brief's instrument is the
  decisions the *kit* presents, not the potions.
- **Relics at the end:** Tamakushi Casket (start each combat with the
  Bake-Kurage; whenever you apply a debuff to an enemy it deals 2 Hydro damage
  to that enemy), Large Capsule, Vexing Puzzlebox (start of each combat, add a
  random card to hand, free this turn), Pantograph (heal 25 at the start of
  each Boss combat), Parrying Shield (end a turn with ≥10 Block → 6 damage to a
  random enemy).
- **Deck at the end**, as far as the bridge ever printed it: 3 Strike, ~5
  Defend, Slack Water, Kurage's Oath, Riptide *(Sharp 2)*, Feint, Treatise,
  Exposed Flank, Amber — Fiery Rain, Bouncing Flask, and **one card I cannot
  name** (see the Morphic Grove note below). I never got a full deck listing:
  the only screens that enumerate the deck are the Enchant picker (Attacks
  only, that time) and the Transform picker, and the Transform picker's list
  ran past what I read. So the Defend count is "at least 4, probably 5–6" and
  is honest guesswork, not a reading.
- **Not in the deck, despite showing up every fight:** Sea-Salt Prayer, Ambush,
  Change of Plans, Ripple, Cleansing Wave, Vanguard. Each arrived once, at the
  start of one combat, with the "cost printed on this card is 1; it is showing
  0 here" note — i.e. these are Vexing Puzzlebox's free random card, not cards
  I drafted. That relic is doing a *lot* of the work in this record and I want
  that flagged: **six of the most interesting Plan cards I ever saw were relic
  gifts, not draft picks.**

**Neow pick: Large Capsule** (2 random relics, +1 Strike and +1 Defend).
I took it because two relics is the biggest one-shot power swing on the screen
and two basics is a cheap dilution; Fishing Rod pays out on a three-combat
clock I might not live to see twice, and Neow's Torment adds a card I'd have to
draw. It paid: Vexing Puzzlebox and Pantograph.

---

## Fight 1 — Shrinker Beetle [A], 40 HP

Opening hand: 4 Defend, 1 Strike, Sea-Salt Prayer (free, Puzzlebox).

**Turn 1** — played Sea-Salt Prayer on A (free: 4 Block, 1 Weak), then Strike on
A, then ended with 2 energy unspent and four Defends in hand.
*Rejected:* spending those 2 energy on Defends. The intent line read
`Strategic (DebuffStrong) — This enemy intends to apply a Debuff to you`, i.e.
no damage was coming, so 10 Block would have bought nothing. **The front half
of this turn was a real decision (Sea-Salt Prayer first, so the Casket's
debuff-trigger fires before anything else, and Strike vs. banking energy); the
back half had none — two energy and four identical cards against a no-damage
intent.**
Beetle 40 → 32. The 8 checks out exactly: Strike 6 + Casket 2. **Plans written:
none** — and not by choice, see the refusal below.

**The first refusal, and it is the round's biggest legibility finding.**
The battle screen's `What you can say` block prints, unconditionally, every
turn:

> `play "<card title>" on "Bake-Kurage"   (writes its Plan instead of playing it now)`

and the Bake-Kurage panel says *"Play a card on it to write its **Plan** line
instead of playing the card now."* So I tried it:

- `play "Defend (1)" on "Bake-Kurage"` → *"'Defend (1)' is played on you, not on
  an enemy, so it takes no `on "Bake-Kurage"`. The form that resolves: play
  "Defend (1)"."*
- (turn 2) `play "Strike (1)" on "Bake-Kurage"` → *"'Strike (1)' cannot be
  planned on Bake-Kurage, so aiming it there would spend the action and do
  nothing."*

Both refusals are correct and both are helpful. But **for the whole of fight 1's
first two turns the kit's centrepiece was inert and nothing on any screen told
me why.** The jellyfish panel says "play a card on it"; the keyword says "a
**Plan** card"; nothing in my opening hand printed the word Plan, and no screen
said "you are holding no Plan cards." I only learned what a Plan card is on
**round 3**, when Kurage's Oath and Slack Water finally arrived printing a
literal `Plan:` line. The rule is legible *on the cards*; it is not legible
*from the absence of them*, and a new player's first two turns with this
character are spent poking a mascot that cannot do anything.

**Turn 2** — Shrink landed: `Shrink -1 — While Shrinker Beetle is alive, your
Attacks deal 30% less damage`, and every Strike in hand reprinted itself as
"Deal 4 damage" instead of 6. **Screen and outcome agreed perfectly, and I want
to credit that: the card face changed, so I never had to do the arithmetic.**
Played 3 Strikes (12). *Rejected:* Defend, trading 4 damage for 5 HP — with the
beetle escalating (7 → 13 → 7 → 13) I judged racing better than bleeding turns.
**Plans: none** (refused, above). Took 7 → HP 57.

**Turn 3** — the first turn with a real menu. Hand: Kurage's Oath (1: deal 2 to
ALL / *Plan:* 7 to ALL), Slack Water (1: deal 2 + 1 Weak / *Plan:* Weak to
ALL), 2 Strike, Defend, against a 20 HP beetle intending 13.
Played Slack Water on A (Weak, cutting the 13 to 9, plus Casket 2), planned
Kurage's Oath, Strike.
*Rejected:* playing Oath face-up for 2. The Plan line is 7 against a face of 2
and my Strikes are Shrunk to 4, so **the interesting question was whether Shrink
bites the carry-out.** The keyword only promised *"Enemy Vulnerable counts; your
Weak and Strength do not"* and says nothing about Shrink. **Plans written: 1 —
Kurage's Oath.**

**Turn 4** — the readout answered it:

> `Bake-Kurage: Kurage's Oath, 7 — the 7 is damage.` / `Shrinker Beetle lost 7 HP`

**7, undiminished, on a turn where my own Strikes hit for 4 instead of 6.** That
is the kit's thesis in one line and it is the best moment of the round: the
jellyfish is the answer to a debuff that turns your own deck off. It is also
*under*-printed — Shrink's own text says "your Attacks", the Plan keyword lists
Weak and Strength, and nothing connects the two. I found it by testing, not by
reading. Beetle 20 → 5.
Then the turn itself: 1 Strike (4) and four Defends against a 5 HP body.
**No decision at all.** Strike + 2 Defends, take 0.

**Turn 5** — one Strike for the kill. The lethal was set up two turns earlier by
the planned Oath, so I score this as *the plan paying off*, not a dead turn.

**Fight 1: 5 rounds, 64 → 48 HP.**
Reward: 10 Gold, Skill Potion, and a card choice — Feint / Riptide / Chain of
Command / Gorou — Crystal Collapse. **Cards reading the jellyfish's history:
none of the four.** Chain of Command counts *Companions*, Gorou copies a
Companion; neither counts Plans. **Took Riptide** (2: 9 to ALL / *Plan:* 13 to
ALL) because my entire damage output was 4–6 per card and it is the only card
on the sheet that scales with the number of bodies.

---

## Fight 2 — Wriggler ×4 [A] 18, [B] 20, [C] 19, [D] 21 (78 HP total)

Reached through the Dense Vegetation event: **Rest — Heal 24 HP. Fight some
enemies**, over **Trudge On — Gain 95 Gold. Lose 8 HP.** I took the fight: gold
only converts at a shop and no shop was inside my action budget, and a seat that
is measuring a kit should buy fights, not currency. HP 48 → 72.

**Turn 1** — hand: Strike ×2, Defend ×2, Slack Water, Ambush (free: deal 5 /
*Plan:* 12). Planned Ambush (free), then Slack Water on A (4 + Casket 2 = 6),
Strike, Strike — **A dead exactly on the button, 18 = 6+6+6.**
*Rejected:* playing Ambush face-up for 5. Planning it cost me nothing this turn
(it was the free card) and still killed A, so this was the round's cleanest
"free" decision — a strictly-better line the board handed me. **Plans: 1 —
Ambush.** Took 6 → 66.

**Turn 2** — 3 Strike, 2 Defend, no kit card. Killed B (at 8 after the planned
Ambush's 12) with 2 Strikes, then Defend. *Rejected:* Striking C instead of
Defending — 6 damage into a 19 HP body that I could not finish either way, vs 5
Block against a body doing 8. **This turn presented a decision only in the
weakest sense; the hand was five basics.** **Plans: none — no Plan card in
hand.** HP 66 → 63.

**Turn 3** — the round's best turn. Hand: Kurage's Oath, Riptide, 2 Defend, and
**Infection** (a status card the Wrigglers gave me: *Unplayable. At the end of
your turn, if this is in your Hand, take 3 damage*). C 19, D 21, incoming 8.
**Planned Riptide AND Kurage's Oath** — the first time I tried two Plans in one
turn, and it worked.
*Rejected:* playing both face-up for 9+3 = 12 to each. Planned they are 13+7 =
20 to each, which is **exactly lethal on C (19)** where 12 is not; the enemies
get exactly one turn in between either way, so the delay cost me nothing and
bought +8 and a guaranteed kill. This is the decision I would point to if
someone asked whether this kit has a turn worth thinking about.
**Plans written: 2 — Riptide, Kurage's Oath.** Took 8 + 3 (Infection) → 52.

**Turn 4** — readout:

> `Riptide, 13` → C −13, D −13; `Kurage's Oath, 7` → `Wriggler (3) lost 6 HP,
> and died` / D −7

D left on 1. Strike, done. Again: obvious lethal, *because the plan I wrote two
turns ago made it obvious*. **Plans: none needed.**

**Fight 2: 4 rounds, 72 → 52 HP.**
Reward card choice — Feint / Shell Guard / **Tide Chart** / Sayu — Yoohoo Art.
**Card reading what the jellyfish did: Tide Chart** — *"Next turn, after the
Bake-Kurage carries out its Plans, draw 1 card for each"* (a count of Plans).
**I did not take it.** Reason: I had just proved I can write two Plans in a
turn, so it is a 0-cost draw-2 in my best case — but it draws *nothing* on any
turn I plan nothing, and three of my seven turns so far had been all-basics
hands with no Plan card to write. **Took Feint** (1: 6 / *Plan:* 10) instead,
because a 1-energy 10 that ignores Shrink and Weak is the best rate on the
sheet and it gives the jellyfish something to do on exactly those dead turns.

---

## Fight 3 — Fuzzy Wurm Crawler [A], 55 HP

**Turn 1** — the free Puzzlebox card was **Change of Plans**: *"The Bake-Kurage
carries out your first Plan now. Exhaust."* It printed
`CANNOT BE PLAYED: no Plan is written`, which is a very good refusal-in-advance
— it told me the sequencing rule before I wasted an action on it.
Planned Kurage's Oath, then played Change of Plans → **7 damage immediately, for
1 energy, off a card whose face reads "Deal 3 damage to ALL".** Then Slack Water
(4 + Casket 2) and Strike. 55 → 36.
*Rejected:* holding the Oath plan for next turn and playing Change of Plans
later. There was no later — it exhausts, and the enemy was hitting for 4, so
there was no defensive reason to bank. **Plans written: 1 (Kurage's Oath),
consumed the same turn.** The screen labelled it correctly and separately:
*"The Bake-Kurage carried these out THIS TURN, the moment each was written, and
not this morning."* Took 3 → 49.

**Turn 2** — Riptide, Strike, 3 Defend, against a Buff intent (no damage).
Planned Riptide, Striked. *Rejected:* Riptide face-up for 9. Planned is 13, the
enemy did nothing this turn, so the delay was free and the swap was +4.
**Plans: 1 — Riptide.** Took 0.

**Turn 3** — Riptide's 13 landed; A at 17 with Strength 7 and an 11-damage
intent. Hand: 3 Strike, Feint, Defend. **3 Strikes = 18 ≥ 17, lethal.**
*Rejected:* planning Feint for 10 next turn — there is no next turn when lethal
is on the table now. A real decision, decided by arithmetic on the printed
numbers, which is the good kind.

**Fight 3: 3 rounds, 52 → 49 HP.**
Reward card choice — **Treatise** / Pincer / **Tide Wall** / Yoimiya — Aurous
Blaze. **Cards reading what the jellyfish did: two.** *Treatise* — "Once per
turn, **when the Bake-Kurage carries out a Plan**, draw 1 card." *Tide Wall* —
"*Plan:* Gain 3 Block **for each Plan the Bake-Kurage carries out this
morning**." **Took Treatise**, because the recurring failure mode of the run was
drawing five basics with no Plan card to write, and a permanent +1 card on every
turn I do plan attacks that directly.

---

## Fight 4 — Nibbit [A], 45 HP

(HP now 56/87 — the Byrdonis Nest event's **Eat the Egg** gave +7 Max HP and
healed it. I passed on **Take the Egg** because hatching costs a whole rest site
and I had one rest site and ~35 actions left.)

**Turn 1** — free card was **Ripple** (*Gain 2 Block. Plan: Gain 1 Energy and 4
Block*). Planned Ripple, planned Riptide, played Slack Water on A.
*Rejected:* Riptide face-up (9 vs 13) and Ripple face-up (2 Block vs 1 Energy +
4 Block next turn). Against a 12-damage single attacker with a long fight ahead,
both delays were cheap. **Plans written: 2 — Ripple, Riptide.** Took 9 (Weak cut
12 → 9) → 47.

**Turn 2** — the readout is worth quoting because it handles a non-damage Plan
cleanly:

> `Bake-Kurage: Ripple, 1 — the 1 is Energy.` / `no enemy lost HP`
> `Bake-Kurage: Riptide, 13 — the 13 is damage.` / `Nibbit lost 13 HP`

Energy showed **4/3**. Planned Kurage's Oath, Strike, one Defend, ended with a
Defend unspent because 9 Block already covered a 6-damage intent.
*Rejected:* the second Defend (pure waste) and Oath face-up (3 vs 7).
**Plans: 1 — Kurage's Oath.** Took 0.

**Turn 3** — and here the screen was honest about something it could have hidden:

> `Kurage's Oath, 7` → `Nibbit lost 2 HP, and 5 more absorbed by Block`

The enemy had blocked; the Plan number was 7 and only 2 landed, and the readout
said so in the same line. **This is the single best piece of writing in the
bridge.** Played Treatise, planned Feint, Strike. *Rejected:* Feint face-up (6
vs 10) on a Buff turn where blocking was worthless. **Plans: 1 — Feint.**

**Turn 4** — Feint's 10 landed, Nibbit at 2, and **Treatise drew me a sixth
card** — confirmed by the hand being six long. Strike for the kill.

**Fight 4: 4 rounds, 56 → 47 HP.**
Reward card choice — Exposed Flank / Battle Plan / **Treatise** / Lisa — Violet
Arc. **Card reading what the jellyfish did: Treatise** (a second copy; same
"when the Bake-Kurage carries out a Plan" line). **I did not take it** — one
Treatise already caps at one draw per turn, so a second copy is a dead draw
whenever the first is out. **Took Exposed Flank** (*Plan:* 2 Vulnerable to ALL),
because the Plan keyword explicitly says *"Enemy Vulnerable counts"*, so it is
the one card that multiplies the jellyfish's big hits, and the Casket turns each
debuff application into free damage on top.

Between fights: campfire **Rest** (47 → 73) over Smith — an Elite was two floors
on and I was at 54%.

**Self-Help Book event** — enchanted **Riptide with Sharp 2** (+2 damage on the
card, for the rest of the run), picking the AoE attack so the +2 multiplies by
the number of bodies. **This produced the round's second real finding — see
fight 5 turn 3.**

**Morphic Grove** — took **Group** (lose all 149 gold, Transform 2 cards) over
**Loner** (+5 Max HP), and transformed 2 Strikes. Gold was dead weight with no
shop inside my budget. **Finding: the game never told me what the two Strikes
became.** I confirmed one of them only by drawing Bouncing Flask in fight 5; the
second I never saw and cannot name. Spending 149 gold and two cards and getting
back a screen that says `Proceed` is the one place in this run where the
interface simply withheld the outcome.

---

## Fight 5 — Axe Raider [A] 21, Assassin Raider [B] 19, Crossbow Raider [C] 18

**Turn 1** — free card **Cleansing Wave** (5 Block, remove a debuff / *Plan:* 10
Block). Played it face-up, plus Defend, to reach exactly **10 Block** and turn on
Parrying Shield, then **Bouncing Flask** (2: apply 3 Poison to a random enemy 3
times).
*Rejected:* planning Cleansing Wave for 10 Block next turn — 29 damage was
queued across three bodies and I needed the block *now*; and rejected two
Strikes at B, because Poison plus the Casket does more total damage than 12
focused. The Casket fired on every Poison application: A −2, C −4 before any
attack. **Plans: none — I deliberately wrote none, the first time that was a
choice rather than an empty hand.** Took 5 → 68.

**Turn 2** — 2 Defend, Strike, Treatise, Kurage's Oath, against 29 incoming.
Planned Oath, played both Defends (10 Block → Parrying Shield again).
*Rejected:* Treatise over the second Defend — with the budget nearly gone, a
draw engine's compounding value was worth less than 5 Block against 29.
**Plans: 1 — Kurage's Oath.** Took 19 → 63. C died to Poison.

**Turn 3 — the Sharp finding.** Riptide arrived in hand printing:

> **Riptide** [Hydro] (Sharp 2) — cost 2, attack
> Deal **11** damage to ALL enemies. Plan: Deal **13** damage to ALL enemies.

**The enchantment moved the face number 9 → 11 and left the Plan number at 13.**
Sharp does not apply to the carry-out. I do not think this contradicts anything
printed — the Plan keyword's exclusion list is "your Weak and Strength", and an
enchantment is arguably neither — but it **inverts the card's whole economy**:
before Sharp, planning Riptide was +4 damage for one turn's delay and I planned
it every single time; after Sharp it is +2, and the correct play flipped to
face-up. **A run-permanent upgrade quietly made my signature Plan worse, and the
only place that is visible is the two numbers sitting next to each other on one
card face.** I noticed it because the numbers were adjacent; if Sharp had landed
on Feint (6 → 8 face, Plan stuck at 10) I would probably have kept mis-planning
it all act.
So: **Riptide face-up for 11 → A dead (6), B to 1; Feint on B for the kill.**
*Rejected:* planning Riptide for 13 — which would have won the fight a turn
later and eaten 22 damage in between. **Plans: none, correctly.**

**Fight 5: 3 rounds, 73 → 63 HP.**
Reward card choice — **Song of Pearls** / Rally / **Tide Wall** / Amber — Fiery
Rain. **Cards reading what the jellyfish did: two.** *Song of Pearls* — "Once
per turn, **when the Bake-Kurage carries out a Plan**, gain 3 Block." *Tide
Wall* — "*Plan:* Gain 3 Block **for each Plan** the Bake-Kurage carries out this
morning." **I took neither.** **Took Amber — Fiery Rain** (1: deal 4 to ALL
enemies 3 times, Pyro), because 12 AoE for 1 energy beats both on rate and
because it was the first chance in the whole run to put a **second element** in
my deck — every aura I had ever applied was Hydro, and the Elemental Reaction
block had been telling me on every screen `NO REACTION IS REACHABLE HERE`.

---

## Fight 6 — Shrinker Beetle [A] 38, Fuzzy Wurm Crawler [B] 55 (in progress)

The last Unknown node was a fight. I had 5 actions and spent them on one turn.

**Turn 1** — free card **Vanguard** (0: apply 1 Vulnerable / *Plan:* 1
Vulnerable and 1 Weak, Exhaust). Planned Vanguard, then **Amber — Fiery Rain**
(12 to both, applying Pyro), then **Slack Water on A** — deliberately, to drop a
Hydro hit onto the Pyro aura Amber had just left. The card face grew a new line
the instant it was targetable:

> *Reaction preview: Vaporize* — Pyro meets Hydro: this hit deals 1.5× damage
> and consumes the aura.

A went 38 → 18: Amber 12, then Slack Water's 4 × 1.5 = 6, then Casket 2. And the
aura readout afterwards said `Hydro Aura 2` on A — **exactly the case the
Elemental Reaction block warns about in advance**: the Vaporize consumed the
Pyro, then the Casket's own Hydro hit re-applied Hydro inside the same beat, so
no screen ever shows the aura gone. **The kit predicted its own most confusing
interaction in writing before it happened to me.** Then Feint on A (Hydro onto
Hydro: refresh, no reaction, 6). **Plans written: 1 — Vanguard.** Ended turn;
took 4 → 59.

The final readout, at 120 actions, is the other thing worth quoting:

> `Bake-Kurage: Vanguard, 1 — the 1 is Vulnerable. Inside the same beat:
> Tamakushi Casket 3 on Shrinker Beetle, Tamakushi Casket 3 on Shrinker Beetle.`
> `Shrinker Beetle lost 6 HP`

Two debuffs applied, so the Casket fired twice, and **each hit was 3 rather than
2 — because the Vulnerable the same Plan had just applied was already on the
body.** The screen itemised a relic proc inside a Plan carry-out and showed the
number changing. Stopped here on budget: A at 6, B at 43, me at 59/87.

---

## The kit, after 6 fights (5 finished)

**(a) Which decisions felt like real choices, and what they traded off.**

- **On the turn — "face-up or planned?", and it is a genuinely different
  question every time.** The trade is *tempo for size*: Oath is 3 now or 7 next
  turn, Feint 6 or 10, Riptide 9 or 13. What makes it a decision rather than a
  ratio is that the enemy's intent line arbitrates it. Against F3's Buff turn and
  F4's Buff turn the delay was literally free, so planning was strictly correct.
  Against F5's 29-damage turn and F5T3's lethal it was strictly wrong. **The
  intent line is the input, the Plan line is the output, and I had to read both
  every turn.** That is the best thing this kit does.
- **Earlier in the fight — the double-plan.** F2T3, planning Riptide *and*
  Kurage's Oath, converting 12-to-each into 20-to-each and turning "C survives on
  7" into "C dies". That is a two-turn commitment made while taking 11 damage on
  the promise, and it is the one turn in the round I would call exciting.
- **Earlier in the fight — Change of Plans (F3T1).** Write a Plan, then cash it
  the same turn: 7 damage out of a card whose face says 2, for 1 energy. A
  sequencing decision that only exists because the Plan is a *board object* and
  not just a delayed effect.
- **At the draft — Exposed Flank over Battle Plan and a second Treatise.** The
  Plan keyword says "Enemy Vulnerable counts", so Vulnerable is the one
  multiplier that reaches the jellyfish's numbers; taking it changed what my
  future plan-turns are worth. Likewise **Riptide over Feint** at reward 1
  decided the shape of fights 2–5.
- **At the event — Sharp 2 onto Riptide**, which turned out to be a decision
  about my *Plan economy* and I did not know it at the time. See (c).

**(b) What felt automatic, and what never seemed worth playing.**

- **Defend was never a decision, it was a leftover.** Every "and then I played
  Defend" in this record is what I did with energy I had nothing better for.
  Twice (F1T1, F1T4) I had four Defends against an intent that could not use
  them.
- **Turns with no Plan card in hand are automatic.** F1T2, F1T4, F2T2, F4T4 —
  five basics, one number to compare, no jellyfish decision available. **This was
  4 of my 18 turns, and it is the kit's real problem: the interesting mechanic is
  gated behind drawing one of ~5 relevant cards out of ~19.**
- **Sea-Salt Prayer** (4 Block, 1 Weak, no Plan line) was the weakest card I
  saw — it exists to trigger the Casket and nothing else.
- **The four "count the Plans" cards** — Tide Chart, Tide Wall, Song of Pearls,
  and the second Treatise — I declined all of them, and I want to be honest that
  I am not sure I was right. They are *the* payoff family for the mechanic, and
  I skipped every one because each is dead on precisely the turns that are
  already dead (the no-Plan-card hands above). That may be a real design tension:
  **the cards that reward planning hardest are the ones that punish the draw
  variance the kit already has.**

**(c) What I could not understand, or that contradicted its own printed text.**

- **Nothing contradicted its printed text.** Every number I checked landed:
  18 = 6+6+6, 20 = Riptide 13 + Oath 7, 8 = Strike 6 + Casket 2, 6 = 4×1.5 with
  Vaporize, the blocked Oath saying "lost 2 HP, and 5 more absorbed by Block".
  I want that on the record because it is unusual.
- **What I could not understand, in order of how long it cost me:**
  1. **Which cards can be planned.** Two turns of fight 1 spent finding out by
     refusal. See fight 1.
  2. **Whether Shrink bites the carry-out.** The Plan keyword lists Weak and
     Strength as excluded and says nothing about a third debuff that reads
     "your Attacks deal 30% less damage". It does not bite — I had to test it.
  3. **Sharp vs the Plan line.** An enchantment raises the face number and not
     the Plan number, and nothing anywhere says so. It is *visible* (two numbers
     on one card) but never *stated*, and it silently reversed the right play on
     my best card.
  4. **What my two transformed Strikes became.** Never printed.
- **What was explained unusually well:** the Elemental Reaction block told me,
  before I had any second element at all, that a relic re-applying the aura's own
  element inside the same beat would make a reaction *look* like it did not
  happen — and then that exact thing happened to me in fight 6 and I recognised
  it instead of filing it as a bug. That is a paragraph that earned its length.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- **Never wanted:** Defend. Not because 5 Block is bad, but because in 18 turns
  it never once competed with anything — it was what I did when the jellyfish
  had nothing to eat.
- **Happiest to draw:** **Riptide**, and specifically Riptide *before* I
  enchanted it. Seeing it in an opening hand meant the next two turns had a
  shape: plan it, survive one turn, watch 13 land on everything. After Sharp 2
  it became a merely good card that I play face-up, which is a slightly sad
  thing to have to write about my own upgrade.

**(e) Did the first turn of the first fight already present a decision?**

**Half of one, and the half that was missing is the kit's own.** The front of the
turn was a real choice: the free Sea-Salt Prayer wants to go first so its Weak
trips the Tamakushi Casket before anything else resolves, and then Strike-vs-bank
against a no-damage intent. The back of the turn was two energy and four
identical Defends against an enemy that could not be blocked profitably. And the
Bake-Kurage — the thing the whole screen is built around, with its own panel and
its own three-paragraph rules block — **could not be used at all, and told me so
only by refusing me twice.** A first turn that spends its energy on Defends while
the mascot sits idle is not the first impression this kit deserves, given that by
round 3 it was the most interesting thing I played all night.

---

## Non-blindness declaration

**Repo files read: none.**

Every game action was one of the two allowed commands, run through the Bash
tool: `GITS_LANE=2 python -m understudy.blindplay observe` and
`GITS_LANE=2 python -m understudy.blindplay act "<command>"`. No other
`understudy` subcommand was run — no `harness state`, no `scenario`, no
`staged_turn`, no `soak`.

Tools and commands used outside those two:

1. **Read tool, once**, on
   `…\scratchpad\brief-kokomi-l2.md` — my own brief, as instructed. It is not a
   repo file.
2. **Bash tool**, `mkdir -p "C:/Users/Monty/Documents/GitHub/GItS/review/qa/kokomi-round-21-2026-09-06" && echo made` — creating the record
   directory, which the coordinator told me to create and declare. The directory
   did not exist.
3. **Bash tool**, repeatedly, to pipe `observe` output through `sed -n` to
   re-read only the blocks I needed (`sed -n '1,8p;/## Your hand/,/^\*More
   than/p;/other side/,/^\*Each/p'` and variants, and one `tail -20`). These
   filter the same `observe` text the bridge printed; they add nothing and hide
   nothing that changed a decision. Where a filter cut something I needed —
   fight 1 turn 4's hand, and the Transform picker's card list — I say so in the
   record rather than guessing, and the deck listing above is flagged as
   incomplete for exactly that reason.
4. **Write tool, once**, for this file.

Two commands were refused; both are written up in Fight 1 as findings, with what
I asked for and what the bridge said back. No screen was TOOL-BLOCKED. The run
was stopped by the action budget with the fight-6 board still live, and I did
not play past it.
