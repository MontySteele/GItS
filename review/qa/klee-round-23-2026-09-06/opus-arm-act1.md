# Blind seat record — KLEEMOD-KLEE, lane 2, Act 1

## Identity

- **Model / seat:** Opus (Claude Fable 5.1), blind TESTER seat, lane 2.
- **Run seed:** CP58TQFK2JYV. **Character:** KLEEMOD-KLEE. **Ascension:** 1.
- **Act:** 1. The map named the act boss **Ceremonial Beast** (never reached).
- **Actions accepted:** 120 of 120.
- **Termination:** action budget. The 120th accepted act was `play "Sizzle" on "A"`
  in round 5 of the elite; I stopped mid-turn without ending it, as the brief
  instructs. Wall clock was nowhere near its cap. Two refusals occurred, never
  consecutive.
- **HP trajectory:** 62/62 → F1 62 → F2 50 → F3 46 → F4 40 → F5 31 → elite 13,
  **stopped at 13/62 with 0 Block facing a printed 23-damage intent**, elite at
  18/127. I expect that hit killed me; I did not see it land.
- **Gold at stop:** ~89 (99 start, +20/+11/+12/+16/+18 from fights, −87 in the shop).
- **Potions held:** none. All three were spent in the elite (Skill Potion ×2,
  Touch of Insanity).
- **Relics:** Pounding Surprise (*Whenever a Bomb goes off, gain 1 Spark*),
  Scroll Boxes.
- **Deck at the end** (26 cards; counts of Strike/Defend I could not pin down
  from the screens, so they are given as "several"): Jumpy Dumpty (Innate),
  several Strike, several Defend, Ka-pow!, Pocket Match ×2, Tinder Toss,
  Rapid Fire, Bang Bang!, Fireworks Show, Dig In, Powder Charge,
  Ammo Scavenging, Split Charge, Careful Now, Sizzle, Countdown,
  Sorry Jean..., Fish-Flavored Bait, Kaeya — Cold-Blooded Strike.
  *(I was told six cards were granted into the starting deck for this round.
  Nothing on any screen marked which they were; from the bundle screen I can
  say Pocket Match / Ammo Scavenging / Split Charge came from Neow, so the
  grants are somewhere among Ka-pow!, Tinder Toss, Rapid Fire, Bang Bang!,
  Fireworks Show, Dig In, Powder Charge.)*

**Neow pick: Scroll Boxes**, then the bundle *Pocket Match / Ammo Scavenging /
Split Charge*. Why: the opening screen told me Sparks are a second currency that
starts at 1 and only grows when a Bomb goes off, and the rival bundle
(Dig In / Fwoosh! / Powder Charge) was three Spark-priced cards competing for
that one scarce pool, while the bundle I took has two Energy-priced cards. I
took the bundle that spent the resource I expected to have spare. That guess
turned out to be the correct read of the kit, and the whole run confirmed it.

---

## Fight 1 — Leaf Slime (S) [A] 15, Twig Slime (M) [B] 28, Twig Slime (S) [C] 10

**Turn 1.** Jumpy Dumpty on B → Pocket Match on B → Tinder Toss → Strike on C → Defend.

Jumpy Dumpty prints *"Place a Bomb 8. When it goes off, place a Mine 3 on ALL
enemies."* The rejected alternative was to place the Bomb and **not** detonate,
since the Bomb keyword prints *"grows 4 a turn"* — Bomb 8 would have been Bomb 12
next turn. I rejected it because detonating converts one Bomb into three Mines,
and Pounding Surprise pays a Spark per Bomb that goes off, so the detonation is
the thing that starts the engine rather than the thing that spends it. It paid
exactly: B took 8 + 5 = 13, three Mine 3 appeared, and my Spark went 1 → spent
1 → back to 1.

Tinder Toss then cost 1 Spark and returned 2, because both of its hits found
Mined bodies (A and C, 7 each). That is the moment the kit taught me its economy:
**detonation is Spark-positive, so the Spark-priced attacks are close to free as
long as something is Bombed.** Strike finished C (the 4-damage attacker) rather
than A because C was in exact kill range after the Mine.

**Turn 2.** Fireworks Show → Ammo Scavenging on B → Rapid Fire.

B's Mine had grown 3 → 7 at turn start, and B's intent printed *"Attack for 11"*.
The rejected alternative was Dig In + Defend (13 Block, stall a turn and let the
Mine grow again). I rejected it on B's printed HP: 15, and I could count 7 (Mine)
+ 4 (a Bomb I could place) + 3 (Rapid Fire's first hit) = 14, one short — so I
sequenced to make the shortfall irrelevant: **Fireworks Show first** so the Mine
detonation would be counted by Ammo Scavenging's *"Draw 1 card for each of your
Bombs that went off this turn"*, then Ammo Scavenging (Bomb 4, drew 1), then
Rapid Fire, whose first hit prefers a Bombed body and so opened on the fresh
Bomb 4. B died on the second Rapid Fire hit. That is one decision (the ordering)
carrying the whole turn, and it was a real one.

**Turn 3.** Ka-pow! on A for lethal. A was at 2; Ka-pow! is 0 cost. No decision —
and I say so: this was the tail of the plan, not a turn.

**Result:** won on round 3, **62/62, no damage taken**. End-of-fight Spark: 2.

---

## Fight 2 — Nibbit [A] 45/45, intent "Attack for 12"

**Turn 1.** Jumpy Dumpty on A → Split Charge → Strike.

The interesting choice was **Split Charge on a single-enemy board**. Its text is
*"Split your largest Bomb into two halves on random enemies"*, which reads like a
multi-target card and looks dead against one body. I played it anyway on the
reasoning that Bomb growth is per-Bomb (*"each grows 4 a turn"*), so two Bomb 4s
grow at +8/turn where one Bomb 8 grows at +4. The screen then printed exactly
that and did the arithmetic for me:

> **Bomb 8** — Set off here deals 8 Pyro damage, **in 2 hits for 2 Sparks**.
> Bomb sizes here: 4 / 4, growing each turn.

Next turn it read **Bomb 16 (8 / 8)**. The rejected alternative was a second
Strike (6 now) instead of Split Charge; splitting was worth +4 Bomb per turn and
+1 Spark per detonation, which beat 6 damage inside two turns. **This was the
best-designed decision of the run** — a card whose printed text hides its real
use, but whose payoff the screen then states in plain numbers.

**Turn 2.** Ka-pow! on A → Ammo Scavenging on A → Bang Bang! on A → Rapid Fire.

Nibbit's intent had become *"Attack for 6"* **and also** *"Defensive (Defend) —
This enemy intends to Block on its turn."* Set off prints *"Block stops them"*.
That single clause decided the turn: a Bomb 16 left to grow would meet a blocking
body, so I detonated immediately rather than banking. Ka-pow! (0 cost, Retain)
did 16 + 4 = 20 and paid 2 Sparks; Ammo Scavenging afterwards drew **2** cards
off the two detonations; Bang Bang! and Rapid Fire finished from 19.

Rejected alternative: three Defends and one more growth turn. Rejected on the
printed Block intent — correctly.

**Result:** won on round 2, **50/62**. End-of-fight Spark: 3.

---

## Fight 3 — Fuzzy Wurm Crawler [A] 56/56, intent "Attack for 4"

**Turn 1.** Jumpy Dumpty on A → Ammo Scavenging on A → Strike.

Deliberately did **not** detonate. The enemy's printed intent was 4 damage — the
cheapest turn in the run to spend on setup. Two Bombs (8 and 4) meant +8/turn.
Rejected alternative: Tinder Toss for an immediate 8 + 8; rejected because 4
damage a turn buys two more growth turns cheaply.

**Turn 2.** Kaeya — Cold-Blooded Strike on A, then **end turn holding Ka-pow!**.

Bombs read **Bomb 20 (12 / 8)**. The enemy's intent was *Empower (Buff)* — no
damage. Kaeya is the run's only Cryo card; the Elemental Reaction glossary and
**Melt** (*"Pyro on a Cryo aura … 1.75x"*) told me a Cryo aura would multiply the
first Bomb hit. After Kaeya the header changed to:

> **Bomb 29** — Set off here deals 29 Pyro damage, in 2 hits for 2 Sparks.
> Bomb sizes here: 12 / 8

**The screen priced the reaction for me before I committed** — 12×1.75 + 8 = 29.
That is excellent legibility and it is what made the next decision possible.

I then held Ka-pow! (Retain) rather than firing for 29 + 4 = 33 into a 42-HP body.
Rejected line: detonate now, leave it at 9, eat one buffed attack. Taken line:
end the turn on a Buff intent, let both Bombs grow one more step, and read the
number off the screen next turn. This is the clearest case in the run of a plan
set two turns earlier paying off.

**Turn 3.** Ka-pow! on A. Screen read **Bomb 40 (16 / 12)** with Cryo Aura 1 still
up; the buff had been **Strength 7**. 40 + 4 = 44 against 42 HP. Dead, and I never
took the buffed hit.

**Result:** won on round 3, **46/62** (only the 4-damage turn-1 hit landed).
End-of-fight Spark: not observed — 2 at the start of the killing turn, +2 owed
from the two halves.

---

## Fight 4 — Assassin Raider [A] 22, Crossbow Raider [B] 20, Axe Raider [C] 21

**Turn 1.** Jumpy Dumpty on A → Sizzle on A → Pocket Match on A → Countdown on B.

Placed on A rather than B or C because A was the only body **not** printing a
Block intent, and *"Block stops them"* makes a Bomb on a blocking body a
liability. A died exactly: 8 (Bomb) + 6 (Sizzle) + 3 (its own new Mine) + 5
(Pocket Match) = 22.

Then a genuine sub-decision: C's intent printed an attack, so its Mine would go
off on its own before the hit (*"A Mine also goes off before this enemy's hit"*),
free. B's intent was Block-only, so B's Mine would **never** self-trigger and
would be eaten by the Block it was about to gain. So I spent Countdown on **B**
and left C's Mine to detonate itself. That was reading two printed clauses
against each other, and I would call it the second-best decision of the run.

**Turn 2.** Bang Bang! on B → Careful Now → Tinder Toss → Rapid Fire (B died).

Careful Now (*"Gain Block equal to your largest Bomb when played, up to 10"*)
gave **4**, because the only Bomb on the board was the Bomb 4 Bang Bang! had just
placed. Playing it before the detonation instead of after was the whole of its
value. Tinder Toss's first hit took B (Bombed), its second took C (unBombed, into
Block 5). Rapid Fire killed B.

I then chose **not** to play Dig In. Block was already 4 against a printed 5, so
8 more Block for 1 Spark would have bought exactly 1 HP. Small, but a real price
check, and worth recording as the only time the Spark price was correctly
refused rather than unaffordable.

**Turn 3.** Strike on C → Kaeya on C — **and the fight ended a card early.**

I had planned Strike + Kaeya + two Bomb placers and had modelled C at 4 HP
afterwards. Instead Kaeya killed it. **I had mis-modelled my own kit:** C wore a
Pyro Aura that *my own* Bomb detonations had applied, and Kaeya is Cryo, so
Kaeya Melted for 1.75× (8 → 14) into a 12-HP body. Every clause needed for that
was printed on the screen in front of me and I still did not see it. Recording
that plainly: **the reaction rule is legible but not salient — I read Melt as a
thing I do to the enemy, not a thing my own Pyro sets up against my own Cryo.**

That produced my first refusal: I asked for `play "Powder Charge" on "C"` and got
*"you are not in a battle."*

**Result:** won on round 3, **40/62**. End-of-fight Spark: 2.

---

## Fight 5 — Twig Slime (M) [A] 28, Leaf Slime (M) [B] 32, Leaf Slime (S) [C] 11, Twig Slime (S) [D] 7

All four opened on *Strategic (StatusCard)* intents — 4 status cards a round, and
only D threatening damage (4).

**Turn 1.** Jumpy Dumpty on B → Ka-pow! on B → Fireworks Show → Tinder Toss → Defend.

Fireworks Show printed **CANNOT BE PLAYED: you have 1 Spark, and this costs 2**
at the top of the turn. The line I found around it is the good one: play Ka-pow!
(0 Energy) first, whose detonation of the Bomb 8 pays a Spark, which **unlocks
Fireworks Show inside the same turn**. Fireworks then set off all four Mine 3
for 12 damage and **four** Sparks. Spark went 1 → 4 across the turn while I spent
2 of it. Rejected alternative: hold the Bomb to grow, since incoming was only 4 —
rejected because four status-card intents meant the deck was being poisoned every
round and the clock was the clog, not the damage.

Tinder Toss with **no** Bombed body on the field put both hits into B (17 → 9).
With nothing to prefer, the randomness doubled up.

**Turn 2.** Bang Bang! on B → Countdown on B (B died) → Strike on D (D died) → Defend.

Incoming had jumped to 26 (11 + 8 + 3 + 4). Rejected alternative: let Bang Bang!'s
Bomb 4 ride on B, kill B with Strike, and let the Bomb **migrate** — the Bomb
keyword prints *"If this enemy dies with it still on, it moves to a survivor."*
Tempting, but it costs 4 HP of incoming, because the alternative use of that
Strike was killing D outright. I killed D. I think that was right and I would like
to see the migration line tested by someone with more turns.

**Turn 3.** Powder Charge on C → Sizzle on C (C died). Both remaining bodies were
on StatusCard intents, so Block was worthless and **2 Energy sat idle**.

**Turn 4.** Kaeya on A → Rapid Fire → Pocket Match on A for exact lethal
(8 + 14 + 5 = A's 25). Rapid Fire's first hit Melted off Kaeya's Cryo (3 → 5).

One thing I could not explain: **Spark rose from 2 to 3 across Kaeya + Rapid Fire
with no Bomb anywhere on the field.** Pounding Surprise prints *"Whenever a Bomb
goes off"* and no Bomb existed. Either something other than a Bomb pays Sparks, or
the relic's text is incomplete. Flagged, not resolved.

**Result:** won on round 4, **31/62**. End-of-fight Spark: 2.

---

## Fight 6 (Elite) — Bygone Effigy [A] 127/127 — **unresolved, budget reached**

Printed debuff, which shaped every turn:

> **Slow 0** — Whenever you play a card, this enemy receives 10% more damage from
> Attacks this turn. **It counts the cards played BEFORE this one.**

**Turn 1** (enemy *Sleeping*). Sorry, Jean... → Jumpy Dumpty → Strike → Strike.

I opened with **Sorry, Jean... on an empty board on purpose**: it is 0 cost, it
removes a Bomb for Block and there were no Bombs, so it did nothing except add a
Slow stack for the attacks behind it. The tool accepted it with no complaint. The
two Strikes then landed at +20% and +30% for 14 total, and Slow read 40 at end of
turn. Rejected alternative: Jumpy Dumpty first — rejected because Sorry, Jean...
after a Bomb exists would have eaten the Bomb 8.

**Turn 2** (enemy *Empower*). Fish-Flavored Bait only.

**This is the turn to look at.** Hand was Careful Now, Fireworks Show, Defend,
Defend, Fish-Flavored Bait, holding **Bomb 12** on the board, and:

> **Fireworks Show** — cost 2 Sparks — **CANNOT BE PLAYED: you have 1 Spark, and
> this costs 2**

It was the **only detonator in hand**, and it was priced out. I could not earn a
Spark either, because Sparks come only from Bombs going off and the only card that
could set one off was the one I could not pay for. So the Bomb sat. I played
Fish-Flavored Bait for a second Bomb and passed with **2 Energy unspent**, because
the enemy's intent was a Buff and Block was worthless. That is the kit's failure
mode in one screen: **Spark-locked, Energy-flush, holding a live Bomb.**

**Turn 3** (intent 23, Strength 10). Careful Now → Countdown → Pocket Match → Kaeya.

Careful Now **before** the detonation for its capped 10 Block; Countdown for the
Bomb 24 (16 / 8) and a draw; then Pocket Match, then Kaeya last so that Melt
(1.75×) and Slow (+30%) multiplied together: 8 → 14 → 18. 51 damage in the turn.

The rejected alternative was Defend instead of Kaeya — 5 Block instead of 18
damage. I took the damage, went to 18 HP, and in hindsight the block was the
correct pick, because what killed the run was not the damage race but having no
Block floor at all.

**Turn 4** (intent 23, me at 18 HP, **zero Block cards in hand**).
Skill Potion → Stoke the Fuse → Powder Charge → Stoke the Fuse → Skill Potion →
Sorry, Jean... → Ka-pow! → Rapid Fire.

Stoke the Fuse (*"Spend all your Sparks. Your largest Bomb grows by 3 per Spark
spent"*) turned Bomb 6 into **Bomb 18** off 4 Sparks — and left me at **zero
Sparks**, which mattered a turn later more than the Bomb did.

Then the sharpest decision of the run, forced by a printed line I had to reason
about rather than read: **Rapid Fire and Ka-pow! both say "Set off", so either of
them would detonate the Bomb 18 before Sorry, Jean... could convert it.** The
Bomb was worth 18 damage or 18 Block, never both, and only if I spent it in the
right order. At 18 HP against a printed 23, I took the Block, played Sorry, Jean...
first, and survived on 13. Good tension; genuinely the most interesting card in
the deck.

**Turn 5** (intent 23, me at 13 HP, 0 Block, **0 Sparks, 0 cards left in the draw
pile**). Touch of Insanity → Sizzle made free → Strike → Strike → Sizzle.
**Budget reached mid-turn.**

The hand printed:

> **Pocket Match** — CANNOT BE PLAYED: you have no Spark, and this costs 1
> **Tinder Toss** — CANNOT BE PLAYED: you have no Spark, and this costs 1

Two of six cards were bricks, **Split Charge was a third** (no Bomb to split), and
there was no placer in hand, so there was no path back to a Spark. Best available
line was 19–20 damage into an 18-remaining body. I stopped at 120 accepted acts
with the elite on **18/127**, myself on **13/62 with 0 Block** against a printed
23. I did not see the hit land, but I could not have survived it.

---

## The kit, after 6 fights

**(a) Which decisions felt like real choices, and where they were made.**

- **Split Charge on a single enemy** (fight 2, on the turn). Trades 6 immediate
  damage for doubling Bomb growth and doubling Spark yield. The card's own text
  actively disguises this; the board header then states it exactly.
- **Detonate now or let it grow** (fights 2, 3, elite; on the turn, read off the
  enemy's intent line). This is the kit's core loop and it is a *good* one,
  because the answer changes with the printed intent: a Buff or Sleep intent says
  grow, a *Defensive (Defend)* intent says fire immediately since *"Block stops
  them"*, and a big Attack intent says fire before you die. Fight 3 was won by
  holding a Retain detonator for two turns; fight 2 was won by refusing to hold.
- **Ordering inside the turn** (elite, on the turn). Slow rewards playing cheap
  and free cards before attacks; Careful Now must be played before the
  detonation, Ammo Scavenging after it; Kaeya must come after a Pyro aura exists
  to Melt. Several of these are worth 30–80% of a card's output.
- **Sorry, Jean... — 18 damage or 18 Block from one Bomb** (elite, on the turn,
  set up two turns earlier). The best single decision the kit produced.
- **The Neow bundle** (at the draft). Choosing the Energy-priced bundle over the
  all-Spark bundle decided how many turns I had a playable detonator, and I felt
  that choice in the elite.

**(b) What felt automatic, and what never seemed worth playing.**

- **Ka-pow!** is a 0-cost Retain detonator. It is never a decision; it is what you
  do. It also produced the two biggest hits of the run (20 and 44). A free card
  that is always correct and sometimes enormous.
- **Strike and Defend** are pure filler here; the only interesting thing they ever
  did was add Slow stacks.
- **Kindling** and **Flame Dance** (seen in a reward and in the shop) key off
  *"an enemy whose aura is not Pyro"* — but the kit's own Set off **applies** Pyro
  to everything it touches. Both cards are anti-synergistic with the deck's core
  action, and I skipped them for that reason. That pattern looked like a mistake
  rather than a tension.
- **Split Charge with no Bomb, Careful Now with no Bomb, Sorry Jean... with no
  Bomb** are all live-but-null: they can be played, and do nothing. Careful Now
  for 0 Block in the elite and Split Charge as a dead card in the last turn were
  both real losses.

**(c) What I could not understand, or that contradicted its printed text.**

1. **Sparks appeared with no Bomb on the field.** Fight 5, turn 4: Spark 2 → 3
   across Kaeya + Rapid Fire with the board completely Bomb-free. Pounding
   Surprise prints only *"Whenever a Bomb goes off, gain 1 Spark."* Nothing on
   screen explains the third Spark.
2. **The Spark economy has no floor and the game does not say so.** Sparks come
   only from Bombs going off; Bombs only go off when a Set off card is played;
   most Set off cards cost Sparks. Nothing printed anywhere warns that the loop
   can zero itself out. It did, in the elite, and it ended the run.
3. **"A random one picks a Bombed enemy first"** is stated but never shown. When
   Tinder Toss fires twice or Rapid Fire four times, the screen prints only the
   after-state, so I could confirm *which bodies* were hit but never the order.
   Whether the preference applies to every hit or only the first is not
   observable from this bridge.
4. **Whether Slow's "+X% from Attacks" applies to Bomb damage** is unresolvable
   from the screen. The Bomb keyword says a Bomb is *"Not an Attack"*, so it
   presumably does not, but a detonation and its carrier card resolve as one
   number and I could never separate them.
5. **Stoke the Fuse.** *"cost 1 Spark. Spend all your Sparks."* — does the price
   count among the spent? I had 5 and got +12 (four Sparks' worth), so the price
   is paid first and not counted. That is inferable only by arithmetic after the
   fact.

**(d) The card I never wanted to play, and the one I was happiest to draw.**

- Never wanted: **Split Charge**, on any board where I did not already have a big
  Bomb — which is most of them, and it is dead rather than weak. **Fireworks
  Show** is a close second for the opposite reason: at 2 Sparks it is priced
  exactly out of the turns where I most wanted it.
- Happiest to draw: **Ka-pow!** every time. 0 cost, Retain, and its number is
  whatever the board has been growing. Drawing it means the turn works.
  **Sorry, Jean...** is the one I most enjoyed *thinking* about.

**(e) Did the first turn of the first fight already present a decision?**

Yes, a real one. The opening hand held Jumpy Dumpty (place a Bomb 8), Pocket
Match (spend my only Spark to set it off) and a printed keyword saying Bombs grow
4 a turn. Detonate-now-for-three-Mines-and-a-Spark versus hold-and-grow was a
genuine fork, decided by an enemy HP total I could read (C at 10, in exact kill
range once a Mine landed). Turn one taught the whole engine, which is the best
thing I can say about the kit.

**Three highest-value findings, in order.**

1. **The Spark loop can deadlock and there is no printed floor.** Elite round 2
   (Bomb 12 live, only detonator priced out at 1 Spark of 2) and round 5 (two
   cards reading *"CANNOT BE PLAYED: you have no Spark"*, no placer, no draw pile)
   are the same bug from both sides. Sparks require detonations, detonations
   require Spark cards, and nothing in the deck breaks the circle for free except
   Ka-pow!. The run ended there, not to damage.
2. **Klee has no Block floor, and her one great defensive card is conditional on
   the thing she also wants to spend.** Careful Now and Sorry, Jean... both read
   the Bomb, so on the turns you have no Bomb you have no defence, and on the
   turns you do, Block and damage are the same resource. The tension is excellent
   design; the *absence of any unconditional Block* underneath it is what makes
   the elite unwinnable at 31 HP.
3. **Energy and Sparks decouple badly on Klee's quiet turns.** I ended turns with
   2–3 Energy unspent and nothing to buy on four separate occasions (fight 3 t2,
   fight 5 t3, elite t2 and t3), and separately ended turns holding 4–5 Sparks
   with no Spark card in hand. Both currencies idle, in the same deck, in the same
   fight. Energy-priced kit cards (Countdown, Ammo Scavenging, Fish-Flavored Bait)
   fixed this the moment I drafted them, which suggests the shipped ratio of
   Spark-priced to Energy-priced cards is too high.

*Honourable mention, because it is a compliment: the board header does the
reaction arithmetic for you.* Seeing `Bomb 20` become `Bomb 29` the instant Kaeya
applied Cryo, and `Bomb 8` become `Bomb 8 … in 2 hits for 2 Sparks / 4 / 4` after
Split Charge, is the clearest in-game explanation of a multiplier I have read.
It is also the reason my only two real modelling errors (Kaeya Melting off my own
Pyro in fight 4, and the phantom Spark in fight 5) stand out — those were the two
places the screen did **not** show me the number in advance.

---

## Non-blindness declaration

- Allowed commands only, for all game actions:
  `GITS_LANE=2 python -m understudy.blindplay observe` and
  `GITS_LANE=2 python -m understudy.blindplay act "<command>"`. 120 accepted
  `act` calls; `observe` used freely and not counted.
- Other Bash use, all of it scratch or filtering, never a second data source:
  - `mkdir -p .../review/qa/klee-round-23-2026-09-06` (once, to create the
    directory for this file, as the coordinator instructed).
  - `cd` into the repo root as a prefix on every call.
  - `sed -n` and `grep -vE` piped over `observe` output, purely to re-read one
    block of a screen I had already been shown (hand, enemies, header). No
    command produced information the bridge had not already printed.
- Other tools: **Read**, used exactly once, on the brief at the scratchpad path
  the coordinator gave. **Write**, used exactly once, for this record.
- **Repo files read: none.** No YAML sheet, no C# source, no doc, no packet, no
  other seat's record, no `harness state` / `scenario` / `staged_turn` / `soak`
  or any other understudy subcommand.
- Refusals (2, never consecutive, both recorded above):
  1. `play "Powder Charge" on "C"` → *"you are not in a battle."* — Kaeya had
     already killed the last Raider via a Melt I had not predicted.
  2. `play "Strike (1)" on "A"` → *"a card chooser is open and has to be answered
     first — \"Choose a card to make free.\"."* — Touch of Insanity's overlay
     needed an explicit `confirm` after `choose`, which the potion's own text
     did not lead me to expect.
