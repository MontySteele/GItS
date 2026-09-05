# Klee — blind seat, round 18 (targeted), lane 1

## Identity

- **Model / seat:** Opus, blind TESTER seat ("cook"), lane 1.
- **Run seed:** `SX9ZHGZ3WXN5`. **Ascension 0.** **Act 1**, boss named on the map
  as **Lagavulin Matriarch** — never reached; the budget ran out on floor 12 of
  17, six floors short of the boss.
- **Actions accepted:** 120 of 120.
- **Termination:** action cap. The bridge printed `actions: 120 of 120` on my
  last `end turn`; I stopped mid-fight 6 (round 3, one Two-Tailed Rat left at
  17/21 intending to Summon). No wall-clock or stall stop; one refusal all round.
- **HP trajectory:** 62 → 47 (fight 1) → 36 (fight 2) → 22 (fight 3) → rest 40 →
  22 (fight 4) → rest 40 → 30 (fight 5) → rest 48 → **29** (mid-fight 6).
  Never below 22.
- **Gold:** 89. Spent 123 at the one shop; the Gremlin Merc stole 20 and I got it
  back by killing the Fat Gremlin that carried `Heist 20`.
- **Potions:** 1 of 5 slots — **Gambler's Brew**. Spent a Fire Potion in fight 4.
- **Relics:** Pounding Surprise (start), Winged Boots (Neow, all 3 charges used),
  Potion Belt (floor-9 chest).
- **Deck at the end** (22): Albedo — Solar Isotoma, Barbara — Front Row Seat,
  Big Badda Boom, Careful Arrangement, Chain Fuse, Defend ×4, Grounded,
  Jumpy Dumpty, Ka-pow! (Sharp 2), Mine Toss, Pocket Match, Pop!, Rapid Fire,
  Sizzle, Sorry Jean..., Stoke the Fuse, Strike ×4.

**Neow pick: Winged Boots** ("ignore paths 3 times"). I took it over Neow's
Torment and Dowsing Rod because I had been told six extra cards were already in
the deck, so a third-adding option looked like more dilution of a deck I had not
read yet, and Dowsing Rod wanted 5 `?` rooms I could not promise in one act. In
hindsight the Boots were quietly good: they paid for the lane jump to the shop.

---

## Fight 1 — Toadpole (1) [A] 22 HP, Toadpole (2) [B] 21 HP

Opening hand Strike ×2, Defend ×2, Ka-pow!. Draw pile 11, so 16 cards total —
the ten-card starter plus the six extras.

**Turn 1.** Ka-pow! on B (free, `Retain`, so playing it costs nothing), then
Strike, Strike on B (21 → 5), then one Defend. **Rejected:** Ka-pow! + one Strike
+ two Defends, which would have blocked B's whole 7 and cost me 2 HP instead of 2.
I took the aggressive line because neither line could kill B this turn — the 7 was
coming either way — so the 6 extra damage bought a cheaper turn 2. This was a real
choice and the numbers were close.

**Turn 2.** Strike killed B; Big Badda Boom on A for 12 (A 22 → 10, and A's
`Thorns 2` bit me back). **Rejected:** playing Grounded and holding BBB. I rejected
it because A had 22 HP and Grounded's whole clause is *"if none of your Bombs went
off last turn"* — it pays you for not doing the thing the deck is built to do.
**Refusal here:** I then typed `play "Grounded"` with 0 energy left and got
`'Grounded' cannot be played right now: you do not have enough energy`. My
miscount, not the tool's; the message named the working forms.

**Turn 3.** Strike A (10 → 4), Jumpy Dumpty (Bomb 8 on A), Defend.
**Rejected:** Strike + Defend + Defend, which takes zero damage. I paid 2 HP to
plant a bomb specifically to see the Set off loop.

**Turn 4.** The bomb had grown to `Bomb 12` — and my hand held **no Set off card**
(Ka-pow! and Big Badda Boom were both in the discard). I killed A with a Strike and
the Bomb 12 evaporated: the printed rule is *"A kill moves them to a survivor"* and
there was no survivor. **A whole turn of setup for nothing, and the screen told me
so before I acted.** No alternative existed — a hand of Pop!, Defend, Strike, Chain
Fuse, Strike cannot cash a bomb.

| turn | Sparks at end | anything go off? |
|---|---|---|
| 1 | 1 | no |
| 2 | 1 | no |
| 3 | 1 | no |
| 4 | 1 | no — the Bomb 12 died with its host |

**Card reward:** took **Mine Toss**, nearly took **Dodoco Cover**. I was looking
for damage that does **not** need a Set off card in hand, because that is exactly
what fight 1 had just cost me; Mine Toss's `Mine` keyword promised a bomb that
fires itself. Companion offered: **Sucrose — Catalyst Conversion** — not taken.

---

## Fight 2 — Seapunk [A] 44 HP

**Turn 1.** Pop! (Bomb 5) → Stoke the Fuse (1 Spark, no energy → Bomb 8) →
Careful Arrangement (Bomb 13) → Big Badda Boom: bomb 13, then 12, then *"damage
equal to what the Bombs dealt"* 13 again = **38 damage in one turn**, 44 → 6, all
three energy. **Rejected:** Pop! + Stoke + BBB + Strike, which is 34. Careful
Arrangement's flat +5 beats Strike's 6 here *only* because Big Badda Boom counts
the bomb twice — that is a genuine piece of arithmetic the printed text supports,
and working it out was the most satisfying moment of the round.

**Turn 2.** Strike for the last 6. **No alternative and none needed** — this is
turn 1's plan paying off, not a dead turn.

| turn | Sparks at end | anything go off? |
|---|---|---|
| 1 | 1 (spent 1 on Stoke, refunded by Pounding Surprise) | **yes** |
| 2 | 1 | no |

**Card reward:** took **Barbara — Front Row Seat**, nearly took **Fish-Flavored
Bait**. I was looking for Block (I had 2 Defends and 36/62 HP) and for a second
element, since every "Elemental Reaction" paragraph on every screen so far ended
with *"NO REACTION IS REACHABLE HERE"*. Companion offered: **Barbara — Front Row
Seat** — **taken**.

**Event (Self-Help Book):** took Sharp 2, put it on **Ka-pow!** (4 → 6). Rejected
Nimble on a Defend and Swift on Grounded: Ka-pow! costs 0 and Retains, so it is
the card I play most often per fight.

**Shop:** bought **Sorry, Jean...** (51) and **Rapid Fire** (72) of 132 gold.
Both purchases were aimed at the fight-1 failure: Rapid Fire was a third Set off,
Sorry Jean converts an unspent bomb into Block instead of nothing. Passed on
**The Big One** (151, *"Set off for quadruple damage"*) only on price — it is
obviously the card this deck wants.

---

## Fight 3 — Sludge Spinner [A] 39 HP

**Turn 1.** Barbara (5 Block, Hydro Aura 2 on the enemy, and it quietly paid
**+1 Spark** — the card's small print says Klee's own Companions make a Spark),
then Big Badda Boom into the Hydro aura → **Vaporize**, *"This hit deals 1.5x
damage and consumes the aura"* → 18 instead of 12. 39 → 21. **Rejected:** Strike +
BBB for 18 flat. Same damage, but the Barbara line also bought 5 Block and a
Spark. First real elemental decision of the run and it was legible: the Vaporize
paragraph appeared on the screen the instant it fired.

**Turn 2.** Weakened (the screen re-printed Strike as "Deal 4 damage" — good).
Pop! (Bomb 5) → Stoke the Fuse (2 Sparks → Bomb 11) → Ka-pow! set off for 11 + 4 =
15 (21 → 6) → Strike (6 → 2) → Grounded with the spare energy. **Note the bomb
took no Weak penalty**: 11 landed as 11, which matches *"Not an Attack"*.
**Rejected:** holding the bomb so Grounded would trigger. I chose the damage and
knowingly turned Grounded off.

**Turn 3.** Grounded did **not** fire, exactly as its text says. Then the hand:
Defend, Defend, Chain Fuse, Careful Arrangement, Sorry Jean... — **five cards and
not one point of damage** against an enemy on 2 HP. Chain Fuse, Careful Arrangement
and Sorry Jean all read "Bomb" and there was no bomb. I played two Defends, took 0,
and passed. **No decision existed on this turn**; that is the finding.

**Turn 4.** Grounded fired (6 Block + 1 Spark at turn start — the mechanic works,
it just never wants what the rest of the deck wants). Mine Toss put a Mine 4 on the
2 HP enemy and it died *before its hit*, as printed. I played a Defend as
insurance. **Rejected:** just Striking it, which was strictly simpler — I spent the
turn testing whether Mines really self-trigger, and they do.

| turn | Sparks at end | anything go off? |
|---|---|---|
| 1 | 2 | no |
| 2 | 1 | **yes** |
| 3 | 2 | no |
| 4 | — (fight ended) | **yes**, on the enemy's own beat |

**Card reward:** took **Pocket Match**, nearly took **Sizzle**. I was looking for a
Set off that does not cost Energy, so a turn spent building could still be cashed;
Pocket Match costs 1 Spark and Retains, which is the exact fix for fight 1 turn 4.
Companion offered: **Gorou — Inuzaka All-Round Defense** — not taken.

---

## Fight 4 — Gremlin Merc [A] 49 HP (`Surprise 1`, `Thievery 20`)

**Turn 1.** Mine Toss + Rapid Fire: Rapid Fire's first of four Set offs popped my
own Mine 4 immediately, so 4 + 12 = 16. 49 → 33. **Rejected:** Defend + Rapid Fire
(5 Block, 12 damage). I chose the race because the Merc hit for 14 a turn and I
had a Fire Potion in reserve. **Worth flagging:** Rapid Fire and Mine Toss are
anti-synergistic in the same turn — the mine would have fired for free at the
enemy's attack, and Rapid Fire spent it early for nothing.

**Turn 2.** Jumpy Dumpty (Bomb 8) → Big Badda Boom: 8 + 12 + 8 = 28, 33 → 5, and
Jumpy Dumpty's rider dropped a Mine 3. Then **Fire Potion** for the last 5.
**Rejected:** letting the Mine 3 finish it next turn, which would have cost me 12
HP and 20 stolen gold. Then `Surprise 1` resolved: the Merc **split into Sneaky
Gremlin (13) and Fat Gremlin (15, `Heist 20`)**, and my Mine 3 moved onto the Fat
one — *"A kill moves them to a survivor"* doing real work for the first time.

**Turn 3.** The Fat Gremlin intended to **Escape** with my gold. Chain Fuse on it
(Mine 7 → 13) → Pocket Match (1 Spark, no energy) set off 13 + 5 = 18 ≥ 15, killed
it, gold returned. Then Strike + Defend on the other rat. **Rejected:** killing the
Sneaky Gremlin (the one actually attacking me) first — the escape intent was a
timer, so the target choice was the decision and the screen made it readable.

**Turn 4.** Pop! (Bomb 5) + Ka-pow! (set off 5 + 6 = 11 ≥ 7) killed it **for zero
energy**. Rejected: Strike, which cost energy for less.

| turn | Sparks at end | anything go off? |
|---|---|---|
| 1 | 2 | **yes** |
| 2 | 3 | **yes** |
| 3 | 3 | **yes** |
| 4 | — (fight ended) | **yes** |

**Card reward:** took **Albedo — Solar Isotoma**, nearly took **Perfect Timing**.
I was looking for repeating Block-and-damage: *"at the end of your turn, if any
enemy has an aura, deal 8 damage to that enemy and gain 4 Block"*, and my Pyro
cards leave an aura almost every turn. Companion offered: **Albedo — Solar
Isotoma** — **taken**. (I never drew it in the two fights that followed, so I
cannot report how it plays.)

---

## Fight 5 — Sewer Clam [A] 56 HP, Block 8, `Plating 8`, later `Strength 4`

The instructive fight. The Set off keyword prints *"Block stops them"*, so the
clam's renewing shield is aimed squarely at this kit.

**Turn 1.** Jumpy Dumpty (Bomb 8), then Strike ×2 to chew the 8 Block (only 4 got
through). **Rejected:** setting the Bomb 8 off at once, which the printed rule told
me would leave 0 after Block. Building was forced by the text, not guessed.

**Turn 2** (clam buffing, no hit incoming). Mine Toss (Mine 4) then **Careful
Arrangement**, which merged Bomb 12 + Mine 4 into a single **Mine 21** — and, to my
surprise, the merged charge *kept its Mine status* ("Bombs here: 25, including 1
Mine"). **Rejected:** leaving the two charges separate. Merging was right precisely
because of Block: two hits of 12 and 4 lose 8 to the shield twice over, one hit of
21 loses 8 once. That is a decision the printed keyword handed me.

**Turn 3.** Mine had grown to 25. Barbara (Hydro Aura + 5 Block) → Chain Fuse
(Mine 31) → Ka-pow! set off → **Vaporize** → 45 damage through the 7 Block,
56 → 7. The set-off also re-armed Jumpy Dumpty's rider (a fresh Mine 3), so
**Pocket Match** (1 Spark, no energy) set that off for 3 + 5 = 8 and killed it in
the same turn. **Rejected:** waiting for the Mine 25 to fire itself at the clam's
attack — it would have left the clam alive around 13 and cost me a 14-damage hit.
Best turn of the round, and every number on it was printed somewhere I could read.

| turn | Sparks at end | anything go off? |
|---|---|---|
| 1 | 1 | no |
| 2 | 1 | no |
| 3 | 3 | **yes**, twice |

**Card reward:** took **Sizzle**, nearly took **Fireworks Show**. I was looking for
a cheap Energy-priced Set off to stop competing with Stoke the Fuse and Pocket
Match over the same Sparks. Companion offered: **Mika — Starfrost Swirl** — not
taken.

---

## Fight 6 — Two-Tailed Rat ×3, 19 / 21 / 18 HP (incomplete — budget)

**Turn 1.** Mine Toss (Mine 4 on all three), Strike on A, Pocket Match on A
(set off 4 + 5). A → 4. **Rejected:** Careful Arrangement to build one big charge —
wrong against three bodies. At the enemy turn, **B's mine fired and C's did not**:
C's intent was a Debuff, and the keyword says a Mine goes off *"before its enemy's
hit"*. No hit, no mine. C's charge instead grew to 8. That is a clean, learnable
rule and the screen let me predict it.

**Turn 2.** Stoke the Fuse (2 Sparks → C's Mine 14) then Rapid Fire, whose four
random Set offs killed **both** A (on 4) and C (on 18, via the 14 charge).
**Rejected:** Barbara for Block — the screen printed *"Reaction preview: Vaporize —
This card deals no damage. Pyro plus Hydro is still consumed, and there is no hit
here for the 1.5x to multiply"*, which talked me out of a play I would otherwise
have made. That preview line is the single best piece of UI in the round.
Then a Defend (Frail printed it as 3, not 5 — correctly).

| turn | Sparks at end | anything go off? |
|---|---|---|
| 1 | 2 | **yes** (A's mine to Pocket Match, B's on its own beat) |
| 2 | 1 | **yes** |

Budget reached at 120 with one rat left on 17, intending to Summon.

---

## The kit, after 5 completed fights (and 2 turns of a sixth)

**(a) Real choices, and where they were made.**

- **On the turn — the assembly order.** Fight 2 turn 1 and fight 5 turn 3 were
  both four-card sequences where the order was load-bearing and the sizes were
  arithmetic I could do from the printed text: place → grow → merge → set off.
  Fight 2's was a real trade (Careful Arrangement's +5 over Strike's 6, worth it
  only because Big Badda Boom counts the bomb twice). This is the best thing in
  the kit.
- **On the turn — cash now or grow.** A charge grows 4 a turn by itself, so every
  turn asks whether to spend it or let it compound. Against the Sewer Clam the
  enemy's own Block made that question sharp, because a shield eats a small hit
  whole and barely dents a big one.
- **Earlier in the fight — element setup.** Barbara costs a card and an energy one
  turn early to make a later Pyro hit 1.5x. Fight 3 turn 1 and fight 5 turn 3 were
  both that trade, and both paid.
- **At the draft — my deck had one bottleneck and I could see it.** After fight 1
  wasted a Bomb 12 for lack of a Set off in hand, every reward pick and both shop
  purchases were about that one hole. That is a draft doing its job.
- **Target choice.** The Fat Gremlin's Escape intent and its `Heist 20` made "which
  body do I kill" a real question rather than "which is lowest".

**(b) Automatic, and never worth playing.**

- **Strike and Defend.** Four each; I played them as filler for a leftover energy
  and never once chose between them and something interesting.
- **Grounded is a trap in its own deck.** *"if none of your Bombs went off last
  turn"* pays you for skipping the kit's entire loop. In five fights it triggered
  **once**, and that was a turn I had already conceded. I would cut it first.
- **Careful Arrangement and Chain Fuse against a single small enemy** are just
  worse Strikes; they are only interesting once a charge is large or the enemy has
  Block.
- **Sorry, Jean...** I bought it and never played it — every time it was in hand
  there was no bomb to cash, and every time there was a bomb I wanted the damage.
- **The last-hit problem.** Twice (fight 1 turn 4, fight 3 turn 3) I held a full
  hand of bomb-support cards and could not deal 2 damage. The support cards all
  read "Bomb" and all do literally nothing without one.

**(c) Could not understand, or contradicted itself.**

- Nothing contradicted its text. The one thing I could not predict in advance was
  whether **Careful Arrangement preserves Mine status** when it merges a Mine with
  a plain Bomb. It does (fight 5 turn 2), and the resulting body line said so, but
  the card itself only says "as one Bomb", which reads like a downgrade.
- **`Surprise 1` — "Something is off about this creature..."** is deliberately
  opaque and I had no way to plan around the split. Fair, but worth naming.
- The **Elemental Reaction** paragraph is enormous, appears on nearly every screen,
  and spends most of its length on an edge case about a relic re-applying an aura
  inside the same beat — which I never met. Meanwhile the thing I actually needed
  (Pyro + Hydro = 1.5x) only appeared *after* it fired.
- I never learned what **Albedo — Solar Isotoma** does in play; I drafted it and
  never drew it.

**(d) The card I never wanted, and the one I was happiest to draw.**

- **Never wanted: Grounded.** See (b) — it asks me not to play my deck.
- **Happiest to draw: Ka-pow!**, and it was not close. 0 Energy, `Retain`, and it
  is the Set off, so it converts any turn's leftovers into whatever I built and
  waits in hand when I have nothing to cash. **Pocket Match** is the same shape on
  a Spark price and was almost as welcome. **Big Badda Boom** produces the biggest
  number but only when the setup already happened.

**(e) Did the first turn of the first fight present a decision?**

**Yes, a small real one.** Ka-pow! was free and Retained so playing it was not a
choice; the choice was the last two energy: Strike + Strike to leave B on 5, or
Strike + Defend to eat almost none of its 7. Neither killed B, so it was a
straight 6 damage vs 5 Block trade with tempo on the side, and I had to think for a
moment. It was, however, entirely a **base-Strike/Defend** decision — the kit
proper did not present anything until turn 3, when I first had a bomb to place, and
the kit's actual loop did not close until **fight 2**. Fight 1 taught me the loop
mostly by failing at it.

---

## Non-blindness declaration

Commands run beyond the two allowed forms:

- `mkdir -p .../scratchpad/klee18` and `echo "notes" >> .../notes.md` — created a
  scratchpad notes file at the start; I never wrote anything further into it or
  read it back.
- `mkdir -p review/qa/klee-round-18-2026-09-05` — for this record.
- Shell plumbing around the allowed commands only: `cd` into the working
  directory, `&&` chaining of `act`/`observe` calls, `>/dev/null` to drop echoed
  `act` output, and `sed -n '...p'` / `tail -n` to re-read a subset of an
  `observe` I had just printed. No `observe` output was filtered before I had
  seen the screen it belonged to, and no other understudy subcommand was run —
  no `harness state`, no `scenario`, no `staged_turn`, no `soak`.

Tools used: **Bash** (as above) and **Write** (once, this file).

**Repo files read: none.**
