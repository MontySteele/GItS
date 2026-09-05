# Blind seat record — KLEEMOD-KLEE, lane 2, round 15 run 2

## Identity

- Model and seat: Claude Opus, blind Opus seat, round 15 run 2
- Lane: 2
- Run seed: `XEN2USFZBJZ1`
- Character: Klee (KLEEMOD-KLEE)
- Ascension: 1
- Act: 1. The map printed the act's boss as **Ceremonial Beast**. I never reached it.
- Floors reached: 8 (the elite was floor 8; I stopped on the map above it)
- Actions accepted: **117 of 120**
- Termination reason: **action budget**. I stopped voluntarily at 117 because three
  remaining `act` calls cannot open and finish another fight, and the brief says a
  budget stop is a complete round rather than something to play past. The bridge
  never printed `budget reached`, never refused a command, and never stalled.
- HP trajectory: 62 → 50 (fight 1 turn 1, ate a 12 unblocked) → 49 (fight 1 turn 2)
  → 49 through fights 2 and 3 (both taken at zero damage) → 43 (fight 4) → 37
  (fight 5) → 14 → **2** (fight 6, the elite, two 23-damage swings). Ended at
  **2/62**.
- Gold at the end: **79**
- Potions held: Attack Potion, Poison Potion (one slot empty)
- Relics at the end: **Pounding Surprise** ("Whenever a Bomb goes off, gain 1
  Spark"), **Winged Boots** (1 charge left), **Beating Remnant** (elite drop — I
  never saw its printed text; no screen I was given reprinted it after the claim)
- Deck at the end (the map's own list at floor 8, plus Diona claimed after it):
  Ammo Scavenging, Bang Bang!, Defend ×4, Grounded, Jumpy Dumpty, Ka-pow!,
  Lisa — Lightning Rose, Pocket Fireworks, Rosaria — Ravaging Confession, Sizzle,
  Sparks 'n' Splash, Strike ×4, Tinder Toss, Diona — Shaken, Not Purred (20 cards)
- Fights: **6 entered, 6 won**, including one elite.

**Neow pick: Winged Boots.** I took it over Kaleidoscope because Kaleidoscope's "2
card rewards from other characters" would have diluted the only thing I was there
to read — this character's own cards — and over Dowsing Rod because a card that is
Unplayable until five ? rooms have passed is a dead draw for most of an act.

Three Slimed status cards were forced into me in fight 3 and appeared in the
floor-5 deck list; they were gone from the floor-6 list, so they are combat-only.
That is worth saying because the floor-5 map screen made them look permanent and I
briefly planned a 75-gold shop removal around them.

---

## Fight 1 — Nibbit, HP 45/45

Opening hand: Ka-pow! (0), Strike ×2, Defend, Jumpy Dumpty. Enemy telegraphed
Attack 12.

**Turn 1.** Played Jumpy Dumpty → Strike → Strike (12 damage, Nibbit 45→33), then
Ka-pow! for free at 0 energy: 8 (the Bomb) + 4 = 12, Nibbit → 21.
*Rejected:* holding Ka-pow! a turn. The card Retains and the Bomb line says bombs
"grow 4 a turn", so waiting turns an 8 into a 12 — but detonating now also placed
the Mine 3 on the enemy (Jumpy Dumpty's rider) a full turn earlier, and a Mine
"goes off before its enemy's hit" on its own. I ran the arithmetic on the screen
and the immediate detonation won by three points of damage over two turns. That
was a real decision, made entirely off printed text, on turn one.
*Also rejected:* Defend. Nothing in the fight was going to be blocked profitably
at 5 while a 45-HP enemy still had 45 HP.

**Turn 2.** The Mine had gone off during the enemy's turn: Nibbit 21→18, and Spark
went 2→3, which is Pounding Surprise paying out. **The Mine dealt 3, not 7** — it
detonated at its printed size without taking the turn's growth. So growth happens
at the start of *my* turn, and a Mine placed on turn N pays its base value on turn
N+1. Nothing on the screen says that; I worked it out from the HP.
Played Grounded → Strike → Defend.
*Rejected:* three Defends for 15 block against a telegraph the page itself flagged
as "a part it MAY perform". Grounded is a Power and compounds, so it goes down on
the earliest turn I can afford it.

**Turn 3.** Nibbit at 12 HP behind 5 Block. Played Strike, Strike, Ka-pow!,
Defend — 16 raw against 17 of effective HP, so it lived on 1.
*Rejected:* **Sparks 'n' Splash** (2 energy, "at the end of your turn, deal Pyro
damage to a random enemy equal to its largest Bomb"). With no Bomb on the field it
is a two-energy card that deals zero, and the fight was ending. This is the first
time the card was in my hand and the first time it was unplayable-in-practice; it
happened again in fight 4.

**Turn 4.** Nibbit at 1. Played Strike. **No rejected alternative — this turn
presented no decision.**

Reward: Rosaria — Ravaging Confession ("Deal 9 damage. If the enemy has an aura,
apply 1 Vulnerable", Cryo) over Dodoco Cover, Careful Now and Rapid Fire. 9 for 1
is above rate, my deck paints Pyro constantly, and the Bomb keyword says outright
that "only Vulnerable and a cap move it" — so a Vulnerable source is a Bomb
amplifier. That reasoning turned out to be exactly right in fights 3 and 4.

---

## Fight 2 — Shrinker Beetle, HP 38/38

An "Unknown" node that opened into a fight.

**Turn 1.** Jumpy Dumpty (Bomb 8) → Strike (6) → Rosaria (9), all on the Beetle;
38 → 23. Rosaria left a Cryo Aura 2.
*Rejected:* Defend against a "Strategic (DebuffStrong)" telegraph — block does not
stop a debuff, and the screen told me the intent was a debuff, so blocking would
have been pure waste.
*The deliberate part:* I spent the turn painting Cryo on a target I had just
bombed, specifically so that next turn's Pyro detonation would react.

**Turn 2.** The Beetle's debuff landed: `Shrink -1 — While Shrinker Beetle is
alive, your Attacks deal 30% less damage`, and every attack in my hand reprinted
itself at the reduced number (Strike 6→4, Ka-pow 4→2). That is very good screen
work: the debuff was legible in the card faces, not just in a status line.
Ka-pow! now carried `*Reaction preview: Melt* — Pyro meets Cryo: this hit deals
1.75x damage and consumes the aura`, and the Bomb read `Bomb 12`.
Played Ka-pow! alone, for 0 energy. The Bomb went off as a Pyro hit, took the Cryo
aura, and Melted: 12 × 1.75 = 21, plus Ka-pow!'s own 2. **Exactly lethal on 23.**
*Rejected:* holding Ka-pow! one more turn for a Bomb 16. The aura printed `Cryo
Aura 1 — clings for 1 more turn`, so waiting would have traded a 1.75× multiplier
for four points of bomb growth. This is the best decision the kit offered me all
round: **bomb growth and aura expiry run on different clocks and the screen prints
both numbers**, so the tension is legible and the answer is not obvious.
*Also worth recording:* Shrink is an Attack modifier and the Bomb keyword says a
Bomb "is not an Attack". The 21 confirms bombs ignored the 30% cut. The screen
never says this in one place; I inferred it and the outcome agreed.

Reward: Sizzle over Mine Toss, Chain Fuse, Charlotte. I had exactly one Set off
card and wanted a second that is never dead (6 damage floor).

---

## Fight 3 — Twig Slime (S) 10, Leaf Slime (M) 33, Leaf Slime (S) 14

**Turn 1.** Lisa — Lightning Rose → Strike on the Twig → Ka-pow! on the Twig
(6 + 4 = exactly 10, killed) → Defend.
*Rejected:* dumping the same 10 into Leaf Slime (M). Killing the 10-HP body
removed 4 damage a turn permanently for the same points; the M slime's telegraph
was status cards, not damage.
*Rejected:* saving Lisa. She Exhausts and runs "for 3 turns", so every turn she
sits in hand is a tick thrown away.

**Turn 2.** Rosaria now printed `*Reaction preview: Superconduct* — Electro meets
Cryo: the reacted enemy gains 2 Vulnerable`, because Lisa had painted Electro.
Played Jumpy Dumpty (Bomb 8) → Rosaria → Strike, all on Leaf Slime (M): 28 → 6.
That is 22 from cards printing 9 and 6. The board then read
`Vulnerable 3 (debuff) — Receive 50% more damage from Attacks for 3 turns`, and
the arithmetic only closes if **Superconduct's Vulnerable applied before Rosaria's
own damage resolved** (13 + 9 = 22). Rosaria buffed herself with her own reaction.
Nothing printed says the order; I had to reverse-engineer it from two HP numbers.
*Rejected:* killing Leaf Slime (S) with the same 15 points. I chose to load
Vulnerable onto the body that was already carrying my Bomb, because the Bomb line
had just started printing `Set off here deals 12 Pyro damage **after Vulnerable**.
Bombs here: 8` — **the single best piece of screen text in the whole round**: it
shows base and effective side by side and names the reason for the gap.

**Turn 3.** Lisa's tick killed Leaf Slime (M) at end of my turn, and the Bomb
transferred — `A kill moves them to a survivor` — landing on Leaf Slime (S) and
then growing to 12. Played Sizzle: 12 (Bomb) + 6 = 18 into a 14-HP body. Won.
*Rejected:* Sparks 'n' Splash again, for the same reason as fight 1 — two energy
in a fight that was ending on the current turn.

Reward: Ammo Scavenging over Rapid Fire, Witches' Circle, Lisa — Violet Arc.
I picked it because through three fights my bottleneck had been **one** bomb
placer. Witches' Circle was tempting and I could not evaluate it: see (c).

---

## Fight 4 — Nibbit 42, Nibbit 44

**Turn 1.** Lisa → Jumpy Dumpty on Nibbit (2) → Rosaria on Nibbit (2). 44 → 35,
Bomb 8 planted, Cryo painted.
*Rejected:* Pocket Fireworks instead of Rosaria — identical 9 damage, but Rosaria
leaves the Cryo aura that makes the next Pyro detonation worth 1.75×. Same number
on the card, very different turn.

**Turn 2.** Ka-pow! now printed **two** reaction previews at once — Overloaded
(against the Electro-painted Nibbit 1) and Melt (against the Cryo-painted
Nibbit 2). Played Ka-pow! on Nibbit (2): Bomb 12 Melted for 21 plus Ka-pow!'s 4 =
25, 35 → 10. Then Strike, Strike to kill it, then Defend.
*Rejected:* Ka-pow! on Nibbit (1) for Overloaded (6 to ALL + 1 Weak). Six AoE and
a Weak against 21 on a single target — the screen gave me both numbers and the
choice was arithmetic, which is the good kind of choice.
*Rejected:* Sparks 'n' Splash a third time. One Bomb on the field, about to be
detonated, and the power targets *randomly* — a coin flip between 12 and 0, in
exchange for not killing the enemy telegraphing 14.

**Turn 3.** The kill had moved the Mine onto the survivor, which now carried two:
`Mine 14 — Bombs here: 7 / 7, including 2 Mines`. Played Sizzle: the first Mine's
Pyro hit took the Electro aura → Overloaded (6 to all, 1 Weak), second Mine 7,
Sizzle 6 + 6 for its own reaction rider = **32 damage from a 1-cost card**, 37 → 5,
and the Weak dropped the incoming 14 to 10. Then Ammo Scavenging, which drew 2
because two Bombs had gone off.
*Rejected:* letting the Mines auto-fire before the enemy's hit. That is 14 damage
free; setting them off myself was 32 and applied Weak before the swing. Genuinely
the most satisfying turn of the round, and every input was on the screen.

**Turn 4.** Strike for the last 5. No rejected alternative.

Reward: Tinder Toss (1 **Spark**, not energy) over a second Pocket Fireworks,
Sorry Jean, Sayu. Four fights in, Spark had been accumulating to 4–5 per combat
with **nothing in my deck that could spend it**. I bought the sink.

---

## Fight 5 — Inklet 12, Inklet 11, Inklet 17, all `Slippery 1`

`Slippery 1 — The next time Inklet loses HP, it only loses 1 HP instead.`

**Turn 1.** Strike into Inklet (2) (stripped Slippery for 1), Strike again (6),
then Lisa, then Tinder Toss for its Spark.
*Rejected:* spreading the two Strikes across two bodies. Slippery makes the first
hit on each body worth 1 regardless of size, so the correct play is to double up —
this is the one enemy in the round that punished my kit's shape, since a Klee deck
wants one enormous hit and Slippery taxes exactly that. Multi-hit cards (Tinder
Toss, Rapid Fire, a Mine stack) are the counter, and I owned one.
*Rejected:* Defend. Three attackers for 12 total against a 5-point card.

**Turn 2.** Rosaria showed both previews again. Played her into the **Pyro**-painted
Inklet for Melt: 9 × 1.75 = 15, 16 → 1.
*Rejected:* Rosaria into the Electro-painted Inklet for Superconduct, which would
have killed that body outright (13 vs 11 HP). I chose the Melt because it set up a
Strike to remove the 10-damage attacker instead of the 6-damage one — 6 damage
taken rather than 10. This is a good decision: two reactions, both correct-looking,
separated only by which enemy I wanted dead first.
Strike killed it, Strike chipped the other, Lisa's tick finished the fight.

Reward: Bang Bang! (2 Sparks: set off, 8 damage, place a Bomb 4). A second Spark
sink, and one that both spends and re-creates the Bomb it consumes.

---

## Fight 6 (ELITE) — Bygone Effigy, HP 127/127

`Slow 0 — Whenever you play a card, this enemy receives 10% more damage from
Attacks this turn.` Sleeping on turn 1.

Bang Bang! printed `CANNOT BE PLAYED: you have 1 Spark, and this costs 2` — the
refusal is on the card face, before I ask. Good.

**Turn 1.** Strike → Strike → Rosaria, cheapest first, biggest last, because Slow
increments *per card played* and therefore rewards ordering. 127 → 105, Slow 30.
*Rejected:* Rosaria first. Same three cards, roughly 3 fewer damage. The card order
inside a turn mattered, which is a real (if small) decision the screen supports —
`Slow 30 ... (Receives 30% more damage)` prints the running total.
*Rejected:* blocking. It was asleep and the screen said so.

**Turn 2.** Slow had reset to 0, confirming "this turn". Ammo Scavenging (Bomb 4)
→ Defend → Defend → Tinder Toss, which Melted the fresh Bomb off the Cryo aura and
hit twice at Slow 40. 105 → 88, and Spark ended where it started (spent 1, Pounding
Surprise refunded 1 for the detonation).
*Rejected:* letting the Bomb grow instead of detonating. The aura printed
`Cryo Aura 1` — one more turn — so growth and reaction were again on different
clocks, and here I chose the reaction. **I noted at the time that the two Defends
were pure waste as block** (the telegraph was Empower, no damage) **and I played
them anyway as Slow fuel.** That is an honest oddity: an enemy mechanic turned my
dead defensive cards into damage, which is more interesting than what those cards
normally do.

**Turn 3.** The Effigy woke up with `Strength 10` and a 23-damage telegraph, and
**I had no block card in hand at all**. Grounded → Ka-pow! → Strike → Pocket
Fireworks, ordered for Slow. 88 → 66. Took 23. **HP 37 → 14.**
*Rejected:* Lisa. 15 damage over three turns against a body I was no longer sure I
would live three turns in front of.
This is where I was plainly outplayed by my own deckbuilding: four Defends at 5
apiece and one Grounded at 6 is not a defence against 23, and I had known that for
two floors and taken damage cards anyway.

**Turn 4.** HP 14, block 6 from Grounded, 23 incoming, one Defend in hand. Played
Defend (11 block total), Jumpy Dumpty (Bomb 8, to be a 12 next turn), Strike.
Took 12. **HP 2.**
*Rejected:* Sparks 'n' Splash, finally drawn at a moment when a Bomb existed — but
two energy for 8 random-target damage, in a turn where the alternative was the
Defend that kept me alive, is not close. Across six fights **Sparks 'n' Splash was
never once the right card.**

**Turn 5, at 2 HP against 59 remaining.** I counted the whole turn before playing
anything. Colorless Potion offered Finesse / Purity / **Salvo** (12 damage, 1
energy) and I took Salvo. Then, ordered so the non-damage cards banked Slow first:
Ammo Scavenging (Bomb 4, joining the Bomb 12) → Strike (7 at Slow 20) → Salvo (15
at Slow 30) → Tinder Toss at Slow 40, which set off **both** Bombs (12 + 4 = 16,
unmodified — bombs are not Attacks so Slow did not touch them) and hit twice for 11.
59 → **10**, exactly the number I had predicted. Fire Potion for 20. **Elite dead,
me at 2 HP.**
*Rejected:* Finesse (4 block + draw) from the potion. Four block against 23 is not
survival; the only line that lived was the one that killed. And *rejected:* Poison
Potion — 6 Poison ticks after the enemy's turn, which was a turn I did not have.
*This turn is the round's high point.* Every input — bomb sizes, the Slow
percentage, the Spark price, the potion's damage — was printed, and a five-card
lethal at 2 HP was computable in advance and then landed on the number.

Reward: Diona — Shaken, Not Purred (6 Block, Cryo twice, +5 Block if a Bomb goes
off) over Sugar Rush, Perfect Timing, Witches' Circle. Six fights had told me the
deck's hole was block, and Diona is the first card I was offered that gives block
*and* paints the Cryo the detonations want.

---

## The kit, after 6 fights

**(a) Which decisions felt like real choices, and what they traded off.**

The kit's central decision is genuinely good and it is available on turn one:
**detonate now, or let the Bomb grow.** It works because two clocks run against
each other and the screen prints both numbers — `Bombs here: 8, growing each turn`
against `Cryo Aura 1 — clings for 1 more turn`. In fight 2 I gave up four points
of growth to keep a 1.75× Melt; in fight 1 I gave up four points of growth to start
the Mine a turn early; in the elite's turn 2 I did it again for the reaction. Same
question, three different right answers, all decided by arithmetic I could actually
do. That is the good axis.

Second real choice: **which reaction**. Once two elements are on the board Rosaria
prints two previews at once, and picking Melt over Superconduct (fight 5) is
picking which enemy dies first, not which number is bigger. The `*Reaction
preview:*` line on the card face is what makes this playable blind — without it I
would have been guessing.

Third: **the Spark economy is a separate resource with its own decisions.** Tinder
Toss and Bang Bang! cost Sparks, not energy, so they are free actions layered on
top of a normal turn, and Pounding Surprise refunds a Spark per detonation. In the
elite's lethal turn my energy did three cards and my Sparks did a fourth. The face
even pre-empts the obvious rules lawyering: *"an effect that makes a card free to
play... covers Energy only, and the 1 Spark is still spent."*

Fourth, and I did not expect it: **card order within a turn** mattered twice — Slow
rewards ordering, and Rosaria's Superconduct buffs her own damage.

**(b) What felt automatic, and what never seemed worth playing.**

**Sparks 'n' Splash is the dead card of this deck.** Two energy, a Power, "at the
end of your turn, deal Pyro damage to a random enemy equal to its largest Bomb."
It was in my hand in fights 1, 3, 4 and 6 and I **never played it once**, and I do
not think I was wrong any of those times. It needs a Bomb alive at end of turn —
but every other card in the deck wants that Bomb detonated *now*, and the two
Set off cards are the deck's best cards. It also targets randomly. It is a payoff
card for a board state its own deck is built to destroy.

Grounded has the same problem in miniature, stated out loud: *"if none of your
Bombs went off last turn."* It is a Power that pays you for not doing the thing the
character does. It was fine in fight 1 (a slow four-turn fight where I had no bomb
up) and it saved my life on the elite's turn 4 — but noticing that it is
anti-synergy with the whole kit took me about four seconds, and the tension never
resolved into an interesting choice; it just meant Grounded is good in the fights
where the kit is bad.

Automatic: Strike and Defend, unsurprisingly, and roughly half of all turns were
"play the three cards, there is no other assignment of three energy". Fight 1's
turn 4 and fight 4's turn 4 were single-card lethals with no decision at all.

**(c) What I could not understand, or that contradicted its own printed text.**

1. **Lisa's Vulnerable is invisible and I believe it is very close to dead text.**
   The card promises "deal 5 Electro damage to a random enemy **and apply 1
   Vulnerable**". I played her in three fights and **never once saw a Vulnerable
   stack on any board**. The explanation is on the keyword itself — she fires at
   the end of *my* turn, and `One stack falls off at the end of each of its turns`
   — so the stack is created and expires inside the enemy's turn, before I get
   another look. It is only doing work for damage that lands during the enemy's
   turn, which for me means Mines and nothing else. I cannot tell from any printed
   text whether that is the design or a bug, and the fact that a purchased 74-gold
   card's second clause is unobservable is the thing I most want someone to check.
2. **Hexerei is a keyword I could not evaluate.** `Hexerei — A Companion card that
   prints the word, and Klee herself. Some are Klee's own, some are not.` I was
   offered Witches' Circle ("Whenever you play a Hexerei card, place a Bomb 3")
   twice and skipped it both times, because **not one card in my deck printed the
   word**, including two Companions (Rosaria, Lisa) and Klee's own cards. Sucrose
   printed `Hexerei.` as a line of card text, which proves the word does appear —
   so either my deck genuinely had no Hexerei cards, or the tag is not being
   printed where it needs to be. Either way the reward screen asked me to price a
   card against information the deck screen does not carry. That is a real
   purchasing decision I had to make blind, twice.
3. **The Mine's first detonation ignores its growth.** Jumpy Dumpty's Mine 3 was
   still worth 3 when it fired on the enemy's turn, not 7. Consistent, but nothing
   printed tells you which side of the growth tick a Mine lands on, and it changes
   whether the rider is worth the card.
4. **Whether Superconduct's Vulnerable applies before or after the damage of the
   card that caused it.** From the numbers it applies first, and Rosaria therefore
   amplifies herself by 50%. That is a 4-point swing on a 1-cost card and it is
   nowhere on the screen.
5. **`Beating Remnant`** was claimed as an elite relic and no subsequent screen
   reprinted its text, so I finished the run holding a relic I cannot describe.
   Every other relic I own prints in the combat header.

Against all of that: the reaction rules text is *long*, and it is long in the right
way. The paragraph explaining that a reacting hit leaves no aura behind, and the
paragraph warning that a re-applied aura can make a reaction look as if it did not
happen, both answered questions I actually had while playing. And the two lines
`Set off here deals 12 Pyro damage after Vulnerable. Bombs here: 8` and
`CANNOT BE PLAYED: you have 1 Spark, and this costs 2` are the clearest pieces of
UI text I met.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

Never wanted: **Sparks 'n' Splash** — four appearances, zero plays, and I would
make the same call again in all four. Runner-up is Grounded, for asking me to stop
doing the fun thing.

Happiest to draw: **Sizzle**. It is a 1-cost attack with a floor of 6 that turned
into 32 damage plus a Weak in fight 4 because two Mines and an Electro aura had
piled up behind it, and it never once cost me a turn when the board was empty.
**Ka-pow! is the more spectacular card** (0 cost, Retain, and it did 25 in one
click on the elite's fight) but Sizzle is the one whose good turns I *built*.

**(e) Did the first turn of the first fight already present a decision?**

**Yes, and a good one.** The opening hand was Ka-pow!, Strike, Strike, Defend,
Jumpy Dumpty, and after spending three energy I still had a free 0-cost Retain
detonator and a choice: set off a Bomb 8 now and start the Mine, or hold and set
off a Bomb 12 next turn. I did the arithmetic on printed numbers alone, chose to
detonate, and it was correct by three points. No first turn in this round was a
"play everything, there is no ordering" turn — which is more than I can say for
about half the turns that followed.

---

## Non-blindness declaration

Commands run outside the two allowed ones, all via the Bash tool:

1. `mkdir -p <scratchpad>/... && echo "lane2 klee round15 run2 notes" > <scratchpad>/notes.md`
   — created a scratch notes file at the start. I never appended to it or read it
   back; I kept the action count from the bridge's own `actions: N of 120` line
   instead. Declared for completeness.
2. `... | sed -n '<range>'` on the output of `observe`, many times, to print only
   the header, the hand, or the enemy block instead of the whole screen. All ranges
   were non-overlapping within a single invocation.

Tools used: **Bash** (for the two allowed commands and the two items above) and
**Write** (once, for this file).

No `harness state`, no `scenario`, no `staged_turn`, no `soak`, no other understudy
subcommand. No `git` command. No web access.

**Repo files read: none.**
